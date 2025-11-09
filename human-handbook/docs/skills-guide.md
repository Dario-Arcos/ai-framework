# Guía de Expert Skills

::: tip ¿Qué son las Skills?
Capacidades especializadas que extienden Claude con conocimiento experto en dominios específicos. Se activan automáticamente según el contexto.
:::

---

## Skills Disponibles

| Skill | Tipo | Activación |
|-------|------|-----------|
| [claude-code-expert](#claude-code-expert) | 🔧 Development | Crear/modificar agents, commands, hooks, MCP |
| [browser-tools](#browser-tools) | 🌐 Web | Browser automation, testing, profiling, scraping |
| [skill-creator](#skill-creator) | 🏗️ Meta | Crear/actualizar skills |
| [core-memory-expert](#core-memory-expert) | 💾 Memory | Setup/config RedPlanet Core memory |
| [algorithmic-art](#algorithmic-art) | 🎨 Creative | Arte algorítmico, p5.js, flow fields |

::: details Superpowers Skills (Integración Completa)
**Testing:** test-driven-development, condition-based-waiting, testing-anti-patterns

**Debugging:** systematic-debugging, root-cause-tracing, verification-before-completion, defense-in-depth

**Collaboration:** brainstorming, writing-plans, executing-plans, dispatching-parallel-agents, requesting-code-review, receiving-code-review, using-git-worktrees, finishing-a-development-branch, subagent-driven-development

**Meta:** sharing-skills, testing-skills-with-subagents, using-superpowers

[Ver documentación completa de superpowers →](https://github.com/obra/superpowers)
:::

---

## claude-code-expert

::: tip Tipo: Development Tool
Genera componentes Claude Code production-ready con validación automática (6 quality gates: syntax, security, logic, constitutional, integration, production).
:::

**Proceso:** WebFetch docs oficiales → Analiza patrones proyecto → Genera componente → Valida automáticamente

::: details Ejemplos de Uso

```bash
# Agent especializado
"Crea un agente para optimización de PostgreSQL"

# Comando workflow
"Agrega comando para migraciones de schema"

# Hook
"Implementa hook que valide commit messages"

# MCP server
"Integra Notion vía MCP para docs"
```

:::

**Genera:** Agents, Commands, Hooks, MCP Servers

---

## skill-creator

::: tip Tipo: Meta-Skill
Proceso guiado de 6 pasos para crear skills personalizadas siguiendo best practices.
:::

**Workflow:**

1. **Validación** - Define problema, audiencia, verifica duplicados
2. **Recursos** - Scripts, referencias, assets necesarios
3. **Estructura** - `python scripts/init_skill.py skill-name`
4. **Edición** - Frontmatter, descripción, workflow, ejemplos
5. **Validación** - `python scripts/validate_skill.py skill-name`
6. **Empaquetado** - `python scripts/package_skill.py skill-name`

::: details Ejemplos de Uso

```bash
# Framework específico
"Crea skill para desarrollo con Astro.js"

# Integración externa
"Skill para integración con Jira"

# Análisis
"Skill para performance web con Lighthouse"
```

:::

**Genera:** `skills/skill-name/` con SKILL.md + scripts + referencias + assets

---

## browser-tools

::: tip Tipo: Web Tool
Control Chrome/Chromium via CDP para testing, profiling, scraping, debugging. Puppeteer API completo, zero context overhead.
:::

**Capacidades:** E2E testing, network interception, performance profiling, coverage analysis, multi-tab orchestration, web scraping

**Platform:** macOS only (Chrome paths específicos, rsync)

**Setup:** `cd skills/browser-tools/tools && npm install` (una vez)

**Tools:** start.js, nav.js, eval.js, screenshot.js, stop.js

::: danger CRITICAL
**NUNCA usar `killall Chrome`** — cierra TODAS tus sesiones. Usa `./tools/stop.js` (solo cierra debugging instance en puerto 9223).
:::

**Cuándo usar:** Context budget crítico, E2E testing ad-hoc, profiling programático, scraping complejo

---

## core-memory-expert

::: tip Tipo: Memory System
Setup/config RedPlanet Core como memory layer. Cloud deployment (<2min) o self-hosted (Docker).
:::

**Capacidades:** Persistent context, knowledge graphs, conversation history, user preferences, project decisions

**Deployment:** Cloud (zero config) o Self-hosted (Docker + PostgreSQL)

**Components:** Setup scripts, REST API reference, Spaces CLI, agent templates

**Cuándo usar:** Necesitas memoria persistente entre sesiones, contexto long-term, knowledge graphs

---

## algorithmic-art

::: tip Tipo: Creative Tool
Arte generativo p5.js con filosofías algorítmicas. Cada pieza define su principio estético y comportamiento computacional único.
:::

**Proceso:** Define filosofía algorítmica → Implementa p5.js → Genera viewer interactivo (seed navigation + controles paramétricos + export)

::: details Ejemplos de Uso

```bash
# Flow fields
"Flow fields con partículas orgánicas"

# Sistemas geométricos
"Arte algorítmico con polígonos y ruido Perlin"

# Inspiración artística
"Arte inspirado en Bridget Riley (Op Art)"
```

:::

**Output:** Filosofía (.md) + HTML interactivo con reproducibilidad (mismo seed = mismo output)

---

## Cómo Usar Skills

**Activación Automática:**

```
User Request → Detect Keywords → Match Triggers → Activate Skill
```

Claude detecta el contexto y activa la skill apropiada sin invocación explícita.

**Invocación Manual (opcional):**

```bash
"Usando claude-code-expert skill: crea agent para X"
```

**Crear Nueva Skill:**

```bash
"Crea una skill para [dominio específico]"
# → skill-creator guía el proceso interactivamente
```

---

## Troubleshooting

::: details Skill No Se Activa

**Problema:** Solicitud muy genérica

```bash
❌ "Ayúdame con código"
✅ "Crea agent para análisis de código Python"
```

**Problema:** Skill no instalada

```bash
ls -la skills/  # Verificar instalación
```

:::

::: details Output Incorrecto

**Si claude-code-expert falla:**

```bash
# Docs desactualizadas
"WebFetch latest Claude Code documentation"
```

**Si cualquier skill falla:**

```bash
# Validar recursos
ls -la skills/skill-name/
```

:::

---

## Best Practices

::: tip Recomendaciones

**✅ Hacer:**

- Solicitudes específicas con contexto
- Validar output contra quality gates
- Iterar basado en feedback

**❌ Evitar:**

- Solicitudes genéricas sin contexto
- Ignorar warnings de validación
- Duplicar funcionalidad existente
  :::

---

## Recursos

**Scripts Esenciales:**

- `init_skill.py` - Inicializar skill
- `validate_skill.py` - Validar estructura
- `package_skill.py` - Empaquetar para distribución

**Documentación:**

- 📖 Plugin Guide: `.claude-plugin/README.md`
- ⚖️ Constitution: `.specify/memory/constitution.md`

---

::: info Última Actualización
**Fecha**: 2025-10-24 | **Skills**: 3 | **Status**: Production-Ready
:::
