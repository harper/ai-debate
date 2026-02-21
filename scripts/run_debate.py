#!/usr/bin/env python3
"""Run a test debate between two AI models."""

import argparse
import asyncio
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from ai_debate.debate import DebateEngine, transcript_to_markdown
from ai_debate.models import AnthropicModel, GoogleModel, OpenAIModel, XAIModel

MODEL_MAP = {
    "claude": AnthropicModel,
    "gpt": OpenAIModel,
    "gemini": GoogleModel,
    "grok": XAIModel,
}


def init_model(key: str):
    """Initialize a model by its short name."""
    if key not in MODEL_MAP:
        raise ValueError(f"Unknown model: {key!r}. Choose from: {', '.join(MODEL_MAP)}")
    return MODEL_MAP[key]()


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
    parser.add_argument(
        "--judge",
        action="store_true",
        help="Run judging after the debate completes",
    )
    parser.add_argument(
        "--judge-models",
        type=str,
        default=None,
        help="Comma-separated judge model names (e.g. 'gemini,grok'). "
             "Defaults to the 2 models not debating.",
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

    # Judging
    if args.judge:
        from ai_debate.judging import JudgePanel
        from ai_debate.judging.judge import result_to_markdown

        # Determine judge models
        if args.judge_models:
            judge_keys = [k.strip() for k in args.judge_models.split(",")]
        else:
            # Default: the 2 models not debating
            debating = {"claude", "gpt"} if not args.swap else {"gpt", "claude"}
            judge_keys = [k for k in MODEL_MAP if k not in debating]

        print(f"\nInitializing judges: {', '.join(judge_keys)}")
        judge_models = []
        for key in judge_keys:
            try:
                model = init_model(key)
                judge_models.append(model)
                print(f"  {model.name} ({model.model_id})")
            except (ValueError, Exception) as e:
                print(f"  Error initializing {key}: {e}")

        if judge_models:
            panel = JudgePanel(judges=judge_models, verbose=True)
            result = await panel.judge_debate(transcript)
            markdown += result_to_markdown(transcript, result)
        else:
            print("  No judges available, skipping judging.")

    output_file.write_text(markdown)
    print(f"\nTranscript saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
