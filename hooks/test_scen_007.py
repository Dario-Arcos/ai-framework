#!/usr/bin/env python3
"""SCEN-007 — Bash git-commit guard requires verification-before-completion.

SPEC Section 5 / 3.4 Point 1:
  * `Bash(git commit)` with pending scenarios but no verification → DENY (exit 2).
  * `Bash(git commit --no-verify ...)` → ALLOW with telemetry warning.
  * Verification recorded → ALLOW.
  * No scenarios present → ALLOW (backward compatibility).
  * Non-commit Bash (git status, ls, etc.) → ALLOW.
  * Commit variants (-am, --amend, -s) must all be recognized.

Fail-today design: `sdd-test-guard.py` has no Bash handler — any Bash
tool_name reaches `is_test_file(file_path="")` which returns False, then
the hook exits 0 via the fast-path. Tests in DENY branches assert exit 2
and will fail until the hook implements the `_bash_is_git_commit` guard.
"""
import hashlib
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
sdd_test_guard = importlib.import_module("sdd-test-guard")
import _sdd_scenarios as S
import _sdd_state as State


# ─────────────────────────────────────────────────────────────────
# Fixture — reused scenario shape from test_sdd_scenarios.py
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

SESSION_ID_RAW = "scen-007-session"
SID = hashlib.md5(SESSION_ID_RAW.encode()).hexdigest()[:8]


def _seed_scenarios(cwd):
    """Create `.claude/scenarios/login.scenarios.md` under cwd."""
    d = Path(cwd) / S.SCENARIO_DIR
    d.mkdir(parents=True, exist_ok=True)
    (d / f"login{S.SCENARIO_FILE_SUFFIX}").write_text(_VALID_FILE, encoding="utf-8")


def _invoke_guard(cwd, command, session_id=SESSION_ID_RAW):
    """Invoke sdd-test-guard.main() with a Bash PreToolUse payload.

    Returns (exit_code, stdout, stderr).
    """
    payload = {
        "session_id": session_id,
        "cwd": str(cwd),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }
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
                sdd_test_guard.main()
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
# SCEN-007
# ─────────────────────────────────────────────────────────────────

class TestScen007(unittest.TestCase):
    """Bash(git commit) is gated by verification-before-completion."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="scen-007-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # --- DENY path ----------------------------------------------------

    def test_git_commit_without_verification_denied(self):
        """Scenarios present + no verification + git commit → exit 2."""
        _seed_scenarios(self.tmpdir)
        code, _out, err = _invoke_guard(self.tmpdir, 'git commit -m "x"')
        self.assertEqual(
            code, 2,
            f"expected DENY (exit 2) for git commit without verification; "
            f"got exit {code}; stderr={err!r}",
        )
        lowered = err.lower()
        self.assertTrue(
            any(tok in lowered for tok in ("verification", "git commit", "scenarios")),
            f"stderr missing verification/git commit/scenarios vocab: {err!r}",
        )

    def test_commit_variants_all_denied(self):
        """-am / --amend / -m + -s must all be recognized as commits."""
        _seed_scenarios(self.tmpdir)
        variants = [
            'git commit -am "update"',
            "git commit --amend --no-edit",
            'git commit -m "msg" -s',
            'git commit --message="x"',
            "git commit",
        ]
        for cmd in variants:
            with self.subTest(command=cmd):
                code, _out, err = _invoke_guard(self.tmpdir, cmd)
                self.assertEqual(
                    code, 2,
                    f"expected DENY (exit 2) for variant {cmd!r}; "
                    f"got exit {code}; stderr={err!r}",
                )

    # --- ALLOW paths --------------------------------------------------

    def test_no_verify_bypass_allowed(self):
        """--no-verify is an explicit bypass: exit 0 (telemetry warning optional)."""
        _seed_scenarios(self.tmpdir)
        code, _out, _err = _invoke_guard(
            self.tmpdir, 'git commit --no-verify -m "x"'
        )
        self.assertEqual(
            code, 0,
            f"--no-verify must bypass the guard (exit 0); got {code}",
        )

    def test_verification_recorded_allows_commit(self):
        """verification-before-completion invoked this session → exit 0."""
        _seed_scenarios(self.tmpdir)
        State.write_skill_invoked(
            self.tmpdir, "verification-before-completion", sid=SID
        )
        # Precondition: has_pending_scenarios must now return False.
        self.assertFalse(
            S.has_pending_scenarios(self.tmpdir, sid=SID),
            "precondition: verification record should clear pending state",
        )
        code, _out, err = _invoke_guard(self.tmpdir, 'git commit -m "x"')
        self.assertEqual(
            code, 0,
            f"expected ALLOW (exit 0) with verification recorded; "
            f"got exit {code}; stderr={err!r}",
        )

    def test_no_scenarios_dir_allows_commit(self):
        """No `.claude/scenarios/` → backward compat, exit 0."""
        # Deliberately skip _seed_scenarios — no scenarios dir exists.
        self.assertFalse(
            (Path(self.tmpdir) / S.SCENARIO_DIR).exists(),
            "precondition: scenarios directory must be absent",
        )
        code, _out, err = _invoke_guard(self.tmpdir, 'git commit -m "x"')
        self.assertEqual(
            code, 0,
            f"expected ALLOW (exit 0) when no scenarios exist; "
            f"got exit {code}; stderr={err!r}",
        )

    def test_non_commit_bash_allowed(self):
        """Guard is specific to git commit — other Bash passes through."""
        _seed_scenarios(self.tmpdir)
        benign = [
            "git status",
            "git log --oneline -5",
            "git diff",
            "ls -la",
            "pwd",
            "git commit-tree HEAD^{tree} -m x",  # plumbing command, not porcelain commit
        ]
        for cmd in benign:
            with self.subTest(command=cmd):
                code, _out, err = _invoke_guard(self.tmpdir, cmd)
                self.assertEqual(
                    code, 0,
                    f"non-commit Bash must pass (stderr={err!r}): {cmd!r}",
                )

    def test_commit_lookalikes_not_false_positive(self):
        """`git-commit-wrapper`, `my-git commit`, `echo "git commit"` must NOT match."""
        _seed_scenarios(self.tmpdir)
        lookalikes = [
            "git-commit-wrapper --flag",   # hyphenated tool, not `git commit`
            "my-git commit -m x",          # different binary
            'echo "git commit -m x"',      # quoted string, not an invocation
            "# git commit -m x",           # shell comment
        ]
        for cmd in lookalikes:
            with self.subTest(command=cmd):
                code, _out, err = _invoke_guard(self.tmpdir, cmd)
                self.assertEqual(
                    code, 0,
                    f"lookalike must not trigger guard (stderr={err!r}): {cmd!r}",
                )


if __name__ == "__main__":
    unittest.main()
