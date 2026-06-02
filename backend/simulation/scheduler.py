"""
Simulation scheduler for managing tick-based simulation execution.

Handles the discrete tick loop, event scheduling, and coordination
between different simulation systems.
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .agents import Agent
from .culture import Norm
from .economy import Trade, TradeStatus
from .memory import MemoryEvent
from .memory.graph import RelationshipType
from .social import InstitutionType
from .world import World


class SchedulerState(Enum):
    """Scheduler execution states."""

    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    STEPPING = "stepping"


@dataclass
class SchedulerConfig:
    """Configuration for the simulation scheduler."""

    tick_duration_ms: int = 100  # Milliseconds per tick
    max_ticks: int = 10000
    agents_per_tick: int = 50  # Number of agents to process per tick
    interactions_per_tick: int = 100  # Number of interactions per tick
    reflection_frequency: int = 10  # How often agents reflect
    culture_update_frequency: int = 5  # How often culture updates
    snapshot_frequency: int = 20  # How often to take snapshots
    event_generation_probability: float = 0.05  # Probability of generating events per tick


@dataclass
class TickResult:
    """Result of a single simulation tick."""

    tick: int
    duration_ms: float
    agents_processed: int
    interactions: int
    trades_completed: int
    myths_created: int
    norms_proposed: int
    events_processed: int
    errors: List[str] = field(default_factory=list)


class SimulationScheduler:
    """Manages the discrete tick-based simulation execution."""

    def __init__(self, world: World, config: SchedulerConfig):
        self.world = world
        self.config = config
        self.state = SchedulerState.STOPPED

        # Execution tracking
        self.current_tick = 0
        self.start_time: Optional[float] = None
        self.tick_start_time: Optional[float] = None
        self.tick_results: List[TickResult] = []

        # Performance tracking
        self.performance_stats = {
            "total_ticks": 0,
            "avg_tick_duration": 0.0,
            "total_duration": 0.0,
            "agents_processed": 0,
            "interactions_processed": 0,
        }

        # Event callbacks (may be sync or async; async results are awaited)
        self.tick_callbacks: List[Callable[[int], Any]] = []
        self.completion_callbacks: List[Callable[[], Any]] = []

    def add_tick_callback(self, callback: Callable[[int], Any]):
        """Add callback to be called after each tick."""
        self.tick_callbacks.append(callback)

    def add_completion_callback(self, callback: Callable[[], Any]):
        """Add callback to be called when simulation completes."""
        self.completion_callbacks.append(callback)

    async def run_simulation(self, max_ticks: Optional[int] = None) -> List[TickResult]:
        """Run the simulation for specified number of ticks."""
        if self.state == SchedulerState.RUNNING:
            raise RuntimeError("Simulation is already running")

        self.state = SchedulerState.RUNNING
        self.start_time = time.time()
        self.current_tick = 0

        max_ticks = max_ticks or self.config.max_ticks

        try:
            while (
                self.state == SchedulerState.RUNNING
                and self.current_tick < max_ticks
                and self.current_tick < self.world.tick_limit
            ):
                tick_result = await self.execute_tick()
                self.tick_results.append(tick_result)

                # Call tick callbacks
                for callback in self.tick_callbacks:
                    try:
                        result = callback(self.current_tick)
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as e:
                        print(f"Error in tick callback: {e}")

                # Check if we should pause
                if self.state == SchedulerState.STEPPING:
                    self.state = SchedulerState.PAUSED
                    break

                # Wait for tick duration
                await self._wait_for_tick_duration()

                self.current_tick += 1
                self.world.current_tick = self.current_tick

        except Exception as e:
            print(f"Simulation error: {e}")
            self.state = SchedulerState.STOPPED

        finally:
            # Call completion callbacks
            for completion_callback in self.completion_callbacks:
                try:
                    result = completion_callback()
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as e:
                    print(f"Error in completion callback: {e}")

            if self.state == SchedulerState.RUNNING:
                self.state = SchedulerState.STOPPED

        return self.tick_results

    async def execute_tick(self) -> TickResult:
        """Execute a single simulation tick."""
        self.tick_start_time = time.time()
        tick = self.current_tick

        result = TickResult(
            tick=tick,
            duration_ms=0.0,
            agents_processed=0,
            interactions=0,
            trades_completed=0,
            myths_created=0,
            norms_proposed=0,
            events_processed=0,
        )

        try:
            # 1. Generate random events
            await self._generate_events(tick)

            # 2. Process agent interactions
            interactions = await self._process_agent_interactions(tick)
            result.interactions = interactions

            # 3. Update economy
            await self._update_economy(tick)

            # 4. Update culture (less frequently)
            if tick % self.config.culture_update_frequency == 0:
                culture_updates = await self._update_culture(tick)
                result.myths_created = culture_updates.get("myths_created", 0)
                result.norms_proposed = culture_updates.get("norms_proposed", 0)

            # 5. Agent reflection (less frequently)
            if tick % self.config.reflection_frequency == 0:
                await self._agent_reflection(tick)

            # 6. Update world state
            await self._update_world_state(tick)

            # 7. Process events
            events_processed = await self._process_events(tick)
            result.events_processed = events_processed

            # 8. Update statistics
            self.world.update_statistics()

            # 9. Record tick history
            self.world.record_tick_history()

            # Update performance stats
            self.performance_stats["total_ticks"] += 1
            result.agents_processed = len(self.world.agents)

        except Exception as e:
            result.errors.append(str(e))
            print(f"Error in tick {tick}: {e}")

        # Calculate tick duration
        tick_duration = time.time() - self.tick_start_time
        result.duration_ms = tick_duration * 1000

        # Update performance stats
        self._update_performance_stats(tick_duration)

        return result

    async def _generate_events(self, tick: int):
        """Generate random events for the current tick."""
        # Generate random events
        event = self.world.event_system.generate_random_event(
            tick, list(self.world.agents.values()), self.world.stats
        )

        if event:
            event.active = True
            self.world.event_system.active_events.append(event)

    async def _process_agent_interactions(self, tick: int) -> int:
        """Process agent interactions for the current tick."""
        interactions = 0
        agents = list(self.world.agents.values())

        # Select random agents for interaction
        num_interactions = min(
            self.config.interactions_per_tick, len(agents) * (len(agents) - 1) // 2
        )

        for _ in range(num_interactions):
            if len(agents) < 2:
                break

            # Select two random agents
            agent1, agent2 = random.sample(agents, 2)

            # Determine interaction type
            interaction_type = self._select_interaction_type(agent1, agent2)

            if interaction_type == "trade":
                await self._process_trade_interaction(agent1, agent2, tick)
            elif interaction_type == "social":
                await self._process_social_interaction(agent1, agent2, tick)
            elif interaction_type == "cultural":
                await self._process_cultural_interaction(agent1, agent2, tick)

            interactions += 1

        return interactions

    def _select_interaction_type(self, agent1: Agent, agent2: Agent) -> str:
        """Select interaction type based on agent states and relationships."""
        # Check trust level
        trust_level = agent1.get_trust_level(agent2.id)

        # Determine interaction type based on trust and personality
        if trust_level > 0.5:
            # High trust - more likely to trade
            return random.choices(["trade", "social", "cultural"], weights=[0.6, 0.3, 0.1])[0]
        elif trust_level < -0.3:
            # Low trust - more likely to have conflicts
            return random.choices(["trade", "social", "cultural"], weights=[0.2, 0.7, 0.1])[0]
        else:
            # Neutral trust - balanced interactions
            return random.choices(["trade", "social", "cultural"], weights=[0.4, 0.4, 0.2])[0]

    async def _process_trade_interaction(self, agent1: Agent, agent2: Agent, tick: int):
        """Process trade interaction between two agents."""
        # Agent1 proposes trade
        trade_proposal = agent1.propose_trade(agent2)
        if not trade_proposal:
            return

        # Agent2 evaluates proposal
        accept, utility = agent2.evaluate_trade_offer(
            trade_proposal["offer"], trade_proposal["request"], agent1.id
        )

        if accept:
            # Execute trade
            for resource, amount in trade_proposal["offer"].items():
                if resource in agent1.resources and agent1.resources[resource] >= amount:
                    agent1.resources[resource] -= amount
                    agent2.resources[resource] = agent2.resources.get(resource, 0) + amount

            for resource, amount in trade_proposal["request"].items():
                if resource in agent2.resources and agent2.resources[resource] >= amount:
                    agent2.resources[resource] -= amount
                    agent1.resources[resource] = agent1.resources.get(resource, 0) + amount

            # Update trust relationships
            agent1.update_trust(agent2.id, 0.1, tick)
            agent2.update_trust(agent1.id, 0.1, tick)

            # Record trade
            trade = Trade(
                initiator_id=agent1.id,
                partner_id=agent2.id,
                resources_offered=trade_proposal["offer"],
                resources_requested=trade_proposal["request"],
                tick_created=tick,
                status=TradeStatus.COMPLETED,
            )
            self.world.economy.trade_history.append(trade)

            # Record the trade in the world's hybrid (graph + vector) memory
            if self.world.memory_manager is not None:
                self.world.memory_manager.add_episodic_memory(
                    content=f"Trade completed between {agent1.name} and {agent2.name}",
                    agent_id=agent1.id,
                    importance=0.6,
                    metadata={"tick": tick, "partner_id": agent2.id},
                )
        else:
            # Direct offer rejected - fall back to bilateral negotiation
            await self._negotiate_trade(agent1, agent2, trade_proposal, tick)

    async def _negotiate_trade(
        self, agent1: Agent, agent2: Agent, proposal: Dict[str, Any], tick: int
    ):
        """Run a bilateral negotiation; fall back to the double-auction market."""
        ne = self.world.negotiation_engine
        # Assign negotiation strategies from personality: agreeable agents
        # cooperate, disagreeable agents drive a hard bargain (which more often
        # collapses into the double-auction market fallback).
        for agent in (agent1, agent2):
            if agent.id not in ne.negotiation_strategies:
                if agent.personality.agreeableness > 0.6:
                    ne.create_strategy(agent.id, "cooperative")
                elif agent.personality.agreeableness < 0.35:
                    ne.create_strategy(agent.id, "aggressive")
                else:
                    ne.create_strategy(agent.id, "diplomatic")

        negotiation = ne.start_negotiation(agent1.id, agent2.id, "trade")
        agent_resources = {
            agent1.id: dict(agent1.resources),
            agent2.id: dict(agent2.resources),
        }

        result: Dict[str, Any] = {}
        for _ in range(negotiation.max_rounds + 2):
            result = ne.process_negotiation_round(negotiation.negotiation_id, agent_resources)
            if result.get("status") in ("completed", "failed", "timeout"):
                break

        if result.get("status") == "completed":
            # Bilateral negotiation succeeded
            agent1.update_trust(agent2.id, 0.08, tick)
            agent2.update_trust(agent1.id, 0.08, tick)
            self.world.economy.trade_history.append(
                Trade(
                    initiator_id=agent1.id,
                    partner_id=agent2.id,
                    resources_offered=proposal["offer"],
                    resources_requested=proposal["request"],
                    tick_created=tick,
                    status=TradeStatus.COMPLETED,
                )
            )
        else:
            # Negotiation failed - post orders to the double-auction market
            for resource, amount in proposal["offer"].items():
                ne.market_fallback.add_sell_order(agent1.id, resource, amount, min_price=1.0)
            for resource, amount in proposal["request"].items():
                ne.market_fallback.add_buy_order(agent2.id, resource, amount, max_price=5.0)
            ne.market_fallback.clear_market()
            agent1.update_trust(agent2.id, -0.05, tick)
            agent2.update_trust(agent1.id, -0.05, tick)

    async def _process_social_interaction(self, agent1: Agent, agent2: Agent, tick: int):
        """Process social interaction between two agents."""
        # Determine interaction outcome based on personality compatibility
        personality_compatibility = self._calculate_personality_compatibility(agent1, agent2)

        # Random factor
        random_factor = random.uniform(-0.3, 0.3)

        # Calculate trust change
        trust_change = personality_compatibility + random_factor
        trust_change = max(-0.2, min(0.2, trust_change))  # Clamp to reasonable range

        # Update trust relationships
        agent1.update_trust(agent2.id, trust_change, tick)
        agent2.update_trust(agent1.id, trust_change, tick)

        # Update satisfaction
        satisfaction_change = trust_change * 0.5
        agent1.satisfaction = max(0.0, min(1.0, agent1.satisfaction + satisfaction_change))
        agent2.satisfaction = max(0.0, min(1.0, agent2.satisfaction + satisfaction_change))

        # Drive higher-order social dynamics through the social engine
        se = self.world.social_engine
        mutual_trust = (agent1.get_trust_level(agent2.id) + agent2.get_trust_level(agent1.id)) / 2

        allied = agent2.id in se.social_network.get(agent1.id, set())

        if not allied and mutual_trust > 0.5 and personality_compatibility > 0.3:
            # Strong, compatible bond - form an alliance
            se.relationship_strengths[(agent1.id, agent2.id)] = max(
                0.5, se.relationship_strengths.get((agent1.id, agent2.id), 0.5)
            )
            if se.form_alliance(agent1.id, agent2.id) and self.world.memory_manager is not None:
                self.world.memory_manager.add_social_memory(
                    content=f"{agent1.name} allied with {agent2.name}",
                    agent_id=agent1.id,
                    other_agent_id=agent2.id,
                    relationship_type=RelationshipType.ALLIES_WITH,
                    valence=0.5,
                )
        elif allied and agent1.personality.agreeableness < 0.4:
            # Disagreeable agents may opportunistically betray an ally, or a
            # collapse of trust drives a betrayal. Both damage reputation and
            # dissolve the alliance.
            opportunistic = random.random() < 0.05
            hostile = mutual_trust < -0.1
            if opportunistic or hostile:
                alliance_id = next(
                    (
                        aid
                        for aid, a in se.alliances.items()
                        if agent1.id in a.members and agent2.id in a.members
                    ),
                    None,
                )
                se.execute_betrayal(
                    agent1.id,
                    agent2.id,
                    alliance_id=alliance_id,
                    reason="Opportunistic betrayal" if opportunistic else "Breakdown of trust",
                    severity=random.uniform(0.3, 0.8),
                )
                se.social_network[agent1.id].discard(agent2.id)
                se.social_network[agent2.id].discard(agent1.id)
                agent1.update_trust(agent2.id, -0.3, tick, betrayed=True)
                if self.world.memory_manager is not None:
                    self.world.memory_manager.add_social_memory(
                        content=f"{agent1.name} betrayed {agent2.name}",
                        agent_id=agent1.id,
                        other_agent_id=agent2.id,
                        relationship_type=RelationshipType.BETRAYED,
                        valence=-0.7,
                    )

    async def _process_cultural_interaction(self, agent1: Agent, agent2: Agent, tick: int):
        """Process cultural interaction between two agents."""
        # Share slang
        if agent1.language.vocabulary and agent2.language.vocabulary:
            # Agent1 shares slang with Agent2
            shared_word = random.choice(list(agent1.language.vocabulary.keys()))
            slang = agent1.language.vocabulary[shared_word]

            adoption_rate = random.uniform(0.05, 0.2)
            agent2.language.adopt_slang(slang.word, slang.meaning, adoption_rate)

        # Create shared cultural memory
        event = MemoryEvent(
            tick=tick,
            event_type="cultural_interaction",
            description="Cultural exchange between agents",
            participants=[agent1.id, agent2.id],
            outcome="cultural_exchange",
            emotional_valence=0.1,
        )

        agent1.memory.add_event(event)
        agent2.memory.add_event(event)

    def _calculate_personality_compatibility(self, agent1: Agent, agent2: Agent) -> float:
        """Calculate personality compatibility between two agents."""
        from scipy.spatial.distance import cosine

        p1 = agent1.personality.to_vector()
        p2 = agent2.personality.to_vector()

        try:
            similarity = 1 - cosine(p1, p2)
            return max(-1.0, min(1.0, similarity))
        except Exception:
            return 0.0

    async def _update_economy(self, tick: int):
        """Update economic systems."""
        # Produce and distribute resources
        # production = self.world.economy.produce_resources(tick)
        # distribution = self.world.economy.distribute_resources(
        #     list(self.world.agents.values()), production
        # )

        # Update market
        self.world.economy.update_market(tick, list(self.world.agents.values()))

        # Apply economic events
        self.world.economy.apply_events(tick)

    async def _update_culture(self, tick: int) -> Dict[str, int]:
        """Update cultural systems."""
        culture_updates = {"myths_created": 0, "norms_proposed": 0}

        # Language evolution
        self.world.culture.evolve_language(list(self.world.agents.values()), tick)

        # Myth canonization
        self.world.culture.canonize_myths(tick)

        # Agent myth creation
        for agent in self.world.agents.values():
            myth = agent.craft_myth(tick)
            if myth:
                self.world.culture.add_myth(myth)
                culture_updates["myths_created"] += 1

        # Norm enforcement
        self.world.culture.enforce_norms(list(self.world.agents.values()), tick)

        # Random norm proposals
        if random.random() < 0.1:  # 10% chance
            proposer = random.choice(list(self.world.agents.values()))
            # Create simple norm
            norm = Norm(
                title=f"New Rule by {proposer.name}",
                description="A new social rule has been proposed",
                norm_type=random.choice(["cooperation", "innovation", "order", "leadership"]),
                tick_proposed=tick,
            )
            self.world.culture.propose_norm(norm, proposer.id)
            culture_updates["norms_proposed"] += 1

        return culture_updates

    async def _agent_reflection(self, tick: int):
        """Process agent reflection and memory consolidation."""
        for agent in self.world.agents.values():
            agent.reflect(tick)

    async def _update_world_state(self, tick: int):
        """Update overall world state."""
        # Process faction dynamics
        self.world.process_faction_dynamics()

        # Advance social dynamics (alliance decay, faction stability)
        self.world.social_engine.update_social_state()

        # Resolve any negotiations that have timed out or maxed out their rounds
        self.world.negotiation_engine.update_negotiations()

        # Periodically found a lasting institution led by the most influential agent
        if tick > 0 and tick % self.config.culture_update_frequency == 0 and self.world.agents:
            se = self.world.social_engine
            if len(se.institutions) < 5:
                leader = max(self.world.agents.values(), key=lambda a: a.influence)
                institution_type = random.choice(list(InstitutionType))
                se.create_institution(
                    name=f"{institution_type.value.title()} of {leader.name}",
                    institution_type=institution_type,
                    founder_id=leader.id,
                    purpose="Maintain social order and continuity",
                )

    async def _process_events(self, tick: int) -> int:
        """Process active events."""
        completed_events = self.world.event_system.process_events(
            tick, list(self.world.agents.values()), self.world.economy, self.world.culture
        )
        return len(completed_events)

    async def _wait_for_tick_duration(self):
        """Wait for the configured tick duration."""
        if self.tick_start_time:
            elapsed = time.time() - self.tick_start_time
            target_duration = self.config.tick_duration_ms / 1000.0

            if elapsed < target_duration:
                await asyncio.sleep(target_duration - elapsed)

    def _update_performance_stats(self, tick_duration: float):
        """Update performance statistics."""
        total_duration = time.time() - self.start_time if self.start_time else 0.0

        self.performance_stats["total_duration"] = total_duration
        total_ticks = self.performance_stats["total_ticks"]
        if total_ticks > 0:
            self.performance_stats["avg_tick_duration"] = (
                self.performance_stats["avg_tick_duration"] * (total_ticks - 1) + tick_duration
            ) / total_ticks

    def pause(self):
        """Pause the simulation."""
        if self.state == SchedulerState.RUNNING:
            self.state = SchedulerState.PAUSED

    def resume(self):
        """Resume the simulation."""
        if self.state == SchedulerState.PAUSED:
            self.state = SchedulerState.RUNNING

    def step(self):
        """Step one tick forward."""
        if self.state == SchedulerState.PAUSED:
            self.state = SchedulerState.STEPPING

    def stop(self):
        """Stop the simulation."""
        self.state = SchedulerState.STOPPED

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            **self.performance_stats,
            "current_tick": self.current_tick,
            "state": self.state.value,
            "tick_results_count": len(self.tick_results),
        }

    def get_recent_tick_results(self, count: int = 10) -> List[TickResult]:
        """Get recent tick results."""
        return self.tick_results[-count:] if self.tick_results else []
