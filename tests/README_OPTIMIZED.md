# Optimized Testing Guide | Cannlytics

This document outlines the optimized testing strategy for the Cannlytics project, including best practices, tools, and examples.

## 🚀 Quick Start

### Install Testing Dependencies
```bash
pip install -r tests/requirements.txt
```

### Run Tests
```bash
# Run all tests
python run_tests.py --type all

# Run unit tests only
python run_tests.py --type unit

# Run with coverage
python run_tests.py --type all --coverage

# Run in parallel
python run_tests.py --type all --parallel
```

## 📁 Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── utils.py                    # Test utilities and helpers
├── requirements.txt            # Testing dependencies
├── api/                        # API endpoint tests
│   ├── test_api_samples_optimized.py
│   └── lims/
├── cannlytics/                 # Core library tests
│   ├── data/
│   │   └── test_coas_optimized.py
│   ├── lims/
│   └── utils/
├── performance/                # Performance benchmarks
│   └── test_data_processing_performance.py
└── assets/                     # Test data files
    ├── coas/
    ├── instruments/
    └── data/
```

## 🧪 Test Categories

### 1. Unit Tests (`@pytest.mark.unit`)
- Test individual functions and methods
- Use mocks for external dependencies
- Fast execution (< 1 second per test)

### 2. Integration Tests (`@pytest.mark.integration`)
- Test component interactions
- May use real external services
- Slower execution (1-10 seconds per test)

### 3. API Tests (`@pytest.mark.api`)
- Test REST API endpoints
- Mock external services
- Test request/response cycles

### 4. Data Tests (`@pytest.mark.data`)
- Test data processing operations
- Use sample datasets
- Test data transformations

### 5. Performance Tests (`@pytest.mark.slow`)
- Benchmark critical operations
- Test memory usage
- Identify performance bottlenecks

## 🔧 Testing Tools

### Pytest Configuration
- **pytest.ini**: Global pytest settings
- **conftest.py**: Shared fixtures and configuration
- **Markers**: Categorize tests for selective execution

### Test Utilities
- **utils.py**: Common helper functions
- **Mock data generators**: Create realistic test data
- **File utilities**: Handle temporary files and cleanup

### Coverage Reporting
- HTML coverage reports in `htmlcov/`
- XML reports for CI/CD integration
- Terminal output with missing line coverage

## 📊 Test Data Management

### Mock Data
```python
from tests.utils import create_mock_coa_data, create_mock_instrument_data

# Create realistic test data
coa_data = create_mock_coa_data()
instrument_data = create_mock_instrument_data()
```

### Test Assets
- **COA PDFs**: Sample certificates of analysis
- **Instrument data**: Excel files from lab instruments
- **API responses**: Mock API response data

### Temporary Files
```python
import tempfile
from pathlib import Path

# Use pytest's tmp_path fixture
def test_file_processing(tmp_path):
    test_file = tmp_path / "test.csv"
    # Test file operations
    # Files automatically cleaned up after test
```

## 🎯 Best Practices

### 1. Test Organization
- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Mocking Strategy
```python
from unittest.mock import patch, Mock

@patch('cannlytics.firebase.initialize_firebase')
def test_firebase_integration(mock_firebase):
    mock_firebase.return_value = Mock()
    # Test with mocked Firebase
```

### 3. Fixture Usage
```python
@pytest.fixture
def sample_data():
    """Provide test data to multiple tests."""
    return create_mock_coa_data()

def test_processing(sample_data):
    # Use the fixture data
    result = process_data(sample_data)
    assert result is not None
```

### 4. Error Testing
```python
def test_error_handling():
    with pytest.raises(ValueError):
        function_that_raises_error()
```

### 5. Performance Testing
```python
def test_performance(benchmark):
    def slow_operation():
        # Operation to benchmark
        return result
    
    result = benchmark(slow_operation)
    assert result is not None
```

## 🔄 Migration Guide

### From Old Test Format
1. **Convert manual scripts** to pytest functions
2. **Add proper fixtures** instead of global variables
3. **Use mocking** instead of real external services
4. **Add test markers** for categorization
5. **Implement proper cleanup** with fixtures

### Example Migration
```python
# Old format
if __name__ == '__main__':
    test_data = load_test_data()
    result = process_data(test_data)
    print('Test passed')

# New format
@pytest.fixture
def test_data():
    return load_test_data()

def test_process_data(test_data):
    result = process_data(test_data)
    assert result is not None
```

## 📈 Performance Optimization

### 1. Parallel Execution
```bash
# Run tests in parallel
pytest -n auto
```

### 2. Test Selection
```bash
# Run only fast tests
pytest -m "not slow"

# Run specific test categories
pytest -m "unit or integration"
```

### 3. Coverage Optimization
```bash
# Generate coverage report
pytest --cov=cannlytics --cov-report=html
```

## 🚨 Common Issues

### 1. Import Errors
- Ensure `PYTHONPATH` includes project root
- Use relative imports within test modules
- Check `conftest.py` for path setup

### 2. Mock Configuration
- Mock at the correct level (module vs function)
- Use `autospec=True` for better mock behavior
- Clean up mocks in test teardown

### 3. Test Data Issues
- Use unique identifiers for test data
- Clean up temporary files
- Avoid hardcoded paths

## 📋 Test Checklist

- [ ] Tests cover all critical functionality
- [ ] Error conditions are tested
- [ ] Performance benchmarks included
- [ ] Mock external dependencies
- [ ] Use descriptive test names
- [ ] Include proper assertions
- [ ] Clean up resources
- [ ] Add appropriate markers
- [ ] Generate coverage reports
- [ ] Document complex test scenarios

## 🔗 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/) 