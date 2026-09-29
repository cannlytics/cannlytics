"""
Tests for cannlytics.firebase.firebase_auth
=============================================
Covers: user CRUD, custom claims, tokens, sessions.
All firebase_admin.auth calls are mocked.
"""
from datetime import timedelta
from unittest.mock import MagicMock, patch


from cannlytics.firebase.firebase_auth import (
    create_user,
    get_user,
    get_users,
    update_user,
    delete_user,
    generate_password_reset_link,
    create_custom_claims,
    update_custom_claims,
    get_custom_claims,
    create_custom_token,
    create_session_cookie,
    revoke_refresh_tokens,
    verify_token,
    verify_session_cookie,
)

class TestCreateUser:

    @patch('cannlytics.firebase.firebase_auth.auth')
    @patch('cannlytics.firebase.firebase_auth.create_id', return_value='ulid123')
    def test_creates_user_successfully(self, mock_id, mock_auth):
        mock_auth.create_user.return_value = MagicMock(uid='ulid123')
        user, password = create_user('Test', 'test@example.com')
        assert user is not None
        assert isinstance(password, str)
        assert len(password) == 42
        mock_auth.create_user.assert_called_once()

    @patch('cannlytics.firebase.firebase_auth.auth')
    @patch('cannlytics.firebase.firebase_auth.create_id', return_value='ulid123')
    def test_no_photo_url_and_the_email_goes_nowhere_else(self, mock_id, mock_auth):
        mock_auth.create_user.return_value = MagicMock(uid='ulid123')
        create_user('Test', 'private@example.com')
        kwargs = mock_auth.create_user.call_args.kwargs
        assert 'photo_url' not in kwargs
        assert [key for key, value in kwargs.items() if 'private@example.com' in str(value)] == ['email']

    @patch('cannlytics.firebase.firebase_auth.auth')
    @patch('cannlytics.firebase.firebase_auth.create_id', return_value='ulid123')
    def test_email_in_use_returns_none(self, mock_id, mock_auth):
        from firebase_admin.auth import EmailAlreadyExistsError
        mock_auth.create_user.side_effect = EmailAlreadyExistsError('in use', cause=None, http_response=None)
        assert create_user('Test', 'dupe@example.com') == (None, None)

    @patch('cannlytics.firebase.firebase_auth.auth')
    @patch('cannlytics.firebase.firebase_auth.create_id', return_value='ulid123')
    def test_other_failures_are_logged_without_the_address(self, mock_id, mock_auth, caplog):
        mock_auth.create_user.side_effect = ConnectionError('network down')
        assert create_user('Test', 'secret@example.com') == (None, None)
        assert 'ConnectionError' in caplog.text and 'secret@example.com' not in caplog.text

    @patch('cannlytics.firebase.firebase_auth.auth')
    @patch('cannlytics.firebase.firebase_auth.create_id', return_value='ulid123')
    def test_duplicate_email_returns_none(self, mock_id, mock_auth):
        mock_auth.create_user.side_effect = Exception('Email already exists')
        user, password = create_user('Test', 'dupe@example.com')
        assert user is None
        assert password is None

class TestGetUser:

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_get_by_uid(self, mock_auth):
        mock_auth.get_user.return_value = MagicMock(uid='abc')
        user = get_user('abc')
        assert user.uid == 'abc'

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_get_by_email(self, mock_auth):
        mock_auth.get_user.side_effect = Exception('Not found')
        mock_auth.get_user_by_email.return_value = MagicMock(email='a@b.com')
        user = get_user('a@b.com')
        assert user.email == 'a@b.com'

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_get_by_phone(self, mock_auth):
        mock_auth.get_user.side_effect = Exception('Not found')
        mock_auth.get_user_by_email.side_effect = Exception('Not found')
        mock_auth.get_user_by_phone_number.return_value = MagicMock(phone_number='+1555')
        user = get_user('+1555')
        assert user.phone_number == '+1555'

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_not_found_returns_none(self, mock_auth):
        mock_auth.get_user.side_effect = Exception()
        mock_auth.get_user_by_email.side_effect = Exception()
        mock_auth.get_user_by_phone_number.side_effect = Exception()
        assert get_user('nonexistent') is None

class TestGetUsers:

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_returns_list(self, mock_auth):
        mock_auth.list_users.return_value.iterate_all.return_value = [
            MagicMock(uid='a'), MagicMock(uid='b'),
        ]
        users = get_users()
        assert len(users) == 2

class TestUpdateUser:

    def test_updates_fields(self, mock_user):
        with patch('cannlytics.firebase.firebase_auth.auth') as mock_auth:
            mock_auth.update_user.return_value = mock_user
            update_user(mock_user, {'display_name': 'New Name'})
            mock_auth.update_user.assert_called_once()

class TestDeleteUser:

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_deletes(self, mock_auth):
        delete_user('uid123')
        mock_auth.delete_user.assert_called_once_with('uid123')

class TestPasswordResetLink:

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_generates_link(self, mock_auth):
        mock_auth.generate_password_reset_link.return_value = 'https://reset.link'
        link = generate_password_reset_link('test@example.com')
        assert link == 'https://reset.link'

class TestCustomClaims:

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_create_claims(self, mock_auth):
        create_custom_claims('uid', claims={'admin': True})
        mock_auth.set_custom_user_claims.assert_called_once_with('uid', {'admin': True})

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_create_claims_by_email(self, mock_auth):
        mock_auth.get_user_by_email.return_value = MagicMock(uid='resolved_uid')
        create_custom_claims('ignored', email='a@b.com', claims={'role': 'user'})
        mock_auth.set_custom_user_claims.assert_called_once_with('resolved_uid', {'role': 'user'})

    @patch('cannlytics.firebase.firebase_auth.get_custom_claims', return_value={'old': True})
    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_update_claims_merges(self, mock_auth, mock_get):
        result = update_custom_claims('uid', claims={'new': True})
        assert result == {'old': True, 'new': True}

    @patch('cannlytics.firebase.firebase_auth.get_user')
    def test_get_claims(self, mock_get_user):
        mock_get_user.return_value = MagicMock(custom_claims={'admin': True})
        claims = get_custom_claims('uid')
        assert claims == {'admin': True}

class TestTokensAndSessions:

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_create_custom_token(self, mock_auth):
        mock_auth.create_custom_token.return_value = b'token_bytes'
        token = create_custom_token('uid123')
        assert token == b'token_bytes'

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_create_session_cookie(self, mock_auth):
        mock_auth.create_session_cookie.return_value = b'cookie'
        cookie = create_session_cookie('id_token_abc')
        assert cookie == b'cookie'
        call_kwargs = mock_auth.create_session_cookie.call_args
        assert call_kwargs[1]['expires_in'] == timedelta(days=7)

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_verify_token(self, mock_auth):
        mock_auth.verify_id_token.return_value = {'uid': 'abc', 'email': 'a@b.com'}
        claims = verify_token('test_token')
        assert claims['uid'] == 'abc'

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_verify_session_cookie(self, mock_auth):
        mock_auth.verify_session_cookie.return_value = {'uid': 'abc'}
        claims = verify_session_cookie('session_cookie_value')
        assert claims['uid'] == 'abc'

    @patch('cannlytics.firebase.firebase_auth.auth')
    def test_revoke_refresh_tokens(self, mock_auth):
        revoke_refresh_tokens('uid123')
        mock_auth.revoke_refresh_tokens.assert_called_once_with('uid123')
