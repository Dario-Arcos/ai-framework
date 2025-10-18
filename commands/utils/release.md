---
allowed-tools: Bash(git *, npm version *, gh release *), Read, Edit, AskUserQuestion
description: Analiza cambios, propone versión según semver, crea release en GitHub
---

# Release

Workflow inteligente de release con análisis semántico de cambios y confirmación del usuario.

**Input**: Sin argumentos (análisis automático de `[No Publicado]`)

## Paso 1: Validación Inicial

Ejecutar en bash:

1. Verificar herramientas requeridas:

   ```bash
   command -v npm >/dev/null 2>&1 || {
     echo "❌ Error: npm requerido"
     exit 1
   }
   command -v gh >/dev/null 2>&1 || {
     echo "❌ Error: gh CLI requerido"
     exit 1
   }
   ```

2. Verificar archivos existen:
   - `CHANGELOG.md` en raíz
   - `package.json` en raíz
   - Sección `[No Publicado]` en CHANGELOG.md

3. Obtener versión actual:
   ```bash
   current_version=$(node -p "require('./package.json').version")
   git config --local release.temp.current-version "$current_version"
   ```

**Bloqueadores**:

- npm o gh no instalados → error
- CHANGELOG.md no existe → error
- package.json sin campo `version` → error
- Sección `[No Publicado]` no existe → error

## Paso 2: Analizar Contenido de [No Publicado]

Usar Read tool para leer CHANGELOG.md completo.

Ejecutar en bash para extraer sección `[No Publicado]`:

```bash
# Encontrar líneas de inicio y fin de [No Publicado]
start=$(grep -n "^## \[No Publicado\]" CHANGELOG.md | cut -d: -f1)
end=$(tail -n +$((start + 1)) CHANGELOG.md | grep -n "^## \[" | head -1 | cut -d: -f1)

# Extraer contenido
if [[ -n "$end" ]]; then
  section_end=$((start + end - 1))
else
  section_end=$(wc -l < CHANGELOG.md)
fi

unreleased=$(sed -n "${start},${section_end}p" CHANGELOG.md)
```

Analizar contenido según Keep a Changelog:

```bash
# Buscar indicadores de tipo de cambio
has_breaking=false
has_added=false
has_changed=false
has_fixed=false

# BREAKING CHANGE en cualquier parte
echo "$unreleased" | grep -iq "BREAKING" && has_breaking=true

# Categorías Keep a Changelog
echo "$unreleased" | grep -q "^### Añadido" && has_added=true
echo "$unreleased" | grep -q "^### Cambiado" && has_changed=true
echo "$unreleased" | grep -q "^### Arreglado" && has_fixed=true

# Guardar análisis
git config --local release.temp.has-breaking "$has_breaking"
git config --local release.temp.has-added "$has_added"
git config --local release.temp.has-changed "$has_changed"
git config --local release.temp.has-fixed "$has_fixed"
```

**Bloqueadores**:

- Sección `[No Publicado]` vacía o solo tiene placeholder → error (ejecutar `/changelog` primero)

## Paso 3: Calcular Versión Propuesta (Semver)

Ejecutar en bash:

```bash
# Obtener versión actual
IFS='.' read -r major minor patch <<< "$current_version"

# Determinar tipo de bump según Keep a Changelog + Semver
if [ "$has_breaking" = "true" ]; then
  # BREAKING CHANGE → MAJOR
  release_type="major"
  new_version="$((major + 1)).0.0"
elif [ "$has_added" = "true" ]; then
  # Nueva funcionalidad → MINOR
  release_type="minor"
  new_version="${major}.$((minor + 1)).0"
elif [ "$has_fixed" = "true" ] || [ "$has_changed" = "true" ]; then
  # Solo fixes o cambios → PATCH
  release_type="patch"
  new_version="${major}.${minor}.$((patch + 1))"
else
  echo "❌ Error: No se detectaron cambios clasificables"
  exit 1
fi

# Guardar propuesta
git config --local release.temp.release-type "$release_type"
git config --local release.temp.new-version "$new_version"
```

**Output esperado**: Tipo de release (major/minor/patch) y nueva versión calculada

## Paso 4: Confirmar con Usuario

Construir resumen de cambios:

```bash
# Contar items por categoría
added_count=$(echo "$unreleased" | grep -c "^- " | grep -A 100 "### Añadido" || echo 0)
fixed_count=$(echo "$unreleased" | grep -c "^- " | grep -A 100 "### Arreglado" || echo 0)
changed_count=$(echo "$unreleased" | grep -c "^- " | grep -A 100 "### Cambiado" || echo 0)
```

Usar AskUserQuestion tool:

```
question: "Release v{new_version} ({release_type})"
header: "Confirmar"
options:
  - label: "Sí, crear release"
    description: "Versión: {current_version} → {new_version} | Tipo: {release_type} | Cambios: {added_count} añadidos, {fixed_count} arreglados, {changed_count} modificados"
  - label: "No, cancelar"
    description: "Cancelar proceso de release"
multiSelect: false
```

**Bloqueadores**:

- Usuario selecciona "No" → limpiar state y salir

## Paso 5: Actualizar CHANGELOG.md

Si usuario confirmó, usar Edit tool:

1. Leer CHANGELOG.md con Read tool

2. Reemplazar `## [No Publicado]` con `## [{new_version}] - {current_date}`:

   ```
   old_string: "## [No Publicado]"
   new_string: "## [{new_version}] - {YYYY-MM-DD}"
   ```

3. Insertar nueva sección vacía `[No Publicado]` al inicio (después del header):

   ```
   old_string: (línea después de "---")
   new_string:
   ## [No Publicado]

   - [Cambios futuros se documentan aquí]

   ---
   ```

4. Verificar cambios con Read tool

**Output esperado**: CHANGELOG.md actualizado con nueva versión y sección vacía

## Paso 6: Ejecutar npm version

Ejecutar en bash:

```bash
# npm version ejecuta automáticamente:
# 1. Bump package.json
# 2. scripts/sync-versions.cjs (sync config.js, README.md, docs)
# 3. git commit "chore: release v{version}" (si no hay cambios staged)
# 4. git tag v{version}

npm version "$new_version" --no-git-tag-version

# Verificar bump exitoso
bumped_version=$(node -p "require('./package.json').version")
if [ "$bumped_version" != "$new_version" ]; then
  echo "❌ Error: Bump de versión falló"
  exit 1
fi

echo "✓ package.json → v$new_version"
```

Ejecutar sync-versions.cjs manualmente:

```bash
node scripts/sync-versions.cjs
```

Crear commit y tag:

```bash
git add -A
git commit -m "chore: release v$new_version"
git tag "v$new_version"

echo "✓ Commit y tag v$new_version creados"
```

**Output esperado**: Versión sincronizada, commit y tag creados

## Paso 7: Confirmar Push + GitHub Release

Usar AskUserQuestion tool:

```
question: "¿Push a remoto y crear GitHub Release v{new_version}?"
header: "Publicar"
options:
  - label: "Sí, publicar ahora"
    description: "Push commit + tag + crear GitHub Release público"
  - label: "No, solo local"
    description: "Mantener release local (puedes publicar después con git push --follow-tags)"
multiSelect: false
```

**Bloqueadores**:

- Usuario selecciona "No" → informar comandos manuales y salir exitosamente

## Paso 8: Push y Crear GitHub Release

Si usuario confirmó publicación:

### 8.1 Push con Tags

Ejecutar en bash:

```bash
current_branch=$(git branch --show-current)

# Push commit + tags
git push origin "$current_branch" --follow-tags || {
  echo "❌ Error: Push falló"
  exit 1
}

echo "✓ Push a origin/$current_branch con tags completado"
```

### 8.2 Generar Release Notes desde CHANGELOG

Ejecutar en bash:

```bash
# Extraer sección de la nueva versión desde CHANGELOG
version_start=$(grep -n "^## \[$new_version\]" CHANGELOG.md | cut -d: -f1)
version_end=$(tail -n +$((version_start + 1)) CHANGELOG.md | grep -n "^## \[" | head -1 | cut -d: -f1)

if [[ -n "$version_end" ]]; then
  section_end=$((version_start + version_end - 1))
else
  section_end=$(wc -l < CHANGELOG.md)
fi

# Extraer contenido (sin el header de versión)
release_notes=$(sed -n "$((version_start + 2)),${section_end}p" CHANGELOG.md)

# Guardar en archivo temporal
echo "$release_notes" > /tmp/release_notes_$new_version.md
```

### 8.3 Crear GitHub Release

Ejecutar en bash:

```bash
# Crear release con gh CLI
gh release create "v$new_version" \
  --title "v$new_version" \
  --notes-file "/tmp/release_notes_$new_version.md" || {
  echo "❌ Error: Creación de GitHub Release falló"
  exit 1
}

# Limpiar temporal
rm -f "/tmp/release_notes_$new_version.md"

echo "✓ GitHub Release v$new_version creado"
echo "🌐 URL: https://github.com/{owner}/{repo}/releases/tag/v$new_version"
```

**Output esperado**: Release publicado en GitHub con notas desde CHANGELOG

## Paso 9: Limpiar State

Ejecutar en bash:

```bash
git config --local --unset-all release.temp
```

**Output final**: Release v{new_version} completado y publicado exitosamente

## Seguridad

**Prevención de Inyección**:

- Variables git quoted: `"$var"`
- No eval de contenido CHANGELOG
- Validar formato de versión antes de tag
- gh CLI con archivos temporales (no heredocs con contenido no sanitizado)

## Rollback

Si falla antes de push:

```bash
# Revertir commit y tag
git tag -d "v$new_version" 2>/dev/null
git reset --hard HEAD~1 2>/dev/null

# Restaurar CHANGELOG desde git
git checkout -- CHANGELOG.md

# Restaurar package.json
npm version "$current_version" --no-git-tag-version

# Limpiar state
git config --local --unset-all release.temp
rm -f /tmp/release_notes_*.md

exit 1
```

Si falla después de push pero antes de GitHub Release:

```bash
# Crear release manualmente:
gh release create "v$new_version" --title "v$new_version" --notes "Ver CHANGELOG.md"
```

## Notas de Implementación

- **Análisis semántico**: Interpreta Keep a Changelog → calcula semver correcto
- **Doble confirmación**: Usuario aprueba versión propuesta y publicación
- **Edit tool obligatorio**: No sed/awk para modificar CHANGELOG
- **AskUserQuestion**: Confirmaciones interactivas con opciones claras
- **Atomic operations**: Commit + tag juntos, rollback completo si falla
- **GitHub Release desde CHANGELOG**: Extrae notas automáticamente
- **State management**: git config para datos entre pasos
- **Workflow recomendado**:
  1. `/changelog` → actualiza [No Publicado]
  2. Revisar/editar CHANGELOG.md manualmente si necesario
  3. `/release` → análisis → confirmación → publicación
