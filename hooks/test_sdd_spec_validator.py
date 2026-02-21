#!/usr/bin/env python3
"""Tests for spec validation (merged into sdd-auto-test.py)."""
import importlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sdd_auto_test = importlib.import_module("sdd-auto-test")

validate_spec = sdd_auto_test.validate_spec
_extract_section = sdd_auto_test._extract_section
main = sdd_auto_test.main


class TestExtractSection(unittest.TestCase):
    """Test _extract_section() heading extraction."""

    def test_extracts_section_content(self):
        content = "## Foo\nline 1\nline 2\n## Bar\nother"
        self.assertEqual(_extract_section(content, "## Foo"), "line 1\nline 2")

    def test_last_section(self):
        content = "## Foo\nline 1\n## Bar\nlast section"
        self.assertEqual(_extract_section(content, "## Bar"), "last section")

    def test_missing_section(self):
        content = "## Foo\nline 1"
        self.assertEqual(_extract_section(content, "## Missing"), "")


class TestValidateSpec(unittest.TestCase):
    """Test validate_spec() structural validation."""

    def test_valid_spec_no_warnings(self):
        content = """## Acceptance Criteria
- Given user is logged in
  When they click logout
  Then they see login page
- Given cart has 3 items
  When user removes 1
  Then cart shows 2 items
- Given empty form
  When user submits
  Then validation errors shown
## Metadata
- Scenario-Strategy: required"""
        self.assertEqual(validate_spec(content), [])

    def test_missing_acceptance_criteria(self):
        warnings = validate_spec("## Description\nSome task")
        self.assertEqual(len(warnings), 1)
        self.assertIn("Missing", warnings[0])

    def test_too_few_criteria(self):
        content = """## Acceptance Criteria
- Given x When y Then z
## Metadata
- Scenario-Strategy: required"""
        warnings = validate_spec(content)
        self.assertTrue(any("Only 1" in w for w in warnings))

    def test_two_criteria_warns(self):
        content = """## Acceptance Criteria
- Given a When b Then c
- Given d When e Then f
## Metadata
- Scenario-Strategy: required"""
        warnings = validate_spec(content)
        self.assertTrue(any("Only 2" in w for w in warnings))

    def test_missing_scenario_strategy(self):
        content = """## Acceptance Criteria
- Given a When b Then c
- Given d When e Then f
- Given g When h Then i"""
        warnings = validate_spec(content)
        self.assertTrue(any("Scenario-Strategy" in w for w in warnings))

    def test_zero_criteria_warns(self):
        content = """## Acceptance Criteria
Some description without Given-When-Then format.
## Metadata
- Scenario-Strategy: required"""
        warnings = validate_spec(content)
        self.assertTrue(any("Only 0" in w for w in warnings))

    def test_case_insensitive_given(self):
        content = """## Acceptance Criteria
- given user exists
  when they login
  then dashboard shown
- GIVEN admin role
  WHEN accessing settings
  THEN settings page loads
- Given new user
  When signing up
  Then welcome email sent
## Metadata
- Scenario-Strategy: required"""
        self.assertEqual(validate_spec(content), [])


class TestSpecValidationInMain(unittest.TestCase):
    """Test spec validation integrated into sdd-auto-test.py main()."""

    def _run_main(self, input_data):
        stdin_mock = io.StringIO(json.dumps(input_data))
        stdout_capture = io.StringIO()
        exit_code = 0
        with patch("sys.stdin", stdin_mock), \
             patch("sys.stdout", stdout_capture), \
             patch.object(sys, "argv", ["sdd-auto-test.py"]):
            try:
                main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return exit_code, stdout_capture.getvalue()

    def test_non_code_task_file_ignored(self):
        """Non-.code-task.md Write → no spec warnings (proceeds to source guard)."""
        exit_code, stdout = self._run_main({
            "cwd": "/tmp/proj",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "README.md",
                "content": "no acceptance criteria here",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    def test_valid_spec_no_output(self):
        """Valid .code-task.md → exit 0, no output."""
        content = """## Acceptance Criteria
- Given a When b Then c
- Given d When e Then f
- Given g When h Then i
## Metadata
- Scenario-Strategy: required"""
        exit_code, stdout = self._run_main({
            "cwd": "/tmp/proj",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "sprint.code-task.md",
                "content": content,
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    def test_invalid_spec_emits_warnings(self):
        """Invalid .code-task.md → additionalContext with warnings."""
        content = """## Acceptance Criteria
- Given a When b Then c"""
        exit_code, stdout = self._run_main({
            "cwd": "/tmp/proj",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "sprint.code-task.md",
                "content": content,
            },
        })
        self.assertEqual(exit_code, 0)
        data = json.loads(stdout)
        ctx = data["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Only 1", ctx)
        self.assertIn("Scenario-Strategy", ctx)

    def test_empty_content_ignored(self):
        """Empty content → exit 0, no output."""
        exit_code, stdout = self._run_main({
            "cwd": "/tmp/proj",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "sprint.code-task.md",
                "content": "",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")


if __name__ == "__main__":
    unittest.main()
