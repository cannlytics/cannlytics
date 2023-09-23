# Invoices Endpoint `/api/invoices`

For all requests, you will need to pass an `organization_id` parameter. Ensure that you send your API key in an authorization bearer token in the headers of your requests.

=== "Python"

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
    BASE = 'https://cannlytics.com/api'
    ORG_ID = 'test-company'
    ```

=== "Node.js"

    ``` js
    const axios = require('axios');
    require('dotenv').config();

    // Pass API key through the authorization header as a bearer token.
    const apiKey = process.env.CANNLYTICS_API_KEY;
    const options = {
      headers: { 'Authorization' : `Bearer ${apiKey}` }
    };

    // Define the API and your organization.
    const base = 'https://cannlytics.com/api';
    const orgId = 'test-company';
    ```

## Create an invoice

You can create an invoice by posting data that includes it's `invoice_id`.

```py
# Create an invoice

data = {
    'invoice_id': 'TEST',
    'project_id': 'project-1',
    'amount': '350',
    'currency': 'USD',
}
url = f'{BASE}/invoices?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

=== "Node.js"

    ``` js

    ```

Expecting a response in the form:

```py
{
    'success': True,
    'data': {
        'invoice_id': 'TEST',
        'project_id': 'project-1',
        'amount': '350',
        'currency': 'USD',
    }
}
```

=== "Node.js"

    ``` js

    ```

## Get invoices

You can get invoices with the following:

```py
# Get all invoices

url = f'{BASE}/invoices?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
print('Response:', response.json())
```

=== "Node.js"

    ``` js

    ```

Expecting a response in the form:

```py
{
    'success': True,
    'data': [
          {
              'invoice_id': 'TEST',
              'project_id': 'project-1',
              'amount': '350',
              'currency': 'USD',
          }
    ]
}
```

=== "Node.js"

    ``` js

    ```

## Update an invoice

You can update an invoice by passing it's `invoice_id` and the updated key, value pairs.

```py
# Update an invoice.

data = {
    'invoice_id': 'TEST',
    'amount': '720',
}
url = f'{BASE}/invoices?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

=== "Node.js"

    ``` js

    ```

The response to an update only includes the data posted.

```py
{
    'success': True,
    'data': {
        'invoice_id': 'TEST',
        'amount': '720',
    }
}
```

=== "Node.js"

    ``` js

    ```

## Delete an invoice

You can delete an invoice by sending a `DELETE` request with the `invoice_id` of the invoice that you want to delete.

```py
# Delete an invoice.

data = {
    'invoice_id': 'TEST',
}
url = f'{BASE}/invoices?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

=== "Node.js"

    ``` js

    ```

A successful delete will return an empty array.

```py
{'success': True, 'data': []}
```

=== "Node.js"

    ``` js

    ```
