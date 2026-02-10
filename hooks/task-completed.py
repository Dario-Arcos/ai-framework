#!/usr/bin/env python3
"""TaskCompleted hook — quality gates and failure tracking for ralph-orchestrator.

Fires when an Agent Teams teammate marks a task as complete.
Exit 2 = task NOT marked complete, stderr fed back to teammate.
Exit 0 = task marked complete.

Guard: only activates in ralph-orchestrator projects (.ralph/config.sh).
Non-ralph Agent Teams usage is transparent (immediate exit 0).

Decision logic:
  1. prototype quality  → exit 0 (skip all gates)
  2. Run gates in order → first failure = exit 2 + increment failures.json
  3. All gates pass     → exit 0 + reset failures.json + update metrics.json
"""
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path


# ─────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────

CONFIG_KEYS = [
    "QUALITY_LEVEL",
    "GATE_TEST",
    "GATE_TYPECHECK",
    "GATE_LINT",
    "GATE_BUILD",
]

CONFIG_DEFAULTS = {
    "QUALITY_LEVEL": "production",
    "GATE_TEST": "npm test",
    "GATE_TYPECHECK": "npm run typecheck",
    "GATE_LINT": "npm run lint",
    "GATE_BUILD": "npm run build",
}


def load_config(config_path):
    """Source bash config and extract known keys (single subprocess)."""
    config = dict(CONFIG_DEFAULTS)
    if not config_path.exists():
        return config

    # Build printf chain: source config → print each value null-separated
    # Use ${VAR-default} (not :-) so explicitly empty values are preserved
    printf_parts = " ".join(
        f'"${{{k}-{CONFIG_DEFAULTS[k]}}}"' for k in CONFIG_KEYS
    )
    script = (
        f"source '{config_path}' 2>/dev/null"
        f" && printf '%s\\0' {printf_parts}"
    )

    try:
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            values = result.stdout.split("\0")
            for i, key in enumerate(CONFIG_KEYS):
                if i < len(values):
                    config[key] = values[i]
    except (subprocess.TimeoutExpired, OSError):
        pass

    return config


# ─────────────────────────────────────────────────────────────────
# FAILURES TRACKING (with file locking)
# ─────────────────────────────────────────────────────────────────

def _failures_path(ralph_dir):
    return ralph_dir / "failures.json"


def read_failures(ralph_dir):
    """Read per-teammate failure counters."""
    path = _failures_path(ralph_dir)
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                data = json.load(f)
                fcntl.flock(f, fcntl.LOCK_UN)
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def write_failures(ralph_dir, failures):
    """Write failure counters atomically with exclusive lock."""
    path = _failures_path(ralph_dir)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(failures, f, indent=2)
            f.write("\n")
            fcntl.flock(f, fcntl.LOCK_UN)
    except OSError:
        pass


def increment_failure(ralph_dir, teammate_name):
    """Increment failure counter for a teammate."""
    failures = read_failures(ralph_dir)
    failures[teammate_name] = failures.get(teammate_name, 0) + 1
    write_failures(ralph_dir, failures)
    return failures[teammate_name]


def reset_failure(ralph_dir, teammate_name):
    """Reset failure counter for a teammate (on success)."""
    failures = read_failures(ralph_dir)
    if teammate_name in failures:
        failures[teammate_name] = 0
        write_failures(ralph_dir, failures)


# ─────────────────────────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────────────────────────

def update_metrics(ralph_dir, success):
    """Update .ralph/metrics.json with task result (locked)."""
    metrics_path = ralph_dir / "metrics.json"
    try:
        metrics = {}
        if metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                metrics = json.load(f)
                fcntl.flock(f, fcntl.LOCK_UN)

        metrics["total_tasks"] = metrics.get("total_tasks", 0) + 1
        key = "successful_tasks" if success else "failed_tasks"
        metrics[key] = metrics.get(key, 0) + 1
        metrics["last_updated"] = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
        )

        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        with open(metrics_path, "w", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(metrics, f, indent=2)
            f.write("\n")
            fcntl.flock(f, fcntl.LOCK_UN)
    except (json.JSONDecodeError, OSError):
        pass


# ─────────────────────────────────────────────────────────────────
# QUALITY GATES
# ─────────────────────────────────────────────────────────────────

def run_gate(name, command, cwd):
    """Run a single quality gate.

    Returns:
        (passed: bool, output: str)
    """
    if not command:
        return True, ""

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=120,
        )
        output = (result.stdout + result.stderr).strip()
        # Truncate to last 800 chars for readable feedback
        if len(output) > 800:
            output = "...\n" + output[-800:]
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"Gate '{name}' timed out after 120s"
    except OSError as e:
        return False, f"Gate '{name}' failed to execute: {e}"


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    """Main hook logic."""
    # Read input from stdin (hook protocol)
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # malformed input → pass-through

    cwd = input_data.get("cwd", os.getcwd())
    task_subject = input_data.get("task_subject", "unknown task")
    teammate_name = input_data.get("teammate_name", "unknown")

    # Guard: not a ralph-orchestrator project
    ralph_dir = Path(cwd) / ".ralph"
    config_path = ralph_dir / "config.sh"
    if not config_path.exists():
        sys.exit(0)

    # Load config
    config = load_config(config_path)

    # Prototype: skip all gates
    if config["QUALITY_LEVEL"] == "prototype":
        reset_failure(ralph_dir, teammate_name)
        update_metrics(ralph_dir, success=True)
        sys.exit(0)

    # Run quality gates in order
    gates = [
        ("test", config["GATE_TEST"]),
        ("typecheck", config["GATE_TYPECHECK"]),
        ("lint", config["GATE_LINT"]),
        ("build", config["GATE_BUILD"]),
    ]

    for gate_name, gate_cmd in gates:
        if not gate_cmd:
            continue

        passed, output = run_gate(gate_name, gate_cmd, cwd)

        if not passed:
            count = increment_failure(ralph_dir, teammate_name)
            update_metrics(ralph_dir, success=False)
            print(
                f"Quality gate '{gate_name}' failed for: {task_subject}\n\n"
                f"Output:\n{output}\n\n"
                f"Fix the issue before completing this task. "
                f"(consecutive failures: {count})",
                file=sys.stderr,
            )
            sys.exit(2)

    # All gates passed
    reset_failure(ralph_dir, teammate_name)
    update_metrics(ralph_dir, success=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
