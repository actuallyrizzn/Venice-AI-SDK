"""
Venice AI SDK - Embeddings Module

This module provides vector embedding generation and similarity calculation capabilities.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from .client import HTTPClient
from .errors import VeniceAPIError, EmbeddingError
from .config import load_config


@dataclass
class Embedding:
    """Represents a single embedding vector."""
    embedding: List[float]
    index: int
    object: str = "embedding"
    
    def __len__(self) -> int:
        """Get the dimension of the embedding."""
        return len(self.embedding)
    
    def magnitude(self) -> float:
        """Calculate the magnitude (length) of the embedding vector."""
        return math.sqrt(sum(x * x for x in self.embedding))
    
    def normalize(self) -> List[float]:
        """Return a normalized version of the embedding."""
        mag = self.magnitude()
        if mag == 0:
            return self.embedding
        return [x / mag for x in self.embedding]


@dataclass
class EmbeddingResult:
    """Represents the result of an embedding generation request."""
    embeddings: List[Embedding]
    model: str
    usage: Optional[Dict[str, int]] = None
    object: str = "list"
    
    def __len__(self) -> int:
        """Get the number of embeddings."""
        return len(self.embeddings)
    
    def __getitem__(self, index: int) -> Embedding:
        """Get embedding by index."""
        return self.embeddings[index]
    
    def __iter__(self):
        """Iterate over embeddings."""
        return iter(self.embeddings)
    
    def get_embedding(self, index: int = 0) -> List[float]:
        """Get the embedding vector at the specified index."""
        if index >= len(self.embeddings):
            raise IndexError(f"Index {index} out of range for {len(self.embeddings)} embeddings")
        return self.embeddings[index].embedding
    
    def get_all_embeddings(self) -> List[List[float]]:
        """Get all embedding vectors as a list of lists."""
        return [emb.embedding for emb in self.embeddings]


class EmbeddingsAPI:
    """Embeddings generation API client."""
    
    def __init__(self, client: HTTPClient):
        self.client = client
    
    def generate(
        self,
        input_text: Union[str, List[str]],
        model: str = "text-embedding-ada-002",
        encoding_format: str = "float",
        user: Optional[str] = None,
        **kwargs
    ) -> EmbeddingResult:
        """
        Generate embeddings for text.
        
        Args:
            input_text: Text or list of texts to embed
            model: Embedding model to use
            encoding_format: Format of the returned embeddings
            user: User identifier for tracking
            **kwargs: Additional parameters
            
        Returns:
            EmbeddingResult with generated embeddings
        """
        data = {
            "model": model,
            "input": input_text,
            "encoding_format": encoding_format,
            **kwargs
        }
        
        if user:
            data["user"] = user
        
        response = self.client.post("/embeddings/generate", data=data)
        result = response.json()
        
        if "data" not in result:
            raise EmbeddingError("Invalid response format from embeddings API")
        
        embeddings = []
        for item in result["data"]:
            embeddings.append(Embedding(
                embedding=item["embedding"],
                index=item["index"],
                object=item.get("object", "embedding")
            ))
        
        return EmbeddingResult(
            embeddings=embeddings,
            model=result["model"],
            usage=result.get("usage"),
            object=result.get("object", "list")
        )
    
    def generate_single(
        self,
        text: str,
        model: str = "text-embedding-ada-002",
        **kwargs
    ) -> List[float]:
        """
        Generate a single embedding and return just the vector.
        
        Args:
            text: Text to embed
            model: Embedding model to use
            **kwargs: Additional parameters
            
        Returns:
            Embedding vector as list of floats
        """
        result = self.generate(text, model=model, **kwargs)
        return result.get_embedding(0)
    
    def generate_batch(
        self,
        texts: List[str],
        model: str = "text-embedding-ada-002",
        batch_size: int = 100,
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings for a large batch of texts.
        
        Args:
            texts: List of texts to embed
            model: Embedding model to use
            batch_size: Number of texts to process in each batch
            **kwargs: Additional parameters
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = self.generate(batch, model=model, **kwargs)
            all_embeddings.extend(result.get_all_embeddings())
        
        return all_embeddings


class EmbeddingSimilarity:
    """Utility class for embedding similarity calculations."""
    
    @staticmethod
    def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (-1 to 1)
        """
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings must have the same dimension")
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in embedding1))
        magnitude2 = math.sqrt(sum(b * b for b in embedding2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    @staticmethod
    def euclidean_distance(embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate Euclidean distance between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Euclidean distance (lower is more similar)
        """
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings must have the same dimension")
        
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(embedding1, embedding2)))
    
    @staticmethod
    def manhattan_distance(embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate Manhattan distance between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Manhattan distance (lower is more similar)
        """
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings must have the same dimension")
        
        return sum(abs(a - b) for a, b in zip(embedding1, embedding2))
    
    @staticmethod
    def dot_product(embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate dot product between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Dot product value
        """
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings must have the same dimension")
        
        return sum(a * b for a, b in zip(embedding1, embedding2))


class SemanticSearch:
    """Semantic search using embeddings."""
    
    def __init__(self, embeddings_api: EmbeddingsAPI):
        self.embeddings_api = embeddings_api
        self.documents = []
        self.document_embeddings = []
        self.model = "text-embedding-ada-002"
    
    def add_documents(
        self,
        documents: List[str],
        model: Optional[str] = None
    ) -> None:
        """
        Add documents to the search index.
        
        Args:
            documents: List of document texts
            model: Embedding model to use
        """
        if model:
            self.model = model
        
        # Generate embeddings for documents
        result = self.embeddings_api.generate(documents, model=self.model)
        embeddings = result.get_all_embeddings()
        
        # Add to index
        self.documents.extend(documents)
        self.document_embeddings.extend(embeddings)
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results with documents and similarity scores
        """
        if not self.documents:
            return []
        
        # Generate embedding for query
        query_embedding = self.embeddings_api.generate_single(query, model=self.model)
        
        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(self.document_embeddings):
            similarity = EmbeddingSimilarity.cosine_similarity(query_embedding, doc_embedding)
            if similarity >= similarity_threshold:
                similarities.append({
                    "document": self.documents[i],
                    "similarity": similarity,
                    "index": i
                })
        
        # Sort by similarity (descending) and return top_k
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]
    
    def clear(self) -> None:
        """Clear all documents from the search index."""
        self.documents.clear()
        self.document_embeddings.clear()


class EmbeddingClustering:
    """Clustering utilities for embeddings."""
    
    @staticmethod
    def kmeans_clusters(
        embeddings: List[List[float]],
        k: int,
        max_iterations: int = 100
    ) -> List[int]:
        """
        Perform k-means clustering on embeddings.
        
        Args:
            embeddings: List of embedding vectors
            k: Number of clusters
            max_iterations: Maximum number of iterations
            
        Returns:
            List of cluster assignments for each embedding
        """
        if not embeddings:
            return []
        
        if k >= len(embeddings):
            return list(range(len(embeddings)))
        
        # Initialize centroids randomly
        import random
        centroids = random.sample(embeddings, k)
        assignments = [0] * len(embeddings)
        
        for _ in range(max_iterations):
            # Assign each embedding to nearest centroid
            new_assignments = []
            for emb in embeddings:
                distances = [
                    EmbeddingSimilarity.euclidean_distance(emb, centroid)
                    for centroid in centroids
                ]
                new_assignments.append(distances.index(min(distances)))
            
            # Check for convergence
            if new_assignments == assignments:
                break
            
            assignments = new_assignments
            
            # Update centroids
            for i in range(k):
                cluster_embeddings = [emb for j, emb in enumerate(embeddings) if assignments[j] == i]
                if cluster_embeddings:
                    # Calculate mean of cluster
                    dimension = len(cluster_embeddings[0])
                    centroids[i] = [
                        sum(emb[d] for emb in cluster_embeddings) / len(cluster_embeddings)
                        for d in range(dimension)
                    ]
        
        return assignments


# Convenience functions
def generate_embedding(
    text: str,
    client: Optional[HTTPClient] = None,
    **kwargs
) -> List[float]:
    """Convenience function to generate a single embedding."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = EmbeddingsAPI(client)
    return api.generate_single(text, **kwargs)


def calculate_similarity(
    text1: str,
    text2: str,
    client: Optional[HTTPClient] = None,
    **kwargs
) -> float:
    """Convenience function to calculate similarity between two texts."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = EmbeddingsAPI(client)
    emb1 = api.generate_single(text1, **kwargs)
    emb2 = api.generate_single(text2, **kwargs)
    
    return EmbeddingSimilarity.cosine_similarity(emb1, emb2)


def generate_embeddings(
    texts: Union[str, List[str]],
    client: Optional[HTTPClient] = None,
    **kwargs
) -> EmbeddingResult:
    """Convenience function to generate embeddings."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = EmbeddingsAPI(client)
    return api.generate(texts, **kwargs)
