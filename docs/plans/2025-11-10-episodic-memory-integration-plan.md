# Episodic Memory Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use ai-framework:executing-plans to implement this plan task-by-task.

**Goal:** Integrar documentación de Episodic Memory en ai-framework como sistema complementario a Team Memory para búsqueda semántica personal de conversaciones.

**Architecture:** Documentación problem-first que unifica sistemas de memoria (Team Memory + Episodic Memory) con guías de setup híbridas, actualización de sidebar VitePress, y configuración MCP siguiendo patrón existente.

**Tech Stack:** Markdown (VitePress), JavaScript (config), JSON (MCP config)

---

## Pre-requisitos

- Proyecto ai-framework clonado
- Node.js instalado (para validar VitePress)
- Permisos de escritura en repositorio

---

## Task 1: Crear Documento Base `memory-systems.md`

**Files:**
- Create: `human-handbook/docs/memory-systems.md`

**Step 1: Crear archivo con header y estructura básica**

```bash
touch human-handbook/docs/memory-systems.md
```

**Step 2: Escribir header y sección "¿Qué problema resuelves?"**

```markdown
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
```

**Step 3: Verificar sintaxis Markdown**

```bash
# Validar que no hay errores de sintaxis
head -n 20 human-handbook/docs/memory-systems.md
```

Expected: Contenido visible sin errores

**Step 4: Commit progreso**

```bash
git add human-handbook/docs/memory-systems.md
git commit -m "docs: create memory-systems.md base structure"
```

---

## Task 2: Agregar Tabla Comparativa

**Files:**
- Modify: `human-handbook/docs/memory-systems.md`

**Step 1: Agregar sección de comparativa técnica**

Agregar después de la última línea de Task 1:

```markdown
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
```

**Step 2: Verificar formato de tabla**

```bash
# Contar columnas de tabla (debe ser consistente)
grep -A 10 "Comparativa Técnica" human-handbook/docs/memory-systems.md | grep "^|" | head -n 3
```

Expected: 3 líneas con mismo número de `|`

**Step 3: Commit progreso**

```bash
git add human-handbook/docs/memory-systems.md
git commit -m "docs(memory-systems): add technical comparison table"
```

---

## Task 3: Documentar Setup de Episodic Memory

**Files:**
- Modify: `human-handbook/docs/memory-systems.md`

**Step 1: Agregar sección completa de Episodic Memory**

Agregar después de la última línea de Task 2:

```markdown
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
```

**Step 2: Verificar bloques de código**

```bash
# Contar bloques de código (deben estar cerrados)
grep -c '```' human-handbook/docs/memory-systems.md
```

Expected: Número par (cada apertura tiene cierre)

**Step 3: Commit progreso**

```bash
git add human-handbook/docs/memory-systems.md
git commit -m "docs(memory-systems): add episodic memory setup guide"
```

---

## Task 4: Documentar Setup de Team Memory

**Files:**
- Modify: `human-handbook/docs/memory-systems.md`

**Step 1: Agregar sección completa de Team Memory**

Agregar después de la última línea de Task 3:

```markdown
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
```

**Step 2: Commit progreso**

```bash
git add human-handbook/docs/memory-systems.md
git commit -m "docs(memory-systems): add team memory setup guide"
```

---

## Task 5: Agregar Guía de Decisión y Troubleshooting

**Files:**
- Modify: `human-handbook/docs/memory-systems.md`

**Step 1: Agregar sección de guía de decisión**

Agregar después de la última línea de Task 4:

```markdown
## ¿Cuál Usar Cuándo?

### Escenarios Comunes

**Escenario 1: "¿Cómo resolvimos este bug antes?"**
✅ **Episodic Memory** - Busca en tus conversaciones pasadas

**Escenario 2: "¿Cuál es la arquitectura oficial de autenticación?"**
✅ **Team Memory** - Consulta decisiones del proyecto

**Escenario 3: "¿Qué experimenté con Docker la semana pasada?"**
✅ **Episodic Memory** - Tu trabajo personal no afecta memoria oficial

**Escenario 4: "¿Por qué elegimos PostgreSQL sobre MongoDB?"**
✅ **Team Memory** - Decisiones arquitectónicas documentadas

**Escenario 5: "¿Qué discutí con Claude sobre refactoring?"**
✅ **Episodic Memory** - Conversaciones completas indexadas

### Workflow Recomendado

```
1. Búsqueda rápida personal
   → Episodic Memory (fast, local)

2. Si no encuentras o necesitas validar
   → Team Memory (source of truth oficial)

3. Encontraste solución nueva e importante
   → Notifica al admin para agregar a Team Memory
```

### Anti-Patrones

❌ **NO uses Team Memory para:** Experimentos, trabajo en progreso, conversaciones exploratorias

❌ **NO uses Episodic Memory para:** Decisiones oficiales del proyecto (no es source of truth)

✅ **SÍ usa ambos:** Son complementarios, no excluyentes

---
```

**Step 2: Agregar sección de troubleshooting**

```markdown
## Troubleshooting

### Episodic Memory no indexa conversaciones

**Check:**
1. `episodic-memory sync` ejecutado al menos una vez
2. Conversaciones no tienen marker `DO_NOT_INDEX`
3. MCP server activo en `/mcp`

**Debug:**
```bash
episodic-memory stats
# Debe mostrar conversaciones indexadas
```

### Team Memory no conecta

**Check:**
1. Token válido en `.claude/.mcp.json`
2. Server no está en `disabledMcpjsonServers`
3. Conexión de red a Railway proxy

**Debug:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://team-core-proxy.up.railway.app/health
# Expected: {"status":"ok"}
```

### Performance degradation

Si notas lentitud con múltiples MCPs activos:
- Deshabilita MCPs no críticos en `settings.local.json`
- Mantén solo memory systems + 1-2 tools esenciales
- Ver [Context Budget en MCP Servers](/docs/mcp-servers#context-budget-responsabilidad)

---

::: info Última Actualización
**Fecha**: 2025-11-10 | **Sistemas**: Team Memory (proxy) + Episodic Memory (local)
:::
```

**Step 3: Verificar documento completo**

```bash
# Contar líneas totales
wc -l human-handbook/docs/memory-systems.md
```

Expected: ~350-400 líneas

**Step 4: Commit progreso**

```bash
git add human-handbook/docs/memory-systems.md
git commit -m "docs(memory-systems): add decision guide and troubleshooting"
```

---

## Task 6: Actualizar Sidebar de VitePress

**Files:**
- Modify: `human-handbook/.vitepress/config.js:42-68`

**Step 1: Leer configuración actual**

```bash
# Ver sección sidebar actual
sed -n '42,68p' human-handbook/.vitepress/config.js
```

Expected: Ver estructura actual de sidebar

**Step 2: Agregar entrada "Memory Systems" en sección Guides**

Modificar línea 51 (después de "Pro Tips"):

```javascript
sidebar: [
  {
    text: "Guides",
    collapsed: false,
    items: [
      { text: "Por Qué AI Framework", link: "/docs/why-ai-framework" },
      { text: "Inicio Rápido", link: "/docs/quickstart" },
      { text: "AI-First Workflow", link: "/docs/ai-first-workflow" },
      { text: "Pro Tips", link: "/docs/claude-code-pro-tips" },
      { text: "Memory Systems", link: "/docs/memory-systems" }, // ← NUEVO
    ],
  },
  {
    text: "Tools",
    collapsed: false,
    items: [
      { text: "Comandos", link: "/docs/commands-guide" },
      { text: "Agentes", link: "/docs/agents-guide" },
      { text: "Skills", link: "/docs/skills-guide" },
      { text: "MCP Servers", link: "/docs/mcp-servers" },
    ],
  },
  {
    text: "Project",
    collapsed: false,
    items: [{ text: "Changelog", link: "/docs/changelog" }],
  },
],
```

**Step 3: Validar sintaxis JavaScript**

```bash
# Validar que config.js es JavaScript válido
node -c human-handbook/.vitepress/config.js
```

Expected: Sin errores de sintaxis

**Step 4: Verificar cambio en diff**

```bash
git diff human-handbook/.vitepress/config.js
```

Expected: Ver línea agregada con "Memory Systems"

**Step 5: Commit cambio**

```bash
git add human-handbook/.vitepress/config.js
git commit -m "config(vitepress): add Memory Systems to Guides sidebar"
```

---

## Task 7: Actualizar Configuración MCP

**Files:**
- Modify: `.mcp.json:1-17`

**Step 1: Leer configuración actual**

```bash
cat .mcp.json
```

Expected: Ver configuración actual con playwright, shadcn, core-memory

**Step 2: Agregar servidor episodic-memory**

Modificar después de "core-memory":

```json
{
  "$comment": "SECURITY: Never add tokens/secrets here (repo is public). Use .claude/.mcp.json for private configs. See human-handbook/docs/mcp-servers.md",
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"]
    },
    "shadcn": {
      "command": "npx",
      "args": ["-y", "@jpisnice/shadcn-ui-mcp-server"]
    },
    "core-memory": {
      "type": "http",
      "url": "https://core.heysol.ai/api/v1/mcp?source=Claude-Code"
    },
    "episodic-memory": {
      "command": "episodic-memory-mcp"
    }
  }
}
```

**Step 3: Validar sintaxis JSON**

```bash
# Validar que .mcp.json es JSON válido
python3 -m json.tool .mcp.json > /dev/null
```

Expected: Sin errores de sintaxis

**Step 4: Verificar cambio en diff**

```bash
git diff .mcp.json
```

Expected: Ver entrada "episodic-memory" agregada

**Step 5: Commit cambio**

```bash
git add .mcp.json
git commit -m "config(mcp): add episodic-memory server"
```

---

## Task 8: Validar Integración Completa

**Files:**
- Test: `human-handbook/docs/memory-systems.md`
- Test: `human-handbook/.vitepress/config.js`
- Test: `.mcp.json`

**Step 1: Verificar archivo memory-systems.md existe y tiene contenido**

```bash
# Debe existir y tener ~350-400 líneas
ls -lh human-handbook/docs/memory-systems.md
wc -l human-handbook/docs/memory-systems.md
```

Expected: Archivo existe, ~350-400 líneas

**Step 2: Verificar sidebar contiene Memory Systems**

```bash
# Debe contener entrada "Memory Systems"
grep -A 2 "Memory Systems" human-handbook/.vitepress/config.js
```

Expected: Línea con link `/docs/memory-systems`

**Step 3: Verificar .mcp.json contiene episodic-memory**

```bash
# Debe contener servidor episodic-memory
grep -A 2 "episodic-memory" .mcp.json
```

Expected: Configuración de episodic-memory

**Step 4: Iniciar VitePress dev server (validación final)**

```bash
# Iniciar servidor de docs
cd human-handbook && npm run docs:dev
```

Expected: Servidor inicia sin errores, navegar a http://localhost:5173/ai-framework/

**Step 5: Validar navegación**

1. Abrir http://localhost:5173/ai-framework/
2. Buscar "Memory Systems" en sidebar bajo "Guides"
3. Click en "Memory Systems"
4. Verificar que página carga correctamente
5. Verificar que tabla comparativa se renderiza
6. Verificar que bloques de código se muestran correctamente

**Step 6: Detener servidor**

```bash
# Ctrl+C para detener
```

**Step 7: Commit final (si todo OK)**

```bash
git add -A
git commit -m "docs: complete episodic memory integration

- Created memory-systems.md with problem-first approach
- Added sidebar entry in VitePress config
- Configured episodic-memory MCP server
- Documented Team Memory vs Episodic Memory differences
- Added decision guide and troubleshooting

Closes: episodic-memory integration
"
```

---

## Task 9: Actualizar Changelog (Opcional)

**Files:**
- Modify: `human-handbook/docs/changelog.md`

**Step 1: Agregar entrada al changelog**

Agregar al inicio del archivo (después del header):

```markdown
## [Unreleased]

### Added
- Documentación completa de Memory Systems (Team Memory + Episodic Memory)
- Guía de decisión problem-first para elegir sistema de memoria
- Configuración MCP para episodic-memory
- Tabla comparativa técnica entre sistemas
- Troubleshooting para problemas comunes

### Changed
- Sidebar organizado: Memory Systems en Guides (conceptual), MCP Servers en Tools (técnico)

---
```

**Step 2: Commit changelog**

```bash
git add human-handbook/docs/changelog.md
git commit -m "docs(changelog): add episodic memory integration entry"
```

---

## Verificación Final

**Checklist:**

- [ ] `human-handbook/docs/memory-systems.md` existe (~350-400 líneas)
- [ ] Sidebar contiene "Memory Systems" en sección Guides
- [ ] `.mcp.json` contiene configuración de episodic-memory
- [ ] VitePress dev server inicia sin errores
- [ ] Página Memory Systems navega correctamente
- [ ] Tablas se renderizan correctamente
- [ ] Bloques de código tienen syntax highlighting
- [ ] Links internos funcionan (a mcp-servers.md)
- [ ] Todos los commits tienen mensajes descriptivos
- [ ] Changelog actualizado (opcional)

---

## Rollback (si algo falla)

```bash
# Ver últimos commits
git log --oneline -n 10

# Revertir al commit anterior
git reset --hard <commit-hash-before-integration>
```

---

## Próximos Pasos (después de implementar)

1. **Proof of Concept**: Instalar episodic-memory en proyecto ai-framework
2. **Testing**: Verificar que búsqueda semántica funciona
3. **Documentation**: Agregar screenshots si es necesario
4. **Team Onboarding**: Compartir con equipo y documentar feedback

---

**Plan creado**: 2025-11-10
**Estimación**: 60-90 minutos (9 tasks × 7-10 min/task)
**Complejidad**: Size M (documentación + configuración, sin código)
