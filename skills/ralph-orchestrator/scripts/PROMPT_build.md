# Ralph: Building Mode

You are a fresh AI instance. Previous work lives in files, not your memory.

---

## Phase 0: Orient

### 0a. Study Guardrails FIRST

```
@guardrails.md
```

Follow ALL Signs/memories. They contain lessons from previous iterations.

### 0b. Load Configuration

Check `.ralph/config.sh` for:
- **QUALITY_LEVEL**: prototype | production | library
- **CONFESSION_MIN_CONFIDENCE**: Minimum confidence to mark task complete (default: 80)
- **GATE_***: Custom validation commands

### 0c. Verify AGENTS.md

```
@AGENTS.md
```

**AGENTS.md is generated during planning (Step 5).** Contains project context, build commands, constraints. If missing, exit with error—planning phase incomplete.

### 0d. Study State Files

Using subagents, read:
1. `@AGENTS.md` - Operational guide
2. `@scratchpad.md` - Session memory (last task, next task, blockers)
3. `specs/*/implementation/plan.md` - Task checklist
4. `specs/*/implementation/step*/task-*.code-task.md` - Task files (if exist)

### 0e. Check Blockers

If `specs/{goal}/implementation/{task}/blockers.md` exists with **Active Blockers**:
1. Attempt resolution if within your capability
2. If resolved → move to Resolved Blockers section, continue
3. If unresolved → add Sign to guardrails, skip task, select next available

**Blockers indicate previous iteration couldn't complete. Don't repeat the same failure.**

---

## Phase 1: Task Selection

1. Read `specs/{goal}/implementation/plan.md` for task checklist
2. If `.code-task.md` files exist:
   - Filter those WITHOUT `## Status: COMPLETED`
   - Filter those WITHOUT `## Blocked-By:` pointing to incomplete tasks
   - Order by step and task number
   - Select first available task
3. If no `.code-task.md` files, use checklist in `plan.md` directly

**Search before implementing:** Check if functionality already exists.

---

## Phase 2: Implementation

**Use the `/sop-code-assist` skill in autonomous mode:**

```
/sop-code-assist task_description="{selected_task_path}" mode="autonomous"
```

The skill handles:
- **Explore**: Analyze requirements, research patterns
- **Plan**: Design test strategy
- **Code**: SDD cycle (SCENARIO → SATISFY → REFACTOR)
- **Commit**: Conventional commit

The skill emits required markers:
- `> sdd:scenario {scenario_name}` / `> sdd:satisfy {scenario_name}`
- `> confession: objective=[...], met=[...], confidence=[...], evidence=[...]`
- `> task_completed: [Task name]`

**If skill unavailable:** Follow SDD manually:
1. Write scenario → Run → MUST FAIL (SCENARIO)
2. Write minimal code → Run → MUST PASS (SATISFY)
3. Refactor while keeping satisfied

---

## Phase 3: Validation

**Quality gates (production/library only):**

| Level | Behavior |
|-------|----------|
| prototype | Skip all gates |
| production | All gates must pass |
| library | Gates + coverage + docs |

```bash
[ -n "${GATE_TEST:-}" ] && eval "$GATE_TEST"
[ -n "${GATE_TYPECHECK:-}" ] && eval "$GATE_TYPECHECK"
[ -n "${GATE_LINT:-}" ] && eval "$GATE_LINT"
[ -n "${GATE_BUILD:-}" ] && eval "$GATE_BUILD"
```

**If any gate fails:** Fix and re-run. Do NOT commit until all pass.

---

## Phase 4: Update State

### 4a. Update Task Status

**For .code-task.md files:**
- Add `## Status: COMPLETED` and `## Completed: YYYY-MM-DD`

**For plan.md:** Mark `[ ]` → `[x]`

### 4b. Update AGENTS.md

If you learned commands, quirks, or gotchas → add to `@AGENTS.md`. Keep brief.

### 4c. Add Memory to Guardrails

If you learned something, add to `@guardrails.md`:

```markdown
### fix-{timestamp}-{hex}
> [What failed and how to fix it]
<!-- tags: testing, build | created: YYYY-MM-DD -->
```

### 4d. Update Scratchpad

Update `@scratchpad.md` with:
- Last task completed
- Next task to do
- Files modified
- Key decisions
- Blockers

### 4e. Verify Confession Output

**Verify the skill emitted these markers** (do NOT emit duplicates):

```
> confession: objective=[task name], met=[Yes/No], confidence=[N], evidence=[proof]
> task_completed: [Task name from plan]
```

**Note:** Brackets `[]` are LITERAL. If skill was unavailable (fallback SDD), emit markers yourself.

**Confidence thresholds:**
| Range | Action |
|-------|--------|
| 0-79 | Do NOT mark complete, add blocker to guardrails |
| 80-100 | Mark complete, proceed to commit |

---

## Phase 5: Commit (if needed)

**If skill completed successfully:** Skip—skill already committed.

**If skill unavailable or fallback SDD used:**
```bash
git add -A
git commit -m "feat: [description]"
# Do NOT push
```

---

## Phase 6: Check Completion

If ALL tasks in `specs/{goal}/implementation/plan.md` are complete:

```
<promise>COMPLETE</promise>
```

**Note:** Loop requires TWO consecutive COMPLETE signals.

If tasks remain: exit normally. Loop continues with fresh context.

---

## Safety Rules

- **Gutter detection:** Same command fails 3x or file modified 5x → Add Sign, exit
- **No placeholders:** Complete implementation only
- **AGENTS.md operational only:** No status updates, no bloat
- **Fresh context:** Complete ONE atomic task, then exit

---

## Exit

After ONE task:
1. Gates passed ✅
2. State files updated ✅
3. Committed ✅
4. Markers emitted ✅

→ Exit. Loop continues with fresh context.
