#!/usr/bin/env python3
"""Run a full round-robin matrix tournament between AI models.

Every model debates every other model on both sides. Non-debating models
serve as judges. For N models this produces N*(N-1) debates.

Examples:
  # Full 4-model matrix (12 debates)
  python scripts/run_matrix.py "Resolved: Space exploration funding should be increased"

  # Quick 2-model test (2 debates)
  python scripts/run_matrix.py --models claude,gpt "Resolved: AI is beneficial"

  # Preview schedule and cost without running
  python scripts/run_matrix.py --dry-run
"""

import argparse
import asyncio
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from ai_debate.debate import transcript_to_markdown
from ai_debate.judging.judge import result_to_markdown
from ai_debate.matrix import (
    MatrixRunner,
    build_matrix_schedule,
    estimate_matrix_cost,
    leaderboard_to_markdown,
    matrix_to_markdown,
    matrix_result_to_json,
)
from ai_debate.models import AnthropicModel, GoogleModel, OpenAIModel, XAIModel

MODEL_REGISTRY = {
    "claude": ("Claude", AnthropicModel, "ANTHROPIC_API_KEY"),
    "gpt": ("GPT", OpenAIModel, "OPENAI_API_KEY"),
    "gemini": ("Gemini", GoogleModel, "GOOGLE_API_KEY"),
    "grok": ("Grok", XAIModel, "XAI_API_KEY"),
}


def init_models(keys: list[str]) -> dict[str, object]:
    """Initialize models by their short names. Returns dict of name -> model."""
    models = {}
    for key in keys:
        key = key.strip().lower()
        if key not in MODEL_REGISTRY:
            print(f"Unknown model: {key!r}. Available: {', '.join(MODEL_REGISTRY)}")
            raise SystemExit(1)

        label, cls, env_var = MODEL_REGISTRY[key]
        try:
            model = cls()
            models[model.name] = model
            print(f"  {model.name} ({model.model_id})")
        except ValueError as e:
            print(f"  Error initializing {label}: {e}")
            print(f"  Set {env_var} environment variable")
            raise SystemExit(1)

    return models


async def main() -> None:
    """Run a full matrix tournament."""
    parser = argparse.ArgumentParser(
        description="Run a round-robin matrix tournament between AI models"
    )
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
        "--models", "-m",
        default="claude,gpt,gemini,grok",
        help="Comma-separated model keys (default: claude,gpt,gemini,grok)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show schedule and cost estimate without running",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose output",
    )
    args = parser.parse_args()
    verbose = not args.quiet

    model_keys = [k.strip() for k in args.models.split(",")]
    num_models = len(model_keys)

    # Cost estimate
    cost = estimate_matrix_cost(num_models)
    print(f"\nMatrix Tournament Plan")
    print(f"  Models: {', '.join(model_keys)} ({num_models})")
    print(f"  Total debates: {cost['total_debates']}")
    print(f"  Judges per debate: {cost['judges_per_debate']}")
    print(f"  Estimated tokens: ~{cost['estimated_total_tokens']:,}")
    print()

    if args.dry_run:
        # Show schedule preview using placeholder names
        placeholder_names = model_keys
        schedule = build_matrix_schedule(placeholder_names)
        print("Schedule:")
        for entry in schedule:
            judges = ", ".join(entry.judge_names)
            print(f"  {entry.debate_index + 1}. {entry.affirmative_name} (AFF) vs "
                  f"{entry.negative_name} (NEG) — Judges: {judges}")
        print("\nDry run complete. No debates were run.")
        return

    # Initialize models
    print("Initializing models...")
    models = init_models(model_keys)

    if len(models) < 2:
        print("\nNeed at least 2 models. Exiting.")
        return

    print(f"\nResolution: {args.resolution}")
    print(f"Matrix: {cost['total_debates']} debates, every model debates every other\n")

    # Set up directories
    debates_dir = Path("debates")
    debates_dir.mkdir(exist_ok=True)
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    # Callback to save individual debates incrementally
    def on_debate_complete(debate_index, matrix_result, transcript, debate_result):
        output_file = debates_dir / f"debate-{transcript.id}.md"
        markdown = transcript_to_markdown(transcript)
        markdown += result_to_markdown(transcript, debate_result)
        output_file.write_text(markdown)
        if verbose:
            print(f"  Saved: {output_file}")

    # Build schedule and run
    model_names = list(models.keys())
    schedule = build_matrix_schedule(model_names)

    runner = MatrixRunner(
        models=models,
        verbose=verbose,
        on_debate_complete=on_debate_complete,
    )

    result = await runner.run_matrix(
        resolution=args.resolution,
        schedule=schedule,
    )

    # Save matrix summary
    matrix_id = result.started_at.strftime("%Y%m%d-%H%M%S")
    summary_file = results_dir / f"matrix-{matrix_id}.md"
    summary_file.write_text(matrix_to_markdown(result))

    # Save structured JSON
    json_file = results_dir / f"matrix-{matrix_id}.json"
    json_file.write_text(matrix_result_to_json(result))

    # Print final leaderboard
    print(f"\n{'=' * 60}")
    print("MATRIX TOURNAMENT COMPLETE")
    print(f"{'=' * 60}")
    print()
    print(leaderboard_to_markdown(result.stats))

    print(f"Matrix summary: {summary_file}")
    print(f"Structured data: {json_file}")
    print(f"Individual debates: {debates_dir}/")


if __name__ == "__main__":
    asyncio.run(main())
