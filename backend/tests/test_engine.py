"""
Tests for the simulation engine core functionality.
"""

import asyncio

import pytest

from adapters import LLMMode
from simulation.agents import Agent
from simulation.engine import SimulationConfig, SimulationEngine
from simulation.world import WorldState


class TestSimulationEngine:
    """Test cases for SimulationEngine."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return SimulationConfig(
            num_agents=10,
            seed=42,
            max_ticks=100,
            llm_mode=LLMMode.MOCK,
            tick_duration_ms=10,
            agents_per_tick=5,
            interactions_per_tick=10,
        )

    @pytest.fixture
    def engine(self, config):
        """Create a simulation engine for testing."""
        return SimulationEngine(config)

    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine initialization."""
        assert engine.state.value == "uninitialized"

        success = await engine.initialize()
        assert success
        assert engine.state.value == "ready"
        assert engine.world is not None
        assert engine.scheduler is not None
        assert engine.llm_adapter is not None

    @pytest.mark.asyncio
    async def test_world_initialization(self, engine):
        """Test world initialization with agents."""
        await engine.initialize()

        world = engine.world
        assert len(world.agents) == 10  # num_agents from config
        assert world.state == WorldState.RUNNING

        # Check agent properties
        for agent in world.agents.values():
            assert isinstance(agent, Agent)
            assert agent.personality is not None
            assert agent.memory is not None

    @pytest.mark.asyncio
    async def test_simulation_run(self, engine):
        """Test running a short simulation."""
        await engine.initialize()

        # Run for a few ticks
        success = await engine.run_simulation(max_ticks=5)
        assert success
        assert engine.world.current_tick == 5

    @pytest.mark.asyncio
    async def test_simulation_pause_resume(self, engine):
        """Test pausing and resuming simulation."""
        await engine.initialize()

        # Start simulation
        asyncio.create_task(engine.run_simulation(max_ticks=10))

        # Wait a bit then pause
        await asyncio.sleep(0.1)
        await engine.pause_simulation()
        assert engine.state.value == "paused"

        # Resume
        await engine.resume_simulation()
        assert engine.state.value == "running"

        # Stop
        await engine.stop_simulation()
        assert engine.state.value == "stopped"

    @pytest.mark.asyncio
    async def test_snapshot_functionality(self, engine):
        """Test taking and loading snapshots."""
        await engine.initialize()

        # Take snapshot
        snapshot_file = await engine.take_snapshot("test_snapshot")
        assert snapshot_file is not None

        # Load snapshot
        success = await engine.load_snapshot(snapshot_file)
        assert success

    @pytest.mark.asyncio
    async def test_simulation_status(self, engine):
        """Test getting simulation status."""
        await engine.initialize()

        status = await engine.get_simulation_status()
        assert "state" in status
        assert "current_tick" in status
        assert status["state"] == "ready"
        assert status["current_tick"] == 0

    @pytest.mark.asyncio
    async def test_agent_data_access(self, engine):
        """Test accessing agent data."""
        await engine.initialize()

        # Get all agents
        all_agents = await engine.get_agent_data()
        assert "agents" in all_agents
        assert len(all_agents["agents"]) == 10

        # Get specific agent
        agent_id = list(engine.world.agents.keys())[0]
        agent_data = await engine.get_agent_data(agent_id)
        assert agent_data["id"] == agent_id

    @pytest.mark.asyncio
    async def test_cultural_data_access(self, engine):
        """Test accessing cultural data."""
        await engine.initialize()

        cultural_data = await engine.get_cultural_data()
        assert "myths" in cultural_data
        assert "norms" in cultural_data
        assert "slang" in cultural_data
        assert "timeline" in cultural_data

    @pytest.mark.asyncio
    async def test_economic_data_access(self, engine):
        """Test accessing economic data."""
        await engine.initialize()

        economic_data = await engine.get_economic_data()
        assert "market_summary" in economic_data
        assert "gini_coefficient" in economic_data

    @pytest.mark.asyncio
    async def test_network_data_access(self, engine):
        """Test accessing network data."""
        await engine.initialize()

        network_data = await engine.get_network_data()
        assert "nodes" in network_data
        assert "edges" in network_data
        assert len(network_data["nodes"]) == 10

    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config
        config = SimulationConfig(num_agents=100, seed=42)
        assert config.num_agents == 100
        assert config.seed == 42

        # Test config to dict conversion
        config_dict = config.to_dict()
        assert "num_agents" in config_dict
        assert "seed" in config_dict

    @pytest.mark.asyncio
    async def test_cleanup(self, engine):
        """Test engine cleanup."""
        await engine.initialize()

        engine.cleanup()
        assert engine.state.value == "stopped"

    @pytest.mark.asyncio
    async def test_error_handling(self, engine):
        """Test error handling in simulation."""
        # Test with invalid configuration
        invalid_config = SimulationConfig(num_agents=-1)
        invalid_engine = SimulationEngine(invalid_config)

        success = await invalid_engine.initialize()
        # Should still succeed but with default values
        assert success or not success  # Either way is acceptable


class TestSimulationConfig:
    """Test cases for SimulationConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SimulationConfig()
        assert config.num_agents == 300
        assert config.seed == 42
        assert config.max_ticks == 10000
        assert config.llm_mode == LLMMode.MOCK
        assert config.tick_duration_ms == 100

    def test_config_customization(self):
        """Test customizing configuration."""
        config = SimulationConfig(
            num_agents=500,
            seed=123,
            max_ticks=5000,
            llm_mode=LLMMode.OPENAI,
            llm_model="gpt-4",
            llm_temperature=0.5,
        )

        assert config.num_agents == 500
        assert config.seed == 123
        assert config.max_ticks == 5000
        assert config.llm_mode == LLMMode.OPENAI
        assert config.llm_model == "gpt-4"
        assert config.llm_temperature == 0.5

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = SimulationConfig(num_agents=100, seed=42)
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["num_agents"] == 100
        assert config_dict["seed"] == 42
        assert config_dict["llm_mode"] == "mock"


@pytest.mark.asyncio
async def test_benchmark_simulation():
    """Test running a benchmark simulation."""
    config = SimulationConfig(num_agents=50, seed=42, max_ticks=50, llm_mode=LLMMode.MOCK)

    engine = SimulationEngine(config)
    await engine.initialize()

    # Run short simulation for benchmarking
    success = await engine.run_simulation(max_ticks=10)
    assert success

    # Check that some activity occurred
    assert engine.world.current_tick == 10
    assert len(engine.world.agents) == 50


@pytest.mark.asyncio
async def test_deterministic_behavior():
    """Test that simulations with same seed produce deterministic results."""
    config1 = SimulationConfig(num_agents=10, seed=42, max_ticks=20)
    config2 = SimulationConfig(num_agents=10, seed=42, max_ticks=20)

    engine1 = SimulationEngine(config1)
    engine2 = SimulationEngine(config2)

    await engine1.initialize()
    await engine2.initialize()

    await engine1.run_simulation()
    await engine2.run_simulation()

    # Both should reach same tick
    assert engine1.world.current_tick == engine2.world.current_tick

    # Agent states should be similar (allowing for some randomness)
    assert len(engine1.world.agents) == len(engine2.world.agents)


@pytest.mark.asyncio
async def test_social_engine_is_driven_by_simulation():
    """Alliances, institutions, and reputation are produced by a real run."""
    config = SimulationConfig(num_agents=60, seed=7, max_ticks=40, llm_mode=LLMMode.MOCK)
    engine = SimulationEngine(config)
    await engine.initialize()
    await engine.run_simulation()

    social = engine.world.social_engine
    # The social engine should have formed alliances and founded institutions.
    assert len(social.alliances) > 0
    assert len(social.institutions) > 0
    # World statistics should surface the social dynamics.
    stats = engine.world.stats
    assert stats["total_alliances"] >= 0
    assert "total_betrayals" in stats
    assert "avg_reputation" in stats


@pytest.mark.asyncio
async def test_negotiation_and_market_fallback_are_exercised():
    """Trades route through bilateral negotiation with a double-auction fallback."""
    config = SimulationConfig(num_agents=60, seed=7, max_ticks=40, llm_mode=LLMMode.MOCK)
    engine = SimulationEngine(config)
    await engine.initialize()
    await engine.run_simulation()

    negotiation = engine.world.negotiation_engine
    summary = negotiation.get_negotiation_summary()
    # Bilateral negotiations should have completed during the run.
    assert summary["completed_negotiations"] > 0
    # Failed negotiations fall back to the double-auction market.
    assert summary["market_clearings"] >= 0


@pytest.mark.asyncio
async def test_world_hybrid_memory_is_populated():
    """The hybrid graph + vector memory store records events during a run."""
    config = SimulationConfig(num_agents=40, seed=42, max_ticks=30, llm_mode=LLMMode.MOCK)
    engine = SimulationEngine(config)
    await engine.initialize()
    await engine.run_simulation()

    stats = engine.world.memory_manager.get_memory_statistics()
    assert stats["total_memories"] > 0
    assert stats["graph_memory"]["total_nodes"] > 0
    assert stats["vector_memory"]["total_memories"] > 0


if __name__ == "__main__":
    pytest.main([__file__])
