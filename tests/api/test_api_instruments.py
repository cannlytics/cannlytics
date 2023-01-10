"""
Test Instruments API Endpoint | Cannlytics API

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 7/19/2021
Updated: 7/19/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
import os
import requests
from dotenv import load_dotenv

# Test using development server.
# BASE = 'http://127.0.0.1:8000/api'

# Uncomment to test with production server.
BASE = 'https://console.cannlytics.com/api'

# Load your API key.
load_dotenv('../../../.env')
API_KEY = os.getenv('CANNLYTICS_API_KEY')

# Pass your API key through the authorization header as a bearer token.
HEADERS = {
    'Authorization': 'Bearer %s' % API_KEY,
    'Content-type': 'application/json',
}

# Identify the organization that you are working with.
ORG_ID = 'test-company'

#------------------------------------------------------------------------------
# Create an instrument.
#------------------------------------------------------------------------------
data = {
    'calibrated_by': '',
    'instrument_id': 'TEST',
    'area_id': '',
    'description': '',
    'area_name': '',
    'calibrated_at': 0,
    'vendor': 'Nomad',
    'name': 'Romulus',
    'initials': 'KLS',
    'instrument_type': 'HPLC',
    'date': '2021-07-19T00:00:00Z',
    'data_path': ''
}
url = f'{BASE}/instruments?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Created instrument:', response.json()['data'])

#------------------------------------------------------------------------------
# Get instruments.
#------------------------------------------------------------------------------
organization_id = 'test-company'
url = f'{BASE}/instruments?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
assert response.status_code == 200
print('Found instruments:', response.json()['data'])

#------------------------------------------------------------------------------
# Update an instrument.
#------------------------------------------------------------------------------
data = {
    'calibrated_at': '2020-07-19',
    'calibrated_by': 'KLS',
    'instrument_id': 'TEST',
    'initials': 'KLS',
    'name': 'Remus',
    'vendor': 'Rome',
}
url = f'{BASE}/instruments?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Updated instrument:', response.json()['data'])

#------------------------------------------------------------------------------
# Delete an instrument.
#------------------------------------------------------------------------------
data = {
    'instrument_id': 'TEST',
}
url = f'{BASE}/instruments?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Deleted instrument:', response.json()['data'])
