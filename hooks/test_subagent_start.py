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

    def test_contains_invocation_hint(self):
        """Sub-agents must know skills are invoked via Skill tool."""
        output = self._run_hook()
        ctx = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Skill tool", ctx)

    def test_contains_agent_browser_description(self):
        """agent-browser should have a usage hint."""
        output = self._run_hook()
        ctx = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("agent-browser", ctx)

    def test_no_redundancy(self):
        """Each skill name should appear at most once to minimize reasoning friction."""
        ctx = subagent_start.SKILL_INDEX
        for skill in ["scenario-driven-development", "systematic-debugging",
                       "deep-research", "context-engineering", "commit"]:
            count = ctx.count(skill)
            self.assertLessEqual(count, 1, f'"{skill}" appears {count} times, expected <=1')

    def test_token_budget(self):
        """Skill index should stay compact — under 1200 chars (~250 tokens)."""
        self.assertLess(len(subagent_start.SKILL_INDEX), 1200)

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
