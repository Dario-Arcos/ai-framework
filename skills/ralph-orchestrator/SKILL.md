---
name: ralph-orchestrator
description: Use when building features requiring planning + autonomous execution. Triggers on multi-step implementations, overnight development, or when parallel ephemeral teammates with fresh 200K context improve quality. Orchestrates SOP skills (referent discovery, planning, task-generation) then launches Agent Teams cockpit.
---

# Ralph Orchestrator

> **SINGLE ENTRY POINT.** One invocation orchestrates everything.
> DO NOT invoke SOP skills separately — Ralph invokes them in sequence.

## Overview

- **Planning**: Interactive OR autonomous (user chooses)
- **Execution**: ALWAYS autonomous — Agent Teams in same session (tmux recommended for cockpit)

## Parameters

- **goal** (optional): High-level description. Asked in Step 1 if not provided.
- **planning_mode** (optional): `interactive` (default) or `autonomous`.

## Output

- Artifacts from sop-reverse, sop-planning, sop-task-generator in `.ralph/specs/{goal}/`
- Autonomous execution via Agent Teams — progress in `TaskList`, metrics in `.ralph/metrics.json`

**{goal} derivation:** Slugify `goal_description` to kebab-case (lowercase, spaces to hyphens, remove special chars, max 50 chars). Example: 'Add Real-Time Collaboration' becomes `add-real-time-collaboration`. All SOP skills MUST use this same derivation for pipeline continuity.

## The Complete Flow

1. **State Detection**: Scan .ralph/specs/, detect phase, offer resume or new
2. **Step 0**: Choose planning mode (Interactive/Autonomous)
3. **Step 1**: Validate prerequisites
4. **Step 2**: Referent Discovery (`sop-reverse referent`)
5. **Step 3-4**: Planning (`sop-planning`) + Task generation (`sop-task-generator`)
6. **Step 5**: Generate AGENTS.md (bootstrap teammate context)
7. **Step 6**: Plan Review Checkpoint (mandatory before execution)
8. **Step 7**: Configure execution (quality gates, cockpit services, checkpoints)
9. **Step 8**: Execute via Agent Teams (plan mode pre-flight → spawn teammates)

---

## Steps

### Infrastructure Setup

**Planning prerequisites (required now):**
- [ ] `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in environment
- [ ] `.ralph/config.sh` exists — if missing: copy from `templates/config.sh.template`
- [ ] `.ralph/guardrails.md` exists — if missing: copy from `templates/guardrails.md.template`

**Execution prerequisites (required for Step 8):**
- [ ] `tmux` installed (`which tmux`) — **Recommended (default teammate mode)**
  - If missing: **Use AskUserQuestion**:
    Question: "tmux no esta instalado. Es el modo recomendado para Agent Teams (split-panes para cada teammate, cockpit de servicios). Sin el, los teammates corren como sub-agentes in-process (menos visibilidad). Quieres instalarlo?"
    Header: "tmux"
    Options:
    - Instalar ahora (Recommended): Ejecuta brew install tmux (macOS) / sudo apt install tmux (Linux)
    - Continuar sin tmux: Modo in-process (teammates como sub-agentes, sin split-panes ni cockpit)

**Recommended (cockpit viewer):**
- [ ] Ghostty (macOS) — terminal dedicada para visualizar e intervenir en el cockpit
  - If missing: **Use AskUserQuestion**:
    Question: "Ghostty no esta instalado. Sin el, el cockpit se abrira en tu terminal actual (puede quedar 'atrapada' si estas en un IDE). Altamente recomendado para visualizar e intervenir."
    Header: "Ghostty"
    Options:
    - Instalar ahora (Recommended): Ejecuta brew install --cask ghostty
    - Continuar sin Ghostty: El cockpit corre en tmux. Conectate manualmente con `tmux attach -t ralph-{goal}` desde una terminal externa.

**Teammate mode** (automatic — no user input):
- tmux installed → teammates use split-panes, cockpit service windows available
- tmux NOT installed → teammates run in-process (sub-agents, no cockpit)

**You MUST** verify planning prerequisites before planning. **You MUST NOT** proceed to Step 8 without execution prerequisites.

> Error handling: [troubleshooting.md](references/troubleshooting.md)

### State Detection

Scan `.ralph/specs/` for existing goals. For each (or `$ARGUMENTS` if provided), check artifacts:

| Artifact | Detected Phase |
|----------|----------------|
| All `*.code-task.md` with `Status: COMPLETED` | COMPLETE |
| Any `*.code-task.md` with `Status: PENDING` | execution (Step 8) |
| `implementation/plan.md` without task files | task-generator (Step 4) |
| `design/detailed-design.md` | planning (Step 3) |
| `referents/catalog.md` | referent-complete (Step 3) |
| Nothing | NEW |

**Use AskUserQuestion** to confirm: resume from detected phase, or choose goal if multiple. Surface `blockers.md` content if exists. After confirmation, skip to detected phase.

### Convergence Model
The SOP pipeline (referent discovery → planning → task-gen → execution) is conceptually a
**convergence loop**, not a linear waterfall:
- If execution reveals design gaps → loop back to planning
- If planning reveals unknown risks → loop back to referent discovery
- The State Detection table enables re-entry at any phase
- Convergence = all .code-task.md files reach Status: COMPLETED with scenarios satisfied

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

### Step 1: Validate Prerequisites

- [ ] `.ralph/specs/{goal}/referents/catalog.md` exists — If missing: Execute `sop-reverse` in referent mode (Step 2)
- [ ] `.ralph/specs/{goal}/design/detailed-design.md` exists — If missing: Execute `sop-planning`
- [ ] `.ralph/specs/{goal}/implementation/plan.md` + task files exist — If missing: Execute `sop-task-generator`

**You MUST NOT** skip referent discovery, skip planning, or proceed with missing prerequisites.

### Step 2: Referent Discovery

```
/sop-reverse target="{concept}" search_mode="referent" output_dir=".ralph/specs/{goal}" mode={PLANNING_MODE}
```

Output: `.ralph/specs/{goal}/referents/` catalog — Continue to Step 3 with referent patterns as planning input.

### Step 3: Planning

```
/sop-planning rough_idea="{goal}" discovery_path=".ralph/specs/{goal}/referents/catalog.md" project_dir=".ralph/specs/{goal}" mode={PLANNING_MODE}
```

sop-planning reads `extracted-patterns.md` from the `referents/` directory when `discovery_path` points within it. Verified: sop-planning Step 1 constraint.

Output: `.ralph/specs/{goal}/design/detailed-design.md` — Continue to Step 4.

### Step 4: Task Generation

```
/sop-task-generator input=".ralph/specs/{goal}/implementation/plan.md" mode={PLANNING_MODE}
```

Output: `plan.md` + `.code-task.md` files — Continue to Step 5.

### Step 5: Generate AGENTS.md

Populate `templates/AGENTS.md.template` with operational context for teammates.

**Sources:** `.ralph/specs/{goal}/referents/catalog.md` (constraints, recommendation), `.ralph/specs/{goal}/referents/extracted-patterns.md` (patterns to adopt), `.ralph/specs/{goal}/design/detailed-design.md` (architecture, data models), manifest files (commands), `.ralph/config.sh` (quality).

**Population instructions:**
1. **Stack**: Extract the complete Technology Stack table from `detailed-design.md` Section 3.4. Include ALL rows. This is the authoritative technology reference.
2. **Design Reference**: Generate a compressed index of `detailed-design.md` — list section headers (§3.1 System Context, §5 Data Models, etc.) with a 1-line summary each. Include the full path to the design file.
3. **Constraints**: Extract the Recommendation and key constraints from `referents/catalog.md`.
4. **Patterns**: Extract pattern names and 1-line descriptions from `referents/extracted-patterns.md`.

- **Interactive**: Present draft, ask for approval/edits via AskUserQuestion.
- **Autonomous**: Use Explore subagent to extract from sources. Generate without blocking.

**Output:** `.ralph/agents.md` — Continue to Step 6.

### Step 6: Plan Review Checkpoint

**MANDATORY before execution, regardless of planning mode.**

Present to user: planning mode used, artifacts generated (referent catalog, design, N task files, `.ralph/agents.md`), key decisions from design document, blockers found, task summary by step with complexity.

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

**Use AskUserQuestion (1 question):**

| Question | Options |
|----------|---------|
| Checkpoints | **None** (Recommended) / Every N tasks |

**Derive quality gates from Technology Stack** in `detailed-design.md` Section 3.4 (automatic — no user input). Read `.ralph/config.sh` and populate all `GATE_*` variables for the chosen technologies:

| Config Variable | Derived From |
|-----------------|-------------|
| `GATE_TEST` | Unit Testing technology |
| `GATE_COVERAGE` | Unit Testing technology + coverage flag |
| `GATE_TYPECHECK` | Language toolchain (empty for compiled languages) |
| `GATE_LINT` | Language linter |
| `GATE_BUILD` | Build/bundling tool (empty if none) |

Empty string = gate skipped. See `.ralph/config.sh` comments for stack-specific examples.

**Configure cockpit services** — prompt user for optional commands:

| Service | Example | Config Variable |
|---------|---------|-----------------|
| Dev server | `npm run dev` | `COCKPIT_DEV_SERVER` |
| Test watcher | `npm run test:watch` | `COCKPIT_TEST_WATCHER` |
| Logs | `tail -f logs/*.log` | `COCKPIT_LOGS` |
| Database | `docker-compose up -d postgres` | `COCKPIT_DB` |

Update `.ralph/config.sh` with derived gates and user selections. See [configuration-guide.md](references/configuration-guide.md) for all options.

### Step 8: Execute via Agent Teams

**Prerequisites (all must be true):**
- `.ralph/specs/{goal}/implementation/plan.md` + `.code-task.md` files with `Status: PENDING`
- `.ralph/agents.md` exists, Plan Review passed (Step 6)
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` set

**Pre-flight (Plan Mode):**

1. Call `EnterPlanMode` — restricts session to read-only, preventing accidental edits.
2. Build execution plan (read-only):
   a. Read all `.code-task.md` files from `.ralph/specs/{goal}/implementation/`
   b. Map dependencies: parse `Blocked-By` references from each `.code-task.md`
   c. Determine teammate mode: tmux if installed, in-process otherwise
   d. If tmux available and COCKPIT_* services configured: note service windows to create
   e. Summarize: N tasks, dependency graph, teammate mode, quality gates from config.sh
3. Write execution plan to plan file (task list, dependencies, teammate mode, gates).
4. Call `ExitPlanMode` — user approves the execution plan.

**Launch (after plan approval):**

1. If tmux available and COCKPIT_* services configured:
   - Copy `templates/launch-build.sh.template` to `.ralph/launch-build.sh`, `chmod +x`
   - Launch: `Bash(command="bash .ralph/launch-build.sh", run_in_background=true)`
   - This creates ONLY service windows (dev server, test watcher, logs, DB) — NOT a Claude Code instance
2. `TeamCreate(team_name="ralph-{goal-slug}")`
3. For each `.code-task.md`: `TaskCreate` with full file content as description, `metadata={codeTaskFile: path, codeTaskStep: N}`
4. Build dependency mapping: `.code-task.md` `Blocked-By` references → Agent Teams taskIds via metadata lookup
5. `TaskUpdate(addBlockedBy=[...])` for each task with dependencies
6. For each unblocked PENDING task (up to MAX_TEAMMATES): spawn implementer teammate
   ```python
   Task(
       subagent_type="general-purpose",
       team_name="ralph-{goal-slug}",
       name="impl-{task-slug}",
       mode="bypassPermissions",
       prompt=PROMPT_implementer.md content + "\n\nYour assigned task ID: {taskId}"
   )
   ```
7. Enter monitoring mode

> If tmux NOT available: teammates run in-process (sub-agents). No cockpit service windows. Execution works — less visibility.

> Architecture details: [agent-teams-architecture.md](references/agent-teams-architecture.md)

---

## Phase 2: Monitoring

**Role: PURE ORCHESTRATOR.** Lead coordinates via summaries only — never reads code, diffs, or full review content.

**Tools allowed:**
- `TaskList` — task progress
- `TaskGet(taskId)` — read task metadata (codeTaskFile, codeTaskStep)
- `Read(".ralph/guardrails.md")` — lessons accumulated by teammates
- `Read(".ralph/metrics.json")` — success/failure counts
- `Read(".ralph/failures.json")` — per-teammate failure tracking
- `SendMessage` — direct instructions to specific teammates

**If user asks to implement:** Redirect to teammates. Lead coordinates, doesn't implement.

**State machine — Implementer → Reviewer → Next cycle:**

WHEN implementer goes idle — read 8-word summary from SendMessage:

IF summary starts with "BLOCKED:":
1. Send `shutdown_request` to the implementer
2. Read `{documentation_dir}/blockers.md` (path from task metadata: `.ralph/specs/{goal}/implementation/{task_name}/blockers.md`)
3. Surface blocker content to user via text output. Do NOT spawn reviewer — wait for blocker resolution.

OTHERWISE (task completed, gates passed):
1. Send `shutdown_request` to the implementer
2. Spawn a reviewer teammate for the completed task:
   ```python
   Task(
       subagent_type="general-purpose",
       team_name="ralph-{goal-slug}",
       name="rev-{task-slug}",
       mode="bypassPermissions",
       prompt=PROMPT_reviewer.md content + "\n\nYour assigned task ID: {taskId}\nTask file: {path_to_code_task_md}"
   )
   ```

WHEN reviewer goes idle — read 8-word summary from SendMessage:
3. Send `shutdown_request` to the reviewer
4. IF PASS: Mark `.code-task.md` as COMPLETED → `TaskList` for newly unblocked tasks → spawn next implementer if unblocked tasks exist
5. IF FAIL: Spawn NEW implementer for the same task with review feedback:
   ```python
   Task(
       subagent_type="general-purpose",
       team_name="ralph-{goal-slug}",
       name="impl-{task-slug}-r2",
       mode="bypassPermissions",
       prompt=PROMPT_implementer.md content + "\n\nYour assigned task ID: {taskId}\nReview feedback: .ralph/reviews/task-{taskId}-review.md"
   )
   ```
6. IF BLOCKED: Read `.ralph/reviews/task-{taskId}-blockers.md`. Surface blocker to user via text output. Do NOT spawn new teammate until blocker resolved.

**Completion flow:**
1. All tasks complete — all reviewers report PASS
2. Lead verifies: all `.code-task.md` files have `Status: COMPLETED`
3. Lead sends `shutdown_request` to any remaining teammates
4. `TeamDelete` cleans up team resources
5. Inform user: "Ejecucion completa. {N} tasks completadas. {metrics summary}."

> Guardrail enforcement: [backpressure.md](references/backpressure.md)

---

## Core Principles

1. **Single Entry Point** — Invoke once, orchestrate everything. Never invoke SOP skills directly.
2. **Checkpoint Before Execution** — Planning can be interactive OR autonomous, but user ALWAYS approves before execution begins.
3. **Fresh Context + Guardrails = Compounding Intelligence** — Each teammate gets fresh 200K context for a single task. `guardrails.md` accumulates lessons across all tasks. Each completed task feeds learnings into the next. Quality gates (TaskCompleted hook) enforce standards. Reviewer teammates validate SDD compliance after automated gates pass.
4. **Disk Is State, Git Is Memory** — `.code-task.md` files are the task contract. `guardrails.md` is shared memory. Git commits are checkpoints. If a teammate crashes, its task file persists for the next one.

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
| `sop-reverse` | 2 | Referent discovery |
| `sop-planning` | 3 | Research, design |
| `sop-task-generator` | 4 | Task files |
| `sop-code-assist` | Teammates | SDD implementation |
