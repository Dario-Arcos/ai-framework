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
   command -v gh >/dev/null 2>&1 || { echo "❌ gh CLI requerido"; exit 1; }
   ```

2. Verificar archivos:
   ```bash
   [[ -f CHANGELOG.md ]] || { echo "❌ CHANGELOG.md no encontrado"; exit 1; }
   grep -q "^## \[No Publicado\]" CHANGELOG.md || { echo "❌ Sección [No Publicado] no encontrada"; exit 1; }
   ```

**Bloqueadores**:

- gh CLI no instalado → error
- CHANGELOG.md no existe → error
- Sección `[No Publicado]` no existe → error

## Paso 2: Detectar Último Release

Obtener último release tag de git para saber desde dónde buscar PRs:

```bash
last_release=$(git describe --tags --abbrev=0 2>/dev/null)
[[ -z "$last_release" ]] && last_release=$(git rev-list --max-parents=0 HEAD)
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

Para cada PR encontrado en paso anterior:

1. Obtener metadata del PR desde GitHub usando `gh pr view <número>`:
   - Estado (MERGED requerido): `gh pr view <número> --json state`
   - Título del PR: `gh pr view <número> --json title`
   - **Body del PR** (descripción completa): `gh pr view <número> --json body`

   **Nota técnica**: Usar formato JSON para parsing confiable, ej:

   ```bash
   gh pr view <número> --json title,body,state
   ```

2. Verificar que PR está mergeado (skip si no lo está)

3. Extraer tipo convencional del título:
   - Buscar prefijo: `feat:`, `fix:`, `docs:`, `refactor:`, etc.

4. **Construir descripción para CHANGELOG**:
   - **Si body existe y no está vacío**: Usar body del PR
     - Extraer primera sección relevante (detener antes de estas secciones comunes):
       - `## Test plan` / `## Testing`
       - `## Checklist` / `## TODO`
       - `## Related Issues` / `## References`
     - Preservar bullet points y formatting del body
     - Limpiar headers markdown de nivel 2+ (`## Título` → `Título`)
     - Mantener énfasis (**bold**, _italic_) y estructura de bullets
   - **Si body está vacío**: Usar título limpiado (sin prefijo/scope)
   - **Formato final**: Descripción completa del body sin headers de sección de metadata

5. Mapear tipo → categoría Keep a Changelog:
   - `feat` → **### Añadido**
   - `fix` → **### Arreglado**
   - `refactor`, `perf`, `style` → **### Cambiado**
   - `security` → **### Seguridad**
   - `docs` → **### Documentación**
   - Otros → **### Cambiado** (default)

6. Agrupar PRs por categoría para construir estructura del CHANGELOG

**Output esperado**: PRs agrupados por categoría con descripciones completas del body

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

   **Nota**: Las descripciones provienen del body completo del PR, no solo del título

2. Mostrar preview al usuario

3. Preguntar al usuario si desea aplicar los cambios:
   - Si confirma → continuar a paso 6
   - Si cancela → limpiar state y salir

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
   - Insertar categorías con PRs clasificados (solo categorías que tienen items)
   - **Formato de entrada**: `- {descripción del body del PR} (PR #{número})`
     - Descripción viene del body del PR (extraída en Paso 4)
     - Preserva formatting markdown (bold, italics, bullet points si aplicable)
     - Si PR no tiene body, usa título limpiado
   - Mantener orden: Añadido → Cambiado → Arreglado → Seguridad → Documentación

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

- **Instrucciones declarativas**: Claude decide cómo implementar extracción y clasificación
- **Herramientas de Claude**: Read, Edit (no sed/awk)
- **Bash mínimo**: Solo validaciones simples y git config
- **Detección desde release**: No desde último PR, sino último tag
- **Clasificación inteligente**: Tipo convencional → Keep a Changelog
- **Body completo del PR**: Extrae descripción completa del PR (body), no solo título
  - Preserva formatting markdown (bold, bullet points, italics)
  - Extrae sección relevante (ignora metadata: Test plan, Checklist, References)
  - Limpia headers markdown de nivel 2+ manteniendo contenido
  - Fallback a título si body vacío
- **Confirmación obligatoria**: Preview antes de modificar
- **No commit automático**: Usuario decide cuándo commitear
- **Workflow**: `/changelog` → revisar → `/release`
