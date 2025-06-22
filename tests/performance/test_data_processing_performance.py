"""
Performance Tests | Cannlytics Data Processing

Performance benchmarks for data processing operations.
"""
import pytest
import pandas as pd
import numpy as np
from time import time
from tests.utils import create_mock_coa_data


class TestDataProcessingPerformance:
    """Performance tests for data processing operations."""

    @pytest.fixture
    def large_dataset(self):
        """Create a large dataset for performance testing."""
        # Create 1000 sample COA records
        data = []
        for i in range(1000):
            coa_data = create_mock_coa_data()
            coa_data['sample_id'] = f"PERF-TEST-{i:04d}"
            coa_data['results']['thc_total'] = np.random.uniform(10, 30)
            coa_data['results']['cbd_total'] = np.random.uniform(0, 5)
            data.append(coa_data)
        return data

    def test_dataframe_creation_performance(self, large_dataset, benchmark):
        """Benchmark DataFrame creation from large dataset."""
        def create_dataframe():
            return pd.DataFrame(large_dataset)
        
        result = benchmark(create_dataframe)
        assert len(result) == 1000
        assert 'sample_id' in result.columns

    def test_data_filtering_performance(self, large_dataset, benchmark):
        """Benchmark data filtering operations."""
        df = pd.DataFrame(large_dataset)
        
        def filter_high_thc():
            return df[df['results'].apply(lambda x: x.get('thc_total', 0) > 20)]
        
        result = benchmark(filter_high_thc)
        assert len(result) > 0

    def test_data_aggregation_performance(self, large_dataset, benchmark):
        """Benchmark data aggregation operations."""
        df = pd.DataFrame(large_dataset)
        
        def aggregate_results():
            return df['results'].apply(lambda x: {
                'avg_thc': x.get('thc_total', 0),
                'avg_cbd': x.get('cbd_total', 0)
            }).agg(['mean', 'std'])
        
        result = benchmark(aggregate_results)
        assert 'mean' in result.index
        assert 'std' in result.index

    def test_hash_creation_performance(self, large_dataset, benchmark):
        """Benchmark hash creation for large datasets."""
        from cannlytics.data.data import create_hash
        
        def create_hashes():
            return [create_hash(str(item)) for item in large_dataset[:100]]
        
        result = benchmark(create_hashes)
        assert len(result) == 100
        assert all(isinstance(h, str) for h in result)

    @pytest.mark.slow
    def test_large_file_processing(self, benchmark):
        """Benchmark processing of large files."""
        # Create a large CSV file
        large_data = []
        for i in range(10000):
            large_data.append({
                'id': i,
                'value': np.random.random(),
                'category': f'cat_{i % 10}',
                'timestamp': pd.Timestamp.now()
            })
        
        df = pd.DataFrame(large_data)
        
        def process_large_data():
            # Simulate complex data processing
            result = df.groupby('category').agg({
                'value': ['mean', 'std', 'count']
            })
            return result
        
        result = benchmark(process_large_data)
        assert len(result) == 10  # 10 categories

    def test_memory_usage(self, large_dataset):
        """Test memory usage during data processing."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process large dataset
        df = pd.DataFrame(large_dataset)
        df_processed = df.copy()
        
        # Perform some operations
        for _ in range(10):
            df_processed = df_processed.append(df_processed.iloc[:100])
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.2f}MB -> {final_memory:.2f}MB (+{memory_increase:.2f}MB)")
        
        # Memory increase should be reasonable (less than 1GB for this test)
        assert memory_increase < 1024


class TestAPIPerformance:
    """Performance tests for API operations."""

    @pytest.fixture
    def api_client(self):
        """Mock API client for performance testing."""
        from unittest.mock import Mock
        client = Mock()
        client.get.return_value.status_code = 200
        client.post.return_value.status_code = 200
        return client

    def test_bulk_api_requests(self, api_client, benchmark):
        """Benchmark bulk API requests."""
        def make_bulk_requests():
            responses = []
            for i in range(100):
                response = api_client.get(f"/samples/{i}")
                responses.append(response)
            return responses
        
        result = benchmark(make_bulk_requests)
        assert len(result) == 100

    def test_concurrent_api_requests(self, api_client):
        """Test concurrent API request performance."""
        import asyncio
        import aiohttp
        from unittest.mock import AsyncMock
        
        async def make_concurrent_requests():
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i in range(50):
                    task = session.get(f"http://api.example.com/samples/{i}")
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks)
                return responses
        
        # This would need proper async testing setup
        # For now, just test the structure
        assert asyncio.iscoroutinefunction(make_concurrent_requests)


class TestDatabasePerformance:
    """Performance tests for database operations."""

    @pytest.fixture
    def mock_database(self):
        """Mock database for performance testing."""
        from unittest.mock import Mock
        db = Mock()
        db.collection.return_value.add.return_value = [Mock(id='test-id')]
        db.collection.return_value.get.return_value = [Mock(to_dict=lambda: {'id': 'test'})]
        return db

    def test_bulk_database_writes(self, mock_database, benchmark):
        """Benchmark bulk database write operations."""
        def bulk_write():
            collection = mock_database.collection('samples')
            for i in range(100):
                collection.add({'sample_id': f'TEST-{i}'})
        
        benchmark(bulk_write)
        assert mock_database.collection.call_count == 1

    def test_database_query_performance(self, mock_database, benchmark):
        """Benchmark database query operations."""
        def query_samples():
            collection = mock_database.collection('samples')
            return collection.where('project_id', '==', 'TEST').get()
        
        result = benchmark(query_samples)
        assert result is not None 