"""
Tests for cannlytics.data.coas.pdf_utils
==========================================
Covers: is_valid_pdf, InvalidPDFCache, extract_json,
make_schema_strict, encode_image, get_pdf_info,
get_pdf_pages_as_images, extract_pdf_text.
"""
import json
import os
import tempfile

import pytest

from cannlytics.data.coas.pdf_utils import (
    is_valid_pdf,
    InvalidPDFCache,
    extract_json,
    make_schema_strict,
    encode_image,
    metadata_json_hint,
    analysis_json_hint,
    get_pdf_info,
    get_pdf_pages_as_images,
    extract_pdf_text,
    long_path,
    safe_file_size,
)


# ╔══════════════════════════════════════════════════════════════════╗
# ║ PDF Validation                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestIsValidPdf:

    def test_valid_pdf(self, make_pdf):
        pdf = make_pdf('valid.pdf', ['This is a valid COA page.'])
        valid, reason = is_valid_pdf(pdf)
        assert valid is True
        assert reason == ''

    def test_empty_file(self, empty_file):
        valid, reason = is_valid_pdf(empty_file)
        assert valid is False
        assert reason == 'empty_file'

    def test_html_as_pdf(self, html_as_pdf):
        valid, reason = is_valid_pdf(html_as_pdf)
        assert valid is False
        assert reason == 'not_pdf_header'

    def test_tiny_pdf(self, tiny_pdf):
        valid, reason = is_valid_pdf(tiny_pdf)
        assert valid is False
        assert reason == 'too_small'

    def test_nonexistent_file(self):
        valid, reason = is_valid_pdf('/nonexistent/path.pdf')
        assert valid is False
        assert reason == 'unreadable'

    def test_multipage_pdf_valid(self, multipage_pdf):
        valid, reason = is_valid_pdf(multipage_pdf)
        assert valid is True


class TestInvalidPDFCache:

    def test_add_and_contains(self, tmp_dir):
        cache = InvalidPDFCache(str(tmp_dir / 'invalid.txt'))
        assert len(cache) == 0
        cache.add('hash_abc', 'corrupt')
        assert 'hash_abc' in cache
        assert len(cache) == 1

    def test_no_duplicates(self, tmp_dir):
        cache = InvalidPDFCache(str(tmp_dir / 'invalid.txt'))
        cache.add('hash_abc', 'corrupt')
        cache.add('hash_abc', 'corrupt')
        assert len(cache) == 1

    def test_remove(self, tmp_dir):
        cache = InvalidPDFCache(str(tmp_dir / 'invalid.txt'))
        cache.add('hash_abc', 'corrupt')
        cache.remove('hash_abc')
        assert 'hash_abc' not in cache
        assert len(cache) == 0

    def test_persistence(self, tmp_dir):
        """Cache survives reload from disk."""
        path = str(tmp_dir / 'invalid.txt')
        cache1 = InvalidPDFCache(path)
        cache1.add('hash_123')
        cache1.add('hash_456')

        # Reload from disk.
        cache2 = InvalidPDFCache(path)
        assert 'hash_123' in cache2
        assert 'hash_456' in cache2
        assert len(cache2) == 2


# ╔══════════════════════════════════════════════════════════════════╗
# ║ JSON Extraction                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestExtractJson:

    def test_plain_json(self):
        assert extract_json('{"key": 1}') == {'key': 1}

    def test_json_with_code_fences(self):
        text = '```json\n{"key": 2}\n```'
        assert extract_json(text) == {'key': 2}

    def test_json_embedded_in_text(self):
        text = 'Here is the result: {"key": 3} end of response.'
        assert extract_json(text) == {'key': 3}

    def test_empty_returns_none(self):
        assert extract_json('') is None
        assert extract_json(None) is None

    def test_invalid_json_returns_none(self):
        assert extract_json('not json at all') is None

    def test_nested_json(self):
        data = {'metadata': {'name': 'test'}, 'results': [1, 2, 3]}
        result = extract_json(json.dumps(data))
        assert result == data


class TestMakeSchemaStrict:

    def test_adds_additional_properties(self):
        schema = {'type': 'object', 'properties': {'a': {'type': 'string'}}}
        make_schema_strict(schema)
        assert schema['additionalProperties'] is False

    def test_adds_required(self):
        schema = {'type': 'object', 'properties': {'a': {'type': 'string'}, 'b': {'type': 'number'}}}
        make_schema_strict(schema)
        assert set(schema['required']) == {'a', 'b'}

    def test_recurses_into_nested_objects(self):
        schema = {
            'type': 'object',
            'properties': {
                'inner': {
                    'type': 'object',
                    'properties': {'x': {'type': 'string'}},
                },
            },
        }
        make_schema_strict(schema)
        assert schema['properties']['inner']['additionalProperties'] is False

    def test_recurses_into_defs(self):
        schema = {
            '$defs': {
                'Item': {
                    'type': 'object',
                    'properties': {'val': {'type': 'number'}},
                },
            },
            'type': 'object',
            'properties': {},
        }
        make_schema_strict(schema)
        assert schema['$defs']['Item']['additionalProperties'] is False


# ╔══════════════════════════════════════════════════════════════════╗
# ║ JSON Hints                                                       ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestJsonHints:

    def test_metadata_hint_is_valid_json(self):
        data = json.loads(metadata_json_hint())
        assert 'product_name' in data
        assert 'total_thc' in data
        # Totals should be null (not 0.0) to signal "not found".
        assert data['total_thc'] is None

    def test_analysis_hint_is_valid_json(self):
        data = json.loads(analysis_json_hint())
        assert 'analysis' in data
        assert 'results' in data
        assert isinstance(data['results'], list)


# ╔══════════════════════════════════════════════════════════════════╗
# ║ PDF Content Utilities                                            ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestGetPdfInfo:

    def test_basic_info(self, make_pdf):
        pdf = make_pdf('info.pdf', ['Certificate of Analysis\nCannabinoid potency results'])
        info = get_pdf_info(pdf)
        assert info['num_pages'] == 1
        assert info['has_text'] is True
        assert 'cannabinoids' in info['detected_analyses']

    def test_multipage_info(self, multipage_pdf):
        info = get_pdf_info(multipage_pdf)
        assert info['num_pages'] == 3
        assert info['has_text'] is True

    def test_nonexistent_file(self):
        info = get_pdf_info('/nonexistent.pdf')
        assert info['num_pages'] == 0


class TestGetPdfPagesAsImages:

    def test_single_page(self, make_pdf, tmp_dir):
        pdf = make_pdf('img.pdf', ['Page 1 content'])
        images = get_pdf_pages_as_images(pdf, page_indexes=[0], output_dir=str(tmp_dir))
        assert len(images) == 1
        assert os.path.exists(images[0])
        assert images[0].endswith('.jpeg')

    def test_multiple_pages(self, multipage_pdf, tmp_dir):
        images = get_pdf_pages_as_images(
            multipage_pdf, page_indexes=[0, 1, 2], output_dir=str(tmp_dir),
        )
        assert len(images) == 3

    def test_keyword_page_selection(self, multipage_pdf, tmp_dir):
        images = get_pdf_pages_as_images(
            multipage_pdf,
            page_indexes='keywords',
            keywords=['terpene'],
            output_dir=str(tmp_dir),
        )
        # Should find page 3 (terpene content).
        assert len(images) >= 1


class TestExtractPdfText:

    def test_basic_extraction(self, make_pdf):
        pdf = make_pdf('text.pdf', ['Hello world from COA'])
        text = extract_pdf_text(pdf)
        assert 'Hello world' in text

    def test_keyword_filtering(self, multipage_pdf):
        text = extract_pdf_text(multipage_pdf, keywords=['terpene'])
        assert 'Terpene' in text or 'terpene' in text.lower()

    def test_nonexistent_file(self):
        assert extract_pdf_text('/nonexistent.pdf') == ''


class TestEncodeImage:

    def test_encodes_to_base64(self, tmp_dir):
        # Create a small file.
        path = str(tmp_dir / 'test.bin')
        with open(path, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        b64 = encode_image(path)
        assert isinstance(b64, str)
        assert len(b64) > 0
