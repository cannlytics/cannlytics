"""
Regression tests for the 10/30/2026 (R15) changes to kaycha.py (1.3.0).

Four Albany (NY) COAs of 2024-2025 that every AI arm of the parsing
benchmark read correctly showed the algorithm reading heavy metals'
action limits as results, filing microbials as mycotoxins, dropping the
right-hand column of two-column tables, and reading the page's footer and
interleaved letters as pesticides. A differential run over 113 Kaycha
COAs from Florida, Arizona and New York (old against new) changed no
reading other than these. The lines below follow pdfplumber's text of
those COAs; every value is invented.

Run:
    pytest tests/test_coas/test_algorithms/test_kaycha_r15.py -v
"""
from cannlytics.data.coas.algorithms import kaycha


def by_key(rows, key):
    found = [r for r in rows if r['key'] == key]
    assert len(found) == 1, (key, [r['key'] for r in rows])
    return found[0]


# ── 1. A status printed against the result ─────────────────────────────

HEAVY_METALS = (
    'Heavy Metals PASSED\n'
    'Metal LOQ Units Result Pass / Action\n'
    'Fail Level\n'
    'ANTIMONY 0.1000 ug/g <0.1000PASS 2\n'
    'CADMIUM 0.1000 ug/g <0.1000PASS 0.3\n'
    'COPPER 1.0000 ug/g 12.3456PASS 30\n'
    'NICKEL 0.1000 ug/g 1.2345 PASS 5\n'
    'Weight:\n'
    '0.5000g\n'
)


def test_a_glued_status_is_split_from_its_result():
    assert kaycha._tokenize('ANTIMONY 0.1000 ug/g <0.1000PASS 2') == [
        'ANTIMONY', '0.1000', 'ug/g', '<0.1000', 'PASS', '2']
    assert kaycha._tokenize('LEAD 0.1000 ug/g 0.9000FAIL 0.5')[-3:] == ['0.9000', 'FAIL', '0.5']
    assert kaycha._tokenize('ARSENIC ppm 0.0660 0.2000 0.4 NDPASSED')[-2:] == ['ND', 'PASSED']


def test_a_word_ending_in_pass_is_not_split():
    assert kaycha._tokenize('BYPASS COMPASS 0.1 PASS ND') == ['BYPASS', 'COMPASS', '0.1', 'PASS', 'ND']


def test_heavy_metals_below_the_loq_are_not_read_as_their_action_limits():
    for parse in (kaycha._parse_section_fl, kaycha._parse_section_tabular):
        rows = parse(HEAVY_METALS, 'Heavy Metal', 'heavy_metals', 'ppm', location='albany')
        antimony = by_key(rows, 'antimony')
        assert (antimony['value'], antimony['qualifier'], antimony['loq'], antimony['limit']) == (
            None, '<LOQ', 0.1, 2.0)
        cadmium = by_key(rows, 'cadmium')
        assert (cadmium['value'], cadmium['limit'], cadmium['status']) == (None, 0.3, 'pass')


def test_a_measured_metal_is_read_whether_or_not_its_status_is_glued():
    rows = kaycha._parse_section_fl(HEAVY_METALS, 'Heavy Metal', 'heavy_metals', 'ppm',
                                    location='albany')
    copper, nickel = by_key(rows, 'copper'), by_key(rows, 'nickel')
    assert (copper['value'], copper['loq'], copper['limit']) == (12.3456, 1.0, 30.0)
    assert (nickel['value'], nickel['loq'], nickel['limit']) == (1.2345, 0.1, 5.0)
    assert not any(r['value'] == r['limit'] for r in rows if r['value'] is not None)


# ── 2. Two records on one line ─────────────────────────────────────────

PESTICIDES = (
    'Pesticides PASSED\n'
    'Pesticide LOQ Units Action LevelPass/Fail Result Pesticide LOQ Units Action Level Pass/Fail Result\n'
    'ACEQUINOCYL 0.1000 ppm 2 PASS <0.1000 PACLOBUTRAZOL 0.1000 ppm 0.4 PASS <0.1000\n'
    'PYRETHRINS, TOTAL 0.1000 ppm 1 PASS <0.1000 PERMETHRIN 0.1000 ppm 0.2 PASS 0.1500\n'
    'CHLORMEQUAT CHLORIDE 0.1000 ppm 1 PASS <0.1000 CAPTAN * 0.1000 ppm 1 PASS <0.1000\n'
)


def test_both_records_of_a_two_column_line_are_read():
    rows = kaycha._parse_pesticides_tabular(PESTICIDES, location='albany')
    assert [r['key'] for r in rows] == [
        'acequinocyl', 'paclobutrazol', 'permethrin', 'chlormequat_chloride', 'captan']  # totals are skipped
    paclobutrazol = by_key(rows, 'paclobutrazol')
    assert (paclobutrazol['value'], paclobutrazol['qualifier'], paclobutrazol['limit']) == (
        None, '<LOQ', 0.4)
    permethrin = by_key(rows, 'permethrin')
    assert (permethrin['value'], permethrin['limit']) == (0.15, 0.2)


def test_the_left_record_keeps_its_own_cells():
    acequinocyl = by_key(kaycha._parse_pesticides_tabular(PESTICIDES, location='albany'),
                         'acequinocyl')
    assert (acequinocyl['value'], acequinocyl['limit'], acequinocyl['loq']) == (None, 2.0, 0.1)


def test_split_records_starts_a_record_at_a_name_after_cells():
    tokens = kaycha._tokenize('ACEPHATE 0.1000 ppm 0.4 PASS <0.1000 PYRIDABEN 0.1000 ppm 0.2 PASS ND')
    records = kaycha._split_records(tokens)
    assert [r[0] for r in records] == ['ACEPHATE', 'PYRIDABEN']
    # A flag after a result ("0.1575 Q3") does not start a record.
    assert len(kaycha._split_records(kaycha._tokenize('THCA 0.1 PASS 0.1575 Q3'))) == 1


# ── 3. Two sections side by side ───────────────────────────────────────

MICRO_MYCO = (
    'Microbial PASSED Mycotoxins PASSED\n'
    'Analyte LOQ Units Result Pass / Action Analyte LOQ Units Result Pass / Action\n'
    'Fail Level Fail Level\n'
    'TOTAL AEROBIC BACTERIA 100 CFU/g <100 PASS 10000 AFLATOXIN G2 0.0025 ppm <0.0025PASS 0.02\n'
    'TOTAL YEAST AND MOLD 100 CFU/g 300 PASS 1000 AFLATOXIN G1 0.0025 ppm <0.0025PASS 0.02\n'
    'ESCHERICHIA COLI SHIGELLA 1 Not Present PASS AFLATOXIN B2 0.0025 ppm <0.0025PASS 0.02\n'
    'SPP AFLATOXIN B1 0.0025 ppm <0.0025PASS 0.02\n'
    'SALMONELLA SPECIES 1 Not Present PASS OCHRATOXIN A+ 0.0100 ppm <0.0100PASS 0.02\n'
    'ASPERGILLUS TERREUS 1 Not Present PASS TOTAL AFLATOXINS (B1, B2, G1, G2) 0.0025 ppm <0.0025PASS 0.02\n'
    'ASPERGILLUS NIGER 1 Not Present PASS\n'
    'Weight:\n'
    'ASPERGILLUS FLAVUS 1 Not Present PASS 0.5000g\n'
    'Analysis Method : SOP.T.30.104.NY\n'
)


def test_which_column_a_section_is_on_its_title_line():
    left, split = kaycha._column_of('Microbial PASSED Mycotoxins PASSED', 'Microbial')
    assert left == 'left' and split is not None
    right, split = kaycha._column_of('Microbial PASSED Mycotoxins PASSED', 'Mycotoxin')
    assert right == 'right' and split is not None
    assert kaycha._column_of('Heavy Metals PASSED', 'Heavy Metal') == ('', None)


def test_mycotoxins_are_read_from_their_own_column():
    rows = kaycha._parse_section_fl(MICRO_MYCO, 'Mycotoxin', 'mycotoxins', 'ppm', location='albany')
    assert sorted(r['key'] for r in rows) == [
        'aflatoxin_b1', 'aflatoxin_b2', 'aflatoxin_g1', 'aflatoxin_g2', 'ochratoxin_a', 'total_aflatoxins']
    b1 = by_key(rows, 'aflatoxin_b1')
    assert (b1['value'], b1['qualifier'], b1['loq'], b1['limit']) == (None, '<LOQ', 0.0025, 0.02)


def test_microbials_are_not_filed_with_the_mycotoxins_beside_them():
    rows = kaycha._parse_section_fl(MICRO_MYCO, 'Microbial', 'microbials', 'CFU/g', location='albany')
    keys = [r['key'] for r in rows]
    assert not any('aflatoxin' in k or 'ochratoxin' in k for k in keys)
    assert {'total_aerobic_bacteria', 'total_yeast_and_mold', 'salmonella', 'aspergillus_niger'} <= set(keys)
    assert by_key(rows, 'total_yeast_and_mold')['value'] == 300.0


def test_the_tabular_parser_routes_columns_the_same_way():
    myco = kaycha._parse_section_tabular(MICRO_MYCO, 'Mycotoxin', 'mycotoxins', 'ppm', location='albany')
    assert len(myco) == 6 and all(r['qualifier'] == '<LOQ' for r in myco)


SIDE_BY_SIDE = (
    'Water Activity PASSED Moisture PASSED\n'
    'Analyte LOQ Units Result P/F Action Level Analyte LOQ Units Result P/F Action Level\n'
    'WATER ACTIVITY 0.10 aw 0.45 PASS 0.65 MOISTURE CONTENT 5.0 % 10.2 PASS 15\n'
    'Weight:\n'
    'Analysis Method : SOP.T.40.019\n'
)


def test_a_right_hand_section_without_a_known_split_reads_the_records_after_the_first():
    line = 'WATER ACTIVITY 0.10 aw 0.45 PASS 0.65 MOISTURE CONTENT 5.0 % 10.2 PASS 15'
    assert [' '.join(n) for n, _ in kaycha._section_records(line, 'left')] == ['WATER ACTIVITY']
    assert [' '.join(n) for n, _ in kaycha._section_records(line, 'right')] == ['MOISTURE CONTENT']
    # A line with one record is taken to be the left column's.
    assert kaycha._section_records('WATER ACTIVITY 0.10 aw 0.45 PASS 0.65', 'right') == []


def test_water_activity_is_not_filed_as_the_moisture_beside_it():
    assert kaycha._column_of(SIDE_BY_SIDE.split('\n')[0], 'Moisture') == ('right', None)
    for parse in (kaycha._parse_section_fl, kaycha._parse_section_tabular):
        moisture = parse(SIDE_BY_SIDE, 'Moisture', 'moisture', 'percent', location='albany')
        assert [(r['key'], r['value']) for r in moisture] == [('moisture_content', 10.2)]
        water = parse(SIDE_BY_SIDE, 'Water Activity', 'water_activity', 'aw', location='albany')
        assert [(r['key'], r['value']) for r in water] == [('water_activity', 0.45)]


# ── 4. What is not a row ───────────────────────────────────────────────

FOOTER = (
    'Pesticides PASSED\n'
    'ACEPHATE 0.1000 ppm 0.4 PASS <0.1000 PYRIDABEN 0.1000 ppm 0.2 PASS <0.1000\n'
    'A I M P N I Z Y P D A C E O D L R L O I O R E B N - A 3 U Y C 0 0 0 0 . . . . 1 1 1 1 '
    'p p p p m m m m P P A A S S < < 0 0 . .\n'
    'W 0 A A\n'
    'are terms used to describe the smallest concentration that can be detected and reliably measured\n'
    'procedure, respectively. Action Levels are State determined thresholds based on 9 New York Codes, '
    'Rules and ISO 17025 Accreditation # 99999\n'
    'Regulations (NYCRR) Part 130 and Cannabis Law. The Measurement of Uncertainty (MU) error is available\n'
)


def test_interleaved_letters_and_the_footer_are_not_pesticides():
    rows = kaycha._parse_pesticides_tabular(FOOTER, location='albany')
    assert [r['key'] for r in rows] == ['acephate', 'pyridaben']


def test_an_interleaved_line_and_a_lone_letter_are_recognized():
    line = 'A I M P N I Z Y P D A C E O D 0 0 0 0 . . . . 1 1 1 1'
    assert kaycha._is_interleaved(kaycha._tokenize(line))
    assert not kaycha._is_interleaved(kaycha._tokenize('SALMONELLA SPECIES 1 Not Present PASS'))
    assert kaycha._is_spaced_letters(['W'])
    assert not kaycha._is_spaced_letters(['AFLATOXIN', 'B1'])


BELOW_THE_NOTES = (
    'Pesticides PASSED\n'
    'CHLORPYRIFOS 0.0050 ppm 0.2 PASS ND\n'
    'Analyzed by: Weight: Extraction date: Extracted by:\n'
    'CLOFENTEZINE 0.0100 ppm 0.2 PASS ND 101, 202, 33 0.5000g 09/01/23 17:04:16 56\n'
    'Dilution : 25\n'
    'Reagent : 010101.R01; 020202.R02\n'
    'DIMETHOATE 0.0060 ppm 0.2 PASS ND Dilution : 25\n'
    'Residual Solvents PASSED\n'
    'ACETONE 75.000 ppm 750 PASS ND\n'
)


def test_a_table_goes_on_below_its_method_notes_until_the_next_section():
    rows = kaycha._parse_pesticides_tabular(BELOW_THE_NOTES, location='tempe')
    assert [r['key'] for r in rows] == ['chlorpyrifos', 'clofentezine', 'dimethoate']


def test_a_title_line_prints_a_section_status_and_no_result():
    assert kaycha._is_title_line('Vitamin E Acetate PASSED')
    assert kaycha._is_title_line('PASSED')
    assert kaycha._is_title_line('Microbial PASSED Mycotoxins PASSED')
    assert not kaycha._is_title_line('ACEPHATE 0.1000 ppm 0.4 PASS <0.1000')
    assert not kaycha._is_title_line('TOTAL AEROBIC BACTERIA 100 CFU/g <100 TESTED')
    assert not kaycha._is_title_line('SALMONELLA SPECIES Not Present PASSED')


def test_a_section_the_algorithm_does_not_know_ends_the_table():
    for title in ('Vitamin E Acetate PASSED\n', 'PASSED\nVitamin E Acetate\n'):
        text = (
            'Pesticides PASSED\n'
            'CHLORPYRIFOS 0.0050 ppm 0.2 PASS ND\n'
            'Analyzed by: Weight: Extraction date: Extracted by:\n'
            'DIMETHOATE 0.0060 ppm 0.2 PASS ND Dilution : 25\n'
            + title +
            'VITAMIN E ACETATE 0.1000 ppm 0.1 PASS ND\n'
        )
        rows = kaycha._parse_pesticides_tabular(text, location='albany')
        assert [r['key'] for r in rows] == ['chlorpyrifos', 'dimethoate'], title


def test_another_analysis_analyte_is_never_a_pesticide():
    text = (
        'Pesticides PASSED\n'
        'CHLORPYRIFOS 0.0050 ppm 0.2 PASS ND ARSENIC 0.1000 ppm 0.2 PASS <0.1000\n'
        'Analyzed by: Weight: Extraction date: Extracted by:\n'
        'DIMETHOATE 0.0060 ppm 0.2 PASS ND\n'
        'SALMONELLA SPECIES 1 Not Present PASS\n'
        'TOTAL YEAST AND MOLD 100 CFU/g 300 PASS 1000\n'
    )
    rows = kaycha._parse_pesticides_tabular(text, location='albany')
    assert [r['key'] for r in rows] == ['chlorpyrifos', 'dimethoate']


# ── 5. Interleaved rows are read again at a tighter tolerance ──────────

class FakePage:
    """A page whose text depends on the line tolerance asked for."""

    def __init__(self, default: str, tight: str):
        self.default, self.tight, self.calls = default, tight, []

    def extract_text(self, **kwargs):
        self.calls.append(kwargs)
        return self.tight if kwargs.get('y_tolerance') == kaycha._TIGHT_Y_TOLERANCE else self.default


def test_a_page_with_interleaved_rows_is_read_again():
    page = FakePage(FOOTER, PESTICIDES)
    assert kaycha._page_text(page) == PESTICIDES
    assert page.calls == [{}, {'y_tolerance': kaycha._TIGHT_Y_TOLERANCE}]


def test_a_clean_page_is_read_once():
    page = FakePage(PESTICIDES, FOOTER)
    assert kaycha._page_text(page) == PESTICIDES
    assert page.calls == [{}]


def test_the_default_text_is_kept_when_the_tight_text_is_no_better():
    page = FakePage(FOOTER, FOOTER)
    assert kaycha._page_text(page) == FOOTER
