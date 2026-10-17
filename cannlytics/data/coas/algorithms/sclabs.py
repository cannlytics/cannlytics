"""
Parse SC Labs COA — COA Doc Hybrid Algorithm (Offline-First)
Copyright (c) 2022-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/8/2022
Updated: 10/13/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse SC Labs COA PDFs directly from the PDF text and tables — no
    network access required. This is the modernized offline-first engine
    that extracts all data from the PDF itself using pdfplumber text
    extraction, table extraction, and regex-based field parsing.

    SC Laboratories California LLC is the largest cannabis testing lab
    in California by COA volume (~52.8% of the CA corpus). They operate
    from Santa Cruz, CA and test flower, concentrates, edibles,
    pre-rolls, topicals, and other cannabis product types.

    Identification:
        SC Labs COAs contain 'sclabs.com' in the footer of every page:
            "SC Laboratories California LLC. | 100 Pioneer Street, ..."
        Also identifiable by:
            - "Regulatory Compliance Testing" header
            - "SC Labs" or "SC Laboratories" text
            - "sclabs.com" URL
            - License number: C8-0000013-LIC

    Format notes:
        * Page 1: Summary page with metadata, cannabinoid/terpene
          totals, and safety analysis summary (pass/fail per analysis)
        * Pages 2+: Detailed results in two-column layout
        * Tables are proper PDF tables (pdfplumber extract_tables works)
        * LOD/LOQ format: "X / Y" (space-slash-space)
        * Results: numeric values, ND, <LOQ, or None
        * Status: PASS or FAIL per analyte
        * Action limits: "≥ LOD" (Category 1 pesticides) or numeric
        * Edibles: front-page totals in mg/unit (the cannabinoid table
          still prints RESULT (mg/g) and RESULT (%)), no terpenes
        * Flower: includes moisture %, dry-weight calculation
        * Concentrates: includes terpene profile (39 tested)
        * Two COA format eras:
          - 2021-2022: "sc labs™" branding, slightly different layout
          - 2023-2026: "SC Labs®" branding, standardized layout
        * pdfplumber tables (2023-2026): the column header is not a
          row of the table (it is a table of its own, or text above the
          table, or merged into the first row), and a row's columns can
          come merged into fewer cells, e.g.
              ['THCVa', '0.07 / 0.20', '±0.231 4.61 0.461']
              ['n-Pentane', '20 / 50', '5000 ±50.4 646 PASS']
          so rows are read by token, not by cell position
          (_parse_table_row).

    Fixes (10/13/2026), from a benchmark of 4 California COAs
    (2023-2026: a concentrate, a vape, a concentrate and an edible)
    read by four Claude models that agree with each other:
        * The first row of every table was dropped: table[0] was taken
          for the column header, which pdfplumber does not put in the
          table. THCa (or the edible's ∆9-THC), the largest terpene,
          aldicarb, abamectin, cyfluthrin, aflatoxin B1,
          1,2-dichloroethane, acetone, arsenic and STEC were missing,
          and one-row tables (water activity) were skipped whole. A
          header is now recognized by its words, wherever it is: in
          the table, in a header-only table before it, or merged into
          the first row.
        * Cannabinoids and terpenes were 0.0 for every analyte (thcva
          0.0 for 0.461 %, cbg 0.0 for 0.0100 %, beta-myrcene 0.0 mg/g
          for 1.0049 %): the result was read from a fixed cell
          (cells[3], cells[4] or cells[-1]) that holds several merged
          columns ("±0.231 4.61 0.461"), the parse failed, and a
          failed parse was filled in as 0.0. Rows are now read by
          token: the LOD/LOQ pair, the uncertainty ("±..." or "N/A"),
          then RESULT (mg/g) and RESULT (%). Both analyses are read
          from the percent column (units 'percent'; terpenes were
          labeled 'mg/g'), checked against the mg/g column (10 times
          larger), and LOD/LOQ, printed in mg/g, are given in percent.
        * Residual solvents, pesticides, heavy metals and mycotoxins
          were None for every analyte, detected or not (n-pentane
          646 ug/g and ethanol 101 ug/g were lost), and their limits
          and PASS/FAIL were dropped: rows merged into fewer than four
          cells were not read. The result is now the value after the
          uncertainty, or the printed qualifier, before PASS/FAIL; a
          number is never taken from the LOD/LOQ or action limit
          columns (a lone number that may be the action limit is left
          unread).
        * Non-detects keep their qualifier (cannlytics.data.coas.schema
          parse_result_value): "ND" is value None, qualifier 'ND';
          "<LOQ" is value None, qualifier '<LOQ' (with the row's LOQ);
          "<x" gives 'loq' x when the row has none; ">x" is '>ULOQ';
          "N/A" is 'NR'. A failed parse is value None (it was 0.0), and
          0.0 only comes from a printed zero. Every result row carries
          'qualifier'. Microbiology and foreign material rows ("Not
          Detected in 1g ND PASS", "> 1 per 3 grams 0 PASS") are read
          from their end, and their action limit ("> 25%") is never
          read as the result.
        * Front-page totals: "Total CBD: ND" is no longer 0.0 (it is
          left unset), and a total printed in mg/unit (edibles: "Total
          THC: 98.772 mg/unit") is kept as '<key>_per_unit' instead of
          in the percent field (total_thc).

Data Points:

    ✓ product_name, product_type
    ✓ date_tested, date_received, date_collected
    ✓ batch_number, batch_size, sample_size, unit_mass, serving_size
    ✓ lab, lab_license_number, lab_address, lab_city, lab_state,
      lab_zipcode, lab_phone, lab_website
    ✓ producer, producer_license_number, producer_address
    ✓ distributor, distributor_license_number, distributor_address
    ✓ sample_id (lab's CoA ID / Sample ID)
    ✓ total_thc, total_cbd, total_cannabinoids, total_terpenes
    ✓ sum_of_cannabinoids
    ✓ status (overall batch pass/fail)
    ✓ analyses (list of analysis types)
    ✓ results (list of analyte result dicts)
    ✓ metrc_ids (Source Metrc UID)
    ✓ moisture_content
    ✓ coa_id (CoA ID from footer)
"""
# Standard imports:
import hashlib
import json
import logging
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

# External imports:
import pdfplumber

# Internal imports:
from cannlytics.data.coas.schema import parse_result_value

_log = logging.getLogger(__name__)

# ── SC Labs Constants ──────────────────────────────────────────────

SC_LABS = {
    'coa_algorithm': 'sclabs.py',
    'coa_algorithm_entry_point': 'parse_sc_labs_coa',
    'lims': 'SC Labs',
    'url': 'https://sclabs.com',
    'lab': 'SC Labs',
    'lab_website': 'https://sclabs.com',
    'lab_phone': '(866) 435-0709',
    'lab_email': 'info@sclabs.com',
    'lab_address': '100 Pioneer Street, Suite E, Santa Cruz, CA 95060',
    'lab_street': '100 Pioneer Street, Suite E',
    'lab_city': 'Santa Cruz',
    'lab_state': 'CA',
    'lab_zipcode': '95060',
    'lab_license_number': 'C8-0000013-LIC',
}

# Standard analysis name mappings for SC Labs section headers.
ANALYSIS_SECTION_MAP = {
    'cannabinoid': 'cannabinoids',
    'terpenoid': 'terpenes',
    'terpene': 'terpenes',
    'category 1 pesticide': 'pesticides',
    'category 2 pesticide': 'pesticides',
    'pesticide': 'pesticides',
    'mycotoxin': 'mycotoxins',
    'category 1 residual solvent': 'residual_solvents',
    'category 2 residual solvent': 'residual_solvents',
    'residual solvent': 'residual_solvents',
    'heavy metal': 'heavy_metals',
    'microbiology': 'microbials',
    'microbial impurities': 'microbials',
    'foreign material': 'foreign_matter',
    'water activity': 'water_activity',
    'moisture': 'moisture',
}

# Standard units per analysis type.
STANDARD_UNITS = {
    'cannabinoids': 'percent',
    'terpenes': 'mg/g',
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
    'Δ9-THC': 'delta_9_thc',
    '∆9-THC': 'delta_9_thc',
    'Δ8-THC': 'delta_8_thc',
    '∆8-THC': 'delta_8_thc',
    'Δ9THC': 'delta_9_thc',
    'Δ8THC': 'delta_8_thc',
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
    'β-Caryophyllene': 'beta_caryophyllene',
    'β Caryophyllene': 'beta_caryophyllene',
    'β-Pinene': 'beta_pinene',
    'β Pinene': 'beta_pinene',
    'β-Ocimene': 'beta_ocimene',
    'β Ocimene': 'beta_ocimene',
    'α-Humulene': 'alpha_humulene',
    'α Humulene': 'alpha_humulene',
    'α-Pinene': 'alpha_pinene',
    'α Pinene': 'alpha_pinene',
    'α-Bisabolol': 'alpha_bisabolol',
    'α Bisabolol': 'alpha_bisabolol',
    'α-Terpinene': 'alpha_terpinene',
    'α Terpinene': 'alpha_terpinene',
    'α-Phellandrene': 'alpha_phellandrene',
    'α Phellandrene': 'alpha_phellandrene',
    'α-Cedrene': 'alpha_cedrene',
    'α Cedrene': 'alpha_cedrene',
    'γ-Terpinene': 'gamma_terpinene',
    'γ -Terpinene': 'gamma_terpinene',
    'γ Terpinene': 'gamma_terpinene',
    'Δ3-Carene': 'delta_3_carene',
    '∆3-Carene': 'delta_3_carene',
    '3 Carene': 'delta_3_carene',
    'trans-β-Farnesene': 'trans_beta_farnesene',
    'trans-β- Farnesene': 'trans_beta_farnesene',
    'Caryophyllene Oxide': 'caryophyllene_oxide',
    'Sabinene Hydrate': 'sabinene_hydrate',
    'Geranyl Acetate': 'geranyl_acetate',
    'p-Cymene': 'p_cymene',
    '(-)-Isopulegol': 'isopulegol',
    'R-(+)-Pulegone': 'pulegone',
    'Piperonyl Butoxide': 'piperonyl_butoxide',
    'Piperonylbu- toxide': 'piperonyl_butoxide',
    'Piperonylbutoxide': 'piperonyl_butoxide',

    # Pesticides (common multi-word / hyphenated names)
    'Dichlorvos (DDVP)': 'dichlorvos',
    'DDVP (Dichlorvos)': 'dichlorvos',
    'Dichloromethane (Methylene Chloride)': 'dichloromethane',
    'Methylene chloride': 'dichloromethane',
    'Pentachloronitrobenzene (Quintozene)*': 'pentachloronitrobenzene',
    'Pentachloronitrobenzene*': 'pentachloronitrobenzene',
    'Pentachloronitro- benzene*': 'pentachloronitrobenzene',
    'Chlorantranilip- role': 'chlorantraniliprole',
    'Chlorantraniliprole': 'chlorantraniliprole',
    'Parathion-methyl': 'parathion_methyl',
    'Methyl parathion': 'parathion_methyl',
    'Kresoxim-methyl': 'kresoxim_methyl',
    'Ethoprop(hos)': 'ethoprophos',
    'Ethoprophos': 'ethoprophos',
    'Piperonyl Butoxide': 'piperonyl_butoxide',

    # Residual solvents
    '2-Propanol (Isopropyl Alcohol)': 'isopropyl_alcohol',
    'Isopropyl Alcohol': 'isopropyl_alcohol',
    '1,2-Dichloroethane': 'dichloroethane_1_2',
    'Ethyl Acetate': 'ethyl_acetate',
    'Ethyl Ether': 'ethyl_ether',
    'Ethylene Oxide': 'ethylene_oxide',
    'Total Xylenes': 'total_xylenes',
    'n-Butane': 'n_butane',
    'Butane': 'n_butane',
    'n-Heptane': 'n_heptane',
    'Heptane': 'n_heptane',
    'n-Hexane': 'n_hexane',
    'Hexane': 'n_hexane',
    'n-Pentane': 'n_pentane',
    'Pentane': 'n_pentane',

    # Mycotoxins
    'Aflatoxin B1': 'aflatoxin_b1',
    'Aflatoxin B2': 'aflatoxin_b2',
    'Aflatoxin G1': 'aflatoxin_g1',
    'Aflatoxin G2': 'aflatoxin_g2',
    'Total Aflatoxin': 'total_aflatoxin',
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
    'Salmonella spp.': 'salmonella_spp',
    'Shiga toxin-producing Escherichia coli': 'stec',

    # Foreign material
    'Hair Count': 'hair_count',
    'Insect Fragment Count': 'insect_fragment_count',
    'Mammalian Excreta Count': 'mammalian_excreta_count',
    'Total Sample Area Covered by an Imbedded Foreign Material': 'imbedded_foreign_material',
    'Total Sample Area Covered by Mold': 'mold_coverage',
    'Total Sample Area Covered by Sand, Soil, Cinders, or Dirt': 'sand_soil_coverage',

    # Water activity
    'Water Activity': 'water_activity',
}

# Known non-analyte keywords to skip in table parsing.
SKIP_PATTERNS = {
    'SUM OF CANNABINOIDS', 'TOTAL CANNABINOIDS', 'TOTAL TERPENOIDS',
    'TOTAL THC', 'TOTAL CBD', 'TOTAL CBG', 'TOTAL THCV', 'TOTAL CBC',
    'TOTAL CBDV', 'TOTAL CBDV', 'UNIT MASS',
    'Δ9-THC per Unit', '∆9-THC per Unit', 'Δ9THC per Unit',
    'Total THC per Unit', 'Total CBD per Unit',
    'CBD per Unit', 'Total THC per Serving',
    'Total CBD per Serving', 'Δ9-THC per Serving',
    '∆9-THC per Serving',
    'Sum of Cannabinoids per Unit', 'Sum of Cannabinoids per Serving',
    'Total Cannabinoids per Unit', 'Total Cannabinoids per Serving',
    'CBD per Serving',
    'COMPOUND', 'Continued on next page',
}

# Known analysis section header patterns in SC Labs results pages.
SECTION_HEADER_RE = re.compile(
    r'(CANNABINOID|TERPENOID|TERPENE|'
    r'CATEGORY\s+\d\s+PESTICIDE|'
    r'MYCOTOXIN|'
    r'CATEGORY\s+\d\s+RESIDUAL\s+SOLVENT|'
    r'HEAVY\s+METAL|'
    r'MICROBIOLOGY|MICROBIAL\s+IMPURITIES|'
    r'FOREIGN\s+MATERIAL|'
    r'WATER\s+ACTIVITY|'
    r'MOISTURE)\s+TEST\s+RESULT',
    re.IGNORECASE,
)

# ── Utility Functions ──────────────────────────────────────────────

def _snake_case(text: str) -> str:
    """Convert analyte display name to snake_case key.

    Uses ANALYTE_KEY_MAP for exact matches first, then falls back
    to regex normalization for unknown analytes.
    """
    stripped = text.strip()
    # Exact match.
    if stripped in ANALYTE_KEY_MAP:
        return ANALYTE_KEY_MAP[stripped]
    # Try with common cleanup.
    cleaned = re.sub(r'\s+', ' ', stripped)
    if cleaned in ANALYTE_KEY_MAP:
        return ANALYTE_KEY_MAP[cleaned]
    # Fallback: normalize to snake_case.
    s = stripped.lower().strip()
    # Greek letter normalization.
    s = s.replace('α', 'alpha_').replace('β', 'beta_')
    s = s.replace('γ', 'gamma_').replace('δ', 'delta_')
    s = s.replace('∆', 'delta_')
    # Remove asterisks, parenthetical notes.
    s = re.sub(r'\*+$', '', s)
    s = re.sub(r'\([^)]*\)', '', s)
    # Replace non-alphanumeric with underscore.
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s)
    s = s.strip('_')
    return s

def _parse_number(text: str) -> Optional[float]:
    """Parse a numeric string. Returns None for ND/<LOQ/NT, float otherwise."""
    if not text or not isinstance(text, str):
        return None
    text = text.strip()
    upper = text.upper()
    if upper in ('ND', 'N/A', 'NT', '', '-', 'NONE', 'N D', 'N/T'):
        return None
    if '<LOQ' in upper or '<LOD' in upper or '<' in upper:
        return None
    # Remove PASS/FAIL suffixes.
    text = re.sub(r'\s*(PASS|FAIL)\s*$', '', text, flags=re.IGNORECASE).strip()
    # Remove unit suffixes.
    text = re.sub(
        r'\s*(mg/g|mg/unit|mg/serving|%|µg/g|µg/kg|ug/g|ug/kg|ppm|ppb|cfu/g|aw|mg)\s*$',
        '', text, flags=re.IGNORECASE,
    ).strip()
    # Remove commas.
    text = text.replace(',', '')
    # Handle ± (take only the main value before ±).
    if '±' in text:
        text = text.split('±')[0].strip()
    try:
        return float(text)
    except (ValueError, TypeError):
        return None

def _parse_date(text: str) -> str:
    """Parse a date string to ISO format (YYYY-MM-DD)."""
    if not text or not isinstance(text, str):
        return ''
    text = text.strip()
    # Try common SC Labs date formats.
    for fmt in ('%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%b %d, %Y', '%B %d, %Y'):
        try:
            return datetime.strptime(text, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return text

def _parse_lod_loq(text: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse a LOD/LOQ string like '0.03 / 0.08' or '0.03/0.08'."""
    if not text or '/' not in text:
        return None, None
    parts = text.strip().split('/')
    try:
        lod = float(parts[0].strip())
        loq = float(parts[1].strip())
        return lod, loq
    except (ValueError, IndexError):
        return None, None

def _clean_text(text: str) -> str:
    """Clean null bytes and normalize whitespace in extracted text."""
    if not text:
        return ''
    # Remove null bytes (from ligature garbling).
    text = text.replace('\x00', '')
    # Normalize whitespace.
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def _is_skip_row(name: str) -> bool:
    """Check if a table row name should be skipped (not an analyte)."""
    if not name:
        return True
    cleaned = name.strip()
    # Skip exact matches.
    for pattern in SKIP_PATTERNS:
        if pattern.lower() in cleaned.lower():
            return True
    # Skip rows starting with per-unit/per-serving patterns.
    if re.match(r'(Δ|∆|Total|Sum|CBD|THC).*per\s+(Unit|Serving|package)', cleaned, re.IGNORECASE):
        return True
    # Skip if it's just a header row.
    if cleaned.upper() == 'COMPOUND':
        return True
    return False

# ── Metadata Parsing Functions ─────────────────────────────────────

def _parse_front_page_metadata(text: str, page=None) -> Dict:
    """Parse all metadata from the front page text.

    Args:
        text: Full extracted text from page 1.
        page: Optional pdfplumber page object for bbox cropping
              (needed for producer/distributor two-column extraction).
    """
    obs = {}
    lines = text.split('\n')

    # ── Date Issued ──
    date_match = re.search(r'DATE\s+ISSUED\s+(\d{1,2}/\d{1,2}/\d{4})', text)
    if date_match:
        obs['date_tested'] = _parse_date(date_match.group(1))

    # ── Overall Batch Result ──
    if 'OVERALL BATCH RESULT:' in text.upper():
        after = text.upper().split('OVERALL BATCH RESULT:')[1][:20]
        if 'PASS' in after:
            obs['status'] = 'pass'
        elif 'FAIL' in after:
            obs['status'] = 'fail'

    # ── Product Name and Type ──
    name_match = re.search(r'SAMPLE\s+NAME:\s*(.+?)(?:\n|$)', text)
    if name_match:
        obs['product_name'] = name_match.group(1).strip()

    # Product type is typically on the line after sample name.
    for i, line in enumerate(lines):
        if 'SAMPLE NAME:' in line:
            for j in range(i + 1, min(i + 3, len(lines))):
                candidate = lines[j].strip()
                if candidate and 'CULTIVATOR' not in candidate and 'SAMPLE DETAIL' not in candidate:
                    type_patterns = [
                        'Flower', 'Concentrate', 'Infused', 'Pre-Roll',
                        'Edible', 'Topical', 'Tincture', 'Vape', 'Capsule',
                        'Inhalable', 'Product',
                    ]
                    if any(tp.lower() in candidate.lower() for tp in type_patterns):
                        obs['product_type'] = candidate
                        break
            break

    # ── Cultivator / Manufacturer & Distributor ──
    # SC Labs uses a two-column layout for these blocks.
    # We MUST use bbox cropping to separate the columns correctly.
    if page is not None:
        obs.update(_parse_entity_columns(page))
    else:
        # Fallback: regex on interleaved text (less reliable).
        producer_block = _extract_block(text, 'CULTIVATOR / MANUFACTURER', 'DISTRIBUTOR')
        if not producer_block:
            producer_block = _extract_block(text, 'CULTIVATOR/MANUFACTURER', 'DISTRIBUTOR')
        if producer_block:
            obs.update(_parse_entity_block(producer_block, 'producer'))
        distributor_block = _extract_block(text, 'DISTRIBUTOR', 'SAMPLE DETAIL')
        if distributor_block:
            obs.update(_parse_entity_block(distributor_block, 'distributor'))

    # ── Sample Details ──
    sample_block = _extract_block(text, 'SAMPLE DETAIL', 'CANNABINOID ANALYSIS')
    if not sample_block:
        sample_block = _extract_block(text, 'SAMPLE DETAIL', 'Sampling Method')
    if sample_block:
        obs.update(_parse_sample_details(sample_block))

    # ── Cannabinoid Totals ──
    # A total is a percent unless printed per unit or per serving
    # (edibles: "Total THC: 98.772 mg/unit"), which is kept apart as
    # '<key>_per_unit' / '<key>_per_serving'; a total in other units is
    # not read. "ND" is left unset: a non-detect is not a measured 0.0.
    per = {'%': '', 'mg/unit': '_per_unit', 'mg/serving': '_per_serving'}
    for label, key, units_required in [
        (r'Sum\s+of\s+Cannabinoids', 'sum_of_cannabinoids', True),
        (r'Total\s+Cannabinoids', 'total_cannabinoids', True),
        (r'Total\s+THC', 'total_thc', True),
        (r'Total\s+CBD', 'total_cbd', False),
        (r'Total\s+CBG', 'total_cbg', False),
        (r'Total\s+THCV', 'total_thcv', False),
        (r'Total\s+CBC', 'total_cbc', False),
        (r'Total\s+CBDV', 'total_cbdv', False),
    ]:
        match = re.search(
            label + r':\s*([\d.,]+)\s*(%|(?i:mg\s*/\s*[a-z]+|mg\b))?', text,
        )
        if not match:
            continue
        val = _parse_number(match.group(1))
        units = re.sub(r'\s+', '', (match.group(2) or '').lower())
        if val is None or (not units and units_required):
            continue
        if units and units not in per:
            continue
        obs[key + per.get(units, '')] = val
    for pattern, key in [
        (r'Total\s+Terpenoids:\s*([\d.]+)\s*%', 'total_terpenes'),
        (r'Moisture:\s*([\d.]+)\s*%', 'moisture_content'),
    ]:
        match = re.search(pattern, text)
        if match:
            val = _parse_number(match.group(1))
            if val is not None:
                obs[key] = val

    # ── Metrc IDs ──
    metrc_match = re.search(r'Source\s+Metrc\s+UID:\s*([\s\S]*?)(?:Date\s+Collected|$)', text)
    if metrc_match:
        metrc_text = metrc_match.group(1).strip()
        metrc_ids = re.findall(r'(1A\w{20,})', metrc_text)
        if metrc_ids:
            obs['metrc_ids'] = metrc_ids

    # ── Safety Analysis Summary (analysis statuses) ──
    obs.update(_parse_safety_summary(text))

    # ── CoA ID from footer ──
    coa_match = re.search(r'CoA\s+ID:\s*(\S+)', text)
    if coa_match:
        obs['coa_id'] = coa_match.group(1).strip()

    return obs

def _extract_block(text: str, start_marker: str, end_marker: str) -> str:
    """Extract a text block between two markers."""
    try:
        start = text.index(start_marker) + len(start_marker)
        end = text.index(end_marker, start)
        return text[start:end].strip()
    except ValueError:
        return ''

def _parse_entity_columns(page) -> Dict:
    """Extract producer and distributor using bbox cropping.

    SC Labs COAs use a two-column layout for CULTIVATOR/MANUFACTURER
    (left) and DISTRIBUTOR (right). Standard text extraction interleaves
    these columns, so we use pdfplumber's bbox cropping to separate them.

    Strategy:
        1. Find the Y-coordinate of "CULTIVATOR" text
        2. Find the X-coordinate of "DISTRIBUTOR" text (column split point)
        3. Find the Y-coordinate of "SAMPLE DETAIL" text (bottom boundary)
        4. Crop left half for producer, right half for distributor
    """
    obs = {}
    words = page.extract_words()
    if not words:
        return obs

    cult_y = None
    dist_x = None
    sample_detail_y = None

    for w in words:
        if w['text'] == 'CULTIVATOR' and cult_y is None:
            cult_y = w['top']
        if w['text'] == 'DISTRIBUTOR' and dist_x is None:
            dist_x = w['x0']

    # Find SAMPLE DETAIL y-coordinate (below CULTIVATOR).
    if cult_y is not None:
        for w in words:
            if w['text'] == 'SAMPLE' and w['top'] > cult_y + 20:
                nearby = [
                    w2 for w2 in words
                    if abs(w2['top'] - w['top']) < 5
                    and w2['x0'] > w['x1']
                    and w2['x0'] < w['x1'] + 40
                ]
                for nw in nearby:
                    if nw['text'] == 'DETAIL':
                        sample_detail_y = w['top']
                        break
                if sample_detail_y:
                    break

    if not all([cult_y, dist_x, sample_detail_y]):
        return obs

    try:
        # Crop producer column (left of DISTRIBUTOR).
        left_crop = page.within_bbox((0, cult_y, dist_x - 3, sample_detail_y))
        left_text = left_crop.extract_text() or ''
        obs.update(_parse_entity_text(left_text, 'producer'))

        # Crop distributor column (right of DISTRIBUTOR start).
        right_crop = page.within_bbox((dist_x - 3, cult_y, page.width, sample_detail_y))
        right_text = right_crop.extract_text() or ''
        obs.update(_parse_entity_text(right_text, 'distributor'))
    except Exception:
        pass

    return obs

def _parse_entity_text(text: str, prefix: str) -> Dict:
    """Parse a single-column entity block (producer or distributor)."""
    obs = {}
    if not text:
        return obs

    # Business Name.
    name_match = re.search(r'Business\s+Name:\s*(.+?)(?:\nLicense|\n(?=Address)|\Z)', text, re.DOTALL)
    if name_match:
        name = name_match.group(1).strip().replace('\n', ' ')
        name = re.sub(r'\s+', ' ', name)
        obs[prefix] = name

    # License Number.
    lic_match = re.search(r'License\s+Number:\s*(\S+)', text)
    if lic_match:
        obs[f'{prefix}_license_number'] = lic_match.group(1).strip()

    # Address.
    addr_match = re.search(r'Address:\s*(.+)', text, re.DOTALL)
    if addr_match:
        address = addr_match.group(1).strip().replace('\n', ' ')
        address = re.sub(r'\s+', ' ', address)
        obs[f'{prefix}_address'] = address

        # Parse city, state, zipcode.
        state_zip = re.search(r'([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\s*$', address)
        if state_zip:
            obs[f'{prefix}_state'] = state_zip.group(1)
            obs[f'{prefix}_zipcode'] = state_zip.group(2)
            before = address[:state_zip.start()].rstrip(', ')
            parts = before.rsplit(',', 1)
            if len(parts) == 2:
                obs[f'{prefix}_street'] = parts[0].strip()
                obs[f'{prefix}_city'] = parts[1].strip()
            else:
                obs[f'{prefix}_street'] = before

    return obs

def _parse_entity_block(block: str, prefix: str) -> Dict:
    """Parse a cultivator/distributor block into structured fields."""
    obs = {}
    # Business Name.
    name_match = re.search(r'Business\s+Name:\s*(.+?)(?:\n|License)', block, re.DOTALL)
    if name_match:
        obs[prefix] = name_match.group(1).strip().replace('\n', ' ')

    # License Number.
    lic_match = re.search(r'License\s+Number:\s*(\S+)', block)
    if lic_match:
        obs[f'{prefix}_license_number'] = lic_match.group(1).strip()

    # Address.
    addr_match = re.search(r'Address:\s*(.+?)(?:\n(?:SAMPLE|DISTRIBUTOR|Business|$)|\Z)', block, re.DOTALL)
    if addr_match:
        address = addr_match.group(1).strip().replace('\n', ' ')
        # Clean up multiple spaces.
        address = re.sub(r'\s+', ' ', address)
        obs[f'{prefix}_address'] = address

        # Parse city, state, zipcode from address.
        state_zip = re.search(r'([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\s*$', address)
        if state_zip:
            obs[f'{prefix}_state'] = state_zip.group(1)
            obs[f'{prefix}_zipcode'] = state_zip.group(2)
            # Street is everything before "City STATE ZIP"
            before_zip = address[:state_zip.start()].rstrip(', ')
            # City is the last comma-separated part.
            parts = before_zip.rsplit(',', 1)
            if len(parts) == 2:
                obs[f'{prefix}_street'] = parts[0].strip()
                obs[f'{prefix}_city'] = parts[1].strip()
            else:
                obs[f'{prefix}_street'] = before_zip

    return obs

def _parse_sample_details(block: str) -> Dict:
    """Parse the SAMPLE DETAIL block."""
    obs = {}
    patterns = {
        'batch_number': r'Batch\s+Number:\s*(\S+)',
        'sample_id': r'Sample\s+ID:\s*(\S+)',
        'date_collected': r'Date\s+Collected:\s*(\d{1,2}/\d{1,2}/\d{4})',
        'date_received': r'Date\s+Received:\s*(\d{1,2}/\d{1,2}/\d{4})',
        'batch_size': r'Batch\s+Size:\s*(.+?)(?:\n|$)',
        'sample_size': r'Sample\s+Size:\s*(.+?)(?:\n|$)',
        'unit_mass': r'Unit\s+Mass(?:es)?:\s*(.+?)(?:\n|$)',
        'serving_size': r'Serving\s+Size:\s*(.+?)(?:\n|$)',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, block)
        if match:
            value = match.group(1).strip()
            if key in ('date_collected', 'date_received'):
                value = _parse_date(value)
            obs[key] = value
    return obs

def _parse_safety_summary(text: str) -> Dict:
    """Parse SAFETY ANALYSIS - SUMMARY for per-analysis pass/fail."""
    obs = {}
    # Find the safety summary block.
    safety_match = re.search(
        r'SAFETY\s+ANALYSIS\s*[-–—]\s*SUMMARY([\s\S]*?)(?:These\s+results|Sample\s+Certification|$)',
        text,
    )
    if not safety_match:
        return obs

    safety_text = safety_match.group(1)

    # Parse "Analysis: PASS" or "Analysis: FAIL" patterns.
    # SC Labs format: "Pesticides: PASS" or "Pesticides: ✅PASS"
    status_patterns = [
        (r'Pesticides?:?\s*(?:✅|☑)?\.?\s*(PASS|FAIL)', 'pesticides_status'),
        (r'Mycotoxins?:?\s*(?:✅|☑)?\.?\s*(PASS|FAIL)', 'mycotoxins_status'),
        (r'Residual\s+Solvents?:?\s*(?:✅|☑)?\.?\s*(PASS|FAIL)', 'residual_solvents_status'),
        (r'Heavy\s+Metals?:?\s*(?:✅|☑)?\.?\s*(PASS|FAIL)', 'heavy_metals_status'),
        (r'Microbiology:?\s*(?:✅|☑)?\.?\s*(PASS|FAIL)', 'microbials_status'),
        (r'Microbial\s+Impurities:?\s*(?:✅|☑)?\.?\s*(PASS|FAIL)', 'microbials_status'),
        (r'Foreign\s+Material:?\s*(?:✅|☑)?\.?\s*(PASS|FAIL)', 'foreign_matter_status'),
        (r'Water\s+Activity:?\s*(?:✅|☑)?\.?\s*(PASS|FAIL)', 'water_activity_status'),
        (r'[Δ∆]9?.?THC\s+per\s+Unit:?\s*(?:✅|☑)?\.?\s*(PASS|FAIL)', 'thc_per_unit_status'),
        (r'[Δ∆]9?.?THC\s+per\s+Serving:?\s*(?:✅|☑)?\.?\s*(PASS|FAIL)', 'thc_per_serving_status'),
    ]
    for pattern, key in status_patterns:
        match = re.search(pattern, safety_text, re.IGNORECASE)
        if match:
            obs[key] = match.group(1).lower()

    return obs

# ── Results Parsing Functions ──────────────────────────────────────

def _identify_analysis_from_text(page_text: str) -> List[Tuple[str, str]]:
    """Identify all analysis sections on a page from header text.

    Returns list of (raw_header, standard_analysis_name) tuples.
    """
    sections = []
    for match in SECTION_HEADER_RE.finditer(page_text):
        raw = match.group(0)
        header_key = match.group(1).strip().lower()

        # Map to standard analysis name.
        analysis = None
        for prefix, std_name in ANALYSIS_SECTION_MAP.items():
            if prefix in header_key:
                analysis = std_name
                break
        if analysis:
            sections.append((raw, analysis))

    return sections

# Words the first cell of a column header row is (SC Labs: "COMPOUND").
_HEADER_WORDS = {'COMPOUND', 'COMPOUNDS', 'ANALYTE', 'ANALYTES'}

# A results row after its analyte name, read as typed tokens: a date (a
# section title merged into the row; ignored), the "LOD / LOQ" pair, a
# measurement uncertainty ("±0.231"), a "≥ LOD" action limit, PASS/FAIL,
# a printed result (a number, "ND", "<LOQ", "N/A", ...), or another word
# (units, column labels; ignored). See _parse_table_row.
_ROW_TOKEN_RE = re.compile(
    r'(?P<date>\b\d{1,2}/\d{1,2}/\d{2,4}\b)'
    r'|(?P<pair>(?:\d+(?:\.\d+)?|\.\d+)\s*/\s*(?:\d+(?:\.\d+)?|\.\d+))'
    r'|(?P<mu>(?:±|\+/-)\s*(?:\d[\d,]*(?:\.\d+)?|\.\d+))'
    r'|(?P<geq>(?:≥|>=)\s*LO[DQ]\b)'
    r'|(?P<status>\b(?:PASS|FAIL)(?:ED)?\b)'
    r'|(?P<result>'
    r'(?:<|≤)\s*(?:LO[DQ]\b|\d[\d,]*(?:\.\d+)?|\.\d+)'
    r'|>\s*(?:ULOQ\b|\d[\d,]*(?:\.\d+)?|\.\d+)'
    r'|\b(?:Not|None)\s+Detected\b|\bNot\s+Tested\b'
    r'|\b(?:ND|N/D|NR|N/R|NT|N/T|N/A|NA|Detected|Absent|Present'
    r'|Negative|Positive)\b'
    r'|[-+]?(?:\d[\d,]*(?:\.\d+)?|\.\d+)%?'
    r')'
    r'|(?P<other>\S+)',
    re.IGNORECASE,
)

# A microbiology or foreign material row after its analyte name:
# ACTION LIMIT (text: "Not Detected in 1g", "> 1 per 3 grams", "> 25%")
# | RESULT, read from the end of the row once PASS/FAIL is removed. The
# limit is never split from its comparison sign ("> 25%" is a limit,
# not a limit ">" and a result "25%"), a row with a limit is preferred
# to one without (every SC Labs row prints one), and a lone "<x" / ">x"
# may be the limit of a blank result, so it is not taken as a result.
_PASS_FAIL_WORDS = (
    r'(?:Not|None)\s+Detected|Not\s+Tested|Detected|Absent|Present'
    r'|Negative|Positive|N/?[ADRT]'
)
_PASS_FAIL_NUMBER = r'\d[\d,]*(?:\.\d+)?\s*(?:%|CFU/g)?'
_PASS_FAIL_RESULT = (
    rf'{_PASS_FAIL_WORDS}|[<>]\s*\d[\d,]*(?:\.\d+)?|{_PASS_FAIL_NUMBER}'
)
_PASS_FAIL_LIMIT = r'(?P<limit>.+?)(?<![<>≤≥=])'
_PASS_FAIL_ROW_RES = (
    # LIMIT RESULT
    re.compile(
        rf'^{_PASS_FAIL_LIMIT}\s+(?P<result>{_PASS_FAIL_RESULT})\s*$',
        re.IGNORECASE),
    # LIMIT RESULT N/A (an "N/A" status)
    re.compile(
        rf'^{_PASS_FAIL_LIMIT}\s+(?P<result>{_PASS_FAIL_RESULT})\s+N/?A\s*$',
        re.IGNORECASE),
    # RESULT (no limit printed)
    re.compile(
        rf'^(?P<result>{_PASS_FAIL_WORDS}|{_PASS_FAIL_NUMBER})(?:\s+N/?A)?\s*$',
        re.IGNORECASE),
)

# Column labels of a header merged into a data row ("ACTION LIMIT
# > 1 per 3 grams", "RESULT 0").
_COLUMN_LABEL_RE = re.compile(r'\b(?:ACTION\s+LIMIT|RESULTS?)\b', re.IGNORECASE)

# Units named in column headers, e.g. "RESULT (µg/g)".
_HEADER_UNIT_NAMES = {
    '%': 'percent', 'mg/g': 'mg/g', 'µg/g': 'ug/g', 'μg/g': 'ug/g',
    'ug/g': 'ug/g', 'µg/kg': 'ug/kg', 'μg/kg': 'ug/kg', 'ug/kg': 'ug/kg',
    'ppm': 'ppm', 'ppb': 'ppb', 'aw': 'aw', 'mg/unit': 'mg/unit',
    'mg/serving': 'mg/serving', 'cfu/g': 'cfu/g',
}

# Units of mass fraction, as a multiple of a percent (potency columns).
_PERCENT_PER_UNIT = {'percent': Decimal(1), 'mg/g': Decimal('0.1')}

def _row_cells(row: Optional[List]) -> List[str]:
    """A table row's cells as one-line text ('' for an empty cell)."""
    return [
        re.sub(r'\s+', ' ', _clean_text(c)).strip() if c else ''
        for c in (row or [])
    ]

def _row_name(row: Optional[List]) -> str:
    """A row's analyte name: its first cell on one line, less a column
    header word ("COMPOUND") or section title that pdfplumber merged into
    the cell above the name."""
    first = _clean_text(row[0]) if row and row[0] else ''
    lines = [line.strip() for line in first.split('\n') if line.strip()]
    while len(lines) > 1 and (
            lines[0].upper() in _HEADER_WORDS
            or SECTION_HEADER_RE.search(lines[0])):
        lines.pop(0)
    return ' '.join(lines)

def _row_tokens(cells: List[str]) -> List[Tuple[str, str]]:
    """The typed tokens (kind, text) of a row's cells after the name."""
    text = ' '.join(c for c in cells if c)
    return [(m.lastgroup, m.group(0)) for m in _ROW_TOKEN_RE.finditer(text)]

def _row_has_labels(row: Optional[List]) -> bool:
    """Whether a row carries column labels: a header row, or a header
    merged into the first data row."""
    first = _clean_text(row[0]) if row and row[0] else ''
    lines = [line.strip() for line in first.split('\n') if line.strip()]
    if lines and lines[0].upper() in _HEADER_WORDS:
        return True
    joined = ' '.join(_row_cells(row)).upper()
    return 'RESULT' in joined and bool(
        re.search(r'\bLOD\b|\bLIMIT\b|UNCERTAINTY', joined))

def _row_kind(row: Optional[List]) -> str:
    """'empty', 'title' (a section title, "CANNABINOID TEST RESULTS -
    06/30/2023"), 'header' (column labels and no values) or 'data'."""
    cells = _row_cells(row)
    if not any(cells):
        return 'empty'
    if SECTION_HEADER_RE.search(_row_name(row)):
        return 'title'
    if _row_has_labels(row) and not any(
            kind in ('pair', 'mu', 'result', 'status')
            for kind, _ in _row_tokens(cells[1:])):
        return 'header'
    return 'data'

def _table_segments(
        table: Optional[List],
        header: Optional[List] = None,
    ) -> Tuple[List[Tuple[Optional[List], List]], Optional[List]]:
    """Split a pdfplumber table into runs of data rows, each with the
    column header row that heads it (or None).

    pdfplumber does not put the SC Labs column header in the table it
    heads: the header is a table of its own (it then heads the next
    table: pass the returned header to the next call), a row of this
    table, or merged into the first data row ("COMPOUND\\nTHCa"), which
    is then both header and data. A section title starts a new run.

    Returns:
        Tuple of ([(header, data_rows), ...], header for the next table).
    """
    segments = []
    rows: List = []
    for row in table or []:
        kind = _row_kind(row)
        if kind == 'empty':
            continue
        if kind in ('header', 'title'):
            if rows:
                segments.append((header, rows))
                rows = []
            header = row if kind == 'header' else None
            continue
        if not rows and header is None and _row_has_labels(row):
            header = row
        rows.append(row)
    if rows:
        segments.append((header, rows))
        header = None
    return segments, header

def _header_units(header: Optional[List]) -> Dict[str, Any]:
    """Units a column header row names: {'lodloq': units of the LOD/LOQ
    column or None, 'results': units of each RESULT column that names
    its units, in order}."""
    found: Dict[str, Any] = {'lodloq': None, 'results': []}
    for cell in _row_cells(header)[1:]:
        upper = cell.upper()
        named = re.search(r'\(([^)]+)\)', cell)
        units = _HEADER_UNIT_NAMES.get(named.group(1).strip().lower()) \
            if named else None
        if 'LOD' in upper and 'RESULT' not in upper:
            found['lodloq'] = units
        elif 'RESULT' in upper and 'LOD' not in upper and units:
            found['results'].append(units)
    return found

def _potency_header_units(header: Optional[List]) -> Dict[str, Any]:
    """_header_units for a cannabinoid or terpene table, keeping only
    potency units: a header given as a table of its own may head another
    section (pdfplumber orders the tables of a two-column page by
    position), and its units are then ignored."""
    found = _header_units(header)
    if found['lodloq'] not in _PERCENT_PER_UNIT:
        found['lodloq'] = None
    if not all(u in ('percent', 'mg/g', 'mg/unit', 'mg/serving')
               for u in found['results']):
        found['results'] = []
    return found

def _split_pair(text: str) -> Tuple[str, str]:
    """The LOD and LOQ of a printed "LOD / LOQ" pair, as printed."""
    lod, loq = text.split('/', 1)
    return lod.strip(), loq.strip()

def _in_units(text: Optional[str], units: str, target: str) -> Optional[float]:
    """A printed number in ``target`` units (mg/g and percent convert;
    1 mg/g = 0.1 %), exactly: 0.14 mg/g is 0.014 %."""
    if not text:
        return None
    try:
        number = Decimal(text.replace(',', ''))
    except InvalidOperation:
        return None
    if units != target and units in _PERCENT_PER_UNIT \
            and target in _PERCENT_PER_UNIT:
        number = number * _PERCENT_PER_UNIT[units] / _PERCENT_PER_UNIT[target]
    return float(number)

def _decimals(text: str) -> int:
    """How many decimals a printed number has."""
    match = re.search(r'\.(\d+)', text)
    return len(match.group(1)) if match else 0

def _tenfold(mg_text: str, pct_text: str) -> bool:
    """Whether two printed results are the same amount in mg/g and in
    percent (the mg/g one 10 times larger), to their printed rounding."""
    mg = parse_result_value(mg_text)[0]
    pct = parse_result_value(pct_text)[0]
    if mg is None or pct is None:
        return False
    slack = 0.5 * 10 ** -_decimals(mg_text) + 5 * 10 ** -_decimals(pct_text)
    return abs(mg - 10 * pct) <= max(slack, 0.01 * abs(mg)) + 1e-9

def _percent_column(results: List[str], name: str = '') -> int:
    """Which of a potency row's printed results is RESULT (%).

    SC Labs prints RESULT (mg/g) then RESULT (%); two numbers 10 times
    apart (mg/g to the left) confirm the order or correct it. Results
    that are not numbers (ND, <LOQ) read alike in both columns.
    """
    last = len(results) - 1
    for i in range(last, 0, -1):
        if _tenfold(results[i - 1], results[i]):
            return i
    for i in range(last, 0, -1):
        if _tenfold(results[i], results[i - 1]):
            return i - 1
    if parse_result_value(results[-2])[0] is not None \
            and parse_result_value(results[-1])[0] is not None:
        _log.warning(
            'SC Labs %s: %s (mg/g) is not 10 x %s (%%); '
            'reading the last column as percent.',
            name, results[-2], results[-1],
        )
    return last

def _read_potency_row(
        tokens: List[Tuple[str, str]],
        columns: Dict[str, Any],
        name: str = '',
    ) -> Dict[str, Any]:
    """Cannabinoids and terpenes, printed as
    LOD/LOQ (mg/g) | MEASUREMENT UNCERTAINTY (mg/g) | RESULT (mg/g) | RESULT (%).

    The result is read from the percent column (units 'percent'); a
    non-detect prints "N/A" for its uncertainty, which is skipped. LOD
    and LOQ are given in the result's units. A header row, when there is
    one, names the units of the columns.
    """
    lod = loq = None
    results: List[str] = []
    for kind, text in tokens:
        if kind == 'pair':
            if lod is None and not results:
                lod, loq = _split_pair(text)
        elif kind == 'result':
            results.append(text)
    while len(results) > 2 and parse_result_value(results[0])[1] == 'NR':
        results.pop(0)
    named = columns.get('results') or []
    text, units = None, 'percent'
    if results and len(named) == len(results):
        i = named.index('percent') if 'percent' in named else 0
        text, units = results[i], named[i]
    elif len(results) == 1:
        text = results[0]
        units = named[0] if len(named) == 1 else 'percent'
    elif results:
        text = results[_percent_column(results, name)]
    lod_units = columns.get('lodloq') or 'mg/g'
    return {
        'text': text,
        'units': units,
        'lod': _in_units(lod, lod_units, units),
        'loq': _in_units(loq, lod_units, units),
        'limit': None,
        'status': '',
    }

def _read_limit_row(tokens: List[Tuple[str, str]]) -> Dict[str, Any]:
    """Pesticides, residual solvents, heavy metals, mycotoxins, water
    activity and moisture, printed as
    LOD/LOQ | ACTION LIMIT | MEASUREMENT UNCERTAINTY | RESULT | PASS/FAIL.

    The result is the value after the uncertainty ("±50.4"); else the
    printed qualifier ("ND", "<LOQ"); else the last value before
    PASS/FAIL. The action limit is the first number before the result
    ("≥ LOD" is a detection limit, not a number). A number is never
    taken from the LOD/LOQ or action limit columns: a lone number with
    no uncertainty before it, in a row whose limit is not "≥ LOD", may
    be the action limit, and the result is left unread.
    """
    status = ''
    end = len(tokens)
    for i in range(len(tokens) - 1, -1, -1):
        if tokens[i][0] == 'status':
            status = 'pass' if tokens[i][1].upper().startswith('PASS') \
                else 'fail'
            end = i
            break
    body = tokens[:end]
    lod = loq = None
    for i, (kind, text) in enumerate(body):
        if kind == 'pair':
            lod, loq = _split_pair(text)
            body = body[i + 1:]
            break
    detection_limit = any(kind == 'geq' for kind, _ in body)
    uncertainty = None
    for i, (kind, _) in enumerate(body):
        if kind == 'mu':
            uncertainty = i
    values = [(i, text) for i, (kind, text) in enumerate(body)
              if kind == 'result']
    chosen = None
    if uncertainty is not None:
        chosen = next((v for v in values if v[0] > uncertainty), None)
    if chosen is None:
        qualified = [v for v in values
                     if parse_result_value(v[1])[1] not in ('', 'NR')]
        if qualified:
            chosen = qualified[-1]
    if chosen is None and values:
        if len(values) > 1 or detection_limit:
            chosen = values[-1]
        elif parse_result_value(values[0][1])[0] is None:
            chosen = values[0]
    limit = None
    if not detection_limit:
        cutoff = chosen[0] if chosen is not None else len(body)
        if uncertainty is not None:
            cutoff = min(cutoff, uncertainty)
        numbers = [parse_result_value(t)[0] for i, t in values if i < cutoff]
        numbers = [n for n in numbers if n is not None]
        if numbers:
            limit = numbers[0]
    return {
        'text': chosen[1] if chosen is not None else None,
        'units': None,
        'lod': _in_units(lod, '', ''),
        'loq': _in_units(loq, '', ''),
        'limit': limit,
        'status': status,
    }

def _read_pass_fail_row(text: str) -> Dict[str, Any]:
    """Microbiology and foreign material, printed as
    ACTION LIMIT | RESULT | PASS/FAIL, where the action limit is text
    ("Not Detected in 1g", "> 1 per 3 grams"): the row is read from its
    end (_PASS_FAIL_ROW_RES). A printed "0" is 0.0; a blank result is
    left unread, and the action limit is never read as the result."""
    text = _COLUMN_LABEL_RE.sub(' ', text or '')
    text = re.sub(r'\s+', ' ', text).strip()
    status = ''
    match = re.search(r'\s*\b(PASS|FAIL)(?:ED)?\s*$', text, re.IGNORECASE)
    if match:
        status = match.group(1).lower()
        text = text[:match.start()].strip()
    result = None
    for pattern in _PASS_FAIL_ROW_RES if text else ():
        match = pattern.match(text)
        if match:
            result = match.group('result').strip()
            break
    return {
        'text': result,
        'units': 'percent' if result and result.endswith('%') else None,
        'lod': None,
        'loq': None,
        'limit': None,
        'status': status,
    }

def _parse_results_from_tables(pdf) -> Tuple[List[Dict], List[str]]:
    """Extract all analyte results from PDF tables across all pages.

    SC Labs COAs have well-structured tables that pdfplumber can
    extract reliably. Each results page has one or two tables (for
    the two-column layout). The column header is not always a row of
    the table it heads (see _table_segments), so every row is read
    unless it is a header or a section title.

    Returns:
        Tuple of (results_list, analyses_list).
    """
    all_results = []
    analyses_seen = set()

    for page_idx, page in enumerate(pdf.pages):
        try:
            page_text = _clean_text(page.extract_text() or '')
        except Exception:
            continue

        # Skip page 1 (summary page) — but only if we detect it.
        if page_idx == 0 and 'SAMPLE DETAILS' in page_text:
            continue

        # Identify which analysis sections are on this page.
        page_sections = _identify_analysis_from_text(page_text)
        if not page_sections:
            continue
        current_analysis = page_sections[0][1]

        # Extract tables from the page.
        try:
            tables = page.extract_tables()
        except Exception:
            continue

        pending_header = None
        for table in tables or []:
            segments, pending_header = _table_segments(table, pending_header)
            for header, rows in segments:

                # Classify by content; a one-row table (water activity,
                # moisture) must name a known analyte.
                if len(rows) == 1:
                    table_analysis = _classify_table(
                        [header] + rows, page_sections, fallback=False,
                    )
                else:
                    table_analysis = _classify_table(
                        [header] + rows, page_sections,
                    ) or current_analysis
                if not table_analysis:
                    continue

                analyses_seen.add(table_analysis)
                units = STANDARD_UNITS.get(table_analysis, '')

                for row in rows:
                    name = _row_name(row)

                    # Skip non-analyte rows.
                    if not name or len(name) < 2 or _is_skip_row(name):
                        continue

                    # Get the analyte key.
                    key = _snake_case(name)

                    # Skip keys starting with a digit (per-unit rows).
                    if key and key[0].isdigit():
                        continue

                    result = _parse_table_row(
                        row, header, name, key, table_analysis, units,
                    )
                    if result:
                        all_results.append(result)

    analyses = sorted(analyses_seen)
    return all_results, analyses

def _classify_table(
        table: List,
        page_sections: List[Tuple],
        fallback: bool = True,
    ) -> Optional[str]:
    """Classify a table's analysis type by examining its content.

    Uses the content-based classification approach (primary method)
    established in the TagLeaf algorithm. Falls back to page section
    headers if content matching fails (unless ``fallback`` is False).

    ``table[0]`` is the table's header row (or None) and is not read.
    """
    if not table or len(table) < 2:
        return None

    # Extract analyte names from the first 10 data rows.
    sample_names = []
    for row in table[1:11]:
        name = _row_name(row)
        if name and name.upper() not in _HEADER_WORDS:
            sample_names.append(name.lower())

    if not sample_names:
        return None

    # Known analyte sets for content-based classification.
    cannabinoid_markers = {
        'thca', 'δ9-thc', '∆9-thc', 'Δ9-thc', 'cbd', 'cbda', 'cbg',
        'cbga', 'cbn', 'cbc', 'cbca', 'cbdv', 'cbdva', 'thcv', 'thcva',
        'δ8-thc', '∆8-thc', 'cbl',
    }
    terpene_markers = {
        'myrcene', 'limonene', 'linalool', 'β-caryophyllene',
        'β caryophyllene', 'α-humulene', 'α humulene', 'α-pinene',
        'β-pinene', 'terpinolene', 'fenchol', 'terpineol', 'borneol',
        'camphene', 'α-bisabolol', 'ocimene', 'β-ocimene',
        'trans-β-farnesene', 'geraniol', 'fenchone', 'nerolidol',
    }
    pesticide_markers = {
        'abamectin', 'acephate', 'aldicarb', 'bifenazate', 'carbofuran',
        'chlorpyrifos', 'diazinon', 'imidacloprid', 'malathion',
        'permethrin', 'spinosad', 'myclobutanil', 'pyrethrins',
        'bifenthrin', 'fipronil', 'spiromesifen',
    }
    mycotoxin_markers = {
        'aflatoxin b1', 'aflatoxin b2', 'aflatoxin g1', 'aflatoxin g2',
        'total aflatoxin', 'ochratoxin a',
    }
    solvent_markers = {
        'acetone', 'methanol', 'ethanol', 'n-butane', 'butane',
        'n-hexane', 'hexane', 'toluene', 'propane', 'benzene',
        'chloroform', '1,2-dichloroethane', 'isopropyl', '2-propanol',
        'ethyl acetate', 'total xylenes', 'n-pentane',
    }
    metal_markers = {'arsenic', 'cadmium', 'lead', 'mercury'}
    microbe_markers = {
        'aspergillus flavus', 'aspergillus fumigatus',
        'aspergillus niger', 'aspergillus terreus',
        'salmonella spp.', 'salmonella', 'shiga toxin', 'e. coli',
    }
    foreign_markers = {
        'hair count', 'insect fragment', 'mammalian excreta',
        'total sample area', 'imbedded foreign',
    }
    water_markers = {'water activity'}
    moisture_markers = {'moisture'}

    # Score each analysis type.
    scores = {
        'cannabinoids': 0, 'terpenes': 0, 'pesticides': 0,
        'mycotoxins': 0, 'residual_solvents': 0, 'heavy_metals': 0,
        'microbials': 0, 'foreign_matter': 0, 'water_activity': 0,
        'moisture': 0,
    }
    markers = {
        'cannabinoids': cannabinoid_markers,
        'terpenes': terpene_markers,
        'pesticides': pesticide_markers,
        'mycotoxins': mycotoxin_markers,
        'residual_solvents': solvent_markers,
        'heavy_metals': metal_markers,
        'microbials': microbe_markers,
        'foreign_matter': foreign_markers,
        'water_activity': water_markers,
        'moisture': moisture_markers,
    }
    for name in sample_names:
        name_lower = name.lower()
        for analysis, analysis_markers in markers.items():
            if any(marker in name_lower for marker in analysis_markers):
                scores[analysis] += 1

    # Return the highest-scoring analysis type (minimum 1 match).
    best = max(scores, key=scores.get)
    if scores[best] >= 1:
        return best

    # Fallback to page section headers.
    if fallback and page_sections:
        return page_sections[0][1]

    return None

def _parse_table_row(
        row: List,
        header: List,
        name: str,
        key: str,
        analysis: str,
        units: str,
    ) -> Optional[Dict]:
    """Parse a single table row into a result dict.

    SC Labs tables have varying column structures by analysis type:

    Cannabinoids/Terpenes:
        COMPOUND | LOD/LOQ (mg/g) | MEASUREMENT UNCERTAINTY | RESULT (mg/g) | RESULT (%)

    Pesticides:
        COMPOUND | LOD/LOQ (µg/g) | ACTION LIMIT (µg/g) | MEASUREMENT UNCERTAINTY | RESULT (µg/g) | RESULT

    Mycotoxins:
        COMPOUND | LOD/LOQ (µg/kg) | ACTION LIMIT (µg/kg) | MEASUREMENT UNCERTAINTY | RESULT (µg/kg) | RESULT

    Heavy Metals:
        COMPOUND | LOD/LOQ (µg/g) | ACTION LIMIT (µg/g) | MEASUREMENT UNCERTAINTY | RESULT (µg/g) | RESULT

    Microbiology:
        COMPOUND | ACTION LIMIT | RESULT | RESULT

    Foreign Material:
        COMPOUND | ACTION LIMIT | RESULT | RESULT

    Water Activity:
        COMPOUND | LOD/LOQ (Aw) | ACTION LIMIT (Aw) | MEASUREMENT UNCERTAINTY (Aw) | RESULT (Aw) | RESULT

    pdfplumber can merge these columns into fewer cells, and a blank
    cell then leaves no trace (['THCVa', '0.07 / 0.20', '±0.231 4.61
    0.461']), so a row is read by token, in column order, from the text
    of its cells after the name: _read_potency_row,
    _read_limit_row and _read_pass_fail_row. The printed result is
    read with the package's qualifier semantics (parse_result_value):
    "ND" is value None with qualifier 'ND', "<LOQ" is value None with
    qualifier '<LOQ', "<x" gives 'loq' x when the row prints none. A
    result that cannot be read is value None (never 0.0).

    Units: cannabinoids and terpenes are read from RESULT (%) ('percent',
    LOD/LOQ converted from mg/g); other analyses keep the units their
    columns are documented in (``units``, from STANDARD_UNITS).
    """
    cells = _row_cells(row)[1:]
    if analysis in ('microbials', 'foreign_matter'):
        read = _read_pass_fail_row(' '.join(c for c in cells if c))
    elif analysis in ('cannabinoids', 'terpenes'):
        read = _read_potency_row(
            _row_tokens(cells), _potency_header_units(header), name,
        )
    else:
        read = _read_limit_row(_row_tokens(cells))

    value, qualifier, bound = parse_result_value(read['text'])
    lod, loq = read['lod'], read['loq']
    if bound is not None and qualifier == '<LOQ' and loq is None:
        loq = bound
    elif bound is not None and qualifier == '<LOD' and lod is None:
        lod = bound

    return {
        'analysis': analysis,
        'key': key,
        'name': name,
        'value': value,
        'qualifier': qualifier,
        'units': read['units'] or units,
        'lod': lod,
        'loq': loq,
        'limit': read['limit'],
        'status': read['status'],
    }

# ── Main Parsing Function ──────────────────────────────────────────

def parse_sc_labs_pdf(
        parser: Any = None,
        doc: str = '',
        **kwargs,
    ) -> Dict:
    """Parse an SC Labs COA PDF.

    This is the core parsing function. Opens the PDF with pdfplumber,
    extracts metadata from page 1 via text extraction, then extracts
    all analyte results from tables on pages 2+.

    Args:
        parser: Optional CoADoc instance (backwards compatibility; ignored).
        doc:    Path to the COA PDF file.

    Returns:
        Dict with all extracted COA data, including:
            - Metadata fields (product_name, producer, dates, etc.)
            - results: JSON string of list[dict] (analyte results)
            - analyses: JSON string of list[str] (analysis types)
    """
    # Accept file path as either argument.
    pdf_path = doc if isinstance(doc, str) and doc else ''
    if isinstance(parser, str) and not pdf_path:
        pdf_path = parser
        parser = None

    if not pdf_path:
        raise ValueError('No PDF file path provided.')

    obs = {}

    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            raise ValueError(f'PDF has no pages: {pdf_path}')

        # ── Phase 1: Extract metadata from page 1 ────────────
        try:
            front_text = _clean_text(pdf.pages[0].extract_text() or '')
        except Exception as e:
            raise ValueError(f'Failed to extract text from page 1: {e}')

        obs = _parse_front_page_metadata(front_text, page=pdf.pages[0])

        # ── Phase 2: Extract results from tables (pages 2+) ──
        results, analyses = _parse_results_from_tables(pdf)

        # ── Phase 3: Derive analyses from safety summary if needed ──
        # Add analyses detected from safety summary statuses.
        status_analyses = set()
        for key in list(obs.keys()):
            if key.endswith('_status'):
                analysis_name = key.replace('_status', '')
                if analysis_name in STANDARD_UNITS:
                    status_analyses.add(analysis_name)
        for a in status_analyses:
            if a not in analyses:
                analyses.append(a)
        analyses = sorted(set(analyses))

        # ── Phase 4: Compute totals from results if missing ──
        # (total_terpenes is a percent: only percent results are summed.)
        if results and not obs.get('total_terpenes'):
            terp_sum = sum(
                r['value'] for r in results
                if r['analysis'] == 'terpenes'
                and r['key'] not in ('total_terpenes',)
                and r.get('units') == 'percent'
                and r['value'] is not None
                and r['value'] > 0
            )
            if terp_sum > 0:
                obs['total_terpenes'] = round(terp_sum, 4)

        # ── Phase 5: Build final output ──────────────────────
        obs = {**SC_LABS, **obs}
        obs['analyses'] = json.dumps(analyses)
        obs['results'] = json.dumps(results)
        obs['coa_parsed_at'] = datetime.now().isoformat()

        # Generate results hash.
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

        # Store lab's sample ID as lab_id.
        obs['lab_id'] = obs.get('sample_id', '')

        # PDF filename for reference.
        obs['coa_pdf'] = pdf_path.replace('\\', '/').split('/')[-1]

    return obs

# ── Entry Point (LAB_REGISTRY compatible) ──────────────────────────

def parse_sc_labs_coa(
        parser: Any = None,
        doc: str = '',
        **kwargs,
    ) -> Dict:
    """Parse an SC Labs COA PDF.

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

    return parse_sc_labs_pdf(parser, doc, **kwargs)

def is_sc_labs(pdf_path: str) -> bool:
    """Quick check if a PDF is an SC Labs COA (without full parse).

    Args:
        pdf_path: Path to a PDF file.

    Returns:
        True if the PDF appears to be from SC Labs.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return False
            text = (pdf.pages[0].extract_text() or '').lower()
            return (
                'sclabs.com' in text
                or 'sc laboratories' in text
                or 'sc labs' in text
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
            print('Usage: python sclabs.py <pdf_file> [pdf_file2 ...]')
            sys.exit(1)

    success = 0
    fail = 0
    for pdf_file in test_files:
        pdf_path = os.path.join(test_dir, pdf_file) \
            if not os.path.isabs(pdf_file) else pdf_file
        if not os.path.exists(pdf_path):
            print(f'Not found: {pdf_path}')
            continue
        try:
            data = parse_sc_labs_coa(None, pdf_path)
            results = json.loads(data.get('results', '[]'))
            analyses = json.loads(data.get('analyses', '[]'))
            print(f'\n{"="*60}')
            print(f'OK {pdf_file}')
            print(f'  Product:  {data.get("product_name", "?")}')
            print(f'  Type:     {data.get("product_type", "?")}')
            print(f'  Producer: {data.get("producer", "?")}')
            print(f'  Date:     {data.get("date_tested", "?")}')
            print(f'  THC:      {data.get("total_thc", "?")}%')
            print(f'  CBD:      {data.get("total_cbd", "?")}%')
            print(f'  Terpenes: {data.get("total_terpenes", "?")}%')
            print(f'  Status:   {data.get("status", "?")}')
            print(f'  Analyses: {analyses}')
            print(f'  Results:  {len(results)} analytes')
            print(f'  CoA ID:   {data.get("coa_id", "?")}')
            print(f'  Sample:   {data.get("sample_id", "?")}')
            print(f'  Batch:    {data.get("batch_number", "?")}')
            success += 1
        except Exception as e:
            print(f'\nFAIL {pdf_file}: {e}')
            import traceback
            traceback.print_exc()
            fail += 1

    print(f'\n{"="*60}')
    print(f'Results: {success} OK, {fail} FAIL out of {success + fail}')
