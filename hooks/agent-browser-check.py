#!/usr/bin/env python3
"""SessionStart hook - Checks agent-browser CLI and syncs skill if missing.

Ensures CLI is installed and skill is available at user level (~/.claude/skills/)
by copying from the global npm package. Skill at user level is loaded
automatically by Claude Code in all projects — no per-project copy needed.

Also cleans up orphan agent-browser daemons from previous sessions.
Daemons have no idle timeout and survive terminal close, accumulating
until memory is exhausted. Cleanup here is safe because agent-browser
auto-restarts its daemon on the next command (~200ms penalty, once).

Performance: happy path is ~0.2ms (three stat calls, zero subprocesses).
Daemon cleanup adds ~17ms (one pgrep call; pkill only if orphans found).
Sync/install only triggers on first-ever setup, with 1h cooldown on retries.
Auto-update checks CLI + skill every 24h in a detached background process.
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

CLAUDE_HOME = Path(
    os.environ.get("CLAUDE_CONFIG_DIR", "").strip()
    or Path.home() / ".claude"
)
SKILL_DIR = CLAUDE_HOME / "skills" / "agent-browser"
SKILL_FILE = SKILL_DIR / "SKILL.md"
COOLDOWN_FILE = Path(tempfile.gettempdir()) / "agent-browser-sync-ts"
SYNC_COOLDOWN_SECS = 3600

SKILL_COPY_CMD = (
    'SKILL_SRC="$(npm root -g)/agent-browser/skills/agent-browser"'
    ' && [ -d "$SKILL_SRC" ]'
    f' && rm -rf "{SKILL_DIR}"'
    f' && mkdir -p "{SKILL_DIR}"'
    f' && cp -r "$SKILL_SRC/." "{SKILL_DIR}/"'
)

UPDATE_CHECK_FILE = Path(tempfile.gettempdir()) / "agent-browser-update-ts"
UPDATE_CHECK_SECS = 86400  # 24h


def is_installed():
    """Check if agent-browser CLI is in PATH."""
    return shutil.which("agent-browser") is not None


def is_skill_present():
    """Check if agent-browser skill exists at user level (~/.claude/skills/)."""
    try:
        return SKILL_FILE.exists() and SKILL_FILE.stat().st_size > 0
    except OSError:
        return False


def is_cooldown_active():
    """Prevent retry storms: skip if last attempt was < SYNC_COOLDOWN_SECS ago."""
    try:
        if COOLDOWN_FILE.exists():
            return (time.time() - COOLDOWN_FILE.stat().st_mtime) < SYNC_COOLDOWN_SECS
    except OSError:
        pass
    return False


def touch_cooldown():
    """Mark that a sync/install attempt just started."""
    try:
        COOLDOWN_FILE.touch()
    except OSError:
        pass


def run_background(cmd, log_name):
    """Run a shell command in background. Returns (started, log_path)."""
    try:
        log_file = Path(tempfile.gettempdir()) / log_name
        with open(log_file, "w", encoding="utf-8") as log:
            subprocess.Popen(
                ["sh", "-c", cmd],
                stdout=log,
                stderr=log,
                start_new_session=True,
                close_fds=True,
            )
        return True, str(log_file)
    except OSError:
        return False, None


def touch_update_check():
    """Mark that an update check just happened (or a fresh install/sync)."""
    try:
        UPDATE_CHECK_FILE.touch()
    except OSError:
        pass


def sync_skill_background():
    """Copy agent-browser skill from global npm package to ~/.claude/skills/."""
    touch_cooldown()
    touch_update_check()  # fresh sync = latest version
    return run_background(SKILL_COPY_CMD, "agent-browser-skill-sync.log")


def is_update_due():
    """Check if enough time has passed since the last auto-update check."""
    try:
        if UPDATE_CHECK_FILE.exists():
            return (time.time() - UPDATE_CHECK_FILE.stat().st_mtime) >= UPDATE_CHECK_SECS
    except OSError:
        pass
    return True  # no timestamp = never checked = due


def update_background():
    """Auto-update CLI via npm and re-sync skill in background."""
    touch_update_check()

    cmd = f"npm update -g agent-browser 2>/dev/null && {SKILL_COPY_CMD}"
    return run_background(cmd, "agent-browser-update.log")


def install_background():
    """Install CLI + browsers + skill in background."""
    touch_cooldown()
    touch_update_check()  # fresh install = latest version
    cmd = f"npm install -g agent-browser && agent-browser install && {SKILL_COPY_CMD}"
    return run_background(cmd, "agent-browser-install.log")


def cleanup_orphan_daemons():
    """Kill agent-browser daemons left by previous sessions.

    Scans PID files in ~/.agent-browser/ and kills processes that are still
    alive. Then removes stale PID/sock files. Returns the number of daemons
    killed. Safe to call unconditionally — agent-browser auto-restarts its
    daemon on the next command.
    """
    killed = 0
    try:
        if not AGENT_BROWSER_DIR.is_dir():
            return 0
        for pid_file in AGENT_BROWSER_DIR.glob("*.pid"):
            try:
                pid = int(pid_file.read_text().strip())
                os.kill(pid, signal.SIGTERM)
                killed += 1
            except (ValueError, ProcessLookupError, PermissionError):
                pass
            # Clean up PID + sock regardless (stale or just killed)
            try:
                pid_file.unlink(missing_ok=True)
            except OSError:
                pass
            sock_file = pid_file.with_suffix(".sock")
            try:
                sock_file.unlink(missing_ok=True)
            except OSError:
                pass
    except OSError:
        pass
    return killed


def consume_stdin():
    """Consume stdin as required by hook protocol."""
    try:
        if sys.stdin is not None:
            sys.stdin.read()
    except (OSError, ValueError):
        pass


def main():
    """Main hook logic."""
    consume_stdin()
    cleanup_orphan_daemons()

    skip_install = os.environ.get(
        "AI_FRAMEWORK_SKIP_BROWSER_INSTALL", ""
    ).lower() in ("1", "true")

    if is_installed():
        if is_skill_present():
            if is_update_due():
                update_background()
            context = "agent-browser: ready"
        elif is_cooldown_active():
            context = "agent-browser: syncing skill"
        else:
            sync_skill_background()
            context = "agent-browser: syncing skill"

    elif skip_install:
        context = "agent-browser: skipped"

    elif is_cooldown_active():
        context = "agent-browser: installing"

    else:
        ok, _ = install_background()
        context = "agent-browser: installing" if ok else "agent-browser: install failed"

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }))


if __name__ == "__main__":
    main()
