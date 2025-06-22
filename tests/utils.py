"""
Test Utilities | Cannlytics Tests

Common utilities and helper functions for testing.
"""
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd


def create_temp_file(content: str, suffix: str = '.txt') -> str:
    """Create a temporary file with given content."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return path


def create_temp_excel(data: List[Dict[str, Any]], filename: str = None) -> str:
    """Create a temporary Excel file with test data."""
    if filename is None:
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
    else:
        path = tempfile.mktemp(suffix='.xlsx')
    
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
    return path


def create_temp_pdf(content: str = "Test PDF content") -> str:
    """Create a temporary PDF file for testing."""
    # This is a simplified version - in practice you'd use a PDF library
    fd, path = tempfile.mkstemp(suffix='.pdf')
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return path


def load_test_data(filename: str) -> Dict[str, Any]:
    """Load test data from JSON file."""
    data_path = Path(__file__).parent / "assets" / "data" / filename
    with open(data_path, 'r') as f:
        return json.load(f)


def assert_dataframe_equals(df1: pd.DataFrame, df2: pd.DataFrame, 
                           check_dtypes: bool = False) -> None:
    """Assert two DataFrames are equal with helpful error messages."""
    pd.testing.assert_frame_equal(
        df1, df2, 
        check_dtypes=check_dtypes,
        check_index_type=False,
        check_column_type=False
    )


def create_mock_coa_data() -> Dict[str, Any]:
    """Create mock COA data for testing."""
    return {
        'sample_id': 'TEST-001',
        'sample_name': 'Test Strain',
        'test_date': '2023-01-15',
        'lab_name': 'Test Lab',
        'results': {
            'thc_total': 18.5,
            'cbd_total': 0.8,
            'moisture': 12.3,
            'terpenes': {
                'alpha_pinene': 0.15,
                'beta_pinene': 0.08,
                'myrcene': 0.25
            }
        }
    }


def create_mock_instrument_data() -> Dict[str, Any]:
    """Create mock instrument data for testing."""
    return {
        'sample_name': 'CAL1',
        'instrument': 'Agilent GC',
        'analysis_type': 'terpenes',
        'sequence_number': '001',
        'results': [
            {'analyte': 'alpha_pinene', 'concentration': 0.15, 'units': 'mg/g'},
            {'analyte': 'beta_pinene', 'concentration': 0.08, 'units': 'mg/g'},
            {'analyte': 'myrcene', 'concentration': 0.25, 'units': 'mg/g'}
        ]
    }


def create_mock_api_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Create mock API response for testing."""
    return {
        'status_code': status_code,
        'data': data,
        'message': 'Success' if status_code == 200 else 'Error'
    }


def cleanup_temp_files(*file_paths: str) -> None:
    """Clean up temporary files created during testing."""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass  # File might already be deleted 