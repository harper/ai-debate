"""OpenAI (GPT) model adapter."""

import os
from dataclasses import dataclass, field

import openai

from ai_debate.models.base import Message, ModelResponse, Role


@dataclass
class OpenAIModel:
    """Adapter for OpenAI GPT models."""

    model_id: str = "gpt-5.2"
    name: str = "GPT-5.2"
    provider: str = "OpenAI"
    temperature: float = 0.7
    _client: openai.AsyncOpenAI = field(init=False, repr=False)

    def __post_init__(self) -> None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self._client = openai.AsyncOpenAI(api_key=api_key)

    async def generate(
        self,
        system_prompt: str,
        messages: list[Message],
        max_tokens: int = 4096,
    ) -> ModelResponse:
        """Generate a response using GPT.

        Args:
            system_prompt: System instructions for GPT.
            messages: Conversation history.
            max_tokens: Maximum tokens to generate.

        Returns:
            ModelResponse with generated content and usage stats.
        """
        # Build messages list with system prompt first
        openai_messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

        # Add conversation messages
        for msg in messages:
            openai_messages.append({
                "role": self._convert_role(msg.role),
                "content": msg.content,
            })

        response = await self._client.chat.completions.create(
            model=self.model_id,
            messages=openai_messages,
            max_completion_tokens=max_tokens,
            temperature=self.temperature,
        )

        # Extract content from response
        content = response.choices[0].message.content or ""

        # Get usage stats
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        return ModelResponse(
            content=content,
            model=response.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
            },
        )

    def _convert_role(self, role: Role) -> str:
        """Convert Role enum to OpenAI role string."""
        return role.value  # OpenAI uses same role names
