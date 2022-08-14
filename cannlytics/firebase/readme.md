# Cannlytics Firebase Module

The `cannlytics.firebase` module is a wrapper of the [`firebase_admin`](https://pypi.org/project/firebase-admin/) package to make interacting with Firebase services, such as Firestore databases and Firebase Storage buckets, even easier. For more information, see <https://firebase.google.com/docs/>.

| Function | Description |
|----------|-------------|
| `initialize_firebase(env_file=None, key_path=None, bucket_name=None, project_id=None)` | Initialize Firebase, unless already initialized. Searches for environment credentials if `key_path` is not specified. |

```py
from cannlytics.firebase import initialize_firebase

# Initialize Firebase with a .env file.
# with a `GOOGLE_APPLICATION_CREDENTIALS`
# variable of the path of your service account.
database = initialize_firebase('./env')
```

## Firestore

| Function | Description |
|----------|-------------|
| `add_to_array(ref, field, value, database=None)` | Add an element to a given field for a given reference. |
| `create_document(ref, values, database=None)` | Create a given document with given values, this leverages the same functionality as `update_document` thanks to `set` with `merge=True`. |
| `create_reference(database, path)` | Create a database reference for a given path. |
| `delete_collection(ref, batch_size=420, database=None)` | Delete a given collection, a batch at a time. |
| `delete_document(ref, database=None)` | Delete a given document. |
| `delete_field(ref, field, database=None)` | Delete a given field from a document. |
| `remove_from_array(ref, field, value, database=None)` | Remove an element from a given field for a given reference. |
| `increment_value(ref, field, amount=1, database=None)` | Increment a given field for a given reference. |
| `update_document(ref, values, database=None)` | Update a given document with given values. |
| `update_documents(refs, data, database=None)` | Batch update documents, up to the `MAX_BATCH_SIZE`, 420 by default. |
| `get_document(ref, database=None)` | Get a given document. |
| `get_collection(ref, limit=None, order_by=None, desc=False, filters=None, database=None, start_at=None)` | Get documents from a collection. Filters are dictionaries of the form `{'key': '', 'operation': '', 'value': ''}`. Filters apply [Firebase queries](https://firebase.google.com/docs/firestore/query-data/queries) to the given `key` for the given `value`. Operators include: `==`, `>=`, `<=`, `>`, `<`, `!=`, `in`, `not_in`, `array_contains`, `array_contains_any`. |
| `import_data(database, ref, data_file)` | Import data into Firestore. |
| `export_data(database, ref, data_file)` | Export data from Firestore. |
| `create_id()` | Generate a universal ID. |
| `create_id_from_datetime(timestamp)` | Create an ID from an existing datetime. |
| `get_id_timestamp(uid)` | Get the datetime that an ID was created. |

<!-- TODO: Examples -->


## Authentication

| Function | Description |
|----------|-------------|
| `create_user(name, email)` | Given user name and email, create an account. If the email is already being used, then nothing is returned. |
| `create_custom_claims(uid, email=None, claims=None)` | Create custom claims for a user to grant granular permission. The new custom claims will propagate to the user's ID token the next time a new one is issued. |
| `update_custom_claims(uid, email=None, claims=None)` | Update custom claims for a user. The new custom claims will propagate to the user's ID token the next time a new one is issued. |
| `get_custom_claims(name)` | Get custom claims for a user. |
| `create_custom_token(uid='', email=None, claims=None)` | Create a custom token for a given user, expires after one hour. |
| `create_session_cookie(id_token, expires_in=None)` | Create a session cookie. |
| `revoke_refresh_tokens(token)` | Revoke a user's refresh token. |
| `verify_token(token)` | Verify a user's custom token. |
| `verify_session_cookie(session_cookie, check_revoked=True, app=None)` | Verify a user's session cookie. |
| `get_user(name)` | Get a user by user ID or by email. |
| `get_users()` | Get all Firebase users. |
| `update_user(existing_user, data)` | Update a user. |
| `delete_user(uid)` | Delete a user from Firebase. |
| `generate_password_reset_link(email)` | Get a password reset link for a user given their email. |

<!-- TODO: Examples -->


## Secret Manager

| Function | Description |
|----------|-------------|
| `create_secret(project_id, secret_id, secret)` | Create a new secret with the given name. A secret is a logical wrapper around a collection of secret versions. Secret versions hold the actual secret material. |
| `add_secret_version(project_id, secret_id, payload)` | Add a new secret version to the given secret with the provided payload. A secret version contains the actual contents of a secret. A secret version can be enabled, disabled, or destroyed. To change the contents of a secret, you create a new version. Adding a secret version requires the Secret Manager Admin role (roles/secretmanager.admin) on the secret, project, folder, or organization. Roles can't be granted on a secret version. |
| `access_secret_version(project_id, secret_id, version_id)` | Access the payload for a given secret version if one exists. The version can be a version number as a string (e.g. "5") or an alias (e.g. "latest"). |

<!-- TODO: Examples -->


## Storage

| Function | Description |
|----------|-------------|
| `create_short_url(api_key, long_url, project_name)` | Create a short URL to a specified file. |
| `download_file(source_blob_name, destination_file_name, bucket_name=None)` | Downloads a file from Firebase Storage. |
| `download_files(bucket_folder, local_folder, bucket_name=None)` | Download all files in a given Firebase Storage folder. |
| `get_file_url(ref, bucket_name=None, expiration=None)` | Return the storage URL of a given file reference. |
| `upload_file(destination_blob_name, source_file_name=None, data_url=None, content_type='image/jpg', bucket_name=None)` | Upload file to Firebase Storage. |
| `upload_files(bucket_folder, local_folder, bucket_name=None)` | Upload multiple files to Firebase Storage. |
| `list_files(bucket_folder, bucket_name=None)` | List all files in GCP bucket folder. |
| `delete_file(blob_name, bucket_name=None)` | Delete file from GCP bucket. |
| `rename_file(bucket_folder, file_name, newfile_name, bucket_name=None)` | Rename file in GCP bucket. |

<!-- TODO: Examples -->


## Misc

| Function | Description |
|----------|-------------|
| `create_log(ref, claims, action, log_type, key, changes=None)` | Create an activity log. |

<!-- TODO: Examples -->
