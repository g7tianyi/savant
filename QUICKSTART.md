# Quick Start

## Install

In any Claude Code session:

```
/plugin marketplace add g7tianyi/savant
/plugin install savant@g7tianyi/savant
```

Prerequisites: Python 3 installed on your machine. That's it.

## Start a session

**Vocabulary mode** — spaced repetition, tracks mastery per word and grammar concept:

```
/savant russian words
```

Claude will test recall, ask confidence ratings, explain rules, and adapt difficulty in real time. Progress is saved to `~/.claude/savant/russian-words-state.json`.

**Echo mode** — FSI conversational session, picks a scenario and drills it:

```
/savant russian echo
```

Claude introduces a high-value phrase, runs substitution drills, then does a roleplay. Recently seen scenarios are avoided automatically.

## Check progress

```bash
make stats-words   # words mastered / in progress
make stats-echo    # recent scenarios, vocab logged
```

Or directly:

```bash
python3 scripts/state_manager.py stats russian words
python3 scripts/state_manager.py stats russian echo
```

## What a words session looks like

```
Claude: Translate: "I don't have time"

You: У меня нет время

Claude: Close! нет requires genitive: времени, not время.
        Correct: У меня нет времени

        Confidence (0–100)?

You: 60

Claude: Got it — let's reinforce this. What case always follows нет?
```

## What an echo session looks like

```
Claude: Today's scenario: Meeting at a café
        Seed phrase: Мо́жно присе́сть? (May I sit down?)

        Say it aloud, wait 3 seconds, then repeat from memory.

You: Мо́жно присе́сть

Claude: Good. Now substitutions — same pattern, new slot:
        Мо́жно войти́? / Мо́жно спроси́ть? / Мо́жно позвони́ть?

        [roleplay begins]
        You walk into a busy café. Only one free seat. What do you say?
```

## Adding a language

See [languages/README.md](languages/README.md). Add three JSON files for vocabulary, grammar concepts, and echo scenarios — no code changes needed.
