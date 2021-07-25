# Contacts Endpoint `/api/contacts`

For all requests, you will need to pass an `organization_id` parameter. Ensure that you send requests with your API key in an authorization bearer token. The following examples assume that you are using Python 3.8+

```py
import os
import requests
from dotenv import load_dotenv

#  Pass API key through the authorization header as a bearer token.
load_dotenv('.env')
API_KEY = os.getenv('CANNLYTICS_API_KEY')
HEADERS = {
    'Authorization': 'Bearer %s' % API_KEY,
    'Content-type': 'application/json',
}

# Define the API and your organization.
BASE = 'https://console.cannlytics.com/api'
ORG_ID = 'test-company'
```

## Create a contact

You can create a contact by posting data that includes it's `contact_id`.

```py
# Create a contact

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
url = f'{BASE}/contacts?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': {
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
}
```

## Get contacts

You can get contacts with the following:

```py
# Get all contacts

url = f'{BASE}/contacts?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': [
          {
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
    ]
}
```

## Update a contact

You can update a contact by passing it's `contact_id` and the updated key, value pairs.

```py
# Update a contact.

data = {
    'contact_id': 'TEST',
    'city': 'Tulsa',
    'state': 'OK'
}
url = f'{BASE}/contacts?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

The response to an update only includes the data posted.

```py
{
    'success': True,
    'data': {
        'contact_id': 'TEST',
        'city': 'Tulsa',
        'state': 'OK'
    }
}
```

## Delete a contact

You can delete a contact by sending a `DELETE` request with the `contact_id` of the contact that you want to delete.

```py
# Delete a contact.

data = {
    'contact_id': 'TEST',
}
url = f'{BASE}/contacts?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

A successful delete will return an empty array.

```py
{'success': True, 'data': []}
```
