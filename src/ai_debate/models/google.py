"""Google (Gemini) model adapter using the new Google GenAI SDK."""

import os
from dataclasses import dataclass, field

from google import genai
from google.genai import types

from ai_debate.models.base import Message, ModelResponse, Role


@dataclass
class GoogleModel:
    """Adapter for Google Gemini models."""

    model_id: str = "gemini-3-pro-preview"
    name: str = "Gemini 3 Pro"
    provider: str = "Google"
    temperature: float = 0.7
    _client: genai.Client = field(init=False, repr=False)

    def __post_init__(self) -> None:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        self._client = genai.Client(api_key=api_key)

    async def generate(
        self,
        system_prompt: str,
        messages: list[Message],
        max_tokens: int = 4096,
    ) -> ModelResponse:
        """Generate a response using Gemini.

        Args:
            system_prompt: System instructions for Gemini.
            messages: Conversation history.
            max_tokens: Maximum tokens to generate.

        Returns:
            ModelResponse with generated content and usage stats.
        """
        # Build the user content from messages
        user_content = ""
        for msg in messages:
            if msg.role == Role.USER:
                user_content += msg.content

        # Use the new GenAI SDK
        response = await self._client.aio.models.generate_content(
            model=self.model_id,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=max_tokens,
                temperature=self.temperature,
            ),
        )

        # Extract usage metadata
        usage = response.usage_metadata
        input_tokens = usage.prompt_token_count if usage else 0
        output_tokens = usage.candidates_token_count if usage else 0

        return ModelResponse(
            content=response.text or "",
            model=self.model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            metadata={
                "finish_reason": response.candidates[0].finish_reason
                if response.candidates
                else None,
            },
        )
