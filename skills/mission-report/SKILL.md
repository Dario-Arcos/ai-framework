---
name: mission-report
description: "Use when a Ralph mission ends or at any time during/after autonomous work — produces a concise markdown summary of what the factory did (convergence, cascade efficiency, friction) so the dev can trust the autonomous run without reading raw logs."
---

# Mission Report

## Overview

A developer who runs Ralph overnight must wake up to an artifact that makes the factory trustable — not a 30-commit git log and a raw jsonl. This skill reads `.claude/metrics.jsonl` and emits ONE markdown file per invocation summarizing convergence, cascade efficiency, and friction.

Auto-triggered by `teammate-idle.py` when the Ralph circuit breaker opens or the ABORT sentinel fires. Dev may also invoke it manually at any time.

## When to Use

- Wake-up check after an autonomous Ralph mission (auto-triggered, but rerun any time)
- End-of-day summary on a long interactive session
- Debugging: a mission failed and you need the shape of what happened
- Before a release: aggregate evidence across the work that landed

## Output

One file at:
- Ralph mode: `.ralph/mission-report-{YYYYMMDD-HHMMSS}.md`
- Non-Ralph mode: `.claude/mission-report-{YYYYMMDD-HHMMSS}.md`

Shape:
```
# Mission report · {timestamp}

## Convergence
- Tasks completed: N
- Tasks failed: M
- Completions per teammate: impl-a: 3, impl-b: 2, ...
- Scenarios-gated completions: K

## Cascade efficiency (Phase 8)
- Rung 1a: N (X%)
- Rung 1b: N (X%)
- Rung 2: N (X%)
- Rung 3: N (X%)
- Forced-full reasons: lockfile: 2, config: 1

## Friction
- GATE: N failures
- COVERAGE: M failures
- POLICY: K failures

## Follow-ups
- /dogfood invocation suggested for this web project
  (UI validation was not automatically executed at milestone)

## Evidence
- Total events aggregated: N
- Source: .claude/metrics.jsonl
```

## Invocation

Direct script:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/mission-report/scripts/aggregate.py" "$PWD"
```

The script prints the written file path on stdout.

## How it works

1. Read `.claude/metrics.jsonl` line by line; skip malformed JSON silently.
2. Aggregate events into counters: task_completed, task_failed,
   test_run_queued (+ fast_path_rung), milestone_dogfood_needed.
   The aggregator script under `scripts/aggregate.py` still reads
   `scenarios_bypassed` for backward-compatibility with historical
   metrics.jsonl logs; no new sessions emit it (the env-var bypass
   was removed in amend-protocol Step 4).
3. Render markdown with fixed sections. Empty metrics → "no events"
   note (does not crash).
4. Write to the mode-appropriate path.
5. Append a `mission_report_generated` event to metrics.jsonl so
   downstream consumers can find generated reports.

## Integration

- **teammate-idle**: auto-invokes this skill's script when the circuit
  breaker opens or the ABORT sentinel fires.
- **verification-before-completion**: a mission report is not itself a
  verification artifact — it summarizes past events. Do not substitute
  it for fresh verification evidence.

## Artifact Handoff

| Receives | Produces |
|---|---|
| `.claude/metrics.jsonl` from hook telemetry | Markdown report at mode-appropriate path + `mission_report_generated` telemetry event |

## Non-goals

- NOT streaming telemetry to an external service
- NOT building a web dashboard
- NOT replacing `verification-before-completion`
- NOT producing per-task reports (only per-mission / on-demand)
