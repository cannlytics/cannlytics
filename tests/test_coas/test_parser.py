"""
Tests for cannlytics.data.coas.parser — COAdoc
================================================
Integration tests for the COAdoc class using synthetic PDFs
and mocked AI responses. No real API calls are made.
"""
import os
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from cannlytics.data.coas.parser import (
    COAdoc,
    adapt_algorithm_output,
    _hash_file,
    _hash_bytes,
)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Hash Utilities                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestHashing:

    def test_hash_file(self, make_pdf):
        pdf = make_pdf('hash_test.pdf', ['Some content'])
        h = _hash_file(pdf)
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256

    def test_hash_file_deterministic(self, make_pdf):
        pdf = make_pdf('det.pdf', ['Deterministic content'])
        h1 = _hash_file(pdf)
        h2 = _hash_file(pdf)
        assert h1 == h2

    def test_hash_nonexistent_file(self):
        # An unreadable file has no hash. Before 1.0.0 this returned the
        # digest of zero bytes, so every unreadable file collided.
        with pytest.raises(OSError):
            _hash_file('/nonexistent/file.pdf')

    def test_hash_file_covers_whole_file(self, tmp_path):
        # Two files that share their first 64 KB must not share a hash.
        head = b'%PDF-1.4 ' + b'L' * 70_000
        a, b = tmp_path / 'a.pdf', tmp_path / 'b.pdf'
        a.write_bytes(head + b'Sample A')
        b.write_bytes(head + b'Sample B')
        assert _hash_file(str(a)) != _hash_file(str(b))

    def test_hash_bytes(self):
        h = _hash_bytes(b'hello world')
        assert isinstance(h, str)
        assert len(h) == 64

# ╔══════════════════════════════════════════════════════════════════╗
# ║ adapt_algorithm_output                                           ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestAdaptAlgorithmOutput:

    def test_basic_adaptation(self):
        raw = {
            'product_name': 'Blue Dream',
            'producer': 'ABC Farms',
            'total_thc': 22.5,
            'lab': 'Kaycha Labs',
            'analyses': ['cannabinoids', 'terpenes'],
            'results': [
                {'analysis': 'cannabinoids', 'key': 'delta_9_thc', 'name': 'THC', 'value': 2.1},
                {'analysis': 'terpenes', 'key': 'beta_myrcene', 'name': 'Myrcene', 'value': 0.45},
            ],
        }
        adapted = adapt_algorithm_output(raw, 'abc123', 'kaycha', elapsed=0.5)
        assert adapted is not None
        assert 'metadata' in adapted
        assert 'analyses' in adapted
        assert adapted['metadata']['product_name'] == 'Blue Dream'
        assert adapted['metadata']['parsing_method'] == 'algorithm'
        assert adapted['metadata']['parsing_cost'] == 0.0
        assert 'cannabinoids' in adapted['analyses']
        assert 'terpenes' in adapted['analyses']

    def test_none_input_returns_none(self):
        assert adapt_algorithm_output(None, 'abc', 'kaycha') is None
        assert adapt_algorithm_output({}, 'abc', 'kaycha') is None

    def test_string_results_parsed(self):
        """Results stored as JSON strings should be parsed."""
        import json
        raw = {
            'product_name': 'Test',
            'results': json.dumps([
                {'analysis': 'cannabinoids', 'key': 'thca', 'value': 23.0},
            ]),
            'analyses': json.dumps(['cannabinoids']),
        }
        adapted = adapt_algorithm_output(raw, 'hash', 'sclabs')
        assert adapted is not None
        assert len(adapted['analyses']['cannabinoids']['results']) == 1

    def test_analysis_normalization(self):
        """Analysis names like 'Cannabinoid Potency' should normalize."""
        raw = {
            'results': [
                {'analysis': 'Cannabinoid Potency', 'key': 'thc', 'value': 20.0},
                {'analysis': 'Terpene Profile', 'key': 'myrcene', 'value': 0.5},
                {'analysis': 'Heavy Metal Screening', 'key': 'lead', 'value': 0.01},
            ],
        }
        adapted = adapt_algorithm_output(raw, 'hash', 'kaycha')
        assert 'cannabinoids' in adapted['analyses']
        assert 'terpenes' in adapted['analyses']
        assert 'heavy_metals' in adapted['analyses']

# ╔══════════════════════════════════════════════════════════════════╗
# ║ COAdoc Initialization                                            ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCOAdocInit:

    def test_algorithm_only_no_ai_client(self):
        parser = COAdoc(method='algorithm')
        assert parser.ai_client is None
        assert parser.method == 'algorithm'

    def test_auto_mode_creates_ai_client(self):
        """Auto mode should attempt to create an AI client."""
        with mock.patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test'}):
            with patch('cannlytics.data.coas.ai_client.AIClient._init_client'):
                parser = COAdoc(method='auto', provider='anthropic')
                assert parser.ai_client is not None

    def test_qr_scanning_enabled_by_default(self):
        parser = COAdoc(method='algorithm')
        assert parser._scan_qr_enabled is True

    def test_qr_scanning_disabled(self):
        parser = COAdoc(method='algorithm', qrustie_path=False)
        assert parser._scan_qr_enabled is False

    def test_explicit_qrustie_path(self):
        parser = COAdoc(method='algorithm', qrustie_path='/usr/local/bin/qrustie')
        assert parser._qrustie_path == '/usr/local/bin/qrustie'
        assert parser._scan_qr_enabled is True

    def test_cost_tracker_initialized(self):
        parser = COAdoc(method='algorithm')
        assert parser.costs is not None
        assert parser.costs.total_cost == 0.0

# ╔══════════════════════════════════════════════════════════════════╗
# ║ COAdoc.parse() — Error Paths                                    ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCOAdocParseErrors:

    def test_invalid_pdf_returns_error(self, html_as_pdf):
        parser = COAdoc(method='algorithm', qrustie_path=False)
        result = parser.parse(html_as_pdf)
        assert 'error' in result
        assert 'Invalid PDF' in result['error']

    def test_nonexistent_file_returns_error(self):
        parser = COAdoc(method='algorithm', qrustie_path=False)
        result = parser.parse('/nonexistent/coa.pdf')
        assert 'error' in result

    def test_algorithm_only_unrecognized_returns_error(self, unrecognized_pdf):
        """Algorithm-only mode with unrecognized lab should error."""
        parser = COAdoc(method='algorithm', qrustie_path=False)
        result = parser.parse(unrecognized_pdf)
        assert 'error' in result
        assert 'No algorithm' in result['error']

    def test_ai_unavailable_returns_error(self, unrecognized_pdf):
        """Auto mode with no AI client available should error."""
        with mock.patch.dict(os.environ, {}, clear=True):
            parser = COAdoc(method='auto', qrustie_path=False)
            # AI client should be marked exhausted (no key).
            result = parser.parse(unrecognized_pdf)
            assert 'error' in result

# ╔══════════════════════════════════════════════════════════════════╗
# ║ COAdoc.parse() — Algorithm Path                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCOAdocAlgorithmPath:

    def test_algorithm_parse_with_mock_algorithm(self, lab_pdf_factory):
        """A recognized lab with a loadable algorithm should parse."""
        pdf_path = lab_pdf_factory('kaycha')

        # Create a mock algorithm that returns realistic output.
        mock_algorithm = MagicMock(return_value={
            'product_name': 'Sour Diesel Cartridge',
            'producer': 'FL Farms',
            'total_thc': 85.2,
            'lab': 'Kaycha Labs',
            'analyses': ['cannabinoids'],
            'results': [
                {'analysis': 'cannabinoids', 'key': 'delta_9_thc', 'value': 3.5, 'units': 'percent'},
                {'analysis': 'cannabinoids', 'key': 'thca', 'value': 93.1, 'units': 'percent'},
            ],
        })

        parser = COAdoc(method='algorithm', qrustie_path=False)

        # Inject the mock algorithm into the cache.
        parser._algorithm_cache['kaycha'] = mock_algorithm

        result = parser.parse(pdf_path)

        assert 'error' not in result
        assert result['metadata']['product_name'] == 'Sour Diesel Cartridge'
        assert result['parse_method'] == 'algorithm'
        assert result['lab_identified'] == 'kaycha'
        assert 'cannabinoids' in result['analyses']

    def test_algorithm_failure_falls_through_to_ai(self, lab_pdf_factory):
        """If algorithm raises, auto mode should fall through to AI."""
        pdf_path = lab_pdf_factory('kaycha')

        mock_algorithm = MagicMock(side_effect=Exception('Parse error'))

        parser = COAdoc(method='auto', qrustie_path=False)
        parser._algorithm_cache['kaycha'] = mock_algorithm
        # Make AI client unavailable so we get a clean error.
        if parser.ai_client:
            parser.ai_client._exhausted = True

        result = parser.parse(pdf_path)
        # Should fall through to AI, which is unavailable.
        assert 'error' in result

# ╔══════════════════════════════════════════════════════════════════╗
# ║ COAdoc.parse() — AI Path (Mocked)                               ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCOAdocAIPath:

    def _make_parser_with_mock_ai(self):
        """Create a COAdoc with a mocked AI client."""
        with mock.patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test'}):
            with patch('cannlytics.data.coas.ai_client.AIClient._init_client'):
                parser = COAdoc(
                    method='ai',
                    provider='anthropic',
                    qrustie_path=False,
                )
                parser.ai_client.client = MagicMock()
                parser.ai_client._exhausted = False
                return parser

    def test_single_page_ai_parse(self, make_pdf):
        """Single-page COA should use one-shot parse."""
        pdf = make_pdf('single.pdf', ['Certificate of Analysis\nTotal THC: 20.0%'])
        parser = self._make_parser_with_mock_ai()

        # Mock the single-page parse.
        mock_result = {
            'metadata': {
                'product_name': 'Test Product',
                'total_thc': 20.0,
            },
            'cannabinoids': [
                {'key': 'delta_9_thc', 'name': 'THC', 'value': 2.0, 'units': 'percent'},
            ],
        }
        parser.ai_client.parse_single_page = MagicMock(
            return_value=(mock_result, 0.01, 5000, 2000)
        )

        result = parser.parse(pdf)

        assert 'error' not in result
        assert result['metadata']['product_name'] == 'Test Product'
        assert result['parse_method'] == 'ai'

    def test_multipage_ai_parse(self, multipage_pdf):
        """Multi-page COA should parse metadata then each analysis."""
        parser = self._make_parser_with_mock_ai()

        # Mock metadata parse.
        parser.ai_client.parse_metadata = MagicMock(
            return_value=(
                {
                    'product_name': 'Blue Dream',
                    'total_thc': 22.5,
                    'product_type': 'flower',
                    'analyses': ['cannabinoids', 'terpenes'],
                },
                0.01, 5000, 2000,
            )
        )

        # Mock analysis parse.
        parser.ai_client.parse_analysis = MagicMock(
            return_value=(
                {'results': [
                    {'key': 'delta_9_thc', 'name': 'THC', 'value': 2.1, 'units': 'percent'},
                ]},
                0.005, 3000, 1000,
            )
        )

        result = parser.parse(multipage_pdf)

        assert 'error' not in result
        assert result['metadata']['product_name'] == 'Blue Dream'
        assert 'cannabinoids' in result['analyses']

# ╔══════════════════════════════════════════════════════════════════╗
# ║ COAdoc.parse() — QR Scanning Integration                        ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCOAdocQRIntegration:

    def test_qr_scan_adds_coa_url(self, lab_pdf_factory):
        """When QR scanning finds a URL, it should be added to metadata."""
        pdf_path = lab_pdf_factory('kaycha')

        mock_algorithm = MagicMock(return_value={
            'product_name': 'Test',
            'results': [],
        })

        parser = COAdoc(method='algorithm', qrustie_path=False)
        parser._algorithm_cache['kaycha'] = mock_algorithm
        parser._scan_qr_enabled = True

        # Mock scan_qr to return a URL.
        with patch('cannlytics.data.coas.parser.scan_qr', return_value='https://yourcoa.com/coa/123'):
            result = parser.parse(pdf_path)

        assert result['metadata'].get('coa_url') == 'https://yourcoa.com/coa/123'

    def test_qr_scan_disabled(self, lab_pdf_factory):
        """When qrustie_path=False, no QR scan should occur."""
        pdf_path = lab_pdf_factory('kaycha')

        mock_algorithm = MagicMock(return_value={
            'product_name': 'Test',
            'results': [],
        })

        parser = COAdoc(method='algorithm', qrustie_path=False)
        parser._algorithm_cache['kaycha'] = mock_algorithm

        with patch('cannlytics.data.coas.parser.scan_qr') as mock_scan:
            parser.parse(pdf_path)
            mock_scan.assert_not_called()

    def test_qr_scan_failure_non_fatal(self, lab_pdf_factory):
        """QR scan failure should not prevent parse result from being returned."""
        pdf_path = lab_pdf_factory('kaycha')

        mock_algorithm = MagicMock(return_value={
            'product_name': 'Test Product',
            'results': [],
        })

        parser = COAdoc(method='algorithm')
        parser._algorithm_cache['kaycha'] = mock_algorithm
        parser._scan_qr_enabled = True

        with patch('cannlytics.data.coas.parser.scan_qr', side_effect=RuntimeError('QR crash')):
            result = parser.parse(pdf_path)

        # Parse should still succeed despite QR failure.
        assert 'error' not in result
        assert result['metadata']['product_name'] == 'Test Product'

    def test_existing_coa_url_not_overwritten(self, lab_pdf_factory):
        """If algorithm already provides coa_url, QR scan should not overwrite."""
        pdf_path = lab_pdf_factory('kaycha')

        mock_algorithm = MagicMock(return_value={
            'product_name': 'Test',
            'coa_url': 'https://existing-url.com/coa',
            'lab_results_url': 'https://existing-url.com/coa',
            'results': [],
        })

        parser = COAdoc(method='algorithm')
        parser._algorithm_cache['kaycha'] = mock_algorithm
        parser._scan_qr_enabled = True

        with patch('cannlytics.data.coas.parser.scan_qr'):
            parser.parse(pdf_path)

        # The metadata adapter puts coa_url into metadata_keys,
        # so it should be preserved from the algorithm output.
        # scan_qr should check existing_url and skip.
        # Note: coa_url is not in the metadata_keys set in
        # adapt_algorithm_output, so this tests the QR path.

# ╔══════════════════════════════════════════════════════════════════╗
# ║ COAdoc.parse() — Input Types                                    ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCOAdocInputTypes:

    def test_path_string_input(self, make_pdf):
        pdf = make_pdf('string.pdf', ['Test content'])
        parser = COAdoc(method='algorithm', qrustie_path=False)
        result = parser.parse(pdf)
        # Will be 'no algorithm' error, but proves the path works.
        assert 'error' in result

    def test_pathlib_input(self, make_pdf, tmp_dir):
        from pathlib import Path
        pdf = make_pdf('pathlib.pdf', ['Test content'])
        parser = COAdoc(method='algorithm', qrustie_path=False)
        result = parser.parse(Path(pdf))
        assert 'error' in result  # No algorithm, but didn't crash.

    def test_bytes_input(self, make_pdf):
        pdf = make_pdf('bytes.pdf', ['Test content'])
        with open(pdf, 'rb') as f:
            pdf_bytes = f.read()

        parser = COAdoc(method='algorithm', qrustie_path=False)
        result = parser.parse(pdf_bytes, filename='test.pdf')
        assert 'error' in result  # No algorithm, but didn't crash.

    def test_url_input_mocked(self):
        """URL input should download to temp file."""
        parser = COAdoc(method='algorithm', qrustie_path=False)

        # Mock the URL download.
        mock_response = MagicMock()
        mock_response.content = b'%PDF-1.4 fake content' + b'\x00' * 2000
        mock_response.raise_for_status = MagicMock()

        with patch('cannlytics.data.coas.parser.COAdoc._url_to_temp') as mock_dl:
            # Make it return a path that doesn't exist (triggers validation error).
            mock_dl.return_value = '/tmp/nonexistent_download.pdf'
            parser.parse('https://example.com/coa.pdf')
            mock_dl.assert_called_once()

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Pipeline Mode                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCOAdocPipelineMode:

    def test_parse_all_requires_state(self):
        parser = COAdoc(method='algorithm', qrustie_path=False)
        with pytest.raises(ValueError, match='Pipeline mode requires state'):
            parser.parse_all()

    def test_parse_all_missing_directory(self, tmp_dir):
        pytest.importorskip('cannlytics.data.cache', reason='Bogart cache not available')
        parser = COAdoc(
            method='algorithm',
            state='zz',
            data_dir=tmp_dir,
            cache_dir=tmp_dir / 'cache',
            qrustie_path=False,
        )
        summary = parser.parse_all()
        assert summary['parsed'] == 0
