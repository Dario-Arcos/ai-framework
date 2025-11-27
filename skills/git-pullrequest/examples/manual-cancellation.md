# Example: Manual Cancellation

Flow when user decides to cancel and fix issues manually.

---

## Phase 1: Context Display

```
📊 PR Context
   From: feature/database-migration → To: main
   Commits: 4
   ΔLOC: +892 -156 (Δ736)
   Type: feat

Commits:
- a1b2c3d feat(db): add new user schema
- e4f5g6h feat(db): implement migration scripts
- i7j8k9l feat(db): add rollback procedures
- m0n1o2p chore(db): update seed data
```

---

## Phase 2: Quality Gate Results

```
## Quality Gate Results

### Code Review: Not ready - Critical issues

**Top Issues:**
1. [Critical] migrations/002_users.sql:45 - DROP TABLE without backup verification
2. [Critical] migrations/002_users.sql:78 - Missing transaction wrapper
3. [Important] src/db/migrate.ts:23 - No connection pooling configured
4. [Important] src/db/migrate.ts:89 - Hardcoded timeout value

**Strengths:**
- Comprehensive rollback procedures
- Good documentation in migration files

### Security Review: 0 High, 0 Medium

✅ No security vulnerabilities detected

### Observations

| Check | Status | Detail |
|-------|--------|--------|
| Tests | ⚠️ | 4 src files, 0 test files |
| API Changes | ✅ | No API changes |
| Breaking | ⚠️ | BREAKING CHANGE in commit message |
| Complexity | ⚠️ | XL: Δ736 > 600 |

### Summary
4 code review issues (2 Critical, 2 Important), 2 observations need attention
⚠️ Blockers detected - review before proceeding
```

---

## User Decision

**Question:** "Quality gate complete. How to proceed?"

**User selects:** "Cancel"

---

## Exit Response

```
❌ PR creation cancelled.

## Issues to Address

### Critical (must fix)
1. migrations/002_users.sql:45 - DROP TABLE without backup verification
   → Add backup verification step before DROP
2. migrations/002_users.sql:78 - Missing transaction wrapper
   → Wrap migration in BEGIN/COMMIT transaction

### Important (should fix)
3. src/db/migrate.ts:23 - No connection pooling configured
   → Configure connection pool with max connections
4. src/db/migrate.ts:89 - Hardcoded timeout value
   → Extract to environment variable

### Observations
- ⚠️ Tests: Consider adding migration tests
- ⚠️ Breaking: Document breaking changes in CHANGELOG
- ⚠️ Complexity: Consider splitting into smaller PRs

## Next Steps

Fix the issues above, then re-run:
/git-pullrequest main
```

---

## Key Points

1. **Clean exit**: User can cancel at any time
2. **Actionable summary**: Issues listed with file:line and suggestions
3. **Re-run instructions**: Clear path to continue after manual fixes
4. **No partial state**: Nothing pushed, no PR created

---

## Alternative Scenario: Cancel After Fix Attempt

If user selects "Auto fix" first, then "Cancel" on second review:

```
❌ PR creation cancelled.

## Partial Progress

Fix commit created: fix: address pre-PR review findings
1 Critical issue resolved, 1 Critical remaining

## Remaining Issues

### Critical
1. migrations/002_users.sql:78 - Missing transaction wrapper
   → Subagent could not safely add transaction (requires manual review)

## Next Steps

Review the fix commit, address remaining issues manually, then re-run:
/git-pullrequest main
```
