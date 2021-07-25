# Transfers Endpoint `/api/transfers`

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

## Create a transfer

You can create a transfer by posting data that includes it's `transfer_id`.

```py
# Create a transfer

data = {
    'arrived_at': '',
    'arrived_at_time': '',
    'departed_at': '',
    'departed_at_time': '',
    'receiver': '',
    'receiver_org_id': '',
    'sample_count': '',
    'sender': '',
    'sender_org_id': '',
    'status': '',
    'transfer_id': 'heart-of-gold',
    'transfer_type': 'Delivery',
    'transporter': '',
}
url = f'{BASE}/transfers?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': {
        'arrived_at': '',
        'arrived_at_time': '',
        'departed_at': '',
        'departed_at_time': '',
        'receiver': '',
        'receiver_org_id': '',
        'sample_count': '',
        'sender': '',
        'sender_org_id': '',
        'status': '',
        'transfer_id': 'heart-of-gold',
        'transfer_type': 'Delivery',
        'transporter': '',
    }
}
```

## Get transfers

You can get transfers with the following:

```py
# Get all transfers

url = f'{BASE}/transfers?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': [
          {
              'arrived_at': '',
              'arrived_at_time': '',
              'departed_at': '',
              'departed_at_time': '',
              'receiver': '',
              'receiver_org_id': '',
              'sample_count': '',
              'sender': '',
              'sender_org_id': '',
              'status': '',
              'transfer_id': 'heart-of-gold',
              'transfer_type': 'Delivery',
              'transporter': '',
          }
    ]
}
```

## Update a transfer

You can update a transfer by passing it's `transfer_id` and the updated key, value pairs.

```py
# Update a transfer.

data = {
    'transfer_id': 'heart-of-gold',
    'transporter': 'Wiley',
    'notes': "He's a good guy."
}
url = f'{BASE}/transfers?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

The response to an update only includes the data posted.

```py
{
    'success': True,
    'data': {
        'transfer_id': 'heart-of-gold',
        'transporter': 'Wiley',
        'notes': "He's a good guy."
    }
}
```

## Delete a transfer

You can delete a transfer by sending a `DELETE` request with the `transfer_id` of the transfer that you want to delete.

```py
# Delete a transfer.

data = {
    'transfer_id': 'heart-of-gold'',
}
url = f'{BASE}/transfers?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

A successful delete will return an empty array.

```py
{'success': True, 'data': []}
```
