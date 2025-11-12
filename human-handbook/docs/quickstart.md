# Quickstart: 30 Segundos a Productivo

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

```
/plugin marketplace update ai-framework
```

::: tip Importante
Después de habilitar o actualizar, reinicia Claude Code para cargar el framework.
:::

### Paso 4: Comienza en Tu Proyecto

```bash
cd /path/to/your/project
claude
```

::: tip Auto-Install
El framework se auto-instala en la primera sesión.
:::

**Done.** 30 segundos.

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

### Initialize Project Context

```bash
/project-init
```

Analiza tu codebase y configura recomendaciones de agentes.

**Output esperado:**

```text
✅ Project context initialized

Stack Detected: [Tu tech stack]
Recommended Agents: [Agents para tu proyecto]
Generated: .specify/memory/project-context.md
```

### Install Dependencies (Opcional)

```bash
/setup-dependencies
```

Instala tools opcionales (notifications, formatters). Responde `S` para proceder.

---

## Primera Feature (5 minutos)

### Quick Path

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

### Create PR

```bash
/git-commit "feat: add email validation"
/git-pullrequest develop
```

Security review automático ejecuta antes de crear PR.

---

## Troubleshooting

| Issue                    | Solution                                    |
| ------------------------ | ------------------------------------------- |
| **Comandos no visibles** | Restart Claude Code                         |
| **Hooks no ejecutan**    | Verify Python 3.8+: `python3 --version`     |
| **Plugin not appearing** | `/plugin list` — debe aparecer ai-framework |

---

## Next Steps

**Documentación completa:**

- [Commands Guide](./commands-guide.md) — Completo conjunto de comandos documentados ([ver todos](./commands-guide))
- [Agents Guide](./agents-guide.md) — Extensa biblioteca de agentes especializados ([ver todos](./agents-guide))
- [AI-First Workflow](./ai-first-workflow.md) — Workflows completos
- [MCP Servers](./mcp-servers.md) — Extend capabilities

**Requirements:**

- ✅ [Claude Code CLI](https://docs.claude.com/en/docs/claude-code/installation) (required)
- ✅ [Git](https://git-scm.com/downloads) (required)
- ✅ [Python 3.8+](https://www.python.org/downloads/) (required)
- ⚠️ [GitHub CLI](https://cli.github.com/) (recommended para git/github commands)

---

::: info Última Actualización
**Fecha**: 2025-10-23 | **Version**: 1.4.1
:::
