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

### 0c. Load Configuration

The loop loads `.ralph/config.sh` automatically. Key settings:
- **QUALITY_LEVEL**: prototype | production | library
- **CONFESSION_MIN_CONFIDENCE**: Minimum confidence to mark task complete (default: 80)
- **GATE_***: Custom validation commands

Check `.ralph/config.sh` if unsure about project quality requirements.

### 0d. Study State Files

Study these using subagents:
1. `@AGENTS.md` - Operational guide
2. Task sources:
   - `specs/*/implementation/plan.md` - Implementation plan with task checklist
   - `specs/*/implementation/step*/task-*.code-task.md` - SOP-generated task files (if exist)

**Task Selection:**
- Read the implementation plan from specs
- If `.code-task.md` files exist, follow TDD workflow: Explore → Plan → Code → Commit
- Create artifacts in `.sop/planning/implementation/{task_name}/`

> **DEPRECATED**: `IMPLEMENTATION_PLAN.md` in project root is no longer supported.
> All planning goes through: `specs/{feature}/implementation/plan.md`

### 0e. Study Scratchpad (Session Memory)

```
@scratchpad.md
```

Fast context recovery from previous iteration:
- What task was just completed
- Key decisions already made
- Files already modified
- Blockers identified

**If scratchpad doesn't exist**: First iteration, proceed normally.

### 0f. Study Specs

Study `specs/*` with up to 500 parallel Opus subagents.

---

## Phase 1: Task Selection

### 1a. Select Most Important Task

**Task Selection from SOP Structure:**
1. Read `specs/{goal}/implementation/plan.md` for task checklist
2. If `.code-task.md` files exist in `specs/*/implementation/step*/`:
   - List all `task-*.code-task.md` files
   - Filter those WITHOUT `## Status: COMPLETED` header
   - Order by step (step01 before step02) and task number
   - Select first incomplete task
3. If no `.code-task.md` files, use checklist in `plan.md` directly

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

**Load project configuration:**
```bash
source .ralph/config.sh 2>/dev/null || true
```

**Quality level behavior:**

| Level | Backpressure |
|-------|--------------|
| prototype | Skip all gates, commit freely |
| production | All configured gates must pass |
| library | All gates + coverage + documentation |

**Run configured gates (production/library only):**
```bash
# Skip if QUALITY_LEVEL=prototype
[ "${QUALITY_LEVEL:-production}" = "prototype" ] && echo "Prototype mode: skipping gates" && continue

# Execute gates (variables from .ralph/config.sh)
[ -n "${GATE_TEST:-}" ] && eval "$GATE_TEST"
[ -n "${GATE_TYPECHECK:-}" ] && eval "$GATE_TYPECHECK"
[ -n "${GATE_LINT:-}" ] && eval "$GATE_LINT"
[ -n "${GATE_BUILD:-}" ] && eval "$GATE_BUILD"
```

**If any gate fails:**
1. Fix the issue
2. Re-run failed gate
3. Do NOT commit until all gates pass

**Gate defaults (if config missing):**
- GATE_TEST="npm test"
- GATE_TYPECHECK="npm run typecheck"
- GATE_LINT="npm run lint"
- GATE_BUILD="npm run build"

---

## Phase 4: Update State BEFORE Commit

### 4a. Update Implementation Plan

**For .code-task.md files:**
- Add `## Status: COMPLETED` and `## Completed: YYYY-MM-DD` at the file header

**For plan.md checklist:**
Using a subagent, edit `specs/{goal}/implementation/plan.md`:
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
- **Next task to do**: What's next in `specs/{goal}/implementation/plan.md`
- **Files modified this session**: Add files you touched
- **Key decisions**: Any decisions made that next iteration should know
- **Blockers**: Any issues discovered

This helps the next iteration start faster.

### 4e. Output Confession (MANDATORY - Expanded)

**Before committing, produce a ConfessionReport:**

```
## Confession

### Objectives Assessment
- **Objective**: [task from specs/{goal}/implementation/plan.md]
  - **Met?**: Yes/No/Partial
  - **Evidence**: [file:line or test output]

### Uncertainties & Conflicts
- [Any unclear requirements encountered]
- [Spec conflicts discovered]
- [Assumptions made]

### Shortcuts Taken
- [Any technical debt introduced]
- [Features deferred]
- [Edge cases skipped]

### Single Easiest Issue to Verify
- [One command that proves completion]

### Confidence (0-100): [integer]
```

**Confidence thresholds:**

| Range | Meaning | Action |
|-------|---------|--------|
| 0-49 | Task failed, major rework needed | Do NOT mark complete |
| 50-79 | Task incomplete, minor work remains | Do NOT mark complete |
| 80-100 | Task complete, ready to commit | Mark complete, commit |

**CRITICAL: If Confidence < ${CONFESSION_MIN_CONFIDENCE:-80}:**
1. Do NOT mark task as complete in the implementation plan
2. Add a Sign to guardrails.md explaining the blocker
3. Update scratchpad.md with what's left to do
4. Exit normally - next iteration will continue

**Output markers (MANDATORY for loop.sh parsing):**
```
> confession: objective=[task name], met=[Yes/No/Partial], confidence=[N], evidence=[proof]
> task_completed: [Task name from implementation plan]
```

**Example:**
```
## Confession

### Objectives Assessment
- **Objective**: Add user authentication
  - **Met?**: Yes
  - **Evidence**: src/auth.ts:1-150, npm test shows 15/15 pass

### Uncertainties & Conflicts
- None

### Shortcuts Taken
- Skipped password reset flow (added to plan as separate task)

### Single Easiest Issue to Verify
- Run: `curl -X POST localhost:3000/login -d '{"email":"test@test.com"}' | jq .token`

### Confidence (0-100): 92

> confession: objective=[Add user authentication], met=[Yes], confidence=[92], evidence=[tests 15/15]
> task_completed: Task 5: Add user authentication
```

---

## Phase 5: Commit

```bash
git add -A
git commit -m "feat: [description]"
git push
```

---

## Phase 6: Check Completion

If ALL tasks in `specs/{goal}/implementation/plan.md` are complete:

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

Using a subagent, keep `specs/{goal}/implementation/plan.md` current with learnings. Update after finishing.

### 9999999999. Update AGENTS.md

Using a subagent, update `@AGENTS.md` when you learn correct commands. Keep brief.

### 99999999999. Resolve or document bugs

For any bugs noticed, resolve them or document in `specs/{goal}/implementation/plan.md` using a subagent.

### 999999999999. Implement completely

No placeholders. No stubs. Complete implementation only.

### 9999999999999. Clean completed items

Periodically clean completed items from `specs/{goal}/implementation/plan.md` using a subagent.

### 99999999999999. Fix spec inconsistencies

If you find inconsistencies in specs/*, use an Opus subagent to update them.

### 999999999999999. AGENTS.md operational only

Keep `@AGENTS.md` operational only. Status updates and progress notes belong in `specs/{goal}/implementation/plan.md`. Bloated AGENTS.md pollutes every future loop's context.

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
