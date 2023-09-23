"""
Test Receipts Data API Endpoint | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/15/2023
Updated: 6/16/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
import os
from urllib.parse import urljoin

# External imports:
import requests
from dotenv import load_dotenv
import pandas as pd

# API constants.
DEV = 'http://127.0.0.1:8000/api/'
BASE = 'https://cannlytics.com/api'


def test_api_parse_receipt_image(api_key: str, doc: str, base=DEV):
    """Test the API endpoint for parsing a receipt image."""
    print('Testing:', doc)
    headers = {'Authorization': 'Bearer %s' % api_key}
    url = urljoin(base, 'data/receipts')
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


# === Tests ===
# Performed 2023-06-16 by Keegan Skeate <admin@cannlytics.com>.
if __name__ == '__main__':

    # Load a .env file with a CANNLYTICS_API_KEY.
    load_dotenv('../../../.env')
    api_key = os.getenv('CANNLYTICS_API_KEY')

    # [✓] TEST: Parse a single receipt image.
    doc = '../../../tests/assets/receipts/receipt-1.jpg'
    outfile = '../../../tests/assets/receipts/receipt-1.xlsx'
    data = test_api_parse_receipt_image(api_key, doc)
    assert data
    pd.DataFrame(data).to_excel(outfile)

    # [✓] TEST: Query receipts.
    queries = [
        {'limit': 10},
        {'order': 'parsed_at'},
        {'desc': True},
        {'product_name': 'GARCIA HAND PICKED DARK KARMA [3.5G]'},
        {'product_type': 'flower'},
        {'date': '2022-04-20'},
        {'price': '42'},
        {'license': 'C10-00006896-LIC'},
        {'number': 'EWFZVP'},
    ]
    for params in queries:
        print('Testing query:', params)
        headers = {'Authorization': 'Bearer %s' % api_key}
        url = urljoin(DEV, 'data/receipts')
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            print('Retrieved data:', data)
        else:
            print('Error:', response.status_code)
            print(response.json())

    # [✓] TEST: Get a specific receipt.
    receipt_id = data[0]['hash']
    headers = {'Authorization': 'Bearer %s' % api_key}
    url = urljoin(DEV, 'data/receipts/%s' % receipt_id)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()['data']
        print('Retrieved data:', data)
    else:
        print('Error:', response.status_code)
        print(response.json())

    # [✓] TEST: Delete a receipt.
    headers = {'Authorization': 'Bearer %s' % api_key}
    url = urljoin(DEV, 'data/receipts/%s' % receipt_id)
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print('Delete data:', data)
    else:
        print('Error:', response.status_code)
        print(response.json())
