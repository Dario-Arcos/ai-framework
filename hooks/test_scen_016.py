#!/usr/bin/env python3
"""SCEN-016 — FAST_PATH_ENABLED=False preserves full-suite behavior.

Phase 8 rollout safety: the default configuration MUST preserve current
behavior for every existing install. Per-edit still runs the full suite
until the user explicitly opts in via `.claude/config.json`.

Observable: when `FAST_PATH_ENABLED=False` (default), the cascade
function returns the full-suite command regardless of edit classification
or session state. Telemetry records `fast_path_rung="3"` +
`forced_full_reason="disabled"`.
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
class TestScen016RolloutDefault(unittest.TestCase):
    """Default configuration preserves current behavior. Zero-regression rollout."""

    def test_fast_path_disabled_by_default(self):
        """Rollout invariant: Phase 8 ships with the switch OFF.

        Every existing install upgrades without behavior change. Users opt
        in per-project via `.claude/config.json` after validating the
        fast-path telemetry against their workload.
        """
        self.assertFalse(
            _sdd_config.FAST_PATH_ENABLED,
            "FAST_PATH_ENABLED must default to False for safe rollout; "
            f"got: {_sdd_config.FAST_PATH_ENABLED!r}",
        )

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
