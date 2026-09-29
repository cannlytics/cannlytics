"""
Tests for cannlytics.firebase.core
====================================
Covers: initialization, create_reference path routing, CRUD operations,
batch writes, collection queries with FieldFilter, ID generation, logging.
"""
from unittest.mock import MagicMock, patch, call


from cannlytics.firebase import core
from cannlytics.firebase.core import (
    MAX_BATCH_SIZE,
    _get_client,
    initialize_firebase,
    create_reference,
    get_document,
    get_collection,
    update_document,
    update_documents,
    delete_document,
    delete_field,
    add_to_array,
    remove_from_array,
    increment_value,
    create_id,
    create_log,
)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Constants                                                        ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestConstants:

    def test_max_batch_size(self):
        assert MAX_BATCH_SIZE == 420
        assert MAX_BATCH_SIZE < 500  # Must stay under Firestore limit.

# ╔══════════════════════════════════════════════════════════════════╗
# ║ _get_client and database_id routing                              ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestGetClient:

    def test_default_database_when_no_id_set(self):
        """Without a database_id, should call firestore.client() with no args."""
        with patch.object(core, '_default_database_id', None):
            with patch('cannlytics.firebase.core.firestore.client') as mock_client:
                _get_client()
                mock_client.assert_called_once_with()

    def test_enterprise_database_when_id_set(self):
        """With a database_id set, should pass it to firestore.client()."""
        with patch.object(core, '_default_database_id', 'cannlytics-enterprise'):
            with patch('cannlytics.firebase.core.firestore.client') as mock_client:
                _get_client()
                mock_client.assert_called_once_with(database_id='cannlytics-enterprise')

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Initialization                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestInitializeFirebase:

    def test_basic_init(self):
        with patch('cannlytics.firebase.core.initialize_app'):
            with patch('cannlytics.firebase.core.firestore.client') as mock_client:
                mock_client.return_value = MagicMock()
                db = initialize_firebase()
                assert db is not None

    def test_init_with_database_id(self):
        with patch('cannlytics.firebase.core.initialize_app'):
            with patch('cannlytics.firebase.core.firestore.client') as mock_client:
                mock_client.return_value = MagicMock()
                initialize_firebase(database_id='test-db')
                assert core._default_database_id == 'test-db'
        # Reset.
        core._default_database_id = None

    def test_init_with_key_path(self):
        with patch('cannlytics.firebase.core.initialize_app') as mock_init:
            with patch('cannlytics.firebase.core.credentials.Certificate') as mock_cert:
                with patch('cannlytics.firebase.core.firestore.client'):
                    mock_cert.return_value = 'mock_cred'
                    initialize_firebase(key_path='/fake/key.json')
                    mock_cert.assert_called_once_with('/fake/key.json')
                    mock_init.assert_called_once_with('mock_cred', {})

    def test_init_with_env_file(self, tmp_path):
        env_file = tmp_path / '.env'
        env_file.write_text('GOOGLE_APPLICATION_CREDENTIALS=/fake/key.json\n')
        with patch('cannlytics.firebase.core.initialize_app'):
            with patch('cannlytics.firebase.core.credentials.Certificate') as mock_cert:
                with patch('cannlytics.firebase.core.firestore.client'):
                    mock_cert.return_value = 'mock_cred'
                    initialize_firebase(env_file=str(env_file))
                    mock_cert.assert_called_once_with('/fake/key.json')

    def test_init_with_bucket_and_project(self):
        with patch('cannlytics.firebase.core.initialize_app') as mock_init:
            with patch('cannlytics.firebase.core.firestore.client'):
                initialize_firebase(bucket_name='gs://my-bucket', project_id='my-proj')
                expected_options = {'storageBucket': 'my-bucket', 'projectId': 'my-proj'}
                mock_init.assert_called_once_with(None, expected_options)

    def test_already_initialized_swallows_valueerror(self):
        """Second init should not raise."""
        with patch('cannlytics.firebase.core.initialize_app', side_effect=ValueError):
            with patch('cannlytics.firebase.core.firestore.client') as mock_client:
                mock_client.return_value = MagicMock()
                db = initialize_firebase()
                assert db is not None

# ╔══════════════════════════════════════════════════════════════════╗
# ║ create_reference — Path Routing                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCreateReference:

    def test_collection_path(self):
        """Odd-length path ('users') → collection."""
        db = MagicMock()
        create_reference(db, 'users')
        db.collection.assert_called_once_with('users')

    def test_document_path(self):
        """Even-length path ('users/xyz') → collection then document."""
        db = MagicMock()
        col_ref = MagicMock()
        db.collection.return_value = col_ref
        create_reference(db, 'users/xyz')
        db.collection.assert_called_once_with('users')
        col_ref.document.assert_called_once_with('xyz')

    def test_subcollection_path(self):
        """'users/xyz/logs' → collection/document/collection."""
        db = MagicMock()
        col_ref = MagicMock()
        doc_ref = MagicMock()
        db.collection.return_value = col_ref
        col_ref.document.return_value = doc_ref
        create_reference(db, 'users/xyz/logs')
        db.collection.assert_called_with('users')
        col_ref.document.assert_called_with('xyz')
        doc_ref.collection.assert_called_with('logs')

    def test_deep_path(self):
        """4-segment path: collection/doc/collection/doc."""
        db = MagicMock()
        c1 = MagicMock()
        d1 = MagicMock()
        c2 = MagicMock()
        db.collection.return_value = c1
        c1.document.return_value = d1
        d1.collection.return_value = c2
        create_reference(db, 'users/xyz/logs/2026-01-01')
        c2.document.assert_called_with('2026-01-01')

# ╔══════════════════════════════════════════════════════════════════╗
# ║ CRUD Operations                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestGetDocument:

    def test_returns_dict_with_id(self, mock_firestore_client):
        mock_firestore_client._data = {'users': {'xyz': {'name': 'Keegan'}}}
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            from tests.conftest import MockDocumentSnapshot
            mock_doc = MagicMock()
            mock_doc.get.return_value = MockDocumentSnapshot('xyz', {'name': 'Keegan'})
            mock_ref.return_value = mock_doc
            result = get_document('users/xyz')
            assert result['id'] == 'xyz'
            assert result['name'] == 'Keegan'

    def test_nonexistent_returns_empty_dict(self, mock_firestore_client):
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            from tests.conftest import MockDocumentSnapshot
            mock_doc = MagicMock()
            mock_doc.get.return_value = MockDocumentSnapshot('missing', None)
            mock_ref.return_value = mock_doc
            result = get_document('users/missing')
            assert result == {}

class TestUpdateDocument:

    def test_calls_set_with_merge(self, mock_firestore_client):
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            mock_doc = MagicMock()
            mock_ref.return_value = mock_doc
            update_document('users/xyz', {'name': 'Updated'})
            mock_doc.set.assert_called_once_with({'name': 'Updated'}, merge=True)

class TestDeleteDocument:

    def test_calls_delete(self, mock_firestore_client):
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            mock_doc = MagicMock()
            mock_ref.return_value = mock_doc
            delete_document('users/xyz')
            mock_doc.delete.assert_called_once()

class TestUpdateDocuments:

    def test_batch_sharding(self, mock_firestore_client):
        """Ensure batches are split at MAX_BATCH_SIZE."""
        refs = [f'col/doc{i}' for i in range(MAX_BATCH_SIZE + 5)]
        data = [{'i': i} for i in range(MAX_BATCH_SIZE + 5)]
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            mock_ref.return_value = MagicMock()
            mock_batch = MagicMock()
            mock_firestore_client.batch = MagicMock(return_value=mock_batch)
            update_documents(refs, data, database=mock_firestore_client)
            # Should commit twice: one full batch + one partial.
            assert mock_batch.commit.call_count == 2

class TestDeleteField:

    def test_sets_delete_sentinel(self, mock_firestore_client):
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            mock_doc = MagicMock()
            mock_ref.return_value = mock_doc
            delete_field('users/xyz', 'old_field')
            call_args = mock_doc.set.call_args
            assert 'old_field' in call_args[0][0]

class TestArrayOperations:

    def test_add_to_array(self, mock_firestore_client):
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            mock_doc = MagicMock()
            mock_ref.return_value = mock_doc
            add_to_array('users/xyz', 'tags', 'new_tag')
            mock_doc.set.assert_called_once()

    def test_remove_from_array(self, mock_firestore_client):
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            mock_doc = MagicMock()
            mock_ref.return_value = mock_doc
            remove_from_array('users/xyz', 'tags', 'old_tag')
            mock_doc.set.assert_called_once()

class TestIncrementValue:

    def test_increment(self, mock_firestore_client):
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            mock_doc = MagicMock()
            mock_ref.return_value = mock_doc
            increment_value('stats/counter', 'views', amount=5)
            mock_doc.set.assert_called_once()

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Collection Queries                                               ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestGetCollection:

    def test_basic_query(self, mock_firestore_client):
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            from tests.conftest import MockDocumentSnapshot, MockCollectionReference
            docs = [
                MockDocumentSnapshot('d1', {'name': 'A'}),
                MockDocumentSnapshot('d2', {'name': 'B'}),
            ]
            mock_col = MockCollectionReference(docs)
            mock_ref.return_value = mock_col
            result = get_collection('users')
            assert len(result) == 2
            assert result[0]['id'] == 'd1'

    def test_query_with_filters_uses_field_filter(self, mock_firestore_client):
        """Verify FieldFilter is used instead of positional .where()."""
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            mock_col = MagicMock()
            mock_col.where.return_value = mock_col
            mock_col.stream.return_value = iter([])
            mock_ref.return_value = mock_col
            filters = [{'key': 'state', 'operation': '==', 'value': 'ca'}]
            get_collection('results', filters=filters)
            # Check that .where() was called with filter= keyword.
            call_kwargs = mock_col.where.call_args
            assert 'filter' in call_kwargs.kwargs

    def test_query_with_limit(self, mock_firestore_client):
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            mock_col = MagicMock()
            mock_col.limit.return_value = mock_col
            mock_col.stream.return_value = iter([])
            mock_ref.return_value = mock_col
            get_collection('users', limit=10)
            mock_col.limit.assert_called_once_with(10)

    def test_query_with_order_desc(self, mock_firestore_client):
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            mock_col = MagicMock()
            mock_col.order_by.return_value = mock_col
            mock_col.stream.return_value = iter([])
            mock_ref.return_value = mock_col
            get_collection('users', order_by='name', desc=True)
            # `get_collection` also orders by `__name__` for stable cursor
        # pagination, so order_by is legitimately called twice.
        assert mock_col.order_by.call_args_list[0] == call(
            'name', direction='DESCENDING')

    def test_query_with_start_after(self, mock_firestore_client):
        with patch('cannlytics.firebase.core.create_reference') as mock_ref:
            mock_col = MagicMock()
            mock_col.start_after.return_value = mock_col
            mock_col.stream.return_value = iter([])
            mock_ref.return_value = mock_col
            get_collection('users', start_after={'key': 'name', 'value': 'Z'})
            mock_col.start_after.assert_called_once()

# ╔══════════════════════════════════════════════════════════════════╗
# ║ ID Generation                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestIdGeneration:

    def test_create_id_is_string(self):
        uid = create_id()
        assert isinstance(uid, str)
        assert len(uid) == 32  # uuid4().hex — 128 bits → 32 hex chars.

    def test_create_id_is_lowercase_hex(self):
        uid = create_id()
        assert uid == uid.lower()
        assert all(c in '0123456789abcdef' for c in uid)

    def test_create_id_uniqueness(self):
        ids = {create_id() for _ in range(1000)}
        assert len(ids) == 1000

    def test_create_id_no_hyphens(self):
        """Hex form is preferred for Firestore keys (no separator chars)."""
        uid = create_id()
        assert '-' not in uid

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Logging                                                          ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCreateLog:

    def test_creates_log_entry(self, mock_firestore_client):
        with patch('cannlytics.firebase.core.update_document') as mock_update:
            claims = {
                'uid': 'user123',
                'display_name': 'Keegan',
                'email': 'keegan@cannlytics.com',
                'photo_url': '',
            }
            create_log(
                ref='logs/api/entries',
                claims=claims,
                action='Parsed COA',
                log_type='data',
                key='api_coas',
                changes=[{'id': 'abc'}],
            )
            mock_update.assert_called_once()
            call_args = mock_update.call_args[0]
            assert call_args[0].startswith('logs/api/entries/')
            log_data = call_args[1]
            assert log_data['action'] == 'Parsed COA'
            assert log_data['user'] == 'user123'
            assert log_data['changes'] == [{'id': 'abc'}]
