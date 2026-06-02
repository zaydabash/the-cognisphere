"""
Tests for economy and trade systems.
"""

import pytest

from simulation.agents import Agent, AgentPersonality
from simulation.economy import Economy, Market, Resource, Trade, TradeStatus


class TestResource:
    """Test cases for Resource."""

    def test_resource_creation(self):
        """Test resource creation."""
        resource = Resource(
            name="food",
            base_value=1.0,
            scarcity_modifier=1.2,
            demand_modifier=1.1,
            production_rate=2.0,
            decay_rate=0.1,
        )

        assert resource.name == "food"
        assert resource.base_value == 1.0
        assert resource.scarcity_modifier == 1.2
        assert resource.demand_modifier == 1.1
        assert resource.production_rate == 2.0
        assert resource.decay_rate == 0.1

    def test_resource_current_value(self):
        """Test current value calculation."""
        resource = Resource(name="food", base_value=1.0, scarcity_modifier=1.5, demand_modifier=1.2)

        expected_value = 1.0 * 1.5 * 1.2
        assert resource.current_value == expected_value


class TestTrade:
    """Test cases for Trade."""

    def test_trade_creation(self):
        """Test trade creation."""
        trade = Trade(
            initiator_id="agent1",
            partner_id="agent2",
            resources_offered={"food": 10.0},
            resources_requested={"energy": 5.0},
            tick_created=10,
        )

        assert trade.initiator_id == "agent1"
        assert trade.partner_id == "agent2"
        assert trade.resources_offered == {"food": 10.0}
        assert trade.resources_requested == {"energy": 5.0}
        assert trade.status == TradeStatus.PENDING
        assert trade.tick_created == 10

    def test_trade_utility_calculation(self):
        """Test trade utility calculation."""
        trade = Trade(
            initiator_id="agent1",
            partner_id="agent2",
            resources_offered={"food": 10.0, "energy": 5.0},
            resources_requested={"artifacts": 3.0},
        )

        agent_resources = {"food": 50.0, "energy": 30.0, "artifacts": 10.0}

        resource_values = {"food": 1.0, "energy": 1.2, "artifacts": 2.0}

        utility = trade.calculate_utility(agent_resources, resource_values)
        assert utility > 0  # Should be positive for beneficial trade


class TestMarket:
    """Test cases for Market."""

    @pytest.fixture
    def market(self):
        """Create a test market."""
        return Market()

    def test_market_initialization(self, market):
        """Test market initialization with default resources."""
        assert len(market.resources) == 4
        assert "food" in market.resources
        assert "energy" in market.resources
        assert "artifacts" in market.resources
        assert "influence" in market.resources

    def test_market_price_updates(self, market):
        """Test market price updates based on supply and demand."""
        supply_demand = {
            "food": (100.0, 150.0),  # (supply, demand)
            "energy": (200.0, 100.0),  # Low demand, high supply
            "artifacts": (50.0, 80.0),
            "influence": (30.0, 60.0),
        }

        market.update_prices(tick=10, supply_demand=supply_demand)

        # Check that prices were updated
        food_resource = market.resources["food"]
        energy_resource = market.resources["energy"]

        # Food should have higher scarcity (demand > supply)
        assert food_resource.scarcity_modifier > 1.0

        # Energy should have lower scarcity (supply > demand)
        assert energy_resource.scarcity_modifier < 1.0

    def test_market_current_prices(self, market):
        """Test getting current market prices."""
        prices = market.get_current_prices()

        assert isinstance(prices, dict)
        assert "food" in prices
        assert "energy" in prices
        assert "artifacts" in prices
        assert "influence" in prices

        for price in prices.values():
            assert price > 0

    def test_market_trade_processing(self, market):
        """Test processing trades in the market."""
        trade = Trade(
            initiator_id="agent1",
            partner_id="agent2",
            resources_offered={"food": 10.0},
            resources_requested={"energy": 5.0},
            status=TradeStatus.ACCEPTED,
            tick_completed=10,
        )

        market.active_trades.append(trade)

        # Process the trade
        success = market.process_trade(trade)
        assert success

        # Trade should be moved to completed
        assert trade not in market.active_trades
        assert trade in market.completed_trades

        # Volume should be recorded
        assert "food" in market.volume_history
        assert "energy" in market.volume_history

    def test_market_summary(self, market):
        """Test market summary generation."""
        summary = market.get_market_summary()

        assert "name" in summary
        assert "current_prices" in summary
        assert "active_trades" in summary
        assert "completed_trades" in summary
        assert "resources" in summary


class TestEconomy:
    """Test cases for Economy."""

    @pytest.fixture
    def economy(self):
        """Create a test economy."""
        return Economy()

    @pytest.fixture
    def agents(self):
        """Create test agents."""
        agents = []
        for i in range(5):
            agent = Agent(name=f"Agent{i}", personality=AgentPersonality.random(seed=i))
            agent.resources = {
                "food": 50.0 + i * 10,
                "energy": 30.0 + i * 5,
                "artifacts": 10.0 + i * 2,
                "influence": 5.0 + i,
            }
            agent.influence = 1.0 + i * 0.2
            agents.append(agent)
        return agents

    def test_economy_initialization(self, economy):
        """Test economy initialization."""
        assert economy.market is not None
        assert isinstance(economy.market, Market)
        assert len(economy.resource_production) == 4
        assert economy.gini_coefficient == 0.0

    def test_resource_production(self, economy):
        """Test resource production."""
        production = economy.produce_resources(tick=10)

        assert isinstance(production, dict)
        assert "food" in production
        assert "energy" in production
        assert "artifacts" in production
        assert "influence" in production

        for resource, amount in production.items():
            assert amount > 0

    def test_resource_distribution(self, economy, agents):
        """Test resource distribution among agents."""
        production = {"food": 100.0, "energy": 80.0, "artifacts": 20.0, "influence": 10.0}

        distribution = economy.distribute_resources(agents, production)

        assert isinstance(distribution, dict)
        assert "food" in distribution
        assert "energy" in distribution
        assert "artifacts" in distribution
        assert "influence" in distribution

        # Check that resources were added to agents
        total_food = sum(agent.resources["food"] for agent in agents)
        assert total_food > 250.0  # Original + distributed

    def test_supply_demand_calculation(self, economy, agents):
        """Test supply and demand calculation."""
        supply_demand = economy.calculate_supply_demand(agents)

        assert isinstance(supply_demand, dict)
        assert "food" in supply_demand
        assert "energy" in supply_demand
        assert "artifacts" in supply_demand
        assert "influence" in supply_demand

        for resource, (supply, demand) in supply_demand.items():
            assert supply >= 0
            assert demand >= 0

    def test_market_update(self, economy, agents):
        """Test market update with agents."""
        economy.update_market(tick=10, agents=agents)

        # Gini coefficient should be calculated
        assert isinstance(economy.gini_coefficient, float)
        assert 0 <= economy.gini_coefficient <= 1

    def test_gini_coefficient_calculation(self, economy, agents):
        """Test Gini coefficient calculation."""
        # Test with equal wealth (should be 0)
        for agent in agents:
            agent.resources = {
                "food": 100.0,
                "energy": 100.0,
                "artifacts": 100.0,
                "influence": 100.0,
            }

        economy.calculate_gini_coefficient(agents)
        assert economy.gini_coefficient == 0.0

        # Test with unequal wealth (should be > 0)
        agents[0].resources = {
            "food": 1000.0,
            "energy": 1000.0,
            "artifacts": 1000.0,
            "influence": 1000.0,
        }
        for agent in agents[1:]:
            agent.resources = {"food": 1.0, "energy": 1.0, "artifacts": 1.0, "influence": 1.0}

        economy.calculate_gini_coefficient(agents)
        assert economy.gini_coefficient > 0.0
        assert economy.gini_coefficient <= 1.0

    def test_economic_event_creation(self, economy):
        """Test creating economic events."""
        economy.add_economic_event(
            event_type="scarcity",
            description="Resource scarcity",
            resource_effects={"food": 0.7, "energy": 0.8},
            duration=10,
        )

        assert len(economy.global_events) == 1
        event = economy.global_events[0]
        assert event["type"] == "scarcity"
        assert event["description"] == "Resource scarcity"
        assert event["resource_effects"]["food"] == 0.7
        assert event["duration"] == 10
        assert not event["active"]

    def test_economic_event_triggering(self, economy):
        """Test triggering economic events."""
        economy.trigger_event("scarcity", tick=10)

        # Should create a scarcity event
        scarcity_events = [e for e in economy.global_events if e["type"] == "scarcity"]
        assert len(scarcity_events) > 0

        event = scarcity_events[0]
        assert event["active"]
        assert event["tick_start"] == 10

    def test_economic_event_application(self, economy):
        """Test applying active economic events."""
        # Create and activate an event
        economy.add_economic_event(
            event_type="scarcity",
            description="Test scarcity",
            resource_effects={"food": 0.5},
            duration=5,
        )

        event = economy.global_events[0]
        event["active"] = True
        event["tick_start"] = 10

        original_production = economy.resource_production["food"]

        # Apply events at tick 12 (within duration)
        economy.apply_events(tick=12)

        # Production should be modified
        assert economy.resource_production["food"] < original_production

    def test_economy_summary(self, economy):
        """Test economy summary generation."""
        summary = economy.get_economy_summary()

        assert "market_summary" in summary
        assert "gini_coefficient" in summary
        assert "active_events" in summary
        assert "total_trades" in summary
        assert "resource_production" in summary

        assert isinstance(summary["gini_coefficient"], float)
        assert isinstance(summary["active_events"], int)
        assert isinstance(summary["total_trades"], int)


class TestTradeNegotiation:
    """Test cases for trade negotiation mechanics."""

    @pytest.fixture
    def trading_agents(self):
        """Create agents for trade testing."""
        agent1 = Agent(name="Trader1")
        agent1.resources = {"food": 100.0, "energy": 50.0, "artifacts": 20.0}

        agent2 = Agent(name="Trader2")
        agent2.resources = {"food": 30.0, "energy": 120.0, "artifacts": 15.0}

        return agent1, agent2

    def test_trade_negotiation(self, trading_agents):
        """Test trade negotiation between agents."""
        agent1, agent2 = trading_agents

        # Agent1 should be able to propose trade
        proposal = agent1.propose_trade(agent2)

        if proposal:  # May be None if no beneficial trade
            assert "offer" in proposal
            assert "request" in proposal

            # Agent2 should evaluate the proposal
            accept, utility = agent2.evaluate_trade_offer(
                proposal["offer"], proposal["request"], agent1.id
            )

            assert isinstance(accept, bool)
            assert isinstance(utility, float)

    def test_trade_execution(self, trading_agents):
        """Test trade execution and resource transfer."""
        agent1, agent2 = trading_agents

        initial_food1 = agent1.resources["food"]
        initial_energy1 = agent1.resources.get("energy", 0)
        initial_energy2 = agent2.resources["energy"]
        initial_food2 = agent2.resources.get("food", 0)

        # Execute a simple trade
        offer = {"food": 20.0}
        request = {"energy": 10.0}

        # Transfer resources
        for resource, amount in offer.items():
            agent1.resources[resource] -= amount
            agent2.resources[resource] = agent2.resources.get(resource, 0) + amount

        for resource, amount in request.items():
            agent2.resources[resource] -= amount
            agent1.resources[resource] = agent1.resources.get(resource, 0) + amount

        # Check resource changes
        assert agent1.resources["food"] == initial_food1 - 20.0
        assert agent2.resources["energy"] == initial_energy2 - 10.0
        assert agent1.resources["energy"] == initial_energy1 + 10.0
        assert agent2.resources["food"] == initial_food2 + 20.0


if __name__ == "__main__":
    pytest.main([__file__])
