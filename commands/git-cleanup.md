---
name: git-cleanup
allowed-tools: Bash(git *), Bash(echo *)
description: Cleanup workflow after PR merge - delete feature branch and sync with base
---

# Post-Merge Cleanup

Automates the common workflow after merging a PR: delete feature branch and sync with base branch.

## Usage

```bash
/cleanup           # Auto-detect base branch (main/master/develop)
/cleanup main      # Specify base branch explicitly
/cleanup develop   # Cleanup and sync with develop
```

## Examples

```bash
/cleanup          # Returns to main, deletes current feature branch, pulls latest
/cleanup develop  # Returns to develop, deletes current feature branch, pulls latest
```

## Execution

### 1. Validate Current State

**Get current branch:**

- Execute: `current_branch=\`git branch --show-current\``
- Store current branch name for cleanup

**Detect protected branches:**

- Protected patterns: `^(main|master|develop|dev|staging|production|prod|qa|release/.+|hotfix/.+)$`
- Check: `echo "$current_branch" | grep -Eq "<pattern>"`
- If current branch is protected:
  - Show error: "❌ Ya estás en rama base ($current_branch). No hay nada que limpiar."
  - Terminate execution
- If not protected, continue with cleanup

### 2. Determine Target Base Branch

**If argument provided:**

- Use `$ARGUMENTS` as target base branch
- Validate format: `echo "$target_base" | grep -Eq '^[a-zA-Z0-9/_-]+$'`
- If invalid, show error and terminate

**If no argument (auto-detect):**

- Execute: `git fetch origin` to refresh remote refs
- Try detection in order:
  1. `git branch -r | grep -q "origin/main" && echo "main"`
  2. `git branch -r | grep -q "origin/master" && echo "master"`
  3. `git branch -r | grep -q "origin/develop" && echo "develop"`
- Use first match as target base
- If none found, show error: "❌ No se pudo detectar rama base (main/master/develop)" and terminate

**Validate target exists:**

- Execute: `git branch -r | grep -q "origin/$target_base"`
- If not exists, show error: "❌ Rama $target_base no existe en origin" and terminate

### 3. Switch to Base Branch

**Show operation:**

- Display: "🔄 Limpiando workspace: $current_branch → $target_base"

**Checkout base:**

- Execute: `git checkout $target_base`
- Verify success (exit code 0)
- If fails, show error: "❌ Error al cambiar a $target_base" and terminate
- If success, show: "✓ Cambiado a $target_base"

### 4. Delete Feature Branch

**Delete local branch:**

- Execute: `git branch -D "$current_branch"`
- Use `-D` (force) because user explicitly requested cleanup
- Capture output to verify deletion
- Show: "✓ Rama local eliminada: $current_branch"

**Handle errors:**

- If branch doesn't exist (already deleted): silent success
- If deletion fails: show warning but continue (non-critical)

### 5. Sync with Remote

**Pull latest changes:**

- Execute: `git pull origin $target_base --ff-only`
- Use `--ff-only` to prevent accidental merges
- If fails (diverged), show:
  - "⚠️ La rama local ha divergido de origin/$target_base"
  - "Ejecuta manualmente: git pull origin $target_base --rebase"
  - Terminate with warning
- If success, capture number of commits pulled
- Show: "✓ Sincronizado con origin/$target_base (+N commits)"

### 6. Final Status

**Show summary:**

```
✅ Cleanup completado

Operaciones:
- Rama actual: $target_base
- Rama eliminada: $current_branch
- Commits sincronizados: +N
- Working tree: clean
```

**Verify clean state:**

- Execute: `git status --short`
- If empty: show "Working tree clean"
- If changes: show warning about uncommitted changes

## Error Handling

- **Not a git repository**: Show error and terminate
- **Already on base branch**: Inform user, no cleanup needed
- **Base branch not found**: Clear error message with available branches
- **Checkout fails**: Show git error and stop (don't delete branch)
- **Pull fails (diverged)**: Show rebase instructions, don't force

## Important Notes

- Uses `-D` (force delete) for local branch since user explicitly requested cleanup
- Uses `--ff-only` for pull to prevent accidental merges
- Remote branches are automatically deleted by GitHub when PR is merged
- Never deletes protected branches (main, master, develop, etc.)
- Validates all operations before executing
- Provides clear feedback for each step
