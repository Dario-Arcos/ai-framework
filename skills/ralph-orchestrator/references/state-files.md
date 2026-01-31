# State Files Reference

## Overview

This reference defines the state files used by Ralph for persistent state management across iterations. Understanding these files is essential for debugging loops and maintaining context continuity.

---

## File Overview

**Constraints:**
- You MUST understand file lifecycle because incorrect updates corrupt state
- You MUST NOT modify state files during execution monitoring because workers own state during loops
- You SHOULD read state files for debugging because they reveal loop behavior

| File | Purpose | Lifecycle |
|------|---------|-----------|
| `.ralph/config.sh` | Project configuration | Project lifetime |
| `AGENTS.md` | Operational guide (~50 lines) | Project lifetime |
| `guardrails.md` | Signs (session error lessons) | Current loop |
| `scratchpad.md` | Iteration-to-iteration state | Current loop |
| `specs/{goal}/discovery.md` | Problem definition, constraints | Current goal |
| `specs/{goal}/design/detailed-design.md` | Architectural decisions | Current goal |
| `specs/{goal}/implementation/plan.md` | Prioritized tasks | Current goal |
| `specs/*.md` | Requirements per topic | Feature lifetime |

### Implementation Plan Location

The implementation plan is located at:
```
specs/{goal}/implementation/plan.md
```

> **DEPRECATED**: Legacy `IMPLEMENTATION_PLAN.md` in project root is no longer supported.
> Do not use or create this file. All planning goes through the SOP structure.

---

## Signs System (guardrails.md)

**Constraints:**
- You MUST add Signs when errors occur because this prevents repeat failures
- You MUST read Signs at iteration start because accumulated knowledge guides behavior
- You MUST use standard Sign format because workers parse structure

When errors occur, add to guardrails.md:

```markdown
### Sign: [Problem]
- **Trigger**: [When this happens]
- **Instruction**: [What to do instead]
```

Every iteration reads Signs FIRST - Compounding intelligence.

---

## Scratchpad System (scratchpad.md)

Iteration-to-iteration memory within a single loop session.

**Constraints:**
- You MUST update scratchpad after each iteration because next iteration needs context
- You MUST NOT rely on scratchpad for persistent data because it clears on loop start
- You SHOULD include files modified because this aids debugging

### Format

```markdown
## Current State
- **Last task completed**: [task name]
- **Next task to do**: [task name]
- **Files modified this session**: [list]

## Key Decisions This Session
- [Decision with rationale]

## Blockers & Notes
- [Issues discovered]
```

### Comparison

| Aspect | Scratchpad | Signs |
|--------|------------|-------|
| Scope | Current iteration | Current loop |
| Lifecycle | Cleared on loop start | Cleared manually |
| Content | Progress, decisions | Errors, gotchas |
| Updates | Every iteration | On errors |

---

## Confession Pattern

Accountability mechanism for each iteration.

**Constraints:**
- You MUST include confession at iteration end because this forces completion validation
- You MUST provide evidence because claims without evidence are unverifiable
- You MUST NOT hedge with "partially complete" because binary completion enforces quality

### Format

```
> confession: objective=[task], met=[Yes/No], confidence=[N], evidence=[proof]
```

### Components

| Field | Content |
|-------|---------|
| `objective` | Task from `specs/{goal}/implementation/plan.md` |
| `met` | Yes or No (no hedging) |
| `confidence` | 0-100 integer (minimum 80 to mark complete) |
| `evidence` | Test output, file paths, command results |

### Why This Matters

- Forces explicit declaration of completion
- Prevents "I think I did it" without evidence
- Creates audit trail in `logs/iteration.log`
- Enables post-hoc verification of claims

**When:** Phase 4e, after state updates, before commit.

---

## Troubleshooting

### State File Corruption

If state files become inconsistent:
- You SHOULD check git history for last valid state
- You SHOULD regenerate scratchpad from git log
- You MUST NOT continue loop with corrupted state

### Signs Ignored by Workers

If same errors repeat despite Signs:
- You SHOULD verify Sign format includes Trigger and Instruction
- You SHOULD check worker prompts include Sign reading step
- You MUST review Sign clarity (vague instructions are ignored)

---

*Version: 1.2.0 | Updated: 2026-01-30*
*Compliant with strands-agents SOP format (RFC 2119)*
