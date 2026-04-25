---
name: amend-protocol-v2
created_by: brainstorming
created_at: 2026-04-25T00:00:00Z
revised_at: 2026-04-25T01:00:00Z
revision_reason: Removed `_SDD_DISABLE_SCENARIOS=1` env-var bypass. Audit revealed the var is agent-accessible via `Bash(export ...)` — violates factory.ai holdout principle ("validation contract stored outside codebase, not reachable by the agent under evaluation"). With the four-gate amend protocol providing a structured front door for legitimate divergence, the env-var back door has no remaining legitimate use. Replaced documented uses with: (a) amend protocol Format R for scenario divergence, (b) `git commit --no-verify` (already exists, telemetry-logged) for hotfix-without-validation, (c) `git rm` of obsolete scenarios. SCEN-215 reversed; risk row #9 reversed; mission paragraph adjusted; deliberate-rejections list extended; SCEN-223 added for Ralph/non-Ralph parity assertion. Previous revision (R2) findings preserved in Review trail.
status: design-approved-pending-human-review
supersedes: amend marker protocol from Phase 3 (write-once + sop-reviewer marker)
---

# Amend Protocol v2 — Four Gates + Pre-mortem + Adversarial Judge

## Mission

Replace the binary block-or-marker amend protocol with a **decision algorithm** that lets an agent tech-lead authorize legitimate scenario amendments autonomously when evidence supports it, preserves the invariant when not, and escalates to the human only as a true last resort — with an argument honest enough that the human can decide in 30 seconds whether to approve. The four-gate protocol is the **sole** scenario-edit channel: the previous env-var escape valve (`_SDD_DISABLE_SCENARIOS`) is removed in this design because it was reachable by the agent under evaluation, contradicting the factory.ai holdout principle.

This is the load-bearing piece that turns the plugin from a "scenarios-must-not-change" enforcer into an **agentic software factory** where scenarios evolve under controlled adversarial scrutiny.

## Why this matters

The current protocol (write-once + amend marker signed by `sop-reviewer`) has three structural failures:

1. **Arbitrary authority** — `sop-reviewer` was selected without explicit criterion. Why that skill and not `verification-before-completion`, `sop-planning`, or a dedicated `scenario-amend-judge`? The choice is undocumented and undefended.
2. **Brittle hard block** — when an amend IS legitimate (the API really returns 201, the spec really evolved, an edge case really emerged), the guard blocks with no reasonable exit path. The agent loops, burns tokens, eventually defects via `_SDD_DISABLE_SCENARIOS=1` or stops.
3. **No human-in-the-loop with honest argument** — when an amend is genuinely uncertain, there's no canonical channel for the agent to present a radically honest case to the human and let the human be the final authority. The current path is either silent autonomous edit (gated by marker, opaque) or hard block (no escalation).

A semi-automated factory cannot ask the human about every edit (that's friction, not an escape valve). It also cannot let agents amend freely (that's reward hacking). The middle path is an **algorithm of decision** with adversarial scrutiny built in.

## Design principles

1. **Human is last resort, not first**. Asking the human is reserved for true uncertainty.
2. **Each gate is binary, mechanically verifiable, and auditable**. No fuzzy scores.
3. **Adversariality by isolation** — the agent that judges the invariant does NOT see the proposing agent's reasoning. It only sees (original, proposed, evidence).
4. **The pre-mortem is one sentence, not three** — enough to break the auto-justification loop without inflating tokens.
5. **The "what worries me most" field is the cognitive circuit breaker** — its absence or triviality is itself signal to the human.
6. **Teammates STOP after 2 attempts** — they propose and escalate to leader, never loop.
7. **YAGNI everything else** — no confidence scores, no role hierarchies, no per-mode configuration flags.

## Architecture

### Components (3 new, 13 modified)

| File | Status | Purpose |
|---|---|---|
| `hooks/_amend_protocol.py` | NEW (~280 LOC) | Pure module + on-disk proposal helpers. Single eval entry: `evaluate_amend_request(cwd, scenario_rel, proposed_content, premortem, evidence_artifact, base_head_sha, base_file_hash) → AmendDecision`. ALL git reads (`git show HEAD:<scenario_rel>` for invariant input, `git rev-parse HEAD` for staleness check) happen inside this module — NEVER trusts caller-provided baseline content. Also exports `write_proposal()` / `read_proposals()` / `mark_proposal_resolved()` so skills do not import each other. |
| `agents/scenario-amend-judge.md` | NEW | Specialized agent. ONE job: judge the invariant gate. Receives `(scenario_original, amend_proposed, evidence_artifact)` with NO prior reasoning context. Adversarial by isolation. |
| `hooks/test_scen_a23_envvar_parity.py` | NEW | Parametrized integration test asserting Ralph and non-Ralph modes both reject the env-var bypass identically. Replaces removed `TestPhase7Bypass` coverage with the inverted assertion (env var has no effect, no telemetry emitted). |
| `skills/scenario-driven-development/SKILL.md` | MODIFIED | Documents `amend_request` shape, pre-mortem examples, "what worries me" examples (good vs. bad), STOP-after-2 protocol. |
| `skills/ralph-orchestrator/SKILL.md` | MODIFIED | New "Amend proposals" section explaining leader's supervision loop reads `.ralph/specs/{goal}/amend-proposals/`. |
| `skills/ralph-orchestrator/scripts/PROMPT_implementer.md` | MODIFIED | Teammate STOP protocol + how to write amend proposal + `blocked-pending-amend` task state. |
| `skills/ralph-orchestrator/scripts/PROMPT_reviewer.md` | MODIFIED | Same as implementer. |
| `hooks/sdd-test-guard.py` | MODIFIED | (a) When detecting scenario edit divergence, read `tool_input.amend_request`; if present, invoke `evaluate_amend_request` and respect verdict; if absent, current behavior (block). (b) **REMOVE env-var bypass code path**: delete `_BYPASS_ENV` constant (line 41), `_scenarios_bypass_active()` helper (lines 44-45), `_record_bypass()` helper (lines 48-49), the bypass capture in `main()` (lines 522-526), and EVERY `if not bypass_active and ...` guard branch (write-once at line 538, bash-scenario-write at line 618, taskupdate-completion at line 632, bash-git-commit at lines 644-664). After removal: scenario guards run unconditionally; user-facing error messages also dropped legacy `.claude/scenarios/` strings (lines 610, 624, 638, 651) as part of Phase-10-finishing prerequisite — those are out of scope of this spec but tracked separately. |
| `hooks/task-completed.py` | MODIFIED | **REMOVE env-var bypass code path**: delete `if os.environ.get("_SDD_DISABLE_SCENARIOS") == "1": ...` block (lines 542-544) including the `append_telemetry(..., "scenarios_bypassed", ...)` call. After removal: `_enforce_scenario_gate()` runs unconditionally when scenarios are discovered. |
| `hooks/test_bypass_and_version.py` | MODIFIED | **REMOVE `TestPhase7Bypass` class** (8 tests covering bypass behavior). Coverage is replaced by SCEN-215 + SCEN-223 implementations which assert the inverted behavior. Retain `TestVersionDerivation` and any other unrelated tests in the file. |
| `hooks/test_real_world_scenarios.py` | MODIFIED | **REMOVE `TestRealWorldSettingsJsonEnvBypass` class** (and the comment-block referencing settings.json env block delivery). Coverage subsumed by SCEN-215. |
| `docs/migration-to-scenarios.md` | MODIFIED | **REMOVE rollback step 3** ("Reserved emergency bypass: `_SDD_DISABLE_SCENARIOS=1`...", lines 48-60). Replace with three sentences pointing to: amend protocol Format R for scenario divergence, `git commit --no-verify` for hotfix-without-validation, and the existing `git rm` deletion options (steps 1-2 unchanged). |
| `skills/ralph-orchestrator/references/quality-gates.md` | MODIFIED | **REMOVE rollback step 3** describing the env-var bypass (parallel to migration-to-scenarios.md). Same replacement language. Retain the citation table; remove row 10 referencing the env-var key. |
| `hooks/test_scen_020.py` | MODIFIED | **REMOVE `test_worktree_bypass_env_honored`** (lines 227-240) which actively asserts the env var allows worktree first-write. After bypass code is deleted from `sdd-test-guard.py`, the assertion inverts: bypass would be ignored and first-write would be denied. Test removal is mandatory; no replacement needed (worktree-first-write coverage already exists in `test_worktree_first_write_denied` and SCEN-020). Also remove the docstring claim at line 26 (`"3. Bypass env _SDD_DISABLE_SCENARIOS=1 honored in both contexts."`). |
| `docs/phase10-plan.md` | MODIFIED | **REMOVE bypass recommendation at line 140** ("Pitfalls to avoid: ... or use `_SDD_DISABLE_SCENARIOS=1` env for probe-only operations"). The recommendation post-removal would instruct future developers to set an inert env var. Also note: the surrounding pitfall about `.claude/scenarios/` is itself stale post-Phase-10-discovery-primitive (Phase 10 dropped enforcement on legacy path); the entire pitfall block at lines 138-141 should be reviewed and trimmed. |
| `skills/mission-report/SKILL.md` | MODIFIED | Remove the `scenarios_bypassed` mention in the example aggregator output documentation (line 71). New sessions never emit this event; including it as exemplar misleads users. The aggregator script itself (`scripts/aggregate.py`) is left UNCHANGED to preserve backward-compat with historical `metrics.jsonl` logs from pre-removal sessions — see Out of scope below. |

### Data flow

```
[Agent detects divergence]
  ↓ writes pre-mortem (1 sentence)
  ↓ collects evidence_artifact (path) — must satisfy evidence taxonomy (Gate 1)
  ↓ snapshots base_head_sha = current `git rev-parse HEAD`
  ↓ snapshots base_file_hash = sha256 of scenario file at HEAD
  ↓ constructs amend_request {premortem, evidence_artifact, proposed_content,
                              base_head_sha, base_file_hash}
  ↓
─── Mode branch ─────────────────────────────────────────────
RALPH (teammate):
  ↓ writes .ralph/specs/{goal}/amend-proposals/{teammate-sid}-{ts}.json
  ↓ TaskUpdate(blocked-pending-amend) + confession marker
  ↓ teammate session ENDS

  Leader's next supervision tick:
  ↓ reads new amend-proposals/
  ↓ for each: invokes evaluate_amend_request
  ↓ AUTONOMOUS → Edit with amend_request → guard accepts
  ↓ ESCALATE  → pause mission + write Format R to user via mission-report

NON-RALPH (main agent):
  ↓ inline: invokes evaluate_amend_request directly
  ↓ AUTONOMOUS → Edit with amend_request → guard accepts
  ↓ ESCALATE  → reply with Format R in agent's next message
─────────────────────────────────────────────────────────────
  ↓
[evaluate_amend_request — same in both modes]
  ↓ Gate 0 (STALENESS): base_head_sha == current HEAD AND base_file_hash matches
                        scenario at HEAD. If FAIL → return failed_gate="staleness",
                        forces re-propose with fresh baseline (no escalation).
  ↓ Gate 1 (EVIDENCE): evidence_artifact passes the EVIDENCE TAXONOMY
                       (git-tracked OR sandboxed-runs-dir OR captured-command-output).
  ↓ Gate 2 (INVARIANT): _amend_protocol.py reads scenario_original via
                        `git show HEAD:<scenario_rel>` itself (never trusts caller).
                        Spawn Agent(scenario-amend-judge) with FIXED template:
                        proposer-controlled fields are POSITIONAL VALUES, never
                        interpolated into instructions. Judge returns binary
                        verdict + self-confidence percentile.
  ↓ Gate 3 (REVERSIBILITY): diff heuristic — destructive change classes flagged.
                            EXPLICITLY: Gate 3 is necessary but NOT sufficient
                            for semantic safety; Gate 2 owns semantic judgment.
  ↓
4/4 PASS → autonomous amend marker { premortem, gate_verdicts, judge_confidence,
                                     gate_timings_ms, evidence_path,
                                     base_head_sha, base_file_hash } + telemetry
ANY FAIL → escalation with Format R + telemetry
```

## The four gates

### Gate 0 — STALENESS (added per F1)

**Question**: Has the scenario or HEAD moved since the proposal was constructed?

**Pass conditions**:
- `base_head_sha` in proposal equals `git rev-parse HEAD` at evaluation time
- `base_file_hash` in proposal equals the sha256 of the scenario at HEAD

**Fail behavior**: returns `failed_gate="staleness"`. This is NOT escalated to the human — it instructs the proposer (or the leader on the proposer's behalf) to re-propose with a fresh baseline. Telemetry: `amend_proposal_stale`.

**Why this matters**: between proposal write and leader supervision, another teammate may amend the same scenario, or a normal commit may advance HEAD. Without this gate, the leader could apply a stale proposed_content over a divergent baseline, silently undoing intervening work.

### Gate 1 — EVIDENCE

**Question**: Does an observable artifact exist that contradicts the current scenario, AND is that artifact non-trivial to forge?

**EVIDENCE TAXONOMY** (added per F4 — proposer must declare which class, and Gate 1 verifies):

The proposal carries `evidence_artifact = {path, class, metadata}` where `class` is one of three:

**Class (a) — `git_tracked_at_head`**: the artifact is a file tracked at `HEAD`. Verified by `git ls-files --error-unmatch <path>` + `git show HEAD:<path>` non-empty. Cannot be forged within the proposing session because the proposer cannot create a HEAD-tracked file without committing first (which itself triggers the verification gate).

**Class (b) — `sandboxed_run_output`**: artifact lives under `.ralph/runs/{sid}/` (or, in non-Ralph mode, `.claude/runs/{session-id}/`) AND its mtime predates the proposal write by ≥ one supervision cycle (default: 30 seconds). The path is constrained: `_amend_protocol.py` rejects evidence outside these prefixes. Forgery requires the proposer to write evidence, wait, then propose — observable in telemetry as a suspicious idle window.

**Class (c) — `captured_command_output`**: a JSON envelope at `path` containing `{argv: [...], exit_code: int, stdout_sha256: str, stderr_sha256: str, captured_at: ISO8601, captured_by: sid, raw_output_path: str}`. The envelope is signed with HMAC-SHA256 using a per-session key derived from `project_hash + session_id` (key never leaves `_amend_protocol.py`'s memory; rotated per session). Forgery requires extracting the session key, which requires code execution outside the protocol's sandbox.

**Pass conditions** (depend on class):
- (a): `git ls-files --error-unmatch <path>` succeeds AND `git show HEAD:<path>` non-empty
- (b): mtime ≥ 30s before proposal mtime AND path under approved prefix
- (c): HMAC verifies AND `raw_output_path` exists AND its sha256 matches the envelope claim

**Fail conditions** (any of):
- Class missing or unrecognized
- Class-specific check fails
- Path escapes project root
- Zero-byte raw output
- (c) only: HMAC mismatch (treated as P0 security event — `evidence_hmac_failure` telemetry)

**Why three classes**: a single check ("file exists") is theatre — the proposer can write the file 10s before. Three classes raise the cost of forgery: (a) requires a real commit, (b) requires patience plus path discipline, (c) requires breaking crypto. None are unbreakable, all raise the cost meaningfully without infrastructure.

**Implementation**: ~80 LOC including HMAC. `cryptography` is stdlib-adjacent (`hmac` + `hashlib` are both stdlib).

### Gate 2 — INVARIANT

**Question**: Does the proposed amendment preserve the original intent of the scenario?

**Authoritative input source (added per F3)**: `_amend_protocol.py` reads the scenario_original via `git show HEAD:<scenario_rel>` ITSELF. The proposer NEVER passes scenario_original as a parameter. This closes the judge-poisoning vector where a malicious proposer could supply a doctored "original" to make the diff appear trivial.

**Mechanism**: spawn `Agent(scenario-amend-judge)` with a FIXED template (added per F9):

```
You are a hostile reviewer. The scenario file you see below was a contract.
Someone wants to change it. Your job: decide if the proposed change preserves
the original intent (PRESERVES_INVARIANT) or alters it (ALTERS_INVARIANT).

You have NO context on who is proposing this or why. Assume the proposer is
wrong until the diff itself proves otherwise.

ORIGINAL SCENARIO (verbatim from git HEAD):
<scenario_original>

PROPOSED AMENDMENT (verbatim diff):
<unified_diff>

OBSERVABLE EVIDENCE (verbatim file content):
<evidence_artifact_content>

Return: PRESERVES_INVARIANT | ALTERS_INVARIANT, one-sentence justification,
and a self-confidence integer 0-100. Format: `<verdict>|<reason>|<confidence>`.
```

The four placeholder fields are POSITIONAL substitutions, never f-string interpolation. `_amend_protocol.py` validates that the proposer-controlled diff and evidence content do not contain template-injection sequences (`<scenario_original>`, etc.) before substituting; if they do, the proposal is rejected with `failed_gate="invariant_template_injection"`.

The judge receives **NO** context about:
- Who proposed the amend (teammate vs leader vs main agent)
- The proposing agent's reasoning or pre-mortem
- The conversation history that led to the proposal

**Why hostile-persona prompt + isolation (refined per F14)**: same model = correlated blind spots. The hostile-reviewer persona is the cheap-but-real adversariality knob. If we have multi-model availability later, judge can switch model — design supports this without code change (just config).

**Failure mode handling**: if the Agent tool spawn fails (no model available, timeout, etc.), Gate 2 FAILS by default → escalates to human. Safe-fail.

**Adversariality leakage check**: SCEN-203 + SCEN-217 together verify that (a) pre-mortem text never appears in judge prompt, (b) judge prompt is assembled from the fixed template not concatenation, (c) proposer-controlled fields are validated for template injection.

### Gate 3 — REVERSIBILITY

**Question**: If the human reviews this amend later and rejects it, can we revert with a trivial diff?

**Pass conditions** (heuristic on the diff):
- Change limited to `**Then**:` literal value (e.g., "200" → "201")
- Addition of a new SCEN block (additive, removable)
- Addition of an Evidence field where missing
- Wording clarification in `**When**:` that doesn't change semantic anchors

**Fail conditions** (destructive classes):
- SCEN-ID change or removal
- Removal of an Evidence field
- Removal of `**Given**:`, `**When**:`, or `**Then**:` field
- Removal of a SCEN block
- Frontmatter field removal (name, created_by, created_at)
- Diff > 30 lines (large changes are by definition not "trivially revertible")

**Implementation**: AST-light parser over the diff (pre/post markdown). ~70 LOC. Returns `(class_label, is_reversible)`.

**Important caveat (added per F6)**: Gate 3 is **necessary but not sufficient** for semantic safety. A 1-line diff like `**Then**: user logged in` → `**Then**: user not logged in` passes Gate 3's "small literal change in Then" rule but is semantically destructive. Gate 2 (invariant judge) is the load-bearing semantic check. Gate 3 catches structural destruction (field removal, large diffs) that the judge might miss because they look "obviously safe at the diff level". Both gates are required; neither is sufficient alone.

## The pre-mortem (one sentence)

**Format** (mandatory):
```
"El argumento más fuerte contra este amend es: <X>. Mi respuesta: <Y>."
```

**Good examples**:
- "Contra: este puede ser un bug en la API, no un cambio legítimo de contrato. Respuesta: el ticket TPM-401 documenta que 201 es la respuesta esperada post-resource-creation, y la API alineó su comportamiento con la spec, no al revés."
- "Contra: relajar el assertion de evidence puede esconder regresiones futuras. Respuesta: el campo Evidence original era 'audit log' que ya no existe en la nueva arquitectura; reemplazo con 'http response trace' que es estrictamente más observable."

**Bad examples** (reward-hacking signals):
- "Contra: nada significativo. Respuesta: esto es claramente correcto." → escalación recomendada (sin auto-refutación real)
- "Contra: podría haber edge cases. Respuesta: probablemente bien." → escalación (vague on both sides)

## The "what worries me most" field (escalation only)

When a gate fails and we escalate to the human via Format R, the agent MUST write 1-2 sentences in `WHAT WORRIES ME MOST`. This is **one of two** circuit breakers (refined per F14 + the reviewer's challenge to my original "cognitive circuit breaker" claim):

**Honest framing**: this field alone is self-report from a system optimized to produce text that satisfies reviewers. It is NOT a sufficient adversarial check on its own. It is paired with **mechanical signals** in Format R (judge_confidence, gate_timings_ms) that the agent cannot fabricate without lying about specific numbers — which is more visible to the human than fabricated prose.

**Acceptable**:
- "Que esté autorizando un amend que cubre un bug real en mi propio código y no en la API."
- "Que el judge haya fallado por ruido (ningún razonamiento estructural) y yo te esté pidiendo firma por una falla mecánica."
- "Nada — confidence ≥95% que esto es legítimo, pero la puerta de invariante falló y prefiero tu firma."

**Unacceptable** (treat as red flag for human reviewer):
- "Nada me preocupa." (without the "but X failed mechanically" qualifier)
- Generic worries unrelated to which gate failed
- Worries that contradict the mechanical signals (e.g., "I'm not worried" with `judge_confidence: 35`)

**Mechanical signal pairing**: the human reviewing Format R sees BOTH the prose AND the numbers. Mismatch (low confidence + "no worries", or high confidence + "many worries") is itself signal of model unreliability — independent of whether the amend is correct.

## Format R — escalation message to human

```
SCENARIO: <id> / <path>
DIVERGENCE: <one line, what disagrees with current scenario>
EVIDENCE: <absolute path to evidence_artifact> [class=<a|b|c>]
PROPOSED AMEND: <unified diff, ≤20 lines>
PUERTAS:
  0. Staleness:        <PASA|FALLA> — base SHA matches
  1. Evidencia:        <PASA|FALLA> — <reason in ≤1 line>
  2. Invariante:       <PASA|FALLA> — <judge verdict in ≤1 line>
  3. Reversibilidad:   <PASA|FALLA> — <change class>
JUDGE_CONFIDENCE: <0-100>
GATE_TIMINGS_MS: staleness=<n> evidence=<n> invariant=<n> reversibility=<n>
PRE-MORTEM: "El argumento más fuerte contra: <X>. Mi respuesta: <Y>."
WHAT WORRIES ME MOST: <1-2 sentences honest>
RECOMENDACIÓN: <ESCALADO porque puerta X falló | propuesta de acción alternativa>
```

Hard cap: ~280 words for the full message (slight increase per F8 to fit the mechanical signals). The human reviews in 30 seconds.

The 11-field shape (was 9 in v1, fixed per F8) is verified by golden-file test in SCEN-211.

## Mode-specific behavior

### Ralph mode

**Teammate detects divergence**:
1. Try to satisfy scenario as-is. **2 attempts max** — ENFORCED by hook (added per F5): `sdd-test-guard.py` increments an `amend_attempts` counter keyed by `(sid, scenario_rel)` on each failing test run touching that scenario. On attempt 3, the hook blocks the tool use and emits stderr instructing the teammate to construct an amend proposal. Convention is documented; enforcement is mechanical.
2. After 2 failed attempts (or hook-block on 3rd), suspect divergence. **STOP**. No third attempt.
3. Construct `amend_request` JSON with `{premortem, evidence_artifact, proposed_content, base_head_sha, base_file_hash}`.
4. Write to `.ralph/specs/{goal}/amend-proposals/{teammate-sid}-{timestamp}.json` via `_amend_protocol.write_proposal()` (skill calls into the hook module — no skill→skill imports per F10).
5. Emit confession marker: `> blocked: amend-required, proposal=<path>, reason=<one-line>`.
6. `TaskUpdate(status=blocked-pending-amend)`. End session.

**Leader-as-proposer rule (added per F2)**:
If the LEADER itself wants to propose an amend (not a teammate's proposal), the leader writes the proposal to `amend-proposals/leader-{timestamp}.json` AND the proposal is processed in the NEXT supervision tick (not the same tick), AND the judge spawn for Gate 2 is required (no skip). This prevents the leader-evaluates-its-own-proposal self-loop. Telemetry distinguishes `proposer_role: "leader" | "teammate"`.

**Leader's supervision loop**:
1. On every tick, scan `.ralph/specs/{goal}/amend-proposals/` for new files.
2. For each new proposal: invoke `evaluate_amend_request`.
3. AUTONOMOUS → apply via Edit with `amend_request` in `tool_input` → guard accepts → write a sibling resolution file `<proposal>.resolved.json` containing `{status: "resolved-autonomous", marker_path: <path>, resolved_at: <ISO8601>}` → re-spawn teammate or close task. The original proposal file is left intact; resolution is tracked as a sibling artifact.
4. ESCALATE → pause mission, write Format R to user via mission-report or live message → wait for human input → on resolution, write a sibling `<proposal>.resolved.json` containing `{status: "resolved-human:approved" | "resolved-human:rejected", human_reasoning: <text>, resolved_at: <ISO8601>}`. Original proposal still left intact.

**Cleanup (refined per F13)**: on SessionStart, delete BOTH `amend-proposals/{stem}.json` AND `amend-proposals/{stem}.resolved.json` only if (a) the original proposal's mtime > 24h AND (b) a sibling `{stem}.resolved.json` exists (proof of leader processing). Unprocessed proposals (no resolved sibling) are never auto-deleted regardless of age — they accumulate as a debt signal visible to the human.

**Parallel proposals (added per F7)**: when N teammates propose against the same scenario simultaneously, the leader processes them in filename order (timestamp ascending). The first to pass Gate 0 (staleness) wins; subsequent proposals fail Gate 0 (because the first amend advanced HEAD or file_hash) and are returned to their respective teammates as `amend_proposal_stale` so they can re-evaluate against the new baseline. First-write-wins is intentional; deadlocks are impossible because Gate 0 is a fast pre-check.

### Non-Ralph mode

Main agent (me, in this conversation) handles amend inline:
1. Detect divergence.
2. Write pre-mortem in working memory.
3. Invoke `evaluate_amend_request` directly (no proposal-on-disk).
4. AUTONOMOUS → apply Edit with `amend_request` in `tool_input` → continue.
5. ESCALATE → reply to user with Format R → await user decision.

No teammate STOP-after-2 protocol applies (no teammates). No proposal disk persistence (synchronous). Telemetry still recorded in `metrics.jsonl`.

## Telemetry

New event types in `.claude/metrics.jsonl` (refined per F11, F12):

```json
{"event": "amend_proposed",        "scenario": "<rel-path>", "proposer_sid": "<sid>", "proposer_role": "leader|teammate", "premortem": "<sentence>", "evidence_artifact": {"path": "<p>", "class": "git_tracked_at_head|sandboxed_run_output|captured_command_output"}}
{"event": "amend_proposal_stale",  "scenario": "<rel-path>", "proposer_sid": "<sid>", "base_head_sha": "<sha>", "current_head_sha": "<sha>"}
{"event": "amend_proposal_malformed","scenario": "<rel-path>", "proposer_sid": "<sid>", "violation": "missing_field|invalid_evidence_class|template_injection|hmac_failure"}
{"event": "amend_autonomous",      "scenario": "<rel-path>", "proposer_role": "leader|teammate", "gates": {"staleness": "PASS", "evidence": "PASS", "invariant": "PASS", "reversibility": "PASS"}, "judge_verdict": "<sentence>", "judge_confidence": <0-100>, "gate_timings_ms": {"staleness": 12, "evidence": 45, "invariant": 8200, "reversibility": 30}}
{"event": "amend_escalated",       "scenario": "<rel-path>", "failed_gate": "invariant|reversibility|evidence", "format_r_message": "<full text>", "what_worries": "<sentence>", "judge_confidence": <0-100>, "gate_timings_ms": {...}}
{"event": "amend_resolved_human",  "scenario": "<rel-path>", "decision": "approved|rejected", "human_reasoning": "<text>"}
{"event": "evidence_hmac_failure", "scenario": "<rel-path>", "proposer_sid": "<sid>", "envelope_path": "<p>"}
```

Mission-report aggregates: `Mission produced N amend proposals: M autonomous (avg judge confidence X%, avg gate-2 latency Y ms), K escalated (J human-approved, L human-rejected). S stale proposals re-evaluated. R proposals rejected as malformed. E HMAC failures (P0 security signal).`

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Model fakes passing the invariant gate | Judge agent in separate spawn with no proposer context — adversarial by isolation |
| Model fills "what worries me" with cosmetic concerns | SKILL.md documents good/bad examples; field must relate to which gate failed |
| Teammate loops infinitely without recognizing divergence | Hard 2-attempt limit in `PROMPT_implementer.md`; enforced by convention (hook cannot count attempts cheaply) |
| Amend proposals orphaned on disk if Ralph dies | SessionStart cleanup of proposals >24h old |
| Judge agent spawn fails (model unavailable) | Gate 2 FAILS by default → safe escalation |
| Reversibility heuristic misses a destructive class | Diff size cap (>30 lines) is the second line of defense; any large diff escalates regardless of class label |
| Format R becomes ceremonial | "What worries me" field cannot be meaningfully filled by reward-hacking model — it's the load-bearing element |
| `amend_request` payload is forgeable from outside the protocol | Documented as OPTIONAL field; its absence means current behavior (block). Presence requires the five-field shape (`{premortem, evidence_artifact, proposed_content, base_head_sha, base_file_hash}`); malformed proposals are rejected |
| Removal of `_SDD_DISABLE_SCENARIOS=1` leaves no agent-settable bypass | Human-explicit overrides retained: `git commit --no-verify` (telemetry-logged via stderr signal), Format R escalation through the amend protocol, and `git rm` of obsolete scenarios. All three leave artifacts in git or transcript — none are agent-settable without observable trace |

## What this design deliberately rejects

- **Confidence score numerics** (β model): theatre of precision, opaque, uncalibratable.
- **Three written counter-arguments inflated** (γ model): retoric without signal.
- **Graduated teammate roles** (junior vs senior amend authority): YAGNI.
- **Configurable mode flag for non-Ralph** (Z model from brainstorming): the algorithm is good or it isn't.
- **Quality scoring of seeds at authoring time**: separate concern, deferred to Phase 11.
- **LLM-as-judge for Gates 1, 2, and 3**: only Gate 2 needs LLM judgment. Gates 1 and 3 are mechanical. Gate 0 (STALENESS) is also mechanical and was never a candidate for LLM judgment.
- **Env-var bypass `_SDD_DISABLE_SCENARIOS=1`**: agent-accessible via Bash `export`, contradicts factory.ai holdout principle. The amend protocol provides the legitimate front door; `git --no-verify` and `git rm` cover residual emergency cases with observable artifacts. No back door remains.

## Out of scope (explicit)

- Cross-spec contradiction detection (different specs proposing contradictory amends to a shared concept).
- Versioning of scenarios across major refactors (a `SCEN_VERSION` field).
- Web UI for amend review (CLI/text only, by design).
- Voice/Slack integration for human escalation (terminal only).
- Auto-rollback when human rejects an amend (manual revert; the diff is small by Gate 3 design).
- `CHANGELOG.md:43` historical entry describing the env-var bypass as a delivered feature: left as immutable historical record per Keep a Changelog convention. Future entries describing this removal will appear in a new release section.
- `docs/phase9-plan.md:51,57` references to the env-var bypass: this is a historical plan document for a fully-shipped phase. Left as historical record. Phase 9 enforcement still works correctly because it relies on git worktree detection, not on the env var being honored.
- `skills/mission-report/scripts/aggregate.py` lines parsing `scenarios_bypassed` events: kept in code so that aggregating a `metrics.jsonl` file produced before this revision still works. New sessions emit zero such events; the counter will simply stay at 0. `hooks/test_scen_021.py` (which seeds a synthetic `scenarios_bypassed` event into a fixture to exercise the aggregator's historical-event path) stays green because the aggregator code is unchanged.

These are valid future work but not part of this design.

## Observable scenarios

Extracted from each accepted design decision. These become the input for `/scenario-driven-development`.

> **Canonical contract**: the machine-validated source of truth lives at `scenarios/amend-protocol-v2.scenarios.md` (sibling to this design.md, 23 SCEN-2NN blocks, parser-verified). The blocks below are reproduced for narrative continuity; on any divergence, the scenarios file is authoritative. Future amendments must follow the four-gate amend protocol described in this design (sibling `.amends/` markers, sop-reviewer signature for amend marker pre-protocol, or amend_request payload post-protocol).

### SCEN-201: Evidence gate — missing artifact rejected
**Given**: an `amend_request` with `evidence_artifact` pointing to a non-existent path
**When**: `evaluate_amend_request` runs
**Then**: returns `AmendDecision(approved=False, failed_gate="evidence", reason="artifact not found")`; no autonomous Edit; telemetry `amend_escalated` emitted
**Evidence**: hook unit test with synthetic missing path

### SCEN-202: Evidence gate — path traversal rejected
**Given**: an `amend_request` with `evidence_artifact = "/etc/passwd"`
**When**: `evaluate_amend_request` runs
**Then**: returns `AmendDecision(approved=False, failed_gate="evidence", reason="artifact escapes project root")`
**Evidence**: hook unit test

### SCEN-203: Invariant gate — judge agent receives isolated context
**Given**: a teammate proposes an amend with elaborate pre-mortem
**When**: Gate 2 spawns `scenario-amend-judge`
**Then**: the agent's prompt contains ONLY the scenario original, the proposed amend, and the evidence artifact content — NOT the pre-mortem or the proposer's session id
**Evidence**: integration test that captures the spawned agent's input prompt and asserts absence of pre-mortem text

### SCEN-204: Invariant gate — judge spawn failure escalates safely
**Given**: the Agent tool spawn fails (mock returns None)
**When**: Gate 2 is invoked
**Then**: returns `AmendDecision(approved=False, failed_gate="invariant", reason="judge unavailable")` — never returns `approved=True` on judge failure
**Evidence**: hook unit test with monkeypatched Agent spawn

### SCEN-205: Reversibility gate — destructive class fails
**Given**: an `amend_request` whose diff removes an Evidence field
**When**: Gate 3 evaluates
**Then**: returns `(class_label="evidence_field_removed", is_reversible=False)` and Gate 3 FAILS
**Evidence**: hook unit test with synthetic diff

### SCEN-206: Reversibility gate — large diff fails regardless of class
**Given**: an `amend_request` whose diff is 50+ lines (even if all changes look "safe")
**When**: Gate 3 evaluates
**Then**: returns `(class_label="diff_too_large", is_reversible=False)` and Gate 3 FAILS
**Evidence**: hook unit test

### SCEN-207: All gates pass — autonomous amend
**Given**: `amend_request` with valid evidence, judge says PRESERVES_INVARIANT, diff is a 1-line `**Then**:` change
**When**: `sdd-test-guard.py` PreToolUse processes the Edit
**Then**: Edit is allowed; amend marker written to `<scenario_parent>/.amends/{stem}-{HEAD_SHA}.marker` containing the seven-field marker block per the Data flow section (`{premortem, gate_verdicts, judge_confidence, gate_timings_ms, evidence_path, base_head_sha, base_file_hash}`); telemetry `amend_autonomous` emitted with all four gate verdicts
**Evidence**: live hook test with seeded fixture; assert marker exists and contains expected fields

### SCEN-208: Ralph teammate — STOP after 2 attempts
**Given**: a teammate session that has emitted 2 failed attempts at satisfying SCEN-X
**When**: the teammate's third attempt would normally start
**Then**: the PROMPT instruction (verifiable via `grep` of `PROMPT_implementer.md`) explicitly states "STOP. Construct amend proposal. Do not iterate further."
**Evidence**: grep test on the prompt file + a behavioral test that simulates a teammate scenario and asserts the proposal file appears

### SCEN-209: Ralph teammate — proposal written and session ends
**Given**: a teammate decides to escalate after 2 attempts
**When**: it writes the proposal
**Then**: file exists at `.ralph/specs/{goal}/amend-proposals/{sid}-{timestamp}.json` with the five-field shape (`{premortem, evidence_artifact, proposed_content, base_head_sha, base_file_hash}` where `evidence_artifact` is itself a structured object `{path, class, metadata}`); `TaskUpdate(status="blocked-pending-amend")` was called; confession marker `> blocked: amend-required` was emitted; teammate session terminates without further tool calls
**Evidence**: integration test with mock teammate

### SCEN-210: Ralph leader — processes proposals in supervision loop
**Given**: 3 proposals exist in `amend-proposals/` from terminated teammates
**When**: the leader's supervision tick runs
**Then**: each proposal is read, `evaluate_amend_request` is invoked once per proposal, results are written to a sibling `<proposal-stem>.resolved.json` file (status `"resolved-autonomous"` for autonomous-approved, `"resolved-human:approved"` or `"resolved-human:rejected"` after human escalation), original proposal file left intact
**Evidence**: integration test

### SCEN-211: Non-Ralph — escalation surfaces Format R inline
**Given**: main agent (no Ralph) detects divergence and Gate 2 fails
**When**: it constructs the escalation
**Then**: the next agent message to the user contains the Format R skeleton with all 11 fields populated (SCENARIO, DIVERGENCE, EVIDENCE, PROPOSED AMEND, PUERTAS×4, JUDGE_CONFIDENCE, GATE_TIMINGS_MS, PRE-MORTEM, WHAT WORRIES ME MOST, RECOMENDACIÓN), `WHAT WORRIES ME MOST` non-empty, `JUDGE_CONFIDENCE` integer 0-100
**Evidence**: golden-file test — agent output is captured and compared against `tests/fixtures/format_r_skeleton.txt` template; field count and field names asserted via regex `^[A-Z_]+:` per line

### SCEN-212: Telemetry — every amend event recorded
**Given**: any amend flow (autonomous or escalated) completes
**When**: the flow finishes
**Then**: `metrics.jsonl` contains exactly one event of type `amend_proposed`; if autonomous, also `amend_autonomous`; if escalated, also `amend_escalated`; if human resolves, also `amend_resolved_human`
**Evidence**: grep on `.claude/metrics.jsonl` after each test scenario

### SCEN-213: Cleanup — resolved proposals older than 24h removed; unresolved retained
**Given**: three fixture files in `amend-proposals/`: (a) `processed.json` with mtime > 24h AND a sibling `processed.resolved.json` (also old); (b) `unresolved.json` with mtime > 24h AND NO sibling `.resolved.json`; (c) `recent.json` with mtime < 1h regardless of resolution status
**When**: SessionStart hook runs cleanup
**Then**: case (a) BOTH files (`processed.json` AND `processed.resolved.json`) are deleted; case (b) the file is RETAINED (unprocessed proposals accumulate as debt signal); case (c) the file is RETAINED (under 24h threshold). No error if `amend-proposals/` directory is missing.
**Evidence**: hook unit test parametrized over the three cases; assert presence/absence after cleanup; assert no exception if directory absent

### SCEN-214: Pre-mortem absence — autonomous gate rejects
**Given**: an `amend_request` with empty or whitespace-only `premortem` field
**When**: `evaluate_amend_request` runs
**Then**: returns `AmendDecision(approved=False, failed_gate="premortem", reason="pre-mortem missing or trivial")` BEFORE running Gates 1-3
**Evidence**: hook unit test

### SCEN-215: `_SDD_DISABLE_SCENARIOS` env var has no effect
**Given**: a scenario edit attempt with `_SDD_DISABLE_SCENARIOS=1` set in the env (any source: shell `export`, `~/.zshrc`, `settings.json` `env` block, parent process inheritance)
**When**: PreToolUse runs `sdd-test-guard.py` OR TaskCompleted runs `task-completed.py`
**Then**: the env var is **NOT** consulted; standard enforcement applies (write-once guard, completion-without-verification gate, scenario integrity gate); no `scenarios_bypassed` telemetry is emitted because the code path is removed
**Evidence**: (a) `grep -rn "_SDD_DISABLE_SCENARIOS" hooks/` returns empty (no remaining references in production hook code); (b) live hook test seeds env var, attempts scenario edit, asserts exit=2 with `[SDD:SCENARIO]` denial regardless of env var presence; (c) telemetry assertion: `metrics.jsonl` after the test contains zero `scenarios_bypassed` events

### SCEN-216: Staleness gate — base_head_sha drift rejected (added per F1)
**Given**: a proposal with `base_head_sha = "abc1234"` written when HEAD was at abc1234
**When**: between proposal write and leader processing, a normal commit advances HEAD to `def5678`
**Then**: Gate 0 evaluation returns `failed_gate="staleness"`; `amend_proposal_stale` telemetry emitted; the original proposal file is renamed to `*.stale.json` and the proposing teammate (or its successor) is responsible for re-proposing with fresh `base_head_sha`
**Evidence**: integration test — seed proposal at SHA1, advance HEAD with a dummy commit, run leader supervision, assert telemetry + rename

### SCEN-217: Invariant judge — template injection rejected (added per F9)
**Given**: a proposal whose `proposed_content` contains the literal substring `<scenario_original>` (an attempt to inject template control sequences into the judge prompt)
**When**: Gate 2 prepares the judge spawn
**Then**: `_amend_protocol.py` detects the injection pattern via pre-substitution regex check; returns `failed_gate="invariant_template_injection"`; `amend_proposal_malformed` telemetry emitted with `violation="template_injection"`; judge is NOT spawned
**Evidence**: hook unit test with synthetic injection payload across all four template placeholders

### SCEN-218: Leader-as-proposer requires deferred tick + non-skippable judge (added per F2)
**Given**: the leader writes a proposal `leader-{ts}.json` to `amend-proposals/`
**When**: the SAME supervision tick runs immediately after
**Then**: `_amend_protocol.evaluate_amend_request` for leader proposals enforces (a) the proposal mtime is at least one tick interval older than the current tick start (forces deferral) AND (b) skips no gate — judge spawn is mandatory even if heuristics suggest "obvious" approval; the proposer_role telemetry field is set to `"leader"`
**Evidence**: integration test — leader writes proposal, immediately calls evaluate, assert defer-rejected; second tick assert judge spawned

### SCEN-219: Hook-enforced 2-attempt limit (added per F5)
**Given**: a teammate session has emitted 2 failing test runs touching SCEN-X
**When**: the same teammate attempts a 3rd Edit/Write that would re-test SCEN-X
**Then**: PreToolUse blocks with stderr `[SDD:ATTEMPTS] amend-proposal required — 2 attempts exhausted on <scenario_rel>; construct amend_request, write to .ralph/specs/<goal>/amend-proposals/, end session`; `amend_attempts_exhausted` telemetry emitted; counter resets only when proposal is written or a new session starts
**Evidence**: integration test — drive 2 failing runs via test fixture, assert hook blocks 3rd attempt with the exact stderr message

### SCEN-220: Evidence taxonomy — class (a) requires git-tracked file (added per F4)
**Given**: a proposal with `evidence_artifact = {path: "/tmp/proj/fake.txt", class: "git_tracked_at_head"}` where the file is NOT tracked at HEAD
**When**: Gate 1 evaluates
**Then**: returns `failed_gate="evidence"` with reason `"class_a_path_not_tracked_at_head"`; telemetry emitted; no autonomous amend
**Evidence**: hook unit test with untracked file fixture

### SCEN-221: Evidence taxonomy — class (b) requires mtime predating proposal by ≥30s (added per F4)
**Given**: a proposal with class (b) evidence whose mtime is 5 seconds before the proposal mtime
**When**: Gate 1 evaluates
**Then**: returns `failed_gate="evidence"` with reason `"class_b_idle_window_violation"`; this is the anti-forgery check (proposer cannot write evidence then immediately propose)
**Evidence**: hook unit test with backdated mtime fixture

### SCEN-222: Evidence taxonomy — class (c) HMAC verification (added per F4)
**Given**: a proposal with class (c) evidence whose HMAC field has been altered
**When**: Gate 1 evaluates
**Then**: returns `failed_gate="evidence"` with reason `"class_c_hmac_mismatch"`; `evidence_hmac_failure` telemetry emitted (P0 security signal); proposal rejected
**Evidence**: hook unit test with tampered HMAC envelope

### SCEN-223: Env-var removal symmetric across Ralph and non-Ralph modes AND across both hooks (added per R3)
**Given**: two fixture repos — one Ralph-mode (with `.ralph/config.sh`, scenarios at `.ralph/specs/{goal}/scenarios/{goal}.scenarios.md`) and one non-Ralph (no `.ralph/config.sh`, scenarios at `docs/specs/{name}/scenarios/{name}.scenarios.md`), each with one validated scenario file committed to HEAD AND `verification-before-completion` skill NOT recorded as invoked for the test session
**When**: parametrized over `(ralph_mode, hook)` ∈ `{True, False} × {"sdd-test-guard", "task-completed"}` — 4 cases total. For each case, the corresponding hook is invoked with `_SDD_DISABLE_SCENARIOS=1` in the hook process environment:
- For `sdd-test-guard` (PreToolUse): payload is a `tool_name="Edit"` invocation targeting the tracked scenario file with mutated content (triggers the write-once guard).
- For `task-completed` (TaskCompleted lifecycle event): payload is a TaskCompleted JSON with a `task_subject` field; scenarios exist on disk but `verification-before-completion` was never recorded in the session state (triggers the scenario verification gate at `task-completed.py:580-590`).

**Then**: every case returns exit=2 with stderr containing the literal `[SDD:SCENARIO]` category prefix; every case' `.claude/metrics.jsonl` contains zero `scenarios_bypassed` events after the run. Per-hook stderr text expectation:
- `sdd-test-guard` emits stderr including `scenario write-once violation`.
- `task-completed` emits stderr including the literal substring `Scenarios exist but verification-before-completion was not called` (header: `Scenario verification not invoked for: {task_subject}`).
Both stderr texts are mode-invariant (Ralph and non-Ralph produce identical strings); the env var has no effect in any case.

**Evidence**: parametrized integration test `hooks/test_scen_a23_envvar_parity.py` exercises 4 cases via `pytest.mark.parametrize(("ralph_mode", "hook"), [(True, "sdd-test-guard"), (True, "task-completed"), (False, "sdd-test-guard"), (False, "task-completed")])`. For each case the test (1) builds the appropriate fixture repo with `git init` + a tracked scenario at the mode-correct path, (2) invokes the matching hook via `_subprocess_harness.invoke_hook(name, payload, env={"_SDD_DISABLE_SCENARIOS": "1"})`, (3) asserts `result.returncode == 2`, (4) asserts the hook-specific stderr substring is present, (5) asserts `_count_event(cwd / ".claude" / "metrics.jsonl", "scenarios_bypassed") == 0`. The `_count_event` helper signature `def _count_event(metrics_path: Path, event_name: str) -> int` is defined at the top of the test module: opens the file if it exists, reads line-by-line, parses each line as JSON, returns the count of objects whose `event` field equals `event_name` (returns 0 if file is missing — no external dependency).

## Open questions for human review

These need explicit decision before implementation begins:

1. **Where do `amend-proposals/` live in non-Ralph mode** — nowhere on disk (synchronous), or also on disk for auditability? Current design: nowhere.
2. **Should the judge agent use a different model than the proposer** (e.g., proposer Opus, judge Sonnet)? Per F14 review: design supports per-config model swap without code change. Current default: same model + hostile-reviewer persona prompt; switch when multi-model availability is operationally easy.
3. **What is the timeout for the judge spawn** — 30s, 60s, longer? Current design: 60s, fall back to escalation.
4. **Schema enforcement for `amend_request`**: per review, the design now mandates a schema — the five-field shape `{premortem, evidence_artifact, proposed_content, base_head_sha, base_file_hash}` where `evidence_artifact` is itself a structured object `{path, class, metadata}` with `class` constrained to the three-value taxonomy (Gate 1). Implementation may choose dataclass vs Pydantic vs jsonschema; design is implementation-agnostic on representation but strict on shape.
5. **Does Gate 3's "diff too large > 30 lines" threshold need to be configurable**? Current design: hardcoded constant; revisit only if real cases hit the cap.
6. **Cross-spec contradiction detection** — out of scope for this design; flag for Phase 11.
7. **HMAC key rotation cadence**: per-session by default. Revisit if proposals must outlive sessions (probably not — by design they're short-lived).

## Review trail

| Round | Reviewer | Verdict | Findings |
|---|---|---|---|
| R1 | code-reviewer agent (adversarial, no session context) | APPROVE WITH CHANGES | 4 P0 (F1-F4 staleness, leader-self-loop, judge poisoning, evidence forgery), 8 P1 (F5-F12), 4 P2 (F11-F14) |
| R2 | First revision | All P0 closed; F5, F6, F7, F8, F10 closed; F11, F12, F13, F14 closed; F9 closed via SCEN-217. P2 not yet addressed: telemetry sampling, dashboard | — |
| R3 | Strategic synthesis after `_SDD_DISABLE_SCENARIOS` audit (this revision) | Removed env-var bypass. Audit (4 parallel agents) showed the var was agent-accessible via Bash `export`, contradicting the factory.ai holdout principle. Citations: Anthropic *Agentic Misalignment* (2025-06-20, 96% disobey rate in Opus 4); DeepMind *Specification gaming* (Krakovna 2020, "reward tampering"); Claude Code docs (`permissionDecision: 'deny'` in PreToolUse is immune to bypass). With the four-gate protocol as the legitimate front door, the back door is redundant — `git rm` (deletion), Format R (amend escalation), and `git commit --no-verify` (telemetry-logged hotfix) cover every legitimate case | R3 first-pass: SCEN-215 reversed; risk row #9 reversed; mission paragraph clarified; deliberate-rejections list extended; SCEN-223 added; title corrected from "Three Gates" to "Four Gates". R3 second-pass (post spec-document-reviewer iteration 1): Components scope expanded to 13 modified files (added `test_scen_020.py`, `phase10-plan.md`, `mission-report/SKILL.md`); Components header count corrected; `## Open questions for human review` heading restored (regression from first-pass edit); SCEN-223 extended to 4-case parametrization (mode × hook); `_count_event` test helper specified inline; SCEN-209 `four-field` → `five-field` shape with structured `evidence_artifact`; Open question #4 same correction; risk row #9 trimmed; Out-of-scope bullets added for `CHANGELOG.md`, `docs/phase9-plan.md`, and `mission-report/aggregate.py` historical-event handling. R3 third-pass (post spec-document-reviewer iteration 2): SCEN-223 task-completed mapping corrected — was incorrectly described as a `TaskUpdate(status=completed)` PreToolUse payload with stderr `scenarios require verification`; corrected to TaskCompleted lifecycle event with stderr literal `Scenarios exist but verification-before-completion was not called` (verified against `task-completed.py:580-590`); SCEN-210/A13/Cleanup section aligned on sibling `.resolved.json` file pattern (was ambiguous between in-place mutation and sibling file); SCEN-207 amend marker shape corrected from "four-field" to "seven-field" matching Data flow definition; risk row about `amend_request` payload aligned on five-field shape |

---

**Status**: amend-protocol-v2 design at R3 — R1 adversarial review P0+P1 closed (R2), strategic synthesis applied removing env-var bypass for factory.ai-alignment (R3). 23 observable scenarios extracted (15 v1 original + 7 added in R2 + 1 added in R3). Ready for human review + sop-planning.
