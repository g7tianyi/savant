# Savant

Multi-language language learning plugin for Claude Code. Spaced repetition vocabulary and FSI conversational sessions — no servers, no subscriptions, everything local.

## Installation

```
/plugin marketplace add g7tianyi/savant
/plugin install savant@g7tianyi/savant
```

## Usage

```
/savant russian words    — spaced repetition vocabulary + grammar session
/savant russian echo     — FSI conversational session (phrase → echo → drills → roleplay)
```

Your progress is saved locally at `~/.claude/savant/`.

## Adding a language

See [languages/README.md](languages/README.md) — add three JSON files, no code changes needed.

## Development

```bash
make test          # Run state manager tests
make stats-words   # Show Russian words progress
make stats-echo    # Show Russian echo progress
```
