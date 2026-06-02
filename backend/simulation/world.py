"""
World state management for the simulation.

Handles the overall world state, agent management, faction dynamics,
and coordinates between different simulation systems.
"""

import random
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .agents import Agent, AgentPersonality
from .culture import Culture
from .economy import Economy
from .events import EventSystem
from .memory import AgentMemory
from .memory.manager import MemoryManager
from .negotiation import NegotiationEngine
from .social import SocialEngine


class WorldState(Enum):
    """World simulation states."""

    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class Faction:
    """A faction or group of agents with shared ideology."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    ideology: List[float] = field(default_factory=lambda: [random.random() for _ in range(10)])
    leader_id: Optional[str] = None
    member_ids: Set[str] = field(default_factory=set)
    influence: float = 1.0
    resources: Dict[str, float] = field(default_factory=dict)
    goals: List[str] = field(default_factory=list)
    tick_created: int = 0

    def add_member(self, agent_id: str):
        """Add member to faction."""
        self.member_ids.add(agent_id)

    def remove_member(self, agent_id: str):
        """Remove member from faction."""
        self.member_ids.discard(agent_id)

    def get_member_count(self) -> int:
        """Get number of faction members."""
        return len(self.member_ids)

    def to_dict(self) -> Dict[str, Any]:
        """Convert faction to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "leader_id": self.leader_id,
            "member_count": self.get_member_count(),
            "influence": self.influence,
            "resources": self.resources,
            "goals": self.goals,
            "tick_created": self.tick_created,
        }


@dataclass
class World:
    """The main world state managing agents, factions, and systems."""

    # Core state
    state: WorldState = WorldState.INITIALIZING
    current_tick: int = 0
    seed: Optional[int] = None

    # Agents and factions
    agents: Dict[str, Agent] = field(default_factory=dict)
    factions: Dict[str, Faction] = field(default_factory=dict)

    # Systems
    economy: Economy = field(default_factory=Economy)
    culture: Culture = field(default_factory=Culture)
    event_system: EventSystem = field(default_factory=EventSystem)
    social_engine: SocialEngine = field(default_factory=SocialEngine)
    negotiation_engine: NegotiationEngine = field(default_factory=NegotiationEngine)
    memory_manager: Optional[MemoryManager] = None

    # Statistics
    stats: Dict[str, Any] = field(default_factory=dict)
    tick_history: List[Dict[str, Any]] = field(default_factory=list)

    # Configuration
    max_agents: int = 1000
    max_factions: int = 20
    tick_limit: int = 10000
    memory_backend: str = "networkx"  # "networkx" or "neo4j"
    vector_backend: str = "faiss"  # "faiss" or "chroma"

    def __post_init__(self):
        """Initialize world after creation."""
        if self.seed is not None:
            random.seed(self.seed)

        # Build the hybrid memory store with the configured backends. When
        # memory_backend == "neo4j" the graph writes through to Neo4j.
        if self.memory_manager is None:
            self.memory_manager = MemoryManager(
                graph_backend=self.memory_backend,
                vector_backend=self.vector_backend,
            )

        # Initialize statistics
        self.stats = {
            "total_agents": 0,
            "total_factions": 0,
            "total_trades": 0,
            "total_myths": 0,
            "total_norms": 0,
            "total_events": 0,
            "avg_satisfaction": 0.0,
            "avg_influence": 0.0,
            "gini_coefficient": 0.0,
        }

    def add_agent(self, agent: Agent) -> bool:
        """Add agent to the world."""
        if len(self.agents) >= self.max_agents:
            return False

        self.agents[agent.id] = agent
        self.stats["total_agents"] = len(self.agents)
        return True

    def remove_agent(self, agent_id: str) -> bool:
        """Remove agent from the world."""
        if agent_id not in self.agents:
            return False

        agent = self.agents[agent_id]

        # Remove from faction if applicable
        if agent.faction_id and agent.faction_id in self.factions:
            self.factions[agent.faction_id].remove_member(agent_id)

        # Remove from world
        del self.agents[agent_id]
        self.stats["total_agents"] = len(self.agents)
        return True

    def create_faction(self, name: str, leader_id: Optional[str] = None) -> Optional[Faction]:
        """Create a new faction."""
        if len(self.factions) >= self.max_factions:
            return None

        faction = Faction(name=name, leader_id=leader_id, tick_created=self.current_tick)

        self.factions[faction.id] = faction
        self.stats["total_factions"] = len(self.factions)

        # Add leader to faction if specified
        if leader_id and leader_id in self.agents:
            self.add_agent_to_faction(leader_id, faction.id)
            self.agents[leader_id].faction_id = faction.id

        return faction

    def add_agent_to_faction(self, agent_id: str, faction_id: str) -> bool:
        """Add agent to faction."""
        if agent_id not in self.agents or faction_id not in self.factions:
            return False

        agent = self.agents[agent_id]
        faction = self.factions[faction_id]

        # Remove from current faction if any
        if agent.faction_id and agent.faction_id in self.factions:
            self.factions[agent.faction_id].remove_member(agent_id)

        # Add to new faction
        faction.add_member(agent_id)
        agent.faction_id = faction_id

        return True

    def remove_agent_from_faction(self, agent_id: str) -> bool:
        """Remove agent from their faction."""
        if agent_id not in self.agents:
            return False

        agent = self.agents[agent_id]
        if not agent.faction_id or agent.faction_id not in self.factions:
            return False

        faction = self.factions[agent.faction_id]
        faction.remove_member(agent_id)
        agent.faction_id = None

        # Delete faction if empty
        if faction.get_member_count() == 0:
            del self.factions[faction.id]
            self.stats["total_factions"] = len(self.factions)

        return True

    def update_faction_leadership(self, faction_id: str) -> bool:
        """Update faction leadership based on influence."""
        if faction_id not in self.factions:
            return False

        faction = self.factions[faction_id]
        if not faction.member_ids:
            return False

        # Find member with highest influence
        max_influence = 0.0
        new_leader_id = None

        for member_id in faction.member_ids:
            if member_id in self.agents:
                agent = self.agents[member_id]
                if agent.influence > max_influence:
                    max_influence = agent.influence
                    new_leader_id = member_id

        if new_leader_id:
            faction.leader_id = new_leader_id
            return True

        return False

    def process_faction_dynamics(self):
        """Process faction formation, dissolution, and leadership changes."""
        # Update faction leadership
        for faction in self.factions.values():
            self.update_faction_leadership(faction.id)

        # Check for faction formation
        if random.random() < 0.05:  # 5% chance per tick
            self._attempt_faction_formation()

        # Check for faction dissolution
        if random.random() < 0.02:  # 2% chance per tick
            self._attempt_faction_dissolution()

    def _attempt_faction_formation(self):
        """Attempt to form new factions based on agent alignment."""
        if len(self.factions) >= self.max_factions:
            return

        # Find unaffiliated agents
        unaffiliated = [agent for agent in self.agents.values() if not agent.faction_id]

        if len(unaffiliated) < 3:  # Need at least 3 agents to form faction
            return

        # Group agents by ideology similarity
        ideology_groups = defaultdict(list)

        for agent in unaffiliated:
            # Find similar agents
            similar_agents = []
            for other in unaffiliated:
                if other.id != agent.id:
                    # Calculate ideology similarity (cosine similarity)
                    similarity = self._calculate_ideology_similarity(agent, other)
                    if similarity > 0.7:  # High similarity threshold
                        similar_agents.append(other)

            if len(similar_agents) >= 2:  # Need at least 3 total agents
                group_key = tuple(sorted([agent.id] + [a.id for a in similar_agents]))
                ideology_groups[group_key] = [agent] + similar_agents

        # Create faction from largest group
        if ideology_groups:
            largest_group = max(ideology_groups.values(), key=len)
            if len(largest_group) >= 3:
                leader = max(largest_group, key=lambda a: a.influence)
                faction_name = f"Faction of {leader.name}"

                faction = self.create_faction(faction_name, leader.id)
                if faction:
                    # Add all group members to faction
                    for agent in largest_group:
                        if agent.id != leader.id:
                            self.add_agent_to_faction(agent.id, faction.id)

    def _attempt_faction_dissolution(self):
        """Attempt to dissolve weak factions."""
        for faction in list(self.factions.values()):
            if faction.get_member_count() < 3:  # Too small
                # Dissolve faction
                for member_id in list(faction.member_ids):
                    self.remove_agent_from_faction(member_id)
                del self.factions[faction.id]
                self.stats["total_factions"] = len(self.factions)
            elif faction.get_member_count() >= 3:
                # Check for internal conflict
                avg_trust = 0.0
                trust_count = 0

                for member_id in faction.member_ids:
                    if member_id in self.agents:
                        agent = self.agents[member_id]
                        for other_id in faction.member_ids:
                            if other_id != member_id and other_id in agent.trust_relationships:
                                avg_trust += agent.trust_relationships[other_id].trust_level
                                trust_count += 1

                if trust_count > 0:
                    avg_trust /= trust_count
                    if avg_trust < -0.3:  # High internal conflict
                        # Dissolve faction
                        for member_id in list(faction.member_ids):
                            self.remove_agent_from_faction(member_id)
                        del self.factions[faction.id]
                        self.stats["total_factions"] = len(self.factions)

    def _calculate_ideology_similarity(self, agent1: Agent, agent2: Agent) -> float:
        """Calculate ideology similarity between two agents."""
        from scipy.spatial.distance import cosine

        try:
            similarity = 1 - cosine(agent1.ideology, agent2.ideology)
            return max(0.0, similarity)  # Ensure non-negative
        except Exception:
            return 0.0

    def update_statistics(self):
        """Update world statistics."""
        if not self.agents:
            return

        # Basic counts
        self.stats["total_agents"] = len(self.agents)
        self.stats["total_factions"] = len(self.factions)

        # Economic statistics
        self.stats["total_trades"] = len(self.economy.trade_history)
        self.stats["gini_coefficient"] = self.economy.gini_coefficient

        # Cultural statistics
        self.stats["total_myths"] = len(self.culture.myths)
        self.stats["total_norms"] = len(self.culture.active_norms) + len(
            self.culture.proposed_norms
        )

        # Event statistics
        self.stats["total_events"] = len(self.event_system.event_history)

        # Agent statistics
        satisfactions = [agent.satisfaction for agent in self.agents.values()]
        influences = [agent.influence for agent in self.agents.values()]

        self.stats["avg_satisfaction"] = (
            sum(satisfactions) / len(satisfactions) if satisfactions else 0.0
        )
        self.stats["avg_influence"] = sum(influences) / len(influences) if influences else 0.0

        # Social dynamics (alliances, betrayals, institutions, reputation)
        social_summary = self.social_engine.get_social_summary()
        self.stats["total_alliances"] = social_summary["total_alliances"]
        self.stats["total_betrayals"] = social_summary["total_betrayals"]
        self.stats["total_institutions"] = social_summary["total_institutions"]
        self.stats["avg_reputation"] = social_summary["average_reputation"]

        # Negotiation activity (bilateral negotiation + double-auction fallback)
        negotiation_summary = self.negotiation_engine.get_negotiation_summary()
        self.stats["negotiations_completed"] = negotiation_summary["completed_negotiations"]
        self.stats["negotiations_successful"] = negotiation_summary["successful_negotiations"]
        self.stats["market_clearings"] = negotiation_summary["market_clearings"]

        # Hybrid memory store (graph + vector)
        self.stats["world_memories"] = self.memory_manager.get_memory_statistics()["total_memories"]

    def record_tick_history(self):
        """Record current tick state in history."""
        tick_data = {
            "tick": self.current_tick,
            "agents": len(self.agents),
            "factions": len(self.factions),
            "avg_satisfaction": self.stats.get("avg_satisfaction", 0.0),
            "avg_influence": self.stats.get("avg_influence", 0.0),
            "gini_coefficient": self.stats.get("gini_coefficient", 0.0),
            "active_events": len(self.event_system.active_events),
            "myths": len(self.culture.myths),
            "active_norms": len(self.culture.active_norms),
        }

        self.tick_history.append(tick_data)

        # Keep only recent history (last 1000 ticks)
        if len(self.tick_history) > 1000:
            self.tick_history = self.tick_history[-1000:]

    def get_world_summary(self) -> Dict[str, Any]:
        """Get comprehensive world summary."""
        return {
            "state": self.state.value,
            "current_tick": self.current_tick,
            "seed": self.seed,
            "statistics": self.stats.copy(),
            "factions": [faction.to_dict() for faction in self.factions.values()],
            "economy_summary": self.economy.get_economy_summary(),
            "culture_summary": self.culture.get_cultural_summary(),
            "event_summary": self.event_system.get_event_summary(),
            "social_summary": self.social_engine.get_social_summary(),
            "negotiation_summary": self.negotiation_engine.get_negotiation_summary(),
            "memory_summary": (
                self.memory_manager.get_memory_statistics() if self.memory_manager else {}
            ),
            "recent_history": self.tick_history[-10:] if self.tick_history else [],
        }

    def get_agent_network_data(self) -> Dict[str, Any]:
        """Get agent network data for visualization."""
        nodes = []
        edges = []

        # Create nodes for agents
        for agent in self.agents.values():
            nodes.append(
                {
                    "id": agent.id,
                    "name": agent.name,
                    "faction_id": agent.faction_id,
                    "influence": agent.influence,
                    "satisfaction": agent.satisfaction,
                    "personality": {
                        "openness": agent.personality.openness,
                        "conscientiousness": agent.personality.conscientiousness,
                        "extraversion": agent.personality.extraversion,
                        "agreeableness": agent.personality.agreeableness,
                        "neuroticism": agent.personality.neuroticism,
                    },
                }
            )

        # Create edges for trust relationships
        for agent in self.agents.values():
            for other_id, trust_rel in agent.trust_relationships.items():
                if other_id in self.agents:  # Only include relationships with existing agents
                    edges.append(
                        {
                            "source": agent.id,
                            "target": other_id,
                            "trust_level": trust_rel.trust_level,
                            "interaction_count": trust_rel.interaction_count,
                        }
                    )

        return {"nodes": nodes, "edges": edges}

    def get_cultural_timeline(self) -> List[Dict[str, Any]]:
        """Get cultural timeline for visualization."""
        timeline: List[Dict[str, Any]] = []

        # Add myths
        for myth in self.culture.myths.values():
            timeline.append(
                {
                    "tick": myth.tick_created,
                    "type": "myth",
                    "title": myth.title,
                    "theme": myth.theme,
                    "creator_id": myth.creator_id,
                    "popularity": myth.popularity,
                }
            )

        # Add norms
        for norm in self.culture.active_norms.values():
            timeline.append(
                {
                    "tick": norm.tick_proposed,
                    "type": "norm",
                    "title": norm.title,
                    "norm_type": norm.norm_type,
                    "proposer_id": norm.proposer_id,
                    "compliance_rate": norm.compliance_rate,
                }
            )

        # Sort by tick
        timeline.sort(key=lambda x: x["tick"])
        return timeline

    def initialize_world(self, num_agents: int = 300, seed: Optional[int] = None):
        """Initialize world with agents and basic systems."""
        if seed is not None:
            self.seed = seed
            random.seed(seed)

        # Create agents
        for i in range(num_agents):
            agent = Agent(
                name=f"Agent-{i:03d}",
                personality=AgentPersonality.random(seed + i if seed else None),
                memory=AgentMemory(),
            )
            self.add_agent(agent)

        # Initialize systems
        self.state = WorldState.RUNNING
        self.update_statistics()

        print(f"Initialized world with {len(self.agents)} agents")

    def cleanup(self):
        """Clean up world resources."""
        self.state = WorldState.STOPPED

        # Close the Neo4j driver if the graph memory opened one.
        if self.memory_manager is not None:
            graph = getattr(self.memory_manager, "graph_memory", None)
            if graph is not None and hasattr(graph, "close"):
                graph.close()

        # Clear data structures
        self.agents.clear()
        self.factions.clear()
        self.tick_history.clear()
        self.stats.clear()
