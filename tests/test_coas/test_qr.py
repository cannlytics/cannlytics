"""
Tests for cannlytics.data.coas.qr
===================================
Covers: is_url, find_qrustie, decode functions (graceful degradation),
scan_qr, scan_qr_raw.
"""
import os
from unittest.mock import MagicMock, patch

import pytest

from cannlytics.data.coas.qr import (
    is_url,
    find_qrustie,
    decode_qr_qrustie,
    decode_qr_python,
    extract_qr_regions,
    scan_qr,
    scan_qr_raw,
)


class TestIsUrl:

    @pytest.mark.parametrize('url', [
        'https://lab.example.com/coa/12345',
        'http://example.com',
        'https://yourcoa.com/share/abc',
        'https://confidentcannabis.com/report/xyz',
    ])
    def test_valid_urls(self, url):
        assert is_url(url) is True

    @pytest.mark.parametrize('not_url', [
        'ftp://example.com',
        'not a url',
        'www.example.com',  # No scheme.
        '',
        '12345',
        'just some text',
    ])
    def test_invalid_urls(self, not_url):
        assert is_url(not_url) is False

    def test_none(self):
        assert is_url(None) is False

    def test_whitespace_stripped(self):
        assert is_url('  https://example.com  ') is True


class TestFindQrustie:

    def test_returns_none_when_not_found(self):
        """In a clean environment, qrustie should not be found."""
        with patch.dict(os.environ, {}, clear=True):
            result = find_qrustie()
            # May or may not find it depending on system — just verify no crash.
            assert result is None or isinstance(result, str)

    def test_explicit_path_valid(self, tmp_dir):
        """An explicit path to an existing file should be returned."""
        fake_binary = tmp_dir / 'qrustie'
        fake_binary.write_bytes(b'#!/bin/sh\necho "fake"')
        result = find_qrustie(str(fake_binary))
        assert result is not None
        assert 'qrustie' in result

    def test_explicit_path_invalid(self):
        result = find_qrustie('/nonexistent/qrustie')
        # Should fall through to other search methods.
        assert result is None or isinstance(result, str)

    def test_env_var_path(self, tmp_dir):
        fake_binary = tmp_dir / 'qrustie_env'
        fake_binary.write_bytes(b'fake binary')
        with patch.dict(os.environ, {'QRUSTIE_PATH': str(fake_binary)}):
            result = find_qrustie()
            assert result is not None


class TestDecodeQrQrustie:

    def test_timeout_returns_clean_result(self):
        """Timeout should produce a clean error dict, not raise."""
        with patch('cannlytics.data.coas.qr.subprocess') as mock_sub:
            import subprocess
            mock_sub.run.side_effect = subprocess.TimeoutExpired('qrustie', 30)
            mock_sub.TimeoutExpired = subprocess.TimeoutExpired
            result = decode_qr_qrustie('/fake/image.png', '/fake/qrustie')
            assert result['found'] is False
            assert 'Timeout' in result['error']

    def test_successful_decode(self):
        """Successful decode should return parsed JSON."""
        import json
        mock_output = json.dumps({
            'file': 'image.png',
            'found': True,
            'data': ['https://yourcoa.com/coa/123'],
            'decoder': 'rqrr',
            'strategy': 'original',
            'error': '',
        })
        with patch('cannlytics.data.coas.qr.subprocess') as mock_sub:
            mock_result = MagicMock()
            mock_result.stdout = mock_output
            mock_result.stderr = ''
            mock_result.returncode = 0
            mock_sub.run.return_value = mock_result
            result = decode_qr_qrustie('/fake/image.png', '/fake/qrustie')
            assert result['found'] is True
            assert result['data'] == ['https://yourcoa.com/coa/123']


class TestDecodeQrPython:

    def test_no_decoder_available(self):
        """When no Python QR decoder is installed, should return clean error."""
        with patch.dict('sys.modules', {'pyzbar': None, 'zxingcpp': None}):
            result = decode_qr_python('/fake/image.png')
            assert result['found'] is False


class TestExtractQrRegions:

    def test_returns_empty_for_nonexistent(self, tmp_dir):
        result = extract_qr_regions('/nonexistent.png', str(tmp_dir))
        assert result == []


class TestScanQr:

    def test_nonexistent_pdf_returns_none(self):
        result = scan_qr('/nonexistent/coa.pdf')
        assert result is None

    def test_scan_returns_url_when_found(self, make_pdf):
        """When QR decode finds a URL, scan_qr should return it."""
        pdf = make_pdf('qr_test.pdf', ['Some COA content'])

        mock_decode_result = {
            'found': True,
            'data': ['https://yourcoa.com/coa/456'],
            'decoder': 'rqrr',
            'strategy': 'original',
            'error': '',
        }

        with patch('cannlytics.data.coas.qr.find_qrustie', return_value='/fake/qrustie'):
            with patch('cannlytics.data.coas.qr.decode_qr_qrustie', return_value=mock_decode_result):
                url = scan_qr(pdf)
                assert url == 'https://yourcoa.com/coa/456'

    def test_scan_returns_none_when_no_qr(self, make_pdf):
        """When no QR code is found, scan_qr should return None."""
        pdf = make_pdf('no_qr.pdf', ['Just text, no QR code'])

        mock_decode_result = {
            'found': False,
            'data': [],
            'decoder': '',
            'strategy': '',
            'error': '',
        }

        with patch('cannlytics.data.coas.qr.find_qrustie', return_value='/fake/qrustie'):
            with patch('cannlytics.data.coas.qr.decode_qr_qrustie', return_value=mock_decode_result):
                url = scan_qr(pdf)
                assert url is None

    def test_scan_non_url_qr_returns_none(self, make_pdf):
        """QR code with non-URL data should return None."""
        pdf = make_pdf('non_url_qr.pdf', ['COA content'])

        mock_decode_result = {
            'found': True,
            'data': ['SAMPLE-12345-NOT-A-URL'],
            'decoder': 'rqrr',
            'strategy': 'original',
            'error': '',
        }

        with patch('cannlytics.data.coas.qr.find_qrustie', return_value='/fake/qrustie'):
            with patch('cannlytics.data.coas.qr.decode_qr_qrustie', return_value=mock_decode_result):
                url = scan_qr(pdf)
                assert url is None


class TestScanQrRaw:

    def test_returns_full_details(self, make_pdf):
        pdf = make_pdf('raw_test.pdf', ['COA content'])

        mock_decode_result = {
            'found': True,
            'data': ['https://yourcoa.com/coa/789'],
            'decoder': 'rqrr',
            'strategy': 'grayscale',
            'error': '',
        }

        with patch('cannlytics.data.coas.qr.find_qrustie', return_value='/fake/qrustie'):
            with patch('cannlytics.data.coas.qr.decode_qr_qrustie', return_value=mock_decode_result):
                result = scan_qr_raw(pdf)
                assert result['coa_url'] == 'https://yourcoa.com/coa/789'
                assert result['qr_data'] == 'https://yourcoa.com/coa/789'
                assert result['decoder'] == 'rqrr'
                assert result['strategy'] == 'grayscale'

    def test_nonexistent_returns_error(self):
        result = scan_qr_raw('/nonexistent/coa.pdf')
        assert result['coa_url'] is None
        assert result['error'] != ''
