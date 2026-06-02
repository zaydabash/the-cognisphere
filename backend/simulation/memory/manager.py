"""
Memory Manager for The Cognisphere.

This module integrates graph-based and vector-based memory systems to provide
comprehensive memory management for agents and the simulation.
"""

import threading
import uuid
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .graph import MemoryGraph, MemoryNode, MemoryType, RelationshipType
from .vector import VectorMemory, VectorMemorySystem


@dataclass
class MemoryQuery:
    """Represents a memory query with parameters."""

    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_text: str = ""
    memory_types: List[MemoryType] = field(default_factory=list)
    relationship_types: List[RelationshipType] = field(default_factory=list)
    importance_threshold: float = 0.0
    similarity_threshold: float = 0.0
    max_results: int = 10
    include_metadata: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary."""
        return {
            "query_id": self.query_id,
            "query_text": self.query_text,
            "memory_types": [mt.value for mt in self.memory_types],
            "relationship_types": [rt.value for rt in self.relationship_types],
            "importance_threshold": self.importance_threshold,
            "similarity_threshold": self.similarity_threshold,
            "max_results": self.max_results,
            "include_metadata": self.include_metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class MemoryResult:
    """Represents a memory search result."""

    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    memory_node: Optional[MemoryNode] = None
    vector_memory: Optional[VectorMemory] = None
    similarity_score: float = 0.0
    relevance_score: float = 0.0
    relationship_path: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "result_id": self.result_id,
            "memory_node": self.memory_node.to_dict() if self.memory_node else None,
            "vector_memory": self.vector_memory.to_dict() if self.vector_memory else None,
            "similarity_score": self.similarity_score,
            "relevance_score": self.relevance_score,
            "relationship_path": self.relationship_path,
            "metadata": self.metadata,
        }


class MemoryManager:
    """Integrated memory management system combining graph and vector stores."""

    def __init__(
        self,
        graph_backend: str = "networkx",
        vector_backend: str = "faiss",
        vector_dimension: int = 384,
        max_memories: int = 100000,
    ):
        self.graph_backend = graph_backend
        self.vector_backend = vector_backend
        self.max_memories = max_memories

        # Initialize memory systems. When graph_backend == "neo4j" the graph
        # writes through to a Neo4j database (falling back to NetworkX if the
        # server is unreachable).
        self.graph_memory = MemoryGraph(backend=graph_backend)
        self.vector_memory = VectorMemorySystem(backend=vector_backend, dimension=vector_dimension)

        # Memory synchronization
        self.memory_sync_queue: deque = deque()
        self.sync_lock = threading.Lock()

        # Query cache
        self.query_cache: Dict[str, Any] = {}
        self.cache_size = 1000

        # Statistics
        self.stats: Dict[str, Any] = {
            "total_queries": 0,
            "cache_hits": 0,
            "graph_searches": 0,
            "vector_searches": 0,
            "hybrid_searches": 0,
            "last_cleanup": datetime.now(),
        }

        # Background tasks
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.background_tasks: List[Any] = []

    def add_episodic_memory(
        self,
        content: str,
        agent_id: str,
        importance: float = 0.5,
        valence: float = 0.0,
        arousal: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, str]:
        """Add an episodic memory to both graph and vector stores."""
        # Add to graph memory
        graph_node_id = self.graph_memory.create_episodic_memory(
            content=content,
            importance=importance,
            valence=valence,
            arousal=arousal,
            metadata=metadata or {},
        )

        # Add to vector memory
        vector_memory_id = self.vector_memory.add_memory(
            content=content,
            memory_type="episodic",
            importance=importance,
            metadata={"agent_id": agent_id, "graph_node_id": graph_node_id, **(metadata or {})},
        )

        # Create relationship between graph node and agent
        if agent_id in self.graph_memory.nodes:
            self.graph_memory.create_relationship(
                source_id=graph_node_id,
                target_id=agent_id,
                relationship_type=RelationshipType.CREATED,
            )

        return graph_node_id, vector_memory_id

    def add_semantic_memory(
        self,
        content: str,
        agent_id: str,
        importance: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, str]:
        """Add a semantic memory to both graph and vector stores."""
        # Add to graph memory
        graph_node_id = self.graph_memory.create_semantic_memory(
            content=content, importance=importance, metadata=metadata or {}
        )

        # Add to vector memory
        vector_memory_id = self.vector_memory.add_memory(
            content=content,
            memory_type="semantic",
            importance=importance,
            metadata={"agent_id": agent_id, "graph_node_id": graph_node_id, **(metadata or {})},
        )

        # Create relationship between graph node and agent
        if agent_id in self.graph_memory.nodes:
            self.graph_memory.create_relationship(
                source_id=graph_node_id,
                target_id=agent_id,
                relationship_type=RelationshipType.KNOWS,
            )

        return graph_node_id, vector_memory_id

    def add_social_memory(
        self,
        content: str,
        agent_id: str,
        other_agent_id: str,
        relationship_type: RelationshipType,
        valence: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, str]:
        """Add a social memory to both graph and vector stores."""
        # Add to graph memory
        graph_node_id = self.graph_memory.create_social_memory(
            content=content,
            other_agent_id=other_agent_id,
            relationship_type=relationship_type,
            valence=valence,
            metadata=metadata or {},
        )

        # Add to vector memory
        vector_memory_id = self.vector_memory.add_memory(
            content=content,
            memory_type="social",
            importance=0.6,
            metadata={
                "agent_id": agent_id,
                "other_agent_id": other_agent_id,
                "relationship_type": relationship_type.value,
                "graph_node_id": graph_node_id,
                **(metadata or {}),
            },
        )

        # Create relationship between agents
        if other_agent_id in self.graph_memory.nodes:
            self.graph_memory.create_relationship(
                source_id=agent_id, target_id=other_agent_id, relationship_type=relationship_type
            )

        return graph_node_id, vector_memory_id

    def search_memories(self, query: MemoryQuery) -> List[MemoryResult]:
        """Search memories using hybrid graph and vector approach."""
        self.stats["total_queries"] += 1

        # Check cache first
        cache_key = self._get_cache_key(query)
        if cache_key in self.query_cache:
            self.stats["cache_hits"] += 1
            return self.query_cache[cache_key]

        results = []

        # Perform vector search
        vector_results = self.vector_memory.search_memories(
            query=query.query_text,
            k=query.max_results,
            memory_types=[mt.value for mt in query.memory_types] if query.memory_types else None,
            similarity_threshold=query.similarity_threshold,
        )

        self.stats["vector_searches"] += 1

        # Convert vector results to MemoryResult objects
        for vector_memory, similarity_score in vector_results:
            # Get corresponding graph node if available
            graph_node_id = vector_memory.metadata.get("graph_node_id")
            memory_node = None

            if graph_node_id:
                memory_node = self.graph_memory.get_node(graph_node_id)

            # Calculate relevance score
            relevance_score = similarity_score * vector_memory.importance

            # Filter by importance threshold
            if relevance_score >= query.importance_threshold:
                result = MemoryResult(
                    memory_node=memory_node,
                    vector_memory=vector_memory,
                    similarity_score=similarity_score,
                    relevance_score=relevance_score,
                    metadata=vector_memory.metadata,
                )
                results.append(result)

        # Perform graph search if relationship types specified
        if query.relationship_types:
            graph_results = self._search_graph_memories(query)
            self.stats["graph_searches"] += 1

            # Merge graph results with vector results
            results = self._merge_search_results(results, graph_results, query)
            self.stats["hybrid_searches"] += 1

        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        # Limit results
        results = results[: query.max_results]

        # Cache results
        self._cache_results(cache_key, results)

        return results

    def _search_graph_memories(self, query: MemoryQuery) -> List[MemoryResult]:
        """Search graph memories based on relationships."""
        results = []

        # Search for nodes by content
        graph_nodes = self.graph_memory.search_nodes(query.query_text, limit=query.max_results)

        for node in graph_nodes:
            # Check memory type filter
            if query.memory_types and node.memory_type not in query.memory_types:
                continue

            # Check importance threshold
            if node.importance < query.importance_threshold:
                continue

            # Find related nodes
            related_nodes = self.graph_memory.get_neighbors(
                node.node_id,
                relationship_type=query.relationship_types[0] if query.relationship_types else None,
            )

            # Calculate relevance score
            relevance_score = node.importance * node.accessibility

            result = MemoryResult(
                memory_node=node,
                similarity_score=0.0,  # Graph search doesn't provide similarity scores
                relevance_score=relevance_score,
                relationship_path=[node.node_id]
                + [neighbor.node_id for neighbor, _ in related_nodes],
                metadata={"search_type": "graph"},
            )
            results.append(result)

        return results

    def _merge_search_results(
        self,
        vector_results: List[MemoryResult],
        graph_results: List[MemoryResult],
        query: MemoryQuery,
    ) -> List[MemoryResult]:
        """Merge vector and graph search results."""
        # Create a map of results by memory ID
        result_map = {}

        # Add vector results
        for result in vector_results:
            if result.vector_memory:
                memory_id = result.vector_memory.memory_id
            elif result.memory_node:
                memory_id = result.memory_node.node_id
            else:
                continue
            result_map[memory_id] = result

        # Merge graph results
        for graph_result in graph_results:
            if not graph_result.memory_node:
                continue
            memory_id = graph_result.memory_node.node_id
            if memory_id in result_map:
                # Combine scores
                existing_result = result_map[memory_id]
                existing_result.relevance_score = max(
                    existing_result.relevance_score, graph_result.relevance_score
                )
                existing_result.relationship_path = graph_result.relationship_path
            else:
                result_map[memory_id] = graph_result

        return list(result_map.values())

    def get_agent_memories(
        self, agent_id: str, memory_types: Optional[List[MemoryType]] = None, limit: int = 50
    ) -> List[MemoryResult]:
        """Get all memories associated with an agent."""
        query = MemoryQuery(query_text=agent_id, memory_types=memory_types or [], max_results=limit)

        results = self.search_memories(query)

        # Filter to only include memories from this agent
        agent_results = []
        for result in results:
            if result.vector_memory:
                if result.vector_memory.metadata.get("agent_id") == agent_id:
                    agent_results.append(result)
            elif result.memory_node:
                # Check if this memory is related to the agent
                neighbors = self.graph_memory.get_neighbors(
                    result.memory_node.node_id, relationship_type=RelationshipType.CREATED
                )
                for neighbor, _ in neighbors:
                    if neighbor.node_id == agent_id:
                        agent_results.append(result)
                        break

        return agent_results

    def get_memory_context(self, memory_id: str, context_radius: int = 2) -> Dict[str, Any]:
        """Get contextual information around a memory."""
        context: Dict[str, Any] = {
            "memory": None,
            "related_memories": [],
            "relationships": [],
            "timeline": [],
        }

        # Get the memory
        memory = self.graph_memory.get_node(memory_id)
        if memory:
            context["memory"] = memory.to_dict()

            # Get related memories
            related_memories = self.graph_memory.get_neighbors(memory_id)
            context["related_memories"] = [
                {"memory": neighbor.to_dict(), "relationship": edge.to_dict()}
                for neighbor, edge in related_memories
            ]

            # Get relationship paths
            if context_radius > 1:
                # Get second-degree relationships
                for neighbor, _ in related_memories:
                    second_degree = self.graph_memory.get_neighbors(neighbor.node_id)
                    context["relationships"].extend(
                        [
                            {"memory": neighbor.to_dict(), "relationship": edge.to_dict()}
                            for neighbor, edge in second_degree
                        ]
                    )

        return context

    def consolidate_agent_memories(self, agent_id: str) -> Dict[str, Any]:
        """Consolidate and organize an agent's memories."""
        consolidation_result: Dict[str, Any] = {
            "total_memories": 0,
            "episodic_memories": 0,
            "semantic_memories": 0,
            "social_memories": 0,
            "consolidated_concepts": [],
            "memory_clusters": [],
            "timeline": [],
        }

        # Get all agent memories
        agent_memories = self.get_agent_memories(agent_id)
        consolidation_result["total_memories"] = len(agent_memories)

        # Categorize memories
        for result in agent_memories:
            if result.vector_memory:
                memory_type = result.vector_memory.memory_type
                if memory_type == "episodic":
                    consolidation_result["episodic_memories"] += 1
                elif memory_type == "semantic":
                    consolidation_result["semantic_memories"] += 1
                elif memory_type == "social":
                    consolidation_result["social_memories"] += 1

        # Create memory clusters based on content similarity
        if len(agent_memories) > 1:
            clusters = self._cluster_memories(agent_memories)
            consolidation_result["memory_clusters"] = clusters

        # Extract consolidated concepts
        concepts = self._extract_concepts(agent_memories)
        consolidation_result["consolidated_concepts"] = concepts

        # Create timeline
        timeline = self._create_memory_timeline(agent_memories)
        consolidation_result["timeline"] = timeline

        return consolidation_result

    def _cluster_memories(
        self, memories: List[MemoryResult], similarity_threshold: float = 0.7
    ) -> List[List[Dict[str, Any]]]:
        """Cluster memories based on content similarity."""
        if len(memories) < 2:
            return []

        clusters = []
        processed = set()

        for i, memory in enumerate(memories):
            if i in processed:
                continue

            cluster = [memory.to_dict()]
            processed.add(i)

            # Find similar memories
            for j, other_memory in enumerate(memories[i + 1 :], i + 1):
                if j in processed:
                    continue

                # Calculate similarity (simplified)
                if (
                    memory.vector_memory
                    and other_memory.vector_memory
                    and memory.similarity_score >= similarity_threshold
                ):
                    cluster.append(other_memory.to_dict())
                    processed.add(j)

            if len(cluster) > 1:
                clusters.append(cluster)

        return clusters

    def _extract_concepts(self, memories: List[MemoryResult]) -> List[Dict[str, Any]]:
        """Extract key concepts from memories."""
        concept_counts: Dict[str, int] = defaultdict(int)
        concept_examples = defaultdict(list)

        for memory in memories:
            if memory.vector_memory:
                content = memory.vector_memory.content
                # Simple concept extraction (in production, use NLP)
                words = content.lower().split()
                for word in words:
                    if len(word) > 3:  # Filter short words
                        concept_counts[word] += 1
                        concept_examples[word].append(content[:100])

        # Get top concepts
        top_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:20]

        concepts = []
        for concept, count in top_concepts:
            concepts.append(
                {
                    "concept": concept,
                    "frequency": count,
                    "examples": concept_examples[concept][:3],  # Top 3 examples
                }
            )

        return concepts

    def _create_memory_timeline(self, memories: List[MemoryResult]) -> List[Dict[str, Any]]:
        """Create a timeline of memories."""
        timeline_entries: List[Dict[str, Any]] = []

        for memory in memories:
            timestamp = None
            if memory.vector_memory:
                timestamp = memory.vector_memory.created_at
            elif memory.memory_node:
                timestamp = memory.memory_node.created_at

            if timestamp:
                if memory.vector_memory:
                    content = memory.vector_memory.content
                    mem_type = memory.vector_memory.memory_type
                    importance = memory.vector_memory.importance
                elif memory.memory_node:
                    content = memory.memory_node.content
                    mem_type = memory.memory_node.memory_type.value
                    importance = memory.memory_node.importance
                else:
                    continue
                timeline_entries.append(
                    {
                        "timestamp": timestamp.isoformat(),
                        "content": content,
                        "type": mem_type,
                        "importance": importance,
                    }
                )

        # Sort by timestamp
        timeline_entries.sort(key=lambda x: x["timestamp"])
        return timeline_entries

    def _get_cache_key(self, query: MemoryQuery) -> str:
        """Generate cache key for query."""
        return f"{query.query_text}_{query.memory_types}_{query.relationship_types}_{query.max_results}"

    def _cache_results(self, cache_key: str, results: List[MemoryResult]) -> None:
        """Cache search results."""
        if len(self.query_cache) >= self.cache_size:
            # Remove oldest entries
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]

        self.query_cache[cache_key] = results

    def cleanup_old_memories(
        self, age_threshold_days: int = 30, importance_threshold: float = 0.1
    ) -> Dict[str, int]:
        """Clean up old and unimportant memories."""
        cleanup_stats = {
            "graph_memories_removed": 0,
            "vector_memories_removed": 0,
            "relationships_removed": 0,
        }

        # Clean up graph memories
        threshold_date = datetime.now() - timedelta(days=age_threshold_days)
        nodes_to_remove = []

        for node_id, node in self.graph_memory.nodes.items():
            if (
                node.created_at < threshold_date
                and node.importance < importance_threshold
                and node.access_count < 5
            ):
                nodes_to_remove.append(node_id)

        for node_id in nodes_to_remove:
            self.graph_memory.remove_node(node_id)
            cleanup_stats["graph_memories_removed"] += 1

        # Clean up vector memories (simplified - would need more sophisticated approach)
        # This is a placeholder for vector memory cleanup

        return cleanup_stats

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics."""
        graph_stats = self.graph_memory.get_memory_statistics()
        vector_stats = self.vector_memory.get_memory_statistics()

        return {
            "graph_memory": graph_stats,
            "vector_memory": vector_stats,
            "graph_backend": self.graph_memory.backend,
            "neo4j_connected": self.graph_memory.neo4j_driver is not None,
            "query_stats": self.stats.copy(),
            "cache_stats": {
                "cache_size": len(self.query_cache),
                "cache_hit_rate": self.stats["cache_hits"] / max(1, self.stats["total_queries"]),
            },
            "total_memories": graph_stats["total_nodes"] + vector_stats["total_memories"],
        }

    def save_memory_system(self, filename: str) -> None:
        """Save the entire memory system to files."""
        # Save graph memory
        graph_filename = f"{filename}_graph.json"
        self.graph_memory.save_to_file(graph_filename)

        # Save vector memory
        vector_filename = f"{filename}_vector.json"
        self.vector_memory.export_memories(vector_filename)

        # Save statistics
        stats_filename = f"{filename}_stats.json"
        import json

        with open(stats_filename, "w") as f:
            json.dump(self.get_memory_statistics(), f, indent=2, default=str)

    def load_memory_system(self, filename: str) -> None:
        """Load the entire memory system from files."""
        # Load graph memory
        graph_filename = f"{filename}_graph.json"
        self.graph_memory.load_from_file(graph_filename)

        # Load vector memory
        vector_filename = f"{filename}_vector.json"
        self.vector_memory.import_memories(vector_filename)

    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=True)
