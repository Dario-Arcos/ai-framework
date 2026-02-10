#!/usr/bin/env python3
"""TeammateIdle hook — keeps ralph-orchestrator teammates working.

Fires when an Agent Teams teammate is about to go idle.
Exit 2 = teammate receives stderr as feedback and continues working.
Exit 0 = teammate goes idle normally.

Guard: only activates in ralph-orchestrator projects (.ralph/config.sh).
Non-ralph Agent Teams usage is transparent (immediate exit 0).

Decision logic:
  1. ABORT file exists          → exit 0 (manual abort)
  2. Circuit breaker triggered  → exit 0 (consecutive failures exceeded)
  3. Rotation threshold reached → exit 0 (teammate writes handoff, lead respawns)
  4. Pending tasks remain       → exit 2 (keep working)
  5. All tasks complete         → exit 0 (allow idle)
"""
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


def load_max_tasks_per_teammate(config_path):
    """Extract MAX_TASKS_PER_TEAMMATE from bash config."""
    try:
        result = subprocess.run(
            ["bash", "-c",
             f"source '{config_path}' 2>/dev/null"
             " && printf '%s' \"${MAX_TASKS_PER_TEAMMATE:-20}\""],
            capture_output=True, text=True, timeout=5,
        )
        val = result.stdout.strip()
        return int(val) if val.isdigit() else 20
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return 20


def read_failures(ralph_dir):
    """Read per-teammate failure counters from .ralph/failures.json."""
    failures_path = ralph_dir / "failures.json"
    try:
        if failures_path.exists():
            with open(failures_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def read_teammate_completed(ralph_dir, teammate_name):
    """Read completed task count for a specific teammate from metrics.json."""
    metrics_path = ralph_dir / "metrics.json"
    try:
        if metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                metrics = json.load(f)
            per_teammate = metrics.get("per_teammate", {})
            teammate_stats = per_teammate.get(teammate_name, {})
            return teammate_stats.get("completed", 0)
    except (json.JSONDecodeError, OSError):
        pass
    return 0


def count_pending_tasks(cwd):
    """Count .code-task.md files with Status: PENDING or IN_PROGRESS.

    Returns:
        int: number of pending/in-progress tasks, or -1 on error.
    """
    try:
        result = subprocess.run(
            [
                "grep", "-rlE",
                "Status: (PENDING|IN_PROGRESS)",
                "--include=*.code-task.md",
                ".",
            ],
            capture_output=True, text=True, cwd=cwd, timeout=10,
        )
        lines = [l for l in result.stdout.strip().split("\n") if l]
        return len(lines)
    except (subprocess.TimeoutExpired, OSError):
        return -1  # error → assume tasks remain (safe default)


def main():
    """Main hook logic."""
    # Read input from stdin (hook protocol)
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # malformed input → pass-through

    cwd = input_data.get("cwd", os.getcwd())
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

    # Rotation threshold: rotate coordinator after N completed tasks
    max_tasks = load_max_tasks_per_teammate(config_path)
    if max_tasks > 0:
        completed = read_teammate_completed(ralph_dir, teammate_name)
        if completed >= max_tasks:
            print(
                f"Rotation threshold reached: {teammate_name} completed "
                f"{completed}/{max_tasks} tasks. Write your handoff summary "
                f"to .ralph/handoff-{teammate_name}.md, then go idle.",
                file=sys.stderr,
            )
            sys.exit(0)

    # Count pending tasks
    pending = count_pending_tasks(cwd)
    if pending == 0:
        sys.exit(0)  # all done → allow idle

    # Tasks remain → keep working
    print(
        "Re-read guardrails.md for latest lessons from other teammates. "
        "Claim your next task from the task list.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
