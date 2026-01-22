# Ralph: Building Mode

You are a fresh AI instance. Previous work lives in files, not your memory.

---

## Phase 0: Orient

### 0a. Study Guardrails FIRST

```
@guardrails.md
```

Follow ALL Signs. They contain lessons from previous iterations.

### 0b. Study State Files

Study these using subagents:
1. `@AGENTS.md` - Operational guide
2. `@IMPLEMENTATION_PLAN.md` - Task list

### 0c. Study Specs

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

### 2a. Test-Driven Development

1. Write test first
2. Watch it fail (RED)
3. Write minimal implementation (GREEN)
4. Refactor for clarity

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

### 4c. Add Sign (If Errors Occurred)

Using a subagent, add to `@guardrails.md`:

```markdown
### Sign: [Problem description]
- **Trigger**: [Condition that causes this]
- **Instruction**: [Action to prevent it]
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

## Context Health

- 🟢 <60%: Continue freely
- 🟡 60-80%: Finish task, then exit
- 🔴 >80%: Commit current state, exit NOW

---

## Exit

After ONE task:
1. All gates passed ✅
2. State files updated ✅
3. Committed ✅

→ Exit. Loop continues with fresh context.
