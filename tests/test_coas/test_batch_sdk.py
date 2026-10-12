"""
Message Batches through the real Anthropic SDK (1.0.6)
=======================================================
``AnthropicBatches`` against ``anthropic.Anthropic`` with its HTTP replaced
by a mock transport: what the SDK sends for a batch of extraction requests
(effort, the JSON schema, the hour-long prompt cache, the PDF), how it
reads results back from the results URL, and token counting. Nothing
leaves the machine.
"""
import base64
import json

import pytest

anthropic = pytest.importorskip('anthropic')
try:                        # the SDK's HTTP library: httpx2 from 1.11 on, httpx before
    import httpx2 as httpx
except ImportError:
    httpx = pytest.importorskip('httpx')

from cannlytics.data.coas.batch import AnthropicBatches, extraction_request

SHA = 'a' * 64
BATCH = 'msgbatch_013Zva2CMHLNnXjNJJKqJ2EF'
ANSWER = {'metadata': {'lab': 'KCA Laboratories', 'total_thc': 21.0},
          'results': [{'analysis': 'pesticides', 'key': 'abamectin', 'name': 'Abamectin', 'value': None,
                       'qualifier': 'ND', 'units': 'ppb', 'limit': 100.0, 'lod': None, 'loq': None,
                       'status': 'pass'}]}


def _batch(status: str, results_url=None) -> dict:
    return {'id': BATCH, 'type': 'message_batch', 'processing_status': status,
            'request_counts': {'processing': 0 if status == 'ended' else 1, 'succeeded': 1 if status == 'ended' else 0,
                               'errored': 0, 'canceled': 0, 'expired': 0},
            'created_at': '2026-10-09T12:00:00Z', 'expires_at': '2026-10-10T12:00:00Z',
            'ended_at': '2026-10-09T12:30:00Z' if status == 'ended' else None, 'archived_at': None,
            'cancel_initiated_at': None, 'results_url': results_url}


class Server:
    """The batch endpoints, recording what the SDK sent."""

    def __init__(self):
        self.sent = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        body = json.loads(request.content) if request.content else None
        self.sent.append((request.method, path, body))
        if request.method == 'POST' and path == '/v1/messages/batches':
            return httpx.Response(200, json=_batch('in_progress'))
        if request.method == 'GET' and path == f'/v1/messages/batches/{BATCH}':
            return httpx.Response(200, json=_batch('ended', f'https://api.anthropic.com/v1/messages/batches/{BATCH}/results'))
        if request.method == 'GET' and path == f'/v1/messages/batches/{BATCH}/results':
            line = {'custom_id': SHA, 'result': {'type': 'succeeded', 'message': {
                'id': 'msg_1', 'type': 'message', 'role': 'assistant', 'model': 'claude-opus-5-5',
                'content': [{'type': 'text', 'text': json.dumps(ANSWER)}], 'stop_reason': 'end_turn',
                'stop_sequence': None,
                'usage': {'input_tokens': 9_000, 'output_tokens': 3_000, 'cache_creation_input_tokens': 0,
                          'cache_read_input_tokens': 2_500}}}}
            expired = {'custom_id': 'b' * 64, 'result': {'type': 'expired'}}
            text = json.dumps(line) + '\n' + json.dumps(expired) + '\n'
            return httpx.Response(200, content=text.encode(), headers={'content-type': 'application/binary'})
        if request.method == 'POST' and path == f'/v1/messages/batches/{BATCH}/cancel':
            return httpx.Response(200, json=_batch('canceling'))
        if request.method == 'POST' and path == '/v1/messages/count_tokens':
            return httpx.Response(200, json={'input_tokens': 7_321})
        return httpx.Response(404, json={'type': 'error', 'error': {'type': 'not_found_error', 'message': path}})


@pytest.fixture
def server_and_batches():
    server = Server()
    client = anthropic.Anthropic(api_key='sk-ant-test', max_retries=0,
                                 http_client=httpx.Client(transport=httpx.MockTransport(server)))
    return server, AnthropicBatches(client=client)


def test_the_sdk_sends_effort_the_schema_the_cache_and_the_pdf(server_and_batches):
    server, batches = server_and_batches
    request = extraction_request(SHA, b'%PDF-1.4 fake', 'claude-opus-5-5', effort='max')
    assert batches.submit([request]) == BATCH
    method, path, body = server.sent[0]
    params = body['requests'][0]['params']
    assert body['requests'][0]['custom_id'] == SHA
    assert params['output_config']['effort'] == 'max'
    assert params['output_config']['format']['type'] == 'json_schema'
    assert params['system'][0]['cache_control'] == {'type': 'ephemeral', 'ttl': '1h'}
    document = params['messages'][0]['content'][0]
    assert base64.b64decode(document['source']['data']) == b'%PDF-1.4 fake'
    assert params['max_tokens'] == 128_000 and 'thinking' not in params and 'tool_choice' not in params


def test_the_sdk_reads_results_from_the_results_url(server_and_batches):
    server, batches = server_and_batches
    status = batches.retrieve(BATCH)
    assert status['processing_status'] == 'ended' and status['request_counts']['succeeded'] == 1
    outcomes = list(batches.results(BATCH, model='claude-opus-5-5'))
    ok, expired = outcomes
    assert ok.ok and ok.parsed['results'][0]['value'] is None and ok.parsed['results'][0]['qualifier'] == 'ND'
    assert ok.cost == pytest.approx((9_000 * 4.0 + 2_500 * 4.0 * 0.05 + 3_000 * 20.0) / 1e6 * 0.5)
    assert expired.status == 'expired' and expired.cost == 0.0
    raw = list(batches.raw_results(BATCH))
    assert raw[0]['result']['message']['usage']['cache_read_input_tokens'] == 2_500
    assert json.loads(json.dumps(raw)) == raw


def test_the_sdk_counts_tokens_and_cancels(server_and_batches):
    server, batches = server_and_batches
    params = extraction_request(SHA, b'%PDF-1.4 fake', 'claude-haiku-5-5', effort='low')['params']
    assert batches.count_tokens(params) == 7_321
    _, path, body = server.sent[-1]
    assert path == '/v1/messages/count_tokens' and set(body) == {'model', 'system', 'messages', 'output_config'}
    assert batches.cancel(BATCH)['processing_status'] == 'ended'      # retrieved after asking to cancel
    assert any(p.endswith('/cancel') for _, p, _ in server.sent)
