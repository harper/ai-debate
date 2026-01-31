"""xAI (Grok) model adapter.

xAI's API is compatible with the OpenAI SDK, so we use it with a custom base URL.
"""

import os
from dataclasses import dataclass, field

import openai

from ai_debate.models.base import Message, ModelResponse, Role


@dataclass
class XAIModel:
    """Adapter for xAI Grok models.

    Uses the OpenAI SDK with xAI's API endpoint, as xAI's API is
    fully compatible with the OpenAI API format.
    """

    model_id: str = "grok-4"
    name: str = "Grok 4"
    provider: str = "xAI"
    temperature: float = 0.7
    base_url: str = "https://api.x.ai/v1"
    _client: openai.AsyncOpenAI = field(init=False, repr=False)

    def __post_init__(self) -> None:
        api_key = os.environ.get("XAI_API_KEY")
        if not api_key:
            raise ValueError("XAI_API_KEY environment variable not set")
        self._client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=self.base_url,
        )

    async def generate(
        self,
        system_prompt: str,
        messages: list[Message],
        max_tokens: int = 4096,
    ) -> ModelResponse:
        """Generate a response using Grok.

        Args:
            system_prompt: System instructions for Grok.
            messages: Conversation history.
            max_tokens: Maximum tokens to generate.

        Returns:
            ModelResponse with generated content and usage stats.
        """
        # Build messages list with system prompt first (OpenAI format)
        xai_messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

        # Add conversation messages
        for msg in messages:
            xai_messages.append({
                "role": self._convert_role(msg.role),
                "content": msg.content,
            })

        response = await self._client.chat.completions.create(
            model=self.model_id,
            messages=xai_messages,
            max_tokens=max_tokens,
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
        """Convert Role enum to xAI/OpenAI role string."""
        return role.value
