---
name: git-pullrequest
description: Use when creating a PR - validates changes, dispatches code-reviewer + security-reviewer subagents in parallel, generates contextual observations, presents consolidated findings, and creates PR with quality documentation. Supports corporate commit format (type|TASK-ID|YYYYMMDD|desc). Human authorizes every decision point.
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

## Review Architecture: Three Complementary Layers

**1. Observations (Phase 2.2)** - Pattern Matching
- **What:** Facts via grep/regex (tests count, BREAKING keyword, API files, complexity)
- **Speed:** Instant
- **Coverage:** Known patterns only
- **Example:** "0 test files added when source changed"

**2. Code Review (Phase 2.1a)** - Logic & Architecture
- **What:** Bugs, architectural issues, missing features, test quality
- **Speed:** 30-60s (parallel with security)
- **Coverage:** Semantic code analysis
- **Example:** "Missing error handling in async function"

**3. Security Review (Phase 2.1b)** - Vulnerabilities
- **What:** SQL injection, hardcoded secrets, XSS, command injection, auth bypass
- **Speed:** 30-60s (parallel with code review)
- **Coverage:** Security-focused patterns + exploitability analysis
- **Example:** "SQL injection via string concatenation"

**Why three layers:** Observations catch obvious patterns fast. Code review catches logic issues. Security review catches vulnerabilities. Complementary, not redundant.

---

## Phase 2: Quality Gate

### 2.1 Dispatch Reviews (Parallel)

**Execute TWO reviews in parallel using single message with 2 Task tool calls:**

**Review A: Code Quality & Architecture**

Use `requesting-code-review` skill OR dispatch `ai-framework:code-reviewer` directly with:

- WHAT_WAS_IMPLEMENTED: `{commit_count} commits for PR to {target_branch}: {first_commit}`
- PLAN_OR_REQUIREMENTS: `Pre-PR quality gate validation before merge to {target_branch}`
- BASE_SHA: `origin/{target_branch}`
- HEAD_SHA: `HEAD`

**Review B: Security Analysis**

Dispatch `ai-framework:security-reviewer` subagent (runs current branch analysis automatically).

**Store outputs:**

Code review:
- `cr_strengths`, `cr_issues`, `cr_assessment`
- `cr_has_critical`, `cr_has_important` (booleans)

Security review:
- `sr_issues` (High/Medium vulnerabilities)
- `sr_has_high`, `sr_has_medium` (booleans)

### 2.2 Auto-Detect Observations

Run checks on `origin/{target_branch}..HEAD`:

| Check | Condition | Status |
|-------|-----------|--------|
| Tests | src files changed without test files | ⚠️ if true |
| API | Files in api/, routes/, endpoints/ | ⚠️ if any |
| Breaking | BREAKING in commit messages | ⚠️ if found |
| Complexity | S≤80, M≤250, L≤600, XL>600 | ⚠️ if over budget |

**Note:** Secrets detection handled by security-reviewer (Phase 2.1b).

### 2.3 Consolidate Findings

Build structure from THREE sources:

```
findings = {
  code_review: {
    assessment: cr_assessment,
    critical_count: len(cr_issues.critical),
    important_count: len(cr_issues.important),
    minor_count: len(cr_issues.minor),
    strengths: cr_strengths,
    issues: cr_issues
  },
  security_review: {
    high_count: len(sr_issues.high),
    medium_count: len(sr_issues.medium),
    issues: sr_issues
  },
  observations: {
    tests: { status, detail },
    api: { status, detail },
    breaking: { status, detail },
    complexity: { status, detail }
  },
  summary: {
    has_blockers: cr_has_critical OR sr_has_high,
    total_issues: cr_critical_count + cr_important_count + cr_minor_count + sr_high_count + sr_medium_count,
    attention_count: count of non-✅ observations
  }
}
```

### 2.4 Present Findings

**Structure:**

```
## Quality Gate Results

### Code Review: {cr_assessment}
{Top 3 code review issues if any}

### Security Review: {sr_high_count} High, {sr_medium_count} Medium
{Top 3 security issues if any}

**Strengths:**
{cr_strengths as bullet list}

### Observations
| Check | Status | Detail |
|-------|--------|--------|
| Tests | {status} | {detail} |
| API Changes | {status} | {detail} |
| Breaking | {status} | {detail} |
| Complexity | {status} | {detail} |

### Summary
{total_issues} issues found, {attention_count} observations need attention
{If has_blockers: "⚠️ Blockers detected - review before proceeding"}
```

### 2.5 User Decision

Use AskUserQuestion:

```
Question: "Quality gate complete. How to proceed?"
Header: "PR Decision"
Options:
  - label: "Create PR"
    description: "Push branch and create PR with current findings documented"
  - label: "Auto fix"
    description: "Subagent fixes Critical+Important+High+Medium security issues, then re-review"
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

Extract issues from BOTH reviews:

```
fix_list = []

# Code review: Critical + Important
for issue in cr_issues.critical:
  fix_list.append({
    severity: "Critical",
    source: "Code Review",  # Traceability: which review found this
    ...issue  # Includes: file, line, problem, suggestion
  })
for issue in cr_issues.important:
  fix_list.append({ severity: "Important", source: "Code Review", ...issue })

# Security review: High + Medium
for issue in sr_issues.high:
  fix_list.append({ severity: "High (Security)", source: "Security Review", ...issue })
for issue in sr_issues.medium:
  fix_list.append({ severity: "Medium (Security)", source: "Security Review", ...issue })
```

### 2b.2 Apply Fixes Using receiving-code-review

Invoke the `receiving-code-review` skill with the consolidated fix_list as feedback.

The skill automatically enforces:
1. READ files to understand context
2. VERIFY suggestions technically correct
3. IMPLEMENT one fix at a time
4. TEST each fix
5. PUSH BACK if suggestion breaks functionality

Example invocation:
```
Skill: receiving-code-review

Feedback to process: {fix_list with 4 issues}
- [Critical] file.js:23 - SQL injection
- [Important] file.js:45 - Missing error handling
- [High (Security)] config.js:17 - Hardcoded API_KEY
...
```

After all fixes, commit:
```bash
git add -A && git commit -m "fix: address pre-PR review findings"
```

### 2b.3 Return to Quality Gate

After fix completes:
1. Return to Phase 2.1 (re-dispatch BOTH code-reviewer AND security-reviewer in parallel)
2. Re-run Phase 2.2 (observations)
3. Consolidate findings (Phase 2.3)
4. Present new findings (Phase 2.4)
5. User decides again (Phase 2.5)

**Loop exit strategy:**
- **Natural termination**: Both reviews return clean (0 Critical/Important/High/Medium issues) → user selects "Create PR"
- **User control**: User can select "Cancel" at any decision point to exit
- **Expected iterations**: 1-2 (comprehensive first review should catch all issues)
- **If >2 iterations**: Indicates incomplete review or fixes introducing new issues - user should investigate

User always controls loop via decision options.

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

**CRITICAL: Check if on protected branch first**

```bash
current_branch=$(git branch --show-current)

# Comprehensive list of protected branches (common in real teams)
protected="^(main|master|develop|development|staging|stage|production|prod|release|releases|qa|uat|hotfix)$"
```

**If on protected branch:**

```bash
if echo "$current_branch" | grep -Eq "$protected"; then
  # NEVER push to protected - create temp branch
  timestamp=$(date +%Y%m%d%H%M%S)
  slug=$(echo "$first_commit" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 ]/-/g' | tr -s '-' | cut -c1-30)
  slug="${slug:-feature}"  # Fallback if empty
  pr_branch="pr/${slug}-${timestamp}"

  echo "⚠️ On protected branch: $current_branch"
  echo "Creating temp branch: $pr_branch"

  git checkout -b "$pr_branch"
  git push origin "$pr_branch" --set-upstream
else
  # Feature branch - push normally
  pr_branch="$current_branch"

  if ! git rev-parse --abbrev-ref "@{upstream}" >/dev/null 2>&1; then
    git push origin "$pr_branch" --set-upstream
  else
    git push origin "$pr_branch"
  fi
fi
```

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

{If cr_issues or sr_issues exist:}
**Issues Addressed:**
{List code review issues that were fixed or acknowledged}
{List security issues that were fixed or acknowledged}

### Security Review: {sr_high_count} High, {sr_medium_count} Medium
{If sr_issues: List resolved/acknowledged security findings}
{Else: "✅ No security vulnerabilities detected"}

### Observations

| Check | Status |
|-------|--------|
| Tests | {status} |
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
2. **Three-layer validation**: Code review + Security review + Observations (parallel execution)
3. **Loop with exit**: Auto fix returns to user decision, exits naturally when reviews clean
4. **Corporate support**: Detect and validate corporate commit format
5. **Skills integration**: Uses requesting-code-review and receiving-code-review for consistency
