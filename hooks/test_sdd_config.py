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

    def test_bare_string_source_extensions_falls_back(self):
        """Bare string (not list) → fallback to defaults.

        Prevents silent disable from char-iteration bug (Codex Phase 1 finding).
        """
        self._write_config({"SOURCE_EXTENSIONS": "not-a-list"})
        self.assertEqual(get_source_extensions(self.tmpdir), DEFAULT_SOURCE_EXTENSIONS)

    def test_invalid_extension_entries_filtered(self):
        """Extensions without leading '.' or non-string filtered; valid kept."""
        self._write_config({"SOURCE_EXTENSIONS": [".py", "nodot", "", 42, ".jl"]})
        result = get_source_extensions(self.tmpdir)
        self.assertEqual(result, frozenset({".py", ".jl"}))

    def test_all_invalid_extensions_fall_back(self):
        """If no valid extensions remain after filter, defaults apply."""
        self._write_config({"SOURCE_EXTENSIONS": ["nodot", "", 42]})
        self.assertEqual(get_source_extensions(self.tmpdir), DEFAULT_SOURCE_EXTENSIONS)

    def test_invalid_test_patterns_type_falls_back(self):
        self._write_config({"TEST_FILE_PATTERNS": 42})
        self.assertEqual(get_test_file_patterns(self.tmpdir), DEFAULT_TEST_FILE_PATTERNS)

    def test_malformed_regex_patterns_filtered(self):
        """Malformed regex (e.g. unclosed bracket) filtered; valid kept.

        Prevents re.error from crashing hooks (Codex Phase 1 finding).
        """
        self._write_config({"TEST_FILE_PATTERNS": [r"test_", r"["]})
        result = get_test_file_patterns(self.tmpdir)
        self.assertEqual(result, ("test_",))

    def test_all_malformed_patterns_fall_back(self):
        """If no valid patterns remain, defaults apply."""
        self._write_config({"TEST_FILE_PATTERNS": [r"[", r"(unclosed"]})
        self.assertEqual(get_test_file_patterns(self.tmpdir), DEFAULT_TEST_FILE_PATTERNS)

    def test_non_string_patterns_filtered(self):
        """Non-string entries in TEST_FILE_PATTERNS filtered."""
        self._write_config({"TEST_FILE_PATTERNS": ["test_", 42, None, ""]})
        result = get_test_file_patterns(self.tmpdir)
        self.assertEqual(result, ("test_",))

    def test_invalid_coverage_path_falls_back(self):
        self._write_config({"COVERAGE_REPORT_PATH": 42})
        result = get_coverage_report_path(self.tmpdir, "coverage/lcov.info")
        self.assertEqual(result, "coverage/lcov.info")


class TestCacheInvalidationCascade(unittest.TestCase):
    """_clear_project_config_cache must also clear downstream lru_caches."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        _clear_project_config_cache()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_config(self, config):
        claude_dir = Path(self.tmpdir) / ".claude"
        claude_dir.mkdir(exist_ok=True)
        (claude_dir / "config.json").write_text(json.dumps(config))

    def test_test_pattern_cache_cleared_on_reload(self):
        """Editing .claude/config.json + _clear_project_config_cache() must
        invalidate compiled regex cache in _sdd_coverage.
        """
        self._write_config({"TEST_FILE_PATTERNS": [r"foo_"]})
        self.assertTrue(is_test_file("/x/foo_file.py", cwd=self.tmpdir))
        self.assertFalse(is_test_file("/x/bar_file.py", cwd=self.tmpdir))

        # Change config
        self._write_config({"TEST_FILE_PATTERNS": [r"bar_"]})
        _clear_project_config_cache()

        # After cache clear, new pattern applies
        self.assertFalse(is_test_file("/x/foo_file.py", cwd=self.tmpdir))
        self.assertTrue(is_test_file("/x/bar_file.py", cwd=self.tmpdir))

    def test_coverage_detect_cache_cleared_on_reload(self):
        """Editing .claude/config.json COVERAGE_REPORT_PATH + cache clear must
        invalidate detect_coverage_command lru_cache.
        """
        # Create a minimal vitest project
        pkg = Path(self.tmpdir) / "package.json"
        pkg.write_text(json.dumps({"scripts": {"test": "vitest run"}}))

        from _sdd_detect import detect_coverage_command

        # First call — no override, default path
        self._write_config({})
        _clear_project_config_cache()
        result = detect_coverage_command(self.tmpdir)
        self.assertIsNotNone(result)
        self.assertEqual(result[2], "coverage/lcov.info")

        # Override path
        self._write_config({"COVERAGE_REPORT_PATH": "custom/lcov.info"})
        _clear_project_config_cache()

        # Expect new path reflected
        result2 = detect_coverage_command(self.tmpdir)
        self.assertEqual(result2[2], "custom/lcov.info")


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
