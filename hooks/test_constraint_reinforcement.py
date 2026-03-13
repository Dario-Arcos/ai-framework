#!/usr/bin/env python3
"""Tests for constraint-reinforcement.py — UserPromptSubmit hook."""
import importlib
import io
import json
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
constraint_reinforcement = importlib.import_module("constraint-reinforcement")


class TestOutput(unittest.TestCase):
    """Test main() produces valid UserPromptSubmit hook output."""

    def _run_hook(self):
        """Run main() capturing stdout, return parsed JSON."""
        stdout_capture = io.StringIO()
        with unittest.mock.patch("sys.stdin", io.StringIO("")), \
             unittest.mock.patch("sys.stdout", stdout_capture), \
             self.assertRaises(SystemExit) as cm:
            constraint_reinforcement.main()
        self.assertEqual(cm.exception.code, 0)
        return json.loads(stdout_capture.getvalue())

    def test_valid_json_structure(self):
        output = self._run_hook()
        self.assertIn("hookSpecificOutput", output)
        self.assertEqual(
            output["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit"
        )
        self.assertIn("additionalContext", output["hookSpecificOutput"])

    def test_contains_activation_tokens(self):
        """Reminder must contain verbatim CLAUDE.md phrases for associative activation."""
        output = self._run_hook()
        ctx = output["hookSpecificOutput"]["additionalContext"]
        for token in [
            "CLAUDE.md",
            "MANDATORY",
            "Skills precede ALL work",
            "/brainstorming",
            "plan mode",
            "/scenario-driven-development",
            "/verification-before-completion",
            "NEVER start without observable scenarios",
            "satisfaction criteria",
            "reward hacking",
            "opus only",
            "/agent-browser",
        ]:
            self.assertIn(token, ctx, f"Missing activation token: {token}")

    def test_token_budget(self):
        """Reminder should stay compact — under 400 chars."""
        self.assertLess(len(constraint_reinforcement.REINFORCEMENT), 400)

    def test_no_aggressive_language(self):
        """Opus 4.6 guidance: no CRITICAL/MUST — verbatim CLAUDE.md keywords allowed."""
        ctx = constraint_reinforcement.REINFORCEMENT.upper()
        for word in ["CRITICAL", "MUST"]:
            self.assertNotIn(word, ctx, f"Aggressive language found: {word}")

    def test_handles_empty_stdin(self):
        """Hook must not crash on empty stdin."""
        stdout_capture = io.StringIO()
        with unittest.mock.patch("sys.stdin", io.StringIO("")), \
             unittest.mock.patch("sys.stdout", stdout_capture), \
             self.assertRaises(SystemExit) as cm:
            constraint_reinforcement.main()
        self.assertEqual(cm.exception.code, 0)

    def test_handles_stdin_ioerror(self):
        """Hook must not crash when stdin raises IOError."""
        class BrokenStdin:
            def read(self):
                raise IOError("broken pipe")
        stdout_capture = io.StringIO()
        with unittest.mock.patch("sys.stdin", BrokenStdin()), \
             unittest.mock.patch("sys.stdout", stdout_capture), \
             self.assertRaises(SystemExit) as cm:
            constraint_reinforcement.main()
        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
