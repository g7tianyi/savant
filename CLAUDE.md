# Technical Documentation

Architecture and implementation details for the Learning Skills system.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Skills System](#skills-system)
- [State Management](#state-management)
- [Data Schema](#data-schema)
- [Learning Algorithms](#learning-algorithms)
- [Extensibility](#extensibility)
- [Development Guide](#development-guide)

## Architecture Overview

### Design Philosophy

**Minimalist, conversation-based learning** - No backends, no servers, just dialogue.

```
┌─────────────────────────────────────────────────┐
│  Claude Code (Conversation Layer)              │
│  - Natural language interaction                │
│  - Adaptive dialogue                           │
│  - Real-time feedback                          │
└─────────────────────────────────────────────────┘
           ↓                    ↑
┌─────────────────────────────────────────────────┐
│  Skills (.claude/skills/)                       │
│  - russian-learning.md (orchestration)          │
│  - spanish-learning.md (planned)                │
└─────────────────────────────────────────────────┘
           ↓                    ↑
┌─────────────────────────────────────────────────┐
│  State Manager (Python)                         │
│  - init-session: Select items for review        │
│  - update: Record interactions                  │
│  - finalize: Mark session complete              │
│  - stats: Show progress                         │
└─────────────────────────────────────────────────┘
           ↓                    ↑
┌─────────────────────────────────────────────────┐
│  Data Layer (JSON)                              │
│  - vocabulary.json (domain content)             │
│  - concepts.json (grammar/theory)               │
│  - learner-state.json (progress tracking)       │
└─────────────────────────────────────────────────┘
```

### Key Principles

1. **No Complexity** - Pure conversation + JSON state
2. **Local-First** - Everything on your machine
3. **Stateless Conversations** - State managed explicitly via Python scripts
4. **Composable** - Skills are independent, data-driven modules

## Skills System

### Skill Structure

A skill is a Markdown file that instructs Claude how to conduct a learning session.

```
.claude/skills/
└── russian-learning.md          # Skill definition
    └── scripts/
        └── state_manager.py     # State management logic
```

### Skill Definition (russian-learning.md)

Key sections:

1. **Role Definition** - What is Claude's role?
2. **Session Protocol** - How to initialize and run a session
3. **Dialogue Examples** - Natural conversation patterns
4. **Update Protocol** - How to track progress
5. **Methodologies** - Learning principles to apply
6. **Conversation Style** - Tone and engagement patterns

### Invocation

```bash
@russian-learning
```

This loads `.claude/skills/russian-learning.md` and starts the session.

## State Management

### State Manager (Python)

Path: `.claude/skills/russian-learning/scripts/state_manager.py`

**Commands:**

```bash
# Initialize session (select items for review)
python3 state_manager.py init-session [count]

# Record interaction
python3 state_manager.py update <item_id> <type> <correct> <confidence>

# Finalize session
python3 state_manager.py finalize <session_id>

# View stats
python3 state_manager.py stats
```

### Session Initialization

```python
def select_session_items(target_count: int = 15) -> Dict:
    """
    Select words/concepts for session based on:
    1. Due items (spaced repetition schedule)
    2. New items (never seen before)

    Returns:
    {
      "session_id": "20260308-143022",
      "words": ["книга", "время", ...],
      "concepts": ["genitive-possession", ...],
      "stats": {
        "due_words": 5,
        "new_words": 3,
        ...
      }
    }
    """
```

### Mastery Update

```python
def update_item_mastery(state, item_id, item_type, correct, confidence):
    """
    Updates mastery using Bayesian-inspired approach:

    If correct:
      mastery += 0.1 * (1 + confidence/100 * 0.5)
      interval *= 2.5

    If incorrect:
      mastery -= 0.15
      interval = 1 day

    Next review = now + interval_days
    """
```

### Spaced Repetition (SM-2 Style)

- **Correct answer**: Interval multiplied by 2.5
- **Incorrect answer**: Reset to 1 day
- **Capped**: 1 day minimum, 90 days maximum

## Data Schema

### Vocabulary (`data/russian-vocabulary.json`)

```json
{
  "meta": {
    "total_words": 1847,
    "levels": ["A1", "A2", "B1"],
    "categories": ["pronouns", "food", "travel", ...],
    "purpose": "A2→B1 practical conversation"
  },
  "words": {
    "книга": {
      "russian": "книга",
      "translation": "book",
      "pos": "noun",
      "level": "A1",
      "frequency": 5,
      "category": "daily-life",
      "examples": [
        "Я читаю книгу",
        "У меня есть книга"
      ],
      "notes": "Feminine noun, genitive: книги"
    }
  }
}
```

### Concepts (`data/russian-concepts.json`)

```json
{
  "meta": {
    "domain": "russian",
    "focus": "A2→B1 grammar",
    "total_concepts": 42
  },
  "concepts": {
    "genitive-possession": {
      "id": "genitive-possession",
      "name": "Genitive Case: Possession",
      "level": "A2",
      "category": "grammar",
      "prerequisites": ["nominative-case"],
      "description": "Using genitive with 'у' for possession",
      "examples": [
        "У меня есть книга (I have a book)",
        "У неё нет машины (She doesn't have a car)"
      ],
      "drills": [
        "Translate: I don't have time → У меня нет времени",
        "Create sentence using 'у + genitive'"
      ]
    }
  }
}
```

### Learner State (`data/learner-state.json`)

```json
{
  "meta": {
    "created": "2026-03-07T22:15:31",
    "last_session": "2026-03-08T14:30:22",
    "total_sessions": 5
  },
  "words": {
    "книга": {
      "mastery": 0.85,
      "review_count": 7,
      "error_count": 1,
      "last_reviewed": "2026-03-08T14:30:22",
      "next_review": "2026-03-15T14:30:22",
      "interval_days": 7
    }
  },
  "concepts": {
    "genitive-possession": {
      "mastery": 0.72,
      "review_count": 4,
      "error_count": 1,
      "last_reviewed": "2026-03-08T14:35:10",
      "next_review": "2026-03-12T14:35:10",
      "interval_days": 4
    }
  }
}
```

## Learning Algorithms

### 1. Retrieval-First Architecture

**Always test before teaching** - Creates knowledge gaps that prime attention.

```
Struggle to retrieve → Receive information → Stronger encoding
```

Implementation:
- Ask questions before presenting material
- Use graduated prompting (free recall → recognition → cued recall)
- Minimal hints to unlock retrieval

### 2. Adaptive Cognitive Load

**Monitor performance signals** - Adjust difficulty in real-time.

Signals:
- Response latency (slow = overload)
- Error patterns (random = overload, systematic = misconception)
- Self-reported confidence

Adjustments:
- **Overload**: Simplify, provide worked examples, break into sub-steps
- **Underload**: Combine concepts, introduce edge cases, request synthesis

### 3. Generative Learning

**Force production, not passive consumption**.

Methods:
- "Explain in your own words"
- "Create a sentence using X"
- "Teach this concept to a peer"
- Active construction > passive recognition

### 4. Metacognitive Tracking

**Confidence calibration** - Make learning observable.

After each interaction:
- Record confidence (0-100%)
- Compare to accuracy
- Detect overconfidence (confidence > accuracy)
- Provide calibration feedback

### 5. Spaced Repetition (SM-2)

**Optimize review timing** - Strengthen long-term retention.

Formula:
- `interval_next = interval_current * 2.5` (if correct)
- `interval_next = 1 day` (if incorrect)
- Capped between 1-90 days

### 6. Just-In-Time Elaboration

**Elaborate progressively** - Don't dump context upfront.

Schedule:
- Review 1: Basic facts
- Review 2: Contrastive examples
- Review 3: Causal reasoning
- Review 4: Systemic context

Error-triggered: Generate contrastive examples if confusion detected.

## Extensibility

### Adding a New Language (e.g., Spanish)

1. **Create vocabulary file**:
   ```bash
   data/spanish-vocabulary.json
   ```

2. **Create concepts file**:
   ```bash
   data/spanish-concepts.json
   ```

3. **Copy skill**:
   ```bash
   cp .claude/skills/russian-learning.md .claude/skills/spanish-learning.md
   ```

4. **Update references**:
   - Change "Russian" → "Spanish"
   - Update file paths
   - Adjust level (A1→B2, etc.)

5. **Invoke**:
   ```bash
   @spanish-learning
   ```

### Adding a New Domain (e.g., Neuroscience)

Same process, but adapt data schema:

```json
// data/neuroscience-concepts.json
{
  "meta": {
    "domain": "neuroscience",
    "focus": "Cellular & systems neuroscience",
    "total_concepts": 120
  },
  "concepts": {
    "action-potential": {
      "id": "action-potential",
      "name": "Action Potential",
      "category": "cellular",
      "prerequisites": ["membrane-potential"],
      "description": "...",
      "examples": ["...", "..."],
      "drills": ["Explain propagation", "Calculate threshold"]
    }
  }
}
```

Skill would conduct Socratic dialogues on neuroscience concepts.

## Development Guide

### File Structure

```
learning-skills/
├── .claude/
│   ├── session-memory.md              # (auto-generated)
│   └── skills/
│       ├── russian-learning.md
│       └── russian-learning/
│           └── scripts/
│               └── state_manager.py
├── data/
│   ├── russian-vocabulary.json        # 1,847 words
│   ├── russian-concepts.json          # 42 concepts
│   └── learner-state.json             # Your progress
├── brainstorm/
│   └── learning.md
├── Makefile                           # Convenience commands
├── README.md
├── QUICKSTART.md
└── CLAUDE.md (this file)
```

### Adding New Features

#### 1. Confidence Calibration Feedback

Track `confidence vs accuracy` over time, provide feedback:

```python
def analyze_calibration(state):
    """
    If confidence > accuracy: Overconfident
    If confidence < accuracy: Underconfident
    """
    # Calculate calibration error
    # Return feedback for Claude
```

#### 2. Multi-Modal Encoding

Generate diagrams, timelines, analogies:

```json
{
  "concept": "genitive-case",
  "modalities": {
    "text": "Genitive expresses possession",
    "visual": "<diagram of case usage>",
    "analogical": "Like English 's or 'of'"
  }
}
```

#### 3. Knowledge Graph

Track prerequisites and dependencies:

```python
def build_knowledge_graph(concepts):
    """
    Nodes: concepts
    Edges: prerequisites

    Returns DAG for optimal learning path
    """
```

### Testing

#### Using Makefile (Recommended)

```bash
# View all available commands
make help

# Test the state manager
make test

# View learning statistics
make stats

# Backup your progress
make backup

# Reset progress (with backup)
make reset-progress
```

#### Manual Testing

```bash
# Test session initialization
python3 .claude/skills/russian-learning/scripts/state_manager.py init-session 10

# Test update
python3 .claude/skills/russian-learning/scripts/state_manager.py update "книга" "words" true 80

# View stats
python3 .claude/skills/russian-learning/scripts/state_manager.py stats
```

#### Unit Tests (Planned)

```python
def test_mastery_update():
    state = init_state()
    update_item_mastery(state, "test", "words", True, 80)
    assert state["words"]["test"]["mastery"] > 0
```

### Performance Optimization

Current implementation is lightweight (JSON reads/writes). For large datasets:

1. **Cache vocabulary in memory** during session
2. **Batch state updates** (write after session, not per interaction)
3. **Index learner state** by next_review for faster due item queries

### Error Handling

State manager should handle:
- Missing data files (create with defaults)
- Corrupted JSON (backup + reinitialize)
- Invalid item IDs (log warning, skip)

## Philosophy

From [brainstorm/learning.md](brainstorm/learning.md):

> "Learning is not information transfer, it's cognitive restructuring. The agent's job is to manage the learner's confusion—keep them in the zone where current schemas are insufficient, but new schemas are constructible."

This system implements that philosophy through:
- **Conversation over flashcards**
- **Production over consumption**
- **Adaptive difficulty over fixed curriculum**
- **Metacognition over passive repetition**

## References

- **Spaced Repetition**: SM-2 algorithm (Wozniak, 1990)
- **Retrieval Practice**: "Make It Stick" (Brown, Roediger, McDaniel)
- **Desirable Difficulty**: Bjork & Bjork (1992)
- **Generative Learning**: Chi et al. (1994)
- **Metacognition**: Dunning-Kruger effect, calibration research

## Publishing

### Creating a Release

Use the Makefile to tag and publish releases:

```bash
# Create a tag only
make tag VERSION=v1.0.0

# Tag and push to remote (full publish)
make publish VERSION=v1.0.0

# Push existing tags
make push-tags
```

### Release Checklist

1. Update version references in documentation
2. Test the state manager: `make test`
3. Commit all changes: `git add . && git commit -m "Release v1.0.0"`
4. Publish: `make publish VERSION=v1.0.0`
5. Create release notes on GitHub

## Contributing

Want to extend this framework?

1. Fork the repository
2. Create domain-specific vocabulary/concepts
3. Copy and adapt a skill
4. Submit a PR with your domain implementation

## Future Work

- [ ] Multi-modal encoding (diagrams, audio)
- [ ] Knowledge graph visualization
- [ ] Confidence calibration feedback
- [ ] Export/import learner state
- [ ] Web-based progress dashboard (optional)
- [ ] Collaborative learning (peer explanations)

---

**Built with**: Claude Code Skills, Python, JSON

**Methodology**: 6 research-backed learning principles

**Philosophy**: Conversation-based cognitive restructuring
