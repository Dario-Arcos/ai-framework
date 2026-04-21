#!/usr/bin/env python3
"""SCEN-018 — hooks.json PostToolUse matcher must include MultiEdit+NotebookEdit.

sdd-auto-test.py records per-session file edits via record_file_edit(cwd,
file_path, sid). Phase 8 cascade Rung 1b reads that session state to
scope tests to files the agent itself has touched in this session. When
the matcher omits MultiEdit or NotebookEdit, any test file created via
those tools is invisible to Rung 1b — cascade silently degrades to
Rung 2 (stack-native impacted) or Rung 3 (full suite).

This defeats the per-edit efficiency guarantee advertised by Phase 8
on any workflow where the agent uses MultiEdit or Jupyter notebooks.

Red-green contract:
  1. Before fix, matcher = "Edit|Write|Skill" — "MultiEdit" and
     "NotebookEdit" are absent; two tests FAIL.
  2. Fix adds both tokens to hooks.json:81; tests pass.
  3. Reverting restores red.

Milestone guarantee is preserved regardless: TaskCompleted always runs
the full suite, independent of PostToolUse matcher coverage. The
matcher gap affects only per-edit scoping — the safety net at
work-block boundaries is unchanged.
"""
import json
import unittest
from pathlib import Path


HOOKS_JSON = Path(__file__).resolve().parent / "hooks.json"


def _load_config():
    return json.loads(HOOKS_JSON.read_text(encoding="utf-8"))


def _auto_test_matcher(config):
    """Return the PostToolUse matcher string for sdd-auto-test entry."""
    for entry in config.get("hooks", {}).get("PostToolUse", []):
        for h in entry.get("hooks", []):
            if "sdd-auto-test.py" in h.get("command", ""):
                return entry.get("matcher", "")
    raise AssertionError("No PostToolUse entry invokes sdd-auto-test.py")


def _matcher_tokens(matcher):
    return [tok.strip() for tok in matcher.split("|") if tok.strip()]


class TestScen018PostToolUseEditCoverage(unittest.TestCase):
    """PostToolUse matcher must cover every tool that mutates files."""

    @classmethod
    def setUpClass(cls):
        cls.config = _load_config()
        cls.matcher = _auto_test_matcher(cls.config)
        cls.tokens = _matcher_tokens(cls.matcher)

    def test_multiedit_in_posttooluse_matcher(self):
        """Rung 1b session tracking must capture MultiEdit edits."""
        self.assertIn(
            "MultiEdit",
            self.tokens,
            f"PostToolUse matcher must list MultiEdit so record_file_edit "
            f"captures session test files created via MultiEdit. Without "
            f"this, Phase 8 Rung 1b cascade silently degrades to Rung 2/3. "
            f"Current matcher: {self.matcher!r}",
        )

    def test_notebookedit_in_posttooluse_matcher(self):
        """Rung 1b session tracking must capture NotebookEdit edits."""
        self.assertIn(
            "NotebookEdit",
            self.tokens,
            f"PostToolUse matcher must list NotebookEdit so Jupyter "
            f"notebook test edits are recorded for Rung 1b. "
            f"Current matcher: {self.matcher!r}",
        )

    def test_existing_tool_coverage_preserved(self):
        """Edit, Write, Skill must remain covered (no regression)."""
        for required in ("Edit", "Write", "Skill"):
            self.assertIn(
                required,
                self.tokens,
                f"PostToolUse matcher must preserve {required} coverage; "
                f"got: {self.matcher!r}",
            )

    def test_matcher_tokens_are_unique(self):
        self.assertEqual(
            len(self.tokens),
            len(set(self.tokens)),
            f"PostToolUse matcher has duplicate tokens: {self.matcher!r}",
        )


if __name__ == "__main__":
    unittest.main()
