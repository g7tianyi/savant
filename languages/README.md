# Language Pack Extension Guide

This guide explains how to add a new language pack to the Savant plugin.

## Overview

Each language pack lives under `languages/<language>/` and consists of exactly three files:

| File | Purpose |
|---|---|
| `vocabulary.json` | Word list with translations, part-of-speech, level, and usage examples |
| `concepts.json` | Grammar and theory concepts with explanations, examples, and drills |
| `echo-scenarios.json` | Real-world conversational scenarios for echo practice |

All three files are required. The state manager and skill definition reference them by the directory name, so the directory must match the language identifier used in the skill file.

## Currently Supported Languages

| Language | Directory | Levels | Words | Concepts | Echo Scenarios |
|---|---|---|---|---|---|
| Russian | `languages/russian/` | A1, A2, B1 | 1,847 | 42 | 10 |

## Step-by-Step: Adding Korean

This walkthrough uses Korean as the example. Substitute the language name and paths for any other target language.

### 1. Create the directory

```bash
mkdir languages/korean
```

### 2. Create `vocabulary.json`

See the full schema below. Minimum: 100 words.

```bash
touch languages/korean/vocabulary.json
```

### 3. Create `concepts.json`

See the full schema below. Minimum: 10 concepts.

```bash
touch languages/korean/concepts.json
```

### 4. Create `echo-scenarios.json`

See the full schema below. Minimum: 10 scenarios.

```bash
touch languages/korean/echo-scenarios.json
```

### 5. Copy and adapt the skill definition

```bash
cp .claude/skills/russian-learning.md .claude/skills/korean-learning.md
```

Open `.claude/skills/korean-learning.md` and update:

- Every reference to "Russian" / "russian" to "Korean" / "korean"
- The target proficiency level (e.g., A1→A2 instead of A2→B1)
- The data file paths (`languages/korean/vocabulary.json`, etc.)
- Any language-specific notes (script name, romanization system, etc.)

### 6. Test the new pack

```bash
python3 scripts/state_manager.py init-session korean words 5
python3 scripts/state_manager.py init-session korean echo
```

Then invoke from Claude Code:

```
@korean-learning
```

---

## File Schemas

### `vocabulary.json`

#### Top-level structure

```json
{
  "meta": { ... },
  "words": { ... }
}
```

#### `meta` object

| Field | Type | Required | Description |
|---|---|---|---|
| `total_words` | integer | yes | Total number of entries in `words` |
| `levels` | array of strings | yes | CEFR levels present, e.g. `["A1", "A2"]` |
| `categories` | array of strings | yes | Semantic categories used across entries |
| `generated` | string (YYYY-MM-DD) | yes | Date the file was created or last regenerated |
| `purpose` | string | yes | One-sentence description of scope and goal |

#### Word entry

Each key in `words` is the word in the target language. The value is an object:

| Field | Type | Required | Description |
|---|---|---|---|
| `<native_script>` | string | yes | The word in the target language (same as the key) |
| `translation` | string | yes | English gloss |
| `pos` | string | yes | Part of speech: `noun`, `verb`, `adjective`, `pronoun`, `adverb`, etc. |
| `level` | string | yes | CEFR level: `A1`, `A2`, `B1`, `B2` |
| `frequency` | integer | yes | Relative frequency rank (1 = most frequent) |
| `category` | string | yes | Must match a value in `meta.categories` |
| `examples` | array of strings | yes | 1-3 example sentences in the target language |
| `gender` | string | no | Grammatical gender where applicable (`masculine`, `feminine`, `neuter`) |
| `notes` | string | no | Short grammatical or usage note |
| `romanization` | string | no | Romanized pronunciation (strongly recommended for non-Latin scripts) |

#### Minimal example — Korean entry

```json
{
  "meta": {
    "total_words": 150,
    "levels": ["A1", "A2"],
    "categories": ["pronouns", "greetings", "food", "numbers", "daily-life"],
    "generated": "2026-03-09",
    "purpose": "A1→A2 Korean vocabulary for practical conversation"
  },
  "words": {
    "나": {
      "native": "나",
      "translation": "I / me (informal)",
      "romanization": "na",
      "pos": "pronoun",
      "level": "A1",
      "frequency": 1,
      "category": "pronouns",
      "examples": [
        "나는 학생이에요. (I am a student.)",
        "나는 한국어를 배워요. (I am learning Korean.)"
      ],
      "notes": "Informal register. Use 저 in formal/polite speech."
    }
  }
}
```

---

### `concepts.json`

#### Top-level structure

```json
{
  "meta": { ... },
  "concepts": { ... }
}
```

#### `meta` object

| Field | Type | Required | Description |
|---|---|---|---|
| `domain` | string | yes | Language name, e.g. `"korean"` |
| `focus` | string | yes | Scope description, e.g. `"A1→A2 grammar essentials"` |
| `total_concepts` | integer | yes | Total number of entries in `concepts` |
| `generated` | string (YYYY-MM-DD) | yes | Creation or regeneration date |

#### Concept entry

Each key in `concepts` is a slug ID. The value is an object:

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Must match the key exactly |
| `name` | string | yes | Human-readable concept name |
| `level` | string | yes | CEFR level |
| `category` | string | yes | e.g. `"grammar"`, `"pronunciation"`, `"pragmatics"` |
| `prerequisites` | array of strings | yes | IDs of concepts that should be understood first (empty array if none) |
| `description` | string | yes | One-to-three sentence explanation of the concept |
| `examples` | array of strings | yes | 2-4 annotated examples with English translations in parentheses |
| `drills` | array of strings | yes | 2-4 practice prompts or transformation tasks |

#### Minimal example — Korean entry

```json
{
  "meta": {
    "domain": "korean",
    "focus": "A1→A2 practical conversation grammar",
    "total_concepts": 15,
    "generated": "2026-03-09"
  },
  "concepts": {
    "topic-marker": {
      "id": "topic-marker",
      "name": "Topic Marker: 은/는",
      "level": "A1",
      "category": "grammar",
      "prerequisites": [],
      "description": "The particles 은 (after a consonant) and 는 (after a vowel) mark the topic of the sentence. The topic is what the sentence is about and is often already known to both speakers.",
      "examples": [
        "저는 학생이에요. (I [topic] am a student.)",
        "고양이는 귀여워요. (The cat [topic] is cute.)"
      ],
      "drills": [
        "Which particle: 저___ 한국어를 공부해요. → 저는",
        "Add the correct topic marker: 사과___ 맛있어요. → 사과는",
        "Explain the difference between 은/는 and 이/가 in your own words."
      ]
    }
  }
}
```

---

### `echo-scenarios.json`

Echo scenarios teach natural spoken patterns through imitation and substitution. Each scenario provides a model phrase, its literal and natural English translations, substitution variants that follow the same pattern, and key vocabulary.

#### Top-level structure

```json
{
  "meta": { ... },
  "scenarios": { ... }
}
```

#### `meta` object

| Field | Type | Required | Description |
|---|---|---|---|
| `language` | string | yes | Language name, e.g. `"korean"` |
| `total_scenarios` | integer | yes | Total number of entries in `scenarios` |
| `levels` | array of strings | yes | CEFR levels present |
| `topics` | array of strings | yes | Thematic tags used across entries |

#### Scenario entry

Each key in `scenarios` is a slug ID:

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Must match the key |
| `title` | string | yes | Short descriptive title |
| `level` | string | yes | CEFR level |
| `tags` | array of strings | yes | Thematic tags; must appear in `meta.topics` |
| `seed_phrase` | string | yes | The model phrase in the target language; include stress marks or tone markers where helpful |
| `seed_meaning` | string | yes | Literal gloss first, then natural English translation |
| `substitutions` | array of strings | yes | 3 phrases that follow the same grammatical pattern |
| `vocabulary` | array of strings | yes | Key words from the seed phrase in `word — gloss` format |
| `romanization` | string | no | Romanized pronunciation of `seed_phrase` (recommended for non-Latin scripts) |

#### Minimal example — Korean entry

```json
{
  "meta": {
    "language": "korean",
    "total_scenarios": 10,
    "levels": ["A1", "A2"],
    "topics": ["greetings", "daily-life", "food", "travel", "social"]
  },
  "scenarios": {
    "cafe-order": {
      "id": "cafe-order",
      "title": "Ordering at a Café",
      "level": "A1",
      "tags": ["daily-life", "food"],
      "seed_phrase": "아메리카노 한 잔 주세요.",
      "romanization": "Amerikano han jan juseyo.",
      "seed_meaning": "Literally: Americano one cup give-please. Natural: One Americano, please.",
      "substitutions": [
        "라떼 한 잔 주세요.",
        "녹차 한 잔 주세요.",
        "물 한 병 주세요."
      ],
      "vocabulary": [
        "한 잔 — one cup/glass",
        "주세요 — please give me",
        "병 — bottle"
      ]
    }
  }
}
```

---

## Testing a New Language Pack

### 1. Validate JSON syntax

```bash
python3 -c "import json; json.load(open('languages/korean/vocabulary.json'))" && echo "OK"
python3 -c "import json; json.load(open('languages/korean/concepts.json'))" && echo "OK"
python3 -c "import json; json.load(open('languages/korean/echo-scenarios.json'))" && echo "OK"
```

### 2. Check entry counts match `meta.total_*`

```bash
python3 - <<'EOF'
import json

vocab = json.load(open("languages/korean/vocabulary.json"))
assert len(vocab["words"]) == vocab["meta"]["total_words"], \
    f"Word count mismatch: {len(vocab['words'])} entries vs {vocab['meta']['total_words']} declared"

concepts = json.load(open("languages/korean/concepts.json"))
assert len(concepts["concepts"]) == concepts["meta"]["total_concepts"], \
    f"Concept count mismatch"

scenarios = json.load(open("languages/korean/echo-scenarios.json"))
assert len(scenarios["scenarios"]) == scenarios["meta"]["total_scenarios"], \
    f"Scenario count mismatch"

print("All counts match.")
EOF
```

### 3. Initialize a session

```bash
python3 scripts/state_manager.py init-session korean words 5
python3 scripts/state_manager.py init-session korean echo
```

### 4. Run an interactive session

Invoke the skill from Claude Code:

```
@korean-learning
```

Walk through at least one full session: answer questions, trigger both correct and incorrect paths, and verify that mastery updates are written to the learner state file.

---

## Quality Checklist

Before submitting a pull request, confirm every item below:

- [ ] At least 100 words in `vocabulary.json`
- [ ] At least 10 concepts in `concepts.json`
- [ ] At least 10 echo scenarios in `echo-scenarios.json`
- [ ] All required fields are present on every entry (see schemas above)
- [ ] `meta.total_words`, `meta.total_concepts`, `meta.total_scenarios` match actual entry counts
- [ ] All concept `id` fields match their key in the `concepts` object
- [ ] All scenario `id` fields match their key in the `scenarios` object
- [ ] `prerequisites` arrays reference only IDs that exist in the same file
- [ ] Example sentences are grammatically correct and include English translations
- [ ] Stress marks included on echo scenario `seed_phrase` (Cyrillic, Greek, etc.) or tone/romanization provided for tonal/non-Latin scripts
- [ ] `romanization` or pronunciation guide included for non-Latin scripts
- [ ] All JSON files parse without errors
- [ ] A corresponding skill file (`.claude/skills/<language>-learning.md`) has been created and references the correct data paths
- [ ] At least one full session tested end-to-end in Claude Code

---

## Contributing

1. Fork the repository on GitHub.
2. Create a branch: `git checkout -b add-korean-language-pack`
3. Add the three data files under `languages/korean/`.
4. Add the skill definition at `.claude/skills/korean-learning.md`.
5. Work through the testing steps above and confirm the quality checklist.
6. Commit your changes:
   ```bash
   git add languages/korean/ .claude/skills/korean-learning.md
   git commit -m "feat: add Korean language pack (A1→A2)"
   ```
7. Open a pull request against `main` with a short description of the language, the target level range, and the word/concept/scenario counts.

Language packs for any natural language are welcome. If you are unsure about grammatical correctness, note in the PR that a native-speaker review would be appreciated.
