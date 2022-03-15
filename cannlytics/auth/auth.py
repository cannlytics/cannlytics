"""
Authentication Logic | Cannlytics
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 1/22/2021
Updated: 12/21/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Authentication mechanisms for the Cannlytics API, including API key
utility functions, request authentication and verification helpers,
and the authentication endpoints.
"""
# Standard imports.
import hmac
from hashlib import sha256

# Internal imports.
from ..firebase import (
    get_custom_claims,
    get_document,
    verify_session_cookie,
)

#-----------------------------------------------------------------------
# User interface authentication
#-----------------------------------------------------------------------

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
            claims = get_user_from_api_key(key)
        except:
            claims = {}
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


# TODO: Should the following functions be implemented in the main cannlytics module?

#-----------------------------------------------------------------------
# API Keys
#-----------------------------------------------------------------------

# def create_api_key(request, *args, **argv): #pylint: disable=unused-argument
#     """Mint an API key for a user, granting programmatic use at the same
#     level of permission as the user.
#     Args:
#         request (HTTPRequest): A request to get the user's session.
#     Returns:
#         (JsonResponse): A JSON response containing the API key in an
#             `api_key` field.
#     """
#     user_claims = authenticate_request(request)
#     uid = user_claims['uid']
#     api_key = token_urlsafe(48)
#     app_secret = get_document('admin/api')['app_secret_key']
#     app_salt = get_document('admin/api')['app_salt']
#     code = sha256_hmac(app_secret, api_key + app_salt)
#     post_data = loads(request.body.decode('utf-8'))
#     now = datetime.now()
#     expiration_at = post_data['expiration_at']
#     try:
#         expiration_at = datetime.fromisoformat(expiration_at)
#     except:
#         expiration_at = datetime.strptime(expiration_at, '%m/%d/%Y')
#     if expiration_at - now > timedelta(365):
#         expiration_at = now + timedelta(365)
#     key_data = {
#         'created_at': now.isoformat(),
#         'expiration_at': expiration_at.isoformat(),
#         'name': post_data['name'],
#         'permissions': post_data['permissions'],
#         'uid': uid,
#         'user_email': user_claims['email'],
#         'user_name': user_claims.get('name', 'No Name'),
#     }
#     update_document(f'admin/api/api_key_hmacs/{code}', key_data)
#     update_document(f'users/{uid}/api_key_hmacs/{code}', key_data)
#     create_log(f'users/{uid}/logs', user_claims, 'Created API key.', 'api_key', 'api_key_create', [key_data])
#     return JsonResponse({'status': 'success', 'api_key': api_key})


# def delete_api_key(request, *args, **argv): #pylint: disable=unused-argument
#     """Deletes a user's API key passed through an authorization header,
#     e.g. `Authorization: API-key xyz`.
#     Args:
#         request (HTTPRequest): A request to get the user's API key.
#     """
#     user_claims = authenticate_request(request)
#     uid = user_claims['uid']
#     post_data = loads(request.body.decode('utf-8'))

#     # FIXME: Get the name of the desired key to delete.

#     # Delete the key from the users API keys.

#     # Remove the key HMAC by created_at time.

#     # authorization = request.META['HTTP_AUTHORIZATION']
#     # api_key = authorization.split(' ')[-1]
#     # app_secret = get_document('admin/api')['app_secret_key']
#     # code = sha256_hmac(app_secret, api_key)
#     # key_data = get_document(f'admin/api/api_key_hmacs/{code}')
#     # uid = key_data['uid']
#     # delete_document(f'admin/api/api_key_hmacs/{code}')
#     # delete_document(f'users/{uid}/api_key_hmacs/{code}')
#     # return JsonResponse({'status': 'success'})
#     create_log(f'users/{uid}/logs', user_claims, 'Deleted API key.', 'api_key', 'api_key_delete', [{'deleted_at': datetime.now().isoformat()}])
#     message = 'Delete API key not yet implemented, will be implemented shortly.'
#     return JsonResponse({'error': True, 'message': message})


# def get_api_key_hmacs(request, *args, **argv): #pylint: disable=unused-argument
#     """Get a user's API key HMAC information.
#     Args:
#         request (HTTPRequest): A request to get the user's HMAC information.
#     Returns:
#         (JsonResponse): A JSON response containing the API key HMAC
#             information in a `data` field.
#     """
#     user_claims = authenticate_request(request)
#     uid = user_claims['uid']
#     query = {'key': 'uid', 'operation': '==', 'value': uid}
#     docs = get_collection('admin/api/api_key_hmacs', filters=[query])
#     return JsonResponse({'status': 'success', 'data': docs})

#-----------------------------------------------------------------------
# User Pins
#-----------------------------------------------------------------------

# def create_user_pin(request, *args, **argv): #pylint: disable=unused-argument
#     """Using a pin for a given user, create and store a hash of the `pin:uid`.
#     Args:
#         request (HTTPRequest): A request to get the user's session.
#     Returns:
#         (JsonResponse): A JSON response with a success message.
#     """
#     user_claims = authenticate_request(request)
#     uid = user_claims['uid']
#     post_data = loads(request.body.decode('utf-8'))
#     pin = post_data['pin']
#     message = f'{pin}:{uid}'
#     app_secret = get_document('admin/api')['app_secret_key']
#     app_salt = get_document('admin/api')['app_salt']
#     code = sha256_hmac(app_secret, message + app_salt)
#     post_data = loads(request.body.decode('utf-8'))
#     now = datetime.now()
#     # Optional: Add expiration to pins
#     user_claims['hmac'] = code
#     delete_user_pin(request)
#     update_document(f'admin/api/pin_hmacs/{code}', user_claims)
#     update_document(f'users/{uid}', {'pin_created_at': now.isoformat() })
#     create_log(f'users/{uid}/logs', user_claims, 'Created pin.', 'pin', 'pin_create', [{'created_at': now}])
#     return JsonResponse({'success': True, 'message': 'Pin successfully created.'})


# def delete_user_pin(request, *args, **argv): #pylint: disable=unused-argument
#     """Delete all pins for a given user, removing the data stored with their hash.
#     Args:
#         request (HTTPRequest): A request to get the user's session.
#     Returns:
#         (JsonResponse): A JSON response containing the API key in an
#             `api_key` field.
#     """
#     user_claims = authenticate_request(request)
#     uid = user_claims['uid']
#     query = {'key': 'uid', 'operation': '==', 'value': uid}
#     existing_pins = get_collection('admin/api/pin_hmacs', filters=[query])
#     for pin in existing_pins:
#         code = pin['hmac']
#         delete_document(f'admin/api/pin_hmacs/{code}')
#     delete_field(f'users/{uid}', 'pin_created_at')
#     create_log(f'users/{uid}/logs', user_claims, 'Deleted pin.', 'pin', 'pin_delete', [{'deleted_at': datetime.now().isoformat()}])
#     return JsonResponse({'success': True, 'message': 'User pin deleted.'})


# def verify_user_pin(request, *args, **argv): #pylint: disable=unused-argument
#     """Verify a pin for a given user, using a stored hash of the `pin:uid`.
#     Args:
#         request (HTTPRequest): A request to get the user's session.
#     Returns:
#         (JsonResponse): A JSON response containing the user's claims.
#     """
#     user_claims = authenticate_request(request)
#     uid = user_claims['uid']
#     post_data = loads(request.body.decode('utf-8'))
#     pin = post_data['pin']
#     message = f'{pin}:{uid}'
#     app_secret = get_document('admin/api')['app_secret_key']
#     app_salt = get_document('admin/api')['app_salt']
#     code = sha256_hmac(app_secret, message + app_salt)
#     verified_claims = get_document(f'admin/api/pin_hmacs/{code}')
#     if verified_claims.get('uid') == uid:
#         token = create_custom_token(uid, claims={'pin_verified': True})
#         return JsonResponse({'success': True, 'message': 'User verified.', 'token': token})
#     else:
#         return JsonResponse({'error': True, 'message': 'Invalid pin.'})

#-----------------------------------------------------------------------
# Signatures
#-----------------------------------------------------------------------

# def create_signature(request, *args, **argv): #pylint: disable=unused-argument
#     """Save a signature for a user, given their pin.
#     Args:
#         request (HTTPRequest): A request to get the user's session.
#     Returns:
#         (JsonResponse): A JSON response with a success message.
#     """
#     user_claims = authenticate_request(request)
#     uid = user_claims['uid']
#     post_data = loads(request.body.decode('utf-8'))
#     data_url = post_data['data_url']
#     ref = f'admin/auth/{uid}/user_settings/signature.png'
#     upload_file(BUCKET_NAME, ref, data_url=data_url)
#     url = get_file_url(ref, bucket_name=BUCKET_NAME)
#     signature_created_at = datetime.now().isoformat()
#     signature_data = {
#         'signature_created_at': signature_created_at,
#         'signature_url': url,
#         'signature_ref': ref,
#     }
#     update_document(f'admin/auth/{uid}/user_settings', signature_data)
#     update_document(f'users/{uid}/user_settings/signature', signature_data)
#     create_log(f'users/{uid}/logs', user_claims, 'Created signature.', 'signature', 'signature_create', [{'created_at': signature_created_at}])
#     return JsonResponse({'success': True, 'message': 'Signature saved.', 'signature_url': url})


# def delete_signature(request, *args, **argv): #pylint: disable=unused-argument
#     """Delete a user's signature.
#     Args:
#         request (HTTPRequest): A request to get the user's session.
#     Returns:
#         (JsonResponse): A JSON response containing the user's claims.
#     """
#     user_claims = authenticate_request(request)
#     uid = user_claims['uid']
#     entry = {
#         'signature_created_at': '',
#         'signature_url': '',
#         'signature_ref': '',
#     }
#     delete_file(BUCKET_NAME, f'users/{uid}/user_settings/signature.png')
#     update_document(f'users/{uid}', entry)
#     update_document(f'users/{uid}/user_settings/signature', entry)
#     create_log(f'users/{uid}/logs', user_claims, 'Deleted signature.', 'signature', 'signature_delete', [{'deleted_at': datetime.now().isoformat()}])
#     return JsonResponse({'success': True, 'message': 'Signature deleted.'})


# def get_signature(request, *args, **argv): #pylint: disable=unused-argument
#     """Get a user's signature given their pin, using a stored hash of the `pin:uid`.
#     Args:
#         request (HTTPRequest): A request to get the user's session.
#     Returns:
#         (JsonResponse): A JSON response containing the user's claims.
#     """
#     user_claims = authenticate_request(request)
#     uid = user_claims['uid']
#     post_data = loads(request.body.decode('utf-8'))
#     pin = post_data['pin']
#     message = f'{pin}:{uid}'
#     app_secret = get_document('admin/api')['app_secret_key']
#     app_salt = get_document('admin/api')['app_salt']
#     code = sha256_hmac(app_secret, message + app_salt)
#     verified_claims = get_document(f'admin/api/pin_hmacs/{code}')
#     if not verified_claims:
#         return JsonResponse({'error': True, 'message': 'Invalid pin.'})
#     elif verified_claims.get('uid') == uid:
#         signature_data = get_document(f'users/{uid}/user_settings/signature')
#         return JsonResponse({
#             'success': True,
#             'message': 'User verified.',
#             'signature_url': signature_data['signature_url'],
#             'signature_created_at': signature_data['signature_created_at']
#         })
#     else:
#         return JsonResponse({'error': True, 'message': 'Invalid pin.'})
