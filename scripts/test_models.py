#!/usr/bin/env python3
"""Test each model adapter to verify API keys are working."""

import asyncio
import sys

from dotenv import load_dotenv
load_dotenv()

from ai_debate.models import AnthropicModel, OpenAIModel, GoogleModel, XAIModel
from ai_debate.models.base import Message, Role


async def test_model(name: str, model_class: type) -> bool:
    """Test a single model adapter."""
    print(f"\nTesting {name}...")

    try:
        model = model_class()
        print(f"  Model: {model.name} ({model.model_id})")
    except ValueError as e:
        print(f"  ✗ Failed to initialize: {e}")
        return False

    try:
        response = await model.generate(
            system_prompt="You are a helpful assistant. Be very brief.",
            messages=[Message(role=Role.USER, content="Say hello in exactly 5 words.")],
            max_tokens=50
        )
        print(f"  ✓ Response: {response.content.strip()}")
        print(f"  ✓ Tokens: {response.input_tokens} in, {response.output_tokens} out")
        return True
    except Exception as e:
        print(f"  ✗ API call failed: {e}")
        return False


async def main() -> None:
    """Test all configured model adapters."""
    models = [
        ("Anthropic (Claude)", AnthropicModel),
        ("OpenAI (GPT)", OpenAIModel),
        ("Google (Gemini)", GoogleModel),
        ("xAI (Grok)", XAIModel),
    ]

    results = {}

    for name, model_class in models:
        results[name] = await test_model(name, model_class)

    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {name}")

    print(f"\n{passed}/{total} models working")

    if passed < 2:
        print("\n⚠ Need at least 2 working models to run a debate")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
