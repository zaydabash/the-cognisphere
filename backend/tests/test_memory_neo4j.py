"""
Tests for the Neo4j write-through backend of the memory graph.

These verify that, when ``backend="neo4j"`` is requested:
  * a reachable server receives MERGE writes for every node and edge, and
  * an unreachable server degrades gracefully to the in-memory NetworkX graph.

A fake driver is injected so the behaviour is verifiable without a live Neo4j.
"""

from unittest.mock import patch

from simulation.memory.graph import (
    MemoryEdge,
    MemoryGraph,
    MemoryNode,
    MemoryType,
    RelationshipType,
)


class _FakeSession:
    def __init__(self, recorder):
        self.recorder = recorder

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def run(self, query, **params):
        self.recorder.append((query, params))


class _FakeDriver:
    def __init__(self, recorder):
        self.recorder = recorder
        self.closed = False

    def verify_connectivity(self):
        return True

    def session(self, database=None):
        return _FakeSession(self.recorder)

    def close(self):
        self.closed = True


def test_neo4j_write_through_persists_nodes_and_edges():
    recorder = []
    fake = _FakeDriver(recorder)

    with patch("neo4j.GraphDatabase.driver", return_value=fake):
        graph = MemoryGraph(backend="neo4j")

    assert graph.neo4j_driver is fake
    assert graph.backend == "neo4j"

    n1 = MemoryNode(content="event one", memory_type=MemoryType.EPISODIC)
    n2 = MemoryNode(content="event two", memory_type=MemoryType.EPISODIC)
    graph.add_node(n1)
    graph.add_node(n2)

    edge = MemoryEdge(
        source_id=n1.node_id,
        target_id=n2.node_id,
        relationship_type=RelationshipType.KNOWS,
    )
    graph.add_edge(edge)

    queries = " ".join(q for q, _ in recorder)
    # Constraint + node MERGEs + edge MERGE should all have been issued.
    assert "CREATE CONSTRAINT" in queries
    assert "MERGE (n:Memory {node_id: $node_id})" in queries
    assert "MERGE (a)-[r:RELATES {edge_id: $edge_id}]->(b)" in queries

    # Nodes still live in the in-memory graph too (write-through, not replace).
    assert graph.get_node(n1.node_id) is n1
    assert graph.get_edge(edge.edge_id) is edge

    graph.close()
    assert fake.closed is True
    assert graph.neo4j_driver is None


def test_neo4j_unreachable_falls_back_to_networkx():
    with patch("neo4j.GraphDatabase.driver", side_effect=Exception("connection refused")):
        graph = MemoryGraph(backend="neo4j")

    # Falls back cleanly: no driver, backend downgraded, still usable.
    assert graph.neo4j_driver is None
    assert graph.backend == "networkx"

    node = MemoryNode(content="still works", memory_type=MemoryType.EPISODIC)
    graph.add_node(node)
    assert graph.get_node(node.node_id) is node


def test_default_backend_is_networkx_without_neo4j():
    graph = MemoryGraph()
    assert graph.backend == "networkx"
    assert graph.neo4j_driver is None
