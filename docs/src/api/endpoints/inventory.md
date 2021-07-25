# Instruments Endpoint `/api/inventory`

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

## Create an inventory item

You can create an inventory item by posting data that includes it's `item_id`.

```py
# Create an inventory item

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
url = f'{BASE}/inventory?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': {
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
}
```

## Get inventory items

You can get inventory items with the following:

```py
# Get all inventory items

url = f'{BASE}/inventory?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': [
          {
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
    ]
}
```

## Update an inventory item

You can update an inventory item by passing it's `item_id` and the updated key, value pairs.

```py
# Update an inventory item.

data = {
    'item_id': 'endo',
    'strain_name': 'Old-time Moonshine',
}
url = f'{BASE}/inventory?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

The response to an update only includes the data posted.

```py
{
    'success': True,
    'data': {
        'item_id': 'endo',
        'strain_name': 'Old-time Moonshine',
    }
}
```

## Delete an inventory item

You can delete an inventory item by sending a `DELETE` request with the `item_id` of the item that you want to delete.

```py
# Delete an inventory item.

data = {
    'item_id': 'endo',
}
url = f'{BASE}/inventory?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

A successful delete will return an empty array.

```py
{'success': True, 'data': []}
```
