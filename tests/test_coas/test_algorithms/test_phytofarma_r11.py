"""
Regression tests for the 10/13/2026 (R11) fixes to phytofarma.py
(Phyto-Farma Labs COA parser, Warwick NY).

No real PDFs are used. Each test feeds synthetic page text, built from
the row layouts documented in phytofarma.py and from what a benchmark of
four Phyto-Farma COAs (read by four Claude models that agree with each
other) implies the printed lines are, to the table parser, or drives
parse_phyto_farma_pdf through a stand-in for pdfplumber. The synthetic
rows reproduce every value the r10 parser reported in the benchmark
(the action limits for 2023 trace metals, acetone 5000 ppm, null
moisture and stems, water activity in percent). The bug tests fail on
the r10-delivered parser; the regression tests pin formats that the r10
parser already read right.

    1. 2023 trace metals: the eight action limits reported as results.
    2. Residual solvents: acetone <LOQ read as 5000 ppm (its limit); a
       digit in a name shifted its cells or dropped the row.
    3. Moisture content null (10.90 %, 11.60 %), stems null (0.00);
       water activity reported in percent from the filth table.
    4. Non-detects: '<LOQ' read as 0.0; now value None, qualifier '<LOQ'.
    5. Names with digits dropped: Δ8/Δ9/Δ10-THC, 3-Carene; aflatoxins
       B1-G2 read as their limit; MDG pathogens keyed with their type.

Run:
    pytest tests/test_coas/test_algorithms/test_phytofarma_r11.py -v
"""
import json

import pytest

from cannlytics.data.coas.algorithms import phytofarma


def by_key(rows, key, analysis=None):
    """The one row with ``key`` (and ``analysis``, when given)."""
    found = [
        r for r in rows
        if r['key'] == key and (analysis is None or r['analysis'] == analysis)
    ]
    assert len(found) == 1, f'{key}: {found}'
    return found[0]


def parse(text, analysis, units, col_spec, **kwargs):
    """Run the table parser on synthetic section text."""
    return phytofarma._parse_analyte_table_text(text, analysis, units, col_spec, **kwargs)


def physical_routes():
    """The routes the main parser gives the filth/moisture/water page."""
    routes = dict(phytofarma._PHYSICAL_ROUTES)
    routes[None] = phytofarma._PHYSICAL_ROUTES['foreign_matter']
    return routes


# ── 1. 2023 trace metals: the result is not the action limit ─────────
#
# Benchmark COA 5a170fc8 (2023, "Phyto-farma Labs", OCMPPL-2022-00004):
# r10 reported antimony 2.0, arsenic 0.2, cadmium 0.3, chromium 110,
# copper 30, lead 0.5, mercury 0.1, nickel 2.0 ug/g -- New York's limits.
# The COA prints copper 15.94, nickel 0.72, cadmium 0.09, the rest <LOQ.
# r10 read the third cell after the name, so the result is not there;
# both column orders that make r10 read the limit are tested.

HISTORIC_METALS = {
    'loq_result_limit': """\
Trace Metals
Analyte LOQ (ug/g) Results (ug/g) Action Level (ug/g) Pass/Fail
Antimony (Sb) 0.13 <LOQ 2.0 PASS
Arsenic (As) 0.07 <LOQ 0.2 PASS
Cadmium (Cd) 0.06 0.09 0.3 PASS
Chromium (Cr) 0.36 <LOQ 110 PASS
Copper (Cu) 0.39 15.94 30 PASS
Lead (Pb) 0.08 <LOQ 0.5 PASS
Mercury (Hg) 0.01 <LOQ 0.1 PASS
Nickel (Ni) 0.11 0.72 2.0 PASS
""",
    'result_loq_limit': """\
Trace Metals
Analyte Results LOQ Action Level Pass/Fail
Antimony (Sb) <LOQ 0.13 2.0 PASS
Arsenic (As) <LOQ 0.07 0.2 PASS
Cadmium (Cd) 0.09 0.06 0.3 PASS
Chromium (Cr) <LOQ 0.36 110 PASS
Copper (Cu) 15.94 0.39 30 PASS
Lead (Pb) <LOQ 0.08 0.5 PASS
Mercury (Hg) <LOQ 0.01 0.1 PASS
Nickel (Ni) 0.72 0.11 2.0 PASS
""",
}

HISTORIC_METAL_ANSWERS = {
    # key: (value, qualifier, loq, limit)
    'antimony': (None, '<LOQ', 0.13, 2.0),
    'arsenic': (None, '<LOQ', 0.07, 0.2),
    'cadmium': (0.09, '', 0.06, 0.3),
    'chromium': (None, '<LOQ', 0.36, 110.0),
    'copper': (15.94, '', 0.39, 30.0),
    'lead': (None, '<LOQ', 0.08, 0.5),
    'mercury': (None, '<LOQ', 0.01, 0.1),
    'nickel': (0.72, '', 0.11, 2.0),
}


def check_historic_metals(rows):
    assert len(rows) == 8
    for key, (value, qualifier, loq, limit) in HISTORIC_METAL_ANSWERS.items():
        row = by_key(rows, key)
        assert row['value'] == value, key
        assert row['qualifier'] == qualifier, key
        assert row['loq'] == loq, key
        assert row['limit'] == limit, key
        assert row['units'] == 'ug/g'
        assert row['status'] == 'pass'


@pytest.mark.parametrize('layout', sorted(HISTORIC_METALS))
def test_historic_trace_metals_are_not_the_action_limits(layout):
    # r10: copper 30.0, nickel 2.0, cadmium 0.3, antimony 2.0, ...
    text = HISTORIC_METALS[layout]
    section = phytofarma._extract_section_text(text, 'Trace Metals')
    check_historic_metals(parse(section, 'heavy_metals', 'ug/g', 'loq_limit_value_status'))


@pytest.mark.parametrize('layout', sorted(HISTORIC_METALS))
def test_historic_trace_metals_without_a_header_row(layout):
    # The "<LOQ" cells alone locate the result column.
    rows_only = '\n'.join(HISTORIC_METALS[layout].splitlines()[2:])
    check_historic_metals(parse(rows_only, 'heavy_metals', 'ug/g', 'loq_limit_value_status'))


def test_historic_trace_metals_all_detected_header_places_the_result():
    # No non-detect to locate the result column: the header row does.
    text = """\
Analyte Results (ug/g) LOQ (ug/g) Action Level (ug/g) Pass/Fail
Copper (Cu) 15.94 0.39 30 PASS
Nickel (Ni) 0.72 0.11 2.0 PASS
Cadmium (Cd) 0.09 0.06 0.3 PASS
"""
    rows = parse(text, 'heavy_metals', 'ug/g', 'loq_limit_value_status')
    assert by_key(rows, 'copper')['value'] == 15.94
    assert by_key(rows, 'copper')['limit'] == 30.0
    assert by_key(rows, 'nickel')['value'] == 0.72
    assert by_key(rows, 'cadmium')['loq'] == 0.06


def test_historic_trace_metals_all_detected_no_header_passing_result_is_below_limit():
    # Neither non-detects nor a header: a passing result lies between
    # its LOQ and its limit, so the limit is not read as the result.
    text = """\
Copper (Cu) 0.39 15.94 30 PASS
Nickel (Ni) 0.11 0.72 2.0 PASS
"""
    rows = parse(text, 'heavy_metals', 'ug/g', 'loq_limit_value_status')
    copper = by_key(rows, 'copper')
    assert (copper['value'], copper['loq'], copper['limit']) == (15.94, 0.39, 30.0)
    assert by_key(rows, 'nickel')['value'] == 0.72


def test_end_to_end_historic_coa(monkeypatch):
    # The whole 2023 COA through parse_phyto_farma_pdf.
    pages = [
        FakePage(HISTORIC_FRONT),
        FakePage(HISTORIC_MICRO),
        FakePage(HISTORIC_MICRO_2),
        FakePage(HISTORIC_METALS['loq_result_limit'] + 'Page 4 of 4\n'),
    ]
    results, data = run_parser(monkeypatch, pages)
    check_historic_metals([r for r in results if r['analysis'] == 'heavy_metals'])
    assert 'heavy_metals' in json.loads(data['analyses'])
    assert data['lab'] == 'Phyto-Farma Labs'


# ── 2. Residual solvents: the result is not the action limit ─────────
#
# Benchmark COAs c072518b (LOQs 125 ppm) and 541de5e6 (LOQ 15.9 ppm):
# r10 read acetone as 5000 ppm. "Acetone (2-Propanone)" was cut at its
# first digit, so the cells shifted and the limit sat in the result
# position. Rows whose names start with a digit were dropped.

SOLVENTS_541 = """\
Residual Solvents (SOP: PFL-SOP-0021)
Analyte LOQ (ppm) Action Limit (ppm) Results (ppm) Pass/Fail
1,2-Dichloroethane (Ethylene dichloride, Ethylene chloride) 0.67 5 <LOQ PASS
2-Propanol (Isopropanol, Isopropyl alcohol) 21.7 5000 231 PASS
Acetone (2-Propanone) 15.9 5000 <LOQ PASS
Acetonitrile 0.85 410 <LOQ PASS
Benzene 0.71 2 <LOQ PASS
Butanes, Total 4.85 5000 <LOQ PASS
Dimethyl sulfoxide (DMSO) 0.66 5000 <LOQ PASS
Ethyl ether (Diethyl ether, 1,1’-Oxybisethane) 0.44 5000 <LOQ PASS
Heptane (n-Heptane) 0.36 5000 <LOQ PASS
Trichloroethane (1,1,1-) 0.41 1500 <LOQ PASS
Tetrafluoroethane (1,1,1,2-) (HFC134a)* 1.0 1000 <LOQ PASS
Xylenes, Total (ortho-, meta-, para-) 3.63 2170 <LOQ PASS
Certificate: 4892.1
"""


@pytest.mark.parametrize('loq', ['15.9', '125'])
def test_acetone_nondetect_is_not_the_action_limit(loq):
    # r10: acetone 5000.0 ppm.
    text = SOLVENTS_541.replace('Acetone (2-Propanone) 15.9', f'Acetone (2-Propanone) {loq}')
    section = phytofarma._extract_section_text(text, 'Residual Solvents')
    rows = parse(section, 'residual_solvents', 'ppm', 'loq_limit_value_status')
    acetone = by_key(rows, 'acetone')
    assert acetone['value'] is None
    assert acetone['qualifier'] == '<LOQ'
    assert acetone['loq'] == float(loq)
    assert acetone['limit'] == 5000.0
    assert acetone['units'] == 'ppm'
    assert acetone['status'] == 'pass'


def test_solvent_names_with_digits_keep_their_cells():
    section = phytofarma._extract_section_text(SOLVENTS_541, 'Residual Solvents')
    rows = parse(section, 'residual_solvents', 'ppm', 'loq_limit_value_status')
    assert len(rows) == 12
    # Dropped by r10 (the name starts with a digit).
    isopropanol = by_key(rows, 'isopropanol')
    assert (isopropanol['value'], isopropanol['loq'], isopropanol['limit']) == (231.0, 21.7, 5000.0)
    dichloroethane = by_key(rows, '1_2_dichloroethane')
    assert dichloroethane['value'] is None and dichloroethane['qualifier'] == '<LOQ'
    assert (dichloroethane['loq'], dichloroethane['limit']) == (0.67, 5.0)
    # r10: 5000, 1500 and 1.0 (the limit, the limit and the LOQ).
    for key, loq, limit in (
        ('ethyl_ether', 0.44, 5000.0),
        ('trichloroethane', 0.41, 1500.0),
        ('tetrafluoroethane', 1.0, 1000.0),
    ):
        row = by_key(rows, key)
        assert row['value'] is None, key
        assert row['qualifier'] == '<LOQ', key
        assert (row['loq'], row['limit']) == (loq, limit), key
    # Canonical keys (r10: 'dmso').
    assert by_key(rows, 'dimethyl_sulfoxide')['loq'] == 0.66


def test_wrapped_solvent_name_is_joined():
    # A long name pdfplumber wraps onto a second line.
    text = """\
Analyte LOQ Action Limit Results Pass/Fail
1,2-Dichloroethane (Ethylene dichloride, 0.1 5 <LOQ PASS
Ethylene chloride)
Benzene 0.1 2 <LOQ PASS
"""
    rows = parse(text, 'residual_solvents', 'ppm', 'loq_limit_value_status')
    assert [r['key'] for r in rows] == ['1_2_dichloroethane', 'benzene']
    assert by_key(rows, '1_2_dichloroethane')['limit'] == 5.0


# ── 3. Filth, moisture content and water activity ────────────────────
#
# Benchmark COAs b82a2e50 (moisture 11.60 %, water activity 0.56) and
# c072518b (moisture 10.90 %, water activity <LOQ): r10 read moisture as
# null, stems as null (the COA prints 0.00), and water activity in
# percent from the filth table, which ran on into the other two. The
# moisture row has two numbers before the status (r10 read it from the
# left); the forms of its LOQ cell that do so are tested.

PHYSICAL_PAGE = """\
Filth and Foreign Matter (SOP: PFL-SOP-0040)
Analyte LOQ Action Limit Results Pass/Fail
Mammalian excreta (mg/lb) 0.00 1.00 0.00 PASS
Stems >3mm in diameter (%) 0.00 5.00 0.00 PASS
Other Foreign Material (%) 0.00 2.00 0.00 PASS
Moisture Content (SOP: PFL-SOP-0012)
Analyte LOQ Action Limit Results Pass/Fail
{moisture}
Water Activity (SOP: PFL-SOP-0013)
Analyte LOQ Action Limit Results Pass/Fail
Water Activity 0.25 0.65 {water} PASS
Certificate: 5010.1
"""

MOISTURE_ROWS = {
    'blank_loq': 'Moisture Content 15.00 {value} PASS',
    'dash_loq': 'Moisture Content - 15.00 {value} PASS',
    'unit_cell': 'Moisture Content 0.00 15.00 % {value} PASS',
}


def physical_rows(monkeypatch, moisture='blank_loq', value='11.60', water='0.56'):
    """The filth/moisture/water page parsed by parse_phyto_farma_coa."""
    page = PHYSICAL_PAGE.format(
        moisture=MOISTURE_ROWS[moisture].format(value=value), water=water,
    )
    results, _ = run_parser(monkeypatch, [FakePage(MODERN_FRONT), FakePage(page)])
    return results


@pytest.mark.parametrize('moisture', sorted(MOISTURE_ROWS))
@pytest.mark.parametrize('value', ['11.60', '10.90'])
def test_moisture_content_is_read(monkeypatch, moisture, value):
    # r10: null.
    row = by_key(physical_rows(monkeypatch, moisture, value), 'moisture_content', 'moisture')
    assert row['value'] == float(value)
    assert row['qualifier'] == ''
    assert row['limit'] == 15.0
    assert row['units'] == 'percent'
    assert row['status'] == 'pass'


def test_moisture_table_with_its_own_columns(monkeypatch):
    # A header row that names the result before the limit is followed.
    page = PHYSICAL_PAGE.format(moisture='Moisture Content 10.90 15.00 PASS', water='0.56').replace(
        'Moisture Content (SOP: PFL-SOP-0012)\nAnalyte LOQ Action Limit Results Pass/Fail',
        'Moisture Content (SOP: PFL-SOP-0012)\nAnalyte Results Action Limit Pass/Fail',
    )
    results, _ = run_parser(monkeypatch, [FakePage(MODERN_FRONT), FakePage(page)])
    row = by_key(results, 'moisture_content', 'moisture')
    assert (row['value'], row['limit']) == (10.9, 15.0)


def test_stems_zero_is_a_measured_zero(monkeypatch):
    # r10: null ("Stems >3mm" was cut at the 3).
    stems = by_key(physical_rows(monkeypatch), 'stems', 'foreign_matter')
    assert stems['value'] == 0.0
    assert stems['qualifier'] == ''
    assert (stems['loq'], stems['limit']) == (0.0, 5.0)
    assert stems['units'] == 'percent'


def test_water_activity_is_in_aw_and_its_own_analysis(monkeypatch):
    # r10: water activity 0.56 'percent', from the filth table.
    rows = physical_rows(monkeypatch)
    assert [(r['analysis'], r['units']) for r in rows if r['key'] == 'water_activity'] == [
        ('water_activity', 'aw'),
    ]
    water = by_key(rows, 'water_activity')
    assert water['value'] == 0.56
    assert (water['loq'], water['limit']) == (0.25, 0.65)
    below = by_key(physical_rows(monkeypatch, water='<LOQ'), 'water_activity')
    assert below['value'] is None
    assert below['qualifier'] == '<LOQ'
    assert below['loq'] == 0.25
    assert below['units'] == 'aw'


def test_mammalian_excreta_units_are_mg_per_lb(monkeypatch):
    excreta = by_key(physical_rows(monkeypatch), 'mammalian_excreta')
    assert excreta['units'] == 'mg/lb'  # r10: 'percent'
    assert excreta['value'] == 0.0


def test_physical_rows_go_to_their_own_analyses(monkeypatch):
    results, data = run_parser(monkeypatch, [
        FakePage(MODERN_FRONT),
        FakePage(PHYSICAL_PAGE.format(moisture=MOISTURE_ROWS['dash_loq'].format(value='11.60'), water='0.56')),
    ])
    assert [(r['analysis'], r['key']) for r in results] == [
        ('foreign_matter', 'mammalian_excreta'),
        ('foreign_matter', 'stems'),
        ('foreign_matter', 'other_foreign_material'),
        ('moisture', 'moisture_content'),
        ('water_activity', 'water_activity'),
    ]
    assert json.loads(data['analyses']) == ['foreign_matter', 'moisture', 'water_activity']


def test_moisture_mention_on_another_page_does_not_block_the_physical_page(monkeypatch):
    # A page that only mentions moisture (a dry-weight note) is not the
    # filth/moisture/water page, and leaves no rows behind.
    potency = CANNABINOIDS.replace(
        'Certificate: 5010.1',
        'Potency corrected for Moisture Content of 12 % (dry weight)\nCertificate: 5010.1',
    )
    physical = PHYSICAL_PAGE.format(moisture=MOISTURE_ROWS['blank_loq'].format(value='10.90'), water='0.56')
    results, data = run_parser(monkeypatch, [FakePage(MODERN_FRONT), FakePage(potency), FakePage(physical)])
    assert by_key(results, 'moisture_content', 'moisture')['value'] == 10.9
    assert by_key(results, 'stems', 'foreign_matter')['value'] == 0.0
    assert by_key(results, 'water_activity', 'water_activity')['units'] == 'aw'
    assert {r['analysis'] for r in results} == {
        'cannabinoids', 'foreign_matter', 'moisture', 'water_activity',
    }


def test_physical_routes_table_parser():
    # The routes the main parser passes, used directly.
    page = PHYSICAL_PAGE.format(moisture=MOISTURE_ROWS['blank_loq'].format(value='10.90'), water='<LOQ')
    keyword = phytofarma._first_keyword(page, phytofarma._PHYSICAL_KEYWORDS)
    assert keyword == 'Foreign Matter'
    section = phytofarma._extract_section_text(page, keyword)
    rows = parse(section, 'foreign_matter', 'percent', 'foreign_matter', routes=physical_routes())
    assert by_key(rows, 'moisture_content')['value'] == 10.9
    # Without routes, the filth table keeps only its own rows.
    rows = parse(section, 'foreign_matter', 'percent', 'foreign_matter')
    assert [r['key'] for r in rows] == ['mammalian_excreta', 'stems', 'other_foreign_material']


def test_regression_filth_values():
    # Read right by r10.
    rows = phytofarma._parse_analyte_table_text(
        phytofarma._extract_section_text(
            PHYSICAL_PAGE.format(moisture='', water='0.56'), 'Foreign Matter',
        ),
        'foreign_matter', 'percent', 'foreign_matter',
    )
    assert by_key(rows, 'mammalian_excreta')['value'] == 0.0
    assert by_key(rows, 'other_foreign_material')['value'] == 0.0
    assert by_key(rows, 'other_foreign_material')['limit'] == 2.0


# ── 4. Non-detects keep their qualifier ──────────────────────────────

MODERN_METALS = """\
Trace Metals (SOP: PFL-SOP-0030)
Analyte LOQ Action Limit Results Pass/Fail
Antimony (Sb)* 0.315 2.0 <LOQ PASS
Arsenic (As)* 0.18 0.2 <LOQ PASS
Cadmium (Cd)* 0.159 0.2 <LOQ PASS
Chromium (Cr)* 0.891 110 <LOQ PASS
Copper (Cu)* 0.984 30 4.47 PASS
Lead (Pb)* 0.195 0.5 <LOQ PASS
Mercury (Hg)* 0.033 0.1 <LOQ PASS
Nickel (Ni)* 0.273 5.0 <LOQ PASS
Mycotoxins (SOP: PFL-SOP-0031)
Analyte LOQ Action Limit Results Pass/Fail
Aflatoxin B1 0.001 0.02 <LOQ PASS
Aflatoxin B2 0.002 0.02 <LOQ PASS
Aflatoxin G1 0.001 0.02 <LOQ PASS
Aflatoxin G2 0.002 0.02 <LOQ PASS
Sum of Aflatoxins 0.02 0.000 PASS
Ochratoxin A 0.002 0.02 <LOQ PASS
Certificate: 5010.1
"""


def modern_metals():
    section = phytofarma._extract_section_text(MODERN_METALS, 'Trace Metals')
    return parse(section, 'heavy_metals', 'ug/g', 'loq_limit_value_status')


def mycotoxins():
    section = phytofarma._extract_section_text(MODERN_METALS, 'Mycotoxin')
    return parse(section, 'mycotoxins', 'ug/g', 'loq_limit_value_status')


def test_below_loq_is_a_qualifier_not_zero():
    # r10: antimony 0.0.
    antimony = by_key(modern_metals(), 'antimony')
    assert antimony['value'] is None
    assert antimony['qualifier'] == '<LOQ'
    assert antimony['loq'] == 0.315
    assert antimony['limit'] == 2.0


def test_below_bound_becomes_the_loq_when_the_row_has_none():
    rows = parse(
        'Analyte Action Limit Results Pass/Fail\nLead (Pb) 0.5 <0.08 PASS\n',
        'heavy_metals', 'ug/g', 'loq_limit_value_status',
    )
    lead = by_key(rows, 'lead')
    assert (lead['value'], lead['qualifier'], lead['loq'], lead['limit']) == (None, '<LOQ', 0.08, 0.5)


def test_parse_number_does_not_read_a_bound_as_a_number():
    # r10: 0.0 for '<LOQ' and '<0.13'.
    assert phytofarma._parse_number('<LOQ') is None
    assert phytofarma._parse_number('<0.13') is None
    assert phytofarma._parse_number('5,000') == 5000.0
    assert phytofarma._parse_number('10.90%') == 10.9
    assert phytofarma._parse_result('Not_Detected') == (None, 'ND', None)
    assert phytofarma._parse_result('<0.13') == (None, '<LOQ', 0.13)
    assert phytofarma._parse_result('0.00') == (0.0, '', None)
    assert phytofarma._parse_result('None') == (None, '', None)


def test_every_row_carries_the_result_fields():
    for row in modern_metals() + mycotoxins() + cannabinoids() + mdg_rows():
        for field in ('value', 'qualifier', 'lod', 'loq', 'limit', 'status', 'units'):
            assert field in row, (row['key'], field)


def test_regression_modern_metals_values():
    # Read right by r10 (24/24 rows in the benchmark).
    rows = modern_metals()
    assert by_key(rows, 'copper')['value'] == 4.47
    assert by_key(rows, 'copper')['limit'] == 30.0
    assert by_key(rows, 'nickel')['limit'] == 5.0
    for key in ('antimony', 'arsenic', 'cadmium', 'chromium', 'lead', 'mercury', 'nickel'):
        assert not by_key(rows, key)['value'], key
    detected = parse(
        'Analyte LOQ Action Limit Results Pass/Fail\n'
        'Lead (Pb)* 0.08 0.5 0.083 PASS\nNickel (Ni)* 0.11 2.0 0.148 PASS\n',
        'heavy_metals', 'ug/g', 'loq_limit_value_status',
    )
    assert by_key(detected, 'lead')['value'] == 0.083
    assert by_key(detected, 'nickel')['value'] == 0.148


# ── 5. Names with digits; MDG; tables printed below ──────────────────

def test_aflatoxins_are_not_their_limit():
    # r10: 'aflatoxin_b' 0.02 (the limit), B1 and B2 merged.
    rows = mycotoxins()
    assert [r['key'] for r in rows] == [
        'aflatoxin_b1', 'aflatoxin_b2', 'aflatoxin_g1', 'aflatoxin_g2',
        'total_aflatoxins', 'ochratoxin_a',
    ]
    b1 = by_key(rows, 'aflatoxin_b1')
    assert (b1['value'], b1['qualifier'], b1['loq'], b1['limit']) == (None, '<LOQ', 0.001, 0.02)
    total = by_key(rows, 'total_aflatoxins')
    assert (total['value'], total['loq'], total['limit']) == (0.0, None, 0.02)


def test_wrapped_sum_of_aflatoxins_is_joined():
    text = MODERN_METALS.replace('Sum of Aflatoxins 0.02 0.000 PASS', 'Sum of 0.02 0.000 PASS\nAflatoxins')
    section = phytofarma._extract_section_text(text, 'Mycotoxin')
    total = by_key(parse(section, 'mycotoxins', 'ug/g', 'loq_limit_value_status'), 'total_aflatoxins')
    assert total['value'] == 0.0


def test_mycotoxins_are_not_reported_as_heavy_metals():
    # r10: the trace metals section ran on into the mycotoxin table.
    keys = [r['key'] for r in modern_metals()]
    assert 'ochratoxin_a' not in keys
    assert not [k for k in keys if k.startswith('aflatoxin')]


CANNABINOIDS = """\
Average Cannabinoid Profile (SOP: PFL-SOP-0005)
Analyte LOQ Average % (w/w)
Total Tetrahydrocannabinol (THC) 63.1
Tetrahydrocannabinolic acid (THCA) 0.5 66.6
Δ8-THC 0.5 <LOQ
Δ9-THC 0.5 4.48
Δ10-THC-RS 0.5 0.195
Δ10-THC-RR 0.5 <LOQ
Total Cannabidiol (CBD) 0.111
Cannabinadiolic acid (CBDA) 0.5 0.127
Cannabidiol (CBD) 0.5 <LOQ
Total Active Tetrahydrocannabivarin (THCV) 0.292
Tetrahydrocannabivarinic acid (THCVA)* 0.5 0.337
Tetrahydrocannabivarin (THCV) 0.5 <LOQ
Total Active Cannabigerol (CBG) 2.21
Cannabigerolic acid (CBGA) 0.5 2.17
Cannabigerol (CBG) 0.5 0.305
Cannabidivarin (CBDV) 0.5 <LOQ
Cannabinol (CBN) 0.5 <LOQ
Cannabichromene (CBC) 0.5 <LOQ
Total Cannabinoids 65.7
Certificate: 5010.1
"""


def cannabinoids():
    section = phytofarma._extract_section_text(CANNABINOIDS, 'Cannabinoid')
    return parse(section, 'cannabinoids', 'percent', 'loq_value')


def test_delta_thc_rows_are_read():
    # r10 dropped all four ("Δ9-THC" was cut to "Δ").
    rows = cannabinoids()
    assert len(rows) == 14
    assert by_key(rows, 'delta_9_thc')['value'] == 4.48
    assert by_key(rows, 'delta_10_thc_rs')['value'] == 0.195
    for key in ('delta_8_thc', 'delta_10_thc_rr'):
        row = by_key(rows, key)
        assert (row['value'], row['qualifier'], row['loq']) == (None, '<LOQ', 0.5), key


def test_delta_sign_variants():
    rows = parse(
        'Analyte LOQ Average\n∆9-THC 0.5 0.399\nD8-THC 0.5 0.0876\n',
        'cannabinoids', 'percent', 'loq_value',
    )
    assert by_key(rows, 'delta_9_thc')['value'] == 0.399
    assert by_key(rows, 'delta_8_thc')['value'] == 0.0876


def test_regression_cannabinoid_values():
    # Read right by r10 (30/30 in the benchmark); totals are not rows.
    rows = cannabinoids()
    for key, value in (
        ('thca', 66.6), ('cbda', 0.127), ('thcva', 0.337), ('cbga', 2.17), ('cbg', 0.305),
    ):
        assert by_key(rows, key)['value'] == value, key
        assert by_key(rows, key)['loq'] == 0.5, key
        assert by_key(rows, key)['units'] == 'percent', key
    for key in ('cbd', 'thcv', 'cbdv', 'cbn', 'cbc'):
        assert not by_key(rows, key)['value'], key
    assert not [r for r in rows if r['key'].startswith('total_')]


TERPENES_LEFT = """\
Terpenes (SOP: PFL-SOP-0008)
Analyte LOQ (%) Results (%)
3-Carene 0.00042 <LOQ
alpha-Bisabolol 0.0005 0.0544
alpha-Humulene 0.00056 0.0102
alpha-Pinene 0.00048 0.0406
beta-Myrcene 0.00064 0.395
Camphor 0.0004 <LOQ
Farnesene 0.00084 0.3873
"""

TERPENES_RIGHT = """\
Analyte LOQ (%) Results (%)
Limonene 0.00074 0.3299
Linalool 0.00046 0.0842
Pulegone (+) 0.00056 <LOQ
Sabinene 0.00034 0.059
Sabinene Hydrate 0.00042 <LOQ
trans-b-Ocimene 0.00042 <LOQ
trans-Caryophyllene 0.00066 0.4886
"""


def test_three_carene_is_read():
    # r10 dropped it (the name starts with a digit).
    section = phytofarma._extract_section_text(TERPENES_LEFT, 'Analyte')
    carene = by_key(parse(section, 'terpenes', 'percent', 'terpene'), 'delta_3_carene')
    assert (carene['value'], carene['qualifier'], carene['loq']) == (None, '<LOQ', 0.00042)


def test_regression_terpene_values():
    # Read right by r10 (114/114 in the benchmark).
    rows = []
    for half in (TERPENES_LEFT, TERPENES_RIGHT):
        section = phytofarma._extract_section_text(half, 'Analyte')
        rows += parse(section, 'terpenes', 'percent', 'terpene')
    for key, value in (
        ('alpha_bisabolol', 0.0544), ('beta_myrcene', 0.395), ('farnesene', 0.3873),
        ('limonene', 0.3299), ('sabinene', 0.059), ('trans_caryophyllene', 0.4886),
    ):
        assert by_key(rows, key)['value'] == value, key
    assert by_key(rows, 'limonene')['loq'] == 0.00074
    for key in ('camphor', 'pulegone', 'sabinene_hydrate', 'trans_beta_ocimene'):
        assert not by_key(rows, key)['value'], key


MDG_PAGE = """\
Microbial Impurities - MDG (SOP: PFL-SOP-0050)
Analyte Microbial Type LOQ Allowable Limit Results Pass/Fail
Shiga toxin-producing Escherichia coli Bacterial 1 Not Detected Not Detected PASS
Salmonella species Bacterial 1 Not Detected Not Detected PASS
Aspergillus flavus Fungal 1 Not Detected Not Detected PASS
Aspergillus niger Fungal 1 Not Detected Not Detected PASS
Aspergillus terreus Fungal 1 Not Detected Not Detected PASS
Aspergillus fumigatus Fungal 1 Not Detected Not Detected PASS
Certificate: 5010.1
"""


def mdg_rows(page=MDG_PAGE):
    section = phytofarma._extract_section_text(page, 'Microbial')
    return parse(section, 'microbials', 'cfu/g', 'microbial_mdg')


def test_mdg_pathogens_are_keyed_without_their_type():
    # r10: 'shiga_toxin_producing_escherichia_coli_bacterial', ...
    rows = mdg_rows()
    assert [r['key'] for r in rows] == [
        'stec', 'salmonella', 'aspergillus_flavus', 'aspergillus_niger',
        'aspergillus_terreus', 'aspergillus_fumigatus',
    ]
    for row in rows:
        assert row['value'] is None
        assert row['qualifier'] == 'ND'
        assert row['loq'] == 1.0
        assert row['limit'] is None
        assert row['status'] == 'pass'
        assert row['units'] == 'cfu/g'


def test_mdg_detected_and_pending_rows():
    page = MDG_PAGE.replace(
        'Aspergillus flavus Fungal 1 Not Detected Not Detected PASS',
        'Aspergillus flavus Fungal 1 Not Detected Detected FAIL',
    ).replace(
        'Aspergillus niger Fungal 1 Not Detected Not Detected PASS',
        'Aspergillus niger None 1 None None None',
    ).replace(' - MDG', ' – MDG')
    rows = mdg_rows(page)
    flavus = by_key(rows, 'aspergillus_flavus')
    assert (flavus['value'], flavus['qualifier'], flavus['status']) == (None, 'detected', 'fail')
    niger = by_key(rows, 'aspergillus_niger')  # Pending: not a non-detect.
    assert (niger['value'], niger['qualifier'], niger['status']) == (None, '', None)


def test_historic_pcr_rows_without_digits_are_read():
    # 2023 PCR rows print no LOQ ("... Not Detected PASS"); r10 skipped
    # rows without a digit and cut "stx1 gene ..." to "stx".
    rows = parse(HISTORIC_MICRO_2.split('Page')[0], 'microbials', 'cfu/g', 'microbial_mdg')
    assert [r['key'] for r in rows] == [
        'e_coli_gene', 'e_coli_shigella', 'salmonella', 'stx1_gene', 'stx2_gene',
        'aspergillus_flavus', 'aspergillus_niger', 'aspergillus_terreus',
        'aspergillus_fumigatus',
    ]
    assert all(r['value'] is None and r['qualifier'] == 'ND' for r in rows)


PLATING_PAGE = """\
Microbial Impurities - TAPC (SOP: PFL-SOP-0052)
Analyte LOQ Action Limit Results Pass/Fail
Total Aerobic Bacteria/CDP-TC 5 N/A 10000 PASS
Microbial Impurities - TYMC (SOP: PFL-SOP-0053)
Analyte LOQ Action Limit Results Pass/Fail
Total Yeast and Mold 5 N/A 5000 PASS
Mold Count 5 N/A 5000 PASS
Yeast Count 5 N/A <LOQ PASS
Certificate: 5010.1
"""


def test_regression_microbial_plating_values():
    # Read right by r10.
    tapc = parse(
        phytofarma._extract_section_text(
            PLATING_PAGE, 'TAPC', end_keywords=['Microbial Impurities - TYMC', 'Certificate:'],
        ),
        'microbials', 'cfu/g', 'microbial_plating',
    )
    assert [r['key'] for r in tapc] == ['total_aerobic_bacteria']
    assert tapc[0]['value'] == 10000.0
    assert tapc[0]['loq'] == 5.0
    tymc = parse(
        phytofarma._extract_section_text(PLATING_PAGE, 'TYMC', end_keywords=['Certificate:']),
        'microbials', 'cfu/g', 'microbial_plating',
    )
    assert by_key(tymc, 'total_yeast_and_mold')['value'] == 5000.0
    assert by_key(tymc, 'mold_count')['value'] == 5000.0
    assert not by_key(tymc, 'yeast_count')['value']


PESTICIDES_LEFT = """\
Pesticides LC (SOP: PFL-SOP-0060)
Analyte LOQ Action Limit Results Pass/Fail
Abamectin* 0.018 0.5 <LOQ PASS
Acephate* 0.007 0.4 <LOQ PASS
Acequinocyl* 0.016 2.0 <LOQ PASS
Indole-3-butyric acid* 0.007 1.0 <LOQ PASS
Kresoxim methyl* 0.012 0.4 <LOQ PASS
"""

PESTICIDES_RIGHT = """\
Analyte LOQ Action Limit Results Pass/Fail
MGK-264* 0.011 0.2 <LOQ PASS
Myclobutanil* 0.013 0.2 <LOQ PASS
Permethrins, Total* 0.009 0.2 <LOQ PASS
Spinetoram, Total* 0.005 1.0 <LOQ PASS
Thiamethoxam* 0.008 0.2 <LOQ PASS
"""

PESTICIDES_GC = """\
Pesticides GC (SOP: PFL-SOP-0061)
Analyte LOQ Action Limit Results Pass/Fail
Captan* 0.3 1.0 <LOQ PASS
Chlordane* 0.07 1.0 <LOQ PASS
Pentachloronitrobenzene* 0.17 1.0 <LOQ PASS
Trifloxystrobin* 0.11 0.2 <LOQ PASS
Certificate: 5010.1
"""


def test_pesticide_names_with_digits_are_read():
    # r10: 'mgk' 0.2 (its limit) and 'indole' 0.007 (its LOQ).
    rows = []
    for half in (PESTICIDES_LEFT, PESTICIDES_RIGHT):
        rows += parse(phytofarma._extract_section_text(half, 'Analyte'), 'pesticides', 'ppm', 'loq_limit_value_status')
    mgk = by_key(rows, 'mgk_264')
    assert (mgk['value'], mgk['qualifier'], mgk['loq'], mgk['limit']) == (None, '<LOQ', 0.011, 0.2)
    iba = by_key(rows, 'indole_3_butyric_acid')
    assert (iba['value'], iba['qualifier'], iba['loq'], iba['limit']) == (None, '<LOQ', 0.007, 1.0)


def test_regression_pesticides():
    # Read right by r10 (203/203 in the benchmark).
    rows = []
    for half in (PESTICIDES_LEFT, PESTICIDES_RIGHT):
        rows += parse(phytofarma._extract_section_text(half, 'Analyte'), 'pesticides', 'ppm', 'loq_limit_value_status')
    rows += parse(phytofarma._extract_section_text(PESTICIDES_GC, 'Pesticides GC'), 'pesticides', 'ppm', 'loq_limit_value_status')
    for key, loq, limit in (
        ('abamectin', 0.018, 0.5), ('acequinocyl', 0.016, 2.0), ('kresoxim_methyl', 0.012, 0.4),
        ('myclobutanil', 0.013, 0.2), ('permethrins', 0.009, 0.2), ('spinetoram', 0.005, 1.0),
        ('captan', 0.3, 1.0), ('chlordane', 0.07, 1.0), ('trifloxystrobin', 0.11, 0.2),
    ):
        row = by_key(rows, key)
        assert (row['loq'], row['limit']) == (loq, limit), key
        assert not row['value'], key
        assert row['units'] == 'ppm', key


# ── End to end, through a stand-in for pdfplumber ────────────────────

class FakeCrop:
    """What page.within_bbox() returns."""

    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


class FakePage:
    """A pdfplumber page: its text, and optionally its left and right
    halves (the two-column terpene and pesticide tables)."""

    width = 612
    height = 792

    def __init__(self, text, halves=None):
        self.text = text
        self.halves = halves

    def extract_text(self):
        return self.text

    def extract_words(self):
        return []

    def within_bbox(self, bbox):
        if self.halves:
            return FakeCrop(self.halves[0] if bbox[0] < self.width / 4 else self.halves[1])
        return FakeCrop(self.text)


class FakePDF:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def run_parser(monkeypatch, pages):
    """Parse fake pages; return the results and the whole output."""
    monkeypatch.setattr(phytofarma.pdfplumber, 'open', lambda path: FakePDF(pages))
    data = phytofarma.parse_phyto_farma_coa(None, 'fake_phyto_farma_coa.pdf')
    return json.loads(data['results']), data


MODERN_FRONT = """\
Mill Lane Chemist
Address: 6309 Mill Lane
Brooklyn, NY 11234
Hashtag Honey Cadillac Rainbow snowballz
COMPLIANCE FOR RETAIL
Pass
Sample Status
63.1 %
Total THC
0.111 %
Total CBD
65.7 %
Total Cannabinoids
Certificate: 5010.1 Accreditation #: 121747 Permit #: OCM-CPL-00004
Published: 02/20/2025
"""

HISTORIC_FRONT = """\
Phyto-farma Labs
Client Name: Example Home Farm
Sample Description: EXMP: Wedding Cake, 3.5g
Lot Number: EXMP00010
Results Summary
Microbial Impurities PASS
Trace Metals PASS
"""

HISTORIC_MICRO = """\
Microbial Impurities (CDP-YMR)
Analyte LOQ Results Pass/Fail
Mold Count 5 <LOQ PASS
Yeast Count 5 <LOQ PASS
Page 2 of 4
"""

HISTORIC_MICRO_2 = """\
Microbial Impurities (PdX)
Analyte Results Pass/Fail
Escherichia coli specific gene Not Detected PASS
Escherichia coli/Shigella species Not Detected PASS
Salmonella species Not Detected PASS
stx1 gene (Shiga Toxin Gene 1) Not Detected PASS
stx2 gene (Shiga Toxin Gene 2) Not Detected PASS
Aspergillus flavus Not Detected PASS
Aspergillus niger Not Detected PASS
Aspergillus terreus Not Detected PASS
Aspergillus fumigatus Not Detected PASS
Page 3 of 4
"""


def modern_pages():
    """A 10-page modern COA (the layout of benchmark COA c072518b)."""
    return [
        FakePage(MODERN_FRONT),
        FakePage(CANNABINOIDS),
        FakePage(
            'Terpene Total (SOP: PFL-SOP-0008)\n' + TERPENES_LEFT + TERPENES_RIGHT
            + 'Total Terpenes 2.061\nCertificate: 5010.1\n',
            halves=(TERPENES_LEFT, TERPENES_RIGHT),
        ),
        FakePage(MODERN_METALS),
        FakePage(
            PESTICIDES_LEFT + PESTICIDES_RIGHT + 'Certificate: 5010.1\n',
            halves=(PESTICIDES_LEFT, PESTICIDES_RIGHT),
        ),
        FakePage(PESTICIDES_GC),
        FakePage(MDG_PAGE),
        FakePage(PLATING_PAGE),
        FakePage(PHYSICAL_PAGE.format(
            moisture=MOISTURE_ROWS['blank_loq'].format(value='10.90'), water='<LOQ',
        )),
        FakePage(SOLVENTS_541.replace('15.9 5000', '125 5000')),
    ]


def test_end_to_end_modern_coa(monkeypatch):
    results, data = run_parser(monkeypatch, modern_pages())

    # One result per analysis and key.
    index = [(r['analysis'], r['key']) for r in results]
    assert len(index) == len(set(index))

    # Bugs.
    acetone = by_key(results, 'acetone')
    assert (acetone['value'], acetone['qualifier'], acetone['loq']) == (None, '<LOQ', 125.0)
    moisture = by_key(results, 'moisture_content')
    assert (moisture['value'], moisture['analysis'], moisture['units']) == (10.9, 'moisture', 'percent')
    water = by_key(results, 'water_activity')
    assert (water['value'], water['qualifier'], water['units']) == (None, '<LOQ', 'aw')
    assert by_key(results, 'stems')['value'] == 0.0
    assert by_key(results, 'delta_9_thc')['value'] == 4.48
    assert by_key(results, 'delta_3_carene')['qualifier'] == '<LOQ'
    assert by_key(results, 'aflatoxin_b1')['analysis'] == 'mycotoxins'
    assert by_key(results, 'stec')['qualifier'] == 'ND'
    assert by_key(results, 'antimony')['qualifier'] == '<LOQ'
    assert not [r for r in results if r['value'] == 0.0 and r['key'] not in (
        'mammalian_excreta', 'stems', 'other_foreign_material', 'total_aflatoxins',
    )]

    # Regressions.
    assert by_key(results, 'thca')['value'] == 66.6
    assert by_key(results, 'copper')['value'] == 4.47
    assert by_key(results, 'limonene')['value'] == 0.3299
    assert by_key(results, 'total_aerobic_bacteria')['value'] == 10000.0
    assert by_key(results, 'captan')['limit'] == 1.0
    assert data['total_thc'] == 63.1
    assert data['total_terpenes'] == 2.061
    analyses = json.loads(data['analyses'])
    for name in (
        'cannabinoids', 'terpenes', 'heavy_metals', 'mycotoxins', 'pesticides',
        'microbials', 'residual_solvents', 'foreign_matter', 'moisture', 'water_activity',
    ):
        assert name in analyses, name
