# Backpressure Reference

## Overview

This reference defines the quality gates that reject incomplete work in Ralph. Backpressure ensures work meets quality standards before proceeding.

---

## Standard Gates

**Constraints:**
- You MUST pass all gates before commit because partial passes indicate incomplete work
- You MUST NOT skip gates in production/library mode because quality is mandatory
- You SHOULD configure gates for your stack because defaults may not match your tooling

```bash
npm test          # Tests must pass
npm run typecheck # Types must check
npm run lint      # Lint must pass
npm run build     # Build must succeed
```

**All gates must pass before commit. No exceptions.**

---

## Safety-Based Backpressure

Safety limits provide execution-level backpressure by stopping teammates when failures accumulate.

**Constraints:**
- You MUST configure safety limits before execution because defaults may not match your risk tolerance
- You MUST diagnose root cause before restarting after circuit breaker because same failures will repeat
- You SHOULD monitor .ralph/failures.json during execution for early warning signs

### Configuration

In `.ralph/config.sh`:

```bash
# Circuit breaker: stop teammate after N consecutive gate failures
MAX_CONSECUTIVE_FAILURES=3

# Task retry limit: max attempts per task before escalating
MAX_TASK_ATTEMPTS=3

# Runtime limit (0 = unlimited)
MAX_RUNTIME=0
```

### Safety Mechanisms

#### 1. Circuit Breaker (Consecutive Failures)

**Behavior:**
- Tracks consecutive gate failures per teammate in `.ralph/failures.json`
- When a teammate hits `MAX_CONSECUTIVE_FAILURES`, it goes idle (exit 0 via teammate-idle hook)
- Counter resets on any successful task completion
- Review `.ralph/failures.json` to diagnose the pattern

**Use when adjusting:**
- Lower (2) for high-risk tasks where early stopping matters
- Default (3) for production work
- Higher (5) for experimental/prototype work where some failures are expected

#### 2. Task Retry Limit (Per-Task Attempts)

**Behavior:**
- Each task can be attempted up to `MAX_TASK_ATTEMPTS` times
- After exhausting attempts, the task is escalated
- Prevents a single difficult task from blocking all progress

**Use when adjusting:**
- Lower (2) for tasks that should succeed on first or second try
- Default (3) for normal development
- Higher (5) for complex tasks where iteration is expected

---

## Backpressure Stack

**Constraints:**
- You MUST understand all backpressure levels because each serves different purpose
- You MUST NOT override circuit breaker without diagnosis because repeated failures indicate issues
- You SHOULD trust quality gates in production mode because they enforce standards

Ralph implements backpressure at multiple levels:

```mermaid
graph TD
    A[Task attempted] --> B{Quality gates pass?}
    B -->|No| C[Reject: Exit 2<br/>Teammate retries]
    B -->|Yes| D[Commit]

    D --> E{Circuit breaker?}
    E -->|MAX_CONSECUTIVE_FAILURES hit| F[Teammate goes idle<br/>Exit 0]
    E -->|OK| G{Task retry limit?}

    G -->|MAX_TASK_ATTEMPTS hit| H[Task escalated<br/>Move to next task]
    G -->|OK| I{Pending tasks?}

    I -->|Yes| J[Claim next task<br/>Exit 2 from teammate-idle]
    I -->|No| K[All done<br/>Exit 0]

    C --> A

    style C fill:#ffe1e1
    style F fill:#ffe1e1
    style H fill:#fff4e1
    style K fill:#e1ffe1
    style J fill:#e1ffe1
```

### Backpressure Levels

| Level | Mechanism | Trigger | Action |
|-------|-----------|---------|--------|
| **Task** | Quality gates | Gate fails | Reject task completion (exit 2), teammate retries |
| **Task retry** | MAX_TASK_ATTEMPTS | Same task fails N times | Task escalated, teammate moves on |
| **Circuit breaker** | MAX_CONSECUTIVE_FAILURES | N consecutive failures | Teammate goes idle (exit 0) |

---

## Quality Levels

**Constraints:**
- You MUST set quality level before execution because it determines gate behavior
- You MUST NOT use prototype in production code because shortcuts accumulate debt
- You SHOULD use library level for reusable code because polish matters for shared code

Define expectations in `.ralph/config.sh` (`QUALITY_LEVEL` variable):

| Level | Shortcuts OK | Tests Required | Polish Required |
|-------|--------------|----------------|-----------------|
| **Prototype** | Yes | No | No |
| **Production** | No | Yes | Some |
| **Library** | No | Yes | Yes |

### Behavior by Level

- **Prototype** - Fast iteration, skip backpressure gates
- **Production** - SDD mandatory, all gates must pass
- **Library** - Full coverage, documentation, edge cases

**Set in:** `.ralph/config.sh` (`QUALITY_LEVEL`)

---

## Task Sizing

**Constraints:**
- You MUST ensure one task fits one context window because exceeding context degrades quality
- You MUST split tasks that require >2000 lines to understand because complexity limits comprehension
- You MUST NOT batch unrelated work into single task because focused tasks are more reliable

One task = one context window.

### Right-sized

- Add database column + migration
- Add UI component to existing page
- Fix bug in login flow

### Too Large

- Build entire auth system
- Implement complete dashboard

**Test:** If >2000 lines to understand or >5 files -> split.

---

## Context Philosophy

Ralph does NOT enforce context percentages. The 40-60% sweet spot emerges naturally from atomic task design.

**INPUT-based control**: auto-compaction (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`) manages context size between task cycles
**No OUTPUT measurement**: We don't track or exit based on context percentage

---

## Gutter Detection

**Constraints:**
- You MUST add Sign and exit if stuck because continued attempts waste resources
- You MUST NOT retry same failed command more than 3 times because systematic issues need different approach
- You SHOULD recognize file modification cycles because oscillation indicates confusion

**You're stuck if:**
- Same command fails 3 times
- Same file modified 5+ times
- No progress in 30 minutes

**Recovery:** Add Sign -> Exit -> Fresh approach next task cycle.

---

## Circuit Breaker

**Constraints:**
- You MUST check .ralph/failures.json after circuit breaker because root cause needs identification
- You MUST fix underlying issue before restart because same failures will repeat
- You MUST NOT disable circuit breaker because it protects against runaway failures

After 3 consecutive failures, Agent Teams cockpit stops:

1. Check `.ralph/failures.json` for per-teammate failure counts
2. Check `.ralph/metrics.json` for task success/failure history
3. Fix underlying issue or adjust specs
4. Run `bash .ralph/launch-build.sh` again

---

## Plan Format

**Constraints:**
- You MUST keep plan under 100 lines because verbose plans confuse teammates
- You MUST limit each task to 3-5 lines because detail belongs in specs
- You MUST NOT include implementation details because tasks define what, not how

**The plan is disposable.** Regeneration costs one planning task cycle.

### Constraints

| Element | Limit |
|---------|-------|
| Entire plan | <100 lines |
| Each task | 3-5 lines |
| Implementation details | None |

### Task Format

```markdown
- [ ] Task title | Size: S/M | Files: N
  Acceptance: [single sentence]
```

### Anti-patterns

- 400-line plans
- Research summaries in plan (move to .ralph/specs/)
- Step-by-step implementation notes
- Keeping completed tasks forever

**Recovery:** If plan exceeds 100 lines -> re-run planning via Agent Teams cockpit (`bash .ralph/launch-build.sh`)

---

## Troubleshooting

### Gates Keep Failing

If quality gates fail repeatedly:
- You SHOULD check if task is too large
- You SHOULD verify gate commands are correct
- You MUST review gate output for specific errors

### Circuit Breaker Trips Too Often

If circuit breaker triggers frequently:
- You SHOULD check task clarity in plan
- You SHOULD lower MAX_CONSECUTIVE_FAILURES to catch issues earlier
- You MUST diagnose root cause before continuing

### Tasks Taking Too Long

If tasks consistently fail to complete in one task cycle:
- You SHOULD split task into smaller atomic parts
- You SHOULD reduce exploration in `PROMPT_teammate.md`
- You SHOULD use auto-compaction (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`) to reduce context size

---

*Version: 2.0.0 | Updated: 2026-02-10*
*Compliant with strands-agents SOP format (RFC 2119)*
