# Alternative Loops Reference

Beyond standard plan/build, Ralph can run specialized loops.

## Test Coverage Loop

Find uncovered code and write tests systematically.

### Setup

```markdown
# specs/coverage.md
Target: 80% line coverage
Focus: src/core/*.ts (critical paths)
Ignore: src/generated/*, *.test.ts
```

### Prompt Modification

```markdown
## Phase 1: Find Uncovered Lines
Run: npm run coverage -- --reporter=json
Parse coverage report, select ONE uncovered function.

## Phase 2: Write Test
TDD still applies: test must fail first, then pass.

## Phase 3: Validate
Coverage must increase. If not -> Sign + exit.
```

---

## Linting Loop

Fix lint errors one at a time with fresh context.

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

1. Define clear **selection criteria** (what to work on)
2. Define **validation gate** (how to know it worked)
3. Define **exit condition** (when to stop)

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
2. Each iteration runs all `passes` commands
3. Loop continues until ALL pass
4. Human doesn't need to define "done" - spec does
