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
| **Búsqueda** | Conceptual (knowledge graph) | Semántica (full-text) |
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
