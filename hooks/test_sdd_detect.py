#!/usr/bin/env python3
"""Tests for _sdd_detect.py — detect_test_command() and parse_test_summary()."""
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import (
    detect_test_command, has_exit_suppression, is_test_running,
    parse_test_summary, pid_path, read_skill_invoked, read_state,
    skill_invoked_path, state_path, write_skill_invoked, write_state,
)


class TestDetectTestCommand(unittest.TestCase):
    """Test detect_test_command() with real filesystem fixtures."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # ── empty dir → None ──
    def test_empty_dir_returns_none(self):
        self.assertIsNone(detect_test_command(self.tmpdir))

    # ── package.json with test → "npm test" (unchanged) ──
    def test_package_json_with_test_script(self):
        (Path(self.tmpdir) / "package.json").write_text(
            '{"scripts": {"test": "jest"}}', encoding="utf-8"
        )
        self.assertEqual(detect_test_command(self.tmpdir), "npm test")

    def test_package_json_no_test_specified(self):
        (Path(self.tmpdir) / "package.json").write_text(
            '{"scripts": {"test": "echo \\"Error: no test specified\\" && exit 1"}}',
            encoding="utf-8",
        )
        self.assertIsNone(detect_test_command(self.tmpdir))

    # ── pyproject.toml: false positive FIX ──
    def test_pyproject_without_pytest_or_tests_returns_none(self):
        """Key fix: bare pyproject.toml no longer falsely detects pytest."""
        (Path(self.tmpdir) / "pyproject.toml").write_text(
            '[build-system]\nrequires = ["setuptools"]', encoding="utf-8"
        )
        self.assertIsNone(detect_test_command(self.tmpdir))

    def test_pyproject_with_pytest_in_content(self):
        (Path(self.tmpdir) / "pyproject.toml").write_text(
            '[tool.pytest.ini_options]\ntestpaths = ["tests"]', encoding="utf-8"
        )
        self.assertEqual(detect_test_command(self.tmpdir), "pytest")

    def test_pyproject_with_pytest_dependency(self):
        (Path(self.tmpdir) / "pyproject.toml").write_text(
            '[project.optional-dependencies]\ndev = ["pytest>=7.0"]', encoding="utf-8"
        )
        self.assertEqual(detect_test_command(self.tmpdir), "pytest")

    def test_pyproject_with_tests_dir(self):
        (Path(self.tmpdir) / "pyproject.toml").write_text(
            '[build-system]\nrequires = ["setuptools"]', encoding="utf-8"
        )
        (Path(self.tmpdir) / "tests").mkdir()
        self.assertEqual(detect_test_command(self.tmpdir), "pytest")

    def test_pyproject_with_test_dir(self):
        (Path(self.tmpdir) / "pyproject.toml").write_text(
            '[build-system]\nrequires = ["setuptools"]', encoding="utf-8"
        )
        (Path(self.tmpdir) / "test").mkdir()
        self.assertEqual(detect_test_command(self.tmpdir), "pytest")

    # ── setup.py: false positive FIX ──
    def test_setup_py_without_tests_dir_returns_none(self):
        """Key fix: bare setup.py no longer falsely detects pytest."""
        (Path(self.tmpdir) / "setup.py").write_text(
            'from setuptools import setup\nsetup(name="pkg")', encoding="utf-8"
        )
        self.assertIsNone(detect_test_command(self.tmpdir))

    def test_setup_py_with_tests_dir(self):
        (Path(self.tmpdir) / "setup.py").write_text(
            'from setuptools import setup\nsetup(name="pkg")', encoding="utf-8"
        )
        (Path(self.tmpdir) / "tests").mkdir()
        self.assertEqual(detect_test_command(self.tmpdir), "pytest")

    # ── go.mod → "go test ./..." (unchanged) ──
    def test_go_mod(self):
        (Path(self.tmpdir) / "go.mod").write_text("module example.com/m", encoding="utf-8")
        self.assertEqual(detect_test_command(self.tmpdir), "go test ./...")

    # ── Cargo.toml → "cargo test" (unchanged) ──
    def test_cargo_toml(self):
        (Path(self.tmpdir) / "Cargo.toml").write_text('[package]\nname = "p"', encoding="utf-8")
        self.assertEqual(detect_test_command(self.tmpdir), "cargo test")

    # ── Makefile: false positive FIX ──
    def test_makefile_without_test_target_returns_none(self):
        """Key fix: Makefile without test target no longer falsely detects make test."""
        (Path(self.tmpdir) / "Makefile").write_text(
            "build:\n\tgcc -o main main.c\n", encoding="utf-8"
        )
        self.assertIsNone(detect_test_command(self.tmpdir))

    def test_makefile_with_test_target(self):
        (Path(self.tmpdir) / "Makefile").write_text(
            "build:\n\tgcc -o main main.c\n\ntest:\n\tpytest\n", encoding="utf-8"
        )
        self.assertEqual(detect_test_command(self.tmpdir), "make test")

    def test_makefile_with_test_target_and_deps(self):
        (Path(self.tmpdir) / "Makefile").write_text(
            "test: build\n\t./run-tests\n", encoding="utf-8"
        )
        self.assertEqual(detect_test_command(self.tmpdir), "make test")

    # ── Priority: package.json beats pyproject.toml ──
    def test_package_json_takes_priority_over_pyproject(self):
        (Path(self.tmpdir) / "package.json").write_text(
            '{"scripts": {"test": "vitest"}}', encoding="utf-8"
        )
        (Path(self.tmpdir) / "pyproject.toml").write_text(
            '[tool.pytest.ini_options]', encoding="utf-8"
        )
        self.assertEqual(detect_test_command(self.tmpdir), "npm test")

    # ── Bug #7: lockfile-aware package manager detection ──
    def test_pnpm_lockfile_returns_pnpm_test(self):
        (Path(self.tmpdir) / "package.json").write_text(
            '{"scripts": {"test": "vitest"}}', encoding="utf-8"
        )
        (Path(self.tmpdir) / "pnpm-lock.yaml").write_text("", encoding="utf-8")
        self.assertEqual(detect_test_command(self.tmpdir), "pnpm test")

    def test_yarn_lockfile_returns_yarn_test(self):
        (Path(self.tmpdir) / "package.json").write_text(
            '{"scripts": {"test": "jest"}}', encoding="utf-8"
        )
        (Path(self.tmpdir) / "yarn.lock").write_text("", encoding="utf-8")
        self.assertEqual(detect_test_command(self.tmpdir), "yarn test")

    def test_bun_lockfile_returns_bun_test(self):
        (Path(self.tmpdir) / "package.json").write_text(
            '{"scripts": {"test": "bun:test"}}', encoding="utf-8"
        )
        (Path(self.tmpdir) / "bun.lockb").write_text("", encoding="utf-8")
        self.assertEqual(detect_test_command(self.tmpdir), "bun test")

    def test_no_lockfile_defaults_to_npm(self):
        """No lockfile present → npm test (backward compatible default)."""
        (Path(self.tmpdir) / "package.json").write_text(
            '{"scripts": {"test": "jest"}}', encoding="utf-8"
        )
        self.assertEqual(detect_test_command(self.tmpdir), "npm test")

    def test_multiple_lockfiles_bun_wins(self):
        """If multiple lockfiles exist, bun > pnpm > yarn > npm."""
        (Path(self.tmpdir) / "package.json").write_text(
            '{"scripts": {"test": "test"}}', encoding="utf-8"
        )
        (Path(self.tmpdir) / "bun.lockb").write_text("", encoding="utf-8")
        (Path(self.tmpdir) / "yarn.lock").write_text("", encoding="utf-8")
        self.assertEqual(detect_test_command(self.tmpdir), "bun test")


class TestExitSuppression(unittest.TestCase):
    """Test has_exit_suppression() regex."""

    def test_pipe_true(self):
        self.assertTrue(has_exit_suppression("npm test || true"))

    def test_pipe_colon(self):
        self.assertTrue(has_exit_suppression("npm test || :"))

    def test_pipe_exit_0(self):
        self.assertTrue(has_exit_suppression("npm test || exit 0"))

    def test_semicolon_true(self):
        self.assertTrue(has_exit_suppression("npm test; true"))

    def test_semicolon_exit_0(self):
        self.assertTrue(has_exit_suppression("npm test; exit 0"))

    def test_path_true(self):
        self.assertTrue(has_exit_suppression("npm test || /usr/bin/true"))

    def test_no_suppression(self):
        self.assertFalse(has_exit_suppression("npm test"))

    def test_and_chain(self):
        self.assertFalse(has_exit_suppression("npm test && echo done"))

    def test_pipe_to_grep(self):
        self.assertFalse(has_exit_suppression("npm test | grep passed"))


class TestParseTestSummary(unittest.TestCase):
    """Test parse_test_summary() parser."""

    def test_tap_pass_only(self):
        output = "# pass 3\n# fail 0"
        self.assertEqual(parse_test_summary(output, 0), "3 passed")

    def test_tap_with_failures(self):
        output = "# pass 2\n# fail 1"
        self.assertEqual(parse_test_summary(output, 1), "2 passed, 1 failed")

    def test_jest_format(self):
        output = "Tests: 2 passed, 1 failed, 3 total"
        self.assertIn("3 total", parse_test_summary(output, 1))

    def test_pytest_format(self):
        output = "5 passed"
        self.assertEqual(parse_test_summary(output, 0), "5 passed")

    def test_go_format(self):
        output = "ok  \tpkg/a\nok  \tpkg/b\nFAIL\tpkg/c"
        self.assertEqual(parse_test_summary(output, 1), "2 ok, 1 failed")

    def test_cargo_format(self):
        # "5 passed" matches pytest regex first — correct, summary is still accurate
        output = "test result: ok. 5 passed; 0 failed; 0 ignored"
        self.assertEqual(parse_test_summary(output, 0), "5 passed")

    def test_fallback_pass(self):
        self.assertEqual(parse_test_summary("", 0), "tests passed")

    def test_fallback_fail(self):
        self.assertEqual(parse_test_summary("", 1), "tests failed")


class TestStateIO(unittest.TestCase):
    """Test state I/O functions (state_path, pid_path, read/write_state, is_test_running)."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Clean up any state files from this test cwd
        for p in [state_path(self.tmpdir), pid_path(self.tmpdir)]:
            try:
                p.unlink()
            except FileNotFoundError:
                pass

    def tearDown(self):
        for p in [state_path(self.tmpdir), pid_path(self.tmpdir)]:
            try:
                p.unlink()
            except FileNotFoundError:
                pass
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_state_path_format(self):
        sp = state_path(self.tmpdir)
        self.assertTrue(str(sp).startswith("/tmp/sdd-test-state-"))
        self.assertTrue(str(sp).endswith(".json"))

    def test_pid_path_format(self):
        pp = pid_path(self.tmpdir)
        self.assertTrue(str(pp).startswith("/tmp/sdd-test-run-"))
        self.assertTrue(str(pp).endswith(".pid"))

    def test_read_state_missing_returns_none(self):
        self.assertIsNone(read_state(self.tmpdir))

    def test_write_then_read_roundtrip(self):
        write_state(self.tmpdir, True, "5 passed")
        state = read_state(self.tmpdir)
        self.assertIsNotNone(state)
        self.assertTrue(state["passing"])
        self.assertEqual(state["summary"], "5 passed")
        self.assertIn("timestamp", state)

    def test_is_test_running_no_pid(self):
        self.assertFalse(is_test_running(self.tmpdir))

    def test_is_test_running_stale_pid_cleans_up(self):
        pf = pid_path(self.tmpdir)
        pf.write_text("999999999")  # non-existent PID
        self.assertFalse(is_test_running(self.tmpdir))
        self.assertFalse(pf.exists(), "Stale PID file should be cleaned up")


class TestSkillInvokedPerSkill(unittest.TestCase):
    """Test per-skill state files for skill invocation tracking."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._cleanup_paths = []

    def tearDown(self):
        for p in self._cleanup_paths:
            try:
                p.unlink()
            except FileNotFoundError:
                pass
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _track(self, path):
        self._cleanup_paths.append(path)
        return path

    def test_separate_files_per_skill(self):
        p1 = self._track(skill_invoked_path(self.tmpdir, "sop-code-assist"))
        p2 = self._track(skill_invoked_path(self.tmpdir, "sop-reviewer"))
        self.assertNotEqual(str(p1), str(p2))
        self.assertIn("sop-code-assist", str(p1))
        self.assertIn("sop-reviewer", str(p2))

    def test_read_specific_skill(self):
        self._track(skill_invoked_path(self.tmpdir, "sop-code-assist"))
        self._track(skill_invoked_path(self.tmpdir, "sop-reviewer"))
        write_skill_invoked(self.tmpdir, "sop-code-assist")
        self.assertIsNotNone(read_skill_invoked(self.tmpdir, "sop-code-assist"))
        self.assertIsNone(read_skill_invoked(self.tmpdir, "sop-reviewer"))

    def test_write_does_not_clobber_other_skill(self):
        self._track(skill_invoked_path(self.tmpdir, "sop-code-assist"))
        self._track(skill_invoked_path(self.tmpdir, "sop-reviewer"))
        write_skill_invoked(self.tmpdir, "sop-code-assist")
        write_skill_invoked(self.tmpdir, "sop-reviewer")
        ca = read_skill_invoked(self.tmpdir, "sop-code-assist")
        rv = read_skill_invoked(self.tmpdir, "sop-reviewer")
        self.assertIsNotNone(ca)
        self.assertIsNotNone(rv)
        self.assertEqual(ca["skill"], "sop-code-assist")
        self.assertEqual(rv["skill"], "sop-reviewer")

    def test_default_skill_name_is_sop_code_assist(self):
        p_default = skill_invoked_path(self.tmpdir)
        p_explicit = skill_invoked_path(self.tmpdir, "sop-code-assist")
        self.assertEqual(str(p_default), str(p_explicit))


class TestReadStateTTL(unittest.TestCase):
    """Test TTL enforcement in read_state()."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        try:
            state_path(self.tmpdir).unlink()
        except FileNotFoundError:
            pass

    def tearDown(self):
        try:
            state_path(self.tmpdir).unlink()
        except FileNotFoundError:
            pass
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_fresh_state_returned(self):
        """State written just now is returned (within TTL)."""
        write_state(self.tmpdir, True, "5 passed")
        self.assertIsNotNone(read_state(self.tmpdir))

    def test_stale_state_returns_none(self):
        """State older than max_age_seconds returns None."""
        write_state(self.tmpdir, False, "1 failed")
        # Force stale timestamp
        import json, time
        sp = state_path(self.tmpdir)
        data = json.loads(sp.read_text())
        old_ts = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(time.time() - 700),  # 700s ago > 600s default
        )
        data["timestamp"] = old_ts
        sp.write_text(json.dumps(data))
        self.assertIsNone(read_state(self.tmpdir))

    def test_custom_max_age(self):
        """Custom max_age_seconds is respected."""
        write_state(self.tmpdir, True, "ok")
        # Fresh state with very short TTL (0s) → expired
        self.assertIsNone(read_state(self.tmpdir, max_age_seconds=0))

    def test_missing_timestamp_treated_as_fresh(self):
        """State without timestamp field is not expired (backward compat)."""
        import json
        sp = state_path(self.tmpdir)
        sp.write_text(json.dumps({"passing": True, "summary": "ok"}))
        self.assertIsNotNone(read_state(self.tmpdir))

    def test_max_age_zero_always_expires(self):
        """max_age_seconds=0 expires everything with a timestamp."""
        write_state(self.tmpdir, True, "ok")
        result = read_state(self.tmpdir, max_age_seconds=0)
        self.assertIsNone(result)


class TestReadSkillInvokedTTL(unittest.TestCase):
    """Test TTL enforcement in read_skill_invoked()."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._paths = []

    def tearDown(self):
        for p in self._paths:
            try:
                p.unlink()
            except FileNotFoundError:
                pass
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _track(self, skill_name):
        p = skill_invoked_path(self.tmpdir, skill_name)
        self._paths.append(p)
        return p

    def test_fresh_skill_returned(self):
        """Skill invoked just now is returned."""
        self._track("sop-code-assist")
        write_skill_invoked(self.tmpdir, "sop-code-assist")
        self.assertIsNotNone(read_skill_invoked(self.tmpdir, "sop-code-assist"))

    def test_stale_skill_returns_none(self):
        """Skill state older than max_age returns None."""
        self._track("sop-code-assist")
        write_skill_invoked(self.tmpdir, "sop-code-assist")
        # Force stale timestamp
        import json, time
        sp = skill_invoked_path(self.tmpdir, "sop-code-assist")
        data = json.loads(sp.read_text())
        old_ts = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(time.time() - 15000),  # 15000s > 14400s default
        )
        data["timestamp"] = old_ts
        sp.write_text(json.dumps(data))
        self.assertIsNone(read_skill_invoked(self.tmpdir, "sop-code-assist"))

    def test_custom_max_age(self):
        """Custom max_age_seconds is respected."""
        self._track("sop-reviewer")
        write_skill_invoked(self.tmpdir, "sop-reviewer")
        self.assertIsNone(read_skill_invoked(self.tmpdir, "sop-reviewer", max_age_seconds=0))


if __name__ == "__main__":
    unittest.main()
