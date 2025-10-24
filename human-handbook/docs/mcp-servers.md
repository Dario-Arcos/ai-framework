# MCP Servers

::: tip ¿Qué es MCP?
Model Context Protocol conecta Claude Code con herramientas externas (databases, APIs, browsers, docs) sin escribir código custom. Extend capabilities on-demand.
:::

---

## Servidores Instalados

| Server         | Propósito                                    | Package                          |
| -------------- | -------------------------------------------- | -------------------------------- |
| **playwright** | Browser automation, E2E testing, screenshots | `@playwright/mcp`                |
| **shadcn**     | Shadcn/ui v4 component library integration   | `@jpisnice/shadcn-ui-mcp-server` |

**Rationale:** playwright (testing/design review) + shadcn (UI acceleration). Más servers según necesidades del proyecto.

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
**Fecha**: 2025-10-24 | **Servers Instalados**: playwright, shadcn
:::
