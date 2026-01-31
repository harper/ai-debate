# AI Debate Arena

An experimental platform that orchestrates structured debates between different AI models in a round-robin matrix format. Models debate both sides of issues against each other, providing insights into their reasoning capabilities, argumentation styles, and philosophical stances.

## Concept

Each debate topic runs as a full matrix where every AI model debates every other model on both sides of the issue:

```
Topic: "Social media does more harm than good"

         | Claude | Gemini | GPT | Grok |
---------|--------|--------|-----|------|
Claude   |   -    |  A/N   | A/N | A/N  |
Gemini   |  N/A   |   -    | A/N | A/N  |
GPT      |  N/A   |  N/A   |  -  | A/N  |
Grok     |  N/A   |  N/A   | N/A |  -   |

A = Affirmative, N = Negative
Each cell represents two debates (model argues both sides)
```

## Debate Format

We use a modified **Lincoln-Douglas** format optimized for AI, combined with **Oxford-style** judging:

### Structure (per debate)

| Phase | Speaker | Duration | Purpose |
|-------|---------|----------|---------|
| 1. Affirmative Constructive | Affirmative | ~800 words | Present case and framework |
| 2. Cross-Examination | Negative | 3 questions | Challenge affirmative's case |
| 3. Negative Constructive | Negative | ~1000 words | Present counter-case and rebuttals |
| 4. Cross-Examination | Affirmative | 3 questions | Challenge negative's case |
| 5. Affirmative Rebuttal | Affirmative | ~500 words | Address attacks, rebuild case |
| 6. Negative Rebuttal | Negative | ~700 words | Final attacks and summation |
| 7. Affirmative Rejoinder | Affirmative | ~400 words | Final defense and voting issues |

### Why This Format?

- **Lincoln-Douglas base**: 1v1 format is clean for AI-to-AI debates, emphasizes values and philosophy over pure evidence
- **Cross-examination**: Tests models' ability to respond under pressure and defend positions
- **Affirmative speaks first and last**: Standard debate convention that balances burden of proof
- **Oxford-style judging**: Audience/judge voting before and after measures persuasion, not just "who won"

## Judging System

Each debate is evaluated by:

1. **AI Judge Panel** (3 different models not participating in the debate)
   - Score on: argumentation, evidence use, rebuttal quality, rhetorical effectiveness
   - Provide reasoning for decisions

2. **Human Voting** (future)
   - Pre-debate stance poll
   - Post-debate stance poll
   - Winner = side that moved more voters

3. **Metrics Tracked**
   - Win/loss record per model
   - Win rate by position (Affirmative vs Negative)
   - Persuasion delta (stance change induced)
   - Head-to-head records

## Models

Initial lineup (latest flagship reasoning models as of Jan 2026):
- **Claude** (Anthropic) - `claude-opus-4-5-20251124` - Anthropic's most intelligent model
- **GPT-5.2** (OpenAI) - `gpt-5.2` - OpenAI's flagship model (supersedes o3)
- **Gemini** (Google) - `gemini-3-pro` with Deep Think - Google's most capable reasoning model
- **Grok** (xAI) - `grok-4.1` - xAI's latest, #1 on LMArena leaderboard

## Topics

Topics follow the resolution format common in competitive debate, drawn from major policy debates of 2025.

### Phase 1: Curated Topics

**AI & Technology**
- "Resolved: AI regulation should be handled at the federal level, preempting state laws like the Colorado AI Act"
- "Resolved: Companies should be required to disclose when AI systems are used in hiring, pricing, or lending decisions"
- "Resolved: The benefits of AI job automation outweigh the costs to displaced workers"
- "Resolved: Military integration of commercial AI systems (like Grok in the Pentagon) poses unacceptable risks"

**Economy & Trade**
- "Resolved: The 2025 tariff increases have done more harm than good to the U.S. economy"
- "Resolved: Protectionist trade policies are justified to counter China's economic influence"
- "Resolved: Cryptocurrency should be regulated as a commodity rather than a security"
- "Resolved: The Federal Reserve should issue a Central Bank Digital Currency (CBDC)"

**Society & Governance**
- "Resolved: Social media platforms should be legally liable for algorithmic amplification of misinformation"
- "Resolved: Deepfake technology should be banned for non-entertainment purposes"
- "Resolved: Mass deportation policies cause more harm than benefit to the United States"
- "Resolved: DOGE-style government efficiency initiatives are an appropriate approach to reducing federal spending"

**Privacy & Ethics**
- "Resolved: Individuals should have the right to delete all personal data held by corporations"
- "Resolved: Facial recognition technology should be banned in public spaces"
- "Resolved: AI companies should be required to pay royalties to creators whose work was used in training data"

### Phase 2: Community Topics (Future)
- Polling platform for topic suggestions
- Voting by humans and AI agents
- Weekly/monthly featured debates

## Project Structure

```
ai-debate/
├── src/
│   ├── debate/
│   │   ├── engine.py         # Core debate orchestration
│   │   ├── formats.py        # Debate format definitions
│   │   └── prompts.py        # System prompts for debaters
│   ├── models/
│   │   ├── base.py           # Abstract model interface
│   │   ├── anthropic.py      # Claude integration
│   │   ├── openai.py         # GPT integration
│   │   ├── google.py         # Gemini integration
│   │   └── xai.py            # Grok integration
│   ├── judging/
│   │   ├── panel.py          # AI judge panel logic
│   │   ├── scoring.py        # Scoring criteria and rubrics
│   │   └── metrics.py        # Statistics and analysis
│   ├── storage/
│   │   ├── debates.py        # Debate transcript storage
│   │   └── results.py        # Results and leaderboards
│   └── cli.py                # Command-line interface
├── debates/                   # Stored debate transcripts
├── results/                   # Analysis and leaderboards
├── tests/
└── pyproject.toml
```

## Usage

```bash
# Run a single debate
ai-debate run --topic "Social media does more harm than good" \
              --affirmative claude --negative gpt

# Run full matrix for a topic
ai-debate matrix --topic "Privacy vs security" --models claude,gpt,gemini,grok

# View leaderboard
ai-debate leaderboard

# Export debate transcript
ai-debate export --debate-id <id> --format markdown
```

## Installation

```bash
# Clone and install
git clone https://github.com/harper/ai-debate.git
cd ai-debate
uv sync

# Configure API keys
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...
export XAI_API_KEY=...
```

## Roadmap

- [ ] Core debate engine with LD format
- [ ] Model integrations (Claude, GPT, Gemini, Grok)
- [ ] AI judge panel
- [ ] CLI for running debates
- [ ] Transcript storage and export
- [ ] Basic leaderboard
- [ ] Web viewer for debate transcripts
- [ ] Human voting integration
- [ ] Community topic suggestions
- [ ] Real-time debate streaming

## Research Questions

This project aims to explore:

1. Do models argue differently when defending positions they might "disagree" with?
2. Which models are most persuasive? Most logically rigorous?
3. Are there systematic differences in argumentation style between model families?
4. How do models perform in adversarial reasoning against each other?
5. Can models identify and exploit weaknesses in other models' arguments?
6. **Bias detection**: Since models argue both sides of each issue, can we detect underlying biases by comparing argument quality/effort across positions? Do judges show favoritism toward their own model family?

## License

MIT

## References

Debate format research:
- [Lincoln-Douglas Debate Format](https://www.csun.edu/~dgw61315/debformats.html)
- [Oxford-Style Debate Format](https://opentodebate.org/what-is-the-oxford-style-debate-format/)
- [NPDA Parliamentary Debate](https://en.wikipedia.org/wiki/National_Parliamentary_Debate_Association)
- [Policy Debate Structure](https://debateus.org/the-basic-structure-of-policy-debate-2/)
