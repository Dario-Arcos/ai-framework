---
outline: 2
---

# Phase 9 Plan — Factory-grade autonomy without over-engineering

**Tech Lead**: Claude Opus 4.7 (Chief Engineer stewardship)
**Date authored**: 2026-04-21
**Baseline**: `fd7871b` (post-Phase-8.1)
**Mission alignment**: `/Users/dariarcos/G-Lab/IA-First-Development/prod/ai-framework` must deliver autonomous agentic workflows that a developer can trust — like factory.ai — without over-engineering, without accidents.

## 1. Mission (user-corrected statement)

> **Make the agentic workflow deliver high-quality outcomes without over-engineering, without accidents — that a developer can trust an automated software factory to this plugin as they'd trust factory.ai.**

Phase 8.1 closed three integrity holes that opened the door for quiet reward-hacking during autonomous runs. Phase 9 must close what still prevents a developer from sleeping while Ralph works overnight.

## 2. What factory.ai provides · what we provide today

| Missions primitive | Evidence factory.ai has it | Our state post-Phase-8.1 |
|---|---|---|
| validation-contract BEFORE code | `factory.ai/news/missions-architecture` (Apr 2026) | `.claude/scenarios/*.scenarios.md` authored Ralph Step 3.5; SCEN-011 SCEN-017 SCEN-018 write-once |
| Fresh-context validator at milestone | Theo Luan Apr 2026 deep dive | `/verification-before-completion` + worktree sub-agents |
| Black-box execution-grounded verification | StrongDM principles, Mar 2026 | Evidence field per SCEN; TaskCompleted real commands |
| Milestone full validation | Missions architecture | `task-completed.py` full suite + coverage + scenarios (SCEN-019 proves independence from cascade) |
| Worker writes session tests | Missions workflow | `record_file_edit(cwd, file_path, sid)`; Phase 8 Rung 1b |
| Orchestrator spawns fresh workers | Missions + Luan | Ralph + native EnterWorktree |
| Write-once holdout | factory.strongdm.ai | `sdd-test-guard.py` 5-guard defense |
| Circuit breaker + abort | Missions runtime | `teammate-idle.py` + `.ralph/ABORT` |
| Per-edit test scoping | Luan: "session-scoped impacted tests" | Phase 8 cascade (Rungs 1a/1b/2/3) |
| **Per-mission telemetry aggregation** | Luan: "every mission emits structured trace for review" | **MISSING** — events exist, no aggregator, no human-readable report |
| **Auto UI dogfood at milestone** | Luan: "validators exercise system as black box with screenshot + network evidence" | **MISSING** — `/dogfood` exists, manual invocation only |
| **Mechanical parent-branch scenarios enforcement** | Implicit: Missions authors contract BEFORE workers | **PARTIAL** — procedural only; teammate worktree first-writes slip past |

12/14 on the factory.ai alignment matrix since Phase 8. **Phase 9 closes the remaining 2** (aggregation + auto dogfood) **and the one partial** (worktree scenario first-write).

## 3. Mission gaps Phase 9 closes · in priority order

Four items. Each closes a concrete mission gap. Each is verifiable with red-green-mutation proof. Each ships independently. **Every item covers Ralph AND non-Ralph modes** — factory autonomy means the same contract applies whether a human drives interactively or a teammate runs overnight.

### 9.1 — Parent-branch scenarios: mechanical enforcement

**What**: Extend `sdd-test-guard.py` PreToolUse so first-write of a NEW `.claude/scenarios/*.scenarios.md` inside a teammate worktree is DENIED. Leader must author + commit on the parent branch; teammates inherit via branch checkout.

**Why this matters for the mission**: Autonomous Ralph spawns workers in worktrees. A worker that authors its own scenarios inside its worktree defeats the external holdout — the scenarios are no longer independent of the implementer. Today the enforcement is procedural (documented in Ralph SKILL.md Step 3.5). One forgotten step = compromised holdout. Factory-grade means mechanical.

**How** (concise):
- Worktree detection: `git rev-parse --show-toplevel` vs `git rev-parse --git-common-dir` resolve difference → we're in a worktree
- New-scenario detection: file path starts with `.claude/scenarios/` AND `git ls-files --error-unmatch {path}` returns non-zero (untracked) AND tool is Edit/Write/MultiEdit/NotebookEdit
- Block condition: worktree context + new scenario file → deny with `[SDD:SCENARIO] parent-branch-only`
- Opt-out escape hatch: `.ralph/ABORT` present OR env `_SDD_DISABLE_SCENARIOS=1` (reuses existing bypass)

**Observable acceptance (SCEN-020)**:
- **Ralph mode**: writing NEW scenario file inside a teammate worktree → exit 2 with categorized prefix
- **Non-Ralph mode**: writing NEW scenario file on main clone (no worktree) → allowed (dev authors scenarios interactively, factory-compatible)
- Editing EXISTING scenario file in worktree → falls through to existing write-once guard (unchanged behavior)
- Bypass env `_SDD_DISABLE_SCENARIOS=1` → allows through with `scenarios_bypassed` telemetry (existing pattern)

**Files**: `hooks/sdd-test-guard.py` (+1 guard block, ~30 LOC), `hooks/test_scen_020.py` (new, 4-5 tests)

**Risk**: zero — additive guard, bypass escape hatch already plumbed, doesn't block legitimate parent-branch authorship.

### 9.2 — Mission observability: `/mission-report` + auto-aggregation

**What**: New skill `ai-framework:mission-report` that reads `.claude/metrics.jsonl` and emits one human-readable artifact per mission at `.ralph/mission-report-{timestamp}.md`. Auto-invoked at mission boundary (TeammateIdle circuit-open OR all tasks complete).

**Why this matters for the mission**: Today a dev wakes up to 30 commits and a metrics.jsonl they must parse with `jq`. That's not a factory — that's raw logs. A factory gives you a dashboard. Per Luan Apr 2026: "every mission emits a structured trace suitable for review". Without this, trust-by-observation is impossible.

**Report shape** (minimal, one page):
```markdown
# Mission {slug} · {timestamp}

## Convergence
- Scenarios satisfied: N/M
- Rounds to satisfaction (median): X
- Tasks completed: X/Y
- Teammates converged: X; circuit-open: Y

## Cascade efficiency (Phase 8)
- Rung 1a: X% (test file edits)
- Rung 1b: X% (source + session tests)
- Rung 2: X% (stack-native fallback)
- Rung 3: X% (full suite) ← forced_full_reason breakdown
- Mean per-edit cost: Xs

## Friction
- Top 5 retry patterns
- Scenarios that blocked more than once

## Evidence
- Commit range: {first..last}
- Files changed: N
- Test suite at end: X passed / Y failed
```

**How** (concise):
- Skill reads `.claude/metrics.jsonl` only (no network, no external deps, stdlib `json` + `collections`)
- Writes one file; that's the artifact
- Emits `mission_report_generated` telemetry event with path for downstream consumers
- **Ralph mode**: auto-invocation in `teammate-idle.py` when circuit opens OR Ralph end-of-mission marker detected; report lands at `.ralph/mission-report-{ts}.md`
- **Non-Ralph mode**: no auto-trigger (no mission boundary); dev invokes `/ai-framework:mission-report` manually; report lands at `.claude/mission-report-{ts}.md`
- Same aggregator serves both — only the trigger and output path differ

**Observable acceptance (SCEN-021)**:
- Given seed metrics.jsonl with mixed events → report contains all required sections with correct counts
- Given empty metrics → report notes "no events recorded" instead of crashing
- Given malformed event line → skips and notes parse error; doesn't crash
- Auto-invocation on TeammateIdle circuit-open → report file appears in `.ralph/`

**Files**: `skills/mission-report/SKILL.md` (~80 LOC), `skills/mission-report/scripts/aggregate.py` (~150 LOC stdlib only), `hooks/teammate-idle.py` (+~15 LOC trigger), `hooks/test_scen_021.py` (~8 tests)

**Risk**: low — pure reader, no mutations to existing state. Bounded by `.claude/metrics.jsonl` rotation (10MB × 3 rotations, already in place).

### 9.3 — Milestone UI validation: auto `/dogfood` when web project detected

**What**: `task-completed.py` detects web project signature (`package.json` + dep in `{react,vue,svelte,next,nuxt,astro,remix}`). When all code gates pass AND signature matches, signal that `/dogfood` should run as final milestone step. Dev opts out via `.claude/config.json: {"AUTO_DOGFOOD": false}`.

**Why this matters for the mission**: The current milestone gate validates code (tests, typecheck, build, coverage, scenarios). It does NOT validate runtime UI behavior — console errors, failed network requests, broken interactions. Factory.ai validators exercise the system as black box. For web projects, Phase 9 closes this gap by making `/dogfood` the last milestone step, not a skill the dev must remember to invoke.

**Scope discipline (no over-engineering)**:
- Only `/dogfood` + agent-browser. **NOT** `/bombadil` (local skill in testing, user-confirmed exclusion).
- Only when signature matches. Backend-only / CLI / library projects never trigger.
- Runs as signal, not gate: emits `milestone_dogfood_needed` signal into `.claude/metrics.jsonl`.
- **Ralph mode**: signal is surfaced in the next `/mission-report` as a checklist item; teammate cannot run `/dogfood` itself (no browser in worktree by design), so the mission report flags it as pending dev follow-up.
- **Non-Ralph mode**: signal is surfaced to the dev in-session via additionalContext; they invoke `/dogfood` when ready.
- Dev keeps manual `/dogfood` invocation always available; Phase 9.3 adds the default trigger, doesn't remove control.

**Observable acceptance (SCEN-022)**:
- Project with React in package.json + all gates pass → `milestone_dogfood_needed` event in metrics, report summary lists it
- Project with no web signature (e.g., pure Python library) → no signal, report omits section
- Project with web signature + `AUTO_DOGFOOD=false` → no signal, opt-out respected
- Project with web signature + failing code gate → no signal (gate blocked before dogfood consideration)

**Files**: `hooks/task-completed.py` (+~25 LOC signature detector + signal emitter), `hooks/_sdd_config.py` (+1 config key), `hooks/test_scen_022.py` (~6 tests)

**Risk**: low — signal-only, doesn't block completion. Dev retains veto via config.

### 9.4 — `task-completed.py` refactor: no deferred debt

**What**: Decompose the 251-LOC `main()` into named phase helpers and extract the 28-LOC coverage-demotion duplication between Ralph and non-Ralph branches. Zero behavior change — pure structural.

**Why this matters for the mission**: The mission includes "sin accidentes". Today a bug in coverage-demotion requires patching in two places; forgetting one = silent divergence between Ralph and non-Ralph. A 251-LOC function with 6 responsibilities is a cognitive trap when debugging an autonomous run that failed at milestone. "No deuda" is not aesthetic — it's safety under time pressure.

**Scope discipline (surgical, not ambitious)**:
- Extract `_coverage_gate(cwd, sid, scenarios_gated, ralph_ctx=None)` used by both Ralph and non-Ralph branches — collapses 28 LOC duplicate into one helper
- Extract phase helpers invoked by main(): `_gate_scenarios`, `_gate_test`, `_gate_typecheck`, `_gate_lint`, `_gate_build`, `_gate_coverage`, `_gate_verification`
- main() becomes a readable decision tree ≤100 LOC, each helper ≤60 LOC with single responsibility
- **No new behavior**: existing 1693-LOC `test_task_completed.py` must continue passing untouched. That IS the safety net for the refactor.

**Observable acceptance (SCEN-023)**:
- `test_task_completed.py` runs identically (zero test modifications; if any test fails, the refactor is wrong)
- `wc -l hooks/task-completed.py` main() ≤100 LOC (structural assertion)
- Coverage-demotion appears in exactly ONE location (grep-assertion)
- Phase helpers exist as named functions (import check)
- Ralph + non-Ralph `task_completed` telemetry events identical shape pre- and post-refactor (behavior preservation)

**Files**: `hooks/task-completed.py` (restructured, ~same LOC), `hooks/test_scen_023.py` (new, ~6 tests covering structural invariants)

**Risk**: MEDIUM — refactoring a gate-critical hook. Mitigation: the pre-existing 1693-LOC test file serves as the behavior-preservation oracle. Every refactor step verified against `pytest hooks/test_task_completed.py -v`. If any test breaks, revert.

## 4. Cross-cutting: project-init audit extension (no new skill)

**What**: Extend existing `skills/project-init/SKILL.md` to output a factory-readiness section in the generated rules files, not a separate skill.

**Content emitted** (only if data present; no hallucination):
- `.claude/scenarios/` exists? How many scenario files?
- `.ralph/config.sh` present with GATE_* commands set?
- `FAST_PATH_ENABLED` in config?
- Coverage tool detected?

**Why this matters**: Users install the plugin, run `/project-init`, and don't know what a scenario is or why it matters. A short diagnostic section teaches the mental model by showing WHERE THEY STAND against the factory contract.

**Why it's not a new skill**: project-init already analyzes the project and writes rule files. Adding a section to its output is +30 LOC, zero new surface. New skills need justification; extensions don't.

**Observable acceptance**: project with existing `.claude/scenarios/` and `.ralph/config.sh` gets a readiness section citing those files; fresh project gets a section showing what's missing.

**Files**: `skills/project-init/references/analysis-layers.md` (+1 layer), no new files.

## 5. Deferred to Phase 10+ · with explicit reasoning

Items the mission eventually needs that I am NOT shipping in Phase 9, with why-not:

| Deferred | Why not now |
|---|---|
| Default FAST_PATH flip review after 30d telemetry | We don't have 30d of telemetry yet. Phase 9.2 enables the collection; review belongs to a later data-informed phase. |
| Scenario quality validator (semantic) — reject vague Evidence fields | Current structural validator catches absence. Semantic validation requires LLM-as-judge inside hooks, which Phase 3 threat model rejects. Revisit when we have judge-outside-hook pattern. |
| Trajectory-level critic (multi-mission drift) | Requires corpus of real missions. We have zero in production. Shipping this now = speculation. Phase 10+ once we have 100+ missions logged. |
| Contrastive LLM-judge (TRACE Jan 2026) | Requires labeled hack-trajectory dataset. Out of single-project scope. If adopted, belongs in `/verification-before-completion` evolution, not hooks. |
| Formal specs / DSL (Lahiri Mar 2026 "Intent Formalization") | Scenarios sit deliberately at the lightweight rung. Moving up the spectrum is a separate design conversation, not an incremental ship. |
| Hodoscope-style unsupervised monitoring | Requires baseline trajectory corpus. Enterprise dashboard concern, not plugin layer. |

## 6. Execution sequence · one commit per scenario

**Order**: 9.1 → 9.4 (refactor first — cleaner base for 9.2/9.3 additions) → 9.2 → 9.3 → project-init extension. Each lands on main as atomic commit with red-green-mutation proof.

**Ordering rationale**: refactor BEFORE adding behavior. If I add 9.2/9.3 first and then refactor, I refactor around the additions which increases risk. Refactor the existing gate loop first, then additions plug into named helpers.

**Per-item commit discipline**:
1. Author SCEN test file first (fresh-context — I should NOT see the implementation during authorship per anti-eval-awareness)
2. Run SCEN → confirm RED
3. Implement
4. Run SCEN → confirm GREEN
5. `git stash` implementation → confirm RED restored (mutation proof)
6. `git stash pop` → confirm GREEN restored
7. Full suite regression check
8. Commit with the conventional format

**No bundling unless tests pair naturally** (9.1's matcher-like change is single-scope; 9.2 skill + hook trigger pair naturally; 9.3 detector + signal emitter pair naturally).

**Verification cadence**:
- Per commit: full suite green (1019+ → 1019+N)
- Per item: /verification-before-completion with fresh evidence
- End of Phase 9: mission-level adversarial probe (can I defeat each new guard?)

## 7. Release plan

| Milestone | Version | Contents |
|---|---|---|
| Phase 8.1 shipped (today) | unreleased, on main | 4 commits `2d69d7d..fd7871b` |
| Phase 9.1 + 9.4 | 2026.4.0 candidate | Phase 8 cascade + 8.1 integrity + worktree enforcement + task-completed refactor + SDD artifact docs |
| Phase 9.2 | 2026.4.1 | `/mission-report` skill + aggregation trigger |
| Phase 9.3 + project-init ext | 2026.4.2 | Auto dogfood signal + factory-readiness audit |

CalVer rationale:
- 2026.4.0: feature release consolidating Phase 8 cascade + 8.1 integrity + 9.1 mechanical holdout — the first factory-autonomy-trustable version
- 2026.4.1 / 4.2: incremental additions that improve but don't alter the contract
- **No push to remote without explicit user authorization.**

## 8. Risk register · with mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Worktree detection false positive blocks legitimate main-repo authoring | High if it fires wrong | SCEN-020 covers main-repo-positive case; bypass env var exists |
| mission-report grows beyond one-page-fit when missions get long | Medium | Bounded sections; top-5 friction; older events trimmed via metrics.jsonl rotation already |
| Auto-dogfood triggers on CLI tool with React dev-dep | Medium | Signature requires dep + `scripts.test` / `scripts.dev` referencing dev server; opt-out via config |
| PreToolUse latency from added guard in 9.1 | Low | Single git subprocess (worktree detection cached per cwd); 5s budget preserved |
| Skill count growing (now 22 with mission-report) | Low | Each skill self-contained markdown; no runtime cost to presence, only at invocation |

## 9. Non-goals · explicit rejections

Listed so future Tech Leads can see what was deliberately chosen NOT to do:

- NOT building a web dashboard. Markdown artifact is sufficient and trivially grep-able.
- NOT streaming telemetry to an external service. Local-only fits Pragmatic threat model and removes dependency surface.
- NOT adding `/bombadil` auto-invocation (user-confirmed: local skill in testing).
- NOT writing new agents. The 6 existing review agents cover the quality integration surface.
- NOT adding `/mission-report` auto-invocation at every task completion (only at mission boundary). Per-task reports drown signal in noise.
- NOT changing the scenarios markdown format. External holdout integrity depends on stable contract; adding fields = version migration risk.

## 10. Success definition

Phase 9 is complete when:

1. Four SCEN files (020/021/022/023) green with red-green-mutation proof
2. Full suite ≥ 1045 passing (1019 baseline + ~26 new tests across the 4 items + project-init extension)
3. `test_task_completed.py` runs identically pre- and post-9.4 refactor (behavior preservation)
4. Ralph + non-Ralph parity verified per item (each SCEN includes both-mode cases)
5. Adversarial mission probe:
   - Worktree agent attempts new scenario authorship → DENIED (9.1)
   - Mission finishes → `.ralph/mission-report-{ts}.md` exists and lists every event category (9.2)
   - Web project finishes all gates → dogfood signal emitted in report (9.3)
   - `task-completed.py` main() ≤100 LOC and coverage-demotion in exactly ONE location (9.4)
6. `/ai-framework:project-init` run on a fresh repo emits factory-readiness section
7. 2026.4.0 candidate version bumped locally, awaiting user authorization to push

## 11. Tech Lead commitment

I own the outcome. If any Phase 9 item ships without red-green-mutation proof, I have failed the contract. If a shipped item blocks legitimate workflow, I fix it in the next commit. If a design decision looks right but feels wrong once in production, I revert rather than patch.

The purpose is not "Phase 9 done". The purpose is **a developer closes their laptop, Ralph runs overnight, and the next morning they see a concise mission report that makes them trust the factory worked**.

If the plan serves that, ship. If it doesn't, cut.

---

**End of plan. Awaits user review before execution.**
