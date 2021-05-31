"""
Authentication Views | Cannlytics API
Created: 1/22/2021
Updated: 5/10/2021

Authentication mechanisms for the Cannlytics API, including API key
utility functions, request authentication and verification helpers,
and the authentication endpoints.
"""

# Standard imports
from json import loads
from secrets import token_urlsafe
from time import time

# External imports
import hmac
from hashlib import sha256
from datetime import datetime, timedelta
from django.http.response import JsonResponse
from firebase_admin import auth, exceptions, initialize_app
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

# Internal imports
from cannlytics.firebase import (
    create_log,
    delete_document,
    get_collection,
    get_custom_claims,
    get_document,
    update_document,
)

# Initialize Firebase.
try:
    initialize_app()
except ValueError:
    pass

#-----------------------------------------------------------------------
# Core Authentication Mechanism
#-----------------------------------------------------------------------

def authenticate_request(request):
    """Authenticate a user given a Firebase token or an API key
    passed in an `Authentication: Bearer <token>` header.
    Args:
        request: An instance of `django.http.HttpRequest` or
            `rest_framework.request.Request`.
    Returns:
        claims (dict): A dictionary of the user's custom claims, including
            the user's `uid`.
    """
    authorization = request.META['HTTP_AUTHORIZATION']
    token = authorization.split(' ')[-1]
    user_claims = get_user_from_api_key(token)
    if not user_claims:
        try:
            user_claims = auth.verify_id_token(token)
        except auth.InvalidIdTokenError:
            user_claims = {}
    return user_claims


def verify_session(request):
    """Verifies that the user has authenticated with a Firebase ID token.
    If the session cookie is unavailable, then force the user to login.
    Verify the session cookie. In this case an additional check is added to detect
    if the user's Firebase session was revoked, user deleted/disabled, etc.
    If the session cookie is invalid, expired or revoked, then force the user to login.
    Args:
        request: An instance of `django.http.HttpRequest` or
            `rest_framework.request.Request`.
    Returns:
        claims (dict): A dictionary of the user's custom claims, including
            the user's `uid`.
    """
    session_cookie = request.COOKIES.get('session')
    if not session_cookie:
        return {}
    try:
        return auth.verify_session_cookie(session_cookie, check_revoked=True)
    except auth.InvalidSessionCookieError:
        return {}


#-----------------------------------------------------------------------
# API Key Utilities
# FIXME: Insufficient permissions with desired design (data lives in 1 place)
# Current fix is to save key data to both the user's collection and the admin
# collection. It would be ideal to fix the Firestore security rules so
# data only needs to be stored in admin/api/api_key_hmacs
#-----------------------------------------------------------------------

def create_api_key(request, *args, **argv): #pylint: disable=unused-argument
    """Mint an API key for a user, granting programmatic use at the same
    level of permission as the uer.
    Args:
        request (HTTPRequest): A request to get the user's session.
    Returns:
        (JsonResponse): A JSON response containing the API key in an
            `api_key` field.
    """
    user_claims = verify_session(request)
    uid = user_claims['uid']
    api_key = token_urlsafe(48)
    app_secret = get_document('admin/api')['app_secret_key']
    code = sha256_hmac(app_secret, api_key)
    post_data = loads(request.body.decode('utf-8'))
    now = datetime.now()
    expiration_date = datetime.fromisoformat(post_data['expiration'])
    if expiration_date - now > timedelta(365):
        expiration_date = now + timedelta(365)
    key_data = {
        'created_at': now.isoformat(),
        'expiration_at': expiration_date.isoformat(),
        'name': post_data['name'],
        'permissions': post_data['permissions'],
        'uid': uid,
        'user_email': user_claims['email'],
        'user_name': user_claims['name'],
    }
    update_document(f'admin/api/api_key_hmacs/{code}', key_data)
    update_document(f'users/{uid}/api_key_hmacs/{code}', key_data)
    return JsonResponse({'status': 'success', 'api_key': api_key})


def delete_api_key(request, *args, **argv): #pylint: disable=unused-argument
    """Deletes a user's API key passed through an authorization header,
    e.g. `Authorization: API-key xyz`.
    Args:
        request (HTTPRequest): A request to get the user's API key.
    """
    authorization = request.META['HTTP_AUTHORIZATION']
    api_key = authorization.split(' ')[-1]
    app_secret = get_document('admin/api')['app_secret_key']
    code = sha256_hmac(app_secret, api_key)
    key_data = get_document(f'admin/api/api_key_hmacs/{code}')
    uid = key_data['uid']
    delete_document(f'admin/api/api_key_hmacs/{code}')
    delete_document(f'users/{uid}/api_key_hmacs/{code}')


def get_api_key_hmacs(request, *args, **argv): #pylint: disable=unused-argument
    """Get a user's API key HMAC information.
    Args:
        request (HTTPRequest): A request to get the user's HMAC information.
    Returns:
        (JsonResponse): A JSON response containing the API key HMAC
            information in a `data` field.
    """
    user_claims = verify_session(request)
    uid = user_claims['uid']
    query = {'key': 'uid', 'operation': '==', 'value': uid}
    docs = get_collection('admin/api/api_key_hmacs', filters=[query])
    return JsonResponse({'status': 'success', 'data': docs})


def get_user_from_api_key(api_key):
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
    user_claims = get_custom_claims(key_data['uid'])
    user_claims['permissions'] = key_data['permissions']
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
    byte_key = bytes(secret, 'UTF-8')
    payload = message.encode()
    return hmac.new(byte_key, payload, sha256).hexdigest()


#-----------------------------------------------------------------------
# API Authentication Endpoints
#-----------------------------------------------------------------------

@api_view(['GET'])
def authenticate(request):
    """Generate a session cookie for a user from an ID token sent via
    HTTP authorization bearer token."""

    # Get the user's ID token from the authorization header.
    auth_header = request.META['HTTP_AUTHORIZATION']
    id_token = auth_header.split(' ')[-1]

    # Ensure that cookies are set only on recently signed in users,
    # by checking the auth_time of the ID token before creating a cookie.
    # Only create a session if the user signed in within the last 5 minutes.
    try:
        decoded_claims = auth.verify_id_token(id_token)
        if time() - decoded_claims['auth_time'] < 5 * 60:
            # Optional: Make expiration_time_of_session a setting variable.
            expires_in = timedelta(days=7)
            expires = datetime.now() + expires_in
            session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
            response = Response({'status': 'success'}, content_type='application/json')
            response.set_cookie(
                key='session',
                value=session_cookie,
                expires=expires,
                httponly=True,
                secure=True,
            )
            uid = decoded_claims['uid']
            create_log(
                ref=f'users/{uid}/logs',
                claims=decoded_claims,
                action='Signed in.',
                log_type='auth',
                key='login'
            )
            update_document(f'users/{uid}', {'signed_in': True})
            return response

        # Otherwise, the user did not sign in recently. To guard against
        # ID token theft, re-authentication is required.
        return Response(
            {'status': 'error', 'message': 'Recent sign in required.'},
            content_type='application/json',
            status=status.HTTP_401_UNAUTHORIZED
        )
    except auth.InvalidIdTokenError:
        return Response(
            {'status': 'error', 'message': 'Invalid ID token.'},
            content_type='application/json',
            status=status.HTTP_401_UNAUTHORIZED
        )
    except exceptions.FirebaseError:
        return Response(
            {'status': 'error', 'message': 'Failed to create a session cookie.'},
            content_type='application/json',
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['GET'])
def logout(request):
    """End a user's session."""
    session_cookie = request.COOKIES.get('session')
    try:
        decoded_claims = auth.verify_session_cookie(session_cookie)
        uid = decoded_claims['uid']
        create_log(
            ref=f'users/{uid}/logs',
            claims=decoded_claims,
            action='Signed out.',
            log_type='auth',
            key='logout'
        )
        update_document(f'users/{uid}', {'signed_in': False})
        auth.revoke_refresh_tokens(decoded_claims['sub'])
        response = Response(
            {'status': 'success'},
            content_type='application/json'
        )
        response.set_cookie('session', expires=0)
        print('Successfully logged out, cookie expired.')
        return response
    except auth.InvalidSessionCookieError:
        return Response(
            {'success': 'error', 'message': 'Invalid session cookie.'},
            content_type='application/json',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
