# Observability Reference

Ralph generates structured logs for monitoring and debugging.

## Output Artifacts

| Artifact | Purpose |
|----------|---------|
| `logs/iteration.log` | Timestamped iteration events |
| `logs/metrics.json` | Success rate, durations, totals |
| `claude_output/iteration_NNN.txt` | Complete Claude output per iteration |
| `status.json` | Current loop state |
| `errors.log` | Failed iteration details |

---

## Utilities

```bash
./status.sh           # View current status & metrics
./tail-logs.sh        # Show last iteration output
./tail-logs.sh 3      # Show iteration 3 output
./tail-logs.sh follow # Real-time log following
```

---

## Interactive Monitoring

Use an active Claude Code session as observer:

- Cost: ~$0.48 per 2 hours
- Won't compact in sessions <4h
- No interference with bash loops (independent processes)

### Monitoring Pattern

```
1. result = Bash("./loop.sh", run_in_background=true)
2. while status not in [complete, failed, stopped]:
     TaskOutput(task_id, block=false, timeout=interval*1000)
     Read("status.json")
     display_dashboard()
     interval = clamp(last_duration/3, 30, 90)
3. TaskOutput(task_id, block=true)
```

---

## Status File Format

```json
{
  "current_iteration": 10,
  "consecutive_failures": 0,
  "status": "running",
  "mode": "build",
  "branch": "feature-x",
  "timestamp": "2026-01-25T17:31:41Z"
}
```

**Status values:** `running`, `complete`, `max_iterations`, `circuit_breaker`

---

## Metrics File Format

```json
{
  "total_iterations": 10,
  "successful": 9,
  "failed": 1,
  "total_duration_seconds": 1800,
  "avg_duration_seconds": 180
}
```

---

## Token Usage (Experimental)

To extract token usage from Claude's JSON output:

```bash
# Parse tokens from stream-json output
cat claude_output/iteration_001.txt | \
  grep '"type":"result"' | \
  jq -r '.usage.input_tokens, .usage.output_tokens'
```

**Note:** Token metrics require `--output-format=stream-json` flag.

---

## Log Analysis

```bash
# Count successful vs failed iterations
grep -c "SUCCESS" logs/iteration.log
grep -c "FAILED" logs/iteration.log

# Find slowest iteration
grep "Duration:" logs/iteration.log | sort -t: -k4 -rn | head -1

# Extract all task completions
grep "Task:" logs/iteration.log
```

---

## Debugging Failed Iterations

1. Check `errors.log` for failure details
2. Read `claude_output/iteration_NNN.txt` for full context
3. Look for patterns in Signs (guardrails.md)
4. Review `status.json` for circuit breaker state
