# Projects Endpoint `/api/projects`

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
    BASE = 'https://console.cannlytics.com/api'
    ORG_ID = 'test-company'
    ```

## Create a project

You can create a project by posting data that includes it's `project_id`.

```py
# Create a project

data = {
    'created_at': '07/19/2021',
    'created_at_time': '16:20',
    'created_by': 'KLS',
    'notes': '',
    'organization': 'Cannlytics',
    'project_id': 'TEST',
    'received_at': '07/19/2021',
    'received_at_time': '4:20',
    'transfer_ids': ''
}
url = f'{BASE}/projects?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': {
        'created_at': '07/19/2021',
        'created_at_time': '16:20',
        'created_by': 'KLS',
        'notes': '',
        'organization': 'Cannlytics',
        'project_id': 'TEST',
        'received_at': '07/19/2021',
        'received_at_time': '4:20',
        'transfer_ids': ''
    }
}
```

## Get projects

You can get projects with the following:

```py
# Get all projects

url = f'{BASE}/projects?organization_id={ORG_ID}'
response = requests.get(url, headers=HEADERS)
print('Response:', response.json())
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': [
          {
              'created_at': '07/19/2021',
              'created_at_time': '16:20',
              'created_by': 'KLS',
              'notes': '',
              'organization': 'Cannlytics',
              'project_id': 'TEST',
              'received_at': '07/19/2021',
              'received_at_time': '4:20',
              'transfer_ids': ''
          }
    ]
}
```

## Update a project

You can update a project by passing it's `project_id` and the updated key, value pairs.

```py
# Update a project.

data = {
    'project_id': 'M-5',
    'notes': 'Look ma, no hands.',
}
url = f'{BASE}/projects?organization_id={ORG_ID}'
response = requests.post(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

The response to an update only includes the data posted.

```py
{
    'success': True,
    'data': {
        'project_id': 'M-5',
        'notes': 'Look ma, no hands.',
    }
}
```

## Delete a project

You can delete a project by sending a `DELETE` request with the `project_id` of the project that you want to delete.

```py
# Delete a project.

data = {
    'project_id': 'M-5',
}
url = f'{BASE}/projects?organization_id={ORG_ID}'
response = requests.delete(url, json=data, headers=HEADERS)
print('Response:', response.json())
```

A successful delete will return an empty array.

```py
{'success': True, 'data': []}
```
