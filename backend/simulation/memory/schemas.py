"""
Memory schemas and data structures for agent memory systems.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MemoryType(Enum):
    """Types of memory nodes."""

    EVENT = "event"
    CONCEPT = "concept"
    AGENT = "agent"
    MYTH = "myth"
    NORM = "norm"
    SLANG = "slang"
    RESOURCE = "resource"
    LOCATION = "location"


class RelationshipType(Enum):
    """Types of relationships between memory nodes."""

    CAUSES = "causes"
    PRECEDES = "precedes"
    INVOLVES = "involves"
    CREATES = "creates"
    CONTRADICTS = "contradicts"
    DERIVES_FROM = "derives_from"
    TRUSTS = "trusts"
    BETRAYS = "betrays"
    TRADES_WITH = "trades_with"
    ALLIES_WITH = "allies_with"
    ENEMIES_WITH = "enemies_with"
    REFERENCES = "references"
    SIMILAR_TO = "similar_to"


@dataclass
class MemoryEvent:
    """An episodic memory event."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    tick: int = 0
    event_type: str = ""
    description: str = ""
    participants: List[str] = field(default_factory=list)
    outcome: str = ""
    emotional_valence: float = 0.0  # -1.0 to 1.0
    importance: float = 0.5  # 0.0 to 1.0
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MemoryConcept:
    """A semantic memory concept."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = ""
    definition: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    associations: List[str] = field(default_factory=list)
    confidence: float = 0.5  # 0.0 to 1.0
    last_accessed: datetime = field(default_factory=datetime.now)


@dataclass
class MemoryRelationship:
    """A relationship between memory nodes."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""
    relationship_type: RelationshipType = RelationshipType.REFERENCES
    strength: float = 1.0  # 0.0 to 1.0
    confidence: float = 0.5  # 0.0 to 1.0
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentMemory:
    """Agent's personal memory system."""

    agent_id: str = ""
    episodic_memories: List[MemoryEvent] = field(default_factory=list)
    semantic_memories: Dict[str, MemoryConcept] = field(default_factory=dict)
    social_memories: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    max_episodic_memories: int = 1000
    consolidation_threshold: int = 50

    def add_event(self, event):
        """Add an episodic memory event.

        Accepts either a ``MemoryEvent`` or a plain ``dict`` describing the
        event (the dict may use ``type`` or ``event_type`` for the kind).
        """
        if isinstance(event, dict):
            event = MemoryEvent(
                tick=event.get("tick", 0),
                event_type=event.get("event_type", event.get("type", "")),
                description=event.get("description", ""),
                participants=event.get("participants", []),
                outcome=event.get("outcome", ""),
                emotional_valence=event.get("emotional_valence", 0.0),
                importance=event.get("importance", 0.5),
                context=event.get("context", {}),
            )
        self.episodic_memories.append(event)

        # Maintain memory limit
        if len(self.episodic_memories) > self.max_episodic_memories:
            # Remove oldest, least important memories
            self.episodic_memories.sort(key=lambda e: e.importance)
            self.episodic_memories = self.episodic_memories[-self.max_episodic_memories :]

    def add_concept(self, concept: MemoryConcept):
        """Add or update a semantic memory concept."""
        self.semantic_memories[concept.name] = concept

    def get_recent_events(
        self, limit: int = 10, event_type: Optional[str] = None
    ) -> List[MemoryEvent]:
        """Get recent episodic memories."""
        events = self.episodic_memories

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Sort by tick (most recent first)
        events.sort(key=lambda e: e.tick, reverse=True)
        return events[:limit]

    def get_events_with_participant(
        self, participant_id: str, limit: int = 10
    ) -> List[MemoryEvent]:
        """Get events involving a specific participant."""
        events = [e for e in self.episodic_memories if participant_id in e.participants]
        events.sort(key=lambda e: e.tick, reverse=True)
        return events[:limit]

    def get_concept(self, name: str) -> Optional[MemoryConcept]:
        """Get a semantic memory concept."""
        return self.semantic_memories.get(name)

    def search_concepts(self, query: str) -> List[MemoryConcept]:
        """Search for concepts matching a query."""
        query_lower = query.lower()
        matches = []

        for concept in self.semantic_memories.values():
            if (
                query_lower in concept.name.lower()
                or query_lower in concept.definition.lower()
                or any(
                    query_lower in attr.lower()
                    for attr in concept.attributes.values()
                    if isinstance(attr, str)
                )
            ):
                matches.append(concept)

        # Sort by confidence
        matches.sort(key=lambda c: c.confidence, reverse=True)
        return matches

    def update_social_memory(
        self, other_agent_id: str, interaction_type: str, outcome: str, emotional_valence: float
    ):
        """Update social memory about another agent."""
        if other_agent_id not in self.social_memories:
            self.social_memories[other_agent_id] = {
                "interactions": [],
                "trust_level": 0.0,
                "last_interaction": None,
            }

        social_mem = self.social_memories[other_agent_id]
        social_mem["interactions"].append(
            {
                "type": interaction_type,
                "outcome": outcome,
                "emotional_valence": emotional_valence,
                "timestamp": datetime.now(),
            }
        )

        # Update trust level based on interactions
        recent_interactions = social_mem["interactions"][-10:]  # Last 10 interactions
        if recent_interactions:
            avg_valence = sum(i["emotional_valence"] for i in recent_interactions) / len(
                recent_interactions
            )
            social_mem["trust_level"] = 0.7 * social_mem["trust_level"] + 0.3 * avg_valence
            social_mem["trust_level"] = max(-1.0, min(1.0, social_mem["trust_level"]))

        social_mem["last_interaction"] = datetime.now()

    def consolidate(self, current_tick: int):
        """Consolidate memories - convert important events to concepts."""
        # Find important events that might become concepts
        important_events = [
            e
            for e in self.episodic_memories
            if e.importance > 0.7 and current_tick - e.tick > self.consolidation_threshold
        ]

        for event in important_events:
            # Create concept from important event
            concept_name = f"{event.event_type}_{event.tick}"
            if concept_name not in self.semantic_memories:
                concept = MemoryConcept(
                    name=concept_name,
                    category=event.event_type,
                    definition=event.description,
                    attributes={
                        "tick": event.tick,
                        "outcome": event.outcome,
                        "participants": event.participants,
                        "emotional_valence": event.emotional_valence,
                    },
                    confidence=event.importance,
                )
                self.add_concept(concept)

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of agent's memory state."""
        return {
            "agent_id": self.agent_id,
            "episodic_count": len(self.episodic_memories),
            "semantic_count": len(self.semantic_memories),
            "social_count": len(self.social_memories),
            "recent_events": len(self.get_recent_events(limit=10)),
            "avg_importance": (
                sum(e.importance for e in self.episodic_memories) / len(self.episodic_memories)
            )
            if self.episodic_memories
            else 0.0,
        }
