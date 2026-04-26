# Quality Gates Reference

## Overview

This reference defines quality gates for ralph-orchestrator execution. Gates apply backpressure to ensure code quality without prescribing implementation details. Teammates determine "how" while gates verify "what".

**Core Philosophy**: Backpressure Over Prescription - Create gates that reject bad work rather than dictating how teammates should implement.

---

## Available Gates

**Constraints:**
- You MUST configure all gates for your stack because missing gates allow defects through
- You SHOULD use project-specific commands because generic commands may miss project conventions

| Gate | Purpose | Example Command |
|------|---------|-----------------|
| `GATE_TEST` | Run unit test suite | `npm test`, `pytest` |
| `GATE_TYPECHECK` | Type checking | `npm run typecheck`, `mypy src/` |
| `GATE_LINT` | Linting | `npm run lint`, `ruff check .` |
| `GATE_BUILD` | Build validation | `npm run build`, `go build ./...` |
| `GATE_INTEGRATION` | Integration tests (testcontainers, real DB) | `npm run test:integration`, `pytest -m integration` |
| `GATE_E2E` | End-to-end tests | `npx playwright test`, `npx cypress run` |

### Supplementary: Coverage Gate

| Gate | Purpose | Example Command |
|------|---------|-----------------|
| `GATE_COVERAGE` | Coverage enforcement | `npx vitest run --coverage`, `pytest --cov` |

GATE_COVERAGE is evaluated AFTER the 6 standard gates pass. Requires `MIN_TEST_COVERAGE > 0` and a non-empty `GATE_COVERAGE` command in config.sh. In non-scenario projects it can still reject the task; when committed scenarios exist, coverage is demoted to an informational signal so the scenario contract remains the primary acceptance decision.

---

## Gate Configuration

**Constraints:**
- You MUST pass GATE_TEST before committing because untested code has higher defect rates
- You MUST pass GATE_TYPECHECK because type errors cause runtime failures
- You MUST pass GATE_LINT because style violations reduce code readability
- You MUST pass GATE_BUILD because build failures indicate broken code

All gates are required. SDD is mandatory. There is one quality standard: production excellence.

```bash
# All gates required for every task
# GATE_TEST: Required
# GATE_TYPECHECK: Required
# GATE_LINT: Required
# GATE_BUILD: Required
```

---

## Gate Execution Order

**Constraints:**
- You MUST execute gates in order because earlier gates catch simpler issues faster
- You MUST NOT skip to later gates because failed early gates invalidate later results

**Order:**
1. `GATE_TEST` - Verify unit behavior (fast feedback)
2. `GATE_TYPECHECK` - Catch type errors
3. `GATE_LINT` - Catch style issues
4. `GATE_BUILD` - Ensure it compiles
5. `GATE_INTEGRATION` - Verify integration behavior (testcontainers, real deps)
6. `GATE_E2E` - Verify end-to-end flows
7. `GATE_COVERAGE` - Enforce minimum coverage (when configured)

If any gate fails, the `task-completed.py` hook returns exit 2 with failure output on stderr. The teammate receives the gate output and must fix the issue before marking the task complete again.

---

## SDD Gate Enforcement

**Constraints:**
- You MUST write scenarios before implementation because SDD ensures testable design
- You MUST see scenario fail first (scenario) because passing scenarios prove nothing without failure
- You MUST implement minimal code to satisfy (satisfy) because over-implementation adds unnecessary complexity
- You MUST refactor while satisfied because refactoring on unsatisfied risks breaking functionality
- You MUST NOT skip SDD steps because gates reject work that bypasses the cycle

**SDD Cycle:**
1. Scenario must be defined first
2. Scenario must fail first (scenario)
3. Implementation satisfies the scenario (satisfy)
4. Refactor while satisfied

Tasks with `Scenario-Strategy: required` (or field absent) follow full SDD. Tasks classified as `not-applicable` skip the SDD cycle in sop-code-assist (Step 4a) but all quality gates run unconditionally — behavioral gates on non-code changes catch unexpected side effects and align with correctness over comfort.

### Scenario Gate Priority

When committed scenario files exist under any configured discovery root (Ralph: `.ralph/specs/{goal}/scenarios/`; non-Ralph: `docs/specs/{name}/scenarios/`), those committed scenario artifacts are the primary quality contract. Automated gates still run, but the orchestration model is scenarios first:

- Scenario integrity and verification are blocking.
- Coverage is an informational signal when scenarios exist, not the authority on task correctness.
- A task that satisfies all committed scenarios but has thin coverage still needs follow-up, but the scenario contract remains the main acceptance decision.

### Write-Once Contract (PreToolUse Guard)

Committed scenario files are protected by two layers of `sdd-test-guard.py`:

1. **Post-mutation disk check** (SCEN-001..010): if the on-disk file diverges from the baseline recorded at first add-commit, deny unless a valid amend marker exists. Catches out-of-band edits (external editors, git operations, Bash piping).
2. **Pre-edit simulation check** (SCEN-011): at `PreToolUse` timing the tool has not yet applied, so disk still equals baseline. `_predict_scenario_post_edit_hash()` simulates the pending edit — `Edit(old, new, replace_all?)` via `str.replace`, `Write(content)` wholesale, `MultiEdit[edits]` sequentially, `NotebookEdit(new_source)` wholesale — hashes the predicted bytes, and denies if the prediction diverges from baseline.

Both sides canonicalize via `_canon_scenario_bytes()` (strips UTF-8 BOM + normalizes CRLF→LF) so editor serialization differences do not trigger false denies.

Malformed edits are denied BEFORE simulation: `Edit.old_string` empty or absent from disk, non-object MultiEdit entries. This prevents pathological `replace()` semantics and silent pass-through when the simulator cannot verify the divergence.

Amend flow has two routes. Manual: invoke `/ai-framework:sop-reviewer` in the session and create `<scenario_parent>/.amends/{stem}-{HEAD_SHA}.marker`. Autonomous: pass an `amend_request` payload through the four-gate protocol (`docs/specs/2026-04-25-amend-protocol/`); on PASS the hook writes the marker for you. Either way the marker is invalidated by the next `git commit`, enforcing "amends must be justified per-commit".

---

## Exit Code Suppression (Anti-Pattern)

**Constraints:**
- You MUST NOT use `|| true`, `; true`, `|| :`, or `|| exit 0` in gate commands because they force exit code 0, defeating the gate entirely
- You MUST NOT use `2>&1 || true` because it both redirects output AND suppresses failure
- You MUST use `&&` to chain multi-package commands because `&&` propagates the first failure

The `task-completed.py` hook rejects gate commands containing exit code suppression at runtime. If your gate command is rejected, replace the suppression with `&&`.

```bash
# BAD — gate always passes, tests never enforced:
GATE_TEST="npm test --prefix packages/server 2>&1 || true"

# BAD — first failure is swallowed:
GATE_TEST="npm test --prefix packages/a ; true ; npm test --prefix packages/b"

# GOOD — first failure stops the chain:
GATE_TEST="npm test --prefix packages/server && npm test --prefix packages/web"
```

**Why this matters:** Exit code suppression defeats ALL three enforcement layers simultaneously — the TaskCompleted gate, the SDD auto-test state, and the reward hacking guard.

---

## How Coverage Is Verified

The coverage gate uses **diff-coverage** based on the test runner's own coverage report — the same approach used by SWE-bench, [diff-cover](https://github.com/Bachmann1234/diff_cover), and other state-of-the-art systems.

**Detection** (zero per-project config required):

| Manifest | Runner | Coverage command | Report format |
|---|---|---|---|
| `package.json` with `vitest` in scripts.test | Vitest | `npx vitest run --coverage --coverage.reporter=lcov` | lcov |
| `package.json` with `jest` in scripts.test | Jest | `npx jest --coverage --coverageReporters=lcov` | lcov |
| `package.json` with other JS test runner | c8 wrapper | `npx c8 --reporter=lcov -- <script>` | lcov |
| `pyproject.toml` containing `pytest` | pytest-cov | `pytest --cov=. --cov-report=lcov:coverage.lcov` | lcov |
| `go.mod` | Go native | `go test -coverprofile=coverage.out ./...` | go-cover |
| `Cargo.toml` (with `cargo-llvm-cov` installed) | cargo-llvm-cov | `cargo llvm-cov --lcov --output-path coverage.lcov` | lcov |

**Decision flow** (`compute_uncovered`):

1. If the project's coverage report (`coverage/lcov.info`, `coverage.out`, etc.) exists and is fresh (newer than the session's edits with 5s grace), parse it and use **line-level** coverage when `git diff` is available, **file-level** otherwise.
2. If no coverage report exists or it's stale, the hook tries to regenerate it by running the detected coverage command (subject to the gate budget).
3. If detection fails entirely (no recognized manifest), fall back to the legacy basename + filesystem heuristic — projects with `foo.ts` and `foo.test.ts` siblings still pass.

**Why this is anti-reward-hacking**: an empty `foo.test.ts` satisfies the basename heuristic but produces no line hits in the coverage report. The diff-coverage gate sees zero hits and flags the file as uncovered. Module-level tests, integration tests, and E2E tests are honored natively because every test that exercises a line shows up as a hit, regardless of where the test file lives.

**Project-level customization without config**: there is none, by design. If a file genuinely shouldn't have tests (framework shell, generated code), exclude it via the runner's own coverage configuration (`coverage.exclude` in vitest, `omit` in pytest-cov, etc.) — the report will not contain it, and the gate will not flag it.

---

## Custom Quality Gates

**Constraints:**
- You MUST modify `hooks/task-completed.py` to add NEW gate types (e.g., `GATE_SECURITY`) because the hook only reads gate names listed in `CONFIG_KEYS`
- You MUST add the corresponding gate command to `.ralph/config.sh`
- You MUST NOT assume that adding a new `GATE_*` variable to `config.sh` alone will activate it

This applies only to entirely new gate categories. Coverage detection is automatic (see above) and requires no plugin modification.

**Example** (requires both hook and config changes):

```bash
# In .ralph/config.sh — define the command
GATE_SECURITY="npm audit --audit-level=high"
```

```python
# In hooks/task-completed.py — add to CONFIG_KEYS and gate execution
CONFIG_KEYS = [
    "GATE_TEST", "GATE_TYPECHECK", "GATE_LINT", "GATE_BUILD",
    "GATE_INTEGRATION", "GATE_E2E",
    "GATE_SECURITY",  # ← add here
]
```

---

## Gate Failure Handling

**Constraints:**
- You MUST provide failure output to teammates because they need context to fix issues
- You MUST allow teammates to attempt fixes because automated retries often succeed
- You MUST trip circuit breaker after 3 consecutive failures because infinite loops waste resources

**Process:**
1. Teammate receives failure output
2. Teammate attempts fix
3. Teammate re-runs gate
4. If 3 consecutive failures, circuit breaker trips

---

## Task Completion Protocol

**Constraints:**
- You MUST understand that task completion is enforced by the `task-completed.py` hook, not by manual signals
- You MUST NOT bypass the hook because it is the single enforcement point for quality gates

**Process:**
- When a teammate marks a task as complete, the `TaskCompleted` hook fires automatically
- The hook runs all configured gates in order (test → typecheck → lint → build → integration → e2e)
- **Exit 0**: all gates passed — task is marked complete, failure counter resets, metrics updated
- **Exit 2**: a gate failed — task remains incomplete, failure output sent to teammate via stderr, failure counter incremented

---

## Reviewer as SDD Validation Layer

After automated gates pass, a **reviewer teammate** validates SDD compliance for each completed task. This is a second validation layer that catches process violations gates cannot detect.

**What the reviewer checks:**
- Scenarios were defined before implementation (not retrofitted)
- Scenarios failed first before being satisfied
- Implementation is minimal to satisfy scenarios (no over-engineering)
- Refactoring was done while scenarios remained green

**Workflow:**
1. Implementer completes task → automated gates pass (test, typecheck, lint, build, integration, e2e)
2. Lead spawns a reviewer teammate for the completed task
3. Reviewer runs `/sop-reviewer` against the task
4. Reviewer writes review to `.ralph/reviews/task-{id}-review.md`
5. Reviewer sends 8-word summary to lead via SendMessage
6. Lead reads only the 8-word summary — never the full review

**Constraints:**
- You MUST NOT skip reviewer validation because automated gates catch correctness but not process compliance
- You MUST NOT have the lead read full reviews because this would pollute the lead's orchestration context

---

## Troubleshooting

### Gates Failing Unexpectedly

If gates fail but code appears correct:
- You SHOULD check environment setup (node version, dependencies installed)
- You SHOULD run gates manually to see full output
- You MAY have missing test fixtures or configuration

### Teammates Stuck in Gate Loop

If teammates repeatedly fail the same gate:
- You SHOULD review the task specification for clarity issues
- You SHOULD check if prerequisites are missing
- You MUST NOT implement fixes as orchestrator because this violates role boundaries

---

## Observability

### Failure mode prefixes

- `[SDD:GATE]` — standard test/typecheck/lint/build/integration/e2e failures. Example: `[SDD:GATE] Quality gate 'lint' failed for: auth refactor`
- `[SDD:COVERAGE]` — uncovered files or coverage command/threshold failures. Example: `[SDD:COVERAGE] Untested source files for: checkout flow`
- `[SDD:SCENARIO]` — invalid scenarios, missing verification, or scenario/test-integrity guards. Example: `[SDD:SCENARIO] Scenario verification not invoked for: payment task`
- `[SDD:POLICY]` — missing required SDD skill invocation or protected review writes. Example: `[SDD:POLICY] SDD skill not invoked for: reviewer task`

Compact taxonomy: `[SDD:GATE|COVERAGE|SCENARIO|POLICY]`

### `metrics.jsonl` format

Every line is one JSON object in `.claude/metrics.jsonl`.

- Common fields: `ts`, `project_hash`, `session_id`, `hook_version`, `event`
- Event-specific fields: `category`, `reason`, `teammate`, `scenarios_gated`, `command`, `passed`, `duration_s`, `tool_name`, `file_path`

### `jq` examples

```bash
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' .claude/metrics.jsonl
jq 'select(.event=="task_failed")' .claude/metrics.jsonl | tail -10
jq -s '
  [ .[] | select(.event=="test_run_end") ] as $runs
  | ($runs | map(select(.passed == true)) | length) as $passed
  | ($runs | map(select(.passed == false)) | length) as $failed
  | {passed: $passed, failed: $failed, ratio: ($passed / ($failed // 1))}
' .claude/metrics.jsonl
```

### Rotation

`metrics.jsonl` rotates once the active file exceeds `10 MiB`. The current file becomes `.claude/metrics.jsonl.1`; older files shift to `.2` and `.3`; `.3` is the oldest retained file.

### Rollback / disable

Deleting `.claude/metrics.jsonl` is safe. The next telemetry write recreates it automatically, and rotation will recreate the numbered files as needed.

### Scenario rollback ladder

Escalate from narrowest to broadest rollback (no env-var bypass — the back door was removed in amend-protocol Step 4 per the factory.ai holdout principle):

1. `git rm` a single scenario file under its discovery root to drop a single contract from the holdout. Commit the removal.
2. `git rm -r` the goal's `scenarios/` directory to return the project to backward-compatible pre-scenario behavior for that goal.
3. For genuine scenario divergence (the contract is wrong, not the code): construct an `amend_request` and route it through the four-gate amend protocol. If any gate fails, the hook surfaces a Format R escalation and a human disposes of the proposal — there is no single-key escape hatch.
4. Hotfix-without-scenario-validation in an incident window: `git commit --no-verify`. This is telemetry-logged as a deliberate bypass; review the log post-incident and either roll forward with a real validation or revert.

### Circuit Breaker Tripped

If circuit breaker trips (3 failures):
- You MUST review task cycle state for systemic issues
- You SHOULD consider reducing task scope
- You MAY need to update the plan with more specific guidance

---

## Official Claude Code docs — viability citation table (Phase 7 C7)

Every matcher / event / schema / stdin shape used by this plugin is grounded in an official Claude Code doc URL. Verified 2026-04-17 via the `claude-code-guide` sub-agent fetching `code.claude.com/docs`.

| # | Plugin claim | Official doc | Verdict |
|---|---|---|---|
| 1 | `hooks/hooks.json` `PreToolUse.matcher` accepts `Edit\|Write\|NotebookEdit\|TaskUpdate\|Bash` | `code.claude.com/docs/en/hooks.md` + `tools.md` | SUPPORTED — matchers are regex over tool names; `TaskUpdate` and `NotebookEdit` are current built-in tools |
| 2 | `MultiEdit` removed from matcher | `code.claude.com/docs/en/tools.md` | `MultiEdit` is NOT in the current tools reference; safely removed |
| 3 | `PostToolUse.matcher` includes `Skill` | `code.claude.com/docs/en/hooks-guide.md` | UNCLEAR — official examples show `Edit\|Write` but not `Skill`; retained as defensive (regex won't match invalid names → no-op) |
| 4 | `SessionStart.matcher` values `startup\|resume\|clear\|compact` | `code.claude.com/docs/en/hooks-guide.md` | SUPPORTED |
| 5 | Hook events `TeammateIdle`, `TaskCompleted`, `SubagentStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`, `Notification` | `code.claude.com/docs/en/hooks-guide.md` | SUPPORTED |
| 6 | Hook stdin fields `tool_name`, `tool_input`, `cwd`, `session_id`, `transcript_path` | `code.claude.com/docs/en/hooks.md` | SUPPORTED |
| 7 | TeammateIdle stdin field `teammate_name` | `code.claude.com/docs/en/hooks.md` | UNCLEAR — docs show generic fields only. Hook uses `input_data.get("teammate_name", "unknown")` so it degrades gracefully |
| 8 | Exit codes: 0 = allow, 2 = deny with stderr surfaced to agent | `code.claude.com/docs/en/hooks.md` | SUPPORTED |
| 9 | `settings.json` top-level `env` block applies environment variables per session | `code.claude.com/docs/en/settings.md` | SUPPORTED |
| 10 | `_SDD_DISABLE_SCENARIOS` env key (leading underscore) | `code.claude.com/docs/en/env-vars.md` | UNCLEAR — docs do not restrict key naming; treated as permitted |
| 11 | Plugin manifest `.claude-plugin/plugin.json` — `name` required, `version` + `description` optional | `code.claude.com/docs/en/plugins-reference.md` | SUPPORTED |
| 12 | Version format CalVer `YYYY.MINOR.MICRO` | `code.claude.com/docs/en/plugins-reference.md` | UNCLEAR — docs say "Semantic version" but format is free-text; CalVer accepted de facto |
| 13 | SKILL.md YAML frontmatter keys `name`, `description` | `code.claude.com/docs/en/skills.md` | SUPPORTED |
| 14 | `references/` subdirectory inside skills | `code.claude.com/docs/en/skills.md` | UNCLEAR — docs show `reference.md` single-file; directory is project-specific convention, harmless |
| 15 | `EnterWorktree` / `ExitWorktree` canonical worktree tooling | `code.claude.com/docs/en/tools.md` | SUPPORTED |
| 16 | `Agent` tool with `isolation: "worktree"` | Runtime tool schema (`Agent.parameters.isolation.enum == ["worktree"]`) | SUPPORTED at the runtime level; public `tools.md` does not document the `isolation` parameter explicitly |

### Action items landed in Phase 7 C7

- Removed legacy `MultiEdit` token from `PreToolUse.matcher` (#2).
- Kept `teammate_name` fallback default in `teammate-idle.py` (#7 defensive).
- No refactors required for the UNCLEAR rows — each is either project-local convention (14), defensive dead-code (3), free-text format (12), or runtime-schema-only (16).

### Sub-agent audit evidence

The two `claude-code-guide` sub-agents emitted a security warning about using `WebFetch`/`WebSearch` directly. This is the sub-agent's allowlisted behavior (the agent is specifically designed to fetch docs); the main agent never used WebFetch/WebSearch — it consumed the sub-agent reports, which is the pattern the CLAUDE.md constraint allows.

---

*Version: 2.0.0 | Updated: 2026-04-17*
*Compliant with Agent Teams architecture (RFC 2119)*
