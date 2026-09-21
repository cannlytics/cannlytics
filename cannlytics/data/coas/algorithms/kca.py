"""
Parse KCA Laboratories COA -- COA Doc Hybrid Algorithm (Offline-First)
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Dr. Jack Doobie, CSO (algorithm design)
Created: 7/12/2026
Updated: 7/12/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse KCA Laboratories COA PDFs directly from the PDF text -- no
    network access required. KCA Laboratories (KCA Labs, KDA Lic. P_0058)
    is one of two safety-compliance facilities serving Kentucky's medical
    cannabis program (the other being CannaBusiness Laboratories).

    Identification:
        KCA COAs contain 'kcalabs.com' and 'KCA Laboratories' on page 1,
        and the distinctive license string 'P_0058'.

    Format (observed, 2025 medical corpus -- 10 pages):
        * Page 1 : Metadata block, page-1 Summary table (test/date/status),
                   five-cell summary strip (Total D9-THC, Total CBD,
                   D9-THCA, Total Cannabinoids, Moisture), and the
                   Cannabinoids-by-HPLC table.
        * Page 2 : Terpenes by GCMS (single column, percent).
        * Page 3 : Heavy Metals by ICPMS (ppm, Pass/Fail).
        * Page 4 : Pesticides by LCMS & GCMS -- TWO-COLUMN layout.
        * Page 5 : Mycotoxins by LCMS (ug/kg).
        * Page 6 : Microbials by Plating & PCR (mixed quantitative /
                   qualitative "Detected per 1 gram" rows).
        * Page 7 : Vitamin E Acetate (percent, Pass/Fail).
        * Page 8 : Moisture Content (bare percent value).
        * Page 9 : Water Activity (Aw, Pass/Fail).
        * Page 10: Reporting Limit Appendix (reference limits -- NOT
                   sample results; ignored for extraction).

    CRITICAL parsing notes (validated against the sample batch):
        1. SCRAMBLED TEXT LAYER is stream-order-only. Some KCA PDFs
           (e.g. the ...081 sample) place cannabinoid values at the tail
           of the raw character stream. pdfplumber's DEFAULT extraction
           (sorted by top, then x0) resolves this; we therefore NEVER use
           use_text_flow=True. The cannabinoid table is additionally
           parsed via explicit y-band row reconstruction for robustness.
        2. SAMPLE-ID REUSE: KCA reuses Sample IDs across physically
           distinct samples (both sample COAs share SA-251119-72867 but
           carry different Metrc tags / batches). Deduplication MUST be by
           pdf_hash (SHA-256), never by sample_id. This parser reports the
           Sample ID as-is; the pipeline dedups by hash.
        3. NULL vs ZERO: ND / <LOQ / NT / UA serialize as ``None``, never
           0.0. Totals not printed are computed from the acid+neutral
           forms with the 0.877 decarboxylation factor, else ``None``.
        4. FAILING RESULTS ARE PRESERVED (never filtered). The overall
           status is Fail if any analysis failed.

Data Points:
    * product_name, product_type, strain_name, matrix
    * date_tested (Completed), date_received, date_collected
    * batch_number, sample_id (lab_id), metrc_ids
    * lab, lab_license_number, lab_address, lab_city, lab_state,
      lab_zipcode, lab_phone
    * producer, producer_license_number, producer_street, producer_city,
      producer_state, producer_zipcode
    * total_thc, total_cbd, total_cannabinoids, total_terpenes, moisture
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


# ── KCA Laboratories constants ─────────────────────────────────────

KCA_LAB = {
    'coa_algorithm': 'kca.py',
    'coa_algorithm_entry_point': 'parse_kca_coa',
    'lab': 'KCA Laboratories',
    'lab_license_number': 'P_0058',            # KDA testing license
    'lab_med_license_number': 'TEST0001057',   # Medical cannabis license
    'lab_address': '232 North Plaza Drive, Nicholasville, KY 40356',
    'lab_street': '232 North Plaza Drive',
    'lab_city': 'Nicholasville',
    'lab_state': 'KY',
    'lab_zipcode': '40356',
    'lab_phone': '+1-833-KCA-LABS',
    'lab_website': 'https://kcalabs.com',
    'lab_accreditation': 'ISO/IEC 17025:2017 (PJLA #108651)',
}

# Result tokens that must serialize as null (never 0.0).
NULL_TOKENS = {'ND', 'NT', 'UA', 'NR', 'N/A', 'NA', '-', '--', '\u2014'}
BELOW_LOQ_TOKENS = {'<LOQ', '<loq'}
ABOVE_TOKENS = {'>ULOL', '>uloL', '>ULOL'}

# Analyte display name -> standardized snake_case key.
ANALYTE_KEY_MAP = {
    # Cannabinoids
    'Total THC': 'total_thc', 'Total CBD': 'total_cbd',
    'Total Cannabinoids': 'total_cannabinoids',
    'THCa': 'thca', 'THCA': 'thca',
    'Delta-9-THC': 'delta_9_thc', 'Delta-8-THC': 'delta_8_thc',
    'CBDA': 'cbda', 'CBD': 'cbd', 'CBN': 'cbn',
    'CBGa': 'cbga', 'CBG': 'cbg', 'THCV': 'thcv', 'CBC': 'cbc',
    'CBDV': 'cbdv',
    # Terpenes (Greek prefixes normalized)
    '\u03b1-Bisabolol': 'alpha_bisabolol', '(+)-Borneol': 'borneol',
    'Camphene': 'camphene', '\u03b2-Caryophyllene': 'beta_caryophyllene',
    'Caryophyllene Oxide': 'caryophyllene_oxide',
    'Eucalyptol': 'eucalyptol', '\u03b1-Humulene': 'alpha_humulene',
    'Limonene': 'limonene', 'Linalool': 'linalool',
    '\u03b2-Myrcene': 'beta_myrcene', 'trans-Nerolidol': 'trans_nerolidol',
    '\u03b1-Pinene': 'alpha_pinene', '\u03b2-Pinene': 'beta_pinene',
    '\u03b1-Terpineol': 'alpha_terpineol', 'Geraniol': 'geraniol',
    # Heavy metals
    'Arsenic': 'arsenic', 'Cadmium': 'cadmium',
    'Lead': 'lead', 'Mercury': 'mercury',
    # Mycotoxins
    'Aflatoxins (Total)': 'total_aflatoxins', 'Aflatoxin B1': 'aflatoxin_b1',
    'Aflatoxin B2': 'aflatoxin_b2', 'Aflatoxin G1': 'aflatoxin_g1',
    'Aflatoxin G2': 'aflatoxin_g2', 'Ochratoxin A': 'ochratoxin_a',
    # Microbials
    'Total Escherichia coli': 'total_ecoli',
    'Shiga-toxin producing Escherichia coli': 'stec',
    'Salmonella species': 'salmonella',
    'Pathogenic Aspergillus sp.': 'pathogenic_aspergillus',
    'Yeast and Mold': 'yeast_and_mold',
    # Other
    'Vitamin E Acetate': 'vitamin_e_acetate',
    'Water Activity': 'water_activity', 'Moisture': 'moisture',
}

# Page-1 Summary-table test name -> analysis name it corroborates.
SUMMARY_TEST_TO_ANALYSIS = {
    'Cannabinoids': 'cannabinoids',
    'Terpenoids': 'terpenes',
    'Residual Solvents': 'residual_solvents',
    'Residual Pesticides': 'pesticides',
    'Heavy Metals': 'heavy_metals',
    'Microbial Impurities': 'microbials',
    'Mycotoxins': 'mycotoxins',
    'Water Activity': 'water_activity',
    'Yeast and Molds': 'microbials',
    'Vitamin E Acetate': 'vitamin_e_acetate',
}


# ── Value / token helpers ──────────────────────────────────────────

def _snake(name: str) -> str:
    """Fallback snake_case for analyte names not in the key map."""
    s = name.strip().lower()
    s = s.replace('\u03b1', 'alpha_').replace('\u03b2', 'beta_')
    s = s.replace('\u03b3', 'gamma_').replace('\u0394', 'delta_')
    s = re.sub(r'\([^)]*\)', '', s)          # drop parentheticals
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')


def _key_for(name: str) -> str:
    return ANALYTE_KEY_MAP.get(name, _snake(name))


def _num(token: str) -> Optional[float]:
    """Parse a numeric token to float, or None for ND/<LOQ/NT/etc.

    Enforces the null-vs-zero doctrine: non-detects and untested values
    return None, never 0.0. A literal printed 0 is returned as 0.0 only
    when it is a genuine number token (callers decide whether to trust
    it -- totals prefer the summary strip).
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


def _raw_token(token: str) -> str:
    """Normalize the raw result token for provenance (ND/<LOQ/NT/value)."""
    t = str(token).strip()
    if t in BELOW_LOQ_TOKENS:
        return '<LOQ'
    return t


# ── Coordinate-aware row reconstruction (scramble-proof) ───────────

def _rows(page, y_tol: float = 3.0) -> List[str]:
    """Reconstruct visual rows from words using spatial order.

    Words are sorted by (top, x0) and grouped into rows whose vertical
    positions fall within ``y_tol`` points; each row is then ordered
    left-to-right. This is immune to the KCA stream-order scramble and
    naturally concatenates side-by-side columns (e.g. the two-column
    pesticide table) into a single row string.
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


def _right_column_block(page, anchor_text: str = 'Client',
                        x_pad: float = 4.0) -> List[str]:
    """Extract the client/producer block (a right-hand column).

    Finds the ``anchor_text`` word, then reconstructs the rows formed by
    words at/right-of its x position and below it -- isolating the client
    column from the interleaved metadata/date columns.
    """
    try:
        words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    except Exception:
        return []
    anchor = next((w for w in words if w['text'] == anchor_text), None)
    if anchor is None:
        return []
    cx, cy = anchor['x0'] - x_pad, anchor['top']
    col = [w for w in words if w['x0'] >= cx and w['top'] > cy + 1]
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


# ── Metadata extraction (page 1) ───────────────────────────────────

def _first(pattern: str, text: str, flags=0) -> str:
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ''


def _parse_metadata(page1_text: str, page1) -> Dict[str, Any]:
    obs: Dict[str, Any] = {}

    # Product name: the line immediately preceding the Metrc tag line.
    lines = [l.rstrip() for l in page1_text.split('\n')]
    metrc_idx = next((i for i, l in enumerate(lines)
                      if l.strip().startswith('Metrc')), None)
    if metrc_idx and metrc_idx > 0:
        for j in range(metrc_idx - 1, -1, -1):
            cand = lines[j].strip()
            if cand and not any(x in cand for x in (
                'KCA', 'Nicholasville', 'Med Cannabis', 'KDA Lic',
                'of 10', 'kcalabs', 'Certificate', '+1-833', 'https')):
                obs['product_name'] = cand
                break

    # Labeled scalar fields.
    metrc = _first(r'Metrc.*?Tag\s*#:\s*(\S+)', page1_text)
    if metrc:
        obs['metrc_ids'] = [metrc]
        obs['metrc_id'] = metrc
    obs['sample_id'] = _first(r'Sample ID:\s*(\S+)', page1_text)
    obs['batch_number'] = _first(r'Batch:\s*(\S+)', page1_text)
    matrix = _first(r'Matrix:\s*([^\n]+)', page1_text)
    if matrix:
        obs['matrix'] = matrix.strip()
    ktype = _first(r'Type:\s*(Raw Material|[A-Za-z ]+?)\s+(?:Mayfield|Matrix|Lexington|USA)', page1_text)
    if ktype:
        obs['sample_type'] = ktype.strip()

    # Dates.
    obs['date_collected'] = _first(r'Collected:\s*(\d{2}/\d{2}/\d{4})', page1_text)
    obs['date_received'] = _first(r'Received:\s*(\d{2}/\d{2}/\d{4})', page1_text)
    obs['date_tested'] = _first(r'Completed:\s*(\d{2}/\d{2}/\d{4})', page1_text)

    # Producer / client block (right-hand column).
    block = _right_column_block(page1, 'Client')
    # Drop trailing "USA" line and locate the license line.
    prod_lic = _first(r'(CULT\d+)', page1_text)
    if prod_lic:
        obs['producer_license_number'] = prod_lic
    if block:
        # block[0] = name, [1] = street, [2] = city/state/zip, ...
        obs['producer'] = block[0].strip()
        if len(block) > 1 and not block[1].startswith('Lic'):
            obs['producer_street'] = block[1].strip()
        for row in block:
            csz = re.match(r'^(.*?),\s*([A-Z]{2})\s+(\d{5})', row)
            if csz:
                obs['producer_city'] = csz.group(1).strip()
                obs['producer_state'] = csz.group(2)
                obs['producer_zipcode'] = csz.group(3)
                break
    return obs


def _parse_summary_strip(page1_text: str) -> Dict[str, Any]:
    """Parse the five-cell summary strip: labels then values on next line.

        Total D9-THC | Total CBD | D9-THCA | Total Cannabinoids | Moisture
        16.46 %      | ND        | 12.14 % | 16.69 %            | 10.3 %
    """
    out: Dict[str, Any] = {}
    lines = page1_text.split('\n')
    for i, ln in enumerate(lines):
        if 'Total' in ln and 'THC' in ln and 'Moisture' in ln and i + 1 < len(lines):
            vals = lines[i + 1].strip()
            # Tokens: numbers (with optional %) or ND/<LOQ.
            toks = re.findall(r'(ND|<LOQ|[\d.]+)\s*%?', vals)
            # Expect 5 in order: totalTHC, totalCBD, D9THCA, totalCann, moisture
            if len(toks) >= 5:
                out['total_thc'] = _num(toks[0])
                out['total_cbd'] = _num(toks[1])
                out['delta_9_thca'] = _num(toks[2])
                out['total_cannabinoids'] = _num(toks[3])
                out['moisture'] = _num(toks[4])
            break
    return out


def _parse_summary_status(page1_text: str) -> Tuple[str, List[str]]:
    """Read the page-1 Summary table -> (overall_status, analyses_present)."""
    statuses = []
    present = set()
    for test, analysis in SUMMARY_TEST_TO_ANALYSIS.items():
        m = re.search(re.escape(test) + r'.*?(Pass|Fail|Tested|NT)\b', page1_text)
        if m:
            st = m.group(1)
            statuses.append(st)
            if st in ('Pass', 'Fail', 'Tested'):
                present.add(analysis)
    overall = 'fail' if 'Fail' in statuses else 'pass'
    return overall, sorted(present)


# ── Analysis section parsers ───────────────────────────────────────

def _parse_cannabinoids(page1) -> Tuple[List[Dict], Dict[str, Any]]:
    """Parse the Cannabinoids-by-HPLC table (scramble-proof).

    Row shapes:
        NAME LOD LOQ MU% RESULT% RESULTmg/g     (individual analytes)
        Total X RESULT% RESULTmg/g              (three totals -> metadata)
    """
    results: List[Dict] = []
    totals: Dict[str, Any] = {}
    rows = _rows(page1)
    in_table = False
    for row in rows:
        if 'Cannabinoids by HPLC' in row:
            in_table = True
            continue
        if not in_table:
            continue
        if row.startswith('UA =') or 'reported expanded' in row:
            break
        s = row.strip()
        # Totals (no LOD/LOQ/MU): "Total THC 16.46 164.57"
        mt = re.match(r'^(Total THC|Total CBD|Total Cannabinoids)\s+'
                      r'(ND|<LOQ|[\d.]+)\s+(ND|<LOQ|[\d.]+)\s*$', s)
        if mt:
            key = ANALYTE_KEY_MAP[mt.group(1)]
            totals[key] = _num(mt.group(2))
            continue
        # Individual: NAME LOD LOQ MU% pct mgg
        mi = re.match(r'^([A-Za-z][A-Za-z0-9\-]*?)\s+'
                      r'([\d.]+)\s+([\d.]+)\s+([\d.]+%)\s+'
                      r'(ND|<LOQ|[\d.]+)\s+(ND|<LOQ|[\d.]+)\s*$', s)
        if mi:
            name = mi.group(1)
            results.append({
                'analysis': 'cannabinoids',
                'key': _key_for(name),
                'name': name,
                'value': _num(mi.group(5)),
                'value_mg_g': _num(mi.group(6)),
                'units': 'percent',
                'lod': _num(mi.group(2)),
                'loq': _num(mi.group(3)),
                'mu': mi.group(4),
                'result_raw': _raw_token(mi.group(5)),
            })
    return results, totals


def _parse_percent_single(page, analysis: str) -> Tuple[List[Dict], Optional[float]]:
    """Parse a single-result percent table (terpenes / vitamin E).

    Row: NAME LOD LOQ MU% RESULT [Pass/Fail]
    Returns (results, total) where total is the 'Total Terpenes' value.
    """
    results: List[Dict] = []
    total = None
    for row in _rows(page):
        s = row.strip()
        mtot = re.match(r'^Total Terpenes.*?([\d.]+)\s*%?\s*$', s)
        if mtot:
            total = _num(mtot.group(1))
            continue
        m = re.match(r'^([A-Za-z(+\u0370-\u03ff][A-Za-z0-9\-()+.\s\u0370-\u03ff]*?)\s+'
                     r'([\d.]+)\s+([\d.]+)\s+([\d.]+%)\s+'
                     r'(ND|<LOQ|[\d.]+)(?:\s+(Pass|Fail))?\s*$', s)
        if m:
            name = m.group(1).strip()
            if name.lower().startswith(('analyte', 'total')):
                continue
            results.append({
                'analysis': analysis,
                'key': _key_for(name),
                'name': name,
                'value': _num(m.group(5)),
                'units': 'percent',
                'lod': _num(m.group(2)),
                'loq': _num(m.group(3)),
                'mu': m.group(4),
                'status': m.group(6),
                'result_raw': _raw_token(m.group(5)),
            })
    return results, total


def _parse_passfail_table(page, analysis: str, units: str) -> List[Dict]:
    """Parse a two-column-safe Pass/Fail numeric table.

    Handles heavy metals (single column) and pesticides (two column).
    The MU%'s trailing '%' anchors column boundaries so both columns
    extract from a single reconstructed row.
    Row unit: NAME LOD LOQ MU% RESULT Pass/Fail
    """
    results: List[Dict] = []
    pat = re.compile(
        r'([A-Za-z][A-Za-z0-9\-\s()]*?)\s+'
        r'([\d.]+)\s+([\d.]+)\s+([\d.]+%)\s+'
        r'(ND|<LOQ|>ULOL|[\d.]+)\s+(Pass|Fail)'
    )
    for row in _rows(page):
        for m in pat.finditer(row):
            name = m.group(1).strip().lstrip('*').strip()
            name = re.sub(r'\s{2,}', ' ', name)
            # Guard against header fragments captured as names.
            if name.lower() in ('analyte', 'result', 'lod', 'loq', 'mu') or len(name) < 2:
                continue
            results.append({
                'analysis': analysis,
                'key': _key_for(name),
                'name': name,
                'value': _num(m.group(5)),
                'units': units,
                'lod': _num(m.group(2)),
                'loq': _num(m.group(3)),
                'mu': m.group(4),
                'status': m.group(6),
                'result_raw': _raw_token(m.group(5)),
            })
    return results


def _parse_mycotoxins(page) -> List[Dict]:
    """Parse mycotoxins (ug/kg). Individual aflatoxins have no per-row
    Pass/Fail; the (Total) and Ochratoxin rows carry status."""
    results: List[Dict] = []
    names = ['Aflatoxins (Total)', 'Aflatoxin B1', 'Aflatoxin B2',
             'Aflatoxin G1', 'Aflatoxin G2', 'Ochratoxin A']
    for row in _rows(page):
        s = row.strip()
        for name in names:
            if not s.startswith(name):
                continue
            rest = s[len(name):].strip()
            status = None
            if rest.endswith('Pass') or rest.endswith('Fail'):
                status = 'Fail' if rest.endswith('Fail') else 'Pass'
            # result token: first ND/<LOQ/number after any LOD/LOQ/MU
            toks = re.findall(r'(ND|<LOQ|>ULOL|[\d.]+%?)', rest)
            # The reported result is the last non-% numeric/ND token before status.
            val_tok = None
            for tk in reversed(toks):
                if tk.endswith('%'):
                    continue
                val_tok = tk
                break
            results.append({
                'analysis': 'mycotoxins',
                'key': _key_for(name),
                'name': name,
                'value': _num(val_tok) if val_tok else None,
                'units': 'ug/kg',
                'status': status,
                'result_raw': _raw_token(val_tok) if val_tok else None,
            })
            break
    return results


def _parse_microbials(page) -> List[Dict]:
    """Parse microbials (mixed quantitative + qualitative rows).

    The Shiga-toxin analyte name wraps across several reconstructed rows
    (``Shiga-toxin producing`` / ``Not Detected per 1 gram Pass`` /
    ``Escherichia coli``). We therefore scan row-by-row and, for the
    qualitative organisms, read the ``Detected|Not Detected per 1 gram
    (Pass|Fail)`` result from whichever row carries it -- associating a
    dangling qualitative result with a pending wrapped name. This is the
    fail-preservation-critical section (Salmonella / Aspergillus).
    """
    rows = _rows(page)
    found: Dict[str, Dict] = {}

    def add(name, value=None, status=None, qualitative=None, raw=None):
        found[name] = {
            'analysis': 'microbials', 'key': _key_for(name), 'name': name,
            'value': value, 'units': 'CFU/g', 'status': status,
            'qualitative': qualitative, 'result_raw': raw,
        }

    pending_name = None  # a wrapped analyte name awaiting its result row
    qual_re = re.compile(r'(Detected|Not Detected) per 1 gram\s+(Pass|Fail)')
    quant_re = re.compile(r'\s+[\d.]+\s+[\d.]+\s+[\d.]+%\s+(ND|[\d.]+)\s+(Pass|Fail)\s*$')

    for row in rows:
        s = row.strip()

        # Quantitative organisms (E. coli total, Yeast and Mold).
        for name in ('Total Escherichia coli', 'Yeast and Mold'):
            if s.startswith(name):
                mq = quant_re.search(s)
                if mq:
                    add(name, value=_num(mq.group(1)), status=mq.group(2),
                        raw=_raw_token(mq.group(1)))

        # Salmonella / Aspergillus: name + qualitative on the same row.
        for name in ('Salmonella species', 'Pathogenic Aspergillus sp.'):
            if s.startswith(name):
                mqual = qual_re.search(s)
                if mqual:
                    add(name, status=mqual.group(2), qualitative=mqual.group(1),
                        raw=mqual.group(1))

        # Shiga-toxin name is wrapped; remember it and grab the next
        # standalone qualitative result row.
        if 'Shiga-toxin producing' in s:
            pending_name = 'Shiga-toxin producing Escherichia coli'
            # Result may be on the same row.
            mqual = qual_re.search(s)
            if mqual:
                add(pending_name, status=mqual.group(2),
                    qualitative=mqual.group(1), raw=mqual.group(1))
                pending_name = None
        elif pending_name and qual_re.search(s) and not any(
                s.startswith(n) for n in ('Salmonella', 'Pathogenic')):
            mqual = qual_re.search(s)
            add(pending_name, status=mqual.group(2),
                qualitative=mqual.group(1), raw=mqual.group(1))
            pending_name = None

    # Emit in canonical order; include any organism not matched as null.
    order = ['Total Escherichia coli', 'Shiga-toxin producing Escherichia coli',
             'Salmonella species', 'Pathogenic Aspergillus sp.', 'Yeast and Mold']
    results = []
    for name in order:
        results.append(found.get(name, {
            'analysis': 'microbials', 'key': _key_for(name), 'name': name,
            'value': None, 'units': 'CFU/g', 'status': None,
            'qualitative': None, 'result_raw': None,
        }))
    return results


def _parse_moisture(page) -> Optional[Dict]:
    """Moisture Content page: bare 'RESULT % MU%'."""
    for row in _rows(page):
        m = re.match(r'^([\d.]+)\s*%\s+[\d.]+%\s*$', row.strip())
        if m:
            return {
                'analysis': 'moisture',
                'key': 'moisture', 'name': 'Moisture',
                'value': _num(m.group(1)), 'units': 'percent',
                'result_raw': m.group(1),
            }
    return None


def _parse_water_activity(page) -> Optional[Dict]:
    """Water Activity page: 'RESULT(Aw) LOD LOQ MU% Pass/Fail'."""
    for row in _rows(page):
        m = re.match(r'^([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+%)\s+(Pass|Fail)\s*$',
                     row.strip())
        if m:
            return {
                'analysis': 'water_activity',
                'key': 'water_activity', 'name': 'Water Activity',
                'value': _num(m.group(1)), 'units': 'aw',
                'lod': _num(m.group(2)), 'loq': _num(m.group(3)),
                'mu': m.group(4), 'status': m.group(5),
                'result_raw': m.group(1),
            }
    return None


# ── Total computation (decarboxylation fallback) ───────────────────

def _result_value(results: List[Dict], key: str) -> Optional[float]:
    for r in results:
        if r.get('key') == key:
            return r.get('value')
    return None


def _compute_total_thc(results: List[Dict]) -> Optional[float]:
    """Total THC = 0.877 * THCa + Delta-9-THC (per Keegan's call).

    Returns None if neither component is quantified.
    """
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


# ── Main parse ─────────────────────────────────────────────────────

def parse_kca_pdf(parser: Any, doc: str, **kwargs) -> Dict:
    """Parse a KCA Laboratories COA PDF into the flat hybrid record."""
    pdf_path = doc
    obs: Dict[str, Any] = dict(KCA_LAB)
    all_results: List[Dict] = []
    analyses: List[str] = []

    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages
        page1 = pages[0]
        page1_text = page1.extract_text() or ''

        # ── Metadata + summary strip + overall status ─────────
        obs.update(_parse_metadata(page1_text, page1))
        strip = _parse_summary_strip(page1_text)
        overall_status, _present = _parse_summary_status(page1_text)
        obs['status'] = overall_status

        # ── Cannabinoids (page 1) ─────────────────────────────
        cann_results, cann_totals = _parse_cannabinoids(page1)
        if cann_results:
            all_results.extend(cann_results)
            analyses.append('cannabinoids')

        # ── Per-analysis pages (titled sections) ──────────────
        for page in pages[1:]:
            try:
                ptext = page.extract_text() or ''
            except Exception:
                continue
            title = ptext.split('\n')[0] if ptext else ''

            if 'Terpenes by' in ptext:
                terps, total_terp = _parse_percent_single(page, 'terpenes')
                if terps:
                    all_results.extend(terps)
                    analyses.append('terpenes')
                    if total_terp is not None:
                        obs['total_terpenes'] = total_terp
            elif 'Heavy Metals by' in ptext:
                hm = _parse_passfail_table(page, 'heavy_metals', 'ppm')
                if hm:
                    all_results.extend(hm)
                    analyses.append('heavy_metals')
            elif 'Pesticides by' in ptext:
                pest = _parse_passfail_table(page, 'pesticides', 'ppm')
                if pest:
                    all_results.extend(pest)
                    analyses.append('pesticides')
            elif 'Mycotoxins by' in ptext:
                myco = _parse_mycotoxins(page)
                if myco:
                    all_results.extend(myco)
                    analyses.append('mycotoxins')
            elif 'Microbials by' in ptext:
                micro = _parse_microbials(page)
                if micro:
                    all_results.extend(micro)
                    analyses.append('microbials')
            elif 'Vitamin E Acetate' in ptext and 'by' not in title:
                vea, _ = _parse_percent_single(page, 'vitamin_e_acetate')
                if vea:
                    all_results.extend(vea)
                    analyses.append('vitamin_e_acetate')
            elif 'Moisture Content by' in ptext:
                mo = _parse_moisture(page)
                if mo:
                    all_results.append(mo)
                    analyses.append('moisture')
                    if mo['value'] is not None and 'moisture' not in obs:
                        obs['moisture'] = mo['value']
            elif 'Water Activity by' in ptext:
                wa = _parse_water_activity(page)
                if wa:
                    all_results.append(wa)
                    analyses.append('water_activity')
            # Page 10 (Reporting Limit Appendix) intentionally ignored.

    # ── Totals: the summary strip is authoritative ────────────
    # The five-cell strip prints ND (-> None) for non-detects, whereas
    # the detail table sometimes prints a literal "0" for the same cell
    # (e.g. Total CBD). Null-vs-zero doctrine: a strip ND must NOT be
    # overwritten by the table's 0. We only fall back to the detail
    # table / decarb when the strip did not report the cell at all.
    strip_has = 'total_thc' in strip  # strip parsed successfully at all
    total_thc = strip.get('total_thc')
    if not strip_has and total_thc is None:
        total_thc = cann_totals.get('total_thc')
    if total_thc is None:
        total_thc = _compute_total_thc(all_results)
    obs['total_thc'] = total_thc

    total_cbd = strip.get('total_cbd')
    if not strip_has and total_cbd is None:
        total_cbd = cann_totals.get('total_cbd')
    if total_cbd is None and not strip_has:
        total_cbd = _compute_total_cbd(all_results)
    obs['total_cbd'] = total_cbd

    total_cann = strip.get('total_cannabinoids')
    if not strip_has and total_cann is None:
        total_cann = cann_totals.get('total_cannabinoids')
    obs['total_cannabinoids'] = total_cann

    if strip.get('moisture') is not None and 'moisture' not in obs:
        obs['moisture'] = strip['moisture']
    if strip.get('delta_9_thca') is not None:
        obs['delta_9_thca'] = strip['delta_9_thca']

    # ── Product type from matrix ("Plant - Flower" -> flower) ──
    matrix = (obs.get('matrix') or '').lower()
    if 'flower' in matrix:
        obs['product_type'] = 'flower'
    elif matrix:
        obs['product_type'] = obs.get('sample_type', '').lower() or matrix
    obs.setdefault('product_type', '')

    # KCA 2025 corpus is flower/raw material -> strain lives in product_name.
    if obs.get('product_name') and not obs.get('strain_name'):
        # Product name is "<Strain>-YYYY-MM-DD"; strip trailing date.
        obs['strain_name'] = re.sub(r'-\d{4}-\d{2}-\d{2}\s*$', '',
                                    obs['product_name']).strip()

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

def parse_kca_coa(parser: Any = None, doc: str = '', **kwargs) -> Dict:
    """Parse a KCA Laboratories COA PDF.

    Registered entry point satisfying the algorithm contract
    ``parse_{lab}_coa(parser, doc)``. The pipeline calls this as
    ``parse_kca_coa(None, file_path)``.

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
    return parse_kca_pdf(parser, doc, **kwargs)


def is_kca(pdf_path: str) -> bool:
    """Quick check whether a PDF is a KCA Laboratories COA."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return False
            t = (pdf.pages[0].extract_text() or '').lower()
            return 'kcalabs.com' in t or 'kca laboratories' in t or 'p_0058' in t
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
            data = parse_kca_coa(None, fp)
            results = json.loads(data.get('results', '[]'))
            analyses = json.loads(data.get('analyses', '[]'))
            print(f'\n{"=" * 62}')
            print(f'OK {os.path.basename(fp)}')
            print(f'  Product : {data.get("product_name")!r}  '
                  f'(strain={data.get("strain_name")!r})')
            print(f'  Type    : {data.get("product_type")!r}  '
                  f'matrix={data.get("matrix")!r}')
            print(f'  Producer: {data.get("producer")!r}  '
                  f'lic={data.get("producer_license_number")!r}')
            print(f'  Sample  : {data.get("sample_id")!r}  '
                  f'batch={data.get("batch_number")!r}')
            print(f'  Metrc   : {data.get("metrc_id")!r}')
            print(f'  Dates   : coll={data.get("date_collected")} '
                  f'recv={data.get("date_received")} test={data.get("date_tested")}')
            print(f'  THC     : {data.get("total_thc")}%   '
                  f'CBD: {data.get("total_cbd")}   '
                  f'Total: {data.get("total_cannabinoids")}%')
            print(f'  Terps   : {data.get("total_terpenes")}%   '
                  f'Moisture: {data.get("moisture")}%')
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
    print(f'\n{"=" * 62}\nResults: {ok} OK, {fail} FAIL of {ok + fail}')
