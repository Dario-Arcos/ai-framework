---
allowed-tools: Bash(git *), Bash(test *), Bash(mkdir *), Bash(date *), Bash(whoami), Bash([[ ]]), Bash(realpath *), Bash(stat *)
description: Safe removal of specific worktrees with ownership validation and discovery mode
---

# Worktree Cleanup

## Output Convention

All "show", "display", "output" instructions = normal Claude text output, NOT bash echo. Use bash tools ONLY for git operations, file system queries, data processing.

## Shell Syntax (macOS/zsh)

**Negation**: `! [[ condition ]]` (outside brackets)
**Command substitution**: Backticks `` `...` ``
**Error suppression**: `2>/dev/null`

```bash
# ❌ WRONG: [[ ! "$var" =~ pattern ]]
# ✅ CORRECT: ! [[ "$var" =~ pattern ]]
```

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

- Execute validation from section 3
- If matches current directory: skip with error

**2d. Existence validation:**

- Verify exists: `git worktree list --porcelain`
- If doesn't exist: skip with "Worktree no encontrado"

**2e. Ownership validation:**

- Verify ownership using section 4 logic
- If not user's: skip with "No es tu worktree"

**2f. Clean state validation:**

- Verify: `git status --porcelain` in worktree
- If not clean: skip with problem message

### 3. Current directory validation (CRITICAL SECURITY)

- Get: `current_dir="\`realpath \"\`pwd\`\" 2>/dev/null\`"`
- If fails: error "❌ Error: No se pudo resolver directorio actual" and terminate
- Get worktree target path:
  ```
  git worktree list --porcelain | awk -v target="$target" '
      /^worktree / {
          path = substr($0, 10)
          split(path, parts, "/")
          dir_name = parts[length(parts)]
          if (dir_name == target) { print path; exit }
      }
  '
  ```
- If target not found: continue (handled by other validation)
- Get: `target_path="\`realpath \"$target_path\" 2>/dev/null\`"`
- If fails: error "❌ Error: No se pudo resolver path del worktree target" and skip
- Execute: `[ "$current_dir" = "$target_path" ] && echo "match" || echo "no_match"`
- If output is "match":
  - Error: "❌ Error: No puedes eliminar el worktree donde estás actualmente"
  - Show current location and solution
  - Skip with warning

### 4. Cross-platform compatibility

Get file owner and compare:

- Execute: `echo "$OSTYPE" | grep -Eq '^darwin' && stat -f %Su "$path" 2>/dev/null || stat -c %U "$path" 2>/dev/null`
- Capture owner in variable
- Execute: `[ "$owner" = "\`whoami\`" ] && echo "match" || echo "no_match"`
- If output is "no_match": skip with "No es tu worktree"

### 5. User confirmation

- Output summary of valid targets (normal text)
- Ask: "¿Confirmas la eliminación? Responde 'ELIMINAR' para proceder:"
- WAIT for user response
- If response != "ELIMINAR": show cancellation and terminate
- If response == "ELIMINAR": proceed to step 6

### 6. Dual atomic cleanup

For each confirmed target:

- Remove worktree: `git worktree remove "$target"`
- Remove local branch: `git branch -D "$branch_name"`

### 7. Logging and final cleanup

- Log operation in JSONL format
- Execute: `git remote prune origin`
- Show results report

### 8. Update current branch

- Execute: `git pull`
- If fails: warning "⚠️ No se pudo actualizar desde remoto" but continue
- If success: "Updated from remote"

## Discovery Mode Implementation

**Phase 1: Discovery**

- Get: `current_canonical="\`realpath \"\`pwd\`\" 2>/dev/null\`"`
- If fails: error and terminate
- Process worktrees:

  ```
  git worktree list --porcelain | awk -v current_canonical="$current_canonical" -v current_user="\`whoami\`" -v ostype="$OSTYPE" '
      /^worktree / {
          path = substr($0, 10)
          cmd = "realpath \"" path "\" 2>/dev/null"
          cmd | getline canonical
          close(cmd)

          if (canonical == current_canonical) next

          if (ostype ~ /^darwin/) {
              stat_cmd = "stat -f %Su \"" path "\" 2>/dev/null"
          } else {
              stat_cmd = "stat -c %U \"" path "\" 2>/dev/null"
          }
          stat_cmd | getline owner
          close(stat_cmd)

          if (owner == current_user) {
              split(path, parts, "/")
              print parts[length(parts)]
          }
      }
  '
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
