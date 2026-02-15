# Troubleshooting Reference

Quick reference for common issues and their solutions during ralph-orchestrator operation.

---

## Infrastructure Issues

### Missing config.sh

- **Cause**: Incomplete installation or corrupted setup
- **Fix**: Copy from templates: `cp templates/config.sh.template .ralph/config.sh`
- **Verification**: Check that `.ralph/config.sh` exists and is valid shell

### Missing guardrails.md

- **Cause**: Partial installation
- **Fix**: Copy from templates: `cp templates/guardrails.md.template .ralph/guardrails.md`
- **Verification**: File exists at `.ralph/guardrails.md`

### Agent Teams Flag Not Set

- **Cause**: Environment variable missing
- **Fix**: `export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (add to shell profile for persistence)
- **Verification**: `echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` returns `1`

---

## Planning Issues

### User unsure which flow

- **Symptom**: User cannot decide between Forward and Reverse flow
- **Fix**: Ask clarifying questions:
  - **Forward** = Building something new (feature, improvement, project)
  - **Reverse** = Understanding existing code/artifact before modifying

### Planning taking too long

- **Cause**: Too many clarifying questions or research rabbit holes
- **Fix**: Set time expectations upfront:
  - **Discovery**: 10-20 minutes
  - **Planning**: 30-60 minutes
- **Prevention**: Stay focused on essentials, defer edge cases

### Missing SOP artifacts

- **Symptom**: Prerequisites validation fails
- **Cause**: Skipped or incomplete SOP phase
- **Fix**: Execute the missing SOP skill:
  - Missing `referents/catalog.md` → Run `/sop-reverse` with `search_mode="referent"`
  - Missing `detailed-design.md` → Run `/sop-planning`
  - Missing task files → Run `/sop-task-generator`

---

## Execution Issues

### Teammate Not Claiming Tasks

- **Cause**: No PENDING tasks, or TeammateIdle hook not firing
- **Fix**:
  1. `TaskList` — verify tasks exist with PENDING status
  2. Check `.code-task.md` files have `Status: PENDING` header
  3. Check `.ralph/failures.json` — circuit breaker may have triggered
  4. Verify TeammateIdle hook is registered in `hooks/hooks.json`

### Gates Failing for All Teammates

- **Cause**: Misconfigured gate commands, missing dependencies
- **Fix**:
  1. Run gate commands manually:
     ```bash
     npm test        # GATE_TEST
     npm run lint    # GATE_LINT
     npm run build   # GATE_BUILD
     ```
  2. Fix the failing command
  3. Update `.ralph/config.sh` if gate command is wrong
  4. Teammates will succeed on next attempt (TaskCompleted rejects, they retry)

### Orchestrator Tempted to Implement

- **Symptom**: Lead wants to write code directly instead of delegating
- **Fix**: Remember — each teammate gets fresh 200K context and dedicated focus on a single task. Lead coordinates, doesn't implement.
- **Response template**: *"Each teammate has fresh 200K context for their task. Your role is coordination. Use SendMessage to guide them."*

### Circuit Breaker Triggered

- **Symptom**: Teammate stops claiming tasks
- **Cause**: MAX_CONSECUTIVE_FAILURES exceeded in `.ralph/failures.json`
- **Fix**:
  1. Check `.ralph/failures.json` for the affected teammate
  2. Identify the failing gate and fix root cause
  3. Reset failures: edit `.ralph/failures.json` and set the failing teammate's value to 0, e.g., `{"teammate-1": 0}`
  4. Spawn new teammate

---

## Monitoring Issues

### Cannot See Execution Progress

- **Cause**: Not using the right monitoring tools
- **Fix**: Use these read-only approaches:
  - `TaskList` — real-time task states
  - `Read(".ralph/metrics.json")` — aggregate counts
  - `Read(".ralph/failures.json")` — per-teammate failures
  - `SendMessage` — query specific teammate for status

### Metrics Show High Failure Rate

If success rate drops below 80%:
- You SHOULD review `.ralph/guardrails.md` for common issues
- You SHOULD check task sizing (may be too large)
- You SHOULD verify gate commands work manually
- You MAY reduce MAX_TEAMMATES to reduce resource contention

---

## Configuration Issues

### Quality Gates Failing Unexpectedly

- **Cause**: Misconfigured gate commands in `.ralph/config.sh`
- **Fix**: Verify gate commands work manually:
  ```bash
  npm test        # GATE_TEST
  npm run lint    # GATE_LINT
  npm run build   # GATE_BUILD
  ```

### Configuration Not Taking Effect

- **Cause**: Config is read at teammate spawn, not dynamically
- **Fix**:
  1. Verify config.sh syntax: `source .ralph/config.sh && echo "OK"`
  2. Stop current execution: `touch .ralph/ABORT`
  3. Wait for teammates to idle
  4. Remove abort: `rm .ralph/ABORT`
  5. Spawn new teammates (they'll read updated config)

---

## Quick Diagnosis Checklist

When something goes wrong:

1. [ ] `TaskList` — What are the task states?
2. [ ] `Read(".ralph/failures.json")` — Which teammates are failing?
3. [ ] `Read(".ralph/metrics.json")` — What's the success rate?
4. [ ] Verify `.ralph/config.sh` — Is configuration correct?
5. [ ] Check `.ralph/guardrails.md` — Any known gotchas?
6. [ ] Review `.ralph/agents.md` — Is project context complete?

---

## See Also

- [configuration-guide.md](configuration-guide.md) - All configuration options
- [agent-teams-architecture.md](agent-teams-architecture.md) - Architecture, hooks, execution model
- [observability.md](observability.md) - Metrics, debugging
- [supervision-modes.md](supervision-modes.md) - Planning modes

---

*Troubleshooting reference for ralph-orchestrator.*
*Version: 2.0.0 | Updated: 2026-02-15*
