# Ralph Loop Scripts

## Installation

```bash
# From skill directory
./install.sh /path/to/your/project
```

## Main Loop

```bash
./loop.sh specs/{goal}/           # Execute plan, unlimited iterations
./loop.sh specs/{goal}/ 20        # Execute plan, max 20 iterations
./loop.sh specs/{goal}/ --monitor # Execute with tmux split dashboard
```

## Observability

### Live Dashboard

```bash
./monitor.sh              # Continuous refresh dashboard
./monitor.sh --stream     # Stream worker output in real-time
./monitor.sh --status     # One-shot status view
./monitor.sh --logs       # Tail iteration log
```

## Generated Artifacts

```
logs/
  iteration.log           # Timestamped events
  metrics.json            # Aggregated statistics
  iteration-{N}-output.log # Raw Claude output per iteration

status.json               # Current loop state
errors.log                # Failed iteration details
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

## Dependencies

- `claude` - Claude Code CLI
- `git` - Version control
- `jq` - JSON processing
- `bc` - Arithmetic calculations
- `bash` 4+ - Shell
