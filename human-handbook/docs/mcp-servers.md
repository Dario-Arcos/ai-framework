# MCP Servers

::: tip ¿Qué es MCP?
Model Context Protocol conecta Claude Code con herramientas externas (databases, APIs, browsers, docs) sin escribir código custom. Extend capabilities on-demand.
:::

---

## Servidores Instalados

| Server          | Propósito                                    | Package/URL                      | Scope   |
| --------------- | -------------------------------------------- | -------------------------------- | ------- |
| **playwright**  | Browser automation, E2E testing, screenshots | `@playwright/mcp`                | Público |
| **shadcn**      | Shadcn/ui v4 component library integration   | `@jpisnice/shadcn-ui-mcp-server` | Público |
| **core-memory** | Personal memory (admin/write access)         | `core.heysol.ai/api/v1/mcp`      | Público |
| **team-memory** | Team memory (read-only via proxy)            | `team-core-proxy.railway.app`    | Local   |

**Público:** Configurados en `.mcp.json` (repo)
**Local:** Requieren `.claude/.mcp.json` (gitignored, contiene tokens privados)

---

## Configuración

**Archivo clave:** `.claude/settings.local.json` (mayor precedencia)

::: warning Importante
`.claude/settings.json` es ignorado si existe `.claude/settings.local.json`. Siempre edita el archivo `.local` para customizations.
:::

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
  "enabledMcpjsonServers": ["playwright", "shadcn", "github"]
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
  "enabledMcpjsonServers": ["team-memory"]
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

1. `enabledMcpjsonServers` incluye el nombre
2. `.mcp.json` tiene configuración
3. Restart después de cambios

**Debug:** `cat .claude/settings.local.json | grep enabledMcpjsonServers`

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
**Fecha**: 2025-11-03 | **Servers**: playwright, shadcn, core-memory, team-memory (local)
:::
