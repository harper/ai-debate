"""Base types and protocol for AI model adapters."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, runtime_checkable


class Role(str, Enum):
    """Message role in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """A single message in a conversation."""

    role: Role
    content: str


@dataclass
class ModelResponse:
    """Response from a model generation request."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    metadata: dict[str, object] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        """Total tokens used in the request."""
        return self.input_tokens + self.output_tokens


@runtime_checkable
class DebateModel(Protocol):
    """Protocol for AI model adapters used in debates.

    All model implementations must satisfy this interface to be used
    in the debate engine.
    """

    @property
    def name(self) -> str:
        """Human-readable name for this model (e.g., 'Claude Opus 4.5')."""
        ...

    @property
    def model_id(self) -> str:
        """API model identifier (e.g., 'claude-opus-4-5-20251124')."""
        ...

    @property
    def provider(self) -> str:
        """Provider name (e.g., 'Anthropic', 'OpenAI')."""
        ...

    async def generate(
        self,
        system_prompt: str,
        messages: list[Message],
        max_tokens: int = 4096,
    ) -> ModelResponse:
        """Generate a response from the model.

        Args:
            system_prompt: System instructions for the model.
            messages: Conversation history.
            max_tokens: Maximum tokens to generate.

        Returns:
            ModelResponse with generated content and usage stats.
        """
        ...


@dataclass
class ModelConfig:
    """Configuration for instantiating a model."""

    provider: str
    model_id: str
    name: str
    api_key_env: str  # Environment variable name for API key
    temperature: float = 0.7
    max_retries: int = 3
