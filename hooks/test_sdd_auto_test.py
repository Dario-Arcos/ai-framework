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
from unittest.mock import MagicMock, patch

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

    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="5 passed")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_passing_tests(self, mock_run, mock_suppress, mock_write, mock_summary, mock_pid):
        mock_pid.return_value = self.pid_file
        mock_run.return_value = subprocess.CompletedProcess(
            args="pytest", returncode=0, stdout="5 passed\n", stderr="",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        mock_write.assert_called_once_with(self.tmpdir, True, "5 passed")

    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="2 failed")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_failing_tests(self, mock_run, mock_suppress, mock_write, mock_summary, mock_pid):
        mock_pid.return_value = self.pid_file
        mock_run.return_value = subprocess.CompletedProcess(
            args="pytest", returncode=1, stdout="2 failed\n", stderr="",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        mock_write.assert_called_once_with(self.tmpdir, False, "2 failed")

    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="summary")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_output_truncation_at_8k(self, mock_run, mock_suppress, mock_write, mock_summary, mock_pid):
        mock_pid.return_value = self.pid_file
        big_output = "x" * 10000
        mock_run.return_value = subprocess.CompletedProcess(
            args="pytest", returncode=0, stdout=big_output, stderr="",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        # parse_test_summary should receive the truncated + stripped output
        call_args = mock_summary.call_args[0]
        self.assertLessEqual(len(call_args[0]), 8192)

    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="summary")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_output_no_truncation(self, mock_run, mock_suppress, mock_write, mock_summary, mock_pid):
        mock_pid.return_value = self.pid_file
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
        mock_write.assert_called_once_with(self.tmpdir, False, "tests timed out (300s)")

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

    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="ok")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch("subprocess.run")
    def test_pid_cleanup_in_finally(self, mock_run, mock_suppress, mock_write, mock_summary, mock_pid):
        mock_pid.return_value = self.pid_file
        mock_run.return_value = subprocess.CompletedProcess(
            args="pytest", returncode=0, stdout="ok", stderr="",
        )
        sdd_auto_test._run_tests_worker(self.tmpdir, "pytest")
        self.assertFalse(self.pid_file.exists(), "PID file should be cleaned up in finally block")


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
            argv=["sdd-auto-test.py", "--run-tests", "/tmp/proj", "pytest"],
        )
        mock_worker.assert_called_once_with("/tmp/proj", "pytest")

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
        mock_bg.assert_called_once_with("/tmp/proj", "pytest")

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "detect_test_command", return_value="pytest")
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value={"passing": True, "summary": "5 passed"})
    def test_previous_passing_state_feedback(self, mock_read, mock_running,
                                              mock_detect, mock_suppress, mock_bg):
        stdout, _ = self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "app/main.py"},
        })
        self.assertIn("[PASS]", stdout)

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
    def test_no_previous_state_no_output(self, mock_read, mock_detect, mock_running, mock_bg):
        stdout, _ = self._run_main(input_data={
            "cwd": "/tmp/proj",
            "tool_input": {"file_path": "app/main.py"},
        })
        self.assertEqual(stdout, "")

    @patch.object(sdd_auto_test, "run_tests_background")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "detect_test_command", return_value="pytest")
    @patch.object(sdd_auto_test, "is_test_running", return_value=False)
    @patch.object(sdd_auto_test, "read_state", return_value={"passing": True, "summary": "ok"})
    def test_output_json_structure(self, mock_read, mock_running, mock_detect,
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
        # read_state should have been called with the getcwd fallback
        mock_read.assert_called_once_with(fake_cwd)


if __name__ == "__main__":
    unittest.main()
