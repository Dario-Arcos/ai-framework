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

### Quick Install

**1. Instalar globalmente:**

```bash
npm install -g episodic-memory
```

**2. Configurar MCP en `.mcp.json`:**

```json
{
  "mcpServers": {
    "episodic-memory": {
      "command": "episodic-memory-mcp-server"
    }
  }
}
```

**3. Activar en `.claude/settings.local.json`:**

```json
{
  "disabledMcpjsonServers": ["playwright", "shadcn", "core-memory"]
  // episodic-memory activo (no está en la lista)
}
```

**4. Restart:** `Ctrl+D` → `claude`

**5. Verificar:** `/mcp` debe mostrar `episodic-memory: ✓ Connected`

### Uso desde Claude Code

**Búsqueda básica:**
```
Busca en mis conversaciones: decisiones sobre arquitectura de API
```

**Búsqueda con filtro de fecha:**
```
Busca conversaciones sobre Docker desde hace 1 semana
```

**Multi-concepto (AND search):**
```
Busca conversaciones sobre testing Y performance
```

### Comandos CLI

Además del uso desde Claude Code, puedes usar episodic-memory desde terminal:

```bash
# Sincronizar conversaciones nuevas
episodic-memory sync

# Buscar
episodic-memory search "authentication bug"

# Ver estadísticas
episodic-memory stats

# Ver conversación específica
episodic-memory show <conversation-id>
```

### Features Clave

| Feature | Descripción |
|---------|-------------|
| **Semantic Search** | Búsqueda por significado, no solo keywords |
| **Offline** | Todo local, sin servicios cloud |
| **Privacy** | Control total sobre qué se indexa |
| **Multi-concept** | Combina 2-5 conceptos con AND |
| **Date Filtering** | Filtra por rango temporal |

### Control de Indexación

Para excluir conversaciones específicas, usa markers:

```xml
<INSTRUCTIONS-TO-EPISODIC-MEMORY>DO NOT INDEX THIS CHAT</INSTRUCTIONS-TO-EPISODIC-MEMORY>
```

Las conversaciones marcadas se archivan pero NO se indexan.

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

### Quick Setup (requiere admin)

**1. Obtener token:**

Solicita el token de acceso a tu admin del proyecto.

**2. Configurar en `.claude/.mcp.json` (gitignored):**

```json
{
  "mcpServers": {
    "team-memory": {
      "type": "http",
      "url": "https://team-core-proxy.up.railway.app/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TEAM_TOKEN_HERE"
      }
    }
  }
}
```

**3. Activar en `.claude/settings.local.json`:**

```json
{
  "disabledMcpjsonServers": ["playwright", "shadcn", "core-memory"]
  // team-memory activo (no está en la lista)
}
```

**4. Restart:** `Ctrl+D` → `claude`

**5. Verificar:** `/mcp` debe mostrar `team-memory: ✓ Connected`

### Uso desde Claude Code

**Búsqueda:**
```
Busca en memoria del equipo: patrones de autenticación
```

**Limitación:** Solo read-only. No puedes agregar información (no hay `memory_ingest`).

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
