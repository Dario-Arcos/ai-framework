#!/usr/bin/env python3
"""Tests for session-start.py — SessionStart hook for AI Framework plugin."""
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
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
session_start = importlib.import_module("session-start")


class TestActiveGitignoreRules(unittest.TestCase):
    """Test active_gitignore_rules() filtering logic."""

    def test_filters_comments_and_empty(self):
        content = "# comment\n\n/.claude/*"
        result = session_start.active_gitignore_rules(content)
        self.assertEqual(result, {"/.claude/*"})

    def test_all_comments(self):
        content = "# only comments\n# another comment"
        result = session_start.active_gitignore_rules(content)
        self.assertEqual(result, set())

    def test_preserves_all_rules(self):
        content = "/.claude/*\n!/.claude/rules/\n/CLAUDE.md"
        result = session_start.active_gitignore_rules(content)
        self.assertEqual(result, {"/.claude/*", "!/.claude/rules/", "/CLAUDE.md"})


class TestMigrateClaudeGitignore(unittest.TestCase):
    """Test migrate_claude_gitignore() rule migration."""

    def test_migrates_old_rule(self):
        content = "/.claude/\n/other\n"
        result = session_start.migrate_claude_gitignore(content)
        self.assertIn("/.claude/*", result)
        self.assertNotIn("/.claude/\n", result)

    def test_preserves_new_rule(self):
        content = "/.claude/*\n/other\n"
        result = session_start.migrate_claude_gitignore(content)
        self.assertEqual(result, content)


class TestRemoveTemplateSuffix(unittest.TestCase):
    """Test remove_template_suffix() path transformation."""

    def test_removes_suffix(self):
        result = session_start.remove_template_suffix("foo.template")
        self.assertEqual(result, "foo")

    def test_nested_template_dirs(self):
        result = session_start.remove_template_suffix(
            ".claude.template/settings.json.template"
        )
        self.assertEqual(result, ".claude/settings.json")


class TestEnsureGitignoreRules(unittest.TestCase):
    """Test ensure_gitignore_rules() with real filesystem."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.plugin_root = Path(self.tmpdir) / "plugin"
        self.project_dir = Path(self.tmpdir) / "project"
        self.plugin_root.mkdir()
        self.project_dir.mkdir()
        self.template_dir = self.plugin_root / "template"
        self.template_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_gitignore_copies_template(self):
        template_gi = self.template_dir / "gitignore.template"
        template_gi.write_text("/.claude/*\n!/.claude/rules/\n", encoding="utf-8")

        session_start.ensure_gitignore_rules(self.plugin_root, self.project_dir)

        project_gi = self.project_dir / ".gitignore"
        self.assertTrue(project_gi.exists())
        content = project_gi.read_text(encoding="utf-8")
        self.assertIn("/.claude/*", content)

    def test_adds_missing_rules(self):
        project_gi = self.project_dir / ".gitignore"
        project_gi.write_text("node_modules/\n", encoding="utf-8")

        session_start.ensure_gitignore_rules(self.plugin_root, self.project_dir)

        content = project_gi.read_text(encoding="utf-8")
        self.assertIn("node_modules/", content)
        for rule in session_start.CRITICAL_GITIGNORE_RULES:
            self.assertIn(rule, content)

    def test_existing_rule_not_duplicated_when_other_rules_missing(self):
        project_gi = self.project_dir / ".gitignore"
        project_gi.write_text(
            "node_modules/\n!/.claude/scenarios/\n",
            encoding="utf-8",
        )

        session_start.ensure_gitignore_rules(self.plugin_root, self.project_dir)

        content = project_gi.read_text(encoding="utf-8")
        self.assertEqual(content.count("!/.claude/scenarios/\n"), 1)
        for rule in session_start.CRITICAL_GITIGNORE_RULES:
            self.assertIn(rule, content)

    def test_all_rules_present_no_change(self):
        all_rules = "\n".join(session_start.CRITICAL_GITIGNORE_RULES) + "\n"
        project_gi = self.project_dir / ".gitignore"
        project_gi.write_text(all_rules, encoding="utf-8")

        session_start.ensure_gitignore_rules(self.plugin_root, self.project_dir)

        content = project_gi.read_text(encoding="utf-8")
        self.assertEqual(content, all_rules)

    def test_migrates_and_adds(self):
        project_gi = self.project_dir / ".gitignore"
        # Old rule /.claude/ + missing other rules
        project_gi.write_text("/.claude/\n", encoding="utf-8")

        session_start.ensure_gitignore_rules(self.plugin_root, self.project_dir)

        content = project_gi.read_text(encoding="utf-8")
        # Old rule migrated
        self.assertIn("/.claude/*", content)
        self.assertNotIn("/.claude/\n", content.split("/.claude/*")[0])
        # Missing rules added
        for rule in session_start.CRITICAL_GITIGNORE_RULES:
            self.assertIn(rule, content)


class TestSyncTemplateGitignoreOnce(unittest.TestCase):
    """Test one-time sync of template gitignore rules on template change."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.plugin_root = Path(self.tmpdir) / "plugin"
        self.project_dir = Path(self.tmpdir) / "project"
        self.plugin_root.mkdir()
        self.project_dir.mkdir()
        self.template_dir = self.plugin_root / "template"
        self.template_dir.mkdir()
        (self.project_dir / ".claude").mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_template_changed_adds_missing_rules(self):
        """Scenario 1: plugin updates template with new rule → existing project gets it."""
        template = self.template_dir / "gitignore.template"
        template.write_text("/.claude/*\n/.visual-companion/\n", encoding="utf-8")
        project_gi = self.project_dir / ".gitignore"
        project_gi.write_text("/.claude/*\nnode_modules/\n", encoding="utf-8")

        session_start.sync_template_gitignore_once(self.plugin_root, self.project_dir)

        content = project_gi.read_text(encoding="utf-8")
        self.assertIn("/.visual-companion/", content)
        self.assertIn("node_modules/", content)  # preserved

    def test_template_unchanged_no_modification(self):
        """Scenario 2: template hash matches → .gitignore untouched."""
        template = self.template_dir / "gitignore.template"
        template.write_text("/.claude/*\n", encoding="utf-8")
        project_gi = self.project_dir / ".gitignore"
        project_gi.write_text("/.claude/*\n", encoding="utf-8")

        # First call stores hash
        session_start.sync_template_gitignore_once(self.plugin_root, self.project_dir)
        mtime_before = project_gi.stat().st_mtime

        # Second call — same template, should not touch .gitignore
        time.sleep(0.01)
        session_start.sync_template_gitignore_once(self.plugin_root, self.project_dir)
        mtime_after = project_gi.stat().st_mtime

        self.assertEqual(mtime_before, mtime_after)

    def test_no_gitignore_skips(self):
        """Scenario 3: no .gitignore exists → skip (ensure_gitignore_rules handles creation)."""
        template = self.template_dir / "gitignore.template"
        template.write_text("/.claude/*\n", encoding="utf-8")

        session_start.sync_template_gitignore_once(self.plugin_root, self.project_dir)

        self.assertFalse((self.project_dir / ".gitignore").exists())

    def test_no_template_skips(self):
        """Scenario 4: no template file → skip."""
        project_gi = self.project_dir / ".gitignore"
        project_gi.write_text("node_modules/\n", encoding="utf-8")

        session_start.sync_template_gitignore_once(self.plugin_root, self.project_dir)

        content = project_gi.read_text(encoding="utf-8")
        self.assertEqual(content, "node_modules/\n")


class TestMain(unittest.TestCase):
    """Test main() entry point with mocked filesystem and I/O."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.plugin_root = Path(self.tmpdir) / "plugin"
        self.project_dir = Path(self.tmpdir) / "project"
        self.plugin_root.mkdir()
        self.project_dir.mkdir()
        # Create minimal template structure
        template_dir = self.plugin_root / "template"
        template_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch.dict(os.environ, {}, clear=False)
    def test_happy_path(self):
        env_patch = {"CLAUDE_PLUGIN_ROOT": str(self.plugin_root)}
        stdout_capture = io.StringIO()

        with patch.dict(os.environ, env_patch), \
             patch("sys.stdin", io.StringIO("{}")), \
             patch("sys.stdout", stdout_capture), \
             patch("sys.stderr", io.StringIO()), \
             patch.object(session_start, "find_project_dir", return_value=self.project_dir), \
             self.assertRaises(SystemExit) as cm:
            session_start.main()

        self.assertEqual(cm.exception.code, 0)
        output = json.loads(stdout_capture.getvalue())
        # Success path: no additionalContext injected (empty JSON)
        self.assertNotIn("hookSpecificOutput", output)

    def test_plugin_root_missing(self):
        nonexistent = str(self.plugin_root / "does-not-exist")
        env_patch = {"CLAUDE_PLUGIN_ROOT": nonexistent}
        stdout_capture = io.StringIO()

        with patch.dict(os.environ, env_patch), \
             patch("sys.stdin", io.StringIO("{}")), \
             patch("sys.stdout", stdout_capture), \
             patch("sys.stderr", io.StringIO()), \
             self.assertRaises(SystemExit) as cm:
            session_start.main()

        self.assertEqual(cm.exception.code, 1)
        output = json.loads(stdout_capture.getvalue())
        self.assertIn("not found", output["hookSpecificOutput"]["additionalContext"])

    def test_env_override_plugin_root(self):
        env_patch = {"CLAUDE_PLUGIN_ROOT": str(self.plugin_root)}
        stdout_capture = io.StringIO()

        with patch.dict(os.environ, env_patch), \
             patch("sys.stdin", io.StringIO("{}")), \
             patch("sys.stdout", stdout_capture), \
             patch("sys.stderr", io.StringIO()), \
             patch.object(session_start, "find_project_dir", return_value=self.project_dir), \
             self.assertRaises(SystemExit) as cm:
            session_start.main()

        self.assertEqual(cm.exception.code, 0)
        output = json.loads(stdout_capture.getvalue())
        # Success path: no additionalContext (silent success)
        self.assertNotIn("hookSpecificOutput", output)

    def test_exception_handled(self):
        env_patch = {"CLAUDE_PLUGIN_ROOT": str(self.plugin_root)}
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        def exploding_project_dir():
            raise RuntimeError("Simulated failure")

        with patch.dict(os.environ, env_patch), \
             patch("sys.stdin", io.StringIO("{}")), \
             patch("sys.stdout", stdout_capture), \
             patch("sys.stderr", stderr_capture), \
             patch.object(session_start, "find_project_dir", side_effect=exploding_project_dir), \
             self.assertRaises(SystemExit) as cm:
            session_start.main()

        self.assertEqual(cm.exception.code, 1)
        self.assertIn("Simulated failure", stderr_capture.getvalue())
        output = json.loads(stdout_capture.getvalue())
        self.assertIn("Simulated failure", output["hookSpecificOutput"]["additionalContext"])


class TestCleanupStaleSdd(unittest.TestCase):
    """cleanup_stale_sdd must age-based purge; never touch live files or dirs."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_gettempdir = tempfile.gettempdir
        # Redirect the function's internal tempdir lookup to our sandbox.
        # cleanup_stale_sdd calls Path(tempfile.gettempdir()) — patch module-level.
        self._patcher = patch.object(session_start.tempfile, "gettempdir",
                                      return_value=self.tmpdir)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_old_files_unlinked(self):
        """Files older than max_age are removed."""
        old = Path(self.tmpdir) / "sdd-test-old.json"
        old.write_text("old", encoding="utf-8")
        stale = time.time() - 172800  # 48h ago
        os.utime(old, (stale, stale))

        session_start.cleanup_stale_sdd(max_age=86400)

        self.assertFalse(old.exists(), "Stale file should be unlinked")

    def test_fresh_files_preserved(self):
        """Files within max_age are kept."""
        fresh = Path(self.tmpdir) / "sdd-test-fresh.json"
        fresh.write_text("fresh", encoding="utf-8")

        session_start.cleanup_stale_sdd(max_age=86400)

        self.assertTrue(fresh.exists(), "Fresh file must be preserved")

    def test_directories_skipped(self):
        """Directories matching sdd-* glob must not be removed."""
        d = Path(self.tmpdir) / "sdd-something-dir"
        d.mkdir()
        stale = time.time() - 172800
        os.utime(d, (stale, stale))

        session_start.cleanup_stale_sdd(max_age=86400)

        self.assertTrue(d.exists(), "Directories must be skipped")

    def test_non_sdd_files_untouched(self):
        """Files not matching sdd-* glob are ignored entirely."""
        other = Path(self.tmpdir) / "unrelated-old.tmp"
        other.write_text("old", encoding="utf-8")
        stale = time.time() - 172800
        os.utime(other, (stale, stale))

        session_start.cleanup_stale_sdd(max_age=86400)

        self.assertTrue(other.exists(),
            "Only sdd-* files are purged; others are left alone")

    def test_oserror_on_stat_swallowed(self):
        """OSError from stat() must not propagate (per-file try/except)."""
        Path(self.tmpdir, "sdd-x").write_text("x", encoding="utf-8")
        # Patch os.stat at module level to raise
        with patch.object(session_start.os, "stat", side_effect=OSError("eio")):
            session_start.cleanup_stale_sdd(max_age=86400)  # must not raise


class TestSyncAllFiles(unittest.TestCase):
    """sync_all_files copies whitelisted templates, skips identical, tolerates errors."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.plugin_root = Path(self.tmpdir) / "plugin"
        self.project_dir = Path(self.tmpdir) / "project"
        self.plugin_root.mkdir()
        self.project_dir.mkdir()
        self.template_dir = self.plugin_root / "template"
        self.template_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_whitelisted_templates(self):
        """Create minimal content for the whitelisted template paths."""
        for rel in session_start.ALLOWED_TEMPLATE_PATHS:
            src = self.template_dir / rel
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_text(f"// content of {rel}\n", encoding="utf-8")

    def test_copies_all_whitelisted(self):
        self._make_whitelisted_templates()

        session_start.sync_all_files(self.plugin_root, self.project_dir)

        for rel in session_start.ALLOWED_TEMPLATE_PATHS:
            expected = self.project_dir / session_start.remove_template_suffix(rel)
            self.assertTrue(expected.exists(), f"Missing: {expected}")

    def test_missing_source_is_skipped(self):
        """A whitelisted path that doesn't exist in template/ is simply skipped."""
        # Create only one template file; others missing
        only = session_start.ALLOWED_TEMPLATE_PATHS[0]
        src = self.template_dir / only
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text("x", encoding="utf-8")

        session_start.sync_all_files(self.plugin_root, self.project_dir)

        copied = self.project_dir / session_start.remove_template_suffix(only)
        self.assertTrue(copied.exists())
        # Others not created
        for rel in session_start.ALLOWED_TEMPLATE_PATHS[1:]:
            missing = self.project_dir / session_start.remove_template_suffix(rel)
            self.assertFalse(missing.exists())

    def test_identical_file_not_recopied(self):
        """filecmp.cmp equal → skip copy (preserve mtime)."""
        self._make_whitelisted_templates()
        session_start.sync_all_files(self.plugin_root, self.project_dir)

        dst = self.project_dir / session_start.remove_template_suffix(
            session_start.ALLOWED_TEMPLATE_PATHS[0]
        )
        mtime_before = dst.stat().st_mtime

        time.sleep(0.01)
        session_start.sync_all_files(self.plugin_root, self.project_dir)

        self.assertEqual(mtime_before, dst.stat().st_mtime,
            "Identical file must not be re-copied")

    def test_copy_error_writes_warning(self):
        """OSError during copy writes to stderr but does not abort the loop."""
        self._make_whitelisted_templates()
        stderr_capture = io.StringIO()
        with patch.object(session_start.shutil, "copy2",
                          side_effect=OSError("disk full")), \
             patch("sys.stderr", stderr_capture):
            session_start.sync_all_files(self.plugin_root, self.project_dir)
        self.assertIn("WARNING: Failed to sync template",
                      stderr_capture.getvalue())


class TestOutputHookResponse(unittest.TestCase):
    """output_hook_response emits valid JSON — with or without context."""

    def test_empty_emits_empty_object(self):
        stdout_capture = io.StringIO()
        with patch("sys.stdout", stdout_capture):
            session_start.output_hook_response("")
        self.assertEqual(stdout_capture.getvalue().strip(), "{}")

    def test_context_wraps_in_additionalContext(self):
        stdout_capture = io.StringIO()
        with patch("sys.stdout", stdout_capture):
            session_start.output_hook_response("hello world")
        payload = json.loads(stdout_capture.getvalue())
        self.assertEqual(
            payload["hookSpecificOutput"]["hookEventName"], "SessionStart"
        )
        self.assertEqual(
            payload["hookSpecificOutput"]["additionalContext"], "hello world"
        )


class TestConsumeStdinSessionStart(unittest.TestCase):
    """consume_stdin must not crash on any stdin state."""

    def test_normal_stdin(self):
        with patch("sys.stdin", io.StringIO("{}")):
            session_start.consume_stdin()

    def test_ioerror_swallowed(self):
        fake = MagicMock()
        fake.read.side_effect = IOError("broken pipe")
        with patch("sys.stdin", fake):
            session_start.consume_stdin()

    def test_oserror_swallowed(self):
        fake = MagicMock()
        fake.read.side_effect = OSError("closed")
        with patch("sys.stdin", fake):
            session_start.consume_stdin()


if __name__ == "__main__":
    unittest.main()
