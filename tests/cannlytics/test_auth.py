"""
Cannlytics Auth Test | Cannlytics Engine
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/10/2021
Updated: 5/2/2022
License: MIT License <https://opensource.org/licenses/MIT>
"""

# TODO: Implement auth tests
# https://stackoverflow.com/questions/2036202/how-to-mock-users-and-requests-in-django
# https://stackoverflow.com/questions/47089299/mocking-request-and-the-response-inside-django-rest-fbv
from ...cannlytics.auth import (
    authenticate_request,
    get_user_from_api_key,
    sha256_hmac,
)


def test_authenticate_request():
    """Tests """
    raise NotImplementedError
    # request = ''
    # claims = authenticate_request(request)


def test_get_user_from_api_key():
    """Tests """
    raise NotImplementedError
    # user = get_user_from_api_key(api_key)


def test_sha256_hmac():
    """Tests """
    raise NotImplementedError
    secret = ''
    message = ''
    new_hash = sha256_hmac(secret, message)
    assert new_hash == ''


if __name__ == '__main__':

    test_authenticate_request()
    test_get_user_from_api_key()
    test_sha256_hmac()
