# Observability Reference

Ralph generates structured logs for monitoring and debugging.

## Output Artifacts

| Artifact | Purpose |
|----------|---------|
| `logs/iteration.log` | Timestamped iteration events |
| `logs/metrics.json` | Success rate, durations, totals |
| `status.json` | Current loop state |
| `errors.log` | Failed iteration details |

---

## Utilities

```bash
./status.sh           # View current status & metrics
./tail-logs.sh        # Real-time log following
```

---

## Interactive Monitoring

Use an active Claude Code session as observer:

- Cost: ~$0.48 per 2 hours
- Won't compact in sessions <4h
- No interference with bash loops (independent processes)

### Monitoring Pattern (Specs-Based Execution)

Since ralph-loop now only executes (planning is separate), monitoring focuses on task progress:

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

1. Check `errors.log` for failure details
2. Look for patterns in Signs (guardrails.md)
3. Review `status.json` for circuit breaker state
