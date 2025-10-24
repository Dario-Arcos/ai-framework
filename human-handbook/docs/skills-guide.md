# Guía de Expert Skills

::: tip ¿Qué son las Skills?
Capacidades especializadas que extienden Claude con conocimiento experto en dominios específicos. Se activan automáticamente según el contexto.
:::

---

## Skills Disponibles

| Skill                                     | Tipo           | Activación                                   |
| ----------------------------------------- | -------------- | -------------------------------------------- |
| [claude-code-expert](#claude-code-expert) | 🔧 Development | Crear/modificar agents, commands, hooks, MCP |
| [skill-creator](#skill-creator)           | 🏗️ Meta        | Crear/actualizar skills                      |
| [algorithmic-art](#algorithmic-art)       | 🎨 Creative    | Arte algorítmico, p5.js, flow fields         |

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
