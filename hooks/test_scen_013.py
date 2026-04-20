#!/usr/bin/env python3
"""SCEN-013 — Rung 1b: source edit with session-tracked tests runs those.

Factory.ai pattern: worker tests what THIS session produced. Session
state is keyed on `(cwd, sid)` — naturally isolates per-worktree in
Ralph mode, per-session in non-Ralph.

When the agent edits a source file AND the current session has
previously edited test files (tracked via `record_file_edit`), the
cascade returns a command running those session-local test files.
This avoids both full-suite and graph analysis: reuse what the worker
already invested in.

Observable isolation (Ralph):
  * Teammate W1 edits test_a.py then src/a.py → Rung 1b runs test_a.py
  * Teammate W2 (distinct sid + distinct cwd) has its own session state
  * W2 editing src/b.py does NOT pick up W1's test_a.py
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


_PY_TEST_BODY = 'def test_x():\n    assert len("abc") == 3\n'


def _write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@unittest.skipUnless(_HAS_CASCADE, f"cascade missing: {_IMPORT_ERR}")
class TestScen013Rung1bSessionTests(unittest.TestCase):
    """Rung 1b: source edit + session tests → run session's tests."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen013-")
        self._orig_enabled = _sdd_detect._sdd_config.FAST_PATH_ENABLED
        _sdd_detect._sdd_config.FAST_PATH_ENABLED = True

    def tearDown(self):
        _sdd_detect._sdd_config.FAST_PATH_ENABLED = self._orig_enabled
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _seed_session(self, sid, test_files):
        """Seed record_file_edit with test_files for (cwd, sid)."""
        for tf in test_files:
            _write(tf, _PY_TEST_BODY)
            _sdd_detect.record_file_edit(self.tmpdir, tf, sid)

    def test_source_edit_with_session_tests_runs_those(self):
        """Edit src/foo.py → cascade runs session's test files."""
        _write(Path(self.tmpdir) / "pyproject.toml",
               '[project]\nname = "p"\nversion = "0.0.1"\n')
        sid = "scen013-session"
        test_a = str(Path(self.tmpdir) / "tests" / "test_a.py")
        test_b = str(Path(self.tmpdir) / "tests" / "test_b.py")
        self._seed_session(sid, [test_a, test_b])

        source_edit = str(Path(self.tmpdir) / "src" / "foo.py")
        _write(source_edit, "def foo(): return 42\n")

        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, source_edit, sid=sid,
        )
        self.assertEqual(result["rung"], "1b",
            f"expected Rung 1b when session has tests; got {result!r}")
        self.assertIn("pytest", result["command"].lower(),
            f"expected pytest command; got: {result['command']!r}")
        # Both test files present in scoped command
        self.assertIn("test_a.py", result["command"])
        self.assertIn("test_b.py", result["command"])
        self.assertEqual(result["session_test_files_count"], 2)

    def test_source_edit_no_session_tests_not_1b(self):
        """Source edit with empty session state → not Rung 1b (falls through)."""
        _write(Path(self.tmpdir) / "pyproject.toml",
               '[project]\nname = "p"\nversion = "0.0.1"\n')
        sid = "scen013-empty"
        source_edit = str(Path(self.tmpdir) / "src" / "foo.py")
        _write(source_edit, "def foo(): return 42\n")

        result = _sdd_detect.cascade_impacted_test_command(
            self.tmpdir, source_edit, sid=sid,
        )
        self.assertNotEqual(result["rung"], "1b",
            f"without session tests, should NOT be Rung 1b; got {result!r}")

    def test_ralph_isolation_between_worktrees(self):
        """Two distinct sids + two distinct cwds have independent session state.

        Simulates Ralph teammates W1 and W2 editing in parallel worktrees.
        Verification: W1's session tests do NOT influence W2's cascade.
        """
        # W1 worktree
        w1 = Path(tempfile.mkdtemp(prefix="sdd-scen013-w1-"))
        _write(w1 / "pyproject.toml", '[project]\nname = "p"\nversion = "0.0.1"\n')
        w1_test = str(w1 / "tests" / "test_w1.py")
        _write(w1_test, _PY_TEST_BODY)
        _sdd_detect.record_file_edit(str(w1), w1_test, "sid-w1")

        # W2 worktree — DIFFERENT cwd, DIFFERENT sid
        w2 = Path(tempfile.mkdtemp(prefix="sdd-scen013-w2-"))
        _write(w2 / "pyproject.toml", '[project]\nname = "p"\nversion = "0.0.1"\n')

        try:
            # W2 teammate edits source with no session tests in W2
            w2_source = str(w2 / "src" / "b.py")
            _write(w2_source, "def b(): return 1\n")
            result_w2 = _sdd_detect.cascade_impacted_test_command(
                str(w2), w2_source, sid="sid-w2",
            )
            self.assertNotEqual(result_w2["rung"], "1b",
                "W2 must not inherit W1's session tests")
            self.assertEqual(result_w2["session_test_files_count"], 0)

            # W1 still sees its own tests
            w1_source = str(w1 / "src" / "a.py")
            _write(w1_source, "def a(): return 2\n")
            result_w1 = _sdd_detect.cascade_impacted_test_command(
                str(w1), w1_source, sid="sid-w1",
            )
            self.assertEqual(result_w1["rung"], "1b",
                "W1 with its own session tests → Rung 1b")
            self.assertIn("test_w1.py", result_w1["command"])
        finally:
            shutil.rmtree(str(w1), ignore_errors=True)
            shutil.rmtree(str(w2), ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
