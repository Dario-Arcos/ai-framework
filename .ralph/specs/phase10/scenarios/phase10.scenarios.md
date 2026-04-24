---
name: phase10
created_by: tech-lead
created_at: 2026-04-24T14:00:00Z
---

## SCEN-10-001: discovery finds Ralph-spec scenarios
**Given**: a file at `.ralph/specs/feat-x/scenarios/feat-x.scenarios.md` tracked in git
**When**: `scenario_files(cwd)` is invoked
**Then**: returned list contains that path (absolute)
**Evidence**: test asserts path in result; glob pattern `.ralph/specs/**/scenarios/*.scenarios.md` matches

## SCEN-10-002: discovery finds non-Ralph spec scenarios
**Given**: a file at `docs/specs/feat-y/scenarios/feat-y.scenarios.md` tracked in git
**When**: `scenario_files(cwd)` is invoked
**Then**: returned list contains that path
**Evidence**: test asserts inclusion; glob pattern `docs/specs/**/scenarios/*.scenarios.md` matches

## SCEN-10-003: legacy location emits deprecation, not discovered
**Given**: a file at `.claude/scenarios/legacy.scenarios.md`
**When**: SessionStart hook runs
**Then**: stderr contains `[SDD:DEPRECATED]` pointing to migration doc; `scenario_files` does NOT include legacy path
**Evidence**: SessionStart stderr capture; discovery test confirms exclusion

## SCEN-10-004: SCENARIO_DISCOVERY_ROOTS config override
**Given**: `.claude/config.json` with `{"SCENARIO_DISCOVERY_ROOTS": ["custom/specs"]}`
**When**: `scenario_files(cwd)` called in that project
**Then**: only `custom/specs/**/scenarios/*.scenarios.md` matches; defaults ignored
**Evidence**: test with temp config asserts behavior

## SCEN-10-005: nested-path write-once guard
**Given**: `.ralph/specs/feat-x/scenarios/feat-x.scenarios.md` committed
**When**: Edit tool attempts content mutation
**Then**: PreToolUse denies exit=2 with `[SDD:SCENARIO] scenario write-once violation on .ralph/specs/feat-x/scenarios/feat-x.scenarios.md`
**Evidence**: live hook invocation with nested path; exact stderr matches

## SCEN-10-006: PreToolUse Edit parity across locations
**Given**: a tracked scenario at any valid discovery root
**When**: Edit attempts mutation
**Then**: identical `[SDD:SCENARIO]` denial regardless of path depth
**Evidence**: parametrized test across `.ralph/specs/...` and `docs/specs/...`

## SCEN-10-007: Bash sed/rm on nested scenario DENY
**Given**: a tracked scenario at `.ralph/specs/x/scenarios/x.scenarios.md`
**When**: `Bash({"command": "sed -i \"\" \"s/a/b/\" .ralph/specs/x/scenarios/x.scenarios.md"})`
**Then**: PreToolUse denies exit=2 with `[SDD:SCENARIO] Bash command modifies scenario files`
**Evidence**: Bash regex matches `.ralph/specs/*/scenarios/` pattern; live hook test

## SCEN-10-008: amend marker co-located with spec
**Given**: an amend at `.ralph/specs/x/scenarios/.amends/x-<SHA>.marker` + sop-reviewer invoked
**When**: Edit attempts content change on `.ralph/specs/x/scenarios/x.scenarios.md`
**Then**: Edit ALLOWED (marker honored)
**Evidence**: live hook test; amend resolver walks parent `scenarios/` dir for markers

## SCEN-10-009: telemetry records full nested file_path
**Given**: guard fires on nested path
**When**: `guard_triggered` event written to metrics.jsonl
**Then**: `file_path` field contains full absolute nested path
**Evidence**: metrics.jsonl parse confirms full path string

## SCEN-10-010: integrity gate BEFORE `_has_source_edits` early-exit
**Given**: teammate modifies ONLY a scenario file (no source edits)
**When**: teammate calls TaskUpdate(completed) → task-completed.py runs
**Then**: `_enforce_scenario_integrity` runs BEFORE the `_has_source_edits` early-return; hash mismatch detected; exit=2 `[SDD:SCENARIO] integrity`
**Evidence**: monkeypatched test of task-completed.py with scenario tamper + no source edits → _fail_task called

## SCEN-10-011: deletion detection in integrity gate
**Given**: a scenario was tracked at HEAD but removed from disk
**When**: task-completed.py integrity check runs
**Then**: exit=2 `[SDD:SCENARIO] integrity — deleted: <path>`
**Evidence**: test with `rm scenarios/X` before hook invocation; assertion in stderr

## SCEN-10-012: new scenario post-baseline rejection
**Given**: a scenario exists on disk but not tracked at HEAD AND current session is not the authoring session
**When**: task-completed.py integrity check runs
**Then**: exit=2 `[SDD:SCENARIO] integrity — extra: <path>`
**Evidence**: test with new untracked scenario + teammate sid context

## SCEN-10-013: scenario-driven-development outputs spec-folder
**Given**: SKILL invoked with scenario name "auth"
**When**: skill produces its output
**Then**: file lives at `docs/specs/auth/scenarios/auth.scenarios.md` (non-Ralph) OR `.ralph/specs/auth/scenarios/auth.scenarios.md` (Ralph detected)
**Evidence**: grep of SKILL.md confirms canonical path guidance; integration test

## SCEN-10-014: brainstorming skill outputs inside spec folder
**Given**: brainstorming skill invoked for goal "cart-redesign"
**When**: skill writes brainstorm artifact
**Then**: file lives at `docs/specs/cart-redesign/brainstorm.md` (non-Ralph) OR `.ralph/specs/cart-redesign/brainstorm.md` (Ralph detected)
**Evidence**: grep of SKILL.md confirms; artifact path reference aligned

## SCEN-10-015: ralph-orchestrator Step 3.5 new path
**Given**: ralph-orchestrator at Step 3.5 for goal "auth-rewrite"
**When**: invokes scenario-driven-development
**Then**: produces `.ralph/specs/auth-rewrite/scenarios/auth-rewrite.scenarios.md` — never `.claude/scenarios/`
**Evidence**: grep of SKILL.md + template; no `.claude/scenarios/` references outside deprecation docs

## SCEN-10-016: sop-* chain references aligned
**Given**: sop-discovery, sop-planning, sop-task-generator, sop-code-assist, sop-reviewer
**When**: grep across all SOP SKILL.md files for scenario path references
**Then**: zero references to `.claude/scenarios/`; all use `{spec-root}/{spec}/scenarios/`
**Evidence**: grep returns empty for the old pattern outside migration docs

## SCEN-10-017: verification-before-completion handles multi-spec discovery
**Given**: project with 3 active specs in `.ralph/specs/` and 2 in `docs/specs/`
**When**: skill iterates scenarios to verify
**Then**: reads all 5 specs' scenarios; validates each SCEN block against execution evidence
**Evidence**: skill references discovery primitive; test with multi-spec fixture

## SCEN-10-018: admin-task TaskUpdate bypasses policy gate
**Given**: a task WITHOUT `metadata.codeTaskFile`
**When**: TaskUpdate(status="completed") fires
**Then**: sdd-test-guard policy gate does NOT fire; TaskUpdate succeeds
**Evidence**: live probe with admin task → no stderr, no exit 2

## SCEN-10-019: Ralph-generated TaskUpdate enforces policy gate
**Given**: a task WITH `metadata.codeTaskFile` (Ralph-generated)
**When**: TaskUpdate(status="completed") fires without prior /verification-before-completion
**Then**: exit=2 `[SDD:POLICY] TaskUpdate(completed) blocked`
**Evidence**: live probe with Ralph-metadata task; denial observed

## SCEN-10-020: legacy-only project shows migration guidance
**Given**: project with ONLY `.claude/scenarios/X.scenarios.md` and no spec folders
**When**: SessionStart runs
**Then**: stderr shows `[SDD:MIGRATION] legacy .claude/scenarios/ detected — migrate to docs/specs/{name}/scenarios/ (see docs/migration-to-phase10.md)`
**Evidence**: SessionStart invocation with legacy-only fixture → stderr capture

## SCEN-10-021: ai-framework self-suite still passes
**Given**: ai-framework repo post-Phase-10 migration
**When**: `python3 -m pytest hooks/ -q`
**Then**: stdout last line `1053 passed` or greater; no new failures
**Evidence**: full suite run output
