#!/usr/bin/env python3
"""SCEN-016 — Fast-path rollout infrastructure invariants.

Policies the cascade depends on regardless of the FAST_PATH_ENABLED
default (SCEN-019 owns the default-value policy):

  - Per-edit budget exists and is bounded (no runaway per-edit runs).
  - FAST_PATH_FORCE_FULL_FILES covers mainstream lockfiles (dependency
    resolution changes invalidate everything).
  - FAST_PATH_FORCE_FULL_FILES covers mainstream stack configs
    (runtime-assumption changes test runners can't self-detect).

These are the safety rails for Phase 8's per-edit scoping. When
FAST_PATH_ENABLED=True (Phase 8.1 default), these rails ensure that
lockfile/config edits still force Rung 3 full-suite.
"""
import importlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    _sdd_config = importlib.import_module("_sdd_config")
    _HAS_FAST_PATH_KNOBS = hasattr(_sdd_config, "FAST_PATH_ENABLED")
    _IMPORT_ERR = "" if _HAS_FAST_PATH_KNOBS else "FAST_PATH_ENABLED missing"
except Exception as exc:  # pragma: no cover
    _sdd_config = None
    _HAS_FAST_PATH_KNOBS = False
    _IMPORT_ERR = repr(exc)


@unittest.skipUnless(_HAS_FAST_PATH_KNOBS, f"fast-path knobs missing: {_IMPORT_ERR}")
class TestScen016RolloutInfrastructure(unittest.TestCase):
    """Budget + force-full-files rails that keep the cascade safe."""

    def test_budget_defined(self):
        """FAST_PATH_BUDGET_SECONDS defined and reasonable."""
        self.assertTrue(hasattr(_sdd_config, "FAST_PATH_BUDGET_SECONDS"))
        budget = _sdd_config.FAST_PATH_BUDGET_SECONDS
        self.assertIsInstance(budget, (int, float))
        self.assertGreater(budget, 0)
        self.assertLessEqual(budget, 120,
            f"Budget {budget}s exceeds reasonable per-edit cap")

    def test_force_full_files_includes_lockfiles(self):
        """FAST_PATH_FORCE_FULL_FILES covers mainstream lockfiles."""
        self.assertTrue(hasattr(_sdd_config, "FAST_PATH_FORCE_FULL_FILES"))
        files = _sdd_config.FAST_PATH_FORCE_FULL_FILES
        # Mainstream lockfiles that MUST trigger forced-full
        for lockfile in (
            "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
            "poetry.lock", "uv.lock", "Cargo.lock", "requirements.txt",
        ):
            self.assertIn(lockfile, files,
                f"Lockfile {lockfile} must trigger forced-full-suite")

    def test_force_full_files_includes_configs(self):
        """Stack configs trigger forced-full (Microsoft TIA fall-back-to-all pattern)."""
        files = _sdd_config.FAST_PATH_FORCE_FULL_FILES
        for config in (
            "pyproject.toml", "tsconfig.json", "nx.json", "turbo.json",
            "pytest.ini",
        ):
            self.assertIn(config, files,
                f"Config {config} must trigger forced-full-suite")


if __name__ == "__main__":
    unittest.main()
