---
allowed-tools: Bash(git *, npm version *, jq *)
description: Ejecuta workflow completo de release con bump de versión y sincronización
---

# Release

Ejecuta workflow completo de release: bump versión → actualizar CHANGELOG → sync → commit/tag → push.

## Pre-requisitos

- CHANGELOG.md actualizado con `/changelog`
- Sección `[No Publicado]` con cambios documentados

## Uso

```bash
/release    # Workflow completo: pregunta tipo → bump → sync → tag → push?
```

## Ejecución

Cuando ejecutes este comando, sigue estos pasos:

### 1. Validar herramientas y archivos requeridos

```bash
command -v npm >/dev/null 2>&1 || {
  echo "❌ Error: npm requerido"
  echo "💡 Instalar: https://nodejs.org/"
  exit 1
}
command -v jq >/dev/null 2>&1 || {
  echo "❌ Error: jq requerido"
  echo "💡 Instalar: brew install jq (macOS) o apt install jq (Ubuntu)"
  exit 1
}

[[ -f CHANGELOG.md ]] || {
  echo "❌ Error: CHANGELOG.md no encontrado"
  echo "💡 Asegúrate de estar en la raíz del proyecto"
  exit 1
}

[[ -f package.json ]] || {
  echo "❌ Error: package.json no encontrado"
  echo "💡 Asegúrate de estar en la raíz del proyecto"
  exit 1
}

grep -q "^## \[No Publicado\]" CHANGELOG.md || {
  echo "❌ Error: Sección [No Publicado] no encontrada en CHANGELOG.md"
  echo "💡 Ejecuta /changelog primero para actualizar el CHANGELOG"
  exit 1
}
```

### 2. Verificar que [No Publicado] tiene cambios reales

```bash
unreleased_line=$(grep -n "^## \[No Publicado\]" CHANGELOG.md | cut -d: -f1)
next_section_line=$(tail -n +$((unreleased_line + 1)) CHANGELOG.md | grep -n "^## \[" | head -1 | cut -d: -f1)

if [[ -n "$next_section_line" ]]; then
  section_end=$((unreleased_line + next_section_line - 1))
else
  section_end=$(wc -l < CHANGELOG.md)
fi

unreleased_content=$(sed -n "${unreleased_line},${section_end}p" CHANGELOG.md | grep -v "^## \[No Publicado\]" | grep -v "^---$" | grep -v "^\s*$")

if [[ -z "$unreleased_content" ]] || echo "$unreleased_content" | grep -q "^\[Cambios futuros se documentan aquí\]$"; then
  echo "❌ Error: No hay cambios en sección [No Publicado]"
  echo "💡 Ejecuta /changelog para actualizar con PRs pendientes"
  exit 1
fi

echo "✓ Sección [No Publicado] tiene cambios documentados"
```

### 3. Preguntar tipo de release

```bash
current_version=$(jq -r '.version // empty' package.json)
[[ -n "$current_version" ]] || {
  echo "❌ Error: package.json no tiene campo 'version'"
  exit 1
}

echo ""
echo "📍 Versión actual: $current_version"
echo ""
echo "¿Qué tipo de release quieres ejecutar?"
echo ""
echo "  [1] patch ($current_version → X.X.X+1) - Bug fixes, mejoras menores"
echo "  [2] minor ($current_version → X.Y+1.0) - Nuevas features sin breaking changes"
echo "  [3] major ($current_version → X+1.0.0) - Breaking changes"
echo "  [4] Cancelar"
echo ""
read -p "Selecciona opción [1-4]: " choice

case $choice in
  1) release_type="patch" ;;
  2) release_type="minor" ;;
  3) release_type="major" ;;
  *)
    echo "✓ Release cancelado"
    exit 0
    ;;
esac

echo "🚀 Ejecutando release $release_type..."
```

### 4. Ejecutar npm version (auto-dispara sync-versions.cjs)

```bash
echo "📦 Bump versión con npm version $release_type..."

# npm version hace:
# 1. Bump version en package.json
# 2. Auto-ejecuta scripts/sync-versions.cjs (hook npm version)
# 3. Crea git commit "chore: release vX.X.X"
# 4. Crea git tag vX.X.X

new_version=$(npm version "$release_type" 2>&1)
npm_exit_code=$?

if [[ $npm_exit_code -ne 0 ]]; then
  echo "❌ Error: npm version falló"
  echo "$new_version"
  exit 1
fi

# Extraer versión (npm version retorna "vX.X.X")
new_version=$(echo "$new_version" | tr -d 'v')
current_date=$(date +%Y-%m-%d)

echo "✓ Versión bumpeada: $new_version"
echo "✓ Scripts sincronizados (sync-versions.cjs ejecutado)"
```

### 5. Actualizar CHANGELOG: [No Publicado] → [version] - date

```bash
echo "📝 Actualizando CHANGELOG.md..."

# Reemplazar [No Publicado] con [version] - date
sed -i.bak "s/^## \[No Publicado\]/## [$new_version] - $current_date/" CHANGELOG.md

# Verificar cambio
if ! grep -q "^## \[$new_version\] - $current_date" CHANGELOG.md; then
  echo "❌ Error: Falló actualización de CHANGELOG"
  mv CHANGELOG.md.bak CHANGELOG.md
  exit 1
fi

rm -f CHANGELOG.md.bak
echo "✓ CHANGELOG actualizado con versión $new_version"
```

### 6. Crear nueva sección [No Publicado] vacía

```bash
echo "📝 Creando nueva sección [No Publicado]..."

# Encontrar línea después del header inicial (---)
header_end=$(grep -n "^---$" CHANGELOG.md | head -1 | cut -d: -f1)
insert_line=$((header_end + 2))

# Insertar nueva sección [No Publicado]
sed -i.bak "${insert_line}i\\
## [No Publicado]\\
\\
- [Cambios futuros se documentan aquí]\\
\\
---\\
" CHANGELOG.md

# Verificar inserción
if ! grep -q "^## \[No Publicado\]" CHANGELOG.md; then
  echo "❌ Error: Falló creación de sección [No Publicado]"
  mv CHANGELOG.md.bak CHANGELOG.md
  exit 1
fi

rm -f CHANGELOG.md.bak
echo "✓ Nueva sección [No Publicado] creada"
```

### 7. Actualizar commit con CHANGELOG modificado

```bash
echo "📝 Actualizando commit de release con CHANGELOG..."

# Agregar CHANGELOG.md al commit que acaba de crear npm version
git add CHANGELOG.md

# Amend el commit de release
git commit --amend --no-edit || {
  echo "❌ Error: Falló actualización del commit"
  exit 1
}

echo "✓ Commit de release actualizado"
```

### 8. Verificar commit y tag creados

```bash
echo "🔍 Verificando commit y tag..."

# Verificar commit existe
last_commit=$(git log -1 --pretty=format:"%s")
if ! echo "$last_commit" | grep -q "release"; then
  echo "⚠️  Warning: Último commit no parece ser de release: $last_commit"
fi

# Verificar tag existe
if ! git tag | grep -q "^v$new_version$"; then
  echo "❌ Error: Tag v$new_version no encontrado"
  echo "💡 Ejecuta manualmente: git tag v$new_version"
  exit 1
fi

echo "✓ Commit de release: $last_commit"
echo "✓ Tag creado: v$new_version"
```

### 9. Preguntar si push con tags

```bash
echo ""
echo "✅ Release v$new_version completado exitosamente"
echo ""
echo "📦 Cambios listos para publicar:"
echo "  - Commit: $last_commit"
echo "  - Tag: v$new_version"
echo "  - CHANGELOG.md actualizado"
echo "  - package.json, README.md, docs sincronizados"
echo ""
read -p "¿Quieres hacer push ahora (incluye tags)? [y/N] " push_choice

if [[ "$push_choice" =~ ^[Yy]$ ]]; then
  current_branch=$(git branch --show-current)

  echo "🚀 Pushing a origin/$current_branch con tags..."

  git push origin "$current_branch" --follow-tags || {
    echo "❌ Error: Push falló"
    echo "💡 Ejecuta manualmente: git push origin $current_branch --follow-tags"
    exit 1
  }

  echo "✅ Push completado exitosamente"
  echo "🌐 Release v$new_version publicado"
else
  echo "✓ Release creado localmente"
  echo "💡 Para publicar más tarde: git push origin $(git branch --show-current) --follow-tags"
fi
```

## Notas

- **Pre-requisito**: CHANGELOG.md debe tener sección `[No Publicado]` con cambios
- **Auto-sync**: `npm version` ejecuta automáticamente `scripts/sync-versions.cjs` que sincroniza:
  - human-handbook/.vitepress/config.js
  - README.md
  - human-handbook/docs/changelog.md
- **Atomic**: Commit + tag creados automáticamente por npm version
- **Safe**: Validaciones previenen releases vacíos o incorrectos
- **Flexible**: Usuario decide cuándo hacer push (local vs remoto)
- **Workflow recomendado**:
  1. `/changelog` → actualiza CHANGELOG con PRs
  2. Revisar/editar CHANGELOG.md manualmente
  3. `/release` → bump version + sync + tag
