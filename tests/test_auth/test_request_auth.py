"""
Tests for cannlytics.auth.auth
================================
Covers: authenticate_request (session cookie, Bearer token, API key),
get_user_from_api_key, sha256_hmac.
"""
from unittest.mock import MagicMock, patch

import pytest

from cannlytics.auth.auth import (
    authenticate_request,
    get_user_from_api_key,
    sha256_hmac,
)

class TestSha256Hmac:

    def test_produces_hex_string(self):
        result = sha256_hmac('secret', 'message')
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex digest.

    def test_deterministic(self):
        a = sha256_hmac('key', 'data')
        b = sha256_hmac('key', 'data')
        assert a == b

    def test_different_keys_differ(self):
        a = sha256_hmac('key1', 'data')
        b = sha256_hmac('key2', 'data')
        assert a != b

    def test_different_messages_differ(self):
        a = sha256_hmac('key', 'msg1')
        b = sha256_hmac('key', 'msg2')
        assert a != b

class TestAuthenticateRequest:

    def test_session_cookie_auth(self):
        mock_request = MagicMock()
        mock_request.COOKIES.get.return_value = 'valid_cookie'
        with patch('cannlytics.auth.auth.verify_session_cookie') as mock_verify:
            mock_verify.return_value = {'uid': 'user1', 'email': 'a@b.com'}
            claims = authenticate_request(mock_request)
            assert claims['uid'] == 'user1'

    def test_bearer_token_auth(self):
        mock_request = MagicMock()
        mock_request.COOKIES.get.return_value = None
        mock_request.session.get.return_value = None
        mock_request.META = {'HTTP_AUTHORIZATION': 'Bearer test_token'}
        with patch('cannlytics.auth.auth.verify_session_cookie', side_effect=Exception):
            with patch('cannlytics.auth.auth.verify_token') as mock_verify:
                mock_verify.return_value = {'uid': 'user2'}
                claims = authenticate_request(mock_request)
                assert claims['uid'] == 'user2'

    def test_api_key_auth(self):
        mock_request = MagicMock()
        mock_request.COOKIES.get.return_value = None
        mock_request.session.get.return_value = None
        mock_request.META = {'HTTP_AUTHORIZATION': 'Bearer api_key_value'}
        with patch('cannlytics.auth.auth.verify_session_cookie', side_effect=Exception):
            with patch('cannlytics.auth.auth.get_user_from_api_key') as mock_api:
                mock_api.return_value = {'uid': 'api_user', 'permissions': {}}
                claims = authenticate_request(mock_request)
                assert claims['uid'] == 'api_user'

    def test_no_credentials_returns_empty(self):
        mock_request = MagicMock()
        mock_request.COOKIES.get.return_value = None
        mock_request.session.get.return_value = None
        mock_request.META = {}
        with patch('cannlytics.auth.auth.verify_session_cookie', side_effect=Exception):
            claims = authenticate_request(mock_request)
            assert claims == {}

    def test_session_from_django_session(self):
        mock_request = MagicMock()
        mock_request.COOKIES.get.return_value = None
        mock_request.session.get.return_value = 'session_cookie_val'
        with patch('cannlytics.auth.auth.verify_session_cookie') as mock_verify:
            mock_verify.return_value = {'uid': 'sess_user'}
            claims = authenticate_request(mock_request)
            assert claims['uid'] == 'sess_user'

class TestGetUserFromApiKey:

    @patch('cannlytics.auth.auth.get_custom_claims')
    @patch('cannlytics.auth.auth.get_document')
    def test_resolves_user(self, mock_get_doc, mock_get_claims):
        mock_get_doc.side_effect = [
            {'app_secret_key': 'server_secret'},
            {'uid': 'user_abc', 'permissions': {'read': True}},
        ]
        mock_get_claims.return_value = {'admin': False}
        result = get_user_from_api_key('client_api_key')
        assert result['uid'] == 'user_abc'
        assert result['permissions'] == {'read': True}
