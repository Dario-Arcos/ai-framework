---
allowed-tools: Bash(git *), Bash(gh *), Task
description: Crea PR con pre-review dual (code quality + security)
---

# Pull Request

Workflow automatizado para crear PR con validación de calidad y seguridad.

**Input**: `$ARGUMENTS` = target branch (ej: "main")

## Paso 1: Validación Inicial

Ejecutar en bash (usa `bash <<'SCRIPT'...SCRIPT` para compatibilidad zsh):

1. Parsear `target_branch` desde `$ARGUMENTS`
2. Validar formato: `^[a-zA-Z0-9/_-]+$` (rechazar si empieza con `--`)
3. `git fetch origin`
4. Verificar branch objetivo existe: `git branch -r | grep "origin/$target_branch"`
5. Contar commits: `git rev-list --count "origin/$target_branch..HEAD" --`
6. Guardar estado en git config:
   ```bash
   git config --local pr.temp.target-branch "$target_branch"
   git config --local pr.temp.current-branch "$(git branch --show-current)"
   git config --local pr.temp.commit-count "$commit_count"
   ```

**Bloqueadores**:

- Sin argumentos → error
- Branch objetivo no existe → error
- Cero commits → error

## Paso 2: Análisis de Commits

Ejecutar en bash para extraer metadata:

1. **Logs**: `git log --pretty=format:'- %s' "origin/$target_branch..HEAD" --`
2. **Estadísticas**: `git diff --shortstat "origin/$target_branch..HEAD" --`
3. **Tipo primario**: Parsear commits, contar frecuencia de `feat|fix|docs|refactor`, usar el más común
4. **Scope**: Extraer `(scope)` de commits con `grep -oE '\([a-z-]+\)'`
5. **Breaking changes**: `git log --pretty=format:'%B' | grep -iE 'BREAKING'`

Guardar en git config: `primary_type`, `scope`, `files_changed`, `additions`, `deletions`

## Paso 3: Reviews en Paralelo (BLOQUEANTE)

Ejecutar Task tool en **paralelo**:

### Review 1: Code Quality

```
Prompt: "Review changes in current branch vs origin/$target_branch.
Return '✅ NO_ISSUES' if clean, otherwise list issues:
## Critical
- issue
## Warnings
- warning"

Agent: code-quality-reviewer
```

### Review 2: Security

```
Prompt: "Security review of changes in current branch vs origin/$target_branch.
Return '✅ SECURE' if no issues, otherwise list findings with Severity (HIGH/MEDIUM/LOW) and Confidence (0.0-1.0)."

Agent: security-reviewer
```

### Evaluación de Resultados

Ejecutar en bash:

```bash
has_security_critical=false
if echo "$security_review_result" | grep -Eq 'Severity.*:.*HIGH'; then
  if echo "$security_review_result" | grep -Eq 'Confidence.*:.*(0\.[89]|1\.0)'; then
    has_security_critical=true
  fi
fi

if [ "$has_security_critical" = "true" ]; then
  echo "❌ PR BLOQUEADO: Vulnerabilidades HIGH con confidence ≥0.8"
  git config --local --unset-all pr.temp
  exit 1
fi
```

**Si hay quality issues pero no security critical**: Preguntar al usuario si continuar (y/n/d)

## Paso 4: Push Branch

Ejecutar en bash:

1. Si current branch es protegida (main|master|develop|staging|production):
   - Crear feature branch temporal: `{scope}-{timestamp}`
   - `git checkout -b "$new_branch"`
   - `git push origin "$new_branch" --set-upstream`
2. Sino:
   - `git push origin "$current_branch"` (agregar `--set-upstream` si no tiene remote)

Guardar `branch_name` en git config

## Paso 5: Crear PR con gh CLI

Ejecutar en bash:

1. Obtener metadata de git config
2. Generar título:
   - Si primer commit ya tiene formato convencional → usar tal cual
   - Sino → `$primary_type: $first_commit_subject`
3. Generar body en archivo temporal:

   ```markdown
   ## Summary

   Changes based on **$primary_type** commits affecting **$files_changed** files.

   ## Changes Made ($commit_count commits)

   $git_log

   ## Files & Impact

   - **Files modified**: $files_changed
   - **Lines**: +$additions -$deletions

   ## Test Plan

   - [ ] {test_items_según_primary_type}

   ## Breaking Changes

   $breaking_content
   ```

4. `gh pr create --title "$title" --body-file "$temp_file" --base "$target_branch"`
5. Extraer URL del output
6. `git config --local --unset-all pr.temp`

**Output**: PR URL

## Test Items por Tipo

- **feat**: "Nueva funcionalidad probada; Tests agregados; Docs actualizada"
- **fix**: "Bug reproducido y verificado; Tests de regresión; Staging verificado"
- **refactor**: "Tests existentes pasan; Funcionalidad equivalente"
- **default**: "Cambios verificados localmente; Build exitoso"

## Seguridad

**Prevención de Command Injection**:

1. Todas las variables git quoted: `"$var"` nunca `$var`
2. Git commands con separator: `git cmd "ref" --`
3. Rechazar branches que empiezan con `--`
4. Sanitizar outputs: `tr -d '\`$'`

## Rollback

En cualquier error:

```bash
git config --local --unset-all pr.temp 2>/dev/null
exit 1
```

Si se creó feature branch temporal y falló push:

```bash
git checkout "$original_branch"
git branch -d "$temp_branch"
```

## Notas de Implementación

- **Bash explícito**: Siempre usar `bash <<'SCRIPT'...SCRIPT` para compatibilidad zsh/bash
- **Atomic commands**: Claude ejecuta cada paso con Bash tool individual
- **No hardcodear lógica**: Instrucciones para Claude, no scripts monolíticos
- **Git config como state**: Usar `pr.temp.*` para pasar estado entre pasos
- **Dual review bloqueante**: Security HIGH ≥0.8 confidence bloquea automáticamente
