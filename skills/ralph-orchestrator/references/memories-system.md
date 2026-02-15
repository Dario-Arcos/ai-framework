# Memory Architecture

> **Status**: Ralph uses a distributed memory architecture with structured format in guardrails.md.

## Overview

Ralph uses a **distributed memory architecture** where different types of learnings are stored in appropriate locations based on their scope and permanence.

## Memory Components

| Component | Scope | Lifetime | Purpose |
|-----------|-------|----------|---------|
| `.ralph/guardrails.md` | Team | Session | Fixes, decisions, patterns, current state (shared memory) |
| `.ralph/specs/design/` | Feature | Permanent | Architectural decisions |
| `.ralph/agents.md` | Project | Permanent | Build commands, patterns, conventions |
| Git history | All | Permanent | Complete audit trail |

## Structured Guardrails (New Format)

Guardrails now supports typed memory sections:

```markdown
# Guardrails

## Fixes
### fix-1737372000-a1b2
> npm test fails: run npm build first
<!-- tags: build, test | created: 2024-01-20 -->

## Decisions
### decision-1737372100-b2c3
> Chose TailwindCSS over styled-components for bundle size
<!-- tags: css, performance | created: 2024-01-20 -->

## Patterns
### pattern-1737372200-c3d4
> All API handlers return { success: boolean, data?: T }
<!-- tags: api, types | created: 2024-01-20 -->
```

### Memory ID Format

```
{type}-{unix_timestamp}-{4_hex_chars}
```

### Memory Types

| Type | Section | Use For |
|------|---------|---------|
| `fix` | `## Fixes` | Solutions to recurring problems |
| `decision` | `## Decisions` | Architectural choices with rationale |
| `pattern` | `## Patterns` | Codebase conventions discovered |

## Configuration

In `.ralph/config.sh`:

```bash
MEMORIES_ENABLED=true   # Enable structured memory format
```

> **MEMORIES_BUDGET (deprecated):** No enforcement mechanism was ever implemented. Guardrails.md grows naturally (~1 entry per task, bounded by session scope). Reviewer teammates validate entry accuracy via CORRECTION entries (see PROMPT_reviewer.md Phase 2).

## Backwards Compatibility

Format detection is automatic:

| Format | Detection | Behavior |
|--------|-----------|----------|
| `structured` | Contains `## Fixes`, `## Decisions`, or `## Patterns` | Uses new parsing |
| `legacy` | Contains `### Sign:` | Uses legacy Sign format |

Legacy Signs format continues to work without modification.

## Decision Tree: Where to Store Learnings

```
What kind of learning?
│
├── Error/Gotcha encountered?
│   └── → .ralph/guardrails.md ## Fixes
│
├── Architectural choice made?
│   └── → .ralph/guardrails.md ## Decisions (session)
│   └── → .ralph/specs/design/ (permanent)
│
├── Convention/pattern discovered?
│   └── → .ralph/guardrails.md ## Patterns
│
├── Progress/State for next task cycle?
│   └── → .ralph/guardrails.md (shared memory)
│
└── Permanent project-wide pattern?
    └── → .ralph/agents.md
```

## Related

- [state-files.md](state-files.md) - Detailed file purposes and update rules
- [backpressure.md](backpressure.md) - How learnings prevent repeated errors

---

*Version: 2.0.0 | Updated: 2026-02-15*
*Structured memories with typed sections*
