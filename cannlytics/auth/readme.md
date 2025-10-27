# Authentication

Cannlytics leverages [Firebase](https://console.firebase.google.com/) for data storage, file storage, and user authentication. Use of Firebase is entirely optional and you are welcome to use your favorite database and backend services.

## Admin <a name="admin"></a>

For administering your Firebase projects, you will need to provide credentials for your applications. This is typically done by setting a `GOOGLE_APPLICATION_CREDENTIALS` environment variable that points to your service account credentials.

## Users <a name="users"></a>

Firebase secure access tokens are used to authenticate users.

| Function | Description |
|----------|-------------|
| `authenticate_request(request)` | Verifies that the user has authenticated with a Firebase ID token or passed a valid API key in an `Authentication: Bearer <token>` header. |
| `get_user_from_api_key(api_key)` | Identify a user given an API key. |
| `sha256_hmac(secret, message)` | Create a SHA256-HMAC (hash-based message authentication code). |

<!-- TODO: Add examples -->
