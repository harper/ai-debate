"""Matrix tournament runner — orchestrates round-robin debates."""

from collections.abc import Callable
from datetime import datetime, timezone
from uuid import uuid4

from ai_debate.debate.engine import DebateEngine, DebateTranscript
from ai_debate.judging.judge import JudgePanel
from ai_debate.judging.scoring import AggregateScores, DebateResult
from ai_debate.models.base import DebateModel

from .stats import compute_matrix_stats
from .types import MatrixDebateEntry, MatrixDebateResult, MatrixResult


def _build_category_scores(
    aff_model: str,
    neg_model: str,
    agg_a: AggregateScores,
    agg_b: AggregateScores,
) -> dict[str, dict[str, float]]:
    """Extract category scores into a flat dict keyed by model name."""
    categories = ["argumentation", "evidence", "clash", "rebuttal", "persuasiveness"]
    return {
        aff_model: {cat: getattr(agg_a, cat) for cat in categories},
        neg_model: {cat: getattr(agg_b, cat) for cat in categories},
    }


class MatrixRunner:
    """Orchestrates a full round-robin matrix tournament."""

    def __init__(
        self,
        models: dict[str, DebateModel],
        verbose: bool = True,
        on_debate_complete: Callable[[int, MatrixDebateResult, DebateTranscript, DebateResult], None] | None = None,
    ):
        """Initialize the matrix runner.

        Args:
            models: Dict mapping model short names to DebateModel instances.
            verbose: Whether to print progress.
            on_debate_complete: Optional callback after each debate finishes.
                Receives (debate_index, matrix_result, transcript, debate_result).
        """
        names = list(models.keys())
        if len(names) != len(set(names)):
            raise ValueError("Model names must be unique")
        if len(names) < 2:
            raise ValueError("Need at least 2 models for a matrix tournament")

        self.models = models
        self.verbose = verbose
        self.on_debate_complete = on_debate_complete
        self._full_results: list[tuple[DebateTranscript, DebateResult]] = []

    @property
    def full_results(self) -> list[tuple[DebateTranscript, DebateResult]]:
        """Full debate transcripts and results for saving individual files."""
        return self._full_results

    async def run_matrix(
        self,
        resolution: str,
        schedule: list[MatrixDebateEntry],
    ) -> MatrixResult:
        """Run all debates in the matrix sequentially.

        Judges within each debate run in parallel via JudgePanel.
        """
        started_at = datetime.now(timezone.utc)
        model_names = list(self.models.keys())
        engine = DebateEngine(verbose=self.verbose)
        debate_results: list[MatrixDebateResult] = []
        self._full_results = []

        for entry in schedule:
            if self.verbose:
                print(f"\n{'#' * 60}")
                print(f"# MATRIX DEBATE {entry.debate_index + 1}/{len(schedule)}")
                print(f"# {entry.affirmative_name} (AFF) vs {entry.negative_name} (NEG)")
                print(f"# Judges: {', '.join(entry.judge_names)}")
                print(f"{'#' * 60}")

            affirmative = self.models[entry.affirmative_name]
            negative = self.models[entry.negative_name]
            judges = [self.models[name] for name in entry.judge_names]

            # Run debate
            transcript = await engine.run_debate(
                resolution=resolution,
                affirmative=affirmative,
                negative=negative,
            )

            # Judge debate (parallel within panel)
            panel = JudgePanel(judges=judges, verbose=self.verbose)
            result = await panel.judge_debate(transcript)
            self._full_results.append((transcript, result))

            # Build flat result
            loser = (
                transcript.negative_model
                if result.winner_side == "affirmative"
                else transcript.affirmative_model
            )

            category_scores = _build_category_scores(
                transcript.affirmative_model,
                transcript.negative_model,
                result.aggregate_a,
                result.aggregate_b,
            )

            matrix_result = MatrixDebateResult(
                debate_index=entry.debate_index,
                affirmative_model=transcript.affirmative_model,
                negative_model=transcript.negative_model,
                winner_model=result.winner_model,
                loser_model=loser,
                winner_side=result.winner_side,
                margin=result.margin,
                is_unanimous=result.is_unanimous,
                aggregate_aff_total=result.aggregate_a.total,
                aggregate_neg_total=result.aggregate_b.total,
                category_scores=category_scores,
                judge_names=[d.judge_name for d in result.decisions],
                transcript_id=transcript.id,
            )
            debate_results.append(matrix_result)

            if self.verbose:
                print(f"\n  Debate {entry.debate_index + 1} winner: {result.winner_model}")

            if self.on_debate_complete:
                self.on_debate_complete(entry.debate_index, matrix_result, transcript, result)

        completed_at = datetime.now(timezone.utc)
        stats = compute_matrix_stats(debate_results, model_names)

        return MatrixResult(
            id=uuid4().hex[:8],
            resolution=resolution,
            model_names=model_names,
            total_debates=len(debate_results),
            debate_results=debate_results,
            stats=stats,
            started_at=started_at,
            completed_at=completed_at,
        )
