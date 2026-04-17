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
        """Reminder must contain section pointers and key behavioral gates."""
        output = self._run_hook()
        ctx = output["hookSpecificOutput"]["additionalContext"]
        for token in [
            "CLAUDE.md",
            "MANDATORY",
            "<constraints>",
            "<identity>",
            "<workflow>",
            "Skills precede ALL work",
            "NEVER start without observable scenarios",
            "satisfaction criteria",
            "same rigor as turn one",
        ]:
            self.assertIn(token, ctx, f"Missing activation token: {token}")

    def test_salience_wrapper(self):
        """Reinforcement must use EXTREMELY_IMPORTANT salience wrapper."""
        ctx = constraint_reinforcement.REINFORCEMENT
        self.assertIn("<EXTREMELY_IMPORTANT>", ctx)
        self.assertIn("</EXTREMELY_IMPORTANT>", ctx)

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

    def test_output_is_single_line_json(self):
        """Hook protocol: stdout must be a single valid JSON object."""
        stdout_capture = io.StringIO()
        with unittest.mock.patch("sys.stdin", io.StringIO("")), \
             unittest.mock.patch("sys.stdout", stdout_capture), \
             self.assertRaises(SystemExit):
            constraint_reinforcement.main()
        raw = stdout_capture.getvalue()
        # Trailing newline from print() is tolerated; inner newlines are not.
        self.assertLessEqual(raw.count("\n"), 1,
            f"Hook output must be one JSON line; got multi-line: {raw!r}")
        json.loads(raw)  # must parse — raises if malformed

    def test_ignores_stdin_content(self):
        """Hook is pure — output is the same regardless of input payload."""
        outputs = []
        for payload in ("", '{"prompt":"x"}',
                        json.dumps({"transcript_path": "/dev/null"}),
                        "garbage data that is not json"):
            stdout_capture = io.StringIO()
            with unittest.mock.patch("sys.stdin", io.StringIO(payload)), \
                 unittest.mock.patch("sys.stdout", stdout_capture), \
                 self.assertRaises(SystemExit):
                constraint_reinforcement.main()
            outputs.append(stdout_capture.getvalue())
        # All outputs must be byte-identical — hook must not leak input
        self.assertEqual(len(set(outputs)), 1,
            "Hook output must be independent of stdin content")

    def test_idempotent_across_invocations(self):
        """Repeated calls return the same context — no mutable global state."""
        results = []
        for _ in range(3):
            stdout_capture = io.StringIO()
            with unittest.mock.patch("sys.stdin", io.StringIO("")), \
                 unittest.mock.patch("sys.stdout", stdout_capture), \
                 self.assertRaises(SystemExit):
                constraint_reinforcement.main()
            results.append(stdout_capture.getvalue())
        self.assertEqual(len(set(results)), 1,
            "Hook must be idempotent across invocations")


if __name__ == "__main__":
    unittest.main()
