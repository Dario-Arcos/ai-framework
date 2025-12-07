---
name: git-pullrequest
description: Use when creating a PR - validates changes, dispatches code-reviewer + security-reviewer agents in parallel, generates contextual observations, presents consolidated findings, and creates PR with quality documentation. Supports corporate commit format (type|TASK-ID|YYYYMMDD|desc). Human authorizes every decision point.
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

1. Validate target branch format: `^[a-zA-Z0-9/_-]+$` (alphanumeric, `/`, `-`, `_`)
2. Reject branches starting with `--` (security - prevents git flag injection)
3. Verify remote exists: `git remote get-url origin` (error if no remote configured)
4. Run `git fetch origin --quiet`
5. Verify `origin/{target_branch}` exists: `git rev-parse --verify origin/{target_branch}`
6. Count commits: `git rev-list --count origin/{target_branch}..HEAD`
7. Error if no commits (0 count)

### 1.2 Extract Metadata

Store in working memory:

| Variable | Command |
|----------|---------|
| `current_branch` | `git branch --show-current` |
| `commit_count` | `git rev-list --count origin/{target_branch}..HEAD` |
| `first_commit` | `git log --reverse --pretty=format:'%s' origin/{target_branch}..HEAD \| head -1` |
| `commit_list` | `git log --pretty=format:'- %h %s' origin/{target_branch}..HEAD` |
| `files_changed` | From `git diff --shortstat origin/{target_branch}..HEAD` |
| `additions` | From `git diff --shortstat origin/{target_branch}..HEAD` |
| `deletions` | From `git diff --shortstat origin/{target_branch}..HEAD` |
| `delta_loc` | `additions - deletions` (used for complexity check) |
| `primary_type` | First word of `first_commit` before `(` or `:` (default: feat) |

### 1.3 Detect Corporate Format

Check if `first_commit` matches corporate pattern:

```
Pattern (regex): ^[a-z]+\|[A-Z]+-[0-9]+\|[0-9]{8}\|.+$
Bash check: echo "$first_commit" | grep -Eq '^[a-z]+\|[A-Z]+-[0-9]+\|[0-9]{8}\|.+$'
Example: feat|TRV-350|20251023|add user authentication
```

**Valid types:** feat, fix, refactor, chore, docs, test, style, perf, ci, build, security

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

Dispatch `ai-framework:code-reviewer` agent with these parameters (matches template at `requesting-code-review/code-reviewer.md`):

- DESCRIPTION: `{commit_count} commits for PR to {target_branch}: {first_commit}`
- PLAN_REFERENCE: `Pre-PR quality gate validation before merge to {target_branch}`
- BASE_SHA: `origin/{target_branch}`
- HEAD_SHA: `HEAD`

**Review B: Security Analysis**

Dispatch `ai-framework:security-reviewer` agent. The agent automatically:
1. Runs `git diff --merge-base origin/HEAD` to get changes
2. Analyzes against `origin/{target_branch}` (pass as context if needed)
3. Returns findings in markdown format with severity levels

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
| Tests | Files in `src/` or `lib/` changed AND no files in `test/`, `tests/`, `__tests__/`, or `*.test.*`, `*.spec.*` added | ⚠️ if true |
| API | Any files modified in `api/`, `routes/`, `endpoints/`, or files matching `**/api/**` | ⚠️ if any |
| Breaking | Commit messages contain "BREAKING CHANGE" or "BREAKING:" | ⚠️ if found |
| Complexity | Based on `delta_loc`: S (≤80), M (≤250), L (≤600), XL (>600) | ⚠️ if XL |

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
    description: "Fix Critical+Important (code) and High+Medium (security) issues, then re-review. Minor issues not auto-fixed."
  - label: "Cancel"
    description: "Exit. Fix manually and re-run /git-pullrequest {target_branch}"
```

- **"Create PR"** → Phase 3
- **"Cancel"** → Exit with actionable summary (see `examples/manual-cancellation.md`)
- **"Auto fix"** → Phase 2b

---

## Phase 2b: Auto Fix (Verified)

Only if user chose "Auto fix". See `examples/auto-fix-loop.md` for complete flow.

**Why verification matters:** Subagents can generate false positives, suggest fixes that break functionality, or miss codebase context. The `receiving-code-review` skill acts as a **second line of defense** to filter issues before implementing.

### 2b.1 Prepare Fix List

Extract issues from BOTH reviews:

```
fix_list = []

# Code review: Critical + Important (NOT Minor)
for issue in cr_issues.critical:
  fix_list.append({
    severity: "Critical",
    source: "Code Review",
    file: issue.file,
    line: issue.line,
    problem: issue.what,
    suggestion: issue.fix
  })
for issue in cr_issues.important:
  fix_list.append({ severity: "Important", source: "Code Review", ...issue })

# Security review: High + Medium
for issue in sr_issues.high:
  fix_list.append({ severity: "High (Security)", source: "Security Review", ...issue })
for issue in sr_issues.medium:
  fix_list.append({ severity: "Medium (Security)", source: "Security Review", ...issue })
```

### 2b.2 Verify and Apply Fixes (Using receiving-code-review)

**Invoke the `receiving-code-review` skill** with the fix_list as feedback to process.

The skill enforces verification for EACH issue:

1. **READ** - Read the file to understand context around the issue
2. **UNDERSTAND** - Restate the problem in own words
3. **VERIFY** - Check: Is this issue REAL in this codebase?
4. **EVALUATE** - Check: Is the suggested fix technically correct?
5. **DECIDE**:
   - ✅ **Valid** → Implement the fix
   - ⚠️ **False positive** → Skip with justification
   - ❌ **Fix breaks something** → Pushback, document why
6. **TEST** - Run related tests after each fix

**Example invocation:**
```
Skill: receiving-code-review

Feedback to process (from code-reviewer + security-reviewer):
1. [Critical] src/payments/validator.ts:23 - SQL injection via string concatenation
   Suggestion: Use parameterized query with prepared statement
2. [High (Security)] config.js:17 - Hardcoded API_KEY exposed
   Suggestion: Move to environment variable
3. [Important] src/payments/validator.ts:45 - Card number logged in plaintext
   Suggestion: Mask card number, show only last 4 digits
4. [Medium (Security)] src/auth/session.ts:89 - Potential session fixation
   Suggestion: Regenerate session ID after authentication
```

**Example verification output:**
```
Processing 4 issues with verification...

1/4 [Critical] SQL injection - src/payments/validator.ts:23
    READ: Line 23 shows `query = "SELECT * FROM cards WHERE id=" + cardId`
    VERIFY: ✅ Confirmed - string concatenation with user input
    EVALUATE: ✅ Parameterized query is correct fix
    → Implementing fix
    TEST: ✅ All 12 tests passing
    → ✅ Fixed

2/4 [High (Security)] Hardcoded API_KEY - config.js:17
    READ: Line 17 shows `API_KEY = "sk_live_abc123..."`
    VERIFY: ✅ Confirmed - production key in source
    EVALUATE: ✅ Environment variable is correct approach
    → Implementing fix
    → ✅ Fixed

3/4 [Important] Card number logging - src/payments/validator.ts:45
    READ: Line 45 shows `console.log("Processing card: " + cardNumber)`
    VERIFY: ✅ Confirmed - full card number in logs
    EVALUATE: ✅ Masking is correct approach
    → Implementing fix
    → ✅ Fixed

4/4 [Medium (Security)] Session fixation - src/auth/session.ts:89
    READ: Lines 85-95 show session handling logic
    VERIFY: ⚠️ Session IS regenerated in authenticateUser() (line 92)
    EVALUATE: This is a FALSE POSITIVE - session already regenerated
    → ⚠️ Skipped: False positive - session regeneration exists at line 92
```

### 2b.3 Commit Verified Fixes

After verification and implementation:

```bash
git add -A && git commit -m "fix: address verified pre-PR review findings

Applied (verified):
- [Critical] SQL injection in validator.ts:23 - parameterized query
- [High] Hardcoded API key in config.js:17 - moved to env var
- [Important] Card number logging in validator.ts:45 - masked output

Skipped (false positive):
- [Medium] Session fixation - already handled at auth/session.ts:92"
```

### 2b.4 Return to Quality Gate

After fix completes:
1. Return to Phase 2.1 (re-dispatch BOTH code-reviewer AND security-reviewer in parallel)
2. Re-run Phase 2.2 (observations)
3. Consolidate findings (Phase 2.3)
4. Present new findings (Phase 2.4)
5. User decides again (Phase 2.5)

**Loop exit strategy:**
- **Natural termination**: Both reviews return clean (0 Critical/Important/High/Medium issues) → user selects "Create PR"
- **User control**: User can select "Cancel" at any decision point to exit
- **Expected iterations**: 1-2 (verification catches false positives early)
- **If >2 iterations**: Indicates fixes introducing new issues - user should investigate

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

# Protected branches: exact matches OR prefixes (e.g., release/*, hotfix/*)
protected_exact="^(main|master|develop|development|staging|stage|production|prod|qa|uat)$"
protected_prefix="^(release|releases|hotfix)/"
```

**If on protected branch:**

```bash
if echo "$current_branch" | grep -Eq "$protected_exact" || echo "$current_branch" | grep -Eq "$protected_prefix"; then
  # NEVER push to protected - create temp branch
  timestamp=$(date +%Y%m%d%H%M%S)

  # Generate slug from first_commit, with robust fallback
  slug=$(echo "$first_commit" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//' | cut -c1-30)
  slug="${slug:-pr-changes}"  # Fallback if empty or only special chars

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

{Generate checklist based on primary_type - always unchecked for reviewer to complete:}

**For feat:**
- [ ] New functionality tested
- [ ] Tests added
- [ ] Docs updated

**For fix:**
- [ ] Bug reproduced before fix
- [ ] Regression test added
- [ ] Verified in staging

**For refactor:**
- [ ] Existing tests pass
- [ ] Functionality unchanged

**For other types (docs, chore, etc.):**
- [ ] Changes verified
- [ ] Build successful
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
| No remote configured | `❌ No remote 'origin' configured. Run: git remote add origin <url>` |
| Target not found | `❌ origin/{target} not found. Run: git fetch origin` |
| No commits | `❌ No commits between {current} and {target}` |
| Invalid branch format | `❌ Invalid branch name. Use alphanumeric, /, -, _ only` |
| Invalid corporate format | `❌ Invalid format. Use: type\|TASK-ID\|YYYYMMDD\|desc` |
| Push fails | Show error + manual command |
| gh CLI missing | `❌ gh CLI required. Install: https://cli.github.com` |
| PR create fails | Show error + `gh pr create` command |

---

## Key Principles

1. **Human decides**: Never auto-proceed past quality gate
2. **Three-layer validation**: Code review + Security review + Observations (parallel execution)
3. **Verified fixes**: Auto-fix uses `receiving-code-review` to filter false positives before implementing
4. **Loop with exit**: Auto fix returns to user decision, exits naturally when reviews clean
5. **Corporate support**: Detect and validate corporate commit format
6. **Protected branches**: Never push directly to main/master/develop - auto-creates temp branch

## The Virtuous Cycle

```
Detection (code-reviewer + security-reviewer)
         │
         ▼
   fix_list (may contain false positives)
         │
         ▼
Verification (receiving-code-review filters each issue)
         │
         ├── Valid → Implement
         ├── False positive → Skip with justification
         └── Breaks something → Pushback
         │
         ▼
Re-validation (both reviewers again)
         │
         ▼
Clean? → Create PR : Loop
```

This ensures **multiple perspectives** validate every change before merge.
