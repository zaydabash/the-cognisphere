"""
LLM adapter for deterministic mock mode and OpenAI integration.

Provides a unified interface for language model interactions with both
deterministic mock responses for scalable simulation and real OpenAI API calls.
"""

import asyncio
import hashlib
import json
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp


class LLMMode(Enum):
    """LLM operation modes."""

    MOCK = "mock"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMResponse:
    """Response from LLM adapter."""

    content: str
    tokens_used: int
    model: str
    response_time: float
    seed_used: Optional[int] = None


@dataclass
class LLMConfig:
    """Configuration for LLM adapter."""

    mode: LLMMode = LLMMode.MOCK
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.3
    max_tokens: int = 1000
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30


class LLMAdapter(ABC):
    """Abstract base class for LLM adapters."""

    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from LLM."""
        pass

    @abstractmethod
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[LLMResponse]:
        """Generate responses for multiple prompts."""
        pass


class MockLLMAdapter(LLMAdapter):
    """Deterministic mock LLM adapter for scalable simulation."""

    def __init__(self, config: LLMConfig, seed: Optional[int] = None):
        self.config = config
        self.seed = seed
        self.response_templates = self._load_response_templates()
        self.conversation_history: Dict[str, List[Dict]] = {}

    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load deterministic response templates for different prompt types."""
        return {
            "trade_negotiation": [
                "I propose we exchange {resource1} for {resource2} in equal amounts.",
                "Let me offer you {amount1} {resource1} for {amount2} {resource2}.",
                "I'm willing to trade my {resource1} for your {resource2}.",
                "How about we make a fair exchange of resources?",
                "I need {resource1} and can offer you {resource2} in return.",
            ],
            "myth_creation": [
                "Long ago, when the world was young, there lived {character} who {action}.",
                "In the ancient times, {character} discovered {discovery} and shared it with all.",
                "The legend tells of {character} who {heroic_deed} and brought {benefit} to the people.",
                "Once upon a time, {character} faced {challenge} and through {virtue} overcame it.",
                "The story goes that {character} found {treasure} and used it to {noble_purpose}.",
            ],
            "norm_proposal": [
                "I propose that we should {action} because it will {benefit}.",
                "Let us establish a rule that {rule} to ensure {outcome}.",
                "I suggest we adopt the practice of {practice} for the good of all.",
                "We should create a norm that {norm} to maintain {value}.",
                "I recommend we follow {guideline} to promote {positive_outcome}.",
            ],
            "slang_creation": [
                "Let's call {concept} '{word}' - it sounds {quality}.",
                "I think we should use '{word}' to mean {meaning}.",
                "How about '{word}' for when we {action}?",
                "Let me introduce '{word}' - it means {meaning} in our new way.",
                "We could say '{word}' instead of {old_word} to be {quality}.",
            ],
            "reflection": [
                "I've been thinking about {topic} and I realize {insight}.",
                "Looking back on recent events, I notice {pattern}.",
                "I've learned that {lesson} through {experience}.",
                "My thoughts on {topic} have evolved - now I believe {belief}.",
                "I've come to understand {understanding} about {subject}.",
            ],
            "general": [
                "That's an interesting perspective on {topic}.",
                "I see what you mean about {concept}.",
                "Let me share my thoughts on {subject}.",
                "I have some ideas about {topic}.",
                "What do you think about {concept}?",
            ],
        }

    def _get_deterministic_seed(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> int:
        """Generate deterministic seed from prompt and context."""
        # Create hash from prompt and context
        content = prompt
        if context:
            content += json.dumps(context, sort_keys=True)

        hash_obj = hashlib.md5(content.encode())
        hash_int = int(hash_obj.hexdigest()[:8], 16)

        # Use base seed if provided
        if self.seed is not None:
            hash_int = (hash_int + self.seed) % (2**32)

        return hash_int

    def _extract_prompt_type(self, prompt: str) -> str:
        """Extract prompt type from prompt content."""
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ["trade", "exchange", "negotiate", "offer"]):
            return "trade_negotiation"
        elif any(word in prompt_lower for word in ["myth", "story", "legend", "tale"]):
            return "myth_creation"
        elif any(word in prompt_lower for word in ["norm", "rule", "propose", "suggest"]):
            return "norm_proposal"
        elif any(word in prompt_lower for word in ["slang", "word", "term", "language"]):
            return "slang_creation"
        elif any(word in prompt_lower for word in ["reflect", "think", "learn", "realize"]):
            return "reflection"
        else:
            return "general"

    def _generate_deterministic_response(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate deterministic response based on prompt."""
        # Set random seed for deterministic generation
        seed = self._get_deterministic_seed(prompt, context)
        random.seed(seed)

        # Get prompt type
        prompt_type = self._extract_prompt_type(prompt)
        templates = self.response_templates.get(prompt_type, self.response_templates["general"])

        # Select template
        template = random.choice(templates)

        # Fill in template variables
        response = self._fill_template(template, context or {})

        return response

    def _fill_template(self, template: str, context: Dict[str, Any]) -> str:
        """Fill template variables with context data."""
        # Default values for template variables
        defaults = {
            "character": random.choice(
                ["the Wise One", "the Brave One", "the Ancient Spirit", "the First Creator"]
            ),
            "action": random.choice(
                [
                    "discovered great wisdom",
                    "brought peace to the land",
                    "taught the people",
                    "created harmony",
                ]
            ),
            "discovery": random.choice(
                [
                    "the secret of cooperation",
                    "the power of unity",
                    "the way of balance",
                    "the art of understanding",
                ]
            ),
            "heroic_deed": random.choice(
                [
                    "faced the great challenge",
                    "saved the people",
                    "brought light to darkness",
                    "united the tribes",
                ]
            ),
            "benefit": random.choice(["prosperity", "peace", "wisdom", "harmony"]),
            "challenge": random.choice(
                ["terrible danger", "great darkness", "ancient curse", "mighty foe"]
            ),
            "virtue": random.choice(["courage", "wisdom", "compassion", "determination"]),
            "treasure": random.choice(
                ["ancient knowledge", "sacred wisdom", "divine power", "eternal truth"]
            ),
            "noble_purpose": random.choice(
                ["help others", "protect the innocent", "spread wisdom", "create peace"]
            ),
            "resource1": random.choice(["food", "energy", "artifacts"]),
            "resource2": random.choice(["energy", "artifacts", "influence"]),
            "amount1": str(random.randint(5, 20)),
            "amount2": str(random.randint(5, 20)),
            "word": self._generate_slang_word(),
            "meaning": random.choice(
                [
                    "to work together",
                    "to share wisdom",
                    "to create something new",
                    "to understand deeply",
                ]
            ),
            "concept": random.choice(["cooperation", "innovation", "wisdom", "harmony"]),
            "quality": random.choice(["unique", "powerful", "meaningful", "inspiring"]),
            "action_type": random.choice(["cooperate", "innovate", "share", "understand"]),
            "old_word": random.choice(["work", "think", "create", "help"]),
            "topic": random.choice(["our society", "cooperation", "innovation", "the future"]),
            "insight": random.choice(
                [
                    "we are stronger together",
                    "sharing brings prosperity",
                    "innovation drives progress",
                    "understanding creates harmony",
                ]
            ),
            "pattern": random.choice(
                [
                    "cooperation leads to success",
                    "innovation spreads quickly",
                    "trust builds over time",
                    "diversity brings strength",
                ]
            ),
            "lesson": random.choice(
                [
                    "the importance of cooperation",
                    "the value of innovation",
                    "the power of trust",
                    "the beauty of diversity",
                ]
            ),
            "experience": random.choice(
                [
                    "recent interactions",
                    "trading with others",
                    "creating new ideas",
                    "working together",
                ]
            ),
            "belief": random.choice(
                [
                    "we should cooperate more",
                    "innovation is essential",
                    "trust is fundamental",
                    "diversity is valuable",
                ]
            ),
            "understanding": random.choice(
                [
                    "the nature of cooperation",
                    "how innovation works",
                    "why trust matters",
                    "the value of diversity",
                ]
            ),
            "subject": random.choice(["society", "cooperation", "innovation", "relationships"]),
            "rule": random.choice(
                [
                    "share resources fairly",
                    "respect each other",
                    "innovate together",
                    "cooperate always",
                ]
            ),
            "outcome": random.choice(["prosperity", "harmony", "progress", "peace"]),
            "practice": random.choice(["sharing", "cooperation", "innovation", "respect"]),
            "norm": random.choice(
                [
                    "helping others",
                    "sharing knowledge",
                    "working together",
                    "respecting differences",
                ]
            ),
            "value": random.choice(["fairness", "cooperation", "innovation", "respect"]),
            "guideline": random.choice(
                ["the golden rule", "mutual respect", "shared prosperity", "common good"]
            ),
            "positive_outcome": random.choice(
                ["better society", "stronger community", "more innovation", "greater harmony"]
            ),
        }

        # Fill template
        try:
            response = template.format(**{**defaults, **context})
        except KeyError:
            # If template has variables not in context, use defaults
            response = template.format(**defaults)

        return response

    def _generate_slang_word(self) -> str:
        """Generate a random slang word."""
        prefixes = ["novo", "flex", "sync", "flux", "nex", "vex", "zap", "bop", "top", "hop"]
        suffixes = ["ate", "ize", "ify", "oso", "ico", "ado", "ito", "ura", "ela", "ola"]

        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)

        return prefix + suffix

    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate deterministic mock response."""
        import time

        start_time = time.time()

        # Extract context from kwargs
        context = {
            k: v for k, v in kwargs.items() if k in ["agent_id", "tick", "resources", "personality"]
        }

        # Generate response
        content = self._generate_deterministic_response(prompt, context)

        # Simulate response time
        await asyncio.sleep(random.uniform(0.01, 0.05))  # 10-50ms

        response_time = time.time() - start_time

        return LLMResponse(
            content=content,
            tokens_used=len(content.split()),
            model="mock-llm",
            response_time=response_time,
            seed_used=self._get_deterministic_seed(prompt, context),
        )

    async def generate_batch(self, prompts: List[str], **kwargs) -> List[LLMResponse]:
        """Generate responses for multiple prompts."""
        tasks = [self.generate_response(prompt, **kwargs) for prompt in prompts]
        return await asyncio.gather(*tasks)

    def set_seed(self, seed: int):
        """Set random seed for deterministic generation."""
        self.seed = seed


class OpenAIAdapter(LLMAdapter):
    """OpenAI API adapter for real LLM interactions."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response using OpenAI API."""
        import time

        start_time = time.time()

        session = await self._get_session()

        # Prepare request
        url = f"{self.config.base_url or 'https://api.openai.com/v1'}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        try:
            async with session.post(
                url,
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    tokens_used = result["usage"]["total_tokens"]
                else:
                    content = f"Error: {response.status}"
                    tokens_used = 0
        except Exception as e:
            content = f"Error: {str(e)}"
            tokens_used = 0

        response_time = time.time() - start_time

        return LLMResponse(
            content=content,
            tokens_used=tokens_used,
            model=self.config.model,
            response_time=response_time,
        )

    async def generate_batch(self, prompts: List[str], **kwargs) -> List[LLMResponse]:
        """Generate responses for multiple prompts."""
        tasks = [self.generate_response(prompt, **kwargs) for prompt in prompts]
        return await asyncio.gather(*tasks)

    async def close(self):
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()


class LLMAdapterFactory:
    """Factory for creating LLM adapters."""

    @staticmethod
    def create_adapter(config: LLMConfig, seed: Optional[int] = None) -> LLMAdapter:
        """Create LLM adapter based on configuration."""
        if config.mode == LLMMode.MOCK:
            return MockLLMAdapter(config, seed)
        elif config.mode == LLMMode.OPENAI:
            return OpenAIAdapter(config)
        else:
            raise ValueError(f"Unsupported LLM mode: {config.mode}")


# Convenience functions
async def generate_agent_response(
    prompt: str, agent_id: str, tick: int, llm_adapter: LLMAdapter, **kwargs
) -> str:
    """Generate response for an agent using LLM adapter."""
    response = await llm_adapter.generate_response(prompt, agent_id=agent_id, tick=tick, **kwargs)
    return response.content


async def generate_batch_responses(
    prompts: List[str], llm_adapter: LLMAdapter, **kwargs
) -> List[str]:
    """Generate batch responses using LLM adapter."""
    responses = await llm_adapter.generate_batch(prompts, **kwargs)
    return [response.content for response in responses]
