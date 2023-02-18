"""
Cannlytics Authentication Tests
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/10/2021
Updated: 1/10/2023
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports:
import os
import sys

# External imports:
from django.http import HttpRequest
from dotenv import load_dotenv

# Internal imports:
sys.path.append('../..')
from cannlytics.auth import (
    authenticate_request,
    get_user_from_api_key,
    sha256_hmac,
)


def test_authenticate_request(request):
    """Test the authentication of a request."""
    claims = authenticate_request(request)
    assert claims is not None


def test_get_user_from_api_key(api_key):
    """Test identify a user given an API key."""
    user = get_user_from_api_key(api_key)
    assert user is not None


def test_sha256_hmac(secret, message):
    """Test the creation of a SHA256 HMAC."""
    new_hash = sha256_hmac(secret, message)
    assert new_hash == ''


if __name__ == '__main__':

    # Test using development server.
    BASE = 'http://127.0.0.1:8000/api'

    # Uncomment to test with production server.
    # BASE = 'https://console.cannlytics.com/api'

    # Load your API key.
    load_dotenv('../../.env')
    API_KEY = os.getenv('CANNLYTICS_API_KEY')

    # Pass your API key through the authorization header as a bearer token.
    HEADERS = {
        'Authorization': 'Bearer %s' % API_KEY,
        'Content-type': 'application/json',
    }

    # Authenticate a test user.
    request = HttpRequest()
    request.method = 'GET'
    request.headers = HEADERS
    request.META['SERVER_NAME'] = 'localhost'

    # Test authenticating a test user.
    test_sha256_hmac(API_KEY, 'cannlytics.eth')
    test_get_user_from_api_key(API_KEY)
    test_authenticate_request(request)
