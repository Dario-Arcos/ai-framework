# Supervision Modes Reference

## Overview

Ralph-orchestrator has two distinct phases with different supervision options. This reference clarifies exactly what modes exist and eliminates ambiguity.

---

## The Two Phases

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: PLANNING                                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Mode: Interactive OR Autonomous (user chooses)         │    │
│  │  Tools: SOP skills (discovery, planning, task-gen)      │    │
│  │  Duration: 30-90 minutes                                │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  MANDATORY CHECKPOINT: User approves plan before execution      │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 2: EXECUTION                                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Mode: ALWAYS AUTONOMOUS (Agent Teams)           │    │
│  │  Safety: Circuit breaker + quality gates                  │    │
│  │  Duration: 1-8 hours                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Planning Modes

### Interactive Mode (Default)

**When to use:**
- Requirements are unclear or complex
- First time working with this type of project
- User wants to learn from the process
- Architectural decisions need discussion

**Behavior:**
- SOP skills ask questions one at a time
- User answers, skill iterates
- User confirms before phase transitions
- Full collaboration throughout

**Duration:** 60-90 minutes typical

### Autonomous Mode

**When to use:**
- Requirements are clear and well-defined
- Similar to past projects
- User has limited time
- Trust the system to make reasonable decisions

**Behavior:**
- SOP skills make decisions independently
- All decisions documented in artifacts
- Blockers written to `blockers.md` in relevant spec directory
- Continues without blocking for input

**Duration:** 15-30 minutes typical

### Planning Mode Comparison

| Aspect | Interactive | Autonomous |
|--------|-------------|------------|
| User presence | Required | Not required |
| Questions | Asked one at a time | Answered with reasonable defaults |
| Decisions | User chooses | System chooses, documents why |
| Blockers | User resolves immediately | Documented for later review |
| Duration | 60-90 min | 15-30 min |
| Best for | Complex/unclear projects | Clear/familiar projects |

---

## Mandatory Checkpoint

**ALWAYS required between planning and execution, regardless of planning mode.**

The checkpoint presents:
- Summary of all artifacts generated
- Key decisions made (with rationale if autonomous)
- Any blockers found
- Task count and complexity breakdown

User options:
- **Approve**: Continue to execution
- **Review**: Inspect artifact contents
- **Redo**: Return to planning with interactive mode

**You MUST NOT skip this checkpoint.**

---

## Phase 2: Execution

### Core Truth

**Execution is ALWAYS autonomous.** The Agent Teams launches ephemeral teammates that each claim 1 task, implement it with fresh 200K context, and complete. There is no "interactive execution" - that's a contradiction.

### Safety Configuration

Execution runs autonomously until all tasks complete or a safety limit is reached. The key configuration options in `.ralph/config.sh`:

| Option | Variable | Default | Behavior |
|--------|----------|---------|----------|
| **Circuit breaker** | `MAX_CONSECUTIVE_FAILURES` | 3 | Stop teammate after N consecutive gate failures |
| **Coverage command** | `GATE_COVERAGE` | `""` (disabled) | Command that outputs coverage data. Parsed for percentage and compared against `MIN_TEST_COVERAGE` |
| **Coverage gate** | `MIN_TEST_COVERAGE` | 90 | Coverage below this blocks completion. Requires `GATE_COVERAGE` to be set |

### Configuration Example

```bash
# .ralph/config.sh

# Safety limits
MAX_CONSECUTIVE_FAILURES=3   # Circuit breaker threshold

# Coverage enforcement (GATE_COVERAGE must be set for MIN_TEST_COVERAGE to apply)
GATE_COVERAGE=""              # e.g., "npx vitest run --coverage" or "pytest --cov --cov-report=term"
MIN_TEST_COVERAGE=90          # Minimum coverage to accept (0-100)
```

---

## Safety Features (Always Active)

These protections are always active during execution:

| Feature | Trigger | Action |
|---------|---------|--------|
| **Circuit breaker** | `MAX_CONSECUTIVE_FAILURES` consecutive failures | Teammate goes idle (exit 0 via teammate-idle hook) |
| **Quality gates** | Test/typecheck/lint/build failure | Reject task completion (exit 2), teammate retries |
| **Coverage gate** | Coverage below `MIN_TEST_COVERAGE` (when `GATE_COVERAGE` set) | Reject task completion (exit 2) |

---

## Common Misconceptions

### "HITL Execution"

**Wrong:** "I want human-in-the-loop execution where I review each task."

**Right:** Execution is always autonomous. The Agent Teams runs teammates that claim tasks, execute them, and pass quality gates. Safety is enforced by circuit breakers and quality gates, not by human pauses.

### "AFK vs HITL"

**Wrong:** "AFK and HITL are two different execution modes."

**Right:** There's only ONE execution mode: autonomous via Agent Teams. Safety nets (MAX_CONSECUTIVE_FAILURES, quality gates) protect against runaway failures. You review results when execution completes.

### "Autonomous Planning = No Control"

**Wrong:** "If I use autonomous planning, I lose all control."

**Right:** The mandatory checkpoint before execution means you ALWAYS review and approve the plan. Autonomous planning just means you weren't present during generation - you still approve before anything executes.

---

## Decision Flowchart

```
Start
  │
  ▼
┌─────────────────────────────┐
│ Will you be present during  │
│ the planning phase?         │
└─────────────┬───────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
┌────────┐         ┌──────────┐
│  Yes   │         │    No    │
└───┬────┘         └────┬─────┘
    │                   │
    ▼                   ▼
Interactive         Autonomous
Planning            Planning
    │                   │
    └─────────┬─────────┘
              │
              ▼
┌─────────────────────────────┐
│ MANDATORY CHECKPOINT        │
│ Review and approve plan     │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ Configure safety limits in  │
│ .ralph/config.sh            │
└─────────────┬───────────────┘
              │
              ▼
       Launch Agent Teams
       (ALWAYS autonomous)
              │
              ▼
┌─────────────────────────────┐
│ Safety nets active:         │
│ - Circuit breaker (failures)│
│ - Quality gates per task    │
│ - Coverage gate (optional)  │
└─────────────────────────────┘
```

---

*Version: 2.0.0 | Updated: 2026-02-15*
*Rewritten to eliminate HITL/AFK ambiguity and ghost variables*
