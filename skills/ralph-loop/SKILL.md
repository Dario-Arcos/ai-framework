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

## State Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Operational guide (~50 lines) |
| `guardrails.md` | Signs (error lessons) |
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

## Context Thresholds

| Zone | Usage | Action |
|------|-------|--------|
| 🟢 | <60% | Operate freely |
| 🟡 | 60-80% | Wrap up current task |
| 🔴 | >80% | Force rotation |

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
