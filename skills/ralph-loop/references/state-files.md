# State Files Reference

Ralph uses several files for state management across iterations.

## File Overview

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
- Creates audit trail in `claude_output/iteration_NNN.txt`
- Enables post-hoc verification of claims

**When:** Phase 4e, after state updates, before commit.
