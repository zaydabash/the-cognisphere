"""
Vector-based memory system for The Cognisphere.

This module implements vector database functionality for semantic search,
similarity matching, and knowledge retrieval using embeddings.
"""

import hashlib
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import chromadb

    # from chromadb.config import Settings  # Unused import
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


@dataclass
class VectorMemory:
    """Represents a vector memory with embedding and metadata."""

    memory_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    embedding: np.ndarray = field(default_factory=lambda: np.array([]))
    memory_type: str = "general"
    importance: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "embedding": self.embedding.tolist() if self.embedding.size > 0 else [],
            "memory_type": self.memory_type,
            "importance": self.importance,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorMemory":
        """Create from dictionary."""
        memory = cls()
        memory.memory_id = data["memory_id"]
        memory.content = data["content"]
        memory.embedding = np.array(data["embedding"]) if data["embedding"] else np.array([])
        memory.memory_type = data["memory_type"]
        memory.importance = data["importance"]
        memory.created_at = datetime.fromisoformat(data["created_at"])
        memory.last_accessed = datetime.fromisoformat(data["last_accessed"])
        memory.access_count = data["access_count"]
        memory.metadata = data["metadata"]
        return memory


class MockEmbeddingModel:
    """Mock embedding model for testing and development."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vocab: Dict[str, int] = {}
        self.vocab_size = 1000

    def embed_text(self, text: str) -> np.ndarray:
        """Generate mock embedding for text."""
        # Create deterministic embedding based on text hash. Use a *local*
        # RandomState so we don't clobber the global numpy RNG seed that the
        # rest of the simulation depends on for reproducible (seeded) runs.
        text_hash = hashlib.md5(text.encode()).hexdigest()
        rng = np.random.RandomState(int(text_hash[:8], 16))

        # Generate embedding
        embedding = rng.normal(0, 1, self.dimension)

        # Normalize
        embedding = embedding / np.linalg.norm(embedding)

        return embedding

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for batch of texts."""
        embeddings = []
        for text in texts:
            embeddings.append(self.embed_text(text))
        return np.array(embeddings)


class FAISSVectorStore:
    """Vector store implementation using FAISS."""

    def __init__(self, dimension: int = 384, index_type: str = "flat"):
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS is not available. Install with: pip install faiss-cpu")

        self.dimension = dimension
        self.index_type = index_type
        self.memories: Dict[str, VectorMemory] = {}

        # Initialize FAISS index
        if index_type == "flat":
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        elif index_type == "ivf":
            quantizer = faiss.IndexFlatIP(dimension)
            self.index = faiss.IndexIVFFlat(quantizer, dimension, 100)
        else:
            self.index = faiss.IndexFlatIP(dimension)

        self.is_trained = False

    def add_memory(self, memory: VectorMemory) -> str:
        """Add a memory to the vector store."""
        if memory.embedding.size == 0:
            raise ValueError("Memory must have an embedding")

        # Ensure embedding is the right dimension
        if memory.embedding.shape[0] != self.dimension:
            raise ValueError(
                f"Embedding dimension {memory.embedding.shape[0]} doesn't match store dimension {self.dimension}"
            )

        # Add to FAISS index
        embedding = memory.embedding.reshape(1, -1).astype("float32")

        if not self.is_trained and hasattr(self.index, "is_trained"):
            # Train IVF index if needed
            if not self.index.is_trained:
                training_data = np.random.random((1000, self.dimension)).astype("float32")
                self.index.train(training_data)
            self.is_trained = True

        self.index.add(embedding)
        self.memories[memory.memory_id] = memory

        return memory.memory_id

    def search(
        self, query_embedding: np.ndarray, k: int = 10, memory_types: Optional[List[str]] = None
    ) -> List[Tuple[VectorMemory, float]]:
        """Search for similar memories."""
        if query_embedding.size == 0:
            return []

        # Ensure query embedding is the right dimension
        if query_embedding.shape[0] != self.dimension:
            raise ValueError(
                f"Query embedding dimension {query_embedding.shape[0]} doesn't match store dimension {self.dimension}"
            )

        query_embedding = query_embedding.reshape(1, -1).astype("float32")

        # Search FAISS index
        scores, indices = self.index.search(
            query_embedding, k * 2
        )  # Get more results for filtering

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue

            # Get memory by index (FAISS returns indices in order of addition)
            memory_ids = list(self.memories.keys())
            if idx < len(memory_ids):
                memory_id = memory_ids[idx]
                memory = self.memories[memory_id]

                # Filter by memory type if specified
                if memory_types is None or memory.memory_type in memory_types:
                    results.append((memory, float(score)))

                    if len(results) >= k:
                        break

        return results

    def remove_memory(self, memory_id: str) -> bool:
        """Remove a memory from the vector store."""
        if memory_id not in self.memories:
            return False

        # FAISS doesn't support efficient removal, so we'll mark as removed
        # In production, you'd want to rebuild the index periodically
        del self.memories[memory_id]
        return True

    def get_memory(self, memory_id: str) -> Optional[VectorMemory]:
        """Get a memory by ID."""
        return self.memories.get(memory_id)

    def update_memory(self, memory_id: str, **kwargs) -> bool:
        """Update a memory."""
        if memory_id not in self.memories:
            return False

        memory = self.memories[memory_id]
        for key, value in kwargs.items():
            if hasattr(memory, key):
                setattr(memory, key, value)

        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_memories": len(self.memories),
            "dimension": self.dimension,
            "index_type": self.index_type,
            "index_size": self.index.ntotal,
            "memory_types": list(set(memory.memory_type for memory in self.memories.values())),
        }


class ChromaVectorStore:
    """Vector store implementation using ChromaDB."""

    def __init__(
        self, collection_name: str = "cognisphere_memories", persist_directory: str = "./chroma_db"
    ):
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB is not available. Install with: pip install chromadb")

        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name, metadata={"description": "Cognisphere memory embeddings"}
            )

    def add_memory(self, memory: VectorMemory) -> str:
        """Add a memory to the vector store."""
        if memory.embedding.size == 0:
            raise ValueError("Memory must have an embedding")

        # Add to ChromaDB collection
        self.collection.add(
            ids=[memory.memory_id],
            embeddings=[memory.embedding.tolist()],
            documents=[memory.content],
            metadatas=[
                {
                    "memory_type": memory.memory_type,
                    "importance": memory.importance,
                    "created_at": memory.created_at.isoformat(),
                    "access_count": memory.access_count,
                    **memory.metadata,
                }
            ],
        )

        return memory.memory_id

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        memory_types: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[VectorMemory, float]]:
        """Search for similar memories."""
        if query_embedding.size == 0:
            return []

        # Prepare query metadata filter
        query_where = {}
        if memory_types:
            query_where["memory_type"] = {"$in": memory_types}

        if where:
            query_where.update(where)

        # Search ChromaDB collection. ChromaDB's QueryResult is a loosely-typed
        # TypedDict (Optional fields, union metadata values); treat it as dynamic.
        results: Any = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k,
            where=query_where if query_where else None,  # type: ignore[arg-type]
        )

        # Convert results to VectorMemory objects
        memories = []
        if results["ids"] and results["ids"][0]:
            for i, memory_id in enumerate(results["ids"][0]):
                content = results["documents"][0][i]
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]

                # Convert distance to similarity score (ChromaDB returns L2 distance)
                similarity = 1.0 / (1.0 + distance)

                memory = VectorMemory(
                    memory_id=memory_id,
                    content=content,
                    embedding=np.array(results["embeddings"][0][i]),
                    memory_type=metadata.get("memory_type", "general"),
                    importance=metadata.get("importance", 0.5),
                    created_at=datetime.fromisoformat(
                        metadata.get("created_at", datetime.now().isoformat())
                    ),
                    access_count=metadata.get("access_count", 0),
                    metadata={
                        k: v
                        for k, v in metadata.items()
                        if k not in ["memory_type", "importance", "created_at", "access_count"]
                    },
                )

                memories.append((memory, similarity))

        return memories

    def remove_memory(self, memory_id: str) -> bool:
        """Remove a memory from the vector store."""
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False

    def get_memory(self, memory_id: str) -> Optional[VectorMemory]:
        """Get a memory by ID."""
        try:
            results: Any = self.collection.get(ids=[memory_id])
            if results["ids"]:
                i = 0
                memory_id = results["ids"][i]
                content = results["documents"][i]
                metadata = results["metadatas"][i]

                return VectorMemory(
                    memory_id=memory_id,
                    content=content,
                    embedding=np.array(results["embeddings"][i]),
                    memory_type=metadata.get("memory_type", "general"),
                    importance=metadata.get("importance", 0.5),
                    created_at=datetime.fromisoformat(
                        metadata.get("created_at", datetime.now().isoformat())
                    ),
                    access_count=metadata.get("access_count", 0),
                    metadata={
                        k: v
                        for k, v in metadata.items()
                        if k not in ["memory_type", "importance", "created_at", "access_count"]
                    },
                )
        except Exception:
            pass
        return None

    def update_memory(self, memory_id: str, **kwargs) -> bool:
        """Update a memory."""
        try:
            # Get existing memory
            memory = self.get_memory(memory_id)
            if not memory:
                return False

            # Update fields
            for key, value in kwargs.items():
                if hasattr(memory, key):
                    setattr(memory, key, value)

            # Remove and re-add with updated data
            self.remove_memory(memory_id)
            self.add_memory(memory)
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        try:
            count = self.collection.count()
            return {
                "total_memories": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory,
            }
        except Exception:
            return {"total_memories": 0}


class VectorMemorySystem:
    """Main vector memory system that manages semantic search and retrieval."""

    def __init__(self, backend: str = "faiss", dimension: int = 384, embedding_model: str = "mock"):
        self.backend = backend
        self.dimension = dimension
        self.embedding_model_name = embedding_model

        # Initialize embedding model
        if embedding_model == "mock":
            self.embedding_model = MockEmbeddingModel(dimension)
        else:
            # Could add support for other models like sentence-transformers
            self.embedding_model = MockEmbeddingModel(dimension)

        # Initialize vector store
        self.vector_store: Union[FAISSVectorStore, ChromaVectorStore]
        if backend == "faiss":
            self.vector_store = FAISSVectorStore(dimension)
        elif backend == "chroma":
            self.vector_store = ChromaVectorStore()
        else:
            raise ValueError(f"Unsupported backend: {backend}")

        # Cache for recent searches
        self.search_cache: Dict[str, Any] = {}
        self.cache_size = 1000

    def add_memory(
        self,
        content: str,
        memory_type: str = "general",
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add a memory to the vector store."""
        # Generate embedding
        embedding = self.embedding_model.embed_text(content)

        # Create memory object
        memory = VectorMemory(
            content=content,
            embedding=embedding,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata or {},
        )

        # Add to vector store
        return self.vector_store.add_memory(memory)

    def search_memories(
        self,
        query: str,
        k: int = 10,
        memory_types: Optional[List[str]] = None,
        similarity_threshold: float = 0.0,
    ) -> List[Tuple[VectorMemory, float]]:
        """Search for memories similar to the query."""
        # Check cache first
        cache_key = f"{query}_{k}_{memory_types}_{similarity_threshold}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]

        # Generate query embedding
        query_embedding = self.embedding_model.embed_text(query)

        # Search vector store
        results = self.vector_store.search(query_embedding, k=k, memory_types=memory_types)

        # Filter by similarity threshold
        filtered_results = [
            (memory, score) for memory, score in results if score >= similarity_threshold
        ]

        # Update access counts
        for memory, _ in filtered_results:
            memory.access_count += 1
            memory.last_accessed = datetime.now()

        # Cache results
        if len(self.search_cache) >= self.cache_size:
            # Remove oldest entries
            oldest_key = next(iter(self.search_cache))
            del self.search_cache[oldest_key]

        self.search_cache[cache_key] = filtered_results

        return filtered_results

    def add_batch(
        self,
        contents: List[str],
        memory_types: Optional[List[str]] = None,
        importances: Optional[List[float]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """Add multiple memories at once."""
        if memory_types is None:
            memory_types = ["general"] * len(contents)
        if importances is None:
            importances = [0.5] * len(contents)
        if metadatas is None:
            metadatas = [{}] * len(contents)

        # Generate embeddings for batch
        embeddings = self.embedding_model.embed_batch(contents)

        memory_ids = []
        for i, content in enumerate(contents):
            memory = VectorMemory(
                content=content,
                embedding=embeddings[i],
                memory_type=memory_types[i],
                importance=importances[i],
                metadata=metadatas[i],
            )

            memory_id = self.vector_store.add_memory(memory)
            memory_ids.append(memory_id)

        return memory_ids

    def get_memory(self, memory_id: str) -> Optional[VectorMemory]:
        """Get a memory by ID."""
        return self.vector_store.get_memory(memory_id)

    def update_memory(self, memory_id: str, **kwargs) -> bool:
        """Update a memory."""
        return self.vector_store.update_memory(memory_id, **kwargs)

    def remove_memory(self, memory_id: str) -> bool:
        """Remove a memory."""
        return self.vector_store.remove_memory(memory_id)

    def semantic_search(
        self, query: str, context_memories: Optional[List[str]] = None, k: int = 5
    ) -> List[Dict[str, Any]]:
        """Perform semantic search with context."""
        # Search for relevant memories
        results = self.search_memories(query, k=k * 2)

        # If context memories provided, boost similar memories
        if context_memories:
            context_results = []
            for context_memory_id in context_memories:
                context_memory = self.get_memory(context_memory_id)
                if context_memory:
                    # Find memories similar to context
                    context_search = self.search_memories(context_memory.content, k=k)
                    context_results.extend(context_search)

            # Merge and deduplicate results
            all_results = results + context_results
            seen_ids = set()
            merged_results = []

            for memory, score in all_results:
                if memory.memory_id not in seen_ids:
                    seen_ids.add(memory.memory_id)
                    merged_results.append((memory, score))

            # Sort by score and take top k
            merged_results.sort(key=lambda x: x[1], reverse=True)
            results = merged_results[:k]

        # Format results
        formatted_results = []
        for memory, score in results:
            formatted_results.append(
                {
                    "memory_id": memory.memory_id,
                    "content": memory.content,
                    "memory_type": memory.memory_type,
                    "importance": memory.importance,
                    "similarity_score": score,
                    "created_at": memory.created_at,
                    "access_count": memory.access_count,
                    "metadata": memory.metadata,
                }
            )

        return formatted_results

    def get_related_memories(self, memory_id: str, k: int = 5) -> List[Dict[str, Any]]:
        """Get memories related to a specific memory."""
        memory = self.get_memory(memory_id)
        if not memory:
            return []

        return self.semantic_search(memory.content, k=k)

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get statistics about the vector memory system."""
        store_stats = self.vector_store.get_stats()

        return {
            "backend": self.backend,
            "dimension": self.dimension,
            "embedding_model": self.embedding_model_name,
            "cache_size": len(self.search_cache),
            **store_stats,
        }

    def clear_cache(self) -> None:
        """Clear the search cache."""
        self.search_cache.clear()

    def export_memories(self, filename: str) -> None:
        """Export all memories to a file."""
        # This is a simplified export - in production you'd want more robust serialization
        memories_data = []

        # Get all memories (this is backend-specific)
        if hasattr(self.vector_store, "memories"):
            for memory in self.vector_store.memories.values():
                memories_data.append(memory.to_dict())

        with open(filename, "w") as f:
            json.dump(memories_data, f, indent=2, default=str)

    def import_memories(self, filename: str) -> int:
        """Import memories from a file."""
        if not os.path.exists(filename):
            return 0

        with open(filename, "r") as f:
            memories_data = json.load(f)

        imported_count = 0
        for memory_data in memories_data:
            try:
                memory = VectorMemory.from_dict(memory_data)
                self.vector_store.add_memory(memory)
                imported_count += 1
            except Exception as e:
                print(f"Error importing memory: {e}")
                continue

        return imported_count
