---
name: ralph
description: Autonomous development pipeline. Detects current state and resumes from any phase.
argument-hint: "[specs/goal-name]"
disable-model-invocation: true
---

Invoke the ai-framework:ralph-orchestrator skill and follow it exactly.

Before executing the skill workflow, detect current pipeline state:

## State Detection

Scan `specs/` for existing goals. For each (or $ARGUMENTS if provided), check artifacts:

| Artifact | Phase |
|----------|-------|
| All `*.code-task.md` with `Status: COMPLETED` | COMPLETE |
| Any `*.code-task.md` with `Status: PENDING` | code-assist |
| `implementation/plan.md` without task files | task-generator |
| `design/detailed-design.md` | planning |
| `discovery.md` | discovery-complete |
| `investigation.md` + `specs-generated/` | reverse-complete |
| Nothing | NEW |

## Confirm Before Execution

Use AskUserQuestion to confirm detected state:

- If resumable: "Resume [goal] from [phase]" as recommended option
- If new: "Forward (build new)" or "Reverse (investigate existing)"
- If multiple goals: let user choose

Surface `blockers.md` content if exists.

After confirmation, proceed with skill workflow.
