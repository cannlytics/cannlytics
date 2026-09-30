"""
Parse TagLeaf LIMS COA — COA Doc Hybrid Algorithm
Copyright (c) 2022-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2022
Updated: 3/6/2026
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
}

# Metrc tag prefixes (used to identify Metrc IDs in text).
METRC_PREFIXES = ['1A40']


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


def _parse_number(text: str) -> float:
    """Parse a numeric string, handling ND, <LOQ, etc."""
    if not text or not isinstance(text, str):
        return 0.0
    text = text.strip().upper()
    if text in ('ND', 'N/A', '', '-', 'N D', 'PASS', 'FAIL'):
        return 0.0
    if '<' in text or 'LOQ' in text:
        return 0.0
    # Remove units suffixes.
    text = re.sub(r'\s*(mg/g|%|µg/g|µg/kg|ug/g|ug/kg|ppm|ppb|cfu/g|aw|mg)\s*$',
                  '', text, flags=re.IGNORECASE).strip()
    try:
        return float(text.replace(',', ''))
    except (ValueError, TypeError):
        return 0.0


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


def _parse_lod_loq(text: str) -> Tuple[float, float]:
    """Parse a LOD/LOQ string like '0.0109/0.24767'."""
    if not text or '/' not in text:
        return 0.0, 0.0
    parts = text.strip().split('/')
    try:
        lod = float(parts[0].strip())
        loq = float(parts[1].strip())
        return lod, loq
    except (ValueError, IndexError):
        return 0.0, 0.0


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


def _infer_analysis_from_content(table) -> Optional[str]:
    """Infer analysis type from the analyte names in a table's rows.

    This is more reliable than section-header tracking for multi-section
    pages where pdfplumber table positions don't map cleanly to text
    line numbers.
    """
    if not table or len(table) < 2:
        return None

    # Collect analyte names from first ~8 data rows.
    names = []
    for row in table[1:9]:
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


def _parse_results_from_tables(pdf) -> Tuple[List[Dict], List[str]]:
    """Extract all analyte results from all pages using table extraction.

    Strategy: For each page, scan the full page text to find ALL analysis
    section headers (e.g., "CANNABINOID PROFILE BY UPLC-UV // APR 02, 2024").
    Then assign each table to the most recent section header that precedes it.

    Returns:
        Tuple of (results_list, analyses_list).
    """
    results = []
    analyses = set()

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
            if not table or len(table) < 2:
                continue

            header = table[0]
            if not header:
                continue
            header_str = ' '.join(str(c or '') for c in header).upper()

            # Skip non-result tables (overview, cultivator info, etc.).
            if not any(kw in header_str for kw in
                       ['ANALYTE', 'AMT', 'LOD', 'PASS', 'LIMIT']):
                continue

            # ── Determine analysis type for this table ────────
            # PRIMARY: Content-based inference from analyte names.
            # This is the most reliable method for multi-section pages.
            table_analysis = _infer_analysis_from_content(table)

            # FALLBACK 1: Check table header_str for analysis keywords.
            if not table_analysis:
                for keyword, analysis in ANALYSIS_SECTION_MAP.items():
                    if keyword.upper() in header_str:
                        table_analysis = analysis
                        break

            # FALLBACK 2: Use section headers from page text.
            if not table_analysis:
                table_analysis = page_default_analysis

            # FALLBACK 3: Infer from header units.
            if not table_analysis:
                if 'µG/G' in header_str or 'UG/G' in header_str:
                    table_analysis = 'pesticides'
                elif 'µG/KG' in header_str or 'UG/KG' in header_str:
                    table_analysis = 'mycotoxins'
                elif 'CFU' in header_str:
                    table_analysis = 'microbials'
                elif 'AW' in header_str or 'MOISTURE' in header_str:
                    table_analysis = 'moisture_foreign_matter'
                else:
                    table_analysis = 'cannabinoids'

            # Determine units from header.
            units = STANDARD_UNITS.get(table_analysis, 'percent')
            if 'µg/g' in header_str.lower() or 'ug/g' in header_str.lower():
                units = 'ug/g'
            elif 'µg/kg' in header_str.lower() or 'ug/kg' in header_str.lower():
                units = 'ug/kg'
            elif 'CFU' in header_str.upper():
                units = 'cfu/g'
            elif 'AW' in header_str.upper():
                units = 'aW'

            # Identify column indices.
            col_names = [str(c or '').upper().strip() for c in header]
            has_limit = any('LIMIT' in c for c in col_names)

            # Parse data rows.
            for row in table[1:]:
                if not row or not any(row):
                    continue

                cells = [str(c or '').strip() for c in row]
                if not cells[0] or cells[0].startswith('**'):
                    continue

                analyte_name = cells[0].replace('\n', ' ').strip()
                if not analyte_name or len(analyte_name) < 2:
                    continue

                # Skip total/summary and per-serving/per-package rows.
                name_upper = analyte_name.upper()
                skip_patterns = [
                    'TOTAL THC/', 'TOTAL CBD/', 'CBD/SRV', 'CBD/PKG',
                    'THC/SRV', 'THC/PKG', '/SRV', '/PKG',
                    'TOTAL THC**', 'TOTAL CBD**', 'TOT THC', 'TOT CBD',
                    'TOTAL THC *', 'TOTAL CBD *',
                    'TOTAL CANNABINOIDS', 'SUM OF CANNABINOIDS',
                    'SUM OF TERPENES',
                ]
                if any(p in name_upper for p in skip_patterns):
                    continue

                # Skip status summary bar entries that pdfplumber may
                # extract as table rows (e.g., "POTENCY PASS ...").
                status_keywords = {
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
                if name_upper in status_keywords:
                    continue
                # Also skip if first word is a status keyword and rest
                # looks like "PASS" or "FAIL" or another keyword.
                first_word = name_upper.split()[0] if name_upper.split() else ''
                if first_word in status_keywords and len(analyte_name) < 30:
                    continue

                key = _snake_case(analyte_name)
                result = {
                    'analysis': table_analysis,
                    'key': key,
                    'name': analyte_name,
                    'value': 0.0,
                    'units': units,
                    'limit': 0.0,
                    'lod': 0.0,
                    'loq': 0.0,
                    'status': '',
                }

                # Parse cells based on column structure.
                if has_limit and len(cells) >= 4:
                    # ANALYTE | LIMIT | AMT | LOD/LOQ | PASS/FAIL
                    result['limit'] = _parse_number(cells[1])
                    result['value'] = _parse_number(cells[2])
                    if len(cells) >= 4:
                        lod, loq = _parse_lod_loq(cells[3])
                        result['lod'] = lod
                        result['loq'] = loq
                    if len(cells) >= 5:
                        status = cells[4].strip().upper()
                        if status in ('PASS', 'FAIL'):
                            result['status'] = status.lower()
                elif len(cells) >= 4:
                    # ANALYTE | AMT | AMT(mg/g) | LOD/LOQ | PASS/FAIL
                    result['value'] = _parse_number(cells[1])
                    if len(cells) >= 4:
                        lod, loq = _parse_lod_loq(cells[3])
                        result['lod'] = lod
                        result['loq'] = loq
                    if len(cells) >= 5:
                        status = cells[4].strip().upper()
                        if status in ('PASS', 'FAIL'):
                            result['status'] = status.lower()
                elif len(cells) >= 3:
                    # Short format: ANALYTE | AMT | PASS/FAIL
                    result['value'] = _parse_number(cells[1])
                    if len(cells) >= 3:
                        status = cells[2].strip().upper()
                        if status in ('PASS', 'FAIL'):
                            result['status'] = status.lower()

                analyses.add(table_analysis)
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
            # Total terpenes.
            if not obs.get('total_terpenes'):
                terp_sum = sum(
                    r['value'] for r in results
                    if r['analysis'] == 'terpenes'
                    and r['key'] != 'total_terpenes'
                    and r['value'] > 0
                )
                # Check if a total_terpenes result exists.
                for r in results:
                    if r['key'] == 'total_terpenes' and r['value'] > 0:
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