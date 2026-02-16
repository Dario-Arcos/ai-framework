# Formato de Changelog

## Categorías Keep a Changelog

| Orden | Categoría | Descripción |
|-------|-----------|-------------|
| 1 | **Añadido** | Funcionalidades nuevas |
| 2 | **Cambiado** | Cambios en funcionalidad existente |
| 3 | **Obsoleto** | Marcado para eliminación futura |
| 4 | **Eliminado** | Funcionalidades removidas |
| 5 | **Arreglado** | Corrección de bugs |
| 6 | **Seguridad** | Vulnerabilidades corregidas |

> **Orden dentro de cada categoría**: las entradas se ordenan por impacto — breaking changes primero, luego por alcance de usuarios afectados (de mayor a menor).

## Formato de Entrada

Formato híbrido Keep a Changelog + Common Changelog. Toda entrada DEBE incluir referencia a PR, issue o commit.

Los verbos en la descripción usan modo imperativo en español ("Añadir", "Corregir", "Eliminar"), aunque los encabezados de categoría mantienen su forma estándar ("Añadido", "Cambiado", etc.).

```markdown
## [No Publicado]

### Añadido

- **Feature X**: Descripción técnica en imperativo (PR #123, commit abc1234)
- **Feature Y**: Otra descripción técnica específica (PR #124)

### Cambiado

- ⚠️ **BREAKING**: [Qué cambió] — [Anterior] → [Nuevo]. Migración: [pasos] (PR #125)
- Refactorizar módulo Z para mejorar performance en 35% (PR #126)

### Obsoleto

- Marcar `oldFunction()` como obsoleto — usar `newFunction()` en su lugar. Remoción planificada: v3.0 (PR #127)

### Eliminado

- ⚠️ **BREAKING**: Remover endpoint `/api/v1/legacy` deprecado en v2.0 (PR #128)

### Arreglado

- Corregir validación de rutas en Windows que causaba error 500 en uploads (PR #129)

### Seguridad

- Corregir inyección SQL en endpoint de búsqueda (CVE-2026-XXXX) (PR #130)
```

## Reglas de Redacción

- Español técnico conciso
- 1-2 líneas máximo por entrada
- QUÉ cambió + POR QUÉ importa, no historia de cómo se llegó
- Verbos en imperativo (Añadir, Corregir, Eliminar, Refactorizar)
- Nombrar módulos/funciones/componentes específicos
- Incluir métricas cuando sea posible ("reducir en 35%", "soportar hasta 10K registros")
- Referencia obligatoria al final: (PR #N), (commit abc1234), o (issue #N)

## Formato de Breaking Changes

Plantilla para documentar cambios incompatibles, inspirada en el formato de Astro:

```markdown
- ⚠️ **BREAKING**: [Qué cambió] — [Comportamiento anterior] → [Comportamiento nuevo]
  - **Migración**: [Pasos concretos o diff de código]
```

**Ejemplo:**

```markdown
- ⚠️ **BREAKING**: Cambiar firma de `createUser(name, email)` → `createUser(options)` — pasar objeto de opciones en lugar de argumentos posicionales (PR #200)
  - **Migración**: `createUser("John", "j@x.com")` → `createUser({ name: "John", email: "j@x.com" })`
```

## Anti-Patrones

| Incorrecto | Correcto |
|------------|----------|
| "Bug fixes" | "Corregir error de deprecación PHP 8.2 que causaba fallos en el dashboard admin (PR #301)" |
| "Mejoras de rendimiento" | "Reducir tiempo de respuesta de API en 35% mediante lazy loading de módulos (PR #302)" |
| "Múltiples mejoras en hooks" | "Añadir validación de esquema JSON en hook anti_drift (PR #303)" |
| "Actualizado archivo X" | "Añadir soporte de rutas Windows en módulo de upload (PR #304)" |
| "Cambios en 5 archivos" | "Refactorizar sistema de skills con carga lazy para reducir tiempo de inicio (PR #305)" |
| "Mejoras menores" | "Corregir cálculo de timeout en reconexión WebSocket (PR #306)" |
| "Documentación actualizada" | "Documentar API de webhooks con ejemplos de integración (PR #307)" |
| Documentar feature revertido | Ignorar (no existe en diff final) |
| Una entrada por commit | Una entrada por cambio lógico |
| Entrada sin referencia | Siempre incluir (PR #N) o (commit abc1234) |

---

*Version: 2.0.0 | Updated: 2026-02-16*
