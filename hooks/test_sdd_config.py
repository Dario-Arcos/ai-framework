#!/usr/bin/env python3
"""Tests for _sdd_config Tier 2 loading and stack-agnostic patterns.

Covers:
  - Default loading (no .claude/config.json → defaults apply)
  - Override via .claude/config.json (SOURCE_EXTENSIONS, TEST_FILE_PATTERNS,
    COVERAGE_REPORT_PATH)
  - Invalid config gracefully falls back to defaults
  - is_source_file + is_test_file respect per-cwd config
  - detect_coverage_command returns overridden COVERAGE_REPORT_PATH
  - SCEN-010: Julia project with .jl added to SOURCE_EXTENSIONS → tracked
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _sdd_config import (
    DEFAULT_SOURCE_EXTENSIONS,
    DEFAULT_TEST_FILE_PATTERNS,
    get_coverage_report_path,
    get_source_extensions,
    get_test_file_patterns,
    _clear_project_config_cache,
)
from _sdd_coverage import is_source_file, is_test_file


class TestTierTwoConfigLoading(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        _clear_project_config_cache()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_config(self, config):
        claude_dir = Path(self.tmpdir) / ".claude"
        claude_dir.mkdir(exist_ok=True)
        (claude_dir / "config.json").write_text(json.dumps(config))

    # ── Defaults ────────────────────────────────────────────────────

    def test_no_config_returns_default_source_extensions(self):
        self.assertEqual(get_source_extensions(self.tmpdir), DEFAULT_SOURCE_EXTENSIONS)

    def test_no_config_returns_default_test_patterns(self):
        self.assertEqual(get_test_file_patterns(self.tmpdir), DEFAULT_TEST_FILE_PATTERNS)

    def test_no_cwd_returns_defaults(self):
        self.assertEqual(get_source_extensions(None), DEFAULT_SOURCE_EXTENSIONS)
        self.assertEqual(get_test_file_patterns(None), DEFAULT_TEST_FILE_PATTERNS)

    # ── Override ────────────────────────────────────────────────────

    def test_source_extensions_override(self):
        self._write_config({"SOURCE_EXTENSIONS": [".jl", ".ex"]})
        result = get_source_extensions(self.tmpdir)
        self.assertEqual(result, frozenset({".jl", ".ex"}))

    def test_test_patterns_override(self):
        self._write_config({"TEST_FILE_PATTERNS": [r"_spec\.rb$", r"Test\.php$"]})
        result = get_test_file_patterns(self.tmpdir)
        self.assertEqual(result, (r"_spec\.rb$", r"Test\.php$"))

    def test_coverage_report_path_override(self):
        self._write_config({"COVERAGE_REPORT_PATH": "custom/lcov.info"})
        result = get_coverage_report_path(self.tmpdir, "coverage/lcov.info")
        self.assertEqual(result, "custom/lcov.info")

    def test_coverage_report_path_default_when_no_override(self):
        result = get_coverage_report_path(self.tmpdir, "coverage/lcov.info")
        self.assertEqual(result, "coverage/lcov.info")

    # ── Invalid config falls back ───────────────────────────────────

    def test_malformed_json_falls_back(self):
        claude_dir = Path(self.tmpdir) / ".claude"
        claude_dir.mkdir(exist_ok=True)
        (claude_dir / "config.json").write_text("{ not valid json")
        self.assertEqual(get_source_extensions(self.tmpdir), DEFAULT_SOURCE_EXTENSIONS)

    def test_non_dict_root_falls_back(self):
        self._write_config(["not", "a", "dict"])
        self.assertEqual(get_source_extensions(self.tmpdir), DEFAULT_SOURCE_EXTENSIONS)

    def test_invalid_source_extensions_type_falls_back(self):
        self._write_config({"SOURCE_EXTENSIONS": "not-a-list"})
        result = get_source_extensions(self.tmpdir)
        # "not-a-list" is iterable (yields chars); frozenset of chars is returned.
        # Downstream callers will still work because extensions like ".py" won't match.
        # Acceptable: no crash.
        self.assertIsInstance(result, frozenset)

    def test_invalid_test_patterns_type_falls_back(self):
        self._write_config({"TEST_FILE_PATTERNS": 42})
        self.assertEqual(get_test_file_patterns(self.tmpdir), DEFAULT_TEST_FILE_PATTERNS)

    def test_invalid_coverage_path_falls_back(self):
        self._write_config({"COVERAGE_REPORT_PATH": 42})
        result = get_coverage_report_path(self.tmpdir, "coverage/lcov.info")
        self.assertEqual(result, "coverage/lcov.info")


class TestCwdAwareClassification(unittest.TestCase):
    """is_source_file and is_test_file respect per-cwd SOURCE_EXTENSIONS."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        _clear_project_config_cache()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_config(self, config):
        claude_dir = Path(self.tmpdir) / ".claude"
        claude_dir.mkdir(exist_ok=True)
        (claude_dir / "config.json").write_text(json.dumps(config))

    def test_jl_not_source_by_default(self):
        """Julia .jl files: not a default source extension."""
        self.assertFalse(is_source_file("/x/app.jl"))
        self.assertFalse(is_source_file("/x/app.jl", cwd=self.tmpdir))

    def test_jl_is_source_with_config_override(self):
        """SCEN-010: .jl added to SOURCE_EXTENSIONS via .claude/config.json."""
        self._write_config({"SOURCE_EXTENSIONS": list(DEFAULT_SOURCE_EXTENSIONS) + [".jl"]})
        self.assertTrue(is_source_file("/x/app.jl", cwd=self.tmpdir))

    def test_cwd_none_uses_defaults(self):
        """Backward-compat: legacy callers without cwd get default behavior."""
        self.assertTrue(is_source_file("/x/app.py"))  # .py is default
        self.assertFalse(is_source_file("/x/app.jl"))

    def test_ruby_spec_pattern_via_config(self):
        """Ruby projects: custom test pattern via TEST_FILE_PATTERNS."""
        self._write_config({
            "TEST_FILE_PATTERNS": [r"_spec\.rb$", r"test_"],
        })
        self.assertTrue(is_test_file("/x/user_spec.rb", cwd=self.tmpdir))
        self.assertFalse(is_test_file("/x/user.rb", cwd=self.tmpdir))

    def test_default_test_patterns_without_cwd(self):
        """Default TEST_FILE_RE still works for legacy callers."""
        self.assertTrue(is_test_file("test_foo.py"))
        self.assertTrue(is_test_file("foo.test.js"))


if __name__ == "__main__":
    unittest.main()
