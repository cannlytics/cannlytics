# Samples Endpoint `/api/samples`

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

## Create a sample

You can create a sample by posting data that includes it's `sample_id`.

=== "Python"

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

=== "Node.js"

    ``` js
    // Create a sample.

    let data = {
      batch_id: '',
      coa_url: '',
      created_at: '07/19/2021',
      created_at_time: '',
      created_by: 'KLS',
      notes: '',
      project_id: 'TEST',
      sample_id: 'SAMPLE-1',
      updated_at: '07/19/2021',
      updated_at_time: '',
      updated_by: ''
    };
    axios.post(`${base}/samples?organization_id=${orgId}`, data, options)
      .then(response => {
        console.log(response.data);
      })
      .catch(error => {
        console.log(error);
      });
    ```

Expecting a response in the form:

=== "Python"

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

=== "Node.js"

    ``` js
    {
      success: true,
      data: {
        batch_id: '',
        coa_url: '',
        created_at: '07/19/2021',
        created_at_time: '',
        created_by: 'KLS',
        notes: '',
        project_id: 'TEST',
        sample_id: 'SAMPLE-1',
        updated_at: '07/19/2021',
        updated_at_time: '',
        updated_by: ''
      }
    }
    ```

## Get samples

You can get samples with the following:

=== "Python"

    ```py
    # Get all samples

    url = f'{BASE}/samples?organization_id={ORG_ID}'
    response = requests.get(url, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Get samples.

    axios.get(`${base}/samples?organization_id=${orgId}`, options)
      .then(response => {
        console.log(response.data);
      })
      .catch(error => {
        console.log(error);
      });
    ```

Expecting a response in the form:

=== "Python"

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

=== "Node.js"

    ``` js
    {
      success: true,
      data: [
        {
          created_by: 'KLS',
          created_at: '07/08/2021',
          updated_at: '07/08/2021',
          updated_by: '',
          updated_at_time: '',
          created_at_time: '',
          batch_id: '',
          project_id: 'P210708-Test',
          sample_id: 'S210708-',
          coa_url: '',
          notes: ''
        }
      ]
    }
    ```

## Update a sample

You can update a sample by passing it's `sample_id` and the updated key, value pairs.

=== "Python"

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

=== "Node.js"

    ``` js
    // Update a sample.

    data = {
      sample_id: 'SAMPLE-1',
      batch_id: 'Night Crew Batch 86',
    };
    axios.post(`${base}/samples?organization_id=${orgId}`, data, options)
      .then(response => {
        console.log(response.data);
      })
      .catch(error => {
        console.log(error);
      });
    ```

The response to an update only includes the data posted.

=== "Python"

    ```py
    {
        'success': True,
        'data': {
            'sample_id': 'SAMPLE-1',
            'batch_id': 'Night Crew Batch 86',
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: {
        sample_id: 'SAMPLE-1',
        batch_id: 'Night Crew Batch 86'
      }
    }
    ```

## Delete a sample

You can delete a sample by sending a `DELETE` request with the `sample_id` of the sample that you want to delete.

=== "Python"

    ```py
    # Delete a sample.

    data = {
        'sample_id': 'SAMPLE-1',
    }
    url = f'{BASE}/samples?organization_id={ORG_ID}'
    response = requests.delete(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Delete a sample.

    const objID = 'TEST';
    data = { area_id: objID };
    axios.delete(`${base}/samples/${objID}?organization_id=${orgId}`, { data, ...options})
      .then(response => {
        console.log(response.data);
      })
      .catch(error => {
        console.log(error);
      });
    ```

A successful delete will return an empty array.

=== "Python"

    ```py
    {'success': True, 'data': []}
    ```

=== "Node.js"

    ``` js
    { success: true, data: [] }
    ```
