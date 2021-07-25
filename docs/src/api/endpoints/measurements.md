# Measurements Endpoint `/api/measurements`

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

## Create a measurement

You can create a measurement by posting data that includes it's `measurement_id`.

```py
# Create a measurement

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
url = f'{BASE}/measurements?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': {
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
}
```

## Get measurements

You can get measurements with the following:

```py
# Get all measurements

url = f'{BASE}/measurements?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': [
          {
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
    ]
}
```

## Update a measurement

You can update a measurement by passing it's `measurement_id` and the updated key, value pairs.

```py
# Update a measurement.

data = {
    'measurement_id': 'M-5',
    'notes': 'Be careful what you measure.',
}
url = f'{BASE}/measurements?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

The response to an update only includes the data posted.

```py
{
    'success': True,
    'data': {
        'measurement_id': 'M-5',
        'notes': 'Be careful what you measure.',
    }
}
```

## Delete a measurement

You can delete a measurement by sending a `DELETE` request with the `measurement_id` of the measurement that you want to delete.

```py
# Delete a measurement.

data = {
    'measurement_id': 'TEST',
}
url = f'{BASE}/measurements?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

A successful delete will return an empty array.

```py
{'success': True, 'data': []}
```
