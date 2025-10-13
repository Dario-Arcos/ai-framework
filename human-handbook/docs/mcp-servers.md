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
PRECEDENCIA completa (mayor → menor):
1. Enterprise managed policies     (no aplica al plugin)
2. Command line arguments          (no aplica al plugin)
3. .claude/settings.local.json    ← Plugin instala aquí (MAYOR)
4. .claude/settings.json          ← Si creas este, es IGNORADO
5. ~/.claude/settings.json         (global, no aplica al plugin)
```

⚠️ **Crítico:** El plugin usa #3 (`settings.local.json`), que tiene MAYOR precedencia que `settings.json` (#4).

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

Abre tu `.mcp.json` existente y agrega el nuevo servidor (ejemplo: GitHub):

```json
{
  "mcpServers": {
    // ... tus servers existentes (playwright, shadcn)
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
```

⚠️ **No sobreescribas** los servers existentes - solo agrega el nuevo.

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
