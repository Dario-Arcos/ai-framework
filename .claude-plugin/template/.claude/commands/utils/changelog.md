---
allowed-tools: Bash(git *, gh *, jq *, npm version *)
description: Actualiza CHANGELOG.md con PRs pendientes y opcionalmente ejecuta release
---

# Changelog Update

Actualiza CHANGELOG.md con PRs mergeados siguiendo [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

## Uso

```bash
/changelog                     # Auto-detectar PRs → actualizar → preguntar release
```

## Ejecución

Cuando ejecutes este comando, sigue estos pasos:

### 1. Validar herramientas y CHANGELOG

```bash
command -v gh >/dev/null 2>&1 || {
  echo "❌ Error: gh CLI requerido"
  echo "💡 Instalar: https://cli.github.com/"
  exit 1
}
command -v jq >/dev/null 2>&1 || {
  echo "❌ Error: jq requerido"
  echo "💡 Instalar: brew install jq (macOS) o apt install jq (Ubuntu)"
  exit 1
}
[[ -f CHANGELOG.md ]] || {
  echo "❌ Error: CHANGELOG.md no encontrado en $(pwd)"
  echo "💡 Asegúrate de estar en la raíz del proyecto"
  exit 1
}

grep -q "^## \[No Publicado\]" CHANGELOG.md || {
  echo "❌ Error: Sección [No Publicado] no encontrada en CHANGELOG.md"
  echo "💡 Agrega la sección al inicio del CHANGELOG"
  exit 1
}
```

### 2. Auto-detectar PRs pendientes

```bash
echo "🔍 Auto-detectando PRs pendientes..."

last_pr=$(grep -oE 'PR #[0-9]+' CHANGELOG.md | grep -oE '[0-9]+' | sort -n | tail -1)
[[ -n "$last_pr" ]] || {
  echo "❌ Error: No se encontró PR previo en CHANGELOG"
  echo "💡 Agrega manualmente el primer PR"
  exit 1
}
echo "📍 Último PR documentado: #$last_pr"

pr_list=$(git log --pretty=format:"%s" --all | \
  grep -oE '(#[0-9]+|Merge pull request #[0-9]+|\(#[0-9]+\))' | \
  grep -oE '[0-9]+' | sort -n -u | \
  awk -v last="$last_pr" '$1 > last')

[[ -n "$pr_list" ]] || {
  echo "✓ CHANGELOG actualizado - no hay PRs nuevos posteriores a #$last_pr"
  exit 0
}

pr_count=$(echo "$pr_list" | wc -w | xargs)
echo "🔍 Encontrados $pr_count PRs nuevos: $(echo $pr_list | tr '\n' ' ')"
```

### 3. Actualizar CHANGELOG con PRs validados

```bash
added_count=0

for pr in $pr_list; do
  # Validar PR en GitHub
  pr_data=$(gh pr view "$pr" --json state,title 2>/dev/null)
  [[ -n "$pr_data" ]] || {
    echo "⚠️  PR #$pr no encontrado en GitHub - omitido"
    continue
  }

  # Verificar que está mergeado
  state=$(echo "$pr_data" | jq -r '.state')
  [[ "$state" == "MERGED" ]] || {
    echo "⚠️  PR #$pr no está mergeado (estado: $state) - omitido"
    continue
  }

  # Detectar duplicados
  if grep -q "(PR #$pr)" CHANGELOG.md; then
    echo "⚠️  PR #$pr ya existe en CHANGELOG - omitido"
    continue
  fi

  # Sanitizar título (prevenir inyección de comandos)
  title=$(echo "$pr_data" | jq -r '.title' | sed 's/[&/\$]/\\&/g' | tr -d '\n\r')

  # Limpiar prefijo de tipo (feat:, fix:, etc)
  clean_title=$(echo "$title" | sed -E 's/^(feat|fix|refactor|docs|style|test|chore|security|perf|ci|build|revert)(\([^)]+\))?!?:\s*//')

  # Insertar en sección [No Publicado]
  unreleased_line=$(grep -n "^## \[No Publicado\]" CHANGELOG.md | cut -d: -f1)
  insert_line=$((unreleased_line + 2))

  sed -i.bak "${insert_line}i\\
- $clean_title (PR #$pr)\\
" CHANGELOG.md || {
    echo "❌ Error: Falló inserción de PR #$pr"
    exit 1
  }

  echo "✓ PR #$pr agregado: $clean_title"
  added_count=$((added_count + 1))
done

rm -f CHANGELOG.md.bak

[[ $added_count -eq 0 ]] && {
  echo "✓ No se agregaron PRs nuevos"
  exit 0
}

echo "✅ $added_count PRs agregados al CHANGELOG"
```

### 4. Commit automático del CHANGELOG

```bash
git add CHANGELOG.md

commit_prs=$(echo $pr_list | tr '\n' ',' | sed 's/,$//' | tr ' ' ',')
git commit -m "docs: update CHANGELOG with PRs $commit_prs" || {
  echo "❌ Error: Commit falló"
  exit 1
}

echo "✅ CHANGELOG commiteado"
```

### 5. Preguntar por release

```bash
echo ""
echo "¿Quieres ejecutar un release ahora?"
echo ""
echo "  [1] patch (1.1.1 → 1.1.2) - Bug fixes"
echo "  [2] minor (1.1.1 → 1.2.0) - New features"
echo "  [3] major (1.1.1 → 2.0.0) - Breaking changes"
echo "  [4] No, solo actualizar CHANGELOG"
echo ""
read -p "Selecciona opción [1-4]: " choice

case $choice in
  1) release_type="patch" ;;
  2) release_type="minor" ;;
  3) release_type="major" ;;
  *)
    echo "✓ CHANGELOG actualizado sin release"
    echo "💡 Para hacer release más tarde: /changelog"
    exit 0
    ;;
esac

echo "🚀 Ejecutando release $release_type..."

# Validar package.json
[[ -f package.json ]] || {
  echo "❌ Error: package.json no encontrado"
  exit 1
}

current_version=$(jq -r '.version // empty' package.json)
[[ -n "$current_version" ]] || {
  echo "❌ Error: package.json no tiene campo 'version'"
  exit 1
}

echo "📍 Versión actual: $current_version"

# Calcular nueva versión
new_version=$(npm version "$release_type" --no-git-tag-version 2>/dev/null | tr -d 'v')
[[ -n "$new_version" ]] || {
  echo "❌ Error: npm version falló"
  exit 1
}

current_date=$(date +%Y-%m-%d)
echo "📍 Nueva versión: $new_version ($current_date)"

# Reemplazar [No Publicado] con versión
sed -i.bak "s/^## \[No Publicado\]/## [$new_version] - $current_date/" CHANGELOG.md

# Crear nueva sección [No Publicado]
header_end=$(grep -n "^---$" CHANGELOG.md | head -1 | cut -d: -f1)
insert_line=$((header_end + 2))

sed -i.bak "${insert_line}i\\
## [No Publicado]\\
\\
- [Cambios futuros se documentan aquí]\\
\\
---\\
" CHANGELOG.md

rm -f CHANGELOG.md.bak

# Ejecutar npm version para sincronizar
npm version "$new_version" --allow-same-version || {
  echo "❌ Error: npm version falló en sincronización"
  exit 1
}

echo "✅ Release $release_type completado: v$new_version"
echo "📝 Commit y tag creados automáticamente"
echo "💡 Push con: git push origin main --follow-tags"
```

## Notas

- **Auto-detección**: Detecta automáticamente PRs mergeados desde el último PR documentado
- **Sanitización**: Títulos de PR sanitizados para prevenir inyección de comandos
- **Commit automático**: CHANGELOG se commitea automáticamente después de actualizar
- **Release interactivo**: El usuario decide si ejecutar release y qué tipo
- **Duplicados**: PRs existentes se omiten automáticamente
