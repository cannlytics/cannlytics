# Analyses Endpoint `/api/analyses`

For all requests, you will need to pass an `organization_id` parameter. Ensure that you send requests with your API key in an authorization bearer token. The following examples assume that you are using Python 3.8+

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

## Create an analysis

You can create an analysis by posting data that includes it's `analysis_id`.

=== "Python"
  ```py
  # Create an analysis

  data = {
      'analysis_id': 'hemp-analysis',
      'analytes': ['cbd', 'cbda', 'thc', 'thca'],
      'date': '2021-07-19',
      'initials': 'KLS',
      'key': 'hemp-analysis',
      'name': 'Hemp Analysis',
      'price': '',
      'public': False
  }
  url = f'{BASE}/analyses?organization_id={ORG_ID}'
  response = requests.post(url, json=data, headers=HEADERS)
  print('Response:', response.json())
  ```

Expecting a response in the form:

=== "Python"
  ```py
  {
      'success': True,
      'data': {
          'analysis_id': 'hemp-analysis',
          'analytes': ['cbd', 'cbda', 'thc', 'thca'],
          'date': '2021-07-19',
          'initials': 'KLS',
          'key': 'hemp-analysis',
          'name': 'Hemp Analysis',
          'price': '',
          'public': False
      }
  }
  ```

## Get analyses

You can get analyses with the following:

=== "Python"
  ```py
  # Get all analyses

  url = f'{BASE}/analyses?organization_id={ORG_ID}'
  response = requests.get(url, headers=HEADERS)
  print('Response:', response.json())
  ```

Expecting a response in the form:

=== "Python"
  ```py
  {
      'success': True,
      'data': [
            {
                'analysis_id': 'hemp-analysis',
                'analytes': ['cbd', 'cbda', 'thc', 'thca'],
                'date': '2021-07-19',
                'initials': 'KLS',
                'key': 'hemp-analysis',
                'name': 'Hemp Analysis',
                'price': '',
                'public': False
            }
      ]
  }
  ```

## Update an analysis

You can update an analysis by passing it's `analysis_id` and the updated key, value pairs.

=== "Python"
  ```py
  # Update an analysis.

  data = {
      'analysis_id': 'hemp-analysis',
      'price': '$50',
  }
  url = f'{BASE}/analyses?organization_id={ORG_ID}'
  response = requests.post(url, json=data, headers=HEADERS)
  print('Response:', response.json())
  ```

The response to an update only includes the data posted.

=== "Python"
  ```py
  {
      'success': True,
      'data': {
          'analysis_id': 'hemp-analysis',
          'price': '$50
      }
  }
  ```

## Delete an analysis

You can delete an analysis by sending a `DELETE` request with the `analysis_id` of the analysis that you want to delete.

=== "Python"
  ```py
  # Delete an analysis.

  data = {
      'analysis_id': 'hemp-analysis',
  }
  url = f'{BASE}/analyses?organization_id={ORG_ID}'
  response = requests.delete(url, json=data, headers=HEADERS)
  print('Response:', response.json())
  ```

A successful delete will return an empty array.

=== "Python"
  ```py
  {'success': True, 'data': []}
  ```
