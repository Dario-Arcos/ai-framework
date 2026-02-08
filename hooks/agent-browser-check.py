#!/usr/bin/env python3
"""SessionStart hook - Checks agent-browser CLI and syncs skill if missing.

Ensures CLI is installed and skill is available at user level (~/.claude/skills/)
via `npx skills` (Vercel's open skill ecosystem). Skill at user level is loaded
automatically by Claude Code in all projects — no per-project copy needed.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SUBPROCESS_TIMEOUT = 5
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+")

CLAUDE_HOME = Path(
    os.environ.get("CLAUDE_CONFIG_DIR", "").strip()
    or Path.home() / ".claude"
)
SKILL_FILE = CLAUDE_HOME / "skills" / "agent-browser" / "SKILL.md"

SKILL_ADD_CMD = (
    "npx -y skills add --global --yes vercel-labs/agent-browser"
    " -s agent-browser -a claude-code"
)


def is_installed():
    """Check if agent-browser CLI is in PATH."""
    return shutil.which("agent-browser") is not None


def get_installed_version():
    """Get installed agent-browser version. Returns semver string or None."""
    try:
        result = subprocess.run(
            ["agent-browser", "--version"],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
        )
        if result.returncode == 0 and result.stdout.strip():
            for token in reversed(result.stdout.strip().split()):
                if SEMVER_RE.match(token):
                    return token
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def is_skill_present():
    """Check if agent-browser skill exists at user level (~/.claude/skills/)."""
    try:
        return SKILL_FILE.exists() and SKILL_FILE.stat().st_size > 0
    except OSError:
        return False


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


def sync_skill_background():
    """Sync agent-browser skill to ~/.claude/skills/ via npx skills."""
    return run_background(SKILL_ADD_CMD, "agent-browser-skill-sync.log")


def install_background():
    """Install CLI + browsers + skill in background."""
    if sys.platform == "darwin" and shutil.which("brew"):
        install_cli = "(brew install agent-browser || npm install -g agent-browser)"
    else:
        install_cli = "npm install -g agent-browser"

    cmd = f"{install_cli} && agent-browser install && {SKILL_ADD_CMD}"
    return run_background(cmd, "agent-browser-install.log")


def consume_stdin():
    """Consume stdin as required by hook protocol."""
    try:
        sys.stdin.read()
    except OSError:
        pass


def main():
    """Main hook logic."""
    consume_stdin()

    skip_install = os.environ.get(
        "AI_FRAMEWORK_SKIP_BROWSER_INSTALL", ""
    ).lower() in ("1", "true")

    if is_installed():
        version = get_installed_version()
        v = f"v{version}" if version else ""

        if is_skill_present():
            context = f"agent-browser: ✓ {v}. Use agent-browser skill for web tasks."
        else:
            sync_skill_background()
            context = f"agent-browser: ✓ CLI {v}, ⏳ syncing skill..."

    elif skip_install:
        context = "agent-browser: ⚠ Skipped (AI_FRAMEWORK_SKIP_BROWSER_INSTALL=1)"

    else:
        ok, log_path = install_background()
        if ok:
            context = (
                f"agent-browser: ⏳ Installing in background... (log: {log_path})"
            )
        else:
            context = "agent-browser: ✗ Install failed"

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }))


if __name__ == "__main__":
    main()
