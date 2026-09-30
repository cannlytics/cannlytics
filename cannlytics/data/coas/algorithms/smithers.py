"""
Parse Smithers CTS COA -- COA Doc Hybrid Algorithm (Offline-First)
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 3/8/2026
Updated: 3/8/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Smithers CTS COA PDFs directly from the PDF text -- no
    network access required. This is the modernized offline-first engine
    that extracts all data from the PDF itself using pdfplumber text
    extraction and regex-based field parsing.

    Smithers CTS operates cannabis testing laboratories in:
      * Arizona: Smithers CTS Arizona LLC
          - 734 W Highland Avenue, 2nd Floor, Phoenix, AZ 85013
          - License #: 00000020LCVT89602592, Accreditation #: 103104
          - Technical Lab Director: Ahmed Munshi
      * New York: Smithers CTS New York LLC
          - 49 John Hicks Drive, Warwick, NY 10990
          - Permit #: OCM-CPL-00004, Accreditation #: 121747
          - Lab Manager: Weston Owen
      * Note: The NY location is the same facility as "Phyto-Farma Labs"
        (a Smithers company). NY COAs may be branded as either Smithers
        or Phyto-Farma. If branded as Phyto-Farma, use phytofarma.py.

    Identification:
        Smithers COAs contain 'Smithers' (case-insensitive) in page 1
        text, and/or 'smithers.com' in the footer. The key fingerprints
        are 'Smithers CTS Arizona' for AZ and 'Smithers CTS New York'
        for NY.

    Format notes:
        * AZ format (primary):
          - Page 1: Summary + "COMPLIANCE FOR RETAIL" + headline totals
          - Page 2: Cannabinoid Profile (HPLC) -- single table
          - Page 3: Terpene Total (GC-FID) -- TWO-COLUMN layout
          - Page 4: Microbial Analysis -- multiple sub-sections (E. coli,
            Salmonella, Aspergillus) with text-based criteria
          - Page 5: Residual Solvents (HS-GC-MS) -- TWO-COLUMN layout
          - Page 6: Heavy Metals (ICP-MS) + Mycotoxins (LC-MS/MS)
          - Page 7: Pesticides, Fungicides, Growth Regulators -- TWO-COLUMN
          - Page 8: Qualifier Legend (skip)
          - Page 9: Notes (may contain extraction method, cultivator info)
          - Some COAs have Moisture Analysis and/or Water Activity pages
        * NY format: Nearly identical to Phyto-Farma modern format.
          Uses "Average Cannabinoid Profile" with LOQ-only columns,
          8 trace metals, separate Pesticides LC/GC pages, and
          Microbial MDG/TAPC/TYMC sections. For NY-branded COAs,
          this parser delegates to the phytofarma.py format internally.

    AZ Table Column Structures:
        Cannabinoids: Analyte | LOD(mg/g) | LOQ(mg/g) | Dil. | Actual%(w/w) | mg/g | Qualifier
        Terpenes (2-col): Analyte | LOD/LOQ(%) | Dil. | Results(%) | Qualifier
        Residual Solvents (2-col): Analyte | LOD/LOQ(ppm) | Dil. | Action Limit(ppm) | Results(ppm) | Qualifier
        Heavy Metals: Analyte | LOD(ppm) | LOQ(ppm) | Dil. | Action Limit(ppm) | Results(ppm) | Qualifier
        Mycotoxins: Analyte | LOD(ppb) | LOQ(ppb) | Dil. | Action Limit(ppb) | Results(ppb) | Qualifier
        Pesticides (2-col): Analyte | LOD/LOQ(ppm) | Dil. | Action Limit(ppm) | Results(ppm) | Qualifier
        Microbials: Analyte | Allowable Criteria | Actual Result | Pass/Fail | Qualifier

Data Points:

    * product_name, product_type, strain_name
    * date_tested, date_received, date_sampled, date_harvested, date_manufactured
    * batch_number, sample_size, sample_id (lab_id)
    * lab, lab_license_number, lab_address, lab_phone
    * producer, producer_license_number, producer_address
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


# ── Smithers CTS Constants ────────────────────────────────────────

SMITHERS = {
    'coa_algorithm': 'smithers.py',
    'coa_algorithm_entry_point': 'parse_smithers_coa',
    'lims': 'Smithers',
    'lab': 'Smithers',
    'lab_website': 'https://www.smithers.com',
}

# Lab locations keyed by state detection.
SMITHERS_LOCATIONS = {
    'az': {
        'lab': 'Smithers CTS Arizona LLC',
        'lab_address': '734 W Highland Avenue, 2nd Floor, Phoenix, AZ 85013',
        'lab_street': '734 W Highland Avenue, 2nd Floor',
        'lab_city': 'Phoenix',
        'lab_state': 'AZ',
        'lab_zipcode': '85013',
        'lab_phone': '(602) 806-6930',
        'lab_license_number': '00000020LCVT89602592',
        'lab_accreditation': '103104',
    },
    'ny': {
        'lab': 'Smithers CTS New York LLC',
        'lab_address': '49 John Hicks Drive, Warwick, NY 10990',
        'lab_street': '49 John Hicks Drive',
        'lab_city': 'Warwick',
        'lab_state': 'NY',
        'lab_zipcode': '10990',
        'lab_phone': '(845) 202-9737',
        'lab_license_number': 'OCM-CPL-00004',
        'lab_accreditation': '121747',
    },
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
    'moisture': 'percent',
    'water_activity': 'aw',
}

# ── ANALYTE_KEY_MAP ────────────────────────────────────────────────
# Maps display names (uppercase) to standardized snake_case keys.
ANALYTE_KEY_MAP = {
    # ── Cannabinoids ──
    'CBC': 'cbc',
    'CBD': 'cbd',
    'CBDA': 'cbda',
    'CBDV': 'cbdv',
    'CBG': 'cbg',
    'CBGA': 'cbga',
    'CBN': 'cbn',
    'D8-THC': 'delta_8_thc',
    'D9-THC': 'delta_9_thc',
    'THCA': 'thca',
    'THCV': 'thcv',
    'THCVA': 'thcva',
    # NY extended cannabinoid panel
    'TOTAL TETRAHYDROCANNABINOL (THC)': 'total_thc',
    'TETRAHYDROCANNABINOLIC ACID (THCA)': 'thca',
    'Δ9-THC': 'delta_9_thc',
    'Δ8-THC': 'delta_8_thc',
    'Δ10-THC-RS': 'delta_10_thc_rs',
    'D10-THC-RS': 'delta_10_thc_rs',
    'Δ10-THC-RR': 'delta_10_thc_rr',
    'D10-THC-RR': 'delta_10_thc_rr',
    'TOTAL CANNABIDIOL (CBD)': 'total_cbd',
    'CANNABIDIOLIC ACID (CBDA)': 'cbda',
    'CANNABIDIOL (CBD)': 'cbd',
    'TOTAL ACTIVE TETRAHYDROCANNABIVARIN (THCV)': 'total_thcv',
    'TETRAHYDROCANNABIVARINIC ACID (THCVA)': 'thcva',
    'TETRAHYDROCANNABIVARIN (THCV)': 'thcv',
    'TOTAL ACTIVE CANNABIGEROL (CBG)': 'total_cbg',
    'CANNABIGEROLIC ACID (CBGA)': 'cbga',
    'CANNABIGEROL (CBG)': 'cbg',
    'CANNABIDIVARIN (CBDV)': 'cbdv',
    'CANNABINOL (CBN)': 'cbn',
    'CANNABICHROMENE (CBC)': 'cbc',
    'CANNABINOID TOTALS': '_skip_',
    # ── Terpenes ──
    '3-CARENE': 'delta_3_carene',
    'ALPHA-BISABOLOL': 'alpha_bisabolol',
    'ALPHA-CEDRENE': 'alpha_cedrene',
    'ALPHA-HUMULENE': 'alpha_humulene',
    'ALPHA-PHELLANDRENE': 'alpha_phellandrene',
    'ALPHA-PINENE': 'alpha_pinene',
    'ALPHA-TERPINENE': 'alpha_terpinene',
    'ALPHA-TERPINEOL': 'alpha_terpineol',
    'BETA-MYRCENE': 'beta_myrcene',
    'BETA-PINENE': 'beta_pinene',
    'BORNEOL': 'borneol',
    'CAMPHENE': 'camphene',
    'CAMPHOR': 'camphor',
    'CARYOPHYLLENE OXIDE': 'caryophyllene_oxide',
    'CEDRENE': 'cedrene',
    'CEDROL': 'cedrol',
    'CIS-NEROLIDOL': 'cis_nerolidol',
    'CIS-OCIMENE': 'cis_ocimene',
    'EUCALYPTOL': 'eucalyptol',
    'FARNESENE': 'farnesene',
    'FENCHOL': 'fenchol',
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
    'PULEGONE (+)': 'pulegone',
    'PULEGONE': 'pulegone',
    'SABINENE': 'sabinene',
    'SABINENE HYDRATE': 'sabinene_hydrate',
    'TERPINEOL': 'terpineol',
    'TERPINOLENE': 'terpinolene',
    'TRANS-CARYOPHYLLENE': 'trans_caryophyllene',
    'TRANS-NEROLIDOL': 'trans_nerolidol',
    'TRANS-OCIMENE': 'trans_ocimene',
    'TRANS-B-OCIMENE': 'trans_beta_ocimene',
    'VALENCENE': 'valencene',
    'TOTAL TERPENES': 'total_terpenes',
    # ── Heavy metals ──
    'ARSENIC': 'arsenic',
    'CADMIUM': 'cadmium',
    'LEAD': 'lead',
    'MERCURY': 'mercury',
    'ANTIMONY (SB)': 'antimony',
    'ARSENIC (AS)': 'arsenic',
    'CADMIUM (CD)': 'cadmium',
    'CHROMIUM (CR)': 'chromium',
    'COPPER (CU)': 'copper',
    'LEAD (PB)': 'lead',
    'MERCURY (HG)': 'mercury',
    'NICKEL (NI)': 'nickel',
    # ── Mycotoxins ──
    'TOTAL AFLATOXINS': 'total_aflatoxins',
    'AFLATOXIN B1': 'aflatoxin_b1',
    'AFLATOXIN B2': 'aflatoxin_b2',
    'AFLATOXIN G1': 'aflatoxin_g1',
    'AFLATOXIN G2': 'aflatoxin_g2',
    'OCHRATOXIN A': 'ochratoxin_a',
    'SUM OF AFLATOXINS': 'total_aflatoxins',
    # ── Microbials ──
    'E. COLI': 'e_coli',
    'SALMONELLA': 'salmonella',
    'ASPERGILLUS FLAVUS': 'aspergillus_flavus',
    'ASPERGILLUS FUMIGATUS': 'aspergillus_fumigatus',
    'ASPERGILLUS NIGER': 'aspergillus_niger',
    'ASPERGILLUS TERREUS': 'aspergillus_terreus',
    'SHIGA TOXIN-PRODUCING ESCHERICHIA COLI': 'stec',
    'SALMONELLA SPECIES': 'salmonella',
    'TOTAL AEROBIC BACTERIA/CDP-TC': 'total_aerobic_bacteria',
    'TOTAL YEAST AND MOLD': 'total_yeast_and_mold',
    # ── Residual solvents ──
    'ACETONE': 'acetone',
    'ACETONITRILE': 'acetonitrile',
    'BENZENE': 'benzene',
    'BUTANES': 'butanes',
    'CHLOROFORM': 'chloroform',
    'DICHLOROMETHANE': 'dichloromethane',
    'ETHANOL': 'ethanol',
    'ETHYL ACETATE': 'ethyl_acetate',
    'ETHYL ETHER': 'ethyl_ether',
    'HEPTANE': 'heptane',
    'HEXANES': 'hexanes',
    'ISOPROPYL ACETATE': 'isopropyl_acetate',
    'METHANOL': 'methanol',
    'PENTANES': 'pentanes',
    '2-PROPANOL (IPA)': 'isopropanol',
    'TOLUENE': 'toluene',
    'XYLENES': 'xylenes',
    # NY extended solvents
    '1,2-DICHLOROETHANE (ETHYLENE DICHLORIDE, ETHYLENE CHLORIDE)': 'dichloroethane',
    '2-PROPANOL (ISOPROPANOL, ISOPROPYL ALCOHOL)': 'isopropanol',
    'ACETONE (2-PROPANONE)': 'acetone',
    'BUTANES, TOTAL': 'butanes',
    'DICHLOROMETHANE (METHYLENE CHLORIDE)': 'dichloromethane',
    'DIMETHYL SULFOXIDE (DMSO)': 'dmso',
    'ETHANOL (ETHYL ALCOHOL)': 'ethanol',
    'ETHYL ACETATE (ACETIC ACID ETHYL ESTER)': 'ethyl_acetate',
    "ETHYL ETHER (DIETHYL ETHER, 1,1'-OXYBISETHANE)": 'ethyl_ether',
    'HEPTANE (N-HEPTANE)': 'heptane',
    'HEXANES, TOTAL': 'hexanes',
    'METHANOL (METHYL ALCOHOL)': 'methanol',
    'PENTANES, TOTAL': 'pentanes',
    'PROPANE': 'propane',
    'TOLUENE (METHYLBENZENE)': 'toluene',
    'TRICHLOROETHANE (1,1,1-)': 'trichloroethane',
    'TETRAFLUOROETHANE (1,1,1,2-) (HFC134A)*': 'tetrafluoroethane',
    'TETRAFLUOROETHANE (1,1,1,2-) (HFC134A)': 'tetrafluoroethane',
    'XYLENES, TOTAL (ORTHO-, META-, PARA-)': 'xylenes',
    # ── Pesticides (comprehensive AZ + NY panels) ──
    'ABAMECTIN B1A': 'abamectin',
    'ABAMECTIN': 'abamectin',
    'ACEPHATE': 'acephate',
    'ACEQUINOCYL': 'acequinocyl',
    'ACETAMIPRID': 'acetamiprid',
    'ALDICARB': 'aldicarb',
    'AZADIRACHTIN': 'azadirachtin',
    'AZOXYSTROBIN': 'azoxystrobin',
    'BIFENAZATE': 'bifenazate',
    'BIFENTHRIN': 'bifenthrin',
    'BOSCALID': 'boscalid',
    'CAPTAN': 'captan',
    'CARBARYL': 'carbaryl',
    'CARBOFURAN': 'carbofuran',
    'CHLORANTRANILIPROLE': 'chlorantraniliprole',
    'CHLORDANE': 'chlordane',
    'CHLORFENAPYR': 'chlorfenapyr',
    'CHLORMEQUAT CHLORIDE': 'chlormequat_chloride',
    'CHLORPYRIFOS': 'chlorpyrifos',
    'CLOFENTEZINE': 'clofentezine',
    'COUMAPHOS': 'coumaphos',
    'CYFLUTHRIN': 'cyfluthrin',
    'CYPERMETHRIN': 'cypermethrin',
    'DAMINOZIDE': 'daminozide',
    'DIAZINON': 'diazinon',
    'DICHLORVOS': 'dichlorvos',
    'DIMETHOATE': 'dimethoate',
    'DIMETHOMORPH': 'dimethomorph',
    'ETHOPROPHOS': 'ethoprophos',
    'ETOFENPROX': 'etofenprox',
    'ETOXAZOLE': 'etoxazole',
    'FENHEXAMID': 'fenhexamid',
    'FENOXYCARB': 'fenoxycarb',
    'FENPYROXIMATE': 'fenpyroximate',
    'FIPRONIL': 'fipronil',
    'FLONICAMID': 'flonicamid',
    'FLUDIOXONIL': 'fludioxonil',
    'HEXYTHIAZOX': 'hexythiazox',
    'IMAZALIL': 'imazalil',
    'IMIDACLOPRID': 'imidacloprid',
    'INDOLE-3-BUTYRIC ACID': 'indole_3_butyric_acid',
    'KRESOXIM-METHYL': 'kresoxim_methyl',
    'KRESOXIM METHYL': 'kresoxim_methyl',
    'MALATHION': 'malathion',
    'METALAXYL': 'metalaxyl',
    'METHIOCARB': 'methiocarb',
    'METHOMYL': 'methomyl',
    'METHYL PARATHION': 'methyl_parathion',
    'MEVINPHOS': 'mevinphos',
    'MGK-264': 'mgk_264',
    'MYCLOBUTANIL': 'myclobutanil',
    'NALED': 'naled',
    'OXAMYL': 'oxamyl',
    'PACLOBUTRAZOL': 'paclobutrazol',
    'PENTACHLORONITROBENZENE': 'pentachloronitrobenzene',
    'PERMETHRINS': 'permethrins',
    'PERMETHRINS, TOTAL': 'permethrins',
    'PHOSMET': 'phosmet',
    'PIPERONYL BUTOXIDE': 'piperonyl_butoxide',
    'PRALLETHRIN': 'prallethrin',
    'PROPICONAZOLE': 'propiconazole',
    'PROPOXUR': 'propoxur',
    'PYRETHRINS': 'pyrethrins',
    'PYRIDABEN': 'pyridaben',
    'SPINETORAM, TOTAL': 'spinetoram',
    'SPINOSAD': 'spinosad',
    'SPINOSAD, TOTAL': 'spinosad',
    'SPIROMESIFEN': 'spiromesifen',
    'SPIROTETRAMAT': 'spirotetramat',
    'SPIROXAMINE': 'spiroxamine',
    'TEBUCONAZOLE': 'tebuconazole',
    'THIACLOPRID': 'thiacloprid',
    'THIAMETHOXAM': 'thiamethoxam',
    'TRIFLOXYSTROBIN': 'trifloxystrobin',
    # ── Moisture / Water Activity ──
    'MOISTURE CONTENT': 'moisture_content',
    'WATER ACTIVITY': 'water_activity',
}

# Non-data line patterns to skip.
SKIP_PATTERNS = {
    'QUALIFIER LEGEND', 'CANNABINOID TOTALS', 'TOTAL CANNABINOIDS',
    'TERPENE TOTALS', 'TOTAL TERPENES', 'TOTAL THC =',
    'ND = NOT DETECTED', 'NT = NOT TESTED', '<LOQ = BELOW',
    'SERVING WEIGHT', 'DOSE WEIGHT', 'TOTAL ACTIVE',
    'PAGE ', 'CERTIFICATE:', 'AHMED MUNSHI', 'WESTON OWEN',
    'TECHNICAL LABORATORY', 'LABORATORY MANAGER',
    'THE PRODUCT ASSOCIATED', 'TESTING RESULTS WERE',
    'THIS COA IS GOVERNED', 'THIS IS A SMITHERS',
    'ACCREDITATION', 'SMITHERS CTS', 'WEIGHT %:',
    'SAMPLE PREP', 'SAMPLE ANALYSIS', 'BATCH DATE:',
    'BATCH NUMBER:', 'SOP:', 'SAMPLE WEIGHT:', 'VOLUME:',
    'TEST ID:', 'ANALYST:', 'ANALYZED BY:', 'DATE:',
    'CULTIVATED BY:', 'MANUFACTURED BY:', 'DISCLAIMER:',
    'USING MARIJUANA', 'DISTRIBUTION CHAIN',
    'NOTES:', 'REPORT NOTES:',
}

# Logger.
logger = logging.getLogger(__name__)


# ── Utility Functions ──────────────────────────────────────────────

def _snake_case(name: str) -> str:
    """Convert analyte display name to snake_case key."""
    stripped = name.strip()
    upper = stripped.upper()
    # Remove trailing qualifier codes and markers.
    clean_upper = re.sub(r'[†*]+$', '', upper).strip()
    mapped = ANALYTE_KEY_MAP.get(upper) or ANALYTE_KEY_MAP.get(clean_upper)
    if mapped:
        return mapped
    # Fallback: normalize to snake_case.
    s = stripped.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s


def _parse_number(text: str) -> Optional[float]:
    """Parse a numeric value from text.
    Returns None for ND/Not Detected, 0.0 for <LOQ, float otherwise.
    """
    if text is None:
        return None
    t = text.strip().replace(',', '')
    if not t or t in ('ND', 'N/A', '-', '', 'None', 'NT'):
        return None
    if t.startswith('Not '):
        return None
    if t.startswith('<') or 'LOQ' in t.upper():
        return 0.0
    # Strip trailing qualifier codes (e.g., "0.1575 Q3 M2" -> "0.1575").
    t = re.sub(r'\s+[A-Z][0-9].*$', '', t)
    # Strip trailing non-numeric chars.
    t = re.sub(r'[^0-9.\-].*$', '', t)
    try:
        return float(t)
    except (ValueError, TypeError):
        return None


def _parse_date(text: str) -> str:
    """Parse date string to ISO format (YYYY-MM-DD)."""
    if not text or not isinstance(text, str):
        return ''
    t = text.strip()
    # Remove time portion.
    t = re.sub(r'\s+\d{1,2}:\d{2}(:\d{2})?\s*(AM|PM|am|pm)?\s*$', '', t).strip()
    for fmt in ('%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%B %d, %Y', '%b %d, %Y'):
        try:
            return datetime.strptime(t, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return t


def _find_first_number(line: str) -> int:
    """Find the index of the first standalone numeric value or '<' in a line.
    Skips digits that are part of analyte names (e.g., d8-THC, 3-Carene).
    A standalone number is preceded by a space.
    """
    # First try: find a digit or '<' preceded by whitespace (standalone number).
    match = re.search(r'\s([\d<])', line)
    if match:
        return match.start(1)
    # Fallback: first digit or '<' anywhere.
    match = re.search(r'[\d<]', line)
    return match.start() if match else len(line)


def _should_skip_line(line: str) -> bool:
    """Check if a line is a non-data line that should be skipped."""
    upper = line.strip().upper()
    if not upper or len(upper) < 2:
        return True
    return any(skip in upper for skip in SKIP_PATTERNS)


# ── Location Detection ─────────────────────────────────────────────

def _detect_location(text: str) -> str:
    """Detect which Smithers location produced this COA.
    Returns: 'az' or 'ny'.
    """
    lower = text.lower()
    if 'smithers cts arizona' in lower or 'phoenix, az' in lower:
        return 'az'
    if 'smithers cts new york' in lower or 'warwick, ny' in lower:
        return 'ny'
    # Fallback: check sample ID prefix.
    m = re.search(r'Sample ID:\s*\d{4}SM([A-Z]{2})', text)
    if m:
        state = m.group(1)
        if state == 'AZ':
            return 'az'
        if state == 'NY':
            return 'ny'
    return 'az'  # Default to AZ.


def _detect_format(text: str, location: str) -> str:
    """Detect the COA format variant.
    Returns: 'az' or 'ny'.
    """
    return location


# ── AZ Metadata Parsing ───────────────────────────────────────────

def _parse_metadata_az(front_text: str, front_page) -> Dict:
    """Parse metadata from an AZ-format page 1."""
    obs = {}
    lines = front_text.split('\n')

    # ── Producer info from header (top-left block) ──
    # The first line is usually the producer/company name.
    # Lines before "License #:" and "Sample ID:" contain producer info.
    try:
        crop = front_page.within_bbox(
            (0, 0, front_page.width * 0.55, front_page.height * 0.13)
        )
        header_text = crop.extract_text() or ''
        header_lines = header_text.split('\n')
        if header_lines:
            # First line is the company name.
            obs['producer'] = header_lines[0].strip()
            # Look for address lines (before "License #").
            addr_parts = []
            for h_line in header_lines[1:]:
                if 'License' in h_line or 'Sample ID' in h_line or 'Batch' in h_line:
                    break
                if h_line.strip():
                    addr_parts.append(h_line.strip())
            if addr_parts:
                obs['producer_address'] = ', '.join(addr_parts)
    except Exception:
        pass

    # ── Producer license ──
    m = re.search(r'^License\s*#:\s*(\S+)', front_text, re.MULTILINE)
    if m:
        obs['producer_license_number'] = m.group(1)

    # ── Product name (line immediately after "Certificate: XXXX") ──
    for i, line in enumerate(lines):
        if line.strip().startswith('Certificate:'):
            if i + 1 < len(lines):
                candidate = lines[i + 1].strip()
                # Product name is the first non-field line after Certificate.
                if candidate and 'Batch' not in candidate and ':' not in candidate:
                    obs['product_name'] = candidate
            break

    # ── Key-value fields from product block ──
    field_patterns = {
        r'Batch\s*#:\s*(\S+)': 'batch_number',
        r'Sample\s+ID:\s*(\S+)': 'lab_id',
        r'Strain:\s*(.+?)(?:\s+Amount|\s{2,}|\n|$)': 'strain_name',
        r'Amount\s+Received:\s*(.+?)(?:\s{2,}|\n|$)': 'sample_size',
        r'Sample\s+Type:\s*(.+?)(?:\n|$)': 'product_type',
        r'Production\s+Method:\s*(.+?)(?:\s+Sample|\s{2,}|\n|$)': 'production_method',
        r'Harvest\s+Date:\s*(\d{2}/\d{2}/\d{4})': 'date_harvested',
        r'Manufacture\s+Date:\s*(\d{2}/\d{2}/\d{4})': 'date_manufactured',
        r'Sample\s+Collected:\s*(\d{2}/\d{2}/\d{4})': 'date_sampled',
        r'Received:\s*(\d{2}/\d{2}/\d{4})': 'date_received',
        r'Published:\s*(\d{2}/\d{2}/\d{4})': 'date_tested',
    }
    for pattern, field in field_patterns.items():
        m = re.search(pattern, front_text)
        if m:
            val = m.group(1).strip()
            if 'date' in field:
                val = _parse_date(val)
            obs[field] = val

    # ── Certificate ID ──
    m = re.search(r'Certificate:\s*(\S+)', front_text)
    if m:
        obs['coa_id'] = m.group(1)

    # ── Overall status ──
    # Check the "COMPLIANCE FOR RETAIL" section for Pass/Fail badges.
    compliance_section = front_text.split('COMPLIANCE FOR RETAIL')[-1] if 'COMPLIANCE FOR RETAIL' in front_text else front_text
    # Status is inferred from safety test results.
    if 'Fail' in compliance_section.split('Additional Analytes')[0] if 'Additional Analytes' in compliance_section else compliance_section:
        obs['status'] = 'fail'
    else:
        obs['status'] = 'pass'

    # ── Headline totals ──
    thc_match = re.search(r'([\d.]+)\s*%?\s*\n\s*Total THC', front_text)
    if thc_match:
        obs['total_thc'] = _parse_number(thc_match.group(1))
    cbd_match = re.search(r'([\d.]+)\s*%?\s*\n\s*Total CBD', front_text)
    if cbd_match:
        obs['total_cbd'] = _parse_number(cbd_match.group(1))
    # Handle "ND" for CBD/CBN/CBG.
    nd_cbd = re.search(r'ND\s*\n\s*Total CBD', front_text)
    if nd_cbd:
        obs['total_cbd'] = None
    tc_match = re.search(r'([\d.]+)\s*%?\s*\n\s*Total Cannabinoids', front_text)
    if tc_match:
        obs['total_cannabinoids'] = _parse_number(tc_match.group(1))

    # ── Lab accreditation ──
    acc_match = re.search(r'Accreditation\s*#:\s*(\d+)', front_text)
    if acc_match:
        obs['lab_accreditation'] = acc_match.group(1)

    return obs


# ── NY Metadata Parsing ───────────────────────────────────────────

def _parse_metadata_ny(front_text: str, front_page) -> Dict:
    """Parse metadata from an NY-format page 1.
    Uses same patterns as phytofarma.py modern format.
    """
    obs = {}

    # ── Producer from header block ──
    try:
        crop = front_page.within_bbox(
            (0, 0, front_page.width * 0.6, front_page.height * 0.15)
        )
        header_text = crop.extract_text() or ''
        header_lines = header_text.split('\n')
        if header_lines:
            obs['producer'] = header_lines[0].strip()
        for line in header_lines:
            if 'Address:' in line:
                obs['producer_address'] = line.split(':', 1)[-1].strip()
            elif 'License #:' in line:
                obs['producer_license_number'] = line.split(':', 1)[-1].strip()
    except Exception:
        pass

    # ── Product name ──
    try:
        crop_name = front_page.within_bbox(
            (0, front_page.height * 0.15, front_page.width * 0.65, front_page.height * 0.25)
        )
        name_text = crop_name.extract_text() or ''
        name_lines = name_text.split('\n')
        if name_lines:
            obs['product_name'] = name_lines[0].strip()
    except Exception:
        pass

    # ── Key-value fields ──
    field_patterns = {
        r'Lot\s*#:\s*(\S+)': 'batch_number',
        r'Lot\s+Size:\s*(\S+)': 'batch_size',
        r'Sample\s+ID:\s*(\S+)': 'lab_id',
        r'Sample\s+Type:\s*(.+?)(?:\s{2,}|$)': 'product_type',
        r'Regulatory\s+Category:\s*(.+?)(?:\s{2,}|$)': 'classification',
        r'Amount\s+Received:\s*(.+?)(?:\s{2,}|$)': 'sample_size',
        r'Sample\s+Collected:\s*(\d{2}/\d{2}/\d{4})': 'date_sampled',
        r'Received:\s*(\d{2}/\d{2}/\d{4})': 'date_received',
        r'Published:\s*(\d{2}/\d{2}/\d{4})': 'date_tested',
        r'Metrc\s+Package\s+ID:\s*(\S+)': 'traceability_id',
        r'Metrc\s+Tag:\s*(\S+)': 'metrc_tag',
    }
    for pattern, field in field_patterns.items():
        m = re.search(pattern, front_text)
        if m:
            val = m.group(1).strip()
            if 'date' in field:
                val = _parse_date(val)
            obs[field] = val

    # ── Certificate ID ──
    m = re.search(r'Certificate:\s*(\S+)', front_text)
    if m:
        obs['coa_id'] = m.group(1)

    # ── Overall status ──
    if re.search(r'Pass\s*\n\s*Sample Status', front_text):
        obs['status'] = 'pass'
    elif re.search(r'Fail\s*\n\s*Sample Status', front_text):
        obs['status'] = 'fail'
    else:
        obs['status'] = 'pass'

    # ── Headline totals ──
    # NY format: value% at end of one line, "Total THC" at end of next line.
    ny_lines = front_text.split('\n')
    for i, line in enumerate(ny_lines):
        if 'Total THC' in line and i > 0:
            prev = ny_lines[i - 1]
            pct = re.search(r'([\d.]+)\s*%\s*$', prev)
            if pct:
                obs['total_thc'] = _parse_number(pct.group(1))
        elif 'Total CBD' in line and i > 0:
            prev = ny_lines[i - 1]
            pct = re.search(r'([\d.]+)\s*%\s*$', prev)
            if pct:
                obs['total_cbd'] = _parse_number(pct.group(1))
        elif 'Total Cannabinoids' in line and i > 0:
            prev = ny_lines[i - 1]
            pct = re.search(r'([\d.]+)\s*%?\s*$', prev)
            if pct:
                obs['total_cannabinoids'] = _parse_number(pct.group(1))

    # ── Permit number ──
    m = re.search(r'Permit\s*#:\s*([\w\-]+)', front_text)
    if m:
        obs['lab_license_number'] = m.group(1)

    return obs


# ── AZ Results Parsing ─────────────────────────────────────────────

def _parse_az_cannabinoids(page_text: str) -> List[Dict]:
    """Parse cannabinoid results from an AZ cannabinoid page.
    Column layout: Analyte | LOD | LOQ | Dil. | Actual%(w/w) | mg/g | Qualifier
    """
    results = []
    lines = page_text.split('\n')
    in_table = False

    for line in lines:
        stripped = line.strip()

        # Detect table boundaries BEFORE skip check.
        if 'Analyte' in stripped and 'LOD' in stripped and 'LOQ' in stripped:
            in_table = True
            continue
        if 'Cannabinoid Totals' in stripped or 'Total THC =' in stripped:
            in_table = False
            continue
        if 'Ahmed Munshi' in stripped or 'Weston Owen' in stripped:
            in_table = False
            continue
        if stripped.startswith('ND = ') or stripped.startswith('ND ='):
            in_table = False
            continue

        if not in_table:
            continue
        if _should_skip_line(stripped):
            continue

        # Split at first standalone number to get analyte name.
        first_num = _find_first_number(stripped)
        if first_num >= len(stripped) or first_num < 2:
            continue

        name = stripped[:first_num].strip()
        values_str = stripped[first_num:].strip()
        values = values_str.split()

        key = _snake_case(name)
        if key == '_skip_' or not key:
            continue
        # Skip total/summary rows.
        if key.startswith('total_'):
            continue

        result = {
            'analysis': 'cannabinoids',
            'key': key,
            'name': name,
            'units': 'percent',
        }

        try:
            # AZ: LOD | LOQ | Dil | Actual%(w/w) | mg/g | Qualifier?
            if len(values) >= 5:
                result['lod'] = _parse_number(values[0])
                result['loq'] = _parse_number(values[1])
                # values[2] is Dil. (usually "1")
                result['value'] = _parse_number(values[3])
                result['mg_g'] = _parse_number(values[4])
            elif len(values) >= 4:
                result['lod'] = _parse_number(values[0])
                result['loq'] = _parse_number(values[1])
                result['value'] = _parse_number(values[3])
        except (IndexError, ValueError):
            continue

        results.append(result)

    return results


def _parse_az_two_column_table(
    page,
    page_text: str,
    analysis: str,
    units: str,
    has_action_limit: bool = False,
) -> List[Dict]:
    """Parse a two-column table from an AZ page.
    Used for terpenes, residual solvents, and pesticides.

    Terpenes: Analyte | LOD/LOQ(%) | Dil. | Results(%) | Qualifier
    Solvents/Pesticides: Analyte | LOD/LOQ(ppm) | Dil. | Action Limit(ppm) | Results(ppm) | Qualifier
    """
    results = []

    # Find Y boundary (stop before footer/chart).
    y_bound = page.height * 0.88
    words = page.extract_words()
    for i, w in enumerate(words):
        if w['text'] == 'Ahmed' or w['text'] == 'Weston':
            y_bound = min(y_bound, w['top'] - 10)
            break
        # Also stop at the terpene bar chart area.
        if w['text'] == 'Weight' and i + 1 < len(words) and words[i + 1]['text'] == '%:':
            y_bound = min(y_bound, w['top'] - 5)
            break

    # Find Y start (after "Analyte" header row).
    y_start = 0
    for w in words:
        if w['text'] == 'Analyte' and w['top'] > page.height * 0.15:
            y_start = w['bottom'] + 2
            break

    if y_start == 0:
        return results

    # Crop left and right halves.
    mid_x = page.width * 0.5
    for half_bbox in [
        (0, y_start, mid_x, y_bound),
        (mid_x, y_start, page.width, y_bound),
    ]:
        try:
            crop = page.within_bbox(half_bbox)
            crop_text = crop.extract_text() or ''
        except Exception:
            continue

        for line in crop_text.split('\n'):
            stripped = line.strip()
            if _should_skip_line(stripped):
                continue
            if stripped.upper().startswith('ANALYTE'):
                continue

            first_num = _find_first_number(stripped)
            if first_num >= len(stripped) or first_num < 2:
                continue

            name = stripped[:first_num].strip()
            values_str = stripped[first_num:].strip()

            key = _snake_case(name)
            if key == '_skip_' or not key:
                continue
            # Skip total rows.
            if key.startswith('total_') and key != 'total_aflatoxins':
                continue

            result = {
                'analysis': analysis,
                'key': key,
                'name': name,
                'units': units,
            }

            # Parse LOD/LOQ combined format "0.0009 / 0.0028" or separate values.
            lod_loq_match = re.match(r'([\d.]+)\s*/\s*([\d.]+)\s+(.*)', values_str)
            if lod_loq_match:
                result['lod'] = _parse_number(lod_loq_match.group(1))
                result['loq'] = _parse_number(lod_loq_match.group(2))
                remaining = lod_loq_match.group(3).strip().split()
            else:
                remaining = values_str.split()

            try:
                if has_action_limit:
                    # Dil | Action Limit | Results | Qualifier?
                    # Skip "1" (Dil), then limit, then result.
                    vals = [v for v in remaining if v not in ('Q3', 'M1', 'M2', 'I1', 'L1', 'V1', 'R1', 'R2', 'B1', 'B2')]
                    if len(vals) >= 3:
                        result['limit'] = _parse_number(vals[1])
                        result['value'] = _parse_number(vals[2])
                    elif len(vals) >= 2:
                        result['limit'] = _parse_number(vals[0])
                        result['value'] = _parse_number(vals[1])
                else:
                    # Dil | Results | Qualifier?
                    vals = [v for v in remaining if v not in ('Q3', 'M1', 'M2', 'I1', 'L1', 'V1', 'R1', 'R2', 'B1', 'B2')]
                    if len(vals) >= 2:
                        result['value'] = _parse_number(vals[1])
                    elif len(vals) >= 1:
                        result['value'] = _parse_number(vals[0])
            except (IndexError, ValueError):
                continue

            results.append(result)

    return results


def _parse_az_metals_mycotoxins(page_text: str) -> Tuple[List[Dict], List[Dict]]:
    """Parse heavy metals and mycotoxins from the combined AZ page.
    Heavy Metals: Analyte | LOD | LOQ | Dil. | Action Limit | Results | Qualifier
    Mycotoxins: Same structure but ppb units.
    """
    metals = []
    mycotoxins = []
    lines = page_text.split('\n')

    current_analysis = None
    in_table = False

    for line in lines:
        stripped = line.strip()

        # Detect section boundaries.
        if 'Heavy Metals' in stripped and 'ICP-MS' not in stripped:
            current_analysis = 'heavy_metals'
            in_table = False
            continue
        if 'Mycotoxin Analysis' in stripped or ('Mycotoxin' in stripped and 'LC-MS' not in stripped):
            current_analysis = 'mycotoxins'
            in_table = False
            continue

        if _should_skip_line(stripped):
            continue

        # Detect table start.
        if 'Analyte' in stripped and ('LOD' in stripped or 'LOQ' in stripped):
            in_table = True
            continue

        if not in_table or current_analysis is None:
            continue

        first_num = _find_first_number(stripped)
        if first_num >= len(stripped) or first_num < 2:
            continue

        name = stripped[:first_num].strip()
        values_str = stripped[first_num:].strip()
        values = values_str.split()

        key = _snake_case(name)
        if key == '_skip_' or not key:
            continue

        units = 'ppm' if current_analysis == 'heavy_metals' else 'ppb'
        result = {
            'analysis': current_analysis,
            'key': key,
            'name': name,
            'units': units,
        }

        try:
            # LOD | LOQ | Dil | Action Limit | Results | Qualifier?
            # Strip qualifier codes from values list.
            clean_vals = []
            for v in values:
                if re.match(r'^[A-Z]\d+', v) and not re.match(r'^[\d.]', v):
                    continue
                clean_vals.append(v)

            if len(clean_vals) >= 5:
                result['lod'] = _parse_number(clean_vals[0])
                result['loq'] = _parse_number(clean_vals[1])
                # clean_vals[2] is Dil
                result['limit'] = _parse_number(clean_vals[3])
                result['value'] = _parse_number(clean_vals[4])
            elif len(clean_vals) >= 4:
                result['lod'] = _parse_number(clean_vals[0])
                result['loq'] = _parse_number(clean_vals[1])
                result['limit'] = _parse_number(clean_vals[2])
                result['value'] = _parse_number(clean_vals[3])
        except (IndexError, ValueError):
            continue

        if current_analysis == 'heavy_metals':
            metals.append(result)
        else:
            mycotoxins.append(result)

    return metals, mycotoxins


def _parse_az_microbials(page_text: str) -> List[Dict]:
    """Parse microbial results from an AZ microbial page.
    Format: Analyte | Allowable Criteria | Actual Result | Pass/Fail | Qualifier
    Multiple sub-sections (E. coli, Salmonella, Aspergillus).
    """
    results = []
    lines = page_text.split('\n')

    for line in lines:
        stripped = line.strip()
        if _should_skip_line(stripped):
            continue
        if stripped.upper().startswith('ANALYTE'):
            continue

        # Check for known microbial analytes.
        upper = stripped.upper()
        analyte_name = None
        for known in ['E. COLI', 'SALMONELLA', 'ASPERGILLUS FLAVUS',
                       'ASPERGILLUS FUMIGATUS', 'ASPERGILLUS NIGER',
                       'ASPERGILLUS TERREUS']:
            if upper.startswith(known):
                analyte_name = known.title()
                if known == 'E. COLI':
                    analyte_name = 'E. coli'
                break

        if not analyte_name:
            continue

        key = _snake_case(analyte_name)
        result = {
            'analysis': 'microbials',
            'key': key,
            'name': analyte_name,
            'units': 'cfu/g',
        }

        # Determine pass/fail from the line text.
        if 'Pass' in stripped:
            result['status'] = 'pass'
        elif 'Fail' in stripped:
            result['status'] = 'fail'

        # Determine value from result text.
        if 'Not Detected' in stripped:
            result['value'] = None
        elif '< 100 CFU/g' in stripped or '<100 CFU/g' in stripped:
            result['value'] = 0.0
        elif '< 10 CFU/g' in stripped or '<10 CFU/g' in stripped:
            result['value'] = 0.0
        else:
            # Try to extract numeric value.
            num_match = re.search(r'(\d+)\s*CFU', stripped)
            if num_match:
                result['value'] = float(num_match.group(1))

        # Extract limit from allowable criteria.
        limit_match = re.search(r'<\s*(\d+)\s*CFU/g', stripped)
        if limit_match:
            result['limit'] = float(limit_match.group(1))
        elif 'Not Detected in One Gram' in stripped:
            result['limit'] = 0.0

        results.append(result)

    return results


def _parse_az_moisture_water(page_text: str) -> List[Dict]:
    """Parse moisture and/or water activity from standalone AZ pages."""
    results = []

    # Moisture: "Moisture: XX.XX %"
    m = re.search(r'Moisture:\s*([\d.]+)\s*%', page_text)
    if m:
        results.append({
            'analysis': 'moisture',
            'key': 'moisture_content',
            'name': 'Moisture',
            'units': 'percent',
            'value': _parse_number(m.group(1)),
        })

    # Water Activity: "Water Activity: X.XXXXaw aw" or "Water Activity: X.XXXXAW aw"
    m = re.search(r'Water\s+Activity:\s*([\d.]+)', page_text)
    if m:
        results.append({
            'analysis': 'water_activity',
            'key': 'water_activity',
            'name': 'Water Activity',
            'units': 'aw',
            'value': _parse_number(m.group(1)),
        })

    return results


def _parse_az_notes(page_text: str) -> Dict:
    """Parse notes page for additional metadata (extraction method, etc.)."""
    obs = {}

    # Extraction method.
    m = re.search(r'Method\s+of\s+Extraction:\s*(.+?)(?:\n|$)', page_text, re.IGNORECASE)
    if m:
        obs['extraction_method'] = m.group(1).strip()

    # Extraction method from "Extraction Method:" field.
    m = re.search(r'Extraction\s+Method:\s*(.+?)(?:\n|$)', page_text, re.IGNORECASE)
    if m:
        obs['extraction_method'] = m.group(1).strip()

    # Cultivated By.
    m = re.search(r'Cultivated\s+By:\s*(.+?)(?:\n|$)', page_text, re.IGNORECASE)
    if m:
        val = m.group(1).strip()
        if val:
            obs['cultivator'] = val

    # Distribution Chain.
    m = re.search(r'Distribution\s+Chain:\s*(.+?)(?:\n|$)', page_text, re.IGNORECASE)
    if m:
        val = m.group(1).strip()
        if val:
            obs['distributor'] = val

    # Harvest Date (sometimes on notes page for older COAs).
    m = re.search(r'Harvest\s+Date:\s*(\d{2}/\d{2}/\d{4})', page_text)
    if m:
        obs['date_harvested'] = _parse_date(m.group(1))

    # Manufacture Date.
    m = re.search(r'Manufacture\s+Date:\s*(\d{2}/\d{2}/\d{4})', page_text)
    if m:
        obs['date_manufactured'] = _parse_date(m.group(1))

    # Revision notes.
    revision_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})\s+Revision:', page_text)
    if revision_match:
        obs['revision_date'] = _parse_date(revision_match.group(1))

    return obs


# ── NY Results Parsing (delegates to phytofarma-style logic) ──────

def _parse_ny_analyte_table(
    text: str,
    analysis: str,
    units: str,
    col_spec: str = 'loq_value',
) -> List[Dict]:
    """Parse analyte results from NY-format text tables.
    Uses same logic as phytofarma.py's _parse_analyte_table_text.
    """
    results = []
    lines = text.split('\n')

    for line in lines:
        stripped = line.strip()
        if _should_skip_line(stripped):
            continue
        if stripped.upper().startswith('ANALYTE'):
            continue

        first_num = _find_first_number(stripped)
        if first_num >= len(stripped) or first_num < 2:
            continue

        name = re.sub(r'[†*]+$', '', stripped[:first_num]).strip()
        if not name or len(name) < 2:
            continue

        key = _snake_case(name)
        if key == '_skip_' or not key:
            continue
        if key.startswith('total_') and key not in (
            'total_aflatoxins', 'total_aerobic_bacteria',
            'total_yeast_and_mold',
        ):
            continue

        values = stripped[first_num:].strip().split()
        result = {
            'analysis': analysis,
            'key': key,
            'name': name,
            'units': units,
        }

        try:
            if col_spec == 'loq_value':
                if len(values) >= 2:
                    result['loq'] = _parse_number(values[0])
                    result['value'] = _parse_number(values[1])
                    if len(values) >= 3:
                        result['mg_per_serving'] = _parse_number(values[2])
            elif col_spec == 'loq_limit_value_status':
                if len(values) >= 4:
                    result['loq'] = _parse_number(values[0])
                    result['limit'] = _parse_number(values[1])
                    result['value'] = _parse_number(values[2])
                    if values[3] in ('PASS', 'FAIL', 'Pass', 'Fail'):
                        result['status'] = values[3].lower()
        except (IndexError, ValueError):
            continue

        results.append(result)

    return results


def _extract_section_text(
    page_text: str,
    section_keyword: str,
) -> str:
    """Extract text for a specific section from a page."""
    lines = page_text.split('\n')
    start = None
    for i, line in enumerate(lines):
        if section_keyword in line:
            for j in range(max(0, i - 2), min(len(lines), i + 5)):
                if 'Analyte' in lines[j]:
                    start = j + 1
                    break
            if start is None:
                start = i + 1
            break

    if start is None:
        return ''

    end = len(lines)
    stop_markers = [
        'Certificate:', 'Ahmed Munshi', 'Weston Owen',
        'Technical Laboratory', 'Laboratory Manager',
        'Page ', 'The product associated',
    ]
    for i in range(start, len(lines)):
        if any(m in lines[i] for m in stop_markers):
            end = i
            break

    return '\n'.join(lines[start:end])


# ── Main Parsing Function ──────────────────────────────────────────

def parse_smithers_pdf(
    parser: Any = None,
    doc: str = '',
    **kwargs,
) -> Dict:
    """Parse a Smithers CTS COA PDF.

    Opens the PDF with pdfplumber, detects the location/format,
    extracts metadata from page 1, then extracts results from
    all pages.
    """
    pdf_path = doc if isinstance(doc, str) and doc else ''
    if isinstance(parser, str) and not pdf_path:
        pdf_path = parser
        parser = None
    if not pdf_path:
        raise ValueError('No PDF file path provided.')

    obs = {}
    all_results = []
    analyses = []
    methods = []

    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            raise ValueError(f'PDF has no pages: {pdf_path}')

        # ── Phase 1: Extract page 1 text ──
        try:
            front_text = pdf.pages[0].extract_text() or ''
            front_text = front_text.replace('\x00', '')
        except Exception:
            return {}

        # ── Phase 2: Detect location and format ──
        location = _detect_location(front_text)
        fmt = _detect_format(front_text, location)
        loc_info = SMITHERS_LOCATIONS.get(location, SMITHERS_LOCATIONS['az'])

        # ── Phase 3: Parse metadata ──
        if fmt == 'az':
            obs = _parse_metadata_az(front_text, pdf.pages[0])
        else:
            obs = _parse_metadata_ny(front_text, pdf.pages[0])

        # ── Phase 4: Parse all pages for results ──
        for page_idx in range(len(pdf.pages)):
            try:
                page = pdf.pages[page_idx]
                page_text = page.extract_text() or ''
                page_text = page_text.replace('\x00', '')
            except Exception:
                continue

            # Skip Qualifier Legend and Distribution Chain pages.
            if 'Qualifier Legend' in page_text:
                continue
            if 'Intended Point of Sale' in page_text:
                continue
            if 'Starting Concentrate Information' in page_text:
                continue
            if 'Starting Flower Information' in page_text:
                continue
            if 'Distribution Chain:' in page_text and 'Product Form' in page_text:
                continue

            upper_text = page_text.upper()

            # ── Cannabinoids ──
            if ('Cannabinoid Profile' in page_text or
                'Average Cannabinoid Profile' in page_text) and 'Analyte' in page_text:
                if 'cannabinoids' not in analyses:
                    if fmt == 'az':
                        cann_results = _parse_az_cannabinoids(page_text)
                    else:
                        section = _extract_section_text(page_text, 'Cannabinoid')
                        cann_results = _parse_ny_analyte_table(
                            section, 'cannabinoids', 'percent', 'loq_value'
                        )
                    if cann_results:
                        all_results.extend(cann_results)
                        analyses.append('cannabinoids')

                    # Extract totals from cannabinoid page if not found on page 1.
                    for line in page_text.split('\n'):
                        if line.strip().startswith('Total THC') and 'total_thc' not in obs:
                            vals = line.split()
                            for v in vals:
                                n = _parse_number(v)
                                if n is not None and n > 0:
                                    obs['total_thc'] = n
                                    break
                        elif line.strip().startswith('Total CBD') and 'total_cbd' not in obs:
                            vals = line.split()
                            for v in vals:
                                n = _parse_number(v)
                                if n is not None and n > 0:
                                    obs['total_cbd'] = n
                                    break
                        elif line.strip().startswith('Total Cannabinoids') and 'total_cannabinoids' not in obs:
                            vals = line.split()
                            for v in vals:
                                n = _parse_number(v)
                                if n is not None and n > 0:
                                    obs['total_cannabinoids'] = n
                                    break

                    # Extract SOP/method.
                    sop_match = re.search(r'SOP:\s*([\w.\-]+)', page_text)
                    if sop_match:
                        methods.append(sop_match.group(1))

            # ── Terpenes ──
            if 'Terpene Total' in page_text and 'Analyte' in page_text:
                if 'terpenes' not in analyses:
                    # Total terpenes from header.
                    terp_total_match = re.search(
                        r'Tested\s*\(([\d.]+)%?\)', page_text
                    )
                    if terp_total_match:
                        obs['total_terpenes'] = _parse_number(terp_total_match.group(1))
                    # Fallback.
                    if 'total_terpenes' not in obs:
                        terp_total_match2 = re.search(
                            r'Total\s+Terpenes\s+([\d.]+)', page_text
                        )
                        if terp_total_match2:
                            obs['total_terpenes'] = _parse_number(terp_total_match2.group(1))

                    if fmt == 'az':
                        terp_results = _parse_az_two_column_table(
                            page, page_text, 'terpenes', 'percent',
                            has_action_limit=False
                        )
                    else:
                        # NY: two-column terpenes.
                        terp_results = _parse_az_two_column_table(
                            page, page_text, 'terpenes', 'percent',
                            has_action_limit=False
                        )

                    if terp_results:
                        all_results.extend(terp_results)
                        analyses.append('terpenes')

                    sop_match = re.search(r'SOP:\s*([\w.\-]+)', page_text)
                    if sop_match:
                        methods.append(sop_match.group(1))

            # ── Microbials ──
            if 'Microbial Analysis' in page_text or 'Microbial Impurities' in page_text:
                if 'microbials' not in analyses:
                    if fmt == 'az':
                        micro_results = _parse_az_microbials(page_text)
                    else:
                        section = _extract_section_text(page_text, 'Microbial')
                        micro_results = _parse_ny_analyte_table(
                            section, 'microbials', 'cfu/g', 'loq_limit_value_status'
                        )
                    if micro_results:
                        all_results.extend(micro_results)
                        analyses.append('microbials')

            # ── Residual Solvents ──
            if 'Residual Solvents' in page_text and 'Analyte' in page_text:
                if 'residual_solvents' not in analyses:
                    if fmt == 'az':
                        solv_results = _parse_az_two_column_table(
                            page, page_text, 'residual_solvents', 'ppm',
                            has_action_limit=True
                        )
                    else:
                        section = _extract_section_text(page_text, 'Residual Solvents')
                        solv_results = _parse_ny_analyte_table(
                            section, 'residual_solvents', 'ppm', 'loq_limit_value_status'
                        )
                    if solv_results:
                        all_results.extend(solv_results)
                        analyses.append('residual_solvents')

            # ── Heavy Metals + Mycotoxins (AZ combined page) ──
            if ('Heavy Metals' in page_text or 'Trace Metals' in page_text) and 'Analyte' in page_text:
                if fmt == 'az':
                    if 'heavy_metals' not in analyses or 'mycotoxins' not in analyses:
                        metals, mycotoxins = _parse_az_metals_mycotoxins(page_text)
                        if metals and 'heavy_metals' not in analyses:
                            all_results.extend(metals)
                            analyses.append('heavy_metals')
                        if mycotoxins and 'mycotoxins' not in analyses:
                            all_results.extend(mycotoxins)
                            analyses.append('mycotoxins')
                else:
                    # NY: Trace Metals on its own page.
                    if 'heavy_metals' not in analyses:
                        section = _extract_section_text(page_text, 'Trace Metals')
                        if not section:
                            section = _extract_section_text(page_text, 'Heavy Metals')
                        metal_results = _parse_ny_analyte_table(
                            section, 'heavy_metals', 'ug/g', 'loq_limit_value_status'
                        )
                        if metal_results:
                            all_results.extend(metal_results)
                            analyses.append('heavy_metals')

            # ── Mycotoxins (standalone page, NY or AZ w/o metals on same page) ──
            if 'Mycotoxin Analysis' in page_text and 'Heavy Metals' not in page_text and 'Analyte' in page_text:
                if 'mycotoxins' not in analyses:
                    if fmt == 'ny':
                        section = _extract_section_text(page_text, 'Mycotoxin')
                        myco_results = _parse_ny_analyte_table(
                            section, 'mycotoxins', 'ug/g', 'loq_limit_value_status'
                        )
                        if myco_results:
                            all_results.extend(myco_results)
                            analyses.append('mycotoxins')

            # ── Pesticides ──
            if ('Pesticides' in page_text or 'Pesticide' in page_text) and 'Analyte' in page_text:
                if fmt == 'az':
                    if 'pesticides' not in analyses:
                        analyses.append('pesticides')
                    pest_results = _parse_az_two_column_table(
                        page, page_text, 'pesticides', 'ppm',
                        has_action_limit=True
                    )
                    if pest_results:
                        all_results.extend(pest_results)
                else:
                    # NY: Pesticides LC and GC on separate pages.
                    if 'pesticides' not in analyses:
                        analyses.append('pesticides')
                    for half_bbox in [
                        (0, 0, page.width * 0.5, page.height * 0.9),
                        (page.width * 0.5, 0, page.width, page.height * 0.9),
                    ]:
                        try:
                            crop = page.within_bbox(half_bbox)
                            crop_text = crop.extract_text() or ''
                            section = _extract_section_text(crop_text, 'Analyte')
                            if section:
                                pest_results = _parse_ny_analyte_table(
                                    section, 'pesticides', 'ppm', 'loq_limit_value_status'
                                )
                                all_results.extend(pest_results)
                        except Exception:
                            continue

            # ── Moisture / Water Activity ──
            if 'Moisture Analysis' in page_text and page_idx > 0:
                if 'moisture' not in analyses:
                    mw_results = _parse_az_moisture_water(page_text)
                    for r in mw_results:
                        if r['analysis'] == 'moisture':
                            all_results.append(r)
                            analyses.append('moisture')
                        elif r['analysis'] == 'water_activity':
                            all_results.append(r)
                            if 'water_activity' not in analyses:
                                analyses.append('water_activity')

            # Water Activity on same page or standalone.
            if 'Water Activity' in page_text and 'water_activity' not in analyses and page_idx > 0:
                wa_results = _parse_az_moisture_water(page_text)
                for r in wa_results:
                    if r['analysis'] == 'water_activity':
                        all_results.append(r)
                        analyses.append('water_activity')

            # ── Notes page ──
            if 'Notes:' in page_text and page_idx > 0:
                notes_data = _parse_az_notes(page_text)
                for k, v in notes_data.items():
                    if k not in obs or not obs[k]:
                        obs[k] = v

            # ── Extract SOPs from any page ──
            for sop_match in re.finditer(r'SOP:\s*([\w.\-]+)', page_text):
                methods.append(sop_match.group(1))

    # ── Phase 5: Build final output ──
    obs = {**SMITHERS, **loc_info, **obs}

    # Ensure required fields have defaults.
    obs.setdefault('product_name', '')
    obs.setdefault('status', 'pass')
    obs.setdefault('date_tested', '')

    # Set sample_id from lab_id.
    obs.setdefault('sample_id', obs.get('lab_id', ''))

    # Serialize results and analyses.
    analyses = sorted(set(analyses))
    methods = sorted(set(m for m in methods if m))
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
        obs.get('producer', '') +
        obs.get('date_tested', '')
    )
    if not obs.get('sample_id'):
        obs['sample_id'] = hashlib.sha256(id_input.encode()).hexdigest()[:16]

    obs['coa_pdf'] = pdf_path.replace('\\', '/').split('/')[-1]

    return obs


# ── Entry Point (LAB_REGISTRY compatible) ──────────────────────────

def parse_smithers_coa(
    parser: Any = None,
    doc: Any = '',
    **kwargs,
) -> Dict:
    """Parse a Smithers CTS COA PDF.

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

    return parse_smithers_pdf(parser, doc, **kwargs)


def is_smithers(pdf_path: str) -> bool:
    """Quick check if a PDF is a Smithers CTS COA."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return False
            text = (pdf.pages[0].extract_text() or '').lower()
            return (
                'smithers' in text
                and ('certificate of analysis' in text or 'compliance for retail' in text)
            )
    except Exception:
        return False


# ── CLI Tests ──────────────────────────────────────────────────────

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
        print('Usage: python smithers.py <pdf_file> [pdf_file2 ...]')
        sys.exit(1)

    success = 0
    fail = 0
    for pdf_file in test_files:
        pdf_path = pdf_file if os.path.isabs(pdf_file) else os.path.join(os.getcwd(), pdf_file)
        if not os.path.exists(pdf_path):
            print(f'Not found: {pdf_path}')
            continue
        try:
            data = parse_smithers_coa(None, pdf_path)
            results = json.loads(data.get('results', '[]'))
            analyses = json.loads(data.get('analyses', '[]'))
            print(f'\n{"="*60}')
            print(f'OK {os.path.basename(pdf_file)}')
            print(f'  Product:  {data.get("product_name", "?")}')
            print(f'  Type:     {data.get("product_type", "?")}')
            print(f'  Strain:   {data.get("strain_name", "?")}')
            print(f'  Producer: {data.get("producer", "?")}')
            print(f'  Date:     {data.get("date_tested", "?")}')
            print(f'  THC:      {data.get("total_thc", "?")}%')
            print(f'  CBD:      {data.get("total_cbd", "?")}%')
            print(f'  Terpenes: {data.get("total_terpenes", "?")}%')
            print(f'  Status:   {data.get("status", "?")}')
            print(f'  Sample:   {data.get("sample_id", "?")}')
            print(f'  Batch:    {data.get("batch_number", "?")}')
            print(f'  Lab:      {data.get("lab", "?")}')
            print(f'  Analyses: {analyses}')
            print(f'  Results:  {len(results)} analytes')
            # Per-analysis counts.
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
