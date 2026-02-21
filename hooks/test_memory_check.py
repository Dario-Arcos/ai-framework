#!/usr/bin/env python3
"""Tests for memory-check.py — rules staleness detection and manifest change tracking."""
import hashlib
import importlib
import io
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
memory_check = importlib.import_module("memory-check")


class TestHashFile(unittest.TestCase):
    """Test _hash_file() MD5 hashing."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_hashes_content(self):
        path = os.path.join(self.tmpdir, "hello.txt")
        with open(path, "wb") as f:
            f.write(b"hello")
        expected = hashlib.md5(b"hello").hexdigest()
        self.assertEqual(memory_check._hash_file(path), expected)

    def test_missing_file(self):
        path = os.path.join(self.tmpdir, "nonexistent.txt")
        self.assertIsNone(memory_check._hash_file(path))

    def test_unreadable_file(self):
        with patch("builtins.open", side_effect=PermissionError("denied")):
            self.assertIsNone(memory_check._hash_file("/fake/path"))


class TestRulesMtime(unittest.TestCase):
    """Test _rules_mtime() with real filesystem."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_rules_dir(self):
        self.assertIsNone(memory_check._rules_mtime(self.tmpdir))

    def test_empty_rules_dir(self):
        rules_dir = os.path.join(self.tmpdir, ".claude", "rules")
        os.makedirs(rules_dir)
        self.assertIsNone(memory_check._rules_mtime(self.tmpdir))

    def test_returns_latest_mtime(self):
        rules_dir = os.path.join(self.tmpdir, ".claude", "rules")
        os.makedirs(rules_dir)
        old_file = os.path.join(rules_dir, "old.md")
        new_file = os.path.join(rules_dir, "new.md")
        Path(old_file).write_text("old rules", encoding="utf-8")
        Path(new_file).write_text("new rules", encoding="utf-8")
        # Set distinct mtimes: old at 1000, new at 2000
        os.utime(old_file, (1000, 1000))
        os.utime(new_file, (2000, 2000))
        self.assertEqual(memory_check._rules_mtime(self.tmpdir), 2000.0)


class TestAgeDays(unittest.TestCase):
    """Test _age_days() calculation."""

    def test_zero_days(self):
        _real_time = memory_check.time
        mock_time = type(_real_time)  # module type — but simpler to use a namespace
        # Patch the module-level time reference directly
        import types
        fake_time = types.SimpleNamespace(time=lambda: 1000.0)
        memory_check.time = fake_time
        try:
            self.assertEqual(memory_check._age_days(1000.0), 0)
        finally:
            memory_check.time = _real_time

    def test_multiple_days(self):
        _real_time = memory_check.time
        import types
        mtime = 1000.0
        fake_time = types.SimpleNamespace(time=lambda: mtime + 5 * 86400)
        memory_check.time = fake_time
        try:
            self.assertEqual(memory_check._age_days(mtime), 5)
        finally:
            memory_check.time = _real_time


class TestHasTestInfra(unittest.TestCase):
    """Test _has_test_infra() with real filesystem."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_tests_dir_exists(self):
        os.makedirs(os.path.join(self.tmpdir, "tests"))
        self.assertTrue(memory_check._has_test_infra(self.tmpdir))

    def test_jest_config_exists(self):
        Path(os.path.join(self.tmpdir, "jest.config.ts")).write_text("{}", encoding="utf-8")
        self.assertTrue(memory_check._has_test_infra(self.tmpdir))

    def test_nothing_exists(self):
        self.assertFalse(memory_check._has_test_infra(self.tmpdir))


class TestEnsureBaseline(unittest.TestCase):
    """Test _ensure_baseline() checksums management."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.rules_dir = os.path.join(self.tmpdir, ".claude", "rules")
        os.makedirs(self.rules_dir)
        self.checksums_path = os.path.join(self.rules_dir, ".manifest-checksums")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_creates_checksums_first_time(self):
        # Create a manifest file so there's something to hash
        pkg = os.path.join(self.tmpdir, "package.json")
        Path(pkg).write_text('{"name":"test"}', encoding="utf-8")
        rules_mtime = 1000.0

        memory_check._ensure_baseline(self.tmpdir, rules_mtime)

        self.assertTrue(os.path.exists(self.checksums_path))
        with open(self.checksums_path, "r") as f:
            checksums = json.load(f)
        self.assertEqual(checksums["_sentinel_mtime"], 1000.0)
        expected_hash = hashlib.md5(b'{"name":"test"}').hexdigest()
        self.assertEqual(checksums["package.json"], expected_hash)

    def test_skips_if_sentinel_matches(self):
        rules_mtime = 1000.0
        # Pre-create checksums with matching sentinel
        with open(self.checksums_path, "w") as f:
            json.dump({"_sentinel_mtime": rules_mtime, "package.json": "abc123"}, f)
        original_mtime = os.path.getmtime(self.checksums_path)
        # Small delay to ensure mtime would differ if file were rewritten
        time.sleep(0.05)

        memory_check._ensure_baseline(self.tmpdir, rules_mtime)

        # File should NOT have been rewritten
        self.assertEqual(os.path.getmtime(self.checksums_path), original_mtime)

    def test_rebaselines_on_mtime_change(self):
        # Pre-create checksums with OLD sentinel
        with open(self.checksums_path, "w") as f:
            json.dump({"_sentinel_mtime": 500.0, "package.json": "old_hash"}, f)
        # Create a manifest
        pkg = os.path.join(self.tmpdir, "package.json")
        Path(pkg).write_text('{"version":"2"}', encoding="utf-8")
        new_rules_mtime = 1000.0

        memory_check._ensure_baseline(self.tmpdir, new_rules_mtime)

        with open(self.checksums_path, "r") as f:
            checksums = json.load(f)
        self.assertEqual(checksums["_sentinel_mtime"], new_rules_mtime)
        expected_hash = hashlib.md5(b'{"version":"2"}').hexdigest()
        self.assertEqual(checksums["package.json"], expected_hash)


class TestCheckManifestStaleness(unittest.TestCase):
    """Test _check_manifest_staleness() two-phase detection."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.rules_dir = os.path.join(self.tmpdir, ".claude", "rules")
        os.makedirs(self.rules_dir)
        self.checksums_path = os.path.join(self.rules_dir, ".manifest-checksums")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_manifests(self):
        changed, has_manifest = memory_check._check_manifest_staleness(self.tmpdir, 1000.0)
        self.assertEqual(changed, [])
        self.assertFalse(has_manifest)

    def test_manifest_unchanged(self):
        # Manifest mtime < rules_mtime => not a candidate
        pkg = os.path.join(self.tmpdir, "package.json")
        Path(pkg).write_text('{"name":"test"}', encoding="utf-8")
        os.utime(pkg, (500, 500))
        rules_mtime = 1000.0

        changed, has_manifest = memory_check._check_manifest_staleness(self.tmpdir, rules_mtime)
        self.assertEqual(changed, [])
        self.assertTrue(has_manifest)

    def test_manifest_mtime_changed_content_same(self):
        # Manifest mtime > rules_mtime BUT hash matches baseline => no change
        content = b'{"name":"test"}'
        pkg = os.path.join(self.tmpdir, "package.json")
        with open(pkg, "wb") as f:
            f.write(content)
        rules_mtime = 1000.0
        os.utime(pkg, (2000, 2000))  # mtime after rules

        # Write baseline with matching hash
        content_hash = hashlib.md5(content).hexdigest()
        with open(self.checksums_path, "w") as f:
            json.dump({"_sentinel_mtime": rules_mtime, "package.json": content_hash}, f)

        changed, has_manifest = memory_check._check_manifest_staleness(self.tmpdir, rules_mtime)
        self.assertEqual(changed, [])
        self.assertTrue(has_manifest)

    def test_manifest_content_changed(self):
        # Manifest mtime > rules_mtime AND hash differs from baseline => changed
        pkg = os.path.join(self.tmpdir, "package.json")
        Path(pkg).write_text('{"name":"updated"}', encoding="utf-8")
        rules_mtime = 1000.0
        os.utime(pkg, (2000, 2000))  # mtime after rules

        # Write baseline with DIFFERENT hash
        with open(self.checksums_path, "w") as f:
            json.dump({"_sentinel_mtime": rules_mtime, "package.json": "stale_hash_abc"}, f)

        changed, has_manifest = memory_check._check_manifest_staleness(self.tmpdir, rules_mtime)
        self.assertEqual(changed, ["package.json"])
        self.assertTrue(has_manifest)


class TestMain(unittest.TestCase):
    """Test main() end-to-end with real filesystem + stdout capture."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run_main(self, mock_time_value=None):
        """Helper: run main() capturing stdout, optionally mocking time."""
        import types
        captured = io.StringIO()
        patches = [
            patch("sys.stdin", io.StringIO("")),
            patch("os.getcwd", return_value=self.tmpdir),
            patch("sys.stdout", captured),
        ]
        real_time = None
        if mock_time_value is not None:
            real_time = memory_check.time
            memory_check.time = types.SimpleNamespace(time=lambda: mock_time_value)
        for p in patches:
            p.start()
        try:
            memory_check.main()
        finally:
            for p in patches:
                p.stop()
            if real_time is not None:
                memory_check.time = real_time
        return captured.getvalue()

    def test_no_rules_dir(self):
        output = self._run_main()
        data = json.loads(output)
        context = data["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(context, "No project memory. Suggest /project-init before proceeding.")

    def test_fresh_rules_no_changes(self):
        # Create rules so they exist
        rules_dir = os.path.join(self.tmpdir, ".claude", "rules")
        os.makedirs(rules_dir)
        rule_file = os.path.join(rules_dir, "arch.md")
        Path(rule_file).write_text("# Arch", encoding="utf-8")
        # Set mtime to "now" so rules are fresh
        now = time.time()
        os.utime(rule_file, (now, now))

        output = self._run_main(mock_time_value=now)
        data = json.loads(output)
        # No messages: response should be empty (no hookSpecificOutput or empty context)
        if "hookSpecificOutput" in data:
            context = data["hookSpecificOutput"].get("additionalContext", "")
            # Should NOT contain staleness or "No project memory" messages
            self.assertNotIn("No project memory", context)
            self.assertNotIn("days old", context)
        # If no hookSpecificOutput key at all, that's also valid (empty response)

    def test_stale_rules(self):
        rules_dir = os.path.join(self.tmpdir, ".claude", "rules")
        os.makedirs(rules_dir)
        rule_file = os.path.join(rules_dir, "stack.md")
        Path(rule_file).write_text("# Stack", encoding="utf-8")
        rule_mtime = 1000.0
        os.utime(rule_file, (rule_mtime, rule_mtime))
        # Mock time to be 45 days later
        mock_now = rule_mtime + 45 * 86400

        output = self._run_main(mock_time_value=mock_now)
        data = json.loads(output)
        context = data["hookSpecificOutput"]["additionalContext"]
        self.assertIn("45d old", context)
        self.assertIn("Suggest /project-init", context)

    def test_no_test_infra(self):
        # Create rules + a manifest but NO test infrastructure
        rules_dir = os.path.join(self.tmpdir, ".claude", "rules")
        os.makedirs(rules_dir)
        rule_file = os.path.join(rules_dir, "proj.md")
        Path(rule_file).write_text("# Project", encoding="utf-8")
        now = time.time()
        os.utime(rule_file, (now, now))
        # Create a manifest so has_manifest is True
        pkg = os.path.join(self.tmpdir, "package.json")
        Path(pkg).write_text('{"name":"app"}', encoding="utf-8")
        # Set manifest mtime BEFORE rules so it's not flagged as changed
        os.utime(pkg, (now - 100, now - 100))

        output = self._run_main(mock_time_value=now)
        data = json.loads(output)
        context = data["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(context, "No test infrastructure detected. Flag proactively to user.")


if __name__ == "__main__":
    unittest.main()
