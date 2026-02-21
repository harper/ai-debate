"""Elo rating computation for matrix tournaments."""

from .types import EloRating, MatrixDebateResult

DEFAULT_K = 32
DEFAULT_RATING = 1500.0


def expected_score(rating_a: float, rating_b: float) -> float:
    """Calculate expected score for player A against player B."""
    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))


def update_ratings(
    rating_winner: float,
    rating_loser: float,
    k: float = DEFAULT_K,
) -> tuple[float, float]:
    """Update Elo ratings after a game.

    Returns (new_winner_rating, new_loser_rating).
    """
    expected_w = expected_score(rating_winner, rating_loser)
    expected_l = expected_score(rating_loser, rating_winner)

    new_winner = rating_winner + k * (1.0 - expected_w)
    new_loser = rating_loser + k * (0.0 - expected_l)

    return new_winner, new_loser


def compute_elo_ratings(
    debate_results: list[MatrixDebateResult],
    model_names: list[str],
    k: float = DEFAULT_K,
) -> dict[str, EloRating]:
    """Compute Elo ratings from debate results in schedule order."""
    ratings = {
        name: EloRating(model_name=name) for name in model_names
    }

    for result in debate_results:
        winner = result.winner_model
        loser = result.loser_model

        new_winner, new_loser = update_ratings(
            ratings[winner].rating,
            ratings[loser].rating,
            k=k,
        )

        ratings[winner].rating = new_winner
        ratings[winner].games_played += 1
        ratings[winner].rating_history.append(new_winner)

        ratings[loser].rating = new_loser
        ratings[loser].games_played += 1
        ratings[loser].rating_history.append(new_loser)

    return ratings
