# Configuration Guide

Ralph uses `.ralph/config.sh` for project-specific settings.

## Quality Levels

```bash
QUALITY_LEVEL="production"  # Default
```

| Level | Behavior |
|-------|----------|
| `prototype` | Skip all gates, commit freely |
| `production` | TDD mandatory, all gates must pass |
| `library` | Full coverage + docs + edge cases |

## Backpressure Gates

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

## Checkpoint Configuration

```bash
CHECKPOINT_MODE="none"        # none|iterations|milestones
CHECKPOINT_INTERVAL=5         # Pause every N iterations (if mode=iterations)
CHECKPOINT_ON_MODULE=true     # Pause when module completes (if mode=milestones)
```

## Safety Settings (Circuit Breakers)

```bash
CONFESSION_MIN_CONFIDENCE=80    # 0-100, tasks below this are NOT complete
MAX_CONSECUTIVE_FAILURES=3      # Circuit breaker threshold
MAX_TASK_ATTEMPTS=3             # Exit if same task fails N times
MAX_RUNTIME=0                   # Max seconds (0 = unlimited)
CONTEXT_LIMIT=200000            # Token limit for context health
```

## AFK Mode Configuration

For unattended execution:

```bash
AFK_MODE=true                   # Enable AFK mode
AFK_NOTIFICATION="slack"        # slack|email|none
AFK_WEBHOOK_URL=""              # Slack webhook for notifications
```

## Execution Modes Summary

| Mode | Description | Use When |
|------|-------------|----------|
| 100% AFK | No interruptions | Overnight runs, high confidence |
| Checkpoint (iterations) | Pause every N | Learning the system, want oversight |
| Checkpoint (milestones) | Pause at modules | Complex features, natural review points |

## Termination & Exit Codes

| Exit Code | Name | Trigger |
|-----------|------|---------|
| 0 | SUCCESS | `<promise>COMPLETE</promise>` confirmed twice |
| 1 | ERROR | Validation failure, missing files |
| 2 | CIRCUIT_BREAKER | 3 consecutive Claude failures |
| 3 | MAX_ITERATIONS | User-defined iteration limit reached |
| 4 | MAX_RUNTIME | Runtime limit exceeded |
| 5 | CONTEXT_EXHAUSTED | Context usage > 80% of limit |
| 6 | LOOP_THRASHING | Oscillating task pattern (A-B-A-B) |
| 7 | TASKS_ABANDONED | Same task failed 3+ times |
| 8 | CHECKPOINT_PAUSE | Checkpoint reached, waiting for resume |
| 130 | INTERRUPTED | Ctrl+C (SIGINT) |

## Recovery Commands

If Ralph goes off-track, use from terminal (not monitoring session):

```bash
Ctrl+C                              # Stop the loop
git reset --hard HEAD~N             # Revert N commits
# Re-run planning phase in interactive session
./loop.sh specs/{goal}/             # Resume building
```
