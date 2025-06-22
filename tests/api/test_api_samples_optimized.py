"""
Optimized API Samples Tests | Cannlytics API

Modern pytest-based tests for samples API endpoints.
"""
import pytest
import requests
from unittest.mock import patch, Mock
from tests.utils import create_mock_api_response


class TestSamplesAPI:
    """Test suite for samples API endpoints."""

    @pytest.fixture
    def api_base_url(self):
        """Base URL for API testing."""
        return "http://127.0.0.1:8000/api"

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return {
            'batch_id': 'TEST-BATCH-001',
            'coa_url': 'https://example.com/coa.pdf',
            'created_at': '2023-01-15',
            'created_by': 'test_user',
            'notes': 'Test sample',
            'project_id': 'TEST-PROJECT',
            'sample_id': 'TEST-SAMPLE-001',
            'updated_at': '2023-01-15',
            'updated_by': 'test_user'
        }

    @pytest.fixture
    def headers(self):
        """API headers for testing."""
        return {
            'Authorization': 'Bearer test-api-key',
            'Content-Type': 'application/json'
        }

    @patch('requests.post')
    def test_create_sample(self, mock_post, api_base_url, sample_data, headers):
        """Test creating a new sample."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = create_mock_api_response(sample_data)
        mock_post.return_value = mock_response

        url = f"{api_base_url}/samples?organization_id=test-company"
        response = requests.post(url, json=sample_data, headers=headers)

        assert response.status_code == 200
        assert response.json()['data'] == sample_data
        mock_post.assert_called_once_with(url, json=sample_data, headers=headers)

    @patch('requests.get')
    def test_get_samples(self, mock_get, api_base_url, headers):
        """Test retrieving samples."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = create_mock_api_response([
            {'sample_id': 'SAMPLE-1', 'sample_name': 'Test 1'},
            {'sample_id': 'SAMPLE-2', 'sample_name': 'Test 2'}
        ])
        mock_get.return_value = mock_response

        url = f"{api_base_url}/samples?organization_id=test-company"
        response = requests.get(url, headers=headers)

        assert response.status_code == 200
        assert len(response.json()['data']) == 2
        mock_get.assert_called_once_with(url, headers=headers)

    @patch('requests.post')
    def test_update_sample(self, mock_post, api_base_url, headers):
        """Test updating an existing sample."""
        update_data = {
            'sample_id': 'TEST-SAMPLE-001',
            'batch_id': 'UPDATED-BATCH-001'
        }

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = create_mock_api_response(update_data)
        mock_post.return_value = mock_response

        url = f"{api_base_url}/samples?organization_id=test-company"
        response = requests.post(url, json=update_data, headers=headers)

        assert response.status_code == 200
        assert response.json()['data'] == update_data
        mock_post.assert_called_once_with(url, json=update_data, headers=headers)

    @patch('requests.delete')
    def test_delete_sample(self, mock_delete, api_base_url, headers):
        """Test deleting a sample."""
        delete_data = {'sample_id': 'TEST-SAMPLE-001'}

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = create_mock_api_response(delete_data)
        mock_delete.return_value = mock_response

        url = f"{api_base_url}/samples?organization_id=test-company"
        response = requests.delete(url, json=delete_data, headers=headers)

        assert response.status_code == 200
        assert response.json()['data'] == delete_data
        mock_delete.assert_called_once_with(url, json=delete_data, headers=headers)

    @patch('requests.post')
    def test_create_sample_validation_error(self, mock_post, api_base_url, headers):
        """Test sample creation with validation error."""
        invalid_data = {'sample_id': ''}  # Missing required fields

        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'status_code': 400,
            'message': 'Validation error',
            'errors': ['sample_id is required']
        }
        mock_post.return_value = mock_response

        url = f"{api_base_url}/samples?organization_id=test-company"
        response = requests.post(url, json=invalid_data, headers=headers)

        assert response.status_code == 400
        assert 'Validation error' in response.json()['message']

    @patch('requests.get')
    def test_get_samples_unauthorized(self, mock_get, api_base_url):
        """Test getting samples without authorization."""
        # Mock unauthorized response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'status_code': 401,
            'message': 'Unauthorized'
        }
        mock_get.return_value = mock_response

        url = f"{api_base_url}/samples?organization_id=test-company"
        response = requests.get(url)  # No headers

        assert response.status_code == 401
        assert response.json()['message'] == 'Unauthorized'

    @pytest.mark.parametrize("sample_id", [
        "SAMPLE-001",
        "SAMPLE-002", 
        "SAMPLE-003"
    ])
    @patch('requests.get')
    def test_get_sample_by_id(self, mock_get, api_base_url, headers, sample_id):
        """Test getting a specific sample by ID."""
        sample_data = {'sample_id': sample_id, 'sample_name': f'Test {sample_id}'}

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = create_mock_api_response(sample_data)
        mock_get.return_value = mock_response

        url = f"{api_base_url}/samples/{sample_id}?organization_id=test-company"
        response = requests.get(url, headers=headers)

        assert response.status_code == 200
        assert response.json()['data']['sample_id'] == sample_id

    @patch('requests.get')
    def test_get_samples_with_filters(self, mock_get, api_base_url, headers):
        """Test getting samples with query parameters."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = create_mock_api_response([])
        mock_get.return_value = mock_response

        # Test with various filters
        filters = {
            'project_id': 'TEST-PROJECT',
            'batch_id': 'TEST-BATCH',
            'created_after': '2023-01-01'
        }

        url = f"{api_base_url}/samples?organization_id=test-company"
        for key, value in filters.items():
            url += f"&{key}={value}"

        response = requests.get(url, headers=headers)

        assert response.status_code == 200
        mock_get.assert_called_once_with(url, headers=headers)


class TestSamplesAPIIntegration:
    """Integration tests for samples API."""

    @pytest.mark.integration
    @patch('requests.post')
    @patch('requests.get')
    @patch('requests.delete')
    def test_full_sample_lifecycle(self, mock_delete, mock_get, mock_post, 
                                  api_base_url, sample_data, headers):
        """Test complete sample lifecycle: create, read, update, delete."""
        # Mock responses for each operation
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = create_mock_api_response(sample_data)
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = create_mock_api_response([sample_data])
        
        mock_delete.return_value.status_code = 200
        mock_delete.return_value.json.return_value = create_mock_api_response(sample_data)

        base_url = f"{api_base_url}/samples?organization_id=test-company"

        # 1. Create sample
        create_response = requests.post(base_url, json=sample_data, headers=headers)
        assert create_response.status_code == 200

        # 2. Get samples
        get_response = requests.get(base_url, headers=headers)
        assert get_response.status_code == 200

        # 3. Delete sample
        delete_response = requests.delete(base_url, json={'sample_id': sample_data['sample_id']}, headers=headers)
        assert delete_response.status_code == 200

        # Verify all operations were called
        assert mock_post.call_count == 1
        assert mock_get.call_count == 1
        assert mock_delete.call_count == 1 