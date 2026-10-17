"""
COA Parsing Configuration — AI Providers & Operational Constants
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/1/2026
Updated: 10/13/2026
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
        - ``long_context`` prices replace the base prices for a request
          whose prompt (input plus cached tokens) is longer than ``above``
          tokens (Claude Haiku 5.5, above 100,000).
        - Prompt caching: a cache read costs ``cache_read`` times the input
          price; a write costs ``CACHE_WRITE_MULTIPLIERS`` times it (1.25
          for five minutes, 2 for an hour).
        - ``batch_discount`` is the provider's batch price as a share of the
          standard price (Anthropic's Message Batches: 0.5, on every token).
          Only providers whose batches cannlytics submits declare it.
        - ``efforts`` are the effort levels a model accepts, and
          ``default_effort`` the one the client sends when none is given.
          It is sent explicitly because the API default differs by model
          (``medium`` on Claude Opus 5.5 and Haiku 5.5, ``high`` on others).

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

# The date every price below was checked against the provider's page. A
# provider's own ``prices_verified`` is later when only its prices were
# checked since (Anthropic: 2026-10-09, with Claude Haiku 5.5 added).
PRICES_VERIFIED: str = '2026-09-29'

# Effort levels, lowest first (``output_config.effort`` on Claude).
EFFORT_LEVELS = ('low', 'medium', 'high', 'xhigh', 'max')

# Output cap sent by default for each effort: thinking counts toward
# ``max_tokens``, so higher effort needs more room. Capped by the model's
# ``max_output_tokens``.
EFFORT_MAX_TOKENS = {'low': 16_000, 'medium': 32_000, 'high': 64_000, 'xhigh': 96_000, 'max': 128_000}

# Prompt-cache write prices, as multiples of the input price.
CACHE_WRITE_MULTIPLIERS = {'5m': 1.25, '1h': 2.0}

AI_PROVIDERS: Dict[str, Dict[str, Any]] = {
    'anthropic': {
        'name': 'Anthropic Claude',
        'pricing_url': 'https://platform.claude.com/docs/en/about-claude/pricing',
        'prices_verified': '2026-10-09',
        # Message Batches: half price on every token, results within 24 hours.
        'batch_discount': 0.5,
        'models': {
            # The least expensive Claude: a tenth of Haiku 4.5's price for
            # prompts up to 100,000 tokens, five times that above them.
            'claude-haiku-5-5': {
                'input': 0.10, 'output': 0.50,
                'long_context': {'above': 100_000, 'input': 0.50, 'output': 2.50},
                'cache_read': 0.10,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'efforts': EFFORT_LEVELS, 'default_effort': 'high',
                'max_output_tokens': 128_000,
            },
            # Superseded by Haiku 5.5 at a tenth of the price; no effort levels.
            'claude-haiku-4-5-20251001': {
                'input': 1.00, 'output': 5.00,
                'cache_read': 0.10,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'max_output_tokens': 64_000,
                'legacy': True,
            },
            # Latest Sonnet; same price as Sonnet 5.
            'claude-sonnet-5-5': {
                'input': 2.00, 'output': 10.00,
                'cache_read': 0.05,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'efforts': EFFORT_LEVELS, 'default_effort': 'high',
                'max_output_tokens': 128_000,
            },
            # Opus 5.5 and Fable 5.1 always think before answering; the
            # client keeps only the text blocks of a response. Thinking
            # cannot be disabled, and forced tool use is refused (400), so
            # structured output goes through `output_config.format`.
            'claude-opus-5-5': {
                'input': 4.00, 'output': 20.00,
                'cache_read': 0.05,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'efforts': EFFORT_LEVELS, 'default_effort': 'high',
                'max_output_tokens': 128_000,
            },
            'claude-fable-5-1': {
                'input': 10.00, 'output': 50.00,
                'cache_read': 0.025,
                'supports_pdf': True, 'supports_images': True,
                'supports_structured_output': True,
                'efforts': EFFORT_LEVELS, 'default_effort': 'high',
                'max_output_tokens': 128_000,
            },
        },
        # The extraction benchmark's choice (cannabis_results run r2,
        # decided 2026-10-12): Haiku 5.5 at its default effort, high, the
        # least expensive arm non-inferior to Opus 5.5 at high effort
        # within the benchmark's margins (2% of values, 10% of fully
        # correct COAs), at 0.038 of its cost on the same COAs. A larger
        # run is to narrow the margins.
        'default_model': 'claude-haiku-5-5',
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
        prompt_tokens: Optional[int] = None,
    ) -> Tuple[float, float]:
    """The input and output price of a model on a date.

    Args:
        model_config: A model's entry in ``AI_PROVIDERS``.
        on: The date (default: today). Entries of ``price_schedule``
            whose ``from`` date has arrived replace the base price, the
            latest winning.
        prompt_tokens: The request's prompt length (input plus cached
            tokens). Above a model's ``long_context`` threshold, its long
            context prices apply.

    Returns:
        ``(input, output)`` in USD per 1,000,000 tokens.
    """
    when = (on if isinstance(on, str) else (on or date.today()).isoformat())[:10]
    prices = (model_config['input'], model_config['output'])
    for change in sorted(model_config.get('price_schedule', []), key=lambda c: c['from']):
        if change['from'] <= when:
            prices = (change['input'], change['output'])
    tier = model_config.get('long_context')
    if tier and prompt_tokens is not None and prompt_tokens > tier['above']:
        prices = (tier['input'], tier['output'])
    return prices

def token_cost(
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cache_write_tokens: int = 0,
        cache_read_tokens: int = 0,
        cache_ttl: str = '5m',
        batch: bool = False,
        flex: bool = False,
        on: Optional[Union[date, str]] = None,
    ) -> float:
    """The USD cost of one request from its usage.

    Args:
        provider: Provider key.
        model: Model identifier.
        input_tokens: Uncached input tokens. (Anthropic reports cache
            reads and writes apart from ``input_tokens``.)
        output_tokens: Output tokens, thinking included.
        cache_write_tokens: Tokens written to the prompt cache.
        cache_read_tokens: Tokens read from the prompt cache.
        cache_ttl: ``'5m'`` or ``'1h'``, the duration of the cache written.
        batch: Whether the request ran in a batch (``batch_discount``).
        flex: Whether OpenAI flex processing was used.
        on: Price date (default: today); see ``effective_prices``.

    Raises:
        KeyError: For an unknown provider or model.
        ValueError: For a batch request to a provider without batches.
    """
    provider_config = AI_PROVIDERS[provider]
    model_config = provider_config['models'][model]
    prompt = input_tokens + cache_write_tokens + cache_read_tokens
    input_price, output_price = effective_prices(model_config, on, prompt_tokens=prompt)
    write = CACHE_WRITE_MULTIPLIERS.get(cache_ttl, CACHE_WRITE_MULTIPLIERS['5m'])
    read = model_config.get('cache_read', 0.1)
    cost = (
        input_tokens * input_price
        + cache_write_tokens * input_price * write
        + cache_read_tokens * input_price * read
        + output_tokens * output_price
    ) / 1_000_000
    if batch:
        discount = provider_config.get('batch_discount')
        if discount is None:
            raise ValueError(f'{provider} batches are not supported by cannlytics')
        cost *= discount
    if flex:
        cost *= FLEX_COST_MULTIPLIER
    return cost

def get_model_cost(
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        num_images: int = 0,
        flex: bool = False,
        on: Optional[Union[date, str]] = None,
        *,
        cache_write_tokens: int = 0,
        cache_read_tokens: int = 0,
        cache_ttl: str = '5m',
        batch: bool = False,
    ) -> float:
    """Calculate the cost of a single API call.

    Args:
        provider: Provider key (e.g., 'anthropic', 'openai').
        model: Model identifier (e.g., 'claude-haiku-5-5').
        input_tokens: Input tokens, as the API reports them (images and
            PDF pages included; for Anthropic, cache reads and writes are
            reported, and passed, apart).
        output_tokens: Output tokens, thinking included.
        num_images: Images sent. Adds a surcharge only for a model that
            declares ``image_cost``; none of the registered models do,
            since their images are already input tokens.
        flex: Whether OpenAI flex processing was used.
        on: Price date (default: today); see ``effective_prices``.
        cache_write_tokens: Tokens written to the prompt cache.
        cache_read_tokens: Tokens read from the prompt cache.
        cache_ttl: Duration of the cache written, ``'5m'`` or ``'1h'``.
        batch: Whether the call ran in a batch, at ``batch_discount``.

    Returns:
        Cost in USD.

    Raises:
        KeyError: If provider or model is not found in AI_PROVIDERS.
    """
    cost = token_cost(provider, model, input_tokens, output_tokens,
                      cache_write_tokens=cache_write_tokens, cache_read_tokens=cache_read_tokens,
                      cache_ttl=cache_ttl, batch=batch, flex=flex, on=on)
    return cost + num_images * AI_PROVIDERS[provider]['models'][model].get('image_cost', 0.0)

def resolve_effort(provider: str, model: str, effort: Optional[str] = None) -> Optional[str]:
    """The effort level to send: ``effort`` if the model accepts it, the
    model's ``default_effort`` if none is given, or ``None`` for a model
    without effort levels.

    Raises:
        ValueError: For an effort the model does not accept.
    """
    model_config = AI_PROVIDERS[resolve_provider(provider)]['models'][model]
    levels = model_config.get('efforts')
    if not levels:
        if effort:
            raise ValueError(f'{model} takes no effort level (asked for {effort!r}).')
        return None
    if effort is None:
        return model_config.get('default_effort')
    effort = str(effort).strip().lower()
    if effort not in levels:
        raise ValueError(f'{model} accepts effort {", ".join(levels)}; not {effort!r}.')
    return effort

def default_max_tokens(provider: str, model: str, effort: Optional[str] = None) -> int:
    """The output cap to send: room for thinking at the effort level
    (``EFFORT_MAX_TOKENS``), within the model's ``max_output_tokens``."""
    model_config = AI_PROVIDERS[resolve_provider(provider)]['models'][model]
    cap = model_config.get('max_output_tokens', 16_384)
    return min(cap, EFFORT_MAX_TOKENS.get(effort or '', cap))

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
