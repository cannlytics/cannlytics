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
