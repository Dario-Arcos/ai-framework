---
name: phase10
created_by: tech-lead
created_at: 2026-04-24T14:00:00Z
revised_at: 2026-04-24T14:15:00Z
revision_reason: Codex 5.5 xhigh review — 10 material holes addressed
---

## SCEN-101: discovery finds Ralph-spec scenarios
**Given**: a file at `.ralph/specs/feat-x/scenarios/feat-x.scenarios.md` tracked in git
**When**: `scenario_files(cwd)` is invoked
**Then**: returned list contains that path (absolute)
**Evidence**: test asserts path in result; glob pattern `.ralph/specs/**/scenarios/*.scenarios.md` matches

## SCEN-102: discovery finds non-Ralph spec scenarios
**Given**: a file at `docs/specs/feat-y/scenarios/feat-y.scenarios.md` tracked in git
**When**: `scenario_files(cwd)` is invoked
**Then**: returned list contains that path
**Evidence**: test asserts inclusion; glob pattern `docs/specs/**/scenarios/*.scenarios.md` matches

## SCEN-103: legacy location fails closed
**Given**: a file at `.claude/scenarios/legacy.scenarios.md`
**When**: PreToolUse Edit, TaskUpdate(completed), OR task-completed gate runs
**Then**: exit=2 `[SDD:MIGRATION_REQUIRED]` stderr with migration guidance pointing to `docs/migration-to-phase10.md`; `scenario_files` does NOT include legacy path
**Evidence**: live hook test with legacy fixture; stderr capture; migration doc exists

## SCEN-104: SCENARIO_DISCOVERY_ROOTS config override
**Given**: `.claude/config.json` with `{"SCENARIO_DISCOVERY_ROOTS": ["custom/specs"]}`
**When**: `scenario_files(cwd)` called
**Then**: only `custom/specs/**/scenarios/*.scenarios.md` matches; defaults ignored
**Evidence**: test with temp config asserts behavior

## SCEN-105: nested-path write-once guard
**Given**: `.ralph/specs/feat-x/scenarios/feat-x.scenarios.md` committed
**When**: Edit tool attempts content mutation
**Then**: PreToolUse denies exit=2 with `[SDD:SCENARIO] scenario write-once violation on .ralph/specs/feat-x/scenarios/feat-x.scenarios.md`
**Evidence**: live hook invocation with nested path; exact stderr matches

## SCEN-106: PreToolUse Edit parity across locations
**Given**: a tracked scenario at any valid discovery root
**When**: Edit attempts mutation
**Then**: identical `[SDD:SCENARIO]` denial regardless of path depth
**Evidence**: parametrized test across `.ralph/specs/...` and `docs/specs/...`

## SCEN-107: Bash sed/rm on nested scenario DENY
**Given**: a tracked scenario at `.ralph/specs/x/scenarios/x.scenarios.md`
**When**: `Bash({"command": "sed -i '' 's/a/b/' .ralph/specs/x/scenarios/x.scenarios.md"})`
**Then**: PreToolUse denies exit=2 with `[SDD:SCENARIO] Bash command modifies scenario files`
**Evidence**: Bash regex matches `.ralph/specs/*/scenarios/` pattern; live hook test

## SCEN-108: amend marker strict parent-scoped
**Given**: an amend at `.ralph/specs/x/scenarios/.amends/x-<SHA>.marker` (same directory as scenario) + sop-reviewer invoked
**When**: Edit attempts content change on `.ralph/specs/x/scenarios/x.scenarios.md`
**Then**: Edit ALLOWED (marker honored). A marker placed at `docs/.amends/` or `.ralph/specs/.amends/` is NOT honored (parent-scoped only). Symlinks under `.amends/` are rejected.
**Evidence**: live hook test — 3 cases: sibling (accept), non-sibling (reject), symlink (reject)

## SCEN-109: telemetry records full nested file_path
**Given**: guard fires on nested path
**When**: `guard_triggered` event written to metrics.jsonl
**Then**: `file_path` field contains full absolute nested path
**Evidence**: metrics.jsonl parse confirms full path string

## SCEN-110: cheap integrity check before early-exit
**Given**: teammate task with scenarios present in repo (tracked), no source edits in session
**When**: task-completed.py runs
**Then**: cheap integrity scan (disk vs HEAD diff on discovered scenario paths) runs BEFORE `_has_source_edits` early-exit; detects deleted/extra/modified scenario files; exit=2 with `[SDD:SCENARIO]` if any mismatch; admin tasks with NO scenario divergence pass fast
**Evidence**: monkeypatched test — (a) tamper scenario → reject; (b) no tamper, admin task → early-exit reached, gate passes

## SCEN-111: deletion detection in integrity gate
**Given**: a scenario was tracked at HEAD but removed from disk at TaskCompleted time
**When**: task-completed.py integrity check runs
**Then**: exit=2 `[SDD:SCENARIO] integrity — deleted: <rel-path>`
**Evidence**: test with `rm scenarios/X` before hook invocation; stderr assertion

## SCEN-112: untracked scenario rejected at completion (no sid allowlist)
**Given**: a scenario exists on disk but NOT tracked at HEAD
**When**: task-completed.py integrity check runs
**Then**: exit=2 `[SDD:SCENARIO] integrity — untracked: <rel-path> (commit scenarios to parent branch before spawning teammates)`
**Evidence**: test with new untracked scenario in any session context; rejection regardless of sid

## SCEN-113: full verification runs only on implementation tasks
**Given**: task with `metadata.codeTaskFile` present (Ralph implementation task)
**When**: task-completed.py runs after cheap integrity passes
**Then**: full `_enforce_scenario_gate` runs (validates all scenarios + requires verification-before-completion skill invocation)
**Evidence**: test — implementation task without skill invocation → rejected with POLICY

## SCEN-114: scenario-driven-development outputs spec-folder
**Given**: SKILL invoked with scenario name "auth"
**When**: skill produces its output
**Then**: file lives at `docs/specs/auth/scenarios/auth.scenarios.md` (non-Ralph) OR `.ralph/specs/auth/scenarios/auth.scenarios.md` (Ralph detected via `.ralph/config.sh` presence)
**Evidence**: grep of SKILL.md confirms canonical path guidance; integration test with both modes

## SCEN-115: brainstorming skill outputs inside spec folder
**Given**: brainstorming skill invoked for goal "cart-redesign"
**When**: skill writes brainstorm artifact
**Then**: file lives at `docs/specs/cart-redesign/brainstorm.md` (non-Ralph) OR `.ralph/specs/cart-redesign/brainstorm.md` (Ralph mode)
**Evidence**: grep of SKILL.md confirms; artifact path reference aligned

## SCEN-116: ralph-orchestrator Step 3.5 new path
**Given**: ralph-orchestrator at Step 3.5 for goal "auth-rewrite"
**When**: invokes scenario-driven-development
**Then**: produces `.ralph/specs/auth-rewrite/scenarios/auth-rewrite.scenarios.md` — never `.claude/scenarios/`
**Evidence**: grep of SKILL.md + templates; no `.claude/scenarios/` references outside deprecation docs

## SCEN-117: sop-* chain references aligned
**Given**: sop-discovery, sop-planning, sop-task-generator, sop-code-assist, sop-reviewer
**When**: grep across all SOP SKILL.md files for scenario path references
**Then**: zero references to `.claude/scenarios/`; all use `{spec-root}/{spec}/scenarios/`
**Evidence**: grep returns empty for the old pattern outside migration docs

## SCEN-118: admin task opt-IN bypass (fail-closed default)
**Given**: a task with explicit `metadata.admin=true` flag set at creation
**When**: TaskUpdate(status="completed") fires
**Then**: sdd-test-guard policy gate SKIPS for this task; TaskUpdate succeeds
**Given (negative case)**: a task WITHOUT `metadata.admin=true` (default)
**When**: TaskUpdate(completed) fires with scenarios present
**Then**: policy gate ENFORCES — exit=2 `[SDD:POLICY]` unless verification-before-completion invoked
**Evidence**: live probes — admin flag honored, missing flag fails closed

## SCEN-119: legacy .claude/scenarios/ blocks commit
**Given**: project upgraded to 2026.4.0 with legacy `.claude/scenarios/X.scenarios.md` still present
**When**: user/agent attempts Bash(git commit) OR TaskUpdate(completed)
**Then**: exit=2 `[SDD:MIGRATION_REQUIRED] legacy .claude/scenarios/ detected — migrate to docs/specs/{name}/scenarios/ or .ralph/specs/{goal}/scenarios/ (see docs/migration-to-phase10.md)` — until migrated, no commits or completions proceed
**Evidence**: live test with legacy fixture; commit attempt blocked

## SCEN-120: ai-framework self-suite still passes
**Given**: ai-framework repo post-Phase-10 migration
**When**: `python3 -m pytest hooks/ -q`
**Then**: stdout last line `1053 passed` or greater; no new failures
**Evidence**: full suite run output

## SCEN-121: verification-before-completion handles multi-spec discovery
**Given**: project with 3 active specs in `.ralph/specs/` and 2 in `docs/specs/`
**When**: skill iterates scenarios to verify
**Then**: reads all 5 specs' scenarios; validates each SCEN block against execution evidence
**Evidence**: skill references discovery primitive; test with multi-spec fixture

## SCEN-122: discovery performance fast-path
**Given**: large repo (1000+ files) with no scenarios anywhere
**When**: PreToolUse Edit on any file fires
**Then**: `has_any_scenarios(cwd)` returns False in <5ms; hook returns allow without full glob
**Evidence**: perf benchmark asserts <5ms for empty-scenario case; lru_cache on discovery roots

## SCEN-123: migration audit tool detects secrets
**Given**: project with `.ralph/specs/{goal}/design/detailed-design.md` containing `API_KEY=sk-...` or `password=...`
**When**: `scripts/phase10-migration-audit.py` runs pre-commit
**Then**: stdout lists findings with file:line; exit=1; user must review before `git add .ralph/specs/`
**Evidence**: test with synthetic secret-containing spec; audit catches it

## SCEN-124: gitignore nested-override warning
**Given**: user has `.ralph/` ignored globally AND wants to track `.ralph/specs/`
**When**: Phase 10 migration guide referenced
**Then**: doc explicitly shows `!/.ralph/specs/` + `!/.ralph/specs/**` pattern + warns about nested `.gitignore` that can re-ignore descendants; provides verification command `git check-ignore -v .ralph/specs/x/scenarios/x.scenarios.md`
**Evidence**: migration doc grep confirms all three components present
