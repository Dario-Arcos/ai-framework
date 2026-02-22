#!/usr/bin/env python3
"""Tests for teammate-idle.py — TeammateIdle hook circuit breaker logic."""
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
teammate_idle = importlib.import_module("teammate-idle")


class TestLoadMaxFailures(unittest.TestCase):
    """Test load_max_failures() config extraction."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_default_value(self):
        """Nonexistent config path returns default 3."""
        result = teammate_idle.load_max_failures("/nonexistent/config.sh")
        self.assertEqual(result, 3)

    def test_custom_value(self):
        """Config with MAX_CONSECUTIVE_FAILURES=5 returns 5."""
        config = Path(self.tmpdir) / "config.sh"
        config.write_text("MAX_CONSECUTIVE_FAILURES=5\n", encoding="utf-8")
        result = teammate_idle.load_max_failures(str(config))
        self.assertEqual(result, 5)

    def test_non_numeric(self):
        """Config with non-numeric MAX_CONSECUTIVE_FAILURES returns default 3."""
        config = Path(self.tmpdir) / "config.sh"
        config.write_text("MAX_CONSECUTIVE_FAILURES=abc\n", encoding="utf-8")
        result = teammate_idle.load_max_failures(str(config))
        self.assertEqual(result, 3)

    def test_subprocess_timeout(self):
        """subprocess.run raising TimeoutExpired returns default 3."""
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("bash", 5)):
            result = teammate_idle.load_max_failures("/any/config.sh")
        self.assertEqual(result, 3)


class TestReadFailures(unittest.TestCase):
    """Test read_failures() with real filesystem fixtures."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ralph_dir = Path(self.tmpdir) / ".ralph"
        self.ralph_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_file(self):
        """No failures.json returns empty dict."""
        result = teammate_idle.read_failures(self.ralph_dir)
        self.assertEqual(result, {})

    def test_valid_json(self):
        """Valid failures.json with fresh _updated_at returns parsed dict."""
        import time
        fresh_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        failures_path = self.ralph_dir / "failures.json"
        failures_path.write_text(
            json.dumps({"worker-1": 3, "_updated_at": fresh_ts}),
            encoding="utf-8",
        )
        result = teammate_idle.read_failures(self.ralph_dir)
        self.assertEqual(result.get("worker-1"), 3)

    def test_corrupt_json(self):
        """Corrupt JSON content returns empty dict."""
        failures_path = self.ralph_dir / "failures.json"
        failures_path.write_text("{not valid json!!", encoding="utf-8")
        result = teammate_idle.read_failures(self.ralph_dir)
        self.assertEqual(result, {})


class TestMain(unittest.TestCase):
    """Test main() end-to-end with mocked stdin and filesystem."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_invalid_json_exits_0(self):
        """Bad stdin JSON causes exit 0."""
        with patch("sys.stdin", io.StringIO("not json")):
            with self.assertRaises(SystemExit) as cm:
                teammate_idle.main()
        self.assertEqual(cm.exception.code, 0)

    def test_non_ralph_exits_0(self):
        """No .ralph/config.sh causes exit 0."""
        stdin_data = json.dumps({"cwd": self.tmpdir, "teammate_name": "worker-1"})
        with patch("sys.stdin", io.StringIO(stdin_data)):
            with self.assertRaises(SystemExit) as cm:
                teammate_idle.main()
        self.assertEqual(cm.exception.code, 0)

    def test_abort_file_exits_0(self):
        """ABORT file present causes exit 0."""
        ralph_dir = Path(self.tmpdir) / ".ralph"
        ralph_dir.mkdir()
        (ralph_dir / "config.sh").write_text("", encoding="utf-8")
        (ralph_dir / "ABORT").write_text("", encoding="utf-8")
        stdin_data = json.dumps({"cwd": self.tmpdir, "teammate_name": "worker-1"})
        with patch("sys.stdin", io.StringIO(stdin_data)):
            with self.assertRaises(SystemExit) as cm:
                teammate_idle.main()
        self.assertEqual(cm.exception.code, 0)

    def test_below_max_failures_exits_0(self):
        """Failures below max causes exit 0 without circuit breaker."""
        import time
        ralph_dir = Path(self.tmpdir) / ".ralph"
        ralph_dir.mkdir()
        (ralph_dir / "config.sh").write_text("", encoding="utf-8")
        fresh_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (ralph_dir / "failures.json").write_text(
            json.dumps({"worker-1": 1, "_updated_at": fresh_ts}),
            encoding="utf-8",
        )
        stdin_data = json.dumps({"cwd": self.tmpdir, "teammate_name": "worker-1"})
        with patch("sys.stdin", io.StringIO(stdin_data)):
            with self.assertRaises(SystemExit) as cm:
                teammate_idle.main()
        self.assertEqual(cm.exception.code, 0)

    def test_circuit_breaker_prints_stderr(self):
        """Failures >= max prints circuit breaker warning to stderr and exits 0."""
        import time
        ralph_dir = Path(self.tmpdir) / ".ralph"
        ralph_dir.mkdir()
        (ralph_dir / "config.sh").write_text("", encoding="utf-8")
        fresh_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (ralph_dir / "failures.json").write_text(
            json.dumps({"worker-1": 3, "_updated_at": fresh_ts}),
            encoding="utf-8",
        )
        stdin_data = json.dumps({"cwd": self.tmpdir, "teammate_name": "worker-1"})
        with patch("sys.stdin", io.StringIO(stdin_data)):
            with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as cm:
                    teammate_idle.main()
        self.assertEqual(cm.exception.code, 0)
        stderr_output = mock_stderr.getvalue()
        self.assertIn("Circuit breaker", stderr_output)
        self.assertIn("worker-1", stderr_output)
        self.assertIn("3", stderr_output)


# ─────────────────────────────────────────────────────────────────
# Bug #4: Stale failures.json from previous orchestration run
# ─────────────────────────────────────────────────────────────────

class TestStaleFailures(unittest.TestCase):
    """Failures from a previous run must NOT trigger circuit breaker in a new run."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ralph_dir = Path(self.tmpdir) / ".ralph"
        self.ralph_dir.mkdir()
        (self.ralph_dir / "config.sh").write_text("", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_stale_failures_ignored(self):
        """failures.json with stale _updated_at must be ignored (not circuit-break)."""
        import time
        stale_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 10800))  # 3h ago
        (self.ralph_dir / "failures.json").write_text(
            json.dumps({"worker-1": 5, "_updated_at": stale_ts}),
            encoding="utf-8",
        )
        stdin_data = json.dumps({"cwd": self.tmpdir, "teammate_name": "worker-1"})
        with patch("sys.stdin", io.StringIO(stdin_data)):
            with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as cm:
                    teammate_idle.main()
        self.assertEqual(cm.exception.code, 0)
        # Should NOT contain circuit breaker message — stale failures ignored
        self.assertNotIn("Circuit breaker", mock_stderr.getvalue())

    def test_fresh_failures_still_trigger(self):
        """failures.json with fresh _updated_at still triggers circuit breaker."""
        import time
        fresh_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (self.ralph_dir / "failures.json").write_text(
            json.dumps({"worker-1": 3, "_updated_at": fresh_ts}),
            encoding="utf-8",
        )
        stdin_data = json.dumps({"cwd": self.tmpdir, "teammate_name": "worker-1"})
        with patch("sys.stdin", io.StringIO(stdin_data)):
            with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as cm:
                    teammate_idle.main()
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("Circuit breaker", mock_stderr.getvalue())

    def test_no_updated_at_treated_as_stale(self):
        """Legacy failures.json without _updated_at field treated as stale (safe default)."""
        (self.ralph_dir / "failures.json").write_text(
            json.dumps({"worker-1": 5}),
            encoding="utf-8",
        )
        stdin_data = json.dumps({"cwd": self.tmpdir, "teammate_name": "worker-1"})
        with patch("sys.stdin", io.StringIO(stdin_data)):
            with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as cm:
                    teammate_idle.main()
        self.assertEqual(cm.exception.code, 0)
        self.assertNotIn("Circuit breaker", mock_stderr.getvalue())


# ─────────────────────────────────────────────────────────────────
# Bug #5: ABORT file exits silently — no diagnostic output
# ─────────────────────────────────────────────────────────────────

class TestAbortWarning(unittest.TestCase):
    """ABORT file must produce a warning in stderr, not exit silently."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ralph_dir = Path(self.tmpdir) / ".ralph"
        self.ralph_dir.mkdir()
        (self.ralph_dir / "config.sh").write_text("", encoding="utf-8")
        (self.ralph_dir / "ABORT").write_text("", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_abort_prints_warning_to_stderr(self):
        """ABORT file must print a warning to stderr before exiting."""
        stdin_data = json.dumps({"cwd": self.tmpdir, "teammate_name": "worker-1"})
        with patch("sys.stdin", io.StringIO(stdin_data)):
            with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as cm:
                    teammate_idle.main()
        self.assertEqual(cm.exception.code, 0)
        stderr_output = mock_stderr.getvalue()
        self.assertIn("ABORT", stderr_output)
        self.assertTrue(len(stderr_output) > 0, "stderr must not be empty")


if __name__ == "__main__":
    unittest.main()
