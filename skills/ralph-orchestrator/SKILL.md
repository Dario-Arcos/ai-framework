---
name: ralph-orchestrator
description: Use when building features requiring planning + autonomous execution. Triggers on multi-step implementations, overnight development, or when parallel teammates with persistent context improve quality. Orchestrates SOP skills (discovery, planning, task-generation) then launches Agent Teams cockpit.
---

# Ralph Orchestrator

> **SINGLE ENTRY POINT.** One invocation orchestrates everything.
> DO NOT invoke SOP skills separately — Ralph invokes them in sequence.

## Overview

- **Planning**: Interactive OR autonomous (user chooses)
- **Execution**: ALWAYS autonomous — Agent Teams cockpit (Ghostty + tmux)

## When to Use

- New features or projects requiring multi-task implementation
- Large implementation plans with parallelizable work
- Overnight/AFK development with quality gates

## When NOT to Use

| Situation | Use Instead |
|-----------|-------------|
| Simple single-file change | Direct implementation |
| Only debugging | `systematic-debugging` skill |
| Only code review | `code-reviewer` agent or `pull-request` skill |
| Research only, no implementation | `sop-reverse` alone |

## Parameters

- **goal** (optional): High-level description. Asked in Step 1 if not provided.
- **flow** (optional, default: `"forward"`): `forward` (new) or `reverse` (investigate existing).
- **planning_mode** (optional): `interactive` (default) or `autonomous`.

## Output

- Artifacts from sop-discovery, sop-planning, sop-task-generator in `specs/{goal}/`
- Autonomous execution via Agent Teams — progress in `TaskList`, metrics in `.ralph/metrics.json`

## The Complete Flow

1. **State Detection**: Scan specs/, detect phase, offer resume or new
2. **Step 0**: Choose planning mode (Interactive/Autonomous)
3. **Step 1**: Validate prerequisites + detect flow (Forward/Reverse)
4. **Step 2**: Discovery (`sop-discovery`) OR Investigation (`sop-reverse`)
5. **Step 3-4**: Planning (`sop-planning`) + Task generation (`sop-task-generator`)
6. **Step 5**: Generate AGENTS.md (bootstrap teammate context)
7. **Step 6**: Plan Review Checkpoint (mandatory before execution)
8. **Step 7**: Configure execution (quality level, cockpit services, checkpoints)
9. **Step 8**: Launch Agent Teams cockpit

---

## Steps

### Infrastructure Setup

**Required before planning. Verified automatically, not by retrieval.**

- [ ] `tmux` installed (`which tmux` — if missing: `brew install tmux`)
- [ ] `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in environment
- [ ] Ghostty available (macOS: `open -na Ghostty.app` — if missing: `brew install --cask ghostty`)
- [ ] `.ralph/config.sh` exists — if missing: copy from `templates/config.sh.template`
- [ ] `guardrails.md` exists in project root — if missing: copy from `templates/guardrails.md.template`

**You MUST** verify all prerequisites before planning. **You MUST NOT** proceed if any are missing.

> Error handling: [troubleshooting.md](references/troubleshooting.md)

### State Detection

Scan `specs/` for existing goals. For each (or `$ARGUMENTS` if provided), check artifacts:

| Artifact | Detected Phase |
|----------|----------------|
| All `*.code-task.md` with `Status: COMPLETED` | COMPLETE |
| Any `*.code-task.md` with `Status: PENDING` | execution (Step 8) |
| `implementation/plan.md` without task files | task-generator (Step 4) |
| `design/detailed-design.md` | planning (Step 3) |
| `discovery.md` | discovery-complete (Step 3) |
| `investigation.md` + `specs-generated/` | reverse-complete (Step 3) |
| Nothing | NEW |

**Use AskUserQuestion** to confirm: resume from detected phase, choose goal if multiple, choose flow if NEW. Surface `blockers.md` content if exists. After confirmation, skip to detected phase.

### Step 0: Choose Planning Mode

**Use AskUserQuestion:**
```text
Question: "Estaras presente durante la planificacion?"
Header: "Planning Mode"
Options:
- Interactive (Recommended): Te guiare paso a paso, preguntando sobre requisitos y diseno
- Autonomous: Planificare autonomamente. Revisaras el plan completo antes de ejecutar.
```

| Mode | SOP Skills Behavior |
|------|---------------------|
| **Interactive** | Ask questions, wait for answers, iterate with user |
| **Autonomous** | Make reasonable decisions, document rationale, continue without blocking |

Store as `PLANNING_MODE={interactive|autonomous}`. **You MUST NOT** proceed without explicit selection.

> Mode recommendations: [supervision-modes.md](references/supervision-modes.md)

### Step 1: Validate Prerequisites and Detect Flow

- [ ] `specs/{goal}/discovery.md` exists — If missing: Execute `sop-discovery`
- [ ] `specs/{goal}/design/detailed-design.md` exists — If missing: Execute `sop-planning`
- [ ] `specs/{goal}/implementation/plan.md` + task files exist — If missing: Execute `sop-task-generator`

**Detect Flow (Use AskUserQuestion):** Forward (build new) or Reverse (investigate existing).

**You MUST NOT** skip discovery, skip planning, or proceed with missing prerequisites.

### Step 2A: Discovery (Forward)

```
/sop-discovery goal_description="{goal}" mode={PLANNING_MODE}
```

Output: `specs/{goal}/discovery.md` — Continue to Step 3.

### Step 2B: Reverse Investigation

```
/sop-reverse target="{path}" mode={PLANNING_MODE}
```

Ask user if continuing to Forward (interactive). In autonomous mode, continue by default.

### Step 3: Planning

```
/sop-planning rough_idea="{goal}" discovery_path="specs/{goal}/discovery.md" project_dir="specs/{goal}" mode={PLANNING_MODE}
```

Output: `specs/{goal}/design/detailed-design.md` — Continue to Step 4.

### Step 4: Task Generation

```
/sop-task-generator input="specs/{goal}/implementation/plan.md" mode={PLANNING_MODE}
```

Output: `plan.md` + `.code-task.md` files — Continue to Step 5.

### Step 5: Generate AGENTS.md

Populate `templates/AGENTS.md.template` with operational context for teammates.

**Sources:** `specs/{goal}/discovery.md` (constraints, risks), `specs/{goal}/design/detailed-design.md` (architecture), manifest files (commands), `.ralph/config.sh` (quality).

- **Interactive**: Present draft, ask for approval/edits via AskUserQuestion.
- **Autonomous**: Use Explore subagent to extract from sources. Generate without blocking.

**Output:** `AGENTS.md` in project root — Continue to Step 6.

### Step 6: Plan Review Checkpoint

**MANDATORY before execution, regardless of planning mode.**

Present to user: planning mode used, artifacts generated (discovery, design, N task files, AGENTS.md), key decisions from design document, blockers found, task summary by step with complexity.

**Use AskUserQuestion:**
```text
Question: "Aprobar plan y continuar a ejecucion?"
Options:
- Aprobar y continuar: Proceder a configurar ejecucion
- Revisar artifacts: Mostrar contenido de artifacts antes de decidir
- Rehacer planificacion: Volver a Step 2 con modo interactivo
```

**You MUST NOT** skip this checkpoint, launch without approval, or proceed if user requests review.

### Step 7: Configure Execution

**Use AskUserQuestion (2 questions):**

| Question | Options |
|----------|---------|
| Quality Level | **Production** (Recommended) / Prototype / Library |
| Checkpoints | **None** (Recommended) / Every N tasks |

**Configure cockpit services** — prompt user for optional commands:

| Service | Example | Config Variable |
|---------|---------|-----------------|
| Dev server | `npm run dev` | `COCKPIT_DEV_SERVER` |
| Test watcher | `npm run test:watch` | `COCKPIT_TEST_WATCHER` |
| Logs | `tail -f logs/*.log` | `COCKPIT_LOGS` |
| Database | `docker-compose up -d postgres` | `COCKPIT_DB` |

Update `.ralph/config.sh`. See [configuration-guide.md](references/configuration-guide.md) for all options.

### Step 8: Launch Execution

**Prerequisites (all must be true):**
- `specs/{goal}/implementation/plan.md` + `.code-task.md` files with `Status: PENDING`
- `AGENTS.md` in project root, Plan Review passed (Step 6)
- `tmux` installed, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` set

**Actions:**

1. Copy `templates/launch-build.sh.template` to `.ralph/launch-build.sh`, `chmod +x`
2. Launch: `Bash(command="bash .ralph/launch-build.sh")`
3. Inform user: "Cockpit lanzado en Ghostty. `team` (Ctrl+B 0): Lead + teammates, `services` (Ctrl+B 1): Dev server + DB, `quality` (Ctrl+B 2): Test watcher, `monitor` (Ctrl+B 3): Logs, `shell` (Ctrl+B 4): Terminal libre."

**In the Ghostty session** (automatic via launch-build.sh):
1. Claude Code starts with `--teammate-mode tmux`
2. `/ralph-orchestrator` auto-invoked — state detection routes to Step 8 continuation
3. `TeamCreate(team_name="ralph-{goal-slug}")`
4. For each `.code-task.md`: `TaskCreate` + `TaskUpdate(addBlockedBy=[...])` per `Blocked-By` field
5. Spawn teammates (up to MAX_TEAMMATES) with `scripts/PROMPT_teammate.md`
6. Enter monitoring mode (Phase 2)

> Architecture details: [agent-teams-architecture.md](references/agent-teams-architecture.md)

---

## Phase 2: Monitoring

**Role: MONITOR ONLY.** Lead in delegate mode — coordination tools only. No Write/Edit. No implement.

**Tools allowed:**
- `TaskList` — task progress
- `Read("guardrails.md")` — lessons accumulated by teammates
- `Read(".ralph/metrics.json")` — success/failure counts
- `Read(".ralph/failures.json")` — per-teammate failure tracking
- `SendMessage` — direct instructions to specific teammates

**If user asks to implement:** Redirect to teammates. Lead coordinates, doesn't implement.

**Completion flow:**
1. All tasks complete — teammates go idle (TeammateIdle hook allows it)
2. Lead verifies: all `.code-task.md` files have `Status: COMPLETED`
3. Lead sends `shutdown_request` to each teammate
4. `TeamDelete` cleans up team resources
5. Inform user: "Ejecucion completa. {N} tasks completadas. {metrics summary}."

> Guardrail enforcement: [backpressure.md](references/backpressure.md)

---

## Core Principles

1. **Single Entry Point** — Invoke once, orchestrate everything. Never invoke SOP skills directly.
2. **Checkpoint Before Execution** — Planning can be interactive OR autonomous, but user ALWAYS approves before execution begins.
3. **Fresh Context + Guardrails = Compounding Intelligence** — Teammates coordinate; sub-agents implement with fresh 200K context per task. `guardrails.md` accumulates lessons across all tasks and teammates. Each completed task feeds learnings into the next. Quality gates (TaskCompleted hook) enforce standards. Persistent coordinator context + fresh implementation context = consistent quality at any task count.
4. **Disk Is State, Git Is Memory** — `.code-task.md` files are the handoff mechanism. `guardrails.md` is shared memory. Git commits are checkpoints. If a teammate crashes, its task file persists for the next one.

---

## References

| File | Description |
|------|-------------|
| [configuration-guide.md](references/configuration-guide.md) | All config options and defaults |
| [execution-paths.md](references/execution-paths.md) | Agent Teams execution model |
| [agent-teams-architecture.md](references/agent-teams-architecture.md) | Cockpit architecture, hooks, tmux layout |
| [supervision-modes.md](references/supervision-modes.md) | Planning modes, checkpoint behavior |
| [quality-gates.md](references/quality-gates.md) | Gate descriptions, SDD enforcement |
| [sop-integration.md](references/sop-integration.md) | How SOP skills connect |
| [state-files.md](references/state-files.md) | File purposes and lifecycle |
| [memories-system.md](references/memories-system.md) | Memory architecture |
| [backpressure.md](references/backpressure.md) | Circuit breakers, task sizing |
| [mode-selection.md](references/mode-selection.md) | Decision flowcharts |
| [observability.md](references/observability.md) | Metrics, debugging |
| [red-flags.md](references/red-flags.md) | Dangerous thought patterns |
| [alternative-loops.md](references/alternative-loops.md) | Specialized loop patterns |
| [pressure-testing.md](references/pressure-testing.md) | Adversarial scenarios |
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
| `sop-code-assist` | Teammates | SDD implementation |
