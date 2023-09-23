# Authentication

The Cannlytics API utilizes API keys for authentication.

## API Keys

A Cannlytics API key identifies a particular user, granting programmatic use at the same level of permission as the user. User API keys are encrypted using a provider's secret key. The secret key is specific to the provider, such as the Cannlytics self-hosted solution. So, only that provider can provide services to the user with the credentials provided. Cannlytics leverages [Google Secret Manager](https://cloud.google.com/secret-manager) to protect your user API keys. Cannlytics does not store API keys, leveraging HMACs to securely represent API key claims instead. Out-of-the-box, your have [audit logs](https://cloud.google.com/logging/docs/audit). All access to your information is logged, with you being able to view the logs in the Cannlytics Console.

!!! danger "Your API key is observable if you use HTTP, so please use HTTPS when you make requests to the Cannlytics API."

!!! tip "We strongly recommend that you encrypt your API keys in your data store and in memory when working with them except when you need to access them to access the service."

<!-- 
### Permissions

The default levels of permission are:

- **Staff**: Has a restricted set of actions that can be performed, such as lacking the ability to delete data, and has restricted access to certain data.
- **QA**: Can perform the majority of organization actions and has access to the majority of organization data.
- **Owner**: Has full control of an organization and can perform any action and access all organization data. -->

#### Expiration

Your API key will expire after a set mount of time, 6 months by default, but you can set the expiration date as you desire.

#### Customer Holding

You hold your API key, we do not have your API key and can not generate it if it is lost. However, you can easily delete lost API keys and create new API keys to use in their place.

## Client Requests

Cannlytics leverages Firebase Auth for [server-side session cookie management](https://firebase.google.com/docs/auth/admin/manage-cookies). The advantages of this security mechanism includes:

- All the benefits of using JWTs for authentication, with improved security.

- The ability to create session cookies with custom expiration times ranging from 5 minutes to 2 weeks. Sessions last **7 days by default**.

- The ability to revoke session cookies immediately if token theft is suspected.

Client requests are sent with a hash-based message authentication code (HMAC) [in case HTTPS is defeated](https://hackernoon.com/improve-the-security-of-api-keys-v5kp3wdu). Request authorization time is checked before issuing a client session cookie, minimizing the window of attack in case an ID token is stolen. After sign-in, all access-protected views check the session cookie and verify it before serving restricted content based on the user's custom claims.

## App authentication

For advanced usage, you can manage your authentication session with the `auth` endpoints in the table below.

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `/auth/authenticate` | `POST` | Create an authorized session. |
| `/auth/login` | `POST` | Sign into your Firebase user account. |
| `/auth/logout` | `POST` | Sign out of your Firebase user account and end your authorized session. |

<!-- TODO: Document the following endpoints:
create-key
create-pin
create-signature
delete-key
delete-pin
delete-signature
get-keys
get-signature
verify-pin
-->

<!-- 
## API Requests

You can make requests through the API passing your API key as a bearer token in the authorization header. Below is an example in Python reading an API key from a local `.env` file.

=== "Python"

    ```py

    import os
    from dotenv import load_dotenv

    # Load your API key.
    load_dotenv('.env')
    API_KEY = os.getenv('CANNLYTICS_API_KEY')

    # Pass your API key through the authorization header as a bearer token.
    HEADERS = {
        'Authorization': 'Bearer %s' % API_KEY,
        'Content-type': 'application/json',
    }
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
    ``` -->

<!-- DRAFTS -->
<!-- You can restrict the domains from which your API key can be used. -->
<!-- Optional: Examples for the following endpoints -->
<!-- /auth/create-key -->
<!-- /auth/create-pin -->
<!-- /auth/create-signature -->
<!-- /auth/delete-key -->
<!-- /auth/delete-pin -->
<!-- /auth/delete-signature -->
<!-- /auth/get-keys-->
<!-- /auth/get-signature -->
<!-- /auth/verify-pin -->

## Users Endpoint `/api/users`

You can manage your Cannlytics user account through the `users` API endpoints listed in the table below.

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `api/users/<user_id>` | `GET`, `POST` | Get and update your user details. |
