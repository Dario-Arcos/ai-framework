---
outline: 2
---

# Phase 10 — Scenarios-in-Specs + Enforcement Refinement

**Status**: AUTHORIZED 2026-04-24 by user
**Owner**: Claude Opus 4.7 (Tech Lead)
**Supersedes**: prior Option A/B/C proposals
**Target release**: 2026.4.0
**Baseline**: `a87d807` (65 commits ahead of origin)

## Executive summary

Phase 10 addresses three orthogonal findings discovered during Phase 9 silent validation:

1. **Architectural**: scenarios currently live in `.claude/scenarios/` (flat, global, orphaned from specs). Factory.ai / StrongDM co-locate the validation contract with its spec. Migrate to spec-folder layout.
2. **G1 bypass (Codex 5.5 xhigh)**: `_has_source_edits` early-exit in `task-completed.py:1007` skips the scenario gate for teammate tasks that modify only non-source files. Fix.
3. **Empirical reality (Fase 0 decisive)**: `PreToolUse sdd-test-guard` DOES fire in Ralph teammates (shared cwd, `Task(team_name=...)` no isolation). Previously documented as "known gap" — this claim is now wrong. Update docs + remove caveats.

**NO backward-compat** for legacy `.claude/scenarios/` — clean break.

---

## Final architecture

```
Ralph mode:
  .ralph/specs/{goal}/
    ├── referents/catalog.md
    ├── design/detailed-design.md
    ├── implementation/plan.md
    ├── scenarios/{goal}.scenarios.md          ← NEW location
    │   └── .amends/<name>-<HEAD_SHA>.marker   ← amend markers co-located
    └── tasks/*.code-task.md

Non-Ralph mode:
  docs/specs/{spec-name}/
    ├── design.md (or brainstorm.md, etc.)
    └── scenarios/
        ├── {spec-name}.scenarios.md
        └── .amends/
```

**Config** (`_sdd_config.py`):
```python
SCENARIO_DISCOVERY_ROOTS = [".ralph/specs", "docs/specs"]
SCENARIO_FILE_PATTERN = "**/scenarios/*.scenarios.md"
```

Override via `.claude/config.json` → `SCENARIO_DISCOVERY_ROOTS`.

**Discovery**: `scenario_files(cwd)` globs `{root}/**/scenarios/*.scenarios.md` for each root in config, dedup, return sorted.

---

## Observable scenarios (SCEN-10-*, SDD contract)

### Category A — Architecture migration
- **SCEN-10-001**: Discovery glob finds scenarios under `.ralph/specs/*/scenarios/*.scenarios.md`
- **SCEN-10-002**: Discovery glob finds scenarios under `docs/specs/*/scenarios/*.scenarios.md`
- **SCEN-10-003**: `.claude/scenarios/` presence emits `[SDD:DEPRECATED]` warning at SessionStart; files NOT discovered (forced migration)
- **SCEN-10-004**: Config override `SCENARIO_DISCOVERY_ROOTS` in `.claude/config.json` honored
- **SCEN-10-005**: Write-once guard path resolution correct for nested scenario paths (`.ralph/specs/feat-x/scenarios/feat-x.scenarios.md`)

### Category B — Hook migration
- **SCEN-10-006**: PreToolUse Edit on scenario under new path → DENY `[SDD:SCENARIO]` (parity with old path)
- **SCEN-10-007**: Bash writes (sed -i, rm, etc.) to new scenario paths → DENY
- **SCEN-10-008**: Amend marker location updated: `{spec}/scenarios/.amends/...` — resolution works
- **SCEN-10-009**: Post-tool-use telemetry `guard_triggered` includes full new path in `file_path` field

### Category C — G1 fix (Codex finding)
- **SCEN-10-010**: Ralph teammate marks TaskUpdate(completed) after modifying ONLY scenarios → gate runs BEFORE `_has_source_edits` early-exit → REJECT if hash mismatch
- **SCEN-10-011**: Integrity gate on deletion: teammate deletes a committed scenario → gate detects missing path → REJECT
- **SCEN-10-012**: Integrity gate on new scenario: teammate creates new scenario not in baseline → REJECT unless leader-authored (Ralph Step 3.5)

### Category D — Skill alignment
- **SCEN-10-013**: `scenario-driven-development` skill outputs to `docs/specs/{name}/scenarios/` (non-Ralph) or `.ralph/specs/{goal}/scenarios/` (Ralph) — never `.claude/scenarios/`
- **SCEN-10-014**: `brainstorming` skill output location aligned — artifacts in `docs/specs/{name}/` or `.ralph/specs/{goal}/`
- **SCEN-10-015**: `ralph-orchestrator` Step 3.5 updated: outputs scenarios under `.ralph/specs/{goal}/scenarios/`
- **SCEN-10-016**: `sop-discovery`, `sop-planning`, `sop-task-generator`, `sop-code-assist`, `sop-reviewer` reference new path canonically
- **SCEN-10-017**: `verification-before-completion` skill references new path; handles multi-spec discovery

### Category E — Admin task friction
- **SCEN-10-018**: TaskUpdate(completed) on admin-tracking tasks (no `metadata.codeTaskFile`) → policy gate SKIPS (no verification required)
- **SCEN-10-019**: TaskUpdate(completed) on Ralph-generated tasks (has `metadata.codeTaskFile`) → policy gate ENFORCES (verification required)

### Category F — Backward compat (minimal, clean break)
- **SCEN-10-020**: Project with ONLY legacy `.claude/scenarios/` → SessionStart emits `[SDD:MIGRATION]` warning with migration instructions, hooks treat as if no scenarios present (backward-compat mode)
- **SCEN-10-021**: Full suite on this repo (ai-framework itself) continues passing at ≥1053 tests after migration

**Satisfaction criteria**: 21/21 scenarios satisfied via execution evidence (red-green-refactor per SCEN).

---

## Phase breakdown (7 phases, 12-16h wall-clock, ~12-15 atomic commits)

### Phase 10.0 — Plan + SDD scenario authorship (1-2h)

**Gate**: plan approved + scenarios written + committed

1. Commit this plan file (`docs/phase10-plan.md`) + scenarios file (`.ralph/specs/phase10/scenarios/phase10.scenarios.md`)
2. User reviews + approves plan via ExitPlanMode
3. Codex review of plan before Phase 10.1

### Phase 10.1 — Config-driven discovery primitive (2h)

**Commits**:
- `feat(hooks): _sdd_config SCENARIO_DISCOVERY_ROOTS + DISCOVERY_PATTERN` + `test_sdd_config_discovery`
- `refactor(hooks): _sdd_scenarios discovery glob-based, backward-compat fallback REMOVED`

**Gate**: all existing scenario tests either updated or explicitly skipped; new discovery tests green; SCEN-10-001, 002, 004 satisfied.

### Phase 10.2 — Hook path migration (2h)

**Commits**:
- `refactor(hooks): sdd-test-guard path resolution for nested spec paths` + tests
- `refactor(hooks): amend marker resolver co-located with spec`
- `feat(hooks): SessionStart emits [SDD:DEPRECATED] for legacy .claude/scenarios/`

**Gate**: SCEN-10-003, 005, 006, 007, 008, 009, 020 satisfied.

### Phase 10.3 — G1 fix (integrity gate before early-exit) (2h)

**Commits**:
- `fix(hooks): task-completed scenario integrity BEFORE _has_source_edits early-exit`
- `feat(hooks): _enforce_scenario_integrity — deleted/extra/modified detection via manifest-like check`

**Implementation note**: use live git-HEAD comparison (not separate manifest JSON — simpler). For each tracked scenario at HEAD: if disk missing → REJECT. For each disk scenario: if not tracked at HEAD (no first-add-commit) → REJECT unless leader's own session created it (sid-scoped allowlist).

**Gate**: SCEN-10-010, 011, 012 satisfied.

### Phase 10.4 — Skill updates (3h)

**Commits**:
- `docs(skills): scenario-driven-development outputs spec-folder scenarios`
- `docs(skills): brainstorming outputs to {spec-root}/{name}/`
- `docs(skills): ralph-orchestrator Step 3.5 + templates updated`
- `docs(skills): sop-* chain references aligned`
- `docs(skills): verification-before-completion canonical path reference updated`

**Gate**: SCEN-10-013, 014, 015, 016, 017 satisfied (verified by grep + test_scen_10_docs.py).

### Phase 10.5 — Admin task friction fix (1-2h)

**Commits**:
- `fix(hooks): TaskUpdate guard narrowed — only enforces on tasks with codeTaskFile metadata`

**Gate**: SCEN-10-018, 019 satisfied.

### Phase 10.6 — Tests migration + full suite (2h)

**Commits**:
- `test(hooks): migrate all hardcoded .claude/scenarios/ to discovery-based fixtures`

**Gate**: `pytest hooks/ -q` → 1053+ passed (SCEN-10-021 satisfied).

### Phase 10.7 — Docs + CHANGELOG + threat-model + release prep (1-2h)

**Commits**:
- `docs: update threat-model.md for Phase 10 architecture + empirical hook-firing evidence`
- `docs: migration-to-phase10.md — user-facing migration guide (humanized)`
- `docs: CHANGELOG 2026.4.0 entry (humanized)`
- `chore: remove template/.claude/scenarios/ placeholder if present`

**Gate**: /humanizer pass on user-facing prose; CHANGELOG validated; no orphan refs to `.claude/scenarios/`.

---

## Validation cycles

Per phase:
1. **Red**: failing tests for SCEN covered by this phase
2. **Green**: minimal impl
3. **Refactor**: clean
4. **Mutation**: revert impl → tests must go red → restore → tests green
5. **Full-suite**: `pytest hooks/ -q` → 1053+ passed
6. **Codex review**: `codex exec --model gpt-5.5 --config model_reasoning_effort=xhigh` on `git diff {phase_start}..HEAD` — address P0/P1
7. **Dogfood**: manual probe of the specific SCENs just satisfied (live hook invocation + metrics.jsonl inspection)
8. **Commit** with evidence in commit body

Before Phase 10.7 release prep:
- Full dogfood: create synthetic project with new layout, verify end-to-end
- Simulated Ralph run (bounded teammate) — verify Step 3.5 → scenarios → Phase 10.3 gate

---

## Hard constraints (respected throughout)

- NEVER `git push` without explicit user authorization
- NEVER `--no-verify` except for probe commits with explicit "revert after" in message (reverted same session)
- NEVER delete files outside declared scope
- ALWAYS SDD: tests before impl
- ALWAYS invoke `verification-before-completion` before each commit
- ALWAYS request Codex second opinion per-phase
- ALWAYS ask user when uncertain
- Negative-constraint phrasing in rules/docs (Zhang 2026)
- Observable Evidence fields on all SCEN (anti-eval-awareness)

---

## Success definition

Plugin 2026.4.0 ships when:
- 21/21 SCEN-10-* scenarios satisfied with fresh execution evidence
- `pytest hooks/ -q` ≥1053 passed
- Zero references to `.claude/scenarios/` outside explicit deprecation/migration docs
- Codex 5.5 xhigh per-phase reviews clean (no P0/P1 open)
- CHANGELOG + threat-model + migration guide humanized
- User explicit approval for `npm version 2026.4.0` + push + tag

---

## Resume instructions (if compacted)

1. Read this file end-to-end.
2. Run preflight: `python3 -m pytest hooks/ -q | tail -3` — must show 1053 passed.
3. Check task list — resume from in_progress phase.
4. Check last commit message for current position.
5. Read `.ralph/specs/phase10/scenarios/phase10.scenarios.md` for the SCEN contract.
6. Continue red-green-refactor per the uncompleted SCEN.

---

**END OF PLAN**
