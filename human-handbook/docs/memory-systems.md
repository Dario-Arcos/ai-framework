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
npm install -g @obra/episodic-memory
```

**2. Configurar MCP en `.mcp.json`:**

```json
{
  "mcpServers": {
    "episodic-memory": {
      "command": "episodic-memory-mcp"
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
<INSTRUCTIONS-TO-EPISODIC-MEMORY>
DO_NOT_INDEX
</INSTRUCTIONS-TO-EPISODIC-MEMORY>
```

Las conversaciones marcadas se archivan pero NO se indexan.

### Ver También

→ [Documentación oficial completa](https://github.com/obra/episodic-memory)
→ [MCP Servers - Configuración avanzada](/docs/mcp-servers)

---
