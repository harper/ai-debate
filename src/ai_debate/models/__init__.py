"""Model adapters for different AI providers."""

from ai_debate.models.anthropic import AnthropicModel
from ai_debate.models.base import (
    DebateModel,
    Message,
    ModelConfig,
    ModelResponse,
    Role,
)
from ai_debate.models.google import GoogleModel
from ai_debate.models.openai import OpenAIModel
from ai_debate.models.xai import XAIModel

__all__ = [
    "AnthropicModel",
    "DebateModel",
    "GoogleModel",
    "Message",
    "ModelConfig",
    "ModelResponse",
    "OpenAIModel",
    "Role",
    "XAIModel",
]
