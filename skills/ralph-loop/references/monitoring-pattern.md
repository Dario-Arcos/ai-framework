# Monitoring Pattern

## Role During Execution: MONITOR ONLY

> **CRITICAL**: Once the loop launches, your role changes completely.
>
> You become a **MONITOR**. You do NOT:
> - Write or edit code
> - Run tests, builds, or lints
> - Edit ANY files
> - Spawn Task agents to implement
> - Research with WebFetch/WebSearch
>
> Workers have fresh 200K token context. You have polluted context.
> Workers implement BETTER at LOWER cost.

## Allowed Actions (EXHAUSTIVE)

```python
# ONLY these tool calls are permitted:
Bash("./loop.sh specs/{goal}/", run_in_background=True)  # Start loop
TaskOutput(task_id, block=False)  # Check progress
TaskOutput(task_id, block=True)   # Wait for completion
Read("status.json")               # Read loop state
Read("logs/*")                    # Read iteration logs
Read("specs/{goal}/implementation/plan.md")  # Check task status
```

## Forbidden Actions

- **ANY Write/Edit** to ANY file
- **ANY Bash** that modifies state (npm, git, mkdir, etc.)
- **Task tool** for implementation
- **Grep/Glob** in source code (only logs/output)
- **Research tools** (workers research if needed)

## If User Asks to Implement

Respond with:

*"This session monitors ralph-loop. To implement that, I'll update the plan
and restart the loop. Workers have fresh 200K token context - 10x better for
implementation. Want me to update the plan and restart?"*

## Monitoring Loop Pattern

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

## Dashboard Format

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

## Status Checking Utilities

```bash
./status.sh              # View current status & metrics
./tail-logs.sh           # Real-time log following
```

## Reading Logs

Iteration logs are stored in `logs/` directory:
- `logs/iteration-{N}.log` - Full iteration output
- `logs/metrics.json` - Aggregated metrics
- `status.json` - Current loop state

## Context Health Monitoring

Tracks `input_tokens` from Claude responses. Zones:
- **Green** (<60%): Healthy
- **Yellow** (60-80%): Warning displayed
- **Red** (>80%): EXIT_CONTEXT_EXHAUSTED
