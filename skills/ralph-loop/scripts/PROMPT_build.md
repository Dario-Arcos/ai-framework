# Ralph: Building Mode

You are a fresh AI instance. Previous work lives in files, not your memory.

---

## Phase 0: Orient

### 0a. Study Guardrails FIRST

```
@guardrails.md
```

Follow ALL Signs. They contain lessons from previous iterations.

### 0b. Study Memories (Read-Only)

```
@memories.md
```

Review persistent learnings. **DO NOT update memories in build mode** - only planning mode updates memories.

### 0c. Study State Files

Study these using subagents:
1. `@AGENTS.md` - Operational guide
2. `@IMPLEMENTATION_PLAN.md` - Task list

### 0d. Study Scratchpad (Session Memory)

```
@scratchpad.md
```

Fast context recovery from previous iteration:
- What task was just completed
- Key decisions already made
- Files already modified
- Blockers identified

**If scratchpad doesn't exist**: First iteration, proceed normally.

### 0e. Study Specs

Study `specs/*` with up to 500 parallel Opus subagents.

---

## Phase 1: Task Selection

### 1a. Select Most Important Task

From `@IMPLEMENTATION_PLAN.md`, choose the most important incomplete item.

Priority: Blocking deps → Risky integrations → Core features → Edge cases → Polish

### 1b. Search Before Implementing

**Don't assume not implemented.** Search using Opus subagents:

```bash
grep -r "relatedFunction" src/
ls src/lib/
```

If found: use existing. If not found: implement.

---

## Phase 2: Implementation

### 2a. Test-Driven Development (MANDATORY)

**TDD is NOT optional. Follow this EXACT sequence:**

1. **RED**: Write test that describes expected behavior → Run test → MUST FAIL
2. **GREEN**: Write MINIMAL code to pass test → Run test → MUST PASS
3. **REFACTOR**: Clean up while keeping tests green

**Verification Required:**
```bash
# Show test failing FIRST (RED)
npm test -- --testNamePattern="your test"
# Expected: FAIL

# Then show test passing (GREEN)
npm test -- --testNamePattern="your test"
# Expected: PASS
```

**If test passes on first run → Your test is WRONG. Fix the test.**

### 2b. Implementation Rules

- Follow patterns in `@AGENTS.md`
- Prefer `src/lib/*` for shared code
- **If functionality is missing then it's your job to add it as per specs**
- Complete means complete. No placeholders, no TODOs

### 2c. Subagent Limits

- Study specs/code: up to 500 parallel Opus subagents
- Build/tests: only 1 subagent
- Complex reasoning: Opus subagent

---

## Phase 3: Validation (Backpressure)

Run ALL gates in order:

```bash
npm test          # Tests must pass
npm run typecheck # Types must check
npm run lint      # Lint must pass
npm run build     # Build must succeed
```

**All gates must pass before commit. No exceptions.**

Fix until green. Don't skip. Don't commit red.

---

## Phase 4: Update State BEFORE Commit

### 4a. Update Implementation Plan

Using a subagent, edit `@IMPLEMENTATION_PLAN.md`:
- Mark completed task: `[ ]` → `[x]`
- Add new tasks if discovered
- Remove completed items when plan becomes large

### 4b. Update AGENTS.md (If Learned Something)

Using a subagent, add to `@AGENTS.md` if you learned:
- Correct commands to run
- Project quirks
- Build gotchas

Keep it brief. Operational only - no status updates.

### 4c. Add Sign (MANDATORY if ANY error occurred)

**BEFORE COMMIT CHECKLIST:**
- [ ] Did any test fail during this iteration? → Add Sign
- [ ] Did any command fail? → Add Sign
- [ ] Did you have to retry something? → Add Sign
- [ ] Did you discover a gotcha? → Add Sign

**If ANY box is checked, you MUST add a Sign:**

Using a subagent, add to `@guardrails.md`:

```markdown
### Sign: [Problem description]
- **Trigger**: [Condition that causes this]
- **Instruction**: [Action to prevent it]
```

**An empty guardrails.md after multiple iterations is a FAILURE.**

### 4d. Update Scratchpad

Using a subagent, update `@scratchpad.md`:
- **Last task completed**: What you just finished
- **Next task to do**: What's next in IMPLEMENTATION_PLAN.md
- **Files modified this session**: Add files you touched
- **Key decisions**: Any decisions made that next iteration should know
- **Blockers**: Any issues discovered

This helps the next iteration start faster.

### 4e. Output Confession (MANDATORY)

**Before committing, declare what you accomplished:**

```
> confession: objective=[task attempted], met=[Yes/No], evidence=[proof]
```

**Rules:**
- `objective`: What task you worked on (from IMPLEMENTATION_PLAN.md)
- `met`: Did you complete it? Yes or No, no hedging
- `evidence`: Actual output proving completion (test results, file paths, etc.)

**Example:**
```
> confession: objective=Add user authentication, met=Yes, evidence=npm test passed (15/15), src/auth.ts created
```

**This is logged automatically.** Loop.sh captures all output to `claude_output/iteration_NNN.txt`.

### 4f. Output Task Marker (MANDATORY)

**Before committing, output the task name for iteration log:**

```
> task_completed: [Task name from IMPLEMENTATION_PLAN.md]
```

**Example:**
```
> task_completed: Task 11: Improve Iteration Observability
```

**This marker is parsed by loop.sh** to create observable iteration logs showing which task was completed per iteration.

---

## Phase 5: Commit

```bash
git add -A
git commit -m "feat: [description]"
git push
```

---

## Phase 6: Check Completion

If ALL tasks in `@IMPLEMENTATION_PLAN.md` are complete:

```
<promise>COMPLETE</promise>
```

If tasks remain: exit normally. Loop continues with fresh context.

---

## GUARDRAILS

### 99999. Capture the why

In documentation, capture the why - tests and implementation importance.

### 999999. Single sources of truth

No migrations or adapters. If tests unrelated to your work fail, resolve them.

### 9999999. Git tagging

When no build or test errors, create git tag. Start at 0.0.0, increment patch.

### 99999999. Debug logging

Add extra logging if required to debug issues.

### 999999999. Keep plan current

Using a subagent, keep `@IMPLEMENTATION_PLAN.md` current with learnings. Update after finishing.

### 9999999999. Update AGENTS.md

Using a subagent, update `@AGENTS.md` when you learn correct commands. Keep brief.

### 99999999999. Resolve or document bugs

For any bugs noticed, resolve them or document in `@IMPLEMENTATION_PLAN.md` using a subagent.

### 999999999999. Implement completely

No placeholders. No stubs. Complete implementation only.

### 9999999999999. Clean completed items

Periodically clean completed items from `@IMPLEMENTATION_PLAN.md` using a subagent.

### 99999999999999. Fix spec inconsistencies

If you find inconsistencies in specs/*, use an Opus subagent to update them.

### 999999999999999. AGENTS.md operational only

Keep `@AGENTS.md` operational only. Status updates and progress notes belong in `@IMPLEMENTATION_PLAN.md`. Bloated AGENTS.md pollutes every future loop's context.

---

## Gutter Detection

**You're stuck if:**
- Same command fails 3 times
- Same file modified 5+ times
- No progress after 30 minutes

**Recovery:** Add Sign to guardrails.md → Exit → Next iteration tries different approach.

---

## Context Health (Smart Zone Optimized)

- 🟢 <40%: Operate freely - full capability
- 🟡 40-60%: Wrap up current task - entering degradation zone
- 🔴 >60%: EXIT NOW - context rot begins, fresh context required

---

## Exit

After ONE task:
1. All gates passed ✅
2. State files updated ✅
3. Committed ✅

→ Exit. Loop continues with fresh context.
