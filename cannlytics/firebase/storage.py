"""
Firebase Storage Operations | Cannlytics Firebase Module
Copyright (c) 2021-2026 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 2/7/2021
Updated: 3/22/2026
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Upload, download, list, rename, and delete files
in Firebase Storage (Google Cloud Storage) buckets.
"""
# Standard imports:
from __future__ import annotations
from datetime import timedelta
import os
from typing import Any

# External imports:
from firebase_admin import storage


# === File Operations ===

def upload_file(
        destination_blob_name: str,
        source_file_name: str | None = None,
        data_url: str | None = None,
        content_type: str | None = 'image/jpg',
        bucket_name: str | None = None,
    ):
    """Upload a file to Firebase Storage.

    Either ``source_file_name`` (upload from disk) or ``data_url``
    (upload from a string/bytes) must be provided.

    Args:
        destination_blob_name: The storage path to save the file as.
        source_file_name: Path to a local file to upload.
        data_url: Raw data to upload as a string.
        content_type: MIME type when uploading from a string.
        bucket_name: The storage bucket name (optional).
    """
    bucket = storage.bucket(name=bucket_name)
    blob = bucket.blob(destination_blob_name)
    if source_file_name:
        blob.upload_from_filename(source_file_name)
    else:
        blob.upload_from_string(data_url, content_type=content_type)


def upload_files(
        bucket_folder: str,
        local_folder: str,
        bucket_name: str | None = None,
    ):
    """Upload all files in a local folder to Firebase Storage.

    Args:
        bucket_folder: The destination folder in the storage bucket.
        local_folder: Path to the local folder of files to upload.
        bucket_name: The storage bucket name (optional).
    """
    bucket = storage.bucket(name=bucket_name)
    for file_name in os.listdir(local_folder):
        local_file = os.path.join(local_folder, file_name)
        if os.path.isfile(local_file):
            blob = bucket.blob(bucket_folder + '/' + file_name)
            blob.upload_from_filename(local_file)


def download_file(
        source_blob_name: str,
        destination_file_name: str,
        bucket_name: str | None = None,
    ):
    """Download a file from Firebase Storage.

    Args:
        source_blob_name: The storage path of the file.
        destination_file_name: The local path to save the file.
        bucket_name: The storage bucket name (optional).
    """
    bucket = storage.bucket(name=bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


def download_files(
        bucket_folder: str,
        local_folder: str,
        bucket_name: str | None = None,
    ):
    """Download all files in a Firebase Storage folder.

    Creates the local folder if it does not exist.

    Args:
        bucket_folder: The storage folder to download from.
        local_folder: The local folder to save files to.
        bucket_name: The storage bucket name (optional).
    """
    os.makedirs(local_folder, exist_ok=True)
    bucket = storage.bucket(name=bucket_name)
    file_list = list_files(bucket_folder, bucket_name=bucket_name)
    for file in file_list:
        blob = bucket.blob(file)
        file_name = blob.name.split('/')[-1]
        blob.download_to_filename(os.path.join(local_folder, file_name))


def get_file_url(
        ref: str,
        bucket_name: str | None = None,
        expiration: int = 604800,
    ) -> str:
    """Return a URL for a file in Firebase Storage.

    Generates a signed URL that expires after the given duration.
    This replaces the previous ``make_public()`` approach, which
    permanently exposed files and could not be revoked.

    .. note::
        Signed URLs require that the service account has the
        ``iam.serviceAccounts.signBlob`` permission, or that
        the ``IAM Service Account Credentials API`` is enabled.

    Args:
        ref: The storage path of the file.
        bucket_name: The storage bucket name (optional).
        expiration: URL lifetime in seconds (default: 604800 = 7 days).

    Returns:
        A signed URL string for the file.
    """
    bucket = storage.bucket(name=bucket_name)
    blob = bucket.blob(ref)
    url = blob.generate_signed_url(
        expiration=timedelta(seconds=expiration),
        method='GET',
        **_signing_kwargs(blob),
    )
    return url


def _signing_kwargs(blob: Any) -> dict:
    """Arguments that let token-only credentials sign a URL.

    On Cloud Run, Cloud Functions, and Compute Engine the default
    credentials hold an access token, not a private key, and cannot sign
    locally. Given the service account's e-mail and a current token, the
    storage library signs through the IAM Credentials API instead; the
    account needs ``iam.serviceAccounts.signBlob`` on itself (the
    Service Account Token Creator role). Credentials that can sign (a
    service account key) need nothing.
    """
    import google.auth.credentials
    credentials = getattr(getattr(blob, 'client', None), '_credentials', None)
    if not isinstance(credentials, google.auth.credentials.Credentials):
        return {}
    if isinstance(credentials, google.auth.credentials.Signing):
        return {}
    if not credentials.valid:
        from google.auth.transport.requests import Request
        credentials.refresh(Request())
    email = getattr(credentials, 'service_account_email', None)
    if not email or email == 'default':
        return {}
    return {'service_account_email': email, 'access_token': credentials.token}


def list_files(
        bucket_folder: str,
        bucket_name: str | None = None,
    ) -> list[str]:
    """List all files in a storage bucket folder.

    Args:
        bucket_folder: The folder prefix to list.
        bucket_name: The storage bucket name (optional).

    Returns:
        A list of file paths (blob names) in the folder.
    """
    bucket = storage.bucket(name=bucket_name)
    files = bucket.list_blobs(prefix=bucket_folder)
    return [file.name for file in files if '.' in file.name]


def delete_file(blob_name: str, bucket_name: str | None = None):
    """Delete a file from a storage bucket.

    Args:
        blob_name: The storage path of the file to delete.
        bucket_name: The storage bucket name (optional).
    """
    bucket = storage.bucket(name=bucket_name)
    bucket.delete_blob(blob_name)


def rename_file(
        bucket_folder: str,
        file_name: str,
        newfile_name: str,
        bucket_name: str | None = None,
    ):
    """Rename a file in a storage bucket.

    Args:
        bucket_folder: The folder containing the file.
        file_name: The current file name.
        newfile_name: The new file name.
        bucket_name: The storage bucket name (optional).
    """
    bucket = storage.bucket(name=bucket_name)
    blob = bucket.blob(bucket_folder + '/' + file_name)
    bucket.rename_blob(blob, new_name=newfile_name)
