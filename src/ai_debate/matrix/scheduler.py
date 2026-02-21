"""Round-robin schedule generation for matrix tournaments."""

from .types import MatrixDebateEntry


def build_matrix_schedule(models: list[str]) -> list[MatrixDebateEntry]:
    """Build a full round-robin schedule where every model debates every other.

    For each ordered pair (A, B) where A != B, A debates as affirmative
    against B as negative. Non-debating models serve as judges.

    For N models: N * (N-1) debates total.
    """
    schedule: list[MatrixDebateEntry] = []
    index = 0

    for aff in models:
        for neg in models:
            if aff == neg:
                continue
            judges = [m for m in models if m != aff and m != neg]
            schedule.append(
                MatrixDebateEntry(
                    affirmative_name=aff,
                    negative_name=neg,
                    judge_names=judges,
                    debate_index=index,
                )
            )
            index += 1

    return schedule


def estimate_matrix_cost(
    num_models: int,
    avg_tokens_per_debate: int = 40_000,
    avg_tokens_per_judge: int = 8_000,
) -> dict[str, int]:
    """Estimate token cost for a matrix tournament.

    Returns dict with total_debates, judges_per_debate, and estimated token counts.
    """
    total_debates = num_models * (num_models - 1)
    judges_per_debate = num_models - 2

    debate_tokens = total_debates * avg_tokens_per_debate
    judge_tokens = total_debates * judges_per_debate * avg_tokens_per_judge
    total_tokens = debate_tokens + judge_tokens

    return {
        "total_debates": total_debates,
        "judges_per_debate": judges_per_debate,
        "estimated_debate_tokens": debate_tokens,
        "estimated_judge_tokens": judge_tokens,
        "estimated_total_tokens": total_tokens,
    }
