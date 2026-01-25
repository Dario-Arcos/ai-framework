---
name: ralph-loop
description: Autonomous multi-iteration development with fresh context rotation and persistent state management
---

# Ralph Loop

Infinite loop where each iteration operates with fresh context. State persists in files and git, not LLM memory. **By default, runs until objective is 100% complete.**

## Quick Start

### Prerequisites

- **Existing git repository** (ralph-loop does NOT create git)
- Project with validation commands (tests, lint, build)

### Installation

```bash
# From your project root (must have .git/)
RALPH_SKILL="path/to/skills/ralph-loop"

cp "$RALPH_SKILL/scripts/loop.sh" .
cp "$RALPH_SKILL/scripts/PROMPT_build.md" .
cp "$RALPH_SKILL/scripts/PROMPT_plan.md" .
chmod +x loop.sh
```

### First Run

```bash
./loop.sh plan      # Generate plan (runs until complete)
# Review IMPLEMENTATION_PLAN.md

./loop.sh           # Execute plan (runs until ALL tasks done)
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

## Two Modes

| Mode | Command | Purpose |
|------|---------|---------|
| PLANNING | `./loop.sh plan` | Gap analysis -> generate plan |
| BUILDING | `./loop.sh` | Select task -> implement -> commit |

---

## Session Role: ORCHESTRATOR

**This session = MONITOR. Never EXECUTOR.**

### Allowed
- `Bash("./loop.sh", run_in_background=true)`
- `TaskOutput(task_id, block=false)`
- `Read`: status.json, logs/*, claude_output/*
- Display progress, alerts

### Forbidden
- Write/Edit: src/*, AGENTS.md, guardrails.md
- Bash: npm test, npm run build, git commit
- Any implementation work

**Rationale:** Worker sessions have fresh 200K tokens. This session monitors. Mixing roles wastes context.

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

## Usage

```bash
./loop.sh              # Build mode (unlimited, until complete)
./loop.sh 20           # Build mode, max 20 iterations
./loop.sh plan         # Plan mode (unlimited, until complete)
./loop.sh plan 5       # Plan mode, max 5 iterations
```

**Default is unlimited.** Loop continues until `<promise>COMPLETE</promise>` or user stops with Ctrl+C.

---

## Termination

| Method | When |
|--------|------|
| `<promise>COMPLETE</promise>` | All tasks done |
| Max iterations (if specified) | User-defined limit |
| Ctrl+C | Manual stop |
| Circuit breaker | 3 consecutive failures |

---

## Recovery

If Ralph goes off-track:
```bash
Ctrl+C
git reset --hard HEAD~N
./loop.sh plan    # Regenerate plan
./loop.sh         # Resume building
```

---

## Files Created

| File | Purpose |
|------|---------|
| `AGENTS.md` | Project context & patterns |
| `guardrails.md` | Signs (error lessons) |
| `memories.md` | Persistent learnings |
| `scratchpad.md` | Session state |
| `IMPLEMENTATION_PLAN.md` | Task list |
| `logs/` | Observability |
| `status.json` | Loop state |

---

## References

Extended documentation in `references/`:

| File | Content |
|------|---------|
| [state-files.md](references/state-files.md) | Signs, Memories, Scratchpad, Confession |
| [supervision-modes.md](references/supervision-modes.md) | HITL vs AFK, Docker sandbox |
| [alternative-loops.md](references/alternative-loops.md) | Coverage, Lint, Entropy loops |
| [observability.md](references/observability.md) | Logs, metrics, monitoring |
| [backpressure.md](references/backpressure.md) | Gates, quality levels, task sizing |

---

## Security

Run with `--dangerously-skip-permissions` in sandbox only. Isolated environment recommended for AFK mode.
