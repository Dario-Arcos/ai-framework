---
name: ralph-orchestrator
description: Use when building features requiring planning + autonomous execution. Triggers on multi-step implementations, overnight development, or when fresh context per task improves quality. Orchestrates SOP skills (discovery, planning, task-generation) then launches AFK loop.
---

# Ralph Loop: Master Orchestrator

> **SINGLE ENTRY POINT.** One invocation orchestrates everything.
> DO NOT invoke SOP skills separately - Ralph invokes them in sequence.

---

## Overview

- **Planning (HITL)**: Guide user through discovery, design, task generation
- **Execution (AFK)**: Workers implement with fresh 200K context per iteration

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

---

## The Complete Flow

1. **Step 0-1**: Validate infrastructure + detect flow (Forward/Reverse)
2. **Step 2**: Discovery (`sop-discovery`) OR Investigation (`sop-reverse`)
3. **Step 3-4**: Planning (`sop-planning`) + Task generation (`sop-task-generator`)
4. **Step 5**: Configure execution mode (AFK/Checkpoint/HITL)
5. **Step 6**: Launch `./loop.sh specs/{goal}/` in background

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

### Step 0: Validate SOP Prerequisites

- [ ] `specs/{feature}/discovery.md` exists → If missing: Execute `sop-discovery`
- [ ] `specs/{feature}/design/detailed-design.md` exists → If missing: Execute `sop-planning`
- [ ] `specs/{feature}/implementation/plan.md` + task files exist → If missing: Execute `sop-task-generator`

**You MUST NOT:**
- Skip discovery and use AGENTS.md as substitute
- Skip planning and improvise architecture
- Proceed if ANY prerequisite is missing

---

### Step 1: Detect Flow and Goal

**Use AskUserQuestion:**
```text
Question: "What type of flow do you need?"
Options:
- Forward: Build something new (feature, improvement, project)
- Reverse: Investigate something existing before modifying it
```

**You MUST NOT** proceed without knowing the flow type.

---

### Step 2A: Discovery (Forward)

```text
/sop-discovery goal="{goal}"
```
Output: `specs/{goal}/discovery.md` → Continue to Step 3.

---

### Step 2B: Reverse Investigation

```text
/sop-reverse artifact="{path}"
```
Ask user if continuing to Forward. If no → End.

---

### Step 3: Planning

```text
/sop-planning discovery_path="specs/{goal}/discovery.md"
```
Output: `specs/{goal}/design/detailed-design.md` → Continue to Step 4.

---

### Step 4: Task Generation

```text
/sop-task-generator input="specs/{goal}/design/detailed-design.md"
```
Output: `plan.md` + `.code-task.md` files → Continue to Step 5.

---

### Step 5: Configure Execution

| Question | Options |
|----------|---------|
| Supervision Mode | **AFK**: Fully autonomous (Recommended) / **Checkpoint**: Pause every N tasks / **HITL**: Active supervision |
| Checkpoint Interval | 3 / 5 / 10 tasks |
| Quality Level | **Production**: Tests+Types+Lint+Build (Recommended) / **Prototype**: Skip verifications / **Library**: All + coverage + docs |

Update `.ralph/config.sh` with selections. Details: [configuration-guide.md](references/configuration-guide.md)

---

### Step 6: Launch Execution

**Prerequisites checklist:**
- [ ] `specs/{goal}/implementation/plan.md` exists
- [ ] `.code-task.md` files exist
- [ ] `.ralph/config.sh` configured

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
2. **HITL Planning, AFK Execution** - Interactive planning, autonomous execution
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

*Version: 3.0.0 | Updated: 2026-01-28*
