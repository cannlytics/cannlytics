"""
Parse TerpLife Labs / TL Laboratories COA — COA Doc Hybrid Algorithm (Offline-First)
Copyright (c) 2023-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/20/2023
Updated: 3/8/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse TerpLife Labs and TL Laboratories COA PDFs directly from the
    PDF text — no network access required. This is the modernized
    offline-first engine that extracts all data from the PDF itself
    using pdfplumber text extraction, bbox cropping, and regex-based
    field parsing.

    TerpLife Labs is a major Florida cannabis testing laboratory
    operating from Tampa, FL (CMTL-00010). In late 2025, they
    rebranded some COAs under "TL Laboratories" with an expanded
    analyte panel (d10-THC, HHC, THCp) and updated layout.

    Identification:
        TerpLife COAs contain 'TerpLife Labs' or 'TL Laboratories'
        or 'TL LABORATORIES' in the page header, and/or
        'terplifelabs.com' in the footer.

    Format notes:
        * Two brands: "TerpLife Labs" (2022-2025) and
          "TL Laboratories" (2025+), same address/director
        * Single-page COAs: cannabinoids + terpenes summary only
        * Multi-page COAs (2-5 pages): full compliance panel
        * Page 1: Header metadata, Safety Summary grid,
          Potency Summary, two-column Terpenes (left) +
          Cannabinoids (right) layout
        * Page 2+: Pesticides (two-column), Mycotoxins,
          Microbials, Heavy Metals, Foreign Materials,
          Water Activity, Moisture Content, Residual Solvents,
          extended Terpenes, Cannabinoids (as received)
        * Flower: Reports "dry weight" and "as received" values
        * Edibles/Derivatives: mg/Serving and mg/Unit columns
        * Safety Summary grid: PASS/NOT TESTED/TESTED per analysis

Data Points:

    ✓ product_name, product_type, strain_name
    ✓ date_tested, date_received, date_collected, date_produced
    ✓ batch_number, batch_size, sample_weight, product_size
    ✓ lab_id, sample_id, external_id, traceability_id
    ✓ lab, lab_license_number, lab_address, lab_city, lab_state,
      lab_zipcode, lab_phone, lab_website
    ✓ producer, producer_license_number, producer_address,
      producer_street, producer_city, producer_state, producer_zipcode
    ✓ distributor
    ✓ total_thc, total_cbd, total_cannabinoids, total_terpenes
    ✓ status (overall compliance pass/fail)
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

# External imports (only pdfplumber per dependency policy):
import pdfplumber


# ── TerpLife Labs Constants ────────────────────────────────────────

TERPLIFE_LABS = {
    'coa_algorithm': 'terplife.py',
    'coa_algorithm_entry_point': 'parse_terplife_coa',
    'lims': 'TerpLife Labs',
    'lab': 'TerpLife Labs',
    'lab_license_number': 'CMTL-00010',
    'lab_image_url': 'https://www.terplifelabs.com/wp-content/uploads/2022/03/website-logo.png',
    'lab_address': '10350 Fisher Ave, Tampa, FL 33619',
    'lab_street': '10350 Fisher Ave',
    'lab_city': 'Tampa',
    'lab_county': 'Hillsborough',
    'lab_state': 'FL',
    'lab_zipcode': '33619',
    'lab_phone': '813-726-3103',
    'lab_email': 'info@terplifelabs.com',
    'lab_website': 'https://www.terplifelabs.com',
    'lab_latitude': 27.959174,
    'lab_longitude': -82.3278,
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
    'foreign material': 'foreign_matter',
    'water activity': 'water_activity',
    'moisture content': 'moisture',
}

# Standard units per analysis type.
STANDARD_UNITS = {
    'cannabinoids': 'percent',
    'terpenes': 'percent',
    'pesticides': 'ppb',
    'heavy_metals': 'ppb',
    'microbials': 'cfu/g',
    'mycotoxins': 'ppb',
    'residual_solvents': 'ppm',
    'foreign_matter': 'percent',
    'water_activity': 'aw',
    'moisture': 'percent',
}

# Metadata field mappings from COA text labels to output keys.
METADATA_FIELDS = {
    'Seed to Sale': 'traceability_id',
    'Retail Batch#': 'batch_number',
    'Client Lic#': 'producer_license_number',
    'Retail Batch Total Wt/Vol': 'batch_size',
    'Retail Batch Total Units': 'batch_units',
    'Cultivar': 'strain_name',
    'Cultivation Facility': 'producer',
    'Processing Facility': 'distributor',
    'Total Units Received': 'sample_units',
    'Total Sample Received': 'sample_weight',
    'Retail Batch Date': 'date_produced',
    'Date Sampled': 'date_collected',
    'Date Received': 'date_received',
    'Date Reported': 'date_tested',
    'Matrix': 'product_type',
    'Unit Weight': 'product_size',
    'Sampling SOP': 'sampling_method',
}

# Safety Summary grid analysis labels.
SAFETY_ANALYSES = {
    'Foreign Materials': 'foreign_matter',
    'Heavy Metals': 'heavy_metals',
    'Microbials': 'microbials',
    'Homogeneity': 'homogeneity',
    'Label Claim': 'label_claim',
    'Moisture Content': 'moisture',
    'Mycotoxins': 'mycotoxins',
    'Pesticides': 'pesticides',
    'Residual Solvents': 'residual_solvents',
    'TCL': 'total_contaminant_load',
    'Terpenes': 'terpenes',
    'Water Activity': 'water_activity',
    'Vitamins Supplements': 'vitamins_supplements',
}

# ── ANALYTE_KEY_MAP ────────────────────────────────────────────────
# Maps display names (uppercase) to standardized snake_case keys.
ANALYTE_KEY_MAP = {
    # Cannabinoids (TerpLife display names)
    'CANNABICHROMENE (CBC)': 'cbc',
    'CANNABIDIOL (CBD)': 'cbd',
    'CANNABIDIOLIC ACID (CBDA)': 'cbda',
    'CANNABIDIVARIN (CBDV)': 'cbdv',
    'CANNABIGEROL (CBG)': 'cbg',
    'CANNABIGEROLIC ACID (CBGA)': 'cbga',
    'CANNABINOL (CBN)': 'cbn',
    'D8 - TETRAHYDROCANNABINOID (D8-THC)': 'delta_8_thc',
    'D9 - TETRAHYDROCANNABINOID (D9-THC)': 'delta_9_thc',
    'D9 - TETRAHYDROCANNABINOLIC ACID (THCA)': 'thca',
    'TETRAHYDROCANNABIVARIN (THCV)': 'thcv',
    'D10 - TETRAHYDROCANNABINOID (D10-THC)': 'delta_10_thc',
    'HEXAHYDROCANNABINOL (HHC)': 'hhc',
    'THCP TOT': 'thcp',
    # Short cannabinoid names (sometimes used in summaries)
    'TOTAL THC': 'total_thc',
    'TOTAL CBD': 'total_cbd',
    'TOTAL CANNABINOIDS': 'total_cannabinoids',
    # Terpenes
    '3-CARENE (+)-': 'delta_3_carene',
    '3-CARENE, (+)-': 'delta_3_carene',
    'ALPHA BISABOLOL, L': 'alpha_bisabolol',
    'ALPHA-BISABOLOL': 'alpha_bisabolol',
    'ALPHA-CEDRENE': 'alpha_cedrene',
    'ALPHA-FENCHYL ALCOHOL, (+)-': 'fenchyl_alcohol',
    'ALPHA-HUMULENE': 'alpha_humulene',
    'ALPHA-PHELLANDRENE': 'alpha_phellandrene',
    'ALPHA-PINENE': 'alpha_pinene',
    'ALPHA-TERPINENE': 'alpha_terpinene',
    'ALPHA-TERPINEOL': 'alpha_terpineol',
    'BETA-MYRCENE': 'beta_myrcene',
    'BETA-OCIMENE': 'beta_ocimene',
    'BETA-PINENE': 'beta_pinene',
    'BORNEOL': 'borneol',
    'CAMPHENE': 'camphene',
    'CAMPHOR': 'camphor',
    'CARYOPHYLLENE OXIDE': 'caryophyllene_oxide',
    'CEDROL': 'cedrol',
    'D-LIMONENE': 'limonene',
    'E-CARYOPHYLLENE': 'beta_caryophyllene',
    'E-NEROLIDOL': 'trans_nerolidol',
    'EUCALYPTOL': 'eucalyptol',
    'FARNESENE': 'farnesene',
    'FENCHONE': 'fenchone',
    'GAMMA-TERPINENE': 'gamma_terpinene',
    'GERANIOL': 'geraniol',
    'GERANYL ACETATE': 'geranyl_acetate',
    'GUAIOL': 'guaiol',
    'ISOBORNEOL': 'isoborneol',
    'ISOPULEGOL': 'isopulegol',
    'LINALOOL': 'linalool',
    'MENTHOL': 'menthol',
    'NEROL': 'nerol',
    'P-CYMENE': 'p_cymene',
    'PULEGONE': 'pulegone',
    'SABINENE': 'sabinene',
    'SABINENE HYDRATE': 'sabinene_hydrate',
    'TERPINOLENE': 'terpinolene',
    'VALENCENE': 'valencene',
    'Z-NEROLIDOL': 'cis_nerolidol',
    # Heavy metals
    'ARSENIC': 'arsenic',
    'CADMIUM': 'cadmium',
    'LEAD': 'lead',
    'MERCURY': 'mercury',
    # Mycotoxins
    'AFLATOXIN B1': 'aflatoxin_b1',
    'AFLATOXIN B2': 'aflatoxin_b2',
    'AFLATOXIN G1': 'aflatoxin_g1',
    'AFLATOXIN G2': 'aflatoxin_g2',
    'OCHRATOXIN A': 'ochratoxin_a',
    # Microbials
    'ASPERGILLUS FLAVUS': 'aspergillus_flavus',
    'ASPERGILLUS FUMIGATUS': 'aspergillus_fumigatus',
    'ASPERGILLUS NIGER': 'aspergillus_niger',
    'ASPERGILLUS TERREUS': 'aspergillus_terreus',
    'SALMONELLA': 'salmonella',
    'SHIGA TOXIN PRODUCING E. COLI': 'e_coli',
    'SHIGA TOXIN PRODUCING E. COLI': 'e_coli',
    'TOTAL YEAST AND MOLD': 'total_yeast_and_mold',
    # Foreign materials
    'FOREIGN MATERIAL': 'foreign_matter',
    'FECES': 'feces',
    # Water activity
    'WATER ACTIVITY': 'water_activity',
    # Moisture
    'PERCENT MOISTURE': 'moisture_content',
}

# Non-analyte keywords to skip when parsing result lines.
SKIP_KEYWORDS = {
    'TOTAL THC', 'TOTAL CBD', 'TOTAL CANNABINOIDS', 'TOTAL',
    'TOTAL TERPENES', 'TOTAL CONTAMINANT LOAD',
    'HEAVY METALS & PESTICIDES',
}

# Residual solvent analyte names (for section identification).
RESIDUAL_SOLVENTS = {
    '1,1-Dichloroethene', '1,2-Dichloroethane', 'Acetone',
    'Acetonitrile', 'Benzene', 'Butane', 'Chloroform', 'Ethanol',
    'Ethyl acetate', 'Ethyl ether', 'Ethylene oxide', 'Heptane',
    'Hexane', 'Isopropyl alcohol', 'Methanol', 'Methylene chloride',
    'Pentane', 'Propane', 'Toluene', 'Xylenes, total',
    'Trichloroethylene',
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
    Returns None for ND/Not Detected/N/A/Absent, float otherwise.
    """
    if text is None:
        return None
    t = text.strip().replace(',', '')
    if not t or t in ('ND', 'N/A', 'NT', ''):
        return None
    if t.startswith('Not ') or t.startswith('Absent') or t.startswith('<'):
        return None
    # Match numeric values (including negative and scientific notation).
    m = re.match(r'^-?[\d.]+(?:[eE][+-]?\d+)?', t)
    if m:
        try:
            return float(m.group())
        except ValueError:
            return None
    return None


def _parse_date(text: str) -> str:
    """Parse a date string into ISO format (YYYY-MM-DD).
    Handles: MM/DD/YYYY, MM/DD/YY, and various formats.
    Returns empty string on failure.
    """
    if not text or not text.strip():
        return ''
    t = text.strip()
    for fmt in ('%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%b %d, %Y', '%B %d, %Y'):
        try:
            return datetime.strptime(t, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return t


def _find_first_number(line: str) -> int:
    """Find the position of the first numeric token in a line.

    Handles digit-prefixed analyte names (d8-THC, 3-Carene, 1,1-Dichloroethene)
    by requiring whitespace before the number.

    Strategy: Find the first digit that is preceded by whitespace and
    followed by a digit or period, which indicates a numeric column value.
    """
    # Look for whitespace + digit pattern that indicates start of numeric data.
    m = re.search(r'\s(\d[\d.]*)', line)
    if m:
        return m.start(1)
    return len(line)


def _detect_format(front_text: str) -> str:
    """Detect the COA format variant.

    Returns:
        'tl_labs' for TL Laboratories (2025+ rebranded)
        'terplife' for classic TerpLife Labs
    """
    if 'TL LABORATORIES' in front_text.upper() or 'TL Laboratories' in front_text:
        return 'tl_labs'
    return 'terplife'


def _clean_text(text: str) -> str:
    """Clean extracted text by removing QR code artifacts and extra whitespace."""
    # Remove QR code block characters.
    text = re.sub(r'[█▀▄▌▐░▒▓■□▪▫]', '', text)
    # Collapse multiple newlines.
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _extract_section_between(text: str, start: str, end: str) -> str:
    """Extract text between two markers (case-sensitive)."""
    idx_start = text.find(start)
    if idx_start < 0:
        return ''
    idx_start += len(start)
    idx_end = text.find(end, idx_start)
    if idx_end < 0:
        return text[idx_start:]
    return text[idx_start:idx_end]


# ── Metadata Parsing ──────────────────────────────────────────────

def _parse_metadata(front_text: str, page: Any) -> Dict:
    """Extract all metadata fields from the front page."""
    obs = {}
    lines = [x.strip() for x in front_text.split('\n') if x.strip()]

    # ── Lab ID (Sample ID prefix like T5B0157, T408577, etc.) ──
    for line in lines:
        m = re.match(r'^(T[A-Z0-9]{4,10})\b', line)
        if m:
            obs['lab_id'] = m.group(1)
            break
    # Also check for "Sample ID:" pattern.
    m = re.search(r'Sample ID:\s*(T[\w-]+)', front_text)
    if m:
        obs['lab_id'] = m.group(1).split()[0]

    # ── CCB ID / External ID ──
    m = re.search(r'CCB ID:(.+?)(?:Matrix|$)', front_text, re.DOTALL)
    if m:
        obs['external_id'] = m.group(1).strip().split('\n')[0].strip()

    # ── Product name ──
    # Product name appears before "Total Sample Received" on front page
    # or after "Compliance for Retail:" line.
    for line in lines:
        if 'Certificate of Analysis' in line:
            continue
        if 'Total Sample Received' in line:
            name = line.split('Total Sample Received')[0].strip()
            if name:
                obs['product_name'] = name
            break

    # Also try: the line immediately before "Certificate of Analysis"
    # in newer format, or the line after "Compliance for Retail: PASS".
    if not obs.get('product_name'):
        for i, line in enumerate(lines):
            if 'Compliance for Retail' in line and i + 1 < len(lines):
                candidate = lines[i + 1].strip()
                if candidate and 'Sample' not in candidate and 'Total' not in candidate:
                    obs['product_name'] = candidate
                    break

    # ── Compliance status ──
    m = re.search(r'Compliance for Retail:\s*(PASS|FAIL)', front_text, re.IGNORECASE)
    if m:
        obs['status'] = m.group(1).lower()

    # ── Key-value metadata fields ──
    for label, key in METADATA_FIELDS.items():
        # Search for "Label : Value" or "Label: Value" patterns.
        pattern = re.escape(label) + r'\s*:?\s*(.+?)(?:\n|$)'
        m = re.search(pattern, front_text)
        if m:
            val = m.group(1).strip()
            # Clean trailing metadata labels from the value.
            for other_label in METADATA_FIELDS:
                if other_label in val and other_label != label:
                    val = val.split(other_label)[0].strip()
            if val:
                obs[key] = val

    # ── Producer address (top-left corner) ──
    try:
        corner = (0, 0, page.width * 0.4, page.height * 0.2)
        corner_crop = page.crop(corner)
        corner_text = corner_crop.extract_text() or ''

        # Producer/client name: first meaningful line in corner after lab header.
        producer_lines = [x.strip() for x in corner_text.split('\n') if x.strip()]
        for pl in producer_lines:
            if any(skip in pl for skip in [
                'TerpLife', 'TL LABORATORIES', 'TL Laboratories',
                'Certificate', 'Lab State', 'CMTL',
            ]):
                continue
            if pl and not pl.startswith('(') and len(pl) > 2:
                # This is typically the client/company name (Sanctuary, MÜV, Curaleaf, etc.)
                if 'Client Lic' not in pl and not re.match(r'^\d', pl):
                    # Skip cropping artifacts (very short partial words).
                    if len(pl) <= 3 and not pl[0].isupper():
                        continue
                    obs.setdefault('producer', pl)
                    break

        # Extract address after "Client Lic#:" line.
        if 'Client Lic#' in corner_text:
            addr_block = corner_text.split('Client Lic#')[-1]
            addr_lines = [x.strip() for x in addr_block.split('\n') if x.strip()]
            if len(addr_lines) >= 2:
                # Find the address line (starts with a digit).
                for j, al in enumerate(addr_lines):
                    if re.match(r'^\d', al):
                        street = al.strip()
                        obs['producer_street'] = street
                        # Next line might be city, state zip or phone.
                        if j + 1 < len(addr_lines):
                            city_line = addr_lines[j + 1].strip()
                            if not re.match(r'^\(\d{3}\)', city_line):
                                obs['producer_address'] = f'{street}, {city_line}'
                                csz = re.match(
                                    r'(.+?),?\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)',
                                    city_line
                                )
                                if csz:
                                    obs['producer_city'] = csz.group(1).strip().rstrip(',')
                                    obs['producer_state'] = csz.group(2)
                                    obs['producer_zipcode'] = csz.group(3)
                            else:
                                obs['producer_address'] = street
                        break
    except Exception as e:
        logger.debug(f'Producer address extraction failed: {e}')

    # ── Parse dates to ISO format ──
    for key in ['date_tested', 'date_received', 'date_collected', 'date_produced']:
        if key in obs:
            obs[key] = _parse_date(obs[key])

    # ── Serving size (edibles) ──
    m = re.search(r'Serving Size:\s*([\d.]+)\s*g', front_text)
    if m:
        obs['serving_size'] = m.group(1)

    return obs


def _parse_safety_summary(front_text: str) -> Dict[str, str]:
    """Parse the Safety Summary grid to determine which analyses
    were performed and their pass/fail status.

    Returns dict mapping analysis name to status (pass/fail/tested/not_tested).
    """
    safety = {}
    # The Safety Summary is a grid with analysis labels and PASS/FAIL/NOT TESTED/TESTED.
    for label, analysis in SAFETY_ANALYSES.items():
        # Look for the label followed by PASS, FAIL, NOT TESTED, or TESTED.
        pattern = re.escape(label) + r'\s*(PASS|FAIL|NOT TESTED|TESTED)'
        m = re.search(pattern, front_text, re.IGNORECASE)
        if m:
            safety[analysis] = m.group(1).strip().lower().replace(' ', '_')
    return safety


# ── Potency Summary Parsing ───────────────────────────────────────

def _parse_potency_summary(front_text: str) -> Dict:
    """Extract total THC, CBD, and cannabinoids from the Potency Summary.

    TerpLife uses a "value-above-label" pattern:
        Line N:   46.2%  42.6%  92.2%
        Line N+1: Total THC  Total CBD  Total Cannabinoids

    Flower COAs also show dry weight / as received pairs:
        25.5% 22.8%  (dry weight, as received)
    """
    obs = {}

    # Find the Potency Summary section.
    summary = ''
    if 'Potency Summary' in front_text:
        if 'Terpenes Summary' in front_text:
            summary = _extract_section_between(front_text, 'Potency Summary', 'Terpenes Summary')
        elif 'Cannabinoids' in front_text:
            summary = _extract_section_between(front_text, 'Potency Summary', 'Cannabinoids')
        else:
            summary = front_text.split('Potency Summary')[-1][:800]

    if not summary:
        return obs

    lines = [x.strip() for x in summary.split('\n') if x.strip()]

    # Strategy 1: Find the value-above-label pattern.
    # The label line contains "Total THC" and "Total CBD" and starts with "Total"
    # (not with digits like the gauge scale line "0 Total THC 100...").
    for i, line in enumerate(lines):
        if ('Total THC' in line and 'Total CBD' in line
                and '=' not in line and '*' not in line
                and line.strip().startswith('Total')):
            # Value-above-label: read the preceding line for percentages.
            if i > 0:
                value_line = lines[i - 1]
                pct_values = re.findall(r'([\d.]+)\s*%', value_line)
                if len(pct_values) >= 6:
                    # Flower: THC_dry, THC_wet, CBD_dry, CBD_wet, Cann_dry, Cann_wet
                    obs['total_thc'] = _parse_number(pct_values[0])
                    obs['total_thc_wet'] = _parse_number(pct_values[1])
                    obs['total_cbd'] = _parse_number(pct_values[2])
                    obs['total_cbd_wet'] = _parse_number(pct_values[3])
                    obs['total_cannabinoids'] = _parse_number(pct_values[4])
                    obs['total_cannabinoids_wet'] = _parse_number(pct_values[5])
                elif len(pct_values) >= 3:
                    obs['total_thc'] = _parse_number(pct_values[0])
                    obs['total_cbd'] = _parse_number(pct_values[1])
                    obs['total_cannabinoids'] = _parse_number(pct_values[2])
                elif len(pct_values) >= 2:
                    obs['total_thc'] = _parse_number(pct_values[0])
                    obs['total_cbd'] = _parse_number(pct_values[1])
            # Label-above-value: look forward for percentage line.
            elif i == 0:
                for j in range(i + 1, min(i + 15, len(lines))):
                    pct_values = re.findall(r'([\d.]+)\s*%', lines[j])
                    if len(pct_values) >= 3:
                        if len(pct_values) >= 6:
                            obs['total_thc'] = _parse_number(pct_values[0])
                            obs['total_thc_wet'] = _parse_number(pct_values[1])
                            obs['total_cbd'] = _parse_number(pct_values[2])
                            obs['total_cbd_wet'] = _parse_number(pct_values[3])
                            obs['total_cannabinoids'] = _parse_number(pct_values[4])
                            obs['total_cannabinoids_wet'] = _parse_number(pct_values[5])
                        else:
                            obs['total_thc'] = _parse_number(pct_values[0])
                            obs['total_cbd'] = _parse_number(pct_values[1])
                            obs['total_cannabinoids'] = _parse_number(pct_values[2])
                        break
            break

    # Strategy 2: Check for "at dry weight" / "as received" pairs.
    # Pattern: "25.5% 22.8%" on same line (flower COAs).
    if not obs.get('total_thc'):
        dry_wet = re.findall(r'([\d.]+)\s*%\s+([\d.]+)\s*%', summary)
        if dry_wet and len(dry_wet) >= 2:
            obs['total_thc'] = _parse_number(dry_wet[0][0])
            obs['total_thc_wet'] = _parse_number(dry_wet[0][1])
            if len(dry_wet) >= 3:
                obs['total_cbd'] = _parse_number(dry_wet[1][0])
                obs['total_cbd_wet'] = _parse_number(dry_wet[1][1])
                obs['total_cannabinoids'] = _parse_number(dry_wet[2][0])
                obs['total_cannabinoids_wet'] = _parse_number(dry_wet[2][1])

    # Strategy 3: TL Labs format — read from cannabinoid table totals.
    # "Total THC 0.169 5.07 0.000" or "Total THC 46.2 462"
    if not obs.get('total_thc'):
        m = re.search(r'Total THC\s+([\d.]+)', front_text)
        if m:
            obs['total_thc'] = _parse_number(m.group(1))
        m = re.search(r'Total CBD\s+([\d.]+)', front_text)
        if m:
            obs['total_cbd'] = _parse_number(m.group(1))
        m = re.search(r'Total Cannabinoids\s+([\d.]+)', front_text)
        if m:
            obs['total_cannabinoids'] = _parse_number(m.group(1))

    return obs


# ── Front Page Results Parsing ────────────────────────────────────

def _parse_cannabinoid_line(line: str) -> Optional[Dict]:
    """Parse a single cannabinoid result line from text extraction.

    TerpLife cannabinoid lines look like:
        'Cannabidiol (CBD) 10 0.463 42.6 426'
        'Cannabidiol (CBD) 1 0.0107 0.240 2.40'
        'Cannabidiol (CBD) 1 0.0107 ND ND'
    Columns: Name | Dilution | LOD | Results(%) | Result(mg/g)
    """
    line = line.strip()
    if not line:
        return None

    # Skip non-analyte lines.
    upper = line.upper().strip()
    for skip in SKIP_KEYWORDS:
        if upper.startswith(skip):
            return None

    # Use whitespace-anchored number finding for digit-prefixed analytes.
    # Find name vs numeric boundary.
    # Strategy: known cannabinoid names end with ')' or specific patterns.
    name = ''
    values_str = ''

    # Try matching known cannabinoid patterns.
    m = re.match(r'^(.+?(?:\([A-Za-z0-9-]+\)|\(THCV\)|tot))\s+(\d.*)$', line)
    if m:
        name = m.group(1).strip()
        values_str = m.group(2).strip()
    else:
        # Fallback: split at first sequence of whitespace + digit.
        idx = _find_first_number(line)
        if idx < len(line):
            name = line[:idx].strip()
            values_str = line[idx:].strip()

    if not name or not values_str:
        return None

    # Parse numeric values.
    parts = values_str.split()
    if len(parts) < 3:
        return None

    key = _snake_case(name)
    dilution = _parse_number(parts[0])
    lod = _parse_number(parts[1])

    # Result value is in percent (3rd column).
    value = _parse_number(parts[2])

    # mg/g value (4th column) if present.
    mg_g = _parse_number(parts[3]) if len(parts) > 3 else None

    result = {
        'analysis': 'cannabinoids',
        'key': key,
        'name': name,
        'value': value,
        'units': 'percent',
    }
    if lod is not None:
        result['lod'] = lod
    if mg_g is not None:
        result['mg_g'] = mg_g

    return result


def _parse_terpene_line(line: str) -> Optional[Dict]:
    """Parse a single terpene result line from text extraction.

    TerpLife terpene lines look like:
        'Terpinolene 0.0232 1.01 █████...'
        'D-Limonene 1 0.00550 0.465 █████...'
    Columns: Name | [Dilution] | LOD | Results(%) | [bar chart chars]
    """
    # Remove bar chart characters.
    line = re.sub(r'[█▓▒░]+', '', line).strip()
    if not line:
        return None

    upper = line.upper().strip()
    if upper.startswith('TOTAL TERPENES') or upper.startswith('TOTAL '):
        return None

    # Find name vs numeric boundary.
    idx = _find_first_number(line)
    if idx >= len(line):
        return None

    name = line[:idx].strip()
    values_str = line[idx:].strip()

    if not name:
        return None

    parts = values_str.split()
    if len(parts) < 2:
        return None

    key = _snake_case(name)

    # Determine column layout:
    # Format 1 (front page, no dilution): LOD Results
    # Format 2 (full page, with dilution): Dilution LOD Results
    if len(parts) >= 3:
        dilution = _parse_number(parts[0])
        lod = _parse_number(parts[1])
        value = _parse_number(parts[2])
    else:
        dilution = None
        lod = _parse_number(parts[0])
        value = _parse_number(parts[1])

    result = {
        'analysis': 'terpenes',
        'key': key,
        'name': name,
        'value': value,
        'units': 'percent',
    }
    if lod is not None:
        result['lod'] = lod

    return result


def _parse_front_page_cannabinoids(page: Any, front_text: str) -> List[Dict]:
    """Parse cannabinoid results from the front page.

    Handles two formats:
        Classic TerpLife: two-column layout, right half has cannabinoids
            Columns: Name | Dilution | LOD | Results(%) | Result(mg/g)
        TL Laboratories: full-width cannabinoid table
            Columns: Name | Dilution | Results(%) | mg/Serving | mg/Unit
    """
    results = []

    # Determine if this is a TL Labs full-width format or classic two-column.
    is_tl_labs = 'TL LABORATORIES' in front_text.upper() or 'mg/Serving' in front_text

    try:
        if is_tl_labs:
            # TL Labs: full-width cannabinoid table parsed from full text.
            text = front_text
        else:
            # Classic TerpLife: cannabinoids in right column.
            midpoint = page.width * 0.48
            right = page.crop((midpoint, 0, page.width, page.height))
            text = right.extract_text() or ''
            text = _clean_text(text)

        # Find the cannabinoid data section after headers.
        section = ''
        for marker in ['% % mg/g', '% mg/g', '% mg mg', 'Results Result',
                        'Results mg/Serving', 'Dilution Results']:
            if marker in text:
                section = text.split(marker)[-1]
                break

        if not section:
            # Fallback: find section after "Analyte" header.
            if 'Analyte' in text and 'Cannabichromene' in text:
                idx = text.find('Cannabichromene')
                section = text[idx:]

        if not section:
            return results

        # Cut off at summary/footer lines.
        for terminator in ['Total THC=', 'Total THC =', 'mg/Unit =',
                           'LOD = Limit', 'Unless otherwise',
                           'The data contained']:
            if terminator in section:
                section = section.split(terminator)[0]

        # Handle line-wrapped analyte names (e.g., "d10 - Tetrahydrocannabinoid\n(d10-THC)")
        # by joining lines that start with "(" to the previous line.
        raw_lines = section.split('\n')
        joined_lines = []
        for line in raw_lines:
            stripped = line.strip()
            if stripped.startswith('(') and joined_lines:
                joined_lines[-1] = joined_lines[-1] + ' ' + stripped
            elif stripped:
                joined_lines.append(stripped)

        # Parse each line.
        for line in joined_lines:
            line = line.strip()
            if not line:
                continue

            # Skip total/summary lines.
            upper = line.upper()
            skip = False
            for kw in SKIP_KEYWORDS:
                if upper.startswith(kw):
                    skip = True
                    break
            if skip:
                continue

            # Parse the cannabinoid line.
            # Match: "Name ... Dilution Value1 Value2 [Value3]"
            # Known cannabinoid names end with ')' or 'tot'.
            m = re.match(
                r'^(.+?(?:\([A-Za-z0-9-]+\)|tot))\s+(\d.*)$',
                line
            )
            if m:
                name = m.group(1).strip()
                values_str = m.group(2).strip()
            else:
                idx = _find_first_number(line)
                if idx >= len(line):
                    continue
                name = line[:idx].strip()
                values_str = line[idx:].strip()

            if not name or not values_str:
                continue

            parts = values_str.split()
            if len(parts) < 2:
                continue

            key = _snake_case(name)

            if is_tl_labs:
                # TL Labs columns: Dilution | Results(%) | mg/Serving | mg/Unit
                dilution = _parse_number(parts[0])
                value = _parse_number(parts[1]) if len(parts) > 1 else None
                mg_serving = _parse_number(parts[2]) if len(parts) > 2 else None
                mg_unit = _parse_number(parts[3]) if len(parts) > 3 else None
                result = {
                    'analysis': 'cannabinoids',
                    'key': key,
                    'name': name,
                    'value': value,
                    'units': 'percent',
                }
                if mg_serving is not None:
                    result['mg_serving'] = mg_serving
                if mg_unit is not None:
                    result['mg_unit'] = mg_unit
            else:
                # Classic columns: Dilution | LOD | Results(%) | Result(mg/g)
                dilution = _parse_number(parts[0])
                lod = _parse_number(parts[1]) if len(parts) > 1 else None
                value = _parse_number(parts[2]) if len(parts) > 2 else None
                mg_g = _parse_number(parts[3]) if len(parts) > 3 else None
                result = {
                    'analysis': 'cannabinoids',
                    'key': key,
                    'name': name,
                    'value': value,
                    'units': 'percent',
                }
                if lod is not None:
                    result['lod'] = lod
                if mg_g is not None:
                    result['mg_g'] = mg_g

            results.append(result)

    except Exception as e:
        logger.debug(f'Front page cannabinoid extraction failed: {e}')

    return results


def _parse_front_page_terpenes(page: Any, front_text: str) -> Tuple[List[Dict], Optional[float]]:
    """Parse terpene results from the front page left column.

    Returns (results_list, total_terpenes_value).
    """
    results = []
    total_terpenes = None
    try:
        # Terpenes are in the left half of the page.
        midpoint = page.width * 0.48
        left = page.crop((0, 0, midpoint, page.height))
        left_text = left.extract_text() or ''
        left_text = _clean_text(left_text)

        # Find the terpene data section.
        section = ''
        for marker in ['% %', 'LOD Results']:
            if marker in left_text:
                section = left_text.split(marker)[-1]
                break

        if not section:
            return results, total_terpenes

        # Extract total terpenes before trimming.
        total_match = re.search(r'Total Terpenes\s+([\d.]+)', section)
        if total_match:
            total_terpenes = _parse_number(total_match.group(1))

        # Cut off at Total Terpenes.
        for terminator in ['Total Terpenes', 'Terpene results', 'LOD = Limit']:
            if terminator in section:
                section = section.split(terminator)[0]

        # Parse each line.
        for line in section.split('\n'):
            line = line.strip()
            if not line:
                continue
            result = _parse_terpene_line(line)
            if result:
                results.append(result)

    except Exception as e:
        logger.debug(f'Front page terpene extraction failed: {e}')

    return results, total_terpenes


# ── Multi-Page Panel Parsing ──────────────────────────────────────

def _parse_pesticides_page(page: Any) -> List[Dict]:
    """Parse pesticides from a two-column page layout."""
    results = []
    try:
        midpoint = page.width * 0.48
        for bbox in [(0, 0, midpoint, page.height), (midpoint, 0, page.width, page.height * 0.85)]:
            crop = page.crop(bbox)
            text = crop.extract_text() or ''
            text = _clean_text(text)

            # Find the data section after column headers.
            section = ''
            for marker in ['ppb ppb ppb', 'LOD Results Status']:
                if marker in text:
                    parts = text.split(marker)
                    section = parts[-1] if len(parts) > 1 else ''
                    break

            if not section:
                continue

            # Cut off at footer/notes.
            for terminator in ['LOD = Limit', 'Unless otherwise', '* - GC']:
                if terminator in section:
                    section = section.split(terminator)[0]

            for line in section.split('\n'):
                line = line.strip()
                if not line or line.startswith('*'):
                    continue

                # Parse: Name DIL ActionLimit LOD Results Status
                idx = _find_first_number(line)
                if idx >= len(line):
                    continue
                name = line[:idx].strip()
                if not name or name.upper() in SKIP_KEYWORDS:
                    continue

                parts = line[idx:].split()
                if len(parts) < 5:
                    continue

                key = _snake_case(name)
                results.append({
                    'analysis': 'pesticides',
                    'key': key,
                    'name': name,
                    'value': _parse_number(parts[3]),
                    'units': 'ppb',
                    'limit': _parse_number(parts[1]),
                    'lod': _parse_number(parts[2]),
                    'status': parts[-1].lower() if parts[-1] in ('Pass', 'Fail') else None,
                })

    except Exception as e:
        logger.debug(f'Pesticides extraction failed: {e}')

    return results


def _parse_mycotoxins_section(text: str) -> List[Dict]:
    """Parse mycotoxins from page text."""
    results = []
    try:
        if 'Mycotoxins' not in text:
            return results

        section = text.split('Mycotoxins')[1] if text.count('Mycotoxins') > 1 else text.split('Mycotoxins')[-1]
        # Find data after header row.
        for marker in ['ppb ppb ppb', 'LOD Results Status']:
            if marker in section:
                section = section.split(marker)[-1]
                break

        for terminator in ['LOD = Limit', 'Unless otherwise']:
            if terminator in section:
                section = section.split(terminator)[0]

        for line in section.split('\n'):
            line = line.strip()
            if not line:
                continue
            idx = _find_first_number(line)
            if idx >= len(line):
                continue
            name = line[:idx].strip()
            if not name or name.upper() in SKIP_KEYWORDS:
                continue

            parts = line[idx:].split()
            if len(parts) < 4:
                continue

            key = _snake_case(name)
            results.append({
                'analysis': 'mycotoxins',
                'key': key,
                'name': name,
                'value': _parse_number(parts[2]),
                'units': 'ppb',
                'limit': _parse_number(parts[0]),
                'lod': _parse_number(parts[1]),
                'status': parts[-1].lower() if parts[-1] in ('Pass', 'Fail') else None,
            })
    except Exception as e:
        logger.debug(f'Mycotoxins extraction failed: {e}')

    return results


def _parse_microbials_section(text: str) -> List[Dict]:
    """Parse microbials from page text."""
    results = []
    try:
        if 'Microbials' not in text:
            return results

        section = text.split('Microbials')[-1]
        for marker in ['cfu/g cfu/g', 'Results Status', 'LOD Results']:
            if marker in section:
                section = section.split(marker)[-1]
                break

        for terminator in ['LOD = Limit', 'Unless otherwise']:
            if terminator in section:
                section = section.split(terminator)[0]

        for line in section.split('\n'):
            line = line.strip()
            if not line:
                continue
            idx = _find_first_number(line)
            if idx >= len(line):
                # Check for "Absent in X gram" pattern.
                if 'Absent' in line:
                    name = line.split('Absent')[0].strip()
                    # Find numeric limit before "Absent".
                    parts_before = re.findall(r'[\d.]+', name)
                    name = re.sub(r'[\d.]+\s*[\d.]*\s*$', '', name).strip()
                    key = _snake_case(name)
                    results.append({
                        'analysis': 'microbials',
                        'key': key,
                        'name': name,
                        'value': None,
                        'units': 'cfu/g',
                        'status': 'pass',
                    })
                continue

            name = line[:idx].strip()
            if not name or name.upper() in SKIP_KEYWORDS:
                continue

            parts = line[idx:].split()
            key = _snake_case(name)

            # Microbial lines: Limit LOD Result Status
            # or: Limit LOD "Absent in 1 gram" Status
            value = None
            status = None
            if 'Absent' in line:
                value = None
                status = 'pass' if 'Pass' in line else None
            elif len(parts) >= 3:
                value = _parse_number(parts[2])
                status = parts[-1].lower() if parts[-1] in ('Pass', 'Fail') else None

            results.append({
                'analysis': 'microbials',
                'key': key,
                'name': name,
                'value': value,
                'units': 'cfu/g',
                'limit': _parse_number(parts[0]) if parts else None,
                'lod': _parse_number(parts[1]) if len(parts) > 1 else None,
                'status': status,
            })
    except Exception as e:
        logger.debug(f'Microbials extraction failed: {e}')

    return results


def _parse_heavy_metals_section(text: str, page: Any = None) -> List[Dict]:
    """Parse heavy metals from page text, using bbox cropping when available."""
    results = []
    try:
        if 'Heavy Metals' not in text:
            return results

        # Use left-half bbox cropping if page available (heavy metals are
        # always on the left side of multi-section pages).
        section_text = text
        if page is not None:
            try:
                left = page.crop((0, 0, page.width * 0.5, page.height))
                section_text = left.extract_text() or text
                section_text = _clean_text(section_text)
            except Exception:
                pass

        # Skip "Heavy Metals & Pesticides" (TCL line).
        sections = section_text.split('Heavy Metals')
        section = ''
        for s in sections[1:]:
            if not s.strip().startswith('&') and not s.strip().startswith('& '):
                section = s
                break

        if not section:
            return results

        for marker in ['ppb ppb ppb', 'LOD Results Status']:
            if marker in section:
                section = section.split(marker)[-1]
                break

        for terminator in ['LOD = Limit', 'Unless otherwise', 'Total ']:
            if terminator in section:
                section = section.split(terminator)[0]

        for line in section.split('\n'):
            line = line.strip()
            if not line:
                continue
            idx = _find_first_number(line)
            if idx >= len(line):
                continue
            name = line[:idx].strip()
            if not name or name.upper() in SKIP_KEYWORDS:
                continue

            parts = line[idx:].split()
            if len(parts) < 4:
                continue

            key = _snake_case(name)

            # Heavy metals columns: DIL | Action Limit | LOD | Results | Status
            # Some formats: Action Limit | LOD | Results | Status (no DIL)
            if len(parts) >= 5:
                # Has DIL column.
                results.append({
                    'analysis': 'heavy_metals',
                    'key': key,
                    'name': name,
                    'value': _parse_number(parts[3]),
                    'units': 'ppb',
                    'limit': _parse_number(parts[1]),
                    'lod': _parse_number(parts[2]),
                    'status': parts[-1].lower() if parts[-1] in ('Pass', 'Fail') else None,
                })
            else:
                # No DIL column.
                results.append({
                    'analysis': 'heavy_metals',
                    'key': key,
                    'name': name,
                    'value': _parse_number(parts[2]),
                    'units': 'ppb',
                    'limit': _parse_number(parts[0]),
                    'lod': _parse_number(parts[1]),
                    'status': parts[-1].lower() if parts[-1] in ('Pass', 'Fail') else None,
                })
    except Exception as e:
        logger.debug(f'Heavy metals extraction failed: {e}')

    return results


def _parse_residual_solvents_section(text: str) -> List[Dict]:
    """Parse residual solvents from page text."""
    results = []
    try:
        if 'Residual Solvents' not in text:
            return results

        section = text.split('Residual Solvents')[-1]
        for marker in ['ppm ppm ppm', 'LOD Results', 'Results Status']:
            if marker in section:
                section = section.split(marker)[-1]
                break

        for terminator in ['LOD = Limit', 'Unless otherwise']:
            if terminator in section:
                section = section.split(terminator)[0]

        for line in section.split('\n'):
            line = line.strip()
            if not line:
                continue
            idx = _find_first_number(line)
            if idx >= len(line):
                continue
            name = line[:idx].strip()
            if not name or name.upper() in SKIP_KEYWORDS:
                continue

            parts = line[idx:].split()
            if len(parts) < 4:
                continue

            key = _snake_case(name)
            results.append({
                'analysis': 'residual_solvents',
                'key': key,
                'name': name,
                'value': _parse_number(parts[2]),
                'units': 'ppm',
                'limit': _parse_number(parts[0]),
                'lod': _parse_number(parts[1]),
                'status': parts[-1].lower() if parts[-1] in ('Pass', 'Fail') else None,
            })
    except Exception as e:
        logger.debug(f'Residual solvents extraction failed: {e}')

    return results


def _parse_foreign_materials_section(text: str) -> List[Dict]:
    """Parse foreign materials from page text."""
    results = []
    try:
        if 'Foreign Materials' not in text:
            return results

        section = text.split('Foreign Materials')[-1]
        for marker in ['Results Status', 'Status']:
            if marker in section:
                section = section.split(marker)[-1]
                break

        for terminator in ['ND = ', 'Unless otherwise', 'LOD = ']:
            if terminator in section:
                section = section.split(terminator)[0]

        for line in section.split('\n'):
            line = line.strip()
            if not line:
                continue
            idx = _find_first_number(line)
            if idx >= len(line):
                continue
            name = line[:idx].strip()
            if not name:
                continue

            parts = line[idx:].split()
            if len(parts) < 2:
                continue

            key = _snake_case(name)
            results.append({
                'analysis': 'foreign_matter',
                'key': key,
                'name': name,
                'value': _parse_number(parts[1]) if len(parts) > 1 else None,
                'units': 'percent',
                'limit': _parse_number(parts[0]),
                'status': parts[-1].lower() if parts[-1] in ('Pass', 'Fail') else None,
            })
    except Exception as e:
        logger.debug(f'Foreign materials extraction failed: {e}')

    return results


def _parse_water_activity_section(text: str, page: Any = None) -> List[Dict]:
    """Parse water activity from page text.

    Uses bbox cropping when a page object is available for more
    precise extraction on multi-section pages.
    """
    results = []
    try:
        if 'Water Activity' not in text:
            return results

        # Strategy 1: Look for the definitive water activity data pattern.
        # "Water Activity 0.65 0.45 Pass" or "Water Activity 0.85 0.65 Pass"
        for m in re.finditer(
            r'Water Activity\s+([\d.]+)\s+([\d.]+)\s+(Pass|Fail)',
            text, re.IGNORECASE
        ):
            limit_val = float(m.group(1))
            result_val = float(m.group(2))
            # Water activity values are always < 1.0 (aw units).
            if limit_val <= 1.0 and result_val <= 1.0:
                results.append({
                    'analysis': 'water_activity',
                    'key': 'water_activity',
                    'name': 'Water Activity',
                    'value': result_val,
                    'units': 'aw',
                    'limit': limit_val,
                    'status': m.group(3).lower(),
                })
                return results

        # Strategy 2: Look for "aW" unit marker in the section.
        sections = text.split('Water Activity')
        for section in sections[1:]:
            if 'aW' in section:
                m = re.search(r'([\d.]+)\s+([\d.]+)\s+(Pass|Fail)', section)
                if m:
                    limit_val = _parse_number(m.group(1))
                    result_val = _parse_number(m.group(2))
                    if limit_val and result_val and limit_val <= 1.0 and result_val <= 1.0:
                        results.append({
                            'analysis': 'water_activity',
                            'key': 'water_activity',
                            'name': 'Water Activity',
                            'value': result_val,
                            'units': 'aw',
                            'limit': limit_val,
                            'status': m.group(3).lower(),
                        })
                        return results

    except Exception as e:
        logger.debug(f'Water activity extraction failed: {e}')

    return results


def _parse_moisture_content_section(text: str) -> List[Dict]:
    """Parse moisture content from page text."""
    results = []
    try:
        if 'Moisture Content' not in text:
            return results

        section = text.split('Moisture Content')[-1]
        for terminator in ['Unless otherwise', 'established by']:
            if terminator in section:
                section = section.split(terminator)[0]

        # Look for "Percent Moisture 15.0 9.38 Pass"
        m = re.search(r'Percent Moisture\s+([\d.]+)\s+([\d.]+)\s+(Pass|Fail)', section, re.IGNORECASE)
        if m:
            results.append({
                'analysis': 'moisture',
                'key': 'moisture_content',
                'name': 'Percent Moisture',
                'value': _parse_number(m.group(2)),
                'units': 'percent',
                'limit': _parse_number(m.group(1)),
                'status': m.group(3).lower(),
            })
    except Exception as e:
        logger.debug(f'Moisture content extraction failed: {e}')

    return results


def _parse_full_terpenes_page(page_text: str) -> List[Dict]:
    """Parse a full terpenes page (page 4+ in multi-page COAs)."""
    results = []
    try:
        if 'Terpenes Summary' not in page_text:
            return results

        section = page_text.split('Terpenes Summary')[-1]
        # Find data after column headers.
        for marker in ['% %', 'LOD Results']:
            if marker in section:
                section = section.split(marker)[-1]
                break

        for terminator in ['Total Terpenes', 'Terpene results', 'LOD = Limit']:
            if terminator in section:
                section = section.split(terminator)[0]

        for line in section.split('\n'):
            line = re.sub(r'[█▓▒░]+', '', line).strip()
            if not line:
                continue
            result = _parse_terpene_line(line)
            if result:
                results.append(result)
    except Exception as e:
        logger.debug(f'Full terpenes page extraction failed: {e}')

    return results


# ── Main Parsing Orchestrator ─────────────────────────────────────

def parse_terplife_pdf(
    parser: Any,
    pdf_path: str,
    verbose: bool = False,
    **kwargs,
) -> Dict:
    """Parse a TerpLife Labs / TL Laboratories COA PDF.

    This is the core parsing function that orchestrates all extraction.

    Args:
        parser: Optional CoADoc instance (backwards compat, unused).
        pdf_path: Path to the COA PDF file.
        verbose: Enable verbose logging.

    Returns:
        Dict with all extracted COA data conforming to the
        standard algorithm output schema.
    """
    obs = {}
    all_results: List[Dict] = []
    analyses: List[str] = []
    methods: List[str] = []

    # ── Phase 1: Open PDF and extract front page text ─────────
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
        front_page = pdf.pages[0]
        raw_text = front_page.extract_text() or ''

        if not raw_text:
            logger.warning(f'No text extracted from page 1 of {pdf_path}')
            obs['coa_pdf'] = pdf_path.replace('\\', '/').split('/')[-1]
            obs = {**TERPLIFE_LABS, **obs}
            obs['results'] = json.dumps([])
            obs['analyses'] = json.dumps([])
            obs['coa_parsed_at'] = datetime.now().isoformat()
            obs['results_hash'] = hashlib.sha256(b'[]').hexdigest()[:16]
            obs['sample_id'] = ''
            return obs

        front_text = _clean_text(raw_text)

        # ── Phase 2: Detect format ───────────────────────────
        fmt = _detect_format(front_text)
        if verbose:
            logger.info(f'Detected format: {fmt} ({num_pages} pages)')

        # Detect lab brand name.
        if fmt == 'tl_labs':
            obs['lab'] = 'TL Laboratories'

        # ── Phase 3: Extract metadata ────────────────────────
        obs.update(_parse_metadata(front_text, front_page))

        # ── Phase 4: Parse Safety Summary ────────────────────
        safety = _parse_safety_summary(front_text)
        for analysis_name, status in safety.items():
            if status in ('pass', 'fail', 'tested'):
                analyses.append(analysis_name)

        # ── Phase 5: Parse Potency Summary ───────────────────
        obs.update(_parse_potency_summary(front_text))

        # ── Phase 6: Parse front page terpenes (left column) ─
        if 'Terpenes Summary' in front_text:
            terp_results, total_terps = _parse_front_page_terpenes(front_page, front_text)
            if terp_results:
                all_results.extend(terp_results)
                if 'terpenes' not in analyses:
                    analyses.append('terpenes')
            if total_terps is not None:
                obs['total_terpenes'] = total_terps

        # ── Phase 7: Parse front page cannabinoids (right column)
        if 'Cannabinoids' in front_text:
            cann_results = _parse_front_page_cannabinoids(front_page, front_text)
            if cann_results:
                all_results.extend(cann_results)
                if 'cannabinoids' not in analyses:
                    analyses.append('cannabinoids')

        # ── Phase 8: Parse multi-page full panel ─────────────
        # Track analyte names already parsed to avoid duplicates.
        parsed_analytes = {r['name'] for r in all_results}

        for page_idx in range(1, num_pages):
            page = pdf.pages[page_idx]
            page_text = page.extract_text() or ''
            page_text = _clean_text(page_text)

            if not page_text:
                continue

            # ── Pesticides ──
            if 'Pesticides' in page_text and 'Heavy Metals & Pesticides' not in page_text:
                pest_results = _parse_pesticides_page(page)
                if pest_results:
                    all_results.extend(pest_results)
                    if 'pesticides' not in analyses:
                        analyses.append('pesticides')
                # Extract methods.
                sop_matches = re.findall(r'SOP\s*[\d]+', page_text)
                methods.extend(sop_matches)
                continue

            # ── Residual Solvents (can share page with terpenes in TL Labs) ──
            if 'Residual Solvents' in page_text:
                rs_results = _parse_residual_solvents_section(page_text)
                if rs_results:
                    all_results.extend(rs_results)
                    if 'residual_solvents' not in analyses:
                        analyses.append('residual_solvents')

            # ── Terpenes (full page, later pages) ──
            if 'Terpenes Summary' in page_text:
                terp_results = _parse_full_terpenes_page(page_text)
                # Only add terpenes not already parsed from front page.
                for tr in terp_results:
                    if tr['name'] not in parsed_analytes:
                        all_results.append(tr)
                        parsed_analytes.add(tr['name'])
                if terp_results and 'terpenes' not in analyses:
                    analyses.append('terpenes')

            # ── Mycotoxins ──
            if 'Mycotoxins' in page_text and 'Safety Summary' not in page_text:
                myco_results = _parse_mycotoxins_section(page_text)
                if myco_results:
                    all_results.extend(myco_results)
                    if 'mycotoxins' not in analyses:
                        analyses.append('mycotoxins')

            # ── Microbials ──
            if 'Microbials' in page_text and 'Safety Summary' not in page_text:
                micro_results = _parse_microbials_section(page_text)
                if micro_results:
                    all_results.extend(micro_results)
                    if 'microbials' not in analyses:
                        analyses.append('microbials')

            # ── Heavy Metals ──
            if 'Heavy Metals' in page_text and 'Heavy Metals & Pesticides' not in page_text:
                hm_results = _parse_heavy_metals_section(page_text, page=page)
                if hm_results:
                    all_results.extend(hm_results)
                    if 'heavy_metals' not in analyses:
                        analyses.append('heavy_metals')

            # Also check for combined pages where Heavy Metals appears
            # alongside "Heavy Metals & Pesticides" (TCL).
            if 'Heavy Metals' in page_text and 'Heavy Metals & Pesticides' in page_text:
                # The page has TCL + Heavy Metals section.
                hm_results = _parse_heavy_metals_section(page_text, page=page)
                if hm_results:
                    all_results.extend(hm_results)
                    if 'heavy_metals' not in analyses:
                        analyses.append('heavy_metals')

            # ── Foreign Materials ──
            if 'Foreign Materials' in page_text and 'Safety Summary' not in page_text:
                fm_results = _parse_foreign_materials_section(page_text)
                if fm_results:
                    all_results.extend(fm_results)
                    if 'foreign_matter' not in analyses:
                        analyses.append('foreign_matter')

            # ── Water Activity ──
            if 'Water Activity' in page_text and 'Safety Summary' not in page_text:
                wa_results = _parse_water_activity_section(page_text, page=page)
                if wa_results:
                    all_results.extend(wa_results)
                    if 'water_activity' not in analyses:
                        analyses.append('water_activity')

            # ── Moisture Content ──
            if 'Moisture Content' in page_text and 'Safety Summary' not in page_text:
                mc_results = _parse_moisture_content_section(page_text)
                if mc_results:
                    all_results.extend(mc_results)
                    if 'moisture' not in analyses:
                        analyses.append('moisture')

            # ── Total Contaminant Load ──
            if 'Total Contaminant Load' in page_text:
                m = re.search(
                    r'Total Contaminant Load\s+([\d,.]+)\s+([\d,.]+|ND)\s+(Pass|Fail)',
                    page_text, re.IGNORECASE
                )
                if m:
                    all_results.append({
                        'analysis': 'total_contaminant_load',
                        'key': 'total_contaminant_load',
                        'name': 'Total Contaminant Load',
                        'value': _parse_number(m.group(2)),
                        'units': 'ppb',
                        'limit': _parse_number(m.group(1)),
                        'status': m.group(3).lower(),
                    })

            # ── Cannabinoids (as received) — last page ──
            if 'Cannabinoids (as received)' in page_text:
                # Parse wet-weight cannabinoid values.
                # These are informational; dry weight on page 1 is primary.
                pass  # Front page values are authoritative.

    # ── Phase 9: Build final output ──────────────────────────
    obs = {**TERPLIFE_LABS, **obs}

    # Ensure required fields have defaults.
    obs.setdefault('product_name', '')
    obs.setdefault('product_type', '')
    obs.setdefault('status', 'pass')
    obs.setdefault('date_tested', '')

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
        obs['sample_id'] = obs.get('lab_id', hashlib.sha256(id_input.encode()).hexdigest()[:16])

    obs.setdefault('lab_id', obs.get('sample_id', ''))
    obs['coa_pdf'] = pdf_path.replace('\\', '/').split('/')[-1]

    if verbose:
        logger.info(
            f'Parsed {obs["coa_pdf"]}: '
            f'{len(all_results)} results, '
            f'{len(analyses)} analyses'
        )

    return obs


# ── Entry Point (LAB_REGISTRY compatible) ──────────────────────────

def parse_terplife_coa(
    parser: Any = None,
    doc: Any = '',
    **kwargs,
) -> Dict:
    """Parse a TerpLife Labs / TL Laboratories COA PDF.

    This is the main entry point registered in the LAB_REGISTRY.
    Satisfies the algorithm contract: parse_{lab}_coa(parser, doc).

    Args:
        parser: Optional CoADoc instance (backwards compatibility).
        doc:    Path to the COA PDF file.

    Returns:
        Dict with all extracted COA data.
    """
    # Handle legacy call signature: parse_terplife_coa(parser, doc).
    if isinstance(parser, str) and not doc:
        doc = parser
        parser = None

    if isinstance(doc, str) and doc.startswith('http'):
        raise ValueError(
            'URL parsing requires network access. '
            'Provide the PDF file path instead.'
        )

    return parse_terplife_pdf(parser, doc, **kwargs)


def is_terplife(pdf_path: str) -> bool:
    """Quick check if a PDF is a TerpLife Labs / TL Laboratories COA.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        True if the PDF is identified as TerpLife Labs.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = pdf.pages[0].extract_text() or ''
            text_upper = text.upper()
            return (
                'TERPLIFE' in text_upper
                or 'TL LABORATORIES' in text_upper
                or 'TERPLIFELABS.COM' in text_upper
            )
    except Exception:
        return False


# ── Tests ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    import os
    import sys

    # Enable verbose logging for testing.
    logging.basicConfig(level=logging.INFO)

    # Test with provided sample COAs.
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [f for f in os.listdir(test_dir) if f.endswith('.pdf')]

    if not test_files:
        print('No PDF files found in current directory.')
        print('Usage: python terplife.py')
        print('Place TerpLife COA PDFs in the same directory.')
        sys.exit(0)

    all_data = []
    errors = []
    start = datetime.now()

    for pdf_file in sorted(test_files):
        pdf_path = os.path.join(test_dir, pdf_file)
        try:
            data = parse_terplife_coa(doc=pdf_path, verbose=True)
            all_data.append(data)
            results = json.loads(data.get('results', '[]'))
            analyses = json.loads(data.get('analyses', '[]'))
            print(
                f'  ✓ {pdf_file}: '
                f'{data.get("product_name", "?")} | '
                f'{len(results)} results | '
                f'{", ".join(analyses)}'
            )
        except Exception as e:
            errors.append((pdf_file, str(e)))
            print(f'  ✗ {pdf_file}: {e}')

    end = datetime.now()
    print(f'\nParsed {len(all_data)} of {len(test_files)} COAs '
          f'in {(end - start).total_seconds():.2f}s')
    if errors:
        print(f'Errors ({len(errors)}):')
        for f, e in errors:
            print(f'  {f}: {e}')
