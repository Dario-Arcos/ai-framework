#!/usr/bin/env python3
"""Phase 7 bypass coverage for HOOK_VERSION alignment and scenario bypass."""
import importlib.util
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

import _sdd_state
from _sdd_detect import write_state
from _subprocess_harness import HOOKS_DIR, cleanup_all_state, invoke_hook


_SCENARIO_REL = ".claude/scenarios/login.scenarios.md"
_METRICS_REL = Path(".claude") / "metrics.jsonl"
_VALID_SCENARIO = """\
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


def _require_git():
    try:
        subprocess.run(
            ["git", "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise unittest.SkipTest(f"git not available: {exc}")


def _metrics_path(cwd):
    return Path(cwd) / _METRICS_REL


def _read_metrics(cwd):
    path = _metrics_path(cwd)
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _scenarios_bypassed_events(cwd, hook_name):
    return [
        event
        for event in _read_metrics(cwd)
        if event.get("event") == "scenarios_bypassed"
        and event.get("hook") == hook_name
    ]


def _seed_pending_scenario(cwd):
    path = Path(cwd) / _SCENARIO_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_VALID_SCENARIO, encoding="utf-8")
    return path


def _git_init_with_scenario(cwd):
    _require_git()
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    scenario_path = _seed_pending_scenario(cwd)
    for command in (
        ["git", "-C", str(cwd), "init", "-q"],
        ["git", "-C", str(cwd), "config", "user.email", "t@t.com"],
        ["git", "-C", str(cwd), "config", "user.name", "tester"],
        ["git", "-C", str(cwd), "add", _SCENARIO_REL],
        ["git", "-C", str(cwd), "commit", "-q", "-m", "init"],
    ):
        subprocess.run(
            command,
            check=True,
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
        )
    return scenario_path


def _fresh_sdd_state_with_missing_package():
    module_path = HOOKS_DIR / "_sdd_state.py"
    spec = importlib.util.spec_from_file_location("_sdd_state_missing_pkg", module_path)
    module = importlib.util.module_from_spec(spec)
    original_read_text = Path.read_text

    def _fake_read_text(self, *args, **kwargs):
        if self.name == "package.json":
            raise FileNotFoundError("missing package.json")
        return original_read_text(self, *args, **kwargs)

    with patch.object(Path, "read_text", new=_fake_read_text):
        spec.loader.exec_module(module)
    return module


class TestPhase7Bypass(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-bypass-")

    def tearDown(self):
        cleanup_all_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_hook_version_matches_package_json(self):
        package_json = json.loads((HOOKS_DIR.parent / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(_sdd_state.HOOK_VERSION, package_json["version"])

    def test_hook_version_fallback_on_missing_package_json(self):
        fresh_module = _fresh_sdd_state_with_missing_package()
        self.assertEqual(fresh_module.HOOK_VERSION, "2026.04.0")
        self.assertEqual(fresh_module._read_hook_version(), "2026.04.0")

    def test_scenarios_bypass_active_skips_scenario_guard(self):
        scenario_path = _git_init_with_scenario(self.tmpdir)
        updated = _VALID_SCENARIO + "\n## SCEN-002: drift\n**When**: x\n**Then**: y\n"
        scenario_path.write_text(updated, encoding="utf-8")

        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(scenario_path),
                "old_string": _VALID_SCENARIO,
                "new_string": updated,
            },
        })
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:SCENARIO]"), stderr)

        rc, _stdout, stderr, _elapsed_ms = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": self.tmpdir,
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": str(scenario_path),
                    "old_string": _VALID_SCENARIO,
                    "new_string": updated,
                },
            },
            env={"_SDD_DISABLE_SCENARIOS": "1"},
        )
        self.assertEqual(rc, 0)
        self.assertNotIn("[SDD:SCENARIO]", stderr)
        self.assertEqual(len(_scenarios_bypassed_events(self.tmpdir, "sdd-test-guard")), 1)

    def test_scenarios_bypass_skips_bash_scenario_write(self):
        payload = {
            "cwd": self.tmpdir,
            "tool_name": "Bash",
            "tool_input": {
                "command": "cat > .claude/scenarios/foo.scenarios.md <<'EOF'\ntext\nEOF\n",
            },
        }

        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", payload)
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:SCENARIO]"), stderr)

        rc, _stdout, stderr, _elapsed_ms = invoke_hook(
            "sdd-test-guard.py",
            payload,
            env={"_SDD_DISABLE_SCENARIOS": "1"},
        )
        self.assertEqual(rc, 0)
        self.assertNotIn("[SDD:SCENARIO]", stderr)

    def test_scenarios_bypass_skips_taskupdate_guard(self):
        _seed_pending_scenario(self.tmpdir)
        payload = {
            "cwd": self.tmpdir,
            "session_id": "phase7-taskupdate",
            "tool_name": "TaskUpdate",
            "tool_input": {"status": "completed", "taskId": "T-1"},
        }

        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", payload)
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:POLICY]"), stderr)

        rc, _stdout, stderr, _elapsed_ms = invoke_hook(
            "sdd-test-guard.py",
            payload,
            env={"_SDD_DISABLE_SCENARIOS": "1"},
        )
        self.assertEqual(rc, 0)
        self.assertNotIn("[SDD:POLICY]", stderr)

    def test_scenarios_bypass_skips_git_commit_guard(self):
        _seed_pending_scenario(self.tmpdir)
        payload = {
            "cwd": self.tmpdir,
            "session_id": "phase7-git-commit",
            "tool_name": "Bash",
            "tool_input": {"command": 'git commit -m "x"'},
        }

        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", payload)
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:POLICY]"), stderr)

        rc, _stdout, stderr, _elapsed_ms = invoke_hook(
            "sdd-test-guard.py",
            payload,
            env={"_SDD_DISABLE_SCENARIOS": "1"},
        )
        self.assertEqual(rc, 0)
        self.assertNotIn("[SDD:POLICY]", stderr)

    def test_scenarios_bypass_does_not_skip_assertion_weakening_guard(self):
        write_state(self.tmpdir, passing=False, summary="1 failed")
        payload = {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(Path(self.tmpdir) / "test_reward.py"),
                "old_string": "assert x == 1\nassert y == 2\n",
                "new_string": "",
            },
        }

        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", payload)
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:GATE]"), stderr)

        rc, _stdout, stderr, _elapsed_ms = invoke_hook(
            "sdd-test-guard.py",
            payload,
            env={"_SDD_DISABLE_SCENARIOS": "1"},
        )
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:GATE]"), stderr)

    def test_scenarios_bypass_skips_task_completed_gate(self):
        _seed_pending_scenario(self.tmpdir)
        payload = {
            "cwd": self.tmpdir,
            "task_subject": "Ship feature",
            "teammate_name": "impl-ship-feature",
            "session_id": "phase7-task-completed",
        }

        rc, _stdout, stderr, _elapsed_ms = invoke_hook(
            "task-completed.py",
            payload,
            env={"_SDD_DISABLE_SCENARIOS": "1"},
        )
        self.assertEqual(rc, 0, stderr)
        self.assertNotIn("[SDD:SCENARIO]", stderr)
        self.assertEqual(len(_scenarios_bypassed_events(self.tmpdir, "task-completed")), 1)

    def test_bypass_env_var_non_1_value_is_off(self):
        scenario_path = _git_init_with_scenario(self.tmpdir)
        updated = _VALID_SCENARIO + "\n## SCEN-002: drift\n**When**: x\n**Then**: y\n"
        scenario_path.write_text(updated, encoding="utf-8")
        payload = {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(scenario_path),
                "old_string": _VALID_SCENARIO,
                "new_string": updated,
            },
        }

        for value in ("true", "0"):
            with self.subTest(value=value):
                rc, _stdout, stderr, _elapsed_ms = invoke_hook(
                    "sdd-test-guard.py",
                    payload,
                    env={"_SDD_DISABLE_SCENARIOS": value},
                )
                self.assertEqual(rc, 2)
                self.assertTrue(stderr.startswith("[SDD:SCENARIO]"), stderr)

        self.assertEqual(_scenarios_bypassed_events(self.tmpdir, "sdd-test-guard"), [])

    def test_bypass_telemetry_emitted_exactly_once_per_invocation(self):
        _seed_pending_scenario(self.tmpdir)
        payload = {
            "cwd": self.tmpdir,
            "session_id": "phase7-telemetry",
            "tool_name": "TaskUpdate",
            "tool_input": {"status": "completed", "taskId": "T-telemetry"},
        }

        rc, _stdout, stderr, _elapsed_ms = invoke_hook(
            "sdd-test-guard.py",
            payload,
            env={"_SDD_DISABLE_SCENARIOS": "1"},
        )
        self.assertEqual(rc, 0, stderr)
        events = _scenarios_bypassed_events(self.tmpdir, "sdd-test-guard")
        self.assertEqual(len(events), 1, events)


if __name__ == "__main__":
    unittest.main()
