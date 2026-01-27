---
name: sop-task-generator
description: Generates structured implementation tasks from designs or descriptions
---

# SOP Task Generator

## Table of Contents

- [Overview](#overview)
- [When to Use](#when-to-use)
- [When NOT to Use](#when-not-to-use)
- [Quick Reference](#quick-reference)
- [The Process](#the-process)
- [Key Principles](#key-principles)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [Common Mistakes](#common-mistakes)
- [Notes](#notes)

## Overview

Generate structured code task files from descriptions or PDD (Problem-Driven Development) plans, based on Amazon's code-task-generator SOP.

This skill creates well-formed implementation tasks that can be executed by code-assist or other execution agents, ensuring consistent task structure and complete requirements specification.

## When to Use

- Converting PDD plans into executable tasks
- Breaking down design documents into work items
- Preparing for autonomous execution via ralph-loop
- Creating implementation checklists from descriptions

## When NOT to Use

| Situation | Why Not | Use Instead |
|-----------|---------|-------------|
| No design/plan exists | Need planning first | `sop-planning` |
| Simple single-file change | Overhead exceeds benefit | Direct implementation |
| Exploring/researching | Not for analysis | `sop-reverse` |
| Requirements unclear | Discovery needed | `sop-discovery` |

## Quick Reference

| Parameter | Required | Description |
|-----------|----------|-------------|
| `input` | Yes | Text, file path to design/PDD |
| `output_dir` | No | Task files directory (default: specs/{goal}/implementation) |
| `step_number` | No | Specific PDD step to process |

**Output**: `.code-task.md` files in output_dir

## The Process

### Step 1: Detect Input Mode

**Actions:**
1. Check if input is a file path
2. If file path, read the file content
3. Analyze structure:
   - Has checklist format + numbered steps → **PDD mode**
   - Otherwise → **Description mode**
4. Inform user which mode was detected and what will be generated

**Example output:**
```
Detected: PDD mode
Source: specs/feature-x/plan.md
Found: 5 implementation steps
```

### Step 2: Analyze Input

**For PDD mode:**
- Parse the implementation plan structure
- Extract all numbered steps
- Identify which step to process (from parameter or ask user)
- Read step description and demo requirements
- Extract technical requirements and constraints

**For Description mode:**
- Identify core functionality being described
- Extract explicit requirements
- Identify implicit requirements and constraints
- Determine technical scope

**For both modes:**
- Assess complexity: Low/Medium/High
- Identify required skills/technologies
- Note dependencies on other systems or components

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

**Output:** Structured requirements ready for task generation

### Step 4: Plan Tasks

**CRITICAL:** Do NOT generate files yet. Present plan for approval first.

**Actions:**
1. Determine task breakdown:
   - Simple feature → Single task
   - Complex feature → Multiple tasks with dependencies
   - PDD step → One or more tasks per step

2. Present to user:
   ```
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

3. Wait for user approval
4. If user suggests changes, adjust and re-present
5. Only proceed to Step 5 when user explicitly approves

### Step 5: Generate Tasks

**File Organization:**

**For PDD mode:**
```
{output_dir}/
└── stepNN/
    ├── task-01-{title}.code-task.md
    ├── task-02-{title}.code-task.md
    └── task-03-{title}.code-task.md
```

**For Description mode:**
```
{output_dir}/
├── task-01-{title}.code-task.md
└── task-02-{title}.code-task.md
```

**Task File Format:**

Each task file MUST follow this exact structure:

```markdown
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
```

**Quality Requirements:**
- Description: 2-4 sentences, clear purpose
- Background: Sufficient context, no jargon without explanation
- Technical Requirements: Specific, measurable, testable
- Acceptance Criteria: At least 3 criteria, all in Given-When-Then format
- Include unit test requirements in acceptance criteria
- Dependencies: All external dependencies documented
- Implementation Approach: Guidance without over-prescription

### Step 6: Report Results

**Actions:**
1. List all generated files with absolute paths
2. Show file count and total lines generated
3. Provide next steps

**Report format:**
```
✓ Generated [N] task file(s)

Files created:
- /absolute/path/to/task-01-{title}.code-task.md
- /absolute/path/to/task-02-{title}.code-task.md

Next steps:
1. Review generated tasks for completeness
2. Execute tasks in sequence:
   - Run code-assist on task-01
   - After completion, run code-assist on task-02
   - Continue until all tasks complete

[For PDD mode only:]
Step demo requirements:
- [Demo requirement 1 from PDD]
- [Demo requirement 2 from PDD]
```

## Key Principles

| Principle | Requirements |
|-----------|-------------|
| **Task Quality** | Completable in one session, clear success criteria, explicit dependencies |
| **User Collaboration** | Get approval before generating, present breakdown clearly, allow iteration |
| **Consistency** | Follow code task format exactly, Given-When-Then criteria, reference designs |
| **Execution Readiness** | Self-contained tasks, all context included, verifiable acceptance criteria |

## Examples

### Example 1: PDD Mode

**Input:**
```
input: specs/auth-feature/plan.md
step_number: 3
```

**Detected:** PDD mode, Step 3 of 5

**Generated:**
```
specs/auth-feature/implementation/step03/
└── task-01-implement-jwt-validation.code-task.md
```

### Example 2: Description Mode

**Input:**
```
input: "Add user profile editing with validation and profile picture upload"
output_dir: specs/user-profile/tasks
```

**Detected:** Description mode, complex feature

**Generated:**
```
specs/user-profile/tasks/
├── task-01-profile-data-validation.code-task.md
├── task-02-profile-update-api.code-task.md
└── task-03-profile-picture-upload.code-task.md
```

## Error Handling

**Invalid Input:**
- If input file doesn't exist, inform user and ask for correct path
- If input is neither valid file nor clear description, ask for clarification

**Missing Dependencies:**
- If referenced design document doesn't exist, warn user but continue
- Mark as "TODO: Create design document" in task

**Complexity Issues:**
- If single step requires >5 tasks, warn user and suggest breaking into sub-steps
- If task complexity is High, note that it may need further decomposition

## Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Generating >5 tasks per step | Tasks too complex | Decompose further |
| Vague acceptance criteria | Unclear completion | Use Given-When-Then format |
| Missing dependencies | Blocked execution | Document all dependencies |
| No design reference | Implementation drift | Always reference design doc |

## Notes

- This skill creates task specifications, not implementations
- Tasks are meant to be executed by code-assist or similar agents
- Always validate with user before creating files
- Tasks should be implementation-agnostic where possible
- Focus on "what" and "why", not "how" (except in Implementation Approach as guidance)
