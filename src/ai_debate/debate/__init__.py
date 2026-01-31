"""Debate engine and format definitions."""

from ai_debate.debate.engine import (
    DebateEngine,
    DebateTranscript,
    PhaseResult,
    transcript_to_markdown,
)
from ai_debate.debate.formats import (
    LINCOLN_DOUGLAS,
    DebateFormat,
    DebatePhase,
    PhaseType,
    SpeakerRole,
)

__all__ = [
    "DebateEngine",
    "DebateFormat",
    "DebatePhase",
    "DebateTranscript",
    "LINCOLN_DOUGLAS",
    "PhaseResult",
    "PhaseType",
    "SpeakerRole",
    "transcript_to_markdown",
]
