---
name: sop-code-assist
description: Use when executing .code-task.md files or when structured requirements are ready for implementation.
---

# Code Assist

Scenario-driven implementation of code tasks. Balances automation with user collaboration while adhering to existing patterns.

## Parameters

- **task_description** (required): Task to implement - file path, text, or URL
- **mode** (optional, default: `interactive`): `interactive` or `autonomous`
- **repo_root** (optional, default: cwd): Repository root path
- **documentation_dir** (optional, default: `.ralph/specs/{goal}/implementation/{task_name}`)
- **task_name** (optional, auto-generated): Short descriptive name

**Constraints for parameter acquisition:**
- You MUST request all required parameters upfront in a single prompt because repeated interruptions degrade the workflow
- You MUST support multiple input methods for task_description:
  - Direct text input
  - File path to a `.code-task.md` file
  - URL to a task description
- You MUST use appropriate tools to access content based on the input method
- You MUST confirm successful acquisition of all parameters before proceeding

## Mode Behavior

<mode_interactive>
- Present proposed actions for confirmation
- Explain pros/cons when multiple approaches exist
- Ask clarifying questions about ambiguous requirements
- Use AskUserQuestion for user input
</mode_interactive>

<mode_autonomous>
- Execute without user confirmation
- Document decisions in `.ralph/guardrails.md`
- If blocked: document in blockers.md, exit cleanly
- You MUST NOT use AskUserQuestion because autonomous mode must never block for input — blockers go to blockers.md
</mode_autonomous>

## Steps

### 1. Setup

Read context and prepare environment.

- Create `{documentation_dir}/logs/` for build outputs
- Read `guardrails.md` for lessons learned (under ralph: `.ralph/guardrails.md`)
- Read `AGENTS.md` for build commands and constraints (under ralph: `.ralph/agents.md`)
- Read `.code-task.md` for requirements and acceptance criteria
- Read all files listed in `Reference Documentation` and `Files to Read` sections of `.code-task.md`

**Constraints:**
- You MUST read AGENTS.md before any implementation
- You MUST read guardrails.md to avoid repeating past mistakes
- You MUST read all files listed in the task's `Reference Documentation` section

### 2. Explore

Analyze requirements and research patterns.

- Analyze acceptance criteria from `.code-task.md`
- Research existing patterns in repository
- Check `.code-task.md` Metadata for `Scenario-Strategy`
  - If `not-applicable`: skip SDD cycle (Steps 3-4), implement directly, proceed to Commit
  - If `required` or absent: proceed with full SDD
- Identify scenario strategy

<bug_fix_detection>
**IF** the task describes a defect (bug report, regression, unexpected behavior, error reproduction):

1. Invoke the systematic-debugging skill's Phases 1-3 BEFORE proceeding to Plan
2. Phase 1: Root Cause Investigation — reproduce, trace data flow, gather evidence
3. Phase 2: Pattern Analysis — find working examples, identify differences
4. Phase 3: Hypothesis — form and test a single hypothesis minimally

The root cause you identify becomes the specification for your first scenario in Step 4.

**You MUST NOT** design scenarios for a bug you haven't diagnosed. Symptom-based tests pass for the wrong reasons.
</bug_fix_detection>

**Constraints:**
- You MUST understand existing patterns before introducing new ones
- You MUST identify edge cases during exploration
- You MUST complete root cause investigation before planning scenarios for bug fixes

### 3. Plan

Design scenarios covering all acceptance criteria.

- Design scenarios for each acceptance criterion (scope: unit, integration, e2e as needed)

**Constraints:**
- Scenarios MUST define observable behavior before code exists (SCENARIO phase)
- You MUST cover both happy path and edge cases

### 4. Code

Implement using the scenario-driven-development skill.

- Follow the scenario-driven-development skill for the full SCENARIO → SATISFY → REFACTOR cycle
- Follow its Iron Law: no production code without a defined scenario first
- Follow its Gate Functions at each phase transition
- After all tests pass, run quality validation

#### Anti-Reward-Hacking Constraint
- NEVER modify existing tests to make them pass new code because scenarios are holdout sets — modifying them to match code is reward hacking
- NEVER weaken acceptance criteria to match implementation limitations because criteria define user intent, not implementation convenience
- If a scenario cannot be satisfied, escalate as blocker — do not adjust the scenario

<failure_escalation>
**IF** during SDD you hit unexpected failures (scenario unclear, stuck at SATISFY after 2 attempts, build breaks for unknown cause):

1. STOP the SDD cycle
2. Invoke the systematic-debugging skill — treat the failure as a bug
3. Find root cause before retrying
4. Return to SDD with understanding, not with hope

**You MUST NOT** retry the same approach more than twice without diagnosing why it fails. Thrashing wastes iterations and triggers the circuit breaker.
</failure_escalation>

**Constraints:**
- Implementation MUST be in `repo_root`, not `documentation_dir`
- You MUST run quality validation after tests pass
- You MUST escalate to systematic-debugging after 2 unexpected failures

<quality_validation>
When mode="autonomous" AND `.ralph/config.sh` exists: skip quality_validation.
Rationale: reviewer teammate + TaskCompleted hook handle validation externally.

Otherwise (interactive mode or standalone usage):
1. Invoke `code-simplifier` on modified artifacts
2. Invoke `code-reviewer` to validate against requirements
3. Address Critical/Important issues before Commit
</quality_validation>

<autonomous_signals>
> sdd:scenario {scenario_name}
> sdd:satisfy {scenario_name}
</autonomous_signals>

### Satisfaction Model
Satisfaction is NOT boolean (green/red). It is convergence:
- Run scenarios → observe trajectories → measure fraction satisfying intent
- A scenario "satisfies" when the observable behavior matches the acceptance criteria
  across multiple execution paths, not just the happy path
- Report satisfaction as [M/N scenarios satisfied] — partial satisfaction is valid signal
- The SDD cycle runs UNTIL satisfaction converges (scenarios pass AND STAY PASSING)

### 5. Commit

Finalize and commit changes.

- Invoke the verification-before-completion skill's 6-step gate
- Every claim ("tests pass", "build succeeds") requires fresh evidence
- `git add` relevant files
- `git commit` with Conventional Commits format
- Emit confession markers (autonomous mode)

**Constraints:**
- You MUST NOT push to remote because this could publish unreviewed code to shared repositories
- You MUST complete the verification-before-completion gate before commit
- Evidence format: `[Claim]: \`[command]\` → [output]`

<autonomous_signals>
> confession: objective=[task name], met=[Yes/No], confidence=[N], evidence=[proof]
> task_completed: [Task name from plan]
</autonomous_signals>

Brackets `[]` are LITERAL in markers.

## Ralph Integration

When invoked from ralph-orchestrator in autonomous mode:

<at_startup>
- Read `.ralph/guardrails.md` for lessons
- Read `.ralph/agents.md` for operational context
- Use `GATE_*` from `.ralph/config.sh` if defined
</at_startup>

<at_completion>
- Add memories to `.ralph/guardrails.md`
- Emit confession and task_completed markers
</at_completion>

<guardrails_format>
### fix-{timestamp}-{hex}
> [What failed and how to fix it]
<!-- tags: testing, build | created: YYYY-MM-DD -->
</guardrails_format>

## Separation of Concerns

**sop-code-assist owns:**
- Scenario-driven implementation
- Confession markers
- guardrails.md updates

**ralph-orchestrator owns:**
- Task selection and assignment
- Task completion (TaskUpdate status="completed")
- Quality gates execution (TaskCompleted hook)
- plan.md updates

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
- `references/troubleshooting.md` - Common issues
- `references/examples.md` - Usage examples
- scenario-driven-development skill - Full SDD workflow (Step 4)
- verification-before-completion skill - Completion verification (Step 5)
- systematic-debugging skill - Root cause investigation (Step 2 bug fixes, Step 4 failure escalation)
