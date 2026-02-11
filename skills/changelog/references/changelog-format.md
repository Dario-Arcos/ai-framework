# Changelog Format Reference

## Categorías Keep a Changelog

| Orden | Categoría | Descripción |
|-------|-----------|-------------|
| 1 | **Añadido** | Funcionalidades nuevas |
| 2 | **Cambiado** | Cambios en funcionalidad existente |
| 3 | **Obsoleto** | Marcado para eliminación futura |
| 4 | **Eliminado** | Funcionalidades removidas |
| 5 | **Arreglado** | Corrección de bugs |
| 6 | **Seguridad** | Vulnerabilidades corregidas |

## Formato de Entrada

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

## Reglas de Redacción

- Español
- 1-2 líneas máximo
- QUÉ cambió, no historia de cómo llegamos ahí
- Técnico y específico (módulos, funciones, impacto)
- Sin verbosidad innecesaria

## Anti-Patrones

| Incorrecto | Correcto |
|------------|----------|
| "Múltiples mejoras en hooks" | "Hook anti_drift v5.0 con restatement científico" |
| "Actualizado archivo X" | "Nueva validación de rutas Windows en X" |
| "Cambios en 5 archivos" | "Refactorizado sistema de skills con carga lazy" |
| Documentar feature revertido | Ignorar (no existe en diff final) |
| Una entrada por commit | Una entrada por cambio lógico |

---

*Version: 1.0.0 | Updated: 2026-02-11*
