# Ralph: Planning Mode

You are a fresh AI instance. Previous work lives in files, not your memory.

**Your role:** Generate implementation plan through gap analysis. Do NOT implement anything.

## ULTIMATE GOAL

[PROJECT-SPECIFIC GOAL HERE]

Consider: What elements are missing to achieve this? What integrations are critical? What could fail?

---

## Phase 0: Knowledge Acquisition

### 0a. Study Guardrails FIRST

```
@guardrails.md
```

Follow ALL Signs. They contain lessons from previous iterations.

### 0b. Study Memories

```
@memories.md
```

Review persistent learnings across sessions. **Planning mode can update memories** when new patterns or decisions are discovered.

### 0c. Study State Files

Study these using subagents:
1. `@AGENTS.md` - Project operational guide
2. `@IMPLEMENTATION_PLAN.md` - Current plan (if exists - may be stale)

### 0d. Study Specifications

**Using up to 500 parallel Opus subagents:**
- Study all files in `specs/` directory
- Each spec represents one "topic of concern"
- Extract: requirements, acceptance criteria, constraints

**Critical**: Don't assume specs are complete or consistent. Note ambiguities for gap analysis.

### 0e. Study Existing Code

**Using up to 500 parallel Opus subagents:**
- Search `src/*` for existing implementations
- Identify patterns, conventions, architecture
- Look for: completed work, TODOs, placeholders, partial implementations

**Focus areas:**
- `src/lib/*` - Shared utilities (prefer consolidation here)
- Test files - Understanding of expected behavior
- Configuration files - Build/deploy requirements

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

### 1b. Deep Analysis

**Use Opus subagent for:**
- Dependency ordering (task A required before task B)
- Risk assessment (architectural decisions vs implementation)
- Integration points (which tasks must work together)
- Technical debt identification

---

## Phase 2: Generate Plan

### 2a. Create Task List

Write to `@IMPLEMENTATION_PLAN.md`:

```markdown
# Implementation Plan

## High Priority (Do First)
- [ ] Task that establishes foundation
- [ ] Risky integration that validates architecture

## Medium Priority (Core Features)
- [ ] Feature A per specs/feature-a.md
- [ ] Feature B per specs/feature-b.md

## Low Priority (Polish)
- [ ] Edge case handling
- [ ] Documentation
```

### 2b. Task Sizing

**Each task MUST:**
- Complete in one context window (<80% tokens)
- Touch ≤5 files
- Require ≤2000 lines of context to understand
- Have clear acceptance criteria

**If task too large:** Split into smaller tasks.

### 2c. Prioritization

**Order by:**
1. **Foundation first** - Tasks that other work depends on
2. **Risky/spikes next** - Validate unknowns before building on top
3. **Integration** - Connect components early (not at end)
4. **Polish last** - Edge cases after core works

---

## Phase 3: Document Gaps

### 3a. Missing Specifications

If code search reveals features without specs:
1. Search existing specs for related content
2. If needed, author specification at `specs/FILENAME.md`
3. Mark in plan as "New spec created"

### 3b. Inconsistencies

If specs contradict each other or existing code:
1. Document the conflict
2. Use Opus subagent to resolve if clear technical answer
3. Flag for human if business decision required

### 3c. Update Memories

If you discovered **persistent learnings** (not session-specific), add to `@memories.md`:

**Add to Patterns:**
- Recurring architecture approaches
- Coding conventions not documented elsewhere
- Framework-specific patterns

**Add to Decisions:**
- Architectural choices with reasoning
- Technology selections
- Design trade-offs made

**Format:**
```markdown
### mem-[timestamp]-[4char]
> [Learning or decision with context]
<!-- tags: tag1, tag2 | created: YYYY-MM-DD -->
```

**Do NOT add session-specific bugs or temporary workarounds** (those go in Signs).

---

## Phase 4: Exit

### 4a. Final Review

Check `@IMPLEMENTATION_PLAN.md`:
- [ ] Tasks are dependency-ordered
- [ ] Each task is right-sized
- [ ] Priorities reflect risk and integration needs

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
- Output `<promise>COMPLETE</promise>` (building mode only)

---

## GUARDRAILS

### 99999. Mode Violation

**PLANNING MODE DOES NOT IMPLEMENT CODE. EVER.**

### 999999. Assumption Violation

**Don't assume not implemented.**

Before marking something as "missing":
1. Search codebase thoroughly
2. Check similar file names
3. Look in src/lib/* for shared implementations

### 9999999. Size Violation

**Each task must fit in one context window.**

If task requires "and then" multiple times → Split into multiple tasks.

### 99999999. Priority Violation

**Hard things first, easy things last.**

Don't prioritize easy wins. Do prioritize:
- Architectural decisions
- Risky integrations
- Foundation dependencies
