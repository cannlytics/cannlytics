"""
Parse AcreLabs / Acre Analytical COA — Offline-First Engine
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2026
Updated: 7/15/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse AcreLabs (dba of Acre Analytical, LLC) Certificate of Analysis
    PDFs directly from the PDF text layer — no network access required.
    AcreLabs is the dominant testing laboratory in the Louisiana medical
    cannabis program (KDA/LDH), producing ~82% of the CY2025 LDH
    public-records COA corpus.

    Offline-first, pdfplumber + Python stdlib only. No pandas, PIL,
    requests, or cannlytics internals.

Identification:

    AcreLabs COAs carry, on page 1:
        * License #: 37-0001646
        * 1823 Highway #546, West Monroe, LA 71292
        * Phone: 318-381-3491
        * Brand mark "acrelabs." (2025-mid onward) or "Acre Analytical"
          (early 2025). The disclaimer text reads either
          "AcreLabs may use Measurement Uncertainty ..." or
          "Acre Analytical, LLC may use Measurement Uncertainty ...".
    The lab license 37-0001646 is the single most stable fingerprint and
    is invariant across both brand eras.

Format notes:

    * Page 1 carries the client/sample metadata block plus the
      Cannabinoids (potency), Moisture, and Water Activity panels.
      (In the raw text layer the Moisture/Water Activity blocks are
      emitted BEFORE the client block — position-independent parsing.)
    * The potency table has THREE column schemas, keyed on the header row:
        - Flower / Pre-Roll / Trim:  % (Dry) | mg/g (Dry) | % | mg/g | LOD | LOQ
        - Edible:                    % | mg/g | mg/serv | mg/pkg | LOD | LOQ
        - Concentrate:               % | mg/g | LOD | LOQ
      "% (Dry)" is the moisture-corrected (dry-weight) basis; "%" is the
      as-received basis, and (dry)*(1-moisture) == as-received.
    * Panel scope is driven by the SAMPLE MATRIX. Untested panels are
      printed with every cell reading "NT" (Not Tested). Such panels are
      OMITTED from the record (never zero-filled), per the null-vs-zero
      doctrine. e.g. flower omits Residual Solvents; edibles/concentrates
      omit Moisture / Water Activity; R&D samples may run only pesticides.
    * "9-THC" on the COA denotes delta-9-THC; "delta-8-THC" is delta-8.
    * Total Potential THC/CBD/Cannabinoids are printed; a decarboxylation
      fallback (0.877*THCa + d9-THC) is used only when a total is absent.

Data Points:

    ✓ product_name, strain_name, product_type / matrix
    ✓ producer (client), producer_license_number
    ✓ lab, lab_license_number, lab_address, lab_phone
    ✓ sample_id (lab_id), batch_number, harvest_batch_id
    ✓ metrc_batch_id, metrc_sample_id, metrc_ids
    ✓ date_received, date_tested (reported)
    ✓ product_size (package mass g), servings_per_package
    ✓ total_thc, total_cbd, total_cannabinoids, total_terpenes
    ✓ status (Sample Result), per-panel contaminant statuses
    ✓ moisture_content, water_activity (also emitted as result rows)
    ✓ analyses (list), results (full analyte array w/ dual units + LOD/LOQ)
"""
# Standard imports:
import hashlib
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# External imports:
import pdfplumber


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Constants                                                        ║
# ╚══════════════════════════════════════════════════════════════════╝

ACRELABS = {
    'coa_algorithm': 'acrelabs.py',
    'coa_algorithm_entry_point': 'parse_acrelabs_coa',
    'lab': 'AcreLabs',
    'lab_license_number': '37-0001646',
    'lab_address': '1823 Highway #546, West Monroe, LA 71292',
    'lab_street': '1823 Highway #546',
    'lab_city': 'West Monroe',
    'lab_county': 'Ouachita',
    'lab_state': 'LA',
    'lab_zipcode': '71292',
    'lab_phone': '318-381-3491',
}

# Fingerprints for identification (any one suffices; license is invariant).
ACRELABS_URLS: List[str] = []  # AcreLabs COAs carry no lab URL in the text layer.
ACRELABS_TEXT_PATTERNS = [
    '37-0001646',          # Lab license — invariant across both brand eras.
    'AcreLabs',
    'Acre Analytical',
    '1823 Highway #546',
]

# Decarboxylation factor (molecular-weight ratio, acid -> neutral).
DECARB = 0.877

# Not-a-measurement tokens -> value is null (never 0.0).
NULL_TOKENS = {'ND', 'NT', 'NR', '<LOQ', '<LOD', '>ULOL', 'N/A', 'NA', '-', ''}

# Status anchor tokens for Pass/Fail panels.
STATUS_TOKENS = {'PASS', 'FAIL', 'NT', 'TESTED', 'N/A'}

# Placeholder analyte names to skip (empty rows in un-run panels).
SKIP_NAMES = {'none', 'total'}

# Analysis method-description lines -> analysis key (unambiguous anchors).
METHOD_LINE_MAP = [
    ('potency analysis', 'cannabinoids'),
    ('terpene analysis', 'terpenes'),
    ('residual solvents', 'residual_solvents'),
    ('residual solvent', 'residual_solvents'),
    ('heavy metals analysis', 'heavy_metals'),
    ('heavy metal analysis', 'heavy_metals'),
    ('residual pesticide', 'pesticides'),
    ('pesticide analysis', 'pesticides'),
    ('microbiological screening', 'microbials'),
    ('microbial analysis', 'microbials'),
    ('mycotoxin analysis', 'mycotoxins'),
    ('moisture content analysis', 'moisture'),
    ('water activity analysis', 'water_activity'),
]

# Explicit analyte-name -> (analysis, canonical key). Content-based routing
# (doctrine): the analyte identity, not the section header, decides the panel.
CANNABINOID_NAMES = {
    'cbc': 'cbc', 'cbca': 'cbca', 'cbd': 'cbd', 'cbda': 'cbda',
    'cbdv': 'cbdv', 'cbdva': 'cbdva', 'cbg': 'cbg', 'cbga': 'cbga',
    'cbn': 'cbn', 'cbna': 'cbna', 'cbl': 'cbl',
    '9-thc': 'delta_9_thc', 'delta-9-thc': 'delta_9_thc', 'd9-thc': 'delta_9_thc',
    'delta-8-thc': 'delta_8_thc', '8-thc': 'delta_8_thc', 'd8-thc': 'delta_8_thc',
    'thca': 'thca', 'thcv': 'thcv', 'thcva': 'thcva',
}
TERPENE_NAMES = {
    'β-myrcene': 'beta_myrcene', 'beta-myrcene': 'beta_myrcene',
    'limonene': 'd_limonene', 'd-limonene': 'd_limonene',
    'linalool': 'linalool',
    'β-caryophyllene': 'beta_caryophyllene', 'beta-caryophyllene': 'beta_caryophyllene',
    'α-pinene': 'alpha_pinene', 'alpha-pinene': 'alpha_pinene',
    'β-pinene': 'beta_pinene', 'beta-pinene': 'beta_pinene',
    'α-humulene': 'alpha_humulene', 'alpha-humulene': 'alpha_humulene',
    'terpinolene': 'terpinolene',
    'γ-terpinene': 'gamma_terpinene', 'gamma-terpinene': 'gamma_terpinene',
    'α-terpinene': 'alpha_terpinene', 'alpha-terpinene': 'alpha_terpinene',
    'cis-β-ocimene': 'ocimene', 'cis-beta-ocimene': 'ocimene', 'ocimene': 'ocimene',
    'trans-nerolidol': 'trans_nerolidol', 'nerolidol': 'trans_nerolidol',
    'isopulegol': 'isopulegol', 'guaiol': 'guaiol', 'geraniol': 'geraniol',
    'eucalyptol': 'eucalyptol', 'cymene': 'p_cymene', 'p-cymene': 'p_cymene',
    'caryophyllene oxide': 'caryophyllene_oxide',
    '3-carene': 'delta_3_carene', 'camphene': 'camphene',
    'α-bisabolol': 'alpha_bisabolol', 'alpha-bisabolol': 'alpha_bisabolol',
}
METAL_NAMES = {'arsenic', 'cadmium', 'lead', 'mercury', 'antimony', 'chromium', 'nickel', 'copper'}
MICROBIAL_NAMES = {'yeast/mold', 'yeast and mold', 'e.coli', 'e. coli', 'e-coli',
                   'salmonella', 'salmonella spp.', 'salmonella spp',
                   'coliforms', 'total coliforms', 'aspergillus'}
MYCOTOXIN_NAMES = {'aflatoxins', 'aflatoxin', 'ochratoxins', 'ochratoxin', 'ochratoxin a',
                   'total aflatoxins', 'b1', 'b2', 'g1', 'g2'}
SOLVENT_NAMES = {'butanes', 'butane', 'heptanes', 'heptane', 'benzene', 'toluene',
                 'hexanes', 'hexane', 'xylenes', 'xylene', 'ethanol', 'acetone',
                 'methanol', 'propane', 'isopropanol', 'pentane', 'chloroform'}


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Text helpers                                                     ║
# ╚══════════════════════════════════════════════════════════════════╝

def _deligature(text: str) -> str:
    """Restore the 'fi'/'ti' ligature that pdfplumber renders as \\x00 in
    this template (Certi\\x00cate, de\\x00ned, Of\\x00ce). Substituting 'fi'
    recovers the words used for identification and parsing."""
    if not text:
        return ''
    text = text.replace('\x00', 'fi')
    # The Acre Analytical title splits "fi\n cate" -> normalize.
    text = text.replace('fi\ncate', 'ficate')
    return text


_GREEK = {
    'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta', 'Δ': 'delta',
    'ω': 'omega', 'µ': 'u',
}


def _snake_case(name: str) -> str:
    """Analyte display name -> snake_case key.

    Greek letters spelled out; textual parentheticals dropped but numeric
    parentheticals preserved (isomer disambiguation, per doctrine);
    'spp.' and trailing dots stripped.
    """
    s = name.strip()
    for g, r in _GREEK.items():
        s = s.replace(g, r)
    # Drop textual parentheticals e.g. "(Dichlorvos)"; keep numeric e.g. "(20.1)".
    s = re.sub(r'\(([^)]*)\)', lambda m: (
        f' {m.group(1)} ' if re.fullmatch(r'[\d.]+', m.group(1).strip()) else ' '
    ), s)
    s = re.sub(r'\bspp\.?', ' ', s, flags=re.IGNORECASE)
    s = s.replace('/', ' ')
    s = re.sub(r'[^a-zA-Z0-9.\s]', ' ', s)   # keep '.' for numeric isomers momentarily
    s = re.sub(r'\s+', '_', s.strip())
    s = s.lower().replace('.', '_')
    s = re.sub(r'_+', '_', s).strip('_')
    return s


def _num(token: Optional[str]) -> Optional[float]:
    """Parse a numeric value. ND / NT / <LOQ / <LOD / >ULOL / blank -> None.
    Never returns 0.0 for a non-detect; only a printed numeric 0 stays 0.0."""
    if token is None:
        return None
    t = str(token).strip().replace(',', '')
    if t.upper() in NULL_TOKENS:
        return None
    if t.startswith('<') or t.startswith('>'):
        return None
    # Strip a leading '<'/'>' that survived normalization (defensive).
    t = t.lstrip('<>').strip()
    m = re.match(r'^-?\d+(?:\.\d+)?', t)
    if not m:
        return None
    try:
        return float(m.group(0))
    except (ValueError, TypeError):
        return None


def _limit_num(token: Optional[str]) -> Optional[float]:
    """Parse a limit/threshold, tolerating a leading '<' (e.g. '<10' -> 10)."""
    if token is None:
        return None
    t = str(token).strip().lstrip('<>').strip()
    m = re.match(r'^-?\d+(?:\.\d+)?', t)
    return float(m.group(0)) if m else None


def _norm_line(line: str) -> str:
    """Collapse multi-token qualifiers so column counting is stable:
    '< LOQ' -> '<LOQ', '< LOD' -> '<LOD', '> ULOL' -> '>ULOL', '< 10' -> '<10'."""
    line = re.sub(r'<\s+(LOQ|LOD)\b', r'<\1', line)
    line = re.sub(r'>\s+(ULOL|ULOQ)\b', r'>\1', line)
    line = re.sub(r'([<>])\s+(\d)', r'\1\2', line)
    return line


def _parse_date(text: str) -> str:
    """MM/DD/YYYY, M/D/YY, YYYY-MM-DD -> ISO YYYY-MM-DD; else '' ."""
    if not text:
        return ''
    t = text.strip()
    t = re.sub(r'\s+\d{1,2}:\d{2}(:\d{2})?\s*(AM|PM)?', '', t, flags=re.IGNORECASE).strip()
    for fmt in ('%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%b %d, %Y', '%B %d, %Y'):
        try:
            return datetime.strptime(t, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return ''


def _raw_token(token: Optional[str]) -> Optional[str]:
    """Canonical raw token to preserve in result_raw (ND/<LOQ/NT/...)."""
    if token is None:
        return None
    t = str(token).strip()
    up = t.upper()
    if up in ('ND', 'NT', 'NR', '<LOQ', '<LOD', '>ULOL', 'N/A', 'NA'):
        return up
    return None


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Identification                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

def _identify(pdf) -> bool:
    """True if this PDF is an AcreLabs / Acre Analytical COA."""
    for page in pdf.pages[:3]:
        text = _deligature(page.extract_text() or '')
        low = text.lower()
        if ('37-0001646' in text
                or 'acrelabs' in low
                or 'acre analytical' in low
                or '1823 highway #546' in low):
            return True
    return False


def is_acrelabs(pdf_path: str) -> bool:
    """Public quick check for the census/registry."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return False
            return _identify(pdf)
    except Exception:
        return False


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Metadata (page 1)                                                ║
# ╚══════════════════════════════════════════════════════════════════╝

def _field(text: str, label: str) -> Optional[str]:
    """Grab a single-line labeled field value (e.g. 'License Number:')."""
    m = re.search(rf'{re.escape(label)}\s*:?\s*(.+)', text)
    if not m:
        return None
    val = m.group(1).strip()
    return val or None


def _parse_metadata(page1: str) -> Dict[str, Any]:
    obs: Dict[str, Any] = {}

    obs['producer'] = _field(page1, 'Client Name')
    addr = _field(page1, 'Address')
    if addr:
        obs['producer_address'] = addr
        mstate = re.search(r'([A-Za-z .]+),\s*([A-Z]{2})\s*(\d{5})', addr)
        if mstate:
            obs['producer_city'] = mstate.group(1).strip()
            obs['producer_state'] = mstate.group(2)
            obs['producer_zipcode'] = mstate.group(3)
    obs['producer_license_number'] = _field(page1, 'License Number')
    obs['sample_id'] = _field(page1, 'Sample ID')

    # Sample Name may wrap across lines; capture until the next known label.
    mname = re.search(
        r'Sample Name:\s*(.*?)\s*(?:Sample Matrix:|Sample Type:|Date Received:)',
        page1, re.DOTALL,
    )
    if mname:
        name = re.sub(r'\s+', ' ', mname.group(1)).strip()
        obs['product_name'] = name or None

    matrix = _field(page1, 'Sample Matrix')
    if matrix:
        obs['matrix'] = matrix
        obs['product_type'] = matrix

    dr = _field(page1, 'Date Received')
    if dr:
        obs['date_received'] = _parse_date(dr)
    rep = _field(page1, 'Date Reported')
    if rep:
        obs['date_tested'] = _parse_date(rep)

    mb = _field(page1, 'METRC Batch ID')
    if mb:
        obs['metrc_batch_id'] = mb
    ms = _field(page1, 'METRC Sample ID')
    if ms:
        obs['metrc_sample_id'] = ms
    hb = _field(page1, 'Harvest Batch ID')
    if hb:
        obs['harvest_batch_id'] = hb
        # Use the harvest/production batch as batch_number; fall back to METRC batch.
        obs['batch_number'] = hb
    if not obs.get('batch_number') and mb:
        obs['batch_number'] = mb

    # Edible-only fields.
    pm = re.search(r'Package Mass:\s*([\d.]+)\s*g', page1)
    if pm:
        obs['product_size'] = float(pm.group(1))
    sv = re.search(r'Servings:\s*(\d+)', page1)
    if sv:
        obs['servings_per_package'] = int(sv.group(1))

    # Overall sample result.
    sr = re.search(r'Sample Result:\s*(PASS|FAIL|Pass|Fail)', page1)
    if sr:
        obs['status'] = sr.group(1).lower()

    # METRC id list (short form(s) present on the doc).
    metrc_ids = []
    for v in (obs.get('metrc_sample_id'), obs.get('metrc_batch_id')):
        if v:
            metrc_ids.append(v)
    if metrc_ids:
        obs['metrc_ids'] = metrc_ids
        obs['metrc_source_id'] = obs.get('metrc_sample_id')

    return obs


def _detect_potency_schema(lines: List[str]) -> str:
    """Inspect the potency header row to determine the column schema.
    Returns one of: 'dry' (flower/preroll/trim), 'serving' (edible),
    'plain' (concentrate). Defaults to 'plain'."""
    for ln in lines:
        low = ln.lower()
        if low.startswith('analyte') and ('%' in ln or 'mg/g' in low):
            if '(dry)' in low:
                return 'dry'
            if 'mg/serv' in low or 'mg/pkg' in low:
                return 'serving'
            if 'mg/g' in low:
                return 'plain'
    return 'plain'


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Row classification & parsing                                     ║
# ╚══════════════════════════════════════════════════════════════════╝

def _classify_analyte(name: str, section: Optional[str]) -> Optional[str]:
    """Content-based analysis routing: analyte identity first, section
    context as fallback for unknown analytes."""
    key = name.strip().lower()
    if key in CANNABINOID_NAMES:
        return 'cannabinoids'
    if key in TERPENE_NAMES:
        return 'terpenes'
    if key in METAL_NAMES:
        return 'heavy_metals'
    if key in MICROBIAL_NAMES:
        return 'microbials'
    if key in MYCOTOXIN_NAMES:
        return 'mycotoxins'
    if key in SOLVENT_NAMES:
        return 'residual_solvents'
    return section


def _canonical_key(name: str, analysis: str) -> str:
    key = name.strip().lower()
    if analysis == 'cannabinoids' and key in CANNABINOID_NAMES:
        return CANNABINOID_NAMES[key]
    if analysis == 'terpenes' and key in TERPENE_NAMES:
        return TERPENE_NAMES[key]
    return _snake_case(name)


# Units per Pass/Fail analysis.
STATUS_UNITS = {
    'pesticides': 'ppm', 'heavy_metals': 'ppm', 'residual_solvents': 'ppm',
    'microbials': 'cfu/g', 'mycotoxins': 'ppb',
}

# Names that terminate a record without being analytes.
TOTAL_NAMES = {'total thc', 'total cbd', 'total cannabinoids', 'total terpenes'}


def _is_value_token(tok: str) -> bool:
    """True if a token is a measurement/limit value rather than part of an
    analyte name. Purely-numeric (optionally with a </>/= prefix or % suffix)
    or a non-detect qualifier. '3-Carene' and 'MGK-264' are NOT values
    (they contain letters)."""
    if tok is None:
        return False
    t = tok.strip()
    up = t.upper()
    if up in ('ND', 'NT', 'NR', 'N/A', 'NA'):
        return True
    if up in ('<LOQ', '<LOD', '>ULOL', '>ULOQ'):
        return True
    if re.fullmatch(r'[<>]?=?\d+(?:\.\d+)?%?', t):
        return True
    return False


def _is_status_token(tok: str) -> bool:
    return tok.strip().upper() in ('PASS', 'FAIL')


def _split_records(line: str) -> List[Tuple[str, Optional[str], List[str]]]:
    """Segment a (possibly two-column) table line into records.

    AcreLabs prints Terpenes and Pesticides in two side-by-side columns that
    pdfplumber flattens onto a single physical line, e.g.
        'β-Myrcene 1.04 10.38 0.01 0.25 trans-Nerolidol ND ND 0.031 0.25'
        'Abamectin PASS ND 0.5 0.036 Imazalil PASS ND 0.2 0.072'
    A token state machine walks the line: name tokens accumulate until a
    STATUS token or the first value token, then value tokens accumulate until
    the next name token (which starts a new record). This yields one record
    per column and correctly handles multi-word names ('Methyl Parathion',
    'Caryophyllene Oxide', 'Total Terpenes') and blank-LOQ rows.

    Returns a list of (name, status, values) tuples.
    """
    toks = _norm_line(line).split()
    records: List[Tuple[str, Optional[str], List[str]]] = []
    name: List[str] = []
    status: Optional[str] = None
    vals: List[str] = []
    state = 'NAME'

    def flush():
        if name:
            records.append((' '.join(name), status, list(vals)))

    for tok in toks:
        if state == 'NAME':
            if _is_status_token(tok):
                status = tok.upper()
                state = 'VALUES'
            elif _is_value_token(tok):
                vals.append(tok)
                state = 'VALUES'
            else:
                name.append(tok)
        else:  # VALUES
            if _is_status_token(tok):
                # A second status with no intervening name => start a new
                # record (defensive; normal 2-col lines have a name first).
                flush()
                name, status, vals = [], tok.upper(), []
            elif _is_value_token(tok):
                vals.append(tok)
            else:  # letter token -> next column's analyte name
                flush()
                name, status, vals = [tok], None, []
                state = 'NAME'
    flush()
    return records


def _build_cannabinoid(name: str, vals: List[str], schema: str) -> Optional[Dict]:
    """Build a cannabinoid result row from a split record under the schema.

    'dry':     [%dry, mgg_dry, %, mgg, lod, loq]  (primary value = % Dry)
    'serving': [%, mgg, mg_serv, mg_pkg, lod, loq]
    'plain':   [%, mgg, lod, loq]
    """
    disp = 'Δ9-THC' if name == '9-THC' else name
    row: Dict[str, Any] = {
        'analysis': 'cannabinoids', 'units': 'percent',
        'name': disp, 'key': _canonical_key(name, 'cannabinoids'),
    }

    def take(i):
        return vals[i] if i < len(vals) else None

    if schema == 'dry':
        pct_dry, mgg_dry, pct, mgg, lod, loq = (take(0), take(1), take(2),
                                                take(3), take(4), take(5))
        row['value'] = _num(pct_dry)
        row['value_mg_g'] = _num(mgg_dry)
        row['value_as_received'] = _num(pct)
        row['value_mg_g_as_received'] = _num(mgg)
        row['lod'] = _num(lod)
        row['loq'] = _num(loq)
        raw = _raw_token(pct_dry) or _raw_token(pct)
    elif schema == 'serving':
        pct, mgg, mgserv, mgpkg, lod, loq = (take(0), take(1), take(2),
                                             take(3), take(4), take(5))
        row['value'] = _num(pct)
        row['value_mg_g'] = _num(mgg)
        row['value_mg_serving'] = _num(mgserv)
        row['value_mg_pkg'] = _num(mgpkg)
        row['lod'] = _num(lod)
        row['loq'] = _num(loq)
        raw = _raw_token(pct)
    else:  # plain
        pct, mgg, lod, loq = take(0), take(1), take(2), take(3)
        row['value'] = _num(pct)
        row['value_mg_g'] = _num(mgg)
        row['lod'] = _num(lod)
        row['loq'] = _num(loq)
        raw = _raw_token(pct)

    if raw:
        row['result_raw'] = raw
    row['_nt'] = (raw == 'NT')
    return row


def _build_total(which: str, vals: List[str], schema: str) -> Dict:
    """Build a totals dict (value = primary basis matching cannabinoids)."""
    if not vals:
        return {'value': None}
    if schema == 'dry':
        return {
            'value': _num(vals[0]) if len(vals) > 0 else None,
            'value_mg_g': _num(vals[1]) if len(vals) > 1 else None,
            'value_as_received': _num(vals[2]) if len(vals) > 2 else None,
            'value_mg_g_as_received': _num(vals[3]) if len(vals) > 3 else None,
        }
    if schema == 'serving':
        return {
            'value': _num(vals[0]) if len(vals) > 0 else None,
            'value_mg_g': _num(vals[1]) if len(vals) > 1 else None,
            'value_mg_serving': _num(vals[2]) if len(vals) > 2 else None,
            'value_mg_pkg': _num(vals[3]) if len(vals) > 3 else None,
        }
    return {
        'value': _num(vals[0]) if len(vals) > 0 else None,
        'value_mg_g': _num(vals[1]) if len(vals) > 1 else None,
    }


def _build_terpene(name: str, vals: List[str]) -> Optional[Dict]:
    """Build a terpene result row: [%, mg/g, LOD, LOQ]."""
    pct = vals[0] if len(vals) > 0 else None
    mgg = vals[1] if len(vals) > 1 else None
    lod = vals[2] if len(vals) > 2 else None
    loq = vals[3] if len(vals) > 3 else None
    raw = _raw_token(pct)
    row = {
        'analysis': 'terpenes', 'key': _canonical_key(name, 'terpenes'),
        'name': name, 'value': _num(pct), 'value_mg_g': _num(mgg),
        'lod': _num(lod), 'loq': _num(loq), 'units': 'percent',
        '_nt': (raw == 'NT'),
    }
    if raw:
        row['result_raw'] = raw
    return row


def _build_status(name: str, status_raw: Optional[str], vals: List[str],
                  analysis: str, units: str) -> Dict:
    """Build a Pass/Fail panel row: [result, limit, loq(optional)]."""
    result_tok = vals[0] if len(vals) > 0 else None
    limit_tok = vals[1] if len(vals) > 1 else None
    loq_tok = vals[2] if len(vals) > 2 else None
    status = None
    if status_raw == 'PASS':
        status = 'pass'
    elif status_raw == 'FAIL':
        status = 'fail'
    raw = _raw_token(result_tok)
    row = {
        'analysis': analysis, 'key': _canonical_key(name, analysis),
        'name': name, 'value': _num(result_tok),
        'limit': _limit_num(limit_tok), 'loq': _num(loq_tok),
        'units': units, 'status': status,
        '_nt': (status_raw == 'NT') or (raw == 'NT') or (
            status_raw is None and raw == 'NT'),
    }
    if raw:
        row['result_raw'] = raw
    return row


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Core parse                                                       ║
# ╚══════════════════════════════════════════════════════════════════╝

def parse_acrelabs_pdf(parser: Any = None, doc: str = '', **kwargs) -> Dict:
    """Parse an AcreLabs COA PDF into the standard flat observation dict."""
    pdf_path = doc if isinstance(doc, str) and doc else ''
    if isinstance(parser, str) and not pdf_path:
        pdf_path, parser = parser, None
    if not pdf_path:
        raise ValueError('No PDF path provided.')

    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            raise ValueError(f'Empty PDF: {pdf_path}')
        pages_text = [_deligature(p.extract_text() or '') for p in pdf.pages]

    page1 = pages_text[0]
    full = '\n'.join(pages_text)
    lines = [ln.rstrip() for ln in full.split('\n')]

    # ── Metadata ──────────────────────────────────────────────
    obs: Dict[str, Any] = dict(ACRELABS)
    obs.update(_parse_metadata(page1))

    # Brand era (informational).
    obs['lab_brand'] = 'Acre Analytical' if 'acre analytical' in full.lower() \
        and 'acrelabs' not in full.lower() else 'AcreLabs'

    schema = _detect_potency_schema(lines)
    obs['_potency_schema'] = schema

    # ── Walk lines, classify, parse ───────────────────────────
    results: List[Dict] = []
    totals: Dict[str, Dict] = {}
    section: Optional[str] = None

    # Section names, optionally suffixed with a panel PASS/FAIL summary.
    SECTION_NAMES = {
        'cannabinoids': 'cannabinoids', 'terpenes': 'terpenes',
        'residual solvents': 'residual_solvents', 'heavy metals': 'heavy_metals',
        'pesticides': 'pesticides', 'microbials': 'microbials',
        'mycotoxins': 'mycotoxins', 'moisture': 'moisture',
        'water activity': 'water_activity',
    }

    for ln in lines:
        raw = ln.strip()
        if not raw:
            continue
        low = raw.lower()

        # Section context from method-description lines (anchor, not gate).
        matched_method = False
        for needle, sect in METHOD_LINE_MAP:
            if needle in low:
                section = sect
                matched_method = True
                break
        if matched_method:
            continue

        # Bare or PASS/FAIL-suffixed section headers update context and are
        # never consumed as data (e.g. 'Pesticides PASS', 'Heavy Metals PASS').
        hdr = re.sub(r'\s+(PASS|FAIL|NT)$', '', raw, flags=re.IGNORECASE).strip().lower()
        if hdr in SECTION_NAMES:
            section = SECTION_NAMES[hdr]
            continue

        # Moisture / Water Activity — combined ('Moisture 12.2 Water Activity
        # 0.57') or separate lines; NT => not tested (omit, no scalar).
        if re.search(r'\bMoisture\s+(?:[\d.]+|NT|ND)\b', raw) or \
                re.search(r'\bWater Activity\s+(?:[\d.]+|NT|ND)\b', raw):
            for mm in re.finditer(r'\bMoisture\s+([\d.]+|NT|ND)\b', raw):
                v = _num(mm.group(1))
                if v is not None:
                    results.append({'analysis': 'moisture', 'key': 'moisture',
                                    'name': 'Moisture', 'value': v,
                                    'units': 'percent'})
                    obs['moisture_content'] = v
            for mm in re.finditer(r'\bWater Activity\s+([\d.]+|NT|ND)\b', raw):
                v = _num(mm.group(1))
                if v is not None:
                    results.append({'analysis': 'water_activity',
                                    'key': 'water_activity', 'name': 'Water Activity',
                                    'value': v, 'units': 'aw'})
                    obs['water_activity'] = v
            continue

        # Homogeneity: "Homogeneity 15% Pass 0.14" (Pass mid-row => handled here,
        # not by the generic splitter). A bare "Homogeneity 15%" (no Pass/result,
        # e.g. R&D samples) is not-tested — skip it entirely so it never leaks
        # into the cannabinoids panel.
        if re.match(r'^Homogeneity\b', raw):
            m_homo = re.match(
                r'^Homogeneity\s+([\d.]+)%?\s+(Pass|Fail)\s+([\d.]+)', raw)
            if m_homo:
                results.append({
                    'analysis': 'homogeneity', 'key': 'homogeneity',
                    'name': 'Homogeneity', 'value': _num(m_homo.group(3)),
                    'limit': _num(m_homo.group(1)),
                    'status': m_homo.group(2).lower(), 'units': 'percent',
                })
            continue

        # Skip headers / method text / footers before record splitting.
        if low.startswith('analyte'):
            continue
        if any(k in low for k in (
            'certificate of analysis', 'determination of pass', 'measurement uncertainty',
            'these results only relate', 'this report shall', 'license #', 'license number',
            'client name', 'address:', 'phone:', 'sample id', 'sample name',
            'sample matrix', 'date received', 'date reported', 'metrc', 'harvest batch',
            'package mass', 'servings', 'lab director', 'sample result', 'analysis utilizing',
            'west monroe', 'highway', 'page ', 'nd=not', 'lod=', 'loq=', 'limit units',
            'analyst:', 'date:',
        )):
            continue

        # Split the (possibly two-column) line into records and classify each.
        for name, status_raw, vals in _split_records(raw):
            if not vals:
                continue  # bare header fragment, no measurement
            low_name = name.strip().lower()

            # Totals (may appear in the right column of a terpene/cann line).
            if low_name == 'total terpenes':
                v = _num(vals[0]) if vals else None
                if v is not None:
                    obs['total_terpenes'] = v
                continue
            if low_name in ('total thc', 'total cbd', 'total cannabinoids'):
                which = low_name.replace(' ', '_')
                totals[which] = _build_total(which, vals, schema)
                continue
            if low_name in SKIP_NAMES:
                continue

            analysis = _classify_analyte(name, section)
            if analysis is None:
                continue

            if analysis == 'cannabinoids':
                row = _build_cannabinoid(name, vals, schema)
            elif analysis == 'terpenes':
                row = _build_terpene(name, vals)
            else:
                units = STATUS_UNITS.get(analysis, 'ppm')
                row = _build_status(name, status_raw, vals, analysis, units)

            if row:
                results.append(row)

    # ── Panel-scope pruning: drop panels that were entirely NT ────
    results = _prune_untested_panels(results)

    # ── Totals -> scalars (decarb fallback if a total is missing) ─
    _apply_totals(obs, totals, results, schema)

    # ── Contaminant status roll-ups ───────────────────────────
    _rollup_statuses(obs, results)

    # ── Strip internal flags before serialization ─────────────
    for r in results:
        r.pop('_nt', None)
        r.pop('_total', None)

    analyses = sorted({r['analysis'] for r in results})

    # ── Finalize ──────────────────────────────────────────────
    obs.pop('_potency_schema', None)
    obs['analyses'] = json.dumps(analyses)
    obs['results'] = json.dumps(results)
    obs['coa_parsed_at'] = datetime.now().isoformat()

    hash_input = json.dumps(results, sort_keys=True)
    obs['results_hash'] = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    if not obs.get('sample_id'):
        id_input = (hash_input + str(obs.get('product_name', ''))
                    + str(obs.get('producer', '')) + str(obs.get('date_tested', '')))
        obs['sample_id'] = hashlib.sha256(id_input.encode()).hexdigest()[:16]
    obs['lab_id'] = obs.get('sample_id', '')
    obs['coa_pdf'] = pdf_path.replace('\\', '/').split('/')[-1]
    obs.setdefault('status', 'pass')

    return obs



def _prune_untested_panels(results: List[Dict]) -> List[Dict]:
    """Drop any analysis whose every row is not-tested (NT). A run panel with
    all-ND rows is retained (tested, non-detect). Doctrine: untested panels
    are absent, never zero-filled."""
    by_analysis: Dict[str, List[Dict]] = {}
    for r in results:
        by_analysis.setdefault(r['analysis'], []).append(r)
    keep: List[Dict] = []
    for analysis, rows in by_analysis.items():
        # moisture/water_activity rows are only appended when tested, so keep.
        if all(r.get('_nt') for r in rows):
            continue
        keep.extend(rows)
    return keep


def _apply_totals(obs: Dict, totals: Dict[str, Dict], results: List[Dict],
                  schema: str) -> None:
    """Set total_thc/total_cbd/total_cannabinoids scalars from printed totals;
    fall back to the decarboxylation formula only when a total is absent."""
    have_cannabinoids = any(r['analysis'] == 'cannabinoids' for r in results)

    for which in ('total_thc', 'total_cbd', 'total_cannabinoids'):
        row = totals.get(which)
        if row and row.get('value') is not None:
            obs[which] = row['value']

    # Decarb fallback for total_thc/total_cbd if not printed but acids present.
    if have_cannabinoids and obs.get('total_thc') is None:
        acid = _analyte_value(results, 'thca')
        neutral = _analyte_value(results, 'delta_9_thc')
        if acid is not None or neutral is not None:
            obs['total_thc'] = round(DECARB * (acid or 0.0) + (neutral or 0.0), 4)
    if have_cannabinoids and obs.get('total_cbd') is None:
        acid = _analyte_value(results, 'cbda')
        neutral = _analyte_value(results, 'cbd')
        if acid is not None or neutral is not None:
            obs['total_cbd'] = round(DECARB * (acid or 0.0) + (neutral or 0.0), 4)

    # Promote a handful of individual cannabinoids to top-level scalars.
    for key in ('delta_9_thc', 'delta_8_thc', 'thca', 'cbd', 'cbda',
                'cbg', 'cbga', 'cbn', 'cbc', 'cbdv', 'thcv'):
        v = _analyte_value(results, key)
        if v is not None:
            obs[key] = v


def _analyte_value(results: List[Dict], key: str) -> Optional[float]:
    for r in results:
        if r.get('analysis') == 'cannabinoids' and r.get('key') == key:
            return r.get('value')
    return None


def _rollup_statuses(obs: Dict, results: List[Dict]) -> None:
    """Derive per-panel contaminant statuses from result rows."""
    mapping = {
        'pesticides': 'pesticides_status',
        'heavy_metals': 'heavy_metals_status',
        'microbials': 'microbials_status',
        'mycotoxins': 'mycotoxins_status',
        'residual_solvents': 'residual_solvents_status',
    }
    for analysis, field_name in mapping.items():
        rows = [r for r in results if r.get('analysis') == analysis]
        if not rows:
            continue
        statuses = [r.get('status') for r in rows if r.get('status')]
        if not statuses:
            continue
        obs[field_name] = 'fail' if 'fail' in statuses else 'pass'


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Entry point (LAB_REGISTRY contract)                             ║
# ╚══════════════════════════════════════════════════════════════════╝

def parse_acrelabs_coa(parser: Any = None, doc: str = '', **kwargs) -> Dict:
    """Main entry point registered in LAB_REGISTRY.
    Satisfies the algorithm contract: parse_{lab}_coa(parser, doc, **kwargs)."""
    if isinstance(parser, str) and not doc:
        doc, parser = parser, None
    if isinstance(doc, str) and doc.startswith('http'):
        raise ValueError('URL parsing requires network access. '
                         'Provide the PDF file path instead.')
    return parse_acrelabs_pdf(parser, doc, **kwargs)


# ── CLI smoke test ─────────────────────────────────────────────────

if __name__ == '__main__':
    import sys
    for pdf_file in sys.argv[1:]:
        print('=' * 88)
        print(pdf_file)
        try:
            out = parse_acrelabs_coa(doc=pdf_file)
        except Exception as e:
            print('  ERROR:', type(e).__name__, e)
            continue
        rs = json.loads(out['results'])
        print(f"  product={out.get('product_name')!r}  matrix={out.get('matrix')!r}"
              f"  status={out.get('status')!r}")
        print(f"  total_thc={out.get('total_thc')}  total_cbd={out.get('total_cbd')}"
              f"  total_cannabinoids={out.get('total_cannabinoids')}")
        print(f"  moisture={out.get('moisture_content')}  water_activity={out.get('water_activity')}")
        print(f"  analyses={json.loads(out['analyses'])}")
        print(f"  #results={len(rs)}")