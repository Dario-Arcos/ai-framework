---
description: Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation.
model: claude-opus-4-1
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

Goal: Identify inconsistencies, duplications, ambiguities, and underspecified items across the three core artifacts (`spec.md`, `plan.md`, `tasks.md`) before implementation. This command MUST run only after `/SDD-cycle:tasks` has successfully produced a complete `tasks.md`.

STRICTLY READ-ONLY: Do **not** modify any files. Output a structured analysis report. Offer an optional remediation plan (user must explicitly approve before any follow-up editing commands would be invoked manually).

Constitution Authority: The project constitution (`.specify/memory/constitution.md`) is **non-negotiable** within this analysis scope. Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks—not dilution, reinterpretation, or silent ignoring of the principle. If a principle itself needs to change, that must occur in a separate, explicit constitution update outside `/analyze`.

Execution steps:

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` once from repo root and parse JSON for FEATURE_DIR and AVAILABLE_DOCS. Derive absolute paths:
   - SPEC = FEATURE_DIR/spec.md
   - PLAN = FEATURE_DIR/plan.md
   - TASKS = FEATURE_DIR/tasks.md
     Abort with an error message if any required file is missing (instruct the user to run missing prerequisite command).

2. Load artifacts:
   - Parse spec.md sections: Overview/Context, Functional Requirements, Non-Functional Requirements, User Stories, Edge Cases (if present).
   - Parse plan.md: Architecture/stack choices, Data Model references, Phases, Technical constraints.
   - Parse tasks.md: Task IDs, descriptions, phase grouping, parallel markers [P], referenced file paths.
   - Load constitution `.specify/memory/constitution.md` for principle validation.

3. Build internal semantic models:
   - Requirements inventory: Each functional + non-functional requirement with a stable key (derive slug based on imperative phrase; e.g., "User can upload file" -> `user-can-upload-file`).
   - User story/action inventory.
   - Task coverage mapping: Map each task to one or more requirements or stories (inference by keyword / explicit reference patterns like IDs or key phrases).
   - Constitution rule set: Extract principle names and any MUST/SHOULD normative statements.

4. Detection passes:
   A. Duplication detection:
   - Identify near-duplicate requirements. Mark lower-quality phrasing for consolidation.
     B. Ambiguity detection:
   - Flag vague adjectives (fast, scalable, secure, intuitive, robust) lacking measurable criteria.
   - Flag unresolved placeholders (TODO, TKTK, ???, <placeholder>, etc.).
     C. Underspecification:
   - Requirements with verbs but missing object or measurable outcome.
   - User stories missing acceptance criteria alignment.
   - Tasks referencing files or components not defined in spec/plan.
     D. Constitution alignment:
   - Any requirement or plan element conflicting with a MUST principle.
   - Missing mandated sections or quality gates from constitution.
     E. Coverage gaps:
   - Requirements with zero associated tasks.
   - Tasks with no mapped requirement/story.
   - Non-functional requirements not reflected in tasks (e.g., performance, security).
     F. Inconsistency:
   - Terminology drift (same concept named differently across files).
   - Data entities referenced in plan but absent in spec (or vice versa).
   - Task ordering contradictions (e.g., integration tasks before foundational setup tasks without dependency note).
   - Conflicting requirements (e.g., one requires to use Next.js while other says to use Vue as the framework).

5. Parallel Stream Analysis:
   **DELEGATE TO SPECIALIST**: Use Task tool to invoke `agent-assignment-analyzer` with tasks.md content to generate intelligent agent assignments and parallel execution recommendations.

   Use Task tool: `agent-assignment-analyzer` → Analyze tasks.md content and generate:
   - Task-to-agent intelligent mapping
   - File dependency conflict detection
   - Parallel execution streams identification
   - Coordination points analysis
   - Parallelization optimization recommendations
     A. Task categorization by agent expertise:
   - Setup tasks → general-purpose
   - Test tasks (unit/integration) → test-automator
   - API/Service tasks → backend-architect
   - Frontend/UI tasks → frontend-developer
   - Database/Schema tasks → database-optimizer
   - DevOps/Infrastructure → devops-troubleshooter
   - Documentation → docs-architect
     B. File dependency mapping:
   - Parse file paths referenced in tasks.md
   - Identify shared files across multiple tasks
   - Mark file conflicts that require coordination
     C. Coordination point identification:
   - Tasks affecting same files = sequential execution required
   - Tasks with [P] marker + different files = parallel eligible
   - Dependencies between task phases (Setup → Tests → Core → Integration → Polish)
     D. Generate execution coordination plan:
   - Group parallel-eligible tasks into streams
   - Assign optimal agent type per stream
   - Document coordination checkpoints
   - Estimate parallelization factor (sequential time / parallel time)

6. Severity assignment heuristic:
   - CRITICAL: Violates constitution MUST, missing core spec artifact, or requirement with zero coverage that blocks baseline functionality.
   - HIGH: Duplicate or conflicting requirement, ambiguous security/performance attribute, untestable acceptance criterion.
   - MEDIUM: Terminology drift, missing non-functional task coverage, underspecified edge case.
   - LOW: Style/wording improvements, minor redundancy not affecting execution order.

7. Produce a Markdown report (no file writes) with sections:

   ### Specification Analysis Report

   | ID  | Category    | Severity | Location(s)      | Summary                      | Recommendation                       |
   | --- | ----------- | -------- | ---------------- | ---------------------------- | ------------------------------------ |
   | A1  | Duplication | HIGH     | spec.md:L120-134 | Two similar requirements ... | Merge phrasing; keep clearer version |

   (Add one row per finding; generate stable IDs prefixed by category initial.)

   Additional subsections:
   - Coverage Summary Table:
     | Requirement Key | Has Task? | Task IDs | Notes |
   - Constitution Alignment Issues (if any)
   - Unmapped Tasks (if any)
   - **Parallel Execution Plan**:
     | Stream | Agent Type | Tasks | Can Start | Dependencies | Files at Risk |
     |--------|------------|-------|-----------|--------------|---------------|
     | Stream A | backend-architect | T001, T003 | Immediately | None | src/api/_.ts |
     | Stream B | test-automator | T002, T004 | Immediately | None | tests/_.spec.ts |
     | Stream C | frontend-developer | T005 | After Stream A | Stream A complete | src/components/\*.tsx |
   - **Coordination Points**:
     - Shared files requiring sequential access
     - Phase dependencies that cannot be parallelized
     - Agent handoff points and synchronization needs
   - Metrics:
     - Total Requirements
     - Total Tasks
     - Coverage % (requirements with >=1 task)
     - Ambiguity Count
     - Duplication Count
     - Critical Issues Count
     - **Parallel Streams Identified**
     - **Parallelization Factor** (estimated speedup)

8. At end of report, output a concise Next Actions block:
   - If CRITICAL issues exist: Recommend resolving before `/SDD-cycle:implement`.
   - If only LOW/MEDIUM: User may proceed, but provide improvement suggestions.
   - Provide explicit command suggestions: e.g., "Run /SDD-cycle:specify with refinement", "Run /SDD-cycle:plan to adjust architecture", "Manually edit tasks.md to add coverage for 'performance-metrics'".

9. Ask the user: "Would you like me to suggest concrete remediation edits for the top N issues?" (Do NOT apply them automatically.)

Behavior rules:

- NEVER modify files.
- NEVER hallucinate missing sections—if absent, report them.
- KEEP findings deterministic: if rerun without changes, produce consistent IDs and counts.
- LIMIT total findings in the main table to 50; aggregate remainder in a summarized overflow note.
- If zero issues found, emit a success report with coverage statistics and proceed recommendation.

Context: $ARGUMENTS
