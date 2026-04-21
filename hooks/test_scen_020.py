#!/usr/bin/env python3
"""SCEN-020 — Parent-branch scenario authorship: mechanical enforcement.

Phase 9.1. Closes the last procedural hole in the factory.ai holdout
contract: Ralph teammates run inside git worktrees and — until now —
could author NEW `.claude/scenarios/*.scenarios.md` files inside their
worktree, bypassing the parent-branch holdout.

Before fix: `sdd-test-guard.py` scenario write-once guard permitted
first-write of untracked scenario files. Behavior was:
    baseline_hash is None  →  allow (first-write)
That rule is correct for the LEADER authoring on parent branch. It
is wrong for a TEAMMATE authoring inside a worktree — they should
inherit scenarios from the branch, never author fresh.

After fix: worktree detection splits the two cases.
    main clone + untracked scenario  →  allow (leader authorship)
    worktree + untracked scenario    →  DENY (reward-hacking vector)
Edit on a tracked scenario falls through to the existing write-once
guard (SCEN-001..011) — this test does not re-verify that path.

Red-green contract:
    1. Pre-fix, worktree first-write passes silently (exit 0).
    2. Post-fix, worktree first-write denies with [SDD:SCENARIO]
       prefix; main-clone first-write still passes (no regression).
    3. Bypass env `_SDD_DISABLE_SCENARIOS=1` honored in both contexts.

Ralph + non-Ralph coverage:
    Ralph     → worktree context → DENY
    Non-Ralph → main clone → ALLOW (dev author scenarios interactively)
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _subprocess_harness import cleanup_all_state, invoke_hook


_VALID_SCENARIO = """\
---
name: worktree-enforcement
created_by: leader
created_at: 2026-04-21T00:00:00Z
---

## SCEN-001: leader authors scenarios on parent branch
**Given**: factory-grade holdout contract
**When**: teammate worktree attempts first-write of a new scenario
**Then**: PreToolUse denies with [SDD:SCENARIO] parent-branch-only
**Evidence**: exit code 2, stderr contains parent-branch or worktree tokens
"""


def _require_git():
    try:
        subprocess.run(
            ["git", "--version"],
            check=True, capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise unittest.SkipTest(f"git not available: {exc}")


def _git_init_main_clone(path):
    """Initialize a plain git repo at path (the 'main clone')."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    for cmd in (
        ["git", "-C", str(path), "init", "-q"],
        ["git", "-C", str(path), "config", "user.email", "t@t.com"],
        ["git", "-C", str(path), "config", "user.name", "tester"],
    ):
        subprocess.run(cmd, check=True, env=env, capture_output=True,
                       text=True, timeout=5)
    # Need an initial commit for worktree add to work
    readme = Path(path) / "README.md"
    readme.write_text("seed\n", encoding="utf-8")
    for cmd in (
        ["git", "-C", str(path), "add", "README.md"],
        ["git", "-C", str(path), "commit", "-q", "-m", "seed"],
    ):
        subprocess.run(cmd, check=True, env=env, capture_output=True,
                       text=True, timeout=5)


def _git_add_worktree(main_path, worktree_path, branch_name):
    """Add a new worktree on a new branch from main clone."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    subprocess.run(
        ["git", "-C", str(main_path),
         "worktree", "add", "-b", branch_name, str(worktree_path)],
        check=True, env=env, capture_output=True, text=True, timeout=10,
    )


class TestScen020ParentBranchScenarioEnforcement(unittest.TestCase):
    """Worktree context + new scenario file = deny; main clone = allow."""

    @classmethod
    def setUpClass(cls):
        _require_git()

    def setUp(self):
        self.base = tempfile.mkdtemp(prefix="sdd-scen020-")
        self.main_clone = Path(self.base) / "main-clone"
        self.worktree = Path(self.base) / "teammate-worktree"
        self.main_clone.mkdir(parents=True)
        _git_init_main_clone(self.main_clone)
        _git_add_worktree(self.main_clone, self.worktree, "teammate-A")

    def tearDown(self):
        cleanup_all_state(str(self.main_clone))
        cleanup_all_state(str(self.worktree))
        shutil.rmtree(self.base, ignore_errors=True)

    def _write_scenario_payload(self, cwd, filename):
        """Build a PreToolUse payload for authoring a new scenario file."""
        rel = f".claude/scenarios/{filename}"
        abs_path = str(Path(cwd) / rel)
        return {
            "cwd": str(cwd),
            "tool_name": "Write",
            "tool_input": {
                "file_path": abs_path,
                "content": _VALID_SCENARIO,
            },
        }

    def test_worktree_new_scenario_denied(self):
        """Ralph mode: teammate worktree must not author fresh scenarios."""
        payload = self._write_scenario_payload(
            self.worktree, "teammate-authored.scenarios.md"
        )
        rc, _stdout, stderr, _elapsed = invoke_hook(
            "sdd-test-guard.py", payload,
        )
        self.assertEqual(
            rc, 2,
            f"Worktree first-write of new scenario must be denied "
            f"(Ralph holdout contract); got exit={rc}, stderr={stderr!r}",
        )
        self.assertTrue(
            "[SDD:SCENARIO]" in stderr,
            f"Denial must carry [SDD:SCENARIO] category prefix; "
            f"got: {stderr!r}",
        )
        self.assertTrue(
            any(tok in stderr.lower() for tok in ("parent", "worktree", "holdout")),
            f"Denial stderr must explain the parent-branch contract; "
            f"got: {stderr!r}",
        )

    def test_main_clone_new_scenario_allowed(self):
        """Non-Ralph mode: dev on main clone can author scenarios interactively."""
        payload = self._write_scenario_payload(
            self.main_clone, "dev-authored.scenarios.md"
        )
        rc, _stdout, stderr, _elapsed = invoke_hook(
            "sdd-test-guard.py", payload,
        )
        self.assertEqual(
            rc, 0,
            f"Main clone first-write of new scenario must be allowed "
            f"(leader authorship); got exit={rc}, stderr={stderr!r}",
        )

    def test_worktree_existing_scenario_falls_through_to_write_once(self):
        """Existing tracked scenario in worktree uses existing SCEN-011 guard.

        Setup: commit scenario on main BEFORE creating a fresh worktree. The
        worktree branches from that commit and inherits the tracked scenario.
        Attempting divergent Edit must be caught by the pre-existing write-once
        guard (SCEN-011), not by the new Phase 9.1 worktree-first-write guard.
        Proves 9.1 does not over-reach onto tracked files.
        """
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        scenario_rel = ".claude/scenarios/shared.scenarios.md"
        scenario_abs = self.main_clone / scenario_rel
        scenario_abs.parent.mkdir(parents=True, exist_ok=True)
        scenario_abs.write_text(_VALID_SCENARIO, encoding="utf-8")
        for cmd in (
            ["git", "-C", str(self.main_clone), "add", scenario_rel],
            ["git", "-C", str(self.main_clone), "commit", "-q", "-m", "seed scenario"],
        ):
            subprocess.run(cmd, check=True, env=env, capture_output=True,
                           text=True, timeout=5)
        # Create a FRESH worktree AFTER the scenario is committed so it
        # inherits the tracked file at branch creation. The setUp worktree
        # predates the scenario commit and does not have it tracked.
        fresh_worktree = Path(self.base) / "fresh-teammate"
        subprocess.run(
            ["git", "-C", str(self.main_clone),
             "worktree", "add", "-b", "fresh-teammate", str(fresh_worktree)],
            check=True, env=env, capture_output=True, text=True, timeout=10,
        )
        worktree_scenario = fresh_worktree / scenario_rel
        self.assertTrue(worktree_scenario.exists(),
                        "Precondition: scenario must exist in fresh worktree")
        payload = {
            "cwd": str(fresh_worktree),
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(worktree_scenario),
                "old_string": "leader authors scenarios on parent branch",
                "new_string": "REWARD HACKED FROM WORKTREE",
            },
        }
        rc, _stdout, stderr, _elapsed = invoke_hook(
            "sdd-test-guard.py", payload,
        )
        self.assertEqual(
            rc, 2,
            f"Divergent Edit on tracked scenario in worktree must deny "
            f"via existing write-once guard; got exit={rc}, stderr={stderr!r}",
        )
        self.assertTrue(
            "write-once" in stderr.lower() or "violation" in stderr.lower(),
            f"Denial must cite write-once contract (existing SCEN-011 guard), "
            f"not the worktree-first-write guard; got: {stderr!r}",
        )

    def test_worktree_bypass_env_honored(self):
        """_SDD_DISABLE_SCENARIOS=1 bypasses the new guard (existing pattern)."""
        payload = self._write_scenario_payload(
            self.worktree, "bypassed.scenarios.md"
        )
        rc, _stdout, stderr, _elapsed = invoke_hook(
            "sdd-test-guard.py", payload,
            env={"_SDD_DISABLE_SCENARIOS": "1"},
        )
        self.assertEqual(
            rc, 0,
            f"Bypass env must allow worktree first-write; "
            f"got exit={rc}, stderr={stderr!r}",
        )

    def test_worktree_non_scenario_file_unaffected(self):
        """Guard targets only .claude/scenarios/ — other files in worktree must pass."""
        other_path = self.worktree / "src" / "feature.py"
        payload = {
            "cwd": str(self.worktree),
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(other_path),
                "content": "def feature():\n    return 42\n",
            },
        }
        rc, _stdout, stderr, _elapsed = invoke_hook(
            "sdd-test-guard.py", payload,
        )
        self.assertEqual(
            rc, 0,
            f"Non-scenario files in worktree must not be affected; "
            f"got exit={rc}, stderr={stderr!r}",
        )


if __name__ == "__main__":
    unittest.main()
