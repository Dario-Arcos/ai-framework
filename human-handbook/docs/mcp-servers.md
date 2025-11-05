# MCP Servers

::: tip ¿Qué es MCP?
Model Context Protocol conecta Claude Code con herramientas externas (databases, APIs, browsers, docs) sin escribir código custom. Extend capabilities on-demand.
:::

---

## Servidores Instalados

| Server          | Propósito                                    | Package/URL                      | Estado Default | Context Cost |
| --------------- | -------------------------------------------- | -------------------------------- | -------------- | ------------ |
| **playwright**  | Browser automation, E2E testing, screenshots | `@playwright/mcp`                | ⚠️ Deshabilitado | Alto (~15 tools) |
| **shadcn**      | Shadcn/ui v4 component library integration   | `@jpisnice/shadcn-ui-mcp-server` | ⚠️ Deshabilitado | Medio (~7 tools) |
| **core-memory** | Personal memory (admin/write access)         | `core.heysol.ai/api/v1/mcp`      | ⚠️ Deshabilitado | Medio (~6 tools) |
| **team-memory** | Team memory (read-only via proxy)            | `team-core-proxy.railway.app`    | ⚠️ Deshabilitado | Medio (~2 tools) |

**Por defecto:** Todos deshabilitados (optimización de contexto)
**Activación:** Explícita en `.claude/settings.local.json`
**Local:** `team-memory` además requiere `.claude/.mcp.json` con token privado

---

## Configuración

**Archivo clave:** `.claude/settings.local.json` (mayor precedencia)

::: warning Importante
`.claude/settings.json` es ignorado si existe `.claude/settings.local.json`. Siempre edita el archivo `.local` para customizations.
:::

---

## ⚠️ Context Budget & Responsabilidad

::: warning Impacto en Contexto
Cada MCP activo agrega tools al system prompt de Claude Code. El presupuesto de contexto es finito.

**Regla:** Habilita solo MCPs que usas activamente en tu proyecto actual.
:::

**Context consumption estimado:**

- **1 MCP**: ~5-15 tools, 2-5% context
- **2 MCPs**: ~10-25 tools, 5-10% context
- **4+ MCPs**: ~30-50 tools, 20-30% context

**Síntomas de context overflow:**
- Respuestas más lentas
- Degradación en calidad de razonamiento
- Pérdida de contexto conversacional

**Solución:** Deshabilita MCPs no críticos para tu trabajo actual.

---

## Activar Servidores Opt-In

**Por defecto:** Todos los MCPs están deshabilitados (optimización de contexto).

**Activación:** Remueve servers de `disabledMcpjsonServers` en `.claude/settings.local.json`.

### Ejemplo: Activar Playwright + Shadcn

**1. Crear/editar `.claude/settings.local.json`:**

```json
{
  "disabledMcpjsonServers": ["core-memory", "team-memory"]
  // playwright y shadcn ahora activos (removidos de blacklist)
}
```

**2. Restart:** `Ctrl+D` → `claude`

**3. Verificar:** `/mcp` debe mostrar:
```
playwright: ✓ Connected
shadcn: ✓ Connected
```

::: tip Context-Aware Activation
Solo habilita MCPs que necesitas para tu proyecto actual. Puedes cambiar `settings.local.json` cuando cambies de proyecto.
:::

### Core Memory (Personal)

Requiere autenticación OAuth. Ver [Core Memory Expert skill](https://github.com/Dario-Arcos/ai-framework/tree/main/skills/core-memory-expert).

---

## Agregar Nuevo Servidor

**Workflow:** `.mcp.json` → `.claude/settings.local.json` → Restart

::: details Ejemplo: Agregar GitHub Server

**1. Configurar en `.mcp.json`:**

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
```

**2. Activar en `.claude/settings.local.json`:**

```json
{
  "disabledMcpjsonServers": ["core-memory", "team-memory"]
  // playwright, shadcn, github activos
}
```

**3. Restart:** `Ctrl+D` → `claude`

:::

::: details Team Memory Server (Local Config)

**Context:** `team-memory` requiere token privado → No committeable en `.mcp.json` público.

**Solución:** Configuración local en `.claude/.mcp.json` (gitignored).

**Setup:**

**1. Crear `.claude/.mcp.json`:**

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

**2. Obtener token:**
- Solicitar al admin del proyecto
- Reemplazar `YOUR_TEAM_TOKEN_HERE` con token real

**3. Activar en `.claude/settings.local.json`:**

```json
{
  "disabledMcpjsonServers": ["playwright", "shadcn", "core-memory"]
  // solo team-memory activo
}
```

**4. Restart:** `Ctrl+D` → `claude`

**5. Verificar:** `/mcp` debe mostrar `team-memory: ✓ Connected`

**Uso:**
```
Busca en memoria: [tu query]
```

**Nota:** Read-only. No puedes agregar memoria (tool `memory_ingest` no disponible).

**Repo:** [team-core-proxy](https://github.com/Dario-Arcos/team-core-proxy)

:::

---

## Catálogo & Recursos

**Registries:**

- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [mcpservers.org](https://mcpservers.org)
- [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/mcp)

**Recomendados:** `filesystem` · `github` · `memory` · `postgres` · `context7` · `brave-search`

---

## Uso con Framework

**Playwright:** Browser automation via `/agent:design-review` (screenshots automáticos)

**Shadcn:** Component integration via `/agent:shadcn-quick-helper` (install commands)

---

## Troubleshooting

::: details Server No Aparece

**Check:**

1. Server NO está en `disabledMcpjsonServers` (o lista está vacía)
2. `.mcp.json` tiene configuración del server
3. Restart después de cambios

**Debug:**
```bash
cat .claude/settings.local.json | grep disabledMcpjsonServers
```

:::

::: details Environment Variables

**Opción 1 (recomendada):** System environment

```bash
export GITHUB_TOKEN="your_token"
claude
```

**Opción 2:** `.mcp.json` env (usa `${ }` placeholders)

```json
{ "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" } }
```

:::

---

## Best Practices

::: tip Minimalismo
Comienza con 2-3 servers. Cada uno consume recursos y aumenta startup time. Agrega más solo cuando tengas necesidad clara.
:::

::: warning Security
**Nunca** commits tokens en `.mcp.json`. Usa env vars del sistema con placeholders `${ }`
:::

---

---

::: info Última Actualización
**Fecha**: 2025-11-05 | **Servers**: Todos opt-in (context optimization)
:::
