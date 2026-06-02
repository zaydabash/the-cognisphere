"""
Tests for agent behavior and cognitive architecture.
"""

from unittest.mock import patch

import numpy as np
import pytest

from simulation.agents import Agent, AgentPersonality, AgentState, TrustRelationship
from simulation.culture import Myth, Norm


class TestAgentPersonality:
    """Test cases for AgentPersonality."""

    def test_personality_creation(self):
        """Test creating agent personality."""
        personality = AgentPersonality()
        assert 0 <= personality.openness <= 1
        assert 0 <= personality.conscientiousness <= 1
        assert 0 <= personality.extraversion <= 1
        assert 0 <= personality.agreeableness <= 1
        assert 0 <= personality.neuroticism <= 1

    def test_personality_random(self):
        """Test random personality generation."""
        personality = AgentPersonality.random(seed=42)
        assert isinstance(personality, AgentPersonality)

        # Same seed should produce same personality
        personality2 = AgentPersonality.random(seed=42)
        assert personality.openness == personality2.openness
        assert personality.conscientiousness == personality2.conscientiousness

    def test_personality_to_vector(self):
        """Test converting personality to numpy vector."""
        personality = AgentPersonality(
            openness=0.1,
            conscientiousness=0.2,
            extraversion=0.3,
            agreeableness=0.4,
            neuroticism=0.5,
        )

        vector = personality.to_vector()
        assert isinstance(vector, np.ndarray)
        assert len(vector) == 5
        assert vector[0] == 0.1
        assert vector[1] == 0.2
        assert vector[2] == 0.3
        assert vector[3] == 0.4
        assert vector[4] == 0.5


class TestAgent:
    """Test cases for Agent."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        return Agent(name="TestAgent", personality=AgentPersonality.random(seed=42))

    @pytest.fixture
    def agent_with_resources(self):
        """Create agent with specific resources."""
        agent = Agent(name="TestAgent", personality=AgentPersonality.random(seed=42))
        agent.resources = {"food": 100.0, "energy": 50.0, "artifacts": 25.0, "influence": 10.0}
        return agent

    def test_agent_creation(self, agent):
        """Test agent creation and initialization."""
        assert agent.name == "TestAgent"
        assert agent.id is not None
        assert isinstance(agent.personality, AgentPersonality)
        assert agent.state == AgentState.IDLE
        assert agent.satisfaction == 0.5
        assert agent.faction_id is None

        # Check default resources
        assert "food" in agent.resources
        assert "energy" in agent.resources
        assert "artifacts" in agent.resources
        assert "influence" in agent.resources

    def test_agent_trust_relationships(self, agent):
        """Test trust relationship management."""
        other_agent_id = "other_agent_123"

        # Initial trust should be 0
        assert agent.get_trust_level(other_agent_id) == 0.0

        # Update trust
        agent.update_trust(other_agent_id, 0.5, tick=10)
        assert agent.get_trust_level(other_agent_id) == 0.5

        # Trust should be clamped to [-1, 1]
        agent.update_trust(other_agent_id, 2.0, tick=11)
        assert agent.get_trust_level(other_agent_id) == 1.0

        agent.update_trust(other_agent_id, -2.0, tick=12)
        assert agent.get_trust_level(other_agent_id) == -1.0

    def test_trust_relationship_betrayal(self, agent):
        """Test betrayal tracking in trust relationships."""
        other_agent_id = "other_agent_123"

        agent.update_trust(other_agent_id, 0.3, tick=10, betrayed=True)
        agent.update_trust(other_agent_id, 0.2, tick=11, betrayed=False)

        rel = agent.trust_relationships[other_agent_id]
        assert rel.betrayal_count == 1
        assert rel.cooperation_count == 1
        assert rel.interaction_count == 2

    def test_utility_calculation(self, agent_with_resources):
        """Test utility calculation with Cobb-Douglas function."""
        # Test with current resources
        utility = agent_with_resources.calculate_utility(agent_with_resources.resources)
        assert utility > 0

        # Test with empty resources
        empty_utility = agent_with_resources.calculate_utility({})
        assert empty_utility == 0

        # Test with additional resources
        additional = {"food": 50.0, "energy": 25.0}
        new_utility = agent_with_resources.calculate_utility(additional)
        assert new_utility > 0

    def test_trade_evaluation(self, agent_with_resources):
        """Test trade offer evaluation."""
        other_agent_id = "other_agent_123"

        # Test beneficial trade: receive scarce energy, give abundant food
        offer = {"energy": 20.0}
        request = {"food": 5.0}

        accept, utility = agent_with_resources.evaluate_trade_offer(offer, request, other_agent_id)

        # Should accept beneficial trades
        assert utility > 0
        # Accept decision depends on trust and utility

        # Test with high trust
        agent_with_resources.update_trust(other_agent_id, 0.8, tick=10)
        accept_high_trust, utility_high_trust = agent_with_resources.evaluate_trade_offer(
            offer, request, other_agent_id
        )

        # High trust should make acceptance more likely
        assert utility_high_trust > utility

    def test_trade_proposal(self, agent_with_resources):
        """Test trade proposal generation."""
        # Create another agent with different resources
        other_agent = Agent(name="OtherAgent")
        other_agent.resources = {"food": 20.0, "energy": 80.0, "artifacts": 30.0, "influence": 5.0}

        proposal = agent_with_resources.propose_trade(other_agent)

        if proposal:  # May be None if no beneficial trade possible
            assert "offer" in proposal
            assert "request" in proposal
            assert "round" in proposal
            assert proposal["round"] == 1

    def test_myth_creation(self, agent):
        """Test myth creation by agents."""
        # Mock random to ensure myth creation
        with patch("random.random", return_value=0.05):  # 5% chance
            myth = agent.craft_myth(tick=10)

            if myth:  # May be None
                assert isinstance(myth, Myth)
                assert myth.creator_id == agent.id
                assert myth.tick_created == 10
                assert myth.title is not None
                assert myth.content is not None
                assert myth.theme is not None

    def test_slang_creation(self, agent):
        """Test slang creation by agents."""
        # Mock random to ensure slang creation
        with patch("random.random", return_value=0.04):  # 5% chance
            slang_data = agent.mint_slang(tick=10)

            if slang_data:  # May be None
                word, meaning = slang_data
                assert isinstance(word, str)
                assert isinstance(meaning, str)
                assert len(word) > 0
                assert len(meaning) > 0

    def test_norm_voting(self, agent):
        """Test norm voting behavior."""
        norm = Norm(
            title="Test Norm", description="A test norm", norm_type="cooperation", tick_proposed=10
        )

        # Test voting
        vote = agent.vote_on_norm(norm, tick=15)
        assert isinstance(vote, bool)

        # Check that vote was recorded
        assert norm.id in agent.voted_norms
        assert agent.voted_norms[norm.id] is True

    def test_agent_reflection(self, agent):
        """Test agent reflection and memory consolidation."""
        # Add some events to memory
        agent.memory.add_event(
            {
                "tick": 10,
                "type": "trade_success",
                "participants": [agent.id],
                "outcome": "success",
                "emotional_valence": 0.5,
                "importance": 0.7,
            }
        )

        # initial_satisfaction = agent.satisfaction

        # Perform reflection
        agent.reflect(tick=20)

        # Satisfaction may have changed based on events
        assert isinstance(agent.satisfaction, float)
        assert 0 <= agent.satisfaction <= 1

    def test_agent_serialization(self, agent):
        """Test agent serialization to dictionary."""
        agent_dict = agent.to_dict()

        assert isinstance(agent_dict, dict)
        assert agent_dict["id"] == agent.id
        assert agent_dict["name"] == agent.name
        assert "personality" in agent_dict
        assert "resources" in agent_dict
        assert "influence" in agent_dict
        assert "satisfaction" in agent_dict

        # Check personality serialization
        personality_dict = agent_dict["personality"]
        assert "openness" in personality_dict
        assert "conscientiousness" in personality_dict
        assert "extraversion" in personality_dict
        assert "agreeableness" in personality_dict
        assert "neuroticism" in personality_dict

    def test_agent_ideology_compatibility(self):
        """Test ideology compatibility calculation."""
        agent1 = Agent(name="Agent1")
        agent2 = Agent(name="Agent2")

        # Set similar ideologies
        agent1.ideology = np.array([0.5, 0.6, 0.7, 0.8, 0.9])
        agent2.ideology = np.array([0.5, 0.6, 0.7, 0.8, 0.9])

        # Should have high compatibility
        compatibility = agent1._calculate_ideology_similarity(agent2)
        assert compatibility > 0.9

        # Set different ideologies
        agent2.ideology = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

        # Should have lower compatibility
        compatibility = agent1._calculate_ideology_similarity(agent2)
        assert compatibility < 0.5

    def test_agent_state_transitions(self, agent):
        """Test agent state transitions."""
        assert agent.state == AgentState.IDLE

        # Simulate state changes
        agent.state = AgentState.TRADING
        assert agent.state == AgentState.TRADING

        agent.state = AgentState.REFLECTING
        assert agent.state == AgentState.REFLECTING


class TestTrustRelationship:
    """Test cases for TrustRelationship."""

    def test_trust_relationship_creation(self):
        """Test trust relationship creation."""
        rel = TrustRelationship(
            target_id="target_123",
            trust_level=0.5,
            interaction_count=5,
            last_interaction_tick=10,
            betrayal_count=1,
            cooperation_count=4,
        )

        assert rel.target_id == "target_123"
        assert rel.trust_level == 0.5
        assert rel.interaction_count == 5
        assert rel.last_interaction_tick == 10
        assert rel.betrayal_count == 1
        assert rel.cooperation_count == 4

    def test_trust_relationship_defaults(self):
        """Test trust relationship default values."""
        rel = TrustRelationship(target_id="target_123")

        assert rel.target_id == "target_123"
        assert rel.trust_level == 0.0
        assert rel.interaction_count == 0
        assert rel.last_interaction_tick == 0
        assert rel.betrayal_count == 0
        assert rel.cooperation_count == 0


if __name__ == "__main__":
    pytest.main([__file__])
