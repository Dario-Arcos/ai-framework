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
    """Test _handle_non_ralph_completion() — runs tests fresh."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch.object(task_completed, "detect_test_command", return_value=None)
    def test_no_test_command_allows(self, _mock):
        """No test infrastructure → allow completion."""
        task_completed._handle_non_ralph_completion(self.tmpdir, "my task")

    @patch.object(task_completed, "run_gate", return_value=(True, "5 passed"))
    @patch.object(task_completed, "detect_test_command", return_value="npm test")
    def test_tests_passing_allows(self, _mock_detect, _mock_gate):
        """Tests passing (fresh run) → allow completion."""
        task_completed._handle_non_ralph_completion(self.tmpdir, "my task")

    @patch.object(task_completed, "run_gate", return_value=(False, "FAIL: 2 tests"))
    @patch.object(task_completed, "detect_test_command", return_value="npm test")
    def test_tests_failing_exits_2(self, _mock_detect, _mock_gate):
        """Tests failing (fresh run) → exit 2."""
        with self.assertRaises(SystemExit) as ctx:
            task_completed._handle_non_ralph_completion(self.tmpdir, "my task")
        self.assertEqual(ctx.exception.code, 2)

    @patch("sys.stderr", new_callable=io.StringIO)
    @patch.object(task_completed, "run_gate", return_value=(False, "1 failed, 2 passed"))
    @patch.object(task_completed, "detect_test_command", return_value="pytest")
    def test_failing_shows_output_in_stderr(self, _mock_detect, _mock_gate, mock_stderr):
        """Failure feedback includes fresh test output."""
        with self.assertRaises(SystemExit):
            task_completed._handle_non_ralph_completion(self.tmpdir, "my task")
        output = mock_stderr.getvalue()
        self.assertIn("1 failed", output)
        self.assertIn("my task", output)


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
    def test_all_gates_pass(self, _mock_gate, _mock_skill):
        self._make_ralph_project(
            'GATE_TEST="npm test"\nGATE_TYPECHECK="tsc"\nGATE_LINT="eslint"\nGATE_BUILD="npm run build"\n'
        )
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)
        # Verify failures were reset
        failures_file = self.ralph_dir / "failures.json"
        if failures_file.exists():
            data = json.loads(failures_file.read_text())
            self.assertEqual(data.get("agent-1", 0), 0)

    @patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-code-assist"})
    def test_gate_fails(self, _mock_skill):
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
    def test_empty_gate_skipped(self, mock_gate, _mock_skill):
        self._make_ralph_project('GATE_TEST="npm test"\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n')
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)
        # run_gate called for GATE_TEST only (empty gates skipped by main loop)
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
    def test_all_gates_run_when_configured(self, mock_gate, _mock_skill):
        """All configured gates run — no scenario-strategy filtering."""
        self._make_ralph_project(
            'GATE_TEST="npm test"\nGATE_TYPECHECK="tsc"\nGATE_LINT=""\nGATE_BUILD=""\n'
        )
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)
        gate_names = [c[0][0] for c in mock_gate.call_args_list]
        self.assertIn("test", gate_names)
        self.assertIn("typecheck", gate_names)

    @patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-code-assist"})
    def test_coverage_below_threshold(self, _mock_skill):
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
    def test_coverage_above_threshold(self, _mock_skill):
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
    def test_coverage_not_extractable_passes(self, _mock_skill):
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
    def test_no_coverage_gate(self, _mock_gate, _mock_skill):
        self._make_ralph_project(
            'GATE_TEST=""\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n'
            'GATE_COVERAGE=""\nMIN_TEST_COVERAGE="0"\n'
        )
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)


# ─────────────────────────────────────────────────────────────────
# TestSkillEnforcement
# ─────────────────────────────────────────────────────────────────

class TestSkillEnforcement(unittest.TestCase):
    """TaskCompleted denies if required SDD skill not invoked in ralph project."""

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
    def test_no_skill_exits_2(self, _mock_skill):
        """No skill state → exit 2."""
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 2)

    @patch.object(task_completed, "run_gate", return_value=(True, "ok"))
    @patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-code-assist"})
    def test_skill_present_proceeds(self, _mock_skill, _mock_gate):
        """Skill state exists → passes check, proceeds to quality gates."""
        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)

    def test_rev_teammate_requires_sop_reviewer(self):
        """rev-* teammate without sop-reviewer → exit 2."""
        with patch.object(task_completed, "read_skill_invoked", return_value=None):
            with patch("sys.stdin", self._make_stdin(self._default_input(teammate_name="rev-code"))):
                with self.assertRaises(SystemExit) as ctx:
                    task_completed.main()
                self.assertEqual(ctx.exception.code, 2)

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_rev_teammate_error_mentions_sop_reviewer(self, mock_stderr):
        """rev-* teammate failure message mentions sop-reviewer."""
        with patch.object(task_completed, "read_skill_invoked", return_value=None):
            with patch("sys.stdin", self._make_stdin(self._default_input(teammate_name="rev-security"))):
                with self.assertRaises(SystemExit):
                    task_completed.main()
        output = mock_stderr.getvalue()
        self.assertIn("sop-reviewer", output)

    @patch.object(task_completed, "run_gate", return_value=(True, "ok"))
    def test_rev_teammate_with_sop_reviewer_proceeds(self, _mock_gate):
        """rev-* teammate with sop-reviewer invoked → proceeds to gates."""
        with patch.object(task_completed, "read_skill_invoked", return_value={"skill": "sop-reviewer"}):
            with patch("sys.stdin", self._make_stdin(self._default_input(teammate_name="rev-arch"))):
                with self.assertRaises(SystemExit) as ctx:
                    task_completed.main()
                self.assertEqual(ctx.exception.code, 0)

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_non_rev_teammate_error_mentions_sop_code_assist(self, mock_stderr):
        """Non-rev teammate failure message mentions sop-code-assist."""
        with patch.object(task_completed, "read_skill_invoked", return_value=None):
            with patch("sys.stdin", self._make_stdin(self._default_input(teammate_name="worker-1"))):
                with self.assertRaises(SystemExit):
                    task_completed.main()
        output = mock_stderr.getvalue()
        self.assertIn("sop-code-assist", output)

    def test_rev_checks_sop_reviewer_not_sop_code_assist(self):
        """rev-* teammate checks for sop-reviewer specifically (not sop-code-assist)."""
        calls = []
        def mock_read_skill(cwd, skill_name):
            calls.append(skill_name)
            return {"skill": skill_name}

        with patch.object(task_completed, "read_skill_invoked", side_effect=mock_read_skill):
            with patch.object(task_completed, "run_gate", return_value=(True, "ok")):
                with patch("sys.stdin", self._make_stdin(self._default_input(teammate_name="rev-x"))):
                    with self.assertRaises(SystemExit) as ctx:
                        task_completed.main()
                    self.assertEqual(ctx.exception.code, 0)
        self.assertIn("sop-reviewer", calls)

    def test_non_rev_checks_sop_code_assist(self):
        """Non-rev teammate checks for sop-code-assist specifically."""
        calls = []
        def mock_read_skill(cwd, skill_name):
            calls.append(skill_name)
            return {"skill": skill_name}

        with patch.object(task_completed, "read_skill_invoked", side_effect=mock_read_skill):
            with patch.object(task_completed, "run_gate", return_value=(True, "ok")):
                with patch("sys.stdin", self._make_stdin(self._default_input(teammate_name="agent-1"))):
                    with self.assertRaises(SystemExit) as ctx:
                        task_completed.main()
                    self.assertEqual(ctx.exception.code, 0)
        self.assertIn("sop-code-assist", calls)


# ─────────────────────────────────────────────────────────────────
# TestSkillStateClearOnSuccess
# ─────────────────────────────────────────────────────────────────

class TestSkillStateClearOnSuccess(unittest.TestCase):
    """TaskCompleted clears skill state after all gates pass (prevents inheritance)."""

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
        # Clean up any /tmp/ state files
        import _sdd_detect
        for skill in ("sop-code-assist", "sop-reviewer"):
            try:
                _sdd_detect.skill_invoked_path(self.tmpdir, skill).unlink(missing_ok=True)
            except OSError:
                pass

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

    @patch.object(task_completed, "run_gate", return_value=(True, "ok"))
    def test_state_cleared_after_success(self, _mock_gate):
        """After all gates pass, skill state files are deleted."""
        import _sdd_detect
        # Pre-condition: skill state exists
        _sdd_detect.write_skill_invoked(self.tmpdir, "sop-code-assist")
        _sdd_detect.write_skill_invoked(self.tmpdir, "sop-reviewer")
        self.assertIsNotNone(_sdd_detect.read_skill_invoked(self.tmpdir, "sop-code-assist"))
        self.assertIsNotNone(_sdd_detect.read_skill_invoked(self.tmpdir, "sop-reviewer"))

        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)

        # Post-condition: both skill states cleared
        self.assertIsNone(_sdd_detect.read_skill_invoked(self.tmpdir, "sop-code-assist"))
        self.assertIsNone(_sdd_detect.read_skill_invoked(self.tmpdir, "sop-reviewer"))

    def test_state_preserved_on_gate_failure(self):
        """On gate failure, skill state is NOT cleared (teammate retries)."""
        import _sdd_detect
        _sdd_detect.write_skill_invoked(self.tmpdir, "sop-code-assist")

        (self.ralph_dir / "config.sh").write_text(
            'GATE_TEST="npm test"\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n',
            encoding="utf-8",
        )
        with patch.object(task_completed, "run_gate", return_value=(False, "FAIL")):
            with patch("sys.stdin", self._make_stdin(self._default_input())):
                with self.assertRaises(SystemExit) as ctx:
                    task_completed.main()
                self.assertEqual(ctx.exception.code, 2)

        # State preserved — teammate needs it for retry
        self.assertIsNotNone(_sdd_detect.read_skill_invoked(self.tmpdir, "sop-code-assist"))

    @patch.object(task_completed, "run_gate", return_value=(True, "ok"))
    def test_clear_tolerates_missing_files(self, _mock_gate):
        """Clear doesn't crash if state files don't exist."""
        import _sdd_detect
        _sdd_detect.write_skill_invoked(self.tmpdir, "sop-code-assist")
        # sop-reviewer state deliberately NOT created

        with patch("sys.stdin", self._make_stdin(self._default_input())):
            with self.assertRaises(SystemExit) as ctx:
                task_completed.main()
            self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
