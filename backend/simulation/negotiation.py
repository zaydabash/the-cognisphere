"""
Negotiation system for The Cognisphere.

Handles bilateral negotiations, alternating offers, and market fallback
mechanisms for resource trading and social interactions.
"""

import random
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class NegotiationStatus(Enum):
    """Status of a negotiation."""

    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class OfferType(Enum):
    """Types of offers in negotiations."""

    INITIAL = "initial"
    COUNTER = "counter"
    FINAL = "final"


@dataclass
class NegotiationOffer:
    """Represents an offer in a negotiation."""

    offer_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    offerer_id: str = ""
    receiver_id: str = ""
    offer_type: OfferType = OfferType.INITIAL
    offered_resources: Dict[str, float] = field(default_factory=dict)
    requested_resources: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    round_number: int = 0
    utility_offerer: float = 0.0
    utility_receiver: float = 0.0
    fairness_score: float = 0.0

    def calculate_fairness(self) -> float:
        """Calculate fairness score of this offer."""
        offer_value = sum(self.offered_resources.values())
        request_value = sum(self.requested_resources.values())

        if request_value == 0:
            return 1.0 if offer_value == 0 else 0.0

        ratio = offer_value / request_value
        # Fairness decreases as ratio deviates from 1.0
        fairness = 1.0 - abs(ratio - 1.0)
        return max(0.0, min(1.0, fairness))


@dataclass
class Negotiation:
    """Represents a negotiation between two agents."""

    negotiation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    initiator_id: str = ""
    partner_id: str = ""
    negotiation_type: str = "trade"  # trade, alliance, institution
    status: NegotiationStatus = NegotiationStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_offer_at: datetime = field(default_factory=datetime.now)
    max_rounds: int = 5
    timeout_minutes: int = 10
    current_round: int = 0
    offers: List[NegotiationOffer] = field(default_factory=list)
    final_agreement: Optional[NegotiationOffer] = None

    def add_offer(self, offer: NegotiationOffer) -> None:
        """Add an offer to the negotiation."""
        offer.round_number = self.current_round
        self.offers.append(offer)
        self.last_offer_at = datetime.now()

        if offer.offer_type == OfferType.COUNTER:
            self.current_round += 1

    def is_expired(self) -> bool:
        """Check if negotiation has expired."""
        return (datetime.now() - self.last_offer_at).total_seconds() > (self.timeout_minutes * 60)

    def is_max_rounds_reached(self) -> bool:
        """Check if maximum rounds have been reached."""
        return self.current_round >= self.max_rounds

    def get_latest_offer(self) -> Optional[NegotiationOffer]:
        """Get the latest offer in the negotiation."""
        return self.offers[-1] if self.offers else None

    def get_offer_history(self) -> List[NegotiationOffer]:
        """Get all offers in chronological order."""
        return self.offers.copy()


class NegotiationStrategy:
    """Base class for negotiation strategies."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def make_initial_offer(
        self,
        negotiation: Negotiation,
        available_resources: Dict[str, float],
        desired_resources: Dict[str, float],
    ) -> NegotiationOffer:
        """Make an initial offer in a negotiation."""
        raise NotImplementedError

    def respond_to_offer(
        self,
        negotiation: Negotiation,
        received_offer: NegotiationOffer,
        available_resources: Dict[str, float],
        desired_resources: Dict[str, float],
    ) -> Optional[NegotiationOffer]:
        """Respond to an offer with accept, reject, or counter-offer."""
        raise NotImplementedError


class CooperativeStrategy(NegotiationStrategy):
    """Cooperative negotiation strategy - seeks fair deals."""

    def make_initial_offer(
        self,
        negotiation: Negotiation,
        available_resources: Dict[str, float],
        desired_resources: Dict[str, float],
    ) -> NegotiationOffer:
        """Make a fair initial offer."""
        # Offer 80-90% of what we have available
        offered_resources = {}
        for resource, amount in available_resources.items():
            offered_resources[resource] = amount * random.uniform(0.8, 0.9)

        # Request 70-80% of what they might have
        requested_resources = {}
        for resource, amount in desired_resources.items():
            requested_resources[resource] = amount * random.uniform(0.7, 0.8)

        offer = NegotiationOffer(
            offerer_id=self.agent_id,
            receiver_id=negotiation.partner_id,
            offer_type=OfferType.INITIAL,
            offered_resources=offered_resources,
            requested_resources=requested_resources,
        )
        offer.fairness_score = offer.calculate_fairness()

        return offer

    def respond_to_offer(
        self,
        negotiation: Negotiation,
        received_offer: NegotiationOffer,
        available_resources: Dict[str, float],
        desired_resources: Dict[str, float],
    ) -> Optional[NegotiationOffer]:
        """Respond cooperatively to an offer."""
        # Accept if offer is fair enough
        if received_offer.fairness_score > 0.7:
            return None  # Accept the offer

        # Make a counter-offer that's slightly more favorable
        offered_resources = {}
        for resource, amount in received_offer.requested_resources.items():
            if resource in available_resources:
                offered_resources[resource] = min(amount, available_resources[resource])

        requested_resources = {}
        for resource, amount in received_offer.offered_resources.items():
            if resource in desired_resources:
                requested_resources[resource] = amount * 0.9  # Slightly less than offered

        counter_offer = NegotiationOffer(
            offerer_id=self.agent_id,
            receiver_id=negotiation.initiator_id,
            offer_type=OfferType.COUNTER,
            offered_resources=offered_resources,
            requested_resources=requested_resources,
        )
        counter_offer.fairness_score = counter_offer.calculate_fairness()

        return counter_offer


class AggressiveStrategy(NegotiationStrategy):
    """Aggressive negotiation strategy - seeks maximum benefit."""

    def make_initial_offer(
        self,
        negotiation: Negotiation,
        available_resources: Dict[str, float],
        desired_resources: Dict[str, float],
    ) -> NegotiationOffer:
        """Make an aggressive initial offer."""
        # Offer minimal resources
        offered_resources = {}
        for resource, amount in available_resources.items():
            offered_resources[resource] = amount * random.uniform(0.3, 0.5)

        # Request maximum resources
        requested_resources = {}
        for resource, amount in desired_resources.items():
            requested_resources[resource] = amount * random.uniform(1.2, 1.5)

        offer = NegotiationOffer(
            offerer_id=self.agent_id,
            receiver_id=negotiation.partner_id,
            offer_type=OfferType.INITIAL,
            offered_resources=offered_resources,
            requested_resources=requested_resources,
        )
        offer.fairness_score = offer.calculate_fairness()

        return offer

    def respond_to_offer(
        self,
        negotiation: Negotiation,
        received_offer: NegotiationOffer,
        available_resources: Dict[str, float],
        desired_resources: Dict[str, float],
    ) -> Optional[NegotiationOffer]:
        """Respond aggressively to an offer."""
        # Only accept if very favorable
        if received_offer.fairness_score < 0.3:  # Unfair to them, good for us
            return None  # Accept the offer

        # Make a counter-offer that's even more aggressive
        offered_resources = {}
        for resource, amount in received_offer.requested_resources.items():
            if resource in available_resources:
                offered_resources[resource] = amount * random.uniform(0.5, 0.7)

        requested_resources = {}
        for resource, amount in received_offer.offered_resources.items():
            if resource in desired_resources:
                requested_resources[resource] = amount * random.uniform(1.1, 1.3)

        counter_offer = NegotiationOffer(
            offerer_id=self.agent_id,
            receiver_id=negotiation.initiator_id,
            offer_type=OfferType.COUNTER,
            offered_resources=offered_resources,
            requested_resources=requested_resources,
        )
        counter_offer.fairness_score = counter_offer.calculate_fairness()

        return counter_offer


class DiplomaticStrategy(NegotiationStrategy):
    """Diplomatic negotiation strategy - balances cooperation and self-interest."""

    def make_initial_offer(
        self,
        negotiation: Negotiation,
        available_resources: Dict[str, float],
        desired_resources: Dict[str, float],
    ) -> NegotiationOffer:
        """Make a diplomatic initial offer."""
        # Offer moderate resources
        offered_resources = {}
        for resource, amount in available_resources.items():
            offered_resources[resource] = amount * random.uniform(0.6, 0.8)

        # Request moderate resources
        requested_resources = {}
        for resource, amount in desired_resources.items():
            requested_resources[resource] = amount * random.uniform(0.8, 1.0)

        offer = NegotiationOffer(
            offerer_id=self.agent_id,
            receiver_id=negotiation.partner_id,
            offer_type=OfferType.INITIAL,
            offered_resources=offered_resources,
            requested_resources=requested_resources,
        )
        offer.fairness_score = offer.calculate_fairness()

        return offer

    def respond_to_offer(
        self,
        negotiation: Negotiation,
        received_offer: NegotiationOffer,
        available_resources: Dict[str, float],
        desired_resources: Dict[str, float],
    ) -> Optional[NegotiationOffer]:
        """Respond diplomatically to an offer."""
        # Accept if reasonably fair
        if received_offer.fairness_score > 0.6:
            return None  # Accept the offer

        # Make a balanced counter-offer
        offered_resources = {}
        for resource, amount in received_offer.requested_resources.items():
            if resource in available_resources:
                offered_resources[resource] = amount * random.uniform(0.8, 1.0)

        requested_resources = {}
        for resource, amount in received_offer.offered_resources.items():
            if resource in desired_resources:
                requested_resources[resource] = amount * random.uniform(0.9, 1.1)

        counter_offer = NegotiationOffer(
            offerer_id=self.agent_id,
            receiver_id=negotiation.initiator_id,
            offer_type=OfferType.COUNTER,
            offered_resources=offered_resources,
            requested_resources=requested_resources,
        )
        counter_offer.fairness_score = counter_offer.calculate_fairness()

        return counter_offer


class MarketFallback:
    """Market fallback mechanism for failed negotiations."""

    def __init__(self):
        self.market_orders: List[Dict[str, Any]] = []
        self.clearing_history: List[Dict[str, Any]] = []

    def add_buy_order(self, agent_id: str, resource: str, quantity: float, max_price: float) -> str:
        """Add a buy order to the market."""
        order_id = str(uuid.uuid4())
        order = {
            "order_id": order_id,
            "agent_id": agent_id,
            "order_type": "buy",
            "resource": resource,
            "quantity": quantity,
            "max_price": max_price,
            "timestamp": datetime.now(),
        }
        self.market_orders.append(order)
        return order_id

    def add_sell_order(
        self, agent_id: str, resource: str, quantity: float, min_price: float
    ) -> str:
        """Add a sell order to the market."""
        order_id = str(uuid.uuid4())
        order = {
            "order_id": order_id,
            "agent_id": agent_id,
            "order_type": "sell",
            "resource": resource,
            "quantity": quantity,
            "min_price": min_price,
            "timestamp": datetime.now(),
        }
        self.market_orders.append(order)
        return order_id

    def clear_market(self) -> List[Dict[str, Any]]:
        """Clear the market using double auction mechanism."""
        trades = []

        # Group orders by resource
        resource_orders: Dict[str, Dict[str, list]] = defaultdict(lambda: {"buy": [], "sell": []})
        for order in self.market_orders:
            resource = order["resource"]
            if order["order_type"] == "buy":
                resource_orders[resource]["buy"].append(order)
            else:
                resource_orders[resource]["sell"].append(order)

        # Clear each resource market
        for resource, orders in resource_orders.items():
            buy_orders = sorted(orders["buy"], key=lambda x: x["max_price"], reverse=True)
            sell_orders = sorted(orders["sell"], key=lambda x: x["min_price"])

            # Match orders
            for buy_order in buy_orders:
                for sell_order in sell_orders:
                    if (
                        buy_order["max_price"] >= sell_order["min_price"]
                        and buy_order["quantity"] > 0
                        and sell_order["quantity"] > 0
                    ):
                        # Calculate trade quantity and price
                        trade_quantity = min(buy_order["quantity"], sell_order["quantity"])
                        trade_price = (buy_order["max_price"] + sell_order["min_price"]) / 2

                        # Execute trade
                        trade = {
                            "trade_id": str(uuid.uuid4()),
                            "buyer_id": buy_order["agent_id"],
                            "seller_id": sell_order["agent_id"],
                            "resource": resource,
                            "quantity": trade_quantity,
                            "price": trade_price,
                            "timestamp": datetime.now(),
                        }
                        trades.append(trade)

                        # Update order quantities
                        buy_order["quantity"] -= trade_quantity
                        sell_order["quantity"] -= trade_quantity

                        if sell_order["quantity"] == 0:
                            break

                if buy_order["quantity"] == 0:
                    break

        # Remove completed orders
        self.market_orders = [order for order in self.market_orders if order["quantity"] > 0]

        self.clearing_history.append(
            {
                "timestamp": datetime.now(),
                "trades": trades,
                "remaining_orders": len(self.market_orders),
            }
        )

        return trades


class NegotiationEngine:
    """Main negotiation engine that manages all negotiations."""

    def __init__(self):
        self.active_negotiations: Dict[str, Negotiation] = {}
        self.completed_negotiations: List[Negotiation] = []
        self.negotiation_strategies: Dict[str, NegotiationStrategy] = {}
        self.market_fallback = MarketFallback()

    def create_strategy(self, agent_id: str, strategy_type: str) -> NegotiationStrategy:
        """Create a negotiation strategy for an agent."""
        strategy: NegotiationStrategy
        if strategy_type == "cooperative":
            strategy = CooperativeStrategy(agent_id)
        elif strategy_type == "aggressive":
            strategy = AggressiveStrategy(agent_id)
        elif strategy_type == "diplomatic":
            strategy = DiplomaticStrategy(agent_id)
        else:
            strategy = DiplomaticStrategy(agent_id)  # Default

        self.negotiation_strategies[agent_id] = strategy
        return strategy

    def start_negotiation(
        self, initiator_id: str, partner_id: str, negotiation_type: str = "trade"
    ) -> Negotiation:
        """Start a new negotiation."""
        negotiation = Negotiation(
            initiator_id=initiator_id, partner_id=partner_id, negotiation_type=negotiation_type
        )

        self.active_negotiations[negotiation.negotiation_id] = negotiation
        return negotiation

    def process_negotiation_round(
        self, negotiation_id: str, agent_resources: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Process a round of negotiation."""
        if negotiation_id not in self.active_negotiations:
            return {"error": "Negotiation not found"}

        negotiation = self.active_negotiations[negotiation_id]

        # Check if negotiation has expired or reached max rounds
        if negotiation.is_expired():
            negotiation.status = NegotiationStatus.TIMEOUT
            self._complete_negotiation(negotiation)
            return {"status": "timeout"}

        if negotiation.is_max_rounds_reached():
            negotiation.status = NegotiationStatus.FAILED
            self._complete_negotiation(negotiation)
            return {"status": "failed", "reason": "max_rounds_reached"}

        # Determine whose turn it is to make an offer
        latest_offer = negotiation.get_latest_offer()

        if latest_offer is None:
            # First offer - initiator makes initial offer
            current_agent = negotiation.initiator_id
            other_agent = negotiation.partner_id
        else:
            # Subsequent offers - alternate
            current_agent = (
                negotiation.partner_id
                if latest_offer.offerer_id == negotiation.initiator_id
                else negotiation.initiator_id
            )
            other_agent = (
                negotiation.initiator_id
                if latest_offer.offerer_id == negotiation.initiator_id
                else negotiation.partner_id
            )

        # Get agent strategy
        strategy = self.negotiation_strategies.get(current_agent)
        if not strategy:
            strategy = self.create_strategy(current_agent, "diplomatic")

        # Make offer
        offer: Optional[NegotiationOffer]
        if latest_offer is None:
            # Initial offer
            available_resources = agent_resources.get(current_agent, {})
            desired_resources = agent_resources.get(other_agent, {})
            offer = strategy.make_initial_offer(negotiation, available_resources, desired_resources)
        else:
            # Response to previous offer
            available_resources = agent_resources.get(current_agent, {})
            desired_resources = agent_resources.get(other_agent, {})
            offer = strategy.respond_to_offer(
                negotiation, latest_offer, available_resources, desired_resources
            )

        if offer is None:
            # Accept previous offer
            negotiation.status = NegotiationStatus.COMPLETED
            negotiation.final_agreement = latest_offer
            self._complete_negotiation(negotiation)
            return {"status": "completed", "agreement": latest_offer}
        else:
            # Add counter offer
            negotiation.add_offer(offer)
            return {"status": "active", "offer": offer}

    def _complete_negotiation(self, negotiation: Negotiation) -> None:
        """Complete a negotiation and move it to completed list."""
        if negotiation.negotiation_id in self.active_negotiations:
            del self.active_negotiations[negotiation.negotiation_id]
        self.completed_negotiations.append(negotiation)

    def get_negotiation_status(self, negotiation_id: str) -> Dict[str, Any]:
        """Get status of a negotiation."""
        if negotiation_id in self.active_negotiations:
            negotiation = self.active_negotiations[negotiation_id]
            return {
                "status": negotiation.status.value,
                "current_round": negotiation.current_round,
                "max_rounds": negotiation.max_rounds,
                "latest_offer": negotiation.get_latest_offer(),
                "is_expired": negotiation.is_expired(),
            }

        # Check completed negotiations
        for negotiation in self.completed_negotiations:
            if negotiation.negotiation_id == negotiation_id:
                return {
                    "status": negotiation.status.value,
                    "final_agreement": negotiation.final_agreement,
                    "completed_at": negotiation.created_at,
                }

        return {"error": "Negotiation not found"}

    def update_negotiations(self) -> Dict[str, Any]:
        """Update all active negotiations."""
        completed: List[str] = []
        failed = []

        for negotiation in list(self.active_negotiations.values()):
            if negotiation.is_expired():
                negotiation.status = NegotiationStatus.TIMEOUT
                self._complete_negotiation(negotiation)
                failed.append(negotiation.negotiation_id)
            elif negotiation.is_max_rounds_reached():
                negotiation.status = NegotiationStatus.FAILED
                self._complete_negotiation(negotiation)
                failed.append(negotiation.negotiation_id)

        # Clear market for failed negotiations
        if failed:
            market_trades = self.market_fallback.clear_market()
            return {
                "completed_negotiations": completed,
                "failed_negotiations": failed,
                "market_trades": market_trades,
            }

        return {
            "completed_negotiations": completed,
            "failed_negotiations": failed,
            "market_trades": [],
        }

    def get_negotiation_summary(self) -> Dict[str, Any]:
        """Get summary of negotiation activity."""
        return {
            "active_negotiations": len(self.active_negotiations),
            "completed_negotiations": len(self.completed_negotiations),
            "successful_negotiations": len(
                [n for n in self.completed_negotiations if n.status == NegotiationStatus.COMPLETED]
            ),
            "failed_negotiations": len(
                [
                    n
                    for n in self.completed_negotiations
                    if n.status in [NegotiationStatus.FAILED, NegotiationStatus.TIMEOUT]
                ]
            ),
            "market_orders": len(self.market_fallback.market_orders),
            "market_clearings": len(self.market_fallback.clearing_history),
        }
