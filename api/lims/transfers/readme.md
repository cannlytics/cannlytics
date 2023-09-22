# Transfers Endpoint `/api/transfers`

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

## Create a transfer

You can create a transfer by posting data that includes it's `transfer_id`.

=== "Python"

    ```py
    # Create a transfer

    data = {
        'arrived_at': '',
        'arrived_at_time': '',
        'departed_at': '',
        'departed_at_time': '',
        'receiver': '',
        'receiver_org_id': '',
        'sample_count': '',
        'sender': '',
        'sender_org_id': '',
        'status': '',
        'transfer_id': 'heart-of-gold',
        'transfer_type': 'Delivery',
        'transporter': '',
    }
    url = f'{BASE}/transfers?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Create a transfer.

    let data = {
      arrived_at: '',
      arrived_at_time: '',
      departed_at: '',
      departed_at_time: '',
      receiver: '',
      receiver_org_id: '',
      sample_count: '',
      sender: '',
      sender_org_id: '',
      status: '',
      transfer_id: 'heart-of-gold',
      transfer_type: 'Delivery',
      transporter: '',
    };
    axios.post(`${base}/transfers?organization_id=${orgId}`, data, options)
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
            'arrived_at': '',
            'arrived_at_time': '',
            'departed_at': '',
            'departed_at_time': '',
            'receiver': '',
            'receiver_org_id': '',
            'sample_count': '',
            'sender': '',
            'sender_org_id': '',
            'status': '',
            'transfer_id': 'heart-of-gold',
            'transfer_type': 'Delivery',
            'transporter': '',
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: {
        arrived_at: '',
        arrived_at_time: '',
        departed_at: '',
        departed_at_time: '',
        receiver: '',
        receiver_org_id: '',
        sample_count: '',
        sender: '',
        sender_org_id: '',
        status: '',
        transfer_id: 'heart-of-gold',
        transfer_type: 'Delivery',
        transporter: ''
      }
    }
    ```

## Get transfers

You can get transfers with the following:

=== "Python"

    ```py
    # Get all transfers

    url = f'{BASE}/transfers?organization_id={ORG_ID}'
    response = requests.get(url, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Get transfers.

    axios.get(`${base}/transfers?organization_id=${orgId}`, options)
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
                  'arrived_at': '',
                  'arrived_at_time': '',
                  'departed_at': '',
                  'departed_at_time': '',
                  'receiver': '',
                  'receiver_org_id': '',
                  'sample_count': '',
                  'sender': '',
                  'sender_org_id': '',
                  'status': '',
                  'transfer_id': 'heart-of-gold',
                  'transfer_type': 'Delivery',
                  'transporter': '',
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
          receiver: '',
          arrived_at: '',
          status: '',
          receiver_org_id: '',
          arrived_at_time: '',
          sender_org_id: '',
          departed_at_time: '',
          sender: '',
          departed_at: '',
          transporter: '',
          sample_count: '',
          transfer_type: '',
          transfer_id: 'TR210708-'
        }
      ]
    }
    ```

## Update a transfer

You can update a transfer by passing it's `transfer_id` and the updated key, value pairs.

=== "Python"

    ```py
    # Update a transfer.

    data = {
        'transfer_id': 'heart-of-gold',
        'transporter': 'Wiley',
        'notes': "He's a good guy."
    }
    url = f'{BASE}/transfers?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Update a transfer.

    data = {
      transfer_id: 'heart-of-gold',
      transporter: 'Wiley',
      notes: "He's a good guy."
    };
    axios.post(`${base}/transfers?organization_id=${orgId}`, data, options)
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
            'transfer_id': 'heart-of-gold',
            'transporter': 'Wiley',
            'notes': "He's a good guy."
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: {
        transfer_id: 'heart-of-gold',
        transporter: 'Wiley',
        notes: "He's a good guy."
      }
    }
    ```

## Delete a transfer

You can delete a transfer by sending a `DELETE` request with the `transfer_id` of the transfer that you want to delete.

=== "Python"

    ```py
    # Delete a transfer.

    data = {
        'transfer_id': 'heart-of-gold'',
    }
    url = f'{BASE}/transfers?organization_id={ORG_ID}'
    response = requests.delete(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Delete a transfer.

    const objID = 'heart-of-gold';
    data = { area_id: objID };
    axios.delete(`${base}/transfers/${objID}?organization_id=${orgId}`, { data, ...options})
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
