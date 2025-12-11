# Inicio Rápido: 30 Segundos a Productivo

::: tip Objetivo
Instalar el framework y ejecutar tu primera feature en 5 minutos.
:::

---

## Instalación (30 segundos)

### Paso 1: Agregar al Marketplace

```
/plugin marketplace add Dario-Arcos/ai-framework
```

### Paso 2: Habilitar Plugin

```
/plugin enable ai-framework@ai-framework
```

### Paso 3: Actualizar Plugin (cuando sea necesario)

**Actualización rápida** (cambios menores):
```
/plugin marketplace update ai-framework
```

**Actualización limpia** (recomendada en cambios de versión):
```
/plugin marketplace remove ai-framework
/plugin marketplace add Dario-Arcos/ai-framework
/plugin enable ai-framework@ai-framework
```

::: warning Por qué reinstalar completamente
El comando `marketplace update` solo sincroniza archivos nuevos pero no elimina componentes obsoletos. Remover y re-agregar el marketplace garantiza un estado limpio sin residuos de versiones anteriores.
:::

::: tip Importante
Después de habilitar o actualizar, reinicia Claude Code para cargar el framework.
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
/plugin disable ai-framework@ai-framework
```

**Re-habilitar después de deshabilitar:**
```bash
/plugin enable ai-framework@ai-framework
```

**Desinstalar completamente:**
```bash
/plugin uninstall ai-framework@ai-framework
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
| **Plugin no aparece**    | `/plugin list` — debe aparecer ai-framework |

---

## Siguientes Pasos

**Documentación completa:**

- [Commands Guide](./commands-guide.md) — Completo conjunto de comandos documentados ([ver todos](./commands-guide))
- [Agents Guide](./agents-guide.md) — Extensa biblioteca de agentes especializados ([ver todos](./agents-guide))
- [AI-First Workflow](./ai-first-workflow.md) — Workflows completos
- [MCP Servers](./mcp-servers.md) — Extend capabilities

**Requisitos:**

- ✅ [Claude Code CLI](https://docs.claude.com/en/docs/claude-code/installation) (requerido)
- ✅ [Git](https://git-scm.com/downloads) (requerido)
- ✅ [Python 3.8+](https://www.python.org/downloads/) (requerido)
- ⚠️ [GitHub CLI](https://cli.github.com/) (recomendado para comandos git/github)

---

::: info Última Actualización
**Fecha**: 2025-12-11 | **Versión**: 4.2.0
:::
