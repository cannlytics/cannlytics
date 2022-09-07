# Cannlytics Authentication

Authentication mechanisms for the Cannlytics API, including API key utility functions, request authentication and verification helpers, and the authentication endpoints.

| Function | Description |
|----------|-------------|
| `authenticate_request(request)` | Verifies that the user has authenticated with a Firebase ID token or passed a valid API key in an `Authentication: Bearer <token>` header. |
| `get_user_from_api_key(api_key)` | Identify a user given an API key. |
| `sha256_hmac(secret, message)` | Create a SHA256-HMAC (hash-based message authentication code). |

<!-- TODO: Add examples -->
