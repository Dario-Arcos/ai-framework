---
allowed-tools: Bash(git *), Bash(gh *), Task
description: Crea PR con pre-review dual (code quality + security)
---

# Pull Request

Workflow automatizado para crear PR con validación de calidad y seguridad.

**Input**: `$ARGUMENTS` = target branch (ej: "main")

## Format Detection

Detecta automáticamente formato de commits:

- **Corporate**: `Tipo|IdTarea|YYYYMMDD|Descripción` → preserva como PR title
- **Conventional**: `type(scope): description` → preserva como PR title

Detection: Si primer commit match `{word}|{UPPERCASE-DIGITS}|{8digits}|{text}` = corporate, sino conventional.

## Temporary Branch Naming

Cuando crea branch temporal desde protected branch (main, master, develop, staging, production):

**Formato**: `temp-{keywords}-{timestamp}` (max 60 chars, lowercase-hyphen, timestamp: YYYYMMDDHHmmss)

## Paso 1: Validación Inicial

Ejecutar en bash (usa `bash <<'SCRIPT'...SCRIPT` para compatibilidad zsh):

```bash
# Parse and validate target branch
target_branch="$ARGUMENTS"
target_branch=$(echo "$target_branch" | xargs)

if [ -z "$target_branch" ]; then
  echo "❌ Error: No target branch specified"
  exit 1
fi

# Validate format
if ! echo "$target_branch" | grep -Eq '^[a-zA-Z0-9/_-]+$'; then
  echo "❌ Error: Invalid branch name format"
  exit 1
fi

if echo "$target_branch" | grep -Eq '^--'; then
  echo "❌ Error: Branch name cannot start with --"
  exit 1
fi

# Fetch and validate target branch exists
git fetch origin

if ! git branch -r | grep -q "origin/$target_branch"; then
  echo "❌ Error: Branch origin/$target_branch does not exist"
  exit 1
fi

# Count commits
commit_count=$(git rev-list --count "origin/$target_branch..HEAD" --)

if [ "$commit_count" -eq 0 ]; then
  echo "❌ Error: No commits to create PR"
  exit 1
fi

# Save state
current_branch=$(git branch --show-current)

git config --local pr.temp.target-branch "$target_branch"
git config --local pr.temp.current-branch "$current_branch"
git config --local pr.temp.commit-count "$commit_count"
```

## Paso 2A: Análisis de Commits - Extracción de Metadata

Ejecutar en bash para extraer metadata:

```bash
target_branch=$(git config --local pr.temp.target-branch)

# 1. Extract commit logs (usar archivo temporal para evitar truncamiento git config)
git_log_raw=$(git log --pretty=format:'- %s' "origin/$target_branch..HEAD" --)
echo "$git_log_raw" > .git/pr-temp-commits.txt

# Get first commit for format detection and title
first_commit=$(git log --pretty=format:'%s' "origin/$target_branch..HEAD" -- | head -1)
git config --local pr.temp.first-commit "$first_commit"

# 2. Extract statistics
stats=$(git diff --shortstat "origin/$target_branch..HEAD" --)

if [ -z "$stats" ]; then
  files_changed=0
  additions=0
  deletions=0
else
  files_changed=$(echo "$stats" | grep -oE '[0-9]+ file' | grep -oE '[0-9]+')
  additions=$(echo "$stats" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+')
  deletions=$(echo "$stats" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+')
fi

git config --local pr.temp.files-changed "${files_changed:-0}"
git config --local pr.temp.additions "${additions:-0}"
git config --local pr.temp.deletions "${deletions:-0}"

# 3. Detect format and extract primary type
# Corporate format pattern: "word|CAPS-NUM|8digits|text"
if echo "$first_commit" | grep -Eq '^[a-z]+\|[A-Z]+-[0-9]+\|[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]\|'; then
  commit_format="corporate"
  primary_type=$(echo "$first_commit" | cut -d'|' -f1)
else
  commit_format="conventional"
  # Extract type from conventional: "type(scope): msg" or "type: msg"
  primary_type=$(echo "$first_commit" | grep -oE '^[a-z]+' | head -1)
  if [ -z "$primary_type" ]; then
    primary_type="feat"
  fi
fi

git config --local pr.temp.commit-format "$commit_format"
git config --local pr.temp.primary-type "$primary_type"

# 4. Extract breaking changes (optional)
breaking=$(git log --pretty=format:'%B' "origin/$target_branch..HEAD" -- | grep -iE 'BREAKING' || echo "")
if [ -n "$breaking" ]; then
  git config --local pr.temp.breaking-changes "$breaking"
fi
```

## Paso 2B: Selección de Título del PR (solo formato corporate)

**Si `commit_format = "corporate"`**, preguntar al usuario sobre el título del PR:

1. Leer valores guardados en git config:

   ```bash
   first_commit=$(git config --local pr.temp.first-commit)
   commit_format=$(git config --local pr.temp.commit-format)
   ```

2. Si `commit_format = "corporate"`, mostrar al usuario:
   - El primer commit detectado: `{first_commit}`
   - Mensaje: "Este será el título del PR basado en el primer commit."

3. Usar **AskUserQuestion tool** para preguntar al usuario:

   **Question**: "¿Deseas usar el primer commit como título del PR o proporcionar un título personalizado?"

   **Options**:
   - **A**: "Usar primer commit" (default) — Descripción: "El PR usará: `{first_commit}`"
   - **B**: "Título personalizado" — Descripción: "Proporcionarás un título en formato corporativo personalizado"

4. Si usuario selecciona **Opción B**:
   - Pedir input adicional: "Ingresa el título personalizado en formato: `tipo|TASK-ID|YYYYMMDD|descripción`"
   - Ejemplo: `refactor|TRV-350|20251023|mejora sistema autenticación`
   - Tipos válidos: feat, fix, refactor, chore, docs, test, security
   - Proceder al Paso 2C para validar

5. Si usuario selecciona **Opción A** o formato NO es corporate:
   - Continuar al Paso 3 (sin Paso 2C)

## Paso 2C: Validación y Almacenamiento de Título Personalizado

**Solo ejecutar si usuario proporcionó título personalizado en Paso 2B.**

Ejecutar en bash:

```bash
# Título personalizado proporcionado por usuario
custom_title="$CUSTOM_TITLE_FROM_USER"

# Validar formato corporativo: tipo|TASK-ID|YYYYMMDD|descripción
if echo "$custom_title" | grep -Eq '^(feat|fix|refactor|chore|docs|test|security)\|[A-Z]+-[0-9]+\|[0-9]{8}\|.+$'; then
  # Formato válido: guardar
  git config --local pr.temp.custom-title "$custom_title"

  # Extraer primary type del título personalizado
  primary_type=$(echo "$custom_title" | cut -d'|' -f1)
  git config --local pr.temp.primary-type "$primary_type"

  echo "✅ Título personalizado guardado: $custom_title"
else
  echo "⚠️  Formato inválido. Usando primer commit como fallback."
  echo "   Formato esperado: tipo|TASK-ID|YYYYMMDD|descripción"
  echo "   Ejemplo: refactor|TRV-350|20251023|mejora autenticación"
fi
```

## Paso 3: Reviews en Paralelo (BLOQUEANTE)

Ejecutar Task tool en **paralelo**:

### Review 1: Plan Alignment & Quality

```
Prompt: "Review implementation in current branch vs origin/$target_branch.

Analyze:
1. Plan alignment (if planning document exists in .specify/ or docs/)
2. Code quality and best practices
3. Architecture and design patterns
4. Documentation completeness

Return structured findings categorized as:
- Critical (must fix before deployment)
- Important (should fix, affects maintainability)
- Suggestions (nice to have, optional improvements)

Focus on maintainability, testability, and adherence to project standards defined in CLAUDE.md."

Agent: code-reviewer
```

### Review 2: Production Readiness (CI/CD Prevention)

```
Prompt: "Production-readiness review of changes in current branch vs origin/$target_branch.

This review MUST replicate CI/CD bot logic to prevent GitHub Actions failures.

Analyze ALL categories:
- SECURITY vulnerabilities (with false positive filtering)
- BUG risks (logical errors, edge cases)
- RELIABILITY issues (error handling, resilience)
- PERFORMANCE problems (production impact)
- CONSTITUTIONAL compliance (Δ LOC budget from CLAUDE.md §3)
- MAINTAINABILITY concerns (when materially impactful)

Return findings with EXACT format:
- Category: SECURITY | BUG | RELIABILITY | PERFORMANCE | MAINTAINABILITY
- Severity: BLOCKER | CRITICAL | MAJOR | MINOR | NIT
- Confidence: 0.00-1.00 (drop findings < 0.80)
- File: <path>:<line>
- Why: 1-3 sentences tying evidence to impact
- Fix: minimal concrete patch or precise steps

Review Decision:
- BLOCK if any BLOCKER severity
- BLOCK if any CRITICAL with confidence ≥0.80
- WARN if only MAJOR/MINOR/NIT
- APPROVE if no valid findings

Return '✅ APPROVED' if no issues, otherwise list all findings."

Agent: ci-cd-pre-reviewer
```

### Evaluación de Resultados

Ejecutar en bash:

```bash
# Check code-reviewer results
code_review_critical=false
if echo "$code_review_result" | grep -Eq 'Critical'; then
  code_review_critical=true
fi

# Check ci-cd-pre-reviewer results (blockers)
has_blockers=false
if echo "$ci_cd_review_result" | grep -Eq 'Severity.*:.*BLOCKER'; then
  has_blockers=true
elif echo "$ci_cd_review_result" | grep -Eq 'Severity.*:.*CRITICAL'; then
  if echo "$ci_cd_review_result" | grep -Eq 'Confidence.*:.*(0\.[89]|1\.0)'; then
    has_blockers=true
  fi
fi

# Block PR if blockers detected
if [ "$has_blockers" = "true" ]; then
  echo "❌ PR BLOQUEADO: Issues críticos detectados por ci-cd-pre-reviewer"
  echo "   (BLOCKER severity o CRITICAL con confidence ≥0.8)"
  echo ""
  echo "Findings:"
  echo "$ci_cd_review_result"
  git config --local --remove-section pr.temp 2>/dev/null
  exit 1
fi

# Warn if code-reviewer found critical issues
if [ "$code_review_critical" = "true" ]; then
  echo "⚠️  WARNING: code-reviewer encontró issues críticos"
  echo "Findings:"
  echo "$code_review_result"
  echo ""
  read -p "¿Continuar con PR? (y/n): " continue_choice
  if [ "$continue_choice" != "y" ]; then
    git config --local --remove-section pr.temp 2>/dev/null
    exit 1
  fi
fi
```

**Lógica de bloqueo:**
- ci-cd-pre-reviewer BLOCKER → automático (sin preguntar)
- ci-cd-pre-reviewer CRITICAL + confidence ≥0.8 → automático
- code-reviewer Critical → pregunta al usuario

## Paso 4: Push Branch

Ejecutar en bash:

1. **Check if current branch is protected**:

   ```bash
   current_branch=$(git config --local pr.temp.current-branch)
   if echo "$current_branch" | grep -Eq '^(main|master|develop|staging|production)$'; then
     is_protected=true
   else
     is_protected=false
   fi
   ```

2. **If protected branch, create temporary branch**:

   ```bash
   if [ "$is_protected" = "true" ]; then
     first_commit=$(git config --local pr.temp.first-commit)
     timestamp=$(date +%Y%m%d%H%M%S)

     # Generate branch suffix: simple approach
     # Convert to lowercase, remove special chars, take first 3-4 words
     first_commit_clean=$(echo "$first_commit" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 ]/ /g')
     branch_suffix=$(echo "$first_commit_clean" | awk '{for(i=1;i<=4 && i<=NF;i++) printf "%s-",$i}' | sed 's/-$//')

     # Truncate to max 39 chars (60 total - 21 overhead = 39 for suffix)
     branch_suffix=$(echo "$branch_suffix" | cut -c1-39 | sed 's/-$//')

     # Fallback if empty
     if [ -z "$branch_suffix" ]; then
       branch_suffix="feature"
     fi

     temp_branch="temp-${branch_suffix}-${timestamp}"

     # Validate branch doesn't exist
     if git show-ref --verify --quiet "refs/heads/$temp_branch"; then
       echo "❌ Branch $temp_branch already exists"
       git config --local --remove-section pr.temp 2>/dev/null
       exit 1
     fi

     # Create and push
     git checkout -b "$temp_branch"
     git push origin "$temp_branch" --set-upstream

     # Save branch name
     git config --local pr.temp.branch-name "$temp_branch"
   else
     # Push current branch
     branch_to_push="$current_branch"

     # Check if has upstream
     if ! git rev-parse --abbrev-ref "$branch_to_push@{upstream}" >/dev/null 2>&1; then
       git push origin "$branch_to_push" --set-upstream
     else
       git push origin "$branch_to_push"
     fi

     git config --local pr.temp.branch-name "$branch_to_push"
   fi
   ```

## Paso 5: Crear PR con gh CLI

Ejecutar en bash:

```bash
# 1. Retrieve metadata from git config y archivo temporal
target_branch=$(git config --local pr.temp.target-branch)
commit_count=$(git config --local pr.temp.commit-count)
git_log=$(cat .git/pr-temp-commits.txt)
first_commit=$(git config --local pr.temp.first-commit)
files_changed=$(git config --local pr.temp.files-changed)
additions=$(git config --local pr.temp.additions)
deletions=$(git config --local pr.temp.deletions)
commit_format=$(git config --local pr.temp.commit-format)
primary_type=$(git config --local pr.temp.primary-type)
breaking=$(git config --local pr.temp.breaking-changes 2>/dev/null || echo "")

# 2. Generate PR title based on format
# Priority: custom_title > first_commit
custom_title=$(git config --local pr.temp.custom-title 2>/dev/null || echo "")

if [ -n "$custom_title" ]; then
  # User provided custom title (Paso 2B/2C)
  pr_title="$custom_title"
elif [ "$commit_format" = "corporate" ]; then
  # Preserve corporate format from first commit
  pr_title="$first_commit"
else
  # Use conventional format from first commit
  pr_title="$first_commit"
fi

# 3. Generate test items based on primary type
case "$primary_type" in
  feat)
    test_items="- [ ] Nueva funcionalidad probada
- [ ] Tests agregados
- [ ] Docs actualizada"
    ;;
  fix)
    test_items="- [ ] Bug reproducido y verificado
- [ ] Tests de regresión agregados
- [ ] Staging verificado"
    ;;
  refactor)
    test_items="- [ ] Tests existentes pasan
- [ ] Funcionalidad equivalente verificada"
    ;;
  *)
    test_items="- [ ] Cambios verificados localmente
- [ ] Build exitoso"
    ;;
esac

# 4. Generate PR body
temp_file=$(mktemp)
cat > "$temp_file" <<EOF
## Summary

Changes based on **$primary_type** commits affecting **$files_changed** files.

## Changes Made ($commit_count commits)

$git_log

## Files & Impact

- **Files modified**: $files_changed
- **Lines**: +$additions -$deletions

## Test Plan

$test_items

$(if [ -n "$breaking" ]; then echo "## Breaking Changes"; echo "$breaking"; fi)
EOF

# 5. Create PR
pr_url=$(gh pr create --title "$pr_title" --body-file "$temp_file" --base "$target_branch" 2>&1 | grep -oE 'https://[^ ]+')
rm "$temp_file"

# 6. Cleanup
git config --local --remove-section pr.temp
rm -f .git/pr-temp-commits.txt
echo "✅ PR created: $pr_url"
```

**Output**: PR URL

## Seguridad

**Prevención de Command Injection**:

1. Todas las variables git quoted: `"$var"` nunca `$var`
2. Git commands con separator: `git cmd "ref" --`
3. Rechazar branches que empiezan con `--`
4. Sanitizar outputs: `tr -d '\`$'`

## Rollback

En cualquier error:

```bash
git config --local --remove-section pr.temp 2>/dev/null
rm -f .git/pr-temp-commits.txt 2>/dev/null
exit 1
```

Si se creó feature branch temporal y falló push:

```bash
git checkout "$original_branch"
git branch -d "$temp_branch"
```

## Notas

- **Git config state**: Usar `pr.temp.*` para pasar estado entre pasos
- **Dual review bloqueante**: Security HIGH ≥0.8 confidence bloquea automáticamente
