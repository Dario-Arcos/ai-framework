# Memory Systems

::: tip ¿Qué son los Memory Systems?
Sistemas de persistencia de contexto para Claude Code. Permiten recordar decisiones, conversaciones y conocimiento del proyecto entre sesiones.
:::

---

## Estado Actual

::: warning Deprecación de Core Memory
**Core Memory (RedPlanet)** ha sido deprecado del framework debido a:
- Diseño orientado a memoria personal, no equipos
- Inestabilidad como producto startup temprano
- Falta de features de colaboración nativas

**Team Memory** (proxy read-only) también está deprecado al depender de Core Memory.

**Solución actual**: Episodic Memory para memoria local personal.
:::

---

## Episodic Memory

### ¿Qué es?

Búsqueda semántica local de tus conversaciones completas con Claude Code. Mantiene un índice personal de TODAS tus conversaciones para búsqueda full-text y semántica.

**Casos de uso:**
- Encontrar "¿Cómo resolvimos el bug de autenticación hace 2 semanas?"
- Rastrear evolución de decisiones técnicas
- Recuperar patrones de solución aplicados anteriormente
- Buscar por contexto semántico, no solo keywords

### Instalación Rápida

::: warning Prerequisito
Requiere superpowers-marketplace instalado.
:::

**Instalación via Claude Code Plugin:**

```bash
# Paso 1: Agregar marketplace (si no lo tienes)
/plugin marketplace add obra/superpowers-marketplace

# Paso 2: Instalar plugin
/plugin install episodic-memory@superpowers-marketplace

# Paso 3: Restart Claude Code
Ctrl+D → claude
```

**El plugin configura automáticamente:**
- ✅ Binario episodic-memory
- ✅ Hook session-end para sync automático
- ✅ MCP server con tools search/read
- ✅ Indexación al finalizar cada sesión

**Verificar instalación:**

```bash
/mcp  # Debe mostrar: episodic-memory: ✓ Connected
```

**Primera sincronización:**

El plugin indexará conversaciones automáticamente. Para sync manual inmediato:

```bash
# Desde el directorio del plugin
cd ~/.claude/plugins/cache/episodic-memory
node dist/index-cli.js
```

::: tip ⚡ Recomendación: Procesamiento Completo Inicial
**IMPORTANTE**: La primera vez que instalas o actualizas episodic-memory, ejecuta el procesamiento completo para indexar todas las conversaciones inmediatamente.

**Por qué es importante:**
- El hook automático procesa solo 10 conversaciones por sesión (incremental)
- Si tienes cientos de conversaciones, tomaría múltiples sesiones indexarlas todas
- El procesamiento completo inicial te da acceso inmediato a toda tu historia

**Comando recomendado:**
```bash
cd ~/.claude/plugins/cache/episodic-memory
node dist/index-cli.js --cleanup --concurrency 8
```

**Tiempo estimado:** ~2-5 minutos para 100-500 conversaciones

**Recursos usados:**
- Modelo de embeddings LOCAL (~23 MB, descarga automática primera vez)
- CPU: Procesamiento paralelo (8 hilos)
- RAM: ~150-300 MB durante procesamiento
- Disco: Base de datos SQLite + resúmenes

Después de esta indexación inicial, el hook automático mantendrá todo sincronizado incrementalmente.
:::

### Uso desde Claude Code

::: code-group

```bash [Búsqueda Básica]
Busca en mis conversaciones: decisiones sobre arquitectura de API
```

```bash [Con Filtro de Fecha]
Busca conversaciones sobre Docker desde hace 1 semana
```

```bash [Multi-concepto (AND)]
Busca conversaciones sobre testing Y performance
```

```bash [Búsqueda Semántica]
Encuentra discusiones donde hablamos de optimizar queries
# No necesitas keywords exactas, busca por significado
```

:::

::: tip Búsqueda Semántica Inteligente
Episodic Memory usa embeddings para entender contexto. Puedes buscar por significado, no solo por palabras exactas. Por ejemplo: "problemas de rendimiento" encontrará conversaciones sobre "lentitud", "timeouts", "optimización".
:::

### Features Clave

| Feature | Descripción |
|---------|-------------|
| **Semantic Search** | Búsqueda por significado, no solo keywords |
| **Offline** | Todo local, sin servicios cloud |
| **Privacy** | Control total sobre qué se indexa |
| **Multi-concept** | Combina 2-5 conceptos con AND |
| **Date Filtering** | Filtra por rango temporal |

### Control de Indexación

::: warning Privacidad y Control
Puedes prevenir la indexación de conversaciones sensibles o experimentales.
:::

Para excluir conversaciones específicas, agrega este marker al inicio de la conversación:

```xml
<INSTRUCTIONS-TO-EPISODIC-MEMORY>DO NOT INDEX THIS CHAT</INSTRUCTIONS-TO-EPISODIC-MEMORY>
```

::: info Comportamiento
Las conversaciones marcadas se **archivan** pero **NO se indexan** en la base de datos de búsqueda. Esto es útil para:
- Conversaciones con información sensible
- Experimentos que no necesitas recordar
- Prototipos desechables
- Debugging sessions temporales
:::

### Ver También

→ [Documentación oficial completa](https://github.com/obra/episodic-memory)
→ [Integrations - Configuración avanzada](/docs/integrations)

---

## Solución de Problemas

### Episodic Memory no indexa conversaciones

::: details Diagnóstico y Solución

**Verificaciones básicas:**

1. ✅ Sync ejecutado al menos una vez
2. ✅ Conversaciones no tienen marker `DO_NOT_INDEX`
3. ✅ MCP server activo en `/mcp`

**Comandos de diagnóstico:**

```bash
# Verificar que el plugin está instalado
ls ~/.claude/plugins/cache/episodic-memory

# Ejecutar sync manual
cd ~/.claude/plugins/cache/episodic-memory
node dist/index-cli.js
```

:::

### Performance degradation

::: warning Impacto en Performance
Si notas lentitud con múltiples MCPs activos, estás excediendo el context budget recomendado.
:::

**Estrategias de optimización:**

::: code-group

```json [Configuración Mínima]
// .claude/settings.local.json
{
  "disabledMcpjsonServers": [
    "playwright",    // Solo si no haces browser testing
    "shadcn"         // Solo si no trabajas con UI
  ]
}
```

:::

**Recomendaciones:**

- ✅ Mantén solo memory systems + 1-2 tools esenciales
- ✅ Deshabilita MCPs no críticos para tu tarea actual
- ✅ Consulta [Context Budget en Integrations](/docs/integrations)

---

## Futuro: Memoria Compartida de Equipo

::: info Evaluación en Progreso
La memoria compartida vectorial para equipos está en evaluación. Opciones consideradas:

- **Mem0 Platform**: API managed con orgs/projects
- **Qdrant + Proxy custom**: Self-hosted con control total
- **Supabase pgvector**: SQL familiar

El proxy pattern desarrollado (`team-core-proxy`) es reutilizable para cualquier backend.

Cuando el mercado madure, se evaluará una solución estable.
:::

---

::: info Última Actualización
**Fecha**: 2025-12-06 | **Cambios**: Deprecación de Core Memory y Team Memory
:::
