# Savant Plugin Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade `learning-russian` to `savant` — a publishable multi-language, multi-mode Claude Code learning plugin with `words` (spaced repetition) and `echo` (FSI conversational) modes.

**Architecture:** Single `savant.md` skill dispatches on `{language} {mode}` args. Language content lives in `languages/{lang}/` (vocabulary, concepts, echo-scenarios). User state lives in `~/.claude/savant/{lang}-{mode}-state.json`. One shared `state_manager.py` handles all languages and modes.

**Tech Stack:** Python 3 (stdlib only), JSON, Claude Code Skills plugin format

---

## Task 1: Restructure the repo

Rename and reorganize all files to match the new plugin layout. No logic changes yet — just moves.

**Files:**
- Create: `languages/russian/` (directory)
- Create: `languages/README.md`
- Create: `scripts/` (directory)
- Move: `data/russian-vocabulary.json` → `languages/russian/vocabulary.json`
- Move: `data/russian-concepts.json` → `languages/russian/concepts.json`
- Move: `.claude/skills/russian-learning/scripts/state_manager.py` → `scripts/state_manager.py`
- Delete: `.claude/skills/russian-learning.md`
- Delete: `.claude/skills/russian-learning/` (old dir)
- Delete: `data/learner-state.json` (state moves to `~/.claude/savant/`)
- Delete: `data/` (now empty)

**Step 1: Move language data files**

```bash
mkdir -p languages/russian scripts
mv data/russian-vocabulary.json languages/russian/vocabulary.json
mv data/russian-concepts.json languages/russian/concepts.json
mv .claude/skills/russian-learning/scripts/state_manager.py scripts/state_manager.py
```

**Step 2: Remove old files**

```bash
rm -rf .claude/skills/russian-learning.md .claude/skills/russian-learning data/
```

**Step 3: Verify structure**

```bash
ls languages/russian/   # vocabulary.json  concepts.json
ls scripts/             # state_manager.py
```

**Step 4: Commit**

```bash
git add -A
git commit -m "refactor: restructure repo for savant plugin layout"
```

---

## Task 2: Create `languages/russian/echo-scenarios.json`

New file. Provides FSI roleplay scenarios for Russian echo mode. Start with 10 scenarios covering daily life, travel, and social/dating topics.

**Files:**
- Create: `languages/russian/echo-scenarios.json`

**Step 1: Create the file**

```json
{
  "meta": {
    "language": "russian",
    "total_scenarios": 10,
    "levels": ["A2", "B1"],
    "topics": ["daily-life", "travel", "social", "dating"]
  },
  "scenarios": {
    "cafe-meeting": {
      "id": "cafe-meeting",
      "title": "Meeting at a café",
      "level": "A2",
      "tags": ["daily-life", "social"],
      "seed_phrase": "Мо́жно присе́сть?",
      "seed_meaning": "May I sit down? (lit: Is it possible to sit down?)",
      "substitutions": [
        "Мо́жно войти́?",
        "Мо́жно спроси́ть?",
        "Мо́жно позвони́ть?"
      ],
      "vocabulary": ["присе́сть", "войти́", "спроси́ть"]
    },
    "asking-directions": {
      "id": "asking-directions",
      "title": "Asking for directions",
      "level": "A2",
      "tags": ["travel", "daily-life"],
      "seed_phrase": "Как пройти́ до метро́?",
      "seed_meaning": "How do I get to the metro?",
      "substitutions": [
        "Как пройти́ до аэропо́рта?",
        "Как пройти́ до го́стиницы?",
        "Как пройти́ до рестора́на?"
      ],
      "vocabulary": ["пройти́", "метро́", "аэропо́рт", "го́стиница"]
    },
    "complimenting": {
      "id": "complimenting",
      "title": "Giving a compliment",
      "level": "A2",
      "tags": ["social", "dating"],
      "seed_phrase": "Ты о́чень краси́вая.",
      "seed_meaning": "You are very beautiful. (to a woman)",
      "substitutions": [
        "Ты о́чень интере́сная.",
        "У тебя́ о́чень краси́вые глаза́.",
        "Ты о́чень у́мная."
      ],
      "vocabulary": ["краси́вая", "интере́сная", "глаза́", "у́мная"]
    },
    "ordering-food": {
      "id": "ordering-food",
      "title": "Ordering at a restaurant",
      "level": "A2",
      "tags": ["daily-life", "travel"],
      "seed_phrase": "Я бы хоте́л зака́зать...",
      "seed_meaning": "I would like to order... (male speaker)",
      "substitutions": [
        "Я бы хоте́ла зака́зать... (female)",
        "Мо́жно мне борщ?",
        "Что вы реко́мендуете?"
      ],
      "vocabulary": ["зака́зать", "реко́мендовать", "борщ", "меню́"]
    },
    "phone-number": {
      "id": "phone-number",
      "title": "Asking for someone's number",
      "level": "A2",
      "tags": ["social", "dating"],
      "seed_phrase": "Да́й мне свой но́мер телефо́на.",
      "seed_meaning": "Give me your phone number. (informal)",
      "substitutions": [
        "Мо́жно твой но́мер?",
        "Как с тобо́й связа́ться?",
        "Ты есть в Telegram?"
      ],
      "vocabulary": ["но́мер", "телефо́н", "связа́ться", "Telegram"]
    },
    "making-plans": {
      "id": "making-plans",
      "title": "Making plans to meet",
      "level": "A2",
      "tags": ["social", "dating"],
      "seed_phrase": "Ты свобо́ден в пя́тницу?",
      "seed_meaning": "Are you free on Friday? (to a man)",
      "substitutions": [
        "Ты свобо́дна в пя́тницу? (to a woman)",
        "Что ты де́лаешь в су́бботу?",
        "Пойдём куда́-нибудь вме́сте?"
      ],
      "vocabulary": ["свобо́ден", "пя́тница", "суббо́та", "вме́сте"]
    },
    "at-the-airport": {
      "id": "at-the-airport",
      "title": "At the airport",
      "level": "A2",
      "tags": ["travel"],
      "seed_phrase": "Где регистра́ция на рейс?",
      "seed_meaning": "Where is check-in?",
      "substitutions": [
        "Где мой вы́ход на поса́дку?",
        "Когда́ поса́дка?",
        "Мой рейс задержа́лся."
      ],
      "vocabulary": ["регистра́ция", "рейс", "поса́дка", "задержа́ться"]
    },
    "at-the-hotel": {
      "id": "at-the-hotel",
      "title": "Checking into a hotel",
      "level": "B1",
      "tags": ["travel"],
      "seed_phrase": "У меня́ забронирован но́мер.",
      "seed_meaning": "I have a room booked.",
      "substitutions": [
        "На фами́лию Смит.",
        "Мо́жно ра́нний заезд?",
        "Когда́ расчётный час?"
      ],
      "vocabulary": ["забронировать", "но́мер", "заезд", "расчётный час"]
    },
    "talking-about-yourself": {
      "id": "talking-about-yourself",
      "title": "Talking about yourself",
      "level": "A2",
      "tags": ["social", "daily-life"],
      "seed_phrase": "Я рабо́таю в сфе́ре IT.",
      "seed_meaning": "I work in IT.",
      "substitutions": [
        "Я у́чусь в университе́те.",
        "Я из Аме́рики, но живу́ в Москве́.",
        "Я изуча́ю ру́сский язы́к уже́ год."
      ],
      "vocabulary": ["рабо́тать", "у́читься", "изуча́ть", "язы́к"]
    },
    "expressing-interest": {
      "id": "expressing-interest",
      "title": "Expressing interest in someone",
      "level": "B1",
      "tags": ["social", "dating"],
      "seed_phrase": "Ты о́чень интере́сный челове́к.",
      "seed_meaning": "You are a very interesting person. (to a man)",
      "substitutions": [
        "Мне нра́вится, как ты ду́маешь.",
        "С тобо́й о́чень прия́тно разгова́ривать.",
        "Я бы хоте́л узна́ть тебя́ лу́чше."
      ],
      "vocabulary": ["интере́сный", "нра́виться", "разгова́ривать", "узна́ть"]
    }
  }
}
```

**Step 2: Commit**

```bash
git add languages/russian/echo-scenarios.json
git commit -m "feat: add Russian FSI echo scenarios (10 scenarios)"
```

---

## Task 3: Rewrite `scripts/state_manager.py`

Extend the existing state manager to support multiple languages and both modes. Key changes:
- All commands now take `{lang} {mode}` as first two args
- State files live at `~/.claude/savant/{lang}-{mode}-state.json`
- Language packs resolved relative to script location: `../languages/{lang}/`
- New `log-vocab` command for echo mode
- New echo state structure (recent_scenarios, echo_vocab_log)

**Files:**
- Modify: `scripts/state_manager.py`

**Step 1: Write tests first** (create `scripts/test_state_manager.py`)

```python
#!/usr/bin/env python3
"""Tests for state_manager.py"""
import json
import subprocess
import tempfile
import os
from pathlib import Path


SCRIPT = Path(__file__).parent / "state_manager.py"


def run(args, env_override=None):
    env = os.environ.copy()
    if env_override:
        env.update(env_override)
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True, text=True, env=env
    )
    return result


def test_init_session_words(tmp_path):
    """init-session russian words returns words and concepts"""
    env = {"SAVANT_STATE_DIR": str(tmp_path)}
    result = run(["init-session", "russian", "words", "10"], env)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert "words" in data
    assert "concepts" in data
    assert "session_id" in data
    print("PASS: test_init_session_words")


def test_update_words(tmp_path):
    """update records interaction and creates state file"""
    env = {"SAVANT_STATE_DIR": str(tmp_path)}
    run(["init-session", "russian", "words", "5"], env)
    result = run(["update", "russian", "words", "книга", "true", "80"], env)
    assert result.returncode == 0, result.stderr
    state_file = tmp_path / "russian-words-state.json"
    assert state_file.exists()
    state = json.loads(state_file.read_text())
    assert "книга" in state["words"]
    assert state["words"]["книга"]["mastery"] > 0
    print("PASS: test_update_words")


def test_init_session_echo(tmp_path):
    """init-session russian echo returns a scenario"""
    env = {"SAVANT_STATE_DIR": str(tmp_path)}
    result = run(["init-session", "russian", "echo"], env)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert "scenario" in data
    assert "seed_phrase" in data["scenario"]
    print("PASS: test_init_session_echo")


def test_echo_avoids_recent(tmp_path):
    """echo mode does not repeat recently seen scenarios"""
    env = {"SAVANT_STATE_DIR": str(tmp_path)}
    seen = set()
    # Run enough sessions to detect no immediate repeats
    for _ in range(5):
        result = run(["init-session", "russian", "echo"], env)
        data = json.loads(result.stdout)
        scenario_id = data["scenario"]["id"]
        # finalize to mark as seen
        run(["finalize", "russian", "echo", data["session_id"]], env)
        seen.add(scenario_id)
    # After 5 sessions we should have seen 5 different scenarios
    assert len(seen) == 5, f"Expected 5 unique scenarios, got {seen}"
    print("PASS: test_echo_avoids_recent")


def test_log_vocab(tmp_path):
    """log-vocab adds word to echo vocab log"""
    env = {"SAVANT_STATE_DIR": str(tmp_path)}
    result = run(["log-vocab", "russian", "echo", "присесть"], env)
    assert result.returncode == 0, result.stderr
    state_file = tmp_path / "russian-echo-state.json"
    state = json.loads(state_file.read_text())
    words = [e["word"] for e in state["echo_vocab_log"]]
    assert "присесть" in words
    print("PASS: test_log_vocab")


def test_missing_language(tmp_path):
    """init-session with unknown language exits non-zero with clear message"""
    env = {"SAVANT_STATE_DIR": str(tmp_path)}
    result = run(["init-session", "klingon", "words"], env)
    assert result.returncode != 0
    assert "klingon" in result.stderr.lower() or "klingon" in result.stdout.lower()
    print("PASS: test_missing_language")


def test_stats_words(tmp_path):
    """stats returns structured summary"""
    env = {"SAVANT_STATE_DIR": str(tmp_path)}
    run(["update", "russian", "words", "книга", "true", "80"], env)
    result = run(["stats", "russian", "words"], env)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "words" in data
    assert "total_sessions" in data
    print("PASS: test_stats_words")


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        test_init_session_words(tmp_path)
        test_update_words(tmp_path)
        test_init_session_echo(tmp_path)
        test_echo_avoids_recent(tmp_path)
        test_log_vocab(tmp_path)
        test_missing_language(tmp_path)
        test_stats_words(tmp_path)
        print("\nAll tests passed.")
```

**Step 2: Run tests — expect all failures (script not yet updated)**

```bash
python3 scripts/test_state_manager.py
```

Expected: errors about missing args / wrong behavior.

**Step 3: Rewrite `scripts/state_manager.py`**

```python
#!/usr/bin/env python3
"""
State Manager for Savant Plugin

Handles all languages and modes (words, echo).
- Language packs: {script_dir}/../languages/{lang}/
- User state:     $SAVANT_STATE_DIR/{lang}-{mode}-state.json
                  (defaults to ~/.claude/savant/)

Usage:
  state_manager.py init-session <lang> <mode> [count]
  state_manager.py update <lang> words <item_id> <correct> <confidence>
  state_manager.py log-vocab <lang> echo <word>
  state_manager.py finalize <lang> <mode> <session_id>
  state_manager.py stats <lang> <mode>
"""

import json
import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LANGUAGES_DIR = SCRIPT_DIR.parent / "languages"
SAVANT_STATE_DIR = Path(os.environ.get("SAVANT_STATE_DIR", Path.home() / ".claude" / "savant"))

MODES = {"words", "echo"}


# ── Path helpers ──────────────────────────────────────────────────────────────

def lang_dir(lang: str) -> Path:
    return LANGUAGES_DIR / lang


def state_file(lang: str, mode: str) -> Path:
    SAVANT_STATE_DIR.mkdir(parents=True, exist_ok=True)
    return SAVANT_STATE_DIR / f"{lang}-{mode}-state.json"


def validate_lang(lang: str):
    if not lang_dir(lang).exists():
        print(f"Error: No language pack found for '{lang}'. "
              f"See languages/README.md to add it.", file=sys.stderr)
        sys.exit(1)


# ── JSON I/O ──────────────────────────────────────────────────────────────────

def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_json(data: dict):
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ── Words mode ────────────────────────────────────────────────────────────────

def init_words_state() -> dict:
    return {
        "meta": {"created": datetime.now().isoformat(), "last_session": None, "total_sessions": 0},
        "words": {},
        "concepts": {}
    }


def get_due_items(state: dict, item_type: str) -> list:
    now = datetime.now()
    due = []
    for item_id, item_data in state.get(item_type, {}).items():
        next_review = item_data.get("next_review")
        if not next_review or datetime.fromisoformat(next_review) <= now:
            due.append(item_id)
    return due


def get_new_items(state: dict, all_items: list, item_type: str, limit: int) -> list:
    seen = set(state.get(item_type, {}).keys())
    unseen = [i for i in all_items if i not in seen]
    return random.sample(unseen, min(limit, len(unseen)))


def init_session_words(lang: str, count: int) -> dict:
    vocab = load_json(lang_dir(lang) / "vocabulary.json")
    concepts_data = load_json(lang_dir(lang) / "concepts.json")
    sf = state_file(lang, "words")
    state = load_json(sf) if sf.exists() else init_words_state()

    all_words = list(vocab.get("words", {}).keys())
    all_concepts = list(concepts_data.get("concepts", {}).keys())

    due_words = get_due_items(state, "words")
    due_concepts = get_due_items(state, "concepts")
    new_words = get_new_items(state, all_words, "words", limit=5)
    new_concepts = get_new_items(state, all_concepts, "concepts", limit=3)

    selected_words = (due_words[:10] + new_words)[:max(1, count // 2)]
    selected_concepts = (due_concepts[:5] + new_concepts)[:max(1, count // 3)]

    return {
        "session_id": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "lang": lang,
        "mode": "words",
        "words": selected_words,
        "concepts": selected_concepts,
        "stats": {
            "due_words": len(due_words),
            "due_concepts": len(due_concepts),
            "new_words": len(new_words),
            "new_concepts": len(new_concepts)
        }
    }


def update_words(lang: str, item_id: str, item_type: str, correct: bool, confidence: int):
    sf = state_file(lang, "words")
    state = load_json(sf) if sf.exists() else init_words_state()

    if item_type not in state:
        state[item_type] = {}
    if item_id not in state[item_type]:
        state[item_type][item_id] = {
            "mastery": 0.0, "review_count": 0, "error_count": 0,
            "last_reviewed": None, "next_review": None, "interval_days": 1
        }

    item = state[item_type][item_id]
    if correct:
        item["mastery"] = min(1.0, item["mastery"] + 0.1 * (1 + confidence / 200))
        item["interval_days"] = min(90, item["interval_days"] * 2.5)
    else:
        item["mastery"] = max(0.0, item["mastery"] - 0.15)
        item["interval_days"] = 1

    item["review_count"] += 1
    if not correct:
        item["error_count"] += 1
    item["last_reviewed"] = datetime.now().isoformat()
    item["next_review"] = (datetime.now() + timedelta(days=item["interval_days"])).isoformat()

    save_json(sf, state)


def finalize_words(lang: str, session_id: str):
    sf = state_file(lang, "words")
    state = load_json(sf) if sf.exists() else init_words_state()
    state["meta"]["last_session"] = datetime.now().isoformat()
    state["meta"]["total_sessions"] = state["meta"].get("total_sessions", 0) + 1
    save_json(sf, state)


def stats_words(lang: str) -> dict:
    sf = state_file(lang, "words")
    state = load_json(sf) if sf.exists() else init_words_state()
    total_words = len(state.get("words", {}))
    mastered_words = sum(1 for w in state.get("words", {}).values() if w.get("mastery", 0) >= 0.8)
    total_concepts = len(state.get("concepts", {}))
    mastered_concepts = sum(1 for c in state.get("concepts", {}).values() if c.get("mastery", 0) >= 0.8)
    return {
        "lang": lang, "mode": "words",
        "total_sessions": state["meta"].get("total_sessions", 0),
        "last_session": state["meta"].get("last_session", "Never"),
        "words": {"total": total_words, "mastered": mastered_words, "in_progress": total_words - mastered_words},
        "concepts": {"total": total_concepts, "mastered": mastered_concepts, "in_progress": total_concepts - mastered_concepts}
    }


# ── Echo mode ─────────────────────────────────────────────────────────────────

ECHO_WINDOW = 5  # avoid repeating last N scenarios


def init_echo_state() -> dict:
    return {"recent_scenarios": [], "echo_vocab_log": []}


def init_session_echo(lang: str) -> dict:
    scenarios_data = load_json(lang_dir(lang) / "echo-scenarios.json")
    all_scenarios = scenarios_data.get("scenarios", {})
    sf = state_file(lang, "echo")
    state = load_json(sf) if sf.exists() else init_echo_state()

    recent = set(state.get("recent_scenarios", [])[-ECHO_WINDOW:])
    available = [sid for sid in all_scenarios if sid not in recent]
    if not available:
        available = list(all_scenarios.keys())  # all seen — reset

    chosen_id = random.choice(available)
    chosen = all_scenarios[chosen_id]

    return {
        "session_id": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "lang": lang,
        "mode": "echo",
        "scenario": chosen
    }


def log_vocab_echo(lang: str, word: str):
    sf = state_file(lang, "echo")
    state = load_json(sf) if sf.exists() else init_echo_state()
    state.setdefault("echo_vocab_log", []).append({
        "word": word,
        "seen": datetime.now().isoformat()
    })
    save_json(sf, state)


def finalize_echo(lang: str, session_id: str, scenario_id: str = None):
    sf = state_file(lang, "echo")
    state = load_json(sf) if sf.exists() else init_echo_state()
    if scenario_id:
        recent = state.get("recent_scenarios", [])
        recent.append(scenario_id)
        state["recent_scenarios"] = recent[-ECHO_WINDOW * 2:]  # keep rolling window
    save_json(sf, state)


def stats_echo(lang: str) -> dict:
    sf = state_file(lang, "echo")
    state = load_json(sf) if sf.exists() else init_echo_state()
    return {
        "lang": lang, "mode": "echo",
        "recent_scenarios": state.get("recent_scenarios", []),
        "vocab_logged": len(state.get("echo_vocab_log", [])),
        "echo_vocab_log": state.get("echo_vocab_log", [])[-10:]  # last 10
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def usage():
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        usage()

    cmd = args[0]

    if cmd == "init-session":
        if len(args) < 3:
            usage()
        lang, mode = args[1], args[2]
        validate_lang(lang)
        if mode == "words":
            count = int(args[3]) if len(args) > 3 else 15
            print_json(init_session_words(lang, count))
        elif mode == "echo":
            print_json(init_session_echo(lang))
        else:
            print(f"Unknown mode: {mode}. Use 'words' or 'echo'.", file=sys.stderr)
            sys.exit(1)

    elif cmd == "update":
        # update <lang> words <item_id> <correct> <confidence>
        if len(args) < 6:
            usage()
        lang, mode, item_id = args[1], args[2], args[3]
        validate_lang(lang)
        if mode == "words":
            correct = args[4].lower() == "true"
            confidence = int(args[5])
            update_words(lang, item_id, "words", correct, confidence)
            print(f"Updated {lang}/words: {item_id}")
        else:
            print(f"'update' is for words mode. Use 'log-vocab' for echo.", file=sys.stderr)
            sys.exit(1)

    elif cmd == "log-vocab":
        # log-vocab <lang> echo <word>
        if len(args) < 4:
            usage()
        lang, mode, word = args[1], args[2], args[3]
        validate_lang(lang)
        log_vocab_echo(lang, word)
        print(f"Logged vocab: {word}")

    elif cmd == "finalize":
        # finalize <lang> <mode> <session_id> [scenario_id]
        if len(args) < 4:
            usage()
        lang, mode, session_id = args[1], args[2], args[3]
        validate_lang(lang)
        if mode == "words":
            finalize_words(lang, session_id)
        elif mode == "echo":
            scenario_id = args[4] if len(args) > 4 else None
            finalize_echo(lang, session_id, scenario_id)
        print(f"Finalized {lang}/{mode} session {session_id}")

    elif cmd == "stats":
        if len(args) < 3:
            usage()
        lang, mode = args[1], args[2]
        validate_lang(lang)
        if mode == "words":
            print_json(stats_words(lang))
        elif mode == "echo":
            print_json(stats_echo(lang))

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        usage()
```

**Step 4: Run tests — all should pass**

```bash
python3 scripts/test_state_manager.py
```

Expected output:
```
PASS: test_init_session_words
PASS: test_update_words
PASS: test_init_session_echo
PASS: test_echo_avoids_recent
PASS: test_log_vocab
PASS: test_missing_language
PASS: test_stats_words

All tests passed.
```

**Step 5: Commit**

```bash
git add scripts/state_manager.py scripts/test_state_manager.py
git commit -m "feat: rewrite state_manager for multi-language, multi-mode support"
```

---

## Task 4: Create `skills/savant.md`

The single skill entry point. Reads `{language} {mode}` from the invocation, validates them, then runs the appropriate session protocol.

**Files:**
- Create: `skills/savant.md`
- Delete: (old `.claude/skills/russian-learning.md` — already done in Task 1)

**Step 1: Create `skills/savant.md`**

````markdown
# Savant — Language Learning Skill

You are Savant, a language learning tutor. You are invoked as:

```
/savant {language} {mode}
```

Examples: `/savant russian words`, `/savant korean echo`

## Step 1: Parse Arguments

Extract `{language}` and `{mode}` from the invocation. If missing or invalid, respond:

> "Usage: `/savant {language} {mode}`
> Modes: `words` (vocabulary), `echo` (FSI conversational)
> Example: `/savant russian words`"

## Step 2: Validate Language Pack

Run:
```bash
python3 {PLUGIN_DIR}/scripts/state_manager.py init-session {language} {mode}
```

If it exits non-zero (language pack missing), relay the error message to the user and stop.

## Step 3: Dispatch to Mode

### If mode = `words`

Follow the **Words Session Protocol** below.

### If mode = `echo`

Follow the **Echo Session Protocol** below.

---

## Words Session Protocol

### Initialize

```bash
python3 {PLUGIN_DIR}/scripts/state_manager.py init-session {lang} words 15
```

Returns `session_id`, `words[]`, `concepts[]`. Load vocabulary details from `{PLUGIN_DIR}/languages/{lang}/vocabulary.json` and `concepts.json`.

### Session Loop

Mix vocabulary and grammar in natural conversation. For each item:

1. Present a challenge (varied drill types — see Quick Reference below)
2. User responds
3. Ask confidence: "Confidence (0–100%)?"
4. Provide feedback + explanation of WHY
5. Update state silently:
   ```bash
   python3 {PLUGIN_DIR}/scripts/state_manager.py update {lang} words "{item_id}" {true/false} {confidence}
   ```

### Adaptive Difficulty

- 3+ consecutive errors → simplify (hints, sub-steps, worked examples)
- Breezing through → increase challenge (free production, no hints, edge cases)

### Finalize

```bash
python3 {PLUGIN_DIR}/scripts/state_manager.py finalize {lang} words {session_id}
python3 {PLUGIN_DIR}/scripts/state_manager.py stats {lang} words
```

Show summary: accuracy, topics covered, mastered items, next review schedule.

### Words Quick Reference — Drill Types

1. **Translate** (recognition): "Translate: I don't have time"
2. **Reverse translate** (production): "How do you say 'I don't have time'?"
3. **Fill blank**: "У меня ___ времени"
4. **Correct error**: "У меня нет время → fix it"
5. **Explain**: "Why genitive after нет?"
6. **Produce**: "Create a sentence using genitive of negation"
7. **Compare-contrast**: "Explain difference: читал vs прочитал"

---

## Echo Session Protocol

### Initialize

```bash
python3 {PLUGIN_DIR}/scripts/state_manager.py init-session {lang} echo
```

Returns `session_id` and `scenario` (id, title, seed_phrase, seed_meaning, substitutions, vocabulary).

### The FSI-Echo Loop

Follow this sequence for the chosen scenario:

**1. Target Phrase**
Introduce the `seed_phrase`. Explain literal meaning and natural usage. Include stress marks.

**2. Echo Phase**
Present the phrase with stress marks. Ask the user to:
- Hear it (native TTS if available, or imagine native pronunciation)
- Wait 3 seconds (the "Echo")
- Mimic it out loud
- Type what they said / how it felt

**3. FSI Substitution Drills**
Run through `substitutions[]` one by one. For each:
- Present the substitution
- User repeats / adapts
- Brief feedback on form

**4. Roleplay**
Initiate a short back-and-forth roleplay using the scenario topic. User must use the seed phrase or its substitutions naturally.

### Vocabulary Tracking

Introduce 2–3 words from `vocabulary[]` during the session. Log each silently:
```bash
python3 {PLUGIN_DIR}/scripts/state_manager.py log-vocab {lang} echo "{word}"
```

Spontaneously test recalled words in later turns.

### Correction Protocol

If the user makes a grammatical error: correct it briefly FIRST, then reply to the content.

### Finalize

```bash
python3 {PLUGIN_DIR}/scripts/state_manager.py finalize {lang} echo {session_id} {scenario_id}
python3 {PLUGIN_DIR}/scripts/state_manager.py stats {lang} echo
```

Show summary: scenario covered, vocabulary logged, next session preview.

---

## Shared Principles (Both Modes)

- **Retrieval-first**: Test before teaching. Ask what they think before explaining.
- **Generative learning**: Force production ("create a sentence", "explain to a friend").
- **Metacognitive tracking**: Always ask confidence after each response.
- **Just-in-time elaboration**: Don't dump context upfront. Add depth on repeat reviews.
- **Natural tone**: Supportive, not robotic. "Close!", "Almost!", "Exactly!"
- **Explain WHY**: Grammar rules, cultural context, usage notes — not just correct/wrong.
````

**Step 2: Commit**

```bash
git add skills/savant.md
git commit -m "feat: add savant.md skill with words and echo mode dispatch"
```

---

## Task 5: Create `plugin.yaml`

Plugin metadata file that makes this installable as a Claude Code plugin.

**Files:**
- Create: `plugin.yaml`

**Step 1: Create `plugin.yaml`**

```yaml
name: savant
version: 0.1.0
description: >
  Multi-language, multi-mode language learning plugin for Claude Code.
  Supports spaced repetition vocabulary (words mode) and FSI conversational
  training (echo mode). Ships with Russian; extensible to any language.

skills:
  - name: savant
    file: skills/savant.md
    description: >
      Language learning session. Usage: /savant {language} {mode}
      Modes: words (spaced repetition), echo (FSI conversational)
    triggers:
      - "savant"
      - "learn language"
      - "language practice"

repository: https://github.com/{your-username}/savant
author: {your-username}
license: MIT
```

**Step 2: Commit**

```bash
git add plugin.yaml
git commit -m "feat: add plugin.yaml for Claude Code plugin packaging"
```

---

## Task 6: Create `languages/README.md` — Extension Guide

Documents exactly how to add a new language pack. This is the community contribution guide.

**Files:**
- Create: `languages/README.md`

**Step 1: Create `languages/README.md`**

````markdown
# Savant Language Packs

This directory contains language packs for the Savant plugin. Each language is a subdirectory with three JSON files.

## Adding a New Language

To add Korean (for example):

### 1. Create the directory

```bash
mkdir languages/korean
```

### 2. Create `vocabulary.json`

Follow this schema exactly. Copy `languages/russian/vocabulary.json` as a template.

```json
{
  "meta": {
    "language": "korean",
    "total_words": 0,
    "levels": ["A1", "A2", "B1"],
    "categories": ["pronouns", "numbers", "daily-life", "travel", "food", "emotions", "verbs"],
    "purpose": "A2→B1 practical conversation"
  },
  "words": {
    "책": {
      "target": "책",
      "romanization": "chaek",
      "translation": "book",
      "pos": "noun",
      "level": "A1",
      "frequency": 2,
      "category": "daily-life",
      "examples": [
        "책을 읽어요 (I read a book)",
        "재미있는 책 (interesting book)"
      ],
      "notes": "Counter: 권 (gwon)"
    }
  }
}
```

**Required fields per word:** `target`, `translation`, `pos`, `level`, `frequency` (1–10), `category`, `examples`

**Optional:** `romanization`, `notes`, `declension`/`conjugation` (for morphologically rich languages)

### 3. Create `concepts.json`

Grammar concepts with prerequisite dependencies.

```json
{
  "meta": {
    "language": "korean",
    "focus": "A2→B1 grammar",
    "total_concepts": 0
  },
  "concepts": {
    "topic-marker": {
      "id": "topic-marker",
      "name": "Topic Marker: 은/는",
      "level": "A1",
      "category": "grammar",
      "prerequisites": [],
      "description": "은/는 marks the topic of the sentence",
      "examples": [
        "저는 학생이에요 (I am a student)",
        "이것은 책이에요 (This is a book)"
      ],
      "drills": [
        "Add topic marker: 나 → 저는",
        "Translate: I am a teacher"
      ]
    }
  }
}
```

**Required fields per concept:** `id`, `name`, `level`, `category`, `prerequisites` (array of concept ids), `description`, `examples`, `drills`

### 4. Create `echo-scenarios.json`

FSI roleplay scenarios for conversational practice.

```json
{
  "meta": {
    "language": "korean",
    "total_scenarios": 0,
    "levels": ["A2", "B1"],
    "topics": ["daily-life", "travel", "social", "dating"]
  },
  "scenarios": {
    "cafe-meeting": {
      "id": "cafe-meeting",
      "title": "Meeting at a café",
      "level": "A2",
      "tags": ["daily-life", "social"],
      "seed_phrase": "여기 앉아도 돼요?",
      "seed_meaning": "May I sit here?",
      "substitutions": [
        "들어가도 돼요?",
        "물어봐도 돼요?",
        "전화해도 돼요?"
      ],
      "vocabulary": ["앉다", "들어가다", "물어보다"]
    }
  }
}
```

**Required fields per scenario:** `id`, `title`, `level`, `tags`, `seed_phrase`, `seed_meaning`, `substitutions` (3–4), `vocabulary`

**Aim for:** 10+ scenarios covering daily-life, travel, social, dating topics.

### 5. Test it

```bash
python3 scripts/state_manager.py init-session korean words 5
python3 scripts/state_manager.py init-session korean echo
```

Both should return valid JSON without errors.

### 6. Use it

```
/savant korean words
/savant korean echo
```

---

## Currently Supported Languages

| Language | Words | Concepts | Echo Scenarios |
|----------|-------|----------|----------------|
| Russian  | 350+  | 42       | 10             |

---

## Contributing

1. Fork this repo
2. Add your language pack following the guide above
3. Test with the state manager
4. Open a PR with the new `languages/{lang}/` directory

Language pack quality checklist:
- [ ] Minimum 100 words at A1–A2 level
- [ ] Minimum 10 grammar concepts
- [ ] Minimum 10 echo scenarios across all topic tags
- [ ] All required fields present (no missing keys)
- [ ] Stress marks / romanization included where helpful
- [ ] Examples are natural, not textbook-stiff
````

**Step 2: Commit**

```bash
git add languages/README.md
git commit -m "docs: add language pack extension guide (languages/README.md)"
```

---

## Task 7: Update root `README.md` and `Makefile`

Reflect the new plugin name, invocation syntax, and structure.

**Files:**
- Modify: `README.md`
- Modify: `Makefile`

**Step 1: Rewrite `README.md`**

Keep it short — installation, usage, adding languages. Remove all references to `russian-learning`, `data/`, old paths.

Key sections:
- What is Savant
- Installation (as Claude Code plugin)
- Usage: `/savant russian words`, `/savant russian echo`
- Adding a language (link to `languages/README.md`)
- Running tests: `python3 scripts/test_state_manager.py`

**Step 2: Update `Makefile`**

Replace old targets:

```makefile
.PHONY: test stats help

help:
	@echo "Savant Plugin"
	@echo "  make test          - Run state manager tests"
	@echo "  make stats-words   - Show Russian words progress"
	@echo "  make stats-echo    - Show Russian echo progress"

test:
	python3 scripts/test_state_manager.py

stats-words:
	python3 scripts/state_manager.py stats russian words

stats-echo:
	python3 scripts/state_manager.py stats russian echo
```

**Step 3: Commit**

```bash
git add README.md Makefile
git commit -m "docs: update README and Makefile for savant plugin"
```

---

## Task 8: Wire the plugin into Claude Code

Install the local plugin so `/savant` is available in this project.

**Step 1: Update `.claude/settings.local.json`**

The skill needs to reference the new path. Check current content:

```bash
cat .claude/settings.local.json
```

Add or update to point at the new skill location:

```json
{
  "skills": [
    {
      "name": "savant",
      "file": "skills/savant.md"
    }
  ]
}
```

**Step 2: Smoke test**

Open a new Claude Code session in this repo and run:

```
/savant russian words
```

Verify:
- Claude initializes a session
- State file created at `~/.claude/savant/russian-words-state.json`
- Conversation flows correctly

Then test:

```
/savant russian echo
```

Verify:
- A scenario is returned from `echo-scenarios.json`
- FSI loop runs (phrase → echo → drills → roleplay)
- State file at `~/.claude/savant/russian-echo-state.json` updated

**Step 3: Commit**

```bash
git add .claude/settings.local.json
git commit -m "chore: wire savant skill into local Claude Code settings"
```

---

## Final Checklist

- [ ] All tests pass: `python3 scripts/test_state_manager.py`
- [ ] `/savant russian words` starts a session
- [ ] `/savant russian echo` starts an FSI session
- [ ] `/savant klingon words` shows a clear error message
- [ ] `~/.claude/savant/russian-words-state.json` created after first words session
- [ ] `~/.claude/savant/russian-echo-state.json` created after first echo session
- [ ] Echo does not repeat scenario within 5 sessions
- [ ] `languages/README.md` explains how to add Korean
- [ ] `make test` runs all tests
