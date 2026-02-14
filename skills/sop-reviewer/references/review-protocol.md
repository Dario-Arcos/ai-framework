# Review Protocol

Detailed checklists and patterns for SDD review validation.

## SDD Compliance Checklist

### Scenario Ordering (git history evidence)
- [ ] Scenario commit predates or equals implementation commit
- [ ] Scenario text describes user intent, not implementation steps
- [ ] No scenario modifications in same commit as implementation changes
- [ ] Scenario-Strategy field in `.code-task.md` is respected

### Scenario Quality
- [ ] Each scenario uses concrete values (not "some input", "valid data")
- [ ] Each scenario describes end-to-end user story (Given/When/Then or equivalent)
- [ ] Scenarios are independent — no shared mutable state between them
- [ ] Scenarios cover at least: happy path, error path, edge case

### Execution Evidence
- [ ] Test output or command output demonstrating scenario satisfaction
- [ ] Evidence is from actual execution, not "should work" claims
- [ ] Previous scenarios re-executed after new implementation (regression check)
- [ ] Satisfaction reported as fraction `[M/N]`, not boolean

## Acceptance Criteria Coverage Checklist

### Criterion-to-Scenario Mapping
- [ ] ALL acceptance criteria extracted from `.code-task.md`
- [ ] Each criterion mapped to at least one scenario
- [ ] No criterion left as MISSING — gaps are automatic FAIL
- [ ] Mapped scenarios test the criterion's specific requirement, not a proxy

### Assertion Quality (per scenario)
- [ ] Assertions use precise comparisons (exact match, not `toBeTruthy()` or `contains()`)
- [ ] No scenario can be satisfied by a hardcoded return value
- [ ] At least 2 distinct inputs with distinct expected outputs per scenario
- [ ] Assertions verify the user-facing requirement, not internal implementation details

## Reward Hacking Patterns Catalog

### Pattern 1: Scenario Rewriting
**Detection:** `git log --all --oneline -- '*.test.*' '*.spec.*' '*.code-task.md'` shows scenario file modifications during implementation phase.
**Severity:** Critical — automatic FAIL.
**Example:** Changing `expect(result).toBe(42)` to `expect(result).toBe(41)` after implementation returns 41.

### Pattern 2: Trivial Satisfaction
**Detection:** Scenario can be satisfied by constant return value or single-branch logic.
**Severity:** Critical — automatic FAIL.
**Example:** `function isValid() { return true; }` satisfies `expect(isValid(input)).toBe(true)`.
**Mitigation:** Demand variant scenarios with different expected outputs.

### Pattern 3: Precision Evasion
**Detection:** Assertions use loose comparisons or type coercion that mask errors.
**Severity:** Critical — automatic FAIL.
**Examples:**
- `int(result)` instead of exact float comparison
- `string.contains("partial")` instead of exact match
- `expect(result).toBeCloseTo(expected, 0)` with precision 0

### Pattern 4: Code-First Scenarios
**Detection:** Scenarios mirror implementation structure (function names, internal state) rather than user-observable behavior.
**Severity:** Critical — automatic FAIL.
**Symptoms:**
- Scenario steps match function call sequence
- Assertions reference internal variables or private APIs
- Scenarios added in same commit as all implementation code

## Behavioral Satisfaction Criteria

### Convergence Model
Satisfaction is NOT binary. Measure as: "of observed trajectories, what fraction satisfies user intent?"

- **Full convergence (N/N):** All observed execution paths satisfy intent — only passing verdict
- **Partial convergence (M/N, M < N):** Some paths satisfy — automatic FAIL. Identify which fail and why for rework feedback
- **No convergence (0/N):** Implementation does not satisfy — immediate FAIL

### Assessment Dimensions
1. **Functional correctness:** Does output match expected values?
2. **Edge case handling:** Boundaries, empty inputs, max values behave correctly?
3. **Error behavior:** Failures produce useful feedback, not crashes or silent corruption?
4. **UX coherence:** User-facing behavior is consistent and complete?

## Review Output Template

```markdown
# Review: Task {task_id}

## Verdict: {PASS|FAIL}

## SDD Compliance: {PASS|FAIL}
{Checklist results — which items passed/failed}

## Acceptance Criteria Coverage: {PASS|FAIL}
| Criterion | Scenario | Covered? |
|-----------|----------|----------|
{Mapping table — every criterion from .code-task.md}

## Behavioral Satisfaction: [{M}/{N} satisfied]
{Per-scenario assessment with convergence analysis and assertion quality evaluation}

## Reward Hacking: {CLEAN|DETECTED}
{Pattern-by-pattern check results}

## Findings

### Critical
{Blocking issues — must fix before merge}

### Important
{Should fix — may cause problems if ignored}

### Suggestions
{Nice to have — improves quality but not blocking}

## Summary
{Exactly 8 words for lead consumption}
```
