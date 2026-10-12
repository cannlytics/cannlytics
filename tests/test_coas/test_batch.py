"""
Message Batches for COA extraction (1.0.6)
==========================================
Requests are sized into batches under Anthropic's limits (100,000
requests or 256 MB), matched back by ``custom_id`` (a PDF's SHA-256), and
read as outcomes with the extraction normalized and the cost at batch
prices. The SDK is replaced by a fake: nothing here calls the API.
"""
import hashlib
import json

import pytest

pytest.importorskip('pydantic')

from cannlytics.data.coas.batch import (
    MAX_REQUEST_BYTES,
    AnthropicBatches,
    BatchOutcome,
    batch_backend,
    check_custom_id,
    chunk_requests,
    estimate_cost,
    extraction_request,
    outcome_from_result,
    priced_model,
    request_bytes,
    to_dict,
)

SHA = hashlib.sha256(b'coa').hexdigest()

def _request(i, size=1_000):
    return {'custom_id': f'r{i}', 'params': {'model': 'claude-opus-5-5', 'blob': 'x' * size}}

# ── Requests ──────────────────────────────────────────────────────

def test_a_sha256_is_a_valid_custom_id_and_other_ids_are_checked():
    assert check_custom_id(SHA) == SHA and len(SHA) == 64
    for bad in ('a' * 65, 'has space', '', 'slash/'):
        with pytest.raises(ValueError):
            check_custom_id(bad)

def test_an_extraction_request_carries_the_pdf_and_an_hour_long_prompt_cache():
    request = extraction_request(SHA, b'%PDF-1.4 x', 'claude-opus-5-5', effort='max')
    assert request['custom_id'] == SHA
    params = request['params']
    assert params['system'][0]['cache_control'] == {'type': 'ephemeral', 'ttl': '1h'}
    assert params['output_config']['effort'] == 'max'
    assert request_bytes(request) == len(json.dumps(request, separators=(',', ':')).encode())

def test_batches_are_cut_by_size_and_by_count():
    requests = [_request(i) for i in range(10)]
    one = request_bytes(requests[0])
    by_size = list(chunk_requests(requests, max_bytes=3 * one))
    assert [len(c) for c in by_size] == [3, 3, 3, 1]
    by_count = list(chunk_requests(requests, max_count=4))
    assert [len(c) for c in by_count] == [4, 4, 2]
    assert [r['custom_id'] for c in by_size for r in c] == [f'r{i}' for i in range(10)]

def test_a_duplicate_id_or_an_oversized_request_is_refused():
    with pytest.raises(ValueError, match='duplicate'):
        list(chunk_requests([_request(1), _request(1)]))
    with pytest.raises(ValueError, match='limit'):
        list(chunk_requests([_request(1, size=MAX_REQUEST_BYTES + 1)]))

def test_batch_prices_are_half():
    full = (20_000 * 4.0 + 8_000 * 20.0) / 1e6
    assert estimate_cost('claude-opus-5-5', 20_000, 8_000) == pytest.approx(full / 2)
    # Haiku 5.5: a tenth of a cent per thousand COA pages, roughly.
    assert estimate_cost('claude-haiku-5-5', 20_000, 8_000) == pytest.approx((20_000 * 0.10 + 8_000 * 0.50) / 1e6 / 2)

# ── Results ───────────────────────────────────────────────────────

def _succeeded(custom_id, text, stop='end_turn', **usage):
    return {'custom_id': custom_id, 'result': {'type': 'succeeded', 'message': {
        'model': 'claude-opus-5-5', 'stop_reason': stop,
        'content': [{'type': 'thinking', 'thinking': '.'}, {'type': 'text', 'text': text}],
        'usage': {'input_tokens': 10_000, 'output_tokens': 2_000, **usage}}}}

ANSWER = json.dumps({'metadata': {'lab': 'KCA Labs', 'total_thc': 21.0, 'batch_size': None},
                     'results': [{'analysis': 'pesticides', 'key': 'abamectin', 'name': 'Abamectin',
                                  'value': 0.0, 'qualifier': 'ND', 'units': 'ppb', 'limit': 100.0,
                                  'lod': None, 'loq': None, 'status': 'pass'}]})

def test_a_succeeded_result_is_normalized_and_priced_at_batch_rates():
    outcome = outcome_from_result(_succeeded(SHA, ANSWER, cache_read_input_tokens=2_000))
    assert outcome.ok and outcome.status == 'succeeded' and outcome.problem == ''
    assert outcome.parsed['metadata']['lab'] == 'KCA Labs'
    assert outcome.parsed['results'][0]['value'] is None        # ND, never 0.0
    expected = (10_000 * 4.0 + 2_000 * 4.0 * 0.05 + 2_000 * 20.0) / 1e6 * 0.5
    assert outcome.cost == pytest.approx(expected)

def test_a_truncated_answer_is_billed_but_has_nothing_to_keep():
    outcome = outcome_from_result(_succeeded(SHA, '{"metadata": {"lab": "K', stop='max_tokens'))
    assert not outcome.ok and outcome.problem == 'max_tokens' and outcome.cost > 0

def test_a_dated_snapshot_is_priced_as_the_model_it_belongs_to():
    assert priced_model('claude-opus-5-5') == 'claude-opus-5-5'
    assert priced_model('claude-opus-5-5-20261001') == 'claude-opus-5-5'
    assert priced_model('claude-haiku-5-5-20261001') == 'claude-haiku-5-5'
    assert priced_model('claude-next', fallback='claude-sonnet-5-5') == 'claude-sonnet-5-5'
    assert priced_model('claude-next') is None

def test_an_answer_from_an_unknown_model_is_priced_as_requested_or_not_at_all():
    line = _succeeded(SHA, ANSWER)
    line['result']['message']['model'] = 'claude-next'
    assert outcome_from_result(line, model='claude-opus-5-5').cost == pytest.approx(
        outcome_from_result(_succeeded(SHA, ANSWER)).cost)
    # Unpriced is None, never 0.0: a budget must not count it as free.
    assert outcome_from_result(line).cost is None

def test_raw_results_are_plain_data():
    class Model:
        def model_dump(self, mode='python'):
            return {'custom_id': SHA, 'result': {'type': 'expired'}}
    assert to_dict(Model()) == {'custom_id': SHA, 'result': {'type': 'expired'}}
    assert to_dict(json.dumps({'a': 1})) == {'a': 1}
    assert to_dict({'a': [1, 2]}) == {'a': [1, 2]}

@pytest.mark.parametrize('kind', ['errored', 'canceled', 'expired'])
def test_requests_that_did_not_run_cost_nothing(kind):
    line = {'custom_id': SHA, 'result': {'type': kind}}
    if kind == 'errored':
        line['result']['error'] = {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'bad pdf'}}
    outcome = outcome_from_result(json.dumps(line))
    assert outcome.status == kind and outcome.cost == 0.0 and not outcome.ok
    if kind == 'errored':
        assert outcome.error == 'invalid_request_error: bad pdf'

# ── The backend, against a fake SDK ───────────────────────────────

class _FakeBatches:
    def __init__(self, lines):
        self.lines, self.created, self.canceled = lines, [], []

    def create(self, requests):
        self.created.append(requests)
        return {'id': 'msgbatch_1'}

    def retrieve(self, batch_id):
        return {'id': batch_id, 'processing_status': 'ended', 'created_at': '2026-10-09T00:00:00Z',
                'request_counts': {'processing': 0, 'succeeded': 1, 'errored': 1, 'canceled': 0, 'expired': 0}}

    def results(self, batch_id):
        return iter(self.lines)

    def cancel(self, batch_id):
        self.canceled.append(batch_id)

class _FakeMessages:
    def __init__(self, lines):
        self.batches = _FakeBatches(lines)
        self.counted = []

    def count_tokens(self, **kwargs):
        self.counted.append(kwargs)
        return {'input_tokens': 12_345}

class _FakeClient:
    def __init__(self, lines):
        self.messages = _FakeMessages(lines)

def test_submit_status_results_and_cancel():
    lines = [_succeeded(SHA, ANSWER), {'custom_id': 'b' * 64, 'result': {'type': 'expired'}}]
    client = _FakeClient(lines)
    batches = AnthropicBatches(client=client)
    request = extraction_request(SHA, b'%PDF x', 'claude-opus-5-5')
    assert batches.submit([request]) == 'msgbatch_1'
    assert client.messages.batches.created == [[request]]
    status = batches.retrieve('msgbatch_1')
    assert status['processing_status'] == 'ended' and status['request_counts']['errored'] == 1
    outcomes = list(batches.results('msgbatch_1'))
    assert [o.status for o in outcomes] == ['succeeded', 'expired']
    assert all(isinstance(o, BatchOutcome) for o in outcomes)
    raw = list(batches.raw_results('msgbatch_1'))
    assert raw[1] == {'custom_id': 'b' * 64, 'result': {'type': 'expired'}}
    assert json.loads(json.dumps(raw)) == raw
    batches.cancel('msgbatch_1')
    assert client.messages.batches.canceled == ['msgbatch_1']

def test_token_counting_sends_only_what_the_endpoint_takes():
    client = _FakeClient([])
    params = extraction_request(SHA, b'%PDF x', 'claude-opus-5-5')['params']
    assert AnthropicBatches(client=client).count_tokens(params) == 12_345
    assert set(client.messages.counted[0]) == {'model', 'system', 'messages', 'output_config'}

def test_an_empty_or_oversized_submission_is_refused():
    with pytest.raises(ValueError):
        AnthropicBatches(client=_FakeClient([])).submit([])

def test_other_providers_name_the_ones_with_batches():
    assert isinstance(batch_backend('claude', client=_FakeClient([])), AnthropicBatches)
    with pytest.raises(NotImplementedError, match='anthropic'):
        batch_backend('openai')
