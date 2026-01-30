# Observability Reference

## Overview

This reference defines the structured logging and monitoring capabilities of Ralph. Understanding observability is essential for debugging loops and tracking execution progress.

---

## Output Artifacts

**Constraints:**
- You MUST monitor status.json for loop state because this is the source of truth
- You MUST check iteration.log for debugging because detailed events are recorded there
- You SHOULD review metrics.json for performance analysis because aggregated data reveals patterns

| Artifact | Purpose |
|----------|---------|
| `logs/iteration.log` | Timestamped iteration events |
| `logs/metrics.json` | Success rate, durations, totals |
| `status.json` | Current loop state |
| `errors.log` | Failed iteration details |

---

## Utilities

**Constraints:**
- You MUST use status.sh for quick state checks because it formats output clearly
- You SHOULD use tail-logs.sh for real-time monitoring because it streams events

```bash
./status.sh           # View current status & metrics
./tail-logs.sh        # Real-time log following
```

---

## Interactive Monitoring

**Constraints:**
- You MUST use separate Claude session for monitoring because implementation sessions have polluted context
- You MUST NOT interfere with bash loops because monitoring and execution are independent
- You SHOULD keep monitoring sessions under 4 hours because compaction loses context

Use an active Claude Code session as observer:

- Cost: ~$0.48 per 2 hours
- Won't compact in sessions <4h
- No interference with bash loops (independent processes)

### Monitoring Pattern (Specs-Based Execution)

Since ralph-orchestrator now only executes (planning is separate), monitoring focuses on task progress:

```
1. result = Bash("./loop.sh specs/{goal}/", run_in_background=true)
2. task_id = result.task_id
3. specs_path = "specs/{goal}/"

4. REPEAT every 30-90 seconds:
   a. TaskOutput(task_id, block=false, timeout=interval*1000)
   b. Read("status.json")
   c. Read(specs_path + "implementation/plan.md")  # Check task completion
   d. display_dashboard()
   e. interval = clamp(last_duration/3, 30, 90)

5. When status != "running":
   TaskOutput(task_id, block=true)  # Get final output
```

### Key Monitoring Points

| Artifact | Purpose | Update Frequency |
|----------|---------|------------------|
| `status.json` | Loop state, iteration count | Real-time |
| `specs/{goal}/implementation/plan.md` | Task checklist progress | Per iteration |
| `logs/iteration.log` | Iteration events | Per iteration |
| `logs/metrics.json` | Success rates, durations | Continuous |

### Dashboard Display

```
═══════════════════════════════════════════════
RALPH LOOP MONITOR
═══════════════════════════════════════════════
Status:     running
Iteration:  12
Specs:      specs/user-auth-system/
Branch:     feature-user-auth
Quality:    production
═══════════════════════════════════════════════
Tasks:      ✓ 8 complete | ⧗ 1 in progress | ○ 3 pending
Progress:   67% (8/12 tasks)
Duration:   2h 15m
Success:    92% (11/12 iterations)
═══════════════════════════════════════════════
Current:    Implementing JWT token validation
Last:       Tests passed, types checked, committed
Next:       Token refresh mechanism
═══════════════════════════════════════════════
```

---

## Monitoring Task Progress

**Constraints:**
- You MUST use plan.md as source of truth for progress because workers update it
- You MUST NOT modify plan.md during monitoring because workers own the file
- You SHOULD track completion percentage because this indicates remaining work

The implementation plan (`specs/{goal}/implementation/plan.md`) is the source of truth for progress tracking.

### Task Plan Format

```markdown
# Implementation Plan

## Tasks

- [x] Setup authentication routes
  Files: src/routes/auth.ts, tests/auth.test.ts

- [x] Implement JWT token generation
  Files: src/utils/jwt.ts, tests/jwt.test.ts

- [ ] Add token validation middleware
  Files: src/middleware/auth.ts, tests/middleware.test.ts

- [ ] Implement token refresh endpoint
  Files: src/routes/refresh.ts, tests/refresh.test.ts
```

### Progress Tracking

Workers mark tasks as complete by:
1. Changing `[ ]` to `[x]`
2. Adding completion notes if needed
3. Committing the updated plan.md

### Monitoring Script Example

```bash
#!/bin/bash
# Quick progress check
PLAN="specs/my-feature/implementation/plan.md"

total=$(grep -c "^- \[" "$PLAN")
done=$(grep -c "^- \[x\]" "$PLAN")
pct=$((done * 100 / total))

echo "Progress: $done/$total tasks ($pct%)"
grep "^- \[ \]" "$PLAN" | head -1 | sed 's/- \[ \] /Next: /'
```

---

## Status File Format

**Constraints:**
- You MUST check status field for loop state because this determines next actions
- You MUST check consecutive_failures for circuit breaker because approaching threshold needs attention
- You SHOULD check timestamp for stale status because stuck loops don't update

```json
{
  "current_iteration": 10,
  "consecutive_failures": 0,
  "status": "running",
  "mode": "build",
  "branch": "feature-x",
  "timestamp": "2026-01-25T17:31:41Z"
}
```

**Status values:** `running`, `complete`, `max_iterations`, `circuit_breaker`

---

## Metrics File Format

**Constraints:**
- You SHOULD calculate success rate because this indicates loop health
- You SHOULD track avg_duration because increasing duration indicates complexity growth
- You MAY use metrics for cost estimation because tokens correlate with cost

```json
{
  "total_iterations": 10,
  "successful": 9,
  "failed": 1,
  "total_duration_seconds": 1800,
  "avg_duration_seconds": 180
}
```

---

## Log Analysis

**Constraints:**
- You MUST review errors.log after circuit breaker because root cause needs identification
- You SHOULD search for patterns in failures because systematic issues have common causes
- You MAY use grep for quick analysis because structured logs enable filtering

```bash
# Count successful vs failed iterations
grep -c "SUCCESS" logs/iteration.log
grep -c "FAILED" logs/iteration.log

# Find slowest iteration
grep "Duration:" logs/iteration.log | sort -t: -k4 -rn | head -1

# Extract all task completions
grep "Task:" logs/iteration.log
```

---

## Debugging Failed Iterations

**Constraints:**
- You MUST check errors.log first because this contains failure details
- You MUST look for patterns in Signs because repeated errors indicate systematic issues
- You MUST NOT restart loop without diagnosing because same failures will repeat

1. Check `errors.log` for failure details
2. Look for patterns in Signs (guardrails.md)
3. Review `status.json` for circuit breaker state

---

## Context Philosophy

Ralph does NOT monitor context percentages. The INPUT-based approach (truncating files before iteration) ensures each iteration starts fresh without measuring output.

**Observability**: Track `num_turns` and `total_cost_usd` for session metrics, not context percentage.

---

## Troubleshooting

### Status File Not Updating

If status.json stops updating:
- You SHOULD check if loop process is running
- You SHOULD check for disk space issues
- You MUST NOT assume loop is healthy without updates

### Metrics Show High Failure Rate

If success rate drops below 80%:
- You SHOULD review recent Signs for common issues
- You SHOULD check task sizing (may be too large)
- You MUST consider returning to HITL mode for diagnosis

### Logs Missing Information

If logs lack expected detail:
- You SHOULD verify log level configuration
- You SHOULD check disk space for truncation
- You MUST ensure worker prompts include logging instructions

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
