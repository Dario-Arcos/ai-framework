---
name: phase10
created_by: tech-lead
created_at: 2026-04-24T14:00:00Z
revised_at: 2026-04-25T00:00:00Z
revision_reason: User-authorized clean drop of legacy `.claude/scenarios/` migration enforcement. SCEN-103, 119, 123, 124 marked DROPPED — no migration guards, no audit tool, no migration doc. New scenarios author into spec folders from day one; legacy files (if any) become harmless artifacts the user removes manually. Active count drops from 27 → 23.
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

## SCEN-103: [DROPPED 2026-04-25] no migration enforcement for legacy path
User-authorized clean break. The discovery primitive simply does NOT scan `.claude/scenarios/`. Any legacy file there becomes an inert artifact the user removes manually. No `[SDD:MIGRATION_REQUIRED]` guard, no audit tooling, no migration doc. Phase 10 forward-only.

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
**Given**: a tracked scenario at any valid discovery root (explicit test cases: `.ralph/specs/auth/scenarios/auth.scenarios.md` AND `docs/specs/checkout/scenarios/checkout-flow.scenarios.md`)
**When**: Edit attempts mutation
**Then**: identical `[SDD:SCENARIO]` denial regardless of path depth
**Evidence**: parametrized test with 2 concrete paths

## SCEN-107: Bash sed/rm on nested scenario DENY
**Given**: a tracked scenario at `.ralph/specs/x/scenarios/x.scenarios.md`
**When**: `Bash({"command": "sed -i '' 's/a/b/' .ralph/specs/x/scenarios/x.scenarios.md"})`
**Then**: PreToolUse denies exit=2 with `[SDD:SCENARIO] Bash command modifies scenario files`
**Evidence**: Bash regex matches `.ralph/specs/*/scenarios/` pattern; live hook test

## SCEN-108: amend marker strict sibling-scoped, symlinks rejected
**Given**: an amend at `.ralph/specs/x/scenarios/.amends/x-<SHA>.marker` (same directory as scenario) + sop-reviewer invoked
**When**: Edit attempts content change on `.ralph/specs/x/scenarios/x.scenarios.md`
**Then**: Edit ALLOWED (marker honored). A marker placed at `.ralph/specs/.amends/` or `docs/.amends/` is NOT honored (strict sibling only — `rel.parent / ".amends"`). Symlinks anywhere under `.amends/` are rejected. Symlinked scenario files themselves are rejected at PreToolUse (pre-existing behavior retained).
**Evidence**: live hook test — 5 cases: sibling accept, parent-level reject, symlink-marker reject, symlink-scenario reject, regular rejection when no marker

## SCEN-109: telemetry records full nested file_path
**Given**: guard fires on nested path
**When**: `guard_triggered` event written to metrics.jsonl
**Then**: `file_path` field contains full absolute nested path
**Evidence**: metrics.jsonl parse confirms full path string

## SCEN-110: cheap integrity check before early-exit, session-cached
**Given**: any task-completed invocation in a repo that discovers ≥1 scenario
**When**: hook starts processing
**Then**: cheap integrity scan runs BEFORE `_has_source_edits` early-exit. Cheap = single `git ls-tree -r HEAD -- {root}` per discovery root, cached to `/tmp/sdd-discovery-{project_hash}-{sid}.json` with TTL 600s. Detects deleted/extra scenario files on disk vs HEAD.
**Evidence**: (a) monkeypatched test — tamper scenario → reject; (b) no tamper, admin task → cheap check returns clean, early-exit reached; (c) cache hit test — 2nd invocation within TTL does NOT re-run git subprocess

## SCEN-111: deletion detection in integrity gate
**Given**: a scenario was tracked at HEAD but removed from disk at TaskCompleted time
**When**: task-completed.py integrity check runs
**Then**: exit=2 `[SDD:SCENARIO] integrity — deleted: <rel-path>`
**Evidence**: test with `rm scenarios/X` before hook invocation; stderr assertion

## SCEN-112: untracked scenario rejected at completion (no sid allowlist, commit-before-all-completions)
**Given**: a scenario exists on disk but NOT tracked at HEAD
**When**: task-completed.py integrity check runs (ANY completion — leader's own task, teammate's task, admin task)
**Then**: exit=2 `[SDD:SCENARIO] integrity — untracked: <rel-path> (scenarios must be committed to parent branch BEFORE ANY completion; invoke Ralph Step 3.5 → commit → then proceed)`
**Evidence**: test with new untracked scenario in (a) teammate session, (b) leader session with admin task, (c) leader session with code task — all 3 rejected

## SCEN-113: [DROPPED v5] no admin/implementation classifier
Classification by `_has_source_edits` is bypassable via Bash-based source edits (Codex v4 finding). Path Z: drop the distinction. All tasks face the same gates. Friction is accepted; admin tasks invoke skill fast (no-op for clean state).

## SCEN-114: scenario-driven-development outputs spec-folder
**Given**: SKILL invoked with scenario name "auth"
**When**: skill produces its output
**Then**: file lives at `docs/specs/auth/scenarios/auth.scenarios.md` (non-Ralph mode detected by absence of `.ralph/config.sh`) OR `.ralph/specs/auth/scenarios/auth.scenarios.md` (Ralph mode detected by `.ralph/config.sh` presence)
**Evidence**: grep of SKILL.md confirms canonical path guidance; integration test with both modes

## SCEN-115: brainstorming skill outputs inside spec folder
**Given**: brainstorming skill invoked for goal "cart-redesign"
**When**: skill writes brainstorm artifact
**Then**: file lives at `docs/specs/cart-redesign/brainstorm.md` (non-Ralph) OR `.ralph/specs/cart-redesign/brainstorm.md` (Ralph mode)
**Evidence**: grep of SKILL.md confirms; artifact path reference aligned

## SCEN-116: ralph-orchestrator Step 3.5 new path + commit-before-spawn
**Given**: ralph-orchestrator at Step 3.5 for goal "auth-rewrite"
**When**: invokes scenario-driven-development
**Then**: produces `.ralph/specs/auth-rewrite/scenarios/auth-rewrite.scenarios.md` AND commits BEFORE Step 4 task generation AND before spawning teammates (explicit commit-before-anything contract)
**Evidence**: grep of SKILL.md confirms; no `.claude/scenarios/` references outside migration docs; SKILL explicitly states commit-before-spawn

## SCEN-117: sop-* chain references aligned
**Given**: sop-discovery, sop-planning, sop-task-generator, sop-code-assist, sop-reviewer
**When**: grep across all SOP SKILL.md files for scenario path references
**Then**: zero references to `.claude/scenarios/`; all use `{spec-root}/{spec}/scenarios/`
**Evidence**: grep returns empty for the old pattern outside migration docs

## SCEN-118: [DROPPED v5] no admin opt-IN bypass
All TaskUpdate(completed) calls require verification-before-completion (checked via project-scoped shared state, SCEN-128). No metadata-based bypass. No session-state-based bypass. Friction is intentional — it's the signal that work was verified.

## SCEN-119: [DROPPED 2026-04-25] superseded by SCEN-103 drop
Same rationale as SCEN-103 — no enforcement on legacy path. New scenarios author into spec folders from day one.

## SCEN-120: ai-framework self-suite still passes
**Given**: ai-framework repo post-Phase-10 migration
**When**: `python3 -m pytest hooks/ -q`
**Then**: stdout last line `1053 passed` or greater; no new failures
**Evidence**: full suite run output

## SCEN-121: verification-before-completion handles multi-spec discovery
**Given**: fixture repo at `hooks/test_fixtures/phase10_multi_spec/` with 3 specs in `.ralph/specs/` (auth, checkout, payment — each with one scenarios file containing 2 SCEN blocks) and 2 specs in `docs/specs/` (onboarding, admin-panel — each with one scenarios file containing 1 SCEN block)
**When**: test runs `scenario_files(fixture_root)` and iterates each result through `parse_scenarios()`
**Then**: returned list length == 5 (paths); total SCEN blocks parsed == 8 (3 specs × 2 + 2 specs × 1); each parse returns valid dict with `id`/`when`/`then` populated
**Evidence**: `hooks/test_scen_phase10_multi_spec.py::test_discovers_and_parses_all_specs` asserts exact counts; `grep` of `skills/verification-before-completion/SKILL.md` confirms the skill documents iterating `scenario_files(cwd)` (not the old `.claude/scenarios/` path)

## SCEN-122: discovery performance fast-path with benchmark baseline
**Given**: fixture at `hooks/test_fixtures/phase10_perf_empty/` — 2000 placeholder files (empty) under various paths, zero `*.scenarios.md` anywhere under `.ralph/specs/` or `docs/specs/` or any configured SCENARIO_DISCOVERY_ROOTS
**When**: `has_any_scenarios(fixture_root)` is invoked 100 times in a tight loop (measured via `time.perf_counter()`)
**Then**: returns False for every call. Median of 100 invocations ≤ 5 ms. Max ≤ 10 ms. Test command: `pytest hooks/test_scen_phase10_perf.py::test_has_any_scenarios_empty_perf -v`. Test asserts `median_ms <= 5 and max_ms <= 10`. Failure = regression.
**Evidence**: `hooks/test_scen_phase10_perf.py` fixture + explicit assertion; if CI variability causes flakes, the test xfails with `strict=False` and comment `tracked for root-cause` — do NOT relax thresholds

## SCEN-123: [DROPPED 2026-04-25] no migration audit tool
No migration → no audit. If users want to scan their own specs for secrets, that's a generic concern outside Phase 10 scope.

## SCEN-124: [DROPPED 2026-04-25] no migration documentation
No migration → no migration doc. The new layout is documented in skill SKILL.md files (Phase 10.4 scope) and in CHANGELOG (Phase 10.7 scope).

## SCEN-125: multiple specs with same scenario basename coexist (no false rejection)
**Given**: legitimate specs `auth/scenarios/auth.scenarios.md` AND `auth-redesign/scenarios/auth.scenarios.md` (both named `auth` within their own spec scope)
**When**: `scenario_files(cwd)` runs
**Then**: both paths returned (dedup by ABSOLUTE PATH only, not basename). If the user genuinely wants each file treated as a distinct scenario contract, this works. Telemetry event `discovery_same_basename_detected` emitted (info-level, not error) to surface potential confusion.
**Evidence**: test with 2 legit same-basename-different-spec fixtures → both discovered, no rejection, telemetry present

## SCEN-126: symlinks rejected at ALL discovery entry points
**Given**: 4 symlink vectors — (a) symlinked discovery root `.ralph/specs -> /tmp/specs`, (b) symlinked spec dir `.ralph/specs/auth -> /tmp/auth`, (c) symlinked scenarios dir `.ralph/specs/auth/scenarios -> /tmp/scenarios`, (d) symlinked scenario file `.ralph/specs/auth/scenarios/auth.scenarios.md -> /tmp/auth.md`
**When**: `scenario_files(cwd)` runs on each
**Then**: each symlink is SKIPPED at discovery with telemetry event `discovery_symlink_rejected` including the vector type; scenarios under the symlinked branch not discovered; `Path.is_symlink()` check applied BEFORE any glob iteration; migration doc lists all 4 vectors as unsupported
**Evidence**: test fixture parametrized over all 4 vectors; discovery returns empty for each; telemetry present with correct vector label

## SCEN-127: template config updated with SCENARIO_DISCOVERY_ROOTS
**Given**: `template/.claude.template/config.json.template`
**When**: grep for SCENARIO_DISCOVERY_ROOTS
**Then**: template includes commented default `"SCENARIO_DISCOVERY_ROOTS": [".ralph/specs", "docs/specs"]` AND example override comment
**Evidence**: grep asserts; new project `/project-init` produces config.json with the key

## SCEN-128: skill-invoked state project-scoped AND recorder allowlist extended (complete B1 fix)
Two mechanical changes together:

**Change 1**: `sdd-auto-test.py:192` PostToolUse Skill allowlist extended from `{sop-code-assist, sop-reviewer}` to `{sop-code-assist, sop-reviewer, verification-before-completion}`. Otherwise `verification-before-completion` invocation is NEVER recorded — the gate's check is unreachable.

**Change 1b (normalization, Codex v5 finding)**: `tool_input.skill` values arrive as either unqualified (`verification-before-completion`) or namespaced (`ai-framework:verification-before-completion`). Before the allowlist match, strip any `<plugin>:` prefix so the canonical unqualified key is both stored and consumed. Without this step, `Skill(skill="ai-framework:verification-before-completion")` invocations (what prompts recommend) fail to match the allowlist and no state is recorded.

**Change 2**: `skill_invoked_path(cwd, skill)` drops the `sid` parameter. File written at `/tmp/sdd-skill-{skill}-{project_hash}.json` (no sid). TTL 30 min via mtime.

**Propagation mechanism** (also requires Phase 10.4):
- `PROMPT_implementer.md` updated: "Before calling `TaskUpdate(status=completed)`, invoke `Skill(skill='ai-framework:verification-before-completion')` in YOUR session"
- `PROMPT_reviewer.md` updated: same
- Leader's invocation in main session ALSO counts (project-scoped); if leader invokes before spawning teammates, teammates within 30 min TTL already inherit

**Given**: any session invokes `/ai-framework:verification-before-completion`
**When**: the hook PostToolUse records the skill
**Then**: file `/tmp/sdd-skill-verification-before-completion-{project_hash}.json` exists with mtime=now

**Given (read path)**: any session in same cwd calls `read_skill_invoked(cwd, "verification-before-completion")` within 30 min
**Then**: returns True

**Given (TTL expired)**: 31 min since last invocation
**Then**: `read_skill_invoked` returns False; TaskUpdate blocked; agent must re-invoke skill

**Evidence**: tests (a) skill invoke → file exists; (b) different session reads → True within TTL; (c) mtime>30min → False; (d) PROMPT_implementer.md grep confirms invocation instruction; (e) allowlist in sdd-auto-test.py grep confirms verification-before-completion present

## SCEN-129: template/gitignore.template Phase-10 aligned
**Given**: `template/gitignore.template` (distributed to downstream projects on install)
**When**: grep for ralph/scenarios/docs/specs rules
**Then**: template does NOT have legacy `!/.claude/scenarios/` (removed); DOES have `!/.ralph/specs/`, `!/.ralph/specs/**`, `!/docs/specs/`, `!/docs/specs/**`; does NOT have `.claude/scenarios/` legacy allowance; ephemeral Ralph state still ignored (`.ralph/config.sh`, `.ralph/metrics.json`, `.ralph/failures.json`, `.ralph/ABORT`)
**Evidence**: grep of template file asserts all changes; downstream new-project generation includes correct gitignore
