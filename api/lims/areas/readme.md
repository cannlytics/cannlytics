# Areas Endpoint `/api/areas`

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

## Create an area

You can create an area by posting data that includes it's `area_id`.

=== "Python"

    ```py
    # Create an area

    data = {
        'active': True,
        'area_id': 'area-51',
        'area_type': 'Default',
        'name': 'Area 51',
        'quarantine': True
    }
    url = f'{BASE}/areas?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Create an area.

    let data = {
      active: true,
      area_id: 'area-51',
      area_type: 'Default',
      name: 'Area 51',
      quarantine: true,
    };
    axios.post(`${base}/areas?organization_id=${orgId}`, data, options)
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
            'active': True,
            'area_id': 'area-51',
            'area_type': 'Default',
            'name': 'Area 51',
            'quarantine': True
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: {
        active: true,
        area_id: 'area-51',
        area_type: 'Default',
        name: 'Area 51',
        quarantine: true
      }
    }
    ```

## Get areas

You can get areas with the following:

=== "Python"

    ```py
    # Get all areas

    url = f'{BASE}/areas?organization_id={ORG_ID}'
    response = requests.get(url, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Get areas.

    axios.get(`${base}/areas?organization_id=${orgId}`, options)
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
                  'area_type': 'Default',
                  'quarantine': True,
                  'name': 'Area 51',
                  'area_id': 'area-51',
                  'active': True
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
          active: true,
          quarantine: true,
          name: 'Area 51',
          area_type: 'Default',
          area_id: 'area-51'
        }
      ]
    }
    ```

## Update an area

You can update an area by passing it's `area_id` and the updated key, value pairs.

=== "Python"

    ```py
    # Update an area.

    data = {
        'area_id': 'area-51',
        'active': False
    }
    url = f'{BASE}/areas?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Update an area.

    data = {
      area_id: 'area-51',
      active: false,
    };
    axios.post(`${base}/areas?organization_id=${orgId}`, data, options)
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
            'area_id': 'area-51',
            'active': False
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: { area_id: 'area-51', active: false }
    }
    ```

## Delete an area

You can delete an area by sending a `DELETE` request with the `area_id` of the area that you want to delete.

=== "Python"

    ```py
    # Delete an area.

    data = {
        'area_id': 'area-51',
    }
    url = f'{BASE}/areas?organization_id={ORG_ID}'
    response = requests.delete(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Delete an area.

    const objID = 'area-51';
    data = { area_id: objID };
    axios.delete(`${base}/areas/${objID}?organization_id=${orgId}`, { data, ...options})
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
