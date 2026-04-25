#!/usr/bin/env python3
"""SCEN-009: worktree isolation via project_hash(cwd).

SPEC Section 5 SCEN-009:
    Worktree isolation: orchestrator commits scenarios to parent branch,
    each worktree inherits via branch, each validates independently
    (different project_hash(cwd)).

Mechanism:
    project_hash(cwd) hashes the working-directory path via md5. Two
    worktrees derived from the same commit have DIFFERENT absolute paths,
    so their state files in /tmp/ cannot collide. Scenarios (git content)
    are shared; state (skill invocations, test state, coverage) is per-cwd
    → per-worktree. Invoking verification-before-completion in worktree A
    does NOT satisfy the gate for worktree B.

Coverage:
    1. project_hash(cwd) differs for distinct cwd paths.
    2. has_pending_scenarios is per-cwd: verification in worktree1 does
       not clear the pending flag for worktree2.
    3. task-completed invocation in each worktree observes isolated state.
       The scenario-gate hook integration is NOT yet implemented, so the
       hook-level assertion is marked as a red/future test (documented
       inline). The direct _sdd_scenarios.has_pending_scenarios call is
       the load-bearing assertion that must pass today.

Red/green breakdown:
    - test_distinct_cwds_produce_distinct_project_hashes → GREEN today
    - test_shared_scenarios_isolated_state_via_project_hash → GREEN today
      (exercises already-shipped _sdd_scenarios.has_pending_scenarios)
    - test_task_completed_scenario_gate_isolation → RED today (depends on
      the task-completed scenario gate landing; documented inline).
"""
import importlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
task_completed = importlib.import_module("task-completed")
import _sdd_detect
import _sdd_scenarios
import _sdd_state


_VALID_SCENARIO_BODY = """\
---
name: login-validation
created_by: orchestrator
created_at: 2026-04-16T10:00:00Z
---

## SCEN-001: successful login
**Given**: unregistered anonymous user
**When**: POST /login with valid email + password
**Then**: response 200 with session token, redirect to /dashboard
**Evidence**: HTTP response body, cookies set
"""

# Phase 10 fixture path: scenarios live under spec folders.
_SCENARIO_DIR_REL = ".ralph/specs/scen009/scenarios"


class TestScen009(unittest.TestCase):
    """SCEN-009: worktree isolation via project_hash(cwd).

    Two sibling tmpdir roots simulate git worktrees — they share the same
    scenario content (as a committed file in the parent repo would be)
    but have distinct absolute paths. State lives under
    /tmp/sdd-*-{project_hash(cwd)}*, so distinct cwds yield isolated state.
    """

    def setUp(self):
        # Parent scratch root for worktree siblings.
        self.root = tempfile.mkdtemp(prefix="sdd-scen-009-")
        self.worktree1 = Path(self.root) / "wt1"
        self.worktree2 = Path(self.root) / "wt2"
        self.worktree1.mkdir()
        self.worktree2.mkdir()

        # Raw session id is shared across worktrees — represents the same
        # logical teammate session. The hook hashes this, but direct
        # _sdd_state writes use whatever sid is passed in.
        self.raw_sid = "scen009-session"
        self.hashed_sid = _sdd_state.extract_session_id(
            {"session_id": self.raw_sid}
        )

        # Seed identical scenario content in both worktrees (mirrors what
        # `git worktree add` would yield after the parent branch committed
        # the scenario file). No git setup needed for the core isolation
        # invariant — cwd-hash isolation is path-based, not git-based.
        for wt in (self.worktree1, self.worktree2):
            scen_dir = wt / _SCENARIO_DIR_REL
            scen_dir.mkdir(parents=True)
            (scen_dir / f"login{_sdd_scenarios.SCENARIO_FILE_SUFFIX}").write_text(
                _VALID_SCENARIO_BODY, encoding="utf-8"
            )

    def tearDown(self):
        # Clean per-worktree state (skill invocation + test state files).
        for wt in (self.worktree1, self.worktree2):
            cwd = str(wt)
            try:
                _sdd_state.state_path(cwd).unlink(missing_ok=True)
                _sdd_state.skill_invoked_path(
                    cwd, "verification-before-completion",
                    sid=self.hashed_sid,
                ).unlink(missing_ok=True)
            except OSError:
                pass
        shutil.rmtree(self.root, ignore_errors=True)

    # ─────────────────────────────────────────────────────────
    # Test #1 — project_hash keys on cwd (GREEN today)
    # ─────────────────────────────────────────────────────────

    def test_distinct_cwds_produce_distinct_project_hashes(self):
        """Two distinct cwd strings yield two distinct project hashes.

        This is the core invariant of worktree isolation: state files in
        /tmp are named by project_hash(cwd), so two worktrees with
        different absolute paths cannot collide on state storage.
        """
        h1 = _sdd_detect.project_hash(str(self.worktree1))
        h2 = _sdd_detect.project_hash(str(self.worktree2))

        self.assertNotEqual(
            h1, h2,
            f"project_hash must differ for distinct cwds to isolate state "
            f"across worktrees. Got h1={h1!r}, h2={h2!r}. FAILURE MODE: "
            f"project_hash is no longer keyed off cwd — state would collide "
            f"between worktrees and verification in one would spuriously "
            f"satisfy the gate in another."
        )
        # Deterministic same-input → same-output (idempotent hash).
        self.assertEqual(
            h1, _sdd_detect.project_hash(str(self.worktree1)),
            "project_hash must be deterministic for a fixed cwd."
        )

    # ─────────────────────────────────────────────────────────
    # Test #2 — scenarios shared, state isolated (GREEN today)
    # ─────────────────────────────────────────────────────────

    def test_shared_scenarios_isolated_state_via_project_hash(self):
        """Verification recorded in worktree1 does NOT clear worktree2's flag.

        Both worktrees contain the same valid scenario file (simulating a
        shared git-committed artifact). Only worktree1 records the
        verification-before-completion skill invocation. The per-cwd
        project_hash keeps the two state files distinct, so worktree2
        still reports pending scenarios.
        """
        cwd1 = str(self.worktree1)
        cwd2 = str(self.worktree2)

        # Sanity: both worktrees see the scenario file (shared content).
        self.assertEqual(
            len(_sdd_scenarios.scenario_files(cwd1)), 1,
            "worktree1 must see its scenario file."
        )
        self.assertEqual(
            len(_sdd_scenarios.scenario_files(cwd2)), 1,
            "worktree2 must see its (identical) scenario file."
        )

        # Record verification ONLY for worktree1.
        _sdd_state.write_skill_invoked(
            cwd1, "verification-before-completion", sid=self.hashed_sid,
        )

        # worktree1: verification recorded → no pending scenarios.
        self.assertFalse(
            _sdd_scenarios.has_pending_scenarios(cwd1, sid=self.hashed_sid),
            f"worktree1 recorded verification-before-completion → gate "
            f"should be satisfied. FAILURE MODE: verification state not "
            f"observed by has_pending_scenarios (path mismatch in "
            f"skill_invoked_path or sid mishandling)."
        )

        # worktree2: no verification → scenarios still pending.
        self.assertTrue(
            _sdd_scenarios.has_pending_scenarios(cwd2, sid=self.hashed_sid),
            f"worktree2 never recorded verification → gate must still "
            f"consider scenarios pending. FAILURE MODE: per-cwd state "
            f"isolation is broken — worktree2 is inheriting worktree1's "
            f"verification state, likely because project_hash stopped "
            f"keying on cwd or skill_invoked_path dropped the project hash."
        )

        # Cross-check: the two skill_invoked_path values are physically
        # distinct files on disk.
        p1 = _sdd_state.skill_invoked_path(
            cwd1, "verification-before-completion", sid=self.hashed_sid,
        )
        p2 = _sdd_state.skill_invoked_path(
            cwd2, "verification-before-completion", sid=self.hashed_sid,
        )
        self.assertNotEqual(
            p1, p2,
            f"skill_invoked_path must differ between worktrees. Got "
            f"p1={p1!r}, p2={p2!r}. FAILURE MODE: state path is not "
            f"derived from project_hash(cwd), so worktrees collide."
        )

    # ─────────────────────────────────────────────────────────
    # Test #3 — task-completed gate is per-worktree (RED today)
    # ─────────────────────────────────────────────────────────

    @patch.object(task_completed, "_has_source_edits", return_value=True)
    def test_task_completed_scenario_gate_isolation(self, _mock_edits):
        """task-completed invocation sees isolated verification state.

        Today, task-completed.py does NOT yet enforce the scenario gate,
        so both worktree invocations short-circuit to the existing
        test-state gate and exit 0. When the scenario gate lands (SPEC
        3.4 point 2, phase 3.3-3.4), worktree1 (with verification
        recorded) should exit 0 and worktree2 (without verification)
        should exit 2 with a message about verification.

        Red today, goes green when the task-completed scenario gate
        integration lands. The assertions below target the post-gate
        behavior — they MUST fail until the gate exists, which is
        exactly the signal we want.
        """
        # Seed fresh passing test state in BOTH worktrees so the existing
        # non-Ralph test gate does not mask the scenario-gate outcome.
        for wt in (self.worktree1, self.worktree2):
            _sdd_state.write_state(
                str(wt), True, "1 passed",
                raw_output="1 passed",
            )

        # Record verification ONLY in worktree1.
        _sdd_state.write_skill_invoked(
            str(self.worktree1), "verification-before-completion",
            sid=self.hashed_sid,
        )

        code1, stderr1 = self._run_task_completed(self.worktree1)
        code2, stderr2 = self._run_task_completed(self.worktree2)

        # worktree1 (verification recorded) must accept completion.
        self.assertEqual(
            code1, 0,
            f"worktree1 recorded verification → task-completed must accept "
            f"(exit 0). Got exit={code1}, stderr={stderr1!r}. FAILURE MODE "
            f"(today): scenario gate not yet wired, so either path could "
            f"currently exit 0 — this assertion is the load-bearing check "
            f"that worktree1 ALWAYS accepts once the gate lands."
        )

        # worktree2 (no verification) must block completion under the
        # future scenario gate. Today this assertion will FAIL because
        # task-completed.py does not yet check verification-before-completion.
        self.assertEqual(
            code2, 2,
            f"worktree2 never recorded verification → task-completed must "
            f"block with exit 2 once the scenario gate lands. Got "
            f"exit={code2}, stderr={stderr2!r}. RED TODAY: this test "
            f"documents the expected behavior after task-completed.py "
            f"scenario gate implementation (SPEC 3.4 point 2). Goes GREEN "
            f"when the gate enforces has_pending_scenarios() before the "
            f"existing test gate."
        )
        self.assertIn(
            "verification", stderr2.lower(),
            f"worktree2 stderr must cite the missing verification skill. "
            f"Got: {stderr2!r}. RED TODAY: asserts the scenario-gate error "
            f"message shape post-integration."
        )

    # ─────────────────────────────────────────────────────────
    # Optional sanity — real git worktrees share committed content
    # ─────────────────────────────────────────────────────────

    def test_real_git_worktrees_share_committed_scenarios(self):
        """Optional integration: git worktree add yields two worktrees with
        identical committed scenario content AND distinct project hashes.

        This is a sanity check that the cwd-hash-based isolation the core
        tests rely on aligns with real git worktree behavior. Skipped when
        git is unavailable — the core invariant (test #1) does not depend
        on git; this confirms the mapping to real worktrees holds.
        """
        if shutil.which("git") is None:
            self.skipTest("git not available")

        parent = Path(self.root) / "parent"
        parent.mkdir()
        # Minimal git init + commit of a scenarios file, --initial-branch
        # fallback for older git versions that ignore the flag.
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        subprocess.run(
            ["git", "init", "-q", str(parent)], check=True, env=env,
        )
        subprocess.run(
            ["git", "-C", str(parent), "config", "user.email", "t@t.t"],
            check=True, env=env,
        )
        subprocess.run(
            ["git", "-C", str(parent), "config", "user.name", "t"],
            check=True, env=env,
        )
        scen_dir = parent / _SCENARIO_DIR_REL
        scen_dir.mkdir(parents=True)
        scen_file = scen_dir / f"login{_sdd_scenarios.SCENARIO_FILE_SUFFIX}"
        scen_file.write_text(_VALID_SCENARIO_BODY, encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(parent), "add", "."], check=True, env=env,
        )
        subprocess.run(
            ["git", "-C", str(parent), "commit", "-q", "-m", "scen"],
            check=True, env=env,
        )

        wt_a = Path(self.root) / "real-wt-a"
        # git worktree add requires a distinct branch for each worktree.
        subprocess.run(
            ["git", "-C", str(parent), "worktree", "add", "-q",
             "-b", "wt-a-branch", str(wt_a)],
            check=True, env=env,
        )

        # Both parent and worktree contain the committed scenario file
        # (shared git content), but their cwd-based project hashes differ.
        self.assertTrue(
            (parent / _SCENARIO_DIR_REL /
             f"login{_sdd_scenarios.SCENARIO_FILE_SUFFIX}").exists()
        )
        self.assertTrue(
            (wt_a / _SCENARIO_DIR_REL /
             f"login{_sdd_scenarios.SCENARIO_FILE_SUFFIX}").exists()
        )
        self.assertNotEqual(
            _sdd_detect.project_hash(str(parent)),
            _sdd_detect.project_hash(str(wt_a)),
            "Real git worktree must yield a distinct project_hash vs parent.",
        )

    # ─────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────

    def _run_task_completed(self, cwd):
        """Invoke task_completed.main() against a given worktree cwd."""
        stdin_payload = {
            "cwd": str(cwd),
            "task_subject": "Ship feature",
            "teammate_name": "worker-1",
            "session_id": self.raw_sid,
        }
        stdin_mock = io.StringIO(json.dumps(stdin_payload))
        stderr_buf = io.StringIO()
        exit_code = 0
        env_patch = {"CLAUDE_PROJECT_DIR": str(cwd)}
        with patch("sys.stdin", stdin_mock), \
             patch("sys.stderr", stderr_buf), \
             patch.dict(os.environ, env_patch):
            try:
                task_completed.main()
            except SystemExit as e:
                exit_code = e.code if e.code is not None else 0
        return exit_code, stderr_buf.getvalue()


if __name__ == "__main__":
    unittest.main()
