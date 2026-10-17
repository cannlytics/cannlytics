"""
Regression tests for the 10/13/2026 (R11) fixes to kaycha.py
(Kaycha Labs COA parser: FL Davie/Gainesville, NY Albany, AZ Tempe).

No real PDFs are used. Each test feeds synthetic page text, built from
the row layouts documented in kaycha.py and from what a benchmark of 12
Kaycha COAs (read by four Claude models) implies the printed lines are,
to a section function, or drives parse_kaycha_pdf through a stand-in
for pdfplumber. The bug tests fail on the r10-delivered parser; the
regression tests pin formats that the r10 parser already read right.

    1. Tabular (NY/AZ) rows: a non-detect was reported as its action
       limit (AZ "ACEPHATE ppm 0.0100 0.2000 0.4 PASS ND" -> 0.4).
    2. FL-layout section rows: "ACETONE 75.000 ppm 750 PASS ND" -> 750.
    3. NY terpenes: mg/unit read as percent (limonene 5.1 for 0.51%).
    4. NY cannabinoids: values shifted two analytes to the left.
    5. "<0.1000" read as the number 0.1 instead of a '<LOQ' qualifier.

Run:
    pytest tests/test_coas/test_algorithms/test_kaycha_r11.py -v
"""
import json
import logging

import pytest

from cannlytics.data.coas.algorithms import kaycha

LOGGER = 'cannlytics.data.coas.algorithms.kaycha'


def by_key(rows, key):
    """The one row with ``key``."""
    found = [r for r in rows if r['key'] == key]
    assert len(found) == 1, f'{key}: {found}'
    return found[0]


# ── 1. Tabular rows: the result is not the last number ────────────────

AZ_PESTICIDES = """\
Pesticides PASSED
ACEPHATE ppm 0.0100 0.2000 0.4 PASS ND
ACETAMIPRID ppm 0.0050 0.1000 0.2 PASS ND
DICHLORVOS (DDVP) ppm 0.0010 0.0500 0.1 PASS ND
BIFENAZATE ppm 0.0060 0.1000 0.2 FAIL 0.3500
Analyzed by: 1234, 5678
"""


def check_az_pesticides(rows):
    acephate = by_key(rows, 'acephate')
    assert acephate['value'] is None
    assert acephate['qualifier'] == 'ND'
    assert acephate['lod'] == 0.01
    assert acephate['loq'] == 0.2
    assert acephate['limit'] == 0.4
    assert acephate['status'] == 'pass'
    assert acephate['units'] == 'ppm'
    assert by_key(rows, 'acetamiprid')['value'] is None
    assert by_key(rows, 'dichlorvos_ddvp')['value'] is None
    bifenazate = by_key(rows, 'bifenazate')
    assert bifenazate['value'] == 0.35
    assert bifenazate['limit'] == 0.2
    assert bifenazate['status'] == 'fail'


def test_az_pesticide_nondetect_is_not_the_action_limit():
    # r10: acephate 0.4, acetamiprid 0.2 (the action limits).
    check_az_pesticides(kaycha._parse_pesticides_tabular(AZ_PESTICIDES))


def test_az_pesticides_read_from_header_row():
    page = AZ_PESTICIDES.replace(
        'Pesticides PASSED\n',
        'Pesticides PASSED\nANALYTES UNIT LOD LOQ ACTION LEVEL PASS/FAIL RESULT\n',
    )
    check_az_pesticides(kaycha._parse_pesticides_tabular(page))
    assert kaycha._parse_header(
        'ANALYTES UNIT LOD LOQ ACTION LEVEL PASS/FAIL RESULT'
    ) == ['units', 'lod', 'loq', 'limit', 'status', 'result']


def test_az_section_rows_units_first():
    page = (
        'Heavy Metals PASSED\n'
        'ARSENIC ppm 0.0660 0.2000 0.4 PASS ND\n'
        'LEAD ppm 0.1660 0.5000 1 PASS 0.2100\n'
        'Analyzed by: 1\n'
    )
    rows = kaycha._parse_section_tabular(page, 'Heavy Metal', 'heavy_metals', 'ppm')
    arsenic = by_key(rows, 'arsenic')
    assert arsenic['value'] is None  # r10: 0.4
    assert arsenic['qualifier'] == 'ND'
    assert (arsenic['lod'], arsenic['loq'], arsenic['limit']) == (0.066, 0.2, 0.4)
    assert by_key(rows, 'lead')['value'] == 0.21


def test_merged_second_record_does_not_supply_the_result():
    # pdfplumber can merge two table columns into one line; r10 took the
    # last number on the line (BIFENTHRIN's 0.3000) as ACEPHATE's result.
    page = (
        'Pesticides PASSED\n'
        'ACEPHATE 0.1000 ppm 0.4 PASS <0.1000 BIFENTHRIN 0.1000 ppm 0.2 FAIL 0.3000\n'
    )
    acephate = by_key(kaycha._parse_pesticides_tabular(page), 'acephate')
    assert acephate['value'] is None
    assert acephate['qualifier'] == '<LOQ'
    assert acephate['limit'] == 0.4


# The benchmark's two "az:kaycha" COAs with residual-solvent errors
# (da710957..., e71a3381...) are Albany NY COAs (AL sample IDs). Their
# rows read as the action limit (DMSO 5000, ethanol 5000 for 1316.9).
# r10 gives exactly those values for the first printing through
# _parse_section_fl and for the second through _parse_section_tabular;
# which path those COAs take is not known, so both are tested.
NY_SOLVENTS_LIMIT_FIRST = """\
Residual Solvents PASSED
DIMETHYL SULFOXIDE 375.0000 ppm 5000 PASS <375.0000
HEXANE, TOTAL 125.0000 ppm 290 PASS <125.0000
ETHANOL 125.0000 ppm 5000 PASS 1316.9000
1,1,1,2-TETRAFLUOROETHANE 500.0000 ppm 1000 PASS <500.0000
Analyzed by: 1
"""
NY_SOLVENTS_RESULT_FIRST = """\
Residual Solvents PASSED
DIMETHYL SULFOXIDE 375.0000 ppm <LOQ PASS 5000
HEXANE, TOTAL 125.0000 ppm <LOQ PASS 290
ETHANOL 125.0000 ppm 1316.9000 PASS 5000
Analyzed by: 1
"""


@pytest.mark.parametrize('page', [NY_SOLVENTS_LIMIT_FIRST, NY_SOLVENTS_RESULT_FIRST])
@pytest.mark.parametrize('parse', [kaycha._parse_section_fl, kaycha._parse_section_tabular])
def test_ny_residual_solvents_are_not_the_action_limit(page, parse):
    rows = parse(page, 'Residual Solvents', 'residual_solvents', 'ppm')
    dmso = by_key(rows, 'dimethyl_sulfoxide')
    assert dmso['value'] is None
    assert dmso['qualifier'] == '<LOQ'
    assert dmso['loq'] == 375.0 or dmso['lod'] == 375.0
    assert dmso['limit'] == 5000.0
    assert by_key(rows, 'hexane_total')['value'] is None
    ethanol = by_key(rows, 'ethanol')
    assert ethanol['value'] == 1316.9
    assert ethanol['qualifier'] == ''
    assert ethanol['limit'] == 5000.0


def test_ny_rows_label_the_detection_limit_loq():
    rows = kaycha._parse_section_fl(
        NY_SOLVENTS_LIMIT_FIRST, 'Residual Solvents', 'residual_solvents', 'ppm',
        location='albany',
    )
    ethanol = by_key(rows, 'ethanol')
    assert (ethanol['lod'], ethanol['loq']) == (None, 125.0)
    # Names that begin with locants are read (r10 skipped them).
    tfe = by_key(rows, '1_1_1_2_tetrafluoroethane')
    assert (tfe['value'], tfe['qualifier'], tfe['loq']) == (None, '<LOQ', 500.0)


def test_ny_microbial_counts_and_pathogens():
    page = (
        'Microbial PASSED\n'
        'TOTAL AEROBIC BACTERIA 100.0000 CFU/g 10000 PASS <100.0000\n'
        'TOTAL YEAST AND MOLD 100.0000 CFU/g 100000 PASS 400.0000\n'
        'ESCHERICHIA COLI SHIGELLA SPP 1.0000 CFU/g Not Present PASS\n'
        'SALMONELLA SPECIES Not Detected in 1 g PASS\n'
        'Analyzed by: 1\n'
    )
    for parse in (kaycha._parse_section_fl, kaycha._parse_section_tabular):
        rows = parse(page, 'Microbial', 'microbials', 'CFU/g')
        tab = by_key(rows, 'total_aerobic_bacteria')
        assert tab['value'] is None  # r10: 10000 (FL path) or 100.0 (tabular)
        assert (tab['qualifier'], tab['loq'], tab['limit']) == ('<LOQ', 100.0, 10000.0)
        assert by_key(rows, 'total_yeast_and_mold')['value'] == 400.0
        e_coli = by_key(rows, 'e_coli')
        assert (e_coli['value'], e_coli['qualifier'], e_coli['status']) == (None, 'ND', 'pass')
        salmonella = by_key(rows, 'salmonella')
        assert (salmonella['value'], salmonella['qualifier'], salmonella['status']) == (
            None, 'ND', 'pass')


# ── 2. FL-layout sections ─────────────────────────────────────────────

FL_SOLVENTS = """\
Residual Solvents PASSED
ACETONE 75.000 ppm 750 PASS ND
DICHLOROMETHANE 12.500 ppm 125 PASS ND
ETHANOL 500.000 ppm 5000 PASS ND
TOTAL XYLENES 15.000 ppm 150 PASS ND
1,2-DICHLOROETHANE 0.200 ppm 2 PASS ND
Analyzed by: 1
"""


def check_fl_solvents(rows):
    acetone = by_key(rows, 'acetone')
    assert acetone['value'] is None
    assert acetone['qualifier'] == 'ND'
    assert (acetone['lod'], acetone['limit'], acetone['status']) == (75.0, 750.0, 'pass')
    assert by_key(rows, 'ethanol')['value'] is None
    assert by_key(rows, 'dichloromethane')['value'] is None
    assert by_key(rows, 'total_xylenes')['value'] is None
    assert by_key(rows, '1_2_dichloroethane')['value'] is None


def test_fl_residual_solvent_nondetect_is_not_the_action_limit():
    # r10: acetone 750, ethanol 5000 (the action limits).
    rows = kaycha._parse_section_fl(FL_SOLVENTS, 'Residual Solvents', 'residual_solvents', 'ppm')
    check_fl_solvents(rows)


def test_fl_residual_solvents_read_from_header_row():
    page = FL_SOLVENTS.replace(
        'Residual Solvents PASSED\n',
        'Residual Solvents PASSED\nSolvents LOD Units Action Level Pass/Fail Result\n',
    )
    rows = kaycha._parse_section_fl(page, 'Residual Solvents', 'residual_solvents', 'ppm')
    check_fl_solvents(rows)


@pytest.mark.parametrize('header', [
    '', 'Analyte LOD Units Result Pass / Fail Action Level\n',
])
def test_fl_section_with_result_before_status(header):
    # "NAME LOD UNITS RESULT STATUS LIMIT", with or without its header
    # row: the "<10" result is below the LOQ, not a count of 10.
    page = (
        'Microbial PASSED\n' + header +
        'TOTAL YEAST AND MOLD 10 CFU/g <10 PASS 100000\n'
        'ASPERGILLUS NIGER Not Present PASS\n'
        'Analyzed by: 1\n'
    )
    rows = kaycha._parse_section_fl(page, 'Microbial', 'microbials', 'CFU/g')
    tym = by_key(rows, 'total_yeast_and_mold')
    assert tym['value'] is None  # r10: 10.0, the bound read as a count
    assert tym['qualifier'] == '<LOQ'
    assert (tym['lod'], tym['loq'], tym['limit']) == (10.0, 10.0, 100000.0)
    assert by_key(rows, 'aspergillus_niger')['qualifier'] == 'ND'


@pytest.mark.parametrize('row', [
    'WATER ACTIVITY 0.010 aw 0.85 PASS 0.472',
    'WATER ACTIVITY 0.010 aw 0.472 PASS 0.85',
])
def test_fl_two_numbers_a_pass_result_is_below_its_limit(row):
    page = f'Water Activity PASSED\n{row}\nAnalyzed by: 1\n'
    rows = kaycha._parse_section_fl(page, 'Water Activity', 'water_activity', 'aw')
    wa = by_key(rows, 'water_activity')
    assert (wa['value'], wa['limit'], wa['units']) == (0.472, 0.85, 'aw')


def test_fl_failing_solvent_keeps_its_result():
    page = 'Residual Solvents FAILED\nETHANOL 500.000 ppm 5000 FAIL 6200\n'
    ethanol = by_key(
        kaycha._parse_section_fl(page, 'Residual Solvents', 'residual_solvents', 'ppm'),
        'ethanol',
    )
    assert (ethanol['value'], ethanol['limit'], ethanol['status']) == (6200.0, 5000.0, 'fail')


def test_fl_section_skips_lines_that_are_not_rows():
    page = (
        'Heavy Metals PASSED\n'
        'ARSENIC 0.020 ppm 0.2 PASS ND MERCURY 0.020 ppm 0.2 PASS 0.0300\n'
        'DILUTION 10 20\n'
        'Reviewed On : 04/18/24 12:00:00\n'
        'Analyzed by: 1\n'
    )
    rows = kaycha._parse_section_fl(page, 'Heavy Metal', 'heavy_metals', 'ppm')
    assert [r['key'] for r in rows] == ['arsenic']
    # The merged MERCURY record does not supply arsenic's result.
    assert rows[0]['value'] is None and rows[0]['limit'] == 0.2


def test_failing_pathogen_is_kept():
    page = 'Microbial FAILED\nSALMONELLA SPECIFIC GENE Present FAIL\nAnalyzed by: 1\n'
    salmonella = by_key(
        kaycha._parse_section_fl(page, 'Microbial', 'microbials', 'CFU/g'), 'salmonella',
    )
    assert (salmonella['value'], salmonella['qualifier'], salmonella['status']) == (
        None, 'detected', 'fail')


# ── 3. NY terpenes: the percent column ────────────────────────────────

# 553b4b1d... (a 1 g pre-roll): percent after PASS, then mg/unit.
NY_TERPENES_DETECTED = [
    ('LIMONENE', 0.51), ('BETA-CARYOPHYLLENE', 0.47), ('LINALOOL', 0.27),
    ('ALPHA-HUMULENE', 0.15), ('GUAIOL', 0.09), ('BETA-MYRCENE', 0.09),
    ('ALPHA TERPINEOL', 0.07), ('FENCHYL ALCOHOL', 0.06), ('BETA-PINENE', 0.06),
    ('OCIMENE', 0.03), ('ALPHA-BISABOLOL', 0.03), ('ALPHA-PINENE', 0.03),
    ('VALENCENE', 0.02), ('CAMPHENE', 0.01), ('CARYOPHYLLENE OXIDE', 0.01),
]
NY_TERPENES_BELOW_LOQ = ['GERANIOL', 'MENTHOL', 'TERPINOLENE', 'ALPHA-PHELLANDRENE']


def ny_terpene_page(header='', mg_first=False, total=1.9):
    def row(name, loq, pct, mg):
        cells = f'{mg} {pct}' if mg_first else f'{pct} {mg}'
        return f'{name} {loq} 10 PASS {cells}'
    lines = ['Terpenes PASSED']
    if header:
        lines.append(header)
    total_cells = f'{total * 10:.4f} {total:.4f}' if mg_first else f'{total:.4f} {total * 10:.4f}'
    lines.append(f'TOTAL TERPENES 0.1000 11.5 PASS {total_cells}')
    for name, pct in NY_TERPENES_DETECTED:
        lines.append(row(name, '0.0040', f'{pct:.4f}', f'{pct * 10:.4f}'))
    lines.append(row('FARNESENE', '0.0400', '<0.0400', '<0.4000'))
    for name in NY_TERPENES_BELOW_LOQ:
        lines.append(row(name, '0.0040', '<0.0040', '<0.0400'))
    lines.append('Analyzed by: 1')
    return '\n'.join(lines) + '\n'


def check_ny_terpenes(rows, total):
    assert total == 1.9  # r10: 0.1 (the TOTAL TERPENES row's LOQ)
    limonene = by_key(rows, 'limonene')
    assert limonene['value'] == 0.51  # r10: 5.1 (mg/unit)
    assert limonene['units'] == 'percent'
    assert (limonene['loq'], limonene['limit'], limonene['status']) == (0.004, 10.0, 'pass')
    assert by_key(rows, 'beta_caryophyllene')['value'] == 0.47
    farnesene = by_key(rows, 'farnesene')
    assert farnesene['value'] is None  # r10: 0.4 (the LOQ in mg)
    assert (farnesene['qualifier'], farnesene['loq']) == ('<LOQ', 0.04)
    geraniol = by_key(rows, 'geraniol')
    assert (geraniol['value'], geraniol['qualifier'], geraniol['loq']) == (None, '<LOQ', 0.004)
    assert round(sum(r['value'] for r in rows if r['value'] is not None), 4) == 1.9


def test_ny_terpenes_read_the_percent_column(caplog):
    caplog.set_level(logging.WARNING, logger=LOGGER)
    rows, total = kaycha._parse_terpenes_tabular(ny_terpene_page())
    check_ny_terpenes(rows, total)
    assert not [r for r in caplog.records if 'TOTAL TERPENES' in r.getMessage()]


def test_ny_terpenes_header_names_the_percent_column():
    header = 'ANALYTES LOQ ACTION LEVEL PASS/FAIL RESULT (%) RESULT (mg/unit)'
    rows, total = kaycha._parse_terpenes_tabular(ny_terpene_page(header))
    check_ny_terpenes(rows, total)
    # A header that prints mg/unit first is followed.
    header = 'ANALYTES LOQ ACTION LEVEL PASS/FAIL RESULT (mg/unit) RESULT (%)'
    rows, total = kaycha._parse_terpenes_tabular(ny_terpene_page(header, mg_first=True))
    check_ny_terpenes(rows, total)


def test_ny_terpenes_total_mismatch_is_reported(caplog):
    caplog.set_level(logging.WARNING, logger=LOGGER)
    rows, total = kaycha._parse_terpenes_tabular(ny_terpene_page(total=3.8))
    assert total == 3.8
    assert [r for r in caplog.records if 'TOTAL TERPENES' in r.getMessage()]


# ── 4. NY cannabinoids: D10-THC isomer columns ─────────────────────────

NY_NAMES = 'CBC CBD CBDA CBDV CBG CBGA D8-THC CBN D9-THC THCA THCV'


def ny_front_page(header_lines, cells, loq, totals='33.3945% <0.1000 39.1979%'):
    lines = [
        'Kaycha Labs', 'Purple Haze 1g Preroll', 'Purple Haze',
        'Matrix: Flower', 'Sample:AL50827002-001',
        'Cannabinoid', 'Total THC Total CBD Total Cannabinoids', totals,
    ] + header_lines + ['% ' + cells, 'LOQ ' + loq]
    return '\n'.join(lines), lines


# 553b4b1d...: the '%' row leads with (6AR,9R) and (6AR,9S) D10-THC.
CELLS_553B = ('<0.1000 <0.1000 <0.1000 <0.1000 0.1100 <0.1000 0.1499 1.1682 '
              '<0.1000 <0.1000 2.1986 35.5712 <0.1000')
LOQ_553B = ' '.join(['0.1000'] * 13)


def check_553b(rows):
    values = {r['key']: r['value'] for r in rows}
    # r10: cbg 0.11, delta_8_thc 0.1499, cbn 1.1682, thcv 2.1986,
    # delta_9_thc 0.1 and thca 0.1.
    assert values == {
        '9r_delta_10_thc': None, '9s_delta_10_thc': None, 'cbc': None,
        'cbd': None, 'cbda': 0.11, 'cbdv': None, 'cbg': 0.1499,
        'cbga': 1.1682, 'delta_8_thc': None, 'cbn': None,
        'delta_9_thc': 2.1986, 'thca': 35.5712, 'thcv': None,
    }
    cbn = by_key(rows, 'cbn')
    assert (cbn['qualifier'], cbn['loq'], cbn['units']) == ('<LOQ', 0.1, 'percent')
    assert by_key(rows, 'thca')['qualifier'] == ''


@pytest.mark.parametrize('header_lines', [
    ['(6AR,9R) (6AR,9S)', 'D10-THC D10-THC', NY_NAMES],  # isomer lines above
    ['(6AR,9R) (6AR,9S)', NY_NAMES, 'D10-THC D10-THC'],  # 'D10-THC' line below
])
def test_ny_cannabinoids_d10_isomers_lead_the_row(header_lines):
    text, lines = ny_front_page(header_lines, CELLS_553B, LOQ_553B)
    check_553b(kaycha._parse_cannabinoids(text, lines))


def test_ny_cannabinoids_edible_loq_row_aligns_with_the_cells():
    # c9195c64... (gummy): the first cell is the 9R isomer's "<0.0006".
    names = 'CBC CBD CBDA CBDV CBG D8-THC CBGA CBN D9-THC THCA THCV'
    cells = ('<0.0006 <0.0007 <0.0007 0.0007 <0.0007 <0.0007 0.0067 <0.0007 '
             '<0.0007 0.0039 0.1861 <0.0007 0.0033')
    loq = '0.0006 ' + ' '.join(['0.0007'] * 12)
    text, lines = ny_front_page(
        ['(6AR,9R) (6AR,9S)', 'D10-THC D10-THC', names], cells, loq,
        totals='0.1861% 0.0007% 0.2007%',
    )
    rows = kaycha._parse_cannabinoids(text, lines)
    values = {r['key']: r['value'] for r in rows}
    # r10: cbc 0.0006, cbga 0.0067, thca 0.0039, thcv 0.1861.
    assert values == {
        '9r_delta_10_thc': None, '9s_delta_10_thc': None, 'cbc': None,
        'cbd': 0.0007, 'cbda': None, 'cbdv': None, 'cbg': 0.0067,
        'delta_8_thc': None, 'cbga': None, 'cbn': 0.0039,
        'delta_9_thc': 0.1861, 'thca': None, 'thcv': 0.0033,
    }
    assert by_key(rows, '9r_delta_10_thc')['loq'] == 0.0006
    assert by_key(rows, 'cbc')['loq'] == 0.0007


def test_cannabinoid_guard_realigns_unexplained_leading_cells(caplog):
    # No isomer labels in the header: 13 cells for 11 names. The printed
    # Total THC (D9-THC + 0.877 * THCA) picks the alignment.
    caplog.set_level(logging.WARNING, logger=LOGGER)
    text, lines = ny_front_page([NY_NAMES], CELLS_553B, LOQ_553B)
    rows = kaycha._parse_cannabinoids(text, lines)
    values = {r['key']: r['value'] for r in rows}
    assert values['delta_9_thc'] == 2.1986
    assert values['thca'] == 35.5712
    assert values['cbg'] == 0.1499
    assert values['thcv'] is None
    assert len(rows) == 11
    assert [r for r in caplog.records if 'Total THC' in r.getMessage()]


def test_cannabinoid_guard_drops_rows_it_cannot_align(caplog):
    caplog.set_level(logging.WARNING, logger=LOGGER)
    text, lines = ny_front_page(
        [NY_NAMES], CELLS_553B, LOQ_553B, totals='50.0000% <0.1000 39.1979%',
    )
    assert kaycha._parse_cannabinoids(text, lines) == []
    assert [r for r in caplog.records if 'dropped' in r.getMessage()]


def test_cannabinoid_guard_keeps_a_header_explained_alignment(caplog):
    # One cell per name: kept even if the total disagrees (e.g. a total
    # per unit), with a warning.
    caplog.set_level(logging.WARNING, logger=LOGGER)
    text, lines = fl_front_page(totals='70.000% 0.187% 86.44%')
    rows = kaycha._parse_cannabinoids(text, lines)
    assert by_key(rows, 'delta_9_thc')['value'] == 81.295
    assert [r for r in caplog.records if 'keeping' in r.getMessage()]


# ── 5. Qualifiers: "<x" and "ND" are not numbers ──────────────────────

def test_below_loq_result_is_a_qualifier_not_the_limit():
    page = (
        'Pesticides PASSED\n'
        'ACEQUINOCYL 0.1000 ppm 2 PASS <0.1000\n'
        'MYCLOBUTANIL 0.1000 ppm 0.2 PASS < 0.1000\n'
    )
    rows = kaycha._parse_pesticides_tabular(page)
    for key in ('acequinocyl', 'myclobutanil'):
        row = by_key(rows, key)
        assert row['value'] is None  # r10: 0.1
        assert row['qualifier'] == '<LOQ'
        assert row['loq'] == 0.1


def test_below_limit_bound_becomes_the_loq_when_the_row_has_none():
    page = 'BIFENAZATE 0.010 ppm 0.1 PASS <0.010\nCARBARYL 0.010 ppm 0.5 PASS 0\n'
    rows = kaycha._parse_pesticides_fl(page)
    bifenazate = by_key(rows, 'bifenazate')
    assert bifenazate['value'] is None  # r10: 0.01
    assert bifenazate['qualifier'] == '<LOQ'
    assert (bifenazate['lod'], bifenazate['loq']) == (0.01, 0.01)
    carbaryl = by_key(rows, 'carbaryl')
    assert carbaryl['value'] == 0.0 and carbaryl['qualifier'] == ''


def test_parse_number_does_not_read_a_bound_as_a_number():
    assert kaycha._parse_number('<0.100') is None  # r10: 0.1
    assert kaycha._parse_number('0.100') == 0.1
    assert kaycha._parse_number('5,000') == 5000.0
    assert kaycha._parse_number('0') == 0.0
    assert kaycha._parse_result('<0.100') == (None, '<LOQ', 0.1)
    assert kaycha._parse_result('Not Present') == (None, 'ND', None)
    assert kaycha._parse_result('0.0000') == (0.0, '', None)


def test_totals_qualifier_cells_are_none_and_keep_their_place():
    lines = ['Total THC Total CBD Total Cannabinoids', '25.5961% <0.1000 29.7057%']
    totals = kaycha._parse_totals('\n'.join(lines), lines)
    assert totals == {
        'total_thc': 25.5961, 'total_cbd': None, 'total_cannabinoids': 29.7057,
    }  # r10: total_cbd 0.1
    lines = ['Total THC Total CBD Total Cannabinoids', '25.5961% ND 29.7057%']
    totals = kaycha._parse_totals('\n'.join(lines), lines)
    assert totals['total_cbd'] is None  # r10: 29.7057 (total cannabinoids)
    assert totals['total_cannabinoids'] == 29.7057


# ── Regression: formats the r10 parser already read correctly ─────────

FL_PESTICIDES = """\
Pesticides PASSED
Pesticide LOD Units Action Level Pass/Fail Result
TOTAL CONTAMINANT LOAD (PESTICIDES) 0.010 ppm 5 PASS ND
ABAMECTIN B1A 0.010 ppm 0.1 PASS ND
ACEPHATE 0.010 ppm 0.1 PASS ND
BIFENAZATE 0.010 ppm 0.1 PASS 0.052
PENTACHLORONITROBENZENE (PCNB) * 0.010 PPM 0.15 PASS ND
Analyzed by: 1
"""


def test_regression_fl_pesticides():
    rows = kaycha._parse_pesticides_fl(FL_PESTICIDES)
    assert [r['key'] for r in rows] == [
        'abamectin_b1a', 'acephate', 'bifenazate', 'pentachloronitrobenzene_pcnb',
    ]
    abamectin = by_key(rows, 'abamectin_b1a')
    assert abamectin['value'] is None
    assert (abamectin['lod'], abamectin['limit'], abamectin['status'], abamectin['units']) == (
        0.01, 0.1, 'pass', 'ppm')
    assert by_key(rows, 'bifenazate')['value'] == 0.052
    pcnb = by_key(rows, 'pentachloronitrobenzene_pcnb')
    assert (pcnb['value'], pcnb['limit'], pcnb['units']) == (None, 0.15, 'ppm')


def test_regression_fl_microbials_not_present():
    page = (
        'Microbial PASSED\n'
        'Analyte Result Pass / Fail\n'
        'ASPERGILLUS TERREUS Not Present PASS\n'
        'ASPERGILLUS NIGER Not Present PASS\n'
        'SALMONELLA SPECIFIC GENE Not Present PASS\n'
        'Analyzed by: 1\n'
    )
    rows = kaycha._parse_section_fl(page, 'Microbial', 'microbials', 'CFU/g')
    assert [r['key'] for r in rows] == ['aspergillus_terreus', 'aspergillus_niger', 'salmonella']
    for row in rows:
        assert row['value'] is None
        assert row['status'] == 'pass'
        assert row['units'] == 'CFU/g'
        assert row['analysis'] == 'microbials'


def test_regression_ny_pesticides():
    page = (
        'Pesticides PASSED\n'
        'ANALYTES LOQ UNIT ACTION LEVEL PASS/FAIL RESULT\n'
        'PYRETHRINS, TOTAL 0.1000 ppm 1 PASS <0.1000\n'
        'ACEQUINOCYL 0.1000 ppm 2 PASS <0.1000\n'
        'BIFENAZATE 0.1000 ppm 0.2 PASS 0.1500\n'
        'CAPTAN * 0.1000 ppm 1 PASS <0.1000\n'
        'Analyzed by: 1\n'
    )
    rows = kaycha._parse_pesticides_tabular(page)
    assert [r['key'] for r in rows] == ['acequinocyl', 'bifenazate', 'captan']
    bifenazate = by_key(rows, 'bifenazate')
    assert (bifenazate['value'], bifenazate['limit'], bifenazate['status'], bifenazate['units']) == (
        0.15, 0.2, 'pass', 'ppm')
    assert by_key(rows, 'acequinocyl')['limit'] == 2.0


def fl_front_page(totals='81.458% 0.187% 86.44%'):
    lines = [
        'Kaycha Labs', 'SEL,Elite VapeCart,Hwi,Cliq,1.0g', 'Hawaiian',
        'Matrix: Derivative', 'Sample:DA40416001-004',
        'Cannabinoid', 'Total THC Total CBD Total Cannabinoids', totals,
        'D9-THC THCA CBD CBDA D8-THC CBG CBGA CBN THCV CBDV CBC',
        '% 81.295 0.187 0.187 ND 0.353 2.278 ND 0.409 0.523 ND 1.208',
        'mg/g 812.95 1.87 1.87 ND 3.53 22.78 ND 4.09 5.23 ND 12.08',
        'LOD ' + ' '.join(['0.001'] * 11),
    ]
    return '\n'.join(lines), lines


def test_regression_fl_cannabinoids():
    text, lines = fl_front_page()
    rows = kaycha._parse_cannabinoids(text, lines)
    assert {r['key']: r['value'] for r in rows} == {
        'delta_9_thc': 81.295, 'thca': 0.187, 'cbd': 0.187, 'cbda': None,
        'delta_8_thc': 0.353, 'cbg': 2.278, 'cbga': None, 'cbn': 0.409,
        'thcv': 0.523, 'cbdv': None, 'cbc': 1.208,
    }
    assert all(r['lod'] == 0.001 for r in rows)


def test_regression_fl_terpenes():
    page = (
        'Terpenes TESTED\n'
        'LIMONENE 0.007 14.28 1.428\n'
        'BETA-CARYOPHYLLENE 0.007 8.55 0.855\n'
        'BORNEOL 0.013 ND ND\n'
    )
    rows, _ = kaycha._parse_terpenes_fl(page)
    assert {r['key']: r['value'] for r in rows} == {
        'limonene': 1.428, 'beta_caryophyllene': 0.855, 'borneol': None,
    }
    assert by_key(rows, 'borneol')['lod'] == 0.013


# ── End to end: parse_kaycha_pdf with a stand-in for pdfplumber ───────

class _Page:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


class _PDF:
    def __init__(self, pages):
        self.pages = [_Page(t) for t in pages]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def parse_pages(monkeypatch, pages):
    monkeypatch.setattr(kaycha.pdfplumber, 'open', lambda path: _PDF(pages))
    data = kaycha.parse_kaycha_coa(None, 'synthetic.pdf')
    return data, json.loads(data['results'])


def result(rows, analysis, key):
    found = [r for r in rows if r['analysis'] == analysis and r['key'] == key]
    assert len(found) == 1, f'{analysis}/{key}: {found}'
    return found[0]


def test_end_to_end_ny_coa(monkeypatch):
    text, _ = ny_front_page(
        ['(6AR,9R) (6AR,9S)', 'D10-THC D10-THC', NY_NAMES], CELLS_553B, LOQ_553B,
    )
    front = text.replace(
        'Cannabinoid', '1 Winners Circle, Albany, NY 12205\nPASSED\nCannabinoid', 1,
    )
    pesticides = (
        'Kaycha Labs\nPesticides PASSED\n'
        'ACEQUINOCYL 0.1000 ppm 2 PASS <0.1000\n'
        'BIFENAZATE 0.1000 ppm 0.2 PASS 0.1500\nAnalyzed by: 1\n'
    )
    solvents = 'Kaycha Labs\n' + NY_SOLVENTS_LIMIT_FIRST
    data, rows = parse_pages(monkeypatch, [front, ny_terpene_page(), pesticides, solvents])
    assert data['lab_city'] == 'Albany'
    assert data['total_thc'] == 33.3945
    assert data['total_cbd'] is None
    assert data['total_terpenes'] == 1.9
    assert result(rows, 'cannabinoids', 'delta_9_thc')['value'] == 2.1986
    assert result(rows, 'cannabinoids', 'thca')['value'] == 35.5712
    assert result(rows, 'terpenes', 'limonene')['value'] == 0.51
    acequinocyl = result(rows, 'pesticides', 'acequinocyl')
    assert (acequinocyl['value'], acequinocyl['qualifier'], acequinocyl['loq']) == (None, '<LOQ', 0.1)
    dmso = result(rows, 'residual_solvents', 'dimethyl_sulfoxide')
    assert (dmso['value'], dmso['qualifier'], dmso['loq'], dmso['lod']) == (None, '<LOQ', 375.0, None)
    assert result(rows, 'residual_solvents', 'ethanol')['value'] == 1316.9


def test_end_to_end_az_coa(monkeypatch):
    front = '\n'.join([
        'Kaycha Labs', 'TFR1-5_LBR_FWR', 'Lemon Butter Rum', 'Matrix: Flower',
        'Sample:TE60109003-002',
        '1231 W. Warner Road, Suite 105, Tempe, AZ 85284', 'PASSED',
        'Cannabinoid', 'Total THC Total CBD Total Cannabinoids', '25.0786% 0.0421% 29.12%',
        'D9-THC THCA CBD CBDA CBG CBGA CBN D8-THC THCV CBDV CBC',
        '% 0.677 27.824 ND 0.048 0.170 0.401 ND ND ND ND ND',
        'LOD ' + ' '.join(['0.0001'] * 11),
    ])
    metals = (
        'Kaycha Labs\nHeavy Metals PASSED\n'
        'ARSENIC ppm 0.0660 0.2000 0.4 PASS ND\n'
        'LEAD ppm 0.1660 0.5000 1 PASS 0.2100\nAnalyzed by: 1\n'
    )
    data, rows = parse_pages(monkeypatch, [front, 'Kaycha Labs\n' + AZ_PESTICIDES, metals])
    assert data['lab_city'] == 'Tempe'
    acephate = result(rows, 'pesticides', 'acephate')
    assert acephate['value'] is None  # r10: 0.4
    assert (acephate['qualifier'], acephate['limit']) == ('ND', 0.4)
    assert result(rows, 'cannabinoids', 'thca')['value'] == 27.824
    assert result(rows, 'cannabinoids', 'cbd')['qualifier'] == 'ND'
    arsenic = result(rows, 'heavy_metals', 'arsenic')
    assert (arsenic['value'], arsenic['qualifier'], arsenic['lod'], arsenic['loq']) == (
        None, 'ND', 0.066, 0.2)
    assert result(rows, 'heavy_metals', 'lead')['value'] == 0.21


# ── Review of 10/14/2026: limits and LOQs are still never results ─────

def _row(line, **kwargs):
    name, cells = kaycha._split_name(kaycha._tokenize(line))
    return kaycha._read_row(cells, **kwargs)


@pytest.mark.parametrize('line, kwargs, expected', [
    # No limit printed: the cell before the status is the LOQ, not a
    # limit, and the result after the status is not compared with it.
    ('LIMONENE 0.0040 PASS 0.5100 5.1000', {'detection': 'loq', 'terpene': True}, (0.51, None, 0.004)),
    ('BIFENAZATE 0.1000 ppm PASS 0.1500', {'detection': 'loq'}, (0.15, None, 0.1)),
    ('ACEPHATE ppm 0.0100 0.2000 PASS 0.35', {'detection': 'lod'}, (0.35, None, 0.2)),
    # With a limit, both orders still read (the benchmark could not tell
    # which one Albany's residual solvents print).
    ('LIMONENE 0.0040 10 PASS 0.5100 5.1000', {'detection': 'loq', 'terpene': True}, (0.51, 10.0, 0.004)),
    ('ETHANOL 125.0000 ppm 5000 PASS 1316.9000', {'detection': 'loq'}, (1316.9, 5000.0, 125.0)),
    ('ETHANOL 125.0000 ppm 1316.9000 PASS 5000', {'detection': 'loq'}, (1316.9, 5000.0, 125.0)),
])
def test_a_row_without_a_limit_reads_the_cell_after_the_status(line, kwargs, expected):
    row = _row(line, **kwargs)
    assert (row['value'], row['limit'], row['loq']) == expected


def test_a_number_before_the_status_with_nothing_after_it_is_not_read():
    # "ACETONE 75.000 ppm 750 PASS": 750 is the limit or the result.
    assert _row('ACETONE 75.000 ppm 750 PASS', detection='lod') is None
    row = _row('ACETONE 75.000 ppm ND PASS', detection='lod')
    assert (row['value'], row['qualifier']) == (None, 'ND')


def test_the_fl_pesticide_pattern_keeps_its_order_on_a_fail():
    # A FAIL below its limit is the COA's to explain, not a reason to
    # read the limit as the result.
    rows = kaycha._parse_pesticides_fl('MYCLOBUTANIL 0.010 ppm 0.2 FAIL 0.15\n')
    assert [(r['value'], r['limit'], r['status']) for r in rows] == [(0.15, 0.2, 'fail')]


def test_a_failing_pathogen_is_not_its_limit():
    for line, expected in (('SALMONELLA SPECIES Not Detected in 1 g Detected FAIL', ('detected', 'fail')),
                           ('SALMONELLA SPECIES Not Present PASS', ('ND', 'pass'))):
        name, cells = kaycha._split_name(kaycha._tokenize(line))
        row, _ = kaycha._read_word_row(cells, detection='loq')
        assert (row['qualifier'], row['status']) == expected
        assert row['lod'] is None and row['loq'] is None   # "in 1 g" is no detection limit


def test_another_tables_header_does_not_read_the_pesticides():
    page = ('Terpenes TESTED\n'
            'ANALYTES LOQ ACTION LEVEL PASS/FAIL RESULT (%) RESULT (mg/g)\n'
            'LIMONENE 0.0040 10 PASS 0.5100 5.1000\n'
            'Analyzed by: 1\n'
            'Pesticides PASSED\n'
            'ACEPHATE ppm 0.0100 0.2000 0.4 PASS ND\n'
            'BIFENAZATE ppm 0.0060 0.1000 0.2 FAIL 0.3500\n')
    rows = kaycha._parse_pesticides_tabular(page)
    assert [(r['key'], r['value'], r['qualifier'], r['limit']) for r in rows] == [
        ('acephate', None, 'ND', 0.4), ('bifenazate', 0.35, '', 0.2)]
    # A header whose status falls elsewhere is not applied to the row.
    header = kaycha._parse_header('ANALYTES LOQ ACTION LEVEL PASS/FAIL RESULT (%) RESULT (mg/g)')
    row = _row('ACEPHATE ppm 0.0100 0.2000 0.4 PASS ND', layout=header, detection='lod')
    assert (row['value'], row['qualifier'], row['limit']) == (None, 'ND', 0.4)
