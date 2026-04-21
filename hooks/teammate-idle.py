#!/usr/bin/env python3
"""TeammateIdle hook — safety net for ralph-orchestrator teammates.

Fires when an Agent Teams teammate is about to go idle.
Exit 0 = teammate goes idle normally. The LEAD manages task flow.

Guard: only activates in ralph-orchestrator projects (.ralph/config.sh).
Non-ralph Agent Teams usage is transparent (immediate exit 0).

Decision logic:
  1. ABORT file exists          -> exit 0 (manual abort)
  2. Circuit breaker triggered  -> exit 0 (consecutive failures exceeded)
  3. Default                    -> exit 0 (allow idle, lead assigns work)

Phase 9.2: on ABORT or circuit-open, auto-generate a mission report
so the developer wakes up to a structured summary of what the factory
did, instead of a raw metrics.jsonl.
"""
try:
    import fcntl
except ImportError:
    fcntl = None  # Windows — file locking skipped
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import _parse_utc_timestamp


_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
_AGGREGATE_SCRIPT = (
    _PLUGIN_ROOT / "skills" / "mission-report" / "scripts" / "aggregate.py"
)


def _generate_mission_report(cwd):
    """Best-effort: render and persist a mission report.

    Loads the aggregator dynamically so this hook doesn't depend on it
    at import time (graceful degradation if skill is absent or broken).
    Returns the written path, or None on any failure.
    """
    if not _AGGREGATE_SCRIPT.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            "_mission_report_aggregate", _AGGREGATE_SCRIPT,
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.write_report(cwd)
    except Exception:  # noqa: BLE001 - telemetry side-effect must never crash hook
        return None


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


def read_failures(ralph_dir, max_age_seconds=7200):
    """Read per-teammate failure counters from .ralph/failures.json.

    Args:
        max_age_seconds: Ignore failures older than this (default 7200s = 2h).
            Prevents stale failures from previous orchestration runs
            triggering circuit breaker in new runs.
    """
    failures_path = ralph_dir / "failures.json"
    try:
        if failures_path.exists():
            with open(failures_path, "r", encoding="utf-8") as f:
                if fcntl:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                data = json.load(f)
                if fcntl:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # TTL check: ignore stale failures from previous runs
            ts = data.get("_updated_at")
            if not ts:
                return {}  # No timestamp -> legacy/stale -> ignore
            written = _parse_utc_timestamp(ts)
            if written is None:
                return {}  # Unparseable -> treat as stale
            if time.time() - written > max_age_seconds:
                return {}

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
        sys.exit(0)  # malformed input -> pass-through

    cwd = os.environ.get("CLAUDE_PROJECT_DIR", input_data.get("cwd", os.getcwd()))
    teammate_name = input_data.get("teammate_name", "unknown")

    # Guard: not a ralph-orchestrator project
    ralph_dir = Path(cwd) / ".ralph"
    config_path = ralph_dir / "config.sh"
    if not config_path.exists():
        sys.exit(0)

    # Check manual abort. Auto-generate a mission report so the dev
    # wakes up to a structured summary (Phase 9.2).
    abort_path = ralph_dir / "ABORT"
    if abort_path.exists():
        report_path = _generate_mission_report(cwd)
        extra = (f"\nMission report: {report_path}"
                 if report_path is not None else "")
        print(
            f"Orchestration aborted — ABORT file detected\n\n"
            f"Path: {abort_path}\n"
            f"Remove this file to resume orchestration.{extra}",
            file=sys.stderr,
        )
        sys.exit(0)

    # Circuit breaker: check consecutive failures for this teammate.
    # Circuit-open marks the end of this teammate's contribution to the
    # mission, so auto-generate a report (Phase 9.2).
    max_failures = load_max_failures(config_path)
    failures = read_failures(ralph_dir)
    teammate_failures = failures.get(teammate_name, 0)
    if teammate_failures >= max_failures:
        report_path = _generate_mission_report(cwd)
        extra = (f"\nMission report: {report_path}"
                 if report_path is not None else "")
        print(
            f"Circuit breaker triggered — {teammate_name} going idle\n\n"
            f"{teammate_failures} consecutive failures (max allowed: {max_failures}).\n"
            f"Teammate will not receive new tasks until failures are resolved.{extra}",
            file=sys.stderr,
        )
        sys.exit(0)

    # Default: allow idle - lead manages task assignment
    sys.exit(0)


if __name__ == "__main__":
    main()
