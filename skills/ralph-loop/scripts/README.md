# Ralph Loop Scripts

## Main Loop

```bash
./loop.sh              # Build mode, unlimited iterations
./loop.sh 20           # Build mode, max 20 iterations
./loop.sh plan         # Planning mode, unlimited iterations
./loop.sh plan 5       # Planning mode, max 5 iterations
```

## Observability Utilities

### View Status & Metrics

```bash
./status.sh
```

Shows:
- Current status (running/complete/circuit_breaker)
- Iteration count and mode
- Metrics (success rate, durations)
- Recent activity log

### View Claude Output

```bash
./tail-logs.sh              # Show last iteration output
./tail-logs.sh 3            # Show iteration 3 output
./tail-logs.sh follow       # Follow iteration log in real-time
```

## Generated Artifacts

Ralph generates the following for observability:

```
logs/
  iteration.log      # Timestamped events
  metrics.json       # Aggregated statistics

claude_output/
  iteration_001.txt  # Complete Claude output per iteration
  iteration_002.txt
  ...

status.json          # Current loop state
errors.log           # Failed iteration details
```

## Example Outputs

### status.json
```json
{
  "current_iteration": 5,
  "consecutive_failures": 0,
  "status": "running",
  "mode": "build",
  "branch": "feature/counter",
  "timestamp": "2026-01-21T18:30:45Z"
}
```

### logs/metrics.json
```json
{
  "total_iterations": 5,
  "successful": 4,
  "failed": 1,
  "total_duration_seconds": 725,
  "avg_duration_seconds": 145
}
```

### logs/iteration.log
```
[2026-01-21T18:15:00Z] ITERATION 1 START
[2026-01-21T18:17:30Z] ITERATION 1 SUCCESS - Duration: 150s
[2026-01-21T18:17:31Z] ITERATION 2 START
[2026-01-21T18:19:45Z] ITERATION 2 SUCCESS - Duration: 134s
[2026-01-21T18:19:46Z] ITERATION 3 START
[2026-01-21T18:21:50Z] ITERATION 3 FAILED - Exit: 1 - Duration: 124s
```

## Dependencies

Required commands (available on macOS by default):
- `jq` - JSON processing
- `bc` - Arithmetic calculations
- `date` - Timestamp generation
