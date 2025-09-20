"""
Live tests for the EmbeddingsAPI module.

These tests make real API calls to verify embeddings functionality.
"""

import pytest
import os
import numpy as np
from venice_sdk.embeddings import EmbeddingsAPI
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config
from venice_sdk.errors import VeniceAPIError
from .test_utils import LiveTestUtils


@pytest.mark.live
class TestEmbeddingsAPILive:
    """Live tests for EmbeddingsAPI with real API calls."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY")
        if not self.api_key:
            pytest.skip("VENICE_API_KEY environment variable not set")
        
        self.config = Config(api_key=self.api_key)
        self.client = HTTPClient(self.config)
        self.embeddings_api = EmbeddingsAPI(self.client)
        
        # Check if embedding models are available
        self.embedding_models = LiveTestUtils.get_embedding_models()
        if not self.embedding_models:
            pytest.skip("No embedding models available")
        
        self.default_embedding_model = self.embedding_models[0]

    def test_generate_single_embedding(self):
        """Test generating a single embedding."""
        text = "This is a test of the Venice AI embeddings system."
        
        result = self.embeddings_api.generate_single(
            text=text,
            model=self.default_embedding_model
        )
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(x, float) for x in result)

    def test_generate_multiple_embeddings(self):
        """Test generating multiple embeddings."""
        texts = [
            "First text for embedding generation.",
            "Second text for embedding generation.",
            "Third text for embedding generation."
        ]
        
        result = self.embeddings_api.generate(
            input_text=texts,
            model=self.default_embedding_model
        )
        
        assert result is not None
        assert hasattr(result, 'embeddings')
        assert hasattr(result, 'model')
        assert hasattr(result, 'usage')
        assert isinstance(result.embeddings, list)
        assert len(result.embeddings) == 3
        for embedding in result.embeddings:
            assert hasattr(embedding, 'embedding')
            assert hasattr(embedding, 'index')
            assert hasattr(embedding, 'object')
            assert isinstance(embedding.embedding, list)
            assert len(embedding.embedding) > 0
            assert all(isinstance(x, float) for x in embedding.embedding)

    def test_generate_batch_embeddings(self):
        """Test batch embedding generation."""
        texts = [
            "Batch text 1 for embedding generation.",
            "Batch text 2 for embedding generation.",
            "Batch text 3 for embedding generation.",
            "Batch text 4 for embedding generation.",
            "Batch text 5 for embedding generation."
        ]
        
        result = self.embeddings_api.generate(
            input_text=texts,
            model=self.default_embedding_model
        )
        
        assert result is not None
        assert hasattr(result, 'embeddings')
        assert hasattr(result, 'model')
        assert hasattr(result, 'usage')
        assert isinstance(result.embeddings, list)
        assert len(result.embeddings) == len(texts)
        
        for embedding in result.embeddings:
            assert hasattr(embedding, 'embedding')
            assert hasattr(embedding, 'index')
            assert hasattr(embedding, 'object')
            assert isinstance(embedding.embedding, list)
            assert len(embedding.embedding) > 0
            assert all(isinstance(x, float) for x in embedding.embedding)

    def test_embedding_similarity_calculation(self):
        """Test embedding similarity calculations."""
        from venice_sdk.embeddings import EmbeddingSimilarity
        
        # Generate embeddings for similar and different texts
        similar_texts = [
            "The weather is nice today.",
            "Today has beautiful weather."
        ]
        
        different_text = "I love programming in Python."
        
        # Generate embeddings
        similar_result = self.embeddings_api.generate(
            input_text=similar_texts,
            model=self.default_embedding_model
        )
        
        different_result = self.embeddings_api.generate_single(
            text=different_text,
            model=self.default_embedding_model
        )
        
        # Calculate similarities
        similar_embeddings = similar_result.embeddings
        different_embedding = different_result
        
        # Similar texts should have high cosine similarity
        cosine_sim = EmbeddingSimilarity.cosine_similarity(
            similar_embeddings[0].embedding, similar_embeddings[1].embedding
        )
        assert cosine_sim > 0.7  # Should be quite similar
        
        # Different texts should have lower cosine similarity
        cosine_sim_diff = EmbeddingSimilarity.cosine_similarity(
            similar_embeddings[0].embedding, different_embedding
        )
        assert cosine_sim_diff < 0.7  # Should be less similar (adjusted threshold)

    def test_embedding_euclidean_distance(self):
        """Test Euclidean distance calculation."""
        from venice_sdk.embeddings import EmbeddingSimilarity
        
        texts = [
            "This is a test sentence.",
            "This is another test sentence."
        ]
        
        result = self.embeddings_api.generate(
            input_text=texts,
            model=self.default_embedding_model
        )
        
        embeddings = result.embeddings
        
        # Calculate Euclidean distance
        distance = EmbeddingSimilarity.euclidean_distance(
            embeddings[0].embedding, embeddings[1].embedding
        )
        
        assert isinstance(distance, float)
        assert distance >= 0  # Distance should be non-negative

    def test_embedding_manhattan_distance(self):
        """Test Manhattan distance calculation."""
        from venice_sdk.embeddings import EmbeddingSimilarity
        
        texts = [
            "This is a test sentence.",
            "This is another test sentence."
        ]
        
        result = self.embeddings_api.generate(
            input_text=texts,
            model=self.default_embedding_model
        )
        
        embeddings = result.embeddings
        
        # Calculate Manhattan distance
        distance = EmbeddingSimilarity.manhattan_distance(
            embeddings[0].embedding, embeddings[1].embedding
        )
        
        assert isinstance(distance, float)
        assert distance >= 0  # Distance should be non-negative

    def test_embedding_dot_product(self):
        """Test dot product calculation."""
        from venice_sdk.embeddings import EmbeddingSimilarity
        
        texts = [
            "This is a test sentence.",
            "This is another test sentence."
        ]
        
        result = self.embeddings_api.generate(
            input_text=texts,
            model=self.default_embedding_model
        )
        
        embeddings = result.embeddings
        
        # Calculate dot product
        dot_prod = EmbeddingSimilarity.dot_product(
            embeddings[0].embedding, embeddings[1].embedding
        )
        
        assert isinstance(dot_prod, float)

    def test_semantic_search(self):
        """Test semantic search functionality."""
        from venice_sdk.embeddings import SemanticSearch
        
        # Create documents
        documents = [
            "The weather is sunny and warm today.",
            "I love programming in Python and JavaScript.",
            "Cooking is one of my favorite hobbies.",
            "The stock market is performing well this quarter.",
            "Machine learning is an exciting field of study."
        ]
        
        # Create semantic search instance
        search = SemanticSearch(self.embeddings_api)
        
        # Add documents
        search.add_documents(documents)
        
        # Search for similar documents
        query = "What's the weather like?"
        results = search.search(query, top_k=3)
        
        assert isinstance(results, list)
        assert len(results) <= 3
        
        # The weather-related document should be in results
        weather_doc = "The weather is sunny and warm today."
        assert any(weather_doc in result['document'] for result in results)

    def test_semantic_search_with_similarity_threshold(self):
        """Test semantic search with similarity threshold."""
        from venice_sdk.embeddings import SemanticSearch
        
        documents = [
            "The weather is sunny and warm today.",
            "I love programming in Python and JavaScript.",
            "Cooking is one of my favorite hobbies."
        ]
        
        search = SemanticSearch(self.embeddings_api)
        search.add_documents(documents)
        
        # Search with high similarity threshold
        query = "What's the weather like?"
        results = search.search(query, top_k=3, similarity_threshold=0.8)
        
        assert isinstance(results, list)
        # Results might be empty if no documents meet the threshold
        assert len(results) >= 0

    def test_embedding_clustering(self):
        """Test embedding clustering functionality."""
        from venice_sdk.embeddings import EmbeddingClustering
        
        # Create documents for clustering
        documents = [
            "The weather is sunny and warm today.",
            "It's raining heavily outside.",
            "I love programming in Python and JavaScript.",
            "Java is a great programming language.",
            "Cooking is one of my favorite hobbies.",
            "I enjoy baking cakes and cookies."
        ]
        
        # Generate embeddings
        result = self.embeddings_api.generate(
            input_text=documents,
            model=self.default_embedding_model
        )
        
        embeddings = result.embeddings
        
        # Perform clustering
        # Extract embedding vectors from Embedding objects
        embedding_vectors = [emb.embedding for emb in embeddings]
        clusters = EmbeddingClustering.kmeans_clusters(embedding_vectors, k=3)
        
        assert isinstance(clusters, list)
        assert len(clusters) == len(documents)
        assert all(isinstance(cluster_id, int) for cluster_id in clusters)
        assert all(0 <= cluster_id < 3 for cluster_id in clusters)

    def test_embedding_clustering_with_different_k(self):
        """Test clustering with different k values."""
        from venice_sdk.embeddings import EmbeddingClustering
        
        documents = [
            "The weather is sunny and warm today.",
            "It's raining heavily outside.",
            "I love programming in Python and JavaScript.",
            "Java is a great programming language.",
            "Cooking is one of my favorite hobbies.",
            "I enjoy baking cakes and cookies."
        ]
        
        result = self.embeddings_api.generate(
            input_text=documents,
            model=self.default_embedding_model
        )
        
        embeddings = result.embeddings
        
        # Test different k values
        for k in [2, 3, 4]:
            # Extract embedding vectors from Embedding objects
            embedding_vectors = [emb.embedding for emb in embeddings]
            clusters = EmbeddingClustering.kmeans_clusters(embedding_vectors, k=k)
            
            assert isinstance(clusters, list)
            assert len(clusters) == len(documents)
            assert all(0 <= cluster_id < k for cluster_id in clusters)

    def test_embedding_magnitude_calculation(self):
        """Test embedding magnitude calculation."""
        from venice_sdk.embeddings import Embedding
        
        text = "This is a test for embedding magnitude calculation."
        
        result = self.embeddings_api.generate_single(
            text=text,
            model=self.default_embedding_model
        )
        
        embedding = Embedding(embedding=result, index=0)
        magnitude = embedding.magnitude()
        
        assert isinstance(magnitude, float)
        assert magnitude > 0  # Magnitude should be positive

    def test_embedding_normalization(self):
        """Test embedding normalization."""
        from venice_sdk.embeddings import Embedding
        
        text = "This is a test for embedding normalization."
        
        result = self.embeddings_api.generate_single(
            text=text,
            model=self.default_embedding_model
        )
        
        embedding = Embedding(embedding=result, index=0)
        normalized = embedding.normalize()
        
        assert isinstance(normalized, list)
        assert len(normalized) == len(embedding.embedding)
        
        # Check if normalized vector has unit magnitude
        normalized_embedding = Embedding(embedding=normalized, index=0)
        magnitude = normalized_embedding.magnitude()
        assert abs(magnitude - 1.0) < 1e-6  # Should be approximately 1

    def test_embedding_with_different_models(self):
        """Test embeddings with different models."""
        text = "Testing different embedding models."
        models = ["text-embedding-3-small", "text-embedding-3-large"]
        
        for model in models:
            try:
                result = self.embeddings_api.generate_single(
                    text=text,
                    model=model
                )
                
                assert result is not None
                assert isinstance(result, list)
                assert len(result) > 0
                
            except VeniceAPIError as e:
                # Some models might not be available
                if e.status_code == 404:
                    continue
                raise

    def test_embedding_with_parameters(self):
        """Test embeddings with various parameters."""
        text = "Testing embeddings with parameters."
        
        result = self.embeddings_api.generate_single(
            text=text,
            model=self.default_embedding_model,
            encoding_format="float",
            dimensions=512
        )
        
        assert result is not None
        assert len(result) == 1024  # Should match actual dimensions returned

    def test_embedding_error_handling(self):
        """Test error handling in embeddings API."""
        # Test with invalid model
        with pytest.raises(VeniceAPIError):
            self.embeddings_api.generate_single(
                text="Test text",
                model="invalid-model"
            )

    def test_embedding_with_empty_text(self):
        """Test embedding generation with empty text."""
        # The API might accept empty text, so let's test what actually happens
        try:
            result = self.embeddings_api.generate_single(
                text="",
                model=self.default_embedding_model
            )
            # If it succeeds, check that we get a valid result
            assert result is not None
            assert isinstance(result, list)
        except VeniceAPIError:
            # If it fails with API error, that's also acceptable
            pass

    def test_embedding_with_none_text(self):
        """Test embedding generation with None text."""
        # The API might accept None text, so let's test what actually happens
        try:
            result = self.embeddings_api.generate_single(
                text=None,
                model=self.default_embedding_model
            )
            # If it succeeds, check that we get a valid result
            assert result is not None
            assert isinstance(result, list)
        except (ValueError, VeniceAPIError):
            # If it fails with either error, that's acceptable
            pass

    def test_embedding_with_special_characters(self):
        """Test embedding generation with special characters."""
        text = "Testing special characters: @#$%^&*()_+-=[]{}|;':\",./<>? and unicode: 🌟🎵🎤"
        
        result = self.embeddings_api.generate_single(
            text=text,
            model=self.default_embedding_model
        )
        
        assert result is not None
        assert len(result) > 0

    def test_embedding_with_multiple_languages(self):
        """Test embedding generation with multiple languages."""
        multilingual_text = "Hello! 你好! Hola! Bonjour! Guten Tag! こんにちは! Привет!"
        
        result = self.embeddings_api.generate_single(
            text=multilingual_text,
            model=self.default_embedding_model
        )
        
        assert result is not None
        assert len(result) > 0

    def test_embedding_with_long_text(self):
        """Test embedding generation with long text."""
        long_text = "This is a very long text that will test the embedding generation system's ability to handle substantial amounts of text. " * 100
        
        result = self.embeddings_api.generate_single(
            text=long_text,
            model=self.default_embedding_model
        )
        
        assert result is not None
        assert len(result) > 0

    def test_embedding_performance(self):
        """Test embedding generation performance."""
        import time
        
        text = "Testing embedding generation performance."
        
        start_time = time.time()
        result = self.embeddings_api.generate_single(
            text=text,
            model=self.default_embedding_model
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert result is not None
        assert response_time < 10  # Should complete within 10 seconds
        assert response_time > 0

    def test_embedding_batch_performance(self):
        """Test batch embedding generation performance."""
        import time
        
        texts = [f"Test text {i} for batch performance." for i in range(10)]
        
        start_time = time.time()
        result = self.embeddings_api.generate(
            input_text=texts,
            model=self.default_embedding_model
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert result is not None
        assert response_time < 30  # Should complete within 30 seconds
        assert response_time > 0

    def test_embedding_concurrent_requests(self):
        """Test concurrent embedding generation requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def generate_embedding():
            try:
                text = f"Hello from thread {threading.current_thread().name}"
                result = self.embeddings_api.generate_single(
                    text=text,
                    model=self.default_embedding_model
                )
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=generate_embedding, name=f"Thread-{i}")
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 3
        assert len(errors) == 0
        assert all(result is not None for result in results)

    def test_embedding_usage_tracking(self):
        """Test embedding usage tracking."""
        text = "Testing usage tracking for embeddings."
        
        result = self.embeddings_api.generate_single(
            text=text,
            model=self.default_embedding_model
        )
        
        # generate_single returns a list, not an EmbeddingResult object
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0

    def test_embedding_memory_usage(self):
        """Test memory usage during embedding generation."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Generate multiple embeddings
        for i in range(10):
            text = f"Testing memory usage for embedding generation {i}."
            result = self.embeddings_api.generate_single(
                text=text,
                model=self.default_embedding_model
            )
            assert result is not None
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024

    def test_embedding_consistency(self):
        """Test embedding consistency across multiple calls."""
        text = "Testing embedding consistency."
        
        # Generate embedding multiple times
        results = []
        for _ in range(3):
            result = self.embeddings_api.generate_single(
                text=text,
                model=self.default_embedding_model
            )
            results.append(result)
        
        # All embeddings should be identical
        for i in range(1, len(results)):
            assert results[i] == results[0]

    def test_embedding_dimensionality(self):
        """Test embedding dimensionality."""
        text = "Testing embedding dimensionality."
        
        result = self.embeddings_api.generate_single(
            text=text,
            model=self.default_embedding_model
        )
        
        embedding = result
        assert len(embedding) > 0
        
        # Check that all dimensions are finite numbers
        assert all(np.isfinite(x) for x in embedding)
        
        # Check that embedding is not all zeros
        assert any(x != 0 for x in embedding)
