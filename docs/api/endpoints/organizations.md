# Organizations `/api/organizations`

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

    # Define the API.
    BASE = 'https://console.cannlytics.com/api'
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

    // Define the API.
    const base = 'https://console.cannlytics.com/api';
    ```

## GET `/api/organizations`

List public organizations or organizations where you are a team member or owner. Below is an example in Python.

=== "Python"

    ```py
    url = f'{BASE}/organizations'
    response = requests.get(url, headers=HEADERS)
    print('Response:', response.json())
    ```

=== "Node.js"

    ```js
    // Get organizations.

    axios.get(`${base}/organizations`, options)
      .then(response => {
        console.log(response.data);
      })
      .catch(error => {
        console.log(error);
      });
    ```

Expected response:

=== "Python"

    ```py
    {
        'data': [
            {
                'photo_ref': 'organizations/test-compnoteany/organization_settings/logo.png',
                'owner': '<uid>',
                'linkedin': '',
                'state': '',
                'photo_size': 28439,
                'photo_modified_at': '2021-05-07T16:55:22.108000Z',
                'photo_type': 'image/png',
                'name': 'Test Company',
                'public': 'false',
                'external_id': '',
                'uid': 'test-company',
                'phone': '',
                'address': '',
                'photo_url': '',
                'organization_id': 'test-company',
                'city': '',
                'website': 'https://cannlytics.com',
                'team': ['<uid>'],
                'zip_code': '',
                'trade_name': 'Cannlytics',
                'email': 'contact@cannlytics.com',
                'photo_uploaded_at': '2021-07-05T16:45:41.379Z',
                'country': ''
            }
        ]
    }
    ```

=== "Node.js"

    ```js
    {
      data: [
        {
          photo_ref: 'organizations/test-company/organization_settings/logo.png',
          photo_size: 28439,
          owner: '<uid>',
          state: '',
          city: '',
          photo_type: 'image/png',
          public: 'false',
          trade_name: 'Cannlytics',
          country: '',
          uid: 'test-company',
          name: 'Test Company',
          email: 'contact@cannlytics.com',
          photo_uploaded_at: '2021-07-05T16:45:41.379Z',
          photo_modified_at: '2021-05-07T16:55:22.108000Z',
          external_id: '',
          photo_url: '',
          phone: '',
          organization_id: 'test-company',
          website: 'https://cannlytics.com',
          zip_code: '',
          address: '',
          linkedin: '',
          team: ['<uid>',]
        }
      ]
    }
    ```

## GET `/api/organizations/{org_id}`

You can get a specific organization by appending the organization ID (`organization_id`) as an additional path.

=== "Python"

    ```py
    org_id = 'test-company'
    url = f'{BASE}/organizations/{org_id}'
    response = requests.get(url, headers=HEADERS)
    print('Response:',  response.json())
    ```

Expected response:

=== "Python"

    ```py
    {
        'linkedin': '',
        'uid': 'test-company',
        'zip_code': '',
        'state': '',
        'photo_modified_at': '2021-05-07T16:55:22.108000Z',
        'address': '',
        'photo_size': 28439,
        'external_id': '',
        'country': '',
        'organization_id': 'test-company',
        'photo_ref': 'organizations/test-company/organization_settings/logo.png',
        'team': ['<uid>'],
        'city': '',
        'phone': '',
        'email': 'contact@cannlytics.com',
        'photo_url': ',
        'trade_name': 'Cannlytics',
        'photo_type': 'image/png',
        'owner': '<uid>',
        'photo_uploaded_at': '2021-07-05T16:45:41.379Z',
        'name': 'Test Company',
        'website': 'https://cannlytics.com',
        'public': 'false'
    }
    ```

## GET `/api/organizations/{org_id}/team`

You can get information about all users in an organization's team using the `organizations/{org_id}/team` endpoint.

=== "Python"

    ```py
    org_id = 'test-company'
    url = f'{BASE}/{ENDPOINT}/{org_id}/team'
    response = requests.get(url, headers=HEADERS)
    print('Response:', response.json())
    ```

Expected response:

=== "Python"

    ```py
    {
        'data': [
            {
                'name': 'Keegan',
                'uid': '<uid>',
                'photo_url': 'https://robohash.org/test@cannlytics.com?set=set5',
                'position': '',
                'email': 'test@cannlytics.com',
                'type': 'lab',
                'phone_number': '',
                'signed_in': True,
                'license': '',
            }
        ]
    }
    ```

## POST `/api/organizations`

Create an organization or Update an organization with the posted data if there is an ID. All organizations have a unique `organization_id`. An error is returned if the organization already exists and the user is not part of the organization's team. If an organization already exists, then only the owner can edit the organization's team.

!!! Note
    Posted API keys are stored as secrets.

On organization creation, the creating user get custom claims.

```json
{
    "owner": ["{{ organization_id }}"],
    "team": ["{{ organization_id }}"]
}
```

Owners can add other users to the organization's team, with# the receiving user having the `organization_id` added to their `team` custom claim:

```json
{
    "team": ["{{ organization_id }}", ...]
}
```

Organizations start with the standard data models. 

## POST `/api/organizations/{org_id}`

Update an organization where you are a team member with required permissions or the owner.

## DELETE `/api/organizations/{org_id}`

Archive an organization where you are the owner.

!!! Warning
    At this time, the ability to delete an organization is only implemented in the [user interface](https://console.cannlytics.com).


<!-- TODO: Describe join an organization endpoint -->