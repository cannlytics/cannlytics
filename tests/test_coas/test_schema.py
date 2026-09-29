"""
Tests for cannlytics.data.coas.schema
======================================
Covers: analyte key lists, ANALYSIS_CONFIGS, normalization helpers,
LabResult dataclass, ResultDetail, validation rules, and Pydantic
models (when available).
"""
from datetime import datetime

import pytest

from cannlytics.data.coas.schema import (
    # Analyte key lists.
    CANNABINOID_KEYS,
    TERPENE_KEYS,
    PESTICIDE_KEYS,
    HEAVY_METAL_KEYS,
    MICROBIAL_KEYS,
    RESIDUAL_SOLVENT_KEYS,
    MOISTURE_KEYS,
    FOREIGN_MATTER_KEYS,
    ANALYSIS_CONFIGS,
    # Normalization.
    normalize_analyte_key,
    normalize_status,
    normalize_product_type,
    # Dataclasses.
    LabResult,
    ResultDetail,
    # Validation.
    VALIDATION_RULES,
    validate_result,
    # Pydantic models (may be None).
    LabTestMetadata,
    LabTestResult,
    LabAnalysis,
)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Analyte Key Lists                                                ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestAnalyteKeys:
    """Verify analyte key lists are well-formed."""

    def test_cannabinoid_keys_not_empty(self):
        assert len(CANNABINOID_KEYS) >= 10

    def test_terpene_keys_not_empty(self):
        assert len(TERPENE_KEYS) >= 30

    def test_pesticide_keys_not_empty(self):
        assert len(PESTICIDE_KEYS) >= 50

    def test_all_keys_are_snake_case(self):
        """Every key should be lowercase with underscores only."""
        all_keys = (
            CANNABINOID_KEYS + TERPENE_KEYS + PESTICIDE_KEYS
            + HEAVY_METAL_KEYS + MICROBIAL_KEYS + RESIDUAL_SOLVENT_KEYS
            + MOISTURE_KEYS + FOREIGN_MATTER_KEYS
        )
        for key in all_keys:
            assert key == key.lower(), f'Key not lowercase: {key}'
            assert ' ' not in key, f'Key has spaces: {key}'
            assert '-' not in key, f'Key has hyphens: {key}'

    def test_no_duplicate_keys_within_lists(self):
        for name, keys in [
            ('cannabinoids', CANNABINOID_KEYS),
            ('terpenes', TERPENE_KEYS),
            ('pesticides', PESTICIDE_KEYS),
            ('heavy_metals', HEAVY_METAL_KEYS),
        ]:
            assert len(keys) == len(set(keys)), f'Duplicates in {name}'

    def test_analysis_configs_reference_correct_keys(self):
        """Each ANALYSIS_CONFIGS entry should reference the right key list."""
        assert ANALYSIS_CONFIGS['cannabinoids']['keys'] is CANNABINOID_KEYS
        assert ANALYSIS_CONFIGS['terpenes']['keys'] is TERPENE_KEYS
        assert ANALYSIS_CONFIGS['pesticides']['keys'] is PESTICIDE_KEYS

    def test_analysis_configs_have_keywords(self):
        for name, config in ANALYSIS_CONFIGS.items():
            assert 'keywords' in config, f'{name} missing keywords'
            assert len(config['keywords']) > 0, f'{name} has empty keywords'

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Normalization: Analyte Keys                                      ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestNormalizeAnalyteKey:
    """Verify analyte key normalization covers common variants."""

    @pytest.mark.parametrize('input_key,expected', [
        ('THC', 'delta_9_thc'),
        ('thc', 'delta_9_thc'),
        ('d9thc', 'delta_9_thc'),
        ('delta_9_thc', 'delta_9_thc'),
        ('delta9thc', 'delta_9_thc'),
        ('d8thc', 'delta_8_thc'),
        ('thca_a', 'thca'),
        ('thc_a', 'thca'),
        ('cbd_a', 'cbda'),
        ('cannabidiol', 'cbd'),
        ('cannabigerol', 'cbg'),
    ])
    def test_cannabinoid_aliases(self, input_key, expected):
        assert normalize_analyte_key(input_key) == expected

    @pytest.mark.parametrize('input_key,expected', [
        ('myrcene', 'beta_myrcene'),
        ('b_myrcene', 'beta_myrcene'),
        ('limonene', 'd_limonene'),
        ('caryophyllene', 'beta_caryophyllene'),
        ('humulene', 'alpha_humulene'),
        ('a_pinene', 'alpha_pinene'),
        ('a_bisabolol', 'alpha_bisabolol'),
    ])
    def test_terpene_aliases(self, input_key, expected):
        assert normalize_analyte_key(input_key) == expected

    def test_unknown_key_passthrough(self):
        """Unrecognized keys are lowered and returned as-is."""
        assert normalize_analyte_key('SomeNewAnalyte') == 'somenewanalyte'
        assert normalize_analyte_key('my-compound') == 'my_compound'

    def test_whitespace_handling(self):
        assert normalize_analyte_key('  THC  ') == 'delta_9_thc'

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Normalization: Status                                            ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestNormalizeStatus:

    @pytest.mark.parametrize('input_val,expected', [
        ('pass', 'pass'),
        ('Pass', 'pass'),
        ('PASSED', 'pass'),
        ('passing', 'pass'),
        ('p', 'pass'),
        ('compliant', 'pass'),
        ('yes', 'pass'),
        ('true', 'pass'),
        ('1', 'pass'),
    ])
    def test_pass_variants(self, input_val, expected):
        assert normalize_status(input_val) == expected

    @pytest.mark.parametrize('input_val,expected', [
        ('fail', 'fail'),
        ('FAILED', 'fail'),
        ('failing', 'fail'),
        ('f', 'fail'),
        ('non-compliant', 'fail'),
        ('no', 'fail'),
        ('0', 'fail'),
    ])
    def test_fail_variants(self, input_val, expected):
        assert normalize_status(input_val) == expected

    @pytest.mark.parametrize('input_val,expected', [
        ('nt', 'nt'),
        ('not tested', 'nt'),
        ('N/A', 'nt'),
        ('na', 'nt'),
        ('-', 'nt'),
        ('', 'nt'),
    ])
    def test_not_tested_variants(self, input_val, expected):
        assert normalize_status(input_val) == expected

    def test_none_returns_none(self):
        assert normalize_status(None) is None

    def test_unknown_passthrough(self):
        assert normalize_status('pending') == 'pending'

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Normalization: Product Type                                      ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestNormalizeProductType:

    @pytest.mark.parametrize('input_val,expected', [
        ('flower', 'flower'),
        ('Flower', 'flower'),
        ('bud', 'flower'),
        ('Pre-Roll', 'preroll'),
        ('preroll', 'preroll'),
        ('joint', 'preroll'),
        ('Live Resin', 'concentrate'),
        ('shatter', 'concentrate'),
        ('wax', 'concentrate'),
        ('distillate', 'concentrate'),
        ('cartridge', 'vape'),
        ('Vape', 'vape'),
        ('gummy', 'edible'),
        ('chocolate', 'edible'),
        ('tincture', 'tincture'),
        ('oil', 'tincture'),
        ('cream', 'topical'),
        ('balm', 'topical'),
    ])
    def test_known_types(self, input_val, expected):
        assert normalize_product_type(input_val) == expected

    def test_none_returns_none(self):
        assert normalize_product_type(None) is None

    def test_unknown_passthrough(self):
        # Unknown types are returned as-is (not lowered by default).
        result = normalize_product_type('Suppository')
        assert result == 'Suppository'

# ╔══════════════════════════════════════════════════════════════════╗
# ║ LabResult Dataclass                                              ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestLabResult:

    def test_auto_generates_id(self):
        r = LabResult(product_name='Test', state='ca')
        assert r.id is not None
        assert len(r.id) == 16

    def test_auto_generates_hash(self):
        r = LabResult(product_name='Test', state='ca')
        assert r.sample_hash is not None
        assert len(r.sample_hash) == 64  # SHA-256

    def test_deterministic_id(self):
        """Same inputs → same ID."""
        r1 = LabResult(product_name='A', producer='B', batch_number='C', date_tested=datetime(2024, 1, 1))
        r2 = LabResult(product_name='A', producer='B', batch_number='C', date_tested=datetime(2024, 1, 1))
        assert r1.id == r2.id

    def test_unique_ids_for_different_inputs(self):
        """Different inputs must produce different IDs."""
        r1 = LabResult(product_name='Blue Dream', producer='Farm A')
        r2 = LabResult(product_name='OG Kush', producer='Farm A')
        r3 = LabResult(product_name='Blue Dream', producer='Farm B')
        assert r1.id != r2.id
        assert r1.id != r3.id
        assert r2.id != r3.id

    def test_create_full(self):
        """Create a LabResult with comprehensive data."""
        data = {
            'product_name': 'Blue Dream',
            'product_type': 'flower',
            'strain_name': 'Blue Dream',
            'producer': 'Test Farm',
            'producer_license_number': 'CCL20-0000001',
            'lab': 'SC Labs',
            'lab_license_number': 'C8-0000001-LIC',
            'date_tested': datetime(2026, 1, 15),
            'total_thc': 24.5,
            'total_cbd': 0.5,
            'total_terpenes': 2.3,
            'beta_myrcene': 0.8,
            'd_limonene': 0.5,
            'pesticides_status': 'pass',
            'heavy_metals_status': 'pass',
            'microbials_status': 'pass',
            'status': 'pass',
            'state': 'ca',
            'source': 'flower_company',
        }
        r = LabResult(**data)
        assert r.product_name == 'Blue Dream'
        assert r.total_thc == 24.5
        assert r.state == 'ca'
        assert r.lab == 'SC Labs'
        assert r.beta_myrcene == 0.8

    def test_list_fields_default_empty(self):
        """All list fields should default to empty lists."""
        r = LabResult(state='ca')
        assert r.analyses == []
        assert r.metrc_ids == []
        assert r.traceability_ids == []
        assert r.coa_urls == []
        assert r.results == []
        assert r.images == []

    def test_to_dict_serializes_dates(self):
        dt = datetime(2024, 6, 15, 12, 0, 0)
        r = LabResult(date_tested=dt, state='ca')
        d = r.to_dict()
        assert d['date_tested'] == '2024-06-15T12:00:00'

    def test_from_dict_parses_dates(self):
        data = {
            'product_name': 'Blue Dream',
            'state': 'ca',
            'date_tested': '2024-06-15',
            'total_thc': 22.5,
        }
        r = LabResult.from_dict(data)
        assert r.product_name == 'Blue Dream'
        assert r.total_thc == 22.5
        assert isinstance(r.date_tested, datetime)

    def test_from_dict_ignores_unknown_fields(self):
        data = {'product_name': 'Test', 'state': 'ca', 'unknown_field': 'ignored'}
        r = LabResult.from_dict(data)
        assert r.product_name == 'Test'
        assert not hasattr(r, 'unknown_field')

    def test_round_trip(self):
        r = LabResult(
            product_name='Gelato',
            producer='Farm Co',
            total_thc=28.5,
            state='ca',
        )
        d = r.to_dict()
        r2 = LabResult.from_dict(d)
        assert r2.product_name == r.product_name
        assert r2.total_thc == r.total_thc

# ╔══════════════════════════════════════════════════════════════════╗
# ║ ResultDetail Dataclass                                           ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestResultDetail:

    def test_to_dict(self):
        rd = ResultDetail(
            analysis='cannabinoids',
            key='delta_9_thc',
            name='Δ9-THC',
            value=2.10,
            units='percent',
            status='pass',
        )
        d = rd.to_dict()
        assert d['analysis'] == 'cannabinoids'
        assert d['key'] == 'delta_9_thc'
        assert d['value'] == 2.10

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Validation                                                       ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestValidation:

    def test_valid_result_passes(self):
        r = LabResult(state='ca', total_thc=25.0, total_cbd=0.5)
        is_valid, errors = validate_result(r)
        assert is_valid
        assert errors == []

    def test_missing_required_state(self):
        r = LabResult(product_name='Test')
        is_valid, errors = validate_result(r)
        assert not is_valid
        assert any('state' in e for e in errors)

    def test_thc_above_maximum(self):
        r = LabResult(state='ca', total_thc=150.0)
        is_valid, errors = validate_result(r)
        assert not is_valid
        assert any('total_thc' in e and 'above' in e for e in errors)

    def test_water_activity_out_of_range(self):
        r = LabResult(state='ca', water_activity=1.5)
        is_valid, errors = validate_result(r)
        assert not is_valid

    def test_invalid_status_value(self):
        r = LabResult(state='ca', pesticides_status='maybe')
        is_valid, errors = validate_result(r)
        assert not is_valid

    def test_none_values_skip_validation(self):
        """Fields that are None should not trigger min/max errors."""
        r = LabResult(state='ca')
        is_valid, errors = validate_result(r)
        assert is_valid

    def test_negative_thc(self):
        """Negative THC should fail validation."""
        r = LabResult(state='ca', total_thc=-5.0)
        is_valid, errors = validate_result(r)
        assert not is_valid
        assert any('total_thc' in e and 'below' in e for e in errors)

    def test_terpenes_valid_range(self):
        """Valid terpene values should pass."""
        r = LabResult(state='ca', total_terpenes=3.5)
        is_valid, errors = validate_result(r)
        assert is_valid

    def test_terpenes_above_maximum(self):
        """Terpenes above the 20% maximum should fail."""
        r = LabResult(state='ca', total_terpenes=25.0)
        is_valid, errors = validate_result(r)
        assert not is_valid
        assert any('total_terpenes' in e for e in errors)

class TestValidationRules:
    """Verify VALIDATION_RULES structure covers key analyte fields."""

    def test_cannabinoid_rules_exist(self):
        for field in ['delta_9_thc', 'total_thc', 'cbd', 'total_cbd', 'total_cannabinoids']:
            assert field in VALIDATION_RULES, f'Missing rule for {field}'
            assert 'min' in VALIDATION_RULES[field]
            assert 'max' in VALIDATION_RULES[field]

    def test_terpene_rules_exist(self):
        assert 'total_terpenes' in VALIDATION_RULES
        assert VALIDATION_RULES['total_terpenes']['max'] == 20

    def test_status_rules_have_expected_values(self):
        status_fields = ['pesticides_status', 'heavy_metals_status',
                         'microbials_status', 'residual_solvents_status', 'status']
        for field in status_fields:
            assert field in VALIDATION_RULES, f'Missing rule for {field}'
            assert 'values' in VALIDATION_RULES[field]
            assert 'pass' in VALIDATION_RULES[field]['values']
            assert 'fail' in VALIDATION_RULES[field]['values']

    def test_coordinate_rules_exist(self):
        for field in ['producer_latitude', 'producer_longitude', 'lab_latitude', 'lab_longitude']:
            assert field in VALIDATION_RULES
            assert 'min' in VALIDATION_RULES[field]
            assert 'max' in VALIDATION_RULES[field]

    def test_moisture_rules_exist(self):
        assert 'moisture_content' in VALIDATION_RULES
        assert VALIDATION_RULES['moisture_content']['max'] == 20
        assert 'water_activity' in VALIDATION_RULES
        assert VALIDATION_RULES['water_activity']['max'] == 1

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Pydantic Models (conditional)                                    ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestPydanticModels:

    @pytest.mark.skipif(LabTestMetadata is None, reason='Pydantic not installed')
    def test_metadata_defaults(self):
        m = LabTestMetadata()
        assert m.product_name == ''
        assert m.total_thc == 0.0
        assert m.analyses == []

    @pytest.mark.skipif(LabTestMetadata is None, reason='Pydantic not installed')
    def test_metadata_model_dump(self):
        m = LabTestMetadata(product_name='Test', total_thc=25.0)
        d = m.model_dump()
        assert d['product_name'] == 'Test'
        assert d['total_thc'] == 25.0

    @pytest.mark.skipif(LabTestResult is None, reason='Pydantic not installed')
    def test_result_defaults(self):
        r = LabTestResult(key='delta_9_thc', name='THC')
        assert r.value == 0.0
        assert r.units == ''

    @pytest.mark.skipif(LabAnalysis is None, reason='Pydantic not installed')
    def test_analysis_with_results(self):
        a = LabAnalysis(
            analysis='cannabinoids',
            results=[
                LabTestResult(key='delta_9_thc', name='THC', value=2.1, units='percent'),
            ],
        )
        assert len(a.results) == 1
        assert a.results[0].key == 'delta_9_thc'
