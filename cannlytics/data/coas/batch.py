"""
Message Batches for COA Extraction
Copyright (c) 2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/9/2026
Updated: 10/9/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Thousands of COAs at half price. Anthropic's Message Batches API runs
    requests asynchronously (most batches within an hour, all within 24)
    at 50% of the standard price on every token, which suits a dataset
    pipeline: nobody waits on any one COA. The website parses one COA at a
    time with ``AIClient.parse_coa``; both send the same request
    (``cannlytics.data.coas.extraction``).

    This module builds the requests, sizes them into batches, submits
    them, and reads the results back as ``BatchOutcome`` records with the
    extraction normalized and the cost computed from the usage at batch
    prices. What to do with the results (caches, ledgers, budgets) belongs
    to the pipeline that calls it.

    Limits (Anthropic, October 2026): 100,000 requests or 256 MB per batch,
    whichever comes first; a ``custom_id`` of 1 to 64 letters, digits,
    hyphens and underscores (a SHA-256 hex digest fits); results kept for
    29 days. Requests that error, are canceled, or expire are not billed.

    Other providers: ``batch_backend('openai')`` names the providers this
    module supports. A backend is a class with ``submit``, ``retrieve``,
    ``results`` and ``cancel``; adding OpenAI's or Gemini's batch APIs
    means adding one and registering it in ``BATCH_BACKENDS``.

    Usage::

        from cannlytics.data.coas.batch import AnthropicBatches, chunk_requests, extraction_request

        requests = [extraction_request(sha, path, 'claude-opus-5-5', effort='high')
                    for sha, path in pdfs]
        batches = AnthropicBatches(api_key='sk-ant-...')
        ids = [batches.submit(chunk) for chunk in chunk_requests(requests)]
        ...
        for outcome in batches.results(ids[0]):
            print(outcome.custom_id, outcome.status, outcome.cost)
"""
# Standard imports:
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

# Internal imports:
from cannlytics.data.coas.config import AI_PROVIDERS, token_cost
from cannlytics.data.coas.extraction import (
    anthropic_extraction_params,
    message_cost,
    message_usage,
    normalize_extraction,
    response_json,
)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Limits                                                           ║
# ╚══════════════════════════════════════════════════════════════════╝

MAX_BATCH_REQUESTS = 100_000
MAX_BATCH_BYTES = 256 * 1024 * 1024
# Batches are cut below the limit: the request list is serialized with
# the SDK's own framing, which this size does not count exactly.
DEFAULT_BATCH_BYTES = 200 * 1024 * 1024
# One Messages request may be at most 32 MB, in a batch or not.
MAX_REQUEST_BYTES = 32 * 1024 * 1024
CUSTOM_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Requests                                                         ║
# ╚══════════════════════════════════════════════════════════════════╝

def check_custom_id(custom_id: str) -> str:
    """The id if it is a valid ``custom_id``; raises ``ValueError`` if not."""
    if not isinstance(custom_id, str) or not CUSTOM_ID_PATTERN.match(custom_id):
        raise ValueError(f'custom_id must be 1-64 letters, digits, - or _: {custom_id!r}')
    return custom_id

def extraction_request(
        custom_id: str,
        document: Union[bytes, str],
        model: str,
        effort: Optional[str] = None,
        max_tokens: Optional[int] = None,
        cache_ttl: Optional[str] = '1h',
        **kwargs: Any,
    ) -> Dict[str, Any]:
    """One batch request extracting one COA.

    Args:
        custom_id: The id the result comes back with (a PDF's SHA-256).
        document: The PDF as bytes, a path, or base64.
        model: A Claude model.
        effort: Effort level (default: the model's ``default_effort``).
        max_tokens: Output cap, thinking included (default: by effort).
        cache_ttl: The system prompt's cache duration. One hour by
            default: a batch's requests can run more than five minutes
            apart, and a one-hour write pays for itself after two reads.
        **kwargs: Passed to ``anthropic_extraction_params``.
    """
    params = anthropic_extraction_params(model, document, effort=effort, max_tokens=max_tokens,
                                         cache_ttl=cache_ttl, **kwargs)
    return {'custom_id': check_custom_id(custom_id), 'params': params}

def request_bytes(request: Dict[str, Any]) -> int:
    """The serialized size of one request, as it is sent."""
    return len(json.dumps(request, separators=(',', ':')).encode('utf-8'))

def chunk_requests(
        requests: Iterable[Dict[str, Any]],
        max_bytes: int = DEFAULT_BATCH_BYTES,
        max_count: int = MAX_BATCH_REQUESTS,
    ) -> Iterator[List[Dict[str, Any]]]:
    """Group requests into batches under both limits, in order.

    A COA's PDF is most of its request, so the byte limit binds first: at
    the median COA (about 400 KB, 540 KB as base64) a 200 MB batch holds
    some 370 requests. Duplicate ``custom_id`` values raise, since results
    are matched to requests by them.

    Raises:
        ValueError: For a request over ``MAX_REQUEST_BYTES`` (or over
            ``max_bytes``), or a duplicate ``custom_id``.
    """
    chunk: List[Dict[str, Any]] = []
    size = 0
    seen = set()
    for request in requests:
        custom_id = check_custom_id(request.get('custom_id'))
        if custom_id in seen:
            raise ValueError(f'duplicate custom_id {custom_id}')
        seen.add(custom_id)
        n = request_bytes(request)
        if n > min(MAX_REQUEST_BYTES, max_bytes):
            raise ValueError(f'request {custom_id} is {n:,} bytes, over the '
                             f'{min(MAX_REQUEST_BYTES, max_bytes):,}-byte limit')
        if chunk and (size + n > max_bytes or len(chunk) >= max_count):
            yield chunk
            chunk, size = [], 0
        chunk.append(request)
        size += n
    if chunk:
        yield chunk

def estimate_cost(
        model: str,
        input_tokens: int,
        output_tokens: int,
        cache_read_tokens: int = 0,
        cache_write_tokens: int = 0,
        cache_ttl: str = '1h',
    ) -> float:
    """USD for one Claude request at batch prices."""
    return token_cost('anthropic', model, input_tokens, output_tokens,
                      cache_write_tokens=cache_write_tokens, cache_read_tokens=cache_read_tokens,
                      cache_ttl=cache_ttl, batch=True)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Results                                                          ║
# ╚══════════════════════════════════════════════════════════════════╝

@dataclass
class BatchOutcome:
    """One request's result.

    ``status`` is the API's: ``succeeded``, ``errored``, ``canceled`` or
    ``expired``. A succeeded request may still have no ``parsed`` answer:
    ``problem`` then says why (``refusal``, ``max_tokens``, ``no_json``),
    and its tokens were billed. ``cost`` is computed from the usage at
    batch prices; requests that did not succeed cost nothing, and a
    succeeded one whose model has no price is ``None``.
    """
    custom_id: str
    status: str
    parsed: Optional[Dict[str, Any]] = None
    problem: str = ''
    usage: Dict[str, int] = field(default_factory=lambda: {'input': 0, 'output': 0, 'cache_write': 0, 'cache_read': 0})
    cost: Optional[float] = 0.0
    model: str = ''
    stop_reason: str = ''
    error: str = ''

    @property
    def ok(self) -> bool:
        return self.status == 'succeeded' and self.parsed is not None

def _get(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)

def to_dict(obj: Any) -> Any:
    """A batch result (SDK object or dict) as plain JSON-serializable data,
    to keep the raw results: they were paid for, and the API deletes them
    after 29 days."""
    if isinstance(obj, (str, bytes)):
        return json.loads(obj)
    if hasattr(obj, 'model_dump'):
        return obj.model_dump(mode='json')
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    return json.loads(json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o))))

def priced_model(name: str, fallback: Optional[str] = None) -> Optional[str]:
    """The price-table entry for a model a response names.

    A response may name a dated snapshot (``claude-opus-5-5-20261001``) of
    the model requested; it is priced as the longest registered name it
    begins with, else as ``fallback`` (the model requested), else None.
    """
    models = AI_PROVIDERS['anthropic']['models']
    if name in models:
        return name
    prefixes = [m for m in models if name and name.startswith(m + '-')]
    if prefixes:
        return max(prefixes, key=len)
    return fallback if fallback in models else None

def outcome_from_result(result: Any, cache_ttl: str = '1h', model: Optional[str] = None) -> BatchOutcome:
    """A ``BatchOutcome`` from one line of a batch's results (an SDK
    object or the line's JSON as a dict).

    Args:
        result: The result line.
        cache_ttl: The prompt cache's duration, which prices cache writes.
        model: The model requested, which prices the usage when the
            response names a model the price table does not know. If
            neither is known the cost is ``None``: a budget must not count
            an unpriced answer as free.
    """
    if isinstance(result, (str, bytes)):
        result = json.loads(result)
    custom_id = _get(result, 'custom_id', '')
    inner = _get(result, 'result', None)
    status = _get(inner, 'type', '') or ''
    if status != 'succeeded':
        error = _get(inner, 'error', None)
        detail = _get(error, 'error', error)
        text = ''
        if detail is not None:
            text = ': '.join(str(x) for x in (_get(detail, 'type', ''), _get(detail, 'message', '')) if x)
        return BatchOutcome(custom_id=custom_id, status=status or 'unknown', problem=status or 'unknown', error=text)
    message = _get(inner, 'message', None)
    served = _get(message, 'model', '') or ''
    usage = message_usage(message)
    pricing = priced_model(served, model)
    cost = message_cost(pricing, usage, batch=True, cache_ttl=cache_ttl) if pricing else None
    parsed, problem = response_json(message)
    return BatchOutcome(
        custom_id=custom_id,
        status='succeeded',
        parsed=normalize_extraction(parsed) if parsed is not None else None,
        problem=problem,
        usage=usage,
        cost=cost,
        model=served or (model or ''),
        stop_reason=_get(message, 'stop_reason', '') or '',
    )

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Backends                                                         ║
# ╚══════════════════════════════════════════════════════════════════╝

class AnthropicBatches:
    """Anthropic's Message Batches: submit, poll, read results, cancel.

    Args:
        client: An ``anthropic.Anthropic`` client (or a test double).
        api_key: Used to make a client when none is given.
    """

    provider = 'anthropic'

    def __init__(self, client: Any = None, api_key: Optional[str] = None):
        if client is None:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key) if api_key else Anthropic()
        self.client = client

    def submit(self, requests: List[Dict[str, Any]]) -> str:
        """Create a batch; returns its id (``msgbatch_...``)."""
        if not requests:
            raise ValueError('no requests to submit')
        if len(requests) > MAX_BATCH_REQUESTS:
            raise ValueError(f'{len(requests):,} requests: at most {MAX_BATCH_REQUESTS:,} per batch')
        batch = self.client.messages.batches.create(requests=requests)
        return _get(batch, 'id')

    def retrieve(self, batch_id: str) -> Dict[str, Any]:
        """The batch's status: ``processing_status`` (``in_progress``,
        ``canceling`` or ``ended``), ``request_counts`` and its dates."""
        batch = self.client.messages.batches.retrieve(batch_id)
        counts = _get(batch, 'request_counts', None)
        return {
            'id': _get(batch, 'id', batch_id),
            'processing_status': _get(batch, 'processing_status', ''),
            'request_counts': {k: int(_get(counts, k, 0) or 0)
                               for k in ('processing', 'succeeded', 'errored', 'canceled', 'expired')},
            'created_at': str(_get(batch, 'created_at', '') or ''),
            'ended_at': str(_get(batch, 'ended_at', '') or ''),
            'expires_at': str(_get(batch, 'expires_at', '') or ''),
        }

    def raw_results(self, batch_id: str) -> Iterator[Dict[str, Any]]:
        """Each result line as plain data (``to_dict``), to be kept: the
        API deletes results 29 days after the batch was created."""
        for result in self.client.messages.batches.results(batch_id):
            yield to_dict(result)

    def results(self, batch_id: str, cache_ttl: str = '1h', model: Optional[str] = None) -> Iterator[BatchOutcome]:
        """Each request's outcome, streamed (in any order; match on
        ``custom_id``). Available once the batch has ended. ``model`` is
        the model requested (see ``outcome_from_result``)."""
        for result in self.client.messages.batches.results(batch_id):
            yield outcome_from_result(result, cache_ttl=cache_ttl, model=model)

    def cancel(self, batch_id: str) -> Dict[str, Any]:
        """Ask to cancel; requests not yet sent are not billed."""
        self.client.messages.batches.cancel(batch_id)
        return self.retrieve(batch_id)

    def count_tokens(self, params: Dict[str, Any]) -> int:
        """Input tokens of one request's ``params``, from the token
        counting endpoint (free; an estimate, as the API says)."""
        keys = ('model', 'system', 'messages', 'output_config')
        response = self.client.messages.count_tokens(**{k: params[k] for k in keys if k in params})
        return int(_get(response, 'input_tokens', 0) or 0)

BATCH_BACKENDS: Dict[str, Any] = {'anthropic': AnthropicBatches}

def batch_backend(provider: str, **kwargs: Any) -> Any:
    """The batch backend for a provider.

    Raises:
        NotImplementedError: For a provider without one yet, naming those
            with one.
    """
    key = str(provider).strip().lower()
    key = {'claude': 'anthropic'}.get(key, key)
    if key not in BATCH_BACKENDS:
        supported = ', '.join(sorted(BATCH_BACKENDS))
        known = 'a provider cannlytics knows' if key in AI_PROVIDERS else 'not a provider cannlytics knows'
        raise NotImplementedError(f'No batch backend for {provider!r} ({known}); batches are supported for: {supported}.')
    return BATCH_BACKENDS[key](**kwargs)
