#!/usr/bin/env python3
"""SCEN-008: task-completed rejects scenario files with zero parseable SCEN blocks.

SPEC Section 3.3 shape rule: a scenario file must contain >= 1
`## SCEN-NNN: <title>` block. A file with only frontmatter is vacuous and
MUST fail validation. SPEC Section 3.4 / 4 Phase 3.3 places the enforcement
inside `task-completed.py` before the existing gate loop, so an invalid
scenario file blocks completion regardless of test/lint/typecheck state.

Status today:
  * Tests #1-#3 FAIL: task-completed has no scenario-validation gate yet,
    so a frontmatter-only scenarios file is silently accepted (exit 0).
  * Test #4 PASSES: `_sdd_scenarios.validate_scenario_file` already returns
    `(False, ["no parseable scenarios"])` — this test locks in the contract
    the new gate will consume.
"""
import importlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
task_completed = importlib.import_module("task-completed")
import _sdd_scenarios
import _sdd_state


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────

_VACUOUS_FRONTMATTER_ONLY = """\
---
name: empty
---

No scenario blocks here.
"""

_VACUOUS_EMPTY_BODY = """\
---
name: empty
---
"""

_VALID_SCENARIO_FILE = """\
---
name: login-validation
---

## SCEN-001: successful login
**Given**: unregistered anonymous user
**When**: POST /login with valid email and password
**Then**: response 200 with session token, redirect to /dashboard
**Evidence**: HTTP response body, cookies set
"""


def _write_scenario(cwd, name, content):
    """Create .claude/scenarios/<name>.scenarios.md under cwd."""
    d = Path(cwd) / _sdd_scenarios.SCENARIO_DIR
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{name}{_sdd_scenarios.SCENARIO_FILE_SUFFIX}"
    p.write_text(content, encoding="utf-8")
    return p


def _run_task_completed(input_data):
    """Invoke task-completed.main() with JSON stdin; return (exit, stdout, stderr).

    Mirrors the env/stdin patching idiom from test_sdd_integration.py so that
    CLAUDE_PROJECT_DIR does not override the tmpdir under test.
    """
    stdin_mock = io.StringIO(json.dumps(input_data))
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    exit_code = 0

    env_patch = {}
    if "cwd" in input_data:
        env_patch["CLAUDE_PROJECT_DIR"] = input_data["cwd"]

    with patch("sys.stdin", stdin_mock), \
         patch("sys.stdout", stdout_capture), \
         patch("sys.stderr", stderr_capture), \
         patch.dict(os.environ, env_patch):
        try:
            task_completed.main()
        except SystemExit as e:
            exit_code = e.code if e.code is not None else 0

    return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()


def _prime_passing_state(cwd, sid):
    """Seed a passing test state so the existing test gate cannot block first.

    Without this, _handle_non_ralph_completion would run fresh tests against
    the bare tmpdir and the fact that no test command exists would pass-through
    — but we still write state to be robust against future detection changes.
    """
    _sdd_state.write_state(cwd, passing=True, summary="1 passed", sid=sid)
    _sdd_state.write_skill_invoked(cwd, "sop-code-assist", sid=sid)


# ─────────────────────────────────────────────────────────────────
# TESTS
# ─────────────────────────────────────────────────────────────────

class TestScen008(unittest.TestCase):
    """SCEN-008: frontmatter-only scenario files must block task completion."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen008-")
        self.sid_input = "scen008-session"
        # _sdd_state hashes the provided session_id; pre-compute for state writes
        self.sid = _sdd_state.extract_session_id({"session_id": self.sid_input})

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # Test #1 — FAILS today (gate not yet implemented)
    @patch.object(task_completed, "_has_source_edits", return_value=True)
    def test_vacuous_frontmatter_only_file_blocks_completion(self, _mock_edits):
        """A file containing ONLY frontmatter + prose (no SCEN blocks) → exit 2."""
        _write_scenario(self.tmpdir, "empty", _VACUOUS_FRONTMATTER_ONLY)
        _prime_passing_state(self.tmpdir, self.sid)

        exit_code, _stdout, stderr = _run_task_completed({
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
            "session_id": self.sid_input,
        })

        self.assertEqual(
            exit_code, 2,
            f"Expected exit 2 (scenario validation should block); got {exit_code}. "
            f"stderr={stderr!r}",
        )
        lowered = stderr.lower()
        self.assertTrue(
            "no parseable scenarios" in lowered or "invalid" in lowered,
            f"stderr must explain validation failure; got {stderr!r}",
        )
        self.assertIn(
            "empty.scenarios.md", stderr,
            f"stderr must identify the offending file; got {stderr!r}",
        )

    # Test #2 — FAILS today (gate not yet implemented)
    @patch.object(task_completed, "_has_source_edits", return_value=True)
    def test_empty_body_after_frontmatter_blocks_completion(self, _mock_edits):
        """Frontmatter with zero body content (not even prose) also blocks."""
        _write_scenario(self.tmpdir, "bare", _VACUOUS_EMPTY_BODY)
        _prime_passing_state(self.tmpdir, self.sid)

        exit_code, _stdout, stderr = _run_task_completed({
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
            "session_id": self.sid_input,
        })

        self.assertEqual(
            exit_code, 2,
            f"Expected exit 2 on bare frontmatter; got {exit_code}. "
            f"stderr={stderr!r}",
        )
        lowered = stderr.lower()
        self.assertTrue(
            "no parseable scenarios" in lowered or "invalid" in lowered,
            f"stderr must explain validation failure; got {stderr!r}",
        )
        self.assertIn(
            "bare.scenarios.md", stderr,
            f"stderr must identify the offending file; got {stderr!r}",
        )

    # Test #3 — FAILS today (gate not yet implemented)
    @patch.object(task_completed, "_has_source_edits", return_value=True)
    def test_mixed_dir_invalid_file_blocks_despite_valid_sibling(self, _mock_edits):
        """One valid + one vacuous in the same dir → invalid file still blocks."""
        _write_scenario(self.tmpdir, "login", _VALID_SCENARIO_FILE)
        _write_scenario(self.tmpdir, "empty", _VACUOUS_FRONTMATTER_ONLY)
        _prime_passing_state(self.tmpdir, self.sid)

        exit_code, _stdout, stderr = _run_task_completed({
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
            "session_id": self.sid_input,
        })

        self.assertEqual(
            exit_code, 2,
            f"Expected exit 2 — invalid sibling must block even with valid file "
            f"present; got {exit_code}. stderr={stderr!r}",
        )
        self.assertIn(
            "empty.scenarios.md", stderr,
            f"stderr must identify the specific offending file (empty), "
            f"not the valid one (login); got {stderr!r}",
        )
        # The valid file should not be flagged as the source of failure.
        self.assertNotIn(
            "login.scenarios.md: no parseable scenarios", stderr,
            f"Valid file must not be falsely flagged; got {stderr!r}",
        )

    # Test #4 — PASSES today: documents the already-shipped contract.
    def test_validate_scenario_file_contract_on_vacuous_fixture(self):
        """_sdd_scenarios.validate_scenario_file already rejects vacuous files.

        This is the CI-safety test: the gate in task-completed will call this
        function, so the contract must hold before we wire it up.
        """
        p = _write_scenario(self.tmpdir, "empty", _VACUOUS_FRONTMATTER_ONLY)
        valid, errors = _sdd_scenarios.validate_scenario_file(p)

        self.assertFalse(valid, "Frontmatter-only file must be invalid")
        self.assertIn(
            "no parseable scenarios", errors,
            f"Expected canonical error string; got {errors!r}",
        )


if __name__ == "__main__":
    unittest.main()
