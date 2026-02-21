#!/usr/bin/env python3
"""Tests for task-completed.py — TaskCompleted hook quality gates and failure tracking."""
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
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
task_completed = importlib.import_module("task-completed")


# ─────────────────────────────────────────────────────────────────
# TestLoadConfig
# ─────────────────────────────────────────────────────────────────

class TestLoadConfig(unittest.TestCase):
    """Test load_config() with real config files."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_file_returns_defaults(self):
        config = task_completed.load_config(Path(self.tmpdir) / "nonexistent.sh")
        self.assertEqual(config, task_completed.CONFIG_DEFAULTS)

    def test_valid_config_overrides(self):
        cfg = Path(self.tmpdir) / "config.sh"
        cfg.write_text('GATE_TEST="pytest"\n', encoding="utf-8")
        config = task_completed.load_config(cfg)
        self.assertEqual(config["GATE_TEST"], "pytest")
        # Other keys keep defaults
        self.assertEqual(config["GATE_BUILD"], task_completed.CONFIG_DEFAULTS["GATE_BUILD"])

    def test_partial_config(self):
        cfg = Path(self.tmpdir) / "config.sh"
        cfg.write_text('GATE_LINT="eslint ."\nGATE_BUILD=""\n', encoding="utf-8")
        config = task_completed.load_config(cfg)
        self.assertEqual(config["GATE_LINT"], "eslint .")
        self.assertEqual(config["GATE_BUILD"], "")
        self.assertEqual(config["GATE_TEST"], task_completed.CONFIG_DEFAULTS["GATE_TEST"])

    def test_empty_values_preserved(self):
        cfg = Path(self.tmpdir) / "config.sh"
        cfg.write_text('GATE_LINT=""\n', encoding="utf-8")
        config = task_completed.load_config(cfg)
        self.assertEqual(config["GATE_LINT"], "")

    def test_subprocess_timeout_returns_defaults(self):
        cfg = Path(self.tmpdir) / "config.sh"
        cfg.write_text('GATE_TEST="pytest"\n', encoding="utf-8")
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="bash", timeout=5)):
            config = task_completed.load_config(cfg)
        self.assertEqual(config, task_completed.CONFIG_DEFAULTS)


# ─────────────────────────────────────────────────────────────────
# TestAtomicUpdateFailures
# ─────────────────────────────────────────────────────────────────

class TestAtomicUpdateFailures(unittest.TestCase):
    """Test _atomic_update_failures() with real filesystem."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ralph_dir = Path(self.tmpdir) / ".ralph"
        self.ralph_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_increment_new_file(self):
        count = task_completed._atomic_update_failures(self.ralph_dir, "agent-1", "increment")
        self.assertEqual(count, 1)
        data = json.loads((self.ralph_dir / "failures.json").read_text())
        self.assertEqual(data["agent-1"], 1)

    def test_increment_existing(self):
        (self.ralph_dir / "failures.json").write_text(
            json.dumps({"agent-1": 2}), encoding="utf-8"
        )
        count = task_completed._atomic_update_failures(self.ralph_dir, "agent-1", "increment")
        self.assertEqual(count, 3)

    def test_increment_new_teammate(self):
        (self.ralph_dir / "failures.json").write_text(
            json.dumps({"agent-1": 2}), encoding="utf-8"
        )
        count = task_completed._atomic_update_failures(self.ralph_dir, "agent-2", "increment")
        self.assertEqual(count, 1)
        data = json.loads((self.ralph_dir / "failures.json").read_text())
        self.assertEqual(data["agent-1"], 2)
        self.assertEqual(data["agent-2"], 1)

    def test_reset(self):
        (self.ralph_dir / "failures.json").write_text(
            json.dumps({"agent-1": 5}), encoding="utf-8"
        )
        count = task_completed._atomic_update_failures(self.ralph_dir, "agent-1", "reset")
        self.assertEqual(count, 0)

    def test_corrupt_json_recovers(self):
        (self.ralph_dir / "failures.json").write_text("not valid json{{{", encoding="utf-8")
        count = task_completed._atomic_update_failures(self.ralph_dir, "agent-1", "increment")
        self.assertEqual(count, 1)

    def test_creates_parent_dir(self):
        nested = Path(self.tmpdir) / "deep" / "nested" / ".ralph"
        count = task_completed._atomic_update_failures(nested, "agent-1", "increment")
        self.assertEqual(count, 1)
        self.assertTrue((nested / "failures.json").exists())


# ─────────────────────────────────────────────────────────────────
# TestUpdateMetrics
# ─────────────────────────────────────────────────────────────────

class TestUpdateMetrics(unittest.TestCase):
    """Test update_metrics() with real filesystem."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ralph_dir = Path(self.tmpdir) / ".ralph"
        self.ralph_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _read_metrics(self):
        return json.loads((self.ralph_dir / "metrics.json").read_text())

    def test_success_new_file(self):
        task_completed.update_metrics(self.ralph_dir, success=True, teammate_name="agent-1")
        m = self._read_metrics()
        self.assertEqual(m["total_tasks"], 1)
        self.assertEqual(m["successful_tasks"], 1)
        self.assertNotIn("failed_tasks", m)

    def test_failure_new_file(self):
        task_completed.update_metrics(self.ralph_dir, success=False, teammate_name="agent-1")
        m = self._read_metrics()
        self.assertEqual(m["total_tasks"], 1)
        self.assertEqual(m["failed_tasks"], 1)
        self.assertNotIn("successful_tasks", m)

    def test_increments_existing(self):
        task_completed.update_metrics(self.ralph_dir, success=True, teammate_name="agent-1")
        task_completed.update_metrics(self.ralph_dir, success=True, teammate_name="agent-1")
        task_completed.update_metrics(self.ralph_dir, success=False, teammate_name="agent-1")
        m = self._read_metrics()
        self.assertEqual(m["total_tasks"], 3)
        self.assertEqual(m["successful_tasks"], 2)
        self.assertEqual(m["failed_tasks"], 1)
        self.assertEqual(m["per_teammate"]["agent-1"]["completed"], 2)
        self.assertEqual(m["per_teammate"]["agent-1"]["failed"], 1)

    def test_last_updated_set(self):
        task_completed.update_metrics(self.ralph_dir, success=True, teammate_name="agent-1")
        m = self._read_metrics()
        self.assertIn("last_updated", m)
        # Verify ISO format: YYYY-MM-DDTHH:MM:SSZ
        self.assertRegex(m["last_updated"], r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")

    def test_corrupt_json_recovers(self):
        (self.ralph_dir / "metrics.json").write_text("{bad json!!!", encoding="utf-8")
        task_completed.update_metrics(self.ralph_dir, success=True, teammate_name="agent-1")
        m = self._read_metrics()
        self.assertEqual(m["total_tasks"], 1)


# ─────────────────────────────────────────────────────────────────
# TestRunGate
# ─────────────────────────────────────────────────────────────────

class TestRunGate(unittest.TestCase):
    """Test run_gate() with mocked subprocess."""

    def test_empty_command_passes(self):
        passed, output = task_completed.run_gate("test", "", "/tmp")
        self.assertTrue(passed)
        self.assertEqual(output, "")

    def test_exit_suppression_fails(self):
        passed, output = task_completed.run_gate("test", "npm test || true", "/tmp")
        self.assertFalse(passed)
        self.assertIn("exit code suppression", output)

    @patch("subprocess.run")
    def test_passing_command(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args="npm test", returncode=0, stdout="5 passed\n", stderr=""
        )
        passed, output = task_completed.run_gate("test", "npm test", "/tmp")
        self.assertTrue(passed)
        self.assertIn("5 passed", output)

    @patch("subprocess.run")
    def test_failing_command(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args="npm test", returncode=1, stdout="", stderr="FAIL src/app.test.js\n"
        )
        passed, output = task_completed.run_gate("test", "npm test", "/tmp")
        self.assertFalse(passed)
        self.assertIn("FAIL", output)

    @patch("subprocess.run")
    def test_output_truncation(self, mock_run):
        long_output = "x" * 1200
        mock_run.return_value = subprocess.CompletedProcess(
            args="npm test", returncode=0, stdout=long_output, stderr=""
        )
        passed, output = task_completed.run_gate("test", "npm test", "/tmp")
        self.assertTrue(passed)
        self.assertTrue(output.startswith("...\n"))
        self.assertEqual(len(output), 800 + len("...\n"))

    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="npm test", timeout=120))
    def test_timeout(self, _mock):
        passed, output = task_completed.run_gate("test", "npm test", "/tmp")
        self.assertFalse(passed)
        self.assertIn("timed out", output)

    @patch("subprocess.run", side_effect=OSError("No such file"))
    def test_oserror(self, _mock):
        passed, output = task_completed.run_gate("test", "npm test", "/tmp")
        self.assertFalse(passed)
        self.assertIn("failed to execute", output)


# ─────────────────────────────────────────────────────────────────
# TestExtractCoveragePct
# ─────────────────────────────────────────────────────────────────

class TestExtractCoveragePct(unittest.TestCase):
    """Test extract_coverage_pct() pattern matching."""

    def test_jest_format(self):
        output = "All files | 85.71 | 80.00 | 90.00 | 85.71"
        self.assertAlmostEqual(task_completed.extract_coverage_pct(output), 85.71)

    def test_istanbul_format(self):
        output = "Statements : 85.71%"
        self.assertAlmostEqual(task_completed.extract_coverage_pct(output), 85.71)

    def test_pytest_cov_format(self):
        output = "TOTAL    100    15    85%"
        self.assertAlmostEqual(task_completed.extract_coverage_pct(output), 85.0)

    def test_go_format(self):
        output = "coverage: 85.0% of statements"
        self.assertAlmostEqual(task_completed.extract_coverage_pct(output), 85.0)

    def test_generic_format(self):
        output = "Total coverage: 90.5%"
        self.assertAlmostEqual(task_completed.extract_coverage_pct(output), 90.5)

    def test_no_match_returns_none(self):
        self.assertIsNone(task_completed.extract_coverage_pct("no coverage info here"))


# ─────────────────────────────────────────────────────────────────
# TestFindScenarioStrategy
# ─────────────────────────────────────────────────────────────────

class TestFindScenarioStrategy(unittest.TestCase):
    """Test find_scenario_strategy() detection from description and files."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_from_description_not_applicable(self):
        result = task_completed.find_scenario_strategy(
            self.tmpdir, "Fix typo", "Scenario-Strategy: not-applicable\nJust a typo fix"
        )
        self.assertEqual(result, "not-applicable")

    def test_from_description_required(self):
        result = task_completed.find_scenario_strategy(
            self.tmpdir, "Add auth", "Scenario-Strategy: required\nMust have tests"
        )
        self.assertEqual(result, "required")

    def test_no_description_no_files(self):
        result = task_completed.find_scenario_strategy(self.tmpdir, "Some task", "")
        self.assertEqual(result, "required")

    def test_from_file_not_applicable(self):
        task_file = Path(self.tmpdir) / "sprint.code-task.md"
        task_file.write_text(
            "# Task: Fix typo\nScenario-Strategy: not-applicable\nJust fix the typo.\n",
            encoding="utf-8",
        )
        result = task_completed.find_scenario_strategy(self.tmpdir, "Fix typo", "")
        self.assertEqual(result, "not-applicable")

    def test_from_file_no_strategy_line(self):
        task_file = Path(self.tmpdir) / "sprint.code-task.md"
        task_file.write_text(
            "# Task: Add feature\nImplement the feature.\n",
            encoding="utf-8",
        )
        result = task_completed.find_scenario_strategy(self.tmpdir, "Add feature", "")
        self.assertEqual(result, "required")

    def test_description_takes_priority(self):
        task_file = Path(self.tmpdir) / "sprint.code-task.md"
        task_file.write_text(
            "# Task: Mixed task\nScenario-Strategy: required\nNeeds tests.\n",
            encoding="utf-8",
        )
        result = task_completed.find_scenario_strategy(
            self.tmpdir, "Mixed task",
            "Scenario-Strategy: not-applicable\nOverride from description"
        )
        self.assertEqual(result, "not-applicable")

    def test_html_comment_not_applicable_in_description(self):
        """Template renders <!-- required | not-applicable --> — must strip comment."""
        result = task_completed.find_scenario_strategy(
            self.tmpdir, "Add feature",
            "- **Scenario-Strategy**: required <!-- required | not-applicable -->\nDetails"
        )
        self.assertEqual(result, "required")

    def test_html_comment_not_applicable_in_file(self):
        task_file = Path(self.tmpdir) / "sprint.code-task.md"
        task_file.write_text(
            "# Task: Add feature\n"
            "- **Scenario-Strategy**: required <!-- required | not-applicable -->\n",
            encoding="utf-8",
        )
        result = task_completed.find_scenario_strategy(self.tmpdir, "Add feature", "")
        self.assertEqual(result, "required")

    def test_html_comment_actual_not_applicable(self):
        """When value IS not-applicable, comment should not interfere."""
        result = task_completed.find_scenario_strategy(
            self.tmpdir, "Fix typo",
            "- **Scenario-Strategy**: not-applicable <!-- required | not-applicable -->\nJust a fix"
        )
        self.assertEqual(result, "not-applicable")


# ─────────────────────────────────────────────────────────────────
# TestFailTask
# ─────────────────────────────────────────────────────────────────

class TestFailTask(unittest.TestCase):
    """Test _fail_task() exit behavior and stderr output."""

    def test_exits_2(self):
        with self.assertRaises(SystemExit) as ctx:
            task_completed._fail_task("Header", "Body")
        self.assertEqual(ctx.exception.code, 2)

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_stderr_format(self, mock_stderr):
        with self.assertRaises(SystemExit):
            task_completed._fail_task("HEADER", "BODY")
        output = mock_stderr.getvalue()
        self.assertIn("HEADER", output)
        self.assertIn("BODY", output)
        self.assertIn("Fix the issue before completing this task.", output)

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_custom_footer(self, mock_stderr):
        with self.assertRaises(SystemExit):
            task_completed._fail_task("H", "B", "Custom footer message.")
        output = mock_stderr.getvalue()
        self.assertIn("Custom footer message.", output)
        self.assertNotIn("Fix the issue before completing this task.", output)


# ─────────────────────────────────────────────────────────────────
# TestHandleNonRalphCompletion
# ─────────────────────────────────────────────────────────────────

class TestHandleNonRalphCompletion(unittest.TestCase):
    """Test _handle_non_ralph_completion() with mocked SDD functions."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch.object(task_completed, "detect_test_command", return_value=None)
    def test_no_test_command_allows(self, _mock):
        # Should return without exit
        task_completed._handle_non_ralph_completion(self.tmpdir, "my task")

    @patch.object(task_completed, "is_test_running", return_value=False)
    @patch.object(task_completed, "read_state", return_value={"passing": True, "summary": "ok"})
    @patch.object(task_completed, "detect_test_command", return_value="npm test")
    def test_state_passing_allows(self, *_mocks):
        task_completed._handle_non_ralph_completion(self.tmpdir, "my task")

    @patch.object(task_completed, "is_test_running", return_value=False)
    @patch.object(task_completed, "read_state", return_value={"passing": False, "summary": "2 failed"})
    @patch.object(task_completed, "detect_test_command", return_value="npm test")
    def test_state_failing_exits_2(self, *_mocks):
        with self.assertRaises(SystemExit) as ctx:
            task_completed._handle_non_ralph_completion(self.tmpdir, "my task")
        self.assertEqual(ctx.exception.code, 2)

    @patch.object(task_completed, "write_state")
    @patch.object(task_completed, "parse_test_summary", return_value="5 passed")
    @patch.object(task_completed, "run_gate", return_value=(True, "5 passed"))
    @patch.object(task_completed, "read_state", side_effect=[None, None])
    @patch.object(task_completed, "is_test_running", side_effect=[True, False])
    @patch.object(task_completed, "detect_test_command", return_value="npm test")
    @patch("time.sleep")
    @patch("time.monotonic", side_effect=[0, 1, 2])
    def test_waits_for_running_autotest(self, *_mocks):
        task_completed._handle_non_ralph_completion(self.tmpdir, "my task")

    @patch.object(task_completed, "write_state")
    @patch.object(task_completed, "parse_test_summary", return_value="5 passed")
    @patch.object(task_completed, "run_gate", return_value=(True, "5 passed"))
    @patch.object(task_completed, "read_state", return_value=None)
    @patch.object(task_completed, "is_test_running", return_value=False)
    @patch.object(task_completed, "detect_test_command", return_value="npm test")
    def test_no_state_fresh_run_pass(self, *_mocks):
        task_completed._handle_non_ralph_completion(self.tmpdir, "my task")

    @patch.object(task_completed, "write_state")
    @patch.object(task_completed, "parse_test_summary", return_value="tests failed")
    @patch.object(task_completed, "run_gate", return_value=(False, "FAIL src/app.test.js"))
    @patch.object(task_completed, "read_state", return_value=None)
    @patch.object(task_completed, "is_test_running", return_value=False)
    @patch.object(task_completed, "detect_test_command", return_value="npm test")
    def test_no_state_fresh_run_fail(self, *_mocks):
        with self.assertRaises(SystemExit) as ctx:
            task_completed._handle_non_ralph_completion(self.tmpdir, "my task")
        self.assertEqual(ctx.exception.code, 2)

    @patch.object(task_completed, "is_test_running", return_value=False)
    @patch.object(task_completed, "detect_test_command", return_value="npm test")
    def test_lock_double_check_passing(self, *_mocks):
        """After acquiring lock, state appeared passing from another teammate."""
        # First read_state returns None (before lock), second returns passing (after lock)
        with patch.object(task_completed, "read_state", side_effect=[None, {"passing": True, "summary": "ok"}]):
            task_completed._handle_non_ralph_completion(self.tmpdir, "my task")

    @patch.object(task_completed, "is_test_running", return_value=False)
    @patch.object(task_completed, "detect_test_command", return_value="npm test")
    def test_lock_double_check_failing(self, *_mocks):
        """After acquiring lock, state appeared failing from another teammate."""
        with patch.object(task_completed, "read_state", side_effect=[None, {"passing": False, "summary": "1 failed"}]):
            with self.assertRaises(SystemExit) as ctx:
                task_completed._handle_non_ralph_completion(self.tmpdir, "my task")
            self.assertEqual(ctx.exception.code, 2)


# ─────────────────────────────────────────────────────────────────
# TestMainRalph
# ─────────────────────────────────────────────────────────────────

class TestMainRalph(unittest.TestCase):
    """Test main() entry point with ralph and non-ralph scenarios."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ralph_dir = Path(self.tmpdir) / ".ralph"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_ralph_project(self, config_content=""):
        """Create .ralph/config.sh with given content."""
        self.ralph_dir.mkdir(parents=True, exist_ok=True)
        (self.ralph_dir / "config.sh").write_text(config_content, encoding="utf-8")

    def _make_stdin(self, data):
        """Return a StringIO with JSON data for sys.stdin."""
        return io.StringIO(json.dumps(data))

    def _default_input(self, **overrides):
        """Build default stdin JSON payload."""
        base = {
            "cwd": self.tmpdir,
            "task_subject": "Implement feature X",
            "task_description": "",
            "teammate_name": "agent-1",
        }
        base.update(overrides)
        return base

    def test_invalid_json_exits_0(self):
        with patch("sys.stdin", io.StringIO("not json at all{")):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)

    @patch.object(task_completed, "_handle_non_ralph_completion")
    def test_non_ralph_delegates(self, mock_handler):
        """No .ralph/config.sh → delegates to _handle_non_ralph_completion."""
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)
        mock_handler.assert_called_once()

    @patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-code-assist"})
    @patch.object(task_completed, "run_gate", return_value=(True, "ok"))
    @patch.object(task_completed, "find_scenario_strategy", return_value="required")
    def test_all_gates_pass(self, _mock_strategy, _mock_gate, _mock_skill):
        self._make_ralph_project(
            'GATE_TEST="npm test"\nGATE_TYPECHECK="tsc"\nGATE_LINT="eslint"\nGATE_BUILD="npm run build"\n'
        )
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)
        # Verify failures were reset and metrics updated
        failures_file = self.ralph_dir / "failures.json"
        if failures_file.exists():
            data = json.loads(failures_file.read_text())
            self.assertEqual(data.get("agent-1", 0), 0)
        metrics_file = self.ralph_dir / "metrics.json"
        self.assertTrue(metrics_file.exists())
        metrics = json.loads(metrics_file.read_text())
        self.assertEqual(metrics["successful_tasks"], 1)

    @patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-code-assist"})
    @patch.object(task_completed, "find_scenario_strategy", return_value="required")
    def test_gate_fails(self, _mock_strategy, _mock_skill):
        self._make_ralph_project('GATE_TEST="npm test"\n')
        with patch.object(task_completed, "run_gate", return_value=(False, "FAIL: 2 tests")):
            with patch("sys.stdin", self._make_stdin(self._default_input())):
                with self.assertRaises(SystemExit) as ctx:
                    task_completed.main()
                self.assertEqual(ctx.exception.code, 2)
        # Failures incremented
        data = json.loads((self.ralph_dir / "failures.json").read_text())
        self.assertEqual(data["agent-1"], 1)

    @patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-code-assist"})
    @patch.object(task_completed, "run_gate", return_value=(True, "ok"))
    @patch.object(task_completed, "find_scenario_strategy", return_value="required")
    def test_empty_gate_skipped(self, _mock_strategy, mock_gate, _mock_skill):
        self._make_ralph_project('GATE_TEST="npm test"\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n')
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)
        # run_gate called for GATE_TEST only (empty gates skipped by main loop)
        # Note: run_gate handles empty command internally too, but the main loop
        # skips empty gate_cmd before calling run_gate
        calls = mock_gate.call_args_list
        gate_names = [c[0][0] for c in calls]
        self.assertIn("test", gate_names)
        # Empty gates should not appear since main loop skips them
        for name in gate_names:
            self.assertNotEqual(name, "typecheck")
            self.assertNotEqual(name, "lint")
            self.assertNotEqual(name, "build")

    @patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-code-assist"})
    @patch.object(task_completed, "run_gate", return_value=(True, "ok"))
    @patch.object(task_completed, "find_scenario_strategy", return_value="not-applicable")
    def test_not_applicable_skips_test_gate(self, _mock_strategy, mock_gate, _mock_skill):
        self._make_ralph_project(
            'GATE_TEST="npm test"\nGATE_TYPECHECK="tsc"\nGATE_LINT=""\nGATE_BUILD=""\n'
        )
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)
        gate_names = [c[0][0] for c in mock_gate.call_args_list]
        self.assertNotIn("test", gate_names)
        self.assertIn("typecheck", gate_names)

    @patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-code-assist"})
    @patch.object(task_completed, "find_scenario_strategy", return_value="required")
    def test_coverage_below_threshold(self, _mock_strategy, _mock_skill):
        self._make_ralph_project(
            'GATE_TEST=""\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n'
            'GATE_COVERAGE="npm run coverage"\nMIN_TEST_COVERAGE="80"\n'
        )
        with patch.object(task_completed, "run_gate", return_value=(True, "coverage: 70.0% of statements")):
            with patch.object(task_completed, "extract_coverage_pct", return_value=70.0):
                with patch("sys.stdin", self._make_stdin(self._default_input())):
                    with self.assertRaises(SystemExit) as ctx:
                        task_completed.main()
                    self.assertEqual(ctx.exception.code, 2)

    @patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-code-assist"})
    @patch.object(task_completed, "find_scenario_strategy", return_value="required")
    def test_coverage_above_threshold(self, _mock_strategy, _mock_skill):
        self._make_ralph_project(
            'GATE_TEST=""\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n'
            'GATE_COVERAGE="npm run coverage"\nMIN_TEST_COVERAGE="80"\n'
        )
        with patch.object(task_completed, "run_gate", return_value=(True, "coverage: 90.0% of statements")):
            with patch.object(task_completed, "extract_coverage_pct", return_value=90.0):
                with patch("sys.stdin", self._make_stdin(self._default_input())):
                    with self.assertRaises(SystemExit) as ctx:
                        task_completed.main()
                    self.assertEqual(ctx.exception.code, 0)

    @patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-code-assist"})
    @patch.object(task_completed, "find_scenario_strategy", return_value="required")
    def test_coverage_not_extractable_passes(self, _mock_strategy, _mock_skill):
        self._make_ralph_project(
            'GATE_TEST=""\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n'
            'GATE_COVERAGE="npm run coverage"\nMIN_TEST_COVERAGE="80"\n'
        )
        with patch.object(task_completed, "run_gate", return_value=(True, "tests complete")):
            with patch.object(task_completed, "extract_coverage_pct", return_value=None):
                with patch("sys.stdin", self._make_stdin(self._default_input())):
                    with self.assertRaises(SystemExit) as ctx:
                        task_completed.main()
                    self.assertEqual(ctx.exception.code, 0)

    @patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-code-assist"})
    @patch.object(task_completed, "run_gate", return_value=(True, "ok"))
    @patch.object(task_completed, "find_scenario_strategy", return_value="required")
    def test_no_coverage_gate(self, _mock_strategy, _mock_gate, _mock_skill):
        self._make_ralph_project(
            'GATE_TEST=""\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n'
            'GATE_COVERAGE=""\nMIN_TEST_COVERAGE="0"\n'
        )
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)


# ─────────────────────────────────────────────────────────────────
# TestValidateScenarioStrategy
# ─────────────────────────────────────────────────────────────────

class TestValidateScenarioStrategy(unittest.TestCase):
    """Test validate_scenario_strategy() safety net for misclassified tasks."""

    def _mock_git_diffs(self, uncommitted="", committed=""):
        """Mock both git diff calls: uncommitted (HEAD) and last commit (HEAD~1..HEAD)."""
        def side_effect(cmd, **kwargs):
            if "HEAD~1" in cmd:
                return subprocess.CompletedProcess(
                    args=cmd, returncode=0, stdout=committed, stderr=""
                )
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout=uncommitted, stderr=""
            )
        return patch("subprocess.run", side_effect=side_effect)

    def _mock_git_diffs_both_fail(self):
        """Mock both git diff calls returning non-zero."""
        return patch(
            "subprocess.run",
            return_value=subprocess.CompletedProcess(
                args=[], returncode=1, stdout="", stderr=""
            ),
        )

    def test_strategy_required_unchanged(self):
        """Non-'not-applicable' strategies pass through without git call."""
        with patch("subprocess.run") as mock_run:
            result = task_completed.validate_scenario_strategy("required", "/tmp")
            self.assertEqual(result, "required")
            mock_run.assert_not_called()

    def test_only_docs_returns_not_applicable(self):
        with self._mock_git_diffs(uncommitted="README.md\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "not-applicable")

    def test_python_file_overrides_to_required(self):
        with self._mock_git_diffs(uncommitted="api.py\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "required")

    def test_tsx_file_overrides_to_required(self):
        with self._mock_git_diffs(uncommitted="Component.tsx\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "required")

    def test_github_dir_returns_not_applicable(self):
        with self._mock_git_diffs(uncommitted=".github/workflow.yml\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "not-applicable")

    def test_git_failure_returns_not_applicable(self):
        with self._mock_git_diffs_both_fail():
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "not-applicable")

    def test_git_timeout_returns_not_applicable(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=5)):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "not-applicable")

    def test_git_not_found_returns_not_applicable(self):
        with patch("subprocess.run", side_effect=FileNotFoundError("git")):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "not-applicable")

    def test_mixed_docs_and_source_overrides(self):
        with self._mock_git_diffs(uncommitted="README.md\nutils.ts\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "required")

    def test_shell_script_overrides_to_required(self):
        with self._mock_git_diffs(uncommitted="deploy.sh\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "required")

    def test_no_changed_files_returns_not_applicable(self):
        with self._mock_git_diffs():
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "not-applicable")

    def test_docs_root_returns_not_applicable(self):
        with self._mock_git_diffs(uncommitted="docs/guide.md\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "not-applicable")

    def test_unknown_extension_overrides_to_required(self):
        with self._mock_git_diffs(uncommitted="app.zig\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "required")

    # --- New tests for review findings ---

    def test_committed_source_detected_via_last_commit(self):
        """Teammate committed before TaskCompleted → last commit diff catches it."""
        with self._mock_git_diffs(uncommitted="", committed="src/handler.py\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "required")

    def test_committed_docs_only_returns_not_applicable(self):
        with self._mock_git_diffs(uncommitted="", committed="README.md\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "not-applicable")

    def test_docs_subdir_treated_as_source(self):
        """src/docs/helper.ts is NOT root docs/ — should be treated as source."""
        with self._mock_git_diffs(uncommitted="src/docs/helper.ts\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "required")

    def test_license_file_returns_not_applicable(self):
        """Extensionless LICENSE file is non-code."""
        with self._mock_git_diffs(uncommitted="LICENSE\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "not-applicable")

    def test_makefile_returns_not_applicable(self):
        with self._mock_git_diffs(uncommitted="Makefile\n"):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "not-applicable")

    def test_one_diff_fails_other_succeeds(self):
        """If uncommitted diff fails but last commit has source → override."""
        def side_effect(cmd, **kwargs):
            if "HEAD~1" in cmd:
                return subprocess.CompletedProcess(
                    args=cmd, returncode=0, stdout="app.rs\n", stderr=""
                )
            return subprocess.CompletedProcess(
                args=cmd, returncode=128, stdout="", stderr="error"
            )
        with patch("subprocess.run", side_effect=side_effect):
            result = task_completed.validate_scenario_strategy("not-applicable", "/tmp")
            self.assertEqual(result, "required")


class TestSkillEnforcement(unittest.TestCase):
    """TaskCompleted denies if sop-code-assist not invoked in ralph project."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ralph_dir = Path(self.tmpdir) / ".ralph"
        self.ralph_dir.mkdir(parents=True)
        (self.ralph_dir / "config.sh").write_text(
            'GATE_TEST=""\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n',
            encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_stdin(self, data):
        return io.StringIO(json.dumps(data))

    def _default_input(self, **overrides):
        base = {
            "cwd": self.tmpdir,
            "task_subject": "Implement feature X",
            "task_description": "",
            "teammate_name": "agent-1",
        }
        base.update(overrides)
        return base

    @patch.object(task_completed, "read_skill_invoked", return_value=None)
    @patch.object(task_completed, "find_scenario_strategy", return_value="required")
    def test_no_skill_exits_2(self, _mock_strategy, _mock_skill):
        """No skill state → exit 2."""
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 2)

    @patch.object(task_completed, "run_gate", return_value=(True, "ok"))
    @patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-code-assist"})
    @patch.object(task_completed, "find_scenario_strategy", return_value="required")
    def test_skill_present_proceeds(self, _mock_strategy, _mock_skill, _mock_gate):
        """Skill state exists → passes check, proceeds to quality gates."""
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)


class TestNonCodeExtensions(unittest.TestCase):
    """Test extended NON_CODE_EXT_RE for generated artifacts (Gap 5)."""

    def test_source_map_is_non_code(self):
        self.assertTrue(task_completed.NON_CODE_EXT_RE.search("bundle.js.map"))

    def test_snapshot_is_non_code(self):
        self.assertTrue(task_completed.NON_CODE_EXT_RE.search("Button.test.js.snap"))

    def test_dts_is_non_code(self):
        self.assertTrue(task_completed.NON_CODE_EXT_RE.search("types.d.ts"))

    def test_minified_js_is_non_code(self):
        self.assertTrue(task_completed.NON_CODE_EXT_RE.search("app.min.js"))

    def test_minified_css_is_non_code(self):
        self.assertTrue(task_completed.NON_CODE_EXT_RE.search("styles.min.css"))

    def test_prisma_is_code(self):
        self.assertIsNone(task_completed.NON_CODE_EXT_RE.search("schema.prisma"))

    def test_graphql_is_code(self):
        self.assertIsNone(task_completed.NON_CODE_EXT_RE.search("schema.graphql"))

    def test_python_is_code(self):
        self.assertIsNone(task_completed.NON_CODE_EXT_RE.search("app.py"))

    def test_typescript_is_code(self):
        """Regular .ts files should NOT match (they are code)."""
        # .ts alone should not match d.ts pattern
        self.assertIsNone(task_completed.NON_CODE_EXT_RE.search("app.ts"))


if __name__ == "__main__":
    unittest.main()
