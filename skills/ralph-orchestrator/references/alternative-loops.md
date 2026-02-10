# Alternative Loops Reference

## Overview

This reference defines alternative loop patterns beyond standard plan/build. These specialized loops provide targeted approaches for specific maintenance tasks like test coverage, linting, and entropy reduction.

---

## Test Coverage Loop

Find uncovered code and write tests systematically.

**Constraints:**
- You MUST define target coverage percentage before starting because this sets completion criteria
- You MUST specify focus directories (critical paths) because comprehensive coverage is impractical
- You MUST define ignore patterns because generated files and tests should be excluded
- You SHOULD run coverage with JSON reporter because automated parsing requires structured output

### Setup

```markdown
# specs/coverage.md
Target: 90% line coverage
Focus: src/core/*.ts (critical paths)
Ignore: src/generated/*, *.test.ts
```

### Prompt Modification

**Constraints:**
- You MUST select ONE uncovered function per task cycle because batch processing loses focus
- You MUST apply SDD (scenario must be defined first) because this validates scenario correctness
- You MUST verify coverage increases because stagnant coverage indicates stuck loop

```markdown
## Phase 1: Find Uncovered Lines
Run: npm run coverage -- --reporter=json
Parse coverage report, select ONE uncovered function.

## Phase 2: Write Test
SDD still applies: scenario must fail first, then pass.

## Phase 3: Validate
Coverage must increase. If not -> Sign + exit.
```

---

## Linting Loop

Fix lint errors one at a time with fresh context via sub-agents.

**Constraints:**
- You MUST fix ONE error per task cycle because batch fixes introduce new errors
- You MUST verify lint count decreases because stagnant count indicates configuration issues
- You MUST NOT batch multiple lint fixes because cross-file fixes create conflicts

### When to Use

- 500+ lint errors after enabling new rules
- Codemod failed partially
- Need consistent style changes

### Prompt Modification

```markdown
## Task Selection
Run: npm run lint -- --format=json | head -1
Fix ONE error completely. Don't batch.

## Validation
Lint error count must decrease by >=1.
Same error type appearing -> Sign + exit.
```

---

## Entropy Loop

Reduce code smells and technical debt methodically.

**Constraints:**
- You MUST measure before refactoring because baseline metrics quantify improvement
- You MUST select ONE smell with highest impact because prioritization maximizes value
- You MUST ensure tests pass after refactoring because refactoring must preserve behavior

### Targets

- Dead code removal
- Unused imports
- Duplicate functions
- Complex conditionals (cyclomatic complexity)

### Prompt Modification

```markdown
## Phase 1: Measure
Run static analysis tool (e.g., `npm run analyze`).
Select ONE smell with highest impact.

## Phase 2: Refactor
Apply standard refactoring patterns.
Tests must still pass.

## Phase 3: Validate
Complexity metric must improve.
```

---

## Creating Custom Loops

**Constraints:**
- You MUST define clear selection criteria because sub-agents need unambiguous task selection
- You MUST define validation gate because completion requires measurable verification
- You MUST define exit condition because infinite loops waste resources

### Template

```markdown
## Phase 1: Select
[How to find next item to fix]

## Phase 2: Execute
[What to do with the item]

## Phase 3: Validate
[Metric that must improve]
[Exit condition if stuck]
```

---

## Spec-Driven Loop

Define acceptance criteria upfront with a `passes` field.

**Constraints:**
- You MUST include `passes` field in spec because this defines completion
- You MUST list all validation commands because incomplete validation misses failures
- You SHOULD use specific test filters because full test suite may timeout

### Setup

```markdown
# specs/feature.md
## Acceptance Criteria
passes:
  - npm test -- --grep "feature-name"
  - npm run lint
  - curl localhost:3000/api/feature returns 200
```

### How It Works

1. Ralph reads spec with `passes` field
2. Each task cycle runs all `passes` commands
3. Loop continues until ALL pass
4. Human doesn't need to define "done" - spec does

---

## Troubleshooting

### Coverage Not Increasing

If coverage remains stagnant:
- You SHOULD verify test actually runs the target code
- You SHOULD check coverage tool configuration includes target files
- You MUST exit with Sign if same function fails 3 times

### Lint Loop Creates New Errors

If fixing one error creates another:
- You SHOULD check if rules conflict with each other
- You SHOULD fix rule configuration before continuing
- You MUST NOT continue loop if error count oscillates

### Custom Loop Never Exits

If custom loop runs indefinitely:
- You SHOULD verify exit condition is reachable
- You SHOULD check validation metric is measuring correctly
- You MUST add timeout-based exit as fallback

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
