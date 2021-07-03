"""
Authentication Views | Cannlytics API
Created: 1/22/2021
Updated: 6/21/2021

Authentication mechanisms for the Cannlytics API, including API key
utility functions, request authentication and verification helpers,
and the authentication endpoints.
"""

# Standard imports
from json import loads
from secrets import token_urlsafe

# External imports
import hmac
from hashlib import sha256
from datetime import datetime, timedelta
from django.http.response import JsonResponse

# Internal imports
from cannlytics.firebase import (
    create_custom_token,
    delete_document,
    delete_field,
    get_collection,
    get_custom_claims,
    get_document,
    get_file_url,
    initialize_firebase,
    update_document,
    upload_file,
    verify_session_cookie,
    verify_token,
)
from console.settings import 

# Initialize Firebase.
try:
    initialize_firebase()
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
    claims = {}
    try:
        authorization = request.META['HTTP_AUTHORIZATION']
        token = authorization.split(' ').pop()
        claims = verify_token(token)
    except:
        try:
            claims = get_user_from_api_key(token)
        except:
            pass
    return claims


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
    try:
        session_cookie = request.COOKIES.get('__session')
        return verify_session_cookie(session_cookie, check_revoked=True)
    except:
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
    level of permission as the user.
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
    expiration_at = post_data['expiration_at']
    try:
        expiration_at = datetime.fromisoformat(expiration_at)
    except:
        expiration_at = datetime.strptime(expiration_at, '%m/%d/%Y')
    if expiration_at - now > timedelta(365):
        expiration_at = now + timedelta(365)
    key_data = {
        'created_at': now.isoformat(),
        'expiration_at': expiration_at.isoformat(),
        'name': post_data['name'],
        'permissions': post_data['permissions'],
        'uid': uid,
        'user_email': user_claims['email'],
        'user_name': user_claims.get('name', 'No Name'),
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
    user_claims = verify_session(request)
    uid = user_claims['uid']
    post_data = loads(request.body.decode('utf-8'))

    # FIXME: Get the name of the desired key to delete.

    # Delete the key from the users API keys.

    # Remove the key HMAC by created_at time.

    # authorization = request.META['HTTP_AUTHORIZATION']
    # api_key = authorization.split(' ')[-1]
    # app_secret = get_document('admin/api')['app_secret_key']
    # code = sha256_hmac(app_secret, api_key)
    # key_data = get_document(f'admin/api/api_key_hmacs/{code}')
    # uid = key_data['uid']
    # delete_document(f'admin/api/api_key_hmacs/{code}')
    # delete_document(f'users/{uid}/api_key_hmacs/{code}')
    # return JsonResponse({'status': 'success'})
    return JsonResponse({'error': True, 'message': 'Delete API key not yet implemented, will be implemented shortly.'})


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
# User Pin Utilities
#-----------------------------------------------------------------------

def create_user_pin(request, *args, **argv): #pylint: disable=unused-argument
    """Using a pin for a given user, create and store a hash of the `pin:uid`.
    Args:
        request (HTTPRequest): A request to get the user's session.
    Returns:
        (JsonResponse): A JSON response with a success message.
    """
    user_claims = verify_session(request)
    uid = user_claims['uid']
    post_data = loads(request.body.decode('utf-8'))
    pin = post_data['pin']
    message = f'{pin}:{uid}'
    app_secret = get_document('admin/api')['app_secret_key']
    code = sha256_hmac(app_secret, message)
    post_data = loads(request.body.decode('utf-8'))
    now = datetime.now()
    # Optional: Add expiration to pins
    user_claims['hmac'] = code
    delete_user_pin(request)
    update_document(f'admin/api/pin_hmacs/{code}', user_claims)
    update_document(f'users/{uid}', {'pin_created_at': now.isoformat() })
    return JsonResponse({'success': True, 'message': 'Pin successfully created.'})


def create_signature(request, *args, **argv): #pylint: disable=unused-argument
    """Save a signature for a user, given their pin.
    Args:
        request (HTTPRequest): A request to get the user's session.
    Returns:
        (JsonResponse): A JSON response with a success message.
    """
    user_claims = verify_session(request)
    uid = user_claims['uid']
    post_data = loads(request.body.decode('utf-8'))
    # pin = post_data['pin']
    data_url = post_data['data_url']
    # message = f'{pin}:{uid}'
    # app_secret = get_document('admin/api')['app_secret_key']
    # code = sha256_hmac(app_secret, message)
    # verified_claims = get_document(f'admin/api/pin_hmacs/{code}')
    # if verified_claims.get('uid') == uid:
    ref = f'admin/auth/{uid}/user_settings/signature.png'
    upload_file(, ref, data_url=data_url)
    url = get_file_url(ref, bucket_name=None)
    update_document(f'admin/auth/{uid}/user_settings', {
        'signature_url': url,
    })
    return JsonResponse({'success': True, 'message': 'Signature saved.', 'signature_url': url})
    # else:
    #     return JsonResponse({'error': True, 'message': 'Invalid pin.'})


def delete_signature(request, *args, **argv): #pylint: disable=unused-argument
    """Delete a user's signature.
    Args:
        request (HTTPRequest): A request to get the user's session.
    Returns:
        (JsonResponse): A JSON response containing the user's claims.
    """
    user_claims = verify_session(request)
    uid = user_claims['uid']
    delete_field(f'admin/auth/{uid}/user_settings', 'signature_url')
    return JsonResponse({'success': True, 'message': 'Signature deleted.'})


def delete_user_pin(request, *args, **argv): #pylint: disable=unused-argument
    """Delete all pins for a given user, removing the data stored with their hash.
    Args:
        request (HTTPRequest): A request to get the user's session.
    Returns:
        (JsonResponse): A JSON response containing the API key in an
            `api_key` field.
    """
    user_claims = verify_session(request)
    uid = user_claims['uid']
    query = {'key': 'uid', 'operation': '==', 'value': uid}
    existing_pins = get_collection('admin/api/pin_hmacs', filters=[query])
    for pin in existing_pins:
        code = pin['hmac']
        delete_document(f'admin/api/pin_hmacs/{code}')
    delete_field(f'users/{uid}', 'pin_created_at')
    return JsonResponse({'success': True, 'message': 'User pin deleted.'})


def get_signature(request, *args, **argv): #pylint: disable=unused-argument
    """Get a user's signature given their pin, using a stored hash of the `pin:uid`.
    Args:
        request (HTTPRequest): A request to get the user's session.
    Returns:
        (JsonResponse): A JSON response containing the user's claims.
    """
    user_claims = verify_session(request)
    uid = user_claims['uid']
    post_data = loads(request.body.decode('utf-8'))
    pin = post_data['pin']
    message = f'{pin}:{uid}'
    app_secret = get_document('admin/api')['app_secret_key']
    code = sha256_hmac(app_secret, message)
    verified_claims = get_document(f'admin/api/pin_hmacs/{code}')
    if verified_claims.get('uid') == uid:
        user_settings = get_document(f'admin/auth/{uid}/user_settings')
        data_url = user_settings['signature_url']
        return JsonResponse({'success': True, 'message': 'User verified.', 'data_url': data_url})
    else:
        return JsonResponse({'error': True, 'message': 'Invalid pin.'})


def verify_user_pin(request, *args, **argv): #pylint: disable=unused-argument
    """Verify a pin for a given user, using a stored hash of the `pin:uid`.
    Args:
        request (HTTPRequest): A request to get the user's session.
    Returns:
        (JsonResponse): A JSON response containing the user's claims.
    """
    user_claims = verify_session(request)
    uid = user_claims['uid']
    post_data = loads(request.body.decode('utf-8'))
    pin = post_data['pin']
    message = f'{pin}:{uid}'
    app_secret = get_document('admin/api')['app_secret_key']
    code = sha256_hmac(app_secret, message)
    verified_claims = get_document(f'admin/api/pin_hmacs/{code}')
    if verified_claims.get('uid') == uid:
        token = create_custom_token(uid, claims={'pin_verified': True})
        return JsonResponse({'success': True, 'message': 'User verified.', 'token': token})
    else:
        return JsonResponse({'error': True, 'message': 'Invalid pin.'})
