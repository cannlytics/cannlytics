"""
Projects API Endpoint Test | Cannlytics API

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
ENDPOINT = 'projects'

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
# Create a project.
#------------------------------------------------------------------------------
data = {
    'created_at': '07/19/2021',
    'created_at_time': '16:20',
    'created_by': 'KLS',
    'notes': '',
    'organization': 'Cannlytics',
    'project_id': 'TEST',
    'received_at': '07/19/2021',
    'received_at_time': '4:20',
    'transfer_ids': ''
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Created:', response.json()['data'])

#------------------------------------------------------------------------------
# Get projects.
#------------------------------------------------------------------------------
organization_id = 'test-company'
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
assert response.status_code == 200
data = response.json()['data']
print('Found:', len(data))

#------------------------------------------------------------------------------
# Update a project.
#------------------------------------------------------------------------------
data = {
    'project_id': 'TEST',
    'notes': 'Too cool for school.',
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Updated:', response.json()['data'])

#------------------------------------------------------------------------------
# Delete a project.
#------------------------------------------------------------------------------
data = {
    'project_id': 'TEST',
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Deleted:', response.json()['data'])
