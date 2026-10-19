"""
Regression tests for the 10/16/2026 (R12) change to kaycha.py (1.1.1).

R11's runs printed "D9-THC + 0.877 * THCA disagrees with the printed
Total THC ...; keeping the header alignment." thousands of times: New
York labs may print Total THC with delta-8 THC and the delta-10 isomers
added, which the check did not allow. The check now accepts either
total; the notes are counted in ``kaycha.ALIGNMENT_NOTES`` and logged at
debug level, and only dropped rows are a warning.

Run:
    pytest tests/test_coas/test_algorithms/test_kaycha_r12.py -v
"""
import logging

import pytest

from cannlytics.data.coas.algorithms import kaycha

LOGGER = 'cannlytics.data.coas.algorithms.kaycha'
NAMES = ['D9-THC', 'THCA', 'D8-THC', '(6AR,9R) D10-THC', '(6AR,9S) D10-THC']


def pairs(names=NAMES):
    return [(name, i) for i, name in enumerate(names)]


@pytest.mark.parametrize('cells, total, expected', [
    (['1.000', '20.000', 'ND', 'ND', 'ND'], 18.54, True),            # D9 + 0.877 x THCA
    (['1.000', '20.000', '2.000', '0.500', 'ND'], 21.04, True),      # plus D8 and a D10 isomer (NY)
    (['1.000', '20.000', '2.000', '0.500', 'ND'], 18.54, True),      # the plain formula still counts
    (['1.000', '20.000', '2.000', '0.500', 'ND'], 25.00, False),     # neither
    (['ND', 'ND', '2.000', 'ND', 'ND'], 2.00, True),                 # D9-THC and THCA not detected
    (['1.000', '20.000', 'ND', 'ND', 'ND'], None, None),             # no total printed
])
def test_total_thc_check_allows_delta_8_and_delta_10(cells, total, expected):
    assert kaycha._total_thc_check(pairs(), cells, total) is expected


def test_total_thc_check_needs_delta_9_or_thca():
    names = ['D8-THC', 'CBD']
    assert kaycha._total_thc_check(pairs(names), ['2.000', 'ND'], 2.0) is None


def test_alignment_notes_are_counted_not_warned(caplog):
    caplog.set_level(logging.DEBUG, logger=LOGGER)
    kaycha.ALIGNMENT_NOTES.clear()
    names = ['D9-THC', 'THCA', 'CBD']
    # Explained by the header (one cell per name), the total disagrees: kept, counted.
    kept = kaycha._align_cannabinoids(names, [], ['1.0', '20.0', 'ND'], 50.0)
    assert kept == [('D9-THC', 0), ('THCA', 1), ('CBD', 2)]
    # The total agrees: the header's alignment, counted.
    kaycha._align_cannabinoids(names, [], ['1.0', '20.0', 'ND'], 18.54)
    assert kaycha.ALIGNMENT_NOTES == {'header, total disagrees': 1, 'header': 1}
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
    assert [r for r in caplog.records if r.levelno == logging.DEBUG and 'keeping' in r.getMessage()]


def test_rows_that_cannot_be_aligned_are_still_a_warning(caplog):
    caplog.set_level(logging.WARNING, logger=LOGGER)
    kaycha.ALIGNMENT_NOTES.clear()
    # Four cells for three names, and no alignment agrees with the total.
    assert kaycha._align_cannabinoids(['D9-THC', 'THCA', 'CBD'], [], ['9.0', '1.0', '20.0', 'ND'], 70.0) == []
    assert kaycha.ALIGNMENT_NOTES['dropped'] == 1
    assert [r for r in caplog.records if 'dropped' in r.getMessage()]
