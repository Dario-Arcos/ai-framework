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

### tmux Not Installed

- **Cause**: Missing prerequisite
- **Fix**: `brew install tmux`
- **Verification**: `which tmux` returns a path

### Ghostty Not Available

- **Cause**: Missing prerequisite for cockpit
- **Fix**: `brew install --cask ghostty`
- **Verification**: `open -na Ghostty.app` launches without error

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
  - Missing `discovery.md` → Run `/sop-discovery`
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
  1. Run gate commands manually in the `shell` tmux window:
     ```bash
     npm test        # GATE_TEST
     npm run lint    # GATE_LINT
     npm run build   # GATE_BUILD
     ```
  2. Fix the failing command
  3. Update `.ralph/config.sh` if gate command is wrong
  4. Teammates will succeed on next attempt (TaskCompleted rejects, they retry)

### Cockpit Not Launching

- **Cause**: tmux or Ghostty issue, or launch-build.sh missing
- **Fix**:
  1. Verify `.ralph/launch-build.sh` exists and is executable
  2. If missing: copy from `templates/launch-build.sh.template`, `chmod +x`
  3. Check tmux is not already running a "ralph" session: `tmux ls`
  4. Kill stale session if needed: `tmux kill-session -t ralph`
  5. Re-launch: `bash .ralph/launch-build.sh`

### tmux Session Issues

- **Symptom**: Windows missing, panes not responding
- **Fix**:
  1. List sessions: `tmux ls`
  2. Attach to verify: `tmux attach -t ralph`
  3. Check window list: `Ctrl+B w` (inside tmux)
  4. If corrupted: kill and relaunch
     ```bash
     tmux kill-session -t ralph
     bash .ralph/launch-build.sh
     ```

### Orchestrator Tempted to Implement

- **Symptom**: Lead wants to write code directly instead of delegating
- **Fix**: Remember — teammates have persistent context and dedicated focus. Lead coordinates, doesn't implement.
- **Response template**: *"Teammates have persistent context and dedicated focus. Your role is coordination. Use SendMessage to guide them."*

### Circuit Breaker Triggered

- **Symptom**: Teammate stops claiming tasks
- **Cause**: MAX_CONSECUTIVE_FAILURES exceeded in `.ralph/failures.json`
- **Fix**:
  1. Check `.ralph/failures.json` for the affected teammate
  2. Identify the failing gate and fix root cause
  3. Reset failures: edit `.ralph/failures.json` to set `consecutive_failures: 0`
  4. Re-launch cockpit or spawn new teammate

---

## Monitoring Issues

### Cannot See Execution Progress

- **Cause**: Not using the right monitoring tools
- **Fix**: Use these read-only approaches:
  - `TaskList` — real-time task states
  - `Read(".ralph/metrics.json")` — aggregate counts
  - `Read(".ralph/failures.json")` — per-teammate failures
  - `tmux capture-pane -p -t ralph:team.0` — team window output

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

- **Cause**: Cockpit reads config at launch, not dynamically
- **Fix**:
  1. Verify config.sh syntax: `source .ralph/config.sh && echo "OK"`
  2. Stop current execution: `touch .ralph/ABORT`
  3. Wait for teammates to idle
  4. Remove abort: `rm .ralph/ABORT`
  5. Re-launch cockpit

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
- [agent-teams-architecture.md](agent-teams-architecture.md) - Architecture, hooks, cockpit
- [observability.md](observability.md) - Metrics, debugging
- [supervision-modes.md](supervision-modes.md) - Planning modes

---

*Troubleshooting reference for ralph-orchestrator.*
*Version: 2.0.0 | Updated: 2026-02-10*
