# Integrations

::: tip ¿Qué son las Integraciones?
Plugins, MCPs y CLIs que extienden Claude Code con herramientas externas.
:::

## Índice

| Tipo | Herramienta | Propósito |
|------|-------------|-----------|
| **Plugin** | [Superpowers](#superpowers-plugin) | Skills de desarrollo profesional (TDD, debugging, etc.) |
| **Plugin** | [Episodic Memory](#episodic-memory) | Búsqueda semántica de conversaciones |
| **Plugin** | [Anthropic Plugins](#plugins-anthropic) | Directorio oficial de plugins |
| **MCP** | [context7](#context7) | Documentación de librerías en tiempo real |
| **MCP** | [mobile-mcp](#mobile-mcp) | Automation iOS/Android |
| **MCP** | [maestro](#maestro) | E2E testing mobile |
| **CLI** | [agent-browser](#agent-browser) | Browser automation |
| **CLI** | [Spec-Kit](#spec-kit-cli) | Especificación de requirements |

---

# Plugins

## Superpowers (Plugin)

::: tip Recomendado
**Superpowers** provee skills de desarrollo profesional: TDD, debugging sistemático, code review, worktrees, y más.
:::

**Repositorio:** [github.com/obra/superpowers](https://github.com/obra/superpowers)

**Instalación:**
```bash
# 1. Agregar marketplace
/plugin marketplace add obra/superpowers-marketplace

# 2. Instalar superpowers
/plugin install superpowers@superpowers-marketplace
```

**Skills incluidos:**
- test-driven-development, systematic-debugging, verification-before-completion
- writing-plans, executing-plans
- requesting-code-review, receiving-code-review
- using-git-worktrees, finishing-a-development-branch
- Y más...

---

## Episodic Memory

Plugin del marketplace Superpowers para búsqueda semántica de conversaciones.

**Instalación:**
```bash
/plugin install episodic-memory@superpowers-marketplace
```

::: details Detalles
**¿Qué es?**
Búsqueda semántica local de tus conversaciones con Claude Code.

**Casos de uso:**
- Encontrar "¿Cómo resolvimos el bug de autenticación hace 2 semanas?"
- Rastrear evolución de decisiones técnicas
- Recuperar patrones de solución aplicados anteriormente

**Features:**
- Semantic Search: Búsqueda por significado, no solo keywords
- Offline: Todo local, sin servicios cloud
- Privacy: Control total sobre qué se indexa

**Control de Indexación:**
```xml
<INSTRUCTIONS-TO-EPISODIC-MEMORY>DO NOT INDEX THIS CHAT</INSTRUCTIONS-TO-EPISODIC-MEMORY>
```
:::

---

## Plugins Anthropic

Anthropic mantiene un directorio de plugins oficiales que se actualiza constantemente.

**Ver plugins disponibles:**
```bash
/plugin
# Seleccionar "Discover" para ver el catálogo completo
```

**Instalar un plugin:**
```bash
/plugin install <nombre>@claude-plugin-directory
```

---

# MCPs

Los siguientes MCPs están preconfigurados en `.claude/.mcp.json.template`:

## context7

Documentación de librerías y frameworks en tiempo real.

| Campo | Valor |
|-------|-------|
| Tipo | HTTP |
| URL | `https://mcp.context7.com/mcp` |
| Auth | No requerida |

**Uso:** Automático cuando consultas documentación de librerías.

---

## mobile-mcp

Automation para iOS y Android: UI debugging, accessibility trees, screenshots.

| Campo | Valor |
|-------|-------|
| Comando | `npx` |
| Args | `-y @mobilenext/mobile-mcp@latest` |
| Instalación | Automática (npx) |

**Requisitos:**
- Node.js 22+
- iOS: Xcode CLI Tools (`xcode-select --install`)
- Android: Android Platform Tools

---

## maestro

E2E testing mobile con YAML flows y AI assertions.

| Campo | Valor |
|-------|-------|
| Comando | `maestro` |
| Args | `mcp` |
| Instalación | **Manual requerida** |

**Instalación previa:**
```bash
curl -Ls "https://get.maestro.mobile.dev" | bash
```

**Verificar:**
```bash
maestro --version
```

**Requisitos:** Java 17+

---

## Activar MCPs

1. Copiar template:
```bash
cp .claude/.mcp.json.template .mcp.json
```

2. Habilitar en `.claude/settings.local.json`:
```json
{ "enabledMcpjsonServers": ["context7", "mobile-mcp", "maestro"] }
```

3. Restart: `Ctrl+D` → `claude`

---

# CLIs

## agent-browser

::: tip Auto-instalación
Se instala **automáticamente** al iniciar Claude Code.
:::

CLI de browser automation basado en Playwright con skill integrado.

**Funcionalidades:**
- Navegación y búsquedas
- Llenado de formularios
- Screenshots
- Extracción de datos

**Ventaja sobre WebFetch/WebSearch:** No se bloquea, no trunca contenido, puede interactuar con páginas dinámicas.

**Desactivar Auto-instalación:**
```bash
export AI_FRAMEWORK_SKIP_BROWSER_INSTALL=1
```

---

## Spec-Kit CLI

::: warning CLI Independiente
**Spec-Kit** es un CLI de especificación de requirements basado en Python. **NO es un plugin**.
:::

**Repositorio:** [github.com/github/spec-kit](https://github.com/github/spec-kit)

**Prerequisitos:**
- Python 3.11+
- Git
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes Python)

**Instalación persistente (recomendada):**
```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

**Uso sin instalación:**
```bash
uvx --from git+https://github.com/github/spec-kit.git specify init <proyecto>
```

**Comandos principales:**
```bash
# Inicializar proyecto
specify init mi-proyecto --ai claude

# Crear spec desde descripción
specify spec "OAuth 2.0 with Google"

# Ver ayuda
specify --help
```

Para documentación completa, ver el [README oficial](https://github.com/github/spec-kit#readme).

---

# Context Budget

::: warning Impacto en Contexto
Cada MCP/plugin activo consume contexto. Habilita solo lo necesario.
:::

**Consumo estimado:**
- 1-2 MCPs: 5-10% context
- 4+ MCPs: 20-30% context

---

::: info Última Actualización
**Fecha**: 2026-01-25 | **Cambios**: agent-browser movido a CLIs
:::
