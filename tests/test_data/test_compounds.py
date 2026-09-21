"""
Tests for cannlytics.data.compounds
================================
Covers: data integrity of cannabinoids, terpenes, heavy_metals, pesticides.
Validates CAS numbers, required fields, no duplicates.
"""
import re
from collections import Counter

import pytest

from cannlytics.data.compounds import cannabinoids, terpenes, heavy_metals, pesticides


CAS_PATTERN = re.compile(r'^\d{2,7}-\d{2}-\d$')


class TestCannabinoids:

    def test_not_empty(self):
        assert len(cannabinoids) > 10

    def test_all_have_name(self):
        for key, data in cannabinoids.items():
            assert 'name' in data, f'{key} missing name'

    def test_all_have_cas(self):
        for key, data in cannabinoids.items():
            assert 'cas' in data, f'{key} missing CAS number'
            assert CAS_PATTERN.match(data['cas']), f'{key} has invalid CAS: {data["cas"]}'

    def test_no_duplicate_cas(self):
        cas_numbers = [d['cas'] for d in cannabinoids.values()]
        dupes = [c for c, n in Counter(cas_numbers).items() if n > 1]
        assert dupes == [], f'Duplicate CAS numbers: {dupes}'

    def test_common_cannabinoids_present(self):
        expected = ['delta_9_thc', 'cbd', 'cbg', 'cbn', 'thca', 'cbda']
        for key in expected:
            assert key in cannabinoids, f'Missing common cannabinoid: {key}'


class TestTerpenes:

    def test_not_empty(self):
        assert len(terpenes) > 20

    def test_all_have_name(self):
        for key, data in terpenes.items():
            assert 'name' in data, f'{key} missing name'

    def test_all_have_cas(self):
        for key, data in terpenes.items():
            assert 'cas' in data, f'{key} missing CAS number'
            assert CAS_PATTERN.match(data['cas']), f'{key} has invalid CAS: {data["cas"]}'

    def test_all_have_type(self):
        valid_types = {'monoterpenoid', 'sesquiterpenoid', 'diterpenoid'}
        for key, data in terpenes.items():
            assert 'type' in data, f'{key} missing type'
            assert data['type'] in valid_types, f'{key} has invalid type: {data["type"]}'

    def test_no_duplicate_cas(self):
        cas_numbers = [d['cas'] for d in terpenes.values()]
        dupes = [c for c, n in Counter(cas_numbers).items() if n > 1]
        # Cineole and eucalyptol share CAS 470-82-6 (same compound,
        # both listed for mapping flexibility).
        known_synonyms = {'470-82-6'}
        unexpected = [c for c in dupes if c not in known_synonyms]
        assert unexpected == [], f'Unexpected duplicate CAS numbers: {unexpected}'

    def test_common_terpenes_present(self):
        expected = ['beta_myrcene', 'd_limonene', 'alpha_pinene', 'linalool', 'beta_caryophyllene']
        for key in expected:
            assert key in terpenes, f'Missing common terpene: {key}'


class TestHeavyMetals:

    def test_big_four_present(self):
        for metal in ['arsenic', 'cadmium', 'lead', 'mercury']:
            assert metal in heavy_metals

    def test_all_have_cas(self):
        for key, data in heavy_metals.items():
            assert 'cas' in data, f'{key} missing CAS number'


class TestPesticides:

    def test_not_empty(self):
        assert len(pesticides) > 50

    def test_all_have_name(self):
        for key, data in pesticides.items():
            assert 'name' in data, f'{key} missing name'

    def test_all_have_limit(self):
        for key, data in pesticides.items():
            assert 'limit' in data or 'isomers' in data, f'{key} missing limit'

    def test_all_have_cas(self):
        for key, data in pesticides.items():
            assert 'cas' in data, f'{key} missing CAS number'

    def test_isomer_groups_have_subentries(self):
        for key, data in pesticides.items():
            if 'isomers' in data:
                assert len(data['isomers']) >= 2, f'{key} isomer group has < 2 isomers'
                for iso_key, iso_data in data['isomers'].items():
                    assert 'name' in iso_data
                    assert 'cas' in iso_data
