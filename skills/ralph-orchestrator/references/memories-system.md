# Memory Architecture

> **Status**: Ralph uses a distributed memory architecture with structured format in guardrails.md.

## Overview

Ralph uses a **distributed memory architecture** where different types of learnings are stored in appropriate locations based on their scope and permanence.

## Memory Components

| Component | Scope | Lifetime | Purpose |
|-----------|-------|----------|---------|
| `scratchpad.md` | Iteration | Session | Current state, progress, blockers |
| `guardrails.md` | Loop | Session | Fixes, decisions, patterns (structured) |
| `specs/design/` | Feature | Permanent | Architectural decisions |
| `AGENTS.md` | Project | Permanent | Build commands, patterns, conventions |
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
MEMORIES_BUDGET=2000    # Max tokens to inject (~8000 chars)
```

## Truncation Behavior

The `truncate-context.sh` script respects memory block boundaries:
- Never cuts mid-memory (waits for `-->` marker)
- Adds `<!-- truncated: budget exceeded -->` when truncating
- Preserves parseability of remaining memories

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
│   └── → guardrails.md ## Fixes
│
├── Architectural choice made?
│   └── → guardrails.md ## Decisions (session)
│   └── → specs/design/ (permanent)
│
├── Convention/pattern discovered?
│   └── → guardrails.md ## Patterns
│
├── Progress/State for next iteration?
│   └── → scratchpad.md
│
└── Permanent project-wide pattern?
    └── → AGENTS.md
```

## Related

- [state-files.md](state-files.md) - Detailed file purposes and update rules
- [backpressure.md](backpressure.md) - How learnings prevent repeated errors

---

*Version: 3.0.0 | Updated: 2026-01-31*
*Structured memories with typed sections*
