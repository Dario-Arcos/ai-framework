# Ralph-Orchestrator References

Quick navigation for detailed documentation.

## Core Workflow

| File | Description |
|------|-------------|
| [ralph-orchestrator-flow.md](ralph-orchestrator-flow.md) | Complete step-by-step flow diagram |
| [sop-integration.md](sop-integration.md) | SOP skill connections and integration points |
| [mode-selection.md](mode-selection.md) | Decision flowcharts for choosing modes |

## Execution

| File | Description |
|------|-------------|
| [monitoring-pattern.md](monitoring-pattern.md) | How to monitor execution loops |
| [supervision-modes.md](supervision-modes.md) | AFK / HITL / Checkpoint modes |
| [quality-gates.md](quality-gates.md) | TDD and quality gate requirements |
| [backpressure.md](backpressure.md) | Circuit breakers and rate limiting |

## State & Knowledge

| File | Description |
|------|-------------|
| [state-files.md](state-files.md) | Purpose of each state file |
| [memories-system.md](memories-system.md) | Memory architecture overview |
| [observability.md](observability.md) | Logs, metrics, and debugging |

## Risk & Troubleshooting

| File | Description |
|------|-------------|
| [red-flags.md](red-flags.md) | Dangerous patterns to avoid |

## Advanced

| File | Description |
|------|-------------|
| [alternative-loops.md](alternative-loops.md) | Specialized loop variants |
| [configuration-guide.md](configuration-guide.md) | All configuration options |
| [pressure-testing.md](pressure-testing.md) | Adversarial and stress tests |

---

## Quick Reference

| Need | Go To |
|------|-------|
| "How do I start?" | [ralph-orchestrator-flow.md](ralph-orchestrator-flow.md) |
| "Which supervision mode?" | [supervision-modes.md](supervision-modes.md) |
| "How to select mode?" | [mode-selection.md](mode-selection.md) |
| "Something looks wrong" | [red-flags.md](red-flags.md) |
| "Configure options" | [configuration-guide.md](configuration-guide.md) |
| "Monitor execution" | [monitoring-pattern.md](monitoring-pattern.md) |
| "Debug issues" | [observability.md](observability.md) |
| "Connect with SOPs" | [sop-integration.md](sop-integration.md) |

---

## File Overview (14 files)

```
references/
├── Core Workflow
│   ├── ralph-orchestrator-flow.md   # Main flow diagram
│   ├── sop-integration.md           # SOP connections
│   └── mode-selection.md            # Mode decision trees
├── Execution
│   ├── monitoring-pattern.md        # Loop monitoring
│   ├── supervision-modes.md         # AFK/HITL/Checkpoint
│   ├── quality-gates.md             # TDD gates
│   └── backpressure.md              # Circuit breakers
├── State & Knowledge
│   ├── state-files.md               # File purposes
│   ├── memories-system.md           # Memory architecture
│   └── observability.md             # Logs & metrics
├── Risk
│   └── red-flags.md                 # Dangerous patterns
└── Advanced
    ├── alternative-loops.md         # Specialized loops
    ├── configuration-guide.md       # All options
    └── pressure-testing.md          # Stress tests
```
