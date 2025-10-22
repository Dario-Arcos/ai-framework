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

## Paso 2: Análisis de Commits

Ejecutar en bash para extraer metadata:

```bash
target_branch=$(git config --local pr.temp.target-branch)

# 1. Extract commit logs
git_log_raw=$(git log --pretty=format:'- %s' "origin/$target_branch..HEAD" --)
git config --local pr.temp.git-log "$git_log_raw"

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
       git config --local --unset-all pr.temp
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
# 1. Retrieve metadata from git config
target_branch=$(git config --local pr.temp.target-branch)
commit_count=$(git config --local pr.temp.commit-count)
git_log=$(git config --local pr.temp.git-log)
first_commit=$(git config --local pr.temp.first-commit)
files_changed=$(git config --local pr.temp.files-changed)
additions=$(git config --local pr.temp.additions)
deletions=$(git config --local pr.temp.deletions)
commit_format=$(git config --local pr.temp.commit-format)
primary_type=$(git config --local pr.temp.primary-type)
breaking=$(git config --local pr.temp.breaking-changes 2>/dev/null || echo "")

# 2. Generate PR title based on format
if [ "$commit_format" = "corporate" ]; then
  # Preserve corporate format
  pr_title="$first_commit"
else
  # Use conventional format
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
git config --local --unset-all pr.temp
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
git config --local --unset-all pr.temp 2>/dev/null
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
