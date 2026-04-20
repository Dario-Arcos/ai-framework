#!/usr/bin/env python3
"""SCEN-015 — Forced Rung 3: lockfile/config edits bypass cascade.

Mirrors Microsoft Azure TIA's fall-back-to-all pattern for non-managed
code. A decade of production data: lockfile and stack-config edits can
invalidate any test through dependency resolution or runtime assumptions
the test runner cannot self-detect. Better a cheap full-suite run than
a silently missed regression.

Observable: when the changed file's basename is in
`FAST_PATH_FORCE_FULL_FILES`, cascade returns `rung="3"` with
`forced_full_reason` set to "lockfile" or "config". Caller falls back
to full-suite via `detect_test_command(cwd)`.
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
class TestScen015ForcedFullTriggers(unittest.TestCase):
    """Lockfile + config edits force Rung 3 regardless of session state."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen015-")
        self._orig_enabled = _sdd_detect._sdd_config.FAST_PATH_ENABLED
        _sdd_detect._sdd_config.FAST_PATH_ENABLED = True

    def tearDown(self):
        _sdd_detect._sdd_config.FAST_PATH_ENABLED = self._orig_enabled
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_package_lock_forces_full(self):
        _write(Path(self.tmpdir) / "package.json",
               '{"name":"p","version":"0.0.1"}')
        lockfile = str(Path(self.tmpdir) / "package-lock.json")
        _write(lockfile, '{}')
        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, lockfile, sid="scen015-npm",
        )
        self.assertEqual(result["rung"], "3")
        self.assertEqual(result["forced_full_reason"], "lockfile")
        self.assertIsNone(result["command"],
            "Rung 3 must return None so caller uses detect_test_command()")

    def test_cargo_lock_forces_full(self):
        _write(Path(self.tmpdir) / "Cargo.toml",
               '[package]\nname = "p"\nversion = "0.0.1"\nedition = "2021"\n')
        lockfile = str(Path(self.tmpdir) / "Cargo.lock")
        _write(lockfile, "")
        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, lockfile, sid="scen015-cargo",
        )
        self.assertEqual(result["rung"], "3")
        self.assertEqual(result["forced_full_reason"], "lockfile")

    def test_pyproject_forces_full(self):
        pyp = str(Path(self.tmpdir) / "pyproject.toml")
        _write(pyp, '[project]\nname = "p"\nversion = "0.0.1"\n')
        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, pyp, sid="scen015-pyproject",
        )
        self.assertEqual(result["rung"], "3")
        self.assertEqual(result["forced_full_reason"], "config")

    def test_tsconfig_forces_full(self):
        _write(Path(self.tmpdir) / "package.json", '{"name":"p","version":"0.0.1"}')
        tsc = str(Path(self.tmpdir) / "tsconfig.json")
        _write(tsc, '{"compilerOptions":{"strict":true}}')
        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, tsc, sid="scen015-tsconfig",
        )
        self.assertEqual(result["rung"], "3")
        self.assertEqual(result["forced_full_reason"], "config")

    def test_jest_config_forces_full(self):
        _write(Path(self.tmpdir) / "package.json",
               '{"name":"p","version":"0.0.1","devDependencies":{"jest":"^29.0.0"},"scripts":{"test":"jest"}}')
        jc = str(Path(self.tmpdir) / "jest.config.js")
        _write(jc, 'module.exports = {};\n')
        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, jc, sid="scen015-jest-cfg",
        )
        self.assertEqual(result["rung"], "3")
        self.assertEqual(result["forced_full_reason"], "config")


if __name__ == "__main__":
    unittest.main()
