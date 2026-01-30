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
│  │  Mode: ALWAYS AUTONOMOUS (loop.sh in background)        │    │
│  │  Optional: Checkpoints every N tasks for review         │    │
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

**Execution is ALWAYS autonomous.** The loop.sh script runs in the background and executes tasks with fresh context per iteration. There is no "interactive execution" - that's a contradiction.

### Checkpoint Configuration

The ONLY configuration choice for execution is checkpoint frequency:

| Option | Configuration | Behavior |
|--------|---------------|----------|
| **No checkpoints** | `CHECKPOINT_MODE="none"` | Run until complete or failure |
| **Every N tasks** | `CHECKPOINT_MODE="iterations"` + `CHECKPOINT_INTERVAL=N` | Pause every N tasks for review |

### When to Use Checkpoints

**No checkpoints (recommended for most cases):**
- Well-defined tasks with clear acceptance criteria
- Strong test coverage (90%+)
- Confident in quality gates
- Overnight/AFK runs

**Checkpoints every 3-5 tasks:**
- First time using ralph-orchestrator
- Learning how the system handles your codebase
- Higher-risk changes (auth, payments)
- Testing new quality gate configurations

### Configuration Example

```bash
# .ralph/config.sh

# No checkpoints - run until complete
CHECKPOINT_MODE="none"

# OR: Checkpoint every 5 tasks
CHECKPOINT_MODE="iterations"
CHECKPOINT_INTERVAL=5
```

---

## Safety Features (Always Active)

These protections work regardless of checkpoint configuration:

| Feature | Trigger | Action |
|---------|---------|--------|
| **Circuit breaker** | 3 consecutive failures | Exit with code 2 |
| **Task abandonment** | Same task fails 3 times | Exit with code 7 |
| **Loop thrashing** | Oscillating task patterns | Exit with code 6 |
| **Quality gates** | Test/lint/build failure | Reject iteration, retry |

---

## Common Misconceptions

### "HITL Execution"

**Wrong:** "I want human-in-the-loop execution where I review each task."

**Right:** Execution is always autonomous. If you want frequent review, use checkpoints every 1-3 tasks. But the loop itself runs autonomously - you review at pauses, not during execution.

### "AFK vs HITL"

**Wrong:** "AFK and HITL are two different execution modes."

**Right:** There's only ONE execution mode: autonomous via loop.sh. "AFK" means no checkpoints. "Frequent checkpoints" replaces what was misleadingly called "HITL".

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
│ Do you want review pauses   │
│ during execution?           │
└─────────────┬───────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
┌────────┐         ┌──────────┐
│  Yes   │         │    No    │
└───┬────┘         └────┬─────┘
    │                   │
    ▼                   ▼
Checkpoints         No checkpoints
every N tasks       (full AFK)
    │                   │
    └─────────┬─────────┘
              │
              ▼
       Launch loop.sh
       (ALWAYS autonomous)
```

---

*Version: 2.0.0 | Updated: 2026-01-29*
*Rewritten to eliminate HITL/AFK ambiguity*
