"""
Test Data COA API Endpoint | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/26/2021
Updated: 6/11/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
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


def test_api_parse_coa(api_key: str, base = DEV, params=None):
    """Test the API endpoint for parsing COAs."""
    headers = {'Authorization': 'Bearer %s' % api_key}
    url = urljoin(base, 'data/coas')
    print('URL:', url)
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()['data']
        print('Successfully parsed %i observations.' % len(data))
        return data
    else:
        print('Error:', response.status_code)
        print(response.json())


# === Tests ===
if __name__ == '__main__':

    # Load the API key from the .env file.
    load_dotenv('../../../.env')
    api_key = os.getenv('CANNLYTICS_API_KEY')

    # [ ] TEST: Parse a single COA.


    # [ ] TEST: Upload COA(s).



    # [ ] TEST: Get a specific COA.



    # [ ] TEST: Query COAs.



    # [ ] TEST: delete a COA.

