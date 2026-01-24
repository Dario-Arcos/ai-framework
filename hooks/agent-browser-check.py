#!/usr/bin/env python3
"""SessionStart hook - Checks agent-browser and installs deterministically if missing."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Cache for project root (computed once per execution)
_project_root_cache: Path | None = None
_project_root_computed = False

# How often to check npm for updates (avoid network call every session)
VERSION_CHECK_INTERVAL_HOURS = 24


def find_project_root() -> Path | None:
    """Find project root by searching upward for .claude directory. Cached."""
    global _project_root_cache, _project_root_computed
    if _project_root_computed:
        return _project_root_cache

    current = Path(os.getcwd()).resolve()
    for _ in range(20):
        if (current / ".claude").is_dir():
            _project_root_cache = current
            _project_root_computed = True
            return current
        if current == current.parent:
            break
        current = current.parent

    _project_root_computed = True
    return None


def log_result(status: str, details: str = ""):
    """Log hook result for traceability."""
    try:
        project_root = find_project_root()
        if not project_root:
            return
        now = datetime.now()
        log_dir = project_root / ".claude" / "logs" / now.strftime("%Y-%m-%d")
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / "agent-browser-check.jsonl", "a") as f:
            f.write(json.dumps({
                "timestamp": now.isoformat(),
                "hook": "agent-browser-check",
                "status": status,
                "details": details
            }) + "\n")
    except Exception:
        pass


def is_agent_browser_installed() -> bool:
    """Check if agent-browser CLI is available in PATH."""
    return shutil.which("agent-browser") is not None


def get_npm_global_path() -> Path | None:
    """Get npm global modules path dynamically."""
    try:
        result = subprocess.run(
            ["npm", "root", "-g"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def get_installed_version() -> str | None:
    """Get installed agent-browser version."""
    try:
        result = subprocess.run(
            ["agent-browser", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Output format: "agent-browser X.Y.Z" - take last token
            parts = result.stdout.strip().split()
            return parts[-1] if parts else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def get_version_cache_file() -> Path | None:
    """Get path to version cache file."""
    project_root = find_project_root()
    if project_root:
        return project_root / ".claude" / "cache" / "agent-browser-version.json"
    return None


def get_latest_npm_version() -> str | None:
    """
    Get latest agent-browser version from npm registry.
    Uses cache to avoid network call on every session.
    """
    cache_file = get_version_cache_file()

    # Try cache first
    if cache_file:
        try:
            cache_data = json.loads(cache_file.read_text())
            cached_time = datetime.fromisoformat(cache_data["checked_at"])
            if datetime.now() - cached_time < timedelta(hours=VERSION_CHECK_INTERVAL_HOURS):
                return cache_data.get("version")
        except (OSError, json.JSONDecodeError, KeyError, ValueError):
            pass

    # Cache miss or expired - fetch from npm
    try:
        result = subprocess.run(
            ["npm", "view", "agent-browser", "version"],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            # Update cache
            if cache_file and version:
                try:
                    cache_file.parent.mkdir(parents=True, exist_ok=True)
                    cache_file.write_text(json.dumps({
                        "version": version,
                        "checked_at": datetime.now().isoformat()
                    }))
                except OSError:
                    pass
            return version
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def get_skill_version(skill_dir: Path) -> str | None:
    """Read version from skill's .version file."""
    try:
        return (skill_dir / ".version").read_text().strip()
    except (OSError, FileNotFoundError):
        return None


def save_skill_version(skill_dir: Path, version: str) -> None:
    """Save version to skill's .version file."""
    try:
        (skill_dir / ".version").write_text(version)
    except OSError:
        pass


def ensure_skill_installed(cli_version: str | None = None) -> tuple[bool, str]:
    """
    Copy agent-browser skill to .claude/skills/ if not present or outdated.

    Args:
        cli_version: Current CLI version to sync skill with

    Returns:
        (success, message) tuple
    """
    project_root = find_project_root()
    if not project_root:
        return False, "project root not found"

    dest_skill_dir = project_root / ".claude" / "skills" / "agent-browser"
    skill_exists = dest_skill_dir.exists() and (dest_skill_dir / "SKILL.md").exists()
    skill_version = get_skill_version(dest_skill_dir) if skill_exists else None
    needs_update = skill_exists and cli_version and skill_version != cli_version

    # Already installed and up to date
    if skill_exists and not needs_update:
        return True, "skill already present"

    # Find source skill in npm global modules
    npm_global = get_npm_global_path()
    if not npm_global:
        return False, "npm global path not found"

    source_skill_dir = npm_global / "agent-browser" / "skills" / "agent-browser"
    if not source_skill_dir.exists():
        return False, "source skill not found in npm package"

    # Ensure parent directory exists
    dest_skill_dir.parent.mkdir(parents=True, exist_ok=True)

    # Remove old skill if updating
    if needs_update and dest_skill_dir.exists():
        try:
            shutil.rmtree(dest_skill_dir)
        except OSError as e:
            return False, f"failed to remove old skill: {e}"

    # Copy skill directory
    try:
        shutil.copytree(source_skill_dir, dest_skill_dir)
        # Save version for future sync checks
        if cli_version:
            save_skill_version(dest_skill_dir, cli_version)
        action = "updated" if needs_update else "copied"
        return True, f"skill {action} successfully"
    except (shutil.Error, OSError) as e:
        return False, f"copy failed: {e}"


def run_npm_background(command: str) -> bool:
    """Run an npm command in a detached background process."""
    try:
        subprocess.Popen(
            ["sh", "-c", command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def install_agent_browser_background() -> bool:
    """Install agent-browser in background process."""
    return run_npm_background("npm install -g agent-browser && agent-browser install")


def update_agent_browser_background() -> bool:
    """Update agent-browser to latest version in background process."""
    return run_npm_background("npm update -g agent-browser")


def main():
    # Consume hook input (required for SessionStart protocol)
    try:
        sys.stdin.read(1048576)
    except (IOError, MemoryError):
        pass

    # Explicit skip via environment variable
    skip = os.environ.get("AI_FRAMEWORK_SKIP_BROWSER_INSTALL", "").lower() in ("1", "true")
    installed = is_agent_browser_installed()

    if installed:
        # Check versions for update
        current_version = get_installed_version()
        latest_version = get_latest_npm_version()
        update_available = current_version and latest_version and current_version != latest_version

        # Trigger background update if newer version available
        if update_available:
            update_agent_browser_background()
            log_result("updating", f"v{current_version} -> v{latest_version}")

        # Ensure skill is copied/synced to .claude/skills/
        skill_ok, skill_msg = ensure_skill_installed(cli_version=current_version)

        if skill_ok:
            version_info = f"v{current_version}" if current_version else ""
            update_note = f" (updating to v{latest_version})" if update_available else ""
            context = (
                f"agent-browser: ✓ Installed {version_info}{update_note}. "
                "Use agent-browser skill for web tasks instead of WebFetch/WebSearch."
            )
            log_result("installed", f"{version_info}, {skill_msg}")
        else:
            context = (
                "agent-browser: ✓ CLI installed, ⚠ skill not copied. "
                "Use Bash(agent-browser ...) directly. "
                f"Skill issue: {skill_msg}"
            )
            log_result("partial", f"CLI ok but skill issue: {skill_msg}")
    elif skip:
        context = (
            "agent-browser: ⚠ Skipped. "
            "Use WebFetch/WebSearch for web tasks."
        )
        log_result("skipped", "AI_FRAMEWORK_SKIP_BROWSER_INSTALL=1")
    else:
        # Deterministically install in background
        started = install_agent_browser_background()
        if started:
            context = (
                "agent-browser: ⏳ Installing in background. "
                "Use WebFetch/WebSearch for now. agent-browser will be available shortly."
            )
            log_result("installing", "background install started")
        else:
            context = (
                "agent-browser: ✗ Install failed. "
                "Use WebFetch/WebSearch for web tasks."
            )
            log_result("failed", "could not start background install")

    # Output context for Claude
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
