# MCP Servers

::: tip Model Context Protocol
MCP conecta Claude Code con herramientas externas: databases, APIs, browsers, documentación. Extend capabilities sin código custom.
:::

---

## 🔧 Servidores Incluidos

AI Framework incluye por defecto:

| Server         | Propósito                                    | Package                          |
| -------------- | -------------------------------------------- | -------------------------------- |
| **playwright** | Browser automation, E2E testing, screenshots | `@playwright/mcp`                |
| **shadcn**     | Shadcn/ui v4 component library integration   | `@jpisnice/shadcn-ui-mcp-server` |

**Por qué estos:**

- **playwright**: Essential para testing automation y design review
- **shadcn**: Acelera UI development con component library integration

Más servidores se agregarán según evolucione el ecosistema.

---

## ⚙️ Cómo Funciona la Configuración

### Precedencia de Archivos

El plugin usa `.claude/settings.local.json` que tiene **mayor precedencia** que otros settings files:

```
PRECEDENCIA (mayor → menor):
1. Enterprise managed policies     (no aplica al plugin)
2. Command line arguments          (no aplica al plugin)
3. .claude/settings.local.json    ← Plugin usa ESTE (MAYOR)
4. .claude/settings.json          ← Si creas este, es IGNORADO
5. ~/.claude/settings.json         (global, no aplica al plugin)
```

::: tip Por Qué Importa
Si creates `.claude/settings.json` pensando que override, **será ignorado**. El plugin ya instaló `settings.local.json` con mayor precedencia.
:::

**Recomendación:** Siempre edita `.claude/settings.local.json` para customizations.

---

## 🎯 Agregar Nuevos Servidores MCP

### Paso 1: Agregar a `.mcp.json`

Abre tu `.mcp.json` existente y agrega el nuevo servidor (ejemplo: GitHub):

```json
{
  "mcpServers": {
    // Tus servers existentes (playwright, shadcn)
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
```

::: warning Preserva Existentes
No sobreescribas los servers existentes - solo agrega el nuevo.
:::

---

### Paso 2: Activar en Settings

Edita `.claude/settings.local.json`:

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

**Key:** Agrega `"github"` al array `enabledMcpjsonServers`.

---

### Paso 3: Reiniciar Claude Code

```bash
# Exit (Ctrl+D) y reiniciar
claude
```

**Verificación:** Los tools del nuevo server deben aparecer disponibles.

---

## 📚 Catálogo de Servidores

**Explora servidores disponibles:**

- **Official Registry:** [MCP Servers](https://github.com/modelcontextprotocol/servers)
- **Community Hub:** [mcpservers.org](https://mcpservers.org)
- **Claude Code Docs:** [MCP Documentation](https://docs.claude.com/en/docs/claude-code/mcp)

**Recomendados para desarrollo:**

- `filesystem` — Advanced file operations
- `github` — GitHub API integration
- `memory` — Persistent context across sessions
- `postgres` — Database operations
- `context7` — Documentation search
- `brave-search` — Web search capabilities

**Pro tip:** Start con los 2 incluidos (playwright, shadcn). Agrega más según needs específicas de tu proyecto.

---

## 🎨 Uso Efectivo

### Playwright (Browser Automation)

**Capabilities:**

- Navigate websites
- Take screenshots
- Fill forms
- Click elements
- Execute JavaScript
- Monitor network requests

**Uso típico con framework:**

```bash
# Design review de PR
/agent:design-review
# → Usa playwright MCP para browser automation
# → Screenshots automáticos para visual evidence
```

---

### Shadcn (UI Components)

**Capabilities:**

- Component source code
- Usage examples
- Installation commands
- Registry search

**Uso típico con framework:**

```bash
# Quick component help
/agent:shadcn-quick-helper
# → "Need a modal" → Provides dialog component + install command
```

---

## 🔍 Troubleshooting

### Server No Aparece

**Check:**

1. `enabledMcpjsonServers` incluye el server name
2. `.mcp.json` tiene el server configurado
3. Restart Claude Code después de cambios

**Debug:**

```bash
# Verifica que settings se cargaron
cat .claude/settings.local.json | grep enabledMcpjsonServers
```

---

### Environment Variables

Si server requiere env vars (como `GITHUB_TOKEN`):

**Opción 1: System environment**

```bash
export GITHUB_TOKEN="your_token"
claude
```

**Opción 2: `.mcp.json` env**

```json
{
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
  }
}
```

**Recomendación:** System environment es más seguro (no committed a git).

---

## 💡 Best Practices

### Start Minimal

Incluye solo servers que realmente usas. Cada server adicional:

- Consume recursos
- Aumenta startup time
- Añade complejidad a debugging

**Pattern:** Start con 2-3 servers, agrega más cuando hits clara necesidad.

---

### Security con Tokens

**Nunca commits tokens en `.mcp.json`.**

**Safe pattern:**

```json
{
  "env": {
    "API_TOKEN": "${MY_API_TOKEN}"
  }
}
```

Luego en system:

```bash
export MY_API_TOKEN="actual_token"
```

**Benefit:** `.mcp.json` can be committed safely. Token lives en environment.

---

## 🎯 Next Steps

**Experimentar:**

1. Usa playwright server para browser automation
2. Usa shadcn server para UI components
3. Cuando necesites más capabilities, explora [mcpservers.org](https://mcpservers.org)

**Contribuir:**

- Found useful server? Share en [GitHub Discussions](https://github.com/Dario-Arcos/ai-framework/discussions)
- Created custom server? Contribute via PR

---

::: info Última Actualización
**Fecha**: 2025-10-16 | **Servers**: 2 instalados por default
:::
