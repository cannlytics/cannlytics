"""
Regression tests for the 10/18/2026 (R13) changes to kaycha.py (1.2.0).

Arizona COAs of 2025 inside compiled packets, read by the AI in the
cannabis_results dataset, showed two misreadings on the Kaycha page
itself: "Completed: 04/14/25" ends its line, and the date took the next
line's first word ("04/14/25\\nProduction", kept as text); and "Total
Cannabinoids" prints a line below "Total THC  Total CBD", between the
labels and the values, so total THC was not read. The lines follow
pdfplumber's text of those COAs; names and IDs are invented.

Run:
    pytest tests/test_coas/test_algorithms/test_kaycha_r13.py -v
"""
from cannlytics.data.coas.algorithms import kaycha

HEADER = """Kaycha Labs
Example Infused 3.5 G.
1231 W. Warner Road, Suite 105 Matrix: Flower
Harvest/Lot ID: EX-0001 Lab ID: TE00000000-001
Batch #: EX-0001 Sampled: 04/08/25
Manufacturing Date: 04/07/25 Completed: 04/14/25
Production Method: Butane Revised: 04/16/25
Sampled Date: 2025-04-08 17:44:22"""


def test_a_date_ends_its_line():
    obs = kaycha._parse_metadata(HEADER, HEADER.split('\n'), 'az')
    assert obs['date_tested'] == '2025-04-14'
    assert '\n' not in obs.get('date_collected', '')


def test_a_date_keeps_its_time_on_its_line():
    text = 'Completed: 04/14/25 05:30 PM\nProduction Method: Butane'
    assert kaycha._parse_metadata(text, text.split('\n'), 'az')['date_tested'] == '2025-04-14'


def test_totals_under_a_label_printed_a_line_lower():
    lines = ['Cannabinoid PASSED', 'Total THC Total CBD Q3', 'Total Cannabinoids',
             '44.3561% ND 51.2430%', 'D9-THC THCA CBD']
    obs = kaycha._parse_totals('\n'.join(lines), lines)
    assert (obs['total_thc'], obs['total_cbd'], obs['total_cannabinoids']) == (44.3561, None, 51.243)


def test_totals_on_the_next_line_as_before():
    lines = ['Total THC Total CBD Total Cannabinoids', '25.5961% <0.1000 29.7057%']
    obs = kaycha._parse_totals('\n'.join(lines), lines)
    assert (obs['total_thc'], obs['total_cbd'], obs['total_cannabinoids']) == (25.5961, None, 29.7057)


def test_a_line_that_is_not_a_row_of_totals_is_not_read_as_one():
    """Numbers on the next lines that do not start the line ("Sample Size
    3.5 g 2 units") are not totals, one line down or two."""
    for lines in (['Total THC Total CBD', 'Total Cannabinoids', 'Sample Size 3.5 g 2 units'],
                  ['Total THC Total CBD', 'Sample Size 3.5 g 2 units'],
                  ['Total THC Total CBD Total Cannabinoids', 'Sample Size 3.5 g 2 units']):
        obs = kaycha._parse_totals('\n'.join(lines), lines)
        assert obs.get('total_thc') is None and obs.get('total_cbd') is None, lines
