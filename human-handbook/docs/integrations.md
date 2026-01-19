# Integrations

::: tip ¿Qué son las Integraciones?
Plugins oficiales y MCPs que extienden Claude Code con herramientas externas (databases, APIs, browsers, docs). Un **plugin** es un paquete completo (puede incluir MCP + comandos + agentes), mientras que un **MCP** es solo un servidor de herramientas.
:::

---

## Plugins Oficiales (Recomendado)

Anthropic mantiene un directorio de plugins oficiales. **Instalación con un comando:**

```bash
/plugin install {name}@claude-plugin-directory
```

O navegar: `/plugin` → `Discover`

### Plugins First-Party Disponibles

| Plugin | Propósito | Comando |
|--------|-----------|---------|
| **context7** | Real-time library docs | `/plugin install context7@claude-plugin-directory` |
| **playwright** | Browser automation, E2E | `/plugin install playwright@claude-plugin-directory` |
| **linear** | Issue tracking | `/plugin install linear@claude-plugin-directory` |
| **github** | GitHub integration | `/plugin install github@claude-plugin-directory` |
| **gitlab** | GitLab integration | `/plugin install gitlab@claude-plugin-directory` |
| **firebase** | Firebase backend | `/plugin install firebase@claude-plugin-directory` |
| **supabase** | Supabase backend | `/plugin install supabase@claude-plugin-directory` |
| **stripe** | Payments | `/plugin install stripe@claude-plugin-directory` |
| **slack** | Messaging | `/plugin install slack@claude-plugin-directory` |
| **asana** | Project management | `/plugin install asana@claude-plugin-directory` |

::: tip Ventajas de Plugins Oficiales
- Mantenidos por Anthropic/partners
- Actualizaciones automáticas
- Instalación limpia sin configuración manual
:::

**Catálogo completo:** [github.com/anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)

---

## Browser Automation (agent-browser)

::: tip Auto-instalación
`agent-browser` se instala **automáticamente** al iniciar Claude Code si no está presente. No requiere acción manual.
:::

### ¿Qué es agent-browser?

CLI de browser automation basado en Playwright, optimizado para tareas web rápidas:
- Navegación y búsquedas
- Llenado de formularios
- Screenshots
- Extracción de datos

**Ventaja sobre WebFetch/WebSearch:** No se bloquea, no trunca contenido, puede interactuar con páginas dinámicas.

### Comportamiento del Hook

Al iniciar cada sesión, el hook `agent-browser-check` verifica e instala automáticamente:

| Estado | Mensaje | Acción |
|--------|---------|--------|
| ✓ Instalado | `agent-browser: ✓ Installed` | Usa agent-browser para tareas web |
| ⏳ Instalando | `agent-browser: ⏳ Installing in background` | Usa WebFetch mientras instala (~30s) |
| ⚠ Skipped | `agent-browser: ⚠ Skipped` | Variable de entorno activa |
| ✗ Falló | `agent-browser: ✗ Install failed` | Usa WebFetch como fallback |

### Desactivar Auto-instalación

Si no deseas la instalación automática (CI sin browser, entorno restringido):

```bash
export AI_FRAMEWORK_SKIP_BROWSER_INSTALL=1
```

### Logs

El hook registra cada ejecución para trazabilidad:

```
.claude/logs/YYYY-MM-DD/agent-browser-check.jsonl
```

```json
{"timestamp": "2026-01-19T12:59:45", "hook": "agent-browser-check", "status": "installed", "details": "agent-browser already available"}
```

### Instalación Manual (si necesario)

```bash
npm install -g agent-browser
agent-browser install  # Descarga Chromium (~150MB)
```

::: warning Primera instalación
La primera instalación descarga Chromium (~150MB). En conexiones lentas puede tomar 1-2 minutos.
:::

---

## MCPs Adicionales (Mobile)

Para desarrollo mobile, usamos MCPs que **no tienen plugin oficial**. Estos requieren configuración manual.

| Server | Propósito | Instalación |
|--------|-----------|-------------|
| **mobile-mcp** | Automation iOS/Android, debugging UI | Automática (npx) ✅ |
| **maestro** | E2E testing mobile, YAML flows | **Manual requerida** ⚠️ |

::: warning Maestro requiere instalación previa
A diferencia de `mobile-mcp` que se auto-instala via `npx`, **Maestro MCP requiere tener el CLI instalado globalmente**. Sin esto, el MCP fallará silenciosamente al iniciar Claude Code.
:::

### Instalar Maestro CLI (requisito previo)

```bash
# Opción 1: curl (recomendado)
curl -Ls "https://get.maestro.mobile.dev" | bash

# Opción 2: Homebrew
brew tap mobile-dev-inc/tap && brew install maestro
```

**Verificar instalación:**
```bash
maestro --version
# Debe mostrar: Maestro CLI x.x.x
```

::: tip ¿Por qué esta diferencia?
- `mobile-mcp`: Paquete npm, se descarga automáticamente con `npx`
- `maestro`: CLI binario con dependencias de Java, requiere instalación del sistema
:::

### Activar MCPs Mobile

**1. Copiar template:**

```bash
cp .claude/.mcp.json.template .mcp.json
```

**2. Habilitar en `.claude/settings.local.json`:**

```json
{
  "enabledMcpjsonServers": ["mobile-mcp", "maestro"]
}
```

**3. Restart:** `Ctrl+D` → `claude`

**4. Verificar:** `/mcp` debe mostrar servidores conectados.

::: details Troubleshooting: Maestro MCP no conecta
Si `/mcp` no muestra maestro como conectado:

1. **Verificar CLI instalado:** `which maestro` debe retornar una ruta
2. **Verificar versión:** `maestro --version`
3. **Verificar Java:** `java --version` (requiere Java 17+)
4. **Probar MCP manual:** `maestro mcp` (debe iniciar sin errores)

Si `maestro mcp` falla, reinstalar el CLI.
:::

---

## ⚠️ Context Budget

::: warning Impacto en Contexto
Cada MCP/plugin activo consume contexto. Habilita solo lo necesario para tu proyecto actual.
:::

**Consumo estimado:**
- 1-2 MCPs: 5-10% context
- 4+ MCPs: 20-30% context

**Síntomas de overflow:** Respuestas lentas, pérdida de contexto, degradación de razonamiento.

---

## Mobile Testing (React Native, Expo, Flutter)

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
**Para plugins oficiales:**
- Verificar instalación: `/plugin`
- Reinstalar: `/plugin install {name}@claude-plugin-directory`

**Para MCPs del template:**
1. `.mcp.json` existe (copiado desde template)
2. Server en `enabledMcpjsonServers`
3. Restart después de cambios
:::

::: details Environment Variables
**Sistema (recomendado):**
```bash
export GITHUB_TOKEN="your_token"
claude
```

**En `.mcp.json`:**
```json
{ "env": { "TOKEN": "${TOKEN}" } }
```
:::

---

## Mejores Prácticas

::: tip Minimalismo
Comienza con 1-2 plugins/MCPs. Agrega más solo cuando tengas necesidad clara.
:::

::: warning Security
**Nunca** commits tokens en archivos. Usa env vars del sistema.
:::

---

::: info Última Actualización
**Fecha**: 2026-01-19 | **Cambios**: Añadida sección Browser Automation (agent-browser) con auto-instalación
:::
