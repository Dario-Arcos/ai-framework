# Best Practices Reference

> Consolidated best practices for Ralph Orchestrator operation.
> See also: [supervision-modes.md](supervision-modes.md), [monitoring-pattern.md](monitoring-pattern.md), [configuration-guide.md](configuration-guide.md)

---

## Loop Execution

**Background execution required:**
```bash
# Correct: Use run_in_background=true
Bash(command="./loop.sh specs/{goal}/", run_in_background=true)

# Incorrect: Foreground execution risks timeout
Bash(command="./loop.sh")  # May be killed by timeout
```

**Monitor without blocking:**
```bash
# Check status without waiting
TaskOutput(task_id="{id}", block=false)

# Read full log for details
Read(file_path="logs/iteration-{N}.log")

# DO NOT use these (they block):
# tail -f logs/current.log  # Blocks indefinitely
# Bash with long timeout    # May kill process
```

> Cross-reference: [monitoring-pattern.md](monitoring-pattern.md) for complete monitoring strategies.

---

## Context Philosophy

The 40-60% context sweet spot is an **observation**, not a target to enforce:

- Atomic task design naturally stays within effective context range
- Control is INPUT-based (truncate scratchpad/guardrails before iteration)
- No post-hoc measurement or exit conditions based on context percentage

**Configuration**: Use `max_iterations` and `max_runtime` for limits, not context percentages.

> Cross-reference: [configuration-guide.md](configuration-guide.md) for all configuration options.
> Cross-reference: [backpressure.md](backpressure.md) for backpressure handling.

---

## Iteration Strategy

**When to let it iterate:**
- Complex multi-file changes
- Debugging cycles
- Tests failing
- Worker making measurable progress

**When to intervene:**
- Loop stuck on same error (3+ attempts)
- 3+ iterations on simple task
- Quality degrading instead of improving
- Red flags appearing in logs

> Cross-reference: [red-flags.md](red-flags.md) for warning signs requiring intervention.
> Cross-reference: [alternative-loops.md](alternative-loops.md) for loop execution strategies.

---

## Knowledge Capture

After every session verify:
1. `guardrails.md` has new Signs (if gotchas found)
2. `scratchpad.md` reflects final state

**Capture checklist:**
| Artifact | Check | Purpose |
|----------|-------|---------|
| guardrails.md | New Signs added? | Prevent repeat mistakes |
| scratchpad.md | State updated? | Resume point for next iteration |

> Cross-reference: [state-files.md](state-files.md) for state file management.

---

## Supervision Levels

| Mode | Use Case | Intervention |
|------|----------|--------------|
| Autonomous | Overnight runs, high confidence tasks | None until completion |
| Checkpoint (iterations) | Complex features, want visibility | Every N iterations |
| Checkpoint (milestones) | Multi-module features | At module boundaries |

**Mode selection criteria:**
- **Autonomous**: Confident in SOP, well-tested pipeline, low-risk changes
- **Checkpoint (iterations)**: New features, moderate complexity, want progress visibility
- **Checkpoint (milestones)**: Multi-module work, want review at natural boundaries

> Cross-reference: [supervision-modes.md](supervision-modes.md) for detailed mode documentation.
> Cross-reference: [mode-selection.md](mode-selection.md) for mode selection flowchart.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Foreground loops | Timeout kills process | Use `run_in_background=true` |
| Blocking monitors | Claude stuck waiting | Use `block=false` with TaskOutput |
| Context pollution | Worker context degraded | Update plan, don't pollute worker |
| Skip prerequisites | Missing SOP artifacts | Always validate Step 0 |
| Ignore red flags | Issues compound | Intervene at first sign |

---

## Quick Reference

**Essential commands:**
```bash
# Start loop
Bash(command="./loop.sh specs/{goal}/", run_in_background=true)

# Check status
TaskOutput(task_id="{id}", block=false)

# Read logs
Read(file_path="logs/iteration-{N}.log")

# Force iteration
echo "ITERATE" > specs/{goal}/control/iteration-trigger
```

**Context philosophy:**
- 40-60% sweet spot emerges from atomic task design
- INPUT-based control via `truncate-context.sh`
- No OUTPUT measurement or context-based exits

**Knowledge artifacts:**
- `guardrails.md`: Warning signs and rules
- `scratchpad.md`: Current state
