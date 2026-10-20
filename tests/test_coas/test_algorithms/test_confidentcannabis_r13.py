"""
Tests for the Confident Cannabis COA parser fixes of 10/18/2026 (R13,
confidentcannabis 1.3.0).
Copyright (c) 2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/18/2026
Updated: 10/18/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    The cannabis_results dataset's algorithm runs remembered 80 COAs that
    this parser claimed and failed on; each was then parsed by the AI. 79
    were Bia Diagnostics (Vermont) COAs, which Confident LIMS prints: a
    pathogen panel whose header is led by its title ("Pathogens LOD
    Results"), and moisture and water activity printed only in the
    Summary table. Arizona's compiled packets (a producer's cover pages,
    then the lab's COA) lost their lab, product name and totals to the
    cover pages. The pages below follow the layouts pdfplumber printed;
    the client names, lots and sample IDs are invented.
"""
# Standard imports:
import contextlib
import json
from types import SimpleNamespace

# Internal imports:
from cannlytics.data.coas.algorithms import confidentcannabis as cc


class _Page:
    """A stand-in for a pdfplumber page."""

    def __init__(self, text: str):
        self._text = text

    def extract_text(self) -> str:
        return self._text


def _parse(monkeypatch, *pages: str) -> dict:
    """parse_cc_coa on pages of text, with a stand-in for pdfplumber."""
    @contextlib.contextmanager
    def fake_open(path):
        yield SimpleNamespace(pages=[_Page(text) for text in pages])

    monkeypatch.setattr(cc, 'pdfplumber', SimpleNamespace(open=fake_open))
    return cc.parse_cc_coa(None, '/tmp/coa.pdf')


def _by_key(obs: dict) -> dict:
    found = {}
    for result in json.loads(obs['results']):
        found.setdefault(result['key'], result)
    return found


HEADER = """QA Testing
Bia Diagnostics (802) 540-0148
480 Hercules Drive Suite 101 https://www.biadiagnostics.com/
Colchester, VT 05446 Lic# TLAB0029
1 of 1
HL 001 Example
Sample ID: BIA000000S0001 Produced: Client
Strain: HL 001 Example Collected: Example Farm
Received: 02/21/2025 Lic. # CLTV0000
Matrix: Plant Completed: 02/27/2025 1 MAIN ST
Type: Flower - Cured Batch#: HL 001 Example Barre, VT 05641
Sample Size: 6.01 g
Lot#: HL 001 Example"""

FOOTER = """Con\x00dent LIMS
All Rights Reserved
coa.support@con\x00dentlims.com
Laboratory Director www.con\x00dentlims.com
This report shall not be reproduced except in full without approval of the laboratory."""

PATHOGENS = """Pathogens Completed
Pathogens LOD Results
CFU/g CFU/g
Aspergillus 5 Not Detected
Shiga Toxin E. Coli 5 Not Detected
Salmonella SPP 5 Not Detected
Analyst: 049
Test Methodology: Bio-Rad IQ-Check PCR Kits
cfu/g = colony forming units per gram
LOD = The lowest quantity that this method can reliably detect. Any microbial growth that was not detected is assumed to be less than the
stated LOD (<LOD).
Reagent Blanks: <LOD for all analytes"""

SUMMARY = """Summary
Test Date Tested Result
Sample Complete
Moisture 09/05/2025 11.40% - Complete
Water Activity 09/05/2025 0.572 aw - Complete
All moisture and water activity analysis is determined by dewpoint measurement."""


def test_a_pathogen_panel_led_by_its_title_is_read(monkeypatch):
    obs = _parse(monkeypatch, '\n'.join((HEADER, PATHOGENS, FOOTER)))
    found = _by_key(obs)
    assert set(found) == {'aspergillus', 'stec', 'salmonella'}     # no "Analyst", "LOD =", "Reagent Blanks"
    for key in found:
        r = found[key]
        assert (r['analysis'], r['value'], r['qualifier'], r['lod'], r['units']) == \
            ('microbials', None, 'ND', 5.0, 'cfu/g')
    assert json.loads(obs['analyses']) == ['microbials']
    assert obs['lab'] == 'Bia Diagnostics'


def test_the_client_beside_the_sample_fields_is_the_producer(monkeypatch):
    obs = _parse(monkeypatch, '\n'.join((HEADER, PATHOGENS, FOOTER)))
    assert obs['producer'] == 'Example Farm'
    assert (obs['sample_id'], obs['date_tested'], obs['date_received']) == \
        ('BIA000000S0001', '2025-02-27', '2025-02-21')


def test_a_title_with_its_status_or_method_is_not_a_header():
    led = cc._title_led_columns('Pathogens LOD Results')
    assert led is not None and led[0] == 'microbials'
    assert [column[0] for group in led[1] for column in group] == ['lod', 'result']
    for line in ('Pathogens Completed', 'Cannabinoids by HPLC', 'Microbials Pass', 'Terpenes Results',
                 'Heavy Metals (PPB) Result'):
        assert cc._title_led_columns(line) is None, line


def test_moisture_and_water_activity_in_the_summary_are_results(monkeypatch):
    obs = _parse(monkeypatch, '\n'.join((HEADER, SUMMARY, FOOTER)))
    found = _by_key(obs)
    assert (found['moisture_content']['value'], found['moisture_content']['units']) == (11.4, 'percent')
    assert (found['water_activity']['value'], found['water_activity']['units']) == (0.572, 'aw')
    assert '_summary_results' not in obs


def test_a_summary_row_needs_its_units():
    """A date and a number alone ("Moisture 09/05/2025 Complete", or a
    count) are not a moisture result."""
    obs, _ = cc._parse_summary('Moisture 09/05/2025 Complete\nWater Activity 09/05/2025 12 Complete')
    assert '_summary_results' not in obs


COVER = """Final Product Information:
Product Form FLOWER
Strain EXAMPLE CAKE
Batch Number Example.B01.2025.
Arizona Dept. of Health Services Warning"""

POINTS_OF_SALE = """Intended Point of Sale Locations
Marijuana Establishment Name Marijuana Establishment License Number
Example Dispensary LLC 00000000ESXX00000000"""

APOLLO = """Regulatory Compliance Testing
Apollo Labs (602) 767-7600
17301 North Perimeter Drive http://www.apollolabscorp.com
Scottsdale, AZ 85255 Lic# 00000013LCRK62049775
1 of 2
Example Cake
Sample ID: 2511APL0001.0001 Harvest Date: 11/03/2025 Client
Strain: Example Cake Collected: Example Grower
Matrix: Plant Received: 11/14/2025
Type: Flower - Cured Completed: 11/21/2025
10.59% ND 11.90%
Total THC Total CBD Total Cannabinoids
Cannabinoids Complete
Analyte LOQ Mass Mass
% % mg/g
THCa 0.1 11.2 112
Δ9-THC 0.1 0.77 7.7
Confident Cannabis All Rights Reserved"""


def test_a_packet_is_read_from_its_first_confident_cannabis_page(monkeypatch):
    """Cover pages (one with no 'Sample ID:', one a list of points of sale,
    one empty) are skipped: the lab, product and totals are the COA's."""
    obs = _parse(monkeypatch, COVER, POINTS_OF_SALE, '', APOLLO)
    assert obs['lab'] == 'Apollo Labs'
    assert obs['product_name'] == 'Example Cake'
    assert (obs['total_thc'], obs['total_cannabinoids']) == (10.59, 11.9)
    assert _by_key(obs)['thca']['value'] == 11.2


def test_a_confident_cannabis_reference_is_not_a_marker():
    """Kaycha Labs' Arizona COAs print a Confident Cannabis sample ID and
    QR code beside their own name."""
    assert not cc._cc_page('Kaycha Labs\n* Confident Cannabis sample ID: 2603KLAZ0001.0001\nCONFIDENT CANNABIS QR')
    assert cc._cc_page('Powered by Con\x00dent LIMS')
    assert cc._coa_start(['Kaycha Labs', '* Confident Cannabis sample ID: X', APOLLO]) == 2


LEVEL_ONE = """Certi\x00cate of Analysis Powered by Con\x00dent LIMS
1 of 12
Example Sciences Sample: 2508LVL0001.0001
Example Sciences Secondary License: ; Chain of Distribution:
Phoenix, AZ 85032 Strain: Example Fumez; Batch Size: 986 g
Lic. #00000000ESXX00000000 Date of Pickup: 08/07/2025 Time Collected: 9:52
Example Fumez
Concentrates & Extracts, Other, Butane
76.24% ND
Total THC Total CBD
This product has been tested by Level One Labs, LLC using valid testing methodologies and a quality system as required by state law."""


def test_the_powered_by_template_names_its_product_and_lab(monkeypatch):
    obs = _parse(monkeypatch, LEVEL_ONE)
    assert obs['product_name'] == 'Example Fumez'
    assert obs['lab'] == 'Level One Labs, LLC'


def test_a_cover_sheet_with_the_coas_link_is_skipped(monkeypatch):
    """A cover sheet may print the COA's Confident Cannabis link; the COA
    still starts at the lab's page."""
    linked = COVER + '\nCOA: https://orders.confidentcannabis.com/report/public/sample/00000000'
    sale = POINTS_OF_SALE + '\nhttps://orders.confidentcannabis.com/report/public/sample/00000000'
    obs = _parse(monkeypatch, linked, sale, APOLLO)
    assert obs['lab'] == 'Apollo Labs'
    assert (obs['product_name'], obs['total_thc']) == ('Example Cake', 10.59)
    assert cc._coa_start([linked, sale, APOLLO]) == 2


LEVEL_ONE_PAGE_TWO = """Certi\x00cate of Analysis Powered by Con\x00dent LIMS
2 of 12
Cannabinoids Complete
Analyte LOQ Mass Mass
% % mg/g
THCa 0.1 80.1 801
This product has been tested by Level One Labs, LLC using valid testing methodologies."""


def test_a_client_block_phrase_does_not_move_the_coas_start(monkeypatch):
    """A COA's client block may print "Marijuana Establishment Name:"; the
    COA still starts at its first page."""
    page = LEVEL_ONE.replace('Example Sciences Secondary License: ;',
                             'Marijuana Establishment Name: Example Sciences Secondary License: ;')
    assert not cc._cover_page(page)
    assert cc._coa_start([page, LEVEL_ONE_PAGE_TWO]) == 0
    obs = _parse(monkeypatch, page, LEVEL_ONE_PAGE_TWO)
    assert (obs['product_name'], obs['total_thc']) == ('Example Fumez', 76.24)


def test_a_sample_identifier_keeps_a_page_in_the_coa():
    """A page printing a sample identifier ("Sample ID:", "LIMS ID:", or the
    "Powered by" template's "Sample:") is a COA's, though it print a cover
    phrase; a lab's form number in a footer is not a cover phrase."""
    for label in ('Sample ID: 2511APL0001.0001', 'LIMS ID: 0001', 'Sample: 2508LVL0001.0001'):
        assert not cc._cover_page(f'Intended Point of Sale: Example Dispensary LLC\n{label}'), label
    assert cc._cover_page(POINTS_OF_SALE)
    assert not cc._cover_page('Order Information Batch Information\nPass\nCOA Cover Sheet/Form F_QCD_00 /Version 1.1')
