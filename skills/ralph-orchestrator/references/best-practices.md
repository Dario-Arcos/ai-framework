# Best Practices Reference

> Consolidated best practices for Ralph Orchestrator operation.
> See also: [supervision-modes.md](supervision-modes.md), [observability.md](observability.md), [configuration-guide.md](configuration-guide.md)

---

## Task Cycle Execution

**Agent Teams cockpit launch:**
```bash
# Correct: Launch via Agent Teams cockpit
Bash(command="bash .ralph/launch-build.sh", run_in_background=true)

# Incorrect: Foreground execution risks timeout
Bash(command="bash .ralph/launch-build.sh")  # May be killed by timeout
```

**Monitor without blocking:**
```bash
# Check status via TaskList
TaskList()

# Read teammate output
TaskOutput(task_id="{id}", block=false)

# DO NOT use these (they block):
# tail -f logs/current.log  # Blocks indefinitely
# Bash with long timeout    # May kill process
```

> Cross-reference: [observability.md](observability.md) for complete monitoring strategies.

---

## Context Philosophy

The 40-60% context sweet spot is an **observation**, not a target to enforce:

- Atomic task design naturally stays within effective context range
- Control is INPUT-based (trim guardrails before each task cycle)
- No post-hoc measurement or exit conditions based on context percentage

**Configuration**: Use `max_iterations` and `max_runtime` for limits, not context percentages.

> Cross-reference: [configuration-guide.md](configuration-guide.md) for all configuration options.
> Cross-reference: [backpressure.md](backpressure.md) for backpressure handling.

---

## Task Cycle Strategy

**When to let it continue:**
- Complex multi-file changes
- Debugging cycles
- Tests failing
- Teammate making measurable progress

**When to intervene:**
- Task cycle stuck on same error (3+ attempts)
- 3+ task cycles on simple task
- Quality degrading instead of improving
- Red flags appearing in logs

> Cross-reference: [red-flags.md](red-flags.md) for warning signs requiring intervention.
> Cross-reference: [alternative-loops.md](alternative-loops.md) for loop execution strategies.

---

## Knowledge Capture

After every session verify:
1. `guardrails.md` has new Signs (if gotchas found)
2. `guardrails.md` reflects final state (shared memory across teammates and sub-agents)

**Capture checklist:**
| Artifact | Check | Purpose |
|----------|-------|---------|
| guardrails.md | New Signs added? | Prevent repeat mistakes |
| guardrails.md | State updated? | Shared memory for teammates and sub-agents |

> Cross-reference: [state-files.md](state-files.md) for state file management.

---

## Supervision Levels

| Mode | Use Case | Intervention |
|------|----------|--------------|
| Autonomous | Overnight runs, high confidence tasks | None until completion |
| Checkpoint (task cycles) | Complex features, want visibility | Every N task cycles |

> Note: Checkpoint (milestones) mode is planned but NOT IMPLEMENTED.

**Mode selection criteria:**
- **Autonomous**: Confident in SOP, well-tested pipeline, low-risk changes
- **Checkpoint (task cycles)**: New features, moderate complexity, want progress visibility

> Cross-reference: [supervision-modes.md](supervision-modes.md) for detailed mode documentation.
> Cross-reference: [mode-selection.md](mode-selection.md) for mode selection flowchart.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Foreground launch | Timeout kills process | Use `run_in_background=true` |
| Blocking monitors | Claude stuck waiting | Use `block=false` with TaskOutput |
| Context pollution | Sub-agent context degraded | Update plan, don't pollute sub-agent |
| Skip prerequisites | Missing SOP artifacts | Always validate Step 0 |
| Ignore red flags | Issues compound | Intervene at first sign |

---

## Quick Reference

**Essential commands:**
```bash
# Launch Agent Teams cockpit
Bash(command="bash .ralph/launch-build.sh", run_in_background=true)

# Check status via TaskList
TaskList()

# Read teammate output
TaskOutput(task_id="{id}", block=false)
```

**Context philosophy:**
- 40-60% sweet spot emerges from atomic task design
- INPUT-based control via auto-compaction (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`)
- Fresh context via sub-agents — no OUTPUT measurement or context-based exits

**Knowledge artifacts:**
- `guardrails.md`: Warning signs, rules, and shared memory across teammates and sub-agents
