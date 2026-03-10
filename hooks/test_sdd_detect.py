#!/usr/bin/env python3
"""Tests for _sdd_detect.py — detect_test_command() and parse_test_summary()."""
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from unittest.mock import patch
from _sdd_detect import (
    acquire_runner_lock, await_test_completion, detect_test_command,
    has_exit_suppression, is_test_running, parse_test_summary, pid_path,
    read_skill_invoked, read_state, release_runner_lock, skill_invoked_path,
    state_path, has_test_on_disk, write_skill_invoked, write_state,
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
        expected = os.path.join(tempfile.gettempdir(), "sdd-test-state-")
        self.assertTrue(str(sp).startswith(expected))
        self.assertTrue(str(sp).endswith(".json"))

    def test_pid_path_format(self):
        pp = pid_path(self.tmpdir)
        expected = os.path.join(tempfile.gettempdir(), "sdd-test-run-")
        self.assertTrue(str(pp).startswith(expected))
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

    def test_is_test_running_with_lock_held(self):
        """flock held on PID file → is_test_running returns True."""
        lock_fd = acquire_runner_lock(self.tmpdir)
        self.assertIsNotNone(lock_fd)
        try:
            self.assertTrue(is_test_running(self.tmpdir))
        finally:
            release_runner_lock(lock_fd, self.tmpdir)

    def test_is_test_running_after_lock_released(self):
        """flock released → is_test_running returns False."""
        lock_fd = acquire_runner_lock(self.tmpdir)
        self.assertIsNotNone(lock_fd)
        release_runner_lock(lock_fd, self.tmpdir)
        self.assertFalse(is_test_running(self.tmpdir))


class TestRunnerLock(unittest.TestCase):
    """Test acquire_runner_lock / release_runner_lock atomicity."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        for p in [pid_path(self.tmpdir)]:
            try:
                p.unlink()
            except FileNotFoundError:
                pass

    def tearDown(self):
        for p in [pid_path(self.tmpdir)]:
            try:
                p.unlink()
            except FileNotFoundError:
                pass
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_acquire_returns_fd(self):
        fd = acquire_runner_lock(self.tmpdir)
        self.assertIsNotNone(fd)
        release_runner_lock(fd, self.tmpdir)

    def test_acquire_writes_pid(self):
        fd = acquire_runner_lock(self.tmpdir)
        try:
            pf = pid_path(self.tmpdir)
            pid = int(pf.read_text().strip())
            self.assertEqual(pid, os.getpid())
        finally:
            release_runner_lock(fd, self.tmpdir)

    def test_second_acquire_returns_none(self):
        """Second acquire while first holds lock → None (rejected)."""
        fd1 = acquire_runner_lock(self.tmpdir)
        self.assertIsNotNone(fd1)
        try:
            fd2 = acquire_runner_lock(self.tmpdir)
            self.assertIsNone(fd2, "Second acquire should fail while lock is held")
        finally:
            release_runner_lock(fd1, self.tmpdir)

    def test_acquire_after_release_succeeds(self):
        """After release, a new acquire should succeed."""
        fd1 = acquire_runner_lock(self.tmpdir)
        release_runner_lock(fd1, self.tmpdir)
        fd2 = acquire_runner_lock(self.tmpdir)
        self.assertIsNotNone(fd2)
        release_runner_lock(fd2, self.tmpdir)

    def test_release_leaves_pid_file(self):
        """PID file persists after release — cleaned by is_test_running probe."""
        fd = acquire_runner_lock(self.tmpdir)
        pf = pid_path(self.tmpdir)
        self.assertTrue(pf.exists())
        release_runner_lock(fd, self.tmpdir)
        self.assertTrue(pf.exists(), "PID file should persist (cleaned by probe)")
        # Probe cleans it up
        self.assertFalse(is_test_running(self.tmpdir))
        self.assertFalse(pf.exists(), "Probe should clean stale PID file")

    def test_release_none_is_noop(self):
        """release_runner_lock(None, cwd) should not raise."""
        release_runner_lock(None, self.tmpdir)

    def test_release_sentinel_cleans_pid(self):
        """release_runner_lock(-1, cwd) handles Windows sentinel."""
        pf = pid_path(self.tmpdir)
        pf.write_text("12345")
        release_runner_lock(-1, self.tmpdir)
        self.assertFalse(pf.exists())


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


class TestAwaitTestCompletion(unittest.TestCase):
    """Test await_test_completion() polling and timeout behavior."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch("_sdd_detect.time.sleep")
    @patch("_sdd_detect.is_test_running")
    def test_polls_until_worker_finishes(self, mock_running, mock_sleep):
        """Worker running 3 polls then stops → returns read_state()."""
        mock_running.side_effect = [True, True, True, False]
        write_state(self.tmpdir, True, "5 passed")
        result = await_test_completion(self.tmpdir, timeout=30)
        self.assertIsNotNone(result)
        self.assertTrue(result["passing"])
        self.assertEqual(mock_sleep.call_count, 3)

    @patch("_sdd_detect.time.monotonic")
    @patch("_sdd_detect.time.sleep")
    @patch("_sdd_detect.is_test_running", return_value=True)
    def test_timeout_returns_none(self, mock_running, mock_sleep, mock_mono):
        """Worker never finishes → returns None after timeout."""
        # monotonic: start=0, then always past deadline
        mock_mono.side_effect = [0.0, 31.0]
        result = await_test_completion(self.tmpdir, timeout=30)
        self.assertIsNone(result)


class TestRerunMarker(unittest.TestCase):
    """Test rerun marker primitives for coalescing worker."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_write_and_has(self):
        from _sdd_detect import write_rerun_marker, has_rerun_marker
        self.assertFalse(has_rerun_marker(self.tmpdir))
        write_rerun_marker(self.tmpdir)
        self.assertTrue(has_rerun_marker(self.tmpdir))

    def test_clear(self):
        from _sdd_detect import write_rerun_marker, has_rerun_marker, clear_rerun_marker
        write_rerun_marker(self.tmpdir)
        clear_rerun_marker(self.tmpdir)
        self.assertFalse(has_rerun_marker(self.tmpdir))

    def test_clear_when_not_exists(self):
        from _sdd_detect import clear_rerun_marker
        clear_rerun_marker(self.tmpdir)  # Should not raise

    def test_marker_is_project_scoped(self):
        """Same cwd always produces the same marker path."""
        from _sdd_detect import rerun_marker_path
        p1 = rerun_marker_path(self.tmpdir)
        p2 = rerun_marker_path(self.tmpdir)
        self.assertEqual(p1, p2)
        # No sid in path
        self.assertNotIn("sid", str(p1))


class TestTestExistsOnDisk(unittest.TestCase):
    """Test has_test_on_disk() convention-based lookup."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_test_returns_false(self):
        src = os.path.join(self.tmpdir, "src")
        os.makedirs(src)
        Path(src, "main.py").write_text("pass", encoding="utf-8")
        self.assertFalse(has_test_on_disk("src/main.py", self.tmpdir))

    def test_python_test_prefix(self):
        src = os.path.join(self.tmpdir, "src")
        os.makedirs(src)
        Path(src, "main.py").write_text("pass", encoding="utf-8")
        Path(src, "test_main.py").write_text("pass", encoding="utf-8")
        self.assertTrue(has_test_on_disk("src/main.py", self.tmpdir))

    def test_python_test_suffix(self):
        src = os.path.join(self.tmpdir, "src")
        os.makedirs(src)
        Path(src, "main.py").write_text("pass", encoding="utf-8")
        Path(src, "main_test.py").write_text("pass", encoding="utf-8")
        self.assertTrue(has_test_on_disk("src/main.py", self.tmpdir))

    def test_ts_test_file(self):
        src = os.path.join(self.tmpdir, "src")
        os.makedirs(src)
        Path(src, "service.ts").write_text("", encoding="utf-8")
        Path(src, "service.test.ts").write_text("", encoding="utf-8")
        self.assertTrue(has_test_on_disk("src/service.ts", self.tmpdir))

    def test_ts_spec_file(self):
        src = os.path.join(self.tmpdir, "src")
        os.makedirs(src)
        Path(src, "service.ts").write_text("", encoding="utf-8")
        Path(src, "service.spec.ts").write_text("", encoding="utf-8")
        self.assertTrue(has_test_on_disk("src/service.ts", self.tmpdir))

    def test_dunder_tests_dir(self):
        src = os.path.join(self.tmpdir, "src")
        tests = os.path.join(src, "__tests__")
        os.makedirs(tests)
        Path(src, "Button.tsx").write_text("", encoding="utf-8")
        Path(tests, "Button.test.tsx").write_text("", encoding="utf-8")
        self.assertTrue(has_test_on_disk("src/Button.tsx", self.tmpdir))

    def test_project_level_tests_dir(self):
        src = os.path.join(self.tmpdir, "src")
        tests = os.path.join(self.tmpdir, "tests")
        os.makedirs(src)
        os.makedirs(tests)
        Path(src, "foo.py").write_text("pass", encoding="utf-8")
        Path(tests, "test_foo.py").write_text("pass", encoding="utf-8")
        self.assertTrue(has_test_on_disk("src/foo.py", self.tmpdir))

    def test_go_test_file(self):
        pkg = os.path.join(self.tmpdir, "pkg")
        os.makedirs(pkg)
        Path(pkg, "handler.go").write_text("", encoding="utf-8")
        Path(pkg, "handler_test.go").write_text("", encoding="utf-8")
        self.assertTrue(has_test_on_disk("pkg/handler.go", self.tmpdir))

    def test_no_match_different_stem(self):
        src = os.path.join(self.tmpdir, "src")
        os.makedirs(src)
        Path(src, "foo.py").write_text("pass", encoding="utf-8")
        Path(src, "test_bar.py").write_text("pass", encoding="utf-8")
        self.assertFalse(has_test_on_disk("src/foo.py", self.tmpdir))


class TestDetectTestCommandCache(unittest.TestCase):
    """Test file-based caching for detect_test_command()."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Clear any cached state
        from _sdd_detect import project_hash, _tmp
        self.cache_path = _tmp(f"sdd-test-cmd-{project_hash(self.tmpdir)}.json")
        try:
            self.cache_path.unlink()
        except FileNotFoundError:
            pass

    def tearDown(self):
        try:
            self.cache_path.unlink()
        except FileNotFoundError:
            pass
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_detect_test_command_caches_result(self):
        """Second call returns cached result without re-scanning filesystem."""
        # Use go.mod — not tracked by mtime invalidation (only config.sh/package.json are)
        (Path(self.tmpdir) / "go.mod").write_text("module example.com/m", encoding="utf-8")
        result1 = detect_test_command(self.tmpdir)
        self.assertEqual(result1, "go test ./...")
        # Cache file should exist
        self.assertTrue(self.cache_path.exists())
        # Remove go.mod — cached result persists (mtime keys unchanged)
        (Path(self.tmpdir) / "go.mod").unlink()
        result2 = detect_test_command(self.tmpdir)
        self.assertEqual(result2, "go test ./...")

    def test_detect_test_command_cache_invalidates_on_mtime(self):
        """Cache invalidated when package.json mtime changes."""
        import json as json_mod
        pkg = Path(self.tmpdir) / "package.json"
        pkg.write_text('{"scripts": {"test": "jest"}}', encoding="utf-8")
        detect_test_command(self.tmpdir)  # populate cache
        self.assertTrue(self.cache_path.exists())
        # Force cache to have old pkg_mtime
        cache_data = json_mod.loads(self.cache_path.read_text())
        cache_data["pkg_mtime"] = 0.0
        self.cache_path.write_text(json_mod.dumps(cache_data))
        # Should re-detect (cache invalidated)
        result = detect_test_command(self.tmpdir)
        self.assertEqual(result, "npm test")

    def test_detect_test_command_cache_invalidates_on_ttl(self):
        """Cache invalidated when TTL expires."""
        import json as json_mod
        (Path(self.tmpdir) / "go.mod").write_text("module example.com/m", encoding="utf-8")
        detect_test_command(self.tmpdir)  # populate cache
        # Force expired TTL
        cache_data = json_mod.loads(self.cache_path.read_text())
        cache_data["detected_at"] = 0.0  # epoch = very old
        self.cache_path.write_text(json_mod.dumps(cache_data))
        # Should re-detect
        result = detect_test_command(self.tmpdir)
        self.assertEqual(result, "go test ./...")

    def test_detect_test_command_cache_handles_missing_file(self):
        """Missing cache file doesn't crash — falls through to detection."""
        (Path(self.tmpdir) / "Cargo.toml").write_text('[package]\nname = "p"', encoding="utf-8")
        # No cache file exists
        result = detect_test_command(self.tmpdir)
        self.assertEqual(result, "cargo test")

    def test_detect_test_command_cache_handles_corrupt_file(self):
        """Corrupt cache file doesn't crash — falls through to detection."""
        (Path(self.tmpdir) / "go.mod").write_text("module example.com/m", encoding="utf-8")
        self.cache_path.write_text("not json at all")
        result = detect_test_command(self.tmpdir)
        self.assertEqual(result, "go test ./...")


class TestParseUtcTimestamp(unittest.TestCase):
    """Test _parse_utc_timestamp() helper."""

    def test_valid_timestamp(self):
        from _sdd_detect import _parse_utc_timestamp
        result = _parse_utc_timestamp("2026-01-15T10:30:00Z")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)

    def test_invalid_format(self):
        from _sdd_detect import _parse_utc_timestamp
        self.assertIsNone(_parse_utc_timestamp("not-a-timestamp"))

    def test_none_input(self):
        from _sdd_detect import _parse_utc_timestamp
        self.assertIsNone(_parse_utc_timestamp(None))

    def test_empty_string(self):
        from _sdd_detect import _parse_utc_timestamp
        self.assertIsNone(_parse_utc_timestamp(""))


class TestReadJsonWithTtl(unittest.TestCase):
    """Test _read_json_with_ttl() helper."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_fresh_data_returned(self):
        import json as json_mod, time as time_mod
        from _sdd_detect import _read_json_with_ttl
        p = Path(self.tmpdir) / "test.json"
        data = {"value": 42, "timestamp": time_mod.strftime("%Y-%m-%dT%H:%M:%SZ", time_mod.gmtime())}
        p.write_text(json_mod.dumps(data))
        result = _read_json_with_ttl(p, max_age_seconds=600)
        self.assertIsNotNone(result)
        self.assertEqual(result["value"], 42)

    def test_expired_data_returns_none(self):
        import json as json_mod, time as time_mod
        from _sdd_detect import _read_json_with_ttl
        p = Path(self.tmpdir) / "test.json"
        old_ts = time_mod.strftime("%Y-%m-%dT%H:%M:%SZ", time_mod.gmtime(time_mod.time() - 7200))
        data = {"value": 42, "timestamp": old_ts}
        p.write_text(json_mod.dumps(data))
        result = _read_json_with_ttl(p, max_age_seconds=600)
        self.assertIsNone(result)

    def test_missing_file_returns_none(self):
        from _sdd_detect import _read_json_with_ttl
        p = Path(self.tmpdir) / "nonexistent.json"
        self.assertIsNone(_read_json_with_ttl(p, max_age_seconds=600))

    def test_corrupt_file_returns_none(self):
        from _sdd_detect import _read_json_with_ttl
        p = Path(self.tmpdir) / "corrupt.json"
        p.write_text("not json")
        self.assertIsNone(_read_json_with_ttl(p, max_age_seconds=600))


class TestWriteJsonAtomic(unittest.TestCase):
    """Test _write_json_atomic() helper."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_roundtrip(self):
        import json as json_mod
        from _sdd_detect import _write_json_atomic
        p = Path(self.tmpdir) / "output.json"
        _write_json_atomic(p, {"key": "value"})
        self.assertTrue(p.exists())
        data = json_mod.loads(p.read_text())
        self.assertEqual(data["key"], "value")

    def test_atomic_overwrite(self):
        import json as json_mod
        from _sdd_detect import _write_json_atomic
        p = Path(self.tmpdir) / "output.json"
        _write_json_atomic(p, {"v": 1})
        _write_json_atomic(p, {"v": 2})
        data = json_mod.loads(p.read_text())
        self.assertEqual(data["v"], 2)


if __name__ == "__main__":
    unittest.main()
