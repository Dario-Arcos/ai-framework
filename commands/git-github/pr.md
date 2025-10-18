---
allowed-tools: Bash(git *), Bash(gh *), Task
description: Crea PR con pre-review dual (code quality + security)
---

# Pull Request

Crea Pull Request con análisis automático de calidad y seguridad.

## Uso

```bash
/pr <target_branch>
```

## Ejecución

### 1. Validaciones completas

```bash
target_branch="$ARGUMENTS"
[ -z "$target_branch" ] && { echo "❌ Uso: /pr <target_branch>"; exit 1; }

if ! echo "$target_branch" | grep -Eq '^[a-zA-Z0-9/_-]+$'; then
  echo "❌ Nombre de target branch inválido"
  exit 1
fi

git fetch origin || { echo "❌ git fetch falló"; exit 1; }

current_branch=$(git branch --show-current)
[ -z "$current_branch" ] && { echo "❌ No estás en ninguna rama"; exit 1; }

if ! git branch -r | grep -q "origin/$target_branch"; then
  echo "❌ Branch objetivo no existe: origin/$target_branch"
  exit 1
fi

PROTECTED_BRANCHES="^(main|master|develop|dev|staging|production|prod|qa|release/.+|hotfix/.+)$"
if [ "$current_branch" = "$target_branch" ]; then
  if echo "$current_branch" | grep -Eq "$PROTECTED_BRANCHES"; then
    echo "⚠️  Rama protegida detectada: se creará feature branch automática"
    git config --local pr.temp.auto-create "true"
  else
    echo "❌ No puedes crear PR de una rama hacia sí misma"
    echo "   (current: $current_branch, target: $target_branch)"
    exit 1
  fi
fi

commits_behind=$(git rev-list --count HEAD..origin/$target_branch 2>/dev/null || echo "0")
[ "$commits_behind" -gt 0 ] && echo "⚠️  Tu rama está $commits_behind commits atrás de origin/$target_branch"

if git config "branch.$current_branch.remote" >/dev/null 2>&1; then
  commits_behind_own=$(git rev-list --count HEAD..origin/$current_branch 2>/dev/null || echo "0")
  if [ "$commits_behind_own" -gt 0 ]; then
    echo "❌ Tu rama $current_branch está $commits_behind_own commits atrás de origin/$current_branch"
    echo "   Sincroniza primero: git pull origin $current_branch"
    exit 1
  fi
fi

commit_count=$(git rev-list --count origin/$target_branch..HEAD 2>/dev/null || echo "0")
[ "$commit_count" -eq 0 ] && { echo "❌ No hay commits para PR"; exit 1; }

echo "📍 $current_branch → $target_branch ($commit_count commits)"

git config --local pr.temp.target-branch "$target_branch"
git config --local pr.temp.current-branch "$current_branch"
git config --local pr.temp.commit-count "$commit_count"
```

### 2. Verificar PR existente

```bash
target_branch=$(git config --local pr.temp.target-branch)
current_branch=$(git config --local pr.temp.current-branch)

if ! command -v jq &>/dev/null; then
  echo "⚠️  jq no instalado, omitiendo verificación de PR existente"
  pr_exists=""
else
  pr_exists=$(gh pr view --json state,url 2>/dev/null)
fi

if [ -n "$pr_exists" ] && echo "$pr_exists" | jq -e '.state == "OPEN"' >/dev/null 2>&1; then
  pr_url=$(echo "$pr_exists" | jq -r '.url')
  echo "⚠️  PR abierto detectado: $pr_url"
  read -p "¿Actualizar PR existente? (Y/n) " choice
  if [ "$choice" != "n" ] && [ "$choice" != "N" ]; then
    git push origin HEAD || { echo "❌ Push falló"; exit 1; }
    echo "✅ PR actualizado: $pr_url"
    git config --local --unset pr.temp.target-branch 2>/dev/null
    git config --local --unset pr.temp.current-branch 2>/dev/null
    git config --local --unset pr.temp.commit-count 2>/dev/null
    exit 0
  fi
fi
```

### 3. Análisis de commits

```bash
target_branch=$(git config --local pr.temp.target-branch)

git_log=$(git log --pretty=format:'- %s' origin/$target_branch..HEAD)
files_stat=$(git diff --shortstat origin/$target_branch..HEAD)
files_changed=$(git diff --name-only origin/$target_branch..HEAD | wc -l | tr -d ' ')

primary_type=$(git log --pretty=format:'%s' origin/$target_branch..HEAD | \
  grep -Eo '^(feat|fix|docs|refactor|style|test|chore|perf)' | \
  sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
[ -z "$primary_type" ] && primary_type="feat"

scope=$(git log --pretty=format:'%s' origin/$target_branch..HEAD | \
  sed -n 's/^[a-z]*(\([^)]*\)).*/\1/p' | \
  sort | uniq -c | sort -rn | head -1 | awk '{print $2}')

breaking=$(git log --pretty=format:'%B' origin/$target_branch..HEAD | \
  grep -iE '(BREAKING|breaking change|deprecated|removed)' || echo "")

stats=$(echo "$files_stat" | awk '{
  for (i=1; i<=NF; i++) {
    if ($i ~ /^[0-9]+$/) {
      if ($(i+1) == "insertion" || $(i+1) == "insertions") additions=$i
      if ($(i+1) == "deletion" || $(i+1) == "deletions") deletions=$i
    }
  }
  print additions " " deletions
}')
additions=$(echo "$stats" | awk '{print $1}')
deletions=$(echo "$stats" | awk '{print $2}')
additions=${additions:-0}
deletions=${deletions:-0}

git config --local pr.temp.git-log "$git_log"
git config --local pr.temp.files-changed "$files_changed"
git config --local pr.temp.primary-type "$primary_type"
git config --local pr.temp.scope "$scope"
git config --local pr.temp.breaking "$breaking"
git config --local pr.temp.additions "$additions"
git config --local pr.temp.deletions "$deletions"
```

### 4. Reviews en paralelo (BLOQUEANTE)

**Claude DEBE ejecutar Task tool DOS VECES en paralelo:**

1. Invocar `code-quality-reviewer`:

```
Review changes in current branch vs origin/$target_branch.
Return '✅ NO_ISSUES' if clean, otherwise list issues as:
## Critical
- issue
## Warnings
- warning
```

2. Invocar `security-reviewer`:

```
Security review of changes in current branch vs origin/$target_branch.
Return '✅ SECURE' if no issues, otherwise list findings with severity.
```

**Capturar resultados**: `quality_review_result` y `security_review_result`

Luego evaluar:

```bash
target_branch=$(git config --local pr.temp.target-branch)
current_branch=$(git config --local pr.temp.current-branch)

echo "🔍 Ejecutando reviews de calidad y seguridad..."

has_quality_issues=false
! echo "$quality_review_result" | grep -q "✅ NO_ISSUES" && has_quality_issues=true

has_security_critical=false
echo "$security_review_result" | grep -Eq '[Ss]everity.*:.*HIGH' && \
  echo "$security_review_result" | grep -Eq '[Cc]onfidence.*:.*(0\.[89]|1\.0)' && \
  has_security_critical=true

if [ "$has_quality_issues" = "true" ] || [ "$has_security_critical" = "true" ]; then
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  [ "$has_quality_issues" = "true" ] && {
    echo "⚠️  Code Quality Issues:"
    echo "$quality_review_result"
    echo ""
  }

  [ "$has_security_critical" = "true" ] && {
    echo "🛡️  Security Findings (CRITICAL):"
    echo "$security_review_result"
    echo ""
  }

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  if [ "$has_security_critical" = "true" ]; then
    echo "❌ PR BLOQUEADO: Vulnerabilidades críticas detectadas"
    echo "   Corrige los issues de seguridad y reintenta: /pr $target_branch"
    git config --local --unset-all pr.temp 2>/dev/null
    exit 1
  fi

  read -p "¿Crear PR con issues conocidos (y), corregir (n), descartar (d)? " choice

  case $choice in
    y|Y)
      echo "⚠️  Creando PR con issues conocidos..."
      git config --local pr.temp.quality-result "$quality_review_result"
      ;;
    n|N)
      echo "✓ Corrige issues y reintenta: /pr $target_branch"
      git config --local --unset-all pr.temp 2>/dev/null
      exit 0
      ;;
    *)
      echo "✓ Descartado"
      git config --local --unset-all pr.temp 2>/dev/null
      exit 0
      ;;
  esac
else
  echo "✅ Reviews pasaron sin issues críticos"
fi
```

### 5. Preparar branch y push

```bash
current_branch=$(git config --local pr.temp.current-branch)
auto_create=$(git config --local pr.temp.auto-create 2>/dev/null || echo "false")
PROTECTED_BRANCHES="^(main|master|develop|dev|staging|production|prod|qa|release/.+|hotfix/.+)$"

if [ "$auto_create" = "true" ] || echo "$current_branch" | grep -Eq "$PROTECTED_BRANCHES"; then
  primary_type=$(git config --local pr.temp.primary-type)
  scope=$(git config --local pr.temp.scope)
  timestamp=$(date -u +%Y%m%d-%H%M%S)
  branch_name="${scope:-$primary_type}-${timestamp}"

  echo "⚠️  Creando feature branch: $branch_name"
  original_branch="$current_branch"

  if ! git checkout -b "$branch_name" || ! git push origin "$branch_name" --set-upstream; then
    echo "❌ Creación/push falló, rollback..."
    git checkout "$original_branch" 2>/dev/null
    git branch -d "$branch_name" 2>/dev/null
    git config --local --unset-all pr.temp 2>/dev/null
    exit 1
  fi
else
  branch_name="$current_branch"
  echo "✓ Usando branch actual: $branch_name"

  push_flags=$(git config "branch.$current_branch.remote" >/dev/null 2>&1 && echo "" || echo "--set-upstream")
  if ! git push origin "$current_branch" $push_flags; then
    echo "❌ Push falló"
    git config --local --unset-all pr.temp 2>/dev/null
    exit 1
  fi
fi

git config --local pr.temp.branch-name "$branch_name"
echo "✓ Branch pushed: $branch_name"
```

### 6. Crear PR con template rico

```bash
target_branch=$(git config --local pr.temp.target-branch)
branch_name=$(git config --local pr.temp.branch-name)
commit_count=$(git config --local pr.temp.commit-count)
git_log=$(git config --local pr.temp.git-log)
files_changed=$(git config --local pr.temp.files-changed)
primary_type=$(git config --local pr.temp.primary-type)
scope=$(git config --local pr.temp.scope)
breaking=$(git config --local pr.temp.breaking)
additions=$(git config --local pr.temp.additions)
deletions=$(git config --local pr.temp.deletions)
quality_result=$(git config --local pr.temp.quality-result 2>/dev/null || echo "")

first_commit=$(git log --pretty=format:'%s' origin/$target_branch..HEAD | head -1 | tr -d '`$')
if [ -n "$scope" ]; then
  pr_title="$first_commit"
elif echo "$first_commit" | grep -Eq '^(feat|fix|docs|refactor|style|test|chore|perf):'; then
  pr_title="$first_commit"
else
  pr_title="${primary_type}: $first_commit"
fi

case $primary_type in
  feat) test_items="Nueva funcionalidad probada manualmente
- [ ] Tests unitarios agregados/actualizados
- [ ] Documentación actualizada" ;;
  fix) test_items="Bug reproducido y verificado como corregido
- [ ] Tests de regresión ejecutados
- [ ] Verificación en ambiente de staging" ;;
  refactor|perf) test_items="Tests existentes pasan sin cambios
- [ ] Funcionalidad equivalente verificada
- [ ] Performance medida (si aplica)" ;;
  *) test_items="Cambios verificados localmente
- [ ] Build exitoso" ;;
esac

pr_body_file=$(mktemp)
breaking_warn=$([ -n "$breaking" ] && echo "⚠️ " || echo "")
breaking_content=$([ -n "$breaking" ] && echo "$breaking" | tr -d '`$' || echo "None")
quality_section=$([ -n "$quality_result" ] && echo "

## ⚠️ Code Quality Issues

$quality_result" || echo "")

cat > "$pr_body_file" <<EOF
## Summary

Changes based on **$primary_type** commits affecting **$files_changed** files.

## Changes Made ($commit_count commits)

$git_log

## Files & Impact

- **Files modified**: $files_changed
- **Lines**: +$additions -$deletions

## Test Plan

- [ ] $test_items

## ${breaking_warn}Breaking Changes

$breaking_content$quality_section
EOF

echo "🚀 Creando PR..."

pr_url=$(gh pr create --title "$pr_title" --body-file "$pr_body_file" --base "$target_branch" 2>&1 | grep -oE 'https://[^ ]+')

rm -f "$pr_body_file"

if [ -z "$pr_url" ]; then
  echo "❌ gh pr create falló"
  git config --local --unset-all pr.temp 2>/dev/null
  exit 1
fi

git config --local --unset-all pr.temp 2>/dev/null

echo "✅ PR creado: $pr_url"
[ -n "$quality_result" ] && echo "⚠️  Contiene quality issues documentados"
```

## Notas

- Dual review (code-quality + security) en paralelo
- Security HIGH bloquea automáticamente
- Template dinámico según tipo de commit
- Branch inteligente para ramas protegidas
- Rollback completo en puntos de fallo
