"""Scoring data types and aggregation for debate judging."""

from dataclasses import dataclass, field
from enum import Enum


class ScoringCategory(str, Enum):
    """Categories used for scoring debates."""

    ARGUMENTATION = "argumentation"
    EVIDENCE = "evidence"
    CLASH = "clash"
    REBUTTAL = "rebuttal"
    PERSUASIVENESS = "persuasiveness"


@dataclass
class DebaterScores:
    """Scores for a single debater from a single judge."""

    argumentation: int
    evidence: int
    clash: int
    rebuttal: int
    persuasiveness: int

    @property
    def total(self) -> int:
        return (
            self.argumentation
            + self.evidence
            + self.clash
            + self.rebuttal
            + self.persuasiveness
        )

    def validate(self) -> None:
        """Raise ValueError if any score is outside 1-10."""
        for cat in ScoringCategory:
            val = getattr(self, cat.value)
            if not isinstance(val, int) or not 1 <= val <= 10:
                raise ValueError(
                    f"{cat.value} score must be an integer 1-10, got {val!r}"
                )


@dataclass
class JudgeDecision:
    """A single judge's decision for a debate."""

    judge_name: str
    judge_model_id: str
    judge_provider: str
    scores_a: DebaterScores  # Affirmative
    scores_b: DebaterScores  # Negative
    winner: str  # "A" or "B"
    reasoning: str
    raw_response: str
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class AggregateScores:
    """Averaged scores across multiple judges."""

    argumentation: float
    evidence: float
    clash: float
    rebuttal: float
    persuasiveness: float

    @property
    def total(self) -> float:
        return (
            self.argumentation
            + self.evidence
            + self.clash
            + self.rebuttal
            + self.persuasiveness
        )


@dataclass
class DebateResult:
    """Complete judging result for a debate."""

    debate_id: str
    resolution: str
    affirmative_model: str
    negative_model: str
    decisions: list[JudgeDecision]
    aggregate_a: AggregateScores
    aggregate_b: AggregateScores
    winner_side: str  # "affirmative" or "negative"
    winner_model: str
    margin: float

    @property
    def is_unanimous(self) -> bool:
        if not self.decisions:
            return True
        first = self.decisions[0].winner
        return all(d.winner == first for d in self.decisions)


def aggregate_scores(decisions: list[JudgeDecision], side: str) -> AggregateScores:
    """Average scores across judges for a given side ('a' or 'b')."""
    if not decisions:
        return AggregateScores(0.0, 0.0, 0.0, 0.0, 0.0)

    attr = f"scores_{side}"
    n = len(decisions)
    totals = {cat: 0.0 for cat in ScoringCategory}

    for decision in decisions:
        scores: DebaterScores = getattr(decision, attr)
        for cat in ScoringCategory:
            totals[cat] += getattr(scores, cat.value)

    return AggregateScores(
        argumentation=totals[ScoringCategory.ARGUMENTATION] / n,
        evidence=totals[ScoringCategory.EVIDENCE] / n,
        clash=totals[ScoringCategory.CLASH] / n,
        rebuttal=totals[ScoringCategory.REBUTTAL] / n,
        persuasiveness=totals[ScoringCategory.PERSUASIVENESS] / n,
    )


def determine_winner(
    decisions: list[JudgeDecision],
    aggregate_a: AggregateScores,
    aggregate_b: AggregateScores,
) -> tuple[str, float]:
    """Determine the winner using tie-breaking rules.

    Returns (winner side "A" or "B", margin).

    Tie-break order:
    1. Majority of judge picks
    2. Higher aggregate total
    3. Higher persuasiveness
    4. Affirmative wins
    """
    a_picks = sum(1 for d in decisions if d.winner == "A")
    b_picks = len(decisions) - a_picks

    # 1. Majority picks
    if a_picks != b_picks:
        winner = "A" if a_picks > b_picks else "B"
        margin = abs(aggregate_a.total - aggregate_b.total)
        return winner, margin

    # 2. Higher aggregate total
    if aggregate_a.total != aggregate_b.total:
        winner = "A" if aggregate_a.total > aggregate_b.total else "B"
        margin = abs(aggregate_a.total - aggregate_b.total)
        return winner, margin

    # 3. Higher persuasiveness
    if aggregate_a.persuasiveness != aggregate_b.persuasiveness:
        winner = "A" if aggregate_a.persuasiveness > aggregate_b.persuasiveness else "B"
        margin = abs(aggregate_a.persuasiveness - aggregate_b.persuasiveness)
        return winner, margin

    # 4. Affirmative wins
    return "A", 0.0
