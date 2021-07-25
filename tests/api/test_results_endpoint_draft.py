"""
Results API Endpoint Test | Cannlytics API

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
ENDPOINT = 'results'

# Test using development server.
# BASE = 'http://127.0.0.1:8000/api'

# Uncomment to test with production server.
BASE = 'https://console.cannlytics.com/api'

# Load your API key.
load_dotenv('../../.env')
API_KEY = os.getenv('CANNLYTICS_API_KEY')

# Pass your API key through the authorization header as a bearer token.
HEADERS = {
    'Authorization': 'Bearer %s' % API_KEY,
    'Content-type': 'application/json',
}

# Identify the organization that you are working with.
ORG_ID = 'test-company'

#------------------------------------------------------------------------------
# Create a result.
#------------------------------------------------------------------------------
data = {
    'approved_at': '',
    'approved_at_time': '',
    'approved_by': '',
    'non_mandatory': 'on',
    'notes': '',
    'package_id': '',
    'package_label': '',
    'product_name': '',
    'released': 'on',
    'released_at': '',
    'released_at_time': '',
    'result': '',
    'result_id': 'RESULT-1',
    'reviewed_at': '',
    'reviewed_at_time': '',
    'reviewed_by': '',
    'sample_id': '',
    'sample_type': '',
    'status': '',
    'tested_at': '',
    'tested_at_time': '',
    'units': '',
    'voided_at': '',
    'voided_at_time': ''
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Created:', response.json()['data'])

#------------------------------------------------------------------------------
# Get results.
#------------------------------------------------------------------------------
organization_id = 'test-company'
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
assert response.status_code == 200
data = response.json()['data']
print('Found:', len(data))

#------------------------------------------------------------------------------
# Update a result.
#------------------------------------------------------------------------------
data = {
    'result_id': 'RESULT-1',
    'notes': 'Now is better than never!',
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Updated:', response.json()['data'])

#------------------------------------------------------------------------------
# Delete a result.
#------------------------------------------------------------------------------
data = {
    'result_id': 'RESULT-1',
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Deleted:', response.json()['data'])
