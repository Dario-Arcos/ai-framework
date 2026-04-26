"""SCEN-301 + SCEN-307 — `_sdd_coverage.is_test_file` false-positive closure.

B1 (P0): `test_` substring in TEST_FILE_RE has no boundary, so production
files like `attest_logger.py`, `prod_test_data.py` get classified as test
files and skip coverage. Fix anchors `test_` to filename start (after `/`,
`\\`, or string start).

B2 (P1): TEST_FILE_RE enumerates `test/` (singular) and `__tests__/` but
not plural `tests/`, so `tests/conftest.py`, `tests/foo.py` get
misclassified as production. Fix adds `tests/` alternative.

True-positive preservation is non-negotiable: every previously-detected
test layout must still match.
"""
import os
import sys
import unittest

# Hooks live alongside this test under hooks/; add to sys.path for stdlib import.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _sdd_coverage import is_test_file  # noqa: E402


class TestSCEN301ProductionRenameRejected(unittest.TestCase):
    """SCEN-301 (P0) — production filenames containing `test_` substring
    must NOT be classified as test files. Closes a reward-hacking surface
    where an agent renames a source file to skip coverage.
    """

    def test_attest_logger_is_production(self):
        """`attest_logger.py` — `test_` is mid-filename, not a test file."""
        self.assertFalse(is_test_file("attest_logger.py"))

    def test_fastest_loader_is_production(self):
        """`fastest_loader.py` — `test_` is mid-filename, not a test file."""
        self.assertFalse(is_test_file("fastest_loader.py"))

    def test_prod_test_data_is_production(self):
        """`prod_test_data.py` — `test_` mid-filename after `prod_`."""
        self.assertFalse(is_test_file("prod_test_data.py"))

    def test_contest_winner_is_production(self):
        """`contest_winner.py` — `test_` embedded in `contest_`."""
        self.assertFalse(is_test_file("contest_winner.py"))

    def test_attest_logger_in_subdir_is_production(self):
        """Nested production: `src/utils/attest_logger.py` still production."""
        self.assertFalse(is_test_file("src/utils/attest_logger.py"))

    def test_fastest_loader_with_backslash_is_production(self):
        """Windows-style separator: `src\\utils\\fastest_loader.py` still production."""
        self.assertFalse(is_test_file("src\\utils\\fastest_loader.py"))


class TestSCEN301TruePositivesPreserved(unittest.TestCase):
    """B1 must not weaken: every legitimate `test_` prefix still matches."""

    def test_test_login_at_root(self):
        """`test_login.py` — bare filename starts with `test_`."""
        self.assertTrue(is_test_file("test_login.py"))

    def test_test_foo_in_tests_dir(self):
        """`tests/test_foo.py` — `test_` at filename start (after `/`)."""
        self.assertTrue(is_test_file("tests/test_foo.py"))

    def test_test_helper_in_src(self):
        """`src/test_helper.py` — `test_` at filename start (after `/`)."""
        self.assertTrue(is_test_file("src/test_helper.py"))

    def test_test_logger_after_backslash(self):
        """Windows-style separator: `src\\test_logger.py` matches (filename start)."""
        self.assertTrue(is_test_file("src\\test_logger.py"))


class TestSCEN307PluralTestsDir(unittest.TestCase):
    """SCEN-307 (P1) — pytest convention `tests/` (plural) must be
    recognized as a test layout. Previously only `test/` (singular) and
    `__tests__/` were enumerated.
    """

    def test_tests_conftest_is_test(self):
        """`tests/conftest.py` — pytest convention root."""
        self.assertTrue(is_test_file("tests/conftest.py"))

    def test_tests_foo_is_test(self):
        """`tests/foo.py` — any file under plural `tests/` counts."""
        self.assertTrue(is_test_file("tests/foo.py"))

    def test_src_tests_helper_is_test(self):
        """`src/tests/helper.py` — `tests/` segment anywhere in path."""
        self.assertTrue(is_test_file("src/tests/helper.py"))


class TestSCEN307SingularStillMatches(unittest.TestCase):
    """B2 must not weaken: singular `test/` and `__tests__/` still match."""

    def test_singular_test_dir(self):
        """`test/foo.py` — singular `test/` directory still recognized."""
        self.assertTrue(is_test_file("test/foo.py"))

    def test_dunder_tests_dir(self):
        """`__tests__/foo.js` — Jest convention still recognized."""
        self.assertTrue(is_test_file("__tests__/foo.js"))

    def test_dot_test_suffix(self):
        """`foo.test.ts` — `.test.` suffix still recognized."""
        self.assertTrue(is_test_file("foo.test.ts"))

    def test_dot_spec_suffix(self):
        """`foo.spec.ts` — `.spec.` suffix still recognized."""
        self.assertTrue(is_test_file("foo.spec.ts"))

    def test_underscore_test_go(self):
        """`foo_test.go` — Go convention still recognized."""
        self.assertTrue(is_test_file("foo_test.go"))


if __name__ == "__main__":
    unittest.main()
