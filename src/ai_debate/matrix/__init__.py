"""Matrix tournament module for round-robin AI debates."""

from .markdown import leaderboard_to_markdown, matrix_to_markdown
from .runner import MatrixRunner
from .scheduler import build_matrix_schedule, estimate_matrix_cost
from .serialization import matrix_result_to_json
from .types import (
    CategoryAverages,
    EloRating,
    HeadToHead,
    MatrixDebateEntry,
    MatrixDebateResult,
    MatrixResult,
    MatrixStats,
    ModelRecord,
)

__all__ = [
    "MatrixRunner",
    "build_matrix_schedule",
    "estimate_matrix_cost",
    "matrix_to_markdown",
    "leaderboard_to_markdown",
    "matrix_result_to_json",
    "CategoryAverages",
    "EloRating",
    "HeadToHead",
    "MatrixDebateEntry",
    "MatrixDebateResult",
    "MatrixResult",
    "MatrixStats",
    "ModelRecord",
]
