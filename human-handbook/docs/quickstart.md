# Inicio Rápido: 30 Segundos a Productivo

::: tip Objetivo
Instalar el framework y ejecutar tu primera feature en 5 minutos.
:::

---

## Instalación (30 segundos)

### Paso 1: Agregar el Marketplace

```
/plugin marketplace add Dario-Arcos/ai-framework-marketplace
```

### Paso 2: Instalar el Plugin

```
/plugin install ai-framework@ai-framework-marketplace
```

### Paso 3: Actualizar Plugin (cuando sea necesario)

**Actualizar el plugin (2 pasos):**
```bash
# 1. Sincronizar el marketplace con la versión remota
/plugin marketplace update ai-framework-marketplace

# 2. Actualizar el plugin
/plugin update ai-framework@ai-framework-marketplace
```

::: warning Importante
El paso 1 es necesario porque Claude Code no sincroniza automáticamente los marketplaces de terceros. Sin este paso, `/plugin update` usará la versión cacheada localmente.
:::

**Actualización limpia** (si los pasos anteriores no funcionan):
```bash
/plugin marketplace remove ai-framework-marketplace
/plugin marketplace add Dario-Arcos/ai-framework-marketplace
/plugin install ai-framework@ai-framework-marketplace
```

::: tip Reinicio requerido
Después de instalar o actualizar, reinicia Claude Code para aplicar los cambios.
:::

### Paso 4: Comienza en Tu Proyecto

```bash
cd /path/to/your/project
claude
```

::: tip Instalación Automática
El framework se auto-instala en la primera sesión.
:::

**Listo.** 30 segundos.

---

## Gestión de Plugins

::: tip Comandos Adicionales
Operaciones útiles después de la instalación inicial.
:::

**Deshabilitar temporalmente:**
```bash
/plugin disable ai-framework@ai-framework-marketplace
```

**Re-habilitar después de deshabilitar:**
```bash
/plugin enable ai-framework@ai-framework-marketplace
```

**Desinstalar completamente:**
```bash
/plugin uninstall ai-framework@ai-framework-marketplace
```

**Explorar plugins disponibles (modo interactivo):**
```bash
/plugin
```

::: warning Recuerda
Reinicia Claude Code después de cualquier cambio en plugins (enable/disable/update).
:::

---

## Post-Instalación (2 minutos)

### Inicializar Contexto del Proyecto

```bash
/project-init
```

Analiza tu codebase y genera reglas team-shared en `docs/claude-rules/` (tracked).

**Output esperado:**

```text
✅ Generated docs/claude-rules/ (tracked):
   • stack.md, patterns.md, architecture.md

📋 Synced to .claude/rules/ (local working copy)

💡 Rules flow:
   • docs/claude-rules/ → commit to git (team-shared)
   • .claude/rules/ → auto-synced on session start
```

### Instalar Dependencias (Opcional)

```bash
/setup-dependencies
```

Instala tools opcionales (notifications, formatters). Responde `S` para proceder.

### Notificaciones de Escritorio (Recomendado)

El framework envía notificaciones cuando Claude necesita tu atención:

**Cuándo notifica:**
- 🔒 Claude espera tu aprobación (permissions, confirmations)
- ✅ Tarea completada (con duración)
- 🔴 Bloqueado esperando tu input

**Instalación** (incluida en `/setup-dependencies`):
```bash
brew install terminal-notifier  # macOS only
```

**Beneficio**: Trabaja en otra ventana, recibe alert cuando Claude te necesita.

::: tip macOS Only
Notifications requieren macOS. En Linux/Windows, Claude Code UI muestra estado.
:::

### Variables de Entorno (Opcional)

El template incluye configuración optimizada de tokens en `settings.json`:

| Variable | Valor | Propósito |
|----------|-------|-----------|
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 64000 | Máximo de tokens de salida |
| `MAX_THINKING_TOKENS` | 31999 | Budget de razonamiento (ultrathink) |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` | 30000 | Budget para skills visibles |

::: tip Sobrescribir configuración
Para usar valores por defecto de Claude Code, deja el campo `"env": {}` vacío en `.claude/settings.local.json`.
:::

---

## Primera Funcionalidad (5 minutos)

### Ruta Rápida

```bash
/speckit.specify "add user email validation"
/speckit.clarify
/speckit.plan
/speckit.tasks
/speckit.implement
```

::: tip Recomendación Importante
El paso `clarify` previene horas de refactor. Vale la pena los 2 minutos que toma.
:::

### Crear PR

```bash
/git-commit "feat: add email validation"
/git-pullrequest develop
```

Security review automático ejecuta antes de crear PR.

---

## Solución de Problemas

| Problema                 | Solución                                    |
| ------------------------ | ------------------------------------------- |
| **Comandos no visibles** | Reinicia Claude Code                        |
| **Hooks no ejecutan**    | Verifica Python 3.8+: `python3 --version`   |
| **Plugin no aparece**    | `/plugin` — debe aparecer ai-framework en el marketplace |
| **Update no actualiza**  | Ejecuta primero `/plugin marketplace update ai-framework-marketplace` |

---

## Siguientes Pasos

**Documentación completa:**

- [Commands Guide](./commands-guide.md) — Completo conjunto de comandos documentados ([ver todos](./commands-guide))
- [Agents Guide](./agents-guide.md) — Extensa biblioteca de agentes especializados ([ver todos](./agents-guide))
- [AI-First Workflow](./ai-first-workflow.md) — Workflows completos
- [Integrations](./integrations.md) — Plugins & MCPs

**Requisitos:**

- ✅ [Claude Code CLI](https://docs.claude.com/en/docs/claude-code/installation) (requerido)
- ✅ [Git](https://git-scm.com/downloads) (requerido)
- ✅ [Python 3.8+](https://www.python.org/downloads/) (requerido)
- ⚠️ [GitHub CLI](https://cli.github.com/) (recomendado para comandos git/github)

---

::: info Última Actualización
**Fecha**: 2025-12-20 | **Versión**: 5.0.0
:::
