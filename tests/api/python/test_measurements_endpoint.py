"""
Measurements API Endpoint Test | Cannlytics API

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 7/19/2021
Updated: 7/19/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
import os
import requests
from dotenv import load_dotenv

# Define the endpoint.
ENDPOINT = 'measurements'

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
# Create an analyte.
#------------------------------------------------------------------------------
data = {
    'analysis': '',
    'analysis_id': '',
    'analyte': '',
    'analyte_id': '',
    'created_at': '',
    'created_at_time': '',
    'created_by': '',
    'dilution_factor': '',
    'instrument': '',
    'instrument_id': '',
    'measurement': '',
    'measurement_id': 'M-5',
    'measurement_units': '',
    'notes': '',
    'product_name': '',
    'sample_id': 'S2',
    'sample_type': '',
    'sample_weight': '',
    'units': ''
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Created:', response.json()['data'])

#------------------------------------------------------------------------------
# Get analyte.
#------------------------------------------------------------------------------
organization_id = 'test-company'
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
assert response.status_code == 200
data = response.json()['data']
print('Found:', len(data))

#------------------------------------------------------------------------------
# Update an analyte.
#------------------------------------------------------------------------------
data = {
    'measurement_id': 'M-5',
    'notes': 'Be careful what you measure.',
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Updated:', response.json()['data'])

#------------------------------------------------------------------------------
# Delete an analyte.
#------------------------------------------------------------------------------
data = {
    'measurement_id': 'M-5',
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Deleted:', response.json()['data'])
