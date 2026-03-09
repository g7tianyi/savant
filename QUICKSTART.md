# Quick Start Guide

Get up and running with Learning Skills in under 5 minutes.

## Prerequisites

- Python 3.x (for state management)
- Claude Code CLI

That's it! No npm, no servers, no deployment.

## Installation

### Option 1: Clone from GitHub

```bash
git clone https://github.com/YOUR_USERNAME/learning-skills.git
cd learning-skills
```

### Option 2: Local Setup (If You Have the Files)

If you already have the project files:

```bash
cd /path/to/learning-skills

# Verify Python is installed
python3 --version

# Check that data files are present
ls data/

# You should see:
# - russian-vocabulary.json
# - russian-concepts.json
# - learner-state.json (will be auto-created if missing)
```

### Verify Installation

Test the state manager:

```bash
# View current stats
python3 .claude/skills/russian-learning/scripts/state_manager.py stats

# Or use the Makefile (if available)
make stats
```

That's it! No dependencies to install, no build steps.

## Start Your First Session

### Option 1: Russian Learning

Start a Russian learning session by invoking the skill:

```bash
@russian-learning
```

Claude will:
1. Initialize a session with vocabulary and grammar concepts
2. Engage you in natural conversation (not flashcards)
3. Ask you to translate, explain, and produce Russian sentences
4. Track your progress automatically in the background
5. Adapt difficulty based on your performance

### Option 2: Check Your Progress

View your learning statistics:

```bash
python3 .claude/skills/russian-learning/scripts/state_manager.py stats
```

Output shows:
- Total sessions completed
- Words/concepts mastered
- Words/concepts in progress

## What to Expect in a Session

1. **Vocabulary Practice** (~10 words)
   - Translate Russian ↔ English
   - Rate your confidence (0-100%)
   - Get corrections with explanations

2. **Grammar Practice** (~5 concepts)
   - Explain grammar rules in your own words
   - Apply concepts to create sentences
   - Learn WHY rules work (not just memorization)

3. **Conversation Mode**
   - Natural dialogue using today's vocabulary/grammar
   - Real-time error correction
   - Contextual learning

## Session Example

```
Claude: Translate to Russian: "I don't have time"

You: У меня нет время

Claude: Close! "нет" requires genitive case.
        время (nominative) → времени (genitive)
        Correct: "У меня нет времени"

        Confidence (0-100%)?

You: 60

Claude: Got it! Let's reinforce genitive case.
        What case follows "нет"?

You: Genitive

Claude: Perfect! Now create a sentence using "нет + genitive"
```

## How It Works

```
@russian-learning (skill invocation)
    ↓
Loads vocabulary + grammar concepts from data/
    ↓
Claude conducts natural conversation
    ↓
Python script tracks mastery (background)
    ↓
Updates data/learner-state.json
```

No servers. No backends. Just conversation + state management.

## Data Files (All Local)

Everything is stored on your machine:

```
data/
├── russian-vocabulary.json    # 1,847 words (A1-B1)
├── russian-concepts.json      # 42 grammar concepts
└── learner-state.json         # Your progress (auto-created)
```

## Tips for Effective Learning

1. **Be honest with confidence ratings** - They help Claude adapt difficulty
2. **Explain in your own words** - Don't just memorize
3. **Ask "why?"** - Claude will provide linguistic/cultural context
4. **Practice regularly** - Spaced repetition works best with consistency
5. **Make mistakes** - They're learning opportunities

## Methodology

Learning Skills implements 6 research-backed methodologies:

1. **Retrieval-First**: Test before teaching (creates knowledge gaps)
2. **Adaptive Difficulty**: Adjusts based on your performance
3. **Metacognitive Tracking**: Monitors confidence calibration
4. **Generative Learning**: Forces active production
5. **Spaced Repetition**: SM-2 algorithm with Bayesian updates
6. **Just-In-Time Elaboration**: Context when needed

Learn more in [brainstorm/learning.md](brainstorm/learning.md)

## Adding More Languages

Want to add Spanish or another language?

1. Create `data/spanish-vocabulary.json`
2. Create `data/spanish-concepts.json`
3. Copy `.claude/skills/russian-learning.md` → `spanish-learning.md`
4. Update references from Russian → Spanish
5. Invoke: `@spanish-learning`

That's it!

## Troubleshooting

### Session not initializing?

Check that data files exist:
```bash
ls -la data/
```

You should see `russian-vocabulary.json` and `russian-concepts.json`.

### Python script errors?

Ensure Python 3.x is installed:
```bash
python3 --version
```

### Progress not saving?

Check `data/learner-state.json` permissions - it should be writable.

## What's Next?

- Read the [README](README.md) for project philosophy
- Explore the [brainstorm](brainstorm/learning.md) for methodology details
- Check [CLAUDE.md](CLAUDE.md) for technical architecture

---

**Ready?** Start learning: `@russian-learning`
