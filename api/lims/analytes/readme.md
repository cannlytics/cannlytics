# Analytes Endpoint `/api/analytes`

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

    ```js
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

## Create an analyte

You can create an analyte by posting data that includes it's `analyte_id`. The `formula` is used to calculate final results given instrument measurements. The `limit` is any state-mandated failure threshold. The `lod` and `loq` are your lowest order of detection and lowest order of quantification respectively. Any measurement below the `lod` will be reported as `nd` and any value between the `lod` and `loq` will have an asterisk (*) appended to the final result.

=== "Python"

    ```py
    # Create an analyte.

    data = {
        'analyte_id': 'cbt',
        'cas': 0.0,
        'date': '2021-07-16T00:00:00Z',
        'formula': '((measurement]*40*50)/[mass])/10058',
        'initials': 'KLS',
        'key': 'cbt',
        'limit': 100,
        'lod': 1,
        'loq': 1,
        'measurement_units': 'ppm',
        'name': 'CBT',
        'public': False,
        'result_units': 'percent'
    }
    url = f'{BASE}/analytes?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ```js
    // Create an analyte.

    let data = {
      analyte_id: 'cbt',
      cas: 0.0,
      date: '2021-07-16T00:00:00Z',
      formula: '((measurement]*40*50)/[mass])/10058',
      initials: 'KLS',
      key: 'cbt',
      limit: 100,
      lod: 1,
      loq: 1,
      measurement_units: 'ppm',
      name: 'CBT',
      public: false,
      result_units: 'percent'
    };
    axios.post(`${base}/analytes?organization_id=${orgId}`, data, options)
      .then(response => {
        console.log(response.data.data);
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
            'analyte_id': 'cbt',
            'cas': 0.0,
            'date': '2021-07-16T00:00:00Z',
            'formula': '((measurement]*40*50)/[mass])/10058',
            'initials': 'KLS',
            'key': 'cbt',
            'limit': 100,
            'lod': 1,
            'loq': 1,
            'measurement_units': 'ppm',
            'name': 'CBT',
            'public': False,
            'result_units': 'percent'
        }
    }
    ```

=== "Node.js"

    ```js
    {
      success: true,
      data: {
        analyte_id: 'cbt',
        cas: 0,
        date: '2021-07-16T00:00:00Z',
        formula: '((measurement]*40*50)/[mass])/10058',
        initials: 'KLS',
        key: 'cbt',
        limit: 100,
        lod: 1,
        loq: 1,
        measurement_units: 'ppm',
        name: 'CBT',
        public: false,
        result_units: 'percent'
      }
    }
    ```

## Get analytes

You can get analytes with the following:

=== "Python"

    ```py
    # Get all analytes

    url = f'{BASE}/analytes?organization_id={ORG_ID}'
    response = requests.get(url, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ```js
    // Get all analytes.

    axios.get(`${base}/analytes?organization_id=${orgId}`, options)
      .then(response => {
        console.log(response.data.data);
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
                  'key': 'abamectin',
                  'loq': 0.2,
                  'result_units': 'percent',
                  'date': '2021-07-16T00:00:00Z',
                  'cas': None,
                  'initials': 'KLS',
                  'public': False,
                  'analyte_id': 'abamectin',
                  'measurement_units': 'ppm',
                  'name': 'Abamectin',
                  'formula': '((measurement]*40*50)/[mass])/10058',
                  'lod': 0.2,
                  'limit': 0.5
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
          date: '2021-07-16T00:00:00Z',
          key: 'yeast_mold',
          formula: '((measurement]*40*50)/[mass])/10041',
          result_units: 'percent',
          cas: null,
          measurement_units: 'ppm',
          analyte_id: 'yeast_mold',
          limit: 10000,
          loq: 'NA',
          initials: 'KLS',
          name: 'Yeast Mold',
          public: false,
          lod: 'NA'
        }
      ]
    }
    ```

## Update an analyte

You can update an analyte by passing it's `analyte_id` and the updated key, value pairs.

=== "Python"

    ```py
    # Update an analyte.

    data = {
        'analyte_id': 'cbt',
        'limit': 'n/a',
    }
    url = f'{BASE}/analytes?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```
  
=== "Node.js"

    ```js
    // Update an analyte.

    data = {
      analyte_id: 'cbt',
      limit: 'n/a',
    };
    axios.post(`${base}/analytes?organization_id=${orgId}`, data, options)
      .then(response => {
        console.log(response.data.data);
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
            'analyte_id': 'cbt',
            'limit': 'n/a',
        }
    }
    ```

=== "Node.js"

    ```js
    {
      success: true,
      data: {
        analyte_id: 'cbt', 
        limit: 'n/a'
      }
    }
    ```

## Delete an analysis

You can delete an analyte by sending a `DELETE` request with the `analyte_id` of the analyte that you want to delete.

=== "Python"

    ```py
    # Delete an analyte.

    data = {'analyte_id': 'cbt'}
    url = f'{BASE}/analytes?organization_id={ORG_ID}'
    response = requests.delete(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ```js
    // Delete an analyte.

    const objID = 'cbt';
    data = { analysis_id: objID };
    axios.delete(`${base}/analytes/${objID}?organization_id=${orgId}`, { data, ...options})
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
