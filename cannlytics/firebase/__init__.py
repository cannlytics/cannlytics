"""
Firebase Interface | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/5/2022
Updated: 6/12/2026
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: The ``cannlytics.firebase`` module provides a convenient
wrapper around ``firebase_admin`` for interacting with Firestore
databases, Firebase Storage, Firebase Auth, and Google Cloud
Secret Manager.

All public functions are re-exported from focused submodules for
backward compatibility::

    from cannlytics.firebase import initialize_firebase, get_document

Submodules:
    - ``core``: Firestore initialization, CRUD, queries, IDs, logging
    - ``storage``: Firebase Storage file operations
    - ``firebase_auth``: Firebase Auth user management
    - ``secrets``: Google Cloud Secret Manager

Requires the ``firebase`` extra::

    pip install "cannlytics[firebase]"
"""
# Fail with an actionable message rather than a bare
# ModuleNotFoundError from deep inside a submodule. Every module below
# needs `firebase_admin`, so check once, here.
try:
    import firebase_admin as _firebase_admin  # noqa: F401
except ImportError as _err:  # pragma: no cover
    raise ImportError(
        'cannlytics.firebase requires the `firebase` extra. '
        'Install it with:\n\n    pip install "cannlytics[firebase]"\n'
    ) from _err

# --- Core: Firestore operations, initialization, IDs, logging ---
from .core import (
    MAX_BATCH_SIZE,
    add_to_array,
    create_id,
    create_log,
    create_reference,
    delete_collection,
    delete_document,
    delete_field,
    get_collection,
    get_document,
    increment_value,
    initialize_firebase,
    remove_from_array,
    update_document,
    update_documents,
)

# --- Storage: Firebase Storage file operations ---
from .storage import (
    delete_file,
    download_file,
    download_files,
    get_file_url,
    list_files,
    rename_file,
    upload_file,
    upload_files,
)

# --- Auth: Firebase Auth user management ---
from .firebase_auth import (
    create_custom_claims,
    create_custom_token,
    create_session_cookie,
    create_user,
    delete_user,
    generate_password_reset_link,
    get_custom_claims,
    get_user,
    get_users,
    revoke_refresh_tokens,
    update_custom_claims,
    update_user,
    verify_session_cookie,
    verify_token,
)

# --- Secrets: Google Cloud Secret Manager ---
from .secrets import (
    access_secret_version,
    add_secret_version,
    create_secret,
)

# --- Re-export get_random_string for backward compatibility ---
# (Previously exported from the monolith; used by cannlytics.auth)
from cannlytics.utils import get_random_string

__all__ = [
    # Core
    'MAX_BATCH_SIZE',
    'add_to_array',
    'create_id',
    'create_log',
    'create_reference',
    'delete_collection',
    'delete_document',
    'delete_field',
    'get_collection',
    'get_document',
    'increment_value',
    'initialize_firebase',
    'remove_from_array',
    'update_document',
    'update_documents',
    # Storage
    'delete_file',
    'download_file',
    'download_files',
    'get_file_url',
    'list_files',
    'rename_file',
    'upload_file',
    'upload_files',
    # Auth
    'create_custom_claims',
    'create_custom_token',
    'create_session_cookie',
    'create_user',
    'delete_user',
    'generate_password_reset_link',
    'get_custom_claims',
    'get_random_string',
    'get_user',
    'get_users',
    'revoke_refresh_tokens',
    'update_custom_claims',
    'update_user',
    'verify_session_cookie',
    'verify_token',
    # Secrets
    'access_secret_version',
    'add_secret_version',
    'create_secret',
]