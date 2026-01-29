# Troubleshooting Reference

Quick reference for common issues and their solutions during ralph-orchestrator operation.

---

## Infrastructure Issues

### Missing loop.sh

- **Cause**: Infrastructure not installed in project
- **Fix**: Run `./skills/ralph-orchestrator/scripts/install.sh /path/to/project`
- **Verification**: Check that `./loop.sh` exists in project root

### Missing config.sh

- **Cause**: Incomplete installation or corrupted setup
- **Fix**: Re-run `./skills/ralph-orchestrator/scripts/install.sh`
- **Verification**: Check that `.ralph/config.sh` exists

### Missing guardrails.md or scratchpad.md

- **Cause**: Partial installation
- **Fix**: Re-run install script, which creates all required files
- **Verification**: All files listed in install output exist

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

### Workers failing on same task repeatedly

- **Cause**: Task too complex or missing context in AGENTS.md
- **Fix**:
  1. Read logs in `logs/` directory for error details
  2. Update AGENTS.md with missing project context
  3. Consider breaking task into smaller subtasks
  4. Add relevant Sign to `guardrails.md` if technical gotcha found

### Orchestrator tempted to implement

- **Symptom**: Urge to write code directly instead of delegating
- **Fix**: Remember - Workers have 200K fresh context (10x better than polluted orchestrator context). Update the plan instead of implementing.
- **Response template**: *"Workers have fresh 200K token context. Your intervention pollutes. Update plan instead."*

### Loop fails mid-execution

- **Fix**:
  1. Check `logs/` directory for error details
  2. Read last iteration output
  3. Identify root cause (config error, missing dependency, etc.)
  4. Fix the issue
  5. Restart loop (do not start fresh - continuity matters)

### Loop seems stuck

- **Symptom**: Same task attempted 3+ times without progress
- **Cause**: Missing context, circular dependency, or impossible task
- **Fix**:
  1. Check `status.json` for current state
  2. Read recent logs for patterns
  3. Consider intervention:
     - Update AGENTS.md with missing context
     - Break task into subtasks
     - Skip task if truly blocked

---

## Monitoring Issues

### Cannot see loop progress

- **Cause**: Loop running in background without monitoring
- **Fix**: Use these read-only commands:
  ```python
  TaskOutput(task_id, block=False)  # Check background task
  Read("status.json")               # Current state
  Read("logs/iteration-N.log")      # Specific iteration
  ```

### Log files too large

- **Cause**: Long-running loops accumulate logs
- **Fix**: Focus on recent iterations only
- **Prevention**: Clean old logs between major sessions

---

## Configuration Issues

### Quality gates failing unexpectedly

- **Cause**: Misconfigured gate commands in `.ralph/config.sh`
- **Fix**: Verify gate commands work manually:
  ```bash
  npm test        # GATE_TEST
  npm run lint    # GATE_LINT
  npm run build   # GATE_BUILD
  ```

### Circuit breaker triggered

- **Symptom**: Loop stops after consecutive failures
- **Cause**: MAX_CONSECUTIVE_FAILURES (default: 3) exceeded
- **Fix**:
  1. Check logs for pattern of failures
  2. Fix root cause
  3. Restart loop

---

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue to next task |
| 1 | Task failed | Check logs, update context |
| 2 | Config error | Fix `.ralph/config.sh` |
| 3 | Prerequisites missing | Run install.sh |
| 4 | Circuit breaker | Too many failures, manual intervention needed |

---

## Quick Diagnosis Checklist

When something goes wrong:

1. [ ] Check `status.json` - What's the current state?
2. [ ] Read latest log in `logs/` - What was the last action?
3. [ ] Verify `.ralph/config.sh` - Is configuration correct?
4. [ ] Check `guardrails.md` - Any known gotchas?
5. [ ] Review AGENTS.md - Is project context complete?

---

## See Also

- [configuration-guide.md](configuration-guide.md) - All configuration options and exit codes
- [monitoring-pattern.md](monitoring-pattern.md) - How to monitor execution properly
- [supervision-modes.md](supervision-modes.md) - AFK vs Checkpoint vs HITL modes

---

*Troubleshooting reference for ralph-orchestrator.*
*Version: 1.0.0 | Updated: 2026-01-28*
