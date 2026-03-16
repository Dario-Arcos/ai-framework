#!/usr/bin/env python3
"""Tests for statusline — Python renderer in statusline.py."""
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import statusline.py directly from template
_py_path = (
    Path(__file__).resolve().parent.parent
    / "template" / ".claude.template" / "statusline.py"
)
_spec = importlib.util.spec_from_file_location("statusline", _py_path)
statusline = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(statusline)


class TestFormatDuration(unittest.TestCase):
    """Test format_duration() millisecond conversion."""

    def test_zero_ms(self):
        self.assertEqual(statusline.format_duration(0), "0m")

    def test_negative_treated_as_zero(self):
        self.assertEqual(statusline.format_duration(-1), "0m")

    def test_under_one_minute(self):
        self.assertEqual(statusline.format_duration(30000), "<1m")

    def test_exactly_one_minute(self):
        self.assertEqual(statusline.format_duration(60000), "1m")

    def test_multiple_minutes(self):
        self.assertEqual(statusline.format_duration(300000), "5m")

    def test_rounds_down(self):
        self.assertEqual(statusline.format_duration(90000), "1m")


class TestBuildContextBar(unittest.TestCase):
    """Test build_context_bar() bar rendering and color selection."""

    def test_zero_percent(self):
        bar, color = statusline.build_context_bar(0)
        self.assertEqual(bar, "\u2591" * 10)
        self.assertIn("32m", color)  # green

    def test_100_percent(self):
        bar, color = statusline.build_context_bar(100)
        self.assertEqual(bar, "\u2588" * 10)
        self.assertIn("31m", color)  # red

    def test_50_percent_yellow(self):
        bar, color = statusline.build_context_bar(50)
        self.assertEqual(bar, "\u2588" * 5 + "\u2591" * 5)
        self.assertIn("33m", color)  # yellow

    def test_49_percent_green(self):
        _, color = statusline.build_context_bar(49)
        self.assertIn("32m", color)

    def test_80_percent_red(self):
        _, color = statusline.build_context_bar(80)
        self.assertIn("31m", color)

    def test_79_percent_yellow(self):
        _, color = statusline.build_context_bar(79)
        self.assertIn("33m", color)

    def test_custom_bar_width(self):
        bar, _ = statusline.build_context_bar(50, bar_width=4)
        self.assertEqual(len(bar), 4)
        self.assertEqual(bar, "\u2588\u2588\u2591\u2591")


class TestGetGitInfo(unittest.TestCase):
    """Test get_git_info() git detection."""

    def test_not_a_git_repo(self):
        with patch.object(statusline.subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            branch, worktree = statusline.get_git_info()
        self.assertEqual(branch, "")
        self.assertEqual(worktree, "")

    def test_git_repo_no_worktree(self):
        def side_effect(cmd, **kwargs):
            result = MagicMock()
            if "rev-parse" in cmd:
                result.returncode = 0
                result.stdout = "/home/user/project\n"
            elif "branch" in cmd:
                result.returncode = 0
                result.stdout = "main\n"
            elif "worktree" in cmd:
                result.returncode = 0
                result.stdout = "/home/user/project  abc1234 [main]\n"
            return result

        with patch.object(statusline.subprocess, "run", side_effect=side_effect):
            branch, worktree = statusline.get_git_info()
        self.assertEqual(branch, "main")
        self.assertEqual(worktree, "")

    def test_git_repo_with_worktree(self):
        def side_effect(cmd, **kwargs):
            result = MagicMock()
            if "rev-parse" in cmd:
                result.returncode = 0
                result.stdout = "/home/user/project/.claude/worktrees/feature-wt\n"
            elif "branch" in cmd:
                result.returncode = 0
                result.stdout = "feature\n"
            elif "worktree" in cmd:
                result.returncode = 0
                result.stdout = "/home/user/project  abc1234 [main]\n/home/user/project/.claude/worktrees/feature-wt  def5678 [feature]\n"
            return result

        with patch.object(statusline.subprocess, "run", side_effect=side_effect):
            branch, worktree = statusline.get_git_info()
        self.assertEqual(branch, "feature")
        self.assertEqual(worktree, "feature-wt")

    def test_subprocess_oserror(self):
        with patch.object(statusline.subprocess, "run", side_effect=OSError("git not found")):
            branch, worktree = statusline.get_git_info()
        self.assertEqual(branch, "")
        self.assertEqual(worktree, "")


class TestMainOutput(unittest.TestCase):
    """Test main() end-to-end JSON parsing and ANSI output."""

    def _run_main(self, input_data):
        """Helper to run main() with given JSON input and capture stdout."""
        json_str = json.dumps(input_data) if isinstance(input_data, dict) else input_data
        stdout_capture = io.StringIO()
        with patch.object(statusline, "sys") as mock_sys:
            mock_sys.stdin.read.return_value = json_str
            mock_sys.stdout = stdout_capture
            with patch.object(statusline, "get_git_info", return_value=("main", "")):
                statusline.main()
        return stdout_capture.getvalue()

    def test_full_json(self):
        data = {
            "model": {"display_name": "Opus"},
            "version": "1.2.3",
            "cost": {
                "total_duration_ms": 120000,
                "total_lines_added": 42,
                "total_lines_removed": 7,
            },
            "context_window": {"used_percentage": 35.6},
        }
        output = self._run_main(data)
        self.assertIn("Opus", output)
        self.assertIn("v1.2.3", output)
        self.assertIn("~35%", output)
        self.assertIn("2m", output)
        self.assertIn("42/7", output)
        self.assertTrue(output.endswith("\n"))

    def test_empty_json_defaults(self):
        output = self._run_main({})
        self.assertIn("Claude", output)
        self.assertIn("v?", output)
        self.assertIn("~0%", output)
        self.assertIn("0m", output)
        self.assertIn("0/0", output)

    def test_invalid_json(self):
        output = self._run_main("not valid json")
        self.assertIn("Claude", output)
        self.assertIn("v?", output)

    def test_used_percentage_floor(self):
        data = {"context_window": {"used_percentage": 55.9}}
        output = self._run_main(data)
        self.assertIn("~55%", output)

    def test_fallback_percentage_from_tokens(self):
        data = {
            "context_window": {
                "context_window_size": 200000,
                "current_usage": {
                    "input_tokens": 100000,
                    "cache_creation_input_tokens": 20000,
                    "cache_read_input_tokens": 10000,
                },
            },
        }
        output = self._run_main(data)
        self.assertIn("~65%", output)

    def test_percent_capped_at_100(self):
        data = {"context_window": {"used_percentage": 150}}
        output = self._run_main(data)
        self.assertIn("~100%", output)

    def test_worktree_shown(self):
        data = {"model": {"display_name": "Sonnet"}}
        stdout_capture = io.StringIO()
        with patch.object(statusline, "sys") as mock_sys:
            mock_sys.stdin.read.return_value = json.dumps(data)
            mock_sys.stdout = stdout_capture
            with patch.object(statusline, "get_git_info", return_value=("feat", "my-wt")):
                statusline.main()
        output = stdout_capture.getvalue()
        self.assertIn("feat", output)
        self.assertIn("my-wt", output)

    def test_no_branch_no_separator(self):
        stdout_capture = io.StringIO()
        with patch.object(statusline, "sys") as mock_sys:
            mock_sys.stdin.read.return_value = json.dumps({})
            mock_sys.stdout = stdout_capture
            with patch.object(statusline, "get_git_info", return_value=("", "")):
                statusline.main()
        output = stdout_capture.getvalue()
        self.assertNotIn("\u2387", output)

    def test_duration_under_one_minute(self):
        data = {"cost": {"total_duration_ms": 30000}}
        output = self._run_main(data)
        self.assertIn("<1m", output)


class TestCrossPlatformIntegration(unittest.TestCase):
    """Test cross-platform statusline files are in sync."""

    def test_template_and_plugin_py_are_identical(self):
        """Both .py copies must be in sync."""
        plugin_py = (
            Path(__file__).resolve().parent.parent / ".claude" / "statusline.py"
        )
        self.assertEqual(
            _py_path.read_text(),
            plugin_py.read_text(),
            "template and .claude/ statusline.py are out of sync",
        )

    def test_template_and_plugin_cmd_are_identical(self):
        """Both .cmd copies must be in sync."""
        template_cmd = _py_path.parent / "statusline.cmd"
        plugin_cmd = (
            Path(__file__).resolve().parent.parent / ".claude" / "statusline.cmd"
        )
        self.assertEqual(
            template_cmd.read_text(),
            plugin_cmd.read_text(),
            "template and .claude/ statusline.cmd are out of sync",
        )

    def test_statusline_py_compiles(self):
        """statusline.py must compile without errors."""
        compile(_py_path.read_text(), "statusline.py", "exec")

    def test_no_stale_sh_in_template(self):
        """statusline.sh must NOT exist (replaced by .cmd + .py)."""
        sh_path = _py_path.parent / "statusline.sh"
        self.assertFalse(
            sh_path.exists(),
            f"Stale statusline.sh found at {sh_path} — replaced by .cmd + .py",
        )


if __name__ == "__main__":
    unittest.main()
