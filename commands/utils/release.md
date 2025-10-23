---
allowed-tools: Bash(git *, npm *, gh *), Read, Edit, AskUserQuestion
description: Analiza cambios, propone versión según semver, crea release en GitHub
---

# Release

Workflow inteligente de release con análisis semántico de cambios y confirmación del usuario.

**Input**: Sin argumentos (análisis automático de `[No Publicado]`)

## Paso 1: Validación Inicial

Ejecutar en bash:

1. Verificar herramientas requeridas:

   ```bash
   command -v npm >/dev/null 2>&1 || { echo "❌ npm requerido"; exit 1; }
   command -v gh >/dev/null 2>&1 || { echo "❌ gh CLI requerido"; exit 1; }
   ```

2. Verificar archivos:

   ```bash
   [[ -f CHANGELOG.md ]] || { echo "❌ CHANGELOG.md no encontrado"; exit 1; }
   [[ -f package.json ]] || { echo "❌ package.json no encontrado"; exit 1; }
   grep -q "^## \[No Publicado\]" CHANGELOG.md || { echo "❌ Sección [No Publicado] no encontrada"; exit 1; }
   ```

3. Verificar working tree limpio:

   ```bash
   [[ -z $(git status --porcelain) ]] || { echo "❌ Working tree no limpio"; exit 1; }
   ```

4. Guardar versión actual:
   ```bash
   current_version=$(node -p "require('./package.json').version")
   git config --local release.temp.current-version "$current_version"
   ```

**Bloqueadores**:

- Herramientas no instaladas → error
- Archivos no existen → error
- Working tree no limpio → error
- Sección `[No Publicado]` no existe → error

## Paso 2: Analizar Contenido de [No Publicado]

1. Usar Read tool para leer `CHANGELOG.md` completo

2. Identificar sección `[No Publicado]`:
   - Desde línea `## [No Publicado]`
   - Hasta próxima línea `## [versión]` o fin de archivo

3. Verificar que sección tiene contenido real (no solo placeholder "Cambios futuros")

4. Analizar categorías Keep a Changelog presentes:
   - `### Añadido` → indica nuevas features
   - `### Cambiado` → indica modificaciones
   - `### Arreglado` → indica bug fixes
   - `### Seguridad` → indica security fixes
   - Texto "BREAKING" en cualquier parte → indica breaking changes

5. Guardar análisis en git config:
   ```bash
   git config --local release.temp.has-breaking "true/false"
   git config --local release.temp.has-added "true/false"
   git config --local release.temp.has-changed "true/false"
   git config --local release.temp.has-fixed "true/false"
   ```

**Bloqueadores**:

- Sección vacía o solo placeholder → error (ejecutar `/changelog` primero)

## Paso 3: Calcular Versión Propuesta (Semver)

Basado en análisis del paso anterior, determinar tipo de bump según Semantic Versioning:

1. **Si `has-breaking = true`** → MAJOR bump
   - Ejemplo: 1.2.3 → 2.0.0

2. **Si `has-added = true`** (y no breaking) → MINOR bump
   - Ejemplo: 1.2.3 → 1.3.0

3. **Si solo `has-fixed = true` o `has-changed = true`** → PATCH bump
   - Ejemplo: 1.2.3 → 1.2.4

4. **Si ninguna categoría detectada** → error

Calcular nueva versión y guardar:

```bash
# Parsear versión actual: major.minor.patch
# Calcular nueva versión según regla de bump
# Ejemplo bash (Claude puede usar su propio método):
IFS='.' read -r major minor patch <<< "$current_version"
# Aplicar bump correspondiente...
git config --local release.temp.release-type "major/minor/patch"
git config --local release.temp.new-version "$new_version"
```

**Output esperado**: Tipo de release y nueva versión calculada

## Paso 4: Confirmar con Usuario (BLOQUEANTE)

1. Contar items de cambio por categoría en sección `[No Publicado]`:
   - Contar líneas que empiezan con `- ` bajo cada `###`

2. Construir resumen legible:
   - Versión actual vs propuesta
   - Tipo de bump (major/minor/patch)
   - Cantidad de cambios por categoría

3. **IMPORTANTE**: Usar AskUserQuestion tool y **ESPERAR** respuesta del usuario:
   - **Pregunta**: `"¿Crear y publicar release v{new_version} ({release_type})?"`
   - **Header**: `"Release"`
   - **Opciones**:
     - Label: "Sí, crear y publicar"
       Description: "Versión: {current} → {new} | Tipo: {type} | Cambios: {summary} | Incluye push a GitHub"
     - Label: "No, cancelar"
       Description: "Cancelar proceso de release completo"
   - **multiSelect**: false

4. **WAIT para respuesta del usuario** (NO continuar automáticamente)

5. Si usuario selecciona "No, cancelar":
   ```bash
   git config --local --remove-section release.temp 2>/dev/null
   echo "❌ Release cancelado por el usuario"
   exit 0
   ```

**Bloqueadores**:

- Usuario selecciona "No" → limpiar state y salir (exit 0, no error)

## Paso 5: Actualizar CHANGELOG.md

**IMPORTANTE**: Este paso debe ejecutarse ANTES de npm version (sync-versions.cjs valida que versión exista en CHANGELOG)

Si usuario confirmó "Sí, crear y publicar":

1. Usar Read tool para obtener contenido completo de CHANGELOG.md

2. Identificar sección exacta `[No Publicado]`:
   - Desde línea `## [No Publicado]`
   - Hasta línea siguiente que empieza con `## [` o `---`

3. Construir `old_string`: contenido exacto de sección incluyendo header

4. Construir `new_string`:
   - Reemplazar header `## [No Publicado]` con `## [{new_version}] - {YYYY-MM-DD}`
   - Mantener todo el contenido de la sección

5. Usar Edit tool con `old_string` y `new_string`

6. Insertar nueva sección vacía `[No Publicado]` al inicio:
   - Ubicar línea después del primer `---` (después del header CHANGELOG)
   - Usar Edit tool para insertar:

     ```
     ## [No Publicado]

     - [Cambios futuros se documentan aquí]

     ---
     ```

7. Verificar cambios con Read tool

**Output esperado**: CHANGELOG.md actualizado con versión y nueva sección vacía

## Paso 6: Bump Versión y Sincronizar

Ejecutar en bash:

```bash
new_version=$(git config --local release.temp.new-version)

# npm version crea commit + tag automáticamente
npm version "$new_version" -m "chore: release v%s" || {
  echo "❌ npm version falló"
  git config --local --remove-section release.temp 2>/dev/null
  exit 1
}

# Verificar que commit y tag se crearon
git tag | grep -q "^v$new_version$" || {
  echo "❌ Tag no creado"
  exit 1
}

echo "✅ Versión bumpeada: $new_version"
echo "✅ Commit y tag creados"
```

**Output esperado**:

- package.json → 1.5.0
- sync-versions.cjs ejecutado (config.js, README.md, docs/changelog.md sincronizados)
- commit creado: "chore: release v1.5.0"
- tag creado: v1.5.0

## Paso 7: Push y Crear GitHub Release

Ejecutar en bash:

```bash
new_version=$(git config --local release.temp.new-version)
current_branch=$(git branch --show-current)

# Push commit + tag
git push origin "$current_branch" --follow-tags || {
  echo "❌ Push falló"
  exit 1
}

echo "✅ Push completado: commit + tag v$new_version"
```

## Paso 8: Extraer Release Notes y Crear GitHub Release

1. Usar Read tool para leer CHANGELOG.md actualizado

2. Identificar sección de la nueva versión:
   - Desde línea `## [{new_version}] - {date}`
   - Hasta próxima línea `## [` o `---`

3. Extraer contenido (sin el header de versión):
   - Solo el contenido entre headers
   - Remover líneas `---` si existen

4. Crear archivo temporal con release notes:

   ```bash
   echo "$release_notes" > /tmp/release_notes_${new_version}.md
   ```

5. Crear GitHub Release:

   ```bash
   gh release create "v$new_version" \
     --title "v$new_version" \
     --notes-file "/tmp/release_notes_${new_version}.md" || {
     echo "❌ GitHub Release falló"
     rm -f "/tmp/release_notes_${new_version}.md"
     exit 1
   }
   ```

6. Obtener URL y limpiar:
   ```bash
   release_url=$(gh release view "v$new_version" --json url -q .url)
   rm -f "/tmp/release_notes_${new_version}.md"
   echo "✅ GitHub Release creado: $release_url"
   ```

## Paso 9: Limpiar State

Ejecutar en bash:

```bash
git config --local --remove-section release.temp 2>/dev/null
```

**Output final**: `✅ Release v{new_version} completado y publicado: {release_url}`

## Seguridad

**Prevención de Command Injection**:

- Todas las variables git quoted: `"$var"`
- No eval de contenido de CHANGELOG
- gh CLI con archivos temporales (no stdin con contenido no sanitizado)
- Validar formato de versión antes de crear tag

## Rollback

En caso de error **después de Paso 5 (CHANGELOG actualizado) pero antes de Paso 6 (npm version)**:

```bash
# Restaurar CHANGELOG.md
git checkout HEAD -- CHANGELOG.md

# Limpiar state
git config --local --remove-section release.temp 2>/dev/null

exit 1
```

En caso de error **después de Paso 6 (npm version) pero antes de Paso 7 (push)**:

```bash
# Revertir commit y tag creados por npm version
git tag -d "v$new_version" 2>/dev/null
git reset --hard HEAD~1

# Limpiar state
git config --local --remove-section release.temp 2>/dev/null
rm -f /tmp/release_notes_*.md 2>/dev/null

exit 1
```

En caso de error **después de Paso 7 (push) pero antes de Paso 8 (GitHub Release)**:

```bash
# El commit y tag ya están en GitHub, crear release manualmente
gh release create "v$new_version" --generate-notes

# Limpiar state
git config --local --remove-section release.temp 2>/dev/null
```

## Notas de Implementación

- **Instrucciones declarativas**: Claude decide cómo implementar análisis y cálculos
- **Herramientas de Claude**: Read, Edit, AskUserQuestion (no bash complejos)
- **Bash mínimo**: Solo validaciones simples y comandos directos (git, npm, gh)
- **Análisis semántico**: Claude interpreta Keep a Changelog → calcula semver
- **Confirmación ÚNICA**: Usuario confirma TODO de una vez (versión + publicación)
- **Orden correcto**: CHANGELOG primero → npm version (para que sync-versions.cjs valide)
- **npm version automático**: Crea commit + tag (NO usar --no-git-tag-version)
- **State temporal**: git config para pasar datos entre pasos
- **Workflow recomendado**:
  1. `/changelog` → actualiza [No Publicado] con PRs clasificados
  2. Revisar/editar CHANGELOG.md manualmente si necesario
  3. `/release` → análisis automático → confirmación → publicación
