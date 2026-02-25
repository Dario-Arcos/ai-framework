#!/usr/bin/env python3
"""Tests for subagent-start.py — SubagentStart hook for skill registry injection."""
import importlib
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
subagent_start = importlib.import_module("subagent-start")


class TestOutput(unittest.TestCase):
    """Test main() produces valid SubagentStart hook output."""

    def _run_hook(self):
        """Run main() capturing stdout, return parsed JSON."""
        stdout_capture = io.StringIO()
        with unittest.mock.patch("sys.stdin", io.StringIO("")), \
             unittest.mock.patch("sys.stdout", stdout_capture), \
             self.assertRaises(SystemExit) as cm:
            subagent_start.main()
        self.assertEqual(cm.exception.code, 0)
        return json.loads(stdout_capture.getvalue())

    def test_valid_json_structure(self):
        output = self._run_hook()
        self.assertIn("hookSpecificOutput", output)
        self.assertEqual(
            output["hookSpecificOutput"]["hookEventName"], "SubagentStart"
        )
        self.assertIn("additionalContext", output["hookSpecificOutput"])

    def test_contains_critical_skills(self):
        output = self._run_hook()
        ctx = output["hookSpecificOutput"]["additionalContext"]
        for skill in [
            "scenario-driven-development",
            "verification-before-completion",
            "agent-browser",
            "systematic-debugging",
        ]:
            self.assertIn(skill, ctx, f"Missing critical skill: {skill}")

    def test_contains_invocation_syntax(self):
        """The whole point: sub-agents must know HOW to invoke skills."""
        output = self._run_hook()
        ctx = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn('Skill("', ctx)
        self.assertIn('Skill("scenario-driven-development")', ctx)
        self.assertIn('Skill("agent-browser"', ctx)

    def test_no_constraint_language(self):
        """Constraints live in CLAUDE.md, not in the skill index."""
        output = self._run_hook()
        ctx = output["hookSpecificOutput"]["additionalContext"]
        for term in ["MUST", "NEVER", "ALWAYS", "CRITICAL"]:
            self.assertNotIn(
                term, ctx, f"Constraint language '{term}' should not be in skill index"
            )

    def test_no_redundancy(self):
        """Each skill name should appear exactly once to minimize reasoning friction."""
        ctx = subagent_start.SKILL_INDEX
        for skill in ["scenario-driven-development", "systematic-debugging",
                       "deep-research", "context-engineering", "commit"]:
            count = ctx.count(f'Skill("{skill}")')
            self.assertEqual(count, 1, f'Skill("{skill}") appears {count} times, expected 1')

    def test_token_budget(self):
        """Skill index should stay compact — under 800 chars (~150 tokens)."""
        self.assertLess(len(subagent_start.SKILL_INDEX), 800)

    def test_handles_empty_stdin(self):
        """Hook must not crash on empty stdin."""
        stdout_capture = io.StringIO()
        with unittest.mock.patch("sys.stdin", io.StringIO("")), \
             unittest.mock.patch("sys.stdout", stdout_capture), \
             self.assertRaises(SystemExit) as cm:
            subagent_start.main()
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
            subagent_start.main()
        self.assertEqual(cm.exception.code, 0)


# Need mock import at top for _run_hook helper
import unittest.mock  # noqa: E402


if __name__ == "__main__":
    unittest.main()
