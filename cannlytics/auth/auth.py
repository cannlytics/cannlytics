"""
Authentication Logic | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/22/2021
Updated: 9/21/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Authentication mechanisms for the Cannlytics API, specifically API
    request authentication and verification. Requires the `firebase`
    extra. ``sha256_hmac`` lives in ``cannlytics.utils.hashing`` and is
    re-exported here, so code that only needs the hash does not need
    Firebase.
"""
# Internal imports:
from cannlytics.firebase import (
    get_custom_claims,
    get_document,
    verify_session_cookie,
    verify_token,
)
from cannlytics.utils.hashing import sha256_hmac  # noqa: F401 (re-exported)

def authenticate_request(request):
    """Verifies that the user has authenticated with a Firebase ID token
    or passed a valid API key in an `Authentication: Bearer <token>` header.
    Args:
        request: An instance of `django.http.HttpRequest` or
            `rest_framework.request.Request`.
    Returns:
        claims (dict): A dictionary of the user's custom claims, including
            the user's `uid`.
    """
    claims = {}
    try:
        session_cookie = request.COOKIES.get('__session')
        if session_cookie is None:
            session_cookie = request.session.get('__session')
        claims = verify_session_cookie(session_cookie, check_revoked=True)
    except Exception:
        try:
            authorization = request.META['HTTP_AUTHORIZATION']
            key = authorization.split(' ').pop()
            try:
                claims = get_user_from_api_key(key)
            except Exception:
                claims = verify_token(key)
        except Exception:
            pass
    return claims

def get_user_from_api_key(api_key: str) -> dict:
    """Identify a user given an API key.
    Args:
        api_key (str): An API key to identify a given user.
    Returns:
        (dict): Any user data found, with an empty dictionary if there
            is no user found.
    """
    app_secret = get_document('admin/api')['app_secret_key']
    code = sha256_hmac(app_secret, api_key)
    key_data = get_document(f'admin/api/api_key_hmacs/{code}')
    uid = key_data['uid']
    user_claims = get_custom_claims(uid)
    user_claims['permissions'] = key_data['permissions']
    user_claims['uid'] = uid
    return user_claims
