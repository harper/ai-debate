"""Markdown output for matrix tournament results and leaderboard."""

from .types import MatrixResult, MatrixStats


def leaderboard_to_markdown(stats: MatrixStats) -> str:
    """Format a compact leaderboard table."""
    lines = [
        "## Leaderboard",
        "",
        "| Rank | Model | W-L | Win% | Aff% | Neg% | Elo |",
        "|:----:|-------|:---:|:----:|:----:|:----:|:---:|",
    ]

    sorted_models = sorted(
        stats.records.values(),
        key=lambda r: (r.win_rate, r.wins, stats.elo_ratings[r.model_name].rating),
        reverse=True,
    )

    for rank, record in enumerate(sorted_models, 1):
        elo = stats.elo_ratings[record.model_name].rating
        lines.append(
            f"| {rank} | {record.model_name} "
            f"| {record.wins}-{record.losses} "
            f"| {record.win_rate:.0%} "
            f"| {record.aff_win_rate:.0%} "
            f"| {record.neg_win_rate:.0%} "
            f"| {elo:.0f} |"
        )

    lines.append("")
    return "\n".join(lines)


def _head_to_head_grid(result: MatrixResult) -> str:
    """Format an NxN head-to-head grid."""
    names = result.model_names
    h2h = result.stats.head_to_head
    lines = [
        "## Head-to-Head",
        "",
        "Wins by row model against column model:",
        "",
    ]

    # Header row
    header = "| | " + " | ".join(names) + " |"
    separator = "|---|" + "|".join(":---:" for _ in names) + "|"
    lines.append(header)
    lines.append(separator)

    for row_name in names:
        cells = []
        for col_name in names:
            if row_name == col_name:
                cells.append("-")
            else:
                record = h2h[row_name][col_name]
                cells.append(str(record.a_wins))
        lines.append(f"| {row_name} | " + " | ".join(cells) + " |")

    lines.append("")
    return "\n".join(lines)


def _category_averages_table(result: MatrixResult) -> str:
    """Format per-model category averages."""
    lines = [
        "## Category Averages",
        "",
        "| Model | Arg | Evi | Clash | Reb | Pers | Total |",
        "|-------|:---:|:---:|:-----:|:---:|:----:|:-----:|",
    ]

    sorted_models = sorted(
        result.stats.category_averages.values(),
        key=lambda c: c.total,
        reverse=True,
    )

    for cat_avg in sorted_models:
        lines.append(
            f"| {cat_avg.model_name} "
            f"| {cat_avg.argumentation:.1f} "
            f"| {cat_avg.evidence:.1f} "
            f"| {cat_avg.clash:.1f} "
            f"| {cat_avg.rebuttal:.1f} "
            f"| {cat_avg.persuasiveness:.1f} "
            f"| {cat_avg.total:.1f} |"
        )

    lines.append("")
    return "\n".join(lines)


def _elo_ratings_section(result: MatrixResult) -> str:
    """Format Elo ratings with delta from starting 1500."""
    lines = [
        "## Elo Ratings",
        "",
        "| Model | Rating | Delta | Games |",
        "|-------|:------:|:-----:|:-----:|",
    ]

    sorted_ratings = sorted(
        result.stats.elo_ratings.values(),
        key=lambda e: e.rating,
        reverse=True,
    )

    for elo in sorted_ratings:
        delta = elo.rating - 1500.0
        sign = "+" if delta >= 0 else ""
        lines.append(
            f"| {elo.model_name} "
            f"| {elo.rating:.0f} "
            f"| {sign}{delta:.0f} "
            f"| {elo.games_played} |"
        )

    lines.append("")
    return "\n".join(lines)


def _debate_summaries(result: MatrixResult) -> str:
    """Format per-debate summaries."""
    lines = [
        "## Debate Summaries",
        "",
    ]

    for dr in result.debate_results:
        decision = "Unanimous" if dr.is_unanimous else "Split"
        lines.append(f"### Debate {dr.debate_index + 1}: {dr.affirmative_model} (AFF) vs {dr.negative_model} (NEG)")
        lines.append(f"- **Winner:** {dr.winner_model} ({dr.winner_side})")
        lines.append(f"- **Decision:** {decision} | Margin: {dr.margin:.1f}")
        lines.append(f"- **Scores:** AFF {dr.aggregate_aff_total:.1f} — NEG {dr.aggregate_neg_total:.1f}")
        lines.append(f"- **Judges:** {', '.join(dr.judge_names)}")
        lines.append(f"- **Transcript:** `debate-{dr.transcript_id}.md`")
        lines.append("")

    return "\n".join(lines)


def matrix_to_markdown(result: MatrixResult) -> str:
    """Format complete matrix tournament results as markdown."""
    duration = result.duration_seconds
    minutes = int(duration // 60)
    seconds = int(duration % 60)

    lines = [
        f"# Matrix Tournament Results",
        "",
        f"**Resolution:** {result.resolution}",
        f"**Date:** {result.started_at.strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Models:** {', '.join(result.model_names)}",
        f"**Total Debates:** {result.total_debates}",
        f"**Duration:** {minutes}m {seconds}s",
        "",
    ]

    sections = [
        leaderboard_to_markdown(result.stats),
        _head_to_head_grid(result),
        _category_averages_table(result),
        _elo_ratings_section(result),
        _debate_summaries(result),
    ]

    return "\n".join(lines) + "\n".join(sections)
