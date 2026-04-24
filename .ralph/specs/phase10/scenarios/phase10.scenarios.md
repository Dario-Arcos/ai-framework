---
name: phase10
created_by: tech-lead
created_at: 2026-04-24T14:00:00Z
revised_at: 2026-04-24T14:30:00Z
revision_reason: Codex 5.5 xhigh v2 review — 7 of 10 findings still open + 4 new holes
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

## SCEN-103: legacy location fails closed at every enforcement point
**Given**: a file at `.claude/scenarios/legacy.scenarios.md`
**When**: ANY of — SessionStart, PreToolUse Edit, TaskUpdate(completed), or task-completed gate — runs
**Then**: exit=2 `[SDD:MIGRATION_REQUIRED]` with migration guidance; `scenario_files()` does NOT include legacy path; `legacy_scenarios_present(cwd)` helper returns True at ALL four enforcement points BEFORE any early-exit or scenarios-missing skip
**Evidence**: live hook test at each of the 4 points; exit code + stderr verbatim

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

## SCEN-113: full verification runs only on implementation tasks
**Given**: task with `tool_input.metadata.codeTaskFile` present (Ralph implementation task)
**When**: task-completed.py runs after cheap integrity passes
**Then**: full `_enforce_scenario_gate` runs (validates all scenarios + requires verification-before-completion skill invocation). For tasks WITHOUT codeTaskFile, full verification is skipped.
**Evidence**: test — implementation task without skill invocation → rejected with POLICY; admin task → full verification skipped

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

## SCEN-118: admin task opt-IN via tool_input.metadata (fail-closed default)
**Given**: a TaskUpdate call with `tool_input = {"status": "completed", "metadata": {"admin": true}}`
**When**: sdd-test-guard PreToolUse processes the tool_input
**Then**: policy gate SKIPS for this tool_input; exit=0
**Given (negative case)**: a TaskUpdate without `metadata.admin=true` (default absent, or `admin=false`)
**When**: TaskUpdate(completed) fires with scenarios present
**Then**: policy gate ENFORCES — exit=2 `[SDD:POLICY]` unless verification-before-completion invoked
**Transport**: hook reads `tool_input.metadata.admin` from the stdin JSON payload (`input_data["tool_input"]["metadata"]["admin"]`). NO external TaskGet call — purely payload-based.
**Evidence**: live probes — admin flag honored, missing flag fails closed, default fails closed

## SCEN-119: legacy .claude/scenarios/ blocks commit AND TaskUpdate
**Given**: project upgraded to 2026.4.0 with legacy `.claude/scenarios/X.scenarios.md` still present
**When**: user/agent attempts Bash(git commit) OR TaskUpdate(completed) OR task-completed gate runs
**Then**: exit=2 `[SDD:MIGRATION_REQUIRED] legacy .claude/scenarios/ detected — migrate to docs/specs/{name}/scenarios/ or .ralph/specs/{goal}/scenarios/ (see docs/migration-to-phase10.md)` — until migrated, no commits or completions proceed. Check runs in PreToolUse AND TaskCompleted (dual enforcement).
**Evidence**: live test with legacy fixture; all 3 enforcement points block

## SCEN-120: ai-framework self-suite still passes
**Given**: ai-framework repo post-Phase-10 migration
**When**: `python3 -m pytest hooks/ -q`
**Then**: stdout last line `1053 passed` or greater; no new failures
**Evidence**: full suite run output

## SCEN-121: verification-before-completion handles multi-spec discovery
**Given**: project with 3 active specs in `.ralph/specs/` (including `auth`, `checkout`, `payment`) and 2 in `docs/specs/` (including `onboarding`, `admin-panel`)
**When**: skill iterates scenarios to verify
**Then**: reads all 5 specs' scenarios; validates each SCEN block against execution evidence; reports per-spec satisfaction
**Evidence**: skill references discovery primitive; integration test with multi-spec fixture (5 concrete specs)

## SCEN-122: discovery performance fast-path with benchmark baseline
**Given**: fixture repo with 2000 files, zero scenarios in any discovery root
**When**: PreToolUse Edit on any file fires
**Then**: `has_any_scenarios(cwd)` returns False. Benchmark: median of 100 invocations < 5ms on CI hardware; hard cap 10ms. Test asserts against baseline; CI records for regression tracking.
**Evidence**: perf benchmark test with explicit fixture + baseline assertion

## SCEN-123: migration audit tool detects secrets via defined detector
**Given**: project with a `.ralph/specs/{goal}/design/detailed-design.md` containing any of — `API_KEY=sk-[0-9a-zA-Z]+`, `password=` followed by non-placeholder, `-----BEGIN (RSA|EC) PRIVATE KEY-----`, `AKIA[0-9A-Z]{16}`, high-entropy string ≥32 chars with base64/hex alphabet (entropy > 4.5 bits/char)
**When**: `scripts/phase10-migration-audit.py` runs
**Then**: stdout lists findings with `file:line:pattern`; exit=1 if ANY finding; supports `.migration-allowlist` for false positives (file-line suppressions with justification comment)
**Evidence**: test fixture with 5 secret types + 1 allowlisted false positive → audit catches 5, allows 1; test fixture with pure prose → exit=0

## SCEN-124: gitignore nested-override docs with verification command
**Given**: user has `.ralph/` ignored globally AND wants to track `.ralph/specs/`
**When**: user reads `docs/migration-to-phase10.md`
**Then**: doc explicitly shows `!/.ralph/specs/` + `!/.ralph/specs/**` AND warns about nested `.gitignore` that can re-ignore descendants AND provides verification command `git check-ignore -v .ralph/specs/x/scenarios/x.scenarios.md` with expected "file NOT ignored" output AND provides `session-start.py CRITICAL_GITIGNORE_RULES` update reference
**Evidence**: migration doc grep confirms all 4 components present

## SCEN-125: duplicate scenario name across specs rejected
**Given**: a scenario at `docs/specs/auth/scenarios/flow.scenarios.md` AND another at `.ralph/specs/auth-redesign/scenarios/flow.scenarios.md` (both named "flow")
**When**: `scenario_files(cwd)` runs
**Then**: exit=2 `[SDD:CONFLICT] duplicate scenario file name 'flow' across specs — rename to unique filename per spec` OR discovery returns both paths with conflict metadata allowing downstream hooks to reject. Implementation-wise: dedup is BY BASENAME, not by abs-path. Duplicates = error.
**Evidence**: test with 2 duplicate-name fixtures; discovery asserts error

## SCEN-126: symlinked spec directories rejected at discovery
**Given**: `.ralph/specs/auth` is a symlink pointing to `/tmp/external-spec`
**When**: `scenario_files(cwd)` runs
**Then**: symlinked spec directory is SKIPPED with telemetry event `discovery_symlink_rejected`; scenarios under it not discovered; migration doc explicitly lists symlinked specs as unsupported
**Evidence**: test fixture with symlinked spec dir; discovery returns empty for that branch; telemetry present

## SCEN-127: template config updated with SCENARIO_DISCOVERY_ROOTS
**Given**: `template/.claude.template/config.json.template`
**When**: grep for SCENARIO_DISCOVERY_ROOTS
**Then**: template includes commented default `"SCENARIO_DISCOVERY_ROOTS": [".ralph/specs", "docs/specs"]` AND example override comment
**Evidence**: grep asserts; new project `/project-init` produces config.json with the key
