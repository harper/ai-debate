#!/usr/bin/env python3
"""Run a full 4-debate match between 4 AI models.

Match structure (each model debates twice and judges twice):
  Round 1: A(aff) vs B(neg) — judged by C, D
  Round 2: B(aff) vs A(neg) — judged by C, D
  Round 3: C(aff) vs D(neg) — judged by A, B
  Round 4: D(aff) vs C(neg) — judged by A, B
"""

import argparse
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from ai_debate.debate import DebateEngine, transcript_to_markdown
from ai_debate.debate.engine import DebateTranscript
from ai_debate.judging import DebateResult, JudgePanel
from ai_debate.judging.judge import result_to_markdown
from ai_debate.models import AnthropicModel, GoogleModel, OpenAIModel, XAIModel
from ai_debate.models.base import DebateModel


@dataclass
class MatchDebate:
    """A single debate within a match."""

    affirmative: DebateModel
    negative: DebateModel
    judges: list[DebateModel]


@dataclass
class MatchResult:
    """Complete results of a 4-debate match."""

    resolution: str
    rounds: list[tuple[DebateTranscript, DebateResult]]
    model_records: dict[str, dict[str, int]]  # model_name -> {wins, losses}
    started_at: datetime
    completed_at: datetime


def build_match_schedule(models: list[DebateModel]) -> list[MatchDebate]:
    """Build a 4-debate schedule from 4 models.

    Round 1: models[0](aff) vs models[1](neg) — judged by models[2], models[3]
    Round 2: models[1](aff) vs models[0](neg) — judged by models[2], models[3]
    Round 3: models[2](aff) vs models[3](neg) — judged by models[0], models[1]
    Round 4: models[3](aff) vs models[2](neg) — judged by models[0], models[1]
    """
    a, b, c, d = models
    return [
        MatchDebate(affirmative=a, negative=b, judges=[c, d]),
        MatchDebate(affirmative=b, negative=a, judges=[c, d]),
        MatchDebate(affirmative=c, negative=d, judges=[a, b]),
        MatchDebate(affirmative=d, negative=c, judges=[a, b]),
    ]


def compute_records(
    rounds: list[tuple[DebateTranscript, DebateResult]],
    models: list[DebateModel],
) -> dict[str, dict[str, int]]:
    """Tally wins and losses per model."""
    records = {m.name: {"wins": 0, "losses": 0} for m in models}

    for transcript, result in rounds:
        winner = result.winner_model
        loser = (
            transcript.negative_model
            if result.winner_side == "affirmative"
            else transcript.affirmative_model
        )
        records[winner]["wins"] += 1
        records[loser]["losses"] += 1

    return records


async def run_match(
    resolution: str,
    models: list[DebateModel],
    verbose: bool = True,
) -> MatchResult:
    """Run a full 4-debate match.

    Debates run sequentially to respect rate limits and ensure no model
    debates and judges simultaneously. Judges within each round run in parallel.
    """
    started_at = datetime.now(timezone.utc)
    schedule = build_match_schedule(models)
    engine = DebateEngine(verbose=verbose)
    rounds: list[tuple[DebateTranscript, DebateResult]] = []

    for i, debate in enumerate(schedule, 1):
        if verbose:
            print(f"\n{'#'*60}")
            print(f"# MATCH ROUND {i}/4")
            print(f"# {debate.affirmative.name} (AFF) vs {debate.negative.name} (NEG)")
            print(f"# Judges: {', '.join(j.name for j in debate.judges)}")
            print(f"{'#'*60}")

        transcript = await engine.run_debate(
            resolution=resolution,
            affirmative=debate.affirmative,
            negative=debate.negative,
        )

        panel = JudgePanel(judges=debate.judges, verbose=verbose)
        result = await panel.judge_debate(transcript)
        rounds.append((transcript, result))

        if verbose:
            print(f"\n  Round {i} winner: {result.winner_model}")

    completed_at = datetime.now(timezone.utc)
    records = compute_records(rounds, models)

    return MatchResult(
        resolution=resolution,
        rounds=rounds,
        model_records=records,
        started_at=started_at,
        completed_at=completed_at,
    )


def match_to_markdown(match: MatchResult) -> str:
    """Format complete match results as markdown."""
    lines = [
        f"# Match Results: {match.resolution}",
        "",
        f"**Date:** {match.started_at.strftime('%Y-%m-%d %H:%M UTC')}",
    ]

    duration = (match.completed_at - match.started_at).total_seconds()
    lines.append(f"**Duration:** {duration:.0f} seconds")
    lines.append("")

    # Standings
    lines.append("## Standings")
    lines.append("")
    lines.append("| Model | Wins | Losses |")
    lines.append("|-------|:----:|:------:|")

    sorted_models = sorted(
        match.model_records.items(),
        key=lambda x: x[1]["wins"],
        reverse=True,
    )
    for name, record in sorted_models:
        lines.append(f"| {name} | {record['wins']} | {record['losses']} |")

    lines.append("")

    # Per-round summaries
    lines.append("## Round-by-Round")
    lines.append("")

    for i, (transcript, result) in enumerate(match.rounds, 1):
        unanimous = "Unanimous" if result.is_unanimous else "Split"
        lines.append(f"### Round {i}")
        lines.append(f"- **{transcript.affirmative_model}** (AFF) vs **{transcript.negative_model}** (NEG)")
        lines.append(f"- **Winner:** {result.winner_model} ({result.winner_side})")
        lines.append(f"- **Decision:** {unanimous} | Margin: {result.margin:.1f}")
        lines.append(f"- **Scores:** AFF {result.aggregate_a.total:.1f} — NEG {result.aggregate_b.total:.1f}")

        judges_str = ", ".join(
            f"{d.judge_name} -> {d.winner}" for d in result.decisions
        )
        lines.append(f"- **Judges:** {judges_str}")
        lines.append("")

    return "\n".join(lines)


async def main() -> None:
    """Run a full match between 4 AI models."""
    parser = argparse.ArgumentParser(
        description="Run a 4-debate match between all AI models"
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
        "--verbose", "-v",
        action="store_true",
        default=True,
        help="Print detailed progress (default: True)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress detailed output",
    )
    args = parser.parse_args()
    verbose = not args.quiet

    print("Initializing all 4 models...\n")

    models: list[DebateModel] = []
    model_classes = [
        ("Claude", AnthropicModel, "ANTHROPIC_API_KEY"),
        ("GPT", OpenAIModel, "OPENAI_API_KEY"),
        ("Gemini", GoogleModel, "GOOGLE_API_KEY"),
        ("Grok", XAIModel, "XAI_API_KEY"),
    ]

    for label, cls, env_var in model_classes:
        try:
            model = cls()
            models.append(model)
            print(f"  {model.name} ({model.model_id})")
        except ValueError as e:
            print(f"  Error initializing {label}: {e}")
            print(f"  Set {env_var} environment variable")
            return

    if len(models) < 4:
        print("\nNeed all 4 models to run a match. Exiting.")
        return

    print(f"\nResolution: {args.resolution}")
    print(f"Match: 4 rounds, each model debates 2x and judges 2x\n")

    result = await run_match(
        resolution=args.resolution,
        models=models,
        verbose=verbose,
    )

    # Save individual debate transcripts
    debates_dir = Path("debates")
    debates_dir.mkdir(exist_ok=True)

    for transcript, debate_result in result.rounds:
        output_file = debates_dir / f"debate-{transcript.id}.md"
        markdown = transcript_to_markdown(transcript)
        markdown += result_to_markdown(transcript, debate_result)
        output_file.write_text(markdown)

    # Save match summary
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    match_id = result.started_at.strftime("%Y%m%d-%H%M%S")
    summary_file = results_dir / f"match-{match_id}.md"
    summary_file.write_text(match_to_markdown(result))

    print(f"\n{'='*60}")
    print("MATCH COMPLETE")
    print(f"{'='*60}")
    print(f"\nStandings:")
    sorted_models = sorted(
        result.model_records.items(),
        key=lambda x: x[1]["wins"],
        reverse=True,
    )
    for name, record in sorted_models:
        print(f"  {name}: {record['wins']}W-{record['losses']}L")

    print(f"\nMatch summary saved to: {summary_file}")
    print(f"Individual debates saved to: {debates_dir}/")


if __name__ == "__main__":
    asyncio.run(main())
