# Memories System

Persistent learnings that survive loop restarts and context refreshes.

## Purpose

Memories capture:
- **Patterns**: Architectural decisions and conventions
- **Decisions**: Choices made with reasoning
- **Fixes**: Solutions to recurring problems

## CLI Commands

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

## Memory File Format

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

## When Workers Use Memories

Workers automatically read `.ralph/memories.md` at iteration start. This provides:
- Consistent patterns across iterations
- Previous decisions to maintain coherence
- Known fixes to avoid repeated mistakes

## Best Practices

1. **Be specific**: "Use Result<T>" is better than "handle errors"
2. **Include context**: Tags help future searches
3. **Document reasoning**: Decisions without reasons are cargo cult
4. **Keep it actionable**: Memories guide behavior, not document history
