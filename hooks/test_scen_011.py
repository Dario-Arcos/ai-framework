#!/usr/bin/env python3
"""SCEN-011 — PreToolUse predicts post-edit hash BEFORE disk mutation.

Unlike SCEN-001 (which pre-mutates disk to simulate post-edit state),
this test verifies the write-once guard against REAL PreToolUse timing:
the hook fires BEFORE the Edit/Write/MultiEdit tool applies, so disk is
still at baseline. The hook must simulate the edit via tool_input and
deny if the predicted hash diverges from baseline.

Coverage gap closed: hooks/sdd-test-guard.py:387-391 compared only the
on-disk hash. At real PreToolUse timing, disk == baseline → no denial
→ Edit tool proceeds. Dogfood A1 confirmed this defect.

Red-green contract:
  1. This file must FAIL against the pre-fix hook (disk still at baseline
     → current_file_hash matches → guard silently allows).
  2. After fix, hook reads disk + simulates edit + hashes predicted bytes.
  3. Reverting the fix must make these tests fail again (true red-green).
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

try:
    sdd_test_guard = importlib.import_module("sdd-test-guard")
    _IMPORT_OK = True
    _IMPORT_ERR = ""
except Exception as exc:  # pragma: no cover - defensive
    sdd_test_guard = None
    _IMPORT_OK = False
    _IMPORT_ERR = repr(exc)

import _sdd_scenarios as S  # noqa: E402


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
    subprocess.run(["git", "-C", str(cwd), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(cwd), "config", "user.email", "t@t.com"], check=True)
    subprocess.run(["git", "-C", str(cwd), "config", "user.name", "tester"], check=True)
    full = Path(cwd) / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(cwd), "add", rel_path], check=True)
    subprocess.run(["git", "-C", str(cwd), "commit", "-q", "-m", "init"], check=True)


def _run_hook_stdin(hook_main, payload):
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
class TestScen011PreEditSimulation(unittest.TestCase):
    """Guard must simulate the edit from tool_input, not rely on disk state."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen011-")
        self.rel = f"{S.SCENARIO_DIR}/login{S.SCENARIO_FILE_SUFFIX}"
        _git_init_with_commit(self.tmpdir, self.rel, _VALID_FILE)
        self.scenario_path = Path(self.tmpdir) / self.rel

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _baseline_still_on_disk(self):
        """Confirm the on-disk file still matches the git baseline."""
        current = S.current_file_hash(self.scenario_path)
        baseline = S.scenario_baseline_hash(self.tmpdir, self.rel)
        self.assertEqual(current, baseline,
            "Precondition: disk must equal baseline at real PreToolUse timing")

    def test_edit_predicted_divergence_denied(self):
        """Edit whose simulated apply diverges from baseline must be denied."""
        self._baseline_still_on_disk()
        exit_code, _, stderr = _run_hook_stdin(sdd_test_guard.main, {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(self.scenario_path),
                "old_string": "successful login",
                "new_string": "obliterated",
            },
            "cwd": self.tmpdir,
            "session_id": "scen011-edit",
        })
        self.assertEqual(exit_code, 2,
            f"Edit that would diverge from baseline must deny; "
            f"got exit={exit_code}, stderr={stderr!r}")
        self.assertTrue(
            any(k in stderr.lower() for k in ("write-once", "scenario", "amend")),
            f"stderr must mention write-once/scenario/amend; got: {stderr!r}")

    def test_write_content_divergence_denied(self):
        """Write whose content hash diverges from baseline must be denied."""
        self._baseline_still_on_disk()
        exit_code, _, stderr = _run_hook_stdin(sdd_test_guard.main, {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(self.scenario_path),
                "content": "totally different replacement bytes\n",
            },
            "cwd": self.tmpdir,
            "session_id": "scen011-write",
        })
        self.assertEqual(exit_code, 2,
            f"Write with divergent content must deny; "
            f"got exit={exit_code}, stderr={stderr!r}")

    def test_multiedit_sequential_divergence_denied(self):
        """MultiEdit with any edit producing divergence must be denied."""
        self._baseline_still_on_disk()
        exit_code, _, stderr = _run_hook_stdin(sdd_test_guard.main, {
            "tool_name": "MultiEdit",
            "tool_input": {
                "file_path": str(self.scenario_path),
                "edits": [
                    {"old_string": "successful login", "new_string": "mutated"},
                    {"old_string": "Evidence", "new_string": "Proof"},
                ],
            },
            "cwd": self.tmpdir,
            "session_id": "scen011-multi",
        })
        self.assertEqual(exit_code, 2,
            f"MultiEdit with divergent edits must deny; "
            f"got exit={exit_code}, stderr={stderr!r}")

    def test_edit_noop_allowed(self):
        """Edit whose simulated apply equals baseline must be ALLOWED.

        Guards against false positives: old_string == new_string produces
        identical bytes, so predicted hash == baseline. No denial.
        """
        self._baseline_still_on_disk()
        exit_code, _, stderr = _run_hook_stdin(sdd_test_guard.main, {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(self.scenario_path),
                "old_string": "successful login",
                "new_string": "successful login",
            },
            "cwd": self.tmpdir,
            "session_id": "scen011-noop",
        })
        self.assertEqual(exit_code, 0,
            f"No-op Edit must be allowed (predicted == baseline); "
            f"got exit={exit_code}, stderr={stderr!r}")

    def test_write_baseline_content_allowed(self):
        """Write whose content exactly equals baseline must be ALLOWED."""
        self._baseline_still_on_disk()
        exit_code, _, stderr = _run_hook_stdin(sdd_test_guard.main, {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(self.scenario_path),
                "content": _VALID_FILE,
            },
            "cwd": self.tmpdir,
            "session_id": "scen011-write-noop",
        })
        self.assertEqual(exit_code, 0,
            f"Write with baseline content must be allowed; "
            f"got exit={exit_code}, stderr={stderr!r}")


if __name__ == "__main__":
    unittest.main()
