---
name: pull-request
description: Use when creating a PR, preparing code for review, or ready to merge feature work into a target branch
---

# Git Pull Request Workflow

Create PRs with integrated quality gate. Human always decides.

**Input:** Target branch from `$ARGUMENTS` (e.g., "main").

If `$ARGUMENTS` is empty, use AskUserQuestion: "¿A qué rama destino quieres dirigir el Pull Request?" with options from `git branch -r | grep -v HEAD | sed 's/origin\///' | head -5`.

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
PR Context
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

### 2.1 Dispatch Reviews (Parallel)

**Execute TWO reviews in parallel using single message with 2 Task tool calls:**

**Review A: Code Quality & Architecture**

Dispatch `ai-framework:code-reviewer` agent with these parameters:

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

Merge code review, security review, and observations into a single findings summary:

- **Code review**: assessment, issue counts by severity (critical/important/minor), strengths, full issues list
- **Security review**: issue counts by severity (high/medium), full issues list
- **Observations**: status and detail for each check (tests, api, breaking, complexity)
- **Summary flags**: `has_blockers` (any critical OR high), `total_issues` (all severities except minor), `attention_count` (non-OK observations)

### 2.4 Present Findings

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
  - label: "Auto fix (all)"
    description: "Fix all reported issues, then re-review"
  - label: "Auto fix (blockers only)"
    description: "Fix Critical+Important (code) and High+Medium (security) only — skip Minor/Low"
  - label: "Cancel"
    description: "Exit. Fix manually and re-run /pull-request {target_branch}"
```

- **"Create PR"** → Phase 3
- **"Cancel"** → Exit with actionable summary (see `examples/manual-cancellation.md`)
- **"Auto fix (all)"** → Phase 2b with `fix_scope = all`
- **"Auto fix (blockers only)"** → Phase 2b with `fix_scope = blockers`

---

## Phase 2b: Auto Fix (Verified)

Only if user chose "Auto fix". See `examples/auto-fix-loop.md` for complete flow.

### 2b.1 Prepare Fix List

Extract issues from BOTH reviews based on `fix_scope`:

| fix_scope | Code Review | Security Review |
|-----------|-------------|-----------------|
| `all` | Critical, Important, Minor | High, Medium |
| `blockers` | Critical, Important | High, Medium |

Each entry: `{severity, source, file, line, problem, suggestion}`.

### 2b.2 Verify and Apply Fixes

For EACH issue in fix_list, execute the verification protocol directly:

1. **READ** — Read the file, observe actual code at the reported location
2. **STUDY** — Restate the problem in own words; identify which scenarios are affected
3. **VERIFY** — Is this issue REAL? Compare reported vs observed behavior — assumed ≠ observed
4. **EVALUATE** — Is the suggested fix correct? Will it break existing scenario satisfaction?
5. **DECIDE**:
   - Valid → Implement the fix
   - False positive → Skip with justification (observed behavior contradicts report)
   - Fix breaks satisfaction → Skip, document why
6. **TEST** — Run related tests, observe output, confirm no scenario regressions

**Document each issue on one line:**
```
N/T [{severity}] {file}:{line} — {problem} → {Fixed|Skipped: reason}
```

**Example:**
```
1/4 [Critical] validator.ts:23 — SQL injection → Fixed: parameterized query
2/4 [High] config.js:17 — Hardcoded API key → Fixed: moved to env var
3/4 [Important] validator.ts:45 — Card logged plaintext → Fixed: masked output
4/4 [Medium] session.ts:89 — Session fixation → Skipped: observed behavior contradicts report (regenerateId() at line 92)
```

### 2b.3 Commit Verified Fixes

Stage only modified files — never `git add -A`:

```bash
git add <specific-files-modified> && git commit -m "fix: address verified pre-PR review findings

Applied (verified):
- [{severity}] {description} in {file} - {fix applied}

Skipped (false positive):
- [{severity}] {description} - {reason}"
```

### 2b.4 Return to Quality Gate

After fix commit:
1. Return to Phase 2.1 (re-dispatch BOTH reviewers in parallel)
2. Re-run Phase 2.2 (observations)
3. Consolidate (2.3), present (2.4), user decides (2.5)

**Loop exit:**
- **Natural**: Both reviews clean (0 Critical/Important/High/Medium) → user selects "Create PR"
- **User control**: "Cancel" at any decision point
- **Expected iterations**: 1-2 (verification catches false positives early)
- **If >2 iterations**: Warn user — fixes may be introducing new issues, suggest manual investigation

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

Read `[references/pr-body-template.md]`, fill all `{variables}` from working memory, write to temp file.

### 3.4 Create PR

```bash
gh pr create --title "$pr_title" --body-file "$temp_body_file" --base "$target_branch" --head "$pr_branch"
```

### 3.5 Report Success

```
PR Created

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
| No target branch | `Usage: /pull-request main` |
| No remote configured | `No remote 'origin' configured. Run: git remote add origin <url>` |
| Target not found | `origin/{target} not found. Run: git fetch origin` |
| No commits | `No commits between {current} and {target}` |
| Invalid branch format | `Invalid branch name. Use alphanumeric, /, -, _ only` |
| Invalid corporate format | `Invalid format. Use: type\|TASK-ID\|YYYYMMDD\|desc` |
| Push fails | Show error + manual command |
| gh CLI missing | `gh CLI required. Install: https://cli.github.com` |
| PR create fails | Show error + `gh pr create` command |

---

## Constraints

- Never auto-proceed past quality gate — human decides at every gate
- Never use `git add -A` — stage specific files only
- Never push to protected branches — auto-create temp branch
- Never skip verification protocol in auto-fix — every issue gets READ→STUDY→VERIFY→EVALUATE→DECIDE→TEST
- If >2 fix iterations: warn user, suggest manual investigation
