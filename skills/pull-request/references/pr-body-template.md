# PR Body Template

Fill placeholders from working memory. Remove conditional blocks that don't apply.

---

## Summary

{primary_type} changes affecting **{files_changed}** files ({delta_loc} LOC).
{If is_corporate: "**Task:** {corp_task_id}"}

## Changes ({commit_count} commits)

{commit_list}

## Pre-PR Quality Gate

### Code Review: {cr_assessment}

**Strengths:**
{cr_strengths as bullet list}

{If cr_issues or sr_issues exist:}
**Issues Addressed:**
{List code review issues that were fixed or acknowledged}
{List security issues that were fixed or acknowledged}

### Security Review: {sr_high_count} High, {sr_medium_count} Medium

{If sr_issues: List resolved/acknowledged security findings}
{Else: "No security vulnerabilities detected"}

### Observations

| Check | Status |
|-------|--------|
| Tests | {status} |
| API Changes | {status} |
| Breaking Changes | {status} |
| Complexity | {status} ({size}: {delta_loc}) |

## Test Plan

{Select ONE checklist based on primary_type:}

**feat:**
- [ ] New functionality tested
- [ ] Tests added
- [ ] Docs updated

**fix:**
- [ ] Bug reproduced before fix
- [ ] Regression test added
- [ ] Verified in staging

**refactor:**
- [ ] Existing tests pass
- [ ] Functionality unchanged

**other (docs, chore, ci, etc.):**
- [ ] Changes verified
- [ ] Build successful
