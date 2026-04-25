#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _subprocess_harness import HOOKS_DIR, cleanup_all_state, invoke_hook
from _sdd_detect import write_state
from _sdd_state import append_telemetry, rotate_telemetry


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

_SCENARIO_REL = ".ralph/specs/hook-subprocess/scenarios/login.scenarios.md"
_METRICS_REL = Path(".claude") / "metrics.jsonl"


def _require_git():
    try:
        subprocess.run(
            ["git", "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except OSError:
        pytest.skip("git not available")


def _skip_windows_append_contract():
    if os.name == "nt":
        pytest.skip("POSIX append/rename contract only")


def _metrics_path(cwd):
    return Path(cwd) / _METRICS_REL


def _metrics_files(cwd):
    base = _metrics_path(cwd)
    paths = [base]
    for idx in range(1, 4):
        paths.append(Path(str(base) + f".{idx}"))
    return [path for path in paths if path.exists()]


def _read_jsonl(path):
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _all_events(cwd):
    events = []
    for path in _metrics_files(cwd):
        events.extend(_read_jsonl(path))
    return events


def _assert_guard_event(testcase, cwd, category, tool_name):
    events = [
        event for event in _all_events(cwd)
        if event.get("event") == "guard_triggered"
    ]
    testcase.assertTrue(events, "expected at least one guard_triggered event")
    testcase.assertTrue(
        any(
            event.get("category") == category and
            event.get("tool_name") == tool_name
            for event in events
        ),
        f"missing guard_triggered event for {category}/{tool_name}: {events!r}",
    )


def _git_init_with_scenario(cwd):
    _require_git()
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    scenario_path = Path(cwd) / _SCENARIO_REL
    scenario_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "-C", str(cwd), "init", "-q"],
        check=True,
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
    )
    subprocess.run(
        ["git", "-C", str(cwd), "config", "user.email", "t@t.com"],
        check=True,
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
    )
    subprocess.run(
        ["git", "-C", str(cwd), "config", "user.name", "tester"],
        check=True,
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
    )
    scenario_path.write_text(_VALID_SCENARIO, encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(cwd), "add", _SCENARIO_REL],
        check=True,
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
    )
    subprocess.run(
        ["git", "-C", str(cwd), "commit", "-q", "-m", "init"],
        check=True,
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
    )
    return scenario_path


def _seed_untracked_scenario(cwd):
    scenario_path = Path(cwd) / _SCENARIO_REL
    scenario_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_path.write_text(_VALID_SCENARIO, encoding="utf-8")
    return scenario_path


def _seed_metrics_file(cwd, target_bytes, payload_size=180):
    metrics_path = _metrics_path(cwd)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps({
        "event": "seed",
        "idx": 0,
        "payload": "S" * payload_size,
    }) + "\n"
    repeats = max(1, target_bytes // len(line.encode("utf-8")))
    metrics_path.write_text(line * repeats, encoding="utf-8")
    size = metrics_path.stat().st_size
    if size > target_bytes:
        metrics_path.write_text(
            metrics_path.read_text(encoding="utf-8")[:-len(line)],
            encoding="utf-8",
        )
    return metrics_path


def _spawn_appenders(cwd, process_count, event_count, payload, event_name, start_idx=0):
    procs = []
    for idx in range(process_count):
        marker = start_idx + idx
        snippet = (
            "import sys\n"
            f"sys.path.insert(0, {str(HOOKS_DIR)!r})\n"
            "import _sdd_state as state\n"
            f"cwd = {str(cwd)!r}\n"
            f"idx = {marker}\n"
            f"payload = {payload!r}\n"
            f"event_name = {event_name!r}\n"
            f"event_count = {event_count}\n"
            "for _ in range(event_count):\n"
            "    state.append_telemetry(cwd, {'event': event_name, 'idx': idx, 'payload': payload})\n"
        )
        procs.append(subprocess.Popen(
            [sys.executable, "-c", snippet],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ))
    return procs


def _wait_for_procs(testcase, procs, timeout=10):
    deadline = time.time() + timeout
    results = []
    for proc in procs:
        remaining = deadline - time.time()
        testcase.assertGreater(remaining, 0, "timed out waiting for subprocesses")
        try:
            stdout, stderr = proc.communicate(timeout=remaining)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            testcase.fail(f"subprocess timed out: stdout={stdout!r} stderr={stderr!r}")
        results.append((proc.returncode, stdout, stderr))
    return results


class TestPhase7CategoryPrefixes(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="phase7-a-")
        self.tmpdir = self._tmp.name

    def tearDown(self):
        cleanup_all_state(self.tmpdir)
        self._tmp.cleanup()

    def test_scenario_prefix_for_tracked_scenario_edit_without_amend(self):
        scenario_path = _git_init_with_scenario(self.tmpdir)
        scenario_path.write_text(
            _VALID_SCENARIO + "\n## SCEN-002: drift\n**When**: x\n**Then**: y\n",
            encoding="utf-8",
        )
        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(scenario_path),
                "old_string": _VALID_SCENARIO,
                "new_string": scenario_path.read_text(encoding="utf-8"),
            },
        })
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:SCENARIO]"), stderr)
        _assert_guard_event(self, self.tmpdir, "SCENARIO", "Edit")

    def test_scenario_prefix_for_bash_cat_redirect_into_scenarios(self):
        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", {
            "cwd": self.tmpdir,
            "tool_name": "Bash",
            "tool_input": {
                "command": "cat > .ralph/specs/hook-subprocess/scenarios/foo.scenarios.md <<'EOF'\ntext\nEOF\n",
            },
        })
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:SCENARIO]"), stderr)
        _assert_guard_event(self, self.tmpdir, "SCENARIO", "Bash")

    def test_policy_prefix_for_taskupdate_completed_without_verification(self):
        _seed_untracked_scenario(self.tmpdir)
        raw_sid = "phase7-taskupdate"
        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", {
            "cwd": self.tmpdir,
            "session_id": raw_sid,
            "tool_name": "TaskUpdate",
            "tool_input": {"status": "completed", "taskId": "T-1"},
        })
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:POLICY]"), stderr)
        _assert_guard_event(self, self.tmpdir, "POLICY", "TaskUpdate")

    def test_policy_prefix_for_git_commit_without_verification(self):
        _seed_untracked_scenario(self.tmpdir)
        raw_sid = "phase7-git-commit"
        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", {
            "cwd": self.tmpdir,
            "session_id": raw_sid,
            "tool_name": "Bash",
            "tool_input": {"command": 'git commit -m "x"'},
        })
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:POLICY]"), stderr)
        _assert_guard_event(self, self.tmpdir, "POLICY", "Bash")

    def test_gate_prefix_for_assertion_weakening_when_tests_failing(self):
        write_state(self.tmpdir, passing=False, summary="1 failed")
        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(Path(self.tmpdir) / "test_reward.py"),
                "old_string": "assert x == 1\nassert y == 2\n",
                "new_string": "",
            },
        })
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:GATE]"), stderr)
        _assert_guard_event(self, self.tmpdir, "GATE", "Edit")

    def test_gate_prefix_for_tautological_new_test(self):
        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", {
            "cwd": self.tmpdir,
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(Path(self.tmpdir) / "test_foo.py"),
                "content": "def test_trivial():\n    assert True\n",
            },
        })
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:GATE]"), stderr)
        _assert_guard_event(self, self.tmpdir, "GATE", "Write")

    def test_happy_path_source_edit_passes_without_sdd_prefix(self):
        write_state(self.tmpdir, passing=True, summary="3 passed")
        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(Path(self.tmpdir) / "src" / "app.py"),
                "old_string": "return 1\n",
                "new_string": "return 2\n",
            },
        })
        self.assertEqual(rc, 0)
        self.assertNotIn("[SDD:", stderr)


class TestPhase7ConcurrentRotation(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="phase7-b-")
        self.tmpdir = self._tmp.name

    def tearDown(self):
        cleanup_all_state(self.tmpdir)
        self._tmp.cleanup()

    def test_concurrent_append_triggers_rotation_once(self):
        _skip_windows_append_contract()
        _seed_metrics_file(self.tmpdir, 10276000)
        procs = _spawn_appenders(
            self.tmpdir,
            process_count=8,
            event_count=250,
            payload="A" * 200,
            event_name="test",
        )
        results = _wait_for_procs(self, procs, timeout=10)
        for rc, _stdout, stderr in results:
            self.assertEqual(rc, 0, stderr)

        base = _metrics_path(self.tmpdir)
        self.assertFalse(Path(str(base) + ".4").exists())
        self.assertTrue(Path(str(base) + ".1").exists())
        allowed = {
            "metrics.jsonl",
            "metrics.jsonl.1",
            "metrics.jsonl.2",
            "metrics.jsonl.3",
        }
        existing = {path.name for path in base.parent.iterdir() if path.name.startswith("metrics.jsonl")}
        self.assertTrue(existing.issubset(allowed), existing)

        total = 0
        for path in _metrics_files(self.tmpdir):
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    json.loads(line)
                    total += 1
        self.assertGreaterEqual(total, 1000)

    def test_rotation_boundary_no_crash(self):
        _skip_windows_append_contract()
        _seed_metrics_file(self.tmpdir, 10370000)
        deadline = time.time() + 10
        count = 0
        while not Path(str(_metrics_path(self.tmpdir)) + ".2").exists():
            append_telemetry(self.tmpdir, {
                "event": "boundary",
                "idx": count,
                "payload": "B" * 900,
            })
            count += 1
            if time.time() > deadline:
                self.fail("timed out waiting for second rotation")

        self.assertFalse(Path(str(_metrics_path(self.tmpdir)) + ".4").exists())
        for path in _metrics_files(self.tmpdir):
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        json.loads(line)

    def test_rotation_preserves_chronological_suffix_order(self):
        append_telemetry(self.tmpdir, {"event": "old", "idx": 0, "payload": "x"})
        append_telemetry(self.tmpdir, {"event": "old", "idx": 1, "payload": "x"})
        append_telemetry(self.tmpdir, {"event": "old", "idx": 2, "payload": "x"})
        rotate_telemetry(self.tmpdir)
        append_telemetry(self.tmpdir, {"event": "new", "idx": 3, "payload": "y"})
        append_telemetry(self.tmpdir, {"event": "new", "idx": 4, "payload": "y"})
        append_telemetry(self.tmpdir, {"event": "new", "idx": 5, "payload": "y"})
        rotate_telemetry(self.tmpdir)

        older = _read_jsonl(Path(str(_metrics_path(self.tmpdir)) + ".2"))
        newer = _read_jsonl(Path(str(_metrics_path(self.tmpdir)) + ".1"))
        self.assertEqual([event["event"] for event in older], ["old", "old", "old"])
        self.assertEqual([event["idx"] for event in older], [0, 1, 2])
        self.assertEqual([event["event"] for event in newer], ["new", "new", "new"])
        self.assertEqual([event["idx"] for event in newer], [3, 4, 5])


class TestPhase7ConcurrentAppendIntegrity(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="phase7-c-")
        self.tmpdir = self._tmp.name

    def tearDown(self):
        cleanup_all_state(self.tmpdir)
        self._tmp.cleanup()

    def test_16_subprocess_parallel_append_no_lost_lines(self):
        _skip_windows_append_contract()
        procs = _spawn_appenders(
            self.tmpdir,
            process_count=16,
            event_count=1,
            payload="M",
            event_name="marker",
        )
        results = _wait_for_procs(self, procs, timeout=10)
        for rc, _stdout, stderr in results:
            self.assertEqual(rc, 0, stderr)

        lines = _metrics_path(self.tmpdir).read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 16)
        events = [json.loads(line) for line in lines]
        self.assertEqual({event["idx"] for event in events}, set(range(16)))

    def test_interleaved_append_no_torn_line(self):
        _skip_windows_append_contract()
        procs = _spawn_appenders(
            self.tmpdir,
            process_count=4,
            event_count=100,
            payload="I" * 200,
            event_name="interleaved",
        )
        results = _wait_for_procs(self, procs, timeout=10)
        for rc, _stdout, stderr in results:
            self.assertEqual(rc, 0, stderr)

        count = 0
        with _metrics_path(self.tmpdir).open("r", encoding="utf-8") as handle:
            for line in handle.readlines():
                if not line:
                    continue
                self.assertTrue(line.startswith("{"), line[:80])
                self.assertTrue(line.endswith("}\n"), line[-80:])
                json.loads(line)
                count += 1
        self.assertGreaterEqual(count, 398)

    def test_concurrent_append_with_rotation_no_torn_line(self):
        _skip_windows_append_contract()
        _seed_metrics_file(self.tmpdir, 10370000)
        procs = _spawn_appenders(
            self.tmpdir,
            process_count=4,
            event_count=100,
            payload="R" * 200,
            event_name="rotating",
        )
        results = _wait_for_procs(self, procs, timeout=10)
        for rc, _stdout, stderr in results:
            self.assertEqual(rc, 0, stderr)

        self.assertFalse(Path(str(_metrics_path(self.tmpdir)) + ".4").exists())
        for path in _metrics_files(self.tmpdir):
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        json.loads(line)


class TestPhase7ExitCodePropagation(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="phase7-d-")
        self.tmpdir = self._tmp.name

    def tearDown(self):
        cleanup_all_state(self.tmpdir)
        self._tmp.cleanup()

    def test_exit_0_round_trip(self):
        write_state(self.tmpdir, passing=True, summary="1 passed")
        rc, _stdout, _stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(Path(self.tmpdir) / "src" / "ok.py"),
                "old_string": "return 1\n",
                "new_string": "return 2\n",
            },
        })
        self.assertEqual(rc, 0)

    def test_exit_2_round_trip_scenario(self):
        scenario_path = _git_init_with_scenario(self.tmpdir)
        scenario_path.write_text(
            _VALID_SCENARIO + "\n## SCEN-002: changed\n**When**: x\n**Then**: y\n",
            encoding="utf-8",
        )
        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(scenario_path),
                "old_string": _VALID_SCENARIO,
                "new_string": scenario_path.read_text(encoding="utf-8"),
            },
        })
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:SCENARIO]"), stderr)

    def test_stderr_only_on_failure(self):
        write_state(self.tmpdir, passing=True, summary="1 passed")
        rc, _stdout, stderr, _elapsed_ms = invoke_hook("sdd-test-guard.py", {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(Path(self.tmpdir) / "src" / "benign.py"),
                "old_string": "x = 1\n",
                "new_string": "x = 2\n",
            },
        })
        self.assertEqual(rc, 0)
        self.assertTrue(not stderr or "[SDD:" not in stderr, stderr)
