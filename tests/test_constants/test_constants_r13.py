"""
Analyte keys corrected on 10/18/2026 (R13).

Delta-10 THC printed without its isomer is ``delta_10_thc`` (it was the
9R isomer for some spellings and not for others); Shiga toxin-producing
Escherichia coli is ``stec`` whichever way E. coli is spelled.
"""
import pytest

from cannlytics.constants.analytes import normalize_analyte_key


@pytest.mark.parametrize('name', ['D10 THC', 'D10-THC', 'd10thc', 'delta10thc', 'Delta-10 THC',
                                  'Delta-10 Tetrahydrocannabinol', 'D 10 THC'])
def test_delta_10_thc_without_its_isomer(name):
    assert normalize_analyte_key(name) == 'delta_10_thc'


@pytest.mark.parametrize('name, key', [('(6aR,9R)-d10-THC', '9r_delta_10_thc'), ('(6aR,9S)-d10-THC', '9s_delta_10_thc'),
                                       ('d10/R9-THC', '9r_delta_10_thc'), ('d10/S9-THC', '9s_delta_10_thc')])
def test_delta_10_thc_isomers_keep_their_keys(name, key):
    assert normalize_analyte_key(name) == key


@pytest.mark.parametrize('name', ['Shiga Toxin Producing E. coli', 'Shiga Toxin Producing Escherichia coli', 'STEC'])
def test_stec(name):
    assert normalize_analyte_key(name) == 'stec'
