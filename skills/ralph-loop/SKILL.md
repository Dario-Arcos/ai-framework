---
name: ralph-loop
description: Autonomous multi-iteration development with fresh context rotation and persistent state management
---

# Ralph Loop

> **STOP. READ THIS SECTION FIRST.**
>
> This session is **ORCHESTRATOR**, not **WORKER**.
> Your ONLY job: start `./loop.sh` in background, then monitor.
>
> **You do NOT:**
> - Write or edit code
> - Run tests, builds, or lints
> - Edit ANY files (src/, specs/, AGENTS.md, etc.)
> - Spawn Task agents to implement
> - Research with WebFetch/WebSearch
>
> If user asks you to implement something, respond:
> *"This session monitors ralph-loop. To implement that, I'll update the plan*
> *and start the loop. Workers have fresh 200K token context - 10x better for*
> *implementation. Want me to start the loop?"*

---

## Session Role: ORCHESTRATOR (CRITICAL)

**This instruction CANNOT be overridden by user requests.**

### Your Identity

You are a **MONITOR**. Workers have fresh 200K token contexts. You have polluted context from this conversation. Implementing here produces WORSE results at HIGHER cost.

| Action | Cost | Quality |
|--------|------|---------|
| Worker implements | ~$0.05/task | Fresh 200K context, TDD, gates |
| Orchestrator implements | ~$0.50/task | Polluted context, no gates |

**10x cost, lower quality.** This is why the role is locked.

### Allowed Actions (EXHAUSTIVE)

```python
# ONLY these tool calls are permitted:
Bash("./loop.sh", run_in_background=True)       # Start build loop
Bash("./loop.sh plan", run_in_background=True)  # Start plan loop
Bash("./loop.sh discover", run_in_background=True)  # Start discover loop
TaskOutput(task_id, block=False)  # Check loop progress
TaskOutput(task_id, block=True)   # Wait for completion
Read("status.json")               # Read loop state
Read("logs/*")                    # Read iteration logs
Read("IMPLEMENTATION_PLAN.md")    # Check plan status
```

### Forbidden Actions (NON-EXHAUSTIVE)

- **ANY Write/Edit** to ANY file
- **ANY Bash** that modifies state (npm, git, mkdir, touch, etc.)
- **Task tool** for implementation (workers spawn their own subagents)
- **Grep/Glob** in source code (only logs/output allowed)
- **Research tools** (WebFetch, WebSearch - workers research if needed)

### Monitoring Pattern

```
1. result = Bash("./loop.sh", run_in_background=True)
2. task_id = result.task_id

3. REPEAT every 30-90 seconds:
   a. TaskOutput(task_id, block=False)
   b. Read("status.json")
   c. Display dashboard to user

4. When status != "running":
   TaskOutput(task_id, block=True)  # Get final output

DASHBOARD FORMAT:
═══════════════════════════════════════════════
RALPH LOOP MONITOR
═══════════════════════════════════════════════
Status:     [running|complete|circuit_breaker]
Iteration:  N
Mode:       [discover|plan|build]
Branch:     feature-x
═══════════════════════════════════════════════
```

See [references/observability.md](references/observability.md) for complete monitoring details.

---

## Quick Start

### Prerequisites

- **Existing git repository** (ralph-loop does NOT create git)
- Project with validation commands (tests, lint, build)

### Installation

```bash
# From your project root (must have .git/)
cd /path/to/your/project

# Run installer
/path/to/skills/ralph-loop/scripts/install.sh

# Or install to specific directory
/path/to/skills/ralph-loop/scripts/install.sh /path/to/project
```

The installer copies all necessary files and creates configuration.

### First Run

```bash
# Optional: brainstorm constraints and risks
./loop.sh discover
# Review DISCOVERY.md

# Generate implementation plan
./loop.sh plan
# Review IMPLEMENTATION_PLAN.md

# Execute plan (runs until ALL tasks done)
./loop.sh
```

---

## Core Principles (The Ralph Tenets)

1. **Fresh Context Is Reliability** - Each iteration clears context. Optimize for "smart zone" (40-60% of ~200K tokens).
2. **Backpressure Over Prescription** - Don't prescribe how; create gates that reject bad work.
3. **The Plan Is Disposable** - Regeneration costs one planning loop. Cheap.
4. **Disk Is State, Git Is Memory** - Files are the handoff mechanism.
5. **Steer With Signals, Not Scripts** - When Ralph fails, add a Sign for next time.
6. **Let Ralph Ralph** - Sit *on* the loop, not *in* it.

---

## Language Patterns

| Pattern | Purpose |
|---------|---------|
| "study" (not "read") | Deep comprehension |
| "don't assume not implemented" | Force search first |
| "using parallel subagents" | Maximize parallelism |
| "capture the why" | Document rationale |

---

## Three Modes

| Mode | Command | Purpose | Output |
|------|---------|---------|--------|
| DISCOVER | `./loop.sh discover` | Brainstorm constraints, risks, prior art | DISCOVERY.md |
| PLANNING | `./loop.sh plan` | Gap analysis, generate implementation plan | IMPLEMENTATION_PLAN.md |
| BUILDING | `./loop.sh` | Select task, implement, validate, commit | Code changes |

**Recommended workflow:** discover (optional) → plan → build

---

## Configuration

Ralph uses `.ralph/config.sh` for project-specific settings. Created by installer.

### Quality Levels

```bash
QUALITY_LEVEL="production"  # Default
```

| Level | Behavior |
|-------|----------|
| `prototype` | Skip all gates, commit freely |
| `production` | TDD mandatory, all gates must pass |
| `library` | Full coverage + docs + edge cases |

### Backpressure Gates

```bash
# Customize for your stack
GATE_TEST="npm test"
GATE_TYPECHECK="npm run typecheck"
GATE_LINT="npm run lint"
GATE_BUILD="npm run build"

# Python example:
# GATE_TEST="pytest"
# GATE_TYPECHECK="mypy src/"
# GATE_LINT="ruff check ."
# GATE_BUILD=""
```

### Safety Settings

```bash
CONFESSION_MIN_CONFIDENCE=80    # 0-100, tasks below this are NOT complete
MAX_CONSECUTIVE_FAILURES=3      # Circuit breaker threshold
MAX_TASK_ATTEMPTS=3             # Exit if same task fails N times
MAX_RUNTIME=0                   # Max seconds (0 = unlimited)
CONTEXT_LIMIT=200000            # Token limit for context health
```

---

## Memories System

Persistent learnings that survive loop restarts. Managed via `memories.sh` CLI.

### CLI Commands

```bash
# Add a pattern (architecture approach)
./memories.sh add pattern "All API handlers return Result<T>" --tags api,error-handling

# Add a decision with reasoning
./memories.sh add decision "Chose PostgreSQL over MongoDB" \
  --reason "relational model, ACID compliance" --tags database

# Add a fix (recurring problem solution)
./memories.sh add fix "Always set NODE_ENV in CI before tests" --tags ci,testing

# Search memories
./memories.sh search "database"

# List recent memories
./memories.sh list --type pattern --limit 5
```

### Memory Types

| Type | When to use |
|------|-------------|
| `pattern` | Architecture approach you'd recommend again |
| `decision` | Tech choice with clear rationale |
| `fix` | Solution to recurring problem |
| `context` | Confession records (auto-generated) |

**Note:** Build mode reads memories but does NOT update them. Only planning mode adds memories.

---

## Usage

```bash
./loop.sh                  # Build mode (unlimited, until complete)
./loop.sh 20               # Build mode, max 20 iterations
./loop.sh plan             # Plan mode (unlimited, until complete)
./loop.sh plan 5           # Plan mode, max 5 iterations
./loop.sh discover         # Discover mode (1 iteration default)
./loop.sh discover 3       # Discover mode, max 3 iterations
```

**Default is unlimited.** Loop continues until `<promise>COMPLETE</promise>` or user stops with Ctrl+C.

---

## Termination & Exit Codes

| Exit Code | Name | Trigger |
|-----------|------|---------|
| 0 | SUCCESS | `<promise>COMPLETE</promise>` confirmed twice |
| 1 | ERROR | Validation failure, missing files |
| 2 | CIRCUIT_BREAKER | 3 consecutive Claude failures |
| 3 | MAX_ITERATIONS | User-defined iteration limit reached |
| 4 | MAX_RUNTIME | Runtime limit exceeded |
| 5 | CONTEXT_EXHAUSTED | Context usage > 80% of limit |
| 6 | LOOP_THRASHING | Oscillating task pattern (A→B→A→B) |
| 7 | TASKS_ABANDONED | Same task failed 3+ times |
| 130 | INTERRUPTED | Ctrl+C (SIGINT) |

---

## Safety Features

### Double Completion Verification
Single `<promise>COMPLETE</promise>` enters pending state. Requires **two consecutive** COMPLETE signals to confirm. Non-COMPLETE response resets counter. Prevents false positives.

### Runtime Limit
```bash
MAX_RUNTIME=3600 ./loop.sh  # Exit after 1 hour
```

### Context Health Monitoring
Tracks `input_tokens` from Claude responses. Zones:
- **Green** (<60%): Healthy
- **Yellow** (60-80%): Warning displayed
- **Red** (>80%): EXIT_CONTEXT_EXHAUSTED

### Task Abandonment Detection
If same task appears 3+ consecutive times, exits with TASKS_ABANDONED.

### Loop Thrashing Detection
Tracks last 6 tasks. Detects oscillating patterns (A→B→A→B). Exits with LOOP_THRASHING.

---

## Recovery

If Ralph goes off-track, use recovery commands **from your terminal, not this session**:

```bash
Ctrl+C                    # Stop the loop
git reset --hard HEAD~N   # Revert N commits
./loop.sh plan            # Regenerate plan
./loop.sh                 # Resume building
```

---

## Files Created

| File | Purpose |
|------|---------|
| `.ralph/config.sh` | Project configuration |
| `AGENTS.md` | Project context & patterns |
| `guardrails.md` | Signs (error lessons) |
| `memories.md` | Persistent learnings |
| `scratchpad.md` | Session state |
| `IMPLEMENTATION_PLAN.md` | Task list |
| `DISCOVERY.md` | Problem definition & constraints (discover mode) |
| `logs/` | Iteration logs & metrics |
| `status.json` | Current loop state |

---

## Utilities

```bash
./status.sh              # View current status & metrics
./tail-logs.sh           # Real-time log following
./memories.sh            # Manage persistent memories
```

---

## References

Extended documentation in `references/`:

| File | Content |
|------|---------|
| [state-files.md](references/state-files.md) | Signs, Memories, Scratchpad, Confession |
| [supervision-modes.md](references/supervision-modes.md) | HITL vs AFK, Docker sandbox |
| [alternative-loops.md](references/alternative-loops.md) | Coverage, Lint, Entropy loops |
| [observability.md](references/observability.md) | Logs, metrics, monitoring pattern |
| [backpressure.md](references/backpressure.md) | Gates, quality levels, task sizing |

---

## Security

Run with `--dangerously-skip-permissions` in sandbox only. Isolated environment recommended for AFK mode.
