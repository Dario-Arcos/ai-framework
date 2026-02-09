# Skills

Los skills son workflows especializados que Claude carga automáticamente por contexto o que puedes invocar de forma explícita. Cada skill encapsula un proceso completo (debugging, commits, PRs, diseño UI) con sus propias fases, validaciones y outputs.

> **Antes de empezar**: lee [Workflow AI-first](./ai-first-workflow.md) para entender cómo los skills se integran en el pipeline de desarrollo.

::: tip Activación
Claude detecta el contexto y carga el skill apropiado. También puedes forzarlo: `"Usando frontend-design: crea landing page"`.
:::

---

## Todos los skills

### Core

| Skill | Qué hace | Cuándo se activa |
|-------|----------|------------------|
| `brainstorming` | Diálogo para diseñar soluciones | Usuario describe qué construir, añadir o cambiar |
| `systematic-debugging` | Debugging metódico con 4 fases | Bug, test failure, comportamiento inesperado |
| `pull-request` | PR con quality gate integrado | Listo para crear pull request |
| `frontend-design` | Diseño UI distintivo | Construir o estilizar UI (web, mobile, posters) |
| `humanizer` | Elimina patrones de texto AI | Escribir o editar prosa (docs, UI copy, mensajes) |
| `claude-code-expert` | Investiga docs oficiales Claude Code | Pregunta sobre features, APIs, skills, hooks, MCP |
| `skill-creator` | Crear skills nuevas | Creando o actualizando un skill |
| `context-engineering` | Optimizar prompts y CLAUDE.md | System prompts, agent architecture |
| `agent-browser` | Browser automation con Playwright | Cualquier interacción web (research, E2E, scraping) |

### Git & Workflow

| Skill | Qué hace | Cuándo se activa |
|-------|----------|------------------|
| `commit` | Commits semánticos con agrupación | Listo para commitear |
| `changelog` | Actualiza CHANGELOG desde diff real | Documentar cambios |
| `branch-cleanup` | Limpieza post-merge | Después de mergear PR |
| `worktree-create` | Worktree aislado en sibling dir | Necesitas workstream paralelo |
| `worktree-cleanup` | Eliminar worktrees con validación | Terminar con worktrees |
| `project-init` | Genera rules de equipo | Proyecto nuevo o cambiado |
| `deep-research` | Investigación multi-fuente verificada | Investigación compleja |

### Pipeline SOP (desarrollo autónomo)

| Skill | Qué hace | Cuándo se activa |
|-------|----------|------------------|
| `ralph-orchestrator` | Orquesta todo el pipeline | **Entry point** — invoca este |
| `sop-discovery` | Explora constraints y riesgos | Fase 1: exploración |
| `sop-reverse` | Investiga sistemas existentes | Fase 1: exploración (alternativa) |
| `sop-planning` | Diseña solución detallada | Fase 2: diseño |
| `sop-task-generator` | Genera .code-task.md files | Fase 3: planificación |
| `sop-code-assist` | Implementa con SDD | Fase 4: ejecución |

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
| iOS/Mobile | `-p ios`, `tap`, `swipe`, `device list` |
| Debug | `--headed`, `console`, `errors`, `trace` |
:::

Se instala automáticamente. Ver [Integraciones](./integrations.md#agent-browser).

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

## systematic-debugging

Proceso de 4 fases para encontrar root cause antes de intentar fixes.

**Ley de hierro:** NO fixes sin investigación de root cause primero.

**Las 4 fases:**

| Fase | Actividad | Criterio de éxito |
|------|-----------|-------------------|
| 1. Root Cause | Leer errores, reproducir, check changes | Entender QUÉ y POR QUÉ |
| 2. Pattern | Encontrar ejemplos funcionales, comparar | Identificar diferencias |
| 3. Hypothesis | Formar teoría, testear mínimamente | Confirmado o nueva hipótesis |
| 4. Implementation | Crear test, fix, verificar | Bug resuelto, tests pasan |

::: warning Red flags — STOP y vuelve a Fase 1
- "Quick fix por ahora, investigar después"
- "Solo intenta cambiar X y ve si funciona"
- Proponer soluciones sin trazar data flow
- 3+ fixes fallidos → cuestiona la arquitectura
:::

**Técnicas incluidas:**
- `root-cause-tracing.md` — Trazar bugs hacia atrás en call stack
- `defense-in-depth.md` — Validación en múltiples capas
- `condition-based-waiting.md` — Reemplazar timeouts arbitrarios
- `find-polluter.sh` — Script para encontrar test que contamina

---

## pull-request

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

**Output:** `.claude/agents/*.md`, `skills/*/SKILL.md`, `hooks/*.py`

---

## frontend-design

Interfaces web con dirección estética bold. Sin look genérico.

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

## skill-creator

Guía para crear skills efectivas. Basado en el [skill-creator de Anthropic](https://github.com/anthropics/skills/tree/main/skills/skill-creator).

```bash
# Inicializar un skill nuevo
python skills/skill-creator/scripts/init_skill.py my-skill --path skills/

# Validar estructura
python skills/skill-creator/scripts/quick_validate.py skills/my-skill/

# Empaquetar para distribución
python skills/skill-creator/scripts/package_skill.py skills/my-skill/
```

**Principios clave:**
- **Conciso**: El context window es recurso compartido. Solo añade lo que Claude no sabe.
- **Progressive Disclosure**: Metadata siempre → SKILL.md al activar → references bajo demanda.
- **Grados de libertad**: Bridge estrecho = guardrails estrictos. Campo abierto = instrucciones flexibles.

::: details Anatomía de un skill
```
skill-name/
├── SKILL.md           # Frontmatter (name, description) + instrucciones
├── scripts/           # Código ejecutable (Python/Bash)
├── references/        # Docs cargadas bajo demanda
└── assets/            # Archivos para output (templates, imágenes)
```
:::

---

## context-engineering

Optimiza system prompts, CLAUDE.md, AGENTS.md y arquitecturas de agentes.

```
"Mi agente no usa las tools disponibles"
"Optimiza este CLAUDE.md para mejor activación"
```

**Cuándo usarlo:**
- Agentes que underperform pese a instrucciones correctas
- Diseño de system prompts o AGENTS.md
- Optimización de token efficiency en context windows
- Pérdida de coherencia en tareas largas

**Basado en:**
- [Vercel AGENTS.md Primitives](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)
- [Anthropic Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## commit

Commits semánticos con agrupación automática por tipo de archivo.

::: code-group
```bash [Convencional]
/commit "feat(auth): add OAuth2 support"
```

```bash [Corporativo]
/commit "TRV-345 implementar autenticación"
# Output: feat|TRV-345|20260131|implementar autenticación
```

```bash [Tipo explícito]
/commit "refactor: TRV-345 mejorar módulo auth"
```
:::

**Agrupación automática:** Si modificas archivos de 2+ categorías (config + código, docs + tests), crea commits separados por tipo.

---

## changelog

Actualiza CHANGELOG.md basándose en el **diff real**, no en commits.

```bash
/changelog "desde última versión"
/changelog "desde v2.0.0"
```

**Por qué diff y no commits:**

```
Commits:                    Diff real:
1. feat: add caching        Solo existe: logging.py
2. fix: caching bug
3. revert: remove caching   El caching NO EXISTE.
4. feat: add logging        Documentarlo sería mentir.
```

El changelog documenta qué existe, no qué se intentó.

---

## branch-cleanup

Limpieza después de merge: elimina feature branch, sincroniza con base.

```bash
/branch-cleanup        # Auto-detecta base (main/master/develop)
/branch-cleanup main   # Base explícita
```

GitHub elimina la branch remota al mergear. Este skill limpia la local.

---

## worktree-create

Crea worktree en directorio sibling con rama nueva.

```bash
/worktree-create "implementar autenticacion OAuth" main
# Crea: ../worktree-implementar-autenticacion-oauth
```

::: tip Branch vs Worktree
**Branch:** Desarrollo lineal, una feature a la vez.
**Worktree:** Múltiples features en paralelo, cada una en directorio aislado.
:::

::: warning Después de crear
El IDE se abre automáticamente, pero debes iniciar nueva sesión Claude en esa ventana. Si no, Claude sigue trabajando en el directorio anterior.
:::

---

## worktree-cleanup

Elimina worktrees con validación de ownership.

```bash
/worktree-cleanup              # Discovery: lista disponibles
/worktree-cleanup worktree-1   # Eliminar específico
```

**Restricciones:**
- Solo elimina worktrees que te pertenecen
- No toca branches protegidas (main, develop, staging)
- Requiere working tree limpio

---

## project-init

Genera reglas de proyecto compartibles con el equipo.

```bash
/project-init
```

**Arquitectura dual:**

```
docs/claude-rules/    ← TRACKED (source of truth)
├── stack.md
├── patterns.md
├── architecture.md
└── testing.md
        ↓ session-start hook (auto-sync)
.claude/rules/        ← IGNORED (working copy)
```

Las reglas viven en `docs/claude-rules/` para versionarlas y reviewarlas en PRs. El hook de session-start las sincroniza a `.claude/rules/` automáticamente.

::: info Para nuevos miembros
Si el proyecto ya tiene `docs/claude-rules/`, no necesitas ejecutar `/project-init`. El hook sincroniza automáticamente.
:::

---

## deep-research

Investigación multi-fuente con verificación y confidence ratings.

```bash
/deep-research "análisis competitivo sector fintech"
```

**Metodología:**
- 3-5 pases iterativos de búsqueda
- Mínimo 3 fuentes independientes por claim
- Confidence rating (High/Medium/Low/Uncertain)
- Cada afirmación citada con URL y fecha

::: details Jerarquía de fuentes
| Tier | Ejemplos |
|------|----------|
| **1 (Primary)** | .gov, SEC, peer-reviewed, World Bank |
| **2 (Industry)** | McKinsey, Gartner, Bloomberg, FT |
| **3 (Corroborative)** | WSJ, The Economist, industry bodies |
:::

Usa `agent-browser` para navegación real, no cached data.

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

Implementa tasks con SDD: SCENARIO → SATISFY → REFACTOR.

**Output:** Código + tests + commits.

---

## Workflows típicos

| Escenario | Skills |
|-----------|--------|
| **Feature nueva** | `/brainstorming` → implementar → `/commit` → `/pull-request` |
| **Bug fix urgente** | `/worktree-create` → fix → `/commit` → `/pull-request` |
| **Desarrollo autónomo** | `/ralph-orchestrator` (orquesta todo el pipeline) |
| **Post-merge** | `/branch-cleanup` |

---

## Más skills

Para plugins externos (Episodic Memory, Superpowers) y catálogos de terceros (skills.sh), ver [Integraciones](./integrations.md).

---

## Troubleshooting

::: details Skill no se activa
Sé específico o menciónalo:
```
❌ "Ayuda con código"
✅ "Crear PR a main"
✅ "Usando pull-request: crear PR"
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

**Siguiente paso**: [Agentes](./agents-guide.md)

---

::: info Última actualización
**Fecha**: 2026-02-08
:::
