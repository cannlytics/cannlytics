# Areas Endpoint `/api/areas`

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

## Create an area

You can create an area by posting data that includes it's `area_id`.

```py
# Create an area

data = {
    'active': True,
    'area_id': 'area-51',
    'area_type': 'Default',
    'name': 'Area 51',
    'quarantine': True
}
url = f'{BASE}/areas?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': {
        'active': True,
        'area_id': 'area-51',
        'area_type': 'Default',
        'name': 'Area 51',
        'quarantine': True
    }
}
```

## Get areas

You can get areas with the following:

```py
# Get all areas

url = f'{BASE}/areas?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': [
          {
              'area_type': 'Default',
              'quarantine': True,
              'name': 'Area 51',
              'area_id': 'area-51',
              'active': True
          }
    ]
}
```

## Update an area

You can update an area by passing it's `area_id` and the updated key, value pairs.

```py
# Update an area.

data = {
    'area_id': 'area-51',
    'active': False
}
url = f'{BASE}/areas?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

The response to an update only includes the data posted.

```py
{
    'success': True,
    'data': {
        'area_id': 'area-51',
        'active': False
    }
}
```

## Delete an area

You can delete an area by sending a `DELETE` request with the `area_id` of the area that you want to delete.

```py
# Delete an area.

data = {
    'area_id': 'area-51',
}
url = f'{BASE}/areas?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

A successful delete will return an empty array.

```py
{'success': True, 'data': []}
```
