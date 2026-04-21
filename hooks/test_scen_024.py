#!/usr/bin/env python3
"""SCEN-024 - pytest detection via package.json scripts.test (npm shim).

Phase 9.5 correctness. Discovered when invoking /mission-report on
ai-framework itself: the cascade returned Rung 3 (full suite) for
every edit even though FAST_PATH_ENABLED=True, because
_detect_test_framework fell through to None.

Root cause: the detector checked package.json for vitest/jest and
then Python manifests (pyproject.toml / pytest.ini / setup.py), but
never inspected package.json.scripts.test for a pytest invocation.
Projects like ai-framework that use npm as a task runner
(scripts.test = 'python3 -m pytest hooks/ -q') have neither vitest
nor a Python manifest, so detection silently failed. Result: Phase 8
default flip (Phase 8.1) was observably a no-op on these projects.

Fix: after the vitest/jest checks, inspect scripts.test for 'pytest'
and return 'pytest' so the cascade produces 'pytest {rel}' commands.
This closes the detection gap without changing behavior on projects
that already had proper detection (pyproject/pytest.ini/setup.py
still win when present, and the vitest/jest order is preserved).

Observable contract:
  - Fixture project with package.json scripts.test='pytest ...' AND
    no Python manifest → _detect_test_framework returns 'pytest'
  - cascade on a test file → Rung 1a with 'pytest {rel}' command
  - Projects with vitest still detect as vitest (regression guard)
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
    _HAS_DETECT_FW = hasattr(_sdd_detect, "_detect_test_framework")
    _IMPORT_ERR = "" if _HAS_DETECT_FW else "missing _detect_test_framework"
except Exception as exc:  # pragma: no cover
    _sdd_detect = None
    _HAS_DETECT_FW = False
    _IMPORT_ERR = repr(exc)


@unittest.skipUnless(_HAS_DETECT_FW, f"cascade missing: {_IMPORT_ERR}")
class TestScen024PytestViaNpmShim(unittest.TestCase):
    """pytest detection when scripts.test invokes python -m pytest."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen024-")
        self._orig = _sdd_detect._sdd_config.FAST_PATH_ENABLED
        _sdd_detect._sdd_config.FAST_PATH_ENABLED = True

    def tearDown(self):
        _sdd_detect._sdd_config.FAST_PATH_ENABLED = self._orig
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write(self, rel, content):
        path = Path(self.tmpdir) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_scripts_test_pytest_detects_pytest(self):
        """package.json scripts.test='pytest ...' -> _detect_test_framework='pytest'.

        No pyproject/pytest.ini/setup.py present. This is the ai-framework
        shape: npm drives pytest. Before fix: returned None -> cascade
        fell to Rung 3 silently. After fix: returns 'pytest'.
        """
        self._write(
            "package.json",
            '{"name":"p","version":"0.0.1",'
            '"scripts":{"test":"python3 -m pytest hooks/ -q"}}',
        )
        result = _sdd_detect._detect_test_framework(self.tmpdir)
        self.assertEqual(
            result, "pytest",
            f"npm-shimmed pytest must be detected as 'pytest'; "
            f"got {result!r}. This is the ai-framework scenario.",
        )

    def test_scripts_test_pytest_cascade_rung_1a(self):
        """End-to-end: test-file edit on npm-shimmed pytest project -> Rung 1a."""
        self._write(
            "package.json",
            '{"name":"p","version":"0.0.1",'
            '"scripts":{"test":"python3 -m pytest hooks/ -q"}}',
        )
        self._write("hooks/test_feature.py",
                    'def test_x():\n    assert len("ab") == 2\n')
        test_file = str(Path(self.tmpdir) / "hooks" / "test_feature.py")
        r = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, test_file, sid="scen024",
        )
        self.assertEqual(
            r["rung"], "1a",
            f"Test file on npm-shimmed pytest project must cascade to "
            f"Rung 1a, not Rung 3. Got: {r}",
        )
        self.assertIsNotNone(r["command"])
        self.assertIn("pytest", r["command"])

    def test_vitest_still_wins_over_pytest_in_scripts(self):
        """Regression guard: vitest in deps AND pytest in scripts -> vitest.

        Priority order preserved (vitest/jest before pytest) so projects
        that have Python tooling for tangential scripts but vitest as the
        primary test runner still detect correctly.
        """
        self._write(
            "package.json",
            '{"name":"p","version":"0.0.1",'
            '"scripts":{"test":"vitest run","misc":"pytest"},'
            '"devDependencies":{"vitest":"^1.0"}}',
        )
        result = _sdd_detect._detect_test_framework(self.tmpdir)
        self.assertEqual(result, "vitest")

    def test_pyproject_toml_still_detects_pytest(self):
        """Regression guard: projects with pyproject.toml still detect pytest."""
        self._write("pyproject.toml",
                    '[project]\nname="p"\nversion="0.0.1"\n')
        result = _sdd_detect._detect_test_framework(self.tmpdir)
        self.assertEqual(result, "pytest")

    def test_no_manifest_still_returns_none(self):
        """Regression guard: completely empty project -> None (no crash)."""
        result = _sdd_detect._detect_test_framework(self.tmpdir)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
