"""
Test Data COA API Endpoint | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/26/2021
Updated: 1/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
import os

# External imports:
import requests
from dotenv import load_dotenv


# Test using development server.
BASE = 'http://127.0.0.1:8000/api'

# Uncomment to test with production server.
# BASE = 'https://console.cannlytics.com/api'

# Define the endpoint.
ENDPOINT = 'data/coas'

# Load your API key.
load_dotenv('../../../.env')
API_KEY = os.getenv('CANNLYTICS_API_KEY')

# Pass your API key through the authorization header as a bearer token.
HEADERS = {
    'Authorization': 'Bearer %s' % API_KEY,
    'Content-type': 'application/json',
}


def test_api_data_coas():
    """Test the strain data API endpoints."""
    raise NotImplementedError
    # data = {}
    # url = f'{BASE}/{ENDPOINT}'
    # response = requests.get(url, data=data, headers=HEADERS)
    # assert response.status_code == 200
    # print(response.json()['data'])
