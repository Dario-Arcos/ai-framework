---
name: commit
description: Intelligent git commit with automatic grouping and quality checks
---

# Smart Git Commit

Intelligently analyze and commit changes with automatic grouping and quality checks.

**Input**: `$ARGUMENTS`

## Workflow

### 1. Parse Arguments and Validate Repository

Parse `$ARGUMENTS`:
- **Explicit type with Task ID**: Pattern `^(feat|fix|refactor|chore|docs|test|security):\s*([A-Z]+-[0-9]+)\s+(.+)$`
  - If match: store explicit_type, task_id, description. Set has_explicit_type=true
- **Task ID only**: Pattern `([A-Z]+-[0-9]+)`
  - If match: auto-map type from file categories. Set has_explicit_type=false
- **No Task ID**: Use conventional commit format

Validate: `git rev-parse --git-dir`

### 2. Analyze Changes

```bash
git status --porcelain          # Any changes?
git diff --cached --name-only   # Staged files
git diff --name-only            # Unstaged modified
git ls-files --others --exclude-standard  # Untracked
```

### 3. Handle Staging

- Nothing staged + changes exist → `git add -A`
- Files already staged → use existing

### 4. Classify Files by Category

Classify each staged file using natural language processing.
Read [references/commit-formats.md](references/commit-formats.md) for classification rules and format templates.

Categories: config, docs, security, test, main

### 5. Determine Strategy (Single vs Multiple)

- **Multiple commits**: 2+ categories with 2+ files each, OR any security files
- **Single commit**: one significant category or limited changes

### 6. Execute Commits

For each category (order: security, config, docs, test, main):

- If has_explicit_type=true → use explicit type (overrides category mapping)
- If has_explicit_type=false + Task ID → auto-map category to type
- No Task ID → conventional format: `type(scope): description`

Read [references/commit-formats.md](references/commit-formats.md) for corporate format template and auto-mapping rules.

### 7. Report Results

```bash
git log --oneline -n 3
```

## Important Notes

- No AI signatures or attributions in commits
- No git config modifications
- Stages ALL changes when nothing pre-staged (modified, new, deleted)
- Fallback to single commit when grouping provides no benefit
