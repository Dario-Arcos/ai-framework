---
name: sop-code-assist
description: "Use when executing .code-task.md files or when structured requirements are ready for implementation."
---

# Code Assist

Scenario-driven implementation of code tasks. Balances automation with user collaboration while adhering to existing patterns.

## Parameters

- **task_description** (required): Task to implement - file path, text, or URL
- **mode** (optional, default: `interactive`): `interactive` or `autonomous`
- **repo_root** (optional, default: cwd): Repository root path
- **documentation_dir** (optional, default: `docs/specs/{goal}/implementation/{task_name}`)
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
- After reading guardrails.md, list the 3 entries most relevant to this task and how each changes your approach — active engagement surfaces patterns that passive reading misses

### 2. Explore

Analyze requirements and research patterns.

- Analyze acceptance criteria from `.code-task.md`
- Research existing patterns in repository
- Check `.code-task.md` Metadata for `Scenario-Strategy`
  - If `not-applicable`: skip Plan (Step 3) and SDD cycle (Step 4a). Implement directly, then proceed to validation (Step 4b).
  - If `required` or absent: proceed with full SDD (Steps 3 → 4a → 4b)
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

Implement changes and validate quality.

#### 4a. Implementation

**When Scenario-Strategy is `required` or absent (default):**

Follow the scenario-driven-development skill for the full SCENARIO → SATISFY → REFACTOR cycle.

- Follow its Iron Law: no production code without a defined scenario first
- Follow its Gate Functions at each phase transition

**When Scenario-Strategy is `not-applicable`:**

Implement directly without SDD cycle. Apply existing patterns from the repository.

##### Anti-Reward-Hacking Constraint
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

<autonomous_signals>
> sdd:scenario {scenario_name}
> sdd:satisfy {scenario_name}
</autonomous_signals>

##### Satisfaction Model
Satisfaction is NOT boolean (green/red). It is convergence:
- Run scenarios → observe trajectories → measure fraction satisfying intent
- A scenario "satisfies" when the observable behavior matches the acceptance criteria
  across multiple execution paths, not just the happy path
- Report satisfaction as [M/N scenarios satisfied] — partial satisfaction is valid signal
- The SDD cycle runs UNTIL satisfaction converges (scenarios pass AND STAY PASSING)

##### Review Alignment Check
Before moving to validation, self-check against the criteria your reviewer will evaluate — failing review means rework with a fresh teammate, and all your implementation context is lost:

1. **Criteria coverage** — build a `Criterion → Scenario → Covered?` table. Every acceptance criterion from `.code-task.md` must map to at least one scenario.
2. **Input diversity** — each scenario must exercise 2+ distinct inputs with distinct expected outputs. A single-input test can be satisfied by a hardcoded return value.
3. **Assertion precision** — use exact comparisons (`toBe`, `toEqual`, `===`). Loose matchers (`toBeTruthy`, `string.contains`) and try/catch wrappers without value assertions mask incorrect behavior and trigger automatic review failure.

Address gaps before proceeding. The reviewer cannot see your reasoning — only your tests speak.

#### 4b. Validate

Runs for ALL tasks after implementation, regardless of Scenario-Strategy.

<quality_validation>
Invoke `code-simplifier` + `code-reviewer` + `edge-case-detector` + `performance-engineer` (parallel — all four are read-only, independent).

<mode_interactive>
1. Present findings summary grouped by severity (Critical, Important, Suggestion)
2. Ask user to confirm which issues to address before Commit
3. Address all confirmed Critical/Important issues
</mode_interactive>

<mode_autonomous>
1. Resolve all Critical and Important issues — fix the code, re-run affected tests, confirm green
2. Resolve Suggestion-level issues when the fix is straightforward (< 5 min)
3. Document what was resolved and rationale in guardrails.md
</mode_autonomous>
</quality_validation>

<runtime_validation>
**WHEN** the project has web or mobile UI (detect from: AGENTS.md/agents.md stack field, package.json dependencies, or presence of frontend frameworks):

Invoke the agent-browser skill for runtime validation. The skill loads the complete browser automation methodology — do NOT use CLI commands directly without loading the skill first.

Validation checks:
1. Navigate to the application URL, wait for load
2. Verify zero console errors
3. Verify zero page errors and zero failed network requests
4. **IF** the task modified UI components: take screenshots of affected views for visual verification
5. **IF** iOS flows apply: use platform-specific validation via the skill
6. **IF** feature-complete milestone: invoke /dogfood for exploratory QA — finds issues scenarios didn't anticipate

<mode_interactive>
1. Present console/errors output and screenshots to user
2. Ask user to confirm runtime is clean or identify issues to fix
3. Fix confirmed issues, re-validate until clean
</mode_interactive>

<mode_autonomous>
1. If console errors or network failures found: fix the root cause in code, re-validate until clean
2. If /dogfood finds issues: fix Critical/High severity, document Medium/Low in guardrails.md
3. If unfixable after 2 attempts (external dependency, environment issue): document in blockers.md with evidence and emit BLOCKED signal
4. Do NOT proceed to Commit with known Critical runtime errors — either fix or block
</mode_autonomous>

**WHEN** the project has NO web/mobile UI: skip runtime_validation.
</runtime_validation>

**Constraints:**
- Implementation MUST be in `repo_root`, not `documentation_dir`
- You MUST run validation (Step 4b) after implementation, regardless of Scenario-Strategy
- You MUST escalate to systematic-debugging after 2 unexpected failures

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
- Add memories to `.ralph/guardrails.md` using **Edit (append at end)**, never Write (overwrite) — concurrent teammates may write simultaneously
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

**edge-case-detector**: Invoke after tests pass. Detects boundary violations, concurrency bugs, resource leaks, silent failures.

**performance-engineer**: Invoke after tests pass. Detects query inefficiencies, algorithmic complexity, I/O bottlenecks, scalability anti-patterns.

## Related

- **sop-task-generator**: Creates `.code-task.md` inputs
- **sop-planning**: Creates detailed designs
- **ralph-orchestrator**: Invokes this skill in autonomous mode

## References

- `references/mode-behavior.md` - Interactive vs autonomous
- `references/troubleshooting.md` - Common issues
- `references/examples.md` - Usage examples
- scenario-driven-development skill - Full SDD workflow (Step 4a)
- verification-before-completion skill - Completion verification (Step 5)
- systematic-debugging skill - Root cause investigation (Step 2 bug fixes, Step 4a failure escalation)

## Scenario Artifact Note

Before implementation, check whether the configured discovery roots (Ralph: `.ralph/specs/{goal}/scenarios/`; non-Ralph: `docs/specs/{name}/scenarios/`) contain a relevant scenario file. The runtime answer comes from `_sdd_scenarios.scenario_files(cwd)`. If one exists, treat it as the observable contract for the work and implement against that committed artifact rather than inventing a new local interpretation. If no relevant scenario exists and the task changes behavior, ask the user whether to generate one via `scenario-driven-development` before writing production code.
