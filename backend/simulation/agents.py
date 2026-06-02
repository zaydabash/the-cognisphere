"""
Agent cognitive architecture and behavior systems.

Each agent has personality, memory, trust calculus, and capabilities
for negotiation, trade, alliance formation, and cultural creation.
"""

import random
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .culture import Language, Myth, Norm
from .economy import Trade
from .memory import AgentMemory


class AgentState(Enum):
    """Agent behavioral states."""

    IDLE = "idle"
    TRADING = "trading"
    NEGOTIATING = "negotiating"
    REFLECTING = "reflecting"
    CRAFTING = "crafting"
    VOTING = "voting"


@dataclass
class AgentPersonality:
    """OCEAN-style personality vector for agent behavior."""

    openness: float = 0.5
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5

    def to_vector(self) -> np.ndarray:
        """Convert personality to numpy vector."""
        return np.array(
            [
                self.openness,
                self.conscientiousness,
                self.extraversion,
                self.agreeableness,
                self.neuroticism,
            ]
        )

    @classmethod
    def random(cls, seed: Optional[int] = None) -> "AgentPersonality":
        """Generate random personality."""
        if seed is not None:
            random.seed(seed)
        return cls(
            openness=random.uniform(0.0, 1.0),
            conscientiousness=random.uniform(0.0, 1.0),
            extraversion=random.uniform(0.0, 1.0),
            agreeableness=random.uniform(0.0, 1.0),
            neuroticism=random.uniform(0.0, 1.0),
        )


@dataclass
class TrustRelationship:
    """Trust relationship between two agents."""

    target_id: str
    trust_level: float = 0.0  # -1.0 to 1.0
    interaction_count: int = 0
    last_interaction_tick: int = 0
    betrayal_count: int = 0
    cooperation_count: int = 0


@dataclass
class Agent:
    """Core agent with cognitive architecture and capabilities."""

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    generation: int = 0

    # Cognitive architecture
    personality: AgentPersonality = field(default_factory=AgentPersonality)
    memory: AgentMemory = field(default_factory=AgentMemory)
    ideology: np.ndarray = field(default_factory=lambda: np.random.rand(10))

    # Social relationships
    trust_relationships: Dict[str, TrustRelationship] = field(default_factory=dict)
    faction_id: Optional[str] = None
    influence: float = 1.0

    # Resources
    resources: Dict[str, float] = field(
        default_factory=lambda: {
            "food": 100.0,
            "energy": 100.0,
            "artifacts": 10.0,
            "influence": 1.0,
        }
    )

    # Language and culture
    language: Language = field(default_factory=Language)
    created_myths: List[str] = field(default_factory=list)
    voted_norms: Dict[str, bool] = field(default_factory=dict)

    # State
    state: AgentState = AgentState.IDLE
    current_trade: Optional[Trade] = None
    satisfaction: float = 0.5

    def __post_init__(self):
        """Initialize agent after creation."""
        if not self.name:
            self.name = f"Agent-{self.id[:8]}"
        self.memory.agent_id = self.id

    def get_trust_level(self, other_id: str) -> float:
        """Get trust level for another agent."""
        if other_id not in self.trust_relationships:
            return 0.0
        return self.trust_relationships[other_id].trust_level

    def update_trust(self, other_id: str, change: float, tick: int, betrayed: bool = False):
        """Update trust relationship with another agent."""
        if other_id not in self.trust_relationships:
            self.trust_relationships[other_id] = TrustRelationship(
                target_id=other_id, trust_level=0.0
            )

        rel = self.trust_relationships[other_id]
        rel.trust_level = np.clip(rel.trust_level + change, -1.0, 1.0)
        rel.interaction_count += 1
        rel.last_interaction_tick = tick

        if betrayed:
            rel.betrayal_count += 1
        else:
            rel.cooperation_count += 1

    def calculate_utility(self, resources: Dict[str, float]) -> float:
        """Calculate utility from resource bundle using Cobb-Douglas function."""
        if not resources:
            return 0.0

        # Cobb-Douglas utility with personality modifiers
        utility = 1.0
        for resource, amount in resources.items():
            if amount > 0:
                # Personality affects resource preferences
                if resource == "food":
                    weight = 0.3 + 0.2 * self.personality.conscientiousness
                elif resource == "energy":
                    weight = 0.3 + 0.2 * self.personality.extraversion
                elif resource == "artifacts":
                    weight = 0.2 + 0.3 * self.personality.openness
                elif resource == "influence":
                    weight = 0.2 + 0.3 * self.personality.extraversion
                else:
                    weight = 0.1

                utility *= amount**weight

        return utility

    def evaluate_trade_offer(
        self, offer: Dict[str, float], request: Dict[str, float], other_agent_id: str
    ) -> Tuple[bool, float]:
        """Evaluate a trade offer from another agent."""
        # Calculate utility change
        current_utility = self.calculate_utility(self.resources)

        # Simulate resource change
        new_resources = self.resources.copy()
        for resource, amount in offer.items():
            new_resources[resource] = new_resources.get(resource, 0) + amount
        for resource, amount in request.items():
            new_resources[resource] = new_resources.get(resource, 0) - amount

        new_utility = self.calculate_utility(new_resources)
        utility_change = new_utility - current_utility

        # Trust modifier
        trust_level = self.get_trust_level(other_agent_id)
        trust_modifier = 1.0 + 0.5 * trust_level

        # Final evaluation
        final_utility = utility_change * trust_modifier

        # Accept if positive utility and sufficient trust
        accept = final_utility > 0 and trust_level > -0.5

        return accept, final_utility

    def propose_trade(self, other_agent: "Agent") -> Optional[Dict[str, Any]]:
        """Propose a trade to another agent."""
        # Find resources we have excess of and others need
        our_excess = {}
        their_excess = {}

        for resource in ["food", "energy", "artifacts", "influence"]:
            our_amount = self.resources.get(resource, 0)
            their_amount = other_agent.resources.get(resource, 0)

            if our_amount > 50:  # We have excess
                our_excess[resource] = min(our_amount - 50, 20)
            if their_amount > 50:  # They have excess
                their_excess[resource] = min(their_amount - 50, 20)

        # Simple trade: exchange excess resources
        if our_excess and their_excess:
            # Randomly select resources to trade
            our_resource = random.choice(list(our_excess.keys()))
            their_resource = random.choice(list(their_excess.keys()))

            return {
                "offer": {our_resource: our_excess[our_resource]},
                "request": {their_resource: their_excess[their_resource]},
                "round": 1,
            }

        return None

    def negotiate(self, other_agent: "Agent", max_rounds: int = 3) -> Optional[Trade]:
        """Negotiate a trade with another agent."""
        current_offer = self.propose_trade(other_agent)
        if not current_offer:
            return None

        for round_num in range(max_rounds):
            # Evaluate their counter-offer if this isn't the first round
            if round_num > 0:
                accept, utility = self.evaluate_trade_offer(
                    current_offer["offer"], current_offer["request"], other_agent.id
                )

                if accept and utility > 0:
                    # Create trade
                    trade = Trade(
                        initiator_id=self.id,
                        partner_id=other_agent.id,
                        resources_offered=current_offer["offer"],
                        resources_requested=current_offer["request"],
                        tick_created=0,  # Will be set by simulation
                    )
                    return trade

            # Modify offer for next round (simplified)
            if round_num < max_rounds - 1:
                # Reduce offer slightly to show flexibility
                for resource, amount in current_offer["offer"].items():
                    current_offer["offer"][resource] = amount * 0.9
                for resource, amount in current_offer["request"].items():
                    current_offer["request"][resource] = amount * 1.1

        return None

    def craft_myth(self, tick: int) -> Optional[Myth]:
        """Craft a new myth based on recent events and personality."""
        if random.random() > 0.1:  # 10% chance per tick
            return None

        # Retrieve recent episodic memories to ground the myth in lived
        # experience (retrieval-augmented deliberation).
        recent_events = self.memory.get_recent_events(limit=5)

        # Generate myth based on personality...
        myth_themes = []
        if self.personality.openness > 0.7:
            myth_themes.extend(["creation", "transformation", "exploration"])
        if self.personality.conscientiousness > 0.7:
            myth_themes.extend(["order", "duty", "sacrifice"])
        if self.personality.extraversion > 0.7:
            myth_themes.extend(["heroism", "leadership", "celebration"])

        if not myth_themes:
            myth_themes = ["mystery", "wisdom", "balance"]

        # ...and bias the theme toward what the agent has actually experienced.
        experience_themes = {
            "trade": "prosperity",
            "trade_success": "prosperity",
            "cultural_interaction": "wisdom",
            "alliance": "unity",
            "betrayal": "betrayal",
        }
        recalled_outcome = None
        for event in recent_events:
            theme_hint = experience_themes.get(event.event_type)
            if theme_hint:
                myth_themes.append(theme_hint)
            if event.outcome and recalled_outcome is None:
                recalled_outcome = event.outcome

        theme = random.choice(myth_themes)

        # Weave a recalled memory into the myth when one is available.
        if recalled_outcome:
            content = (
                f"Long ago, our people knew {recalled_outcome.replace('_', ' ')}. "
                f"From it, the {theme} came to shape who we are..."
            )
        else:
            content = f"Long ago, when the world was young, the {theme} came to our people..."

        myth = Myth(
            id=str(uuid.uuid4()),
            creator_id=self.id,
            title=f"The {theme.title()} of the {random.choice(['Ancient', 'Wise', 'Brave'])} Ones",
            content=content,
            theme=theme,
            tick_created=tick,
            popularity=1.0,
        )

        self.created_myths.append(myth.id)
        return myth

    def mint_slang(self, tick: int) -> Optional[Tuple[str, str]]:
        """Create new slang based on recent events and personality."""
        if random.random() > 0.05:  # 5% chance per tick
            return None

        # Retrieve recent episodic memories so slang can echo lived experience.
        recent_events = self.memory.get_recent_events(limit=3)

        # Generate slang based on personality
        if self.personality.openness > 0.6:
            base_words = ["innovate", "discover", "create", "transform"]
        elif self.personality.extraversion > 0.6:
            base_words = ["connect", "share", "celebrate", "unite"]
        else:
            base_words = ["think", "reflect", "understand", "know"]

        # Let a recent experience seed the vocabulary.
        experience_words = {
            "trade": "share",
            "trade_success": "share",
            "cultural_interaction": "connect",
            "alliance": "unite",
            "betrayal": "reflect",
        }
        for event in recent_events:
            seeded = experience_words.get(event.event_type)
            if seeded:
                base_words = [seeded] + base_words

        base_word = random.choice(base_words)

        # Apply phonetic mutations
        mutations = {
            "innovate": "novate",
            "discover": "scova",
            "create": "crate",
            "transform": "transfo",
            "connect": "necto",
            "share": "sharo",
            "celebrate": "celeb",
            "unite": "unito",
            "think": "thunk",
            "reflect": "flex",
            "understand": "stando",
            "know": "kno",
        }

        slang = mutations.get(base_word, base_word)
        meaning = f"to {base_word} in a new way"

        return (slang, meaning)

    def vote_on_norm(self, norm: Norm, tick: int) -> bool:
        """Vote on a proposed norm based on personality and ideology."""
        # Store vote
        self.voted_norms[norm.id] = True

        # Personality-based voting
        if norm.norm_type == "cooperation" and self.personality.agreeableness > 0.6:
            return True
        elif norm.norm_type == "innovation" and self.personality.openness > 0.6:
            return True
        elif norm.norm_type == "order" and self.personality.conscientiousness > 0.6:
            return True
        elif norm.norm_type == "leadership" and self.personality.extraversion > 0.6:
            return True

        # Default to random vote with slight bias toward approval
        return random.random() > 0.4

    def reflect(self, tick: int):
        """Periodic reflection to consolidate memories and update satisfaction.

        The agent adapts based on lived experience: it recalls recent episodic
        memories and lets their average emotional valence drive its
        satisfaction, so a string of good (or bad) outcomes shifts behaviour.
        """
        recent_events = self.memory.get_recent_events(limit=10)
        if recent_events:
            avg_valence = sum(e.emotional_valence for e in recent_events) / len(recent_events)
            # Experience dominates, with a little noise.
            satisfaction_change = 0.1 * avg_valence + random.uniform(-0.03, 0.03)
        else:
            satisfaction_change = random.uniform(-0.1, 0.1)

        self.satisfaction = max(0.0, min(1.0, self.satisfaction + satisfaction_change))

        # Consolidate memories
        self.memory.consolidate(tick)

    def _calculate_ideology_similarity(self, other: "Agent") -> float:
        """Calculate ideological similarity to another agent.

        Returns a value in [0, 1] where 1.0 means identical ideology vectors
        and values approach 0.0 as the vectors diverge.
        """
        a = np.asarray(self.ideology, dtype=float)
        b = np.asarray(other.ideology, dtype=float)
        n = min(len(a), len(b))
        if n == 0:
            return 0.0
        distance = float(np.linalg.norm(a[:n] - b[:n]))
        return max(0.0, 1.0 - distance)

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "generation": self.generation,
            "personality": {
                "openness": self.personality.openness,
                "conscientiousness": self.personality.conscientiousness,
                "extraversion": self.personality.extraversion,
                "agreeableness": self.personality.agreeableness,
                "neuroticism": self.personality.neuroticism,
            },
            "resources": self.resources,
            "influence": self.influence,
            "faction_id": self.faction_id,
            "state": self.state.value,
            "satisfaction": self.satisfaction,
            "trust_relationships": {
                k: {
                    "trust_level": v.trust_level,
                    "interaction_count": v.interaction_count,
                    "betrayal_count": v.betrayal_count,
                    "cooperation_count": v.cooperation_count,
                }
                for k, v in self.trust_relationships.items()
            },
        }
