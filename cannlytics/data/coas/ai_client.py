"""
AI Client for COA Parsing — Multi-Provider Unified Interface
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/7/2024
Updated: 3/19/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Unified AI client supporting Anthropic Claude, OpenAI, Google
    Gemini, and xAI Grok for COA data extraction. Includes per-call
    cost tracking, OpenAI flex processing, and automatic fallback
    on rate limits.

    This module is consumed by the ``COAdoc`` parser class in
    ``parser.py``. It depends on ``config.py`` for AI provider
    definitions and ``pdf_utils.py`` for image encoding and JSON
    extraction. AI provider SDKs are imported lazily so they are
    only required when actually used.

    Public API:
        - CostTracker: Cumulative cost tracking across providers.
        - AIClient: Unified AI client with parse_metadata(),
          parse_analysis(), and parse_single_page() methods.
"""
# Standard imports:
import base64
import json
import logging
import os
import tempfile
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Internal imports (within cannlytics.data.coas):
from cannlytics.data.coas.config import (
    effective_prices,
    AI_PROVIDERS,
    FLEX_COST_MULTIPLIER,
    FLEX_TIMEOUT,
)
from cannlytics.data.coas.prompts import (
    METADATA_SYSTEM_PROMPT,
    METADATA_USER_PROMPT,
    ANALYSIS_SYSTEM_PROMPT,
    ANALYSIS_USER_PROMPT,
    SINGLE_PAGE_SYSTEM_PROMPT,
    SINGLE_PAGE_USER_PROMPT,
)
from cannlytics.data.coas.pdf_utils import (
    long_path,
    encode_image,
    extract_json,
    make_schema_strict,
    metadata_json_hint,
    analysis_json_hint,
    get_pdf_pages_as_images,
    extract_pdf_text,
)

# Lazy-import schema (Pydantic models may be None).
try:
    from cannlytics.data.coas.schema import (
        LabTestMetadata,
        LabAnalysis,
        PYDANTIC_AVAILABLE,
        PYDANTIC_IMPORT_ERROR,
    )
except ImportError:
    LabTestMetadata = None
    LabAnalysis = None
    PYDANTIC_AVAILABLE = False
    PYDANTIC_IMPORT_ERROR = 'cannlytics.data.coas.schema could not be imported'

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Cost Tracker                                                     ║
# ╚══════════════════════════════════════════════════════════════════╝

class CostTracker:
    """Track cumulative costs across all providers and models.

    Usage::

        tracker = CostTracker()
        tracker.record('anthropic', 'claude-haiku-4-5', 5000, 2000, 0.015)
        print(tracker.summary())
    """

    def __init__(self):
        self.records: List[Dict] = []
        self.total_cost: float = 0.0

    def record(
            self,
            provider: str,
            model: str,
            input_tokens: int,
            output_tokens: int,
            cost: float,
            analysis: str = '',
            pdf_hash: str = '',
        ):
        """Record a single API call's cost."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost,
            'analysis': analysis,
            'pdf_hash': pdf_hash,
        }
        self.records.append(entry)
        self.total_cost += cost

    def summary(self) -> Dict:
        """Get a summary of all costs."""
        by_provider = {}
        by_model = {}
        for r in self.records:
            prov = r['provider']
            mod = r['model']
            by_provider[prov] = by_provider.get(prov, 0.0) + r['cost']
            by_model[mod] = by_model.get(mod, 0.0) + r['cost']
        return {
            'total_cost': round(self.total_cost, 6),
            'total_calls': len(self.records),
            'by_provider': {k: round(v, 6) for k, v in by_provider.items()},
            'by_model': {k: round(v, 6) for k, v in by_model.items()},
        }

    def reset(self):
        """Reset all tracked costs."""
        self.records.clear()
        self.total_cost = 0.0

    def __str__(self) -> str:
        s = self.summary()
        return (
            f"Total: ${s['total_cost']:.4f} "
            f"({s['total_calls']} calls) | "
            f"By provider: {s['by_provider']}"
        )

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Flex Processing Detection                                        ║
# ╚══════════════════════════════════════════════════════════════════╝

def _is_flex_unavailable(error: Exception) -> bool:
    """Check if an OpenAI error is a flex-specific Resource Unavailable.

    OpenAI returns 429 "Resource Unavailable" when flex processing
    lacks capacity. This is distinct from rate-limit 429 errors and
    should trigger a retry with standard processing.
    """
    error_str = str(error).lower()
    status_code = getattr(error, 'status_code', None)
    if status_code == 429 and 'resource' in error_str:
        return True
    error_code = getattr(error, 'code', '')
    if error_code and 'resource' in str(error_code).lower():
        return True
    return False

# ╔══════════════════════════════════════════════════════════════════╗
# ║ AI Client                                                        ║
# ╚══════════════════════════════════════════════════════════════════╝

class AIClient:
    """Unified AI client supporting multiple providers.

    API key resolution order:
      1. Explicit ``api_key`` parameter (highest priority).
      2. ``config`` dict (e.g., from ``dotenv_values()``).
      3. Environment variable (e.g., ``ANTHROPIC_API_KEY``).

    AI provider SDKs (``anthropic``, ``openai``, ``google-genai``)
    are imported lazily on first use so they are not required at
    install time.

    Args:
        provider: Provider key — ``'anthropic'``, ``'openai'``,
            ``'gemini'``, or ``'xai'``.
        model: Model identifier. Defaults to the provider's default.
        api_key: Explicit API key (takes priority over all other sources).
        config: Optional dict mapping env key names to values
            (e.g., ``{'ANTHROPIC_API_KEY': 'sk-ant-...'}``).
        logger: Optional logger instance.

    Usage::

        client = AIClient(provider='anthropic', api_key='sk-ant-...')
        data, cost, in_tok, out_tok = client.parse_metadata(
            pdf_path='coa.pdf',
        )
    """

    def __init__(
            self,
            provider: str = 'anthropic',
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            config: Optional[Dict] = None,
            logger: Optional[logging.Logger] = None,
        ):
        self.provider = provider
        self.provider_config = AI_PROVIDERS[provider]
        self.model = model or self.provider_config['default_model']
        self.model_config = self.provider_config['models'][self.model]
        self._api_key = api_key
        self._config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.client = None
        self._exhausted = False
        self.use_flex = provider == 'openai'
        self._flex_failures = 0
        self._warned_unconstrained = False
        self._init_client()
        self._warn_if_structured_output_unavailable()

    def _warn_if_structured_output_unavailable(self):
        """Warn when this model supports structured output but pydantic
        is missing.

        Without pydantic, ``schema.py`` leaves the response models as
        ``None``, so the structured-output branch below is skipped and
        extraction falls back to free-text JSON. That fallback does not
        raise and does not appear in the output -- it shows up much
        later as drift in field coverage and null fidelity. Warn once,
        loudly, naming the package to install.
        """
        if (PYDANTIC_AVAILABLE
                or not self.supports_structured_output
                or self._warned_unconstrained):
            return
        self.logger.warning(
            '%s/%s supports schema-constrained extraction, but pydantic '
            'is not installed, so parsing will fall back to free-text '
            'JSON. Results will NOT be schema-constrained. '
            'Install it with: pip install "cannlytics[coa,ai]" '
            '(import error: %s)',
            self.provider, self.model, PYDANTIC_IMPORT_ERROR,
        )
        self._warned_unconstrained = True

    @property
    def structured_output_active(self) -> bool:
        """Whether extraction is actually schema-constrained.

        ``supports_structured_output`` describes the *model*. This
        describes the *runtime*: it is ``False`` when the model supports
        constrained extraction but pydantic is missing. Check this
        before trusting parsed output in a production pipeline.
        """
        return self.supports_structured_output and PYDANTIC_AVAILABLE

    def _resolve_api_key(self) -> str:
        """Resolve the API key from all available sources."""
        env_key = self.provider_config['env_key']
        # Priority: explicit → config dict → environment.
        return (
            self._api_key
            or self._config.get(env_key, '')
            or os.environ.get(env_key, '')
        )

    def _init_client(self):
        """Initialize the provider-specific SDK client."""
        api_key = self._resolve_api_key()
        if not api_key:
            self.logger.warning(
                f'{self.provider}: No API key found for '
                f'{self.provider_config["env_key"]}'
            )
            self._exhausted = True
            return

        if self.provider == 'openai':
            from openai import OpenAI
            self.client = OpenAI(
                api_key=api_key,
                timeout=FLEX_TIMEOUT,
            )

        elif self.provider == 'anthropic':
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)

        elif self.provider == 'gemini':
            from google import genai
            self.client = genai.Client(api_key=api_key)

        elif self.provider == 'xai':
            from openai import OpenAI
            self.client = OpenAI(
                api_key=api_key,
                base_url='https://api.x.ai/v1',
            )

    @property
    def is_available(self) -> bool:
        """Whether the client is initialized and not rate-limited."""
        return self.client is not None and not self._exhausted

    @property
    def supports_pdf(self) -> bool:
        return self.model_config.get('supports_pdf', False)

    @property
    def supports_structured_output(self) -> bool:
        return self.model_config.get('supports_structured_output', False)

    def calculate_cost(
            self,
            input_tokens: int,
            output_tokens: int,
            num_images: int = 0,
            used_flex: bool = False,
        ) -> float:
        """Calculate the cost of a single API call in USD.

        Token counts are the API's own, which already include image and
        PDF input; ``num_images`` adds a surcharge only for a model that
        declares ``image_cost`` (none of the registered models do).
        """
        input_price, output_price = effective_prices(self.model_config)
        token_cost = (input_tokens * input_price + output_tokens * output_price) / 1_000_000
        image_cost = num_images * self.model_config.get('image_cost', 0.0)
        cost = token_cost + image_cost
        if used_flex:
            cost *= FLEX_COST_MULTIPLIER
        return cost

    # ── Public parsing methods ─────────────────────────────────────

    def parse_metadata(
            self,
            pdf_path: Optional[str] = None,
            page_images: Optional[List[str]] = None,
            page_text: Optional[str] = None,
        ) -> Tuple[Optional[Dict], float, int, int]:
        """Parse metadata from a COA.

        Returns: ``(parsed_data, cost, input_tokens, output_tokens)``
        """
        return self._call_ai(
            system_prompt=METADATA_SYSTEM_PROMPT,
            user_prompt=METADATA_USER_PROMPT,
            pdf_path=pdf_path,
            page_images=page_images,
            page_text=page_text,
            response_schema=LabTestMetadata,
            mode='metadata',
        )

    def parse_analysis(
            self,
            analysis_name: str,
            analyte_keys: List[str],
            pdf_path: Optional[str] = None,
            page_images: Optional[List[str]] = None,
            page_text: Optional[str] = None,
        ) -> Tuple[Optional[Dict], float, int, int]:
        """Parse a specific analysis from a COA.

        Returns: ``(parsed_data, cost, input_tokens, output_tokens)``
        """
        user_prompt = ANALYSIS_USER_PROMPT % (
            analysis_name,
            '\n'.join(analyte_keys),
        )
        return self._call_ai(
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            pdf_path=pdf_path,
            page_images=page_images,
            page_text=page_text,
            response_schema=LabAnalysis,
            mode='analysis',
        )

    def parse_single_page(
            self,
            page_images: Optional[List[str]] = None,
            page_text: Optional[str] = None,
        ) -> Tuple[Optional[Dict], float, int, int]:
        """Parse a single-page COA in one shot (metadata + all results).

        Returns: ``(parsed_data, cost, input_tokens, output_tokens)``
        where parsed_data has ``'metadata'``, ``'cannabinoids'``,
        ``'terpenes'``, etc.
        """
        return self._call_ai(
            system_prompt=SINGLE_PAGE_SYSTEM_PROMPT,
            user_prompt=SINGLE_PAGE_USER_PROMPT,
            pdf_path=None,
            page_images=page_images,
            page_text=page_text,
            response_schema=None,
            mode='single_page',
        )

    # ── Unified dispatch ───────────────────────────────────────────

    def _call_ai(
            self,
            system_prompt: str,
            user_prompt: str,
            pdf_path: Optional[str] = None,
            page_images: Optional[List[str]] = None,
            page_text: Optional[str] = None,
            response_schema: Any = None,
            mode: str = 'metadata',
        ) -> Tuple[Optional[Dict], float, int, int]:
        """Unified AI call across all providers."""
        if not self.is_available:
            return None, 0.0, 0, 0

        try:
            if self.provider in ('openai', 'xai'):
                return self._call_openai(
                    system_prompt, user_prompt, pdf_path,
                    page_images, page_text, response_schema, mode,
                )
            elif self.provider == 'anthropic':
                return self._call_anthropic(
                    system_prompt, user_prompt, pdf_path,
                    page_images, page_text, mode,
                )
            elif self.provider == 'gemini':
                return self._call_gemini(
                    system_prompt, user_prompt, pdf_path,
                    page_images, page_text, response_schema, mode,
                )
        except Exception as e:
            error_str = str(e).lower()
            if '429' in error_str or 'rate' in error_str or 'quota' in error_str:
                self.logger.warning(f'{self.provider}: Rate limited / exhausted.')
                self._exhausted = True
            else:
                self.logger.error(f'{self.provider} error: {e}')
            return None, 0.0, 0, 0

    # ── OpenAI / xAI ──────────────────────────────────────────────

    def _call_openai(
            self,
            system_prompt, user_prompt, pdf_path,
            page_images, page_text, response_schema, mode,
        ) -> Tuple[Optional[Dict], float, int, int]:
        """Call OpenAI or xAI (OpenAI-compatible API)."""

        # Path A: PDF via Responses API (OpenAI only).
        if pdf_path and not page_images and self.provider == 'openai':
            return self._call_openai_responses_api(
                system_prompt, user_prompt, pdf_path,
                response_schema, mode,
            )

        # Path B: Images/text via Chat Completions.
        user_content = [{'type': 'text', 'text': user_prompt}]

        _temp_dir = None
        if pdf_path and not page_images:
            _temp_dir = tempfile.mkdtemp()
            page_images = get_pdf_pages_as_images(
                pdf_path,
                page_indexes=list(range(5)),
                output_dir=_temp_dir,
            )
            if not page_images:
                page_text = extract_pdf_text(pdf_path)

        if page_images:
            for img_path in page_images:
                b64 = encode_image(img_path)
                user_content.append({
                    'type': 'image_url',
                    'image_url': {'url': f'data:image/jpeg;base64,{b64}', 'detail': 'high'},
                })
        elif page_text:
            user_content[0]['text'] = f'{user_prompt}\n\nCOA Text:\n{page_text}'

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_content},
        ]

        kwargs = {'model': self.model, 'messages': messages}

        used_flex = False
        if self.use_flex and self.provider == 'openai':
            kwargs['service_tier'] = 'flex'
            used_flex = True

        if self.supports_structured_output and not response_schema \
                and not PYDANTIC_AVAILABLE and not self._warned_unconstrained:
            # Reached when a caller passed a response model that
            # schema.py set to None. Same degradation as above, but
            # detected at the call site.
            self.logger.warning(
                'Falling back to unconstrained free-text JSON extraction: '
                'pydantic is not installed. Install with: '
                'pip install "cannlytics[coa,ai]"'
            )
            self._warned_unconstrained = True

        if self.supports_structured_output and response_schema:
            try:
                completion = self.client.beta.chat.completions.parse(
                    **kwargs,
                    response_format=response_schema,
                    reasoning_effort='high',
                )
            except Exception as e:
                if used_flex and _is_flex_unavailable(e):
                    self.logger.info('Flex unavailable, retrying standard...')
                    kwargs.pop('service_tier', None)
                    used_flex = False
                    self._flex_failures += 1
                    completion = self.client.beta.chat.completions.parse(
                        **kwargs,
                        response_format=response_schema,
                        reasoning_effort='high',
                    )
                else:
                    raise
            msg = completion.choices[0].message
            if getattr(msg, 'refusal', None):
                self.logger.warning(f'Model refused: {msg.refusal}')
                return None, 0.0, 0, 0
            try:
                parsed = msg.parsed.model_dump()
            except Exception:
                return None, 0.0, 0, 0
        else:
            kwargs['max_completion_tokens'] = self.model_config.get(
                'max_output_tokens', 16_384,
            )
            try:
                completion = self.client.chat.completions.create(**kwargs)
            except Exception as e:
                if used_flex and _is_flex_unavailable(e):
                    self.logger.info('Flex unavailable, retrying standard...')
                    kwargs.pop('service_tier', None)
                    used_flex = False
                    self._flex_failures += 1
                    completion = self.client.chat.completions.create(**kwargs)
                else:
                    raise
            content = completion.choices[0].message.content
            parsed = extract_json(content)
            if parsed is None:
                return None, 0.0, 0, 0

        usage = getattr(completion, 'usage', None)
        in_tok = getattr(usage, 'prompt_tokens', 0) if usage else 0
        out_tok = getattr(usage, 'completion_tokens', 0) if usage else 0
        num_images = len(page_images) if page_images else 0
        cost = self.calculate_cost(in_tok, out_tok, num_images, used_flex=used_flex)

        if _temp_dir:
            import shutil
            shutil.rmtree(_temp_dir, ignore_errors=True)

        return parsed, cost, in_tok, out_tok

    def _call_openai_responses_api(
            self,
            system_prompt: str,
            user_prompt: str,
            pdf_path: str,
            response_schema: Any,
            mode: str,
        ) -> Tuple[Optional[Dict], float, int, int]:
        """Call OpenAI's Responses API with native PDF input."""
        with open(long_path(pdf_path), 'rb') as f:
            pdf_b64 = base64.b64encode(f.read()).decode('utf-8')

        pdf_filename = os.path.basename(pdf_path)
        input_content = [
            {'type': 'input_text', 'text': user_prompt},
            {
                'type': 'input_file',
                'filename': pdf_filename,
                'file_data': f'data:application/pdf;base64,{pdf_b64}',
            },
        ]

        kwargs = {
            'model': self.model,
            'instructions': system_prompt,
            'input': [{'role': 'user', 'content': input_content}],
        }

        if response_schema and hasattr(response_schema, 'model_json_schema'):
            schema_name = response_schema.__name__.lower()
            schema = response_schema.model_json_schema()
            make_schema_strict(schema)
            kwargs['text'] = {
                'format': {
                    'type': 'json_schema',
                    'name': schema_name,
                    'schema': schema,
                },
            }

        used_flex = False
        if self.use_flex:
            kwargs['service_tier'] = 'flex'
            used_flex = True

        try:
            response = self.client.responses.create(**kwargs)
        except Exception as e:
            if used_flex and _is_flex_unavailable(e):
                self.logger.info('Flex unavailable (Responses API), retrying standard...')
                kwargs.pop('service_tier', None)
                used_flex = False
                self._flex_failures += 1
                response = self.client.responses.create(**kwargs)
            else:
                raise

        output_text = response.output_text
        parsed = extract_json(output_text)
        if parsed is None:
            self.logger.warning(
                f'OpenAI Responses API: failed to parse JSON '
                f'from response ({len(output_text)} chars).'
            )
            return None, 0.0, 0, 0

        usage = getattr(response, 'usage', None)
        in_tok = getattr(usage, 'input_tokens', 0) if usage else 0
        out_tok = getattr(usage, 'output_tokens', 0) if usage else 0
        cost = self.calculate_cost(in_tok, out_tok, used_flex=used_flex)

        return parsed, cost, in_tok, out_tok

    # ── Anthropic ─────────────────────────────────────────────────

    def _call_anthropic(
            self,
            system_prompt, user_prompt, pdf_path,
            page_images, page_text, mode,
        ) -> Tuple[Optional[Dict], float, int, int]:
        """Call Anthropic Claude with PDF or image support."""
        content = []

        if pdf_path and self.supports_pdf:
            with open(long_path(pdf_path), 'rb') as f:
                pdf_b64 = base64.b64encode(f.read()).decode('utf-8')
            content.append({
                'type': 'document',
                'source': {
                    'type': 'base64',
                    'media_type': 'application/pdf',
                    'data': pdf_b64,
                },
            })
        elif page_images:
            for img_path in page_images:
                b64 = encode_image(img_path)
                content.append({
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': 'image/jpeg',
                        'data': b64,
                    },
                })
        elif page_text:
            user_prompt = f'{user_prompt}\n\nCOA Text:\n{page_text}'

        content.append({'type': 'text', 'text': user_prompt})

        if mode == 'metadata':
            json_schema = metadata_json_hint()
        else:
            json_schema = analysis_json_hint()

        enhanced_system = (
            f'{system_prompt}\n\n'
            f'IMPORTANT: Respond ONLY with valid JSON matching this schema:\n'
            f'{json_schema}'
        )

        # Streamed, then collected: the Anthropic SDK refuses a
        # non-streaming request whose `max_tokens` could run past ten
        # minutes (above about 21,000 tokens), so with the models' real
        # output limits every non-streaming call failed before it was sent.
        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.model_config.get('max_output_tokens', 16_384),
            system=enhanced_system,
            messages=[{'role': 'user', 'content': content}],
        ) as stream:
            response = stream.get_final_message()

        text = ''.join(
            block.text for block in response.content
            if hasattr(block, 'text')
        )
        parsed = extract_json(text)
        if parsed is None:
            return None, 0.0, 0, 0

        in_tok = response.usage.input_tokens
        out_tok = response.usage.output_tokens
        cost = self.calculate_cost(in_tok, out_tok)

        return parsed, cost, in_tok, out_tok

    # ── Gemini ────────────────────────────────────────────────────

    def _call_gemini(
            self,
            system_prompt, user_prompt, pdf_path,
            page_images, page_text, response_schema, mode,
        ) -> Tuple[Optional[Dict], float, int, int]:
        """Call Google Gemini with PDF or image support."""
        from google.genai import types

        contents = []

        if pdf_path and self.supports_pdf:
            with open(long_path(pdf_path), 'rb') as f:
                pdf_bytes = f.read()
            contents.append(types.Part.from_bytes(
                data=pdf_bytes, mime_type='application/pdf',
            ))
        elif page_images:
            for img_path in page_images:
                with open(img_path, 'rb') as f:
                    img_bytes = f.read()
                contents.append(types.Part.from_bytes(
                    data=img_bytes, mime_type='image/jpeg',
                ))
        elif page_text:
            user_prompt = f'{user_prompt}\n\nCOA Text:\n{page_text}'

        contents.append(user_prompt)

        gen_config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type='application/json',
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=gen_config,
        )

        parsed = extract_json(response.text)
        if parsed is None:
            return None, 0.0, 0, 0

        usage = response.usage_metadata
        in_tok = getattr(usage, 'prompt_token_count', 0) or 0
        # Thinking tokens are billed as output ("including thinking
        # tokens") but reported apart from the candidates.
        out_tok = (getattr(usage, 'candidates_token_count', 0) or 0) + (getattr(usage, 'thoughts_token_count', 0) or 0)
        cost = self.calculate_cost(in_tok, out_tok)

        return parsed, cost, in_tok, out_tok
