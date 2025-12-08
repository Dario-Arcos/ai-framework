# MCP Servers

::: tip ¿Qué es MCP?
Model Context Protocol conecta Claude Code con herramientas externas (databases, APIs, browsers, docs) sin escribir código custom. Extend capabilities on-demand.
:::

---

## Servidores Disponibles

| Server              | Propósito                                    | Package/URL                      | Estado Default | Context Cost |
| ------------------- | -------------------------------------------- | -------------------------------- | -------------- | ------------ |
| **playwright**      | Browser automation, E2E testing, screenshots | `@playwright/mcp`                | ❌ No instalado | Alto (~15 tools) |
| **shadcn**          | Shadcn/ui v4 component library integration   | `@jpisnice/shadcn-ui-mcp-server` | ❌ No instalado | Medio (~7 tools) |
| **mobile-mcp**      | Mobile automation: iOS/Android debugging     | `@mobilenext/mobile-mcp`         | ❌ No instalado | Alto (~20 tools) |
| **maestro**         | Mobile E2E testing: YAML flows, AI assertions| `maestro mcp` (CLI built-in)     | ❌ No instalado | Medio (~10 tools) |
| **episodic-memory** | Local episodic memory (via plugin)           | `superpowers-marketplace`        | ❌ No instalado | Medio (~4 tools) |

**Por defecto:** Zero MCPs instalados (opt-in explícito)
**Instalación:** Copiar `.claude/.mcp.json.template` → `.mcp.json` (proyecto)
**Activación:** Habilitar en `.claude/settings.local.json`

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

**Por defecto:** Zero MCPs instalados (optimización de contexto).

**Flujo de activación:** Template → Copiar → Habilitar → Restart

### Ejemplo: Activar Playwright + Shadcn

**1. Copiar template al proyecto:**

```bash
cp .claude/.mcp.json.template .mcp.json
```

**2. Habilitar en `.claude/settings.local.json`:**

```json
{
  "enabledMcpjsonServers": ["playwright", "shadcn"]
}
```

**3. Restart:** `Ctrl+D` → `claude`

**4. Verificar:** `/mcp` debe mostrar:
```
playwright: ✓ Connected
shadcn: ✓ Connected
```

::: tip Context-Aware Activation
Solo habilita MCPs que necesitas para tu proyecto actual. Puedes cambiar `enabledMcpjsonServers` cuando cambies de proyecto.
:::

::: details Ver .mcp.json.template
El template incluye 4 servidores preconfigurados:
- `playwright`: Browser automation (web)
- `shadcn`: Shadcn/ui components
- `mobile-mcp`: Mobile automation (iOS/Android)
- `maestro`: Mobile E2E testing (YAML flows)

Incluye descripción por servidor (`$description`).
:::

---

## Agregar Nuevo Servidor

**Workflow:** Copiar template → Agregar custom → Habilitar → Restart

::: details Ejemplo: Agregar GitHub Server

**1. Copiar template (si no existe `.mcp.json`):**

```bash
cp .claude/.mcp.json.template .mcp.json
```

**2. Agregar servidor en `.mcp.json`:**

```json
{
  "mcpServers": {
    "playwright": { ... },  // servidores del template
    "shadcn": { ... },
    "github": {  // tu servidor custom
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
```

**3. Habilitar en `.claude/settings.local.json`:**

```json
{
  "enabledMcpjsonServers": ["github"]
}
```

**4. Restart:** `Ctrl+D` → `claude`

:::

## Catálogo & Recursos

**Registries:**

- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [mcpservers.org](https://mcpservers.org)
- [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/mcp)

**Recomendados:** `filesystem` · `github` · `memory` · `postgres` · `context7` · `brave-search`

---

## Uso con Framework

**Playwright:** Browser automation via `design-review` agent (screenshots automáticos)

**Shadcn:** Component library integration para desarrollo UI con shadcn/ui v4

**Mobile-MCP + Maestro:** Mobile testing via `mobile-test-generator` agent

### Mobile Testing (React Native, Expo, Flutter)

::: tip Cuándo usar cada uno
- **mobile-mcp**: Debugging interactivo, exploración UI, screenshots
- **maestro**: Test suites E2E, CI/CD, auto-healing tests
:::

**Requisitos:**

| Herramienta | Requisito | Instalación |
|-------------|-----------|-------------|
| mobile-mcp | Node.js 22+ | Automático via npx |
| mobile-mcp (iOS) | Xcode CLI Tools | `xcode-select --install` |
| mobile-mcp (Android) | Android Platform Tools | Android Studio |
| maestro | Java 17+ | `java --version` |
| maestro CLI | Latest | `curl -fsSL "https://get.maestro.mobile.dev" \| bash` |

**Activación para proyecto mobile:**

```json
{
  "enabledMcpjsonServers": ["mobile-mcp", "maestro"]
}
```

**Expo/React Native:**
- Usar Development Builds (no Expo Go) para E2E testing
- Maestro usa `openLink` para deep links Expo
- Preferir `testID` sobre text matching para estabilidad

::: details Ejemplo: Debugging con mobile-mcp
```
User: "El botón de login no responde"

Claude usa:
1. mobile_list_available_devices → iPhone 15 Simulator
2. mobile_launch_app → inicia app
3. mobile_take_screenshot → captura visual
4. mobile_list_elements_on_screen → árbol de accesibilidad
5. Identifica: botón tiene enabled=false
6. Reporta: "Botón deshabilitado, revisar validación"
```
:::

::: details Ejemplo: Generar tests Maestro
```yaml
# flows/auth/login.yaml
appId: com.myapp
---
- launchApp
- tapOn: "Email"
- inputText: "user@example.com"
- tapOn: "Password"
- inputText: "SecurePass123"
- tapOn: "Sign In"
- assertVisible: "Welcome"
```

Ejecutar: `maestro test flows/auth/`
:::

---

## Troubleshooting

::: details Server No Aparece

**Check:**

1. `.mcp.json` existe (copiado desde `.claude/.mcp.json.template`)
2. Server está en `enabledMcpjsonServers` en `.claude/settings.local.json`
3. Restart después de cambios

**Debug:**
```bash
# Verificar que template fue copiado
ls -la .mcp.json

# Verificar servidores habilitados
cat .claude/settings.local.json | grep enabledMcpjsonServers
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

## Mejores Prácticas

::: tip Minimalismo
Comienza con 2-3 servers. Cada uno consume recursos y aumenta startup time. Agrega más solo cuando tengas necesidad clara.
:::

::: warning Security
**Nunca** commits tokens en `.mcp.json`. Usa env vars del sistema con placeholders `${ }`
:::

---

---

::: info Última Actualización
**Fecha**: 2025-12-07 | **Cambios**: Mobile testing (mobile-mcp + maestro) integration
:::
