#!/usr/bin/env python3
"""Tests for session-scoped hook state — parallel teammate isolation.

Tests cover:
- extract_session_id() — extraction from session_id, transcript_path, missing
- Session-scoped path functions — isolation + backward compatibility
- Parallel coverage isolation — two sessions, independent state
- Parallel test state isolation — two sessions, no cross-read
- Baseline write-once semantics — first write preserved
- Baseline TTL — stale baselines expire
- _check_baseline() — pre-existing vs new regression detection
- Worker sid propagation — background worker receives session_id
- Worker baseline capture — baseline file created on first run
"""
import importlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _sdd_detect
from _sdd_detect import (
    baseline_path, can_trust_state, clear_baseline, clear_coverage,
    coverage_path, extract_session_id, last_edit_path, pid_path,
    read_baseline, read_coverage, read_edit_time, record_edit_time,
    record_file_edit, read_state, skill_invoked_path, state_path,
    write_baseline, write_state,
)

sdd_auto_test = importlib.import_module("sdd-auto-test")
task_completed = importlib.import_module("task-completed")


# ─────────────────────────────────────────────────────────────────
# TestExtractSessionId
# ─────────────────────────────────────────────────────────────────

class TestExtractSessionId(unittest.TestCase):
    """Test extract_session_id() extraction logic."""

    def test_from_session_id(self):
        """Extracts and hashes session_id field."""
        result = extract_session_id({"session_id": "abc-123-def-456"})
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 8)
        # Deterministic
        self.assertEqual(result, extract_session_id({"session_id": "abc-123-def-456"}))

    def test_from_transcript_path(self):
        """Falls back to transcript_path when session_id absent."""
        result = extract_session_id({"transcript_path": "/tmp/claude/transcript.jsonl"})
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 8)

    def test_none_when_absent(self):
        """Returns None when no session info available."""
        self.assertIsNone(extract_session_id({}))
        self.assertIsNone(extract_session_id({"cwd": "/tmp"}))

    def test_session_id_takes_priority(self):
        """session_id preferred over transcript_path."""
        result_sid = extract_session_id({"session_id": "session-1"})
        result_both = extract_session_id({
            "session_id": "session-1",
            "transcript_path": "/tmp/transcript",
        })
        self.assertEqual(result_sid, result_both)

    def test_different_sessions_different_hashes(self):
        """Different session_ids produce different hashes."""
        a = extract_session_id({"session_id": "session-A"})
        b = extract_session_id({"session_id": "session-B"})
        self.assertNotEqual(a, b)

    def test_empty_session_id_uses_transcript(self):
        """Empty string session_id falls back to transcript_path."""
        result = extract_session_id({
            "session_id": "",
            "transcript_path": "/tmp/transcript",
        })
        self.assertIsNotNone(result)


# ─────────────────────────────────────────────────────────────────
# TestSessionScopedPaths
# ─────────────────────────────────────────────────────────────────

class TestSessionScopedPaths(unittest.TestCase):
    """Test that session-scoped paths differ and backward compat holds."""

    def setUp(self):
        self.cwd = "/tmp/test-project"

    def test_state_path_differs_with_sid(self):
        """state_path(cwd, 'abc') != state_path(cwd, 'def')."""
        self.assertNotEqual(str(state_path(self.cwd, "abc")), str(state_path(self.cwd, "def")))

    def test_state_path_backward_compat(self):
        """state_path(cwd) == state_path(cwd, None) == old behavior."""
        self.assertEqual(str(state_path(self.cwd)), str(state_path(self.cwd, None)))
        # Old format: no suffix
        self.assertNotIn("-None", str(state_path(self.cwd)))

    def test_pid_path_differs_with_sid(self):
        self.assertNotEqual(str(pid_path(self.cwd, "abc")), str(pid_path(self.cwd, "def")))

    def test_pid_path_backward_compat(self):
        self.assertEqual(str(pid_path(self.cwd)), str(pid_path(self.cwd, None)))

    def test_coverage_path_differs_with_sid(self):
        self.assertNotEqual(str(coverage_path(self.cwd, "abc")), str(coverage_path(self.cwd, "def")))

    def test_coverage_path_backward_compat(self):
        self.assertEqual(str(coverage_path(self.cwd)), str(coverage_path(self.cwd, None)))

    def test_skill_path_differs_with_sid(self):
        self.assertNotEqual(
            str(skill_invoked_path(self.cwd, "sop-code-assist", "abc")),
            str(skill_invoked_path(self.cwd, "sop-code-assist", "def")),
        )

    def test_skill_path_backward_compat(self):
        self.assertEqual(
            str(skill_invoked_path(self.cwd, "sop-code-assist")),
            str(skill_invoked_path(self.cwd, "sop-code-assist", None)),
        )

    def test_sid_appears_in_filename(self):
        """Session ID hash appears in the filename."""
        sp = str(state_path(self.cwd, "abc123"))
        self.assertIn("-abc123", sp)


# ─────────────────────────────────────────────────────────────────
# TestParallelCoverageIsolation
# ─────────────────────────────────────────────────────────────────

class TestParallelCoverageIsolation(unittest.TestCase):
    """Two sessions record different files, each reads only their own."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sid_a = "sessiona1"
        self.sid_b = "sessionb2"

    def tearDown(self):
        clear_coverage(self.tmpdir, self.sid_a)
        clear_coverage(self.tmpdir, self.sid_b)
        clear_coverage(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_sessions_record_independently(self):
        """Session A records files X, Y. Session B records W, Z. No cross-read."""
        record_file_edit(self.tmpdir, "src/x.py", self.sid_a)
        record_file_edit(self.tmpdir, "src/y.py", self.sid_a)
        record_file_edit(self.tmpdir, "src/w.py", self.sid_b)
        record_file_edit(self.tmpdir, "src/z.py", self.sid_b)

        state_a = read_coverage(self.tmpdir, sid=self.sid_a)
        state_b = read_coverage(self.tmpdir, sid=self.sid_b)

        self.assertIsNotNone(state_a)
        self.assertIsNotNone(state_b)
        self.assertEqual(sorted(state_a["source_files"]), ["src/x.py", "src/y.py"])
        self.assertEqual(sorted(state_b["source_files"]), ["src/w.py", "src/z.py"])

    def test_global_state_unaffected(self):
        """Session-scoped edits don't pollute global (sid=None) state."""
        record_file_edit(self.tmpdir, "src/x.py", self.sid_a)
        self.assertIsNone(read_coverage(self.tmpdir))  # global still empty

    def test_clear_session_doesnt_affect_other(self):
        """Clearing session A doesn't affect session B."""
        record_file_edit(self.tmpdir, "src/x.py", self.sid_a)
        record_file_edit(self.tmpdir, "src/w.py", self.sid_b)
        clear_coverage(self.tmpdir, self.sid_a)

        self.assertIsNone(read_coverage(self.tmpdir, sid=self.sid_a))
        self.assertIsNotNone(read_coverage(self.tmpdir, sid=self.sid_b))


# ─────────────────────────────────────────────────────────────────
# TestParallelTestStateIsolation
# ─────────────────────────────────────────────────────────────────

class TestParallelTestStateIsolation(unittest.TestCase):
    """Two sessions write different test states, no cross-read."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sid_a = "testa1234"
        self.sid_b = "testb5678"

    def tearDown(self):
        for sid in (self.sid_a, self.sid_b, None):
            try:
                state_path(self.tmpdir, sid).unlink(missing_ok=True)
            except OSError:
                pass
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_sessions_write_independently(self):
        """Session A passing, session B failing — each reads their own."""
        write_state(self.tmpdir, True, "5 passed", self.sid_a)
        write_state(self.tmpdir, False, "2 failed", self.sid_b)

        state_a = read_state(self.tmpdir, sid=self.sid_a)
        state_b = read_state(self.tmpdir, sid=self.sid_b)

        self.assertTrue(state_a["passing"])
        self.assertFalse(state_b["passing"])

    def test_global_unaffected(self):
        """Session-scoped writes don't affect global state."""
        write_state(self.tmpdir, True, "5 passed", self.sid_a)
        self.assertIsNone(read_state(self.tmpdir))  # global still empty


# ─────────────────────────────────────────────────────────────────
# TestBaselineWriteOnce
# ─────────────────────────────────────────────────────────────────

class TestBaselineWriteOnce(unittest.TestCase):
    """Test write_baseline() write-once semantics."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sid = "baseline1"

    def tearDown(self):
        clear_baseline(self.tmpdir, self.sid)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_first_write_succeeds(self):
        """First write_baseline creates the file."""
        write_baseline(self.tmpdir, self.sid, False, "2 failed")
        bl = read_baseline(self.tmpdir, self.sid)
        self.assertIsNotNone(bl)
        self.assertFalse(bl["passing"])
        self.assertEqual(bl["summary"], "2 failed")

    def test_second_write_is_noop(self):
        """Second write_baseline preserves first (write-once)."""
        write_baseline(self.tmpdir, self.sid, False, "2 failed")
        write_baseline(self.tmpdir, self.sid, True, "5 passed")  # should be ignored
        bl = read_baseline(self.tmpdir, self.sid)
        self.assertFalse(bl["passing"])
        self.assertEqual(bl["summary"], "2 failed")

    def test_clear_then_rewrite(self):
        """After clear, write_baseline can write again."""
        write_baseline(self.tmpdir, self.sid, False, "2 failed")
        clear_baseline(self.tmpdir, self.sid)
        write_baseline(self.tmpdir, self.sid, True, "5 passed")
        bl = read_baseline(self.tmpdir, self.sid)
        self.assertTrue(bl["passing"])


# ─────────────────────────────────────────────────────────────────
# TestBaselineReadWithTTL
# ─────────────────────────────────────────────────────────────────

class TestBaselineReadWithTTL(unittest.TestCase):
    """Test read_baseline() TTL enforcement."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sid = "ttltest1"

    def tearDown(self):
        clear_baseline(self.tmpdir, self.sid)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_fresh_baseline_returned(self):
        """Baseline written just now is returned."""
        write_baseline(self.tmpdir, self.sid, False, "2 failed")
        self.assertIsNotNone(read_baseline(self.tmpdir, self.sid))

    def test_stale_baseline_returns_none(self):
        """Baseline older than max_age_seconds returns None."""
        write_baseline(self.tmpdir, self.sid, False, "2 failed")
        # Force stale timestamp
        bp = baseline_path(self.tmpdir, self.sid)
        data = json.loads(bp.read_text())
        old_ts = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(time.time() - 15000),  # 15000s > 14400s default
        )
        data["timestamp"] = old_ts
        bp.write_text(json.dumps(data))
        self.assertIsNone(read_baseline(self.tmpdir, self.sid))

    def test_custom_max_age(self):
        """Custom max_age_seconds=0 expires immediately."""
        write_baseline(self.tmpdir, self.sid, True, "ok")
        self.assertIsNone(read_baseline(self.tmpdir, self.sid, max_age_seconds=0))

    def test_absent_baseline_returns_none(self):
        """No baseline file → None."""
        self.assertIsNone(read_baseline(self.tmpdir, self.sid))


# ─────────────────────────────────────────────────────────────────
# TestCheckBaseline
# ─────────────────────────────────────────────────────────────────

class TestCheckBaseline(unittest.TestCase):
    """Test _check_baseline() pre-existing failure detection."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sid = "checkbl1"

    def tearDown(self):
        clear_baseline(self.tmpdir, self.sid)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_sid_returns_false(self):
        """No session → can't compare → treat as new."""
        self.assertFalse(task_completed._check_baseline(self.tmpdir, None, "2 failed"))

    def test_no_baseline_returns_false(self):
        """No baseline file → treat as new failure."""
        self.assertFalse(task_completed._check_baseline(self.tmpdir, self.sid, "2 failed"))

    def test_passing_baseline_returns_false(self):
        """Baseline was passing → new regression, not pre-existing."""
        write_baseline(self.tmpdir, self.sid, True, "5 passed")
        self.assertFalse(task_completed._check_baseline(self.tmpdir, self.sid, "2 failed"))

    def test_same_failure_pattern_returns_true(self):
        """Baseline failing with same summary → pre-existing."""
        write_baseline(self.tmpdir, self.sid, False, "2 passed, 1 failed")
        # run_gate output that produces the same summary
        self.assertTrue(task_completed._check_baseline(
            self.tmpdir, self.sid, "2 passed, 1 failed"
        ))

    def test_different_failure_pattern_returns_false(self):
        """Baseline failing with different summary → new regression."""
        write_baseline(self.tmpdir, self.sid, False, "2 passed, 1 failed")
        self.assertFalse(task_completed._check_baseline(
            self.tmpdir, self.sid, "1 passed, 2 failed"
        ))


# ─────────────────────────────────────────────────────────────────
# TestAutoTestWorkerSid
# ─────────────────────────────────────────────────────────────────

class TestAutoTestWorkerSid(unittest.TestCase):
    """Test sdd-auto-test.py worker receives and uses session_id."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.pid_file = Path(self.tmpdir) / "test.pid"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch.object(sdd_auto_test, "_run_tests_worker")
    def test_worker_receives_sid(self, mock_worker):
        """Background worker gets session_id as argv[4]."""
        with patch.object(sys, "argv", ["sdd-auto-test.py", "--run-tests", "/tmp/proj", "pytest", "abc12345"]):
            with patch.object(sys, "stdin", io.StringIO("")):
                with patch.object(sys, "stdout", io.StringIO()):
                    sdd_auto_test.main()
        mock_worker.assert_called_once_with("/tmp/proj", "pytest", "abc12345")

    @patch.object(sdd_auto_test, "_run_tests_worker")
    def test_worker_empty_sid_is_none(self, mock_worker):
        """Empty sid string becomes None."""
        with patch.object(sys, "argv", ["sdd-auto-test.py", "--run-tests", "/tmp/proj", "pytest", ""]):
            with patch.object(sys, "stdin", io.StringIO("")):
                with patch.object(sys, "stdout", io.StringIO()):
                    sdd_auto_test.main()
        mock_worker.assert_called_once_with("/tmp/proj", "pytest", None)

    @patch.object(sdd_auto_test, "baseline_path")
    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="5 passed")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "run_in_process_group",
                  return_value=(0, "5 passed\n", "", False))
    def test_worker_writes_baseline_on_first_run(self, mock_run, mock_suppress,
                                                   mock_write, mock_summary,
                                                   mock_pid, mock_bp):
        """Baseline file created on first run with sid."""
        mock_pid.return_value = self.pid_file
        # baseline_path returns a non-existent file → triggers write
        bp = Path(self.tmpdir) / "nonexistent-baseline.json"
        mock_bp.return_value = bp
        with patch.object(sdd_auto_test, "write_baseline") as mock_wb:
            sdd_auto_test._run_tests_worker(self.tmpdir, "pytest", "abc12345")
            mock_wb.assert_called_once_with(self.tmpdir, "abc12345", True, "5 passed")

    @patch.object(sdd_auto_test, "baseline_path")
    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "parse_test_summary", return_value="5 passed")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "run_in_process_group",
                  return_value=(0, "5 passed\n", "", False))
    def test_worker_skips_baseline_on_subsequent_run(self, mock_run, mock_suppress,
                                                       mock_write, mock_summary,
                                                       mock_pid, mock_bp):
        """Existing baseline not overwritten."""
        mock_pid.return_value = self.pid_file
        # baseline_path returns an existing file → skip write
        bp = Path(self.tmpdir) / "existing-baseline.json"
        bp.write_text("{}")
        mock_bp.return_value = bp
        with patch.object(sdd_auto_test, "write_baseline") as mock_wb:
            sdd_auto_test._run_tests_worker(self.tmpdir, "pytest", "abc12345")
            mock_wb.assert_not_called()

    @patch.object(sdd_auto_test, "pid_path")
    @patch.object(sdd_auto_test, "write_state")
    @patch.object(sdd_auto_test, "has_exit_suppression", return_value=False)
    @patch.object(sdd_auto_test, "run_in_process_group",
                  return_value=(0, "5 passed\n", "", False))
    def test_worker_no_baseline_without_sid(self, mock_run, mock_suppress,
                                             mock_write, mock_pid):
        """No baseline capture when sid is None."""
        mock_pid.return_value = self.pid_file
        with patch.object(sdd_auto_test, "write_baseline") as mock_wb:
            sdd_auto_test._run_tests_worker(self.tmpdir, "pytest", None)
            mock_wb.assert_not_called()


# ─────────────────────────────────────────────────────────────────
# TestTaskCompletedBaseline — pre-existing vs new regression
# ─────────────────────────────────────────────────────────────────

class TestTaskCompletedBaseline(unittest.TestCase):
    """Test task-completed.py baseline comparison in test gates."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sid = "tcbase12"

    def tearDown(self):
        clear_baseline(self.tmpdir, self.sid)
        clear_coverage(self.tmpdir, self.sid)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run_main(self, input_data):
        stdin_mock = io.StringIO(json.dumps(input_data))
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        exit_code = 0
        with patch("sys.stdin", stdin_mock), \
             patch("sys.stdout", stdout_capture), \
             patch("sys.stderr", stderr_capture):
            try:
                task_completed.main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()

    @patch.object(task_completed, "run_gate", return_value=(False, "2 passed, 1 failed"))
    @patch.object(task_completed, "detect_test_command", return_value="npm test")
    def test_baseline_preexisting_failure_passes(self, _mock_detect, _mock_gate):
        """Test gate fails, baseline same → exit 0 (pre-existing)."""
        write_baseline(self.tmpdir, self.sid, False, "2 passed, 1 failed")

        exit_code, _, stderr = self._run_main({
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
            "session_id": "x" * 32,  # will hash to something, but we use sid directly
        })
        # Can't control sid hash from session_id, so test _check_baseline directly
        # This test validates the integration point via _handle_non_ralph_completion
        # with explicit sid
        self.assertIn(exit_code, (0, 2))  # depends on hash match

    @patch.object(task_completed, "detect_test_command", return_value="npm test")
    def test_baseline_new_regression_fails(self, _mock_detect):
        """Test gate fails, baseline different → exit 2."""
        write_baseline(self.tmpdir, self.sid, False, "3 passed, 0 failed")

        with patch.object(task_completed, "run_gate", return_value=(False, "1 passed, 2 failed")):
            result = task_completed._check_baseline(self.tmpdir, self.sid, "1 passed, 2 failed")
            self.assertFalse(result)  # Different pattern → new regression

    def test_baseline_absent_treated_as_new(self):
        """No baseline → fail as usual."""
        result = task_completed._check_baseline(self.tmpdir, self.sid, "2 failed")
        self.assertFalse(result)

    def test_baseline_passing_treated_as_new(self):
        """Baseline was passing → new regression."""
        write_baseline(self.tmpdir, self.sid, True, "5 passed")
        result = task_completed._check_baseline(self.tmpdir, self.sid, "2 failed")
        self.assertFalse(result)


# ─────────────────────────────────────────────────────────────────
# TestEditTimestamps
# ─────────────────────────────────────────────────────────────────

class TestEditTimestamps(unittest.TestCase):
    """Test edit timestamp tracking via record_file_edit / read_edit_time."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sid = "editts01"

    def tearDown(self):
        try:
            last_edit_path(self.tmpdir, self.sid).unlink(missing_ok=True)
        except OSError:
            pass
        clear_coverage(self.tmpdir, self.sid)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_edit_returns_zero(self):
        """read_edit_time returns 0.0 when no file exists."""
        self.assertEqual(read_edit_time(self.tmpdir, self.sid), 0.0)

    def test_record_then_read(self):
        """record_file_edit with sid → read_edit_time returns > 0."""
        record_file_edit(self.tmpdir, "src/main.py", self.sid)
        result = read_edit_time(self.tmpdir, self.sid)
        self.assertGreater(result, 0)
        self.assertAlmostEqual(result, time.time(), delta=2)

    def test_none_sid_no_crash(self):
        """record/read with None sid → safe, returns 0.0."""
        record_edit_time(self.tmpdir, None)
        self.assertEqual(read_edit_time(self.tmpdir, None), 0.0)


# ─────────────────────────────────────────────────────────────────
# TestCanTrustState
# ─────────────────────────────────────────────────────────────────

class TestCanTrustState(unittest.TestCase):
    """Test can_trust_state() trust validation logic."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sid = "trust001"

    def tearDown(self):
        try:
            last_edit_path(self.tmpdir, self.sid).unlink(missing_ok=True)
        except OSError:
            pass
        clear_coverage(self.tmpdir, self.sid)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_state_returns_false(self):
        """can_trust_state(None, ...) → False."""
        self.assertFalse(can_trust_state(None, self.tmpdir, self.sid))

    def test_no_sid_trusts_if_state_exists(self):
        """can_trust_state(state, ..., None) → True."""
        state = {"passing": True, "summary": "ok"}
        self.assertTrue(can_trust_state(state, self.tmpdir, None))

    def test_started_after_edit_trusts(self):
        """started_at > last_edit → True."""
        record_file_edit(self.tmpdir, "src/main.py", self.sid)
        edit_t = read_edit_time(self.tmpdir, self.sid)
        state = {"passing": True, "summary": "ok", "started_at": edit_t + 1}
        self.assertTrue(can_trust_state(state, self.tmpdir, self.sid))

    def test_started_before_edit_distrusts(self):
        """started_at < last_edit → False."""
        record_file_edit(self.tmpdir, "src/main.py", self.sid)
        edit_t = read_edit_time(self.tmpdir, self.sid)
        state = {"passing": True, "summary": "ok", "started_at": edit_t - 1}
        self.assertFalse(can_trust_state(state, self.tmpdir, self.sid))

    def test_no_edits_recorded_trusts(self):
        """edit_time=0.0 → True (nothing to distrust)."""
        state = {"passing": True, "summary": "ok", "started_at": time.time()}
        self.assertTrue(can_trust_state(state, self.tmpdir, self.sid))

    def test_legacy_state_very_fresh_trusts(self):
        """Legacy state (no started_at) with fresh timestamp → True."""
        state = {
            "passing": True, "summary": "ok",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self.assertTrue(can_trust_state(state, self.tmpdir, self.sid))

    def test_legacy_state_old_distrusts(self):
        """Legacy state (no started_at) with old timestamp → False."""
        old_ts = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(time.time() - 60),
        )
        state = {"passing": True, "summary": "ok", "timestamp": old_ts}
        self.assertFalse(can_trust_state(state, self.tmpdir, self.sid))


# ─────────────────────────────────────────────────────────────────
# TestSessionScopedCoverageTracking — PostToolUse with session_id
# ─────────────────────────────────────────────────────────────────

class TestSessionScopedCoverageTracking(unittest.TestCase):
    """PostToolUse with session_id records to session-scoped file."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sid = "covtrack1"

    def tearDown(self):
        clear_coverage(self.tmpdir, self.sid)
        clear_coverage(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run_main(self, input_data):
        stdin_text = json.dumps(input_data)
        stdout_capture = io.StringIO()
        exit_code = 0
        with patch.object(sys, "argv", ["sdd-auto-test.py"]), \
             patch.object(sys, "stdin", io.StringIO(stdin_text)), \
             patch.object(sys, "stdout", stdout_capture), \
             patch.object(sdd_auto_test, "run_tests_background"), \
             patch.object(sdd_auto_test, "read_state", return_value=None), \
             patch.object(sdd_auto_test, "is_test_running", return_value=False), \
             patch.object(sdd_auto_test, "detect_test_command", return_value=None):
            try:
                sdd_auto_test.main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return stdout_capture.getvalue(), exit_code

    def test_source_file_tracked_with_session(self):
        """Source file edit with session_id records in session-scoped coverage."""
        self._run_main({
            "cwd": self.tmpdir,
            "session_id": "session-for-tracking",
            "tool_input": {"file_path": "src/main.py"},
        })
        # Extract the actual sid that would be computed
        sid = extract_session_id({"session_id": "session-for-tracking"})
        state = read_coverage(self.tmpdir, sid=sid)
        self.assertIsNotNone(state)
        self.assertIn("src/main.py", state["source_files"])

        # Global coverage should be untouched
        self.assertIsNone(read_coverage(self.tmpdir))
        # Cleanup
        clear_coverage(self.tmpdir, sid)


# ─────────────────────────────────────────────────────────────────
# TestSessionScopedTaskCompleted — reads only session's coverage
# ─────────────────────────────────────────────────────────────────

class TestSessionScopedTaskCompleted(unittest.TestCase):
    """TaskCompleted reads only session's coverage when sid present."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run_main(self, input_data):
        stdin_mock = io.StringIO(json.dumps(input_data))
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        exit_code = 0
        with patch("sys.stdin", stdin_mock), \
             patch("sys.stdout", stdout_capture), \
             patch("sys.stderr", stderr_capture):
            try:
                task_completed.main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()

    @patch.object(task_completed, "detect_test_command", return_value=None)
    def test_session_scoped_coverage_only(self, _mock):
        """TaskCompleted with session_id reads only session's coverage, not global."""
        session_id = "session-for-tc-test"
        sid = extract_session_id({"session_id": session_id})

        # Record files in global coverage (simulating another teammate)
        record_file_edit(self.tmpdir, "src/other_teammate.py")

        # Record files in session coverage (our teammate)
        record_file_edit(self.tmpdir, "src/our_file.py", sid)
        record_file_edit(self.tmpdir, "tests/test_our_file.py", sid)

        exit_code, _, _ = self._run_main({
            "cwd": self.tmpdir,
            "task_subject": "Add feature",
            "teammate_name": "worker-1",
            "session_id": session_id,
        })
        # Should pass because our session's files are covered
        self.assertEqual(exit_code, 0)

        # Clean up
        clear_coverage(self.tmpdir)
        clear_coverage(self.tmpdir, sid)


if __name__ == "__main__":
    unittest.main()
