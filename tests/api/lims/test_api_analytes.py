"""
Analytes API Endpoint Test | Cannlytics API

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
ENDPOINT = 'analytes'

# Test using development server.
# BASE = 'http://127.0.0.1:8000/api'

# Uncomment to test with production server.
BASE = 'https://cannlytics.com/api'

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
    'analyte_id': 'cbt',
    'cas': 0.0,
    'date': '2021-07-16T00:00:00Z',
    'formula': '((measurement]*40*50)/[mass])/10058',
    'initials': 'KLS',
    'key': 'cbt',
    'limit': 100,
    'lod': 1,
    'loq': 1,
    'measurement_units': 'ppm',
    'name': 'CBT',
    'public': False,
    'result_units': 'percent'
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
    'analyte_id': 'cbt',
    'limit': 'n/a',
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Updated:', response.json()['data'])

#------------------------------------------------------------------------------
# Delete an analyte.
#------------------------------------------------------------------------------
data = {
    'analyte_id': 'cbt',
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Deleted:', response.json()['data'])
