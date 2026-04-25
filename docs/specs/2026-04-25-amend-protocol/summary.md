---
name: amend-protocol-v2-planning-summary
created_by: sop-planning
created_at: 2026-04-25T02:30:00Z
spec: docs/specs/2026-04-25-amend-protocol/design.md
contract: docs/specs/2026-04-25-amend-protocol/scenarios/amend-protocol-v2.scenarios.md
plan: docs/specs/2026-04-25-amend-protocol/implementation/plan.md
---

# Planning Summary — Amend Protocol v2 R3

**Date**: 2026-04-25
**Goal**: Land the four-gate amend protocol with adversarial judge isolation and Format R escalation, removing the agent-accessible env-var bypass that contradicted the factory.ai holdout principle. Turn the plugin from a "scenarios-must-not-change enforcer with a back door" into "scenarios evolve under controlled adversarial scrutiny via a single front door."

## Artifacts Created

| Artifact | Purpose |
|----------|---------|
| `design.md` | Technical design at R3 — 537 lines, 16 sections, 23 inline scenarios, three review iterations closed (R1 adversarial, R2 P0/P1, R3 strategic synthesis) |
| `scenarios/amend-protocol-v2.scenarios.md` | Machine-validated contract — 23 SCEN-201..223 blocks, parser-verified (0 errors, 0 warnings), discovered by `_sdd_scenarios.scenario_files()` |
| `implementation/plan.md` | Ordered 8-step implementation plan with file-structure map (6 NEW + 14 MODIFIED), per-step acceptance criteria mapped to SCENs, complexity estimates, rollout plan. Two review iterations closed all P0/P1 issues. |
| `implementation/summary.md` | This file |

Note: brainstorming flow produced design.md + scenarios directly without intermediate `rough-idea.md` / `idea-honing.md` / `research/` artifacts; the audit + brainstorming dialog took their place.

## Key Decisions

1. **Remove `_SDD_DISABLE_SCENARIOS=1` env-var bypass without replacement** — the variable was agent-accessible via Bash `export`, contradicting the factory.ai holdout principle. Three primitives already cover legitimate emergency cases: `git rm` of obsolete scenarios, `git commit --no-verify` for hotfix-without-validation (telemetry-logged), and Format R escalation for genuine scenario divergence.

2. **Four-gate amend protocol replaces the binary write-once-or-marker enforcement** — Gate 0 STALENESS (mechanical SHA comparison), Gate 1 EVIDENCE (three-class taxonomy with HMAC for class c), Gate 2 INVARIANT (adversarial judge agent, isolated context, hostile-reviewer prompt), Gate 3 REVERSIBILITY (diff-class heuristic with 30-line cap). Mechanical gates (0, 1, 3) are fast deterministic checks; only Gate 2 spawns an LLM. Judge runs with a fixed positional-substitution template in a separate Agent spawn — no proposer reasoning context — making cross-context manipulation cost-prohibitive.

3. **Co-located resolved-marker convention via sibling `.resolved.json` files** — leader writes resolution alongside the original proposal (`<stem>.resolved.json`), original proposal stays intact, cleanup deletes both files together when (mtime > 24h AND sibling exists). Unresolved proposals accumulate as a debt signal visible to the human.

4. **Ralph + non-Ralph mode parity preserved across the entire flow** — SCEN-223 enforces 4-case parametrized testing (`{ralph_mode} × {sdd-test-guard, task-completed}`); both modes use the same discovery primitive (`get_scenario_discovery_roots()`), the same gate logic, the same cleanup. Mode-specific differences (teammate STOP-after-2 in Ralph, inline `evaluate_amend_request` in non-Ralph) live in skill prompts, not in core enforcement.

5. **Implementation phasing: front door first, back door close second** — Steps 1-3 build the amend protocol (foundation, judge, sdd-test-guard integration), Step 4 removes the env-var bypass code paths atomically. The system is in a coherent dual-channel state if Steps 1-3 land and Step 4 stalls — no rollback needed before resuming.

## Complexity Estimate

| Dimension | Value |
|-----------|-------|
| **Overall complexity** | M-L (medium-to-large feature, well-scoped) |
| **Total duration** | 13-16 hours across 8 steps |
| **Risk Level** | Medium — Gate 2 judge spawn behavior with the actual Agent tool is the largest unknown; SCEN-204 safe-fail mitigates |
| **Step distribution** | 6 × M (~2-3h each), 2 × S (~1h each) |
| **File touches** | 6 NEW + 14 MODIFIED = 20 files |
| **Test coverage target** | 23/23 SCEN-201..223 satisfied via fresh `pytest hooks/ -q` runs |
| **Out-of-scope (deliberate)** | CHANGELOG.md (immutable), phase9-plan.md (historical), mission-report/aggregate.py (backward-compat for historical metrics.jsonl) |

## Recommended Next Steps

Three options for transitioning from plan to implementation:

**Option A — Full autonomous via Ralph** (recommended for overnight execution):
1. `/sop-task-generator` converts each of the 8 plan steps into a `.code-task.md` file under `docs/specs/2026-04-25-amend-protocol/implementation/step*/task-*.code-task.md`
2. `/ralph-orchestrator` runs the 8 tasks with leader-supervised teammate execution
3. Each teammate executes one task via `/sop-code-assist`; scenarios validate via `/scenario-driven-development`; verification via `/verification-before-completion`
4. Mission report at end via `/mission-report`

**Option B — Interactive per-step**:
1. `/sop-task-generator` for the .code-task.md files (same as A)
2. Manual invocation of `/sop-code-assist` per step, in user-paced sequence
3. PR readiness via `/pull-request` after all 8 steps land

**Option C — Pause for human review of plan + summary first**:
1. User reviews `design.md`, `scenarios/amend-protocol-v2.scenarios.md`, and `implementation/plan.md` end-to-end
2. Surface any concerns before generating .code-task.md files
3. Then proceed with A or B

## Open Questions Deferred

These were marked as open in design.md and remain for the implementer to resolve during execution (none block planning):

1. Judge agent timeout (60s default) — make configurable via `.claude/config.json` if hardcoded becomes inflexible during Step 2
2. Schema enforcement representation (dataclass vs Pydantic vs jsonschema) — Step 1 implementer's call; design is implementation-agnostic
3. Gate 3 30-line cap — hardcoded constant per spec; revisit only if real cases hit it
4. HMAC key rotation cadence — per-session by default; revisit if proposals must outlive sessions

## Suggested Skill Transitions

| Current state | Next skill |
|---------------|------------|
| Plan approved, ready for tasks | `/sop-task-generator` |
| Tasks generated, ready for code | `/sop-code-assist` (interactive) or `/ralph-orchestrator` (autonomous) |
| All 8 steps complete, ready for PR | `/verification-before-completion` then `/pull-request` |
| PR merged | `/branch-cleanup` then `/mission-report` |
