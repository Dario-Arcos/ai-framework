---
outline: 2
---

# Phase 10 — Scenarios-in-Specs + Enforcement Refinement

**Status**: READY FOR IMPLEMENTATION 2026-04-24 · Plan v6 final after 5 Codex 5.5 xhigh reviews
**Owner**: Claude Opus 4.7 (Tech Lead)
**Supersedes**: prior Option A/B/C proposals and plan v1-v5
**Target release**: 2026.4.0
**Plan baseline commit**: `f1860e9` (plan v6c) — current HEAD is `f1860e9` OR LATER (future v6d, v7 may follow). Use `git log --grep="phase10" --oneline` to find the latest phase10 plan commit before starting.

---

## RESUME INSTRUCTIONS FOR A FRESH AGENT (READ FIRST)

**If you are a Claude Opus 4.7 Tech Lead with NO session context reading this file**: this document is self-sufficient to complete Phase 10. Read these THREE files, in order, before any other action:

1. **This file** (`docs/phase10-plan.md`) — mission, design decisions, phase breakdown, code map
2. **`.ralph/specs/phase10/scenarios/phase10.scenarios.md`** — the 27 active SCEN acceptance contracts (+ 2 DROPPED, explicitly marked)
3. **`docs/phase10-progress.md`** — durable progress ledger, one row per SCEN. Tells you what's done, what's mid-flight, what's next. Update it in the SAME commit that satisfies each SCEN.

Then follow this section end-to-end.

### What you need to know in 60 seconds

`ai-framework` is a Claude Code plugin. Its mission: factory.ai-grade anti-reward-hacking via scenario-driven development. Scenarios (`.scenarios.md` files) are write-once observable behavior contracts. Ralph orchestrator skill spawns parallel teammates (sub-agents via `Task(team_name=...)`) who implement tasks. The plugin's hooks enforce scenario immutability, integrity, and verification-before-completion.

Current state (pre-Phase-10):
- Scenarios live in `.claude/scenarios/*.scenarios.md` (flat, global — architecturally misaligned)
- 1053 passing pytest tests in `hooks/`
- Phase 9 delivered cascade routing (Rung 1a/1b/2/3), mission-report aggregator, auto-dogfood signal
- Cache path: `~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1/` — installed and active

Phase 10 goal: migrate scenarios to spec-folder architecture, fix 2 architectural enforcement holes (B1: skill-invoked state per-sid doesn't propagate leader→teammate; B2: bypass via Bash source edits), close ~29 issues identified across 5 Codex review rounds.

### Preflight (MUST RUN before writing code)

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /Users/dariarcos/G-Lab/IA-First-Development/prod/ai-framework

# 1. Latest plan commit is an ancestor of (or equal to) current HEAD
# Use -1 on git log itself to avoid SIGPIPE from `| head -1` under pipefail
LATEST_PLAN=$(git log -1 --format=%h --grep="^docs(phase10): plan")
[ -n "$LATEST_PLAN" ] || { echo "FAIL: no phase10 plan commit found"; exit 1; }
git merge-base --is-ancestor "$LATEST_PLAN" HEAD || { echo "FAIL: HEAD predates latest plan $LATEST_PLAN"; exit 1; }

# 2. Working tree clean except tolerable untracked docs/specs/ (which is a Phase 10 output directory that may be empty in fresh checkouts)
DIRTY=$(git status --short | grep -v "^?? docs/specs/$" || true)
[ -z "$DIRTY" ] || { echo "FAIL: working tree dirty:"; echo "$DIRTY"; exit 1; }

# 3. Tests pass with >=1053 passing (parsed, not tailed)
PYTEST_OUT=$(python3 -m pytest hooks/ -q 2>&1 | tail -1)
echo "$PYTEST_OUT"
PASSED=$(echo "$PYTEST_OUT" | grep -oE "[0-9]+ passed" | head -1 | awk '{print $1}')
[ -n "$PASSED" ] && [ "$PASSED" -ge 1053 ] || { echo "FAIL: expected >=1053 passed, got '$PASSED'"; exit 1; }

# 4. SCEN invariants (exact counts)
[ -f .ralph/specs/phase10/scenarios/phase10.scenarios.md ] || { echo "FAIL: scenarios file missing"; exit 1; }
SCEN_TOTAL=$(grep -c "^## SCEN-1" .ralph/specs/phase10/scenarios/phase10.scenarios.md)
SCEN_DROPPED=$(grep -c "\[DROPPED" .ralph/specs/phase10/scenarios/phase10.scenarios.md)
[ "$SCEN_TOTAL" = "29" ] || { echo "FAIL: expected 29 SCEN headings, got $SCEN_TOTAL"; exit 1; }
[ "$SCEN_DROPPED" = "2" ] || { echo "FAIL: expected 2 DROPPED markers, got $SCEN_DROPPED"; exit 1; }

echo "PREFLIGHT PASS — plan $LATEST_PLAN, $PASSED tests, $SCEN_TOTAL SCEN ($SCEN_DROPPED DROPPED)"
```

If ANY check fails: STOP. Either the environment was reset or the baseline is wrong. Do not proceed.

### Methodology (non-negotiable, enforced by CLAUDE.md)

1. **SDD**: every SCEN is red-green-refactor-mutation.
   - Write failing test first (red)
   - Implement minimum code to pass (green)
   - Refactor for clarity (keep green)
   - Revert implementation → test MUST go red (proves test is effective)
   - Restore → test green
2. **Per phase**: end with `pytest hooks/ -q` (1053+ passing, monotonic growth)
3. **Per phase**: Codex 5.5 xhigh review of `git diff {phase_start}..HEAD` — address P0/P1 before next phase
4. **Commits**: conventional format (`feat(hooks): ...`, `fix(hooks): ...`, etc.) — NEVER `--no-verify` unless probe-with-revert-in-same-session
5. **Scenarios already committed in `.ralph/specs/phase10/scenarios/phase10.scenarios.md`** — they are the contract. DO NOT modify them during implementation unless you ALSO write the amend marker via sop-reviewer.

### Phase sequence (implement IN ORDER, commit per sub-step)

| Phase | Scope | SCEN gated | Estimated |
|---|---|---|---|
| 10.1+10.2 (atomic) | Config-driven discovery primitive + hook path migration + legacy fail-closed + session-start update — MUST land together on one branch | 101, 102, 103, 104, 105, 106, 107, 108, 109, 119, 125, 126 | 5h |
| 10.3 | Cheap integrity gate BEFORE `_has_source_edits` early-exit (`task-completed.py` restructure) + discovery fast-path + `/tmp/sdd-discovery-{project_hash}-{sid}.json` cache | 110, 111, 112, 122 | 2h |
| 10.4 | Skill alignment: brainstorming, SDD skill, ralph-orchestrator Step 3.5, sop-* chain, verification-before-completion canonical path refs, PROMPT_implementer/reviewer teammate skill invocation instructions | 114, 115, 116, 117, 121 | 3h |
| 10.5 | Path Z skill propagation: (a) extend `sdd-auto-test.py:192` allowlist with `verification-before-completion`; (b) drop sid from `skill_invoked_path`; (c) normalize `ai-framework:` prefix before allowlist match | 128 | 2h |
| 10.6 | Tests migration: ~100 LOC hardcoded `.claude/scenarios/` fixtures → discovery-based; full suite 1053+ | 120 | 2h |
| 10.7 | Migration tooling + docs: `scripts/phase10-migration-audit.py`, `docs/migration-to-phase10.md`, `template/.claude.template/config.json.template` + `template/gitignore.template` updates, CHANGELOG 2026.4.0 entry | 123, 124, 127, 129 | 2-3h |

Total effort estimate: 16-17h.

### Hard constraints (from `/Users/dariarcos/CLAUDE.md`)

- NEVER `git push` without explicit user authorization
- NEVER skip `/verification-before-completion` before any commit/completion claim
- NEVER deliver user-facing prose without `/humanizer` (changelogs, migration docs)
- NEVER use WebSearch/WebFetch directly — route through `/agent-browser`
- NEVER answer about external APIs from pre-training — use Context7 or `/agent-browser`
- NEVER execute multi-step work inline — TaskCreate + delegate to sub-agents
- NEVER modify context files (skills/, agents/, rules/, CLAUDE.md) without FIRST invoking `/context-engineering`
- NEVER start a task without defining observable scenarios — for Phase 10, scenarios are already in `.ralph/specs/phase10/scenarios/phase10.scenarios.md`
- WHEN context is long: re-read files before editing, re-execute before claiming done
- Language: Spanish user-facing · English code/commits/context files

### What was decided and WHY (chronological trail)

These are the non-obvious design decisions. A fresh agent must understand these to avoid re-litigating.

1. **Scenarios moved from `.claude/scenarios/` to `.ralph/specs/{goal}/scenarios/` (Ralph) or `docs/specs/{name}/scenarios/` (non-Ralph)**. Reason: factory.ai / StrongDM Factory co-locate validation contracts with their spec (design/plan/tasks in same folder). Flat global `.claude/scenarios/` = orphaned state. User explicitly authorized this architectural move 2026-04-24.

2. **NO backward-compat for `.claude/scenarios/`**. User authorized clean break. Legacy path must FAIL CLOSED at 4 points (SessionStart, PreToolUse, TaskUpdate, task-completed) via `legacy_scenarios_present(cwd)` helper. Silent migration is unacceptable.

3. **Admin/implementation classifier DROPPED (Path Z, plan v5)**. Earlier plan versions (v1-v4) attempted to distinguish admin tasks (docs only) from implementation (code) to reduce friction. Codex v4 identified that the classifier (`_has_source_edits`) is bypassable via Bash-based source edits — `cat > src/auth.py <<EOF` doesn't trigger `record_file_edit` because that's only called from PostToolUse on Edit/Write tools, not Bash. Path Z: drop the classifier, all tasks face same gate. Accepted friction: admin tasks also invoke `verification-before-completion` (fast no-op). SCEN-113, 118 marked DROPPED in the SCEN file.

4. **verification-before-completion mechanics (B1 fix)**: (a) `sdd-auto-test.py:192` PostToolUse Skill allowlist extends to include `verification-before-completion` (previously only recorded `sop-code-assist` + `sop-reviewer` — invocation was never captured). (b) `skill_invoked_path(cwd, skill)` drops `sid` parameter, file becomes per-project-hash with 30min mtime TTL. (c) Skill-name normalization: strip `ai-framework:` prefix before allowlist match because PROMPTs invoke `Skill(skill='ai-framework:verification-before-completion')` (namespaced) but allowlist matches unqualified. All three pieces MUST land together (Phase 10.5) — partial landing = broken enforcement.

5. **Phase 10.1 + 10.2 coupling**: discovery primitive alone (10.1) breaks hooks that still reference old paths. Must land with 10.2 (hook path migration) OR ship as two commits on same merge. Prefer atomic.

6. **Scenario IDs parser-compatible**: current regex `^SCEN-\d{3}$` in `hooks/_sdd_scenarios.py:42`. DO NOT use `SCEN-10-NNN` — use `SCEN-1NN` (3-digit). The plan and scenarios file already use the correct form.

7. **Gitignore un-ignore already committed** at `10f3597` — `.gitignore` has `!/.ralph/specs/**` and `!/docs/specs/**` so tracked specs work. Template file (`template/gitignore.template`) still needs the SAME updates in Phase 10.7 (user projects that adopt the plugin).

8. **Empirical evidence from Fase 0 decisive probe** (2026-04-24): `Task(team_name=X, subagent_type=general-purpose, NO isolation)` teammates share leader cwd AND hooks DO fire in their session (`PreToolUse sdd-test-guard` emits `[SDD:SCENARIO] scenario write-once violation` on teammate's Edit attempt). Telemetry confirmed: `guard_triggered` events in `.claude/metrics.jsonl` with teammate-timestamp. This means Phase 9 already protects against direct scenario edits by teammates. Phase 10 closes the remaining integrity gaps (deletion, untracked creation, Bash-based tampering of non-scenario source).

9. **Pitfalls to avoid**:
   - `Bash` commands that contain literal `.claude/scenarios/` WILL trip the guard even in diagnostic contexts. Construct paths via Python variables in subprocess calls, or use `_SDD_DISABLE_SCENARIOS=1` env for probe-only operations.
   - `TaskUpdate(completed)` policy gate fires when scenarios exist. To commit probe scenarios during experiments use `--no-verify` only with "probe, revert after" in commit message AND revert in the same session.
   - `git worktree` created by `Agent(isolation=worktree)` branches from OLD commits (release tag `bcfff25`), NOT current HEAD. Do not assume current commits are inherited. Use `Task(team_name=..., NO isolation)` for in-tree parallelism — teammates share leader branch.

### Verification cadence per phase

After each phase, in order:

```bash
# 1. Full suite
python3 -m pytest hooks/ -q | tail -3

# 2. Count new tests — monotonic growth expected
python3 -m pytest hooks/ -q 2>&1 | tail -1 | grep -oE "[0-9]+ passed"

# 3. Codex review
PHASE_START_COMMIT=<commit-before-this-phase>
git diff ${PHASE_START_COMMIT}..HEAD > /tmp/phase-review.patch
codex exec --model gpt-5.5 --config model_reasoning_effort=xhigh --sandbox read-only \
  "Review this Phase 10 diff for bugs, races, edge cases. Check against docs/phase10-plan.md and .ralph/specs/phase10/scenarios/phase10.scenarios.md SCEN contracts. Be brutal." < /tmp/phase-review.patch

# 4. Dogfood: manual probe of the specific SCEN just satisfied
# (e.g., for Phase 10.2 SCEN-105: feed PreToolUse Edit payload on a nested scenario path, expect [SDD:SCENARIO] denial)
```

Address any P0/P1 before next phase. Document mitigations in commit body.

### When Phase 10 is DONE

All of the following are true:
- 27 active SCEN satisfied with execution evidence (29 headings total in the SCEN file; SCEN-113 and SCEN-118 are explicitly DROPPED and do not count toward this total)
- `pytest hooks/ -q` = 1053+ passing (monotonic from start)
- `grep -rn "\.claude/scenarios/" hooks/ skills/ template/ | grep -v migration-to-phase10 | grep -v deprecation` = empty
- Codex 5.5 xhigh review of final diff clean (P0/P1 addressed)
- CHANGELOG 2026.4.0 entry humanized (invoke `/ai-framework:humanizer` after writing)
- `docs/migration-to-phase10.md` humanized
- User explicitly authorizes `npm version 2026.4.0` + push + tag

### Escape hatches

- If a phase reveals the plan is wrong: STOP implementation, update `docs/phase10-plan.md` + SCEN file, re-request Codex review, get user approval, resume
- If a test regression: immediately revert, diagnose (invoke `/ai-framework:systematic-debugging`), fix, commit separately from feature
- If a phase takes 3x estimate: flag to user, consider scope trim
- If locked/stuck: invoke `/brainstorming` or ask user directly

### Code Map — exact files + functions to edit per SCEN

| SCEN | Files to edit (current line refs) | Tests to write |
|---|---|---|
| 101, 102, 104 | `hooks/_sdd_config.py` (add `SCENARIO_DISCOVERY_ROOTS`, `SCENARIO_FILE_PATTERN`), `hooks/_sdd_scenarios.py:55-67` (rewrite `scenario_dir`/`scenario_files` glob-based) | `hooks/test_sdd_config_discovery.py` (NEW), `hooks/test_sdd_scenarios.py` (UPDATE — legacy path tests go red, replaced with discovery-based) |
| 103, 119 | `hooks/sdd-test-guard.py` (NEW `legacy_scenarios_present(cwd)` helper + call at PreToolUse Edit, Bash git commit, TaskUpdate), `hooks/task-completed.py:540-560` (call at TaskCompleted), `hooks/session-start.py:35-50` (call + emit `[SDD:MIGRATION_REQUIRED]`) | `hooks/test_scen_phase10_legacy.py` (NEW) — 4 enforcement points × fixture with legacy `.claude/scenarios/X.scenarios.md` |
| 105, 106, 107, 108 | `hooks/sdd-test-guard.py:241-274` (`_rel_scenario_path` — verify nested paths resolve), `hooks/_sdd_scenarios.py:415-445` (amend marker resolver → strict sibling) | `hooks/test_scen_phase10_nested.py` (NEW) |
| 109 | `hooks/_sdd_state.py` telemetry writers (already record file_path; verify passthrough) | `hooks/test_scen_phase10_telemetry.py` (NEW) |
| 110, 111, 112 | `hooks/task-completed.py:529-599` (`_enforce_scenario_gate` split into `_enforce_scenario_integrity_cheap` + existing full verification), `hooks/_sdd_scenarios.py` (add batch `git ls-tree -r HEAD` helper, cache at `/tmp/sdd-discovery-{project_hash}-{sid}.json` TTL 600s) | `hooks/test_scen_phase10_integrity.py` (NEW) |
| 114, 115, 116, 117 | `skills/brainstorming/SKILL.md`, `skills/scenario-driven-development/SKILL.md`, `skills/ralph-orchestrator/SKILL.md:107, 147, 149`, all `skills/sop-*/SKILL.md` | `hooks/test_scen_phase10_docs.py` (NEW) — grep-based invariants |
| 120 | Run `python3 -m pytest hooks/ -q` after all prior phases | — (suite gate) |
| 121 | `skills/verification-before-completion/SKILL.md` (reference new discovery primitive) | `hooks/test_scen_phase10_multi_spec.py` (NEW) |
| 122 | `hooks/_sdd_scenarios.py` (add `has_any_scenarios(cwd)` fast-path + lru_cache) | `hooks/test_scen_phase10_perf.py` (NEW) — 2000-file fixture, <5ms median |
| 123 | `scripts/phase10-migration-audit.py` (NEW, ~150 LOC) | `hooks/test_phase10_migration_audit.py` (NEW) |
| 124 | `docs/migration-to-phase10.md` (NEW) | grep-based test in `hooks/test_scen_phase10_docs.py` |
| 125 | `hooks/_sdd_scenarios.py:scenario_files` (dedup by abs-path, NOT basename; emit telemetry on duplicate basename) | `hooks/test_scen_phase10_nested.py` (extend) |
| 126 | `hooks/_sdd_scenarios.py:scenario_files` (4 symlink vectors — check each entry with `Path.is_symlink()` before descending) | `hooks/test_scen_phase10_symlink.py` (NEW) |
| 127 | `template/.claude.template/config.json.template` | grep-based test |
| 128 | `hooks/sdd-auto-test.py:192-196` (extend allowlist + normalize `ai-framework:` prefix), `hooks/_sdd_state.py:655-680` (`skill_invoked_path(cwd, skill)` drop sid), `skills/ralph-orchestrator/scripts/PROMPT_implementer.md` + `PROMPT_reviewer.md` (add skill invocation instruction) | `hooks/test_scen_phase10_skill_propagation.py` (NEW) |
| 129 | `template/gitignore.template` | grep-based test |

### Grep exclusions reference (CANONICAL — use this exact command)

After Phase 10 complete, the command below MUST return zero matches.

Allowed files for legacy references (annotated as migration/deprecation documentation):
- `docs/migration-to-phase10.md` (user-facing migration guide)
- `CHANGELOG.md` (version history)
- `hooks/sdd-test-guard.py` — only inside `legacy_scenarios_present()` helper and the enforcement messages
- `hooks/session-start.py` — only inside CRITICAL_GITIGNORE_RULES comments marking legacy rule as removed
- `hooks/task-completed.py` — only inside `legacy_scenarios_present()` call site

```bash
matches=$(grep -rn "\.claude/scenarios" hooks/ skills/ template/ .claude/ scripts/ docs/ \
  --include="*.py" --include="*.md" --include="*.template" --include="*.json" \
  --exclude-dir="__pycache__" 2>/dev/null \
  | grep -v "docs/migration-to-phase10\.md:" \
  | grep -v "^CHANGELOG\.md:" \
  | grep -v "legacy_scenarios_present" \
  | grep -vE "^hooks/(sdd-test-guard|session-start|task-completed)\.py:.*(MIGRATION_REQUIRED|legacy_scenarios_present|# legacy|# deprecated)" \
  || true)
test -z "$matches" && echo "GREP GATE PASS — no stale refs" || { echo "FAIL — stale refs:"; echo "$matches"; exit 1; }
```

Expected result: `GREP GATE PASS` + exit 0. Any match = stale reference to investigate before release.

---

## Historical review trail (APPENDIX — non-normative, SUPERSEDED)

> **DO NOT READ THIS FOR IMPLEMENTATION GUIDANCE.** Everything in this appendix documents older plan versions (v1-v5) that are now SUPERSEDED. Executable design lives ONLY in the **Resume Instructions** section at the top of this file and in **`.ralph/specs/phase10/scenarios/phase10.scenarios.md`**.
>
> **Specifically SUPERSEDED below** (do not grep these as specs):
> - Any mention of `_has_source_edits` as admin/implementation classifier → SUPERSEDED by Path Z (no classifier)
> - Any mention of `metadata.admin=true` or `metadata.codeTaskFile` → SUPERSEDED by Path Z (no metadata)
> - SCEN-125 "duplicate basename = REJECT" → SUPERSEDED by SCEN-125 "coexist + telemetry"
> - SCEN-126 "symlinked spec directory" only → SUPERSEDED by SCEN-126 "4 symlink vectors"
>
> Skip ahead to the next h2 heading if you are a fresh-context agent implementing Phase 10.

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

Revised 2026-04-24 post Codex 5.5 xhigh review. Full contract: `.ralph/specs/phase10/scenarios/phase10.scenarios.md`. **Canonical count: 29 SCEN headings total · 27 active · 2 DROPPED (SCEN-113, SCEN-118).** All other numeric mentions in this doc defer to this truth.

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
- **SCEN-113**: [DROPPED v5] — classifier was bypassable via Bash edits. Absorbed into SCEN-128 where all tasks face same gate.

### Category D — Skill alignment
- **SCEN-114**: scenario-driven-development outputs spec-folder
- **SCEN-115**: brainstorming outputs spec-folder
- **SCEN-116**: ralph-orchestrator Step 3.5 new path
- **SCEN-117**: sop-* chain references aligned

### Category E — Admin task friction (OPT-IN, fail-closed default)
- **SCEN-118**: [DROPPED v5] — metadata-based admin opt-IN was unsound (transport + Bash bypass). All TaskUpdate(completed) face same gate via SCEN-128.

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

- **SCEN-125**: legitimate duplicate scenario basenames across specs COEXIST (dedup by absolute path only, not basename); info-level telemetry `discovery_same_basename_detected`. No rejection.
- **SCEN-126**: symlinks rejected at ALL 4 discovery entry points — (a) symlinked discovery root, (b) symlinked spec directory, (c) symlinked scenarios/ directory, (d) symlinked scenario file — with `Path.is_symlink()` check BEFORE glob iteration and telemetry `discovery_symlink_rejected` including vector label
- **SCEN-127**: `template/.claude.template/config.json.template` includes SCENARIO_DISCOVERY_ROOTS

---

## Phase breakdown (7 phases, 12-16h wall-clock, ~12-15 atomic commits)

### Phase 10.0 — Plan + SDD scenario authorship (1-2h)

**Gate**: plan approved + scenarios written + committed

1. Commit this plan file (`docs/phase10-plan.md`) + scenarios file (`.ralph/specs/phase10/scenarios/phase10.scenarios.md`)
2. User reviews + approves plan via ExitPlanMode
3. Codex review of plan before Phase 10.1

### Phase 10.1+10.2 — Discovery primitive + hook migration (ATOMIC, 5h)

**These two phases MUST land together on a single feature branch before merge.** Phase 10.1 alone breaks enforcement because hooks still reference `.claude/scenarios/`. Split only for logical clarity below; ship as one branch with atomic merge (squash or fast-forward).

#### 10.1 sub-scope — Config-driven discovery primitive

**Commits**:
- `feat(hooks): _sdd_config SCENARIO_DISCOVERY_ROOTS + DISCOVERY_PATTERN` + `test_sdd_config_discovery`
- `refactor(hooks): _sdd_scenarios discovery glob-based, backward-compat fallback REMOVED`

**Gate**: all existing scenario tests either updated or explicitly skipped; new discovery tests green; SCEN-101, SCEN-102, SCEN-104 satisfied.

#### 10.2 sub-scope — Hook path migration + legacy fail-closed + session-start update

**Commits**:
- `refactor(hooks): sdd-test-guard path resolution for nested spec paths + symlink rejection` + tests
- `refactor(hooks): amend marker resolver strict sibling-scoped (rel.parent/.amends only)` + symlink rejection tests
- `feat(hooks): legacy_scenarios_present(cwd) helper + 4-point fail-closed enforcement (SessionStart, PreToolUse, TaskUpdate, TaskCompleted)`
- `refactor(hooks): session-start.py CRITICAL_GITIGNORE_RULES for Phase 10 — remove legacy !/.claude/scenarios/, add !/.ralph/specs/ !/.ralph/specs/** !/docs/specs/ !/docs/specs/**`

**Gate**: SCEN-103, 105, 106, 107, 108, 109, 119, 126 satisfied.

### Phase 10.3 — Integrity gate (Path Z aligned, 2-3h)

**Commits**:
- `feat(hooks): _enforce_scenario_integrity_cheap — deleted/extra/modified detection via git-HEAD diff`
- `fix(hooks): task-completed runs cheap integrity BEFORE _has_source_edits early-exit`

**Path Z alignment**: there is NO metadata-based classifier and NO admin/implementation split here. Phase 10.3 delivers ONE mechanism — the cheap integrity check — that runs before any early-exit. Full verification (scenarios shape + skill invocation) lives in the existing `_enforce_scenario_gate` and applies unconditionally when scenarios exist. Admin tasks pay the small cost of invoking `verification-before-completion` (the skill returns fast when there's nothing to verify).

- **Cheap check** (always runs first): disk path set diff against `git ls-tree -r HEAD -- {discovery_roots}`. Deleted → REJECT. Untracked scenario → REJECT (no sid allowlist; leader must commit before spawn).
- **Full verification** (unconditional when scenarios exist): existing `_enforce_scenario_gate` with project-scoped skill-invoked state from Phase 10.5.
- **Fast-path**: `has_any_scenarios(cwd)` lru_cached + disk cache at `/tmp/sdd-discovery-{project_hash}-{sid}.json` TTL 600s; returns False in <5ms for empty-scenario repos — integrity check short-circuits.

**Gate**: SCEN-110, 111, 112, 122 satisfied. (SCEN-113 is DROPPED — do not gate on it.)

### Phase 10.4 — Skill updates (3h)

**Commits**:
- `docs(skills): scenario-driven-development outputs spec-folder scenarios`
- `docs(skills): brainstorming outputs to {spec-root}/{name}/`
- `docs(skills): ralph-orchestrator Step 3.5 + templates updated`
- `docs(skills): sop-* chain references aligned`
- `docs(skills): verification-before-completion canonical path reference updated`

**Gate**: SCEN-114, 115, 116, 117, 121 satisfied (verified by grep + test_scen_phase10_docs.py fixture).

### Phase 10.5 — Skill invocation propagation (Path Z complete B1 fix) (2-3h)

**Commits**:
- `feat(hooks): sdd-auto-test Skill allowlist extended with verification-before-completion` — required so the invocation is actually recorded
- `refactor(hooks): skill_invoked_path drops sid parameter, state project-scoped, 30min TTL` — leader invocation inherited by teammates
- `docs(skills): PROMPT_implementer + PROMPT_reviewer instruct teammate to invoke /ai-framework:verification-before-completion before TaskUpdate(completed)` — close path Z

**NO classification**: admin/implementation distinction dropped (Codex v4 found Bash-based bypass). All tasks go through same gate. Accepted friction: admin tasks invoke the skill too (skill returns fast when no work to verify).

**Gate**: SCEN-128 satisfied (absorbs previously-separate SCEN-113, 118 which are now dropped).

### Phase 10.6 — Tests migration + full suite (2h)

**Commits**:
- `test(hooks): migrate all hardcoded .claude/scenarios/ to discovery-based fixtures`

**Gate**: `pytest hooks/ -q` → 1053+ passed (SCEN-120 satisfied).

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
- 27/27 active SCEN-1* scenarios satisfied with fresh execution evidence (SCEN-113 and SCEN-118 are DROPPED and not counted)
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
