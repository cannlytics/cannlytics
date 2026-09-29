"""
Parse CannaBusiness Laboratories COA -- COA Doc Hybrid Algorithm
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2026
Updated: 7/15/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse CannaBusiness Laboratories COA PDFs directly from the PDF text --
    no network access required. CannaBusiness Laboratories (legal entity
    Aquatic Laboratories LLC, KDA Lic. P_0059) is one of two safety-
    compliance facilities serving Kentucky's medical cannabis program
    (the other being KCA Laboratories).

    Identification:
        CannaBusiness COAs contain 'cannabusinesslabs.us' and
        'CANNABUSINESS LABORATORIES' on page 1, and the distinctive
        license string 'P_0059'.

    Two page-1 layouts (both handled):
        A. FULL-PANEL (Buds / Flower) -- 7 pages. Page 1 is a
           "CANNABINOID PROFILE" cover page (sample image, bar chart,
           % / mg/g cannabinoid table with Total Potential THC/CBD/CBG);
           the "Overall Batch Results" pass/fail grid + full metadata
           block is on page 2. Full analysis panel: Potency, Microbial,
           Mycotoxins, Metals, Pesticides (APCI + ESI), Terpenoids,
           Water Activity.
        B. BIOMASS -- 4 pages. There is NO cover profile page; page 1
           leads with the "Overall Batch Results" grid + metadata block.
           Limited panel: Potency + Pesticides (APCI + ESI) only. The
           microbial, metals, mycotoxin, terpene, and water-activity
           panels were NOT run -> they serialize as absent (null), never
           zero-filled.

    Metadata block (Overall Batch Results header, label:value pairs):
        Sample Name, Sample ID, Order Number, External Sample ID,
        Batch Number, Product Type, Sample Type (Buds / Biomass /
        Flower), Received / Collection dates, COA released; Customer
        block (name, street, city/state/zip, cultivator CULT license).

    CRITICAL parsing notes (validated against the sample batch):
        1. STRAIN FIELD IS NOT FIXED. The human-readable strain lives in
           whichever of {Sample Name, External Sample ID} is NOT a Metrc
           package tag (Metrc tags match 1A4...). For pure-biomass
           submissions there may be no human-readable strain at all
           (both fields empty / tag-only) -> strain_name = None, never a
           guess.
        2. SAMPLE TYPE DRIVES PANEL SCOPE. Biomass ran potency +
           pesticides only; the parser must NOT assume a fixed analysis
           set. Untested panels are simply absent (null), never 0.0.
        3. DUAL %/mg-g ROWS. Every analyte is printed twice -- once as
           "% Dry Weight" and once as "mg/g". These collapse to a single
           result record carrying both units (value = percent,
           value_mg_g = mg/g).
        4. TWO PESTICIDE PANELS. Pesticides are reported as separate APCI
           (CB-SOP-053) and ESI (CB-SOP-025) tables whose analyte order
           is not stable; content-based matching (not positional) is
           used, and both panels merge into the single 'pesticides'
           analysis.
        5. NULL vs ZERO. ND / <LOQ / >ULOL / NT serialize as ``None``,
           never 0.0. The raw token is preserved in ``result_raw``.
        6. BIOMASS TOTAL THC. Biomass COAs do not print a Total Potential
           THC summary (flower/buds do, on the cover page). For biomass,
           total_thc is computed from the lab's own printed decarb
           formula: Total Potential THC = 0.877 * THCa + d9-THC, else
           null. The same formula backs total_cbd / total_cbg.
        7. FAILING RESULTS ARE PRESERVED (never filtered). Overall status
           is Fail if any panel/analyte failed.

    Dedup: the pipeline dedups by pdf_hash (SHA-256); this parser reports
    Sample ID / batch / Metrc tag as-is.

Data Points:
    * product_name, product_type, strain_name, sample_type
    * date_tested (COA Released), date_received, date_collected
    * batch_number, sample_id (lab_id), order_number, metrc_ids
    * lab, lab_license_number, lab_address/city/state/zipcode, lab_phone
    * producer, producer_license_number, producer_street/city/state/zip
    * total_thc, total_cbd, total_cannabinoids, total_cbg, total_terpenes,
      moisture, cbd_thc_ratio, cbg_thc_ratio
    * status (overall pass/fail)
    * analyses (list) and results (list of analyte dicts)
"""
# Standard imports:
import hashlib
import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# External imports (only pdfplumber allowed per dependency policy):
import pdfplumber


# ── CannaBusiness Laboratories constants ───────────────────────────

CANNABUSINESS_LAB = {
    'coa_algorithm': 'cannabusiness.py',
    'coa_algorithm_entry_point': 'parse_cannabusiness_coa',
    'lab': 'CannaBusiness Laboratories',
    'lab_legal_entity': 'Aquatic Laboratories LLC',
    'lab_license_number': 'P_0059',            # KDA testing license
    'lab_med_license_number': 'TEST0004034',   # Medical cannabis license
    'lab_address': '2554 Palumbo Drive, Lexington, KY 40509',
    'lab_street': '2554 Palumbo Drive',
    'lab_city': 'Lexington',
    'lab_state': 'KY',
    'lab_zipcode': '40509',
    'lab_phone': '(859) 514-6999',
    'lab_email': 'INFO@CANNABUSINESSLABS.US',
    'lab_website': 'cannabusinesslabs.us',
    'lab_accreditation': 'PJLA #109588',
}

# Result tokens that must serialize as null (never 0.0).
NULL_TOKENS = {'ND', 'NT', 'UA', 'NR', 'N/A', 'NA', '-', '--', '\u2014',
               'Negative'}
BELOW_LOQ_TOKENS = {'<LOQ', '<loq'}
ABOVE_TOKENS = {'>ULOL', '>ulol', '>ULOL'}
# Qualitative microbial tokens.
QUAL_NEG = {'Negative', 'Not Detected', 'ND'}
QUAL_POS = {'Positive', 'Detected'}

# A Metrc package tag: 1A4... (24 chars). Used to decide which of
# Sample Name / External Sample ID holds the human-readable strain.
METRC_RE = re.compile(r'^1A4[0-9A-Z]{5,}$')

# Analyte display name -> standardized snake_case key.
ANALYTE_KEY_MAP = {
    # Cannabinoids (both cover-page "CBC" and detail "CBC (Cannabichromene)")
    'CBC': 'cbc', 'CBD': 'cbd', 'CBDa': 'cbda', 'CBDA': 'cbda',
    'CBDV': 'cbdv', 'CBG': 'cbg', 'CBGa': 'cbga', 'CBGA': 'cbga',
    'CBN': 'cbn', 'd8-THC': 'delta_8_thc', 'D8-THC': 'delta_8_thc',
    'd9-THC': 'delta_9_thc', 'D9-THC': 'delta_9_thc',
    'THCa': 'thca', 'THCA': 'thca', 'THCV': 'thcv',
    'Total Cannabinoids': 'total_cannabinoids',
    'Total Potential THC': 'total_thc', 'Total Potential CBD': 'total_cbd',
    'Total Potential CBG': 'total_cbg',
    # Metals
    'Arsenic': 'arsenic', 'Cadmium': 'cadmium',
    'Lead': 'lead', 'Mercury': 'mercury',
    # Pesticide isomers that must not collide under snake_case:
    'MGK-264 (20.1)': 'mgk_264_20_1', 'MGK-264 (79.9)': 'mgk_264_79_9',
    # Mycotoxins
    'Aflatoxin B1': 'aflatoxin_b1', 'Aflatoxin B2': 'aflatoxin_b2',
    'Aflatoxin G1': 'aflatoxin_g1', 'Aflatoxin G2': 'aflatoxin_g2',
    'Total Aflatoxins': 'total_aflatoxins',
    'Ochratoxin-M+H': 'ochratoxin_a', 'Ochratoxin A': 'ochratoxin_a',
    # Microbials
    'E.coli by Plating': 'total_ecoli', 'Total Escherichia coli': 'total_ecoli',
    'Listeria monocytogenes': 'listeria_monocytogenes',
    'Listeria spp.': 'listeria',
    'Salmonella spp.': 'salmonella', 'Salmonella species': 'salmonella',
    'Shiga toxin-producing E. coli (STEC)': 'stec',
    'Total Yeast and Mold': 'yeast_and_mold', 'Yeast and Mold': 'yeast_and_mold',
    'Aspergillus spp.': 'pathogenic_aspergillus',
    # Water activity / moisture
    'Water Activity': 'water_activity', 'Percent Moisture': 'moisture',
}

# Detail-table cannabinoid rows are named "<CODE> (<Full Name>)"; the
# code before the parenthetical is what we key on.
CANN_DETAIL_CODE_RE = re.compile(r'^([A-Za-z0-9\-]+)\s*\(')

# Panel section headers (line-based). A header line begins a section that
# continues until the next header or footer. Sections repeat across pages
# and several share a page, so we track state over the whole document.
SECTION_HEADERS = {
    'Potency - Flower': 'potency',
    'Microbial - Flower': 'microbials',
    'Microbial': 'microbials',
    'Mycotoxins': 'mycotoxins',
    'Metals': 'metals',
    'Pesticides (APCI)': 'pesticides',
    'Pesticides (ESI)': 'pesticides',
    'Terpenoids': 'terpenes',
    'Water Activity': 'water_activity',
}


# ── Value / token helpers ──────────────────────────────────────────

def _snake(name: str) -> str:
    """Fallback snake_case for analyte names not in the key map.

    Parentheticals are dropped EXCEPT numeric-bearing ones that
    distinguish otherwise-identical analytes (e.g. the MGK-264 isomers
    ``MGK-264 (20.1)`` vs ``MGK-264 (79.9)`` -> ``mgk_264_20_1`` vs
    ``mgk_264_79_9``). Descriptive parentheticals like ``(Cannabichromene)``
    or ``(mixture of isomers)`` are still dropped.
    """
    s = name.strip()
    s = s.replace('\u03b1', 'alpha_').replace('\u03b2', 'beta_')
    s = s.replace('\u03b3', 'gamma_').replace('\u0394', 'delta_')
    s = s.replace('\u03b4', 'delta_')
    # Preserve numeric-only parentheticals; drop textual ones.
    def _paren(m):
        inner = m.group(1)
        return ('_' + inner) if re.fullmatch(r'[\d.]+', inner.strip()) else ''
    s = re.sub(r'\(([^)]*)\)', _paren, s)
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')


def _key_for(name: str) -> str:
    return ANALYTE_KEY_MAP.get(name, _snake(name))


def _num(token: Optional[str]) -> Optional[float]:
    """Parse a numeric token to float, or None for ND/<LOQ/>ULOL/NT/etc.

    Enforces the null-vs-zero doctrine: non-detects and untested values
    return None, never 0.0. A literal printed 0 is returned as 0.0 only
    when it is a genuine number token.
    """
    if token is None:
        return None
    t = str(token).strip().replace(',', '')
    if t in NULL_TOKENS or t in BELOW_LOQ_TOKENS or t in ABOVE_TOKENS:
        return None
    t = t.rstrip('%')
    try:
        return float(t)
    except ValueError:
        return None


def _raw_token(token: Optional[str]) -> Optional[str]:
    """Normalize the raw result token for provenance."""
    if token is None:
        return None
    t = str(token).strip()
    if t in BELOW_LOQ_TOKENS:
        return '<LOQ'
    if t in ABOVE_TOKENS:
        return '>ULOL'
    return t


def _clean_strain(value: str) -> str:
    """Tidy a strain string (drop trailing lab shorthand / dates)."""
    if not value:
        return ''
    s = value.strip()
    # Collapse internal runs of whitespace introduced by wrapped text.
    s = re.sub(r'\s{2,}', ' ', s)
    return s


# ── Coordinate-aware row reconstruction (metadata block) ───────────

def _rows(page, y_tol: float = 3.0) -> List[str]:
    """Reconstruct visual rows from words using spatial order.

    Words are sorted by (top, x0) and grouped into rows whose vertical
    positions fall within ``y_tol`` points; each row is ordered
    left-to-right. Used for the label:value metadata block on the
    Overall-Batch-Results page (labels and values sit in separate x
    columns that line up by row).
    """
    try:
        words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    except Exception:
        return [ln for ln in (page.extract_text() or '').split('\n')]
    words.sort(key=lambda w: (w['top'], w['x0']))
    rows: List[str] = []
    cur: List[dict] = []
    anchor: Optional[float] = None
    for w in words:
        if anchor is None or abs(w['top'] - anchor) <= y_tol:
            cur.append(w)
            if anchor is None:
                anchor = w['top']
        else:
            cur.sort(key=lambda x: x['x0'])
            rows.append(' '.join(x['text'] for x in cur))
            cur = [w]
            anchor = w['top']
    if cur:
        cur.sort(key=lambda x: x['x0'])
        rows.append(' '.join(x['text'] for x in cur))
    return rows


# ── Layout detection ───────────────────────────────────────────────

def _left_column_block(page, anchor_texts=('Customer', 'Customer:'),
                       x_pad: float = 6.0, x_max_frac: float = 0.42) -> List[str]:
    """Reconstruct the left-hand customer column below a 'Customer' anchor.

    Isolates words whose x0 sits left of the page's ~42% width and below
    the anchor row, so the interleaved Overall-Batch-Results grid and the
    right-hand label:value column don't pollute the customer name/address.
    """
    try:
        words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    except Exception:
        return []
    anchor = None
    for w in words:
        if w['text'] in anchor_texts or w['text'].rstrip(':') == 'Customer':
            anchor = w
            break
    if anchor is None:
        return []
    page_w = float(page.width or 612)
    x_cut = page_w * x_max_frac
    cy = anchor['top']
    col = [w for w in words if w['x0'] < x_cut and w['top'] >= cy - 1]
    col.sort(key=lambda w: (w['top'], w['x0']))
    rows, cur, top = [], [], None
    for w in col:
        if top is None or abs(w['top'] - top) <= 3.0:
            cur.append(w)
            top = w['top'] if top is None else top
        else:
            cur.sort(key=lambda x: x['x0'])
            rows.append(' '.join(x['text'] for x in cur))
            cur, top = [w], w['top']
    if cur:
        cur.sort(key=lambda x: x['x0'])
        rows.append(' '.join(x['text'] for x in cur))
    return rows


def _find_layout(pdf) -> Tuple[int, bool]:
    """Return (metadata_page_index, has_cover_profile).

    Full-panel (Buds/Flower) COAs lead with a CANNABINOID PROFILE cover
    page; the Overall Batch Results metadata block is on page 2.
    Biomass COAs have no cover page; the metadata block is on page 1.
    """
    p1 = pdf.pages[0].extract_text() or ''
    has_cover = 'CANNABINOID PROFILE' in p1
    meta_idx = 0
    for i, pg in enumerate(pdf.pages):
        t = pg.extract_text() or ''
        if 'Overall Batch Results' in t:
            meta_idx = i
            break
    return meta_idx, has_cover


# ── Metadata extraction ────────────────────────────────────────────

def _label_value(rows: List[str], label: str) -> Optional[str]:
    """Pull the value following an inline 'Label: value' or 'Label value'
    from the reconstructed metadata rows. Handles both the colon form on
    the OBR page ('Sample ID: 251119021') and the OBR-grid right column
    ('Sample Name: 1A4220...')."""
    pat_colon = re.compile(re.escape(label) + r':\s*(\S.*?)\s*$')
    for r in rows:
        m = pat_colon.search(r)
        if m:
            val = m.group(1).strip()
            # Strip a trailing time on date/COA lines handled elsewhere.
            return val
    return None


def _extract_external_sample_id(page) -> Optional[str]:
    """Extract the (possibly wrapped) External Sample ID from the cover
    page's right column.

    The value can span two rows, e.g.:
        External Sample ID  Emerald Fire 11.02.25
                            MB Auto
    with the left-column 'CULT...' interleaved by y-position. We isolate
    the right column (x0 >= the value's start) and collect rows from just
    below the 'External Sample ID' label down to (but excluding) the
    'Received Date' / 'Batch Number' row.
    """
    try:
        words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    except Exception:
        return None
    label_words = [w for w in words if w['text'] == 'External']
    if not label_words:
        return None
    lbl = label_words[0]
    ytop = lbl['top']
    # The value column starts to the right of the "External Sample ID"
    # label text. Find the x where the value begins (first word right of
    # "ID" on the label row).
    label_row = [w for w in words if abs(w['top'] - ytop) <= 3.0]
    label_row.sort(key=lambda w: w['x0'])
    # words on the label row after the token 'ID'
    val_x0 = None
    seen_id = False
    for w in label_row:
        if seen_id:
            val_x0 = w['x0']
            break
        if w['text'] == 'ID':
            seen_id = True
    if val_x0 is None:
        return None
    # Lower y-bound: the next right-column landmark below the label.
    stop_y = None
    for w in words:
        if w['x0'] >= val_x0 - 4 and w['top'] > ytop + 4:
            if w['text'] in ('Received', 'Batch', 'Collection', 'COA', 'Product'):
                if stop_y is None or w['top'] < stop_y:
                    stop_y = w['top']
    # Collect right-column words within [ytop, stop_y).
    band = [w for w in words
            if w['x0'] >= val_x0 - 4
            and ytop - 1 <= w['top'] < (stop_y if stop_y else ytop + 40)]
    # Drop the label tokens themselves.
    band = [w for w in band if w['text'] not in ('External', 'Sample', 'ID')]
    band.sort(key=lambda w: (w['top'], w['x0']))
    val = ' '.join(w['text'] for w in band).strip()
    return _clean_strain(val) or None


def _parse_metadata_block(meta_page, cover_page=None) -> Dict[str, Any]:
    """Parse metadata from the Overall-Batch-Results block and, for
    full-panel COAs, the CANNABINOID PROFILE cover page.

    Layout differences:
      * Biomass (no cover): everything is on the OBR page. Sample Name is
        the Metrc tag; there is no External Sample ID / strain.
      * Full-panel: the OBR page (page 2) carries Sample Name / Batch /
        dates, but the human-readable strain (External Sample ID) and the
        customer block live on the cover page (page 1). We read scalar
        fields from the OBR page and overlay strain + customer from the
        cover page.
    """
    obs: Dict[str, Any] = {}
    rows = _rows(meta_page)
    text = meta_page.extract_text() or ''

    def grab(label, source=rows):
        return _label_value(source, label)

    sample_id = grab('Sample ID')
    order_number = grab('Order Number')
    product_type = grab('Product Type')
    sample_type = grab('Sample Type')

    # Metrc-tag fields wrap across lines; repair from raw text.
    def repair_tag(label, src_text):
        m = re.search(re.escape(label) + r'[:\s]+([0-9A-Za-z].*?)(?:\n|$)', src_text)
        if not m:
            return None
        val = m.group(1).strip()
        if val.startswith('1A4') and len(val) < 24:
            after = src_text[m.end():m.end() + 40]
            nxt = re.match(r'\s*\n\s*(\d{1,3})\b', after)
            if nxt:
                val = val + nxt.group(1)
        return val

    sample_name = repair_tag('Sample Name', text) or grab('Sample Name')
    batch_number = repair_tag('Batch Number', text) or grab('Batch Number')

    # External Sample ID / strain + customer block:
    #   * full-panel -> from the cover page (right column, wrap-glued)
    #   * biomass    -> none (there is no External Sample ID)
    external_id = None
    if cover_page is not None:
        external_id = _extract_external_sample_id(cover_page)
        if not external_id:
            # Fallback: line-based from the cover text.
            ct = cover_page.extract_text() or ''
            mext = re.search(
                r'External Sample ID\s+(.+?)(?:\n(?:Batch|Comments|Product|CULT|Received|Collection|COA)|$)',
                ct, re.DOTALL)
            external_id = _clean_strain(mext.group(1).replace('\n', ' ')) if mext else None
    ext_source_text = (cover_page.extract_text() or '') if cover_page else text
    # On the cover, Sample Name is also present (and is the Metrc tag);
    # prefer the cover's repaired Sample Name if the OBR one is missing.
    if cover_page is not None:
        cov_sn = repair_tag('Sample Name', ext_source_text)
        if cov_sn and not sample_name:
            sample_name = cov_sn

    if sample_name:
        obs['sample_name'] = sample_name
    if external_id:
        obs['external_sample_id'] = external_id
    if sample_id:
        obs['sample_id'] = sample_id
    if order_number:
        obs['order_number'] = order_number
    if product_type:
        obs['product_type_raw'] = product_type
    if sample_type:
        obs['sample_type'] = sample_type
    if batch_number:
        obs['batch_number'] = batch_number

    # Metrc tag = the Sample Name (a 1A4... package tag).
    metrc = None
    for cand in (sample_name, batch_number):
        if cand and cand.startswith('1A4'):
            metrc = cand
            break
    if metrc:
        obs['metrc_ids'] = [metrc]
        obs['metrc_id'] = metrc

    # Dates (present on the OBR page in both layouts).
    obs['date_received'] = _first(r'Received Date:?\s*(\d{2}/\d{2}/\d{4})', text)
    obs['date_collected'] = _first(r'Collection Date:?\s*(\d{2}/\d{2}/\d{4})', text)
    obs['date_tested'] = _first(r'COA [Rr]eleased:?\s*(\d{2}/\d{2}/\d{4})', text)

    # Producer / customer block. For full-panel, the cleanest source is
    # the cover page's left column; for biomass, the OBR page's.
    cust_page = cover_page if cover_page is not None else meta_page
    prod_lic = _first(r'(CULT\d+)', cust_page.extract_text() or '')
    if prod_lic:
        obs['producer_license_number'] = prod_lic
    obs.update(_parse_customer_block(cust_page))

    _resolve_product_and_strain(obs)
    return obs


def _parse_customer_block(page) -> Dict[str, Any]:
    """Extract producer name / street / city-state-zip from the left-hand
    customer column using coordinate isolation (grid text excluded)."""
    obs: Dict[str, Any] = {}
    block = _left_column_block(page)
    text = page.extract_text() or ''

    name = None
    street = None
    for i, r in enumerate(block):
        rs = r.strip()
        # 'Customer' or 'Customer: <maybe name>' anchor row.
        m = re.match(r'^Customer:?\s*(.*)$', rs)
        if m is not None and i < 3:
            trailing = m.group(1).strip()
            # Name may be inline (rare) or on the next row.
            if trailing and not re.match(r'^(Sample|Overall)', trailing):
                name = trailing
            else:
                for j in range(i + 1, min(i + 4, len(block))):
                    nxt = block[j].strip()
                    if nxt and not re.match(r'^(Sample|Overall|PASS|FAIL)', nxt):
                        name = nxt
                        break
            break
    # Fallback: first LLC/Co line in the left column.
    if not name:
        for r in block:
            m = re.match(r'^([A-Z][A-Za-z0-9&.,\' ]+?(?:LLC|Inc\.?|Co\.?|Company|CannaCo))\b', r.strip())
            if m:
                name = m.group(1).strip()
                break
    if name:
        name = re.sub(r'\s+(PASS|FAIL)\b.*$', '', name).strip()
        obs['producer'] = name

    # Street + city/state/zip from the left column.
    for r in block:
        if street is None:
            ms = re.match(r'^(\d+\s+[A-Za-z0-9.\' ]+(?:STE|Suite|Ste|Dr|Drive|Road|Rd|St|Street|Ave|Avenue|Lane|Ln|Blvd)\.?\s*\w*)\b', r.strip())
            if ms:
                street = ms.group(1).strip()
                obs['producer_street'] = street
        csz = re.match(r'^([A-Za-z .]+),\s*([A-Z]{2})\s+(\d{5})\b', r.strip())
        if csz and '40509' not in r:  # exclude lab footer address
            obs['producer_city'] = csz.group(1).strip()
            obs['producer_state'] = csz.group(2)
            obs['producer_zipcode'] = csz.group(3)
    return obs


def _resolve_product_and_strain(obs: Dict[str, Any]) -> None:
    """Resolve product_type and strain_name.

    Strain rule: the strain is whichever of {Sample Name, External Sample
    ID} is NOT a Metrc tag. If both are tags / empty (pure biomass),
    strain_name is None -- never guessed.
    """
    # Product type: prefer explicit Sample Type (Buds/Biomass/Flower),
    # fall back to Product Type field. Normalize to lowercase.
    stype = (obs.get('sample_type') or '').strip()
    ptype = (obs.get('product_type_raw') or '').strip()
    chosen = stype or ptype
    if chosen:
        obs['product_type'] = chosen.lower()
    obs.setdefault('product_type', '')

    sample_name = obs.get('sample_name', '') or ''
    external_id = obs.get('external_sample_id', '') or ''

    strain = None
    # If Sample Name is NOT a Metrc tag, it is the strain.
    if sample_name and not sample_name.startswith('1A4'):
        strain = sample_name
    # Else if External Sample ID is present and not a tag, it is the strain.
    elif external_id and not external_id.startswith('1A4'):
        strain = external_id
    if strain:
        obs['strain_name'] = _clean_strain(strain)
        # Product name mirrors the strain (COA prints no separate product).
        obs.setdefault('product_name', obs['strain_name'])
    else:
        # Pure biomass / tag-only: no human-readable strain.
        obs['strain_name'] = None


def _first(pattern: str, text: str, flags=0) -> str:
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ''


# ── Cover-page cannabinoid profile (Layout A) ──────────────────────

def _parse_cover_cannabinoids(page) -> Tuple[List[Dict], Dict[str, Any]]:
    """Parse the CANNABINOID PROFILE cover table (full-panel COAs).

    NOTE: this cover table is used only as a source of the printed
    Total Potential THC/CBD/CBG summary and ratios; the per-analyte
    cannabinoid *records* are taken from the clean "Potency - Flower"
    detail section (present in both layouts). The cover table's analyte
    order can render scrambled, so we read only the labeled Total rows
    and ratios here via line text.
    """
    totals: Dict[str, Any] = {}
    text = page.extract_text() or ''
    # Labeled totals: "Total Potential THC 26.20 262.0"
    for label, key in (('Total Cannabinoids', 'total_cannabinoids'),
                       ('Total Potential THC', 'total_thc'),
                       ('Total Potential CBD', 'total_cbd'),
                       ('Total Potential CBG', 'total_cbg')):
        m = re.search(re.escape(label) + r'\s+(ND|<LOQ|[\d.]+)\s+([\d.]+)', text)
        if m:
            totals[key] = _num(m.group(1))
    # Ratios: "Ratio of Total Potential CBD to Total Potential THC 0.00 :1"
    mcbd = re.search(r'Ratio of Total Potential CBD to Total Potential THC\s+([\d.]+)\s*:\s*1', text)
    if mcbd:
        totals['cbd_thc_ratio'] = _num(mcbd.group(1))
    mcbg = re.search(r'Ratio of Total Potential CBG to Total Potential THC\s+([\d.]+)\s*:\s*1', text)
    if mcbg:
        totals['cbg_thc_ratio'] = _num(mcbg.group(1))
    return [], totals


# ── Detail-section parsers (line-based; sections tracked globally) ──

def _iter_section_lines(pdf, meta_idx: int) -> List[Tuple[str, str]]:
    """Yield (section, line) for every content line across the COA.

    A section header line begins a section that continues until the next
    header. The metadata/cover pages contribute nothing (their lines
    precede the first 'Potency - Flower' header). Footer / boilerplate
    lines are dropped.
    """
    out: List[Tuple[str, str]] = []
    section = None
    footer_markers = ('M of U =', 'This product has been tested',
                      'safety, or other risks', 'of sample received by the lab',
                      'Page', '2554 PALUMBO', 'CANNABUSINESS LABORATORIES, LLC',
                      'Certificate of Analysis')
    # A line carrying a measurement token / verdict is a DATA row, never a
    # section header -- this matters where an analyte shares the section
    # name (e.g. the "Water Activity 0.462 Aw ... Pass" row sits directly
    # under the "Water Activity" header and must not be mistaken for it).
    data_row_re = re.compile(r'\b(Aw|ppm|CFUs?|ug/kg|mg/g)\b|\d\s*%|\b(Pass|Fail)\b')

    for pg in pdf.pages:
        text = pg.extract_text() or ''
        for raw in text.split('\n'):
            line = raw.rstrip()
            s = line.strip()
            if not s:
                continue
            # Section header? (only if the line isn't itself a data row)
            hdr = None
            if not data_row_re.search(s):
                for h, sec in SECTION_HEADERS.items():
                    if s == h or s.startswith(h + ' '):
                        hdr = sec
                        break
            if hdr is not None:
                section = hdr
                continue
            # Skip obvious non-data lines.
            if any(s.startswith(fm) or fm in s for fm in footer_markers):
                continue
            if s.startswith('Date Tested') or s.startswith('Analyte '):
                continue
            if section is None:
                continue
            out.append((section, s))
    return out


def _parse_cannabinoid_detail(lines: List[str]) -> Tuple[List[Dict], Dict[str, Any]]:
    """Parse the Potency - Flower cannabinoid detail rows into single
    records collapsing the %/mg-g pair.

    Row shapes:
        CBC (Cannabichromene) ND % 0.010 0.005
        CBC (Cannabichromene) mg/g ND mg/g 0.100 0.05
        D9-THC (D9-Tetrahydrocannabinol) 0.231 % 0.010 0.005 35 Pass
        THCa (Tetrahydrocannabinolic Acid) 29.61 % 0.010 0.005
        Percent Moisture 9 % 1.000 1
    """
    pct: Dict[str, Dict] = {}
    mgg: Dict[str, float] = {}
    moisture = None
    order: List[str] = []

    # % row: "<name> <result> % <loq> <lod> [limit] [Pass/Fail]"
    pct_re = re.compile(
        r'^(?P<name>.+?)\s+(?P<result>ND|<LOQ|>ULOL|[\d.]+)\s+%\s+'
        r'(?P<loq>[\d.]+)\s+(?P<lod>[\d.]+)'
        r'(?:\s+(?P<limit>[\d.]+))?(?:\s+(?P<pf>Pass|Fail))?\s*$')
    # mg/g row: "<name> mg/g <result> mg/g <loq> <lod>"
    mgg_re = re.compile(
        r'^(?P<name>.+?)\s+mg/g\s+(?P<result>ND|<LOQ|>ULOL|[\d.]+)\s+mg/g\s+'
        r'[\d.]+\s+[\d.]+\s*$')
    # Moisture line: "Percent Moisture 9 % 1.000 1" (and CB-SOP variant)
    moist_re = re.compile(r'^Percent Moisture.*?\s+(\d+(?:\.\d+)?)\s+%')

    for s in lines:
        mm = moist_re.match(s)
        if mm:
            moisture = _num(mm.group(1))
            continue
        g = mgg_re.match(s)
        if g:
            code_m = CANN_DETAIL_CODE_RE.match(g.group('name').strip())
            code = code_m.group(1) if code_m else g.group('name').strip()
            mgg[code] = _num(g.group('result'))
            continue
        p = pct_re.match(s)
        if p:
            name = p.group('name').strip()
            if name.lower().startswith(('percent moisture', 'analyte')):
                continue
            code_m = CANN_DETAIL_CODE_RE.match(name)
            code = code_m.group(1) if code_m else name
            if code not in pct:
                order.append(code)
            pct[code] = {
                'analysis': 'cannabinoids',
                'key': _key_for(code),
                'name': name,
                'value': _num(p.group('result')),
                'units': 'percent',
                'loq': _num(p.group('loq')),
                'lod': _num(p.group('lod')),
                'status': p.group('pf'),
                'result_raw': _raw_token(p.group('result')),
            }

    results: List[Dict] = []
    for code in order:
        rec = pct[code]
        rec['value_mg_g'] = mgg.get(code)
        results.append(rec)
    extra = {'moisture': moisture} if moisture is not None else {}
    return results, extra


def _parse_terpenes_detail(lines: List[str]) -> Tuple[List[Dict], Optional[float]]:
    """Parse Terpenoids rows, collapsing %/mg-g pairs. Returns
    (results, total_terpenes_percent)."""
    pct: Dict[str, Dict] = {}
    mgg: Dict[str, float] = {}
    order: List[str] = []
    total = None

    total_re = re.compile(r'^Total Terpenes \(%\)\s+([\d.]+)')
    # mg/g row: "<name> (mg/g) <result> mg/g <loq> <lod>"
    mgg_re = re.compile(
        r'^(?P<name>.+?)\s*\(mg/g\)\s+(?P<result>ND|<LOQ|>ULOL|[\d.]+)\s+mg/g\s+'
        r'[\d.]+\s+[\d.]+\s*$')
    # % row: "<name> <result> % <loq> <lod>"
    pct_re = re.compile(
        r'^(?P<name>.+?)\s+(?P<result>ND|<LOQ|>ULOL|[\d.]+)\s+%\s+'
        r'[\d.]+\s+[\d.]+\s*$')

    for s in lines:
        mt = total_re.match(s)
        if mt:
            total = _num(mt.group(1))
            continue
        if s.startswith('Total Terpenes'):
            continue
        g = mgg_re.match(s)
        if g:
            name = g.group('name').strip()
            mgg[name] = _num(g.group('result'))
            continue
        p = pct_re.match(s)
        if p:
            name = p.group('name').strip()
            if name not in pct:
                order.append(name)
            pct[name] = {
                'analysis': 'terpenes',
                'key': _key_for(name),
                'name': name,
                'value': _num(p.group('result')),
                'units': 'percent',
                'result_raw': _raw_token(p.group('result')),
            }

    results: List[Dict] = []
    for name in order:
        rec = pct[name]
        rec['value_mg_g'] = mgg.get(name)
        results.append(rec)
    return results, total


def _parse_ppm_table(lines: List[str], analysis: str) -> List[Dict]:
    """Parse a ppm Pass/Fail table (metals, pesticides APCI/ESI).

    Row shapes:
        Arsenic ND ppm 0.200 0.125 0.2 Pass
        Acequinocyl ND ppm 0.100 0.1 2.0 Pass
        Captan NT ppm 0.100 0.1
        MGK-264 (20.1) ND ppm 0.040 0.0402
        AbamectinB1a ND ppm 0.009 0.0094 0.5 Pass
    """
    results: List[Dict] = []
    seen = set()
    row_re = re.compile(
        r'^(?P<name>.+?)\s+(?P<result>ND|NT|<LOQ|>ULOL|[\d.]+)\s+ppm\s+'
        r'(?P<loq>[\d.]+)\s+(?P<lod>[\d.]+)'
        r'(?:\s+(?P<limit>[\d.]+))?(?:\s+(?P<pf>Pass|Fail))?\s*$')
    for s in lines:
        m = row_re.match(s)
        if not m:
            continue
        name = m.group('name').strip()
        if name.lower() in ('analyte', 'result') or len(name) < 2:
            continue
        key = _key_for(name)
        dedup = (analysis, key, name)
        if dedup in seen:
            continue
        seen.add(dedup)
        results.append({
            'analysis': analysis,
            'key': key,
            'name': name,
            'value': _num(m.group('result')),
            'units': 'ppm',
            'loq': _num(m.group('loq')),
            'lod': _num(m.group('lod')),
            'limit': _num(m.group('limit')) if m.group('limit') else None,
            'status': m.group('pf'),
            'result_raw': _raw_token(m.group('result')),
        })
    return results


def _parse_mycotoxins_detail(lines: List[str]) -> List[Dict]:
    """Parse Mycotoxins rows (ug/kg)."""
    results: List[Dict] = []
    row_re = re.compile(
        r'^(?P<name>Aflatoxin [BG][12]|Total Aflatoxins|Ochratoxin-M\+H)\s+'
        r'(?P<result>ND|NT|<LOQ|[\d.]+)\s+ug/kg\s+[\d.]+\s+[\d.]+'
        r'(?:\s+[\d.]+)?(?:\s+(?P<pf>Pass|Fail))?\s*$')
    for s in lines:
        m = row_re.match(s)
        if not m:
            continue
        name = m.group('name').strip()
        results.append({
            'analysis': 'mycotoxins',
            'key': _key_for(name),
            'name': name,
            'value': _num(m.group('result')),
            'units': 'ug/kg',
            'status': m.group('pf'),
            'result_raw': _raw_token(m.group('result')),
        })
    return results


def _parse_microbials_detail(lines: List[str]) -> List[Dict]:
    """Parse Microbial - Flower rows (mixed quantitative CFU + qualitative
    Negative/Positive). CannaBusiness reports Aspergillus via qPCR
    (Negative/Positive), E.coli and Yeast/Mold quantitatively, and
    Listeria/Salmonella/STEC qualitatively."""
    results: List[Dict] = []
    seen = set()

    # Quantitative: "E.coli by Plating 0 CFUs 0 100 Pass" /
    #               "Total Yeast and Mold 2759 CFUs 0 0 10000 Pass"
    quant_re = re.compile(
        r'^(?P<name>E\.coli by Plating|Total Yeast and Mold)\s+'
        r'(?P<result>ND|[\d.]+)\s+CFUs?\s+[\d.\s]*?'
        r'(?:(?P<limit>\d+)\s+)?(?P<pf>Pass|Fail)\s*$')
    # Qualitative w/ limits+status: "Salmonella spp. Negative Positive Pass"
    qual_pf_re = re.compile(
        r'^(?P<name>.+?)\s+(?P<result>Negative|Positive|Detected|Not Detected)\s+'
        r'(?P<limit>Positive|Negative)\s+(?P<pf>Pass|Fail)\s*$')
    # Qualitative bare: "Listeria monocytogenes Negative"
    qual_bare_re = re.compile(
        r'^(?P<name>Listeria monocytogenes|Listeria spp\.)\s+'
        r'(?P<result>Negative|Positive)\s*$')
    # Aspergillus qPCR (from Potency page grouping): handled if present.
    asp_re = re.compile(
        r'^Aspergillus spp\.\s+(?P<result>Negative|Positive)\s+'
        r'(?P<limit>Positive|Negative)\s+(?P<pf>Pass|Fail)\s*$')

    def add(name, value=None, status=None, qualitative=None, raw=None, units='CFU/g'):
        key = _key_for(name)
        if (key, name) in seen:
            return
        seen.add((key, name))
        # For qualitative pathogen rows the COA may not print an explicit
        # Pass/Fail column (bare "Negative"/"Positive"). Derive it: a
        # non-detect is unambiguously a pass; a detected pathogen is
        # unambiguously a fail under every state's microbial spec. This
        # keeps the per-analyte rollup (agg_results) complete and matches
        # KCA's handling -- without fabricating a verdict for quantitative
        # rows, whose status is read from the COA directly.
        if status is None and qualitative is not None:
            status = 'Fail' if qualitative == 'Detected' else 'Pass'
        results.append({
            'analysis': 'microbials', 'key': key, 'name': name,
            'value': value, 'units': units, 'status': status,
            'qualitative': qualitative, 'result_raw': raw,
        })

    for s in lines:
        mq = quant_re.match(s)
        if mq:
            add(mq.group('name'), value=_num(mq.group('result')),
                status=mq.group('pf'), raw=_raw_token(mq.group('result')))
            continue
        ma = asp_re.match(s)
        if ma:
            qual = 'Detected' if ma.group('result') == 'Positive' else 'Not Detected'
            add('Aspergillus spp.', status=ma.group('pf'),
                qualitative=qual, raw=ma.group('result'), units='qualitative')
            continue
        mp = qual_pf_re.match(s)
        if mp:
            res = mp.group('result')
            qual = 'Detected' if res in ('Positive', 'Detected') else 'Not Detected'
            add(mp.group('name'), status=mp.group('pf'),
                qualitative=qual, raw=res, units='qualitative')
            continue
        mb = qual_bare_re.match(s)
        if mb:
            res = mb.group('result')
            qual = 'Detected' if res == 'Positive' else 'Not Detected'
            add(mb.group('name'), qualitative=qual, raw=res, units='qualitative')
            continue
    return results


def _parse_water_activity_detail(lines: List[str]) -> Optional[Dict]:
    """Water Activity: 'Water Activity 0.462 Aw 0.150 0.150 0.650 Pass'."""
    row_re = re.compile(
        r'^Water Activity\s+(?P<result>[\d.]+)\s+Aw\s+'
        r'(?P<loq>[\d.]+)\s+(?P<lod>[\d.]+)\s+(?P<limit>[\d.]+)\s+'
        r'(?P<pf>Pass|Fail)\s*$')
    for s in lines:
        m = row_re.match(s)
        if m:
            return {
                'analysis': 'water_activity',
                'key': 'water_activity', 'name': 'Water Activity',
                'value': _num(m.group('result')), 'units': 'aw',
                'loq': _num(m.group('loq')), 'lod': _num(m.group('lod')),
                'limit': _num(m.group('limit')), 'status': m.group('pf'),
                'result_raw': m.group('result'),
            }
    return None


# ── Overall status (from the Overall Batch Results grid) ───────────

def _parse_overall_status(page) -> str:
    """Read the Overall Batch Results grid -> 'pass' / 'fail'.

    The grid prints an overall 'PASS'/'FAIL' under the header plus a
    per-panel PASS/FAIL matrix. Any FAIL anywhere -> fail.
    """
    text = page.extract_text() or ''
    # Isolate the grid region (between the header and the first detail
    # section) to avoid catching unrelated tokens.
    region = text
    mstart = text.find('Overall Batch Results')
    if mstart != -1:
        mend = text.find('Potency', mstart)
        region = text[mstart:mend] if mend != -1 else text[mstart:]
    if re.search(r'\bFAIL\b', region):
        return 'fail'
    if re.search(r'\bPASS\b', region):
        return 'pass'
    return 'pass'


# ── Total computation (decarboxylation fallback) ───────────────────

def _result_value(results: List[Dict], key: str) -> Optional[float]:
    for r in results:
        if r.get('analysis') == 'cannabinoids' and r.get('key') == key:
            return r.get('value')
    return None


def _compute_total_thc(results: List[Dict]) -> Optional[float]:
    """Total Potential THC = 0.877 * THCa + d9-THC (lab's printed formula).
    Returns None if neither component is quantified."""
    thca = _result_value(results, 'thca')
    d9 = _result_value(results, 'delta_9_thc')
    if thca is None and d9 is None:
        return None
    return round(0.877 * (thca or 0.0) + (d9 or 0.0), 4)


def _compute_total_cbd(results: List[Dict]) -> Optional[float]:
    cbda = _result_value(results, 'cbda')
    cbd = _result_value(results, 'cbd')
    if cbda is None and cbd is None:
        return None
    return round(0.877 * (cbda or 0.0) + (cbd or 0.0), 4)


def _compute_total_cbg(results: List[Dict]) -> Optional[float]:
    cbga = _result_value(results, 'cbga')
    cbg = _result_value(results, 'cbg')
    if cbga is None and cbg is None:
        return None
    return round(0.877 * (cbga or 0.0) + (cbg or 0.0), 4)


def _compute_total_cannabinoids(results: List[Dict]) -> Optional[float]:
    """Sum of all detected cannabinoid % values (fallback when the cover
    total is absent, i.e. biomass)."""
    vals = [r['value'] for r in results
            if r.get('analysis') == 'cannabinoids'
            and not r.get('key', '').startswith('total_')
            and isinstance(r.get('value'), (int, float))]
    if not vals:
        return None
    return round(sum(vals), 4)


# ── Main parse ─────────────────────────────────────────────────────

def parse_cannabusiness_pdf(parser: Any, doc: str, **kwargs) -> Dict:
    """Parse a CannaBusiness Laboratories COA PDF into the flat record."""
    pdf_path = doc
    obs: Dict[str, Any] = dict(CANNABUSINESS_LAB)
    all_results: List[Dict] = []
    analyses: List[str] = []

    with pdfplumber.open(pdf_path) as pdf:
        meta_idx, has_cover = _find_layout(pdf)
        meta_page = pdf.pages[meta_idx]

        # ── Metadata (both layouts) ───────────────────────────
        cover_page = pdf.pages[0] if has_cover else None
        obs.update(_parse_metadata_block(meta_page, cover_page))
        obs['coa_layout'] = 'full' if has_cover else 'biomass'
        obs['status'] = _parse_overall_status(meta_page)

        # ── Cover-page totals (full-panel only) ───────────────
        cover_totals: Dict[str, Any] = {}
        if has_cover:
            _, cover_totals = _parse_cover_cannabinoids(pdf.pages[0])

        # ── Detail sections (line-based, tracked over document) ─
        section_lines: Dict[str, List[str]] = {}
        for section, line in _iter_section_lines(pdf, meta_idx):
            section_lines.setdefault(section, []).append(line)

        # Cannabinoids (from the clean Potency - Flower detail section).
        pot_lines = section_lines.get('potency', [])
        cann_results, pot_extra = _parse_cannabinoid_detail(pot_lines)
        if cann_results:
            all_results.extend(cann_results)
            analyses.append('cannabinoids')
        # Moisture: emit as a RESULT ROW (key 'moisture_content') as well as
        # a scalar. The pipeline's parse cache keeps only the canonical
        # top-level columns plus the results array, and agg_results promotes
        # moisture_content from a result row -- a top-level scalar alone
        # would be dropped. (Mirrors kaycha/kca handling.)
        if pot_extra.get('moisture') is not None:
            obs['moisture'] = pot_extra['moisture']
            obs['moisture_content'] = pot_extra['moisture']
            all_results.append({
                'analysis': 'moisture',
                'key': 'moisture_content',
                'name': 'Moisture Content',
                'value': pot_extra['moisture'],
                'units': 'percent',
                'result_raw': str(pot_extra['moisture']),
            })
            analyses.append('moisture')

        # Terpenoids.
        terp_lines = section_lines.get('terpenes', [])
        if terp_lines:
            terps, total_terp = _parse_terpenes_detail(terp_lines)
            if terps:
                all_results.extend(terps)
                analyses.append('terpenes')
                if total_terp is not None:
                    obs['total_terpenes'] = total_terp

        # Metals.
        metal_lines = section_lines.get('metals', [])
        if metal_lines:
            metals = _parse_ppm_table(metal_lines, 'heavy_metals')
            if metals:
                all_results.extend(metals)
                analyses.append('heavy_metals')

        # Pesticides (APCI + ESI merged into one analysis).
        pest_lines = section_lines.get('pesticides', [])
        if pest_lines:
            pests = _parse_ppm_table(pest_lines, 'pesticides')
            if pests:
                all_results.extend(pests)
                analyses.append('pesticides')

        # Mycotoxins.
        myco_lines = section_lines.get('mycotoxins', [])
        if myco_lines:
            myco = _parse_mycotoxins_detail(myco_lines)
            if myco:
                all_results.extend(myco)
                analyses.append('mycotoxins')

        # Microbials.
        micro_lines = section_lines.get('microbials', [])
        if micro_lines:
            micro = _parse_microbials_detail(micro_lines)
            if micro:
                all_results.extend(micro)
                analyses.append('microbials')

        # Water activity.
        wa_lines = section_lines.get('water_activity', [])
        if wa_lines:
            wa = _parse_water_activity_detail(wa_lines)
            if wa:
                all_results.append(wa)
                analyses.append('water_activity')
                if wa.get('value') is not None:
                    obs['water_activity'] = wa['value']

    # ── Totals: cover page authoritative; else decarb fallback ─
    # Full-panel COAs print Total Potential THC/CBD/CBG on the cover.
    # Biomass COAs do not -> compute from the acid+neutral forms with the
    # lab's own 0.877 decarb factor (Keegan's call), else null.
    total_thc = cover_totals.get('total_thc')
    if total_thc is None:
        total_thc = _compute_total_thc(all_results)
    obs['total_thc'] = total_thc

    total_cbd = cover_totals.get('total_cbd')
    if total_cbd is None:
        total_cbd = _compute_total_cbd(all_results)
    obs['total_cbd'] = total_cbd

    total_cbg = cover_totals.get('total_cbg')
    if total_cbg is None:
        total_cbg = _compute_total_cbg(all_results)
    obs['total_cbg'] = total_cbg

    total_cann = cover_totals.get('total_cannabinoids')
    if total_cann is None:
        total_cann = _compute_total_cannabinoids(all_results)
    obs['total_cannabinoids'] = total_cann

    if cover_totals.get('cbd_thc_ratio') is not None:
        obs['cbd_thc_ratio'] = cover_totals['cbd_thc_ratio']
    if cover_totals.get('cbg_thc_ratio') is not None:
        obs['cbg_thc_ratio'] = cover_totals['cbg_thc_ratio']

    # ── Serialize + provenance ────────────────────────────────
    analyses = sorted(set(analyses))
    obs['analyses'] = json.dumps(analyses)
    obs['results'] = json.dumps(all_results, default=str)
    obs['coa_parsed_at'] = datetime.now().isoformat()

    hash_input = json.dumps(all_results, sort_keys=True, default=str)
    obs['results_hash'] = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    obs['lab_id'] = obs.get('sample_id', '')
    if pdf_path:
        obs['coa_pdf'] = str(pdf_path).replace('\\', '/').split('/')[-1]

    return obs


# ── Entry point (LAB_REGISTRY compatible) ──────────────────────────

def parse_cannabusiness_coa(parser: Any = None, doc: str = '', **kwargs) -> Dict:
    """Parse a CannaBusiness Laboratories COA PDF.

    Registered entry point satisfying the algorithm contract
    ``parse_{lab}_coa(parser, doc)``. The pipeline calls this as
    ``parse_cannabusiness_coa(None, file_path)``.

    Args:
        parser: Optional CoADoc instance (unused; kept for compatibility).
        doc:    Path to the COA PDF file.

    Returns:
        Flat dict with all extracted COA data; ``results`` and
        ``analyses`` are JSON strings.
    """
    if isinstance(parser, str) and not doc:
        doc, parser = parser, None
    if isinstance(doc, str) and doc.startswith('http'):
        raise ValueError(
            'URL parsing requires network access. Provide the PDF file path.'
        )
    return parse_cannabusiness_pdf(parser, doc, **kwargs)


def is_cannabusiness(pdf_path: str) -> bool:
    """Quick check whether a PDF is a CannaBusiness Laboratories COA."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return False
            t = (pdf.pages[0].extract_text() or '').lower()
            return ('cannabusinesslabs.us' in t
                    or 'cannabusiness laboratories' in t
                    or 'p_0059' in t)
    except Exception:
        return False


# ── CLI / smoke test ───────────────────────────────────────────────

if __name__ == '__main__':
    import sys
    from collections import Counter

    files = sys.argv[1:]
    if not files:
        here = os.path.dirname(os.path.abspath(__file__))
        files = [os.path.join(here, f) for f in os.listdir(here)
                 if f.lower().endswith('.pdf')]
    ok = fail = 0
    for fp in files:
        if not os.path.exists(fp):
            print(f'Not found: {fp}')
            continue
        try:
            data = parse_cannabusiness_coa(None, fp)
            results = json.loads(data.get('results', '[]'))
            analyses = json.loads(data.get('analyses', '[]'))
            print(f'\n{"=" * 64}')
            print(f'OK {os.path.basename(fp)}  [{data.get("coa_layout")}]')
            print(f'  Product : {data.get("product_name")!r}  '
                  f'(strain={data.get("strain_name")!r})')
            print(f'  Type    : {data.get("product_type")!r}  '
                  f'sample_type={data.get("sample_type")!r}')
            print(f'  Producer: {data.get("producer")!r}  '
                  f'lic={data.get("producer_license_number")!r}')
            print(f'  Sample  : {data.get("sample_id")!r}  '
                  f'batch={data.get("batch_number")!r}')
            print(f'  Metrc   : {data.get("metrc_id")!r}')
            print(f'  SampleNm: {data.get("sample_name")!r}  '
                  f'ExtID={data.get("external_sample_id")!r}')
            print(f'  Dates   : coll={data.get("date_collected")} '
                  f'recv={data.get("date_received")} test={data.get("date_tested")}')
            print(f'  THC     : {data.get("total_thc")}   '
                  f'CBD: {data.get("total_cbd")}   CBG: {data.get("total_cbg")}   '
                  f'Total: {data.get("total_cannabinoids")}')
            print(f'  Terps   : {data.get("total_terpenes")}   '
                  f'Moisture: {data.get("moisture")}')
            print(f'  Status  : {data.get("status")}')
            print(f'  Analyses: {analyses}')
            print(f'  Results : {len(results)} analytes')
            counts = Counter(r.get('analysis') for r in results)
            for a, c in sorted(counts.items()):
                print(f'      {a}: {c}')
            ok += 1
        except Exception as e:
            import traceback
            print(f'\nFAIL {os.path.basename(fp)}: {e}')
            traceback.print_exc()
            fail += 1
    print(f'\n{"=" * 64}\nResults: {ok} OK, {fail} FAIL of {ok + fail}')