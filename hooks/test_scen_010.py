#!/usr/bin/env python3
"""SCEN-010 — Tier 2 config: stack-agnostic extension via `.claude/config.json`.

From SPEC Section 5 (Phase 1 scope):
    Project adds `.jl` to SOURCE_EXTENSIONS via `.claude/config.json` →
    Julia files tracked in coverage state without plugin code change.

The stack-agnosticism principle (SPEC 3.6) forbids hardcoded stack knowledge
outside the `detect_*` functions. Tier 2 per-project config is the escape
hatch for unusual stacks (Julia, Elixir, Crystal, Dart, etc.) — the project
declares its extensions and patterns, and the plugin honors them without
any framework edit.

This file locks in the contract end-to-end: config.json → get_source_extensions
→ is_source_file → record_file_edit writes the Julia file into the source
set for coverage tracking.

Green today — Phase 1 already shipped the Tier 2 config infrastructure.
Regressions here would mean a stack-agnosticism violation slipped in.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _sdd_config as config
import _sdd_coverage as coverage
import _sdd_state as state


class TestScen010JuliaViaConfig(unittest.TestCase):
    """End-to-end: config.json adds .jl → Julia files become first-class sources."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="scen010-")
        (Path(self.tmpdir) / ".claude").mkdir()
        # Important: cache invalidation — other tests may have populated the
        # per-cwd config cache for previous tmpdirs. Clearing here ensures
        # this test starts from a clean slate.
        config._clear_project_config_cache()

    def tearDown(self):
        config._clear_project_config_cache()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_config(self, data):
        cfg = Path(self.tmpdir) / ".claude" / "config.json"
        cfg.write_text(json.dumps(data), encoding="utf-8")

    def test_defaults_do_not_include_jl(self):
        """Precondition: .jl is not in the shipped defaults; projects must opt in."""
        self.assertNotIn(".jl", config.DEFAULT_SOURCE_EXTENSIONS,
            "If .jl becomes a default, this scenario no longer proves "
            "stack-agnostic opt-in — refresh the test.")

    def test_config_override_adds_jl(self):
        """Project config with .jl listed → get_source_extensions includes it."""
        self._write_config({"SOURCE_EXTENSIONS": [".py", ".jl"]})
        exts = config.get_source_extensions(self.tmpdir)
        self.assertIn(".jl", exts)
        self.assertIn(".py", exts)

    def test_is_source_file_recognizes_jl_with_config(self):
        """`is_source_file("foo.jl", cwd)` → True when .jl is in the config."""
        self._write_config({"SOURCE_EXTENSIONS": [".jl"]})
        self.assertTrue(coverage.is_source_file("src/app.jl", cwd=self.tmpdir))
        # Without cwd, defaults are used → .jl not tracked
        self.assertFalse(coverage.is_source_file("src/app.jl"))

    def test_record_file_edit_stores_julia_in_coverage_set(self):
        """Full path: config → is_source_file → record_file_edit writes to
        the coverage state's source_files set.
        """
        self._write_config({"SOURCE_EXTENSIONS": [".jl"]})
        sid = state.extract_session_id({"session_id": "julia-sess"})
        coverage.record_file_edit(self.tmpdir, "src/solver.jl", sid=sid)
        coverage.record_file_edit(self.tmpdir, "test/test_solver.jl", sid=sid)

        data = coverage.read_coverage(self.tmpdir, sid=sid)
        self.assertIsNotNone(data, "coverage state must be written")
        self.assertIn("src/solver.jl", data.get("source_files", []))

    def test_invalid_override_falls_back_to_defaults(self):
        """Malformed config (non-list SOURCE_EXTENSIONS) must NOT break the
        project — defaults are used instead of crashing the hook.
        """
        self._write_config({"SOURCE_EXTENSIONS": ".jl"})  # bare string: invalid
        self.assertEqual(
            config.get_source_extensions(self.tmpdir),
            config.DEFAULT_SOURCE_EXTENSIONS,
        )

    def test_cross_stack_coexistence(self):
        """Project with Julia + Elixir + Dart extensions all coexist."""
        self._write_config({"SOURCE_EXTENSIONS": [".jl", ".ex", ".exs", ".dart"]})
        for path in ("app.jl", "app.ex", "app.exs", "main.dart"):
            self.assertTrue(
                coverage.is_source_file(path, cwd=self.tmpdir),
                f"{path} must be recognized under Tier 2 config",
            )
        # Files outside the declared set are not tracked
        self.assertFalse(coverage.is_source_file("app.go", cwd=self.tmpdir))


if __name__ == "__main__":
    unittest.main()
