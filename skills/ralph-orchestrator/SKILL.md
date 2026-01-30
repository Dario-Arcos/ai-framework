---
name: ralph-orchestrator
description: Use when building features requiring planning + autonomous execution. Triggers on multi-step implementations, overnight development, or when fresh context per task improves quality. Orchestrates SOP skills (discovery, planning, task-generation) then launches AFK loop.
---

# Ralph Loop: Master Orchestrator

> **SINGLE ENTRY POINT.** One invocation orchestrates everything.
> DO NOT invoke SOP skills separately - Ralph invokes them in sequence.

---

## Overview

- **Planning**: Interactive OR autonomous (user chooses)
- **Execution**: ALWAYS autonomous via loop.sh (optional checkpoints for review)

---

## When to Use

- New features or projects
- Large implementation plans
- Overnight/AFK development

---

## When NOT to Use

| Situation | Use Instead |
|-----------|-------------|
| Simple single-file change | Direct implementation |
| Only debugging | `systematic-debugging` skill |
| Only code review | `requesting-code-review` skill |
| Research only, no implementation | `sop-reverse` alone |

---

## Parameters

- **goal** (optional): High-level description. Asked in Step 1 if not provided.
- **flow** (optional): `forward` (new) or `reverse` (investigate existing).
- **planning_mode** (optional): `interactive` (default) or `autonomous`. Determines how SOP skills operate during planning phase.

---

## The Complete Flow

1. **Step 0**: Choose planning mode (Interactive/Autonomous)
2. **Step 1**: Validate prerequisites + detect flow (Forward/Reverse)
3. **Step 2**: Discovery (`sop-discovery`) OR Investigation (`sop-reverse`)
4. **Step 3-4**: Planning (`sop-planning`) + Task generation (`sop-task-generator`)
5. **Step 5**: Plan Review Checkpoint (mandatory before execution)
6. **Step 6**: Configure execution (quality level, optional checkpoints)
7. **Step 7**: Launch `./loop.sh specs/{goal}/` (ALWAYS autonomous)

> Full diagram: [ralph-orchestrator-flow.md](references/ralph-orchestrator-flow.md)

---

## Steps

### Infrastructure Setup

- [ ] Check if `./loop.sh` exists in project root
- [ ] If missing: `./skills/ralph-orchestrator/scripts/install.sh /path/to/project`
- [ ] Verify: `./loop.sh`, `.ralph/config.sh`, `guardrails.md`, `scratchpad.md` exist

**You MUST** verify loop.sh exists before planning. **You MUST NOT** proceed if infrastructure is missing.

> Error handling: [troubleshooting.md](references/troubleshooting.md)

---

### Step 0: Choose Planning Mode

**Use AskUserQuestion:**
```text
Question: "¿Estarás presente durante la planificación?"
Header: "Planning Mode"
Options:
- Interactive (Recommended): Te guiaré paso a paso, preguntando sobre requisitos y diseño
- Autonomous: Planificaré autónomamente, documentando todas las decisiones. Revisarás el plan completo antes de ejecutar.
```

**Mode determines how SOP skills operate:**

| Planning Mode | SOP Skills Behavior |
|---------------|---------------------|
| **Interactive** | Ask questions, wait for answers, iterate with user |
| **Autonomous** | Make reasonable decisions, document rationale, continue without blocking |

**Store selection:** `PLANNING_MODE={interactive|autonomous}` for use in subsequent steps.

**Recommendations:**
- **Interactive** → Projects with unclear requirements, complex decisions, or when user wants to learn
- **Autonomous** → Clear requirements, similar to past projects, or user has limited time

**You MUST NOT** proceed without explicit mode selection.

---

### Step 1: Validate Prerequisites and Detect Flow

**Validate SOP Prerequisites:**
- [ ] `specs/{feature}/discovery.md` exists → If missing: Execute `sop-discovery`
- [ ] `specs/{feature}/design/detailed-design.md` exists → If missing: Execute `sop-planning`
- [ ] `specs/{feature}/implementation/plan.md` + task files exist → If missing: Execute `sop-task-generator`

**Detect Flow (Use AskUserQuestion):**
```text
Question: "What type of flow do you need?"
Options:
- Forward: Build something new (feature, improvement, project)
- Reverse: Investigate something existing before modifying it
```

**You MUST NOT:**
- Skip discovery and use AGENTS.md as substitute
- Skip planning and improvise architecture
- Proceed if ANY prerequisite is missing or flow type unknown

---

### Step 2A: Discovery (Forward)

```text
/sop-discovery goal="{goal}" --mode={PLANNING_MODE}
```

**Mode behavior:**
- `interactive`: Asks questions one at a time, waits for answers
- `autonomous`: Generates comprehensive discovery, documents assumptions

Output: `specs/{goal}/discovery.md` → Continue to Step 3.

---

### Step 2B: Reverse Investigation

```text
/sop-reverse artifact="{path}" --mode={PLANNING_MODE}
```

**Mode behavior:**
- `interactive`: Confirms artifact type, asks clarifying questions
- `autonomous`: Auto-detects type, completes investigation, documents deferred questions

Ask user if continuing to Forward (in interactive mode). In autonomous mode, continue to Forward by default.

---

### Step 3: Planning

```text
/sop-planning discovery_path="specs/{goal}/discovery.md" --mode={PLANNING_MODE}
```

**Mode behavior:**
- `interactive`: Iterates on requirements, research, and design with user feedback
- `autonomous`: Generates complete design in single pass, documents all decisions

Output: `specs/{goal}/design/detailed-design.md` → Continue to Step 4.

---

### Step 4: Task Generation

```text
/sop-task-generator input="specs/{goal}/design/detailed-design.md" --mode={PLANNING_MODE}
```

**Mode behavior:**
- `interactive`: Presents task breakdown for approval, allows iteration
- `autonomous`: Generates all task files, adds "[AUTO-GENERATED]" metadata

Output: `plan.md` + `.code-task.md` files → Continue to Step 5.

---

### Step 5: Plan Review Checkpoint

**MANDATORY before execution, regardless of planning mode.**

**Present summary to user:**
```markdown
## Plan Review

**Planning Mode Used:** {PLANNING_MODE}

### Artifacts Generated
- Discovery: `specs/{goal}/discovery.md`
- Design: `specs/{goal}/design/detailed-design.md`
- Tasks: {N} task files in `specs/{goal}/implementation/`

### Key Decisions Made
1. [Decision 1 from design document]
2. [Decision 2 from design document]
3. [Decision 3 from design document]

### Blockers Found
- [List from blockers.md if exists, or "None"]

### Task Summary
| Step | Tasks | Complexity |
|------|-------|------------|
| 01   | N     | S/M/L      |
| ...  | ...   | ...        |
```

**Use AskUserQuestion:**
```text
Question: "¿Aprobar plan y continuar a ejecución?"
Options:
- Aprobar y continuar: Proceder a configurar ejecución
- Revisar artifacts: Mostrar contenido de artifacts antes de decidir
- Rehacer planificación: Volver a Step 2 con modo interactivo
```

**You MUST NOT:**
- Skip this checkpoint even if planning was interactive
- Launch execution without explicit user approval
- Proceed if user requests artifact review (show artifacts first)

---

### Step 6: Configure Execution

**Execution is ALWAYS autonomous via loop.sh.** The only choice is checkpoint frequency.

| Question | Options |
|----------|---------|
| Checkpoints | **None** (Recommended): Run until complete / **Every N tasks**: Pause for review |
| Checkpoint Interval | 3 / 5 / 10 tasks (only if checkpoints enabled) |
| Quality Level | **Production**: Tests+Types+Lint+Build (Recommended) / **Prototype**: Skip verifications / **Library**: All + coverage + docs |

Update `.ralph/config.sh` with selections. Details: [configuration-guide.md](references/configuration-guide.md)

---

### Step 7: Launch Execution

**Prerequisites checklist:**
- [ ] `specs/{goal}/implementation/plan.md` exists
- [ ] `.code-task.md` files exist
- [ ] `.ralph/config.sh` configured
- [ ] **Plan Review Checkpoint passed (Step 5)**

**Launch:**
```bash
Bash("./loop.sh specs/{goal}/", run_in_background=True)
```

Transition to Phase 2: Monitoring mode.

---

## Phase 2: Execution Monitoring

**Your role changes to MONITOR ONLY.**

| Allowed | Forbidden |
|---------|-----------|
| `TaskOutput(task_id, block=False)` | Write/Edit tools |
| `Read("status.json")` | Bash commands that modify state |
| `Read("logs/*")` | Task tool for implementation |

**If user asks to implement:** *"Workers have fresh 200K token context - 10x better. Want me to update the plan and restart instead?"*

> Full monitoring guide: [monitoring-pattern.md](references/monitoring-pattern.md)

---

## Core Principles

1. **Single Entry Point** - Invoke once, orchestrate everything
2. **Flexible Planning, Checkpoint Before Execution** - Planning can be interactive OR autonomous, but user ALWAYS approves before execution
3. **Fresh Context Is Reliability** - Each iteration clears context
4. **Disk Is State, Git Is Memory** - Files are handoff mechanism

---

## References

| File | Description |
|------|-------------|
| [ralph-orchestrator-flow.md](references/ralph-orchestrator-flow.md) | Complete step-by-step flow diagram |
| [monitoring-pattern.md](references/monitoring-pattern.md) | Dashboard, log reading, status |
| [supervision-modes.md](references/supervision-modes.md) | AFK vs Checkpoint vs HITL |
| [configuration-guide.md](references/configuration-guide.md) | All config options |
| [quality-gates.md](references/quality-gates.md) | Gate descriptions, TDD |
| [sop-integration.md](references/sop-integration.md) | How SOP skills connect |
| [state-files.md](references/state-files.md) | File purposes and lifecycle |
| [memories-system.md](references/memories-system.md) | Signs vs Memories |
| [backpressure.md](references/backpressure.md) | Checkpoints, circuit breakers |
| [mode-selection.md](references/mode-selection.md) | Decision flowcharts |
| [observability.md](references/observability.md) | Logging, metrics, debugging |
| [red-flags.md](references/red-flags.md) | Dangerous thoughts |
| [alternative-loops.md](references/alternative-loops.md) | Coverage, lint, entropy loops |
| [pressure-testing.md](references/pressure-testing.md) | Adversarial testing |
| [troubleshooting.md](references/troubleshooting.md) | Common issues and fixes |
| [best-practices.md](references/best-practices.md) | Recommended patterns |

---

## Related Skills

| Skill | Step | Purpose |
|-------|------|---------|
| `sop-discovery` | 2A | Constraints, risks |
| `sop-planning` | 3 | Research, design |
| `sop-task-generator` | 4 | Task files |
| `sop-reverse` | 2B | Investigation |
| `sop-code-assist` | Workers | TDD implementation |

---

*Version: 3.1.0 | Updated: 2026-01-29*
