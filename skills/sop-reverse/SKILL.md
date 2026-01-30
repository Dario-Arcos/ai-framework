---
name: sop-reverse
description: Use when inheriting undocumented systems, integrating with third-party APIs, or preparing legacy systems for migration. Investigates existing artifacts and generates structured specifications.
---

# SOP Reverse Engineering

## Overview

Systematically investigate existing artifacts and generate structured specifications from them. This is the "reverse" flow: understanding what exists and documenting it for future development.

**Note**: This is NOT just for code. It works with ANY artifact: codebases, APIs, documentation, processes, or abstract concepts.

## When to Use

- Inheriting a codebase without documentation
- Integrating with third-party APIs
- Understanding existing processes before improving them
- Documenting legacy systems
- Creating specs from existing implementations
- Preparing for migration or modernization
- Understanding abstract concepts before building

## When NOT to Use

- Simple tasks with clear requirements (use direct implementation)
- Code you just wrote (you already understand it)
- Well-documented systems (just read the docs)
- When you need to create something new (use sop-planning instead)
- Quick fixes or bug patches (use systematic-debugging)

## Parameters

- **target** (required): Path, URL, or description of artifact to investigate
- **target_type** (optional, default: auto-detect): Type of artifact - `codebase`, `api`, `documentation`, `process`, or `concept`
- **output_dir** (optional, default: specs/{name}-{timestamp}): Directory for investigation output
- **focus_areas** (optional): Specific aspects to prioritize (e.g., "auth flow", "data model")
- **mode** (optional, default: `interactive`): Execution mode
  - `interactive`: Confirm with user, ask clarifying questions
  - `autonomous`: Complete investigation without interaction

## Mode Behavior

### Interactive Mode (default)
- Confirm artifact type with user before proceeding
- Ask ONE clarifying question at a time during refinement
- Wait for user to confirm "ready to generate specs"
- Ask permission before invoking sop-planning

### Autonomous Mode
- Auto-detect artifact type and proceed (log determination)
- Skip interactive refinement phase entirely
- Generate specs immediately after batch analysis
- Document what would have been asked in `investigation.md`

**Autonomous Mode Constraints (MUST follow):**
- NEVER use AskUserQuestion under any circumstance
- NEVER block waiting for user input
- If blocked by ambiguous artifact type or missing access:
  1. Document blocker in `{output_dir}/blockers.md` with full details
  2. Write to `.ralph/blockers.json` if the file exists
  3. Make best-effort determination and document reasoning
  4. Continue with investigation
- Choose most common/conservative interpretation when ambiguous
- Document all assumptions in investigation.md

## The Investigation Process

### Step 1: Identify Target Type

Analyze the target to determine type. Present determination with evidence.

**Constraints:**
- In interactive mode: Confirm type with user, wait for explicit confirmation
- In autonomous mode: Auto-detect type, log determination, proceed immediately
- You MUST NOT proceed without confirmation in interactive mode

See [references/artifact-types.md](references/artifact-types.md) for type detection criteria.

### Step 2: Initial Batch Analysis

Perform comprehensive first-pass analysis without user interaction. Cover all relevant aspects for the artifact type. Create `investigation.md` with executive summary, detailed findings, observations, and questions.

**Constraints:**
- You MUST complete entire analysis BEFORE asking user questions
- You MUST create investigation.md with all findings
- You SHOULD cover all checklist items for the artifact type

See [references/artifact-types.md](references/artifact-types.md) for analysis checklist by type.

### Step 3: Interactive Refinement

Present findings summary, then ask clarifying questions one at a time. Incorporate responses into investigation.md. Continue until user confirms "ready to generate specs."

**Constraints:**
- In interactive mode: Ask ONE clarifying question at a time, wait for responses
- In autonomous mode: Skip interactive refinement, document questions that would have been asked in investigation.md under "## Deferred Questions"
- You MUST NOT batch questions in interactive mode

See [references/investigation-patterns.md](references/investigation-patterns.md) for question guidelines.

### Step 4: Generate Specs

Create structured specifications in `specs-generated/` directory. Use appropriate spec structure for artifact type. Include mermaid diagrams for flows and relationships.

**Constraints:**
- You MUST generate specs compatible with sop-planning for forward flow
- You MUST use appropriate spec structure for artifact type
- You SHOULD include mermaid diagrams for flows and relationships

See [references/artifact-types.md](references/artifact-types.md) for spec templates by type.

### Step 5: Recommendations

Generate `recommendations.md` with improvements, risks, migration paths, and prioritized next steps. Present final summary and ask if user wants to continue to sop-planning (forward flow).

**Constraints:**
- In interactive mode: Ask user if they want to continue to sop-planning
- In autonomous mode: Do NOT auto-invoke sop-planning, just document recommendation
- You MUST NOT auto-invoke sop-planning without user permission in interactive mode

See [references/output-structure.md](references/output-structure.md) for template.

## Output Structure

```text
{output_dir}/
├── investigation.md          # Raw findings and analysis
├── specs-generated/          # Structured specs by type
├── recommendations.md        # Improvement suggestions
├── summary.md                # Overview and next steps
└── artifacts/                # Supporting materials
```

See [references/output-structure.md](references/output-structure.md) for complete structure and templates.

## Key Principles

| Principle | Requirement |
|-----------|-------------|
| Universal Support | Support ALL artifact types equally - never assume code only |
| Batch Then Refine | Complete batch analysis BEFORE asking questions |
| One Question Rule | Present findings and ask ONE question at a time |
| Spec Compatibility | Generate specs compatible with sop-planning |
| User Control | Confirm type, confirm refinement complete, confirm forward flow |
| Transparency | Show evidence, list what was analyzed, acknowledge limitations |

## Troubleshooting

### Problem: Cannot determine artifact type
**Cause**: Mixed artifact (e.g., API docs with embedded code examples)
**Solution**: Ask user to clarify primary intent. Default to most relevant type.

### Problem: Investigation produces shallow findings
**Cause**: Batch analysis missed critical details
**Solution**: Re-run with specific focus_areas parameter. Ask user what aspects are most important.

### Problem: Generated specs don't match user expectations
**Cause**: Interactive refinement skipped or cut short
**Solution**: Return to Step 3. Ask more targeted questions about specific findings.

## Integration with Forward Flow

After investigation completes, specs in `specs-generated/` feed into sop-planning:

```text
sop-reverse -> sop-planning -> sop-task-generator -> ralph-orchestrator
```

This creates a complete loop: understand what exists, plan improvements, generate tasks, execute.

## References

- [references/artifact-types.md](references/artifact-types.md) - Analysis checklists and spec templates per type
- [references/output-structure.md](references/output-structure.md) - Directory structure and file templates
- [references/mermaid-examples.md](references/mermaid-examples.md) - Diagram types and examples
- [references/investigation-patterns.md](references/investigation-patterns.md) - Questions, errors, quality gates

---

*Part of the SOP framework: sop-reverse -> sop-planning -> sop-task-generator -> ralph-orchestrator*
