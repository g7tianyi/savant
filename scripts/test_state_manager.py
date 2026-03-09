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
    env = {"SAVANT_STATE_DIR": str(tmp_path)}
    result = run(["init-session", "russian", "words", "10"], env)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert "words" in data
    assert "concepts" in data
    assert "session_id" in data
    print("PASS: test_init_session_words")

def test_update_words(tmp_path):
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
    env = {"SAVANT_STATE_DIR": str(tmp_path)}
    result = run(["init-session", "russian", "echo"], env)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert "scenario" in data
    assert "seed_phrase" in data["scenario"]
    print("PASS: test_init_session_echo")

def test_echo_avoids_recent(tmp_path):
    env = {"SAVANT_STATE_DIR": str(tmp_path)}
    seen = set()
    for _ in range(5):
        result = run(["init-session", "russian", "echo"], env)
        data = json.loads(result.stdout)
        scenario_id = data["scenario"]["id"]
        run(["finalize", "russian", "echo", data["session_id"], scenario_id], env)
        seen.add(scenario_id)
    assert len(seen) == 5, f"Expected 5 unique scenarios, got {seen}"
    print("PASS: test_echo_avoids_recent")

def test_log_vocab(tmp_path):
    env = {"SAVANT_STATE_DIR": str(tmp_path)}
    result = run(["log-vocab", "russian", "echo", "присесть"], env)
    assert result.returncode == 0, result.stderr
    state_file = tmp_path / "russian-echo-state.json"
    state = json.loads(state_file.read_text())
    words = [e["word"] for e in state["echo_vocab_log"]]
    assert "присесть" in words
    print("PASS: test_log_vocab")

def test_missing_language(tmp_path):
    env = {"SAVANT_STATE_DIR": str(tmp_path)}
    result = run(["init-session", "klingon", "words"], env)
    assert result.returncode != 0
    output = result.stderr + result.stdout
    assert "klingon" in output.lower()
    print("PASS: test_missing_language")

def test_stats_words(tmp_path):
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
