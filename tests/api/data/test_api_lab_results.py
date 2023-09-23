"""
Test Lab Results API Endpoint | Cannlytics API

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 6/9/2023
Updated: 6/9/2023
License: MIT License <https://opensource.org/licenses/MIT>
"""
import os
import requests
from dotenv import load_dotenv
from urllib.parse import urljoin


# API constants.
DEV = 'http://127.0.0.1:8000/api/'
BASE = 'https://api.cannlytics.com'


def test_api_get_lab_results(api_key: str, base = DEV, params=None):
    """Test the API endpoint for getting lab results."""
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


# === Tests ===
# Performed 2023-06-09 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':

    # Load the API key from the .env file.
    load_dotenv('../../../.env')
    api_key = os.getenv('CANNLYTICS_API_KEY')

    # [ ] TEST: Get results by strain name.
    # data = test_api_get_licenses(api_key, base=DEV, params=None)

    # [ ] TEST: Get results by license number.

    # [ ] TEST: Get results by lab ID, batch number, etc.
