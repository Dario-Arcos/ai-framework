# Example: Auto Fix Loop (With Verification)

Complete flow showing the virtuous cycle: detection → verification → implementation → re-validation → success.

**Key concept:** The inline verification protocol verifies each issue before implementing, catching false positives.

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

### Code Review: Ready with minor improvements

**Top Issues:**
1. [Important] src/payments/validator.ts:45 - Card number logged in plaintext
2. [Minor] src/payments/validator.ts:8 - Unused import

**Strengths:**
- Good test structure
- Clear separation of validation logic

### Security Review: 1 High, 0 Medium

**Vulnerabilities:**
1. [High] src/payments/validator.ts:23 - SQL injection vulnerability in card lookup
   - String concatenation in SQL query allows injection
   - Fix: Use parameterized queries with placeholders

### Observations

| Check | Status | Detail |
|-------|--------|--------|
| Tests | ✅ | 1 test file added |
| API Changes | ✅ | No API changes |
| Breaking | ✅ | No BREAKING commits |
| Complexity | ✅ | S: Δ63 ≤ 80 |

### Summary
2 issues (1 High Security, 1 Important), 0 observations need attention
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
    "severity": "High (Security)",
    "source": "Security Review",
    "file": "src/payments/validator.ts",
    "line": 23,
    "problem": "SQL injection vulnerability in card lookup",
    "suggestion": "Use parameterized query instead of string concatenation"
  },
  {
    "severity": "Important",
    "source": "Code Review",
    "file": "src/payments/validator.ts",
    "line": 45,
    "problem": "Card number logged in plaintext",
    "suggestion": "Mask card number, show only last 4 digits"
  },
  {
    "severity": "Medium (Security)",
    "source": "Security Review",
    "file": "src/payments/validator.ts",
    "line": 67,
    "problem": "Potential timing attack in card comparison",
    "suggestion": "Use constant-time comparison function"
  }
]
```

### 2b.2 Verify and Apply Fixes

**Run inline verification protocol** for each issue before implementing:

```
Issues to verify (from code-reviewer + security-reviewer):
1. [High (Security)] SQL injection at validator.ts:23
2. [Important] Card number logging at validator.ts:45
3. [Medium (Security)] Timing attack at validator.ts:67
```

**Verification output:**

```
Processing 3 issues with verification...

1/3 [High (Security)] SQL injection - src/payments/validator.ts:23
    READ: Line 23 shows `const query = "SELECT * FROM cards WHERE num=" + cardNum`
    VERIFY: ✅ Confirmed - direct string concatenation with user input
    EVALUATE: ✅ Parameterized query is the correct fix
    → Implementing: Changed to prepared statement with placeholder
    TEST: ✅ All 12 tests passing
    → ✅ Fixed

2/3 [Important] Card number logging - src/payments/validator.ts:45
    READ: Line 45 shows `console.log("Processing: " + cardNumber)`
    VERIFY: ✅ Confirmed - full 16-digit card number in logs
    EVALUATE: ✅ Masking approach is correct
    → Implementing: Added maskCard() helper, logs "****-****-****-1234"
    TEST: ✅ All 12 tests passing
    → ✅ Fixed

3/3 [Medium (Security)] Timing attack - src/payments/validator.ts:67
    READ: Lines 65-70 show card validation logic
    VERIFY: ⚠️ Line 67 uses `crypto.timingSafeEqual()` already
    EVALUATE: This is a FALSE POSITIVE - constant-time comparison exists
    → ⚠️ Skipped: False positive - timingSafeEqual already in use at line 67
```

### 2b.3 Commit Verified Fixes

```bash
git add src/payments/validator.ts && git commit -m "fix: address verified pre-PR review findings

Applied (verified):
- [High] SQL injection in validator.ts:23 - parameterized query
- [Important] Card number logging in validator.ts:45 - masked output

Skipped (false positive):
- [Medium] Timing attack - already uses timingSafeEqual at line 67"
```

---

## Phase 2: Quality Gate Results (Second Pass)

*Loop returns to Phase 2.1 - BOTH code-reviewer AND security-reviewer dispatched in parallel*

```
## Quality Gate Results

### Code Review: Ready to merge

**Strengths:**
- Good test structure
- Clear separation of validation logic
- Proper data masking implemented

### Security Review: 0 High, 0 Medium

✅ No security vulnerabilities detected (SQL injection fixed)

### Observations

| Check | Status | Detail |
|-------|--------|--------|
| Tests | ✅ | 1 test file, all passing |
| API Changes | ✅ | No API changes |
| Breaking | ✅ | No BREAKING commits |
| Complexity | ✅ | S: Δ68 ≤ 80 |

### Summary
0 issues, 0 observations need attention
✅ All checks passed
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
Quality Gate: 0 issues, 4 observations OK
```

---

## Key Points

1. **User always in control**: Loop only continues if user selects "Auto fix"
2. **Parallel detection**: Code-reviewer AND security-reviewer run in parallel
3. **Verified fixes**: Inline verification protocol verifies each issue before implementing
4. **False positive filtering**: Verification catches issues that don't exist (like the timing attack)
5. **Re-validation**: BOTH reviewers run again after fixes to ensure quality
6. **Natural loop exit**: When both reviews return clean, user selects "Create PR"
7. **Exit anytime**: User can select "Cancel" at any decision point

## The Virtuous Cycle in Action

```
Detection: 3 issues found (1 High, 1 Important, 1 Medium)
    │
    ▼
Verification: 1 false positive caught (timing attack)
    │
    ▼
Implementation: 2 valid fixes applied
    │
    ▼
Re-validation: 0 issues remaining
    │
    ▼
Result: Clean PR with verified, high-quality fixes
```
