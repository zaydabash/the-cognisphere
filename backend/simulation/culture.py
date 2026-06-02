"""
Cultural evolution systems including language drift, myth generation,
norm formation, and cultural diffusion mechanisms.
"""

import random
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from scipy.spatial.distance import jensenshannon


class MythTheme(Enum):
    """Themes for myth generation."""

    CREATION = "creation"
    HEROISM = "heroism"
    WISDOM = "wisdom"
    TRANSFORMATION = "transformation"
    SACRIFICE = "sacrifice"
    EXPLORATION = "exploration"
    ORDER = "order"
    CHAOS = "chaos"
    MYSTERY = "mystery"
    CELEBRATION = "celebration"


class NormType(Enum):
    """Types of social norms."""

    COOPERATION = "cooperation"
    INNOVATION = "innovation"
    ORDER = "order"
    LEADERSHIP = "leadership"
    SHARING = "sharing"
    COMPETITION = "competition"
    HONESTY = "honesty"
    LOYALTY = "loyalty"


@dataclass
class Myth:
    """A cultural myth or story."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    title: str = ""
    content: str = ""
    theme: str = ""
    characters: List[str] = field(default_factory=list)
    motifs: List[str] = field(default_factory=list)
    tick_created: int = 0
    popularity: float = 1.0
    influence: float = 1.0
    version: int = 1
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert myth to dictionary."""
        return {
            "id": self.id,
            "creator_id": self.creator_id,
            "title": self.title,
            "content": self.content,
            "theme": self.theme,
            "characters": self.characters,
            "motifs": self.motifs,
            "tick_created": self.tick_created,
            "popularity": self.popularity,
            "influence": self.influence,
            "version": self.version,
            "parent_id": self.parent_id,
        }


@dataclass
class Norm:
    """A social norm or rule."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    proposer_id: str = ""
    title: str = ""
    description: str = ""
    norm_type: str = ""
    tick_proposed: int = 0
    votes_for: int = 0
    votes_against: int = 0
    status: str = "proposed"  # proposed, active, rejected, superseded
    enforcement_strength: float = 0.5
    compliance_rate: float = 0.0
    violations: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert norm to dictionary."""
        return {
            "id": self.id,
            "proposer_id": self.proposer_id,
            "title": self.title,
            "description": self.description,
            "norm_type": self.norm_type,
            "tick_proposed": self.tick_proposed,
            "votes_for": self.votes_for,
            "votes_against": self.votes_against,
            "status": self.status,
            "enforcement_strength": self.enforcement_strength,
            "compliance_rate": self.compliance_rate,
            "violations": self.violations,
        }


@dataclass
class Slang:
    """A piece of slang or language innovation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    word: str = ""
    meaning: str = ""
    usage_context: str = ""
    tick_created: int = 0
    popularity: float = 1.0
    adoption_rate: float = 0.0
    parent_word: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert slang to dictionary."""
        return {
            "id": self.id,
            "creator_id": self.creator_id,
            "word": self.word,
            "meaning": self.meaning,
            "usage_context": self.usage_context,
            "tick_created": self.tick_created,
            "popularity": self.popularity,
            "adoption_rate": self.adoption_rate,
            "parent_word": self.parent_word,
        }


@dataclass
class Language:
    """Agent's language and slang vocabulary."""

    agent_id: str = ""
    vocabulary: Dict[str, Slang] = field(default_factory=dict)
    shared_vocabulary: Dict[str, float] = field(default_factory=dict)  # word -> adoption rate
    communication_style: str = "neutral"
    creativity_level: float = 0.5

    def add_slang(self, slang: Slang):
        """Add new slang to vocabulary."""
        self.vocabulary[slang.word] = slang

    def adopt_slang(self, word: str, meaning: str, adoption_rate: float = 0.1):
        """Adopt slang from another agent."""
        if word not in self.shared_vocabulary:
            self.shared_vocabulary[word] = 0.0

        # Increase adoption rate
        self.shared_vocabulary[word] = min(1.0, self.shared_vocabulary[word] + adoption_rate)

    def get_shared_words(self, threshold: float = 0.3) -> List[str]:
        """Get words shared with other agents above threshold."""
        return [word for word, rate in self.shared_vocabulary.items() if rate >= threshold]

    def calculate_divergence(self, other_language: "Language") -> float:
        """Calculate language divergence using JSD."""
        all_words = set(self.shared_vocabulary.keys()) | set(
            other_language.shared_vocabulary.keys()
        )

        if not all_words:
            return 0.0

        # Create probability distributions
        p1_values = []
        p2_values = []

        for word in all_words:
            p1_values.append(self.shared_vocabulary.get(word, 0.0))
            p2_values.append(other_language.shared_vocabulary.get(word, 0.0))

        # Normalize
        p1 = np.array(p1_values)
        p2 = np.array(p2_values)

        if p1.sum() > 0:
            p1 = p1 / p1.sum()
        else:
            p1 = np.ones_like(p1) / len(p1)

        if p2.sum() > 0:
            p2 = p2 / p2.sum()
        else:
            p2 = np.ones_like(p2) / len(p2)

        # Calculate Jensen-Shannon divergence
        try:
            return jensenshannon(p1, p2)
        except Exception:
            return 0.0


@dataclass
class Culture:
    """The cultural system managing myths, norms, language, and cultural evolution."""

    myths: Dict[str, Myth] = field(default_factory=dict)
    active_norms: Dict[str, Norm] = field(default_factory=dict)
    proposed_norms: Dict[str, Norm] = field(default_factory=dict)
    slang_registry: Dict[str, Slang] = field(default_factory=dict)
    cultural_events: List[Dict[str, Any]] = field(default_factory=list)

    # Language evolution parameters
    language_drift_frequency: int = 5  # Every 5 ticks
    slang_mutation_rate: float = 0.1
    myth_canonization_threshold: float = 0.7

    def add_myth(self, myth: Myth):
        """Add a new myth to the culture."""
        self.myths[myth.id] = myth

        # Record cultural event
        self.cultural_events.append(
            {
                "tick": myth.tick_created,
                "type": "myth_created",
                "agent_id": myth.creator_id,
                "content": myth.title,
                "theme": myth.theme,
            }
        )

    def canonize_myths(self, tick: int):
        """Canonize popular myths and reduce popularity of unpopular ones."""
        for myth in self.myths.values():
            # Update popularity based on recent cultural events
            recent_myth_events = [
                e
                for e in self.cultural_events[-50:]  # Last 50 events
                if e.get("type") == "myth_reference" and e.get("myth_id") == myth.id
            ]

            # Increase popularity for referenced myths
            myth.popularity = 0.9 * myth.popularity + 0.1 * len(recent_myth_events)

            # Canonize very popular myths
            if myth.popularity > self.myth_canonization_threshold:
                myth.influence *= 1.1
            elif myth.popularity < 0.2:
                myth.influence *= 0.95

    def propose_norm(self, norm: Norm, proposer_id: str):
        """Propose a new social norm."""
        norm.proposer_id = proposer_id
        self.proposed_norms[norm.id] = norm

        # Record cultural event
        self.cultural_events.append(
            {
                "tick": norm.tick_proposed,
                "type": "norm_proposed",
                "agent_id": proposer_id,
                "content": norm.title,
                "norm_type": norm.norm_type,
            }
        )

    def vote_on_norm(self, norm_id: str, agent_id: str, vote: bool):
        """Record a vote on a proposed norm."""
        if norm_id in self.proposed_norms:
            norm = self.proposed_norms[norm_id]
            if vote:
                norm.votes_for += 1
            else:
                norm.votes_against += 1

            # Check if norm should be activated
            total_votes = norm.votes_for + norm.votes_against
            if total_votes >= 3:  # Minimum quorum required
                approval_rate = norm.votes_for / total_votes
                if approval_rate >= 0.6:  # 60% approval threshold
                    norm.status = "active"
                    self.active_norms[norm_id] = norm
                    del self.proposed_norms[norm_id]
                else:
                    norm.status = "rejected"
                    del self.proposed_norms[norm_id]

    def enforce_norms(self, agents: List[Any], tick: int):
        """Enforce active norms and update compliance rates."""
        for norm in self.active_norms.values():
            violations = 0
            compliance_count = 0

            for agent in agents:
                # Simple compliance check based on personality
                compliance_prob = 0.5

                if norm.norm_type == "cooperation":
                    compliance_prob += 0.3 * agent.personality.agreeableness
                elif norm.norm_type == "innovation":
                    compliance_prob += 0.3 * agent.personality.openness
                elif norm.norm_type == "order":
                    compliance_prob += 0.3 * agent.personality.conscientiousness
                elif norm.norm_type == "leadership":
                    compliance_prob += 0.3 * agent.personality.extraversion

                # Check compliance
                if random.random() < compliance_prob:
                    compliance_count += 1
                else:
                    violations += 1
                    # Apply penalty for violation
                    agent.influence *= 0.99

            # Update norm statistics
            total_agents = len(agents)
            if total_agents > 0:
                norm.compliance_rate = compliance_count / total_agents
                norm.violations = violations

    def evolve_language(self, agents: List[Any], tick: int):
        """Evolve language through slang creation and diffusion."""
        if tick % self.language_drift_frequency != 0:
            return

        # Collect new slang from agents
        new_slang = []
        for agent in agents:
            slang_data = agent.mint_slang(tick)
            if slang_data:
                word, meaning = slang_data
                slang = Slang(
                    creator_id=agent.id,
                    word=word,
                    meaning=meaning,
                    usage_context="general",
                    tick_created=tick,
                )
                new_slang.append(slang)
                self.slang_registry[slang.id] = slang
                agent.language.add_slang(slang)

        # Diffuse slang among agents
        if new_slang:
            for slang in new_slang:
                # Find agents who might adopt this slang
                potential_adopters = [
                    agent
                    for agent in agents
                    if agent.id != slang.creator_id and random.random() < self.slang_mutation_rate
                ]

                for agent in potential_adopters:
                    adoption_rate = random.uniform(0.05, 0.2)
                    agent.language.adopt_slang(slang.word, slang.meaning, adoption_rate)
                    slang.adoption_rate += adoption_rate / len(agents)

        # Update slang popularity
        for slang in self.slang_registry.values():
            slang.popularity = 0.9 * slang.popularity + 0.1 * slang.adoption_rate

    def generate_myth_templates(self) -> List[Dict[str, Any]]:
        """Generate myth templates for agents to use."""
        templates = [
            {
                "theme": "creation",
                "title_template": "The Birth of {entity}",
                "content_template": "In the beginning, there was only {void}. Then came {entity}, who brought {concept} to the world...",
                "entities": ["the First One", "the Creator", "the Ancient Spirit"],
                "concepts": ["light", "order", "wisdom", "life"],
            },
            {
                "theme": "heroism",
                "title_template": "The {hero}'s {journey}",
                "content_template": "Long ago, {hero} embarked on a {journey} to {goal}. Along the way, they faced {challenge}...",
                "heroes": ["Brave One", "Wise One", "Swift One"],
                "journeys": ["Quest", "Journey", "Adventure"],
                "goals": ["save the people", "find wisdom", "restore balance"],
                "challenges": ["great trials", "terrible monsters", "impossible choices"],
            },
            {
                "theme": "transformation",
                "title_template": "How {entity} Became {new_form}",
                "content_template": "Once, {entity} was {old_form}. But through {process}, they transformed into {new_form}...",
                "entities": ["the Wanderer", "the Seeker", "the Lost One"],
                "old_forms": ["ordinary", "powerless", "lost"],
                "processes": ["great sacrifice", "deep wisdom", "true understanding"],
                "new_forms": ["wise", "powerful", "enlightened"],
            },
        ]
        return templates

    @staticmethod
    def _singularize(key: str) -> str:
        """Best-effort singular form of a plural template key."""
        if key.endswith("ies"):
            return key[:-3] + "y"
        if key.endswith("es") and key[:-2].endswith(("o", "s")):
            return key[:-2]
        if key.endswith("s"):
            return key[:-1]
        return key

    def create_myth_from_template(self, template: Dict[str, Any], agent_id: str, tick: int) -> Myth:
        """Create a myth from a template."""
        theme = template["theme"]

        # Build substitution values from list-valued template fields, exposing
        # both the plural key and a singular alias so templates using either
        # form (e.g. {entities} or {entity}) resolve correctly.
        substitutions: Dict[str, str] = {}
        for key, value in template.items():
            if isinstance(value, list) and value:
                choice = random.choice(value)
                substitutions[key] = choice
                substitutions.setdefault(self._singularize(key), choice)

        # Tolerate placeholders with no matching list (e.g. {void}).
        class _SafeDict(dict):
            def __missing__(self, missing_key: str) -> str:
                return "the unknown"

        safe = _SafeDict(substitutions)
        title = template["title_template"].format_map(safe)
        content = template["content_template"].format_map(safe)

        myth = Myth(
            creator_id=agent_id,
            title=title,
            content=content,
            theme=theme,
            tick_created=tick,
            popularity=random.uniform(0.3, 0.8),
        )

        return myth

    def get_cultural_summary(self) -> Dict[str, Any]:
        """Get summary of cultural state."""
        return {
            "myths_count": len(self.myths),
            "active_norms_count": len(self.active_norms),
            "proposed_norms_count": len(self.proposed_norms),
            "slang_count": len(self.slang_registry),
            "recent_events": len(self.cultural_events[-20:]),  # Last 20 events
            "top_myths": [
                {"title": myth.title, "theme": myth.theme, "popularity": myth.popularity}
                for myth in sorted(self.myths.values(), key=lambda m: m.popularity, reverse=True)[
                    :5
                ]
            ],
            "active_norms": [
                {
                    "title": norm.title,
                    "type": norm.norm_type,
                    "compliance_rate": norm.compliance_rate,
                }
                for norm in self.active_norms.values()
            ],
            "popular_slang": [
                {"word": slang.word, "meaning": slang.meaning, "popularity": slang.popularity}
                for slang in sorted(
                    self.slang_registry.values(), key=lambda s: s.popularity, reverse=True
                )[:10]
            ],
        }
