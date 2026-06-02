"""
Economy and trade systems for the simulation.

Handles resource management, bilateral negotiation, market dynamics,
and economic events that affect agent behavior and civilization development.
"""

import random
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class ResourceType(Enum):
    """Types of resources in the economy."""

    FOOD = "food"
    ENERGY = "energy"
    ARTIFACTS = "artifacts"
    INFLUENCE = "influence"


class TradeStatus(Enum):
    """Status of a trade."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Resource:
    """A resource in the economy."""

    name: str
    base_value: float = 1.0
    scarcity_modifier: float = 1.0
    demand_modifier: float = 1.0
    production_rate: float = 1.0
    decay_rate: float = 0.0

    @property
    def current_value(self) -> float:
        """Calculate current market value of resource."""
        return self.base_value * self.scarcity_modifier * self.demand_modifier


@dataclass
class Trade:
    """A trade between two agents."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    initiator_id: str = ""
    partner_id: str = ""
    resources_offered: Dict[str, float] = field(default_factory=dict)
    resources_requested: Dict[str, float] = field(default_factory=dict)
    status: TradeStatus = TradeStatus.PENDING
    rounds_negotiated: int = 0
    max_rounds: int = 3
    tick_created: int = 0
    tick_completed: Optional[int] = None
    utility_initiator: float = 0.0
    utility_partner: float = 0.0

    def calculate_utility(
        self, agent_resources: Dict[str, float], resource_values: Dict[str, float]
    ) -> float:
        """Calculate utility of this trade for an agent."""
        # Calculate net resource change
        net_change: Dict[str, float] = {}
        for resource, amount in self.resources_offered.items():
            net_change[resource] = net_change.get(resource, 0) + amount
        for resource, amount in self.resources_requested.items():
            net_change[resource] = net_change.get(resource, 0) - amount

        # Calculate utility using Cobb-Douglas function
        utility = 1.0
        for resource, change in net_change.items():
            if change != 0:
                new_amount = agent_resources.get(resource, 0) + change
                if new_amount > 0:
                    weight = resource_values.get(resource, 1.0)
                    utility *= new_amount ** (weight * 0.3)

        return utility


@dataclass
class Market:
    """A market for resource exchange."""

    name: str = ""
    resources: Dict[str, Resource] = field(default_factory=dict)
    price_history: Dict[str, List[Tuple[int, float]]] = field(default_factory=dict)
    volume_history: Dict[str, List[Tuple[int, float]]] = field(default_factory=dict)
    active_trades: List[Trade] = field(default_factory=list)
    completed_trades: List[Trade] = field(default_factory=list)

    def __post_init__(self):
        """Initialize market with default resources."""
        if not self.resources:
            self.resources = {
                "food": Resource("food", base_value=1.0, production_rate=2.0),
                "energy": Resource("energy", base_value=1.2, production_rate=1.5),
                "artifacts": Resource("artifacts", base_value=2.0, production_rate=0.5),
                "influence": Resource("influence", base_value=3.0, production_rate=0.3),
            }

    def update_prices(self, tick: int, supply_demand: Dict[str, Tuple[float, float]]):
        """Update resource prices based on supply and demand."""
        for resource_name, (supply, demand) in supply_demand.items():
            if resource_name in self.resources:
                resource = self.resources[resource_name]

                # Calculate scarcity modifier: >1.0 when demand outstrips
                # supply, <1.0 when supply is plentiful, ~1.0 at equilibrium.
                if supply > 0:
                    resource.scarcity_modifier = min(demand / supply, 10.0)
                else:
                    resource.scarcity_modifier = 10.0  # Extreme scarcity

                # Record price history
                if resource_name not in self.price_history:
                    self.price_history[resource_name] = []
                self.price_history[resource_name].append((tick, resource.current_value))

                # Keep only recent history
                if len(self.price_history[resource_name]) > 100:
                    self.price_history[resource_name] = self.price_history[resource_name][-100:]

    def get_current_prices(self) -> Dict[str, float]:
        """Get current market prices for all resources."""
        return {name: resource.current_value for name, resource in self.resources.items()}

    def process_trade(self, trade: Trade) -> bool:
        """Process a trade and update market state."""
        if trade.status == TradeStatus.ACCEPTED:
            # Record trade volume
            total_volume = sum(trade.resources_offered.values()) + sum(
                trade.resources_requested.values()
            )

            for resource in set(trade.resources_offered.keys()) | set(
                trade.resources_requested.keys()
            ):
                if resource not in self.volume_history:
                    self.volume_history[resource] = []
                self.volume_history[resource].append((trade.tick_completed or 0, total_volume))

                # Keep only recent history
                if len(self.volume_history[resource]) > 100:
                    self.volume_history[resource] = self.volume_history[resource][-100:]

            # Move to completed trades
            if trade in self.active_trades:
                self.active_trades.remove(trade)
            self.completed_trades.append(trade)

            return True
        return False

    def get_market_summary(self) -> Dict[str, Any]:
        """Get summary of market state."""
        return {
            "name": self.name,
            "current_prices": self.get_current_prices(),
            "active_trades": len(self.active_trades),
            "completed_trades": len(self.completed_trades),
            "resources": {
                name: {
                    "base_value": res.base_value,
                    "current_value": res.current_value,
                    "scarcity_modifier": res.scarcity_modifier,
                    "production_rate": res.production_rate,
                }
                for name, res in self.resources.items()
            },
        }


@dataclass
class Economy:
    """The economic system managing resources, trade, and market dynamics."""

    market: Market = field(default_factory=Market)
    resource_production: Dict[str, float] = field(default_factory=dict)
    global_events: List[Dict[str, Any]] = field(default_factory=list)
    trade_history: List[Trade] = field(default_factory=list)
    gini_coefficient: float = 0.0

    def __post_init__(self):
        """Initialize economy."""
        if not self.resource_production:
            self.resource_production = {
                "food": 1000.0,
                "energy": 800.0,
                "artifacts": 200.0,
                "influence": 100.0,
            }

    def produce_resources(self, tick: int) -> Dict[str, float]:
        """Produce resources for the current tick."""
        production = {}
        for resource_name, base_production in self.resource_production.items():
            if resource_name in self.market.resources:
                resource = self.market.resources[resource_name]
                production[resource_name] = base_production * resource.production_rate
            else:
                production[resource_name] = base_production

        return production

    def distribute_resources(
        self, agents: List[Any], production: Dict[str, float]
    ) -> Dict[str, float]:
        """Distribute produced resources among agents."""
        if not agents:
            return {}

        # Simple distribution based on agent influence and random factors
        distribution = {resource: 0.0 for resource in production.keys()}

        for resource_name, total_production in production.items():
            # Weight distribution by influence
            total_influence = sum(agent.influence for agent in agents)
            if total_influence > 0:
                for agent in agents:
                    share = (agent.influence / total_influence) * total_production
                    # Add some randomness
                    share *= random.uniform(0.8, 1.2)
                    agent.resources[resource_name] = agent.resources.get(resource_name, 0) + share
                    distribution[resource_name] += share

        return distribution

    def calculate_supply_demand(self, agents: List[Any]) -> Dict[str, Tuple[float, float]]:
        """Calculate supply and demand for each resource."""
        supply_demand = {}

        for resource_name in self.market.resources.keys():
            # Calculate supply (total resources held)
            supply = sum(agent.resources.get(resource_name, 0) for agent in agents)

            # Calculate demand (based on agent needs and preferences)
            demand = 0.0
            for agent in agents:
                current_amount = agent.resources.get(resource_name, 0)
                # Agents want to maintain certain resource levels
                desired_amount = 50.0  # Base desired amount

                # Personality affects desired amounts
                if resource_name == "food":
                    desired_amount *= 1.0 + agent.personality.conscientiousness
                elif resource_name == "energy":
                    desired_amount *= 1.0 + agent.personality.extraversion
                elif resource_name == "artifacts":
                    desired_amount *= 1.0 + agent.personality.openness
                elif resource_name == "influence":
                    desired_amount *= 1.0 + agent.personality.extraversion

                if current_amount < desired_amount:
                    demand += desired_amount - current_amount

            supply_demand[resource_name] = (supply, demand)

        return supply_demand

    def update_market(self, tick: int, agents: List[Any]):
        """Update market prices and process trades."""
        # Calculate supply and demand
        supply_demand = self.calculate_supply_demand(agents)

        # Update market prices
        self.market.update_prices(tick, supply_demand)

        # Process active trades
        completed_trades = []
        for trade in self.market.active_trades:
            if self.market.process_trade(trade):
                completed_trades.append(trade)

        # Calculate Gini coefficient for resource inequality
        self.calculate_gini_coefficient(agents)

    def calculate_gini_coefficient(self, agents: List[Any]):
        """Calculate Gini coefficient for resource inequality."""
        if not agents:
            self.gini_coefficient = 0.0
            return

        # Calculate total wealth for each agent
        agent_wealth = []
        for agent in agents:
            wealth = sum(agent.resources.values())
            agent_wealth.append(wealth)

        agent_wealth.sort()
        n = len(agent_wealth)

        if n == 0 or sum(agent_wealth) == 0:
            self.gini_coefficient = 0.0
            return

        # Calculate Gini coefficient from sorted wealth values
        # G = (n + 1 - 2 * (sum_i (n + 1 - i) * x_i) / sum(x)) / n
        total_wealth = sum(agent_wealth)
        weighted_sum = sum((n + 1 - i) * w for i, w in enumerate(agent_wealth, 1))
        self.gini_coefficient = (n + 1 - 2 * weighted_sum / total_wealth) / n

    def add_economic_event(
        self, event_type: str, description: str, resource_effects: Dict[str, float], duration: int
    ):
        """Add an economic event that affects resource availability."""
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "description": description,
            "resource_effects": resource_effects,
            "duration": duration,
            "tick_start": 0,  # Will be set when event is activated
            "active": False,
        }
        self.global_events.append(event)

    def apply_events(self, tick: int):
        """Apply active economic events to resource production."""
        for event in self.global_events:
            if event["active"]:
                # Check if event should end
                if tick - event["tick_start"] >= event["duration"]:
                    event["active"] = False
                else:
                    # Apply resource effects
                    for resource, effect in event["resource_effects"].items():
                        if resource in self.resource_production:
                            self.resource_production[resource] *= effect

    def trigger_event(self, event_type: str, tick: int):
        """Trigger a random economic event."""
        events: Dict[str, Dict[str, Any]] = {
            "scarcity": {
                "description": "Resource scarcity affects production",
                "effects": {"food": 0.7, "energy": 0.8},
                "duration": 10,
            },
            "abundance": {
                "description": "Resource abundance boosts production",
                "effects": {"artifacts": 1.5, "influence": 1.3},
                "duration": 8,
            },
            "disaster": {
                "description": "Natural disaster disrupts economy",
                "effects": {"food": 0.5, "energy": 0.6, "artifacts": 0.8},
                "duration": 15,
            },
            "innovation": {
                "description": "Technological innovation improves production",
                "effects": {"energy": 1.4, "artifacts": 1.6},
                "duration": 20,
            },
        }

        if event_type in events:
            event_data = events[event_type]
            self.add_economic_event(
                event_type=event_type,
                description=event_data["description"],
                resource_effects=event_data["effects"],
                duration=event_data["duration"],
            )
            # Activate the newly added event at the current tick
            new_event = self.global_events[-1]
            new_event["active"] = True
            new_event["tick_start"] = tick

    def get_economy_summary(self) -> Dict[str, Any]:
        """Get summary of economy state."""
        return {
            "market_summary": self.market.get_market_summary(),
            "gini_coefficient": self.gini_coefficient,
            "active_events": len([e for e in self.global_events if e["active"]]),
            "total_trades": len(self.trade_history),
            "resource_production": self.resource_production.copy(),
        }
