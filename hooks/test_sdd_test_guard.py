#!/usr/bin/env python3
"""Tests for sdd-test-guard.py — PreToolUse hook that prevents reward hacking."""
import importlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sdd_test_guard = importlib.import_module("sdd-test-guard")

is_test_file = sdd_test_guard.is_test_file
count_assertions = sdd_test_guard.count_assertions
count_precise = sdd_test_guard.count_precise
analyze_edit = sdd_test_guard.analyze_edit
is_tautological_test_addition = sdd_test_guard._is_tautological_test_addition
load_critical_paths = sdd_test_guard._load_critical_paths
matches_critical_path = sdd_test_guard._matches_critical_path
main = sdd_test_guard.main


class TestIsTestFile(unittest.TestCase):
    """Test is_test_file() pattern matching."""

    def test_none(self):
        self.assertFalse(is_test_file(None))

    def test_empty(self):
        self.assertFalse(is_test_file(""))

    def test_test_prefix(self):
        self.assertTrue(is_test_file("test_foo.py"))

    def test_test_suffix(self):
        self.assertTrue(is_test_file("foo_test.go"))

    def test_dot_test(self):
        self.assertTrue(is_test_file("foo.test.js"))

    def test_dot_spec(self):
        self.assertTrue(is_test_file("foo.spec.ts"))

    def test_tests_dir(self):
        self.assertTrue(is_test_file("test/foo.py"))

    def test_dunder_tests_dir(self):
        self.assertTrue(is_test_file("__tests__/foo.js"))

    def test_source_file(self):
        self.assertFalse(is_test_file("src/main.py"))


class TestCountAssertions(unittest.TestCase):
    """Test count_assertions() across languages."""

    def test_none(self):
        self.assertEqual(count_assertions(None), 0)

    def test_empty(self):
        self.assertEqual(count_assertions(""), 0)

    def test_python_assert(self):
        text = "assert x == 1\nassert y == 2"
        self.assertEqual(count_assertions(text), 2)

    def test_jest_expect(self):
        text = "expect(foo).toBe(1)\nexpect(bar).toEqual(2)"
        # expect( matches twice, plus .toBe and .toEqual
        count = count_assertions(text)
        self.assertGreaterEqual(count, 2)

    def test_go_t_error(self):
        text = 't.Error("fail")\nt.Fatal("bad")'
        self.assertEqual(count_assertions(text), 2)

    def test_rust_assert_eq(self):
        text = "assert_eq!(a, b)\nassert_ne!(c, d)"
        self.assertEqual(count_assertions(text), 2)

    def test_no_assertions(self):
        text = 'print("hello")\nx = 1'
        self.assertEqual(count_assertions(text), 0)


class TestAnalyzeEdit(unittest.TestCase):
    """Test analyze_edit() for Edit and Write tools."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_edit_tool_counts(self):
        """Edit with old_string having 2 assertions, new_string having 1."""
        tool_input = {
            "file_path": "test_foo.py",
            "old_string": "assert x == 1\nassert y == 2",
            "new_string": "assert x == 1",
        }
        old, new, old_text, new_text = analyze_edit("Edit", tool_input)
        self.assertEqual(old, 2)
        self.assertEqual(new, 1)
        self.assertEqual(old_text, "assert x == 1\nassert y == 2")
        self.assertEqual(new_text, "assert x == 1")

    def test_edit_removing_assertions(self):
        """Edit removing all assertions."""
        tool_input = {
            "file_path": "test_foo.py",
            "old_string": "assert x == 1\nassert y == 2\nassert z == 3",
            "new_string": "pass",
        }
        old, new, _, _ = analyze_edit("Edit", tool_input)
        self.assertEqual(old, 3)
        self.assertEqual(new, 0)

    def test_edit_adding_assertions(self):
        """Edit adding assertions where there were none."""
        tool_input = {
            "file_path": "test_foo.py",
            "old_string": "pass",
            "new_string": "assert x == 1\nassert y == 2",
        }
        old, new, _, _ = analyze_edit("Edit", tool_input)
        self.assertEqual(old, 0)
        self.assertEqual(new, 2)

    def test_write_new_file(self):
        """Write to nonexistent file — old count is 0."""
        nonexistent = os.path.join(self.tmpdir, "new_test.py")
        tool_input = {
            "file_path": nonexistent,
            "content": "assert a == 1\nassert b == 2",
        }
        old, new, _, _ = analyze_edit("Write", tool_input)
        self.assertEqual(old, 0)
        self.assertEqual(new, 2)

    def test_write_existing_file(self):
        """Write to existing file — reads old assertions from disk."""
        existing = os.path.join(self.tmpdir, "test_existing.py")
        Path(existing).write_text(
            "assert x == 1\nassert y == 2\nassert z == 3", encoding="utf-8"
        )
        tool_input = {
            "file_path": existing,
            "content": "assert x == 1",
        }
        old, new, _, _ = analyze_edit("Write", tool_input)
        self.assertEqual(old, 3)
        self.assertEqual(new, 1)

    def test_unknown_tool(self):
        """Unknown tool name returns (0, 0, '', '')."""
        old, new, old_text, new_text = analyze_edit("Read", {"file_path": "test_foo.py"})
        self.assertEqual(old, 0)
        self.assertEqual(new, 0)
        self.assertEqual(old_text, "")
        self.assertEqual(new_text, "")


class TestFailHelper(unittest.TestCase):
    """Direct tests for _fail() formatting."""

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_default_category_prefix(self, mock_stderr):
        with self.assertRaises(SystemExit) as ctx:
            sdd_test_guard._fail("blocked")
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("[SDD:SCENARIO] SDD Guard: blocked", mock_stderr.getvalue())


class TestMain(unittest.TestCase):
    """Test main() decision matrix end-to-end."""

    def _run_main(self, input_data):
        """Run main() with given JSON input, return (exit_code, stdout, stderr)."""
        stdin_mock = io.StringIO(json.dumps(input_data))
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        exit_code = 0
        with patch("sys.stdin", stdin_mock), \
             patch("sys.stdout", stdout_capture), \
             patch("sys.stderr", stderr_capture):
            try:
                main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()

    def test_invalid_json_exits_0(self):
        """Bad stdin → exit 0 (allow)."""
        stdin_mock = io.StringIO("not valid json{{{")
        with patch("sys.stdin", stdin_mock):
            with self.assertRaises(SystemExit) as ctx:
                main()
            self.assertEqual(ctx.exception.code, 0)

    def test_non_test_file_allows(self):
        """Source file (not a test) → exit 0."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "src/main.py",
                "old_string": "assert x == 1",
                "new_string": "pass",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    @patch.object(sdd_test_guard, "read_state", return_value=None)
    def test_no_state_allows(self, _mock):
        """Test file, no state → exit 0 (no data = no block)."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test_foo.py",
                "old_string": "assert x == 1",
                "new_string": "pass",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    @patch.object(sdd_test_guard, "read_state", return_value={"passing": True, "summary": "5 passed"})
    def test_passing_state_allows(self, _mock):
        """Test file, tests passing → exit 0 (refactoring OK)."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test_foo.py",
                "old_string": "assert x == 1\nassert y == 2",
                "new_string": "assert x == 1",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    @patch.object(sdd_test_guard, "read_state", return_value={"passing": False, "summary": "2 failed"})
    def test_failing_assertions_reduced_denies(self, _mock):
        """Tests failing + assertions reduced → DENY (exit 2 + stderr)."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test_foo.py",
                "old_string": "assert x == 1\nassert y == 2",
                "new_string": "assert x == 1",
            },
        })
        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("reward hacking", stderr)
        self.assertIn("2", stderr)
        self.assertIn("1", stderr)

    @patch.object(sdd_test_guard, "read_state", return_value={"passing": False, "summary": "1 failed"})
    def test_failing_assertions_same_allows(self, _mock):
        """Tests failing + assertions unchanged → exit 0 (allow)."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test_foo.py",
                "old_string": "assert x == 1",
                "new_string": "assert y == 2",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    @patch.object(sdd_test_guard, "read_state", return_value={"passing": False, "summary": "1 failed"})
    def test_failing_assertions_increased_allows(self, _mock):
        """Tests failing + assertions increased → exit 0 (allow)."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test_foo.py",
                "old_string": "assert x == 1",
                "new_string": "assert x == 1\nassert y == 2\nassert z == 3",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")


class TestCountPrecise(unittest.TestCase):
    """Test count_precise() for concrete value assertions."""

    def test_python_equality(self):
        self.assertEqual(count_precise('assert x == 42'), 1)

    def test_python_string_equality(self):
        self.assertEqual(count_precise('assert x == "hello"'), 1)

    def test_python_is_not_none(self):
        self.assertEqual(count_precise('assert x is not None'), 0)

    def test_jest_toBe(self):
        self.assertEqual(count_precise('expect(x).toBe(42)'), 1)

    def test_jest_toEqual(self):
        self.assertEqual(count_precise('expect(x).toEqual({a: 1})'), 1)

    def test_jest_toStrictEqual(self):
        self.assertEqual(count_precise('expect(x).toStrictEqual([1, 2])'), 1)

    def test_jest_toBeTruthy(self):
        self.assertEqual(count_precise('expect(x).toBeTruthy()'), 0)

    def test_rust_assert_eq(self):
        self.assertEqual(count_precise('assert_eq!(a, b)'), 1)

    def test_python_assertEqual(self):
        self.assertEqual(count_precise('self.assertEqual(x, 42)'), 1)

    def test_chai_to_equal(self):
        self.assertEqual(count_precise('expect(x).to.equal(42)'), 1)

    def test_chai_to_eql(self):
        self.assertEqual(count_precise('expect(x).to.eql({a: 1})'), 1)

    def test_none_input(self):
        self.assertEqual(count_precise(None), 0)

    def test_empty_input(self):
        self.assertEqual(count_precise(""), 0)

    def test_no_precise_assertions(self):
        self.assertEqual(count_precise('assert x\nassert y is not None'), 0)

    def test_multiple_precise(self):
        text = 'assert x == 42\nassert y == "hi"\nself.assertEqual(z, 1)'
        self.assertEqual(count_precise(text), 3)


class TestPrecisionDenyInMain(unittest.TestCase):
    """Tests failing + same assertion count + precision decreased → DENY."""

    def _run_main(self, input_data):
        stdin_mock = io.StringIO(json.dumps(input_data))
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        exit_code = 0
        with patch("sys.stdin", stdin_mock), \
             patch("sys.stdout", stdout_capture), \
             patch("sys.stderr", stderr_capture):
            try:
                main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()

    @patch.object(sdd_test_guard, "read_state", return_value={"passing": False, "summary": "1 failed"})
    def test_exact_to_existence_denied(self, _mock):
        """assert x == 42 → assert x is not None: count 1→1, precise 1→0 → DENY (exit 2)."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test_foo.py",
                "old_string": "assert x == 42",
                "new_string": "assert x is not None",
            },
        })
        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("precision", stderr)

    @patch.object(sdd_test_guard, "read_state", return_value={"passing": False, "summary": "1 failed"})
    def test_exact_to_different_exact_allowed(self, _mock):
        """assert x == 42 → assert x == 43: count 1→1, precise 1→1 → ALLOW."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test_foo.py",
                "old_string": "assert x == 42",
                "new_string": "assert x == 43",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")


class TestTautologicalTests(unittest.TestCase):
    def _run_main(self, input_data):
        stdin_mock = io.StringIO(json.dumps(input_data))
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        exit_code = 0
        with patch("sys.stdin", stdin_mock), \
             patch("sys.stdout", stdout_capture), \
             patch("sys.stderr", stderr_capture):
            try:
                main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()

    def test_assert_true_addition_denied(self):
        self.assertTrue(is_tautological_test_addition("assert True"))

    def test_assert_one_equals_one_addition_denied(self):
        self.assertTrue(is_tautological_test_addition("assert 1 == 1"))

    def test_expect_true_to_be_true_addition_denied(self):
        self.assertTrue(is_tautological_test_addition("expect(true).toBe(true)"))

    def test_empty_test_function_addition_denied(self):
        self.assertTrue(
            is_tautological_test_addition("def test_placeholder():\n    pass")
        )

    def test_empty_arrow_test_addition_denied(self):
        self.assertTrue(
            is_tautological_test_addition("it('x', () => {})")
        )

    def test_pattern_inside_docstring_allowed(self):
        self.assertFalse(
            is_tautological_test_addition(
                '"""Example only:\nassert True\nexpect(true).toBe(true)\n"""'
            )
        )

    def test_removal_of_tautological_test_allowed(self):
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test_foo.py",
                "old_string": "assert True",
                "new_string": "assert result == 42",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")
        self.assertNotIn("tautological", stderr)

    def test_non_test_file_with_tautology_allowed(self):
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "src/main.py",
                "old_string": "pass",
                "new_string": "assert True",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")


class TestCriticalPathSignals(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        critical = Path(self.tmpdir) / ".claude" / "critical-paths.md"
        critical.parent.mkdir(parents=True, exist_ok=True)
        critical.write_text(
            "# Critical paths\n\n"
            "auth/**\n"
            "payments/**\n"
            "migrations/**\n"
            "*.sql\n"
            ".github/workflows/**\n"
            ".env*\n"
            "secrets/**\n",
            encoding="utf-8",
        )

    def tearDown(self):
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
                main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()

    def test_matching_path_emits_warning(self):
        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": ".github/workflows/ci.yml",
                "old_string": "",
                "new_string": "name: ci",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")
        self.assertIn(".github/workflows/ci.yml", stderr)
        self.assertIn("critical path", stderr.lower())

    def test_warning_is_non_blocking_unless_another_guard_triggers(self):
        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "auth/test_guard.py",
                "old_string": "assert value == 1",
                "new_string": "assert True",
            },
        })
        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("critical path", stderr.lower())
        self.assertIn("tautological test detected", stderr)

    def test_no_critical_paths_file_means_no_warning(self):
        shutil.rmtree(Path(self.tmpdir) / ".claude", ignore_errors=True)
        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": ".github/workflows/ci.yml",
                "old_string": "",
                "new_string": "name: ci",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")
        self.assertNotIn("critical path", stderr.lower())

    def test_multiple_patterns_each_match(self):
        patterns = load_critical_paths(self.tmpdir)
        self.assertTrue(matches_critical_path("auth/service.py", patterns))
        self.assertTrue(matches_critical_path("payments/checkout.ts", patterns))
        self.assertTrue(matches_critical_path("migrations/001_init.sql", patterns))
        self.assertTrue(matches_critical_path(".github/workflows/ci.yml", patterns))
        self.assertTrue(matches_critical_path(".env.local", patterns))
        self.assertTrue(matches_critical_path("secrets/token.txt", patterns))

    def test_comments_and_blank_lines_ignored(self):
        patterns = load_critical_paths(self.tmpdir)
        self.assertEqual(
            patterns,
            [
                "auth/**",
                "payments/**",
                "migrations/**",
                "*.sql",
                ".github/workflows/**",
                ".env*",
                "secrets/**",
            ],
        )

    @patch.object(sdd_test_guard, "read_state", return_value={"passing": False, "summary": "1 failed"})
    def test_loose_to_exact_allowed(self, _mock):
        """assert x is not None → assert x == 42: count 1→1, precise 0→1 → ALLOW."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test_foo.py",
                "old_string": "assert x is not None",
                "new_string": "assert x == 42",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    @patch.object(sdd_test_guard, "read_state", return_value={"passing": False, "summary": "1 failed"})
    def test_assertions_increased_but_precision_decreased_denies(self, _mock):
        """assert x == 42 → assert x + assert y + assert z is not None: count 1→3, precise 1→0 → DENY."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test_foo.py",
                "old_string": "assert x == 42",
                "new_string": "assert x\nassert y\nassert z is not None",
            },
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("precision", stderr)

    @patch.object(sdd_test_guard, "read_state", return_value={"passing": False, "summary": "1 failed"})
    def test_no_old_precise_allows_any_change(self, _mock):
        """No precise assertions in old → can't drop precision → ALLOW."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": "/tmp/project",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "test_foo.py",
                "old_string": "assert x is not None",
                "new_string": "assert y is not None",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")


class TestSourceOrderingGuard(unittest.TestCase):
    """PreToolUse blocks source edits when no test files in session and no test on disk."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
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
                main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()

    @patch.object(sdd_test_guard, "read_coverage", return_value={
        "source_files": ["src/a.py"], "test_files": [],
    })
    @patch.object(sdd_test_guard, "has_test_on_disk", return_value=False)
    def test_source_no_tests_no_disk_denies(self, _mock_disk, _mock_cov):
        """Source file + no test files in session + no test on disk → DENY."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "src/feature.py",
                "old_string": "pass",
                "new_string": "return 1",
            },
        })
        self.assertEqual(exit_code, 2)
        self.assertIn("SDD Guard", stderr)
        self.assertIn("write test scenarios", stderr.lower())

    @patch.object(sdd_test_guard, "read_coverage", return_value={
        "source_files": ["src/a.py"], "test_files": [],
    })
    @patch.object(sdd_test_guard, "has_test_on_disk", return_value=False)
    def test_denial_writes_guard_telemetry(self, _mock_disk, _mock_cov):
        exit_code, _stdout, _stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "src/feature.py",
                "old_string": "pass",
                "new_string": "return 1",
            },
        })
        self.assertEqual(exit_code, 2)
        metrics = Path(self.tmpdir) / ".claude" / "metrics.jsonl"
        events = [
            json.loads(line)
            for line in metrics.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        event = events[-1]
        self.assertEqual(event["event"], "guard_triggered")
        self.assertEqual(event["category"], "POLICY")
        self.assertEqual(event["tool_name"], "Edit")
        self.assertEqual(event["file_path"], "src/feature.py")

    @patch.object(sdd_test_guard, "has_test_on_disk", return_value=True)
    def test_source_test_on_disk_allows(self, _mock_disk):
        """Source file + test exists on disk → ALLOW (bug fix / refactoring)."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "src/feature.py",
                "old_string": "pass",
                "new_string": "return 1",
            },
        })
        self.assertEqual(exit_code, 0)

    @patch.object(sdd_test_guard, "read_coverage", return_value={
        "source_files": ["src/a.py"], "test_files": ["tests/test_a.py"],
    })
    @patch.object(sdd_test_guard, "has_test_on_disk", return_value=False)
    def test_source_with_session_tests_allows(self, _mock_disk, _mock_cov):
        """Source file + test files edited in session → ALLOW."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "src/feature.py",
                "old_string": "pass",
                "new_string": "return 1",
            },
        })
        self.assertEqual(exit_code, 0)

    @patch.object(sdd_test_guard, "read_coverage", return_value=None)
    @patch.object(sdd_test_guard, "has_test_on_disk", return_value=False)
    def test_source_no_coverage_state_allows(self, _mock_disk, _mock_cov):
        """Source file + no coverage state (first edit) → ALLOW (grace)."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "src/feature.py",
                "old_string": "pass",
                "new_string": "return 1",
            },
        })
        self.assertEqual(exit_code, 0)

    def test_exempt_file_not_blocked(self):
        """Exempt file (e.g. __init__.py) → ALLOW regardless of coverage."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "src/__init__.py",
                "old_string": "",
                "new_string": "from .main import foo",
            },
        })
        self.assertEqual(exit_code, 0)

    def test_non_source_file_not_blocked(self):
        """Non-source file (e.g. README.md) → ALLOW."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "README.md",
                "old_string": "# Old",
                "new_string": "# New",
            },
        })
        self.assertEqual(exit_code, 0)

    @patch.object(sdd_test_guard, "read_coverage", return_value={
        "source_files": [], "test_files": [],
    })
    @patch.object(sdd_test_guard, "has_test_on_disk", return_value=False)
    def test_empty_coverage_state_allows(self, _mock_disk, _mock_cov):
        """Coverage state exists but both lists empty → ALLOW (no meaningful edits yet)."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "src/feature.py",
                "old_string": "pass",
                "new_string": "return 1",
            },
        })
        self.assertEqual(exit_code, 0)


class TestReviewFileGuard(unittest.TestCase):
    """PreToolUse denies Write to .ralph/reviews/ without sop-reviewer."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
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
                main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()

    @patch.object(sdd_test_guard, "read_skill_invoked", return_value=None)
    def test_review_write_without_skill_denied(self, _mock):
        """Write to .ralph/reviews/ without sop-reviewer state → deny (exit 2)."""
        ralph_dir = Path(self.tmpdir) / ".ralph"
        ralph_dir.mkdir()
        (ralph_dir / "config.sh").write_text('GATE_TEST="npm test"\n', encoding="utf-8")

        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Write",
            "tool_input": {
                "file_path": f"{self.tmpdir}/.ralph/reviews/task-1-review.md",
                "content": "## Review\nLGTM",
            },
        })
        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("sop-reviewer", stderr)

    @patch.object(sdd_test_guard, "read_skill_invoked", return_value={"skill": "sop-reviewer"})
    def test_review_write_with_skill_allowed(self, _mock):
        """sop-reviewer state present → no deny output (falls through to test file check)."""
        ralph_dir = Path(self.tmpdir) / ".ralph"
        ralph_dir.mkdir()
        (ralph_dir / "config.sh").write_text('GATE_TEST="npm test"\n', encoding="utf-8")

        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Write",
            "tool_input": {
                "file_path": f"{self.tmpdir}/.ralph/reviews/task-1-review.md",
                "content": "## Review\nLGTM",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    def test_non_review_write_unaffected(self):
        """Write to src/main.py → normal flow (no deny)."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Write",
            "tool_input": {
                "file_path": f"{self.tmpdir}/src/main.py",
                "content": "print('hello')",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")

    def test_non_ralph_project_unaffected(self):
        """No .ralph/config.sh → no deny even for review path."""
        exit_code, stdout, stderr = self._run_main({
            "cwd": self.tmpdir,
            "tool_name": "Write",
            "tool_input": {
                "file_path": f"{self.tmpdir}/.ralph/reviews/task-1-review.md",
                "content": "## Review\nLGTM",
            },
        })
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")


if __name__ == "__main__":
    unittest.main()
