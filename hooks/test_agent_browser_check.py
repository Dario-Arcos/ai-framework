#!/usr/bin/env python3
"""Tests for agent-browser-check.py — SessionStart hook."""
import importlib
import io
import json
import os
import shutil
import signal
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
agent_browser_check = importlib.import_module("agent-browser-check")
# Register under underscore name so patch("agent_browser_check.x") resolves
sys.modules["agent_browser_check"] = agent_browser_check


class TestIsInstalled(unittest.TestCase):
    """Test is_installed() via shutil.which mock."""

    @patch.object(shutil, "which", return_value="/usr/local/bin/agent-browser")
    def test_found_in_path(self, mock_which):
        self.assertTrue(agent_browser_check.is_installed())
        mock_which.assert_called_once_with("agent-browser")

    @patch.object(shutil, "which", return_value=None)
    def test_not_in_path(self, mock_which):
        self.assertFalse(agent_browser_check.is_installed())
        mock_which.assert_called_once_with("agent-browser")


class TestIsSkillPresent(unittest.TestCase):
    """Test is_skill_present() with real filesystem fixtures."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_skill_file = agent_browser_check.SKILL_FILE
        self.skill_file = Path(self.tmpdir) / "SKILL.md"
        agent_browser_check.SKILL_FILE = self.skill_file

    def tearDown(self):
        agent_browser_check.SKILL_FILE = self._orig_skill_file
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_skill_exists_and_nonempty(self):
        self.skill_file.write_text("# Agent Browser Skill", encoding="utf-8")
        self.assertTrue(agent_browser_check.is_skill_present())

    def test_skill_missing(self):
        self.assertFalse(agent_browser_check.is_skill_present())

    def test_skill_empty(self):
        self.skill_file.write_text("", encoding="utf-8")
        self.assertFalse(agent_browser_check.is_skill_present())


class TestCooldown(unittest.TestCase):
    """Test is_cooldown_active() with mocked COOLDOWN_FILE."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_cooldown = agent_browser_check.COOLDOWN_FILE
        self.cooldown_file = Path(self.tmpdir) / "cooldown-ts"
        agent_browser_check.COOLDOWN_FILE = self.cooldown_file

    def tearDown(self):
        agent_browser_check.COOLDOWN_FILE = self._orig_cooldown
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_cooldown_file(self):
        self.assertFalse(agent_browser_check.is_cooldown_active())

    def test_cooldown_active(self):
        self.cooldown_file.touch()
        # mtime is now, which is < 3600s ago
        self.assertTrue(agent_browser_check.is_cooldown_active())

    def test_cooldown_expired(self):
        self.cooldown_file.touch()
        expired_time = time.time() - 7200  # 2 hours ago
        os.utime(self.cooldown_file, (expired_time, expired_time))
        self.assertFalse(agent_browser_check.is_cooldown_active())


class TestRunBackground(unittest.TestCase):
    """Test run_background() Popen behavior."""

    def test_launches_popen(self):
        with patch.object(agent_browser_check.subprocess, "Popen", return_value=MagicMock()) as mock_popen:
            ok, log_path = agent_browser_check.run_background("echo hello", "test.log")
            self.assertTrue(ok)
            self.assertIsNotNone(log_path)
            self.assertTrue(log_path.endswith("test.log"))
            mock_popen.assert_called_once()

    def test_oserror(self):
        with patch.object(agent_browser_check.subprocess, "Popen", side_effect=OSError("fail")):
            ok, log_path = agent_browser_check.run_background("echo hello", "test.log")
            self.assertFalse(ok)
            self.assertIsNone(log_path)


class TestCleanupOrphanDaemons(unittest.TestCase):
    """Test cleanup_orphan_daemons() with real filesystem temp dir."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_dir = agent_browser_check.AGENT_BROWSER_DIR
        agent_browser_check.AGENT_BROWSER_DIR = Path(self.tmpdir)

    def tearDown(self):
        agent_browser_check.AGENT_BROWSER_DIR = self._orig_dir
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_dir_noop(self):
        agent_browser_check.AGENT_BROWSER_DIR = Path(self.tmpdir) / "nonexistent"
        # Should return without error
        agent_browser_check.cleanup_orphan_daemons()

    @patch("os.kill")
    def test_kills_pid_removes_files(self, mock_kill):
        base = Path(self.tmpdir)
        pid_file = base / "session1.pid"
        sock_file = base / "session1.sock"
        port_file = base / "session1.port"
        stream_file = base / "session1.stream"
        pid_file.write_text("12345", encoding="utf-8")
        sock_file.touch()
        port_file.touch()
        stream_file.touch()

        agent_browser_check.cleanup_orphan_daemons()

        mock_kill.assert_called_once_with(12345, signal.SIGTERM)
        self.assertFalse(pid_file.exists())
        self.assertFalse(sock_file.exists())
        self.assertFalse(port_file.exists())
        self.assertFalse(stream_file.exists())

    @patch("os.kill", side_effect=ProcessLookupError("No such process"))
    def test_stale_pid_file(self, mock_kill):
        base = Path(self.tmpdir)
        pid_file = base / "session2.pid"
        sock_file = base / "session2.sock"
        pid_file.write_text("99999", encoding="utf-8")
        sock_file.touch()

        agent_browser_check.cleanup_orphan_daemons()

        mock_kill.assert_called_once_with(99999, signal.SIGTERM)
        # Files should still be cleaned up despite ProcessLookupError
        self.assertFalse(pid_file.exists())
        self.assertFalse(sock_file.exists())

    @patch("agent_browser_check.subprocess.run")
    @patch("os.kill")
    def test_pkill_fallback_orphan_sockets(self, mock_kill, mock_run):
        base = Path(self.tmpdir)
        # Socket without corresponding PID file = orphan
        sock_file = base / "orphan.sock"
        sock_file.touch()

        agent_browser_check.cleanup_orphan_daemons()

        # No PID files, so os.kill should not be called
        mock_kill.assert_not_called()
        # pkill fallback should fire because orphan .sock remains
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        self.assertEqual(call_args[0][0][0], "pkill")


class TestMain(unittest.TestCase):
    """Test main() with all dependencies mocked."""

    def _run_main(self, patches):
        """Helper: apply patches, run main(), return parsed JSON output."""
        defaults = {
            "agent_browser_check.consume_stdin": None,
            "agent_browser_check.cleanup_orphan_daemons": None,
            "agent_browser_check.is_installed": False,
            "agent_browser_check.is_skill_present": False,
            "agent_browser_check.is_cooldown_active": False,
            "agent_browser_check.is_update_due": False,
            "agent_browser_check.sync_skill_background": (True, "/tmp/sync.log"),
            "agent_browser_check.install_background": (True, "/tmp/install.log"),
            "agent_browser_check.update_background": (True, "/tmp/update.log"),
        }
        defaults.update(patches)

        active_patches = []
        for target, value in defaults.items():
            if value is None:
                p = patch(target)
            elif isinstance(value, MagicMock):
                p = patch(target, new=value)
            else:
                p = patch(target, return_value=value)
            active_patches.append(p)
            p.start()

        try:
            captured = io.StringIO()
            with patch("sys.stdout", captured):
                agent_browser_check.main()
            output = json.loads(captured.getvalue())
            return output["hookSpecificOutput"]["additionalContext"]
        finally:
            for p in active_patches:
                p.stop()

    def test_installed_skill_present_ready(self):
        context = self._run_main({
            "agent_browser_check.is_installed": True,
            "agent_browser_check.is_skill_present": True,
            "agent_browser_check.is_update_due": False,
        })
        self.assertEqual(context, "agent-browser: ready")

    def test_installed_skill_present_update_due(self):
        mock_update = MagicMock(return_value=(True, "/tmp/update.log"))
        context = self._run_main({
            "agent_browser_check.is_installed": True,
            "agent_browser_check.is_skill_present": True,
            "agent_browser_check.is_update_due": True,
            "agent_browser_check.update_background": mock_update,
        })
        self.assertEqual(context, "agent-browser: ready")
        mock_update.assert_called_once()

    def test_installed_no_skill_syncs(self):
        mock_sync = MagicMock(return_value=(True, "/tmp/sync.log"))
        context = self._run_main({
            "agent_browser_check.is_installed": True,
            "agent_browser_check.is_skill_present": False,
            "agent_browser_check.is_cooldown_active": False,
            "agent_browser_check.sync_skill_background": mock_sync,
        })
        self.assertEqual(context, "agent-browser: syncing skill")
        mock_sync.assert_called_once()

    def test_installed_no_skill_cooldown(self):
        mock_sync = MagicMock(return_value=(True, "/tmp/sync.log"))
        context = self._run_main({
            "agent_browser_check.is_installed": True,
            "agent_browser_check.is_skill_present": False,
            "agent_browser_check.is_cooldown_active": True,
            "agent_browser_check.sync_skill_background": mock_sync,
        })
        self.assertEqual(context, "agent-browser: syncing skill")
        # Sync should NOT be called because cooldown is active
        mock_sync.assert_not_called()

    def test_not_installed_installs(self):
        mock_install = MagicMock(return_value=(True, "/tmp/install.log"))
        context = self._run_main({
            "agent_browser_check.is_installed": False,
            "agent_browser_check.is_cooldown_active": False,
            "agent_browser_check.install_background": mock_install,
        })
        self.assertEqual(context, "agent-browser: installing")
        mock_install.assert_called_once()

    def test_not_installed_cooldown(self):
        mock_install = MagicMock(return_value=(True, "/tmp/install.log"))
        context = self._run_main({
            "agent_browser_check.is_installed": False,
            "agent_browser_check.is_cooldown_active": True,
            "agent_browser_check.install_background": mock_install,
        })
        self.assertEqual(context, "agent-browser: installing")
        # Install should NOT be called because cooldown is active
        mock_install.assert_not_called()

    @patch.dict(os.environ, {"AI_FRAMEWORK_SKIP_BROWSER_INSTALL": "1"})
    def test_not_installed_skip_env(self):
        context = self._run_main({
            "agent_browser_check.is_installed": False,
        })
        self.assertEqual(context, "agent-browser: skipped")

    def test_install_fails(self):
        mock_install = MagicMock(return_value=(False, None))
        context = self._run_main({
            "agent_browser_check.is_installed": False,
            "agent_browser_check.is_cooldown_active": False,
            "agent_browser_check.install_background": mock_install,
        })
        self.assertEqual(context, "agent-browser: install failed")
        mock_install.assert_called_once()


if __name__ == "__main__":
    unittest.main()
