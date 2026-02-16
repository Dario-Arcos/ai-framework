---
name: ralph-orchestrator
description: Use when building features requiring planning + autonomous execution. Triggers on multi-step implementations, overnight development, or when parallel ephemeral teammates with fresh 200K context improve quality. Orchestrates SOP skills (referent discovery, planning, task-generation) then launches Agent Teams.
---

# Ralph Orchestrator

> **SINGLE ENTRY POINT.** One invocation orchestrates everything.
> DO NOT invoke SOP skills separately — Ralph invokes them in sequence.

## Overview

- **Planning**: Interactive OR autonomous (user chooses)
- **Execution**: ALWAYS autonomous — Agent Teams in same session

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
7. **Step 6**: Configure execution (quality gates)
8. **Step 7**: Execute via Agent Teams (plan mode pre-flight → spawn teammates)

---

## Steps

### Infrastructure Setup

**Planning prerequisites (required now):**
- [ ] `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in environment
- [ ] `.ralph/config.sh` exists — if missing: copy from `templates/config.sh.template`
- [ ] `.ralph/guardrails.md` exists — if missing: copy from `templates/guardrails.md.template`

**Teammate mode**: always in-process.

> Error handling: [troubleshooting.md](references/troubleshooting.md)

### State Detection

Scan `.ralph/specs/` for existing goals. For each (or `$ARGUMENTS` if provided), check artifacts:

| Artifact | Detected Phase |
|----------|----------------|
| All `*.code-task.md` with `Status: COMPLETED` | COMPLETE |
| Any `*.code-task.md` with `Status: IN_REVIEW` | execution (Step 7) |
| Any `*.code-task.md` with `Status: PENDING` | execution (Step 7) |
| `implementation/plan.md` without task files | task-generator (Step 4) |
| `design/detailed-design.md` | planning-complete (Step 4) |
| `referents/catalog.md` | referent-complete (Step 3) |
| Nothing | NEW |

**Use AskUserQuestion** to confirm: resume from detected phase, or choose goal if multiple. Surface `blockers.md` content if exists.

### Convergence Model
The SOP pipeline is a **convergence loop**, not a linear waterfall:
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

Output: `.ralph/specs/{goal}/referents/` catalog — Continue to Step 3.

### Step 3: Planning

```
/sop-planning rough_idea="{goal}" discovery_path=".ralph/specs/{goal}/referents/catalog.md" project_dir=".ralph/specs/{goal}" mode={PLANNING_MODE}
```

sop-planning reads `extracted-patterns.md` from `referents/` when `discovery_path` points within it.

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

### Step 6: Configure Execution

**Use AskUserQuestion (1 question):**

| Question | Options |
|----------|---------|
| Checkpoints | **None** (Recommended) / Every N tasks |

**Derive quality gates from Technology Stack** in `detailed-design.md` Section 3.4 (automatic — no user input). Read `.ralph/config.sh` and populate all `GATE_*` variables for the chosen technologies:

| Config Variable | Derived From |
|-----------------|-------------|
| `GATE_TEST` | Unit Testing technology |
| `GATE_TYPECHECK` | Language toolchain (empty for compiled languages) |
| `GATE_LINT` | Language linter |
| `GATE_BUILD` | Build/bundling tool (empty if none) |
| `GATE_INTEGRATION` | Integration Testing technology (empty if none) |
| `GATE_E2E` | E2E technology (empty if none) |

Empty string = gate skipped. Integration and E2E gates run after build and are skipped for `Scenario-Strategy: not-applicable` tasks. See `.ralph/config.sh` comments for stack-specific examples.

**You MUST NOT** use exit code suppression in gate commands. The following patterns defeat quality gates and are rejected at runtime:
- `|| true`, `; true`, `|| :`, `; :`, `|| exit 0`, `; exit 0` — forces exit 0 regardless of test result
- `2>&1 || true` — redirects output AND suppresses failure
- For multi-package projects, use `&&` to chain commands: `cmd1 && cmd2` (propagates first failure)

**Supplementary gate (evaluated after the 4 standard gates by the TaskCompleted hook):**

| Config Variable | Derived From |
|-----------------|-------------|
| `GATE_COVERAGE` | Unit Testing technology + coverage flag |

GATE_COVERAGE requires `MIN_TEST_COVERAGE > 0` and a non-empty `GATE_COVERAGE` command in config.sh.

Update `.ralph/config.sh` with derived gates and user selections. See [configuration-guide.md](references/configuration-guide.md) for all options.

### Step 7: Execute via Agent Teams

**Prerequisites (all must be true):**
- `.ralph/specs/{goal}/implementation/plan.md` + `.code-task.md` files with `Status: PENDING`
- `.ralph/agents.md` exists
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` set

**Pre-flight (Plan Mode):**

1. Call `EnterPlanMode` — restricts session to read-only.
2. Build execution plan (read-only):
   a. Read all `.code-task.md` files from `.ralph/specs/{goal}/implementation/`
   b. Map dependencies: parse `Blocked-By` references from each `.code-task.md`
   c. Detect file overlap between parallelizable tasks:
      1. For each `.code-task.md`, extract the `Files to Modify` list from Metadata
      2. Identify parallelizable groups: tasks with no `Blocked-By` relationship between them
      3. Within each group, check if any two tasks share one or more files
      4. If overlap detected: add `Blocked-By` from the lower-step task to the higher-step one (serialize them)
      5. Report in Execution Strategy: "File overlap: Task {Y} waits for Task {X} (shared: {file})"
   d. Read `.ralph/config.sh` for quality gates, MAX_TEAMMATES, and MODEL
   e. Determine parallelism: calculate max parallelizable tasks from dependency graph (including overlaps from 2c). Cap at 3. **Use AskUserQuestion**:
      - Question: "¿Cuantos teammates quieres ejecutar en paralelo?"
      - Header: "Paralelismo"
      - Options (calculate dynamically, all capped at 3):
        - "{recommended} (Recomendado)": min(parallelizable_count, 3) teammates — {parallelizable_count} tasks parallelizables de {total_tasks} totales.
        - "1": Ejecucion secuencial — mas lenta pero menor consumo de API.
        - "2": Dos teammates en paralelo — equilibrio entre velocidad y consumo.
      - The user's choice overrides MAX_TEAMMATES from config.sh for this execution. Hard cap: 3.
   f. Resolve absolute paths for these ralph-orchestrator plugin files:
      - `templates/execution-runbook.md.template`
      - `scripts/PROMPT_implementer.md`
      - `scripts/PROMPT_reviewer.md`
3. Write execution plan to plan file with FOUR sections:
   a. **Planning Summary** (for human review — mandatory, regardless of planning mode):
      Present to user: planning mode used, artifacts generated (referent catalog,
      design, N task files, `.ralph/agents.md`), key decisions from design document,
      blockers found, task summary by step with complexity.
      Include paths to all artifacts so the user can inspect them.
      Include note: "To redo planning: reject this plan with 'rehacer'.
      To review specific artifacts before approving: reject with 'revisar {artifact}'."
   b. **Execution Strategy** (for human review): N tasks, dependency graph,
      quality gates, file overlap resolution
   c. **Execution Data** (concrete values — drives runbook generation after approval):
      - Team name: `ralph-{concrete-goal-slug}`
      - MAX_TEAMMATES: {user's choice from step 2e, or config.sh default if skipped}
      - MODEL: {value from config.sh}
      - Task Registry table: `| Step | File (absolute path) | Blocked-By | Title |`
      - Quality Gates table: `| Gate | Command |` (non-empty gates only)
      - File Paths (absolute): runbook template, implementer prompt, reviewer prompt
      - Goal directory: `.ralph/specs/{goal}`
   d. **Post-Approval Directive** (MUST be last section — survives context compression):
      ```
      ## Post-Approval Execution
      After this plan is approved, IMMEDIATELY:
      1. Generate execution runbook:
         - Read runbook template from: {absolute_template_path}
         - Read implementer prompt from: {absolute_implementer_prompt_path}
         - Read reviewer prompt from: {absolute_reviewer_prompt_path}
         - Populate ALL template sections with Execution Data values above
         - Section 7: inline FULL implementer prompt content
         - Section 8: inline FULL reviewer prompt content
         - Write populated runbook to: {goal_dir}/implementation/execution-runbook.md
      2. Read the generated execution-runbook.md
      3. Follow EVERY instruction in the runbook
      4. You are the ORCHESTRATOR — teammates implement, you coordinate
      ```
4. Call `ExitPlanMode` — user approves the execution plan.

**Launch (after plan approval):**

> Execute the Post-Approval Directive. Generate runbook first, then read and execute it.
> Runbook is the single source of truth — re-read if context compresses.
> See `templates/execution-runbook.md.template` for structure.

1. `TeamCreate(team_name="ralph-{goal-slug}")`
2. For each `.code-task.md`: `TaskCreate` with full file content as description, `metadata={codeTaskFile: path, codeTaskStep: N}`
3. Build dependency mapping: `.code-task.md` `Blocked-By` references → Agent Teams taskIds via metadata lookup
4. `TaskUpdate(addBlockedBy=[...])` for each task with dependencies
5. For each unblocked PENDING task (up to MAX_TEAMMATES): spawn implementer teammate
   ```python
   Task(
       subagent_type="general-purpose",
       team_name="ralph-{goal-slug}",
       name="impl-{task-slug}",
       mode="bypassPermissions",
       model="{model}",
       prompt=PROMPT_implementer.md content + "\n\nYour assigned task ID: {taskId}"
   )
   ```
6. Enter monitoring mode

> Architecture details: [agent-teams-architecture.md](references/agent-teams-architecture.md)

---

## Phase 2: Execution

**Role: PURE ORCHESTRATOR.** Never read code, diffs, or full review content — summaries only.

**Tools allowed:**
- `TaskList` — task progress
- `TaskGet(taskId)` — read task metadata (codeTaskFile, codeTaskStep)
- `Read(".ralph/guardrails.md")` — lessons accumulated by teammates
- `Read(".ralph/metrics.json")` — success/failure counts
- `Read(".ralph/failures.json")` — per-teammate failure tracking
- `SendMessage` — direct instructions to specific teammates

**If user asks to implement:** Redirect to teammates. Lead never implements.

**State machine — Pipeline parallelism (independent tasks overlap, dependent tasks wait for review):**

**Internal state:** Maintain `tasks_in_review` — a set of taskIds whose implementation completed but review has not yet passed. Initialized empty at launch.

**Launchable task rule:** A task is launchable when ALL of these are true:
1. Unblocked in Agent Teams (no pending `blockedBy`)
2. None of its original `blockedBy` dependencies are in `tasks_in_review`
3. Active teammates < MAX_TEAMMATES

WHEN implementer goes idle — read 8-word summary from SendMessage:

IF summary starts with "BLOCKED:":
1. Send `shutdown_request` to the implementer
2. Read `{documentation_dir}/blockers.md` (path from task metadata: `.ralph/specs/{goal}/implementation/{task_name}/blockers.md`)
3. Surface blocker content to user via text output. Do NOT spawn reviewer — wait for blocker resolution.

OTHERWISE (task completed, gates passed):
1. Send `shutdown_request` to the implementer
2. Add taskId to `tasks_in_review`
3. Spawn a reviewer teammate for the completed task:
   ```python
   Task(
       subagent_type="general-purpose",
       team_name="ralph-{goal-slug}",
       name="rev-{task-slug}",
       mode="bypassPermissions",
       model="{model}",
       prompt=PROMPT_reviewer.md content + "\n\nYour assigned task ID: {taskId}\nTask file: {path_to_code_task_md}"
   )
   ```
4. Check `TaskList` for launchable tasks. Spawn implementers up to MAX_TEAMMATES.

WHEN reviewer goes idle — read 8-word summary from SendMessage:
1. Send `shutdown_request` to the reviewer
2. IF PASS: Remove taskId from `tasks_in_review` → mark `.code-task.md` as COMPLETED → check `TaskList` for launchable tasks → spawn implementers up to MAX_TEAMMATES
3. IF FAIL: taskId stays in `tasks_in_review` → spawn NEW implementer with review feedback:
   ```python
   Task(
       subagent_type="general-purpose",
       team_name="ralph-{goal-slug}",
       name="impl-{task-slug}-r{N}",  # Increment N on each rework cycle: r2, r3, r4...
       mode="bypassPermissions",
       model="{model}",
       prompt=PROMPT_implementer.md content + "\n\nYour assigned task ID: {taskId}\nReview feedback: .ralph/reviews/task-{taskId}-review.md"
   )
   ```
4. IF BLOCKED: Remove taskId from `tasks_in_review` → read `.ralph/reviews/task-{taskId}-blockers.md` → surface to user. Do NOT spawn until resolved.

**Completion flow:**
1. All tasks complete — all reviewers report PASS
2. Lead verifies: all `.code-task.md` files have `Status: COMPLETED`
3. Lead sends `shutdown_request` to any remaining teammates
4. `TeamDelete`
5. Inform user: "Ejecucion completa. {N} tasks completadas. {metrics summary}."

> Guardrail enforcement: [backpressure.md](references/backpressure.md)

---

## Core Principles

1. **Single Entry Point** — Invoke once, orchestrate everything. Never invoke SOP skills directly.
2. **Checkpoint Before Execution** — Planning can be interactive OR autonomous, but user ALWAYS approves the execution plan (Step 7 ExitPlanMode) before execution begins.
3. **Fresh Context + Guardrails = Compounding Intelligence** — Each teammate gets fresh 200K context. `guardrails.md` accumulates lessons across tasks. Quality gates (TaskCompleted hook) enforce standards. Reviewers validate SDD compliance after gates pass.
4. **Disk Is State, Git Is Memory** — `.code-task.md` files are the task contract. `guardrails.md` is shared memory. Git commits are checkpoints. If a teammate crashes, its task file persists for the next one.

---

## References

| File | Description |
|------|-------------|
| [configuration-guide.md](references/configuration-guide.md) | All config options and defaults |
| [execution-paths.md](references/execution-paths.md) | Agent Teams execution model |
| [agent-teams-architecture.md](references/agent-teams-architecture.md) | Agent Teams architecture, hooks, execution model |
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
| [autonomous-mode-constraint.md](references/autonomous-mode-constraint.md) | Autonomous planning constraints |

---

## Related Skills

| Skill | Step | Purpose |
|-------|------|---------|
| `sop-reverse` | 2 | Referent discovery |
| `sop-planning` | 3 | Research, design |
| `sop-task-generator` | 4 | Task files |
| `sop-code-assist` | Teammates | SDD implementation |
