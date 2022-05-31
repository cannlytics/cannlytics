"""
Test Statistics API Endpoint | Cannlytics API

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
# BASE = 'https://console.cannlytics.com/api'
BASE = 'http://127.0.0.1:8000/api'

# Load your API key.
load_dotenv('../../../.env')
API_KEY = os.getenv('CANNLYTICS_API_KEY')

# Pass your API key through the authorization header as a bearer token.
HEADERS = {
    'Authorization': 'Bearer %s' % API_KEY,
    'Content-type': 'application/json',
}

# Define the endpoint.
ENDPOINT = 'stats'


def test_api_effects_stats():
    """Test the effects statistics endpoint."""

    # Optional: User requests effects statistics.

    # User posts lab results to get potential effects and aromas.
    data = {}
    url = f'{BASE}/{ENDPOINT}/effects'
    response = requests.post(url, json=data, headers=HEADERS)
    assert response.status_code == 200
    print('Potential effects / aromas:')
    print(response.json()['data'])


def test_api_recommendations():
    """Test the effects statistics endpoint."""

    # User requests recommendations given a
    # list of desired effects and aromas.
    # A list of strains is returned that match the desired
    # effects and aromas ranked by the number of matched effects.
    # Future work: Return statistics for the probability of reporting
    # effects and aromas.
    params = {}
    url = f'{BASE}/{ENDPOINT}/recommendations'
    response = requests.get(url, params=params, headers=HEADERS)
    assert response.status_code == 200
    print('Recommended strains:')
    print(response.json()['data'])

    # User passes link to lab results data and / or reviews
    # data to train their own model.
    data = {}
    url = f'{BASE}/{ENDPOINT}/recommendations'
    response = requests.post(url, json=data, headers=HEADERS)
    assert response.status_code == 200
    print('Recommended strains:')
    print(response.json()['data'])

    # User posts if the recommendation was useful or not.
    rec_id = ''
    data = {}
    url = f'{BASE}/{ENDPOINT}/recommendations/{rec_id}'
    response = requests.post(url, json=data, headers=HEADERS)
    assert response.status_code == 200
    print('Posted feedback:')
    print(response.json()['data'])
