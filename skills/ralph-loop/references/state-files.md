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
| `memories.md` | Persistent learnings | Indefinite |
| `scratchpad.md` | Iteration-to-iteration state | Current loop |
| `DISCOVERY.md` | Problem definition, constraints | Current goal |
| `IMPLEMENTATION_PLAN.md` | Prioritized tasks | Current goal |
| `specs/*.md` | Requirements per topic | Feature lifetime |

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

## Memories System (memories.md)

Persistent learnings that survive loop restarts.

**Constraints:**
- You MUST update memories only during planning mode because build mode focuses on execution
- You MUST include tags because tags enable search and categorization
- You SHOULD include reasoning for decisions because cargo-cult decisions lack foundation

### CLI Management (memories.sh)

```bash
# Add memories
./memories.sh add pattern "All APIs return Result<T>" --tags api,error-handling
./memories.sh add decision "Chose PostgreSQL" --reason "ACID compliance" --tags database
./memories.sh add fix "Set NODE_ENV in CI" --tags ci,testing

# Query memories
./memories.sh search "database"
./memories.sh list --type pattern --limit 5
```

### Format

```markdown
### mem-[timestamp]-[hash]
> [Learning or decision with context]
> Reason: [Why this matters]  (optional, from --reason flag)
<!-- tags: tag1, tag2 | created: YYYY-MM-DD -->
```

### Categories

| Category | Content |
|----------|---------|
| **Patterns** | Architecture approaches, coding conventions |
| **Decisions** | Tech choices, design trade-offs |
| **Fixes** | Solutions to persistent problems |
| **Context** | Confessions and accountability records |

### Signs vs Memories

| Aspect | Signs (guardrails.md) | Memories (memories.md) |
|--------|----------------------|------------------------|
| Scope | Current loop session | All future sessions |
| Content | Error lessons, gotchas | Patterns, preferences |
| Lifecycle | Cleared with new goal | Persists indefinitely |
| Updates | Build mode (errors) | Planning mode only |

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

| Aspect | Scratchpad | Signs | Memories |
|--------|------------|-------|----------|
| Scope | Current iteration | Current loop | All loops |
| Lifecycle | Cleared on loop start | Cleared manually | Persists |
| Content | Progress, decisions | Errors, gotchas | Patterns |
| Updates | Every iteration | On errors | Planning only |

---

## Confession Pattern

Accountability mechanism for each iteration.

**Constraints:**
- You MUST include confession at iteration end because this forces completion validation
- You MUST provide evidence because claims without evidence are unverifiable
- You MUST NOT hedge with "partially complete" because binary completion enforces quality

### Format

```
> confession: objective=[task], met=[Yes/No], evidence=[proof]
```

### Components

| Field | Content |
|-------|---------|
| `objective` | Task from IMPLEMENTATION_PLAN.md |
| `met` | Yes or No (no hedging) |
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

### Memories Not Loading

If workers don't see memories:
- You SHOULD verify memories.md path is correct
- You SHOULD check memories format follows template
- You MUST ensure memories.md is committed to branch

### Signs Ignored by Workers

If same errors repeat despite Signs:
- You SHOULD verify Sign format includes Trigger and Instruction
- You SHOULD check worker prompts include Sign reading step
- You MUST review Sign clarity (vague instructions are ignored)

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
