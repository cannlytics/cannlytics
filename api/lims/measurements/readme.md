# Measurements Endpoint `/api/measurements`

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

## Create a measurement

You can create a measurement by posting data that includes it's `measurement_id`.

=== "Python"

    ```py
    # Create a measurement

    data = {
        'analysis': '',
        'analysis_id': '',
        'analyte': '',
        'analyte_id': '',
        'created_at': '',
        'created_at_time': '',
        'created_by': '',
        'dilution_factor': '',
        'instrument': '',
        'instrument_id': '',
        'measurement': '',
        'measurement_id': 'M-5',
        'measurement_units': '',
        'notes': '',
        'product_name': '',
        'sample_id': 'S2',
        'sample_type': '',
        'sample_weight': '',
        'units': ''
    }
    url = f'{BASE}/measurements?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Create a measurement.

    let data = {
      analysis: '',
      analysis_id: '',
      analyte: '',
      analyte_id: '',
      created_at: '',
      created_at_time: '',
      created_by: '',
      dilution_factor: '',
      instrument: '',
      instrument_id: '',
      measurement: '',
      measurement_id: 'M-5',
      measurement_units: '',
      notes: '',
      product_name: '',
      sample_id: 'S2',
      sample_type: '',
      sample_weight: '',
      units: ''
    };
    axios.post(`${base}/measurements?organization_id=${orgId}`, data, options)
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
            'analysis': '',
            'analysis_id': '',
            'analyte': '',
            'analyte_id': '',
            'created_at': '',
            'created_at_time': '',
            'created_by': '',
            'dilution_factor': '',
            'instrument': '',
            'instrument_id': '',
            'measurement': '',
            'measurement_id': 'M-5',
            'measurement_units': '',
            'notes': '',
            'product_name': '',
            'sample_id': 'S2',
            'sample_type': '',
            'sample_weight': '',
            'units': ''
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: {
        analysis: '',
        analysis_id: '',
        analyte: '',
        analyte_id: '',
        created_at: '',
        created_at_time: '',
        created_by: '',
        dilution_factor: '',
        instrument: '',
        instrument_id: '',
        measurement: '',
        measurement_id: 'M-5',
        measurement_units: '',
        notes: '',
        product_name: '',
        sample_id: 'S2',
        sample_type: '',
        sample_weight: '',
        units: ''
      }
    }
    ```

## Get measurements

You can get measurements with the following:

=== "Python"

    ```py
    # Get all measurements

    url = f'{BASE}/measurements?organization_id={ORG_ID}'
    response = requests.get(url, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Get measurements.

    axios.get(`${base}/measurements?organization_id=${orgId}`, options)
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
                  'analysis': '',
                  'analysis_id': '',
                  'analyte': '',
                  'analyte_id': '',
                  'created_at': '',
                  'created_at_time': '',
                  'created_by': '',
                  'dilution_factor': '',
                  'instrument': '',
                  'instrument_id': '',
                  'measurement': '',
                  'measurement_id': 'M-5',
                  'measurement_units': '',
                  'notes': '',
                  'product_name': '',
                  'sample_id': 'S2',
                  'sample_type': '',
                  'sample_weight': '',
                  'units': ''
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
          analyte: '',
          sample_id: 'S2',
          created_by: '',
          analyte_id: '',
          analysis_id: '',
          measurement_units: '',
          created_at_time: '',
          instrument_id: '',
          measurement: '',
          product_name: '',
          units: '',
          analysis: '',
          sample_weight: '',
          created_at: '',
          sample_type: '',
          dilution_factor: '',
          measurement_id: 'M-5',
          notes: '',
          instrument: ''
        }
      ]
    }
    ```

## Update a measurement

You can update a measurement by passing it's `measurement_id` and the updated key, value pairs.

=== "Python"

    ```py
    # Update a measurement.

    data = {
        'measurement_id': 'M-5',
        'notes': 'Be careful what you measure.',
    }
    url = f'{BASE}/measurements?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    data = {
      measurement_id: 'M-5',
      notes: 'Be careful what you measure.',
    };
    axios.post(`${base}/measurements?organization_id=${orgId}`, data, options)
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
            'measurement_id': 'M-5',
            'notes': 'Be careful what you measure.',
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: { measurement_id: 'M-5', notes: 'Be careful what you measure.' }
    }
    ```

## Delete a measurement

You can delete a measurement by sending a `DELETE` request with the `measurement_id` of the measurement that you want to delete.

=== "Python"

    ```py
    # Delete a measurement.

    data = {
        'measurement_id': 'TEST',
    }
    url = f'{BASE}/measurements?organization_id={ORG_ID}'
    response = requests.delete(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Delete a measurement.

    const objID = 'TEST';
    data = { area_id: objID };
    axios.delete(`${base}/measurements/${objID}?organization_id=${orgId}`, { data, ...options})
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
