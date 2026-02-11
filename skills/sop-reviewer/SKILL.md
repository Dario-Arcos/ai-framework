---
name: sop-reviewer
description: Use when validating completed implementation tasks against SDD compliance, behavioral satisfaction, and reward hacking detection. Invoked by reviewer teammates after TaskCompleted hook gates pass, or standalone for manual review.
---

# SDD Reviewer

Validates implementation tasks against Scenario-Driven Development compliance. Based on [StrongDM SDD methodology](https://factory.strongdm.ai/) and [Agent-SOP](https://github.com/strands-agents/agent-sop) structure.

Code is opaque weights. You validate through externally observable behavior, not by reading source. If scenarios weren't defined before code, or behavior doesn't satisfy user intent, no amount of clean architecture matters.

## Parameters

- **task_id** (required): Task identifier (e.g., `1`, `task-slug`)
- **task_file** (required): Path to `.code-task.md` file with acceptance criteria
- **goal** (optional): High-level goal description for context
- **mode** (optional, default: `interactive`): `interactive` or `autonomous`

**Constraints:**
- You MUST have both `task_id` and `task_file` before proceeding

## Mode Behavior

<mode_interactive>
- Present findings at each gate, ask for confirmation before proceeding
- Use AskUserQuestion when a gate result is ambiguous
- Allow user to override Suggestion-level findings
</mode_interactive>

<mode_autonomous>
- Execute all gates without user interaction
- Write review to disk — never use AskUserQuestion
- Document blockers in `.ralph/reviews/task-{task_id}-blockers.md` if unable to complete
- You MUST NOT use AskUserQuestion in autonomous mode
</mode_autonomous>

## Steps

### 1. Read Context

Gather all evidence before evaluating.

- Read `.code-task.md` at `{task_file}` — extract acceptance criteria, Scenario-Strategy field, blocked-by relationships
- Read `.ralph/agents.md` — project context, stack, constraints
- Run `git log --oneline -5` — recent commit history
- Run `git diff HEAD~1 --stat` — files changed in last commit
- Read `.ralph/guardrails.md` — accumulated project lessons

**Constraints:**
- You MUST read the task file before any evaluation
- You MUST NOT skip git history — it provides ordering evidence for SDD compliance

### 2. SDD Compliance Gate (BLOCKING)

Verify the implementation followed scenario-driven development ordering.

**You MUST verify ALL of the following:**

1. **Scenarios defined BEFORE code** — Check git history for evidence that scenario definitions (in task file, test files, or conversation) preceded implementation commits. If Scenario-Strategy is `not-applicable`, this sub-check is waived.
2. **Scenarios describe end-to-end user stories** — Scenarios MUST use concrete values and describe observable behavior from user perspective. Assertions against implementation internals are insufficient.
3. **Scenarios validated through execution** — Observable output MUST exist (test results, command output, screenshots). "It should work" or "verified by reading code" is NOT validation.
4. **All previous scenarios still satisfy** — Regression check. New implementation MUST NOT break previously passing scenarios.

**Constraints:**
- You MUST report FAIL if ANY sub-check fails, regardless of code quality
- You MUST NOT proceed to Step 3 if this gate fails — report immediately
- If Scenario-Strategy is `not-applicable`, verify the task genuinely doesn't need scenarios (config-only, docs-only, scaffolding). If it modifies behavior, it needs scenarios regardless of the field value.

### 3. Behavioral Satisfaction

Assess convergence — not boolean pass/fail.

**You MUST evaluate satisfaction as convergence:**
- "Of observed trajectories, what fraction satisfies user intent?"
- A scenario "satisfies" when observable behavior matches acceptance criteria across realistic variations, not just the happy path
- Report as `[M/N scenarios satisfied]` — partial satisfaction is valid signal

**You MUST check:**
- Edge cases: boundary values, empty inputs, error paths
- Floating-point and rounding: display precision matches user expectations
- UX completeness: user-facing behavior is coherent end-to-end
- Real behavior: test code exercises actual implementation, not mocks or stubs

**Constraints:**
- You MUST NOT treat satisfaction as boolean (green/red)
- You SHOULD verify test code exercises real behavior, not mock return values
- You MAY flag scenarios that pass but produce unsatisfying user experience

### 4. Reward Hacking Detection (BLOCKING)

Detect patterns that game the validation system. Any finding here is automatic FAIL.

**You MUST check for:**

1. **Scenario rewriting** — Did the agent modify ANY existing scenario during implementation? Scenarios are holdout sets — altering them to match code is reward hacking.
2. **Trivial satisfaction** — Could any scenario pass with `return true`, a hardcoded value, or single-input oracle? Demand variant scenarios that prevent gaming.
3. **Precision evasion** — Do assertions use loose comparisons that mask incorrect behavior? (`int()` truncation, missing `round()`, string-contains instead of exact match)
4. **Code-first scenarios** — Evidence that scenarios were written AFTER code to describe what was built rather than what should satisfy. Symptom: scenarios mirror implementation structure instead of user experience.

**Constraints:**
- You MUST report FAIL if ANY pattern is detected
- You MUST NOT downgrade reward hacking findings to Suggestion level
- You SHOULD check git history timestamps for scenario vs. code ordering

### 5. Write Review

Output structured review to disk.

**Output path:** `.ralph/reviews/task-{task_id}-review.md`

**Template:**
```markdown
# Review: Task {task_id}

## Verdict: {PASS|FAIL}

## SDD Compliance: {PASS|FAIL}
{findings}

## Behavioral Satisfaction: [{M}/{N} satisfied]
{findings per scenario}

## Reward Hacking: {CLEAN|DETECTED}
{findings or "No patterns detected"}

## Findings

### Critical
{list or "None"}

### Important
{list or "None"}

### Suggestions
{list or "None"}

## Summary
{8-word summary}
```

**Constraints:**
- You MUST use the template structure above
- You MUST categorize every finding as Critical, Important, or Suggestion
- You MUST include an 8-word summary for lead consumption

## Output

- `.ralph/reviews/task-{task_id}-review.md` — full review
- SendMessage to lead: 8-word summary (e.g., "Task 3: PASS, SDD compliant, 4/4 satisfied")

## Ralph Integration

<at_startup>
- Read `.ralph/guardrails.md` for accumulated lessons
- Read `.ralph/agents.md` for project context
</at_startup>

<at_completion>
- Emit confession marker if review process revealed own limitations
- Append non-obvious lessons to `.ralph/guardrails.md`:
```markdown
### review-{descriptive-slug}
> [What the review revealed that future reviewers should know]
<!-- tags: task-{task_id} | created: YYYY-MM-DD -->
```
</at_completion>

## Constraints (RFC 2119)

- You MUST NOT modify implementation code — reviewers observe, never change
- You MUST validate through observable behavior, not code reading (StrongDM: "code as opaque weights")
- You MUST report FAIL if SDD compliance gate fails, regardless of code quality
- You MUST report FAIL if reward hacking is detected, regardless of other findings
- You SHOULD check that Scenario-Strategy field in `.code-task.md` was respected
- You SHOULD verify convergence across multiple execution paths, not just happy path
- You MAY suggest improvements as Suggestion-level findings without affecting verdict

## References

- [review-protocol.md](references/review-protocol.md) — Detailed checklists and patterns catalog
