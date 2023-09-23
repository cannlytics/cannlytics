"""
Organizations API Endpoint Test | Cannlytics API

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 7/24/2021
Updated: 7/24/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
import os
import requests
from dotenv import load_dotenv

# Define the endpoint.
ENDPOINT = 'organizations'

# Test using development server.
BASE = 'http://127.0.0.1:8000/api'

# Uncomment to test with production server.
# BASE = 'https://cannlytics.com/api'

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
# Create an organization
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Update an organization
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Get organizations
#------------------------------------------------------------------------------
url = f'{BASE}/{ENDPOINT}'
response = requests.get(url, headers=HEADERS)
assert response.status_code == 200
data = response.json()['data']
print('Found:', len(data))


#------------------------------------------------------------------------------
# Delete an organization?
#------------------------------------------------------------------------------

