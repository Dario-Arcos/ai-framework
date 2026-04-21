#!/usr/bin/env python3
"""SCEN-019 — FAST_PATH_ENABLED defaults to True + milestone invariance.

Phase 8.1 rollout policy change: cascade ON by default so large projects
get per-edit efficiency automatically. Safety rests on the milestone
gate at TaskCompleted, which runs the full suite regardless of the
per-edit cascade configuration.

Two invariants encoded here:

  (a) Default policy: `_sdd_config.FAST_PATH_ENABLED` is True so fresh
      installs benefit from the cascade without manual opt-in.

  (b) Milestone invariance: `task-completed.py` (the full-suite gate)
      MUST NOT read FAST_PATH_ENABLED nor call
      cascade_impacted_test_command. Its test command is GATE_TEST from
      user config (full suite); cascade affects only per-edit behavior
      in sdd-auto-test.py.

This pair is the safety net for the policy flip: per-edit may scope
tests, but completion always validates the whole suite.
"""
import importlib
import sys
import unittest
from pathlib import Path


HOOKS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HOOKS_DIR))

try:
    _sdd_config = importlib.import_module("_sdd_config")
    _HAS_CONFIG = hasattr(_sdd_config, "FAST_PATH_ENABLED")
    _IMPORT_ERR = "" if _HAS_CONFIG else "FAST_PATH_ENABLED missing"
except Exception as exc:  # pragma: no cover
    _sdd_config = None
    _HAS_CONFIG = False
    _IMPORT_ERR = repr(exc)


@unittest.skipUnless(_HAS_CONFIG, f"_sdd_config missing: {_IMPORT_ERR}")
class TestScen019DefaultAndMilestoneInvariance(unittest.TestCase):
    """Default policy is cascade-ON; milestone gate is independent."""

    def test_fast_path_enabled_by_default(self):
        """Policy: fresh installs get per-edit cascade automatically.

        Rationale: the large-project problem that motivated Phase 8
        (full-suite on every edit = unsustainable) must be solved
        without manual opt-in. Users who prefer the old behavior set
        FAST_PATH_ENABLED=false in .claude/config.json.
        """
        self.assertTrue(
            _sdd_config.FAST_PATH_ENABLED,
            "FAST_PATH_ENABLED must default to True for out-of-the-box "
            "per-edit efficiency on large projects; "
            f"got: {_sdd_config.FAST_PATH_ENABLED!r}",
        )

    def test_milestone_does_not_read_fast_path_enabled(self):
        """task-completed.py must not branch on FAST_PATH_ENABLED.

        Proving the milestone gate is independent of cascade config
        means flipping the per-edit default cannot silently degrade
        the bloc-level quality gate.
        """
        src = (HOOKS_DIR / "task-completed.py").read_text(encoding="utf-8")
        self.assertNotIn(
            "FAST_PATH_ENABLED",
            src,
            "task-completed.py must not reference FAST_PATH_ENABLED; "
            "milestone gate is the safety net and must run full suite "
            "regardless of per-edit cascade configuration.",
        )

    def test_milestone_does_not_invoke_cascade(self):
        """task-completed.py must not call cascade_impacted_test_command.

        Cascade is a per-edit concern (sdd-auto-test.py PostToolUse).
        The milestone gate uses GATE_TEST from user config = full suite.
        """
        src = (HOOKS_DIR / "task-completed.py").read_text(encoding="utf-8")
        self.assertNotIn(
            "cascade_impacted_test_command",
            src,
            "task-completed.py must not invoke cascade_impacted_test_command; "
            "milestone gate must always run full suite (GATE_TEST) to "
            "catch regressions the per-edit cascade may have scoped past.",
        )

    def test_force_full_files_still_defined_when_enabled(self):
        """Safety: when cascade is on, lockfile/config edits still force full.

        FAST_PATH_FORCE_FULL_FILES is the Microsoft-TIA-style fall-back-
        to-all for edits whose impact radius the cascade cannot infer.
        Must remain populated under the new default.
        """
        self.assertTrue(
            hasattr(_sdd_config, "FAST_PATH_FORCE_FULL_FILES"),
            "FAST_PATH_FORCE_FULL_FILES must exist",
        )
        files = _sdd_config.FAST_PATH_FORCE_FULL_FILES
        self.assertGreater(
            len(files),
            5,
            f"FAST_PATH_FORCE_FULL_FILES must cover mainstream lockfiles "
            f"and configs; got only {len(files)} entries",
        )


if __name__ == "__main__":
    unittest.main()
