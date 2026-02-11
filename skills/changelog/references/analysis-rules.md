# Analysis Rules Reference

## Análisis por Tipo de Archivo

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

## Detección de Breaking Changes

```yaml
breaking_signals:
  - Función/método público eliminado
  - Cambio de firma (parámetros requeridos añadidos/removidos)
  - Cambio de tipo de retorno
  - Opción de config requerida eliminada
  - Cambio de comportamiento por defecto
  - API endpoint removido o cambiado
```

## Agrupación

```
Archivos modificados:
├── hooks/anti_drift.py (M)
├── docs/claude-rules/hooks.md (M)
└── tests/test_anti_drift.py (M)

→ UNA entrada:
"Refactorizado hook anti_drift con validación mejorada"

NO tres entradas separadas.
```

Criterios: mismo módulo/componente, mismo PR asociado, mismo scope funcional.

---

*Version: 1.0.0 | Updated: 2026-02-11*
