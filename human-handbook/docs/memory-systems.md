# Memory Systems

::: tip ¿Qué son los Memory Systems?
Sistemas de persistencia de contexto para Claude Code. Permiten recordar decisiones, conversaciones y conocimiento del proyecto entre sesiones.
:::

---

## ¿Qué problema resuelves?

### Necesito acceder a la memoria oficial del proyecto

→ **Team Memory** - Read-only vía proxy, memoria compartida del equipo

**Ideal para:**
- Consultar decisiones arquitectónicas del proyecto
- Buscar patrones establecidos por el equipo
- Onboarding de nuevos miembros (contexto inmediato)
- Mantener consistencia en todo el equipo

### Necesito buscar MIS conversaciones pasadas sin afectar memoria oficial

→ **Episodic Memory** - Búsqueda semántica local, memoria personal

**Ideal para:**
- Encontrar "¿Cómo resolvimos el bug de autenticación hace 2 semanas?"
- Rastrear evolución de decisiones técnicas
- Recuperar patrones de solución aplicados anteriormente
- Buscar por contexto semántico, no solo keywords

---

## Comparativa Técnica

| Feature | Team Memory | Episodic Memory |
|---------|-------------|-----------------|
| **Propósito** | Memoria oficial del proyecto | Memoria personal del desarrollador |
| **Tipo** | Knowledge graph | Vector search |
| **Granularidad** | Facts/entities | Conversaciones completas |
| **Búsqueda** | Conceptual (knowledge graph) | Semántica (vector embeddings) |
| **Persistencia** | Cloud (proxy Railway) | Local SQLite |
| **Acceso** | Read-only (vía proxy) | Read/write (local) |
| **Alimentación** | Planificada por admin | Automática (session-end) |
| **Costo contexto** | Bajo (~2 tools) | Bajo (~3 tools) |
| **Privacidad** | Compartido (equipo) | Personal (solo tú) |

::: tip Implementación desde Cero
Si necesitas configurar tu propia memoria estructurada personal, consulta [MCP Servers - Core Memory](/docs/mcp-servers#core-memory-personal)
:::

---

## Setup Guides

- [Team Memory Setup](#team-memory)
- [Episodic Memory Setup](#episodic-memory)

---

## Episodic Memory

### ¿Qué es?

Búsqueda semántica local de tus conversaciones completas con Claude Code. A diferencia de Team Memory (knowledge graph centralizado), Episodic Memory mantiene un índice personal de TODAS tus conversaciones para búsqueda full-text y semántica.

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

::: tip Compatibilidad
Compatible con team-memory y core-memory (tool names diferentes). Puedes usar los tres simultáneamente sin conflictos.
:::

**Verificar instalación:**

```bash
/mcp  # Debe mostrar: episodic-memory: ✓ Connected
```

**Primera sincronización:**

El plugin indexará conversaciones automáticamente. Para sync manual inmediato:

```bash
episodic-memory sync
episodic-memory stats  # Ver estadísticas
```

::: tip ⚡ Recomendación: Procesamiento Completo Inicial
**IMPORTANTE**: La primera vez que instalas o actualizas episodic-memory, ejecuta el procesamiento completo para indexar todas las conversaciones inmediatamente.

**Por qué es importante:**
- El hook automático procesa solo 10 conversaciones por sesión (incremental)
- Si tienes cientos de conversaciones, tomaría múltiples sesiones indexarlas todas
- El procesamiento completo inicial te da acceso inmediato a toda tu historia

**Comando recomendado:**
```bash
# Procesa todas las conversaciones con 8 hilos paralelos
index-conversations --cleanup --concurrency 8

# Verificar resultado
episodic-memory stats
```

**Tiempo estimado:** ~2-5 minutos para 100-500 conversaciones (depende de tu máquina)

**Recursos usados:**
- Modelo de embeddings LOCAL (~23 MB, descarga automática primera vez)
- CPU: Procesamiento paralelo (8 hilos)
- RAM: ~150-300 MB durante procesamiento
- Disco: Base de datos SQLite + resúmenes

Después de esta indexación inicial, el hook automático mantendrá todo sincronizado incrementalmente (10 conversaciones por sesión).
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

### Comandos CLI

::: info Acceso Directo
Además del uso desde Claude Code, puedes usar episodic-memory directamente desde terminal.
:::

```bash
# Sincronizar conversaciones nuevas // [!code highlight]
episodic-memory sync

# Buscar por contenido // [!code highlight]
episodic-memory search "authentication bug"

# Ver estadísticas de indexación
episodic-memory stats

# Ver conversación completa
episodic-memory show <conversation-id>

# Búsqueda avanzada con fecha
episodic-memory search "Docker" --since "2024-11-01"

# Exportar conversación
episodic-memory export <conversation-id> > conversation.md
```

::: details Comandos Avanzados
```bash
# Reindexar toda la base de datos
episodic-memory reindex

# Limpiar conversaciones antiguas (>90 días)
episodic-memory prune --days 90

# Ver configuración actual
episodic-memory config

# Verificar integridad de la base de datos
episodic-memory verify
```
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
→ [MCP Servers - Configuración avanzada](/docs/mcp-servers)

---

## Team Memory

### ¿Qué es?

Acceso read-only a la memoria oficial del proyecto vía proxy Railway. Permite al equipo consultar decisiones, arquitectura y facts del proyecto sin capacidad de modificación. La alimentación es planificada y controlada por el admin.

**Casos de uso:**
- Consultar decisiones arquitectónicas del proyecto
- Buscar patrones establecidos por el equipo
- Onboarding de nuevos miembros (contexto inmediato)
- Mantener consistencia en todo el equipo

### Configuración Rápida (requiere admin)

::: warning Prerequisito Administrativo
Team Memory requiere acceso autorizado al servidor del proyecto. Contacta a tu admin para obtener credenciales.
:::

**1. Obtener token de acceso:**

Solicita el token de acceso a tu admin del proyecto.

**2. Configurar en `.claude/.mcp.json` (gitignored):**

```json {3-10}
{
  "mcpServers": {
    "team-memory": { // [!code highlight]
      "type": "http", // [!code highlight]
      "url": "https://team-core-proxy.up.railway.app/mcp", // [!code highlight]
      "headers": { // [!code highlight]
        "Authorization": "Bearer YOUR_TEAM_TOKEN_HERE" // [!code warning]
      }
    }
  }
}
```

::: danger Seguridad del Token
- **NUNCA** commitees `.claude/.mcp.json` con tokens
- El archivo debe estar en `.gitignore`
- Rota tokens comprometidos inmediatamente
- Usa tokens de solo lectura cuando sea posible
:::

**3. Activar en `.claude/settings.local.json`:**

```json {2}
{
  "disabledMcpjsonServers": ["playwright", "shadcn", "core-memory"] // [!code highlight]
  // team-memory activo (no está en la lista) // [!code highlight]
}
```

**4. Restart:** `Ctrl+D` → `claude`

**5. Verificar:** `/mcp` debe mostrar `team-memory: ✓ Connected`

::: tip Verificación Rápida
Si ves errores de conexión, verifica primero la conectividad de red al servidor Railway antes de reportar problemas.
:::

### Uso desde Claude Code

::: code-group

```bash [Team Memory (Read-Only)]
Busca en memoria del equipo: patrones de autenticación
# Solo consultas, no modificación
```

```bash [Episodic Memory (Read-Write)]
Busca en mis conversaciones: cómo implementé autenticación
# Tu memoria personal, con escritura
```

:::

::: warning Limitación Read-Only
Team Memory es **solo lectura**. No puedes agregar información directamente (no hay `memory_ingest`). Para agregar conocimiento oficial, notifica al admin del proyecto.
:::

### Diferencia con Episodic Memory

| Aspecto | Team Memory | Episodic Memory |
|---------|-------------|-----------------|
| **Contenido** | Facts curados del proyecto | Todas tus conversaciones |
| **Búsqueda** | Conceptual (knowledge graph) | Semántica (full-text) |
| **Privacidad** | Compartido (equipo) | Personal (solo tú) |
| **Modificación** | No (read-only) | Sí (local) |

**Recomendación:** Usa ambos complementariamente:
- Team Memory: Para consultar decisiones oficiales
- Episodic Memory: Para rastrear tu trabajo personal

### Setup Completo

Para detalles técnicos completos del proxy, troubleshooting y configuración avanzada:

→ [MCP Servers - Team Memory Server](/docs/mcp-servers#team-memory-server-local-config)
→ [Team Core Proxy Repository](https://github.com/Dario-Arcos/team-core-proxy)

---

## ¿Cuál Usar Cuándo?

### Escenarios Comunes

::: tip Escenario 1: "¿Cómo resolvimos este bug antes?"
✅ **Episodic Memory** - Busca en tus conversaciones pasadas

Ideal para recuperar soluciones que TÚ implementaste anteriormente.
:::

::: info Escenario 2: "¿Cuál es la arquitectura oficial de autenticación?"
✅ **Team Memory** - Consulta decisiones del proyecto

Fuente de verdad oficial para decisiones arquitectónicas del equipo.
:::

::: tip Escenario 3: "¿Qué experimenté con Docker la semana pasada?"
✅ **Episodic Memory** - Tu trabajo personal no afecta memoria oficial

Experimentos y prototipos quedan en tu memoria personal sin contaminar la oficial.
:::

::: info Escenario 4: "¿Por qué elegimos PostgreSQL sobre MongoDB?"
✅ **Team Memory** - Decisiones arquitectónicas documentadas

Contexto histórico de decisiones técnicas críticas del proyecto.
:::

::: tip Escenario 5: "¿Qué discutí con Claude sobre refactoring?"
✅ **Episodic Memory** - Conversaciones completas indexadas

Búsqueda semántica de tus sesiones de desarrollo y discusiones técnicas.
:::

### Workflow Recomendado

```mermaid
graph TD
    A[Pregunta técnica] --> B{¿Es personal/experimental?}
    B -->|Sí| C[Episodic Memory]
    B -->|No| D{¿Es decisión oficial?}
    D -->|Sí| E[Team Memory]
    D -->|No sé| F[Intenta Episodic primero]
    F --> G{¿Encontraste?}
    G -->|No| E
    G -->|Sí| H[Usa resultado]
    C --> I{¿Solución importante?}
    I -->|Sí| J[Notifica al admin]
    I -->|No| H
```

::: info Estrategia Híbrida
**Paso 1**: Búsqueda rápida personal → **Episodic Memory** (fast, local)

**Paso 2**: Si no encuentras o necesitas validar → **Team Memory** (source of truth oficial)

**Paso 3**: Encontraste solución nueva e importante → Notifica al admin para agregar a Team Memory
:::

### Anti-Patrones

::: danger NO uses Team Memory para
- ❌ Experimentos personales
- ❌ Trabajo en progreso no validado
- ❌ Conversaciones exploratorias
- ❌ Prototipos descartables
- ❌ Debug sessions temporales

**Razón**: Team Memory es la fuente de verdad oficial del equipo. Contaminarla con trabajo experimental reduce su valor.
:::

::: danger NO uses Episodic Memory para
- ❌ Decisiones oficiales del proyecto (no es source of truth)
- ❌ Documentación canónica
- ❌ Compartir conocimiento con el equipo
- ❌ Onboarding de nuevos miembros

**Razón**: Episodic Memory es personal y local. No está disponible para el resto del equipo.
:::

::: tip Uso Complementario
✅ **SÍ usa ambos sistemas**: Son complementarios, no excluyentes.

- **Episodic Memory**: Tu cuaderno personal de desarrollo
- **Team Memory**: La biblioteca oficial del proyecto
:::

---

## Solución de Problemas

### Episodic Memory no indexa conversaciones

::: details Diagnóstico y Solución

**Verificaciones básicas:**

1. ✅ `episodic-memory sync` ejecutado al menos una vez
2. ✅ Conversaciones no tienen marker `DO_NOT_INDEX`
3. ✅ MCP server activo en `/mcp`

**Comandos de diagnóstico:**

```bash
# Ver estadísticas de indexación // [!code highlight]
episodic-memory stats

# Debe mostrar: // [!code highlight]
# Total conversations: X
# Indexed conversations: Y
# Last sync: <timestamp>

# Forzar resincronización
episodic-memory sync --force

# Verificar integridad de la base de datos
episodic-memory verify
```

**Soluciones comunes:**

::: code-group

```bash [Reindexar todo]
episodic-memory reindex
# Reconstruye el índice completo
```

```bash [Limpiar y sincronizar]
episodic-memory sync --clean
# Elimina índice corrupto y reindexa
```

```bash [Verificar permisos]
ls -la ~/.episodic-memory/
# Verifica que tienes permisos de escritura
```

:::

:::

### Team Memory no conecta

::: details Diagnóstico y Solución

**Verificaciones básicas:**

1. ✅ Token válido en `.claude/.mcp.json`
2. ✅ Server no está en `disabledMcpjsonServers`
3. ✅ Conexión de red a Railway proxy

**Test de conectividad:**

```bash
# Verificar health del servidor // [!code highlight]
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://team-core-proxy.up.railway.app/health

# Respuesta esperada: // [!code highlight]
# {"status":"ok"}

# Test de autenticación
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://team-core-proxy.up.railway.app/mcp/v1/info
```

**Problemas comunes:**

::: warning Token Inválido o Expirado
```bash
# Error: 401 Unauthorized
# Solución: Solicita nuevo token al admin
```
:::

::: warning Network Issues
```bash
# Error: Connection timeout
# Solución: Verifica firewall, proxy corporativo, o VPN
```
:::

::: warning MCP Configuration
```json
// ❌ INCORRECTO (typo en URL) // [!code error]
{
  "url": "https://team-core-proxy.railway.app/mcp" // [!code error]
}

// ✅ CORRECTO // [!code highlight]
{
  "url": "https://team-core-proxy.up.railway.app/mcp" // [!code highlight]
}
```
:::

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
    "shadcn",        // Solo si no trabajas con UI
    "core-memory"    // Usa episodic-memory O core-memory, no ambos
  ]
}
```

```json [Solo Memory Systems]
// .claude/settings.local.json
{
  "disabledMcpjsonServers": [
    "playwright",
    "shadcn"
  ]
  // Solo episodic-memory o team-memory activo
}
```

```json [Performance Mode]
// .claude/settings.local.json
{
  "disabledMcpjsonServers": [
    "playwright",
    "shadcn",
    "core-memory",
    "team-memory"
  ]
  // Solo episodic-memory para búsqueda rápida
}
```

:::

**Recomendaciones:**

- ✅ Mantén solo memory systems + 1-2 tools esenciales
- ✅ Deshabilita MCPs no críticos para tu tarea actual
- ✅ Consulta [Context Budget en MCP Servers](/docs/mcp-servers#context-budget-responsabilidad)
- ⚠️ Múltiples memory systems simultáneos pueden causar confusión en Claude

:::

---

::: info Última Actualización
**Fecha**: 2025-11-11 | **Cambios**: Método plugin para episodic-memory (npm install deprecated)
:::

