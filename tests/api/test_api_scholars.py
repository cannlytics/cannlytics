"""
Get Scholars Test | Cannlytics API

Author: Keegan Skeate
Created: Wed Mar 24 10:37:41 2021
License: MIT License

Description:
    Tests the get scholar information from the Cannlytics API.

Resources:
    https://github.com/cannlytics/cannlytics-api
"""

import requests
import urllib

# Cannlytics API and API scholars endpoint.
url = 'https://api.cannlytics.com/' # Production
url = 'http://127.0.0.1:4200/' # Dev
endpoint = 'scholars/'

expected_result = {
    'author': 'Kraler, Simon',
    'affiliation': 'Center for Molecular Cardiology, University of Zurich',
}

# Get an author's data with the API.
author = 'Kraler, Simon'
query = urllib.parse.urlencode({'q': author})
respone = requests.get(url + endpoint + '?' + query)

# Ensure that the request was successful.
assert respone.status_code == 200

# Ensure that the author's data looks correct, note that author may
# update their information, at which point the test will need to
# be updated.
author_data = respone.json()
assert author_data['author'] == expected_result['author']
assert author_data['affiliation'] == expected_result['affiliation']

print('Get scholar test successful ✓')
