"""
Tests for cultural evolution systems.
"""

from unittest.mock import patch

import pytest

from simulation.agents import Agent, AgentPersonality
from simulation.culture import Culture, Language, Myth, Norm, Slang


class TestMyth:
    """Test cases for Myth."""

    def test_myth_creation(self):
        """Test myth creation."""
        myth = Myth(
            creator_id="agent123",
            title="The Great Discovery",
            content="Once upon a time, there was a great discovery...",
            theme="discovery",
            tick_created=10,
        )

        assert myth.creator_id == "agent123"
        assert myth.title == "The Great Discovery"
        assert myth.content.startswith("Once upon a time")
        assert myth.theme == "discovery"
        assert myth.tick_created == 10
        assert myth.popularity == 1.0
        assert myth.influence == 1.0
        assert myth.version == 1

    def test_myth_serialization(self):
        """Test myth serialization to dictionary."""
        myth = Myth(creator_id="agent123", title="Test Myth", content="Test content", theme="test")

        myth_dict = myth.to_dict()

        assert isinstance(myth_dict, dict)
        assert myth_dict["creator_id"] == "agent123"
        assert myth_dict["title"] == "Test Myth"
        assert myth_dict["theme"] == "test"
        assert myth_dict["popularity"] == 1.0


class TestNorm:
    """Test cases for Norm."""

    def test_norm_creation(self):
        """Test norm creation."""
        norm = Norm(
            proposer_id="agent123",
            title="Share Resources",
            description="Agents should share resources fairly",
            norm_type="cooperation",
            tick_proposed=15,
        )

        assert norm.proposer_id == "agent123"
        assert norm.title == "Share Resources"
        assert norm.description == "Agents should share resources fairly"
        assert norm.norm_type == "cooperation"
        assert norm.tick_proposed == 15
        assert norm.status == "proposed"
        assert norm.votes_for == 0
        assert norm.votes_against == 0

    def test_norm_serialization(self):
        """Test norm serialization to dictionary."""
        norm = Norm(
            proposer_id="agent123",
            title="Test Norm",
            description="Test description",
            norm_type="test",
        )

        norm_dict = norm.to_dict()

        assert isinstance(norm_dict, dict)
        assert norm_dict["proposer_id"] == "agent123"
        assert norm_dict["title"] == "Test Norm"
        assert norm_dict["norm_type"] == "test"
        assert norm_dict["status"] == "proposed"


class TestSlang:
    """Test cases for Slang."""

    def test_slang_creation(self):
        """Test slang creation."""
        slang = Slang(
            creator_id="agent123",
            word="novato",
            meaning="to innovate in a new way",
            usage_context="general",
            tick_created=20,
        )

        assert slang.creator_id == "agent123"
        assert slang.word == "novato"
        assert slang.meaning == "to innovate in a new way"
        assert slang.usage_context == "general"
        assert slang.tick_created == 20
        assert slang.popularity == 1.0
        assert slang.adoption_rate == 0.0

    def test_slang_serialization(self):
        """Test slang serialization to dictionary."""
        slang = Slang(creator_id="agent123", word="testword", meaning="test meaning")

        slang_dict = slang.to_dict()

        assert isinstance(slang_dict, dict)
        assert slang_dict["creator_id"] == "agent123"
        assert slang_dict["word"] == "testword"
        assert slang_dict["meaning"] == "test meaning"


class TestLanguage:
    """Test cases for Language."""

    @pytest.fixture
    def language(self):
        """Create a test language."""
        return Language(agent_id="agent123")

    def test_language_creation(self, language):
        """Test language creation."""
        assert language.agent_id == "agent123"
        assert language.vocabulary == {}
        assert language.shared_vocabulary == {}
        assert language.communication_style == "neutral"
        assert language.creativity_level == 0.5

    def test_language_slang_addition(self, language):
        """Test adding slang to language."""
        slang = Slang(creator_id="agent123", word="testword", meaning="test meaning")

        language.add_slang(slang)

        assert "testword" in language.vocabulary
        assert language.vocabulary["testword"] == slang

    def test_language_slang_adoption(self, language):
        """Test adopting slang from other agents."""
        language.adopt_slang("borrowed_word", "borrowed meaning", 0.3)

        assert "borrowed_word" in language.shared_vocabulary
        assert language.shared_vocabulary["borrowed_word"] == 0.3

    def test_language_shared_words(self, language):
        """Test getting shared words above threshold."""
        language.shared_vocabulary = {"word1": 0.5, "word2": 0.2, "word3": 0.8}

        shared_words = language.get_shared_words(threshold=0.3)

        assert "word1" in shared_words
        assert "word3" in shared_words
        assert "word2" not in shared_words

    def test_language_divergence(self):
        """Test language divergence calculation."""
        lang1 = Language(agent_id="agent1")
        lang2 = Language(agent_id="agent2")

        # Same vocabulary should have 0 divergence
        lang1.shared_vocabulary = {"word1": 0.5, "word2": 0.5}
        lang2.shared_vocabulary = {"word1": 0.5, "word2": 0.5}

        divergence = lang1.calculate_divergence(lang2)
        assert divergence == 0.0

        # Different vocabulary should have > 0 divergence
        lang2.shared_vocabulary = {"word1": 1.0, "word2": 0.0}

        divergence = lang1.calculate_divergence(lang2)
        assert divergence > 0.0


class TestCulture:
    """Test cases for Culture."""

    @pytest.fixture
    def culture(self):
        """Create a test culture."""
        return Culture()

    @pytest.fixture
    def agents(self):
        """Create test agents."""
        agents = []
        for i in range(3):
            agent = Agent(name=f"Agent{i}", personality=AgentPersonality.random(seed=i))
            agents.append(agent)
        return agents

    def test_culture_initialization(self, culture):
        """Test culture initialization."""
        assert culture.myths == {}
        assert culture.active_norms == {}
        assert culture.proposed_norms == {}
        assert culture.slang_registry == {}
        assert culture.cultural_events == []

    def test_myth_addition(self, culture):
        """Test adding myths to culture."""
        myth = Myth(creator_id="agent123", title="Test Myth", content="Test content", theme="test")

        culture.add_myth(myth)

        assert myth.id in culture.myths
        assert culture.myths[myth.id] == myth

        # Should record cultural event
        assert len(culture.cultural_events) == 1
        event = culture.cultural_events[0]
        assert event["type"] == "myth_created"
        assert event["agent_id"] == "agent123"

    def test_myth_canonization(self, culture):
        """Test myth canonization based on popularity."""
        # Create myths with different popularity
        myth1 = Myth(creator_id="agent1", title="Popular Myth", popularity=0.8, tick_created=10)

        myth2 = Myth(creator_id="agent2", title="Unpopular Myth", popularity=0.2, tick_created=11)

        culture.add_myth(myth1)
        culture.add_myth(myth2)

        # Canonize myths
        culture.canonize_myths(tick=20)

        # Popular myth should gain influence
        assert myth1.influence > 1.0
        # Unpopular myth should lose influence
        assert myth2.influence < 1.0

    def test_norm_proposal(self, culture):
        """Test norm proposal."""
        norm = Norm(
            proposer_id="agent123",
            title="Test Norm",
            description="Test description",
            norm_type="cooperation",
        )

        culture.propose_norm(norm, "agent123")

        assert norm.id in culture.proposed_norms
        assert culture.proposed_norms[norm.id] == norm

        # Should record cultural event
        assert len(culture.cultural_events) == 1
        event = culture.cultural_events[0]
        assert event["type"] == "norm_proposed"
        assert event["agent_id"] == "agent123"

    def test_norm_voting(self, culture):
        """Test norm voting."""
        norm = Norm(
            proposer_id="agent123",
            title="Test Norm",
            description="Test description",
            norm_type="cooperation",
        )

        culture.propose_norm(norm, "agent123")

        # Vote on norm
        culture.vote_on_norm(norm.id, "voter1", True)
        culture.vote_on_norm(norm.id, "voter2", True)
        culture.vote_on_norm(norm.id, "voter3", False)

        assert norm.votes_for == 2
        assert norm.votes_against == 1

        # With 67% approval, should be activated
        assert norm.status == "active"
        assert norm.id in culture.active_norms

    def test_norm_enforcement(self, culture, agents):
        """Test norm enforcement."""
        norm = Norm(
            proposer_id="agent123",
            title="Cooperation Norm",
            description="Agents should cooperate",
            norm_type="cooperation",
            status="active",
        )

        culture.active_norms[norm.id] = norm

        # Mock random to control compliance
        with patch("random.random", return_value=0.3):  # 30% chance
            culture.enforce_norms(agents, tick=10)

        # Check that compliance rate was calculated
        assert 0 <= norm.compliance_rate <= 1
        assert norm.violations >= 0

    def test_language_evolution(self, culture, agents):
        """Test language evolution through slang creation and diffusion."""
        # Mock random to ensure slang creation
        with patch("random.random", return_value=0.04):  # 5% chance
            culture.evolve_language(agents, tick=10)

        # Some slang should be created
        assert len(culture.slang_registry) > 0

        # Check slang properties
        for slang in culture.slang_registry.values():
            assert slang.creator_id in [agent.id for agent in agents]
            assert slang.word is not None
            assert slang.meaning is not None

    def test_myth_templates(self, culture):
        """Test myth template generation."""
        templates = culture.generate_myth_templates()

        assert isinstance(templates, list)
        assert len(templates) > 0

        for template in templates:
            assert "theme" in template
            assert "title_template" in template
            assert "content_template" in template
            # Every template must provide at least one list of substitution options
            assert any(isinstance(v, list) and v for v in template.values())

    def test_myth_from_template(self, culture):
        """Test creating myth from template."""
        template = {
            "theme": "creation",
            "title_template": "The Birth of {entity}",
            "content_template": "In the beginning, there was {concept}...",
            "entities": ["the First One"],
            "concepts": ["light"],
        }

        myth = culture.create_myth_from_template(template, "agent123", tick=10)

        assert isinstance(myth, Myth)
        assert myth.creator_id == "agent123"
        assert myth.theme == "creation"
        assert myth.tick_created == 10
        assert myth.title is not None
        assert myth.content is not None

    def test_cultural_summary(self, culture):
        """Test cultural summary generation."""
        # Add some cultural content
        myth = Myth(creator_id="agent1", title="Test Myth", theme="test")
        culture.add_myth(myth)

        norm = Norm(proposer_id="agent2", title="Test Norm", norm_type="test")
        culture.propose_norm(norm, "agent2")

        slang = Slang(creator_id="agent3", word="test", meaning="test")
        culture.slang_registry[slang.id] = slang

        summary = culture.get_cultural_summary()

        assert "myths_count" in summary
        assert "active_norms_count" in summary
        assert "proposed_norms_count" in summary
        assert "slang_count" in summary
        assert "recent_events" in summary
        assert "top_myths" in summary
        assert "active_norms" in summary
        assert "popular_slang" in summary

        assert summary["myths_count"] == 1
        assert summary["proposed_norms_count"] == 1
        assert summary["slang_count"] == 1


class TestCulturalEvolution:
    """Test cases for cultural evolution mechanics."""

    @pytest.fixture
    def culture_with_content(self):
        """Create culture with existing content."""
        culture = Culture()

        # Add myths
        for i in range(3):
            myth = Myth(
                creator_id=f"agent{i}",
                title=f"Myth {i}",
                theme=f"theme{i}",
                popularity=0.5 + i * 0.2,
            )
            culture.add_myth(myth)

        # Add norms (propose to record cultural events, then activate)
        for i in range(2):
            norm = Norm(
                proposer_id=f"agent{i}", title=f"Norm {i}", norm_type=f"type{i}", status="active"
            )
            culture.propose_norm(norm, f"agent{i}")
            culture.proposed_norms.pop(norm.id, None)
            culture.active_norms[norm.id] = norm

        # Add slang
        for i in range(5):
            slang = Slang(
                creator_id=f"agent{i}",
                word=f"word{i}",
                meaning=f"meaning {i}",
                popularity=0.3 + i * 0.1,
            )
            culture.slang_registry[slang.id] = slang

        return culture

    def test_cultural_diversity(self, culture_with_content):
        """Test cultural diversity metrics."""
        summary = culture_with_content.get_cultural_summary()

        assert summary["myths_count"] == 3
        assert summary["active_norms_count"] == 2
        assert summary["slang_count"] == 5

        # Top myths should be sorted by popularity
        top_myths = summary["top_myths"]
        if len(top_myths) > 1:
            for i in range(len(top_myths) - 1):
                assert top_myths[i]["popularity"] >= top_myths[i + 1]["popularity"]

    def test_cultural_events_tracking(self, culture_with_content):
        """Test cultural events tracking."""
        events = culture_with_content.cultural_events

        # Should have events for each myth added
        myth_events = [e for e in events if e["type"] == "myth_created"]
        assert len(myth_events) == 3

        # Should have events for each norm proposed
        norm_events = [e for e in events if e["type"] == "norm_proposed"]
        assert len(norm_events) == 2

    def test_language_drift_simulation(self):
        """Test language drift simulation."""
        import random

        random.seed(42)  # deterministic slang generation
        culture = Culture()
        agents = [Agent(name=f"Agent{i}") for i in range(5)]

        # Simulate multiple ticks of language evolution
        for tick in range(10, 20):
            culture.evolve_language(agents, tick)

        # Should have generated some slang
        assert len(culture.slang_registry) > 0

        # Check slang diversity
        unique_words = set(slang.word for slang in culture.slang_registry.values())
        assert len(unique_words) > 0

        # Check adoption rates
        for slang in culture.slang_registry.values():
            assert 0 <= slang.adoption_rate <= 1


if __name__ == "__main__":
    pytest.main([__file__])
