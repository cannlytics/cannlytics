"""
Test Data API Endpoint | Cannlytics API

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 5/26/2021
Updated: 5/27/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
import os
import requests
from dotenv import load_dotenv


# Test using development server.
# Uncomment to test with production server.
# BASE = 'https://cannlytics.com/api'
BASE = 'http://127.0.0.1:8000/api'

# Define the endpoint.
ENDPOINT = 'data'

# Load your API key.
load_dotenv('../../../.env')
API_KEY = os.getenv('CANNLYTICS_API_KEY')

# Pass your API key through the authorization header as a bearer token.
HEADERS = {
    'Authorization': 'Bearer %s' % API_KEY,
    'Content-type': 'application/json',
}


def test_api_strain_data():
    """Test the strain data API endpoints."""

    # Get strain data.
    params = {}
    url = f'{BASE}/{ENDPOINT}/strains'
    response = requests.get(url, params=params, headers=HEADERS)
    assert response.status_code == 200
    print(response.json()['data'])

    # Posts effects, aromas and/or
    # lab results observed for a given strain.
    data = {}
    url = f'{BASE}/{ENDPOINT}/strains'
    response = requests.get(url, data=data, headers=HEADERS)
    assert response.status_code == 200
    print(response.json()['data'])


def test_api_patent_data():
    """Test the patent data API endpoints."""

    # Get all plant patents.
    params = {}
    url = f'{BASE}/{ENDPOINT}/patents'
    response = requests.get(url, params=params, headers=HEADERS)
    assert response.status_code == 200
    print(response.json()['data'])

    # Get a specific patent.
    patent_number = ''
    url = f'{BASE}/{ENDPOINT}/patents/{patent_number}'
    response = requests.get(url, headers=HEADERS)
    data = response.json()['data']
    assert data['patent_number'] == patent_number
    print()


def test_api_states_data():
    """Test the states data API endpoints."""
    url = f'{BASE}/{ENDPOINT}/states'
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()['data']
    assert len(data) > 0


# TODO: Test lab data endpoints.

# url = f'{BASE}/{ENDPOINT}/labs'
# response = requests.get(url)
# assert response.status_code == 200
# data = response.json()['data']
# assert len(data) > 0


# Future work: Test the compound data API endpoints.


# Future work: Test analysis data endpoints.


# Future work: Test regulation data endpoints.
