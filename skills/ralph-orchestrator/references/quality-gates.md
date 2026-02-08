# Quality Gates Reference

## Overview

This reference defines quality gates for ralph-orchestrator execution. Gates apply backpressure to ensure code quality without prescribing implementation details. Workers determine "how" while gates verify "what".

**Core Philosophy**: Backpressure Over Prescription - Create gates that reject bad work rather than dictating how workers should implement.

---

## Available Gates

**Constraints:**
- You MUST configure appropriate gates for your quality level because missing gates allow defects through
- You SHOULD use project-specific commands because generic commands may miss project conventions

| Gate | Purpose | Example Command |
|------|---------|-----------------|
| `GATE_TEST` | Run test suite | `npm test`, `pytest` |
| `GATE_TYPECHECK` | Type checking | `npm run typecheck`, `mypy src/` |
| `GATE_LINT` | Linting | `npm run lint`, `ruff check .` |
| `GATE_BUILD` | Build validation | `npm run build`, `go build ./...` |
| `GATE_SECURITY` | Security scan | `npm audit`, `safety check` |

---

## Gate Configuration by Quality Level

### Prototype

**Constraints:**
- You MAY skip all gates when rapid iteration is required
- You MUST NOT use prototype level for production code because untested code causes production failures

```bash
QUALITY_LEVEL="prototype"
# All gates skipped
# Commits freely
# Use for: rapid iteration, proof of concept
```

### Production (Default)

**Constraints:**
- You MUST pass GATE_TEST before committing because untested code has higher defect rates
- You MUST pass GATE_TYPECHECK because type errors cause runtime failures
- You MUST pass GATE_LINT because style violations reduce code readability
- You MUST pass GATE_BUILD because build failures indicate broken code

```bash
QUALITY_LEVEL="production"
# GATE_TEST: Required
# GATE_TYPECHECK: Required
# GATE_LINT: Required
# GATE_BUILD: Required
# Use for: most development work
```

### Library

**Constraints:**
- You MUST achieve 100% test coverage because library users depend on complete testing
- You MUST complete documentation because undocumented libraries cannot be adopted
- You MUST test edge cases because library users encounter scenarios you didn't anticipate

```bash
QUALITY_LEVEL="library"
# All production gates PLUS:
# - 100% test coverage required
# - Documentation must be complete
# - Edge cases must be tested
# Use for: published packages, critical infrastructure
```

---

## Gate Execution Order

**Constraints:**
- You MUST execute gates in order because earlier gates catch simpler issues faster
- You MUST NOT skip to later gates because failed early gates invalidate later results

**Order:**
1. `GATE_LINT` - Catch style issues early
2. `GATE_TYPECHECK` - Catch type errors
3. `GATE_TEST` - Verify behavior
4. `GATE_BUILD` - Ensure it compiles
5. `GATE_SECURITY` - Final security check

If any gate fails, worker must fix before proceeding.

---

## SDD Gate Enforcement

**Constraints:**
- You MUST write scenarios before implementation in production/library mode because SDD ensures testable design
- You MUST see scenario fail first (scenario) because passing scenarios prove nothing without failure
- You MUST implement minimal code to satisfy (satisfy) because over-implementation adds unnecessary complexity
- You MUST refactor while satisfied because refactoring on unsatisfied risks breaking functionality
- You MUST NOT skip SDD steps because gates reject work that bypasses the cycle

**SDD Cycle:**
1. Scenario must be defined first
2. Scenario must fail first (scenario)
3. Implementation satisfies the scenario (satisfy)
4. Refactor while satisfied

Workers that skip SDD have their work rejected by gates.

---

## Custom Gates

**Constraints:**
- You MAY add custom gates for project-specific requirements
- You MUST add custom gates to `.ralph/config.sh` because this ensures they persist

```bash
# E2E tests
GATE_E2E="npm run e2e"

# Performance check
GATE_PERF="npm run benchmark"

# Documentation check
GATE_DOCS="npm run docs:check"
```

---

## Gate Failure Handling

**Constraints:**
- You MUST provide failure output to workers because they need context to fix issues
- You MUST allow workers to attempt fixes because automated retries often succeed
- You MUST trip circuit breaker after 3 consecutive failures because infinite loops waste resources

**Process:**
1. Worker receives failure output
2. Worker attempts fix
3. Worker re-runs gate
4. If 3 consecutive failures, circuit breaker trips

---

## Double Completion Verification

**Constraints:**
- You MUST require two consecutive COMPLETE signals because single signals may be premature
- You MUST NOT accept completion on first signal because workers often claim done before actual completion

**Process:**
- Single `<promise>COMPLETE</promise>` enters pending state
- Requires **two consecutive** COMPLETE signals to confirm
- Prevents premature "done" claims

---

## Troubleshooting

### Gates Failing Unexpectedly

If gates fail but code appears correct:
- You SHOULD check environment setup (node version, dependencies installed)
- You SHOULD run gates manually to see full output
- You MAY have missing test fixtures or configuration

### Workers Stuck in Gate Loop

If workers repeatedly fail the same gate:
- You SHOULD review the task specification for clarity issues
- You SHOULD check if prerequisites are missing
- You MUST NOT implement fixes as orchestrator because this violates role boundaries

### Circuit Breaker Tripped

If circuit breaker trips (3 failures):
- You MUST review loop state for systemic issues
- You SHOULD consider reducing task scope
- You MAY need to update the plan with more specific guidance

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
