---
allowed-tools: Bash(git *), Bash(gh *), Task
description: Crea PR desde rama actual con pre-review de calidad
---

# Pull Request

Crea Pull Request con pre-review automático de calidad.

## Uso

```bash
/pr <target_branch>
```

## Ejecución

Sigue estos pasos en orden:

### 1. Validaciones básicas

```bash
target_branch="$ARGUMENTS"
[ -z "$target_branch" ] && { echo "❌ Uso: /pr <target_branch>"; exit 1; }

git fetch origin || { echo "❌ git fetch falló"; exit 1; }

current_branch=$(git branch --show-current)
[ -z "$current_branch" ] && { echo "❌ No estás en ninguna rama"; exit 1; }

commit_count=$(git rev-list --count origin/$target_branch..HEAD 2>/dev/null || echo "0")
[ "$commit_count" -eq 0 ] && { echo "❌ No hay commits para PR"; exit 1; }

commits_behind=$(git rev-list --count HEAD..origin/$target_branch 2>/dev/null || echo "0")

echo "📍 $current_branch → $target_branch ($commit_count commits)"
[ "$commits_behind" -gt 0 ] && echo "⚠️  $commits_behind commits atrás de origin/$target_branch"
```

### 2. Verificar PR existente

```bash
pr_exists=$(gh pr view --json state,url 2>/dev/null)

if [ -n "$pr_exists" ] && echo "$pr_exists" | jq -e '.state == "OPEN"' >/dev/null 2>&1; then
  pr_url=$(echo "$pr_exists" | jq -r '.url')
  echo "⚠️  PR abierto detectado, actualizando..."
  git push origin HEAD || { echo "❌ Push falló"; exit 1; }
  echo "✅ PR actualizado: $pr_url"
  exit 0
fi
```

### 3. Pre-review de calidad (BLOQUEANTE)

**Claude DEBE ejecutar Task tool aquí:**

Invocar `code-quality-reviewer` con prompt:

```
Review changes in current branch vs origin/$target_branch.
Return '✅ NO_ISSUES' if clean, otherwise list issues as:
## Critical
- issue
## Warnings
- warning
```

Capturar output en `$quality_review_result` y evaluar:

```bash
echo "🔍 Code quality review..."

# Variable $quality_review_result disponible desde Task output
if echo "$quality_review_result" | grep -q "✅ NO_ISSUES"; then
  echo "✅ Sin issues detectados"
  quality_review_result=""
else
  echo ""
  echo "⚠️  Issues detectados:"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "$quality_review_result"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  read -p "¿Crear PR igual (y), corregir (n), descartar (d)? " choice

  case $choice in
    y|Y) echo "⚠️  Creando PR con issues conocidos..." ;;
    n|N) echo "✓ Corrige issues y reintenta: /pr $target_branch"; exit 0 ;;
    *) echo "✓ Descartado"; exit 0 ;;
  esac
fi
```

### 4. Preparar branch y push

```bash
PROTECTED_BRANCHES="^(main|master|develop|dev|staging|production|prod|qa)$"

if echo "$current_branch" | grep -Eq "$PROTECTED_BRANCHES"; then
  branch_name="pr-$(date -u +%Y%m%d-%H%M%S)"

  git checkout -b "$branch_name" || { echo "❌ Crear branch falló"; exit 1; }

  if ! git push origin "$branch_name" --set-upstream; then
    echo "❌ Push falló, rollback..."
    git checkout "$current_branch"
    git branch -d "$branch_name" 2>/dev/null
    exit 1
  fi

  echo "✓ Branch temporal: $branch_name"
else
  branch_name="$current_branch"

  if ! git config "branch.$current_branch.remote" >/dev/null 2>&1; then
    git push origin "$current_branch" --set-upstream
  else
    git push origin "$current_branch"
  fi || { echo "❌ Push falló"; exit 1; }
fi
```

### 5. Crear PR

```bash
git_log=$(git log --pretty=format:'- %s' origin/$target_branch..HEAD)
files_stat=$(git diff --shortstat origin/$target_branch..HEAD)
pr_title=$(git log --pretty=format:'%s' origin/$target_branch..HEAD | head -1)

quality_section=""
[ -n "$quality_review_result" ] && quality_section="

## ⚠️ Code Quality Issues
$quality_review_result"

pr_body="## Changes
$git_log

$files_stat
$quality_section"

echo "🚀 Creando PR..."

pr_url=$(gh pr create --title "$pr_title" --body "$pr_body" --base "$target_branch" 2>&1 | grep -oE 'https://[^ ]+')
[ -z "$pr_url" ] && { echo "❌ gh pr create falló"; exit 1; }

echo "✅ PR creado: $pr_url"
[ -n "$quality_review_result" ] && echo "⚠️  Contiene quality issues documentados"
```

## Notas

- Pre-review bloqueante con `code-quality-reviewer`
- Auto-update si PR ya existe
- Branch temporal si estás en rama protegida
