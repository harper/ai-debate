#!/usr/bin/env python3
"""Run a test debate between two AI models."""

import argparse
import asyncio
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from ai_debate.debate import DebateEngine, transcript_to_markdown
from ai_debate.models import AnthropicModel, OpenAIModel


async def main() -> None:
    """Run a debate between Claude and GPT."""
    parser = argparse.ArgumentParser(description="Run an AI debate")
    parser.add_argument(
        "resolution",
        nargs="?",
        default=(
            "Resolved: AI regulation should be handled at the federal level, "
            "preempting state laws like the Colorado AI Act"
        ),
        help="The debate resolution/topic",
    )
    parser.add_argument(
        "--swap",
        action="store_true",
        help="Swap roles: GPT argues affirmative, Claude argues negative",
    )
    args = parser.parse_args()

    print("Initializing models...")

    try:
        claude = AnthropicModel()
        print(f"  Claude: {claude.name} ({claude.model_id})")
    except ValueError as e:
        print(f"  Error initializing Claude: {e}")
        print("  Set ANTHROPIC_API_KEY environment variable")
        return

    try:
        gpt = OpenAIModel()
        print(f"  GPT: {gpt.name} ({gpt.model_id})")
    except ValueError as e:
        print(f"  Error initializing GPT: {e}")
        print("  Set OPENAI_API_KEY environment variable")
        return

    # Assign roles based on --swap flag
    if args.swap:
        affirmative = gpt
        negative = claude
    else:
        affirmative = claude
        negative = gpt

    print(f"\n  Affirmative: {affirmative.name}")
    print(f"  Negative: {negative.name}")

    # Create engine and run debate
    engine = DebateEngine(verbose=True)
    transcript = await engine.run_debate(
        resolution=args.resolution,
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
