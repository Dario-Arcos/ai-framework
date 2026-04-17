# Migration To Scenarios

## Who Is This For

This guide is for projects already using the plugin from before Phase 3, where scenario artifacts did not yet exist as a first-class contract. The goal is adoption with minimal disruption: keep current workflows, add committed observable scenarios where they help, and understand the rollback path if the team needs to back out.

## What Changed

- Scenario artifacts now live at `.claude/scenarios/*.scenarios.md`.
- Committed scenario files are write-once unless a reviewed amend marker exists.
- `verification-before-completion` now treats committed scenarios as the canonical acceptance contract.
- Task completion is scenarios-first when the directory exists.
- Tier-2 stack tuning moved to `.claude/config.json` with `SOURCE_EXTENSIONS`, `TEST_FILE_PATTERNS`, and `COVERAGE_REPORT_PATH`.

## Step-By-Step Adoption

1. Update the plugin.
   Use your normal upgrade path, such as `npm update -g @ai-framework/...`, or the equivalent for your install method.
2. Create `.claude/scenarios/` and write your first scenario.
   Use one `.scenarios.md` file per feature area or task family. Keep the file in the canonical shape:

   ```markdown
   ---
   name: login-validation
   created_by: orchestrator
   created_at: 2026-04-16T10:00:00Z
   ---

   ## SCEN-001: successful login
   **Given**: unregistered anonymous user
   **When**: POST /login with valid email + password
   **Then**: response 200 with session token, redirect to /dashboard
   **Evidence**: HTTP response body, cookies set
   ```
3. Commit the scenario.
   The first commit establishes the baseline. After that, edits are treated as contract amendments and require `sop-reviewer` plus an amend marker.
4. Invoke `verification-before-completion` during implementation.
   When scenarios exist, verification must iterate every committed scenario file and confirm observable satisfaction before you claim completion.
5. Complete the task normally.
   `TaskUpdate(completed)` and `git commit` now run through the scenarios-first gate when `.claude/scenarios/` exists.

## Rollback

Use the narrowest rollback that solves the problem:

1. Delete one scenario file to remove a single contract.
2. Delete `.claude/scenarios/` to revert the project to fully backward-compatible pre-scenario behavior.
3. Reserved emergency bypass: `_SDD_DISABLE_SCENARIOS=1`.
   This is the broadest rollback shape described in `skills/ralph-orchestrator/references/quality-gates.md`, but it is not wired in the current hook code in this release. Do not depend on it unless your local fork explicitly supports it.

## FAQ

### Why does my Edit fail on a scenario file I just wrote?

Because the file now differs from its committed baseline. Revert it, or invoke `sop-reviewer` and create a valid amend marker for the current `HEAD`.

### Can I skip scenarios for a prototype?

Yes. If you do not create `.claude/scenarios/`, the plugin remains backward-compatible and the scenarios-first gates do not apply.
