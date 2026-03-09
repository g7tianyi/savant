# Savant — Technical Documentation

Architecture and implementation details for the Savant plugin.

## Architecture

**Minimalist, conversation-based learning** — no backends, no servers, just dialogue.

```
┌─────────────────────────────────────────────────┐
│  Claude Code (Conversation Layer)               │
│  - Invoked as: /savant {language} {mode}        │
└─────────────────────────────────────────────────┘
           ↓                    ↑
┌─────────────────────────────────────────────────┐
│  Skill (skills/savant/SKILL.md)                 │
│  - Parses language + mode args                  │
│  - Dispatches to words or echo protocol         │
└─────────────────────────────────────────────────┘
           ↓                    ↑
┌─────────────────────────────────────────────────┐
│  State Manager (scripts/state_manager.py)       │
│  - init-session: select items for review        │
│  - update: record word/concept interaction      │
│  - log-vocab: record echo vocab                 │
│  - finalize: mark session complete              │
│  - stats: show progress                         │
└─────────────────────────────────────────────────┘
           ↓                    ↑
┌─────────────────────────────────────────────────┐
│  Data Layer (JSON)                              │
│  - languages/{lang}/vocabulary.json             │
│  - languages/{lang}/concepts.json               │
│  - languages/{lang}/echo-scenarios.json         │
│  - ~/.claude/savant/{lang}-{mode}-state.json    │
└─────────────────────────────────────────────────┘
```

## File Structure

```
savant/
├── .claude-plugin/
│   └── marketplace.json          # Plugin registry declaration
├── plugin.yaml                   # Plugin metadata
├── skills/
│   └── savant/
│       └── SKILL.md              # Single skill, dispatches on {lang} {mode}
├── scripts/
│   ├── state_manager.py          # CLI state manager (all languages, both modes)
│   └── test_state_manager.py     # 8 tests
└── languages/
    ├── README.md                 # How to add a new language
    └── russian/
        ├── vocabulary.json       # 350+ words, A1-B1
        ├── concepts.json         # 42 grammar concepts, A2-B1
        └── echo-scenarios.json   # 10 FSI roleplay scenarios
```

User state is stored outside the plugin at `~/.claude/savant/`:
- `russian-words-state.json` — mastery, spaced repetition schedule
- `russian-echo-state.json` — recent scenarios, vocab log

## State Manager CLI

```bash
python3 scripts/state_manager.py init-session <lang> <mode> [count]
python3 scripts/state_manager.py update <lang> <item_type> <item_id> <correct> <confidence>
python3 scripts/state_manager.py log-vocab <lang> echo <word>
python3 scripts/state_manager.py finalize <lang> <mode> <session_id> [scenario_id]
python3 scripts/state_manager.py stats <lang> <mode>
```

Language packs are resolved at `../languages/{lang}/` relative to the script.
State files default to `~/.claude/savant/`; override with `$SAVANT_STATE_DIR`.

## Learning Modes

### words
Spaced repetition session over vocabulary and grammar concepts.

- SM-2 scheduling: interval × 2.5 on correct, reset to 1 day on error (1–90 day range)
- Bayesian mastery update: correct → +0.1–0.15, incorrect → −0.15
- Confidence-weighted: higher confidence + correct = larger mastery gain
- Mastered threshold: mastery ≥ 0.8

### echo
FSI-Echo conversational session using pre-defined scenarios.

- Picks a scenario not seen in the last 5 sessions
- FSI-Echo loop: target phrase → echo phase → substitution drills → roleplay
- Light state: tracks recent_scenarios[] and echo_vocab_log[]

## Data Schemas

### vocabulary.json
```json
{
  "meta": { "language": "russian", "total_words": 350, "levels": ["A1","A2","B1"] },
  "words": {
    "книга": {
      "russian": "книга", "translation": "book", "pos": "noun",
      "gender": "feminine", "level": "A1", "frequency": 2,
      "category": "daily-life", "examples": ["читать книгу"],
      "declension": { "nominative": "книга", "genitive": "книги", ... }
    }
  }
}
```

### concepts.json
```json
{
  "meta": { "domain": "russian", "focus": "A2→B1 grammar", "total_concepts": 42 },
  "concepts": {
    "genitive-possession": {
      "id": "genitive-possession", "name": "Genitive Case: Possession",
      "level": "A2", "category": "grammar",
      "prerequisites": ["nominative-case"],
      "description": "...", "examples": ["..."], "drills": ["..."]
    }
  }
}
```

### echo-scenarios.json
```json
{
  "meta": { "language": "russian", "total_scenarios": 10 },
  "scenarios": {
    "cafe-meeting": {
      "id": "cafe-meeting", "title": "Meeting at a café",
      "level": "A2", "tags": ["daily-life", "social"],
      "seed_phrase": "Мо́жно присе́сть?",
      "seed_meaning": "May I sit down?",
      "substitutions": ["Мо́жно войти́?", "..."],
      "vocabulary": ["присе́сть", "..."]
    }
  }
}
```

## Learning Algorithms

See [brainstorm/learning.md](brainstorm/learning.md) for full methodology.

Six principles implemented:

1. **Retrieval-First** — test before teaching; knowledge gaps prime attention
2. **Adaptive Cognitive Load** — 3+ errors → simplify; breezing → increase challenge
3. **Generative Learning** — force production over passive recognition
4. **Metacognitive Tracking** — confidence calibration after every response
5. **Just-In-Time Elaboration** — basic → contrastive → causal across review cycles
6. **Social-Cognitive Simulation** — "explain to a friend", roleplay, debate

## Installation

```
/plugin marketplace add g7tianyi/savant
/plugin install savant@g7tianyi/savant
```

## Extending

To add a new language: see [languages/README.md](languages/README.md).
No code changes needed — add three JSON files and the skill works immediately.

## Publishing

```bash
# Tag a release
git tag v0.1.0
git push origin v0.1.0
```

Update `version` in both `plugin.yaml` and `.claude-plugin/marketplace.json`.
