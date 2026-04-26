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


class TestScenarioHashBinding(unittest.TestCase):
    """Bundle B (F2/F3): evidence is bound to scenario file hashes.

    The verification-before-completion skill records ``scenario_hashes``
    at invocation time. The git-commit gate (consume=True) re-hashes
    current scenarios at commit time and rejects on mismatch — closing
    the bypass where the user edits scenarios after invocation to make
    them match the code.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="f2-hashes-")
        _seed_scenarios(self.tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        path = skill_invoked_path(self.tmpdir, "verification-before-completion")
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass

    def _record_evidence_with_current_hashes(self):
        from _sdd_scenarios import current_scenario_hashes
        hashes = current_scenario_hashes(self.tmpdir)
        write_skill_invoked(
            self.tmpdir,
            "verification-before-completion",
            scenario_hashes=hashes,
        )
        return hashes

    def test_matching_hashes_pass(self):
        """No edits between invocation and consume → not pending."""
        self._record_evidence_with_current_hashes()
        self.assertFalse(
            has_pending_scenarios(self.tmpdir, sid="t1", consume=True)
        )

    def test_edited_scenario_invalidates_evidence(self):
        """Editing a scenario after invocation → consume returns pending."""
        self._record_evidence_with_current_hashes()
        sd = Path(self.tmpdir) / "docs" / "specs" / "f1" / "scenarios"
        scenario_file = sd / "f1.scenarios.md"
        original = scenario_file.read_text(encoding="utf-8")
        scenario_file.write_text(original + "\n## SCEN-402: tampered\n", encoding="utf-8")
        self.assertTrue(
            has_pending_scenarios(self.tmpdir, sid="t1", consume=True)
        )

    def test_new_scenario_invalidates_evidence(self):
        """Adding a new scenario file after invocation → consume returns pending."""
        self._record_evidence_with_current_hashes()
        sd = Path(self.tmpdir) / "docs" / "specs" / "g2" / "scenarios"
        sd.mkdir(parents=True, exist_ok=True)
        (sd / "g2.scenarios.md").write_text(_SCENARIO_FRAGMENT, encoding="utf-8")
        self.assertTrue(
            has_pending_scenarios(self.tmpdir, sid="t1", consume=True)
        )

    def test_removed_scenario_does_not_invalidate(self):
        """Deleting a scenario after invocation is tolerated (subset is OK)."""
        # Seed a SECOND scenario, record evidence over both, then delete one.
        sd = Path(self.tmpdir) / "docs" / "specs" / "g2" / "scenarios"
        sd.mkdir(parents=True, exist_ok=True)
        extra = sd / "g2.scenarios.md"
        extra.write_text(_SCENARIO_FRAGMENT, encoding="utf-8")
        self._record_evidence_with_current_hashes()
        extra.unlink()
        self.assertFalse(
            has_pending_scenarios(self.tmpdir, sid="t1", consume=True)
        )

    def test_evidence_without_hashes_skips_binding_check(self):
        """Backwards-compat: evidence written by old call path (no hashes)
        passes as before — only F1 consume semantics apply."""
        # Old-style write: no scenario_hashes argument.
        write_skill_invoked(self.tmpdir, "verification-before-completion")
        self.assertFalse(
            has_pending_scenarios(self.tmpdir, sid="t1", consume=True)
        )

    def test_consume_returns_hashes_in_state(self):
        """The consumed state dict carries the scenario_hashes map."""
        recorded = self._record_evidence_with_current_hashes()
        from _sdd_state import consume_skill_invoked
        state = consume_skill_invoked(self.tmpdir, "verification-before-completion")
        self.assertIsNotNone(state)
        self.assertEqual(state.get("scenario_hashes"), recorded)

    def test_ralph_mode_parity(self):
        """SCEN-404: scenario hash binding works under `.ralph/specs/` too.

        Mode parity is enforced by `current_scenario_hashes` calling
        `scenario_files(cwd)`, which already iterates every configured
        discovery root. This test pins that behavior with a Ralph-mode
        scenario file alongside the default non-Ralph one.
        """
        ralph_sd = Path(self.tmpdir) / ".ralph" / "specs" / "auth" / "scenarios"
        ralph_sd.mkdir(parents=True, exist_ok=True)
        (ralph_sd / "auth.scenarios.md").write_text(
            _SCENARIO_FRAGMENT, encoding="utf-8",
        )
        # Activate Ralph mode by creating .ralph/config.sh.
        (Path(self.tmpdir) / ".ralph" / "config.sh").write_text(
            'GATE_TEST=""\n', encoding="utf-8",
        )
        recorded = self._record_evidence_with_current_hashes()
        # Ralph scenario must appear in the recorded map.
        self.assertTrue(
            any("auth.scenarios.md" in k for k in recorded),
            f"Ralph scenario missing from evidence: {list(recorded)}",
        )
        # Editing the Ralph scenario should invalidate evidence.
        scenario_file = ralph_sd / "auth.scenarios.md"
        scenario_file.write_text(
            _SCENARIO_FRAGMENT + "\n## SCEN-404b: tampered\n", encoding="utf-8",
        )
        self.assertTrue(
            has_pending_scenarios(self.tmpdir, sid="t1", consume=True)
        )


if __name__ == "__main__":
    unittest.main()
