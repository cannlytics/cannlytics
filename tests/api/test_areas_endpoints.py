"""
API Test | Cannlytics API

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 5/7/2021
Updated: 5/7/2021
License: MIT License <https://opensource.org/licenses/MIT>

"""

import os
import environ
import pytest
import requests

import sys
sys.path.append('../../')
from cannlytics import firebase

BASE = 'http://127.0.0.1:8000/api/'
REQUESTS = [
    {
         'endpoint': 'areas',
         'method': 'get',
         'data': None,
     },
    {
         'endpoint': 'areas',
         'method': 'POST',
         'data': {},
     },
    {
         'endpoint': 'areas',
         'method': 'POST',
         'data': {},
     },
    {
         'endpoint': 'areas',
         'method': 'GET',
         'data': {},
     },
    {
         'endpoint': 'areas',
         'method': 'DELETE',
         'data': {},
     },
    {
         'endpoint': 'areas',
         'method': 'GET',
         'data': None,
     },
]

TOKEN = None

# Initialize Firebase
env = environ.Env()
env.read_env('../../.env')
credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
db = firebase.initialize_firebase()

# TODO: Test authenticate.
# if TOKEN is None:
TOKEN = firebase.create_custom_token(email='dev@cannlytics.com')
print('Authenticated user:', 'dev@cannlytics.com')
HEADERS = {
    'Authorization': 'Bearer %s'
}

r = REQUESTS[0]
url = BASE + r['endpoint']
print('Requesting:', url)
response = getattr(requests, r['method'])(url, data=r['data'], headers=HEADERS)

# @pytest.fixture
# def target_endpoints():
#     """Target endpoints."""
#     return target_endpoints


# @pytest.fixture
# def expected_result():
#     """Expected result to be returned."""
#     return [200] * len(REQUESTS)


# def test_endpoints(target_endpoints, expected_result):
#     """Request each endpoint, expecting responses with 200 status code."""
#     metadata = []
#     for r in REQUESTS:
#         url = os.path.join(BASE, r['endpoint']) 
#         response = getattr(requests, r['method'])(url, data=r['data'], headers=HEADERS)
#         metadata.append(response.status_code)
#     assert metadata == expected_result


