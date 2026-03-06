#!/usr/bin/env python3
"""Tests for SDD coverage enforcement — anti reward-hacking by omission.

Tests cover:
- is_exempt_from_tests() — exemption patterns
- find_test_for_source() — convention matching
- record_file_edit() — atomic state I/O
- compute_uncovered() — coverage gap detection
- sdd-auto-test.py main() — coverage tracking
- task-completed.py — coverage gate
"""
import importlib
import io
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _sdd_detect
from _sdd_detect import (
    clear_coverage, compute_uncovered, coverage_path, find_test_for_source,
    is_exempt_from_tests, is_source_file, is_test_file, read_coverage,
    record_file_edit,
)

sdd_auto_test = importlib.import_module("sdd-auto-test")
task_completed = importlib.import_module("task-completed")


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────

def _cleanup_coverage(cwd):
    try:
        coverage_path(cwd).unlink(missing_ok=True)
    except OSError:
        pass


# ─────────────────────────────────────────────────────────────────
# TestIsExemptFromTests
# ─────────────────────────────────────────────────────────────────

class TestIsExemptFromTests(unittest.TestCase):
    """Test is_exempt_from_tests() exemption patterns."""

    def test_none_returns_false(self):
        self.assertFalse(is_exempt_from_tests(None))

    def test_empty_returns_false(self):
        self.assertFalse(is_exempt_from_tests(""))

    def test_init_py_exempt(self):
        self.assertTrue(is_exempt_from_tests("src/__init__.py"))

    def test_conftest_py_exempt(self):
        self.assertTrue(is_exempt_from_tests("tests/conftest.py"))

    def test_setup_py_exempt(self):
        self.assertTrue(is_exempt_from_tests("setup.py"))

    def test_index_ts_exempt(self):
        self.assertTrue(is_exempt_from_tests("src/index.ts"))

    def test_index_tsx_exempt(self):
        self.assertTrue(is_exempt_from_tests("components/index.tsx"))

    def test_types_ts_exempt(self):
        self.assertTrue(is_exempt_from_tests("src/types.ts"))

    def test_types_d_ts_exempt(self):
        self.assertTrue(is_exempt_from_tests("src/types.d.ts"))

    def test_constants_py_exempt(self):
        self.assertTrue(is_exempt_from_tests("app/constants.py"))

    def test_config_json_exempt(self):
        self.assertTrue(is_exempt_from_tests("config.json"))

    def test_config_ts_exempt(self):
        self.assertTrue(is_exempt_from_tests("src/config.ts"))

    def test_config_yaml_exempt(self):
        self.assertTrue(is_exempt_from_tests("config.yaml"))

    def test_migrations_dir_exempt(self):
        self.assertTrue(is_exempt_from_tests("migrations/001_init.py"))

    def test_migration_dir_exempt(self):
        self.assertTrue(is_exempt_from_tests("migration/add_users.sql"))

    def test_generated_dir_exempt(self):
        self.assertTrue(is_exempt_from_tests("generated/schema.ts"))

    def test_vendor_dir_exempt(self):
        self.assertTrue(is_exempt_from_tests("vendor/lib/foo.go"))

    def test_scripts_dir_exempt(self):
        self.assertTrue(is_exempt_from_tests("scripts/deploy.sh"))

    def test_docs_dir_exempt(self):
        self.assertTrue(is_exempt_from_tests("docs/guide.py"))

    def test_ralph_dir_exempt(self):
        """Files in .ralph/ are orchestration infrastructure, not source code."""
        self.assertTrue(is_exempt_from_tests(".ralph/config.sh"))
        self.assertTrue(is_exempt_from_tests(".ralph/specs/goal/implementation/plan.sh"))
        self.assertTrue(is_exempt_from_tests("project/.ralph/scripts/setup.sh"))

    def test_regular_source_not_exempt(self):
        self.assertFalse(is_exempt_from_tests("src/main.py"))

    def test_regular_ts_not_exempt(self):
        self.assertFalse(is_exempt_from_tests("src/service.ts"))

    def test_regular_go_not_exempt(self):
        self.assertFalse(is_exempt_from_tests("pkg/handler.go"))


# ─────────────────────────────────────────────────────────────────
# TestFindTestForSource
# ─────────────────────────────────────────────────────────────────

class TestFindTestForSource(unittest.TestCase):
    """Test find_test_for_source() convention matching."""

    def test_python_test_prefix(self):
        result = find_test_for_source("src/foo.py", ["tests/test_foo.py"])
        self.assertEqual(result, "tests/test_foo.py")

    def test_python_test_suffix(self):
        result = find_test_for_source("src/foo.py", ["tests/foo_test.py"])
        self.assertEqual(result, "tests/foo_test.py")

    def test_ts_test_file(self):
        result = find_test_for_source("src/foo.ts", ["tests/foo.test.ts"])
        self.assertEqual(result, "tests/foo.test.ts")

    def test_ts_spec_file(self):
        result = find_test_for_source("src/foo.ts", ["tests/foo.spec.ts"])
        self.assertEqual(result, "tests/foo.spec.ts")

    def test_jsx_test_file(self):
        result = find_test_for_source("src/Button.tsx", ["__tests__/Button.test.tsx"])
        self.assertEqual(result, "__tests__/Button.test.tsx")

    def test_go_test_file(self):
        result = find_test_for_source("pkg/handler.go", ["pkg/handler_test.go"])
        self.assertEqual(result, "pkg/handler_test.go")

    def test_no_match_returns_none(self):
        result = find_test_for_source("src/foo.py", ["tests/test_bar.py"])
        self.assertIsNone(result)

    def test_empty_test_files_returns_none(self):
        result = find_test_for_source("src/foo.py", [])
        self.assertIsNone(result)

    def test_multiple_test_files_first_match(self):
        tests = ["tests/test_foo.py", "tests/foo_test.py"]
        result = find_test_for_source("src/foo.py", tests)
        self.assertIn(result, tests)

    def test_js_spec_file(self):
        result = find_test_for_source("src/utils.js", ["tests/utils.spec.js"])
        self.assertEqual(result, "tests/utils.spec.js")


# ─────────────────────────────────────────────────────────────────
# TestRecordFileEdit
# ─────────────────────────────────────────────────────────────────

class TestRecordFileEdit(unittest.TestCase):
    """Test record_file_edit() atomic state I/O."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        _cleanup_coverage(self.tmpdir)

    def tearDown(self):
        _cleanup_coverage(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_record_source_file(self):
        record_file_edit(self.tmpdir, "src/main.py")
        state = read_coverage(self.tmpdir)
        self.assertIsNotNone(state)
        self.assertIn("src/main.py", state["source_files"])
        self.assertEqual(state["test_files"], [])

    def test_record_test_file(self):
        record_file_edit(self.tmpdir, "tests/test_main.py")
        state = read_coverage(self.tmpdir)
        self.assertIsNotNone(state)
        self.assertIn("tests/test_main.py", state["test_files"])
        self.assertEqual(state["source_files"], [])

    def test_record_multiple_files(self):
        record_file_edit(self.tmpdir, "src/a.py")
        record_file_edit(self.tmpdir, "src/b.py")
        record_file_edit(self.tmpdir, "tests/test_a.py")
        state = read_coverage(self.tmpdir)
        self.assertEqual(len(state["source_files"]), 2)
        self.assertEqual(len(state["test_files"]), 1)

    def test_deduplication(self):
        record_file_edit(self.tmpdir, "src/main.py")
        record_file_edit(self.tmpdir, "src/main.py")
        state = read_coverage(self.tmpdir)
        self.assertEqual(state["source_files"].count("src/main.py"), 1)

    def test_timestamp_updated(self):
        record_file_edit(self.tmpdir, "src/a.py")
        state = read_coverage(self.tmpdir)
        self.assertIn("timestamp", state)


# ─────────────────────────────────────────────────────────────────
# TestReadCoverage
# ─────────────────────────────────────────────────────────────────

class TestReadCoverage(unittest.TestCase):
    """Test read_coverage() TTL and error handling."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        _cleanup_coverage(self.tmpdir)

    def tearDown(self):
        _cleanup_coverage(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_file_returns_none(self):
        self.assertIsNone(read_coverage(self.tmpdir))

    def test_fresh_state_returned(self):
        record_file_edit(self.tmpdir, "src/main.py")
        self.assertIsNotNone(read_coverage(self.tmpdir))

    def test_stale_state_returns_none(self):
        record_file_edit(self.tmpdir, "src/main.py")
        # Force stale timestamp
        cp = coverage_path(self.tmpdir)
        data = json.loads(cp.read_text())
        old_ts = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(time.time() - 15000),  # 15000s > 14400s
        )
        data["timestamp"] = old_ts
        cp.write_text(json.dumps(data))
        self.assertIsNone(read_coverage(self.tmpdir))

    def test_corrupt_file_returns_none(self):
        cp = coverage_path(self.tmpdir)
        cp.write_text("not json{{{")
        self.assertIsNone(read_coverage(self.tmpdir))


# ─────────────────────────────────────────────────────────────────
# TestClearCoverage
# ─────────────────────────────────────────────────────────────────

class TestClearCoverage(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        _cleanup_coverage(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_clear_removes_file(self):
        record_file_edit(self.tmpdir, "src/main.py")
        self.assertTrue(coverage_path(self.tmpdir).exists())
        clear_coverage(self.tmpdir)
        self.assertFalse(coverage_path(self.tmpdir).exists())

    def test_clear_no_file_no_error(self):
        clear_coverage(self.tmpdir)  # Should not raise


# ─────────────────────────────────────────────────────────────────
# TestComputeUncovered
# ─────────────────────────────────────────────────────────────────

class TestComputeUncovered(unittest.TestCase):
    """Test compute_uncovered() coverage gap detection."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_all_covered(self):
        state = {
            "source_files": ["src/foo.py"],
            "test_files": ["tests/test_foo.py"],
        }
        self.assertEqual(compute_uncovered(self.tmpdir, state), [])

    def test_uncovered_source(self):
        state = {
            "source_files": ["src/foo.py", "src/bar.py"],
            "test_files": ["tests/test_foo.py"],
        }
        uncovered = compute_uncovered(self.tmpdir, state)
        self.assertEqual(uncovered, ["src/bar.py"])

    def test_exempt_files_excluded(self):
        state = {
            "source_files": ["src/__init__.py", "src/foo.py"],
            "test_files": ["tests/test_foo.py"],
        }
        self.assertEqual(compute_uncovered(self.tmpdir, state), [])

    def test_empty_state(self):
        state = {"source_files": [], "test_files": []}
        self.assertEqual(compute_uncovered(self.tmpdir, state), [])

    def test_test_files_in_source_excluded(self):
        """Test files accidentally recorded as source are not flagged."""
        state = {
            "source_files": ["tests/test_foo.py", "src/bar.py"],
            "test_files": ["tests/test_bar.py"],
        }
        # test_foo.py in source_files is a test file → excluded by is_test_file check
        uncovered = compute_uncovered(self.tmpdir, state)
        self.assertEqual(uncovered, [])

    def test_multiple_uncovered(self):
        state = {
            "source_files": ["src/a.py", "src/b.py", "src/c.py"],
            "test_files": [],
        }
        uncovered = compute_uncovered(self.tmpdir, state)
        self.assertEqual(len(uncovered), 3)

    def test_config_exempt(self):
        state = {
            "source_files": ["config.json", "src/main.py"],
            "test_files": ["tests/test_main.py"],
        }
        self.assertEqual(compute_uncovered(self.tmpdir, state), [])


# ─────────────────────────────────────────────────────────────────
# TestAutoTestCoverageTracking
# ─────────────────────────────────────────────────────────────────

class TestAutoTestCoverageTracking(unittest.TestCase):
    """Test sdd-auto-test.py main() coverage tracking."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        _cleanup_coverage(self.tmpdir)

    def tearDown(self):
        _cleanup_coverage(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run_main(self, input_data):
        stdin_text = json.dumps(input_data)
        stdout_capture = io.StringIO()
        exit_code = 0
        with patch.object(sys, "argv", ["sdd-auto-test.py"]), \
             patch.object(sys, "stdin", io.StringIO(stdin_text)), \
             patch.object(sys, "stdout", stdout_capture), \
             patch.object(sdd_auto_test, "run_tests_background"), \
             patch.object(sdd_auto_test, "read_state", return_value=None), \
             patch.object(sdd_auto_test, "is_test_running", return_value=False), \
             patch.object(sdd_auto_test, "detect_test_command", return_value=None):
            try:
                sdd_auto_test.main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return stdout_capture.getvalue(), exit_code

    def test_source_file_tracked(self):
        """Source file edit records in coverage state."""
        self._run_main({"cwd": self.tmpdir, "tool_input": {"file_path": "src/main.py"}})
        state = read_coverage(self.tmpdir)
        self.assertIsNotNone(state)
        self.assertIn("src/main.py", state["source_files"])

    def test_test_file_tracked(self):
        """Test file edit records in coverage state."""
        self._run_main({"cwd": self.tmpdir, "tool_input": {"file_path": "tests/test_main.py"}})
        state = read_coverage(self.tmpdir)
        self.assertIsNotNone(state)
        self.assertIn("tests/test_main.py", state["test_files"])

    def test_exempt_file_not_tracked(self):
        """Exempt file (e.g. __init__.py) is not tracked."""
        self._run_main({"cwd": self.tmpdir, "tool_input": {"file_path": "src/__init__.py"}})
        state = read_coverage(self.tmpdir)
        # __init__.py is a .py source file but exempt → exits before record
        self.assertIsNone(state)

    def test_no_coverage_nudge_emitted(self):
        """Coverage tracking exists but no nudge is emitted to context."""
        for f in ["src/a.py", "src/b.py", "src/c.py"]:
            record_file_edit(self.tmpdir, f)

        stdout, _ = self._run_main({
            "cwd": self.tmpdir,
            "tool_input": {"file_path": "src/d.py"},
        })
        # No nudge — coverage enforcement is at TaskCompleted, not PostToolUse
        self.assertEqual(stdout, "")


# ─────────────────────────────────────────────────────────────────
# TestTaskCompletedCoverageGate
# ─────────────────────────────────────────────────────────────────

class TestTaskCompletedCoverageGate(unittest.TestCase):
    """Test task-completed.py coverage gate behavior."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        _cleanup_coverage(self.tmpdir)

    def tearDown(self):
        _cleanup_coverage(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run_main(self, input_data):
        stdin_mock = io.StringIO(json.dumps(input_data))
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        exit_code = 0
        with patch("sys.stdin", stdin_mock), \
             patch("sys.stdout", stdout_capture), \
             patch("sys.stderr", stderr_capture):
            try:
                task_completed.main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()

    @patch.object(task_completed, "detect_test_command", return_value=None)
    def test_uncovered_files_block_completion(self, _mock):
        """Uncovered source files → exit 2."""
        record_file_edit(self.tmpdir, "src/foo.py")
        record_file_edit(self.tmpdir, "src/bar.py")

        exit_code, _, stderr = self._run_main({
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("Untested source files", stderr)
        self.assertIn("reward hacking by omission", stderr)

    @patch.object(task_completed, "detect_test_command", return_value=None)
    def test_all_covered_allows_completion(self, _mock):
        """All source files have matching tests → exit 0."""
        record_file_edit(self.tmpdir, "src/foo.py")
        record_file_edit(self.tmpdir, "tests/test_foo.py")

        exit_code, _, _ = self._run_main({
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 0)

    @patch.object(task_completed, "detect_test_command", return_value=None)
    def test_exempt_files_dont_block(self, _mock):
        """Exempt files (e.g. __init__.py) don't block completion."""
        record_file_edit(self.tmpdir, "src/__init__.py")
        record_file_edit(self.tmpdir, "src/config.json")

        exit_code, _, _ = self._run_main({
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 0)

    @patch.object(task_completed, "detect_test_command", return_value=None)
    def test_no_coverage_state_allows_completion(self, _mock):
        """No coverage state file → exit 0 (nothing tracked)."""
        exit_code, _, _ = self._run_main({
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertEqual(exit_code, 0)

    @patch.object(task_completed, "detect_test_command", return_value=None)
    def test_coverage_cleared_on_success(self, _mock):
        """Coverage state is cleared after successful completion."""
        record_file_edit(self.tmpdir, "src/foo.py")
        record_file_edit(self.tmpdir, "tests/test_foo.py")

        self._run_main({
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
        })
        self.assertIsNone(read_coverage(self.tmpdir))

    @patch.object(task_completed, "detect_test_command", return_value=None)
    def test_regular_subagent_skips_coverage_gate(self, _mock):
        """Regular sub-agents (no teammate) skip coverage gate."""
        record_file_edit(self.tmpdir, "src/foo.py")  # uncovered

        exit_code, _, _ = self._run_main({
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            # No teammate_name → defaults to "unknown" → skips gate
        })
        self.assertEqual(exit_code, 0)


# ─────────────────────────────────────────────────────────────────
# TestCentralizedClassifiers
# ─────────────────────────────────────────────────────────────────

class TestCentralizedClassifiers(unittest.TestCase):
    """Verify that is_source_file and is_test_file from _sdd_detect work correctly
    and that sdd-auto-test.py and sdd-test-guard.py import from _sdd_detect."""

    def test_is_source_file_from_detect(self):
        self.assertTrue(_sdd_detect.is_source_file("app/main.py"))
        self.assertFalse(_sdd_detect.is_source_file("README.md"))

    def test_is_test_file_from_detect(self):
        self.assertTrue(_sdd_detect.is_test_file("tests/test_foo.py"))
        self.assertFalse(_sdd_detect.is_test_file("src/main.py"))

    def test_auto_test_uses_detect_is_source_file(self):
        """sdd-auto-test.py should use is_source_file from _sdd_detect."""
        self.assertIs(sdd_auto_test.is_source_file, _sdd_detect.is_source_file)

    def test_test_guard_uses_detect_is_test_file(self):
        """sdd-test-guard.py should use is_test_file from _sdd_detect."""
        sdd_test_guard = importlib.import_module("sdd-test-guard")
        self.assertIs(sdd_test_guard.is_test_file, _sdd_detect.is_test_file)


if __name__ == "__main__":
    unittest.main()
