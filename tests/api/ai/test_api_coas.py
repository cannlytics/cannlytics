"""
Test Data COA API Endpoint | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/26/2021
Updated: 6/12/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
import os
from urllib.parse import urljoin

# External imports:
import requests
from dotenv import load_dotenv


def test_api_parse_coa_pdf(api_key: str, doc: str, base=None):
    """Test the API endpoint for parsing a COA PDF."""
    print('Testing:', doc)
    headers = {'Authorization': 'Bearer %s' % api_key}
    url = urljoin(base, 'api/data/coas')
    with open(doc, 'rb') as pdf:
        files = {'file': pdf}
        print('URL:', url)
        response = requests.post(url, files=files, headers=headers)
        print(response.status_code)
        print(response.text)
        if response.status_code == 200:
            data = response.json()['data']
            print('Successfully parsed PDF. Response data:', data)
            return data
        else:
            print('Error:', response.status_code)
            print(response.json())
            return response.json()


def test_api_parse_coa_image(api_key: str, doc: str, base=None):
    """Test the API endpoint for parsing a COA image."""
    print('Testing:', doc)
    headers = {'Authorization': 'Bearer %s' % api_key}
    url = urljoin(base, 'api/data/coas')
    with open(doc, 'rb') as img:
        files = {'file': img}
        response = requests.post(url, files=files, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            print('Successfully parsed image. Response data:', data)
            return data
        else:
            print('Error:', response.status_code)
            print(response.json())
            return response.json()


def test_api_parse_coa_url(api_key: str, urls: list, base=None):
    """Test the API endpoint for parsing a COA URL."""
    print('Testing:', urls)
    headers = {'Authorization': 'Bearer %s' % api_key}
    body = {'urls': urls}
    url = urljoin(base, 'api/data/coas')
    response = requests.post(url, json=body, headers=headers)
    if response.status_code == 200:
        data = response.json()['data']
        print('Successfully parsed URL. Response data:', data)
        return data
    else:
        print('Error:', response.status_code)
        print(response.json())
        return response.json()


# === Tests ===
# Performed 2023-09-05 by Keegan Skeate <admin@cannlytics.com>.
if __name__ == '__main__':

    # Load a .env file with a CANNLYTICS_API_KEY.
    load_dotenv('../../../.env')
    api_key = os.getenv('CANNLYTICS_API_KEY')

    # API constants.
    BASE = 'https://cannlytics.com'

    # Handle development and production environments.
    DEV = False
    if DEV:
        BASE = 'http://127.0.0.1:8000'

    # [✓] TEST: Parse a single COA PDF.
    test_api_parse_coa_pdf(
        api_key,
        doc='../../assets/coas/acs/27675_0002407047.pdf',
        base=BASE,
    )

    # [ ] TEST: Parse a single COA image.
    # FIXME: This fails in production.
    test_api_parse_coa_image(
        api_key,
        doc='../../assets/qr-codes/0dC3ZxO.png',
        base=BASE,
    )

    # [✓] TEST: Parse a single COA URL.
    test_api_parse_coa_url(
        api_key,
        ['https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTM3N181NzU5NDAwMDQwMzA0NTVfMDQxNzIwMjNfNjQzZDhiOTcyMzE1YQ=='],
        base=BASE,
    )

    # [✓] TEST: Parse a unidentified COA with AI!
    test_api_parse_coa_pdf(
        api_key,
        doc='../../assets/coas/gtl/Pineapple-XX-5-13-2129146.pdf',
        base=BASE,
    )

    # [ ] TEST: Query COAs.


    # [ ] TEST: Get a specific COA.


    # [ ] TEST: Delete a COA.

