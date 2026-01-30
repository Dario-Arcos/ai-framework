# Ralph-Orchestrator: Step-by-Step Flow

> Definitive guide to the complete orchestration process

---

## Summary

Ralph-orchestrator executes complex projects by dividing work into SOP (Standard Operating Procedures) phases and delegating implementation to an autonomous loop that maintains fresh context.

```
┌─────────────────────────────────────────────────────────────────┐
│                    RALPH-ORCHESTRATOR                           │
├─────────────────────────────────────────────────────────────────┤
│  PLANNING PHASE (Interactive OR Autonomous - user chooses)      │
│  ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐ │
│  │Mode      │→│Discovery│→│Planning │→│  Tasks  │→│Checkpoint│ │
│  │Selection │ │         │ │         │ │         │ │ (Review) │ │
│  └──────────┘ └─────────┘ └─────────┘ └─────────┘ └──────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  EXECUTION PHASE (Autonomous / Checkpoint - user chooses)       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  LOOP.SH: Iterations with fresh context (~100K max)     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: Infrastructure Verification

**Objective**: Ensure the project has the necessary infrastructure.

### Steps:

1. **Check if `./loop.sh` exists** in the project root
2. **If it does NOT exist**, run installation:
   ```bash
   ./skills/ralph-orchestrator/scripts/install.sh /path/to/project
   ```
3. **Verify created files**:
   - `./loop.sh` - Execution script
   - `.ralph/config.sh` - Configuration
   - `guardrails.md` - Session signs
   - `scratchpad.md` - Temporary state

### If it fails:
- Immediate STOP
- Report what is missing
- DO NOT improvise

---

## Phase 0.5: Planning Mode Selection

**Objective**: Determine how the planning phases will operate.

### Question to User:
```text
"¿Estarás presente durante la planificación?"
- Interactive (Recommended): Guiaré paso a paso, preguntando sobre requisitos y diseño
- Autonomous: Planificaré autónomamente, documentando decisiones. Revisarás antes de ejecutar.
```

### Mode Effects:

| Planning Mode | SOP Skills Behavior |
|---------------|---------------------|
| **Interactive** | Ask questions, wait for answers, iterate with user |
| **Autonomous** | Make reasonable decisions, document rationale, never block |

### Recommendations:
- **Interactive** → Unclear requirements, complex decisions, learning opportunity
- **Autonomous** → Clear requirements, similar to past projects, user has limited time

**Store as `PLANNING_MODE` for all subsequent SOP skill invocations.**

---

## Phase 1: Discovery (sop-discovery)

**Objective**: Document the problem before designing solutions.

### Steps:

1. **Execute skill** `sop-discovery --mode={PLANNING_MODE}`
2. **Document in** `specs/{feature}/discovery.md`:
   - JTBD (Job To Be Done)
   - Constraints
   - Risks
   - Prior Art
   - Decision

### Mode Behavior:
- `interactive`: Asks questions one at a time, waits for answers
- `autonomous`: Generates comprehensive discovery, documents assumptions

### Validation:
- ✓ `specs/{feature}/discovery.md` exists
- ✓ JTBD is documented

---

## Phase 2: Planning (sop-planning)

**Objective**: Design the architecture before implementing.

### Steps:

1. **Execute skill** `sop-planning --mode={PLANNING_MODE}`
2. **Create in** `specs/{feature}/design/`:
   - `detailed-design.md` - Architecture
   - Technical decisions
   - Evaluated trade-offs

### Mode Behavior:
- `interactive`: Iterates on requirements, research, design with user feedback
- `autonomous`: Generates complete design in single pass, documents all decisions

### Validation:
- ✓ `specs/{feature}/design/` directory exists
- ✓ `detailed-design.md` exists

---

## Phase 3: Task Generation (sop-task-generator)

**Objective**: Divide work into atomic tasks.

### Steps:

1. **Execute skill** `sop-task-generator --mode={PLANNING_MODE}`
2. **Create** `specs/{feature}/implementation/plan.md` with steps
3. **Generate ONE task file for EACH step**:
   ```
   specs/{feature}/implementation/
   ├── plan.md
   ├── step01/
   │   └── task-01-description.code-task.md
   ├── step02/
   │   └── task-01-description.code-task.md
   └── step03/
       └── task-01-description.code-task.md
   ```

### Mode Behavior:
- `interactive`: Presents task breakdown for approval, allows iteration
- `autonomous`: Generates all task files, adds "[AUTO-GENERATED]" metadata

### Validation:
- ✓ N task files = N steps in plan
- ✓ Each task has acceptance criteria

---

## Phase 3.5: Plan Review Checkpoint

**Objective**: User approval before execution (MANDATORY regardless of planning mode).

### Present Summary:
```markdown
## Plan Review

**Planning Mode Used:** {PLANNING_MODE}

### Artifacts Generated
- Discovery: `specs/{feature}/discovery.md`
- Design: `specs/{feature}/design/detailed-design.md`
- Tasks: {N} task files

### Key Decisions Made
1. [From design document]
2. [From design document]
3. [From design document]

### Blockers Found
- [From blockers.md or "None"]
```

### User Options:
- **Aprobar y continuar**: Proceed to execution configuration
- **Revisar artifacts**: Show artifact contents before deciding
- **Rehacer planificación**: Return to Phase 1 with interactive mode

### Critical Rules:
- **NEVER skip this checkpoint** even if planning was interactive
- **NEVER launch execution** without explicit user approval
- If user requests artifact review, show artifacts first

---

## Phase 4: Configuration

**Objective**: Prepare the loop for execution.

**Execution is ALWAYS autonomous.** The only choice is checkpoint frequency.

### File `.ralph/config.sh`:

```bash
# Model
MODEL=claude-sonnet-4-20250514

# Quality gates
QUALITY_LEVEL=production  # prototype | production | library
MIN_TEST_COVERAGE=90      # 0-100, 0 disables

# Checkpoints (optional review pauses)
CHECKPOINT_MODE="none"      # "none" or "iterations"
CHECKPOINT_INTERVAL=5       # Only if CHECKPOINT_MODE="iterations"

# Iterations
MAX_ITERATIONS=10
```

---

## Phase 5: Loop Execution

**Objective**: Implement tasks autonomously.

**Execution is ALWAYS autonomous via loop.sh.** Optional checkpoints pause for review but the loop itself runs autonomously.

### Launch:

```bash
# ALWAYS in background, ALWAYS autonomous
Bash(command="./loop.sh specs/{feature}/", run_in_background=true)
```

### The loop does for each iteration:

1. **Reads** `scratchpad.md` for context
2. **Reads** `guardrails.md` for signs
3. **Executes** the current task
4. **Validates** gates (test, lint, typecheck, build)
5. **Updates** state
6. **Captures** signs if it finds gotchas
7. **Decides**: continue or iterate (based on context)

### Context Philosophy:

Ralph does NOT measure context percentages post-hoc. The 40-60% effectiveness observation is EMERGENT from atomic task design, not enforced by code.

**How it works:**
- Tasks are designed to be atomic (completable in ~40-60% of context)
- Input files are truncated BEFORE each iteration (input-based approach)
- Workers start fresh each iteration without context measurement

---

## Phase 6: Pre-Complete Validations

Before accepting `<promise>COMPLETE</promise>`:

### 1. Test Coverage Gate
```bash
if coverage < MIN_TEST_COVERAGE (90%):
    REJECT → "Add more tests"
```

### 2. Guardrails Learning
```bash
if guardrails empty after N iterations:
    WARNING → "Learning failure - no signs captured"
```

### 3. Config Consistency
```bash
if AGENTS.md.QUALITY_LEVEL != config.sh.QUALITY_LEVEL:
    WARNING → "Config mismatch detected"
```

---

## Phase 7: Monitoring

### How to monitor (non-blocking):

```bash
# Check state
TaskOutput(task_id="{id}", block=false)

# View complete log
Read(file_path="logs/iteration-{N}.log")

# View latest output
Read(file_path="logs/current.log")
```

### DO NOT:
- `tail -f` (blocks)
- Long timeout (may kill process)

---

## Phase 8: Completeness

### Completeness signal:

The loop emits `<promise>COMPLETE</promise>` when:
- All tasks in plan.md are `[x]`
- Gates pass (test, lint, build)
- Coverage >= 90%
- Double verification successful

### Final artifacts:

```
project/
├── src/                    # Implemented code
├── tests/                  # Tests (90%+ coverage)
├── specs/{feature}/
│   ├── discovery.md        # Documented JTBD
│   ├── design/
│   │   └── detailed-design.md
│   └── implementation/
│       ├── plan.md         # All [x]
│       └── step*/task*.md  # Status: COMPLETED
├── guardrails.md           # Captured signs
├── scratchpad.md           # Final state
└── logs/                   # Iteration history
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          START                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 0: Does ./loop.sh exist?                                 │
│  ├─ NO → Execute install.sh                                     │
│  └─ YES → Continue                                              │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 0.5: PLANNING MODE SELECTION                             │
│  ├─ Interactive: Guide step by step, ask questions              │
│  └─ Autonomous: Plan independently, document decisions          │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: DISCOVERY (--mode={PLANNING_MODE})                    │
│  └─ Create specs/{feature}/discovery.md                         │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: PLANNING (--mode={PLANNING_MODE})                     │
│  └─ Create specs/{feature}/design/detailed-design.md            │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: TASK GENERATION (--mode={PLANNING_MODE})              │
│  └─ Create plan.md + N task files                               │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3.5: PLAN REVIEW CHECKPOINT (MANDATORY)                  │
│  ├─ Present summary of all artifacts                            │
│  ├─ Show key decisions made                                     │
│  └─ User approves / reviews / redoes                            │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 4: CONFIGURATION                                         │
│  └─ Configure .ralph/config.sh (quality, optional checkpoints)  │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 5: AUTONOMOUS LOOP                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  For each iteration:                                     │   │
│  │  1. Read scratchpad + guardrails                         │   │
│  │  2. Execute task                                         │   │
│  │  3. Validate gates                                       │   │
│  │  4. Update state                                         │   │
│  │  5. All complete? → Exit                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 6: VALIDATIONS                                           │
│  ├─ Coverage >= 90%?                                            │
│  ├─ Guardrails not empty?                                       │
│  └─ Config consistent?                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  <promise>COMPLETE</promise>                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "loop.sh not found" | Infrastructure not installed | Execute install.sh |
| "Context: 0%" | Calculation bug (already fixed) | Update loop.sh |
| "discovery.md missing" | SOP skipped | Execute sop-discovery first |
| "design/ missing" | Planning skipped | Execute sop-planning first |
| "Coverage < 90%" | Insufficient tests | Add more tests |
| "No signs captured" | Learning failure | Add signs manually |

---

## Key Principles

1. **Fresh Context = Quality**: The model is more effective in the first 40-60% of context (emergent observation, not enforced)
2. **SOP Non-Negotiable**: Discovery → Planning → Tasks → Execute
3. **Continuous Validation**: Gates on each iteration
4. **Captured Learning**: Signs document gotchas for future iterations
5. **Controlled Autonomy**: The loop is autonomous but validated

---

*Generated: 2026-01-29*
*Version: 3.1.0 - Added planning mode selection and mandatory review checkpoint*
