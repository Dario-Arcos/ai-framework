#!/usr/bin/env python3
"""Tests for subagent-start.py — SubagentStart hook for skill registry injection.

Skill index is derived dynamically from the plugin's skills/ directory on
every invocation. Tests verify both the integration (main() output format)
and the dynamic discovery (build_skill_index from custom directories).
"""
import importlib
import io
import json
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
subagent_start = importlib.import_module("subagent-start")


# ─────────────────────────────────────────────────────────────────
# TestMainOutput — integration with real plugin layout
# ─────────────────────────────────────────────────────────────────

class TestMainOutput(unittest.TestCase):
    """Test main() produces valid SubagentStart hook output against real skills/."""

    def _run_hook(self):
        """Run main() capturing stdout, return parsed JSON."""
        stdout_capture = io.StringIO()
        with unittest.mock.patch("sys.stdin", io.StringIO("")), \
             unittest.mock.patch("sys.stdout", stdout_capture), \
             self.assertRaises(SystemExit) as cm:
            subagent_start.main()
        self.assertEqual(cm.exception.code, 0)
        return json.loads(stdout_capture.getvalue())

    def test_valid_json_structure(self):
        output = self._run_hook()
        self.assertIn("hookSpecificOutput", output)
        self.assertEqual(
            output["hookSpecificOutput"]["hookEventName"], "SubagentStart"
        )
        self.assertIn("additionalContext", output["hookSpecificOutput"])

    def test_contains_critical_skills(self):
        output = self._run_hook()
        ctx = output["hookSpecificOutput"]["additionalContext"]
        for skill in [
            "scenario-driven-development",
            "verification-before-completion",
            "systematic-debugging",
        ]:
            self.assertIn(skill, ctx, f"Missing critical skill: {skill}")

    def test_contains_invocation_hint(self):
        """Sub-agents must know skills are invoked via Skill tool."""
        output = self._run_hook()
        ctx = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Skill tool", ctx)

    def test_contains_agent_browser_description(self):
        """agent-browser should have a usage hint."""
        output = self._run_hook()
        ctx = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("agent-browser", ctx)

    def test_no_redundancy(self):
        """Each skill name should appear at most once to minimize reasoning friction."""
        ctx = subagent_start.build_skill_index()
        for skill in ["scenario-driven-development", "systematic-debugging",
                       "deep-research", "context-engineering", "commit"]:
            count = ctx.count(skill)
            self.assertLessEqual(count, 1, f'"{skill}" appears {count} times, expected <=1')

    def test_token_budget(self):
        """Skill index should stay compact — under 1500 chars (~300 tokens)."""
        # Note: with 23 skills (vs 14 hardcoded previously), index is slightly
        # larger but still well under the budget.
        self.assertLess(len(subagent_start.build_skill_index()), 1500)

    def test_handles_empty_stdin(self):
        """Hook must not crash on empty stdin."""
        stdout_capture = io.StringIO()
        with unittest.mock.patch("sys.stdin", io.StringIO("")), \
             unittest.mock.patch("sys.stdout", stdout_capture), \
             self.assertRaises(SystemExit) as cm:
            subagent_start.main()
        self.assertEqual(cm.exception.code, 0)

    def test_handles_stdin_ioerror(self):
        """Hook must not crash when stdin raises IOError."""
        class BrokenStdin:
            def read(self):
                raise IOError("broken pipe")
        stdout_capture = io.StringIO()
        with unittest.mock.patch("sys.stdin", BrokenStdin()), \
             unittest.mock.patch("sys.stdout", stdout_capture), \
             self.assertRaises(SystemExit) as cm:
            subagent_start.main()
        self.assertEqual(cm.exception.code, 0)


# ─────────────────────────────────────────────────────────────────
# TestDynamicDiscovery — build_skill_index against synthetic skills/
# ─────────────────────────────────────────────────────────────────

class TestDynamicDiscovery(unittest.TestCase):
    """Test build_skill_index reflects filesystem state dynamically."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.skills_dir = Path(self.tmpdir) / "skills"
        self.skills_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_skill(self, name, content="# A skill\n"):
        skill_dir = self.skills_dir / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

    def test_lists_skills_from_filesystem(self):
        self._make_skill("alpha")
        self._make_skill("beta")
        self._make_skill("gamma")
        index = subagent_start.build_skill_index(self.skills_dir)
        self.assertIn("alpha", index)
        self.assertIn("beta", index)
        self.assertIn("gamma", index)

    def test_excludes_skill_with_empty_skill_md(self):
        """SKILL.md with zero size is excluded — avoids advertising broken skills."""
        self._make_skill("good")
        # Create skill dir with empty SKILL.md
        bad = self.skills_dir / "broken"
        bad.mkdir()
        (bad / "SKILL.md").write_text("", encoding="utf-8")
        index = subagent_start.build_skill_index(self.skills_dir)
        self.assertIn("good", index)
        self.assertNotIn("broken", index)

    def test_excludes_dir_without_skill_md(self):
        """Directory missing SKILL.md is not a skill."""
        self._make_skill("legit")
        # Directory but no SKILL.md
        (self.skills_dir / "not-a-skill").mkdir()
        index = subagent_start.build_skill_index(self.skills_dir)
        self.assertIn("legit", index)
        self.assertNotIn("not-a-skill", index)

    def test_returns_empty_when_no_skills(self):
        index = subagent_start.build_skill_index(self.skills_dir)
        self.assertEqual(index, "")

    def test_returns_empty_when_skills_dir_missing(self):
        """Non-existent skills dir → degrades silently (empty string)."""
        index = subagent_start.build_skill_index(Path(self.tmpdir) / "does-not-exist")
        self.assertEqual(index, "")

    def test_main_outputs_empty_dict_when_no_skills(self):
        """Hook contract: empty `{}` when no skill registry available."""
        stdout_capture = io.StringIO()
        with unittest.mock.patch("sys.stdin", io.StringIO("")), \
             unittest.mock.patch("sys.stdout", stdout_capture), \
             unittest.mock.patch.object(
                 subagent_start, "build_skill_index", return_value=""
             ), \
             self.assertRaises(SystemExit) as cm:
            subagent_start.main()
        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(json.loads(stdout_capture.getvalue()), {})

    def test_alphabetical_ordering(self):
        """Skills listed alphabetically — deterministic for caching."""
        self._make_skill("zebra")
        self._make_skill("alpha")
        self._make_skill("mike")
        index = subagent_start.build_skill_index(self.skills_dir)
        # Find positions
        pos_alpha = index.index("alpha")
        pos_mike = index.index("mike")
        pos_zebra = index.index("zebra")
        self.assertLess(pos_alpha, pos_mike)
        self.assertLess(pos_mike, pos_zebra)


# ─────────────────────────────────────────────────────────────────
# TestPluginRootResolution
# ─────────────────────────────────────────────────────────────────

class TestPluginRootResolution(unittest.TestCase):
    """Test find_skills_dir falls back robustly when env var is absent."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_uses_env_var_when_set(self):
        skills = Path(self.tmpdir) / "plugin" / "skills"
        skills.mkdir(parents=True)
        with unittest.mock.patch.dict(
            "os.environ",
            {"CLAUDE_PLUGIN_ROOT": str(Path(self.tmpdir) / "plugin")},
        ):
            result = subagent_start.find_skills_dir()
        self.assertEqual(result, skills)

    def test_falls_back_to_file_parent_when_env_invalid(self):
        """Env var pointing to non-existent dir → fallback to __file__ parent."""
        with unittest.mock.patch.dict(
            "os.environ",
            {"CLAUDE_PLUGIN_ROOT": "/nonexistent/path"},
        ):
            result = subagent_start.find_skills_dir()
        # Real plugin layout has skills/ as sibling of hooks/
        self.assertIsNotNone(result)
        self.assertTrue(result.is_dir())

    def test_returns_none_when_nothing_resolves(self):
        """Both env and __file__ fallback fail → None (caller degrades silently)."""
        # Mock __file__ resolution to point somewhere with no skills/
        fake_hook = Path(self.tmpdir) / "hooks" / "subagent-start.py"
        fake_hook.parent.mkdir(parents=True)
        fake_hook.write_text("", encoding="utf-8")
        with unittest.mock.patch.dict("os.environ", {}, clear=False), \
             unittest.mock.patch.object(
                 subagent_start, "__file__", str(fake_hook)
             ):
            # Remove env var if present
            if "CLAUDE_PLUGIN_ROOT" in __import__("os").environ:
                del __import__("os").environ["CLAUDE_PLUGIN_ROOT"]
            result = subagent_start.find_skills_dir()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
