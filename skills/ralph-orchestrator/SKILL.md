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
- [Knowledge Management](#knowledge-management)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
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
│  │   Step 0: Validate Prerequisites                                      │ │
│  │   ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │   │ Check: discovery.md, detailed-design.md, plan.md, task files   │ │ │
│  │   │ If missing: Execute required SOP skill FIRST                   │ │ │
│  │   └──────────────────────────┬──────────────────────────────────────┘ │ │
│  │                              │                                        │ │
│  │                              ▼                                        │ │
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

### Infrastructure Setup

**Before starting ANY work, verify infrastructure:**

1. Check if `./loop.sh` exists in project root
2. If NOT exists:
   ```bash
   # Run from ai-framework directory
   ./skills/ralph-orchestrator/scripts/install.sh /path/to/project
   ```
3. Verify installation completed:
   - `./loop.sh` exists
   - `.ralph/config.sh` exists
   - `guardrails.md` exists
   - `scratchpad.md` exists

**You MUST:**
- Always verify loop.sh exists before planning
- Run install.sh if infrastructure is missing
- Verify all required files after installation

**You MUST NOT:**
- Proceed to planning if infrastructure is missing
- Implement directly if loop.sh is absent
- Assume infrastructure exists without checking

---

### Error Handling

**If Prerequisites Fail:**
1. STOP immediately
2. Report missing prerequisites to user:
   - "Missing: loop.sh - Run install.sh first"
   - "Missing: .ralph/config.sh - Infrastructure incomplete"
3. DO NOT improvise or implement directly
4. Suggest remediation steps
5. Wait for user to fix, then retry

**If Loop Fails:**
1. Check logs/ directory for error details
2. Read last iteration output
3. Identify root cause
4. Fix and restart loop (do not start fresh)

---

### Step 0: Validate SOP Prerequisites (BEFORE any work)

**You MUST validate these artifacts exist before proceeding:**

1. **Discovery Phase**
   - Check: `specs/{feature}/discovery.md` exists
   - If missing: Execute sop-discovery skill FIRST
   - Verify: JTBD is documented

2. **Planning Phase**
   - Check: `specs/{feature}/design/` directory exists
   - Check: `specs/{feature}/design/detailed-design.md` exists
   - If missing: Execute sop-planning skill FIRST
   - Verify: Architecture decisions documented

3. **Task Generation**
   - Check: `specs/{feature}/implementation/plan.md` exists
   - Check: Task files exist for ALL steps in plan
   - If missing: Execute sop-task-generator skill FIRST

**You MUST NOT:**
- Skip discovery and use AGENTS.md as substitute
- Skip planning and improvise architecture
- Generate tasks without design artifacts
- Proceed to execution if ANY prerequisite is missing

**If prerequisites fail:**
1. STOP immediately
2. Report which artifacts are missing
3. Execute the required SOP skill
4. Re-validate before continuing

---

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

## Knowledge Management

Ralph uses two complementary systems for capturing knowledge:

### Guardrails (Signs) - Session Scope

**File**: `guardrails.md`
**Purpose**: Capture technical gotchas discovered DURING the current session
**Lifetime**: Read at start of each iteration, relevant for current project
**Examples**:
- ESM import quirks
- Configuration issues
- Build tool workarounds
- Testing environment setup

**When to add a Sign**:
- You encountered an unexpected error
- A workaround was needed
- Something didn't work as documented
- Future iterations might hit the same issue

### Memories - Permanent Scope

**File**: `memories.md`
**Purpose**: Capture DECISIONS that should persist across sessions
**Lifetime**: Permanent project knowledge, survives session restarts
**Examples**:
- Why we chose library X over Y
- Architecture trade-offs made
- Patterns established for the codebase
- Constraints that shouldn't be violated

**When to add a Memory**:
- A significant architectural decision was made
- A trade-off was evaluated and decided
- A pattern was established intentionally
- Future developers need this context

### Comparison

| Aspect | Guardrails (Signs) | Memories |
|--------|-------------------|----------|
| Scope | Session | Permanent |
| Content | Technical gotchas | Decisions & rationale |
| Trigger | "I hit this error" | "We decided this because..." |
| Audience | Same iteration/loop | Future sessions/developers |

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

## Best Practices

### Loop Execution

**Always use background execution:**
```bash
# Correct: Use run_in_background=true
Bash(command="./loop.sh", run_in_background=true)

# Incorrect: Foreground execution risks timeout
Bash(command="./loop.sh")  # May be killed by timeout
```

**Monitor without blocking:**
```bash
# Check status without waiting
TaskOutput(task_id="{id}", block=false)

# Read full log for details
Read(file_path="logs/iteration-{N}.log")

# DO NOT use these (they block):
# tail -f logs/current.log  # Blocks indefinitely
# Bash with long timeout    # May kill process
```

### Context Management

**Target 40-60% context usage:**
- Fresh context = better quality output
- After 60%, consider iterating to reset context
- The first 40-60% of context window is most effective

**Configuration recommendations:**
```bash
CONTEXT_LIMIT=200000    # 200K tokens (Claude Opus)
CONTEXT_WARNING=40      # Start warning at 40%
CONTEXT_CRITICAL=60     # Force iteration at 60%
```

### Iteration Strategy

**When to let it iterate:**
- Complex multi-file changes
- Debugging cycles
- When tests are failing

**When to intervene:**
- Loop seems stuck on same error
- Approaching 3+ iterations on simple task
- Quality degrading instead of improving

### Knowledge Capture

**After every session, verify:**
1. `guardrails.md` has at least 1 new Sign (if gotchas found)
2. `memories.md` captures major decisions
3. `scratchpad.md` reflects final state

---

## Constraints Summary

### Prerequisite Phase (Step 0)
- You MUST validate SOP artifacts exist BEFORE any work
- You MUST check: discovery.md, detailed-design.md, plan.md, task files
- You MUST execute the required SOP skill if artifacts are missing
- You MUST NOT skip discovery and use AGENTS.md as substitute
- You MUST NOT skip planning and improvise architecture
- You MUST NOT proceed to execution if ANY prerequisite is missing

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
| `sop-code-assist` | By workers | TDD implementation per task |

**Note:** You invoke these skills internally during orchestration. The user does NOT invoke them separately.

---

*Master orchestrator for the SOP development framework.*
*Version: 2.0.0 | Updated: 2026-01-28*
