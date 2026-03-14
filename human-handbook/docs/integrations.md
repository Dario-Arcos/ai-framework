# Integraciones

Las integraciones son extensiones que conectan AI Framework con herramientas externas: plugins que agregan skills, MCPs que dan acceso a APIs y servicios, y catálogos donde encontrar más componentes. Esta guía cubre qué hay disponible y cómo configurarlo.

> **Antes de empezar**: lee [Agentes](./agents-guide.md) para entender los componentes nativos del framework antes de ver las extensiones.

---

## Skills nativos

Incluidos en el plugin. No requieren instalación.

### agent-browser

CLI de [AstroTechLabs](https://github.com/AstroTechLabs/agent-browser) para browser automation. Reemplaza WebFetch/WebSearch cuando necesitas interacción real con páginas.

**Capacidades:**
- Navegación y scraping de páginas dinámicas
- E2E testing con snapshots del DOM
- Form filling y clicks por referencia
- Screenshots, PDFs, video recording
- Sesiones autenticadas con estado persistente
- Manejo de tabs, frames, cookies, network mocking

```bash
# Workflow típico
agent-browser open https://example.com
agent-browser snapshot -i          # Lista elementos interactivos (@e1, @e2...)
agent-browser fill @e1 "texto"
agent-browser click @e2
agent-browser screenshot result.png
```

Además del CLI, el paquete incluye skills especializadas que se sincronizan a `~/.claude/skills/` automáticamente:

| Skill | Descripción |
|-------|-------------|
| `agent-browser` | Workflow completo de browser automation: navegación, snapshots, formularios, autenticación, sesiones, diffing |
| `dogfood` | QA exploratorio sistemático — recorre la app como usuario real, documenta cada issue con screenshots y videos de repro |
| `electron` | Automatización de apps Electron (VS Code, Slack, Discord, Figma) conectando vía Chrome DevTools Protocol |
| `vercel-sandbox` | Ejecuta agent-browser + Chrome headless dentro de microVMs efímeras de Vercel Sandbox |

Se instala automáticamente en la primera sesión. Para desactivar:

```bash
export AI_FRAMEWORK_SKIP_BROWSER_INSTALL=1
```

---

## Plugins recomendados

### Superpowers

Skills profesionales complementarios: TDD, planificación estructurada, code review bidireccional, parallel agents, y más. Mantenido por [obra](https://github.com/obra/superpowers).

::: code-group
```bash [Instalación]
# Agregar marketplace
/plugin marketplace add obra/superpowers-marketplace

# Instalar plugin
/plugin install superpowers@superpowers-marketplace
```

```bash [Actualización]
/plugin marketplace update superpowers-marketplace
/plugin update superpowers@superpowers-marketplace
```
:::

::: details Skills incluidos (no nativos de ai-framework)
- `test-driven-development` — TDD workflow completo
- `writing-plans`, `executing-plans` — Planificación estructurada
- `requesting-code-review`, `receiving-code-review` — Code review bidireccional
- `dispatching-parallel-agents` — Orquestación de agentes paralelos
- `subagent-driven-development` — Desarrollo delegado a sub-agentes
- `using-git-worktrees`, `finishing-a-development-branch` — Git avanzado
- `writing-skills` — Creación de skills
- `using-superpowers` — Meta-skill de uso del plugin

Nota: `systematic-debugging`, `verification-before-completion` y `brainstorming` ya son nativos de ai-framework. Superpowers incluye sus propias versiones que pueden coexistir.

Ver lista completa en el [repo](https://github.com/obra/superpowers#skills).
:::

---

### Episodic Memory

Búsqueda semántica de conversaciones pasadas. Cuando no recuerdas cómo resolviste algo hace dos semanas, esto lo encuentra.

```bash
/plugin install episodic-memory@superpowers-marketplace
```

::: tip Requiere Superpowers Marketplace
Si no lo tienes: `/plugin marketplace add obra/superpowers-marketplace`
:::

::: details Control de privacidad
Para excluir una conversación del índice:
```xml
<INSTRUCTIONS-TO-EPISODIC-MEMORY>DO NOT INDEX THIS CHAT</INSTRUCTIONS-TO-EPISODIC-MEMORY>
```
:::

---

### Spec-Kit

CLI para especificación de requirements. Genera specs estructuradas desde descripciones en lenguaje natural.

**Requisitos:** Python 3.11+, Git, [uv](https://docs.astral.sh/uv/)

::: code-group
```bash [Instalación persistente]
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

```bash [Uso sin instalar]
uvx --from git+https://github.com/github/spec-kit.git specify init mi-proyecto
```
:::

```bash
# Crear spec
specify spec "OAuth 2.0 con Google"

# Ver ayuda
specify --help
```

Docs completas: [github.com/github/spec-kit](https://github.com/github/spec-kit)

---

## Plugins oficiales de Anthropic

Anthropic mantiene un directorio de plugins que cambia frecuentemente.

```bash
# Explorar catálogo
/plugin
# → Seleccionar "Discover"

# Instalar desde catálogo oficial
/plugin install <nombre>@claude-plugin-directory
```

---

## Más skills

[skills.sh](https://skills.sh/) es un catálogo abierto de skills para agentes AI. Tiene skills para React, TypeScript, Stripe, Kubernetes, y más.

Consulta el catálogo cuando busques skills para tu stack. Muchos son compatibles con Claude Code.

---

## MCPs

Un MCP (Model Context Protocol) conecta Claude con servicios externos. Claude los invoca automáticamente cuando son relevantes para la tarea en curso.

### Configuración

Crea `.mcp.json` en la raíz de tu proyecto:

```json
{
  "mcpServers": {
    "nombre-del-mcp": {
      "type": "http",
      "url": "https://ejemplo.com/mcp"
    }
  }
}
```

MCPs locales (ejecutan un proceso):

```json
{
  "mcpServers": {
    "mi-mcp-local": {
      "command": "npx",
      "args": ["-y", "paquete-mcp@latest"]
    }
  }
}
```

Habilítalos en `.claude/settings.local.json`:

```json
{
  "enabledMcpjsonServers": ["nombre-del-mcp", "mi-mcp-local"]
}
```

Reinicia Claude Code para aplicar cambios.

### Tipos de MCPs

| Tipo | Configuración | Ejemplo |
|------|---------------|---------|
| HTTP | `type` + `url` | APIs remotas, documentación |
| Local | `command` + `args` | CLIs, herramientas del sistema |

### Dónde encontrar MCPs

- [MCP Hub](https://github.com/modelcontextprotocol) — Repositorio oficial del protocolo
- [Awesome MCP](https://github.com/punkpeye/awesome-mcp-servers) — Lista curada de servidores

---

## Presupuesto de contexto

::: warning Cada integración consume contexto
1-2 MCPs activos: ~5-10% del contexto. 4+ MCPs: 20-30%. Habilita solo lo que uses.
:::

---

**Siguiente paso**: [Changelog](./changelog.md)

---
::: info Última actualización
**Fecha**: 2026-03-11
:::
