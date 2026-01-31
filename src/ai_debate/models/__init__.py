"""Model adapters for different AI providers."""

from ai_debate.models.anthropic import AnthropicModel
from ai_debate.models.base import (
    DebateModel,
    Message,
    ModelConfig,
    ModelResponse,
    Role,
)
from ai_debate.models.openai import OpenAIModel

__all__ = [
    "AnthropicModel",
    "DebateModel",
    "Message",
    "ModelConfig",
    "ModelResponse",
    "OpenAIModel",
    "Role",
]
