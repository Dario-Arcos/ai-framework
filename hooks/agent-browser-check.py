#!/usr/bin/env python3
"""SessionStart hook - Checks agent-browser and installs deterministically if missing."""
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def find_project_root():
    """Find project root by searching upward for .claude directory."""
    current = Path(os.getcwd()).resolve()
    for _ in range(20):
        if (current / ".claude").is_dir():
            return current
        if current == current.parent:
            break
        current = current.parent
    return None


def log_result(status: str, details: str = ""):
    """Log hook result for traceability."""
    try:
        project_root = find_project_root()
        if not project_root:
            return
        log_dir = project_root / ".claude" / "logs" / datetime.now().strftime("%Y-%m-%d")
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / "agent-browser-check.jsonl", "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "hook": "agent-browser-check",
                "status": status,
                "details": details
            }) + "\n")
    except Exception:
        pass


def is_agent_browser_installed() -> bool:
    """Check if agent-browser CLI is available in PATH."""
    try:
        result = subprocess.run(
            ["which", "agent-browser"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def install_agent_browser_background():
    """Install agent-browser in background process."""
    try:
        # Detached background process - won't block the hook
        subprocess.Popen(
            ["sh", "-c", "npm install -g agent-browser && agent-browser install"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def main():
    # Read hook input (required for SessionStart)
    try:
        raw = sys.stdin.read(1048576)
        json.loads(raw) if raw else {}
    except (json.JSONDecodeError, MemoryError):
        pass

    # Explicit skip via environment variable
    skip = os.environ.get("AI_FRAMEWORK_SKIP_BROWSER_INSTALL", "").lower() in ("1", "true")
    installed = is_agent_browser_installed()

    if installed:
        context = (
            "agent-browser: ✓ Installed. "
            "Use agent-browser skill for web tasks instead of WebFetch/WebSearch."
        )
        log_result("installed", "agent-browser already available")
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
