# Integraciones

Claude Code se extiende con plugins y MCPs. Esta guía cubre los que recomendamos.

---

## Plugins recomendados

### Superpowers

Skills profesionales: TDD, debugging sistemático, code review, worktrees. Mantenido por [obra](https://github.com/obra/superpowers).

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

::: details Skills incluidos
- `test-driven-development` — TDD workflow completo
- `systematic-debugging` — Debugging metódico
- `verification-before-completion` — Verificación antes de entregar
- `writing-plans`, `executing-plans` — Planificación estructurada
- `requesting-code-review`, `receiving-code-review` — Code review bidireccional
- `using-git-worktrees`, `finishing-a-development-branch` — Git avanzado

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

## MCPs

Un MCP (Model Context Protocol) conecta Claude con servicios externos. Claude los invoca automáticamente cuando son útiles.

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

## Context budget

::: warning Cada integración consume contexto
1-2 MCPs activos: ~5-10% del contexto. 4+ MCPs: 20-30%. Habilita solo lo que uses.
:::

---

::: info Última actualización
**Fecha**: 2026-01-31
:::
