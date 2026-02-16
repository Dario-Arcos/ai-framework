#!/usr/bin/env python3
"""SDD Test Guard hook — holdout protection against reward hacking.

PreToolUse (Edit|Write): before editing a test file, verify that tests are
currently failing AND the edit reduces assertion count → DENY.

This prevents the AI from weakening tests to make failing code appear correct.
StrongDM: "Not M/M → fix code, never weaken scenarios."

Decision matrix:
  Tests passing  + any change       → ALLOW (refactoring)
  Tests failing  + assertions >=    → ALLOW (fix or new test)
  Tests failing  + assertions <     → DENY  (reward hacking)
  No test state  + any change       → ALLOW (no data = no block)

State shared with sdd-auto-test.py via /tmp/ files (keyed by project hash).
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import read_state


# ─────────────────────────────────────────────────────────────────
# PATTERNS
# ─────────────────────────────────────────────────────────────────

TEST_FILE_RE = re.compile(
    r"(?:test|spec|__tests__)[/\\]|"
    r"\.(?:test|spec)\.|"
    r"_test\.|"
    r"test_"
)

ASSERTION_RE = re.compile(
    r"\bassert\b|"
    r"\bexpect\s*\(|"
    r"\.toBe|\.toEqual|\.toMatch|\.toThrow|\.toHaveBeenCalled|"
    r"\.should|\.to\.|"
    r"t\.(?:Error|Fatal|Run)|"
    r"assert_eq!|assert_ne!|"
    r"#\[test\]|"
    r"@Test|"
    r"def test_"
)


# ─────────────────────────────────────────────────────────────────
# FILE CLASSIFICATION
# ─────────────────────────────────────────────────────────────────

def is_test_file(path):
    """Check if path matches common test file patterns."""
    if not path:
        return False
    return bool(TEST_FILE_RE.search(path))


# ─────────────────────────────────────────────────────────────────
# ASSERTION COUNTING
# ─────────────────────────────────────────────────────────────────

def count_assertions(text):
    """Count assertion-like patterns in text."""
    if not text:
        return 0
    return len(ASSERTION_RE.findall(text))


# ─────────────────────────────────────────────────────────────────
# EDIT ANALYSIS
# ─────────────────────────────────────────────────────────────────

def analyze_edit(tool_name, tool_input):
    """Analyze an Edit or Write to determine assertion count change.

    Returns (old_count, new_count).
    """
    if tool_name == "Edit":
        old_text = tool_input.get("old_string", "")
        new_text = tool_input.get("new_string", "")
        return count_assertions(old_text), count_assertions(new_text)

    if tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        new_text = tool_input.get("content", "")
        new_count = count_assertions(new_text)

        # Read existing file to compare
        try:
            old_text = Path(file_path).read_text(encoding="utf-8")
            old_count = count_assertions(old_text)
        except (FileNotFoundError, OSError):
            # New file — no old assertions to compare
            return 0, new_count

        return old_count, new_count

    return 0, 0


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    """Hook entry point (PreToolUse). ~1ms non-test, ~5ms test files."""
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    cwd = input_data.get("cwd", os.getcwd())
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Fast path: not a test file → allow (~1ms)
    if not is_test_file(file_path):
        sys.exit(0)

    # Read test state
    state = read_state(cwd)

    # No state → allow (no data = no block)
    if state is None:
        sys.exit(0)

    # Tests passing → allow (refactoring is fine)
    if state.get("passing", False):
        sys.exit(0)

    # Tests failing → check assertion count
    old_count, new_count = analyze_edit(tool_name, tool_input)

    if new_count < old_count:
        # DENY: reward hacking detected
        reason = (
            f"SDD Guard: tests are failing and this edit reduces "
            f"assertions ({old_count}\u2192{new_count}). "
            f"Fix implementation code, not tests. "
            f"Weakening a test to match a bug = reward hacking."
        )
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))
        sys.exit(0)

    # Assertions same or increased → allow
    sys.exit(0)


if __name__ == "__main__":
    main()
