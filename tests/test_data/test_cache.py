"""
Tests for cannlytics.data.cache
=================================
Covers: Bogart set/get/expire/clear, hash_url, hash_file,
merge, to_df, read_jsonl, organize_cache.
"""
import json
import os

import pytest

from cannlytics.data.cache import Bogart, read_jsonl, organize_cache

class TestBogartBasics:

    def test_set_and_get(self, tmp_path):
        cache = Bogart(str(tmp_path / 'cache.jsonl'))
        cache.set('key1', {'value': 42})
        assert cache.get('key1') == {'value': 42}

    def test_get_missing_returns_default(self, tmp_path):
        cache = Bogart(str(tmp_path / 'cache.jsonl'))
        assert cache.get('missing') is None
        assert cache.get('missing', 'fallback') == 'fallback'

    def test_expire(self, tmp_path):
        cache = Bogart(str(tmp_path / 'cache.jsonl'))
        cache.set('key1', 'val')
        cache.expire('key1')
        assert cache.get('key1') is None

    def test_clear(self, tmp_path):
        path = str(tmp_path / 'cache.jsonl')
        cache = Bogart(path)
        cache.set('a', 1)
        cache.set('b', 2)
        cache.clear()
        assert cache.get('a') is None
        assert not os.path.exists(path)

    def test_no_duplicates(self, tmp_path):
        cache = Bogart(str(tmp_path / 'cache.jsonl'))
        cache.set('key1', 'first')
        cache.set('key1', 'second')  # Should not overwrite.
        assert cache.get('key1') == 'first'

class TestBogartPersistence:

    def test_survives_reload(self, tmp_path):
        path = str(tmp_path / 'cache.jsonl')
        c1 = Bogart(path)
        c1.set('k1', {'a': 1})
        c1.set('k2', {'b': 2})
        c2 = Bogart(path)
        assert c2.get('k1') == {'a': 1}
        assert c2.get('k2') == {'b': 2}

class TestBogartHashing:

    def test_hash_url_deterministic(self, tmp_path):
        cache = Bogart(str(tmp_path / 'cache.jsonl'))
        h1 = cache.hash_url('https://cannlytics.com')
        h2 = cache.hash_url('https://cannlytics.com')
        assert h1 == h2
        assert isinstance(h1, str)
        assert len(h1) == 64  # SHA-256 hex.

    def test_hash_url_different_urls_differ(self, tmp_path):
        cache = Bogart(str(tmp_path / 'cache.jsonl'))
        h1 = cache.hash_url('https://a.com')
        h2 = cache.hash_url('https://b.com')
        assert h1 != h2

    def test_hash_file(self, tmp_path):
        cache = Bogart(str(tmp_path / 'cache.jsonl'))
        f = tmp_path / 'data.txt'
        f.write_text('hello world')
        h = cache.hash_file(str(f))
        assert isinstance(h, str)
        assert len(h) == 64

class TestBogartMerge:

    def test_merge_combines_caches(self, tmp_path):
        p1 = str(tmp_path / 'c1.jsonl')
        p2 = str(tmp_path / 'c2.jsonl')
        c1 = Bogart(p1)
        c1.set('a', 1)
        c2 = Bogart(p2)
        c2.set('b', 2)
        c1.merge(p2)
        assert c1.get('a') == 1
        assert c1.get('b') == 2

class TestBogartToDataFrame:

    def test_to_df(self, tmp_path):
        cache = Bogart(str(tmp_path / 'cache.jsonl'))
        cache.set('k1', {'name': 'A', 'value': 1})
        cache.set('k2', {'name': 'B', 'value': 2})
        df = cache.to_df()
        assert len(df) == 2
        assert 'name' in df.columns

class TestReadJsonl:

    def test_reads_chunks(self, tmp_path):
        path = str(tmp_path / 'data.jsonl')
        with open(path, 'w') as f:
            for i in range(25):
                json.dump({f'id_{i}': {'name': f'item_{i}', 'val': i}}, f)
                f.write('\n')
        chunks = list(read_jsonl(path, ['name', 'val'], chunk_size=10))
        assert len(chunks) == 3  # 10 + 10 + 5.
        total_rows = sum(len(c) for c in chunks)
        assert total_rows == 25

class TestOrganizeCache:

    def test_sorts_and_deduplicates(self, tmp_path):
        path = str(tmp_path / 'cache.jsonl')
        with open(path, 'w') as f:
            json.dump({'z_key': {'data': 'last'}}, f); f.write('\n')
            json.dump({'a_key': {'data': 'first'}}, f); f.write('\n')
            json.dump({'a_key': {'data': 'duplicate'}}, f); f.write('\n')
        organize_cache(path)
        with open(path, 'r') as f:
            lines = f.readlines()
        assert len(lines) == 2  # Deduplicated.
        first = json.loads(lines[0])
        assert 'a_key' in first  # Sorted alphabetically.

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 1.0.0 hardening: encoding, atomic writes, bare paths, re-keying  ║
# ╚══════════════════════════════════════════════════════════════════╝

import hashlib
import json as _json

from cannlytics.data.cache import rekey_cache

def _read(path):
    with open(path, encoding='utf-8') as file:
        return file.read()

class TestCacheHardening:

    def test_non_ascii_survives_organize_then_load(self, tmp_path):
        # organize_cache writes raw UTF-8; load must read UTF-8 back, or
        # Windows decodes with the locale code page ("Δ9" -> "Î”9").
        path = str(tmp_path / 'c.jsonl')
        cache = Bogart(path)
        cache.set('k', {'analyte': 'Δ9-THC', 'units': 'µg/g'})
        organize_cache(path)
        assert 'Δ9-THC' in _read(path)
        assert Bogart(path).get('k') == {'analyte': 'Δ9-THC', 'units': 'µg/g'}

    def test_every_open_names_its_encoding(self):
        import ast
        from cannlytics.data.cache import cache as module
        tree = ast.parse(_read(module.__file__))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'open':
                mode = node.args[1].value if len(node.args) > 1 else 'r'
                if 'b' not in mode:
                    assert any(k.arg == 'encoding' for k in node.keywords), node.lineno

    def test_bare_filename_cache_path(self, tmp_path, monkeypatch):
        # os.makedirs('') raises; a cache beside the script must work.
        monkeypatch.chdir(tmp_path)
        cache = Bogart('bare.jsonl')
        cache.set('a', 1)
        cache.save()
        assert Bogart('bare.jsonl').get('a') == 1

    def test_save_is_atomic_and_leaves_no_temp_files(self, tmp_path):
        path = str(tmp_path / 'c.jsonl')
        cache = Bogart(path)
        cache.set('a', {'v': 1})
        cache.set('b', {'v': 2})
        cache.expire('a')
        assert sorted(p.name for p in tmp_path.iterdir()) == ['c.jsonl']
        assert Bogart(path).cache == {'b': {'v': 2}}

    def test_failed_save_keeps_the_old_cache(self, tmp_path):
        path = str(tmp_path / 'c.jsonl')
        cache = Bogart(path)
        cache.set('a', 1)
        # Not JSON-serialisable, and first, so an in-place rewrite would
        # truncate the file before reaching the good entry.
        cache.cache = {'bad': object(), **cache.cache}
        with pytest.raises(TypeError):
            cache.save()
        assert Bogart(path).cache == {'a': 1}
        assert sorted(p.name for p in tmp_path.iterdir()) == ['c.jsonl']

    def test_merge_skips_corrupt_lines(self, tmp_path):
        other = tmp_path / 'other.jsonl'
        other.write_text('{"x": 1}\nnot json\n\n{"y": 2}\n', encoding='utf-8')
        cache = Bogart(str(tmp_path / 'c.jsonl'))
        cache.merge(str(other))
        assert cache.cache == {'x': 1, 'y': 2}

    def test_hashes_are_whole_input_sha256(self, tmp_path):
        f = tmp_path / 'f.pdf'
        f.write_bytes(b'x' * 100_000)
        cache = Bogart(str(tmp_path / 'c.jsonl'))
        assert cache.hash_file(str(f)) == hashlib.sha256(b'x' * 100_000).hexdigest()
        assert cache.hash_url('https://cannlytics.com') == hashlib.sha256(b'https://cannlytics.com').hexdigest()

    def test_star_import_works(self):
        namespace = {}
        exec('from cannlytics.data.cache import *', namespace)
        assert 'Bogart' in namespace and 'rekey_cache' in namespace

class TestRekeyCache:

    def test_rekeys_sha1_to_sha256_and_inner_fields(self, tmp_path):
        path = str(tmp_path / 'c.jsonl')
        sha1, sha256 = 'a' * 40, 'b' * 64
        cache = Bogart(path)
        cache.set(sha1, {'pdf_hash': sha1, 'results': [{'key': 'thc', 'value': None}]})
        cache.set('c' * 64, {'pdf_hash': 'c' * 64})
        stats = rekey_cache(path, {sha1: sha256})
        assert stats == {'total': 2, 'rekeyed': 1, 'unchanged': 1, 'collisions': 0}
        reloaded = Bogart(path)
        assert reloaded.get(sha1) is None
        assert reloaded.get(sha256) == {'pdf_hash': sha256, 'results': [{'key': 'thc', 'value': None}]}

    def test_collision_keeps_the_first_entry(self, tmp_path):
        path = str(tmp_path / 'c.jsonl')
        cache = Bogart(path)
        cache.set('new', {'v': 'already-here'})
        cache.set('old', {'v': 'late'})
        stats = rekey_cache(path, {'old': 'new'})
        assert stats['collisions'] == 1
        assert Bogart(path).cache == {'new': {'v': 'already-here'}}

    def test_output_path_leaves_the_input_untouched(self, tmp_path):
        src, dst = str(tmp_path / 'src.jsonl'), str(tmp_path / 'dst.jsonl')
        Bogart(src).set('old', {'hash': 'old'})
        before = _read(src)
        rekey_cache(src, {'old': 'new'}, output_path=dst)
        assert _read(src) == before
        assert _json.loads(_read(dst)) == {'new': {'hash': 'new'}}

    def test_missing_cache_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            rekey_cache(str(tmp_path / 'nope.jsonl'), {})
