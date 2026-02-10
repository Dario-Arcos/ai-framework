# Configuration Guide Reference

## Overview

This reference defines ralph configuration options in `.ralph/config.sh`. Configuration controls quality gates, safety thresholds, and cockpit services for Agent Teams execution.

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
| `production` | SDD mandatory, all gates must pass |
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

Gates execute in order: **test → typecheck → lint → build**. First failure stops the chain (TaskCompleted hook).

**Coverage Threshold:**

```bash
MIN_TEST_COVERAGE=""  # Default: empty (no coverage check)
```

| Option | Default | Description |
|--------|---------|-------------|
| `MIN_TEST_COVERAGE` | `""` | Minimum test coverage percentage. When set, test gate validates coverage meets this threshold. Empty = no coverage enforcement |

---

## Agent Teams Options

**Constraints:**
- You MUST configure cockpit services before launch because launch-build.sh reads config at startup
- You SHOULD set MAX_TEAMMATES based on task parallelism because too many teammates contend for resources

```bash
MODEL="opus"                      # Model for teammates (opus recommended)
MAX_TEAMMATES=3                   # Maximum concurrent teammates
COCKPIT_DEV_SERVER="npm run dev"  # Dev server command (tmux "services" window)
COCKPIT_TEST_WATCHER="npm run test:watch"  # Test watcher (tmux "quality" window)
COCKPIT_LOGS="tail -f logs/*.log" # Log tailing (tmux "monitor" window)
COCKPIT_DB=""                     # Database command (tmux "services" window, pane 1)
```

| Option | Default | Description |
|--------|---------|-------------|
| `MODEL` | `opus` | Model used for teammates |
| `MAX_TEAMMATES` | `3` | Max concurrent teammates |
| `COCKPIT_DEV_SERVER` | `""` | Command for dev server window |
| `COCKPIT_TEST_WATCHER` | `""` | Command for test watcher window |
| `COCKPIT_LOGS` | `""` | Command for log monitoring window |
| `COCKPIT_DB` | `""` | Command for database service |

---

## Safety Settings (Circuit Breakers)

**Constraints:**
- You MUST NOT disable circuit breaker because it protects against runaway failures
- You MUST set reasonable thresholds because too low causes premature stops
- You SHOULD tune based on task complexity because complex tasks may need more attempts

```bash
CONFESSION_MIN_CONFIDENCE=80    # 0-100, tasks below this are NOT complete
MAX_CONSECUTIVE_FAILURES=3      # Circuit breaker threshold (per teammate)
MAX_TASK_ATTEMPTS=3             # Reject task after N failed attempts
MAX_RUNTIME=0                   # Max seconds (0 = unlimited)
```

The circuit breaker tracks failures **per teammate** in `.ralph/failures.json`. When a teammate hits MAX_CONSECUTIVE_FAILURES, the TeammateIdle hook allows it to idle (exit 0) instead of claiming more tasks.

---

## Memories (Guardrails.md)

**Constraints:**
- You SHOULD enable memories for complex tasks because guardrails.md captures patterns and prevents repeated mistakes
- You SHOULD set MEMORIES_BUDGET based on task duration because long-running sessions accumulate more entries

```bash
MEMORIES_ENABLED=true    # Enable/disable memory system
MEMORIES_BUDGET=50       # Max entries before pruning oldest
```

| Option | Default | Description |
|--------|---------|-------------|
| `MEMORIES_ENABLED` | `true` | Enable/disable the guardrails.md memory system. When false, teammates skip writing learned patterns and error signs |
| `MEMORIES_BUDGET` | `50` | Maximum number of entries in guardrails.md before oldest entries are pruned. Prevents unbounded growth in long-running sessions |

---

## Exit Codes

**Constraints:**
- You MUST understand exit codes because they guide recovery actions
- You MUST check logs after non-zero exit because root cause needs identification

| Exit Code | Name | Trigger |
|-----------|------|---------|
| 0 | SUCCESS | All tasks completed, teammates idled |
| 1 | ERROR | Validation failure, missing files, config error |
| 2 | CIRCUIT_BREAKER | Per-teammate consecutive failures hit threshold |
| 4 | MAX_RUNTIME | Runtime limit exceeded |
| 130 | INTERRUPTED | User interrupt (Ctrl+C) or manual ABORT |

**Manual abort**: Create `.ralph/ABORT` file → all teammates idle on next TeammateIdle check.

---

## Recovery Commands

**Constraints:**
- You MUST stop execution before making changes because concurrent edits cause conflicts
- You SHOULD use git reset only when necessary because this discards work

If Ralph goes off-track:

```bash
touch .ralph/ABORT                      # Graceful stop — teammates idle on next check
# Wait for teammates to idle, then:
rm .ralph/ABORT                         # Clear abort flag
git reset --hard HEAD~N                 # Revert N commits if needed
rm .ralph/failures.json                 # Reset circuit breakers
# Re-launch cockpit
bash .ralph/launch-build.sh
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
- You SHOULD check if cockpit was relaunched because running sessions don't reload config
- You MUST source config.sh manually to test because this reveals parse errors

### Exit Codes Not Matching Expected

If execution exits unexpectedly:
- You SHOULD check `.ralph/failures.json` for circuit breaker state
- You SHOULD review `.ralph/metrics.json` for failure patterns
- You MUST check `guardrails.md` for accumulated error Signs

---

*Version: 2.0.0 | Updated: 2026-02-10*
*Agent Teams configuration model*
