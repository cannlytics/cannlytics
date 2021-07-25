# Samples Endpoint `/api/samples`

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

## Create a sample

You can create a sample by posting data that includes it's `sample_id`.

```py
# Create a sample

data = {
    'batch_id': '',
    'coa_url': '',
    'created_at': '07/19/2021',
    'created_at_time': '',
    'created_by': 'KLS',
    'notes': '',
    'project_id': 'TEST',
    'sample_id': 'SAMPLE-1',
    'updated_at': '07/19/2021',
    'updated_at_time': '',
    'updated_by': ''
}
url = f'{BASE}/samples?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': {
        'batch_id': '',
        'coa_url': '',
        'created_at': '07/19/2021',
        'created_at_time': '',
        'created_by': 'KLS',
        'notes': '',
        'project_id': 'TEST',
        'sample_id': 'SAMPLE-1',
        'updated_at': '07/19/2021',
        'updated_at_time': '',
        'updated_by': ''
    }
}
```

## Get results

You can get results with the following:

```py
# Get all results

url = f'{BASE}/samples?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': [
          {
              'batch_id': '',
              'coa_url': '',
              'created_at': '07/19/2021',
              'created_at_time': '',
              'created_by': 'KLS',
              'notes': '',
              'project_id': 'TEST',
              'sample_id': 'SAMPLE-1',
              'updated_at': '07/19/2021',
              'updated_at_time': '',
              'updated_by': ''
          }
    ]
}
```

## Update a sample

You can update a sample by passing it's `sample_id` and the updated key, value pairs.

```py
# Update a sample.

data = {
    'sample_id': 'SAMPLE-1',
    'batch_id': 'Night Crew Batch 86',
}
url = f'{BASE}/samples?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

The response to an update only includes the data posted.

```py
{
    'success': True,
    'data': {
        'sample_id': 'SAMPLE-1',
        'batch_id': 'Night Crew Batch 86',
    }
}
```

## Delete a sample

You can delete a sample by sending a `DELETE` request with the `sample_id` of the sample that you want to delete.

```py
# Delete a sample.

data = {
    'sample_id': 'SAMPLE-1',
}
url = f'{BASE}/samples?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

A successful delete will return an empty array.

```py
{'success': True, 'data': []}
```
