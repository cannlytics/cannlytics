"""
Authentication | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/22/2021
Updated: 6/23/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: Authentication mechanisms for the Cannlytics API, including API key
utility functions, request authentication and verification helpers,
and the authentication endpoints.
"""
# Standard imports.
from datetime import datetime, timedelta
from json import loads
from os import environ
from secrets import token_urlsafe

# External imports.
from django.http.response import JsonResponse

# Internal imports.
from cannlytics.auth.auth import authenticate_request, sha256_hmac
from cannlytics.firebase import (
    create_log,
    delete_document,
    get_collection,
    get_document,
    initialize_firebase,
    update_document,
)

# Initialize Firebase.
try:
    initialize_firebase()
    BUCKET_NAME = environ.get('FIREBASE_STORAGE_BUCKET', None)
except ValueError:
    pass


def get_api_key_hmacs(request, *args, **argv):
    """Get a user's API key HMAC information.
    Args:
        request (HTTPRequest): A request to get the user's HMAC information.
    Returns:
        (JsonResponse): A JSON response containing the API key HMAC
            information in a `data` field.
    """
    user_claims = authenticate_request(request)
    uid = user_claims['uid']
    query = {'key': 'uid', 'operation': '==', 'value': uid}
    docs = get_collection('admin/api/api_key_hmacs', filters=[query])
    return JsonResponse({'status': 'success', 'data': docs})


def create_api_key(request, *args, **argv):
    """Mint an API key for a user, granting programmatic use at the same
    level of permission as the user.
    Args:
        request (HTTPRequest): A request to get the user's session.
    Returns:
        (JsonResponse): A JSON response containing the API key in an
            `api_key` field.
    """
    # Authenticate the user.
    try:
        user_claims = authenticate_request(request)
        uid = user_claims['uid']
    except:
        return JsonResponse({'success': False, 'message': 'Invalid credentials.'})

    # Mint an API key.
    try:
        print('Minting an API key for user:', uid)
        api_key = token_urlsafe(48)
        app_secret = get_document('admin/api')['app_secret_key']
        app_salt = get_document('admin/api')['app_salt']
        code = sha256_hmac(app_secret, api_key + app_salt)

        # Add API key parameters.
        post_data = loads(request.body.decode('utf-8'))

        # Add expiration date.
        now = datetime.now()
        expiration_at = post_data.get('expiration_at', (now + timedelta(365)).isoformat())
        try:
            expiration_at = datetime.fromisoformat(expiration_at)
        except:
            expiration_at = datetime.strptime(expiration_at, '%m/%d/%Y')
        if expiration_at - now > timedelta(365):
            expiration_at = now + timedelta(365)

        # Get the name of the desired key to create.
        key_name = post_data.get('name', api_key[:4])

        # Get the permissions for the key.
        permissions = post_data.get('permissions', ['*'])

        # Save the key data.
        key_data = {
            'code': code,
            'created_at': now.isoformat(),
            'expiration_at': expiration_at.isoformat(),
            'name': key_name,
            'permissions': permissions,
            'uid': uid,
            'user_email': user_claims['email'],
            'user_name': user_claims.get('name', 'Anonymous'),
            'prefix': api_key[:4],
            'suffix': api_key[-4:],
        }
        update_document(f'admin/api/api_key_hmacs/{code}', key_data)
        update_document(f'users/{uid}/api_key_hmacs/{code}', key_data)

        # Create a log.
        create_log(
            ref=f'users/{uid}/logs',
            claims=user_claims,
            action='Created API key.',
            log_type='api_key',
            key='create_api_key',
            changes=[key_data],
        )

        # Return the newly minted API key.
        print('Minted new API key with prefix:', api_key[:4])
        return JsonResponse({'success': True, 'api_key': api_key})
    
    # Handle unknown errors.
    except:
        print('Unknown error creating API key.')
        return JsonResponse({'success': False, 'message': 'Unknown error creating API key.'})


def delete_api_key(request, *args, **argv):
    """Deletes a user's API key passed through an authorization header,
    e.g. `Authorization: API-key xyz`.
    Args:
        request (HTTPRequest): A request to get the user's API key.
    """
    # Authenticate the user.
    user_claims = authenticate_request(request)
    try:
        uid = user_claims['uid']
    except KeyError:
        return JsonResponse({'success': False, 'message': 'Invalid credentials.'})

    # Get the prefix of the desired key to delete.
    try:
        post_data = loads(request.body.decode('utf-8'))
        prefix = post_data['prefix']
    except:
        return JsonResponse({'success': False, 'message': 'A `prefix` is expected in the request body.'})
    
    # Get the API key that belongs to the user with the given prefix.
    try:
        docs = get_collection(
            ref='admin/api/api_key_hmacs',
            filters=[
                {'key': 'prefix', 'operation': '==', 'value': prefix},
                {'key': 'uid', 'operation': '==', 'value': uid},
            ],
            limit=1,
        )
        code = docs[0]['code']
    except:
        return JsonResponse({'success': False, 'message': 'No API key found with the given prefix.'})

    # Delete the key from the users API keys.
    try:
        delete_document(f'users/{uid}/api_key_hmacs/{code}')
        delete_document(f'admin/api/api_key_hmacs/{code}')

        # Create a log.
        create_log(
            ref=f'users/{uid}/logs',
            claims=user_claims,
            action='Deleted API key.',
            log_type='api_key',
            key='delete_api_key',
            changes=[{'deleted_at': datetime.now().isoformat()}]
        )

        # Return a success message.
        message = 'API key successfully deleted.'
        return JsonResponse({'success': True, 'message': message})

    # Handle unknown errors.
    except:
        print('Unknown error deleting API key.')
        return JsonResponse({'success': False, 'message': 'Unknown error deleting API key.'})
