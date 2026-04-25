#!/usr/bin/env python3
"""SCEN-001 — write-once scenario guard (SPEC §5).

Scenario: scenario file Edit → PreToolUse compares content hash vs
`git log --diff-filter=A` baseline → DENY if different AND no valid
amend marker.

This test is RED today: the guard does not yet exist inside
sdd-test-guard.py. Once the guard lands, the hook must exit with code 2
and surface "write-once" / "scenario" / "amend" in stderr when a
committed scenario file is modified on disk without an amend marker.
"""
import importlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Probe import — skip rather than crash collection if the hook is
# somehow unloadable (env drift, dep change, etc.).
try:
    sdd_test_guard = importlib.import_module("sdd-test-guard")
    _IMPORT_OK = True
    _IMPORT_ERR = ""
except Exception as exc:  # pragma: no cover - defensive
    sdd_test_guard = None
    _IMPORT_OK = False
    _IMPORT_ERR = repr(exc)

import _sdd_scenarios as S  # noqa: E402

# Phase 10 fixture path: scenarios live under spec folders.
_SCENARIO_DIR = ".ralph/specs/scen001/scenarios"


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


def _git_init_with_commit(cwd, rel_path, content):
    """Initialize a git repo at cwd and commit the given file."""
    subprocess.run(["git", "-C", str(cwd), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(cwd), "config", "user.email", "t@t.com"], check=True,
    )
    subprocess.run(
        ["git", "-C", str(cwd), "config", "user.name", "tester"], check=True,
    )
    full = Path(cwd) / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(cwd), "add", rel_path], check=True)
    subprocess.run(
        ["git", "-C", str(cwd), "commit", "-q", "-m", "init"], check=True,
    )


def _run_hook_stdin(hook_main, payload):
    """Run hook main() with JSON stdin, capture stdout/stderr + exit code."""
    stdin_mock = io.StringIO(json.dumps(payload))
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    exit_code = 0

    env_patch = {}
    if "cwd" in payload:
        env_patch["CLAUDE_PROJECT_DIR"] = payload["cwd"]

    with patch("sys.stdin", stdin_mock), \
         patch("sys.stdout", stdout_capture), \
         patch("sys.stderr", stderr_capture), \
         patch.dict(os.environ, env_patch):
        try:
            hook_main()
        except SystemExit as e:
            exit_code = e.code if e.code is not None else 0

    return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()


@unittest.skipUnless(_IMPORT_OK, f"sdd-test-guard not importable: {_IMPORT_ERR}")
class TestScen001(unittest.TestCase):
    """SCEN-001: PreToolUse must block divergent scenario Edit/Write."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen001-")
        self.rel = f"{_SCENARIO_DIR}/login{S.SCENARIO_FILE_SUFFIX}"
        # Establish baseline: commit the valid scenario content.
        _git_init_with_commit(self.tmpdir, self.rel, _VALID_FILE)
        self.scenario_path = Path(self.tmpdir) / self.rel

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_edit_on_divergent_scenario_denied(self):
        """Disk bytes differ from baseline + no amend marker → exit 2."""
        # Mutate disk content without creating an amend marker.
        self.scenario_path.write_text(
            _VALID_FILE + "\n## SCEN-002: drift\n**When**: x\n**Then**: y\n",
            encoding="utf-8",
        )
        self.assertNotEqual(
            S.current_file_hash(self.scenario_path),
            S.scenario_baseline_hash(self.tmpdir, self.rel),
            "Precondition: disk hash must diverge from git baseline",
        )
        self.assertFalse(
            S.check_amend_marker(self.tmpdir, self.rel),
            "Precondition: no amend marker recorded",
        )

        exit_code, _, stderr = _run_hook_stdin(sdd_test_guard.main, {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(self.scenario_path)},
            "cwd": self.tmpdir,
            "session_id": "test-sess",
        })

        self.assertEqual(
            exit_code, 2,
            f"Expected exit 2 (DENY) for divergent scenario Edit; "
            f"got {exit_code}. stderr={stderr!r}",
        )
        stderr_lower = stderr.lower()
        self.assertTrue(
            any(k in stderr_lower for k in ("write-once", "scenario", "amend")),
            f"stderr must mention write-once/scenario/amend guidance; "
            f"got: {stderr!r}",
        )

    def test_write_on_divergent_scenario_denied(self):
        """Same invariant via Write tool (full replacement)."""
        self.scenario_path.write_text("totally different bytes\n", encoding="utf-8")

        exit_code, _, stderr = _run_hook_stdin(sdd_test_guard.main, {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(self.scenario_path),
                "content": "totally different bytes\n",
            },
            "cwd": self.tmpdir,
            "session_id": "test-sess",
        })

        self.assertEqual(
            exit_code, 2,
            f"Expected exit 2 for divergent scenario Write; "
            f"got {exit_code}. stderr={stderr!r}",
        )
        stderr_lower = stderr.lower()
        self.assertTrue(
            any(k in stderr_lower for k in ("write-once", "scenario", "amend")),
            f"stderr must mention write-once/scenario/amend guidance; "
            f"got: {stderr!r}",
        )


@unittest.skipUnless(_IMPORT_OK, f"sdd-test-guard import failed: {_IMPORT_ERR}")
class TestScen001SymlinkHardening(unittest.TestCase):
    """Codex Phase 3 H1 — symlinked scenario files silently bypass the
    write-once contract (edits land on the target, baseline hash
    unchanged). The guard must reject Edit/Write when the scenario path
    is a symlink.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="scen001-sym-")
        self.rel = f"{_SCENARIO_DIR}/login{S.SCENARIO_FILE_SUFFIX}"
        _git_init_with_commit(self.tmpdir, self.rel, _VALID_FILE)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_symlink_scenario_file_rejected(self):
        """Replacing a scenario file with a symlink must be denied."""
        scen = Path(self.tmpdir) / self.rel
        scen.unlink()
        target = Path(self.tmpdir) / "fake.md"
        target.write_text("content", encoding="utf-8")
        scen.symlink_to(target)

        exit_code, _stdout, stderr = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(scen),
                "old_string": "a",
                "new_string": "b",
            },
            "session_id": "sess-sym",
        })
        self.assertEqual(exit_code, 2,
            f"Symlinked scenario edit must be denied; stderr={stderr!r}")
        self.assertIn("symlink", stderr.lower(),
            f"stderr must mention symlink; got: {stderr!r}")


if __name__ == "__main__":
    unittest.main()
