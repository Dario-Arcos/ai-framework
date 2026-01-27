---
name: sop-reverse
description: Use when investigating existing artifacts (codebase, API, documentation, process, concept) to generate specs for future development
---

# SOP Reverse Engineering

## Table of Contents

- [Overview](#overview)
- [When to Use](#when-to-use)
- [When NOT to Use](#when-not-to-use)
- [Quick Reference](#quick-reference)
- [The Investigation Process](#the-investigation-process)
- [Output Structure](#output-structure)
- [Key Principles](#key-principles)
- [References](#references)

## Overview

Systematically investigate existing artifacts and generate structured specifications from them. This is the "reverse" flow: understanding what exists and documenting it for future development.

**Critical**: This is NOT just for code. It works with ANY artifact: codebases, APIs, documentation, processes, or abstract concepts.

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

## Quick Reference

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `target` | Yes | - | Path, URL, or description of artifact to investigate |
| `target_type` | No | Auto-detect | `codebase`, `api`, `documentation`, `process`, `concept` |
| `output_dir` | No | `specs/{name}-{timestamp}` | Where to store investigation output |
| `focus_areas` | No | - | Specific aspects to prioritize (e.g., "auth flow", "data model") |

## The Investigation Process

### Step 1: Identify Target Type

Analyze the target to determine type. Present determination with evidence. **MUST confirm type with user before proceeding** - ask one yes/no question and wait for explicit confirmation.

See [references/artifact-types.md](references/artifact-types.md) for type detection criteria.

### Step 2: Initial Batch Analysis

Perform comprehensive first-pass analysis without user interaction. Cover all relevant aspects for the artifact type. Create `investigation.md` with executive summary, detailed findings, observations, and questions.

**Key Constraint**: Complete entire analysis BEFORE asking user questions.

See [references/artifact-types.md](references/artifact-types.md) for analysis checklist by type.

### Step 3: Interactive Refinement

Present findings summary, then ask **ONE clarifying question at a time**. Wait for response before next question. Incorporate responses into investigation.md. Continue until user confirms "ready to generate specs."

See [references/investigation-patterns.md](references/investigation-patterns.md) for question guidelines.

### Step 4: Generate Specs

Create structured specifications in `specs-generated/` directory. Use appropriate spec structure for artifact type. Include mermaid diagrams for flows and relationships.

**Key Constraint**: Specs MUST be compatible with sop-planning for forward flow.

See [references/artifact-types.md](references/artifact-types.md) for spec templates by type.

### Step 5: Recommendations

Generate `recommendations.md` with improvements, risks, migration paths, and prioritized next steps. Present final summary and ask if user wants to continue to sop-planning (forward flow).

**Key Constraint**: Never auto-invoke sop-planning - always ask user.

See [references/output-structure.md](references/output-structure.md) for template.

## Output Structure

```
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

## Integration with Forward Flow

After investigation completes, specs in `specs-generated/` feed into sop-planning:

```
sop-reverse -> sop-planning -> sop-task-generator -> ralph-loop
```

This creates a complete loop: understand what exists, plan improvements, generate tasks, execute.

## References

- [references/artifact-types.md](references/artifact-types.md) - Analysis checklists and spec templates per type
- [references/output-structure.md](references/output-structure.md) - Directory structure and file templates
- [references/mermaid-examples.md](references/mermaid-examples.md) - Diagram types and examples
- [references/investigation-patterns.md](references/investigation-patterns.md) - Questions, errors, quality gates

---

*Part of the SOP framework: sop-reverse -> sop-planning -> sop-task-generator -> ralph-loop*
