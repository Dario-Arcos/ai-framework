---
name: commit
description: Use when creating a git commit.
---

# Smart Git Commit

Intelligently analyze and commit changes with automatic grouping and quality checks.

**Input**: `$ARGUMENTS`

## Workflow

### 1. Parse Arguments and Validate Repository

Parse `$ARGUMENTS` for three components:
- **Commit type prefix** (optional): one of feat, fix, refactor, chore, docs, test, security — typically before a colon
- **Task ID** (optional): alphanumeric project key followed by a number (e.g. TRV-345, PROJ-123)
- **Description**: remaining text

Resolution:
- Type prefix + Task ID found → use explicit type. Set has_explicit_type=true
- Task ID found without type prefix → auto-map type from file categories. Set has_explicit_type=false
- No Task ID → use conventional commit format

Validate: `git rev-parse --git-dir`

### 2. Analyze Changes

```bash
git status --porcelain          # Any changes?
git diff --cached --name-only   # Staged files
git diff --name-only            # Unstaged modified
git ls-files --others --exclude-standard  # Untracked
```

### 3. Handle Staging

- Files already staged → use existing staging
- Nothing staged + changes exist → stage all relevant files by explicit path, **excluding** sensitive files (.env, credentials, secrets, private keys). Prefer `git add <file>...` over `git add -A`

### 4. Classify Files by Category

Classify each staged file by matching against category patterns in [references/commit-formats.md](references/commit-formats.md).

Categories: config, docs, security, test, main

### 5. Determine Strategy and Execute Commits

Apply grouping rules from [references/commit-formats.md](references/commit-formats.md) to decide single vs multiple commits.

For each category (order: security, config, docs, test, main):

- If has_explicit_type=true → use explicit type (overrides category mapping)
- If has_explicit_type=false + Task ID → auto-map category to type
- No Task ID → conventional format: `type(scope): description`

Read [references/commit-formats.md](references/commit-formats.md) for corporate format template and auto-mapping rules.

### 6. Report Results

```bash
git log --oneline -n 3
```

## Important Notes

- No AI signatures or attributions in commits
- No git config modifications
- Stages changes by explicit path when nothing pre-staged, excluding sensitive files
- Fallback to single commit when grouping provides no benefit
