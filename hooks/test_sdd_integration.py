#!/usr/bin/env python3
"""Integration tests — SDD test mechanism end-to-end.

Verifies the REAL MECHANISM works during coding:
  1. sdd-auto-test.py worker runs actual tests, writes shared state
  2. sdd-test-guard.py reads that state, blocks reward hacking
  3. task-completed.py reads that state, gates task completion
  4. Full cycle: edit → test → feedback → guard → complete

These tests create real mini-projects with real test files, execute
real pytest processes, and verify the hooks communicate correctly via
/tmp/ state files.

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
    """Run a hook's main() with JSON stdin, capture stdout/stderr and exit code."""
    stdin_mock = io.StringIO(json.dumps(input_data))
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    exit_code = 0

    with patch("sys.stdin", stdin_mock), \
         patch("sys.stdout", stdout_capture), \
         patch("sys.stderr", stderr_capture):
        try:
            hook_main()
        except SystemExit as e:
            exit_code = e.code if e.code is not None else 0

    return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()


def _cleanup_state(cwd):
    """Remove /tmp/ state and PID files for a project directory."""
    h = _sdd_detect.project_hash(cwd)
    for pattern in [f"/tmp/sdd-test-state-{h}.json",
                    f"/tmp/sdd-test-run-{h}.pid",
                    f"/tmp/sdd-test-lock-{h}"]:
        try:
            os.unlink(pattern)
        except FileNotFoundError:
            pass


# ─────────────────────────────────────────────────────────────────
# 1. SHARED STATE COMMUNICATION
# ─────────────────────────────────────────────────────────────────

class TestSharedStateCommunication(unittest.TestCase):
    """Verify hooks communicate via the same /tmp/ state file."""

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

    def test_pid_file_cleaned_after_execution(self):
        """PID file is created during execution and cleaned after."""
        _create_mini_project(self.tmpdir,
            app_code="x = 1\n",
            test_code="def test_true(): assert True\n",
        )
        pid_file = _sdd_detect.pid_path(self.tmpdir)

        self.assertFalse(pid_file.exists())
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        self.assertFalse(pid_file.exists(), "PID file should be cleaned up")

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

        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "tests/test_app.py",
                "old_string": "assert add(1, 2) == 3\nassert add(0, 0) == 0",
                "new_string": "assert add(1, 2) == 3",  # dropped an assertion
            },
        })
        self.assertEqual(exit_code, 0)
        output = json.loads(stdout)
        decision = output["hookSpecificOutput"]["permissionDecision"]
        self.assertEqual(decision, "deny")
        self.assertIn("reward hacking", output["hookSpecificOutput"]["permissionDecisionReason"])

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

    @patch.object(sdd_auto_test, "run_tests_background")
    def test_passing_state_silent(self, mock_bg):
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

    @patch.object(sdd_auto_test, "run_tests_background")
    def test_no_feedback_when_no_state(self, mock_bg):
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
        """If tests are already running (PID exists), skip launching new ones."""
        pid_file = _sdd_detect.pid_path(self.tmpdir)
        pid_file.write_text(str(os.getpid()))
        try:
            exit_code, stdout, _ = _run_hook_stdin(sdd_auto_test.main, {
                "cwd": self.tmpdir,
                "tool_input": {"file_path": "app.py"},
            })
            mock_bg.assert_not_called()
        finally:
            pid_file.unlink(missing_ok=True)


# ─────────────────────────────────────────────────────────────────
# 5. TASK-COMPLETED READS STATE (NON-RALPH)
# ─────────────────────────────────────────────────────────────────

class TestTaskCompletedReadsState(unittest.TestCase):
    """Verify task-completed reads auto-test state for non-ralph projects."""

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

    def test_passing_state_allows_completion(self):
        """Tests passing → task completion allowed (exit 0)."""
        _sdd_detect.write_state(self.tmpdir, True, "3 passed")

        exit_code, _, _ = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 0)

    def test_failing_state_blocks_completion(self):
        """Tests failing → task completion blocked (exit 2)."""
        _sdd_detect.write_state(self.tmpdir, False, "1 failed")

        exit_code, _, stderr = _run_hook_stdin(task_completed.main, {
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("failed", stderr.lower())

    def test_no_state_runs_fresh_tests(self):
        """No auto-test state → runs fresh tests → writes state → gates."""
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

        # State should now exist (written by the fresh run)
        state = _sdd_detect.read_state(self.tmpdir)
        self.assertIsNotNone(state)
        self.assertTrue(state["passing"])

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
        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
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
        output = json.loads(stdout)
        self.assertEqual(
            output["hookSpecificOutput"]["permissionDecision"], "deny",
            "Guard MUST deny removing assertions when tests fail"
        )

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
        with patch.object(sdd_auto_test, "run_tests_background"):
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
        with patch.object(sdd_auto_test, "run_tests_background"):
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
            "def test_a(): assert True\n"
            "def test_b(): assert True\n"
            "def test_c(): assert True\n",
            encoding="utf-8",
        )
        _sdd_detect.write_state(self.tmpdir, False, "1 failed")

        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(test_file),
                "content": "def test_a(): assert True\n",
            },
        })
        output = json.loads(stdout)
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_write_tool_new_test_file_allowed(self):
        """Write tool creating new test file → allow (file didn't exist before)."""
        _sdd_detect.write_state(self.tmpdir, False, "1 failed")

        new_file = Path(self.tmpdir) / "tests" / "test_new.py"
        exit_code, stdout, _ = _run_hook_stdin(sdd_test_guard.main, {
            "cwd": self.tmpdir,
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(new_file),
                "content": "def test_new(): assert True\n",
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
        """All gates passing → task completes + metrics updated."""
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

        metrics = json.loads((self.ralph_dir / "metrics.json").read_text())
        self.assertEqual(metrics["total_tasks"], 1)
        self.assertEqual(metrics.get("successful_tasks", 0), 1)

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


if __name__ == "__main__":
    unittest.main()
