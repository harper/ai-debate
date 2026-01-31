# Implementation Plan

## Overview

This document outlines the phased implementation approach for the AI Debate Arena platform.

---

## Phase 1: Foundation

### 1.1 Project Setup
- Python project with `pyproject.toml` using `uv` for dependency management
- Dependencies: `anthropic`, `openai`, `google-generativeai`, `httpx` (for xAI)
- Testing framework: `pytest`
- Type hints throughout with `mypy` validation

### 1.2 Model Abstraction Layer

Create a unified interface for all AI models:

```python
class DebateModel(Protocol):
    name: str
    provider: str

    async def generate(
        self,
        system_prompt: str,
        messages: list[Message],
        max_tokens: int
    ) -> str:
        """Generate a debate response."""
        ...
```

Implement for each provider:
- `AnthropicModel` - Claude via `anthropic` SDK
- `OpenAIModel` - GPT via `openai` SDK
- `GoogleModel` - Gemini via `google-generativeai`
- `XAIModel` - Grok via HTTP (uses OpenAI-compatible API)

### 1.3 Debate Format Definition

Define the Lincoln-Douglas format as a data structure:

```python
@dataclass
class DebatePhase:
    name: str
    speaker_role: Literal["affirmative", "negative"]
    phase_type: Literal["constructive", "cross_exam", "rebuttal"]
    word_limit: int
    instructions: str

LD_FORMAT = [
    DebatePhase("Affirmative Constructive", "affirmative", "constructive", 800, ...),
    DebatePhase("Cross-Examination", "negative", "cross_exam", 150, ...),
    # ... etc
]
```

---

## Phase 2: Core Debate Engine

### 2.1 Debate Orchestrator

The central engine that:
1. Accepts a resolution and two models (affirmative/negative)
2. Manages turn-taking according to format
3. Builds conversation context for each model
4. Handles cross-examination as Q&A exchanges
5. Collects and structures the full transcript

```python
class DebateEngine:
    async def run_debate(
        self,
        resolution: str,
        affirmative: DebateModel,
        negative: DebateModel,
        format: list[DebatePhase] = LD_FORMAT
    ) -> DebateTranscript:
        ...
```

### 2.2 Prompt Engineering

Critical prompts to develop:

**Debater System Prompt**
- Role assignment (affirmative/negative)
- Format rules and expectations
- Word limits and structure requirements
- Instruction to argue assigned position regardless of model's "opinions"
- Cross-examination protocol

**Cross-Examination Prompts**
- Questioner: Generate pointed questions that expose weaknesses
- Responder: Answer directly, defend position under pressure

**Rebuttal Prompts**
- Reference opponent's specific arguments
- Clash directly (no ships passing in the night)
- Rebuild own case where attacked

### 2.3 Transcript Structure

```python
@dataclass
class DebateTranscript:
    id: str
    resolution: str
    affirmative_model: str
    negative_model: str
    timestamp: datetime
    phases: list[PhaseResult]

@dataclass
class PhaseResult:
    phase: DebatePhase
    speaker_model: str
    content: str
    word_count: int
    tokens_used: int
```

---

## Phase 3: Judging System

### 3.1 AI Judge Panel

Three AI judges (models not in the debate) evaluate using a rubric:

**Scoring Categories (1-10 each)**
1. **Argumentation** - Logical structure, reasoning quality
2. **Evidence & Examples** - Support for claims
3. **Clash** - Direct engagement with opponent's arguments
4. **Rebuttal Quality** - Effectiveness of responses to attacks
5. **Persuasiveness** - Rhetorical effectiveness, compelling narrative

**Judge Prompt Design**
- Provide full transcript
- Explicit rubric with descriptions
- Require reasoning before scores
- Ask for winner declaration with rationale

### 3.2 Scoring Aggregation

```python
@dataclass
class JudgeDecision:
    judge_model: str
    scores: dict[str, dict[str, int]]  # {model: {category: score}}
    winner: str
    reasoning: str

@dataclass
class DebateResult:
    debate_id: str
    judge_decisions: list[JudgeDecision]
    final_winner: str  # majority vote
    aggregate_scores: dict[str, float]
```

### 3.3 Anti-Bias Measures

- Judges don't know which model produced which arguments (blind judging)
- Rotate judge panels
- Track if judges favor their own model family
- Consider using only "neutral" models as judges (e.g., only Claude judges GPT vs Gemini)

---

## Phase 4: Matrix Debates

### 4.1 Matrix Runner

For a topic, run the full round-robin:

```python
async def run_matrix(
    resolution: str,
    models: list[DebateModel]
) -> MatrixResult:
    """
    For N models, runs N*(N-1) debates.
    Each pair debates twice (switching sides).
    """
    debates = []
    for aff in models:
        for neg in models:
            if aff != neg:
                result = await engine.run_debate(resolution, aff, neg)
                debates.append(result)
    return MatrixResult(debates)
```

### 4.2 Statistics & Leaderboard

Track:
- Overall win rate
- Win rate by position (Aff/Neg)
- Win rate vs each opponent
- Average scores by category
- "Elo" style rating (optional)

---

## Phase 5: Storage & CLI

### 5.1 Storage Backend

Start simple with JSON files:
```
debates/
├── 2024-01-15/
│   ├── debate-abc123.json
│   └── debate-def456.json
└── index.json
```

Later: SQLite or PostgreSQL for querying.

### 5.2 CLI Commands

Using `click` or `typer`:

```bash
# Run single debate
ai-debate run "Resolution here" --aff claude --neg gpt

# Run matrix
ai-debate matrix "Resolution" --models claude,gpt,gemini,grok

# View results
ai-debate results --debate-id abc123
ai-debate leaderboard
ai-debate history --model claude

# Export
ai-debate export abc123 --format markdown
ai-debate export abc123 --format html
```

---

## Phase 6: Future Enhancements

### 6.1 Web Interface
- View debate transcripts with nice formatting
- Real-time streaming of ongoing debates
- Interactive leaderboards and statistics

### 6.2 Human Voting
- Pre/post debate stance polls
- Oxford-style "who moved more voters" winner
- Compare human vs AI judge decisions

### 6.3 Community Topics
- Submit topic suggestions
- Vote on upcoming debates
- Agent-assisted topic curation

### 6.4 Advanced Features
- Multiple debate formats (Policy, Parliamentary)
- Team debates (2 models per side)
- Tournament brackets
- Model fine-tuning analysis (does RLHF affect argumentation?)

---

## Technical Decisions

### Async Throughout
All model calls are async for:
- Parallel judge deliberation
- Future: streaming support
- Matrix debates can parallelize independent matches

### Rate Limiting
Implement per-provider rate limiting:
- Anthropic: Respect tier limits
- OpenAI: Handle 429s with backoff
- Configurable concurrency per provider

### Cost Tracking
Log token usage per debate:
- Input/output tokens per model
- Estimated cost per debate
- Matrix cost projections

### Error Handling
- Retry on transient failures
- Save partial transcripts on failure
- Resume interrupted matrices

---

## Testing Strategy

### Unit Tests
- Format validation
- Prompt construction
- Score aggregation

### Integration Tests
- Mock model responses
- Full debate flow
- Judge panel consensus

### Live Tests (manual)
- Actual model debates
- Quality review of arguments
- Judge calibration

---

## Initial Milestone

**MVP Goal**: Run a single debate between Claude and GPT-4, judged by Gemini

Deliverables:
1. Model interfaces for Claude and GPT
2. Basic LD format implementation
3. Debate engine that produces transcript
4. Single AI judge (not full panel)
5. CLI to run and view debate
6. Markdown export

This proves the concept before expanding to full matrix support.
