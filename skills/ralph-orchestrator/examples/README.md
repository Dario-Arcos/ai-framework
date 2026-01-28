# Ralph Orchestrator Examples

End-to-end examples demonstrating ralph-orchestrator's two-flow architecture.

## Examples

| Example | Flow | Scenario |
|---------|------|----------|
| [forward-flow-rest-api.md](forward-flow-rest-api.md) | Forward | Build REST API from scratch |
| [reverse-flow-legacy-migration.md](reverse-flow-legacy-migration.md) | Reverse → Forward | Investigate + modernize legacy code |

## Flow Selection

**Forward Flow** - Use when:
- Building something new from an idea or spec
- Starting from scratch or clean slate
- You know WHAT you want

**Reverse Flow** - Use when:
- Investigating existing code/artifact
- Understanding before changing
- Dealing with legacy systems

## Decision Tree

```
Need to work on something?
    │
    ├── No existing code → Forward Flow
    │
    └── Existing code → Do you understand it?
                            │
                            ├── No → Reverse Flow
                            │
                            └── Yes, want to improve? → Reverse → Forward
```

## Key Principle

**ONE question at a time** during planning phases. Never batch multiple questions.

---

See [SKILL.md](../SKILL.md) for complete reference.
