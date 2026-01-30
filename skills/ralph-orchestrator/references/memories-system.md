# Memory Architecture

> **Status**: The original `memories.md` system has been replaced with a distributed memory architecture. This document explains the current approach.

## Overview

Ralph uses a **distributed memory architecture** where different types of learnings are stored in appropriate locations based on their scope and permanence.

## Memory Components

| Component | Scope | Lifetime | Purpose |
|-----------|-------|----------|---------|
| `scratchpad.md` | Iteration | Session | Current state, progress, blockers |
| `guardrails.md` | Loop | Session | Signs (error lessons, gotchas) |
| `specs/design/` | Feature | Permanent | Architectural decisions |
| `AGENTS.md` | Project | Permanent | Build commands, patterns, conventions |
| Git history | All | Permanent | Complete audit trail |

## Decision Tree: Where to Store Learnings

```
What kind of learning?
│
├── Error/Gotcha encountered this session?
│   └── → guardrails.md (Sign format)
│
├── Progress/State for next iteration?
│   └── → scratchpad.md
│
├── Architectural decision for this feature?
│   └── → specs/{goal}/design/
│
├── Project-wide pattern or convention?
│   └── → AGENTS.md (Patterns section)
│
└── Permanent record for future reference?
    └── → Git commit message
```

## Signs (guardrails.md)

Signs capture **session-scoped gotchas** that prevent repeated errors within a loop session.

**Format:**
```markdown
### Sign: [Problem Name]
- **Trigger**: [When this applies]
- **Instruction**: [What to do]
```

**Example:**
```markdown
### Sign: ESM Import Syntax
- **Trigger**: "Cannot use import statement outside a module"
- **Instruction**: Check package.json has "type": "module"
```

## Architectural Decisions (specs/design/)

Permanent decisions about **why** something was designed a certain way live in the specs directory.

**Location:** `specs/{goal}/design/decisions.md` or inline in `detailed-design.md`

**Format:** ADR (Architecture Decision Record) style
- Context: What prompted the decision
- Decision: What was decided
- Consequences: Trade-offs accepted

## Historical Note

The original `memories.md` system used a single file with three sections:
- Patterns: Now in `AGENTS.md`
- Decisions: Now in `specs/design/`
- Fixes: Now in `guardrails.md` as Signs

This was simplified because:
1. SOP skills already generate `specs/design/` artifacts
2. Signs provide more actionable format than generic "fixes"
3. Distributed storage matches how information is consumed

## Related

- [state-files.md](state-files.md) - Detailed file purposes and update rules
- [backpressure.md](backpressure.md) - How learnings prevent repeated errors

---

*Version: 2.0.0 | Updated: 2026-01-30*
*Replaces deprecated memories.md system*
