"""
Tests for cannlytics.ai.embeddings
=====================================
Covers: create_embedding, get_embedding, get_results_embedding.
All OpenAI and Firebase calls are mocked.
"""
from unittest.mock import MagicMock, patch

import pytest

from cannlytics.ai.embeddings import (
    create_embedding,
    get_embedding,
    get_results_embedding,
)


class TestCreateEmbedding:

    def test_returns_list_of_floats(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_response
        result = create_embedding('test text', client=mock_client)
        assert result == [0.1, 0.2, 0.3]

    def test_strips_newlines(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.5])]
        mock_client.embeddings.create.return_value = mock_response
        create_embedding('text\nwith\nnewlines', client=mock_client)
        call_args = mock_client.embeddings.create.call_args
        text_arg = call_args[1]['input'][0]
        assert '\n' not in text_arg


class TestGetEmbedding:

    @patch('cannlytics.ai.embeddings.initialize_firebase')
    @patch('cannlytics.ai.embeddings.get_document')
    @patch('cannlytics.ai.embeddings.update_document')
    def test_creates_new_when_not_cached(self, mock_update, mock_get_doc, mock_init):
        mock_init.return_value = MagicMock()
        mock_get_doc.return_value = {}  # Not in Firestore.
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2])]
        mock_client.embeddings.create.return_value = mock_response
        result = get_embedding('new text', client=mock_client, use_db=False)
        assert result == [0.1, 0.2]

    def test_returns_from_cache(self):
        mock_cache = MagicMock()
        mock_cache.get.return_value = {'embedding': [0.5, 0.6, 0.7]}
        result = get_embedding('cached text', cache=mock_cache, use_db=False)
        assert result == [0.5, 0.6, 0.7]


class TestGetResultsEmbedding:

    def test_basic_embedding(self):
        results = {'thc': 25.0, 'cbd': 0.5, 'myrcene': 0.8}
        analytes = ['thc', 'cbd', 'myrcene', 'limonene']
        embedding = get_results_embedding(results, analytes)
        assert embedding == [25.0, 0.5, 0.8, 0.0]

    def test_missing_analytes_default_zero(self):
        results = {'thc': 20.0}
        analytes = ['thc', 'cbd', 'cbn']
        embedding = get_results_embedding(results, analytes)
        assert embedding == [20.0, 0.0, 0.0]

    def test_nan_values_become_zero(self):
        import math
        results = {'thc': float('nan'), 'cbd': 1.0}
        analytes = ['thc', 'cbd']
        embedding = get_results_embedding(results, analytes)
        assert embedding[0] == 0.0
        assert embedding[1] == 1.0

    def test_string_values_converted(self):
        results = {'thc': '25.5%', 'cbd': '0.3'}
        analytes = ['thc', 'cbd']
        embedding = get_results_embedding(results, analytes)
        assert isinstance(embedding[0], float)
