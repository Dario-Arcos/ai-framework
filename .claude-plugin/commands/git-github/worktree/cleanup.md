---
allowed-tools: Bash(git *), Bash(test *), Bash(mkdir *), Bash(date *), Bash(whoami), Bash([[ ]]), Bash(realpath *), Bash(stat *)
description: Safe removal of specific worktrees with ownership validation and discovery mode
---

# Worktree Cleanup

## Output Convention

All "show", "display", "output" instructions = normal Claude text output, NOT bash echo. Use bash tools ONLY for git operations, file system queries, data processing.

## Usage

```bash
/worktree:cleanup                                        # Discovery mode
/worktree:cleanup <worktree1> [worktree2] [worktree3]   # Cleanup mode
```

## Restrictions

- Only removes worktrees/branches created by you
- Never touches protected branches (main, develop, qa, staging, master)
- Requires clean state (no uncommitted changes)

## Execution

### Discovery Mode (no arguments)

Lists available worktrees with suggested commands.

### Cleanup Mode (with arguments)

### 1. Validation and preparation

- Validate each target using single-pass validation
- Create list of valid targets (skip invalid with warnings)
- If no valid targets: show "ℹ️ No hay worktrees válidos para eliminar" and terminate

### 2. Per-target validations

**2a. Format validation:**

- Execute: `echo "$target" | grep -Eq '^[a-zA-Z0-9][a-zA-Z0-9_-]*$' && echo "valid" || echo "invalid"`
- If output is "invalid": skip with "Formato de nombre inválido"

**2b. Protected branch validation:**

- Check: `echo "$target" | grep -qE "^(main|develop|qa|staging|master)$" && echo "protected" || echo "not_protected"`
- If output is "protected": skip with "Rama protegida"

**2c. Current directory validation:**

- Get current directory canonical path: `realpath "$(pwd)" 2>/dev/null`
- Get target worktree path from `git worktree list --porcelain` matching target name
- Get target canonical path: `realpath "$target_path" 2>/dev/null`
- Compare paths: if match, skip with "❌ No puedes eliminar worktree actual"

**2d. Existence validation:**

- Verify exists: `git worktree list --porcelain`
- If doesn't exist: skip with "Worktree no encontrado"

**2e. Ownership validation:**

- Get worktree owner: `stat -f %Su "$path" 2>/dev/null || stat -c %U "$path" 2>/dev/null` (cross-platform)
- Compare with current user: `whoami`
- If not match: skip with "No es tu worktree"

**2f. Clean state validation:**

- Verify: `git status --porcelain` in worktree
- If not clean: skip with problem message

### 3. User confirmation

- Output summary of valid targets (normal text)
- Ask: "¿Confirmas la eliminación? Responde 'ELIMINAR' para proceder:"
- WAIT for user response
- If response != "ELIMINAR": show cancellation and terminate
- If response == "ELIMINAR": proceed to step 4

### 4. Dual atomic cleanup

For each confirmed target:

- Remove worktree: `git worktree remove "$target"`
- Remove local branch: `git branch -D "$branch_name"`

### 5. Logging and final cleanup

- Log operation in JSONL format
- Execute: `git remote prune origin`
- Show results report

### 6. Update current branch

- Execute: `git pull`
- If fails: warning "⚠️ No se pudo actualizar desde remoto" but continue
- If success: "Updated from remote"

## Discovery Mode Implementation

**Phase 1: Discovery**

- Get current directory: `current_canonical="\`realpath \"\`pwd\`\" 2>/dev/null\`"`
- If fails: error and terminate
- Get current user: `current_user="\`whoami\`"`
- Process worktrees using simplified pipeline:

  ```bash
  git worktree list --porcelain | awk '/^worktree / {print substr($0, 10)}' | while read -r path; do
      # Get canonical path
      canonical=\`realpath "$path" 2>/dev/null\`
      [ -z "$canonical" ] && continue

      # Skip current directory
      [ "$canonical" = "$current_canonical" ] && continue

      # Get owner (cross-platform)
      owner=\`stat -f %Su "$path" 2>/dev/null || stat -c %U "$path" 2>/dev/null\`

      # Only list user's worktrees
      if [ "$owner" = "$current_user" ]; then
          basename "$path"
      fi
  done
  ```

  - For each result: add to numbered list

**Phase 2: User Interaction**

- Output: "🔍 Tus worktrees disponibles para eliminar:"
- Show numbered list: `"   1. $worktree_name"`
- Ask: "Selecciona números separados por espacios (ej: 1 2) o 'todos':"
- WAIT for user response
- Parse input and convert to worktree names
- Continue with cleanup flow

## Logging Format

- Create: `log_dir=".claude/logs/\`date +%Y-%m-%d\`" && mkdir -p "$log_dir"`
- Add to: `"$log_dir/worktree_operations.jsonl"`

```bash
{"timestamp":"`date -Iseconds`","operation":"worktree_cleanup","target":"$target","user":"`whoami`","my_email":"`git config user.email`","worktree_removed":"$worktree_removed","local_removed":"$local_removed","local_only":true,"commit_sha":"`git rev-parse HEAD`"}
```
