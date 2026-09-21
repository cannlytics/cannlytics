"""
Parse Encore Labs COA — COA Doc Hybrid Algorithm (Offline-First)
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 3/2/2024
Updated: 3/6/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Encore Labs COA PDFs directly from the PDF text — no network
    access required. This is the modernized offline-first engine that
    extracts all data from the PDF itself using pdfplumber text
    extraction, bbox cropping, and regex-based field parsing.

    Encore Labs is a major California cannabis testing laboratory
    operating from Pasadena, CA. They test flower, concentrates,
    edibles, pre-rolls, and other cannabis product types under
    California's regulatory compliance testing framework.

    Identification:
        Encore Labs COAs contain 'Encore Labs' in the header and
        either 'encorelabs.com' or 'encore-labs.com' URL.
        Two format eras exist:
            - 2023-2024: 75 N Vinedo Ave, Lic# C8-0000086-LIC
            - 2025-2026: 120 W Bellevue Dr, Lic# C8-0000179-LIC

    Format notes:
        * Text-based layout (pdfplumber extract_text + regex)
        * Page 1: Header, product info, summary table, cannabinoid
          results with value-above-label summary boxes
        * Page 2: Pesticides (two-column merged layout) or Terpenes
        * Page 3: Mycotoxins + Residual Solvents
        * Page 4: Microbials + Heavy Metals
        * Two-column Distributor/Producer entity layout (needs bbox)
        * Flower: includes terpenes, moisture, water activity
        * Edibles: cannabinoids in mg/serving, different pesticide limits
        * Concentrates: standard full-panel without terpenes

Data Points:

    ✓ product_name, strain_name, product_type, product_subtype
    ✓ date_tested, date_received, date_collected, date_produced
    ✓ batch_number, batch_size, sample_size
    ✓ lab, lab_license_number, lab_address, lab_city, lab_state,
      lab_zipcode, lab_phone, lab_website
    ✓ producer, producer_license_number, producer_address
    ✓ distributor, distributor_license_number, distributor_address
    ✓ sample_id (lab's Sample ID)
    ✓ metrc_ids (METRC Batch, METRC Sample)
    ✓ total_thc, total_cbd, total_cannabinoids, total_terpenes
    ✓ sum_of_cannabinoids
    ✓ moisture_content, water_activity
    ✓ status (overall batch pass/fail)
    ✓ analyses (list of analysis types)
    ✓ results (list of analyte result dicts)
"""
# Standard imports:
import hashlib
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# External imports:
import pdfplumber


# ── Encore Labs Constants ─────────────────────────────────────────

ENCORE_LABS = {
    'coa_algorithm': 'encore.py',
    'coa_algorithm_entry_point': 'parse_encore_coa',
    'lims': 'Encore Labs',
    'url': 'https://encorelabs.com',
    'lab': 'Encore Labs',
    'lab_website': 'https://encorelabs.com',
    'lab_phone': '(626) 696-3086',
}

# Standard analysis name mappings for Encore Labs section headers.
ANALYSIS_SECTION_MAP = {
    'cannabinoid': 'cannabinoids',
    'terpene': 'terpenes',
    'pesticide': 'pesticides',
    'mycotoxin': 'mycotoxins',
    'residual solvent': 'residual_solvents',
    'heavy metal': 'heavy_metals',
    'microbial impurit': 'microbials',
    'microbial': 'microbials',
    'foreign matter': 'foreign_matter',
    'moisture': 'moisture',
    'water activity': 'water_activity',
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
    'foreign_matter': '',
    'water_activity': 'aw',
    'moisture': 'percent',
}

# Analyte key standardization map (display name -> snake_case key).
ANALYTE_KEY_MAP = {
    # Cannabinoids
    '\u03949-THC': 'delta_9_thc',
    '\u22069-THC': 'delta_9_thc',
    'D9-THC': 'delta_9_thc',
    '\u03948-THC': 'delta_8_thc',
    '\u22068-THC': 'delta_8_thc',
    'D8-THC': 'delta_8_thc',
    'THCa': 'thca',
    'THCVa': 'thcva',
    'THCV': 'thcv',
    'CBDa': 'cbda',
    'CBD': 'cbd',
    'CBDVa': 'cbdva',
    'CBDV': 'cbdv',
    'CBGa': 'cbga',
    'CBG': 'cbg',
    'CBCa': 'cbca',
    'CBC': 'cbc',
    'CBN': 'cbn',
    'CBL': 'cbl',

    # Terpenes
    '\u03b2-Caryophyllene': 'beta_caryophyllene',
    '\u03b2-Myrcene': 'beta_myrcene',
    '\u03b2-Pinene': 'beta_pinene',
    '\u03b2-Ocimene': 'beta_ocimene',
    '\u03b1-Humulene': 'alpha_humulene',
    '\u03b1-Pinene': 'alpha_pinene',
    '\u03b1-Bisabolol': 'alpha_bisabolol',
    '\u03b1-Terpinene': 'alpha_terpinene',
    '\u03b1-Phellandrene': 'alpha_phellandrene',
    '\u03b1-Cedrene': 'alpha_cedrene',
    '\u03b3-Terpinene': 'gamma_terpinene',
    '\u03b4-Limonene': 'delta_limonene',
    '\u03b4-3-Carene': 'delta_3_carene',
    'trans-\u03b2-Ocimene': 'trans_beta_ocimene',
    'cis-Nerolidol': 'cis_nerolidol',
    'trans-Nerolidol': 'trans_nerolidol',
    'Caryophyllene Oxide': 'caryophyllene_oxide',
    'Sabinene Hydrate': 'sabinene_hydrate',
    'Geranyl Acetate': 'geranyl_acetate',
    'p-Cymene': 'p_cymene',
    'Piperonyl Butoxide': 'piperonyl_butoxide',

    # Pesticides (multi-word / special names)
    'Parathion Methyl': 'parathion_methyl',
    'Kresoxim Methyl': 'kresoxim_methyl',
    'Ethylene Oxide': 'ethylene_oxide',
    'Piperonyl Butoxide': 'piperonyl_butoxide',
    'PCNB': 'pcnb',

    # Residual solvents
    'Isopropyl alcohol': 'isopropyl_alcohol',
    'Isopropanol': 'isopropyl_alcohol',
    '1,2-Dichloroethane': 'dichloroethane_1_2',
    '1,2-Dichloro-Ethane': 'dichloroethane_1_2',
    'Ethyl acetate': 'ethyl_acetate',
    'Ethyl-Acetate': 'ethyl_acetate',
    'Ethyl ether': 'ethyl_ether',
    'Ethyl-Ether': 'ethyl_ether',
    'Ethylene Oxide': 'ethylene_oxide',
    'Total xylenes (ortho-, meta-, para-)': 'total_xylenes',
    'Xylenes': 'total_xylenes',
    'Methylene chloride': 'methylene_chloride',
    'Methylene-Chloride': 'methylene_chloride',
    'n-Hexane': 'n_hexane',
    'Trichloroethylene': 'trichloroethylene',
    'Trichloroethene': 'trichloroethylene',

    # Mycotoxins
    'Aflatoxin B1': 'aflatoxin_b1',
    'Aflatoxin B2': 'aflatoxin_b2',
    'Aflatoxin G1': 'aflatoxin_g1',
    'Aflatoxin G2': 'aflatoxin_g2',
    'Total Aflatoxins': 'total_aflatoxins',
    'Ochratoxin A': 'ochratoxin_a',

    # Heavy metals
    'Arsenic': 'arsenic',
    'Cadmium': 'cadmium',
    'Lead': 'lead',
    'Mercury': 'mercury',

    # Microbiology
    'Aspergillus flavus': 'aspergillus_flavus',
    'Aspergillus fumigatus': 'aspergillus_fumigatus',
    'Aspergillus niger': 'aspergillus_niger',
    'Aspergillus terreus': 'aspergillus_terreus',
    'Salmonella spp': 'salmonella_spp',
    'Shiga toxin\u2013producing Escherichia coli': 'stec',
    'Shiga toxin-producing Escherichia coli': 'stec',
}

# Lines to skip in results extraction.
SKIP_KEYWORDS = {
    'analytes', 'analyte', 'method:', 'date tested', 'loq =',
    'lod =', 'total thc =', 'result is based', 'samples obtained',
    'all laboratory', 'encore labs', 'certificate of analysis',
    'regulatory compliance', 'lic#', 'qa supervisor', 'compliance manager',
    'laboratory supervisor', 'vp of operations', 'brad kao',
    'jessica burnham', 'mary beth smith', 'evelyn alvarez',
    'primary aromas', 'serving(s) per container',
    'testing performed', 'total thc = thca', 'cannabinoid acid',
    '\u03bcg/g', '\u03bcg/kg', 'mg/g', 'mg/unit', 'mg/serving',
    'without the written', 'product tested',
}

# Section header patterns to detect analysis boundaries.
SECTION_HEADERS = [
    'Cannabinoids', 'Terpenes', 'Pesticides', 'Mycotoxins',
    'Residual Solvents', 'Microbial Impurities', 'Heavy Metals',
    'Foreign Matter', 'Moisture', 'Water Activity',
]


# ── Utility Functions ─────────────────────────────────────────────

def _snake_case(text: str) -> str:
    """Convert analyte display name to snake_case key."""
    stripped = text.strip()
    if stripped in ANALYTE_KEY_MAP:
        return ANALYTE_KEY_MAP[stripped]
    # Try with whitespace normalization.
    cleaned = re.sub(r'\s+', ' ', stripped)
    if cleaned in ANALYTE_KEY_MAP:
        return ANALYTE_KEY_MAP[cleaned]
    # Fallback: normalize to snake_case.
    s = stripped.lower().strip()
    s = s.replace('\u03b1', 'alpha_').replace('\u03b2', 'beta_')
    s = s.replace('\u03b3', 'gamma_').replace('\u03b4', 'delta_')
    s = s.replace('\u0394', 'delta_').replace('\u2206', 'delta_')
    s = re.sub(r'\*+$', '', s)
    s = re.sub(r'\([^)]*\)', '', s)
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s)
    s = s.strip('_')
    return s


def _parse_number(text: str) -> Optional[float]:
    """Parse a numeric string. Returns None for ND/<LOQ/NT."""
    if not text or not isinstance(text, str):
        return None
    text = text.strip()
    upper = text.upper()
    if upper in ('ND', 'N/A', 'NT', '', '-', 'NONE', 'N/T'):
        return None
    if '<LOQ' in upper or '<LOD' in upper or '<' in upper:
        return None
    if 'NOT DETECTED' in upper:
        return None
    # Remove status suffixes.
    text = re.sub(r'\s*(PASS|FAIL|TESTED|COMPLETE)\s*$', '', text,
                  flags=re.IGNORECASE).strip()
    text = text.replace(',', '')
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def _parse_date(text: str) -> str:
    """Parse a date string to ISO format (YYYY-MM-DD)."""
    if not text or not isinstance(text, str):
        return ''
    text = text.strip()
    for fmt in ('%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%b %d, %Y',
                '%B %d, %Y'):
        try:
            return datetime.strptime(text, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return text


def _clean_text(text: str) -> str:
    """Clean null bytes and normalize whitespace."""
    if not text:
        return ''
    text = text.replace('\x00', '')
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def _should_skip_line(line: str) -> bool:
    """Check if a line should be skipped during results parsing."""
    if not line or not line.strip():
        return True
    lower = line.strip().lower()
    for kw in SKIP_KEYWORDS:
        if kw in lower:
            return True
    return False


def _find_first_number(line: str) -> int:
    """Find the index of the first numeric value in a line.

    Returns the character index where the first number starts,
    used to split analyte name from numeric values.
    """
    # Match the first occurrence of a decimal number, optionally negative.
    match = re.search(r'(?<!\w)(\d+\.?\d*)', line)
    if match:
        return match.start()
    return len(line)


def _extract_sections(lines: List[str], start_line: int = 0) -> Dict[str, List[str]]:
    """Extract analysis sections from text lines.

    Splits lines into sections based on known section headers.
    Returns a dict mapping analysis name -> list of content lines.
    """
    sections = {}
    current_section = None
    current_lines = []

    for line in lines[start_line:]:
        stripped = line.strip()

        # Check if this line is a section header.
        matched_section = None
        for header in SECTION_HEADERS:
            if stripped == header or stripped.startswith(header + '\n'):
                for prefix, std_name in ANALYSIS_SECTION_MAP.items():
                    if prefix.lower() in header.lower():
                        matched_section = std_name
                        break
                break

        if matched_section:
            # Save previous section.
            if current_section and current_lines:
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].extend(current_lines)
            current_section = matched_section
            current_lines = []
        elif current_section:
            current_lines.append(line)

    # Save last section.
    if current_section and current_lines:
        if current_section not in sections:
            sections[current_section] = []
        sections[current_section].extend(current_lines)

    return sections


# ── Metadata Parsing Functions ────────────────────────────────────

def _parse_lab_header(lines: List[str]) -> Dict:
    """Parse lab details from the page header (lines 0-4)."""
    obs = {}

    for line in lines[:6]:
        line = _clean_text(line)

        # Lab name and phone.
        if '(626)' in line or '696-3086' in line:
            parts = line.split('(626)')
            obs['lab'] = parts[0].strip()
            obs['lab_phone'] = '(626)' + parts[1].strip() if len(parts) > 1 else '(626) 696-3086'

        # Lab address and website.
        if 'encorelabs.com' in line.lower() or 'encore-labs.com' in line.lower():
            # Street is before 'http'.
            if 'http' in line:
                street_part = line.split('http')[0].strip()
                obs['lab_street'] = street_part
                url_part = 'http' + line.split('http')[1]
                # Clean URL - stop at first space or 'Certificate'.
                url = re.match(r'(https?://[^\s]+)', url_part)
                if url:
                    obs['lab_website'] = url.group(1)

        # License and city/state/zip.
        if 'Lic#' in line or 'Lic #' in line:
            lic_match = re.search(r'Lic#?\s*(C8-\d+-LIC)', line)
            if lic_match:
                obs['lab_license_number'] = lic_match.group(1)
            # City, State, Zip before Lic#.
            address_part = re.split(r'Lic', line)[0].strip()
            csz = re.match(r'(.+),\s*([A-Z]{2})\s+(\d{5})', address_part)
            if csz:
                obs['lab_city'] = csz.group(1).strip()
                obs['lab_state'] = csz.group(2)
                obs['lab_zipcode'] = csz.group(3)
                if obs.get('lab_street'):
                    obs['lab_address'] = f"{obs['lab_street']}, {address_part}"

    return obs


def _parse_product_metadata(lines: List[str]) -> Dict:
    """Parse product metadata from page 1 text lines."""
    obs = {}

    # Product name is on line 5 (after header block).
    if len(lines) > 5:
        obs['product_name'] = _clean_text(lines[5])

    for line in lines[5:]:
        line = _clean_text(line)

        # METRC IDs.
        if 'METRC Batch:' in line:
            value = line.split('METRC Batch:')[1].strip()
            # May have trailing text after the IDs.
            ids = re.findall(r'(1A[A-Fa-f0-9]{22,})', value)
            if ids:
                obs['metrc_ids'] = ids
                obs['metrc_source_id'] = ', '.join(ids)
        elif 'METRC Sample:' in line:
            parts = line.split('METRC Sample:')[1].strip()
            sample_id = re.match(r'(1A[A-Fa-f0-9]{22,})', parts)
            if sample_id:
                obs['metrc_sample_label'] = sample_id.group(1)
            # "Produced:" may be on the same line.
            if 'Produced:' in line:
                date_match = re.search(r'Produced:\s*(\d{2}/\d{2}/\d{4})', line)
                if date_match:
                    obs['date_produced'] = _parse_date(date_match.group(1))

        # Sample ID.
        if 'Sample ID:' in line:
            sid_match = re.search(r'Sample ID:\s*(\S+)', line)
            if sid_match:
                obs['sample_id'] = sid_match.group(1)

        # Dates.
        if 'Collected:' in line:
            d = re.search(r'Collected:\s*(\d{2}/\d{2}/\d{4})', line)
            if d:
                obs['date_collected'] = _parse_date(d.group(1))
        if 'Received:' in line:
            d = re.search(r'Received:\s*(\d{2}/\d{2}/\d{4})', line)
            if d:
                obs['date_received'] = _parse_date(d.group(1))
        if 'Completed:' in line:
            d = re.search(r'Completed:\s*(\d{2}/\d{2}/\d{4})', line)
            if d:
                obs['date_tested'] = _parse_date(d.group(1))

        # Classifications.
        if 'Strain:' in line:
            obs['strain_name'] = line.split('Strain:')[1].strip().split('Received')[0].strip()
        if 'Matrix:' in line:
            # Extract just the matrix value, stopping at next field.
            after_matrix = line.split('Matrix:')[1].strip()
            # Stop at common following fields.
            for stop in ('Completed:', 'Received:', 'Lic.', 'Sample Size'):
                if stop in after_matrix:
                    after_matrix = after_matrix.split(stop)[0].strip()
            obs['product_type'] = after_matrix
        if line.strip().startswith('Type:'):
            after_type = line.split('Type:')[1].strip()
            # Stop at common following fields.
            for stop in ('Sample Size:', 'Batch:', 'units', 'Lic.'):
                if stop in after_type:
                    after_type = after_type.split(stop)[0].strip()
            obs['product_subtype'] = after_type

        # Batch number - stop at first space-separated address or field.
        if 'Batch#:' in line:
            raw_batch = line.split('Batch#:')[1].strip()
            # Batch numbers are typically alphanumeric with hyphens.
            # Stop at whitespace followed by digits (zip), city names, etc.
            batch_match = re.match(r'([\w\-]+(?:\s*\n)?)', raw_batch)
            if batch_match:
                obs['batch_number'] = batch_match.group(1).strip()

        # Sample size and batch size.
        if 'Sample Size:' in line:
            ss_match = re.search(r'Sample Size:\s*(.+?)(?:;|$)', line)
            if ss_match:
                obs['sample_size'] = ss_match.group(1).strip()
        if 'Batch:' in line and 'METRC' not in line:
            bs_match = re.search(r'Batch:\s*([\d,]+\s*\S*)', line)
            if bs_match:
                obs['batch_size'] = bs_match.group(1).strip()

        # Stop parsing metadata at the summary table.
        if line.strip() == 'Summary':
            break

    return obs


def _parse_entity_columns(page) -> Dict:
    """Extract producer and distributor using bbox cropping.

    Encore Labs uses a two-column layout for Distributor (left) and
    Producer (right), similar to SC Labs. Standard text extraction
    interleaves these columns, producing garbled text. We use
    pdfplumber's bbox cropping to separate them.
    """
    obs = {}
    try:
        words = page.extract_words()
    except Exception:
        return obs

    if not words:
        return obs

    # Find key word coordinates.
    producer_x = None
    producer_y = None
    distributor_x = None
    distributor_y = None
    summary_y = None
    batch_hash_y = None

    for word in words:
        text = word['text']
        if text == 'Producer' and producer_x is None:
            producer_x = word['x0']
            producer_y = word['top']
        elif text == 'Distributor' and distributor_x is None:
            distributor_x = word['x0']
            distributor_y = word['top']
        elif text == 'Summary' and summary_y is None:
            summary_y = word['top']
        elif text.startswith('Batch#:') and batch_hash_y is None:
            batch_hash_y = word['bottom']

    if not distributor_x or not producer_x:
        return obs

    # Bottom boundary: just above "Summary" or "Batch#" line.
    bottom = summary_y or batch_hash_y or (page.height * 0.35)
    if batch_hash_y and batch_hash_y > (distributor_y or 0):
        bottom = max(batch_hash_y + 15, bottom)

    # Top boundary: the distributor/producer header row.
    top = min(
        distributor_y or page.height,
        producer_y or page.height,
    )

    # ── Distributor (left column) ──
    try:
        dist_bbox = (distributor_x - 2, top, producer_x - 2, bottom)
        dist_crop = page.within_bbox(dist_bbox)
        if dist_crop:
            dist_text = dist_crop.extract_text() or ''
            _parse_entity_text(dist_text, 'distributor', obs)
    except Exception:
        pass

    # ── Producer (right column) ──
    try:
        prod_bbox = (producer_x - 2, top, page.width, bottom)
        prod_crop = page.within_bbox(prod_bbox)
        if prod_crop:
            prod_text = prod_crop.extract_text() or ''
            _parse_entity_text(prod_text, 'producer', obs)
    except Exception:
        pass

    return obs


def _parse_entity_text(text: str, prefix: str, obs: Dict):
    """Parse entity (producer/distributor) text into obs dict."""
    lines = text.strip().split('\n')
    # Remove the header word itself.
    content_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped in ('Producer', 'Distributor', ''):
            continue
        content_lines.append(stripped)

    if not content_lines:
        return

    # First non-header line is the entity name.
    name = content_lines[0]
    obs[prefix] = name

    # Look for license number.
    for line in content_lines:
        lic_match = re.search(r'Lic\.?\s*#?\s*(C\d{1,2}-\d+-LIC|DCC-\d+|CDPH-\d+|CCL\d+-\d+)', line)
        if lic_match:
            obs[f'{prefix}_license_number'] = lic_match.group(1)

    # Build address from remaining lines after name and license.
    address_parts = []
    for line in content_lines[1:]:
        if 'Lic' in line:
            continue
        if line.strip() == name:
            continue
        # Skip phone numbers.
        if re.match(r'^\s*:?\s*\(\d{3}\)', line):
            continue
        address_parts.append(line.strip())

    if address_parts:
        full_addr = ', '.join(address_parts).replace(', ,', ',')
        obs[f'{prefix}_address'] = full_addr
        # Extract state and zip from last part.
        zip_match = re.search(r'([A-Z]{2})\s+(\d{5})', full_addr)
        if zip_match:
            obs[f'{prefix}_state'] = zip_match.group(1)
            obs[f'{prefix}_zipcode'] = zip_match.group(2)


def _parse_summary_table(lines: List[str]) -> Dict:
    """Parse the summary table for overall status and analysis statuses."""
    obs = {}
    in_summary = False

    for line in lines:
        stripped = line.strip()
        if stripped == 'Summary':
            in_summary = True
            continue
        if in_summary and stripped.startswith('Cannabinoids'):
            # End of summary section.
            in_summary = False

        if in_summary:
            if 'Batch' in stripped and 'Pass' in stripped:
                obs['status'] = 'pass'
            elif 'Batch' in stripped and 'Fail' in stripped:
                obs['status'] = 'fail'

            # Moisture and water activity from summary.
            moisture_match = re.search(r'(\d+\.?\d*)%\s*-?\s*Complete', stripped)
            if moisture_match and 'Moisture' in stripped:
                obs['moisture_content'] = float(moisture_match.group(1))
            wa_match = re.search(r'(\d+\.\d+)\s*aw', stripped)
            if wa_match and 'Water Activity' in stripped:
                obs['water_activity'] = float(wa_match.group(1))

    return obs


def _parse_summary_totals(lines: List[str]) -> Dict:
    """Parse summary box totals (value-above-label pattern).

    Encore Labs uses boxes like:
        85.661 %          0.233 %          90.647 %
        Total THC         Total CBD        Total Cannabinoids

    Or for edibles:
        10.10 mg/serving  ND               10.33 mg/serving
        Total THC         Total CBD        Total Cannabinoids
    """
    obs = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Look for the label line "Total THC Total CBD Total Cannabinoids"
        # Must NOT be the formula line ("Total THC = THCa * 0.877...")
        if ('Total THC' in stripped and 'Total CBD' in stripped
                and '=' not in stripped and '*' not in stripped):
            # Values are on the preceding line.
            if i > 0:
                values_line = lines[i - 1].strip()
                # Extract values using pattern matching.
                # Patterns: "85.661 %", "10.10 mg/serving", "ND", "0.233 %"
                value_tokens = re.findall(
                    r'([\d.]+)\s*(?:%|mg/serving)?|(\bND\b)',
                    values_line,
                )
                extracted = []
                for num_str, nd_str in value_tokens:
                    if nd_str:
                        extracted.append(0.0)
                    elif num_str:
                        try:
                            extracted.append(float(num_str))
                        except ValueError:
                            pass

                # Assign: first=THC, second=CBD, third=Total Cannabinoids
                if len(extracted) >= 1:
                    obs['total_thc'] = extracted[0]
                if len(extracted) >= 2:
                    obs['total_cbd'] = extracted[1]
                if len(extracted) >= 3:
                    obs['total_cannabinoids'] = extracted[2]
            break
    return obs


# ── Results Parsing Functions ─────────────────────────────────────

def _parse_cannabinoid_lines(lines: List[str]) -> Tuple[List[Dict], str]:
    """Parse cannabinoid results from text lines.

    Returns (results_list, method_string).
    """
    results = []
    method = ''
    in_cannabinoids = False
    column_order = None  # Track column structure

    for line in lines:
        stripped = line.strip()

        # Detect cannabinoid section start (standalone header only).
        if stripped == 'Cannabinoids':
            in_cannabinoids = True
            continue
        if not in_cannabinoids:
            continue

        # Section end markers.
        if any(stripped == h for h in SECTION_HEADERS
               if h != 'Cannabinoids'):
            break
        if 'Total THC = THCa' in stripped or '1 Unit =' in stripped:
            break

        # Method line.
        if 'Method:' in stripped:
            method = stripped.split('Method:')[1].strip()
            continue

        # Skip header/unit lines.
        if _should_skip_line(stripped):
            continue
        if stripped.startswith('Analytes') or stripped.startswith('mg/g'):
            continue

        # Parse total summary lines.
        if stripped.startswith('Total THC') and not stripped.startswith('Total THCa'):
            vals = stripped.split('Total THC')[1].strip().split()
            if vals:
                val = _parse_number(vals[0])
                # Store but don't add as analyte result.
            continue
        if stripped.startswith('Total CBD') and not stripped.startswith('Total CBDa'):
            continue
        if stripped.startswith('Total Cannabinoids'):
            continue
        if stripped.startswith('Sum of Cannabinoids'):
            continue

        # Parse analyte line: "THCa 0.273 0.819 ND ND ND"
        first_num = _find_first_number(stripped)
        if first_num >= len(stripped):
            continue

        name = stripped[:first_num].strip()
        if not name or len(name) < 2:
            continue

        key = _snake_case(name)
        values_str = stripped[first_num:]
        parts = values_str.split()

        if len(parts) < 3:
            continue

        try:
            lod = _parse_number(parts[0])
            loq = _parse_number(parts[1])
            value = _parse_number(parts[2])  # % column

            result = {
                'analysis': 'cannabinoids',
                'key': key,
                'name': name,
                'value': value,
                'units': 'percent',
                'lod': lod,
                'loq': loq,
                'limit': None,
                'status': '',
            }

            # mg/g column if available.
            if len(parts) > 3:
                mg_g = _parse_number(parts[3])
                if mg_g is not None:
                    result['mg_g'] = mg_g

            results.append(result)
        except (IndexError, ValueError):
            continue

    return results, method


def _parse_pesticide_lines(lines: List[str]) -> Tuple[List[Dict], str]:
    """Parse pesticide results from text lines.

    Encore Labs renders pesticides in a two-column layout that
    pdfplumber merges into single lines like:
        "Abamectin 0.019 0.056 0.1 ND Pass Fludioxonil 0.011 0.034 0.1 ND Pass"
    """
    results = []
    method = ''
    in_pesticides = False

    for line in lines:
        stripped = line.strip()

        if stripped == 'Pesticides':
            in_pesticides = True
            continue
        if not in_pesticides:
            continue

        # Section end markers.
        if stripped.startswith('Date Tested:'):
            break
        if any(stripped == h for h in SECTION_HEADERS
               if h != 'Pesticides'):
            break

        # Method line.
        if 'Method:' in stripped:
            method = stripped.split('Method:')[1].strip()
            continue

        if _should_skip_line(stripped):
            continue
        if stripped.startswith('Analytes') or stripped.startswith('\u03bcg'):
            continue

        # Parse the two-column merged line.
        _parse_two_column_pesticide_line(stripped, results)

    return results, method


def _parse_two_column_pesticide_line(line: str, results: List[Dict]):
    """Parse a single two-column pesticide line.

    Pattern: "Name1 LOD1 LOQ1 Limit1 Result1 Status1 Name2 LOD2 LOQ2 Limit2 Result2 Status2"

    Strategy: Find all words, identify the "Pass" or "Fail" markers
    to split into left/right columns.
    """
    # Find all Pass/Fail markers to identify column boundaries.
    pass_positions = [(m.start(), m.end()) for m in
                      re.finditer(r'\b(Pass|Fail)\b', line)]

    if not pass_positions:
        return

    # Split at the first Pass/Fail boundary.
    first_end = pass_positions[0][1]
    left_part = line[:first_end].strip()
    right_part = line[first_end:].strip() if first_end < len(line) else ''

    # Parse left column.
    _parse_single_pesticide_entry(left_part, results)

    # Parse right column (if exists).
    if right_part:
        # The right column also ends with Pass/Fail.
        _parse_single_pesticide_entry(right_part, results)


def _parse_single_pesticide_entry(text: str, results: List[Dict]):
    """Parse a single pesticide entry like "Abamectin 0.019 0.056 0.1 ND Pass"."""
    text = text.strip()
    if not text:
        return

    # Extract status from end.
    status = ''
    if text.endswith('Pass'):
        status = 'pass'
        text = text[:-4].strip()
    elif text.endswith('Fail'):
        status = 'fail'
        text = text[:-4].strip()
    elif text.endswith('Tested'):
        status = 'tested'
        text = text[:-6].strip()

    # Find where the name ends and numbers begin.
    first_num = _find_first_number(text)
    if first_num >= len(text):
        return

    name = text[:first_num].strip()
    if not name or len(name) < 2:
        return

    key = _snake_case(name)
    parts = text[first_num:].split()

    if len(parts) < 4:
        return

    try:
        lod = _parse_number(parts[0])
        loq = _parse_number(parts[1])
        limit = _parse_number(parts[2])
        value = _parse_number(parts[3])

        results.append({
            'analysis': 'pesticides',
            'key': key,
            'name': name,
            'value': value,
            'units': 'ug/g',
            'lod': lod,
            'loq': loq,
            'limit': limit,
            'status': status,
        })
    except (IndexError, ValueError):
        pass


def _parse_standard_section_lines(
        lines: List[str],
        section_name: str,
        analysis_type: str,
        units: str,
        has_limit: bool = True,
        has_status: bool = True,
    ) -> Tuple[List[Dict], str]:
    """Parse results for a standard section (heavy metals, solvents, mycotoxins).

    Standard format: "Analyte LOD LOQ [Limit] Result Status"
    """
    results = []
    method = ''
    in_section = False

    for line in lines:
        stripped = line.strip()

        # Match standalone section header only (not summary table entries
        # like "Mycotoxins 02/02/2026 LC-MS Pass").
        if stripped == section_name or stripped == section_name + '\n':
            in_section = True
            continue
        if not in_section:
            continue

        # Section end markers.
        if stripped.startswith('Date Tested:'):
            in_section = False
            continue
        if any(stripped == h or stripped == h + '\n'
               for h in SECTION_HEADERS if h != section_name):
            break
        if 'LOQ = Limit' in stripped:
            continue

        # Method line.
        if 'Method:' in stripped:
            method = stripped.split('Method:')[1].strip()
            continue

        if _should_skip_line(stripped):
            continue

        # Parse analyte line.
        first_num = _find_first_number(stripped)
        if first_num >= len(stripped):
            continue

        name = stripped[:first_num].strip()
        if not name or len(name) < 2:
            continue

        key = _snake_case(name)
        parts = stripped[first_num:].split()

        try:
            if has_limit and has_status and len(parts) >= 5:
                # LOD, LOQ, Limit, Result, Status
                results.append({
                    'analysis': analysis_type,
                    'key': key,
                    'name': name,
                    'value': _parse_number(parts[3]),
                    'units': units,
                    'lod': _parse_number(parts[0]),
                    'loq': _parse_number(parts[1]),
                    'limit': _parse_number(parts[2]),
                    'status': parts[4].lower() if len(parts) > 4 else '',
                })
            elif has_limit and has_status and len(parts) >= 3:
                # Some rows have fewer columns (e.g., Aflatoxin B1 without limit).
                # Try: LOD, LOQ, [Limit], Result, Status
                if parts[-1].lower() in ('pass', 'fail', 'tested'):
                    status = parts[-1].lower()
                    value = _parse_number(parts[-2])
                    limit_val = _parse_number(parts[-3]) if len(parts) >= 4 else None
                    lod = _parse_number(parts[0]) if len(parts) >= 5 else None
                    loq = _parse_number(parts[1]) if len(parts) >= 5 else None
                    results.append({
                        'analysis': analysis_type,
                        'key': key,
                        'name': name,
                        'value': value,
                        'units': units,
                        'lod': lod,
                        'loq': loq,
                        'limit': limit_val,
                        'status': status,
                    })
            elif not has_limit and len(parts) >= 2:
                # Result, Status only (no LOD/LOQ/Limit).
                results.append({
                    'analysis': analysis_type,
                    'key': key,
                    'name': name,
                    'value': _parse_number(parts[0]),
                    'units': units,
                    'lod': None,
                    'loq': None,
                    'limit': None,
                    'status': parts[-1].lower() if parts[-1].lower() in ('pass', 'fail', 'tested') else '',
                })
        except (IndexError, ValueError):
            continue

    return results, method


def _parse_microbial_lines(lines: List[str]) -> Tuple[List[Dict], str]:
    """Parse microbial impurities results.

    Format: "Aspergillus flavus Not Detected in 1g Pass"
    """
    results = []
    method = ''
    in_section = False

    for line in lines:
        stripped = line.strip()

        if stripped == 'Microbial Impurities':
            in_section = True
            continue
        if not in_section:
            continue

        # Section end markers.
        if stripped.startswith('Date Tested:'):
            in_section = False
            continue
        if any(stripped == h for h in SECTION_HEADERS
               if h not in ('Microbial Impurities',)):
            break

        # Method line.
        if 'Method:' in stripped:
            method = stripped.split('Method:')[1].strip()
            continue

        if _should_skip_line(stripped):
            continue
        if stripped.startswith('Analytes'):
            continue

        # Parse microbial line.
        # Pattern: "Aspergillus flavus Not Detected in 1g Pass"
        status = ''
        if stripped.endswith('Pass'):
            status = 'pass'
            stripped = stripped[:-4].strip()
        elif stripped.endswith('Fail'):
            status = 'fail'
            stripped = stripped[:-4].strip()

        # Extract value.
        value = None
        if 'Not Detected' in stripped:
            value = None
            name = stripped.split('Not Detected')[0].strip()
        else:
            # Try to find numeric value.
            first_num = _find_first_number(stripped)
            if first_num < len(stripped):
                name = stripped[:first_num].strip()
                value = _parse_number(stripped[first_num:].split()[0])
            else:
                name = stripped
                value = None

        if not name or len(name) < 3:
            continue

        key = _snake_case(name)
        results.append({
            'analysis': 'microbials',
            'key': key,
            'name': name,
            'value': value,
            'units': 'cfu/g',
            'lod': None,
            'loq': None,
            'limit': None,
            'status': status,
        })

    return results, method


def _parse_terpene_lines(lines: List[str]) -> Tuple[List[Dict], str, Optional[float]]:
    """Parse terpene results from text lines.

    Format: "beta-Caryophyllene 0.084 0.257 1.054 10.54"
    Columns: Analyte LOD LOQ Result(%) Result(mg/g)

    Returns (results, method, total_terpenes).
    """
    results = []
    method = ''
    total_terpenes = None
    in_terpenes = False

    for line in lines:
        stripped = line.strip()

        if stripped == 'Terpenes':
            in_terpenes = True
            continue
        if not in_terpenes:
            continue

        # Section end markers.
        if stripped.startswith('Primary Aromas'):
            break
        if stripped.startswith('Date Tested:'):
            break
        if 'LOQ = Limit' in stripped:
            break
        if any(stripped == h for h in SECTION_HEADERS
               if h != 'Terpenes'):
            break

        # Method line.
        if 'Method:' in stripped:
            method = stripped.split('Method:')[1].strip()
            continue

        if _should_skip_line(stripped):
            continue
        if stripped.startswith('Analytes'):
            continue

        # Total line.
        if stripped.startswith('Total'):
            parts = stripped.split('Total')[1].strip().split()
            if parts:
                total_terpenes = _parse_number(parts[0])
            continue

        # Parse analyte line.
        first_num = _find_first_number(stripped)
        if first_num >= len(stripped):
            continue

        name = stripped[:first_num].strip()
        if not name or len(name) < 2:
            continue

        key = _snake_case(name)
        parts = stripped[first_num:].split()

        if len(parts) < 3:
            continue

        try:
            lod = _parse_number(parts[0])
            loq = _parse_number(parts[1])
            value = _parse_number(parts[2])  # % column

            result = {
                'analysis': 'terpenes',
                'key': key,
                'name': name,
                'value': value,
                'units': 'percent',
                'lod': lod,
                'loq': loq,
                'limit': None,
                'status': '',
            }

            # mg/g column if available.
            if len(parts) > 3:
                mg_g = _parse_number(parts[3])
                if mg_g is not None:
                    result['mg_g'] = mg_g

            results.append(result)
        except (IndexError, ValueError):
            continue

    return results, method, total_terpenes


# ── Main Parsing Function ─────────────────────────────────────────

def parse_encore_pdf(parser: Any, pdf_path: str, **kwargs) -> Dict:
    """Parse an Encore Labs COA PDF.

    This is the core parsing function that extracts all data from the
    PDF using pdfplumber text extraction and regex-based field parsing.

    Args:
        parser: Optional CoADoc instance (backwards compatibility).
        pdf_path: Path to the COA PDF file.

    Returns:
        Dict with all extracted COA data.
    """
    obs = {}

    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            raise ValueError(f'PDF has no pages: {pdf_path}')

        # ── Phase 1: Extract all text ─────────────────────────
        all_lines = []
        unique_lines = []
        seen = set()

        for page in pdf.pages:
            try:
                text = _clean_text(page.extract_text() or '')
            except Exception:
                continue
            for line in text.split('\n'):
                all_lines.append(line)
                if line not in seen:
                    unique_lines.append(line)
                    seen.add(line)

        if not all_lines:
            raise ValueError(f'No text extracted from PDF: {pdf_path}')

        # ── Phase 2: Parse lab header ─────────────────────────
        obs.update(_parse_lab_header(all_lines))

        # ── Phase 3: Parse product metadata ───────────────────
        obs.update(_parse_product_metadata(all_lines))

        # ── Phase 4: Parse entity columns (bbox) ─────────────
        try:
            entity_data = _parse_entity_columns(pdf.pages[0])
            obs.update(entity_data)
        except Exception:
            pass

        # ── Phase 5: Parse summary table ──────────────────────
        obs.update(_parse_summary_table(all_lines))

        # ── Phase 6: Parse summary totals ─────────────────────
        obs.update(_parse_summary_totals(all_lines))

        # ── Phase 7: Parse all results sections ───────────────
        all_results = []
        analyses = set()
        methods = []

        # Cannabinoids (from unique_lines to avoid duplicates).
        cann_results, cann_method = _parse_cannabinoid_lines(unique_lines)
        if cann_results:
            all_results.extend(cann_results)
            analyses.add('cannabinoids')
            if cann_method:
                methods.append(cann_method)

        # Terpenes.
        terp_results, terp_method, total_terp = _parse_terpene_lines(unique_lines)
        if terp_results:
            all_results.extend(terp_results)
            analyses.add('terpenes')
            if terp_method:
                methods.append(terp_method)
            if total_terp is not None:
                obs['total_terpenes'] = total_terp

        # Pesticides (from all_lines to capture both columns).
        pest_results, pest_method = _parse_pesticide_lines(unique_lines)
        if pest_results:
            all_results.extend(pest_results)
            analyses.add('pesticides')
            if pest_method:
                methods.append(pest_method)

        # Mycotoxins.
        myco_results, myco_method = _parse_standard_section_lines(
            unique_lines, 'Mycotoxins', 'mycotoxins', 'ug/kg',
        )
        if myco_results:
            all_results.extend(myco_results)
            analyses.add('mycotoxins')
            if myco_method:
                methods.append(myco_method)

        # Residual Solvents.
        solv_results, solv_method = _parse_standard_section_lines(
            unique_lines, 'Residual Solvents', 'residual_solvents', 'ug/g',
        )
        if solv_results:
            all_results.extend(solv_results)
            analyses.add('residual_solvents')
            if solv_method:
                methods.append(solv_method)

        # Microbial Impurities.
        micro_results, micro_method = _parse_microbial_lines(unique_lines)
        if micro_results:
            all_results.extend(micro_results)
            analyses.add('microbials')
            if micro_method:
                methods.append(micro_method)

        # Heavy Metals.
        metal_results, metal_method = _parse_standard_section_lines(
            unique_lines, 'Heavy Metals', 'heavy_metals', 'ug/g',
        )
        if metal_results:
            all_results.extend(metal_results)
            analyses.add('heavy_metals')
            if metal_method:
                methods.append(metal_method)

        # ── Phase 8: Extract moisture/water activity from text ──
        for line in unique_lines:
            if 'Moisture' in line and 'moisture_content' not in obs:
                match = re.search(r'(\d+\.?\d*)%', line)
                if match and 'Moisture Analyzer' in line:
                    obs['moisture_content'] = float(match.group(1))
            if 'Water Activity' in line and 'water_activity' not in obs:
                match = re.search(r'(\d+\.\d+)\s*aw', line)
                if match:
                    obs['water_activity'] = float(match.group(1))

        # ── Phase 9: Build final output ───────────────────────
        obs = {**ENCORE_LABS, **obs}
        obs['analyses'] = json.dumps(sorted(analyses))
        obs['methods'] = json.dumps(methods)
        obs['results'] = json.dumps(all_results)
        obs['coa_parsed_at'] = datetime.now().isoformat()

        # Generate results hash.
        hash_input = json.dumps(all_results, sort_keys=True)
        obs['results_hash'] = hashlib.sha256(
            hash_input.encode()).hexdigest()[:16]

        # Use lab's Sample ID as lab_id.
        obs['lab_id'] = obs.get('sample_id', '')

        # Generate sample_id hash if not already set.
        if not obs.get('sample_id'):
            id_input = (
                hash_input +
                obs.get('product_name', '') +
                obs.get('producer', '') +
                obs.get('date_tested', '')
            )
            obs['sample_id'] = hashlib.sha256(
                id_input.encode()).hexdigest()[:16]

        # PDF filename for reference.
        obs['coa_pdf'] = pdf_path.replace('\\', '/').split('/')[-1]

    return obs


# ── Entry Point (LAB_REGISTRY compatible) ─────────────────────────

def parse_encore_coa(
        parser: Any = None,
        doc: str = '',
        **kwargs,
    ) -> Dict:
    """Parse an Encore Labs COA PDF.

    This is the main entry point registered in the LAB_REGISTRY.
    For the hybrid engine, this always parses from the PDF directly.

    Args:
        parser: Optional CoADoc instance (backwards compatibility).
        doc:    Path to the COA PDF file.

    Returns:
        Dict with all extracted COA data.
    """
    # Handle argument order flexibility.
    if isinstance(parser, str) and not doc:
        doc = parser
        parser = None

    # For URLs, we cannot parse offline.
    if isinstance(doc, str) and doc.startswith('http'):
        raise ValueError(
            'URL parsing requires network access. '
            'Use the AI parser for URL-based COAs, or provide the PDF.'
        )

    return parse_encore_pdf(parser, doc, **kwargs)


def is_encore(pdf_path: str) -> bool:
    """Quick check if a PDF is an Encore Labs COA (without full parse).

    Args:
        pdf_path: Path to a PDF file.

    Returns:
        True if the PDF appears to be from Encore Labs.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return False
            text = (pdf.pages[0].extract_text() or '').lower()
            return (
                'encorelabs.com' in text
                or 'encore-labs.com' in text
                or 'encore labs' in text
            )
    except Exception:
        return False


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
            print('Usage: python encore.py <pdf_file> [pdf_file2 ...]')
            sys.exit(1)

    success = 0
    fail = 0
    total_analytes = 0
    for pdf_file in test_files:
        pdf_path = os.path.join(test_dir, pdf_file) \
            if not os.path.isabs(pdf_file) else pdf_file
        if not os.path.exists(pdf_path):
            print(f'Not found: {pdf_path}')
            continue
        try:
            data = parse_encore_coa(None, pdf_path)
            results = json.loads(data.get('results', '[]'))
            analyses = json.loads(data.get('analyses', '[]'))
            n_results = len(results)
            total_analytes += n_results
            print(f'\nOK {os.path.basename(pdf_file)}')
            print(f'  Product:     {data.get("product_name", "?")}')
            print(f'  Type:        {data.get("product_type", "?")} / {data.get("product_subtype", "?")}')
            print(f'  Producer:    {data.get("producer", "?")}')
            print(f'  Distributor: {data.get("distributor", "?")}')
            print(f'  Date:        {data.get("date_tested", "?")}')
            print(f'  THC:         {data.get("total_thc", "?")}')
            print(f'  CBD:         {data.get("total_cbd", "?")}')
            print(f'  Terpenes:    {data.get("total_terpenes", "?")}')
            print(f'  Status:      {data.get("status", "?")}')
            print(f'  Sample ID:   {data.get("sample_id", "?")}')
            print(f'  Batch#:      {data.get("batch_number", "?")}')
            print(f'  Analyses:    {analyses}')
            print(f'  Results:     {n_results} analytes')
            print(f'  Lab:         {data.get("lab", "?")} ({data.get("lab_license_number", "?")})')
            success += 1
        except Exception as e:
            print(f'\nFAIL {os.path.basename(pdf_file)}: {e}')
            import traceback
            traceback.print_exc()
            fail += 1

    print(f'\n{"="*60}')
    print(f'Results: {success} OK, {fail} FAIL out of {success + fail}')
    print(f'Total analytes extracted: {total_analytes}')
    if success > 0:
        print(f'Average analytes per COA: {total_analytes / success:.0f}')
