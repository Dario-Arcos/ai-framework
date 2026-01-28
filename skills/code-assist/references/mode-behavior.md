# Mode Behavior Reference

## Overview

The `mode` parameter controls how code-assist interacts with the user throughout the implementation process. This reference documents the exact behavior differences between `interactive` and `auto` modes.

## Mode Selection

### When to Use Interactive Mode

- **Learning:** User wants to understand the TDD process
- **Uncertain Requirements:** Details may need clarification
- **High Risk:** Changes affect critical systems
- **New Domain:** Unfamiliar technology or patterns
- **Collaboration:** User wants to participate in decisions

### When to Use Auto Mode

- **Well-Defined Tasks:** Clear requirements and acceptance criteria
- **Batch Processing:** Multiple tasks in sequence (ralph-orchestrator)
- **Time Constraints:** Need rapid implementation
- **Routine Tasks:** Familiar patterns with low risk
- **Background Execution:** Non-interactive environments

## Behavioral Differences by Phase

### Setup Phase

| Action | Interactive | Auto |
|--------|-------------|------|
| Parameter confirmation | Ask user to confirm | Log and proceed |
| Directory creation | Notify user | Log in progress.md |
| Instruction file selection | Present list, ask which to include | Auto-include CODEASSIST.md + core files |
| Missing CODEASSIST.md | Offer to create template | Note in context.md |

### Explore Phase

| Action | Interactive | Auto |
|--------|-------------|------|
| Requirements analysis | Discuss with user, ask clarifying questions | Document analysis in context.md |
| Pattern research | Share findings, ask if sufficient | Select most relevant patterns |
| Ambiguous requirements | Ask user to clarify | Make reasonable assumption, document it |
| Multiple valid approaches | Present options with pros/cons | Select best approach, document rationale |

### Plan Phase

| Action | Interactive | Auto |
|--------|-------------|------|
| Test strategy | Present strategy for approval | Document strategy and proceed |
| Test coverage | Discuss with user | Apply project defaults or 80% |
| Implementation sequence | Ask for preferences | Use standard sequencing |
| Risk identification | Discuss mitigations with user | Document risks and mitigations |

### Code Phase

| Action | Interactive | Auto |
|--------|-------------|------|
| Before each test | Explain what will be tested | Proceed directly |
| Test failure (RED) | Confirm failure is expected | Log and continue if expected |
| Unexpected failure | Discuss with user | Attempt to resolve, document if stuck |
| Implementation approach | Present options | Select most appropriate |
| Refactoring decisions | Ask for approval | Apply standard refactoring patterns |
| Convention alignment | Ask about ambiguous conventions | Match majority pattern in codebase |

### Validation Phase

| Action | Interactive | Auto |
|--------|-------------|------|
| Test results | Present full results | Log summary |
| Build results | Present output | Log success/failure |
| Coverage report | Discuss if below target | Note in progress.md |
| Checklist review | Walk through with user | Verify programmatically |

### Commit Phase

| Action | Interactive | Auto |
|--------|-------------|------|
| Commit message | Present for approval | Generate following conventions |
| Staged files | List and confirm | Stage relevant files |
| Pre-commit check | Ask to proceed | Proceed if all checks pass |
| Commit execution | Ask for final confirmation | Execute and document |

## Communication Patterns

### Interactive Mode Prompts

```markdown
## Asking for Confirmation
"I've completed the test strategy. Here's the summary:
- 5 unit tests covering core validation
- 2 integration tests for API interaction
- 3 edge case tests

Does this look complete, or should I add more scenarios?"

## Presenting Options
"For implementing the validation logic, I see two approaches:

**Option A: Regex-based**
- Pros: Simple, performant
- Cons: Hard to maintain, may miss edge cases

**Option B: Parser-based**
- Pros: More accurate, easier to extend
- Cons: Slightly more complex

Which would you prefer?"

## Reporting Progress
"Test `validate_email_returns_false_for_empty_string` is now passing.
Moving to the next test: `validate_email_handles_unicode_characters`.
Should I continue?"
```

### Auto Mode Logging

```markdown
## Decision Logging in progress.md

### Decision: Validation Approach
- **Timestamp:** 2026-01-28T10:30:00
- **Context:** Need to choose validation implementation
- **Options:**
  1. Regex-based (simple, performant)
  2. Parser-based (accurate, extensible)
- **Chosen:** Option 2 (Parser-based)
- **Rationale:** Project prioritizes correctness over raw performance,
  and existing codebase uses parser patterns for similar validations.

## Progress Updates
### Code Phase - Cycle 3 Complete
- Test: validate_email_handles_unicode
- Result: GREEN (passing)
- Implementation: Added unicode normalization before validation
- Refactoring: Extracted normalization to shared utility
```

## Error Handling by Mode

### Interactive Mode

```markdown
## On Unexpected Test Failure
"The test `validate_email_returns_true_for_valid` is failing unexpectedly.

**Expected:** True
**Actual:** TypeError: 'NoneType' object is not callable

This seems to be a setup issue rather than a logic error.
Should I:
1. Debug the test setup
2. Review the function signature
3. Something else?"

## On Build Failure
"The build failed with the following error:
[error details]

This appears to be a missing dependency issue.
Should I:
1. Add the dependency to requirements.txt
2. Use a different approach that doesn't need this dependency
3. Investigate further?"
```

### Auto Mode

```markdown
## On Unexpected Test Failure
### Challenge: Unexpected Test Failure
- **Test:** validate_email_returns_true_for_valid
- **Expected Failure:** Function not defined
- **Actual Failure:** TypeError: 'NoneType' object is not callable
- **Analysis:** Test setup issue - import statement incorrect
- **Resolution:** Fixed import path from `src.validate` to `src.validation.validate`
- **Result:** Test now fails as expected (function not defined)

## On Build Failure
### Challenge: Build Failure
- **Error:** ModuleNotFoundError: No module named 'email_validator'
- **Analysis:** Missing dependency not in requirements
- **Resolution:** Added `email-validator>=2.0.0` to requirements.txt
- **Result:** Build succeeds
```

## Escalation Rules

Even in auto mode, certain situations require user input:

| Situation | Action |
|-----------|--------|
| Tests fail for reasons that cannot be resolved | Pause and document, wait for input |
| Multiple approaches with equal merit and different trade-offs | Document both, ask user to decide |
| Security-sensitive changes | Pause and ask for confirmation |
| Breaking changes to public APIs | Pause and ask for confirmation |
| Exceeding time/iteration budget | Summarize progress, ask how to proceed |

## Mode Switching

You MAY suggest switching modes during execution:

```markdown
## Interactive → Auto
"We've resolved the initial uncertainties. The remaining 3 tests follow
the same pattern. Would you like me to continue in auto mode for the rest?"

## Auto → Interactive
"I've encountered a decision that requires your input:
[describe situation]

Switching to interactive mode for this decision.
After resolution, would you like to continue in auto or interactive mode?"
```

## Configuration

### CODEASSIST.md Integration

Projects can override default mode behavior in CODEASSIST.md:

```markdown
## Mode Overrides

### Force Interactive For
- Security-related changes
- Database schema modifications
- API contract changes

### Force Auto For
- Test file updates only
- Documentation updates
- Style/formatting changes
```

## Summary

| Aspect | Interactive | Auto |
|--------|-------------|------|
| **Pace** | User-controlled | Self-paced |
| **Decisions** | User makes or approves | Agent makes and documents |
| **Errors** | Discuss with user | Attempt to resolve, escalate if stuck |
| **Progress** | Verbal updates | Written in progress.md |
| **Best For** | Learning, uncertainty, high risk | Batch processing, routine, time-sensitive |
