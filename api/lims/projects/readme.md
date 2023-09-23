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

## Create a project

You can create a project by posting data that includes it's `project_id`.

=== "Python"

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

=== "Node.js"

    ``` js
    // Create a project.

    const data = {
    created_at: '07/19/2021',
    created_at_time: '16:20',
    created_by: 'KLS',
    notes: '',
    organization: 'Cannlytics',
    project_id: 'TEST',
    received_at: '07/19/2021',
    received_at_time: '4:20',
    transfer_ids: ''
    };
    axios.post(`${base}/projects?organization_id=${orgId}`, data, options)
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

=== "Node.js"

    ``` js
    {
      success: true,
      data: {
        created_at: '07/19/2021',
        created_at_time: '16:20',
        created_by: 'KLS',
        notes: '',
        organization: 'Cannlytics',
        project_id: 'TEST',
        received_at: '07/19/2021',
        received_at_time: '4:20',
        transfer_ids: ''
      }
    }
    ```

## Get projects

You can get projects with the following:

=== "Python"

    ```py
    # Get all projects

    url = f'{BASE}/projects?organization_id={ORG_ID}'
    response = requests.get(url, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Get projects.

    axios.get(`${base}/projects?organization_id=${orgId}`, options)
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

=== "Node.js"

    ``` js
    {
      success: true,
      data: [
        {
          received_at: '07/28/2021',
          organization: 'Cannlytics',
          created_by: '',
          project_id: 'P210708-Test',
          notes: '',
          created_at_time: '15:15',
          created_at: '07/08/2021',
          transfer_ids: '',
          received_at_time: '15:15'
        }
      ]
    }
    ```

## Update a project

You can update a project by passing it's `project_id` and the updated key, value pairs.

=== "Python"

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

=== "Node.js"

    ``` js
    // Update a project.

    data = {
      project_id: 'TEST',
      notes: 'Too cool for school.',
    };
    axios.post(`${base}/projects?organization_id=${orgId}`, data, options)
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
            'project_id': 'M-5',
            'notes': 'Look ma, no hands.',
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: { project_id: 'TEST', notes: 'Too cool for school.' }
    }
    ```

## Delete a project

You can delete a project by sending a `DELETE` request with the `project_id` of the project that you want to delete.

=== "Python"

    ```py
    # Delete a project.

    data = {
        'project_id': 'M-5',
    }
    url = f'{BASE}/projects?organization_id={ORG_ID}'
    response = requests.delete(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Delete a project.

    const objID = 'TEST';
    data = { area_id: objID };
    axios.delete(`${base}/projects/${objID}?organization_id=${orgId}`, { data, ...options})
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
