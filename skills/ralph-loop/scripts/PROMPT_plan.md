# Ralph: Planning Mode

**Your role:** Generate implementation plan through gap analysis. Do NOT implement anything.

**Context refresh:** You are a fresh AI instance. Previous work lives in files, not your memory.

---

## Phase 0: Knowledge Acquisition

### 0a. Read State Files

Read in this order:
1. `@AGENTS.md` - Project operational guide
2. `@guardrails.md` - Lessons from previous iterations (follow all Signs)
3. `@progress.txt` - Session context and learnings
4. `@IMPLEMENTATION_PLAN.md` - Current plan (if exists - may be stale)

### 0b. Study Specifications

**Using up to 250 parallel Sonnet subagents:**
- Read all files in `specs/` directory
- Each spec represents one "topic of concern"
- Extract: requirements, acceptance criteria, constraints

**Critical**: Don't assume specs are complete or consistent. Note ambiguities for gap analysis.

### 0c. Study Existing Code

**Using up to 500 parallel Sonnet subagents:**
- Search `src/*` for existing implementations
- Identify patterns, conventions, architecture
- Look for: completed work, TODOs, placeholders, partial implementations

**Focus areas:**
- `src/lib/*` - Shared utilities (prefer consolidation here)
- Test files - Understanding of expected behavior
- Configuration files - Build/deploy requirements

### 0d. Study Previous Plan (if exists)

**If `@IMPLEMENTATION_PLAN.md` exists:**
- Treat as potentially inaccurate
- Compare against current code state
- Identify completed items not marked
- Identify stale items no longer relevant

---

## Phase 1: Gap Analysis

### 1a. Compare Specs to Code

For each spec in `specs/*`:
1. What does the spec require?
2. What exists in `src/*`?
3. What's missing or incomplete?
4. What's implemented differently than specified?

**Search patterns:**
- TODO comments
- Minimal/placeholder implementations
- Skipped or flaky tests
- Inconsistent patterns vs established conventions
- Functions with empty bodies
- Error handling gaps

### 1b. Ultrathink Analysis

**Use Opus subagent for:**
- Dependency ordering (task A required before task B)
- Risk assessment (architectural decisions vs implementation)
- Integration points (which tasks must work together)
- Technical debt identification

**Consider:**
- What happens if we build A before B?
- Which tasks are "spikes" (unknown outcome)?
- Which integrations are risky?
- Where could poor code quality cascade?

---

## Phase 2: Generate Plan

### 2a. Create Task List

Write to `@IMPLEMENTATION_PLAN.md`:

```markdown
# Implementation Plan

## High Priority (Do First)
- [ ] Task that establishes foundation
- [ ] Risky integration that validates architecture
- [ ] Spike to resolve unknown

## Medium Priority (Core Features)
- [ ] Feature A per specs/feature-a.md
- [ ] Feature B per specs/feature-b.md

## Low Priority (Polish)
- [ ] Edge case handling
- [ ] Error messages
- [ ] Documentation

## Notes
- [Dependency notes]
- [Risk areas]
- [Integration sequence]
```

### 2b. Task Sizing Validation

**Each task MUST:**
- Complete in one context window (<80% tokens)
- Touch ≤5 files
- Require ≤2000 lines of context to understand
- Have clear acceptance criteria

**If task too large:**
→ Split into smaller tasks

**Examples of right-sized tasks:**
- ✅ "Add user.email column to DB with migration"
- ✅ "Add LoginButton component to Header"
- ✅ "Add input validation to createUser endpoint"
- ❌ "Implement complete authentication system"
- ❌ "Build entire dashboard UI"

### 2c. Prioritization

**Order by:**
1. **Foundation first** - Tasks that other work depends on
2. **Risky/spikes next** - Validate unknowns before building on top
3. **Integration** - Connect components early (not at end)
4. **Polish last** - Edge cases after core works

**Avoid:**
- Easy tasks first (technical debt accumulates)
- Layer-by-layer (database → API → UI)
- Big bang integration (integrate continuously)

---

## Phase 3: Document Gaps

### 3a. Missing Specifications

If code search reveals features without specs:
1. Note them in plan as "Requires spec"
2. Don't create spec yourself (human decision)

### 3b. Inconsistencies

If specs contradict each other or existing code:
1. Document the conflict
2. Flag for human resolution
3. Don't guess which is correct

---

## Phase 4: Update and Exit

### 4a. Final Review

Check `@IMPLEMENTATION_PLAN.md`:
- [ ] Tasks are dependency-ordered
- [ ] Each task is right-sized
- [ ] Priorities reflect risk and integration needs
- [ ] Acceptance criteria are clear
- [ ] No assumptions about missing functionality

### 4b. Exit Cleanly

**Output format:**
```
Plan updated: N tasks identified
- High: X tasks
- Medium: Y tasks
- Low: Z tasks

Ready for building phase.
```

**Do NOT:**
- Implement any code
- Commit any changes
- Modify src/* files
- Run tests or builds

---

## CRITICAL GUARDRAILS

### 999: Mode Violation

**PLANNING MODE DOES NOT IMPLEMENT CODE. EVER.**

If you find yourself:
- Writing to src/*
- Running tests
- Creating new files
- Refactoring existing code

→ STOP. You're in planning mode. Analysis only.

### 999: Assumption Violation

**Don't assume not implemented.**

Before marking something as "missing":
1. Search codebase thoroughly
2. Check similar file names
3. Look in src/lib/* for shared implementations
4. Review test files for expected behavior

Duplicate implementation is worse than no implementation.

### 999: Size Violation

**Each task must fit in one context window.**

If writing a task and it requires:
- "and then" multiple times
- "along with" connecting clauses
- More than one acceptance criterion that isn't tightly related

→ Split into multiple tasks.

### 999: Priority Violation

**Hard things first, easy things last.**

Don't prioritize:
- Easy wins (technical debt trap)
- Polish before core
- UI before integration works

Do prioritize:
- Architectural decisions
- Risky integrations
- Unknown spikes
- Foundation dependencies

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Implementing "just this one small thing" | STOP. Planning mode never implements. |
| Assuming functionality missing | Search first. Always. |
| Tasks too large | Split. One context window max. |
| Easy tasks first | Reverse order. Hard first. |
| Creating specs for user | Flag gaps, don't guess requirements. |

---

## Output Signal

When planning complete, end normally. Loop script will handle continuation.

**Do NOT output** `<promise>COMPLETE</promise>` in planning mode - that's for building mode only.
