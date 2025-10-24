# Quickstart: 30 Segundos a Productivo

::: tip Objetivo
Instalar el framework y ejecutar tu primera feature en 5 minutos.
:::

---

## Instalación (30 segundos)

### Paso 1: Install Plugin

```bash
/plugin marketplace add Dario-Arcos/ai-framework
/plugin install ai-framework@ai-framework
```

### Paso 2: Comienza en Tu Proyecto

```bash
cd /path/to/your/project
claude
```

::: tip Auto-Install
El framework se auto-instala en la primera sesión.
:::

### Paso 3: Restart Claude Code

::: warning Importante
Sal y reabre Claude Code para cargar el framework. Este paso es necesario para que comandos y agentes estén disponibles.
:::

**Done.** 30 segundos.

---

## Post-Instalación (2 minutos)

### Initialize Project Context

```bash
/ai-framework:utils:project-init
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
/ai-framework:utils:setup-dependencies
```

Instala tools opcionales (notifications, formatters). Responde `S` para proceder.

---

## Actualizar el Plugin

```
/plugin marketplace update ai-framework
```

Reinicia Claude Code después de actualizar.

::: tip Importante
Mantente actualizado para acceder a nuevos comandos, agentes y mejoras de seguridad.
:::

---

## Primera Feature (5 minutos)

### Quick Path

```bash
/ai-framework:SDD-cycle:speckit.specify "add user email validation"
/ai-framework:SDD-cycle:speckit.clarify
/ai-framework:SDD-cycle:speckit.plan
/ai-framework:SDD-cycle:speckit.tasks
/ai-framework:SDD-cycle:speckit.implement
```

::: tip Recomendación Importante
El paso `clarify` previene horas de refactor. Vale la pena los 2 minutos que toma.
:::

### Create PR

```bash
/ai-framework:git-github:commit "feat: add email validation"
/ai-framework:git-github:pullrequest develop
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
