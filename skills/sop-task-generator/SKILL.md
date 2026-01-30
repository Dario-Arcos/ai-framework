---
name: sop-task-generator
description: Use when converting designs, PDD plans, or descriptions into structured .code-task.md files for autonomous execution by ralph-orchestrator or sop-code-assist.
---

# SOP Task Generator

## Overview

Generate structured code task files from descriptions or PDD (Problem-Driven Development) plans, based on Amazon's code-task-generator SOP.

This skill creates well-formed implementation tasks that can be executed by sop-code-assist or other execution agents, ensuring consistent task structure and complete requirements specification.

## When to Use

- Converting PDD plans into executable tasks
- Breaking down design documents into work items
- Preparing for autonomous execution via ralph-orchestrator
- Creating implementation checklists from descriptions

## When NOT to Use

| Situation | Why Not | Use Instead |
|-----------|---------|-------------|
| No design/plan exists | Need planning first | `sop-planning` |
| Simple single-file change | Overhead exceeds benefit | Direct implementation |
| Exploring/researching | Not for analysis | `sop-reverse` |
| Requirements unclear | Discovery needed | `sop-discovery` |

## Parameters

- **input** (required): Text description or file path to design/PDD document
- **output_dir** (optional, default: specs/{goal}/implementation): Directory for task files
- **step_number** (deprecated): In PDD mode, ALL steps are processed automatically. This parameter is only used for edge cases requiring single-step regeneration.
- **mode** (optional, default: `interactive`): Execution mode
  - `interactive`: Ask user questions, wait for approvals
  - `autonomous`: Generate tasks without interaction, document decisions

## Mode Behavior

### Interactive Mode (default)
- Inform user of detected mode and wait for acknowledgment
- Present task breakdown for user review
- Wait for explicit approval before generating files
- Allow iteration based on user feedback

### Autonomous Mode
- Log detected mode but proceed without waiting
- Generate task breakdown based on best judgment
- Create all task files without approval prompts
- Document all decisions in generated files

**Autonomous Mode Constraints (MUST follow):**
- NEVER use AskUserQuestion under any circumstance
- NEVER block waiting for user input
- If blocked by missing information or ambiguity:
  1. Document blocker in output_dir/blockers.md with full details
  2. Make reasonable assumption and document it in task file
  3. Continue generating remaining tasks
- Choose safest/simplest approach when ambiguous
- Add "[AUTO-GENERATED]" note to task metadata when in autonomous mode

## Output

`.code-task.md` files in output_dir

## The Process

### Step 1: Detect Input Mode

**Actions:**
1. Check if input is a file path
2. If file path, read the file content
3. Analyze structure:
   - Has checklist format + numbered steps → **PDD mode**
   - Otherwise → **Description mode**
4. Inform user which mode was detected and what will be generated

**Constraints:**
- In interactive mode: Inform user of detected mode, wait for acknowledgment
- In autonomous mode: Log detected mode, proceed immediately
- You MUST NOT proceed without acknowledgment in interactive mode because proceeding without user awareness may generate tasks for incorrect input interpretation

**Example output:**
```text
Detected: PDD mode
Source: specs/feature-x/plan.md
Found: 5 implementation steps
Action: Will generate 5 task files (one per step)
```

### Step 2: Analyze Input

**For PDD mode:**
- Parse the implementation plan structure
- Extract ALL numbered steps from the plan
- Count total steps (N) to determine scope
- For EACH step: read description, demo requirements, and constraints
- Build complete dependency graph across all steps
- Extract technical requirements for every step

**CRITICAL: You MUST process ALL steps, not just one.**

**For Description mode:**
- Identify core functionality being described
- Extract explicit requirements
- Identify implicit requirements and constraints
- Determine technical scope

**For both modes:**
- Assess complexity: Low/Medium/High
- Identify required skills/technologies
- Note dependencies on other systems or components

**Constraints:**
- You MUST identify all functional requirements
- You MUST assess complexity before proceeding
- You SHOULD note any ambiguities for clarification

### Step 3: Structure Requirements

**For PDD mode:**
- Extract step title and number
- Pull step description
- Identify demo requirements for the step
- Convert into functional requirements
- Create measurable acceptance criteria (Given-When-Then format)

**For Description mode:**
- Identify functional requirements from description
- Extract non-functional requirements (performance, security, etc.)
- Create measurable acceptance criteria (Given-When-Then format)
- Ensure all "what" is captured, not "how"

**Constraints:**
- You MUST use Given-When-Then format for acceptance criteria
- You MUST NOT include implementation details in requirements because requirements should specify "what" not "how" to allow implementation flexibility

**Output:** Structured requirements ready for task generation

### Step 4: Plan Tasks

**Actions:**
1. Determine task breakdown:
   - Simple feature → Single task
   - Complex feature → Multiple tasks with dependencies
   - PDD step → One or more tasks per step

2. Present to user:
   ```text
   Proposed task breakdown for [Step X / Feature Y]:

   Task 1: [Title]
   - [Brief description]
   - Complexity: [Low/Medium/High]

   Task 2: [Title]
   - [Brief description]
   - Depends on: Task 1
   - Complexity: [Low/Medium/High]

   Files to create:
   - specs/{goal}/implementation/stepNN/task-01-{title}.code-task.md
   - specs/{goal}/implementation/stepNN/task-02-{title}.code-task.md

   Approve task breakdown? (yes/no)
   ```

3. Wait for user approval (interactive mode only)
4. If user suggests changes, adjust and re-present (interactive mode only)
5. Only proceed to Step 5 when user explicitly approves (interactive mode) or immediately (autonomous mode)

**Constraints:**
- In interactive mode: Present breakdown, wait for explicit approval
- In autonomous mode: Log breakdown, proceed to generation immediately
- You MUST NOT generate files before user approval in interactive mode because generating unapproved files creates artifacts that may need deletion or cause confusion

### Task File Generation Requirements (PDD Mode)

**You MUST generate a task file for EVERY step in the plan:**

1. Read `specs/{feature}/implementation/plan.md`
2. Count total steps (N)
3. For EACH step, create:
   - Directory: `specs/{feature}/implementation/step{NN}/`
   - File: `task-{NN}-{description}.code-task.md`
4. Verify: N task files created = N steps in plan

**Generation Flow:**
```text
Plan has 5 steps → Generate 5 task files (step01, step02, step03, step04, step05)
Plan has 3 steps → Generate 3 task files (step01, step02, step03)
```

**Validation Checklist:**
- [ ] All steps from plan have corresponding task files
- [ ] Each task file has complete acceptance criteria
- [ ] Dependencies between tasks are documented
- [ ] No orphan steps without task files
- [ ] Task numbering matches step numbering

**You MUST NOT:**
- Create only the first task and leave others for later because incomplete task generation leaves orchestrator without full execution scope
- Generate tasks ad-hoc during execution because ad-hoc generation causes inconsistent scope and missed dependencies
- Skip steps that seem "simple" because simplicity is subjective and skipped steps create gaps in the execution sequence
- Ask which step to process (process ALL of them) because selective processing defeats the purpose of complete upfront task generation

### Step 5: Generate Tasks

**File Organization:**

**For PDD mode:**
```text
{output_dir}/
└── stepNN/
    ├── task-01-{title}.code-task.md
    ├── task-02-{title}.code-task.md
    └── task-03-{title}.code-task.md
```

**For Description mode:**
```text
{output_dir}/
├── task-01-{title}.code-task.md
└── task-02-{title}.code-task.md
```

**Task File Format:**

Each task file MUST follow this exact structure:

```markdown
## Status: PENDING
## Completed: [DATE when done]

# Task: [Task Name]

## Description
[What needs to be implemented and why. Should be clear enough that someone unfamiliar with the project can understand the goal.]

## Background
[Context needed to understand the task. Include relevant architectural decisions, existing patterns to follow, or constraints from the larger system.]

## Reference Documentation
**Required:**
- Design: [path to detailed design document]

**Additional References:**
- [Path to relevant research docs]
- [Path to related implementation plans]
- [Links to external documentation]

**Note:** You MUST read the detailed design before implementing.

## Technical Requirements

1. [Specific technical requirement with measurable criteria]
2. [Another requirement]
3. [Requirements should be testable]

## Dependencies

- **[Dependency name]**: [Why it's needed and how to verify it's met]
- **[Another dependency]**: [Details]

## Implementation Approach

1. [High-level step - what to do, not exact code]
2. [Another step]
3. [Steps should guide but not prescribe exact implementation]

**Note:** This is suggested approach. Alternative solutions are acceptable if they meet requirements.

## Acceptance Criteria

1. **[Criterion Name]**
   - Given [precondition or initial state]
   - When [action or trigger]
   - Then [expected observable result]

2. **[Unit Tests]**
   - Given [test setup]
   - When [test execution]
   - Then [test passes with expected assertions]

3. **[Integration/E2E Criterion]**
   - Given [system state]
   - When [user action or system event]
   - Then [end-to-end expected result]

## Metadata
- **Complexity**: [Low/Medium/High]
- **Estimated Effort**: [S/M/L/XL based on CLAUDE.md budget table]
- **Labels**: [comma, separated, tags]
- **Required Skills**: [Skills or expertise needed]
- **Related Tasks**: [Links to dependent or related tasks]
- **Step**: [NN of total] (e.g., "03 of 05")
```

**Status Field Values:**
- `PENDING` - Initial state, not yet started
- `IN_PROGRESS` - Currently being executed
- `COMPLETED` - Successfully finished (update Completed date)
- `BLOCKED` - Waiting on dependencies

**Quality Requirements:**
- Status: Always starts as `PENDING`
- Completed: Empty on creation, filled when done
- Description: 2-4 sentences, clear purpose
- Background: Sufficient context, no jargon without explanation
- Technical Requirements: Specific, measurable, testable
- Acceptance Criteria: At least 3 criteria, all in Given-When-Then format
- Include unit test requirements in acceptance criteria
- Dependencies: All external dependencies documented, including previous steps
- Implementation Approach: Guidance without over-prescription
- Metadata Step: Must include position (e.g., "03 of 05")

**Constraints:**
- You MUST follow the exact task file format
- You MUST include all required sections (Description, Background, Reference Documentation, etc.)
- You MUST NOT place tasks in wrong directory structure because incorrect placement breaks orchestrator discovery and task sequencing

### Step 6: Report Results

**Actions:**
1. List all generated files with absolute paths
2. Show file count and total lines generated
3. Provide next steps

**Constraints:**
- You MUST list all generated files with absolute paths
- You MUST provide clear next steps

**Report format:**
```text
✓ Generated [N] task file(s) for [N] steps

Validation:
- Steps in plan: [N]
- Task files created: [N]
- Status: ✓ All steps covered

Files created:
- /absolute/path/to/step01/task-01-{title}.code-task.md
- /absolute/path/to/step02/task-02-{title}.code-task.md
- /absolute/path/to/step03/task-03-{title}.code-task.md
- ...

Next steps:
1. Review generated tasks for completeness
2. Execute tasks in sequence:
   - Run sop-code-assist on step01/task-01
   - After completion, run sop-code-assist on step02/task-02
   - Continue until all tasks complete
3. Update Status field as tasks progress

[For PDD mode only:]
Demo requirements by step:
- Step 01: [Demo requirement]
- Step 02: [Demo requirement]
- ...
```

## Key Principles

| Principle | Requirements |
|-----------|-------------|
| **Task Quality** | Completable in one session, clear success criteria, explicit dependencies |
| **User Collaboration** | Interactive: Get approval before generating, present breakdown clearly, allow iteration. Autonomous: Document decisions, proceed without approval |
| **Consistency** | Follow code task format exactly, Given-When-Then criteria, reference designs |
| **Execution Readiness** | Self-contained tasks, all context included, verifiable acceptance criteria |

## Examples

### Example 1: PDD Mode (All Steps)

**Input:**
```text
input: specs/auth-feature/plan.md
```

**Detected:** PDD mode, 5 total steps

**Generated (ALL steps upfront):**
```text
specs/auth-feature/implementation/
├── step01/
│   └── task-01-setup-auth-infrastructure.code-task.md
├── step02/
│   └── task-02-implement-user-model.code-task.md
├── step03/
│   └── task-03-implement-jwt-validation.code-task.md
├── step04/
│   └── task-04-create-login-endpoint.code-task.md
└── step05/
    └── task-05-add-session-management.code-task.md
```

**Verification:** 5 steps in plan → 5 task files created ✓

### Example 2: Description Mode

**Input:**
```text
input: "Add user profile editing with validation and profile picture upload"
output_dir: specs/user-profile/tasks
```

**Detected:** Description mode, complex feature

**Generated:**
```text
specs/user-profile/tasks/
├── task-01-profile-data-validation.code-task.md
├── task-02-profile-update-api.code-task.md
└── task-03-profile-picture-upload.code-task.md
```

## Error Handling

**Invalid Input:**
- Interactive mode: If input file doesn't exist, inform user and ask for correct path
- Autonomous mode: If input file doesn't exist, document blocker and abort with error
- Interactive mode: If input is neither valid file nor clear description, ask for clarification
- Autonomous mode: If input is ambiguous, make reasonable assumption and document in blockers.md

**Missing Dependencies:**
- If referenced design document doesn't exist, warn user (interactive) or log (autonomous) but continue
- Mark as "TODO: Create design document" in task

**Complexity Issues:**
- Interactive mode: If single step requires >5 tasks, warn user and suggest breaking into sub-steps
- Autonomous mode: If single step requires >5 tasks, proceed with best judgment and document in task metadata
- If task complexity is High, note that it may need further decomposition

## Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Creating only first task file | Incomplete task set, manual generation later | Generate ALL task files upfront |
| Generating tasks ad-hoc during execution | Inconsistent scope, missed steps | Process entire plan in one pass |
| Generating >5 tasks per step | Tasks too complex | Decompose further |
| Vague acceptance criteria | Unclear completion | Use Given-When-Then format |
| Missing dependencies | Blocked execution | Document all dependencies |
| No design reference | Implementation drift | Always reference design doc |
| Missing Status field | No progress tracking | Always include Status: PENDING |

## Troubleshooting

### Problem: Generated tasks are too large
**Cause**: Step complexity underestimated during planning
**Solution**: Decompose into sub-tasks. Each task should be completable in one session (<2 hours).

### Problem: Tasks have unclear acceptance criteria
**Cause**: Requirements missing specific success conditions
**Solution**: Add Given-When-Then format. Each criterion must be testable.

### Problem: Task dependencies create circular blocks
**Cause**: Poor task ordering or shared state assumptions
**Solution**: Reorder tasks to build foundation first. Extract shared code into earlier task.

## Notes

- This skill creates task specifications, not implementations
- Tasks are meant to be executed by sop-code-assist or similar agents
- In interactive mode: Always validate with user before creating files
- In autonomous mode: Document all decisions, proceed without validation
- Tasks should be implementation-agnostic where possible
- Focus on "what" and "why", not "how" (except in Implementation Approach as guidance)
