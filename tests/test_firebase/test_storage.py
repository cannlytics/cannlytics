"""
Tests for cannlytics.firebase.storage
=======================================
Covers: upload, download, list, delete, rename files, and signed URL generation.
"""
import os
from unittest.mock import MagicMock, patch


from cannlytics.firebase.storage import (
    upload_file,
    upload_files,
    download_file,
    download_files,
    get_file_url,
    list_files,
    delete_file,
    rename_file,
)

class TestUploadFile:

    def test_upload_from_filename(self, mock_storage_bucket, tmp_path):
        src = tmp_path / 'test.txt'
        src.write_text('hello')
        upload_file('remote/test.txt', source_file_name=str(src))
        blob = mock_storage_bucket.blob('remote/test.txt')
        assert blob._data == b'hello'

    def test_upload_from_string(self, mock_storage_bucket):
        upload_file('remote/data.json', data_url='{"key": 1}', content_type='application/json')
        blob = mock_storage_bucket.blob('remote/data.json')
        assert blob._data == '{"key": 1}'

class TestUploadFiles:

    def test_uploads_all_files(self, mock_storage_bucket, tmp_path):
        (tmp_path / 'a.txt').write_text('aaa')
        (tmp_path / 'b.txt').write_text('bbb')
        upload_files('remote', str(tmp_path))
        assert 'remote/a.txt' in mock_storage_bucket._blobs
        assert 'remote/b.txt' in mock_storage_bucket._blobs

    def test_skips_directories(self, mock_storage_bucket, tmp_path):
        (tmp_path / 'file.txt').write_text('data')
        (tmp_path / 'subdir').mkdir()
        upload_files('remote', str(tmp_path))
        assert 'remote/file.txt' in mock_storage_bucket._blobs
        assert 'remote/subdir' not in mock_storage_bucket._blobs

class TestDownloadFile:

    def test_download_creates_local_file(self, mock_storage_bucket, tmp_path):
        blob = mock_storage_bucket.blob('remote/test.txt')
        blob._data = b'downloaded content'
        dest = str(tmp_path / 'local.txt')
        download_file('remote/test.txt', dest)
        assert os.path.exists(dest)
        with open(dest, 'rb') as f:
            assert f.read() == b'downloaded content'

class TestDownloadFiles:

    def test_creates_local_folder(self, mock_storage_bucket, tmp_path):
        blob = mock_storage_bucket.blob('remote/file.txt')
        blob._data = b'data'
        local = str(tmp_path / 'downloads')
        with patch('cannlytics.firebase.storage.list_files', return_value=['remote/file.txt']):
            download_files('remote', local)
        assert os.path.isdir(local)

class TestGetFileUrl:

    def test_returns_signed_url(self, mock_storage_bucket):
        url = get_file_url('users/xyz/photo.jpg')
        assert 'storage.googleapis.com' in url
        assert 'sig=' in url

    def test_does_not_call_make_public(self, mock_storage_bucket):
        """Verify the security fix: make_public is NOT called."""
        blob = mock_storage_bucket.blob('test.jpg')
        blob.make_public = MagicMock()
        blob.generate_signed_url = MagicMock(return_value='https://signed.url')
        with patch('cannlytics.firebase.storage.storage.bucket', return_value=mock_storage_bucket):
            get_file_url('test.jpg')
        blob.make_public.assert_not_called()

class TestListFiles:

    def test_lists_files_with_extensions(self, mock_storage_bucket):
        mock_storage_bucket.blob('folder/a.pdf')
        mock_storage_bucket.blob('folder/b.jpg')
        mock_storage_bucket.blob('folder/')  # Directory placeholder.
        files = list_files('folder')
        file_names = [f for f in files if '.' in f]
        assert len(file_names) >= 2

class TestDeleteFile:

    def test_deletes_blob(self, mock_storage_bucket):
        mock_storage_bucket.blob('to_delete.pdf')
        delete_file('to_delete.pdf')
        assert 'to_delete.pdf' not in mock_storage_bucket._blobs

class TestRenameFile:

    def test_renames_blob(self, mock_storage_bucket):
        mock_storage_bucket.blob('folder/old.pdf')
        rename_file('folder', 'old.pdf', 'new.pdf')
        assert 'new.pdf' in mock_storage_bucket._blobs


class TestSignedUrlCredentials:
    """`get_file_url` on Cloud Run, where credentials hold only a token."""

    def _bucket_for(self, credentials):
        blob = MagicMock()
        blob.client._credentials = credentials
        blob.generate_signed_url.return_value = 'https://signed.example/x'
        bucket = MagicMock()
        bucket.blob.return_value = blob
        return bucket, blob

    def test_token_only_credentials_sign_through_iam(self):
        import google.auth.credentials

        class TokenOnly(google.auth.credentials.Credentials):
            def __init__(self):
                super().__init__()
                self.service_account_email, self.refreshes = 'default', 0

            def refresh(self, request):
                self.token, self.refreshes = 'token-123', self.refreshes + 1
                self.service_account_email = 'site@cannlytics.iam.gserviceaccount.com'

        credentials = TokenOnly()
        bucket, blob = self._bucket_for(credentials)
        with patch('cannlytics.firebase.storage.storage.bucket', return_value=bucket):
            assert get_file_url('users/x/coa.pdf') == 'https://signed.example/x'
        kwargs = blob.generate_signed_url.call_args.kwargs
        assert kwargs['service_account_email'] == 'site@cannlytics.iam.gserviceaccount.com'
        assert kwargs['access_token'] == 'token-123' and credentials.refreshes == 1

    def test_credentials_with_a_key_sign_locally(self):
        import google.auth.credentials

        class WithKey(google.auth.credentials.Credentials, google.auth.credentials.Signing):
            def refresh(self, request):
                pass

            def sign_bytes(self, message):
                return b'signature'

            @property
            def signer_email(self):
                return 'key@cannlytics.iam.gserviceaccount.com'

            @property
            def signer(self):
                return None

        bucket, blob = self._bucket_for(WithKey())
        with patch('cannlytics.firebase.storage.storage.bucket', return_value=bucket):
            get_file_url('users/x/coa.pdf')
        assert 'access_token' not in blob.generate_signed_url.call_args.kwargs
