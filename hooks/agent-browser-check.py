#!/usr/bin/env python3
"""SessionStart hook - Checks agent-browser and installs if missing."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SUBPROCESS_TIMEOUT = 5


def find_project_root():
    """Find project root by searching upward for .claude directory."""
    current = Path.cwd().resolve()
    for _ in range(20):
        if (current / ".claude").is_dir():
            return current
        if current == current.parent:
            break
        current = current.parent
    return None


def is_installed():
    """Check if agent-browser CLI is in PATH."""
    return shutil.which("agent-browser") is not None


def get_installed_version():
    """Get installed agent-browser version."""
    try:
        result = subprocess.run(
            ["agent-browser", "--version"],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split()
            return parts[-1] if parts else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def install_background():
    """Install agent-browser in background."""
    try:
        subprocess.Popen(
            ["sh", "-c", "npm install -g agent-browser && agent-browser install"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True
        )
        return True
    except OSError:
        return False


def ensure_skill_synced(cli_version):
    """Ensure skill is copied to .claude/skills/."""
    root = find_project_root()
    if not root:
        return False, "no project root"

    dest_dir = root / ".claude" / "skills" / "agent-browser"
    version_file = dest_dir / ".version"
    skill_file = dest_dir / "SKILL.md"

    # Check if already synced
    if skill_file.exists():
        try:
            if version_file.read_text(encoding="utf-8").strip() == cli_version:
                return True, "synced"
        except OSError:
            pass

    # Find source in npm global
    try:
        result = subprocess.run(
            ["npm", "root", "-g"],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT
        )
        if result.returncode != 0:
            return False, "npm root failed"

        source_dir = Path(result.stdout.strip()) / "agent-browser" / "skills" / "agent-browser"
        if not source_dir.exists():
            return False, "source not found"

        # Copy skill directory
        dest_dir.parent.mkdir(parents=True, exist_ok=True)
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        shutil.copytree(source_dir, dest_dir)

        # Write version
        if cli_version:
            version_file.write_text(cli_version, encoding="utf-8")

        return True, "copied"

    except (subprocess.TimeoutExpired, OSError, shutil.Error) as e:
        return False, str(type(e).__name__)


def consume_stdin():
    """Consume stdin as required by hook protocol."""
    try:
        while True:
            if not sys.stdin.read(4096):
                break
    except (IOError, OSError):
        pass


def main():
    """Main hook logic."""
    consume_stdin()

    skip_install = os.environ.get(
        "AI_FRAMEWORK_SKIP_BROWSER_INSTALL", ""
    ).lower() in ("1", "true")

    if is_installed():
        version = get_installed_version()
        skill_ok, skill_msg = ensure_skill_synced(version)
        v = f"v{version}" if version else ""

        if skill_ok:
            context = f"agent-browser: ✓ {v}. Use agent-browser skill for web tasks."
        else:
            context = f"agent-browser: ✓ CLI {v}, ⚠ skill: {skill_msg}"

    elif skip_install:
        context = "agent-browser: ⚠ Skipped (AI_FRAMEWORK_SKIP_BROWSER_INSTALL=1)"

    else:
        if install_background():
            context = "agent-browser: ⏳ Installing in background..."
        else:
            context = "agent-browser: ✗ Install failed"

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context
        }
    }))


if __name__ == "__main__":
    main()
