---
allowed-tools: Bash(git *), Bash(test *), Bash(mkdir *), Bash(date *), Bash(whoami), Bash(echo *), Bash(tr *), Bash(sed *)
description: Creates worktree with consistent branch in sibling directory
---

# Worktree Create

Creates worktree from specified parent branch with consistent naming.

## Usage

```bash
/worktree:create "<objetivo-descripción>" <parent-branch>  # Ambos argumentos obligatorios
```

## Examples

```bash
/worktree:create "implementar autenticacion OAuth" main        # → worktree-implementar-autenticacion-oauth
/worktree:create "fix bug critico en pagos" develop            # → worktree-fix-bug-critico-en-pagos
/worktree:create "refactor dashboard usuarios" main            # → worktree-refactor-dashboard-usuarios
/worktree:create "add API endpoints v2" qa                     # → worktree-add-api-endpoints-v2
```

## Execution

When executing this command with `$ARGUMENTS`, follow these steps:

### 1. Argument validation

- Count arguments in `$ARGUMENTS` using array expansion
- Si no hay exactamente 2 argumentos, mostrar error: "❌ Error: Se requieren 2 argumentos. Uso: /worktree:create \"<objetivo>\" <parent-branch>"
- Capture first argument as `objetivo_descripcion` and second as `parent_branch`
- Mostrar: "Creando worktree para: <objetivo_descripcion> desde rama padre: <parent_branch>"

### 2. Working directory validation

- Execute `status_output=\`git status --porcelain\`` to capture pending changes
- If there is output (uncommitted changes):
  - Mostrar error: "❌ Error: Directorio de trabajo no está limpio. Commitea o stash cambios primero"
  - Mostrar contenido: `echo "$status_output"`
  - TERMINATE process completely
- Si no hay cambios, mostrar: "✓ Directorio de trabajo limpio, continuando..."

### 3. Parent branch validation

- Execute `git show-ref --verify --quiet refs/heads/$parent_branch` to verify it exists locally
- If command fails (exit code != 0):
  - Mostrar error: "❌ Error: Branch '$parent_branch' no existe localmente"
  - Mostrar: "Branches disponibles:"
  - Ejecutar `git branch --list`
  - TERMINATE process completely
- Si existe, mostrar: "✓ Rama padre '$parent_branch' verificada"

### 4. Generate consistent names

- Convert `objetivo_descripcion` to valid slug using optimized transformation:
  - Execute `echo "$objetivo_descripcion" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g; s/--*/-/g; s/^-//; s/-$//'`
  - Capture result as `objetivo_slug`
- Build `worktree_name` as: "worktree-$objetivo_slug"
- Build `branch_name` identical to `worktree_name`
- Build `worktree_path` as: "../$worktree_name"
- Mostrar: "Nombres generados desde objetivo: '$objetivo_descripcion' → Directorio: $worktree_path, Rama: $branch_name"

### 5. Check for collisions

- **5a. Directory collision check**: Execute `[ -d "$worktree_path" ]` to verify if directory exists
  - If exists (exit code 0): Mostrar error: "❌ Error: Directory $worktree_path ya existe" and TERMINATE
- **5b. Branch collision check**: Execute `git show-ref --verify --quiet refs/heads/$branch_name` to verify if branch exists
  - If exists (exit code 0): Mostrar error: "❌ Error: Branch $branch_name ya existe" and TERMINATE
- **5c. Confirmation**: Mostrar: "✓ No se detectaron colisiones"

### 6. Prepare parent branch

- Execute `git checkout "$parent_branch"` to switch to parent
- If fails, show error: "❌ Error: No se pudo cambiar a $parent_branch" and terminate
- Execute `git pull origin "$parent_branch"` to update from remote
- If fails, show warning: "⚠️ No se pudo actualizar $parent_branch desde remoto" but continue
- Si exitoso, mostrar: "✓ Rama padre actualizada desde remoto"

### 7. Create worktree

- Execute `git worktree add "$worktree_path" -b "$branch_name"`
- If command fails, show error: "❌ Error: No se pudo crear worktree" and terminate
- Mostrar: "✅ Worktree created: $worktree_path with branch $branch_name"

### 8. Open IDE automatically

- Detect available IDE by executing commands in order:
  - `which code > /dev/null 2>&1` para VS Code
  - `which cursor > /dev/null 2>&1` para Cursor
- If IDE is found, execute `(cd "$worktree_path" && [IDE_COMMAND] . --new-window)` where [IDE_COMMAND] is `code` or `cursor`
- Si IDE se abre exitosamente, mostrar: "✅ IDE abierto en nueva ventana: $worktree_path"
- Si no se encuentra IDE disponible, mostrar: "⚠️ No se encontró IDE compatible. Abre manualmente: [IDE] $worktree_path"
- If fails to open IDE, show warning: "⚠️ No se pudo abrir IDE automáticamente" but continue

### 9. Logging and final result

- **Log operation**: Create logs directory with `log_dir=".claude/logs/\`date +%Y-%m-%d\`" && mkdir -p "$log_dir"`
- If directory creation fails: show warning but continue
- Add JSONL entry to `"$log_dir/worktree_operations.jsonl"` using the template
- Show successful status:

  ```
  ✅ Worktree created successfully:
  - Directory: $worktree_path
  - Branch: $branch_name (local)
  - Rama padre: $parent_branch

  ⚠️  CRÍTICO: IDE abierto automáticamente, pero debes:

  PASO 1 - En la nueva ventana del IDE:
    Abrir Terminal integrado (Cmd+` o View → Terminal)

  PASO 2 - Verificar directorio correcto:
    pwd  # Debe mostrar: $worktree_path

  PASO 3 - Iniciar nueva sesión Claude Code:
    claude /workflow:session-start

  ❌ SI NO HACES ESTO: Claude seguirá trabajando en el directorio
     anterior y NO funcionará correctamente el worktree.

  ✅ SOLO así tendrás sesiones Claude Code paralelas funcionando.
  ```

## 📊 Logging Format Template

Para operación exitosa, agregar línea al archivo JSONL:

### Worktree Creation Log:

```bash
{"timestamp":"`date -Iseconds`","operation":"worktree_create","objetivo_descripcion":"$objetivo_descripcion","parent_branch":"$parent_branch","worktree_path":"$worktree_path","branch_name":"$branch_name","local_only":true,"user":"`whoami`","commit_sha":"`git rev-parse HEAD`"}
```

**IMPORTANTE**:

- No solicitar confirmación al usuario en ningún paso
- Ejecutar todos los pasos secuencialmente
- Si algún paso crítico falla, detener ejecución y mostrar error claro
- Crear directorio de logs antes de escribir
