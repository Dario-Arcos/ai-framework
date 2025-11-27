# Example: Code Review with Findings (User Proceeds)

Flow when code review finds issues but user decides to create PR anyway.

---

## Phase 1: Context Display

```
📊 PR Context
   From: feature/oauth-integration → To: main
   Commits: 3
   ΔLOC: +189 -23 (Δ166)
   Type: feat

Commits:
- a1b2c3d feat(auth): add OAuth2 provider integration
- e4f5g6h feat(auth): implement token refresh logic
- i7j8k9l test(auth): add OAuth2 integration tests
```

---

## Phase 2: Quality Gate Results

```
## Quality Gate Results

### Code Review: Ready to merge with fixes

**Top Issues:**
1. [Important] src/auth/oauth.ts:45 - Token stored in localStorage (security concern)
2. [Important] src/auth/oauth.ts:78 - Missing error handling for refresh failure
3. [Minor] src/auth/oauth.ts:12 - Magic number 3600, extract to constant

**Strengths:**
- Clean separation between OAuth providers
- Comprehensive error handling for most scenarios
- Good test coverage for happy paths

### Observations

| Check | Status | Detail |
|-------|--------|--------|
| Tests | ✅ | 2 test files modified |
| Secrets | ✅ | No secrets detected |
| API Changes | ⚠️ | 2 files in api/auth/ |
| Breaking | ✅ | No BREAKING commits |
| Complexity | ✅ | M: Δ166 ≤ 250 |

### Summary
3 need attention (2 Important, 1 Minor), 4 OK
```

---

## User Decision

**Question:** "Quality gate complete. How to proceed?"

**User selects:** "Create PR"

*(User decides to document issues in PR and address in follow-up)*

---

## Phase 3: PR Created

```
✅ PR Created

URL: https://github.com/org/repo/pull/143
Branch: feature/oauth-integration → main
Commits: 3
Quality Gate: 3 addressed, 4 OK
```

---

## PR Body Generated

```markdown
## Summary

feat changes affecting **5** files (Δ166 LOC).

## Changes (3 commits)

- a1b2c3d feat(auth): add OAuth2 provider integration
- e4f5g6h feat(auth): implement token refresh logic
- i7j8k9l test(auth): add OAuth2 integration tests

## Pre-PR Quality Gate

### Code Review: Ready to merge with fixes

**Strengths:**
- Clean separation between OAuth providers
- Comprehensive error handling for most scenarios
- Good test coverage for happy paths

**Issues Addressed:**
- [Important] Token storage: Documented as tech debt, follow-up ticket TRV-456
- [Important] Refresh error handling: Added fallback, needs review
- [Minor] Magic number: Acknowledged, will refactor in next PR

### Observations

| Check | Status |
|-------|--------|
| Tests | ✅ |
| Secrets | ✅ |
| API Changes | ⚠️ New endpoints in api/auth |
| Breaking Changes | ✅ |
| Complexity | ✅ (M: Δ166) |

## Test Plan

- [x] New functionality tested
- [x] Tests added
- [ ] Docs updated
```

---

## Findings Structure (Internal)

```json
{
  "code_review": {
    "assessment": "Ready to merge with fixes",
    "critical_count": 0,
    "important_count": 2,
    "minor_count": 1,
    "strengths": [
      "Clean separation between OAuth providers",
      "Comprehensive error handling for most scenarios"
    ],
    "issues": [
      {
        "severity": "Important",
        "file": "src/auth/oauth.ts",
        "line": 45,
        "what": "Token stored in localStorage",
        "fix": "Use httpOnly cookie or secure storage"
      },
      {
        "severity": "Important",
        "file": "src/auth/oauth.ts",
        "line": 78,
        "what": "Missing error handling for refresh failure",
        "fix": "Add try-catch and fallback to re-auth"
      },
      {
        "severity": "Minor",
        "file": "src/auth/oauth.ts",
        "line": 12,
        "what": "Magic number 3600",
        "fix": "Extract to TOKEN_EXPIRY_SECONDS constant"
      }
    ]
  },
  "observations": {
    "tests": { "status": "✅", "detail": "2 test files modified" },
    "secrets": { "status": "✅", "detail": "No secrets detected" },
    "api": { "status": "⚠️", "detail": "2 files in api/auth/" },
    "breaking": { "status": "✅", "detail": "No BREAKING commits" },
    "complexity": { "status": "✅", "detail": "M: Δ166 ≤ 250" }
  },
  "summary": {
    "has_blockers": false,
    "attention_count": 3,
    "ok_count": 4
  }
}
```
