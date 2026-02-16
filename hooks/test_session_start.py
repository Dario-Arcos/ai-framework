#!/usr/bin/env python3
"""Tests for session-start.py — SessionStart hook for AI Framework plugin."""
import importlib
import io
import json
import os
import shutil
import sys
import tempfile
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


class TestReadEnforcementContent(unittest.TestCase):
    """Test read_enforcement_content() frontmatter stripping."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.plugin_root = Path(self.tmpdir)
        self.skill_dir = self.plugin_root / "skills" / "using-ai-framework"
        self.skill_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_reads_and_strips_frontmatter(self):
        skill_file = self.skill_dir / "SKILL.md"
        skill_file.write_text(
            "---\nname: test\ndescription: test skill\n---\nActual content here",
            encoding="utf-8",
        )
        result = session_start.read_enforcement_content(self.plugin_root)
        self.assertEqual(result, "Actual content here")

    def test_no_frontmatter(self):
        skill_file = self.skill_dir / "SKILL.md"
        skill_file.write_text("Plain content without frontmatter", encoding="utf-8")
        result = session_start.read_enforcement_content(self.plugin_root)
        self.assertEqual(result, "Plain content without frontmatter")

    def test_missing_file(self):
        result = session_start.read_enforcement_content(self.plugin_root / "nonexistent")
        self.assertEqual(result, "")


class TestBuildAdditionalContext(unittest.TestCase):
    """Test build_additional_context() wrapping logic."""

    def test_wraps_content(self):
        result = session_start.build_additional_context("Some enforcement rules")
        self.assertTrue(result.startswith("<EXTREMELY_IMPORTANT>"))
        self.assertTrue(result.endswith("</EXTREMELY_IMPORTANT>"))
        self.assertIn("Some enforcement rules", result)

    def test_empty_returns_empty(self):
        result = session_start.build_additional_context("   \n  ")
        self.assertEqual(result, "")


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
        # Create skill file for enforcement content
        skill_dir = self.plugin_root / "skills" / "using-ai-framework"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test\n---\nEnforcement content", encoding="utf-8"
        )

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
        self.assertIn("hookSpecificOutput", output)
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "SessionStart")

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
        # Verify enforcement content was picked up (proves plugin root was used)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("EXTREMELY_IMPORTANT", ctx)
        self.assertIn("Enforcement content", ctx)

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


if __name__ == "__main__":
    unittest.main()
