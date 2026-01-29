# Ralph-Orchestrator: Step-by-Step Flow

> Definitive guide to the complete orchestration process

---

## Summary

Ralph-orchestrator executes complex projects by dividing work into SOP (Standard Operating Procedures) phases and delegating implementation to an autonomous loop that maintains fresh context.

```
┌─────────────────────────────────────────────────────────────────┐
│                    RALPH-ORCHESTRATOR                           │
├─────────────────────────────────────────────────────────────────┤
│  HITL PHASE (Human-in-the-Loop)                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│  │Discovery│→│Planning │→│  Tasks  │→│ Config  │               │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘               │
├─────────────────────────────────────────────────────────────────┤
│  AFK PHASE (Away-From-Keyboard)                                 │
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

## Phase 1: Discovery (sop-discovery)

**Objective**: Document the problem before designing solutions.

### Steps:

1. **Execute skill** `sop-discovery`
2. **Document in** `specs/{feature}/discovery.md`:
   - JTBD (Job To Be Done)
   - Constraints
   - Risks
   - Prior Art
   - Decision

### Modes:
- `--mode=interactive` - With human questions (default)
- `--mode=autonomous` - For AI execution (skips irrelevant questions)

### Validation:
- ✓ `specs/{feature}/discovery.md` exists
- ✓ JTBD is documented

---

## Phase 2: Planning (sop-planning)

**Objective**: Design the architecture before implementing.

### Steps:

1. **Execute skill** `sop-planning`
2. **Create in** `specs/{feature}/design/`:
   - `detailed-design.md` - Architecture
   - Technical decisions
   - Evaluated trade-offs

### Validation:
- ✓ `specs/{feature}/design/` directory exists
- ✓ `detailed-design.md` exists

---

## Phase 3: Task Generation (sop-task-generator)

**Objective**: Divide work into atomic tasks.

### Steps:

1. **Execute skill** `sop-task-generator`
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

### Validation:
- ✓ N task files = N steps in plan
- ✓ Each task has acceptance criteria

---

## Phase 4: Configuration

**Objective**: Prepare the loop for execution.

### File `.ralph/config.sh`:

```bash
# Model and context
MODEL=claude-sonnet-4-20250514
CONTEXT_LIMIT=200000      # 200K tokens
CONTEXT_WARNING=40        # Warning at 40%
CONTEXT_CRITICAL=60       # Iterate at 60%

# Quality gates
QUALITY_LEVEL=production  # prototype | production | world-class
MIN_TEST_COVERAGE=90      # 0-100, 0 disables

# Iterations
MAX_ITERATIONS=10
```

---

## Phase 5: Loop Execution

**Objective**: Implement tasks autonomously.

### Launch:

```bash
# ALWAYS in background
Bash(command="./loop.sh", run_in_background=true)
```

### The loop does for each iteration:

1. **Reads** `scratchpad.md` for context
2. **Reads** `guardrails.md` for signs
3. **Executes** the current task
4. **Validates** gates (test, lint, typecheck, build)
5. **Updates** state
6. **Captures** signs if it finds gotchas
7. **Decides**: continue or iterate (based on context)

### Context Management:

```
0-40%   → Green zone, continue
40-60%  → Yellow zone, consider iterating
60%+    → Red zone, MUST iterate
```

The calculation includes:
- `input_tokens`
- `cache_read_input_tokens`
- `cache_creation_input_tokens`

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
│  PHASE 1: DISCOVERY                                             │
│  └─ Create specs/{feature}/discovery.md                         │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: PLANNING                                              │
│  └─ Create specs/{feature}/design/detailed-design.md            │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: TASK GENERATION                                       │
│  └─ Create plan.md + N task files                               │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 4: CONFIGURATION                                         │
│  └─ Verify .ralph/config.sh                                     │
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
│  │  5. Context > 60%? → New iteration                       │   │
│  │  6. All complete? → Exit                                 │   │
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

1. **Fresh Context = Quality**: The model is more effective in the first 40-60% of context
2. **SOP Non-Negotiable**: Discovery → Planning → Tasks → Execute
3. **Continuous Validation**: Gates on each iteration
4. **Captured Learning**: Signs document gotchas for future iterations
5. **Controlled Autonomy**: The loop is autonomous but validated

---

*Generated: 2026-01-28*
*Version: Post-audit with 16 improvements implemented*
