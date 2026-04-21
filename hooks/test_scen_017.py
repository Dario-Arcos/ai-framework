#!/usr/bin/env python3
"""SCEN-017 — hooks.json PreToolUse matcher must include MultiEdit.

Claude Code runtime dispatches hooks based on the matcher string in
hooks.json. The matcher is a pipe-separated set of exact tool names;
a tool that is not listed never triggers the hook.

sdd-test-guard.py has been written to simulate MultiEdit throughout:
- _predict_scenario_post_edit_hash handles tool_name == "MultiEdit"
- _malformed_scenario_edit_reason handles tool_name == "MultiEdit"
- scenario write-once block checks tool_name in {..., "MultiEdit"}
- critical-path guard checks tool_name in {..., "MultiEdit"}

But if "MultiEdit" is not in the PreToolUse matcher, Claude Code
NEVER invokes the hook on MultiEdit calls. The simulation code is
dead, and the write-once contract has a bypass — an agent using
MultiEdit on a .claude/scenarios/ file bypasses all four guards.

Red-green contract:
  1. Before fix, matcher = "Edit|Write|NotebookEdit|TaskUpdate|Bash" —
     "MultiEdit" is absent; test_multiedit_in_pretooluse_matcher FAILS.
  2. Fix adds MultiEdit to hooks.json:69; test passes.
  3. Reverting hooks.json restores red.
"""
import json
import unittest
from pathlib import Path


HOOKS_JSON = Path(__file__).resolve().parent / "hooks.json"


def _load_config():
    return json.loads(HOOKS_JSON.read_text(encoding="utf-8"))


def _guard_matcher(config):
    """Return the PreToolUse matcher string for the sdd-test-guard entry."""
    for entry in config.get("hooks", {}).get("PreToolUse", []):
        for h in entry.get("hooks", []):
            if "sdd-test-guard.py" in h.get("command", ""):
                return entry.get("matcher", "")
    raise AssertionError("No PreToolUse entry invokes sdd-test-guard.py")


def _matcher_tokens(matcher):
    return [tok.strip() for tok in matcher.split("|") if tok.strip()]


class TestScen017PreToolUseMultiEditCoverage(unittest.TestCase):
    """PreToolUse matcher must cover every tool sdd-test-guard handles."""

    @classmethod
    def setUpClass(cls):
        cls.config = _load_config()
        cls.matcher = _guard_matcher(cls.config)
        cls.tokens = _matcher_tokens(cls.matcher)

    def test_multiedit_in_pretooluse_matcher(self):
        """Closes write-once bypass: hook must fire on MultiEdit tool calls."""
        self.assertIn(
            "MultiEdit",
            self.tokens,
            f"PreToolUse matcher must list MultiEdit so Claude Code "
            f"dispatches sdd-test-guard on MultiEdit tool calls. Without "
            f"this coverage, agent using MultiEdit on a scenario file "
            f"bypasses the write-once guard entirely. "
            f"Current matcher: {self.matcher!r}",
        )

    def test_existing_tool_coverage_preserved(self):
        """No regression: tools already covered must remain covered."""
        for required in ("Edit", "Write", "NotebookEdit", "TaskUpdate", "Bash"):
            self.assertIn(
                required,
                self.tokens,
                f"PreToolUse matcher must preserve {required} coverage "
                f"(pre-existing guard surface). Current matcher: "
                f"{self.matcher!r}",
            )

    def test_matcher_tokens_are_unique(self):
        """Hygiene: no accidental duplicates in the alternation."""
        self.assertEqual(
            len(self.tokens),
            len(set(self.tokens)),
            f"PreToolUse matcher has duplicate tokens: {self.matcher!r}",
        )

    def test_matcher_has_no_empty_tokens(self):
        """Hygiene: no stray `||` creating empty alternatives."""
        for tok in self.matcher.split("|"):
            self.assertEqual(
                tok,
                tok.strip(),
                f"PreToolUse matcher token has surrounding whitespace: "
                f"{tok!r} in {self.matcher!r}",
            )
            self.assertNotEqual(
                tok, "", f"PreToolUse matcher has empty token: {self.matcher!r}"
            )


if __name__ == "__main__":
    unittest.main()
