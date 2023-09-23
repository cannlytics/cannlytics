# Instruments Endpoint `/api/inventory`

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

## Create an inventory item

You can create an inventory item by posting data that includes it's `item_id`.

=== "Python"

    ```py
    # Create an inventory item

    data = {
        'admin_method': 'None',
        'approved': 'None',
        'approved_at': 'None',
        'approved_at_time': '',
        'area_id': 'None',
        'area_name': 'None',
        'category_name': 'None',
        'category_type': 'None',
        'dose': '',
        'dose_number': '',
        'dose_units': 'None',
        'item_id': 'endo',
        'item_type': 'None',
        'moved_at': 'None',
        'moved_at_time': '',
        'name': 'Item',
        'quantity': 'None',
        'quantity_type': 'None',
        'serving_size': '',
        'status': 'None',
        'strain_name': 'None',
        'supply_duration_days': '',
        'units': 'None',
        'volume': '',
        'volume_units': 'None',
        'weight': '',
        'weight_units': 'None'
    }
    url = f'{BASE}/inventory?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Create an inventory item.

    let data = {
      admin_method: null,
      approved: null,
      approved_at: null,
      approved_at_time: '',
      area_id: null,
      area_name: null,
      category_name: null,
      category_type: null,
      dose: '',
      dose_number: '',
      dose_units: null,
      item_id: 'endo',
      item_type: null,
      moved_at: null,
      moved_at_time: '',
      name: 'Item',
      quantity: null,
      quantity_type: null,
      serving_size: '',
      status: null,
      strain_name: null,
      supply_duration_days: '',
      units: null,
      volume: '',
      volume_units: null,
      weight: '',
      weight_units: null
    };
    axios.post(`${base}/inventory?organization_id=${orgId}`, data, options)
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
                'admin_method': 'None',
                'approved': 'None',
                'approved_at': 'None',
                'approved_at_time': '',
                'area_id': 'None',
                'area_name': 'None',
                'category_name': 'None',
                'category_type': 'None',
                'dose': '',
                'dose_number': '',
                'dose_units': 'None',
                'item_id': 'endo',
                'item_type': 'None',
                'moved_at': 'None',
                'moved_at_time': '',
                'name': 'Item',
                'quantity': 'None',
                'quantity_type': 'None',
                'serving_size': '',
                'status': 'None',
                'strain_name': 'None',
                'supply_duration_days': '',
                'units': 'None',
                'volume': '',
                'volume_units': 'None',
                'weight': '',
                'weight_units': 'None'
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: {
        admin_method: null,
        approved: null,
        approved_at: null,
        approved_at_time: '',
        area_id: null,
        area_name: null,
        category_name: null,
        category_type: null,
        dose: '',
        dose_number: '',
        dose_units: null,
        item_id: 'endo',
        item_type: null,
        moved_at: null,
        moved_at_time: '',
        name: 'Item',
        quantity: null,
        quantity_type: null,
        serving_size: '',
        status: null,
        strain_name: null,
        supply_duration_days: '',
        units: null,
        volume: '',
        volume_units: null,
        weight: '',
        weight_units: null
      }
    }
    ```

## Get inventory items

You can get inventory items with the following:

=== "Python"

    ```py
    # Get all inventory items

    url = f'{BASE}/inventory?organization_id={ORG_ID}'
    response = requests.get(url, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Get inventory.

    axios.get(`${base}/inventory?organization_id=${orgId}`, options)
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
                  'admin_method': 'None',
                  'approved': 'None',
                  'approved_at': 'None',
                  'approved_at_time': '',
                  'area_id': 'None',
                  'area_name': 'None',
                  'category_name': 'None',
                  'category_type': 'None',
                  'dose': '',
                  'dose_number': '',
                  'dose_units': 'None',
                  'item_id': 'endo',
                  'item_type': 'None',
                  'moved_at': 'None',
                  'moved_at_time': '',
                  'name': 'Item',
                  'quantity': 'None',
                  'quantity_type': 'None',
                  'serving_size': '',
                  'status': 'None',
                  'strain_name': 'None',
                  'supply_duration_days': '',
                  'units': 'None',
                  'volume': '',
                  'volume_units': 'None',
                  'weight': '',
                  'weight_units': 'None'
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
          serving_size: '',
          weight: '',
          strain_name: 'None',
          moved_at: 'None',
          area_id: 'None',
          status: 'None',
          quantity: 'None',
          dose_units: 'None',
          admin_method: 'None',
          supply_duration_days: '',
          dose: '',
          volume_units: 'None',
          units: 'None',
          volume: '',
          approved_at: 'None',
          name: 'Item',
          category_name: 'None',
          category_type: 'None',
          item_id: 'IN20210705-2',
          moved_at_time: '',
          weight_units: 'None',
          dose_number: '',
          approved: 'None',
          quantity_type: 'None',
          item_type: 'None',
          area_name: 'None',
          approved_at_time: ''
        }
      ]
    }
    ```

## Update an inventory item

You can update an inventory item by passing it's `item_id` and the updated key, value pairs.

=== "Python"

    ```py
    # Update an inventory item.

    data = {
        'item_id': 'endo',
        'strain_name': 'Old-time Moonshine',
    }
    url = f'{BASE}/inventory?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Update an inventory item.

    data = {
      item_id: 'endo',
      strain_name: 'Old-time Moonshine',
    };
    axios.post(`${base}/inventory?organization_id=${orgId}`, data, options)
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
            'item_id': 'endo',
            'strain_name': 'Old-time Moonshine',
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: { item_id: 'endo', strain_name: 'Old-time Moonshine' }
    }
    ```

## Delete an inventory item

You can delete an inventory item by sending a `DELETE` request with the `item_id` of the item that you want to delete.

=== "Python"

    ```py
    # Delete an inventory item.

    data = {
        'item_id': 'endo',
    }
    url = f'{BASE}/inventory?organization_id={ORG_ID}'
    response = requests.delete(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Delete an inventory item.

    const objID = 'endo';
    data = { area_id: objID };
    axios.delete(`${base}/inventory/${objID}?organization_id=${orgId}`, { data, ...options})
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
