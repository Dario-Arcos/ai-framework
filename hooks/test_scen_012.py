#!/usr/bin/env python3
"""SCEN-012 — Rung 1a: edit on test file runs THAT test file only.

Factory.ai pattern: worker validates what they just wrote. Cheapest
possible per-edit signal. The cascade function recognizes that the
changed file is itself a test and returns a command scoped to that
single file — no graph analysis, no global run, no session lookup.

Stacks supported (via detected test framework):
  - Python pytest → `pytest <file>`
  - Vitest       → `vitest run <file>`
  - Jest         → `jest <file>`
  - Go           → `go test <package>` (Go tests are package-scoped)
"""
import importlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    _sdd_detect = importlib.import_module("_sdd_detect")
    _HAS_CASCADE = hasattr(_sdd_detect, "cascade_impacted_test_command")
    _IMPORT_ERR = "" if _HAS_CASCADE else "cascade_impacted_test_command missing"
except Exception as exc:  # pragma: no cover
    _sdd_detect = None
    _HAS_CASCADE = False
    _IMPORT_ERR = repr(exc)


def _write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# Non-tautological fixture test bodies (sidestep our own tautological detector)
_PY_TEST_BODY = 'def test_x():\n    assert len("abc") == 3\n'
_TS_TEST_BODY = (
    "import {test,expect} from 'vitest';\n"
    "test('x', () => { expect('abc'.length).toBe(3); });\n"
)
_GO_TEST_BODY = (
    "package foo\n\n"
    "import \"testing\"\n\n"
    "func TestX(t *testing.T) {\n"
    "  if len(\"abc\") != 3 { t.Fatal(\"fail\") }\n"
    "}\n"
)


@unittest.skipUnless(_HAS_CASCADE, f"cascade missing: {_IMPORT_ERR}")
class TestScen012Rung1aTestFileEdit(unittest.TestCase):
    """Edit on test file → Rung 1a: run that test only."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen012-")
        self._orig_enabled = _sdd_detect._sdd_config.FAST_PATH_ENABLED
        _sdd_detect._sdd_config.FAST_PATH_ENABLED = True

    def tearDown(self):
        _sdd_detect._sdd_config.FAST_PATH_ENABLED = self._orig_enabled
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_pytest_test_file_edit_scopes_to_file(self):
        _write(Path(self.tmpdir) / "pyproject.toml",
               '[project]\nname = "p"\nversion = "0.0.1"\n')
        test_file = str(Path(self.tmpdir) / "tests" / "test_foo.py")
        _write(test_file, _PY_TEST_BODY)

        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, test_file, sid="scen012-pytest",
        )
        self.assertEqual(result["rung"], "1a",
            f"expected Rung 1a for test-file edit; got {result!r}")
        self.assertIn("pytest", result["command"].lower(),
            f"expected pytest in command; got: {result['command']!r}")
        self.assertIn("test_foo.py", result["command"],
            f"expected scoped to test_foo.py; got: {result['command']!r}")
        self.assertIsNone(result.get("forced_full_reason"))

    def test_vitest_test_file_edit_scopes_to_file(self):
        _write(Path(self.tmpdir) / "package.json",
               '{"name":"p","version":"0.0.1","devDependencies":{"vitest":"^1.0.0"},"scripts":{"test":"vitest"}}')
        test_file = str(Path(self.tmpdir) / "tests" / "foo.test.ts")
        _write(test_file, _TS_TEST_BODY)

        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, test_file, sid="scen012-vitest",
        )
        self.assertEqual(result["rung"], "1a")
        self.assertIn("vitest", result["command"].lower(),
            f"expected vitest; got: {result['command']!r}")
        self.assertIn("foo.test.ts", result["command"])

    def test_go_test_file_edit_scopes_to_package(self):
        _write(Path(self.tmpdir) / "go.mod", "module m\n\ngo 1.21\n")
        test_file = str(Path(self.tmpdir) / "pkg" / "foo" / "foo_test.go")
        _write(test_file, _GO_TEST_BODY)

        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, test_file, sid="scen012-go",
        )
        self.assertEqual(result["rung"], "1a")
        self.assertIn("go test", result["command"].lower())
        self.assertIn("./pkg/foo", result["command"],
            f"expected package path scope; got: {result['command']!r}")

    def test_non_test_file_returns_not_1a(self):
        _write(Path(self.tmpdir) / "pyproject.toml",
               '[project]\nname = "p"\nversion = "0.0.1"\n')
        source_file = str(Path(self.tmpdir) / "src" / "foo.py")
        _write(source_file, "def foo(): return 42\n")

        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, source_file, sid="scen012-src",
        )
        self.assertNotEqual(result["rung"], "1a",
            f"source-file edit must not be classified as Rung 1a; got {result!r}")

    def test_fast_path_disabled_returns_rung3(self):
        _sdd_detect._sdd_config.FAST_PATH_ENABLED = False
        _write(Path(self.tmpdir) / "pyproject.toml",
               '[project]\nname = "p"\nversion = "0.0.1"\n')
        test_file = str(Path(self.tmpdir) / "tests" / "test_foo.py")
        _write(test_file, _PY_TEST_BODY)

        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, test_file, sid="scen012-disabled",
        )
        self.assertEqual(result["rung"], "3",
            f"FAST_PATH_ENABLED=False must force Rung 3; got {result!r}")


if __name__ == "__main__":
    unittest.main()
