# Cannlytics Firebase SDK

API reference for the `cannlytics.firebase` module.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Function</th>
      <th>Description</th>
      <th>Args</th>
      <th>Returns</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>`access_secret_version`</td>
      <td>Access the payload for a given secret version if one exists. The version can be a version number as a string (e.g. "5") or an alias (e.g. "latest"). 'Secret Manager Admin' permissions needed for service account. See <https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets>. !!! Warning     Do not print the secret in a production environment.</td>
      <td>project_id (str): A Firestore project ID.    secret_id (str): An ID for the secret.    version_id (str): A version for the secret.</td>
      <td>(str): The secret value.</td>
    </tr>
    <tr>
      <td>`add_secret_version`</td>
      <td>Add a new secret version to the given secret with the provided payload. A secret version contains the actual contents of a secret. A secret version can be enabled, disabled, or destroyed. To change the contents of a secret, you create a new version. Adding a secret version requires the Secret Manager Admin role (roles/secretmanager.admin) on the secret, project, folder, or organization. Roles can't be granted on a secret version. 'Secret Manager Admin' permissions needed for service account. See <https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets>.</td>
      <td>project_id (str): A Firestore project ID.    secret_id (str): An ID for the secret.    payload (dynamic): The secret.</td>
      <td>(str): The secret version's name.</td>
    </tr>
    <tr>
      <td>`add_to_array`</td>
      <td>Add an element to a given field for a given reference.</td>
      <td>ref (str): A document reference.    field (str): A list field to create or update.    value (dynamic): The value to be added to the list.    database (Client): An optional existing Firestore database client.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_custom_claims`</td>
      <td>Create custom claims for a user to grant granular permission. The new custom claims will propagate to the user's ID token the next time a new one is issued.</td>
      <td>uid (str): A user's ID.    email (str): A user's email.    claims (dict): A dictionary of the user's custom claims.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_custom_token`</td>
      <td>Create a custom token for a given user, expires after one hour.</td>
      <td>uid (str): A user's ID.    email (str): A user's email.    claims (dict):  A dictionary of the user's claims.</td>
      <td>(bytes): A token minted from the input parameters.</td>
    </tr>
    <tr>
      <td>`create_document`</td>
      <td>Create a given document with given values, this leverages the same functionality as `update_document` thanks to `set` with `merge=True`.</td>
      <td>ref (str): A document reference.    values (str): A dictionary of values to update.    database (Client): An optional existing Firestore database client.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_id`</td>
      <td>Generate a universal ID.</td>
      <td></td>
      <td>(str): A unique lexicographic ID.</td>
    </tr>
    <tr>
      <td>`create_id_from_datetime`</td>
      <td>Create an ID from an existing datetime.</td>
      <td>timestamp (datetime): The time to timestamp the ID.</td>
      <td>(str): A unique lexicographic ID.</td>
    </tr>
    <tr>
      <td>`create_log`</td>
      <td>Create an activity log.</td>
      <td>ref (str): Path to a collection of logs.    claims (dict): A dict with user fields or a Firestore user object.    action (str): The activity that took place.    log_type (str): The log type.    key (str): A key to recognize the action.    changes (list): An optional list of changes that took place.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_reference`</td>
      <td>Create a database reference for a given path.</td>
      <td>database (Firestore Client): The Firestore Client.    path (str): The path to the document or collection.</td>
      <td>(ref): Either a document or collection reference.</td>
    </tr>
    <tr>
      <td>`create_secret`</td>
      <td>Create a new secret with the given name. A secret is a logical wrapper around a collection of secret versions. Secret versions hold the actual secret material. 'Secret Manager Admin' permissions needed for service account. See <https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets>.</td>
      <td>project_id (str): The project associated with the secret.    secret_id (str): An ID for the secret.    secret (dynamic): The secret data, a string or a dict can both be used.</td>
      <td>(str): The name of the created secret.</td>
    </tr>
    <tr>
      <td>`create_session_cookie`</td>
      <td>Create a session cookie.</td>
      <td>id_token (str): A user ID token passed from the client.    expires_in (timedelta): The time until the session will expire.</td>
      <td>(bytes): A session cookie in bytes.</td>
    </tr>
    <tr>
      <td>`create_short_url`</td>
      <td>Create a short URL to a specified file.</td>
      <td>api_key (str): An API key for Firebase dynamic links.    long_url (str): A URL to create a short, dynamic link.    project_name (str): The name of the Firebase project.</td>
      <td>(str): A short link to the given URL.</td>
    </tr>
    <tr>
      <td>`create_user`</td>
      <td>Given user name and email, create an account. If the email is already being used, then nothing is returned.</td>
      <td>name (str): A name for the user.    email (str): The user's email.</td>
      <td>(tuple): Returns the User instance and a random password.</td>
    </tr>
    <tr>
      <td>`delete_collection`</td>
      <td>Delete a given collection, a batch at a time.</td>
      <td>ref (str): A document reference.    batch_size (int): The number of documents to delete at a time.        The default is 420 and the maximum is 500.    database (Client): An optional existing Firestore database client.</td>
      <td></td>
    </tr>
    <tr>
      <td>`delete_document`</td>
      <td>Delete a given document.</td>
      <td>ref (str): A document reference.    database (Client): An optional existing Firestore database client.</td>
      <td></td>
    </tr>
    <tr>
      <td>`delete_field`</td>
      <td>Delete a given field from a document.</td>
      <td>ref (str): A document reference.    field (str): The field to remove from the document.    database (Client): An optional existing Firestore database client.</td>
      <td></td>
    </tr>
    <tr>
      <td>`delete_file`</td>
      <td>Delete file from GCP bucket.</td>
      <td>blob_name (str): The name of the file to delete.    bucket_name (str): The name of the storage bucket (optional).</td>
      <td></td>
    </tr>
    <tr>
      <td>`delete_user`</td>
      <td>Delete a user from Firebase.</td>
      <td>uid (str): A user's ID.</td>
      <td></td>
    </tr>
    <tr>
      <td>`download_file`</td>
      <td>Downloads a file from Firebase Storage.</td>
      <td>source_blob_name (str): The file name to upload.    destination_file_name (str): The destination file name.    bucket_name (str): The name of the storage bucket (optional).</td>
      <td></td>
    </tr>
    <tr>
      <td>`download_files`</td>
      <td>Download all files in a given Firebase Storage folder.</td>
      <td>bucket_folder (str): A folder in the storage bucket.    local_folder (str): The local folder to download files.    bucket_name (str): The name of the storage bucket (optional).</td>
      <td></td>
    </tr>
    <tr>
      <td>`export_data`</td>
      <td>Export data from Firestore.</td>
      <td>database (Firestore Client):    ref (str): A collection or document reference.    data_file (str): The path to the local data file to upload.!!! info "Wishlist"    Parse fields that are objects into fields, similar to below.    ```py    from pandas.io.json import json_normalize    artist_and_track = json_normalize(        data=tracks_response['tracks'],        record_path='artists',        meta=['id'],        record_prefix='sp_artist_',        meta_prefix='sp_track_',        sep='_'    )    ```</td>
      <td></td>
    </tr>
    <tr>
      <td>`generate_password_reset_link`</td>
      <td>Get a password reset link for a user given their email.</td>
      <td>email (str): A user's email.</td>
      <td>(str): A password reset link for the user.</td>
    </tr>
    <tr>
      <td>`get_collection`</td>
      <td>Get documents from a collection.</td>
      <td>ref (str): A document reference.    limit (int): The maximum number of documents to return. The default is no limit.    order_by (str): A field to order the documents by, with the default being none.    desc (bool): The direction to order the documents by the order_by field.    filters (list): Filters are dictionaries of the form        `{'key': '', 'operation': '', 'value': ''}`.        Filters apply [Firebase queries](https://firebase.google.com/docs/firestore/query-data/queries)        to the given `key` for the given `value`.        Operators include: `==`, `>=`, `<=`, `>`, `<`, `!=`,        `in`, `not_in`, `array_contains`, `array_contains_any`.    start_at (dict): Optional starting at value for pagination. Expect a dict        of with `key` and `value` fields. For example: `{'key': 'number', 'value': 4 }`.    database (Client): A Firestore database client.</td>
      <td>(list): A list of documents.</td>
    </tr>
    <tr>
      <td>`get_custom_claims`</td>
      <td>Get custom claims for a user.</td>
      <td>name (str): A user ID or user email.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_document`</td>
      <td>Get a given document.</td>
      <td>ref (str): A document reference.    database (Client): A Firestore database client.</td>
      <td>(dict): Returns the document as a dictionary.\n        Returns an empty dictionary if no data is found.</td>
    </tr>
    <tr>
      <td>`get_file_url`</td>
      <td>Return the storage URL of a given file reference.</td>
      <td>ref (str): The storage location of the file.    bucket_name (str): The name of the storage bucket.    expiration (datetime): The date for when the file link should expire.</td>
      <td>(str): The storage URL of the file.</td>
    </tr>
    <tr>
      <td>`get_id_timestamp`</td>
      <td>Get the datetime that an ID was created.</td>
      <td>uid (str): A unique ID string.</td>
      <td>(datetime): The date when a unique lexicographic ID was generated.</td>
    </tr>
    <tr>
      <td>`get_random_string`</td>
      <td>Return a securely generated random string.  The bit length of the returned value can be calculated with the formula:     log_2(len(allowed_chars)^length)  For example, with default `allowed_chars` (26+26+10), this gives:   * length: 12, bit length =~ 71 bits   * length: 22, bit length =~ 131 bits  Copyright (c) Django Software Foundation and individual contributors. All rights reserved.  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:      1. Redistributions of source code must retain the above copyright notice,        this list of conditions and the following disclaimer.      2. Redistributions in binary form must reproduce the above copyright        notice, this list of conditions and the following disclaimer in the        documentation and/or other materials provided with the distribution.      3. Neither the name of Django nor the names of its contributors may be used        to endorse or promote products derived from this software without        specific prior written permission.  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`get_user`</td>
      <td>Get a user by user ID or by email.</td>
      <td>name (str): A user ID, email, or phone number.</td>
      <td>(UserRecord): A Firebase user object.</td>
    </tr>
    <tr>
      <td>`get_users`</td>
      <td>Get all Firebase users.</td>
      <td></td>
      <td>(list): A list of Firebase users.</td>
    </tr>
    <tr>
      <td>`import_data`</td>
      <td>Import data into Firestore.</td>
      <td>database (Firestore Client):    ref (str): A collection or document reference.    data_file (str): The path to the local data file to upload.!!! info "Wishlist"    It would be desirable for the following functionality to be implemented:    - Batch upload    - Handle types <https://hackersandslackers.com/importing-excel-dates-times-into-pandas/></td>
      <td></td>
    </tr>
    <tr>
      <td>`increment_value`</td>
      <td>Increment a given field for a given reference.</td>
      <td>ref (str): A document reference.    field (str): A numeric field to create or update.    amount (int): The amount to increment, default 1.    database (Client): An optional existing Firestore database client.</td>
      <td></td>
    </tr>
    <tr>
      <td>`initialize_firebase`</td>
      <td>Initialize Firebase, unless already initialized. Searches for environment credentials if `key_path` is not specified.</td>
      <td>env_file (str): An .env file that contains `GOOGLE_APPLICATION_CREDENTIALS`.    key_path (str): A path to your service account credentials (optional).    project_id (str): A Firebase project ID (optional).    bucket_name (str): A Cloud Storage bucket name (optional).</td>
      <td>(Firestore client): A Firestore database instance.</td>
    </tr>
    <tr>
      <td>`list_files`</td>
      <td>List all files in GCP bucket folder.</td>
      <td>bucket_folder (str): A folder in the storage bucket to list files.    bucket_name (str): The name of the storage bucket (optional).</td>
      <td>(list): A list of file names in the given bucket.</td>
    </tr>
    <tr>
      <td>`remove_from_array`</td>
      <td>Remove an element from a given field for a given reference.</td>
      <td>ref (str): A document reference.    field (str): A list field to update.    value (dynamic): The value to be removed from the list.    database (Client): An optional existing Firestore database client.</td>
      <td></td>
    </tr>
    <tr>
      <td>`rename_file`</td>
      <td>Rename file in GCP bucket.</td>
      <td>bucket_folder (str): A folder in the storage bucket.    file_name (str): The name of the file to rename.    newfile_name (str): The new name for the file.    bucket_name (str): The name of the storage bucket (optional).</td>
      <td></td>
    </tr>
    <tr>
      <td>`revoke_refresh_tokens`</td>
      <td>Revoke a user's refresh token.</td>
      <td>token (str): The refresh token to authenticate a user.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_custom_claims`</td>
      <td>Update custom claims for a user. The new custom claims will propagate to the user's ID token the next time a new one is issued.</td>
      <td>uid (str): A user's ID.    email (str): A user's email.    claims (dict): A dictionary of the user's custom claims.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_document`</td>
      <td>Update a given document with given values.</td>
      <td>ref (str): A document reference.    values (str): A dictionary of values to update.    database (Client): An optional existing Firestore database client.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_documents`</td>
      <td>Batch update documents, up to the `MAX_BATCH_SIZE`, 420 by default.</td>
      <td>refs (list): A list of document paths (str).    data (list): A list of document data (dict).    database (Client): An optional existing Firestore database client.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_user`</td>
      <td>Update a user.</td>
      <td>existing_user (Firebase user): A Firebase user object.    data (dict): The values of the user to update, which can include        email, phone_number, email_verified, display_name, photo_url,        and disabled.</td>
      <td></td>
    </tr>
    <tr>
      <td>`upload_file`</td>
      <td>Upload file to Firebase Storage.</td>
      <td>destination_blob_name (str): The name to save the file as.    source_file_name (str): The local file name.    data_url (str): The data URL to upload from a string.    content_type (str): The content type of the file, when uploading from a string.    bucket_name (str): The name of the storage bucket (optional).</td>
      <td></td>
    </tr>
    <tr>
      <td>`upload_files`</td>
      <td>Upload multiple files to Firebase Storage.</td>
      <td>bucket_folder (str): A folder in the storage bucket to upload files.    local_folder (str): The local folder of files to upload.    bucket_name (str): The name of the storage bucket (optional).</td>
      <td></td>
    </tr>
    <tr>
      <td>`verify_session_cookie`</td>
      <td>Verify a user's session cookie.</td>
      <td>session_cookie (str): A session cookie to authenticate a user.    check_revoked (bool): Checks if the cookie has been revoked or not (optional).    app (App): A Firebase App instance.</td>
      <td>(dict): A dictionary of key-value pairs parsed from the decoded JWT.</td>
    </tr>
    <tr>
      <td>`verify_token`</td>
      <td>Verify a user's custom token.</td>
      <td>token (str): The custom token to authenticate a user.</td>
      <td>(dict): A dictionary of key-value pairs parsed from the decoded JWT.</td>
    </tr>
  </tbody>
</table>
