---
name: worktree-create
description: Creates worktree with consistent branch in sibling directory
---

# Worktree Create

Creates worktree from specified parent branch with consistent naming.

## Usage

```bash
/worktree-create <objetivo-descripción> <parent-branch>
```

## Examples

```bash
/worktree-create implementar autenticacion OAuth main        # → worktree-implementar-autenticacion-oauth
/worktree-create fix bug critico en pagos develop            # → worktree-fix-bug-critico-en-pagos
```

## Execution

### 1. Argument validation

- Split `$ARGUMENTS`: last element = `parent_branch`, rest = `objetivo_descripcion`
- Both required, terminate with usage error if missing

### 2. Working directory validation

- `git status --porcelain` — if output exists: error, terminate

### 3. Parent branch validation

- `git show-ref --verify --quiet refs/heads/$parent_branch`
- If fails: show available branches, terminate

### 4. Generate consistent names

```bash
echo "$objetivo_descripcion" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g; s/--*/-/g; s/^-//; s/-$//'
```

- `worktree_name` = `worktree-$objetivo_slug`
- `branch_name` = `worktree_name`
- `worktree_path` = `../$worktree_name`

### 5. Check for collisions

- Directory: `[ -d "$worktree_path" ]`
- Branch: `git show-ref --verify --quiet refs/heads/$branch_name`
- If either exists: error, terminate

### 6. Prepare parent branch

```bash
git checkout "$parent_branch"
git pull origin "$parent_branch" --ff-only
```

### 7. Create worktree

```bash
git worktree add "$worktree_path" -b "$branch_name"
```

### 8. Open IDE (Optional)

- Detect: `which code` or `which cursor`
- Execute: `(cd "$worktree_path" && [IDE] . --new-window) &`

### 9. Logging and result

Log to `.claude/logs/YYYY-MM-DD/worktree_operations.jsonl`:
```bash
{"timestamp":"...","operation":"worktree_create","objetivo_descripcion":"...","parent_branch":"...","worktree_path":"...","branch_name":"..."}
```

```
✅ Worktree creado y listo para usar:
- Directorio: $worktree_path
- Rama: $branch_name (local, desde $parent_branch)
- IDE abierto automáticamente en nueva ventana
```

**IMPORTANTE**: No solicitar confirmación. Ejecutar secuencialmente. Si falla paso crítico, detener con error claro.
