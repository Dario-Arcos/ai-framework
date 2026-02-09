#!/usr/bin/env python3
"""SessionStart hook - Checks agent-browser CLI and syncs skill if missing.

Ensures CLI is installed and skill is available at user level (~/.claude/skills/)
via `npx skills` (Vercel's open skill ecosystem). Skill at user level is loaded
automatically by Claude Code in all projects — no per-project copy needed.

Performance: happy path is ~0.2ms (three stat calls, zero subprocesses).
Sync/install only triggers on first-ever setup, with 1h cooldown on retries.
Auto-update checks CLI + skill every 24h in a detached background process.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CLAUDE_HOME = Path(
    os.environ.get("CLAUDE_CONFIG_DIR", "").strip()
    or Path.home() / ".claude"
)
SKILL_FILE = CLAUDE_HOME / "skills" / "agent-browser" / "SKILL.md"
COOLDOWN_FILE = Path(tempfile.gettempdir()) / "agent-browser-sync-ts"
SYNC_COOLDOWN_SECS = 3600

SKILL_ADD_CMD = (
    "npx -y skills add --global --yes vercel-labs/agent-browser"
    " -s agent-browser -a claude-code"
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
    """Sync agent-browser skill to ~/.claude/skills/ via npx skills."""
    touch_cooldown()
    touch_update_check()  # fresh sync = latest version
    return run_background(SKILL_ADD_CMD, "agent-browser-skill-sync.log")


def is_update_due():
    """Check if enough time has passed since the last auto-update check."""
    try:
        if UPDATE_CHECK_FILE.exists():
            return (time.time() - UPDATE_CHECK_FILE.stat().st_mtime) >= UPDATE_CHECK_SECS
    except OSError:
        pass
    return True  # no timestamp = never checked = due


def update_background():
    """Auto-update skill (via npx skills update) and CLI in background."""
    touch_update_check()

    cmd = "npx -y skills update 2>/dev/null; npm update -g agent-browser 2>/dev/null"
    return run_background(cmd, "agent-browser-update.log")


def install_background():
    """Install CLI + browsers + skill in background."""
    touch_cooldown()
    touch_update_check()  # fresh install = latest version
    cmd = f"npm install -g agent-browser && agent-browser install && {SKILL_ADD_CMD}"
    return run_background(cmd, "agent-browser-install.log")


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
