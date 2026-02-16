---
name: changelog
description: Actualiza CHANGELOG.md con análisis Truth-Based del diff real entre versiones. Use when: "actualizar changelog", "qué cambió desde la última versión", "preparar release notes", "documentar cambios para vX.Y", "changelog", "what changed", "release notes", "prepare release".
---

# Truth-Based Changelog

Actualiza `[No Publicado]` en CHANGELOG.md basándose en el **diff real** entre versiones, no en la narrativa de commits.

**Input**: `$ARGUMENTS` — Rango a analizar (ej: "desde v4.2.0", "últimos cambios")

## When to Use

- Preparar una nueva versión o release
- Generar release notes
- Auditar qué cambió realmente entre dos puntos del repositorio

## When NOT to Use

| Situación | Usar en su lugar |
|---|---|
| Crear el commit message para cambios actuales | commit |
| Crear un PR con descripción de cambios | pull-request |
| Publicar un release en GitHub | release |

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

**Error handling**:

| Error | Fallback |
|-------|----------|
| No hay tags | Usar primer commit como base |
| Tag inválido en `$ARGUMENTS` | Listar tags disponibles, pedir al usuario que elija |
| Repositorio sin commits | Abortar con mensaje claro |
| CHANGELOG.md no existe | Crear estructura base con `## [No Publicado]` |

### Fase 2: Extraer la Verdad y Análisis Semántico

```bash
git diff "$last_tag..HEAD" --name-status
```

Read [references/analysis-rules.md](references/analysis-rules.md) for signal/noise filtering, file type analysis table, and breaking change signals.

**Resumen de filtrado**:
- **Excluir siempre**: lock files, build artifacts, dotfiles de desarrollo, cambios de formateo puro
- **Incluir siempre**: cambios de API pública, correcciones de seguridad, cambios de runtime mínimo
- **Evaluar caso por caso**: refactors internos, CI/CD, documentación

Para cada archivo relevante, obtener diff específico y analizar según tipo.

**Error handling**: Si `git diff` falla, verificar rango válido. Si diff >100 archivos, agrupar por directorio primero. Si no hay cambios, informar al usuario sin crear entrada vacía.

### Fase 3: Contexto del "Por Qué"

```bash
git log "$last_tag..HEAD" --oneline -- "path/to/file"
```

Enriquecer descripción con propósito. NO usar para determinar qué cambió (eso viene del diff).

### Fase 4: Detección de Breaking Changes

Read [references/breaking-changes.md](references/breaking-changes.md) for detection signals, severity classification, and communication template.

Para cada breaking change detectado:
1. Clasificar severidad (Alta/Media/Baja)
2. Redactar entrada con prefijo `⚠️ **BREAKING**`
3. Incluir sección de migración para severidad Alta
4. Verificar si fue deprecado en versión anterior — referenciar

### Fase 5: Agrupación Inteligente

Cambios relacionados = una entrada. Criterios: mismo módulo, mismo PR, mismo scope funcional.

**Orden dentro de cada categoría**: Breaking changes primero, luego por scope de impacto (más usuarios afectados → más arriba).

### Fase 6: Redacción

Read [references/entry-quality-rubric.md](references/entry-quality-rubric.md) for quality dimensions and transformation examples.
Read [references/changelog-format.md](references/changelog-format.md) for entry format, categories, and anti-patterns.

**Reglas inline de calidad**:
- Toda entrada debe alcanzar nivel 2+ en las 4 dimensiones (Especificidad, Impacto, Accionabilidad, Concisión)
- Verbos en imperativo: Añadir, Corregir, Eliminar, Refactorizar
- Nombrar módulo/función/componente específico
- Incluir métricas cuando existan
- 1-2 líneas máximo

### Fase 7: Actualizar CHANGELOG.md

1. Read CHANGELOG.md completo
2. Localizar sección `## [No Publicado]` (si no existe, crearla al inicio)
3. Construir contenido con categorías aplicables
4. Cada entrada DEBE incluir referencia: `(PR #N)`, `(commit abc1234)`, o `(issue #N)`
5. Edit para reemplazar sección completa (preservar entradas existentes, agregar sin duplicar)
6. Verificar con Read

### Fase 8: Verificación

Checklist de completitud:

- [ ] Cada cambio significativo en el diff tiene entrada correspondiente
- [ ] Ninguna entrada describe algo que no existe en el diff
- [ ] Breaking changes tienen prefijo `⚠️ **BREAKING**` y migración (si severidad Alta)
- [ ] Toda entrada tiene referencia (PR, commit, o issue)
- [ ] Entradas en imperativo, no participio
- [ ] Categorías ordenadas según Keep a Changelog
- [ ] Dentro de categorías: breaking primero, luego por impacto
- [ ] Reverts auto-cancelados (no aparecen)
- [ ] No hay entradas duplicadas ni solapadas

### Fase 9: Reporte Final

```
✅ CHANGELOG actualizado (Truth-Based Analysis)

Rango: $last_tag..HEAD
Análisis: N archivos en diff, N analizados, N excluidos (ruido)
Cambios: N Añadido, N Cambiado, N Obsoleto, N Eliminado, N Arreglado, N Seguridad
Breaking: N detectados (N Alta, N Media, N Baja)
Fuentes: N PRs + N commits directos referenciados
```

## Reglas Inquebrantables

1. **El diff es la verdad** — Si no está en `git diff`, no existe
2. **Commits dan contexto, no verdad** — Explican el "por qué", no el "qué"
3. **Reverts se auto-cancelan** — Si algo se añadió y luego se quitó, no aparece
4. **Una entrada por feature** — No por archivo, no por commit
5. **Breaking changes siempre marcados** — `⚠️ **BREAKING**` con migración
6. **Español, técnico, conciso** — 1-2 líneas, imperativo, módulos específicos
7. **NO commitear automáticamente** — Usuario decide cuándo
8. **Referencias obligatorias** — Cada entrada enlaza a PR, issue, o commit
9. **Orden por impacto** — Breaking changes siempre primero dentro de su categoría
10. **Calidad sobre completitud** — Preferir una entrada clara sobre tres vagas

## Related Skills

| Skill | Relación |
|---|---|
| **commit** | Genera el commit message; changelog documenta el cambio para usuarios |
| **pull-request** | PR describe cambios para revisores; changelog describe cambios para usuarios finales |
| **release** | Consume el changelog para generar release notes en GitHub |
| **verification-before-completion** | Gate de verificación aplicado en Fase 8 |
