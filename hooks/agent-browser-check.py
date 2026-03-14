#!/usr/bin/env python3
"""SessionStart hook — keeps agent-browser CLI and skills current.

Two paths:
- CLI installed → unconditional background update + skill sync (5min dedup)
- CLI missing   → background first-install with 1h retry cooldown

Also cleans up orphan daemons (browser, chrome) from previous sessions.

Performance:
- Dedup path (95% of sessions): 2 stat calls, ~0.5ms, zero subprocesses
- Update path (every ~5min): stat calls + fork, ~5ms, work runs in background
- Daemon cleanup: ~0.1ms normal; ~19ms only if orphan sockets found
"""
import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

AGENT_BROWSER_DIR = Path.home() / ".agent-browser"
TMPDIR = Path(tempfile.gettempdir())

CLAUDE_HOME = Path(
    os.environ.get("CLAUDE_CONFIG_DIR", "").strip()
    or Path.home() / ".claude"
)
SKILLS_DEST = CLAUDE_HOME / "skills"
SKILLS_TO_SYNC = ("agent-browser", "dogfood", "electron", "vercel-sandbox")

# First-install retry cooldown (1h) — prevents storms when npm registry is down
COOLDOWN_FILE = TMPDIR / "agent-browser-install-ts"
INSTALL_COOLDOWN_SECS = 3600

# Update dedup — log file mtime prevents redundant forks, NOT update skips.
# If the background process fails, the log mtime still resets the 5min window,
# so the next session after 5min retries automatically.
UPDATE_LOG = TMPDIR / "agent-browser-update.log"
UPDATE_DEDUP_SECS = 300

SESSION_EXTS = (".pid", ".sock", ".port", ".stream")


def _build_sync_cmd():
    """Shell command to copy skills from npm package to ~/.claude/skills/."""
    dest = str(SKILLS_DEST)
    skills = " ".join(SKILLS_TO_SYNC)
    return (
        f'mkdir -p "{dest}";'
        f' SRC="$(npm root -g)/agent-browser/skills";'
        f' for s in {skills}; do'
        f'  [ -d "$SRC/$s" ] && rm -rf "{dest}/$s" && cp -r "$SRC/$s" "{dest}/$s";'
        f" done"
    )


SYNC_CMD = _build_sync_cmd()
UPDATE_CMD = f"npm install -g agent-browser@latest 2>&1; {SYNC_CMD}"
INSTALL_CMD = f"npm install -g agent-browser@latest 2>&1 && agent-browser install 2>&1; {SYNC_CMD}"


def is_installed():
    """Check if agent-browser CLI is in PATH."""
    return shutil.which("agent-browser") is not None


def is_cooldown_active():
    """Prevent first-install retry storms: skip if last attempt was < 1h ago."""
    try:
        if COOLDOWN_FILE.exists():
            return (time.time() - COOLDOWN_FILE.stat().st_mtime) < INSTALL_COOLDOWN_SECS
    except OSError:
        pass
    return False


def _update_ran_recently():
    """Anti-fork-storm check. NOT an update skip mechanism.

    Returns True if the update log was written in the last 5 minutes.
    The log file is created by run_background() at fork time, so its mtime
    naturally tracks when the last update was launched.
    """
    try:
        if UPDATE_LOG.exists():
            return (time.time() - UPDATE_LOG.stat().st_mtime) < UPDATE_DEDUP_SECS
    except OSError:
        pass
    return False


def run_background(cmd, log_name):
    """Run a shell command in background. Returns (started, log_path)."""
    try:
        log_file = TMPDIR / log_name
        with open(log_file, "w", encoding="utf-8") as log:
            subprocess.Popen(
                ["bash", "-c", cmd],
                stdout=log,
                stderr=log,
                start_new_session=True,
                close_fds=True,
            )
        return True, str(log_file)
    except OSError:
        return False, None


def update_and_sync():
    """Update CLI + sync all skills in background."""
    return run_background(UPDATE_CMD, "agent-browser-update.log")


def install_and_sync():
    """First install: CLI + browser download + skill sync in background."""
    try:
        COOLDOWN_FILE.touch()
    except OSError:
        pass
    return run_background(INSTALL_CMD, "agent-browser-install.log")


def cleanup_orphan_daemons():
    """Kill agent-browser daemons and their orphan children.

    Phase 1 — PID files: read PID, SIGTERM, remove session files. ~0.1ms.
    Phase 2 — pkill fallback: only if orphan .sock files remain after Phase 1
              (daemon that lost its PID file via crash/kill -9). ~19ms, rare.
    Phase 3 — chrome-headless-shell: kill orphan browser processes left when
              daemons died without cleaning up children (PPID=1). ~19ms, rare.

    Safe to call unconditionally — agent-browser auto-restarts on next command.
    """
    if not AGENT_BROWSER_DIR.is_dir():
        return

    for pf in AGENT_BROWSER_DIR.glob("*.pid"):
        try:
            os.kill(int(pf.read_text().strip()), signal.SIGTERM)
        except (ValueError, ProcessLookupError, PermissionError, OSError):
            pass
        for ext in SESSION_EXTS:
            try:
                pf.with_suffix(ext).unlink(missing_ok=True)
            except OSError:
                pass

    # pkill fallback: orphan sockets indicate a daemon that lost its PID file
    if any(AGENT_BROWSER_DIR.glob("*.sock")) and sys.platform in ("darwin", "linux"):
        try:
            subprocess.run(
                ["pkill", "-TERM", "-f", f"agent-browser-{sys.platform}"],
                capture_output=True, timeout=5,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass

    # Phase 3: kill orphan chrome-headless-shell processes.
    # When the daemon dies without cleanup, chrome children survive with PPID=1.
    # -P 1 ensures only true orphans are killed — active chrome from
    # parallel sessions (PPID=daemon) is untouched.
    if sys.platform in ("darwin", "linux"):
        try:
            subprocess.run(
                ["pkill", "-TERM", "-P", "1", "-f", "chrome-headless-shell"],
                capture_output=True, timeout=5,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass


def consume_stdin():
    """Consume stdin as required by hook protocol."""
    try:
        if sys.stdin is not None:
            sys.stdin.read()
    except (OSError, ValueError):
        pass


def main():
    """Entry point."""
    consume_stdin()
    cleanup_orphan_daemons()

    skip_install = os.environ.get(
        "AI_FRAMEWORK_SKIP_BROWSER_INSTALL", ""
    ).lower() in ("1", "true")

    context = ""

    if is_installed():
        if not _update_ran_recently():
            update_and_sync()
    elif not skip_install:
        if not is_cooldown_active():
            ok, _ = install_and_sync()
            if not ok:
                context = "agent-browser install failed. Inform user: npm install -g agent-browser"

    if context:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        }))
    else:
        print(json.dumps({}))


if __name__ == "__main__":
    main()
