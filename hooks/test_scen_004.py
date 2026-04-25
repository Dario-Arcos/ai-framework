#!/usr/bin/env python3
"""SCEN-004: scenario gate in task-completed.py.

SPEC Section 5 SCEN-004:
    All scenarios valid + verification invoked → completion accepted.
    Coverage uncovered → warning only.

Mechanism (SPEC 3.4 point 2 + 4 phase 3.3-3.4):
    task-completed.py, before the existing gate loop, must:
      1. Detect `.claude/scenarios/` presence.
      2. Validate each scenario file via _sdd_scenarios.validate_scenario_file.
         Any invalid file → exit 2 with structured message.
      3. Require read_skill_invoked(cwd, "verification-before-completion",
         sid=<hashed_sid>) truthy. Otherwise → exit 2 mentioning verification.
      4. Emit telemetry "scenario_gate_passed".
      5. Once scenarios pass, coverage becomes informational: uncovered files
         → stderr warning + telemetry "coverage_signal", NOT exit 2.

These tests must FAIL today — the scenario gate does not yet exist in
task-completed.py. Each test asserts an observable outcome that can only
happen after Phase 3.3-3.4 lands. The failure mode flags "scenario gate
not implemented".

Path: non-Ralph completion (teammate_name set, no .ralph/config.sh). Chosen
because the non-Ralph path is the minimal setup to exercise the pre-gate
scenario check and the coverage-warning handoff.
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
import _sdd_state
import _sdd_scenarios


_VALID_SCENARIO_BODY = """\
---
name: login-validation
created_by: orchestrator
created_at: 2026-04-16T10:00:00Z
---

## SCEN-001: successful login
**Given**: unregistered anonymous user
**When**: POST /login with valid email + password
**Then**: response 200 with session token, redirect to /dashboard
**Evidence**: HTTP response body, cookies set
"""

_INVALID_SCENARIO_BODY = "no frontmatter, no SCEN blocks, just prose.\n"


class TestScen004(unittest.TestCase):
    """SCEN-004: scenario gate enforces validity + verification, warns on coverage.

    Shape mirrors TestTaskCompletedRunsFreshTests + TestRalphMultiGateCascade
    (integration patterns): real tmpdir, real scenario files, real session
    state via _sdd_state writers. The hook is invoked via stdin with the
    non-Ralph path (teammate_name set, no .ralph/config.sh).
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen-004-")
        self.raw_sid = "scen004-session"
        # Hook re-hashes session_id via extract_session_id — verification
        # state must be written under the hashed form.
        self.hashed_sid = _sdd_state.extract_session_id(
            {"session_id": self.raw_sid}
        )
        # Scenarios dir + one valid file (shared across happy + missing-verification).
        self._scen_dir = Path(self.tmpdir) / ".ralph/specs/scen004/scenarios"
        self._scen_dir.mkdir(parents=True)
        (self._scen_dir / f"login{_sdd_scenarios.SCENARIO_FILE_SUFFIX}").write_text(
            _VALID_SCENARIO_BODY, encoding="utf-8"
        )

    def tearDown(self):
        # Clean temp state artifacts tied to this cwd.
        try:
            _sdd_state.state_path(self.tmpdir).unlink(missing_ok=True)
            _sdd_state.skill_invoked_path(
                self.tmpdir, "verification-before-completion",
                sid=self.hashed_sid,
            ).unlink(missing_ok=True)
        except OSError:
            pass
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # ─────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────

    def _stdin(self, **overrides):
        data = {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
            "session_id": self.raw_sid,
        }
        data.update(overrides)
        return io.StringIO(json.dumps(data))

    def _seed_passing_test_state(self):
        """Write a fresh passing test state so the existing test gate passes.

        Without this, the non-Ralph path would try to run a real test command
        and the scenario-gate assertion would be masked by missing pytest.
        """
        _sdd_state.write_state(
            self.tmpdir, True, "1 passed",
            started_at=None, raw_output="1 passed",
        )

    def _mark_verification_invoked(self):
        _sdd_state.write_skill_invoked(
            self.tmpdir, "verification-before-completion", sid=self.hashed_sid,
        )

    def _run_main(self):
        """Invoke task_completed.main() with captured stderr; return (exit_code, stderr)."""
        stderr_buf = io.StringIO()
        exit_code = 0
        env_patch = {"CLAUDE_PROJECT_DIR": self.tmpdir}
        with patch("sys.stdin", self._stdin()), \
             patch("sys.stderr", stderr_buf), \
             patch.dict(os.environ, env_patch):
            try:
                task_completed.main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return exit_code, stderr_buf.getvalue()

    # ─────────────────────────────────────────────────────────
    # Happy path: valid scenarios + verification invoked + coverage warn only
    # ─────────────────────────────────────────────────────────

    # Force non-Ralph source-edit path so the hook exercises the scenario gate
    # (ralph guard is inert without .ralph/; this patch is defensive alignment
    # with the Ralph-path pattern in test_sdd_integration.py:1267).
    @patch.object(task_completed, "_has_source_edits", return_value=True)
    def test_valid_scenarios_plus_verification_accepts_completion(self, _mock_edits):
        """Valid scenarios + verification invoked + uncovered files → exit 0 + warn."""
        self._seed_passing_test_state()
        self._mark_verification_invoked()

        # Record an uncovered source edit so the post-scenarios coverage branch
        # has something to warn about (SPEC: "Coverage uncovered → warning only").
        # record_file_edit stores under hashed sid — consistent with hook read.
        try:
            _sdd_state.record_file_edit = _sdd_state.record_file_edit  # type: ignore[attr-defined]
        except AttributeError:
            # _sdd_state exposes record_file_edit via _sdd_detect re-export;
            # fall through to direct import if needed.
            pass
        import _sdd_detect
        _sdd_detect.record_file_edit(
            self.tmpdir, "src/feature.py", self.hashed_sid,
        )

        exit_code, stderr = self._run_main()

        self.assertEqual(
            exit_code, 0,
            f"Happy path must accept completion (scenario gate passed, "
            f"coverage informational). Got exit={exit_code}, stderr={stderr!r}. "
            f"FAILURE MODE: scenario gate not implemented — hook either still "
            f"blocks on coverage (exit 2) or never emits the coverage-signal "
            f"warning branch."
        )
        stderr_low = stderr.lower()
        self.assertTrue(
            ("coverage signal" in stderr_low)
            or ("informational" in stderr_low)
            or ("coverage_signal" in stderr_low),
            f"Stderr must announce coverage as informational (not a block). "
            f"Got: {stderr!r}. FAILURE MODE: coverage warning branch absent — "
            f"hook still uses the pre-SCEN-004 blocking coverage gate."
        )

    # ─────────────────────────────────────────────────────────
    # Invalid scenario blocks completion
    # ─────────────────────────────────────────────────────────

    @patch.object(task_completed, "_has_source_edits", return_value=True)
    def test_invalid_scenario_file_blocks_completion(self, _mock_edits):
        """Malformed scenario file (no SCEN blocks) → exit 2 citing the file."""
        self._seed_passing_test_state()
        self._mark_verification_invoked()

        # Introduce a malformed scenario file alongside the valid one.
        bad_name = f"broken{_sdd_scenarios.SCENARIO_FILE_SUFFIX}"
        (self._scen_dir / bad_name).write_text(
            _INVALID_SCENARIO_BODY, encoding="utf-8",
        )

        exit_code, stderr = self._run_main()

        self.assertEqual(
            exit_code, 2,
            f"Invalid scenario must block completion with exit 2. Got "
            f"exit={exit_code}, stderr={stderr!r}. FAILURE MODE: scenario "
            f"validation not wired into task-completed.py (the pre-gate "
            f"validator check is missing — any scenario file is accepted)."
        )
        self.assertIn(
            "broken", stderr,
            f"Structured message must mention the invalid file. Got: "
            f"{stderr!r}. FAILURE MODE: scenario gate absent or emits a "
            f"generic message without the offending filename.",
        )

    # ─────────────────────────────────────────────────────────
    # Missing verification blocks completion
    # ─────────────────────────────────────────────────────────

    @patch.object(task_completed, "_has_source_edits", return_value=True)
    def test_missing_verification_blocks_completion(self, _mock_edits):
        """Scenarios valid but verification-before-completion NOT invoked → exit 2."""
        self._seed_passing_test_state()
        # Deliberately DO NOT call self._mark_verification_invoked().

        exit_code, stderr = self._run_main()

        self.assertEqual(
            exit_code, 2,
            f"Missing verification skill must block completion with exit 2. "
            f"Got exit={exit_code}, stderr={stderr!r}. FAILURE MODE: "
            f"verification-before-completion enforcement not wired — hook "
            f"proceeds past the scenario gate without checking the skill."
        )
        self.assertIn(
            "verification", stderr.lower(),
            f"Error message must cite verification. Got: {stderr!r}. "
            f"FAILURE MODE: scenario gate present but verification check "
            f"missing from failure message.",
        )


if __name__ == "__main__":
    unittest.main()
