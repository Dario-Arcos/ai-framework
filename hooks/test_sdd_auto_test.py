#!/usr/bin/env python3
"""Tests for sdd-auto-test.py — PostToolUse hook for continuous test execution."""
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
from unittest.mock import ANY, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sdd_auto_test = importlib.import_module("sdd-auto-test")


class TestIsSourceFile(unittest.TestCase):
    """Test is_source_file() file classification."""

    def test_none_returns_false(self):
        self.assertFalse(sdd_auto_test.is_source_file(None))

    def test_empty_returns_false(self):
        self.assertFalse(sdd_auto_test.is_source_file(""))

    def test_python_file(self):
        self.assertTrue(sdd_auto_test.is_source_file("app/main.py"))

    def test_typescript_file(self):
        self.assertTrue(sdd_auto_test.is_source_file("src/Component.tsx"))

    def test_non_source_file(self):
        self.assertFalse(sdd_auto_test.is_source_file("README.md"))
        self.assertFalse(sdd_auto_test.is_source_file("config.json"))


class TestRunTestsWorker(unittest.TestCase):
    """Test _run_tests_worker() subprocess execution and state writing."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.pid_file = Path(self.tmpdir) / "test.pid"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=True)
    def test_exit_suppression_writes_failure(self, mock_suppress, mock_write):
        sdd_auto_test._run_tests_worker(self.tmpdir, "npm test || true")
        mock_write.assert_called_once_with(
            self.tmpdir, False,
            "gate command has exit code suppression — remove || true",
        )

    @patch.object(sdd_auto_test, "baseline_path")
    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="5 passed")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_passing_tests(self, mock_run, mock_suppress, mock_write, mock_summary, mock_pid, mock_bp):
        mock_pid.return_value = self.pid_file
        mock_bp.return_value = self.pid_file  # non-existent path
        mock_run.return_value = subprocess.CompletedProcess(
            args="pytest", returncode=0, stdout="5 passed\n", stderr="",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        mock_write.assert_called_once_with(
            self.tmpdir, True, "5 passed",
            raw_output=ANY, started_at=ANY,
        )

    @patch.object(sdd_auto_test, "baseline_path")
    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="2 failed")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_failing_tests(self, mock_run, mock_suppress, mock_write, mock_summary, mock_pid, mock_bp):
        mock_pid.return_value = self.pid_file
        mock_bp.return_value = self.pid_file  # non-existent path
        mock_run.return_value = subprocess.CompletedProcess(
            args="pytest", returncode=1, stdout="2 failed\n", stderr="",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        mock_write.assert_called_once_with(
            self.tmpdir, False, "2 failed",
            raw_output=ANY, started_at=ANY,
        )

    @patch.object(sdd_auto_test, "baseline_path")
    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="summary")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_output_truncation_at_8k(self, mock_run, mock_suppress, mock_write, mock_summary, mock_pid, mock_bp):
        mock_pid.return_value = self.pid_file
        mock_bp.return_value = self.pid_file
        big_output = "x" * 10000
        mock_run.return_value = subprocess.CompletedProcess(
            args="pytest", returncode=0, stdout=big_output, stderr="",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        # parse_test_summary should receive the truncated + stripped output
        call_args = mock_summary.call_args[0]
        self.assertLessEqual(len(call_args[0]), 8192)

    @patch.object(sdd_auto_test, "baseline_path")
    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="summary")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_output_no_truncation(self, mock_run, mock_suppress, mock_write, mock_summary, mock_pid, mock_bp):
        mock_pid.return_value = self.pid_file
        mock_bp.return_value = self.pid_file
        short_output = "5 passed"
        mock_run.return_value = subprocess.CompletedProcess(
            args="pytest", returncode=0, stdout=short_output, stderr="",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        call_args = mock_summary.call_args[0]
        self.assertEqual(call_args[0], short_output)

    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="pytest", timeout=300))
    def test_timeout_writes_failure(self, mock_run, mock_suppress, mock_write, mock_pid):
        mock_pid.return_value = self.pid_file
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        mock_write.assert_called_once_with(
            self.tmpdir, False, "tests timed out (300s)",
            started_at=ANY,
        )

    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run", side_effect=OSError("No such file"))
    def test_oserror_writes_failure(self, mock_run, mock_suppress, mock_write, mock_pid):
        mock_pid.return_value = self.pid_file
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        mock_write.assert_called_once()
        args = mock_write.call_args[0]
        self.assertEqual(args[0], self.tmpdir)
        self.assertFalse(args[1])
        self.assertIn("test execution error:", args[2])
        # started_at passed as kwarg
        self.assertIn("started_at", mock_write.call_args[1])

    @patch.object(sdd_auto_test, "baseline_path")
    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="ok")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_pid_cleanup_in_finally(self, mock_run, mock_suppress, mock_write, mock_summary, mock_pid, mock_bp):
        mock_pid.return_value = self.pid_file
        mock_bp.return_value = self.pid_file
        mock_run.return_value = subprocess.CompletedProcess(
            args="pytest", returncode=0, stdout="ok", stderr="",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        self.assertFalse(self.pid_file.exists(), "PID file should be cleaned up in finally block")


class TestCoalescingWorker(unittest.TestCase):
    """Test coalescing behavior: rerun marker, max reruns, project-scoped lock."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.pid_file = Path(self.tmpdir) / "test.pid"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch.object(sdd_auto_test, "baseline_path")
    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="5 passed")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_worker_reruns_when_marker_set(self, mock_run, _suppress,
                                           mock_write, _summary, mock_pid, mock_bp):
        """Worker runs twice when rerun marker exists after first run."""
        mock_pid.return_value = self.pid_file
        mock_bp.return_value = self.pid_file
        mock_run.return_value = subprocess.CompletedProcess(
            args="pytest", returncode=0, stdout="5 passed\n", stderr="",
        )
        # Simulate: marker set after clear_rerun_marker in first iteration
        call_count = [0]
        original_has = sdd_auto_test.has_rerun_marker

        def fake_has_marker(cwd):
            call_count[0] += 1
            return call_count[0] == 1  # True after first run, False after second

        with patch.object(sdd_auto_test, "has_rerun_marker", side_effect=fake_has_marker):
            sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")

        self.assertEqual(mock_run.call_count, 2, "Worker should have run tests twice")
        self.assertEqual(mock_write.call_count, 2, "State should be written twice")

    @patch.object(sdd_auto_test, "baseline_path")
    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="5 passed")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_worker_respects_max_reruns(self, mock_run, _suppress,
                                        mock_write, _summary, mock_pid, mock_bp):
        """Worker stops after _MAX_RERUNS+1 total runs even if marker keeps appearing."""
        mock_pid.return_value = self.pid_file
        mock_bp.return_value = self.pid_file
        mock_run.return_value = subprocess.CompletedProcess(
            args="pytest", returncode=0, stdout="ok\n", stderr="",
        )
        # Marker always present → should still stop at max
        with patch.object(sdd_auto_test, "has_rerun_marker", return_value=True):
            sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")

        max_runs = sdd_auto_test._MAX_RERUNS + 1
        self.assertEqual(mock_run.call_count, max_runs,
                         f"Worker should stop after {max_runs} runs")

    @patch.object(sdd_auto_test, "baseline_path")
    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="5 passed")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_worker_no_rerun_without_marker(self, mock_run, _suppress,
                                             _write, _summary, mock_pid, mock_bp):
        """Worker runs once when no rerun marker exists."""
        mock_pid.return_value = self.pid_file
        mock_bp.return_value = self.pid_file
        mock_run.return_value = subprocess.CompletedProcess(
            args="pytest", returncode=0, stdout="ok\n", stderr="",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        self.assertEqual(mock_run.call_count, 1, "Should run exactly once")

    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch("subprocess.Popen")
    def test_launcher_writes_child_pid(self, mock_popen, _running):
        """run_tests_background writes child PID from parent (closes TOCTOU)."""
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_popen.return_value = mock_proc

        from _sdd_detect import pid_path as real_pid_path
        pf = real_pid_path(self.tmpdir)

        sdd_auto_test.run_tests_background(self.tmpdir, "pytest")
        self.assertTrue(pf.exists(), "PID file should be written by parent")
        self.assertEqual(pf.read_text(), "12345")
        pf.unlink(missing_ok=True)

    @patch.object(sdd_auto_test, "is_test_running", return_value=True)
    @patch("subprocess.Popen")
    def test_launcher_skips_when_running(self, mock_popen, _running):
        """run_tests_background skips launch when runner is active."""
        sdd_auto_test.run_tests_background(self.tmpdir, "pytest")
        mock_popen.assert_not_called()

    @patch.object(sdd_auto_test, "is_test_running", return_value=True)
    def test_launcher_sets_rerun_marker_when_skipping(self, _running):
        """Skipped launch still sets rerun marker for the running worker."""
        from _sdd_detect import rerun_marker_path
        marker = rerun_marker_path(self.tmpdir)
        marker.unlink(missing_ok=True)

        sdd_auto_test.run_tests_background(self.tmpdir, "pytest")
        self.assertTrue(marker.exists(), "Rerun marker should be set even when skipping")
        marker.unlink(missing_ok=True)


class TestFormatFeedback(unittest.TestCase):
    """Test format_feedback() message formatting."""

    def test_none_returns_none(self):
        self.assertIsNone(sdd_auto_test.format_feedback(None))

    def test_passing_state(self):
        result = sdd_auto_test.format_feedback({"passing": True, "summary": "5 passed"})
        self.assertIn("[PASS]", result)
        self.assertIn("5 passed", result)

    def test_failing_state(self):
        result = sdd_auto_test.format_feedback({"passing": False, "summary": "2 failed"})
        self.assertIn("[FAIL]", result)
        self.assertIn("fix implementation", result)

    def test_missing_summary(self):
        result = sdd_auto_test.format_feedback({"passing": True})
        self.assertIn("unknown", result)


class TestMain(unittest.TestCase):
    """Test main() hook entry point."""

    def _run_main(self, input_data=None, argv=None):
        """Helper: run main() with mocked stdin/stdout/argv, return (stdout_str, exit_code)."""
        if argv:
            argv_patch = patch.object(sys, "argv", argv)
        else:
            argv_patch = patch.object(sys, "argv", ["sdd-auto-test.py"])

        stdin_text = json.dumps(input_data) if input_data is not None else ""
        stdin_patch = patch.object(sys, "stdin", io.StringIO(stdin_text))
        stdout_capture = io.StringIO()
        stdout_patch = patch.object(sys, "stdout", stdout_capture)

        exit_code = 0
        with argv_patch, stdin_patch, stdout_patch:
            try:
                sdd_auto_test.main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0

        return stdout_capture.getvalue(), exit_code

    @patch.object(sdd_auto_test, "_run_tests_worker")
    def test_worker_mode_dispatches(self, mock_worker):
        _, exit_code = self._run_main(
            argv=["sdd-auto-test.py", "--run-tests", "/tmp/proj", "pytest", ""],
        )
        mock_worker.assert_called_once_with("/tmp/proj", "pytest", None)

    def test_invalid_json_exits_0(self):
        with patch.object(sys, "stdin", io.StringIO("not json")), \
             patch.object(sys, "argv", ["sdd-auto-test.py"]):
            with self.assertRaises(SystemExit) as ctx:
                sdd_auto_test.main()
            self.assertEqual(ctx.exception.code, 0)

    @patch.object(sdd_auto_test, "read_state", return_value=None)
    def test_non_source_file_exits_0(self, mock_read):
        _, exit_code = self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "README.md"},
        })
        self.assertEqual(exit_code, 0)

    @patch.object(sdd_auto_test, "read_state", return_value=None)
    def test_no_file_path_exits_0(self, mock_read):
        _, exit_code = self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": ""},
        })
        self.assertEqual(exit_code, 0)

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "detect_test_command", return_value="pytest")
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value=None)
    def test_source_file_launches_tests(self, mock_read, mock_running, mock_detect,
                                         mock_suppress, mock_bg):
        self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "app/main.py"},
        })
        mock_bg.assert_called_once_with("/tmp/proj", "pytest", None)

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "detect_test_command", return_value="pytest")
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value={"passing": True, "summary": "5 passed"})
    @patch.object(sdd_auto_test, "read_coverage", return_value=None)
    def test_previous_passing_state_silent(self, _cov, mock_read, mock_running,
                                            mock_detect, mock_suppress, mock_bg):
        stdout, _ = self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "app/main.py"},
        })
        # Passing state = no output (silence reduces attention dilution)
        self.assertEqual(stdout, "")

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "detect_test_command", return_value="pytest")
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value={"passing": False, "summary": "2 failed"})
    def test_previous_failing_state_feedback(self, mock_read, mock_running,
                                              mock_detect, mock_suppress, mock_bg):
        stdout, _ = self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "app/main.py"},
        })
        self.assertIn("[FAIL]", stdout)

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "detect_test_command", return_value="pytest")
    @patch.object(sdd_auto_test, "is_test_running", return_value=True)
    @patch.object(sdd_auto_test, "read_state", return_value=None)
    def test_tests_running_no_launch(self, mock_read, mock_running, mock_detect, mock_bg):
        self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "app/main.py"},
        })
        mock_bg.assert_not_called()

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "detect_test_command", return_value=None)
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value=None)
    def test_no_test_command_no_launch(self, mock_read, mock_running, mock_detect, mock_bg):
        self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "app/main.py"},
        })
        mock_bg.assert_not_called()

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=True)
    @patch.object(sdd_auto_test, "detect_test_command", return_value="npm test || true")
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value=None)
    def test_exit_suppression_no_launch(self, mock_read, mock_running, mock_detect,
                                         mock_suppress, mock_bg):
        self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "app/main.py"},
        })
        mock_bg.assert_not_called()

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "detect_test_command", return_value=None)
    @patch.object(sdd_auto_test, "read_state", return_value=None)
    @patch.object(sdd_auto_test, "read_coverage", return_value=None)
    def test_no_previous_state_no_output(self, _cov, mock_read, mock_detect, mock_running, mock_bg):
        stdout, _ = self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "app/main.py"},
        })
        self.assertEqual(stdout, "")

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "detect_test_command", return_value="pytest")
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value={"passing": False, "summary": "2 failed"})
    def test_output_json_structure_on_failure(self, mock_read, mock_running, mock_detect,
                                               mock_suppress, mock_bg):
        stdout, _ = self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "app/main.py"},
        })
        data = json.loads(stdout)
        self.assertIn("hookSpecificOutput", data)
        self.assertEqual(data["hookSpecificOutput"]["hookEventName"], "PostToolUse")
        self.assertIn("additionalContext", data["hookSpecificOutput"])

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "detect_test_command", return_value=None)
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value=None)
    def test_cwd_defaults_to_getcwd(self, mock_read, mock_running, mock_detect, mock_bg):
        fake_cwd = "/tmp/fake-cwd-default"
        with patch("os.getcwd", return_value=fake_cwd):
            self._run_main(input_data={
                "tool_input": {"file_path": "app/main.py"},
            })
        # read_state should have been called with the getcwd fallback (project-scoped)
        mock_read.assert_called_once_with(fake_cwd)


class TestSddOrderingNudge(unittest.TestCase):
    """Test SDD ordering nudge in PostToolUse additionalContext."""

    def _run_main(self, input_data=None):
        stdin_text = json.dumps(input_data) if input_data is not None else ""
        stdout_capture = io.StringIO()
        exit_code = 0
        with patch.object(sys, "argv", ["sdd-auto-test.py"]), \
             patch.object(sys, "stdin", io.StringIO(stdin_text)), \
             patch.object(sys, "stdout", stdout_capture):
            try:
                sdd_auto_test.main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return stdout_capture.getvalue(), exit_code

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "detect_test_command", return_value="pytest")
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value=None)
    @patch.object(sdd_auto_test, "read_coverage", return_value={
        "source_files": ["src/a.py"], "test_files": [],
    })
    def test_nudge_when_source_no_tests(self, _cov, _state, _running,
                                         _detect, _suppress, _bg):
        """Source files edited, no test files → nudge emitted."""
        stdout, _ = self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "src/b.py"},
        })
        self.assertIn("SDD ordering", stdout)
        data = json.loads(stdout)
        self.assertIn("additionalContext", data["hookSpecificOutput"])

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "detect_test_command", return_value="pytest")
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value=None)
    @patch.object(sdd_auto_test, "read_coverage", return_value={
        "source_files": ["src/a.py"], "test_files": ["tests/test_a.py"],
    })
    def test_no_nudge_when_tests_present(self, _cov, _state, _running,
                                          _detect, _suppress, _bg):
        """Source + test files in session → no nudge."""
        stdout, _ = self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "src/b.py"},
        })
        self.assertEqual(stdout, "")

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "detect_test_command", return_value="pytest")
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value={"passing": True, "summary": "3 passed"})
    @patch.object(sdd_auto_test, "read_coverage", return_value={
        "source_files": ["src/a.py"], "test_files": [],
    })
    def test_no_nudge_when_passing(self, _cov, _state, _running,
                                    _detect, _suppress, _bg):
        """Tests passing + source-only coverage → no nudge (tests validate the code)."""
        stdout, _ = self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "src/b.py"},
        })
        self.assertEqual(stdout, "")

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "detect_test_command", return_value="pytest")
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value={"passing": False, "summary": "1 failed"})
    @patch.object(sdd_auto_test, "read_coverage", return_value={
        "source_files": ["src/a.py"], "test_files": [],
    })
    def test_failure_takes_priority_over_nudge(self, _cov, _state, _running,
                                                _detect, _suppress, _bg):
        """Test failure message takes priority over ordering nudge."""
        stdout, _ = self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "src/b.py"},
        })
        self.assertIn("[FAIL]", stdout)
        self.assertNotIn("SDD ordering", stdout)


class TestSourceExtensionsNew(unittest.TestCase):
    """Test new source file extensions (Gap 5)."""

    def test_vue_is_source(self):
        self.assertTrue(sdd_auto_test.is_source_file("app.vue"))

    def test_svelte_is_source(self):
        self.assertTrue(sdd_auto_test.is_source_file("app.svelte"))

    def test_graphql_is_source(self):
        self.assertTrue(sdd_auto_test.is_source_file("schema.graphql"))

    def test_gql_is_source(self):
        self.assertTrue(sdd_auto_test.is_source_file("query.gql"))

    def test_prisma_is_source(self):
        self.assertTrue(sdd_auto_test.is_source_file("schema.prisma"))

    def test_proto_is_source(self):
        self.assertTrue(sdd_auto_test.is_source_file("service.proto"))

    def test_sql_is_source(self):
        self.assertTrue(sdd_auto_test.is_source_file("migration.sql"))

    def test_sh_is_source(self):
        self.assertTrue(sdd_auto_test.is_source_file("deploy.sh"))

    def test_bash_is_source(self):
        self.assertTrue(sdd_auto_test.is_source_file("build.bash"))


class TestSkillTracking(unittest.TestCase):
    """Test Skill tool tracking for sop-code-assist (Gap 3)."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        # Clean up any state files
        import glob as g
        for f in g.glob(os.path.join(tempfile.gettempdir(), "sdd-skill-invoked-*.json")):
            try:
                os.unlink(f)
            except OSError:
                pass

    def _run_main(self, input_data=None, argv=None):
        if argv:
            argv_patch = patch.object(sys, "argv", argv)
        else:
            argv_patch = patch.object(sys, "argv", ["sdd-auto-test.py"])

        stdin_text = json.dumps(input_data) if input_data is not None else ""
        stdin_patch = patch.object(sys, "stdin", io.StringIO(stdin_text))
        stdout_capture = io.StringIO()
        stdout_patch = patch.object(sys, "stdout", stdout_capture)

        exit_code = 0
        with argv_patch, stdin_patch, stdout_patch:
            try:
                sdd_auto_test.main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0

        return stdout_capture.getvalue(), exit_code

    @patch.object(sdd_auto_test, "write_skill_invoked")
    def test_sop_code_assist_writes_state(self, mock_write):
        """Skill tool with sop-code-assist → state file written."""
        _, exit_code = self._run_main(input_data={
            "cwd": self.tmpdir,
            "tool_name": "Skill",
            "tool_input": {"skill": "sop-code-assist"},
        })
        self.assertEqual(exit_code, 0)
        mock_write.assert_called_once_with(self.tmpdir, "sop-code-assist", None)

    @patch.object(sdd_auto_test, "write_skill_invoked")
    def test_sop_reviewer_writes_state(self, mock_write):
        """Skill tool with sop-reviewer → state file written."""
        _, exit_code = self._run_main(input_data={
            "cwd": self.tmpdir,
            "tool_name": "Skill",
            "tool_input": {"skill": "sop-reviewer"},
        })
        self.assertEqual(exit_code, 0)
        mock_write.assert_called_once_with(self.tmpdir, "sop-reviewer", None)

    @patch.object(sdd_auto_test, "write_skill_invoked")
    def test_other_skill_no_state(self, mock_write):
        """Skill tool with brainstorming → no state file."""
        _, exit_code = self._run_main(input_data={
            "cwd": self.tmpdir,
            "tool_name": "Skill",
            "tool_input": {"skill": "brainstorming"},
        })
        self.assertEqual(exit_code, 0)
        mock_write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
