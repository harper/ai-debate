"""Anthropic (Claude) model adapter."""

import os
from dataclasses import dataclass, field

import anthropic

from ai_debate.models.base import Message, ModelResponse, Role


@dataclass
class AnthropicModel:
    """Adapter for Anthropic Claude models."""

    model_id: str = "claude-opus-4-5-20251124"
    name: str = "Claude Opus 4.5"
    provider: str = "Anthropic"
    temperature: float = 0.7
    _client: anthropic.AsyncAnthropic = field(init=False, repr=False)

    def __post_init__(self) -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        system_prompt: str,
        messages: list[Message],
        max_tokens: int = 4096,
    ) -> ModelResponse:
        """Generate a response using Claude.

        Args:
            system_prompt: System instructions for Claude.
            messages: Conversation history.
            max_tokens: Maximum tokens to generate.

        Returns:
            ModelResponse with generated content and usage stats.
        """
        # Convert messages to Anthropic format
        anthropic_messages = [
            {"role": self._convert_role(msg.role), "content": msg.content}
            for msg in messages
        ]

        response = await self._client.messages.create(
            model=self.model_id,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=anthropic_messages,
            temperature=self.temperature,
        )

        # Extract text content
        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        return ModelResponse(
            content=content,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            metadata={
                "stop_reason": response.stop_reason,
            },
        )

    def _convert_role(self, role: Role) -> str:
        """Convert Role enum to Anthropic role string."""
        if role == Role.ASSISTANT:
            return "assistant"
        # Anthropic uses "user" for both user and system in messages
        return "user"
