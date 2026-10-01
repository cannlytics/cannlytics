"""
COA Parsing Configuration — AI Providers & Operational Constants
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/1/2026
Updated: 9/29/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Configuration constants for the COA parsing engine: the AI providers
    and models ``COAdoc`` and ``AIClient`` can use, their prices and
    capabilities, flex processing, and analysis skip rules. No
    filesystem or repository dependencies; pipeline configuration lives
    in each dataset repository.

    Keeping this current is a release task. Model registries go stale
    within months: on 2026-09-28 the xAI default had been retired (May
    2026) and every OpenAI, Gemini, and xAI default had a successor. To
    update, check each provider's ``pricing_url``, edit ``models``, set
    ``PRICES_VERIFIED``, run ``tools/check_ai_providers.py`` with your
    API keys, and release.

    Conventions:
        - Prices are USD per 1,000,000 tokens at the provider's standard,
          paid tier, for prompts under any long-context threshold (COA
          requests are far below them).
        - ``price_schedule`` lists announced future prices, applied from
          their ``from`` date (Gemini's introductory Flash pricing ends
          on 2026-12-31).
        - Image and PDF input is billed by every provider here as input
          tokens, which the API reports in its usage. There is therefore
          no per-image surcharge: the former ``image_cost`` (765 tokens
          at GPT-4o's price) counted each image twice.
        - ``max_output_tokens`` is the output cap sent with a request.
          Where a provider publishes the model's limit, it is that limit.
        - ``legacy`` models are superseded but still served: selectable
          by name, never a default. ``quarantined`` models failed a
          fidelity check (see the model's note) and are never a default.
        - Retired models are removed: naming one fails at construction
          rather than at the first request.

    Usage::

        from cannlytics.data.coas.config import AI_PROVIDERS, get_model_cost

        model = AI_PROVIDERS['anthropic']['default_model']
        cost = get_model_cost('anthropic', model, input_tokens=20_000, output_tokens=3_000)
"""
# Standard imports:
from datetime import date
from typing import Any, Dict, Optional, Tuple, Union

# ╔══════════════════════════════════════════════════════════════════╗
# ║ AI Provider Configuration                                        ║
# ╚══════════════════════════════════════════════════════════════════╝

# The date every price below was checked against the provider's page.
PRICES_VERIFIED: str = '2026-09-29'

AI_PROVIDERS: Dict[str, Dict[str, Any]] = {
    'anthropic': {
        'name': 'Anthropic Claude',
        'pricing_url': 'https://platform.claude.com/docs/en/about-claude/pricing',
        'models': {
            # The fastest current Claude, and the least expensive.
            'claude-haiku-4-5-20251001': {
                'input': 1.00, 'output': 5.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': False,
                'max_output_tokens': 64_000,
            },
            # Latest Sonnet; same price as Sonnet 5.
            'claude-sonnet-5-5': {
                'input': 2.00, 'output': 10.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': False,
                'max_output_tokens': 128_000,
            },
            # Opus 5.5 and Fable 5.1 always think before answering; the
            # client keeps only the text blocks of a response.
            'claude-opus-5-5': {
                'input': 4.00, 'output': 20.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': False,
                'max_output_tokens': 128_000,
            },
            'claude-fable-5-1': {
                'input': 10.00, 'output': 50.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': False,
                'max_output_tokens': 128_000,
            },
        },
        'default_model': 'claude-sonnet-5-5',
        'env_key': 'ANTHROPIC_API_KEY',
        'priority': 1,
        'free_tier': False,
    },
    'openai': {
        'name': 'OpenAI',
        'pricing_url': 'https://developers.openai.com/api/docs/pricing',
        'models': {
            'gpt-6-sol': {
                'input': 2.00, 'output': 10.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 128_000,
            },
            # The cost tier. Not a default: the last model of this class
            # (gpt-5-nano) failed the non-detect fidelity check, and this
            # one has not been checked yet.
            'gpt-6-luna': {
                'input': 0.10, 'output': 0.50,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 128_000,
            },
            'gpt-6-astra': {
                'input': 10.00, 'output': 50.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 128_000,
            },
            # Superseded by GPT-6; prices as recorded when they were current.
            'gpt-5-mini': {
                'input': 0.25, 'output': 2.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 16_384,
                'legacy': True,
            },
            'gpt-5': {
                'input': 1.25, 'output': 10.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 32_768,
                'legacy': True,
            },
            'gpt-5-nano': {
                'input': 0.05, 'output': 0.40,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 16_384,
                'legacy': True,
                # Quarantined: 0% non-detect fidelity on every panel tested
                # (it returns 0.0 where the COA says ND). Selectable by name
                # for experiments; never a default.
                'quarantined': True,
            },
        },
        'default_model': 'gpt-6-sol',
        'env_key': 'OPENAI_API_KEY',
        'priority': 2,
        'free_tier': False,
    },
    'gemini': {
        'name': 'Google Gemini',
        'pricing_url': 'https://ai.google.dev/gemini-api/docs/pricing',
        'models': {
            # Introductory pricing through 2026-12-31, doubling on 2027-01-01.
            'gemini-3.8-flash': {
                'input': 0.75, 'output': 3.75,
                'price_schedule': [{'from': '2027-01-01', 'input': 1.50, 'output': 7.50}],
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 65_536,
                'free_tier_input': 0.0, 'free_tier_output': 0.0,
            },
            'gemini-3.5-flash-lite': {
                'input': 0.30, 'output': 2.50,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 65_536,
                'free_tier_input': 0.0, 'free_tier_output': 0.0,
            },
            # Not on the free tier.
            'gemini-3.1-pro-preview': {
                'input': 2.00, 'output': 12.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 65_536,
            },
            'gemini-2.5-flash': {
                'input': 0.30, 'output': 2.50,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 65_536,
                'free_tier_input': 0.0, 'free_tier_output': 0.0,
                'legacy': True,
            },
            'gemini-2.5-pro': {
                'input': 1.25, 'output': 10.00,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 65_536,
                'free_tier_input': 0.0, 'free_tier_output': 0.0,
                'legacy': True,
            },
        },
        'default_model': 'gemini-3.8-flash',
        'env_key': 'GOOGLE_API_KEY',
        'priority': 3,
        'free_tier': True,
    },
    'xai': {
        'name': 'xAI Grok',
        'pricing_url': 'https://docs.x.ai/developers/pricing',
        # grok-4-1-fast-non-reasoning and grok-3-mini, the previous entries,
        # were retired by xAI in May 2026. The client sends a reasoning
        # effort with structured requests, so only reasoning models belong
        # here. PDFs are sent as page images.
        'models': {
            'grok-4.7': {
                'input': 2.00, 'output': 6.00,
                'supports_pdf': False, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 16_384,
            },
            'grok-4.3': {
                'input': 1.25, 'output': 2.50,
                'supports_pdf': False, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 16_384,
            },
        },
        'default_model': 'grok-4.7',
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

# Other names people use for the providers above.
PROVIDER_ALIASES: Dict[str, str] = {'claude': 'anthropic', 'google': 'gemini', 'grok': 'xai'}

def resolve_provider(name: str) -> str:
    """The provider key for a name or alias: ``'google'`` is ``'gemini'``.

    Raises:
        ValueError: For a name that is neither a provider nor an alias.
    """
    key = str(name).strip().lower()
    key = PROVIDER_ALIASES.get(key, key)
    if key not in AI_PROVIDERS:
        raise ValueError(f'Unknown AI provider {name!r}: use one of {", ".join(get_provider_priority())}.')
    return key

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

def effective_prices(
        model_config: Dict[str, Any],
        on: Optional[Union[date, str]] = None,
    ) -> Tuple[float, float]:
    """The input and output price of a model on a date.

    Args:
        model_config: A model's entry in ``AI_PROVIDERS``.
        on: The date (default: today). Entries of ``price_schedule``
            whose ``from`` date has arrived replace the base price, the
            latest winning.

    Returns:
        ``(input, output)`` in USD per 1,000,000 tokens.
    """
    when = (on if isinstance(on, str) else (on or date.today()).isoformat())[:10]
    prices = (model_config['input'], model_config['output'])
    for change in sorted(model_config.get('price_schedule', []), key=lambda c: c['from']):
        if change['from'] <= when:
            prices = (change['input'], change['output'])
    return prices

def get_model_cost(
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        num_images: int = 0,
        flex: bool = False,
        on: Optional[Union[date, str]] = None,
    ) -> float:
    """Calculate the cost of a single API call.

    Args:
        provider: Provider key (e.g., 'anthropic', 'openai').
        model: Model identifier (e.g., 'claude-haiku-4-5-20251001').
        input_tokens: Input tokens, as the API reports them (images and
            PDF pages included).
        output_tokens: Output tokens, thinking included.
        num_images: Images sent. Adds a surcharge only for a model that
            declares ``image_cost``; none of the registered models do,
            since their images are already input tokens.
        flex: Whether OpenAI flex processing was used.
        on: Price date (default: today); see ``effective_prices``.

    Returns:
        Cost in USD.

    Raises:
        KeyError: If provider or model is not found in AI_PROVIDERS.
    """
    model_config = AI_PROVIDERS[provider]['models'][model]
    input_price, output_price = effective_prices(model_config, on)
    cost = (input_tokens * input_price + output_tokens * output_price) / 1_000_000
    cost += num_images * model_config.get('image_cost', 0.0)
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
