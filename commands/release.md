---
name: release
allowed-tools: Bash(git *, npm *, gh *), Read, Edit, AskUserQuestion
description: Analiza cambios, propone versión según semver, crea release en GitHub
---

# Release

Workflow de release con análisis semántico de CHANGELOG y confirmación del usuario.

## Paso 1: Validación

Ejecutar en bash:

```bash
# Validar herramientas
command -v npm >/dev/null 2>&1 || { echo "❌ npm requerido"; exit 1; }
command -v gh >/dev/null 2>&1 || { echo "❌ gh CLI requerido"; exit 1; }

# Validar archivos
test -f CHANGELOG.md || { echo "❌ CHANGELOG.md faltante"; exit 1; }
test -f package.json || { echo "❌ package.json faltante"; exit 1; }
grep -q "^## \[No Publicado\]" CHANGELOG.md || { echo "❌ [No Publicado] no encontrado"; exit 1; }

# Validar working tree (solo CHANGELOG.md modificado)
# CORREGIDO: Compatible con zsh, usa archivos temporales para evitar parse errors
git status --porcelain > /tmp/release_status.txt
grep -v "^ M CHANGELOG.md" /tmp/release_status.txt | grep -v "^??" > /tmp/release_other.txt
if test -s /tmp/release_other.txt; then
  echo "❌ Working tree tiene cambios además de CHANGELOG.md"
  rm -f /tmp/release_status.txt /tmp/release_other.txt
  exit 1
fi
rm -f /tmp/release_status.txt /tmp/release_other.txt
echo "✅ Working tree limpio"

# Guardar versión actual
current_version=$(node -p "require('./package.json').version")
git config --local release.temp.current-version "$current_version"
```

## Paso 2: Analizar y Calcular Versión

1. Usar Read tool para leer CHANGELOG.md

2. Analizar sección `[No Publicado]`:
   - Buscar `### Añadido` → has_added
   - Buscar `### Cambiado` → has_changed
   - Buscar `### Arreglado` → has_fixed
   - Buscar texto "BREAKING" → has_breaking

3. Calcular versión según semver:
   - `has_breaking = true` → MAJOR (2.0.0 → 3.0.0)
   - `has_added = true` → MINOR (2.0.0 → 2.1.0)
   - Solo `has_fixed` o `has_changed` → PATCH (2.0.0 → 2.0.1)

4. Guardar resultado:
   ```bash
   git config --local release.temp.release-type "major/minor/patch"
   git config --local release.temp.new-version "$new_version"
   ```

## Paso 3: Confirmar con Usuario

**IMPORTANTE**: Usar AskUserQuestion tool y **WAIT para respuesta**:

- **Pregunta**: `"¿Crear y publicar release v{new_version} ({release_type})?"`
- **Header**: `"Release"`
- **Opciones**:
  - "Sí, crear y publicar" - Versión: {current} → {new} | Cambios: {count_added} añadidos, {count_changed} cambios, {count_fixed} fixes
  - "No, cancelar" - Cancelar proceso completo

Si usuario cancela:

```bash
git config --local --remove-section release.temp 2>/dev/null
exit 0
```

## Paso 4: Actualizar CHANGELOG

**CRÍTICO**: Debe ejecutarse ANTES de npm version (sync-versions.cjs valida versión en CHANGELOG)

1. Usar Read tool para CHANGELOG.md completo

2. Identificar y reemplazar sección `[No Publicado]`:
   - `old_string`: Desde `## [No Publicado]` hasta `---`
   - `new_string`: `## [{new_version}] - {YYYY-MM-DD}` + contenido

3. Usar Edit tool para reemplazar

4. Insertar nueva sección vacía al inicio:

   ```markdown
   ## [No Publicado]

   - [Cambios futuros se documentan aquí]

   ---
   ```

5. **NUEVO: Actualizar footer "Última Actualización"**:
   - Localizar línea con `**Fecha**: ... | **Versión**: ... | **Formato**: Keep a Changelog`
   - `old_string`: Línea completa con versión antigua
   - `new_string`: `**Fecha**: {YYYY-MM-DD} | **Versión**: {new_version} | **Formato**: Keep a Changelog`
   - Usar Edit tool para reemplazar

## Paso 5: Bump Versión

Ejecutar en bash:

```bash
new_version=$(git config --local release.temp.new-version)

# Commit CHANGELOG primero (npm version requiere working tree limpio)
git add CHANGELOG.md
git commit -m "docs: prepare CHANGELOG for v$new_version"

# npm version: bumps package.json + sync + commit + tag
npm version "$new_version" -m "chore: release v%s" || {
  echo "❌ npm version falló"
  git config --local --remove-section release.temp 2>/dev/null
  exit 1
}
```

## Paso 6: Push y GitHub Release

Ejecutar en bash:

```bash
new_version=$(git config --local release.temp.new-version)
current_branch=$(git branch --show-current)

# Push commit + tag
git push origin "$current_branch" --follow-tags || {
  echo "❌ Push falló"
  git config --local --remove-section release.temp 2>/dev/null
  exit 1
}
```

Crear GitHub Release:

1. Usar Read tool para leer CHANGELOG.md actualizado

2. Extraer sección `## [{new_version}]` (desde header hasta próximo `## [` o `---`)

3. Crear archivo temporal con contenido:

   ```bash
   echo "$release_notes" > /tmp/release_notes_${new_version}.md
   ```

4. Crear release en GitHub:

   ```bash
   gh release create "v$new_version" \
     --title "v$new_version" \
     --notes-file "/tmp/release_notes_${new_version}.md"

   release_url=$(gh release view "v$new_version" --json url -q .url)
   rm -f "/tmp/release_notes_${new_version}.md"

   echo "✅ Release creado: $release_url"
   ```

## Paso 7: Cleanup

Ejecutar en bash:

```bash
git config --local --remove-section release.temp 2>/dev/null
echo "✅ Release v${new_version} publicado"
```

**Output**: Release v{new_version} publicado en {release_url}
