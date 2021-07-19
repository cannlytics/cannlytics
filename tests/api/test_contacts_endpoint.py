"""
Test Contacts API Endpoint | Cannlytics API

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
BASE = 'http://127.0.0.1:8000/api'

# Uncomment to test with production server.
# BASE = 'https://console.cannlytics.com/api'

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

# Define the endpoint.
ENDPOINT = 'contacts'

#------------------------------------------------------------------------------
# Create a contact.
#------------------------------------------------------------------------------
data = {
    'address': '',
    'city': '',
    'contact_id': 'TEST',
    'county': '',
    'email': '',
    'latitude': '',
    'longitude': '',
    'organization': 'Cannlytics Test Contact',
    'phone': '',
    'state': '',
    'street': '',
    'website': '',
    'zip_code': ''
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Created:', response.json()['data'])

#------------------------------------------------------------------------------
# Get contacts.
#------------------------------------------------------------------------------
organization_id = 'test-company'
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
assert response.status_code == 200
data = response.json()['data']
print('Found:', len(data))

#------------------------------------------------------------------------------
# Update a contact.
#------------------------------------------------------------------------------
data = {
    'contact_id': 'TEST',
    'city': 'Tulsa',
    'state': 'OK',
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Updated:', response.json()['data'])

#------------------------------------------------------------------------------
# Delete a contact.
#------------------------------------------------------------------------------
data = {
    'contact_id': 'TEST',
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Deleted:', response.json()['data'])
