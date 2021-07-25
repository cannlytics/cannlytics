# Instruments Endpoint `/api/instruments`

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

## Create an instrument

You can create an instrument by posting data that includes it's `instrument_id`.

```py
# Create an instrument

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
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': {
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
}
```

## Get instruments

You can get instruments with the following:

```py
# Get all instruments

url = f'{BASE}/instruments?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': [
          {
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
    ]
}
```

## Update an instrument

You can update an instrument by passing it's `instrument_id` and the updated key, value pairs.

```py
# Update an instrument.

data = {
    'calibrated_at': '2021-07-19',
    'calibrated_by': 'KLS',
    'instrument_id': 'TEST',
    'initials': 'KLS',
    'name': 'Remus',
    'vendor': 'Rome',
}
url = f'{BASE}/instruments?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

The response to an update only includes the data posted.

```py
{
    'success': True,
    'data': {
        'calibrated_at': '2021-07-19',
        'calibrated_by': 'KLS',
        'instrument_id': 'TEST',
        'initials': 'KLS',
        'name': 'Remus',
        'vendor': 'Rome',
    }
}
```

## Delete an instrument

You can delete an instrument by sending a `DELETE` request with the `instrument_id` of the instrument that you want to delete.

```py
# Delete an instrument.

data = {
    'instrument_id': 'TEST',
}
url = f'{BASE}/instruments?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

A successful delete will return an empty array.

```py
{'success': True, 'data': []}
```
