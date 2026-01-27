# Quality Gates

## Gate Philosophy

**Backpressure Over Prescription**: Don't prescribe how workers should implement. Create gates that reject bad work. Workers figure out the "how".

## Available Gates

| Gate | Purpose | Example Command |
|------|---------|-----------------|
| `GATE_TEST` | Run test suite | `npm test`, `pytest` |
| `GATE_TYPECHECK` | Type checking | `npm run typecheck`, `mypy src/` |
| `GATE_LINT` | Linting | `npm run lint`, `ruff check .` |
| `GATE_BUILD` | Build validation | `npm run build`, `go build ./...` |
| `GATE_SECURITY` | Security scan | `npm audit`, `safety check` |

## Gate Configuration by Quality Level

### Prototype

```bash
QUALITY_LEVEL="prototype"
# All gates skipped
# Commits freely
# Use for: rapid iteration, proof of concept
```

### Production (Default)

```bash
QUALITY_LEVEL="production"
# GATE_TEST: Required
# GATE_TYPECHECK: Required
# GATE_LINT: Required
# GATE_BUILD: Required
# Use for: most development work
```

### Library

```bash
QUALITY_LEVEL="library"
# All production gates PLUS:
# - 100% test coverage required
# - Documentation must be complete
# - Edge cases must be tested
# Use for: published packages, critical infrastructure
```

## Gate Execution Order

1. `GATE_LINT` - Catch style issues early
2. `GATE_TYPECHECK` - Catch type errors
3. `GATE_TEST` - Verify behavior
4. `GATE_BUILD` - Ensure it compiles
5. `GATE_SECURITY` - Final security check

If any gate fails, worker must fix before proceeding.

## TDD Gate Enforcement

In production/library mode, TDD is mandatory:

1. **Test must exist before implementation**
2. **Test must fail first** (red)
3. **Implementation makes test pass** (green)
4. **Refactor while green**

Workers that skip TDD have their work rejected by gates.

## Custom Gates

Add custom gates in `.ralph/config.sh`:

```bash
# E2E tests
GATE_E2E="npm run e2e"

# Performance check
GATE_PERF="npm run benchmark"

# Documentation check
GATE_DOCS="npm run docs:check"
```

## Gate Failure Handling

When a gate fails:
1. Worker receives failure output
2. Worker attempts fix
3. Worker re-runs gate
4. If 3 consecutive failures, circuit breaker trips

## Double Completion Verification

Special gate for completion:
- Single `<promise>COMPLETE</promise>` enters pending state
- Requires **two consecutive** COMPLETE signals to confirm
- Prevents premature "done" claims
