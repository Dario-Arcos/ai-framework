---
name: amend-protocol-v2
created_by: brainstorming
created_at: 2026-04-25T01:30:00Z
source_spec: docs/specs/2026-04-25-amend-protocol/design.md
revision: R3
---

## SCEN-201: Evidence gate — missing artifact rejected
**Given**: an `amend_request` with `evidence_artifact` pointing to a non-existent path
**When**: `evaluate_amend_request` runs
**Then**: returns `AmendDecision(approved=False, failed_gate="evidence", reason="artifact not found")`; no autonomous Edit; telemetry `amend_escalated` emitted
**Evidence**: hook unit test with synthetic missing path

## SCEN-202: Evidence gate — path traversal rejected
**Given**: an `amend_request` with `evidence_artifact = "/etc/passwd"`
**When**: `evaluate_amend_request` runs
**Then**: returns `AmendDecision(approved=False, failed_gate="evidence", reason="artifact escapes project root")`
**Evidence**: hook unit test

## SCEN-203: Invariant gate — judge agent receives isolated context
**Given**: a teammate proposes an amend with elaborate pre-mortem
**When**: Gate 2 spawns `scenario-amend-judge`
**Then**: the agent's prompt contains ONLY the scenario original, the proposed amend, and the evidence artifact content — NOT the pre-mortem or the proposer's session id
**Evidence**: integration test that captures the spawned agent's input prompt and asserts absence of pre-mortem text

## SCEN-204: Invariant gate — judge spawn failure escalates safely
**Given**: the Agent tool spawn fails (mock returns None)
**When**: Gate 2 is invoked
**Then**: returns `AmendDecision(approved=False, failed_gate="invariant", reason="judge unavailable")` — never returns `approved=True` on judge failure
**Evidence**: hook unit test with monkeypatched Agent spawn

## SCEN-205: Reversibility gate — destructive class fails
**Given**: an `amend_request` whose diff removes an Evidence field
**When**: Gate 3 evaluates
**Then**: returns `(class_label="evidence_field_removed", is_reversible=False)` and Gate 3 FAILS
**Evidence**: hook unit test with synthetic diff

## SCEN-206: Reversibility gate — large diff fails regardless of class
**Given**: an `amend_request` whose diff is 50+ lines (even if all changes look "safe")
**When**: Gate 3 evaluates
**Then**: returns `(class_label="diff_too_large", is_reversible=False)` and Gate 3 FAILS
**Evidence**: hook unit test

## SCEN-207: All gates pass — autonomous amend
**Given**: `amend_request` with valid evidence, judge says PRESERVES_INVARIANT, diff is a 1-line `**Then**:` change
**When**: `sdd-test-guard.py` PreToolUse processes the Edit
**Then**: Edit is allowed; amend marker written to `<scenario_parent>/.amends/{stem}-{HEAD_SHA}.marker` containing the seven-field marker block per the Data flow section (`{premortem, gate_verdicts, judge_confidence, gate_timings_ms, evidence_path, base_head_sha, base_file_hash}`); telemetry `amend_autonomous` emitted with all four gate verdicts
**Evidence**: live hook test with seeded fixture; assert marker exists and contains expected fields

## SCEN-208: Ralph teammate — STOP after 2 attempts
**Given**: a teammate session that has emitted 2 failed attempts at satisfying a target scenario
**When**: the teammate's third attempt would normally start
**Then**: the PROMPT instruction (verifiable via `grep` of `PROMPT_implementer.md`) explicitly states "STOP. Construct amend proposal. Do not iterate further."
**Evidence**: grep test on the prompt file + a behavioral test that simulates a teammate scenario and asserts the proposal file appears

## SCEN-209: Ralph teammate — proposal written and session ends
**Given**: a teammate decides to escalate after 2 attempts
**When**: it writes the proposal
**Then**: file exists at `.ralph/specs/{goal}/amend-proposals/{sid}-{timestamp}.json` with the five-field shape (`{premortem, evidence_artifact, proposed_content, base_head_sha, base_file_hash}` where `evidence_artifact` is itself a structured object `{path, class, metadata}`); `TaskUpdate(status="blocked-pending-amend")` was called; confession marker `> blocked: amend-required` was emitted; teammate session terminates without further tool calls
**Evidence**: integration test with mock teammate

## SCEN-210: Ralph leader — processes proposals in supervision loop
**Given**: 3 proposals exist in `amend-proposals/` from terminated teammates
**When**: the leader's supervision tick runs
**Then**: each proposal is read, `evaluate_amend_request` is invoked once per proposal, results are written to a sibling `<proposal-stem>.resolved.json` file (status `"resolved-autonomous"` for autonomous-approved, `"resolved-human:approved"` or `"resolved-human:rejected"` after human escalation), original proposal file left intact
**Evidence**: integration test

## SCEN-211: Non-Ralph — escalation surfaces Format R inline
**Given**: main agent (no Ralph) detects divergence and Gate 2 fails
**When**: it constructs the escalation
**Then**: the next agent message to the user contains the Format R skeleton with all 11 fields populated (SCENARIO, DIVERGENCE, EVIDENCE, PROPOSED AMEND, PUERTAS sub-rows for staleness/evidence/invariant/reversibility, JUDGE_CONFIDENCE, GATE_TIMINGS_MS, PRE-MORTEM, WHAT WORRIES ME MOST, RECOMENDACIÓN), `WHAT WORRIES ME MOST` non-empty, `JUDGE_CONFIDENCE` integer 0-100
**Evidence**: golden-file test — agent output is captured and compared against `tests/fixtures/format_r_skeleton.txt` template; field count and field names asserted via regex `^[A-Z_]+:` per line

## SCEN-212: Telemetry — every amend event recorded
**Given**: any amend flow (autonomous or escalated) completes
**When**: the flow finishes
**Then**: `metrics.jsonl` contains exactly one event of type `amend_proposed`; if autonomous, also `amend_autonomous`; if escalated, also `amend_escalated`; if human resolves, also `amend_resolved_human`
**Evidence**: grep on `.claude/metrics.jsonl` after each test scenario

## SCEN-213: Cleanup — resolved proposals older than 24h removed; unresolved retained
**Given**: three fixture files in `amend-proposals/`: (a) `processed.json` with mtime > 24h AND a sibling `processed.resolved.json` (also old); (b) `unresolved.json` with mtime > 24h AND NO sibling `.resolved.json`; (c) `recent.json` with mtime < 1h regardless of resolution status
**When**: SessionStart hook runs cleanup
**Then**: case (a) BOTH files (`processed.json` AND `processed.resolved.json`) are deleted; case (b) the file is RETAINED (unprocessed proposals accumulate as debt signal); case (c) the file is RETAINED (under 24h threshold). No error if `amend-proposals/` directory is missing.
**Evidence**: hook unit test parametrized over the three cases; assert presence/absence after cleanup; assert no exception if directory absent

## SCEN-214: Pre-mortem absence — autonomous gate rejects
**Given**: an `amend_request` with empty or whitespace-only `premortem` field
**When**: `evaluate_amend_request` runs
**Then**: returns `AmendDecision(approved=False, failed_gate="premortem", reason="pre-mortem missing or trivial")` BEFORE running Gates 1-3
**Evidence**: hook unit test

## SCEN-215: `_SDD_DISABLE_SCENARIOS` env var has no effect
**Given**: a scenario edit attempt with `_SDD_DISABLE_SCENARIOS=1` set in the env (any source: shell `export`, `~/.zshrc`, `settings.json` `env` block, parent process inheritance)
**When**: PreToolUse runs `sdd-test-guard.py` OR TaskCompleted runs `task-completed.py`
**Then**: the env var is **NOT** consulted; standard enforcement applies (write-once guard, completion-without-verification gate, scenario integrity gate); no `scenarios_bypassed` telemetry is emitted because the code path is removed
**Evidence**: (a) `grep -rn "_SDD_DISABLE_SCENARIOS" hooks/` returns empty (no remaining references in production hook code); (b) live hook test seeds env var, attempts scenario edit, asserts exit=2 with `[SDD:SCENARIO]` denial regardless of env var presence; (c) telemetry assertion: `metrics.jsonl` after the test contains zero `scenarios_bypassed` events

## SCEN-216: Staleness gate — base_head_sha drift rejected
**Given**: a proposal with `base_head_sha = "abc1234"` written when HEAD was at abc1234
**When**: between proposal write and leader processing, a normal commit advances HEAD to `def5678`
**Then**: Gate 0 evaluation returns `failed_gate="staleness"`; `amend_proposal_stale` telemetry emitted; the original proposal file is renamed to `*.stale.json` and the proposing teammate (or its successor) is responsible for re-proposing with fresh `base_head_sha`
**Evidence**: integration test — seed proposal at SHA1, advance HEAD with a dummy commit, run leader supervision, assert telemetry + rename

## SCEN-217: Invariant judge — template injection rejected
**Given**: a proposal whose `proposed_content` contains the literal substring `<scenario_original>` (an attempt to inject template control sequences into the judge prompt)
**When**: Gate 2 prepares the judge spawn
**Then**: `_amend_protocol.py` detects the injection pattern via pre-substitution regex check; returns `failed_gate="invariant_template_injection"`; `amend_proposal_malformed` telemetry emitted with `violation="template_injection"`; judge is NOT spawned
**Evidence**: hook unit test with synthetic injection payload across all four template placeholders

## SCEN-218: Leader-as-proposer requires deferred tick + non-skippable judge
**Given**: the leader writes a proposal `leader-{ts}.json` to `amend-proposals/`
**When**: the SAME supervision tick runs immediately after
**Then**: `_amend_protocol.evaluate_amend_request` for leader proposals enforces (a) the proposal mtime is at least one tick interval older than the current tick start (forces deferral) AND (b) skips no gate — judge spawn is mandatory even if heuristics suggest "obvious" approval; the proposer_role telemetry field is set to `"leader"`
**Evidence**: integration test — leader writes proposal, immediately calls evaluate, assert defer-rejected; second tick assert judge spawned

## SCEN-219: Hook-enforced 2-attempt limit
**Given**: a teammate session has emitted 2 failing test runs touching a target scenario
**When**: the same teammate attempts a 3rd Edit/Write that would re-test the same scenario
**Then**: PreToolUse blocks with stderr `[SDD:ATTEMPTS] amend-proposal required — 2 attempts exhausted on <scenario_rel>; construct amend_request, write to .ralph/specs/<goal>/amend-proposals/, end session`; `amend_attempts_exhausted` telemetry emitted; counter resets only when proposal is written or a new session starts
**Evidence**: integration test — drive 2 failing runs via test fixture, assert hook blocks 3rd attempt with the exact stderr message

## SCEN-220: Evidence taxonomy — class (a) requires git-tracked file
**Given**: a proposal with `evidence_artifact = {path: "/tmp/proj/fake.txt", class: "git_tracked_at_head"}` where the file is NOT tracked at HEAD
**When**: Gate 1 evaluates
**Then**: returns `failed_gate="evidence"` with reason `"class_a_path_not_tracked_at_head"`; telemetry emitted; no autonomous amend
**Evidence**: hook unit test with untracked file fixture

## SCEN-221: Evidence taxonomy — class (b) requires mtime predating proposal by ≥30s
**Given**: a proposal with class (b) evidence whose mtime is 5 seconds before the proposal mtime
**When**: Gate 1 evaluates
**Then**: returns `failed_gate="evidence"` with reason `"class_b_idle_window_violation"`; this is the anti-forgery check (proposer cannot write evidence then immediately propose)
**Evidence**: hook unit test with backdated mtime fixture

## SCEN-222: Evidence taxonomy — class (c) HMAC verification
**Given**: a proposal with class (c) evidence whose HMAC field has been altered
**When**: Gate 1 evaluates
**Then**: returns `failed_gate="evidence"` with reason `"class_c_hmac_mismatch"`; `evidence_hmac_failure` telemetry emitted (P0 security signal); proposal rejected
**Evidence**: hook unit test with tampered HMAC envelope

## SCEN-223: Env-var removal symmetric across Ralph and non-Ralph modes AND across both hooks
**Given**: two fixture repos — one Ralph-mode (with `.ralph/config.sh`, scenarios at `.ralph/specs/{goal}/scenarios/{goal}.scenarios.md`) and one non-Ralph (no `.ralph/config.sh`, scenarios at `docs/specs/{name}/scenarios/{name}.scenarios.md`), each with one validated scenario file committed to HEAD AND `verification-before-completion` skill NOT recorded as invoked for the test session
**When**: parametrized over `(ralph_mode, hook)` ∈ `{True, False} × {"sdd-test-guard", "task-completed"}` — 4 cases total. For each case, the corresponding hook is invoked with `_SDD_DISABLE_SCENARIOS=1` in the hook process environment. For `sdd-test-guard` (PreToolUse): payload is a `tool_name="Edit"` invocation targeting the tracked scenario file with mutated content. For `task-completed` (TaskCompleted lifecycle event): payload is a TaskCompleted JSON with a `task_subject` field; scenarios exist on disk but `verification-before-completion` was never recorded in the session state.
**Then**: every case returns exit=2 with stderr containing the literal `[SDD:SCENARIO]` category prefix; every case' `.claude/metrics.jsonl` contains zero `scenarios_bypassed` events after the run. `sdd-test-guard` emits stderr including `scenario write-once violation`; `task-completed` emits stderr including the literal substring `Scenarios exist but verification-before-completion was not called`. Both stderr texts are mode-invariant (Ralph and non-Ralph produce identical strings); the env var has no effect in any case.
**Evidence**: parametrized integration test `hooks/test_scen_a23_envvar_parity.py` exercises 4 cases via `pytest.mark.parametrize(("ralph_mode", "hook"), [(True, "sdd-test-guard"), (True, "task-completed"), (False, "sdd-test-guard"), (False, "task-completed")])`. For each case the test (1) builds the appropriate fixture repo with `git init` + a tracked scenario at the mode-correct path, (2) invokes the matching hook via `_subprocess_harness.invoke_hook(name, payload, env={"_SDD_DISABLE_SCENARIOS": "1"})`, (3) asserts `result.returncode == 2`, (4) asserts the hook-specific stderr substring is present, (5) asserts `_count_event(cwd / ".claude" / "metrics.jsonl", "scenarios_bypassed") == 0`. The `_count_event` helper signature `def _count_event(metrics_path: Path, event_name: str) -> int` is defined at the top of the test module: opens the file if it exists, reads line-by-line, parses each line as JSON, returns the count of objects whose `event` field equals `event_name` (returns 0 if file is missing — no external dependency).
