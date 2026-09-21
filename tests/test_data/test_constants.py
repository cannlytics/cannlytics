"""
Tests for cannlytics.data.constants
======================================
Covers: STANDARD_ANALYSES, ANALYSES, ANALYTES, STANDARD_FIELDS,
CODINGS, states, state_names, state_time_zones data integrity.
"""
import re
from collections import Counter

import pytest

from cannlytics.data.constants import (
    STANDARD_ANALYSES,
    ANALYSES,
    ANALYTES,
    STANDARD_FIELDS,
    STANDARD_UNITS,
    PRODUCT_TYPES,
    CODINGS,
    DECARB,
    RANDOM_STRING_CHARS,
    states,
    state_names,
    state_time_zones,
)


class TestStandardAnalyses:

    def test_core_analyses_present(self):
        expected = [
            'cannabinoids', 'terpenes', 'pesticides', 'heavy_metals',
            'microbes', 'mycotoxins', 'residual_solvents',
            'foreign_matter', 'moisture_content', 'water_activity',
        ]
        for key in expected:
            assert key in STANDARD_ANALYSES, f'Missing: {key}'

    def test_all_have_name(self):
        for key, data in STANDARD_ANALYSES.items():
            assert 'name' in data, f'{key} missing name'


class TestAnalysesMap:

    def test_not_empty(self):
        assert len(ANALYSES) > 50

    def test_all_values_are_standard(self):
        """Every mapped value should be a recognized standard analysis or close variant."""
        valid_targets = set(STANDARD_ANALYSES.keys()) | {
            'microbes', 'microbials', 'moisture', 'propiconazole',
        }
        for key, value in ANALYSES.items():
            assert value in valid_targets or value.endswith('_content'), (
                f'ANALYSES["{key}"] = "{value}" is not a standard analysis'
            )

    def test_moisture_maps_to_moisture_content(self):
        """All moisture-related keys should map to 'moisture_content'."""
        moisture_keys = [k for k in ANALYSES if 'moisture' in k.lower()]
        for key in moisture_keys:
            assert ANALYSES[key] == 'moisture_content', (
                f'ANALYSES["{key}"] = "{ANALYSES[key]}", expected "moisture_content"'
            )


class TestAnalytesMap:

    def test_not_empty(self):
        assert len(ANALYTES) > 200

    def test_all_values_are_snake_case(self):
        """All target analyte keys should be valid snake_case.
        Note: chemical compounds may start with digits (e.g. '1_2_dichloroethane')."""
        snake_re = re.compile(r'^[a-z0-9][a-z0-9_]*$')
        for key, value in ANALYTES.items():
            assert snake_re.match(value), (
                f'ANALYTES["{key}"] = "{value}" is not snake_case'
            )


class TestDecarb:

    def test_value(self):
        assert DECARB == 0.877

    def test_type(self):
        assert isinstance(DECARB, float)


class TestStates:

    def test_50_states_plus_dc(self):
        assert len(states) >= 51

    def test_all_codes_are_two_letters(self):
        for code in states:
            assert len(code) == 2
            assert code == code.upper()

    def test_washington_present(self):
        assert 'WA' in states
        assert states['WA'] == 'Washington'


class TestStateNames:

    def test_reverse_map(self):
        """state_names should be the inverse of states."""
        for code, name in states.items():
            assert state_names.get(name) == code, f'{name} → {code} not in state_names'


class TestStateTimeZones:

    def test_all_states_have_timezone(self):
        for code in states:
            assert code in state_time_zones, f'{code} missing timezone'

    def test_timezones_are_valid_iana(self):
        for code, tz in state_time_zones.items():
            assert '/' in tz, f'{code} timezone "{tz}" is not IANA format'


class TestCodings:

    def test_nd_is_near_zero(self):
        assert CODINGS['ND'] > 0
        assert CODINGS['ND'] < 0.001

    def test_nr_is_none(self):
        assert CODINGS['NR'] is None
        assert CODINGS['N/A'] is None
        assert CODINGS['NT'] is None

    def test_lod_less_than_loq(self):
        assert CODINGS['<LOD'] < CODINGS['<LOQ']


class TestRandomStringChars:

    def test_has_letters_and_digits(self):
        assert any(c.isalpha() for c in RANDOM_STRING_CHARS)
        assert any(c.isdigit() for c in RANDOM_STRING_CHARS)
        assert any(c.isupper() for c in RANDOM_STRING_CHARS)
        assert any(c.islower() for c in RANDOM_STRING_CHARS)
