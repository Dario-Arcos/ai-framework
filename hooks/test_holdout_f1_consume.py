"""F1 holdout enforcement — consume_skill_invoked tests.

Closes the bypass where a single `verification-before-completion` skill
invocation satisfies every commit inside the 30-min TTL window. With
the consume-on-read semantics, the underlying flag file is atomically
read-and-deleted by the git-commit gate. The next commit must invoke
the skill again.

Spec: docs/specs/2026-04-26-holdout-enforcement/
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _sdd_state import (
    consume_skill_invoked,
    read_skill_invoked,
    skill_invoked_path,
    write_skill_invoked,
)
from _sdd_scenarios import has_pending_scenarios

import _sdd_scenarios as scen_mod


_SCENARIO_FRAGMENT = """---
name: f1-holdout-consume
created_by: manual
created_at: 2026-04-26T00:00:00Z
---

## SCEN-401: placeholder
**Given**: tmp scenario
**When**: probe runs
**Then**: pending scenarios returns sane state
**Evidence**: this file
"""


def _seed_scenarios(cwd):
    """Place a scenario file under docs/specs/ so scenarios exist."""
    sd = Path(cwd) / "docs" / "specs" / "f1" / "scenarios"
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "f1.scenarios.md").write_text(_SCENARIO_FRAGMENT, encoding="utf-8")


class TestConsumeSkillInvoked(unittest.TestCase):
    """Unit-level tests for `_sdd_state.consume_skill_invoked`."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="f1-")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        # Clean up any flag file that may have been written for this cwd.
        path = skill_invoked_path(self.tmpdir, "verification-before-completion")
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass

    def test_consume_returns_dict_then_none(self):
        """First consume returns the state; second consume returns None."""
        write_skill_invoked(self.tmpdir, "verification-before-completion")
        first = consume_skill_invoked(self.tmpdir, "verification-before-completion")
        self.assertIsNotNone(first)
        self.assertEqual(first.get("skill"), "verification-before-completion")
        second = consume_skill_invoked(self.tmpdir, "verification-before-completion")
        self.assertIsNone(second)

    def test_consume_when_no_flag_returns_none(self):
        """Consuming a non-existent flag returns None without raising."""
        # Make sure no flag exists (setUp already cleaned)
        result = consume_skill_invoked(self.tmpdir, "verification-before-completion")
        self.assertIsNone(result)

    def test_consume_deletes_underlying_file(self):
        """After consume, the file must not exist on disk."""
        write_skill_invoked(self.tmpdir, "verification-before-completion")
        path = skill_invoked_path(self.tmpdir, "verification-before-completion")
        self.assertTrue(os.path.exists(path), "flag file should exist before consume")
        consume_skill_invoked(self.tmpdir, "verification-before-completion")
        self.assertFalse(os.path.exists(path), "flag file MUST be deleted after consume")

    def test_read_does_not_delete(self):
        """Persistent `read_skill_invoked` semantics preserved."""
        write_skill_invoked(self.tmpdir, "verification-before-completion")
        path = skill_invoked_path(self.tmpdir, "verification-before-completion")
        first = read_skill_invoked(self.tmpdir, "verification-before-completion")
        self.assertIsNotNone(first)
        self.assertTrue(os.path.exists(path), "read must NOT delete the file")
        second = read_skill_invoked(self.tmpdir, "verification-before-completion")
        self.assertIsNotNone(second, "second read must still return data")


class TestHasPendingScenariosConsume(unittest.TestCase):
    """`has_pending_scenarios(cwd, sid, consume=...)` semantics."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="f1-pending-")
        _seed_scenarios(self.tmpdir)
        # Force discovery roots to non-Ralph mode for determinism by
        # creating only docs/specs/ — `.ralph/specs` will be absent so
        # only docs/specs is in the roots tuple.

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_consume_false_preserves_flag(self):
        """consume=False (default) reads but does NOT delete the flag."""
        write_skill_invoked(self.tmpdir, "verification-before-completion")
        # First call: scenarios exist, flag exists → not pending
        self.assertFalse(has_pending_scenarios(self.tmpdir, sid="t1"))
        # Second call: flag still there → still not pending
        self.assertFalse(has_pending_scenarios(self.tmpdir, sid="t1"))

    def test_consume_true_one_shot(self):
        """consume=True removes the flag — second check pending=True."""
        write_skill_invoked(self.tmpdir, "verification-before-completion")
        # First check WITH consume: not pending (flag was there)
        self.assertFalse(
            has_pending_scenarios(self.tmpdir, sid="t1", consume=True)
        )
        # Second check (any mode) — flag consumed → pending
        self.assertTrue(has_pending_scenarios(self.tmpdir, sid="t1"))
        self.assertTrue(
            has_pending_scenarios(self.tmpdir, sid="t1", consume=True)
        )

    def test_no_flag_returns_pending(self):
        """When no flag exists, has_pending_scenarios returns True regardless of consume."""
        # No write_skill_invoked called.
        self.assertTrue(has_pending_scenarios(self.tmpdir, sid="t1"))
        self.assertTrue(
            has_pending_scenarios(self.tmpdir, sid="t1", consume=True)
        )

    def test_no_scenarios_returns_false(self):
        """No scenarios under discovery roots → not pending, regardless of flag."""
        empty = tempfile.mkdtemp(prefix="f1-empty-")
        try:
            self.assertFalse(has_pending_scenarios(empty, sid="t1"))
            self.assertFalse(has_pending_scenarios(empty, sid="t1", consume=True))
        finally:
            import shutil
            shutil.rmtree(empty, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
