"""
Secret Manager Operations | Cannlytics Firebase Module
Copyright (c) 2021-2026 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 2/7/2021
Updated: 3/22/2026
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Create, version, and access secrets stored in
Google Cloud Secret Manager.

See: https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets
"""
# Standard imports:
from __future__ import annotations
from typing import Any

# External imports:
from google.cloud import secretmanager


def create_secret(project_id: str, secret_id: str, secret: Any) -> str:
    """Create a new secret.

    A secret is a logical wrapper around a collection of secret
    versions. Secret versions hold the actual secret material.

    Requires the ``Secret Manager Admin`` role
    (``roles/secretmanager.admin``) on the service account.

    Args:
        project_id: The GCP project ID.
        secret_id: An identifier for the secret.
        secret: The secret configuration (typically a dict
            with ``replication`` settings).

    Returns:
        The fully qualified secret name.
    """
    client = secretmanager.SecretManagerServiceClient()
    response = client.create_secret(
        parent=f'projects/{project_id}',
        secret_id=secret_id,
        secret=secret,
    )
    return response.name


def add_secret_version(
        project_id: str,
        secret_id: str,
        payload: str,
    ) -> str:
    """Add a new version to an existing secret.

    To change the contents of a secret, create a new version.
    Requires ``Secret Manager Admin`` role.

    Args:
        project_id: The GCP project ID.
        secret_id: The secret identifier.
        payload: The secret value as a string.

    Returns:
        The fully qualified secret version name.
    """
    client = secretmanager.SecretManagerServiceClient()
    parent = f'projects/{project_id}/secrets/{secret_id}'
    payload_bytes = payload.encode('UTF-8')
    response = client.add_secret_version(
        parent=parent,
        payload={'data': payload_bytes},
    )
    return response.name


def access_secret_version(
        project_id: str,
        secret_id: str,
        version_id: str = 'latest',
    ) -> str:
    """Access the payload of a secret version.

    The version can be a version number (e.g. ``"5"``) or
    an alias (e.g. ``"latest"``).

    .. warning::
        Do not print the secret in a production environment.

    Requires ``Secret Manager Admin`` role.

    Args:
        project_id: The GCP project ID.
        secret_id: The secret identifier.
        version_id: The version to access (default: ``"latest"``).

    Returns:
        The secret value as a decoded UTF-8 string.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f'projects/{project_id}/secrets/{secret_id}/versions/{version_id}'
    response = client.access_secret_version({'name': name})
    return response.payload.data.decode('UTF-8')