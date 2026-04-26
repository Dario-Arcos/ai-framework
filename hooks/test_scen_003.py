#!/usr/bin/env python3
"""SCEN-003 — Amend via sop-reviewer marker with matching git_sha.

SPEC Section 5 / 3.3 / 3.4:
  * A valid amend marker at `.claude/scenarios/.amends/{stem}-{sha}.marker`
    permits an Edit to a scenario file when `sha` is a prefix of HEAD.
  * The sop-reviewer skill must have been invoked in the current session.
  * A new commit changes HEAD → stale marker SHA no longer matches → DENY.

This test fails today: `sdd-test-guard.py` does not yet consult
`_sdd_scenarios.check_amend_marker` on scenario-file edits, so it exits 0
unconditionally on the two failure branches.
"""
import hashlib
import importlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _sdd_scenarios as S
import _sdd_state as State


# ─────────────────────────────────────────────────────────────────
# Fixtures — reused from test_sdd_scenarios.py patterns
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

_AMENDED_FILE = _VALID_FILE + """
## SCEN-002: invalid credentials
**Given**: registered user
**When**: POST /login with wrong password
**Then**: response 401, message "Invalid credentials"
**Evidence**: HTTP response body
"""

SESSION_ID_RAW = "scen-003-session"
SID = hashlib.md5(SESSION_ID_RAW.encode()).hexdigest()[:8]


def _git_init_with_commit(cwd, rel_path, content):
    subprocess.run(["git", "-C", str(cwd), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(cwd), "config", "user.email", "t@t.com"], check=True)
    subprocess.run(["git", "-C", str(cwd), "config", "user.name", "tester"], check=True)
    full = Path(cwd) / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(cwd), "add", rel_path], check=True)
    subprocess.run(["git", "-C", str(cwd), "commit", "-q", "-m", "init"], check=True)
    result = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def _advance_head(cwd, message="advance"):
    readme = Path(cwd) / "README.md"
    readme.write_text(f"{message}\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(cwd), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(cwd), "commit", "-q", "-m", message], check=True)
    result = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def _invoke_guard(cwd, file_path, new_text, session_id=SESSION_ID_RAW):
    """Invoke sdd-test-guard.py main() as the hook would.

    Returns (exit_code, stdout, stderr). Raises nothing — SystemExit is caught.
    """
    payload = {
        "session_id": session_id,
        "cwd": str(cwd),
        "tool_name": "Edit",
        "tool_input": {
            "file_path": str(file_path),
            "old_string": "placeholder-old",
            "new_string": new_text,
        },
    }
    guard = importlib.import_module("sdd-test-guard")

    stdin_buf = io.StringIO(json.dumps(payload))
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    old_stdin, old_env = sys.stdin, os.environ.get("CLAUDE_PROJECT_DIR")
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

    return code, stdout_buf.getvalue(), stderr_buf.getvalue()


# ─────────────────────────────────────────────────────────────────
# SCEN-003
# ─────────────────────────────────────────────────────────────────

class TestScen003(unittest.TestCase):
    """Amend marker must gate Edit access to scenario files per HEAD SHA."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="scen-003-")
        self.rel = ".ralph/specs/scen003/scenarios/login.scenarios.md"
        self.scenario_path = Path(self.tmpdir) / self.rel
        self.sha1 = _git_init_with_commit(self.tmpdir, self.rel, _VALID_FILE)
        # Phase 10: amend markers are sibling-scoped to the scenario file.
        self.markers_dir = S.amend_marker_dir(self.tmpdir, self.rel)
        self.markers_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_marker(self, sha_prefix):
        """Pre-Fix-1 helper: writes EMPTY-body marker. Post-Fix-1 these
        markers are rejected (the legacy bypass is closed). Tests that
        need a positive case use `_write_valid_marker` below.
        """
        (self.markers_dir / f"login-{sha_prefix}.marker").write_text("", encoding="utf-8")

    def _write_valid_marker(self, sha_prefix):
        """Write a four-gate-issued marker (HMAC-bound 4/4 PASS payload)."""
        gate_verdicts = {
            "staleness": "PASS", "evidence": "PASS",
            "invariant": "PASS", "reversibility": "PASS",
        }
        payload = {
            "scenario_rel": self.rel,
            "head_sha": sha_prefix,
            "gate_verdicts": gate_verdicts,
            "judge_confidence": 95,
            "class_label": "safe_clarification",
        }
        payload["hmac"] = S._expected_marker_hmac(
            self.tmpdir, payload["scenario_rel"], payload["head_sha"],
            payload["gate_verdicts"], payload["judge_confidence"],
            payload["class_label"],
        )
        (self.markers_dir / f"login-{sha_prefix}.marker").write_text(
            json.dumps(payload, sort_keys=True), encoding="utf-8"
        )

    def test_valid_marker_with_sop_reviewer_allows_edit(self):
        """Four-gate-issued marker (HMAC-bound 4/4 PASS) → Edit permitted.

        Pre-Fix-1 this test asserted that an EMPTY-body marker plus a
        recorded `sop-reviewer` skill invocation was sufficient. That
        was the agent-accessible bypass: any session could invoke
        `/sop-reviewer` and write any file with the right name. Fix 1
        closes that path — only markers with the four-gate emission
        payload + HMAC are honored.
        """
        self._write_valid_marker(self.sha1[:10])
        # Sanity check: marker check itself passes (HMAC-bound payload)
        self.assertTrue(
            S.check_amend_marker(self.tmpdir, self.rel),
            "precondition: HMAC-bound marker should validate",
        )

        self.scenario_path.write_text(_AMENDED_FILE, encoding="utf-8")
        code, _out, err = _invoke_guard(self.tmpdir, self.scenario_path, _AMENDED_FILE)
        self.assertEqual(code, 0, f"expected allow, got exit {code}; stderr={err!r}")

    def test_new_commit_invalidates_marker_denies_edit(self):
        """SHA_1 marker → new commit → HEAD is SHA_2 → stale marker → DENY (exit 2)."""
        self._write_valid_marker(self.sha1[:10])

        sha2 = _advance_head(self.tmpdir, "advance past marker")
        self.assertNotEqual(
            self.sha1, sha2,
            "precondition: HEAD must actually advance",
        )
        self.assertFalse(
            S.check_amend_marker(self.tmpdir, self.rel, sid=SID),
            "precondition: marker must be stale after new commit",
        )

        self.scenario_path.write_text(_AMENDED_FILE, encoding="utf-8")
        code, _out, err = _invoke_guard(self.tmpdir, self.scenario_path, _AMENDED_FILE)
        self.assertEqual(
            code, 2,
            f"expected DENY (exit 2) for stale marker, got exit {code}; stderr={err!r}",
        )

    def test_valid_sha_without_sop_reviewer_denies_edit(self):
        """Empty-body marker (no HMAC payload) → DENY.

        Pre-Fix-1 this test relied on the `sop-reviewer` skill having
        been recorded; post-Fix-1 the sop-reviewer-recorded check is
        gone (the four-gate HMAC payload IS the authority). An empty-
        body marker is the canonical legacy bypass attempt and must
        be rejected.
        """
        self._write_marker(self.sha1[:10])  # default empty body
        self.assertFalse(
            S.check_amend_marker(self.tmpdir, self.rel),
            "precondition: empty-body marker must fail post-Fix-1",
        )

        self.scenario_path.write_text(_AMENDED_FILE, encoding="utf-8")
        code, _out, err = _invoke_guard(self.tmpdir, self.scenario_path, _AMENDED_FILE)
        self.assertEqual(
            code, 2,
            f"expected DENY (exit 2) when sop-reviewer missing, got exit {code}; stderr={err!r}",
        )


if __name__ == "__main__":
    unittest.main()
