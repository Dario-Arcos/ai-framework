# Example: Auto Fix Loop

Complete flow showing the auto fix loop: issues found → auto fix → re-review → success.

---

## Phase 1: Context Display

```
📊 PR Context
   From: feature/payment-validation → To: main
   Commits: 2
   ΔLOC: +78 -15 (Δ63)
   Type: feat

Commits:
- a1b2c3d feat(payments): add card validation logic
- e4f5g6h test(payments): add validation tests
```

---

## Phase 2: Quality Gate Results (First Pass)

```
## Quality Gate Results

### Code Review: Not ready - Critical issues

**Top Issues:**
1. [Critical] src/payments/validator.ts:23 - SQL injection vulnerability in card lookup
2. [Important] src/payments/validator.ts:45 - Card number logged in plaintext
3. [Minor] src/payments/validator.ts:8 - Unused import

**Strengths:**
- Good test structure
- Clear separation of validation logic

### Observations

| Check | Status | Detail |
|-------|--------|--------|
| Tests | ✅ | 1 test file added |
| Secrets | ✅ | No secrets detected |
| API Changes | ✅ | No API changes |
| Breaking | ✅ | No BREAKING commits |
| Complexity | ✅ | S: Δ63 ≤ 80 |

### Summary
2 need attention (1 Critical, 1 Important), 4 OK
⚠️ Blockers detected - review before proceeding
```

---

## User Decision (First)

**Question:** "Quality gate complete. How to proceed?"

**User selects:** "Auto fix"

---

## Phase 2b: Auto Fix Execution

### 2b.1 Fix List Prepared

```json
[
  {
    "severity": "Critical",
    "file": "src/payments/validator.ts",
    "line": 23,
    "problem": "SQL injection vulnerability in card lookup",
    "suggestion": "Use parameterized query instead of string concatenation"
  },
  {
    "severity": "Important",
    "file": "src/payments/validator.ts",
    "line": 45,
    "problem": "Card number logged in plaintext",
    "suggestion": "Mask card number, show only last 4 digits"
  }
]
```

### 2b.2 Fix Subagent Dispatched

Subagent receives prompt and executes fixes...

### 2b.3 Fix Subagent Report

```
## Fix Report

**Files modified:**
- src/payments/validator.ts

**Fixes applied:**
1. [Critical] Line 23: Replaced string concatenation with parameterized query using prepared statement
2. [Important] Line 45: Added maskCardNumber() helper, now logs "****-****-****-1234"

**Pushbacks:** None

**Test results:** All 12 tests passing

**Commit created:**
fix: address pre-PR review findings
```

---

## Phase 2: Quality Gate Results (Second Pass)

*Loop returns to Phase 2.1 - code-reviewer dispatched again*

```
## Quality Gate Results

### Code Review: Ready to merge

**Strengths:**
- Security issues properly addressed
- Good test structure
- Clear separation of validation logic
- Proper data masking implemented

### Observations

| Check | Status | Detail |
|-------|--------|--------|
| Tests | ✅ | 1 test file, all passing |
| Secrets | ✅ | No secrets detected |
| API Changes | ✅ | No API changes |
| Breaking | ✅ | No BREAKING commits |
| Complexity | ✅ | S: Δ68 ≤ 80 |

### Summary
0 need attention, 5 OK
```

---

## User Decision (Second)

**Question:** "Quality gate complete. How to proceed?"

**User selects:** "Create PR"

---

## Phase 3: PR Created

```
✅ PR Created

URL: https://github.com/org/repo/pull/144
Branch: feature/payment-validation → main
Commits: 3 (including fix commit)
Quality Gate: 0 addressed, 5 OK
```

---

## Key Points

1. **User always in control**: Loop only continues if user selects "Auto fix"
2. **Re-review after fix**: Code-reviewer runs again to verify fixes
3. **User decides again**: After re-review, user chooses next action
4. **Exit anytime**: User can select "Cancel" at any decision point
