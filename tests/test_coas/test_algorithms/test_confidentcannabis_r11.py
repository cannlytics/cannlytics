"""
Tests for the Confident Cannabis COA parser fixes of 10/13/2026 (R11).
Copyright (c) 2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/13/2026
Updated: 10/13/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    A benchmark of 4 Arizona Confident Cannabis COAs, read by four
    Claude models that agree with each other, found the parser:

        * labelling percent values 'mg/g' (Apollo Labs, 2024: every
          cannabinoid and terpene, e.g. Δ9-THC 90.0348 'mg/g' where the
          COA prints 90.0348 %);
        * reading Arizona action limits as results (OnPoint
          Laboratories, 2021 and 2023: arsenic, cadmium, lead and
          mercury 400, 400, 1000 and 1200 'ug/g' where the COA prints
          <LOQ or ND with LOQs of 200, 200, 500 and 600 ppb; E. coli 100
          cfu/g, its limit, where the COA prints <LOQ or ND);
        * flattening '<LOQ' and '<10' to 0.0 (Level One Labs, 2023).

    No PDFs are available, so these tests feed the module page text as
    pdfplumber prints it, rebuilt from the printed names, values, LOQs
    and limits that the models read, through a stand-in for a PDF. Each
    page reproduces what the r10 parser read (r10 ignored the 'PPB'
    units row and read the limits beside a result cell printed on a line
    of its own). The tests run the functions shared by r10 and the fix,
    so that each bug test fails on r10 by its assertions; the regression
    tests (formats r10 already read correctly) pass on both.
"""
# Standard imports:
import contextlib
import json
from types import SimpleNamespace

# External imports:
import pytest

# Internal imports:
from cannlytics.data.coas.algorithms import confidentcannabis as cc

# ── Helpers ───────────────────────────────────────────────────────

class _Page:
    """A stand-in for a pdfplumber page."""

    def __init__(self, text: str):
        self._text = text

    def extract_text(self) -> str:
        return self._text

class _PDF:
    """A stand-in for a pdfplumber PDF."""

    def __init__(self, *pages: str):
        self.pages = [_Page(text) for text in pages]

def _results(*pages: str) -> list:
    """The results parsed from pages of text."""
    results, _ = cc._parse_results_from_text(_PDF(*pages))
    return results

def _by_key(results: list) -> dict:
    """Results by key (the first result of each key)."""
    found = {}
    for result in results:
        found.setdefault(result['key'], result)
    return found

def _by_name(results: list) -> dict:
    """Results by printed name (the first result of each name)."""
    found = {}
    for result in results:
        found.setdefault(result['name'], result)
    return found

def _f(result: dict, *fields: str) -> tuple:
    """A result's fields, as a tuple (None for a field it lacks)."""
    return tuple(result.get(field) for field in fields)

TOTALS = ('total_thc', 'total_cbd', 'total_cannabinoids')

# ── Pages rebuilt from the benchmark COAs ─────────────────────────

# Apollo Labs, 2024 vape (e77ee893...): a percent and an mg/g column.
APOLLO_CANNABINOIDS = """Cannabinoids Complete
Analyte LOQ Mass Mass
% % mg/g
THCa 0.1 ND ND
Δ9-THC 0.1 90.0348 900.348
Δ8-THC 0.1 ND ND
THCV 0.1 0.4761 4.761
CBD 0.1 0.1861 1.861
CBN 0.1 0.3965 3.965
CBG 0.1 2.5883 25.883
CBC 0.1 0.8512 8.512
Total 94.533 945.33"""

# Apollo Labs terpenes: two tables side by side, merged on each line.
APOLLO_TERPENES = """Terpenes Complete
Analyte LOQ Mass Mass Analyte LOQ Mass Mass
% % mg/g % % mg/g
D,L-Limonene 0.001 0.4816 4.816 cis-beta-Ocimene 0.001 ND ND
β-Caryophyllene 0.001 0.3463 3.463 Citronellol 0.001 ND ND
β-Myrcene 0.001 0.2951 2.951 Eucalyptol 0.001 ND ND
Endo-Fenchyl Alcohol 0.001 0.0480 0.480 Fenchone 0.001 ND ND
α-Thujone 0.001 ND ND γ-Terpinene 0.001 ND ND
3-Carene 0.001 ND ND Guaiol 0.001 ND ND
Total 2.4177 24.177"""

# Apollo Labs pesticides: two tables side by side.
APOLLO_PESTICIDES = """Pesticides Pass
Analyte LOQ Limit Mass Status Analyte LOQ Limit Mass Status
PPM PPM PPM PPM PPM PPM
Abamectin 0.25 0.5 ND Pass Hexythiazox 0.5 1 ND Pass
Acephate 0.2 0.4 ND Pass Imazalil 0.1 0.2 ND Pass
Bifenazate 0.1 0.2 ND Pass Kresoxim Methyl 0.2 0.4 ND Pass
Daminozide 0.5 1 ND Pass Piperonyl Butoxide 1 2 ND Pass
Dichlorvos 0.05 0.1 ND Pass Spinosad 0.1 0.2 ND Pass
Fludioxonil 0.2 0.4 ND Pass Trifloxystrobin 0.1 0.2 ND Pass"""

# Apollo Labs residual solvents: one table.
APOLLO_SOLVENTS = """Residual Solvents Pass
Analyte LOQ Limit Mass Status
PPM PPM PPM
Acetone 381 1000 ND Pass
Butanes 1914 5000 ND Pass
Ethyl-Acetate 1907 5000 ND Pass
n-Heptane 1892 5000 ND Pass
Hexanes 115 290 ND Pass
Isopropanol 1915 5000 ND Pass
Xylenes + Ethyl Benzene 841 2170 ND Pass"""

# Apollo Labs heavy metals, microbials and mycotoxins.
APOLLO_SAFETY = """Heavy Metals Pass
Analyte LOD LOQ Limit Mass Status
PPM PPM PPM PPM
Arsenic 0.066 0.133 0.4 ND Pass
Cadmium 0.066 0.133 0.4 ND Pass
Lead 0.166 0.333 1 ND Pass
Mercury 0.033 0.066 0.2 ND Pass
Microbials Pass
Analyte Limit Mass Status
CFU/g CFU/g
Salmonella SPP by QPCR: SOP-15 Not Detected in 1g Pass
Aspergillus Terreus by QPCR: SOP-14 Not Detected in 1g Pass
E. Coli by traditional plating: SOP-13 100 <10 Pass
Mycotoxins Pass
Analyte LOD LOQ Limit Mass Status
µg/kg µg/kg µg/kg µg/kg
B1 5 10 20 ND Pass
B2 5 10 20 ND Pass
G1 5 10 20 ND Pass
G2 5 10 20 ND Pass
Total Aflatoxins 5 10 20 ND Pass
Ochratoxin A 5 10 20 ND Pass"""

# OnPoint Laboratories, 2023 distillate (90a04e9c...): no LOQ column
# for cannabinoids; heavy-metal results in ppb print on a line of their
# own above their rows (r10 read 400, 400, 1000, 1200 'ug/g').
ONPOINT_2023 = """Cannabinoids Complete
Analyte Mass Mass
% mg/g
THCa ND ND
Δ9-THC 83.9504 839.504
Δ8-THC ND ND
THCV 0.9101 9.101
CBG 3.1477 31.477
Microbials Pass
Analyte Limit Mass Status
CFU/g CFU/g
Aspergillus ND Pass
E. Coli 100 <LOQ Pass
Salmonella ND Pass
Heavy Metals Pass
Analyte LOQ Limit Mass Status
PPB PPB PPB
<LOQ
Arsenic 200 400 Pass
<LOQ
Cadmium 200 400 Pass
<LOQ
Lead 500 1000 Pass
<LOQ
Mercury 600 1200 Pass"""

# OnPoint Laboratories, 2021 batter (95746c57...): ND and <LOQ metals.
ONPOINT_2021_METALS = """Heavy Metals Pass
Analyte LOQ Limit Mass Status
PPB PPB PPB
ND
Arsenic 200 400 Pass
<LOQ
Cadmium 200 400 Pass
<LOQ
Lead 500 1000 Pass
ND
Mercury 600 1200 Pass
Microbials Pass
Analyte Limit Mass Status
CFU/g CFU/g
E. Coli 100 ND Pass"""

# Level One Labs, 2023 edible (f54611fc...): mg/unit, and bounds.
LEVEL_ONE_EDIBLE = """Cannabinoids Complete
Analyte LOQ Mass Mass
mg/unit mg/unit mg/g
THCa 16.119 ND ND
Δ9-THC 16.119 85.742 2.106
CBN 16.119 <LOQ <LOQ
CBG 16.119 <LOQ <LOQ
Microbials Pass
E. Coli <10 Pass
Salmonella Not Detected in one gram Pass"""

# Arizona action limits and LOQs (ppb) of the OnPoint heavy metals.
ARIZONA_METALS = {
    'arsenic': (200.0, 400.0),
    'cadmium': (200.0, 400.0),
    'lead': (500.0, 1000.0),
    'mercury': (600.0, 1200.0),
}

# ── Bug 1: units name the column the value was read from ──────────

def test_cannabinoids_read_from_percent_column_are_labelled_percent():
    """r10: Δ9-THC 90.0348 'mg/g' (the % value, mg/g label)."""
    found = _by_key(_results(APOLLO_CANNABINOIDS))
    d9 = found['delta_9_thc']
    assert _f(d9, 'value', 'units') == (90.0348, 'percent')
    assert _f(d9, 'mg_g', 'loq') == (900.348, 0.1)
    for key, value in (('thcv', 0.4761), ('cbd', 0.1861), ('cbn', 0.3965),
                       ('cbg', 2.5883), ('cbc', 0.8512)):
        assert _f(found[key], 'value', 'units') == (value, 'percent')
    assert _f(found['thca'], 'value', 'units') == (None, 'percent')
    assert 'total' not in found

def test_terpenes_read_from_percent_column_are_labelled_percent():
    """r10: β-Caryophyllene 0.3463 'mg/g'."""
    found = _by_key(_results(APOLLO_TERPENES))
    for key, value in (('beta_caryophyllene', 0.3463), ('beta_myrcene', 0.2951),
                       ('fenchol', 0.048)):
        assert _f(found[key], 'value', 'units') == (value, 'percent')
    limonene = _by_name(found.values())['D,L-Limonene']
    assert _f(limonene, 'value', 'units', 'mg_g') == (0.4816, 'percent', 4.816)

def test_cannabinoids_without_loq_column():
    """OnPoint prints the percent and mg/g only. r10 read the mg/g
    column and took the percent cell as the LOQ (Δ9-THC LOQ 83.9504)."""
    found = _by_key(_results(ONPOINT_2023))
    d9 = found['delta_9_thc']
    assert d9.get('loq') is None
    assert _f(d9, 'value', 'units', 'mg_g') == (83.9504, 'percent', 839.504)
    assert found['cbg']['value'] == 3.1477
    assert found['thca']['value'] is None

def test_edible_cannabinoids_keep_mg_per_unit():
    """r10: Δ9-THC 85.742 'mg/g' (the mg/unit value, mg/g label)."""
    d9 = _by_key(_results(LEVEL_ONE_EDIBLE))['delta_9_thc']
    assert _f(d9, 'value', 'units') == (85.742, 'mg/unit')
    assert _f(d9, 'loq', 'mg_g') == (16.119, 2.106)

def test_heavy_metals_in_ppb_are_labelled_ppb():
    """r10 labelled ppb numbers 'ug/g' (1000x off): it ignored the
    'PPB' units row and fell back to the standard units."""
    metals = [r for r in _results(ONPOINT_2023) if r['analysis'] == 'heavy_metals']
    assert [r['units'] for r in metals] == ['ppb'] * 4

def test_units_do_not_carry_over_between_tables():
    """r10 kept the cannabinoid table's 'mg/g' for the microbial rows
    after it on the page."""
    assert _by_key(_results(LEVEL_ONE_EDIBLE))['e_coli']['units'] == 'cfu/g'

def test_detect_units_from_header_reads_left_to_right():
    """r10 looked units up in a fixed order: "% % mg/g" was 'mg/g' and
    'PPB' was 'ug/kg'."""
    assert cc._detect_units_from_header('% % mg/g', 'cannabinoids') == 'percent'
    assert cc._detect_units_from_header('PPB PPB PPB', 'heavy_metals') == 'ppb'

# ── Bug 2: a result is never an LOD, LOQ or action limit ──────────

def test_heavy_metal_limits_are_not_results():
    """r10: 400, 400, 1000, 1200 'ug/g'; the COA prints <LOQ."""
    found = _by_key(_results(ONPOINT_2023))
    for key, (loq, limit) in ARIZONA_METALS.items():
        metal = found[key]
        assert (key, *_f(metal, 'value', 'qualifier')) == (key, None, '<LOQ')
        assert _f(metal, 'loq', 'limit', 'status') == (loq, limit, 'pass')

def test_heavy_metal_non_detects_and_bounds_keep_their_qualifiers():
    """95746c57: arsenic and mercury ND, cadmium and lead <LOQ; r10 read
    every limit as the result."""
    found = _by_key(_results(ONPOINT_2021_METALS))
    expected = {'arsenic': 'ND', 'cadmium': '<LOQ', 'lead': '<LOQ', 'mercury': 'ND'}
    for key, qualifier in expected.items():
        assert _f(found[key], 'value', 'qualifier') == (None, qualifier)
        assert found[key]['limit'] == ARIZONA_METALS[key][1]

def test_heavy_metal_row_without_its_result_cell_has_no_result():
    """With no lone result cell beside it, the row has no result: its
    numbers are the LOQ and limit, never the limit as a result."""
    found = _by_key(_results("""Heavy Metals Pass
Analyte LOQ Limit Mass Status
PPB PPB PPB
Arsenic 200 400 Pass
Lead 500 1000 Pass"""))
    for key in ('arsenic', 'lead'):
        assert _f(found[key], 'value', 'qualifier') == (None, '')
        assert _f(found[key], 'loq', 'limit') == ARIZONA_METALS[key]

def test_lone_result_cells_below_their_rows():
    found = _by_key(_results("""Heavy Metals Pass
Analyte LOQ Limit Mass Status
PPB PPB PPB
Arsenic 200 400 Pass
ND
Cadmium 200 400 Pass
<LOQ"""))
    assert _f(found['arsenic'], 'value', 'qualifier') == (None, 'ND')
    assert _f(found['cadmium'], 'value', 'qualifier') == (None, '<LOQ')

def test_lone_result_cell_is_not_given_to_a_neighbor_when_ambiguous():
    """A missing result with lone cells both above and below it cannot
    be placed; nor can a lone cell when another row lacks one."""
    arsenic = _by_key(_results("""Heavy Metals Pass
Analyte LOQ Limit Mass Status
PPB PPB PPB
ND
Arsenic 200 400 Pass
<LOQ"""))['arsenic']
    assert _f(arsenic, 'value', 'qualifier') == (None, '')
    found = _by_key(_results("""Heavy Metals Pass
Analyte LOQ Limit Mass Status
PPB PPB PPB
<LOQ
Arsenic 200 400 Pass
Lead 500 1000 Pass"""))
    assert _f(found['arsenic'], 'value', 'qualifier') == (None, '')
    assert _f(found['lead'], 'value', 'qualifier') == (None, '')

def test_measured_heavy_metal_is_read():
    lead = _by_key(_results("""Heavy Metals Pass
Analyte LOQ Limit Mass Status
PPB PPB PPB
Lead 500 1000 612 Pass"""))['lead']
    assert _f(lead, 'value', 'qualifier', 'units') == (612.0, '', 'ppb')
    assert _f(lead, 'loq', 'limit') == (500.0, 1000.0)

@pytest.mark.parametrize('line', [
    'Arsenic 200 400 Pass <LOQ',   # result printed after the status
    'Arsenic <LOQ 200 400 Pass',   # result printed before the LOQ
    'Arsenic 200 <LOQ 400 Pass',   # result printed before the limit
])
def test_displaced_heavy_metal_result(line):
    """r10 read 400 from each: a bound can only be a result."""
    arsenic = _by_key(_results(f"""Heavy Metals Pass
Analyte LOQ Limit Mass Status
PPB PPB PPB
{line}"""))['arsenic']
    assert _f(arsenic, 'value', 'qualifier') == (None, '<LOQ')
    assert _f(arsenic, 'loq', 'limit', 'units') == (200.0, 400.0, 'ppb')

def test_heavy_metal_units_inferred_when_not_printed():
    """Without a units row, an LOQ or limit of 20 or more can only be
    ppb for a heavy metal (r10: the units passed in)."""
    result = cc._parse_analyte_line('Arsenic 200 400 <LOQ Pass', 'heavy_metals', None)
    assert _f(result, 'value', 'qualifier', 'units') == (None, '<LOQ', 'ppb')

def test_microbial_limit_is_not_the_result():
    """r10 took a microbial row's first number, its limit: E. coli 100
    cfu/g where the COA prints <LOQ (2023) or ND (2021)."""
    e_coli = _by_key(_results(ONPOINT_2023))['e_coli']
    assert _f(e_coli, 'value', 'qualifier') == (None, '<LOQ')
    assert _f(e_coli, 'limit', 'units') == (100.0, 'cfu/g')
    e_coli = _by_key(_results(ONPOINT_2021_METALS))['e_coli']
    assert _f(e_coli, 'value', 'qualifier', 'limit') == (None, 'ND', 100.0)

def test_microbial_rows_without_header_read_the_last_number():
    """Without a header row, the result of "Limit Mass Status" is the
    number before the status, not the first (r10: 10000)."""
    results = _results("""Microbials Pass
Yeast & Mold 10000 1200 Pass
Total Aerobic Bacteria 100000 3400 Pass
E. Coli 100 <LOQ Pass""")
    named = _by_name(results)
    assert _f(named['Yeast & Mold'], 'value', 'limit') == (1200.0, 10000.0)
    assert _f(named['E. Coli'], 'value', 'qualifier', 'limit') == (None, '<LOQ', 100.0)
    assert named['Yeast & Mold']['key'] == 'total_yeast_and_mold'
    assert _by_key(results)['total_aerobic_bacteria']['value'] == 3400.0

def test_apollo_microbial_and_mycotoxin_rows():
    results = _results(APOLLO_SAFETY)
    e_coli = _by_name(results)['E. Coli by traditional plating: SOP-13']
    assert _f(e_coli, 'value', 'qualifier') == (None, '<LOQ')
    assert _f(e_coli, 'loq', 'limit', 'key') == (10.0, 100.0, 'e_coli')
    found = _by_key(results)
    assert _f(found['salmonella'], 'value', 'qualifier') == (None, 'ND')
    assert found['aspergillus_terreus'].get('qualifier') == 'ND'
    for key in ('aflatoxin_b1', 'aflatoxin_b2', 'aflatoxin_g1', 'aflatoxin_g2',
                'total_aflatoxins', 'ochratoxin_a'):
        assert _f(found[key], 'value', 'qualifier', 'units') == (None, 'ND', 'ug/kg')
        assert _f(found[key], 'lod', 'loq', 'limit') == (5.0, 10.0, 20.0)
    for key in ('arsenic', 'cadmium', 'lead', 'mercury'):
        assert _f(found[key], 'value', 'qualifier', 'units') == (None, 'ND', 'ppm')
    assert _f(found['lead'], 'lod', 'loq', 'limit') == (0.166, 0.333, 1.0)

# ── Bug 3: the same pattern elsewhere in the module ───────────────

def test_bounds_are_not_measured_zeros():
    """r10: '<LOQ' and '<10' were the number 0.0."""
    assert cc._parse_number('<LOQ') is None
    assert cc._parse_number('<0.10') is None
    assert cc._parse_number('0') == 0.0
    found = _by_key(_results(LEVEL_ONE_EDIBLE))
    for key in ('cbn', 'cbg'):
        assert _f(found[key], 'value', 'qualifier', 'loq') == (None, '<LOQ', 16.119)
    assert _f(found['e_coli'], 'value', 'qualifier', 'loq') == (None, '<LOQ', 10.0)
    assert _f(found['salmonella'], 'value', 'qualifier') == (None, 'ND')

def test_measured_zero_stays_zero():
    cbdv = _by_key(_results("""Cannabinoids Complete
Analyte LOQ Mass Mass
% % mg/g
CBDV 0.1 0.0000 0.000"""))['cbdv']
    assert _f(cbdv, 'value', 'qualifier') == (0.0, '')

def test_summary_totals():
    """Totals: a bound is None (r10: 0.0); a Q3 flag does not shift the
    row (r10 read its '3' as a value); a total in mg/unit is not a
    percent (r10: total_thc 85.742)."""
    labels = '\nTotal THC Total CBD Total Cannabinoids'
    obs, _ = cc._parse_summary('83.9504% <LOQ 88.0082%' + labels)
    assert _f(obs, *TOTALS) == (83.9504, None, 88.0082)
    obs, _ = cc._parse_summary('83.9504% (Q3) ND 88.0082%' + labels)
    assert _f(obs, *TOTALS) == (83.9504, None, 88.0082)
    obs, _ = cc._parse_summary('85.742 mg/unit ND 85.742 mg/unit' + labels)
    assert _f(obs, *TOTALS) == (None, None, None)
    obs, _ = cc._parse_summary('90.0348% 0.1861% 94.533%' + labels)
    assert _f(obs, *TOTALS) == (90.0348, 0.1861, 94.533)

def test_moisture_is_not_read_from_an_unrelated_row():
    """r10 read the last number of the line above 'Moisture' (a
    cannabinoid row's mg/g) when moisture is not tested."""
    obs, _ = cc._parse_summary('CBG 3.1477 31.477\nMoisture (Q3)\nNot Tested')
    assert obs.get('moisture_content') is None
    obs, _ = cc._parse_summary('10.5%\nMoisture')
    assert obs['moisture_content'] == 10.5

def test_page_numbers_are_not_rows():
    """r10 read "Page 2 of 6" as an analyte 'page' with the value 6."""
    results = _results("""Pesticides Pass
Analyte LOQ Limit Mass Status
PPM PPM PPM
Abamectin 0.25 0.5 ND Pass 2 of 6
Page 2 of 6""")
    assert [r['key'] for r in results] == ['abamectin']
    assert _f(results[0], 'loq', 'limit', 'status') == (0.25, 0.5, 'pass')

def test_two_tables_side_by_side_are_split():
    """r10 dropped the right-hand rows, and a left-hand row without a
    status took the right-hand row's cells (Pendimethalin's limit was
    read as None; THCa took CBDa's value)."""
    found = _by_key(_results(APOLLO_PESTICIDES))
    for key in ('hexythiazox', 'imazalil', 'kresoxim_methyl', 'piperonyl_butoxide',
                'spinosad', 'trifloxystrobin'):
        assert _f(found[key], 'value', 'qualifier', 'status') == (None, 'ND', 'pass')
    assert _f(found['hexythiazox'], 'loq', 'limit') == (0.5, 1.0)
    found = _by_key(_results("""Pesticides Pass
Pendimethalin 0.05 0.1 NR Hexythiazox 0.5 1 ND Pass"""))
    assert _f(found['pendimethalin'], 'loq', 'limit') == (0.05, 0.1)
    assert _f(found['pendimethalin'], 'value', 'qualifier') == (None, 'NR')
    assert found['hexythiazox']['limit'] == 1.0
    found = _by_key(_results("""Cannabinoids Complete
Analyte LOQ Mass Mass Analyte LOQ Mass Mass
% % mg/g % % mg/g
THCa 0.1 ND ND CBDa 0.1 0.5000 5.000"""))
    assert found['thca']['value'] is None
    assert found['cbda']['value'] == 0.5

def test_two_column_results_helper():
    """_parse_two_column_results was a stub returning []."""
    text = APOLLO_PESTICIDES.split('\n', 1)[1]
    results = cc._parse_two_column_results(text, 'pesticides', 'ppm')
    assert len(results) == 12
    assert _f(_by_key(results)['trifloxystrobin'], 'loq', 'limit') == (0.1, 0.2)

def test_terpenes_right_hand_table():
    # cis-beta-Ocimene is the isomer, cis_ocimene, since cannlytics 1.0.6
    # (it was the isomer mixture, beta_ocimene).
    found = _by_key(_results(APOLLO_TERPENES))
    for key in ('cis_ocimene', 'citronellol', 'eucalyptol', 'fenchone',
                'gamma_terpinene', 'guaiol'):
        assert _f(found[key], 'value', 'qualifier', 'units') == (None, 'ND', 'percent')

def test_rows_skipped_as_headers_or_aromas_are_read():
    """r10 skipped "MGK-264" rows as a units header ('mg') and "Pinene"
    rows as an aroma line ('Pine')."""
    found = _by_key(_results("""Pesticides Pass
Analyte LOD LOQ Limit Mass Status
µg/g µg/g µg/g µg/g
MGK-264 0.03 0.1 0.1 ND Pass
Terpenes Complete
Analyte LOQ Mass Mass
% % mg/g
Pinene 0.001 0.0472 0.472"""))
    assert _f(found['mgk_264'], 'limit', 'qualifier') == (0.1, 'ND')
    assert found['pinene']['value'] == 0.0472

def test_canonical_keys():
    """'B1' is 'aflatoxin_b1', Greek letters are kept, method notes are
    dropped (r10: 'b1', 'thujone', 'three_carene', 'cy_uthrin',
    'e_coli_by_traditional_plating_sop_13')."""
    assert cc._snake_case('B1') == 'aflatoxin_b1'
    assert cc._snake_case('α-Thujone') == 'alpha_thujone'
    assert cc._snake_case('3-Carene') == 'delta_3_carene'
    assert cc._snake_case('Cyﬂuthrin') == 'cyfluthrin'
    assert cc._snake_case('E. Coli by traditional plating: SOP-13') == 'e_coli'
    assert cc._snake_case('Salmonella SPP by QPCR: SOP-15') == 'salmonella'
    assert cc._snake_case('Endo-Fenchyl Alcohol') == 'fenchol'
    assert cc._snake_case('DDVP') == 'dichlorvos'
    assert cc._snake_case('Δ9-THC') == 'delta_9_thc'
    assert cc._snake_case('Spinosyn (A + D)') == 'spinosad'

def test_name_flags_and_cas_numbers():
    found = _by_key(_results("""Cannabinoids Complete
Analyte LOQ Mass Mass
% % mg/g
CBCa Q3 0.1 0.2000 2.000
THCa 23978-85-0 0.1 ND ND
Mycotoxins Pass
Analyte LOD LOQ Limit Mass Status
µg/kg µg/kg µg/kg µg/kg
Aflatoxin G2 5 10 20 ND Pass"""))
    assert _f(found['cbca'], 'name', 'value') == ('CBCa', 0.2)
    assert found['thca']['name'] == 'THCa'
    assert found['aflatoxin_g2']['name'] == 'Aflatoxin G2'

# ── Regression: formats the r10 parser already read correctly ─────
#
# The benchmark agreed on 79 pesticide and 17 residual-solvent rows.
# These assert what r10 read (value, LOD, LOQ, limit, status), which
# still holds; the conventions added since (qualifier, units as
# printed) are asserted in test_pesticide_and_solvent_conventions.

def test_regression_pesticides_left_hand_table():
    found = _by_key(_results(APOLLO_PESTICIDES))
    expected = {
        'abamectin': (0.25, 0.5), 'acephate': (0.2, 0.4), 'bifenazate': (0.1, 0.2),
        'daminozide': (0.5, 1.0), 'dichlorvos': (0.05, 0.1), 'fludioxonil': (0.2, 0.4),
    }
    for key, (loq, limit) in expected.items():
        assert _f(found[key], 'value', 'loq', 'limit', 'status') == (None, loq, limit, 'pass')

def test_regression_pesticides_one_table_with_lod():
    found = _by_key(_results("""Pesticides Fail
Analyte LOD LOQ Limit Mass Status
µg/g µg/g µg/g µg/g
Abamectin 0.03 0.1 0.1 ND Pass
Bifenazate 0.03 0.1 0.1 0.25 Fail
Spinosyn (A + D) 0.03 0.1 3 ND Pass"""))
    assert _f(found['bifenazate'], 'value', 'status') == (0.25, 'fail')
    assert _f(found['bifenazate'], 'lod', 'loq', 'limit') == (0.03, 0.1, 0.1)
    assert _f(found['abamectin'], 'value', 'units') == (None, 'ug/g')
    assert found['spinosad']['limit'] == 3.0

def test_regression_pesticides_without_header_row():
    found = _by_key(_results("""Pesticides Pass
Abamectin 0.03 0.1 0.1 ND Pass
Bifenazate 0.03 0.1 0.1 0.25 Fail
Acephate 0.2 0.4 ND Pass"""))
    assert _f(found['abamectin'], 'value', 'lod', 'loq', 'limit') == (None, 0.03, 0.1, 0.1)
    assert found['bifenazate']['value'] == 0.25
    assert _f(found['acephate'], 'value', 'loq', 'limit') == (None, 0.2, 0.4)

def test_regression_potency_rows_without_header_row():
    """Without a header, "LOQ Result" rows stay LOQ and result, even
    when the result is ten times the LOQ ('0.001', '0.0100'): only a
    percent and its mg/g printed with the same digits are a pair."""
    found = _by_key(_results("""Terpenes Complete
β-Pinene 0.001 0.0100
Linalool 0.001 0.2734"""))
    assert _f(found['beta_pinene'], 'value', 'loq') == (0.01, 0.001)
    assert _f(found['linalool'], 'value', 'loq') == (0.2734, 0.001)

def test_regression_residual_solvents_one_table():
    found = _by_key(_results(APOLLO_SOLVENTS))
    expected = {
        'acetone': (381.0, 1000.0), 'ethyl_acetate': (1907.0, 5000.0),
        'n_heptane': (1892.0, 5000.0), 'xylenes_ethyl_benzene': (841.0, 2170.0),
    }
    for key, (loq, limit) in expected.items():
        assert _f(found[key], 'value', 'loq', 'limit', 'status') == (None, loq, limit, 'pass')

def test_regression_residual_solvents_two_tables():
    found = _by_key(_results("""Residual Solvents Pass
Analyte LOQ Limit Mass Status Analyte LOQ Limit Mass Status
PPM PPM PPM PPM PPM PPM
Acetone 500 1000 ND Pass Hexanes 145 290 ND Pass
Acetonitrile 205 410 ND Pass Methanol 1500 3000 ND Pass
Benzene 1 2 ND Pass Propane 2500 5000 1200 Pass"""))
    expected = {'acetone': (500.0, 1000.0), 'acetonitrile': (205.0, 410.0), 'benzene': (1.0, 2.0)}
    for key, (loq, limit) in expected.items():
        assert _f(found[key], 'value', 'loq', 'limit') == (None, loq, limit)

def test_regression_louisiana_footer_ends_the_tables():
    """Disclaimer lines after "ND=Not Detected" are not result rows."""
    results = _results("""Pesticides Pass
Analyte LOQ Limit Mass Status
PPM PPM PPM
Abamectin 0.25 0.5 ND Pass
ND=Not Detected; LOQ=Limit of Quantitation
Values reported relate only to the sample 1 2 3 tested""")
    assert [r['key'] for r in results] == ['abamectin']

def test_pesticide_and_solvent_conventions():
    """Non-detects are qualified 'ND' and units are as printed ('ppm'),
    on both tables of a line; a measured solvent is a number."""
    for row in _results(APOLLO_PESTICIDES, APOLLO_SOLVENTS):
        assert _f(row, 'value', 'qualifier', 'units', 'lod') == (None, 'ND', 'ppm', None)
        assert row['limit'] is not None
    found = _by_key(_results("""Residual Solvents Pass
Analyte LOQ Limit Mass Status Analyte LOQ Limit Mass Status
PPM PPM PPM PPM PPM PPM
Benzene 1 2 ND Pass Propane 2500 5000 1200 Pass"""))
    assert _f(found['propane'], 'value', 'qualifier', 'loq') == (1200.0, '', 2500.0)
    assert set(found) == {'benzene', 'propane'}

# ── End to end ────────────────────────────────────────────────────

def test_parse_cc_coa_end_to_end(monkeypatch):
    """parse_cc_coa, with a stand-in for pdfplumber, reports each
    benchmark disagreement as the COAs print it."""
    page1 = ('Regulatory Compliance Testing\n'
             'OnPoint Laboratories (928) 555-0101\n'
             '83.9504% ND 88.0082%\n'
             'Total THC Total CBD Total Cannabinoids\n'
             + ONPOINT_2023 + '\nConfident Cannabis All Rights Reserved')
    pages = [page1, APOLLO_TERPENES]

    @contextlib.contextmanager
    def fake_open(path):
        yield SimpleNamespace(pages=[_Page(text) for text in pages])

    monkeypatch.setattr(cc, 'pdfplumber', SimpleNamespace(open=fake_open))
    obs = cc.parse_cc_coa(None, '/tmp/onpoint.pdf')
    found = _by_key(json.loads(obs['results']))
    assert _f(found['delta_9_thc'], 'value', 'units') == (83.9504, 'percent')
    assert _f(found['arsenic'], 'value', 'qualifier', 'units') == (None, '<LOQ', 'ppb')
    assert _f(found['e_coli'], 'value', 'qualifier') == (None, '<LOQ')
    assert _f(obs, *TOTALS) == (83.9504, None, 88.0082)
    # Total terpenes sums the terpenes read in percent.
    assert obs['total_terpenes'] == pytest.approx(0.4816 + 0.3463 + 0.2951 + 0.048)
    assert 'heavy_metals' in json.loads(obs['analyses'])
    assert obs['coa_pdf'] == 'onpoint.pdf'

# ── Review of 10/14/2026 ──────────────────────────────────────────

def test_a_word_limit_is_not_the_result():
    """A limit printed in words comes before the result word: salmonella
    and aspergillus were found, not non-detects."""
    found = _by_key(_results("""Microbials Fail
Analyte Limit Mass Status
CFU/g CFU/g
Salmonella Not Detected in 1g Detected in 1g Fail
Aspergillus flavus Absence in 1g Presence Fail
E. Coli 100 <10 Pass"""))
    assert _f(found['salmonella'], 'value', 'qualifier', 'status') == (None, 'detected', 'fail')
    assert _f(found['aspergillus_flavus'], 'value', 'qualifier', 'status') == (None, 'detected', 'fail')
    assert _f(found['e_coli'], 'value', 'qualifier', 'loq', 'limit') == (None, '<LOQ', 10.0, 100.0)


def test_the_longer_of_two_side_by_side_tables_keeps_its_analysis_and_units():
    """Rows past the end of the left table are the right table's:
    ochratoxin A is 12 ug/kg of mycotoxin, not 12 ppm of heavy metal."""
    found = _by_key(_results("""Heavy Metals Pass Mycotoxins Pass
Analyte LOQ Limit Mass Status Analyte LOQ Limit Mass Status
PPM PPM PPM µg/kg µg/kg µg/kg
Arsenic 0.133 0.4 ND Pass B1 10 20 ND Pass
Lead 0.333 1 ND Pass B2 10 20 ND Pass
G1 10 20 ND Pass
Ochratoxin A 10 20 12 Pass"""))
    assert _f(found['ochratoxin_a'], 'analysis', 'value', 'units') == ('mycotoxins', 12.0, 'ug/kg')
    assert _f(found['aflatoxin_g1'], 'analysis', 'qualifier', 'units') == ('mycotoxins', 'ND', 'ug/kg')
    assert _f(found['lead'], 'analysis', 'units', 'limit') == ('heavy_metals', 'ppm', 1.0)
