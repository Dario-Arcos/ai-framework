---
name: ralph-loop
description: Use when executing large implementation plans autonomously, when context exhaustion is a concern, or when you need fresh context per task for quality implementation
---

# Ralph Loop

> **STOP. READ THIS SECTION FIRST.**
>
> This skill has **TWO PHASES**:
> 1. **PLANNING (HITL)** - Interactive session where YOU help plan
> 2. **EXECUTION** - Autonomous loop where YOU only MONITOR
>
> Planning is NON-NEGOTIABLE. Every goal goes through planning first.

---

## Table of Contents

- [Overview](#overview)
- [When to Use](#when-to-use)
- [When NOT to Use](#when-not-to-use)
- [Quick Reference](#quick-reference)
- [The Two Flows](#the-two-flows)
- [Phase 1: Planning](#phase-1-planning-hitl)
- [Phase 2: Execution](#phase-2-execution-autonomous)
- [Installation](#installation)
- [Configuration](#configuration)
- [Files & Structure](#files--structure)
- [References](#references)

---

## Overview

Ralph Loop executes implementation plans autonomously with fresh 200K token context per iteration. Workers implement via TDD with quality gates while you monitor progress. Planning happens interactively; execution happens autonomously.

---

## When to Use

- Executing large implementation plans autonomously
- Context exhaustion is a concern (tasks > 100K tokens)
- Fresh context per task improves quality
- Multi-task implementation with TDD
- Overnight or AFK development needed

---

## When NOT to Use

| Situation | Why Not | Use Instead |
|-----------|---------|-------------|
| Simple tasks (<3 steps) | Overhead exceeds benefit | Direct implementation |
| Exploration/research | Requires interactivity | `sop-reverse` skill |
| Debugging | Needs conversation context | `systematic-debugging` skill |
| Code review | Not iterative | `requesting-code-review` skill |
| Projects without tests | Gates won't function | Set up tests first |
| Unclear requirements | Planning phase will fail | `sop-discovery` first |

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `./loop.sh specs/{goal}/` | Execute from specs (unlimited) |
| `./loop.sh specs/{goal}/ 20` | Execute with max 20 iterations |
| `./status.sh` | View current status & metrics |
| `./tail-logs.sh` | Real-time log following |
| `./memories.sh add pattern "..."` | Add persistent memory |

---

## The Two Flows

### Forward (Idea to Implementation)

```
Idea/Spec -> sop-discovery -> sop-planning -> sop-task-generator -> ralph-loop (execution)
```

Use when: You have an idea and want to build something new.

### Reverse (Existing Artifact to Specs)

```
Existing Artifact -> sop-reverse -> (generates specs) -> Forward Flow
```

Use when: You want to understand something existing before improving it. Investigates codebases, APIs, documentation, processes, or concepts.

---

## Phase 1: Planning (HITL)

**MANDATORY. No exceptions. No shortcuts.**

Planning uses SOP skills in the CURRENT interactive session:

| Skill | Purpose | Output |
|-------|---------|--------|
| `sop-discovery` | Constraints, risks, prior art | `specs/{goal}/discovery.md` |
| `sop-planning` | Requirements, research, design | `specs/{goal}/design/detailed-design.md` |
| `sop-task-generator` | Implementation plan | `specs/{goal}/implementation/plan.md` |
| `sop-reverse` | Investigate existing artifacts | `specs/{investigation}/specs-generated/` |

### Planning Rules

- **ONE question at a time** - Never batch questions
- **Wait for response** - Do not proceed without confirmation
- **Document everything** - All Q&A goes into specs
- **User decides** - You propose options, user chooses

### After Planning: Configure Execution

Ask the user:
- **Mode**: 100% AFK | Checkpoint every N | Milestone checkpoints
- **Quality**: Prototype | Production | Library

Wait for explicit selection before launching.

---

## Phase 2: Execution (Autonomous)

**Your role: MONITOR ONLY.** See [references/monitoring-pattern.md](references/monitoring-pattern.md).

### Allowed Actions

```python
Bash("./loop.sh specs/{goal}/", run_in_background=True)  # Start
TaskOutput(task_id, block=False)  # Check progress
Read("status.json")               # Read state
Read("logs/*")                    # Read logs
```

### Forbidden Actions

- ANY Write/Edit to ANY file
- ANY Bash that modifies state
- Task tool for implementation
- Research tools (workers research if needed)

### If User Asks to Implement

*"This session monitors ralph-loop. Workers have fresh 200K token context - 10x better for implementation. Want me to update the plan and restart?"*

See [references/red-flags.md](references/red-flags.md) for common mistakes.

---

## Installation

```bash
# From your project root (must have .git/)
/path/to/skills/ralph-loop/scripts/install.sh
```

**Prerequisites**: Existing git repo, validation commands (tests, lint, build), SOP skills installed.

---

## Configuration

Configuration in `.ralph/config.sh`. See [references/configuration-guide.md](references/configuration-guide.md).

| Setting | Default | Description |
|---------|---------|-------------|
| `QUALITY_LEVEL` | `production` | prototype/production/library |
| `MAX_CONSECUTIVE_FAILURES` | `3` | Circuit breaker threshold |
| `MAX_TASK_ATTEMPTS` | `3` | Task abandonment threshold |
| `CONTEXT_LIMIT` | `200000` | Token limit |

### Quality Gates

See [references/quality-gates.md](references/quality-gates.md).

```bash
GATE_TEST="npm test"
GATE_TYPECHECK="npm run typecheck"
GATE_LINT="npm run lint"
GATE_BUILD="npm run build"
```

---

## Files & Structure

### Specs (from planning)

```
specs/{goal}/
├── discovery.md
├── design/detailed-design.md
└── implementation/plan.md
```

### Ralph Files

| File | Purpose |
|------|---------|
| `.ralph/config.sh` | Project configuration |
| `AGENTS.md` | Project context |
| `guardrails.md` | Error lessons (Signs) |
| `memories.md` | Persistent learnings |
| `status.json` | Current loop state |

See [references/memories-system.md](references/memories-system.md) for memory management.

---

## Core Principles

1. **Fresh Context Is Reliability** - Each iteration clears context
2. **Backpressure Over Prescription** - Gates reject bad work
3. **The Plan Is Disposable** - Regeneration costs one session
4. **Disk Is State, Git Is Memory** - Files are handoff mechanism
5. **Planning Is Non-Negotiable** - Every objective goes through planning

---

## References

| File | Content |
|------|---------|
| [monitoring-pattern.md](references/monitoring-pattern.md) | Dashboard, log reading, status checking |
| [memories-system.md](references/memories-system.md) | Persistent learnings system |
| [configuration-guide.md](references/configuration-guide.md) | All config options, exit codes |
| [red-flags.md](references/red-flags.md) | Common mistakes, rationalizations |
| [quality-gates.md](references/quality-gates.md) | Gate descriptions, TDD enforcement |
| [state-files.md](references/state-files.md) | Signs, Memories, Scratchpad |
| [supervision-modes.md](references/supervision-modes.md) | HITL vs AFK, Docker sandbox |
| [observability.md](references/observability.md) | Logs, metrics |
| [backpressure.md](references/backpressure.md) | Task sizing, quality levels |

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| `sop-discovery` | Brainstorm constraints before planning |
| `sop-planning` | Create detailed requirements and design |
| `sop-task-generator` | Generate implementation tasks |
| `sop-reverse` | Investigate existing artifacts |

---

*Part of the SOP framework: sop-reverse -> sop-discovery -> sop-planning -> sop-task-generator -> ralph-loop*
