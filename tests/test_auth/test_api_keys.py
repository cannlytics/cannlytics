"""
Tests for cannlytics.auth: API-key resolution and failure handling
==================================================================
Complements ``test_request_auth.py``. Firestore is mocked throughout.
"""
import hashlib
import hmac
from unittest.mock import MagicMock, patch

import pytest

from cannlytics import auth
from cannlytics.auth import authenticate_request, get_user_from_api_key, sha256_hmac

def request_with(cookie=None, session=None, header=None):
    request = MagicMock()
    request.COOKIES = {'__session': cookie} if cookie else {}
    request.session = {'__session': session} if session else {}
    request.META = {'HTTP_AUTHORIZATION': header} if header else {}
    return request

class TestApiKeyLookup:

    @patch('cannlytics.auth.auth.get_custom_claims')
    @patch('cannlytics.auth.auth.get_document')
    def test_key_is_looked_up_by_hmac_never_in_the_clear(self, get_doc, get_claims):
        get_doc.side_effect = [{'app_secret_key': 'app-secret'}, {'uid': 'u1', 'permissions': ['read']}]
        get_claims.return_value = {'plan': 'pro'}
        claims = get_user_from_api_key('the-api-key')
        code = hmac.new(b'app-secret', b'the-api-key', hashlib.sha256).hexdigest()
        assert [call.args[0] for call in get_doc.call_args_list] == ['admin/api', f'admin/api/api_key_hmacs/{code}']
        assert 'the-api-key' not in get_doc.call_args_list[1].args[0]
        assert claims == {'plan': 'pro', 'permissions': ['read'], 'uid': 'u1'}

    @patch('cannlytics.auth.auth.get_document')
    def test_unknown_key_raises(self, get_doc):
        get_doc.side_effect = [{'app_secret_key': 's'}, {}]
        with pytest.raises(KeyError):
            get_user_from_api_key('nope')

class TestAuthenticateRequest:

    @patch('cannlytics.auth.auth.verify_token')
    @patch('cannlytics.auth.auth.get_user_from_api_key')
    @patch('cannlytics.auth.auth.verify_session_cookie')
    def test_cookie_wins_over_header(self, verify_cookie, from_key, verify_token):
        verify_cookie.return_value = {'uid': 'cookie-user'}
        assert authenticate_request(request_with(cookie='c', header='Bearer k')) == {'uid': 'cookie-user'}
        verify_cookie.assert_called_once_with('c', check_revoked=True)
        from_key.assert_not_called()
        verify_token.assert_not_called()

    @patch('cannlytics.auth.auth.verify_token')
    @patch('cannlytics.auth.auth.get_user_from_api_key')
    @patch('cannlytics.auth.auth.verify_session_cookie', side_effect=ValueError('no cookie'))
    def test_api_key_is_tried_before_id_token(self, _cookie, from_key, verify_token):
        from_key.return_value = {'uid': 'key-user'}
        assert authenticate_request(request_with(header='Bearer abc123')) == {'uid': 'key-user'}
        from_key.assert_called_once_with('abc123')
        verify_token.assert_not_called()

    @patch('cannlytics.auth.auth.verify_token', side_effect=ValueError('bad token'))
    @patch('cannlytics.auth.auth.get_user_from_api_key', side_effect=KeyError('uid'))
    @patch('cannlytics.auth.auth.verify_session_cookie', side_effect=ValueError('no cookie'))
    def test_every_failure_ends_in_empty_claims_not_an_exception(self, *_):
        assert authenticate_request(request_with(header='Bearer junk')) == {}

    @patch('cannlytics.auth.auth.verify_session_cookie', side_effect=ValueError('no cookie'))
    def test_no_header_is_anonymous(self, _cookie):
        assert authenticate_request(request_with()) == {}

class TestSurface:

    def test_sha256_hmac_is_shared_with_utils(self):
        from cannlytics.utils.hashing import sha256_hmac as canonical
        assert sha256_hmac is canonical and auth.sha256_hmac is canonical

    def test_all_names_resolve(self):
        assert all(hasattr(auth, name) for name in auth.__all__)
