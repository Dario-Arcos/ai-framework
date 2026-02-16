---
outline: 2
---

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
| `brainstorming` | Diálogo estructurado para diseñar soluciones antes de implementar | Usuario describe qué construir, añadir o cambiar |
| `scenario-driven-development` | Ciclo SCENARIO→SATISFY→REFACTOR con convergence gates | Toda implementación — se activa siempre |
| `systematic-debugging` | Debugging metódico con 4 fases | Bug, test failure, comportamiento inesperado |
| `verification-before-completion` | Gate de evidencia: 6 pasos antes de declarar "hecho" | Antes de cualquier claim de completitud |
| `pull-request` | PR con quality gate integrado | Listo para crear pull request |
| `frontend-design` | Diseño UI distintivo | Construir o estilizar UI (web, mobile, posters) |
| `humanizer` | Elimina patrones de texto AI | Escribir o editar prosa (docs, UI copy, mensajes) |
| `skill-creator` | Crear skills nuevas | Creando o actualizando un skill |
| `context-engineering` | Diseño y optimización de system prompts, CLAUDE.md, y agent architectures | System prompts, context windows, coherencia de agentes |

### Git & Workflow

| Skill | Qué hace | Cuándo se activa |
|-------|----------|------------------|
| `commit` | Commits semánticos con agrupación automática por tipo | Listo para commitear |
| `changelog` | Actualiza CHANGELOG desde diff real | Documentar cambios |
| `branch-cleanup` | Limpieza post-merge | Después de mergear PR |
| `worktree-create` | Worktree aislado en sibling dir | Necesitas workstream paralelo |
| `worktree-cleanup` | Eliminar worktrees con validación | Terminar con worktrees |
| `project-init` | Genera rules de proyecto (stack, architecture, conventions) | Proyecto nuevo o stack cambiado |
| `deep-research` | Investigación multi-fuente con verificación y confidence ratings | Investigación compleja |
| `using-ai-framework` | Enforcement de skills y agentes — inyectado automáticamente | Session start (automático), o manual si falta |

### Pipeline SOP (desarrollo autónomo)

| Skill | Qué hace | Cuándo se activa |
|-------|----------|------------------|
| `ralph-orchestrator` | Orquesta pipeline completo con Agent Teams — [ver página dedicada](./ralph-orchestrator.md) | **Entry point** — invoca este |
| `sop-discovery` | Explora constraints y riesgos | Fase 1: exploración |
| `sop-reverse` | Referent discovery (pre-build) + reverse engineering (sistemas existentes) | Fase 1: exploración |
| `sop-planning` | Diseña solución detallada | Fase 2: diseño |
| `sop-task-generator` | Genera .code-task.md files | Fase 3: planificación |
| `sop-code-assist` | Implementa con SDD | Fase 4: ejecución |
| `sop-reviewer` | Valida SDD compliance, reward hacking, satisfacción de scenarios | Post-ejecución: review |

---

## agent-browser <Badge type="info" text="herramienta externa" />

CLI de browser automation. No es un skill del framework — es una herramienta externa que los skills usan internamente. Reemplaza WebFetch/WebSearch para interacción real con páginas.

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

**Entry point** para desarrollo autónomo. Orquesta el pipeline completo — de la idea al código revisado — usando Agent Teams con contexto fresco de 200K tokens por teammate.

> **[Ver página dedicada →](./ralph-orchestrator.md)** — arquitectura, paso a paso, configuración, safety nets, modelo de costos.

**En resumen:** planificación en 2 modos (interactive/autonomous), checkpoint obligatorio, ejecución via Agent Teams con quality gates enforced por hooks y reviewer teammate que valida SDD compliance.

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

Dos capacidades en un skill:

1. **Referent Discovery** (pre-build): busca implementaciones world-class, extrae patrones, construye sobre fundamentos probados.
2. **Reverse Engineering** (investigar existente): investiga artifacts existentes (codebases, APIs, procesos) y genera specs estructurados.

**Cuándo:** Antes de construir algo nuevo (referentes), o al heredar codebase, integrar APIs, documentar legacy.

**Output:** `referents/catalog.md`, `extracted-patterns.md`, `investigation.md`, `recommendations.md`

---

### sop-planning

Transforma ideas en diseños implementables. Metodología PDD (Prompt-Driven Development).

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

### sop-reviewer

Valida implementaciones completadas contra 5 gates en secuencia:

| Gate | Qué valida | Nivel |
|------|-----------|-------|
| 1. SDD Compliance | Scenarios definidos antes del código, end-to-end user stories | BLOCKING |
| 2. Behavioral Satisfaction | Comportamiento observado satisface intent del usuario | BLOCKING |
| 3. Reward Hacking Detection | Tests no fueron reescritos para pasar, scenarios no debilitados | BLOCKING |
| 4. Code Quality | Clean code, no tech debt innecesaria | SUGGESTION |
| 5. Integration Risk | Impacto en otros tasks, side effects | SUGGESTION |

Los gates BLOCKING detienen la review si fallan. Los SUGGESTION se documentan pero no bloquean.

**Detección de reward hacking:** Si el implementer reescribió un test para que pase en vez de arreglar el código, o debilitó un scenario para satisfacerlo, el reviewer lo detecta y rechaza.

---

## scenario-driven-development

Metodología core del framework. Todo código se implementa con el ciclo SCENARIO → SATISFY → REFACTOR.

**Ley de hierro:**
```
NO PRODUCTION CODE WITHOUT A DEFINED SCENARIO FIRST
```

**Concepto clave:** un scenario NO es un test. Es una user story end-to-end con comportamiento observable desde la perspectiva del usuario.

| | Scenario | Test |
|---|---|---|
| **Vive** | En el spec o external | En el codebase |
| **Evalúa** | "¿Satisface al usuario?" | "¿Pasa?" |
| **Vulnerable a** | Nada (holdout externo) | Reward hacking |

**Satisfacción ≠ Pass/Fail:** SDD reemplaza el boolean "todos los tests pasan" con convergencia probabilística — ¿qué fracción de trayectorias por los scenarios satisface al usuario?

**Ciclo:**
1. Definir scenario como user story con valores concretos
2. Encodificar como test que falla
3. Implementar código mínimo para satisfacer
4. Refactor sin romper satisfacción
5. Repetir hasta convergencia

---

## verification-before-completion

Gate de evidencia que se ejecuta antes de cualquier claim de completitud. "Los tests pasan" sin output no es evidencia.

**Ley de hierro:**
```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

**Los 6 pasos:**

| Paso | Acción |
|------|--------|
| 1. IDENTIFY | Lista cada claim que vas a hacer |
| 2. RUN | Ejecuta el comando de verificación AHORA |
| 3. READ | Lee el output COMPLETO — no skimees |
| 4. VERIFY | Confirma que el output coincide con tu claim |
| 5. SATISFY | Verifica contra scenarios definidos |
| 6. REPORT | Reporta [M/N satisfechos] con evidencia |

"Lo corrí antes" no cuenta. "Los tests pasan" sin output no cuenta. Solo evidencia fresca y observable.

---

## sop-reviewer

Disponible como skill standalone o invocado automáticamente por reviewer teammates en Ralph. Ver [sección en Pipeline SOP](#sop-reviewer) para detalles de los 5 gates.

---

## using-ai-framework

Reglas de enforcement que aseguran que Claude invoque skills y agentes por contexto. Inyectado automáticamente al inicio de cada sesión via SessionStart hook.

**Regla:** invocar skills antes de responder. Solo saltar cuando es **seguro** que ningún skill aplica. En duda, invocar — los falsos positivos son baratos, los skills perdidos son caros.

**Red flags** — si piensas esto, STOP e invoca:

| Pensamiento | Realidad |
|-------------|---------|
| "Puedo con mi training" | Training es stale. Skills tienen metodología actual. |
| "El skill es overkill" | Lo simple se complica. Invoca. |
| "Déjame explorar primero" | Skills dicen CÓMO explorar. Invoca primero. |

**Prioridad:** skills de proceso primero (brainstorming, debugging, discovery), luego skills de implementación (scenario-driven-development, frontend-design).

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
**Fecha**: 2026-02-15
:::
