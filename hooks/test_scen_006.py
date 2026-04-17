#!/usr/bin/env python3
"""SCEN-006 — TaskUpdate(completed) blocked when scenarios lack verification.

SPEC Section 5 / 3.4 Point 1 — Guard 3:
    `TaskUpdate(status="completed")` with scenarios present but
    `verification-before-completion` NOT recorded in session → DENY with a
    structured stderr message. Otherwise → ALLOW.

Mechanism (to be added to sdd-test-guard.py):

    if tool_name == "TaskUpdate" and tool_input.get("status") == "completed":
        if has_pending_scenarios(cwd):
            if not read_skill_invoked(
                cwd, "verification-before-completion", sid=sid
            ):
                # emit structured stderr + exit 2

This file fails today: the PreToolUse matcher is `Edit|Write|MultiEdit|
NotebookEdit` (hooks.json) and `sdd-test-guard.main()` contains no branch
for TaskUpdate, so it exits 0 on the deny case. The positive "deny" test
(`test_taskupdate_completed_with_scenarios_no_verification_denies`) fails
with `AssertionError: 0 != 2`. The three "allow" tests pass today because
the hook already exits 0 for unmatched tool names — they serve as
regression guards once the TaskUpdate branch lands, ensuring the new
branch scopes itself to (status=="completed") ∧ scenarios-present ∧
verification-missing and does not over-block legitimate transitions.
"""
import importlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _sdd_scenarios as S
import _sdd_state as State


# ─────────────────────────────────────────────────────────────────
# Fixtures — pattern reused from test_sdd_scenarios.py / test_scen_003.py
# ─────────────────────────────────────────────────────────────────

_VALID_FILE = """\
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

RAW_SID = "scen-006-session"


def _invoke_guard(payload, cwd):
    """Invoke sdd-test-guard.main() with captured stdio. Returns (code, stderr)."""
    guard = importlib.import_module("sdd-test-guard")
    stdin_buf = io.StringIO(json.dumps(payload))
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    old_stdin = sys.stdin
    old_env = os.environ.get("CLAUDE_PROJECT_DIR")
    sys.stdin = stdin_buf
    os.environ["CLAUDE_PROJECT_DIR"] = str(cwd)
    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            try:
                guard.main()
                code = 0
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
    finally:
        sys.stdin = old_stdin
        if old_env is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = old_env

    return code, stderr_buf.getvalue()


# ─────────────────────────────────────────────────────────────────
# SCEN-006
# ─────────────────────────────────────────────────────────────────

class TestScen006(unittest.TestCase):
    """TaskUpdate(completed) must be gated by verification-before-completion
    when scenarios exist; transparent to all other shapes."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="scen-006-")
        # Hook re-hashes session_id via extract_session_id → write state
        # under the same hashed form so read_skill_invoked finds it.
        self.hashed_sid = State.extract_session_id({"session_id": RAW_SID})

    def tearDown(self):
        try:
            State.skill_invoked_path(
                self.tmpdir, "verification-before-completion",
                sid=self.hashed_sid,
            ).unlink(missing_ok=True)
        except OSError:
            pass
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_scenario(self):
        d = Path(self.tmpdir) / S.SCENARIO_DIR
        d.mkdir(parents=True, exist_ok=True)
        (d / f"login{S.SCENARIO_FILE_SUFFIX}").write_text(
            _VALID_FILE, encoding="utf-8",
        )

    def _taskupdate_payload(self, status="completed"):
        return {
            "session_id": RAW_SID,
            "cwd": self.tmpdir,
            "tool_name": "TaskUpdate",
            "tool_input": {"status": status, "taskId": "T1"},
        }

    # ─────────────────────────────────────────────────────────
    # Positive: DENY — scenarios present, verification absent
    # ─────────────────────────────────────────────────────────

    def test_taskupdate_completed_with_scenarios_no_verification_denies(self):
        """TaskUpdate(completed) + scenarios + no verification → exit 2 + structured message.

        FAILS today: sdd-test-guard.py has no TaskUpdate branch → exits 0.
        Expected failure: `AssertionError: 0 != 2`.
        """
        self._write_scenario()
        # Deliberately do NOT write verification-before-completion skill state.

        code, stderr = _invoke_guard(self._taskupdate_payload(), self.tmpdir)

        self.assertEqual(
            code, 2,
            f"Expected DENY (exit 2) when TaskUpdate(completed) runs with "
            f"pending scenarios and no verification. Got exit={code}, "
            f"stderr={stderr!r}. FAILURE MODE: TaskUpdate completion guard "
            f"not implemented in sdd-test-guard.py.",
        )
        stderr_low = stderr.lower()
        self.assertTrue(
            "verification" in stderr_low or "scenarios" in stderr_low,
            f"Structured message must mention verification or scenarios. "
            f"Got: {stderr!r}. FAILURE MODE: guard emits a generic error "
            f"without citing the missing skill or scenario artifacts.",
        )

    # ─────────────────────────────────────────────────────────
    # Allowed: verification recorded
    # ─────────────────────────────────────────────────────────

    def test_taskupdate_completed_with_verification_allows(self):
        """TaskUpdate(completed) + scenarios + verification recorded → exit 0."""
        self._write_scenario()
        State.write_skill_invoked(
            self.tmpdir, "verification-before-completion",
            sid=self.hashed_sid,
        )

        code, stderr = _invoke_guard(self._taskupdate_payload(), self.tmpdir)

        self.assertEqual(
            code, 0,
            f"Verification recorded → guard must allow. Got exit={code}, "
            f"stderr={stderr!r}. FAILURE MODE: guard over-blocks when the "
            f"required skill IS recorded in session state.",
        )

    # ─────────────────────────────────────────────────────────
    # Allowed: no scenarios at all (backward compat)
    # ─────────────────────────────────────────────────────────

    def test_taskupdate_completed_without_scenarios_allows(self):
        """No `.claude/scenarios/` dir → backward-compat passthrough (exit 0)."""
        # Explicitly assert the directory is absent so the fixture intent
        # survives future setUp edits.
        self.assertFalse(
            (Path(self.tmpdir) / S.SCENARIO_DIR).exists(),
            "precondition: scenarios dir must not exist for backward-compat path",
        )

        code, stderr = _invoke_guard(self._taskupdate_payload(), self.tmpdir)

        self.assertEqual(
            code, 0,
            f"Projects without scenarios must be unaffected. Got exit={code}, "
            f"stderr={stderr!r}. FAILURE MODE: guard blocks unconditionally "
            f"on TaskUpdate(completed), breaking every project that has not "
            f"adopted scenarios yet.",
        )

    # ─────────────────────────────────────────────────────────
    # Allowed: status != "completed"
    # ─────────────────────────────────────────────────────────

    def test_taskupdate_in_progress_with_scenarios_no_verification_allows(self):
        """status="in_progress" must not trigger the completion gate (exit 0)."""
        self._write_scenario()
        # No verification recorded — but status is not "completed", so guard
        # must remain silent. The gate is scoped to the completion transition.

        code, stderr = _invoke_guard(
            self._taskupdate_payload(status="in_progress"), self.tmpdir,
        )

        self.assertEqual(
            code, 0,
            f"Non-completion status must bypass the gate. Got exit={code}, "
            f"stderr={stderr!r}. FAILURE MODE: guard triggers on every "
            f"TaskUpdate instead of scoping to status=='completed'.",
        )


if __name__ == "__main__":
    unittest.main()
