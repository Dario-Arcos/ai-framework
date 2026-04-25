---
name: amend-protocol-v2-implementation
created_by: sop-planning
created_at: 2026-04-25T02:00:00Z
spec: docs/specs/2026-04-25-amend-protocol/design.md
contract: docs/specs/2026-04-25-amend-protocol/scenarios/amend-protocol-v2.scenarios.md
mode: interactive
---

# Implementation Plan — Amend Protocol v2 R3

## Goal

Land the four-gate amend protocol with adversarial judge isolation, Format R escalation to human, and the env-var bypass removal — as specified in `design.md` — satisfying the 23 SCEN-2NN observable scenarios committed to the contract file.

## Prerequisites

**P1 — Phase 10 finishing must land first** (separate work track, not in this plan).
The amend protocol's SKILL.md modifications (Steps 5-6 below) assume `scenario-driven-development` and `ralph-orchestrator` SKILL.md files already point to the new discovery roots (`.ralph/specs/{goal}/scenarios/`, `docs/specs/{name}/scenarios/`). If Phase 10 finishing has not landed when this plan begins, either (a) merge that work first, or (b) bundle the path-migration edits into Steps 5-6 of this plan with an explicit note in the commit.

**P2 — Test infrastructure**
- `hooks/_subprocess_harness.py::invoke_hook` exists and supports `env=` parameter (verified 2026-04-25)
- pytest with parametrize is the existing pattern (used in `test_scen_phase10_*` files)
- No new dependencies required; `hmac` and `hashlib` are stdlib

**P3 — Repository state**
- Branch: feature branch off `main` (recommended `feat/amend-protocol-v2`)
- HEAD: at or after commit `83bb207` (spec + scenarios committed)
- No uncommitted changes to files in the file-structure map below

## File Structure Map

Lock decomposition before writing tasks. Each file has one clear responsibility; files that change together live together.

| File | Status | Single Responsibility |
|------|--------|------------------------|
| `hooks/_amend_protocol.py` | NEW | Pure module: `evaluate_amend_request`, four gate functions (staleness, evidence, invariant, reversibility), evidence taxonomy validators (classes a/b/c with HMAC), proposal helpers (`write_proposal`, `read_proposals`, `mark_proposal_resolved`). Internal-only — never trusts caller-provided baseline content. |
| `agents/scenario-amend-judge.md` | NEW | Specialized adversarial judge agent definition. Hostile-reviewer prompt template with positional placeholder substitution. Receives only `(scenario_original, amend_proposed, evidence_artifact)` — no proposer context. |
| `hooks/test_scen_a23_envvar_parity.py` | NEW | Parametrized integration test — 4 cases over `(ralph_mode, hook) ∈ {True,False} × {sdd-test-guard, task-completed}` — asserting env-var has no effect across all modes/hooks. Includes inline `_count_event` helper. |
| `hooks/test_amend_protocol.py` | NEW | Unit tests for `_amend_protocol.py`. Exercises Gate 0 staleness, Gate 1 evidence taxonomy (classes a/b/c with HMAC), Gate 3 reversibility heuristic, premortem absence, template injection. Mocks Gate 2 judge spawn. Created in Step 1. |
| `hooks/test_amend_judge_integration.py` | NEW | Integration test for the adversarial judge agent. Captures the spawned agent's input prompt to assert SCEN-203 (no proposer context leakage) and SCEN-204 (spawn-failure safe-fail). Created in Step 2. |
| `tests/fixtures/format_r_skeleton.txt` | NEW | Golden-file template for Format R escalation message. Used by SCEN-211 assertion. |
| `hooks/sdd-test-guard.py` | MODIFIED | Two-pass change: (a) integrate `tool_input.amend_request` handling — if present, invoke `_amend_protocol.evaluate_amend_request` and respect verdict; if absent, current behavior (block); (b) remove env-var bypass code paths (`_BYPASS_ENV` constant, `_scenarios_bypass_active()`, `_record_bypass()` helpers, the bypass capture in `main()`, every `if not bypass_active and ...` guard branch). Add hook-enforced 2-attempt counter keyed by `(sid, scenario_rel)`. |
| `hooks/task-completed.py` | MODIFIED | Remove env-var bypass code path (the `if os.environ.get("_SDD_DISABLE_SCENARIOS") == "1": ...` block) including the `append_telemetry(..., "scenarios_bypassed", ...)` call. |
| `hooks/test_bypass_and_version.py` | MODIFIED | Remove `TestPhase7Bypass` class (8 tests). Retain `TestVersionDerivation` and other unrelated tests. |
| `hooks/test_real_world_scenarios.py` | MODIFIED | Remove `TestRealWorldSettingsJsonEnvBypass` class and its settings.json env-block delivery comment block. |
| `hooks/test_scen_020.py` | MODIFIED | Remove `test_worktree_bypass_env_honored` (lines 227-240) and the docstring claim at line 26 about bypass-env honored in both contexts. |
| `hooks/session-start.py` | MODIFIED | Add cleanup logic for resolved amend proposals: scan `.ralph/specs/*/scenarios/amend-proposals/`, delete BOTH `<stem>.json` and `<stem>.resolved.json` only when (proposal mtime > 24h AND sibling `.resolved.json` exists). Idempotent; no error if directory missing. |
| `skills/scenario-driven-development/SKILL.md` | MODIFIED | Document `amend_request` shape (5-field with structured `evidence_artifact`), pre-mortem format with good/bad examples, "what worries me" examples, STOP-after-2 protocol guidance. |
| `skills/ralph-orchestrator/SKILL.md` | MODIFIED | New "Amend proposals" section explaining the leader's supervision loop reads `.ralph/specs/{goal}/amend-proposals/`. |
| `skills/ralph-orchestrator/scripts/PROMPT_implementer.md` | MODIFIED | Teammate STOP-after-2 protocol; how to write amend proposal; `blocked-pending-amend` task state. Mandatory `Skill(skill='ai-framework:verification-before-completion')` invocation before TaskUpdate(completed). |
| `skills/ralph-orchestrator/scripts/PROMPT_reviewer.md` | MODIFIED | Same as implementer. |
| `docs/migration-to-scenarios.md` | MODIFIED | Remove rollback step 3 ("Reserved emergency bypass: `_SDD_DISABLE_SCENARIOS=1`...", lines 48-60). Replace with three-sentence pointer to: amend protocol Format R for scenario divergence, `git commit --no-verify` for hotfix-without-validation, `git rm` for obsolete scenarios. |
| `skills/ralph-orchestrator/references/quality-gates.md` | MODIFIED | Parallel to migration-to-scenarios.md. Remove rollback step 3 + remove citation table row 10 referencing the env-var key. |
| `docs/phase10-plan.md` | MODIFIED | Remove bypass recommendation at line 140 ("...or use `_SDD_DISABLE_SCENARIOS=1` env for probe-only operations"). The surrounding `.claude/scenarios/` pitfall block is also stale post-Phase-10; review and trim. |
| `skills/mission-report/SKILL.md` | MODIFIED | Remove `scenarios_bypassed` mention in example aggregator output (line 71). New sessions emit zero such events. The aggregator script (`scripts/aggregate.py`) is left UNCHANGED for backward-compat with historical `metrics.jsonl` logs (Out of scope per spec). |

**Total**: 6 NEW + 14 MODIFIED.

**Out of scope** (per spec):
- `CHANGELOG.md` — historical entry left as immutable record (Keep a Changelog convention)
- `docs/phase9-plan.md` — historical record of fully-shipped phase
- `skills/mission-report/scripts/aggregate.py` — kept for historical-event backward-compat with pre-removal `metrics.jsonl`

## Implementation Steps

Each step follows SDD rhythm: scenarios already exist (committed contract) → write code that satisfies them → verify via fresh test run → refactor for clarity. No step creates "tests later"; scenarios precede code.

### Step 1 — Build amend-protocol foundation module (size: M)

Create `hooks/_amend_protocol.py` with:
- Schema validation for `amend_request` payload (5-field shape with structured `evidence_artifact`)
- Gate 0 (STALENESS): compares `base_head_sha` + `base_file_hash` against current git HEAD
- Gate 1 (EVIDENCE): three-class taxonomy validator (git_tracked_at_head / sandboxed_run_output / captured_command_output). Class (c) HMAC verification using stdlib `hmac` + `hashlib`. Per-session HMAC key derived from `project_hash + session_id`.
- Gate 3 (REVERSIBILITY): diff-class heuristic + 30-line cap. AST-light parser over unified diff.
- Pre-mortem absence check (rejects empty/whitespace before running gates)
- Template-injection check (pre-substitution regex against the four placeholders)
- Public entry: `evaluate_amend_request(cwd, scenario_rel, proposed_content, premortem, evidence_artifact, base_head_sha, base_file_hash) → AmendDecision`. ALL git reads happen INSIDE this module (`git show HEAD:<scenario_rel>` for invariant input, `git rev-parse HEAD` for staleness) — never trust caller-provided baseline.
- Proposal helpers: `write_proposal(cwd, goal, sid, payload) → path`, `read_proposals(cwd, goal) → list[Path]`, `mark_proposal_resolved(cwd, proposal_path, status, payload)` (writes sibling `<stem>.resolved.json`).

**Acceptance** (verifiable via fresh `pytest hooks/test_amend_protocol.py -v` run):
- SCEN-201: missing artifact → `failed_gate="evidence"`
- SCEN-202: path traversal → `failed_gate="evidence"` reason `escapes project root`
- SCEN-205: removed Evidence field diff → Gate 3 FAILS with `class_label="evidence_field_removed"`
- SCEN-206: 50+-line diff → Gate 3 FAILS with `class_label="diff_too_large"`
- SCEN-214: empty pre-mortem → `failed_gate="premortem"` BEFORE running Gates 1-3
- SCEN-216: stale `base_head_sha` → `failed_gate="staleness"`
- SCEN-217: template injection in `proposed_content` → `failed_gate="invariant_template_injection"`
- SCEN-218 (first half only): leader proposal mtime in same tick → defer-rejected via Gate 0 timestamp comparison. The "deferred tick → judge spawn mandatory" half lives in Step 6 (where the supervision tick spawns the judge).
- SCEN-220: class (a) untracked path → `failed_gate="evidence"` reason `class_a_path_not_tracked_at_head`
- SCEN-221: class (b) <30s idle → `failed_gate="evidence"` reason `class_b_idle_window_violation`
- SCEN-222: class (c) HMAC mismatch → `failed_gate="evidence"` reason `class_c_hmac_mismatch` + telemetry `evidence_hmac_failure`

Gate 2 (INVARIANT) is implemented as a stub here that is wired in Step 2; test contract for SCEN-203, 204 is satisfied AFTER Step 2 lands.

### Step 2 — Build adversarial judge agent + wire Gate 2 (size: S)

Create `agents/scenario-amend-judge.md` with:
- Frontmatter: `name`, `description`, `model: opus` (per CLAUDE.md sub-agent constraint)
- Single-purpose mission: judge the invariant gate ONLY
- Hostile-reviewer system prompt with FOUR positional placeholders (`{scenario_original}`, `{unified_diff}`, `{evidence_artifact_content}`, NEVER receives pre-mortem)
- Output format: `<verdict>|<reason>|<confidence>` parseable into `(PRESERVES_INVARIANT|ALTERS_INVARIANT, str, int)`

Wire Gate 2 in `hooks/_amend_protocol.py`:
- `evaluate_amend_request` spawns the judge via the `Agent` tool with isolation guarantees (no proposer context)
- 60s timeout; on spawn failure → `failed_gate="invariant", reason="judge unavailable"` (safe-fail)

**Acceptance**:
- SCEN-203: judge prompt contains ONLY scenario_original + diff + evidence content; NO pre-mortem text. Verifiable via integration test that captures the spawned agent's input prompt.
- SCEN-204: mocked spawn-failure → `approved=False, failed_gate="invariant"`. Never returns `approved=True` on judge failure.

### Step 3 — Integrate amend protocol into sdd-test-guard (size: M)

Modify `hooks/sdd-test-guard.py`:
- When scenario edit divergence detected (existing write-once guard logic), read `tool_input.amend_request`
- If present: call `_amend_protocol.evaluate_amend_request`, respect verdict (4/4 PASS → allow Edit + write amend marker; ANY FAIL → block + emit `amend_escalated` telemetry with Format R skeleton)
- If absent: current behavior (block edit) — preserves backward-compat
- Add 2-attempt counter: track `(sid, scenario_rel)` in session state; on attempt 3, block with stderr instructing amend proposal construction

**Acceptance**:
- SCEN-207: full happy path — amend marker written to `<scenario_parent>/.amends/{stem}-{HEAD_SHA}.marker` containing the seven-field marker block; `amend_autonomous` telemetry emitted with all four gate verdicts (staleness, evidence, invariant, reversibility) PASS.
- SCEN-219: 3rd attempt on same scenario blocks with stderr `[SDD:ATTEMPTS] amend-proposal required — 2 attempts exhausted on <scenario_rel>; construct amend_request, write to .ralph/specs/<goal>/amend-proposals/, end session`; `amend_attempts_exhausted` telemetry event emitted in `metrics.jsonl`; counter resets to zero ONLY when (a) a valid amend proposal is written for that scenario in the same session, OR (b) a new session starts (sid changes). Verifiable via integration test: drive 2 failing runs, assert hook blocks 3rd; then write proposal, assert counter resets and 1st post-proposal attempt is allowed.

### Step 4 — Remove env-var bypass code paths + tests (size: M)

This step closes the back door. Atomic with the new front door already in place (Steps 1-3 must land before this).

Modify `hooks/sdd-test-guard.py`:
- Delete `_BYPASS_ENV = "_SDD_DISABLE_SCENARIOS"` constant (line 41)
- Delete `_scenarios_bypass_active()` helper (lines 44-45)
- Delete `_record_bypass()` helper (lines 48-49)
- Delete bypass capture in `main()` (lines 522-526)
- Remove every `if not bypass_active and ...` guard prefix (write-once at line 538, bash-scenario-write at line 618, taskupdate-completion at line 632, bash-git-commit at lines 644-664) — leaving the unconditional check
- Update legacy `.claude/scenarios/` strings in error messages (lines 610, 624, 638, 651) to reference current discovery roots — minor doc fix

Modify `hooks/task-completed.py`:
- Delete `if os.environ.get("_SDD_DISABLE_SCENARIOS") == "1": ...` block (lines 542-544)

Modify `hooks/test_bypass_and_version.py`:
- Delete `TestPhase7Bypass` class entirely (8 tests). Retain `TestVersionDerivation`.

Modify `hooks/test_real_world_scenarios.py`:
- Delete `TestRealWorldSettingsJsonEnvBypass` class and its settings.json env-block delivery comment block.

Modify `hooks/test_scen_020.py`:
- Delete `test_worktree_bypass_env_honored` (lines 227-240) and update docstring at line 26.

Create `hooks/test_scen_a23_envvar_parity.py`:
- Parametrized over `(ralph_mode, hook) ∈ {True,False} × {sdd-test-guard, task-completed}` — 4 cases
- Inline `_count_event(metrics_path, event_name) → int` helper (no external dep)
- Per-case: build fixture repo with `git init` + tracked scenario at mode-correct path, invoke matching hook with `_SDD_DISABLE_SCENARIOS=1` env, assert `returncode==2` + hook-specific stderr substring + zero `scenarios_bypassed` events

**Acceptance**:
- SCEN-215: `grep -rn "_SDD_DISABLE_SCENARIOS" hooks/` returns empty (no production references); env var has no effect on either hook; zero `scenarios_bypassed` telemetry.
- SCEN-223: 4-case parametrized test passes (mode×hook parity).
- Full pytest suite green: `pytest hooks/ -q` → no regressions.

### Step 5 — Document amend protocol in skills (size: M)

Modify `skills/scenario-driven-development/SKILL.md`:
- Add "Amend protocol" section documenting the 5-field `amend_request` shape
- Pre-mortem format with good/bad examples (per design.md `## The pre-mortem` section)
- "What worries me most" examples
- Reference to amend-protocol-v2 spec for full context

Modify `skills/ralph-orchestrator/SKILL.md`:
- New "Amend proposals" section: leader's supervision loop reads `.ralph/specs/{goal}/amend-proposals/` each tick
- Document parallel-proposal first-write-wins via Gate 0 staleness

Modify `skills/ralph-orchestrator/scripts/PROMPT_implementer.md`:
- Teammate STOP-after-2 protocol with concrete steps
- Amend proposal writing instructions: file at `.ralph/specs/{goal}/amend-proposals/{sid}-{timestamp}.json` with five-field shape
- `blocked-pending-amend` task state on TaskUpdate
- Mandatory `Skill(skill='ai-framework:verification-before-completion')` before TaskUpdate(completed)

Modify `skills/ralph-orchestrator/scripts/PROMPT_reviewer.md`:
- Same as implementer (parity)

**Acceptance**:
- SCEN-208: grep of PROMPT_implementer.md confirms STOP instruction text
- SCEN-209: integration test simulates teammate hitting STOP; assert proposal file appears at correct path with five-field shape; assert `TaskUpdate(status="blocked-pending-amend")` was called; assert confession marker emitted

### Step 6 — Implement Ralph leader supervision loop + cleanup (size: M)

**Depends on**: Step 1 (`_amend_protocol.evaluate_amend_request`, `write_proposal`, `read_proposals`, `mark_proposal_resolved`); Step 2 (judge agent for Gate 2 spawn during supervision-tick processing).

Build leader-side handling in `skills/ralph-orchestrator/SKILL.md` + supporting code if needed:
- Each supervision tick: scan `amend-proposals/` for new `.json` files (no sibling `.resolved.json` yet)
- Process in filename order (timestamp ascending, first-write-wins via Gate 0)
- For each: invoke `_amend_protocol.evaluate_amend_request`
- AUTONOMOUS → apply Edit with `amend_request` in `tool_input` → guard accepts → write sibling `<stem>.resolved.json` with `{status: "resolved-autonomous", marker_path, resolved_at}` → re-spawn teammate or close task
- ESCALATE → pause mission → write Format R via mission-report → on resolution, write sibling with `{status: "resolved-human:approved|rejected", human_reasoning, resolved_at}`

Modify `hooks/session-start.py`:
- Add cleanup function: scan `.ralph/specs/*/scenarios/amend-proposals/` (and `docs/specs/*/scenarios/amend-proposals/` if used in non-Ralph)
- Delete BOTH `<stem>.json` and `<stem>.resolved.json` only when proposal mtime > 24h AND sibling exists
- Idempotent; no error if directory missing

**Acceptance**:
- SCEN-210: integration test seeds 3 proposals from terminated teammates; one supervision tick processes each; for each a sibling `.resolved.json` appears with correct status; original proposals intact
- SCEN-213: cleanup test parametrized over (a) processed+old → BOTH deleted, (b) unresolved+old → RETAINED, (c) recent → RETAINED; no exception if directory absent
- SCEN-218 (second half): integration test — leader writes proposal, immediately calls `evaluate_amend_request` → assert defer-rejected (Gate 0 mtime check); advance one tick interval (sleep or mtime patch); call `evaluate_amend_request` again → assert judge spawn was invoked even if heuristics suggested obvious approval (mandatory); proposer_role telemetry field is `"leader"`

### Step 7 — Telemetry + Format R golden file (size: S)

Verify all telemetry events from `## Telemetry` section of design.md emit correctly:
- `amend_proposed`, `amend_proposal_stale`, `amend_proposal_malformed`, `amend_autonomous`, `amend_escalated`, `amend_resolved_human`, `evidence_hmac_failure`

Create `tests/fixtures/format_r_skeleton.txt`:
- Golden file with the 11-field Format R structure (per design.md `## Format R` section)
- Field-name regex assertion target

Add tests asserting each telemetry event fires in its corresponding flow.

**Acceptance**:
- SCEN-211: golden-file test — non-Ralph escalation produces a message matching the skeleton (regex `^[A-Z_]+:` per line for top-level fields), `WHAT WORRIES ME MOST` non-empty, `JUDGE_CONFIDENCE` integer 0-100
- SCEN-212: after each amend flow, `metrics.jsonl` contains exactly one `amend_proposed` event always; PLUS one `amend_autonomous` event if the flow ended autonomously (4/4 gates passed); PLUS one `amend_escalated` event if any gate failed; PLUS one `amend_resolved_human` event if the human resolved an escalation. Verified by parametrized test over (autonomous-success, gate-fail-escalated, human-approved-after-escalate, human-rejected-after-escalate) flows; each flow grep-asserts the exact event count and event-type set in `metrics.jsonl`.

### Step 8 — Documentation cleanup (size: S)

Modify `docs/migration-to-scenarios.md`:
- Remove rollback step 3 (lines 48-60 — the env-var bypass section)
- Replace with three sentences: amend protocol Format R / `git commit --no-verify` / `git rm`

Modify `skills/ralph-orchestrator/references/quality-gates.md`:
- Parallel change to migration-to-scenarios.md
- Remove citation table row 10 referencing the env-var key

Modify `docs/phase10-plan.md`:
- Remove `_SDD_DISABLE_SCENARIOS=1` recommendation at line 140
- Review surrounding `.claude/scenarios/` pitfall block (already stale post-Phase-10) and trim

Modify `skills/mission-report/SKILL.md`:
- Remove `scenarios_bypassed` mention in example aggregator output (line 71)

**Acceptance**:
- `grep -rn "_SDD_DISABLE_SCENARIOS" docs/ skills/` returns ONLY references inside immutable historical contexts (CHANGELOG.md, phase9-plan.md, mission-report/scripts/aggregate.py)
- All four files compile (markdown valid) and render correctly in VitePress dev server (`npm run docs:dev`)

## Testing Strategy

**Unit tests** (per file):
- `hooks/test_amend_protocol.py` (NEW): exercises gates 0, 1, 3 + premortem absence + template injection. Mocks Gate 2 judge.
- `hooks/test_amend_judge_integration.py` (NEW): exercises Gate 2 spawn isolation (SCEN-203) and spawn-failure safe-fail (SCEN-204).
- `hooks/test_scen_a23_envvar_parity.py` (NEW): SCEN-223.

**Integration tests** (multi-component):
- Teammate STOP + proposal writing (SCEN-208, 209)
- Leader supervision processing (SCEN-210, 218)
- Cleanup loop (SCEN-213)
- Format R golden file (SCEN-211)
- Telemetry event sequences (SCEN-212)

**Regression**:
- Full `python3 -m pytest hooks/ -q` after every step → must remain green
- After Step 4: pytest must drop the deleted test class without errors (full suite still green)

**Manual verification**:
- VitePress build for docs changes: `npm run docs:build`
- `gh pr create` for PR readiness check
- Format R skeleton renders cleanly in terminal output

## Rollout Plan

**Branch strategy**:
- Feature branch `feat/amend-protocol-v2` off main
- One commit per step (8 commits total) — bisectable
- Squash-merge to main after PR approval

**Pre-merge checklist**:
- All 23 SCEN-201..223 satisfied (verified via `pytest hooks/ -q`)
- `/verification-before-completion` invoked with fresh evidence
- `/pull-request` skill (parallel code-reviewer + security-reviewer + edge-case-detector + performance-engineer) returns clean
- /humanizer pass on user-facing prose changes (SKILL.md sections)

**Monitoring**:
- Watch `.claude/metrics.jsonl` for `amend_*` events first 7 days post-merge
- Specifically: `evidence_hmac_failure` count should be 0 (P0 security signal)
- `amend_proposal_malformed` count <5/week is healthy; >20/week indicates skill-prompt drift

**Rollback**:
- Single revert of the squash-merge commit restores previous behavior
- Note: scenarios contract at `docs/specs/2026-04-25-amend-protocol/scenarios/` is independent of code rollback — the contract stays committed

## Complexity Estimate

| Step | Complexity | Estimated Duration |
|------|------------|-----|
| 1. Foundation module | M | 2-3h |
| 2. Judge agent + Gate 2 wire | S | 1-2h |
| 3. sdd-test-guard integration | M | 2h |
| 4. Bypass removal + tests | M | 2h |
| 5. Skills documentation | M | 2h |
| 6. Leader supervision + cleanup | M | 2-3h |
| 7. Telemetry + Format R golden | S | 1h |
| 8. Documentation cleanup | S | 1h |

**Overall**: M-L (8 steps, ~13-16h total)
**Risk Level**: Medium — Gate 2 judge spawn behavior with the actual Agent tool is the largest unknown; SCEN-204 safe-fail mitigates.

## Open Questions Deferred from Spec

These design-document open questions remain for the implementer to surface during implementation:

1. **Judge agent timeout**: spec proposes 60s. Step 2 should make this configurable via `.claude/config.json` if hardcoded becomes inflexible.
2. **Schema enforcement representation**: dataclass vs Pydantic vs jsonschema. Implementer decides during Step 1; design is implementation-agnostic.
3. **Gate 3 30-line cap**: hardcoded constant per spec. Revisit if real cases hit the cap.
4. **HMAC key rotation cadence**: per-session. Revisit if proposals must outlive sessions.

## Recommended Next Steps

1. User reviews this plan and approves (or requests revisions)
2. Plan-document-reviewer subagent dispatch (Step 7.5 of sop-planning) — runs after user approves
3. After plan approved: `/sop-task-generator` converts each step into a `.code-task.md` file
4. Implementation via `/sop-code-assist` (interactive per-step) or `/ralph-orchestrator` (autonomous overnight)
5. Each implementation run validates against scenarios via `/scenario-driven-development` cycle
6. PR readiness via `/verification-before-completion` + `/pull-request`
