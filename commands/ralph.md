---
name: ralph
description: Autonomous development pipeline with state detection. Detects current phase and resumes from any point.
allowed-tools: Read, Glob, Grep, Bash(ls *), Bash(find *), AskUserQuestion
argument-hint: "[specs/goal-name]"
disable-model-invocation: true
---

# Ralph - Autonomous Development Pipeline

Execute the SOP pipeline with automatic state detection and resumption.

## Arguments

$ARGUMENTS

- If path provided: Use that goal directory
- If empty: Scan `specs/` for existing goals

## Execution

### 1. Detect Current State

**Scan for goals:**

```bash
ls -d specs/*/ 2>/dev/null
```

**For each goal (or specified path), check artifacts in order:**

| Check | Files | Phase |
|-------|-------|-------|
| Tasks completed? | All `*.code-task.md` with `Status: COMPLETED` | COMPLETE |
| Tasks pending? | Any `*.code-task.md` with `Status: PENDING` | code-assist |
| Plan exists? | `implementation/plan.md` without task files | task-generator |
| Design exists? | `design/detailed-design.md` | planning |
| Discovery exists? | `discovery.md` | discovery-complete |
| Investigation exists? | `investigation.md` + `specs-generated/` | reverse-complete |
| Nothing? | Empty directory | NEW |

**Extract context:**
- Current phase name
- Next task (if code-assist): first PENDING not blocked by incomplete tasks
- Blockers: read `blockers.md` if exists

### 2. Confirm with User

Use AskUserQuestion with detected state:

**If goal(s) found:**
- Option 1: "Resume [goal] from [phase]" (recommended if resumable)
- Option 2: "Start new goal"
- Option 3: "View detailed status"

**If no goals:**
- Option 1: "Start new goal (Forward)"
- Option 2: "Start investigation (Reverse)"

### 3. Execute

After confirmation, invoke `ai-framework:ralph-orchestrator` with:
- goal: confirmed goal path or new goal description
- phase: detected phase or "fresh"
- mode: user preference (interactive/autonomous)

## Notes

- Never proceed without AskUserQuestion confirmation
- If multiple goals exist, let user choose
- Surface blockers.md content in status display
- Follow ralph-orchestrator skill exactly after confirmation
