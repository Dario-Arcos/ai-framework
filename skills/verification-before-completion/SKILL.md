---
name: verification-before-completion
version: 1.0.0
description: Evidence-based completion gate. Use before ANY claim that work is done, tests pass, or build succeeds.
---

# Verification Before Completion

## Overview

Believing code works is not the same as proving it works. Memory of a passing test is not evidence. Confidence is not verification.

**Core principle:** Evidence before claims, always.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

"I ran the tests earlier" is not evidence. "Tests passed" without output is not evidence. Only fresh, observable output counts.

## The 5-Step Gate

Every completion claim must pass through all five steps, in order.

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
- Feature: Behaves as specified in requirements
- No new warnings introduced

### 5. CLAIM

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

## Common Failures

| Claim | Requires | NOT Sufficient |
|-------|----------|----------------|
| "Tests pass" | Fresh `test` command output showing all pass | "I ran them earlier" / "They should pass" |
| "Build succeeds" | Fresh `build` command output with exit code 0 | "It built before my change" / "No build errors" |
| "Bug is fixed" | Test that reproduced bug now passes + no regressions | "I changed the code that caused it" |
| "Feature complete" | All acceptance criteria verified with evidence | "I implemented all the requirements" |
| "No regressions" | Full test suite passes, not just new tests | "My changes are isolated" |
| "Works correctly" | Observable output matching expected behavior | "The logic looks right" |

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

## Key Patterns

### Tests
```
Tests pass: `pytest tests/ -v` → 23 passed in 1.2s
No regressions: `pytest` → 156 passed, 0 failed, 0 skipped
```

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
Subagent task verified: Read subagent output → [specific evidence from output]
```

The delegating agent is responsible for verifying the subagent's claims.

## When to Apply

**ALWAYS** before any of these:
- Claiming a task is complete
- Marking a TaskUpdate as completed
- Creating a commit
- Reporting results to user
- Emitting confession markers
- Transitioning to next task

**There are NO exceptions.** The cost of running one more command is trivial. The cost of a false completion claim is wasted time, broken trust, and compounding errors.

## Integration

- **sop-code-assist Step 5** — This gate runs before commit
- **ralph-orchestrator** — Confession markers require evidence from this gate:
  ```
  > confession: objective=[task], met=[Yes/No], confidence=[N], evidence=[proof from 5-step gate]
  ```
- **pull-request** — PR readiness requires all claims verified with fresh evidence

## Related

- **test-driven-development** — Ensures tests exist; this skill ensures they're run before claiming done
- **systematic-debugging** — Root cause analysis; this skill ensures fixes are verified after debugging
