# Skills

Workflows especializados que Claude activa automáticamente o que puedes invocar explícitamente.

::: tip Activación
Claude detecta el contexto y carga el skill apropiado. También puedes forzarlo: `"Usando frontend-design: crea landing page"`.
:::

---

## Todos los skills

### Core

| Skill | Qué hace | Cuándo usarlo |
|-------|----------|---------------|
| `agent-browser` | Browser automation con Playwright | Scraping, e2e web, forms, screenshots |
| `brainstorming` | Diálogo para diseñar soluciones | Antes de codear algo nuevo |
| `pr-workflow` | PR con code + security review | Al crear pull requests |
| `claude-code-expert` | Genera componentes Claude Code | Crear agents, commands, hooks |
| `frontend-design` | Diseño web distintivo | Interfaces memorables, no genéricas |
| `humanizer` | Elimina patrones de texto AI | Docs, commits, PRs, UI text |
| `writing-skills` | Crear skills bulletproof | Meta-skill para autores de skills |

### Pipeline SOP (desarrollo autónomo)

| Skill | Qué hace | Posición en el pipeline |
|-------|----------|------------------------|
| `ralph-orchestrator` | Orquesta todo el pipeline | **Entry point** — invoca este |
| `sop-discovery` | Explora constraints y riesgos | 1. Exploración |
| `sop-reverse` | Investiga sistemas existentes | 1. Exploración (alternativa) |
| `sop-planning` | Diseña solución detallada | 2. Diseño |
| `sop-task-generator` | Genera .code-task.md files | 3. Planificación |
| `sop-code-assist` | Implementa con TDD | 4. Ejecución |

---

## agent-browser

CLI de browser automation. Reemplaza WebFetch/WebSearch para interacción real con páginas.

```bash
agent-browser open https://example.com
agent-browser snapshot -i          # Lista elementos (@e1, @e2...)
agent-browser fill @e1 "texto"
agent-browser click @e2
agent-browser screenshot result.png
```

::: details Todas las capacidades
| Categoría | Comandos |
|-----------|----------|
| Navegación | `open`, `back`, `forward`, `reload`, `tab`, `frame` |
| Interacción | `click`, `fill`, `type`, `select`, `upload`, `drag`, `hover` |
| Captura | `screenshot`, `pdf`, `record start/stop` |
| Estado | `cookies`, `storage`, `state save/load` |
| Red | `network route`, `network requests` |
| Debug | `--headed`, `console`, `errors`, `trace` |
:::

Se instala automáticamente. Ver [Integrations](./integrations.md#agent-browser).

---

## brainstorming

Convierte ideas vagas en diseños completos mediante diálogo.

```
"Necesito sistema de notificaciones push"
```

**Flujo:**
1. Examina el proyecto, pregunta una cosa a la vez
2. Propone 2-3 enfoques con trade-offs
3. Diseña en secciones de 200-300 palabras, valida cada una
4. Genera `docs/plans/YYYY-MM-DD-<topic>-design.md`

Después: continúa con `ralph-orchestrator` o Superpowers `writing-plans`.

---

## pr-workflow

Quality gate para PRs: code review + security review + observaciones.

```
"Crear PR a main"
```

**Flujo:**
1. Valida branch, extrae commits, detecta formato
2. Ejecuta en paralelo: code review, security review, observaciones
3. Presenta findings por severidad
4. Opciones: **Create PR** / **Auto fix** / **Cancel**
5. Auto fix → corrige → re-review → pregunta de nuevo
6. Crea PR con findings documentados

::: details Agentes que usa
- `code-reviewer` — lógica, arquitectura, tests
- `security-reviewer` — SQL injection, XSS, secrets
- `receiving-code-review` — verifica issues antes de auto-fix
:::

**Requisitos:** git, gh CLI

---

## claude-code-expert

Genera componentes Claude Code consultando docs oficiales primero.

```
"Crea agent para optimización PostgreSQL"
```

::: warning Training desactualizado
Usa `agent-browser` para consultar https://code.claude.com/docs. Nunca confía en memoria.
:::

**Flujo:**
1. Abre docs oficiales, navega a sección relevante
2. Extrae syntax actual y campos requeridos
3. Analiza patterns del proyecto
4. Genera con 6 quality gates

**Output:** `.claude/agents/*.md`, `commands/*.md`, `hooks/*.py`

---

## frontend-design

Interfaces web con dirección estética bold. Sin look genérico "AI slop".

```
"Landing page para startup fintech"
```

**Flujo obligatorio:**
1. Research — captura 3-5 referencias de Awwwards con `agent-browser`
2. Sintetizar — extrae DNA (colores, tipografía, spacing)
3. Commit — define dirección estética (brutalist, luxury, editorial...)
4. Implementar — código funcional con atención a detalles
5. Validar — compara contra referencias

::: details Principios
- **Typography**: Fonts distintivas. Nunca Arial/Inter/Roboto.
- **Color**: Dominantes con acentos sharp, no gradientes tímidos.
- **Motion**: CSS-only. Staggered reveals > micro-interactions.
- **Layout**: Asimetría, overlap, grid-breaking, negative space.
:::

---

## humanizer

Elimina 24 patrones de texto AI (Wikipedia's "Signs of AI writing").

| Patrón | Ejemplos |
|--------|----------|
| Vocabulario AI | "Additionally", "delve", "landscape", "tapestry" |
| Inflación | "serves as a testament", "pivotal moment" |
| Estructura | Rule of three, em dashes excesivos |
| Tono | "Great question!", "I hope this helps!" |

::: details Ejemplo
**Antes:**
> The software update serves as a testament to the company's commitment to innovation.

**Después:**
> The update adds batch processing, keyboard shortcuts, and offline mode.
:::

No solo limpia — añade voz. Texto estéril es tan obvio como slop.

---

## writing-skills

Meta-skill: crear skills bulletproof con TDD aplicado a documentación.

**Proceso:**
1. **RED** — Escenarios de presión sin skill. Documenta racionalizaciones.
2. **GREEN** — SKILL.md que contrarresta fallas. Verifica compliance.
3. **REFACTOR** — Cierra loopholes, re-testea hasta bulletproof.

::: warning Prerrequisito
Requiere Superpowers `test-driven-development`.
:::

---

## Pipeline SOP

Sistema de desarrollo autónomo. Ralph orquesta estos skills en secuencia:

```
┌─────────────┐     ┌──────────────┐     ┌───────────────────┐     ┌─────────────────┐
│sop-discovery│ ──▶ │ sop-planning │ ──▶ │sop-task-generator │ ──▶ │ sop-code-assist │
└─────────────┘     └──────────────┘     └───────────────────┘     └─────────────────┘
       │                   ▲
       └───────────────────┤
                    ┌──────┴──────┐
                    │ sop-reverse │
                    └─────────────┘
```

### ralph-orchestrator

**Entry point.** Invoca este para desarrollo autónomo.

```bash
# Instalar
./skills/ralph-orchestrator/scripts/install.sh

# Ejecutar
./loop.sh specs/mi-feature/
```

::: warning Requisitos
Git repo, tests/lint/build, Bash 4+, jq, bc.
:::

**Flujo:**
1. Detecta tipo (Forward: nuevo | Reverse: investigar)
2. Discovery o investigation
3. Diseño detallado
4. Genera task files
5. **Checkpoint**: apruebas el plan
6. Ejecución autónoma

::: details Exit codes
| Código | Significado |
|--------|-------------|
| 0 | Completo |
| 1 | Error validación |
| 2 | Circuit breaker (3 fallos) |
| 3 | Max iterations |
| 130 | Ctrl+C |
:::

---

### sop-discovery

Explora constraints, riesgos y prior art. Metodología Amazon agent-SOP.

**Cuándo:** Proyecto nuevo, requirements poco claros.

**Output:** `discovery.md`

---

### sop-reverse

Investiga sistemas existentes y genera specs.

**Cuándo:** Codebase heredado, integrar APIs, documentar legacy.

**Output:** `investigation.md`, `specs-generated/`, `recommendations.md`

---

### sop-planning

Transforma ideas en diseños implementables. Metodología PDD.

**Fases:** Requirements → Research → Design → Implementation plan

**Output:** `design/detailed-design.md`, `implementation/plan.md`

---

### sop-task-generator

Convierte plans en `.code-task.md` files.

**Output:** Un task file por paso, con acceptance criteria (Given-When-Then).

---

### sop-code-assist

Implementa tasks con TDD: RED → GREEN → REFACTOR.

**Output:** Código + tests + commits.

---

## Más skills

- [Superpowers](./integrations.md#superpowers) — TDD, debugging, code review, worktrees
- [skills.sh](https://skills.sh/) — Catálogo abierto con React, TypeScript, Stripe, etc.

---

## Troubleshooting

::: details Skill no se activa
Sé específico o menciónalo:
```
❌ "Ayuda con código"
✅ "Crear PR a main"
✅ "Usando pr-workflow: crear PR"
```
:::

::: details Skill desactualizado
```bash
/plugin marketplace update ai-framework-marketplace
/plugin update ai-framework@ai-framework-marketplace
```
:::

::: details SOP no genera output
Verifica que existe `specs/` en tu proyecto.
:::

---

::: info Última actualización
**Fecha**: 2026-01-31 | **Skills**: 13 total
:::
