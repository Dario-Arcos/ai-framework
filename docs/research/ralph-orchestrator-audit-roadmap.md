# Ralph-Loop vs Ralph-Orchestrator: Audit Roadmap

> **Generated**: 2026-01-26
> **Source**: https://github.com/mikeyobrien/ralph-orchestrator
> **Scope**: 14 audit areas across 5 parallel analysis tracks

---

## Executive Summary

| Dimension | ralph-loop | ralph-orchestrator | Verdict |
|-----------|-----------|-------------------|---------|
| **Architecture** | Bash scripts (~600 LOC) | Rust binary (7 crates, ~15K LOC) | Different philosophy |
| **Safety** | 6 unique features | 4 standard features | **ralph-loop SUPERIOR** |
| **Modes/Hats** | 3 simple modes | Event-driven hat system | Gap exists |
| **CLI Coverage** | 41% of equivalent features | Full CLI | Gap exists |
| **Observability** | File-based | Event-driven + TUI | Gap exists |
| **Multi-Loop** | Single loop only | Parallel worktrees | Gap exists |

**Key Insight**: ralph-loop consciously adopts a simpler architecture. This is a **design decision**, not a limitation. The "Disk is state" and "Fresh context per iteration" principles make many ralph-orchestrator features unnecessary.

---

## Consolidated GAP Analysis

### P0 - Critical (Implement Immediately)

| ID | GAP | Impact | Complexity | Source |
|----|-----|--------|------------|--------|
| **CLI-01** | `--dry-run` flag missing | Cannot validate config without spending tokens | S | Agent 5 |
| **CLI-02** | `--continue` flag missing (scratchpad reset) | Loss of context on restarts | S | Agent 5 |
| **CLI-06** | `ralph clean` missing | Artifact accumulation, disk full | S | Agent 5 |
| **OBS-01** | No event markers in logs | Limits root cause analysis | S | Agent 4 |

**Estimated Effort**: 1-2 days total

### P1 - High Priority (Quick Wins)

| ID | GAP | Impact | Complexity | Source |
|----|-----|--------|------------|--------|
| **PRESET-01** | No preset system | Forces manual PROMPT_*.md editing | S | Agent 3 |
| **PRESET-02** | Missing debug preset | Common workflow unsupported | S | Agent 3 |
| **PRESET-03** | Missing refactor preset | Common workflow unsupported | S | Agent 3 |
| **PRESET-04** | Missing review preset | Common workflow unsupported | S | Agent 3 |
| **MEM-01** | `memories.sh delete` missing | Cannot remove obsolete memories | S | Agent 2 |
| **MEM-02** | `memories.sh show` missing | Cannot view specific memory by ID | S | Agent 2 |
| **MEM-04** | `--recent N` flag missing | Cannot prioritize recent memories | S | Agent 2 |
| **CONF-01** | Confession structure not validated | Silent parsing errors | S | Agent 2 |
| **CLI-08** | Unified CLI entry point missing | 6 separate scripts, poor discoverability | M | Agent 5 |

**Estimated Effort**: 2-3 days total

### P2 - Medium Priority (Strategic Value)

| ID | GAP | Impact | Complexity | Source |
|----|-----|--------|------------|--------|
| **ARCH-01** | No lightweight event pub/sub | Limits automation of complex workflows | M | Agent 1 |
| **ARCH-03** | No backend override per mode | Same model for all modes | S | Agent 1 |
| **ARCH-06** | No auto-triggers between modes | Manual discover→plan→build invocation | S | Agent 1 |
| **TASK-01** | No task dependencies (`blocked_by`) | Cannot express task ordering | M | Agent 2 |
| **TASK-04** | Fragile markdown task parsing | Regex failures on edge cases | M | Agent 2 |
| **OBS-02** | Enhanced status.sh (watch mode) | Requires multiple terminals | M | Agent 4 |
| **OBS-03** | Session recording for replay | Limited post-mortem analysis | M | Agent 4 |
| **SAFE-01** | No idle timeout | Cannot detect "stuck thinking" | S | Agent 4 |
| **SAFE-02** | No checkpoint interval | No recovery after crash | M | Agent 4 |
| **CONF-02** | Multi-backend fallback | Rate limit resilience | M | Agent 3 |
| **CONF-03** | Config validation | Silent errors on typos | S | Agent 3 |

**Estimated Effort**: 1-2 weeks total

### P3 - Low Priority (Evaluate Later)

| ID | GAP | Impact | Complexity | Source |
|----|-----|--------|------------|--------|
| **MULTI-01** | Multi-loop concurrency (worktrees) | 3-5x throughput for large projects | XL | Agent 4 |
| **CLI-03** | Parallel loop management (`loops list/attach`) | Team workflows | L | Agent 5 |
| **CLI-04** | Event history viewer | Integration with external systems | M | Agent 5 |
| **CLI-07** | Runtime config override (`-c`) | Special case flexibility | S | Agent 5 |
| **PRESET-05** | Specialized presets (incident-response, migration-safety) | Niche use cases | L | Agent 3 |

**Estimated Effort**: 2+ weeks if pursued

### NOT IMPLEMENT (By Design)

| ID | Feature | Reason |
|----|---------|--------|
| **TUI-01** | Terminal UI with ratatui | Adds complexity without proportional value in fresh-context architecture |
| **YAML-01** | YAML config format | Adds dependency without benefit over bash source |
| **COMPOSE-01** | Hat composition (multiple simultaneous) | "Disk is state" makes parallel states unnecessary |
| **BUDGET-01** | Memory token budget | Context rotation eliminates need |
| **CONFESS-02** | Separate Builder→Confessor pipeline | Current inline confidence threshold provides same value |

---

## Detailed Recommendations by Area

### 1. Architecture (Agent 1)

**Current State**: Bash loop + Claude CLI
**Gap**: No event system, no type safety in markers

**Recommendations**:
```bash
# GAP-ARCH-01: Lightweight event system
emit_event() {
  local topic="$1" payload="$2"
  echo "{\"topic\":\"$topic\",\"payload\":$payload,\"ts\":\"$(date -u +%FT%TZ)\"}" >> .ralph/events.log
}

# GAP-ARCH-03: Backend override per mode
MODEL_DISCOVER="${MODEL_DISCOVER:-sonnet}"  # Cheaper for brainstorming
MODEL_PLAN="${MODEL_PLAN:-opus}"            # Best for analysis
MODEL_BUILD="${MODEL_BUILD:-opus}"          # Best for implementation

# GAP-ARCH-06: Auto-transition (optional)
AUTO_TRANSITION=true
if [ "$MODE" = "discover" ] && [ "$AUTO_TRANSITION" = "true" ]; then
    exec "$0" plan
fi
```

### 2. Memories System (Agent 2)

**Current State**: `memories.sh add/search/list`
**Gap**: Missing delete, show, recent filter

**Recommendations**:
```bash
# Add to memories.sh:
cmd_delete() {
  local id="$1"
  sed -i '' "/^### $id/,/^###/d" "$MEMORIES_FILE"
}

cmd_show() {
  local id="$1"
  sed -n "/^### $id/,/^###/p" "$MEMORIES_FILE" | head -n -1
}

# Add --recent flag to list command
```

### 3. Tasks System (Agent 2)

**Current State**: Markdown checkboxes in IMPLEMENTATION_PLAN.md
**Gap**: No dependencies, fragile parsing

**Recommendations**:
```markdown
# Standardized task format:
- [ ] task-001: Database schema | Size: S | Files: 2
  Acceptance: Tables exist with correct columns
  blocked_by: []

- [ ] task-002: User model | Size: M | Files: 3
  Acceptance: bcrypt hashing works
  blocked_by: [task-001]
```

### 4. Preset System (Agent 3)

**Current State**: 3 modes (discover/plan/build)
**Gap**: No modular preset selection

**Recommendations**:
```bash
# New presets to create:
PROMPT_debug.md      # Debugging workflow
PROMPT_refactor.md   # Refactoring workflow
PROMPT_review.md     # Code review workflow
PROMPT_research.md   # Research with web access

# Usage:
./loop.sh --preset debug
./loop.sh --preset refactor
```

### 5. Safety Features (Agent 4)

**Current State**: 6 unique safety features (SUPERIOR to ralph-orchestrator)
- Circuit breaker (3 failures)
- Task abandonment detection (3 attempts)
- Double completion verification (2x COMPLETE)
- Loop thrashing detection (A→B→A→B)
- Context health monitoring
- Runtime limit

**Gap**: Missing idle timeout, checkpoint

**Recommendations**:
```bash
# Add to config.sh:
IDLE_TIMEOUT="${IDLE_TIMEOUT:-300}"        # 5 min default
CHECKPOINT_INTERVAL="${CHECKPOINT_INTERVAL:-10}"  # Every 10 iterations
```

### 6. Observability (Agent 4)

**Current State**: File-based (status.json, logs/, claude_output/)
**Gap**: No structured events, no watch mode

**Recommendations**:
```bash
# Phase 1: Event markers in loop.sh
emit_event "iteration.start" "{\"iteration\":$ITERATION}"
emit_event "iteration.complete" "{\"task\":\"$TASK_NAME\",\"duration\":$DURATION}"
emit_event "safety.circuit_breaker" "{\"failures\":$FAILURES}"

# Phase 2: Enhanced status.sh
./status.sh --watch    # Refresh every 5s
./status.sh --dashboard  # Compact view
```

### 7. CLI & Developer Experience (Agent 5)

**Current State**: 6 separate scripts, 41% feature coverage
**Gap**: No unified entry point, no dry-run, no continue

**Recommendations**:
```bash
# Create unified CLI: scripts/ralph
ralph run                    # Build mode
ralph run --dry-run          # Validate without executing
ralph run --continue         # Preserve scratchpad
ralph plan "Add auth"        # Plan with inline idea
ralph status                 # Current state
ralph logs -f                # Follow logs
ralph memories add ...       # Manage memories
ralph clean                  # Remove artifacts
```

---

## Implementation Roadmap

### Sprint 1: CLI Foundation (1-2 days)

| Task | Files | LOC |
|------|-------|-----|
| Create unified `ralph` dispatcher | `scripts/ralph` | ~50 |
| Add `--dry-run` flag | `loop.sh` | ~20 |
| Add `--continue` flag | `loop.sh` | ~15 |
| Create `ralph clean` | `scripts/clean.sh` | ~30 |
| Add event markers | `loop.sh` | ~30 |

**Deliverable**: Unified CLI with critical missing features

### Sprint 2: Memories & Presets (2-3 days)

| Task | Files | LOC |
|------|-------|-----|
| Add `delete` command | `memories.sh` | ~15 |
| Add `show` command | `memories.sh` | ~20 |
| Add `--recent` flag | `memories.sh` | ~15 |
| Create debug preset | `PROMPT_debug.md` | ~100 |
| Create refactor preset | `PROMPT_refactor.md` | ~100 |
| Create review preset | `PROMPT_review.md` | ~100 |
| Add `--preset` flag | `loop.sh` | ~30 |

**Deliverable**: Enhanced memories CLI + 3 new presets

### Sprint 3: Observability & Safety (3-5 days)

| Task | Files | LOC |
|------|-------|-----|
| Enhanced status.sh (watch mode) | `status.sh` | ~80 |
| Session recording | `loop.sh` | ~60 |
| Idle timeout | `loop.sh` | ~30 |
| Checkpoint interval | `loop.sh` | ~50 |
| Backend override per mode | `config.sh.template`, `loop.sh` | ~40 |
| Auto-transition option | `loop.sh` | ~30 |

**Deliverable**: Complete observability + safety parity

### Sprint 4+ (Optional): Advanced Features

Only if needed based on actual usage:
- Multi-loop concurrency (XL effort)
- Task dependencies (M effort)
- Event pub/sub system (M effort)

---

## Philosophical Alignment

### What ralph-loop Gets Right

1. **Fresh Context Is Reliability** - Each iteration clears context, no pollution
2. **Disk Is State, Git Is Memory** - Files are the handoff mechanism
3. **The Plan Is Disposable** - Regeneration costs one planning loop
4. **Let Ralph Ralph** - Sit *on* the loop, not *in* it

### Where ralph-orchestrator Over-Engineers

1. **TUI** - Adds complexity for marginal monitoring benefit
2. **Hat Composition** - Multiple simultaneous personas unnecessary with atomic iterations
3. **Event Bus** - File-based events sufficient for most use cases
4. **Multi-Backend** - Claude Opus is best for development; fallback rarely needed

### Recommended Philosophy

> "ralph-orchestrator is an enterprise framework; ralph-loop is a script that works."

**The 80/20 rule applies**: ralph-loop covers 80% of use cases with 20% of complexity. The remaining 20% of use cases would justify migrating to ralph-orchestrator, not complicating loop.

---

## Success Metrics

After implementing P0+P1:

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| CLI Feature Coverage | 41% | ~60% | Achieved |
| Time to Validate Config | 30s + $0.05 | 0s + $0 | Achieved |
| Scripts to Learn | 6 | 1 | Achieved |
| Preset Workflows | 3 | 6+ | Achieved |
| Memory Management | Basic | Complete | Achieved |

---

## Appendix: Source Analysis Summary

| Agent | Area | Key Finding |
|-------|------|-------------|
| Agent 1 | Architecture + Hats + Events | Event system is main gap; type safety secondary |
| Agent 2 | Memories + Tasks + Backpressure | CLI operations missing; backpressure adequate |
| Agent 3 | Presets + Config + TUI | Preset system high value; TUI not needed |
| Agent 4 | Multi-loop + Confession + Safety + Observability | Safety SUPERIOR; observability needs events |
| Agent 5 | CLI + Developer Experience | 41% coverage; unified CLI recommended |

---

*Generated by 5 parallel Opus subagents analyzing 14 audit areas*
