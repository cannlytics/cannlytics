"""
Firestore Core Operations | Cannlytics Firebase Module
Copyright (c) 2021-2026 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 2/7/2021
Updated: 4/28/2026
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Firestore database initialization, document CRUD operations,
collection queries, batch writes, ID generation, and activity logging.

Path conventions:

    Firestore paths follow strict alternation: collection/document/
    collection/document/... A path with an even number of segments
    resolves to a document; a path with an odd number of segments
    resolves to a collection. Functions in this module that operate
    on documents (``get_document``, ``update_document``,
    ``delete_document``, ``delete_field``, ``add_to_array``,
    ``remove_from_array``, ``increment_value``) validate that the
    given path has an even number of segments. Functions that
    operate on collections (``get_collection``, ``delete_collection``)
    validate odd. Invalid paths raise ``ValueError`` immediately at
    the call site rather than allowing the operation to fail deep
    inside the Google Cloud SDK with a cryptic message.

Example:

```py
from cannlytics.firebase import initialize_firebase, get_document

database = initialize_firebase('./env')
user = get_document('users/xyz', database=database)
```
"""
# Standard imports:
from __future__ import annotations
from datetime import datetime
from typing import Any
from uuid import uuid4

# External imports:
from dotenv import dotenv_values
from firebase_admin import (
    credentials,
    firestore,
    initialize_app,
)
from google.cloud.firestore import ArrayUnion, ArrayRemove, Increment
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.transforms import DELETE_FIELD

# The maximum number of documents to include in batch updates.
# The official limit is 500, but pushing too close to the limit
# increases the likelihood of failure to commit.
MAX_BATCH_SIZE = 420

# Module-level database ID, set during initialize_firebase().
# When set, all functions that default to firestore.client() will
# automatically target this database instead of '(default)'.
_default_database_id: str | None = None


def _get_client() -> Any:
    """Return a Firestore client using the module-level database ID.

    This ensures that after ``initialize_firebase(database_id=...)``
    is called, all subsequent operations automatically target the
    correct database without requiring callers to pass a ``database``
    parameter.
    """
    if _default_database_id:
        return firestore.client(database_id=_default_database_id)
    return firestore.client()


# === Path validation ===

def _validate_document_path(path: str) -> None:
    """Validate that a path resolves to a document (even segment count).

    Firestore paths alternate collection/document/collection/document.
    A path with an even number of segments resolves to a document; an
    odd number resolves to a collection. Document operations require
    even segment count.

    Args:
        path: A slash-delimited Firestore path.

    Raises:
        ValueError: If the path is empty, contains empty segments, or
            has an odd number of segments (which would resolve to a
            collection, not a document).
    """
    if not path:
        raise ValueError("Firestore path cannot be empty.")
    parts = path.split('/')
    if any(not part for part in parts):
        raise ValueError(
            f"Firestore path contains empty segments (check for leading, "
            f"trailing, or doubled slashes): '{path}'"
        )
    if len(parts) % 2 != 0:
        raise ValueError(
            f"Document path must have an even number of segments, got "
            f"{len(parts)}: '{path}'. Firestore paths alternate "
            f"collection/document/collection/document; a path that ends "
            f"on a collection cannot be used for document operations. "
            f"Did you miss a segment, or did you mean to operate on a "
            f"collection (e.g. via get_collection)?"
        )


def _validate_collection_path(path: str) -> None:
    """Validate that a path resolves to a collection (odd segment count).

    Args:
        path: A slash-delimited Firestore path.

    Raises:
        ValueError: If the path is empty, contains empty segments, or
            has an even number of segments (which would resolve to a
            document, not a collection).
    """
    if not path:
        raise ValueError("Firestore path cannot be empty.")
    parts = path.split('/')
    if any(not part for part in parts):
        raise ValueError(
            f"Firestore path contains empty segments (check for leading, "
            f"trailing, or doubled slashes): '{path}'"
        )
    if len(parts) % 2 == 0:
        raise ValueError(
            f"Collection path must have an odd number of segments, got "
            f"{len(parts)}: '{path}'. Firestore paths alternate "
            f"collection/document/collection/document; a path that ends "
            f"on a document cannot be used for collection operations. "
            f"Did you mean to operate on a document (e.g. via "
            f"get_document or update_document)?"
        )


# === Initialization ===

def initialize_firebase(
        env_file: str | None = None,
        key_path: str | None = None,
        bucket_name: str | None = None,
        project_id: str | None = None,
        database_id: str | None = None,
    ) -> Any:
    """Initialize Firebase, unless already initialized.

    Supports Firestore Enterprise multi-database configurations
    via the ``database_id`` parameter. When provided, the database
    ID is stored module-wide so that all subsequent calls to
    ``get_document``, ``get_collection``, etc. automatically
    target the specified database.

    Args:
        env_file: Path to a ``.env`` file containing
            ``GOOGLE_APPLICATION_CREDENTIALS``.
        key_path: Path to a service account JSON key file.
        bucket_name: A Cloud Storage bucket name.
        project_id: A Firebase project ID.
        database_id: Optional Firestore database ID for
            Enterprise multi-database support. Pass ``None``
            (default) to use the ``(default)`` database.

    Returns:
        A Firestore database client instance.
    """
    global _default_database_id
    cred = None
    options = {}
    if env_file:
        config = dotenv_values(env_file)
        key_path = config.get('GOOGLE_APPLICATION_CREDENTIALS')
    if key_path:
        cred = credentials.Certificate(key_path)
    if bucket_name:
        options['storageBucket'] = bucket_name.replace('gs://', '')
    if project_id:
        options['projectId'] = project_id
    try:
        initialize_app(cred, options)
    except ValueError:
        pass
    if database_id:
        _default_database_id = database_id
    return _get_client()


# === Firestore CRUD ===

def create_reference(database: Any, path: str) -> Any:
    """Create a database reference for a given path.

    Odd-length paths (e.g. ``'users'``) resolve to collection
    references; even-length paths (e.g. ``'users/xyz'``) resolve
    to document references.

    This function does not validate path semantics; it simply walks
    the path and returns whatever reference type results. Callers
    that need a specific reference type (document or collection)
    should validate first via ``_validate_document_path`` or
    ``_validate_collection_path``.

    Args:
        database: A Firestore client instance.
        path: Slash-delimited path to a document or collection.

    Returns:
        A Firestore document or collection reference.
    """
    ref = database
    parts = path.split('/')
    for index, part in enumerate(parts):
        if index % 2:
            ref = ref.document(part)
        else:
            ref = ref.collection(part)
    return ref


def get_document(ref: str, database: Any | None = None) -> dict[str, Any]:
    """Retrieve a single Firestore document.

    Args:
        ref: Document path (e.g. ``'users/abc123'``). Must have an
            even number of segments.
        database: Optional Firestore client. Uses the default
            client if not provided.

    Returns:
        Document data as a dictionary with an ``'id'`` field.
        Returns an empty dict if the document does not exist.

    Raises:
        ValueError: If ``ref`` is not a valid document path.
    """
    _validate_document_path(ref)
    if database is None:
        database = _get_client()
    doc = create_reference(database, ref)
    data = doc.get()
    try:
        values = data.to_dict()
        if values is None:
            return {}
        return {'id': data.id, **values}
    except AttributeError:
        return {}


def get_collection(
        ref: str,
        limit: int | None = None,
        order_by: str | None = None,
        desc: bool = False,
        filters: list[dict] | None = None,
        database: Any | None = None,
        start_at: dict | None = None,
        start_after: dict | None = None,
    ) -> list[dict]:
    """Get documents from a collection.

    Args:
        ref: A collection path. Must have an odd number of segments.
        limit: Maximum number of documents to return.
        order_by: A field to order results by.
        desc: If ``True``, order descending.
        filters: List of filter dicts, each with ``'key'``,
            ``'operation'``, and ``'value'`` keys. Supported
            operators: ``==``, ``>=``, ``<=``, ``>``, ``<``,
            ``!=``, ``in``, ``not_in``, ``array_contains``,
            ``array_contains_any``.
        database: Optional Firestore client.
        start_at: Cursor dict with ``'key'`` and ``'value'``
            for ``start_at`` pagination.
        start_after: Cursor dict with ``'key'`` and ``'value'``
            for ``start_after`` pagination.

    Returns:
        A list of document dictionaries, each including an
        ``'id'`` field.

    Raises:
        ValueError: If ``ref`` is not a valid collection path.
    """
    _validate_collection_path(ref)
    docs = []

    if database is None:
        database = _get_client()

    collection = create_reference(database, ref)
    if filters is not None:
        for query_filter in filters:
            collection = collection.where(
                filter=FieldFilter(
                    query_filter['key'],
                    query_filter['operation'],
                    query_filter['value'],
                )
            )

    if order_by and desc:
        collection = collection.order_by(order_by, direction='DESCENDING')
    elif order_by:
        collection = collection.order_by(order_by)

    # Explicit __name__ tiebreaker for stable cursor pagination.
    # Firestore adds this implicitly, but declaring it matches our cursor
    # encoding (which appends the doc ID as the final sort value).
    if order_by:
        from google.cloud.firestore_v1.field_path import FieldPath
        collection = collection.order_by(
            FieldPath.document_id(),
            direction='DESCENDING' if desc else 'ASCENDING',
        )

    if start_at is not None:
        # Accept either a list of values (from cursor pagination) or a dict
        # (legacy single-field pagination). The SDK accepts both.
        collection = collection.start_at(start_at)
    if start_after is not None:
        collection = collection.start_after(start_after)

    if limit:
        collection = collection.limit(limit)

    query = collection.stream()
    for doc in query:
        data = doc.to_dict()
        docs.append({'id': doc.id, **data})

    return docs


def update_document(ref: str, values: dict, database: Any | None = None):
    """Create or update a document with merge semantics.

    Args:
        ref: A document path. Must have an even number of segments.
        values: A dictionary of field values to set.
        database: Optional Firestore client.

    Raises:
        ValueError: If ``ref`` is not a valid document path.
    """
    _validate_document_path(ref)
    if database is None:
        database = _get_client()
    doc = create_reference(database, ref)
    doc.set(values, merge=True)


def update_documents(
        refs: list[str],
        data: list[dict],
        database: Any | None = None,
    ):
    """Batch update documents with automatic sharding.

    Splits writes into batches of ``MAX_BATCH_SIZE`` (420) to
    stay safely under the Firestore 500-document batch limit.

    Args:
        refs: A list of document paths. Each must have an even
            number of segments.
        data: A list of document data dicts (same order as refs).
        database: Optional Firestore client.

    Raises:
        ValueError: If any path in ``refs`` is not a valid document
            path, or if ``refs`` and ``data`` are not the same length.
    """
    if len(refs) != len(data):
        raise ValueError(
            f"refs and data must be the same length, got "
            f"{len(refs)} refs and {len(data)} data entries."
        )
    # Validate all paths up-front so we fail before writing anything.
    # Catching path errors here is much better than committing some
    # batches and then failing partway through.
    for ref in refs:
        _validate_document_path(ref)

    if database is None:
        database = _get_client()
    ref_shards = [refs[i:i + MAX_BATCH_SIZE] for i in range(0, len(refs), MAX_BATCH_SIZE)]
    data_shards = [data[i:i + MAX_BATCH_SIZE] for i in range(0, len(data), MAX_BATCH_SIZE)]
    for shard_index, ref_shard in enumerate(ref_shards):
        data_shard = data_shards[shard_index]
        batch = database.batch()
        for index, ref in enumerate(ref_shard):
            values = data_shard[index]
            doc = create_reference(database, ref)
            batch.set(doc, values, merge=True)
        batch.commit()


def delete_document(ref: str, database: Any | None = None):
    """Delete a document.

    Args:
        ref: A document path. Must have an even number of segments.
        database: Optional Firestore client.

    Raises:
        ValueError: If ``ref`` is not a valid document path.
    """
    _validate_document_path(ref)
    if database is None:
        database = _get_client()
    doc = create_reference(database, ref)
    doc.delete()


def delete_collection(ref: str, batch_size: int = 420, database: Any | None = None):
    """Delete all documents in a collection, one batch at a time.

    Args:
        ref: A collection path. Must have an odd number of segments.
        batch_size: Documents to delete per batch (max 500).
        database: Optional Firestore client.

    Raises:
        ValueError: If ``ref`` is not a valid collection path.
    """
    _validate_collection_path(ref)
    if database is None:
        database = _get_client()
    col = create_reference(database, ref)
    docs = col.limit(batch_size).stream()
    deleted = 0
    for doc in docs:
        doc.reference.delete()
        deleted += 1
    if deleted >= batch_size:
        return delete_collection(ref, batch_size, database)


def delete_field(ref: str, field: str, database: Any | None = None):
    """Remove a field from a document.

    Args:
        ref: A document path. Must have an even number of segments.
        field: The field name to delete.
        database: Optional Firestore client.

    Raises:
        ValueError: If ``ref`` is not a valid document path.
    """
    _validate_document_path(ref)
    if database is None:
        database = _get_client()
    doc = create_reference(database, ref)
    doc.set({field: DELETE_FIELD}, merge=True)


def add_to_array(ref: str, field: str, value: Any, database: Any | None = None):
    """Append an element to an array field in a document.

    Args:
        ref: A document path. Must have an even number of segments.
        field: The array field to update.
        value: The value to append.
        database: Optional Firestore client.

    Raises:
        ValueError: If ``ref`` is not a valid document path.
    """
    _validate_document_path(ref)
    if database is None:
        database = _get_client()
    doc = create_reference(database, ref)
    doc.set({field: ArrayUnion([value])}, merge=True)


def remove_from_array(ref: str, field: str, value: Any, database: Any | None = None):
    """Remove an element from an array field in a document.

    Args:
        ref: A document path. Must have an even number of segments.
        field: The array field to update.
        value: The value to remove.
        database: Optional Firestore client.

    Raises:
        ValueError: If ``ref`` is not a valid document path.
    """
    _validate_document_path(ref)
    if database is None:
        database = _get_client()
    doc = create_reference(database, ref)
    doc.set({field: ArrayRemove([value])}, merge=True)


def increment_value(ref: str, field: str, amount: int = 1, database: Any | None = None):
    """Atomically increment a numeric field.

    Args:
        ref: A document path. Must have an even number of segments.
        field: The numeric field to increment.
        amount: The amount to increment (default 1).
        database: Optional Firestore client.

    Raises:
        ValueError: If ``ref`` is not a valid document path.
    """
    _validate_document_path(ref)
    if database is None:
        database = _get_client()
    doc = create_reference(database, ref)
    doc.set({field: Increment(amount)}, merge=True)


# === ID Generation ===

def create_id() -> str:
    """Generate a random 32-character hex document ID (UUIDv4).

    Returns a UUIDv4 in lowercase hex form with no hyphens. Random
    IDs are the recommended pattern for Firestore document keys —
    monotonically increasing IDs (timestamps, ULIDs, UUIDv7) create
    write hotspots on the most recent index shard at scale.

    To order documents by creation time, store a ``created_at``
    field on the document and order by that field.

    See: https://firebase.google.com/docs/firestore/best-practices

    Returns:
        A 32-character lowercase hex string (e.g.
        ``'a1b2c3d4e5f6...'``). Has 122 bits of entropy — collision
        probability is negligible at any practical scale.
    """
    return uuid4().hex


# === Logging ===

def create_log(
        ref: str,
        claims: dict,
        action: str,
        log_type: str,
        key: str,
        changes: Any = None,
        database: Any | None = None,
):
    """Create a standardized activity log entry in Firestore.

    Args:
        ref: Path to a collection of logs. Must have an odd number
            of segments (since a timestamped doc ID is appended to
            form the final document path).
        claims: A dict with user fields (uid, display_name, email,
            photo_url).
        action: Description of the activity that took place.
        log_type: The log category.
        key: A key to identify the action.
        changes: Optional list of changes that occurred.
        database: Optional Firestore client.

    Raises:
        ValueError: If ``ref`` is not a valid collection path.
    """
    # ``ref`` is the parent collection; the timestamped log ID is
    # appended below to form the final document path. Validate the
    # parent here so misuse is caught at the call site.
    _validate_collection_path(ref)
    now = datetime.now()
    timestamp = now.isoformat()
    log_id = now.strftime('%Y-%m-%d_%H-%M-%S')
    log_entry = {
        'action': action,
        'type': log_type,
        'key': key,
        'created_at': timestamp,
        'log_id': log_id,
        'user': claims.get('uid'),
        'user_name': claims.get('display_name'),
        'user_email': claims.get('email'),
        'user_photo_url': claims.get('photo_url'),
        'changes': changes,
    }
    update_document(f'{ref}/{log_id}', log_entry, database=database)