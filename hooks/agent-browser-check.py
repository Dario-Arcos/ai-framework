#!/usr/bin/env python3
"""SessionStart hook - Checks agent-browser and installs if missing.

Supports both npm and Homebrew installations. Prefers brew on macOS.
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
SKILL_MARKER = Path("skills") / "agent-browser" / "SKILL.md"


def find_project_root():
    """Find project root from hook file location."""
    return Path(__file__).resolve().parent.parent


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
            timeout=SUBPROCESS_TIMEOUT
        )
        if result.returncode == 0 and result.stdout.strip():
            for token in reversed(result.stdout.strip().split()):
                if SEMVER_RE.match(token):
                    return token
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def find_skill_source():
    """Find agent-browser skill source directory. Works with npm and brew.

    Strategy 1: Resolve binary symlinks, walk up looking for skills/ (npm)
    Strategy 2: From resolved binary parent, check lib/node_modules/ (brew)
    Strategy 3: Fallback to npm root -g (npm without symlinks)
    """
    bin_path = shutil.which("agent-browser")
    if not bin_path:
        return None

    resolved = Path(bin_path).resolve()

    # Strategy 1: Walk up from resolved binary (works for npm global)
    # npm layout: .../node_modules/agent-browser/bin/<binary>
    # Walking up 2 levels reaches the package root with skills/
    for parent in list(resolved.parents)[:6]:
        skill = parent / SKILL_MARKER
        if skill.exists():
            return skill.parent

    # Strategy 2: Check sibling lib/node_modules structure (works for brew)
    # brew layout: .../libexec/bin/<binary>
    # Package root: .../libexec/lib/node_modules/agent-browser/
    for parent in list(resolved.parents)[:6]:
        skill = parent / "lib" / "node_modules" / "agent-browser" / SKILL_MARKER
        if skill.exists():
            return skill.parent

    # Strategy 3: Fallback to npm root -g
    try:
        result = subprocess.run(
            ["npm", "root", "-g"],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT
        )
        if result.returncode == 0:
            skill = Path(result.stdout.strip()) / "agent-browser" / SKILL_MARKER
            if skill.exists():
                return skill.parent
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    return None


def install_background():
    """Install agent-browser in background. Prefers brew on macOS, npm otherwise."""
    if sys.platform == "darwin" and shutil.which("brew"):
        cmd = "brew install agent-browser && agent-browser install || npm install -g agent-browser && agent-browser install"
    else:
        cmd = "npm install -g agent-browser && agent-browser install"

    try:
        log_file = Path(tempfile.gettempdir()) / "agent-browser-install.log"
        with open(log_file, "w", encoding="utf-8") as log:
            subprocess.Popen(
                ["sh", "-c", cmd],
                stdout=log,
                stderr=log,
                start_new_session=True,
                close_fds=True
            )
        return True, str(log_file)
    except OSError:
        return False, None


def ensure_skill_synced(cli_version):
    """Ensure skill is copied to .claude/skills/."""
    root = find_project_root()
    if not root.is_dir():
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

    # Find source (works with npm and brew)
    source_dir = find_skill_source()
    if not source_dir:
        return False, "source not found"

    try:
        dest_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)

        # Validate copy: SKILL.md must exist and not be empty
        if not skill_file.exists() or skill_file.stat().st_size == 0:
            return False, "copy verification failed"

        if cli_version:
            version_file.write_text(cli_version, encoding="utf-8")

        return True, "copied"

    except (OSError, shutil.Error) as e:
        return False, str(type(e).__name__)


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
        skill_ok, skill_msg = ensure_skill_synced(version)
        v = f"v{version}" if version else ""

        if skill_ok:
            context = f"agent-browser: ✓ {v}. Use agent-browser skill for web tasks."
        else:
            context = f"agent-browser: ✓ CLI {v}, ⚠ skill: {skill_msg}"

    elif skip_install:
        context = "agent-browser: ⚠ Skipped (AI_FRAMEWORK_SKIP_BROWSER_INSTALL=1)"

    else:
        ok, log_path = install_background()
        if ok:
            context = f"agent-browser: ⏳ Installing in background... (log: {log_path})"
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
