# Configuration Guide Reference

## Overview

This reference defines ralph configuration options in `.ralph/config.sh`. Configuration controls quality gates and safety thresholds for Agent Teams execution.

---

## Backpressure Gates

**Constraints:**
- Gates are auto-derived from Technology Stack in `detailed-design.md` during Step 7 (Configure Execution)
- You MUST pass all gates before commit because partial passes indicate incomplete work
- You SHOULD leave unused gates empty because non-existent commands cause failures

Examples by stack:

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

**Coverage Enforcement:**

```bash
GATE_COVERAGE=""          # Command that outputs coverage data (empty = disabled)
MIN_TEST_COVERAGE=90      # Default: 90% (0-100, coverage below this blocks COMPLETE)
```

When `MIN_TEST_COVERAGE` > 0 **and** `GATE_COVERAGE` is set, the `task-completed.py` hook runs the coverage command, parses its output for a percentage, and blocks completion if coverage is below the threshold (exit 2).

| Option | Default | Description |
|--------|---------|-------------|
| `GATE_COVERAGE` | `""` | Command that outputs coverage data. The hook parses its output for a percentage and compares against `MIN_TEST_COVERAGE`. Empty string disables coverage enforcement |
| `MIN_TEST_COVERAGE` | `90` | Minimum test coverage percentage (0-100). Requires `GATE_COVERAGE` to be set for enforcement. Coverage below this blocks COMPLETE |

**Stack examples for `GATE_COVERAGE`:**

```bash
# JavaScript/TypeScript (Vitest)
GATE_COVERAGE="npx vitest run --coverage"

# Python (pytest-cov)
GATE_COVERAGE="pytest --cov --cov-report=term"

# Go
GATE_COVERAGE="go test -cover ./..."
```

---

## Agent Teams Options

**Constraints:**
- You SHOULD set MAX_TEAMMATES based on task parallelism because too many teammates contend for resources
- You MUST NOT set MAX_TEAMMATES above 3 because more than 3 concurrent teammates degrades coordination quality

```bash
MODEL="opus"                      # Model for teammates (opus recommended)
MAX_TEAMMATES=2                   # Maximum concurrent teammates (hard cap: 3)
```

| Option | Default | Description |
|--------|---------|-------------|
| `MODEL` | `opus` | Model used for teammates |
| `MAX_TEAMMATES` | `2` | Max concurrent teammates (hard cap: 3) |

---

## Scenario-Strategy and Quality Gates

The `Scenario-Strategy` field in `.code-task.md` files controls whether GATE_TEST runs for a given task:

| Scenario-Strategy | Effect on Gates |
|---|---|
| `required` (default) | All gates run. SDD mandatory. |
| `not-applicable` | GATE_TEST skipped. GATE_TYPECHECK, GATE_LINT, GATE_BUILD still run. |

All tasks run full SDD + all gates. Tasks with `Scenario-Strategy: not-applicable` skip GATE_TEST but other gates still run.

The `sop-task-generator` classifies tasks automatically. When in doubt, it defaults to `required` (safe default). The `task-completed.py` hook reads the field at gate execution time.

---

## Safety Settings (Circuit Breaker)

**Constraints:**
- You MUST NOT disable circuit breaker because it protects against runaway failures
- You MUST set reasonable thresholds because too low causes premature stops

```bash
MAX_CONSECUTIVE_FAILURES=3      # Circuit breaker threshold (per teammate)
```

The circuit breaker tracks failures **per teammate** in `.ralph/failures.json`. When a teammate hits MAX_CONSECUTIVE_FAILURES, the TeammateIdle hook allows it to idle (exit 0) instead of claiming more tasks.

---

## Memories (Guardrails.md)

**Constraints:**
- You SHOULD enable memories for complex tasks because guardrails.md captures patterns and prevents repeated mistakes
- You SHOULD NOT worry about guardrails.md size because growth is bounded by session scope (~1 entry per task)

```bash
MEMORIES_ENABLED=true    # Enable/disable memory system
```

| Option | Default | Description |
|--------|---------|-------------|
| `MEMORIES_ENABLED` | `true` | Enable/disable the guardrails.md memory system. When false, teammates skip writing learned patterns and error patterns |

> **Note:** MEMORIES_ENABLED is prompt-enforced (teammates read config.sh and honor it), not hook-enforced. No hook validates this setting.

> **MEMORIES_BUDGET (deprecated):** Never enforced — see [memories-system.md](memories-system.md).

---

## Exit Codes

**Constraints:**
- You MUST understand exit codes because they guide recovery actions
- You MUST check logs after non-zero exit because root cause needs identification

Exit codes from lifecycle hooks (task-completed.py, teammate-idle.py). Codes 1 and 130 are reserved for future orchestrator-level exits.

| Exit Code | Name | Trigger |
|-----------|------|---------|
| 0 | SUCCESS | All tasks completed, teammates idled |
| 1 | ERROR | Reserved — not currently produced by hooks |
| 2 | GATE_FAILURE | Quality gate or coverage gate failure |
| 130 | INTERRUPTED | Reserved — manual ABORT uses .ralph/ABORT file (exit 0) |

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
# Spawn new teammates to resume execution
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
- You SHOULD check if teammates were re-spawned because running teammates don't reload config
- You MUST source config.sh manually to test because this reveals parse errors

### Exit Codes Not Matching Expected

If execution exits unexpectedly:
- You SHOULD check `.ralph/failures.json` for circuit breaker state
- You SHOULD review `.ralph/metrics.json` for failure patterns
- You MUST check `.ralph/guardrails.md` for accumulated memories

---

*Version: 2.0.0 | Updated: 2026-02-15*
*Agent Teams configuration model*
