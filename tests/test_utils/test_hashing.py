"""
Tests for cannlytics.utils.hashing
==================================
The house algorithm is SHA-256 over the whole input. These tests pin
every digest to an independent ground truth (``hashlib`` called
directly, and RFC 4231 for the HMAC) so the derivations can never
drift, and they lock the three pre-1.0.0 ``pdf_hash`` variants that
the migration tooling has to reproduce.
"""
import hashlib
import hmac

import pytest

from cannlytics.utils import hashing
from cannlytics.utils.hashing import (
    EMPTY_SHA256,
    build_hash_crosswalk,
    crosswalk_key_map,
    hash_bytes,
    hash_file,
    hash_file_multi,
    hash_json,
    hash_text,
    hmac_sha256,
    identify_hash,
    legacy_file_hashes,
    sha256_hmac,
    short_hash,
)

@pytest.fixture
def big_file(tmp_path):
    """A 200 KB file: larger than one chunk and than the legacy prefix."""
    path = tmp_path / 'big.bin'
    path.write_bytes(bytes(range(256)) * 800)
    return path

class TestCanonicalHashes:

    def test_hash_bytes_matches_hashlib(self):
        assert hash_bytes(b'cannabis') == hashlib.sha256(b'cannabis').hexdigest()

    def test_hash_text_is_utf8_sha256(self):
        text = 'Δ9-THC 24.5 µg/g'
        assert hash_text(text) == hashlib.sha256(text.encode('utf-8')).hexdigest()

    def test_hash_text_does_not_normalize(self):
        assert hash_text('Blue Dream') != hash_text('blue dream')

    def test_hash_file_is_whole_file_sha256(self, big_file):
        assert hash_file(big_file) == hashlib.sha256(big_file.read_bytes()).hexdigest()

    @pytest.mark.parametrize('size', [1, 7, 4096, 65536, 10_000_000])
    def test_chunk_size_never_changes_the_digest(self, big_file, size):
        assert hash_file(big_file, size=size) == hash_file(big_file)

    def test_files_sharing_a_64kb_prefix_differ(self, tmp_path):
        head = b'%PDF-1.4 ' + b'L' * 70_000
        a, b = tmp_path / 'a.pdf', tmp_path / 'b.pdf'
        a.write_bytes(head + b'Sample A')
        b.write_bytes(head + b'Sample B')
        assert hash_file(a) != hash_file(b)

    def test_unreadable_file_raises(self, tmp_path):
        with pytest.raises(OSError):
            hash_file(tmp_path / 'missing.pdf')

    def test_empty_file_is_the_empty_digest(self, tmp_path):
        path = tmp_path / 'empty.pdf'
        path.write_bytes(b'')
        assert hash_file(path) == EMPTY_SHA256

    @pytest.mark.parametrize('size', [0, -1])
    def test_non_positive_chunk_size_raises(self, big_file, size):
        with pytest.raises(ValueError):
            hash_file(big_file, size=size)

    def test_hash_file_accepts_str_and_path(self, big_file):
        assert hash_file(str(big_file)) == hash_file(big_file)

    def test_sha1_is_reachable_for_migration(self, big_file):
        assert hash_file(big_file, algorithm='sha1') == hashlib.sha1(big_file.read_bytes()).hexdigest()

    def test_hash_file_multi_reads_once_and_agrees(self, big_file):
        digests = hash_file_multi(big_file, ('sha256', 'sha1'))
        assert digests == {
            'sha256': hash_file(big_file),
            'sha1': hash_file(big_file, algorithm='sha1'),
        }

    def test_hash_json_ignores_key_order(self):
        assert hash_json({'a': 1, 'b': None}) == hash_json({'b': None, 'a': 1})

    def test_hash_json_keeps_null_and_zero_apart(self):
        # A non-detect (null) and a measured zero are different results.
        assert hash_json({'thc': None}) != hash_json({'thc': 0})

    def test_short_hash_is_a_sha256_prefix(self):
        assert short_hash('abc') == hashlib.sha256(b'abc').hexdigest()[:16]
        assert short_hash('abc', length=8) == hashlib.sha256(b'abc').hexdigest()[:8]

    @pytest.mark.parametrize('length', [0, 65, -3])
    def test_short_hash_rejects_bad_lengths(self, length):
        with pytest.raises(ValueError):
            short_hash('abc', length=length)

class TestHmac:

    def test_rfc_4231_test_case_2(self):
        # RFC 4231 section 4.3: an independent known answer.
        assert hmac_sha256('Jefe', 'what do ya want for nothing?') == (
            '5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843'
        )

    def test_sha256_hmac_is_the_same_derivation(self):
        assert sha256_hmac('secret', 'api-key') == hmac_sha256('secret', 'api-key')

    def test_matches_the_pre_move_auth_implementation(self):
        # Issued API keys are stored under this exact derivation.
        def original(secret, message):
            return hmac.new(bytes(secret, 'UTF-8'), message.encode(), hashlib.sha256).hexdigest()
        for secret, message in [('s3cr3t', 'key-123'), ('Δ', 'µ'), ('', 'x'), ('x', '')]:
            assert sha256_hmac(secret, message) == original(secret, message)

    def test_key_and_message_are_not_interchangeable(self):
        assert hmac_sha256('a', 'b') != hmac_sha256('b', 'a')

class TestIdentifyHash:

    @pytest.mark.parametrize('value, expected', [
        (hashlib.md5(b'x').hexdigest(), 'md5'),
        (hashlib.sha1(b'x').hexdigest(), 'sha1'),
        (hashlib.sha256(b'x').hexdigest(), 'sha256'),
        (hashlib.sha512(b'x').hexdigest(), 'sha512'),
        (hashlib.sha256(b'x').hexdigest().upper(), 'sha256'),
        (hashlib.sha256(b'x').hexdigest()[:16], 'short'),
        (EMPTY_SHA256, 'empty'),
        ('not-a-hash', 'unknown'),
        ('', 'unknown'),
        (None, 'unknown'),
        (12345, 'unknown'),
    ])
    def test_identify(self, value, expected):
        assert identify_hash(value) == expected

class TestLegacyMigration:

    def test_reproduces_all_three_pre_release_variants(self, big_file):
        data = big_file.read_bytes()
        assert legacy_file_hashes(big_file) == {
            'sha256': hashlib.sha256(data).hexdigest(),
            'sha1': hashlib.sha1(data).hexdigest(),
            'sha256_prefix': hashlib.sha256(data[:65536]).hexdigest(),
        }

    def test_prefix_equals_canonical_for_small_files(self, tmp_path):
        path = tmp_path / 'small.pdf'
        path.write_bytes(b'x' * 1000)
        digests = legacy_file_hashes(path)
        assert digests['sha256_prefix'] == digests['sha256']

    def test_crosswalk_rows_and_error_rows(self, big_file, tmp_path):
        rows = build_hash_crosswalk([big_file, tmp_path / 'missing.pdf'])
        assert rows[0]['file_size'] == 204_800
        assert rows[0]['prefix_differs'] is True
        assert 'error' not in rows[0]
        assert 'FileNotFoundError' in rows[1]['error']
        assert 'sha256' not in rows[1]

    def test_key_map_points_legacy_digests_at_sha256(self, big_file):
        rows = build_hash_crosswalk([big_file])
        key_map = crosswalk_key_map(rows)
        assert key_map[rows[0]['sha1']] == rows[0]['sha256']
        assert key_map[rows[0]['sha256_prefix']] == rows[0]['sha256']

    def test_ambiguous_prefix_is_left_out_of_the_key_map(self, tmp_path):
        # Two files share a prefix hash: re-keying by it would merge them.
        head = b'L' * 70_000
        a, b = tmp_path / 'a.pdf', tmp_path / 'b.pdf'
        a.write_bytes(head + b'A')
        b.write_bytes(head + b'B')
        rows = build_hash_crosswalk([a, b])
        assert rows[0]['sha256_prefix'] == rows[1]['sha256_prefix']
        key_map = crosswalk_key_map(rows)
        assert rows[0]['sha256_prefix'] not in key_map
        assert key_map[rows[0]['sha1']] == rows[0]['sha256']
        assert key_map[rows[1]['sha1']] == rows[1]['sha256']

class TestLeafModule:

    def test_imports_only_the_standard_library(self):
        import ast
        import sys
        import pathlib
        tree = ast.parse(pathlib.Path(hashing.__file__).read_text(encoding='utf-8'))
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split('.')[0])
        assert roots <= set(sys.stdlib_module_names), roots - set(sys.stdlib_module_names)

    def test_one_definition_everywhere(self):
        from cannlytics.auth import sha256_hmac as from_auth
        from cannlytics.utils import hash_file as from_utils
        from cannlytics.utils.utils import hash_file as from_utils_module
        assert from_auth is sha256_hmac
        assert from_utils is hash_file
        assert from_utils_module is hash_file
