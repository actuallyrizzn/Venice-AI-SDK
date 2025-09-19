"""
Comprehensive unit tests for the embeddings module.
"""

import pytest
import math
from unittest.mock import patch, MagicMock
from venice_sdk.embeddings import (
    Embedding, EmbeddingResult, EmbeddingsAPI, EmbeddingSimilarity,
    SemanticSearch, EmbeddingClustering,
    generate_embedding, calculate_similarity, generate_embeddings
)
from venice_sdk.errors import VeniceAPIError, EmbeddingError


class TestEmbeddingComprehensive:
    """Comprehensive test suite for Embedding class."""

    def test_embedding_initialization(self):
        """Test Embedding initialization with all parameters."""
        embedding_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        embedding = Embedding(
            embedding=embedding_vector,
            index=0,
            object="embedding"
        )
        
        assert embedding.embedding == embedding_vector
        assert embedding.index == 0
        assert embedding.object == "embedding"

    def test_embedding_initialization_with_defaults(self):
        """Test Embedding initialization with default values."""
        embedding_vector = [0.1, 0.2, 0.3]
        embedding = Embedding(embedding=embedding_vector, index=1)
        
        assert embedding.embedding == embedding_vector
        assert embedding.index == 1
        assert embedding.object == "embedding"

    def test_embedding_length(self):
        """Test Embedding length method."""
        embedding_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        embedding = Embedding(embedding=embedding_vector, index=0)
        
        assert len(embedding) == 5

    def test_embedding_magnitude(self):
        """Test Embedding magnitude calculation."""
        embedding_vector = [3.0, 4.0]  # 3-4-5 triangle
        embedding = Embedding(embedding=embedding_vector, index=0)
        
        magnitude = embedding.magnitude()
        assert abs(magnitude - 5.0) < 1e-10

    def test_embedding_magnitude_zero_vector(self):
        """Test Embedding magnitude with zero vector."""
        embedding_vector = [0.0, 0.0, 0.0]
        embedding = Embedding(embedding=embedding_vector, index=0)
        
        magnitude = embedding.magnitude()
        assert magnitude == 0.0

    def test_embedding_normalize(self):
        """Test Embedding normalization."""
        embedding_vector = [3.0, 4.0]  # 3-4-5 triangle
        embedding = Embedding(embedding=embedding_vector, index=0)
        
        normalized = embedding.normalize()
        expected = [3.0/5.0, 4.0/5.0]
        
        for i, (actual, exp) in enumerate(zip(normalized, expected)):
            assert abs(actual - exp) < 1e-10

    def test_embedding_normalize_zero_vector(self):
        """Test Embedding normalization with zero vector."""
        embedding_vector = [0.0, 0.0, 0.0]
        embedding = Embedding(embedding=embedding_vector, index=0)
        
        normalized = embedding.normalize()
        assert normalized == embedding_vector  # Should return original

    def test_embedding_equality(self):
        """Test Embedding equality comparison."""
        emb1 = Embedding([0.1, 0.2], 0, "embedding")
        emb2 = Embedding([0.1, 0.2], 0, "embedding")
        emb3 = Embedding([0.1, 0.3], 0, "embedding")
        
        assert emb1 == emb2
        assert emb1 != emb3

    def test_embedding_string_representation(self):
        """Test Embedding string representation."""
        embedding = Embedding([0.1, 0.2], 0)
        emb_str = str(embedding)
        
        assert "Embedding" in emb_str


class TestEmbeddingResultComprehensive:
    """Comprehensive test suite for EmbeddingResult class."""

    def test_embedding_result_initialization(self):
        """Test EmbeddingResult initialization with all parameters."""
        embeddings = [
            Embedding([0.1, 0.2], 0),
            Embedding([0.3, 0.4], 1)
        ]
        usage = {"prompt_tokens": 10, "total_tokens": 10}
        
        result = EmbeddingResult(
            embeddings=embeddings,
            model="text-embedding-ada-002",
            usage=usage,
            object="list"
        )
        
        assert result.embeddings == embeddings
        assert result.model == "text-embedding-ada-002"
        assert result.usage == usage
        assert result.object == "list"

    def test_embedding_result_initialization_with_defaults(self):
        """Test EmbeddingResult initialization with default values."""
        embeddings = [Embedding([0.1, 0.2], 0)]
        
        result = EmbeddingResult(
            embeddings=embeddings,
            model="text-embedding-ada-002"
        )
        
        assert result.embeddings == embeddings
        assert result.model == "text-embedding-ada-002"
        assert result.usage is None
        assert result.object == "list"

    def test_embedding_result_length(self):
        """Test EmbeddingResult length method."""
        embeddings = [
            Embedding([0.1, 0.2], 0),
            Embedding([0.3, 0.4], 1),
            Embedding([0.5, 0.6], 2)
        ]
        result = EmbeddingResult(embeddings=embeddings, model="test")
        
        assert len(result) == 3

    def test_embedding_result_getitem(self):
        """Test EmbeddingResult getitem method."""
        embeddings = [
            Embedding([0.1, 0.2], 0),
            Embedding([0.3, 0.4], 1)
        ]
        result = EmbeddingResult(embeddings=embeddings, model="test")
        
        assert result[0] == embeddings[0]
        assert result[1] == embeddings[1]

    def test_embedding_result_iteration(self):
        """Test EmbeddingResult iteration."""
        embeddings = [
            Embedding([0.1, 0.2], 0),
            Embedding([0.3, 0.4], 1)
        ]
        result = EmbeddingResult(embeddings=embeddings, model="test")
        
        iterated = list(result)
        assert iterated == embeddings

    def test_embedding_result_get_embedding(self):
        """Test EmbeddingResult get_embedding method."""
        embeddings = [
            Embedding([0.1, 0.2], 0),
            Embedding([0.3, 0.4], 1)
        ]
        result = EmbeddingResult(embeddings=embeddings, model="test")
        
        embedding = result.get_embedding(0)
        assert embedding == [0.1, 0.2]
        
        embedding = result.get_embedding(1)
        assert embedding == [0.3, 0.4]

    def test_embedding_result_get_embedding_index_error(self):
        """Test EmbeddingResult get_embedding with invalid index."""
        embeddings = [Embedding([0.1, 0.2], 0)]
        result = EmbeddingResult(embeddings=embeddings, model="test")
        
        with pytest.raises(IndexError, match="Index 1 out of range for 1 embeddings"):
            result.get_embedding(1)

    def test_embedding_result_get_all_embeddings(self):
        """Test EmbeddingResult get_all_embeddings method."""
        embeddings = [
            Embedding([0.1, 0.2], 0),
            Embedding([0.3, 0.4], 1)
        ]
        result = EmbeddingResult(embeddings=embeddings, model="test")
        
        all_embeddings = result.get_all_embeddings()
        assert all_embeddings == [[0.1, 0.2], [0.3, 0.4]]


class TestEmbeddingsAPIComprehensive:
    """Comprehensive test suite for EmbeddingsAPI class."""

    def test_embeddings_api_initialization(self, mock_client):
        """Test EmbeddingsAPI initialization."""
        api = EmbeddingsAPI(mock_client)
        assert api.client == mock_client

    def test_generate_single_text(self, mock_client):
        """Test generating embeddings for single text."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "embedding": [0.1, 0.2, 0.3],
                    "index": 0,
                    "object": "embedding"
                }
            ],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        api = EmbeddingsAPI(mock_client)
        result = api.generate("Hello world")
        
        assert isinstance(result, EmbeddingResult)
        assert len(result) == 1
        assert result.model == "text-embedding-ada-002"
        assert result.get_embedding(0) == [0.1, 0.2, 0.3]

    def test_generate_multiple_texts(self, mock_client):
        """Test generating embeddings for multiple texts."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "embedding": [0.1, 0.2, 0.3],
                    "index": 0,
                    "object": "embedding"
                },
                {
                    "embedding": [0.4, 0.5, 0.6],
                    "index": 1,
                    "object": "embedding"
                }
            ],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 10, "total_tokens": 10},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        api = EmbeddingsAPI(mock_client)
        result = api.generate(["Hello", "World"])
        
        assert isinstance(result, EmbeddingResult)
        assert len(result) == 2
        assert result.get_embedding(0) == [0.1, 0.2, 0.3]
        assert result.get_embedding(1) == [0.4, 0.5, 0.6]

    def test_generate_with_all_parameters(self, mock_client):
        """Test generating embeddings with all parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2], "index": 0, "object": "embedding"}],
            "model": "text-embedding-3-large",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        api = EmbeddingsAPI(mock_client)
        result = api.generate(
            input_text="Hello world",
            model="text-embedding-3-large",
            encoding_format="float",
            user="test-user",
            custom_param="value"
        )
        
        assert result.model == "text-embedding-3-large"
        mock_client.post.assert_called_once_with("/embeddings/generate", data={
            "model": "text-embedding-3-large",
            "input": "Hello world",
            "encoding_format": "float",
            "user": "test-user",
            "custom_param": "value"
        })

    def test_generate_invalid_response(self, mock_client):
        """Test generating embeddings with invalid response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.post.return_value = mock_response
        
        api = EmbeddingsAPI(mock_client)
        
        with pytest.raises(EmbeddingError, match="Invalid response format from embeddings API"):
            api.generate("Hello world")

    def test_generate_single(self, mock_client):
        """Test generate_single method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2, 0.3], "index": 0, "object": "embedding"}],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        api = EmbeddingsAPI(mock_client)
        embedding = api.generate_single("Hello world")
        
        assert embedding == [0.1, 0.2, 0.3]

    def test_generate_single_with_parameters(self, mock_client):
        """Test generate_single method with parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2], "index": 0, "object": "embedding"}],
            "model": "text-embedding-3-large",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        api = EmbeddingsAPI(mock_client)
        embedding = api.generate_single("Hello world", model="text-embedding-3-large")
        
        assert embedding == [0.1, 0.2]

    def test_generate_batch(self, mock_client):
        """Test generate_batch method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1, 0.2], "index": 0, "object": "embedding"},
                {"embedding": [0.3, 0.4], "index": 1, "object": "embedding"}
            ],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 10, "total_tokens": 10},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        api = EmbeddingsAPI(mock_client)
        texts = ["Hello", "World", "Test", "Batch"]
        embeddings = api.generate_batch(texts, batch_size=2)
        
        assert len(embeddings) == 4
        assert embeddings[0] == [0.1, 0.2]
        assert embeddings[1] == [0.3, 0.4]
        assert embeddings[2] == [0.1, 0.2]  # Second batch
        assert embeddings[3] == [0.3, 0.4]  # Second batch

    def test_generate_batch_single_batch(self, mock_client):
        """Test generate_batch method with single batch."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1, 0.2], "index": 0, "object": "embedding"},
                {"embedding": [0.3, 0.4], "index": 1, "object": "embedding"}
            ],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 10, "total_tokens": 10},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        api = EmbeddingsAPI(mock_client)
        texts = ["Hello", "World"]
        embeddings = api.generate_batch(texts, batch_size=10)
        
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2]
        assert embeddings[1] == [0.3, 0.4]

    def test_generate_batch_empty_list(self, mock_client):
        """Test generate_batch method with empty list."""
        api = EmbeddingsAPI(mock_client)
        embeddings = api.generate_batch([])
        
        assert embeddings == []


class TestEmbeddingSimilarityComprehensive:
    """Comprehensive test suite for EmbeddingSimilarity class."""

    def test_cosine_similarity_identical_vectors(self):
        """Test cosine similarity with identical vectors."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        similarity = EmbeddingSimilarity.cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 1e-10

    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity with orthogonal vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        
        similarity = EmbeddingSimilarity.cosine_similarity(vec1, vec2)
        assert abs(similarity - 0.0) < 1e-10

    def test_cosine_similarity_opposite_vectors(self):
        """Test cosine similarity with opposite vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [-1.0, 0.0]
        
        similarity = EmbeddingSimilarity.cosine_similarity(vec1, vec2)
        assert abs(similarity - (-1.0)) < 1e-10

    def test_cosine_similarity_zero_vectors(self):
        """Test cosine similarity with zero vectors."""
        vec1 = [0.0, 0.0]
        vec2 = [1.0, 0.0]
        
        similarity = EmbeddingSimilarity.cosine_similarity(vec1, vec2)
        assert similarity == 0.0

    def test_cosine_similarity_different_dimensions(self):
        """Test cosine similarity with different dimension vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        with pytest.raises(ValueError, match="Embeddings must have the same dimension"):
            EmbeddingSimilarity.cosine_similarity(vec1, vec2)

    def test_euclidean_distance_identical_vectors(self):
        """Test Euclidean distance with identical vectors."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.0, 2.0, 3.0]
        
        distance = EmbeddingSimilarity.euclidean_distance(vec1, vec2)
        assert distance == 0.0

    def test_euclidean_distance_different_vectors(self):
        """Test Euclidean distance with different vectors."""
        vec1 = [0.0, 0.0]
        vec2 = [3.0, 4.0]
        
        distance = EmbeddingSimilarity.euclidean_distance(vec1, vec2)
        assert abs(distance - 5.0) < 1e-10  # 3-4-5 triangle

    def test_euclidean_distance_different_dimensions(self):
        """Test Euclidean distance with different dimension vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        with pytest.raises(ValueError, match="Embeddings must have the same dimension"):
            EmbeddingSimilarity.euclidean_distance(vec1, vec2)

    def test_manhattan_distance_identical_vectors(self):
        """Test Manhattan distance with identical vectors."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.0, 2.0, 3.0]
        
        distance = EmbeddingSimilarity.manhattan_distance(vec1, vec2)
        assert distance == 0.0

    def test_manhattan_distance_different_vectors(self):
        """Test Manhattan distance with different vectors."""
        vec1 = [0.0, 0.0]
        vec2 = [3.0, 4.0]
        
        distance = EmbeddingSimilarity.manhattan_distance(vec1, vec2)
        assert distance == 7.0  # |0-3| + |0-4| = 7

    def test_manhattan_distance_different_dimensions(self):
        """Test Manhattan distance with different dimension vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        with pytest.raises(ValueError, match="Embeddings must have the same dimension"):
            EmbeddingSimilarity.manhattan_distance(vec1, vec2)

    def test_dot_product_identical_vectors(self):
        """Test dot product with identical vectors."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.0, 2.0, 3.0]
        
        dot_product = EmbeddingSimilarity.dot_product(vec1, vec2)
        assert dot_product == 14.0  # 1*1 + 2*2 + 3*3 = 14

    def test_dot_product_orthogonal_vectors(self):
        """Test dot product with orthogonal vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        
        dot_product = EmbeddingSimilarity.dot_product(vec1, vec2)
        assert dot_product == 0.0

    def test_dot_product_different_dimensions(self):
        """Test dot product with different dimension vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        with pytest.raises(ValueError, match="Embeddings must have the same dimension"):
            EmbeddingSimilarity.dot_product(vec1, vec2)


class TestSemanticSearchComprehensive:
    """Comprehensive test suite for SemanticSearch class."""

    def test_semantic_search_initialization(self, mock_client):
        """Test SemanticSearch initialization."""
        api = EmbeddingsAPI(mock_client)
        search = SemanticSearch(api)
        
        assert search.embeddings_api == api
        assert search.documents == []
        assert search.document_embeddings == []
        assert search.model == "text-embedding-ada-002"

    def test_add_documents(self, mock_client):
        """Test adding documents to search index."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1, 0.2], "index": 0, "object": "embedding"},
                {"embedding": [0.3, 0.4], "index": 1, "object": "embedding"}
            ],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 10, "total_tokens": 10},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        api = EmbeddingsAPI(mock_client)
        search = SemanticSearch(api)
        
        documents = ["Document 1", "Document 2"]
        search.add_documents(documents)
        
        assert search.documents == documents
        assert len(search.document_embeddings) == 2
        assert search.document_embeddings[0] == [0.1, 0.2]
        assert search.document_embeddings[1] == [0.3, 0.4]

    def test_add_documents_with_custom_model(self, mock_client):
        """Test adding documents with custom model."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2], "index": 0, "object": "embedding"}],
            "model": "text-embedding-3-large",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        api = EmbeddingsAPI(mock_client)
        search = SemanticSearch(api)
        
        search.add_documents(["Document 1"], model="text-embedding-3-large")
        
        assert search.model == "text-embedding-3-large"

    def test_search_with_documents(self, mock_client):
        """Test searching with documents in index."""
        # Mock response for adding documents
        mock_response1 = MagicMock()
        mock_response1.json.return_value = {
            "data": [
                {"embedding": [1.0, 0.0], "index": 0, "object": "embedding"},
                {"embedding": [0.0, 1.0], "index": 1, "object": "embedding"}
            ],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 10, "total_tokens": 10},
            "object": "list"
        }
        
        # Mock response for query embedding
        mock_response2 = MagicMock()
        mock_response2.json.return_value = {
            "data": [{"embedding": [1.0, 0.0], "index": 0, "object": "embedding"}],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
            "object": "list"
        }
        
        mock_client.post.side_effect = [mock_response1, mock_response2]
        
        api = EmbeddingsAPI(mock_client)
        search = SemanticSearch(api)
        
        # Add documents
        search.add_documents(["Hello world", "Goodbye world"])
        
        # Search
        results = search.search("Hello")
        
        assert len(results) == 2
        assert results[0]["document"] == "Hello world"
        assert results[0]["similarity"] == 1.0  # Identical vectors
        assert results[1]["document"] == "Goodbye world"
        assert results[1]["similarity"] == 0.0  # Orthogonal vectors

    def test_search_without_documents(self, mock_client):
        """Test searching without documents in index."""
        api = EmbeddingsAPI(mock_client)
        search = SemanticSearch(api)
        
        results = search.search("Hello")
        
        assert results == []

    def test_search_with_top_k(self, mock_client):
        """Test searching with top_k parameter."""
        # Mock response for adding documents
        mock_response1 = MagicMock()
        mock_response1.json.return_value = {
            "data": [
                {"embedding": [1.0, 0.0], "index": 0, "object": "embedding"},
                {"embedding": [0.0, 1.0], "index": 1, "object": "embedding"},
                {"embedding": [0.5, 0.5], "index": 2, "object": "embedding"}
            ],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 15, "total_tokens": 15},
            "object": "list"
        }
        
        # Mock response for query embedding
        mock_response2 = MagicMock()
        mock_response2.json.return_value = {
            "data": [{"embedding": [1.0, 0.0], "index": 0, "object": "embedding"}],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
            "object": "list"
        }
        
        mock_client.post.side_effect = [mock_response1, mock_response2]
        
        api = EmbeddingsAPI(mock_client)
        search = SemanticSearch(api)
        
        # Add documents
        search.add_documents(["Doc 1", "Doc 2", "Doc 3"])
        
        # Search with top_k=2
        results = search.search("Hello", top_k=2)
        
        assert len(results) == 2

    def test_search_with_similarity_threshold(self, mock_client):
        """Test searching with similarity threshold."""
        # Mock response for adding documents
        mock_response1 = MagicMock()
        mock_response1.json.return_value = {
            "data": [
                {"embedding": [1.0, 0.0], "index": 0, "object": "embedding"},
                {"embedding": [0.0, 1.0], "index": 1, "object": "embedding"}
            ],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 10, "total_tokens": 10},
            "object": "list"
        }
        
        # Mock response for query embedding
        mock_response2 = MagicMock()
        mock_response2.json.return_value = {
            "data": [{"embedding": [1.0, 0.0], "index": 0, "object": "embedding"}],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
            "object": "list"
        }
        
        mock_client.post.side_effect = [mock_response1, mock_response2]
        
        api = EmbeddingsAPI(mock_client)
        search = SemanticSearch(api)
        
        # Add documents
        search.add_documents(["Doc 1", "Doc 2"])
        
        # Search with high similarity threshold
        results = search.search("Hello", similarity_threshold=0.5)
        
        assert len(results) == 1  # Only the identical vector passes threshold
        assert results[0]["document"] == "Doc 1"

    def test_clear(self, mock_client):
        """Test clearing the search index."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2], "index": 0, "object": "embedding"}],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        api = EmbeddingsAPI(mock_client)
        search = SemanticSearch(api)
        
        # Add documents
        search.add_documents(["Document 1"])
        assert len(search.documents) == 1
        
        # Clear
        search.clear()
        assert search.documents == []
        assert search.document_embeddings == []


class TestEmbeddingClusteringComprehensive:
    """Comprehensive test suite for EmbeddingClustering class."""

    def test_kmeans_clusters_empty_list(self):
        """Test k-means clustering with empty list."""
        clusters = EmbeddingClustering.kmeans_clusters([], k=3)
        assert clusters == []

    def test_kmeans_clusters_k_greater_than_embeddings(self):
        """Test k-means clustering when k >= number of embeddings."""
        embeddings = [[1.0, 0.0], [0.0, 1.0]]
        clusters = EmbeddingClustering.kmeans_clusters(embeddings, k=3)
        assert clusters == [0, 1]

    def test_kmeans_clusters_single_embedding(self):
        """Test k-means clustering with single embedding."""
        embeddings = [[1.0, 0.0]]
        clusters = EmbeddingClustering.kmeans_clusters(embeddings, k=1)
        assert clusters == [0]

    def test_kmeans_clusters_convergence(self):
        """Test k-means clustering convergence."""
        # Create embeddings that should converge quickly
        embeddings = [
            [1.0, 0.0],
            [1.1, 0.1],
            [0.0, 1.0],
            [0.1, 1.1]
        ]
        
        clusters = EmbeddingClustering.kmeans_clusters(embeddings, k=2, max_iterations=10)
        
        assert len(clusters) == 4
        assert all(0 <= cluster < 2 for cluster in clusters)

    def test_kmeans_clusters_max_iterations(self):
        """Test k-means clustering with max iterations."""
        embeddings = [
            [1.0, 0.0],
            [0.0, 1.0],
            [2.0, 0.0],
            [0.0, 2.0]
        ]
        
        clusters = EmbeddingClustering.kmeans_clusters(embeddings, k=2, max_iterations=1)
        
        assert len(clusters) == 4
        assert all(0 <= cluster < 2 for cluster in clusters)


class TestConvenienceFunctionsComprehensive:
    """Comprehensive test suite for convenience functions."""

    def test_generate_embedding_with_client(self, mock_client):
        """Test generate_embedding with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2, 0.3], "index": 0, "object": "embedding"}],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        embedding = generate_embedding("Hello world", client=mock_client)
        
        assert embedding == [0.1, 0.2, 0.3]

    def test_generate_embedding_without_client(self):
        """Test generate_embedding without provided client."""
        with patch('venice_sdk.embeddings.load_config') as mock_load_config:
            with patch('venice_sdk.embeddings.VeniceClient') as mock_venice_client:
                mock_config = MagicMock()
                mock_load_config.return_value = mock_config
                
                mock_client = MagicMock()
                mock_venice_client.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "data": [{"embedding": [0.1, 0.2, 0.3], "index": 0, "object": "embedding"}],
                    "model": "text-embedding-ada-002",
                    "usage": {"prompt_tokens": 5, "total_tokens": 5},
                    "object": "list"
                }
                mock_client.post.return_value = mock_response
                
                embedding = generate_embedding("Hello world")
                
                assert embedding == [0.1, 0.2, 0.3]

    def test_calculate_similarity_with_client(self, mock_client):
        """Test calculate_similarity with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2], "index": 0, "object": "embedding"}],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        similarity = calculate_similarity("Hello", "World", client=mock_client)
        
        # Should be 1.0 since both texts get the same embedding
        assert similarity == 1.0

    def test_calculate_similarity_without_client(self):
        """Test calculate_similarity without provided client."""
        with patch('venice_sdk.embeddings.load_config') as mock_load_config:
            with patch('venice_sdk.embeddings.VeniceClient') as mock_venice_client:
                mock_config = MagicMock()
                mock_load_config.return_value = mock_config
                
                mock_client = MagicMock()
                mock_venice_client.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "data": [{"embedding": [0.1, 0.2], "index": 0, "object": "embedding"}],
                    "model": "text-embedding-ada-002",
                    "usage": {"prompt_tokens": 5, "total_tokens": 5},
                    "object": "list"
                }
                mock_client.post.return_value = mock_response
                
                similarity = calculate_similarity("Hello", "World")
                
                assert similarity == 1.0

    def test_generate_embeddings_with_client(self, mock_client):
        """Test generate_embeddings with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1, 0.2], "index": 0, "object": "embedding"},
                {"embedding": [0.3, 0.4], "index": 1, "object": "embedding"}
            ],
            "model": "text-embedding-ada-002",
            "usage": {"prompt_tokens": 10, "total_tokens": 10},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        result = generate_embeddings(["Hello", "World"], client=mock_client)
        
        assert isinstance(result, EmbeddingResult)
        assert len(result) == 2
        assert result.get_embedding(0) == [0.1, 0.2]
        assert result.get_embedding(1) == [0.3, 0.4]

    def test_generate_embeddings_without_client(self):
        """Test generate_embeddings without provided client."""
        with patch('venice_sdk.embeddings.load_config') as mock_load_config:
            with patch('venice_sdk.embeddings.VeniceClient') as mock_venice_client:
                mock_config = MagicMock()
                mock_load_config.return_value = mock_config
                
                mock_client = MagicMock()
                mock_venice_client.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "data": [{"embedding": [0.1, 0.2], "index": 0, "object": "embedding"}],
                    "model": "text-embedding-ada-002",
                    "usage": {"prompt_tokens": 5, "total_tokens": 5},
                    "object": "list"
                }
                mock_client.post.return_value = mock_response
                
                result = generate_embeddings("Hello world")
                
                assert isinstance(result, EmbeddingResult)
                assert len(result) == 1
                assert result.get_embedding(0) == [0.1, 0.2]

    def test_generate_embeddings_with_kwargs(self, mock_client):
        """Test generate_embeddings with additional kwargs."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2], "index": 0, "object": "embedding"}],
            "model": "text-embedding-3-large",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
            "object": "list"
        }
        mock_client.post.return_value = mock_response
        
        result = generate_embeddings("Hello world", client=mock_client, model="text-embedding-3-large")
        
        assert isinstance(result, EmbeddingResult)
        assert result.model == "text-embedding-3-large"
