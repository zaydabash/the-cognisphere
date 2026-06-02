"""
Event system for managing simulation events, environmental stimuli,
and emergent dynamics that affect agent behavior and civilization development.
"""

import random
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class EventType(Enum):
    """Types of simulation events."""

    # Environmental events
    SCARCITY = "scarcity"
    ABUNDANCE = "abundance"
    DISASTER = "disaster"
    INNOVATION = "innovation"
    MIGRATION = "migration"

    # Social events
    FESTIVAL = "festival"
    CONFLICT = "conflict"
    ALLIANCE_FORMED = "alliance_formed"
    BETRAYAL = "betrayal"
    LEADERSHIP_CHANGE = "leadership_change"

    # Cultural events
    MYTH_CREATED = "myth_created"
    NORM_PROPOSED = "norm_proposed"
    LANGUAGE_SHIFT = "language_shift"
    CULTURAL_DIFFUSION = "cultural_diffusion"

    # Economic events
    TRADE_BOOM = "trade_boom"
    MARKET_CRASH = "market_crash"
    RESOURCE_DISCOVERY = "resource_discovery"

    # External stimuli
    HEAT_WAVE = "heat_wave"
    COLD_SNAP = "cold_snap"
    MEME_ERUPTION = "meme_eruption"
    NEWS_EVENT = "news_event"


class EventPriority(Enum):
    """Event priority levels."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """A simulation event that affects agents and the world."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.SCARCITY
    title: str = ""
    description: str = ""
    tick_created: int = 0
    tick_duration: int = 1
    priority: EventPriority = EventPriority.MEDIUM

    # Event effects
    resource_effects: Dict[str, float] = field(default_factory=dict)
    social_effects: Dict[str, Any] = field(default_factory=dict)
    cultural_effects: Dict[str, Any] = field(default_factory=dict)

    # Event targets
    affected_agents: List[str] = field(default_factory=list)
    affected_factions: List[str] = field(default_factory=list)
    global_effect: bool = True

    # Event state
    active: bool = False
    completed: bool = False
    intensity: float = 1.0  # 0.0 to 2.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "title": self.title,
            "description": self.description,
            "tick_created": self.tick_created,
            "tick_duration": self.tick_duration,
            "priority": self.priority.value,
            "resource_effects": self.resource_effects,
            "social_effects": self.social_effects,
            "cultural_effects": self.cultural_effects,
            "affected_agents": self.affected_agents,
            "affected_factions": self.affected_factions,
            "global_effect": self.global_effect,
            "active": self.active,
            "completed": self.completed,
            "intensity": self.intensity,
        }


@dataclass
class EventSystem:
    """Manages simulation events and their effects."""

    active_events: List[Event] = field(default_factory=list)
    event_history: List[Event] = field(default_factory=list)
    event_handlers: Dict[EventType, Callable] = field(default_factory=dict)

    # Event generation parameters
    base_event_probability: float = 0.05  # 5% chance per tick
    event_cooldown: Dict[EventType, int] = field(default_factory=dict)
    last_event_ticks: Dict[EventType, int] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize event system."""
        # Set up default event handlers
        self.event_handlers = {
            EventType.SCARCITY: self._handle_scarcity_event,
            EventType.ABUNDANCE: self._handle_abundance_event,
            EventType.DISASTER: self._handle_disaster_event,
            EventType.INNOVATION: self._handle_innovation_event,
            EventType.FESTIVAL: self._handle_festival_event,
            EventType.CONFLICT: self._handle_conflict_event,
            EventType.ALLIANCE_FORMED: self._handle_alliance_event,
            EventType.BETRAYAL: self._handle_betrayal_event,
            EventType.MYTH_CREATED: self._handle_myth_event,
            EventType.NORM_PROPOSED: self._handle_norm_event,
            EventType.TRADE_BOOM: self._handle_trade_boom_event,
            EventType.MARKET_CRASH: self._handle_market_crash_event,
        }

        # Initialize cooldowns
        self.event_cooldown = {
            EventType.SCARCITY: 20,
            EventType.ABUNDANCE: 25,
            EventType.DISASTER: 50,
            EventType.INNOVATION: 30,
            EventType.FESTIVAL: 15,
            EventType.CONFLICT: 10,
            EventType.ALLIANCE_FORMED: 5,
            EventType.BETRAYAL: 5,
            EventType.MYTH_CREATED: 2,
            EventType.NORM_PROPOSED: 3,
            EventType.TRADE_BOOM: 20,
            EventType.MARKET_CRASH: 40,
        }

        # Initialize last event tracking
        for event_type in EventType:
            self.last_event_ticks[event_type] = -1000  # Long ago

    def generate_random_event(
        self, tick: int, agents: List[Any], world_state: Dict[str, Any]
    ) -> Optional[Event]:
        """Generate a random event based on current world state."""
        # Check if we should generate an event
        if random.random() > self.base_event_probability:
            return None

        # Filter events by cooldown
        available_events = []
        for et, cooldown in self.event_cooldown.items():
            if tick - self.last_event_ticks[et] >= cooldown:
                available_events.append(et)

        if not available_events:
            return None

        # Select event type based on world state
        event_type = self._select_event_type(available_events, world_state)
        if not event_type:
            return None

        # Create event
        event = self._create_event(event_type, tick, agents, world_state)
        if event:
            self.last_event_ticks[event_type] = tick

        return event

    def _select_event_type(
        self, available_events: List[EventType], world_state: Dict[str, Any]
    ) -> Optional[EventType]:
        """Select event type based on world state probabilities."""
        # Base probabilities for each event type
        probabilities = {
            EventType.SCARCITY: 0.15,
            EventType.ABUNDANCE: 0.10,
            EventType.DISASTER: 0.05,
            EventType.INNOVATION: 0.10,
            EventType.FESTIVAL: 0.15,
            EventType.CONFLICT: 0.10,
            EventType.ALLIANCE_FORMED: 0.10,
            EventType.BETRAYAL: 0.05,
            EventType.MYTH_CREATED: 0.10,
            EventType.NORM_PROPOSED: 0.10,
        }

        # Adjust probabilities based on world state
        gini_coefficient = world_state.get("gini_coefficient", 0.5)
        if gini_coefficient > 0.7:  # High inequality
            probabilities[EventType.CONFLICT] *= 2.0
            probabilities[EventType.BETRAYAL] *= 1.5
        elif gini_coefficient < 0.3:  # Low inequality
            probabilities[EventType.FESTIVAL] *= 1.5
            probabilities[EventType.ALLIANCE_FORMED] *= 1.2

        # Filter by available events
        available_probs = {et: probabilities.get(et, 0.1) for et in available_events}

        # Normalize probabilities
        total_prob = sum(available_probs.values())
        if total_prob == 0:
            return random.choice(available_events)

        # Weighted random selection
        rand_val = random.random() * total_prob
        cum_prob = 0.0

        for event_type, prob in available_probs.items():
            cum_prob += prob
            if rand_val <= cum_prob:
                return event_type

        return random.choice(available_events)

    def _create_event(
        self, event_type: EventType, tick: int, agents: List[Any], world_state: Dict[str, Any]
    ) -> Optional[Event]:
        """Create a specific event based on type."""
        event_templates: Dict[EventType, Dict[str, Any]] = {
            EventType.SCARCITY: {
                "title": "Resource Scarcity",
                "description": "A shortage of essential resources affects the civilization",
                "duration": random.randint(10, 20),
                "resource_effects": {"food": 0.7, "energy": 0.8},
                "intensity": random.uniform(0.5, 1.5),
            },
            EventType.ABUNDANCE: {
                "title": "Resource Abundance",
                "description": "An abundance of resources brings prosperity",
                "duration": random.randint(8, 15),
                "resource_effects": {"artifacts": 1.5, "influence": 1.3},
                "intensity": random.uniform(0.8, 1.2),
            },
            EventType.DISASTER: {
                "title": "Natural Disaster",
                "description": "A catastrophic event disrupts the civilization",
                "duration": random.randint(15, 30),
                "resource_effects": {"food": 0.5, "energy": 0.6, "artifacts": 0.8},
                "intensity": random.uniform(1.0, 2.0),
            },
            EventType.INNOVATION: {
                "title": "Technological Innovation",
                "description": "A breakthrough in technology improves production",
                "duration": random.randint(20, 40),
                "resource_effects": {"energy": 1.4, "artifacts": 1.6},
                "intensity": random.uniform(0.6, 1.4),
            },
            EventType.FESTIVAL: {
                "title": "Cultural Festival",
                "description": "A celebration brings the community together",
                "duration": random.randint(5, 10),
                "social_effects": {"cooperation_bonus": 0.2, "trust_increase": 0.1},
                "intensity": random.uniform(0.7, 1.3),
            },
            EventType.CONFLICT: {
                "title": "Social Conflict",
                "description": "Tensions rise between different groups",
                "duration": random.randint(8, 15),
                "social_effects": {"trust_decrease": 0.2, "cooperation_penalty": 0.15},
                "intensity": random.uniform(0.8, 1.5),
            },
            EventType.ALLIANCE_FORMED: {
                "title": "New Alliance",
                "description": "Groups form new cooperative relationships",
                "duration": random.randint(15, 30),
                "social_effects": {"trust_increase": 0.3, "cooperation_bonus": 0.25},
                "intensity": random.uniform(0.6, 1.2),
            },
            EventType.BETRAYAL: {
                "title": "Betrayal",
                "description": "A trusted relationship is broken",
                "duration": random.randint(10, 20),
                "social_effects": {"trust_decrease": 0.4, "suspicion_increase": 0.3},
                "intensity": random.uniform(1.0, 1.8),
            },
            EventType.MYTH_CREATED: {
                "title": "New Myth Emerges",
                "description": "A powerful new story spreads through the civilization",
                "duration": random.randint(20, 40),
                "cultural_effects": {"myth_influence": 0.3, "cultural_cohesion": 0.2},
                "intensity": random.uniform(0.5, 1.5),
            },
            EventType.NORM_PROPOSED: {
                "title": "New Social Norm",
                "description": "A new rule or expectation is proposed",
                "duration": random.randint(15, 25),
                "cultural_effects": {"norm_debate": 0.4, "social_change": 0.2},
                "intensity": random.uniform(0.4, 1.0),
            },
        }

        template = event_templates.get(event_type)
        if not template:
            return None

        event = Event(
            event_type=event_type,
            title=template["title"],
            description=template["description"],
            tick_created=tick,
            tick_duration=template["duration"],
            resource_effects=template.get("resource_effects", {}),
            social_effects=template.get("social_effects", {}),
            cultural_effects=template.get("cultural_effects", {}),
            intensity=template["intensity"],
            priority=EventPriority.HIGH
            if event_type in [EventType.DISASTER, EventType.BETRAYAL]
            else EventPriority.MEDIUM,
        )

        return event

    def process_events(
        self, tick: int, agents: List[Any], economy: Any, culture: Any
    ) -> List[Event]:
        """Process all active events and return completed events."""
        completed_events = []

        for event in self.active_events[:]:  # Copy to avoid modification during iteration
            # Apply event effects
            self._apply_event_effects(event, agents, economy, culture)

            # Check if event should complete
            if tick - event.tick_created >= event.tick_duration:
                event.completed = True
                event.active = False
                completed_events.append(event)
                self.active_events.remove(event)
                self.event_history.append(event)

        return completed_events

    def _apply_event_effects(self, event: Event, agents: List[Any], economy: Any, culture: Any):
        """Apply the effects of an active event."""
        self._apply_resource_effects(event, economy)
        self._apply_social_effects(event, agents)
        self._apply_cultural_effects(event, culture)

    def _apply_resource_effects(self, event: Event, economy: Any):
        """Apply an event's resource effects to the economy."""
        for resource, multiplier in event.resource_effects.items():
            if hasattr(economy, "resource_production") and resource in economy.resource_production:
                economy.resource_production[resource] *= multiplier**event.intensity

    def _apply_social_effects(self, event: Event, agents: List[Any]):
        """Apply an event's social effects to agents."""
        for effect, value in event.social_effects.items():
            delta = value * event.intensity
            for agent in agents:
                if effect == "trust_increase":
                    for other_id in agent.trust_relationships:
                        agent.update_trust(other_id, delta, 0)
                elif effect == "trust_decrease":
                    for other_id in agent.trust_relationships:
                        agent.update_trust(other_id, -delta, 0)
                elif effect == "cooperation_bonus":
                    agent.satisfaction += delta
                elif effect == "cooperation_penalty":
                    agent.satisfaction -= delta

    def _apply_cultural_effects(self, event: Event, culture: Any):
        """Apply an event's cultural effects."""
        for effect, value in event.cultural_effects.items():
            if effect == "myth_influence" and hasattr(culture, "myths"):
                for myth in culture.myths.values():
                    myth.influence *= 1.0 + value * event.intensity
            elif effect == "cultural_cohesion" and hasattr(culture, "slang_registry"):
                for slang in culture.slang_registry.values():
                    slang.adoption_rate += value * event.intensity

    def add_external_stimuli(self, stimuli_data: List[Dict[str, Any]], tick: int) -> List[Event]:
        """Add external stimuli as events."""
        created_events = []

        for stimulus in stimuli_data:
            event_type_str = stimulus.get("type", "")

            # Map external stimulus types to event types
            type_mapping = {
                "heat_wave": EventType.HEAT_WAVE,
                "cold_snap": EventType.COLD_SNAP,
                "meme_eruption": EventType.MEME_ERUPTION,
                "news_event": EventType.NEWS_EVENT,
                "market_crash": EventType.MARKET_CRASH,
                "trade_boom": EventType.TRADE_BOOM,
            }

            event_type = type_mapping.get(event_type_str)
            if not event_type:
                continue

            event = Event(
                event_type=event_type,
                title=stimulus.get("title", f"External {event_type_str}"),
                description=stimulus.get("description", ""),
                tick_created=tick,
                tick_duration=stimulus.get("duration", 10),
                intensity=stimulus.get("intensity", 1.0),
                priority=EventPriority.MEDIUM,
            )

            # Add resource effects if specified
            if "resource_effects" in stimulus:
                event.resource_effects = stimulus["resource_effects"]

            # Add social effects if specified
            if "social_effects" in stimulus:
                event.social_effects = stimulus["social_effects"]

            created_events.append(event)
            self.active_events.append(event)

        return created_events

    def get_event_summary(self) -> Dict[str, Any]:
        """Get summary of event system state."""
        return {
            "active_events": len(self.active_events),
            "total_events": len(self.event_history),
            "recent_events": [
                {
                    "type": event.event_type.value,
                    "title": event.title,
                    "tick": event.tick_created,
                    "completed": event.completed,
                }
                for event in self.event_history[-10:]  # Last 10 events
            ],
            "active_event_types": [event.event_type.value for event in self.active_events],
        }

    # Event handler methods
    def _handle_scarcity_event(self, event: Event, agents: List[Any], **kwargs):
        """Handle scarcity event effects."""
        pass  # Effects applied in _apply_event_effects

    def _handle_abundance_event(self, event: Event, agents: List[Any], **kwargs):
        """Handle abundance event effects."""
        pass

    def _handle_disaster_event(self, event: Event, agents: List[Any], **kwargs):
        """Handle disaster event effects."""
        pass

    def _handle_innovation_event(self, event: Event, agents: List[Any], **kwargs):
        """Handle innovation event effects."""
        pass

    def _handle_festival_event(self, event: Event, agents: List[Any], **kwargs):
        """Handle festival event effects."""
        pass

    def _handle_conflict_event(self, event: Event, agents: List[Any], **kwargs):
        """Handle conflict event effects."""
        pass

    def _handle_alliance_event(self, event: Event, agents: List[Any], **kwargs):
        """Handle alliance event effects."""
        pass

    def _handle_betrayal_event(self, event: Event, agents: List[Any], **kwargs):
        """Handle betrayal event effects."""
        pass

    def _handle_myth_event(self, event: Event, agents: List[Any], **kwargs):
        """Handle myth event effects."""
        pass

    def _handle_norm_event(self, event: Event, agents: List[Any], **kwargs):
        """Handle norm event effects."""
        pass

    def _handle_trade_boom_event(self, event: Event, agents: List[Any], **kwargs):
        """Handle trade boom event effects."""
        pass

    def _handle_market_crash_event(self, event: Event, agents: List[Any], **kwargs):
        """Handle market crash event effects."""
        pass
