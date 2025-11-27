# Expected Findings - Git Pull Request Skill Validation

Expected behavior when running `/git-pullrequest main` on this test branch with 3-layer review architecture.

---

## Phase 1: Validation & Context

### Expected Output

```
📊 PR Context
   From: test/git-pullrequest-validation → To: main
   Commits: 1
   ΔLOC: ~1200+ (triggers XL complexity)
   Type: test
   Format: Corporate (TEST-123)

Commits:
- [hash] test|TEST-123|20251127|test cases with BREAKING changes for validation
```

**✅ PASS if:**
- Corporate format detected: `TEST-123`
- ΔLOC > 600 (triggers XL)
- Primary type: `test`

---

## Phase 2.1: Parallel Reviews

### Expected Code Review Findings

#### Critical Issues
- SQL injection in `06-mixed-severity/critical.js:13` (findUserByEmail)
- SQL injection in `06-mixed-severity/critical.js:19` (searchUsers)

#### Important Issues
- Missing error handling in `06-mixed-severity/important.js:17` (uploadFile)
- Unhandled promise rejection in `06-mixed-severity/important.js:24` (processUpload)

#### Minor Issues
- Magic number 60000 in `06-mixed-severity/minor.js:15`
- Magic number 100 in `06-mixed-severity/minor.js:18`
- Magic number 3600000 in `06-mixed-severity/minor.js:28`

**✅ PASS if:**
- 2 Critical issues detected
- 2 Important issues detected
- 3 Minor issues detected

### Expected Security Review Findings

#### High Severity
- Hardcoded API_KEY in `02-security-secrets/config.js:17`
- Hardcoded SECRET_KEY in `02-security-secrets/config.js:18`
- Hardcoded GITHUB_TOKEN in `02-security-secrets/config.js:24`
- Hardcoded PRIVATE_KEY in `02-security-secrets/config.js:25`
- SQL injection (should also be detected here)

**✅ PASS if:**
- At least 4 High severity issues detected (secrets)
- SQL injections identified as security vulnerabilities

---

## Phase 2.2: Observations

### Expected Observations Table

| Observation | Expected Status | Reason |
|-------------|-----------------|--------|
| **Tests** | ⚠️ | `03-no-tests/payment.js` has no corresponding test file |
| **API Changes** | ✅ or ⚠️ | `routes.js` might trigger (depends on path detection) |
| **Breaking** | ⚠️ | Commit message contains "BREAKING" keyword |
| **Complexity** | ⚠️ | ΔLOC ~1200 > 600 (XL budget) |

**✅ PASS if:**
- Tests observation flagged
- Breaking observation flagged
- Complexity observation flagged XL
- NO Secrets observation (handled by security review)

---

## Phase 2.3: Consolidated Findings

### Expected Structure

```json
{
  "code_review": {
    "assessment": "Not ready - Critical issues",
    "critical_count": 2,
    "important_count": 2,
    "minor_count": 3,
    "strengths": [...],
    "issues": [...]
  },
  "security_review": {
    "high_count": 4+,
    "medium_count": 0+,
    "issues": [...]
  },
  "observations": {
    "tests": { "status": "⚠️", "detail": "..." },
    "api": { "status": "✅" or "⚠️", "detail": "..." },
    "breaking": { "status": "⚠️", "detail": "..." },
    "complexity": { "status": "⚠️", "detail": "XL: Δ~1200 > 600" }
  },
  "summary": {
    "has_blockers": true,
    "total_issues": 9+,
    "attention_count": 3+
  }
}
```

**✅ PASS if:**
- `has_blockers = true` (Critical issues + High security issues)
- `total_issues >= 9`

---

## Phase 2.4: Present Findings

### Expected Display

```
## Quality Gate Results

### Code Review: Not ready - Critical issues

**Top Issues:**
1. [Critical] 06-mixed-severity/critical.js:13 - SQL injection in findUserByEmail
2. [Critical] 06-mixed-severity/critical.js:19 - SQL injection in searchUsers
3. [Important] 06-mixed-severity/important.js:17 - Missing error handling

**Strengths:**
- Clean logger implementation with proper constants
- Comprehensive test coverage for logger module

### Security Review: 4+ High, 0+ Medium

**Top Vulnerabilities:**
1. [High] 02-security-secrets/config.js:17 - Hardcoded API_KEY
2. [High] 02-security-secrets/config.js:24 - Hardcoded GITHUB_TOKEN
3. [High] 06-mixed-severity/critical.js:13 - SQL injection vulnerability

### Observations

| Check | Status | Detail |
|-------|--------|--------|
| Tests | ⚠️ | Source files without tests detected |
| API Changes | ✅ or ⚠️ | ... |
| Breaking | ⚠️ | BREAKING in commit message |
| Complexity | ⚠️ | XL: Δ~1200 > 600 |

### Summary
9+ issues found, 3+ observations need attention
⚠️ Blockers detected - review before proceeding
```

**✅ PASS if output matches this structure with security review visible**

---

## Phase 2.5: User Decision

### Expected Options

```
Question: "Quality gate complete. How to proceed?"
Header: "PR Decision"
Options:
  - label: "Create PR"
    description: "Push branch and create PR with current findings documented"
  - label: "Auto fix"
    description: "Subagent fixes Critical+Important+High+Medium security issues, then re-review"
  - label: "Cancel"
    description: "Exit. Fix manually and re-run /git-pullrequest main"
```

**✅ PASS if:**
- 3 options presented
- Auto fix description mentions security issues

---

## Auto Fix Validation (If Selected)

### Expected Fix List

Should include issues from BOTH sources:

```json
[
  { "severity": "Critical", "source": "Code Review", "file": "06-mixed-severity/critical.js", "line": 13, ... },
  { "severity": "Critical", "source": "Code Review", "file": "06-mixed-severity/critical.js", "line": 19, ... },
  { "severity": "Important", "source": "Code Review", "file": "06-mixed-severity/important.js", "line": 17, ... },
  { "severity": "Important", "source": "Code Review", "file": "06-mixed-severity/important.js", "line": 24, ... },
  { "severity": "High (Security)", "source": "Security Review", "file": "02-security-secrets/config.js", ... },
  ...
]
```

### Re-Review After Fix

Should dispatch BOTH reviews in parallel:
- code-reviewer (verify fixes didn't break logic)
- security-reviewer (verify vulnerabilities eliminated)

**✅ PASS if:**
- Both reviews run in parallel
- Second pass shows 0 Critical, 0 Important, 0 High, 0 Medium
- User gets decision again (natural loop exit)

---

## Create PR Validation

### Expected PR Body

Should include BOTH reviews:

```markdown
## Pre-PR Quality Gate

### Code Review: {assessment}

**Strengths:** ...

**Issues Addressed:** ...

### Security Review: {high_count} High, {medium_count} Medium

{Vulnerabilities resolved or acknowledged}

### Observations

| Check | Status |
|-------|--------|
| Tests | {status} |
| API Changes | {status} |
| Breaking Changes | {status} |
| Complexity | {status} |
```

**✅ PASS if:**
- Security Review section present in PR body
- Corporate format (TEST-123) in summary
- All findings documented

---

## Final Validation Checklist

- [ ] **Phase 1**: Corporate format detected correctly
- [ ] **Phase 2.1**: TWO reviews run in parallel
- [ ] **Code Review**: 2 Critical, 2 Important, 3 Minor
- [ ] **Security Review**: 4+ High (secrets + SQL injection)
- [ ] **Observations**: 4 checks, NO Secrets check
- [ ] **Consolidation**: 3 sources merged correctly
- [ ] **User Decision**: 3 options, security mentioned in Auto fix
- [ ] **Auto Fix** (if tested): Fix list includes both code + security issues
- [ ] **Re-Review** (if tested): Both reviews run in parallel
- [ ] **PR Body** (if tested): Includes security review section

---

## Notes

- This is a comprehensive stress test with intentionally bad code
- Expected: Multiple blockers from BOTH code and security reviews
- Skill should dispatch reviews in PARALLEL (single message, 2 Task calls)
- Loop exits naturally when both reviews return clean
