"""
Tests for cannlytics.constants
==============================
The tables every repository used to carry its own copy of. Known
answers come from the probe sets that showed the copies disagreeing
(STR-2026-0925-DATASETS-UPSTREAM-V1, U5).
"""
import ast
import pathlib
import sys

import pytest

from cannlytics import constants
from cannlytics.constants import (
    ALL_ANALYTE_KEYS,
    ANALYTE_ALIASES,
    ANALYTE_KEYS,
    ANALYTE_NAMES,
    ANALYTE_TO_ANALYSIS,
    DECARB,
    JURISDICTIONS,
    LICENSE_CATEGORIES,
    LICENSE_TYPE_KEYWORDS,
    PRODUCT_TYPES,
    STANDARD_ANALYSIS_KEYS,
    TIME_ZONES,
    US_STATES,
    analysis_for_analyte,
    is_canadian_province,
    is_us_state,
    normalize_analysis_name,
    normalize_analyte_key,
    normalize_product_type,
    state_code,
    state_name,
    state_slug,
    state_time_zone,
    to_percent,
)

class TestLeafPackage:

    @pytest.mark.parametrize('path', sorted(pathlib.Path(constants.__file__).parent.glob('*.py')), ids=lambda p: p.name)
    def test_imports_only_the_standard_library(self, path):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                roots.add(node.module.split('.')[0])
        assert roots <= set(sys.stdlib_module_names), roots - set(sys.stdlib_module_names)

    def test_all_names_resolve(self):
        assert [n for n in constants.__all__ if not hasattr(constants, n)] == []

class TestStates:

    def test_fifty_states_and_dc(self):
        assert len(US_STATES) == 51 and 'DC' in US_STATES and US_STATES['WA'] == 'Washington'

    def test_every_jurisdiction_has_a_time_zone(self):
        assert set(TIME_ZONES) == set(JURISDICTIONS)

    def test_time_zones_are_iana(self):
        from zoneinfo import ZoneInfo
        for zone in set(TIME_ZONES.values()):
            ZoneInfo(zone)

    @pytest.mark.parametrize('value, code', [
        ('ca', 'CA'), ('CA', 'CA'), ('California', 'CA'), ('california', 'CA'),
        ('New Jersey', 'NJ'), ('new-jersey', 'NJ'), ('new_jersey', 'NJ'), ('NJ', 'NJ'),
        ('District of Columbia', 'DC'), ('Washington, D.C.', 'DC'), ('washington-dc', 'DC'),
        ('Ontario', 'ON'), ('on', 'ON'), ('Québec', 'QC'), ('Puerto Rico', 'PR'),
        ('Narnia', None), ('', None), (None, None), ('X', None),
    ])
    def test_state_code(self, value, code):
        assert state_code(value) == code

    def test_three_views_of_one_table(self):
        # The conventions the four repositories mixed: code, name, slug.
        assert state_name('nj') == 'New Jersey'
        assert state_slug('New Jersey') == 'new-jersey'
        assert state_slug('dc') == 'district-of-columbia'
        assert state_time_zone('Washington') == 'America/Los_Angeles'

    def test_membership(self):
        assert is_us_state('wa') and not is_us_state('pr') and not is_us_state('on')
        assert is_canadian_province('bc') and not is_canadian_province('wa')

class TestAnalytes:

    def test_keys_are_ascii_snake_case(self):
        for key in ALL_ANALYTE_KEYS:
            assert key.isascii() and key == key.lower() and ' ' not in key and '-' not in key, key

    def test_every_key_belongs_to_exactly_one_analysis(self):
        seen = {}
        for analysis, keys in ANALYTE_KEYS.items():
            for key in keys:
                assert key not in seen, f'{key} in {seen.get(key)} and {analysis}'
                seen[key] = analysis
        assert set(ANALYTE_TO_ANALYSIS) == set(ALL_ANALYTE_KEYS)

    def test_every_alias_targets_a_canonical_key(self):
        assert set(ANALYTE_ALIASES.values()) <= set(ALL_ANALYTE_KEYS)
        assert all(key in ANALYTE_ALIASES for key in ALL_ANALYTE_KEYS)

    def test_every_key_has_a_display_name(self):
        assert set(ANALYTE_NAMES) == set(ALL_ANALYTE_KEYS)

    @pytest.mark.parametrize('label, key', [
        # The probes on which the four copies disagreed (U5).
        ('Δ9-THC', 'delta_9_thc'), ('β-Myrcene', 'beta_myrcene'), ('Δ8-THC', 'delta_8_thc'),
        ('Butane', 'n_butane'), ('Isopropanol', '2_propanol'), ('2-Propanol', '2_propanol'),
        ('Isopropyl Alcohol', '2_propanol'), ('IPA', '2_propanol'),
        # Systematic names, specific over aggregate.
        ('PCNB', 'pentachloronitrobenzene'), ('Aflatoxin B1', 'aflatoxin_b1'),
        ('n-Hexane', 'n_hexane'), ('Hexanes', 'total_hexanes'),
        # The package's own historical aliases.
        ('THC', 'delta_9_thc'), ('d9thc', 'delta_9_thc'), ('delta9thc', 'delta_9_thc'),
        ('THCa', 'thca'), ('THC-A', 'thca'), ('thc_a', 'thca'), ('CBD-A', 'cbda'),
        ('limonene', 'd_limonene'), ('caryophyllene', 'beta_caryophyllene'),
        ('humulene', 'alpha_humulene'), ('a-pinene', 'alpha_pinene'), ('THC-V', 'thcv'),
        ('Total THC', 'total_thc'), ('Total Yeast & Mold', 'total_yeast_and_mold'),
        ('Water Activity', 'water_activity'), ('Moisture', 'moisture_content'),
        ('Escherichia coli', 'e_coli'), ('Total Aerobic Count', 'total_aerobic_bacteria'),
    ])
    def test_normalize_analyte_key(self, label, key):
        assert normalize_analyte_key(label) == key

    def test_unknown_labels_are_snake_cased_not_lost(self):
        assert normalize_analyte_key('Brand New Compound (est.)') == 'brand_new_compound_est'

    def test_blank_is_none(self):
        assert normalize_analyte_key(None) is None and normalize_analyte_key('  ') is None

    def test_analysis_for_analyte(self):
        assert analysis_for_analyte('Δ9-THC') == 'cannabinoids'
        assert analysis_for_analyte('Aflatoxin B1') == 'mycotoxins'
        assert analysis_for_analyte('Isopropanol') == 'residual_solvents'
        assert analysis_for_analyte('nonsense') is None

    def test_mycotoxins_are_not_microbes(self):
        assert 'aflatoxin_b1' in ANALYTE_KEYS['mycotoxins'] and 'aflatoxin_b1' not in ANALYTE_KEYS['microbes']

class TestAnalyses:

    def test_ten_standard_analyses(self):
        assert len(STANDARD_ANALYSIS_KEYS) == 10

    @pytest.mark.parametrize('heading, key', [
        ('Potency Analysis by HPLC', 'cannabinoids'), ('Cannabinoid Profile', 'cannabinoids'),
        ('Terpene Profile', 'terpenes'), ('Microbial Contaminants', 'microbes'), ('Microbials', 'microbes'),
        ('Residual Solvents', 'residual_solvents'), ('Heavy Metals', 'heavy_metals'),
        ('Mycotoxins', 'mycotoxins'), ('Moisture', 'moisture_content'), ('Water Activity', 'water_activity'),
        ('Foreign Material', 'foreign_matter'), ('bogus panel', 'bogus_panel'), (None, None),
    ])
    def test_normalize_analysis_name(self, heading, key):
        assert normalize_analysis_name(heading) == key

class TestProducts:

    @pytest.mark.parametrize('label, key', [
        ('Flower', 'flower'), ('bud', 'flower'), ('Shake/Trim', 'flower'), ('Pre-Roll', 'preroll'),
        ('Infused Pre-Roll', 'infused'), ('Live Resin', 'concentrate'), ('Live Resin Cartridge', 'vape'),
        ('Gummies (10 pack)', 'edible'), ('Cartridges', 'vape'), ('Tincture', 'tincture'), ('Balm', 'topical'),
        ('Suppository', 'Suppository'), (None, None), ('  ', None),
    ])
    def test_normalize_product_type(self, label, key):
        assert normalize_product_type(label) == key

    def test_labels_are_lower_case_and_unique(self):
        seen = set()
        for labels in PRODUCT_TYPES.values():
            for label in labels:
                assert label == label.lower() and label not in seen, label
                seen.add(label)

class TestLicensesAndUnits:

    def test_categories_and_keywords_agree(self):
        assert set(LICENSE_TYPE_KEYWORDS.values()) <= set(LICENSE_CATEGORIES)

    def test_decarb(self):
        assert DECARB == 0.877

    @pytest.mark.parametrize('value, unit, expected', [
        (24.5, '%', 24.5), (24.5, 'percent', 24.5), (245.0, 'mg/g', 24.5), (1000.0, 'ppm', 0.1),
        (5.0, 'CFU/g', None), (0.6, 'aW', None), (1.0, None, None),
    ])
    def test_to_percent(self, value, unit, expected):
        assert to_percent(value, unit) == pytest.approx(expected) if expected is not None else to_percent(value, unit) is None

class TestLegacyPaths:

    def test_data_constants_is_the_same_object(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)   # tested in test_data/test_constants.py
            from cannlytics.data import constants as legacy
        assert legacy.DECARB is DECARB and legacy.states is US_STATES and legacy.state_time_zones is TIME_ZONES

    def test_data_compounds_is_the_same_object(self):
        from cannlytics.data import compounds as legacy
        assert legacy.cannabinoids is constants.cannabinoids

    def test_schema_and_utils_share_the_tables(self):
        from cannlytics.data.coas import schema
        from cannlytics.utils import utils
        assert schema.normalize_analyte_key is normalize_analyte_key
        assert schema.normalize_product_type is normalize_product_type
        assert schema.ANALYTE_KEYS is ANALYTE_ALIASES
        assert utils.state_time_zones is TIME_ZONES

class TestAliasInvariants:
    """The 1.0.4 merge of four alias tables let canonical keys alias away
    from themselves (spinosad <-> spinosad_a was a cycle) and mapped
    p-mentha-1,5-diene to myrcene. These pin the corrections."""

    def test_every_canonical_key_maps_to_itself(self):
        from cannlytics.constants import ANALYTE_ALIASES
        assert [k for k in ALL_ANALYTE_KEYS if ANALYTE_ALIASES[k] != k] == []

    @pytest.mark.parametrize('label, key', [
        ('p-Mentha-1,5-diene', 'alpha_phellandrene'), ('Abamectin', 'abamectin'), ('Abamectin B1a', 'avermectin_b1a'),
        ('Avermectin B1b', 'avermectin_b1b'), ('Spinosad', 'spinosad'), ('Spinosyn A', 'spinosad_a'),
        ('Spinosad D', 'spinosad_d'), ('Fenhexamide', 'fenhexamid'), ('Pyriproxifen', 'pyriproxyfen'),
        ('Permethrins', 'permethrin'), ('cis-Permethrin', 'cis_permethrin'), ('Delta-10-THC', 'delta_10_thc'),
        ('R-Delta-10-THC', '9r_delta_10_thc'), ('Terpineol', 'terpineol'), ('alpha-Ocimene', 'alpha_ocimene'),
        ('BTGN', 'btgn'), ('Aspergillus spp.', 'aspergillus'), ('Total Viable Aerobic Bacteria', 'total_aerobic_bacteria'),
        ('Hair', 'hair'), ('Cannabivarin', 'cbv'), ('Pyrethrin I', 'pyrethrin_i'),
    ])
    def test_components_mixtures_and_isomers_stay_apart(self, label, key):
        assert normalize_analyte_key(label) == key

    def test_a_section_heading_is_not_an_analyte(self):
        assert normalize_analyte_key('Mycotoxin') == 'mycotoxin'
