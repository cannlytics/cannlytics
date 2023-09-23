# Instruments Endpoint `/api/instruments`

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

## Create an instrument

You can create an instrument by posting data that includes it's `instrument_id`.

=== "Python"

    ```py
    # Create an instrument.

    data = {
        'calibrated_by': '',
        'instrument_id': 'TEST',
        'area_id': '',
        'description': '',
        'area_name': '',
        'calibrated_at': 0,
        'vendor': 'Nomad',
        'name': 'Romulus',
        'initials': 'KLS',
        'instrument_type': 'HPLC',
        'date': '2021-07-19T00:00:00Z',
        'data_path': ''
    }
    url = f'{BASE}/instruments?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ```js
    // Create an instrument.

    let data = {
      calibrated_by: '',
      instrument_id: 'TEST',
      area_id: '',
      description: '',
      area_name: '',
      calibrated_at: 0,
      vendor: 'Nomad',
      name: 'Romulus',
      initials: 'KLS',
      instrument_type: 'HPLC',
      date: '2021-07-19T00:00:00Z',
      data_path: ''
    };
    axios.post(`${base}/instruments?organization_id=${orgId}`, data, options)
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
            'calibrated_by': '',
            'instrument_id': 'TEST',
            'area_id': '',
            'description': '',
            'area_name': '',
            'calibrated_at': 0,
            'vendor': 'Nomad',
            'name': 'Romulus',
            'initials': 'KLS',
            'instrument_type': 'HPLC',
            'date': '2021-07-19T00:00:00Z',
            'data_path': ''
        }
    }
    ```

=== "Node.js"

    ```js
    {
      success: true,
      data: {
        calibrated_by: '',
        instrument_id: 'TEST',
        area_id: '',
        description: '',
        area_name: '',
        calibrated_at: 0,
        vendor: 'Nomad',
        name: 'Romulus',
        initials: 'KLS',
        instrument_type: 'HPLC',
        date: '2021-07-19T00:00:00Z',
        data_path: ''
      }
    }
    ```

## Get instruments

You can get instruments with the following:

=== "Python"

    ```py
    # Get instruments,

    url = f'{BASE}/instruments?organization_id={ORG_ID}'
    response = requests.get(url, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ```js
    // Get instruments.

    axios.get(`${base}/instruments?organization_id=${orgId}`, options)
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
                  'calibrated_by': '',
                  'instrument_id': 'TEST',
                  'area_id': '',
                  'description': '',
                  'area_name': '',
                  'calibrated_at': 0,
                  'vendor': 'Nomad',
                  'name': 'Romulus',
                  'initials': 'KLS',
                  'instrument_type': 'HPLC',
                  'date': '2021-07-19T00:00:00Z',
                  'data_path': ''
              }
        ]
    }
    ```

=== "Node.js"

    ```js
    {
      success: true,
      data: [
        {
          calibrated_by: '',
          area_id: '',
          name: 'Romulus',
          vendor: 'Agilent',
          initials: 'KLS',
          area_name: '',
          date: '2021-07-16T00:00:00Z',
          instrument_id: 'T001',
          instrument_type: 'HPLC',
          data_path: '',
          description: '',
          calibrated_at: 0
        }
      ]
    }
    ```

## Update an instrument

You can update an instrument by passing it's `instrument_id` and the updated key, value pairs.

=== "Python"

    ```py
    # Update an instrument.

    data = {
        'calibrated_at': '2021-07-19',
        'calibrated_by': 'KLS',
        'instrument_id': 'TEST',
        'initials': 'KLS',
        'name': 'Remus',
        'vendor': 'Rome',
    }
    url = f'{BASE}/instruments?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ```js
    // Update an instrument.

    data = {
      calibrated_at: '2020-07-19',
      calibrated_by: 'KLS',
      instrument_id: 'TEST',
      initials: 'KLS',
      name: 'Remus',
      vendor: 'Rome',
    };
    axios.post(`${base}/instruments?organization_id=${orgId}`, data, options)
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
            'calibrated_at': '2021-07-19',
            'calibrated_by': 'KLS',
            'instrument_id': 'TEST',
            'initials': 'KLS',
            'name': 'Remus',
            'vendor': 'Rome',
        }
    }
    ```

=== "Node.js"

    ```js
    {
      success: true,
      data: {
        calibrated_at: '2020-07-19',
        calibrated_by: 'KLS',
        instrument_id: 'TEST',
        initials: 'KLS',
        name: 'Remus',
        vendor: 'Rome'
      }
    }
    ```

## Delete an instrument

You can delete an instrument by sending a `DELETE` request with the `instrument_id` of the instrument that you want to delete.

=== "Python"

    ```py
    # Delete an instrument.

    data = {
        'instrument_id': 'TEST',
    }
    url = f'{BASE}/instruments?organization_id={ORG_ID}'
    response = requests.delete(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ```js
    // Delete an instrument.

    const objID = 'TEST';
    data = { area_id: objID };
    axios.delete(`${base}/instruments/${objID}?organization_id=${orgId}`, { data, ...options})
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

    ```js
    { success: true, data: [] }
    ```
