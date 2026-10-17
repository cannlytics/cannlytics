"""
Parse Confident Cannabis / Confident LIMS COA — Offline-First Hybrid Engine
Copyright (c) 2022-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2022
Updated: 10/13/2026
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

    Table layout (one analyte per line; see "Results Parsing" below):
        Cannabinoids:   "Analyte LOQ Mass Mass" / "% % mg/g"
                        "Δ9-THC 0.1 90.0348 900.348"
        No LOQ column:  "Analyte Mass Mass" / "% mg/g"
                        "Δ9-THC 83.9504 839.504"
        Edibles:        "Analyte LOQ Mass Mass" / "mg/unit mg/unit mg/g"
        Heavy metals:   "Analyte LOQ Limit Mass Status" / "PPB PPB PPB"
                        "Arsenic 200 400 <LOQ Pass"
        Microbials:     "Analyte Limit Mass Status" / "CFU/g CFU/g"
                        "E. Coli 100 <LOQ Pass"
        Two tables side by side (pesticides, terpenes) share each line:
                        "Abamectin 0.25 0.5 ND Pass Hexythiazox 0.5 1 ND Pass"

    Fixes (10/13/2026), from a benchmark of 4 Arizona COAs read by four
    Claude models that agree with each other:
        * Units now name the column the value was read from. A header
          printing both % and mg/g was labelled 'mg/g' (mg/g was looked
          for first) while the value was read from the % column:
          Δ9-THC 90.0348 'mg/g' where the COA prints 90.0348 %; every
          cannabinoid and terpene of the COA was 10x off by its label.
          Each table's header and units rows are now read column by
          column (_parse_columns_line, _parse_units_line), percent is
          reported when the table prints it, edibles keep 'mg/unit', and
          ppb stays 'ppb' (it was labelled 'ug/g', 1000x off). Units no
          longer carry over from the previous table on the page.
        * A result is never an LOD, LOQ or action limit. Arizona heavy-
          metal rows whose result cell prints off the row's line
          ("Arsenic 200 400 Pass", "<LOQ" on a line of its own) read the
          limit as the result (arsenic, cadmium, lead, mercury 400, 400,
          1000 and 1200 'ug/g' where the COA prints <LOQ or ND); such a
          row now has no result unless the lone result cell beside it is
          found (_attach_orphan_results). Microbial rows took the first
          number, the limit ("E. Coli 100 <LOQ Pass" read as 100 cfu/g);
          rows without a percent column read their LOQ from the percent
          cell ("Δ9-THC 83.9504 839.504": LOQ 83.9504). A row is read
          against its header (_read_record): a non-detect or a bound can
          only be a result, numbers fill the LOD/LOQ/limit columns, and a
          pass/fail row printing only those numbers has no result.
        * Non-detects keep their qualifier (schema.parse_result_value):
          "ND", "Not Detected", "Absence" are value None, qualifier 'ND';
          "<LOQ" and "<10" are value None, qualifier '<LOQ' (they were
          the number 0.0), with 'loq' 10 when the row prints no LOQ;
          ">x" is '>ULOQ'. A measured 0 stays 0.0. Every result carries
          'qualifier', 'lod', 'loq', 'limit' and 'status' (None when not
          printed). Totals printed as "<LOQ" are None, and a total printed
          in mg/unit is not reported as a percent.
        * Two tables printed side by side are split into their two rows
          (the right-hand pesticides and terpenes were dropped, and a
          left-hand row without a status could take the right-hand
          row's cells). "MGK-264" rows are no longer skipped as a header,
          nor "Pinene" as an aroma line, and "Page 2 of 6" is not an
          analyte. A table without a header row is labelled with its
          analysis's units (pesticides were 'percent').
        * Keys are canonical (cannlytics.constants.analytes): 'B1' is
          'aflatoxin_b1', 'α-Thujone' 'alpha_thujone', '3-Carene'
          'delta_3_carene', and method notes are dropped from microbial
          names ('E. Coli by traditional plating: SOP-13' is 'e_coli').
        * Review (10/14/2026): a row past the end of the shorter of two
          tables side by side is read with its own analyte's table (its
          analysis and units), and a limit printed in words before a
          result word ("Absence in 1g Presence Fail") is not the result.

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
from typing import Any, Dict, List, Optional, Set, Tuple

# External imports:
import pdfplumber

# Internal imports:
from cannlytics.constants.analytes import analysis_for_analyte, normalize_analyte_key
from cannlytics.data.coas.schema import (
    MICROBIAL_KEYS,
    RESIDUAL_SOLVENT_KEYS,
    parse_result_value,
)

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
    '3-Carene': 'delta_3_carene',
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

# Ligature characters, and analyte names whose 'fl' ligature some PDFs
# drop ('Cyuthrin') or encode as a NUL byte, which _deligature restores
# as 'fi' ('Cyfiuthrin').
_LIGATURES = {'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl',
              'ﬃ': 'ffi', 'ﬄ': 'ffl'}
_LIGATURE_NAMES = {
    'cyuthrin': 'Cyfluthrin', 'cyfiuthrin': 'Cyfluthrin',
    'trioxystrobin': 'Trifloxystrobin', 'trifioxystrobin': 'Trifloxystrobin',
}

def _snake_case(text: str) -> str:
    """Convert an analyte display name to its canonical snake_case key.

    The module's own map comes first (it knows CC spellings such as
    'Spinosyn (A + D)' and 'PBO'); every key is then made canonical with
    ``normalize_analyte_key`` ('B1' is 'aflatoxin_b1', 'α-Thujone'
    'alpha_thujone', 'Yeast & Mold' 'total_yeast_and_mold'). A method
    note after a microbial name is dropped: 'E. Coli by traditional
    plating: SOP-13' is 'e_coli'.
    """
    text = ''.join(_LIGATURES.get(c, c) for c in text).strip()
    text = re.sub(r'\s+by\s+\S.*$', '', text, flags=re.DOTALL) or text
    text = _LIGATURE_NAMES.get(text.lower(), text)
    # Check exact match first, then a case-insensitive match.
    mapped = ANALYTE_KEY_MAP.get(text)
    if mapped is None:
        for k, v in ANALYTE_KEY_MAP.items():
            if k.lower() == text.lower():
                mapped = v
                break
    key = normalize_analyte_key(mapped if mapped else text)
    if key:
        return key
    # General conversion.
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = s.strip('_')
    return s

def _parse_number(text: str) -> Optional[float]:
    """Parse a plain number: an LOD, LOQ, action limit or total.

    Returns None for a non-detect ('ND', 'Not Detected', 'Absence') and
    for a bound ('<LOQ', '<0.10', '>100'): a bound is a qualifier, not a
    number (until 10/13/2026 anything with '<' or 'LOQ' returned 0.0, a
    measured zero). Read results with _parse_result.
    """
    if not text or not isinstance(text, str):
        return None
    text = text.strip().upper()
    if text in ('ND', 'N/A', '', '-', 'NT', 'NR', 'NOT DETECTED',
                'NOT TESTED', 'NOT REPORTED', 'ABSENCE',
                'NOT DETECTED IN 1G'):
        return None
    if '<' in text or '>' in text or 'LOQ' in text or 'LOD' in text:
        return None
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

# Printed results that the schema's qualifier words do not spell.
_RESULT_SPELLINGS = {
    'ABSENCE': 'ND', 'NOT DETECTED IN 1G': 'ND', 'N/D': 'ND',
    'PRESENCE': 'detected', 'NOT REQUIRED': 'NR', 'NOT ANALYZED': 'NT',
    '—': 'NR', '–': 'NR',
}

def _parse_result(text: Optional[str]) -> Tuple[Optional[float], str, Optional[float]]:
    """Read a printed result as ``(value, qualifier, bound)``.

    Uses the package's qualifier semantics (``parse_result_value``):
    '90.0348' is (90.0348, '', None); 'ND', 'Not Detected' and 'Absence'
    are (None, 'ND', None); '<LOQ' is (None, '<LOQ', None) and '<10' is
    (None, '<LOQ', 10.0), the bound being the limit the result is below;
    '>100' is (None, '>ULOQ', 100.0); '0' is (0.0, '', None). A flag
    after a number ('0.1575 Q3') and a units suffix are dropped.
    """
    if text is None:
        return None, '', None
    t = str(text).replace('_', ' ').strip().strip('*†‡').strip()
    if not t:
        return None, '', None
    special = _RESULT_SPELLINGS.get(' '.join(t.upper().split()))
    if special:
        return None, special, None
    t = re.sub(r'\s+\(?[A-Z]\d{1,2}\)?$', '', t)
    t = re.sub(
        r'\s*(mg/g|mg/unit|mg/serving|mg/container|%|µg/g|μg/g|µg/kg|'
        r'μg/kg|ug/g|ug/kg|ppm|ppb|cfu/g|rfu/g|aw)$',
        '', t, flags=re.IGNORECASE,
    ).strip()
    return parse_result_value(t)

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
    """Detect measurement units from column headers or analysis type.

    Returns the first units printed, reading left to right, as printed
    ('PPB' is 'ppb'). Until 10/13/2026 the units were looked up in a
    fixed order, so "% % mg/g" was 'mg/g' although the first result
    column is percent. A header names one unit per column: rows are
    read column by column with _parse_columns_line and
    _parse_units_line, which this helper no longer stands in for.
    """
    for token in re.split(r'[\s,]+', header_text):
        label = _unit_label(token)
        if label:
            return label
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
            # Drop qualifier flags ("83.9504% (Q3) ND"), whose digit
            # would otherwise read as a value and shift the row.
            values_line = re.sub(r'\(?\b[A-Z]\d{1,2}\b\)?', ' ', values_line)

            # Extract value tokens from the values line.
            # Match: numbers or bounds with optional %, or mg/unit (etc.),
            # ND, <LOQ, NT, NR. Each token keeps its place in the row.
            value_tokens = re.findall(
                r'([<>]?\s*[\d.]*\d[\d.]*\s*(?:%|mg/(?:serving|unit|container|g))?'
                r'|ND|<LOQ|NT|NR|Not\s*Tested)',
                values_line,
            )

            # Match values to labels by position. Totals are percent
            # (schema): a total printed in mg/unit or mg/g is not one,
            # and a total printed as a bound or non-detect is None.
            for vi, (_, field) in enumerate(label_order):
                if vi < len(value_tokens):
                    tok = value_tokens[vi].strip()
                    if 'mg/' in tok:
                        val = None
                    else:
                        val = _parse_result(tok.rstrip('%').strip())[0]
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

    # Moisture content: a summary box prints the value alone on the line
    # above the label ("10.5%" / "Moisture"), or "10.5% Moisture". The
    # last number of an unrelated line above (a cannabinoid row's mg/g
    # when moisture is "Not Tested") is not the moisture content.
    moist_match = re.search(
        r'(?m)(?:^\s*([\d.]+)\s*%?\s*\n\s*|([\d.]+)\s*%\s*)Moisture(?:\s*Content)?',
        text,
    )
    if moist_match:
        obs['moisture_content'] = _parse_number(
            moist_match.group(1) or moist_match.group(2))

    # Water activity, likewise ("0.55 aw" / "Water Activity").
    wa_match = re.search(
        r'(?m)(?:^\s*([\d.]+)\s*(?:aw)?\s*\n\s*|([\d.]+)\s*aw\s*)Water\s*Activity',
        text,
    )
    if wa_match:
        obs['water_activity'] = _parse_number(
            wa_match.group(1) or wa_match.group(2))

    return obs, list(set(analyses))

# ── Results Parsing ───────────────────────────────────────────────
#
# A results table is a section title, a column header row, a units row
# and one row per analyte. pdfplumber prints each row as one line of
# cells separated by single spaces (Arizona, 2021-2024):
#
#     Cannabinoids                                     Complete
#     Analyte       LOQ      Mass       Mass
#                   %        %          mg/g
#     Δ9-THC        0.1      90.0348    900.348
#     THCa          0.1      ND         ND
#
#     Heavy Metals                                     Pass
#     Analyte       LOQ      Limit      Mass      Status
#                   PPB      PPB        PPB
#     Arsenic       200      400        <LOQ      Pass
#
#     Microbials                                       Pass
#     Analyte       Limit    Mass       Status
#                   CFU/g    CFU/g
#     E. Coli       100      <LOQ       Pass
#
# Some tables print no LOQ column ("Δ9-THC 83.9504 839.504": percent and
# mg/g only); edibles print mg/unit ("mg/unit mg/unit mg/g"). Long
# panels (pesticides, terpenes) print two tables side by side, and
# pdfplumber merges each pair of rows into one line:
#
#     Abamectin 0.25 0.5 ND Pass Hexythiazox 0.5 1 ND Pass
#
# Each line is split into tokens (_row_tokens), the tokens into one
# record per table (_split_records), and each record is read against its
# table's columns (_read_record): a cell is what its column says, a
# non-detect or a bound ('ND', '<LOQ', '<10') can only be a result, and
# a result is never an LOD, LOQ or action limit. Arizona heavy-metal
# rows can print their result cell on a line of its own ("<LOQ" above
# "Arsenic 200 400 Pass"); such a row's result is read from that lone
# cell when the cell can be placed (_attach_orphan_results), and is
# otherwise left empty.

_POTENCY_ANALYSES = ('cannabinoids', 'terpenes')

# Column roles that hold a number or a result (a header's 'status',
# 'units', 'qualifier' and 'cas' columns hold neither).
_VALUE_ROLES = ('lod', 'loq', 'limit', 'result')

# Words of a column header row ("Analyte LOQ Limit Mass Status"). Each
# 'Analyte' begins a table; two mean two tables printed side by side.
_GROUP_WORDS = {'analyte', 'analytes', 'compound', 'compounds'}
_COLUMN_WORDS = {
    'lod': 'lod', 'mdl': 'lod',
    'loq': 'loq', 'lloq': 'loq', 'pql': 'loq',
    'limit': 'limit', 'limits': 'limit', 'action': 'limit',
    'mass': 'result', 'result': 'result', 'results': 'result',
    'amount': 'result', 'conc': 'result', 'conc.': 'result',
    'concentration': 'result',
    'status': 'status', 'pass/fail': 'status', 'p/f': 'status',
    'units': 'units', 'unit': 'units',
    'qualifier': 'qualifier', 'qualifiers': 'qualifier',
    'cas': 'cas', 'cas#': 'cas',
}
_COLUMN_PHRASES = {
    ('action', 'level'): 'limit', ('action', 'levels'): 'limit',
    ('action', 'limit'): 'limit', ('action', 'limits'): 'limit',
    ('reporting', 'limit'): 'loq',
}

# Printed units, as a result read from that column is labelled. Units
# stay as printed ('PPB' is 'ppb', never relabelled 'ug/g').
_UNIT_LABELS = {
    '%': 'percent', 'percent': 'percent',
    'mg/g': 'mg/g', 'mg/unit': 'mg/unit', 'mg/serving': 'mg/serving',
    'mg/container': 'mg/container', 'mg/package': 'mg/package',
    'mg/ml': 'mg/ml', 'mg/kg': 'mg/kg',
    'ppm': 'ppm', 'ppb': 'ppb',
    'µg/g': 'ug/g', 'μg/g': 'ug/g', 'ug/g': 'ug/g',
    'µg/kg': 'ug/kg', 'μg/kg': 'ug/kg', 'ug/kg': 'ug/kg',
    'ng/g': 'ng/g', 'cfu/g': 'cfu/g', 'cfu': 'cfu/g', 'rfu/g': 'rfu/g',
    'mpn/g': 'mpn/g', 'aw': 'aw',
}

# Mass fractions on one scale (ppm), to state an LOD, LOQ or limit in
# the units of the result read beside it.
_PPM_PER_UNIT = {
    'percent': 1e4, 'mg/g': 1e3, 'ppm': 1.0, 'ug/g': 1.0, 'mg/kg': 1.0,
    'ppb': 1e-3, 'ug/kg': 1e-3, 'ng/g': 1e-3,
}

# Results printed in words, joined into one token before a line is split
# ('Not Detected' -> 'Not_Detected').
_JOINED_RESULTS = (
    (re.compile(r'\bNot\s+Detected\b', re.IGNORECASE), 'Not_Detected'),
    (re.compile(r'\bNone\s+Detected\b', re.IGNORECASE), 'None_Detected'),
    (re.compile(r'\bNot\s+Present\b', re.IGNORECASE), 'Not_Present'),
    (re.compile(r'\bNot\s+Tested\b', re.IGNORECASE), 'Not_Tested'),
    (re.compile(r'\bNot\s+Reported\b', re.IGNORECASE), 'Not_Reported'),
    (re.compile(r'\bNot\s+Required\b', re.IGNORECASE), 'Not_Required'),
    (re.compile(r'\bNot\s+Analyzed\b', re.IGNORECASE), 'Not_Analyzed'),
)
# An amount after a presence/absence result ("Not Detected in 1g",
# "Absence in one gram"), dropped so that it does not read as a name.
_AMOUNT_NOTE = re.compile(
    r'\s+(?:in|per)\s+(?:one|a|\d+(?:\.\d+)?)\s*(?:g|grams?|ml)\b\.?',
    re.IGNORECASE,
)
# Units glued to a number ('0.4816%').
_GLUED_UNITS = re.compile(
    r'(?<=\d)(%|ppm|ppb|mg/g|mg/unit|mg/serving|cfu/g)(?=\s|$)',
    re.IGNORECASE,
)

_NUMBER = re.compile(r'^[-+]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)$')
_BOUND = re.compile(r'^[<>]=?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)$')
_BOUND_WORDS = {'<LOQ', '<LOD', '<LLOQ', '<RL', '<MDL', '>ULOQ', 'BLQ', 'BQL'}
_RESULT_WORDS = {
    'ND', 'N/D', 'N.D.', 'NR', 'NT', 'N/A', '--', '—',
    'NOT_DETECTED', 'NONE_DETECTED', 'NOT_PRESENT', 'NOT_TESTED',
    'NOT_REPORTED', 'NOT_REQUIRED', 'NOT_ANALYZED',
    'ABSENCE', 'ABSENT', 'PRESENCE', 'PRESENT', 'DETECTED',
    'NEGATIVE', 'POSITIVE',
}
_STATUS_WORDS = {
    'PASS': 'pass', 'PASSED': 'pass', 'FAIL': 'fail', 'FAILED': 'fail',
    'TESTED': 'tested',
}
# Qualifier flags printed beside a name or a result ('CBCa Q3',
# '0.1575 Q3', '(Q3)'). 'B1', 'B2', 'G1' and 'G2' are aflatoxins.
_FLAG = re.compile(r'^\(?[A-Z]\d{1,2}\)?$')
_AFLATOXIN_NAMES = {'B1', 'B2', 'G1', 'G2'}

# Safety analytes whose names begin with 'Total' (a group reported as
# one analyte: 'Total Yeast and Mold', 'Total Xylenes'). Other 'Total'
# rows are sums of the rows above them and are not results.
_TOTAL_ANALYTES = {
    key for key in list(MICROBIAL_KEYS) + list(RESIDUAL_SOLVENT_KEYS)
    if key.startswith('total_')
} | {'total_mycotoxins'}

_SECTION_TITLE = re.compile(
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
    re.IGNORECASE,
)
# A second title on the same line: two tables printed side by side.
_SECTION_NAMES = re.compile(
    r'\b(Cannabinoids|Terpenes|Pesticides|Heavy\s*Metals|Microbials|'
    r'Mycotoxins|Residual\s*Solvents|Foreign\s*Matter|Water\s*Activity|'
    r'Moisture)\b',
    re.IGNORECASE,
)
# Header and units rows are never analyte rows. ('mg/' and not 'mg', so
# that "MGK-264 ..." is read.)
_HEADER_GUARD = re.compile(
    r'^(?:Analyte\b|%|[µμ]g/|ug/|mg/|PPM\b|PPB\b|CFU|RFU)', re.IGNORECASE,
)

# Lines inside a results section that are not analyte rows.
_SKIP_LINE = [re.compile(p, re.IGNORECASE) for p in (
    r'^Analyte\b', r'^%\s', r'^mg/g\s', r'^PPM\s', r'^µg', r'^ug/',
    r'^CFU', r'^RFU', r'^Date\s*Tested',
    r'^Method:', r'^SOP', r'^Instrument:', r'^LOQ\s*=',
    r'^Note:', r'^Entered\s*By', r'^Total\s*THC\s*=',
    r'^Total\s*CBD\s*=', r'^1\s*Unit\s*=', r'^Total\s*theoretical',
    r'^Includes\s', r'^GCA\s*does\s*not',
    r'^ND\s*=', r'^NR\s*=', r'^Primary\s*Aromas',
    # Aroma words (a terpene page's "Primary Aromas" line), as whole
    # words, so that a "Pinene" row is not skipped.
    r'^(?:Orange|Cinnamon|Pine|Hops|Lavender|Lemon|Sweet|Earthy|'
    r'Chamomile|Clove|Wood|Basil)\b',
    r'^\d+\s+of\s+\d+', r'^Page\s+\d+', r'^Quali\x00er', r'^Qualifiers?\b',
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
)]

def _unit_label(token: str) -> Optional[str]:
    """The units label of a printed units token ('%' is 'percent', 'PPB'
    is 'ppb', 'µg/g' is 'ug/g'), or None for any other token."""
    return _UNIT_LABELS.get(token.strip().strip('()[],;:').lower())

def _in_units(number: Optional[float], from_units: Optional[str],
              to_units: Optional[str]) -> Optional[float]:
    """State an LOD, LOQ or limit in the units of the result beside it.

    A number whose column prints no units is taken to share the
    result's. Mass fractions convert (an LOQ of 0.1 % is 1.0 mg/g);
    units that do not convert to the result's (an LOQ in mg/unit beside
    a percent result) give None rather than a number in the wrong units.
    """
    if number is None or not from_units or not to_units or from_units == to_units:
        return number
    if from_units in _PPM_PER_UNIT and to_units in _PPM_PER_UNIT:
        return round(number * _PPM_PER_UNIT[from_units] / _PPM_PER_UNIT[to_units], 10)
    return None

def _default_units(analysis: str, limit: Optional[float],
                   loq: Optional[float], lod: Optional[float]) -> str:
    """Units for a row whose table prints none: the analysis's standard
    units, except heavy metals with an LOQ or limit of 20 or more, which
    can only be ppb (action levels are 0.1 to 10 ppm), and mycotoxins
    under 1, which can only be ppm (action levels are 5 to 20 ppb)."""
    reference = next((x for x in (limit, loq, lod) if x is not None), None)
    if reference is not None:
        if analysis == 'heavy_metals' and reference >= 20:
            return 'ppb'
        if analysis == 'mycotoxins' and reference < 1:
            return 'ppm'
    return STANDARD_UNITS.get(analysis, 'percent')

def _row_tokens(line: str) -> List[str]:
    """Split a table row into tokens: results printed in words joined
    ('Not_Detected'), amount notes ('in 1g') dropped, '< LOQ' rejoined
    as '<LOQ', units glued to a number split off ('0.4816%' is '0.4816',
    '%') and footnote marks removed."""
    text = line.replace('\u00a0', ' ')
    # A page number printed at the end of the line ("... Pass 2 of 6").
    text = re.sub(r'\s+(?:Page\s+)?\d+\s+of\s+\d+\s*$', '', text, flags=re.IGNORECASE)
    for pattern, joined in _JOINED_RESULTS:
        text = pattern.sub(joined, text)
    text = _AMOUNT_NOTE.sub('', text)
    text = re.sub(r'([<>])\s+(?=[\d.]|LO[DQ]\b|ULOQ\b)', r'\1', text,
                  flags=re.IGNORECASE)
    text = _GLUED_UNITS.sub(r' \1', text)
    tokens = []
    for token in text.split():
        token = token.strip('*†‡')
        if token:
            tokens.append(token)
    return tokens

def _token_kind(token: str, previous: Optional[str]) -> str:
    """Classify a row token: 'num', 'bound', 'qual' (a result printed in
    words), 'status', 'unit', 'flag' or 'name'.

    A flag-like token that begins a line or follows a status cell is a
    name, as is an aflatoxin name after a cell: 'B1' begins the row of a
    second table printed beside the first.
    """
    upper = token.upper()
    if _NUMBER.match(token):
        return 'num'
    if _BOUND.match(token) or upper in _BOUND_WORDS:
        return 'bound'
    if upper in _RESULT_WORDS:
        return 'qual'
    if token == '-' and previous in ('num', 'bound', 'qual', 'unit'):
        return 'qual'
    if upper in _STATUS_WORDS:
        return 'status'
    if _unit_label(token):
        return 'unit'
    if '/' in token and len(token) <= 10 and previous in ('num', 'bound', 'qual', 'unit') \
            and not any(ch.isdigit() for ch in token):
        return 'unit'  # Units this module does not know, after a value ('col/g').
    if _FLAG.match(token) and previous not in (None, 'status'):
        if not (upper in _AFLATOXIN_NAMES and previous != 'name'):
            return 'flag'
    return 'name'

def _split_records(tokens: List[str]) -> List[Tuple[List[str], List[Tuple[str, str]]]]:
    """Split a row's tokens into records, ``[(name_tokens, cells)]``,
    each cell a ``(kind, token)``.

    A name after a record's cells begins the next record: the row of a
    second table printed beside the first ("Abamectin 0.25 0.5 ND Pass
    Hexythiazox 0.5 1 ND Pass" is two records). A flag after a name
    stays with the name (it is stripped by _clean_name); a flag after a
    cell is dropped.
    """
    records = []
    name: List[str] = []
    cells: List[Tuple[str, str]] = []
    previous = None
    for token in tokens:
        kind = _token_kind(token, previous)
        if kind == 'name':
            if cells:
                records.append((name, cells))
                name, cells = [], []
            name.append(token)
        elif kind == 'flag':
            if not cells:
                name.append(token)
        else:
            cells.append((kind, token))
        previous = kind
    if name or cells:
        records.append((name, cells))
    return records

def _clean_name(name_tokens: List[str]) -> str:
    """Join a record's name tokens, stripping a trailing CAS number and
    qualifier flags ('THCa 23978-85-0', 'CBCa Q3', 'Bifenthrin M2') but
    keeping an aflatoxin's 'B1'."""
    name = ' '.join(name_tokens).strip()
    while True:
        before = name
        name = re.sub(r'\s+\d{2,7}-\d{2}-\d$', '', name).strip()
        match = re.search(r'\s+\(?([A-Z]\d{1,2})\)?$', name)
        if match and match.group(1) not in _AFLATOXIN_NAMES:
            name = name[:match.start()].rstrip()
        if name == before:
            return name

def _is_total_row(name: str, analysis: str) -> bool:
    """Whether a row is a 'Total' of the rows above it (Total THC, Total
    Cannabinoids, Total), which is not a result. Total aflatoxins and
    the safety analytes reported as a total (Total Yeast and Mold,
    Total Xylenes) are results."""
    low = name.lower()
    if not low.startswith('total'):
        return False
    if low in ('total aflatoxins', 'total mycotoxins'):
        return False
    if analysis not in _POTENCY_ANALYSES and _snake_case(name) in _TOTAL_ANALYTES:
        return False
    return True

def _parse_columns_line(line: str) -> Optional[List[List[List]]]:
    """Read a column header row into its tables' columns, or None.

    "Analyte LOQ Limit Mass Status" is one table whose columns are
    ``[['loq', None], ['limit', None], ['result', None], ['status',
    None]]`` (role, units label); each further 'Analyte' begins a table
    printed beside it, as does an LOD, LOQ or limit column after a
    table's result or status column. Units printed in the header are
    kept: after their column ("LOQ (%)"), or, two or more in a row, one
    per value column ("Analyte LOQ Mass Mass % % mg/g"). A line of
    column words alone ("LOQ Limit Mass", when a two-row header prints
    'Analyte' on a line of its own) is a header row if it names two
    value columns. Returns None for a line that is not a header row.
    """
    text = re.sub(r'\bPass\s*/\s*Fail\b', 'Pass/Fail', line, flags=re.IGNORECASE)
    tokens = text.split()
    if not tokens:
        return None
    led = tokens[0].lower().strip(':') in _GROUP_WORDS
    groups: List[List[List]] = [] if led else [[]]
    marks: List[Tuple[str, Any]] = []
    i = 0
    while i < len(tokens):
        low = tokens[i].lower().strip(':,')
        following = tokens[i + 1].lower().strip(':,') if i + 1 < len(tokens) else ''
        if low in _GROUP_WORDS:
            groups.append([])
            i += 1
            continue
        role = _COLUMN_PHRASES.get((low, following))
        width = 2 if role else 1
        role = role or _COLUMN_WORDS.get(low)
        if role:
            if role in ('lod', 'loq', 'limit') and any(
                    c[0] in ('result', 'status') for c in groups[-1]):
                groups.append([])  # A second table without its 'Analyte'.
            column = [role, None]
            groups[-1].append(column)
            marks.append(('col', column))
        else:
            label = _unit_label(tokens[i])
            if label:
                marks.append(('unit', label))
            elif not led:
                return None  # Not a header row: a word that names no column.
        i += width
    n_values = sum(1 for g in groups for c in g if c[0] in _VALUE_ROLES)
    if n_values == 0 or (not led and n_values < 2):
        return None
    labels = [mark for kind, mark in marks if kind == 'unit']
    if any(a[0] == 'unit' and b[0] == 'unit' for a, b in zip(marks, marks[1:], strict=False)):
        _apply_units(groups, labels)
    else:
        for (kind_a, a), (kind_b, b) in zip(marks, marks[1:], strict=False):
            if kind_a == 'col' and kind_b == 'unit' and a[0] in _VALUE_ROLES:
                a[1] = b
    return groups

def _parse_units_line(line: str) -> Optional[List[str]]:
    """Read a units row ("% % mg/g", "PPB PPB PPB") into its labels, or
    None for any other line. The 'Analyte' and 'Status' cells of a two-
    row header can print on the units line ("PPB PPB PPB Status")."""
    tokens = [t for t in re.split(r'[\s,]+', line.strip()) if t]
    tokens = [t for t in tokens
              if t.lower().strip(':') not in _GROUP_WORDS
              and _COLUMN_WORDS.get(t.lower().strip(':')) != 'status']
    labels = [_unit_label(t) for t in tokens]
    if tokens and all(labels):
        return labels
    return None

def _apply_units(groups: List[List[List]], labels: List[str]) -> None:
    """Give a units row's labels to the value columns (LOD, LOQ, limit,
    result; not status) of the tables printed side by side: one label
    per column, or the same labels for each table, or right-aligned when
    the row prints fewer labels than there are columns."""
    value_columns = [[c for c in g if c[0] in _VALUE_ROLES] for g in groups]
    if len(labels) == sum(len(v) for v in value_columns):
        remaining = iter(labels)
        for columns in value_columns:
            for column in columns:
                column[1] = next(remaining)
        return
    if len(groups) > 1 and len({len(v) for v in value_columns}) == 1 \
            and len(labels) == len(value_columns[0]):
        chunks = [labels] * len(groups)
    elif len(groups) > 1 and len(labels) % len(groups) == 0:
        per = len(labels) // len(groups)
        chunks = [labels[i * per:(i + 1) * per] for i in range(len(groups))]
    else:
        chunks = [labels] + [[] for _ in groups[1:]]
    for columns, chunk in zip(value_columns, chunks, strict=False):
        chunk = chunk[-len(columns):] if columns else []
        for column, label in zip(columns[len(columns) - len(chunk):], chunk, strict=False):
            column[1] = label

def _default_groups(analysis: str, labels: List[str]) -> Optional[List[List[List]]]:
    """Columns for a units row printed without a header row, by the
    number of units: "% % mg/g" is LOQ, percent, mg/g ("% mg/g", two
    results); "PPB PPB PPB" is LOQ, limit, result ("CFU/g CFU/g", limit
    and result). Six or eight units are two tables side by side."""
    n = len(labels)
    if n <= 4:
        sizes = [n]
    elif n % 2 == 0 and n // 2 <= 4:
        sizes = [n // 2, n // 2]
    else:
        return None
    potency = analysis in _POTENCY_ANALYSES
    groups, start = [], 0
    for size in sizes:
        chunk = labels[start:start + size]
        start += size
        if potency:
            if size == 2 and chunk[0] == chunk[1]:
                roles = ['loq', 'result']
            else:
                roles = {1: ['result'], 2: ['result', 'result'],
                         3: ['loq', 'result', 'result'],
                         4: ['lod', 'loq', 'result', 'result']}[size]
        else:
            roles = {1: ['result'], 2: ['limit', 'result'],
                     3: ['loq', 'limit', 'result'],
                     4: ['lod', 'loq', 'limit', 'result']}[size]
        groups.append([[role, label] for role, label in zip(roles, chunk, strict=False)])
    return groups

def _is_percent_mg_pair(first: Tuple[str, str], second: Tuple[str, str]) -> bool:
    """Whether two result cells are a percent and its mg/g: two
    non-detects, two zeros, or numbers the second of which is ten times
    the first to the precision printed, printed with the first's digits
    ('83.9504', '839.504'; the mg/g may be rounded, '0.4761', '4.76').
    An LOQ and a result ten times it are not ('0.001', '0.0100')."""
    (kind_a, a), (kind_b, b) = first, second
    if kind_a != 'num' and kind_b != 'num':
        return True
    if kind_a != 'num' or kind_b != 'num':
        return False
    x, y = float(a.replace(',', '')), float(b.replace(',', ''))
    if x == 0 and y == 0:
        return True
    if x <= 0 or y <= 0:
        return False
    def step(t: str) -> float:
        return 10 ** -len(t.split('.')[1]) if '.' in t else 1.0
    if abs(y - 10 * x) > 10 * step(a) / 2 + step(b) / 2 + 1e-9:
        return False
    def digits(t: str) -> str:
        return t.replace(',', '').replace('.', '').lstrip('+-').lstrip('0')
    da, db = digits(a), digits(b)
    return da == db or (len(db) >= 2 and da.startswith(db))

def _potency_layout(values: List[Tuple[str, str]]) -> List[List]:
    """Columns of a cannabinoid or terpene row whose table prints no
    header: "LOQ Mass(%) Mass(mg/g)" when the last two cells are a
    percent and its mg/g ("Δ9-THC 0.1 90.0348 900.348", or without the
    LOQ "Δ9-THC 83.9504 839.504"); otherwise LOQ, then the result."""
    n = len(values)
    if n >= 2 and _is_percent_mg_pair(values[-2], values[-1]):
        lead = ['lod', 'loq'][max(0, 4 - n):] if n > 2 else []
        return [[r, None] for r in lead] + [['result', 'percent'], ['result', 'mg/g']]
    roles = {0: ['result'], 1: ['result'], 2: ['loq', 'result'],
             3: ['loq', 'result', 'result']}.get(n, ['lod', 'loq', 'result', 'result'])
    return [[r, None] for r in roles]

def _assign_cells(values: List[Tuple[str, str]], columns: List[List],
                  analysis: str, status: Optional[str]) -> Tuple[List, bool]:
    """Place a record's value cells in its table's value columns.

    Returns ``(slots, missing)``: one cell (or None) per column, and
    whether the row's result cell is not on the line.

    1. One cell per column, with numbers in the LOD/LOQ/limit columns:
       each cell is what its column says.
    2. A non-detect or a bound ('ND', '<LOQ', '<10') is a result,
       wherever it prints; the numbers are the LOD/LOQ/limit cells
       (right-aligned: the limit and LOQ print, an LOD may not).
    3. Numbers only, more of them than the LOD/LOQ/limit columns (and
       every cannabinoid or terpene row): results are the last columns.
       A cannabinoid or terpene row one cell short lacks its LOQ only
       when its last two numbers are a percent and its mg/g; otherwise
       it lacks its last result and its cells are read in order.
    4. Numbers only, no more of them than the LOD/LOQ/limit columns, in
       a pass/fail row or a table with an LOD or LOQ column: those are
       the cells printed and the result is not on the line. Taking the
       last number would take the limit ("Arsenic 200 400 Pass" is not
       400 ppb of arsenic).
    5. Otherwise (a "Tested" row may print no limit), right-aligned.
    """
    n = len(columns)
    res_idx = [i for i, c in enumerate(columns) if c[0] == 'result']
    non_idx = [i for i, c in enumerate(columns) if c[0] != 'result']
    slots: List[Optional[Tuple[str, str]]] = [None] * n
    if len(values) == n and all(values[i][0] == 'num' for i in non_idx):
        return list(values), False
    quals = [v for v in values if v[0] != 'num']
    nums = [v for v in values if v[0] == 'num']
    if len(quals) > len(res_idx) > 0:
        # More words than results: a limit printed in words comes first
        # ("Absence in 1g  Presence  Fail" found aspergillus).
        quals = quals[-len(res_idx):]
    if quals:
        for i, v in zip(res_idx, quals, strict=False):
            slots[i] = v
        free = res_idx[len(quals):]
        k = len(non_idx)
        if len(nums) <= k:
            for i, v in zip(non_idx[k - len(nums):], nums, strict=False):
                slots[i] = v
        else:
            for i, v in zip(non_idx, nums[:k], strict=False):
                slots[i] = v
            for i, v in zip(free, nums[k:], strict=False):
                slots[i] = v
        return slots, False
    if not nums:
        return slots, bool(res_idx)
    if analysis in _POTENCY_ANALYSES and len(nums) < n and len(res_idx) >= 2:
        # A short cannabinoid or terpene row lacks its LOQ ("83.9504
        # 839.504": a percent and its mg/g, right-aligned below) or its
        # last result ("0.1 0.3965": the LOQ and the percent, in order).
        # A lone number cannot be placed: it is not read as a result.
        if len(nums) == 1:
            return slots, True
        if not _is_percent_mg_pair(nums[-2], nums[-1]):
            for i, v in zip(non_idx + res_idx, nums, strict=False):
                slots[i] = v
            return slots, all(slots[i] is None for i in res_idx)
    if analysis in _POTENCY_ANALYSES or len(nums) > len(non_idx):
        take = nums[-n:]
        for i, v in zip(range(n - len(take), n), take, strict=False):
            slots[i] = v
        return slots, all(slots[i] is None for i in res_idx)
    if status in ('pass', 'fail') or any(columns[i][0] in ('lod', 'loq') for i in non_idx):
        if len(nums) == len(non_idx):
            for i, v in zip(non_idx, nums, strict=False):
                slots[i] = v
        return slots, True
    take = nums[-n:]
    for i, v in zip(range(n - len(take), n), take, strict=False):
        slots[i] = v
    return slots, all(slots[i] is None for i in res_idx)

def _assign_by_layout(values: List[Tuple[str, str]], analysis: str,
                      status: Optional[str]) -> Tuple[List[List], List, bool]:
    """Columns and cells of a record whose table printed no header or
    units row. Cannabinoids and terpenes: see _potency_layout. Other
    tables: a non-detect or a bound is the result and the numbers are
    the LOD, LOQ and limit before it; numbers only, the result is the
    last ("LOD LOQ Limit Mass Status"), never the first: the first
    number of a microbial row is its limit ("E. Coli 100 <LOQ Pass")."""
    if analysis in _POTENCY_ANALYSES:
        columns = _potency_layout(values)
        slots, missing = _assign_cells(values, columns, analysis, status)
        return columns, slots, missing
    quals = [v for v in values if v[0] != 'num']
    nums = [v for v in values if v[0] == 'num']
    if quals:
        nums = nums[-3:]
        roles = ['lod', 'loq', 'limit'][3 - len(nums):] + ['result']
        return [[r, None] for r in roles], nums + [quals[-1]], False   # the word nearest the status
    if not nums:
        return [['result', None]], [None], False
    nums = nums[-4:]
    roles = {1: ['result'], 2: ['limit', 'result'], 3: ['loq', 'limit', 'result'],
             4: ['lod', 'loq', 'limit', 'result']}[len(nums)]
    return [[r, None] for r in roles], nums, False

def _read_record(cells: List[Tuple[str, str]], columns: Optional[List[List]],
                 analysis: str, default_units: Optional[str] = None,
                 ) -> Optional[Tuple[Dict, bool]]:
    """Read a record's cells against its table's columns.

    Returns ``(row, missing)``: the row's 'units', 'value', 'qualifier',
    'lod', 'loq', 'limit' and 'status' (and 'mg_g' for a cannabinoid or
    terpene table with an mg/g column), and whether its result cell is
    not on the line. None when the record has nothing to read.

    The value is read from the percent column when a cannabinoid or
    terpene table prints one, else from the first result column, and
    'units' names that column's units: units printed in the table, else
    on the row, else ``default_units`` (units on the section title),
    else _default_units.
    """
    status = None
    values: List[Tuple[str, str]] = []
    row_units: List[str] = []
    for kind, token in cells:
        if kind == 'status':
            status = status or _STATUS_WORDS[token.upper()]
        elif kind == 'unit':
            row_units.append(_unit_label(token))
        elif kind in ('num', 'bound', 'qual'):
            values.append((kind, token))
    if not values and status is None:
        return None
    value_columns = [c for c in (columns or []) if c[0] in _VALUE_ROLES]
    if value_columns:
        slots, missing = _assign_cells(values, value_columns, analysis, status)
    else:
        value_columns, slots, missing = _assign_by_layout(values, analysis, status)
    labels = [c[1] for c in value_columns]

    # Two result columns printed without units: a percent and its mg/g
    # when the cells say so.
    result_at = [i for i, c in enumerate(value_columns) if c[0] == 'result']
    potency = analysis in _POTENCY_ANALYSES
    if potency and len(result_at) >= 2:
        a, b = result_at[0], result_at[1]
        if labels[a] is None and labels[b] is None and slots[a] and slots[b] \
                and _is_percent_mg_pair(slots[a], slots[b]):
            labels[a], labels[b] = 'percent', 'mg/g'

    # The result: the percent column when there is one, else the first
    # result column with a cell.
    chosen = None
    if potency:
        chosen = next((i for i in result_at if slots[i] and labels[i] == 'percent'), None)
    if chosen is None:
        chosen = next((i for i in result_at if slots[i]), None)
    if chosen is None:
        value, qualifier, bound = None, '', None
        units = labels[result_at[0]] if result_at else None
    else:
        value, qualifier, bound = _parse_result(slots[chosen][1])
        units = labels[chosen]
    units = units or (row_units[0] if row_units else None) or default_units

    def number(role: str) -> Tuple[Optional[float], Optional[str]]:
        for i, column in enumerate(value_columns):
            if column[0] == role and slots[i] and slots[i][0] == 'num':
                return _parse_number(slots[i][1]), labels[i]
        return None, None

    lod, lod_units = number('lod')
    loq, loq_units = number('loq')
    limit, limit_units = number('limit')
    if not units:
        units = (lod_units or loq_units or limit_units
                 or _default_units(analysis, limit, loq, lod))
    lod = _in_units(lod, lod_units, units)
    loq = _in_units(loq, loq_units, units)
    limit = _in_units(limit, limit_units, units)
    uloq = None
    if qualifier == '<LOQ' and bound is not None and loq is None:
        loq = bound
    elif qualifier == '>ULOQ' and bound is not None:
        uloq = bound
    row = {
        'units': units,
        'value': value,
        'qualifier': qualifier,
        'lod': lod,
        'loq': loq,
        'limit': limit,
        'status': status,
    }
    if uloq is not None:
        row['uloq'] = uloq
    if potency:
        mg_at = next((i for i in result_at if labels[i] == 'mg/g' and i != chosen), None)
        if mg_at is not None:
            row['mg_g'] = _parse_result(slots[mg_at][1])[0] if slots[mg_at] else None
    return row, missing

def _build_result(analysis: str, name_tokens: List[str],
                  cells: List[Tuple[str, str]],
                  columns: Optional[List[List]] = None,
                  default_units: Optional[str] = None,
                  ) -> Tuple[Optional[Dict], bool]:
    """Build a result dict from a record, or None for a record that is
    not an analyte row. Returns ``(result, missing)``, ``missing`` being
    whether the row's result cell is not on its line."""
    name = _clean_name(name_tokens)
    if len(name) < 2 or not re.search(r'[^\W\d_]', name):
        return None, False
    if name.lower() in ('of', 'page'):
        return None, False  # A page number ("Page 1 of 6").
    if _is_total_row(name, analysis):
        return None, False
    read = _read_record(cells, columns, analysis, default_units)
    if read is None:
        return None, False
    row, missing = read
    result = {'analysis': analysis, 'key': _snake_case(name), 'name': name}
    result.update(row)
    return result, missing

def _parse_analyte_line(line: str, analysis: str, units: str,
                        columns: Optional[List[List]] = None) -> Optional[Dict]:
    """Parse a single analyte result line from text.

    Reads the line's first record against ``columns``, its table's
    columns as _parse_columns_line returns them for one table (when
    None, against CC's layouts, see _assign_by_layout):
        Cannabinoids: Analyte [LOD] [LOQ] Result(%) Result(mg/g)
        Terpenes:     Analyte LOQ Result(%) Result(mg/g)
        Pesticides:   Analyte LOD LOQ Limit Result Status
        Heavy Metals: Analyte LOD LOQ Limit Result Status
        Microbials:   Analyte [Limit] Result Status
        Mycotoxins:   Analyte LOD LOQ Limit Result Status
        Solvents:     Analyte LOD LOQ Limit Result Status
    ``units`` labels the result when neither the columns nor the line
    print units.
    """
    line = line.strip()
    if not line or _HEADER_GUARD.match(line) or any(p.match(line) for p in _SKIP_LINE):
        return None
    for name_tokens, cells in _split_records(_row_tokens(line)):
        if not name_tokens:
            continue
        result, _ = _build_result(analysis, name_tokens, cells, columns, units)
        if result:
            return result
    return None

class _Table:
    """The results table being read: its analyses (one per table printed
    side by side), the units on its section title, and its columns once
    its header and units rows are read."""

    def __init__(self, analyses: List[str], units: Optional[str] = None):
        self.analyses = analyses
        self.units = units
        self.groups: Optional[List[List[List]]] = None
        self.units_read = False

    def set_columns(self, groups: List[List[List]]) -> None:
        self.groups = groups
        self.units_read = any(c[1] for g in groups for c in g)

    def set_units(self, labels: List[str]) -> None:
        """Read the table's units row (once: a later lone units token,
        such as a summary box's '%', does not relabel the columns)."""
        if self.units_read:
            return
        self.units_read = True
        if self.groups:
            _apply_units(self.groups, labels)
        else:
            self.groups = _default_groups(self.analyses[0], labels)

    def columns(self, index: int, count: int,
                name: Optional[str] = None) -> Tuple[str, Optional[List[List]]]:
        """The analysis and columns of a line's ``index``-th of ``count``
        records. A line with one record in a table of two side by side
        (one table ran longer than the other) is the table its analyte
        belongs to: the left table's columns and units would put
        ochratoxin A, in ug/kg, among the heavy metals in ppm."""
        analysis = self.analyses[0]
        if not self.groups:
            return analysis, None
        if count > 1 and len(self.groups) > 1:
            index = min(index, len(self.groups) - 1)
            if len(self.analyses) >= len(self.groups):
                analysis = self.analyses[index]
            return analysis, self.groups[index]
        if count == 1 and len(self.groups) > 1 and name:
            known = _ANALYSIS_OF.get(analysis_for_analyte(name), analysis_for_analyte(name))
            for k, candidate in enumerate(self.analyses[:len(self.groups)]):
                if known and candidate == known:
                    return candidate, self.groups[k]
        return analysis, self.groups[0]

# cannlytics' analyses (analysis_for_analyte) by this module's names.
_ANALYSIS_OF = {'microbes': 'microbials', 'moisture_content': 'moisture'}

def _match_section(line: str) -> Optional[Tuple[List[str], Optional[str]]]:
    """Read a section title line into its analyses (a second title on the
    line is a second table printed beside the first) and any units it
    prints ("Heavy Metals (PPB)"), or None."""
    match = _SECTION_TITLE.match(line)
    if not match:
        return None
    analyses = [_classify_analysis(match.group(1))]
    rest = line[match.end():]
    analyses += [_classify_analysis(m.group(1)) for m in _SECTION_NAMES.finditer(rest)]
    units = next((label for label in map(_unit_label, re.split(r'[\s,]+', rest)) if label), None)
    return analyses, units

def _orphan_cell(records: List[Tuple[List[str], List[Tuple[str, str]]]]) -> Optional[str]:
    """The result cell of a line that prints only one ("<LOQ", "ND"),
    optionally with units, or None."""
    if len(records) != 1 or records[0][0]:
        return None
    cells = records[0][1]
    values = [token for kind, token in cells if kind in ('num', 'bound', 'qual')]
    others = [kind for kind, _ in cells if kind not in ('num', 'bound', 'qual', 'unit')]
    if len(values) == 1 and not others:
        return values[0]
    return None

def _attach_orphan_results(missing: List[Tuple[int, int, Dict]],
                           orphans: Dict[int, Tuple[int, str]]) -> None:
    """Read results printed on lines of their own into the rows missing
    them.

    ``missing`` holds ``(line_no, table_id, result)`` for rows whose
    result cell is not on their line; ``orphans`` maps a line number to
    ``(table_id, cell)`` for lines printing only a result cell. A cell
    taller than its row (a two-line result cell beside vertically
    centered cells) prints above its row, or below it. Every row of a
    table that misses its result must find a lone cell on the same side
    (all on the line above, or all on the line below) or none is read,
    so that a cell is never given to a neighbor's row.
    """
    tables: Dict[int, List[Tuple[int, Dict]]] = {}
    for line_no, table_id, result in missing:
        tables.setdefault(table_id, []).append((line_no, result))
    for table_id, rows in tables.items():
        if len({n for n, _ in rows}) != len(rows):
            continue  # Two rows on one line: a cell cannot be placed.
        lone = {n: cell for n, (t, cell) in orphans.items() if t == table_id}
        above = all(n - 1 in lone for n, _ in rows)
        below = all(n + 1 in lone for n, _ in rows)
        if above == below:
            continue
        offset = -1 if above else 1
        for n, result in rows:
            value, qualifier, bound = _parse_result(lone[n + offset])
            result['value'] = value
            result['qualifier'] = qualifier
            if qualifier == '<LOQ' and bound is not None and result.get('loq') is None:
                result['loq'] = bound
            elif qualifier == '>ULOQ' and bound is not None:
                result['uloq'] = bound

def _parse_results_page(text: str, analysis: Optional[str] = None,
                        units: Optional[str] = None,
                        ) -> Tuple[List[Dict], Set[str]]:
    """Parse the results tables of one page of text.

    Returns the page's results and its analyses (those whose sections
    it titles, and those of its results). ``analysis`` (with its
    ``units``) starts the page inside that analysis's table, for text
    that prints no section title.
    """
    results: List[Dict] = []
    analyses: Set[str] = set()
    table = _Table([analysis], units) if analysis else None
    table_id = 0
    missing: List[Tuple[int, int, Dict]] = []
    orphans: Dict[int, Tuple[int, str]] = {}
    line_no = -1
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        line_no += 1

        # Louisiana/Orion footer boundary: once the legal disclaimer
        # begins, we're past the analyte tables. Stop parsing analytes so
        # disclaimer sentences don't leak in as fake result rows. Gated to
        # LA markers, so no other state's parsing changes.
        low = stripped.lower()
        if any(mk in low for mk in _LA_FOOTER_MARKERS):
            table = None
            continue

        # Section titles begin a table.
        section = _match_section(stripped)
        if section:
            names, title_units = section
            table = _Table(names, title_units)
            table_id += 1
            analyses.add(names[0])
            continue
        if table is None:
            continue

        # Column header and units rows.
        groups = _parse_columns_line(stripped)
        if groups:
            table.set_columns(groups)
            continue
        labels = _parse_units_line(stripped)
        if labels:
            table.set_units(labels)
            continue
        if _HEADER_GUARD.match(stripped):
            if not table.groups:
                table.units = table.units or next(
                    (u for u in map(_unit_label, re.split(r'[\s,]+', stripped)) if u),
                    None)
            continue
        if any(p.match(stripped) for p in _SKIP_LINE):
            continue

        # Analyte rows, one record per table printed side by side.
        records = _split_records(_row_tokens(stripped))
        lone = _orphan_cell(records)
        if lone is not None:
            if table.analyses[0] not in _POTENCY_ANALYSES:
                orphans[line_no] = (table_id, lone)
            continue
        records = [r for r in records if r[0]]
        for index, (name_tokens, cells) in enumerate(records):
            record_analysis, columns = table.columns(index, len(records), ' '.join(name_tokens))
            result, is_missing = _build_result(
                record_analysis, name_tokens, cells, columns, table.units)
            if result:
                results.append(result)
                if is_missing:
                    missing.append((line_no, table_id, result))

    _attach_orphan_results(missing, orphans)
    # A second title on a line counts once its table yields rows.
    analyses.update(r['analysis'] for r in results)
    return results, analyses

def _parse_results_from_text(pdf) -> Tuple[List[Dict], List[str]]:
    """Extract all analyte results from the PDF text.

    Iterates through each page, identifies analysis sections,
    and parses analyte lines within each section (_parse_results_page).
    """
    results = []
    analyses = set()

    for page in pdf.pages:
        text = _deligature(page.extract_text() or '')
        if _is_cover_sheet(text):
            continue
        page_results, page_analyses = _parse_results_page(text)
        results.extend(page_results)
        analyses.update(page_analyses)

    return results, sorted(analyses)

def _parse_two_column_results(text: str, analysis: str, units: str) -> List[Dict]:
    """Parse results from two-column layout pages.

    Many Confident Cannabis COAs use a side-by-side two-column
    layout for pesticides and terpenes where the left and right
    halves each contain separate analyte data. pdfplumber merges each
    pair of rows into one line ("Abamectin 0.25 0.5 ND Pass Hexythiazox
    0.5 1 ND Pass"), which _split_records splits into its two records.
    ``text`` holds the table's header, units and data rows (it needs no
    section title); ``units`` labels results when the table prints none.
    """
    return _parse_results_page(text, analysis, units)[0]

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
            # Total terpenes (percent, so only terpenes read in percent).
            if not obs.get('total_terpenes'):
                terp_sum = sum(
                    r.get('value', 0) or 0
                    for r in results
                    if r['analysis'] == 'terpenes'
                    and r['key'] not in ('total_terpenes',)
                    and r.get('units') == 'percent'
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
