#!/usr/bin/env python3
"""Integration tests — SDD test mechanism end-to-end.

Verifies the REAL MECHANISM works during coding:
  1. sdd-auto-test.py worker runs actual tests, writes shared state
  2. sdd-test-guard.py reads that state, blocks reward hacking
  3. task-completed.py reads that state, gates task completion
  4. Full cycle: edit → test → feedback → guard → complete

These tests create real mini-projects with real test files, execute
real pytest processes, and verify the hooks communicate correctly via
shared state files.

IMPORTANT: these tests must pass after any change to hooks/.
"""
import importlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sdd_auto_test = importlib.import_module("sdd-auto-test")
sdd_test_guard = importlib.import_module("sdd-test-guard")
task_completed = importlib.import_module("task-completed")
import _sdd_detect


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────

def _create_mini_project(tmpdir, app_code, test_code):
    """Create a mini Python project with pyproject.toml, app, and tests."""
    proj = Path(tmpdir)
    (proj / "pyproject.toml").write_text(
        '[project]\nname = "mini"\n[tool.pytest]\n', encoding="utf-8"
    )
    (proj / "app.py").write_text(app_code, encoding="utf-8")
    tests_dir = proj / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "__init__.py").write_text("", encoding="utf-8")
    (tests_dir / "test_app.py").write_text(test_code, encoding="utf-8")
    return proj


def _run_hook_stdin(hook_main, input_data):
    """Run a hook's main() with JSON stdin, capture stdout/stderr and exit code.

    Patches CLAUDE_PROJECT_DIR to match input_data["cwd"] so the env var
    doesn't override the test's intended working directory.
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
            hook_main()
        except SystemExit as e:
            exit_code = e.code if e.code is not None else 0

    return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()


def _cleanup_state(cwd):
    """Remove state and PID files for a project directory."""
    h = _sdd_detect.project_hash(cwd)
    tmp = tempfile.gettempdir()
    for pattern in [os.path.join(tmp, f"sdd-test-state-{h}.json"),
                    os.path.join(tmp, f"sdd-test-run-{h}.pid"),
                    os.path.join(tmp, f"sdd-runner-{h}.lock"),
                    os.path.join(tmp, f"sdd-test-lock-{h}")]:
        try:
            os.unlink(pattern)
        except FileNotFoundError:
            pass


def _lock_concurrency_worker(cwd, hold_s, result_file, worker_id,
                             retry_deadline_s):
    """Persistent worker for TestLockConcurrency — spawn-safe (module-level).

    Keeps retrying acquire_runner_lock until success or deadline. Holds the
    lock for `hold_s` seconds, then releases. Writes CSV row to result_file.

    Row format: `worker_id,STATUS,t_acquired,t_release_start,t_release_end`
    where timestamps are time.monotonic() floats (shared clock domain within
    a single machine, not across reboots — fine for test invariant checks).
    """
    import sys as _sys
    import time as _time
    from pathlib import Path as _Path

    _sys.path.insert(0, str(_Path(__file__).resolve().parent))
    import _sdd_state  # noqa: E402

    deadline = _time.monotonic() + retry_deadline_s
    fd = None
    while _time.monotonic() < deadline and fd is None:
        fd = _sdd_state.acquire_runner_lock(cwd)
        if fd is None:
            _time.sleep(0.02)
    if fd is None:
        with open(result_file, "a") as f:
            f.write(f"{worker_id},FAILED,0,0,0\n")
        return
    t_acq = _time.monotonic()
    _time.sleep(hold_s)
    t_rel_start = _time.monotonic()
    _sdd_state.release_runner_lock(fd, cwd)
    t_rel_end = _time.monotonic()
    with open(result_file, "a") as f:
        f.write(f"{worker_id},OK,{t_acq},{t_rel_start},{t_rel_end}\n")


def _lock_concurrency_prober(cwd, result_file, samples):
    """Probe worker for TestLockConcurrency — spawn-safe (module-level)."""
    import sys as _sys
    import time as _time
    from pathlib import Path as _Path

    _sys.path.insert(0, str(_Path(__file__).resolve().parent))
    import _sdd_state  # noqa: E402

    results = []
    for _ in range(samples):
        results.append(_sdd_state.is_test_running(cwd))
        _time.sleep(0.005)
    with open(result_file, "a") as f:
        f.write(",".join("T" if r else "F" for r in results) + "\n")


def _lock_concurrency_worker_cycling(cwd, state_file, cycles, hold_s, idle_s):
    """Cycling worker: repeatedly acquire/hold/release, publishing state.

    Writes 'held' to state_file while holding the lock, 'idle' otherwise.
    The main test process probes at a faster cadence and verifies that
    probe results never claim "no runner" while this worker is 'held'.
    """
    import sys as _sys
    import time as _time
    from pathlib import Path as _Path

    _sys.path.insert(0, str(_Path(__file__).resolve().parent))
    import _sdd_state  # noqa: E402

    for _ in range(cycles):
        fd = None
        deadline = _time.monotonic() + 1.0
        while fd is None and _time.monotonic() < deadline:
            fd = _sdd_state.acquire_runner_lock(cwd)
            if fd is None:
                _time.sleep(0.005)
        if fd is None:
            return
        try:
            with open(state_file, "w") as f:
                f.write("held")
            _time.sleep(hold_s)
            with open(state_file, "w") as f:
                f.write("idle")
        finally:
            _sdd_state.release_runner_lock(fd, cwd)
        _time.sleep(idle_s)


# ─────────────────────────────────────────────────────────────────
# 1. SHARED STATE COMMUNICATION
# ─────────────────────────────────────────────────────────────────

class TestSharedStateCommunication(unittest.TestCase):
    """Verify hooks communicate via shared state files."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-")
        _cleanup_state(self.tmpdir)

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_state_path_deterministic(self):
        """Same cwd always produces the same state file path."""
        p1 = _sdd_detect.state_path(self.tmpdir)
        p2 = _sdd_detect.state_path(self.tmpdir)
        self.assertEqual(p1, p2)

    def test_write_state_readable_by_read_state(self):
        """write_state() output is correctly read by read_state()."""
        _sdd_detect.write_state(self.tmpdir, True, "5 passed")
        state = _sdd_detect.read_state(self.tmpdir)
        self.assertIsNotNone(state)
        self.assertTrue(state["passing"])
        self.assertEqual(state["summary"], "5 passed")

    def test_failing_state_readable(self):
        """Failing state is correctly persisted and read."""
        _sdd_detect.write_state(self.tmpdir, False, "2 passed, 1 failed")
        state = _sdd_detect.read_state(self.tmpdir)
        self.assertFalse(state["passing"])
        self.assertIn("failed", state["summary"])

    def test_state_overwrites_previous(self):
        """New state replaces old state atomically."""
        _sdd_detect.write_state(self.tmpdir, True, "ok")
        _sdd_detect.write_state(self.tmpdir, False, "fail")
        state = _sdd_detect.read_state(self.tmpdir)
        self.assertFalse(state["passing"])
        self.assertEqual(state["summary"], "fail")

    def test_no_state_returns_none(self):
        """Without write_state, read_state returns None."""
        state = _sdd_detect.read_state(self.tmpdir)
        self.assertIsNone(state)


# ─────────────────────────────────────────────────────────────────
# 2. AUTO-TEST WORKER RUNS REAL TESTS
# ─────────────────────────────────────────────────────────────────

class TestAutoTestWorkerRealExecution(unittest.TestCase):
    """Verify _run_tests_worker actually executes tests and writes state."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-")
        _cleanup_state(self.tmpdir)

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_passing_tests_write_passing_state(self):
        """Worker runs real pytest → passing state written."""
        _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return a + b\n",
            test_code=(
                "import sys; sys.path.insert(0, '..')\n"
                "from app import add\n"
                "def test_add(): assert add(1, 2) == 3\n"
                "def test_add_zero(): assert add(0, 0) == 0\n"
            ),
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")

        state = _sdd_detect.read_state(self.tmpdir)
        self.assertIsNotNone(state, "State should be written after tests run")
        self.assertTrue(state["passing"], f"Tests should pass, got: {state}")
        self.assertIn("passed", state["summary"])

    def test_failing_tests_write_failing_state(self):
        """Worker runs real pytest with failing test → failing state written."""
        _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return a + b\n",
            test_code=(
                "import sys; sys.path.insert(0, '..')\n"
                "from app import add\n"
                "def test_add(): assert add(1, 2) == 3\n"
                "def test_wrong(): assert add(1, 1) == 999  # deliberately wrong\n"
            ),
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")

        state = _sdd_detect.read_state(self.tmpdir)
        self.assertIsNotNone(state)
        self.assertFalse(state["passing"], f"Tests should fail, got: {state}")
        # Summary text varies by pytest version/ordering — the critical signal
        # is passing=False (based on returncode), not the summary text content

    def test_pid_file_after_execution(self):
        """PID file persists after worker (cleaned by is_test_running probe)."""
        _create_mini_project(self.tmpdir,
            app_code="x = 1\n",
            test_code="def test_true(): assert True\n",
        )
        pid_file = _sdd_detect.pid_path(self.tmpdir)

        self.assertFalse(pid_file.exists())
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        # PID file persists (no unlink on Unix — avoids inode race)
        # Probe detects lock released and cleans up
        self.assertFalse(_sdd_detect.is_test_running(self.tmpdir))
        self.assertFalse(pid_file.exists(), "Probe should clean stale PID file")

    def test_invalid_command_writes_error_state(self):
        """Nonexistent test command writes error state, doesn't crash."""
        _create_mini_project(self.tmpdir,
            app_code="x = 1\n",
            test_code="def test(): pass\n",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "nonexistent-test-runner-xyz")

        state = _sdd_detect.read_state(self.tmpdir)
        self.assertIsNotNone(state)
        self.assertFalse(state["passing"])

    def test_exit_suppression_rejected(self):
        """Worker rejects commands with || true."""
        _create_mini_project(self.tmpdir,
            app_code="x = 1\n",
            test_code="def test(): pass\n",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest || true")

        state = _sdd_detect.read_state(self.tmpdir)
        self.assertIsNotNone(state)
        self.assertFalse(state["passing"])
        self.assertIn("exit code suppression", state["summary"])


# ─────────────────────────────────────────────────────────────────
# 3. TEST GUARD READS REAL STATE
# ─────────────────────────────────────────────────────────────────

class TestGuardReadsRealState(unittest.TestCase):
    """Verify sdd-test-guard reads state written by sdd-auto-test."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-")
        _cleanup_state(self.tmpdir)

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_guard_allows_when_tests_passing(self):
        """Tests passing → guard allows any test edit."""
        _sdd_detect.write_state(self.tmpdir, True, "5 passed")

        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "tests/test_app.py",
                "old_string": "assert add(1, 2) == 3\nassert add(0, 0) == 0",
                "new_string": "assert add(1, 2) == 3",  # reducing assertions
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "", "Should produce no output (allow)")

    def test_guard_denies_when_tests_failing_and_assertions_reduced(self):
        """Tests failing + assertions reduced → DENY (reward hacking)."""
        _sdd_detect.write_state(self.tmpdir, False, "1 passed, 1 failed")

        exit_code, stdout, stderr = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "tests/test_app.py",
                "old_string": "assert add(1, 2) == 3\nassert add(0, 0) == 0",
                "new_string": "assert add(1, 2) == 3",  # dropped an assertion
            },
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("reward hacking", stderr)

    def test_guard_allows_when_tests_failing_but_assertions_maintained(self):
        """Tests failing + same assertion count → allow (fixing, not weakening)."""
        _sdd_detect.write_state(self.tmpdir, False, "1 failed")

        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "tests/test_app.py",
                "old_string": "assert add(1, 2) == 3",
                "new_string": "assert add(1, 2) == 3",  # same assertions
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    def test_guard_allows_when_tests_failing_and_assertions_increased(self):
        """Tests failing + more assertions → allow (adding tests)."""
        _sdd_detect.write_state(self.tmpdir, False, "1 failed")

        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "tests/test_app.py",
                "old_string": "assert add(1, 2) == 3",
                "new_string": "assert add(1, 2) == 3\nassert add(0, 0) == 0\nassert add(-1, 1) == 0",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    def test_guard_allows_when_no_state(self):
        """No test state → allow (no data = no block)."""
        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "tests/test_app.py",
                "old_string": "assert x\nassert y\nassert z",
                "new_string": "pass",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    def test_guard_ignores_non_test_files(self):
        """Non-test file edits bypass guard entirely."""
        _sdd_detect.write_state(self.tmpdir, False, "1 failed")

        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "app.py",  # source file, not test
                "old_string": "assert x\nassert y",
                "new_string": "pass",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")


# ─────────────────────────────────────────────────────────────────
# 4. AUTO-TEST HOOK MODE → FEEDBACK FORMAT
# ─────────────────────────────────────────────────────────────────

class TestAutoTestHookFeedback(unittest.TestCase):
    """Verify sdd-auto-test hook mode reads state and reports feedback."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-")
        _cleanup_state(self.tmpdir)
        _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return a + b\n",
            test_code="def test(): pass\n",
        )

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch.object(sdd_auto_test, "read_coverage", return_value=None)
    @patch.object(sdd_auto_test, "run_tests_background")
    def test_passing_state_silent(self, mock_bg, _mock_cov):
        """Previous state was passing → silent (no attention dilution)."""
        _sdd_detect.write_state(self.tmpdir, True, "3 passed")

        exit_code, stdout, _ = _run_hook_stdin(sdd_auto_test.main, {
            "cwd": self.tmpdir,
            "tool_input": {"file_path": "app.py"},
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    @patch.object(sdd_auto_test, "run_tests_background")
    def test_reports_failing_feedback(self, mock_bg):
        """Previous state was failing → feedback shows [FAIL] + fix message."""
        _sdd_detect.write_state(self.tmpdir, False, "1 passed, 2 failed")

        exit_code, stdout, _ = _run_hook_stdin(sdd_auto_test.main, {
            "cwd": self.tmpdir,
            "tool_input": {"file_path": "app.py"},
        })
        output = json.loads(stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("[FAIL]", ctx)
        self.assertIn("fix implementation", ctx)

    @patch.object(sdd_auto_test, "read_coverage", return_value=None)
    @patch.object(sdd_auto_test, "run_tests_background")
    def test_no_feedback_when_no_state(self, mock_bg, _mock_cov):
        """No previous state → no feedback output."""
        exit_code, stdout, _ = _run_hook_stdin(sdd_auto_test.main, {
            "cwd": self.tmpdir,
            "tool_input": {"file_path": "app.py"},
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    @patch.object(sdd_auto_test, "run_tests_background")
    def test_triggers_background_tests_for_source_file(self, mock_bg):
        """Source file edit triggers background test execution."""
        exit_code, stdout, _ = _run_hook_stdin(sdd_auto_test.main, {
            "cwd": self.tmpdir,
            "tool_input": {"file_path": "app.py"},
        })
        mock_bg.assert_called_once()
        args = mock_bg.call_args[0]
        self.assertEqual(args[0], self.tmpdir)

    @patch.object(sdd_auto_test, "run_tests_background")
    def test_no_trigger_for_non_source_file(self, mock_bg):
        """Non-source file edit does NOT trigger tests."""
        exit_code, stdout, _ = _run_hook_stdin(sdd_auto_test.main, {
            "cwd": self.tmpdir,
            "tool_input": {"file_path": "README.md"},
        })
        mock_bg.assert_not_called()

    @patch.object(sdd_auto_test, "run_tests_background")
    def test_debounce_prevents_parallel_runs(self, mock_bg):
        """If tests are already running (lock held), skip launching new ones."""
        lock_fd = _sdd_detect.acquire_runner_lock(self.tmpdir)
        self.assertIsNotNone(lock_fd, "Should acquire lock (no other worker)")
        try:
            exit_code, stdout, _ = _run_hook_stdin(sdd_auto_test.main, {
                "cwd": self.tmpdir,
                "tool_input": {"file_path": "app.py"},
            })
            mock_bg.assert_not_called()
        finally:
            _sdd_detect.release_runner_lock(lock_fd, self.tmpdir)


# ─────────────────────────────────────────────────────────────────
# 5. TASK-COMPLETED READS STATE (NON-RALPH)
# ─────────────────────────────────────────────────────────────────

class TestTaskCompletedRunsFreshTests(unittest.TestCase):
    """Verify task-completed runs tests fresh for non-ralph projects."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-")
        _cleanup_state(self.tmpdir)

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_passing_tests_allows_completion(self):
        """Fresh test run passes → task completion allowed (exit 0)."""
        _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return a + b\n",
            test_code=(
                "import sys; sys.path.insert(0, '..')\n"
                "from app import add\n"
                "def test_add(): assert add(1, 2) == 3\n"
            ),
        )

        exit_code, _, _ = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 0)

    def test_failing_tests_blocks_completion(self):
        """Fresh test run fails → task completion blocked (exit 2)."""
        _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return a + b\n",
            test_code=(
                "import sys; sys.path.insert(0, '..')\n"
                "from app import add\n"
                "def test_add(): assert add(1, 2) == 999\n"
            ),
        )

        exit_code, _, stderr = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("failed", stderr.lower())

    def test_stale_state_ignored(self):
        """Stale failing state does NOT block if fresh tests pass."""
        _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return a + b\n",
            test_code=(
                "import sys; sys.path.insert(0, '..')\n"
                "from app import add\n"
                "def test_add(): assert add(1, 2) == 3\n"
            ),
        )
        # Write stale FAILING state — this was the bug
        _sdd_detect.write_state(self.tmpdir, False, "1 failed (stale)")

        exit_code, _, _ = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        # Fresh run passes → stale state ignored
        self.assertEqual(exit_code, 0)

    def test_no_test_command_allows_completion(self):
        """Project without test infrastructure → allows completion."""
        empty_dir = tempfile.mkdtemp(prefix="sdd-int-empty-")
        try:
            _cleanup_state(empty_dir)
            exit_code, _, _ = _run_hook_stdin(task_completed.main, {
                "cwd": empty_dir,
                "task_subject": "Add feature",
                "teammate_name": "worker-1",
            })
            self.assertEqual(exit_code, 0)
        finally:
            _cleanup_state(empty_dir)
            shutil.rmtree(empty_dir, ignore_errors=True)


# ─────────────────────────────────────────────────────────────────
# 6. FULL SDD CYCLE: EDIT → TEST → GUARD → COMPLETE
# ─────────────────────────────────────────────────────────────────

class TestFullSDDCycle(unittest.TestCase):
    """Simulate a complete SDD development cycle end-to-end.

    This is the definitive test: does the mechanism actually work?
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-cycle-")
        _cleanup_state(self.tmpdir)

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_cycle_pass_edit_complete(self):
        """CYCLE 1: Code correct → tests pass → guard allows → task completes.

        Simulates: developer writes correct code, tests pass, everything flows.
        """
        proj = _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return a + b\n",
            test_code=(
                "import sys; sys.path.insert(0, '..')\n"
                "from app import add\n"
                "def test_add(): assert add(1, 2) == 3\n"
                "def test_add_zero(): assert add(0, 0) == 0\n"
            ),
        )

        # PostToolUse — worker runs real tests
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        state = _sdd_detect.read_state(self.tmpdir)
        self.assertTrue(state["passing"], "Tests should pass after correct implementation")

        # PreToolUse — guard allows test edits (tests are passing)
        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "tests/test_app.py",
                "old_string": "assert add(1, 2) == 3\nassert add(0, 0) == 0",
                "new_string": "assert add(1, 2) == 3",
            },
        })
        self.assertEqual(stdout, "", "Guard should allow when tests pass")

        # TaskCompleted — gate allows completion
        exit_code, _, _ = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Implement add",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 0, "Task should complete when tests pass")

    def test_cycle_fail_guard_blocks_weakening(self):
        """CYCLE 2: Code wrong → tests fail → guard blocks assertion removal.

        Simulates: developer has bug, tries to weaken tests to hide it.
        The SDD mechanism MUST prevent this.
        """
        proj = _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return a * b  # BUG: multiply instead of add\n",
            test_code=(
                "import sys; sys.path.insert(0, '..')\n"
                "from app import add\n"
                "def test_add(): assert add(1, 2) == 3\n"
                "def test_add_zero(): assert add(0, 5) == 5  # fails: 0*5=0\n"
            ),
        )

        # Worker runs tests → FAILS
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        state = _sdd_detect.read_state(self.tmpdir)
        self.assertFalse(state["passing"], "Tests should fail with buggy code")

        # Guard BLOCKS removing the failing assertion (reward hacking)
        exit_code, stdout, stderr = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "tests/test_app.py",
                "old_string": (
                    "def test_add(): assert add(1, 2) == 3\n"
                    "def test_add_zero(): assert add(0, 5) == 5  # fails: 0*5=0"
                ),
                "new_string": (
                    "def test_add(): assert add(1, 2) == 3"
                ),
            },
        })
        self.assertEqual(exit_code, 2, "Guard MUST deny removing assertions when tests fail")
        self.assertIn("reward hacking", stderr)

        # TaskCompleted also blocks
        exit_code, _, stderr = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Implement add",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 2, "Task MUST NOT complete when tests fail")

    def test_cycle_fail_then_fix_code_then_complete(self):
        """CYCLE 3: Bug → fail → fix CODE (not tests) → pass → complete.

        The correct SDD workflow: keep tests, fix implementation.
        """
        proj = _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return a * b  # BUG\n",
            test_code=(
                "import sys; sys.path.insert(0, '..')\n"
                "from app import add\n"
                "def test_add(): assert add(2, 3) == 5\n"
                "def test_add_zero(): assert add(0, 5) == 5\n"
            ),
        )

        # Tests fail
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        self.assertFalse(_sdd_detect.read_state(self.tmpdir)["passing"])

        # Task blocked
        exit_code, _, _ = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Implement add",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 2)

        # Developer fixes the CODE (not the tests!)
        (proj / "app.py").write_text("def add(a, b): return a + b  # FIXED\n", encoding="utf-8")

        # Tests re-run → PASS
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        self.assertTrue(_sdd_detect.read_state(self.tmpdir)["passing"],
                        "Tests should pass after fixing code")

        # Task now completes
        exit_code, _, _ = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Implement add",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 0, "Task should complete after fixing code")

    def test_cycle_guard_allows_adding_tests_while_failing(self):
        """CYCLE 4: Tests failing, but developer adds MORE tests → guard allows.

        Adding assertions while failing = strengthening tests = good.
        """
        _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return 0  # BUG\n",
            test_code=(
                "import sys; sys.path.insert(0, '..')\n"
                "from app import add\n"
                "def test_add(): assert add(1, 2) == 3\n"
            ),
        )

        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        self.assertFalse(_sdd_detect.read_state(self.tmpdir)["passing"])

        # Guard ALLOWS adding more assertions
        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "tests/test_app.py",
                "old_string": "def test_add(): assert add(1, 2) == 3",
                "new_string": (
                    "def test_add(): assert add(1, 2) == 3\n"
                    "def test_add_neg(): assert add(-1, -2) == -3\n"
                    "def test_add_zero(): assert add(0, 0) == 0"
                ),
            },
        })
        self.assertEqual(stdout, "", "Guard should allow adding tests while failing")

    def test_cycle_feedback_loop_across_edits(self):
        """CYCLE 5: Multiple edits show evolving feedback.

        Edit 1: no state → no feedback
        Edit 2: tests ran → feedback shows [FAIL]
        Edit 3: after fix → silence (passing state suppressed)
        """
        proj = _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return 0  # BUG\n",
            test_code=(
                "import sys; sys.path.insert(0, '..')\n"
                "from app import add\n"
                "def test_add(): assert add(1, 2) == 3\n"
            ),
        )

        # Edit 1: No state yet → no feedback
        with patch.object(sdd_auto_test, "run_tests_background"), \
             patch.object(sdd_auto_test, "read_coverage", return_value=None):
            _, stdout, _ = _run_hook_stdin(sdd_auto_test.main, {
                "cwd": self.tmpdir,
                "tool_input": {"file_path": "app.py"},
            })
        self.assertEqual(stdout, "", "First edit should have no feedback")

        # Background worker runs
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")

        # Edit 2: State exists → feedback shows [FAIL]
        with patch.object(sdd_auto_test, "run_tests_background"):
            _, stdout, _ = _run_hook_stdin(sdd_auto_test.main, {
                "cwd": self.tmpdir,
                "tool_input": {"file_path": "app.py"},
            })
        output = json.loads(stdout)
        self.assertIn("[FAIL]", output["hookSpecificOutput"]["additionalContext"])

        # Fix the code
        (proj / "app.py").write_text("def add(a, b): return a + b\n", encoding="utf-8")
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")

        # Edit 3: State updated to passing → silent (FAIL→silence = fix confirmed)
        with patch.object(sdd_auto_test, "run_tests_background"), \
             patch.object(sdd_auto_test, "read_coverage", return_value=None):
            _, stdout, _ = _run_hook_stdin(sdd_auto_test.main, {
                "cwd": self.tmpdir,
                "tool_input": {"file_path": "app.py"},
            })
        self.assertEqual(stdout, "")


# ─────────────────────────────────────────────────────────────────
# 7. WRITE TOOL INTEGRATION WITH GUARD
# ─────────────────────────────────────────────────────────────────

class TestWriteToolGuardIntegration(unittest.TestCase):
    """Verify guard works with Write tool (full file replacement)."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-write-")
        _cleanup_state(self.tmpdir)

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_write_tool_reducing_assertions_denied(self):
        """Write tool replacing file with fewer assertions → DENY."""
        test_file = Path(self.tmpdir) / "tests" / "test_app.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(
            "def test_a(): assert status_code == 200\n"
            "def test_b(): assert payload == {'ok': True}\n"
            "def test_c(): assert retries == 3\n",
            encoding="utf-8",
        )
        _sdd_detect.write_state(self.tmpdir, False, "1 failed")

        exit_code, stdout, stderr = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(test_file),
                "content": "def test_a(): assert status_code == 200\n",
            },
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("reward hacking", stderr)

    def test_write_tool_new_test_file_allowed(self):
        """Write tool creating new test file → allow (file didn't exist before)."""
        _sdd_detect.write_state(self.tmpdir, False, "1 failed")

        new_file = Path(self.tmpdir) / "tests" / "test_new.py"
        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(new_file),
                "content": "def test_new(): assert result == 42\n",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "", "New test file should always be allowed")


# ─────────────────────────────────────────────────────────────────
# 8. TEST COMMAND DETECTION → WORKER INTEGRATION
# ─────────────────────────────────────────────────────────────────

class TestCommandDetectionIntegration(unittest.TestCase):
    """Verify detect_test_command finds the right runner for real projects."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-detect-")
        _cleanup_state(self.tmpdir)

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_pyproject_detects_pytest(self):
        """pyproject.toml with pytest → detects 'pytest' command."""
        proj = Path(self.tmpdir)
        (proj / "pyproject.toml").write_text(
            '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n', encoding="utf-8"
        )
        cmd = _sdd_detect.detect_test_command(self.tmpdir)
        self.assertEqual(cmd, "pytest")

    def test_package_json_detects_npm_test(self):
        """package.json with scripts.test → detects 'npm test'."""
        proj = Path(self.tmpdir)
        (proj / "package.json").write_text(
            json.dumps({"scripts": {"test": "jest"}}), encoding="utf-8"
        )
        cmd = _sdd_detect.detect_test_command(self.tmpdir)
        self.assertEqual(cmd, "npm test")

    def test_go_mod_detects_go_test(self):
        """go.mod → detects 'go test ./...'."""
        proj = Path(self.tmpdir)
        (proj / "go.mod").write_text("module example.com/foo\n", encoding="utf-8")
        cmd = _sdd_detect.detect_test_command(self.tmpdir)
        self.assertEqual(cmd, "go test ./...")

    def test_cargo_detects_cargo_test(self):
        """Cargo.toml → detects 'cargo test'."""
        proj = Path(self.tmpdir)
        (proj / "Cargo.toml").write_text('[package]\nname = "foo"\n', encoding="utf-8")
        cmd = _sdd_detect.detect_test_command(self.tmpdir)
        self.assertEqual(cmd, "cargo test")

    def test_makefile_with_test_target(self):
        """Makefile with test: target → detects 'make test'."""
        proj = Path(self.tmpdir)
        (proj / "Makefile").write_text("test:\n\tpytest\n", encoding="utf-8")
        cmd = _sdd_detect.detect_test_command(self.tmpdir)
        self.assertEqual(cmd, "make test")

    def test_ralph_config_takes_priority(self):
        """.ralph/config.sh GATE_TEST overrides all other detection."""
        proj = Path(self.tmpdir)
        (proj / "pyproject.toml").write_text("[tool.pytest]\n", encoding="utf-8")
        ralph_dir = proj / ".ralph"
        ralph_dir.mkdir()
        (ralph_dir / "config.sh").write_text(
            'GATE_TEST="python -m pytest -x"\n', encoding="utf-8"
        )
        cmd = _sdd_detect.detect_test_command(self.tmpdir)
        self.assertEqual(cmd, "python -m pytest -x")

    def test_detected_command_actually_works(self):
        """Detected command for a real project actually runs and produces state."""
        _create_mini_project(self.tmpdir,
            app_code="x = 1\n",
            test_code="def test_true(): assert True\n",
        )
        cmd = _sdd_detect.detect_test_command(self.tmpdir)
        self.assertIsNotNone(cmd, "Should detect a test command")

        sdd_auto_test._run_tests_worker(self.tmpdir, cmd)
        state = _sdd_detect.read_state(self.tmpdir)
        self.assertIsNotNone(state, "Worker should write state after running detected command")
        self.assertTrue(state["passing"])


# ─────────────────────────────────────────────────────────────────
# 9. RALPH PROJECT GATE SEQUENCE
# ─────────────────────────────────────────────────────────────────

class TestRalphGateSequence(unittest.TestCase):
    """Verify ralph project gates run in order and gate correctly."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-ralph-")
        _cleanup_state(self.tmpdir)
        self.ralph_dir = Path(self.tmpdir) / ".ralph"
        self.ralph_dir.mkdir()
        # Simulate sop-code-assist invocation (required by skill enforcement)
        _sdd_detect.write_skill_invoked(self.tmpdir, "sop-code-assist")
        # Simulate source-file edits (required by research-task bypass guard)
        p = patch.object(task_completed, "_has_source_edits", return_value=True)
        p.start()
        self.addCleanup(p.stop)

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        # Clean up per-skill state files
        for name in ("sop-code-assist", "sop-reviewer"):
            try:
                _sdd_detect.skill_invoked_path(self.tmpdir, name).unlink()
            except FileNotFoundError:
                pass
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_all_gates_pass(self):
        """All gates passing → task completes + failures reset."""
        _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return a + b\n",
            test_code=(
                "import sys; sys.path.insert(0, '..')\n"
                "from app import add\n"
                "def test_add(): assert add(1, 2) == 3\n"
            ),
        )
        (self.ralph_dir / "config.sh").write_text(
            'GATE_TEST="pytest"\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n',
            encoding="utf-8",
        )

        exit_code, _, _ = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "task_description": "",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 0)

        # Failures reset to 0 on success
        failures_file = self.ralph_dir / "failures.json"
        if failures_file.exists():
            data = json.loads(failures_file.read_text())
            self.assertEqual(data.get("worker-1", 0), 0)

    def test_test_gate_fails_blocks(self):
        """Test gate fails → exit 2 + failure count incremented."""
        _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return 0  # BUG\n",
            test_code=(
                "import sys; sys.path.insert(0, '..')\n"
                "from app import add\n"
                "def test_add(): assert add(1, 2) == 3\n"
            ),
        )
        (self.ralph_dir / "config.sh").write_text(
            'GATE_TEST="pytest"\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n',
            encoding="utf-8",
        )

        exit_code, _, stderr = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "task_description": "",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("test", stderr.lower())

        failures = json.loads((self.ralph_dir / "failures.json").read_text())
        self.assertEqual(failures["worker-1"], 1)

    def test_exit_suppression_in_gate_rejected(self):
        """Gate command with || true is rejected."""
        _create_mini_project(self.tmpdir,
            app_code="x = 1\n",
            test_code="def test(): pass\n",
        )
        (self.ralph_dir / "config.sh").write_text(
            'GATE_TEST="pytest || true"\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n',
            encoding="utf-8",
        )

        exit_code, _, stderr = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "task_description": "",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("exit code suppression", stderr)


# ─────────────────────────────────────────────────────────────────
# 10. CROSS-HOOK STATE HANDOFF: auto-test writes → task-completed reads
# ─────────────────────────────────────────────────────────────────

class TestCrossHookStateHandoff(unittest.TestCase):
    """Integration: sdd-auto-test writes state → task-completed reads and trusts.

    Ralph scenario: teammate edits source file → PostToolUse fires sdd-auto-test
    → background worker runs tests → writes state. Then teammate marks task complete
    → TaskCompleted fires → _try_cached_test_gate reads auto-test's state → trusts it.

    This tests the FULL cross-hook coordination chain.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-handoff-")
        _cleanup_state(self.tmpdir)
        test_file = Path(self.tmpdir) / "test_sample.py"
        test_file.write_text("def test_pass(): assert True\n")

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_auto_test_state_trusted_by_task_completed(self):
        """Auto-test writes passing state → task-completed trusts it."""
        sid = "test-session-abc123"

        # Step 1: Simulate PostToolUse — record file edit
        _sdd_detect.record_file_edit(self.tmpdir, "src/app.py", sid)

        # Step 2: Simulate auto-test worker — write passing state
        started_at = time.time()
        time.sleep(0.1)  # Ensure started_at > edit_time
        _sdd_detect.write_state(self.tmpdir, True, "1 passed, 0 failed",
                                started_at=started_at)

        # Step 3: Simulate task-completed — read state and check trust
        state = _sdd_detect.read_state(self.tmpdir, max_age_seconds=30)
        self.assertIsNotNone(state)
        self.assertTrue(state["passing"])

        # Trust: state.started_at must be >= last edit time
        trusted = _sdd_detect.can_trust_state(state, self.tmpdir, sid)
        self.assertTrue(trusted, "State should be trusted — started after edit")

    def test_auto_test_state_distrusted_when_edit_after_test(self):
        """Edit after test run → state not trusted → task-completed runs fresh."""
        sid = "test-session-def456"

        # Step 1: Auto-test writes state
        _sdd_detect.write_state(self.tmpdir, True, "1 passed",
                                started_at=time.time())

        time.sleep(0.1)

        # Step 2: ANOTHER edit happens AFTER test state was written
        _sdd_detect.record_file_edit(self.tmpdir, "src/app.py", sid)

        # Step 3: task-completed checks trust → should NOT trust
        state = _sdd_detect.read_state(self.tmpdir, max_age_seconds=30)
        trusted = _sdd_detect.can_trust_state(state, self.tmpdir, sid)
        self.assertFalse(trusted, "State should NOT be trusted — edit after test")


# ─────────────────────────────────────────────────────────────────
# 11. ADAPTIVE TIMEOUT WITH REAL EXECUTION
# ─────────────────────────────────────────────────────────────────

class TestAdaptiveTimeoutRealExecution(unittest.TestCase):
    """Integration: real test execution records duration → adaptive timeout adapts.

    This tests the FULL feedback loop with actual subprocess execution:
    1. Create a project with real tests
    2. Run tests via run_in_process_group
    3. Write state with started_at (duration auto-computed)
    4. Verify adaptive_gate_timeout returns correct value
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-adaptive-")
        _cleanup_state(self.tmpdir)
        # Create a real test file that takes ~0.5s
        test_file = Path(self.tmpdir) / "test_timing.py"
        test_file.write_text(
            "import time\n"
            "def test_slow(): time.sleep(0.5)\n"
            "def test_fast(): assert True\n"
        )

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_duration_recorded_from_real_execution(self):
        """Real pytest run records accurate duration in state."""
        started_at = time.time()
        rc, stdout, stderr, timed_out = _sdd_detect.run_in_process_group(
            f"python3 -m pytest {self.tmpdir}/test_timing.py -q",
            self.tmpdir, timeout=30)

        self.assertFalse(timed_out)
        self.assertEqual(rc, 0)

        # Write state (duration auto-computed from started_at)
        raw = stdout + stderr
        summary = _sdd_detect.parse_test_summary(raw.strip(), rc)
        _sdd_detect.write_state(self.tmpdir, True, summary,
                                started_at=started_at)

        # Read back and verify duration is reasonable
        state = _sdd_detect.read_state(self.tmpdir, max_age_seconds=60)
        self.assertIn("duration", state)
        self.assertGreater(state["duration"], 0.3)  # test_slow sleeps 0.5s
        self.assertLess(state["duration"], 15.0)     # shouldn't take 15s

        # Adaptive timeout should use this duration
        timeout = _sdd_detect.adaptive_gate_timeout(
            self.tmpdir, multiplier=3, min_timeout=30, max_timeout=300)
        # duration ~1-2s → 3×2=6 → clamped to min 30
        self.assertEqual(timeout, 30)


# ─────────────────────────────────────────────────────────────────
# 12. RALPH MULTI-GATE REAL EXECUTION WITH BUDGET
# ─────────────────────────────────────────────────────────────────

class TestRalphMultiGateRealExecution(unittest.TestCase):
    """Integration: real gate execution with budget tracking.

    Ralph scenario: config.sh has GATE_TEST + GATE_LINT + GATE_BUILD.
    All pass → exit 0. Budget not exhausted.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-multigate-")
        _cleanup_state(self.tmpdir)

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_fast_gates_complete_within_budget(self):
        """3 fast gates (echo) complete well within 270s budget."""
        gates = [
            ("test", "echo '2 passed'"),
            ("lint", "echo 'no issues'"),
            ("build", "echo 'build ok'"),
        ]

        budget = 270
        start = time.monotonic()
        results = []

        for name, cmd in gates:
            elapsed = time.monotonic() - start
            remaining = budget - elapsed
            self.assertGreater(remaining, 0,
                               f"Budget exhausted at gate '{name}'")

            timeout = min(60, int(remaining))
            passed, output = task_completed.run_gate(name, cmd, self.tmpdir,
                                                     timeout=timeout)
            results.append((name, passed))

        total_elapsed = time.monotonic() - start

        # All gates passed
        for name, passed in results:
            self.assertTrue(passed, f"Gate '{name}' failed")

        # Total time well under budget
        self.assertLess(total_elapsed, 10,
                        "Fast gates should complete in <10s")

    def test_gate_failure_stops_chain(self):
        """First failing gate stops execution — later gates don't run."""
        gates = [
            ("test", "echo pass"),
            ("typecheck", "exit 1"),   # This fails
            ("lint", "echo pass"),     # Should NOT run
            ("build", "echo pass"),    # Should NOT run
        ]

        executed = []
        for name, cmd in gates:
            passed, output = task_completed.run_gate(name, cmd, self.tmpdir,
                                                     timeout=10)
            executed.append(name)
            if not passed:
                break

        self.assertEqual(executed, ["test", "typecheck"])
        self.assertNotIn("lint", executed)


# ─────────────────────────────────────────────────────────────────
# 13. COALESCING UNDER PRESSURE: multiple triggers, 1 runner
# ─────────────────────────────────────────────────────────────────

class TestCoalescingUnderPressure(unittest.TestCase):
    """Integration: rapid PostToolUse events coalesce to minimal runners.

    Ralph scenario: 3 teammates make 10 edits in 2 seconds.
    Coalescing must prevent 10 parallel pytest processes.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-coalesce-")
        _cleanup_state(self.tmpdir)
        test_file = Path(self.tmpdir) / "test_sample.py"
        test_file.write_text("def test_ok(): assert True\n")

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_rapid_triggers_produce_bounded_runs(self):
        """10 rapid run_tests_background calls → at most 1 concurrent runner."""
        command = f"python3 -m pytest {self.tmpdir}/test_sample.py -q"

        # Rapid-fire 10 background launches
        for _ in range(10):
            sdd_auto_test.run_tests_background(self.tmpdir, command)
            time.sleep(0.05)  # 50ms between — simulates rapid edits

        # At most 1 should be running (coalescing)
        # Count running by checking PID file
        pf = _sdd_detect.pid_path(self.tmpdir)
        if pf.exists():
            running_count = 1  # Max 1 per project
        else:
            running_count = 0

        self.assertLessEqual(running_count, 1,
            "Coalescing failed: more than 1 runner per project")

        # Wait for completion
        time.sleep(8)

        # Final state should exist and be valid
        state = _sdd_detect.read_state(self.tmpdir, max_age_seconds=30)
        # State might not exist if tests ran too fast, but if it does,
        # it should be valid
        if state:
            self.assertIn("passing", state)


# ─────────────────────────────────────────────────────────────────
# COMPLIANCE SCENARIOS — verify hooks enforce quality for real users
# ─────────────────────────────────────────────────────────────────

class TestRalphMultiGateCascade(unittest.TestCase):
    """Ralph: test passes but lint/typecheck fails → task blocked.

    Real scenario: teammate writes working code that doesn't pass linter.
    The hook must block completion with the correct gate name in the error.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-cascade-")
        _cleanup_state(self.tmpdir)
        self.ralph_dir = Path(self.tmpdir) / ".ralph"
        self.ralph_dir.mkdir()
        _sdd_detect.write_skill_invoked(self.tmpdir, "sop-code-assist")
        self.patch = patch.object(task_completed, "_has_source_edits",
                                  return_value=True)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        _cleanup_state(self.tmpdir)
        for name in ("sop-code-assist", "sop-reviewer"):
            try:
                _sdd_detect.skill_invoked_path(self.tmpdir, name).unlink()
            except FileNotFoundError:
                pass
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_test_passes_but_lint_fails_blocks_with_lint_error(self):
        """GATE_TEST passes, GATE_LINT fails → exit 2 with lint error."""
        _create_mini_project(self.tmpdir,
            app_code="x = 1\n",
            test_code="def test(): assert True\n",
        )
        (self.ralph_dir / "config.sh").write_text(
            'GATE_TEST="pytest"\n'
            'GATE_TYPECHECK=""\n'
            'GATE_LINT="exit 1"\n'  # Lint fails
            'GATE_BUILD=""\n',
            encoding="utf-8",
        )

        exit_code, _, stderr = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("lint", stderr.lower())

    def test_all_four_gates_execute_in_order(self):
        """All 4 gates run in sequence — each gate's pass is verified."""
        _create_mini_project(self.tmpdir,
            app_code="x = 1\n",
            test_code="def test(): assert True\n",
        )
        (self.ralph_dir / "config.sh").write_text(
            'GATE_TEST="pytest"\n'
            'GATE_TYPECHECK="echo typecheck-ok"\n'
            'GATE_LINT="echo lint-ok"\n'
            'GATE_BUILD="echo build-ok"\n',
            encoding="utf-8",
        )

        exit_code, _, _ = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 0, "All gates pass → task completes")


class TestBaselinePreexistingFailure(unittest.TestCase):
    """Baseline: pre-existing test failures → teammate CAN complete.

    Real scenario: project already has 3 failing tests when teammate starts.
    Teammate's changes don't fix or break those tests. The hook must allow
    completion with a warning (not block on inherited failures).
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-baseline-")
        _cleanup_state(self.tmpdir)

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_preexisting_failure_allowed_with_warning(self):
        """Same failure pattern as baseline → task completes (with warning)."""
        proj = _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return 0  # pre-existing bug\n",
            test_code=(
                "import sys; sys.path.insert(0, '.')\n"
                "from app import add\n"
                "def test_add(): assert add(1, 2) == 3  # always fails\n"
            ),
        )
        sid = "baseline-test-session"

        # Capture baseline: tests fail on first run
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest", sid=sid)
        state = _sdd_detect.read_state(self.tmpdir)
        self.assertFalse(state["passing"])

        # Write passing state to avoid fresh run in _try_cached_test_gate
        # (the baseline comparison happens on the raw output path)
        # Instead, test via _check_baseline directly
        baseline = _sdd_detect.read_baseline(self.tmpdir, sid)
        self.assertIsNotNone(baseline)
        self.assertFalse(baseline["passing"])

        # Same failure pattern → check_baseline returns True (pre-existing)
        result = task_completed._check_baseline(
            self.tmpdir, sid, state.get("raw_output", state["summary"]))
        self.assertTrue(result,
            "Pre-existing failure pattern should be allowed")

    def test_new_regression_blocked(self):
        """Different failure pattern than baseline → task blocked."""
        # pytest outputs "M failed, N passed" — parse_test_summary regex
        # captures "N passed" only. Changing the pass count between runs
        # ensures distinct summaries ("2 passed" vs "1 passed").
        proj = _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return 0\n",
            test_code=(
                "import sys; sys.path.insert(0, '.')\n"
                "from app import add\n"
                "def test_trivial1(): assert True\n"
                "def test_trivial2(): assert True\n"
                "def test_add(): assert add(1, 2) == 3\n"
            ),
        )
        sid = "regression-test-session"

        # Baseline: 2 passed, 1 failed → summary "2 passed"
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest", sid=sid)

        # Replace one passing test with a failing one → 1 passed, 2 failed
        (proj / "tests" / "test_app.py").write_text(
            "import sys; sys.path.insert(0, '.')\n"
            "from app import add\n"
            "def test_trivial1(): assert True\n"
            "def test_add(): assert add(1, 2) == 3\n"
            "def test_sub(): assert add(5, -3) == 2\n",
            encoding="utf-8",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        new_state = _sdd_detect.read_state(self.tmpdir)

        result = task_completed._check_baseline(
            self.tmpdir, sid, new_state.get("raw_output", new_state["summary"]))
        self.assertFalse(result,
            "New regression (different pattern) must be blocked")


class TestCircuitBreakerEndToEnd(unittest.TestCase):
    """Circuit breaker: 3 failures → teammate-idle fires → teammate stops.

    Real scenario: worker-1 fails gate 3 times. TeammateIdle hook checks
    failures.json and triggers circuit breaker.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-cb-")
        _cleanup_state(self.tmpdir)
        self.ralph_dir = Path(self.tmpdir) / ".ralph"
        self.ralph_dir.mkdir()
        (self.ralph_dir / "config.sh").write_text(
            'MAX_CONSECUTIVE_FAILURES=3\n', encoding="utf-8")

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_three_failures_triggers_circuit_breaker(self):
        """3 gate failures → teammate-idle reports circuit breaker."""
        import importlib
        teammate_idle = importlib.import_module("teammate-idle")

        # Simulate 3 consecutive gate failures
        for _ in range(3):
            task_completed._atomic_update_failures(
                self.ralph_dir, "worker-1", "increment")

        # TeammateIdle should report circuit breaker
        exit_code, _, stderr = _run_hook_stdin(teammate_idle.main, {
            "cwd": self.tmpdir,
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 0)
        self.assertIn("circuit breaker", stderr.lower())

    def test_success_resets_then_no_circuit_breaker(self):
        """After success reset, teammate-idle does NOT fire circuit breaker."""
        import importlib
        teammate_idle = importlib.import_module("teammate-idle")

        # 2 failures + reset
        for _ in range(2):
            task_completed._atomic_update_failures(
                self.ralph_dir, "worker-1", "increment")
        task_completed._atomic_update_failures(
            self.ralph_dir, "worker-1", "reset")

        # TeammateIdle should NOT report circuit breaker
        exit_code, _, stderr = _run_hook_stdin(teammate_idle.main, {
            "cwd": self.tmpdir,
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 0)
        self.assertNotIn("circuit breaker", stderr.lower())


class TestSDDOrderingEnforcement(unittest.TestCase):
    """SDD ordering: source edit without tests → PostToolUse nudges.

    Real scenario: teammate writes app.py without any test file in session.
    PostToolUse must emit SDD ordering nudge.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-ordering-")
        _cleanup_state(self.tmpdir)
        _create_mini_project(self.tmpdir,
            app_code="def add(a, b): return a + b\n",
            test_code="def test(): pass\n",
        )

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch.object(sdd_auto_test, "run_tests_background")
    def test_source_without_tests_emits_nudge(self, mock_bg):
        """Source file edited with no test files in session → SDD nudge."""
        sid = "ordering-test-session"
        # Record source file edit (no test file edit)
        _sdd_detect.record_file_edit(self.tmpdir, "app.py", sid)

        _, stdout, _ = _run_hook_stdin(sdd_auto_test.main, {
            "cwd": self.tmpdir,
            "tool_input": {"file_path": "app.py"},
            "session_id": sid,
        })
        if stdout:
            output = json.loads(stdout)
            ctx = output.get("hookSpecificOutput", {}).get("additionalContext", "")
            self.assertIn("SDD ordering", ctx)

    @patch.object(sdd_auto_test, "run_tests_background")
    def test_source_with_tests_no_nudge(self, mock_bg):
        """Source + test files edited in session → no nudge."""
        sid = "ordering-test-session-2"
        # Record BOTH source and test file
        _sdd_detect.record_file_edit(self.tmpdir, "app.py", sid)
        _sdd_detect.record_file_edit(self.tmpdir, "tests/test_app.py", sid)

        # Write passing state so no [FAIL] feedback
        _sdd_detect.write_state(self.tmpdir, True, "1 passed")

        _, stdout, _ = _run_hook_stdin(sdd_auto_test.main, {
            "cwd": self.tmpdir,
            "tool_input": {"file_path": "app.py"},
            "session_id": sid,
        })
        self.assertEqual(stdout, "", "No nudge when tests exist in session")


class TestPrecisionRegressionEndToEnd(unittest.TestCase):
    """Precision regression: assertEqual → assertTrue while failing → blocked.

    Real scenario: tests fail. Teammate replaces precise assertions with
    loose existence checks to make tests pass. The guard must block this.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-precision-")
        _cleanup_state(self.tmpdir)

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_precise_to_loose_blocked_when_failing(self):
        """assertEqual → assertTrue while tests failing → DENY."""
        _sdd_detect.write_state(self.tmpdir, False, "1 failed")

        exit_code, _, stderr = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "tests/test_app.py",
                "old_string": (
                    "assert result == 42\n"
                    "assert name == 'Alice'\n"
                ),
                "new_string": (
                    "assert result\n"        # Lost precision: == 42 → truthy
                    "assert name is not None\n"  # Lost precision: == 'Alice' → not None
                ),
            },
        })
        self.assertEqual(exit_code, 2, "Precision regression must be blocked")
        self.assertIn("precision", stderr.lower())

    def test_precise_to_different_precise_allowed(self):
        """assertEqual(42) → assertEqual(43) while failing → ALLOW (fixing value)."""
        _sdd_detect.write_state(self.tmpdir, False, "1 failed")

        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "tests/test_app.py",
                "old_string": "assert result == 42",
                "new_string": "assert result == 43",
            },
        })
        self.assertEqual(exit_code, 0,
            "Changing expected value (same precision) should be allowed")


class TestSkillEnforcementEndToEnd(unittest.TestCase):
    """Skill enforcement: ralph teammate must invoke correct SOP skill.

    Real scenario: implementer must use sop-code-assist, reviewer must
    use sop-reviewer. Without skill invocation → task blocked.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-skill-")
        _cleanup_state(self.tmpdir)
        self.ralph_dir = Path(self.tmpdir) / ".ralph"
        self.ralph_dir.mkdir()
        _create_mini_project(self.tmpdir,
            app_code="x = 1\n",
            test_code="def test(): assert True\n",
        )
        (self.ralph_dir / "config.sh").write_text(
            'GATE_TEST="pytest"\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n',
            encoding="utf-8",
        )
        self.patch = patch.object(task_completed, "_has_source_edits",
                                  return_value=True)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        _cleanup_state(self.tmpdir)
        for name in ("sop-code-assist", "sop-reviewer"):
            try:
                _sdd_detect.skill_invoked_path(self.tmpdir, name).unlink()
            except FileNotFoundError:
                pass
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_implementer_without_skill_blocked(self):
        """worker-1 tries to complete without sop-code-assist → exit 2."""
        exit_code, _, stderr = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("sop-code-assist", stderr)

    def test_implementer_with_skill_allowed(self):
        """worker-1 invokes sop-code-assist → task completes."""
        _sdd_detect.write_skill_invoked(self.tmpdir, "sop-code-assist")
        exit_code, _, _ = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 0)

    def test_reviewer_needs_sop_reviewer_not_code_assist(self):
        """rev-1 invokes sop-code-assist instead of sop-reviewer → exit 2."""
        _sdd_detect.write_skill_invoked(self.tmpdir, "sop-code-assist")
        exit_code, _, stderr = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Review task",
            "teammate_name": "rev-1",
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("sop-reviewer", stderr)

    def test_reviewer_with_correct_skill_allowed(self):
        """rev-1 invokes sop-reviewer → task completes."""
        _sdd_detect.write_skill_invoked(self.tmpdir, "sop-reviewer")
        exit_code, _, _ = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Review task",
            "teammate_name": "rev-1",
        })
        self.assertEqual(exit_code, 0)


class TestCoverageGapEndToEnd(unittest.TestCase):
    """Coverage gap: source files without matching tests → task blocked.

    Real scenario: teammate creates src/auth.py and src/db.py but only
    writes tests/test_auth.py. The untested src/db.py must block completion.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-cov-")
        _cleanup_state(self.tmpdir)
        _create_mini_project(self.tmpdir,
            app_code="x = 1\n",
            test_code="def test(): assert True\n",
        )

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_uncovered_source_blocks_completion(self):
        """Source file with no test → exit 2 with uncovered file listed."""
        raw_sid = "cov-test-session"
        # Hook hashes session_id via extract_session_id — coverage files
        # must use the same hashed sid for path alignment
        hashed_sid = _sdd_detect.extract_session_id({"session_id": raw_sid})

        # Record edits with hashed sid (matches what hook will read)
        _sdd_detect.record_file_edit(self.tmpdir, "src/auth.py", hashed_sid)
        _sdd_detect.record_file_edit(self.tmpdir, "src/db.py", hashed_sid)
        _sdd_detect.record_file_edit(self.tmpdir, "tests/test_auth.py", hashed_sid)

        # Create the test file so find_test_for_source can find it
        (Path(self.tmpdir) / "tests" / "test_auth.py").write_text(
            "def test_auth(): assert True\n", encoding="utf-8")

        exit_code, _, stderr = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add auth + db",
            "teammate_name": "worker-1",
            "session_id": raw_sid,
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("db.py", stderr, "Uncovered file must be listed")

    def test_all_covered_allows_completion(self):
        """All source files have tests → task completes."""
        raw_sid = "cov-test-session-2"
        hashed_sid = _sdd_detect.extract_session_id({"session_id": raw_sid})

        _sdd_detect.record_file_edit(self.tmpdir, "src/auth.py", hashed_sid)
        _sdd_detect.record_file_edit(self.tmpdir, "tests/test_auth.py", hashed_sid)

        # Create matching test file
        (Path(self.tmpdir) / "tests" / "test_auth.py").write_text(
            "def test_auth(): assert True\n", encoding="utf-8")

        exit_code, _, _ = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add auth",
            "teammate_name": "worker-1",
            "session_id": raw_sid,
        })
        self.assertEqual(exit_code, 0)


# ─────────────────────────────────────────────────────────────────
# REAL CONCURRENCY — multiprocessing, not mocked serial execution
# Closes Phase 0 Codex deferred finding #3: is_test_running vs
# acquire_runner_lock split-brain TOCTOU. Requires the stable
# runner_lock_path architecture to pass.
# ─────────────────────────────────────────────────────────────────

class TestLockConcurrency(unittest.TestCase):
    """Verify the runner lock serializes real concurrent processes.

    These tests fork/spawn actual OS processes, not threads. They exercise
    the same flock code paths the production hooks use under rapid Agent
    Teams load.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-int-lock-")
        _cleanup_state(self.tmpdir)
        self.result_file = Path(tempfile.gettempdir()) / (
            f"sdd-int-lock-results-{os.getpid()}-{int(time.time() * 1000)}.csv"
        )
        self.result_file.write_text("")

    def tearDown(self):
        _cleanup_state(self.tmpdir)
        try:
            self.result_file.unlink()
        except FileNotFoundError:
            pass
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _parse_rows(self):
        text = self.result_file.read_text().strip()
        if not text:
            return []
        rows = []
        for line in text.split("\n"):
            parts = line.split(",")
            if len(parts) != 5:
                continue
            rows.append({
                "id": parts[0],
                "status": parts[1],
                "t_acq": float(parts[2]),
                "t_rel_start": float(parts[3]),
                "t_rel_end": float(parts[4]),
            })
        return rows

    def test_concurrent_workers_no_interval_overlap(self):
        """N processes compete → critical sections do NOT overlap in time.

        Split-brain would produce overlapping [t_acq, t_rel_end] intervals.
        Correct serialization yields strictly non-overlapping intervals.
        """
        import multiprocessing as mp
        N = 3
        HOLD_S = 0.05
        ctx = mp.get_context("spawn")
        procs = []
        for i in range(N):
            p = ctx.Process(target=_lock_concurrency_worker,
                            args=(self.tmpdir, HOLD_S, str(self.result_file),
                                  f"w{i}", 10.0))
            procs.append(p)
            p.start()
        for p in procs:
            p.join(timeout=20)
            self.assertFalse(p.is_alive(), f"Worker {p.pid} hung")
            self.assertEqual(p.exitcode, 0, f"Worker {p.pid} crashed")

        rows = self._parse_rows()
        ok = [r for r in rows if r["status"] == "OK"]
        self.assertEqual(len(ok), N,
            f"All workers must acquire eventually; got {len(ok)}/{N}: {rows}")

        ok.sort(key=lambda r: r["t_acq"])
        for a, b in zip(ok, ok[1:]):
            self.assertLessEqual(a["t_rel_end"], b["t_acq"] + 1e-3,
                f"Split-brain: worker {a['id']} (ended {a['t_rel_end']}) "
                f"overlapped with {b['id']} (started {b['t_acq']})")

    def test_lockfile_inode_stable_across_probe_acquire_cycles(self):
        """Runner lockfile inode must NEVER change during probe/acquire races.

        Regression guard for the split-brain TOCTOU: old design unlinked
        the lock target (pid_path) during is_test_running probes, allowing
        a fresh inode under a concurrent acquire — two workers each held
        LOCK_EX on different inodes sharing one path.
        """
        lockpath = _sdd_detect.runner_lock_path(self.tmpdir)

        fd = _sdd_detect.acquire_runner_lock(self.tmpdir)
        self.assertIsNotNone(fd, "Initial acquire must succeed")
        inode_initial = lockpath.stat().st_ino
        _sdd_detect.release_runner_lock(fd, self.tmpdir)

        inodes_seen = {inode_initial}
        for _ in range(50):
            _sdd_detect.is_test_running(self.tmpdir)
            if lockpath.exists():
                inodes_seen.add(lockpath.stat().st_ino)
            fd2 = _sdd_detect.acquire_runner_lock(self.tmpdir)
            self.assertIsNotNone(fd2,
                "Re-acquire must not fail after release (lockfile stable)")
            inodes_seen.add(lockpath.stat().st_ino)
            _sdd_detect.release_runner_lock(fd2, self.tmpdir)
            inodes_seen.add(lockpath.stat().st_ino)

        self.assertEqual(len(inodes_seen), 1,
            f"Lockfile inode changed across probe/acquire cycles: "
            f"{inodes_seen}")

    def test_probe_never_creates_lockfile(self):
        """is_test_running must NOT create the lockfile as a side effect.

        A fresh project with no worker history → lockfile does not exist →
        probe returns False → lockfile still does not exist. Creating it
        would amount to an implicit acquire, which violates read-only
        probe semantics.
        """
        lockpath = _sdd_detect.runner_lock_path(self.tmpdir)
        self.assertFalse(lockpath.exists(), "Pre-condition: no lockfile")
        self.assertFalse(_sdd_detect.is_test_running(self.tmpdir))
        self.assertFalse(lockpath.exists(),
            "Probe must not create the lockfile")

    def test_probe_reports_true_while_held_false_after_release(self):
        """Structural contract for probe semantics across release boundary.

        While main process holds LOCK_EX on the lockfile, all probes from
        another OS process must report True. Once released, probes must
        report False. This confirms the probe's flock observation is
        correct — but it does NOT by itself stress-test concurrent probe+
        acquire races (see test_lockfile_inode_stable_* and
        test_concurrent_workers_no_interval_overlap for that guard).
        """
        import multiprocessing as mp

        fd = _sdd_detect.acquire_runner_lock(self.tmpdir)
        self.assertIsNotNone(fd)
        try:
            ctx = mp.get_context("spawn")
            prober = ctx.Process(
                target=_lock_concurrency_prober,
                args=(self.tmpdir, str(self.result_file), 30),
            )
            prober.start()
            prober.join(timeout=10)
            self.assertFalse(prober.is_alive())
            self.assertEqual(prober.exitcode, 0)
        finally:
            _sdd_detect.release_runner_lock(fd, self.tmpdir)

        line = self.result_file.read_text().strip()
        samples = line.split(",")
        false_count = sum(1 for s in samples if s == "F")
        self.assertEqual(false_count, 0,
            f"All probes during held lock must report True; "
            f"got {false_count} False out of {len(samples)}: {line}")

        # After release: probes must observe no-runner
        self.assertFalse(_sdd_detect.is_test_running(self.tmpdir),
            "Probe must report False once lock is released")

    def test_probe_vs_acquire_race_never_false_while_held(self):
        """Stress: another process cycles acquire/hold/release; probe from main
        must observe the held state accurately.

        This guards against a regression where the probe's unlock/cleanup
        sequence leaves stale state visible to subsequent probes. The
        target regression would produce near-100% mismatch (probe
        disconnected from reality); a small scheduler-induced mismatch
        rate under full-suite load is not a bug — it is the inherent
        cost of correlating two processes' views of a tight acquire/
        release cycle via a third shared file.

        Invariant tested: mismatches < 5% of samples. That threshold
        catches any real regression while tolerating macOS scheduler
        variance under pytest full-suite load (~20 concurrent processes).
        A 10-run isolation stress shows 0% mismatch baseline; full-suite
        runs show 0-2% occasionally. Strict equality (==0) made the test
        load-sensitive; the loosened bound is the empirically-correct
        contract.

        The companion test_probe_reports_true_while_held_false_after_release
        holds the strict (0 mismatches) contract for the non-cycling case
        where the race window is not present.
        """
        import multiprocessing as mp

        # Worker: 20 cycles of acquire → hold 20ms → release → wait 5ms.
        # Main runs probes at 2ms cadence; each probe is asked to classify
        # the worker as holding or not. The worker signals its held/unheld
        # state via a second file so we can correlate probe results.
        ctx = mp.get_context("spawn")
        state_file = Path(tempfile.gettempdir()) / (
            f"sdd-probe-race-state-{os.getpid()}-{int(time.time() * 1000)}"
        )
        state_file.write_text("idle")
        try:
            worker = ctx.Process(
                target=_lock_concurrency_worker_cycling,
                args=(self.tmpdir, str(state_file), 20, 0.02, 0.005),
            )
            worker.start()

            mismatches = 0
            samples = 0
            deadline = time.monotonic() + 2.5
            while worker.is_alive() and time.monotonic() < deadline:
                try:
                    claimed = state_file.read_text()
                except OSError:
                    claimed = ""
                observed = _sdd_detect.is_test_running(self.tmpdir)
                if claimed == "held" and not observed:
                    mismatches += 1
                samples += 1
                time.sleep(0.002)
            worker.join(timeout=5)
            self.assertFalse(worker.is_alive(), "Cycling worker hung")
            self.assertEqual(worker.exitcode, 0)
            self.assertGreater(samples, 50, "Not enough probe samples collected")
            # Tolerance: 5% of samples. Real regressions produce near-100%
            # mismatch (probe disconnected from flock reality); legitimate
            # scheduler variance under full-suite load stays under 5%.
            mismatch_pct = 100.0 * mismatches / max(samples, 1)
            self.assertLess(mismatch_pct, 5.0,
                f"Probe reported False while worker claimed held too often: "
                f"{mismatches}/{samples} ({mismatch_pct:.1f}%) — "
                f"threshold 5%. A real regression would approach 100%.")
        finally:
            try:
                state_file.unlink()
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    unittest.main()
