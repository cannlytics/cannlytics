"""
Pytest Configuration | Cannlytics Tests

Centralized test configuration with common fixtures and utilities.
"""
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# Test data paths
TESTS_DIR = Path(__file__).parent
ASSETS_DIR = TESTS_DIR / "assets"
DATA_DIR = ASSETS_DIR / "data"


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    return DATA_DIR


@pytest.fixture(scope="session")
def temp_dir():
    """Provide temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def mock_firebase():
    """Mock Firebase client for testing."""
    with patch('cannlytics.firebase.initialize_firebase') as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_metrc():
    """Mock Metrc client for testing."""
    with patch('cannlytics.metrc.initialize_metrc') as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def sample_coa_data():
    """Sample COA data for testing."""
    return {
        'sample_id': 'TEST-SAMPLE-001',
        'sample_name': 'Test Strain',
        'test_date': '2023-01-15',
        'results': {
            'thc_total': 18.5,
            'cbd_total': 0.8,
            'moisture': 12.3
        }
    }


@pytest.fixture
def sample_instrument_data():
    """Sample instrument data for testing."""
    return {
        'sample_name': 'CAL1',
        'instrument': 'Agilent GC',
        'analysis_type': 'terpenes',
        'results': [
            {'analyte': 'alpha_pinene', 'concentration': 0.15},
            {'analyte': 'beta_pinene', 'concentration': 0.08}
        ]
    }


@pytest.fixture
def api_headers():
    """Standard API headers for testing."""
    return {
        'Authorization': 'Bearer test-api-key',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def test_org_id():
    """Test organization ID."""
    return 'test-company'


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ['TESTING'] = 'true'
    os.environ['CANNLYTICS_API_KEY'] = 'test-api-key'
    yield
    # Cleanup
    os.environ.pop('TESTING', None)
    os.environ.pop('CANNLYTICS_API_KEY', None) 