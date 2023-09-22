# Results Endpoint `/api/results`

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

## Create a result

You can create a result by posting data that includes it's `result_id`.

=== "Python"

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

=== "Node.js"

    ``` js
    // Create a result.

    let data = {
      approved_at: '',
      approved_at_time: '',
      approved_by: '',
      non_mandatory: 'on',
      notes: '',
      package_id: '',
      package_label: '',
      product_name: '',
      released: 'on',
      released_at: '',
      released_at_time: '',
      result: '',
      result_id: 'RESULT-1',
      reviewed_at: '',
      reviewed_at_time: '',
      reviewed_by: '',
      sample_id: '',
      sample_type: '',
      status: '',
      tested_at: '',
      tested_at_time: '',
      units: '',
      voided_at: '',
      voided_at_time: ''
    };
    axios.post(`${base}/results?organization_id=${orgId}`, data, options)
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

=== "Node.js"

    ``` js
    {
      success: true,
      data: {
        approved_at: '',
        approved_at_time: '',
        approved_by: '',
        non_mandatory: 'on',
        notes: '',
        package_id: '',
        package_label: '',
        product_name: '',
        released: 'on',
        released_at: '',
        released_at_time: '',
        result: '',
        result_id: 'RESULT-1',
        reviewed_at: '',
        reviewed_at_time: '',
        reviewed_by: '',
        sample_id: '',
        sample_type: '',
        status: '',
        tested_at: '',
        tested_at_time: '',
        units: '',
        voided_at: '',
        voided_at_time: ''
      }
    }
    ```

## Get results

You can get results with the following:

=== "Python"

    ```py
    # Get all results

    url = f'{BASE}/results?organization_id={ORG_ID}'
    response = requests.get(url, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Get results.

    axios.get(`${base}/results?organization_id=${orgId}`, options)
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

=== "Node.js"

    ``` js
    {
      success: true,
      data: [
        {
          package_label: '',
          result_id: 'R210710-1',
          released: 'on',
          approved_at_time: '',
          voided_at: '',
          tested_at_time: '',
          reviewed_by: '',
          reviewed_at: '',
          product_name: '',
          sample_type: '',
          non_mandatory: 'on',
          units: '',
          notes: '',
          tested_at: '',
          status: '',
          voided_at_time: '',
          package_id: '',
          reviewed_at_time: '',
          sample_id: '',
          approved_by: '',
          result: '',
          released_at_time: '',
          approved_at: '',
          released_at: ''
        }
      ]
    }
    ```

## Update a result

You can update a result by passing it's `result_id` and the updated key, value pairs.

=== "Python"

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

=== "Node.js"

    ``` js
    // Update a result.

    data = {
      result_id: 'RESULT-1',
      notes: 'Now is better than never!',
    };
    axios.post(`${base}/results?organization_id=${orgId}`, data, options)
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
            'result_id': 'RESULT-1',
            'notes': 'Now is better than never!',
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: { result_id: 'RESULT-1', notes: 'Now is better than never!' }
    }
    ```

## Delete a result

You can delete a result by sending a `DELETE` request with the `result_id` of the result that you want to delete.

=== "Python"

    ```py
    # Delete a result.

    data = {
        'result_id': 'RESULT-1',
    }
    url = f'{BASE}/results?organization_id={ORG_ID}'
    response = requests.delete(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Delete a result.

    const objID = 'TEST';
    data = { area_id: objID };
    axios.delete(`${base}/results/${objID}?organization_id=${orgId}`, { data, ...options})
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
