# Monitoring Pattern Reference

## Overview

This reference defines the monitoring role and allowed actions during ralph-orchestrator execution. Understanding this pattern is essential for maintaining role boundaries and preserving worker context advantage.

---

## Role During Execution: MONITOR ONLY

**Constraints:**
- You MUST become a MONITOR once the loop launches because workers need fresh context
- You MUST NOT write or edit code because this pollutes your context
- You MUST NOT run tests, builds, or lints because workers handle these
- You MUST NOT edit ANY files because state is owned by workers
- You MUST NOT spawn Task agents to implement because this duplicates work
- You MUST NOT research with WebFetch/WebSearch because workers research if needed

> **Role Boundary**: Once the loop launches, you become a **MONITOR** because workers have fresh 200K token context while your context is polluted. Workers implement BETTER at LOWER cost.

---

## Allowed Actions (EXHAUSTIVE)

**Constraints:**
- You MUST use only the permitted tool calls because any other action violates monitoring role
- You MUST use `run_in_background=True` for loop.sh because this enables non-blocking monitoring
- You SHOULD read status.json for loop state because this is the source of truth

```python
# ONLY these tool calls are permitted:
Bash("./loop.sh specs/{goal}/", run_in_background=True)  # Start loop
TaskOutput(task_id, block=False)  # Check progress
TaskOutput(task_id, block=True)   # Wait for completion
Read("status.json")               # Read loop state
Read("logs/*")                    # Read iteration logs
Read("specs/{goal}/implementation/plan.md")  # Check task status
```

---

## Prohibited Actions

**Constraints:**
- You MUST NOT use Write/Edit on ANY file because this modifies state workers own
- You MUST NOT use Bash that modifies state because npm, git, mkdir, etc. change project
- You MUST NOT use Task tool for implementation because this duplicates worker role
- You MUST NOT use Grep/Glob in source code because only logs/output are permitted
- You MUST NOT use research tools because workers research if needed

---

## If User Asks to Implement

**Constraints:**
- You MUST explain the monitoring session limitation because context is polluted
- You MUST offer plan update and restart because this is the valid path
- You MUST emphasize worker context advantage because this justifies the constraint

Respond with:

*"This session monitors ralph-orchestrator. To implement that, I'll update the plan
and restart the loop. Workers have fresh 200K token context - 10x better for
implementation. Want me to update the plan and restart?"*

---

## Monitoring Loop Pattern

**Constraints:**
- You MUST check status every 30-90 seconds because this provides regular updates
- You MUST adjust interval based on iteration duration because adaptive polling is efficient
- You SHOULD display dashboard to user because this communicates progress

```
1. result = Bash("./loop.sh specs/{goal}/", run_in_background=True)
2. task_id = result.task_id

3. REPEAT every 30-90 seconds:
   a. TaskOutput(task_id, block=False)
   b. Read("status.json")
   c. Display dashboard to user

4. When status != "running":
   TaskOutput(task_id, block=True)  # Get final output
```

---

## Dashboard Format

**Constraints:**
- You MUST include all key fields because this provides complete status
- You SHOULD use consistent formatting because this aids readability
- You MAY customize appearance because visual clarity matters

```
═══════════════════════════════════════════════
RALPH LOOP MONITOR
═══════════════════════════════════════════════
Status:     [running|complete|circuit_breaker]
Iteration:  N
Mode:       build
Specs:      specs/{goal}/
Branch:     feature-x
═══════════════════════════════════════════════
```

---

## Status Checking Utilities

**Constraints:**
- You MUST use status.sh for quick state checks because it formats output clearly
- You SHOULD use tail-logs.sh for real-time monitoring because it streams events

```bash
./status.sh              # View current status & metrics
./tail-logs.sh           # Real-time log following
```

---

## Reading Logs

**Constraints:**
- You MUST check logs/iteration.log for detailed events because this reveals worker behavior
- You SHOULD check logs/metrics.json for aggregated data because this shows trends
- You MUST check status.json for current state because this is the source of truth

Iteration logs are stored in `logs/` directory:
- `logs/iteration-{N}.log` - Full iteration output
- `logs/metrics.json` - Aggregated metrics
- `status.json` - Current loop state

---

## Context Philosophy

Ralph does NOT monitor context percentages. The INPUT-based approach (truncating files before iteration) ensures each iteration starts fresh without measuring output.

**Observability**: Track `num_turns` and `total_cost_usd` for session metrics, not context percentage.

---

## Troubleshooting

### Loop Not Starting

If loop fails to start:
- You SHOULD verify specs directory exists because missing specs causes failure
- You SHOULD check config.sh syntax because syntax errors prevent execution
- You MUST read error output from bash because this reveals root cause

### Status Not Updating

If status.json stops updating:
- You SHOULD check if loop process is running because hung loops don't update
- You SHOULD check for disk space issues because full disk prevents writes
- You MUST NOT assume loop is healthy without updates because silence indicates problem

### Dashboard Shows Stale Data

If dashboard displays old information:
- You SHOULD verify read operations are succeeding because file access may be blocked
- You SHOULD check timestamp in status.json because this reveals freshness
- You MUST increase polling frequency if updates are slow because this catches changes faster

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
