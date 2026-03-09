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
  state_manager.py finalize <lang> <mode> <session_id> [scenario_id]
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
ECHO_WINDOW = 5


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
        available = list(all_scenarios.keys())

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
        state["recent_scenarios"] = recent[-(ECHO_WINDOW * 2):]
    save_json(sf, state)

def stats_echo(lang: str) -> dict:
    sf = state_file(lang, "echo")
    state = load_json(sf) if sf.exists() else init_echo_state()
    return {
        "lang": lang, "mode": "echo",
        "recent_scenarios": state.get("recent_scenarios", []),
        "vocab_logged": len(state.get("echo_vocab_log", [])),
        "echo_vocab_log": state.get("echo_vocab_log", [])[-10:]
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
        if len(args) < 4:
            usage()
        lang, mode, word = args[1], args[2], args[3]
        validate_lang(lang)
        log_vocab_echo(lang, word)
        print(f"Logged vocab: {word}")

    elif cmd == "finalize":
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
