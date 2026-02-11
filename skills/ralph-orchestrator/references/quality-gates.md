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
| `GATE_TEST` | Run test suite | `npm test`, `pytest` |
| `GATE_TYPECHECK` | Type checking | `npm run typecheck`, `mypy src/` |
| `GATE_LINT` | Linting | `npm run lint`, `ruff check .` |
| `GATE_BUILD` | Build validation | `npm run build`, `go build ./...` |

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
1. `GATE_TEST` - Verify behavior
2. `GATE_TYPECHECK` - Catch type errors
3. `GATE_LINT` - Catch style issues
4. `GATE_BUILD` - Ensure it compiles

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

Tasks with `Scenario-Strategy: required` (or field absent) follow full SDD. Tasks classified as `not-applicable` skip GATE_TEST but all other gates still apply.

### Scenario-Strategy Override

Tasks with `Scenario-Strategy: not-applicable` skip GATE_TEST but run all other gates.

| Scenario-Strategy | GATE_TEST | GATE_TYPECHECK | GATE_LINT | GATE_BUILD |
|---|---|---|---|---|
| `required` | Run | Run | Run | Run |
| `not-applicable` | **Skip** | Run | Run | Run |

Default: field absent → `required` (all gates run).

---

## Custom Gates

**Constraints:**
- You MUST modify `hooks/task-completed.py` to add custom gates because the hook only reads the 4 hardcoded gate names (`GATE_TEST`, `GATE_TYPECHECK`, `GATE_LINT`, `GATE_BUILD`)
- You MUST add the corresponding gate command to `.ralph/config.sh` because the hook sources this file for gate commands
- You MUST NOT assume that adding a new `GATE_*` variable to `config.sh` alone will activate it — the hook's `CONFIG_KEYS` list and gate execution logic must also be updated

**Example** (requires both hook and config changes):

```bash
# In .ralph/config.sh — define the command
GATE_E2E="npm run e2e"
```

```python
# In hooks/task-completed.py — add to CONFIG_KEYS and gate execution
CONFIG_KEYS = [
    "GATE_TEST", "GATE_TYPECHECK", "GATE_LINT", "GATE_BUILD",
    "GATE_E2E",  # ← add here
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
- The hook runs all configured gates in order (test → typecheck → lint → build)
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
1. Implementer completes task → automated gates pass (test, typecheck, lint, build)
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

### Circuit Breaker Tripped

If circuit breaker trips (3 failures):
- You MUST review task cycle state for systemic issues
- You SHOULD consider reducing task scope
- You MAY need to update the plan with more specific guidance

---

*Version: 2.0.0 | Updated: 2026-02-10*
*Compliant with Agent Teams architecture (RFC 2119)*
