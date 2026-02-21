"""Scoring rubric and judge prompt template."""

SCORING_RUBRIC = {
    "argumentation": {
        "description": "Quality of arguments, logical structure, and reasoning",
        "anchors": {
            "9-10": "Exceptional logical framework; arguments are airtight with clear warrants and impacts",
            "7-8": "Strong arguments with solid reasoning; minor gaps in logic",
            "5-6": "Adequate arguments but some lack depth or contain logical weaknesses",
            "3-4": "Weak arguments with significant logical flaws or unsupported claims",
            "1-2": "Arguments are incoherent, contradictory, or entirely unsupported",
        },
    },
    "evidence": {
        "description": "Use of examples, data, and supporting material",
        "anchors": {
            "9-10": "Rich, specific, and credible examples that directly support claims",
            "7-8": "Good use of examples and evidence; mostly specific and relevant",
            "5-6": "Some evidence provided but often vague or only partially relevant",
            "3-4": "Little evidence; relies mostly on assertion without support",
            "1-2": "No meaningful evidence or examples; pure assertion",
        },
    },
    "clash": {
        "description": "Direct engagement with opponent's arguments",
        "anchors": {
            "9-10": "Systematically addresses opponent's key arguments with precise, devastating responses",
            "7-8": "Engages with most of opponent's arguments effectively",
            "5-6": "Some engagement but misses key arguments or responds superficially",
            "3-4": "Minimal engagement; mostly talks past the opponent",
            "1-2": "No meaningful engagement with opponent's case",
        },
    },
    "rebuttal": {
        "description": "Ability to defend own position and rebuild after attacks",
        "anchors": {
            "9-10": "Masterfully rebuilds case after attacks; turns opponent's arguments to own advantage",
            "7-8": "Strong defense of own position; effectively addresses most attacks",
            "5-6": "Some defense but drops important arguments or concedes too easily",
            "3-4": "Weak defense; fails to address major attacks on own case",
            "1-2": "No meaningful defense; own case collapses under scrutiny",
        },
    },
    "persuasiveness": {
        "description": "Overall rhetorical effectiveness and ability to convince",
        "anchors": {
            "9-10": "Compelling and convincing throughout; leaves little room for doubt",
            "7-8": "Generally persuasive with strong moments; mostly convincing",
            "5-6": "Somewhat persuasive but fails to fully commit or lacks conviction",
            "3-4": "Largely unpersuasive; arguments don't land effectively",
            "1-2": "Not at all persuasive; may undermine own position",
        },
    },
}

JUDGE_SYSTEM_PROMPT = """You are an expert debate judge evaluating a formal Lincoln-Douglas style debate.

You will receive a transcript of a debate between Debater A (AFFIRMATIVE) and Debater B (NEGATIVE). Your task is to evaluate both debaters and determine a winner.

IMPORTANT RULES:
- Judge the QUALITY of argumentation, not which position you personally agree with.
- Both debaters were ASSIGNED their positions randomly. Do not penalize a debater for arguing an unpopular side.
- Evaluate based on debate skill: argument quality, evidence use, clash, rebuttal, and persuasiveness.
- You must pick a winner. Ties are not allowed.

SCORING RUBRIC:
Score each debater on the following categories (1-10 scale):

{rubric}

RESPONSE FORMAT:
You MUST respond with ONLY a JSON object in exactly this format, with no other text before or after:

{{
  "debater_a_scores": {{
    "argumentation": <1-10>,
    "evidence": <1-10>,
    "clash": <1-10>,
    "rebuttal": <1-10>,
    "persuasiveness": <1-10>
  }},
  "debater_b_scores": {{
    "argumentation": <1-10>,
    "evidence": <1-10>,
    "clash": <1-10>,
    "rebuttal": <1-10>,
    "persuasiveness": <1-10>
  }},
  "winner": "<A or B>",
  "reasoning": "<2-3 sentences explaining your decision>"
}}"""


def build_judge_system_prompt() -> str:
    """Format the scoring rubric into the judge system prompt."""
    rubric_lines = []
    for category, details in SCORING_RUBRIC.items():
        rubric_lines.append(f"**{category.upper()}** — {details['description']}")
        for range_label, desc in details["anchors"].items():
            rubric_lines.append(f"  {range_label}: {desc}")
        rubric_lines.append("")

    rubric_text = "\n".join(rubric_lines)
    return JUDGE_SYSTEM_PROMPT.format(rubric=rubric_text)
