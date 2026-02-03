---
name: sop-code-assist
version: 2.1.0
description: TDD implementation of code tasks following Explore → Plan → Code → Commit workflow. Use when executing .code-task.md files from ralph-orchestrator or when structured requirements are ready.
---

# Code Assist

TDD implementation of code tasks. Balances automation with user collaboration while adhering to existing patterns.

## Parameters

- **task_description** (required): Task to implement - file path, text, or URL
- **mode** (optional, default: `interactive`): `interactive` or `autonomous`
- **repo_root** (optional, default: cwd): Repository root path
- **documentation_dir** (optional, default: `specs/{goal}/implementation/{task_name}`)
- **task_name** (optional, auto-generated): Short descriptive name

**Constraints:**
- You MUST request all required parameters upfront in a single prompt

## Mode Behavior

<mode_interactive>
- Present proposed actions for confirmation
- Explain pros/cons when multiple approaches exist
- Ask clarifying questions about ambiguous requirements
- Use AskUserQuestion for user input
</mode_interactive>

<mode_autonomous>
- Execute without user confirmation
- Document decisions in guardrails.md
- If blocked: document in blockers.md, exit cleanly
- You MUST NOT use AskUserQuestion
</mode_autonomous>

## Steps

### 1. Setup

Read context and prepare environment.

- Create `{documentation_dir}/logs/` for build outputs
- Read `guardrails.md` for lessons learned
- Read `AGENTS.md` for build commands and constraints
- Read `.code-task.md` for requirements and acceptance criteria

**Constraints:**
- You MUST read AGENTS.md before any implementation
- You MUST read guardrails.md to avoid repeating past mistakes

### 2. Explore

Analyze requirements and research patterns.

- Analyze acceptance criteria from `.code-task.md`
- Research existing patterns in repository
- Identify test strategy

**Constraints:**
- You MUST understand existing patterns before introducing new ones
- You MUST identify edge cases during exploration

### 3. Plan

Design tests covering all acceptance criteria.

- Design test cases for each acceptance criterion
- Plan test structure (unit, integration, e2e as appropriate)

**Constraints:**
- Tests MUST be designed to initially fail (RED phase)
- You MUST cover both happy path and edge cases

### 4. Code

Implement using strict TDD: RED → GREEN → REFACTOR.

- Write tests BEFORE implementation code
- Run tests → verify failure (RED)
- Implement minimal code to pass
- Run tests → verify success (GREEN)
- Refactor for clarity
- Validate: all tests pass, build succeeds

**Constraints:**
- Tests MUST fail initially; if they pass, fix the test
- Implementation MUST be in `repo_root`, not `documentation_dir`
- You MUST run quality validation after tests pass

<quality_validation>
1. Invoke `code-simplifier` on modified artifacts
2. Invoke `code-reviewer` to validate against requirements
3. Address Critical/Important issues before Commit
</quality_validation>

<autonomous_signals>
> tdd:red {test_name}
> tdd:green {test_name}
</autonomous_signals>

### 5. Commit

Finalize and commit changes.

- Verify all tests passing, build succeeding
- `git add` relevant files
- `git commit` with Conventional Commits format
- Emit confession markers (autonomous mode)

**Constraints:**
- You MUST NOT push to remote
- You MUST verify build before commit

<autonomous_signals>
> confession: objective=[task name], met=[Yes/No], confidence=[N], evidence=[proof]
> task_completed: [Task name from plan]
</autonomous_signals>

Brackets `[]` are LITERAL in markers.

## Ralph Integration

When invoked from ralph-orchestrator in autonomous mode:

<at_startup>
- Read `guardrails.md` for lessons
- Read `AGENTS.md` for operational context
- Use `QUALITY_LEVEL` and `GATE_*` from `.ralph/config.sh` if defined
</at_startup>

<at_completion>
- Add memories to `guardrails.md` (orchestrator handles `scratchpad.md`)
- Emit confession and task_completed markers
</at_completion>

<guardrails_format>
### fix-{timestamp}-{hex}
> [What failed and how to fix it]
<!-- tags: testing, build | created: YYYY-MM-DD -->
</guardrails_format>

## Separation of Concerns

**sop-code-assist owns:**
- TDD implementation
- Confession markers
- guardrails.md updates

**ralph-orchestrator owns:**
- Task selection
- `<promise>COMPLETE</promise>` signal
- Quality gates execution
- plan.md updates

You MUST NOT emit `<promise>COMPLETE</promise>` — that's the orchestrator's job.

## Output

Primary: Code and tests in `repo_root`, commit with descriptive message.

Secondary (in `{documentation_dir}/`):
- `blockers.md` - If blocked (autonomous mode)
- `logs/` - Build outputs

## Quality Agents

**code-simplifier**: Invoke after tests pass. Reduces complexity, removes redundancy. Applies to code, configs, docs, plans.

**code-reviewer**: Invoke before commit. Validates against requirements. Applies to code, designs, plans, any deliverable.

## Related

- **sop-task-generator**: Creates `.code-task.md` inputs
- **sop-planning**: Creates detailed designs
- **ralph-orchestrator**: Invokes this skill in autonomous mode

## References

- `references/mode-behavior.md` - Interactive vs autonomous
- `references/tdd-workflow.md` - Detailed TDD guidance
- `references/troubleshooting.md` - Common issues
