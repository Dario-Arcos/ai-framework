#!/usr/bin/env python3
"""Phase 7 — real-world multi-step scenarios.

Each test class simulates a realistic user session end-to-end: a fresh
git repo, committed scenarios, a sequence of tool calls, and observable
outcomes. These tests are the strongest evidence of Claude Code
compatibility short of running inside a live Claude Code session
(documented as a dogfood step in the Phase 7 plan).

What these tests add beyond `test_phase7_integration.py` and
`test_phase7_e2e.py`:

  * Multi-step sequences: the same cwd and sid thread through multiple
    hook invocations, matching the actual lifecycle a user would
    experience in a real Claude Code session.
  * Metrics correlation across the sequence: we re-read
    `.claude/metrics.jsonl` at each step and assert the sequence of
    `event` values.
  * Realistic stacks: synthetic Python + JS + Go projects exercise the
    stack-agnostic config path (`SOURCE_EXTENSIONS`, coverage paths).

Not covered (requires a live Claude Code session):
  * Actual `PreToolUse` dispatch from Claude Code to the hook binary.
  * `TaskUpdate` tool invocation through the agent (we simulate the
    stdin shape directly).
  * Skill invocation through the `Skill` tool (we record via
    `skill_invoked_path + _write_json_atomic` directly).

The gap is documented in the C7 citation table: the hook protocol is
SUPPORTED per docs, so subprocess-level verification is expected to
match live behavior modulo Claude Code's own dispatch correctness.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _sdd_state import extract_session_id, project_hash, skill_invoked_path, _write_json_atomic
from _sdd_scenarios import SCENARIO_FILE_SUFFIX

# Phase 10 fixture path: scenarios live under spec folders.
SCENARIO_DIR = ".ralph/specs/real-world/scenarios"
from _subprocess_harness import cleanup_all_state, invoke_hook


_GIT_AVAILABLE = shutil.which("git") is not None

_VALID_SCENARIO = """\
---
name: checkout
created_by: manual
created_at: 2026-04-17T12:00:00Z
---

## SCEN-001: happy path checkout
**Given**: cart with 2 items totaling USD 42.00
**When**: POST /checkout with valid card token 'tok_visa_4242'
**Then**: HTTP 201 with receipt JSON `{"status": "confirmed"}`
**Evidence**: response body + stripe webhook 'charge.succeeded'

## SCEN-002: declined card
**Given**: cart with 1 item costing USD 10.00
**When**: POST /checkout with token 'tok_decline'
**Then**: HTTP 402 with message 'card declined — try another'
**Evidence**: response body + stripe event 'charge.failed'
"""


def _git(args, cwd):
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _init_repo(cwd):
    _git(["init", "-q"], cwd)
    _git(["config", "user.email", "phase7@example.com"], cwd)
    _git(["config", "user.name", "phase7"], cwd)
    Path(cwd, "README.md").write_text("# phase7 real-world\n", encoding="utf-8")
    _git(["add", "README.md"], cwd)
    _git(["commit", "-q", "-m", "init"], cwd)


def _commit_scenario(cwd, name="checkout"):
    scen_dir = Path(cwd) / SCENARIO_DIR
    scen_dir.mkdir(parents=True, exist_ok=True)
    scen_path = scen_dir / f"{name}{SCENARIO_FILE_SUFFIX}"
    scen_path.write_text(_VALID_SCENARIO, encoding="utf-8")
    _git(["add", f"{SCENARIO_DIR}/{name}{SCENARIO_FILE_SUFFIX}"], cwd)
    _git(["commit", "-q", "-m", f"add {name} scenarios"], cwd)
    return scen_path


def _write_ralph_config(cwd):
    ralph = Path(cwd) / ".ralph"
    ralph.mkdir(parents=True, exist_ok=True)
    (ralph / "config.sh").write_text(
        'GATE_TEST=""\nGATE_TYPECHECK=""\nGATE_LINT=""\nGATE_BUILD=""\n'
        'GATE_INTEGRATION=""\nGATE_E2E=""\nGATE_COVERAGE=""\n'
        'MIN_TEST_COVERAGE="0"\n',
        encoding="utf-8",
    )


def _record_skill(cwd, name, sid):
    import time
    path = skill_invoked_path(cwd, name, sid=sid)
    _write_json_atomic(path, {"skill": name, "ts": int(time.time())})


def _record_source_edit(cwd, rel_path, sid):
    from _sdd_detect import record_file_edit
    full = Path(cwd) / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text("VALUE = 42\n", encoding="utf-8")
    record_file_edit(str(cwd), rel_path, sid=sid)


def _read_events(cwd):
    path = Path(cwd) / ".claude" / "metrics.jsonl"
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git required")
class TestRealWorldHappyPath(unittest.TestCase):
    """User writes scenarios, implements, runs verification, commits. No bypass."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-real-happy-")
        self.raw_sid = "real-happy"
        self.sid = extract_session_id({"session_id": self.raw_sid})

    def tearDown(self):
        cleanup_all_state(self.tmpdir, sid=self.sid)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_scenario_to_completion_full_sequence(self):
        _init_repo(self.tmpdir)
        _commit_scenario(self.tmpdir, "checkout")

        # Step 1: attempt edit on scenario → BLOCKED
        scen_path = Path(self.tmpdir) / SCENARIO_DIR / f"checkout{SCENARIO_FILE_SUFFIX}"
        original = scen_path.read_text(encoding="utf-8")
        mutated = original.replace("USD 42.00", "USD 999.00")
        scen_path.write_text(mutated, encoding="utf-8")
        rc, _out, stderr, _t = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": self.tmpdir,
                "session_id": self.raw_sid,
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": str(scen_path),
                    "old_string": original,
                    "new_string": mutated,
                },
            }
        )
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:SCENARIO]"), stderr)

        # Step 2: record verification + source edit + run task-completed → ACCEPTED
        scen_path.write_text(original, encoding="utf-8")  # revert
        _record_skill(self.tmpdir, "verification-before-completion", self.sid)
        _record_skill(self.tmpdir, "sop-code-assist", self.sid)
        _record_source_edit(self.tmpdir, "src/checkout.py", self.sid)
        _write_ralph_config(self.tmpdir)

        rc, _out, stderr, _t = invoke_hook(
            "task-completed.py",
            {
                "cwd": self.tmpdir,
                "task_subject": "Ship checkout",
                "teammate_name": "impl-checkout",
                "session_id": self.raw_sid,
            }
        )
        self.assertEqual(rc, 0, stderr)
        self.assertIn("Scenario IDs validated", stderr)

        # Step 3: verify metric sequence
        events = _read_events(self.tmpdir)
        guard_events = [e for e in events if e.get("event") == "guard_triggered"]
        task_events = [e for e in events if e.get("event") == "task_completed"]
        self.assertTrue(guard_events, "missing guard_triggered")
        self.assertTrue(task_events, "missing task_completed")
        self.assertEqual(guard_events[0]["category"], "SCENARIO")
        self.assertTrue(task_events[-1].get("scenarios_gated"))


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git required")
class TestRealWorldRewardHackingAttempt(unittest.TestCase):
    """User tries several reward-hacking vectors; each is blocked or bypassed as documented."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-real-hack-")
        self.raw_sid = "real-hack"
        self.sid = extract_session_id({"session_id": self.raw_sid})

    def tearDown(self):
        cleanup_all_state(self.tmpdir, sid=self.sid)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_quoted_path_bash_bypass_blocked(self):
        _init_repo(self.tmpdir)
        _commit_scenario(self.tmpdir, "auth")
        rc, _out, stderr, _t = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": self.tmpdir,
                "tool_name": "Bash",
                "tool_input": {
                    "command": f"sed -i 's/foo/bar/' \"{SCENARIO_DIR}/auth.scenarios.md\"",
                },
            }
        )
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:SCENARIO]"), stderr)

    def test_symlink_bypass_blocked(self):
        _init_repo(self.tmpdir)
        scen_path = _commit_scenario(self.tmpdir, "auth")
        target = Path(self.tmpdir) / "external-attacker.md"
        target.write_text("fake\n", encoding="utf-8")
        scen_path.unlink()
        scen_path.symlink_to(target)
        rc, _out, stderr, _t = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": self.tmpdir,
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": str(scen_path),
                    "old_string": "x",
                    "new_string": "y",
                },
            }
        )
        self.assertEqual(rc, 2)
        self.assertIn("symlink", stderr.lower())

    def test_python_c_bypass_succeeds_as_documented(self):
        """Threat model Pragmatic: arbitrary script execution is out of scope."""
        _init_repo(self.tmpdir)
        scen_path = _commit_scenario(self.tmpdir, "auth")
        snippet = f"open({str(scen_path)!r}, 'w').write('mutated\\n')"
        result = subprocess.run(
            [sys.executable, "-c", snippet],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(scen_path.read_text(), "mutated\n")


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git required")
class TestRealWorldAmendFlow(unittest.TestCase):
    """sop-reviewer + amend marker unlocks edit → new commit invalidates marker → edit blocked again."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-real-amend-")
        self.raw_sid = "real-amend"
        self.sid = extract_session_id({"session_id": self.raw_sid})

    def tearDown(self):
        cleanup_all_state(self.tmpdir, sid=self.sid)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_marker_round_trip(self):
        _init_repo(self.tmpdir)
        scen_path = _commit_scenario(self.tmpdir, "auth")
        original = scen_path.read_text(encoding="utf-8")
        updated = original.replace("USD 42.00", "USD 45.00")
        scen_path.write_text(updated, encoding="utf-8")

        # Without marker: blocked
        rc, _out, _err, _t = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": self.tmpdir,
                "session_id": self.raw_sid,
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": str(scen_path),
                    "old_string": original,
                    "new_string": updated,
                },
            }
        )
        self.assertEqual(rc, 2)

        # With marker for current HEAD + sop-reviewer skill invoked: allowed
        head_sha = _git(["rev-parse", "HEAD"], self.tmpdir).stdout.strip()
        marker_dir = Path(self.tmpdir) / SCENARIO_DIR / ".amends"
        marker_dir.mkdir(parents=True, exist_ok=True)
        (marker_dir / f"auth-{head_sha}.marker").write_text("ok\n", encoding="utf-8")
        _record_skill(self.tmpdir, "sop-reviewer", self.sid)

        rc, _out, _err, _t = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": self.tmpdir,
                "session_id": self.raw_sid,
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": str(scen_path),
                    "old_string": original,
                    "new_string": updated,
                },
            }
        )
        self.assertEqual(rc, 0)

        # New commit advances HEAD → marker invalidated
        Path(self.tmpdir, "bump.txt").write_text("x\n", encoding="utf-8")
        _git(["add", "bump.txt"], self.tmpdir)
        _git(["commit", "-q", "-m", "bump"], self.tmpdir)
        rc, _out, _err, _t = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": self.tmpdir,
                "session_id": self.raw_sid,
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": str(scen_path),
                    "old_string": original,
                    "new_string": updated,
                },
            }
        )
        self.assertEqual(rc, 2)


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git required")
class TestRealWorldBackwardCompat(unittest.TestCase):
    """Project WITHOUT `.claude/scenarios/` must behave exactly as pre-Phase-3."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-real-compat-")

    def tearDown(self):
        cleanup_all_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_scenarios_dir_means_hooks_are_transparent(self):
        # No .claude/scenarios/ created. No git init either — backward-compat scope.
        rc, _out, stderr, _t = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": self.tmpdir,
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": str(Path(self.tmpdir) / "src" / "app.py"),
                    "old_string": "x = 1\n",
                    "new_string": "x = 2\n",
                },
            }
        )
        self.assertEqual(rc, 0, stderr)
        self.assertNotIn("[SDD:", stderr)

    def test_no_scenarios_taskupdate_completed_allowed(self):
        rc, _out, stderr, _t = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": self.tmpdir,
                "tool_name": "TaskUpdate",
                "tool_input": {"status": "completed", "taskId": "T-1"},
            }
        )
        self.assertEqual(rc, 0, stderr)


if __name__ == "__main__":
    unittest.main()
