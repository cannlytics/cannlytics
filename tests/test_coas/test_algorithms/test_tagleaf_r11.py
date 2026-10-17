"""
Regression tests for the 10/13/2026 (R11) fixes to tagleaf.py
(TagLeaf LIMS COA parser: 2 River Labs, BelCosta Labs, Pure Cannalyst
Labs and Infinite Chemical Analysis Labs, California).

No real PDFs are used. Each test feeds pdfplumber-like pages (page text
and the rows of ``extract_tables()``) to _parse_results_from_tables, or
drives parse_tagleaf_coa through a stand-in for pdfplumber. The tables
follow the layouts documented in tagleaf.py, with the values four
Claude models read from 4 TagLeaf COAs. The bug tests fail on the
r10-delivered parser; the regression tests pin values the r10 parser
already read right.

    1. A table that a page break continues has no header row on the
       next page. Its first analyte was taken for the header (its PASS
       let it pass for one), and the rest were read as potency rows,
       whose first number is the result: non-detects read their action
       limit (COA 15c4ba70..., 2 River Labs pesticides: flonicamid 0.1,
       imidacloprid 5.0 ug/g; COA dd7a0f90..., Pure Cannalyst foreign
       material: mold and sand 25.0 percent), and the first analyte of
       each continuation (fipronil, spiromesifen) was lost.
    2. Non-detects were 0.0. They are value None with the qualifier
       'ND' or '<LOQ' (cannlytics.data.coas.schema.parse_result_value).
    3. Moisture and water activity rows were dropped with the status
       bar's "MOISTURE TESTED" entries.
    4. One-row tables (a single analyte left on a page) and header rows
       printed as a table of their own were skipped.
    5. Units are those printed in the read cell or column ('aw', not
       'aW'); of two amounts, the percent one is the result.

Run:
    pytest tests/test_coas/test_algorithms/test_tagleaf_r11.py -v
"""
import json

import pytest

from cannlytics.data.coas.algorithms import tagleaf

# ── pdfplumber stand-ins ──────────────────────────────────────────────

class _Page:
    """A page as pdfplumber gives it: text and table rows."""

    def __init__(self, text='', tables=()):
        self.text = text
        self.tables = [[list(row) for row in table] for table in tables]

    def extract_text(self):
        return self.text

    def extract_tables(self):
        return self.tables


class _PDF:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def parse(pages):
    """Results of _parse_results_from_tables for the pages."""
    results, _ = tagleaf._parse_results_from_tables(_PDF(pages))
    return results


def by_key(rows, key, analysis=None):
    """The one row with ``key`` (and ``analysis``)."""
    found = [r for r in rows if r['key'] == key
             and (analysis is None or r['analysis'] == analysis)]
    assert len(found) == 1, f'{key}: {found}'
    return found[0]


def assert_nondetect(row, limit=None):
    assert row['value'] is None, row
    assert row['qualifier'] == 'ND', row
    assert row['limit'] == limit, row


# ── Table rows ────────────────────────────────────────────────────────

SAFETY = ['ANALYTE', 'LIMIT', 'AMT', 'LOD/LOQ', 'PASS/FAIL']
POTENCY = ['ANALYTE', 'AMT', 'AMT', 'LOD/LOQ', 'PASS/FAIL']


def pest(name, limit, lod_loq, amt='ND', status='PASS'):
    """A pesticide row; Category I pesticides print no limit."""
    return [name, f'{limit} µg/g' if limit else '', amt, lod_loq, status]


# COA 15c4ba70... (2 River Labs, flower): the pesticide list printed in
# two halves side by side, both broken by the page after FENPYROXIMATE
# and SPINOSAD D, so the halves continue on the next page without
# headers. The benchmark's reading: every pesticide ND.
RIVER_GC = [
    SAFETY,
    pest('CHLORDANE', None, '0.026/0.0956'),
    pest('CHLORFENAPYR', None, '0.0215/0.0792'),
    pest('METHYL PARATHION', None, '0.0157/0.0577'),
    pest('PENTACHLORONITROBENZENE', '0.1', '0.0249/0.0916'),
]
RIVER_LEFT = [
    SAFETY,
    pest('ABAMECTIN', '0.1', '0.0117/0.0429'),
    pest('ACEPHATE', '0.1', '0.0231/0.0851'),
    pest('ALDICARB', None, '0.0251/0.0924'),
    pest('BIFENTHRIN', '3', '0.0268/0.0985'),
    pest('FENPYROXIMATE', '0.1', '0.0252/0.0928'),
]
RIVER_RIGHT = [
    SAFETY,
    pest('MALATHION', '0.5', '0.0262/0.0965'),
    pest('METALAXYL', '2', '0.0168/0.062'),
    pest('PYRETHRINS', '0.5', ''),
    ['PYRETHRINS CINERIN I', '', 'ND', '0.0041/0.0151', ''],
    pest('SPINOSAD', '0.1', ''),
    ['SPINOSAD A', '', 'ND', '0.0235/0.0865', ''],
    ['SPINOSAD D', '', 'ND', '0.0034/0.0126', ''],
]
RIVER_LEFT_CONTINUED = [
    pest('FIPRONIL', None, '0.0245/0.0902'),
    pest('FLONICAMID', '0.1', '0.0242/0.0891'),
    pest('FLUDIOXONIL', '0.1', '0.0263/0.0967'),
    pest('HEXYTHIAZOX', '0.1', '0.0203/0.0746'),
    pest('IMAZALIL', None, '0.0195/0.0718'),
    pest('IMIDACLOPRID', '5', '0.0183/0.0673'),
    pest('KRESOXIM-METHYL', '0.1', '0.01/0.0368'),
]
RIVER_RIGHT_CONTINUED = [
    pest('SPIROMESIFEN', '0.1', '0.0269/0.0991'),
    pest('SPIROTETRAMAT', '0.1', '0.0191/0.0703'),
    pest('SPIROXAMINE', None, '0.0201/0.0738'),
    pest('TEBUCONAZOLE', '0.1', '0.0252/0.0927'),
    pest('THIACLOPRID', None, '0.0206/0.0759'),
    pest('THIAMETHOXAM', '5', '0.0117/0.0431'),
    pest('TRIFLOXYSTROBIN', '0.1', '0.0127/0.0466'),
]
RIVER_METALS = [
    SAFETY,
    ['ARSENIC', '0.2 µg/g', 'ND', '0.039/0.123', 'PASS'],
    ['CADMIUM', '0.2 µg/g', '<LOQ', '0.011/0.05', 'PASS'],
    ['LEAD', '0.5 µg/g', 'ND', '0.014/0.05', 'PASS'],
    ['MERCURY', '0.1 µg/g', 'ND', '0.009/0.03', 'PASS'],
]


def river_pesticide_pages():
    return [
        _Page('PESTICIDES BY LC-MS/MS AND GC-MS/MS // DEC 19, 2023 PASS',
              [RIVER_GC, RIVER_LEFT, RIVER_RIGHT]),
        _Page('HEAVY METALS BY ICP-MS // DEC 19, 2023 PASS',
              [RIVER_LEFT_CONTINUED, RIVER_RIGHT_CONTINUED, RIVER_METALS]),
    ]


# ── 1. Continued tables: a non-detect is not its action limit ─────────

# (key, limit) of the 9 pesticides the r10 parser read as their limits.
RIVER_LIMIT_ERRORS = [
    ('flonicamid', 0.1), ('fludioxonil', 0.1), ('hexythiazox', 0.1),
    ('imidacloprid', 5.0), ('kresoxim_methyl', 0.1), ('spirotetramat', 0.1),
    ('tebuconazole', 0.1), ('thiamethoxam', 5.0), ('trifloxystrobin', 0.1),
]


@pytest.mark.parametrize('key,limit', RIVER_LIMIT_ERRORS)
def test_continued_pesticides_are_not_read_as_their_limits(key, limit):
    # r10: flonicamid 0.1, imidacloprid 5.0 ... (the LIMIT column).
    row = by_key(parse(river_pesticide_pages()), key)
    assert_nondetect(row, limit)
    assert row['units'] == 'ug/g'
    assert row['status'] == 'pass'
    assert row['analysis'] == 'pesticides'


def test_continued_pesticides_keep_their_lod_loq():
    rows = parse(river_pesticide_pages())
    flonicamid = by_key(rows, 'flonicamid')
    assert (flonicamid['lod'], flonicamid['loq']) == (0.0242, 0.0891)
    imidacloprid = by_key(rows, 'imidacloprid')
    assert (imidacloprid['lod'], imidacloprid['loq']) == (0.0183, 0.0673)


def test_first_analyte_of_each_continuation_is_read():
    # r10 took FIPRONIL and SPIROMESIFEN for the continuations' headers.
    rows = parse(river_pesticide_pages())
    assert_nondetect(by_key(rows, 'fipronil'), None)
    assert by_key(rows, 'fipronil')['lod'] == 0.0245
    assert_nondetect(by_key(rows, 'spiromesifen'), 0.1)


def test_every_pesticide_is_read_once():
    rows = [r for r in parse(river_pesticide_pages()) if r['analysis'] == 'pesticides']
    names = [r[0] for table in (RIVER_GC, RIVER_LEFT, RIVER_RIGHT) for r in table[1:]]
    names += [r[0] for r in RIVER_LEFT_CONTINUED + RIVER_RIGHT_CONTINUED]
    assert [r['name'] for r in rows] == names
    assert all(r['value'] is None and r['qualifier'] == 'ND' for r in rows)


def test_category_one_continuation_rows_print_no_limit():
    rows = parse(river_pesticide_pages())
    for key in ('imazalil', 'spiroxamine', 'thiacloprid'):
        assert_nondetect(by_key(rows, key), None)


def test_continuation_with_a_measured_pesticide():
    pages = river_pesticide_pages()
    pages[1].tables[0][1] = pest('FLONICAMID', '0.1', '0.0242/0.0891', amt='0.35', status='FAIL')
    flonicamid = by_key(parse(pages), 'flonicamid')
    assert flonicamid['value'] == 0.35
    assert flonicamid['qualifier'] == ''
    assert flonicamid['limit'] == 0.1
    assert flonicamid['status'] == 'fail'


# COA dd7a0f90... (Pure Cannalyst Labs, flower): the foreign material
# table read without its header; the benchmark's reading is ND for all
# four rows, with limits 25 %, 1 per 3 g, 25 % and 25 %.
CANNALYST_METALS = [
    ['Analyte', 'Limit', 'Amt', 'LOD/LOQ', 'Pass/Fail'],
    ['Arsenic', '0.2 µg/g', 'ND', '0.0205/0.062', 'PASS'],
    ['Cadmium', '0.2 µg/g', 'ND', '0.0207/0.063', 'PASS'],
    ['Lead', '0.5 µg/g', 'ND', '0.0592/0.18', 'PASS'],
    ['Mercury', '0.1 µg/g', 'ND', '0.00698/0.0319', 'PASS'],
]
CANNALYST_FOREIGN = [
    ['Imbedded Foreign Material', '25 %', 'ND', 'PASS'],
    ['Insect Fragments, Hair, Mammal Excrement', '1 per 3 g', 'ND', 'PASS'],
    ['Mold', '25 %', 'ND', 'PASS'],
    ['Sand, Soil, Cinders, Dirt', '25 %', 'ND', 'PASS'],
]


def five_columns(rows):
    """The rows with an empty LOD/LOQ column before PASS/FAIL."""
    return [r[:3] + [''] + r[3:] for r in rows]


@pytest.mark.parametrize('foreign', [
    CANNALYST_FOREIGN,
    five_columns(CANNALYST_FOREIGN),
    [['Water Activity', '0.65 aw', '0.573 aw', 'PASS']] + CANNALYST_FOREIGN,
], ids=['4-columns', '5-columns', 'water-activity-first'])
def test_foreign_material_without_header_is_not_read_as_limits(foreign):
    # r10: mold 25.0 and sand 25.0 percent (the LIMIT column).
    page = _Page('HEAVY METALS // SEP 12, 2025\nFOREIGN MATERIAL // SEP 09, 2025',
                 [CANNALYST_METALS, foreign])
    rows = parse([page])
    for key in ('mold', 'sand_soil_cinders_dirt', 'imbedded_foreign_material'):
        row = by_key(rows, key)
        assert_nondetect(row, 25.0)
        assert row['units'] == 'percent'
        assert row['status'] == 'pass'
        assert row['analysis'] == 'moisture_foreign_matter'
    insect = by_key(rows, 'insect_fragments_hair_mammal_excrement')
    assert_nondetect(insect, 1.0)


def test_section_title_in_a_table_without_header_is_not_an_analyte():
    continued = [['HEAVY METALS BY ICP-MS // DEC 19, 2023', '', '', '', 'PASS']]
    continued += RIVER_LEFT_CONTINUED
    rows = parse([river_pesticide_pages()[0], _Page('', [continued])])
    assert [r['key'] for r in rows if r['key'].startswith('heavy')] == []
    assert_nondetect(by_key(rows, 'fipronil'), None)
    assert_nondetect(by_key(rows, 'flonicamid'), 0.1)


def test_water_activity_first_in_a_table_without_header():
    page = _Page('', [CANNALYST_METALS,
                      [['Water Activity', '0.65 aw', '0.573 aw', 'PASS']] + CANNALYST_FOREIGN])
    water = by_key(parse([page]), 'water_activity')
    assert water['value'] == 0.573
    assert (water['units'], water['limit'], water['status']) == ('aw', 0.65, 'pass')
    assert water['analysis'] == 'moisture_foreign_matter'


def test_terpenes_continued_without_header_are_read():
    # r10 skipped a continuation with no PASS, LOD or AMT in its first row.
    terpenes = [
        POTENCY,
        ['TOTAL TERPENES', '2.6648 %', '26.648 mg/g', '', ''],
        ['β-MYRCENE', '1.5393 %', '15.393 mg/g', '0.0079/0.05', ''],
    ]
    continued = [
        ['TRANS-NEROLIDOL', '0.053 %', '0.53 mg/g', '0.0128/0.057', ''],
        ['α-TERPINENE', '<LOQ', '<LOQ', '0.0049/0.05', ''],
        ['GUAIOL', 'ND', 'ND', '0.01/0.05', ''],
    ]
    rows = parse([_Page('TERPENES BY GC-MS // DEC 18, 2023', [terpenes]),
                  _Page('', [continued])])
    nerolidol = by_key(rows, 'trans_nerolidol')
    assert (nerolidol['value'], nerolidol['units'], nerolidol['analysis']) == (0.053, 'percent', 'terpenes')
    assert (nerolidol['lod'], nerolidol['loq']) == (0.0128, 0.057)
    terpinene = by_key(rows, 'alpha_terpinene')
    assert (terpinene['value'], terpinene['qualifier'], terpinene['loq']) == (None, '<LOQ', 0.05)
    assert by_key(rows, 'guaiol')['qualifier'] == 'ND'


def test_a_data_row_is_not_a_header():
    # The root cause: r10 accepted any first row containing 'PASS'.
    assert tagleaf._header_layout(['FIPRONIL', '', 'ND', '0.0245/0.0902', 'PASS']) is None
    assert tagleaf._header_layout(['Mold', '25 %', 'ND', 'PASS']) is None
    assert tagleaf._header_layout(['PESTICIDES // DEC 19, 2023', '', '', '', 'PASS']) is None
    layout = tagleaf._header_layout(SAFETY)
    assert {k: layout[k] for k in ('limit', 'result', 'lod_loq', 'status')} == {
        'limit': 1, 'result': 2, 'lod_loq': 3, 'status': 4}
    layout = tagleaf._header_layout(['ANALYTE', 'AMT', 'AMT', 'LOD/LOQ', 'PASS/FAI'])
    assert (layout['result'], layout['result2'], layout['limit'], layout['status']) == (1, 2, None, 4)


# ── 2. Non-detects keep their qualifier ───────────────────────────────

def test_nondetects_and_bounds_are_not_zero():
    rows = parse([_Page('HEAVY METALS', [RIVER_METALS])])
    arsenic = by_key(rows, 'arsenic')
    assert (arsenic['value'], arsenic['qualifier']) == (None, 'ND')  # r10: 0.0
    assert (arsenic['limit'], arsenic['lod'], arsenic['loq']) == (0.2, 0.039, 0.123)
    cadmium = by_key(rows, 'cadmium')
    assert (cadmium['value'], cadmium['qualifier'], cadmium['loq']) == (None, '<LOQ', 0.05)


def test_bound_without_lod_loq_column_sets_loq():
    table = [['ANALYTE', 'LIMIT', 'AMT', 'PASS/FAIL'],
             ['LEAD', '0.5 µg/g', '<0.05', 'PASS'],
             ['MERCURY', '0.1 µg/g', '0', 'PASS']]
    rows = parse([_Page('HEAVY METALS', [table])])
    lead = by_key(rows, 'lead')
    assert (lead['value'], lead['qualifier'], lead['loq'], lead['lod']) == (None, '<LOQ', 0.05, None)
    assert lead['limit'] == 0.5
    mercury = by_key(rows, 'mercury')
    assert (mercury['value'], mercury['qualifier']) == (0.0, '')  # a measured 0 stays 0.0


def test_unprinted_limits_are_none():
    rows = parse(river_pesticide_pages())
    aldicarb = by_key(rows, 'aldicarb')
    assert (aldicarb['limit'], aldicarb['lod'], aldicarb['loq']) == (None, 0.0251, 0.0924)
    pyrethrins = by_key(rows, 'pyrethrins')
    assert (pyrethrins['limit'], pyrethrins['lod'], pyrethrins['loq']) == (0.5, None, None)


def test_number_helpers_return_none_for_words_and_bounds():
    assert tagleaf._parse_number('0.1 µg/g') == 0.1
    assert tagleaf._parse_number('5,000') == 5000.0
    for text in ('ND', 'LOD', '--', '<0.1', '', None):
        assert tagleaf._parse_number(text) is None
    assert tagleaf._parse_lod_loq('0.0109/0.24767') == (0.0109, 0.24767)
    assert tagleaf._parse_lod_loq('') == (None, None)
    assert tagleaf._parse_lod_loq('12/19/2023') == (None, None)
    assert tagleaf._parse_result('ND') == (None, 'ND', None)
    assert tagleaf._parse_result('<0.05') == (None, '<LOQ', 0.05)
    assert tagleaf._parse_result('44.5938 %') == (44.5938, '', None)
    assert tagleaf._parse_result('') == (None, 'NR', None)


# ── 3. Moisture and water activity ────────────────────────────────────

def test_moisture_and_water_activity_rows_are_kept():
    # COA 1a1452d5... (BelCosta): moisture 7.6 %, water activity 0.57 aw.
    # r10 dropped both as status-bar entries.
    table = [['ANALYTE', 'LIMIT', 'AMT', 'PASS/FAIL'],
             ['MOISTURE', '', '7.6 %', 'TESTED'],
             ['WATER ACTIVITY', '0.65 aw', '0.57 aw', 'PASS']]
    rows = parse([_Page('MOISTURE & WATER ACTIVITY // JUN 12, 2024', [table])])
    moisture = by_key(rows, 'moisture_content')
    assert (moisture['value'], moisture['units'], moisture['limit']) == (7.6, 'percent', None)
    assert moisture['analysis'] == 'moisture_foreign_matter'
    water = by_key(rows, 'water_activity')
    assert (water['value'], water['units'], water['limit'], water['status']) == (0.57, 'aw', 0.65, 'pass')


def test_water_activity_without_printed_units_is_aw():
    table = [['ANALYTE', 'LIMIT', 'AMT', 'PASS/FAIL'],
             ['WATER ACTIVITY', '0.65', '0.4457', 'PASS'],
             ['MOLD', '25 %', 'ND', 'PASS']]
    rows = parse([_Page('FOREIGN MATERIAL', [table])])
    assert by_key(rows, 'water_activity')['units'] == 'aw'
    assert by_key(rows, 'mold')['units'] == 'percent'


def test_status_bar_entries_are_not_analytes():
    status_bar = [['BATCH RESULT', 'PASS'], ['POTENCY', 'TESTED'],
                  ['MOISTURE', 'TESTED'], ['WATER ACTIVITY', 'PASS'],
                  ['PESTICIDES', 'PASS'], ['FOREIGN MATTER', 'PASS']]
    assert parse([_Page('REGULATORY COMPLIANCE TESTING', [status_bar])]) == []


def test_summary_without_status_or_lod_loq_is_not_read():
    # A table without a header is read only as a TagLeaf result table
    # (PASS/FAIL or LOD/LOQ column) or as the continuation of one, so a
    # page-1 summary does not repeat the cannabinoids.
    summary = [['TOTAL THC', '39.4781 %'], ['Δ9-THC', '0.3693 %'], ['THCA', '44.5938 %']]
    rows = parse([_Page(RIVER_FRONT, [summary, RIVER_CANNABINOIDS])])
    assert by_key(rows, 'thca')['value'] == 44.5938
    assert by_key(rows, 'delta_9_thc')['value'] == 0.3693
    assert 'total_thc' not in {r['key'] for r in rows}


# ── 4. One-row tables and lone headers ────────────────────────────────

def test_one_row_table_is_read():
    # COA 1a1452d5... (BelCosta): MALATHION is missing from the r10
    # output; a page break that leaves one row in a table of its own
    # does that (r10 skipped tables of fewer than 2 rows).
    pages = [
        _Page('PESTICIDES', [[SAFETY,
                              pest('IMIDACLOPRID', '5', '0.00796/0.02411'),
                              pest('KRESOXIM-METHYL', '0.1', '0.00989/0.02997')]]),
        _Page('', [[pest('MALATHION', '0.5', '0.00701/0.02124')],
                   [SAFETY, pest('METALAXYL', '2', '0.0058/0.01757')]]),
    ]
    rows = parse(pages)
    malathion = by_key(rows, 'malathion')
    assert_nondetect(malathion, 0.5)
    assert (malathion['lod'], malathion['loq']) == (0.00701, 0.02124)
    assert_nondetect(by_key(rows, 'metalaxyl'), 2.0)


def test_continuation_of_an_amount_first_table():
    # The other layout the BelCosta evidence allows: AMT before a limit
    # column that is not labeled LIMIT, continued without a header from
    # MALATHION. r10 read those rows right by accident (the first number
    # after the name is the result) but lost MALATHION to the header.
    header = ['ANALYTE', 'AMT', 'ACTION LEVEL', 'LOD/LOQ', 'PASS/FAIL']
    pages = [
        _Page('PESTICIDES', [[header,
                              ['KRESOXIM-METHYL', 'ND', '0.1 µg/g', '0.00989/0.02997', 'PASS']]]),
        _Page('', [[['MALATHION', 'ND', '0.5 µg/g', '0.00701/0.02124', 'PASS'],
                    ['METALAXYL', 'ND', '2 µg/g', '0.0058/0.01757', 'PASS'],
                    ['PROPICONAZOLE', '<LOQ', '0.1 µg/g', '0.00577/0.01747', 'PASS']]]),
    ]
    rows = parse(pages)
    assert_nondetect(by_key(rows, 'malathion'), 0.5)
    assert_nondetect(by_key(rows, 'metalaxyl'), 2.0)
    propiconazole = by_key(rows, 'propiconazole')
    assert (propiconazole['value'], propiconazole['qualifier'], propiconazole['loq']) == (None, '<LOQ', 0.01747)
    # Without the header to inherit, the column that prints ND is the result.
    layout = tagleaf._infer_layout(pages[1].tables[0], 'pesticides')
    assert (layout['result'], layout['limit'], layout['lod_loq'], layout['status']) == (1, 2, 3, 4)


def test_header_printed_alone_applies_to_the_next_table():
    # r10 skipped the lone header, took ABAMECTIN for the next table's
    # header, and read ACEPHATE as its limit (0.1).
    pages = [
        _Page('PESTICIDES', [[SAFETY]]),
        _Page('', [[pest('ABAMECTIN', '0.1', '0.0117/0.0429'),
                    pest('ACEPHATE', '0.1', '0.0231/0.0851'),
                    pest('BIFENTHRIN', '3', '0.0268/0.0985')]]),
    ]
    rows = parse(pages)
    assert_nondetect(by_key(rows, 'abamectin'), 0.1)
    assert_nondetect(by_key(rows, 'acephate'), 0.1)
    assert_nondetect(by_key(rows, 'bifenthrin'), 3.0)


# ── 5. Units and the percent amount ───────────────────────────────────

def test_percent_amount_is_the_result():
    # r10 read the first AMT column (mg/g) and called it percent.
    table = [['ANALYTE', 'AMT (mg/g)', 'AMT (%)', 'LOD/LOQ', 'PASS/FAIL'],
             ['THCA', '445.938', '44.5938', '0.268/4', ''],
             ['CBD', 'ND', 'ND', '0.31/4', '']]
    rows = parse([_Page('CANNABINOID PROFILE BY HPLC-DAD', [table])])
    thca = by_key(rows, 'thca')
    assert (thca['value'], thca['units']) == (44.5938, 'percent')


# ── Regression: formats the r10 parser already read right ─────────────

RIVER_CANNABINOIDS = [
    POTENCY,
    ['CBD', 'ND', 'ND', '0.031/0.4', ''],
    ['CBDA', '0.0993 %', '0.993 mg/g', '0.0209/0.4', ''],
    ['CBG', '0.1236 %', '1.236 mg/g', '0.0321/0.4', ''],
    ['CBGA', '0.9336 %', '9.336 mg/g', '0.0523/0.4', ''],
    ['CBN', 'ND', 'ND', '0.0317/0.4', ''],
    ['Δ8-THC', 'ND', 'ND', '0.0391/0.4', ''],
    ['Δ9-THC', '0.3693 %', '3.693 mg/g', '0.0429/0.4', ''],
    ['THCA', '44.5938 %', '445.938 mg/g', '0.0268/0.4', ''],
    ['THCV', 'ND', 'ND', '0.0474/0.4', ''],
    ['TOTAL THC**', '39.4781 %', '394.781 mg/g', '', ''],
    ['TOTAL CBD**', '0.0871 %', '0.871 mg/g', '', ''],
]
RIVER_TERPENES = [
    POTENCY,
    ['TOTAL TERPENES', '2.6648 %', '26.648 mg/g', '', ''],
    ['β-MYRCENE', '1.5393 %', '15.393 mg/g', '0.0079/0.05', ''],
    ['α-PINENE', '0.3712 %', '3.712 mg/g', '0.0068/0.05', ''],
    ['LIMONENE', '0.2332 %', '2.332 mg/g', '0.0053/0.05', ''],
    ['TRANS-CARYOPHYLLENE', '0.1791 %', '1.791 mg/g', '0.0124/0.05', ''],
    ['β-PINENE', '0.1771 %', '1.771 mg/g', '0.0045/0.05', ''],
    ['α-HUMULENE', '0.0778 %', '0.778 mg/g', '0.0087/0.05', ''],
    ['LINALOOL', '0.0052 %', '0.052 mg/g', '0.0109/0.05', ''],
    ['CIS-β-OCIMENE', 'ND', 'ND', '0.0034/0.015', ''],
]


def test_regression_cannabinoids():
    rows = parse([_Page('CANNABINOID PROFILE BY HPLC-DAD // DEC 18, 2023',
                        [RIVER_CANNABINOIDS])])
    values = {r['key']: r['value'] for r in rows if r['value']}
    assert values == {
        'cbda': 0.0993, 'cbg': 0.1236, 'cbga': 0.9336,
        'delta_9_thc': 0.3693, 'thca': 44.5938,
    }
    assert {r['key'] for r in rows} == {
        'cbd', 'cbda', 'cbg', 'cbga', 'cbn', 'delta_8_thc', 'delta_9_thc', 'thca', 'thcv'}
    assert all(r['analysis'] == 'cannabinoids' and r['units'] == 'percent' for r in rows)
    thca = by_key(rows, 'thca')
    assert (thca['lod'], thca['loq']) == (0.0268, 0.4)


def test_regression_cannabinoids_without_units_in_cells():
    # COA dd7a0f90... (Pure Cannalyst): THCA 31.0, D9-THC 0.222 percent.
    table = [['Analyte', 'Amt', 'Amt', 'LOD/LOQ', 'Pass/Fail'],
             ['THCa', '31.0', '310', '0.0313/0.0948', ''],
             ['Δ9-THC', '0.222', '2.22', '0.0285/0.0864', ''],
             ['CBDa', '0.0758', '0.758', '0.0258/0.0781', '']]
    rows = parse([_Page('Cannabinoid Profile by UPLC-UV', [table])])
    assert by_key(rows, 'thca')['value'] == 31.0
    assert by_key(rows, 'delta_9_thc')['value'] == 0.222
    assert by_key(rows, 'cbda')['value'] == 0.0758
    assert all(r['units'] == 'percent' for r in rows)


def test_regression_terpenes():
    rows = parse([_Page('TERPENES BY GC-MS // DEC 18, 2023', [RIVER_TERPENES])])
    values = {r['key']: r['value'] for r in rows if r['value']}
    assert values == {
        'total_terpenes': 2.6648, 'beta_myrcene': 1.5393, 'alpha_pinene': 0.3712,
        'limonene': 0.2332, 'trans_caryophyllene': 0.1791, 'beta_pinene': 0.1771,
        'alpha_humulene': 0.0778, 'linalool': 0.0052,
    }
    assert all(r['analysis'] == 'terpenes' and r['units'] == 'percent' for r in rows)
    assert by_key(rows, 'beta_myrcene')['loq'] == 0.05


def test_regression_heavy_metals():
    # COA 1a1452d5... (BelCosta): lead 0.052, mercury 0.012 ug/g.
    table = [SAFETY,
             ['ARSENIC', '0.2 µg/g', '<LOQ', '0.001/0.05', 'PASS'],
             ['CADMIUM', '0.2 µg/g', '<LOQ', '0.0002/0.05', 'PASS'],
             ['LEAD', '0.5 µg/g', '0.052 µg/g', '0.0003/0.05', 'PASS'],
             ['MERCURY', '0.1 µg/g', '0.012 µg/g', '0.0001/0.01', 'PASS']]
    rows = parse([_Page('HEAVY METALS BY ICP-MS // JUN 12, 2024', [table])])
    lead = by_key(rows, 'lead')
    assert (lead['value'], lead['units'], lead['limit'], lead['status']) == (0.052, 'ug/g', 0.5, 'pass')
    assert (lead['lod'], lead['loq']) == (0.0003, 0.05)
    mercury = by_key(rows, 'mercury')
    assert (mercury['value'], mercury['limit'], mercury['loq']) == (0.012, 0.1, 0.01)
    assert all(r['analysis'] == 'heavy_metals' for r in rows)
    assert by_key(rows, 'arsenic')['limit'] == 0.2


def test_regression_microbials_and_mycotoxins():
    micro = [SAFETY,
             ['ASPERGILLUS FLAVUS', '', 'ND', '', 'PASS'],
             ['ASPERGILLUS FUMIGATUS', '', 'ND', '', 'PASS'],
             ['SALMONELLA SPP.', '', 'ND', '', 'PASS'],
             ['SHIGA TOXIN-PRODUCING E. COLI', '', 'ND', '', 'PASS']]
    myco = [SAFETY,
            ['AFLATOXIN B1', '', 'ND', '0.8479/3.1194', ''],
            ['AFLATOXIN B2', '', 'ND', '0.9973/3.6694', ''],
            ['AFLATOXINS', '20 µg/kg', 'ND', '', 'PASS'],
            ['OCHRATOXIN A', '20 µg/kg', 'ND', '3.9103/14.3867', 'PASS']]
    rows = parse([_Page('MICROBIAL CONTAMINANTS // DEC 19, 2023', [micro, myco])])
    flavus = by_key(rows, 'aspergillus_flavus')
    assert (flavus['analysis'], flavus['units'], flavus['status']) == ('microbials', 'cfu/g', 'pass')
    assert by_key(rows, 'stec')['analysis'] == 'microbials'
    assert by_key(rows, 'salmonella_spp')['status'] == 'pass'
    b1 = by_key(rows, 'aflatoxin_b1')
    assert (b1['analysis'], b1['units'], b1['lod'], b1['loq']) == ('mycotoxins', 'ug/kg', 0.8479, 3.1194)
    ochratoxin = by_key(rows, 'ochratoxin_a')
    assert (ochratoxin['limit'], ochratoxin['units'], ochratoxin['status']) == (20.0, 'ug/kg', 'pass')


def test_regression_residual_solvents():
    # COA 0fa8c3c1... (Infinite Chemical Analysis Labs): butane 5.98 and
    # isopropyl alcohol 14.6 ug/g.
    table = [['Analyte', 'Limit', 'Amt', 'LOD/LOQ', 'Pass/Fail'],
             ['Acetone', '5000 µg/g', '<LOQ', '17.1/51.3', 'PASS'],
             ['Butane', '5000 µg/g', '5.98 µg/g', '0.971/4.85', 'PASS'],
             ['Isopropyl alcohol', '5000 µg/g', '14.6 µg/g', '1.28/3.84', 'PASS'],
             ['Toluene', '890 µg/g', '<LOQ', '0.088/0.864', 'PASS'],
             ['Total xylenes', '2170 µg/g', 'ND', '0.0168/0.143', 'PASS']]
    rows = parse([_Page('Residual Solvents by HS-GC-MS', [table])])
    butane = by_key(rows, 'butane')
    assert (butane['value'], butane['units'], butane['limit']) == (5.98, 'ug/g', 5000.0)
    assert (butane['lod'], butane['loq'], butane['status']) == (0.971, 4.85, 'pass')
    assert by_key(rows, 'isopropyl_alcohol')['value'] == 14.6
    assert by_key(rows, 'total_xylenes')['limit'] == 2170.0
    assert all(r['analysis'] == 'residual_solvents' for r in rows)


def test_regression_pesticides_with_header():
    rows = parse([_Page('PESTICIDES', [RIVER_GC, RIVER_LEFT])])
    abamectin = by_key(rows, 'abamectin')
    assert (abamectin['limit'], abamectin['lod'], abamectin['loq']) == (0.1, 0.0117, 0.0429)
    assert (abamectin['units'], abamectin['status']) == ('ug/g', 'pass')
    assert by_key(rows, 'bifenthrin')['limit'] == 3.0
    assert by_key(rows, 'pentachloronitrobenzene')['limit'] == 0.1
    assert len(rows) == 9


def test_regression_foreign_material_with_header():
    # COAs 15c4ba70... and 1a1452d5...: the table with its header row.
    table = [['ANALYTE', 'LIMIT', 'AMT', 'LOD/LOQ', 'PASS/FAIL']] + five_columns([
        ['IMBEDDED FOREIGN MATERIAL', '25 %', 'ND', 'PASS'],
        ['INSECT FRAGMENTS, HAIR, MAMMAL EXCREMENT', '', 'ND', 'PASS'],
        ['MOLD', '25 %', 'ND', 'PASS'],
        ['SAND, SOIL, CINDERS, DIRT', '25 %', 'ND', 'PASS'],
    ])
    rows = parse([_Page('FOREIGN MATERIAL // DEC 19, 2023', [table])])
    assert len(rows) == 4
    for row in rows:
        assert row['analysis'] == 'moisture_foreign_matter'
        assert row['units'] == 'percent'
        assert row['status'] == 'pass'
    assert by_key(rows, 'mold')['limit'] == 25.0
    assert by_key(rows, 'sand_soil_cinders_dirt')['limit'] == 25.0


# ── End to end: parse_tagleaf_coa with a stand-in for pdfplumber ──────

RIVER_FRONT = '\n'.join([
    'PRIDE ANALYTICS DBA 2 RIVER LABS // 32475 DATE PALM DRIVE CATHEDRAL CITY CA 92234 // PH: 7605551234',
    'LICENSE # C8-0000054-LIC',
    'SAMPLE: 014915 (FLOWER) // CLIENT: CI WELLNESS // BATCH: PASS',
    'SAMPLE ID: 2RLS-231215-003',
    'BATCH NO.: 37120423MF',
    'CANNABINOID PROFILE BY HPLC-DAD // DEC 18, 2023',
    'TOTAL THC: 39.4781 %',
    'TOTAL CBD: 0.0871 %',
])


def test_end_to_end_two_river_labs_coa(monkeypatch):
    pesticide_pages = river_pesticide_pages()
    pages = [
        _Page(RIVER_FRONT, [RIVER_CANNABINOIDS]),
        _Page('TERPENES BY GC-MS // DEC 18, 2023', [RIVER_TERPENES]),
        pesticide_pages[0],
        _Page(pesticide_pages[1].text + '\nhttps://lims.tagleaf.com/coa_/abc123 Page 4 of 4',
              pesticide_pages[1].tables),
    ]
    monkeypatch.setattr(tagleaf.pdfplumber, 'open', lambda path: _PDF(pages))
    data = tagleaf.parse_tagleaf_coa(None, 'synthetic.pdf')
    rows = json.loads(data['results'])
    assert data['lab_license_number'] == 'C8-0000054-LIC'
    assert data['product_name'] == '014915'
    assert data['total_thc'] == 39.4781
    assert data['total_terpenes'] == 2.6648
    assert data['lab_results_url'] == 'https://lims.tagleaf.com/coa_/abc123'
    assert json.loads(data['analyses']) == ['cannabinoids', 'heavy_metals', 'pesticides', 'terpenes']
    assert by_key(rows, 'thca')['value'] == 44.5938
    for key, limit in RIVER_LIMIT_ERRORS:
        assert_nondetect(by_key(rows, key), limit)
    assert_nondetect(by_key(rows, 'fipronil'), None)
    assert_nondetect(by_key(rows, 'spiromesifen'), 0.1)
    cadmium = by_key(rows, 'cadmium')
    assert (cadmium['value'], cadmium['qualifier'], cadmium['loq']) == (None, '<LOQ', 0.05)


def test_a_blank_amount_column_does_not_make_the_limit_the_result():
    # Review of 10/14/2026: a continuation without a header whose AMT
    # cells are blank read the one filled column, the limit, as the result.
    rows = [pest('SPIROMESIFEN', '0.1', '0.0117/0.0429', amt=''),
            pest('SPIROTETRAMAT', '0.1', '0.0117/0.0429', amt='')]
    layout = tagleaf._infer_layout(rows, 'pesticides')
    assert (layout['result'], layout['limit']) == (2, 1)
    for row in parse([_Page('', [rows])]):
        assert row['value'] != 0.1, row
