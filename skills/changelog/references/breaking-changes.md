# Protocolo de Breaking Changes

Los breaking changes son las entradas de mayor impacto en un changelog: un cambio mal comunicado puede romper builds, pipelines y la confianza de los consumidores. Por eso requieren tratamiento especial en tres dimensiones — detección clara mediante señales en el diff, comunicación estructurada que explique el qué, el por qué y el cómo migrar, y guía de migración concreta con código before/after que elimine la ambigüedad.

## Ciclo de Vida de 3 Fases

Inspirado en la política de deprecación de Django, todo breaking change planificado sigue un ciclo de tres fases que da tiempo a los consumidores para adaptarse.

### Fase 1: Deprecación

- Feature marcado como obsoleto con categoría `Obsoleto` en el changelog
- Alternativa documentada en la misma entrada
- Warning en runtime (cuando sea posible)
- Plazo de remoción comunicado (ej: "Remoción planificada: v3.0")

Ejemplo de entrada:

```markdown
### Obsoleto
- Marcar `createUser(name, email)` como obsoleto — usar `createUser(options)` en su lugar. Remoción planificada: v3.0 (PR #200)
```

### Fase 2: Warning Activo

- Feature sigue funcionando pero emite advertencia visible
- Documentación actualizada para reflejar la nueva forma preferida
- Período mínimo recomendado: 1 versión minor

### Fase 3: Remoción

- Feature eliminado
- Entrada en `Eliminado` con prefijo `⚠️ **BREAKING**`
- Referencia a la guía de migración
- Referencia a la versión donde se deprecó

Ejemplo de entrada:

```markdown
### Eliminado
- ⚠️ **BREAKING**: Remover `createUser(name, email)` deprecado en v2.5 — usar `createUser(options)` (PR #250)
  - **Migración**: `createUser("John", "j@x.com")` → `createUser({ name: "John", email: "j@x.com" })`
```

> **Nota**: No todos los breaking changes siguen el ciclo de 3 fases. Los arreglos de seguridad y las versiones major pueden omitir la fase de deprecación cuando la urgencia lo justifica.

## Template de Comunicación

Inspirado en el patrón "What Should I Do?" de Astro, toda comunicación de breaking change debe responder tres preguntas:

```markdown
### Qué cambió
[Descripción del cambio] — [Comportamiento anterior] → [Comportamiento nuevo]

### Por qué
[Razón técnica o de producto para el cambio]

### Qué hacer
[Pasos de migración con código before/after]
```

Template completo para entrada de changelog:

```markdown
- ⚠️ **BREAKING**: [Qué cambió] — [Anterior] → [Nuevo] (PR #N)
  - **Migración**: [Pasos concretos]
```

## Señales de Detección en el Diff

Lista expandida de señales que indican un breaking change cuando se encuentran en un diff:

| Señal | Ejemplo | Severidad |
|-------|---------|-----------|
| API pública eliminada | `export function getUser` removido | Alta |
| API pública renombrada | `getUser` → `fetchUser` | Alta |
| Parámetro requerido añadido | `function save(data, options)` donde `options` es nuevo y requerido | Alta |
| Parámetro eliminado | `function save(data, format)` → `function save(data)` | Alta |
| Tipo de retorno cambiado | `string` → `Promise<string>` | Alta |
| Valor por defecto cambiado | `timeout: 5000` → `timeout: 30000` | Media |
| Variable de entorno removida | `DATABASE_URL` ya no se lee | Alta |
| Variable de entorno renombrada | `DB_URL` → `DATABASE_URL` | Alta |
| Flag de CLI cambiado | `--verbose` → `--log-level` | Media |
| Flag de CLI removido | `--legacy-mode` eliminado | Alta |
| Formato de configuración cambiado | JSON → YAML, o cambio de estructura | Alta |
| Runtime mínimo aumentado | `engines.node: ">=16"` → `">=18"` | Media |
| Puerto por defecto cambiado | `PORT=3000` → `PORT=8080` | Media |
| Protocolo cambiado | HTTP → HTTPS, REST → GraphQL | Alta |
| Esquema de BD incompatible | Columna eliminada, tipo cambiado | Alta |
| Formato de respuesta cambiado | `{ data: [] }` → `{ items: [], total: 0 }` | Alta |

## Tabla de Severidad

| Severidad | Criterio | Urgencia de Comunicación |
|-----------|----------|--------------------------|
| **Alta** | Causa error inmediato si no se migra | Entrada prominente con migración obligatoria |
| **Media** | Cambia comportamiento pero no causa error | Entrada con migración recomendada |
| **Baja** | Cambio cosmético o de conveniencia | Mención en changelog, sin sección de migración especial |

## Reglas

1. Todo breaking change detectado DEBE tener prefijo `⚠️ **BREAKING**`
2. Todo breaking change de severidad Alta DEBE incluir sección de migración
3. Breaking changes van PRIMERO dentro de su categoría
4. Si hay más de 3 breaking changes, considerar agrupar en sección dedicada `### ⚠️ Breaking Changes` al inicio
5. Referencia cruzada obligatoria: si fue deprecado en una versión anterior, mencionar cuál

---

*Version: 1.0.0 | Updated: 2026-02-16*
