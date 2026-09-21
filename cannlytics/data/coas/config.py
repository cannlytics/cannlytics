"""
COA Parsing Configuration — AI Providers & Operational Constants
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/1/2026
Updated: 3/19/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Configuration constants for the COA parsing engine. This module
    contains only the definitions needed by the ``COAdoc`` and
    ``AIClient`` classes — AI provider pricing, model capabilities,
    flex processing settings, and analysis skip rules.

    Pipeline-specific configuration (PathConfig, StateConfig, STATES,
    STATE_NAMES, SOURCE_CONFIG, API_CONFIG, PROCESSING_CONFIG) remains
    in the ``cannabis_results`` repository's ``config/results_config.py``
    and is NOT included here. This module has zero filesystem or
    repository dependencies.

    Configuration Groups:
        - AI_PROVIDERS: Provider definitions with model pricing,
          capabilities, API key environment variable names, and
          priority ordering for the fallback chain.
        - FLEX_COST_MULTIPLIER / FLEX_TIMEOUT: OpenAI Flex processing
          configuration for 50% cost reduction.
        - ANALYSIS_SKIP_RULES: Bayesian product-type-based analysis
          filtering (skip terpenes for edibles, etc.).
        - DATA_QUALITY: Quality thresholds for parsed results.

    Usage::

        from cannlytics.data.coas.config import AI_PROVIDERS

        # Get default model for a provider.
        provider = AI_PROVIDERS['anthropic']
        model = provider['default_model']
        pricing = provider['models'][model]
        cost_per_1m_input = pricing['input']
"""
# Standard imports:
from typing import Any, Dict


# ╔══════════════════════════════════════════════════════════════════╗
# ║ AI Provider Configuration                                        ║
# ╚══════════════════════════════════════════════════════════════════╝

# Provider definitions for the hybrid COA parsing engine.
#
# Each provider specifies:
#   - name:          Human-readable provider name.
#   - models:        Dict of model_id → capabilities and pricing.
#   - default_model: Model ID used when none is specified.
#   - env_key:       Environment variable name for the API key.
#   - priority:      Fallback order (1 = first choice).
#   - free_tier:     Whether a free usage tier is available.
#
# Model capabilities:
#   - input / output:               Cost per 1M tokens (USD).
#   - supports_pdf:                 Can accept PDF files directly.
#   - supports_images:              Can accept base64-encoded images.
#   - supports_structured_output:   Can use Pydantic response schemas.
#   - max_output_tokens:            Maximum completion length.
#   - image_cost:                   Per-image cost (OpenAI only).
#   - free_tier_input/output:       Free-tier pricing (Gemini only).
#
# Pricing is per 1,000,000 tokens. To calculate cost for a single
# API call:
#   cost = (input_tokens * model['input'] / 1_000_000)
#        + (output_tokens * model['output'] / 1_000_000)
#        + (num_images * model.get('image_cost', 0))

AI_PROVIDERS: Dict[str, Dict[str, Any]] = {
    'anthropic': {
        'name': 'Anthropic Claude',
        'models': {
            'claude-sonnet-4-5-20250929': {
                'input': 3.00, 'output': 15.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': False,
                'max_output_tokens': 64_000,
            },
            'claude-haiku-4-5-20251001': {
                'input': 1.00, 'output': 5.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': False,
                'max_output_tokens': 64_000,
            },
        },
        'default_model': 'claude-haiku-4-5-20251001',
        'env_key': 'ANTHROPIC_API_KEY',
        'priority': 1,
        'free_tier': False,
    },
    'openai': {
        'name': 'OpenAI',
        'models': {
            'gpt-5-mini': {
                'input': 0.25, 'output': 2.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 16_384,
                'image_cost': 0.003825,
            },
            'gpt-5-nano': {
                'input': 0.05, 'output': 0.40,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 16_384,
                'image_cost': 0.001275,
            },
            'gpt-5': {
                'input': 1.25, 'output': 10.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 32_768,
                'image_cost': 0.003825,
            },
        },
        'default_model': 'gpt-5-nano',
        'env_key': 'OPENAI_API_KEY',
        'priority': 2,
        'free_tier': False,
    },
    'gemini': {
        'name': 'Google Gemini',
        'models': {
            'gemini-2.5-flash': {
                'input': 0.30, 'output': 2.50,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 65_536,
                'free_tier_input': 0.0, 'free_tier_output': 0.0,
            },
            'gemini-2.5-pro': {
                'input': 1.25, 'output': 10.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 65_536,
                'free_tier_input': 0.0, 'free_tier_output': 0.0,
            },
        },
        'default_model': 'gemini-2.5-flash',
        'env_key': 'GOOGLE_API_KEY',
        'priority': 3,
        'free_tier': True,
    },
    'xai': {
        'name': 'xAI Grok',
        'models': {
            'grok-4-1-fast-non-reasoning': {
                'input': 0.20, 'output': 0.50,
                'supports_pdf': False, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 16_384,
            },
            'grok-3-mini': {
                'input': 0.30, 'output': 0.50,
                'supports_pdf': False, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 16_384,
            },
        },
        'default_model': 'grok-4-1-fast-non-reasoning',
        'env_key': 'XAI_API_KEY',
        'priority': 4,
        'free_tier': False,
    },
}


# ╔══════════════════════════════════════════════════════════════════╗
# ║ OpenAI Flex Processing Configuration                             ║
# ╚══════════════════════════════════════════════════════════════════╝

# OpenAI Flex processing provides 50% cost reduction (Batch API
# rates) for synchronous requests with higher latency tolerance.
# Supported for GPT-5 family models. When flex capacity is
# unavailable, the AIClient retries with standard processing.

FLEX_COST_MULTIPLIER: float = 0.5
"""Discount multiplier applied when flex processing is used."""

FLEX_TIMEOUT: float = 900.0
"""Timeout in seconds for flex requests (15 minutes, per OpenAI docs)."""


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Analysis Skip Rules                                              ║
# ╚══════════════════════════════════════════════════════════════════╝

# Product-type-specific priors for analyses that are known to be
# unnecessary based on domain knowledge and observed zero-result
# patterns. When metadata reveals the product type, we update our
# beliefs about which analyses to parse — skipping those with a
# near-zero prior probability of yielding results.
#
# Structure: {analysis_name: [product_types_to_skip]}
# Rationale is documented per rule so future additions are traceable.

ANALYSIS_SKIP_RULES: Dict[str, list] = {
    # Edibles are almost never tested for terpenes. Terpene
    # profiles are irrelevant after decarboxylation / infusion.
    # Observed: 100% zero-result rate for edibles (11/11 in CA).
    'terpenes': ['edible'],
}


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Data Quality Thresholds                                          ║
# ╚══════════════════════════════════════════════════════════════════╝

DATA_QUALITY: Dict[str, float] = {
    'min_completeness': 0.90,        # 90% field population target
    'min_accuracy': 0.99,            # 99% accuracy target
    'max_duplicate_rate': 0.001,     # 0.1% max duplicate rate
    'max_data_age_days': 30,         # Maximum 30 days since last update
}


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Helper Functions                                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

def get_provider_priority() -> list:
    """Return provider keys sorted by priority (lowest = first).

    Returns:
        List of provider key strings in priority order.

    Example::

        >>> get_provider_priority()
        ['anthropic', 'openai', 'gemini', 'xai']
    """
    return sorted(
        AI_PROVIDERS.keys(),
        key=lambda k: AI_PROVIDERS[k]['priority'],
    )


def get_model_cost(
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        num_images: int = 0,
        flex: bool = False,
    ) -> float:
    """Calculate the cost of a single API call.

    Args:
        provider: Provider key (e.g., 'anthropic', 'openai').
        model: Model identifier (e.g., 'claude-haiku-4-5-20251001').
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.
        num_images: Number of images sent (OpenAI image pricing).
        flex: Whether OpenAI flex processing was used.

    Returns:
        Cost in USD.

    Raises:
        KeyError: If provider or model is not found in AI_PROVIDERS.
    """
    model_config = AI_PROVIDERS[provider]['models'][model]
    in_rate = model_config['input'] / 1_000_000
    out_rate = model_config['output'] / 1_000_000
    token_cost = input_tokens * in_rate + output_tokens * out_rate
    image_cost = num_images * model_config.get('image_cost', 0.0)
    cost = token_cost + image_cost
    if flex:
        cost *= FLEX_COST_MULTIPLIER
    return cost


def get_env_key(provider: str) -> str:
    """Get the environment variable name for a provider's API key.

    Args:
        provider: Provider key (e.g., 'anthropic').

    Returns:
        Environment variable name (e.g., 'ANTHROPIC_API_KEY').

    Raises:
        KeyError: If provider is not found in AI_PROVIDERS.
    """
    return AI_PROVIDERS[provider]['env_key']


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Module Self-Test                                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

if __name__ == '__main__':
    print('=== Cannlytics COA Config ===\n')
    print(f'AI Providers:           {len(AI_PROVIDERS)}')
    print(f'Provider priority:      {get_provider_priority()}')
    for key, prov in AI_PROVIDERS.items():
        print(f'  {key}: {prov["name"]}')
        print(f'    Default model:      {prov["default_model"]}')
        print(f'    Models available:   {len(prov["models"])}')
        print(f'    Env key:            {prov["env_key"]}')
        print(f'    Free tier:          {prov["free_tier"]}')
    print(f'\nFlex multiplier:        {FLEX_COST_MULTIPLIER}')
    print(f'Flex timeout:           {FLEX_TIMEOUT}s')
    print(f'Analysis skip rules:    {len(ANALYSIS_SKIP_RULES)}')
    print(f'Data quality rules:     {len(DATA_QUALITY)}')

    # Test cost calculation.
    cost = get_model_cost('openai', 'gpt-5-nano', 5000, 2000, num_images=3)
    print(f'\nCost test (gpt-5-nano, 5K in / 2K out / 3 images):')
    print(f'  ${cost:.6f}')

    cost_flex = get_model_cost('openai', 'gpt-5-nano', 5000, 2000, num_images=3, flex=True)
    print(f'  ${cost_flex:.6f} (with flex)')

    print('\n✓ Config loaded successfully.')
