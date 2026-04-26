#!/usr/bin/env python3
"""HOOK_VERSION derivation coverage.

Originally part of a file that also exercised the env-var scenario
bypass; that bypass was removed in amend-protocol Step 4 (factory.ai
holdout principle — agents must not have a single-key escape hatch).
What remains here is the pre-existing HOOK_VERSION test surface, which
is independent of any scenario-enforcement code.
"""
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _sdd_state
from _subprocess_harness import HOOKS_DIR, cleanup_all_state


def _fresh_sdd_state_with_missing_package():
    module_path = HOOKS_DIR / "_sdd_state.py"
    spec = importlib.util.spec_from_file_location("_sdd_state_missing_pkg", module_path)
    module = importlib.util.module_from_spec(spec)
    original_read_text = Path.read_text

    def _fake_read_text(self, *args, **kwargs):
        if self.name == "package.json":
            raise FileNotFoundError("missing package.json")
        return original_read_text(self, *args, **kwargs)

    with patch.object(Path, "read_text", new=_fake_read_text):
        spec.loader.exec_module(module)
    return module


class TestVersionDerivation(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="version-derivation-")

    def tearDown(self):
        cleanup_all_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_hook_version_matches_package_json(self):
        package_json = json.loads((HOOKS_DIR.parent / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(_sdd_state.HOOK_VERSION, package_json["version"])

    def test_hook_version_fallback_on_missing_package_json(self):
        fresh_module = _fresh_sdd_state_with_missing_package()
        self.assertEqual(fresh_module.HOOK_VERSION, "2026.04.0")
        self.assertEqual(fresh_module._read_hook_version(), "2026.04.0")


if __name__ == "__main__":
    unittest.main()
