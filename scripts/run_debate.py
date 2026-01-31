#!/usr/bin/env python3
"""Run a test debate between two AI models."""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from ai_debate.debate import DebateEngine, transcript_to_markdown
from ai_debate.models import AnthropicModel, OpenAIModel


async def main() -> None:
    """Run a debate between Claude and GPT."""
    # Default resolution
    resolution = (
        "Resolved: AI regulation should be handled at the federal level, "
        "preempting state laws like the Colorado AI Act"
    )

    # Allow custom resolution from command line
    if len(sys.argv) > 1:
        resolution = " ".join(sys.argv[1:])

    print("Initializing models...")

    try:
        affirmative = AnthropicModel()
        print(f"  Affirmative: {affirmative.name} ({affirmative.model_id})")
    except ValueError as e:
        print(f"  Error initializing Claude: {e}")
        print("  Set ANTHROPIC_API_KEY environment variable")
        return

    try:
        negative = OpenAIModel()
        print(f"  Negative: {negative.name} ({negative.model_id})")
    except ValueError as e:
        print(f"  Error initializing GPT: {e}")
        print("  Set OPENAI_API_KEY environment variable")
        return

    # Create engine and run debate
    engine = DebateEngine(verbose=True)
    transcript = await engine.run_debate(
        resolution=resolution,
        affirmative=affirmative,
        negative=negative,
    )

    # Save transcript as markdown
    output_dir = Path("debates")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"debate-{transcript.id}.md"
    markdown = transcript_to_markdown(transcript)
    output_file.write_text(markdown)

    print(f"\nTranscript saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
