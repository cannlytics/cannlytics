"""
Parse Kaycha Labs COA -- COA Doc Hybrid Algorithm (Offline-First)
Copyright (c) 2022-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/17/2022
Updated: 3/6/2026
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
    '(6AR,9R) D10-THC': 'delta_10_thc_9r',
    '(6AR,9S) D10-THC': 'delta_10_thc_9s',
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
    """Parse a numeric value from text.
    Handles: ND, 'Not Present', '<LOQ', '<0.100', numeric values, '0'.
    Returns None for ND/Not Present, float otherwise.
    """
    if text is None:
        return None
    t = text.strip().replace(',', '')
    if not t or t in ('ND', 'N/A', 'Not Present', 'Not Detected', ''):
        return None
    if t.startswith('Not '):
        return None
    # Handle <LOQ or <value patterns.
    if t.startswith('<'):
        t = t[1:]
    # Strip qualifier flags (e.g., "0.1575 Q3" -> "0.1575").
    t = re.sub(r'\s+[A-Z]\d+\s*$', '', t)
    # Strip trailing non-numeric chars.
    t = re.sub(r'[^0-9.\-].*$', '', t)
    try:
        val = float(t)
        return val
    except (ValueError, TypeError):
        return None


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
    """Parse total THC, CBD, and cannabinoids from page 1."""
    obs = {}
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
                    if re.match(r'^<?[\d.]+$', t_clean):
                        values.append(t_clean)
                if len(values) >= 1:
                    obs['total_thc'] = _parse_number(values[0])
                if len(values) >= 2:
                    obs['total_cbd'] = _parse_number(values[1])
                if len(values) >= 3:
                    obs['total_cannabinoids'] = _parse_number(values[2])
            break

    # Try alternate layout where totals are on separate lines (NY medical).
    if obs.get('total_thc') is None:
        m = re.search(r'Total THC\s*[\n:]*\s*([\d.]+)\s*%', text)
        if m:
            obs['total_thc'] = _parse_number(m.group(1))
    if obs.get('total_cbd') is None:
        m = re.search(r'Total CBD\s*[\n:]*\s*([\d.]+)\s*%', text)
        if m:
            obs['total_cbd'] = _parse_number(m.group(1))
    if obs.get('total_cannabinoids') is None:
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


# ── Cannabinoid Parsing ────────────────────────────────────────────

def _parse_cannabinoids(text: str, lines: List[str]) -> List[Dict]:
    """Parse cannabinoid results from page 1."""
    results = []

    # Find the % row (cannabinoid values).
    for i, line in enumerate(lines):
        if not line.startswith('%'):
            continue

        # Look back for analyte headers.
        # Handle multi-line headers (NY D10-THC splits across 2 lines).
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

        # Parse analyte names from header.
        # Handle special D10-THC format: "(6AR,9R)\nD10-THC"
        header_clean = re.sub(r'\(6AR,9[RS]\)\s*', '', header_line)
        analyte_names = header_clean.strip().split()

        # Clean: remove '(DRY)' and similar.
        analyte_names = [n for n in analyte_names if n not in ('(DRY)', 'TOTAL', 'CAN', 'NABINOIDS')]

        # Fix: merge "TOTAL CAN" + "NABINOIDS" -> skip (this is a summary field).
        # Filter out non-analyte tokens.
        clean_names = []
        for n in analyte_names:
            if n in ('Analyte', 'Qualifier'):
                continue
            clean_names.append(n)
        analyte_names = clean_names

        # Parse values from the % line.
        values_text = line.lstrip('% ').split('Analyte')[0].strip()
        values = values_text.split()

        # Find LOD/LOQ line.
        lod_values = []
        loq_values = []
        for j in range(i + 1, min(i + 5, len(lines))):
            if j >= len(lines):
                break
            if lines[j].startswith('LOD'):
                lod_parts = lines[j].lstrip('LOD ').split()
                lod_values = [_parse_number(v) for v in lod_parts if re.match(r'^[\d.]+$', v)]
            if lines[j].startswith('LOQ'):
                loq_parts = lines[j].lstrip('LOQ ').split()
                loq_values = [_parse_number(v) for v in loq_parts if re.match(r'^[\d.]+$', v)]

        # Build results.
        for k, name in enumerate(analyte_names):
            if k >= len(values):
                break
            # Skip summary columns.
            if name in ('TOTAL', 'CAN', 'NABINOIDS'):
                continue
            key = _snake_case(name)
            value = _parse_number(values[k])
            result = {
                'analysis': 'cannabinoids',
                'key': key,
                'name': name,
                'value': value,
                'units': 'percent',
            }
            if k < len(lod_values):
                result['lod'] = lod_values[k]
            if k < len(loq_values):
                result['loq'] = loq_values[k]
            results.append(result)

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
        total_terpenes = _parse_number(m.group(1))

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
            if name == 'TOTAL TERPENES':
                if total_terpenes is None:
                    total_terpenes = _parse_number(m.group(4))
                continue
            key = _snake_case(name)
            results.append({
                'analysis': 'terpenes',
                'key': key,
                'name': name,
                'value': _parse_number(m.group(4)),
                'units': 'percent',
                'lod': _parse_number(m.group(2)),
            })

    return results, total_terpenes


def _parse_terpenes_tabular(page_text: str) -> Tuple[List[Dict], Optional[float]]:
    """Parse terpenes from NY/AZ tabular ANALYTES format."""
    results = []
    total_terpenes = None

    lines = page_text.split('\n')
    in_terpenes = False

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

        # Skip header line.
        if line.startswith('ANALYTES') or line.startswith('Terpenes'):
            continue

        # NY tabular: "TERPINOLENE 0.00 PASS 11.900 0.3400"
        # or: "TOTAL TERPENES 0.1000 11.5 PASS 2.9300 2051.0000"
        parts = line.strip().split()
        if len(parts) < 3:
            continue

        # Find the analyte name (all uppercase words before numbers).
        name_parts = []
        value_parts = []
        for p in parts:
            if not value_parts and not re.match(r'^[<\d.]', p) and p not in ('PASS', 'FAIL', 'TESTED'):
                name_parts.append(p)
            else:
                value_parts.append(p)

        name = ' '.join(name_parts)
        if not name or not name[0].isalpha():
            continue

        # Extract numeric values from value_parts.
        nums = []
        status = None
        for v in value_parts:
            if v in ('PASS', 'FAIL', 'TESTED'):
                status = v.lower()
            elif re.match(r'^<?[\d.]+$', v):
                nums.append(v)

        if name == 'TOTAL TERPENES':
            # Find the result % value.
            for n in nums:
                val = _parse_number(n)
                if val is not None and val < 20:  # Reasonable terpene total.
                    total_terpenes = val
                    break
            continue

        key = _snake_case(name)
        value = None
        loq = None

        if nums:
            loq = _parse_number(nums[0]) if len(nums) >= 1 else None
            # The result % is typically the second-to-last or a value < 10.
            for n in reversed(nums):
                candidate = _parse_number(n)
                if candidate is not None and candidate < 15:
                    value = candidate
                    break

        results.append({
            'analysis': 'terpenes',
            'key': key,
            'name': name,
            'value': value,
            'units': 'percent',
            'loq': loq,
            'status': status,
        })

    return results, total_terpenes


# ── Pesticide Parsing ──────────────────────────────────────────────

def _parse_pesticides_fl(page_text: str) -> List[Dict]:
    """Parse pesticides from FL two-column format."""
    results = []
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
            key = _snake_case(name)
            results.append({
                'analysis': 'pesticides',
                'key': key,
                'name': name,
                'value': _parse_number(m.group(6)),
                'units': m.group(3).lower(),
                'lod': _parse_number(m.group(2)),
                'limit': _parse_number(m.group(4)),
                'status': m.group(5).lower(),
            })

    return results


def _parse_pesticides_tabular(page_text: str) -> List[Dict]:
    """Parse pesticides from NY/AZ tabular ANALYTES format."""
    results = []
    lines = page_text.split('\n')
    in_pesticides = False

    for line in lines:
        if 'Pesticide' in line and ('PASSED' in line or 'FAILED' in line):
            in_pesticides = True
            continue
        if line.startswith('ANALYTES'):
            continue
        if not in_pesticides:
            continue
        if 'Analyzed' in line or 'Analysis Method' in line or 'Weight:' in line:
            in_pesticides = False
            continue

        line_clean = line.strip()
        if not line_clean or not line_clean[0].isalpha():
            continue

        # NY: "ACEQUINOCYL 0.1000 ppm 2 PASS <0.1000"
        # AZ: "ACEPHATE ppm 0.0100 0.2000 0.4 PASS ND"
        # AZ newer: "ACEPHATE ppm 0.0100 0.2000 0.4 PASS ND"
        parts = line_clean.split()
        if len(parts) < 4:
            continue

        # Find analyte name.
        name_parts = []
        rest_parts = []
        for p in parts:
            if not rest_parts and not re.match(r'^[<\d.]', p) and p not in ('ppm', 'PPM', 'ppb', 'PPB', 'PASS', 'FAIL', 'TESTED', 'ug/g'):
                name_parts.append(p)
            else:
                rest_parts.append(p)

        name = ' '.join(name_parts)
        if not name:
            continue
        if name.upper() in SKIP_KEYWORDS:
            continue

        # Extract values.
        units = 'ppm'
        nums = []
        status = None
        qualifier = None
        for v in rest_parts:
            if v.lower() in ('ppm', 'ppb', 'ug/g', 'ug/kg'):
                units = v.lower()
            elif v in ('PASS', 'FAIL'):
                status = v.lower()
            elif re.match(r'^<?[\d.]+$', v):
                nums.append(v)
            elif re.match(r'^[A-Z]\d', v):
                qualifier = v

        key = _snake_case(name)
        value = _parse_number(nums[-1]) if nums else None
        lod = _parse_number(nums[0]) if len(nums) >= 3 else None
        loq = _parse_number(nums[1]) if len(nums) >= 4 else _parse_number(nums[0]) if len(nums) >= 2 else None
        limit = None
        if len(nums) >= 3:
            limit = _parse_number(nums[-2]) if status else _parse_number(nums[1])
        elif len(nums) >= 2 and status:
            limit = _parse_number(nums[0])

        results.append({
            'analysis': 'pesticides',
            'key': key,
            'name': name,
            'value': value,
            'units': units,
            'lod': lod,
            'limit': limit,
            'status': status,
        })

    return results


# ── Other Analysis Parsing ─────────────────────────────────────────

def _parse_section_fl(page_text: str, section_name: str, analysis: str,
                       default_units: str) -> List[Dict]:
    """Parse a results section from FL-format pages.
    Works for: residual_solvents, heavy_metals, microbials, mycotoxins,
    foreign_matter, water_activity, moisture.
    """
    results = []
    lines = page_text.split('\n')
    in_section = False

    for line in lines:
        # Section detection (exact match to avoid Summary contamination).
        if section_name in line and any(x in line for x in ['PASSED', 'FAILED', 'TESTED']):
            in_section = True
            continue
        if not in_section:
            continue
        # Stop conditions.
        if 'Analyzed by' in line or 'Analysis Method' in line:
            in_section = False
            continue
        if line.startswith('Analyte') and 'LOD' in line:
            continue
        if line.startswith('Solvents') and 'LOD' in line:
            continue
        if line.startswith('Metal') and 'LOD' in line:
            continue

        line_clean = line.strip()
        if not line_clean or not line_clean[0].isalpha():
            continue

        # General pattern: "NAME  LOD  UNITS  RESULT  STATUS  LIMIT"
        # or: "NAME  LOD  UNITS  LIMIT  STATUS  RESULT"
        # Kaycha varies the column order by analysis type.

        # Try microbial pattern (no LOD for pathogen presence).
        if 'Not Present' in line_clean:
            name = line_clean.split('Not Present')[0].strip()
            key = _snake_case(name)
            results.append({
                'analysis': analysis,
                'key': key,
                'name': name,
                'value': None,
                'units': default_units,
                'status': 'pass',
            })
            continue
        if 'Not Detected' in line_clean:
            name_match = re.match(r'^([A-Z][A-Z\s/.()]+?)\s+(?:Not Detected|ND)', line_clean)
            if name_match:
                name = name_match.group(1).strip()
                key = _snake_case(name)
                results.append({
                    'analysis': analysis,
                    'key': key,
                    'name': name,
                    'value': None,
                    'units': default_units,
                    'status': 'pass',
                })
            continue

        # General numeric pattern.
        m = re.match(
            r'^([A-Z][A-Z0-9\- (),>]+?)\s+'
            r'([\d.]+)\s+'              # LOD/LOQ
            r'(%|ppm|PPM|ppb|PPB|ug/g|ug/kg|CFU/g|aw|mg)?\s*'  # units (optional)
            r'([\d.]+|ND|<[\d.]+)\s+'   # result or limit
            r'(PASS|FAIL|TESTED)?\s*'    # status (optional)
            r'([\d.]+|ND|<[\d.]+)?',     # limit or result
            line_clean
        )
        if m:
            name = m.group(1).strip()
            key = _snake_case(name)
            units = (m.group(3) or default_units).lower()

            # Determine which value is result vs limit.
            val1 = m.group(4)
            status = (m.group(5) or '').lower() or None
            val2 = m.group(6)

            if status:
                # FL format: LOD UNITS VALUE STATUS LIMIT
                # or: LOD UNITS LIMIT STATUS RESULT
                value = _parse_number(val1)
                limit = _parse_number(val2)
            else:
                value = _parse_number(val1)
                limit = _parse_number(val2)

            results.append({
                'analysis': analysis,
                'key': key,
                'name': name,
                'value': value,
                'units': units,
                'lod': _parse_number(m.group(2)),
                'limit': limit,
                'status': status,
            })

    return results


def _parse_section_tabular(page_text: str, section_name: str,
                            analysis: str, default_units: str) -> List[Dict]:
    """Parse a results section from NY/AZ tabular ANALYTES format."""
    results = []
    lines = page_text.split('\n')
    in_section = False

    for line in lines:
        if section_name in line and any(x in line for x in ['PASSED', 'FAILED', 'TESTED']):
            in_section = True
            continue
        if line.startswith('ANALYTES'):
            continue
        if not in_section:
            continue
        if 'Analyzed' in line or 'Analysis Method' in line or 'Weight:' in line:
            in_section = False
            continue

        line_clean = line.strip()
        if not line_clean or not line_clean[0].isalpha():
            continue

        # Handle "Not Present" / "Not Detected"
        if 'Not Present' in line_clean or 'Not Detected' in line_clean:
            name = re.split(r'\s+(?:Not Present|Not Detected)', line_clean)[0].strip()
            # Remove trailing numbers/units.
            name = re.sub(r'\s+\d+\s*$', '', name).strip()
            key = _snake_case(name)
            results.append({
                'analysis': analysis,
                'key': key,
                'name': name,
                'value': None,
                'units': default_units,
                'status': 'pass',
            })
            continue

        # General tabular pattern.
        parts = line_clean.split()
        if len(parts) < 3:
            continue

        name_parts = []
        rest_parts = []
        for p in parts:
            if not rest_parts and not re.match(r'^[<\d.]', p) and p.lower() not in (
                'ppm', 'ppb', 'ug/g', 'ug/kg', 'cfu/g', 'aw', '%', 'mg',
                'pass', 'fail', 'tested'
            ):
                name_parts.append(p)
            else:
                rest_parts.append(p)

        name = ' '.join(name_parts)
        if not name:
            continue

        key = _snake_case(name)
        units = default_units
        nums = []
        status = None
        for v in rest_parts:
            if v.lower() in ('ppm', 'ppb', 'ug/g', 'ug/kg', 'cfu/g', 'aw', '%', 'mg'):
                units = v.lower()
            elif v.upper() in ('PASS', 'FAIL', 'TESTED'):
                status = v.lower()
            elif re.match(r'^<?[\d.]+$', v):
                nums.append(v)

        value = _parse_number(nums[-1]) if nums else None
        loq = _parse_number(nums[0]) if len(nums) >= 2 else None
        limit = _parse_number(nums[-2]) if len(nums) >= 3 and status else None

        results.append({
            'analysis': analysis,
            'key': key,
            'name': name,
            'value': value,
            'units': units,
            'loq': loq,
            'limit': limit,
            'status': status,
        })

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
        obs.update(_parse_totals(front_text, lines))
        status_obs, analyses = _parse_safety_statuses(front_text)
        obs.update(status_obs)

        # ── Phase 4: Parse cannabinoids from page 1 ──────────
        cannabinoid_results = _parse_cannabinoids(front_text, lines)
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
                    terp_results, total_terp = _parse_terpenes_tabular(page_text)
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
                    pest_results = _parse_pesticides_tabular(page_text)
                else:
                    pest_results = _parse_pesticides_fl(page_text)
                if pest_results:
                    all_results.extend(pest_results)
                    if 'pesticides' not in analyses:
                        analyses.append('pesticides')

            # -- Residual Solvents --
            if 'Residual Solvents' in page_text or 'Residual' in page_text and 'Solvent' in page_text:
                section = 'Residual Solvents' if 'Residual Solvents' in page_text else 'Solvents'
                if is_tabular:
                    sol_results = _parse_section_tabular(page_text, section, 'residual_solvents', 'ppm')
                else:
                    sol_results = _parse_section_fl(page_text, section, 'residual_solvents', 'ppm')
                if sol_results:
                    all_results.extend(sol_results)
                    if 'residual_solvents' not in analyses:
                        analyses.append('residual_solvents')

            # -- Microbials --
            if 'Microbial' in page_text and ('PASSED' in page_text or 'FAILED' in page_text):
                if is_tabular:
                    mic_results = _parse_section_tabular(page_text, 'Microbial', 'microbials', 'CFU/g')
                else:
                    mic_results = _parse_section_fl(page_text, 'Microbial', 'microbials', 'CFU/g')
                if mic_results:
                    all_results.extend(mic_results)
                    if 'microbials' not in analyses:
                        analyses.append('microbials')

            # -- Mycotoxins --
            if 'Mycotoxin' in page_text and ('PASSED' in page_text or 'FAILED' in page_text):
                if is_tabular:
                    myc_results = _parse_section_tabular(page_text, 'Mycotoxin', 'mycotoxins', 'ppm')
                else:
                    myc_results = _parse_section_fl(page_text, 'Mycotoxin', 'mycotoxins', 'ppm')
                if myc_results:
                    all_results.extend(myc_results)
                    if 'mycotoxins' not in analyses:
                        analyses.append('mycotoxins')

            # -- Heavy Metals --
            if 'Heavy Metal' in page_text and ('PASSED' in page_text or 'FAILED' in page_text):
                if is_tabular:
                    hm_results = _parse_section_tabular(page_text, 'Heavy Metal', 'heavy_metals', 'ppm')
                else:
                    hm_results = _parse_section_fl(page_text, 'Heavy Metal', 'heavy_metals', 'ppm')
                if hm_results:
                    all_results.extend(hm_results)
                    if 'heavy_metals' not in analyses:
                        analyses.append('heavy_metals')

            # -- Filth / Foreign Material --
            if ('Filth' in page_text or 'Foreign' in page_text) and \
               ('PASSED' in page_text or 'FAILED' in page_text):
                section = 'Filth' if 'Filth' in page_text else 'Foreign'
                if is_tabular:
                    fm_results = _parse_section_tabular(page_text, section, 'foreign_matter', 'percent')
                else:
                    fm_results = _parse_section_fl(page_text, section, 'foreign_matter', 'percent')
                if fm_results:
                    all_results.extend(fm_results)
                    if 'foreign_matter' not in analyses:
                        analyses.append('foreign_matter')

            # -- Water Activity --
            if 'Water Activity' in page_text and ('PASSED' in page_text or 'TESTED' in page_text):
                if is_tabular:
                    wa_results = _parse_section_tabular(page_text, 'Water Activity', 'water_activity', 'aw')
                else:
                    wa_results = _parse_section_fl(page_text, 'Water Activity', 'water_activity', 'aw')
                if wa_results:
                    all_results.extend(wa_results)
                    if 'water_activity' not in analyses:
                        analyses.append('water_activity')

            # -- Moisture --
            if 'Moisture' in page_text and ('PASSED' in page_text or 'TESTED' in page_text):
                if 'Moisture Content' in page_text or 'Moisture' in page_text:
                    if is_tabular:
                        mo_results = _parse_section_tabular(page_text, 'Moisture', 'moisture', 'percent')
                    else:
                        mo_results = _parse_section_fl(page_text, 'Moisture', 'moisture', 'percent')
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
