"""
Authentication Logic | Cannlytics
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/22/2021
Updated: 8/24/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Authentication mechanisms for the Cannlytics API,
specifically API request authentication and verification.
"""
# Standard imports.
import hmac
from hashlib import sha256

# Internal imports.
from ..firebase import (
    get_custom_claims,
    get_document,
    verify_session_cookie,
    verify_token,
)


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
    except:
        try:
            authorization = request.META['HTTP_AUTHORIZATION']
            key = authorization.split(' ').pop()
            try:
                claims = get_user_from_api_key(key)
            except:
                claims = verify_token(key)
        except:
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


def sha256_hmac(secret, message):
    """Create a SHA256-HMAC (hash-based message authentication code).
    Args:
        secret (str): A server-side app secret.
        message (str): The client's secret.
    Returns:
        (str): An HMAC string.
    Credit: https://stackoverflow.com/a/66958131/5021266
    """
    return hmac.new(bytes(secret, 'UTF-8'), message.encode(), sha256).hexdigest()
