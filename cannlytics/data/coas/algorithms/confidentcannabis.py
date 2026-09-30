"""
Parse Confident Cannabis / Confident LIMS COA — Offline-First Hybrid Engine
Copyright (c) 2022-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2022
Updated: 3/6/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Confident Cannabis / Confident LIMS COA PDFs directly from
    the PDF text — no network access required. This is the modernized
    offline-first engine that extracts all data from the PDF itself
    using pdfplumber text extraction and regex-based field parsing.

    Confident Cannabis (now Confident LIMS) is the most widely used
    LIMS platform for cannabis testing labs in the US, powering COAs
    across dozens of labs in MO, CA, AZ, NY, and many other states.

    Labs using Confident Cannabis/LIMS include (non-exhaustive):

        * Fleur de Lis Analytical Laboratories (MO)
        * GCA Labs (MO)
        * ContiCorp Labs (MO)
        * Quality Cannabis Labs (CA)
        * Landau Laboratories (CA)
        * Excelbis Labs (CA)
        * Brightside Scientific (CA)
        * Apollo Labs (AZ)
        * Tree House Labs (AZ)
        * Biotrax Testing Laboratory (NY)
        * DRS Testing (NY)
        * Keystone State Testing (NY)
        * And many more

    Identification:
        Confident Cannabis COAs contain 'Confident Cannabis' or
        'Confident LIMS' text in page footers. Footer patterns include:
            - "Confident Cannabis All Rights Reserved"
            - "Confident LIMS All Rights Reserved"
            - "www.confidentcannabis.com"
            - "www.confidentlims.com"
            - "Powered by Confident LIMS"

    Format notes:
        * The data tables are rendered as text blocks within PDF cells
        * Each page has a repeating header with lab info and sample info
        * Analysis sections (Cannabinoids, Terpenes, Pesticides, etc.)
          each get their own page(s)
        * Some labs use two-column layouts for large analyte lists
        * AZ COAs may have multi-page cover sheets (non-CC format)
        * NY COAs may have dual-LIMS reports (Confident LIMS + Keystone)

Data Points:

    ✓ product_name, strain_name, product_type, matrix
    ✓ date_tested, date_received, date_collected, date_produced
    ✓ batch_number, batch_size, sample_size, sample_weight
    ✓ lab, lab_license_number, lab_address, lab_phone, lab_website
    ✓ producer, producer_license_number
    ✓ distributor, distributor_license_number
    ✓ sample_id (lab_id)
    ✓ total_thc, total_cbd, total_cannabinoids, total_terpenes
    ✓ status (overall batch pass/fail)
    ✓ analyses (list of analysis types)
    ✓ results (list of analyte result dicts)
    ✓ metrc_ids (METRC sample and batch IDs)
    ✓ moisture_content, water_activity
"""
# Standard imports:
import hashlib
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# External imports:
import pdfplumber


# ── Constants ─────────────────────────────────────────────────────

CONFIDENT_CANNABIS = {
    'coa_algorithm': 'confidentcannabis.py',
    'coa_algorithm_entry_point': 'parse_cc_coa',
    'lims': 'Confident Cannabis',
    'url': 'https://www.confidentcannabis.com',
}


def _deligature(text: str) -> str:
    """Restore the 'fi'/'fl' ligatures that some Confident LIMS PDFs (notably
    the Louisiana/Orion Therapeutics template) encode as a NUL byte, so that
    'Certi\\x00cate', 'de\\x00ned', 'Of\\x00ce' become readable.

    This is a strict no-op on COAs that contain no NUL byte — every other
    state's Confident Cannabis COA is left byte-for-byte identical, so existing
    parsing is unaffected.
    """
    if '\x00' not in text:
        return text
    # A bare 'fi' on its own line is an extraction artifact; drop it.
    text = re.sub(r'(?m)^\s*fi\s*$\n?', '', text)
    return text.replace('\x00', 'fi')


# Louisiana disclaimer / footer markers. When any of these appear on a line
# inside a results section, we've run past the analyte tables into the legal
# footer — analyte parsing must stop. Gated to Louisiana/Orion text so no
# other state's output can change.
_LA_FOOTER_MARKERS = (
    'orion therapeutics',
    'ldh/oph',
    'louisiana department',
    'regulation of medical marijuana',
    'values reported relate only',
    'pass/fail results are reported',
    'makes no claims',
    'this certificate must not be altered',
    'sampling is done in accordance',
    'nd=not detected',
)


def _is_la_orion(text: str) -> bool:
    """True if the COA is a Louisiana Orion Therapeutics report (Confident
    LIMS template). Used only to gate LA-specific metadata handling."""
    low = _deligature(text).lower()
    return 'orion therapeutics' in low


# Product-form line -> standardized product_type (LA Orion template).
_LA_FORM_MAP = (
    ('soft chew', 'edible'), ('gummy', 'edible'), ('ingestible', 'edible'),
    ('capsule', 'edible'), ('lozenge', 'edible'), ('tablet', 'edible'),
    ('tincture', 'tincture'), ('sublingual', 'tincture'),
    ('topical', 'topical'), ('transdermal', 'topical'), ('lotion', 'topical'),
    ('suppository', 'topical'),
    ('cartridge', 'vape'), ('vape', 'vape'), ('disposable', 'vape'),
    ('distillate', 'concentrate'), ('concentrate', 'concentrate'),
    ('extract', 'concentrate'), ('rosin', 'concentrate'), ('resin', 'concentrate'),
    ('rso', 'concentrate'), ('wax', 'concentrate'), ('shatter', 'concentrate'),
    ('pre-roll', 'preroll'), ('preroll', 'preroll'),
    ('flower', 'flower'), ('bud', 'flower'),
)

_LA_FORM_KEYWORDS = ('soft chew', 'gummy', 'ingestible', 'capsule', 'lozenge',
                     'tablet', 'tincture', 'sublingual', 'topical', 'transdermal',
                     'lotion', 'suppository', 'cartridge', 'vape', 'disposable',
                     'distillate', 'concentrate', 'extract', 'rosin', 'resin',
                     'rso', 'wax', 'shatter', 'pre-roll', 'preroll', 'flower')


def _la_product_type(form_line: str) -> Optional[str]:
    low = form_line.lower()
    for needle, ptype in _LA_FORM_MAP:
        if needle in low:
            return ptype
    return None


def _parse_la_orion_metadata(page1_text: str) -> Dict:
    """Extract producer/lab/product metadata for the Louisiana Orion
    Therapeutics (Confident LIMS) template.

    Header layout (client = producer on the left, labelled fields on the right):
        Ilera Holistic Healthcare  Sample: 2503OTL0016.0137
        13073 Plank Road           Strain: 1A40B0100000259000033315
        Baker, LA 70714            Batch#: WOFEB25B1; Batch Size: g
        jalexander@ileraholistic.com  Sample Received: ...; Report Created: ...
        (225) 612-1264
        Lic. #704-00002            Sampling: ; Environment:
        <PRODUCT NAME>
        <PRODUCT FORM, e.g. "Ingestible, Soft Chew, Alcohol">
        ... METRC Sample: 1A40B0100000259000033487
    Lab identity lives in the footer/disclaimer:
        6300 Corporate Blvd  Confident LIMS
        Baton Rouge, LA      All Rights Reserved
        Lic# 705-00004       www.confidentlims.com
        ... tested by Orion Therapeutics ...

    Returns only the fields this template can supply; the caller overlays them
    onto the generically-parsed obs, and only for Orion COAs.
    """
    obs: Dict[str, Any] = {'lab': 'Orion Therapeutics', 'lims': 'Confident LIMS'}
    lines = [ln.rstrip() for ln in page1_text.split('\n')]

    # ── Producer (client) name: text before "Sample:" on that row ──
    for ln in lines:
        if 'Sample:' in ln and 'METRC' not in ln and 'Received' not in ln:
            producer = ln.split('Sample:')[0].strip()
            if producer:
                obs['producer'] = producer
            sid = ln.split('Sample:')[1].strip()
            if sid:
                obs['sample_id'] = sid.split()[0].strip()
            break

    # ── Producer address ──
    for i, ln in enumerate(lines):
        if 'Strain:' in ln:
            street = ln.split('Strain:')[0].strip()
            if street:
                obs['producer_street'] = street
        if 'Batch#' in ln:
            csz = ln.split('Batch#')[0].strip()
            m = re.match(r'(.+?),\s*([A-Z]{2})\s*(\d{5})?', csz)
            if m:
                obs['producer_city'] = m.group(1).strip()
                obs['producer_state'] = m.group(2).strip()
                if m.group(3):
                    obs['producer_zipcode'] = m.group(3).strip()
            bm = re.search(r'Batch#[:\s]*([A-Za-z0-9-]+)', ln)
            if bm:
                obs['batch_number'] = bm.group(1).strip()

    # ── Licenses: producer "Lic. #704-..."; lab footer "Lic# 705-..." ──
    prod_lic = re.search(r'Lic\.\s*#\s*([A-Z0-9][A-Z0-9-]+)', page1_text)
    if prod_lic:
        obs['producer_license_number'] = prod_lic.group(1).strip()
    lab_lic = re.search(r'Lic#\s+([A-Z0-9][A-Z0-9-]+)', page1_text)
    if lab_lic:
        obs['lab_license_number'] = lab_lic.group(1).strip()

    # ── Lab address (the "…Corporate Blvd … / City, ST" footer block) ──
    lab_addr = re.search(
        r'(\d+\s+[\w\s.]+?(?:Blvd|Street|St|Ave|Drive|Dr|Road|Rd|Way|Pkwy|Highway))'
        r'\s+Confident\s+LIMS\s*\n\s*([\w\s]+?),\s*([A-Z]{2})',
        page1_text)
    if lab_addr:
        obs['lab_street'] = lab_addr.group(1).strip()
        obs['lab_city'] = lab_addr.group(2).strip()
        obs['lab_state'] = lab_addr.group(3).strip()

    # ── Product name + type: the form line, product name is the line above ──
    for i, ln in enumerate(lines):
        low = ln.lower()
        if any(k in low for k in _LA_FORM_KEYWORDS) and ',' in ln and i > 0:
            ptype = _la_product_type(ln)
            if ptype:
                obs['product_type'] = ptype
                obs['product_subtype'] = ln.strip()
                # Product name = nearest non-empty line above that isn't a
                # labelled/field line.
                for j in range(i - 1, -1, -1):
                    cand = lines[j].strip()
                    if cand and not re.search(
                            r'(Sample:|Strain:|Batch#|Received|Lic|Environment'
                            r'|@|^\(\d{3}\))', cand):
                        obs['product_name'] = cand
                        break
                break

    # ── METRC sample id ──
    metrc = re.search(r'METRC\s+Sample:\s*([A-Z0-9]+)', page1_text)
    if metrc:
        obs['metrc_sample_id'] = metrc.group(1).strip()
        obs['metrc_ids'] = [metrc.group(1).strip()]

    # ── Overall status from the safety summary. Scan only the region ABOVE
    # the legal disclaimer, since the disclaimer literally contains the phrase
    # "Pass/Fail results are reported…" which would otherwise false-trigger. ──
    head = page1_text
    for mk in ('ND=Not Detected', 'tested by Orion', 'Pass/Fail results'):
        idx = head.find(mk)
        if idx != -1:
            head = head[:idx]
    if re.search(r'\bFail\b', head):
        obs['status'] = 'fail'
    elif re.search(r'\bPass\b', head):
        obs['status'] = 'pass'

    return obs

# Analysis section headers → standard analysis name.
ANALYSIS_SECTION_MAP = {
    'cannabinoid': 'cannabinoids',
    'potency': 'cannabinoids',
    'terpene': 'terpenes',
    'pesticide': 'pesticides',
    'heavy metal': 'heavy_metals',
    'metal': 'heavy_metals',
    'microbial': 'microbials',
    'microbiological': 'microbials',
    'mycotoxin': 'mycotoxins',
    'residual solvent': 'residual_solvents',
    'solvent': 'residual_solvents',
    'foreign matter': 'foreign_matter',
    'foreign material': 'foreign_matter',
    'moisture': 'moisture',
    'water activity': 'water_activity',
    'vitamin e': 'additives',
    'additive': 'additives',
}

# Standard units by analysis type.
STANDARD_UNITS = {
    'cannabinoids': 'percent',
    'terpenes': 'percent',
    'pesticides': 'ug/g',
    'heavy_metals': 'ug/g',
    'microbials': 'cfu/g',
    'mycotoxins': 'ug/kg',
    'residual_solvents': 'ug/g',
    'foreign_matter': 'percent',
    'moisture': 'percent',
    'water_activity': 'aw',
    'additives': 'ug/g',
}

# Common analyte key overrides (display name → snake_case).
ANALYTE_KEY_MAP = {
    'Δ9-THC': 'delta_9_thc',
    'Δ8-THC': 'delta_8_thc',
    'Δ9-THCa': 'thca',
    '(6aR,9S)-d10-THC': '6ar_9s_delta_10_thc',
    '(6aR,9R)-d10-THC': '6ar_9r_delta_10_thc',
    'β-Caryophyllene': 'beta_caryophyllene',
    'β-Myrcene': 'beta_myrcene',
    'β-Pinene': 'beta_pinene',
    'β-Ocimene': 'beta_ocimene',
    'α-Pinene': 'alpha_pinene',
    'α-Humulene': 'alpha_humulene',
    'α-Bisabolol': 'alpha_bisabolol',
    'α-Terpinene': 'alpha_terpinene',
    'α-Terpineol': 'alpha_terpineol',
    'α-Cedrene': 'alpha_cedrene',
    'α-Phellandrene': 'alpha_phellandrene',
    'α-Ocimene': 'alpha_ocimene',
    'γ-Terpinene': 'gamma_terpinene',
    'γ-Terpineol': 'gamma_terpineol',
    'δ-Limonene': 'delta_limonene',
    'δ-3-Carene': 'delta_3_carene',
    'D,L-Limonene': 'd_l_limonene',
    'D,L-Borneol': 'd_l_borneol',
    '3-Carene': 'three_carene',
    'd-3-Carene': 'delta_3_carene',
    'cis-Ocimene': 'cis_ocimene',
    'cis-Nerolidol': 'cis_nerolidol',
    'cis-beta-Ocimene': 'cis_beta_ocimene',
    'trans-Nerolidol': 'trans_nerolidol',
    'trans-Caryophyllene': 'trans_caryophyllene',
    'trans-beta-Ocimene': 'trans_beta_ocimene',
    'trans-β-Farnesene': 'trans_beta_farnesene',
    'Endo-Fenchyl Alcohol': 'endo_fenchyl_alcohol',
    '1,2-Dichloro-Ethane': '1_2_dichloro_ethane',
    '1,2-Dichloroethane': '1_2_dichloroethane',
    'Ethylene Oxide': 'ethylene_oxide',
    'Methylene-Chloride': 'methylene_chloride',
    'Ethyl-Acetate': 'ethyl_acetate',
    'Ethyl-Ether': 'ethyl_ether',
    'MGK-264': 'mgk_264',
    'Piperonyl Butoxide': 'piperonyl_butoxide',
    'Chlormequat chloride': 'chlormequat_chloride',
    'Chlormequat Chloride': 'chlormequat_chloride',
    'Kresoxim Methyl': 'kresoxim_methyl',
    'Methyl Parathion': 'methyl_parathion',
    'Parathion Methyl': 'methyl_parathion',
    'Vitamin E Acetate': 'vitamin_e_acetate',
    'Shiga toxin-producing E. Coli': 'stec',
    'Shiga Toxin E. Coli': 'stec',
    'Aspergillus flavus': 'aspergillus_flavus',
    'Aspergillus fumigatus': 'aspergillus_fumigatus',
    'Aspergillus niger': 'aspergillus_niger',
    'Aspergillus terreus': 'aspergillus_terreus',
    'Aspergillus spp.': 'aspergillus_spp',
    'Salmonella SPP': 'salmonella_spp',
    'Salmonella': 'salmonella',
    'E. Coli': 'e_coli',
    'Yeast & Mold': 'yeast_and_mold',
    'Aerobic Bacteria': 'aerobic_bacteria',
    'Total Aflatoxins': 'total_aflatoxins',
    'Ochratoxin A': 'ochratoxin_a',
    'Xylenes + Ethyl Benzene': 'xylenes_ethyl_benzene',
    'n-Hexane': 'n_hexane',
    'n-Heptane': 'n_heptane',
    'Isopropyl-Acetate': 'isopropyl_acetate',
    'Trichloroethylene': 'trichloroethylene',
    'Trichloroethene': 'trichloroethene',
    'Dichloromethane': 'dichloromethane',
    'PBO': 'piperonyl_butoxide',
    'Pentachloronitrobenzene (Quintozene)': 'pentachloronitrobenzene',
    'Quintozene': 'pentachloronitrobenzene',
    'Permethrin (trans + cis)': 'permethrins',
    'Permethrins, Total': 'permethrins',
    'Permethrins': 'permethrins',
    'Chlordane (trans + cis)': 'chlordane',
    'Dimethomorph (I + II)': 'dimethomorph',
    'Spinosyn (A + D)': 'spinosad',
    'Spinetoram (J + L)': 'spinetoram',
    'Pyrethrins (Cinerin +\nJasmolin + Pyrethrin)': 'pyrethrins',
    'Pyrethrins Total': 'pyrethrins',
    'Spinosad Total': 'spinosad',
    'Spinetoram Total': 'spinetoram',
}


# ── Utility Functions ─────────────────────────────────────────────

def _snake_case(text: str) -> str:
    """Convert an analyte display name to a snake_case key."""
    text = text.strip()
    # Check exact match first.
    if text in ANALYTE_KEY_MAP:
        return ANALYTE_KEY_MAP[text]
    # Check case-insensitive match.
    for k, v in ANALYTE_KEY_MAP.items():
        if k.lower() == text.lower():
            return v
    # General conversion.
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = s.strip('_')
    return s


def _parse_number(text: str) -> Optional[float]:
    """Parse a numeric string, returning None for non-detects."""
    if not text or not isinstance(text, str):
        return None
    text = text.strip().upper()
    if text in ('ND', 'N/A', '', '-', 'NT', 'NR', 'NOT DETECTED',
                'NOT TESTED', 'NOT REPORTED', 'ABSENCE',
                'NOT DETECTED IN 1G'):
        return None
    if '<' in text or 'LOQ' in text.upper():
        return 0.0  # Detected but below LOQ.
    # Remove units suffixes.
    text = re.sub(
        r'\s*(mg/g|mg/unit|mg/serving|mg/container|%|µg/g|µg/kg|ug/g|'
        r'ug/kg|ppm|ppb|cfu/g|rfu/g|aw|mg)\s*$',
        '', text, flags=re.IGNORECASE,
    ).strip()
    # Remove qualifier flags (Q3, V1, R1, etc.).
    text = re.sub(r'\s+[A-Z]\d+\s*$', '', text).strip()
    try:
        return float(text.replace(',', ''))
    except (ValueError, TypeError):
        return None


def _parse_date(text: str) -> str:
    """Parse a date string to ISO format (YYYY-MM-DD)."""
    if not text or not isinstance(text, str):
        return ''
    text = text.strip()
    # Remove time components.
    text = re.sub(r'\s+\d{1,2}:\d{2}(:\d{2})?\s*(am|pm|AM|PM)?\s*$', '', text)
    text = text.strip()
    for fmt in ('%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%b %d, %Y',
                '%B %d, %Y', '%m/%d/%Y %H:%M'):
        try:
            return datetime.strptime(text, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return text


def _classify_analysis(section_header: str) -> str:
    """Map a section header to a standard analysis name."""
    header_lower = section_header.lower().strip()
    for keyword, analysis in ANALYSIS_SECTION_MAP.items():
        if keyword in header_lower:
            return analysis
    return header_lower.replace(' ', '_')


def _detect_units_from_header(header_text: str, analysis: str) -> str:
    """Detect measurement units from column headers or analysis type."""
    h = header_text.lower()
    if 'µg/kg' in h or 'ug/kg' in h or 'ppb' in h:
        return 'ug/kg'
    if 'µg/g' in h or 'ug/g' in h or 'ppm' in h:
        return 'ug/g'
    if 'mg/g' in h:
        return 'mg/g'
    if 'mg/serving' in h:
        return 'mg/serving'
    if 'mg/unit' in h:
        return 'mg/unit'
    if 'cfu/g' in h:
        return 'cfu/g'
    if 'rfu/g' in h:
        return 'rfu/g'
    if '%' in h:
        return 'percent'
    return STANDARD_UNITS.get(analysis, 'percent')


def _is_cover_sheet(text: str) -> bool:
    """Detect AZ-style cover sheets (non-COA pages)."""
    indicators = [
        'Product Form',
        'Distribution Chain:',
        'Arizona Dept. of Health Services Warning',
        'Marijuana Establishment Name',
    ]
    matches = sum(1 for ind in indicators if ind in text)
    # If the page has multiple cover-sheet indicators and
    # does NOT have the standard CC header, it's a cover sheet.
    if matches >= 2 and 'Sample ID:' not in text:
        return True
    return False


def _find_cc_identifier(pdf) -> str:
    """Check whether a PDF is a Confident Cannabis/LIMS COA."""
    for page in pdf.pages[:3]:
        text = (page.extract_text() or '').lower()
        if any(marker in text for marker in [
            'confidentcannabis.com',
            'confidentlims.com',
            'confident cannabis',
            'confident lims',
            'con\x00dent cannabis',
            'con\x00dent lims',
        ]):
            return 'Confident Cannabis'
    return ''


# ── Metadata Parsing ──────────────────────────────────────────────

def _parse_lab_header(text: str) -> Dict:
    """Parse lab info from the page header or footer area.
    
    Two major CC format variants:
    1. Confident Cannabis classic: Lab info in page header
       (starts with "Regulatory Compliance Testing")
    2. Confident LIMS: Client info in header, Lab info in footer
       (starts with "Certificate of Analysis")
    """
    obs = {}
    lines = text.split('\n')
    full_text = text

    # Skip known page-level header prefixes.
    skip_prefixes = [
        'Regulatory Compliance Testing',
        'QA Testing', 'R&D Report',
        'Certificate of Analysis', 'Certicate of Analysis',
        'Adult Use', 'Powered by',
        'Amended Report', 'Amended Notes',
        'Type of Use',
    ]

    # Determine format: is the lab in the header or the footer?
    # Confident LIMS format: starts with "Certificate of Analysis"
    # then client info (company name, address, email, phone, license)
    # then sample info. Lab info at bottom.
    is_lims_format = any(
        line.strip().startswith('Certi') and 'Analysis' in line
        for line in lines[:3]
    )

    lab_name = ''
    lab_phone = ''

    if not is_lims_format:
        # Classic CC format: lab name after header prefixes, with phone.
        for i, line in enumerate(lines[:10]):
            stripped = line.strip()
            if not stripped or any(stripped.startswith(s) for s in skip_prefixes):
                continue
            phone_match = re.search(r'\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}', stripped)
            if phone_match:
                lab_name = stripped[:phone_match.start()].strip()
                lab_phone = phone_match.group().strip()
                break
            if re.match(r'^\d+\s+\w', stripped) and lab_name:
                break
            if not lab_name:
                lab_name = stripped
    else:
        # Confident LIMS format: lab info in footer.
        # Look for the lab name near the footer text patterns.
        # Footer pattern: "Lab Name, All Rights Reserved\nAddress\nCity\nPhone\nWebsite\nLic#"
        footer_match = re.search(
            r'([A-Z][\w\s,.-]+?),?\s*All\s*Rights\s*Reserved\s*\n'
            r'([\d]+\s+[\w\s.]+(?:St|Dr|Ave|Rd|Blvd|Pkwy|Street|Drive'
            r'|Highway|Court|Way)[\w\s.,#]*)\n'
            r'([\w\s,]+)\n'
            r'\((\d{3})\)\s*(\d{3}[\s-]\d{4})',
            full_text,
        )
        if footer_match:
            lab_name = footer_match.group(1).strip()
            obs['lab_street'] = footer_match.group(2).strip()
            city_state = footer_match.group(3).strip()
            lab_phone = f'({footer_match.group(4)}) {footer_match.group(5)}'
            # Parse city, state from footer.
            csz = re.match(r'([\w\s]+),\s*([A-Z]{2})\s*(\d{5})?', city_state)
            if csz:
                obs['lab_city'] = csz.group(1).strip()
                obs['lab_state'] = csz.group(2).strip()
                if csz.group(3):
                    obs['lab_zipcode'] = csz.group(3).strip()
            elif city_state:
                obs['lab_city'] = city_state

    obs['lab'] = lab_name
    if lab_phone:
        obs['lab_phone'] = lab_phone

    # Lab license number.
    # In footer format, the lab license is near "Lic#" at the bottom.
    if is_lims_format:
        # Get the LAST Lic# in footer area (the lab's license).
        footer_lic = re.findall(r'Lic#?\s*([A-Z0-9][A-Z0-9-]+)', full_text[-500:])
        if footer_lic:
            obs['lab_license_number'] = footer_lic[-1].strip()
    else:
        lic_match = re.search(r'Lic[#\s:]+\s*([A-Z0-9][A-Z0-9-]+)', text[:600])
        if lic_match:
            obs['lab_license_number'] = lic_match.group(1).strip()

    # Lab website.
    url_match = re.search(
        r'(https?://[^\s]+|www\.[^\s]+)',
        text[:600] if not is_lims_format else full_text[-500:],
    )
    if url_match:
        obs['lab_website'] = url_match.group().strip()

    # Lab address from non-LIMS format.
    if not is_lims_format:
        csz_match = re.search(
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)',
            text[:600],
        )
        if csz_match:
            obs['lab_city'] = csz_match.group(1).strip()
            obs['lab_state'] = csz_match.group(2).strip()
            obs['lab_zipcode'] = csz_match.group(3).strip()

    return obs


def _parse_sample_metadata(text: str) -> Dict:
    """Parse sample and product metadata from the header block."""
    obs = {}
    lines = text.split('\n')

    # Product name: Typically appears as a prominent line before
    # "METRC Sample:" or "Sample ID:" lines.
    # It follows the lab header and precedes the sample details.
    for i, line in enumerate(lines):
        # Find the line with Sample ID.
        if 'Sample ID:' in line or 'LIMS ID:' in line or ('Sample:' in line and 'METRC' not in line):
            # Walk backwards to find the product name.
            for j in range(i - 1, max(i - 6, -1), -1):
                candidate = lines[j].strip()
                if not candidate:
                    continue
                # Skip lines that are NOT the product name.
                if any(skip in candidate for skip in [
                    'Lic#', 'Lic.', 'http', 'www.', '.com',
                    'Regulatory', 'QA Testing', 'Certificate',
                    'Certicate', 'Adult Use', 'Powered by',
                    'Amended', 'Type of Use', 'METRC',
                    '@', 'PJLA', 'DEA#',
                ]):
                    continue
                # Skip phone numbers.
                if re.match(r'^\(\d{3}\)', candidate):
                    continue
                # Skip addresses (number + street name).
                if re.match(r'^\d+\s+[\w\s]+(St|Ave|Rd|Dr|Blvd|Street|Road|Pkwy|Perimeter)', candidate):
                    continue
                # Skip city/state/zip lines.
                if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s+[A-Z]{2}\s+\d{5}', candidate):
                    continue
                # Remove page numbers.
                candidate = re.sub(r'\d+\s+of\s+\d+\s*$', '', candidate).strip()
                if candidate and len(candidate) > 2:
                    obs['product_name'] = candidate
                    break
            break

    # Also check for product name in the second text block
    # (some formats: "Product\nFlower - Cured\n...")
    # and the METRC Sample line.
    if not obs.get('product_name'):
        # Look for a line between METRC and Sample ID blocks.
        metrc_line = None
        for i, line in enumerate(lines):
            if 'METRC' in line and i > 0:
                candidate = lines[i - 1].strip()
                candidate = re.sub(r'\d+\s+of\s+\d+\s*$', '', candidate).strip()
                if candidate and len(candidate) > 3:
                    obs['product_name'] = candidate
                    break

    # Sample ID.
    sid_match = re.search(
        r'(?:Sample\s*ID|LIMS\s*ID|Sample)[:\s]+([A-Z0-9][A-Z0-9._-]+)',
        text,
    )
    if sid_match:
        obs['sample_id'] = sid_match.group(1).strip()
        obs['lab_id'] = obs['sample_id']

    # Strain.
    strain_match = re.search(
        r'Strain[:\s]+(.+?)(?:\s{2,}|$)',
        text, re.MULTILINE,
    )
    if strain_match:
        strain = strain_match.group(1).strip()
        # Clean up trailing field labels.
        strain = re.sub(r'\s+(?:Collected|Matrix|Sampling|Batch).*$', '', strain).strip()
        if strain and strain.upper() not in ('N/A', ''):
            obs['strain_name'] = strain

    # Matrix.
    matrix_match = re.search(
        r'Matrix[:\s]+(.+?)(?:\s{2,}|$)',
        text, re.MULTILINE,
    )
    if matrix_match:
        matrix = matrix_match.group(1).strip()
        matrix = re.sub(r'\s+(?:Received|Type|Lic).*$', '', matrix).strip()
        if matrix:
            obs['matrix'] = matrix

    # Product type.
    type_match = re.search(
        r'(?:^|\n)\s*Type[:\s]+(.+?)(?:\s{2,}|$)',
        text, re.MULTILINE,
    )
    if type_match:
        ptype = type_match.group(1).strip()
        ptype = re.sub(r'\s+(?:Completed|Sample Size|Source|Batch|Produced).*$', '', ptype).strip()
        if ptype:
            obs['product_type'] = ptype

    # Category/Type from NY format.
    cat_match = re.search(r'Category/Type[:\s]+(.+?)(?:\n|$)', text)
    if cat_match:
        obs['product_type'] = cat_match.group(1).strip()

    # Dates.
    for field, pattern in [
        ('date_produced', r'Produced[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})'),
        ('date_collected', r'Collected[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})'),
        ('date_received', r'(?:Received|Sampling\s*Date\s*&\s*Received)[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})'),
        ('date_tested', r'(?:Completed|Report\s*Created|Reported|Expires)[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})'),
        ('harvest_date', r'Harvest\s*Date[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})'),
    ]:
        if field not in obs or not obs[field]:
            match = re.search(pattern, text)
            if match:
                obs[field] = _parse_date(match.group(1))

    # Batch number.
    batch_match = re.search(
        r'Batch\s*#?[:\s]+([A-Z0-9][\w./ -]+?)(?:\s{2,}|\n|$)',
        text, re.MULTILINE,
    )
    if batch_match:
        batch_val = batch_match.group(1).strip()
        # Clean trailing field labels.
        batch_val = re.sub(r'\s+(?:Lot|Client|Producer|Distributor|San|St\.).*$', '', batch_val).strip()
        if batch_val:
            obs['batch_number'] = batch_val

    # Sample size / batch size.
    size_match = re.search(
        r'Sample\s*Size[:\s]+([^;\n]+?)(?:;\s*Batch[:\s]+(.+?))?(?:\n|$)',
        text,
    )
    if size_match:
        sample_size = size_match.group(1).strip()
        if sample_size:
            obs['sample_size'] = sample_size
        if size_match.group(2):
            obs['batch_size'] = size_match.group(2).strip()

    # Batch/Lot Size (NY format).
    blot_match = re.search(r'Batch/Lot\s*Size[:\s]+(\d[\d,]*\s*\w+)', text)
    if blot_match:
        obs['batch_size'] = blot_match.group(1).strip()

    # Batch Size (NY DRS format).
    bs_match = re.search(r'Batch\s*Size[:\s]+(\d[\d,]*\s*(?:g|units|lbs?))', text)
    if bs_match and not obs.get('batch_size'):
        obs['batch_size'] = bs_match.group(1).strip()

    # Units sampled (NY format).
    us_match = re.search(r'Units\s*Sampled[:\s]+(.+?)(?:\n|$)', text)
    if us_match:
        obs['units_sampled'] = us_match.group(1).strip()

    # METRC IDs.
    metrc_sample = re.search(r'METRC\s*Sample[:\s]+(\S+)', text)
    metrc_batch = re.search(r'METRC\s*Batch[:\s]+(\S+)', text)
    metrc_ids = []
    if metrc_sample:
        metrc_ids.append(metrc_sample.group(1).rstrip(';'))
    if metrc_batch:
        metrc_ids.append(metrc_batch.group(1).rstrip(';'))
    if metrc_ids:
        obs['metrc_ids'] = metrc_ids

    return obs


def _parse_client_info(text: str) -> Dict:
    """Parse producer/client/distributor info from header."""
    obs = {}

    # CA format: "Distributor\nCompany Name\nLic. # XXX"
    # and "Producer\nCompany Name\nLic. # XXX"
    # MO format: "Client\nCompany Name\nLic. # XXX"
    # AZ format: "Client\nCompany Name\nLic. # XXX"
    # NY format: "Lic. #OCM-PROC-XX-XXXXXX"

    # Strategy: look for these label words and extract the next
    # substantive text line as the entity name.

    lines = text.split('\n')

    # --- Producer / Client ---
    for label in ('Producer', 'Client'):
        for i, line in enumerate(lines):
            # Match the label as a standalone word or at end of a line.
            if re.search(rf'\b{label}\b', line):
                # The name might be on the same line after the label,
                # or on the next line.
                # Check if there's text after the label on the same line.
                after = re.sub(rf'^.*\b{label}\b\s*', '', line).strip()
                if after and not after.startswith('Lic') and len(after) > 3:
                    obs['producer'] = after
                elif i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('Lic'):
                        obs['producer'] = next_line
                break
        if obs.get('producer'):
            break

    # Producer license: look for "Lic. #" or "Lic #" near the producer.
    # In CA format, there may be multiple Lic. # values - we want the
    # producer's (not the lab's or distributor's).
    # The producer license is typically the last one in the header block.
    all_lics = re.findall(r'Lic\.?\s*#?\s*([A-Z0-9][A-Z0-9-]+)', text[:1500])
    if len(all_lics) >= 3:
        # Lab, Distributor, Producer — producer is typically last.
        obs['producer_license_number'] = all_lics[-1]
    elif len(all_lics) >= 2:
        # Lab, Producer/Client.
        obs['producer_license_number'] = all_lics[-1]

    # --- Distributor ---
    for i, line in enumerate(lines):
        if 'Distributor' in line:
            after = re.sub(r'^.*\bDistributor\b\s*', '', line).strip()
            if after and not after.startswith('Lic') and len(after) > 3:
                obs['distributor'] = after
            elif i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith('Lic'):
                    obs['distributor'] = next_line
            # Distributor license.
            for j in range(i, min(i + 4, len(lines))):
                dl_match = re.search(r'Lic\.?\s*#?\s*([A-Z0-9][A-Z0-9-]+)', lines[j])
                if dl_match and j > i:
                    obs['distributor_license_number'] = dl_match.group(1)
                    break
            break

    # NY format: Contact Person and OCM license.
    if not obs.get('producer'):
        cp_match = re.search(r'Contact\s*Person[:\s]+(.+?)(?:\n|$)', text)
        if cp_match:
            # The producer is the entity name, not the contact person.
            # Look for it before the Contact Person line.
            for i, line in enumerate(lines):
                if 'Contact Person' in line and i > 0:
                    # Walk backwards.
                    for j in range(i - 1, max(i - 3, -1), -1):
                        candidate = lines[j].strip()
                        if candidate and not any(s in candidate for s in [
                            'Certificate', 'Certicate', 'Amended',
                            'Powered', 'Type of Use', 'DRS Testing',
                            'Biotrax',
                        ]):
                            obs['producer'] = candidate
                            break
                    break

    # NY OCM license.
    ocm_match = re.search(r'Lic\.?\s*#?\s*(OCM-PROC-\d{2}-\d+)', text)
    if ocm_match:
        obs['producer_license_number'] = ocm_match.group(1)

    return obs


def _parse_summary(text: str) -> Dict:
    """Parse the Summary section for batch status and analysis statuses."""
    obs = {}
    analyses = []

    # Overall batch status.
    batch_status = re.search(r'Batch\s+(Pass|Fail)', text, re.IGNORECASE)
    if batch_status:
        obs['status'] = batch_status.group(1).lower()

    # Individual analysis statuses from the Summary table.
    # Format: "Cannabinoids  12/22/2025  Complete"
    # or:     "Pesticides    Pass"
    status_patterns = re.findall(
        r'(Cannabinoids|Terpenes|Residual\s*Solvents|Microbials|'
        r'Mycotoxins|Pesticides|Heavy\s*Metals|Foreign\s*Matter|'
        r'(?:GC(?:MS)?|LC(?:MS)?)\s*Pesticides|Moisture|Water\s*Activity)'
        r'[^\n]*?\s+(Pass|Fail|Complete|Not\s*Tested|Tested)',
        text, re.IGNORECASE,
    )
    for name, status in status_patterns:
        analysis_key = _classify_analysis(name)
        status_val = status.strip().lower()
        if status_val == 'complete':
            status_val = 'complete'
        obs[f'{analysis_key}_status'] = status_val
        if status_val not in ('not tested',):
            analyses.append(analysis_key)

    # Total THC/CBD from page 1 summary boxes.
    # CC layout: values on line above, labels on "Total THC" line.
    # Values line: "70.96% ND 84.76%" (single-space separated)
    # Labels line: "Total THC Total CBD Total Cannabinoids"
    # AZ: "(Q3)" qualifier line may intervene.
    
    lines_list = text.split('\n')
    for idx, line in enumerate(lines_list):
        if re.search(r'\bTotal\s+THC\b', line) and idx > 0:
            # Skip formula lines.
            if '=' in line and ('THCa' in line or '0.877' in line):
                continue
            # Skip data table rows: "Total THC  25.2924  252.9240"
            if re.match(r'\s*Total\s+THC\s+[\d.]+', line):
                continue
            
            # Extract label order from the label line.
            label_order = []
            label_patterns = [
                (r'Total\s+THC', 'total_thc'),
                (r'Total\s+CBD', 'total_cbd'),
                (r'Total\s+Cannabinoids?\s*(?:\(Neutral\))?', 'total_cannabinoids'),
                (r'Total\s+Terpenes', 'total_terpenes'),
                (r'Total\s+CBG', 'total_cbg'),
                (r'Sum\s+of\s+Cannabinoids', 'total_cannabinoids'),
                (r'Moisture', 'moisture_content'),
            ]
            for pattern, field in label_patterns:
                m = re.search(pattern, line, re.IGNORECASE)
                if m:
                    label_order.append((m.start(), field))
            label_order.sort()
            
            # Find the values line (skip Q3/qualifier and analyte data lines).
            values_idx = idx - 1
            while values_idx >= max(0, idx - 6):
                prev = lines_list[values_idx].strip()
                # Skip blank lines and Q3 qualifier lines.
                if not prev or re.match(r'^\s*\(Q3\)\s*(\(Q3\)\s*)*$', prev):
                    values_idx -= 1
                    continue
                # Skip "Not Tested" standalone lines.
                if prev.lower() in ('not tested', 'nt'):
                    values_idx -= 1
                    continue
                # Skip analyte data rows (Arsenic 0.20 ND, etc.)
                if re.match(r'^[A-Z][a-z]+\s+[\d.]+\s+', prev):
                    values_idx -= 1
                    continue
                # Skip unit header lines (PPM, µg/g, etc.)
                if re.match(r'^(?:PPM|µg|ug|mg|CFU|%)\s', prev, re.IGNORECASE):
                    values_idx -= 1
                    continue
                # This line should contain the summary values.
                break
            
            if values_idx < 0:
                continue
            
            values_line = lines_list[values_idx].strip()
            
            # Extract value tokens from the values line.
            # Match: numbers with optional %, ND, <LOQ, NT, NR
            value_tokens = re.findall(
                r'([\d.]+\s*%?|ND|<LOQ|NT|NR|Not\s*Tested)',
                values_line,
            )
            # Clean tokens.
            clean_values = []
            for tok in value_tokens:
                tok = tok.strip().rstrip('%').strip()
                tok = re.sub(r'\s*mg/(?:serving|unit|container|g)', '', tok)
                clean_values.append(tok)
            
            # Match values to labels by position.
            for vi, (_, field) in enumerate(label_order):
                if vi < len(clean_values):
                    val = _parse_number(clean_values[vi])
                    if not obs.get(field):
                        obs[field] = val
            
            break  # First occurrence only.

    # Total terpenes from standalone terpene section.
    if not obs.get('total_terpenes'):
        tt_match = re.search(
            r'([\d.]+)\s*%?\s*\n\s*Total\s*Terpenes',
            text,
        )
        if tt_match:
            obs['total_terpenes'] = _parse_number(tt_match.group(1))

    # Moisture content.
    moist_match = re.search(
        r'([\d.]+)\s*%?\s*\n?\s*Moisture(?:\s*Content)?',
        text,
    )
    if moist_match:
        obs['moisture_content'] = _parse_number(moist_match.group(1))

    # Water activity.
    wa_match = re.search(
        r'([\d.]+)\s*aw?\s*\n?\s*Water\s*Activity',
        text,
    )
    if wa_match:
        obs['water_activity'] = _parse_number(wa_match.group(1))

    return obs, list(set(analyses))


# ── Results Parsing ───────────────────────────────────────────────

def _parse_analyte_line(line: str, analysis: str, units: str) -> Optional[Dict]:
    """Parse a single analyte result line from text.

    Handles various column layouts:
        Cannabinoids: Analyte LOQ [LOD] Result(%) Result(mg/g)
        Terpenes:     Analyte LOQ Result(%) Result(mg/g)
        Pesticides:   Analyte LOD LOQ Limit Result Status
        Heavy Metals: Analyte LOD LOQ Limit Result Status
        Microbials:   Analyte [Limit] Result Status
        Mycotoxins:   Analyte LOD LOQ Limit Result Status
        Solvents:     Analyte LOD LOQ Limit Result Status
    """
    line = line.strip()
    if not line:
        return None

    # Skip header/footer/total lines.
    skip_patterns = [
        r'^Analyte\b', r'^%\s', r'^mg/g\s', r'^PPM\s', r'^µg',
        r'^ug', r'^CFU', r'^RFU', r'^Date\s*Tested',
        r'^Method:', r'^SOP', r'^Instrument:', r'^LOQ\s*=',
        r'^Note:', r'^Entered\s*By', r'^Total\s*THC\s*=',
        r'^Total\s*CBD\s*=', r'^1\s*Unit\s*=', r'^Total\s*theoretical',
        r'^Includes\s', r'^GCA\s*does\s*not',
        r'^ND\s*=', r'^NR\s*=', r'^Primary\s*Aromas',
        r'^Orange|^Cinnamon|^Pine|^Hops|^Lavender|^Lemon',
        r'^Sweet|^Earthy|^Chamomile|^Clove|^Wood|^Basil',
        r'^\d+\s+of\s+\d+', r'^Quali\x00er',
        r'^Equipment\s*Used', r'^Sampling',
        r'^Con\x00dent|^Condent|^Confident',
        r'^Report\s*Notes', r'^See\s*Report',
        r'^Test\s*Comment', r'^Comment:',
        r'^Results\s*based\s*on', r'^If\s*sampled\s*by',
        r'^LOQ\s*=\s*Limit', r'^ND\s*=\s*Not',
        r'^Pesticides?\s*tested\s*by',
        r'^Residual\s*Solvents?\s*tested\s*by',
        r'^Mycotoxin\s*contamination',
        r'^Heavy\s*Metal\s*contamination',
        r'^[\d.]+%\s+[\d.]+%',  # Summary box lines: "70.96% ND 84.76%"
        r'^[\d.]+%\s+(?:ND|<LOQ)',  # "70.96% ND"
        r'^[\d.]+\s*mg/(?:unit|serving)',  # "884.9010 mg/unit"
        r'^\(Q3\)',  # Arizona Q3 flags
    ]
    for pattern in skip_patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return None

    # Split by whitespace, preserving multi-word analyte names.
    # Strategy: find the analyte name (text part) then the numeric values.
    parts = re.split(r'\s{2,}|\t', line)
    if len(parts) < 2:
        # Try single-space split for tightly packed data.
        parts = line.split()
        if len(parts) < 2:
            return None

    # Find where the numeric data starts.
    name_parts = []
    numeric_start = 0
    for i, part in enumerate(parts):
        # Check if this part looks numeric or is ND/<LOQ/Pass/Fail.
        cleaned = part.strip().upper()
        if re.match(r'^[\d.<>]+$|^ND$|^NT$|^NR$|^<LOQ$|^PASS$|^FAIL$|^TESTED$|^NOT\b', cleaned):
            numeric_start = i
            break
        name_parts.append(part)
    else:
        return None  # No numeric data found.

    analyte_name = ' '.join(name_parts).strip()
    if not analyte_name or len(analyte_name) < 2:
        return None

    # Strip CAS numbers from analyte names (e.g., "THCa 23978-85-0").
    analyte_name = re.sub(r'\s+\d{2,6}-\d{2}-\d{1,2}$', '', analyte_name).strip()

    # Strip qualifier flags from names (e.g., "CBCa Q3", "Bifenthrin M2").
    analyte_name = re.sub(r'\s+[A-Z]\d+$', '', analyte_name).strip()

    # Skip "Total" summary rows (Total THC, Total CBD, Total, etc.)
    # but allow "Total Aflatoxins", "Total Mycotoxins", etc.
    if analyte_name.lower().startswith('total') and analyte_name.lower() not in (
        'total aflatoxins', 'total mycotoxins',
    ):
        return None

    numeric_parts = parts[numeric_start:]

    result = {
        'analysis': analysis,
        'key': _snake_case(analyte_name),
        'name': analyte_name,
        'units': units,
    }

    # Parse based on analysis type and number of numeric columns.
    if analysis == 'cannabinoids':
        # Cannabinoids: LOQ [LOD] Result(%) Result(mg/g) [CAS#]
        # Filter out CAS numbers.
        nums = [p for p in numeric_parts if not re.match(r'^\d+-\d+-\d+$', p.strip())]
        if len(nums) >= 2:
            result['loq'] = _parse_number(nums[0])
            result['value'] = _parse_number(nums[-2]) if len(nums) >= 3 else _parse_number(nums[-1])
            result['mg_g'] = _parse_number(nums[-1])

    elif analysis == 'terpenes':
        # Terpenes: LOQ Result(%) Result(mg/g) [Q-flag]
        nums = [p for p in numeric_parts if not re.match(r'^Q\d+$', p.strip())]
        if len(nums) >= 2:
            result['loq'] = _parse_number(nums[0])
            result['value'] = _parse_number(nums[1]) if len(nums) >= 2 else None
            if len(nums) >= 3:
                result['mg_g'] = _parse_number(nums[2])

    elif analysis in ('pesticides', 'heavy_metals', 'residual_solvents', 'mycotoxins'):
        # Safety: LOD LOQ Limit Result Status [Q-flag]
        # or:     LOQ Limit Result [Q-flag] Status
        nums = [p for p in numeric_parts if not re.match(r'^[A-Z]\d+$', p.strip())]
        # Find status.
        status = None
        status_idx = None
        for idx, p in enumerate(nums):
            if p.strip().upper() in ('PASS', 'FAIL', 'TESTED', 'NT'):
                status = p.strip().lower()
                status_idx = idx
                break
        if status:
            result['status'] = status
            value_nums = nums[:status_idx]
        else:
            value_nums = nums

        if len(value_nums) >= 4:
            result['lod'] = _parse_number(value_nums[0])
            result['loq'] = _parse_number(value_nums[1])
            result['limit'] = _parse_number(value_nums[2])
            result['value'] = _parse_number(value_nums[3])
        elif len(value_nums) >= 3:
            result['loq'] = _parse_number(value_nums[0])
            result['limit'] = _parse_number(value_nums[1])
            result['value'] = _parse_number(value_nums[2])
        elif len(value_nums) >= 2:
            result['limit'] = _parse_number(value_nums[0])
            result['value'] = _parse_number(value_nums[1])
        elif len(value_nums) >= 1:
            result['value'] = _parse_number(value_nums[0])

    elif analysis == 'microbials':
        # Microbials: [LOQ] [Limit] Result Status
        nums = numeric_parts
        status = None
        for p in nums:
            if p.strip().upper() in ('PASS', 'FAIL', 'TESTED'):
                status = p.strip().lower()
        result['status'] = status
        # The result is often qualitative.
        for p in nums:
            val = p.strip()
            if val.upper() in ('PASS', 'FAIL', 'TESTED'):
                continue
            if 'Not Detected' in val or 'ND' == val.upper() or 'Absence' in val:
                result['value'] = None
                break
            parsed = _parse_number(val)
            if parsed is not None:
                result['value'] = parsed
                break

    else:
        # Generic: try to get a value.
        if numeric_parts:
            result['value'] = _parse_number(numeric_parts[-1])

    return result


def _parse_results_from_text(pdf) -> Tuple[List[Dict], List[str]]:
    """Extract all analyte results from the PDF text.

    Iterates through each page, identifies analysis sections,
    and parses analyte lines within each section.
    """
    results = []
    analyses = set()

    for page in pdf.pages:
        text = _deligature(page.extract_text() or '')
        if _is_cover_sheet(text):
            continue

        lines = text.split('\n')
        current_analysis = None
        current_units = 'percent'
        section_header_text = ''

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Louisiana/Orion footer boundary: once the legal disclaimer
            # begins, we're past the analyte tables. Stop parsing analytes so
            # disclaimer sentences don't leak in as fake result rows. Gated to
            # LA markers, so no other state's parsing changes.
            low = stripped.lower()
            if any(mk in low for mk in _LA_FOOTER_MARKERS):
                current_analysis = None
                continue

            # Detect analysis section headers.
            section_match = re.match(
                r'^(Cannabinoids|Terpenes|Pesticides|Heavy\s*Metals|'
                r'Microbials|Mycotoxins|Residual\s*Solvents|'
                r'Foreign\s*Matter|Moisture|Water\s*Activity|'
                r'(?:GC|LC|GCMS|LCMS)\s*Pesticides|'
                r'Cannabinoids\s+by\s+\S+|'
                r'Pesticides\s+by\s+\S+|'
                r'Microbials\s+by\s+\S+|'
                r'Mycotoxins\s+by\s+\S+|'
                r'Terpenes\s+by\s+\S+|'
                r'Heavy\s*Metals\s+by\s+\S+|'
                r'Residual\s*Solvents\s+by\s+\S+)',
                stripped,
                re.IGNORECASE,
            )
            if section_match:
                header = section_match.group(1)
                current_analysis = _classify_analysis(header)
                analyses.add(current_analysis)
                section_header_text = stripped
                continue

            # Detect units from column header lines.
            if current_analysis and re.match(
                r'^(Analyte|%|µg|ug|mg|PPM|CFU|RFU)', stripped, re.IGNORECASE,
            ):
                current_units = _detect_units_from_header(
                    stripped, current_analysis,
                )
                continue

            # Parse analyte lines.
            if current_analysis:
                result = _parse_analyte_line(
                    stripped, current_analysis, current_units,
                )
                if result:
                    results.append(result)

    return results, sorted(analyses)


def _parse_two_column_results(text: str, analysis: str, units: str) -> List[Dict]:
    """Parse results from two-column layout pages.

    Many Confident Cannabis COAs use a side-by-side two-column
    layout for pesticides and terpenes where the left and right
    halves each contain separate analyte data.
    """
    # This is handled naturally by pdfplumber's text extraction
    # which typically merges the columns. The _parse_analyte_line
    # function handles lines that have data from both columns
    # (the second column's analyte name starts mid-line).
    return []


def _parse_primary_aromas(pdf) -> List[str]:
    """Extract Primary Aromas from terpene pages."""
    aromas = []
    for page in pdf.pages:
        text = page.extract_text() or ''
        aroma_match = re.search(
            r'Primary\s*Aromas\s*\n(.+?)(?:\n\s*Date\s*Tested|\n\s*LOQ|\n\s*Con)',
            text, re.DOTALL,
        )
        if aroma_match:
            aroma_text = aroma_match.group(1).strip()
            # Aromas are typically space-separated words on one line.
            for line in aroma_text.split('\n'):
                words = line.strip().split()
                for word in words:
                    w = word.strip()
                    if w and len(w) > 2 and w[0].isupper() and not re.match(r'^\d', w):
                        aromas.append(w.lower())
            if aromas:
                break
    return aromas


# ── Main Entry Points ─────────────────────────────────────────────

def parse_cc_pdf(
        parser: Any = None,
        doc: str = '',
    ) -> Dict:
    """Parse a Confident Cannabis/LIMS COA PDF directly from the file.

    This is the primary parsing function. Extracts all data from the
    PDF using pdfplumber text extraction — no network access required.

    Args:
        parser: Optional CoADoc instance (backwards compatibility).
        doc:    Path to the COA PDF file.

    Returns:
        Dict with all extracted COA data.
    """
    # Handle argument order flexibility.
    pdf_path = doc if doc else parser
    if isinstance(parser, str) and isinstance(doc, str) and doc:
        pdf_path = doc
    elif isinstance(parser, str) and not doc:
        pdf_path = parser
        parser = None

    if not pdf_path or not isinstance(pdf_path, str):
        raise ValueError('No PDF path provided.')

    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            raise ValueError(f'Empty PDF: {pdf_path}')

        # Find the first COA page (skip AZ cover sheets).
        coa_start = 0
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ''
            if _is_cover_sheet(page_text):
                coa_start = i + 1
            else:
                break

        if coa_start >= len(pdf.pages):
            raise ValueError(f'No COA pages found in: {pdf_path}')

        # Extract full text from the first COA page.
        page1_text = _deligature(pdf.pages[coa_start].extract_text() or '')

        # ── Parse lab header ──────────────────────────────
        obs = _parse_lab_header(page1_text)

        # ── Parse sample metadata ─────────────────────────
        obs.update(_parse_sample_metadata(page1_text))

        # ── Parse client/producer info ────────────────────
        obs.update(_parse_client_info(page1_text))

        # ── Louisiana / Orion Therapeutics variant override ──
        # Corrects lab/producer/product metadata for the Orion (Confident
        # LIMS) template. Gated to Orion COAs, so no other state is affected.
        if _is_la_orion(page1_text):
            obs.update(_parse_la_orion_metadata(page1_text))

        # ── Parse summary statuses ────────────────────────
        summary_data, summary_analyses = _parse_summary(page1_text)
        obs.update(summary_data)

        # ── Parse all results from text ───────────────────
        results, text_analyses = _parse_results_from_text(pdf)

        # Louisiana/Orion: enforce the null≠zero doctrine for contaminant
        # panels. On these COAs a 0.0 in a metals/pesticide/microbial/mycotoxin/
        # solvent row is a non-detect the shared parser flattened to zero — a
        # true measured 0.0 does not occur in these panels. Convert to null.
        # Gated to Orion COAs; other states are untouched.
        if _is_la_orion(page1_text):
            _CONTAM = {'heavy_metals', 'pesticides', 'microbials',
                       'mycotoxins', 'residual_solvents'}
            for r in results:
                if r.get('analysis') in _CONTAM and r.get('value') == 0.0:
                    r['value'] = None

        # Merge analyses lists.
        all_analyses = sorted(set(summary_analyses + text_analyses))

        # ── Parse primary aromas ──────────────────────────
        aromas = _parse_primary_aromas(pdf)
        if aromas:
            obs['predicted_aromas'] = aromas

        # ── Compute totals if not already set ─────────────
        if results:
            # Total terpenes.
            if not obs.get('total_terpenes'):
                terp_sum = sum(
                    r.get('value', 0) or 0
                    for r in results
                    if r['analysis'] == 'terpenes'
                    and r['key'] not in ('total_terpenes',)
                    and r.get('value') is not None
                    and r.get('value', 0) > 0
                )
                if terp_sum > 0:
                    obs['total_terpenes'] = round(terp_sum, 5)

        # ── Determine LIMS variant ────────────────────────
        full_text = _deligature('\n'.join(
            (pdf.pages[i].extract_text() or '')
            for i in range(min(3, len(pdf.pages)))
        )).lower()
        if 'confidentlims' in full_text or 'confident lims' in full_text:
            obs['lims'] = 'Confident LIMS'
        else:
            obs['lims'] = 'Confident Cannabis'

        # ── Finalize observation ──────────────────────────
        obs = {**CONFIDENT_CANNABIS, **obs}
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
        obs['lab_id'] = obs.get('lab_id', obs.get('sample_id', ''))

        # PDF filename.
        obs['coa_pdf'] = pdf_path.replace('\\', '/').split('/')[-1]

    return obs


def parse_cc_coa(
        parser: Any = None,
        doc: str = '',
        **kwargs,
    ) -> Dict:
    """Parse a Confident Cannabis/LIMS COA PDF or URL.

    This is the main entry point registered in the algorithm registry.
    Always parses from the PDF directly (offline-first).

    Args:
        parser: Optional CoADoc instance (backwards compatibility).
        doc:    Path to the COA PDF file.

    Returns:
        Dict with all extracted COA data.
    """
    # Handle argument order: (parser, doc) or (doc,)
    if isinstance(parser, str) and not doc:
        doc = parser
        parser = None
    elif isinstance(parser, str) and isinstance(doc, str):
        # Legacy call: parse_cc_coa(parser_instance, pdf_path)
        pass

    if isinstance(doc, str) and doc.startswith('http'):
        raise ValueError(
            'URL parsing is no longer supported in the offline-first engine. '
            'Provide the PDF file path instead.'
        )

    return parse_cc_pdf(parser, doc)


def is_confident_cannabis(pdf_path: str) -> bool:
    """Check if a PDF is a Confident Cannabis/LIMS COA.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        True if the PDF is identified as a Confident Cannabis/LIMS COA.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return bool(_find_cc_identifier(pdf))
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
            print('Usage: python confidentcannabis.py <pdf_file> [...]')
            sys.exit(1)

    for pdf_file in test_files:
        pdf_path = (
            os.path.join(test_dir, pdf_file)
            if not os.path.isabs(pdf_file)
            else pdf_file
        )
        if not os.path.exists(pdf_path):
            print(f'Not found: {pdf_path}')
            continue
        try:
            data = parse_cc_coa(None, pdf_path)
            results = json.loads(data.get('results', '[]'))
            analyses = json.loads(data.get('analyses', '[]'))
            print(f'\n{"="*60}')
            print(f'OK {pdf_file}')
            print(f'  Product:  {data.get("product_name", "?")}')
            print(f'  Type:     {data.get("product_type", "?")}')
            print(f'  Lab:      {data.get("lab", "?")}')
            print(f'  Producer: {data.get("producer", "?")}')
            print(f'  Date:     {data.get("date_tested", "?")}')
            print(f'  THC:      {data.get("total_thc", "?")}%')
            print(f'  CBD:      {data.get("total_cbd", "?")}%')
            print(f'  Analyses: {analyses}')
            print(f'  Results:  {len(results)} analytes')
            print(f'  LIMS:     {data.get("lims", "?")}')
            print(f'  Status:   {data.get("status", "?")}')
        except Exception as e:
            print(f'\nFAIL {pdf_file}: {e}')
            import traceback
            traceback.print_exc()