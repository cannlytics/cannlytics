"""
Tests for file utilities in cannlytics.utils.utils
====================================================
Covers: get_directory_files, find_latest_file, hash_file.
"""
import time
from cannlytics.utils.utils import get_directory_files, find_latest_file, hash_file

class TestGetDirectoryFiles:

    def test_finds_pdfs(self, tmp_path):
        (tmp_path / 'a.pdf').write_text('pdf1')
        (tmp_path / 'b.pdf').write_text('pdf2')
        (tmp_path / 'c.txt').write_text('text')
        result = get_directory_files(str(tmp_path), 'pdf')
        assert len(result) == 2
        assert all(f.endswith('pdf') for f in result)

    def test_custom_extension(self, tmp_path):
        (tmp_path / 'data.csv').write_text('col1,col2')
        (tmp_path / 'data.json').write_text('{}')
        result = get_directory_files(str(tmp_path), 'csv')
        assert len(result) == 1

    def test_empty_directory(self, tmp_path):
        result = get_directory_files(str(tmp_path), 'pdf')
        assert result == []

    def test_skips_subdirectories(self, tmp_path):
        (tmp_path / 'subdir').mkdir()
        (tmp_path / 'file.pdf').write_text('data')
        result = get_directory_files(str(tmp_path), 'pdf')
        assert len(result) == 1

class TestFindLatestFile:

    def test_finds_latest(self, tmp_path):
        f1 = tmp_path / 'all-2026-01-01-00-00.xlsx'
        f1.write_text('old')
        time.sleep(0.1)
        f2 = tmp_path / 'all-2026-03-22-12-00.xlsx'
        f2.write_text('new')
        result = find_latest_file(str(tmp_path))
        assert result.endswith('all-2026-03-22-12-00.xlsx')

    def test_no_match_returns_empty(self, tmp_path):
        result = find_latest_file(str(tmp_path), slug='nonexistent')
        assert result == ''

    def test_custom_slug_and_ext(self, tmp_path):
        f = tmp_path / 'licenses-2026-01-01-00-00.csv'
        f.write_text('data')
        result = find_latest_file(str(tmp_path), slug='licenses', ext='.csv')
        assert 'licenses' in result

class TestHashFile:

    def test_produces_hex_string(self, tmp_path):
        f = tmp_path / 'test.txt'
        f.write_text('hello world')
        h = hash_file(str(f))
        assert isinstance(h, str)
        # SHA-256 hex since 1.0.0 (was SHA-1, 40 characters, before).
        assert len(h) == 64
        assert h == 'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'

    def test_legacy_sha1_still_reachable(self, tmp_path):
        f = tmp_path / 'test.txt'
        f.write_text('hello world')
        assert hash_file(str(f), algorithm='sha1') == '2aae6c35c94fcfb415dbe95f408b9ce91ee846ed'

    def test_deterministic(self, tmp_path):
        f = tmp_path / 'test.txt'
        f.write_text('same content')
        assert hash_file(str(f)) == hash_file(str(f))

    def test_different_content_differs(self, tmp_path):
        f1 = tmp_path / 'a.txt'
        f1.write_text('content A')
        f2 = tmp_path / 'b.txt'
        f2.write_text('content B')
        assert hash_file(str(f1)) != hash_file(str(f2))
