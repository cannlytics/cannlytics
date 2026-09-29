"""
Tests for the deprecated `cannlytics.data.constants`
====================================================
The module is an alias of `cannlytics.constants` through 1.x. Its own
label tables were retired in 1.0.5 (see its docstring).
"""
import importlib
import sys

import pytest

import cannlytics.constants as canonical

def _fresh_import():
    sys.modules.pop('cannlytics.data.constants', None)
    return importlib.import_module('cannlytics.data.constants')

def test_importing_it_warns_and_names_the_new_location():
    with pytest.warns(DeprecationWarning, match='import from cannlytics.constants'):
        _fresh_import()

def test_it_re_exports_the_canonical_objects_themselves():
    with pytest.warns(DeprecationWarning):
        legacy = _fresh_import()
    for name in ('ANALYTE_ALIASES', 'normalize_analyte_key', 'US_STATES', 'DECARB', 'RANDOM_STRING_CHARS', 'COMPOUNDS'):
        assert getattr(legacy, name) is getattr(canonical, name)
    assert legacy.PRODUCT_TYPES is canonical.METRC_PRODUCT_TYPES
    assert legacy.state_time_zones is canonical.TIME_ZONES and legacy.state_names['New Jersey'] == 'NJ'

@pytest.mark.parametrize('name', ['ANALYSES', 'ANALYTES', 'STANDARD_FIELDS', 'STRAINS'])
def test_the_retired_tables_are_gone(name):
    with pytest.warns(DeprecationWarning):
        legacy = _fresh_import()
    assert not hasattr(legacy, name)
