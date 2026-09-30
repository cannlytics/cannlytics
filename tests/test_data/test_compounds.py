"""
Tests for the compound reference
================================
`cannlytics.constants.compounds` (also importable as
`cannlytics.data.compounds`). The invariants hold however the data
grows; the known answers pin the corrections of 1.0.5.
"""
import pytest

from cannlytics.constants import ALL_ANALYTE_KEYS, ANALYTE_TO_ANALYSIS
from cannlytics.constants.compounds import (
    CAS_SOURCES,
    COMPOUNDS,
    cannabinoids,
    foreign_matter,
    get_compound,
    heavy_metals,
    is_valid_cas,
    microbes,
    mycotoxins,
    pesticides,
    residual_solvents,
    terpenes,
)

TABLES = {
    'cannabinoids': cannabinoids, 'terpenes': terpenes, 'heavy_metals': heavy_metals,
    'pesticides': pesticides, 'residual_solvents': residual_solvents, 'microbes': microbes,
    'mycotoxins': mycotoxins, 'foreign_matter': foreign_matter,
}

class TestKeys:

    @pytest.mark.parametrize('analysis', list(TABLES))
    def test_keys_are_canonical_and_in_their_own_analysis(self, analysis):
        for key in TABLES[analysis]:
            assert key in ALL_ANALYTE_KEYS and ANALYTE_TO_ANALYSIS[key] == analysis, key

    def test_every_entry_has_a_name(self):
        assert all(entry.get('name') for entry in COMPOUNDS.values())

    def test_combined_view_is_the_tables(self):
        assert len(COMPOUNDS) == sum(len(t) for t in TABLES.values())

class TestCasNumbers:

    def test_every_cas_passes_its_check_digit(self):
        assert [k for k, e in COMPOUNDS.items() if 'cas' in e and not is_valid_cas(e['cas'])] == []

    def test_no_cas_number_appears_twice(self):
        seen = {}
        for key, entry in COMPOUNDS.items():
            if 'cas' in entry:
                assert entry['cas'] not in seen, f"{key} and {seen.get(entry['cas'])}"
                seen[entry['cas']] = key

    @pytest.mark.parametrize('cas', ['5207-84-8', '18020-13-7', '41372-09-4', '602-18-4', '1235-54-1', '6241-43-4', '5691-30-7'])
    def test_the_check_digit_rejects_the_numbers_earlier_releases_shipped(self, cas):
        assert not is_valid_cas(cas)

    @pytest.mark.parametrize('cas, valid', [
        ('1972-08-3', True), ('7732-18-5', True), ('1330-20-7', True), ('1972-08-4', False),
        ('1972083', False), ('', False), (None, False), ('abc', False),
    ])
    def test_is_valid_cas(self, cas, valid):
        assert is_valid_cas(cas) is valid

    @pytest.mark.parametrize('key, cas', [
        # Corrected in 1.0.5 (the PubChem-enriched analytes dataset).
        ('cbca', '185505-15-1'), ('cbcv', '57130-04-8'), ('cbdva', '31932-13-5'), ('cbl', '21366-63-2'),
        ('cbla', '40524-99-0'), ('cbna', '2808-39-1'), ('cbt', '31508-71-1'), ('thcva', '39986-26-0'),
        # Unchanged anchors.
        ('delta_9_thc', '1972-08-3'), ('cbd', '13956-29-1'), ('beta_myrcene', '123-35-3'),
        # Added, with primary sources.
        ('aflatoxin_b1', '1162-65-8'), ('aflatoxin_b2', '7220-81-7'), ('aflatoxin_g1', '1165-39-5'),
        ('aflatoxin_g2', '7241-98-7'), ('ochratoxin_a', '303-47-9'),
        ('cis_permethrin', '61949-76-6'), ('trans_permethrin', '61949-77-7'), ('permethrin', '52645-53-1'),
        ('2_propanol', '67-63-0'), ('n_hexane', '110-54-3'), ('n_butane', '106-97-8'), ('total_xylenes', '1330-20-7'),
        ('pyrethrin_i', '121-21-1'), ('terpineol', '8000-41-7'), ('alpha_terpineol', '98-55-5'),
    ])
    def test_known_answers(self, key, cas):
        assert COMPOUNDS[key]['cas'] == cas

    @pytest.mark.parametrize('key', ['total_butanes', 'total_hexanes', 'total_pentanes', 'total_aflatoxins',
                                     'ocimene', 'e_coli', 'total_yeast_and_mold', 'soil', 'hair'])
    def test_sums_unspecified_isomers_organisms_and_matter_have_none(self, key):
        assert 'cas' not in COMPOUNDS[key]

    def test_additions_cite_a_primary_source(self):
        assert all(key in COMPOUNDS and 'cas' in COMPOUNDS[key] for key in CAS_SOURCES)

class TestMixtures:

    def test_isomers_are_canonical_pesticides_with_their_own_numbers(self):
        for key, entry in pesticides.items():
            for part in entry.get('isomers', []):
                assert part in pesticides and pesticides[part]['cas'] != entry.get('cas'), (key, part)

    def test_the_mixtures(self):
        assert pesticides['abamectin']['isomers'] == ['avermectin_b1a', 'avermectin_b1b']
        assert pesticides['spinosad']['isomers'] == ['spinosad_a', 'spinosad_d']

class TestCoverage:

    def test_the_formerly_empty_categories(self):
        assert len(residual_solvents) >= 30 and len(microbes) >= 15 and len(mycotoxins) == 6 and len(foreign_matter) >= 7

    def test_common_analytes_present(self):
        for key in ('delta_9_thc', 'thca', 'cbd', 'cbda', 'cbg', 'cbn'):
            assert key in cannabinoids
        for key in ('beta_myrcene', 'd_limonene', 'beta_caryophyllene', 'alpha_pinene', 'linalool'):
            assert key in terpenes
        for key in ('arsenic', 'cadmium', 'lead', 'mercury'):
            assert key in heavy_metals
        for key in ('e_coli', 'salmonella', 'aspergillus', 'total_yeast_and_mold'):
            assert key in microbes

    def test_types_are_known(self):
        known = {'monoterpenoid', 'sesquiterpenoid', 'diterpenoid', 'triterpenoid', 'aromatic', 'ester'}
        assert {e['type'] for e in terpenes.values() if 'type' in e} <= known
        assert {e['type'] for e in microbes.values()} <= {'bacterial', 'fungal', 'aggregate'}

class TestLookup:

    @pytest.mark.parametrize('label, key', [('Δ9-THC', 'delta_9_thc'), ('Isopropanol', '2_propanol'),
                                            ('Spinosyn A', 'spinosad_a'), ('p-Mentha-1,5-diene', 'alpha_phellandrene')])
    def test_any_label(self, label, key):
        assert get_compound(label) is COMPOUNDS[key]

    def test_unknown(self):
        assert get_compound('nonsense') is None and get_compound(None) is None and get_compound('') is None

    def test_legacy_path_is_the_same_objects(self):
        from cannlytics.data import compounds as legacy
        assert legacy.microbes is microbes and legacy.COMPOUNDS is COMPOUNDS
