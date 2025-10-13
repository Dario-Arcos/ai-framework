# MCP Servers

**Model Context Protocol (MCP)** conecta Claude Code con herramientas externas: databases, APIs, browsers, documentación.

---

## 🔧 Servidores Instalados

AI Framework incluye por defecto:

| Server         | Propósito                                    | Package                          |
| -------------- | -------------------------------------------- | -------------------------------- |
| **playwright** | Browser automation, E2E testing, screenshots | `@playwright/mcp`                |
| **shadcn**     | Shadcn/ui v4 component library integration   | `@jpisnice/shadcn-ui-mcp-server` |

Más servidores se agregarán según evolucione el ecosistema.

---

## ⚙️ Cómo Funciona la Configuración

### Precedencia de archivos (oficial)

```
PRECEDENCIA (mayor → menor):
3. .claude/settings.local.json    ← Plugin instala aquí (MAYOR)
4. .claude/settings.json          ← Si creas este, es IGNORADO
```

⚠️ **Crítico:** `settings.local.json` tiene MAYOR precedencia que `settings.json`.

### Para agregar servidores

Edita `.claude/settings.local.json` (el que instaló el plugin):

```json
{
  "enabledMcpjsonServers": ["playwright", "shadcn", "github"]
  // ... resto de configuración
}
```

---

## 🎯 Agregar Servidores MCP

### 1. Agregar a `.mcp.json`

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--isolated"]
    },
    "shadcn": { "command": "npx", "args": ["@jpisnice/shadcn-ui-mcp-server"] },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
```

### 2. Activar en `.claude/settings.local.json`

```json
{
  "enabledMcpjsonServers": ["playwright", "shadcn", "github"],
  "cleanupPeriodDays": 7,
  "includeCoAuthoredBy": false,
  "permissions": {
    // ... resto de configuración existente
  }
}
```

### 3. Reiniciar Claude Code

```bash
# Exit (Ctrl+D) y reiniciar
claude
```

---

## 📚 Catálogo de Servidores

Para explorar servidores disponibles:

- **Official Registry:** https://github.com/modelcontextprotocol/servers
- **Community Hub:** https://mcpservers.org
- **Claude Code Docs:** https://docs.claude.com/en/docs/claude-code/mcp

**Recomendados:** filesystem, github, memory, postgres, context7, brave-search

---

_Última actualización: 2025-10-13 | 2 servers instalados_
