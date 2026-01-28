# Memories System Reference

## Overview

This reference defines the memories system for persistent learnings that survive loop restarts and context refreshes. Understanding memories is essential for maintaining knowledge continuity across iterations.

---

## Purpose

**Constraints:**
- You MUST capture patterns when they emerge because this enables consistency across iterations
- You MUST include reasoning for decisions because decisions without reasons are cargo cult
- You SHOULD use tags for categorization because tags enable future search

Memories capture:
- **Patterns**: Architectural decisions and conventions
- **Decisions**: Choices made with reasoning
- **Fixes**: Solutions to recurring problems

---

## CLI Commands

**Constraints:**
- You MUST use the CLI for adding memories because manual edits may corrupt format
- You MUST include tags because tags enable search and categorization
- You SHOULD include reason for decisions because this documents rationale

### Add a Pattern (Architecture Approach)

```bash
./memories.sh add pattern "All API handlers return Result<T>" --tags api,error-handling
```

### Add a Decision with Reasoning

```bash
./memories.sh add decision "Chose PostgreSQL over MongoDB" \
  --reason "relational model, ACID compliance" --tags database
```

### Add a Fix (Recurring Problem Solution)

```bash
./memories.sh add fix "Always set NODE_ENV in CI before tests" --tags ci,testing
```

### Search Memories

```bash
./memories.sh search "database"
```

### List Recent Memories

```bash
./memories.sh list --type pattern --limit 5
```

---

## Memory File Format

**Constraints:**
- You MUST maintain the standard format because workers parse this structure
- You MUST include date because this provides temporal context
- You MUST include tags because this enables search

Memories are stored in `.ralph/memories.md`:

```markdown
# Memories

## Patterns

### [2025-01-15] All API handlers return Result<T>
Tags: api, error-handling

## Decisions

### [2025-01-15] Chose PostgreSQL over MongoDB
Tags: database
Reason: relational model, ACID compliance

## Fixes

### [2025-01-15] Always set NODE_ENV in CI before tests
Tags: ci, testing
```

---

## When Workers Use Memories

**Constraints:**
- You MUST ensure workers read memories at iteration start because accumulated knowledge guides behavior
- You MUST commit memories to branch because workers need access to file
- You SHOULD not modify memories during execution because workers may be reading

Workers automatically read `.ralph/memories.md` at iteration start. This provides:
- Consistent patterns across iterations
- Previous decisions to maintain coherence
- Known fixes to avoid repeated mistakes

---

## Best Practices

**Constraints:**
- You MUST be specific in memory content because vague memories provide no guidance
- You MUST include context via tags because context enables appropriate application
- You MUST document reasoning because undocumented decisions become cargo cult
- You SHOULD keep memories actionable because memories guide behavior, not document history

1. **Be specific**: "Use Result<T>" is better than "handle errors"
2. **Include context**: Tags help future searches
3. **Document reasoning**: Decisions without reasons are cargo cult
4. **Keep it actionable**: Memories guide behavior, not document history

---

## Troubleshooting

### Memories Not Loading

If workers don't see memories:
- You SHOULD verify memories.md path is correct because wrong path prevents loading
- You SHOULD check memories format follows template because malformed files fail to parse
- You MUST ensure memories.md is committed to branch because uncommitted files aren't visible

### Memories Conflicting

If memories contradict each other:
- You SHOULD review date stamps to determine which is newer because recent decisions supersede
- You SHOULD remove obsolete memories because outdated guidance causes confusion
- You MUST document why older decision was superseded because this creates audit trail

### Memories Not Being Applied

If workers ignore valid memories:
- You SHOULD check if memory is specific enough because vague memories are ignored
- You SHOULD verify tags match worker's context because unrelated tags aren't loaded
- You MUST review worker prompts for memory reading step because this may be missing

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
