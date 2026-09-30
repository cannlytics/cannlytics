"""
Parse ACS Labs COAs — COA Doc Hybrid Algorithm
Copyright (c) 2023-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/18/2023
Updated: 3/8/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse ACS Laboratory COA PDFs directly from the PDF text — no
    network access required. This is the hybrid-engine version that
    extracts all data from the PDF itself using pdfplumber text and
    table extraction.

    ACS Laboratory (formerly ACS Labs) is a major cannabis testing
    laboratory based in Sun City Center, FL. They test products for
    MMTCs (Medical Marijuana Treatment Centers) across Florida and
    serve clients in multiple states.

    Identification:
        ACS COAs contain 'acslabcannabis.com' or 'acslab.com' URLs
        in the header area. The lab address is always:
            721 Cortaro Dr, Sun City Center, FL 33573

    Format variants handled:
        * Patient COA (1 page): Potency + terpene summary, no detail pages
        * Compliance Test (multi-page): Full panel with detail pages
        * Old format (2020-2021): "HPLC/LCMS", "License No. 800025015",
          "Sample Prepared By", "Terpineol" naming
        * Mid format (2022): "SOP13.001 (LCUV)", dry-weight reporting,
          "Prep. By" shorthand
        * New format (2023-2025): Refined LOQ values, "THCA-A" naming,
          "Orig. Completion Date", "Statement of Amendment"

Data Points:

    ✓ product_name, product_type, strain_name
    ✓ batch_number, traceability_id, lot_id
    ✓ sample_weight, product_size, units_per_package, total_products
    ✓ lab, lab_license_number, lab_address, lab_city, lab_state, lab_zipcode
    ✓ lab_phone, lab_email, lab_website
    ✓ producer, producer_address, producer_street, producer_city,
      producer_state, producer_zipcode
    ✓ distributor (production facility)
    ✓ date_collected, date_tested, date_received, date_harvested, date_packaged
    ✓ sample_id (Sample #), lab_id (Order #)
    ✓ total_thc, total_cbd, total_cannabinoids, total_terpenes
    ✓ status (overall pass/fail)
    ✓ analyses (list of analysis types)
    ✓ {analysis}_status for each analysis
    ✓ results: cannabinoids, terpenes, pesticides, heavy_metals, microbes,
      mycotoxins, residual_solvents, moisture, water_activity, foreign_matter
"""
# Standard imports:
import hashlib
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# External imports (pdfplumber only):
import pdfplumber


# ── ACS Labs Constants ─────────────────────────────────────────────

ACS_LABS = {
    'coa_algorithm': 'acs.py',
    'coa_algorithm_entry_point': 'parse_acs_coa',
    'lims': 'ACS Labs',
    'lab': 'ACS Laboratory',
    'lab_license_number': 'CMTL-0003',
    'lab_image_url': 'https://global-uploads.webflow.com/630470e960f8722190672cb4/6305a2e849811b34bf18777d_Desktop%20Logo.svg',
    'lab_address': '721 Cortaro Dr, Sun City Center, FL 33573',
    'lab_street': '721 Cortaro Dr',
    'lab_city': 'Sun City Center',
    'lab_county': 'Hillsborough County',
    'lab_state': 'FL',
    'lab_zipcode': '33573',
    'lab_phone': '813-634-4529',
    'lab_email': 'info@acslabcannabis.com',
    'lab_website': 'https://www.acslabcannabis.com/',
    'lab_latitude': 27.713506,
    'lab_longitude': -82.371029,
}

# Analysis name mappings from ACS badge/section labels.
ANALYSIS_MAP = {
    'potency': 'cannabinoids',
    'terpenes': 'terpenes',
    'pesticides': 'pesticides',
    'heavy metals': 'heavy_metals',
    'pathogenic': 'microbes',
    'pathogenic microbiology': 'microbes',
    'microbiology (qpcr)': 'microbes',
    'microbiology petrifilm': 'microbes',
    'mycotoxins': 'mycotoxins',
    'residual solvents': 'residual_solvents',
    'filth and foreign': 'foreign_matter',
    'total contaminant load': 'foreign_matter',
    'water activity': 'water_activity',
    'moisture': 'moisture',
}

# Metadata field regex patterns: (field_label, output_key, is_date).
METADATA_FIELDS = [
    ('Sample #', 'sample_id', False),
    ('Order #', 'lab_id', False),
    ('Batch #', 'batch_number', False),
    ('Batch Date', 'date_packaged', True),
    ('Seed to Sale #', 'traceability_id', False),
    ('Lot ?ID', 'lot_id', False),
    ('Cultivars', 'strain_name', False),
    ('Sampling Date', 'date_collected', True),
    ('Completion Date', 'date_tested', True),
    ('Orig. Completion Date', 'date_tested', True),
    ('Lab Batch Date', 'date_received', True),
    ('Order Date', 'date_received', True),
    ('Cultivation Date', 'date_harvested', True),
    ('Production Date', 'date_produced', True),
    ('Cultivation Facility', 'cultivation_facility', False),
    ('Production Facility', 'production_facility', False),
    ('Initial Gross Weight', 'sample_weight', False),
    ('Net Weight per Unit', 'product_size', False),
    ('Number of Units', 'units_per_package', False),
    ('Total Number of Final Products', 'total_products', False),
    ('Net Weight', 'net_weight', False),
    ('Test Reg State', 'producer_state', False),
    ('FL License #', 'lab_license_number', False),
    ('Sampling Method', 'sampling_method', False),
]

# Analyte key normalization for ACS-specific names.
ANALYTE_KEY_MAP = {
    'thca-a': 'thca',
    'thca': 'thca',
    'delta-9 thc': 'delta_9_thc',
    'delta-8 thc': 'delta_8_thc',
    'delta-10 thc': 'delta_10_thc',
    'delta6a10a-thc': 'delta_6a10a_thc',
    'cbda': 'cbda',
    'cbd': 'cbd',
    'cbga': 'cbga',
    'cbg': 'cbg',
    'cbna': 'cbna',
    'cbn': 'cbn',
    'cbc': 'cbc',
    'cbca': 'cbca',
    'cbdv': 'cbdv',
    'cbdva': 'cbdva',
    'thcv': 'thcv',
    'thcva': 'thcva',
    'cbl': 'cbl',
    'cbt': 'cbt',
    'cbe': 'cbe',
    'total active thc': 'total_thc',
    'total thc': 'total_thc',
    'total active cbd': 'total_cbd',
    'total cbd': 'total_cbd',
    # Terpenes
    'trans-caryophyllene': 'beta_caryophyllene',
    '(r)-(+)-limonene': 'd_limonene',
    'linalool': 'linalool',
    'beta-myrcene': 'beta_myrcene',
    'alpha-humulene': 'alpha_humulene',
    'alpha-bisabolol': 'alpha_bisabolol',
    'alpha-pinene': 'alpha_pinene',
    'beta-pinene': 'beta_pinene',
    'fenchyl alcohol': 'fenchol',
    'terpinolene': 'terpinolene',
    'total terpineol': 'terpineol',
    'terpineol': 'terpineol',
    'ocimene': 'ocimene',
    'farnesene': 'farnesene',
    'trans-nerolidol': 'trans_nerolidol',
    'cis-nerolidol': 'cis_nerolidol',
    'guaiol': 'guaiol',
    'valencene': 'valencene',
    'nerol': 'nerol',
    'geraniol': 'geraniol',
    'geranyl acetate': 'geranyl_acetate',
    'camphene': 'camphene',
    'eucalyptol': 'eucalyptol',
    'gamma-terpinene': 'gamma_terpinene',
    'alpha-terpinene': 'alpha_terpinene',
    'alpha-phellandrene': 'alpha_phellandrene',
    'alpha-cedrene': 'alpha_cedrene',
    '3-carene': 'delta_3_carene',
    'sabinene': 'sabinene',
    'sabinene hydrate': 'sabinene_hydrate',
    'pulegone': 'pulegone',
    'isopulegol': 'isopulegol',
    'isoborneol': 'isoborneol',
    'borneol': 'borneol',
    'fenchone': 'fenchone',
    'camphors': 'camphor',
    'caryophyllene oxide': 'caryophyllene_oxide',
    '(+)-cedrol': 'cedrol',
    'hexahydrothymol': 'hexahydrothymol',
    # Heavy metals
    'arsenic (as)': 'arsenic',
    'cadmium (cd)': 'cadmium',
    'lead (pb)': 'lead',
    'mercury (hg)': 'mercury',
    # Mycotoxins
    'aflatoxin b1': 'aflatoxin_b1',
    'aflatoxin b2': 'aflatoxin_b2',
    'aflatoxin g1': 'aflatoxin_g1',
    'aflatoxin g2': 'aflatoxin_g2',
    'ochratoxin a': 'ochratoxin_a',
    # Microbes
    'aspergillus (flavus, fumigatus, niger, terreus)': 'aspergillus',
    'aspergillus flavus': 'aspergillus_flavus',
    'aspergillus fumigatus': 'aspergillus_fumigatus',
    'aspergillus niger': 'aspergillus_niger',
    'aspergillus terreus': 'aspergillus_terreus',
    'e.coli': 'e_coli',
    'stec e. coli': 'stec_e_coli',
    'salmonella': 'salmonella',
    'total yeast/mold': 'total_yeast_mold',
    # Moisture / water activity
    'moisture': 'moisture',
    'water activity': 'water_activity',
    # Foreign matter
    'covered area': 'covered_area',
    'feces': 'feces',
    'weight %': 'weight_percent',
}


# ── Utility Functions ──────────────────────────────────────────────

def _snake_case(text: str) -> str:
    """Convert analyte name to standardized snake_case key."""
    if not text:
        return ''
    cleaned = text.strip().lower()
    # Try exact match first.
    if cleaned in ANALYTE_KEY_MAP:
        return ANALYTE_KEY_MAP[cleaned]
    # Normalize to snake_case.
    s = re.sub(r'[^a-z0-9]+', '_', cleaned)
    s = re.sub(r'_+', '_', s).strip('_')
    return s


def _parse_number(text: str) -> Optional[float]:
    """Parse a numeric value, returning None for ND/<LOQ/etc."""
    if not text or not isinstance(text, str):
        return None
    text = text.strip()
    if not text or text in ('-', 'ND', 'N/A', ''):
        return None
    upper = text.upper()
    if upper.startswith('<') or 'LOQ' in upper or 'LOD' in upper:
        return None
    if upper in ('NONE DETECTED', 'NONEDETECTED', 'NOT DETECTED',
                 'PASS', 'PASSED', 'FAIL', 'FAILED', 'NT',
                 'ABSENCE IN 1G', 'ABSENCE'):
        return None
    # Remove trailing units or percent signs.
    text = re.sub(r'\s*(%|mg/?g|ppm|ppb|aw|cfu/g|mg)\s*$', '', text,
                  flags=re.IGNORECASE).strip()
    # Remove commas in numbers.
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
    # Already ISO format.
    if re.match(r'^\d{4}-\d{2}-\d{2}$', text):
        return text
    # Handle 0000-00-00 (ACS sometimes uses this for unknown dates).
    if text == '0000-00-00':
        return ''
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%b %d, %Y'):
        try:
            return datetime.strptime(text, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return text


def _clean_text(text: str) -> str:
    """Clean common PDF extraction artifacts."""
    if not text:
        return ''
    # Fix null bytes and ligature issues.
    text = text.replace('\x00', 'fi')
    text = text.replace('\ufb01', 'fi')
    text = text.replace('\ufb02', 'fl')
    return text


def _rows_between(lines: List[str], start: str, stop: str,
                   inclusive_start: bool = False) -> List[str]:
    """Extract lines between a start and stop pattern.

    Args:
        lines:           List of text lines.
        start:           Start marker (matched at line start).
        stop:            Stop marker (matched at line start).
        inclusive_start:  If True, include the start line.

    Returns:
        List of lines between start and stop.
    """
    collecting = False
    result = []
    for line in lines:
        if not collecting and line.startswith(start):
            collecting = True
            if inclusive_start:
                result.append(line)
            continue
        if collecting:
            if line.startswith(stop):
                break
            result.append(line)
    return result


def _split_two_column_rows(elements: List[str],
                            split_words: List[str]) -> List[str]:
    """Split rows that contain two analytes merged by pdfplumber.

    ACS two-column layouts (heavy metals, foreign matter) often merge
    two analytes onto one extracted line. Split them at known boundaries.
    """
    result = []
    for element in elements:
        was_split = False
        for word in split_words:
            idx = element.find(word)
            if idx > 0:  # Split only if word is not at the start.
                left = element[:idx].strip()
                right = element[idx:].strip()
                if left:
                    result.append(left)
                if right:
                    result.append(right)
                was_split = True
                break
        if not was_split:
            result.append(element.strip())
    return [r for r in result if r]


def _find_first_numeric(text: str) -> int:
    """Find the index of the first numeric value in a string.

    Used to split 'Analyte Name 150.000 3.20E-5 ...' into name and values.
    """
    match = re.search(r'(?<!\w)(\d+\.\d+|<LOQ|<LOD|\d+E[+-]?\d+)', text)
    if match:
        return match.start()
    # Fallback: find first digit after a space.
    match = re.search(r'\s(\d)', text)
    if match:
        return match.start() + 1
    return len(text)


# ── Metadata Extraction ────────────────────────────────────────────

def _extract_product_name(page_text: str, lines: List[str]) -> str:
    """Extract the product name from the top-right header area.

    ACS COAs have the product name in the top-right corner,
    typically on the first or second line of the right-side header.
    Format examples:
        'AL-Flower-3.5g-Xeno-H-FL'
        'CNC-Flower-3.5g-Glt#41-H-FL'
        'TruClearSyringe850mg-CO2-GooBerry'
    """
    # Look for the product name pattern in the first few lines.
    # It's usually in the top-right and appears before "Sample Matrix:".
    for line in lines[:5]:
        line = line.strip()
        # Skip lab header lines.
        if any(skip in line for skip in [
            '721 Cortaro', 'Sun City', 'www.acs', 'DEA No',
            'FL License', 'CLIA No', 'License No', 'CANNABIS & HEMP',
            'BEYOND COMPLIANCE',
        ]):
            continue
        # Product name lines are typically alphanumeric with dashes.
        if line and len(line) > 3 and not line.startswith('Certificate'):
            return line
    return ''


def _extract_product_type(page_text: str) -> str:
    """Extract the product type / sample matrix from the header.

    The sample matrix appears in the top-right, e.g.:
        'CANNABIS (MMTC's) Flower & Plants (Inhalation - Heated)'
    """
    match = re.search(
        r'Sample\s+Matrix:\s*\n?(.*?)(?:\nCertificate|\nPatient|\nCompliance)',
        page_text, re.DOTALL
    )
    if match:
        raw = match.group(1).strip()
        # Clean up multiline extraction.
        parts = [p.strip() for p in raw.split('\n') if p.strip()]
        # Filter out address / lab info lines that may bleed in.
        filtered = [p for p in parts
                    if not any(skip in p for skip in [
                        '721 Cortaro', 'Sun City', 'www.acs', 'DEA No',
                        'FL License', 'CLIA No', 'License No',
                    ])]
        return ' '.join(filtered) if filtered else ' '.join(parts)
    return ''


def _extract_metadata(page_text: str) -> Dict:
    """Extract all metadata fields using regex patterns."""
    obs = {}
    for field_label, output_key, is_date in METADATA_FIELDS:
        if is_date:
            # Date fields: capture YYYY-MM-DD after the label.
            pattern = rf'(?<!Lab ){field_label}:\s*(\d{{4}}-\d{{2}}-\d{{2}})'
            match = re.search(pattern, page_text)
            if match:
                val = _parse_date(match.group(1))
                if val and (output_key not in obs or not obs[output_key]):
                    obs[output_key] = val
        else:
            # Non-date fields: capture value, avoiding Lab Batch # matches.
            # Use negative lookbehind to skip "Lab Batch #" when matching "Batch #".
            if field_label == 'Batch #':
                pattern = r'(?<!Lab )Batch\s*#\s*(\S+)'
            elif field_label == 'Sample #':
                pattern = r'Sample\s*#\s*(\S+)'
            elif field_label == 'Order #':
                pattern = r'Order\s*#\s*(\S+)'
            else:
                pattern = rf'{field_label}:\s*(.+?)(?:\n|$)'

            match = re.search(pattern, page_text)
            if match:
                val = match.group(1).strip()
                # For short-capture patterns (Batch/Sample/Order #),
                # we already have just the ID value.
                if field_label in ('Batch #', 'Sample #', 'Order #'):
                    if val and (output_key not in obs or not obs[output_key]):
                        obs[output_key] = val
                    continue

                # Truncate at next field label if present.
                for other_label, _, _ in METADATA_FIELDS:
                    if other_label != field_label and other_label + ':' in val:
                        val = val[:val.index(other_label + ':')].strip()
                        break
                # Also truncate at common next-field patterns.
                for cutoff in ['Cultivation Facility:', 'Production Facility:',
                               'Cultivation Date:', 'Production Date:',
                               'Test Reg State:', 'Sampling Date:',
                               'Lab Batch Date:', 'Number of Units:',
                               'Net Weight per Unit:', 'Sampling Method:']:
                    if cutoff in val:
                        val = val[:val.index(cutoff)].strip()
                if val and (output_key not in obs or not obs[output_key]):
                    obs[output_key] = val
    return obs


def _extract_client_info(page, page_text: str) -> Dict:
    """Extract client/producer information from the left header area."""
    obs = {}
    try:
        # Try to get the client info block.
        # Pattern: after "CLIA No." or "Certificate of Analysis" header
        # and before "Order #" or "Batch #"
        patterns = [
            # "ClientInformation:" block (newer format).
            r'(?:Client\s*Information:|Patient\s*COA|Compliance\s*Test)\s*\n(.+?)\n(.+?)\n(.+?)(?:\n|$)',
            # Direct after CLIA line.
            r'CLIA No[.\s]+\S+\s*\n(.+?)\n(.+?)\n(.+?)(?:\n|$)',
        ]
        # Try bbox-based extraction for the client info area.
        top_left = page.within_bbox((0, 0, page.width * 0.3, page.height * 0.25))
        top_left_text = _clean_text(top_left.extract_text() or '')
        top_left_lines = top_left_text.split('\n')

        # Find the client block: starts after CLIA/license line, ends before Order/Batch.
        client_lines = []
        collecting = False
        for line in top_left_lines:
            line = line.strip()
            if not collecting:
                if ('CLIA No' in line or 'Certificate of Analysis' in line
                        or 'Patient COA' in line or 'Compliance Test' in line
                        or 'PatientCOA' in line):
                    collecting = True
                    continue
            else:
                if line.startswith('Order #') or line.startswith('Order Date'):
                    break
                if line.startswith('Batch #') or line.startswith('Batch Date'):
                    break
                if line and not line.startswith('Client'):
                    client_lines.append(line)

        if len(client_lines) >= 3:
            # First line: producer name (may have * or - suffix).
            producer = client_lines[0].strip()
            producer = re.sub(r'\s*[\*\-]+\s*$', '', producer).strip()
            # Remove partial "Bat" or "Batch" suffix from bbox clipping.
            producer = re.sub(r'\s+Bat(?:ch)?\.?$', '', producer).strip()
            # Remove trailing asterisks/special chars that remain.
            producer = producer.rstrip(' *-')
            obs['producer'] = producer
            obs['producer_street'] = client_lines[1].strip()
            # Last line: "City, ST ZIPCODE"
            addr_line = client_lines[-1].strip()
            addr_match = re.match(
                r'^(.+?),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$', addr_line
            )
            if addr_match:
                obs['producer_city'] = addr_match.group(1).strip()
                obs['producer_state'] = addr_match.group(2)
                obs['producer_zipcode'] = addr_match.group(3)
                obs['producer_address'] = f"{client_lines[1].strip()}, {addr_line}"
        elif len(client_lines) >= 1:
            producer = re.sub(
                r'\s*[\*\-]+\s*$', '', client_lines[0]
            ).strip()
            producer = re.sub(r'\s+Bat(?:ch)?\.?$', '', producer).strip()
            obs['producer'] = producer
    except Exception:
        pass
    return obs


# ── Analysis Status Extraction ─────────────────────────────────────

def _extract_analysis_statuses(page_text: str) -> Tuple[List[str], Dict, str]:
    """Extract analysis types and their pass/fail statuses from the
    status badge area on page 1.

    Returns:
        (analyses, statuses_dict, overall_status)
    """
    analyses = set()
    statuses = {}
    overall_status = 'Pass'

    # The badge area contains pairs like:
    #   "Potency\nTested" or "Heavy Metals\nPassed" or "Residual Solvents\nNot Tested"
    # We parse these using regex for known analysis names.
    badge_patterns = [
        (r'Potency\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'cannabinoids'),
        (r'Terpenes\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'terpenes'),
        (r'Heavy\s+Metals\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'heavy_metals'),
        (r'Mycotoxins\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'mycotoxins'),
        (r'Pesticides\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'pesticides'),
        (r'Residual\s+Solvents\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'residual_solvents'),
        (r'Moisture\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'moisture'),
        (r'Water\s+Activity\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'water_activity'),
        (r'Pathogenic\s*(?:\s+Microbiology)?\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'microbes'),
        (r'Microbiology\s*\(?\s*q?PCR\s*\)?\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'microbes'),
        (r'Microbiology\s+Petrifilm\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'microbes'),
        (r'Filth\s+and\s+Foreign\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'foreign_matter'),
        (r'Total\s+Contaminant\s*\n?\s*Load\s*\n?\s*(Tested|Passed|Failed|Not Tested)', 'foreign_matter'),
    ]
    for pattern, analysis in badge_patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            raw_status = match.group(1).strip()
            status = raw_status.replace('Passed', 'Pass').replace('Failed', 'Fail')
            if raw_status.lower() == 'not tested':
                status = 'Not Tested'
            else:
                analyses.add(analysis)
            statuses[f'{analysis}_status'] = status
            if 'fail' in status.lower():
                overall_status = 'Fail'

    return sorted(analyses), statuses, overall_status


# ── Potency / Summary Extraction (Page 1) ──────────────────────────

def _extract_potency_summary(page) -> Dict:
    """Extract total THC, CBD, CBG, CBN, cannabinoids, and terpenes
    from the Potency Summary and Terpenes Summary boxes on page 1.

    ACS layout (right-side summary):
        Line N:   'Total Active THC Total Active CBD'
        Line N+1: '29.172% 1,040.478 mg 0.070% 2.488 mg'
        Line N+2: 'Total CBG Total CBN'
        Line N+3: '1.162% 41.447 mg - None Detected'
        Line N+4: 'Other Cannabinoids Total Cannabinoids'
        Line N+5: '4.182% 149.144 mg 34.586% 1,233.557 mg'
    """
    obs = {}
    try:
        crop = page.within_bbox((
            page.width * 0.5, page.height * 0.3,
            page.width, page.height * 0.85
        ))
        text = _clean_text(crop.extract_text() or '')
        lines = text.split('\n')

        for i, line in enumerate(lines):
            # Stop at the definitions/footer area to avoid false matches.
            if any(stop in line for stop in [
                'Definitions and Abbreviations',
                'Detailed Terpenes Analysis',
                'This report shall not',
                'Total Contaminant Load (TCL)',
                'Denitions and Abbreviations',  # fi-ligature garbled
            ]):
                break

            next_line = lines[i + 1] if i + 1 < len(lines) else ''

            # THC and CBD on the same header line, values on next line.
            # "Total Active THC Total Active CBD" / "29.172% 1,040.478 mg 0.070% 2.488 mg"
            # OR "Total THC Total CBD" (older format)
            if ('Total Active THC' in line or 'Total THC' in line) and i + 1 < len(lines):
                val_line = next_line.replace('None Detected', 'ND').replace('Not Detected', 'ND').replace('NoneDetected', 'ND')
                # Extract all percentage-like values from the value line.
                pct_values = re.findall(r'([\d.]+)\s*%', val_line)
                nd_values = re.findall(r'(ND|-)\s', val_line + ' ')

                if pct_values:
                    obs['total_thc'] = _parse_number(pct_values[0])
                # CBD is typically the second percentage or ND.
                if len(pct_values) >= 2:
                    obs['total_cbd'] = _parse_number(pct_values[1])
                elif 'Total Active CBD' in line or 'Total CBD' in line:
                    # Check if CBD part is ND.
                    parts = val_line.split('mg')
                    if len(parts) >= 2:
                        cbd_part = parts[-1].strip()  # After THC mg value
                        cbd_pct = re.search(r'([\d.]+)\s*%', cbd_part)
                        if cbd_pct:
                            obs['total_cbd'] = _parse_number(cbd_pct.group(1))
                        elif 'ND' in cbd_part or '-' == cbd_part.strip():
                            obs['total_cbd'] = None

            # Total Cannabinoids.
            # "Other Cannabinoids Total Cannabinoids" / "4.182% ... 34.586% ..."
            if 'Total Cannabinoids' in line and 'Other' in line and i + 1 < len(lines):
                val_line = next_line.replace('None Detected', 'ND').replace('NoneDetected', 'ND')
                pct_values = re.findall(r'([\d.]+)\s*%', val_line)
                if len(pct_values) >= 2:
                    obs['total_cannabinoids'] = _parse_number(pct_values[-1])
                elif pct_values:
                    obs['total_cannabinoids'] = _parse_number(pct_values[0])
            # Also handle standalone "Total Cannabinoids" header (older format).
            elif line.strip().startswith('Total Cannabinoids') and 'Other' not in line:
                # "30.3% 1070 mg" on same line or next.
                cann_match = re.search(r'([\d.]+)\s*%', line + ' ' + next_line)
                if cann_match:
                    obs['total_cannabinoids'] = _parse_number(cann_match.group(1))

            # Total Terpenes.
            if 'Total Terpenes' in line:
                terp_match = re.search(r'Total\s+Terpenes:?\s*([\d.]+)\s*%?', line)
                if terp_match:
                    obs['total_terpenes'] = _parse_number(terp_match.group(1))

    except Exception:
        pass
    return obs


def _extract_cannabinoids_page1(page, page_text: str) -> List[Dict]:
    """Extract cannabinoid results from the potency table on page 1.

    The potency table is in the left half, roughly 35-80% down the page.
    Columns: Analyte | Dilution | LOD | LOQ | Result(mg/g) | (%)
    """
    results = []
    try:
        # Crop to the potency table area (left side).
        crop = page.within_bbox((
            0, page.height * 0.35,
            page.width * 0.52, page.height * 0.82
        ))
        text = _clean_text(crop.extract_text() or '')
        lines = text.split('\n')

        # Find the data rows between the header and the prep/review line.
        data_lines = _rows_between(
            lines,
            start='Analyte',
            stop='Prep. By',
        )
        if not data_lines:
            data_lines = _rows_between(
                lines,
                start='Analyte',
                stop='Sample Prepared By',
            )
        if not data_lines:
            data_lines = _rows_between(
                lines,
                start='Analyte',
                stop='Total Active',
            )

        for line in data_lines:
            line = line.strip()
            if not line or line.startswith('(') or line.startswith('Dilution'):
                continue
            # Skip summary rows.
            if any(line.startswith(s) for s in [
                'Total Active', 'Total THC', 'Total CBD',
            ]):
                continue

            # Split analyte name from values.
            idx = _find_first_numeric(line)
            if idx >= len(line):
                continue
            name = line[:idx].strip()
            values_str = line[idx:].strip()
            if not name or len(name) < 2:
                continue

            values = values_str.split()
            if len(values) < 3:
                continue

            key = _snake_case(name)
            result = {
                'analysis': 'cannabinoids',
                'key': key,
                'name': name,
                'value': None,
                'units': 'percent',
                'limit': None,
                'lod': None,
                'loq': None,
                'status': '',
            }

            # Parse based on value count.
            # Typical: Dilution LOD LOQ Result(mg/g) (%)
            # Or:      Dilution LOD LOQ <LOQ <LOQ
            result_pct = _parse_number(values[-1])
            result_mg = _parse_number(values[-2]) if len(values) >= 4 else None

            result['value'] = result_pct
            if result_mg is not None:
                result['mg_g'] = result_mg
            if len(values) >= 4:
                result['loq'] = _parse_number(values[2])
            if len(values) >= 3:
                result['lod'] = _parse_number(values[1])

            results.append(result)

    except Exception:
        pass
    return results


def _extract_terpene_summary_page1(page, page_text: str) -> List[Dict]:
    """Extract terpene summary results from page 1 (Patient COAs).

    Patient COAs have a terpene summary in the right-side area
    with columns: Analyte | Result (mg/g) | (%)
    """
    results = []
    if 'Patient COA' not in page_text and 'PatientCOA' not in page_text:
        return results

    try:
        crop = page.within_bbox((
            page.width * 0.5, page.height * 0.45,
            page.width, page.height * 0.85
        ))
        text = _clean_text(crop.extract_text() or '')
        lines = text.split('\n')

        data_lines = _rows_between(
            lines,
            start='Analyte',
            stop='Total Terpenes',
        )

        for line in data_lines:
            line = line.strip()
            if not line or line.startswith('Result') or 'mg/g' in line:
                continue

            idx = _find_first_numeric(line)
            if idx >= len(line):
                continue
            name = line[:idx].strip()
            values_str = line[idx:].strip()
            if not name:
                continue

            values = values_str.split()
            key = _snake_case(name)

            mg_g = _parse_number(values[0]) if values else None
            pct = _parse_number(values[-1].rstrip('%')) if values else None

            results.append({
                'analysis': 'terpenes',
                'key': key,
                'name': name,
                'value': pct,
                'mg_g': mg_g,
                'units': 'percent',
                'limit': None,
                'lod': None,
                'loq': None,
                'status': '',
            })

    except Exception:
        pass
    return results


def _extract_moisture_page1(page, page_text: str) -> List[Dict]:
    """Extract moisture results from page 1 (when present)."""
    results = []
    if 'Moisture' not in page_text:
        return results

    try:
        crop = page.within_bbox((
            0, page.height * 0.7,
            page.width * 0.52, page.height * 0.95
        ))
        text = _clean_text(crop.extract_text() or '')
        lines = text.split('\n')

        for line in lines:
            if line.strip().startswith('Moisture') and re.search(r'\d', line):
                values = line.strip().split()
                if len(values) >= 3:
                    # "Moisture 15 12.710"
                    limit = _parse_number(values[1])
                    value = _parse_number(values[-1])
                    results.append({
                        'analysis': 'moisture',
                        'key': 'moisture',
                        'name': 'Moisture',
                        'value': value,
                        'units': 'percent',
                        'limit': limit,
                        'lod': None,
                        'loq': None,
                        'status': '',
                    })
                    break
    except Exception:
        pass
    return results


# ── Multi-Page Result Extraction ───────────────────────────────────

def _get_page_rows(page) -> Tuple[str, List[str]]:
    """Extract text and rows from a page using left/right bbox split.

    ACS multi-page COAs use a two-column layout. We extract text
    from the left and right halves separately to avoid column merging.
    """
    page_text = _clean_text(page.extract_text() or '')
    try:
        left = page.within_bbox((0, 0, page.width * 0.52, page.height))
        right = page.within_bbox((page.width * 0.48, 0, page.width, page.height))
        rows = (_clean_text(left.extract_text() or '').split('\n') +
                _clean_text(right.extract_text() or '').split('\n'))
    except Exception:
        rows = page_text.split('\n')
    return page_text, rows


def _extract_terpenes(page, page_text: str, rows: List[str],
                       already_collected: set) -> List[Dict]:
    """Extract detailed terpene results from a subsequent page."""
    results = []
    if 'Terpenes' not in page_text:
        return results

    # Find terpene data rows.
    data_lines = _rows_between(
        rows,
        start='Analyte',
        stop='Sample Prepared By',
    )
    if not data_lines:
        data_lines = _rows_between(
            rows,
            start='Analyte',
            stop='Prep. By',
        )
    if not data_lines:
        # Try: first set ends at Prep, second set starts at next Analyte.
        set1 = _rows_between(rows, start='Analyte', stop='Prep. By')
        remaining = rows[rows.index('Prep. By') + 1:] if 'Prep. By' in rows else []
        set2 = _rows_between(remaining, start='Analyte', stop='Analyzed By')
        data_lines = set1 + set2

    for line in data_lines:
        line = line.strip()
        if not line or line.startswith('(') or 'Dilution' in line:
            continue
        if line.startswith('Total Terpenes'):
            continue

        idx = _find_first_numeric(line)
        if idx >= len(line):
            continue
        name = line[:idx].strip()
        values_str = line[idx:].strip()
        if not name or len(name) < 2:
            continue

        key = _snake_case(name)
        if key in already_collected:
            continue

        values = values_str.split()
        # Terpene columns: Dilution | LOQ | Result(mg/g) | (%)
        pct = _parse_number(values[-1]) if values else None
        mg_g = _parse_number(values[-2]) if len(values) >= 2 else None

        loq = None
        if len(values) >= 3:
            loq = _parse_number(values[1])

        results.append({
            'analysis': 'terpenes',
            'key': key,
            'name': name,
            'value': pct,
            'mg_g': mg_g,
            'units': 'percent',
            'limit': None,
            'lod': None,
            'loq': loq,
            'status': '',
        })

    return results


def _extract_heavy_metals(page, page_text: str, rows: List[str]) -> List[Dict]:
    """Extract heavy metals results."""
    results = []
    if 'Arsenic' not in page_text:
        return results

    # Find the heavy metals section.
    section = _rows_between(rows, start='Heavy Metals', stop='Batch Reviewed')
    if not section:
        section = _rows_between(rows, start='Analyte', stop='Batch Reviewed')
    data_lines = _rows_between(
        section, start='Analyte', stop='Prep. By'
    )
    if not data_lines:
        data_lines = _rows_between(
            section, start='Analyte', stop='Sample Prepared By'
        )

    # Heavy metals come in pairs on the same line (Arsenic/Cadmium, Lead/Mercury).
    data_lines = _split_two_column_rows(data_lines, ['Lead', 'Mercury'])

    for line in data_lines:
        line = line.strip()
        if not line or 'LOQ' in line or 'LOD' in line or 'Action' in line:
            continue
        if '(ppb)' in line or 'Dilution' in line:
            continue

        idx = _find_first_numeric(line)
        if idx >= len(line):
            continue
        name = line[:idx].strip()
        values_str = line[idx:].strip()
        if not name or len(name) < 2:
            continue

        key = _snake_case(name)
        values = values_str.split()

        # Columns vary:
        # Old: LOQ | Action Level | Result  (3 values)
        # New: LOD | LOQ | Action Level | Result  (4+ values)
        value = _parse_number(values[-1]) if values else None
        limit = None
        lod = None
        loq = None

        if len(values) >= 4:
            lod = _parse_number(values[0])
            loq = _parse_number(values[1])
            limit = _parse_number(values[2])
        elif len(values) >= 3:
            loq = _parse_number(values[0])
            limit = _parse_number(values[1])

        results.append({
            'analysis': 'heavy_metals',
            'key': key,
            'name': name,
            'value': value,
            'units': 'ppb',
            'limit': limit,
            'lod': lod,
            'loq': loq,
            'status': '',
        })

    return results


def _extract_mycotoxins(page, page_text: str, rows: List[str]) -> List[Dict]:
    """Extract mycotoxin results."""
    results = []
    if 'Mycotoxins' not in page_text:
        return results

    section = _rows_between(rows, start='Mycotoxins', stop='Batch Reviewed')
    data_lines = _rows_between(
        section, start='Analyte', stop='Prep. By'
    )
    if not data_lines:
        data_lines = _rows_between(
            section, start='Analyte', stop='Sample Prepared By'
        )

    # Mycotoxins often have two columns merged.
    data_lines = _split_two_column_rows(
        data_lines, ['Aflatoxin G', 'Aflatoxin B', 'Ochratoxin']
    )

    for line in data_lines:
        line = line.strip()
        if not line or 'LOQ' in line and 'Action' in line:
            continue
        if '(ppb)' in line or 'Dilution' in line:
            continue

        idx = _find_first_numeric(line)
        if idx >= len(line):
            continue
        name = line[:idx].strip()
        values_str = line[idx:].strip()
        if not name or len(name) < 3:
            continue

        key = _snake_case(name)
        values = values_str.split()

        # Columns: Dilution | LOD? | LOQ | Action Level | Result
        value = _parse_number(values[-1]) if values else None
        limit = _parse_number(values[-2]) if len(values) >= 2 else None
        loq = _parse_number(values[-3]) if len(values) >= 3 else None
        lod = _parse_number(values[-4]) if len(values) >= 4 else None

        results.append({
            'analysis': 'mycotoxins',
            'key': key,
            'name': name,
            'value': value,
            'units': 'ppb',
            'limit': limit,
            'lod': lod,
            'loq': loq,
            'status': '',
        })

    return results


def _extract_pesticides(page, page_text: str) -> List[Dict]:
    """Extract pesticide results from the two-column layout."""
    results = []
    if 'Pesticides' not in page_text:
        return results

    try:
        # Pesticides are in a wide two-column table.
        # Try to extract using bbox columns.
        # Left column: ~0-50% width, Right column: ~50-100% width.
        for crop_bounds in [
            # New format: wider left column with LOD.
            [(0, 0, page.width * 0.5, page.height),
             (page.width * 0.5, 0, page.width, page.height)],
            # Old format: narrower columns.
            [(0, 0, page.width * 0.27, page.height),
             (page.width * 0.27, 0, page.width * 0.5, page.height)],
        ]:
            all_lines = []
            for bounds in crop_bounds:
                crop = page.within_bbox(bounds)
                text = _clean_text(crop.extract_text() or '')
                all_lines.extend(text.split('\n'))

            # Get data rows.
            set1 = _rows_between(
                all_lines, start='Analyte', stop='Sample Prepared By'
            )
            if not set1:
                set1 = _rows_between(
                    all_lines, start='Analyte', stop='Prep. By'
                )
            # Check for second column header.
            remaining_after_first_stop = []
            for j, line in enumerate(all_lines):
                if ('Sample Prepared By' in line or 'Prep. By' in line) and j > 5:
                    remaining_after_first_stop = all_lines[j + 1:]
                    break
            set2 = _rows_between(
                remaining_after_first_stop,
                start='Analyte',
                stop='Sample Analyzed By'
            )
            if not set2:
                set2 = _rows_between(
                    remaining_after_first_stop,
                    start='Analyte',
                    stop='Analyzed By'
                )
            data_lines = [x for x in set1 + set2
                         if x.strip() and len(x.split()) > 1
                         and '(ppb)' not in x and 'Dilution' not in x
                         and 'LOQ' not in x.split()[0]]

            if data_lines:
                break
        else:
            data_lines = []

        for line in data_lines:
            line = line.strip()
            if not line:
                continue

            idx = _find_first_numeric(line)
            if idx >= len(line):
                continue
            name = line[:idx].strip()
            values_str = line[idx:].strip()
            if not name or len(name) < 3:
                continue

            key = _snake_case(name)
            values = values_str.split()
            if len(values) < 3:
                continue

            # Columns: Dilution | LOD? | LOQ | Action Level | Result
            value = _parse_number(values[-1])
            limit = _parse_number(values[-2]) if len(values) >= 3 else None
            loq = _parse_number(values[-3]) if len(values) >= 4 else None

            results.append({
                'analysis': 'pesticides',
                'key': key,
                'name': name,
                'value': value,
                'units': 'ppb',
                'limit': limit,
                'lod': None,
                'loq': loq,
                'status': '',
            })

    except Exception:
        pass
    return results


def _extract_residual_solvents(page, page_text: str) -> List[Dict]:
    """Extract residual solvent results from the two-column layout."""
    results = []
    if 'Residual Solvents' not in page_text:
        return results

    try:
        # Residual solvents are in a two-column table, similar to pesticides.
        # Try bbox extraction.
        all_lines = []
        for bounds in [
            (page.width * 0.5, 0, page.width * 0.72, page.height),
            (page.width * 0.71, 0, page.width, page.height),
        ]:
            try:
                crop = page.within_bbox(bounds)
                text = _clean_text(crop.extract_text() or '')
                all_lines.extend(text.split('\n'))
            except Exception:
                pass

        if not all_lines:
            # Fallback: use full page text.
            all_lines = _clean_text(page_text).split('\n')

        # Get data rows.
        elements = _rows_between(
            all_lines, start='Analyte', stop='Lab Batch #'
        )
        set1 = _rows_between(elements, stop='Sample Prepared By')
        if not set1:
            set1 = _rows_between(elements, stop='Prep. By')
        remaining = elements[len(set1) + 1:] if set1 else elements
        set2 = _rows_between(
            remaining, start='Analyte', stop='Sample Analyzed By'
        )
        if not set2:
            set2 = _rows_between(remaining, start='Analyte', stop='Analyzed By')

        data_lines = [x for x in set1 + set2
                     if x.strip() and len(x.split()) > 1]

        for line in data_lines:
            line = line.strip()
            if not line or '(ppm)' in line or 'Dilution' in line:
                continue

            # Handle special case: "1,1-Dichloroethene" or "1,2-Dichloroethane"
            if line.startswith('1,'):
                line = re.sub(r'^(1,\d+)-\s+', r'\1-', line)

            idx = _find_first_numeric(line)
            if idx >= len(line):
                continue
            name = line[:idx].strip()
            values_str = line[idx:].strip()
            if not name or len(name) < 2:
                continue

            key = _snake_case(name)
            values = values_str.split()

            # Columns: Dilution | LOQ | Action Level | Result
            value = _parse_number(values[-1])
            limit = _parse_number(values[-2]) if len(values) >= 3 else None
            loq = _parse_number(values[-3]) if len(values) >= 4 else None

            results.append({
                'analysis': 'residual_solvents',
                'key': key,
                'name': name,
                'value': value,
                'units': 'ppm',
                'limit': limit,
                'lod': None,
                'loq': loq,
                'status': '',
            })

    except Exception:
        pass
    return results


def _extract_microbes(page, page_text: str, rows: List[str]) -> List[Dict]:
    """Extract pathogenic microbiology results."""
    results = []
    if 'Pathogenic' not in page_text:
        return results

    # Find the pathogenic section.
    section = _rows_between(rows, start='Pathogenic', stop='Batch Reviewed')
    if not section:
        section = _rows_between(rows, start='Pathogenic', stop='Reviewed By')
    data_lines = _rows_between(
        section, start='Analyte', stop='Prep. By'
    )
    if not data_lines:
        data_lines = _rows_between(
            section, start='Analyte', stop='Sample Prepared By'
        )

    # Clean and split merged lines.
    cleaned = []
    for line in data_lines:
        line = _clean_text(line)
        if not line.strip() or len(line.split()) < 2:
            continue
        cleaned.append(line)

    cleaned = _split_two_column_rows(
        cleaned, ['Aspergillus terreus', 'Aspergillus niger',
                   'Aspergillus fumigatus', 'Salmonella', 'STEC']
    )

    for line in cleaned:
        line = line.strip()
        # Normalize absence values.
        line = re.sub(r'Absence\s+in\s+1\s*g', 'ND', line)
        line = line.replace('Absence', 'ND')

        # Find where the name ends and values begin.
        idx = _find_first_numeric(line)
        # For microbes, values might just be "1 ND" or "1 Absence in 1g"
        parts = line.rsplit(None, 2)
        if len(parts) < 2:
            continue

        # Try regex for "Name Limit Result" pattern.
        match = re.match(r'^(.+?)\s+(\d+)\s+(.+)$', line)
        if match:
            name = match.group(1).strip()
            limit_str = match.group(2).strip()
            result_str = match.group(3).strip()
        else:
            continue

        key = _snake_case(name)
        value = _parse_number(result_str)
        limit = _parse_number(limit_str)

        results.append({
            'analysis': 'microbes',
            'key': key,
            'name': name,
            'value': value,
            'units': 'cfu/g',
            'limit': limit,
            'lod': None,
            'loq': None,
            'status': 'Pass' if result_str.upper() == 'ND' else '',
        })

    return results


def _extract_moisture(page_text: str, rows: List[str]) -> List[Dict]:
    """Extract moisture content from a subsequent page."""
    results = []
    if 'Moisture' not in page_text:
        return results

    for row in rows:
        row = row.strip()
        if row.startswith('Moisture') and re.search(r'\d+\.\d+', row):
            values = row.split()
            if len(values) >= 3:
                limit = _parse_number(values[1])
                value = _parse_number(values[-1])
                results.append({
                    'analysis': 'moisture',
                    'key': 'moisture',
                    'name': 'Moisture',
                    'value': value,
                    'units': 'percent',
                    'limit': limit,
                    'lod': None,
                    'loq': None,
                    'status': '',
                })
                break

    return results


def _extract_water_activity(page_text: str, rows: List[str]) -> List[Dict]:
    """Extract water activity from a subsequent page."""
    results = []
    if 'Water Activity' not in page_text:
        return results

    for row in rows:
        row = row.strip()
        if row.startswith('Water Activity') and re.search(r'\d+\.\d+', row):
            values = row.split()
            if len(values) >= 3:
                limit = _parse_number(values[-2])
                value = _parse_number(values[-1])
                results.append({
                    'analysis': 'water_activity',
                    'key': 'water_activity',
                    'name': 'Water Activity',
                    'value': value,
                    'units': 'aw',
                    'limit': limit,
                    'lod': None,
                    'loq': None,
                    'status': '',
                })
                break

    return results


def _extract_foreign_matter(page_text: str, rows: List[str]) -> List[Dict]:
    """Extract filth and foreign material results."""
    results = []
    if 'Filth and Foreign' not in page_text:
        return results

    section = _rows_between(rows, start='Filth and Foreign', stop='Batch Reviewed')
    if not section:
        section = _rows_between(rows, start='Filth and Foreign', stop='Reviewed By')
    data_lines = _rows_between(
        section, start='Analyte', stop='Prep. By'
    )
    if not data_lines:
        data_lines = _rows_between(
            section, start='Analyte', stop='Sample Prepared By'
        )

    # Split merged columns.
    data_lines = _split_two_column_rows(data_lines, ['Weight %', 'Feces'])

    for line in data_lines:
        line = line.strip()
        if not line or '(%)' in line or 'Action' in line:
            continue

        idx = _find_first_numeric(line)
        if idx >= len(line):
            continue
        name = line[:idx].strip()
        values_str = line[idx:].strip()
        if not name:
            continue

        key = _snake_case(name)
        values = values_str.split()
        value = _parse_number(values[-1]) if values else None
        limit = _parse_number(values[0]) if len(values) >= 2 else None

        results.append({
            'analysis': 'foreign_matter',
            'key': key,
            'name': name,
            'value': value,
            'units': 'percent',
            'limit': limit,
            'lod': None,
            'loq': None,
            'status': '',
        })

    return results


def _extract_yeast_mold(page_text: str, rows: List[str]) -> List[Dict]:
    """Extract total yeast and mold results."""
    results = []
    if 'Total Yeast and Mold' not in page_text:
        return results

    for row in rows:
        row = row.strip()
        if row.startswith('Total Yeast/Mold'):
            values = row.split()
            if len(values) >= 3:
                limit = _parse_number(values[1])
                # Value could be numeric, "Passed", or "Not Detected".
                raw_result = values[-1]
                value = _parse_number(raw_result)
                status_str = raw_result.strip()
                status = ''
                if status_str.lower() in ('passed', 'pass', 'not detected'):
                    status = 'Pass'
                elif status_str.lower() in ('failed', 'fail'):
                    status = 'Fail'

                results.append({
                    'analysis': 'microbes',
                    'key': 'total_yeast_mold',
                    'name': 'Total Yeast/Mold',
                    'value': value,
                    'units': 'cfu/g',
                    'limit': limit,
                    'lod': None,
                    'loq': None,
                    'status': status,
                })
                break

    return results


def _extract_tcl(page_text: str, rows: List[str]) -> List[Dict]:
    """Extract total contaminant load results."""
    results = []
    if 'Total Contaminant Load' not in page_text:
        return results

    for row in rows:
        row = row.strip()
        if row.startswith('Heavy Metals, Pesticides'):
            values = row.split()
            value = _parse_number(values[-1]) if values else None
            limit = _parse_number(values[-2]) if len(values) >= 3 else None
            results.append({
                'analysis': 'foreign_matter',
                'key': 'total_contaminant_load',
                'name': 'Total Contaminant Load',
                'value': value,
                'units': 'ppm',
                'limit': limit,
                'lod': None,
                'loq': None,
                'status': '',
            })
            break

    return results


# ── Main Entry Point ───────────────────────────────────────────────

def parse_acs_pdf(
        parser: Any = None,
        doc: str = '',
    ) -> Dict:
    """Parse an ACS Laboratory COA PDF directly from the file.

    This is the primary parsing function for the hybrid engine.
    Extracts all data from the PDF using pdfplumber text extraction
    — no network access required.

    Args:
        parser: Optional CoADoc instance (backwards compatibility).
                Not used in the hybrid path.
        doc:    Path to the COA PDF file.

    Returns:
        Dict with all extracted COA data in hybrid format.
    """
    # Handle argument order flexibility.
    pdf_path = doc if doc else parser
    if isinstance(pdf_path, str) and not pdf_path.endswith('.pdf'):
        pdf_path = doc
    if not pdf_path or not isinstance(pdf_path, str):
        raise ValueError('No PDF path provided.')

    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            raise ValueError(f'Empty PDF: {pdf_path}')

        page = pdf.pages[0]
        page_text = _clean_text(page.extract_text() or '')
        lines = page_text.split('\n')

        # ── Initialize observation dict ───────────────────────
        obs = {}

        # ── Extract product name ──────────────────────────────
        obs['product_name'] = _extract_product_name(page_text, lines)

        # ── Extract product type ──────────────────────────────
        obs['product_type'] = _extract_product_type(page_text)

        # ── Extract metadata fields ───────────────────────────
        obs.update(_extract_metadata(page_text))

        # ── Extract client/producer info ──────────────────────
        obs.update(_extract_client_info(page, page_text))

        # ── Use cultivation/production facility as producer/distributor ──
        if not obs.get('producer') and obs.get('cultivation_facility'):
            obs['producer'] = obs['cultivation_facility']
        if obs.get('production_facility'):
            obs['distributor'] = obs['production_facility']

        # ── Extract analysis statuses ─────────────────────────
        analyses, statuses, overall_status = _extract_analysis_statuses(page_text)
        obs.update(statuses)
        obs['status'] = overall_status

        # ── Extract potency summary totals ────────────────────
        obs.update(_extract_potency_summary(page))

        # ── Extract cannabinoid results from page 1 ───────────
        results = _extract_cannabinoids_page1(page, page_text)

        # ── Extract terpene summary (Patient COAs) ────────────
        terpene_summary = _extract_terpene_summary_page1(page, page_text)
        terpene_keys_collected = {r['key'] for r in terpene_summary}
        results.extend(terpene_summary)

        # ── Extract moisture from page 1 (if present) ─────────
        results.extend(_extract_moisture_page1(page, page_text))

        # ── Extract heavy metals from page 1 (Compliance) ─────
        # Some compliance COAs have heavy metals on page 1.
        if 'Arsenic' in page_text and 'Heavy Metals' in page_text:
            crop = page.within_bbox((
                0, page.height * 0.6, page.width * 0.52, page.height
            ))
            crop_text = _clean_text(crop.extract_text() or '')
            crop_rows = crop_text.split('\n')
            hm_page1 = _extract_heavy_metals(page, crop_text, crop_rows)
            if hm_page1:
                results.extend(hm_page1)

        # ── Track which analyses have been collected ──────────
        collected_analyses = {r['analysis'] for r in results}

        # ── Process subsequent pages ──────────────────────────
        for page in pdf.pages[1:]:
            page_text, rows = _get_page_rows(page)

            # Terpenes (detailed).
            if 'Terpenes' in page_text and 'terpenes' not in collected_analyses:
                terp_results = _extract_terpenes(
                    page, page_text, rows, terpene_keys_collected
                )
                results.extend(terp_results)
                if terp_results:
                    collected_analyses.add('terpenes')

            # Heavy metals.
            if 'Arsenic' in page_text and 'heavy_metals' not in collected_analyses:
                hm_results = _extract_heavy_metals(page, page_text, rows)
                results.extend(hm_results)
                if hm_results:
                    collected_analyses.add('heavy_metals')

            # Mycotoxins.
            if 'Mycotoxins' in page_text and 'mycotoxins' not in collected_analyses:
                # Handle wider left column for mycotoxins.
                try:
                    left = page.within_bbox((0, 0, page.width * 0.575, page.height))
                    right = page.within_bbox((page.width * 0.575, 0, page.width, page.height))
                    myco_rows = (_clean_text(left.extract_text() or '').split('\n') +
                                 _clean_text(right.extract_text() or '').split('\n'))
                except Exception:
                    myco_rows = rows
                myco_results = _extract_mycotoxins(page, page_text, myco_rows)
                results.extend(myco_results)
                if myco_results:
                    collected_analyses.add('mycotoxins')

            # Pesticides.
            if 'Pesticides' in page_text:
                pest_results = _extract_pesticides(page, page_text)
                results.extend(pest_results)
                if pest_results:
                    collected_analyses.add('pesticides')

            # Residual solvents.
            if 'Residual Solvents' in page_text:
                solv_results = _extract_residual_solvents(page, page_text)
                results.extend(solv_results)
                if solv_results:
                    collected_analyses.add('residual_solvents')

            # Microbes (pathogenic).
            if 'Pathogenic' in page_text:
                micro_results = _extract_microbes(page, page_text, rows)
                results.extend(micro_results)
                if micro_results:
                    collected_analyses.add('microbes')

            # Moisture.
            if 'Moisture' in page_text and not any(
                r['analysis'] == 'moisture' for r in results
            ):
                results.extend(_extract_moisture(page_text, rows))

            # Water activity.
            if 'Water Activity' in page_text:
                results.extend(_extract_water_activity(page_text, rows))

            # Foreign matter.
            if 'Filth and Foreign' in page_text:
                results.extend(_extract_foreign_matter(page_text, rows))

            # Total yeast and mold.
            if 'Total Yeast and Mold' in page_text:
                results.extend(_extract_yeast_mold(page_text, rows))

            # Total contaminant load.
            if 'Total Contaminant Load' in page_text:
                results.extend(_extract_tcl(page_text, rows))

        # ── Deduplicate results ───────────────────────────────
        seen = set()
        unique_results = []
        for r in results:
            dup_key = (r['analysis'], r['key'])
            if dup_key not in seen:
                seen.add(dup_key)
                unique_results.append(r)
        results = unique_results

        # ── Build final analyses list ─────────────────────────
        result_analyses = sorted({r['analysis'] for r in results})
        # Merge with badge-detected analyses.
        all_analyses = sorted(set(analyses) | set(result_analyses))

        # ── Format dates ──────────────────────────────────────
        for key in list(obs.keys()):
            if key.startswith('date_') and obs[key]:
                obs[key] = _parse_date(str(obs[key]))

        # ── Finalize observation ──────────────────────────────
        obs = {**ACS_LABS, **obs}
        obs['analyses'] = json.dumps(all_analyses)
        obs['results'] = json.dumps(results)
        obs['coa_parsed_at'] = datetime.now().isoformat()

        # Generate hashes.
        hash_input = json.dumps(results, sort_keys=True)
        obs['results_hash'] = hashlib.sha256(
            hash_input.encode()).hexdigest()[:16]

        id_input = (
            hash_input +
            obs.get('product_name', '') +
            obs.get('producer', '') +
            obs.get('date_tested', '')
        )
        obs['sample_id'] = obs.get('sample_id', '') or hashlib.sha256(
            id_input.encode()).hexdigest()[:16]
        obs['lab_id'] = obs.get('lab_id', '')
        obs['coa_pdf'] = pdf_path.replace('\\', '/').split('/')[-1]

    return obs


# ── Entry Point (LAB_REGISTRY compatible) ──────────────────────────

def parse_acs_coa(
        parser: Any = None,
        doc: str = '',
        **kwargs,
    ) -> Dict:
    """Parse an ACS Laboratory COA PDF.

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

    return parse_acs_pdf(parser, doc)


def is_acs_labs(pdf_path: str) -> bool:
    """Quick check if a PDF is an ACS Labs COA (without full parse).

    Args:
        pdf_path: Path to a PDF file.

    Returns:
        True if the PDF appears to be from ACS Laboratory.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return False
            text = (pdf.pages[0].extract_text() or '').lower()
            return (
                'acslabcannabis.com' in text
                or 'acslab.com' in text
                or 'acs laboratory' in text
                or ('721 cortaro' in text and 'sun city center' in text)
            )
    except Exception:
        return False


# ── Tests ──────────────────────────────────────────────────────────

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
            print('Usage: python acs.py <pdf_file> [pdf_file2 ...]')
            sys.exit(1)

    passed = 0
    failed = 0
    for pdf_file in sorted(test_files):
        pdf_path = (os.path.join(test_dir, pdf_file)
                     if not os.path.isabs(pdf_file) else pdf_file)
        if not os.path.exists(pdf_path):
            print(f'Not found: {pdf_path}')
            continue
        try:
            data = parse_acs_coa(None, pdf_path)
            results = json.loads(data.get('results', '[]'))
            analyses = json.loads(data.get('analyses', '[]'))
            print(f'\n{"=" * 60}')
            print(f'✓ {pdf_file}')
            print(f'  Product:    {data.get("product_name", "?")}')
            print(f'  Type:       {data.get("product_type", "?")}')
            print(f'  Strain:     {data.get("strain_name", "?")}')
            print(f'  Producer:   {data.get("producer", "?")}')
            print(f'  Sample #:   {data.get("sample_id", "?")}')
            print(f'  Batch #:    {data.get("batch_number", "?")}')
            print(f'  Tested:     {data.get("date_tested", "?")}')
            print(f'  THC:        {data.get("total_thc", "?")}%')
            print(f'  CBD:        {data.get("total_cbd", "?")}')
            print(f'  Terpenes:   {data.get("total_terpenes", "?")}%')
            print(f'  Status:     {data.get("status", "?")}')
            print(f'  Analyses:   {analyses}')
            print(f'  Results:    {len(results)} analytes')
            # Show result breakdown by analysis.
            from collections import Counter
            breakdown = Counter(r['analysis'] for r in results)
            for analysis, count in sorted(breakdown.items()):
                print(f'    {analysis}: {count}')
            passed += 1
        except Exception as e:
            print(f'\n✗ {pdf_file}: {e}')
            import traceback
            traceback.print_exc()
            failed += 1

    print(f'\n{"=" * 60}')
    print(f'Results: {passed} passed, {failed} failed out of {passed + failed}')
