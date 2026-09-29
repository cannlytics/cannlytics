"""
Tests for cannlytics.data.coas.config
======================================
Covers: AI_PROVIDERS structure, provider priority, cost calculations,
flex configuration, analysis skip rules.
"""
import pytest

from cannlytics.data.coas.config import (
    AI_PROVIDERS,
    FLEX_COST_MULTIPLIER,
    FLEX_TIMEOUT,
    ANALYSIS_SKIP_RULES,
    DATA_QUALITY,
    get_provider_priority,
    get_model_cost,
    get_env_key,
)

class TestAIProviders:
    """Verify AI_PROVIDERS structure is well-formed."""

    def test_has_all_four_providers(self):
        assert set(AI_PROVIDERS.keys()) == {'anthropic', 'openai', 'gemini', 'xai'}

    @pytest.mark.parametrize('provider', ['anthropic', 'openai', 'gemini', 'xai'])
    def test_provider_has_required_fields(self, provider):
        config = AI_PROVIDERS[provider]
        assert 'name' in config
        assert 'models' in config
        assert 'default_model' in config
        assert 'env_key' in config
        assert 'priority' in config
        assert isinstance(config['priority'], int)

    @pytest.mark.parametrize('provider', ['anthropic', 'openai', 'gemini', 'xai'])
    def test_default_model_exists_in_models(self, provider):
        config = AI_PROVIDERS[provider]
        assert config['default_model'] in config['models']

    @pytest.mark.parametrize('provider', ['anthropic', 'openai', 'gemini', 'xai'])
    def test_models_have_pricing(self, provider):
        for model_name, model_config in AI_PROVIDERS[provider]['models'].items():
            assert 'input' in model_config, f'{provider}/{model_name} missing input price'
            assert 'output' in model_config, f'{provider}/{model_name} missing output price'
            assert model_config['input'] >= 0
            assert model_config['output'] >= 0

    @pytest.mark.parametrize('provider', ['anthropic', 'openai', 'gemini', 'xai'])
    def test_models_have_capabilities(self, provider):
        for model_config in AI_PROVIDERS[provider]['models'].values():
            assert 'supports_pdf' in model_config
            assert 'supports_images' in model_config
            assert 'supports_structured_output' in model_config
            assert 'max_output_tokens' in model_config
            assert isinstance(model_config['supports_pdf'], bool)

class TestProviderPriority:

    def test_priority_order(self):
        order = get_provider_priority()
        assert order[0] == 'anthropic'  # Priority 1
        assert order[-1] == 'xai'       # Priority 4

    def test_all_providers_in_priority(self):
        order = get_provider_priority()
        assert set(order) == set(AI_PROVIDERS.keys())

class TestCostCalculation:

    def test_basic_cost(self):
        cost = get_model_cost('openai', 'gpt-5-nano', 10_000, 5_000)
        # 10K * 0.05/1M + 5K * 0.40/1M = 0.0005 + 0.002 = 0.0025
        assert abs(cost - 0.0025) < 1e-10

    def test_flex_halves_cost(self):
        standard = get_model_cost('openai', 'gpt-5-nano', 10_000, 5_000)
        flex = get_model_cost('openai', 'gpt-5-nano', 10_000, 5_000, flex=True)
        assert abs(flex - standard * 0.5) < 1e-10

    def test_images_carry_no_surcharge(self):
        # Images are input tokens in the reported usage; the former
        # per-image surcharge counted each one twice.
        no_images = get_model_cost('openai', 'gpt-5-nano', 1_000, 1_000, num_images=0)
        with_images = get_model_cost('openai', 'gpt-5-nano', 1_000, 1_000, num_images=5)
        assert with_images == no_images

    def test_zero_tokens_zero_cost(self):
        cost = get_model_cost('anthropic', 'claude-haiku-4-5-20251001', 0, 0)
        assert cost == 0.0

    def test_unknown_provider_raises(self):
        with pytest.raises(KeyError):
            get_model_cost('nonexistent', 'model', 100, 100)

class TestEnvKey:

    def test_anthropic_key(self):
        assert get_env_key('anthropic') == 'ANTHROPIC_API_KEY'

    def test_openai_key(self):
        assert get_env_key('openai') == 'OPENAI_API_KEY'

    def test_unknown_raises(self):
        with pytest.raises(KeyError):
            get_env_key('nonexistent')

class TestFlexConfig:

    def test_flex_multiplier(self):
        assert FLEX_COST_MULTIPLIER == 0.5

    def test_flex_timeout(self):
        assert FLEX_TIMEOUT == 900.0  # 15 minutes

class TestAnalysisSkipRules:

    def test_terpenes_skipped_for_edibles(self):
        assert 'edible' in ANALYSIS_SKIP_RULES.get('terpenes', [])

    def test_cannabinoids_not_skipped(self):
        assert 'cannabinoids' not in ANALYSIS_SKIP_RULES

class TestDataQuality:

    def test_thresholds_exist(self):
        assert 'min_completeness' in DATA_QUALITY
        assert 'min_accuracy' in DATA_QUALITY
        assert DATA_QUALITY['min_accuracy'] >= 0.99

class TestRegistryHygiene:
    """The registry is edited every release; these keep it honest."""

    def test_prices_were_verified_on_a_date(self):
        from datetime import date
        from cannlytics.data.coas.config import PRICES_VERIFIED
        assert date.fromisoformat(PRICES_VERIFIED) <= date.today()

    @pytest.mark.parametrize('provider', list(AI_PROVIDERS))
    def test_defaults_are_neither_legacy_nor_quarantined(self, provider):
        default = AI_PROVIDERS[provider]['models'][AI_PROVIDERS[provider]['default_model']]
        assert not default.get('legacy') and not default.get('quarantined')

    @pytest.mark.parametrize('provider', list(AI_PROVIDERS))
    def test_every_provider_names_its_price_page(self, provider):
        assert AI_PROVIDERS[provider]['pricing_url'].startswith('https://')

    def test_no_model_declares_a_per_image_surcharge(self):
        assert not any('image_cost' in m for p in AI_PROVIDERS.values() for m in p['models'].values())

    def test_retired_xai_models_are_gone(self):
        assert not {'grok-4-1-fast-non-reasoning', 'grok-3-mini'} & set(AI_PROVIDERS['xai']['models'])

    def test_schedules_are_ordered_iso_dates(self):
        from datetime import date
        for provider in AI_PROVIDERS.values():
            for model in provider['models'].values():
                dates = [change['from'] for change in model.get('price_schedule', [])]
                assert dates == sorted(dates) and all(date.fromisoformat(d) for d in dates)

class TestPriceSchedule:

    def test_gemini_flash_doubles_on_new_year(self):
        from cannlytics.data.coas.config import effective_prices
        model = AI_PROVIDERS['gemini']['models']['gemini-3.8-flash']
        assert effective_prices(model, '2026-12-31') == (0.75, 3.75)
        assert effective_prices(model, '2027-01-01') == (1.50, 7.50)

    def test_cost_on_a_date(self):
        before = get_model_cost('gemini', 'gemini-3.8-flash', 1_000_000, 1_000_000, on='2026-12-31')
        after = get_model_cost('gemini', 'gemini-3.8-flash', 1_000_000, 1_000_000, on='2027-01-01')
        assert before == pytest.approx(4.50) and after == pytest.approx(9.00)

    def test_flex_still_halves(self):
        assert get_model_cost('openai', 'gpt-6-sol', 1_000_000, 0, flex=True) == pytest.approx(1.00)
