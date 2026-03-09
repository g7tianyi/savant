#!/usr/bin/env python3
"""
State Manager for Russian Learning Skill

Simple script to manage learner state (JSON-based).
Called by the russian-learning skill to:
- Initialize session (select concepts/words to review)
- Update mastery after interactions
- Track progress

No server, no complexity - just pure functions.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import random

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VOCAB_FILE = DATA_DIR / "russian-vocabulary.json"
CONCEPTS_FILE = DATA_DIR / "russian-concepts.json"
STATE_FILE = DATA_DIR / "learner-state.json"


def load_json(filepath: Path) -> Dict:
    """Load JSON file"""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_json(filepath: Path, data: Dict):
    """Save JSON file"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_state() -> Dict:
    """Initialize empty learner state"""
    return {
        "meta": {
            "created": datetime.now().isoformat(),
            "last_session": None,
            "total_sessions": 0
        },
        "words": {},  # word -> {mastery, last_reviewed, review_count, next_review}
        "concepts": {}  # concept_id -> {mastery, last_reviewed, review_count, next_review}
    }


def get_due_items(state: Dict, item_type: str) -> List[str]:
    """Get items due for review"""
    now = datetime.now()
    due = []

    items = state.get(item_type, {})
    for item_id, item_data in items.items():
        next_review = item_data.get("next_review")
        if next_review:
            next_review_dt = datetime.fromisoformat(next_review)
            if next_review_dt <= now:
                due.append(item_id)
        else:
            # Never reviewed - add to due list
            due.append(item_id)

    return due


def get_new_items(state: Dict, all_items: List[str], item_type: str, limit: int = 5) -> List[str]:
    """Get new items not yet seen"""
    seen = set(state.get(item_type, {}).keys())
    unseen = [item for item in all_items if item not in seen]
    return random.sample(unseen, min(limit, len(unseen)))


def select_session_items(target_count: int = 15) -> Dict:
    """Select words and concepts for this session"""
    state = load_json(STATE_FILE) if STATE_FILE.exists() else init_state()
    vocab = load_json(VOCAB_FILE)
    concepts = load_json(CONCEPTS_FILE)

    # Get all words and concepts
    all_words = list(vocab.get("words", {}).keys())
    all_concepts = list(concepts.get("concepts", {}).keys())

    # Get due items (priority)
    due_words = get_due_items(state, "words")
    due_concepts = get_due_items(state, "concepts")

    # Get new items
    new_words = get_new_items(state, all_words, "words", limit=5)
    new_concepts = get_new_items(state, all_concepts, "concepts", limit=3)

    # Combine (prioritize due items)
    selected_words = due_words[:10] + new_words
    selected_concepts = due_concepts[:5] + new_concepts

    # Limit to target count
    selected_words = selected_words[:min(10, target_count // 2)]
    selected_concepts = selected_concepts[:min(5, target_count // 2)]

    return {
        "session_id": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "words": selected_words,
        "concepts": selected_concepts,
        "stats": {
            "due_words": len(due_words),
            "due_concepts": len(due_concepts),
            "new_words": len(new_words),
            "new_concepts": len(new_concepts)
        }
    }


def update_item_mastery(state: Dict, item_id: str, item_type: str, correct: bool, confidence: int):
    """Update mastery for a word or concept"""
    if item_type not in state:
        state[item_type] = {}

    if item_id not in state[item_type]:
        state[item_type][item_id] = {
            "mastery": 0.0,
            "review_count": 0,
            "error_count": 0,
            "last_reviewed": None,
            "next_review": None,
            "interval_days": 1
        }

    item = state[item_type][item_id]

    # Update mastery (Bayesian-inspired)
    if correct:
        adjustment = 0.1 * (1 + confidence / 100 * 0.5)
        item["mastery"] = min(1.0, item["mastery"] + adjustment)
    else:
        adjustment = 0.15
        item["mastery"] = max(0.0, item["mastery"] - adjustment)

    # Update review tracking
    item["review_count"] += 1
    if not correct:
        item["error_count"] += 1
    item["last_reviewed"] = datetime.now().isoformat()

    # Calculate next review (SM-2 style)
    if correct:
        item["interval_days"] *= 2.5
    else:
        item["interval_days"] = 1

    item["interval_days"] = max(1, min(90, item["interval_days"]))
    next_review = datetime.now() + timedelta(days=item["interval_days"])
    item["next_review"] = next_review.isoformat()


def record_interaction(item_id: str, item_type: str, correct: bool, confidence: int):
    """Record a single interaction"""
    state = load_json(STATE_FILE) if STATE_FILE.exists() else init_state()
    update_item_mastery(state, item_id, item_type, correct, confidence)
    save_json(STATE_FILE, state)


def finalize_session(session_id: str):
    """Mark session as complete"""
    state = load_json(STATE_FILE) if STATE_FILE.exists() else init_state()
    state["meta"]["last_session"] = datetime.now().isoformat()
    state["meta"]["total_sessions"] += 1
    save_json(STATE_FILE, state)


def get_stats() -> Dict:
    """Get learning progress stats"""
    state = load_json(STATE_FILE) if STATE_FILE.exists() else init_state()

    # Calculate stats
    total_words = len(state.get("words", {}))
    mastered_words = sum(1 for w in state.get("words", {}).values() if w.get("mastery", 0) >= 0.8)

    total_concepts = len(state.get("concepts", {}))
    mastered_concepts = sum(1 for c in state.get("concepts", {}).values() if c.get("mastery", 0) >= 0.8)

    return {
        "total_sessions": state["meta"].get("total_sessions", 0),
        "last_session": state["meta"].get("last_session", "Never"),
        "words": {
            "total": total_words,
            "mastered": mastered_words,
            "in_progress": total_words - mastered_words
        },
        "concepts": {
            "total": total_concepts,
            "mastered": mastered_concepts,
            "in_progress": total_concepts - mastered_concepts
        }
    }


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: state_manager.py <command> [args]")
        print("Commands:")
        print("  init-session [count]     - Select items for session")
        print("  update <item_id> <type> <correct> <confidence> - Record interaction")
        print("  finalize <session_id>    - Mark session complete")
        print("  stats                    - Show progress stats")
        sys.exit(1)

    command = sys.argv[1]

    if command == "init-session":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        result = select_session_items(count)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "update":
        item_id = sys.argv[2]
        item_type = sys.argv[3]
        correct = sys.argv[4].lower() == "true"
        confidence = int(sys.argv[5])
        record_interaction(item_id, item_type, correct, confidence)
        print(f"Updated {item_type}: {item_id}")

    elif command == "finalize":
        session_id = sys.argv[2]
        finalize_session(session_id)
        print(f"Session {session_id} finalized")

    elif command == "stats":
        stats = get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
