"""Debate format definitions."""

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class SpeakerRole(str, Enum):
    """Role of the speaker in a debate."""

    AFFIRMATIVE = "affirmative"
    NEGATIVE = "negative"


class PhaseType(str, Enum):
    """Type of debate phase."""

    CONSTRUCTIVE = "constructive"
    CROSS_EXAM = "cross_examination"
    REBUTTAL = "rebuttal"


@dataclass(frozen=True)
class DebatePhase:
    """Definition of a single phase in a debate format."""

    name: str
    speaker_role: SpeakerRole
    phase_type: PhaseType
    word_limit: int
    instructions: str


# Lincoln-Douglas Debate Format
# Adapted for AI debates with word limits instead of time limits

LD_FORMAT: list[DebatePhase] = [
    DebatePhase(
        name="Affirmative Constructive",
        speaker_role=SpeakerRole.AFFIRMATIVE,
        phase_type=PhaseType.CONSTRUCTIVE,
        word_limit=800,
        instructions="""Present your constructive case for the affirmative position.

You should:
1. Define key terms in the resolution if needed
2. Present your value premise (the core value you're upholding)
3. Present your value criterion (the standard for measuring the value)
4. Provide 2-3 contentions (main arguments) supporting your position
5. Use logical reasoning and examples to support each contention

Structure your speech clearly with signposting (e.g., "My first contention is...").
Be persuasive but intellectually honest.""",
    ),
    DebatePhase(
        name="Cross-Examination (by Negative)",
        speaker_role=SpeakerRole.NEGATIVE,
        phase_type=PhaseType.CROSS_EXAM,
        word_limit=300,
        instructions="""Ask 3 pointed questions to challenge the affirmative's case.

Your questions should:
1. Expose weaknesses or contradictions in their arguments
2. Clarify positions that seem vague or unsupported
3. Set up arguments you'll make in your constructive

Ask direct questions that require specific answers. Avoid making arguments yourself—this is for questioning only.""",
    ),
    DebatePhase(
        name="Affirmative Answers",
        speaker_role=SpeakerRole.AFFIRMATIVE,
        phase_type=PhaseType.CROSS_EXAM,
        word_limit=300,
        instructions="""Answer the negative's questions directly and defend your position.

You should:
1. Answer each question honestly and directly
2. Defend your positions when challenged
3. Clarify any misunderstandings about your case
4. Avoid evasion—direct answers are more credible

Keep answers concise but complete.""",
    ),
    DebatePhase(
        name="Negative Constructive",
        speaker_role=SpeakerRole.NEGATIVE,
        phase_type=PhaseType.CONSTRUCTIVE,
        word_limit=1000,
        instructions="""Present your case against the resolution AND refute the affirmative's arguments.

You should:
1. Attack the affirmative's value premise or criterion if flawed
2. Refute their key contentions with counter-evidence or logic
3. Present your own value premise and criterion
4. Provide 2-3 contentions supporting the negative position

You have more words because you must both attack and construct. Allocate roughly 400 words to refutation and 600 to your own case.""",
    ),
    DebatePhase(
        name="Cross-Examination (by Affirmative)",
        speaker_role=SpeakerRole.AFFIRMATIVE,
        phase_type=PhaseType.CROSS_EXAM,
        word_limit=300,
        instructions="""Ask 3 pointed questions to challenge the negative's case.

Your questions should:
1. Expose weaknesses in their refutations of your case
2. Challenge the validity of their own contentions
3. Set up arguments for your rebuttal

Focus on the most damaging parts of their speech.""",
    ),
    DebatePhase(
        name="Negative Answers",
        speaker_role=SpeakerRole.NEGATIVE,
        phase_type=PhaseType.CROSS_EXAM,
        word_limit=300,
        instructions="""Answer the affirmative's questions directly and defend your position.

You should:
1. Answer each question honestly and directly
2. Defend both your refutations and your own case
3. Maintain consistency with your constructive speech

Keep answers concise but complete.""",
    ),
    DebatePhase(
        name="Affirmative Rebuttal",
        speaker_role=SpeakerRole.AFFIRMATIVE,
        phase_type=PhaseType.REBUTTAL,
        word_limit=500,
        instructions="""Rebuild your case and respond to the negative's attacks.

You should:
1. Address the most damaging attacks on your case
2. Explain why your arguments still stand
3. Attack weaknesses in the negative's own case
4. Begin crystallizing why you're winning the debate

Do NOT introduce new arguments—extend and apply what's already been said.""",
    ),
    DebatePhase(
        name="Negative Rebuttal",
        speaker_role=SpeakerRole.NEGATIVE,
        phase_type=PhaseType.REBUTTAL,
        word_limit=700,
        instructions="""Deliver your final attacks and summarize why you've won.

You should:
1. Respond to the affirmative's rebuttal
2. Extend your most successful attacks
3. Explain why your case outweighs theirs
4. Crystallize the key voting issues in your favor

This is your last speech—make it count. Be clear about why a judge should vote negative.""",
    ),
    DebatePhase(
        name="Affirmative Rejoinder",
        speaker_role=SpeakerRole.AFFIRMATIVE,
        phase_type=PhaseType.REBUTTAL,
        word_limit=400,
        instructions="""Deliver your final defense and summary.

You should:
1. Respond to the negative's final attacks
2. Crystallize why your value framework is superior
3. Summarize the key voting issues in your favor
4. End with a clear, compelling reason to affirm the resolution

This is your last chance to speak—focus on the most important issues and leave a strong final impression.""",
    ),
]


@dataclass(frozen=True)
class DebateFormat:
    """A complete debate format definition."""

    name: str
    description: str
    phases: list[DebatePhase]

    @property
    def total_word_limit(self) -> int:
        """Total word limit across all phases."""
        return sum(phase.word_limit for phase in self.phases)


LINCOLN_DOUGLAS = DebateFormat(
    name="Lincoln-Douglas",
    description="One-on-one value debate format emphasizing philosophy and logic",
    phases=LD_FORMAT,
)
