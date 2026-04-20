#!/usr/bin/env python3
"""SCEN-014 — Rung 2: source edit without session tests falls back to stack-native.

When the worker edits source WITHOUT having authored any tests in the
current session, the cascade has no session evidence to scope against.
Instead of silently running full-suite, Rung 2:
  1. Records an `[SDD:ORDERING]` signal in the returned dict (so the
     caller can surface the SDD violation in stderr).
  2. Falls back to the stack's native impacted command primitive:
       pytest project + testmon installed → --testmon --testmon-forceselect
       jest                               → jest --findRelatedTests <file>
       vitest                             → vitest related <file> --run
       go                                 → go test ./<pkg-of-changed-file>
       cargo                              → cargo test -p <owning-pkg>
  3. Returns None when no primitive is available → caller runs full suite (Rung 3).

This is Factory.ai-philosophy first (surface the SDD-order violation),
Microsoft-TIA second (use graph primitives only as the fallback).
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
    _IMPORT_ERR = "" if _HAS_CASCADE else "cascade missing"
except Exception as exc:  # pragma: no cover
    _sdd_detect = None
    _HAS_CASCADE = False
    _IMPORT_ERR = repr(exc)


def _write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@unittest.skipUnless(_HAS_CASCADE, f"cascade missing: {_IMPORT_ERR}")
class TestScen014Rung2StackNative(unittest.TestCase):
    """Source edit + no session tests → [SDD:ORDERING] + stack-native fallback."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen014-")
        self._orig_enabled = _sdd_detect._sdd_config.FAST_PATH_ENABLED
        _sdd_detect._sdd_config.FAST_PATH_ENABLED = True

    def tearDown(self):
        _sdd_detect._sdd_config.FAST_PATH_ENABLED = self._orig_enabled
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_jest_findRelatedTests_fallback(self):
        """Jest project + source edit + no session tests → findRelatedTests."""
        _write(Path(self.tmpdir) / "package.json",
               '{"name":"p","version":"0.0.1","devDependencies":{"jest":"^29.0.0"},"scripts":{"test":"jest"}}')
        source = str(Path(self.tmpdir) / "src" / "foo.js")
        _write(source, "export const foo = () => 42;\n")

        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, source, sid="scen014-jest",
        )
        self.assertEqual(result["rung"], "2",
            f"expected Rung 2 for source edit without session tests; got {result!r}")
        self.assertIsNotNone(result["command"])
        self.assertIn("findRelatedTests", result["command"],
            f"expected jest --findRelatedTests; got: {result['command']!r}")
        self.assertIn("foo.js", result["command"])
        self.assertTrue(result.get("ordering_warning", False),
            "Rung 2 must signal SDD-ordering violation for caller stderr")

    def test_vitest_related_fallback(self):
        """Vitest → `vitest related <file> --run`."""
        _write(Path(self.tmpdir) / "package.json",
               '{"name":"p","version":"0.0.1","devDependencies":{"vitest":"^1.0.0"},"scripts":{"test":"vitest"}}')
        source = str(Path(self.tmpdir) / "src" / "bar.ts")
        _write(source, "export const bar = () => 1;\n")

        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, source, sid="scen014-vitest",
        )
        self.assertEqual(result["rung"], "2")
        self.assertIn("related", result["command"])
        self.assertIn("bar.ts", result["command"])

    def test_go_package_scope_fallback(self):
        """Go: source edit → `go test ./<package>` (native per-package scope)."""
        _write(Path(self.tmpdir) / "go.mod", "module m\n\ngo 1.21\n")
        source = str(Path(self.tmpdir) / "pkg" / "foo" / "foo.go")
        _write(source, "package foo\n\nfunc Foo() int { return 42 }\n")

        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, source, sid="scen014-go",
        )
        self.assertEqual(result["rung"], "2")
        self.assertIn("go test", result["command"].lower())
        self.assertIn("./pkg/foo", result["command"])

    def test_cargo_package_scope_fallback(self):
        """Cargo: source edit → `cargo test -p <pkg>`."""
        _write(Path(self.tmpdir) / "Cargo.toml",
               '[package]\nname = "myproj"\nversion = "0.0.1"\nedition = "2021"\n')
        source = str(Path(self.tmpdir) / "src" / "lib.rs")
        _write(source, "pub fn hello() -> u32 { 42 }\n")

        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, source, sid="scen014-cargo",
        )
        self.assertEqual(result["rung"], "2")
        self.assertIn("cargo test", result["command"].lower())
        self.assertIn("-p", result["command"])
        self.assertIn("myproj", result["command"])

    def test_unknown_stack_returns_rung3(self):
        """Bare directory + no primitive → Rung 3."""
        source = str(Path(self.tmpdir) / "main.sh")
        _write(source, 'echo "hi"\n')
        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, source, sid="scen014-unknown",
        )
        self.assertEqual(result["rung"], "3",
            f"unknown stack must fall through to Rung 3; got {result!r}")


if __name__ == "__main__":
    unittest.main()
