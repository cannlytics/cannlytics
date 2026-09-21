# Cannlytics Firebase Module

The `cannlytics.firebase` module is a wrapper of the [`firebase_admin`](https://pypi.org/project/firebase-admin/) package to make interacting with Firestore databases, Firebase Storage buckets, Firebase Auth, and Google Cloud Secret Manager even easier.

## Architecture

The module is organized into focused submodules:

| Submodule | Description |
|-----------|-------------|
| `core.py` | Firestore initialization, CRUD, queries, batch writes, IDs, logging |
| `storage.py` | Firebase Storage file operations |
| `firebase_auth.py` | Firebase Auth user management |
| `secrets.py` | Google Cloud Secret Manager |
| `pipelines.py` | Firestore Enterprise Pipeline operations *(experimental)* |

All public functions are re-exported from `__init__.py` for backward compatibility:

```py
from cannlytics.firebase import initialize_firebase, get_document, upload_file
```

## Quick Start

```py
from cannlytics.firebase import initialize_firebase

# Initialize with a .env file containing GOOGLE_APPLICATION_CREDENTIALS.
database = initialize_firebase('./env')

# Or initialize with Firestore Enterprise multi-database support.
database = initialize_firebase('./env', database_id='my-enterprise-db')
```

> Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the file path of your [service account key](https://firebase.google.com/docs/admin/setup#initialize-sdk) JSON file.

## Firestore

The Firestore functions utilize `create_reference` to turn a path into a document or collection reference, depending on the length of the path. Odd-length paths refer to collections and even-length paths refer to documents.

```py
from cannlytics.firebase import get_document, get_collection, update_document

# Get a document.
user = get_document('users/xyz')

# Update a document.
update_document('users/xyz', {'name': 'Keegan', 'updated_at': '2026-03-22'})

# Query a collection with filters.
docs = get_collection(
    'public/data/results',
    limit=100,
    order_by='total_thc',
    desc=True,
    filters=[{'key': 'state', 'operation': '==', 'value': 'wa'}],
)
```

| Function | Description |
|----------|-------------|
| `initialize_firebase(env_file, key_path, bucket_name, project_id, database_id)` | Initialize Firebase. Supports Enterprise multi-database via `database_id`. |
| `get_document(ref, database)` | Get a document as a dict with an `id` field. |
| `get_collection(ref, limit, order_by, desc, filters, database, start_at, start_after)` | Query documents. Filters use `FieldFilter` syntax. Supports `start_after` cursor pagination. |
| `update_document(ref, values, database)` | Create or update a document with merge semantics. |
| `update_documents(refs, data, database)` | Batch write with automatic sharding (max 420 per batch). |
| `delete_document(ref, database)` | Delete a document. |
| `delete_collection(ref, batch_size, database)` | Delete all documents in a collection. |
| `delete_field(ref, field, database)` | Remove a field from a document. |
| `add_to_array(ref, field, value, database)` | Append to an array field. |
| `remove_from_array(ref, field, value, database)` | Remove from an array field. |
| `increment_value(ref, field, amount, database)` | Atomically increment a numeric field. |
| `create_id()` | Generate a ULID (universally unique, lexicographically sortable). |
| `create_id_from_datetime(timestamp)` | Create a ULID from a specific datetime. |
| `get_id_timestamp(uid)` | Extract the datetime from a ULID. |

## Authentication

```py
from cannlytics.firebase import create_user, get_user, verify_token

# Create a user.
user, password = create_user('CannBot', 'contact@cannlytics.com')

# Get a user by email.
user = get_user('contact@cannlytics.com')

# Verify an ID token from the frontend.
claims = verify_token(id_token)
```

| Function | Description |
|----------|-------------|
| `create_user(name, email)` | Create a user with a generated password. |
| `get_user(name)` | Get a user by UID, email, or phone number. |
| `get_users()` | Get all users. |
| `update_user(existing_user, data)` | Update user profile fields. |
| `delete_user(uid)` | Delete a user. |
| `generate_password_reset_link(email)` | Generate a password reset link. |
| `create_custom_claims(uid, email, claims)` | Set custom claims. |
| `update_custom_claims(uid, email, claims)` | Merge custom claims. |
| `get_custom_claims(name)` | Get custom claims. |
| `create_custom_token(uid, email, claims)` | Create a custom auth token (1 hour). |
| `create_session_cookie(id_token, expires_in)` | Create a session cookie (default: 7 days). |
| `revoke_refresh_tokens(token)` | Revoke refresh tokens. |
| `verify_token(token)` | Verify a Firebase ID token. |
| `verify_session_cookie(session_cookie, check_revoked, app)` | Verify a session cookie. |

## Secret Manager

```py
from cannlytics.firebase import access_secret_version

secret = access_secret_version('my-project', 'my-secret', 'latest')
```

| Function | Description |
|----------|-------------|
| `create_secret(project_id, secret_id, secret)` | Create a new secret. |
| `add_secret_version(project_id, secret_id, payload)` | Add a new version to an existing secret. |
| `access_secret_version(project_id, secret_id, version_id)` | Access a secret version's payload. |

## Storage

```py
from cannlytics.firebase import upload_file, get_file_url, download_file

# Upload a file.
upload_file('users/xyz/photo.jpg', source_file_name='./photo.jpg')

# Get a signed URL (expires in 7 days by default).
url = get_file_url('users/xyz/photo.jpg')

# Download a file.
download_file('users/xyz/photo.jpg', './downloaded_photo.jpg')
```

> **Security note:** `get_file_url` now generates signed URLs instead of making files permanently public.

| Function | Description |
|----------|-------------|
| `upload_file(destination, source_file_name, data_url, content_type, bucket_name)` | Upload a file. |
| `upload_files(bucket_folder, local_folder, bucket_name)` | Upload all files in a folder. |
| `download_file(source, destination, bucket_name)` | Download a file. |
| `download_files(bucket_folder, local_folder, bucket_name)` | Download all files in a folder. |
| `get_file_url(ref, bucket_name, expiration)` | Get a signed URL (default: 7-day expiry). |
| `list_files(bucket_folder, bucket_name)` | List files in a folder. |
| `delete_file(blob_name, bucket_name)` | Delete a file. |
| `rename_file(bucket_folder, file_name, newfile_name, bucket_name)` | Rename a file. |

## Logging

```py
from cannlytics.firebase import create_log

create_log(
    ref='logs/api',
    claims={'uid': 'abc123', 'email': 'user@example.com'},
    action='Parsed COA',
    log_type='data',
    key='api_coas',
)
```