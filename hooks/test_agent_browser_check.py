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


class TestCooldown(unittest.TestCase):
    """Test is_cooldown_active() for first-install retry prevention."""

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
        self.assertTrue(agent_browser_check.is_cooldown_active())

    def test_cooldown_expired(self):
        self.cooldown_file.touch()
        expired_time = time.time() - 7200  # 2 hours ago
        os.utime(self.cooldown_file, (expired_time, expired_time))
        self.assertFalse(agent_browser_check.is_cooldown_active())


class TestUpdateRanRecently(unittest.TestCase):
    """Test _update_ran_recently() — anti-fork-storm dedup."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_log = agent_browser_check.UPDATE_LOG
        self.log_file = Path(self.tmpdir) / "update.log"
        agent_browser_check.UPDATE_LOG = self.log_file

    def tearDown(self):
        agent_browser_check.UPDATE_LOG = self._orig_log
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_log_file(self):
        self.assertFalse(agent_browser_check._update_ran_recently())

    def test_recent_log(self):
        self.log_file.touch()
        self.assertTrue(agent_browser_check._update_ran_recently())

    def test_stale_log(self):
        self.log_file.touch()
        stale_time = time.time() - 600  # 10 min ago, beyond 5min dedup
        os.utime(self.log_file, (stale_time, stale_time))
        self.assertFalse(agent_browser_check._update_ran_recently())


class TestBuildSyncCmd(unittest.TestCase):
    """Test _build_sync_cmd() generates correct shell command."""

    def test_contains_all_skills(self):
        cmd = agent_browser_check._build_sync_cmd()
        for skill in agent_browser_check.SKILLS_TO_SYNC:
            self.assertIn(skill, cmd)

    def test_contains_mkdir(self):
        cmd = agent_browser_check._build_sync_cmd()
        self.assertIn("mkdir -p", cmd)

    def test_contains_npm_root(self):
        cmd = agent_browser_check._build_sync_cmd()
        self.assertIn("npm root -g", cmd)


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


class TestUpdateAndSync(unittest.TestCase):
    """Test update_and_sync() dispatches correct command."""

    @patch("agent_browser_check.run_background", return_value=(True, "/tmp/update.log"))
    def test_uses_update_cmd(self, mock_run):
        ok, _ = agent_browser_check.update_and_sync()
        self.assertTrue(ok)
        cmd = mock_run.call_args[0][0]
        self.assertIn("npm install -g agent-browser@latest", cmd)
        for skill in agent_browser_check.SKILLS_TO_SYNC:
            self.assertIn(skill, cmd)

    @patch("agent_browser_check.run_background", return_value=(True, "/tmp/update.log"))
    def test_stderr_not_silenced(self, mock_run):
        """Regression: old hook used 2>/dev/null, hiding errors."""
        cmd = mock_run.call_args[0][0] if mock_run.called else agent_browser_check.UPDATE_CMD
        agent_browser_check.update_and_sync()
        cmd = mock_run.call_args[0][0]
        self.assertNotIn("2>/dev/null", cmd)
        self.assertIn("2>&1", cmd)


class TestInstallAndSync(unittest.TestCase):
    """Test install_and_sync() dispatches correct command and sets cooldown."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_cooldown = agent_browser_check.COOLDOWN_FILE
        agent_browser_check.COOLDOWN_FILE = Path(self.tmpdir) / "cooldown-ts"

    def tearDown(self):
        agent_browser_check.COOLDOWN_FILE = self._orig_cooldown
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch("agent_browser_check.run_background", return_value=(True, "/tmp/install.log"))
    def test_touches_cooldown(self, mock_run):
        agent_browser_check.install_and_sync()
        self.assertTrue(agent_browser_check.COOLDOWN_FILE.exists())

    @patch("agent_browser_check.run_background", return_value=(True, "/tmp/install.log"))
    def test_uses_install_cmd(self, mock_run):
        agent_browser_check.install_and_sync()
        cmd = mock_run.call_args[0][0]
        self.assertIn("agent-browser install", cmd)
        for skill in agent_browser_check.SKILLS_TO_SYNC:
            self.assertIn(skill, cmd)

    @patch("agent_browser_check.run_background", return_value=(True, "/tmp/install.log"))
    def test_skill_sync_decoupled_from_install(self, mock_run):
        """Skill sync runs even if npm install fails (uses ; not &&)."""
        agent_browser_check.install_and_sync()
        cmd = mock_run.call_args[0][0]
        # After "agent-browser install 2>&1", skill sync uses ";" not "&&"
        install_end = cmd.index("agent-browser install 2>&1") + len("agent-browser install 2>&1")
        after_install = cmd[install_end:]
        self.assertTrue(after_install.startswith(";"))


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
        self.assertFalse(pid_file.exists())
        self.assertFalse(sock_file.exists())

    @patch("agent_browser_check.subprocess.run")
    @patch("os.kill")
    def test_pkill_fallback_orphan_sockets(self, mock_kill, mock_run):
        base = Path(self.tmpdir)
        sock_file = base / "orphan.sock"
        sock_file.touch()

        agent_browser_check.cleanup_orphan_daemons()

        mock_kill.assert_not_called()
        # Phase 2 (daemon pkill) + Phase 3 (chrome-headless-shell) = 2 calls
        self.assertEqual(mock_run.call_count, 2)
        self.assertIn("agent-browser", mock_run.call_args_list[0][0][0][-1])
        self.assertIn("chrome-headless-shell", mock_run.call_args_list[1][0][0][-1])

    @patch("agent_browser_check.subprocess.run")
    @patch("os.kill")
    def test_chrome_headless_shell_cleanup(self, mock_kill, mock_run):
        """Phase 3: only orphan chrome (PPID=1) killed, not active ones."""
        agent_browser_check.cleanup_orphan_daemons()

        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], "pkill")
        self.assertIn("-P", cmd)
        self.assertIn("1", cmd)
        self.assertIn("chrome-headless-shell", cmd[-1])


class TestMain(unittest.TestCase):
    """Test main() — two paths: update (installed) or first-install (missing)."""

    def _run_main(self, patches):
        """Helper: apply patches, run main(), return parsed JSON output dict."""
        defaults = {
            "agent_browser_check.consume_stdin": None,
            "agent_browser_check.cleanup_orphan_daemons": None,
            "agent_browser_check.is_installed": False,
            "agent_browser_check.is_cooldown_active": False,
            "agent_browser_check._update_ran_recently": False,
            "agent_browser_check.update_and_sync": (True, "/tmp/update.log"),
            "agent_browser_check.install_and_sync": (True, "/tmp/install.log"),
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
            return json.loads(captured.getvalue())
        finally:
            for p in active_patches:
                p.stop()

    def _assert_silent(self, output):
        """Assert hook output is silent (no additionalContext to Claude)."""
        self.assertNotIn("hookSpecificOutput", output)

    # --- Installed path: unconditional update ---

    def test_installed_update_fires(self):
        mock_update = MagicMock(return_value=(True, "/tmp/update.log"))
        output = self._run_main({
            "agent_browser_check.is_installed": True,
            "agent_browser_check._update_ran_recently": False,
            "agent_browser_check.update_and_sync": mock_update,
        })
        self._assert_silent(output)
        mock_update.assert_called_once()

    def test_installed_dedup_skips_fork(self):
        mock_update = MagicMock(return_value=(True, "/tmp/update.log"))
        output = self._run_main({
            "agent_browser_check.is_installed": True,
            "agent_browser_check._update_ran_recently": True,
            "agent_browser_check.update_and_sync": mock_update,
        })
        self._assert_silent(output)
        mock_update.assert_not_called()

    def test_installed_always_silent(self):
        """Update path never emits context to Claude — nothing actionable."""
        output = self._run_main({
            "agent_browser_check.is_installed": True,
            "agent_browser_check._update_ran_recently": False,
        })
        self._assert_silent(output)

    # --- Not installed path: first-install ---

    def test_not_installed_installs_silent(self):
        mock_install = MagicMock(return_value=(True, "/tmp/install.log"))
        output = self._run_main({
            "agent_browser_check.is_installed": False,
            "agent_browser_check.is_cooldown_active": False,
            "agent_browser_check.install_and_sync": mock_install,
        })
        self._assert_silent(output)
        mock_install.assert_called_once()

    def test_not_installed_cooldown_skips(self):
        mock_install = MagicMock(return_value=(True, "/tmp/install.log"))
        output = self._run_main({
            "agent_browser_check.is_installed": False,
            "agent_browser_check.is_cooldown_active": True,
            "agent_browser_check.install_and_sync": mock_install,
        })
        self._assert_silent(output)
        mock_install.assert_not_called()

    @patch.dict(os.environ, {"AI_FRAMEWORK_SKIP_BROWSER_INSTALL": "1"})
    def test_not_installed_skip_env_silent(self):
        mock_install = MagicMock(return_value=(True, "/tmp/install.log"))
        output = self._run_main({
            "agent_browser_check.is_installed": False,
            "agent_browser_check.install_and_sync": mock_install,
        })
        self._assert_silent(output)
        mock_install.assert_not_called()

    def test_install_fails_emits_context(self):
        mock_install = MagicMock(return_value=(False, None))
        output = self._run_main({
            "agent_browser_check.is_installed": False,
            "agent_browser_check.is_cooldown_active": False,
            "agent_browser_check.install_and_sync": mock_install,
        })
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("install failed", context)
        self.assertIn("npm install -g agent-browser", context)
        mock_install.assert_called_once()


class TestConsumeStdin(unittest.TestCase):
    """Test consume_stdin() — required by hook protocol, must not crash."""

    def test_consumes_stdin_normally(self):
        """Normal stdin is consumed without raising."""
        with patch("sys.stdin", io.StringIO("hook input")):
            agent_browser_check.consume_stdin()

    def test_stdin_none_no_crash(self):
        """sys.stdin=None must be handled gracefully."""
        with patch("sys.stdin", None):
            agent_browser_check.consume_stdin()

    def test_stdin_oserror_swallowed(self):
        """OSError reading stdin must not propagate."""
        fake_stdin = MagicMock()
        fake_stdin.read.side_effect = OSError("closed")
        with patch("sys.stdin", fake_stdin):
            agent_browser_check.consume_stdin()

    def test_stdin_valueerror_swallowed(self):
        """ValueError (closed file) must not propagate."""
        fake_stdin = MagicMock()
        fake_stdin.read.side_effect = ValueError("I/O on closed file")
        with patch("sys.stdin", fake_stdin):
            agent_browser_check.consume_stdin()


class TestCleanupOrphanEdgeCases(unittest.TestCase):
    """Edge cases in cleanup_orphan_daemons() — malformed state files."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_dir = agent_browser_check.AGENT_BROWSER_DIR
        agent_browser_check.AGENT_BROWSER_DIR = Path(self.tmpdir)

    def tearDown(self):
        agent_browser_check.AGENT_BROWSER_DIR = self._orig_dir
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch("os.kill")
    def test_non_numeric_pid_content(self, mock_kill):
        """PID file with non-numeric content → ValueError swallowed, files cleaned."""
        pid_file = Path(self.tmpdir) / "corrupt.pid"
        pid_file.write_text("not-a-number\n", encoding="utf-8")
        sock_file = Path(self.tmpdir) / "corrupt.sock"
        sock_file.touch()

        agent_browser_check.cleanup_orphan_daemons()

        mock_kill.assert_not_called()
        self.assertFalse(pid_file.exists())
        self.assertFalse(sock_file.exists())

    @patch("os.kill", side_effect=PermissionError("op not permitted"))
    def test_permission_error_on_kill(self, mock_kill):
        """PermissionError on os.kill → swallowed, state files still cleaned."""
        pid_file = Path(self.tmpdir) / "root.pid"
        pid_file.write_text("1", encoding="utf-8")
        sock_file = Path(self.tmpdir) / "root.sock"
        sock_file.touch()

        agent_browser_check.cleanup_orphan_daemons()

        self.assertFalse(pid_file.exists())
        self.assertFalse(sock_file.exists())

    @patch("agent_browser_check.subprocess.run",
           side_effect=__import__("subprocess").TimeoutExpired("pkill", 5))
    @patch("os.kill")
    def test_pkill_timeout_swallowed(self, mock_kill, mock_run):
        """subprocess.TimeoutExpired on pkill must not propagate."""
        sock_file = Path(self.tmpdir) / "orphan.sock"
        sock_file.touch()
        agent_browser_check.cleanup_orphan_daemons()  # must not raise

    @patch("agent_browser_check.subprocess.run", side_effect=OSError("no pkill"))
    @patch("os.kill")
    def test_pkill_oserror_swallowed(self, mock_kill, mock_run):
        """OSError on pkill (not found, denied) must not propagate."""
        sock_file = Path(self.tmpdir) / "orphan.sock"
        sock_file.touch()
        agent_browser_check.cleanup_orphan_daemons()  # must not raise


class TestStatOSErrors(unittest.TestCase):
    """Cooldown/dedup files: OSError on stat must not crash."""

    def test_cooldown_stat_oserror(self):
        """OSError from COOLDOWN_FILE.stat() → returns False (safe default)."""
        fake_path = MagicMock()
        fake_path.exists.return_value = True
        fake_path.stat.side_effect = OSError("eacces")
        orig = agent_browser_check.COOLDOWN_FILE
        try:
            agent_browser_check.COOLDOWN_FILE = fake_path
            self.assertFalse(agent_browser_check.is_cooldown_active())
        finally:
            agent_browser_check.COOLDOWN_FILE = orig

    def test_update_log_stat_oserror(self):
        """OSError from UPDATE_LOG.stat() → returns False (safe default)."""
        fake_path = MagicMock()
        fake_path.exists.return_value = True
        fake_path.stat.side_effect = OSError("eacces")
        orig = agent_browser_check.UPDATE_LOG
        try:
            agent_browser_check.UPDATE_LOG = fake_path
            self.assertFalse(agent_browser_check._update_ran_recently())
        finally:
            agent_browser_check.UPDATE_LOG = orig


class TestInstallCooldownOSError(unittest.TestCase):
    """install_and_sync: OSError touching cooldown file must not block install."""

    @patch("agent_browser_check.run_background",
           return_value=(True, "/tmp/install.log"))
    def test_touch_oserror_still_runs_install(self, mock_run):
        fake_path = MagicMock()
        fake_path.touch.side_effect = OSError("read-only fs")
        orig = agent_browser_check.COOLDOWN_FILE
        try:
            agent_browser_check.COOLDOWN_FILE = fake_path
            ok, _ = agent_browser_check.install_and_sync()
            self.assertTrue(ok)
            mock_run.assert_called_once()
        finally:
            agent_browser_check.COOLDOWN_FILE = orig


if __name__ == "__main__":
    unittest.main()
