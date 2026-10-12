"""
Whole-COA Extraction — Requests and Responses
Copyright (c) 2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/9/2026
Updated: 10/9/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    One request per COA: the PDF, the extraction prompt, and the
    ``COAExtraction`` schema as a structured output, so the model reads the
    PDF once and answers with its metadata and every analyte of every
    analysis. The per-analysis calls this replaces read the PDF (or its
    pages) once per analysis.

    The same request serves one COA at a time (``AIClient.parse_coa``, the
    website) and thousands in a Message Batch (``cannlytics.data.coas.batch``,
    the datasets), so the two cannot drift apart.

    Responses are normalized the same way whichever path made them:
    qualifiers from ``RESULT_QUALIFIERS``, canonical analyte keys, and a
    non-detect is a null value, never 0.0.

    Usage::

        from cannlytics.data.coas.extraction import anthropic_extraction_params

        params = anthropic_extraction_params('claude-opus-5-5', pdf_bytes, effort='high')
        message = client.messages.create(**params)          # or in a batch
        parsed, problem = response_json(message)
        coa = normalize_extraction(parsed)
        metadata, analyses = split_extraction(coa)
"""
# Standard imports:
import base64
import json
import os
from typing import Any, Dict, List, Optional, Tuple, Union

# Internal imports:
from cannlytics.data.coas.config import (
    AI_PROVIDERS,
    default_max_tokens,
    resolve_effort,
    token_cost,
)
from cannlytics.data.coas.pdf_utils import extract_json, long_path
from cannlytics.data.coas.prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    EXTRACTION_USER_PROMPT,
    PROMPT_VERSION,
)
from cannlytics.data.coas.schema import (
    ANALYSIS_NAMES,
    POTENCY_BASES,
    coa_extraction_schema,
    normalize_analyte_key,
    normalize_product_type,
    normalize_qualifier,
    parse_result_value,
)

# Fields of a metadata response that are numbers (null when not printed).
NUMERIC_METADATA = ('batch_size', 'sample_weight', 'total_cannabinoids',
                    'total_cbd', 'total_thc', 'total_terpenes')
NUMERIC_RESULT = ('value', 'limit', 'lod', 'loq')
# Qualifiers that mean no number is the result.
NO_NUMBER = {'ND', '<LOD', '<LOQ', '>ULOQ', 'detected', 'NR', 'NT'}

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Requests                                                         ║
# ╚══════════════════════════════════════════════════════════════════╝

def pdf_base64(document: Union[bytes, str]) -> str:
    """Base64 of a PDF given as bytes, a path, or base64 already."""
    if isinstance(document, bytes):
        return base64.standard_b64encode(document).decode('ascii')
    if isinstance(document, str) and os.path.exists(long_path(document)):
        with open(long_path(document), 'rb') as f:
            return base64.standard_b64encode(f.read()).decode('ascii')
    if isinstance(document, str):
        return document
    raise TypeError('document must be PDF bytes, a path, or base64 text')

def anthropic_extraction_params(
        model: str,
        document: Union[bytes, str],
        effort: Optional[str] = None,
        max_tokens: Optional[int] = None,
        system_prompt: str = EXTRACTION_SYSTEM_PROMPT,
        user_prompt: str = EXTRACTION_USER_PROMPT,
        schema: Optional[Dict[str, Any]] = None,
        cache_ttl: Optional[str] = '5m',
    ) -> Dict[str, Any]:
    """Messages API parameters to extract one COA with Claude.

    The system prompt comes first and is marked for caching (it is the
    same for every COA; a batch should use ``cache_ttl='1h'``, since its
    requests can run more than five minutes apart). The PDF follows as a
    document block, before the instruction, as the PDF guide advises.
    Effort and the JSON schema go in ``output_config``; thinking is left
    to the model (adaptive), since Opus 5.5 refuses to disable it.

    Args:
        model: A Claude model in ``AI_PROVIDERS['anthropic']``.
        document: The PDF as bytes, a path, or base64.
        effort: An effort level the model accepts (default: the model's
            ``default_effort``); ignored for a model without effort levels.
        max_tokens: Output cap, thinking included (default: by effort).
        system_prompt, user_prompt: The prompts (default: extraction).
        schema: The structured-output schema (default: ``COAExtraction``).
        cache_ttl: ``'5m'``, ``'1h'``, or ``None`` not to cache.

    Returns:
        A dict for ``client.messages.create(**params)`` or a batch
        request's ``params``.
    """
    config = AI_PROVIDERS['anthropic']['models'][model]
    level = resolve_effort('anthropic', model, effort) if config.get('efforts') else None
    system_block: Dict[str, Any] = {'type': 'text', 'text': system_prompt}
    if cache_ttl:
        system_block['cache_control'] = {'type': 'ephemeral', **({'ttl': '1h'} if cache_ttl == '1h' else {})}
    params: Dict[str, Any] = {
        'model': model,
        'max_tokens': int(max_tokens or default_max_tokens('anthropic', model, level)),
        'system': [system_block],
        'messages': [{
            'role': 'user',
            'content': [
                {'type': 'document',
                 'source': {'type': 'base64', 'media_type': 'application/pdf', 'data': pdf_base64(document)}},
                {'type': 'text', 'text': user_prompt},
            ],
        }],
    }
    output_config: Dict[str, Any] = {}
    if level:
        output_config['effort'] = level
    if config.get('supports_structured_output'):
        output_config['format'] = {'type': 'json_schema', 'schema': schema or coa_extraction_schema()}
    if output_config:
        params['output_config'] = output_config
    return params

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Responses                                                        ║
# ╚══════════════════════════════════════════════════════════════════╝

def _get(obj: Any, name: str, default: Any = None) -> Any:
    """A field of an SDK object or of a dict."""
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)

def message_text(message: Any) -> str:
    """The text blocks of a message, joined (thinking blocks left out)."""
    parts = []
    for block in _get(message, 'content', None) or []:
        if _get(block, 'type') == 'text' or (_get(block, 'type') is None and _get(block, 'text') is not None):
            parts.append(_get(block, 'text', '') or '')
    return ''.join(parts)

def message_usage(message: Any) -> Dict[str, int]:
    """Token usage: ``input`` (uncached), ``output`` (thinking included),
    ``cache_write`` and ``cache_read``."""
    usage = _get(message, 'usage', None)
    return {
        'input': int(_get(usage, 'input_tokens', 0) or 0),
        'output': int(_get(usage, 'output_tokens', 0) or 0),
        'cache_write': int(_get(usage, 'cache_creation_input_tokens', 0) or 0),
        'cache_read': int(_get(usage, 'cache_read_input_tokens', 0) or 0),
    }

def message_cost(model: str, usage: Dict[str, int], batch: bool = False, cache_ttl: str = '5m') -> float:
    """USD for a Claude message's usage (``message_usage``)."""
    return token_cost('anthropic', model, usage['input'], usage['output'],
                      cache_write_tokens=usage['cache_write'], cache_read_tokens=usage['cache_read'],
                      cache_ttl=cache_ttl, batch=batch)

def response_json(message: Any) -> Tuple[Optional[Dict[str, Any]], str]:
    """A message's JSON answer and, if there is none, why.

    Returns ``(parsed, '')`` on success; otherwise ``(None, problem)``
    with ``problem`` one of ``'refusal'``, ``'max_tokens'`` (the answer was
    cut off: raise ``max_tokens``), or ``'no_json'``.
    """
    stop = _get(message, 'stop_reason', '') or ''
    text = message_text(message)
    if stop == 'refusal':
        return None, 'refusal'
    parsed = None
    if text:
        try:
            parsed = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            parsed = extract_json(text)
    if not isinstance(parsed, dict):
        return None, ('max_tokens' if stop == 'max_tokens' else 'no_json')
    return parsed, ''

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Normalization                                                    ║
# ╚══════════════════════════════════════════════════════════════════╝

def _number(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value) if value == value else None
    number, _, _ = parse_result_value(value)
    return number

def _analysis(value: Any) -> str:
    text = str(value or '').strip().lower().replace(' ', '_').replace('-', '_')
    if text in ANALYSIS_NAMES:
        return text
    for name, words in (('cannabinoids', ('cannab', 'potency')), ('terpenes', ('terp',)),
                        ('pesticides', ('pestic',)), ('heavy_metals', ('metal',)),
                        ('microbials', ('micro', 'myco')), ('residual_solvents', ('solvent',)),
                        ('moisture_foreign_matter', ('moisture', 'water', 'foreign'))):
        if any(w in text for w in words):
            return name
    return 'other'

def normalize_result(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """One analyte row in the dataset's form, or None for a row with
    neither a key nor a name.

    The qualifier is put in the vocabulary (case-insensitively; a model
    may capitalize an enum value). A number that is printed text
    (``"<0.10"``) becomes a qualifier and a limit. A row qualified as not
    a number keeps no value: a non-detect answered as 0.0 is set to null.
    """
    if not isinstance(row, dict):
        return None
    name = str(row.get('name') or '').strip()
    raw_key = str(row.get('key') or '').strip()
    if not raw_key and not name:
        return None
    key = normalize_analyte_key(raw_key or name) or raw_key
    qualifier = normalize_qualifier(row.get('qualifier'))
    value = row.get('value')
    loq = _number(row.get('loq'))
    if isinstance(value, str):
        value, text_qualifier, limit = parse_result_value(value)
        qualifier = qualifier or text_qualifier
        if limit is not None and qualifier == '<LOQ' and loq is None:
            loq = limit
    else:
        value = _number(value)
    if qualifier in NO_NUMBER:
        value = None
    return {
        'analysis': _analysis(row.get('analysis')),
        'key': key,
        'name': name or raw_key,
        'value': value,
        'qualifier': qualifier,
        'units': str(row.get('units') or '').strip(),
        'limit': _number(row.get('limit')),
        'lod': _number(row.get('lod')),
        'loq': loq,
        'status': str(row.get('status') or '').strip().lower(),
    }

def normalize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Metadata with numbers as numbers or None, a standard product type,
    a potency basis from ``POTENCY_BASES``, and ``analyses`` as a list."""
    out = dict(metadata or {})
    for field in NUMERIC_METADATA:
        if field in out:
            out[field] = _number(out[field])
    if out.get('product_type'):
        out['product_type'] = normalize_product_type(out['product_type']) or out['product_type']
    basis = str(out.get('potency_basis') or '').strip().lower().replace(' ', '_')
    out['potency_basis'] = basis if basis in POTENCY_BASES else ''
    analyses = out.get('analyses') or []
    if isinstance(analyses, str):
        analyses = [a.strip() for a in analyses.split(',') if a.strip()]
    out['analyses'] = list(dict.fromkeys(_analysis(a) for a in analyses if str(a).strip()))
    for field in ('status',):
        if isinstance(out.get(field), str):
            out[field] = out[field].strip().lower()
    return out

def normalize_extraction(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """A whole-COA response normalized: ``{'metadata': {...}, 'results': [...]}``.

    Accepts the ``COAExtraction`` shape, or the single-page shape (results
    under one key per analysis).
    """
    parsed = parsed or {}
    metadata = normalize_metadata(parsed.get('metadata') or {})
    rows: List[Dict[str, Any]] = []
    if isinstance(parsed.get('results'), list):
        rows = parsed['results']
    else:
        for name in ANALYSIS_NAMES:
            for row in parsed.get(name) or []:
                if isinstance(row, dict):
                    rows.append({**row, 'analysis': row.get('analysis') or name})
    results = [r for r in (normalize_result(row) for row in rows) if r]
    found = [r['analysis'] for r in results]
    metadata['analyses'] = list(dict.fromkeys(metadata.get('analyses', []) + found))
    return {'metadata': metadata, 'results': results}

def split_extraction(coa: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    """``(metadata, {analysis: results})``: the shape of the per-analysis
    caches, so a whole-COA parse can be written where they are read."""
    analyses: Dict[str, List[Dict[str, Any]]] = {}
    for row in coa.get('results', []):
        item = {k: v for k, v in row.items() if k != 'analysis'}
        analyses.setdefault(row['analysis'], []).append(item)
    return dict(coa.get('metadata') or {}), analyses

def attribution(
        provider: str,
        model: str,
        effort: Optional[str],
        cost: float,
        mode: str = 'sync',
        seconds: Optional[float] = None,
        batch_id: Optional[str] = None,
    ) -> Dict[str, Any]:
    """The provenance fields recorded with a parse."""
    record = {
        'parsing_method': 'ai',
        'parsing_algorithm': None,
        'parsing_model': model,
        'parsing_provider': provider,
        'parsing_effort': effort,
        'parsing_mode': mode,
        'parsing_prompt_version': PROMPT_VERSION,
        'parsing_cost': round(float(cost), 6),
    }
    if seconds is not None:
        record['parsing_time'] = round(float(seconds), 2)
    if batch_id:
        record['parsing_batch_id'] = batch_id
    return record
