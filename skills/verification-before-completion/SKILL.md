---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing — before committing, creating PRs, or reporting results. Requires running verification commands and confirming output before making any success claims. Evidence before assertions, always.
---

# Verification Before Completion

## Overview

Believing code works is not the same as proving it works. Memory of a passing test is not evidence. Confidence is not verification. Code is opaque weights — correctness is inferred exclusively from externally observable behavior, never from reading source.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

"I ran the tests earlier" is not evidence. "Tests passed" without output is not evidence. Only fresh, observable output counts.

## The 6-Step Gate

Every completion claim must pass through all six steps, in order.

### 1. IDENTIFY

List every claim you're about to make:
- "Tests pass"
- "Build succeeds"
- "Feature works as specified"
- "No regressions"

### 2. RUN

For each claim, execute the verification command NOW:
- Tests: Run the test suite
- Build: Run the build command
- Feature: Execute the specific behavior
- Regressions: Run the full suite, not just new tests

### 3. READ

Read the COMPLETE output of each command:
- Don't skim — read every line
- Check for warnings, not just errors
- Check exit codes, not just output text
- Look for skipped tests (they hide failures)

### 4. VERIFY

Confirm output matches your claim:
- All tests: PASSED (not "most tests")
- Build: SUCCESS with exit code 0
- Feature: Behaves as specified in requirements — verified by observing output, NEVER by reading source
- No new warnings introduced
- No skipped or pending tests hiding failures

### 5. SATISFY

Verify that execution evidence demonstrates genuine user satisfaction, not just boolean passage.

**Scenario Convergence:**
- List every defined scenario for the implemented work
- Confirm each scenario is satisfied through execution (not removed, not rewritten to match code)
- Report: `[N/M] scenarios satisfied` — all M must be satisfied to proceed

**Reward Hacking Check:**
- Were any scenarios or tests modified AFTER code was written to make them pass?
- Check `git diff` of test/scenario files: modifications to expectations after implementation = reward hacking
- If scenarios were changed: justify each change against original user intent, or revert

**Satisfaction Assessment:**
- For each scenario: "Would a user accept this behavior across realistic variations beyond the tested inputs?"
- Check for semantic correctness the assertions don't cover: rounding, display format, error message clarity, edge behavior
- If the answer is "it passes but a user might not accept it" → not satisfied

**Stability Verification:**
- A single passing run is insufficient — re-run verification to confirm stability
- If results differ between runs, the system is non-deterministic — investigate before claiming

**Convergence Gate:**
```
□ All defined scenarios satisfied through execution evidence
□ No scenarios removed or weakened during implementation
□ No test expectations modified to match code (reward hacking check)
□ Behavior satisfies user intent beyond the literal assertions
□ [N/M] scenarios satisfied — must be M/M to proceed
□ Verification stable across re-runs (not a lucky single pass)
```

If ANY gate fails, return to implementation. Do not proceed to CLAIM.

### 6. CLAIM

Only now may you state the claim, with evidence:

```
[Claim]: `[command]` → [output]
```

**Examples:**
```
Tests pass: `npm test` → 47 passed, 0 failed, 0 skipped
Build succeeds: `npm run build` → exit code 0, no warnings
Feature works: `curl /api/users/1` → {"id": 1, "name": "Alice"} (200 OK)
```

## Evidence Format

Always use this format when claiming completion:

```
[Claim]: `[command]` → [output]
```

The command must be the actual command you ran. The output must be the actual output you observed. No paraphrasing, no approximation.

**Satisfaction evidence format:**
```
Scenarios: [N/M] satisfied
Reward hacking: [clean | N scenarios modified — justified: reason]
Satisfaction: [genuine | concerns: specific concern]
```

## Common Failures

| Claim | Requires | NOT Sufficient |
|-------|----------|----------------|
| "Tests pass" | Fresh `test` command output showing all pass | "I ran them earlier" / "They should pass" |
| "Build succeeds" | Fresh `build` command output with exit code 0 | "It built before my change" / "No build errors" |
| "Bug is fixed" | Test that reproduced bug now passes + no regressions | "I changed the code that caused it" |
| "Feature complete" | All acceptance criteria verified with evidence | "I implemented all the requirements" |
| "No regressions" | Full test suite passes, not just new tests | "My changes are isolated" |
| "Works correctly" | Observable output matching expected behavior | "The logic looks right" |
| "Linter clean" | Linter output: 0 errors, 0 warnings | "Build passed" (linter ≠ compiler) |
| "Regression test works" | Red-green cycle verified (test fails without fix, passes with) | "Test passes" (without red-green) |
| "Agent completed task" | VCS diff shows correct changes + independent verification | "Agent reported success" |

## Red Flags — STOP

If you catch yourself saying or thinking:
- "should work"
- "probably passes"
- "seems to be working"
- "I'm confident that..."
- "based on my changes..."
- Expressing satisfaction before running verification
- Claiming completion in the same message as the last code change
- Using words like "likely," "presumably," "I believe"
- Rephrasing a success claim with different words to avoid the rule

**ALL mean: You haven't verified. Run the commands.**

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "I just ran the tests" | How long ago? What changed since? Run them again. |
| "My change is too small to break anything" | Small changes cause big breaks. Verify. |
| "The tests are slow, I'll skip this time" | Slow tests that run > fast tests that don't. |
| "I only changed a comment/doc" | Did you? Check git diff. Then verify. |
| "The CI will catch it" | CI catches it after you've already claimed completion. Verify locally first. |
| "I can see in the code that it works" | Reading code is not running code. Execute it. |
| "The same pattern works elsewhere" | This instance might differ. Verify THIS code. |
| "I'll fix it if it's broken" | Claim now, fix later = unreliable claims. Verify now. |
| "Linter passed so build is fine" | Linter ≠ compiler. Run the actual build. |
| "Agent said it's done" | Agent reports are claims, not evidence. Verify independently. |
| "Different words so rule doesn't apply" | Spirit over letter. Rephrasing doesn't exempt you. |

## Key Patterns

### Tests
```
Tests pass: `pytest tests/ -v` → 23 passed in 1.2s
No regressions: `pytest` → 156 passed, 0 failed, 0 skipped
```

### Regression Tests (TDD Red-Green)
```
✅ Write test → Run (pass) → Revert fix → Run (MUST FAIL) → Restore fix → Run (pass)
❌ "I wrote a regression test" (without verifying it fails when the fix is reverted)
```

A test that doesn't fail without the fix proves nothing. The red-green cycle is mandatory for regression tests.

### Build
```
Build succeeds: `npm run build` → compiled successfully, exit code 0
Type check: `tsc --noEmit` → no errors
Lint: `eslint src/` → no warnings, no errors
```

### Requirements
```
AC-1 verified: `curl -X POST /api/users -d '{"name":"test"}' ` → 201 Created
AC-2 verified: `curl /api/users/invalid` → 404 Not Found
AC-3 verified: `npm test -- --grep "validation"` → 5 passed
```

### Agent Delegation
When delegating work to subagents, verification still applies:
```
✅ Agent reports success → Check VCS diff → Verify changes independently → Report actual state
❌ Trust agent report → Echo agent's claims as your own
```

The delegating agent is responsible for verifying the subagent's claims through independent evidence, not by echoing the subagent's assertions.

## When to Apply

**ALWAYS** before any of these:
- Claiming a task is complete
- Marking a TaskUpdate as completed
- Creating a commit
- Reporting results to user
- Emitting confession markers
- Transitioning to next task

**There are NO exceptions.** The cost of running one more command is trivial. The cost of a false completion claim is wasted time, broken trust, and compounding errors.

**Rule applies to:**
- Exact phrases ("tests pass", "build succeeds", "done")
- Paraphrases and synonyms ("looks good", "should be fine", "all clear")
- Implications of success ("moving on to the next task", "let me commit this")
- ANY communication suggesting completion or correctness

## Integration

- **scenario-driven-development** — Precedes this gate. After SDD's Quality Integration (code-reviewer + code-simplifier agents), this gate runs. Scenario list and satisfaction criteria come from SDD's defined scenarios.
- **ralph-orchestrator** — Confession markers require evidence from this gate:
  ```
  > confession: objective=[task], met=[Yes/No], confidence=[N], satisfaction=[N/M scenarios], evidence=[proof from completion gate]
  ```
- **commit** — This gate runs before any commit
- **pull-request** — PR readiness requires all claims verified with fresh evidence

## Related

- **scenario-driven-development** — Ensures scenarios are defined; this skill ensures they're run before claiming done
- **systematic-debugging** — Root cause analysis; this skill ensures fixes are verified after debugging

## Artifact Handoff

| Receives | Produces |
|---|---|
| Satisfaction evidence from SDD (scenarios + execution output) | Verified completion claim with evidence format |
| Quality Integration results (code-reviewer + code-simplifier) | Satisfaction report: `[N/M] scenarios satisfied` |

**← From:** scenario-driven-development produces satisfaction evidence after SCENARIO→SATISFY→REFACTOR + Quality Integration.
