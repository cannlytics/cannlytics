# Results Endpoint `/api/results`

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

## Create a result

You can create a result by posting data that includes it's `result_id`.

```py
# Create a result

data = {
    'approved_at': '',
    'approved_at_time': '',
    'approved_by': '',
    'non_mandatory': 'on',
    'notes': '',
    'package_id': '',
    'package_label': '',
    'product_name': '',
    'released': 'on',
    'released_at': '',
    'released_at_time': '',
    'result': '',
    'result_id': 'RESULT-1',
    'reviewed_at': '',
    'reviewed_at_time': '',
    'reviewed_by': '',
    'sample_id': '',
    'sample_type': '',
    'status': '',
    'tested_at': '',
    'tested_at_time': '',
    'units': '',
    'voided_at': '',
    'voided_at_time': ''
}
url = f'{BASE}/results?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': {
        'approved_at': '',
        'approved_at_time': '',
        'approved_by': '',
        'non_mandatory': 'on',
        'notes': '',
        'package_id': '',
        'package_label': '',
        'product_name': '',
        'released': 'on',
        'released_at': '',
        'released_at_time': '',
        'result': '',
        'result_id': 'RESULT-1',
        'reviewed_at': '',
        'reviewed_at_time': '',
        'reviewed_by': '',
        'sample_id': '',
        'sample_type': '',
        'status': '',
        'tested_at': '',
        'tested_at_time': '',
        'units': '',
        'voided_at': '',
        'voided_at_time': ''
    }
}
```

## Get results

You can get results with the following:

```py
# Get all results

url = f'{BASE}/results?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': [
          {
              'approved_at': '',
              'approved_at_time': '',
              'approved_by': '',
              'non_mandatory': 'on',
              'notes': '',
              'package_id': '',
              'package_label': '',
              'product_name': '',
              'released': 'on',
              'released_at': '',
              'released_at_time': '',
              'result': '',
              'result_id': 'RESULT-1',
              'reviewed_at': '',
              'reviewed_at_time': '',
              'reviewed_by': '',
              'sample_id': '',
              'sample_type': '',
              'status': '',
              'tested_at': '',
              'tested_at_time': '',
              'units': '',
              'voided_at': '',
              'voided_at_time': ''
          }
    ]
}
```

## Update a result

You can update a result by passing it's `result_id` and the updated key, value pairs.

```py
# Update a result.

data = {
    'result_id': 'RESULT-1',
    'notes': 'Now is better than never!',
}
url = f'{BASE}/results?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

The response to an update only includes the data posted.

```py
{
    'success': True,
    'data': {
        'result_id': 'RESULT-1',
        'notes': 'Now is better than never!',
    }
}
```

## Delete a result

You can delete a result by sending a `DELETE` request with the `result_id` of the result that you want to delete.

```py
# Delete a result.

data = {
    'result_id': 'RESULT-1',
}
url = f'{BASE}/results?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

A successful delete will return an empty array.

```py
{'success': True, 'data': []}
```
