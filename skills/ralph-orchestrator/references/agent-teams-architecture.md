# Agent Teams Architecture

> Execution engine for ralph-orchestrator Step 8. Ghostty cockpit + Claude Code Agent Teams + tmux.

---

## Overview

Agent Teams is the execution engine for ralph-orchestrator. It replaces sequential iteration with persistent, parallel teammates coordinated through hooks, shared state files, and a tmux cockpit running inside Ghostty.

Key properties:
- **3-layer execution** — lead monitors, teammates coordinate, sub-agents implement with fresh context
- **Parallel execution** — up to MAX_TEAMMATES coordinators working concurrently
- **Fresh context per task** — sub-agents get clean 200K windows, avoiding progressive degradation
- **Hook-based quality gates** — TaskCompleted validates, TeammateIdle drives continuity
- **Cockpit visibility** — tmux windows for services, tests, logs, and shell access

---

## Component Map

```
.ralph/config.sh ──────────── Configuration (quality, gates, cockpit services)
.ralph/launch-build.sh ────── Ghostty + tmux launcher (copied from template)
.ralph/failures.json ──────── Per-teammate failure counters (written by hooks)
.ralph/metrics.json ───────── Task success/failure metrics (written by hooks)

hooks/teammate-idle.py ────── TeammateIdle hook (continuity + circuit breaker)
hooks/task-completed.py ───── TaskCompleted hook (quality gates + tracking)
hooks/hooks.json ──────────── Hook registration

scripts/PROMPT_teammate.md ── Teammate spawn prompt
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
| All `.code-task.md` COMPLETED | 0 | Work done — allow idle |
| Pending tasks remain | 2 | Keep working: "Re-read guardrails.md. Claim next task." |

### TaskCompleted

Fires when a teammate marks a task complete. Decision by exit code:

| Condition | Exit | Effect |
|-----------|------|--------|
| Not a ralph project | 0 | Pass-through |
| QUALITY_LEVEL=prototype | 0 | Skip all gates — accept task |
| All gates pass | 0 | Reset failure counter, update metrics, accept task |
| Any gate fails | 2 | Reject: "Gate '{name}' failed. Fix before completing." |

Gates execute in order: **test → typecheck → lint → build**. First failure stops the chain.

---

## Execution Model

Three-layer architecture that preserves fresh context for every task while maintaining parallel coordination.

```
Lead (delegate mode)
├── Teammate-1 (coordinator, persistent)
│   ├── Sub-agent: Task A (fresh 200K, implements, dies)
│   ├── Sub-agent: Task D (fresh 200K, implements, dies)
│   └── ...
├── Teammate-2 (coordinator, persistent)
│   ├── Sub-agent: Task B (fresh 200K, implements, dies)
│   ├── Sub-agent: Task E (fresh 200K, implements, dies)
│   └── ...
└── Teammate-3 (coordinator, persistent)
    ├── Sub-agent: Task C (fresh 200K, implements, dies)
    └── ...
```

### Why sub-agents?

LLM effective context is ~60% of the full window. For Opus (200K), quality degrades after ~120K tokens. Progressive compaction is lossy — each compaction loses detail, and after N compactions, early context is compressed N times.

Sub-agents solve this: each task starts with a clean 200K window. The coordinator stays lightweight (claim → delegate → verify → learn), growing ~5-10K per task.

### Coordinator lifecycle (per task)

1. **Claim** — TaskList → TaskUpdate(status: in_progress)
2. **Prepare context** — Read guardrails.md + AGENTS.md + task description
3. **Delegate** — Task(subagent_type="general-purpose", mode="bypassPermissions") with full context
4. **Verify** — Check git diff, cockpit status, test output
5. **Learn** — Append to guardrails.md if non-obvious lesson found
6. **Complete** — TaskUpdate(status: completed) → TaskCompleted hook runs gates

### Sub-agent prompt structure

The coordinator builds a prompt containing:
- Task description (full .code-task.md content)
- AGENTS.md (project context, build commands, constraints)
- guardrails.md (accumulated lessons from all teammates)
- Instruction to use /sop-code-assist or follow SDD manually

### Context budget

| Component | Tokens | Source |
|-----------|--------|--------|
| System prompt + tools | ~20K | Claude Code |
| Task description | ~5-15K | .code-task.md |
| AGENTS.md | ~3-8K | Project context |
| guardrails.md | ~2-10K | Accumulated lessons |
| Available for SDD | ~147-170K | Implementation work |

CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=60 keeps coordinator context clean.

---

## Cockpit Layout

```
tmux session: "ralph"

Window 0 "team"     → Claude Code lead + teammate panes (Agent Teams auto-splits)
Window 1 "services" → COCKPIT_DEV_SERVER + COCKPIT_DB (if configured)
Window 2 "quality"  → COCKPIT_TEST_WATCHER (if configured)
Window 3 "monitor"  → COCKPIT_LOGS (if configured)
Window 4 "shell"    → Free terminal for manual commands
```

Navigation: `Ctrl+B {N}` to switch windows (standard tmux prefix).

---

## Coordinator Capabilities

Coordinators (teammates) interact with the cockpit programmatically through tmux to monitor sub-agent work:

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
| `guardrails.md` | Accumulated error lessons, patterns | Teammates (flock for writes) | All teammates at task start |
| `.code-task.md` | Task descriptions and status | Lead (create), teammates (status) | Teammates (claim), lead (monitor) |
| `.ralph/failures.json` | Per-teammate consecutive failure count | TaskCompleted hook | TeammateIdle hook (circuit breaker) |
| `.ralph/metrics.json` | Task success/failure counts | TaskCompleted hook | Lead (monitoring) |
| `AGENTS.md` | Operational context for teammates | Lead (Step 5) | All teammates at spawn |
| `.ralph/config.sh` | Quality level, gates, cockpit services | Lead (Step 7) | Hooks, launch-build.sh |

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
| tmux | `which tmux` | `brew install tmux` |
| Ghostty | `open -na Ghostty.app` | `brew install --cask ghostty` |
| Agent Teams flag | `echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| Config file | `.ralph/config.sh` exists | Copy from `templates/config.sh.template` |
| Guardrails | `guardrails.md` exists | Copy from `templates/guardrails.md.template` |

---

*Version: 2.1.0 | Updated: 2026-02-10*
*Updated: coordinator + sub-agent pattern for fresh context per task*
