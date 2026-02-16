# Rúbrica de Calidad para Entradas de Changelog

## Dimensiones de Calidad

Cada entrada de changelog se evalúa en 4 dimensiones independientes, con puntuación de 1 a 3. La puntuación total máxima es 12.

### 1. Especificidad (1-3)

| Nivel | Criterio | Ejemplo |
|-------|----------|---------|
| 1 — Vago | No nombra módulos, funciones, ni componentes | "Mejoras de rendimiento" |
| 2 — Parcial | Nombra el área pero no el componente específico | "Mejorar rendimiento de la API" |
| 3 — Específico | Nombra módulo, función, o componente exacto | "Reducir latencia de `GET /api/users` mediante caché de consultas SQL" |

### 2. Impacto (1-3)

| Nivel | Criterio | Ejemplo |
|-------|----------|---------|
| 1 — Invisible | No comunica por qué importa | "Cambiar configuración de timeout" |
| 2 — Implícito | El impacto se puede inferir | "Aumentar timeout de conexión a 30s" |
| 3 — Explícito | Comunica impacto directo al usuario | "Aumentar timeout de conexión a 30s para evitar desconexiones en redes lentas" |

### 3. Accionabilidad (1-3)

| Nivel | Criterio | Ejemplo |
|-------|----------|---------|
| 1 — Pasivo | El lector no sabe qué hacer | "Cambios en la API de autenticación" |
| 2 — Informativo | El lector entiende el cambio | "Requerir token JWT en header Authorization" |
| 3 — Accionable | El lector sabe exactamente qué hacer si le afecta | "Requerir token JWT en header `Authorization: Bearer <token>`. Migración: reemplazar cookie de sesión por JWT (ver docs/auth-migration.md)" |

### 4. Concisión (1-3)

| Nivel | Criterio | Ejemplo |
|-------|----------|---------|
| 1 — Excesivo | Más de 3 líneas, incluye historia de desarrollo | "Después de investigar varios enfoques, decidimos cambiar el sistema de caché. Primero probamos Redis pero encontramos problemas de latencia. Finalmente implementamos un caché en memoria..." |
| 2 — Verboso | Información correcta pero con relleno | "Implementar nuevo sistema de caché en memoria que reemplaza al anterior sistema basado en archivos temporales para mejorar performance" |
| 3 — Conciso | 1-2 líneas, toda palabra es necesaria | "Reemplazar caché de archivos por caché en memoria — reducir latencia de lectura en 80% (PR #234)" |

## Nivel Mínimo Aceptable

Toda entrada debe alcanzar al menos nivel 2 en las 4 dimensiones. Nivel 1 en cualquier dimensión = reescribir.

## Tabla de Transformación

| Entrada Original (Nivel 1) | Entrada Mejorada (Nivel 3) | Dimensión Mejorada |
|---|---|---|
| "Bug fixes" | "Corregir error de serialización en `UserDTO` que causaba respuestas 500 en `/api/profile` (PR #301)" | Especificidad, Impacto |
| "Mejoras de rendimiento" | "Reducir tiempo de carga del dashboard de 4.2s a 1.1s mediante lazy loading de gráficos (PR #302)" | Especificidad, Impacto |
| "Actualizada documentación" | "Documentar flujo de autenticación OAuth 2.0 con ejemplos de integración para React y Vue (PR #303)" | Especificidad, Accionabilidad |
| "Cambios en la API" | "⚠️ **BREAKING**: Cambiar `POST /users` para requerir campo `email` — antes opcional, ahora obligatorio (PR #304)" | Accionabilidad, Impacto |
| "Nuevas funcionalidades" | "Añadir endpoint `GET /api/export` para exportar datos en CSV y JSON con paginación (PR #305)" | Especificidad |
| "Refactoring" | "Refactorizar módulo de pagos para separar lógica de Stripe y PayPal en adaptadores independientes (PR #306)" | Especificidad, Impacto |
| "Corregido error en login" | "Corregir error que impedía login con email con caracteres especiales (ñ, ü) en dominios internacionales (PR #307)" | Especificidad, Impacto |
| "Mejoras de seguridad" | "Corregir vulnerabilidad XSS en campo de comentarios del foro — sanitizar HTML antes de renderizar (CVE-2026-1234, PR #308)" | Especificidad, Accionabilidad |
| "Eliminado código legacy" | "⚠️ **BREAKING**: Remover soporte para Node.js 16 — versión mínima ahora es Node.js 18 LTS (PR #309)" | Impacto, Accionabilidad |
| "Varios arreglos menores" | "Corregir cálculo de zona horaria en programación de tareas que adelantaba 1 hora durante horario de verano (PR #310)" | Especificidad |
| "Añadidos tests" | Skip — no documentar cambios de infraestructura de tests en changelog | Filtrado |
| "Dependencias actualizadas" | "Actualizar React de v17 a v18 — habilitar concurrent features y automatic batching (PR #311)" | Impacto, Accionabilidad |

## Reglas de Redacción

1. **Verbo en imperativo**: Añadir, Corregir, Eliminar, Refactorizar, Actualizar, Marcar (no participio: Añadido, Corregido)
2. **Nombrar el componente**: módulo, función, endpoint, componente, hook — siempre específico
3. **Incluir métricas cuando existan**: "reducir en 35%", "soportar hasta 10K registros", "de 4.2s a 1.1s"
4. **Referencia obligatoria**: Toda entrada termina con (PR #N), (commit abc1234), o (issue #N)
5. **Una línea, dos máximo**: Si necesitas más, la entrada cubre demasiado — dividir en dos
6. **Qué + por qué, nunca cómo**: "Corregir timeout en WebSocket para evitar desconexiones" ✓ / "Corregir timeout en WebSocket cambiando el valor de 5s a 30s en el archivo config.ts línea 42" ✗

---

*Version: 1.0.0 | Updated: 2026-02-16*
