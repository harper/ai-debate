"""Data types for matrix debate tournaments."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MatrixDebateEntry:
    """A scheduled debate within a matrix tournament."""

    affirmative_name: str
    negative_name: str
    judge_names: list[str]
    debate_index: int


@dataclass
class MatrixDebateResult:
    """Flattened summary of a single debate result.

    Stores strings and floats (not embedded engine objects) for clean
    JSON serialization. Full transcripts are saved separately.
    """

    debate_index: int
    affirmative_model: str
    negative_model: str
    winner_model: str
    loser_model: str
    winner_side: str  # "affirmative" or "negative"
    margin: float
    is_unanimous: bool
    aggregate_aff_total: float
    aggregate_neg_total: float
    category_scores: dict[str, dict[str, float]]  # {model_name: {category: avg}}
    judge_names: list[str]
    transcript_id: str


@dataclass
class ModelRecord:
    """Win/loss record for a model."""

    model_name: str
    wins: int = 0
    losses: int = 0
    aff_wins: int = 0
    aff_losses: int = 0
    neg_wins: int = 0
    neg_losses: int = 0

    @property
    def total_games(self) -> int:
        return self.wins + self.losses

    @property
    def win_rate(self) -> float:
        return self.wins / self.total_games if self.total_games > 0 else 0.0

    @property
    def aff_win_rate(self) -> float:
        aff_total = self.aff_wins + self.aff_losses
        return self.aff_wins / aff_total if aff_total > 0 else 0.0

    @property
    def neg_win_rate(self) -> float:
        neg_total = self.neg_wins + self.neg_losses
        return self.neg_wins / neg_total if neg_total > 0 else 0.0


@dataclass
class HeadToHead:
    """Head-to-head record between two models."""

    model_a: str
    model_b: str
    a_wins: int = 0
    b_wins: int = 0

    @property
    def a_win_rate(self) -> float:
        total = self.a_wins + self.b_wins
        return self.a_wins / total if total > 0 else 0.0


@dataclass
class CategoryAverages:
    """Average scores per scoring category for a model."""

    model_name: str
    argumentation: float = 0.0
    evidence: float = 0.0
    clash: float = 0.0
    rebuttal: float = 0.0
    persuasiveness: float = 0.0

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
class EloRating:
    """Elo rating for a model."""

    model_name: str
    rating: float = 1500.0
    games_played: int = 0
    rating_history: list[float] = field(default_factory=lambda: [1500.0])


@dataclass
class MatrixStats:
    """Aggregated statistics for a matrix tournament."""

    records: dict[str, ModelRecord]
    head_to_head: dict[str, dict[str, HeadToHead]]
    category_averages: dict[str, CategoryAverages]
    elo_ratings: dict[str, EloRating]


@dataclass
class MatrixResult:
    """Complete results of a matrix tournament."""

    id: str
    resolution: str
    model_names: list[str]
    total_debates: int
    debate_results: list[MatrixDebateResult]
    stats: MatrixStats
    started_at: datetime
    completed_at: datetime

    @property
    def duration_seconds(self) -> float:
        return (self.completed_at - self.started_at).total_seconds()
