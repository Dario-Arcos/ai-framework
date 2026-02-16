---
name: branch-cleanup
description: Use when cleaning up a branch after PR merge.
---

# Post-Merge Cleanup

Automates the common workflow after merging a PR: delete feature branch and sync with base branch.

## Usage

```bash
/branch-cleanup           # Auto-detect base branch (main/master/develop)
/branch-cleanup main      # Specify base branch explicitly
```

## Execution

### 1. Validate Current State

- Get current branch: `git branch --show-current`
- Check protected: `^(main|master|develop|dev|staging|production|prod|qa|release/.+|hotfix/.+)$`
- If protected: "❌ Ya estás en rama base ($current_branch). No hay nada que limpiar." → terminate

### 2. Determine Target Base Branch

**If argument provided**: Use `$ARGUMENTS`, validate format `^[a-zA-Z0-9/_-]+$`

**If no argument (auto-detect)**:
1. `git fetch origin`
2. Try: `origin/main` → `origin/master` → `origin/develop`
3. First match = target

Validate target exists: `git branch -r | grep -q "origin/$target_base"`

### 3. Switch to Base Branch

- `git checkout $target_base`
- Verify success

### 4. Delete Feature Branch

- `git branch -D "$current_branch"` (force, user explicitly requested cleanup)
- If already deleted: silent success

### 5. Sync with Remote

- `git pull origin $target_base --ff-only`
- If diverged: show rebase instructions, don't force

### 6. Final Status

```
✅ Cleanup completado

Operaciones:
- Rama actual: $target_base
- Rama eliminada: $current_branch
- Commits sincronizados: +N
- Working tree: clean
```

Verify: `git status --short`

## Notes

- Uses `-D` for local branch (user explicitly requested cleanup)
- Uses `--ff-only` to prevent accidental merges
- Remote branches auto-deleted by GitHub on PR merge
- Never deletes protected branches
