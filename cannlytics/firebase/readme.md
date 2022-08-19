# Cannlytics Firebase Module

The `cannlytics.firebase` module is a wrapper of the [`firebase_admin`](https://pypi.org/project/firebase-admin/) package to make interacting with Firebase services, such as Firestore databases and Firebase Storage buckets, even easier. Firebase is initialized with `firebase.initialize_firebase`, which returns a Firestore database instance. The following is a simple example of how to initialize a Firestore database.

```py
from cannlytics.firebase import initialize_firebase

# Initialize Firebase with a .env file.
# with a `GOOGLE_APPLICATION_CREDENTIALS`
# variable of the path of your service account.
database = initialize_firebase('./env')
```

> You will need to provide credentials for your application by setting the GOOGLE_APPLICATION_CREDENTIALS environment variable.
Set the environment variable GOOGLE_APPLICATION_CREDENTIALS to the file path of the JSON file that contains your [service account key](https://firebase.google.com/docs/admin/setup#initialize-sdk). This variable only applies to your current shell session, so if you open a new session, set the variable again.


| Function | Description |
|----------|-------------|
| `initialize_firebase(env_file=None, key_path=None, bucket_name=None, project_id=None)` | Initialize Firebase, unless already initialized. Searches for environment credentials if `key_path` is not specified. |

## Firestore

The Firestore functions utilize `create_reference` to turn a path into a document or collection reference, depending on the length of the path. Odd length paths refer to collections and even length paths refer to documents. For example, `users` is a collection of users, `users/{uid}` is a user's document, and `users/{uid}/logs` is a sub-collection of logs for the user. With this functionality, you can easily get documents as follows.

```py
# Get all user documents.
users = firebase.get_collection("users")

# Get a document.
user = firebase.get_document("users/xyz")
```

And create or update documents as follows.

```py
from datetime import datetime

# Create a user log.
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
firebase.update_document(f"users/xyz/logs/{timestamp}", {
  "activity": "Something happened",
  "created_at": timestamp,
  "updated_at": timestamp
})

# Update the user.
firebase.update_document(f"users/xyz", {
  "recent_activity": timestamp,
})
```

If you need to work with arrays or simply increment a value, then there are utility functions for you.

```py
# Add an element to an array in a document.
firebase.add_to_array("tests/firebase_test", "likes", "Testing")
data = firebase.get_document("tests/firebase_test")

# Remove an element from an array in a document.
firebase.remove_from_array("tests/firebase_test", "likes", "Sandals")
data = firebase.get_document("tests/firebase_test")

# Increment a value in a document.
firebase.increment_value("tests/firebase_test", "runs")
data = firebase.get_document("tests/firebase_test")
```

You can query a collection of documents.

```py
# Get a collection.
limit = 1000
order_by = "time"
filters = [{
  "key": "test",
  "operation": "==",
  "value":
  "firebase_test",
}]
docs = firebase.get_collection("tests", limit=limit, order_by=order_by, filters=filters)
```

Finally, you can import and export data.

```py
# Import .csv data to Firestore.
ref = "tests/test_collections/licensees"
data_file = "./assets/data/licensees_partial.csv"
firebase.import_data(db, ref, data_file)

# Export data to .csv from Firestore.
output_csv_file = "./assets/data/licensees_test.csv"
output_xlsx_file = "./assets/data/licensees_test.xlsx"
firebase.export_data(db, ref, output_csv_file)
```

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

You can use Firebase to add authentication to your app. If you choose to do so, then you can manage permissions for your users.

First, you can create a user.

```py
name = "CannBot"
email = "contact@cannlytics.com"
user, password = firebase.create_account(name, email, notification=True)
```

You can add custom claims for a user to control granular permissions.

```py
# Create and get custom claims.
claims = {"organizations": ["Cannlytics"]}
firebase.create_custom_claims(user.uid, email=email, claims=claims)
custom_claims = firebase.get_custom_claims(email)
```

You can get a user token to authenticate in your client-side code.

```py
# Create custom token.
token = firebase.create_custom_token(user.uid, email=None, claims=custom_claims)
```

You can get a user or users.

```py
# Get user.
user = firebase.get_user(email)

# Get all users.
all_users = firebase.get_users()
```

You can update a user's `photo_url`, `display_name`, `email`, `phone_number`, `email_verified`, and `disabled` fields. Pass a dictionary with the desired key/value pairs that you wish to change.

```py
# Update user.
photo_url = f"https://cannlytics.com/robohash/{user.email}/?width=420&height=420"
user = firebase.update_user(user, {"photo_url": photo_url})
```

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

## Secret Manager

For sensitive credentials, it is recommended to use [Secret Manager](https://cloud.google.com/secret-manager). You can use the following functions to easily create, update, and access secrets.

| Function | Description |
|----------|-------------|
| `create_secret(project_id, secret_id, secret)` | Create a new secret with the given name. A secret is a logical wrapper around a collection of secret versions. Secret versions hold the actual secret material. |
| `add_secret_version(project_id, secret_id, payload)` | Add a new secret version to the given secret with the provided payload. A secret version contains the actual contents of a secret. A secret version can be enabled, disabled, or destroyed. To change the contents of a secret, you create a new version. Adding a secret version requires the Secret Manager Admin role (roles/secretmanager.admin) on the secret, project, folder, or organization. Roles can't be granted on a secret version. |
| `access_secret_version(project_id, secret_id, version_id)` | Access the payload for a given secret version if one exists. The version can be a version number as a string (e.g. "5") or an alias (e.g. "latest"). |

<!-- TODO: Examples -->

## Storage

You can utilize Firebase Storage for file management.

You can upload files to storage.

```py
# Upload a file to a Firebase Storage bucket.
firebase.upload_file(bucket_name, destination_blob_name, source_file_name)

# Upload all files in a folder to a Firebase Storage bucket.
firebase.upload_files(bucket_name, bucket_folder, local_folder)
```

You can then list files in a given bucket's folder.

```py
# List all files in the Firebase Storage bucket folder.
files = firebase.list_files(bucket_name, bucket_folder)
```

You can download files.

```py
# Download a file from Firebase Storage.
firebase.download_file(bucket_name, destination_blob_name, download_file_name)

# Download all files in a given Firebase Storage folder.
firebase.download_files(bucket_name, bucket_folder, download_folder)
```

Finally, you can rename and delete files if needed.

```py
# Rename a file in the Firebase Storage bucket.
firebase.rename_file(bucket_name, bucket_folder, file_name, newfile_name)

# Delete a file from the Firebase Storage bucket.
firebase.delete_file(bucket_name, bucket_folder, file_copy)
```

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

## Misc

If you need to create logs, then there is a method, `create_log` that provides a standardized way to save logs in your database.

| Function | Description |
|----------|-------------|
| `create_log(ref, claims, action, log_type, key, changes=None)` | Create an activity log. |

<!-- TODO: Examples -->
