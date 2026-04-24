---
outline: 2
---

# Phase 10 — Scenarios-in-Specs + Enforcement Refinement

**Status**: AUTHORIZED 2026-04-24 by user · REVISED post Codex 5.5 xhigh review
**Owner**: Claude Opus 4.7 (Tech Lead)
**Supersedes**: prior Option A/B/C proposals
**Target release**: 2026.4.0
**Baseline**: `2b82b2a` (66 commits ahead of origin — plan v1 committed, revisions pending)

## Codex v3 verdict — B1/B2 architectural blockers resolved in v4

v3 review said NO. 6 blockers remained, 2 architectural:

- **B1** (skill invocation per-sid): leader sid ≠ teammate sid → state doesn't propagate
- **B2** (task metadata transport): `TaskUpdate(completed)` payload doesn't carry TaskCreate metadata to the hook

### v4 resolutions (no new complex mechanisms)

**B1 fix** — swap skill-invoked state from per-sid file to per-project file with 30min TTL. ~20 LOC in `_sdd_state.py`. Leader invokes verification → all teammates in same cwd inherit within TTL. Factory.ai semantic: one mission = one verification contract.

**B2 fix** — **drop metadata entirely**. Classifier is the already-tracked `_has_source_edits(cwd, sid)`:
- Session edited `.py/.ts/.go/...` → implementation task → full gate
- Session edited only `.md/docs/scenarios` → admin task → integrity check only

Empirically verified: `sdd-auto-test.py:215` filters non-source/non-test files BEFORE `record_file_edit` — markdown never enters `source_files` set. No new transport needed.

### Other v3 findings closed

- SCEN-103 / SCEN-119 aligned at 4 enforcement points (SessionStart + PreToolUse + TaskUpdate + task-completed)
- SCEN-125 reverted from reject-by-basename to accept + telemetry (fixes overcorrection)
- SCEN-126 expanded to 4 symlink vectors
- SCEN-127 + new SCEN-129 close template scope (`template/.claude.template/config.json.template` + `template/gitignore.template`)
- SCEN-123 expanded: audit scans `.ralph/config.sh` too

## Codex 5.5 xhigh review v2 — 10 original + 4 new findings addressed in v3

Plan v1 had 10 findings. Plan v2 addressed the intent but 7/10 remained open + 4 new holes emerged. Plan v3 closes all 14 with explicit operationalization. Review trail commits: `2b82b2a` (v1) → `3239190` (v2) → THIS commit (v3).

### v2 review follow-ups

| # | Finding v2 | Resolution v3 |
|---|---|---|
| C1b | Plan body referenced `SCEN-10-*` in gates/success criteria (stale from v1) | All refs rewritten to `SCEN-1NN` via sed |
| C2b | SCEN-103 missed that current `task-completed.py:546,1007` skip on no scenarios / no source edits | Enforcement at 4 points explicit; `legacy_scenarios_present(cwd)` check inserted before every early-exit |
| C3b | Commit-before-spawn isn't enough; leader's own completion can race | SCEN-112 extended: commit BEFORE any completion (leader, teammate, admin) |
| C4b | `metadata.admin=true` transport unspecified (hook reads stdin only, no TaskGet) | SCEN-118 explicit: reads `tool_input.metadata.admin` from stdin JSON — payload-based, no external calls |
| C5b | session-start.py auto-adds `!/.claude/scenarios/`; .gitignore never committed; `!/.ralph/specs/**` missing; template still ignores `/.ralph/` | Phase 10.2 scope includes session-start.py CRITICAL_GITIGNORE_RULES update + template/gitignore.template update; gitignore fixed in THIS commit with `!/.ralph/specs/**` + `!/docs/specs/**` |
| C6b/C8b | "cheap" = git ls-tree subprocess; lru_cache per-process is weak | SCEN-110 cache to `/tmp/sdd-discovery-{project_hash}-{sid}.json` TTL 600s; SCEN-122 concrete benchmark baseline |
| C9b | mutation per-phase, not per-SCEN | Validation cycle updated: each SCEN gets red-green-refactor-mutation individually |
| C10b | secret detector method unspecified | SCEN-123: explicit regex list + entropy threshold + `.migration-allowlist` |

### v2 new holes

| # | Finding | Resolution |
|---|---|---|
| N1 | Duplicate scenario names across specs — no conflict policy | SCEN-125: dedup by basename, duplicate = error |
| N2 | Symlinked spec/scenario directories not covered | SCEN-126: symlinks rejected at discovery with telemetry |
| N3 | Phase ordering risk: 10.1 alone breaks enforcement | Phase plan notes 10.1 + 10.2 MUST land together or 10.1 in-flight leaves hooks referencing old paths |
| N4 | `template/.claude.template/config.json.template` missing SCENARIO_DISCOVERY_ROOTS | SCEN-127: template updated in Phase 10.4 |

### Plan v1 findings (for trail completeness)

| # | Finding | Resolution |
|---|---|---|
| C1 | SCEN ID `SCEN-1NNN` fails parser `SCEN-\d{3}` | Renumbered to `SCEN-1NN` (3-digit) |
| C2 | Migration fail-open via silent "no scenarios" fallback | SCEN-103, 119 — legacy path FAIL CLOSED |
| C3 | SID-allowlist weak for "leader vs teammate" | SCEN-112 — no allowlist; commit-before-spawn contract |
| C4 | Admin-task bypass on metadata absence | SCEN-118 — explicit opt-IN `metadata.admin=true` only |
| C5 | Gitignore nested-override risk | SCEN-124 — migration doc covers `!/.ralph/specs/**` + verification cmd |
| C6 | G1 gate full-verification friction on admin tasks | SCEN-110, 113 — split: cheap integrity always, full verification only for `metadata.codeTaskFile` |
| C7 | Amend marker global/upward search | SCEN-108 — strict `rel.parent / ".amends"`, symlinks rejected |
| C8 | Discovery perf on monorepos | SCEN-122 — `has_any_scenarios(cwd)` fast-path + lru_cache |
| C9 | Test migration false-green risk | Plan validation cycle #4 (mutation) mandatory per SCEN |
| C10 | Sensitive data in `.ralph/specs/` on migration | SCEN-123 — `phase10-migration-audit.py` secret scan |

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

## Observable scenarios (SCEN-1XX, SDD contract)

Revised 2026-04-24 post Codex 5.5 xhigh review. Full contract: `.ralph/specs/phase10/scenarios/phase10.scenarios.md`. 24 scenarios organized by category.

### Category A — Architecture migration
- **SCEN-101**: discovery finds `.ralph/specs/*/scenarios/*.scenarios.md`
- **SCEN-102**: discovery finds `docs/specs/*/scenarios/*.scenarios.md`
- **SCEN-103**: legacy `.claude/scenarios/` FAIL CLOSED at PreToolUse/TaskCompleted (NOT silent skip)
- **SCEN-104**: `SCENARIO_DISCOVERY_ROOTS` config override honored

### Category B — Hook path resolution
- **SCEN-105**: nested-path write-once guard
- **SCEN-106**: PreToolUse Edit parity across locations
- **SCEN-107**: Bash sed/rm on nested scenario DENY
- **SCEN-108**: amend marker strict parent-scoped (symlinks rejected, non-sibling rejected)
- **SCEN-109**: telemetry records full nested path

### Category C — G1 fix (Codex finding — integrity gate)
- **SCEN-110**: CHEAP integrity check BEFORE `_has_source_edits` early-exit; admin-task fast-path when no scenario divergence
- **SCEN-111**: deletion detection
- **SCEN-112**: untracked scenario REJECTED at completion — NO sid allowlist (commit-before-spawn contract)
- **SCEN-113**: FULL verification runs ONLY on tasks with `metadata.codeTaskFile`

### Category D — Skill alignment
- **SCEN-114**: scenario-driven-development outputs spec-folder
- **SCEN-115**: brainstorming outputs spec-folder
- **SCEN-116**: ralph-orchestrator Step 3.5 new path
- **SCEN-117**: sop-* chain references aligned

### Category E — Admin task friction (OPT-IN, fail-closed default)
- **SCEN-118**: explicit `metadata.admin=true` required to bypass — missing metadata FAILS CLOSED

### Category F — Migration (clean break, no silent degradation)
- **SCEN-119**: legacy `.claude/scenarios/` BLOCKS commit + TaskUpdate until migrated
- **SCEN-120**: ai-framework self-suite passes (≥1053 tests)

### Category G — Performance
- **SCEN-121**: `verification-before-completion` handles multi-spec
- **SCEN-122**: `has_any_scenarios(cwd)` fast-path <5ms for empty case

### Category H — Migration tooling
- **SCEN-123**: `scripts/phase10-migration-audit.py` detects secrets in `.ralph/specs/`
- **SCEN-124**: migration doc covers nested `.gitignore` edge case

**Satisfaction criteria**: **27/27** scenarios satisfied via execution evidence (red-green-refactor-mutation per SCEN).

### Category I — Conflict + symlink + template

- **SCEN-125**: duplicate scenario basename across specs → REJECT
- **SCEN-126**: symlinked spec directory → SKIP at discovery with telemetry
- **SCEN-127**: `template/.claude.template/config.json.template` includes SCENARIO_DISCOVERY_ROOTS

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

**Gate**: all existing scenario tests either updated or explicitly skipped; new discovery tests green; SCEN-101, SCEN-102, SCEN-104 satisfied.

### Phase 10.2 — Hook path migration + legacy fail-closed + session-start update (3h)

**Must land TOGETHER with Phase 10.1 in single merge (coupling: 10.1 introduces discovery, 10.2 consumes it; 10.1 alone breaks enforcement).**

**Commits**:
- `refactor(hooks): sdd-test-guard path resolution for nested spec paths + symlink rejection` + tests
- `refactor(hooks): amend marker resolver strict sibling-scoped (rel.parent/.amends only)` + symlink rejection tests
- `feat(hooks): legacy_scenarios_present(cwd) helper + 4-point fail-closed enforcement (SessionStart, PreToolUse, TaskUpdate, TaskCompleted)`
- `refactor(hooks): session-start.py CRITICAL_GITIGNORE_RULES for Phase 10 — remove legacy !/.claude/scenarios/, add !/.ralph/specs/ !/.ralph/specs/** !/docs/specs/ !/docs/specs/**`

**Gate**: SCEN-103, 105, 106, 107, 108, 109, 119, 126 satisfied.

### Phase 10.3 — G1 fix (split: cheap integrity + full verification) (2-3h)

**Commits**:
- `feat(hooks): _enforce_scenario_integrity_cheap — deleted/extra/modified detection via git-HEAD diff`
- `fix(hooks): task-completed runs cheap integrity BEFORE _has_source_edits; full verification gated on metadata.codeTaskFile`

**Implementation note** (Codex revisions):
- **Cheap check** (always runs): disk path set diff against `git ls-tree -r HEAD -- {discovery_roots}`. Deleted → REJECT. Untracked scenario → REJECT (no sid allowlist; leader must commit before spawn).
- **Full verification** (only for `metadata.codeTaskFile` tasks): validate_scenario_file + require verification-before-completion skill invocation.
- **Fast-path**: `has_any_scenarios(cwd)` lru_cached; returns False in <5ms for empty-scenario repos — integrity check short-circuits.

**Gate**: SCEN-110, 111, 112, 113, 122 satisfied.

### Phase 10.4 — Skill updates (3h)

**Commits**:
- `docs(skills): scenario-driven-development outputs spec-folder scenarios`
- `docs(skills): brainstorming outputs to {spec-root}/{name}/`
- `docs(skills): ralph-orchestrator Step 3.5 + templates updated`
- `docs(skills): sop-* chain references aligned`
- `docs(skills): verification-before-completion canonical path reference updated`

**Gate**: SCEN-1013, 014, 015, 016, 017 satisfied (verified by grep + test_scen_10_docs.py).

### Phase 10.5 — Admin vs implementation via session edits (B1/B2 fixes) (1-2h)

**Commits**:
- `refactor(hooks): skill-invoked state project-scoped (remove sid from filename), 30min TTL` — B1 fix
- `fix(hooks): TaskUpdate + task-completed policy gate classifies via _has_source_edits (no metadata)` — B2 fix

**Changes**:
- `_sdd_state.py`: `skill_invoked_path(cwd, skill, sid)` → `skill_invoked_path(cwd, skill)` (drop sid). Existing tests updated.
- `sdd-test-guard.py:623`: TaskUpdate policy gate reads `_has_source_edits(cwd, sid)` instead of checking scenarios-existence. If False → bypass. If True → enforce verification requirement.
- Admin tasks (markdown/docs edits only) naturally bypass; implementation tasks naturally enforce.

**Gate**: SCEN-113, 118, 128 satisfied.

### Phase 10.6 — Tests migration + full suite (2h)

**Commits**:
- `test(hooks): migrate all hardcoded .claude/scenarios/ to discovery-based fixtures`

**Gate**: `pytest hooks/ -q` → 1053+ passed (SCEN-1021 satisfied).

### Phase 10.7 — Migration tooling + docs + release prep (2-3h)

**Commits**:
- `feat(scripts): phase10-migration-audit.py — scan .ralph/specs/ for secrets pre-commit`
- `docs: migration-to-phase10.md — user guide with nested-gitignore warnings + secret audit step`
- `docs: update threat-model.md for Phase 10 architecture + empirical hook-firing evidence`
- `docs: CHANGELOG 2026.4.0 entry (humanized)`
- `chore: remove template/.claude/scenarios/ placeholder if present`

**Codex revisions**:
- Migration audit tool (SCEN-123) required before user `git add .ralph/specs/` — scans for API keys, passwords, tokens
- Migration doc covers nested `.gitignore` edge case with `git check-ignore -v` verification command (SCEN-124)

**Gate**: /humanizer pass on user-facing prose; CHANGELOG validated; no orphan refs to `.claude/scenarios/` outside migration docs; SCEN-123, 124 satisfied.

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
- 21/21 SCEN-1* scenarios satisfied with fresh execution evidence
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
