"""
Tests for cannlytics.ai.embeddings: providers, files, keys, vectors
===================================================================
Every provider call is mocked; no key, network, or Firestore is used.
"""
import hashlib
import hmac
import io
import json
import pathlib
import subprocess
import sys
import textwrap
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from cannlytics.ai import embeddings as module
from cannlytics.ai.embeddings import (
    aggregate_embeddings,
    cosine_similarity,
    count_pdf_pages,
    create_batch_file,
    create_embedding,
    create_embeddings,
    create_file_embedding,
    create_pdf_embedding,
    embedding_key,
    find_similar,
    format_task_prompt,
    get_embedding,
    get_embedding_provider,
    legacy_embedding_key,
    normalize_embedding,
    poll_batch_job,
    process_batch_results,
    project_embeddings,
    score_outliers,
    split_pdf_pages,
)

def openai_client(*vectors):
    client = MagicMock()
    client.embeddings.create.side_effect = lambda **kw: SimpleNamespace(
        data=[SimpleNamespace(embedding=list(vectors[i % len(vectors)])) for i in range(len(kw['input']))]
    )
    return client

def gemini_client(vector=(0.6, 0.8), per_content=True):
    client = MagicMock()
    def embed_content(model, contents, config=None):
        count = len(contents) if per_content and isinstance(contents, list) else 1
        return SimpleNamespace(embeddings=[SimpleNamespace(values=list(vector)) for _ in range(count)])
    client.models.embed_content.side_effect = embed_content
    return client

def make_pdf(pages):
    from reportlab.pdfgen import canvas
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, invariant=1)
    for number in range(1, pages + 1):
        pdf.drawString(72, 720, f'Certificate of Analysis, page {number}')
        pdf.showPage()
    pdf.save()
    return buffer.getvalue()

class TestProviderRouting:

    @pytest.mark.parametrize('model, provider', [
        ('text-embedding-3-small', 'openai'),
        ('text-embedding-3-large', 'openai'),
        ('gemini-embedding-001', 'gemini'),
        ('gemini-embedding-2', 'gemini'),
        ('models/gemini-embedding-2', 'gemini'),
        ('gemini-embedding-9-preview', 'gemini'),   # unknown, inferred
        ('text-embedding-4-huge', 'openai'),        # unknown, inferred
    ])
    def test_provider_by_model(self, model, provider):
        assert get_embedding_provider(model) == provider

    def test_unknown_family_raises(self):
        with pytest.raises(ValueError, match='Cannot infer'):
            get_embedding_provider('mystery-vectors-v1')

    def test_openai_request_shape(self):
        client = openai_client([0.1, 0.2])
        assert create_embedding('Blue\nDream', client=client) == [0.1, 0.2]
        assert client.embeddings.create.call_args.kwargs == {
            'input': ['Blue Dream'], 'model': 'text-embedding-3-large', 'dimensions': 1024,
        }

    def test_openai_ignores_task(self):
        client = openai_client([1.0])
        create_embedding('query', client=client, task='search_query')
        assert client.embeddings.create.call_args.kwargs['input'] == ['query']

    def test_gemini_2_wraps_each_text_and_prefixes_the_task(self):
        # Bare inputs would be merged into ONE vector by Gemini Embedding 2.
        client = gemini_client()
        vectors = create_embeddings(['og kush', 'sour diesel'], model='gemini-embedding-2',
                                    dimensions=768, client=client, task='clustering')
        assert vectors == [[0.6, 0.8], [0.6, 0.8]]
        call = client.models.embed_content.call_args.kwargs
        assert [c.parts[0].text for c in call['contents']] == [
            'task: clustering | query: og kush', 'task: clustering | query: sour diesel',
        ]
        assert call['config'].output_dimensionality == 768
        assert call['config'].task_type is None   # not supported by Embedding 2

    def test_gemini_001_uses_task_type_and_renormalizes_truncated(self):
        client = gemini_client(vector=(3.0, 4.0))
        vector = create_embedding('x', model='gemini-embedding-001', dimensions=768,
                                  client=client, task='similarity')
        call = client.models.embed_content.call_args.kwargs
        assert call['contents'] == ['x']
        assert call['config'].task_type == 'SEMANTIC_SIMILARITY'
        assert vector == pytest.approx([0.6, 0.8])

    def test_gemini_001_native_size_is_left_alone(self):
        client = gemini_client(vector=(3.0, 4.0))
        assert create_embedding('x', model='gemini-embedding-001', dimensions=3072, client=client) == [3.0, 4.0]

    def test_gemini_2_is_not_renormalized_by_us(self):
        client = gemini_client(vector=(3.0, 4.0))
        assert create_embedding('x', model='gemini-embedding-2', dimensions=768, client=client) == [3.0, 4.0]

    def test_blank_inputs_cost_nothing_and_keep_their_place(self):
        client = openai_client([1.0])
        assert create_embeddings(['a', '', None, '  ', 'b'], client=client) == [[1.0], [], [], [], [1.0]]
        assert client.embeddings.create.call_count == 1
        assert create_embedding('   ', client=client) == []

    def test_requests_are_chunked(self, monkeypatch):
        monkeypatch.setattr(module, 'OPENAI_MAX_INPUTS', 2)
        client = openai_client([1.0])
        assert len(create_embeddings(list('abcde'), client=client)) == 5
        assert [len(c.kwargs['input']) for c in client.embeddings.create.call_args_list] == [2, 2, 1]

    @pytest.mark.parametrize('model, dimensions', [
        ('text-embedding-3-small', 2000), ('gemini-embedding-2', 64), ('gemini-embedding-2', 4096),
    ])
    def test_impossible_dimensions_fail_before_any_request(self, model, dimensions):
        client = MagicMock()
        with pytest.raises(ValueError, match='dimensions'):
            create_embedding('x', model=model, dimensions=dimensions, client=client)
        assert not client.mock_calls

    def test_unknown_task_raises(self):
        with pytest.raises(ValueError, match='Unknown task'):
            create_embedding('x', client=MagicMock(), task='vibes')

    def test_native_dimensions_above_2048_allowed_without_firestore(self):
        client = openai_client([0.0] * 3)
        assert create_embedding('x', dimensions=3072, client=client) == [0.0] * 3

class TestTaskPrompts:

    @pytest.mark.parametrize('task, expected', [
        (None, 'kush'),
        ('search_query', 'task: search result | query: kush'),
        ('similarity', 'task: sentence similarity | query: kush'),
        ('search_document', 'title: none | text: kush'),
    ])
    def test_formats(self, task, expected):
        assert format_task_prompt('kush', task) == expected

    def test_document_title(self):
        assert format_task_prompt('body', 'search_document', title='COA') == 'title: COA | text: body'

class TestKeys:

    def test_legacy_key_is_the_original_derivation(self):
        # Verbatim pre-1.0.0: sha256_hmac(f'{text}|{model}|{dims}', '').
        def sha256_hmac(secret, message):
            return hmac.new(bytes(secret, 'UTF-8'), message.encode(), hashlib.sha256).hexdigest()
        for text, model, dims in [(' Blue Dream ', 'text-embedding-3-large', 1024), ('Δ9', 'm', None)]:
            dim_str = str(dims) if dims else 'native'
            assert legacy_embedding_key(text, model, dims) == sha256_hmac(f'{text.strip().lower()}|{model}|{dim_str}', '')

    def test_key_is_plain_sha256_and_covers_every_input(self):
        base = embedding_key('blue dream', 'text-embedding-3-large', 1024)
        assert len(base) == 64
        variants = {
            embedding_key('sour diesel', 'text-embedding-3-large', 1024),
            embedding_key('blue dream', 'gemini-embedding-2', 1024),
            embedding_key('blue dream', 'text-embedding-3-large', 768),
            embedding_key('blue dream', 'text-embedding-3-large', None),
            embedding_key('blue dream', 'text-embedding-3-large', 1024, task='clustering'),
            embedding_key('blue dream', 'text-embedding-3-large', 1024, kind='file'),
        }
        assert base not in variants and len(variants) == 6

    def test_legacy_cache_entry_still_hits(self):
        cache = {legacy_embedding_key('Blue Dream', module.DEFAULT_MODEL, 1024): {'embedding': [9.0]}}
        client = MagicMock()
        assert get_embedding('Blue Dream', cache=cache_stub(cache), client=client, use_db=False) == [9.0]
        assert not client.mock_calls

    def test_legacy_lookup_can_be_switched_off(self):
        cache = {legacy_embedding_key('Blue Dream', module.DEFAULT_MODEL, 1024): {'embedding': [9.0]}}
        client = openai_client([1.0])
        assert get_embedding('Blue Dream', cache=cache_stub(cache), client=client, use_db=False, legacy_keys=False) == [1.0]

    def test_new_entries_are_written_under_the_sha256_key(self):
        store = {}
        get_embedding(' Blue Dream ', cache=cache_stub(store), client=openai_client([1.0]), use_db=False)
        assert list(store) == [embedding_key('blue dream', module.DEFAULT_MODEL, 1024)]

    def test_task_changes_the_key_and_is_recorded(self):
        store = {}
        get_embedding('x', model='gemini-embedding-2', cache=cache_stub(store),
                      client=gemini_client(), use_db=False, task='clustering')
        [(key, record)] = store.items()
        assert key == embedding_key('x', 'gemini-embedding-2', 1024, task='clustering')
        assert record['task'] == 'clustering'

def cache_stub(store):
    cache = MagicMock()
    cache.get.side_effect = store.get
    cache.set.side_effect = store.__setitem__
    return cache

class TestFirestoreTier:

    def test_oversized_vector_is_rejected_before_any_call(self):
        client = MagicMock()
        with pytest.raises(ValueError, match='Firestore'):
            get_embedding('x', dimensions=3072, client=client, use_db=True, db=MagicMock())
        with pytest.raises(ValueError, match='Firestore'):
            get_embedding('x', model='gemini-embedding-2', dimensions=None, client=client, use_db=True, db=MagicMock())
        assert not client.mock_calls

    @patch('cannlytics.ai.embeddings.update_document')
    @patch('cannlytics.ai.embeddings.get_document')
    def test_checks_both_keys_then_writes_the_canonical_one(self, get_doc, update_doc):
        get_doc.return_value = {}
        db = MagicMock()
        get_embedding('Kush', client=openai_client([1.0]), db=db, use_db=True)
        read = [call.args[0].rsplit('/', 1)[1] for call in get_doc.call_args_list]
        assert read == [embedding_key('kush', module.DEFAULT_MODEL, 1024),
                        legacy_embedding_key('Kush', module.DEFAULT_MODEL, 1024)]
        assert update_doc.call_args.args[0].endswith(read[0])

    @patch('cannlytics.ai.embeddings.update_document')
    @patch('cannlytics.ai.embeddings.get_document')
    def test_legacy_firestore_hit_writes_no_duplicate(self, get_doc, update_doc):
        get_doc.side_effect = [{}, {'embedding': [7.0]}]
        assert get_embedding('Kush', client=MagicMock(), db=MagicMock(), use_db=True) == [7.0]
        update_doc.assert_not_called()

    def test_missing_firebase_extra_is_named(self, monkeypatch):
        import cannlytics
        # Drop the cached submodule straight from the package namespace.
        # `monkeypatch.delattr` would call `hasattr`, which runs the
        # package's lazy loader and raises outside `pytest.raises`.
        monkeypatch.delitem(vars(cannlytics), 'firebase', raising=False)
        monkeypatch.setitem(sys.modules, 'cannlytics.firebase', None)
        with pytest.raises(ImportError, match=r'cannlytics\[firebase\]'):
            get_embedding('x', client=MagicMock(), use_db=True)

class TestFileEmbeddings:

    def test_image_bytes_become_one_part(self):
        client = gemini_client(per_content=False)
        vector = create_file_embedding(b'\x89PNG...', mime_type='image/png', client=client)
        call = client.models.embed_content.call_args.kwargs
        assert vector == [0.6, 0.8]
        assert call['model'] == 'gemini-embedding-2'
        assert call['config'].output_dimensionality == 1536
        [part] = call['contents']
        assert part.inline_data.mime_type == 'image/png' and part.inline_data.data == b'\x89PNG...'

    def test_mime_type_is_inferred_from_a_path(self, tmp_path):
        path = tmp_path / 'flower.JPG'
        path.write_bytes(b'jpeg-bytes')
        client = gemini_client(per_content=False)
        create_file_embedding(path, client=client)
        assert client.models.embed_content.call_args.kwargs['contents'][0].inline_data.mime_type == 'image/jpeg'

    def test_caption_is_merged_into_the_same_request(self):
        client = gemini_client(per_content=False)
        create_file_embedding(b'x', mime_type='image/png', client=client, text='Purple Punch flower')
        contents = client.models.embed_content.call_args.kwargs['contents']
        assert contents[0] == 'Purple Punch flower' and len(contents) == 2

    def test_bytes_need_a_mime_type(self):
        with pytest.raises(ValueError, match='mime_type'):
            create_file_embedding(b'x', client=MagicMock())

    def test_unsupported_extension_is_named(self, tmp_path):
        path = tmp_path / 'results.xlsx'
        path.write_bytes(b'x')
        with pytest.raises(ValueError, match='.xlsx'):
            create_file_embedding(path, client=MagicMock())

    @pytest.mark.parametrize('model', ['text-embedding-3-large', 'gemini-embedding-001'])
    def test_text_only_models_are_refused(self, model):
        client = MagicMock()
        with pytest.raises(ValueError, match='cannot embed'):
            create_file_embedding(b'x', mime_type='image/png', model=model, dimensions=768, client=client)
        assert not client.mock_calls

    def test_pdf_over_six_pages_is_refused_with_the_remedy(self):
        client = MagicMock()
        with pytest.raises(ValueError, match='create_pdf_embedding'):
            create_file_embedding(make_pdf(7), mime_type='application/pdf', client=client)
        assert not client.mock_calls

class TestPdfEmbeddings:

    def test_split_and_count(self):
        data = make_pdf(8)
        pages = split_pdf_pages(data)
        assert count_pdf_pages(data) == 8
        assert [count_pdf_pages(page) for page in pages] == [1] * 8
        assert len(split_pdf_pages(data, max_pages=3)) == 3

    def test_long_coa_is_embedded_page_by_page_and_joined_by_pdf_hash(self, tmp_path):
        path = tmp_path / 'coa.pdf'
        path.write_bytes(make_pdf(8))
        vectors = iter([[1.0, 0.0]] * 4 + [[0.0, 1.0]] * 4)
        client = MagicMock()
        client.models.embed_content.side_effect = lambda **kw: SimpleNamespace(
            embeddings=[SimpleNamespace(values=next(vectors))])
        record = create_pdf_embedding(path, client=client)
        assert client.models.embed_content.call_count == 8
        assert record['pages'] == record['total_pages'] == 8
        assert record['pdf_hash'] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert record['embedding'] == pytest.approx([2 ** -0.5, 2 ** -0.5])   # mean, re-normalized
        assert len(record['page_embeddings']) == 8

    def test_cached_pdf_costs_nothing(self):
        data, store = make_pdf(2), {}
        first = create_pdf_embedding(data, client=gemini_client(per_content=False), cache=cache_stub(store))
        client = MagicMock()
        assert create_pdf_embedding(data, client=client, cache=cache_stub(store)) == first
        assert not client.mock_calls

    def test_leaves_nothing_on_disk(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        create_pdf_embedding(make_pdf(3), client=gemini_client(per_content=False))
        assert list(tmp_path.iterdir()) == []

class TestVectors:

    def test_normalize(self):
        assert normalize_embedding([3, 4]) == pytest.approx([0.6, 0.8])
        assert normalize_embedding([0, 0]) == [0.0, 0.0]

    def test_aggregate(self):
        assert aggregate_embeddings([[1, 0], [0, 1]]) == pytest.approx([2 ** -0.5] * 2)
        assert aggregate_embeddings([[1, 0], [0, 1]], normalize=False) == pytest.approx([0.5, 0.5])
        assert aggregate_embeddings([[1, 0], [0, 1]], weights=[3, 1], normalize=False) == pytest.approx([0.75, 0.25])
        assert aggregate_embeddings([[1, 0], [], None]) == pytest.approx([1.0, 0.0])
        assert aggregate_embeddings([]) == []
        with pytest.raises(ValueError):
            aggregate_embeddings([[1, 0], [1, 0, 0]])

    def test_cosine(self):
        assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)
        assert cosine_similarity([2, 0], [5, 0]) == pytest.approx(1.0)
        assert cosine_similarity([1, 0], [-1, 0]) == pytest.approx(-1.0)
        assert cosine_similarity([0, 0], [1, 0]) == 0.0

    def test_find_similar_ranks_by_cosine_not_length(self):
        stored = [[10, 0], [0.1, 0.1], [1, 1], [0, 0], [-1, -1]]
        ranked = find_similar([1, 1], stored, k=3)
        assert [i for i, _ in ranked] == [1, 2, 0]
        assert ranked[0][1] == pytest.approx(1.0)
        assert find_similar([1, 1], []) == []

    def test_projection_recovers_the_main_axis_and_is_deterministic(self):
        rng = np.random.default_rng(420)
        line = np.outer(rng.normal(size=200), [3.0, 4.0, 0.0]) + rng.normal(scale=0.01, size=(200, 3))
        coordinates, explained = project_embeddings(line, n_components=2)
        assert coordinates.shape == (200, 2)
        assert explained[0] > 0.999 and explained[0] >= explained[1]
        again, _ = project_embeddings(line, n_components=2)
        assert np.array_equal(coordinates, again)
        with pytest.raises(ValueError):
            project_embeddings([[1.0, 2.0]], n_components=2)

    def test_outlier_stands_out_within_its_own_lab_only(self):
        rng = np.random.default_rng(7)
        lab_a = rng.normal([1, 0, 0], 0.01, size=(30, 3))
        lab_b = rng.normal([0, 1, 0], 0.01, size=(30, 3))
        lab_a[5] = [0.2, 0.2, 1.0]                     # an R&D certificate
        vectors = np.vstack([lab_a, lab_b])
        labs = ['a'] * 30 + ['b'] * 30
        scores = score_outliers(vectors, groups=labs)
        assert scores.argmax() == 5 and scores[5] > 3.5
        # Distances are one-sided, so ordinary COAs can stray past 3.5;
        # the planted one is in another league.
        assert scores[5] > 100 * np.delete(scores, 5).max()
        # Ungrouped, two tight labs sit equally far from the shared centroid.
        assert score_outliers(vectors).argmax() == 5
        assert (score_outliers([[1, 0], [1, 0]]) == 0).all()
        assert len(score_outliers([])) == 0

class TestBatch:

    def test_batch_is_openai_only(self, tmp_path):
        with pytest.raises(ValueError, match='OpenAI models only'):
            create_batch_file(pd.DataFrame({'name': ['x']}), 'name', str(tmp_path / 'b.jsonl'),
                              model='gemini-embedding-2')

    def test_skips_texts_cached_under_either_key(self, tmp_path):
        store = {
            legacy_embedding_key('Old Name', module.DEFAULT_MODEL, 1024): {'embedding': [1.0]},
            embedding_key('new name', module.DEFAULT_MODEL, 1024): {'embedding': [1.0]},
        }
        df = pd.DataFrame({'id': ['1', '2', '3', '4'], 'name': ['Old Name', 'New Name', 'Fresh', None]})
        path = tmp_path / 'out' / 'b.jsonl'
        _, written, skipped = create_batch_file(df, 'name', str(path), cache=cache_stub(store))
        assert (written, skipped) == (1, 2)
        [request] = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
        assert request['custom_id'] == '3' and request['body']['input'] == 'Fresh'

    def test_results_are_cached_under_the_sha256_key(self, tmp_path):
        results = tmp_path / 'names-results.jsonl'
        (tmp_path / 'names-inputs.json').write_text(json.dumps({'1': 'Blue Dream'}), encoding='utf-8')
        lines = [
            {'custom_id': '1', 'response': {'status_code': 200, 'body': {'data': [{'embedding': [0.5]}]}}},
            {'custom_id': '2', 'response': {'status_code': 500, 'body': {'error': {'message': 'boom'}}}},
            {'custom_id': '3', 'response': None},
        ]
        client = MagicMock()
        body = '\n'.join(json.dumps(x) for x in lines) + '\n\n'
        client.files.content.return_value.write_to_file.side_effect = (
            lambda p: pathlib.Path(p).write_text(body, encoding='utf-8'))
        store = {}
        count = process_batch_results(client, SimpleNamespace(output_file_id='f'), str(results),
                                      cache=cache_stub(store), upload_to_firestore=False, verbose=False)
        assert count == 1
        assert list(store) == [embedding_key('blue dream', module.DEFAULT_MODEL, 1024)]

    def test_poll_gives_up_at_the_timeout(self):
        client = MagicMock()
        client.batches.retrieve.return_value = SimpleNamespace(status='in_progress')
        clock = {'now': 0.0}
        def fake_sleep(seconds):
            clock['now'] += seconds
        with patch('time.sleep', side_effect=fake_sleep) as sleep, \
                patch('time.monotonic', side_effect=lambda: clock['now']), \
                pytest.raises(TimeoutError):
            poll_batch_job(client, 'job', poll_interval=10, timeout=25, verbose=False)
        # Polls at 0 s and 10 s, then stops rather than overshoot 25 s.
        assert sleep.call_count == 2 and clock['now'] == 20

class TestImportBoundary:

    def test_imports_without_any_optional_dependency(self):
        # cannlytics.ai must import on a core install: no provider SDK,
        # no Firebase, no pypdf. Checked in a clean interpreter.
        code = textwrap.dedent('''
            import sys
            BLOCKED = ('openai', 'anthropic', 'google', 'firebase_admin', 'pypdf', 'pydantic', 'skimage')
            class Blocker:
                def find_spec(self, fullname, path=None, target=None):
                    if fullname.split('.')[0] in BLOCKED:
                        raise ImportError(f"No module named {fullname!r} (blocked)")
            sys.meta_path.insert(0, Blocker())
            import cannlytics.ai as ai
            assert ai.embedding_key('x', 'm', 8)
            assert ai.normalize_embedding([3, 4]) == [0.6, 0.8]
            loaded = sorted(m for m in sys.modules if m.split('.')[0] in BLOCKED)
            assert not loaded, loaded
            for call, extra in [(lambda: ai.create_embedding('x'), 'ai'),
                                (lambda: ai.get_embedding('x', client=object()), 'firebase')]:
                try:
                    call()
                except ImportError as error:
                    assert f'cannlytics[{extra}]' in str(error), error
                else:
                    raise AssertionError('expected ImportError')
            print('ok')
        ''')
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=120)
        assert result.stdout.strip() == 'ok', result.stderr[-1500:]

class TestClientsAndBatchPipeline:

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match='Unknown embedding provider'):
            module.create_embedding_client('cohere')

    def test_explicit_key_reaches_the_sdk(self):
        pytest.importorskip('openai')
        with patch('openai.OpenAI') as sdk:
            module.create_embedding_client('openai', api_key='sk-test')
        sdk.assert_called_once_with(api_key='sk-test')

    def test_without_a_key_the_sdk_reads_the_environment(self):
        pytest.importorskip('google.genai')
        with patch('google.genai.Client') as sdk:
            module.create_embedding_client('gemini')
        sdk.assert_called_once_with()

    def test_submit_batch_job_uploads_then_creates_and_closes_the_file(self, tmp_path):
        path = tmp_path / 'batch.jsonl'
        path.write_text('{}\n', encoding='utf-8')
        client = MagicMock()
        client.files.create.return_value = SimpleNamespace(id='file-1')
        client.batches.create.return_value = SimpleNamespace(id='batch-1', status='validating')
        job = module.submit_batch_job(client, str(path), verbose=False)
        assert job.id == 'batch-1'
        uploaded = client.files.create.call_args.kwargs
        assert uploaded['purpose'] == 'batch' and uploaded['file'].closed
        created = client.batches.create.call_args.kwargs
        assert created['input_file_id'] == 'file-1' and created['endpoint'] == '/v1/embeddings'
        assert created['completion_window'] == '24h'

    def test_pipeline_makes_no_request_when_everything_is_cached(self, tmp_path):
        store = {embedding_key('blue dream', module.DEFAULT_MODEL, 1024): {'embedding': [1.0]}}
        client = MagicMock()
        count = module.create_embeddings_batch(
            pd.DataFrame({'id': ['1'], 'name': ['Blue Dream']}), 'name', str(tmp_path),
            cache=cache_stub(store), client=client, upload_to_firestore=False, verbose=False)
        assert count == 1 and not client.mock_calls

    def test_pipeline_end_to_end(self, tmp_path):
        client = MagicMock()
        client.files.create.return_value = SimpleNamespace(id='file-1')
        client.batches.create.return_value = SimpleNamespace(id='batch-1', status='validating')
        client.batches.retrieve.return_value = SimpleNamespace(status='completed', output_file_id='out-1')
        line = {'custom_id': '7', 'response': {'status_code': 200, 'body': {'data': [{'embedding': [0.25]}]}}}
        client.files.content.return_value.write_to_file.side_effect = (
            lambda p: pathlib.Path(p).write_text(json.dumps(line) + '\n', encoding='utf-8'))
        store = {}
        count = module.create_embeddings_batch(
            pd.DataFrame({'id': ['7'], 'name': ['Sour Diesel']}), 'name', str(tmp_path),
            cache=cache_stub(store), client=client, upload_to_firestore=False, verbose=False)
        assert count == 1
        assert store[embedding_key('sour diesel', module.DEFAULT_MODEL, 1024)]['embedding'] == [0.25]

    def test_pipeline_is_openai_only(self, tmp_path):
        with pytest.raises(ValueError, match='OpenAI models only'):
            module.create_embeddings_batch(pd.DataFrame({'name': ['x']}), 'name', str(tmp_path),
                                           model='gemini-embedding-2', client=MagicMock())
