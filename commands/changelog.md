---
name: changelog
allowed-tools: Bash(git *, gh *), Read, Edit
description: Actualiza CHANGELOG.md con análisis Truth-Based del diff real entre versiones
argument-hint: "desde última versión" | "desde v1.2.0" | "todos los cambios"
---

# Truth-Based Changelog

Actualiza `[No Publicado]` en CHANGELOG.md basándose en el **diff real** entre versiones, no en la narrativa de commits.

**Principio fundamental**: Los commits cuentan una historia. El diff cuenta la verdad.

**Input**: `$ARGUMENTS` - Rango a analizar (ej: "desde v4.2.0", "últimos cambios")

## Ejemplos de Uso

```bash
/changelog "desde última versión"
/changelog "desde v2.0.0"
/changelog "todos los cambios"
```

## Por Qué Truth-Based

```
Commits:                          Realidad (diff):
─────────────────────────────     ─────────────────────────────
1. feat: add caching              Solo existe: logging.py
2. fix: caching bug
3. revert: remove caching         El caching NO EXISTE.
4. feat: add logging              Documentarlo sería MENTIR.
```

El changelog documenta **qué existe**, no qué se intentó.

---

## Categorías Keep a Changelog

| Orden | Categoría | Descripción |
|-------|-----------|-------------|
| 1 | **Añadido** | Funcionalidades nuevas |
| 2 | **Cambiado** | Cambios en funcionalidad existente |
| 3 | **Obsoleto** | Marcado para eliminación futura |
| 4 | **Eliminado** | Funcionalidades removidas |
| 5 | **Arreglado** | Corrección de bugs |
| 6 | **Seguridad** | Vulnerabilidades corregidas |

---

## Workflow de Ejecución

### Fase 1: Determinar Rango

**Parsear `$ARGUMENTS`**:

| Input | Interpretación |
|-------|----------------|
| "desde última versión" | `$last_tag..HEAD` |
| "desde v2.0.0" | `v2.0.0..HEAD` |
| "todos los cambios" | `$last_tag..HEAD` |
| vacío | `$last_tag..HEAD` |

```bash
# Obtener último tag
last_tag=$(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)
echo "Rango: $last_tag..HEAD"
```

### Fase 2: Extraer la Verdad (Diff Real)

```bash
# Lista de archivos con estado REAL
git diff "$last_tag..HEAD" --name-status
```

**Estados**:
- `A` = Added (archivo nuevo)
- `M` = Modified (archivo modificado)
- `D` = Deleted (archivo eliminado)
- `R` = Renamed (archivo renombrado)

**Filtrar ruido** (excluir del análisis):

```yaml
exclude:
  - "*.lock"
  - "package-lock.json"
  - "yarn.lock"
  - "pnpm-lock.yaml"
  - "dist/**"
  - "build/**"
  - "coverage/**"
  - "node_modules/**"
  - "*.min.js"
  - "*.min.css"
  - ".git/**"

evaluate_case_by_case:
  - "*.md"           # docs - incluir si sustancial
  - "*.test.*"       # tests - incluir si documenta feature
  - ".github/**"     # CI - incluir si impacta usuarios
```

### Fase 3: Análisis Semántico por Archivo

Para **cada archivo relevante**, obtener y analizar el diff:

```bash
# Diff específico del archivo
git diff "$last_tag..HEAD" -- "path/to/file"
```

**Análisis por tipo de archivo**:

| Tipo | Qué Buscar | Categoría |
|------|------------|-----------|
| **Código** | Funciones/clases nuevas | Añadido |
| | Funciones modificadas | Cambiado |
| | Funciones eliminadas | Eliminado (¿breaking?) |
| | Validaciones/edge cases | Arreglado |
| | Sanitización/auth | Seguridad |
| **Config** | Opciones nuevas | Añadido |
| | Opciones modificadas | Cambiado |
| | Opciones eliminadas | Eliminado (¿breaking?) |
| **Docs** | Guías nuevas | Añadido |
| | Updates sustanciales | Cambiado |
| | Solo typos | Skip |

**Detección de Breaking Changes**:

```yaml
breaking_signals:
  - Función/método público eliminado
  - Cambio de firma (parámetros requeridos añadidos/removidos)
  - Cambio de tipo de retorno
  - Opción de config requerida eliminada
  - Cambio de comportamiento por defecto
  - API endpoint removido o cambiado
```

### Fase 4: Contexto del "Por Qué"

El diff dice QUÉ cambió. Los commits/PRs dicen POR QUÉ.

```bash
# Commits que tocaron el archivo (contexto)
git log "$last_tag..HEAD" --oneline -- "path/to/file"

# Si hay PR asociado (extraer de mensaje)
# Buscar patrón #NNN en mensajes
```

**Uso del contexto**:
- Enriquecer descripción con propósito del cambio
- Identificar PR asociado para referencia
- NO usar para determinar qué cambió (eso viene del diff)

### Fase 5: Agrupación Inteligente

**Regla**: Cambios relacionados = una entrada.

```
Archivos modificados:
├── hooks/anti_drift.py (M)
├── docs/claude-rules/hooks.md (M)
└── tests/test_anti_drift.py (M)

→ UNA entrada:
"Refactorizado hook anti_drift con validación mejorada"

NO tres entradas separadas.
```

**Criterios de agrupación**:
- Mismo módulo/componente
- Mismo PR asociado
- Mismo scope funcional

### Fase 6: Síntesis y Redacción

**Para cada cambio/grupo**:

1. **Categorizar** según análisis semántico
2. **Redactar** descripción técnica y específica
3. **Referenciar** PR si existe, o "commit directo" si no
4. **Marcar** breaking changes con `⚠️ **BREAKING**`

**Formato de entrada**:

```markdown
- Descripción técnica específica del cambio real (PR #123)
- ⚠️ **BREAKING**: Cambio que rompe compatibilidad (commit directo)
```

**Reglas de redacción**:
- Español
- 1-2 líneas máximo
- QUÉ cambió, no historia de cómo llegamos ahí
- Técnico y específico (módulos, funciones, impacto)
- Sin verbosidad innecesaria

### Fase 7: Actualizar CHANGELOG.md

1. **Leer** CHANGELOG.md completo
2. **Localizar** sección `## [No Publicado]`
3. **Construir** contenido nuevo:

```markdown
## [No Publicado]

### Añadido

- **Feature X**: Descripción técnica específica (PR #123)
- **Feature Y**: Otra descripción técnica (commit directo)

### Cambiado

- ⚠️ **BREAKING**: Descripción del breaking change con migración (PR #124)
- Refactorizado módulo Z para mejor performance (PR #125)

### Eliminado

- Removido archivo deprecado `old-feature.md` (PR #126)

### Arreglado

- Corregida validación de rutas en Windows (commit directo)
```

4. **Usar Edit** para reemplazar sección completa
5. **Verificar** con Read

### Fase 8: Reporte Final

```
✅ CHANGELOG actualizado (Truth-Based Analysis)

Análisis realizado:
├── Archivos en diff: 15
├── Archivos analizados: 12
├── Archivos excluidos: 3 (locks, builds)
└── Líneas de diff: 342

Cambios documentados:
├── Añadido: 2
├── Cambiado: 3 (1 breaking)
├── Eliminado: 1
└── Arreglado: 1

Fuentes de contexto:
├── PRs asociados: #89, #88, #87
└── Commits directos: 4

Confiabilidad: 100% (basado en diff real, no narrativa)
```

---

## Reglas Inquebrantables

1. **El diff es la verdad** - Si no está en `git diff`, no existe
2. **Commits dan contexto, no verdad** - Explican el "por qué", no el "qué"
3. **Reverts se auto-cancelan** - Si algo se añadió y luego se quitó, no aparece
4. **Una entrada por feature** - No por archivo, no por commit
5. **Breaking changes siempre marcados** - `⚠️ **BREAKING**`
6. **Español, técnico, conciso** - 1-2 líneas, máximo detalle
7. **NO commitear automáticamente** - Usuario decide cuándo

---

## Anti-Patrones (Evitar)

| ❌ Incorrecto | ✅ Correcto |
|---------------|-------------|
| "Múltiples mejoras en hooks" | "Hook anti_drift v5.0 con restatement científico" |
| "Actualizado archivo X" | "Nueva validación de rutas Windows en X" |
| "Cambios en 5 archivos" | "Refactorizado sistema de skills con carga lazy" |
| Documentar feature revertido | Ignorar (no existe en diff final) |
| Una entrada por commit | Una entrada por cambio lógico |
