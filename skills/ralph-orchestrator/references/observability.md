# Observability Reference

## Overview

This reference defines monitoring and debugging capabilities during Agent Teams execution. Understanding observability is essential for tracking progress, diagnosing failures, and maintaining oversight of concurrent teammates.

---

## Primary Observability Channels

**Constraints:**
- You MUST use TaskList as the primary progress indicator because it reflects real-time task state
- You MUST check .ralph/metrics.json for aggregate data because it shows success/failure trends
- You SHOULD check .ralph/failures.json for circuit breaker state because it reveals at-risk teammates

| Channel | Purpose | Access |
|---------|---------|--------|
| `TaskList` | Real-time task progress (PENDING, IN_PROGRESS, COMPLETED, BLOCKED) | Lead tool call |
| `.ralph/metrics.json` | Aggregate success/failure counts | `Read(".ralph/metrics.json")` |
| `.ralph/failures.json` | Per-teammate failure tracking | `Read(".ralph/failures.json")` |
| `.ralph/guardrails.md` | Accumulated error lessons | `Read(".ralph/guardrails.md")` |
| Cockpit windows | Live service output (dev server, tests, logs) | tmux capture-pane |

---

## Monitoring During Execution (Phase 2)

**Constraints:**
- You MUST remain in MONITOR role because teammates handle implementation
- You MUST NOT use Write/Edit because state is owned by teammates and hooks
- You SHOULD check progress periodically because early detection prevents wasted work

### Lead Monitoring Pattern

```
1. TaskList → check task states
2. Read(".ralph/metrics.json") → aggregate progress
3. Read(".ralph/failures.json") → check for struggling teammates
4. Read(".ralph/guardrails.md") → review accumulated lessons
5. If teammate struggling → SendMessage with guidance
6. Repeat every few minutes
```

### What to Monitor

| Signal | Healthy | Concerning | Action |
|--------|---------|------------|--------|
| Tasks completing | Steady progress | No completions for extended time | Check failures.json, SendMessage |
| Failure count | 0-1 consecutive | 2+ consecutive per teammate | Review gate output, add Sign |
| .ralph/guardrails.md growth | Gradual, useful Signs | Rapid growth, repetitive Signs | Task may be too complex — consider splitting |
| Blocked tasks | Rare | Multiple tasks blocked | Review blockers.md, may need user input |

---

## Cockpit Monitoring

Teammates and the lead can observe cockpit windows via tmux:

```bash
# Read dev server output
tmux capture-pane -p -t ralph:services.0

# Read test watcher output
tmux capture-pane -p -t ralph:quality.0

# Read log output
tmux capture-pane -p -t ralph:monitor.0
```

### Useful Patterns

**Check if dev server is healthy:**
```bash
tmux capture-pane -p -t ralph:services.0 | tail -5
# Look for: "ready", "listening on", "compiled successfully"
```

**Check test watcher for failures:**
```bash
tmux capture-pane -p -t ralph:quality.0 | grep -i "fail\|error"
```

---

## Metrics File Format

**Constraints:**
- You SHOULD calculate success rate because this indicates execution health
- You SHOULD use per_teammate data for rotation decisions because it tracks individual performance

```json
{
  "total_tasks": 10,
  "successful_tasks": 8,
  "failed_tasks": 2,
  "last_updated": "2026-02-10T14:30:00Z",
  "per_teammate": {
    "teammate-1": {
      "completed": 5,
      "failed": 1
    },
    "teammate-2": {
      "completed": 3,
      "failed": 1
    }
  }
}
```

### Key Derived Metrics

| Metric | Calculation | Healthy Threshold |
|--------|-------------|-------------------|
| Success rate | successful_tasks / total_tasks | > 80% |
| Completion progress | successful_tasks / total_tasks | Increasing |

---

## Failures File Format

```json
{
  "teammate-1": 2,
  "teammate-2": 0
}
```

Each key is a teammate name, and the value is the consecutive failure count (integer). Reset to 0 on success.

**Circuit breaker**: When consecutive failures >= MAX_CONSECUTIVE_FAILURES (default 3), TeammateIdle hook exits 0, stopping that teammate.

---

## Debugging Failed Tasks

**Constraints:**
- You MUST check failures.json first because this shows which teammate and which gate failed
- You MUST look for patterns in .ralph/guardrails.md because repeated errors indicate systematic issues
- You MUST NOT restart execution without diagnosing because same failures will repeat

### Diagnosis Steps

1. `TaskList` — identify which tasks failed or are stuck
2. `Read(".ralph/failures.json")` — which teammate is failing, what gate
3. `Read(".ralph/guardrails.md")` — are there relevant Signs already?
4. `SendMessage` to struggling teammate — ask for status or provide guidance
5. If systematic: add Sign to .ralph/guardrails.md, all teammates benefit

### Common Failure Patterns

| Pattern | Symptom | Resolution |
|---------|---------|------------|
| Gate misconfiguration | All teammates fail same gate | Fix gate command in config.sh, relaunch |
| Missing dependency | Build/test gates fail immediately | Install dependency, add to .ralph/agents.md |
| Task too complex | Teammate cycles without completing | Split task into subtasks |
| Flaky tests | Intermittent gate failures | Fix test, add Sign about flaky test |

---

## Context Philosophy

Agent Teams teammates have persistent context (compacted by Claude Code). Unlike iteration-based models, there is no context truncation between tasks. Observability focuses on **task outcomes** (metrics.json) and **accumulated lessons** (guardrails.md), not context percentages.

**Track**: Task completion rate, gate pass rate, failure patterns.
**Ignore**: Context size, token counts (managed internally by Claude Code).

---

## Troubleshooting

### Metrics Not Updating

If .ralph/metrics.json stops updating:
- You SHOULD check if TaskCompleted hook is registered in hooks.json
- You SHOULD check if teammates are completing tasks (TaskList)
- You MUST verify hooks directory is accessible

### High Failure Rate

If success rate drops below 80%:
- You SHOULD review .ralph/guardrails.md for common issues
- You SHOULD check task sizing (may be too large)
- You SHOULD verify gate commands work manually
- You MAY reduce MAX_TEAMMATES to reduce contention

### Cockpit Windows Empty

If cockpit windows show no output:
- You SHOULD verify COCKPIT_* variables in config.sh
- You SHOULD check if tmux session "ralph" exists: `tmux ls`
- You MUST verify commands work when run manually

---

*Version: 2.0.0 | Updated: 2026-02-10*
*Agent Teams observability*
