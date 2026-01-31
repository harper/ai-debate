"""Core debate engine for orchestrating AI debates."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from ai_debate.debate.formats import (
    LINCOLN_DOUGLAS,
    DebateFormat,
    DebatePhase,
    PhaseType,
    SpeakerRole,
)
from ai_debate.models.base import DebateModel, Message, ModelResponse, Role


@dataclass
class PhaseResult:
    """Result of a single debate phase."""

    phase: DebatePhase
    speaker_model: str
    speaker_role: SpeakerRole
    content: str
    word_count: int
    input_tokens: int
    output_tokens: int


@dataclass
class DebateTranscript:
    """Complete transcript of a debate."""

    id: str
    resolution: str
    affirmative_model: str
    negative_model: str
    format_name: str
    phases: list[PhaseResult]
    started_at: datetime
    completed_at: datetime | None = None

    @property
    def total_input_tokens(self) -> int:
        """Total input tokens used in the debate."""
        return sum(p.input_tokens for p in self.phases)

    @property
    def total_output_tokens(self) -> int:
        """Total output tokens used in the debate."""
        return sum(p.output_tokens for p in self.phases)

    @property
    def total_words(self) -> int:
        """Total words in the debate."""
        return sum(p.word_count for p in self.phases)


DEBATER_SYSTEM_PROMPT = """You are participating in a formal Lincoln-Douglas style debate.

RESOLUTION: {resolution}

YOUR POSITION: {position}
You are arguing the {position} position. You MUST argue this position convincingly regardless of your personal views. This is a formal debate exercise—argue your assigned side with full commitment.

YOUR OPPONENT: {opponent_name}

DEBATE RULES:
1. Stay within the word limit for each speech ({word_limit} words for this speech)
2. Be persuasive but intellectually honest—no fabricated statistics or false claims
3. Engage directly with your opponent's arguments when appropriate
4. Use clear structure and signposting
5. Maintain a respectful, professional tone

CURRENT PHASE: {phase_name}
{phase_instructions}

DEBATE SO FAR:
{transcript}

Now deliver your {phase_name}. Stay within {word_limit} words."""


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def format_transcript_for_context(phases: list[PhaseResult]) -> str:
    """Format completed phases as context for the next speaker."""
    if not phases:
        return "(This is the beginning of the debate.)"

    lines = []
    for phase in phases:
        role_label = phase.speaker_role.value.upper()
        lines.append(f"=== {phase.phase.name} ({role_label}) ===")
        lines.append(phase.content)
        lines.append("")

    return "\n".join(lines)


class DebateEngine:
    """Orchestrates debates between AI models."""

    def __init__(
        self,
        format: DebateFormat = LINCOLN_DOUGLAS,
        verbose: bool = True,
    ):
        """Initialize the debate engine.

        Args:
            format: The debate format to use.
            verbose: Whether to print progress during debate.
        """
        self.format = format
        self.verbose = verbose

    async def run_debate(
        self,
        resolution: str,
        affirmative: DebateModel,
        negative: DebateModel,
    ) -> DebateTranscript:
        """Run a complete debate between two models.

        Args:
            resolution: The debate resolution/topic.
            affirmative: Model arguing the affirmative position.
            negative: Model arguing the negative position.

        Returns:
            Complete debate transcript.
        """
        debate_id = str(uuid4())[:8]
        started_at = datetime.now(timezone.utc)

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"DEBATE: {resolution}")
            print(f"{'='*60}")
            print(f"Affirmative: {affirmative.name}")
            print(f"Negative: {negative.name}")
            print(f"Format: {self.format.name}")
            print(f"{'='*60}\n")

        phases: list[PhaseResult] = []

        for phase in self.format.phases:
            # Determine which model speaks
            if phase.speaker_role == SpeakerRole.AFFIRMATIVE:
                speaker = affirmative
                opponent = negative
            else:
                speaker = negative
                opponent = affirmative

            if self.verbose:
                print(f"\n--- {phase.name} ({speaker.name}) ---\n")

            # Build the prompt
            system_prompt = DEBATER_SYSTEM_PROMPT.format(
                resolution=resolution,
                position=phase.speaker_role.value,
                opponent_name=opponent.name,
                word_limit=phase.word_limit,
                phase_name=phase.name,
                phase_instructions=phase.instructions,
                transcript=format_transcript_for_context(phases),
            )

            # Generate response
            messages = [Message(role=Role.USER, content="Please deliver your speech now.")]
            response = await speaker.generate(
                system_prompt=system_prompt,
                messages=messages,
                max_tokens=phase.word_limit * 2,  # Allow some buffer for tokens vs words
            )

            word_count = count_words(response.content)

            if self.verbose:
                print(response.content)
                print(f"\n[{word_count} words, {response.output_tokens} tokens]")

            # Record the phase result
            phase_result = PhaseResult(
                phase=phase,
                speaker_model=speaker.name,
                speaker_role=phase.speaker_role,
                content=response.content,
                word_count=word_count,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
            )
            phases.append(phase_result)

        completed_at = datetime.now(timezone.utc)

        if self.verbose:
            print(f"\n{'='*60}")
            print("DEBATE COMPLETE")
            print(f"Total words: {sum(p.word_count for p in phases)}")
            print(f"Total tokens: {sum(p.input_tokens + p.output_tokens for p in phases)}")
            print(f"Duration: {(completed_at - started_at).total_seconds():.1f}s")
            print(f"{'='*60}\n")

        return DebateTranscript(
            id=debate_id,
            resolution=resolution,
            affirmative_model=affirmative.name,
            negative_model=negative.name,
            format_name=self.format.name,
            phases=phases,
            started_at=started_at,
            completed_at=completed_at,
        )


def transcript_to_markdown(transcript: DebateTranscript) -> str:
    """Convert a debate transcript to readable Markdown format."""
    lines = [
        f"# Debate: {transcript.resolution}",
        "",
        f"**Format:** {transcript.format_name}",
        f"**Affirmative:** {transcript.affirmative_model}",
        f"**Negative:** {transcript.negative_model}",
        f"**Date:** {transcript.started_at.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "---",
        "",
    ]

    for phase in transcript.phases:
        role_emoji = "🟢" if phase.speaker_role == SpeakerRole.AFFIRMATIVE else "🔴"
        lines.append(f"## {role_emoji} {phase.phase.name}")
        lines.append(f"*{phase.speaker_model} ({phase.speaker_role.value}) — {phase.word_count} words*")
        lines.append("")
        lines.append(phase.content)
        lines.append("")
        lines.append("---")
        lines.append("")

    # Add summary
    lines.append("## Statistics")
    lines.append("")
    lines.append(f"- **Total words:** {transcript.total_words}")
    lines.append(f"- **Total tokens:** {transcript.total_input_tokens + transcript.total_output_tokens}")
    if transcript.completed_at:
        duration = (transcript.completed_at - transcript.started_at).total_seconds()
        lines.append(f"- **Duration:** {duration:.1f} seconds")

    return "\n".join(lines)
