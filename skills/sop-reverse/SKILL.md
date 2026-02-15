---
name: sop-reverse
description: Use when finding world-class referents before building something new, inheriting undocumented systems, integrating with third-party APIs, or preparing legacy systems for migration. Discovers exemplar implementations AND investigates existing artifacts to generate structured specifications.
---

# SOP Referent Discovery & Reverse Engineering

## Overview

Two complementary capabilities in one skill:

1. **Referent Discovery**: Before building something new, find world-class implementations, extract their patterns, and build on proven foundations.
2. **Reverse Engineering**: Systematically investigate existing artifacts and generate structured specifications from them. Understanding what exists and documenting it for future development.

**Note**: This is NOT just for code. It works with ANY artifact: codebases, APIs, documentation, processes, or abstract concepts.

## When to Use

### Referent Discovery (pre-build)
- Finding world-class referents before building something new
- Analyzing state-of-the-art implementations as inspiration for new work
- Discovering patterns from exemplar codebases/projects before design phase
- Benchmarking against best-in-class solutions in a domain

### Reverse Engineering (investigate existing)
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
- Quick fixes or bug patches (use systematic-debugging)

## Parameters

- **target** (required): Path, URL, concept name, or description of artifact to investigate. For referent discovery, this can be a concept or domain (e.g., "real-time collaboration", "event sourcing frameworks")
- **target_type** (optional, default: auto-detect): Type of artifact - `codebase`, `api`, `documentation`, `process`, or `concept`
- **search_mode** (optional, default: `reverse`): Determines the skill's primary objective
  - `reverse`: Classic reverse engineering — investigate a specific existing artifact
  - `referent`: Referent discovery — search for world-class implementations of a concept, analyze their patterns, and catalog lessons for new design
- **output_dir** (optional, default: .ralph/specs/{name}-{timestamp}): Directory for investigation output
- **focus_areas** (optional, default: none - investigates all aspects if not specified): Specific aspects to prioritize (e.g., "auth flow", "data model")
- **mode** (optional, default: `interactive`): Execution mode
  - `interactive`: Confirm with user, ask clarifying questions
  - `autonomous`: Complete investigation without interaction

**{name} derivation:** When `output_dir` is not provided, `{name}` is derived from `target` using the same kebab-case slugification as ralph-orchestrator's `{goal}`. When invoked by ralph-orchestrator, `output_dir` is always provided explicitly.

**Constraints for parameter acquisition:**
- You MUST validate that target path exists or URL is accessible
- You MUST auto-detect target_type if not specified
- You SHOULD confirm target type with user in interactive mode
- You MUST create output_dir if it doesn't exist

## Mode Behavior

### Interactive Mode (default)
- You MUST confirm artifact type with user before proceeding
- You MUST ask ONE clarifying question at a time during refinement
- You MUST wait for user to confirm "ready to generate specs"
- You MUST ask permission before invoking sop-planning

### Autonomous Mode
- You MUST auto-detect artifact type and proceed
- You MUST log type determination
- You MUST skip interactive refinement phase entirely
- You MUST generate specs immediately after batch analysis
- You MUST document what would have been asked in `investigation.md`

**Autonomous Mode Constraints (MUST follow):** See [autonomous-mode-constraint.md](../ralph-orchestrator/references/autonomous-mode-constraint.md) for the full constraint set. Additional: document all assumptions in `investigation.md`.

## The Referent Discovery Process (search_mode=referent)

When `search_mode=referent`, the skill searches for world-class implementations of a concept rather than analyzing a single artifact.

### Step R1: Define Search Scope

You MUST clarify what concept, domain, or capability the user wants referents for. You MUST identify 3-5 candidate referent projects/implementations.

**Sources for referent identification:**
- User-provided URLs or project names
- Context7 documentation for framework-specific patterns
- agent-browser for current state-of-the-art implementations
- Known exemplar projects in the domain

### Step R2: Analyze Each Referent

For each identified referent, you MUST produce a structured analysis:

- **Architecture patterns**: How is the system structured?
- **Key design decisions**: What tradeoffs were made and why?
- **Testing approach**: How is the system tested? What infrastructure supports integration testing (containers, fixtures, real dependencies vs mocks)?
- **Strengths**: What makes this implementation world-class?
- **Weaknesses**: Where does it fall short or over-engineer?
- **Extractable patterns**: What specific patterns can be adopted?

### Step R3: Comparative Synthesis

You MUST produce a comparative analysis across all referents:

- Pattern frequency: Which patterns appear across multiple referents?
- Best-of-breed selection: Which referent excels at which aspect?
- Anti-patterns: What pitfalls do referents reveal?
- Recommended foundation: Which referent (or combination) provides the best starting point?

### Step R4: Generate Referent Catalog

Output the `referents/` directory with structured findings that feed into sop-planning.

### Referent Discovery Output

```text
{output_dir}/
├── referents/                    # Referent discovery catalog
│   ├── catalog.md                # Summary: all referents, scores, recommendation
│   ├── {referent-1}-analysis.md  # Per-referent detailed analysis
│   ├── {referent-2}-analysis.md
│   ├── comparative-analysis.md   # Cross-referent pattern comparison
│   └── extracted-patterns.md     # Patterns ready to adopt in new design
├── investigation.md              # Search process and methodology
├── recommendations.md            # Which patterns to adopt and why
└── summary.md                    # Executive overview and next steps
```

**Handoff to sop-planning:** The `referents/` directory contents serve as high-quality input for sop-planning. Use `referents/extracted-patterns.md` as the foundation for design decisions, and `referents/catalog.md` as the `discovery_path` equivalent:
- Example: `/sop-planning rough_idea="{goal}" discovery_path="{output_dir}/referents/catalog.md" project_dir=".ralph/specs/{goal}" mode={PLANNING_MODE}`

---

## The Investigation Process (search_mode=reverse)

### Step 1: Identify Target Type

You MUST analyze the target to determine its type. You MUST present determination with evidence.

**Constraints:**
- You MUST confirm type with user in interactive mode
- You MUST wait for explicit confirmation before proceeding in interactive mode
- You MUST auto-detect type and log determination in autonomous mode
- You MUST NOT proceed without confirmation in interactive mode because type misclassification corrupts all downstream analysis
- You SHOULD present multiple candidate types when confidence is low

See [references/artifact-types.md](references/artifact-types.md) for type detection criteria.

### Step 2: Initial Batch Analysis

You MUST perform comprehensive first-pass analysis without user interaction. You MUST cover all relevant aspects for the artifact type. You MUST create `investigation.md` with executive summary, detailed findings, observations, and questions.

**Constraints:**
- You MUST complete entire analysis BEFORE asking user questions
- You MUST create investigation.md with all findings
- You MUST document artifact boundaries and scope
- You SHOULD cover all checklist items for the artifact type
- You SHOULD identify dependencies and integrations
- You MAY skip checklist items with explicit justification when irrelevant to target

See [references/artifact-types.md](references/artifact-types.md) for analysis checklist by type.

### Step 3: Interactive Refinement

You MUST present findings summary before asking questions. You MUST ask clarifying questions one at a time. You MUST incorporate responses into investigation.md. You MUST continue until user confirms "ready to generate specs".

**Constraints:**
- You MUST ask ONE clarifying question at a time in interactive mode
- You MUST wait for user response before asking next question
- You MUST skip interactive refinement in autonomous mode
- You MUST document deferred questions under "## Deferred Questions" in autonomous mode
- You MUST NOT batch questions in interactive mode because batched questions produce shallow, incomplete responses
- You SHOULD prioritize questions by impact on spec quality

See [references/investigation-patterns.md](references/investigation-patterns.md) for question guidelines.

### Step 4: Generate Specs

You MUST create structured specifications in `specs-generated/` directory. You MUST use appropriate spec structure for artifact type. You SHOULD include mermaid diagrams for flows and relationships.

**Constraints:**
- You MUST generate specs compatible with sop-planning for forward flow
- You MUST use appropriate spec structure for artifact type
- You MUST include source references in specs
- You SHOULD include mermaid diagrams for flows and relationships
- You MAY generate additional artifact-specific outputs when they add value

See [references/artifact-types.md](references/artifact-types.md) for spec templates by type.

### Step 5: Recommendations

You MUST generate `recommendations.md` with improvements, risks, migration paths, and prioritized next steps. You MUST present final summary. You SHOULD ask if user wants to continue to sop-planning in interactive mode.

**Constraints:**
- You MUST ask user if they want to continue to sop-planning in interactive mode
- You MUST NOT auto-invoke sop-planning in autonomous mode because the caller controls workflow transitions, not the skill
- You MUST NOT auto-invoke sop-planning without user permission in interactive mode because users need to review findings before committing to planning
- You MUST prioritize recommendations by ROI
- You SHOULD include effort estimates for recommendations

See [references/output-structure.md](references/output-structure.md) for template.

**Handoff to sop-planning:**

The `specs-generated/` output is designed to feed into sop-planning as the `rough_idea` parameter:
- Use `specs-generated/` directory contents as `rough_idea` input to sop-planning
- Alternatively, `investigation.md` serves as a discovery.md equivalent and can be passed as `discovery_path`
- Example: `/sop-planning rough_idea="./specs-generated/" discovery_path="./investigation.md"`

Note: `investigation.md` has a different structure than `discovery.md` from sop-discovery. When passed as `discovery_path` to sop-planning, the planning skill should extract problem definition, constraints, and risks from the investigation's Executive Summary, Detailed Findings, and Observations sections respectively.

## Output Structure

### Reverse Engineering (search_mode=reverse)
```text
{output_dir}/
├── investigation.md          # Raw findings and analysis
├── specs-generated/          # Structured specs by type
├── recommendations.md        # Improvement suggestions
├── summary.md                # Overview and next steps
└── artifacts/                # Supporting materials
```

### Referent Discovery (search_mode=referent)
```text
{output_dir}/
├── referents/                    # Referent discovery catalog
│   ├── catalog.md                # Summary: all referents, scores, recommendation
│   ├── {referent-name}-analysis.md  # Per-referent detailed analysis
│   ├── comparative-analysis.md   # Cross-referent pattern comparison
│   └── extracted-patterns.md     # Patterns ready to adopt in new design
├── investigation.md              # Search process and methodology
├── recommendations.md            # Which patterns to adopt and why
└── summary.md                    # Executive overview and next steps
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
| Referents Before Design | When building new, find world-class exemplars first — build on proven patterns, not guesswork |
| Comparative Analysis | Multiple referents enable pattern extraction; single referent risks cargo-culting |

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
/sop-reverse target="./monolith-app" mode="autonomous" output_dir=".ralph/specs/monolith-audit"
```
Output: Complete investigation without user interaction, deferred questions documented

### Example 5: Referent Discovery Before Building
```text
/sop-reverse target="real-time collaboration engine" search_mode="referent" focus_areas="CRDT,operational-transform"
```
Output: `referents/` catalog with analysis of Yjs, Automerge, ShareDB; comparative patterns; recommended foundation

### Example 6: Referent Discovery for API Design
```text
/sop-reverse target="developer API with excellent DX" search_mode="referent" focus_areas="auth,pagination,error-handling"
```
Output: Analysis of Stripe, GitHub, Twilio APIs; extracted DX patterns; design recommendations

### Example 7: Referent-Driven Architecture
```text
/sop-reverse target="event-driven microservices" search_mode="referent" mode="autonomous" output_dir=".ralph/specs/event-arch-referents"
```
Output: Autonomous catalog of exemplar event architectures; pattern extraction for new design

## Integration with Forward Flow

### Reverse Engineering → Forward
After investigation completes, specs in `specs-generated/` feed into sop-planning:

```text
sop-reverse (reverse) -> sop-planning -> sop-task-generator -> ralph-orchestrator
```

### Referent Discovery → Forward
After referent discovery completes, the `referents/` catalog feeds into sop-planning as high-quality design input:

```text
sop-reverse (referent) -> sop-planning (with referent patterns) -> sop-task-generator -> ralph-orchestrator
```

## References

- [references/artifact-types.md](references/artifact-types.md) - Analysis checklists and spec templates per type
- [references/output-structure.md](references/output-structure.md) - Directory structure and file templates
- [references/mermaid-examples.md](references/mermaid-examples.md) - Diagram types and examples
- [references/investigation-patterns.md](references/investigation-patterns.md) - Questions, errors, quality gates

---

*Part of the SOP framework: sop-reverse (referent|reverse) -> sop-planning -> sop-task-generator -> ralph-orchestrator*
