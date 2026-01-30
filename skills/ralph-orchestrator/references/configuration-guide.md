# Configuration Guide Reference

## Overview

This reference defines ralph configuration options in `.ralph/config.sh`. Understanding configuration is essential for customizing loop behavior to match project requirements.

---

## Quality Levels

**Constraints:**
- You MUST set quality level before execution because it determines gate behavior
- You MUST NOT use prototype in production code because shortcuts accumulate debt
- You SHOULD use library level for reusable code because polish matters for shared code

```bash
QUALITY_LEVEL="production"  # Default
```

| Level | Behavior |
|-------|----------|
| `prototype` | Skip all gates, commit freely |
| `production` | TDD mandatory, all gates must pass |
| `library` | Full coverage + docs + edge cases |

---

## Backpressure Gates

**Constraints:**
- You MUST configure gates for your stack because defaults may not match your tooling
- You MUST pass all gates before commit because partial passes indicate incomplete work
- You SHOULD leave unused gates empty because non-existent commands cause failures

Customize for your stack:

```bash
# JavaScript/TypeScript
GATE_TEST="npm test"
GATE_TYPECHECK="npm run typecheck"
GATE_LINT="npm run lint"
GATE_BUILD="npm run build"

# Python
GATE_TEST="pytest"
GATE_TYPECHECK="mypy src/"
GATE_LINT="ruff check ."
GATE_BUILD=""

# Go
GATE_TEST="go test ./..."
GATE_TYPECHECK=""  # Built into compiler
GATE_LINT="golangci-lint run"
GATE_BUILD="go build ./..."
```

---

## Checkpoint Configuration

**Constraints:**
- You MUST configure checkpoint mode before execution because mid-run changes cause inconsistency
- You MUST resume with same command after checkpoint because state persists
- You SHOULD use milestones for multi-module features because natural breakpoints aid review

```bash
CHECKPOINT_MODE="none"        # none|iterations (milestones not implemented)
CHECKPOINT_INTERVAL=5         # Pause every N iterations (if mode=iterations)
# CHECKPOINT_ON_MODULE=true   # NOT IMPLEMENTED - milestones mode planned for future
```

---

## Safety Settings (Circuit Breakers)

**Constraints:**
- You MUST NOT disable circuit breaker because it protects against runaway failures
- You MUST set reasonable thresholds because too low causes premature stops
- You SHOULD tune based on task complexity because complex tasks may need more attempts

```bash
CONFESSION_MIN_CONFIDENCE=80    # 0-100, tasks below this are NOT complete
MAX_CONSECUTIVE_FAILURES=3      # Circuit breaker threshold
MAX_TASK_ATTEMPTS=3             # Exit if same task fails N times
MAX_RUNTIME=0                   # Max seconds (0 = unlimited)
```

---

## AFK Mode Configuration

> **NOT IMPLEMENTED**: The following options are documented but not yet implemented in loop.sh.
> Autonomous execution works by default - these notification options are planned for future versions.

```bash
# NOT IMPLEMENTED - Planned for future release
AFK_MODE=true                   # Enable AFK mode (not implemented)
AFK_NOTIFICATION="slack"        # slack|email|none (not implemented)
AFK_WEBHOOK_URL=""              # Slack webhook for notifications (not implemented)
```

---

## Execution Modes Summary

**Constraints:**
- You SHOULD use frequent checkpoints for first-time users because learning requires observation
- You MUST use checkpoint mode for risky tasks because human review catches critical errors
- You MAY use 100% AFK when confident in quality gates because fresh context improves throughput

| Mode | Description | Use When |
|------|-------------|----------|
| Autonomous | No interruptions | Overnight runs, high confidence |
| Checkpoint (iterations) | Pause every N | Learning the system, want oversight |
| Checkpoint (milestones) | Pause at modules | *NOT IMPLEMENTED* |

---

## Termination & Exit Codes

**Constraints:**
- You MUST check errors.log after non-zero exit because root cause needs identification
- You MUST fix underlying issue before restart because same failures will repeat
- You SHOULD understand all exit codes because this guides recovery action

| Exit Code | Name | Trigger |
|-----------|------|---------|
| 0 | SUCCESS | `<promise>COMPLETE</promise>` confirmed twice |
| 1 | ERROR | Validation failure, missing files |
| 2 | CIRCUIT_BREAKER | 3 consecutive Claude failures |
| 3 | MAX_ITERATIONS | User-defined iteration limit reached |
| 4 | MAX_RUNTIME | Runtime limit exceeded |
| 6 | LOOP_THRASHING | Oscillating task pattern (A-B-A-B) |
| 7 | TASKS_ABANDONED | Same task failed 3+ times |
| 8 | CHECKPOINT_PAUSE | Checkpoint reached, waiting for resume |
| 130 | INTERRUPTED | Ctrl+C (SIGINT) |

---

## Recovery Commands

**Constraints:**
- You MUST stop the loop before making changes because concurrent edits cause conflicts
- You MUST re-run planning phase in interactive session because this restores context
- You SHOULD use git reset only when necessary because this discards work

If Ralph goes off-track, use from terminal (not monitoring session):

```bash
Ctrl+C                              # Stop the loop
git reset --hard HEAD~N             # Revert N commits
# Re-run planning phase in interactive session
./loop.sh specs/{goal}/             # Resume building
```

---

## Troubleshooting

### Gates Failing Unexpectedly

If quality gates fail when they shouldn't:
- You SHOULD verify gate commands are correct because typos cause failures
- You SHOULD check if dependencies are installed because missing packages fail commands
- You MUST run gate commands manually to diagnose because this reveals specific errors

### Configuration Not Applied

If config changes don't take effect:
- You SHOULD verify config.sh syntax because shell syntax errors prevent loading
- You SHOULD check if loop was restarted because running loops don't reload config
- You MUST source config.sh manually to test because this reveals parse errors

### Exit Codes Not Matching Expected

If loop exits with unexpected code:
- You SHOULD check status.json for detailed state because this reveals true cause
- You SHOULD review logs/iteration.log for failure details because this shows progression
- You MUST map exit code to table above because this guides recovery action

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
