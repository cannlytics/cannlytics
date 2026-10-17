"""
Regression tests for the 10/13/2026 (R11) fixes to sclabs.py
(SC Labs, California: SC Laboratories California LLC).

No real PDFs are used. Each test feeds pdfplumber-like tables (lists of
rows of cell strings) and page text, built from the layouts documented
in sclabs.py and from what a benchmark of 4 SC Labs COAs (2023-2026; a
concentrate, a vape, a concentrate and an edible, read by four Claude
models) implies pdfplumber returns: the column header is not a row of
the table it heads, and a row's columns come merged into three cells,
e.g. ['THCVa', '0.07 / 0.20', '±0.231 4.61 0.461']. The values are the
printed values of those COAs. The bug tests fail on the r10-delivered
parser; the regression tests pin what the r10 parser already read right.

    1. Terpenes were 0.0 mg/g for every analyte (myrcene 1.0049 %).
    2. Cannabinoids were 0.0 for every analyte (thcva 0.461 %, cbg
       0.0100 %, cbc 0.0043 %, thcv 0.0028 %).
    3. Residual solvents were None even when detected (n-pentane 646
       ug/g, ethanol 101 ug/g); limits and PASS/FAIL were dropped.
    4. The first row of every table was dropped (THCa, aldicarb,
       arsenic, ...) and one-row tables (water activity) were skipped.
    5. A non-detect, or a result that could not be read, was 0.0.
    6. Front page: "Total CBD: ND" was 0.0; an edible's "Total THC:
       98.772 mg/unit" was put in the percent field total_thc.

Run:
    pytest tests/test_coas/test_algorithms/test_sclabs_r11.py -v
"""
import json
import logging

import pytest

from cannlytics.data.coas.algorithms import sclabs

LOGGER = 'cannlytics.data.coas.algorithms.sclabs'


# ── pdfplumber stand-ins ──────────────────────────────────────────────

class _Page:
    """A pdfplumber page: text and tables (rows of cell strings)."""

    def __init__(self, text, tables=()):
        self._text = text
        self._tables = [list(table) for table in tables]
        self.width = 612
        self.height = 792

    def extract_text(self):
        return self._text

    def extract_tables(self):
        return self._tables

    def extract_words(self):
        return []


class _PDF:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def row3(name, lod_loq, *columns):
    """A row as pdfplumber merges it: name, LOD/LOQ, the other columns."""
    return [name, lod_loq, ' '.join(c for c in columns if c)]


def parse_tables(page_text, tables):
    """Results of one results page (page 2; page 1 is the summary)."""
    pdf = _PDF([_Page('SAMPLE DETAIL\nsummary'), _Page(page_text, tables)])
    results, analyses = sclabs._parse_results_from_tables(pdf)
    return results, analyses


def by_key(rows, key):
    """The one row with ``key``."""
    found = [r for r in rows if r['key'] == key]
    assert len(found) == 1, f'{key}: {found}'
    return found[0]


def keys(rows, analysis=None):
    return [r['key'] for r in rows if analysis is None or r['analysis'] == analysis]


POTENCY_PAGE = (
    'CANNABINOID TEST RESULTS - 06/30/2023 TERPENOID TEST RESULTS - 06/30/2023'
)
HEADER_POTENCY = [
    'COMPOUND', 'LOD/LOQ\n(mg/g)', 'MEASUREMENT\nUNCERTAINTY\n(mg/g)',
    'RESULT\n(mg/g)', 'RESULT\n(%)',
]
HEADER_LIMITS = [
    'COMPOUND', 'LOD/LOQ\n(µg/g)', 'ACTION LIMIT\n(µg/g)',
    'MEASUREMENT\nUNCERTAINTY\n(µg/g)', 'RESULT\n(µg/g)', 'RESULT',
]
HEADER_MYCOTOXINS = [
    'COMPOUND', 'LOD/LOQ\n(µg/kg)', 'ACTION LIMIT\n(µg/kg)',
    'MEASUREMENT\nUNCERTAINTY\n(µg/kg)', 'RESULT\n(µg/kg)', 'RESULT',
]


# ── 1. Terpenes: read from RESULT (%), not filled in as 0.0 ───────────

# 7f23050d (concentrate, 06/30/2023): sorted by result, largest first.
TERPENES_7F23 = [
    row3('Limonene', '0.005 / 0.016', '±0.3251', '13.003', '1.3003'),
    row3('Myrcene', '0.008 / 0.025', '±0.2512', '10.049', '1.0049'),
    row3('Terpinolene', '0.008 / 0.026', '±0.1370', '5.479', '0.5479'),
    row3('β-Caryophyllene', '0.004 / 0.012', '±0.0984', '3.936', '0.3936'),
    row3('Nerol', '0.003 / 0.011', '±0.0003', '0.013', '0.0013'),
    row3('Sabinene', '0.004 / 0.014', 'N/A', '<LOQ', '<LOQ'),
    row3('Isopulegol', '0.005 / 0.016', 'N/A', 'ND', 'ND'),
]


def check_terpenes_7f23(rows):
    myrcene = by_key(rows, 'myrcene')
    assert myrcene['analysis'] == 'terpenes'
    assert myrcene['value'] == 1.0049
    assert myrcene['units'] == 'percent'
    assert myrcene['qualifier'] == ''
    # LOD/LOQ are printed in mg/g and given in the result's units.
    assert myrcene['lod'] == 0.0008
    assert myrcene['loq'] == 0.0025
    assert by_key(rows, 'terpinolene')['value'] == 0.5479
    assert by_key(rows, 'beta_caryophyllene')['value'] == 0.3936
    assert by_key(rows, 'nerol')['value'] == 0.0013
    sabinene = by_key(rows, 'sabinene')
    assert sabinene['value'] is None
    assert sabinene['qualifier'] == '<LOQ'
    assert sabinene['loq'] == 0.0014
    isopulegol = by_key(rows, 'isopulegol')
    assert isopulegol['value'] is None
    assert isopulegol['qualifier'] == 'ND'


def test_terpenes_are_read_from_the_percent_column():
    # r10: myrcene 0.0 mg/g, terpinolene 0.0 mg/g (cells[-1] holds
    # "±0.2512 10.049 1.0049", the parse failed and was filled as 0.0).
    rows, analyses = parse_tables(POTENCY_PAGE, [TERPENES_7F23])
    check_terpenes_7f23(rows)
    assert 'terpenes' in analyses
    assert all(r['units'] == 'percent' for r in rows)


def test_largest_terpene_first_row_is_kept():
    # r10: the first row (limonene, the largest terpene) was dropped.
    rows, _ = parse_tables(POTENCY_PAGE, [TERPENES_7F23])
    limonene = by_key(rows, 'limonene')
    assert limonene['value'] == 1.3003
    assert limonene['lod'] == 0.0005
    assert limonene['loq'] == 0.0016
    assert len(rows) == len(TERPENES_7F23)


# ── 2. Cannabinoids: every value, not 0.0 ──────────────────────────────

# 7f23050d (concentrate).
CANNABINOIDS_7F23 = [
    row3('THCa', '0.05 / 0.14', '±23.745', '949.81', '94.981'),
    row3('THCVa', '0.07 / 0.20', '±0.231', '4.61', '0.461'),
    row3('∆9-THC', '0.06 / 0.26', 'N/A', 'ND', 'ND'),
    row3('∆8-THC', '0.1 / 0.4', 'N/A', 'ND', 'ND'),
    row3('CBD', '0.07 / 0.29', 'N/A', 'ND', 'ND'),
]

# b5bd2bb5 (edible, 03/07/2026): small detected values.
CANNABINOIDS_B5BD = [
    row3('∆9-THC', '0.002 / 0.014', '±0.064', '2.131', '0.2131'),
    row3('CBG', '0.002 / 0.006', '±0.004', '0.100', '0.0100'),
    row3('CBC', '0.003 / 0.010', '±0.002', '0.043', '0.0043'),
    row3('THCV', '0.002 / 0.012', '±0.001', '0.028', '0.0028'),
    row3('THCa', '0.001 / 0.005', 'N/A', 'ND', 'ND'),
]

# 0c93f027 (concentrate, 09/13/2024).
CANNABINOIDS_0C93 = [
    row3('THCa', '0.05 / 0.14', '±19.781', '791.24', '79.124'),
    row3('∆9-THC', '0.06 / 0.26', '±0.262', '10.48', '1.048'),
    row3('CBGa', '0.1 / 0.2', '±0.230', '9.20', '0.920'),
    row3('CBCa', '0.07 / 0.28', '±0.182', '7.28', '0.728'),
    row3('THCVa', '0.07 / 0.20', '±0.093', '3.73', '0.373'),
    row3('CBDa', '0.02 / 0.19', '±0.039', '1.54', '0.154'),
    row3('CBG', '0.06 / 0.19', 'N/A', 'ND', 'ND'),
]


def test_cannabinoids_concentrate_values():
    # r10: thca missing (first row), thcva 0.0, delta_9_thc 0.0.
    rows, analyses = parse_tables(POTENCY_PAGE, [CANNABINOIDS_7F23])
    thca = by_key(rows, 'thca')
    assert thca['value'] == 94.981
    assert thca['units'] == 'percent'
    assert thca['lod'] == 0.005
    assert thca['loq'] == 0.014
    thcva = by_key(rows, 'thcva')
    assert thcva['value'] == 0.461
    assert thcva['qualifier'] == ''
    for key in ('delta_9_thc', 'delta_8_thc', 'cbd'):
        row = by_key(rows, key)
        assert row['value'] is None, key
        assert row['qualifier'] == 'ND', key
    assert analyses == ['cannabinoids']


def test_cannabinoids_small_detected_values_are_not_zero():
    # r10: cbg 0.0, cbc 0.0, thcv 0.0 (and delta_9_thc, the first row,
    # missing).
    rows, _ = parse_tables(POTENCY_PAGE, [CANNABINOIDS_B5BD])
    assert by_key(rows, 'delta_9_thc')['value'] == 0.2131
    assert by_key(rows, 'cbg')['value'] == 0.01
    assert by_key(rows, 'cbc')['value'] == 0.0043
    assert by_key(rows, 'thcv')['value'] == 0.0028
    assert by_key(rows, 'cbg')['lod'] == 0.0002
    assert by_key(rows, 'thca')['qualifier'] == 'ND'
    assert all(r['units'] == 'percent' for r in rows)


def test_cannabinoids_acids_and_neutrals():
    # r10: delta_9_thc 0.0 (1.048 %), cbga 0.0 (0.920 %), ...
    rows, _ = parse_tables(POTENCY_PAGE, [CANNABINOIDS_0C93])
    expected = {
        'thca': 79.124, 'delta_9_thc': 1.048, 'cbga': 0.92,
        'cbca': 0.728, 'thcva': 0.373, 'cbda': 0.154,
    }
    for key, value in expected.items():
        assert by_key(rows, key)['value'] == value, key
    assert by_key(rows, 'cbg')['value'] is None


def test_cannabinoids_and_terpenes_on_one_page():
    rows, analyses = parse_tables(
        POTENCY_PAGE, [CANNABINOIDS_7F23, TERPENES_7F23])
    assert analyses == ['cannabinoids', 'terpenes']
    assert by_key(rows, 'thcva')['analysis'] == 'cannabinoids'
    check_terpenes_7f23(rows)


def test_percent_column_is_found_beside_a_per_unit_column():
    # A row with RESULT (mg/g), RESULT (%) and a third amount: the
    # percent is the number with the mg/g amount 10 times it on its left.
    rows, _ = parse_tables(POTENCY_PAGE, [[
        row3('∆9-THC', '0.002 / 0.014', '±0.064', '2.131', '0.2131', '98.772'),
        row3('CBG', '0.002 / 0.006', '±0.004', '0.100', '0.0100', '4.635'),
    ]])
    assert by_key(rows, 'delta_9_thc')['value'] == 0.2131
    assert by_key(rows, 'cbg')['value'] == 0.01


def test_percent_column_found_when_printed_before_mg_g():
    rows, _ = parse_tables(POTENCY_PAGE, [[
        row3('THCa', '0.05 / 0.14', '±23.745', '94.981', '949.81'),
        row3('THCVa', '0.07 / 0.20', '±0.231', '0.461', '4.61'),
    ]])
    assert by_key(rows, 'thca')['value'] == 94.981
    assert by_key(rows, 'thcva')['value'] == 0.461


def test_inconsistent_mg_g_and_percent_are_reported(caplog):
    with caplog.at_level(logging.WARNING, logger=LOGGER):
        rows, _ = parse_tables(POTENCY_PAGE, [[
            row3('THCa', '0.05 / 0.14', '±23.745', '949.81', '94.981'),
            row3('THCVa', '0.07 / 0.20', '±0.231', '4.61', '0.731'),
        ]])
    assert by_key(rows, 'thcva')['value'] == 0.731
    assert 'THCVa' in caplog.text and 'is not 10 x' in caplog.text


# ── 3. Residual solvents, pesticides, metals, mycotoxins ──────────────

SOLVENT_PAGE = (
    'CATEGORY 1 RESIDUAL SOLVENT TEST RESULTS - 06/30/2023 '
    'CATEGORY 2 RESIDUAL SOLVENT TEST RESULTS - 06/30/2023'
)
SOLVENTS_CATEGORY_1 = [
    row3('1,2-Dichloroethane', '0.05 / 0.1', '1', 'N/A', 'ND', 'PASS'),
    row3('Benzene', '0.03 / 0.09', '1', 'N/A', 'ND', 'PASS'),
    row3('Chloroform', '0.1 / 0.2', '1', 'N/A', 'ND', 'PASS'),
]
SOLVENTS_CATEGORY_2 = [
    row3('Acetone', '20 / 50', '5000', 'N/A', 'ND', 'PASS'),
    row3('Ethanol', '20 / 50', '5000', '±7.9', '101', 'PASS'),          # b5bd
    row3('n-Butane', '10 / 50', '5000', 'N/A', '<LOQ', 'PASS'),         # 0c93
    row3('2-Propanol (Isopropyl Alcohol)', '10 / 40', '5000', 'N/A', '<LOQ', 'PASS'),
    row3('Methanol', '50 / 200', '3000', 'N/A', 'ND', 'PASS'),
    row3('n-Pentane', '20 / 50', '5000', '±50.4', '646', 'PASS'),       # 7f23
]


def test_detected_residual_solvents_are_read():
    # r10: n_pentane None (646 ug/g), ethanol None (101 ug/g): rows in
    # three cells were not read at all.
    rows, analyses = parse_tables(
        SOLVENT_PAGE, [SOLVENTS_CATEGORY_1, SOLVENTS_CATEGORY_2])
    assert analyses == ['residual_solvents']
    pentane = by_key(rows, 'n_pentane')
    assert pentane['value'] == 646.0
    assert pentane['qualifier'] == ''
    assert pentane['units'] == 'ug/g'
    assert pentane['limit'] == 5000.0
    assert pentane['lod'] == 20.0
    assert pentane['loq'] == 50.0
    assert pentane['status'] == 'pass'
    ethanol = by_key(rows, 'ethanol')
    assert ethanol['value'] == 101.0
    assert ethanol['limit'] == 5000.0


def test_solvents_below_loq_keep_the_qualifier_and_loq():
    rows, _ = parse_tables(SOLVENT_PAGE, [SOLVENTS_CATEGORY_2])
    butane = by_key(rows, 'n_butane')
    assert butane['value'] is None
    assert butane['qualifier'] == '<LOQ'
    assert butane['loq'] == 50.0
    assert butane['limit'] == 5000.0
    propanol = by_key(rows, 'isopropyl_alcohol')
    assert propanol['qualifier'] == '<LOQ'
    assert propanol['loq'] == 40.0


def test_first_solvent_of_each_category_is_kept():
    # r10: 1,2-dichloroethane and acetone (first rows) were dropped.
    rows, _ = parse_tables(
        SOLVENT_PAGE, [SOLVENTS_CATEGORY_1, SOLVENTS_CATEGORY_2])
    dce = by_key(rows, 'dichloroethane_1_2')
    assert dce['value'] is None
    assert dce['qualifier'] == 'ND'
    assert dce['limit'] == 1.0
    assert by_key(rows, 'acetone')['qualifier'] == 'ND'
    assert len(rows) == len(SOLVENTS_CATEGORY_1) + len(SOLVENTS_CATEGORY_2)


PESTICIDE_PAGE = (
    'CATEGORY 1 PESTICIDE TEST RESULTS - 06/30/2023 '
    'CATEGORY 2 PESTICIDE TEST RESULTS - 06/30/2023'
)
PESTICIDES_CATEGORY_1 = [
    row3('Aldicarb', '0.03 / 0.08', '≥ LOD', 'N/A', 'ND', 'PASS'),
    row3('Carbofuran', '0.02 / 0.05', '≥ LOD', 'N/A', 'ND', 'PASS'),
    row3('Chlordane*', '0.03 / 0.08', '≥ LOD', 'N/A', 'ND', 'PASS'),
    row3('Dichlorvos (DDVP)', '0.03 / 0.09', '≥ LOD', 'N/A', 'ND', 'PASS'),
]
# Category 2 is printed in two columns: two tables, the second starting
# at cyfluthrin.
PESTICIDES_CATEGORY_2A = [
    row3('Abamectin', '0.03 / 0.10', '0.1', 'N/A', 'ND', 'PASS'),
    row3('Acephate', '0.02 / 0.07', '0.1', 'N/A', 'ND', 'PASS'),
    row3('Bifenthrin', '0.02 / 0.05', '3', 'N/A', 'ND', 'PASS'),
]
PESTICIDES_CATEGORY_2B = [
    row3('Cyfluthrin', '0.12 / 0.38', '2', 'N/A', 'ND', 'PASS'),
    row3('Cypermethrin', '0.11 / 0.32', '1', 'N/A', 'ND', 'PASS'),
    row3('Diazinon', '0.02 / 0.05', '0.1', 'N/A', 'ND', 'PASS'),
]
PESTICIDE_TABLES = [
    PESTICIDES_CATEGORY_1, PESTICIDES_CATEGORY_2A, PESTICIDES_CATEGORY_2B,
]


def test_first_pesticide_of_each_table_is_kept():
    # r10: aldicarb, abamectin and cyfluthrin were dropped.
    rows, _ = parse_tables(PESTICIDE_PAGE, PESTICIDE_TABLES)
    for key in ('aldicarb', 'abamectin', 'cyfluthrin'):
        row = by_key(rows, key)
        assert row['analysis'] == 'pesticides'
        assert row['value'] is None
        assert row['qualifier'] == 'ND'
    assert len(rows) == sum(len(t) for t in PESTICIDE_TABLES)


def test_pesticide_rows_keep_limits_status_and_qualifier():
    # r10: rows in three cells kept no LOD/LOQ, limit or status.
    rows, _ = parse_tables(PESTICIDE_PAGE, PESTICIDE_TABLES)
    carbofuran = by_key(rows, 'carbofuran')
    assert carbofuran['lod'] == 0.02
    assert carbofuran['loq'] == 0.05
    assert carbofuran['limit'] is None       # "≥ LOD": detect / not detect
    assert carbofuran['status'] == 'pass'
    assert carbofuran['qualifier'] == 'ND'
    bifenthrin = by_key(rows, 'bifenthrin')
    assert bifenthrin['limit'] == 3.0
    assert bifenthrin['lod'] == 0.02
    assert bifenthrin['status'] == 'pass'


def test_detected_pesticide_is_read_after_its_uncertainty():
    rows, _ = parse_tables(PESTICIDE_PAGE, [[
        row3('Abamectin', '0.03 / 0.10', '0.1', 'N/A', 'ND', 'PASS'),
        row3('Myclobutanil', '0.03 / 0.09', '0.1', '±0.011', '0.142', 'FAIL'),
        row3('Aldicarb', '0.03 / 0.08', '≥ LOD', '±0.004', '0.05', 'FAIL'),
    ]])
    myclobutanil = by_key(rows, 'myclobutanil')
    assert myclobutanil['value'] == 0.142
    assert myclobutanil['limit'] == 0.1
    assert myclobutanil['status'] == 'fail'
    aldicarb = by_key(rows, 'aldicarb')
    assert aldicarb['value'] == 0.05
    assert aldicarb['limit'] is None


def test_an_action_limit_is_never_read_as_the_result():
    # A row with one bare number and no uncertainty: the number may be
    # the action limit of a blank result, so the result is left unread.
    rows, _ = parse_tables(PESTICIDE_PAGE, [[
        row3('Abamectin', '0.03 / 0.10', '0.1', 'N/A', 'ND', 'PASS'),
        row3('Acephate', '0.02 / 0.07', '0.1', 'PASS'),
        row3('Bifenthrin', '0.02 / 0.05', '3', '0.25', 'PASS'),
    ]])
    acephate = by_key(rows, 'acephate')
    assert acephate['value'] is None
    assert acephate['qualifier'] == ''
    assert acephate['limit'] == 0.1
    # Two numbers: the action limit, then the result.
    bifenthrin = by_key(rows, 'bifenthrin')
    assert bifenthrin['value'] == 0.25
    assert bifenthrin['limit'] == 3.0


SAFETY_PAGE = (
    'MYCOTOXIN TEST RESULTS - 06/30/2023 HEAVY METAL TEST RESULTS - 06/30/2023 '
    'MICROBIOLOGY TEST RESULTS - 06/30/2023 FOREIGN MATERIAL TEST RESULTS - 06/30/2023 '
    'WATER ACTIVITY TEST RESULTS - 06/30/2023'
)
MYCOTOXINS = [
    row3('Aflatoxin B1', '2.0 / 6.0', 'N/A', 'ND'),
    row3('Aflatoxin B2', '1.8 / 5.6', 'N/A', 'ND'),
    row3('Aflatoxin G1', '1.0 / 3.1', 'N/A', 'ND'),
    row3('Total Aflatoxin', '', '20', 'N/A', 'ND', 'PASS'),
    row3('Ochratoxin A', '6.3 / 19.2', '20', 'N/A', 'ND', 'PASS'),
]
HEAVY_METALS = [
    row3('Arsenic', '0.02 / 0.1', '0.2', 'N/A', 'ND', 'PASS'),
    row3('Cadmium', '0.02 / 0.05', '0.2', 'N/A', 'ND', 'PASS'),
    row3('Lead', '0.04 / 0.1', '0.5', 'N/A', 'ND', 'PASS'),
    row3('Mercury', '0.002 / 0.01', '0.1', 'N/A', 'ND', 'PASS'),
]
MICROBIOLOGY = [
    ['Shiga toxin-producing Escherichia coli', 'Not Detected in 1g', 'ND PASS'],
    ['Salmonella spp.', 'Not Detected in 1g', 'ND PASS'],
    ['Aspergillus fumigatus', 'Not Detected in 1g', 'ND PASS'],
    ['Aspergillus flavus', 'Not Detected in 1g', 'ND PASS'],
]
# 0c93f027: area rows "ND", counts "0".
FOREIGN_MATERIAL = [
    ['Total Sample Area Covered by Sand, Soil, Cinders, or Dirt', '> 25%', 'ND PASS'],
    ['Total Sample Area Covered by Mold', '> 25%', 'ND PASS'],
    ['Insect Fragment Count', '> 1 per 3 grams', '0 PASS'],
    ['Hair Count', '> 1 per 3 grams', '0 PASS'],
    ['Mammalian Excreta Count', '> 1 per 3 grams', '0 PASS'],
]
WATER_ACTIVITY = [
    row3('Water Activity', '0.03 / 0.15', '0.85', '±0.02', '0.54', 'PASS'),
]
SAFETY_TABLES = [
    MYCOTOXINS, HEAVY_METALS, MICROBIOLOGY, FOREIGN_MATERIAL, WATER_ACTIVITY,
]


def test_first_row_of_safety_tables_is_kept():
    # r10: aflatoxin B1, arsenic, STEC and the sand/soil area row (each
    # its table's first row) were dropped.
    rows, _ = parse_tables(SAFETY_PAGE, SAFETY_TABLES)
    b1 = by_key(rows, 'aflatoxin_b1')
    assert b1['analysis'] == 'mycotoxins'
    assert b1['qualifier'] == 'ND'
    assert b1['units'] == 'ug/kg'
    assert b1['lod'] == 2.0
    assert b1['loq'] == 6.0
    assert b1['status'] == ''
    arsenic = by_key(rows, 'arsenic')
    assert arsenic['qualifier'] == 'ND'
    assert arsenic['limit'] == 0.2
    assert arsenic['status'] == 'pass'
    stec = by_key(rows, 'stec')
    assert stec['analysis'] == 'microbials'
    assert stec['value'] is None
    assert stec['qualifier'] == 'ND'
    assert stec['status'] == 'pass'
    sand = by_key(rows, 'sand_soil_coverage')
    assert sand['analysis'] == 'foreign_matter'
    assert sand['qualifier'] == 'ND'


def test_one_row_water_activity_table_is_read():
    # r10: a one-row table was skipped (len(table) < 2).
    rows, analyses = parse_tables(SAFETY_PAGE, SAFETY_TABLES)
    aw = by_key(rows, 'water_activity')
    assert aw['analysis'] == 'water_activity'
    assert aw['value'] == 0.54
    assert aw['units'] == 'aw'
    assert aw['limit'] == 0.85
    assert aw['lod'] == 0.03
    assert aw['loq'] == 0.15
    assert aw['status'] == 'pass'
    assert 'water_activity' in analyses


def test_one_row_table_of_an_unknown_analyte_is_not_read():
    rows, _ = parse_tables(SAFETY_PAGE, [
        [['Report notes', '1 / 2', 'see page 1']],
    ])
    assert rows == []


def test_total_aflatoxin_without_lod_loq_keeps_its_limit():
    rows, _ = parse_tables(SAFETY_PAGE, [MYCOTOXINS])
    total = by_key(rows, 'total_aflatoxin')
    assert total['qualifier'] == 'ND'
    assert total['limit'] == 20.0
    assert total['lod'] is None and total['loq'] is None
    assert total['status'] == 'pass'


def test_foreign_material_limit_is_not_the_result():
    # 7f23050d prints the area rows and counts without a result ("N/A",
    # read as 'NR'). r10: 0.0; a reading split at "> 25%" gives 25.
    rows, _ = parse_tables(SAFETY_PAGE, [[
        ['Total Sample Area Covered by Sand, Soil, Cinders, or Dirt', '> 25%', 'N/A PASS'],
        ['Total Sample Area Covered by Mold', '> 25%', 'N/A PASS'],
        ['Insect Fragment Count', '> 1 per 3 grams', 'N/A PASS'],
        ['Hair Count', '> 1 per 3 grams', 'PASS'],
    ]])
    for row in rows:
        assert row['value'] is None, row
        assert row['status'] == 'pass'
    assert by_key(rows, 'mold_coverage')['qualifier'] == 'NR'
    assert by_key(rows, 'insect_fragment_count')['qualifier'] == 'NR'
    assert by_key(rows, 'hair_count')['qualifier'] == ''   # blank: unread


def test_detected_pathogen_is_kept():
    rows, _ = parse_tables(SAFETY_PAGE, [[
        ['Salmonella spp.', 'Not Detected in 1g', 'ND PASS'],
        ['Aspergillus niger', 'Not Detected in 1g', 'Detected FAIL'],
    ]])
    niger = by_key(rows, 'aspergillus_niger')
    assert niger['value'] is None
    assert niger['qualifier'] == 'detected'
    assert niger['status'] == 'fail'


# ── 4. Where the column header is ─────────────────────────────────────

def test_header_given_as_a_table_of_its_own():
    # The header extracted as a one-row table before the data.
    # r10: the header table was skipped, and the data's first row taken
    # for a header (thca dropped).
    rows, _ = parse_tables(POTENCY_PAGE, [[HEADER_POTENCY], CANNABINOIDS_7F23])
    assert by_key(rows, 'thca')['value'] == 94.981
    assert by_key(rows, 'thcva')['value'] == 0.461
    assert len(rows) == len(CANNABINOIDS_7F23)


def test_header_of_another_section_does_not_set_units():
    # Two-column page, headers extracted as tables ahead of the data:
    # left header, right header, left data, right data.
    rows, _ = parse_tables(PESTICIDE_PAGE + ' MYCOTOXIN TEST RESULTS - 06/30/2023', [
        [HEADER_LIMITS], [HEADER_MYCOTOXINS], PESTICIDES_CATEGORY_2A, MYCOTOXINS,
    ])
    assert {r['units'] for r in rows if r['analysis'] == 'pesticides'} == {'ug/g'}
    assert {r['units'] for r in rows if r['analysis'] == 'mycotoxins'} == {'ug/kg'}
    assert by_key(rows, 'abamectin')['qualifier'] == 'ND'
    rows, _ = parse_tables(POTENCY_PAGE, [
        [HEADER_LIMITS], CANNABINOIDS_7F23,
    ])
    thca = by_key(rows, 'thca')
    assert (thca['value'], thca['units'], thca['lod']) == (94.981, 'percent', 0.005)


def test_header_merged_into_the_first_row():
    # No line between the header and the first row: one row, both.
    # r10: the merged row was taken for the header (thca dropped).
    merged = [h + '\n' + v for h, v in zip(
        HEADER_POTENCY,
        ['THCa', '0.05 / 0.14', '±23.745', '949.81', '94.981'],
    )]
    table = [merged] + [
        ['THCVa', '0.07 / 0.20', '±0.231', '4.61', '0.461'],
        ['CBD', '0.07 / 0.29', 'N/A', 'ND', 'ND'],
    ]
    rows, _ = parse_tables(POTENCY_PAGE, [table])
    thca = by_key(rows, 'thca')
    assert thca['name'] == 'THCa'
    assert thca['value'] == 94.981
    assert thca['lod'] == 0.005
    assert by_key(rows, 'thcva')['value'] == 0.461
    assert by_key(rows, 'cbd')['qualifier'] == 'ND'
    assert len(rows) == 3


def test_microbiology_header_merged_into_the_first_row():
    table = [
        ['COMPOUND\nHair Count', 'ACTION LIMIT\n> 1 per 3 grams', 'RESULT\n0', 'RESULT\nPASS'],
        ['Insect Fragment Count', '> 1 per 3 grams', '0', 'PASS'],
    ]
    rows, _ = parse_tables(SAFETY_PAGE, [table])
    hair = by_key(rows, 'hair_count')
    assert hair['value'] == 0.0
    assert hair['status'] == 'pass'
    assert by_key(rows, 'insect_fragment_count')['value'] == 0.0


def test_section_title_row_in_a_table_is_not_an_analyte():
    table = [
        ['CANNABINOID TEST RESULTS - 06/30/2023', None, None],
        *CANNABINOIDS_7F23,
    ]
    rows, _ = parse_tables(POTENCY_PAGE, [table])
    assert keys(rows) == ['thca', 'thcva', 'delta_9_thc', 'delta_8_thc', 'cbd']


# ── 5. Non-detects and unreadable results are not 0.0 ─────────────────

def test_documented_layout_reads_percent_and_keeps_nondetects():
    # The documented layout: the header is the table's first row and
    # each column is its own cell. r10: non-detects were 0.0, and
    # terpenes were read from mg/g.
    table = [HEADER_POTENCY] + [
        ['Myrcene', '0.008 / 0.025', '±0.2512', '10.049', '1.0049'],
        ['Sabinene', '0.004 / 0.014', 'N/A', '<LOQ', '<LOQ'],
        ['Camphor', '0.006 / 0.019', 'N/A', 'ND', 'ND'],
    ]
    rows, _ = parse_tables(POTENCY_PAGE, [table])
    assert keys(rows) == ['myrcene', 'sabinene', 'camphor']
    myrcene = by_key(rows, 'myrcene')
    assert (myrcene['value'], myrcene['units']) == (1.0049, 'percent')
    assert (myrcene['lod'], myrcene['loq']) == (0.0008, 0.0025)
    camphor = by_key(rows, 'camphor')
    assert camphor['value'] is None
    assert camphor['qualifier'] == 'ND'
    assert by_key(rows, 'sabinene')['qualifier'] == '<LOQ'


def test_header_names_a_percent_lod_loq_column():
    header = ['COMPOUND', 'LOD/LOQ\n(%)', 'MEASUREMENT\nUNCERTAINTY\n(%)',
              'RESULT\n(mg/g)', 'RESULT\n(%)']
    table = [header, ['Myrcene', '0.0008 / 0.0025', '±0.0251', '10.049', '1.0049']]
    rows, _ = parse_tables(POTENCY_PAGE, [table])
    myrcene = by_key(rows, 'myrcene')
    assert (myrcene['value'], myrcene['lod'], myrcene['loq']) == (1.0049, 0.0008, 0.0025)


def test_unreadable_result_is_none_not_zero():
    # r10: a cannabinoid whose result cells are blank was 0.0.
    rows, _ = parse_tables(POTENCY_PAGE, [[
        row3('THCa', '0.05 / 0.14', '±23.745', '949.81', '94.981'),
        ['CBN', '0.1 / 0.3', ''],
    ]])
    cbn = by_key(rows, 'cbn')
    assert cbn['value'] is None
    assert cbn['qualifier'] == ''


def test_printed_zero_is_zero():
    rows, _ = parse_tables(POTENCY_PAGE, [[
        row3('THCa', '0.05 / 0.14', '±23.745', '949.81', '94.981'),
        row3('CBN', '0.1 / 0.3', 'N/A', '0.00', '0.000'),
    ]])
    cbn = by_key(rows, 'cbn')
    assert cbn['value'] == 0.0
    assert cbn['qualifier'] == ''


def test_every_result_row_carries_a_qualifier():
    rows, _ = parse_tables(SAFETY_PAGE, SAFETY_TABLES)
    rows += parse_tables(POTENCY_PAGE, [CANNABINOIDS_7F23])[0]
    for row in rows:
        assert set(row) >= {
            'analysis', 'key', 'name', 'value', 'qualifier', 'units',
            'lod', 'loq', 'limit', 'status'}
        if row['value'] is None:
            assert row['qualifier'] in ('ND', '<LOQ', 'NR', 'detected', ''), row


# ── 6. Front page totals ──────────────────────────────────────────────

FRONT_PAGE_7F23 = """\
SC LABS
DATE ISSUED 06/30/2023 | OVERALL BATCH RESULT: PASS
SAMPLE NAME: Citrus Gas (1g)
Concentrate, Inhalable
CULTIVATOR / MANUFACTURER DISTRIBUTOR
Business Name: Central Coast Ag Products, LLC
License Number: CDPH-10003156
Address: 1201 West Chestnut Ave. Lompoc, CA 93436
SAMPLE DETAIL
Batch Number: 230001317 Sample ID: 230627L045
Date Collected: 06/27/2023 Date Received: 06/28/2023
Batch Size: 2000.0 units Sample Size: 12.0 units
Unit Mass: 1 grams per Unit
CANNABINOID ANALYSIS - SUMMARY
Sum of Cannabinoids: 95.442 % Total Cannabinoids: 83.702 %
Total THC: 83.298 % Total CBD: ND
Total CBG: ND Total THCV: 0.404 %
Total Terpenoids: 4.1713 %
SAFETY ANALYSIS - SUMMARY
Pesticides: PASS Mycotoxins: PASS Residual Solvents: PASS
Heavy Metals: PASS Microbiology: PASS Foreign Material: PASS
These results relate only to the sample tested.
CoA ID: 230627L045-001
SC Laboratories California LLC. | 100 Pioneer Street, Suite E, Santa Cruz, CA 95060 | sclabs.com
"""

FRONT_PAGE_B5BD = """\
DATE ISSUED 03/07/2026 | OVERALL BATCH RESULT: PASS
SAMPLE NAME: Kiva Lost Farm Chew Dragonfruit
Edible, Gummy
SAMPLE DETAIL
Batch Number: 26033CDC01TCD Sample ID: 260305S104
Date Collected: 03/05/2026 Date Received: 03/06/2026
CANNABINOID ANALYSIS - SUMMARY
Total THC: 98.772 mg/unit Total CBD: ND
Sum of Cannabinoids: 106.698 mg/unit Total Cannabinoids: 106.698 mg/unit
Total CBG: 4.635 mg/unit
SAFETY ANALYSIS - SUMMARY
Pesticides: PASS
CoA ID: 260305S104-001
sclabs.com
"""


def test_front_page_total_cbd_nondetect_is_not_zero():
    # r10: total_cbd 0.0 for "Total CBD: ND".
    obs = sclabs._parse_front_page_metadata(FRONT_PAGE_7F23)
    assert obs.get('total_cbd') is None
    assert obs.get('total_cbg') is None
    assert obs['total_thc'] == 83.298


def test_front_page_per_unit_totals_are_not_percents():
    # r10: total_thc 98.772 (mg/unit) in the percent field.
    obs = sclabs._parse_front_page_metadata(FRONT_PAGE_B5BD)
    assert obs.get('total_thc') is None
    assert obs.get('total_cbd') is None
    assert obs.get('total_cannabinoids') is None
    assert obs['total_thc_per_unit'] == 98.772
    assert obs['total_cannabinoids_per_unit'] == 106.698
    assert obs['sum_of_cannabinoids_per_unit'] == 106.698
    assert obs['total_cbg_per_unit'] == 4.635


def test_regression_front_page_totals_in_other_units_are_not_percents():
    obs = sclabs._parse_front_page_metadata(
        'Total THC: 832.98 mg/g Total Cannabinoids: 83.7\nTotal CBD: 0.135 %')
    assert obs.get('total_thc') is None
    assert obs.get('total_cannabinoids') is None
    assert obs['total_cbd'] == 0.135


def test_regression_front_page_metadata():
    obs = sclabs._parse_front_page_metadata(FRONT_PAGE_7F23)
    assert obs['date_tested'] == '2023-06-30'
    assert obs['status'] == 'pass'
    assert obs['product_name'] == 'Citrus Gas (1g)'
    assert obs['product_type'] == 'Concentrate, Inhalable'
    assert obs['batch_number'] == '230001317'
    assert obs['sample_id'] == '230627L045'
    assert obs['date_collected'] == '2023-06-27'
    assert obs['date_received'] == '2023-06-28'
    assert obs['total_thc'] == 83.298
    assert obs['total_cannabinoids'] == 83.702
    assert obs['sum_of_cannabinoids'] == 95.442
    assert obs['total_thcv'] == 0.404
    assert obs['total_terpenes'] == 4.1713
    assert obs['pesticides_status'] == 'pass'
    assert obs['microbials_status'] == 'pass'
    assert obs['coa_id'] == '230627L045-001'


# ── 7. The whole COA, through parse_sc_labs_coa ───────────────────────

def coa_pages():
    return [
        _Page(FRONT_PAGE_7F23),
        _Page(POTENCY_PAGE, [CANNABINOIDS_7F23, TERPENES_7F23]),
        _Page(PESTICIDE_PAGE, PESTICIDE_TABLES),
        _Page(SOLVENT_PAGE + ' ' + SAFETY_PAGE, [
            MYCOTOXINS, SOLVENTS_CATEGORY_1, SOLVENTS_CATEGORY_2,
            HEAVY_METALS, MICROBIOLOGY, FOREIGN_MATERIAL,
        ]),
    ]


@pytest.fixture
def fake_pdfplumber(monkeypatch):
    monkeypatch.setattr(
        sclabs.pdfplumber, 'open', lambda path, *a, **k: _PDF(coa_pages()))


def test_parse_sc_labs_coa_end_to_end(fake_pdfplumber):
    # r10: thcva 0.0, myrcene 0.0 mg/g, n-pentane None, thca missing,
    # total_cbd 0.0.
    data = sclabs.parse_sc_labs_coa(None, '/tmp/230627L045.pdf')
    results = json.loads(data['results'])
    analyses = json.loads(data['analyses'])
    assert by_key(results, 'thca')['value'] == 94.981
    assert by_key(results, 'thcva')['value'] == 0.461
    assert by_key(results, 'myrcene')['value'] == 1.0049
    assert by_key(results, 'myrcene')['units'] == 'percent'
    assert by_key(results, 'n_pentane')['value'] == 646.0
    assert by_key(results, 'aldicarb')['qualifier'] == 'ND'
    assert by_key(results, 'arsenic')['qualifier'] == 'ND'
    assert data.get('total_cbd') is None
    assert data['total_thc'] == 83.298
    assert data['total_terpenes'] == 4.1713
    assert data['product_name'] == 'Citrus Gas (1g)'
    assert data['lab'] == 'SC Labs'
    assert data['coa_pdf'] == '230627L045.pdf'
    for analysis in ('cannabinoids', 'terpenes', 'pesticides', 'mycotoxins',
                     'residual_solvents', 'heavy_metals', 'microbials',
                     'foreign_matter'):
        assert analysis in analyses, analysis
    # No non-detect is coded 0.0; the only zeros are printed counts.
    zeros = [r['key'] for r in results if r['value'] == 0.0]
    assert sorted(zeros) == [
        'hair_count', 'insect_fragment_count', 'mammalian_excreta_count']


def test_total_terpenes_is_summed_from_percent_results(monkeypatch):
    # Without a front-page total, total_terpenes is the sum of the
    # percent results (r10 summed mg/g results, which were all 0.0).
    front = FRONT_PAGE_7F23.replace('Total Terpenoids: 4.1713 %\n', '')
    pages = [_Page(front), _Page(POTENCY_PAGE, [TERPENES_7F23])]
    monkeypatch.setattr(sclabs.pdfplumber, 'open', lambda path, *a, **k: _PDF(pages))
    data = sclabs.parse_sc_labs_coa(None, '/tmp/x.pdf')
    assert data['total_terpenes'] == round(1.3003 + 1.0049 + 0.5479 + 0.3936 + 0.0013, 4)


# ── Regression: formats the r10 parser already read right ─────────────

def test_regression_pesticide_nondetects_merged_cells():
    rows, analyses = parse_tables(PESTICIDE_PAGE, PESTICIDE_TABLES)
    assert analyses == ['pesticides']
    for key in ('carbofuran', 'chlordane', 'dichlorvos', 'acephate',
                'bifenthrin', 'cypermethrin', 'diazinon'):
        row = by_key(rows, key)
        assert row['analysis'] == 'pesticides', key
        assert row['value'] is None, key
        assert row['units'] == 'ug/g', key


def test_regression_heavy_metal_and_mycotoxin_nondetects():
    rows, _ = parse_tables(SAFETY_PAGE, [MYCOTOXINS, HEAVY_METALS])
    for key in ('cadmium', 'lead', 'mercury'):
        row = by_key(rows, key)
        assert (row['analysis'], row['value'], row['units']) == ('heavy_metals', None, 'ug/g')
    for key in ('aflatoxin_b2', 'aflatoxin_g1', 'total_aflatoxin', 'ochratoxin_a'):
        row = by_key(rows, key)
        assert (row['analysis'], row['value'], row['units']) == ('mycotoxins', None, 'ug/kg')


def test_regression_solvent_nondetects():
    rows, _ = parse_tables(SOLVENT_PAGE, [SOLVENTS_CATEGORY_1, SOLVENTS_CATEGORY_2])
    for key in ('benzene', 'chloroform', 'methanol'):
        row = by_key(rows, key)
        assert (row['analysis'], row['value'], row['units']) == ('residual_solvents', None, 'ug/g')


def test_regression_microbial_nondetects():
    rows, analyses = parse_tables(SAFETY_PAGE, [MICROBIOLOGY])
    assert analyses == ['microbials']
    for key in ('salmonella_spp', 'aspergillus_fumigatus', 'aspergillus_flavus'):
        row = by_key(rows, key)
        assert row['analysis'] == 'microbials'
        assert not row['value']
        assert row['status'] == 'pass'


def test_regression_foreign_material_counts():
    rows, _ = parse_tables(SAFETY_PAGE, [FOREIGN_MATERIAL])
    for key in ('hair_count', 'mammalian_excreta_count'):
        row = by_key(rows, key)
        assert row['analysis'] == 'foreign_matter'
        assert row['value'] == 0.0
        assert row['status'] == 'pass'
    assert not by_key(rows, 'mold_coverage')['value']


def test_regression_documented_pesticide_layout():
    table = [HEADER_LIMITS] + [
        ['Aldicarb', '0.03 / 0.08', '≥ LOD', 'N/A', 'ND', 'PASS'],
        ['Carbofuran', '0.02 / 0.05', '≥ LOD', 'N/A', 'ND', 'PASS'],
        ['Abamectin', '0.03 / 0.10', '0.1', 'N/A', 'ND', 'PASS'],
    ]
    rows, _ = parse_tables(PESTICIDE_PAGE, [table])
    assert keys(rows) == ['aldicarb', 'carbofuran', 'abamectin']
    aldicarb = by_key(rows, 'aldicarb')
    assert not aldicarb['value']
    assert (aldicarb['lod'], aldicarb['loq'], aldicarb['limit']) == (0.03, 0.08, None)
    assert aldicarb['status'] == 'pass'
    abamectin = by_key(rows, 'abamectin')
    assert not abamectin['value']
    assert (abamectin['lod'], abamectin['loq'], abamectin['limit']) == (0.03, 0.1, 0.1)
    assert abamectin['units'] == 'ug/g'


def test_regression_documented_cannabinoid_layout():
    table = [HEADER_POTENCY] + [
        ['THCa', '0.05 / 0.14', '±23.745', '949.81', '94.981'],
        ['THCVa', '0.07 / 0.20', '±0.231', '4.61', '0.461'],
    ]
    rows, _ = parse_tables(POTENCY_PAGE, [table])
    assert by_key(rows, 'thca')['value'] == 94.981
    assert by_key(rows, 'thcva')['value'] == 0.461
    assert by_key(rows, 'thca')['units'] == 'percent'


def test_regression_skips_totals_and_per_unit_rows():
    rows, _ = parse_tables(POTENCY_PAGE, [CANNABINOIDS_7F23 + [
        ['Total THC', '', '832.98 83.298'],
        ['SUM OF CANNABINOIDS', '', '954.42 95.442'],
        ['∆9-THC per Unit', '', '1100 mg/unit ND PASS'],
    ]])
    found = keys(rows)
    assert {'thcva', 'delta_9_thc', 'delta_8_thc', 'cbd'} <= set(found)
    assert not [k for k in found if k.startswith(('total', 'sum')) or 'per_unit' in k]
