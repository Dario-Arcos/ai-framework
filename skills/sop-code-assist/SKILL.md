---
name: sop-code-assist
description: Use when implementing code tasks with TDD methodology, executing .code-task.md files from ralph-orchestrator, or when structured requirements are ready for test-driven implementation.
---

# Code Assist

## Overview

This SOP guides implementation of code tasks using test-driven development, following an **Explore → Plan → Code → Commit** workflow. It balances automation with user collaboration while adhering to existing patterns and prioritizing readability and extensibility.

## Parameters

- **task_description** (required): Task to be implemented (file path, direct text, or URL)
- **additional_context** (optional): Supplementary information
- **documentation_dir** (optional, default: `specs/{goal}/implementation/{task_name}`): Directory for planning docs
- **repo_root** (optional, default: cwd): Repository root path
- **task_name** (optional): Short descriptive name (auto-generated if not provided)
- **mode** (optional, default: `interactive`): Execution mode - `interactive` or `autonomous`

**Constraints:**
- You MUST ask for all parameters upfront in a single prompt because this ensures efficient workflow

## Mode Behavior

### Interactive Mode
- Present proposed actions for confirmation
- Explain pros/cons when multiple approaches exist
- Review artifacts and solicit feedback before moving forward
- Ask clarifying questions about ambiguous requirements

### Autonomous Mode
- Execute autonomously without user confirmation
- Document decisions in commit messages and `guardrails.md`
- Select most appropriate approach when alternatives exist
- Provide comprehensive summary at completion
- NEVER use AskUserQuestion
- If blocked: document in `blockers.md`, exit cleanly

See `references/mode-behavior.md` for detailed guidance.

## Ralph Integration (Autonomous Mode)

When invoked from ralph-orchestrator, emit these markers:

### TDD Signals
```
> tdd:red {test_name}
> tdd:green {test_name}
```

### Confession Output (at completion)
```
> confession: objective=[task name], met=[Yes/No], confidence=[N], evidence=[proof]
> task_completed: [Task name from plan]
```

**Note:** Brackets `[]` are LITERAL.

### State Files
- **At startup:** Read `guardrails.md` if exists for lessons learned
- **At completion:** Add memories to `guardrails.md` (orchestrator handles `scratchpad.md`)

**Guardrails format** (use appropriate section: Fixes, Decisions, or Patterns):
```markdown
### fix-{timestamp}-{hex}
> [What failed and how to fix it]
<!-- tags: testing, build | created: YYYY-MM-DD -->
```

### Quality Gates
Use `QUALITY_LEVEL` and `GATE_*` from `.ralph/config.sh` if defined.

## Steps

### 1. Setup
- Create `{documentation_dir}/logs/` for build outputs
- Read `guardrails.md` and `CODEASSIST.md` if they exist
- Read `.code-task.md` for requirements and acceptance criteria

### 2. Explore Phase
- Analyze requirements from `.code-task.md`
- Research existing patterns in the repository
- Identify test strategy

### 3. Plan Phase
- Design tests covering all acceptance criteria
- Tests must be designed to initially fail (RED phase)

### 4. Code Phase
- Implement tests BEFORE implementation code
- Follow strict TDD: **RED → GREEN → REFACTOR**
- Emit `> tdd:red` / `> tdd:green` signals in autonomous mode
- Validate: all tests pass, build succeeds

See `references/tdd-workflow.md` for detailed guidance.

### 5. Commit Phase
- Verify all tasks complete, tests passing, build succeeding
- Follow Conventional Commits specification
- `git add` relevant files, `git commit`
- Emit confession markers in autonomous mode
- **MUST NOT** push to remote

## Key Constraints

- Tests MUST be implemented before any implementation code
- Code implementations MUST be in `repo_root`, not `documentation_dir`
- Tests MUST fail initially before implementation
- Build and test verification required before commits
- **MUST NOT** push to remote repositories

## Critical Separation of Concerns

This skill handles **implementation only**. The orchestrator handles lifecycle:

| Responsibility | Owner |
|----------------|-------|
| Task selection | ralph-orchestrator (PROMPT_build) |
| TDD implementation | **sop-code-assist** |
| Confession markers | **sop-code-assist** |
| `<promise>COMPLETE</promise>` signal | ralph-orchestrator (PROMPT_build) |
| Quality gates | ralph-orchestrator (PROMPT_build) |
| State file updates | Both (skill updates guardrails.md, orchestrator updates plan.md) |

**Never emit** `<promise>COMPLETE</promise>` from this skill—that's the orchestrator's job after all tasks are done.

## Desired Outcome

Upon successful completion:
1. **Tests written and passing** - All acceptance criteria covered
2. **Implementation complete** - Minimal code to pass tests
3. **Code committed** - Conventional commit with descriptive message
4. **Markers emitted** (autonomous mode) - `> confession:` and `> task_completed:` for orchestrator parsing

## Output

```
{documentation_dir}/
├── blockers.md     # Blockers (autonomous mode only, if blocked)
└── logs/           # Build outputs
```

**Primary outputs:** Code and tests in `repo_root`, commit with descriptive message.

## Related Skills

- **sop-task-generator** - Creates `.code-task.md` files
- **sop-planning** - Creates detailed designs
- **ralph-orchestrator** - Invokes this skill in autonomous mode

## References

| File | Content |
|------|---------|
| [mode-behavior.md](references/mode-behavior.md) | Interactive vs autonomous behavior |
| [tdd-workflow.md](references/tdd-workflow.md) | Detailed TDD guidance |
| [troubleshooting.md](references/troubleshooting.md) | Common issues |

---

*Version: 2.0.0 | Updated: 2026-02-02*
