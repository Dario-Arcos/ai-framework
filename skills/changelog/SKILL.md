---
name: changelog
description: Actualiza CHANGELOG.md con análisis Truth-Based del diff real entre versiones
---

# Truth-Based Changelog

Actualiza `[No Publicado]` en CHANGELOG.md basándose en el **diff real** entre versiones, no en la narrativa de commits.

**Principio fundamental**: Los commits cuentan una historia. El diff cuenta la verdad.

**Input**: `$ARGUMENTS` - Rango a analizar (ej: "desde v4.2.0", "últimos cambios")

## Workflow

### Fase 1: Determinar Rango

Parsear `$ARGUMENTS`:

| Input | Interpretación |
|-------|----------------|
| "desde última versión" | `$last_tag..HEAD` |
| "desde v2.0.0" | `v2.0.0..HEAD` |
| "todos los cambios" | `$last_tag..HEAD` |
| vacío | `$last_tag..HEAD` |

```bash
last_tag=$(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)
```

### Fase 2: Extraer la Verdad (Diff Real)

```bash
git diff "$last_tag..HEAD" --name-status
```

Filtrar ruido: `*.lock`, `package-lock.json`, `dist/**`, `build/**`, `coverage/**`, `node_modules/**`, `*.min.*`

Evaluar caso por caso: `*.md`, `*.test.*`, `.github/**`

### Fase 3: Análisis Semántico por Archivo

Para cada archivo relevante, obtener diff específico y analizar según tipo.
Read [references/analysis-rules.md](references/analysis-rules.md) for file type analysis table and breaking change signals.

### Fase 4: Contexto del "Por Qué"

```bash
git log "$last_tag..HEAD" --oneline -- "path/to/file"
```

Enriquecer descripción con propósito. NO usar para determinar qué cambió (eso viene del diff).

### Fase 5: Agrupación Inteligente

Cambios relacionados = una entrada. Criterios: mismo módulo, mismo PR, mismo scope funcional.

### Fase 6: Síntesis y Redacción

Read [references/changelog-format.md](references/changelog-format.md) for Keep a Changelog categories, entry format, and writing rules.

### Fase 7: Actualizar CHANGELOG.md

1. Read CHANGELOG.md completo
2. Localizar sección `## [No Publicado]`
3. Construir contenido con categorías aplicables
4. Edit para reemplazar sección completa
5. Verificar con Read

### Fase 8: Reporte Final

```
✅ CHANGELOG actualizado (Truth-Based Analysis)

Análisis: N archivos en diff, N analizados, N excluidos
Cambios: N Añadido, N Cambiado, N Eliminado, N Arreglado
Fuentes: PRs asociados + commits directos
Confiabilidad: 100% (basado en diff real)
```

## Reglas Inquebrantables

1. **El diff es la verdad** — Si no está en `git diff`, no existe
2. **Commits dan contexto, no verdad** — Explican el "por qué", no el "qué"
3. **Reverts se auto-cancelan** — Si algo se añadió y luego se quitó, no aparece
4. **Una entrada por feature** — No por archivo, no por commit
5. **Breaking changes siempre marcados** — `⚠️ **BREAKING**`
6. **Español, técnico, conciso** — 1-2 líneas, máximo detalle
7. **NO commitear automáticamente** — Usuario decide cuándo
