---
allowed-tools: Bash(git *, gh *), Read, Edit
description: Actualiza CHANGELOG.md con PRs clasificados según Keep a Changelog
---

# Changelog Update

Actualiza `[No Publicado]` con PRs mergeados, clasificados por tipo según [Keep a Changelog](https://keepachangelog.com/).

**Input**: Sin argumentos (detección automática desde último release)

## Paso 1: Validación Inicial

Ejecutar en bash:

1. Verificar herramientas:

   ```bash
   command -v gh >/dev/null 2>&1 || {
     echo "❌ Error: gh CLI requerido"
     echo "💡 Instalar: https://cli.github.com/"
     exit 1
   }
   ```

2. Verificar CHANGELOG.md existe en raíz del proyecto

3. Verificar sección `[No Publicado]` existe:
   ```bash
   grep -q "^## \[No Publicado\]" CHANGELOG.md
   ```

**Bloqueadores**:

- gh CLI no instalado → error
- CHANGELOG.md no existe → error
- Sección `[No Publicado]` no existe → error

## Paso 2: Detectar Último Release

Ejecutar en bash:

1. Obtener último release tag de git:

   ```bash
   last_release=$(git describe --tags --abbrev=0 2>/dev/null)
   ```

2. Si no hay releases previos, usar primer commit:

   ```bash
   [[ -z "$last_release" ]] && last_release=$(git rev-list --max-parents=0 HEAD)
   ```

3. Guardar en git config:
   ```bash
   git config --local changelog.temp.last-release "$last_release"
   ```

**Output esperado**: Tag del último release (ej: `v1.1.2`) o commit hash inicial

## Paso 3: Obtener PRs Mergeados

Ejecutar en bash:

1. Listar commits desde último release:

   ```bash
   git log "$last_release..HEAD" --pretty=format:"%s" --
   ```

2. Extraer números de PR de commits:

   ```bash
   pr_list=$(git log "$last_release..HEAD" --pretty=format:"%s" -- | \
     grep -oE '(#[0-9]+|Merge pull request #[0-9]+|\(#[0-9]+\))' | \
     grep -oE '[0-9]+' | sort -n -u)
   ```

3. Contar PRs encontrados:

   ```bash
   pr_count=$(echo "$pr_list" | wc -w | xargs)
   ```

4. Guardar lista en git config:
   ```bash
   git config --local changelog.temp.pr-list "$pr_list"
   git config --local changelog.temp.pr-count "$pr_count"
   ```

**Bloqueadores**:

- Cero PRs encontrados → informar al usuario y salir con éxito (CHANGELOG ya actualizado)

## Paso 4: Clasificar PRs por Tipo

Para cada PR en `$pr_list`, ejecutar en bash:

1. Obtener metadata del PR desde GitHub:

   ```bash
   pr_data=$(gh pr view "$pr" --json state,title,labels 2>/dev/null)
   ```

2. Verificar estado es MERGED:

   ```bash
   state=$(echo "$pr_data" | jq -r '.state')
   [[ "$state" == "MERGED" ]] || continue
   ```

3. Obtener título y clasificar por tipo convencional:

   ```bash
   title=$(echo "$pr_data" | jq -r '.title')

   # Extraer tipo: feat, fix, docs, etc
   type=$(echo "$title" | grep -oE '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|security)' | head -1)

   # Limpiar título (remover tipo convencional)
   clean_title=$(echo "$title" | sed -E 's/^(feat|fix|refactor|docs|style|test|chore|security|perf|ci|build|revert)(\([^)]+\))?!?:\s*//')
   ```

4. Mapear tipo → categoría Keep a Changelog:
   - `feat` → Añadido
   - `fix` → Arreglado
   - `refactor`, `perf`, `style` → Cambiado
   - `security` → Seguridad
   - `docs` → Documentación
   - Otros → Cambiado (default)

5. Agrupar por categoría:
   ```bash
   # Ejemplo: guardar en arrays asociativos o archivos temporales
   echo "- $clean_title (PR #$pr)" >> /tmp/changelog_added.txt  # para feat
   echo "- $clean_title (PR #$pr)" >> /tmp/changelog_fixed.txt  # para fix
   # etc...
   ```

**Output esperado**: PRs agrupados por categoría Keep a Changelog

## Paso 5: Generar Preview y Confirmar

Usando los archivos temporales del paso anterior:

1. Construir preview del CHANGELOG actualizado mostrando:

   ```
   ## [No Publicado]

   ### Añadido
   - Feature 1 (PR #123)
   - Feature 2 (PR #124)

   ### Arreglado
   - Bug fix 1 (PR #125)

   ### Cambiado
   - Refactor 1 (PR #126)
   ```

2. Mostrar preview al usuario

3. Preguntar al usuario: `"¿Actualizar CHANGELOG.md con estos cambios? [y/N]"`

**Bloqueadores**:

- Usuario responde "N" → limpiar state y salir

## Paso 6: Actualizar CHANGELOG con Edit Tool

Si usuario confirmó:

1. Usar Read tool para leer CHANGELOG.md completo

2. Identificar ubicación de `## [No Publicado]`

3. Usar Edit tool para reemplazar sección `[No Publicado]` con contenido clasificado:

   ```
   old_string: toda la sección [No Publicado] actual
   new_string: sección actualizada con PRs clasificados por categoría
   ```

4. Verificar actualización exitosa con Read tool

**Output esperado**: CHANGELOG.md actualizado con PRs clasificados

## Paso 7: Limpiar State

Ejecutar en bash:

```bash
git config --local --unset-all changelog.temp
rm -f /tmp/changelog_*.txt
```

**Output final**: Mensaje de éxito con número de PRs agregados

## Seguridad

**Prevención de Command Injection**:

- Todas las variables git quoted: `"$var"`
- Git commands con separator: `git cmd "ref" --`
- Sanitizar outputs de gh CLI con jq
- No eval de contenido de PRs

## Rollback

En cualquier error antes de Edit:

```bash
git config --local --unset-all changelog.temp 2>/dev/null
rm -f /tmp/changelog_*.txt 2>/dev/null
exit 1
```

## Notas de Implementación

- **Detección desde release**: No desde último PR, sino último tag release
- **Clasificación inteligente**: Tipo convencional → categoría Keep a Changelog
- **Confirmación obligatoria**: Usuario aprueba preview antes de modificar
- **Edit tool**: Usar Edit tool de Claude (no sed/awk)
- **State temporal**: git config para pasar datos entre pasos
- **No commit automático**: Usuario decide cuándo commitear
