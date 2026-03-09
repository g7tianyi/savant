# Savant

Savant is a multi-language, multi-mode learning plugin for Claude Code that conducts research-backed vocabulary and conversational sessions using spaced repetition and adaptive dialogue.

## Installation

Install as a Claude Code plugin by referencing `plugin.yaml` in this repository:

```bash
# Local install (from repo root)
claude plugin install .

# Or via registry (once published)
claude plugin install @savant-contributors/savant
```

## Usage

```bash
# Spaced repetition vocabulary session
/savant russian words

# FSI conversational immersion session
/savant russian echo
```

- `/savant russian words` — Vocabulary review using SM-2 spaced repetition; tests recall and tracks mastery per word.
- `/savant russian echo` — FSI-style conversational session that drills grammar and listening through natural dialogue.

## Adding a language

Copy an existing language folder and update its data files. See [languages/README.md](languages/README.md) for details.

## Development

```bash
make test          # Run state manager tests
make stats-words   # Show Russian words progress
make stats-echo    # Show Russian echo progress
```
