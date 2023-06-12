"""
Test Licenses API Endpoint | Cannlytics API

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 6/9/2023
Updated: 6/9/2023
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports:
import os
from urllib.parse import urljoin

# External imports:
import requests
from dotenv import load_dotenv


# API constants.
DEV = 'http://127.0.0.1:8000/api/'
BASE = 'https://api.cannlytics.com'


def test_api_get_licenses(api_key: str, base = DEV, params=None):
    """Test the API endpoint for getting licenses."""
    headers = {
        'Authorization': 'Bearer %s' % api_key,
        'Content-type': 'application/json',
    }
    url = urljoin(base, 'data/licenses')
    print('URL:', url)
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()['data']
        print('Successfully got %i observations.' % len(data))
        return data
    else:
        print('Error:', response.status_code)
        print(response.json())


# === Test ===
# Performed 2023-06-09 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':

    # Load the API key from the .env file.
    load_dotenv('../../../.env')
    api_key = os.getenv('CANNLYTICS_API_KEY')

    # [✓] TEST: Get all licenses.
    data = test_api_get_licenses(api_key, base=DEV, params=None)

    # [✓] TEST: Get licenses by state.
    data = test_api_get_licenses(api_key, base=DEV, params={'state': 'MA'})

    # [✓] TEST: Get license by license number.
    data = test_api_get_licenses(api_key, base=DEV, params={'license_number': 'C10-0000642-LIC'})

    # [✓] TEST: Get licenses by type.
    data = test_api_get_licenses(api_key, base=DEV, params={'type': 'Retail Marijuana Store'})

    # [✓] TEST: Get licenses by zip code.
    data = test_api_get_licenses(api_key, base=DEV, params={'zipcode': '92105'})

    # [✓] TEST: Get licenses by county.
    data = test_api_get_licenses(api_key, base=DEV, params={'county': 'San Diego'})

    # [✓] TEST: Get licenses by county and state.
    data = test_api_get_licenses(api_key, base=DEV, params={'county': 'San Diego', 'state': 'CA'})

    # TODO: Repeat the tests in production!