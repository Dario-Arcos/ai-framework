# Agent Teams Architecture

> Execution engine for ralph-orchestrator Step 8. tmux cockpit + Claude Code Agent Teams (Ghostty optional viewer).

---

## Overview

Agent Teams is the execution engine for ralph-orchestrator. It replaces sequential iteration with ephemeral, parallel teammates coordinated through hooks, shared state files. The lead runs in the current session; tmux provides optional cockpit service windows (Ghostty as viewer).

Key properties:
- **2-layer execution** — lead orchestrates, ephemeral teammates implement (1 task each) with fresh 200K context
- **Parallel execution** — up to MAX_TEAMMATES concurrent teammates
- **Fresh 200K context per task** — each teammate gets a clean context window, avoiding progressive degradation
- **Reviewer validation** — after implementer completes and gates pass, a reviewer teammate validates SDD compliance
- **Hook-based quality gates** — TaskCompleted validates, TeammateIdle provides safety (circuit breaker + abort)
- **Cockpit visibility** — tmux windows for services, tests, logs, and shell access

---

## Component Map

```
.ralph/config.sh ──────────── Configuration (quality, gates, cockpit services)
.ralph/launch-build.sh ────── Service windows launcher (tmux, if COCKPIT_* configured)
.ralph/failures.json ──────── Per-teammate failure counters (written by hooks)
.ralph/metrics.json ───────── Task success/failure metrics (written by hooks)

hooks/teammate-idle.py ────── TeammateIdle hook (continuity + circuit breaker)
hooks/task-completed.py ───── TaskCompleted hook (quality gates + tracking)
hooks/hooks.json ──────────── Hook registration

scripts/PROMPT_implementer.md ── Implementer teammate prompt
scripts/PROMPT_reviewer.md ──── Reviewer teammate prompt
templates/launch-build.sh.template ── Cockpit launcher source
templates/config.sh.template ──────── Default configuration
```

---

## Hooks

### TeammateIdle

Fires when a teammate is about to go idle. Decision by exit code:

| Condition | Exit | Effect |
|-----------|------|--------|
| Not a ralph project (.ralph/config.sh missing) | 0 | Pass-through (not a ralph session) |
| `.ralph/ABORT` file exists | 0 | Manual abort — allow idle |
| Teammate failures >= MAX_CONSECUTIVE_FAILURES | 0 | Circuit breaker — stop this teammate |
| Default: all checks pass | 0 | Allow idle — lead manages flow |

### TaskCompleted

Fires when a teammate marks a task complete. Decision by exit code:

| Condition | Exit | Effect |
|-----------|------|--------|
| Not a ralph project | 0 | Pass-through |
| All gates pass | 0 | Reset failure counter, update metrics, accept task |
| Any gate fails | 2 | Reject: "Gate '{name}' failed. Fix before completing." |

Gates execute in order: **test → typecheck → lint → build**. First failure stops the chain.

---

## Execution Model

Two-layer architecture where the lead orchestrates and ephemeral teammates each handle exactly one task with fresh 200K context.

```
Lead (pure orchestrator — reads only 8-word summaries, never code/diffs/reviews)
├── Implementer-1 (ephemeral: spawn → implement Task A → complete → idle → shutdown)
├── Implementer-2 (ephemeral: spawn → implement Task B → complete → idle → shutdown)
├── Reviewer-1   (ephemeral: spawn → review Task A → write review → send summary → idle → shutdown)
├── Implementer-3 (ephemeral: spawn → implement Task C → complete → idle → shutdown)
├── Reviewer-2   (ephemeral: spawn → review Task B → write review → send summary → idle → shutdown)
└── ...
```

### Why ephemeral teammates?

LLM effective context is ~60% of the full window. For Opus (200K), quality degrades after ~120K tokens. Progressive compaction is lossy — each compaction loses detail, and after N compactions, early context is compressed N times.

Ephemeral teammates solve this: each task starts with a clean 200K window. No compaction needed, no context degradation.

### Implementer lifecycle

1. **Spawn** — Lead creates teammate with task context via Task tool
2. **Read context** — .ralph/guardrails.md + .ralph/agents.md + task description
3. **Implement** — Follow SDD (SCENARIO → SATISFY → REFACTOR) with /sop-code-assist
4. **Gates** — TaskCompleted hook runs quality gates (test → typecheck → lint → build)
5. **Learn** — Append to .ralph/guardrails.md if non-obvious lesson found
6. **Complete** — TaskUpdate(status: completed), commit work
7. **Idle → Shutdown** — Lead sends shutdown_request after completion

### Reviewer lifecycle

1. **Spawn** — Lead creates reviewer teammate after implementer completes and gates pass
2. **Review** — Validate SDD compliance via /sop-reviewer on the completed task
3. **Write** — Save review to `.ralph/reviews/task-{id}-review.md`
4. **Summarize** — Send 8-word summary to lead via SendMessage
5. **Idle → Shutdown** — Lead sends shutdown_request after summary received

### Lead behavior

The lead is a **pure orchestrator**: it reads only 8-word summaries from reviewers, never code, diffs, or full reviews. Decision-making is based on task status and summary signals.

### Context budget (per teammate)

| Component | Tokens | Source |
|-----------|--------|--------|
| System prompt + tools | ~20K | Claude Code |
| Task description | ~5-15K | .code-task.md |
| .ralph/agents.md | ~3-8K | Project context |
| .ralph/guardrails.md | ~2-10K | Accumulated lessons |
| Available for SDD | ~147-170K | Implementation work |

Each teammate uses its full 200K context for a single task. No compaction needed.

---

## Cockpit Layout

```
tmux session: "ralph" (service windows only — lead runs in current session)

Window ? "services" → COCKPIT_DEV_SERVER + COCKPIT_DB (if configured)
Window ? "quality"  → COCKPIT_TEST_WATCHER (if configured)
Window ? "monitor"  → COCKPIT_LOGS (if configured)
Window N "shell"    → Free terminal (if any service configured)
```

Windows are created only if COCKPIT_* variables are configured in .ralph/config.sh. If no services configured, no tmux session is created. The lead runs in the current terminal session, not inside tmux.

Navigation: `Ctrl+B {N}` to switch windows (standard tmux prefix).

---

## Teammate Capabilities

Teammates can observe cockpit service windows through tmux (for reading dev server output, test results, etc.):

### Eyes (capture-pane) — Read output from any window

```bash
tmux capture-pane -p -t ralph:services.0    # Read dev server output
tmux capture-pane -p -t ralph:quality.0     # Read test watcher output
tmux capture-pane -p -t ralph:monitor.0     # Read log output
```

### Hands (send-keys) — Execute commands in any window

```bash
tmux send-keys -t ralph:shell.0 "npm run migrate" Enter
tmux send-keys -t ralph:services.0 "C-c" "npm run dev" Enter  # Restart dev server
```

### Reach (new-window) — Create new tools

```bash
tmux new-window -t ralph -n "debug"         # Open a dedicated debug window
```

---

## State Files

| File | Purpose | Written By | Read By |
|------|---------|------------|---------|
| `.ralph/guardrails.md` | Accumulated error lessons, patterns | Teammates (flock for writes) | All teammates at task start |
| `.code-task.md` | Task descriptions and status | Lead (create), teammates (status) | Teammates (claim), lead (monitor) |
| `.ralph/failures.json` | Per-teammate consecutive failure count | TaskCompleted hook | TeammateIdle hook (circuit breaker) |
| `.ralph/metrics.json` | Task success/failure counts | TaskCompleted hook | Lead (monitoring) |
| `.ralph/agents.md` | Operational context for teammates | Lead (Step 5) | All teammates at spawn |
| `.ralph/config.sh` | Gates, cockpit services, safety settings | Lead (Step 7) | Hooks, launch-build.sh |
| `.ralph/reviews/task-{id}-review.md` | SDD compliance review per task | Reviewer teammates | Lead (summary only) |

---

## Safety Nets

| Safety Net | Mechanism |
|------------|-----------|
| **Circuit breaker** | `.ralph/failures.json` tracks per-teammate failures → TeammateIdle exits 0 at threshold |
| **Task rejection** | TaskCompleted hook rejects tasks that fail quality gates → teammate must fix |
| **Manual abort** | Create `.ralph/ABORT` file → all teammates idle on next TeammateIdle check |
| **Quality gates** | TaskCompleted hook runs test/typecheck/lint/build in sequence |
| **Checkpoint review** | Plan Review (Step 6) is mandatory before any execution begins |

---

## Prerequisites

| Requirement | Check | Install |
|-------------|-------|---------|
| tmux | `which tmux` | `brew install tmux` (Optional — enables cockpit service windows for monitoring) |
| Ghostty | `open -na Ghostty.app` | `brew install --cask ghostty` |
| Agent Teams flag | `echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| Config file | `.ralph/config.sh` exists | Copy from `templates/config.sh.template` |
| Guardrails | `.ralph/guardrails.md` exists | Copy from `templates/guardrails.md.template` |

---

*Version: 3.0.0 | Updated: 2026-02-11*
*Redesigned: 2-layer architecture (Lead → ephemeral implementer/reviewer teammates)*
