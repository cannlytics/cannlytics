"""
Tests for cannlytics.data.coas.ai_client
==========================================
Covers: CostTracker, AIClient initialization, API key resolution,
availability checks, cost calculation. Provider-specific API calls
are tested with unittest.mock to avoid real API calls.
"""
import os
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from cannlytics.data.coas.ai_client import (
    AIClient,
    CostTracker,
    _is_flex_unavailable,
)
from cannlytics.data.coas.config import AI_PROVIDERS

# ╔══════════════════════════════════════════════════════════════════╗
# ║ CostTracker                                                      ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCostTracker:

    def test_empty_tracker(self):
        ct = CostTracker()
        assert ct.total_cost == 0.0
        s = ct.summary()
        assert s['total_calls'] == 0
        assert s['total_cost'] == 0.0

    def test_record_and_summary(self):
        ct = CostTracker()
        ct.record('anthropic', 'claude-haiku', 5000, 2000, 0.015, 'metadata', 'abc123')
        ct.record('openai', 'gpt-5-nano', 3000, 1000, 0.005, 'cannabinoids', 'abc123')

        s = ct.summary()
        assert s['total_calls'] == 2
        assert abs(s['total_cost'] - 0.020) < 1e-10
        assert 'anthropic' in s['by_provider']
        assert 'openai' in s['by_provider']

    def test_reset(self):
        ct = CostTracker()
        ct.record('openai', 'gpt-5-nano', 1000, 500, 0.001)
        ct.reset()
        assert ct.total_cost == 0.0
        assert ct.summary()['total_calls'] == 0

    def test_str_representation(self):
        ct = CostTracker()
        ct.record('anthropic', 'claude-haiku', 1000, 500, 0.01)
        s = str(ct)
        assert '$0.01' in s
        assert '1 calls' in s

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Flex Detection                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestFlexDetection:

    def test_flex_resource_unavailable(self):
        err = MagicMock()
        err.status_code = 429
        err.__str__ = lambda self: 'Resource Unavailable'
        assert _is_flex_unavailable(err) is True

    def test_regular_rate_limit(self):
        err = MagicMock()
        err.status_code = 429
        err.__str__ = lambda self: 'Rate limit exceeded'
        err.code = ''
        assert _is_flex_unavailable(err) is False

    def test_non_429_error(self):
        err = MagicMock()
        err.status_code = 500
        err.__str__ = lambda self: 'Internal server error'
        err.code = ''
        assert _is_flex_unavailable(err) is False

# ╔══════════════════════════════════════════════════════════════════╗
# ║ AIClient Initialization                                          ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestAIClientInit:

    def test_no_key_marks_exhausted(self):
        """Client without any API key should be marked as exhausted."""
        # Clear env vars to ensure no key is found.
        with mock.patch.dict(os.environ, {}, clear=True):
            client = AIClient(provider='anthropic', api_key=None, config={})
            assert client.is_available is False

    def test_explicit_api_key_takes_priority(self):
        """Explicit api_key should override env vars."""
        with mock.patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'env-key'}):
            client = AIClient.__new__(AIClient)
            client.provider = 'anthropic'
            client.provider_config = AI_PROVIDERS['anthropic']
            client._api_key = 'explicit-key'
            client._config = {}
            resolved = client._resolve_api_key()
            assert resolved == 'explicit-key'

    def test_config_dict_key_used(self):
        """Config dict should be used when no explicit key."""
        client = AIClient.__new__(AIClient)
        client.provider = 'openai'
        client.provider_config = AI_PROVIDERS['openai']
        client._api_key = None
        client._config = {'OPENAI_API_KEY': 'config-key'}
        with mock.patch.dict(os.environ, {}, clear=True):
            resolved = client._resolve_api_key()
        assert resolved == 'config-key'

    def test_env_var_fallback(self):
        """Environment variable should be used as last resort."""
        client = AIClient.__new__(AIClient)
        client.provider = 'gemini'
        client.provider_config = AI_PROVIDERS['gemini']
        client._api_key = None
        client._config = {}
        with mock.patch.dict(os.environ, {'GOOGLE_API_KEY': 'env-key'}):
            resolved = client._resolve_api_key()
        assert resolved == 'env-key'

    def test_default_model_selection(self):
        """When no model specified, provider's default should be used."""
        with mock.patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test'}):
            with patch('cannlytics.data.coas.ai_client.AIClient._init_client'):
                client = AIClient(provider='anthropic')
                assert client.model == AI_PROVIDERS['anthropic']['default_model']

class TestAIClientProperties:

    def test_supports_pdf(self):
        """Anthropic Claude should support PDF input."""
        with mock.patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test'}):
            with patch('cannlytics.data.coas.ai_client.AIClient._init_client'):
                client = AIClient(provider='anthropic')
                assert client.supports_pdf is True

    def test_supports_structured_output(self):
        """OpenAI should support structured output."""
        with mock.patch.dict(os.environ, {'OPENAI_API_KEY': 'test'}):
            with patch('cannlytics.data.coas.ai_client.AIClient._init_client'):
                client = AIClient(provider='openai', model='gpt-5-nano')
                assert client.supports_structured_output is True

    def test_cost_calculation(self):
        with mock.patch.dict(os.environ, {'OPENAI_API_KEY': 'test'}):
            with patch('cannlytics.data.coas.ai_client.AIClient._init_client'):
                client = AIClient(provider='openai', model='gpt-5-nano')
                cost = client.calculate_cost(10_000, 5_000)
                # 10K * 0.05/1M + 5K * 0.40/1M = 0.0025
                assert abs(cost - 0.0025) < 1e-10

    def test_cost_with_flex(self):
        with mock.patch.dict(os.environ, {'OPENAI_API_KEY': 'test'}):
            with patch('cannlytics.data.coas.ai_client.AIClient._init_client'):
                client = AIClient(provider='openai', model='gpt-5-nano')
                standard = client.calculate_cost(10_000, 5_000)
                flex = client.calculate_cost(10_000, 5_000, used_flex=True)
                assert abs(flex - standard * 0.5) < 1e-10

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Mocked AI Calls                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestMockedAICalls:

    def _make_client(self, provider='openai'):
        """Create an AIClient with a mocked SDK client."""
        with mock.patch.dict(os.environ, {AI_PROVIDERS[provider]['env_key']: 'test-key'}):
            with patch('cannlytics.data.coas.ai_client.AIClient._init_client'):
                client = AIClient(provider=provider)
                client.client = MagicMock()
                client._exhausted = False
                return client

    def test_call_ai_returns_none_when_exhausted(self):
        client = self._make_client()
        client._exhausted = True
        result = client._call_ai('sys', 'user')
        assert result == (None, 0.0, 0, 0)

    def test_rate_limit_marks_exhausted(self):
        """429 errors should mark the client as exhausted."""
        client = self._make_client()
        client.client.beta.chat.completions.parse.side_effect = Exception('429 Rate limit')
        client.use_flex = False

        result = client._call_ai(
            'system prompt', 'user prompt',
            response_schema=MagicMock(model_json_schema=MagicMock()),
        )
        assert result == (None, 0.0, 0, 0)
        assert client._exhausted is True

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Provider call paths with fake SDK clients                         ║
# ╚══════════════════════════════════════════════════════════════════╝

class _Block:
    def __init__(self, **fields):
        self.__dict__.update(fields)

class _FakeAnthropic:
    """Records calls; `messages.create` must never be used."""

    def __init__(self, blocks, input_tokens=1_000, output_tokens=200):
        self.calls = []
        final = _Block(content=blocks, usage=_Block(input_tokens=input_tokens, output_tokens=output_tokens))
        fake = self

        class _Stream:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def get_final_message(self):
                return final

        class _Messages:
            def stream(self, **kwargs):
                fake.calls.append(('stream', kwargs))
                return _Stream()

            def create(self, **kwargs):
                fake.calls.append(('create', kwargs))
                raise AssertionError('non-streaming call')

        self.messages = _Messages()

def _client(provider, fake, model=None):
    with mock.patch.dict(os.environ, {}, clear=True):
        client = AIClient(provider=provider, model=model, api_key=None, config={})
    client.client, client._exhausted = fake, False
    return client

class TestAnthropicStreams:

    def test_streams_with_the_full_output_limit_and_keeps_only_text(self):
        # A thinking block (no `.text`) precedes the answer on Opus 5.5 and Fable 5.1.
        fake = _FakeAnthropic([_Block(thinking='...', signature='sig'), _Block(text='{"lab": "KCA"}')])
        client = _client('anthropic', fake, model='claude-opus-5-5')
        parsed, cost, in_tok, out_tok = client._call_anthropic('system', 'user', None, None, 'COA text', 'metadata')
        assert parsed == {'lab': 'KCA'} and (in_tok, out_tok) == (1_000, 200)
        assert [kind for kind, _ in fake.calls] == ['stream']
        assert fake.calls[0][1]['max_tokens'] == 128_000
        assert cost == pytest.approx((1_000 * 4.00 + 200 * 20.00) / 1_000_000)

    def test_default_model_request_would_exceed_the_sdk_non_streaming_limit(self):
        # The reason for streaming: above ~21,333 tokens the SDK refuses a
        # non-streaming request before sending it.
        model = AI_PROVIDERS['anthropic']['default_model']
        assert AI_PROVIDERS['anthropic']['models'][model]['max_output_tokens'] > 21_333

class _FakeGemini:
    def __init__(self, text, usage):
        response = _Block(text=text, usage_metadata=usage)
        self.models = _Block(generate_content=lambda **kwargs: response)

class TestGeminiCountsThinking:

    def test_thinking_tokens_are_billed_as_output(self):
        pytest.importorskip('google.genai')
        usage = _Block(prompt_token_count=1_000, candidates_token_count=300, thoughts_token_count=700)
        client = _client('gemini', _FakeGemini('{"lab": "KCA"}', usage), model='gemini-3.8-flash')
        with mock.patch('cannlytics.data.coas.config.date') as fake_date:
            fake_date.today.return_value = __import__('datetime').date(2026, 10, 1)
            parsed, cost, in_tok, out_tok = client._call_gemini('system', 'user', None, None, 'COA text', None, 'metadata')
        assert parsed == {'lab': 'KCA'} and out_tok == 1_000
        assert cost == pytest.approx((1_000 * 0.75 + 1_000 * 3.75) / 1_000_000)

    def test_missing_thinking_count_is_zero(self):
        pytest.importorskip('google.genai')
        usage = _Block(prompt_token_count=10, candidates_token_count=5, thoughts_token_count=None)
        client = _client('gemini', _FakeGemini('{"a": 1}', usage), model='gemini-2.5-flash')
        assert client._call_gemini('s', 'u', None, None, 'text', None, 'metadata')[3] == 5
