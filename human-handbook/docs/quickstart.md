# Inicio rápido

Esta guía te lleva de cero a usar AI Framework en tu proyecto: instalar el plugin, configurar tu entorno y ejecutar tu primer comando.

> **Antes de empezar**: lee [Por qué AI Framework](./why-ai-framework.md) para entender qué hace el framework.

---

## Requisitos

- [Claude Code CLI](https://docs.claude.com/en/docs/claude-code/installation)
- [Git](https://git-scm.com/downloads)
- [Python 3.8+](https://www.python.org/downloads/) — requerido por los hooks del plugin
- [Node.js 18+](https://nodejs.org/) — requerido por `agent-browser` (auto-instalación vía npm/brew)
- [GitHub CLI](https://cli.github.com/) (opcional, para `/pull-request` y comandos git)

---

## Instalación

::: code-group
```bash [Primera vez]
# Agregar marketplace
/plugin marketplace add Dario-Arcos/ai-framework-marketplace

# Instalar plugin
/plugin install ai-framework@ai-framework-marketplace
```

```bash [Actualizar]
# Sincronizar marketplace (necesario, no se hace automático)
/plugin marketplace update ai-framework-marketplace

# Actualizar plugin
/plugin update ai-framework@ai-framework-marketplace
```

```bash [Reinstalar limpio]
/plugin marketplace remove ai-framework-marketplace
/plugin marketplace add Dario-Arcos/ai-framework-marketplace
/plugin install ai-framework@ai-framework-marketplace
```
:::

---

## Después de instalar {#post-install}

::: warning Reinicio obligatorio
Después de instalar o actualizar, **cierra Claude Code, espera ~10 segundos y abre una nueva sesión**. Los hooks necesitan registrarse y ejecutarse al menos una vez.
:::

### Qué pasa en la primera sesión

Al iniciar Claude Code después de instalar el plugin, los hooks ejecutan automáticamente:

1. **`session-start.py`** — Sincroniza templates del framework al proyecto (instantáneo)
2. **`agent-browser-check.py`** — Instala `agent-browser` CLI + navegador Chromium en background (~30-60s)

Los hooks son silenciosos cuando todo funciona — solo inyectan mensajes cuando requieren tu atención.

Además, el framework inyecta **spinner tips** personalizados via `spinnerTipsOverride` en `settings.json` — durante la ejecución verás recordatorios sobre `/project-init`, `/commit`, `/scenario-driven-development` y `/verification-before-completion` mezclados con los tips default de Claude Code.

::: tip Flujo recomendado de primera instalación
1. Instala el plugin
2. Cierra Claude Code
3. Espera **~10 segundos** (permite que el proceso termine de registrarse)
4. Abre nueva sesión — la instalación de `agent-browser` ocurre en background
5. Trabaja normalmente. En la siguiente sesión, la skill se activa automáticamente
:::

::: details ¿Por qué esperar antes de reiniciar?
Claude Code necesita unos segundos para registrar los hooks del plugin en su configuración interna. Si abres una nueva sesión inmediatamente, los hooks pueden no haberse registrado aún y no ejecutarán.
:::

---

## Compatibilidad de plataformas {#platforms}

La plataforma principal es **macOS**. Linux funciona completamente. Windows es compatible con Git for Windows.

### Hooks por plataforma

| Hook | Evento | macOS | Linux | Windows |
|------|--------|:-----:|:-----:|:-------:|
| `session-start.py` | SessionStart | ✅ | ✅ | ✅ |
| `agent-browser-check.py` | SessionStart | ✅ | ✅ | ✅ |
| `notify.sh` | Stop, Notification | ✅ | ➖ | ➖ |
| `sdd-test-guard.py` | PreToolUse | ✅ | ✅ | ✅ |
| `sdd-auto-test.py` | PostToolUse | ✅ | ✅ | ✅ |
| `teammate-idle.py` | TeammateIdle | ✅ | ✅ | ✅ |
| `task-completed.py` | TaskCompleted | ✅ | ✅ | ✅ |

::: details Detalles por hook

**session-start.py** — Python puro (stdlib), 100% cross-platform. Sincroniza templates y `.gitignore`.

**agent-browser-check.py** — Usa `bash -c` para lanzar procesos en background. Cross-platform: Git for Windows provee `bash` en Windows.

**notify.sh** — Notificaciones nativas macOS (`afplay` para sonido, `osascript` para visual). En Linux y Windows se salta silenciosamente (`exit 0`). No afecta la funcionalidad del framework.

**sdd-test-guard.py** — Valida que ediciones a archivos de test no reduzcan assertions cuando los tests están fallando (protección contra reward hacking). Cross-platform: file locking gracefully degradado en Windows, paths temporales portables.

**sdd-auto-test.py** — Ejecuta tests en background después de cada edición a archivos fuente. Cross-platform: file locking gracefully degradado en Windows, paths temporales portables.

**teammate-idle.py** — Safety net para ralph-orchestrator. Cross-platform: file locking gracefully degradado en Windows.

**task-completed.py** — Quality gates para validar tareas completadas. Cross-platform: file locking gracefully degradado en Windows.
:::

### Windows

::: info Notas para Windows
- **Requisito**: [Git for Windows](https://git-scm.com/download/win) (Git Bash ejecuta los hooks)
- **File locking**: Degradado gracefully — `fcntl` se omite en Windows sin afectar funcionalidad en uso single-user
- **Statusline**: Usa Python embebido en el script (no requiere `jq`)
- **Notificaciones**: No disponibles (requieren macOS)
:::

Para desactivar la auto-instalación de `agent-browser` en entornos donde falla:

```bash
export AI_FRAMEWORK_SKIP_BROWSER_INSTALL=1
```

Después puedes instalar `agent-browser` manualmente:

::: code-group
```bash [macOS (Homebrew)]
brew install agent-browser
```

```bash [Linux / Windows (npm)]
npm install -g agent-browser
agent-browser install
```
:::

---

## Inicializar proyecto

```bash
cd /tu/proyecto
claude
```

En la primera sesión, ejecuta:

```bash
/project-init
```

Genera reglas de contexto en `.claude/rules/` — Claude las carga automáticamente en cada sesión.

::: details Gestión de plugins
```bash
# Deshabilitar temporalmente
/plugin disable ai-framework@ai-framework-marketplace

# Re-habilitar
/plugin enable ai-framework@ai-framework-marketplace

# Desinstalar
/plugin uninstall ai-framework@ai-framework-marketplace

# Explorar plugins disponibles
/plugin
```
Reinicia Claude Code después de cualquier cambio.
:::

---

## Usar el framework

Describe lo que quieres en lenguaje natural:

```
"Implementa validación de email en el formulario de registro"
```

Claude activa automáticamente los skills relevantes (SDD, code review, etc).

Para commits y PRs:

```bash
/commit "feat: add email validation"
/pull-request develop
```

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| Comandos/skills no visibles | Cierra Claude Code, espera ~10s, abre nueva sesión |
| Hooks no ejecutan | Verifica Python 3.8+: `python3 --version` |
| Plugin no aparece | `/plugin` → selecciona "Discover" |
| Update no funciona | Ejecuta primero `/plugin marketplace update` |
| `agent-browser` no funciona | Revisa log en `/tmp/agent-browser-install.log`. Si falló: `npm install -g agent-browser` |
| `agent-browser install failed` en sesión | Verifica Node.js 18+: `node --version`. Instala manualmente con `npm install -g agent-browser` |
| Notificaciones no suenan | Solo disponibles en macOS. Verifica permisos de Script Editor en System Settings → Privacy |
| Hook falla en Windows | Verifica Git for Windows instalado. Los hooks SDD funcionan nativamente. Para `agent-browser`: `npm install -g agent-browser` |

::: details Ver logs de instalación de agent-browser
```bash
# Log de instalación (primera vez)
cat /tmp/agent-browser-install.log

# Log de sincronización de skill
cat /tmp/agent-browser-skill-sync.log

# Log de auto-update (cada 24h)
cat /tmp/agent-browser-update.log
```
:::

---

## Siguientes pasos

- [Skills Guide](./skills-guide.md) — Los 24 skills del framework
- [Agents Guide](./agents-guide.md) — 6 agentes especializados
- [Integrations](./integrations.md) — Plugins, MCPs y herramientas externas

**Siguiente paso**: [Workflow AI-first](./ai-first-workflow.md)

---

::: info Última actualización
**Fecha**: 2026-02-13
:::
