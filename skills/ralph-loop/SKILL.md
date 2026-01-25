---
name: ralph-loop
description: Autonomous multi-iteration development with fresh context rotation and persistent state management
---

# Ralph Loop

Infinite loop where each iteration operates with fresh context. State persists in files and git, not LLM memory.

## When to Use

**Use when:**
- Task requires multiple hours of autonomous work
- Previous attempts suffered from context rot
- Same errors repeat across sessions
- Need to ship code overnight without supervision

**Don't use when:**
- Single task fits in one session (<80% context)
- High human involvement required
- Debugging production issues

---

## Core Principles

### 1. Context Is EVERYTHING
Fresh context each iteration prevents pollution. State lives in files + git.

### 2. Steering Ralph: Patterns + Backpressure
- Patterns in AGENTS.md guide implementation style
- Backpressure (tests/lint/build) prevents bad commits

### 3. Let Ralph Ralph
Iteration and self-correction reach good outcomes. Trust eventual consistency.

### 4. Move Outside the Loop
Subjective decisions → human. Repetitive work → Ralph.

---

## Language Patterns

Use these exact phrases in prompts:

| Pattern | Purpose |
|---------|---------|
| "study" (not "read") | Deep comprehension |
| "don't assume not implemented" | Force search first |
| "using parallel subagents" | Maximize parallelism |
| "only 1 subagent for build/tests" | Serialize validation |
| "capture the why" | Document rationale |
| "if functionality is missing then it's your job to add it" | Complete implementation |
| "resolve them or document them" | No silent failures |
| "using a subagent" | Delegate state updates |

---

## Hierarchy

```
JTBD (Job to Be Done)
  └── Topic of Concern (specs/*.md)
        └── Task (IMPLEMENTATION_PLAN.md item)
              └── Subtask (within iteration)
```

---

## Two Modes

| Mode | Prompt | Purpose |
|------|--------|---------|
| PLANNING | PROMPT_plan.md | Gap analysis → generate plan |
| BUILDING | PROMPT_build.md | Select task → implement → commit |

---

## Supervision Modes

Two approaches based on human involvement level:

### HITL (Human-in-the-Loop)

**Use for:**
- Learning how Ralph handles your codebase
- Risky tasks (auth, payments, migrations)
- Architectural decisions that need approval
- First-time setup of a new project

**Configuration:**
```bash
./loop.sh build 1     # Single iteration, review after
./loop.sh build 5     # Few iterations, frequent review
```

**Behavior:**
- Short runs (1-5 iterations)
- Human reviews after each batch
- Adjust Signs and specs between runs
- High confidence before AFK mode

### AFK (Away-From-Keyboard)

**Use for:**
- Bulk implementation work
- Low-risk, well-defined tasks
- Overnight batch processing
- Tasks with strong test coverage

**Configuration:**
```bash
./loop.sh build 20    # Medium batch
./loop.sh build 50    # Long overnight run
```

**Behavior:**
- Long runs (10-50+ iterations)
- Circuit breaker handles failures
- Review aggregated results
- Trust backpressure gates

### Progression

```
First project  → HITL (1-5)    → Learn patterns
Stable codebase → AFK (10-20)  → Bulk work
High test coverage → AFK (50+) → Overnight runs
```

**Recommendation:** Start HITL, graduate to AFK as confidence grows.

---

## State Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Operational guide (~50 lines) |
| `guardrails.md` | Signs (session error lessons) |
| `memories.md` | Persistent learnings across sessions |
| `scratchpad.md` | Iteration-to-iteration memory (session only) |
| `IMPLEMENTATION_PLAN.md` | Prioritized tasks |
| `specs/*.md` | Requirements per topic |

---

## Observability

Ralph generates structured logs for monitoring:

| Artifact | Purpose |
|----------|---------|
| `logs/iteration.log` | Timestamped iteration events |
| `logs/metrics.json` | Success rate, durations, totals |
| `claude_output/iteration_NNN.txt` | Complete Claude output per iteration |
| `status.json` | Current loop state |
| `errors.log` | Failed iteration details |

**Utilities:**
```bash
./status.sh           # View current status & metrics
./tail-logs.sh        # Show last iteration output
./tail-logs.sh 3      # Show iteration 3 output
./tail-logs.sh follow # Real-time log following
```

**Interactive Monitoring:**
- Use active Claude Code session as observer
- Cost: ~$0.48 per 2 hours
- Won't compact in sessions <4h
- No interference with bash loops (independent processes)

---

## Session Role: ORCHESTRATOR

**This session = MONITOR. Never EXECUTOR.**

### Allowed
- `Bash("./loop.sh", run_in_background=true)`
- `TaskOutput(task_id, block=false)`
- `Read`: status.json, logs/*, claude_output/*
- `KillShell(shell_id)`
- Display progress, alerts

### Forbidden
- Write/Edit: src/*, AGENTS.md, guardrails.md, IMPLEMENTATION_PLAN.md
- Bash: npm test, npm run build, git commit
- Any implementation work

### Monitoring Loop
```
1. result = Bash("./loop.sh plan 5", run_in_background=true)
2. while status not in [complete, failed, stopped]:
     TaskOutput(task_id, block=false, timeout=interval*1000)
     Read("status.json")
     display_dashboard()
     interval = clamp(last_duration/3, 30, 90)
3. TaskOutput(task_id, block=true)
```

### Rationale
Worker sessions have fresh 200K tokens. This session monitors. Mixing roles wastes context.

---

## Building Mode Lifecycle

1. **Orient** - Read guardrails.md FIRST
2. **Read plan** - Load IMPLEMENTATION_PLAN.md
3. **Select** - Choose highest priority incomplete task
4. **Search** - Don't assume not implemented
5. **Implement** - TDD: test → fail → implement → pass
6. **Validate** - All backpressure gates must pass
7. **Update state** - BEFORE commit
8. **Commit** - Only after all gates green
9. **Exit** - Fresh context next iteration

---

## Backpressure Gates

```bash
npm test          # Tests must pass
npm run typecheck # Types must check
npm run lint      # Lint must pass
npm run build     # Build must succeed
```

**All gates must pass before commit. No exceptions.**

---

## Signs System

When errors occur, add to guardrails.md:

```markdown
### Sign: [Problem]
- **Trigger**: [When this happens]
- **Instruction**: [What to do instead]
```

Every iteration reads Signs FIRST → Compounding intelligence.

---

## Memories System

Persistent learnings that survive loop restarts. Unlike Signs (session-specific), Memories persist indefinitely.

```markdown
### mem-[timestamp]-[hash]
> [Learning or decision with context]
<!-- tags: tag1, tag2 | created: YYYY-MM-DD -->
```

**Categories:**
| Category | Content |
|----------|---------|
| **Patterns** | Architecture approaches, coding conventions |
| **Decisions** | Tech choices, design trade-offs |
| **Fixes** | Solutions to persistent problems |
| **Context** | Confessions and accountability records |

**Signs vs Memories:**
| Aspect | Signs (guardrails.md) | Memories (memories.md) |
|--------|----------------------|------------------------|
| Scope | Current loop session | All future sessions |
| Content | Error lessons, gotchas | Patterns, preferences |
| Lifecycle | Cleared with new goal | Persists indefinitely |
| Updates | Build mode (errors) | Planning mode only |

---

## Scratchpad System

Iteration-to-iteration memory within a single loop session. Reduces context recovery time by recording what each iteration learned.

```markdown
## Current State
- **Last task completed**: [task name]
- **Next task to do**: [task name]
- **Files modified this session**: [list]

## Key Decisions This Session
- [Decision with rationale]

## Blockers & Notes
- [Issues discovered]
```

**Scratchpad vs Signs vs Memories:**
| Aspect | Scratchpad | Signs | Memories |
|--------|------------|-------|----------|
| Scope | Current iteration | Current loop | All loops |
| Lifecycle | Cleared on loop start | Cleared manually | Persists |
| Content | Progress, decisions | Errors, gotchas | Patterns |
| Updates | Every iteration | On errors | Planning only |

---

## Confession Pattern

Accountability mechanism that forces declaration of what was accomplished.

**Format:**
```
> confession: objective=[task], met=[Yes/No], evidence=[proof]
```

**Components:**
| Field | Content |
|-------|---------|
| `objective` | Task from IMPLEMENTATION_PLAN.md |
| `met` | Yes or No (no hedging) |
| `evidence` | Actual proof: test output, file paths, command results |

**Why this matters:**
- Forces explicit declaration of completion
- Prevents "I think I did it" without evidence
- Creates audit trail in `claude_output/iteration_NNN.txt`
- Enables post-hoc verification of claims

**When:** Phase 4e, after state updates, before commit.

---

## Task Sizing

One task = one context window.

**Right-sized:**
- Add database column + migration
- Add UI component to existing page
- Fix bug in login flow

**Too large:**
- Build entire auth system
- Implement complete dashboard

**Test:** If >2000 lines to understand or >5 files → split.

---

## Quality Levels

Define quality expectations in AGENTS.md to control validation behavior.

| Level | Shortcuts OK | Tests Required | Polish Required |
|-------|--------------|----------------|-----------------|
| **Prototype** | Yes | No | No |
| **Production** | No | Yes | Some |
| **Library** | No | Yes | Yes |

**Why this matters:**
- Prototype → Fast iteration, skip backpressure gates
- Production → TDD mandatory, all gates must pass
- Library → Full coverage, documentation, edge cases

**Set in:** `AGENTS.md` → Quality Level section

---

## Plan Format

**The plan is disposable.** Regeneration costs one planning loop. Verbosity wastes every iteration's context.

**Constraints:**
| Element | Limit |
|---------|-------|
| Entire plan | <100 lines |
| Each task | 3-5 lines |
| Implementation details | None (building mode) |

**Task format:**
```markdown
- [ ] Task title | Size: S/M | Files: N
  Acceptance: [single sentence]
```

**Anti-patterns:**
- ❌ 400-line plans (first loop's mistake)
- ❌ Research summaries in plan (move to specs/)
- ❌ Step-by-step implementation notes
- ❌ Keeping completed tasks forever

**Recovery:** If plan exceeds 100 lines → run `./loop.sh plan 1` to regenerate.

---

## Context Thresholds

| Zone | Usage | Action |
|------|-------|--------|
| 🟢 | <40% | Operate freely |
| 🟡 | 40-60% | Wrap up current task |
| 🔴 | >60% | Force rotation |

---

## Gutter Detection

**You're stuck if:**
- Same command fails 3 times
- Same file modified 5+ times
- No progress in 30 minutes

**Recovery:** Add Sign → Exit → Fresh approach next iteration.

---

## Circuit Breaker

After 3 consecutive failures, loop.sh stops and requests human action:
- Check errors.log
- Fix manually or adjust specs
- Run ./loop.sh again

---

## Usage

```bash
./loop.sh              # Build mode, unlimited
./loop.sh 20           # Build mode, max 20 iterations
./loop.sh plan         # Plan mode, unlimited
./loop.sh plan 5       # Plan mode, max 5 iterations
```

---

## Termination

| Method | When |
|--------|------|
| `<promise>COMPLETE</promise>` | All tasks done |
| Max iterations | Cost control |
| Ctrl+C | Manual stop |
| Circuit breaker | 3 consecutive failures |

---

## Recovery

If Ralph goes off-track:
1. Ctrl+C
2. `git reset --hard HEAD~N`
3. `./loop.sh plan` (regenerate plan)
4. `./loop.sh` (resume building)

---

## Security

**Use protection:**
- Run with `--dangerously-skip-permissions` in sandbox only
- "It's not if it gets popped, it's when"
- Isolated environment recommended

---

## Files

**scripts/**
- `loop.sh` - Bash orchestrator
- `PROMPT_plan.md` - Planning instructions
- `PROMPT_build.md` - Building instructions

**templates/**
- `AGENTS.md.template` - Operational guide template
- `guardrails.md.template` - Signs template
- `memories.md.template` - Persistent memories template
- `scratchpad.md.template` - Session scratchpad template
