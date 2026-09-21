"""
Parse Green Analytics COA — COA Doc Hybrid Algorithm (Offline-First)
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 6/28/2024
Updated: 3/8/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Green Analytics COA PDFs directly from the PDF text — no network
    access required. This is the modernized offline-first engine that
    extracts all data from the PDF itself using pdfplumber text
    extraction and regex-based field parsing.

    Green Analytics operates three state-specific laboratories:
        * Green Analytics East, LLC (NJ) — ITL License: TL000002
        * Green Analytics MD, LLC (MD)   — ITL License: L-17-00002
        * Green Analytics NY, LLC (NY)   — License: OCM-CPL-00013

    Identification:
        All Green Analytics COAs contain 'Green Analytics' and
        'greenanalyticsllc.com' in text or QR URLs. Format is
        determined by detecting 'East, LLC', 'MD, LLC', or 'NY, LLC'.

    Format notes:
        * NJ (East): 3-page, two-column page 1 (cannabinoids + terpenes),
          pages 2-3 for safety panels. METRC IDs, MRL-based reporting.
          Lab director: Tyler Lomax, Hamilton Township, NJ.
        * MD: 3-page, page 1 has cannabinoids, terpenes, and safety summary.
          Pages 2-3 for detailed safety results. Test Tags instead of METRC.
          Includes THCVa cannabinoid. Lab director: Daniel Kulakowski.
        * NY: 5-6 page multi-section format. Each analysis in its own box.
          Full Compliance Test or R&D Testing. Expanded pesticide/terpene
          panels (D10-THC isomers, Farnesene, Alpha-phellandrene, etc.).
          Lab directors: Matthew Elmes (current), Ellen Parkin (earlier).

Data Points:

    ✓ product_name, product_type, strain_name
    ✓ date_tested, date_received, date_collected, date_reported
    ✓ batch_number, sample_id (lab_id)
    ✓ lab, lab_license_number, lab_address, lab_state
    ✓ producer, producer_license_number, producer_address
    ✓ metrc_ids, metrc_lab_test_batch, source_package_id
    ✓ total_thc, total_cbd, total_cannabinoids, total_terpenes
    ✓ moisture_content, water_activity
    ✓ status (overall pass/fail)
    ✓ analyses (list of analysis types)
    ✓ results (list of analyte result dicts)
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


# ── Green Analytics Constants ──────────────────────────────────────

GREEN_ANALYTICS = {
    'coa_algorithm': 'green_analytics.py',
    'coa_algorithm_entry_point': 'parse_green_analytics_coa',
    'lims': 'Green Analytics',
    'lab': 'Green Analytics',
    'lab_website': 'https://www.greenanalyticsllc.com',
}

# Lab locations keyed by format detection.
GREEN_ANALYTICS_LOCATIONS = {
    'nj': {
        'lab': 'Green Analytics East, LLC',
        'lab_license_number': 'TL000002',
        'lab_address': '3535 Quakerbridge Rd., Suite 101',
        'lab_city': 'Hamilton Township',
        'lab_state': 'NJ',
        'lab_zipcode': '08619',
    },
    'md': {
        'lab': 'Green Analytics MD, LLC',
        'lab_license_number': 'L-17-00002',
        'lab_address': '',
        'lab_city': '',
        'lab_state': 'MD',
        'lab_zipcode': '',
    },
    'ny': {
        'lab': 'Green Analytics NY, LLC',
        'lab_license_number': 'OCM-CPL-00013',
        'lab_address': '401 North Middletown Road, Building 60B',
        'lab_city': 'Pearl River',
        'lab_state': 'NY',
        'lab_zipcode': '10965',
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
    'foreign': 'foreign_matter',
    'filth': 'foreign_matter',
    'water activity': 'water_activity',
    'moisture': 'moisture',
}

# Standard units per analysis type.
STANDARD_UNITS = {
    'cannabinoids': 'percent',
    'terpenes': 'percent',
    'pesticides': 'ppm',
    'heavy_metals': 'ppm',
    'microbials': 'cfu/g',
    'mycotoxins': 'ppb',
    'residual_solvents': 'ppm',
    'foreign_matter': 'percent',
    'water_activity': 'aw',
    'moisture': 'percent',
}


# ── ANALYTE_KEY_MAP ────────────────────────────────────────────────
# Maps display names (case-insensitive via .upper()) to snake_case keys.
ANALYTE_KEY_MAP = {
    # Cannabinoids — NJ/MD format names
    'CBD': 'cbd',
    'CBDA': 'cbda',
    'CBN': 'cbn',
    'Δ9-THC': 'delta_9_thc',
    'DELTA-9 THC': 'delta_9_thc',
    'DELTA 9 THC': 'delta_9_thc',
    'D9-THC': 'delta_9_thc',
    'D9 THC': 'delta_9_thc',
    'THC': 'delta_9_thc',
    'THCA': 'thca',
    'CBDV': 'cbdv',
    'CBG': 'cbg',
    'CBGA': 'cbga',
    'Δ8-THC': 'delta_8_thc',
    'DELTA-8 THC': 'delta_8_thc',
    'D8-THC': 'delta_8_thc',
    'THCV': 'thcv',
    'CBC': 'cbc',
    'THCVA': 'thcva',
    # NY-specific cannabinoid isomers
    'D10-THC-S': 'delta_10_thc_s',
    'D10-THC-R': 'delta_10_thc_r',
    # Terpenes
    'ALPHA-PINENE': 'alpha_pinene',
    'CAMPHENE': 'camphene',
    'SABINENE': 'sabinene',
    'BETA-PINENE': 'beta_pinene',
    'BETA-MYRCENE': 'beta_myrcene',
    'CARENE': 'delta_3_carene',
    '3-CARENE': 'delta_3_carene',
    'ALPHA-TERPINENE': 'alpha_terpinene',
    'LIMONENE': 'limonene',
    'D-LIMONENE': 'limonene',
    'EUCALYPTOL': 'eucalyptol',
    'OCIMENE': 'ocimene',
    'GAMMA-TERPINENE': 'gamma_terpinene',
    'SABINENE HYDRATE': 'sabinene_hydrate',
    'TERPINOLENE': 'terpinolene',
    'FENCHONE': 'fenchone',
    'LINALOOL': 'linalool',
    'FENCHOL': 'fenchol',
    'ISOPULEGOL': 'isopulegol',
    'CAMPHOR': 'camphor',
    'ISOBORNEOL': 'isoborneol',
    'BORNEOL': 'borneol',
    'MENTHOL': 'menthol',
    'TERPINEOL': 'terpineol',
    'NEROL': 'nerol',
    'PULEGONE': 'pulegone',
    'GERANIOL': 'geraniol',
    'GERANIOL ACETATE': 'geraniol_acetate',
    'BETA-CARYOPHYLLENE': 'beta_caryophyllene',
    'ALPHA-HUMULENE': 'alpha_humulene',
    'VALENCENE': 'valencene',
    'CIS-NEROLIDOL': 'cis_nerolidol',
    'TRANS-NEROLIDOL': 'trans_nerolidol',
    'CARYOPHYLLENE OXIDE': 'caryophyllene_oxide',
    'GUAIOL': 'guaiol',
    'CEDROL': 'cedrol',
    'BETA-EUDESMOL': 'beta_eudesmol',
    'ALPHA-BISABOLOL': 'alpha_bisabolol',
    # NY-specific terpenes
    'ALPHA-PHELLANDRENE': 'alpha_phellandrene',
    'P-CYMENE': 'p_cymene',
    'ALPHA-CEDRENE': 'alpha_cedrene',
    'FARNESENE': 'farnesene',
    'CITRONELLOL': 'citronellol',
    # MD-specific terpenes
    'ALPHA-CEDRENE': 'alpha_cedrene',
    # Heavy metals
    'ARSENIC': 'arsenic',
    'CADMIUM': 'cadmium',
    'CHROMIUM': 'chromium',
    'MERCURY': 'mercury',
    'LEAD': 'lead',
    'NICKEL': 'nickel',
    'COPPER': 'copper',
    'ANTIMONY': 'antimony',
    # Microbials
    'TOTAL YEAST AND MOLD COUNT': 'total_yeast_and_mold',
    'TOTAL YEAST AND MOLD COUNT *': 'total_yeast_and_mold',
    'TOTAL YEAST & MOLD': 'total_yeast_and_mold',
    'TOTAL AEROBIC MICROBIAL COUNT': 'total_aerobic_bacteria',
    'TOTAL AEROBIC MICROBIAL COUNT *': 'total_aerobic_bacteria',
    'TOTAL AEROBIC BACTERIA': 'total_aerobic_bacteria',
    'TOTAL COLIFORMS': 'total_coliforms',
    'E.COLI': 'e_coli',
    'STEC': 'stec',
    'SALMONELLA': 'salmonella',
    'SALMONELLA SPP': 'salmonella',
    'L. MONOCYTOGENES': 'l_monocytogenes',
    'SHIGA TOXIN-PRODUCING E. COLI': 'stec',
    'ASPERGILLUS (FUMIGATUS, FLAVUS, NIGER, TERREUS)': 'aspergillus',
    # Mycotoxins
    'AFLATOXIN B1': 'aflatoxin_b1',
    'AFLATOXIN B2': 'aflatoxin_b2',
    'AFLATOXIN G1': 'aflatoxin_g1',
    'AFLATOXIN G2': 'aflatoxin_g2',
    'OCHRATOXIN': 'ochratoxin_a',
    'OCHRATOXIN A': 'ochratoxin_a',
    'TOTAL AFLATOXINS': 'total_aflatoxins',
    # Residual solvents
    'PROPANE': 'propane',
    'N-BUTANE': 'n_butane',
    'ETHANOL': 'ethanol',
    'HEXANES': 'hexanes',
    'HEXANES, TOTAL': 'hexanes',
    'N-HEXANE': 'hexanes',
    'BENZENE': 'benzene',
    'N-HEPTANE': 'n_heptane',
    'TOLUENE': 'toluene',
    'TOTAL XYLENES': 'total_xylenes',
    'XYLENES, TOTAL': 'total_xylenes',
    'ACETONE': 'acetone',
    'ACETONITRILE': 'acetonitrile',
    'BUTANES, TOTAL': 'butanes_total',
    'CHLOROFORM': 'chloroform',
    'DICHLOROMETHANE': 'dichloromethane',
    'DIMETHYL SULFOXIDE': 'dimethyl_sulfoxide',
    'ETHYL ACETATE': 'ethyl_acetate',
    'ETHYL ETHER': 'ethyl_ether',
    'METHANOL': 'methanol',
    'PENTANES, TOTAL': 'pentanes_total',
    '2-PROPANOL': '2_propanol',
    '1,2-DICHLOROETHANE': '1_2_dichloroethane',
    'TRICHLOROETHANE': 'trichloroethane',
    'TETRAFLUOROETHANE (1,1,1,2-) (HFC-134A)': 'tetrafluoroethane',
    # Water activity & moisture
    'WATER ACTIVITY': 'water_activity',
    'MOISTURE CONTENT': 'moisture_content',
    'MOISTURE': 'moisture_content',
    # Foreign matter
    'FOREIGN MATTER': 'foreign_matter',
    'FOREIGN MATERIAL (OTHER, % M/M)': 'foreign_matter_other',
    'FOREIGN MATERIAL (STEMS, % M/M)': 'foreign_matter_stems',
    'MAMMALIAN EXCRETA (MG/LB)': 'mammalian_excreta',
    # Vitamin E Acetate
    'VITAMIN E ACETATE': 'vitamin_e_acetate',
}

# Pesticide names for content-based classification.
KNOWN_PESTICIDES = {
    'abamectin', 'acephate', 'acequinocyl', 'acetamiprid', 'aldicarb',
    'azadirachtin', 'azoxystrobin', 'bifenazate', 'bifenthrin', 'boscalid',
    'captan', 'carbaryl', 'carbofuran', 'chlorantraniliprole', 'chlorpyrifos',
    'clofentezine', 'clofentazine', 'cyfluthrin', 'daminozide', 'diazinon',
    'dichlorvos', 'dimethoate', 'etoxazole', 'fenpyroximate', 'fipronil',
    'flonicamid', 'fludioxonil', 'hexythiazox', 'imazalil', 'imidacloprid',
    'kresoxim-methyl', 'kresoxym-methyl', 'malathion', 'metalaxyl',
    'methiocarb', 'methomyl', 'myclobutanil', 'naled', 'oxamyl',
    'paclobutrazol', 'permethrin', 'phosmet', 'piperonyl butoxide',
    'propiconazole', 'pyrethrins', 'spinosad', 'spiromesifen',
    'spirotetramat', 'thiamethoxam', 'trifloxystrobin',
}

# Non-analyte keywords to skip.
SKIP_KEYWORDS = {
    'ANALYTE', 'METHODS:', 'MRL', 'LIMIT', 'UNIT', 'STATUS', 'DATE TESTED',
    'TOTAL CANNABINOIDS', 'TOTAL THC', 'TOTAL CBD', 'TOTAL CBG',
    'TOTAL TERPENES', 'POTENCY SUMMARY', 'PASS/FAIL', 'RESULT',
    'INSTRUMENT', '< MRL', 'PAGE',
}

# Logger.
logger = logging.getLogger(__name__)


# ── Utility Functions ──────────────────────────────────────────────

def _snake_case(name: str) -> str:
    """Convert analyte display name to snake_case key."""
    upper = name.strip().upper()
    # Direct lookup first.
    mapped = ANALYTE_KEY_MAP.get(upper)
    if mapped:
        return mapped
    # Handle Greek characters.
    s = name.strip()
    s = s.replace('Δ', 'delta_').replace('α', 'alpha_').replace('β', 'beta_')
    s = s.replace('γ', 'gamma_')
    # Normalize.
    s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
    s = re.sub(r'\s+', '_', s.strip())
    return s.lower()


def _parse_number(text: str) -> Optional[float]:
    """Parse a numeric value from COA text.
    Returns None for ND/Not Detected/<MRL/Not Tested/Not Required/Absent.
    """
    if text is None:
        return None
    t = text.strip().replace(',', '')
    if not t:
        return None
    # Non-detect patterns.
    nd_patterns = (
        '< MRL', '<MRL', 'ND', 'N/A', 'Not Tested', 'Not Detected',
        'Not Required', 'Absent', 'Not Present', '< LOD', '<LOD',
        '< LOQ', '<LOQ', 'Tested',
    )
    for pat in nd_patterns:
        if t.upper().startswith(pat.upper()) or t.upper() == pat.upper():
            return None
    # Handle <value patterns.
    if t.startswith('<'):
        t = t[1:].strip()
    # Strip trailing non-numeric.
    t = re.sub(r'[^0-9.\-].*$', '', t)
    if not t:
        return None
    try:
        return float(t)
    except (ValueError, TypeError):
        return None


def _parse_date(text: str) -> str:
    """Parse date string to ISO format (YYYY-MM-DD)."""
    if not text:
        return ''
    t = text.strip()
    # Remove time portion if present.
    t = re.sub(r'\s+\d{1,2}:\d{2}(:\d{2})?\s*(AM|PM)?', '', t, flags=re.IGNORECASE)
    t = t.strip()
    formats = [
        '%m/%d/%Y', '%m/%d/%y',
        '%b %d, %Y', '%B %d, %Y',
        '%Y-%m-%d',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(t, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return t


def _detect_format(text: str) -> str:
    """Detect which Green Analytics format (nj, md, ny)."""
    t = text.lower()
    if 'green analytics east' in t:
        return 'nj'
    if 'green analytics md' in t:
        return 'md'
    if 'green analytics ny' in t:
        return 'ny'
    # Fallback heuristics.
    if 'hamilton township, nj' in t:
        return 'nj'
    if 'pearl river, ny' in t:
        return 'ny'
    if 'sop-065-md' in t:
        return 'md'
    return 'nj'  # Default.


def _parse_status_from_text(text: str) -> str:
    """Determine overall PASS/FAIL from page 1 text."""
    t = text.upper()
    if 'SAMPLE RESULT: PASS' in t:
        return 'pass'
    if 'SAMPLE RESULT: FAIL' in t:
        return 'fail'
    if 'FAIL' in t and 'PASS' not in t:
        return 'fail'
    return 'pass'


def _sha256(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


# ── NJ (East) Format Parser ───────────────────────────────────────

def _parse_nj_metadata(text: str, lines: List[str]) -> Dict:
    """Parse metadata from NJ (East) format page 1."""
    obs = {}

    # Producer (licensee name) — first bold entity on page.
    m = re.search(r'^(.+?)\s+METRC ID:', text, re.MULTILINE)
    if m:
        obs['producer'] = m.group(1).strip()

    # METRC ID.
    m = re.search(r'METRC ID:\s*(\S+)', text)
    if m:
        obs['metrc_id'] = m.group(1).strip()

    # Source Package ID.
    m = re.search(r'Source Package ID:\s*(\S+)', text)
    if m:
        obs['source_package_id'] = m.group(1).strip()

    # Producer address.
    m = re.search(r'(\d+\s+US\s+\d+[^,]*,\s*\w[^,]+,\s*\w{2}\s+\d{5})', text)
    if m:
        obs['producer_address'] = m.group(1).strip()

    # Licensee permit number.
    m = re.search(r'Licensee Permit #:\s*(\S+)', text)
    if m:
        obs['producer_license_number'] = m.group(1).strip()

    # Batch ID.
    m = re.search(r'Batch ID:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['batch_number'] = m.group(1).strip()

    # Item Name.
    m = re.search(r'Item Name:\s*(.+?)(?:\s+Strain Name:|\n|$)', text)
    if m:
        obs['product_name'] = m.group(1).strip()

    # Strain Name.
    m = re.search(r'Strain Name:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['strain_name'] = m.group(1).strip()

    # Sample dates.
    m = re.search(r'Sample Collected:\s*([\d/]+)', text)
    if m:
        obs['date_collected'] = _parse_date(m.group(1))
    m = re.search(r'Sample Received:\s*([\d/]+)', text)
    if m:
        obs['date_received'] = _parse_date(m.group(1))

    # Lab ID.
    m = re.search(r'Lab ID:\s*(\S+)', text)
    if m:
        obs['sample_id'] = m.group(1).strip()

    # Manifest ID.
    m = re.search(r'Manifest ID:\s*(\S+)', text)
    if m:
        obs['manifest_id'] = m.group(1).strip()

    # METRC Lab Test Batch / product type.
    m = re.search(r'METRC Lab Test Batch\s+(.+?)(?:\n|$)', text)
    if m:
        obs['product_type'] = m.group(1).strip().lower()

    # Report Created.
    m = re.search(r'Report Created:\s*([\d/]+)', text)
    if m:
        obs['date_reported'] = _parse_date(m.group(1))

    # Date Tested (cannabinoids).
    m = re.search(r'Cannabinoids\*?\s+Date Tested\s+([\d/]+)', text)
    if m:
        obs['date_tested'] = _parse_date(m.group(1))

    # Water Activity value.
    m = re.search(r'([\d.]+)\s*Aw', text)
    if m:
        obs['water_activity'] = float(m.group(1))

    # Moisture Content value.
    m = re.search(r'Moisture Content\s*\n?([\d.]+)\s*%', text)
    if not m:
        m = re.search(r'([\d.]+)\s*%\s*\n?\s*PASS\s*\n?\s*(?:Tested|PASS)', text)
    if m:
        obs['moisture_content'] = float(m.group(1))

    return obs


def _parse_nj_cannabinoids(text: str) -> Tuple[List[Dict], Dict]:
    """Parse cannabinoid results from NJ page 1 text."""
    results = []
    totals = {}
    # Cannabinoid analyte lines: Name MRL Value_% Value_mg/g
    nj_cannabinoid_names = [
        'CBD', 'CBDa', 'CBN', 'Δ9-THC', 'THCa', 'CBDV', 'CBG', 'CBGa',
        'Δ8-THC', 'THCV', 'CBC',
    ]
    for name in nj_cannabinoid_names:
        # Match: analyte_name  MRL_value  result_or_MRL  result_mg_or_MRL
        escaped = re.escape(name)
        pattern = rf'^{escaped}\s+([\d.]+)\s+([\d.<> MRL]+)\s+([\d.<> MRL]+)'
        m = re.search(pattern, text, re.MULTILINE)
        if m:
            mrl_val = float(m.group(1))
            pct_raw = m.group(2).strip()
            mg_raw = m.group(3).strip()
            value = _parse_number(pct_raw)
            value_mg = _parse_number(mg_raw)
            results.append({
                'analysis': 'cannabinoids',
                'key': _snake_case(name),
                'name': name,
                'value': value,
                'mg_g': value_mg,
                'units': 'percent',
                'loq': mrl_val,
                'status': 'tested',
            })

    # Total Cannabinoids.
    m = re.search(r'Total Cannabinoids\s+([\d.]+)\s+([\d.]+)', text)
    if m:
        totals['total_cannabinoids'] = float(m.group(1))

    # Total THC.
    m = re.search(r'Total THC\s+\(THCA\*0\.877\)\s*\+\s*[ΔD]9-THC\s+([\d.]+)\s+([\d.]+)', text)
    if not m:
        m = re.search(r'Total THC\s+D8THC\+D9THC\+\(THCA\*0\.877\)\s+([\d.]+)', text)
    if m:
        totals['total_thc'] = float(m.group(1))

    # Total CBD.
    m = re.search(r'Total CBD\s+\(CBDA\*0\.877\)\s*\+\s*CBD\s+([\d.]+)', text)
    if m:
        totals['total_cbd'] = float(m.group(1))

    return results, totals


def _parse_nj_terpenes(text: str) -> List[Dict]:
    """Parse terpene results from NJ page 1 text."""
    results = []
    # Terpene section: each line is "name MRL value_% value_mg"
    # Extract the terpenes section.
    terp_match = re.search(r'Terpenes\s+Date Tested.*?\nTotal\s+([\d.]+)\s+([\d.]+)', text, re.DOTALL)
    if not terp_match:
        return results
    terp_text = terp_match.group(0)
    # Parse individual terpene lines.
    pattern = re.compile(
        r'^([\w\-()]+(?:\s+[\w\-()]+)*?)\s+([\d.]+)\s+([\d.<> MRL]+)\s+([\d.<> MRL]+)\s*$',
        re.MULTILINE
    )
    for m in pattern.finditer(terp_text):
        name = m.group(1).strip()
        # Skip header and non-analyte lines.
        if name.upper() in SKIP_KEYWORDS or name.startswith('Analyte') or name.startswith('%'):
            continue
        if name in ('Total', 'Methods:'):
            continue
        mrl_val = float(m.group(2))
        pct_raw = m.group(3).strip()
        mg_raw = m.group(4).strip()
        value = _parse_number(pct_raw)
        results.append({
            'analysis': 'terpenes',
            'key': _snake_case(name),
            'name': name,
            'value': value,
            'mg_g': _parse_number(mg_raw),
            'units': 'percent',
            'loq': mrl_val,
            'status': 'tested',
        })
    return results


def _parse_nj_safety_panels(pages: List) -> List[Dict]:
    """Parse safety panels from NJ pages 2-3."""
    results = []
    for page in pages:
        text = page.extract_text() or ''
        # Heavy Metals.
        _parse_nj_heavy_metals(text, results)
        # Microbials.
        _parse_nj_microbials(text, results)
        # Mycotoxins.
        _parse_nj_mycotoxins(text, results)
        # Pesticides.
        _parse_nj_pesticides(text, results)
        # Water Activity (already parsed from page 1).
        # Moisture Content (already parsed from page 1).
    return results


def _parse_nj_heavy_metals(text: str, results: List[Dict]):
    """Parse heavy metals from NJ format."""
    metals = ['Arsenic', 'Cadmium', 'Chromium', 'Mercury', 'Lead']
    for metal in metals:
        pattern = rf'{re.escape(metal)}\s+([\d.]+)\s+([\d.]+)\s+([\d.<> MRL]+)\s+(PASS|FAIL)'
        m = re.search(pattern, text)
        if m:
            results.append({
                'analysis': 'heavy_metals',
                'key': _snake_case(metal),
                'name': metal,
                'value': _parse_number(m.group(3)),
                'units': 'ppm',
                'limit': float(m.group(1)),
                'loq': float(m.group(2)),
                'status': m.group(4).lower(),
            })


def _parse_nj_microbials(text: str, results: List[Dict]):
    """Parse microbials from NJ format."""
    # Pattern: "Analyte_Name  Limit  Value  Status"
    microbial_names = {
        'Total Yeast and Mold Count': 'total_yeast_and_mold',
        'Total Yeast and Mold Count *': 'total_yeast_and_mold',
        'Total Aerobic Microbial Count': 'total_aerobic_bacteria',
        'Total Aerobic Microbial Count *': 'total_aerobic_bacteria',
        'E.coli': 'e_coli',
        'Salmonella': 'salmonella',
    }
    for name, key in microbial_names.items():
        escaped = re.escape(name)
        pattern = rf'{escaped}\s+(\d+)\s+([\d.<> MRL()\s]+?)\s+(PASS|FAIL|Not Tested|Not Required)'
        m = re.search(pattern, text)
        if m:
            limit_str = m.group(1)
            val_raw = m.group(2).strip()
            status = m.group(3).strip()
            if status in ('Not Tested', 'Not Required'):
                continue
            # Clean parenthetical MRL values like "< MRL (200)".
            val_clean = re.sub(r'\s*\(\d+\)', '', val_raw)
            results.append({
                'analysis': 'microbials',
                'key': key,
                'name': name.replace(' *', ''),
                'value': _parse_number(val_clean),
                'units': 'cfu/g',
                'limit': float(limit_str) if limit_str.isdigit() else None,
                'status': 'pass' if 'PASS' in status else 'fail',
            })
    # Absence-based microbials.
    for name_pat, key in [('Salmonella', 'salmonella'), ('E.coli', 'e_coli')]:
        if key not in [r['key'] for r in results if r['analysis'] == 'microbials']:
            m = re.search(rf'{re.escape(name_pat)}\s+Absence\s+(Absence|Not Detected)\s+(PASS)', text)
            if m:
                results.append({
                    'analysis': 'microbials',
                    'key': key,
                    'name': name_pat,
                    'value': None,
                    'units': 'cfu/g',
                    'status': 'pass',
                })


def _parse_nj_mycotoxins(text: str, results: List[Dict]):
    """Parse mycotoxins from NJ format."""
    mycotoxins = ['Aflatoxin B1', 'Aflatoxin B2', 'Aflatoxin G1',
                  'Aflatoxin G2', 'Ochratoxin']
    for name in mycotoxins:
        pattern = rf'{re.escape(name)}\s+([\d.]+)\s+([\d.]+)\s+([\d.<> MRL]+)\s+(PASS|FAIL)'
        m = re.search(pattern, text)
        if m:
            results.append({
                'analysis': 'mycotoxins',
                'key': _snake_case(name),
                'name': name,
                'value': _parse_number(m.group(3)),
                'units': 'ppb',
                'limit': float(m.group(1)),
                'loq': float(m.group(2)),
                'status': m.group(4).lower(),
            })


def _parse_nj_pesticides(text: str, results: List[Dict]):
    """Parse pesticides from NJ format."""
    # Pattern: "Pesticide_Name  Limit  MRL  Value  Status"
    pattern = re.compile(
        r'^([A-Z][\w\s\-()]+?)\s+([\d.]+)\s+([\d.]+)\s+([\d.<> MRL]+)\s+(PASS|FAIL)\s*$',
        re.MULTILINE
    )
    # Only parse lines within a Pesticides section.
    in_pesticides = False
    for line in text.split('\n'):
        line_stripped = line.strip()
        if 'Pesticides' in line_stripped and 'Continued' not in line_stripped:
            in_pesticides = True
            continue
        if in_pesticides:
            m = pattern.match(line_stripped)
            if m:
                name = m.group(1).strip()
                if name.lower() in KNOWN_PESTICIDES or len(name) > 3:
                    # Verify it's a pesticide name, not a header.
                    if name.upper() in SKIP_KEYWORDS:
                        continue
                    results.append({
                        'analysis': 'pesticides',
                        'key': _snake_case(name),
                        'name': name,
                        'value': _parse_number(m.group(4)),
                        'units': 'ppm',
                        'limit': float(m.group(2)),
                        'loq': float(m.group(3)),
                        'status': m.group(5).lower(),
                    })


# ── MD Format Parser ──────────────────────────────────────────────

def _parse_md_metadata(text: str, lines: List[str]) -> Dict:
    """Parse metadata from MD format page 1."""
    obs = {}

    # Producer name (first entity line).
    m = re.search(r'^(.+?)\s+Test Tag:', text, re.MULTILINE)
    if m:
        obs['producer'] = m.group(1).strip()

    # Test Tag (similar to METRC ID).
    m = re.search(r'Test Tag:\s*(\S+)', text)
    if m:
        obs['metrc_id'] = m.group(1).strip()

    # Source Package.
    m = re.search(r'Source Package:\s*(\S+)', text)
    if m:
        obs['source_package_id'] = m.group(1).strip()

    # Licensee Permit.
    m = re.search(r'Licensee Permit #:\s*(\S+)', text)
    if m:
        obs['producer_license_number'] = m.group(1).strip()

    # Item Name.
    m = re.search(r'Item Name:\s*(.+?)(?:\s+Sample Received:|\n|$)', text)
    if m:
        obs['product_name'] = m.group(1).strip()

    # Sample Received.
    m = re.search(r'Sample Received:\s*([\d/]+)', text)
    if m:
        obs['date_received'] = _parse_date(m.group(1))

    # Lab ID.
    m = re.search(r'Lab ID:\s*(\S+)', text)
    if m:
        obs['sample_id'] = m.group(1).strip()

    # Manifest ID.
    m = re.search(r'Manifest ID:\s*(\S+)', text)
    if m:
        obs['manifest_id'] = m.group(1).strip()

    # METRC Lab Test Batch / product type.
    m = re.search(r'METRC Lab Test Batch:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['product_type'] = m.group(1).strip().lower()

    # Report Created.
    m = re.search(r'Report Created:\s*([\d/]+)', text)
    if m:
        obs['date_reported'] = _parse_date(m.group(1))

    # Date Tested (cannabinoids).
    m = re.search(r'Cannabinoids\*?\s+Date Tested\s+([\d/]+)', text)
    if not m:
        m = re.search(r'Date Tested\s+([\d/]+)\s+Test Type:', text)
    if m:
        obs['date_tested'] = _parse_date(m.group(1))

    # Test Type.
    m = re.search(r'Test Type:\s*(\S+)', text)
    if m:
        obs['test_type'] = m.group(1).strip()

    return obs


def _parse_md_cannabinoids(text: str) -> Tuple[List[Dict], Dict]:
    """Parse cannabinoid results from MD format page 1.
    Handles both MRL-based (standard) and LOD/LOQ-based (edible) formats.
    """
    results = []
    totals = {}
    is_lodloq = 'LOD/LOQ' in text
    md_cann_names = [
        'CBD', 'CBDa', 'CBN', 'Δ9-THC', 'THCa', 'CBDV', 'CBG', 'CBGa',
        'Δ8-THC', 'THCV', 'CBC', 'THCVa',
    ]

    if is_lodloq:
        # Edible format: "Name  LOD / LOQ  Value_mg_serving  Value_mg_g"
        for name in md_cann_names:
            escaped = re.escape(name)
            # Match: Name  0.009 / 0.027  < LOD  < LOD  (or numeric values)
            pattern = rf'^{escaped}\s+([\d.]+)\s*/\s*([\d.]+)\s+([\d.<> LODQNotMRL]+)\s+([\d.<> LODQNotMRL]+)'
            m = re.search(pattern, text, re.MULTILINE)
            if m:
                lod_val = float(m.group(1))
                loq_val = float(m.group(2))
                val_raw = m.group(3).strip()
                mg_raw = m.group(4).strip()
                results.append({
                    'analysis': 'cannabinoids',
                    'key': _snake_case(name),
                    'name': name,
                    'value': _parse_number(val_raw),
                    'mg_g': _parse_number(mg_raw),
                    'units': 'mg/g',
                    'lod': lod_val,
                    'loq': loq_val,
                    'status': 'tested',
                })
    else:
        # Standard MRL format.
        for name in md_cann_names:
            escaped = re.escape(name)
            pattern = rf'^{escaped}\s+([\d.]+)\s+([\d.<> MRL]+)\s+([\d.<> MRL]+)'
            m = re.search(pattern, text, re.MULTILINE)
            if m:
                mrl_val = float(m.group(1))
                pct_raw = m.group(2).strip()
                mg_raw = m.group(3).strip()
                results.append({
                    'analysis': 'cannabinoids',
                    'key': _snake_case(name),
                    'name': name,
                    'value': _parse_number(pct_raw),
                    'mg_g': _parse_number(mg_raw),
                    'units': 'percent',
                    'loq': mrl_val,
                    'status': 'tested',
                })
        # Check for "THC" (without delta prefix) in some MD reports.
        if not any(r['key'] == 'delta_9_thc' for r in results):
            m = re.search(r'^THC\s+([\d.]+)\s+([\d.<> MRL]+)\s+([\d.<> MRL]+)', text, re.MULTILINE)
            if m:
                results.append({
                    'analysis': 'cannabinoids',
                    'key': 'delta_9_thc',
                    'name': 'THC',
                    'value': _parse_number(m.group(2)),
                    'mg_g': _parse_number(m.group(3)),
                    'units': 'percent',
                    'loq': float(m.group(1)),
                    'status': 'tested',
                })

    # Total THC.
    m = re.search(r'Total THC\s+D8THC\+D9THC\+\(THCA\*0\.877\)\s+([\d.]+)', text)
    if not m:
        m = re.search(r'Total THC\s+\(THCA\*0\.877\)\s*\+\s*[ΔD]9-THC\s+([\d.]+)', text)
    if m:
        totals['total_thc'] = float(m.group(1))

    # Total Cannabinoids.
    m = re.search(r'Total Cannabinoids\s+([\d.]+)\s+([\d.]+)', text)
    if m:
        totals['total_cannabinoids'] = float(m.group(1))

    return results, totals


def _parse_md_terpenes(text: str) -> Tuple[List[Dict], Dict]:
    """Parse terpene results from MD format page 1."""
    results = []
    totals = {}
    # Terpene lines: "name MRL value_% value_mg"
    # Also handles "Not Tested" and "Not Required".
    terp_block = re.search(r'Terpenes\s+Date Tested.*?(?:Total(?:\s+Terpenes)?\s+([\d.]+)\s+([\d.]+)|Total\s*\n)', text, re.DOTALL)
    if not terp_block:
        terp_block = re.search(r'Terpenes\s*\nAnalyte.*?(?:Total\s+([\d.]+)\s+([\d.]+))', text, re.DOTALL)
    if not terp_block:
        return results, totals
    terp_text = terp_block.group(0)

    pattern = re.compile(
        r'^([\w\-()]+(?:\s+[\w\-()]+)*?)\s+([\d.]+)\s+([\d.<> MRLNotTested]+)\s+([\d.<> MRLNotTested]+)\s*$',
        re.MULTILINE
    )
    for m in pattern.finditer(terp_text):
        name = m.group(1).strip()
        if name.upper() in SKIP_KEYWORDS or name in ('Analyte', 'Total', 'Methods:'):
            continue
        if name.startswith('%') or name.startswith('mg'):
            continue
        mrl_val = float(m.group(2))
        pct_raw = m.group(3).strip()
        mg_raw = m.group(4).strip()
        if 'Not Tested' in pct_raw or 'Not Required' in pct_raw:
            continue
        results.append({
            'analysis': 'terpenes',
            'key': _snake_case(name),
            'name': name,
            'value': _parse_number(pct_raw),
            'mg_g': _parse_number(mg_raw),
            'units': 'percent',
            'loq': mrl_val,
            'status': 'tested',
        })
    # Total terpenes.
    if terp_block.group(1):
        totals['total_terpenes'] = float(terp_block.group(1))
    return results, totals


# ── NY Format Parser ──────────────────────────────────────────────

def _parse_ny_product_name(page) -> str:
    """Extract product name from NY format using word-level extraction.
    The NY format has a two-column key-value layout where pdfplumber's
    line-level extraction interleaves columns. We use word coordinates
    to extract the right-column value text between 'Sample ID:' and
    'Sample Matrix:' rows (the product name spans this range).
    """
    try:
        words = page.extract_words()
        if not words:
            return ''
        # Find key label y-positions in the right column (x0 ≈ 302-355).
        id_label_y = None
        matrix_label_y = None
        value_x_min = 380  # Right-column values start around x=393.
        for i, w in enumerate(words):
            if w['text'] == 'ID:' and 300 < w['x0'] < 370:
                if i > 0 and words[i - 1]['text'] == 'Sample':
                    if id_label_y is None:  # Take first "Sample ID:"
                        id_label_y = w['top']
            if w['text'] == 'Matrix:' and 300 < w['x0'] < 370:
                if i > 0 and words[i - 1]['text'] == 'Sample':
                    matrix_label_y = w['top']
        if id_label_y is None or matrix_label_y is None:
            return ''
        # Collect value words between Sample ID and Sample Matrix rows,
        # excluding the Sample ID value itself (on the id_label_y row).
        name_words = []
        for w in words:
            if (w['x0'] >= value_x_min
                    and w['top'] > id_label_y + 5
                    and w['top'] < matrix_label_y - 2):
                name_words.append((w['top'], w['x0'], w['text']))
        # Sort by y then x.
        name_words.sort(key=lambda t: (t[0], t[1]))
        return ' '.join(w[2] for w in name_words)
    except Exception:
        return ''


def _parse_ny_metadata(text: str, lines: List[str], page=None) -> Dict:
    """Parse metadata from NY format page 1."""
    obs = {}

    # Sample ID.
    m = re.search(r'Sample ID:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['sample_id'] = m.group(1).strip()

    # Product name: try word-level extraction first, then regex fallback.
    if page is not None:
        name = _parse_ny_product_name(page)
        if name:
            obs['product_name'] = name
    if not obs.get('product_name'):
        # Regex fallback: try same-line extraction.
        m = re.search(r'Sample Name:\s+(\S.+?)$', text, re.MULTILINE)
        if m and m.group(1).strip():
            obs['product_name'] = m.group(1).strip()

    # Client Name — stop at right-column labels.
    m = re.search(r'Client Name:\s*(.+?)(?:\s+Sample (?:Name|ID|Matrix):|\n|$)', text)
    if m:
        producer_raw = m.group(1).strip()
        # If the product name was already extracted, the two-column merge
        # may have appended it to the client name. Strip it.
        if obs.get('product_name') and len(obs['product_name']) > 3:
            # Check if product name words appear at the end of the producer.
            pn_first_word = obs['product_name'].split()[0]
            idx = producer_raw.find(pn_first_word)
            if idx > 3:  # Must have some producer text before the name.
                producer_raw = producer_raw[:idx].strip()
        obs['producer'] = producer_raw

    # Sampling Location — stop at right-column labels.
    m = re.search(r'Sampling Location:\s*(.+?)(?:\s+(?:Sample (?:Matrix|Sub)|1g\b|0\.\d+g)|\n|$)', text)
    if m:
        obs['producer_address'] = m.group(1).strip()

    # License Number.
    m = re.search(r'License Number:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['producer_license_number'] = m.group(1).strip()

    # Sample Matrix.
    m = re.search(r'Sample Matrix:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['product_type'] = m.group(1).strip().lower()

    # Sample Sub Type.
    m = re.search(r'Sample Sub Type:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['product_subtype'] = m.group(1).strip().lower()

    # Batch Lot ID.
    m = re.search(r'Batch Lot ID:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['batch_number'] = m.group(1).strip()

    # Package ID.
    m = re.search(r'Package ID:\s*(.+?)(?:\n|$)', text)
    if m:
        pid = m.group(1).strip()
        if pid:
            obs['package_id'] = pid

    # Date Reported.
    m = re.search(r'Date Reported:\s*([\d/]+)', text)
    if m:
        obs['date_reported'] = _parse_date(m.group(1))

    # Sampling Date.
    m = re.search(r'Sampling Date:\s*([\d/]+)', text)
    if m:
        obs['date_collected'] = _parse_date(m.group(1))

    # Date Tested from Potency section.
    m = re.search(r'Date Tested:\s*([\d/]+)', text)
    if m:
        obs['date_tested'] = _parse_date(m.group(1))

    # Serving Size.
    m = re.search(r'Serving Size \(g\):\s*([\d.]+)', text)
    if m:
        obs['serving_size_g'] = float(m.group(1))

    # Batch Size.
    m = re.search(r'Batch Size:\s*(\d+)', text)
    if m:
        obs['batch_size'] = int(m.group(1))

    # Medical/Adult Use.
    m = re.search(r'Medical/Adult Use:\s*(.+?)(?:\n|$)', text)
    if m:
        obs['medical_adult_use'] = m.group(1).strip()

    # Overall status.
    obs['status'] = _parse_status_from_text(text)

    return obs


def _parse_ny_cannabinoids(text: str) -> Tuple[List[Dict], Dict]:
    """Parse cannabinoid results from NY format."""
    results = []
    totals = {}
    # NY cannabinoid lines: "Analyte  %w/w  mg/serving  MRL(%w/w)"
    ny_cannabinoid_names = [
        'CBDV', 'CBDA', 'CBGA', 'CBG', 'CBD', 'THCV', 'CBN',
        'D9-THC', 'D8-THC', 'D10-THC-S', 'D10-THC-R', 'CBC', 'THCA',
    ]
    for name in ny_cannabinoid_names:
        escaped = re.escape(name)
        pattern = rf'^{escaped}\s+([\d.<> MRL]+)\s+([\d.<> MRL]+)\s+([\d.]+)'
        m = re.search(pattern, text, re.MULTILINE)
        if m:
            pct_raw = m.group(1).strip()
            mg_raw = m.group(2).strip()
            mrl_val = float(m.group(3))
            results.append({
                'analysis': 'cannabinoids',
                'key': _snake_case(name),
                'name': name,
                'value': _parse_number(pct_raw),
                'mg_g': _parse_number(mg_raw),
                'units': 'percent',
                'loq': mrl_val,
                'status': 'tested',
            })

    # Total THC from Potency Summary.
    m = re.search(r'Total THC\s+\[.*?\]\s+([\d.]+)', text)
    if m:
        totals['total_thc'] = float(m.group(1))

    # Total CBD.
    m = re.search(r'Total CBD\s+\[.*?\]\s+([\d.<> MRL]+)', text)
    if m:
        val = _parse_number(m.group(1))
        if val is not None:
            totals['total_cbd'] = val

    # Total Cannabinoids.
    m = re.search(r'Total Cannabinoids\s+([\d.]+)', text)
    if m:
        totals['total_cannabinoids'] = float(m.group(1))

    return results, totals


def _parse_ny_terpenes(text: str) -> Tuple[List[Dict], Dict]:
    """Parse terpene results from NY format pages."""
    results = []
    totals = {}
    # NY terpene lines: "name  result(%w/w)  MRL(%w/w)"
    pattern = re.compile(
        r'^([\w\-]+(?:\s+[\w\-]+)*?)\s+([\d.<> MRL]+)\s+([\d.]+)\s*$',
        re.MULTILINE
    )
    # Find terpene section.
    terp_section = re.search(r'Terpenes:.*?(?:Total Terpenes|Page \d+ of \d+)', text, re.DOTALL)
    if not terp_section:
        return results, totals
    terp_text = terp_section.group(0)

    for m in pattern.finditer(terp_text):
        name = m.group(1).strip()
        if name.upper() in SKIP_KEYWORDS or name in ('Analyte', 'MRL'):
            continue
        if name.startswith('Page') or name.startswith('Result'):
            continue
        result_raw = m.group(2).strip()
        mrl_val = float(m.group(3))
        results.append({
            'analysis': 'terpenes',
            'key': _snake_case(name),
            'name': name,
            'value': _parse_number(result_raw),
            'units': 'percent',
            'loq': mrl_val,
            'status': 'tested',
        })

    # Total Terpenes.
    m = re.search(r'Total Terpenes \(% w/w\)\s+([\d.]+)', terp_text)
    if m:
        totals['total_terpenes'] = float(m.group(1))

    return results, totals


def _parse_ny_pesticides(text: str) -> List[Dict]:
    """Parse pesticide results from NY format."""
    results = []
    # NY pesticide lines: "name  PASS/FAIL  result(ug/g)  limit(ug/g)  MRL(ug/g)"
    pattern = re.compile(
        r'^(\w[\w\s\-(),./]+?)\s+(PASS|FAIL)\s+([\d.<> MRL]+)\s+([\d.]+)\s+([\d.]+)\s*$',
        re.MULTILINE
    )
    pest_section = re.search(r'Pesticides:.*?(?:Page \d+ of \d+)', text, re.DOTALL)
    if not pest_section:
        return results
    pest_text = pest_section.group(0)

    for m in pattern.finditer(pest_text):
        name = m.group(1).strip()
        if name.upper() in SKIP_KEYWORDS or name == 'Analyte':
            continue
        results.append({
            'analysis': 'pesticides',
            'key': _snake_case(name),
            'name': name,
            'value': _parse_number(m.group(3)),
            'units': 'ug/g',
            'limit': float(m.group(4)),
            'loq': float(m.group(5)),
            'status': m.group(2).lower(),
        })
    return results


def _parse_ny_heavy_metals(text: str) -> List[Dict]:
    """Parse heavy metals from NY format."""
    results = []
    pattern = re.compile(
        r'^(\w[\w\s]+?)\s+(PASS|FAIL)\s+([\d.<> MRL]+)\s+([\d.]+)\s+([\d.]+)\s*$',
        re.MULTILINE
    )
    hm_section = re.search(r'Heavy Metals:.*?(?:Page \d+ of \d+|Microbiological)', text, re.DOTALL)
    if not hm_section:
        return results
    hm_text = hm_section.group(0)

    for m in pattern.finditer(hm_text):
        name = m.group(1).strip()
        if name.upper() in SKIP_KEYWORDS or name == 'Analyte':
            continue
        results.append({
            'analysis': 'heavy_metals',
            'key': _snake_case(name),
            'name': name,
            'value': _parse_number(m.group(3)),
            'units': 'ug/g',
            'limit': float(m.group(4)),
            'loq': float(m.group(5)),
            'status': m.group(2).lower(),
        })
    return results


def _parse_ny_mycotoxins(text: str) -> List[Dict]:
    """Parse mycotoxins from NY format."""
    results = []
    pattern = re.compile(
        r'^(\w[\w\s]+?)\s+(PASS|FAIL)\s+([\d.<> MRL]+)\s+([\d.]+)\s+([\d.]+)\s*$',
        re.MULTILINE
    )
    myco_section = re.search(r'Mycotoxins:.*?(?:Page \d+ of \d+|Heavy Metals)', text, re.DOTALL)
    if not myco_section:
        return results
    myco_text = myco_section.group(0)

    for m in pattern.finditer(myco_text):
        name = m.group(1).strip()
        if name.upper() in SKIP_KEYWORDS or name == 'Analyte':
            continue
        results.append({
            'analysis': 'mycotoxins',
            'key': _snake_case(name),
            'name': name,
            'value': _parse_number(m.group(3)),
            'units': 'ug/g',
            'limit': float(m.group(4)),
            'loq': float(m.group(5)),
            'status': m.group(2).lower(),
        })
    return results


def _parse_ny_microbials(text: str) -> List[Dict]:
    """Parse microbials from NY format."""
    results = []
    # NY microbials: "name  PASS/FAIL  result(CFU/g)  limit(CFU/g)  MRL(CFU/g)"
    pattern = re.compile(
        r'^([\w\s\-(),]+?)\s+(PASS|FAIL)\s+([\d.<> MRLAbsent]+)\s+([\d.Absent\w]+)\s+([\d.]+)\s*$',
        re.MULTILINE
    )
    micro_section = re.search(r'Microbiological Screen:.*?(?:Page \d+ of \d+|Moisture)', text, re.DOTALL)
    if not micro_section:
        return results
    micro_text = micro_section.group(0)

    for m in pattern.finditer(micro_text):
        name = m.group(1).strip()
        if name.upper() in SKIP_KEYWORDS or name == 'Analyte':
            continue
        val_raw = m.group(3).strip()
        limit_raw = m.group(4).strip()
        results.append({
            'analysis': 'microbials',
            'key': _snake_case(name),
            'name': name,
            'value': _parse_number(val_raw),
            'units': 'cfu/g',
            'limit': _parse_number(limit_raw),
            'loq': float(m.group(5)),
            'status': m.group(2).lower(),
        })
    return results


def _parse_ny_moisture_water(text: str) -> List[Dict]:
    """Parse moisture and water activity from NY format."""
    results = []
    # Moisture.
    m = re.search(r'Moisture\s+PASS\s+([\d.]+)\s+([\d.]+)', text)
    if m:
        results.append({
            'analysis': 'moisture',
            'key': 'moisture_content',
            'name': 'Moisture',
            'value': float(m.group(1)),
            'units': 'percent',
            'limit': float(m.group(2)),
            'status': 'pass',
        })
    # Water Activity.
    m = re.search(r'Water Activity\s+PASS\s+([\d.]+)\s+([\d.]+)', text)
    if m:
        results.append({
            'analysis': 'water_activity',
            'key': 'water_activity',
            'name': 'Water Activity',
            'value': float(m.group(1)),
            'units': 'aw',
            'limit': float(m.group(2)),
            'status': 'pass',
        })
    return results


def _parse_ny_residual_solvents(text: str) -> List[Dict]:
    """Parse residual solvents from NY format."""
    results = []
    pattern = re.compile(
        r'^([\w\-(),.\s/]+?)\s+(PASS|FAIL)\s+([\d.<> MRL]+)\s+(\d+)\s+([\d.]+)\s*$',
        re.MULTILINE
    )
    solv_section = re.search(r'Residual Solvents:.*?(?:Page \d+ of \d+)', text, re.DOTALL)
    if not solv_section:
        return results
    solv_text = solv_section.group(0)

    for m in pattern.finditer(solv_text):
        name = m.group(1).strip()
        if name.upper() in SKIP_KEYWORDS or name == 'Analyte':
            continue
        results.append({
            'analysis': 'residual_solvents',
            'key': _snake_case(name),
            'name': name,
            'value': _parse_number(m.group(3)),
            'units': 'ug/g',
            'limit': float(m.group(4)),
            'loq': float(m.group(5)),
            'status': m.group(2).lower(),
        })
    return results


# ── Analyses Detection ────────────────────────────────────────────

def _detect_analyses_nj(text: str) -> List[str]:
    """Detect which analyses were performed from NJ page 1 summary."""
    analyses = ['cannabinoids']
    t = text.upper()
    if 'TERPENES' in t:
        analyses.append('terpenes')
    # Safety summary boxes.
    for label, analysis in [
        ('PESTICIDES', 'pesticides'),
        ('MYCOTOXINS', 'mycotoxins'),
        ('HEAVY METALS', 'heavy_metals'),
        ('MICROBIALS', 'microbials'),
        ('SOLVENTS', 'residual_solvents'),
        ('WATER ACTIVITY', 'water_activity'),
        ('MOISTURE', 'moisture'),
        ('FOREIGN MATTER', 'foreign_matter'),
    ]:
        if label in t:
            # Check for "Not Tested" or "Not Required" next to it.
            idx = t.index(label)
            context = t[idx:idx + len(label) + 50]
            if 'NOT TESTED' not in context and 'NOT REQUIRED' not in context:
                analyses.append(analysis)
    return analyses


def _detect_analyses_ny(text: str) -> List[str]:
    """Detect analyses from NY page 1 status grid."""
    analyses = []
    mapping = {
        'Potency': 'cannabinoids',
        'Terpenes': 'terpenes',
        'Pesticides': 'pesticides',
        'Heavy Metals': 'heavy_metals',
        'Mycotoxins': 'mycotoxins',
        'Microbiological': 'microbials',
        'Residual Solvents': 'residual_solvents',
        'Water Activity': 'water_activity',
        'Moisture': 'moisture',
        'Filth & Foreign Material': 'foreign_matter',
    }
    for label, analysis in mapping.items():
        pattern = rf'{re.escape(label)}\s+(T|P|F)'
        m = re.search(pattern, text)
        if m:
            analyses.append(analysis)
    return analyses if analyses else ['cannabinoids']


# ── Main Entry Point ──────────────────────────────────────────────

def parse_green_analytics_coa(
        parser: Any = None,
        doc: str = '',
        **kwargs,
    ) -> Dict[str, Any]:
    """Parse a Green Analytics COA PDF.

    This is the hybrid engine entry point. Called as:
        algorithm(None, file_path)

    Args:
        parser: Legacy CoADoc instance (ignored, always None).
        doc: PDF file path string, or pdfplumber PDF object.

    Returns:
        Flat dictionary with metadata + JSON-serialized results/analyses.
    """
    # Handle both string paths and pdfplumber objects.
    if isinstance(doc, str):
        pdf_path = doc
        report = pdfplumber.open(doc)
        should_close = True
    else:
        pdf_path = getattr(doc, 'stream', None)
        pdf_path = getattr(pdf_path, 'name', '') if pdf_path else ''
        report = doc
        should_close = False

    try:
        obs = {}
        obs['coa_pdf'] = pdf_path.replace('\\', '/').split('/')[-1] if pdf_path else ''

        # Extract full text from all pages.
        all_text = ''
        page_texts = []
        for page in report.pages:
            pt = page.extract_text() or ''
            page_texts.append(pt)
            all_text += pt + '\n'

        if not page_texts:
            return obs

        p1_text = page_texts[0]
        p1_lines = p1_text.split('\n')

        # Detect format.
        fmt = _detect_format(p1_text)
        loc = GREEN_ANALYTICS_LOCATIONS.get(fmt, GREEN_ANALYTICS_LOCATIONS['nj'])
        obs.update(loc)

        results = []
        analyses = []
        totals = {}

        if fmt == 'ny':
            # ── NY Format ────────────────────────────────────
            meta = _parse_ny_metadata(p1_text, p1_lines, page=report.pages[0])
            obs.update(meta)
            analyses = _detect_analyses_ny(p1_text)

            # Cannabinoids (page 1).
            cann_results, cann_totals = _parse_ny_cannabinoids(p1_text)
            results.extend(cann_results)
            totals.update(cann_totals)

            # Parse all pages for remaining analyses.
            full_text = '\n'.join(page_texts)

            # Terpenes (typically page 2).
            terp_results, terp_totals = _parse_ny_terpenes(full_text)
            results.extend(terp_results)
            totals.update(terp_totals)
            # Fallback: search full text for total terpenes if not found.
            if 'total_terpenes' not in totals:
                m = re.search(r'Total Terpenes \(% w/w\)\s+([\d.]+)', full_text)
                if m:
                    totals['total_terpenes'] = float(m.group(1))

            # Pesticides (typically page 3-4).
            results.extend(_parse_ny_pesticides(full_text))

            # Heavy Metals.
            results.extend(_parse_ny_heavy_metals(full_text))

            # Mycotoxins.
            results.extend(_parse_ny_mycotoxins(full_text))

            # Microbials.
            results.extend(_parse_ny_microbials(full_text))

            # Moisture & Water Activity.
            results.extend(_parse_ny_moisture_water(full_text))

            # Residual Solvents.
            results.extend(_parse_ny_residual_solvents(full_text))

        elif fmt == 'md':
            # ── MD Format ────────────────────────────────────
            meta = _parse_md_metadata(p1_text, p1_lines)
            obs.update(meta)
            analyses = _detect_analyses_nj(p1_text)

            # Cannabinoids (page 1).
            cann_results, cann_totals = _parse_md_cannabinoids(p1_text)
            results.extend(cann_results)
            totals.update(cann_totals)

            # Terpenes (page 1, below cannabinoids).
            terp_results, terp_totals = _parse_md_terpenes(p1_text)
            results.extend(terp_results)
            totals.update(terp_totals)

            # Safety panels (pages 2-3).
            if len(report.pages) > 1:
                for page_idx in range(1, len(report.pages)):
                    page_text = page_texts[page_idx]
                    _parse_nj_heavy_metals(page_text, results)
                    _parse_nj_microbials(page_text, results)
                    _parse_nj_mycotoxins(page_text, results)
                    _parse_nj_pesticides(page_text, results)

                    # MD-specific: Water Activity.
                    m = re.search(r'Water Activity\s+[\d.]+\s+([\d.]+)\s+PASS', page_text)
                    if m:
                        obs['water_activity'] = float(m.group(1))
                    # Moisture Content.
                    m = re.search(r'Moisture Content\s+([\d.]+)\s+PASS', page_text)
                    if m:
                        obs['moisture_content'] = float(m.group(1))

        else:
            # ── NJ Format ────────────────────────────────────
            meta = _parse_nj_metadata(p1_text, p1_lines)
            obs.update(meta)
            analyses = _detect_analyses_nj(p1_text)

            # Cannabinoids (page 1 left column).
            cann_results, cann_totals = _parse_nj_cannabinoids(p1_text)
            results.extend(cann_results)
            totals.update(cann_totals)

            # Terpenes (page 1 right column).
            terp_results = _parse_nj_terpenes(p1_text)
            results.extend(terp_results)
            # Total terpenes.
            m = re.search(r'^Total\s+([\d.]+)\s+([\d.]+)', p1_text, re.MULTILINE)
            if m:
                totals['total_terpenes'] = float(m.group(1))

            # Safety panels (pages 2-3).
            if len(report.pages) > 1:
                safety_results = _parse_nj_safety_panels(report.pages[1:])
                results.extend(safety_results)

        # Apply totals.
        obs.update(totals)

        # If date_tested not found, try report created date.
        if not obs.get('date_tested') and obs.get('date_reported'):
            obs['date_tested'] = obs['date_reported']

        # Set status from results.
        if not obs.get('status'):
            if any(r.get('status') == 'fail' for r in results):
                obs['status'] = 'fail'
            else:
                obs['status'] = 'pass'

        # Determine product_type from product_name if missing.
        if not obs.get('product_type') and obs.get('product_name'):
            pn = obs['product_name'].lower()
            if 'flower' in pn or 'bud' in pn:
                obs['product_type'] = 'flower'
            elif 'distillate' in pn:
                obs['product_type'] = 'concentrate'
            elif 'edible' in pn or 'chocolate' in pn or 'gummy' in pn:
                obs['product_type'] = 'edible'
            elif 'vape' in pn or 'cart' in pn:
                obs['product_type'] = 'vape'
            elif 'pre-roll' in pn or 'preroll' in pn:
                obs['product_type'] = 'preroll'
            elif 'badder' in pn or 'wax' in pn or 'shatter' in pn or 'concentrate' in pn:
                obs['product_type'] = 'concentrate'

        # Clean up product_type.
        if obs.get('product_type'):
            pt = obs['product_type']
            pt_map = {
                'raw plant material': 'flower',
                'solvent based concentrate': 'concentrate',
                'infused edible': 'edible',
            }
            obs['product_type'] = pt_map.get(pt, pt)

        # ── Finalize Output ──────────────────────────────────
        obs = {**GREEN_ANALYTICS, **obs}

        # Deduplicate analyses list.
        result_analyses = list(set(r['analysis'] for r in results))
        all_analyses = list(set(analyses + result_analyses))
        obs['analyses'] = json.dumps(sorted(all_analyses))
        obs['results'] = json.dumps(results)

        # Generate hashes.
        results_str = json.dumps(results, sort_keys=True)
        obs['results_hash'] = hashlib.sha256(results_str.encode()).hexdigest()

        # Sample hash.
        sample_str = json.dumps(
            {k: v for k, v in obs.items() if k != 'sample_hash'},
            sort_keys=True, default=str,
        )
        obs['sample_hash'] = hashlib.sha256(sample_str.encode()).hexdigest()

        # PDF hash.
        if pdf_path and isinstance(pdf_path, str):
            try:
                obs['pdf_hash'] = _sha256(pdf_path)
            except (FileNotFoundError, OSError):
                pass

        # Parsing attribution.
        obs['coa_parsed_at'] = datetime.now().isoformat()
        obs['parsing_method'] = 'algorithm'
        obs['parsing_algorithm'] = f'green_analytics_{fmt}'

        return obs

    except Exception as e:
        logger.error(f'Green Analytics parse failed: {e}', exc_info=True)
        return {'error': str(e)}

    finally:
        if should_close:
            report.close()


# === Tests ===
if __name__ == '__main__':
    import os
    import sys

    test_dir = '/mnt/user-data/uploads'
    test_files = [f for f in os.listdir(test_dir) if f.endswith('.pdf')]

    print(f'Found {len(test_files)} PDFs to test.\n')
    for f in sorted(test_files):
        filepath = os.path.join(test_dir, f)
        try:
            # Quick format check.
            with pdfplumber.open(filepath) as pdf:
                p1 = pdf.pages[0].extract_text() or ''
                if 'green analytics' not in p1.lower():
                    continue

            data = parse_green_analytics_coa(None, filepath)
            fmt = data.get('parsing_algorithm', '?')
            name = data.get('product_name', '?')
            total_thc = data.get('total_thc', '?')
            n_results = len(json.loads(data.get('results', '[]')))
            analyses = json.loads(data.get('analyses', '[]'))
            status = data.get('status', '?')
            print(f'  [{fmt}] {f[:40]:40s} | {name[:35]:35s} | THC={total_thc} | {n_results} results | {status} | {analyses}')
        except Exception as e:
            print(f'  FAIL: {f} — {e}')
