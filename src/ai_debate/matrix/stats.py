"""Statistics computation for matrix tournaments."""

from .elo import compute_elo_ratings
from .types import (
    CategoryAverages,
    HeadToHead,
    MatrixDebateResult,
    MatrixStats,
    ModelRecord,
)


def compute_records(
    debate_results: list[MatrixDebateResult],
    model_names: list[str],
) -> dict[str, ModelRecord]:
    """Tally wins/losses overall and by side for each model."""
    records = {name: ModelRecord(model_name=name) for name in model_names}

    for result in debate_results:
        winner = records[result.winner_model]
        loser = records[result.loser_model]

        winner.wins += 1
        loser.losses += 1

        if result.winner_side == "affirmative":
            winner.aff_wins += 1
            loser.neg_losses += 1
        else:
            winner.neg_wins += 1
            loser.aff_losses += 1

    return records


def compute_head_to_head(
    debate_results: list[MatrixDebateResult],
    model_names: list[str],
) -> dict[str, dict[str, HeadToHead]]:
    """Compute head-to-head records between all pairs."""
    h2h: dict[str, dict[str, HeadToHead]] = {}

    for a in model_names:
        h2h[a] = {}
        for b in model_names:
            if a != b:
                h2h[a][b] = HeadToHead(model_a=a, model_b=b)

    for result in debate_results:
        aff = result.affirmative_model
        neg = result.negative_model
        winner = result.winner_model

        if winner == aff:
            h2h[aff][neg].a_wins += 1
            h2h[neg][aff].b_wins += 1
        else:
            h2h[neg][aff].a_wins += 1
            h2h[aff][neg].b_wins += 1

    return h2h


def compute_category_averages(
    debate_results: list[MatrixDebateResult],
    model_names: list[str],
) -> dict[str, CategoryAverages]:
    """Average the 5 scoring categories across all debates each model participated in."""
    categories = ["argumentation", "evidence", "clash", "rebuttal", "persuasiveness"]
    totals: dict[str, dict[str, float]] = {
        name: {cat: 0.0 for cat in categories} for name in model_names
    }
    counts: dict[str, int] = {name: 0 for name in model_names}

    for result in debate_results:
        for model_name in [result.affirmative_model, result.negative_model]:
            if model_name in result.category_scores:
                scores = result.category_scores[model_name]
                counts[model_name] += 1
                for cat in categories:
                    totals[model_name][cat] += scores.get(cat, 0.0)

    averages = {}
    for name in model_names:
        n = counts[name]
        if n > 0:
            averages[name] = CategoryAverages(
                model_name=name,
                argumentation=totals[name]["argumentation"] / n,
                evidence=totals[name]["evidence"] / n,
                clash=totals[name]["clash"] / n,
                rebuttal=totals[name]["rebuttal"] / n,
                persuasiveness=totals[name]["persuasiveness"] / n,
            )
        else:
            averages[name] = CategoryAverages(model_name=name)

    return averages


def compute_matrix_stats(
    debate_results: list[MatrixDebateResult],
    model_names: list[str],
) -> MatrixStats:
    """Compute all statistics for a matrix tournament."""
    return MatrixStats(
        records=compute_records(debate_results, model_names),
        head_to_head=compute_head_to_head(debate_results, model_names),
        category_averages=compute_category_averages(debate_results, model_names),
        elo_ratings=compute_elo_ratings(debate_results, model_names),
    )
