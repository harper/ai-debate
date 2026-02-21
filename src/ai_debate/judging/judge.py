"""Core judging logic: blind formatting, response parsing, and JudgePanel."""

import asyncio
import json
import re

from ai_debate.debate.engine import DebateTranscript, PhaseResult
from ai_debate.debate.formats import SpeakerRole
from ai_debate.models.base import DebateModel, Message, Role

from .rubric import build_judge_system_prompt
from .scoring import (
    AggregateScores,
    DebateResult,
    DebaterScores,
    JudgeDecision,
    aggregate_scores,
    determine_winner,
)


def format_blind_transcript(transcript: DebateTranscript) -> str:
    """Format a debate transcript with model identities stripped.

    Uses speaker_role (not speaker_model) so model names never appear.
    """
    lines = [
        f"RESOLUTION: {transcript.resolution}",
        "",
        "Debater A argues the AFFIRMATIVE position.",
        "Debater B argues the NEGATIVE position.",
        "",
        "--- TRANSCRIPT ---",
        "",
    ]

    for phase in transcript.phases:
        if phase.speaker_role == SpeakerRole.AFFIRMATIVE:
            label = "Debater A (AFFIRMATIVE)"
        else:
            label = "Debater B (NEGATIVE)"

        lines.append(f"=== {phase.phase.name} — {label} ===")
        lines.append(phase.content)
        lines.append("")

    return "\n".join(lines)


def parse_judge_response(raw: str) -> dict:
    """Parse JSON from a judge's response with fallback strategies.

    Tries:
    1. Direct JSON parse
    2. Markdown code fence extraction
    3. Outermost brace extraction
    """
    # 1. Direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 2. Markdown code fence
    fence_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", raw, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Outermost braces
    first = raw.find("{")
    last = raw.rfind("}")
    if first != -1 and last != -1 and last > first:
        try:
            return json.loads(raw[first : last + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse judge response as JSON:\n{raw[:500]}")


def extract_decision(
    parsed: dict,
    judge_name: str,
    judge_model_id: str,
    judge_provider: str,
    raw_response: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
) -> JudgeDecision:
    """Convert a parsed JSON dict into a validated JudgeDecision."""
    scores_a = DebaterScores(**parsed["debater_a_scores"])
    scores_b = DebaterScores(**parsed["debater_b_scores"])
    scores_a.validate()
    scores_b.validate()

    winner = parsed["winner"].upper()
    if winner not in ("A", "B"):
        raise ValueError(f"Winner must be 'A' or 'B', got {winner!r}")

    return JudgeDecision(
        judge_name=judge_name,
        judge_model_id=judge_model_id,
        judge_provider=judge_provider,
        scores_a=scores_a,
        scores_b=scores_b,
        winner=winner,
        reasoning=parsed.get("reasoning", ""),
        raw_response=raw_response,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


class JudgePanel:
    """Runs multiple judges against a debate transcript."""

    def __init__(self, judges: list[DebateModel], verbose: bool = True):
        self.judges = judges
        self.verbose = verbose

    async def _run_single_judge(
        self,
        judge: DebateModel,
        transcript: DebateTranscript,
    ) -> JudgeDecision:
        """Run a single judge on the transcript."""
        blind = format_blind_transcript(transcript)
        system_prompt = build_judge_system_prompt()

        messages = [Message(role=Role.USER, content=blind)]

        if self.verbose:
            print(f"  Judging: {judge.name}...")

        response = await judge.generate(
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=2048,
        )

        parsed = parse_judge_response(response.content)
        decision = extract_decision(
            parsed=parsed,
            judge_name=judge.name,
            judge_model_id=judge.model_id,
            judge_provider=judge.provider,
            raw_response=response.content,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
        )

        if self.verbose:
            print(f"  {judge.name} picks: Debater {decision.winner} "
                  f"({decision.scores_a.total} vs {decision.scores_b.total})")

        return decision

    async def judge_debate(self, transcript: DebateTranscript) -> DebateResult:
        """Judge a debate with all panel members in parallel."""
        if self.verbose:
            print(f"\nJudging debate {transcript.id}...")

        decisions = await asyncio.gather(
            *[self._run_single_judge(j, transcript) for j in self.judges]
        )

        agg_a = aggregate_scores(list(decisions), "a")
        agg_b = aggregate_scores(list(decisions), "b")
        winner_code, margin = determine_winner(list(decisions), agg_a, agg_b)

        winner_side = "affirmative" if winner_code == "A" else "negative"
        winner_model = (
            transcript.affirmative_model
            if winner_code == "A"
            else transcript.negative_model
        )

        result = DebateResult(
            debate_id=transcript.id,
            resolution=transcript.resolution,
            affirmative_model=transcript.affirmative_model,
            negative_model=transcript.negative_model,
            decisions=list(decisions),
            aggregate_a=agg_a,
            aggregate_b=agg_b,
            winner_side=winner_side,
            winner_model=winner_model,
            margin=margin,
        )

        if self.verbose:
            unanimous = "UNANIMOUS" if result.is_unanimous else "SPLIT"
            print(f"\n  Result: {result.winner_model} wins ({winner_side}) — {unanimous}")
            print(f"  Aggregate: A={agg_a.total:.1f} vs B={agg_b.total:.1f} (margin: {margin:.1f})")

        return result


def result_to_markdown(transcript: DebateTranscript, result: DebateResult) -> str:
    """Format judging results as markdown."""
    lines = [
        "",
        "---",
        "",
        "## Judging Results",
        "",
        f"**Winner: {result.winner_model}** ({result.winner_side})",
        f"**Decision: {'Unanimous' if result.is_unanimous else 'Split'}**",
        f"**Margin: {result.margin:.1f} points**",
        "",
        "### Aggregate Scores",
        "",
        "| Category | Debater A (AFF) | Debater B (NEG) |",
        "|----------|:-:|:-:|",
    ]

    for cat in ["argumentation", "evidence", "clash", "rebuttal", "persuasiveness"]:
        a_val = getattr(result.aggregate_a, cat)
        b_val = getattr(result.aggregate_b, cat)
        lines.append(f"| {cat.capitalize()} | {a_val:.1f} | {b_val:.1f} |")

    lines.append(f"| **Total** | **{result.aggregate_a.total:.1f}** | **{result.aggregate_b.total:.1f}** |")
    lines.append("")

    # Per-judge breakdown
    lines.append("### Per-Judge Breakdown")
    lines.append("")

    for d in result.decisions:
        lines.append(f"#### {d.judge_name} ({d.judge_provider})")
        lines.append(f"- **Pick:** Debater {d.winner}")
        lines.append(f"- **Scores A:** {d.scores_a.total} | Scores B: {d.scores_b.total}")
        lines.append(f"- **Reasoning:** {d.reasoning}")
        lines.append("")

    return "\n".join(lines)
