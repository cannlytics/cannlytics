"""
Parse TagLeaf LIMS COA — COA Doc Hybrid Algorithm
Copyright (c) 2022-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2022
Updated: 10/13/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse TagLeaf LIMS COA PDFs directly from the PDF text — no network
    access required. This is the hybrid-engine version that extracts all
    data from the PDF itself using pdfplumber text and table extraction.

    TagLeaf LIMS is used by multiple labs across the US, including:

        * 2 River Labs, Inc (CA)
        * BelCosta Labs (CA)
        * Green Precision Analytics (MO)
        * Verity Analytics
        * And others

    Identification:
        TagLeaf COAs contain 'lims.tagleaf.com' URLs in page footers
        (typically page 2+). The URL pattern is:
            https://lims.tagleaf.com/coa_/{id}

    Format variants handled:
        * BelCosta (CA, 2021): Lab header on line 0, no 'REGULATORY' header
        * 2 River Labs (CA, 2022): 'REGULATORY COMPLIANCE TESTING' header
        * Green Precision Analytics (MO, 2022-2024): Standard GPA format
        * Single-page potency-only COAs (QA/non-compliance)
        * Multi-page compliance COAs (potency + terpenes + contaminants)

    Result tables (pdfplumber ``extract_tables``), one analyte per row:
        Safety:  ANALYTE | LIMIT | AMT | LOD/LOQ | PASS/FAIL
                 "ABAMECTIN | 0.1 µg/g | ND | 0.0117/0.0429 | PASS"
        Potency: ANALYTE | AMT | AMT | LOD/LOQ | PASS/FAIL
                 "THCA | 44.5938 % | 445.938 mg/g | 0.0268/0.4 |"
        Foreign material: ANALYTE | LIMIT | AMT | PASS/FAIL
    A table that breaks across a page continues on the next page
    without its header row. The pesticide list is printed in two halves
    side by side, so both halves continue that way (2 River Labs).

    Fixes (10/13/2026), from a benchmark of 4 California COAs read by
    four Claude models that agree with each other:
        * A result is never a limit. A table without its header row
          (the continuation of a table broken by a page) had its first
          analyte taken for the header, which was accepted because its
          status cell reads PASS. With no LIMIT label in that "header"
          the rows were read as potency rows, whose first number is the
          result, so every non-detect read its action limit (2 River
          Labs pesticides: flonicamid 0.1, imidacloprid 5.0 ug/g; Pure
          Cannalyst foreign material: mold and sand 25.0 percent), and
          the first analyte of each continuation (fipronil,
          spiromesifen) was lost. A header is now a row of column
          labels with no values (_header_layout), and columns are read
          by their labels. A table without one takes the layout of the
          last header with as many columns for the same analysis, or,
          if it prints a PASS/FAIL or LOD/LOQ column, a layout read from
          its cells, where the result of a safety analysis is the column
          that prints "ND" (a limit never does), else the one after the
          limit (_continued_layout, _infer_layout).
        * Non-detects keep their qualifier (``parse_result_value``):
          "ND" is value None, qualifier 'ND'; "<LOQ" and "<0.05" are
          value None, qualifier '<LOQ', with 'loq' from the LOD/LOQ
          column or else the printed bound. A measured 0 stays 0.0.
          Every result row carries 'qualifier'; 'limit', 'lod' and
          'loq' are None when not printed (they were 0.0).
        * Units are the read cell's or column's own ('0.4457 aw' is
          'aw', '0.1 µg/g' is 'ug/g'), else the analysis default; water
          activity is 'aw' (it was 'aW').
        * Moisture and water activity rows that print a value are kept
          (they were dropped with the status-bar entries "MOISTURE
          TESTED", "WATER ACTIVITY PASS").
        * One-row tables (a single analyte left on a page) are read,
          and a header printed as a table of its own is the layout of
          the next table (both were skipped).
        * Rows named TOTAL THC / TOTAL CBD are skipped like their
          starred forms (totals are metadata), and rows that print
          nothing but a name (sub-headings) are not analytes.
        * Review (10/14/2026): a continued table whose amount cells are
          blank reads no result, not its limits.

    Foreign material "MOLD" (percent of sample area) is keyed 'mold';
    ``normalize_analyte_key`` maps 'mold' to the microbial
    'total_yeast_and_mold' (an alias in ``cannlytics.constants``).

Data Points:

    ✓ product_name, strain_name, product_type
    ✓ date_tested, date_received, date_collected
    ✓ batch_number, batch_size, sample_weight
    ✓ lab, lab_license_number, lab_address, lab_city, lab_state, lab_zipcode, lab_phone
    ✓ producer, producer_license_number
    ✓ distributor, distributor_license_number
    ✓ sample_id (lab_id)
    ✓ total_thc, total_cbd, total_cannabinoids, total_terpenes
    ✓ status (overall batch pass/fail)
    ✓ analyses (list of analysis types)
    ✓ results (list of analyte result dicts)
    ✓ lab_results_url (TagLeaf LIMS URL)
    ✓ metrc_ids
"""
# Standard imports:
import hashlib
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# External imports:
import pdfplumber

# Internal imports:
from cannlytics.data.coas.schema import parse_result_value

# ── TagLeaf LIMS Constants ────────────────────────────────────────

TAGLEAF = {
    'coa_algorithm': 'tagleaf.py',
    'coa_algorithm_entry_point': 'parse_tagleaf_coa',
    'lims': 'TagLeaf LIMS',
    'url': 'https://lims.tagleaf.com',
}

# Standard analysis name mappings for TagLeaf section headers.
ANALYSIS_SECTION_MAP = {
    'cannabinoid': 'cannabinoids',
    'potency': 'cannabinoids',
    'terpene': 'terpenes',
    'terpenoid': 'terpenes',
    'pesticide': 'pesticides',
    'heavy metal': 'heavy_metals',
    'metal': 'heavy_metals',
    'microbial': 'microbials',
    'microbiological': 'microbials',
    'mycotoxin': 'mycotoxins',
    'residual solvent': 'residual_solvents',
    'solvent': 'residual_solvents',
    'moisture': 'moisture_foreign_matter',
    'water activity': 'moisture_foreign_matter',
    'foreign': 'moisture_foreign_matter',
    'vitamin e': 'additives',
    'additive': 'additives',
}

# Standard units per analysis type.
STANDARD_UNITS = {
    'cannabinoids': 'percent',
    'terpenes': 'percent',
    'pesticides': 'ug/g',
    'heavy_metals': 'ug/g',
    'microbials': 'cfu/g',
    'mycotoxins': 'ug/kg',
    'residual_solvents': 'ug/g',
    'moisture_foreign_matter': 'percent',
    'additives': 'ug/g',
}

# Analyte key standardization (display name → snake_case key).
# Only includes common overrides; others are auto-generated.
ANALYTE_KEY_MAP = {
    'Δ9-THC': 'delta_9_thc',
    'Δ8-THC': 'delta_8_thc',
    'Δ3-CARENE': 'delta_3_carene',
    'D-LIMONENE': 'd_limonene',
    'β-CARYOPHYLLENE': 'beta_caryophyllene',
    'β-MYRCENE': 'beta_myrcene',
    'β-PINENE': 'beta_pinene',
    'β-OCIMENE': 'beta_ocimene',
    'α-PINENE': 'alpha_pinene',
    'α-HUMULENE': 'alpha_humulene',
    'α-BISABOLOL': 'alpha_bisabolol',
    'α-TERPINENE': 'alpha_terpinene',
    'α-OCIMENE': 'alpha_ocimene',
    'γ-TERPINENE': 'gamma_terpinene',
    'P-CYMENE': 'p_cymene',
    'CIS-NEROLIDOL': 'cis_nerolidol',
    'TRANS-NEROLIDOL': 'trans_nerolidol',
    'NEROLIDOL 1': 'nerolidol_1',
    'NEROLIDOL 2': 'nerolidol_2',
    'TOTAL TERPENES': 'total_terpenes',
    'TOTAL THC**': 'total_thc',
    'TOTAL CBD**': 'total_cbd',
    'TOT THC **': 'total_thc',
    'TOT CBD **': 'total_cbd',
    'TOTAL THC': 'total_thc',
    'TOTAL CBD': 'total_cbd',
    'TOTAL TERPENES *': 'total_terpenes',
    'TOTAL XYLENES': 'total_xylenes',
    'O-XYLENE': 'o_xylene',
    'P- AND M-XYLENE': 'p_and_m_xylene',
    '1,2-DICHLOROETHANE': '1_2_dichloroethane',
    'SHIGA TOXIN-PRODUCING E. COLI': 'stec',
    'ASPERGILLUS SPP.': 'aspergillus_spp',
    'ASPERGILLUS FLAVUS': 'aspergillus_flavus',
    'ASPERGILLUS FUMIGATUS': 'aspergillus_fumigatus',
    'ASPERGILLUS NIGER': 'aspergillus_niger',
    'ASPERGILLUS TERREUS': 'aspergillus_terreus',
    'SALMONELLA SPP.': 'salmonella_spp',
    'VITAMIN E ACETATE': 'vitamin_e_acetate',
    'MOISTURE': 'moisture_content',
    'MOISTURE CONTENT': 'moisture_content',
}

# Metrc tag prefixes (used to identify Metrc IDs in text).
METRC_PREFIXES = ['1A40']

# Printed units → the package's units ("percent" for %).
UNIT_ALIASES = {
    '%': 'percent',
    'mg/g': 'mg/g',
    'mg': 'mg',
    'ug/g': 'ug/g',
    'ug/kg': 'ug/kg',
    'ppm': 'ppm',
    'ppb': 'ppb',
    'cfu/g': 'cfu/g',
    'aw': 'aw',
}

# A units token at the end of a cell ("0.1 µg/g", "25 %", "AMT (%)").
_UNIT_TOKEN = r'(?:%|(?<![a-z])(?:mg/g|[uµμ]g/k?g|ppm|ppb|cfu/g|aw|mg))'
_TRAILING_UNITS = re.compile(
    r'\(?\s*(' + _UNIT_TOKEN + r')\s*\)?\s*$', re.IGNORECASE)

# A printed number, optionally a bound, optionally with units.
_NUMBER_CELL = re.compile(
    r'^[<>]?\s*=?\s*[-+]?(?:\d[\d,]*\.?\d*|\.\d+)\s*' + _UNIT_TOKEN + r'?$',
    re.IGNORECASE)

# An LOD/LOQ cell: "0.0117/0.0429" (not a date, not "1/3g").
_LOD_LOQ_CELL = re.compile(
    r'^\d*\.?\d+\s*/\s*\d*\.?\d+\s*' + _UNIT_TOKEN + r'?$', re.IGNORECASE)

# Words a PASS/FAIL column prints.
_STATUS_CELLS = {'PASS', 'FAIL', 'PASSED', 'FAILED', 'TESTED', 'NOT TESTED'}

# Qualifiers that are a reading (a non-detect, a bound, "detected").
_READ_QUALIFIERS = {'ND', '<LOD', '<LOQ', '>ULOQ', 'detected'}

# Column labels of a header row, by role, in order of precedence
# (searched after units are removed, so "LIMIT OF DETECTION" is an LOD,
# not a limit). "PASS/FAI" and "LOD/LO" are labels cut short by
# pdfplumber.
_COLUMN_ROLES = (
    ('lod_loq', re.compile(r'^(?:LOD\s*/|LOQ\s*/)')),
    ('lod', re.compile(r'^(?:LOD|MDL)$|LIMIT OF DETECTION|DETECTION LIMIT')),
    ('loq', re.compile(r'^(?:LOQ|LLOQ)$|LIMIT OF QUANTI|QUANTITATION LIMIT')),
    ('status', re.compile(r'^(?:PASS\s*/|STATUS$|P\s*/\s*F$)')),
    ('limit', re.compile(r'\bLIMITS?\b|\bACTION\b|^MAX(?:IMUM)?$')),
    ('result', re.compile(r'^(?:AMT|AMOUNT|RESULTS?|CONC(?:ENTRATION)?)\b')),
    ('name', re.compile(r'^(?:ANALYTES?|COMPOUNDS?)\b')),
)

# Analyses whose tables print two amounts (% and mg/g) and no limit.
_POTENCY_ANALYSES = {'cannabinoids', 'terpenes'}

# ── Utility Functions ─────────────────────────────────────────────

def _snake_case(text: str) -> str:
    """Convert text to snake_case key."""
    stripped = text.strip()
    # Try exact match first (handles Greek letters like α, β, Δ, γ).
    if stripped.upper() in ANALYTE_KEY_MAP:
        return ANALYTE_KEY_MAP[stripped.upper()]
    # Try original case (Greek lowercase α/β stay lowercase with .upper()).
    if stripped in ANALYTE_KEY_MAP:
        return ANALYTE_KEY_MAP[stripped]
    # Normalize Greek letters to Latin before snake_case fallback.
    s = stripped.lower().strip()
    s = s.replace('α', 'alpha_').replace('β', 'beta_')
    s = s.replace('γ', 'gamma_').replace('δ', 'delta_')
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s)
    s = s.strip('_')
    return s

def _parse_number(text: str) -> Optional[float]:
    """Parse a plain number (a limit, LOD or LOQ) from a cell.

    '0.1 µg/g' is 0.1, '5,000' is 5000.0, '1 per 3g' is 1.0. A blank
    cell, a word ('ND', 'LOD', '--') or a bound ('<0.05') is None: a
    bound is a qualifier, not a number. Until 10/13/2026 these were 0.0,
    and results were read with this function; read a result with
    _parse_result.
    """
    if not text or not isinstance(text, str):
        return None
    text = text.strip().replace(',', '')
    if not text or text[0] in '<>':
        return None
    match = re.match(r'^[-+]?(?:\d+\.?\d*|\.\d+)', text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None

def _parse_result(text: str) -> Tuple[Optional[float], str, Optional[float]]:
    """Read a printed result cell as ``(value, qualifier, bound)``.

    Uses the package's qualifier semantics (``parse_result_value``):
    '44.5938 %' is (44.5938, '', None); 'ND' is (None, 'ND', None);
    '<LOQ' is (None, '<LOQ', None); '<0.05' is (None, '<LOQ', 0.05),
    the bound being the limit the result is below; '0' is (0.0, '',
    None). A blank cell is (None, 'NR', None): no result is printed.
    """
    text = ' '.join(str(text or '').split())
    if not text:
        return None, 'NR', None
    return parse_result_value(text)

def _normalize_units(token: str) -> Optional[str]:
    """The package's name for a printed units token ('µg/g' is 'ug/g',
    '%' is 'percent'), or None."""
    if not token:
        return None
    token = token.strip().lower().replace('µ', 'u').replace('μ', 'u')
    return UNIT_ALIASES.get(token)

def _cell_units(text: str) -> Optional[str]:
    """The units a cell prints after its number or label: '0.1 µg/g' is
    'ug/g', '0.4457 aw' is 'aw', 'AMT (%)' is 'percent'. None if none."""
    if not text:
        return None
    match = _TRAILING_UNITS.search(' '.join(str(text).split()))
    return _normalize_units(match.group(1)) if match else None

def _is_lod_loq(text: str) -> bool:
    """Whether a cell is an LOD/LOQ pair such as '0.0117/0.0429'."""
    return bool(text) and bool(_LOD_LOQ_CELL.match(' '.join(str(text).split())))

def _is_value_cell(text: str) -> bool:
    """Whether a cell prints a reading: a number (with or without units
    or a '<' bound) or a qualifier such as 'ND' or '<LOQ'. Placeholders
    ('--', 'N/A'), status words and labels are not readings."""
    text = ' '.join(str(text or '').split())
    if not text:
        return False
    if _NUMBER_CELL.match(text):
        return True
    _, qualifier, _ = parse_result_value(text)
    return qualifier in _READ_QUALIFIERS

def _parse_date(text: str) -> str:
    """Parse a date string to ISO format (YYYY-MM-DD)."""
    if not text or not isinstance(text, str):
        return ''
    text = text.strip()
    for fmt in ('%b %d, %Y', '%B %d, %Y', '%m/%d/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(text, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return text

def _parse_lod_loq(text: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse a LOD/LOQ string like '0.0109/0.24767' (units may follow).
    Returns (None, None) when the cell is not such a pair (until
    10/13/2026, (0.0, 0.0))."""
    if not text or not _is_lod_loq(text):
        return None, None
    numbers = re.findall(r'\d*\.?\d+', text.replace(',', ''))
    if len(numbers) != 2:
        return None, None
    try:
        return float(numbers[0]), float(numbers[1])
    except ValueError:
        return None, None

def _extract_tagleaf_url(pdf) -> str:
    """Find the TagLeaf LIMS URL from page footers."""
    for page in pdf.pages:
        text = page.extract_text() or ''
        match = re.search(r'(https://lims\.tagleaf\.com/coa_/\S+)', text)
        if match:
            url = match.group(1)
            # Clean trailing page info.
            url = re.sub(r'\s+Page\s+\d+.*$', '', url).strip()
            return url
    return ''

# ── Core Parsing Functions ────────────────────────────────────────

def _parse_header(lines: List[str]) -> Dict:
    """Parse lab header and license from the first few lines."""
    obs = {}
    header_line = None
    license_line = None

    for i, line in enumerate(lines[:20]):
        if '//' in line and 'PH:' in line.upper():
            header_line = line.strip()
        # infiniteCAL format: "Lab Name • Address • Phone"
        if not header_line and '•' in line and re.search(r'\d{7,}', line):
            header_line = line.strip()
            obs['_header_format'] = 'infinitecal'
        if 'LICENSE' in line.upper() and '#' in line:
            license_line = line.strip()

    if header_line:
        fmt = obs.pop('_header_format', 'belcosta')
        if fmt == 'infinitecal':
            # infiniteCAL: "Lab Name • Address City ST ZIP • Phone"
            parts = [p.strip() for p in header_line.split('•')]
            if len(parts) >= 1:
                obs['lab'] = parts[0]
            if len(parts) >= 2:
                obs['lab_address'] = parts[1]
                addr = parts[1]
                addr_match = re.search(
                    r'^(.+?)\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$', addr)
                if addr_match:
                    city_street = addr_match.group(1)
                    obs['lab_state'] = addr_match.group(2).lower()
                    obs['lab_zipcode'] = addr_match.group(3)
                    city_match = re.search(r'(\b[A-Z][A-Z ]+)$', city_street)
                    if city_match:
                        obs['lab_city'] = city_match.group(1).strip()
            if len(parts) >= 3:
                obs['lab_phone'] = re.sub(r'[^0-9]', '', parts[2])
        else:
            # BelCosta format: "Lab // Address // PH: Phone"
            parts = [p.strip() for p in header_line.split('//')]
            if len(parts) >= 1:
                obs['lab'] = parts[0]
            if len(parts) >= 2:
                obs['lab_address'] = parts[1]
                addr = parts[1]
                addr_match = re.search(
                    r'^(.+?)\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$', addr)
                if addr_match:
                    city_street = addr_match.group(1)
                    obs['lab_state'] = addr_match.group(2).lower()
                    obs['lab_zipcode'] = addr_match.group(3)
                    city_match = re.search(r'(\b[A-Z][A-Z ]+)$', city_street)
                    if city_match:
                        obs['lab_city'] = city_match.group(1).strip()
            if len(parts) >= 3:
                phone = parts[2].replace('PH:', '').strip()
                obs['lab_phone'] = phone

    if license_line:
        lic_match = re.search(r'#[:\s]*(\S+)', license_line)
        if lic_match:
            obs['lab_license_number'] = lic_match.group(1)

    return obs

def _parse_sample_line(lines: List[str]) -> Dict:
    """Parse the SAMPLE: line for product_name, product_type, client, status."""
    obs = {}
    for line in lines[:10]:
        line_stripped = line.strip()
        # Match both "SAMPLE:" (BelCosta) and "Sample:" (infiniteCAL).
        if line_stripped.upper().startswith('SAMPLE:'):
            content = line_stripped.split(':', 1)[1].strip()

            # Determine separator: '//' (BelCosta) or '•' (infiniteCAL).
            if '//' in content:
                parts = [p.strip() for p in content.split('//')]
            elif '•' in content:
                parts = [p.strip() for p in content.split('•')]
            else:
                parts = [content]

            if parts:
                # Extract product name and type.
                name_part = parts[0].strip()
                type_match = re.search(r'\(([^)]+)\)\s*$', name_part)
                if type_match:
                    obs['product_type'] = type_match.group(1).lower()
                    obs['product_name'] = name_part[:type_match.start()].strip()
                else:
                    obs['product_name'] = name_part

            for part in parts[1:]:
                part_upper = part.strip().upper()
                if part_upper.startswith('CLIENT:'):
                    obs['producer'] = part.split(':', 1)[1].strip()
                elif part_upper.startswith('BATCH:'):
                    obs['status'] = part.split(':', 1)[1].strip().lower()

            break
    return obs

def _parse_metadata_fields(text: str) -> Dict:
    """Extract structured metadata fields from page 1 text."""
    obs = {}
    field_patterns = {
        'date_tested': r'PRODUCED:\s*(.+)',
        'sample_id': r'SAMPLE\s*ID:\s*(\S+)',
        'date_collected': r'COLLECTED\s*ON:\s*(.+)',
        'date_received': r'RECEIVED\s*ON:\s*(.+)',
        'batch_number': r'BATCH\s*(?:NO|ID)[.:]?\s*[:\s]*([A-Za-z0-9][\w\-.]+)',
        'matrix': r'MATRIX:\s*(\S+)',
        'category': r'CATEGORY:\s*(\S+)',
        'cultivar': r'CULTIVAR:\s*(.+)',
    }

    for key, pattern in field_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if key.startswith('date_'):
                value = _parse_date(value)
            obs[key] = value

    # ── Totals extraction (multiple patterns) ─────────────
    # Pattern A (older format): TOTAL THC: 29.382 %
    # Pattern B (newer format, inline in table): TOTAL THC** 28.99 % 289.9 mg/g
    # Pattern C (overview, mg-based): TOTAL CANNABINOIDS: 339.76 mg

    # Total THC.
    thc_match = (
        re.search(r'TOTAL\s+THC:\s*([\d.]+)\s*%', text, re.IGNORECASE) or
        re.search(r'TOTAL\s+THC\*{0,2}\s+([\d.]+)\s*%', text, re.IGNORECASE)
    )
    if thc_match:
        try:
            obs['total_thc'] = float(thc_match.group(1))
        except ValueError:
            pass

    # Total CBD.
    cbd_match = (
        re.search(r'TOTAL\s+CBD:\s*([\d.]+)\s*%', text, re.IGNORECASE) or
        re.search(r'TOTAL\s+CBD\*{0,2}\s+([\d.]+)\s*%', text, re.IGNORECASE)
    )
    if cbd_match:
        try:
            obs['total_cbd'] = float(cbd_match.group(1))
        except ValueError:
            pass

    # Total cannabinoids (may be in % or mg).
    cann_match = (
        re.search(r'TOTAL\s+CANNABINOIDS:\s*([\d.]+)\s*%', text, re.IGNORECASE) or
        re.search(r'TOTAL\s+CANNABINOIDS:\s*([\d.]+)\s*mg', text, re.IGNORECASE)
    )
    if cann_match:
        try:
            val = float(cann_match.group(1))
            # If the value looks like mg (>100), don't set as percent.
            if val <= 100:
                obs['total_cannabinoids'] = val
            else:
                obs['total_cannabinoids_mg'] = val
        except ValueError:
            pass

    # Derive product_type from matrix if not set.
    matrix = obs.pop('matrix', '')
    if matrix:
        obs.setdefault('product_type', matrix.lower())
    obs.pop('category', None)

    # Extract strain name from cultivar or product name.
    cultivar = obs.pop('cultivar', '')
    if cultivar:
        obs['strain_name'] = cultivar

    # Batch/sample size.
    bs_match = re.search(
        r'BATCH/SAMPLE\s+SIZE:\s*(.+)', text, re.IGNORECASE)
    if bs_match:
        obs['batch_size_raw'] = bs_match.group(1).strip()

    # Metrc IDs.
    metrc_ids = []
    for prefix in METRC_PREFIXES:
        for match in re.finditer(prefix + r'[0-9A-Z]+', text):
            tag = match.group(0)
            if len(tag) >= 20 and tag not in metrc_ids:
                metrc_ids.append(tag)
    if metrc_ids:
        obs['metrc_ids'] = metrc_ids

    # Serving/package size.
    srv_match = re.search(
        r'SERVING/PACKAGE\s+SIZE:\s*(.+)', text, re.IGNORECASE)
    if srv_match:
        obs['serving_package_size'] = srv_match.group(1).strip()

    return obs

def _parse_cultivator_distributor(text: str) -> Dict:
    """Extract cultivator/distributor/manufacturer info from page 1."""
    obs = {}

    # Cultivator.
    cult_match = re.search(
        r'CULTIVATOR\n(.+?)\n(.+?)\n(.+?)\nLICENSE\n(\S+)',
        text, re.DOTALL)
    if cult_match:
        obs['producer'] = cult_match.group(1).strip()
        obs['producer_license_number'] = cult_match.group(4).strip()

    # Distributor.
    dist_match = re.search(
        r'DISTRIBUTOR\n(.+?)\n(.+?)\n(.+?)\nLICENSE\n(\S+)',
        text, re.DOTALL)
    if dist_match:
        obs['distributor'] = dist_match.group(1).strip()
        obs['distributor_license_number'] = dist_match.group(4).strip()

    # Manufacturer (MO format uses this instead of distributor).
    mfr_match = re.search(
        r'MANUFACTURER\n(.+?)\n(.+?)\n(.+?)\nLICENSE\n(\S+)',
        text, re.DOTALL)
    if mfr_match:
        obs.setdefault('distributor', mfr_match.group(1).strip())
        obs.setdefault(
            'distributor_license_number',
            mfr_match.group(4).strip(),
        )

    return obs

def _detect_current_analysis(line: str) -> Optional[str]:
    """Detect analysis section from a header line."""
    line_upper = line.upper()
    for keyword, analysis in ANALYSIS_SECTION_MAP.items():
        if keyword.upper() in line_upper:
            return analysis
    return None

# Known analyte names per analysis type for content-based inference.
_CANNABINOID_NAMES = {
    'CBC', 'CBCA', 'CBD', 'CBDA', 'CBDV', 'CBDVA', 'CBG', 'CBGA',
    'CBL', 'CBN', 'CBT', 'THC', 'THCA', 'THCV', 'THCVA',
}
_TERPENE_NAMES = {
    'MYRCENE', 'LIMONENE', 'CARYOPHYLLENE', 'HUMULENE', 'PINENE',
    'LINALOOL', 'BISABOLOL', 'TERPINOLENE', 'TERPINENE', 'OCIMENE',
    'FENCHOL', 'CAMPHENE', 'GUAIOL', 'NEROLIDOL', 'BORNEOL',
    'GERANIOL', 'EUCALYPTOL', 'CYMENE', 'FENCHONE', 'CEDROL',
    'CEDRENE', 'EUDESMOL', 'PULEGONE', 'MENTHOL', 'ISOPULEGOL',
    'CAMPHOR', 'CARENE', 'GERANYL', 'ISOBORNEOL', 'CITRONELLOL',
    'TOTAL TERPENES',
}
_PESTICIDE_NAMES = {
    'ABAMECTIN', 'ACEPHATE', 'ACEQUINOCYL', 'ACETAMIPRID', 'ALDICARB',
    'AZOXYSTROBIN', 'BIFENAZATE', 'BIFENTHRIN', 'BOSCALID', 'CAPTAN',
    'CARBARYL', 'CARBOFURAN', 'CHLORANTRANILIPROLE', 'CHLORDANE',
    'CHLORFENAPYR', 'CHLORPYRIFOS', 'CLOFENTEZINE', 'COUMAPHOS',
    'CYFLUTHRIN', 'CYPERMETHRIN', 'DAMINOZIDE', 'DIAZINON',
    'DICHLORVOS', 'DIMETHOATE', 'DIMETHOMORPH', 'ETHOPROPHOS',
    'ETOFENPROX', 'ETOXAZOLE', 'FENHEXAMID', 'FENOXYCARB',
    'FENPYROXIMATE', 'FIPRONIL', 'FLONICAMID', 'FLUDIOXONIL',
    'HEXYTHIAZOX', 'IMAZALIL', 'IMIDACLOPRID', 'MALATHION',
    'METALAXYL', 'METHIOCARB', 'METHOMYL', 'METHYL PARATHION',
    'MEVINPHOS', 'MYCLOBUTANIL', 'NALED', 'OXAMYL', 'PACLOBUTRAZOL',
    'PENTACHLORONITROBENZENE', 'PERMETHRIN', 'PHOSMET',
    'PIPERONYLBUTOXIDE', 'PRALLETHRIN', 'PROPICONAZOLE', 'PROPOXUR',
    'PYRETHRINS', 'PYRIDABEN', 'SPINETORAM', 'SPINOSAD',
    'SPIROMESIFEN', 'SPIROTETRAMAT', 'SPIROXAMINE', 'TEBUCONAZOLE',
    'THIACLOPRID', 'THIAMETHOXAM', 'TRIFLOXYSTROBIN',
    'KRESOXIM-METHYL', 'KRESOXIM', 'CHLORPYRIFOS',
}
_HEAVY_METAL_NAMES = {'ARSENIC', 'CADMIUM', 'LEAD', 'MERCURY'}
_MICROBIAL_NAMES = {
    'ASPERGILLUS', 'SALMONELLA', 'E. COLI', 'SHIGA',
}
_MYCOTOXIN_NAMES = {'AFLATOXIN', 'OCHRATOXIN'}
_SOLVENT_NAMES = {
    'ACETONE', 'ACETONITRILE', 'BENZENE', 'BUTANE', 'CHLOROFORM',
    'DICHLOROETHANE', 'ETHANOL', 'ETHYL ACETATE', 'ETHYLENE OXIDE',
    'ETHYL ETHER', 'HEPTANE', 'HEXANE', 'ISOPROPYL', 'METHANOL',
    'METHYLENE CHLORIDE', 'PENTANE', 'PROPANE', 'TOLUENE',
    'TRICHLOROETHYLENE', 'XYLENE',
}
_MOISTURE_NAMES = {
    'MOISTURE', 'WATER ACTIVITY', 'FOREIGN MATERIAL', 'IMBEDDED',
    'INSECT FRAGMENT', 'MOLD', 'SAND', 'CINDERS',
}

def _infer_analysis_from_content(table, has_header: bool = True) -> Optional[str]:
    """Infer analysis type from the analyte names in a table's rows.

    This is more reliable than section-header tracking for multi-section
    pages where pdfplumber table positions don't map cleanly to text
    line numbers.

    Args:
        table: Rows of cells, as from pdfplumber ``extract_tables``.
        has_header: Whether the first row is a header (skipped). A
            table continued from the previous page has none.
    """
    start = 1 if has_header else 0
    if not table or len(table) <= start:
        return None

    # Collect analyte names from first ~8 data rows.
    names = []
    for row in table[start:start + 8]:
        if row and row[0]:
            names.append(str(row[0]).strip().upper().replace('\n', ' '))

    if not names:
        return None

    # Score each analysis type by how many analyte names match.
    scores = {
        'cannabinoids': 0, 'terpenes': 0, 'pesticides': 0,
        'heavy_metals': 0, 'microbials': 0, 'mycotoxins': 0,
        'residual_solvents': 0, 'moisture_foreign_matter': 0,
    }
    for name in names:
        for known in _CANNABINOID_NAMES:
            if known in name:
                scores['cannabinoids'] += 1
                break
        for known in _TERPENE_NAMES:
            if known in name:
                scores['terpenes'] += 1
                break
        for known in _PESTICIDE_NAMES:
            if known in name:
                scores['pesticides'] += 1
                break
        for known in _HEAVY_METAL_NAMES:
            if known in name:
                scores['heavy_metals'] += 1
                break
        for known in _MICROBIAL_NAMES:
            if known in name:
                scores['microbials'] += 1
                break
        for known in _MYCOTOXIN_NAMES:
            if known in name:
                scores['mycotoxins'] += 1
                break
        for known in _SOLVENT_NAMES:
            if known in name:
                scores['residual_solvents'] += 1
                break
        for known in _MOISTURE_NAMES:
            if known in name:
                scores['moisture_foreign_matter'] += 1
                break

    # Return the type with the highest score (minimum 2 matches).
    best = max(scores, key=scores.get)
    if scores[best] >= 2:
        return best
    # Single match — still useful for small tables like heavy metals.
    if scores[best] >= 1:
        return best
    return None

# ── Result Tables ─────────────────────────────────────────────────

# Rows that are not analytes: status-bar entries ("POTENCY PASS",
# "MOISTURE TESTED"), notes and page furniture that pdfplumber can
# extract as table rows.
_STATUS_KEYWORDS = {
    'POTENCY', 'FOREIGN', 'METALS', 'MICROBIAL', 'MICRO',
    'MOISTURE', 'MOIST', 'MYCOTOXINS', 'MYCOTOXIN', 'MYCO',
    'PESTICIDES', 'PESTICIDE', 'PEST', 'SOLVENTS', 'SOLVENT',
    'TERPENES', 'TERPENE', 'TERP', 'WATER', 'ADDITIVES',
    'BATCH RESULT', 'PASS', 'FAIL', 'TESTED',
    'CANNABINOID OVERVIEW', 'REGULATORY COMPLIANCE',
    'RESULTS CERTIFIED', 'SAMPLE WAS TESTED',
    'ALL LQC SAMPLES', 'DRY-WEIGHT', 'DRY WEIGHT',
    'ACCREDITATIONS', 'A2LA ACCREDITED',
    'PAGE', 'CERTIFICATE OF ANALYSIS',
}

# Total/summary and per-serving/per-package rows (totals are metadata).
_SKIP_PATTERNS = [
    'TOTAL THC/', 'TOTAL CBD/', 'CBD/SRV', 'CBD/PKG',
    'THC/SRV', 'THC/PKG', '/SRV', '/PKG',
    'TOTAL THC**', 'TOTAL CBD**', 'TOT THC', 'TOT CBD',
    'TOTAL THC *', 'TOTAL CBD *',
    'TOTAL CANNABINOIDS', 'SUM OF CANNABINOIDS',
    'SUM OF TERPENES',
]
_TOTAL_ROWS = {'TOTAL THC', 'TOTAL CBD'}

# Units of analytes whose row may print none, whatever table they are in.
_ANALYTE_UNITS = {'water_activity': 'aw', 'moisture_content': 'percent'}

def _cell_text(cell: Any) -> str:
    """A table cell as one line of text ('' for None)."""
    return ' '.join(str(cell or '').split())

def _column_role(text: str) -> Tuple[Optional[str], Optional[str]]:
    """The role and units of a header cell.

    'AMT (%)' is ('result', 'percent'), 'LIMIT' is ('limit', None),
    'LOD/LOQ' is ('lod_loq', None), 'PASS/FAIL' is ('status', None), and
    a units-only cell such as 'MG/G' is an amount column. (None, None)
    for anything else.
    """
    raw = _cell_text(text)
    if not raw:
        return None, None
    units = None
    match = _TRAILING_UNITS.search(raw)
    if match:
        units = _normalize_units(match.group(1))
        raw = raw[:match.start()]
    label = raw.strip(' ()').upper()
    if not label:
        return ('result', units) if units else (None, None)
    for role, pattern in _COLUMN_ROLES:
        if pattern.search(label):
            return role, units
    return None, None

def _header_layout(cells: List[str]) -> Optional[Dict]:
    """Read the column layout of a header row, or None if the row is not
    a header. A header is column labels (at least two) and no values, so
    the first row of a table continued from the previous page, which
    prints an analyte and its PASS, is not one.

    Returns:
        A dict of column indices: 'result' (the AMT column, or of two
        the one labeled %), 'result2' (the other amount), 'limit',
        'lod_loq', 'lod', 'loq' and 'status' (None when absent), with
        'units' (index -> units printed in that column's label) and
        'ncols'.
    """
    roles: Dict[str, List[int]] = {}
    units: Dict[int, str] = {}
    for i, cell in enumerate(cells):
        if not cell:
            continue
        if _is_value_cell(cell) or _is_lod_loq(cell):
            return None
        role, unit = _column_role(cell)
        if role is None:
            continue
        roles.setdefault(role, []).append(i)
        if unit:
            units[i] = unit
    if sum(len(found) for found in roles.values()) < 2:
        return None

    def first(role: str) -> Optional[int]:
        return (roles.get(role) or [None])[0]

    limit = first('limit')
    amounts = [i for i in roles.get('result', []) if i > 0]
    if not amounts:
        # No amount label: the column after the limit, else the first
        # column without a label.
        taken = {i for found in roles.values() for i in found}
        free = [i for i in range(1, len(cells)) if i not in taken]
        amounts = [i for i in free if limit is not None and i > limit][:1] or free[:1]
    if not amounts:
        return None
    result = amounts[0]
    result2 = amounts[1] if len(amounts) > 1 else None
    if result2 is not None and units.get(result2) == 'percent' \
            and units.get(result) != 'percent':
        result, result2 = result2, result
    return {
        'ncols': len(cells),
        'result': result,
        'result2': result2,
        'limit': limit,
        'lod_loq': first('lod_loq'),
        'lod': first('lod'),
        'loq': first('loq'),
        'status': first('status'),
        'units': units,
    }

def _table_segments(rows: List[List[str]]) -> List[Tuple[Optional[List[str]], Optional[Dict], List[List[str]]]]:
    """Split a table's rows at its header rows.

    Returns:
        A list of (header row, layout, body rows). Rows before the
        first header (a table continued from the previous page) form a
        segment whose header and layout are None. A header with no rows
        after it (a header printed at the foot of a page) is returned
        with an empty body.
    """
    segments = [(None, None, [])]
    for row in rows:
        layout = _header_layout(row)
        if layout is not None:
            segments.append((row, layout, []))
        else:
            segments[-1][2].append(row)
    return [s for s in segments if s[1] is not None or s[2]]

def _looks_like_result_row(cells: List[str]) -> bool:
    """Whether a row reads as an analyte row: a name, then at least one
    reading or LOD/LOQ pair (a section title with a PASS is not one)."""
    if not cells or not cells[0]:
        return False
    if _is_value_cell(cells[0]) or _is_lod_loq(cells[0]):
        return False
    return any(_is_value_cell(c) or _is_lod_loq(c) for c in cells[1:] if c)

def _infer_layout(rows: List[List[str]], analysis: Optional[str]) -> Dict:
    """The column layout of a table without a header, read from its
    cells: the LOD/LOQ column (every cell a pair), the PASS/FAIL column
    (every cell a status word), and the value columns before them.

    Cannabinoids and terpenes print AMT then AMT (% then mg/g): the
    result is the first. Safety analyses print LIMIT then AMT: the
    result is the one column that prints non-detects or bounds ('ND',
    '<LOQ'), which a limit never is, else the second, even when only
    the first prints anything; the limit is the column before it (else
    after it).
    """
    ncols = max(len(r) for r in rows)

    def column(i: int) -> List[str]:
        return [r[i] for r in rows if i < len(r) and r[i]]

    lod_loq = next((i for i in range(1, ncols)
                    if column(i) and all(_is_lod_loq(c) for c in column(i))), None)
    status = next((i for i in range(ncols - 1, 0, -1)
                   if column(i) and all(c.upper() in _STATUS_CELLS for c in column(i))), None)
    end = min(i for i in (lod_loq, status, ncols) if i is not None)
    values = list(range(1, end))
    filled = [i for i in values if column(i)]
    layout = {
        'ncols': ncols, 'result': None, 'result2': None, 'limit': None,
        'lod_loq': lod_loq, 'lod': None, 'loq': None, 'status': status,
        'units': {},
    }
    if analysis in _POTENCY_ANALYSES:
        amounts = filled or values
        layout['result'] = amounts[0] if amounts else None
        layout['result2'] = amounts[1] if len(amounts) > 1 else None
        return layout
    flagged = [i for i in filled if any(
        _parse_result(c)[1] in _READ_QUALIFIERS for c in column(i))]
    if len(flagged) == 1:
        result = flagged[0]
    elif len(filled) >= 2:
        result = filled[1]
    elif len(values) >= 2:
        # LIMIT then AMT with the AMT cells blank: the one filled column
        # is the limit, and the result is not printed (10/14/2026: it
        # was read as the result).
        result = values[1]
    elif filled:
        result = filled[0]
    else:
        result = values[0] if values else None
    layout['result'] = result
    if result is not None:
        before = [i for i in values if i < result]
        after = [i for i in filled if i > result]
        layout['limit'] = before[-1] if before else (after[0] if after else None)
    return layout

def _table_analysis(header: List[str], body: List[List[str]],
                    page_default: Optional[str]) -> str:
    """The analysis of a table with a header row: from its analyte
    names, else its header labels, else the page's section header,
    else the units in its header."""
    analysis = _infer_analysis_from_content([header] + body)
    header_str = ' '.join(header).upper()
    if not analysis:
        for keyword, name in ANALYSIS_SECTION_MAP.items():
            if keyword.upper() in header_str:
                analysis = name
                break
    if not analysis:
        analysis = page_default
    if not analysis:
        units = _table_units('', header)
        analysis = {
            'ug/g': 'pesticides', 'ug/kg': 'mycotoxins',
            'cfu/g': 'microbials', 'aw': 'moisture_foreign_matter',
        }.get(units)
        if not analysis and 'MOISTURE' in header_str:
            analysis = 'moisture_foreign_matter'
    return analysis or 'cannabinoids'

def _table_units(analysis: str, header: Optional[List[str]] = None) -> str:
    """The units of a table's rows that print none: the analysis
    default, unless the header names other units."""
    units = STANDARD_UNITS.get(analysis, 'percent')
    text = ' '.join(header or []).lower().replace('µ', 'u').replace('μ', 'u')
    if 'ug/g' in text:
        units = 'ug/g'
    elif 'ug/kg' in text:
        units = 'ug/kg'
    elif 'cfu' in text:
        units = 'cfu/g'
    elif re.search(r'\baw\b', text):
        units = 'aw'
    return units

def _continued_layout(body: List[List[str]], analysis: Optional[str],
                      layouts: List[Dict]) -> Optional[Dict]:
    """The layout of a table without a header.

    The layout of the last header with as many columns for the analysis
    its analytes name (the table it continues). Otherwise the table must
    print a PASS/FAIL or LOD/LOQ column, as TagLeaf result tables do (a
    summary such as "TOTAL THC | 39.4781 %" does not), and its layout
    is read from its cells (_infer_layout); when its analytes do not
    name the analysis, it takes the layout and analysis of the last
    header with as many columns. None when no layout applies.
    """
    ncols = len(body[0])
    same = [layout for layout in reversed(layouts) if layout['ncols'] == ncols]
    for layout in same:
        if analysis and layout['analysis'] == analysis:
            return layout
    inferred = _infer_layout(body, analysis)
    if inferred['status'] is None and inferred['lod_loq'] is None:
        return None
    if analysis:
        return {**inferred, 'analysis': analysis}
    return same[0] if same else None

def _is_status_row(name_upper: str) -> bool:
    """Whether a row name is a status-bar entry or note, not an analyte."""
    if name_upper in _STATUS_KEYWORDS:
        return True
    words = name_upper.split()
    return bool(words) and words[0] in _STATUS_KEYWORDS and len(name_upper) < 30

def _is_moisture_name(name_upper: str) -> bool:
    """Whether a row name is moisture or water activity."""
    return name_upper.startswith(('MOISTURE', 'WATER ACTIVITY'))

def _read_result_row(cells: List[str], layout: Dict, units: str) -> Dict:
    """Read one analyte row with a column layout.

    The result is read from the amount column only, never from the
    limit, LOD or LOQ; a non-detect is value None with its qualifier
    ('ND'), and '<0.05' is value None, qualifier '<LOQ', with 'loq' 0.05
    when the row prints no LOQ. Units are those printed in the result
    cell, else in its column label, else in the limit, else ``units``.

    Returns:
        A dict with 'value', 'qualifier', 'units', 'limit', 'lod',
        'loq' and 'status'.
    """
    def cell(index: Optional[int]) -> str:
        return cells[index] if index is not None and index < len(cells) else ''

    result_at = layout['result']
    result_text = cell(result_at)
    # Of two amounts, read the one printed in percent.
    other = cell(layout.get('result2'))
    if other and _cell_units(other) == 'percent' \
            and _cell_units(result_text) not in (None, 'percent'):
        result_at, result_text = layout['result2'], other
    value, qualifier, bound = _parse_result(result_text)

    limit_text = cell(layout.get('limit'))
    lod, loq = _parse_lod_loq(cell(layout.get('lod_loq')))
    if layout.get('lod') is not None:
        lod = _parse_number(cell(layout['lod']))
    if layout.get('loq') is not None:
        loq = _parse_number(cell(layout['loq']))
    if bound is not None:
        if qualifier == '<LOQ' and loq is None:
            loq = bound
        elif qualifier == '<LOD' and lod is None:
            lod = bound

    column_units = layout.get('units') or {}
    status = cell(layout.get('status')).upper()
    return {
        'value': value,
        'qualifier': qualifier,
        'units': (
            _cell_units(result_text)
            or column_units.get(result_at)
            or _cell_units(limit_text)
            or column_units.get(layout.get('limit'))
            or units
        ),
        'limit': _parse_number(limit_text),
        'lod': lod,
        'loq': loq,
        'status': status.lower() if status in ('PASS', 'FAIL') else '',
    }

def _parse_results_from_tables(pdf) -> Tuple[List[Dict], List[str]]:
    """Extract all analyte results from all pages using table extraction.

    Strategy: Each table is split at its header rows, and each part is
    read with the column layout of its header (_header_layout). A part
    without a header, the continuation of a table broken by a page, is
    read with the layout of the table it continues, or a layout read
    from its cells (_continued_layout). The analysis of a table is
    inferred from its analyte names, else from the page's section
    headers (e.g., "CANNABINOID PROFILE BY UPLC-UV // APR 02, 2024").

    Returns:
        Tuple of (results_list, analyses_list).
    """
    results = []
    analyses = set()
    layouts: List[Dict] = []
    pending: Optional[Tuple[List[str], Dict]] = None

    for page in pdf.pages:
        text = page.extract_text() or ''
        text_upper = text.upper()
        tables = page.extract_tables()

        # ── Detect all analysis sections on this page ─────────
        # Build a list of (line_index, analysis_type) for section headers.
        page_lines = text.split('\n')
        section_headers = []
        for li, line in enumerate(page_lines):
            detected = _detect_current_analysis(line)
            if detected:
                section_headers.append((li, detected))

        # Default: if no explicit section but page has cannabinoid keywords,
        # assume cannabinoids (covers page 1 where table headers may vary).
        if not section_headers:
            if any(kw in text_upper for kw in [
                'CANNABINOID PROFILE', 'CANNABINOID POTENCY',
                'POTENCY BY HPLC', 'POTENCY BY UPLC',
            ]):
                section_headers.append((0, 'cannabinoids'))
            elif any(kw in text_upper for kw in ['TERPENOID TESTING', 'TERPENES TESTING', 'TERPENES BY GC']):
                section_headers.append((0, 'terpenes'))

        # Assign a default analysis for this page.
        page_default_analysis = section_headers[0][1] if section_headers else None

        for table in tables:
            rows = [[_cell_text(c) for c in row] for row in (table or []) if row]
            rows = [row for row in rows if any(row)]
            if not rows:
                continue

            for header, layout, body in _table_segments(rows):

                # A header printed alone: its rows are the next table's.
                if layout is not None and not body:
                    pending = (header, layout)
                    continue

                # ── Determine the layout and analysis ─────────────
                if layout is None:
                    body = [row for row in body if _looks_like_result_row(row)]
                    if not body:
                        continue
                    if pending and pending[1]['ncols'] == len(body[0]):
                        header, layout = pending
                if layout is not None:
                    table_analysis = _table_analysis(header, body, page_default_analysis)
                    layout = {**layout, 'analysis': table_analysis}
                    layouts.append(layout)
                    units = _table_units(table_analysis, header)
                else:
                    table_analysis = _infer_analysis_from_content(body, has_header=False)
                    layout = _continued_layout(body, table_analysis, layouts)
                    if layout is None or layout.get('result') is None:
                        continue
                    table_analysis = layout['analysis']
                    units = _table_units(table_analysis)
                pending = None

                # Parse data rows.
                for cells in body:
                    if not cells[0] or cells[0].startswith('**'):
                        continue

                    analyte_name = cells[0]
                    if len(analyte_name) < 2:
                        continue

                    # Skip total/summary and per-serving/per-package rows.
                    name_upper = analyte_name.upper()
                    if any(p in name_upper for p in _SKIP_PATTERNS):
                        continue
                    if name_upper.strip(' *:') in _TOTAL_ROWS:
                        continue

                    # Skip sub-headings and notes (no cells but the name).
                    if not any(cells[1:]):
                        continue

                    key = _snake_case(analyte_name)
                    reading = _read_result_row(
                        cells, layout, _ANALYTE_UNITS.get(key, units))

                    # Skip status summary bar entries that pdfplumber may
                    # extract as table rows (e.g., "POTENCY PASS ...").
                    # Moisture and water activity are analytes when they
                    # print a reading.
                    analysis = table_analysis
                    if _is_moisture_name(name_upper):
                        if reading['value'] is None \
                                and reading['qualifier'] not in _READ_QUALIFIERS:
                            continue
                        analysis = 'moisture_foreign_matter'
                    elif _is_status_row(name_upper):
                        continue

                    result = {
                        'analysis': analysis,
                        'key': key,
                        'name': analyte_name,
                        'value': reading['value'],
                        'qualifier': reading['qualifier'],
                        'units': reading['units'],
                        'limit': reading['limit'],
                        'lod': reading['lod'],
                        'loq': reading['loq'],
                        'status': reading['status'],
                    }
                    analyses.add(analysis)
                    results.append(result)

    return results, sorted(analyses)

def _parse_batch_status(text: str) -> Dict:
    """Extract per-analysis pass/fail statuses from page 1."""
    statuses = {}
    status_pairs = re.findall(
        r'(POTENCY|FOREIGN|METALS|MICROBIAL|MOISTURE|MYCOTOXINS?|'
        r'PESTICIDES?|SOLVENTS?|TERPENES?|WATER|ADDITIVES?)\s+'
        r'(PASS|FAIL|TESTED)',
        text, re.IGNORECASE,
    )
    for name, status in status_pairs:
        key = name.strip().lower()
        statuses[key] = status.strip().lower()
    return statuses

# ── Main Entry Points ─────────────────────────────────────────────

def parse_tagleaf_pdf(
        parser: Any = None,
        doc: str = '',
    ) -> Dict:
    """Parse a TagLeaf LIMS COA PDF directly from the file.

    This is the primary parsing function for the hybrid engine.
    Extracts all data from the PDF using pdfplumber text and table
    extraction — no network access required.

    Args:
        parser: Optional CoADoc instance (for backwards compatibility).
                Not used in the hybrid path.
        doc:    Path to the COA PDF file.

    Returns:
        Dict with all extracted COA data in legacy CoADoc format
        (compatible with adapt_algorithm_output).
    """
    # Handle argument order flexibility.
    pdf_path = doc if doc else parser
    if isinstance(pdf_path, str) and not pdf_path.endswith('.pdf'):
        # parser was passed as first arg, doc as second
        pdf_path = doc

    if not pdf_path or not isinstance(pdf_path, str):
        raise ValueError('No PDF path provided.')

    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            raise ValueError(f'Empty PDF: {pdf_path}')

        # ── Extract full text from page 1 ─────────────────────
        try:
            page1_text = pdf.pages[0].extract_text() or ''
        except Exception:
            page1_text = ''
        # Clean null bytes and common PDF ligature artifacts.
        page1_text = page1_text.replace('\x00', '')
        # "fi" ligature often garbled: "Innite" → "Infinite", "Certicate" → "Certificate"
        page1_text = re.sub(r'\bInn(?:i|)te\b', 'Infinite', page1_text)
        page1_text = re.sub(r'\bCerti(?:i|)cate\b', 'Certificate', page1_text)
        page1_text = re.sub(r'\be(?:f|)cacy\b', 'efficacy', page1_text)
        lines = page1_text.split('\n')

        # ── Parse lab header ──────────────────────────────────
        obs = _parse_header(lines)

        # Fallback lab detection from page text if header wasn't found.
        if not obs.get('lab'):
            _KNOWN_LABS = [
                (r'Inn?finite\s+Chemical\s+Analysis\s+Labs?,?\s*([A-Z]{2})?',
                 'Infinite Chemical Analysis Labs'),
                (r'BelCosta\s+Labs?', 'BelCosta Labs'),
                (r'Green\s+Precision\s+Analytics', 'Green Precision Analytics'),
                (r'Verity\s+Analytics', 'Verity Analytics'),
                (r'2\s+River\s+Labs', '2 River Labs, Inc'),
                (r'Pure\s+Cannalyst\s+Labs', 'Pure Cannalyst Labs, Inc'),
                (r'Pride\s+Analytics', 'Pride Analytics'),
            ]
            for pattern, lab_name in _KNOWN_LABS:
                if re.search(pattern, page1_text, re.IGNORECASE):
                    obs['lab'] = lab_name
                    break

        # ── Parse sample line ─────────────────────────────────
        obs.update(_parse_sample_line(lines))

        # ── Parse metadata fields ─────────────────────────────
        obs.update(_parse_metadata_fields(page1_text))

        # ── Parse cultivator/distributor ──────────────────────
        obs.update(_parse_cultivator_distributor(page1_text))

        # ── Parse batch status ────────────────────────────────
        statuses = _parse_batch_status(page1_text)

        # ── Extract TagLeaf URL ───────────────────────────────
        lab_results_url = _extract_tagleaf_url(pdf)
        if lab_results_url:
            obs['lab_results_url'] = lab_results_url

        # ── Parse all results from tables ─────────────────────
        results, analyses = _parse_results_from_tables(pdf)

        # ── Compute totals from results if not in metadata ────
        if results:
            # Total terpenes (a non-detect's value is None).
            if not obs.get('total_terpenes'):
                terp_sum = sum(
                    r['value'] for r in results
                    if r['analysis'] == 'terpenes'
                    and r['key'] != 'total_terpenes'
                    and (r['value'] or 0) > 0
                )
                # Check if a total_terpenes result exists.
                for r in results:
                    if r['key'] == 'total_terpenes' and (r['value'] or 0) > 0:
                        obs['total_terpenes'] = r['value']
                        break
                else:
                    if terp_sum > 0:
                        obs['total_terpenes'] = round(terp_sum, 5)

        # ── Build analysis status fields ──────────────────────
        for analysis_type, status in statuses.items():
            obs[f'{analysis_type}_status'] = status

        # ── Finalize observation ──────────────────────────────
        obs = {**TAGLEAF, **obs}
        obs['analyses'] = json.dumps(analyses)
        obs['results'] = json.dumps(results)
        obs['coa_parsed_at'] = datetime.now().isoformat()

        # Generate a simple sample hash.
        hash_input = json.dumps(results, sort_keys=True)
        obs['results_hash'] = hashlib.sha256(
            hash_input.encode()).hexdigest()[:16]

        # Generate sample_id from results + product_name.
        id_input = (
            hash_input +
            obs.get('product_name', '') +
            obs.get('producer', '') +
            obs.get('date_tested', '')
        )
        obs['sample_id'] = obs.get('sample_id', '') or hashlib.sha256(
            id_input.encode()).hexdigest()[:16]

        # Store the lab's sample ID separately.
        obs['lab_id'] = obs.get('sample_id', '')

        # PDF filename for reference.
        obs['coa_pdf'] = pdf_path.replace('\\', '/').split('/')[-1]

    return obs

def parse_tagleaf_coa(
        parser: Any = None,
        doc: str = '',
        **kwargs,
    ) -> Dict:
    """Parse a TagLeaf LIMS COA PDF or URL.

    This is the main entry point registered in the LAB_REGISTRY.
    For the hybrid engine, this always parses from the PDF directly.

    Args:
        parser: Optional CoADoc instance (backwards compatibility).
        doc:    Path to the COA PDF file, or a URL.

    Returns:
        Dict with all extracted COA data.
    """
    # Handle argument order: (parser, doc) or (doc,)
    if isinstance(parser, str) and not doc:
        doc = parser
        parser = None
    elif parser is None and isinstance(doc, str):
        pass
    elif isinstance(parser, str) and isinstance(doc, str):
        # Legacy call: parse_tagleaf_coa(parser_instance, pdf_path)
        # parser is actually the parser object, doc is the path
        pass

    # For URLs, we cannot parse without network.
    if isinstance(doc, str) and doc.startswith('http'):
        raise ValueError(
            'URL parsing requires network access. '
            'Use the AI parser for URL-based COAs, or provide the PDF.'
        )

    return parse_tagleaf_pdf(parser, doc)

# ── Tests ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys
    import os

    # Test with provided PDF files.
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [f for f in os.listdir(test_dir) if f.endswith('.pdf')]

    if not test_files:
        if len(sys.argv) > 1:
            test_files = sys.argv[1:]
        else:
            print('Usage: python tagleaf.py <pdf_file> [pdf_file2 ...]')
            sys.exit(1)

    for pdf_file in test_files:
        pdf_path = os.path.join(test_dir, pdf_file) if not os.path.isabs(pdf_file) else pdf_file
        if not os.path.exists(pdf_path):
            print(f'Not found: {pdf_path}')
            continue
        try:
            data = parse_tagleaf_coa(None, pdf_path)
            print(f'\n{"="*60}')
            print(f'✓ {pdf_file}')
            print(f'  Product: {data.get("product_name", "?")}')
            print(f'  Type: {data.get("product_type", "?")}')
            print(f'  Lab: {data.get("lab", "?")}')
            print(f'  Date: {data.get("date_tested", "?")}')
            print(f'  THC: {data.get("total_thc", "?")}%')
            print(f'  CBD: {data.get("total_cbd", "?")}%')
            results = json.loads(data.get('results', '[]'))
            analyses = json.loads(data.get('analyses', '[]'))
            print(f'  Analyses: {analyses}')
            print(f'  Results: {len(results)} analytes')
            print(f'  URL: {data.get("lab_results_url", "none")}')
            print(f'  Sample ID: {data.get("sample_id", "?")}')
        except Exception as e:
            print(f'\n✗ {pdf_file}: {e}')
            import traceback
            traceback.print_exc()
