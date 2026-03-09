# Savant Plugin — Design Document

**Date**: 2026-03-09
**Status**: Approved
**Scope**: Upgrade `learning-russian` → `savant`, a publishable multi-language, multi-mode Claude Code learning plugin

---

## Overview

Savant is a Claude Code plugin for language learning. It supports multiple languages and multiple learning modes, invoked as:

```bash
/savant russian words     # spaced repetition vocabulary session
/savant russian echo      # FSI conversational session
/savant korean echo       # same modes, different language
```

---

## Goals

1. **Rename** the project from `learning-russian` to `savant`
2. **Multi-language** — Russian ships bundled; Spanish, Korean, etc. added via language packs
3. **Multi-mode** — `words` (spaced repetition) and `echo` (FSI conversational)
4. **Publishable** — structured as a Claude Code plugin installable from GitHub

---

## Plugin Structure

```
savant/
├── plugin.yaml                      # Plugin metadata (name, version, skills)
├── skills/
│   └── savant.md                    # Single skill, dispatches on {lang} {mode}
├── scripts/
│   ├── state_manager.py             # Shared CLI — all languages & modes
│   ├── words_session.py             # Words mode logic
│   └── echo_session.py              # Echo mode logic
├── languages/
│   ├── README.md                    # How to add a new language (extension guide)
│   └── russian/
│       ├── vocabulary.json          # 350+ words, A1-B1
│       ├── concepts.json            # 42 grammar concepts, A2-B1
│       └── echo-scenarios.json      # FSI roleplay scenarios (new)
└── README.md
```

**User state** lives outside the plugin, at `~/.claude/savant/`:

```
~/.claude/savant/
├── russian-words-state.json         # Mastery tracking, spaced repetition
├── russian-echo-state.json          # Recent scenarios, vocab log
└── korean-words-state.json          # Created when user starts Korean
```

---

## Skill: `savant.md`

Single entry point. Reads `{language} {mode}` from invocation args, dispatches to the appropriate mode logic.

**Dispatch logic:**
- Validates language pack exists at `../languages/{lang}/`
- Validates mode is `words` or `echo`
- Calls `state_manager.py init-session {lang} {mode}`
- Runs the appropriate session (words or echo)

**Error on missing language:**
> "No language pack found for `korean`. To add Korean, see `languages/README.md`."

---

## Mode: Words

Spaced repetition vocabulary and grammar session. Behavior unchanged from current `russian-learning` skill, extended to be language-agnostic.

**Session flow:**
1. `state_manager.py init-session {lang} words 15` — selects due reviews + new items
2. Dialogue loop: translate, produce sentences, explain grammar
3. After each response: record confidence, call `update`
4. Finalize: summary of accuracy, topics, next review dates

**State format** (`~/.claude/savant/russian-words-state.json`):
```json
{
  "meta": { "created": "...", "last_session": "...", "total_sessions": 5 },
  "words": {
    "книга": {
      "mastery": 0.85,
      "review_count": 7,
      "error_count": 1,
      "last_reviewed": "2026-03-09T10:00:00",
      "next_review": "2026-03-16T10:00:00",
      "interval_days": 7
    }
  },
  "concepts": { ... }
}
```

---

## Mode: Echo

FSI Echo conversational session. Light state tracking to avoid repeating recent scenarios.

**Session flow (per FSI-Echo Loop):**
1. `state_manager.py init-session {lang} echo` — picks a scenario not seen recently
2. **Target phrase**: introduce one high-value phrase, literal + natural meaning
3. **Echo phase**: stress-marked phrase, mimic native pronunciation
4. **FSI phase**: 3-4 substitution drills for grammatical muscle memory
5. **Roleplay**: back-and-forth using the new phrase
6. Log any vocabulary introduced mid-session

**Echo scenarios** (`languages/russian/echo-scenarios.json`):
```json
{
  "scenarios": {
    "cafe-meeting": {
      "id": "cafe-meeting",
      "title": "Meeting at a café",
      "level": "A2",
      "tags": ["daily-life", "social"],
      "seed_phrase": "Можно присесть?",
      "seed_meaning": "May I sit down? (lit: Is it possible to sit down?)",
      "substitutions": [
        "Можно войти?",
        "Можно спросить?",
        "Можно позвонить?"
      ],
      "vocabulary": ["присесть", "войти", "спросить"]
    }
  }
}
```

**Echo state** (`~/.claude/savant/russian-echo-state.json`):
```json
{
  "recent_scenarios": ["cafe-meeting", "asking-directions"],
  "echo_vocab_log": [
    { "word": "присесть", "seen": "2026-03-09T10:00:00" }
  ]
}
```

---

## State Manager CLI

All state operations go through `scripts/state_manager.py`. Paths are resolved relative to the script — no hardcoded user paths.

**Words mode:**
```bash
python3 state_manager.py init-session russian words 15
python3 state_manager.py update russian words "книга" true 80
python3 state_manager.py finalize russian words <session_id>
python3 state_manager.py stats russian words
```

**Echo mode:**
```bash
python3 state_manager.py init-session russian echo
python3 state_manager.py log-vocab russian echo "присесть"
python3 state_manager.py stats russian echo
```

---

## Language Extension Guide (summary)

To add a new language (e.g., Korean):

1. Create `languages/korean/vocabulary.json` — follow `languages/russian/vocabulary.json` schema
2. Create `languages/korean/concepts.json` — follow `languages/russian/concepts.json` schema
3. Create `languages/korean/echo-scenarios.json` — follow the echo scenarios schema
4. Run `/savant korean words` — state files are created automatically on first use

No changes to skills or scripts required. Full details in `languages/README.md`.

---

## Migration from `learning-russian`

| Old | New |
|-----|-----|
| `.claude/skills/russian-learning.md` | `skills/savant.md` |
| `.claude/skills/russian-learning/scripts/state_manager.py` | `scripts/state_manager.py` |
| `data/russian-vocabulary.json` | `languages/russian/vocabulary.json` |
| `data/russian-concepts.json` | `languages/russian/concepts.json` |
| `data/learner-state.json` | `~/.claude/savant/russian-words-state.json` |

---

## Out of Scope

- Audio/TTS integration
- Web UI or dashboard
- Multi-user or cloud sync
- SQLite migration (JSON is sufficient for current scale)
