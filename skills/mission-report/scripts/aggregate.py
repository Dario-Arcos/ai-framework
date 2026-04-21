#!/usr/bin/env python3
"""Mission report aggregator — stdlib only, pure aggregation.

Reads `.claude/metrics.jsonl` and emits a concise markdown mission
report. Two public entry points:

    build_report(cwd)         → str (rendered markdown)
    write_report(cwd)         → Path (persisted artifact)

Ralph mode (detected by `.ralph/` presence) writes to
`.ralph/mission-report-{ts}.md`. Non-Ralph writes to
`.claude/mission-report-{ts}.md`. A `mission_report_generated`
telemetry event is appended to `.claude/metrics.jsonl`.

No network, no external deps, no state mutations beyond the single
write + telemetry line. Safe to invoke from hooks or by hand.
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path


METRICS_REL = Path(".claude") / "metrics.jsonl"


def _events_from_metrics(cwd) -> list[dict]:
    """Read metrics.jsonl, skipping malformed lines silently."""
    path = Path(cwd) / METRICS_REL
    if not path.exists():
        return []
    events: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except (json.JSONDecodeError, ValueError):
            continue
    return events


def _aggregate(events: list[dict]) -> dict:
    """Collapse event stream into counters the report needs."""
    completed = [e for e in events if e.get("event") == "task_completed"]
    failed = [e for e in events if e.get("event") == "task_failed"]
    queued = [e for e in events if e.get("event") == "test_run_queued"]
    bypassed = [e for e in events if e.get("event") == "scenarios_bypassed"]
    dogfood = [e for e in events if e.get("event") == "milestone_dogfood_needed"]

    rung_counts: Counter = Counter(
        str(e.get("fast_path_rung", "?")) for e in queued
    )
    fail_categories: Counter = Counter(
        str(e.get("category", "?")) for e in failed
    )
    forced_full_reasons: Counter = Counter(
        str(e.get("forced_full_reason", "")) for e in queued
        if e.get("forced_full_reason")
    )
    teammates_completed: Counter = Counter(
        str(e.get("teammate", "unknown")) for e in completed
    )
    scenarios_gated_count = sum(
        1 for e in completed if e.get("scenarios_gated")
    )

    return {
        "total_events": len(events),
        "tasks_completed": len(completed),
        "tasks_failed": len(failed),
        "scenarios_gated": scenarios_gated_count,
        "scenarios_bypassed": len(bypassed),
        "dogfood_signals": len(dogfood),
        "test_runs_queued": len(queued),
        "rung_counts": dict(rung_counts),
        "fail_categories": dict(fail_categories),
        "forced_full_reasons": dict(forced_full_reasons),
        "teammates_completed": dict(teammates_completed),
    }


def _render_empty(now_iso: str) -> str:
    return (
        f"# Mission report · {now_iso}\n\n"
        f"No events recorded yet — no mission data to report.\n\n"
        f"This file is generated from `.claude/metrics.jsonl`. If you "
        f"expected events, check the hook logs.\n"
    )


def _render(agg: dict, now_iso: str) -> str:
    lines: list[str] = []
    lines.append(f"# Mission report · {now_iso}\n")

    # Convergence
    lines.append("## Convergence\n")
    lines.append(f"- Tasks completed: {agg['tasks_completed']}")
    lines.append(f"- Tasks failed: {agg['tasks_failed']}")
    if agg["teammates_completed"]:
        per_mate = ", ".join(
            f"{n}: {c}" for n, c in sorted(agg["teammates_completed"].items())
        )
        lines.append(f"- Completions per teammate: {per_mate}")
    lines.append(f"- Scenarios-gated completions: {agg['scenarios_gated']}")
    if agg["scenarios_bypassed"]:
        lines.append(
            f"- Scenarios bypass events (_SDD_DISABLE_SCENARIOS=1): "
            f"{agg['scenarios_bypassed']}"
        )
    lines.append("")

    # Cascade efficiency
    lines.append("## Cascade efficiency (Phase 8)\n")
    if agg["test_runs_queued"]:
        total = agg["test_runs_queued"]
        for rung in ("1a", "1b", "2", "3"):
            count = agg["rung_counts"].get(rung, 0)
            pct = (100.0 * count / total) if total else 0.0
            lines.append(f"- Rung {rung}: {count} ({pct:.0f}%)")
        if agg["forced_full_reasons"]:
            reasons = ", ".join(
                f"{r}: {c}" for r, c in sorted(agg["forced_full_reasons"].items())
            )
            lines.append(f"- Forced-full reasons: {reasons}")
    else:
        lines.append("- No cascade events recorded (per-edit telemetry empty).")
    lines.append("")

    # Friction
    lines.append("## Friction\n")
    if agg["fail_categories"]:
        for cat, count in sorted(
            agg["fail_categories"].items(), key=lambda kv: -kv[1]
        ):
            lines.append(f"- {cat}: {count} failures")
    else:
        lines.append("- No task failures recorded.")
    lines.append("")

    # Follow-ups
    if agg["dogfood_signals"]:
        lines.append("## Follow-ups\n")
        lines.append(
            f"- `/dogfood` invocation suggested for this web project "
            f"({agg['dogfood_signals']} signal(s) emitted at TaskCompleted). "
            f"Milestone code gates passed but UI-level validation was not "
            f"automatically executed."
        )
        lines.append("")

    # Evidence
    lines.append("## Evidence\n")
    lines.append(f"- Total events aggregated: {agg['total_events']}")
    lines.append(f"- Source: `.claude/metrics.jsonl`")
    lines.append("")

    return "\n".join(lines) + "\n"


def build_report(cwd) -> str:
    """Pure function: cwd → rendered markdown. No side effects."""
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    events = _events_from_metrics(cwd)
    if not events:
        return _render_empty(now_iso)
    return _render(_aggregate(events), now_iso)


def _output_dir(cwd) -> Path:
    """Ralph mode → .ralph/, else → .claude/."""
    ralph = Path(cwd) / ".ralph"
    return ralph if ralph.is_dir() else Path(cwd) / ".claude"


def _emit_generated_telemetry(cwd, path: Path) -> None:
    """Append `mission_report_generated` to metrics.jsonl."""
    metrics_path = Path(cwd) / METRICS_REL
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "event": "mission_report_generated",
        "path": str(path),
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    try:
        with open(metrics_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except OSError:
        pass  # telemetry is best-effort


def write_report(cwd) -> Path:
    """Render and persist. Returns the path written.

    Filename includes a second-precision timestamp so concurrent
    writes don't clobber. Parent dir created if missing.
    """
    out_dir = _output_dir(cwd)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    out_path = out_dir / f"mission-report-{ts}.md"
    out_path.write_text(build_report(cwd), encoding="utf-8")
    _emit_generated_telemetry(cwd, out_path)
    return out_path


def main() -> int:
    cwd = sys.argv[1] if len(sys.argv) > 1 else "."
    path = write_report(cwd)
    print(str(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
