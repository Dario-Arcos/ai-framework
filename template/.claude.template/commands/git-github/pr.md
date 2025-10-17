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
# Validar jq instalado
if ! command -v jq &>/dev/null; then
  echo "⚠️  jq no instalado, omitiendo verificación de PR existente"
  pr_exists=""
else
  pr_exists=$(gh pr view --json state,url 2>/dev/null)
fi

if [ -n "$pr_exists" ] && echo "$pr_exists" | jq -e '.state == "OPEN"' >/dev/null 2>&1; then
  pr_url=$(echo "$pr_exists" | jq -r '.url')
  echo "⚠️  PR abierto detectado, actualizando..."
  git push origin HEAD || { echo "❌ Push falló"; exit 1; }
  echo "✅ PR actualizado: $pr_url"
  exit 0
fi
```

### 3. Preparar branch temporal (si es rama protegida)

```bash
PROTECTED_BRANCHES="^(main|master|develop|dev|staging|production|prod|qa)$"

if echo "$current_branch" | grep -Eq "$PROTECTED_BRANCHES"; then
  branch_name="pr-$(date -u +%Y%m%d-%H%M%S)"

  git checkout -b "$branch_name" || { echo "❌ Crear branch falló"; exit 1; }
  echo "✓ Branch temporal creado: $branch_name"
else
  branch_name="$current_branch"
  echo "✓ Usando branch actual: $branch_name"
fi
```

### 4. Pre-review de calidad (BLOQUEANTE)

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
    n|N)
      # Rollback: eliminar branch temporal si fue creado
      if echo "$current_branch" | grep -Eq "$PROTECTED_BRANCHES"; then
        echo "✓ Eliminando branch temporal..."
        git checkout "$current_branch"
        git branch -d "$branch_name" 2>/dev/null
      fi
      echo "✓ Corrige issues y reintenta: /pr $target_branch"
      exit 0
      ;;
    *)
      # Rollback: eliminar branch temporal si fue creado
      if echo "$current_branch" | grep -Eq "$PROTECTED_BRANCHES"; then
        git checkout "$current_branch"
        git branch -d "$branch_name" 2>/dev/null
      fi
      echo "✓ Descartado"
      exit 0
      ;;
  esac
fi
```

### 5. Push branch

```bash
if ! git config "branch.$branch_name.remote" >/dev/null 2>&1; then
  git push origin "$branch_name" --set-upstream || {
    echo "❌ Push falló"
    # Rollback si era branch temporal
    if [ "$branch_name" != "$current_branch" ]; then
      git checkout "$current_branch"
      git branch -d "$branch_name" 2>/dev/null
    fi
    exit 1
  }
else
  git push origin "$branch_name" || {
    echo "❌ Push falló"
    exit 1
  }
fi

echo "✓ Branch pushed: $branch_name"
```

### 6. Crear PR

```bash
git_log=$(git log --pretty=format:'- %s' origin/$target_branch..HEAD)
files_stat=$(git diff --shortstat origin/$target_branch..HEAD)
pr_title=$(git log --pretty=format:'%s' origin/$target_branch..HEAD | head -1)

# Construir body usando HEREDOC para evitar problemas con caracteres especiales
if [ -n "$quality_review_result" ]; then
  pr_body=$(cat <<EOF
## Changes
$git_log

$files_stat

## ⚠️ Code Quality Issues
$quality_review_result
EOF
)
else
  pr_body=$(cat <<EOF
## Changes
$git_log

$files_stat
EOF
)
fi

echo "🚀 Creando PR..."

pr_url=$(gh pr create --title "$pr_title" --body "$pr_body" --base "$target_branch" 2>&1 | grep -oE 'https://[^ ]+')

if [ -z "$pr_url" ]; then
  echo "❌ gh pr create falló"
  # Rollback: eliminar branch temporal si fue creado
  if [ "$branch_name" != "$current_branch" ]; then
    git checkout "$current_branch"
    git branch -d "$branch_name" 2>/dev/null
  fi
  exit 1
fi

echo "✅ PR creado: $pr_url"
[ -n "$quality_review_result" ] && echo "⚠️  Contiene quality issues documentados"
```

## Notas

- Pre-review bloqueante con `code-quality-reviewer`
- Auto-update si PR ya existe
- Branch temporal CREADO ANTES del review (permite correcciones)
- Rollback completo si usuario cancela o falla
- HEREDOC para pr_body (maneja caracteres especiales)
- Validación de jq antes de usar
