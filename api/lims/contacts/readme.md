# Contacts Endpoint `/api/contacts`

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

## Create a contact

You can create a contact by posting data that includes it's `contact_id`.

=== "Python"

    ```py
    # Create a contact.

    data = {
        'address': '',
        'city': '',
        'contact_id': 'TEST',
        'county': '',
        'email': '',
        'latitude': '',
        'longitude': '',
        'organization': 'Cannlytics Test Contact',
        'phone': '',
        'state': '',
        'street': '',
        'website': '',
        'zip_code': ''
    }
    url = f'{BASE}/contacts?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ```js
    // Create a contact.

    let data = {
      address: '',
      city: '',
      contact_id: 'TEST',
      county: '',
      email: '',
      latitude: '',
      longitude: '',
      organization: 'Cannlytics Test Contact',
      phone: '',
      state: '',
      street: '',
      website: '',
      zip_code: ''
    };
    axios.post(`${base}/contacts?organization_id=${orgId}`, data, options)
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
            'address': '',
            'city': '',
            'contact_id': 'TEST',
            'county': '',
            'email': '',
            'latitude': '',
            'longitude': '',
            'organization': 'Cannlytics Test Contact',
            'phone': '',
            'state': '',
            'street': '',
            'website': '',
            'zip_code': ''
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: {
        address: '',
        city: '',
        contact_id: 'TEST',
        county: '',
        email: '',
        latitude: '',
        longitude: '',
        organization: 'Cannlytics Test Contact',
        phone: '',
        state: '',
        street: '',
        website: '',
        zip_code: ''
      }
    }
    ```

## Get contacts

You can get contacts with the following:

=== "Python"

    ```py
    # Get all contacts.

    url = f'{BASE}/contacts?organization_id={ORG_ID}'
    response = requests.get(url, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Get contacts.

    axios.get(`${base}/contacts?organization_id=${orgId}`, options)
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
                  'address': '',
                  'city': '',
                  'contact_id': 'TEST',
                  'county': '',
                  'email': '',
                  'latitude': '',
                  'longitude': '',
                  'organization': 'Cannlytics Test Contact',
                  'phone': '',
                  'state': '',
                  'street': '',
                  'website': '',
                  'zip_code': ''
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
          city: 'Tulsa',
          trade_name: '',
          Phone: '8283953954',
          county: '',
          email: 'contact@cannlytics.com',
          website: '',
          phone: '',
          zip_code: '',
          longitude: '',
          address: '',
          latitude: '',
          street: '',
          state: 'OK',
          organization: 'Cannlytics',
          contact_id: 'C20210708-'
        }
      ]
    }
    ```

## Update a contact

You can update a contact by passing it's `contact_id` and the updated key, value pairs.

=== "Python"

    ```py
    # Update a contact.

    data = {
        'contact_id': 'TEST',
        'city': 'Tulsa',
        'state': 'OK'
    }
    url = f'{BASE}/contacts?organization_id={ORG_ID}'
    response = requests.post(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Update a contact.

    data = {
      contact_id: 'TEST',
      city: 'Tulsa',
      state: 'OK',
    };
    axios.post(`${base}/contacts?organization_id=${orgId}`, data, options)
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
            'contact_id': 'TEST',
            'city': 'Tulsa',
            'state': 'OK'
        }
    }
    ```

=== "Node.js"

    ``` js
    {
      success: true,
      data: {
        contact_id: 'TEST',
        city: 'Tulsa',
        state: 'OK'
      }
    }
    ```

## Delete a contact

You can delete a contact by sending a `DELETE` request with the `contact_id` of the contact that you want to delete.

=== "Python"

    ```py
    # Delete a contact.

    data = {
        'contact_id': 'TEST',
    }
    url = f'{BASE}/contacts?organization_id={ORG_ID}'
    response = requests.delete(url, json=data, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ``` js
    // Delete a contact.

    const objID = 'TEST';
    data = { area_id: objID };
    axios.delete(`${base}/contacts/${objID}?organization_id=${orgId}`, { data, ...options})
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
