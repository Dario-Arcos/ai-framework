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
- **focus_areas** (optional, default: none - investigates all aspects if not specified): Specific aspects to prioritize (e.g., "auth flow", "data model")
- **mode** (optional, default: `interactive`): Execution mode
  - `interactive`: Confirm with user, ask clarifying questions
  - `autonomous`: Complete investigation without interaction

**Constraints for parameter acquisition:**
- You MUST validate that target path exists or URL is accessible because invalid targets waste investigation time
- You MUST auto-detect target_type if not specified because manual specification is error-prone
- You SHOULD confirm target type with user in interactive mode because auto-detection may be wrong
- You MUST create output_dir if it doesn't exist because missing directories cause silent failures

## Mode Behavior

### Interactive Mode (default)
- You MUST confirm artifact type with user before proceeding because incorrect type wastes entire investigation
- You MUST ask ONE clarifying question at a time during refinement because batched questions reduce response quality
- You MUST wait for user to confirm "ready to generate specs" because premature generation produces incomplete specs
- You MUST ask permission before invoking sop-planning because unexpected tool invocation disrupts user workflow

### Autonomous Mode
- You MUST auto-detect artifact type and proceed because blocking defeats autonomous purpose
- You MUST log type determination because traceability enables debugging
- You MUST skip interactive refinement phase entirely because user interaction is unavailable
- You MUST generate specs immediately after batch analysis because autonomous mode should complete without delay
- You MUST document what would have been asked in `investigation.md` because deferred questions enable future follow-up

**Autonomous Mode Constraints (MUST follow):**
- NEVER use AskUserQuestion under any circumstance
- NEVER block waiting for user input
- If blocked by ambiguous artifact type or missing access:
  1. Document blocker in `{output_dir}/blockers.md` with full details
  2. Make best-effort determination and document reasoning
  3. Continue with investigation
- Choose most common/conservative interpretation when ambiguous
- Document all assumptions in investigation.md

## The Investigation Process

### Step 1: Identify Target Type

You MUST analyze the target to determine its type because misclassification leads to irrelevant analysis. You MUST present determination with evidence because unsubstantiated claims erode user trust.

**Constraints:**
- You MUST confirm type with user in interactive mode because auto-detection may misclassify hybrid artifacts
- You MUST wait for explicit confirmation before proceeding in interactive mode because implicit assumption causes wasted work
- You MUST auto-detect type and log determination in autonomous mode because blocking on user input defeats autonomous purpose
- You MUST NOT proceed without confirmation in interactive mode because proceeding with wrong type wastes entire investigation
- You SHOULD present multiple candidate types when confidence is low because transparency enables better user decisions

See [references/artifact-types.md](references/artifact-types.md) for type detection criteria.

### Step 2: Initial Batch Analysis

You MUST perform comprehensive first-pass analysis without user interaction because fragmented analysis leads to incomplete understanding. You MUST cover all relevant aspects for the artifact type because partial coverage misses critical dependencies. You MUST create `investigation.md` with executive summary, detailed findings, observations, and questions because structured documentation enables effective refinement.

**Constraints:**
- You MUST complete entire analysis BEFORE asking user questions because premature questions reveal incomplete understanding
- You MUST create investigation.md with all findings because undocumented findings are lost and unrepeatable
- You MUST document artifact boundaries and scope because undefined scope leads to scope creep
- You SHOULD cover all checklist items for the artifact type because checklists ensure comprehensive coverage
- You SHOULD identify dependencies and integrations because isolated analysis misses system interactions
- You MAY skip checklist items with explicit justification when irrelevant to target

See [references/artifact-types.md](references/artifact-types.md) for analysis checklist by type.

### Step 3: Interactive Refinement

You MUST present findings summary before asking questions because context enables better user responses. You MUST ask clarifying questions one at a time because batched questions overwhelm users and reduce response quality. You MUST incorporate responses into investigation.md because untracked responses get lost. You MUST continue until user confirms "ready to generate specs" because premature spec generation produces incomplete outputs.

**Constraints:**
- You MUST ask ONE clarifying question at a time in interactive mode because focused questions yield precise answers
- You MUST wait for user response before asking next question because rapid-fire questions frustrate users
- You MUST skip interactive refinement in autonomous mode because user interaction defeats autonomous purpose
- You MUST document deferred questions under "## Deferred Questions" in autonomous mode because capturing questions enables future follow-up
- You MUST NOT batch questions in interactive mode because users cannot effectively answer multiple questions at once
- You SHOULD prioritize questions by impact on spec quality because limited user patience should be spent on high-value questions

See [references/investigation-patterns.md](references/investigation-patterns.md) for question guidelines.

### Step 4: Generate Specs

You MUST create structured specifications in `specs-generated/` directory because consistent output location enables automation. You MUST use appropriate spec structure for artifact type because mismatched structure confuses downstream consumers. You SHOULD include mermaid diagrams for flows and relationships because visual representation accelerates comprehension.

**Constraints:**
- You MUST generate specs compatible with sop-planning for forward flow because incompatible specs break the SOP pipeline
- You MUST use appropriate spec structure for artifact type because generic structures miss type-specific details
- You MUST include source references in specs because traceability enables verification
- You SHOULD include mermaid diagrams for flows and relationships because diagrams communicate structure faster than text
- You MAY generate additional artifact-specific outputs when they add value

See [references/artifact-types.md](references/artifact-types.md) for spec templates by type.

### Step 5: Recommendations

You MUST generate `recommendations.md` with improvements, risks, migration paths, and prioritized next steps because investigation without recommendations wastes analysis effort. You MUST present final summary because users need executive overview before deciding next steps. You SHOULD ask if user wants to continue to sop-planning in interactive mode because forward flow enables immediate action.

**Constraints:**
- You MUST ask user if they want to continue to sop-planning in interactive mode because auto-invocation removes user agency
- You MUST NOT auto-invoke sop-planning in autonomous mode because autonomous investigation should complete without spawning new processes
- You MUST NOT auto-invoke sop-planning without user permission in interactive mode because unexpected tool invocation breaks user workflow
- You MUST prioritize recommendations by ROI because limited resources should focus on highest-impact improvements
- You SHOULD include effort estimates for recommendations because estimates enable prioritization decisions

See [references/output-structure.md](references/output-structure.md) for template.

**Handoff to sop-planning:**

The `specs-generated/` output is designed to feed into sop-planning as the `rough_idea` parameter:
- Use `specs-generated/` directory contents as `rough_idea` input to sop-planning
- Alternatively, `investigation.md` serves as a discovery.md equivalent and can be passed as `discovery_path`
- Example: `/sop-planning rough_idea="./specs-generated/" discovery_path="./investigation.md"`

This enables the complete reverse-to-forward flow: investigate existing artifacts, then plan improvements based on documented findings.

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

## Examples

### Example 1: Codebase Investigation
```text
/sop-reverse target="./legacy-api" focus_areas="authentication,database"
```
Output: `investigation.md` with architecture analysis, `specs-generated/` with reconstructed specs

### Example 2: API Documentation
```text
/sop-reverse target="https://api.example.com/docs" target_type="api"
```
Output: OpenAPI-style specification, endpoint catalog, auth patterns

### Example 3: Process Documentation
```text
/sop-reverse target="onboarding process" target_type="process" mode="interactive"
```
Output: Process flow diagrams, role responsibilities, bottleneck analysis

### Example 4: Autonomous Legacy System Analysis
```text
/sop-reverse target="./monolith-app" mode="autonomous" output_dir="specs/monolith-audit"
```
Output: Complete investigation without user interaction, deferred questions documented

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
