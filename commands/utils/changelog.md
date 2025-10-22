---
allowed-tools: Bash(git *, gh *), Read, Edit
description: Actualiza CHANGELOG.md con PRs clasificados según Keep a Changelog
---

# Changelog Update

Actualiza `[No Publicado]` con PRs mergeados, clasificados automáticamente por conventional type y mapeados a categorías [Keep a Changelog](https://keepachangelog.com/).

**Input**: Sin argumentos (detección automática desde último release)

## Paso 1: Validación Inicial

Ejecutar en bash:

1. Verificar herramientas:

   ```bash
   command -v gh >/dev/null 2>&1 || { echo "❌ gh CLI requerido"; exit 1; }
   ```

2. Verificar archivos:
   ```bash
   [ -f CHANGELOG.md ] || { echo "❌ CHANGELOG.md no encontrado"; exit 1; }
   grep -q "^## \[No Publicado\]" CHANGELOG.md || { echo "❌ Sección [No Publicado] no encontrada"; exit 1; }
   ```

**Bloqueadores**:

- gh CLI no instalado → error
- CHANGELOG.md no existe → error
- Sección `[No Publicado]` no existe → error

## Paso 2: Detectar Último Release

Obtener último release tag de git para saber desde dónde buscar PRs:

```bash
last_release=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -z "$last_release" ]; then
  last_release=$(git rev-list --max-parents=0 HEAD)
fi
git config --local changelog.temp.last-release "$last_release"
```

**Output esperado**: Tag del último release (ej: `v1.3.0`) o commit hash inicial

## Paso 3: Obtener PRs Mergeados

1. Listar commits desde último release hasta HEAD

2. Extraer números de PR de mensajes de commit:
   - Buscar patrones: `#123`, `(#123)`, `Merge pull request #123`
   - Extraer solo números
   - Eliminar duplicados y ordenar

3. Guardar lista de PRs en git config:
   ```bash
   git config --local changelog.temp.pr-list "$pr_list"
   git config --local changelog.temp.pr-count "$pr_count"
   ```

**Bloqueadores**:

- Cero PRs encontrados → informar usuario y salir exitosamente (CHANGELOG actualizado)

## Paso 4: Clasificar PRs por Tipo

**Estrategia**: Claude decide la mejor implementación usando herramientas disponibles (bash para gh CLI, Claude para procesamiento de texto).

Para cada PR encontrado en paso anterior:

1. **Obtener metadata del PR desde GitHub**:

   Ejecutar en bash:

   ```bash
   # Retry logic: 3 intentos con 2s delay
   for attempt in 1 2 3; do
     pr_data=$(gh pr view "$pr_num" --json title,body,state 2>&1) && break
     [ $attempt -lt 3 ] && sleep 2
   done

   # Skip si falló
   if echo "$pr_data" | grep -qE 'error|not found'; then
     echo "⚠️  PR #$pr_num: No encontrado, skip"
     continue
   fi
   ```

2. **Validar PR mergeado** (bash con jq):

   ```bash
   state=$(echo "$pr_data" | jq -r '.state')
   if [ "$state" != "MERGED" ]; then
     echo "⚠️  PR #$pr_num: No mergeado ($state), skip"
     continue
   fi
   ```

3. **Extraer conventional type** (bash con grep):

   ```bash
   title=$(echo "$pr_data" | jq -r '.title')

   # Portable bash 3.2
   if echo "$title" | grep -qE '^(feat|fix|docs|refactor|perf|style|security|chore|test|build|ci)[:(]'; then
     type=$(echo "$title" | grep -oE '^[a-z]+')
   else
     type="other"
   fi
   ```

4. **Construir descripción para CHANGELOG** (Claude procesa):

   **Responsabilidad de Claude**:
   - Extraer body del PR desde JSON: `jq -r '.body'`
   - **Si body no está vacío** (no es `null`, `""`, o solo whitespace):
     - Identificar primera sección relevante (contenido antes de `## Test`, `## Checklist`, etc.)
     - Preservar markdown: bold, italic, bullets, links
     - Remover headers de nivel 2+ manteniendo contenido (`## Título\nContenido` → `Contenido`)
     - Condensar a 1-3 líneas si es muy largo (preservar esencia)
   - **Si body está vacío**: Usar título sin prefijo/scope (`feat(auth): add login` → `add login`)

   **Criterio de "vacío"**: `body == null || body == "" || body.trim() == ""`

5. **Mapear conventional type → Keep a Changelog categoría**:

   | Conventional Type           | Keep a Changelog Categoría |
   | --------------------------- | -------------------------- |
   | `feat`                      | **### Añadido**            |
   | `fix`                       | **### Arreglado**          |
   | `refactor`, `perf`, `style` | **### Cambiado**           |
   | `security`                  | **### Seguridad**          |
   | `docs`                      | **### Documentación**      |
   | Otros                       | **### Cambiado** (default) |

6. **Agrupar PRs por categoría** (Claude estructura):

   Acumular entradas por categoría y guardar en git config:

   ```bash
   # Por cada PR procesado, agregar a categoría correspondiente
   git config --local "changelog.temp.cat-added" "$cat_added"
   git config --local "changelog.temp.cat-fixed" "$cat_fixed"
   git config --local "changelog.temp.cat-changed" "$cat_changed"
   git config --local "changelog.temp.cat-security" "$cat_security"
   git config --local "changelog.temp.cat-docs" "$cat_docs"
   ```

**Output esperado**: PRs agrupados por categoría con descripciones procesadas del body

## Paso 5: Generar Preview y Confirmar

1. Construir preview de cómo quedará `[No Publicado]` mostrando:

   ```
   ## [No Publicado]

   ### Añadido
   - Generación de documentación SDD en español (spec.md, plan.md, tasks.md) (PR #123)
   - Sincronización automática de develop al hacer push a main vía workflow CI (PR #124)

   ### Arreglado
   - **CRÍTICO**: Regresión en validación de --short-name (permite valor faltante) (PR #125)

   ### Cambiado
   - Directorio PRPs reubicado a raíz del repositorio (mejora organizacional) (PR #126)
   ```

2. Mostrar preview al usuario (stdout)

3. Confirmar cambios (stdout + user input):
   - Usuario confirma (y/yes) → continuar a paso 6
   - Usuario cancela (n/no/cualquier otro) → limpiar state y salir

**Bloqueadores**:

- Usuario cancela → limpiar state (`git config --unset-all changelog.temp`) y salir

## Paso 6: Actualizar CHANGELOG con Edit Tool

Si usuario confirmó:

1. Usar Read tool para leer CHANGELOG.md completo

2. Identificar sección exacta `[No Publicado]`:
   - Desde línea `## [No Publicado]`
   - Hasta próxima línea `## [` o `---`

3. Construir `old_string`: contenido exacto de sección actual incluyendo header

4. Construir `new_string`:
   - Mantener header `## [No Publicado]`
   - Insertar categorías con PRs clasificados (solo categorías con items)
   - **Formato**: `- {descripción del body del PR} (PR #{número})`
     - Descripción viene del body del PR (extraída en Paso 4)
     - Preserva formatting markdown (bold, italics, bullets si aplicable)
     - Si PR no tiene body, usa título limpiado
   - Orden estándar Keep a Changelog

5. Usar Edit tool con `old_string` y `new_string`

6. Verificar actualización exitosa con Read tool

**Output esperado**: CHANGELOG.md actualizado con PRs clasificados por categoría

## Paso 7: Limpiar State

Ejecutar en bash:

```bash
git config --local --unset-all changelog.temp
```

**Output final**: Mensaje de éxito indicando número de PRs agregados por categoría

## Seguridad

**Prevención de Command Injection**:

- Variables git quoted: `"$var"`
- Git commands con separator: `git cmd "ref" --`
- Sanitizar outputs de gh CLI (usar jq si es JSON)
- No eval de contenido de PRs

## Rollback

En cualquier error antes de Edit:

```bash
git config --local --unset-all changelog.temp 2>/dev/null
exit 1
```

## Notas de Implementación

- **Herramientas**: Read, Edit para Claude; bash para git/gh CLI
- **Bash 3.2 Compatible**: POSIX test `[ ]`, `grep -E`, no associative arrays
- **Detección desde release**: No desde último PR, sino último tag git
- **Clasificación inteligente**: Conventional type (feat, fix, docs) → Keep a Changelog categoría (Añadido, Arreglado, Documentación)
- **Body completo del PR**: Extrae descripción del body, no solo título
  - Claude procesa: preserva markdown (bold, bullets, italics)
  - Stop antes de secciones: Test plan, Checklist, References
  - Remueve headers `## ` manteniendo contenido
  - Fallback a título limpiado si body vacío (`null`, `""`, whitespace)
- **Error handling**: Retry logic (3 intentos) para gh CLI, skip PRs no encontrados
- **Confirmación obligatoria**: Preview antes de modificar
- **No commit automático**: Usuario decide cuándo commitear
- **Workflow**: `/changelog` → revisar → `/release`

## Anexo: Ejemplo End-to-End

### Input: PR #123 Real

**PR Metadata**:

```json
{
  "title": "feat(sdd): generación de specs en español",
  "state": "MERGED",
  "body": "## Summary\n\nImplementa generación automática de documentos SDD (spec.md, plan.md, tasks.md) en idioma español.\n\n- Spec template traducido al español\n- Plan template con secciones estándar\n- Tasks con formato dependency-ordered\n\n## Test Plan\n- [x] Templates generados correctamente\n- [x] Encoding UTF-8 verificado"
}
```

### Processing Pipeline

**Paso 1**: Conventional type extraction

```bash
# Input: "feat(sdd): generación de specs en español"
type=$(echo "$title" | grep -oE '^[a-z]+' | head -1)
# Output: "feat"
```

**Paso 2**: Map to Keep a Changelog category

```
feat → ### Añadido
```

**Paso 3**: Body processing (Claude)

```
Input body:
"## Summary\n\nImplementa generación automática de documentos SDD (spec.md, plan.md, tasks.md) en idioma español.\n\n- Spec template traducido al español\n- Plan template con secciones estándar\n- Tasks con formato dependency-ordered\n\n## Test Plan\n- [x] Templates generados correctamente\n- [x] Encoding UTF-8 verificado"

Claude extracts:
1. Stop at "## Test Plan" (metadata section)
2. Remove "## Summary" header, keep content
3. Preserve bullets and bold/italic

Output description:
"Implementa generación automática de documentos SDD (spec.md, plan.md, tasks.md) en idioma español.

- Spec template traducido al español
- Plan template con secciones estándar
- Tasks con formato dependency-ordered"
```

**Paso 4**: Format for CHANGELOG

```markdown
- Implementa generación automática de documentos SDD (spec.md, plan.md, tasks.md) en idioma español.
  - Spec template traducido al español
  - Plan template con secciones estándar
  - Tasks con formato dependency-ordered (PR #123)
```

### Output: CHANGELOG.md Updated

**Antes**:

```markdown
## [No Publicado]

_Sin cambios aún._
```

**Después**:

```markdown
## [No Publicado]

### Añadido

- Implementa generación automática de documentos SDD (spec.md, plan.md, tasks.md) en idioma español.
  - Spec template traducido al español
  - Plan template con secciones estándar
  - Tasks con formato dependency-ordered (PR #123)
```

### Casos Edge

**PR sin body** (body es `null` o `""`):

```json
{ "title": "fix(cli): argumento --help no funcionaba", "body": null }
```

**Resultado**: Usa título limpiado

```markdown
- argumento --help no funcionaba (PR #124)
```

**PR con body solo whitespace**:

```json
{ "title": "docs: actualizar README", "body": "   \n\n  " }
```

**Resultado**: Criterio vacío cumplido, usa título

```markdown
- actualizar README (PR #125)
```
