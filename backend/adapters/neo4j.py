"""
Neo4j adapter for graph-based memory and knowledge storage.

Provides integration with Neo4j database for storing agent relationships,
cultural knowledge, and semantic memory graphs.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from neo4j import AsyncDriver, AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable


@dataclass
class Neo4jConfig:
    """Configuration for Neo4j adapter."""

    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "password"
    database: str = "neo4j"
    max_connection_lifetime: int = 3600
    max_connection_pool_size: int = 50


class Neo4jAdapter:
    """Neo4j adapter for graph-based memory storage."""

    def __init__(self, config: Neo4jConfig):
        self.config = config
        self.driver: Optional[AsyncDriver] = None
        self._connected = False

    async def connect(self) -> bool:
        """Connect to Neo4j database."""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.config.uri,
                auth=(self.config.username, self.config.password),
                max_connection_lifetime=self.config.max_connection_lifetime,
                max_connection_pool_size=self.config.max_connection_pool_size,
            )

            # Test connection
            async with self.driver.session(database=self.config.database) as session:
                await session.run("RETURN 1")

            self._connected = True
            print(f"Connected to Neo4j at {self.config.uri}")
            return True

        except ServiceUnavailable as e:
            print(f"Failed to connect to Neo4j: {e}")
            self._connected = False
            return False
        except Exception as e:
            print(f"Neo4j connection error: {e}")
            self._connected = False
            return False

    async def disconnect(self):
        """Disconnect from Neo4j database."""
        if self.driver:
            await self.driver.close()
            self._connected = False
            print("Disconnected from Neo4j")

    async def ensure_schema(self):
        """Ensure required schema exists."""
        if not self._connected or self.driver is None:
            raise RuntimeError("Not connected to Neo4j")

        schema_queries = [
            # Create constraints
            "CREATE CONSTRAINT agent_id_unique IF NOT EXISTS FOR (a:Agent) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT myth_id_unique IF NOT EXISTS FOR (m:Myth) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT norm_id_unique IF NOT EXISTS FOR (n:Norm) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT slang_id_unique IF NOT EXISTS FOR (s:Slang) REQUIRE s.id IS UNIQUE",
            # Create indexes
            "CREATE INDEX agent_name_index IF NOT EXISTS FOR (a:Agent) ON (a.name)",
            "CREATE INDEX myth_theme_index IF NOT EXISTS FOR (m:Myth) ON (m.theme)",
            "CREATE INDEX norm_type_index IF NOT EXISTS FOR (n:Norm) ON (n.type)",
        ]

        async with self.driver.session(database=self.config.database) as session:
            for query in schema_queries:
                try:
                    await session.run(query)
                except Exception as e:
                    print(f"Schema creation warning: {e}")

    async def save_agent(self, agent_data: Dict[str, Any]) -> bool:
        """Save agent data to Neo4j."""
        if not self._connected or self.driver is None:
            return False

        try:
            async with self.driver.session(database=self.config.database) as session:
                await session.run(
                    """
                    MERGE (a:Agent {id: $agent_id})
                    SET a.name = $name,
                        a.generation = $generation,
                        a.faction_id = $faction_id,
                        a.influence = $influence,
                        a.satisfaction = $satisfaction,
                        a.personality = $personality,
                        a.resources = $resources,
                        a.updated_at = timestamp()
                """,
                    agent_data,
                )

            return True
        except Exception as e:
            print(f"Error saving agent: {e}")
            return False

    async def save_agent_relationship(
        self,
        agent1_id: str,
        agent2_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Save relationship between agents."""
        if not self._connected or self.driver is None:
            return False

        try:
            props = properties or {}
            props["updated_at"] = "timestamp()"

            async with self.driver.session(database=self.config.database) as session:
                await session.run(
                    f"""
                    MATCH (a1:Agent {{id: $agent1_id}}), (a2:Agent {{id: $agent2_id}})
                    MERGE (a1)-[r:{relationship_type}]->(a2)
                    SET r += $properties
                """,
                    {"agent1_id": agent1_id, "agent2_id": agent2_id, "properties": props},
                )

            return True
        except Exception as e:
            print(f"Error saving relationship: {e}")
            return False

    async def save_myth(self, myth_data: Dict[str, Any]) -> bool:
        """Save myth to Neo4j."""
        if not self._connected or self.driver is None:
            return False

        try:
            async with self.driver.session(database=self.config.database) as session:
                await session.run(
                    """
                    MERGE (m:Myth {id: $myth_id})
                    SET m.title = $title,
                        m.content = $content,
                        m.theme = $theme,
                        m.creator_id = $creator_id,
                        m.tick_created = $tick_created,
                        m.popularity = $popularity,
                        m.influence = $influence,
                        m.updated_at = timestamp()

                    WITH m
                    MATCH (creator:Agent {id: $creator_id})
                    MERGE (creator)-[:CREATED]->(m)
                """,
                    myth_data,
                )

            return True
        except Exception as e:
            print(f"Error saving myth: {e}")
            return False

    async def save_norm(self, norm_data: Dict[str, Any]) -> bool:
        """Save norm to Neo4j."""
        if not self._connected or self.driver is None:
            return False

        try:
            async with self.driver.session(database=self.config.database) as session:
                await session.run(
                    """
                    MERGE (n:Norm {id: $norm_id})
                    SET n.title = $title,
                        n.description = $description,
                        n.type = $type,
                        n.proposer_id = $proposer_id,
                        n.tick_proposed = $tick_proposed,
                        n.status = $status,
                        n.compliance_rate = $compliance_rate,
                        n.updated_at = timestamp()

                    WITH n
                    MATCH (proposer:Agent {id: $proposer_id})
                    MERGE (proposer)-[:PROPOSED]->(n)
                """,
                    norm_data,
                )

            return True
        except Exception as e:
            print(f"Error saving norm: {e}")
            return False

    async def save_slang(self, slang_data: Dict[str, Any]) -> bool:
        """Save slang to Neo4j."""
        if not self._connected or self.driver is None:
            return False

        try:
            async with self.driver.session(database=self.config.database) as session:
                await session.run(
                    """
                    MERGE (s:Slang {id: $slang_id})
                    SET s.word = $word,
                        s.meaning = $meaning,
                        s.creator_id = $creator_id,
                        s.tick_created = $tick_created,
                        s.popularity = $popularity,
                        s.adoption_rate = $adoption_rate,
                        s.updated_at = timestamp()

                    WITH s
                    MATCH (creator:Agent {id: $creator_id})
                    MERGE (creator)-[:CREATED]->(s)
                """,
                    slang_data,
                )

            return True
        except Exception as e:
            print(f"Error saving slang: {e}")
            return False

    async def get_agent_network(self, limit: int = 1000) -> Dict[str, Any]:
        """Get agent network data for visualization."""
        if not self._connected or self.driver is None:
            return {"nodes": [], "edges": []}

        try:
            async with self.driver.session(database=self.config.database) as session:
                # Get agents
                agents_result = await session.run(
                    """
                    MATCH (a:Agent)
                    RETURN a.id as id, a.name as name, a.faction_id as faction_id,
                           a.influence as influence, a.satisfaction as satisfaction,
                           a.personality as personality
                    LIMIT $limit
                """,
                    limit=limit,
                )

                nodes = []
                async for record in agents_result:
                    nodes.append(
                        {
                            "id": record["id"],
                            "name": record["name"],
                            "faction_id": record["faction_id"],
                            "influence": record["influence"],
                            "satisfaction": record["satisfaction"],
                            "personality": record["personality"],
                        }
                    )

                # Get relationships
                edges_result = await session.run(
                    """
                    MATCH (a1:Agent)-[r]->(a2:Agent)
                    WHERE type(r) IN ['TRUSTS', 'TRADES_WITH', 'ALLIES_WITH', 'ENEMIES_WITH']
                    RETURN a1.id as source, a2.id as target, type(r) as relationship_type,
                           r.trust_level as trust_level, r.interaction_count as interaction_count
                    LIMIT $limit
                """,
                    limit=limit,
                )

                edges = []
                async for record in edges_result:
                    edges.append(
                        {
                            "source": record["source"],
                            "target": record["target"],
                            "relationship_type": record["relationship_type"],
                            "trust_level": record["trust_level"],
                            "interaction_count": record["interaction_count"],
                        }
                    )

                return {"nodes": nodes, "edges": edges}

        except Exception as e:
            print(f"Error getting agent network: {e}")
            return {"nodes": [], "edges": []}

    async def get_cultural_graph(self) -> Dict[str, Any]:
        """Get cultural knowledge graph."""
        if not self._connected or self.driver is None:
            return {"myths": [], "norms": [], "slang": []}

        try:
            async with self.driver.session(database=self.config.database) as session:
                # Get myths
                myths_result = await session.run(
                    """
                    MATCH (m:Myth)
                    RETURN m.id as id, m.title as title, m.theme as theme,
                           m.creator_id as creator_id, m.popularity as popularity,
                           m.tick_created as tick_created
                    ORDER BY m.popularity DESC
                    LIMIT 50
                """
                )

                myths = []
                async for record in myths_result:
                    myths.append(
                        {
                            "id": record["id"],
                            "title": record["title"],
                            "theme": record["theme"],
                            "creator_id": record["creator_id"],
                            "popularity": record["popularity"],
                            "tick_created": record["tick_created"],
                        }
                    )

                # Get norms
                norms_result = await session.run(
                    """
                    MATCH (n:Norm)
                    WHERE n.status = 'active'
                    RETURN n.id as id, n.title as title, n.type as type,
                           n.proposer_id as proposer_id, n.compliance_rate as compliance_rate,
                           n.tick_proposed as tick_proposed
                    ORDER BY n.compliance_rate DESC
                    LIMIT 50
                """
                )

                norms = []
                async for record in norms_result:
                    norms.append(
                        {
                            "id": record["id"],
                            "title": record["title"],
                            "type": record["type"],
                            "proposer_id": record["proposer_id"],
                            "compliance_rate": record["compliance_rate"],
                            "tick_proposed": record["tick_proposed"],
                        }
                    )

                # Get slang
                slang_result = await session.run(
                    """
                    MATCH (s:Slang)
                    RETURN s.id as id, s.word as word, s.meaning as meaning,
                           s.creator_id as creator_id, s.popularity as popularity,
                           s.adoption_rate as adoption_rate, s.tick_created as tick_created
                    ORDER BY s.popularity DESC
                    LIMIT 100
                """
                )

                slang = []
                async for record in slang_result:
                    slang.append(
                        {
                            "id": record["id"],
                            "word": record["word"],
                            "meaning": record["meaning"],
                            "creator_id": record["creator_id"],
                            "popularity": record["popularity"],
                            "adoption_rate": record["adoption_rate"],
                            "tick_created": record["tick_created"],
                        }
                    )

                return {"myths": myths, "norms": norms, "slang": slang}

        except Exception as e:
            print(f"Error getting cultural graph: {e}")
            return {"myths": [], "norms": [], "slang": []}

    async def get_knowledge_graph_query(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Execute a custom Cypher query on the knowledge graph."""
        if not self._connected or self.driver is None:
            return []

        try:
            async with self.driver.session(database=self.config.database) as session:
                result = await session.run(f"{query} LIMIT {limit}")

                records = []
                async for record in result:
                    records.append(dict(record))

                return records

        except Exception as e:
            print(f"Error executing query: {e}")
            return []

    async def clear_database(self):
        """Clear all data from the database."""
        if not self._connected or self.driver is None:
            return

        try:
            async with self.driver.session(database=self.config.database) as session:
                await session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared")
        except Exception as e:
            print(f"Error clearing database: {e}")

    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if not self._connected or self.driver is None:
            return {}

        try:
            async with self.driver.session(database=self.config.database) as session:
                # Get node counts
                result = await session.run(
                    """
                    MATCH (n)
                    RETURN labels(n) as labels, count(n) as count
                    ORDER BY count DESC
                """
                )

                node_counts = {}
                async for record in result:
                    labels = record["labels"]
                    count = record["count"]
                    if labels:
                        label = labels[0]
                        node_counts[label] = count

                # Get relationship counts
                rel_result = await session.run(
                    """
                    MATCH ()-[r]->()
                    RETURN type(r) as type, count(r) as count
                    ORDER BY count DESC
                """
                )

                rel_counts = {}
                async for record in rel_result:
                    rel_type = record["type"]
                    count = record["count"]
                    rel_counts[rel_type] = count

                return {
                    "nodes": node_counts,
                    "relationships": rel_counts,
                    "total_nodes": sum(node_counts.values()),
                    "total_relationships": sum(rel_counts.values()),
                }

        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}
