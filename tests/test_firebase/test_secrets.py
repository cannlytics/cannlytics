"""
Tests for cannlytics.firebase.secrets
=======================================
Covers: create_secret, add_secret_version, access_secret_version.
All google.cloud.secretmanager calls are mocked.
"""
from unittest.mock import MagicMock, patch

import pytest

from cannlytics.firebase.secrets import (
    create_secret,
    add_secret_version,
    access_secret_version,
)

MOCK_SM = 'cannlytics.firebase.secrets.secretmanager.SecretManagerServiceClient'


class TestCreateSecret:

    @patch(MOCK_SM)
    def test_creates_and_returns_name(self, MockSM):
        client = MockSM.return_value
        mock_response = MagicMock()
        mock_response.name = 'projects/p/secrets/s'
        client.create_secret.return_value = mock_response
        result = create_secret('my-project', 'my-secret', {'replication': {'automatic': {}}})
        assert result == 'projects/p/secrets/s'
        client.create_secret.assert_called_once()


class TestAddSecretVersion:

    @patch(MOCK_SM)
    def test_adds_version(self, MockSM):
        client = MockSM.return_value
        mock_response = MagicMock()
        mock_response.name = 'projects/p/secrets/s/versions/1'
        client.add_secret_version.return_value = mock_response
        result = add_secret_version('my-project', 'my-secret', 'super-secret-value')
        assert 'versions/1' in result
        call_args = client.add_secret_version.call_args
        assert call_args[1]['payload']['data'] == b'super-secret-value'


class TestAccessSecretVersion:

    @patch(MOCK_SM)
    def test_accesses_latest(self, MockSM):
        client = MockSM.return_value
        mock_response = MagicMock()
        mock_response.payload.data = b'my-secret-value'
        client.access_secret_version.return_value = mock_response
        result = access_secret_version('my-project', 'my-secret')
        assert result == 'my-secret-value'

    @patch(MOCK_SM)
    def test_accesses_specific_version(self, MockSM):
        client = MockSM.return_value
        mock_response = MagicMock()
        mock_response.payload.data = b'v2-value'
        client.access_secret_version.return_value = mock_response
        result = access_secret_version('my-project', 'my-secret', version_id='2')
        assert result == 'v2-value'
        call_args = client.access_secret_version.call_args[0][0]
        assert 'versions/2' in call_args['name']
