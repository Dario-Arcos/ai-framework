# Git Pull Request Skill Test Cases

Comprehensive edge case validation for `git-pullrequest` skill.

## Test Strategy

This commit contains **8 mini code fragments** designed to trigger different observations and code review findings when processed through `/git-pullrequest main`.

## Expected Skill Behavior

When running `/git-pullrequest main` from this branch, the skill should:

### Phase 1: Extract Context
- ✅ Detect corporate format in first commit
- ✅ Extract metadata (files changed, ΔLOC, primary type)
- ✅ Display PR context

### Phase 2: Quality Gate

**Code Review:**
- 🔴 **Critical**: SQL injection in `06-mixed-severity/critical.js`
- ⚠️ **Important**: Missing error handling in `06-mixed-severity/important.js`
- 🟡 **Minor**: Magic number in `06-mixed-severity/minor.js`

**Security Review (parallel):**
- 🔴 **High**: Hardcoded secrets in `02-security-secrets/config.js`
- Should detect: API_KEY, SECRET_KEY, GITHUB_TOKEN, PRIVATE_KEY patterns

**Observations:**
- ⚠️ **Tests**: Flag missing tests for `03-no-tests/payment.js`
- ⚠️ **Breaking**: Detect BREAKING in commit message
- ⚠️ **Complexity**: Flag XL size (ΔLOC > 600)
- ⚠️ **API Changes**: Detect new endpoint in `07-api-changes/routes.js`

### Phase 2.5: User Decision
Expected options:
- Create PR
- Auto fix
- Cancel

## Test Cases by Directory

| Case | Triggers | Expected Detection |
|------|----------|-------------------|
| `01-corporate-format/` | Corporate format commit | Detect `test\|TEST-123\|20251127\|...` |
| `02-security-secrets/` | Hardcoded credentials | 🔴 Security Review: High severity |
| `03-no-tests/` | Source without tests | ⚠️ Tests observation |
| `04-breaking-change/` | API breaking change | ⚠️ Breaking observation |
| `05-complexity-xl/` | >600 LOC file | ⚠️ Complexity XL |
| `06-mixed-severity/` | Multiple issue types | Critical + Important + Minor |
| `07-api-changes/` | New API endpoint | ⚠️ API changes observation |
| `08-perfect-code/` | Clean code + tests | ✅ All checks pass |

## Validation Checklist

After running `/git-pullrequest main`, verify:

- [ ] Corporate format detected and parsed correctly
- [ ] Security review flagged secrets (High severity)
- [ ] Tests observation flagged (⚠️)
- [ ] Breaking changes observation flagged (⚠️)
- [ ] Complexity observation flagged (⚠️)
- [ ] API changes observation flagged (⚠️)
- [ ] Code review found Critical issue (SQL injection)
- [ ] Code review found Important issue (error handling)
- [ ] Code review found Minor issue (magic number)
- [ ] User decision presented: Create PR / Auto fix / Cancel
- [ ] If "Auto fix" selected: subagent dispatched with Critical+Important+High+Medium
- [ ] If "Create PR" selected: PR body includes both code review and security review findings

## Notes

- **Do NOT merge this branch** - it's for testing only
- Delete branch after validation: `git branch -D test/git-pullrequest-validation`
- Expected total ΔLOC: ~1200 lines (triggers XL complexity)
