---
name: git-pullrequest
description: Use when creating a PR - validates changes, dispatches code-reviewer subagent, generates contextual observations, presents consolidated findings, and creates PR with quality documentation. Supports corporate commit format (type|TASK-ID|YYYYMMDD|desc). Human authorizes every decision point.
---

# Git Pull Request Workflow

Create PRs with integrated quality gate. Human always decides.

**Input:** Target branch from `$ARGUMENTS` (e.g., "main").

**Examples:** See `examples/` for complete flow scenarios:
- `success-no-findings.md` - Clean code review, direct to PR
- `success-with-findings.md` - Issues found, user proceeds anyway
- `auto-fix-loop.md` - Auto fix loop with re-review
- `manual-cancellation.md` - User cancels to fix manually

---

## Phase 1: Validate & Extract Context

### 1.1 Validate and Fetch

1. Validate target branch format (alphanumeric, `/`, `-`, `_`)
2. Reject branches starting with `--` (security)
3. Run `git fetch origin --quiet`
4. Verify `origin/{target_branch}` exists
5. Count commits: `git rev-list --count origin/{target}..HEAD`
6. Error if no commits

### 1.2 Extract Metadata

Store in working memory:

| Variable | Command |
|----------|---------|
| `current_branch` | `git branch --show-current` |
| `commit_count` | `git rev-list --count origin/{target}..HEAD` |
| `first_commit` | `git log -1 --pretty=format:'%s' origin/{target}..HEAD` |
| `commit_list` | `git log --pretty=format:'- %h %s' origin/{target}..HEAD` |
| `files_changed` | From `git diff --shortstat` |
| `additions` | From `git diff --shortstat` |
| `deletions` | From `git diff --shortstat` |
| `delta_loc` | `additions - deletions` |
| `primary_type` | First word of `first_commit` (default: feat) |

### 1.3 Detect Corporate Format

Check if `first_commit` matches corporate pattern:

```
Pattern: ^[a-z]+\|[A-Z]+-[0-9]+\|[0-9]{8}\|.+$
Example: feat|TRV-350|20251023|add user authentication
```

**Valid types:** feat, fix, refactor, chore, docs, test, security

If match:
- `is_corporate = true`
- Parse: `corp_type`, `corp_task_id`, `corp_date`, `corp_description`

### 1.4 Display Context

```
📊 PR Context
   From: {current_branch} → To: {target_branch}
   Commits: {commit_count}
   ΔLOC: +{additions} -{deletions} (Δ{delta_loc})
   Type: {primary_type}
   {If is_corporate: "Format: Corporate ({corp_task_id})"}

Commits:
{commit_list}
```

---

## Phase 2: Quality Gate

### 2.1 Dispatch Code Reviewer

Use Task tool with `ai-framework:code-reviewer` subagent.

**Prompt (fill placeholders):**

```
You are reviewing code changes for production readiness.

## What Was Implemented
{commit_count} commits for PR to {target_branch}: {first_commit}

## Requirements/Plan
Pre-PR quality gate validation before merge to {target_branch}.

## Git Range to Review
**Base:** origin/{target_branch}
**Head:** HEAD

Review the diff:
git diff origin/{target_branch}..HEAD

## Output Format
Provide: Strengths, Issues (Critical/Important/Minor with file:line), Assessment (Ready to merge: Yes/No/With fixes).
```

**Store output as:**
- `cr_strengths`, `cr_issues`, `cr_assessment`
- `cr_has_critical`, `cr_has_important` (booleans)

### 2.2 Auto-Detect Observations

Run checks on `origin/{target_branch}..HEAD`:

| Check | Condition | Status |
|-------|-----------|--------|
| Tests | src files changed without test files | ⚠️ if true |
| Secrets | Diff contains API_KEY, SECRET, TOKEN, PASSWORD, sk-, ghp_ | 🔴 if found |
| API | Files in api/, routes/, endpoints/ | ⚠️ if any |
| Breaking | BREAKING in commit messages | ⚠️ if found |
| Complexity | S≤80, M≤250, L≤600, XL>600 | ⚠️ if over budget |

### 2.3 Consolidate Findings

Build structure (see `examples/success-with-findings.md` for concrete example):

```
findings = {
  code_review: { assessment, critical_count, important_count, minor_count, strengths, issues },
  observations: { tests, secrets, api, breaking, complexity },
  summary: { has_blockers, attention_count, ok_count }
}
```

`has_blockers` = `cr_has_critical` OR `secrets.status == 🔴`

### 2.4 Present Findings

Show table with all observations and code review summary. Include top 3 issues if any exist.

### 2.5 User Decision

Use AskUserQuestion:

```
Question: "Quality gate complete. How to proceed?"
Header: "PR Decision"
Options:
  - label: "Create PR"
    description: "Push branch and create PR with current findings documented"
  - label: "Auto fix"
    description: "Subagent fixes Critical+Important issues, then re-review"
  - label: "Cancel"
    description: "Exit. Fix manually and re-run /git-pullrequest {target_branch}"
```

- **"Create PR"** → Phase 3
- **"Cancel"** → Exit with actionable summary (see `examples/manual-cancellation.md`)
- **"Auto fix"** → Phase 2b

---

## Phase 2b: Auto Fix

Only if user chose "Auto fix". See `examples/auto-fix-loop.md` for complete flow.

### 2b.1 Prepare Fix List

Extract Critical and Important issues from `findings.code_review.issues`:

```
fix_list = [{ severity, file, line, problem, suggestion }, ...]
```

### 2b.2 Dispatch Fix Subagent

Use Task tool with `general-purpose` subagent:

```
Fix the following pre-PR review issues:

## Issues to Fix (in order)

{For each in fix_list:}
### [{severity}] {file}:{line}
- Problem: {problem}
- Suggestion: {suggestion}

## Instructions

1. Read each file to understand full context before fixing
2. Verify suggestion is technically correct for this codebase
3. Fix one issue at a time, verify each fix works
4. Run tests if available
5. Push back on any suggestion that would break functionality (report why)

## After Fixing

Commit all fixes together:
git add -A && git commit -m "fix: address pre-PR review findings"

## Report Back

- Files modified
- Fixes applied (with brief description)
- Any pushbacks (with technical reasoning)
- Test results (if ran)
```

### 2b.3 Return to Quality Gate

After fix completes:
1. Return to Phase 2.1 (re-dispatch code-reviewer)
2. Re-run Phase 2.2 (observations)
3. Present new findings (Phase 2.4)
4. User decides again (Phase 2.5)

User always controls loop exit.

---

## Phase 3: Create PR

### 3.1 Corporate Title Decision

**If `is_corporate = true`:**

Use AskUserQuestion:

```
Question: "Corporate format detected. PR title?"
Header: "PR Title"
Options:
  - label: "Use first commit"
    description: "{first_commit}"
  - label: "Custom title"
    description: "Enter title following format: type|TASK-ID|YYYYMMDD|description"
```

- **"Use first commit"** → `pr_title = first_commit`
- **"Custom title"** → Prompt for custom title, validate format

**If `is_corporate = false`:**
- `pr_title = first_commit`

### 3.2 Push Branch

1. If on protected branch (main/master/develop/staging/production):
   - Create temp branch: `pr/{slug}-{timestamp}`
   - Checkout and push with `--set-upstream`
2. Else:
   - Push current branch (set upstream if needed)

### 3.3 Generate PR Body

Create temp file with this structure:

```markdown
## Summary

{primary_type} changes affecting **{files_changed}** files (Δ{delta_loc} LOC).
{If is_corporate: "**Task:** {corp_task_id}"}

## Changes ({commit_count} commits)

{commit_list}

## Pre-PR Quality Gate

### Code Review: {cr_assessment}

**Strengths:**
{cr_strengths as bullet list}

{If cr_issues exist:}
**Issues Addressed:**
{List issues that were fixed or acknowledged}

### Observations

| Check | Status |
|-------|--------|
| Tests | {status} |
| Secrets | {status} |
| API Changes | {status} |
| Breaking Changes | {status} |
| Complexity | {status} ({size}: Δ{delta_loc}) |

## Test Plan

{Based on primary_type:}
- feat: [ ] New functionality tested, [ ] Tests added, [ ] Docs updated
- fix: [ ] Bug reproduced, [ ] Regression test added, [ ] Verified in staging
- refactor: [ ] Existing tests pass, [ ] Functionality unchanged
- default: [ ] Changes verified, [ ] Build successful
```

### 3.4 Create PR

```bash
gh pr create --title "$pr_title" --body-file "$temp_body_file" --base "$target_branch" --head "$pr_branch"
```

### 3.5 Report Success

```
✅ PR Created

URL: {pr_url}
Branch: {pr_branch} → {target_branch}
Commits: {commit_count}
{If is_corporate: "Task: {corp_task_id}"}
Quality Gate: {attention_count} addressed, {ok_count} OK
```

---

## Error Handling

| Scenario | Response |
|----------|----------|
| No target branch | `❌ Usage: /git-pullrequest main` |
| Target not found | `❌ origin/{target} not found. Run: git fetch origin` |
| No commits | `❌ No commits between {current} and {target}` |
| Invalid corporate format | `❌ Invalid format. Use: type\|TASK-ID\|YYYYMMDD\|desc` |
| Push fails | Show error + manual command |
| gh CLI missing | `❌ gh CLI required. Install: https://cli.github.com` |
| PR create fails | Show error + `gh pr create` command |

---

## Key Principles

1. **Human decides**: Never auto-proceed past quality gate
2. **Loop with exit**: Auto fix always returns to user decision
3. **Corporate support**: Detect and validate corporate commit format
4. **Consistent output**: PR body structure is deterministic
