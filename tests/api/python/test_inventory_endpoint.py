"""
Inventory API Endpoint Test | Cannlytics API

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
ENDPOINT = 'inventory'

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
# Create an inventory item.
#------------------------------------------------------------------------------
data = {
    'admin_method': 'None',
    'approved': 'None',
    'approved_at': 'None',
    'approved_at_time': '',
    'area_id': 'None',
    'area_name': 'None',
    'category_name': 'None',
    'category_type': 'None',
    'dose': '',
    'dose_number': '',
    'dose_units': 'None',
    'item_id': 'endo',
    'item_type': 'None',
    'moved_at': 'None',
    'moved_at_time': '',
    'name': 'Item',
    'quantity': 'None',
    'quantity_type': 'None',
    'serving_size': '',
    'status': 'None',
    'strain_name': 'None',
    'supply_duration_days': '',
    'units': 'None',
    'volume': '',
    'volume_units': 'None',
    'weight': '',
    'weight_units': 'None'
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Created:', response.json()['data'])

#------------------------------------------------------------------------------
# Get inventory.
#------------------------------------------------------------------------------
organization_id = 'test-company'
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
assert response.status_code == 200
data = response.json()['data']
print('Found:', len(data))

#------------------------------------------------------------------------------
# Update an inventory item.
#------------------------------------------------------------------------------
data = {
    'item_id': 'endo',
    'strain_name': 'Old-time Moonshine',
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Updated:', response.json()['data'])

#------------------------------------------------------------------------------
# Delete an inventory item.
#------------------------------------------------------------------------------
data = {
    'item_id': 'endo',
}
url = f'{BASE}/{ENDPOINT}?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Deleted:', response.json()['data'])
