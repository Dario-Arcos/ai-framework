# Code Assist Examples

## Overview

This reference provides practical examples of sop-code-assist usage, demonstrating the complete flow from task input to committed code.

## Example 1: Simple Task from Text

**Input:**
```bash
/sop-code-assist task_description="Add logout button to navbar"
```

**Flow:**
1. **Setup**: Creates `.sop/planning/implementation/logout-button/`
2. **Explore**: Analyzes navbar component, existing auth patterns
3. **Plan**: Designs test strategy (button renders, click logs out, redirect works)
4. **Code**: RED -> GREEN -> REFACTOR cycle
5. **Commit**: `feat(auth): add logout button to navbar`

**Artifacts Created:**
```text
.sop/planning/implementation/logout-button/
├── context.md      # Navbar structure, auth patterns, dependencies
├── plan.md         # Test scenarios for button behavior
├── progress.md     # TDD cycles, refactoring notes
└── logs/           # Build outputs
```

---

## Example 2: Task from .code-task.md File

**Input:**
```bash
/sop-code-assist task_description="specs/auth/implementation/step01/task-01.code-task.md"
```

**Flow:**
1. **Setup**: Reads task file context section, creates planning directory
2. **Explore**: Follows task's Context section for codebase analysis
3. **Plan**: Uses task's Implementation Guidance, creates test plan
4. **Code**: Implements per Specification section with TDD
5. **Commit**: Conventional commit, marks task as COMPLETED

**Key Difference:** The .code-task.md file provides structured requirements, reducing the exploration phase and enabling auto mode execution.

---

## Example 3: Interactive Mode with Clarification

**Input:**
```bash
/sop-code-assist task_description="Create email validator" mode="interactive"
```

**Interactive Flow:**

1. **Parameter Gathering:**
   > "I see you want to create an email validator. Could you clarify:
   > - Should it validate format only, or also check if the domain exists?
   > - What should happen for empty input - return false or raise an error?
   > - Are there specific edge cases you want to handle (unicode, plus addressing)?"

2. **Test Strategy Approval:**
   > "Here's my proposed test strategy:
   > - 5 unit tests for valid email formats
   > - 4 unit tests for invalid formats
   > - 2 edge case tests (unicode, plus addressing)
   >
   > Does this look complete?"

3. **Implementation Decision:**
   > "For the validation approach, I see two options:
   > - **Regex**: Simple, fast, but may miss edge cases
   > - **Parser**: More accurate, easier to extend
   >
   > Which would you prefer?"

---

## Example 4: Auto Mode Batch Processing

**Input (via ralph-orchestrator):**
```
task_description="specs/feature/implementation/step02/task-03-add-tests.code-task.md"
mode="auto"
```

**Auto Flow:**
- No user prompts during execution
- All decisions documented in progress.md
- Errors trigger pause and documentation, not user interaction
- Summary provided at completion

**Decision Log Entry (progress.md):**
```markdown
### Decision: Test Framework Selection
- **Timestamp:** 2026-01-28T14:30:00
- **Context:** Project has both pytest and unittest installed
- **Analysis:** Existing tests use pytest patterns (fixtures, parametrize)
- **Chosen:** pytest
- **Rationale:** Consistency with existing test suite
```

---

## Example 5: Error Recovery

**Input:**
```bash
/sop-code-assist task_description="Add caching to API client"
```

**Flow with Error:**
1. **Setup**: Creates documentation structure
2. **Explore**: Identifies API client patterns
3. **Plan**: Designs cache invalidation strategy
4. **Code (RED)**: Test fails as expected
5. **Code (GREEN)**: Implementation fails - missing dependency

**Error Handling (Interactive):**
> "The build failed with:
> `ModuleNotFoundError: No module named 'redis'`
>
> Should I:
> 1. Add redis to dependencies
> 2. Use in-memory cache instead (no external dependency)
> 3. Something else?"

**Error Handling (Auto):**
```markdown
### Challenge: Missing Dependency
- **Error:** ModuleNotFoundError: No module named 'redis'
- **Analysis:** Redis not in project dependencies, in-memory cache exists
- **Resolution:** Using existing InMemoryCache class
- **Rationale:** Matches existing patterns, avoids new dependency
```
