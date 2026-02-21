#!/usr/bin/env python3
"""TeammateIdle hook — safety net for ralph-orchestrator teammates.

Fires when an Agent Teams teammate is about to go idle.
Exit 0 = teammate goes idle normally. The LEAD manages task flow.

Guard: only activates in ralph-orchestrator projects (.ralph/config.sh).
Non-ralph Agent Teams usage is transparent (immediate exit 0).

Decision logic:
  1. ABORT file exists          → exit 0 (manual abort)
  2. Circuit breaker triggered  → exit 0 (consecutive failures exceeded)
  3. Default                    → exit 0 (allow idle, lead assigns work)
"""
import fcntl
import json
import os
import subprocess
import sys
from pathlib import Path



def load_max_failures(config_path):
    """Extract MAX_CONSECUTIVE_FAILURES from bash config (single subprocess)."""
    try:
        result = subprocess.run(
            [
                "bash", "-c",
                f"source '{config_path}' 2>/dev/null"
                " && printf '%s' \"${MAX_CONSECUTIVE_FAILURES:-3}\""
            ],
            capture_output=True, text=True, timeout=5,
        )
        val = result.stdout.strip()
        return int(val) if val.isdigit() else 3
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return 3


def read_failures(ralph_dir):
    """Read per-teammate failure counters from .ralph/failures.json."""
    failures_path = ralph_dir / "failures.json"
    try:
        if failures_path.exists():
            with open(failures_path, "r", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                data = json.load(f)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def main():
    """Main hook logic."""
    # Read input from stdin (hook protocol)
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # malformed input → pass-through

    cwd = os.environ.get("CLAUDE_PROJECT_DIR", input_data.get("cwd", os.getcwd()))
    teammate_name = input_data.get("teammate_name", "unknown")

    # Guard: not a ralph-orchestrator project
    ralph_dir = Path(cwd) / ".ralph"
    config_path = ralph_dir / "config.sh"
    if not config_path.exists():
        sys.exit(0)

    # Check manual abort
    if (ralph_dir / "ABORT").exists():
        sys.exit(0)

    # Circuit breaker: check consecutive failures for this teammate
    max_failures = load_max_failures(config_path)
    failures = read_failures(ralph_dir)
    teammate_failures = failures.get(teammate_name, 0)
    if teammate_failures >= max_failures:
        print(
            f"Circuit breaker: {teammate_name} hit {teammate_failures} "
            f"consecutive failures (max {max_failures}). Going idle.",
            file=sys.stderr,
        )
        sys.exit(0)

    # Default: allow idle — lead manages task assignment
    sys.exit(0)


if __name__ == "__main__":
    main()
