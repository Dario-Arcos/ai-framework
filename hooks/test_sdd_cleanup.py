"""Tests for SDD temp file cleanup in session-start.py.

Scenarios:
1. Stale PID file with dead process → removed by age
2. Old PID file → removed by age (no SIGTERM — flock handles concurrency)
3. No subprocess calls — workers self-terminate, not killed
4. Old non-PID sdd files (coverage, markers, state, cmd-cache, baseline) → removed
5. Fresh sdd files (< max_age) → preserved
6. Mixed stale and fresh → only stale removed
7. Corrupt PID file (non-integer, empty) → removed without crash
8. Permission-denied files → skipped without crash
9. Empty temp dir → no-op
10. Non-sdd files → untouched
11. Directories named sdd-* → skipped
12. File disappears during cleanup (race condition) → no crash
13. main() calls cleanup_stale_sdd on startup
"""
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import importlib

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
session_start_mod = importlib.import_module("session-start")


class TestCleanupStaleSdd:
    """Test cleanup_stale_sdd function."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self._patch = patch.object(session_start_mod.tempfile, "gettempdir",
                                   return_value=self.tmpdir)
        self._patch.start()

    def teardown_method(self):
        self._patch.stop()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _create_file(self, name, content="", age_seconds=0):
        """Create a file in tmpdir with optional age."""
        p = Path(self.tmpdir) / name
        p.write_text(content)
        if age_seconds > 0:
            old_time = time.time() - age_seconds
            os.utime(p, (old_time, old_time))
        return p

    # ── Scenario 1: Stale PID files with dead processes ──

    def test_stale_pid_dead_process_removed(self):
        """PID file referencing a dead process → file removed."""
        p = self._create_file("sdd-test-run-abc123.pid", "999999",
                              age_seconds=90000)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert not p.exists()

    # ── Scenario 2: Old PID files are purged by age ──

    def test_old_pid_file_purged_by_age(self):
        """Old PID file → removed by age."""
        p = self._create_file("sdd-test-run-abc123.pid",
                              str(os.getpid()), age_seconds=90000)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert not p.exists()

    # ── Scenario 13: no pkill — workers self-terminate ──

    def test_no_subprocess_calls(self):
        """cleanup_stale_sdd does NOT kill processes — only purges files."""
        assert not hasattr(session_start_mod, "subprocess"), \
            "subprocess should not be imported — no process killing"

    # ── Scenario 4: Old non-PID sdd files removed ──

    def test_old_coverage_file_removed(self):
        p = self._create_file("sdd-coverage-abc123.json", "{}",
                              age_seconds=90000)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert not p.exists()

    def test_old_rerun_marker_removed(self):
        p = self._create_file("sdd-rerun-abc123.marker", "1234",
                              age_seconds=90000)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert not p.exists()

    def test_old_test_state_removed(self):
        p = self._create_file("sdd-test-state-abc123.json", "{}",
                              age_seconds=90000)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert not p.exists()

    def test_old_test_cmd_cache_removed(self):
        p = self._create_file("sdd-test-cmd-abc123.json", "{}",
                              age_seconds=90000)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert not p.exists()

    def test_old_baseline_removed(self):
        p = self._create_file("sdd-test-baseline-abc123.json", "{}",
                              age_seconds=90000)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert not p.exists()

    # ── Scenario 5: Fresh files preserved ──

    def test_fresh_file_preserved(self):
        p = self._create_file("sdd-coverage-abc123.json", "{}",
                              age_seconds=100)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert p.exists()

    def test_fresh_pid_file_preserved(self):
        """Fresh PID file with dead process → kept (not old enough)."""
        p = self._create_file("sdd-test-run-abc123.pid", "999999",
                              age_seconds=100)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert p.exists()

    # ── Scenario 6: Mixed stale and fresh ──

    def test_mixed_only_stale_removed(self):
        old = self._create_file("sdd-coverage-old.json", "{}",
                                age_seconds=90000)
        fresh = self._create_file("sdd-coverage-fresh.json", "{}",
                                  age_seconds=100)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert not old.exists()
        assert fresh.exists()

    # ── Scenario 7: Corrupt PID file ──

    def test_corrupt_pid_no_crash(self):
        p = self._create_file("sdd-test-run-abc123.pid", "not-a-number",
                              age_seconds=90000)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert not p.exists()

    def test_empty_pid_no_crash(self):
        p = self._create_file("sdd-test-run-abc123.pid", "",
                              age_seconds=90000)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert not p.exists()

    # ── Scenario 8: Permission denied ──

    def test_unreadable_file_skipped(self):
        """Files that raise OSError on stat/unlink are skipped gracefully."""
        p = self._create_file("sdd-coverage-locked.json", "{}",
                              age_seconds=90000)
        original_unlink = Path.unlink

        def unlink_that_raises(self_path, *a, **kw):
            if "locked" in str(self_path):
                raise PermissionError("denied")
            return original_unlink(self_path, *a, **kw)

        with patch.object(Path, "unlink", unlink_that_raises):
            # Should not crash
            session_start_mod.cleanup_stale_sdd(max_age=86400)
        # File survives because unlink raised PermissionError
        assert p.exists()

    # ── Scenario 9: Empty temp dir ──

    def test_empty_tmpdir_noop(self):
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        # No crash, no files created

    # ── Scenario 10: Non-sdd files untouched ──

    def test_non_sdd_files_untouched(self):
        p = self._create_file("other-file.json", "{}",
                              age_seconds=90000)
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert p.exists()

    # ── Scenario 11: Directories named sdd-* are skipped ──

    def test_sdd_directory_skipped(self):
        d = Path(self.tmpdir) / "sdd-some-dir"
        d.mkdir()
        session_start_mod.cleanup_stale_sdd(max_age=86400)
        assert d.exists()

    # ── Scenario 12: File disappears between glob and stat (race) ──

    def test_file_disappears_during_cleanup(self):
        p = self._create_file("sdd-coverage-vanish.json", "{}",
                              age_seconds=90000)
        original_stat = session_start_mod.os.stat

        call_count = [0]
        def stat_that_deletes(path, *a, **kw):
            call_count[0] += 1
            if call_count[0] == 1 and "vanish" in str(path):
                p.unlink(missing_ok=True)
                raise FileNotFoundError("gone")
            return original_stat(path, *a, **kw)

        with patch.object(session_start_mod.os, "stat",
                          side_effect=stat_that_deletes):
            session_start_mod.cleanup_stale_sdd(max_age=86400)
        # No crash


class TestCleanupIntegrationWithMain:
    """Verify cleanup_stale_sdd is called during session-start main flow."""

    def test_cleanup_called_in_main(self):
        """main() calls cleanup_stale_sdd before template sync."""
        called = []
        with patch.object(session_start_mod, "cleanup_stale_sdd",
                          side_effect=lambda **kw: called.append(True)), \
             patch.object(session_start_mod, "consume_stdin"), \
             patch.object(session_start_mod, "find_project_dir",
                          return_value=Path(tempfile.mkdtemp())), \
             patch.object(session_start_mod, "find_plugin_root",
                          return_value=Path(tempfile.mkdtemp())), \
             patch.object(session_start_mod, "ensure_gitignore_rules"), \
             patch.object(session_start_mod, "sync_all_files"), \
             patch.object(session_start_mod, "output_hook_response"):
            try:
                session_start_mod.main()
            except SystemExit:
                pass
        assert called, "cleanup_stale_sdd was not called during main()"
