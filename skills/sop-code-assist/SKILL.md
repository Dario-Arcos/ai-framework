---
name: sop-code-assist
description: Use when implementing code tasks with TDD methodology, executing .code-task.md files from ralph-orchestrator, or when structured requirements are ready for test-driven implementation.
---

# Code Assist

## Overview

This skill guides the implementation of code tasks using test-driven development principles, following a structured **Explore → Plan → Code → Commit** workflow. It balances automation with user collaboration while adhering to existing package patterns and prioritizing readability and extensibility.

The agent acts as a **Technical Implementation Partner** and **TDD Coach** - providing guidance, generating test cases and implementation code that follows existing patterns, avoids over-engineering, and produces idiomatic, modern code in the target language.

**Source:** Based on strands-agents/agent-sop `sop-code-assist.sop.md`

## When to Use

- After `sop-task-generator` has created `.code-task.md` files
- When you have a structured task with clear requirements
- For implementing features following TDD methodology
- During the execution phase of the ralph-orchestrator

## When NOT to Use

| Situation | Why Not | Use Instead |
|-----------|---------|-------------|
| No task definition exists | Need structured input | `sop-task-generator` first |
| Requirements unclear | Need clarification | `sop-planning` first |
| Exploring existing code | Not for analysis | `sop-reverse` |
| Simple one-liner fixes | Overhead exceeds benefit | Direct implementation |

## Parameters

- **task_description** (required): Description of the task to implement. Can be a `.code-task.md` file path, direct text, or URL.
- **additional_context** (optional): Supplementary information for implementation context
- **documentation_dir** (optional, default: `specs/{task_name}`): Directory for planning documents. When invoked from ralph-orchestrator, uses `specs/{goal}/implementation/{task_name}/`.
- **repo_root** (optional, default: current working directory): Root directory for code implementation
- **task_name** (optional): Short descriptive name for the task. Auto-generated if not provided.
- **mode** (optional, default: `interactive`): Execution mode - `interactive` or `autonomous`

**Constraints for parameter acquisition:**
- You MUST ask for all parameters upfront in a single prompt because this ensures efficient workflow and prevents repeated interruptions during execution
- You MUST support multiple input methods for task_description:
  - Direct text input
  - File path to `.code-task.md`
  - Directory path (will look for task files within)
- You MUST normalize mode input to `interactive` or `autonomous`
- You MUST validate directory paths and generate task_name if not provided
- You MUST confirm successful acquisition of all parameters before proceeding
- If mode is `autonomous`, you MUST warn the user that no further interaction will be required

## Mode Behavior

Apply these patterns throughout all steps based on the selected mode.

### Interactive Mode

- Present proposed actions and ask for confirmation before proceeding
- When multiple approaches exist, explain pros/cons and ask for user preference
- Review artifacts and solicit specific feedback before moving forward
- Ask clarifying questions about ambiguous requirements
- Pause at key decision points to explain reasoning
- Adapt to user feedback and preferences
- Provide educational context when introducing new patterns

### Autonomous Mode

- Execute all actions autonomously without user confirmation
- Document all decisions, assumptions, and reasoning in `progress.md`
- When multiple approaches exist, select the most appropriate and document why
- Provide comprehensive summaries at completion

**Autonomous Mode Constraints (MUST follow):**
- NEVER use AskUserQuestion under any circumstance
- NEVER block waiting for user input
- If blocked by environment issues (missing dependencies, tools, etc.):
  1. Document blocker in `progress.md` with full details
  2. Write to `.ralph/blockers.json` if the file exists
  3. Exit cleanly - let the orchestrator handle recovery
- Make reasonable assumptions and document them rather than asking
- Choose the safest/simplest approach when ambiguous

See `references/mode-behavior.md` for detailed guidance.

## Important Notes

### Separation of Concerns

This skill maintains **strict separation** between documentation and code:
- All documentation about the implementation process → `{documentation_dir}`
- All actual code (tests AND implementation) → `{repo_root}`
- **NEVER** place code files in documentation directories

### CODEASSIST.md Integration

If `CODEASSIST.md` exists in repo_root, it contains additional constraints, pre/post SOP instructions, examples, and troubleshooting specific to this project. Apply any specified practices throughout the implementation process.

## Steps

### Step 1: Setup

Initialize the project environment and create necessary directory structures.

**You MUST:**
- Validate and create the documentation directory structure:
  - Create `{documentation_dir}/implementation/{task_name}/` with `logs/` subdirectory
  - Verify directory structure was created successfully before proceeding
- Discover existing instruction files (CODEASSIST.md, README.md, CONTRIBUTING.md, etc.)
- Read CODEASSIST.md if found and apply its constraints throughout
- Create `context.md` using `templates/context.md.template`
- Create `progress.md` using `templates/progress.md.template`
- Document project structure, requirements, patterns, and dependencies

**You MUST NOT:**
- Proceed if directory creation fails because missing directories cause file write failures and lost work later
- Place code implementations in documentation directory because mixing code with docs violates separation of concerns and breaks build processes
- Skip context gathering even if the task seems simple because missing context leads to implementations that don't fit project patterns

**Verification:** Directory structure created, context.md and progress.md initialized.

---

### Step 2: Explore Phase

#### 2.1 Analyze Requirements and Context

**You MUST:**
- Create a clear list of functional requirements and acceptance criteria
- Determine appropriate file paths and programming language
- Align with existing project structure and technology stack
- In interactive mode: engage user in discussions about requirements
- In autonomous mode: document analysis in context.md

**You MUST NOT:**
- Make assumptions about requirements without verification because unverified assumptions lead to implementations that miss actual needs
- Skip edge case identification because unhandled edge cases cause production bugs and user frustration

#### 2.2 Research Existing Patterns

**You MUST:**
- Search current repository for relevant code, patterns, and information
- Create a dependency map showing how new code will integrate
- Update context.md with identified implementation paths
- Document any best practices found in internal documentation

#### 2.3 Create Code Context Document

**You MUST:**
- Update context.md with requirements, implementation details, patterns, and dependencies
- Focus on high-level concepts rather than detailed implementation code
- Keep documentation concise and focused on guiding implementation

**You MUST NOT:**
- Include complete code implementations in documentation because documentation should guide, not duplicate, and duplicated code becomes stale
- Create overly detailed specifications that duplicate actual code because over-specification creates maintenance burden and divergence from implementation

**Verification:** context.md contains requirements, patterns, and implementation paths.

---

### Step 3: Plan Phase

#### 3.1 Design Test Strategy

**You MUST:**
- Cover all acceptance criteria with at least one test scenario
- Define explicit input/output pairs for each test case
- Save test scenarios to `{documentation_dir}/implementation/{task_name}/plan.md`
- Design tests that will initially fail (RED phase)

**You MUST NOT:**
- Create mock implementations during test design because mocks during design contaminate the RED phase and mask failing tests
- Include complete test code in documentation (use high-level descriptions) because test code belongs in test files, not documentation that becomes stale

#### 3.2 Implementation Planning & Tracking

**You MUST:**
- Save implementation plan to plan.md
- Include all key implementation tasks
- Maintain implementation checklist in progress.md using markdown checkbox format
- Display current checklist status after each major step

**You SHOULD:**
- Consider performance, security, and maintainability implications
- Use diagrams or pseudocode rather than actual implementation code

**Verification:** plan.md contains test strategy and implementation approach.

---

### Step 4: Code Phase

#### 4.1 Implement Test Cases

**You MUST:**
- Save test implementations to appropriate test directories in repo_root
- Implement tests for ALL requirements BEFORE writing ANY implementation code
- Follow testing framework conventions used in existing codebase
- Execute tests to verify they fail as expected (RED phase)
- Document failure reasons in progress.md

**You MUST NOT:**
- Place test code files in documentation directory because tests must be in repo_root to be discovered and executed by test runners
- Write implementation code before tests because writing code first violates TDD and produces tests that verify implementation rather than requirements

**Handling Blockers by Mode:**

**Interactive mode** - Seek user input if:
- Tests fail for unexpected reasons you cannot resolve
- Structural issues with test framework
- Environment issues preventing test execution

**Autonomous mode** - NEVER use AskUserQuestion. Instead:
- Document blocker in progress.md with full details
- Write blocker to `.ralph/blockers.json` (if exists)
- Exit cleanly with status indicating blocker
- Let the orchestrator handle recovery

See `references/mode-behavior.md` for blocker handling patterns.

#### 4.2 Develop Implementation Code

**You MUST:**
- Follow strict TDD cycle: **RED → GREEN → REFACTOR**
- Document each TDD cycle in progress.md
- Implement only what is needed to make current test(s) pass
- Follow coding style and conventions of existing codebase
- Execute tests after each implementation step

**You MUST:**
- Follow YAGNI, KISS, and SOLID principles
- Ensure all implementation code is in repo_root, not documentation_dir

See `references/tdd-workflow.md` for detailed TDD guidance.

#### 4.3 Refactor and Optimize

**You MUST:**
- Check that all tests pass before refactoring
- Examine code around changes to match existing conventions:
  - Naming conventions
  - Code organization patterns
  - Error handling patterns
  - Documentation style
  - Testing patterns
- Prioritize readability and maintainability over clever optimizations
- Maintain test passing status throughout refactoring

#### 4.4 Validate Implementation

**You MUST:**
- Execute relevant test command and verify all tests pass
- Execute relevant build command and verify builds succeed
- Verify all items in implementation plan have been completed
- Provide complete test execution output

**You MUST NOT:**
- Claim implementation is complete if any tests are failing because failing tests indicate unmet requirements or broken functionality
- Skip build validation because unbuildable code cannot be deployed and may have syntax or dependency errors

**Verification:** All tests pass, build succeeds, checklist complete.

---

### Step 5: Commit Phase

**You MUST:**
- Check that all tasks are complete before proceeding
- Follow Conventional Commits specification
- Use `git status` to check modified files
- Use `git add` to stage relevant files
- Execute `git commit` with prepared message
- Document commit hash and status in progress.md

**You MUST NOT:**
- Commit until builds AND tests are verified passing because committing broken code pollutes history and may break CI/CD pipelines
- Push changes to remote repositories because pushing is a user decision that may require review, approval, or coordination with team

**You SHOULD:**
- Include "Assisted by sop-code-assist skill" in commit footer

**Verification:** Commit created, hash documented in progress.md.

---

## Desired Outcome

- Complete, well-tested code implementation meeting specifications
- Comprehensive test suite validating the implementation
- Clean, documented code that:
  - Follows existing package patterns and conventions
  - Prioritizes readability and extensibility
  - Avoids over-engineering and over-abstraction
  - Is idiomatic and modern in the target language
- Well-organized artifacts in `{documentation_dir}/implementation/{task_name}/`
- Documentation of key design decisions and implementation notes
- Properly committed changes with conventional commit messages

## Artifacts

```text
{documentation_dir}/implementation/{task_name}/
├── context.md      # Workspace structure, requirements, patterns, dependencies
├── plan.md         # Test scenarios, implementation planning, strategy
├── progress.md     # TDD cycles, refactoring notes, commit status
└── logs/           # Build outputs (one log per package)
```

## Related Skills

- **sop-task-generator** - Creates `.code-task.md` files for this skill to consume
- **sop-planning** - Creates detailed designs that inform task generation
- **sop-discovery** - Explores constraints and risks before planning
- **ralph-orchestrator** - Autonomous execution loop that can invoke this skill
- **test-driven-development** - Detailed TDD methodology reference

---

## Examples

### Example 1: New Feature Implementation

**Input:**
```text
/sop-code-assist task="specs/auth/implementation/step01/task-01-jwt-auth.code-task.md"
```

**Process:**
1. Read task file, extract acceptance criteria
2. Write failing test for JWT token generation
3. Implement minimal code to pass
4. Refactor for clarity
5. Run all quality gates

**Output:**
- `src/auth/jwt.ts` - Implementation
- `tests/auth/jwt.test.ts` - Test coverage
- Task file updated with Status: COMPLETED

### Example 2: Bug Fix with TDD

**Input:**
```text
/sop-code-assist task="Fix null pointer in user validation" --mode=interactive
```

**Process:**
1. Write test reproducing the bug
2. Verify test fails
3. Fix minimal code
4. Verify test passes
5. Check no regression

### Example 3: Autonomous Mode

**Input:**
```text
/sop-code-assist task="path/to/task.code-task.md" --mode=autonomous
```

**Behavior:**
- No AskUserQuestion calls
- Blockers written to `.ralph/blockers.json`
- Proceeds with safest implementation choices

---

## Troubleshooting

### Test Won't Fail First

**Symptom:** Test passes immediately without implementation.

**Cause:** Test is checking wrong behavior or mocking too much.

**Solution:**
- Review test assertions match acceptance criteria
- Reduce mocking to only external dependencies
- Ensure test exercises the actual code path

### Quality Gates Failing

**Symptom:** Implementation works but gates reject it.

**Cause:** Lint errors, type errors, or coverage gaps.

**Solution:**
- Run `npm run lint -- --fix` for auto-fixable issues
- Check TypeScript errors with `npm run typecheck`
- Add tests for uncovered branches

### Task File Format Errors

**Symptom:** Skill can't parse task file.

**Cause:** Malformed .code-task.md structure.

**Solution:**
- Verify required sections: Context, Requirements, Acceptance Criteria
- Check markdown formatting
- Regenerate with sop-task-generator if needed

### Autonomous Mode Stuck

**Symptom:** Skill stops without completing in autonomous mode.

**Cause:** Unhandled blocker or ambiguous requirement.

**Solution:**
- Check `.ralph/blockers.json` for documented issues
- Review `progress.md` for blocker details and deferred decisions
- Re-run in interactive mode to resolve ambiguity

---

## References

| File | Content |
|------|---------|
| [mode-behavior.md](references/mode-behavior.md) | Interactive vs autonomous mode behavior |
| [tdd-workflow.md](references/tdd-workflow.md) | Detailed TDD cycle guidance |
| [examples.md](references/examples.md) | Usage examples |
| [troubleshooting.md](references/troubleshooting.md) | Common issues and solutions |

**Source Materials:**
- strands-agents/agent-sop `sop-code-assist.sop.md`
- ralph-orchestrator `.sops/sop-code-assist.sop.md`
- Test-Driven Development (TDD) methodology
- Conventional Commits specification

---

*Version: 1.1.0 | Created: 2026-01-28 | Updated: 2026-01-30*
*Compliant with strands-agents SOP format (RFC 2119)*
