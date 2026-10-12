"""
Whole-COA extraction (1.0.6)
============================
One request per COA, the same for one COA (``AIClient.parse_coa``) and
thousands (``batch``): the PDF once, the extraction prompt, effort and the
``COAExtraction`` schema as a structured output. Responses are normalized
the same way on both paths, and a non-detect is a null value, never 0.0.
"""
import json

import pytest

pytest.importorskip('pydantic')

from cannlytics.data.coas.config import AI_PROVIDERS
from cannlytics.data.coas.extraction import (
    anthropic_extraction_params,
    attribution,
    message_cost,
    message_usage,
    normalize_extraction,
    normalize_result,
    response_json,
    split_extraction,
)
from cannlytics.data.coas.prompts import EXTRACTION_SYSTEM_PROMPT, PROMPT_VERSION
from cannlytics.data.coas.schema import (
    MAX_OPTIONAL_PROPERTIES,
    MAX_UNION_PROPERTIES,
    RESULT_QUALIFIERS,
    coa_extraction_schema,
    normalize_qualifier,
    parse_result_value,
    schema_complexity,
)

PDF = b'%PDF-1.4 fake'

# ── The request ───────────────────────────────────────────────────

def test_the_request_caches_the_prompt_sends_the_pdf_first_and_constrains_the_answer():
    params = anthropic_extraction_params('claude-opus-5-5', PDF, effort='high')
    system = params['system'][0]
    assert system['text'] == EXTRACTION_SYSTEM_PROMPT
    assert system['cache_control'] == {'type': 'ephemeral'}
    content = params['messages'][0]['content']
    assert [block['type'] for block in content] == ['document', 'text']
    assert content[0]['source']['media_type'] == 'application/pdf'
    assert params['output_config']['effort'] == 'high'
    assert params['output_config']['format'] == {'type': 'json_schema', 'schema': coa_extraction_schema()}
    assert params['max_tokens'] == 64_000
    # Opus 5.5 refuses forced tool use and disabled thinking (400).
    assert 'tool_choice' not in params and 'thinking' not in params and 'tools' not in params

def test_a_batch_caches_the_prompt_for_an_hour():
    params = anthropic_extraction_params('claude-sonnet-5-5', PDF, cache_ttl='1h')
    assert params['system'][0]['cache_control'] == {'type': 'ephemeral', 'ttl': '1h'}
    assert params['output_config']['effort'] == 'high'      # the model's default, sent explicitly

def test_no_cache_and_no_effort_where_none_applies():
    params = anthropic_extraction_params('claude-haiku-4-5-20251001', PDF, cache_ttl=None)
    assert 'cache_control' not in params['system'][0]
    assert 'effort' not in params['output_config'] and 'format' in params['output_config']

def test_an_effort_the_model_does_not_take_is_refused():
    with pytest.raises(ValueError):
        anthropic_extraction_params('claude-opus-5-5', PDF, effort='extreme')

def test_max_effort_gets_the_full_output_limit():
    assert anthropic_extraction_params('claude-opus-5-5', PDF, effort='max')['max_tokens'] == 128_000
    assert anthropic_extraction_params('claude-haiku-5-5', PDF, effort='low')['max_tokens'] == 16_000

# ── The schema ────────────────────────────────────────────────────

def test_the_schema_is_within_structured_output_limits():
    schema = coa_extraction_schema()
    counts = schema_complexity(schema)
    assert counts['optional'] == 0 <= MAX_OPTIONAL_PROPERTIES
    assert counts['unions'] <= MAX_UNION_PROPERTIES

def test_the_schema_uses_only_supported_keywords():
    text = json.dumps(coa_extraction_schema())
    for keyword in ('minimum', 'maximum', 'multipleOf', 'minLength', 'maxLength', '"pattern"', 'oneOf'):
        assert keyword not in text

    def objects(node):
        if isinstance(node, dict):
            if node.get('type') == 'object':
                yield node
            for v in node.values():
                yield from objects(v)
        elif isinstance(node, list):
            for v in node:
                yield from objects(v)

    for obj in objects(coa_extraction_schema()):
        assert obj['additionalProperties'] is False
        assert set(obj['required']) == set(obj['properties'])

def test_non_detects_and_missing_numbers_can_be_null_in_the_schema():
    defs = coa_extraction_schema()['$defs']
    value = defs['COAResult']['properties']['value']
    assert {'type': 'null'} in value['anyOf']
    assert defs['COAResult']['properties']['qualifier']['enum'] == list(RESULT_QUALIFIERS)
    assert {'type': 'null'} in defs['LabTestMetadata']['properties']['total_thc']['anyOf']

def test_the_prompt_never_asks_for_a_non_detect_as_zero():
    from cannlytics.data.coas import prompts
    for name in ('EXTRACTION_SYSTEM_PROMPT', 'ANALYSIS_SYSTEM_PROMPT', 'SINGLE_PAGE_SYSTEM_PROMPT'):
        text = getattr(prompts, name)
        assert '"ND" (Not Detected) → value = 0.0' not in text
        assert '"ND" = 0.0' not in text
    assert 'Never record a non-detect as 0' in prompts.EXTRACTION_SYSTEM_PROMPT
    assert PROMPT_VERSION

# ── Qualifiers ────────────────────────────────────────────────────

@pytest.mark.parametrize('text, expected', [
    ('ND', (None, 'ND', None)), ('Not Detected', (None, 'ND', None)), ('absent', (None, 'ND', None)),
    ('<LOQ', (None, '<LOQ', None)), ('<0.10', (None, '<LOQ', 0.1)), ('<LOQ (0.05)', (None, '<LOQ', 0.05)),
    ('BQL', (None, '<LOQ', None)), ('>100', (None, '>ULOQ', 100.0)), ('Present', (None, 'detected', None)),
    ('N/A', (None, 'NR', None)), ('12.5', (12.5, '', None)), ('1,234.5 ppm', (1234.5, '', None)),
    (0, (0.0, '', None)), (None, (None, '', None)),
])
def test_printed_results_are_read(text, expected):
    assert parse_result_value(text) == expected

def test_qualifiers_are_compared_without_case():
    # Structured outputs do not guarantee an enum's capitalization.
    assert normalize_qualifier('nd') == 'ND' and normalize_qualifier('Detected') == 'detected'
    assert normalize_qualifier('<loq') == '<LOQ' and normalize_qualifier('12.1') == ''

# ── Normalization ─────────────────────────────────────────────────

def test_a_non_detect_answered_as_zero_becomes_null():
    row = normalize_result({'analysis': 'Pesticides', 'key': 'abamectin', 'name': 'Abamectin',
                            'value': 0.0, 'qualifier': 'nd', 'units': 'ppb', 'limit': 100, 'lod': 10, 'loq': None,
                            'status': 'Pass'})
    assert row['value'] is None and row['qualifier'] == 'ND'
    assert row['analysis'] == 'pesticides' and row['status'] == 'pass'
    assert row['limit'] == 100.0 and row['lod'] == 10.0 and row['loq'] is None

def test_a_measured_zero_stays_zero():
    assert normalize_result({'key': 'cbn', 'name': 'CBN', 'value': 0, 'qualifier': ''})['value'] == 0.0

def test_a_result_answered_as_text_is_read():
    row = normalize_result({'analysis': 'cannabinoids', 'key': 'cbg', 'name': 'CBG', 'value': '<0.05'})
    assert (row['value'], row['qualifier'], row['loq']) == (None, '<LOQ', 0.05)

def test_rows_without_key_or_name_are_dropped():
    assert normalize_result({'value': 1.0}) is None
    assert normalize_result('not a row') is None

def test_the_extraction_shape_and_the_single_page_shape_normalize_alike():
    whole = {'metadata': {'total_thc': '21.3', 'batch_size': None, 'product_type': 'Pre-Roll',
                          'potency_basis': 'Dry Weight', 'analyses': ['Cannabinoids']},
             'results': [{'analysis': 'cannabinoids', 'key': 'thca', 'name': 'THCa', 'value': 24.1, 'qualifier': ''},
                         {'analysis': 'terpenes', 'key': 'linalool', 'name': 'Linalool', 'value': None, 'qualifier': 'ND'}]}
    page = {'metadata': whole['metadata'],
            'cannabinoids': [{'key': 'thca', 'name': 'THCa', 'value': 24.1}],
            'terpenes': [{'key': 'linalool', 'name': 'Linalool', 'value': 'ND'}]}
    a, b = normalize_extraction(whole), normalize_extraction(page)
    assert a['metadata']['total_thc'] == 21.3 and a['metadata']['batch_size'] is None
    assert a['metadata']['potency_basis'] == 'dry_weight'
    assert a['metadata']['analyses'] == ['cannabinoids', 'terpenes']
    assert [(r['analysis'], r['key'], r['value'], r['qualifier']) for r in a['results']] == \
           [(r['analysis'], r['key'], r['value'], r['qualifier']) for r in b['results']]

def test_split_gives_the_per_analysis_cache_shape():
    coa = normalize_extraction({'metadata': {'lab': 'KCA'}, 'results': [
        {'analysis': 'cannabinoids', 'key': 'thca', 'name': 'THCa', 'value': 24.1},
        {'analysis': 'microbials', 'key': 'aflatoxin_b1', 'name': 'Aflatoxin B1', 'value': None, 'qualifier': 'ND'},
    ]})
    metadata, analyses = split_extraction(coa)
    assert metadata['lab'] == 'KCA'
    assert set(analyses) == {'cannabinoids', 'microbials'}
    assert 'analysis' not in analyses['cannabinoids'][0]

def test_attribution_records_the_model_effort_and_prompt_version():
    record = attribution('anthropic', 'claude-opus-5-5', 'high', 0.1234567, mode='batch', batch_id='msgbatch_1')
    assert record['parsing_effort'] == 'high' and record['parsing_mode'] == 'batch'
    assert record['parsing_prompt_version'] == PROMPT_VERSION and record['parsing_cost'] == 0.123457
    assert record['parsing_batch_id'] == 'msgbatch_1'

# ── Responses ─────────────────────────────────────────────────────

def _message(text, stop='end_turn', **usage):
    return {'model': 'claude-opus-5-5', 'stop_reason': stop,
            'content': [{'type': 'thinking', 'thinking': '...'}, {'type': 'text', 'text': text}],
            'usage': {'input_tokens': 10_000, 'output_tokens': 2_000, **usage}}

def test_the_answer_is_the_text_not_the_thinking():
    parsed, problem = response_json(_message('{"metadata": {}, "results": []}'))
    assert parsed == {'metadata': {}, 'results': []} and problem == ''

@pytest.mark.parametrize('stop, text, problem', [
    ('refusal', '', 'refusal'), ('max_tokens', '{"metadata": {"lab": "K', 'max_tokens'), ('end_turn', 'no json here', 'no_json'),
])
def test_an_answer_without_json_says_why(stop, text, problem):
    assert response_json(_message(text, stop=stop)) == (None, problem)

def test_usage_and_cost_count_the_cache():
    message = _message('{}', cache_read_input_tokens=3_000, cache_creation_input_tokens=0)
    usage = message_usage(message)
    assert usage == {'input': 10_000, 'output': 2_000, 'cache_write': 0, 'cache_read': 3_000}
    # Opus 5.5 in a batch: half of $4 and $20 per million; cache reads at 0.05 of input.
    expected = (10_000 * 4.0 + 3_000 * 4.0 * 0.05 + 2_000 * 20.0) / 1e6 * 0.5
    assert message_cost('claude-opus-5-5', usage, batch=True) == pytest.approx(expected)

def test_every_claude_model_is_priced_for_batches_and_the_cache():
    provider = AI_PROVIDERS['anthropic']
    assert provider['batch_discount'] == 0.5
    for name, model in provider['models'].items():
        assert model['supports_structured_output'] is True, name
        assert 0 < model['cache_read'] <= 0.1, name
