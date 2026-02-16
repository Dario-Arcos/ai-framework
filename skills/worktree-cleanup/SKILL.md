---
name: worktree-cleanup
description: Use when removing git worktrees or discovering existing worktrees.
---

# Worktree Cleanup

## Output Convention

All "show", "display", "output" instructions = normal Claude text output, NOT bash echo. Use bash tools ONLY for git operations, file system queries, data processing.

## Usage

```bash
/worktree-cleanup                                        # Discovery mode
/worktree-cleanup <worktree1> [worktree2] [worktree3]   # Cleanup mode
```

## Restrictions

- Only removes worktrees/branches created by you
- Never touches protected branches (main, develop, qa, staging, master)
- Requires clean state (no uncommitted changes)

## Execution

### Discovery Mode (no arguments)

**Phase 1: Discovery**

```bash
current_canonical="`realpath \"`pwd`\" 2>/dev/null`"
current_user="`whoami`"
git worktree list --porcelain | awk '/^worktree / {print substr($0, 10)}' | while read -r path; do
    canonical=`realpath "$path" 2>/dev/null`
    [ -z "$canonical" ] && continue
    [ "$canonical" = "$current_canonical" ] && continue
    owner=`stat -f %Su "$path" 2>/dev/null || stat -c %U "$path" 2>/dev/null`
    if [ "$owner" = "$current_user" ]; then
        basename "$path"
    fi
done
```

**Phase 2: User Interaction**

- Show numbered list of available worktrees
- Ask: "Selecciona números separados por espacios (ej: 1 2) o 'todos':"
- Parse input, convert to worktree names, continue with cleanup flow

### Cleanup Mode (with arguments)

### 1. Validation and preparation

Validate each target, create list of valid targets (skip invalid with warnings).

### 2. Per-target validations

**2a. Format**: `echo "$target" | grep -Eq '^[a-zA-Z0-9][a-zA-Z0-9_-]*$'`
**2b. Protected**: Check against `^(main|develop|qa|staging|master)$`
**2c. Current directory**: Compare canonical paths, can't delete current worktree
**2d. Existence**: Verify in `git worktree list --porcelain`
**2e. Ownership**: `stat -f %Su "$path" 2>/dev/null || stat -c %U "$path" 2>/dev/null` vs `whoami`
**2f. Clean state**: `git status --porcelain` in worktree

### 3. User confirmation

- Show valid targets summary
- Ask: "¿Confirmas la eliminación? Responde 'ELIMINAR' para proceder:"
- If response != "ELIMINAR": cancel

### 4. Dual atomic cleanup

For each confirmed target:
- `git worktree remove "$target"`
- `git branch -D "$branch_name"`

### 5. Logging

Log to `.claude/logs/YYYY-MM-DD/worktree_operations.jsonl`:
```bash
{"timestamp":"...","operation":"worktree_cleanup","target":"$target","user":"...","worktree_removed":"...","local_removed":"..."}
```

Execute: `git remote prune origin`

### 6. Update current branch

- `git pull` (warning if fails, but continue)
