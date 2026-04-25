#!/usr/bin/env python3
"""SCEN-005 — Opt-in canary: projects without any spec-folder scenarios
behave identically to the pre-Phase-3 baseline.

Phase 10 layout: scenarios live under `.ralph/specs/{goal}/scenarios/` or
`docs/specs/{name}/scenarios/`. Absent any scenarios under those discovery
roots, no new gate should fire, no new guard should trip, no new failure
path should surface — the scenarios machinery is opt-in.

Unlike other SCEN tests, this one is intentionally GREEN. It locks in the
backward-compat contract so any future regression in the scenarios
infrastructure fails loudly here rather than leaking into unsuspecting
projects.
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
import _sdd_scenarios as scenarios
import _sdd_state as state

sdd_test_guard = importlib.import_module("sdd-test-guard")


def _invoke_guard(cwd, payload):
    """Invoke sdd-test-guard.main() with the given stdin payload. Returns
    (exit_code, stdout, stderr). Never raises; SystemExit is caught.
    """
    stdin = io.StringIO(json.dumps(payload))
    stdout = io.StringIO()
    stderr = io.StringIO()
    env = {"CLAUDE_PROJECT_DIR": str(cwd)}
    with patch("sys.stdin", stdin), \
         patch("sys.stdout", stdout), \
         patch("sys.stderr", stderr), \
         patch.dict(os.environ, env):
        try:
            sdd_test_guard.main()
            code = 0
        except SystemExit as exc:
            code = exc.code if exc.code is not None else 0
    return code, stdout.getvalue(), stderr.getvalue()


class TestScen005BackwardCompat(unittest.TestCase):
    """No spec-folder scenarios → all scenario predicates return safe-empty +
    guards do not fire.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="scen005-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_scenario_files_empty_without_spec_folders(self):
        """scenario_files on a fresh project yields [] without side effects."""
        self.assertEqual(scenarios.scenario_files(self.tmpdir), [])
        # Probe must not create discovery roots as a side effect
        self.assertFalse(
            (Path(self.tmpdir) / ".ralph" / "specs").exists(),
            "Discovery must not implicitly create discovery roots",
        )

    def test_has_pending_scenarios_false_without_spec_folders(self):
        """No spec-folder scenarios → never pending, regardless of sid."""
        self.assertFalse(scenarios.has_pending_scenarios(self.tmpdir))
        self.assertFalse(scenarios.has_pending_scenarios(self.tmpdir, sid="x"))

    def test_check_amend_marker_false_without_spec_folders(self):
        """Amend check returns False (not an error) when no scenarios exist."""
        self.assertFalse(
            scenarios.check_amend_marker(
                self.tmpdir,
                ".ralph/specs/scen005/scenarios/x.scenarios.md",
            )
        )

    def test_default_discovery_roots_resolve_to_spec_folders(self):
        """The opt-in contract is anchored on the spec-folder roots."""
        from _sdd_config import get_scenario_discovery_roots
        self.assertEqual(
            get_scenario_discovery_roots(self.tmpdir),
            (".ralph/specs", "docs/specs"),
        )

    def test_guard_allows_edit_on_non_scenario_file_without_dir(self):
        """PreToolUse Edit on an ordinary file in a project with no scenarios
        dir must not trip any scenario-specific guard. This is the exact
        shape the hook sees for 99% of projects today — breaking it would
        torpedo backward compat.
        """
        src = Path(self.tmpdir) / "app.py"
        src.write_text("x = 1\n", encoding="utf-8")
        code, _stdout, stderr = _invoke_guard(self.tmpdir, {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(src)},
            "cwd": self.tmpdir,
            "session_id": "sess-bc",
        })
        self.assertEqual(code, 0,
            f"Edit on ordinary file must not fail; stderr={stderr!r}")

    def test_guard_allows_bash_write_when_no_scenarios_dir(self):
        """A Bash command that WOULD have been blocked if scenarios existed
        must pass when no scenarios dir is present. Verifies the guard
        scopes its regex match to projects that opt in.
        """
        cmd = "sed -i 's/foo/bar/' some_other_file.txt"
        code, _stdout, _stderr = _invoke_guard(self.tmpdir, {
            "tool_name": "Bash",
            "tool_input": {"command": cmd},
            "cwd": self.tmpdir,
            "session_id": "sess-bc",
        })
        self.assertEqual(code, 0,
            f"Bash guard must not fire without scenarios dir (cmd={cmd!r})")

    def test_guard_allows_taskupdate_completed_when_no_scenarios_dir(self):
        """TaskUpdate(status=completed) without scenarios dir → no gate."""
        code, _stdout, _stderr = _invoke_guard(self.tmpdir, {
            "tool_name": "TaskUpdate",
            "tool_input": {"status": "completed", "taskId": "T1"},
            "cwd": self.tmpdir,
            "session_id": "sess-bc",
        })
        self.assertEqual(code, 0,
            "TaskUpdate guard must not fire in projects without scenarios")

    def test_state_files_still_isolated_by_project_hash(self):
        """The session/state infrastructure used by scenarios must coexist
        with scenarios-less projects. Writing state must not leak into or
        depend on scenario-specific artifacts.
        """
        sid = state.extract_session_id({"session_id": "bc-sess"})
        state.write_state(self.tmpdir, passing=True, summary="ok")
        read = state.read_state(self.tmpdir)
        self.assertIsNotNone(read)
        self.assertTrue(read["passing"])
        # No discovery roots must have been created as a side effect
        self.assertFalse(
            (Path(self.tmpdir) / ".ralph" / "specs").exists()
        )


if __name__ == "__main__":
    unittest.main()
