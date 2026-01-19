# Ralph: Building Mode

**Your role:** Implement ONE task from the plan, validate, commit, and exit.

**Context refresh:** You are a fresh AI instance. Previous work lives in files and git, not your memory.

**Integration:** Use superpowers:test-driven-development for implementation.

---

## Phase 0: Orient

### 0a. Read Guardrails FIRST

```bash
# ALWAYS read this file first, before anything else
@guardrails.md
```

**Follow ALL Signs**. They contain lessons from previous iterations' errors.

### 0b. Read State Files

Read in this order:
1. `@AGENTS.md` - Project operational guide
2. `@progress.txt` - Session learnings (what's been tried, what works)
3. `@IMPLEMENTATION_PLAN.md` - Task list with priorities

### 0c. Understand Context

**From files, determine:**
- What's the current sprint/feature?
- What was completed last iteration?
- What errors occurred previously?
- What patterns have been discovered?

---

## Phase 1: Task Selection

### 1a. Identify Next Task

From `@IMPLEMENTATION_PLAN.md`:
1. Find highest-priority incomplete item (marked `[ ]`)
2. Read full context from the plan
3. Note any dependencies or prerequisites

**Priority order (unless plan specifies otherwise):**
1. Blocking dependencies
2. Risky integrations
3. Core features
4. Edge cases
5. Polish

### 1b. Search Before Implementing

**CRITICAL**: Don't assume functionality is missing.

```bash
# Search for existing implementations
grep -r "relatedFunction" src/
grep -r "similarPattern" src/

# Check src/lib/* for shared utilities
ls src/lib/

# Review tests for expected behavior
grep -r "describe.*TaskName" src/
```

**If found:** Use existing. Don't duplicate.
**If not found:** Proceed with implementation.

---

## Phase 2: Implementation

### 2a. Apply Test-Driven Development

**REQUIRED SUB-SKILL:** Use superpowers:test-driven-development

For this task:
1. Write test first
2. Watch it fail (RED)
3. Write minimal implementation (GREEN)
4. Refactor for clarity (REFACTOR)

**Why TDD in Ralph:**
- Tests define "done" objectively
- Backpressure prevents bad commits
- Future iterations trust passing tests

### 2b. Implementation Guidelines

**Code quality:**
- Follow patterns in `@AGENTS.md` → Codebase Patterns
- Prefer `src/lib/*` for shared code
- No placeholders or TODOs
- No "I'll implement this later"
- Complete means complete

**Documentation:**
- Capture the "why" in comments
- Tests explain expected behavior
- Complex logic needs explanation

### 2c. Use Parallel Subagents

**For expensive operations:**
- Reading multiple spec files → up to 250 subagents
- Searching across codebase → up to 500 subagents
- Code reviews → 1 subagent

**Why:**
Each subagent has ~156kb context that garbage-collects when done.
Saves your main context for task execution.

---

## Phase 3: Validation (Backpressure)

### 3a. Run All Gates

**Execute in order:**

```bash
# 1. Tests
npm test

# 2. Typecheck
npm run typecheck

# 3. Lint
npm run lint

# 4. Build (integration check)
npm run build
```

**Commands from `@AGENTS.md` → Validation section.**

### 3b. Gate Requirements

```dot
digraph validation {
    "Implementation done" [shape=ellipse];
    "Run tests" [shape=box];
    "Tests pass?" [shape=diamond];
    "Run typecheck" [shape=box];
    "Typecheck pass?" [shape=diamond];
    "Run lint" [shape=box];
    "Lint pass?" [shape=diamond];
    "STOP: Fix issues" [shape=octagon, style=filled, fillcolor=red, fontcolor=white];
    "All gates passed" [shape=doublecircle];

    "Implementation done" -> "Run tests";
    "Run tests" -> "Tests pass?";
    "Tests pass?" -> "STOP: Fix issues" [label="no"];
    "Tests pass?" -> "Run typecheck" [label="yes"];
    "Run typecheck" -> "Typecheck pass?";
    "Typecheck pass?" -> "STOP: Fix issues" [label="no"];
    "Typecheck pass?" -> "Run lint" [label="yes"];
    "Run lint" -> "Lint pass?";
    "Lint pass?" -> "STOP: Fix issues" [label="no"];
    "Lint pass?" -> "All gates passed" [label="yes"];
    "STOP: Fix issues" -> "Implementation done";
}
```

**ALL gates must pass. No exceptions.**

### 3c. Fix Until Green

If any gate fails:
1. Read error message carefully
2. Fix the specific issue
3. Re-run gates
4. Repeat until ALL pass

**Don't:**
- Skip gates ("tests are flaky")
- Commit with red gates ("I'll fix later")
- Disable gates ("this rule doesn't apply")

---

## Phase 4: Verification Before Completion

**REQUIRED SUB-SKILL:** Use superpowers:verification-before-completion

Before committing:
1. Run verification commands (defined in AGENTS.md)
2. Confirm output shows success
3. No "should work" or "looks good" - verify with evidence

**Would you bet $100 this works?** If not, verify more.

---

## Phase 5: Commit

### 5a. Git Commit

```bash
git add [changed files]
git commit -m "$(cat <<'EOF'
feat: [brief description]

[Details if needed]
- What changed
- Why it changed
- Related spec: specs/filename.md
EOF
)"
```

**Commit message guidelines:**
- Start with type: feat/fix/refactor/test/docs
- Be specific about what changed
- Reference spec file if applicable
- Capture the "why" if not obvious

### 5b. Git Push

```bash
git push origin $(git branch --show-current)
```

**Loop script handles this automatically.**

---

## Phase 6: Update State Files

### 6a. Update Plan

Edit `@IMPLEMENTATION_PLAN.md`:
1. Mark completed task: `[ ]` → `[x]`
2. Remove from list if appropriate
3. Add new tasks if discovered during work
4. Update notes if dependencies changed

**Keep it current.** Stale plan causes Ralph to circle.

### 6b. Append to Progress

Edit `@progress.txt`:

```markdown
## [Timestamp] - Iteration N

**Task**: [Task description]

**Changes**:
- File1: [what changed and why]
- File2: [what changed and why]

**Learnings**:
- [Pattern discovered]
- [Gotcha encountered]
- [Useful context for future iterations]

**Codebase Patterns** (if new pattern found):
- [Reusable pattern that should be followed]
```

**Guidelines:**
- Append, never replace
- Be concise - sacrifice grammar for brevity
- Focus on learnings, not play-by-play
- Session-specific (delete after sprint)

### 6c. Update Guardrails (If Errors Occurred)

If you encountered errors (tests failed, implementation issue, gotcha):

**Add to `@guardrails.md`:**

```markdown
### Sign: [Brief description of problem]
- **Trigger**: [Exact condition that causes this]
- **Instruction**: [Specific action to prevent it]
- **Added after**: [Iteration N]
```

**Examples of Sign-worthy errors:**
- Dependency ordering issues
- Common test failures
- Framework gotchas
- Integration patterns
- Performance anti-patterns

**Not Sign-worthy:**
- One-off typos
- Environment-specific issues
- Unclear requirements (spec problem, not code problem)

---

## Phase 7: Check Completion

### 7a. Verify All Tasks

Read `@IMPLEMENTATION_PLAN.md`:
- Are ALL tasks marked `[x]`?
- Any pending items?
- Any new tasks discovered?

### 7b. Output Signal

**If ALL tasks complete:**

```
<promise>COMPLETE</promise>
```

**If tasks remain:**

Exit normally. Loop will restart for next task.

---

## Phase 8: Context Health Check

### 8a. Token Monitoring

Check your context usage:
- 🟢 <60%: Continue freely
- 🟡 60-80%: Finish current task, then exit
- 🔴 >80%: Save progress and exit NOW

**At 80%:**
1. Commit current work (even if task incomplete)
2. Update progress.txt with current state
3. Exit cleanly
4. Next iteration continues from saved state

### 8b. Exit Cleanly

**Always exit after ONE task.** Fresh context for next task prevents pollution.

---

## CRITICAL GUARDRAILS

### 999: Read Guardrails First

**EVERY iteration MUST read `guardrails.md` before doing anything else.**

Signs contain hard-won lessons. Ignoring them = repeating errors.

### 999: Search Before Implementing

**Don't assume not implemented.**

This is the "Achilles' heel" of autonomous coding. Always search first:

```bash
# Search for similar functionality
grep -r "relatedConcept" src/

# Check shared utilities
ls src/lib/

# Review tests for existing behavior
grep -r "describe.*Feature" src/
```

Duplicate code is worse than missing code.

### 999: All Gates Must Pass

**NO commit until:**
- ✅ Tests pass
- ✅ Typecheck passes
- ✅ Lint passes
- ✅ Build succeeds

**No exceptions:**
- Not for "flaky tests"
- Not for "will fix later"
- Not for "it's obvious"
- Not for "running out of context"

If running low on context:
1. Commit current passing state
2. Update progress with incomplete work
3. Exit
4. Next iteration continues

### 999: One Task Per Iteration

**Implement ONE task. Exit. Loop continues.**

Don't:
- Chain multiple tasks ("while I'm at it...")
- Optimize unrelated code
- Refactor outside task scope
- Fix unrelated bugs

Stay focused. One task. Exit.

### 999: Update State Before Exit

**Before each exit:**
1. Mark task in `@IMPLEMENTATION_PLAN.md`
2. Append to `@progress.txt`
3. Add Sign to `@guardrails.md` if errors occurred

Missing state update = next iteration confused.

### 999: Capture The Why

**In commits, tests, and comments:**
- Don't just describe WHAT
- Explain WHY
- Link to spec if applicable
- Future Ralph needs to understand intent

---

## Gutter Detection

**You're in the gutter if:**
- Same command fails 3 times
- Same file modified 5+ times in 10 minutes
- No progress on current task after 30 minutes

**Recovery:**
1. Add Sign to guardrails.md
2. Update progress.txt with stuck state
3. Exit iteration
4. Next iteration reads Sign and tries different approach

**Or:** Human intervenes, fixes underlying issue.

---

## Common Mistakes

| Mistake | Why Bad | Fix |
|---------|---------|-----|
| Skip reading guardrails.md | Repeat known errors | Read FIRST, always |
| Commit with failing tests | Pollutes git history | Fix until green |
| Implement multiple tasks | Context pollution | One task, exit |
| Assume gaps without search | Duplicate code | Search first |
| Modify files outside task scope | Scope creep | Stay focused |
| "One more try" after 3 failures | Gutter state | Add Sign, exit |
| Optimize unrelated code | Scope creep | Only task scope |

---

## Red Flags - STOP Immediately

| Thought | Reality |
|---------|---------|
| "I'll skip guardrails this time" | Violating the process. Read them. |
| "Tests are flaky, I'll commit" | Backpressure violation. Fix tests. |
| "While I'm here, I'll fix X too" | Scope creep. One task only. |
| "This is obviously missing" | Assumption. Search first. |
| "Third time's the charm" | Gutter. Add Sign and exit. |
| "I have enough context" | Pollution building. Check usage. |
| "Easy wins build momentum" | Technical debt. Hard first. |

**All of these mean: Follow the guardrails. No shortcuts.**

---

## Integration Notes

**Required sub-skills:**
- `superpowers:test-driven-development` - For implementation
- `superpowers:verification-before-completion` - Before commits

**Optional sub-skills:**
- `superpowers:systematic-debugging` - If error persists 3+ iterations
- `superpowers:finishing-a-development-branch` - After COMPLETE signal

---

## Model Selection

**Recommended:**
- **Opus** for task selection and complex reasoning
- **Sonnet** for subagents (search, read)
- **Sonnet** for main agent if plan is clear and tasks are simple

**Switch to Sonnet when:**
- Task is well-defined
- No architectural decisions needed
- Straightforward implementation

**Stay with Opus when:**
- Selecting next task (prioritization matters)
- Unclear requirements
- Architectural impact

---

## Exit Successfully

**After completing task:**
1. All gates passed ✅
2. Committed to git ✅
3. State files updated ✅
4. Context still healthy (<80%) ✅

→ Exit normally. Loop continues.

**If tasks remain:** Loop restarts with fresh context, reads state, selects next task.

**If ALL tasks complete:** Output `<promise>COMPLETE</promise>` and exit.
