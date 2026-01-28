---
name: ralph-orchestrator
description: Master orchestrator for autonomous development handling both interactive planning (HITL) and autonomous execution (AFK). Single entry point for the entire SOP workflow. Ideal for starting new features, executing large implementation plans, or overnight autonomous development.
---

# Ralph Loop: Master Orchestrator

> **STOP. READ THIS FIRST.**
>
> Ralph-orchestrator is the **SINGLE ENTRY POINT** for autonomous development.
> You invoke `/ralph-orchestrator` ONCE. It orchestrates EVERYTHING:
>
> 1. **PLANNING (HITL)** - Interactive session where YOU guide the user through planning
> 2. **EXECUTION (AFK)** - Autonomous loop where YOU only MONITOR
>
> DO NOT invoke sop-discovery, sop-planning, or sop-task-generator separately.
> Ralph-orchestrator invokes them FOR YOU in the correct sequence.

---

## Table of Contents

- [Overview](#overview)
- [When to Use](#when-to-use)
- [When NOT to Use](#when-not-to-use)
- [Parameters](#parameters)
- [The Complete Flow](#the-complete-flow)
- [Steps](#steps)
- [Phase 2: Execution Monitoring](#phase-2-execution-monitoring)
- [Configuration](#configuration)
- [Files & Structure](#files--structure)
- [Troubleshooting](#troubleshooting)
- [References](#references)

---

## Overview

Ralph Loop is the **master orchestrator** for the SOP development framework. It manages the complete lifecycle from idea to implementation:

- **Planning Phase (HITL)**: You guide the user through discovery, design, and task generation using SOP skills in the current interactive session
- **Execution Phase (AFK)**: Workers implement tasks autonomously with fresh 200K token context per iteration

**Key Principle**: One invocation, complete flow. The user says what they want, you orchestrate everything.

---

## When to Use

- Starting any new feature or project
- Implementing improvements based on research
- Executing large implementation plans
- When fresh context per task improves quality
- Overnight or AFK development needed

---

## When NOT to Use

| Situation | Why Not | Use Instead |
|-----------|---------|-------------|
| Simple single-file change | Overhead exceeds benefit | Direct implementation |
| Only debugging | Needs conversation context | `systematic-debugging` skill |
| Only code review | Not iterative | `requesting-code-review` skill |
| Research only, no implementation | Different workflow | `sop-reverse` alone |

---

## Parameters

- **goal** (optional): High-level description of what to build. If not provided, will be asked in Step 1.
- **flow** (optional): `forward` (new feature) or `reverse` (investigate existing). If not provided, will be asked.

---

## The Complete Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RALPH-LOOP ORCHESTRATION                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │              PHASE 1: PLANNING (Interactive - This Session)           │ │
│  │                                                                        │ │
│  │   Step 1: Detect Flow                                                 │ │
│  │   ┌─────────────────────┐                                             │ │
│  │   │ Forward or Reverse? │                                             │ │
│  │   └──────────┬──────────┘                                             │ │
│  │              │                                                         │ │
│  │   ┌──────────┴──────────┐                                             │ │
│  │   ▼                     ▼                                             │ │
│  │ FORWARD              REVERSE                                          │ │
│  │   │                     │                                             │ │
│  │   ▼                     ▼                                             │ │
│  │ Step 2: Discovery    Step 2: Reverse Investigation                   │ │
│  │ (/sop-discovery)     (/sop-reverse)                                   │ │
│  │   │                     │                                             │ │
│  │   ▼                     ▼                                             │ │
│  │ Step 3: Planning     Generates specs, optionally                      │ │
│  │ (/sop-planning)      continues to Forward flow                        │ │
│  │   │                                                                    │ │
│  │   ▼                                                                    │ │
│  │ Step 4: Task Generation                                               │ │
│  │ (/sop-task-generator)                                                 │ │
│  │   │                                                                    │ │
│  │   ▼                                                                    │ │
│  │ Step 5: Configure Execution                                           │ │
│  │ (Mode, Quality Level)                                                 │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                              │                                              │
│                              ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │              PHASE 2: EXECUTION (Autonomous - Background)             │ │
│  │                                                                        │ │
│  │   Step 6: Launch Loop                                                 │ │
│  │   ./loop.sh specs/{goal}/                                             │ │
│  │                                                                        │ │
│  │   Workers execute .code-task.md files with TDD                        │ │
│  │   You MONITOR only (read logs, status, no modifications)             │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Steps

### Step 1: Detect Flow and Goal

**You MUST:**
- Ask the user what they want to accomplish (if not provided)
- Determine if this is a Forward or Reverse flow

**Use AskUserQuestion:**
```
Question: "¿Qué tipo de flujo necesitas?"
Options:
- Forward: Crear algo nuevo (feature, mejora, proyecto)
- Reverse: Investigar algo existente antes de modificarlo
```

**After selection:**
- If Forward → Continue to Step 2A
- If Reverse → Continue to Step 2B

**You MUST NOT:**
- Proceed without knowing the flow type
- Assume Forward without asking

---

### Step 2A: Discovery (Forward Flow)

**You MUST:**
- Invoke the `sop-discovery` skill with the user's goal
- This skill will ask clarifying questions about constraints, risks, and prior art
- Wait for discovery to complete and produce `discovery.md`

**Invocation pattern:**
```
/sop-discovery goal="{user's goal}"
```

**Output expected:** `specs/{goal}/discovery.md`

**After discovery completes:** Continue to Step 3.

---

### Step 2B: Reverse Investigation (Reverse Flow)

**You MUST:**
- Invoke the `sop-reverse` skill with the artifact to investigate
- This skill will analyze and document the artifact
- Wait for investigation to complete

**Invocation pattern:**
```
/sop-reverse artifact="{path or description}"
```

**After investigation:**
- Ask user if they want to continue to Forward flow (improve/modify)
- If yes → Continue to Step 3 with generated specs as context
- If no → End orchestration (investigation complete)

---

### Step 3: Planning

**You MUST:**
- Invoke the `sop-planning` skill with discovery output
- This skill will research, design, and document the solution
- Wait for planning to complete and produce `detailed-design.md`

**Invocation pattern:**
```
/sop-planning discovery_path="specs/{goal}/discovery.md"
```

**Output expected:**
- `specs/{goal}/design/detailed-design.md`
- `specs/{goal}/research/*.md` (if research was done)

**After planning completes:** Continue to Step 4.

---

### Step 4: Task Generation

**You MUST:**
- Invoke the `sop-task-generator` skill with the design document
- This skill will break down the design into implementable tasks
- Wait for task generation to complete

**Invocation pattern:**
```
/sop-task-generator input="specs/{goal}/design/detailed-design.md"
```

**Output expected:**
- `specs/{goal}/implementation/plan.md`
- `specs/{goal}/implementation/step*/task-*.code-task.md`

**After task generation completes:** Continue to Step 5.

---

### Step 5: Configure Execution

**You MUST:**
- Ask the user to configure execution parameters
- Use AskUserQuestion tool for each decision

**Question 1: Supervision Mode**
```
Question: "¿Qué nivel de supervisión quieres durante la ejecución?"
Options:
- AFK: Completamente autónomo. Me voy a dormir. (Recomendado)
- Checkpoint: Pausa cada N tareas para revisión
- HITL: Supervisión activa, me quedo monitoreando
```

**If Checkpoint selected, ask:**
```
Question: "¿Cada cuántas tareas quieres un checkpoint?"
Options:
- 3 tareas
- 5 tareas
- 10 tareas
```

**Question 2: Quality Level**
```
Question: "¿Qué nivel de calidad para los quality gates?"
Options:
- Production: Tests + Types + Lint + Build deben pasar (Recomendado)
- Prototype: Salta verificaciones (rápido pero arriesgado)
- Library: Todo lo anterior + coverage + docs
```

**After configuration:**
- Update `.ralph/config.sh` with selections
- Continue to Step 6

---

### Step 6: Launch Execution

**You MUST:**
- Verify all prerequisites are in place:
  - [ ] `specs/{goal}/implementation/plan.md` exists
  - [ ] `.code-task.md` files exist OR legacy plan.md has tasks
  - [ ] `.ralph/config.sh` is configured
- Launch the execution loop in background:

```bash
Bash("./loop.sh specs/{goal}/", run_in_background=True)
```

**After launch:**
- Report to user that execution has started
- Transition to Phase 2: Monitoring mode
- Provide monitoring instructions

---

## Phase 2: Execution Monitoring

**Your role changes to MONITOR ONLY.**

See [references/monitoring-pattern.md](references/monitoring-pattern.md) for detailed guidance.

### You MAY

```python
TaskOutput(task_id, block=False)  # Check progress
Read("status.json")               # Read state
Read("logs/*")                    # Read logs
Read("specs/*/implementation/*")  # Read plans
```

### You MUST NOT

- Use Write/Edit tools on ANY file
- Run Bash commands that modify state
- Use Task tool for implementation work
- Implement code yourself

### If User Asks to Implement

Respond:
> *"This session monitors ralph-orchestrator. Workers have fresh 200K token context - 10x better than implementing here. Want me to update the plan and restart the loop instead?"*

### Checkpoint Handling

If `CHECKPOINT_MODE` is enabled and loop pauses:
1. Review completed work with user
2. Ask if adjustments needed
3. Resume or stop based on user decision

---

## Configuration

Configuration in `.ralph/config.sh`. See [references/configuration-guide.md](references/configuration-guide.md).

| Setting | Default | Description |
|---------|---------|-------------|
| `QUALITY_LEVEL` | `production` | prototype/production/library |
| `SUPERVISION_MODE` | `afk` | afk/checkpoint/hitl |
| `CHECKPOINT_INTERVAL` | `5` | Tasks between checkpoints |
| `MAX_CONSECUTIVE_FAILURES` | `3` | Circuit breaker threshold |
| `MAX_TASK_ATTEMPTS` | `3` | Task abandonment threshold |
| `CONTEXT_LIMIT` | `200000` | Token limit |

### Quality Gates

```bash
GATE_TEST="npm test"
GATE_TYPECHECK="npm run typecheck"
GATE_LINT="npm run lint"
GATE_BUILD="npm run build"
```

---

## Files & Structure

### Specs (generated during planning)

```
specs/{goal}/
├── discovery.md                    # From sop-discovery
├── rough-idea.md                   # Initial idea
├── idea-honing.md                  # Q&A log
├── research/                       # From sop-planning
│   └── *.md
├── design/
│   └── detailed-design.md          # From sop-planning
└── implementation/
    ├── plan.md                     # Checklist
    └── step*/
        └── task-*.code-task.md     # From sop-task-generator
```

### Ralph Files

| File | Purpose |
|------|---------|
| `.ralph/config.sh` | Project configuration |
| `AGENTS.md` | Project context |
| `guardrails.md` | Error lessons (Signs) |
| `memories.md` | Persistent learnings |
| `scratchpad.md` | Session state |
| `status.json` | Current loop state |

---

## Installation

```bash
# From your project root (must have .git/)
/path/to/skills/ralph-orchestrator/scripts/install.sh
```

**Prerequisites**:
- Existing git repo
- Validation commands (tests, lint, build)
- SOP skills available (sop-discovery, sop-planning, sop-task-generator)

---

## Core Principles

1. **Single Entry Point** - User invokes `/ralph-orchestrator` once, you orchestrate everything
2. **HITL Planning** - Planning is interactive in current session
3. **AFK Execution** - Execution is autonomous in background
4. **Fresh Context Is Reliability** - Each iteration clears context
5. **Backpressure Over Prescription** - Gates reject bad work
6. **Disk Is State, Git Is Memory** - Files are handoff mechanism

---

## Troubleshooting

### Problem: User unsure which flow
**Solution**: Ask clarifying questions. Forward = building new. Reverse = understanding existing first.

### Problem: Planning taking too long
**Cause**: Too many clarifying questions or research rabbit holes
**Solution**: Set time expectations. Discovery should be 10-20 min. Planning 30-60 min.

### Problem: Workers failing on same task
**Cause**: Task too complex or missing context
**Solution**: Read logs, update AGENTS.md, consider breaking task into subtasks.

### Problem: Orchestrator tempted to implement
**Solution**: Workers have 200K fresh context. Your intervention pollutes. Update plan instead.

---

## Constraints Summary

### Planning Phase (Steps 1-5)
- You MUST ask ONE question at a time
- You MUST wait for user response before proceeding
- You MUST invoke SOP skills in correct sequence
- You MUST NOT skip any planning step
- You MUST NOT batch multiple questions
- You MUST document all decisions in specs

### Execution Phase (Step 6+)
- You MUST only monitor, never implement
- You MUST NOT use Write/Edit tools on any file
- You MUST NOT use Task tool for implementation work
- You MAY read status.json, logs, and plan files
- You SHOULD report progress to user periodically

---

## References

| File | Content |
|------|---------|
| [monitoring-pattern.md](references/monitoring-pattern.md) | Dashboard, log reading, status checking |
| [supervision-modes.md](references/supervision-modes.md) | AFK vs Checkpoint vs HITL |
| [configuration-guide.md](references/configuration-guide.md) | All config options, exit codes |
| [quality-gates.md](references/quality-gates.md) | Gate descriptions, TDD enforcement |
| [sop-integration.md](references/sop-integration.md) | How SOP skills connect |

---

## Related Skills (Invoked Internally)

| Skill | When Invoked | Purpose |
|-------|--------------|---------|
| `sop-discovery` | Step 2A | Constraints, risks, prior art |
| `sop-planning` | Step 3 | Requirements, research, design |
| `sop-task-generator` | Step 4 | Generate implementation tasks |
| `sop-reverse` | Step 2B | Investigate existing artifacts |
| `code-assist` | By workers | TDD implementation per task |

**Note:** You invoke these skills internally during orchestration. The user does NOT invoke them separately.

---

*Master orchestrator for the SOP development framework.*
*Version: 2.0.0 | Updated: 2026-01-28*
