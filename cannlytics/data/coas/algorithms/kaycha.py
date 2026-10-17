"""
Parse Kaycha Labs COA -- COA Doc Hybrid Algorithm (Offline-First)
Copyright (c) 2022-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/17/2022
Updated: 10/13/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Kaycha Labs COA PDFs directly from the PDF text -- no network
    access required. This is the modernized offline-first engine that
    extracts all data from the PDF itself using pdfplumber text
    extraction and regex-based field parsing.

    Kaycha Labs is a multi-state cannabis testing laboratory operating
    in FL (Davie, Gainesville), NY (Albany), and AZ (Tempe). They are
    one of the highest-volume labs in the FL and NY cannabis markets.

    Identification:
        Kaycha Labs COAs contain 'Kaycha Labs' on line 0 of page 1,
        and/or 'kaychalabs.com' or 'yourcoa.com' in QR code URLs.

    Format notes:
        * FL (DA/GA prefix): 2-6 pages, LOD-based, two-column layouts
        * NY (AL prefix): 5 pages, LOQ-based, tabular ANALYTES columns
        * AZ (TE prefix): 4-7 pages, LOD+LOQ, tabular ANALYTES columns
        * Page 1: Metadata + cannabinoid summary + safety status icons
        * Page 2: Terpenes (two-column FL, tabular NY/AZ)
        * Page 3+: Pesticides, residual solvents, microbials,
          mycotoxins, heavy metals, filth, water activity, moisture
        * Format eras: 2020 (2-page minimal), 2022 (Gainesville),
          2024+ (modern FL/NY/AZ), 2025+ (medical/tabular NY/AZ)

    Row layouts (one analyte per line, see _read_row):
        FL:  "ACETONE 75.000 ppm 750 PASS ND"
             NAME LOD UNITS LIMIT STATUS RESULT
        NY:  "ACEQUINOCYL 0.1000 ppm 2 PASS <0.1000"
             NAME LOQ UNITS LIMIT STATUS RESULT
        AZ:  "ACEPHATE ppm 0.0100 0.2000 0.4 PASS ND"
             NAME UNITS LOD LOQ LIMIT STATUS RESULT
        NY terpenes: "LIMONENE 0.0040 10 PASS 0.5100 5.1000"
             NAME LOQ LIMIT STATUS RESULT(%) RESULT(mg/unit)

    Fixes (10/13/2026), from a benchmark of 12 COAs read by four
    Claude models that agree with each other almost perfectly:
        * A result is never an LOD, LOQ or action limit. Tabular NY/AZ
          rows took the row's last number, which is the limit whenever
          the result is "ND" (AZ pesticides: acephate read as 0.4 ppm);
          FL-layout section rows took the number after the units, which
          is the limit in "LOD UNITS LIMIT STATUS RESULT" rows (FL and
          NY residual solvents: acetone read as 750 ppm). Rows are now
          read from the page's header row when one is printed, and
          otherwise from the PASS/FAIL/TESTED cell (_read_row).
        * NY terpenes are read from the percent column (they were read
          from mg/unit, 10x the percent for a 1 g unit; the TOTAL
          TERPENES row was read as its LOQ, 0.1).
        * NY cannabinoids: the two D10-THC isomer columns lead the
          '%' row but their names print on lines of their own, so the
          values were assigned two analytes to the left (CBN got CBGA's
          value, THCV got D9-THC's). The isomers are restored to the
          front of the header, and a Total THC self-consistency check
          (D9-THC + 0.877 * THCA) rejects an alignment the COA's own
          total contradicts (_align_cannabinoids).
        * Non-detects keep their qualifier: "ND" / "Not Present" is
          value None, qualifier 'ND'; "<0.1000" is value None,
          qualifier '<LOQ', with 'loq' 0.1 when the row prints no LOQ
          of its own (it was read as the number 0.1). A measured 0
          stays 0.0. Every result row now carries 'qualifier', 'lod',
          'loq', 'limit' and 'status' (None when not printed).
        * The D10-THC isomers map to the canonical keys
          '9r_delta_10_thc' / '9s_delta_10_thc'.
        * Review (10/14/2026): a row that prints no limit is not
          compared with one (its LOQ was read as the result of
          "BIFENAZATE 0.1000 ppm PASS 0.1500"); a number before the
          status with nothing after it is not read; the FL pesticide
          pattern keeps its order on a FAIL; a header applies only to
          rows whose status it places; and of two result words the one
          nearer the status is the result ("Not Detected in 1 g
          Detected FAIL" is a detection).

Data Points:

    * product_name, product_type, strain_name
    * date_tested, date_received, date_collected
    * batch_number, sample_id (lab_id)
    * lab, lab_license_number, lab_address, lab_city, lab_state, lab_zipcode
    * producer, producer_license_number, producer_street, producer_city,
      producer_state, producer_zipcode
    * distributor
    * total_thc, total_cbd, total_cannabinoids, total_terpenes
    * status (overall pass/fail)
    * analyses (list of analysis types)
    * results (list of analyte result dicts)
"""
# Standard imports:
import hashlib
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# External imports (only pdfplumber allowed per dependency policy):
import pdfplumber

# Internal imports:
from cannlytics.data.coas.schema import parse_result_value

# ── Kaycha Labs Constants ──────────────────────────────────────────

KAYCHA_LABS = {
    'coa_algorithm': 'kaycha.py',
    'coa_algorithm_entry_point': 'parse_kaycha_coa',
    'lims': 'Kaycha Labs',
    'lab': 'Kaycha Labs',
    'lab_website': 'https://www.kaychalabs.com',
}

# Lab locations keyed by sample ID prefix or address detection.
KAYCHA_LOCATIONS = {
    'davie': {
        'lab_address': '4131 SW 47th Avenue Suite 1408, Davie, FL 33314',
        'lab_street': '4131 SW 47th Avenue Suite 1408',
        'lab_city': 'Davie',
        'lab_state': 'FL',
        'lab_zipcode': '33314',
        'lab_phone': '(954) 368-7664',
        'lab_license_number': 'CMTL-0002',
    },
    'gainesville': {
        'lab_address': '2444 NE 1st Blvd Suite 700, Gainesville, FL 32609',
        'lab_street': '2444 NE 1st Blvd Suite 700',
        'lab_city': 'Gainesville',
        'lab_state': 'FL',
        'lab_zipcode': '32609',
        'lab_phone': '(833) 465-8378',
        'lab_license_number': 'CMTL-0001',
    },
    'albany': {
        'lab_address': '1 Winners Circle, Albany, NY 12205',
        'lab_street': '1 Winners Circle',
        'lab_city': 'Albany',
        'lab_state': 'NY',
        'lab_zipcode': '12205',
        'lab_phone': '(833) 465-8378',
        'lab_license_number': 'OCM-CPL-2022-00006',
    },
    'tempe': {
        'lab_address': '1231 W. Warner Road, Suite 105, Tempe, AZ 85284',
        'lab_street': '1231 W. Warner Road, Suite 105',
        'lab_city': 'Tempe',
        'lab_state': 'AZ',
        'lab_zipcode': '85284',
        'lab_phone': '(480) 220-4470',
        'lab_license_number': '00000024LCMD66604568',
    },
}

# Standard analysis section header mappings.
ANALYSIS_SECTION_MAP = {
    'cannabinoid': 'cannabinoids',
    'terpene': 'terpenes',
    'pesticide': 'pesticides',
    'heavy metal': 'heavy_metals',
    'microbial': 'microbials',
    'mycotoxin': 'mycotoxins',
    'residual solvent': 'residual_solvents',
    'filth': 'foreign_matter',
    'foreign': 'foreign_matter',
    'water activity': 'water_activity',
    'moisture': 'moisture',
}

# Standard units per analysis type.
STANDARD_UNITS = {
    'cannabinoids': 'percent',
    'terpenes': 'percent',
    'pesticides': 'ppm',
    'heavy_metals': 'ppm',
    'microbials': 'CFU/g',
    'mycotoxins': 'ppm',
    'residual_solvents': 'ppm',
    'foreign_matter': 'percent',
    'water_activity': 'aw',
    'moisture': 'percent',
}

# ── ANALYTE_KEY_MAP ────────────────────────────────────────────────
# Maps display names (uppercase) to standardized snake_case keys.
# This is the most critical data structure for downstream consistency.
ANALYTE_KEY_MAP = {
    # Cannabinoids
    'D9-THC': 'delta_9_thc',
    'D9 THC': 'delta_9_thc',
    'DELTA-9 THC': 'delta_9_thc',
    'DELTA 9 THC': 'delta_9_thc',
    'THCA': 'thca',
    'CBD': 'cbd',
    'CBDA': 'cbda',
    'CBG': 'cbg',
    'CBGA': 'cbga',
    'CBN': 'cbn',
    'CBC': 'cbc',
    'CBDV': 'cbdv',
    'THCV': 'thcv',
    'D8-THC': 'delta_8_thc',
    'D8 THC': 'delta_8_thc',
    'DELTA-8 THC': 'delta_8_thc',
    '(6AR,9R) D10-THC': '9r_delta_10_thc',
    '(6AR,9S) D10-THC': '9s_delta_10_thc',
    'TOTAL CANNABINOIDS': 'total_cannabinoids',
    'TOTAL CBD': 'total_cbd',
    'TOTAL THC': 'total_thc',
    # Terpenes
    '3-CARENE': 'delta_3_carene',
    'ALPHA-BISABOLOL': 'alpha_bisabolol',
    'ALPHA-CEDRENE': 'alpha_cedrene',
    'ALPHA-HUMULENE': 'alpha_humulene',
    'ALPHA-PHELLANDRENE': 'alpha_phellandrene',
    'ALPHA-PINENE': 'alpha_pinene',
    'ALPHA-TERPINENE': 'alpha_terpinene',
    'ALPHA-TERPINEOL': 'alpha_terpineol',
    'ALPHA TERPINEOL': 'alpha_terpineol',
    'ALPHA-TERPINOLENE': 'terpinolene',
    'BETA-CARYOPHYLLENE': 'beta_caryophyllene',
    'BETA-MYRCENE': 'beta_myrcene',
    'BETA-PINENE': 'beta_pinene',
    'BORNEOL': 'borneol',
    'CAMPHENE': 'camphene',
    'CAMPHOR': 'camphor',
    'CARYOPHYLLENE OXIDE': 'caryophyllene_oxide',
    'CEDROL': 'cedrol',
    'CIS-NEROLIDOL': 'cis_nerolidol',
    'EUCALYPTOL': 'eucalyptol',
    'FARNESENE': 'farnesene',
    'FENCHONE': 'fenchone',
    'FENCHYL ALCOHOL': 'fenchyl_alcohol',
    'GAMMA-TERPINENE': 'gamma_terpinene',
    'GAMMA-TERPINEOL': 'gamma_terpineol',
    'GERANIOL': 'geraniol',
    'GERANYL ACETATE': 'geranyl_acetate',
    'GUAIOL': 'guaiol',
    'HEXAHYDROTHYMOL': 'hexahydrothymol',
    'ISOBORNEOL': 'isoborneol',
    'ISOPULEGOL': 'isopulegol',
    'LIMONENE': 'limonene',
    'LINALOOL': 'linalool',
    'MENTHOL': 'menthol',
    'NEROL': 'nerol',
    'OCIMENE': 'ocimene',
    'PULEGONE': 'pulegone',
    'SABINENE': 'sabinene',
    'SABINENE HYDRATE': 'sabinene_hydrate',
    'TERPINOLENE': 'terpinolene',
    'TERPINEOL': 'terpineol',
    'TOTAL TERPINEOL': 'total_terpineol',
    'TOTAL TERPENES': 'total_terpenes',
    'TRANS-NEROLIDOL': 'trans_nerolidol',
    'VALENCENE': 'valencene',
    # Heavy metals
    'ARSENIC': 'arsenic',
    'CADMIUM': 'cadmium',
    'LEAD': 'lead',
    'MERCURY': 'mercury',
    'ANTIMONY': 'antimony',
    'CHROMIUM': 'chromium',
    'COPPER': 'copper',
    'NICKEL': 'nickel',
    'TOTAL CONTAMINANT LOAD METALS': 'total_contaminant_load_metals',
    # Microbials
    'ASPERGILLUS TERREUS': 'aspergillus_terreus',
    'ASPERGILLUS NIGER': 'aspergillus_niger',
    'ASPERGILLUS FUMIGATUS': 'aspergillus_fumigatus',
    'ASPERGILLUS FLAVUS': 'aspergillus_flavus',
    'SALMONELLA SPECIFIC GENE': 'salmonella',
    'SALMONELLA SPP': 'salmonella',
    'SALMONELLA SPP.': 'salmonella',
    'SALMONELLA SPECIES': 'salmonella',
    'ECOLI SHIGELLA': 'e_coli',
    'ESCHERICHIA COLI SHIGELLA SPP': 'e_coli',
    'ESCHERICHIA COLI REC': 'e_coli',
    'ESCHERICHIA COLI/SHIGELLA SPP.': 'e_coli',
    'TOTAL YEAST AND MOLD': 'total_yeast_and_mold',
    'TOTAL AEROBIC BACTERIA': 'total_aerobic_bacteria',
    # Mycotoxins
    'AFLATOXIN B1': 'aflatoxin_b1',
    'AFLATOXIN B2': 'aflatoxin_b2',
    'AFLATOXIN G1': 'aflatoxin_g1',
    'AFLATOXIN G2': 'aflatoxin_g2',
    'OCHRATOXIN A': 'ochratoxin_a',
    'OCHRATOXIN A+': 'ochratoxin_a',
    'TOTAL AFLATOXINS': 'total_aflatoxins',
    'TOTAL AFLATOXINS (B1, B2, G1, G2)': 'total_aflatoxins',
    # Foreign matter
    'FILTH AND FOREIGN MATERIAL': 'foreign_matter',
    'FOREIGN MATTER': 'foreign_matter',
    'STEMS (>3MM)': 'stems',
    'MAMMALIAN EXCRETA': 'mammalian_excreta',
    # Water activity and moisture
    'WATER ACTIVITY': 'water_activity',
    'MOISTURE CONTENT': 'moisture_content',
}

# Non-analyte keywords to skip (phantom row filtering).
SKIP_KEYWORDS = {
    'TOTAL CONTAMINANT LOAD (PESTICIDES)', 'TOTAL DIMETHOMORPH',
    'TOTAL PERMETHRIN', 'TOTAL PYRETHRINS', 'TOTAL SPINETORAM',
    'TOTAL SPINOSAD', 'TOTAL CONTAMINANT LOAD',
    'PYRETHRINS, TOTAL', 'SPINETORAM, TOTAL', 'SPINOSAD, TOTAL',
    'TOTAL PERMETHRINS',
}

# Logger.
logger = logging.getLogger(__name__)

# ── Utility Functions ──────────────────────────────────────────────

def _snake_case(name: str) -> str:
    """Convert analyte display name to snake_case key.
    Tries ANALYTE_KEY_MAP first, then falls back to normalization.
    """
    upper = name.strip().upper()
    mapped = ANALYTE_KEY_MAP.get(upper)
    if mapped:
        return mapped
    # Fallback: normalize to snake_case.
    s = name.strip()
    s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
    s = re.sub(r'\s+', '_', s.strip())
    return s.lower()

def _parse_number(text: str) -> Optional[float]:
    """Parse a plain number (an LOD, LOQ, limit or total) from text.
    Handles: '0.1000', '5,000', '0', '0.1575 Q3' (flag stripped).
    Returns None for ND / 'Not Present' / 'N/A' and for a bound such
    as '<0.100' or '>100': a bound is a qualifier, not a number (until
    10/13/2026 '<0.100' returned 0.1). Read results with _parse_result.
    """
    if text is None:
        return None
    t = text.strip().replace(',', '')
    if not t or t in ('ND', 'N/A', 'Not Present', 'Not Detected', ''):
        return None
    if t.startswith('Not ') or t[0] in '<>':
        return None
    # Strip qualifier flags (e.g., "0.1575 Q3" -> "0.1575").
    t = re.sub(r'\s+[A-Z]\d+\s*$', '', t)
    # Strip trailing non-numeric chars.
    t = re.sub(r'[^0-9.\-].*$', '', t)
    try:
        val = float(t)
        return val
    except (ValueError, TypeError):
        return None

def _parse_result(text: Optional[str]) -> Tuple[Optional[float], str, Optional[float]]:
    """Read a printed result as ``(value, qualifier, bound)``.

    Uses the package's qualifier semantics (``parse_result_value``):
    '0.5100' is (0.51, '', None); 'ND' and 'Not Present' are
    (None, 'ND', None); '<0.1000' is (None, '<LOQ', 0.1), the bound
    being the limit the result is below; '0' is (0.0, '', None).
    Kaycha flags after a number ('0.1575 Q3') are dropped.
    """
    if text is None:
        return None, '', None
    t = str(text).replace('_', ' ').strip()
    t = re.sub(r'\s+[A-Z]\d{1,2}\s*$', '', t)
    return parse_result_value(t)

def _parse_date(text: str) -> str:
    """Parse date string to ISO format (YYYY-MM-DD).
    Handles: MM/DD/YY, MM/DD/YYYY, 'Mon DD, YYYY', with optional time.
    """
    if not text:
        return ''
    t = text.strip()
    # Remove time portion if present.
    t = re.sub(r'\s+\d{1,2}:\d{2}(:\d{2})?\s*(AM|PM)?', '', t, flags=re.IGNORECASE)
    t = t.strip()
    # Remove "Expires: ..." suffix.
    t = re.split(r'\s*Expires:', t)[0].strip()
    formats = [
        '%m/%d/%y', '%m/%d/%Y',
        '%b %d, %Y', '%B %d, %Y',
        '%Y-%m-%d',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(t, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return t

def _detect_location(text: str) -> str:
    """Detect which Kaycha location produced this COA."""
    t = text.lower()
    if 'davie, fl' in t or '4131 sw 47th' in t:
        return 'davie'
    if 'gainesville, fl' in t or '2444 ne 1st' in t:
        return 'gainesville'
    if 'albany, ny' in t or '1 winners circle' in t:
        return 'albany'
    if 'tempe, az' in t or '1231 w. warner' in t or '1231 w warner' in t:
        return 'tempe'
    return 'davie'  # Default fallback.

def _detect_format(text: str, location: str) -> str:
    """Detect the COA format variant.
    Returns: 'fl_standard', 'ny_standard', 'ny_medical', 'az_standard', 'az_tabular'
    """
    if location in ('davie', 'gainesville'):
        return 'fl_standard'
    if location == 'albany':
        if 'ANALYTES' in text and 'UNIT' in text and 'QUALIFIER' in text:
            return 'ny_medical'
        return 'ny_standard'
    if location == 'tempe':
        if 'ANALYTES' in text and 'UNIT' in text and 'QUALIFIER' in text:
            return 'az_tabular'
        return 'az_standard'
    return 'fl_standard'

# ── Metadata Parsing ───────────────────────────────────────────────

def _parse_metadata(text: str, lines: List[str], location: str) -> Dict:
    """Parse metadata fields from page 1 text."""
    obs = {}

    # Product name is always line 1.
    obs['product_name'] = lines[1] if len(lines) > 1 else ''

    # Strain name: line 2 unless it starts with 'Matrix:' or 'Strain:'.
    if len(lines) > 2:
        line2 = lines[2]
        if line2.startswith('Strain:'):
            obs['strain_name'] = line2.split(':', 1)[1].strip()
        elif not line2.startswith('Matrix:') and not line2.startswith('Classification:'):
            obs['strain_name'] = line2
        else:
            obs['strain_name'] = obs['product_name']

    # Product type from Matrix field.
    m = re.search(r'Matrix\s*:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['product_type'] = m.group(1).strip().lower()

    # Sample ID - multiple patterns across states.
    for pattern in [
        r'Sample\s*:\s*(\S+)',
        r'Laboratory Sample ID\s*:\s*(\S+)',
        r'Lab ID\s*:\s*(\S+)',
    ]:
        m = re.search(pattern, text)
        if m:
            obs['sample_id'] = m.group(1).strip()
            break

    # Batch number.
    m = re.search(r'Batch\s*#?\s*:\s*(.+?)(?:\n|$)', text)
    if m:
        val = m.group(1).strip()
        # Clean: remove trailing metadata from multi-column merge.
        val = re.split(r'\s{2,}', val)[0].strip()
        # Remove trailing field names that got merged.
        val = re.split(r'\s+(?:Ordered|Sampled|Sample|Harvest|Completed|Production)', val)[0].strip()
        if val and val != ':' and len(val) > 1:
            obs['batch_number'] = val

    # Harvest/Lot ID.
    m = re.search(r'Harvest/Lot ID\s*:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['source_id'] = m.group(1).strip().split('  ')[0].strip()

    # Dates.
    date_fields = {
        r'Completed\s*:\s*(\S+(?:\s+\S+)?)': 'date_tested',
        r'Sampled\s*(?:Date)?\s*:\s*(\S+(?:\s+\S+(?:\s+\S+)?)?)': 'date_collected',
        r'Ordered\s*:\s*(\S+)': 'date_received',
        r'Batch Date\s*:\s*(\S+)': 'date_harvested',
    }
    for pattern, field in date_fields.items():
        m = re.search(pattern, text)
        if m:
            obs[field] = _parse_date(m.group(1))

    # NY/AZ fallback: extract date_tested from signature block.
    if not obs.get('date_tested'):
        m = re.search(r'Signature\n.*?(\d{2}/\d{2}/\d{2,4})\s*$', text, re.MULTILINE)
        if m:
            obs['date_tested'] = _parse_date(m.group(1))

    # Sample weight / size.
    m = re.search(r'Sample Size Received\s*:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['sample_weight'] = m.group(1).strip()

    # Retail product size.
    m = re.search(r'Retail Product Size\s*:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['product_size'] = m.group(1).strip()

    # Total batch size / amount.
    for pat in [r'Total Batch Size\s*:\s*(.+?)(?:\n|$)',
                r'Total Amount\s*:\s*(.+?)(?:\n|$)']:
        m = re.search(pat, text)
        if m:
            obs['batch_size'] = m.group(1).strip()
            break

    # Producer / distributor from the date|name line (FL format).
    m = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}\s*\|\s*(.+?)(?:\s+PASSED|\s+FAILED|\n)', text)
    if m:
        name = m.group(1).strip()
        obs['distributor'] = name
        if not obs.get('producer'):
            obs['producer'] = name

    # Producer from "Cultivation Facility" (FL).
    m = re.search(r'Cultivation Facility\s*:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['producer'] = m.group(1).strip()

    # Producer/client name from NY/AZ format (name before "License #" block).
    if not obs.get('producer') or obs.get('producer') == obs.get('product_name'):
        # Strategy 1: Name on same line as "PASSED" before "License #".
        for i, line in enumerate(lines):
            if 'License #' in line:
                # Check previous line for "Name PASSED" pattern.
                if i > 0:
                    prev = lines[i - 1].strip()
                    if 'PASSED' in prev:
                        name = prev.replace('PASSED', '').replace('FAILED', '').strip()
                        if name and len(name) > 2 and name[0].isalpha() and \
                                not any(x in name for x in ['Pages', 'Page', 'Certificate']):
                            obs['producer'] = name
                            break
                # Strategy 2: Look back for a clean company name.
                for lookback in range(1, 5):
                    if i - lookback >= 0:
                        candidate = lines[i - lookback].strip()
                        if candidate and not any(x in candidate for x in [
                            'PASSED', 'FAILED', 'Pages', 'Page ', 'Certificate',
                            'Kaycha', ', US', ', AZ', ', FL', ', NY',
                            'SAFETY', 'COMPLIANCE', 'FOR ',
                            'Laboratory', 'AZDHS', 'Warning', 'Cultivated',
                            'Sampling Method', 'Sampling Start', 'Sampling End',
                            'SOP.', 'unborn', 'Manufactured', 'Distributed',
                            'by License', 'dba ', 'Telephone', 'Email',
                        ]) and len(candidate) > 2 and candidate[0].isalpha():
                            obs['producer'] = candidate
                            break
                break

    # AZ format: client name appears after AZDHS warning and before "License #".
    if not obs.get('producer') or obs.get('producer') == obs.get('product_name'):
        # Try to find producer from the "dba" line or company name.
        m = re.search(r'(?:Inc,?\s+dba|LLC\.?|Corp\.?|Inc\.?)\s+(.+?)(?:\n|$)', text)
        if m:
            obs['producer'] = m.group(0).split('\n')[0].strip()
        elif not obs.get('producer'):
            # Last resort: use distributor as producer.
            if obs.get('distributor'):
                obs['producer'] = obs['distributor']

    # Overall status.
    if 'PASSED' in text.split('Cannabinoid')[0] if 'Cannabinoid' in text else text:
        obs['status'] = 'pass'
    elif 'FAILED' in text:
        obs['status'] = 'fail'

    # License number from client/producer block.
    m = re.search(r'License\s*#\s*:\s*(\S+)', text)
    if m:
        obs['producer_license_number'] = m.group(1).strip()

    # Seed to sale / traceability.
    m = re.search(r'Seed to Sale\s*#?\s*:?\s*(\S+)', text)
    if m:
        obs['traceability_id'] = m.group(1).strip()

    return obs

def _parse_totals(text: str, lines: List[str]) -> Dict:
    """Parse total THC, CBD, and cannabinoids from page 1.

    A total printed as a non-detect or a bound ('ND', '<0.1000') is
    None, and it still takes its place in the row, so that "25.5961%
    ND 29.7057%" does not read total cannabinoids as total CBD.
    """
    obs = {}
    from_row = set()
    for i, line in enumerate(lines):
        if 'Total THC' in line and 'Total CBD' in line:
            # Next line has the percentages (e.g., "25.5961% <0.1000 29.7057%").
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # Parse all tokens that look like values (with or without %).
                tokens = next_line.split()
                values = []
                for t in tokens:
                    t_clean = t.rstrip('%')
                    if re.match(r'^<?[\d.,]+$', t_clean) and re.search(r'\d', t_clean):
                        values.append(t_clean)
                    elif t_clean.upper() in ('ND', '<LOQ', '<LOD', 'NR', 'NT', 'N/A'):
                        values.append(t_clean)
                for field, cell in zip(
                    ('total_thc', 'total_cbd', 'total_cannabinoids'), values,
                    strict=False,
                ):
                    obs[field] = _parse_result(cell)[0]
                    from_row.add(field)
            break

    # Try alternate layout where totals are on separate lines (NY medical).
    if obs.get('total_thc') is None and 'total_thc' not in from_row:
        m = re.search(r'Total THC\s*[\n:]*\s*([\d.]+)\s*%', text)
        if m:
            obs['total_thc'] = _parse_number(m.group(1))
    if obs.get('total_cbd') is None and 'total_cbd' not in from_row:
        m = re.search(r'Total CBD\s*[\n:]*\s*([\d.]+)\s*%', text)
        if m:
            obs['total_cbd'] = _parse_number(m.group(1))
    if obs.get('total_cannabinoids') is None and 'total_cannabinoids' not in from_row:
        m = re.search(r'Total Cannabinoids\s*(?:Q\d+)?\s*[\n:]*\s*([\d.]+)\s*%', text)
        if m:
            obs['total_cannabinoids'] = _parse_number(m.group(1))

    return obs

def _parse_safety_statuses(text: str) -> Tuple[Dict, List[str]]:
    """Parse safety result statuses from the icon bar on page 1."""
    obs = {}
    analyses = []

    # Standard analysis order in the safety bar.
    analysis_order = [
        'pesticides', 'heavy_metals', 'microbials', 'mycotoxins',
        'residual_solvents', 'foreign_matter', 'water_activity',
        'moisture', 'terpenes',
    ]

    # Extract the safety results block.
    safety_block = ''
    if 'SAFETY RESULTS' in text:
        safety_block = text.split('SAFETY RESULTS')[-1].split('Cannabinoid')[0]

    if not safety_block:
        return obs, analyses

    # Normalize and find statuses.
    block_clean = safety_block.replace('NOT TESTED', 'NOT_TESTED')
    block_clean = block_clean.replace('NOT TESTED', 'NOT_TESTED')
    statuses = re.findall(r'(PASSED|FAILED|TESTED|NOT_TESTED)', block_clean)

    status_map = {
        'PASSED': 'pass',
        'FAILED': 'fail',
        'TESTED': 'tested',
        'NOT_TESTED': None,
    }

    for i, status in enumerate(statuses):
        if i >= len(analysis_order):
            break
        analysis = analysis_order[i]
        mapped = status_map.get(status)
        if mapped is not None:
            obs[f'{analysis}_status'] = mapped
            analyses.append(analysis)

    return obs, analyses

# ── Row Reading (shared by the section parsers) ────────────────────
#
# Every terpene and contaminant row is an analyte name followed by
# cells: detection limit(s), units, action limit, status, result, and
# for NY terpenes a second result in mg/unit (layouts in the module
# docstring). Some tables print the result before the status instead
# ("NAME LOD UNITS RESULT STATUS LIMIT"). A row is read from the
# page's header row when one is printed and its columns match the
# cells; otherwise from the status cell (see _read_row).

# Words printed in place of a number. Multi-word results are joined
# with '_' before a line is split into tokens.
_MULTIWORD_RESULTS = (
    (re.compile(r'\bNot\s+Present\b', re.IGNORECASE), 'Not_Present'),
    (re.compile(r'\bNot\s+Detected\b', re.IGNORECASE), 'Not_Detected'),
    (re.compile(r'\bNone\s+Detected\b', re.IGNORECASE), 'None_Detected'),
)
_RESULT_WORDS = {
    'ND', 'N/D', 'N.D.', 'NOT_PRESENT', 'NOT_DETECTED', 'NONE_DETECTED',
    'ABSENT', 'PRESENT', 'DETECTED', 'NEGATIVE', 'POSITIVE',
    '<LOQ', '<LOD', '>ULOQ', 'BLQ', 'BQL', 'NR', 'NT', 'N/A', 'NA',
}
# Pathogen results ("ASPERGILLUS TERREUS Not Present PASS"), which
# pass unless the row says otherwise, and word results in general,
# after which a row may print filler ("Not Detected in 1 g PASS").
_PATHOGEN_RESULTS = {'NOT_PRESENT', 'NOT_DETECTED', 'NONE_DETECTED', 'ABSENT', 'NEGATIVE'}
_WORD_RESULTS = _PATHOGEN_RESULTS | {'PRESENT', 'DETECTED', 'POSITIVE'}
_UNIT_WORDS = {
    'ppm', 'ppb', 'ug/g', 'µg/g', 'μg/g', 'ug/kg', 'mg/g', 'mg/kg',
    'mg/ml', 'mg/unit', 'mg/serving', 'mg', 'cfu/g', 'aw', '%', 'percent',
}
_STATUS_WORDS = {
    'PASS': 'pass', 'PASSED': 'pass', 'FAIL': 'fail', 'FAILED': 'fail',
    'TESTED': 'tested',
}
_NUMBER_TOKEN = re.compile(r'^[<>]?=?(?:\d+(?:,\d{3})*(?:\.\d*)?|\.\d+)$')
# Qualifier flags printed beside a result ("0.1575 Q3").
_FLAG_TOKEN = re.compile(r'^[A-Z]\d{1,2}$')
# Solvent names that begin with locants ("1,1-DICHLOROETHENE").
_LOCANT_NAME = re.compile(r'^\d+(?:,\d+)*-[A-Za-z]')
# Characters an FL-layout analyte name is made of (those of the r10
# name regex, plus '+' for "OCHRATOXIN A+").
_STRICT_NAME_TOKEN = re.compile(r'^[A-Z0-9\-(),>+]+$')
# An uppercase word after a row's cells: the name of a second record
# that pdfplumber merged onto the line from a neighboring column.
_RECORD_START = re.compile(r"^[A-Z][A-Z0-9\-(),.'/+]*[A-Z][A-Z0-9\-(),.'/+]*$")

# Header columns, in the order a header row names them.
_HEADER_COLUMNS = (
    ('lod', r'\bLOD\b'),
    ('loq', r'\bLOQ\b'),
    ('units', r'\bUNITS?\b'),
    ('limit', r'\bACTION\s*LEVELS?\b|\bACTION\s*LIMITS?\b|\bLIMITS?\b'),
    ('status', r'\bPASS\s*/\s*FAIL\b|\bSTATUS\b'),
    ('qualifier', r'\bQUALIFIERS?\b'),
)
_HEADER_RESULT = re.compile(r'\bRESULTS?\b(?:\s*\(\s*([^)]*)\))?')

def _tokenize(line: str) -> List[str]:
    """Split a row into tokens: multi-word results joined ('Not_Present'),
    footnote stars dropped, '< 0.1000' rejoined as '<0.1000' and a
    number glued to its units ('0.1000ppm') split."""
    text = line.replace('*', ' ')
    for pattern, joined in _MULTIWORD_RESULTS:
        text = pattern.sub(joined, text)
    text = re.sub(r'([<>])\s+(?=[\d.]|LO[DQ]\b)', r'\1', text, flags=re.IGNORECASE)
    text = re.sub(r'(?<=\d)(ppm|ppb|cfu/g|ug/g|mg/g|%)(?=\s|$)', r' \1', text, flags=re.IGNORECASE)
    return text.split()

def _token_kind(token: str) -> str:
    """Classify a token: 'value', 'unit', 'status' or 'other'."""
    if _NUMBER_TOKEN.match(token):
        return 'value'
    upper = token.upper()
    if upper in _RESULT_WORDS:
        return 'value'
    if upper in _STATUS_WORDS:
        return 'status'
    lower = token.lower()
    if lower in _UNIT_WORDS:
        return 'unit'
    if '/' in lower and len(lower) <= 8 and not re.search(r'\d', lower):
        return 'unit'  # e.g. 'ug/L', 'CFU/mL'
    return 'other'

def _split_name(tokens: List[str]) -> Tuple[List[str], List[str]]:
    """Split a row's tokens into the analyte name and its cells. The
    name ends at the first value, unit or status token, or at a later
    token that starts like a number (a first token may be a locant
    name such as '1,1-DICHLOROETHENE')."""
    for idx, token in enumerate(tokens):
        if _token_kind(token) != 'other' or (idx and re.match(r'^[<>.\d]', token)):
            return tokens[:idx], tokens[idx:]
    return tokens, []

def _is_strict_name(name_tokens: List[str]) -> bool:
    """An FL-layout analyte name: uppercase words, digits, '-(),>+'."""
    if not name_tokens:
        return False
    first = name_tokens[0]
    if not (first[0].isalpha() or _LOCANT_NAME.match(first)):
        return False
    return all(_STRICT_NAME_TOKEN.match(t) for t in name_tokens)

def _parse_header(line: str) -> Optional[List[str]]:
    """Read a table header row into its column order, or None.

    e.g. "Solvents LOD Units Action Level Pass/Fail Result" is
    ['lod', 'units', 'limit', 'status', 'result']; "ANALYTES LOQ ACTION
    LEVEL PASS/FAIL RESULT (%) RESULT (mg/g)" is ['loq', 'limit',
    'status', 'result', 'result_mg']. A header names a result and at
    least two of LOD, LOQ, action level and pass/fail, and prints no
    digits. Two headers merged side by side (a repeated column) are not
    read, so their rows fall back to the status-anchored reading.
    """
    text = ' '.join(str(line).upper().split())
    if not text or re.search(r'\d', text):
        return None
    found = []
    for column, pattern in _HEADER_COLUMNS:
        matches = list(re.finditer(pattern, text))
        if len(matches) > 1:
            return None
        if matches:
            found.append((matches[0].start(), column))
    results = list(_HEADER_RESULT.finditer(text))
    if not results or len(results) > 2:
        return None
    for k, m in enumerate(results):
        unit = (m.group(1) or '').strip()
        if 'MG' in unit:
            column = 'result_mg'
        elif '%' in unit or 'PERCENT' in unit or k == 0:
            column = 'result'
        else:
            column = 'result_2'
        found.append((m.start(), column))
    columns = [c for _, c in sorted(found)]
    if 'result' not in columns or len(columns) != len(set(columns)):
        return None
    if len({'lod', 'loq', 'limit', 'status'} & set(columns)) < 2:
        return None
    return columns

def _detection_for(location: str, default: str) -> str:
    """Which detection limit a lone number before the limit is: NY
    (Albany) prints the LOQ; FL and AZ print the LOD first."""
    if location == 'albany':
        return 'loq'
    if location in ('davie', 'gainesville', 'tempe'):
        return 'lod'
    return default

def _cell_type(token: str) -> str:
    """'number', 'result_word' (ND, <x, Present) or 'placeholder' (NA)."""
    value, qualifier, _ = _parse_result(token)
    if value is not None:
        return 'number'
    if qualifier in ('', 'NR', 'NT'):
        return 'placeholder'
    return 'result_word'

def _result_after_status(before: str, after: str, status: Optional[str]) -> bool:
    """Whether the cell after the status (rather than the one before it)
    is the result. Exactly one non-detect / bound among the two is the
    result; of two numbers, a PASS result cannot exceed its limit and a
    FAIL result must; otherwise the layout of every Kaycha table seen
    so far applies (result after the status)."""
    a, b = _cell_type(after), _cell_type(before)
    if a != b:
        if 'placeholder' in (a, b):
            return b == 'placeholder'
        return a == 'result_word'
    if a == 'number' and status in ('pass', 'fail'):
        x, y = _parse_result(after)[0], _parse_result(before)[0]
        if x != y:
            return x < y if status == 'pass' else x > y
    return True

def _detection_limits(cells: List[str], detection: str,
                      units_first: bool) -> Tuple[Optional[float], Optional[float]]:
    """(lod, loq) from the detection cells before the limit: two cells
    are LOD then LOQ (AZ); one is the state's detection limit."""
    nums = [_parse_number(t) for t in cells if _cell_type(t) == 'number']
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        if detection == 'loq' and not units_first:
            return None, nums[0]
        return nums[0], None
    return None, None

def _read_row(tokens: List[str], layout: Optional[List[str]] = None,
              detection: str = 'lod', terpene: bool = False,
              ordered: bool = False) -> Optional[Dict]:
    """Read the cells after an analyte name.

    Returns a dict with 'value', 'qualifier', 'units', 'lod', 'loq',
    'limit', 'status', 'n_values' (cells read) and 'extra' (further
    result cells, e.g. mg/unit), or None when the row has no value.

    1. Header: when the page printed a header row and its numeric
       columns match the row's value cells one to one, each cell is
       what its column says.
    2. Status anchor: with cells on both sides of PASS/FAIL/TESTED, the
       result is the first cell after it unless _result_after_status
       says the cell before it is; a PASS/FAIL row's cell before the
       result is its limit, and the cells before that are LOD/LOQ.
       Never the last number of the row: in "ppm 0.0100 0.2000 0.4
       PASS ND" that is the limit 0.4. Cells are compared only when
       the row prints more cells before the status than its detection
       limits (one LOD or LOQ, or the LOD and LOQ after units): with
       none more, there is no limit to mistake the result for
       ("BIFENAZATE 0.1000 ppm PASS 0.1500" is 0.15, not its LOQ). A
       row whose cells are known to be in the documented order
       (``ordered``: the FL pesticide pattern) is never reordered.
       A number before the status with nothing after it may be a limit
       or a result: it is not read (a result word, "ND", is).
    3. No status cell: detection limit(s) first, then the result (the
       last cell; for terpenes the first cell after the LOQ, since a
       mg/unit cell may follow).
    """
    cells = []
    started = False
    for token in tokens:
        kind = _token_kind(token)
        if kind == 'other':
            if _FLAG_TOKEN.match(token) or not any(c.isalnum() for c in token):
                continue
            if started and _RECORD_START.match(token):
                break  # A second record merged onto the line.
            continue
        if kind in ('value', 'status'):
            started = True
        cells.append((kind, token))
    values = [(i, t) for i, (kind, t) in enumerate(cells) if kind == 'value']
    if not values:
        return None
    units = next((t.lower() for kind, t in cells if kind == 'unit'), None)
    status_at = next((i for i, (kind, _) in enumerate(cells) if kind == 'status'), None)
    status = _STATUS_WORDS[cells[status_at][1].upper()] if status_at is not None else None
    units_first = any(kind == 'unit' for kind, _ in cells[:values[0][0]])
    value_tokens = [t for _, t in values]

    result = limit = None
    detection_cells, extra = [], []
    columns = [c for c in (layout or []) if c in ('lod', 'loq', 'limit') or c.startswith('result')]
    fits = bool(columns) and len(columns) == len(value_tokens)
    if fits and status_at is not None and 'status' in layout:
        # The header's status falls where the row's does: a header from
        # another table (terpenes' "RESULT (%) RESULT (mg/g)") with as
        # many value columns would put the action limit in the result.
        printed_before = sum(1 for i, _ in values if i < status_at)
        fits = printed_before == sum(1 for c in layout[:layout.index('status')] if c in columns)
    if fits:
        # 1. Header-driven.
        assigned = dict(zip(columns, value_tokens, strict=True))
        result = assigned.get('result')
        limit = assigned.get('limit')
        extra = [assigned[c] for c in columns if c.startswith('result') and c != 'result']
        lod = _parse_number(assigned['lod']) if 'lod' in assigned else None
        loq = _parse_number(assigned['loq']) if 'loq' in assigned else None
    else:
        if status_at is not None:
            before = [t for i, t in values if i < status_at]
            after = [t for i, t in values if i > status_at]
        else:
            before, after = value_tokens, []
        n_detect = 2 if units_first else 1
        if before and after:
            # 2. Status-anchored.
            has_limit = len(before) > n_detect
            if ordered or not has_limit or _result_after_status(before[-1], after[0], status):
                result, extra = after[0], after[1:]
                if has_limit:
                    limit, detection_cells = before[-1], before[:-1]
                else:
                    detection_cells = before
            else:
                result, limit = before[-1], after[0]
                detection_cells, extra = before[:-1], after[1:]
        elif after:
            result, extra = after[0], after[1:]
        elif status_at is not None:
            if _cell_type(before[-1]) == 'number':
                return None   # a limit or a result: which, the row does not say
            result, detection_cells = before[-1], before[:-1]
        else:
            # 3. No status cell.
            n = 2 if units_first else 1
            if terpene and len(before) > n:
                detection_cells, result, extra = before[:n], before[n], before[n + 1:]
            else:
                result = before[-1]
                detection_cells = before[:-1][:n]
                middle = before[n:-1]
                limit = middle[-1] if middle else None
        lod, loq = _detection_limits(detection_cells, detection, units_first)

    value, qualifier, bound = _parse_result(result)
    if bound is not None:
        if qualifier == '<LOQ' and loq is None:
            loq = bound
        elif qualifier == '<LOD' and lod is None:
            lod = bound
    return {
        'value': value,
        'qualifier': qualifier,
        'units': units,
        'lod': lod,
        'loq': loq,
        'limit': _parse_number(limit) if limit else None,
        'status': status,
        'n_values': len(value_tokens),
        'extra': extra,
    }

def _read_word_row(cells: List[str], layout: Optional[List[str]] = None,
                   detection: str = 'lod') -> Optional[Tuple[Dict, str]]:
    """Read a row whose result is a word ("Not Present", "Detected"),
    or None when it has none. Cells after the word other than a status
    are dropped, so "Not Detected in 1 g PASS" is not read as 1. Of two
    words, the one nearer the status is the result.
    Returns the row and the status to assume when none is printed
    ('pass' for a non-detect, '' otherwise)."""
    status_at = next((k for k, c in enumerate(cells) if _token_kind(c) == 'status'), len(cells))
    words = [k for k, c in enumerate(cells[:status_at]) if c.upper() in _WORD_RESULTS]
    if not words:
        words = [k for k, c in enumerate(cells) if c.upper() in _WORD_RESULTS]
    if not words:
        return None
    # The last word before the status: a limit printed in words comes
    # first ("Not Detected in 1 g  Detected  FAIL" detected salmonella).
    word_at = words[-1]
    statuses = [c for c in cells[word_at + 1:] if _token_kind(c) == 'status'][:1]
    # The cells before the first word are the row's (LOQ, units); those
    # between the two words belong to the limit ("in 1 g").
    row = _read_row(cells[:words[0]] + [cells[word_at]] + statuses, layout=layout, detection=detection)
    if row is None:
        return None
    return row, 'pass' if cells[word_at].upper() in _PATHOGEN_RESULTS else ''

def _result_record(analysis: str, name: str, row: Dict,
                   units: Optional[str] = None,
                   status: Optional[str] = None) -> Dict:
    """One result dict in the module's output form."""
    return {
        'analysis': analysis,
        'key': _snake_case(name),
        'name': name,
        'value': row['value'],
        'qualifier': row['qualifier'],
        'units': units if units is not None else row['units'],
        'lod': row['lod'],
        'loq': row['loq'],
        'limit': row['limit'],
        'status': status if status is not None else row['status'],
    }

# ── Cannabinoid Parsing ────────────────────────────────────────────

# The D10-THC isomer labels, printed above 'D10-THC' in NY headers.
_D10_LABEL = re.compile(r'\(\s*6A?R\s*,\s*9\s*([RS])\s*\)', re.IGNORECASE)
_D10_NAMES = {'R': '(6AR,9R) D10-THC', 'S': '(6AR,9S) D10-THC'}

def _cannabinoid_header(lines: List[str], i: int) -> Tuple[List[str], List[str]]:
    """The analyte names over the '%' row at ``lines[i]``, and the D10-THC
    isomer columns printed in the header block (up to 8 lines above).

    Names come from the nearest lines above the '%' row, stopping once
    five names are found. In NY headers the isomer columns print as
    '(6AR,9R)' and 'D10-THC' on lines of their own, which that search
    either misses or appends after THCV; they are returned separately
    so that _align_cannabinoids can put them where their cells are.
    """
    header_line = ''
    for lookback in range(1, 4):
        if i - lookback >= 0:
            candidate = lines[i - lookback]
            # Skip non-header lines.
            if candidate.startswith('mg') or candidate.startswith('LOD') or candidate.startswith('LOQ'):
                continue
            if any(x in candidate for x in ['Total THC', 'Container', 'SAFETY']):
                continue
            header_line = candidate + ' ' + header_line
            # Stop if we have enough analyte names.
            names_found = re.findall(r'[A-Z][A-Z0-9\-]+', header_line)
            if len(names_found) >= 5:
                break
    # Drop the isomer labels, summary columns ("TOTAL CAN NABINOIDS
    # (DRY)") and column captions.
    header_clean = _D10_LABEL.sub(' ', header_line)
    names = [
        n for n in header_clean.split()
        if n not in ('(DRY)', 'TOTAL', 'CAN', 'NABINOIDS', 'Analyte', 'Qualifier')
    ]
    # The D10-THC isomer columns anywhere in the header block.
    isomers, d10_tokens = [], 0
    for candidate in lines[max(0, i - 8):i]:
        for m in _D10_LABEL.finditer(candidate):
            if m.group(1).upper() not in isomers:
                isomers.append(m.group(1).upper())
        d10_tokens += sum(
            1 for t in _D10_LABEL.sub(' ', candidate).split()
            if t.strip('()-,').upper() == 'D10-THC'
        )
    count = min(2, max(len(isomers), d10_tokens))
    order = isomers + [x for x in ('R', 'S') if x not in isomers]
    return names, [_D10_NAMES[x] for x in order[:count]]

def _total_thc_check(pairs: List[Tuple[str, int]], cells: List[str],
                     total_thc: Optional[float]) -> Optional[bool]:
    """Whether an alignment agrees with the printed Total THC
    (D9-THC + 0.877 * THCA, within 2% or 0.01 points); None when the
    COA prints no usable Total THC or the alignment has neither."""
    if total_thc is None or not 0 < total_thc <= 100:
        return None
    found = {}
    for name, idx in pairs:
        key = _snake_case(name)
        if key in ('delta_9_thc', 'thca'):
            found[key] = _parse_result(cells[idx])[0] or 0.0
    if not found:
        return None
    computed = found.get('delta_9_thc', 0.0) + 0.877 * found.get('thca', 0.0)
    return abs(computed - total_thc) <= max(0.02 * total_thc, 0.01)

def _align_cannabinoids(names: List[str], d10_names: List[str],
                        cells: List[str],
                        total_thc: Optional[float]) -> List[Tuple[str, int]]:
    """Pair each analyte name with the index of its cell in the '%' row.

    The header explains the row when the counts agree: the D10-THC
    isomers lead the row (NY: 13 cells for the 11 names on the line
    above plus 2 isomers), or the row has one cell per name. The
    alignment is then checked against the printed Total THC. If it
    disagrees and another alignment (the names as parsed, or the names
    shifted right past unexplained leading cells) agrees, that one is
    used. If none agrees: a header-explained alignment is kept (the
    total may be printed per unit or misread); an unexplained one is
    dropped, so no misaligned value is emitted.
    """
    n = len(cells)
    others = [name for name in names if 'D10' not in name.upper()]

    def pairs_for(name_list: List[str], offset: int = 0) -> List[Tuple[str, int]]:
        return [(name, offset + j) for j, name in enumerate(name_list) if offset + j < n]

    if d10_names and n == len(others) + len(d10_names):
        primary, explained = pairs_for(d10_names + others), True
    elif n == len(names):
        primary, explained = pairs_for(names), True
    elif n == len(others):
        primary, explained = pairs_for(others), True
    else:
        primary, explained = pairs_for(names), False
    if _total_thc_check(primary, cells, total_thc) is not False:
        return primary
    alternatives = [pairs_for(names), pairs_for(others)]
    if d10_names:
        alternatives.append(pairs_for(d10_names + others))
    alternatives += [pairs_for(others, k) for k in range(1, n - len(others) + 1)]
    for alternative in alternatives:
        if alternative != primary and _total_thc_check(alternative, cells, total_thc):
            logger.warning(
                'Kaycha cannabinoids: header alignment contradicts Total THC '
                '%s; using the alignment that agrees with it.', total_thc,
            )
            return alternative
    if explained:
        logger.warning(
            'Kaycha cannabinoids: D9-THC + 0.877 * THCA disagrees with the '
            'printed Total THC %s; keeping the header alignment.', total_thc,
        )
        return primary
    logger.warning(
        'Kaycha cannabinoids: %d cells for %d names and no alignment agrees '
        'with Total THC %s; cannabinoid rows dropped.', n, len(names), total_thc,
    )
    return []

def _limit_cell(row: List[Optional[float]], idx: int, position: int,
                n_cells: int) -> Optional[float]:
    """The LOD/LOQ for a cannabinoid: a full LOD/LOQ row has a cell per
    '%' cell (index ``idx``); a shorter one a cell per name."""
    if len(row) == n_cells:
        return row[idx]
    return row[position] if position < len(row) else None

def _parse_cannabinoids(text: str, lines: List[str],
                        totals: Optional[Dict] = None) -> List[Dict]:
    """Parse cannabinoid results from page 1.

    Layout: a header line of analyte names, the '%' row of results,
    then 'mg/g', 'LOD' and 'LOQ' rows with one cell per analyte:

        D9-THC THCA CBD CBDA D8-THC CBG CBGA CBN THCV CBDV CBC
        % 0.677 27.824 ND 0.048 ND 0.170 0.401 ND ND ND ND

    NY COAs lead the row with the two D10-THC isomers, whose names
    print on separate lines ('(6AR,9R)' over 'D10-THC'):

        (6AR,9R) (6AR,9S)
        CBC CBD CBDA CBDV CBG CBGA D8-THC CBN D9-THC THCA THCV
        D10-THC D10-THC
        % <0.1000 <0.1000 <0.1000 <0.1000 0.1100 ... 35.5712 <0.1000

    The cells are paired with names by _align_cannabinoids. ``totals``
    is _parse_totals' output (computed from the page when omitted).
    """
    results = []
    if totals is None:
        totals = _parse_totals(text, lines)

    # Find the % row (cannabinoid values).
    for i, line in enumerate(lines):
        if not line.startswith('%'):
            continue

        names, d10_names = _cannabinoid_header(lines, i)

        # Parse values from the % line (qualifier flags such as Q3 are
        # not cells).
        values_text = line.lstrip('% ').split('Analyte')[0].strip()
        cells = [v.rstrip('%') for v in values_text.split()]
        cells = [v for v in cells if v and not _FLAG_TOKEN.match(v)]

        # Find LOD/LOQ line.
        lod_values = []
        loq_values = []
        for j in range(i + 1, min(i + 5, len(lines))):
            if lines[j].startswith('LOD'):
                lod_parts = lines[j].lstrip('LOD ').split()
                lod_values = [_parse_number(v) for v in lod_parts if re.match(r'^[\d.]+$', v)]
            if lines[j].startswith('LOQ'):
                loq_parts = lines[j].lstrip('LOQ ').split()
                loq_values = [_parse_number(v) for v in loq_parts if re.match(r'^[\d.]+$', v)]

        # Build results.
        pairs = _align_cannabinoids(names, d10_names, cells, totals.get('total_thc'))
        for position, (name, idx) in enumerate(pairs):
            value, qualifier, bound = _parse_result(cells[idx])
            lod = _limit_cell(lod_values, idx, position, len(cells))
            loq = _limit_cell(loq_values, idx, position, len(cells))
            if bound is not None and qualifier == '<LOQ' and loq is None:
                loq = bound
            elif bound is not None and qualifier == '<LOD' and lod is None:
                lod = bound
            results.append({
                'analysis': 'cannabinoids',
                'key': _snake_case(name),
                'name': name,
                'value': value,
                'qualifier': qualifier,
                'units': 'percent',
                'lod': lod,
                'loq': loq,
            })

        break  # Only parse the first % row.

    return results

# ── Terpene Parsing ────────────────────────────────────────────────

def _parse_terpenes_fl(page_text: str) -> Tuple[List[Dict], Optional[float]]:
    """Parse terpenes from FL-format two-column layout."""
    results = []
    total_terpenes = None

    if 'Terpenes' not in page_text:
        return results, total_terpenes

    # Get total terpenes from "Total (%)" line.
    m = re.search(r'Total\s*\(%?\)\s*[\n\s]*([\d.]+|ND)', page_text)
    if m and m.group(1) != 'ND':
        total_terpenes = _parse_result(m.group(1))[0]

    # Parse individual terpene lines.
    # FL format: "ANALYTE_NAME  LOD  mg/unit  Result(%)"
    # Two columns merged by pdfplumber.
    lines = page_text.split('\n')
    for line in lines:
        # Skip non-data lines.
        if not line or line.startswith('Terpenes') or line.startswith('(%)'):
            continue
        if 'Analyzed by' in line or 'Analysis Method' in line:
            continue
        if 'Total (%)' in line or 'Certificate' in line or 'Kaycha' in line:
            continue
        if 'Terpenoid testing' in line or 'Reviewed On' in line:
            continue
        if 'Batch Date' in line or 'Dilution' in line or 'Reagent' in line:
            continue
        if 'Consumables' in line or 'Pipette' in line or 'Instrument' in line:
            continue
        if 'Analytical Batch' in line or 'SOP.' in line:
            continue

        # Match terpene data pattern: NAME  number  number  number
        # or NAME  number  ND  ND
        m = re.match(
            r'^([A-Z][A-Z0-9\- ]+?)\s+'
            r'([\d.]+)\s+'     # LOD
            r'([\d.]+|ND|<[\d.]+)\s+'  # mg/unit or ND
            r'([\d.]+|ND|<[\d.]+)',    # Result (%)
            line.strip()
        )
        if m:
            name = m.group(1).strip()
            value, qualifier, bound = _parse_result(m.group(4))
            if name == 'TOTAL TERPENES':
                if total_terpenes is None:
                    total_terpenes = value
                continue
            key = _snake_case(name)
            results.append({
                'analysis': 'terpenes',
                'key': key,
                'name': name,
                'value': value,
                'qualifier': qualifier,
                'units': 'percent',
                'lod': _parse_number(m.group(2)),
                'loq': bound if qualifier == '<LOQ' else None,
                'limit': None,
                'status': None,
            })

    return results, total_terpenes

def _parse_terpenes_tabular(page_text: str,
                            location: str = '') -> Tuple[List[Dict], Optional[float]]:
    """Parse terpenes from NY/AZ tabular ANALYTES format.

    NY rows print the LOQ, the action limit, the status and then two
    results, percent first and mg per unit second (for a 1 g unit the
    mg/unit is 10x the percent):

        TOTAL TERPENES 0.1000 11.5 PASS 1.9000 19.0000
        LIMONENE 0.0040 10 PASS 0.5100 5.1000
        FARNESENE 0.0400 10 PASS <0.0400 <0.4000

    The percent cell is read (from the header row when printed, else
    as the first cell after the status), never the last number below
    15, which was the mg/unit cell (limonene 5.1 for 0.51%) or, for a
    "<LOQ" row, the LOQ in mg (0.4). The individual results are checked
    against the COA's own TOTAL TERPENES row.
    """
    results = []
    total_terpenes = None
    detection = _detection_for(location, 'loq')

    lines = page_text.split('\n')
    in_terpenes = False
    layout = None

    for line in lines:
        if 'Terpenes' in line and ('PASSED' in line or 'TESTED' in line):
            in_terpenes = True
            continue
        if not in_terpenes:
            continue
        # Stop at next section or metadata.
        if 'Analyzed' in line or 'Analysis Method' in line or 'Weight:' in line:
            break
        if any(x in line for x in ['Pesticide', 'Heavy Metal', 'Microbial',
                                    'Mycotoxin', 'Residual', 'Filth', 'Water Activity']):
            break

        # Header line: read its column order, then skip it.
        if line.startswith('ANALYTES'):
            layout = _parse_header(line)
            continue
        if line.startswith('Terpenes'):
            continue
        header = _parse_header(line)
        if header:
            layout = header
            continue

        parts = line.strip().split()
        if len(parts) < 3:
            continue

        # The analyte name is the words before the first cell.
        name_tokens, cells = _split_name(_tokenize(line.strip()))
        name = ' '.join(name_tokens)
        if not name or not name[0].isalpha():
            continue
        row = _read_row(cells, layout=layout, detection=detection, terpene=True)
        if row is None:
            continue

        if name.upper() == 'TOTAL TERPENES':
            total_terpenes = row['value']
            continue
        results.append(_result_record('terpenes', name, row, units='percent'))

    # Consistency check: the individual percents add up to the total.
    measured = [r['value'] for r in results if r['value'] is not None]
    if total_terpenes is not None and measured:
        if abs(sum(measured) - total_terpenes) > max(0.15 * total_terpenes, 0.05):
            logger.warning(
                'Kaycha terpenes: results sum to %.4f%% but TOTAL TERPENES '
                'reads %.4f%%; check the column order.', sum(measured), total_terpenes,
            )

    return results, total_terpenes

# ── Pesticide Parsing ──────────────────────────────────────────────

def _parse_pesticides_fl(page_text: str, location: str = '') -> List[Dict]:
    """Parse pesticides from FL two-column format.

    Rows are "NAME LOD UNITS LIMIT STATUS RESULT". The result is the
    first token after the status; any text after it (a second column
    merged onto the line by pdfplumber) is not part of it.
    """
    results = []
    detection = _detection_for(location, 'lod')
    lines = page_text.split('\n')

    for line in lines:
        if 'Analyzed by' in line or 'Analysis Method' in line:
            continue
        if not line or 'Pesticide' in line and 'LOD' in line:
            continue
        if any(x in line for x in ['SOP.', 'Reviewed', 'Batch Date',
                                     'Dilution', 'Reagent', 'Consumables',
                                     'Pipette', 'Testing for', 'Instrument',
                                     'Certificate', 'Kaycha', 'accordance']):
            continue

        # FL format: "ABAMECTIN B1A 0.010 ppm 0.1 PASS ND"
        # Also: "PENTACHLORONITROBENZENE (PCNB) * 0.010 PPM 0.15 PASS ND"
        line_clean = line.replace('*', '').strip()
        if not line_clean:
            continue

        m = re.match(
            r'^([A-Z][A-Z0-9\- ()]+?)\s+'
            r'([\d.]+)\s+'      # LOD
            r'(ppm|PPM|ppb|PPB)\s+'  # units
            r'([\d.]+)\s+'      # action level
            r'(PASS|FAIL)\s+'   # status
            r'(.+)$',           # result
            line_clean
        )
        if m:
            name = m.group(1).strip()
            if name.upper() in SKIP_KEYWORDS:
                continue
            result_cell = _tokenize(m.group(6))[:1]
            if not result_cell or _token_kind(result_cell[0]) != 'value':
                continue  # No readable result after the status.
            row = _read_row(
                [m.group(2), m.group(3), m.group(4), m.group(5)] + result_cell,
                detection=detection, ordered=True,
            )
            if row is None:
                continue
            results.append(_result_record('pesticides', name, row))

    return results

def _parse_pesticides_tabular(page_text: str, location: str = '') -> List[Dict]:
    """Parse pesticides from NY/AZ tabular ANALYTES format.

        NY: "ACEQUINOCYL 0.1000 ppm 2 PASS <0.1000"
            LOQ UNITS LIMIT STATUS RESULT
        AZ: "ACEPHATE ppm 0.0100 0.2000 0.4 PASS ND"
            UNITS LOD LOQ LIMIT STATUS RESULT

    The result is the cell after the status (see _read_row). Until
    10/13/2026 it was the row's last number, so every AZ non-detect
    was reported as its action limit (acephate 0.4 ppm).
    """
    results = []
    detection = _detection_for(location, 'loq')
    lines = page_text.split('\n')
    in_pesticides = False
    layout = None

    for line in lines:
        if 'Pesticide' in line and ('PASSED' in line or 'FAILED' in line):
            in_pesticides = True
            layout = None        # a header read before is another table's
            continue
        if line.startswith('ANALYTES'):
            layout = _parse_header(line)
            continue
        if not in_pesticides:
            continue
        if 'Analyzed' in line or 'Analysis Method' in line or 'Weight:' in line:
            in_pesticides = False
            continue
        header = _parse_header(line)
        if header:
            layout = header
            continue

        line_clean = line.strip()
        if not line_clean or not line_clean[0].isalpha():
            continue
        parts = line_clean.split()
        if len(parts) < 4:
            continue

        # Find analyte name.
        name_tokens, cells = _split_name(_tokenize(line_clean))
        name = ' '.join(name_tokens)
        if not name:
            continue
        if name.upper() in SKIP_KEYWORDS:
            continue
        row = _read_row(cells, layout=layout, detection=detection)
        if row is None:
            continue
        results.append(_result_record('pesticides', name, row, units=row['units'] or 'ppm'))

    return results

# ── Other Analysis Parsing ─────────────────────────────────────────

def _parse_section_fl(page_text: str, section_name: str, analysis: str,
                       default_units: str, location: str = '') -> List[Dict]:
    """Parse a results section from FL-format pages.
    Works for: residual_solvents, heavy_metals, microbials, mycotoxins,
    foreign_matter, water_activity, moisture. NY and AZ COAs whose page
    1 is not tabular are parsed here too.

    Row layouts:
        "ACETONE 75.000 ppm 750 PASS ND"          LOD UNITS LIMIT STATUS RESULT
        "DIMETHYL SULFOXIDE 375.0000 ppm 5000 PASS <375.0000"   (NY, LOQ)
        "ARSENIC ppm 0.0660 0.2000 0.4 PASS ND"  (AZ, units first)
        "ASPERGILLUS TERREUS Not Present PASS"   (pathogens)

    Some tables print "LOD UNITS RESULT STATUS LIMIT" instead. The
    column order comes from the section's header row when it prints one
    ("Solvents LOD Units Action Level Pass/Fail Result"); otherwise the
    cells decide (_read_row). Until 10/13/2026 the cell after the units
    was always taken as the result: in FL residual solvents that is the
    action limit (acetone 750, ethanol 5000 for "ND").
    """
    results = []
    detection = _detection_for(location, 'lod')
    lines = page_text.split('\n')
    in_section = False
    layout = None

    for line in lines:
        # Section detection (exact match to avoid Summary contamination).
        if section_name in line and any(x in line for x in ['PASSED', 'FAILED', 'TESTED']):
            in_section = True
            layout = None
            continue
        if not in_section:
            continue
        # Stop conditions.
        if 'Analyzed by' in line or 'Analysis Method' in line:
            in_section = False
            continue
        # Header rows: read the column order, then skip.
        header = _parse_header(line)
        if header:
            layout = header
            continue
        if line.startswith('Analyte') and 'LOD' in line:
            continue
        if line.startswith('Solvents') and 'LOD' in line:
            continue
        if line.startswith('Metal') and 'LOD' in line:
            continue

        line_clean = line.strip()
        if not line_clean or not (line_clean[0].isalpha() or _LOCANT_NAME.match(line_clean)):
            continue

        name_tokens, cells = _split_name(_tokenize(line_clean))
        name = ' '.join(name_tokens)
        if not name:
            continue
        word = _read_word_row(cells, layout=layout, detection=detection)
        if word:
            # "NAME Not Present PASS": a non-detect passes unless the
            # row says FAIL; "NAME Present FAIL" keeps its failure.
            row, assumed = word
            results.append(_result_record(
                analysis, name, row, units=default_units,
                status=row['status'] or assumed or None,
            ))
            continue
        if not _is_strict_name(name_tokens):
            continue
        row = _read_row(cells, layout=layout, detection=detection)
        if row is None:
            continue
        # A data row has at least two cells (a detection limit and the
        # result), or a single word result with a status ("ND PASS"),
        # and prints a status or units (not "DILUTION 10 20").
        if row['n_values'] < 2 and not (row['status'] and row['qualifier']):
            continue
        if not (row['status'] or row['units']):
            continue
        results.append(_result_record(
            analysis, name, row, units=row['units'] or default_units.lower(),
        ))

    return results

def _parse_section_tabular(page_text: str, section_name: str,
                            analysis: str, default_units: str,
                            location: str = '') -> List[Dict]:
    """Parse a results section from NY/AZ tabular ANALYTES format.

        NY: "DIMETHYL SULFOXIDE 375.0000 ppm 5000 PASS <375.0000"
        AZ: "ARSENIC ppm 0.0660 0.2000 0.4 PASS ND"
        "ESCHERICHIA COLI SHIGELLA SPP 1.0000 CFU/g Not Present PASS"

    The result is read from the header row or the status cell (see
    _read_row), never as the row's last number, which is the action
    limit when the result is a word ("<LOQ").
    """
    results = []
    detection = _detection_for(location, 'loq')
    lines = page_text.split('\n')
    in_section = False
    layout = None

    for line in lines:
        if section_name in line and any(x in line for x in ['PASSED', 'FAILED', 'TESTED']):
            in_section = True
            layout = None
            continue
        if line.startswith('ANALYTES'):
            layout = _parse_header(line)
            continue
        if not in_section:
            continue
        if 'Analyzed' in line or 'Analysis Method' in line or 'Weight:' in line:
            in_section = False
            continue
        header = _parse_header(line)
        if header:
            layout = header
            continue

        line_clean = line.strip()
        if not line_clean or not (line_clean[0].isalpha() or _LOCANT_NAME.match(line_clean)):
            continue

        name_tokens, cells = _split_name(_tokenize(line_clean))
        name = ' '.join(name_tokens)
        if not name:
            continue
        word = _read_word_row(cells, layout=layout, detection=detection)
        if word:
            # Handle "Not Present" / "Not Detected" (and "Present").
            row, assumed = word
            results.append(_result_record(
                analysis, name, row, units=default_units,
                status=row['status'] or assumed or None,
            ))
            continue
        if len(line_clean.split()) < 3:
            continue
        row = _read_row(cells, layout=layout, detection=detection)
        if row is None:
            continue
        results.append(_result_record(
            analysis, name, row, units=row['units'] or default_units,
        ))

    return results

# ── Main Parser ────────────────────────────────────────────────────

def parse_kaycha_pdf(
        parser: Any = None,
        doc: str = '',
        **kwargs,
    ) -> Dict:
    """Parse a Kaycha Labs COA PDF.

    Core parsing function. Opens the PDF with pdfplumber, extracts
    metadata from page 1, then extracts results from all pages.

    Args:
        parser: Optional CoADoc instance (backwards compat; ignored).
        doc:    Path to the COA PDF file.

    Returns:
        Dict with all extracted COA data including:
            - Metadata fields (product_name, producer, dates, etc.)
            - results: JSON string of list[dict] (analyte results)
            - analyses: JSON string of list[str] (analysis types)
    """
    pdf_path = doc if isinstance(doc, str) and doc else ''
    if isinstance(parser, str) and not pdf_path:
        pdf_path = parser
        parser = None
    if not pdf_path:
        raise ValueError('No PDF file path provided.')

    obs = {}
    all_results = []

    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            raise ValueError(f'PDF has no pages: {pdf_path}')

        # ── Phase 1: Extract page 1 text ──────────────────────
        try:
            front_text = pdf.pages[0].extract_text() or ''
            front_text = front_text.replace('\x00', '')  # Null byte cleaning.
        except Exception:
            return {}

        lines = front_text.split('\n')

        # ── Phase 2: Detect location and format ───────────────
        location = _detect_location(front_text)
        fmt = _detect_format(front_text, location)
        is_tabular = fmt in ('ny_medical', 'az_tabular')

        # ── Phase 3: Parse metadata ───────────────────────────
        obs = _parse_metadata(front_text, lines, location)
        totals = _parse_totals(front_text, lines)
        obs.update(totals)
        status_obs, analyses = _parse_safety_statuses(front_text)
        obs.update(status_obs)

        # ── Phase 4: Parse cannabinoids from page 1 ──────────
        cannabinoid_results = _parse_cannabinoids(front_text, lines, totals=totals)
        if cannabinoid_results:
            all_results.extend(cannabinoid_results)
            if 'cannabinoids' not in analyses:
                analyses.append('cannabinoids')

        # ── Phase 5: Parse remaining pages ────────────────────
        for page_idx in range(1, len(pdf.pages)):
            try:
                page_text = pdf.pages[page_idx].extract_text() or ''
                page_text = page_text.replace('\x00', '')
            except Exception:
                continue

            # -- Terpenes --
            if 'Terpenes' in page_text and ('TESTED' in page_text or 'PASSED' in page_text):
                if is_tabular or location in ('albany', 'tempe'):
                    terp_results, total_terp = _parse_terpenes_tabular(page_text, location=location)
                else:
                    terp_results, total_terp = _parse_terpenes_fl(page_text)
                if terp_results:
                    all_results.extend(terp_results)
                    if 'terpenes' not in analyses:
                        analyses.append('terpenes')
                if total_terp is not None:
                    obs['total_terpenes'] = total_terp

            # -- Pesticides --
            if 'Pesticide' in page_text and ('PASSED' in page_text or 'FAILED' in page_text):
                if is_tabular or location in ('albany', 'tempe'):
                    pest_results = _parse_pesticides_tabular(page_text, location=location)
                else:
                    pest_results = _parse_pesticides_fl(page_text, location=location)
                if pest_results:
                    all_results.extend(pest_results)
                    if 'pesticides' not in analyses:
                        analyses.append('pesticides')

            # -- Residual Solvents --
            if 'Residual Solvents' in page_text or 'Residual' in page_text and 'Solvent' in page_text:
                section = 'Residual Solvents' if 'Residual Solvents' in page_text else 'Solvents'
                if is_tabular:
                    sol_results = _parse_section_tabular(page_text, section, 'residual_solvents', 'ppm', location=location)
                else:
                    sol_results = _parse_section_fl(page_text, section, 'residual_solvents', 'ppm', location=location)
                if sol_results:
                    all_results.extend(sol_results)
                    if 'residual_solvents' not in analyses:
                        analyses.append('residual_solvents')

            # -- Microbials --
            if 'Microbial' in page_text and ('PASSED' in page_text or 'FAILED' in page_text):
                if is_tabular:
                    mic_results = _parse_section_tabular(page_text, 'Microbial', 'microbials', 'CFU/g', location=location)
                else:
                    mic_results = _parse_section_fl(page_text, 'Microbial', 'microbials', 'CFU/g', location=location)
                if mic_results:
                    all_results.extend(mic_results)
                    if 'microbials' not in analyses:
                        analyses.append('microbials')

            # -- Mycotoxins --
            if 'Mycotoxin' in page_text and ('PASSED' in page_text or 'FAILED' in page_text):
                if is_tabular:
                    myc_results = _parse_section_tabular(page_text, 'Mycotoxin', 'mycotoxins', 'ppm', location=location)
                else:
                    myc_results = _parse_section_fl(page_text, 'Mycotoxin', 'mycotoxins', 'ppm', location=location)
                if myc_results:
                    all_results.extend(myc_results)
                    if 'mycotoxins' not in analyses:
                        analyses.append('mycotoxins')

            # -- Heavy Metals --
            if 'Heavy Metal' in page_text and ('PASSED' in page_text or 'FAILED' in page_text):
                if is_tabular:
                    hm_results = _parse_section_tabular(page_text, 'Heavy Metal', 'heavy_metals', 'ppm', location=location)
                else:
                    hm_results = _parse_section_fl(page_text, 'Heavy Metal', 'heavy_metals', 'ppm', location=location)
                if hm_results:
                    all_results.extend(hm_results)
                    if 'heavy_metals' not in analyses:
                        analyses.append('heavy_metals')

            # -- Filth / Foreign Material --
            if ('Filth' in page_text or 'Foreign' in page_text) and \
               ('PASSED' in page_text or 'FAILED' in page_text):
                section = 'Filth' if 'Filth' in page_text else 'Foreign'
                if is_tabular:
                    fm_results = _parse_section_tabular(page_text, section, 'foreign_matter', 'percent', location=location)
                else:
                    fm_results = _parse_section_fl(page_text, section, 'foreign_matter', 'percent', location=location)
                if fm_results:
                    all_results.extend(fm_results)
                    if 'foreign_matter' not in analyses:
                        analyses.append('foreign_matter')

            # -- Water Activity --
            if 'Water Activity' in page_text and ('PASSED' in page_text or 'TESTED' in page_text):
                if is_tabular:
                    wa_results = _parse_section_tabular(page_text, 'Water Activity', 'water_activity', 'aw', location=location)
                else:
                    wa_results = _parse_section_fl(page_text, 'Water Activity', 'water_activity', 'aw', location=location)
                if wa_results:
                    all_results.extend(wa_results)
                    if 'water_activity' not in analyses:
                        analyses.append('water_activity')

            # -- Moisture --
            if 'Moisture' in page_text and ('PASSED' in page_text or 'TESTED' in page_text):
                if 'Moisture Content' in page_text or 'Moisture' in page_text:
                    if is_tabular:
                        mo_results = _parse_section_tabular(page_text, 'Moisture', 'moisture', 'percent', location=location)
                    else:
                        mo_results = _parse_section_fl(page_text, 'Moisture', 'moisture', 'percent', location=location)
                    if mo_results:
                        all_results.extend(mo_results)
                        if 'moisture' not in analyses:
                            analyses.append('moisture')

            # -- FL page 1 inline sections (Gainesville 2022 format) --
            # Filth, Water Activity, Moisture on page 1.
            if page_idx == 0:
                for section_kw, analysis_name, units in [
                    ('Filth', 'foreign_matter', 'percent'),
                    ('Water Activity', 'water_activity', 'aw'),
                    ('Moisture', 'moisture', 'percent'),
                ]:
                    if section_kw in page_text and analysis_name not in analyses:
                        inline_results = _parse_section_fl(page_text, section_kw, analysis_name, units)
                        if inline_results:
                            all_results.extend(inline_results)
                            analyses.append(analysis_name)

        # ── Phase 6: Extract methods ─────────────────────────
        methods = []
        for page in pdf.pages:
            try:
                pt = page.extract_text() or ''
            except Exception:
                continue
            found = re.findall(r'SOP\.[\w.\-()]+', pt)
            methods.extend(found)
        methods = sorted(set(methods))

        # ── Phase 7: Parse producer from page 2+ ─────────────
        if not obs.get('producer') and len(pdf.pages) >= 2:
            try:
                p2_text = pdf.pages[1].extract_text() or ''
                # Look for producer in the header block.
                p2_lines = p2_text.split('\n')
                for p2_line in p2_lines:
                    if 'Telephone:' in p2_line or 'Email:' in p2_line:
                        break
                    # The producer name is often the first line after
                    # "Certificate of Analysis" on page 2.
                    if p2_line and not any(x in p2_line for x in [
                        'Kaycha', 'Certificate', 'Matrix', 'Type:',
                        'Page ', 'Albany', 'Davie', 'Tempe', 'Gainesville',
                    ]):
                        candidate = p2_line.strip()
                        if candidate and len(candidate) > 2 and not candidate[0].isdigit():
                            obs['producer'] = candidate
                            break
            except Exception:
                pass

    # ── Phase 8: Build final output ──────────────────────────
    # Apply location-specific lab details.
    loc_details = KAYCHA_LOCATIONS.get(location, KAYCHA_LOCATIONS['davie'])
    obs = {**KAYCHA_LABS, **loc_details, **obs}

    # Ensure required fields have defaults.
    obs.setdefault('product_name', '')
    obs.setdefault('product_type', '')
    obs.setdefault('status', 'pass')
    obs.setdefault('date_tested', '')

    # Serialize results and analyses.
    analyses = sorted(set(analyses))
    obs['analyses'] = json.dumps(analyses)
    obs['results'] = json.dumps(all_results)
    obs['methods'] = json.dumps(methods)
    obs['coa_parsed_at'] = datetime.now().isoformat()

    # Generate hashes.
    hash_input = json.dumps(all_results, sort_keys=True)
    obs['results_hash'] = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    id_input = (
        hash_input +
        obs.get('product_name', '') +
        obs.get('producer', obs.get('distributor', '')) +
        obs.get('date_tested', '')
    )
    if not obs.get('sample_id'):
        obs['sample_id'] = hashlib.sha256(id_input.encode()).hexdigest()[:16]

    obs['lab_id'] = obs.get('sample_id', '')
    obs['coa_pdf'] = pdf_path.replace('\\', '/').split('/')[-1]

    return obs

# ── Entry Point (LAB_REGISTRY compatible) ──────────────────────────

def parse_kaycha_coa(
        parser: Any = None,
        doc: str = '',
        **kwargs,
    ) -> Dict:
    """Parse a Kaycha Labs COA PDF.

    This is the main entry point registered in the LAB_REGISTRY.
    Satisfies the algorithm contract: parse_{lab}_coa(parser, doc).

    Args:
        parser: Optional CoADoc instance (backwards compatibility).
        doc:    Path to the COA PDF file.

    Returns:
        Dict with all extracted COA data.
    """
    if isinstance(parser, str) and not doc:
        doc = parser
        parser = None

    if isinstance(doc, str) and doc.startswith('http'):
        raise ValueError(
            'URL parsing requires network access. '
            'Provide the PDF file path instead.'
        )

    return parse_kaycha_pdf(parser, doc, **kwargs)

def is_kaycha(pdf_path: str) -> bool:
    """Quick check if a PDF is a Kaycha Labs COA."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return False
            text = (pdf.pages[0].extract_text() or '').lower()
            return (
                'kaycha labs' in text
                or 'kaychalabs.com' in text
                or 'yourcoa.com' in text
            )
    except Exception:
        return False

# ── Tests ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys
    import os

    test_files = sys.argv[1:] if len(sys.argv) > 1 else []
    if not test_files:
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_files = [
            os.path.join(test_dir, f)
            for f in os.listdir(test_dir)
            if f.endswith('.pdf')
        ]

    if not test_files:
        print('Usage: python kaycha.py <pdf_file> [pdf_file2 ...]')
        sys.exit(1)

    success = 0
    fail = 0
    for pdf_file in test_files:
        pdf_path = pdf_file if os.path.isabs(pdf_file) else os.path.join(os.getcwd(), pdf_file)
        if not os.path.exists(pdf_path):
            print(f'Not found: {pdf_path}')
            continue
        try:
            data = parse_kaycha_coa(None, pdf_path)
            results = json.loads(data.get('results', '[]'))
            analyses = json.loads(data.get('analyses', '[]'))
            print(f'\n{"="*60}')
            print(f'OK {os.path.basename(pdf_file)}')
            print(f'  Product:  {data.get("product_name", "?")}')
            print(f'  Type:     {data.get("product_type", "?")}')
            print(f'  Producer: {data.get("producer", data.get("distributor", "?"))}')
            print(f'  Lab:      {data.get("lab_city", "?")} {data.get("lab_state", "?")}')
            print(f'  Date:     {data.get("date_tested", "?")}')
            print(f'  THC:      {data.get("total_thc", "?")}%')
            print(f'  CBD:      {data.get("total_cbd", "?")}%')
            print(f'  Terpenes: {data.get("total_terpenes", "?")}%')
            print(f'  Status:   {data.get("status", "?")}')
            print(f'  Sample:   {data.get("sample_id", "?")}')
            print(f'  Batch:    {data.get("batch_number", "?")}')
            print(f'  Analyses: {analyses}')
            print(f'  Results:  {len(results)} analytes')
            # Show per-analysis counts.
            from collections import Counter
            counts = Counter(r.get('analysis') for r in results)
            for a, c in sorted(counts.items()):
                print(f'    {a}: {c}')
            success += 1
        except Exception as e:
            print(f'\nFAIL {os.path.basename(pdf_file)}: {e}')
            import traceback
            traceback.print_exc()
            fail += 1

    print(f'\n{"="*60}')
    print(f'Results: {success} OK, {fail} FAIL out of {success + fail}')
