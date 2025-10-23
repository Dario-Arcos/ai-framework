# Guía de Comandos Claude Code

::: tip Navegación Rápida
Usa esta guía para ejecutar comandos de forma eficiente. Los comandos están diseñados para ejecutarse secuencialmente siguiendo workflows específicos.
:::

_24 comandos disponibles organizados por flujo de desarrollo_

---

## Resumen Ejecutivo

| Categoría                                                     | Comandos | Flujo Típico                           |
| ------------------------------------------------------------- | -------- | -------------------------------------- |
| [Ciclo PRP (Business Layer)](#ciclo-prp-business-layer)       | 2        | Product Requirements → GitHub Tracking |
| [Ciclo SDD (Engineering Layer)](#ciclo-sdd-engineering-layer) | 9        | Spec → Plan → Tasks → Implement        |
| [Git & GitHub](#git-github)                                   | 5        | Commit → PR → Cleanup                  |
| [Utilidades](#utilidades)                                     | 8        | Understand → Research → Polish → Docs  |

::: tip Orden Recomendado
Los comandos del **Ciclo SDD** funcionan mejor en orden específico. Cada paso prepara el siguiente. Ver [Workflows Completos](#workflows-completos) para la secuencia.
:::

---

## Ciclo PRP (Business Layer)

### `/ai-framework:PRP-cycle:prp-new`

Brainstorming interactivo para crear Product Requirements Prompt (PRP) estructurado, minimalista (50-100 líneas), business-focused.

**Usage:**

```bash
/ai-framework:PRP-cycle:prp-new {feature_name}

# Ejemplo
/ai-framework:PRP-cycle:prp-new user-authentication
```

**Output:** `prps/{feature_name}/prp.md`

**Design Philosophy (Steve Jobs Principles):**

- **"Simplicity is the ultimate sophistication"**
- PRP describe WHAT y WHY, no HOW
- Target: 50-100 líneas (vs típico 300+ líneas)
- Say NO a implementation details (stack, architecture, config)
- Focus en user value y business outcomes

**PRP Structure (Minimalista):**

1. **Problem Statement** (5-10 líneas) - Formato estructurado AI-parseable
2. **User Impact** (10-20 líneas) - Primary users, user journey, pain points
3. **Success Criteria** (5-10 líneas) - Quantitative + Qualitative con checkboxes
4. **Constraints** (5-10 líneas) - Budget, timeline, team, compliance, complexity budget
5. **Out of Scope (V1)** (5-10 líneas) - Explícitamente list what we're NOT building

**Discovery & Context Questions:**

- **Problem**: ¿Qué problema específico estamos resolviendo? ¿Por qué ahora?
- **Users**: ¿Quién experimenta este problema? ¿Personas primarias?
- **Impact**: ¿Qué pasa si NO resolvemos esto?
- **Success**: ¿Cómo medimos si esto funciona?
- **Constraints**: ¿Budget, timeline, compliance requirements?
- **Scope**: ¿Qué NO estamos building en V1?

**Quality Checks:**

- [ ] Total length: 50-100 líneas (excluding frontmatter)
- [ ] No implementation details (no stack, config, architecture)
- [ ] Problem statement usa structured format con fields
- [ ] Success criteria usan checkboxes con measurement/verification methods
- [ ] Problem y user impact crystal clear
- [ ] Success criteria son measurable
- [ ] Out of scope explicitly defined
- [ ] All sections complete (no placeholder text como "TBD")
- [ ] Written para business stakeholders (non-technical language)
- [ ] Frontmatter includes complexity_budget y priority

::: tip Cuándo usar
Planificación de nueva feature desde cero con stakeholders de negocio.
:::

**Next Steps:** `➜ /ai-framework:PRP-cycle:prp-sync {feature_name}`

---

### `/ai-framework:PRP-cycle:prp-sync`

Sincroniza PRP a GitHub como Parent Issue con opción de milestone assignment.

**Usage:**

```bash
/ai-framework:PRP-cycle:prp-sync {feature_name}
/ai-framework:PRP-cycle:prp-sync {feature_name} --milestone {number}

# Ejemplos
/ai-framework:PRP-cycle:prp-sync user-authentication
/ai-framework:PRP-cycle:prp-sync user-authentication --milestone 5
```

**Output:** GitHub Issue (parent) + actualiza frontmatter con `github_synced`

**Workflow:**

1. Parse arguments (feature name + optional milestone number)
2. Validate required files exist (`prps/{feature_name}/prp.md`)
3. Milestone handling:
   - **If milestone number provided**: Use existing milestone
   - **If no milestone**: Continue sin milestone assignment
4. Create GitHub issue:
   - Title: Extract desde PRP frontmatter `name` field
   - Body: Clean PRP content sin frontmatter
   - Labels: `prp`, `parent-issue`, `sdd`
   - Assign to milestone si milestone number was provided
5. Update PRP file frontmatter con `github`, `github_synced`, `milestone` (si aplica)
6. Create GitHub mapping file (`prps/{feature_name}/github-mapping.md`)

**Relationship to SDD Workflow:**

```
PRP.md → [prp-sync] → GitHub Parent Issue → [SDD-cycle:speckit.specify --from-issue] → Technical Spec + Sub-Issues
```

::: tip Cuándo usar
Después de aprobar PRP, para tracking en GitHub.
:::

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.specify --from-issue {issue_number}`

---

## Ciclo SDD (Engineering Layer)

::: tip Secuencia Recomendada
Estos comandos funcionan mejor en el orden especificado. Cada paso prepara el siguiente.
:::

### `/ai-framework:SDD-cycle:speckit.specify`

Crea especificación técnica desde descripción natural, GitHub Issue, o PRP.

**Casos de Uso:**

```bash
# Desde descripción natural
/ai-framework:SDD-cycle:speckit.specify "Implement OAuth 2.0 with Google and GitHub"

# Desde GitHub Issue
/ai-framework:SDD-cycle:speckit.specify --from-issue 247

# Desde PRP local
/ai-framework:SDD-cycle:speckit.specify --from-prp user-authentication
```

**¿Qué hace?**

1. **Crea Branch Automática**
   - Nombre: `001-feature-name` (número incremental)
   - Checkout automático (NO crea worktree)
   - Detecta siguiente número disponible

2. **Genera Spec** (`specs/001-feature-name/spec.md`)
   - Focus en WHAT y WHY (no HOW)
   - Success criteria measurables y technology-agnostic
   - User scenarios y acceptance tests
   - Hace máximo 3 preguntas si algo crítico no está claro

3. **Validación Automática**
   - Checklist interno de calidad
   - Detecta requirements ambiguos
   - Marca con `[NEEDS CLARIFICATION]` si necesario (máx 3)

**Reglas de Calidad:**

- ✅ Success criteria con métricas específicas (tiempo, %, cantidad)
- ✅ Sin mencionar tecnologías (frameworks, DBs, APIs)
- ✅ Escrito para stakeholders de negocio
- ❌ No incluir detalles de implementación

**Output:** Branch nueva + spec.md + checklist de validación

::: warning Importante
El comando hace checkout de la branch. Tu workspace cambia a la nueva branch automáticamente.
:::

::: tip Cuándo usar
Primera fase SDD - convierte requisitos en spec técnica.
:::

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.clarify` (recomendado)

---

### `/ai-framework:SDD-cycle:speckit.clarify`

Detecta ambigüedades en spec y pregunta interactivamente hasta 5 clarificaciones prioritarias.

**Casos de Uso:**

```bash
# Después de /speckit.specify, antes de /speckit.plan
/ai-framework:SDD-cycle:speckit.clarify
```

**¿Qué hace?**

1. **Escaneo de Ambigüedades**
   - Detecta términos vagos, placeholders, requisitos incompletos
   - Prioriza por impacto: scope > seguridad/privacidad > UX > detalles técnicos
   - Genera máximo 5 preguntas (las más críticas)

2. **Pregunta Interactiva** (una a la vez)
   - **Multiple-choice**: Tabla con opciones + recomendación justificada
   - **Short-answer**: Respuesta sugerida basada en best practices
   - Puedes aceptar recomendación con "yes" o "recommended"

3. **Actualización Incremental**
   - Aplica cada respuesta a la sección apropiada del spec
   - Guarda después de cada clarificación (atómico)
   - Crea sección `## Clarifications` con historial Q&A

**Categorías que Detecta:**

- Scope & Behavior incompleto
- Data model indefinido
- UX flows ambiguos
- Edge cases sin definir
- Dependencias externas sin especificar

**Output:** spec.md actualizada + sección Clarifications

::: tip ROI 100:1
2 minutos de clarificaciones previenen 4 horas de refactor. SIEMPRE ejecutar antes de `/plan`.
:::

::: tip Cuándo usar
Después de `/speckit.specify`, antes de `/speckit.plan`.
:::

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.plan`

---

### `/ai-framework:SDD-cycle:speckit.plan`

Genera artifacts de diseño técnico y decisiones de implementación.

**Casos de Uso:**

```bash
# Después de /speckit.clarify, antes de /speckit.tasks
/ai-framework:SDD-cycle:speckit.plan
```

**¿Qué genera?**

1. **research.md** - Decisiones técnicas
   - Stack seleccionado (frameworks, libs, tools)
   - Rationale de cada decisión
   - Alternativas consideradas y descartadas

2. **data-model.md** - Entidades y relaciones
   - Entities extraídas del spec
   - Fields + validations + relationships
   - State transitions (si aplica)

3. **contracts/** - API/GraphQL schemas
   - Un endpoint por cada user action
   - OpenAPI o GraphQL schema
   - Standard REST/GraphQL patterns

4. **quickstart.md** - Escenarios de integración
   - Ejemplos de uso de APIs
   - Flujos de integración

5. **Agent Context** - Actualización automática
   - Detecta y actualiza `.claude/` con nuevas tecnologías del plan
   - Preserva configuraciones manuales

**Output:** 5 artifacts + agent context actualizado

::: warning Prerequisito
Todas las clarificaciones deben estar resueltas. El comando falla si encuentra `[NEEDS CLARIFICATION]` en el spec.
:::

::: tip Cuándo usar
Después de `/speckit.clarify`, antes de `/speckit.tasks`.
:::

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.tasks`

---

### `/ai-framework:SDD-cycle:speckit.tasks`

Genera tasks.md ejecutable, organizado por user stories, con paralelización marcada [P].

**Casos de Uso:**

```bash
# Después de /speckit.plan, antes de /speckit.implement
/ai-framework:SDD-cycle:speckit.tasks
```

**Formato de Task (OBLIGATORIO):**

```text
- [ ] T001 [P?] [US1?] Description con file path
      ↑    ↑    ↑      ↑
      │    │    │      └─ Descripción + ruta exacta
      │    │    └─ User Story label (solo en fases US)
      │    └─ [P] = Paralelizable (archivos diferentes)
      └─ Checkbox markdown
```

**Ejemplos:**

- ✅ `- [ ] T001 Create project structure per plan`
- ✅ `- [ ] T005 [P] [US1] Create User model in src/models/user.py`
- ❌ `- [ ] Create User model` (falta ID + label)

**Organización por Phases:**

1. **Setup** - Inicialización del proyecto
2. **Foundational** - Prerequisites bloqueantes
3. **User Stories (P1, P2, P3...)** - Por prioridad
   - Cada story = fase independiente
   - Tests → Models → Services → Endpoints → Integration
4. **Polish** - Cross-cutting concerns

**Output:** `tasks.md` + report con:

- Total tasks + tasks por story
- Oportunidades de paralelización
- MVP scope sugerido (típicamente solo US1)

::: tip Tests son OPCIONALES
Solo se generan tasks de tests si están explícitamente solicitadas en el spec o si se pide enfoque TDD.
:::

::: tip Cuándo usar
Después de `/speckit.plan`, antes de `/speckit.implement`.
:::

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.analyze` (opcional)

---

### `/ai-framework:SDD-cycle:speckit.analyze`

Análisis de consistencia entre artefactos. Valida spec.md + plan.md + tasks.md.

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.analyze
```

::: warning STRICTLY READ-ONLY
Do NOT modify any files. Output structured analysis report.
:::

**Constitution Authority:** La project constitution (`.specify/memory/constitution.md`) es **non-negotiable**. Constitution conflicts son automáticamente CRITICAL.

**Execution Steps:**

1. **Initialize Analysis Context**: Run prerequisite check script y parse FEATURE_DIR + AVAILABLE_DOCS
2. **Load Artifacts (Progressive Disclosure)**: Load minimal necessary context desde cada artifact
3. **Build Semantic Models**: Create internal representations (requirements inventory, user story inventory, task coverage mapping, constitution rule set)
4. **Detection Passes (Token-Efficient Analysis)**:
   - **A. Duplication Detection**: Near-duplicate requirements
   - **B. Ambiguity Detection**: Vague adjectives, unresolved placeholders
   - **C. Underspecification**: Missing objects, missing acceptance criteria
   - **D. Constitution Alignment**: Conflicts con MUST principles
   - **E. Coverage Gaps**: Requirements sin tasks, tasks sin requirements
   - **F. Inconsistency**: Terminology drift, data entity conflicts

**Severity Assignment:**

- **CRITICAL**: Violates constitution MUST, missing core spec artifact, requirement con zero coverage
- **HIGH**: Duplicate/conflicting requirement, ambiguous security/performance, untestable acceptance
- **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case
- **LOW**: Style/wording improvements, minor redundancy

**Output:** Markdown report con:

- Findings table (ID, Category, Severity, Location, Summary, Recommendation)
- Coverage Summary Table (Requirement Key, Has Task?, Task IDs, Notes)
- Constitution Alignment Issues (si any)
- Unmapped Tasks (si any)
- Metrics (Total Requirements, Total Tasks, Coverage %, Ambiguity Count, etc.)

**Next Actions:**

- Si CRITICAL issues exist: Recommend resolving antes de `/implement`
- Si solo LOW/MEDIUM: User may proceed, pero provide improvement suggestions

::: tip Cuándo usar
Validación antes de implementar, después de generar tasks (opcional pero recomendado).
:::

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.checklist` (opcional) o `➜ /ai-framework:SDD-cycle:speckit.implement`

---

### `/ai-framework:SDD-cycle:speckit.implement`

Ejecuta tasks.md fase por fase con paralelización automática y TDD enforcement.

**Casos de Uso:**

```bash
# Después de /speckit.tasks (y opcionalmente /analyze + /checklist)
/ai-framework:SDD-cycle:speckit.implement
```

**¿Qué hace?**

1. **Validación de Checklists** (si existen)
   - Escanea `checklists/` y cuenta items completados
   - ⚠️ Si hay incomplete: pregunta si continuar
   - ✅ Si todos complete: procede automáticamente

2. **Carga Contexto** (artifacts del plan)
   - tasks.md + plan.md (obligatorios)
   - data-model.md, contracts/, research.md, quickstart.md (opcionales)

3. **Setup Automático**
   - Crea/verifica `.gitignore`, `.dockerignore`, etc. según stack detectado
   - Inicializa estructura del proyecto

4. **Ejecución Fase por Fase**
   - **Setup** → **Foundational** → **User Stories (P1, P2...)** → **Polish**
   - Tasks secuenciales: ejecuta en orden
   - Tasks `[P]`: ejecuta en paralelo
   - TDD: tests antes de implementación (si solicitado)
   - Marca `[X]` al completar cada task

5. **Validación Final**
   - Verifica que features match el spec original
   - Confirma que tests pasan (si existen)
   - Report de trabajo completado

**Output:** Implementación completa + tasks.md actualizada con `[X]`

::: warning Prerequisito
Checklists incompletos bloquean ejecución (puedes override manualmente).
:::

::: tip Cuándo usar
Motor central de implementación (paso 6 del flujo SDD-cycle).
:::

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.sync` (opcional)

---

### `/ai-framework:SDD-cycle:speckit.checklist`

Genera checklist customizada para validar quality de requirements ("Unit Tests for Requirements").

**Usage:**

```bash
# DESPUÉS de /ai-framework:SDD-cycle:speckit.analyze (antes de implement)
/ai-framework:SDD-cycle:speckit.checklist "{domain} requirements quality"

# Ejemplos
/ai-framework:SDD-cycle:speckit.checklist "UX requirements quality"
/ai-framework:SDD-cycle:speckit.checklist "API specification completeness"
/ai-framework:SDD-cycle:speckit.checklist "Security requirements coverage"
/ai-framework:SDD-cycle:speckit.checklist "Performance requirements clarity"
```

::: danger CRITICAL CONCEPT (de github/spec-kit)
Checklists son **UNIT TESTS FOR REQUIREMENTS WRITING** - validan quality, clarity, y completeness de requirements en given domain.

**NO son verification tests** (esos son tests de código).
**SON quality gates** para tus especificaciones.
:::

**Propósito Real:**

Si tu spec.md es código escrito en inglés, el checklist es su unit test suite.
Estás validando que tus REQUIREMENTS estén bien escritos, NO que tu implementación funcione.

**NOT for testing implementation:**

- ❌ NOT "Verify the button clicks correctly"
- ❌ NOT "Test error handling works"
- ❌ NOT "Confirm the API returns 200"

**FOR testing requirements quality:**

- ✅ "Are visual hierarchy requirements defined for all card types?" [Completeness]
- ✅ "Is 'prominent display' quantified with sizing/positioning?" [Clarity]
- ✅ "Are hover state requirements consistent across elements?" [Consistency]
- ✅ "Are accessibility requirements defined for keyboard navigation?" [Coverage]
- ✅ "Does the spec define what happens when logo fails to load?" [Edge Cases]

**Workflow Integration:**

```text
specify → clarify → plan → tasks → analyze
                                      ↓
                                  checklist (genera "tests")
                                      ↓
                        [TÚ marcas checkboxes revisando spec/plan]
                                      ↓
                                  implement
                                      ↓
                    (implement lee checklists, bloquea si incomplete)
```

**Por qué ANTES de implement:**

1. Detectas requirements ambiguos/incompletos ANTES de implementar
2. Corriges spec/plan con toda la información
3. Implementas con requirements de calidad alta
4. Evitas re-work por requirements malos

**Category Structure:**

- **Requirement Completeness** - Are all necessary requirements documented?
- **Requirement Clarity** - Are requirements specific y unambiguous?
- **Requirement Consistency** - Do requirements align sin conflicts?
- **Acceptance Criteria Quality** - Are success criteria measurable?
- **Scenario Coverage** - Are all flows/cases addressed?
- **Edge Case Coverage** - Are boundary conditions defined?
- **Non-Functional Requirements** - Performance, Security, Accessibility specified?

**Output:** `checklists/{domain}.md` para validación manual antes de implementar

**Tipos comunes:**

- `ux.md` - UX requirements quality
- `api.md` - API specification completeness
- `security.md` - Security requirements coverage
- `performance.md` - Performance criteria clarity

::: tip Cuándo usar
(Opcional) Después de analyze, antes de implement. Quality gate para requirements.
:::

::: warning Importante
Después de generar checklist, DEBES marcar checkboxes manualmente revisando tu spec/plan. implement bloqueará si checklists están incomplete.
:::

**Next Steps:** Marcar checkboxes → `➜ /ai-framework:SDD-cycle:speckit.implement`

---

### `/ai-framework:SDD-cycle:speckit.sync`

Sincroniza spec.md + plan.md + tasks.md a GitHub como child issue vinculado a parent PRP.

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.sync {parent_issue_number}

# Ejemplo
/ai-framework:SDD-cycle:speckit.sync 247
```

::: warning IMPORTANT
Este comando REQUIERE parent PRP issue. Specs must always be linked a PRP. Si no tienes PRP issue yet, run `/ai-framework:PRP-cycle:prp-sync` first.
:::

**Execution Steps:**

1. **Parse Arguments and Validate**
   - Parse parent issue number desde **$ARGUMENTS** (REQUIRED)
   - Detect feature desde current branch
   - Validate spec.md exists
   - **Verify not already synced** (prevent duplicates):
     - Read frontmatter desde `specs/{feature}/spec.md`
     - Check si `github:` field exists
     - Si exists: Show error con existing issue URL y STOP
   - Validate parent issue exists via `gh issue view`
   - Validate optional files (plan.md, tasks.md)

2. **Prepare Issue Content**:
   - Read spec artifacts (spec.md, plan.md si exists, tasks.md si exists)
   - Strip frontmatter desde spec.md
   - Format para GitHub Issue body:
     - If only spec.md: Include spec content
     - If plan.md exists: Append Implementation Plan section
     - If tasks.md exists: Append Task Breakdown section
   - Write formatted body a temporary file (safety para complex markdown)

3. **Create GitHub Issue and Link to Parent**:
   - Title: "Spec: {feature-name}" (convert kebab-case a Title Case)
   - Body: Use `--body-file` con temporary file
   - Labels: `spec`, `sdd`, `feature`
   - Add comment a parent issue: "Technical specification created: #{spec_issue_number}"

4. **Update Local Spec File**: Update frontmatter con `github`, `github_synced`, `parent_prd`

5. **Create GitHub Mapping File**: `specs/{feature}/github-mapping.md` con parent PRD, spec issue, timestamp

**Timing Recommendation:**

Run `/speckit.sync` AFTER implementation es complete y validated. Esto ensures:

- GitHub Issue documents what was actually built (not speculation)
- Spec + Plan + Tasks son 100% accurate con final code
- Stakeholders see results, not work-in-progress
- Zero need para re-sync o duplicate issues

**Stakeholder View:**

- Business team tracks PRP issue (parent) - high-level requirements
- Tech team tracks Spec issue (child) - technical documentation de what was built
- Parent-child relationship via "Parent PRP: #247" en spec body
- Clear separation de concerns: business requirements (PRP) vs technical implementation (Spec)

::: tip Cuándo usar
(Opcional) DESPUÉS de implementación completa - documenta lo que fue construido.
:::

**Next Steps:** `➜ /ai-framework:git-github:commit` → `/ai-framework:git-github:pullrequest`

---

### `/ai-framework:SDD-cycle:speckit.constitution`

Crea o actualiza constitución del proyecto con principios fundamentales.

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.constitution
```

::: danger RESTRICCIÓN
NO EJECUTAR sin autorización directa del usuario.
:::

**Execution Flow:**

1. Load existing constitution template at `.specify/memory/constitution.md`
2. Identify every placeholder token de form `[ALL_CAPS_IDENTIFIER]`
3. Collect/derive values para placeholders:
   - If user input supplies value, use it
   - Otherwise infer desde existing repo context
   - For governance dates: RATIFICATION_DATE, LAST_AMENDED_DATE
   - CONSTITUTION_VERSION must increment según semantic versioning:
     - MAJOR: Backward incompatible governance/principle removals o redefinitions
     - MINOR: New principle/section added o materially expanded guidance
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements
4. Draft updated constitution content (replace every placeholder)
5. Consistency propagation checklist:
   - Read `.specify/templates/plan-template.md`
   - Read `.specify/templates/spec-template.md`
   - Read `.specify/templates/tasks-template.md`
   - Read each command file en `.specify/templates/commands/*.md`
   - Update references a principles changed
6. Produce Sync Impact Report (prepend como HTML comment):
   - Version change: old → new
   - List de modified principles
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending)
   - Follow-up TODOs
7. Validation antes de final output
8. Write completed constitution back a `.specify/memory/constitution.md`

**Output:** `.specify/memory/constitution.md` actualizada con sync impact report

::: tip Cuándo usar
Setup inicial o actualización de principios fundamentales.
:::

---

## Git & GitHub

### `/ai-framework:git-github:commit`

Commits semánticos con agrupación automática y soporte corporativo.

**Casos de Uso:**

```bash
# 1. Formato Convencional (proyectos open source)
/ai-framework:git-github:commit "feat(auth): add OAuth2 support"

# 2. Task ID solo (tipo automático desde archivos modificados)
/ai-framework:git-github:commit "TRV-345 implementar autenticación"
# → feat|TRV-345|20251023|implementar autenticación

# 3. Tipo + Task ID (RECOMENDADO - control total)
/ai-framework:git-github:commit "refactor: TRV-345 mejorar módulo auth"
# → refactor|TRV-345|20251023|mejorar módulo auth

# 4. Auto-commit (cuando no tienes Task ID)
/ai-framework:git-github:commit "all changes"
# → Genera mensaje basado en archivos modificados
```

**¿Qué formato usar?**

| Tu Input                          | Output del Commit                             | ¿Cuándo usarlo?                      |
| --------------------------------- | --------------------------------------------- | ------------------------------------ |
| `"feat: add feature"`             | `feat: add feature`                           | Proyectos sin Task IDs               |
| `"TRV-345 descripción"`           | `feat\|TRV-345\|20251023\|descripción` (auto) | Confías en auto-detección del tipo   |
| `"refactor: TRV-345 descripción"` | `refactor\|TRV-345\|20251023\|descripción`    | **Quieres control del tipo (mejor)** |
| `"all changes"`                   | Auto-generado según archivos                  | Commits rápidos sin Task ID          |

::: tip Mejor Práctica
**Usa siempre `tipo: TASK-ID descripción`** cuando tengas Task ID. Te da control total y evita sorpresas con el auto-mapping.
:::

**Formato Corporativo - Template:**

```
Tipo|TaskID|YYYYMMDD|Descripción
├─ Tipo: feat, fix, refactor, chore, docs, test, security
├─ TaskID: TRV-345, BUG-287, PROJ-123 (patrón: LETRAS-NÚMEROS)
├─ Fecha: Generada automáticamente (YYYYMMDD)
└─ Descripción: Breve resumen del cambio
```

**Auto-mapping de Tipos (solo cuando usas caso 2):**

- Archivos `config/`, `*.md` → `chore`
- Archivos `docs/`, `README` → `docs`
- Archivos `scripts/`, `*setup*` → `fix`
- Archivos `*test*`, `*.test.*` → `test`
- Otros archivos → `feat`

**Agrupación Inteligente:**

- **Multiple commits**: Si modificas 2+ categorías (config + código, docs + tests)
- **Single commit**: Si modificas solo una categoría o pocos archivos

**Output:** Commits agrupados por tipo con mensajes semánticos

::: tip Cuándo usar
Después de completar cambios.
:::

**Next Steps:** `➜ /ai-framework:git-github:pullrequest`

---

### `/ai-framework:git-github:pullrequest`

Crea PR con security review automático, detección de formato corporativo y título personalizable.

**Casos de Uso:**

```bash
# Desde feature branch → PR a main
/ai-framework:git-github:pullrequest main

# Desde feature branch → PR a develop
/ai-framework:git-github:pullrequest develop

# Desde rama protegida (main) → Crea temp branch automática
/ai-framework:git-github:pullrequest main
# → Crea temp-{keywords}-{timestamp} automáticamente
```

**¿Qué hace el comando?**

1. **Security Review Automático** (BLOCKING)
   - Analiza código en busca de vulnerabilidades
   - ❌ **BLOQUEA PR** si encuentra HIGH severity (confidence ≥ 8.0)
   - ⏱️ Timeout: 80 segundos máximo

2. **Título del PR - Formato Corporativo**
   - **Si detecta commits corporativos** (`feat|TRV-345|20251023|descripción`):
     - **Te pregunta**: ¿Usar primer commit o título personalizado?
     - **Opción A**: Usa primer commit como está
     - **Opción B**: Ingresas título custom: `refactor|TRV-350|20251023|mejora auth`
   - **Si detecta commits convencionales**: Usa primer commit directamente

3. **Branch Protection Handling**
   - **Si estás en main/master/develop**: Crea temp branch automática
   - **Si estás en feature branch**: Usa branch actual

4. **PR Body Automático**
   - Summary: Resumen de cambios por tipo de commit
   - Changes Made: Lista de commits
   - Files & Impact: Archivos modificados + líneas
   - Test Plan: Checklist basada en tipo de cambio
   - Breaking Changes: Si detecta BREAKING

**Validaciones Automáticas:**

- ✅ Target branch existe
- ✅ Hay commits para PR
- ✅ Branch no está desactualizada vs remote
- ✅ Security review aprobado

::: warning Security Review es BLOCKING
Si encuentra vulnerabilidades HIGH, el comando FALLA y NO crea el PR. Debes corregir el código primero.
:::

::: tip Título Personalizado (Formato Corporativo)
Cuando tienes múltiples Task IDs en commits (TRV-345, BUG-287, PROJ-100), el comando te pregunta si quieres un título custom que refleje todos los cambios.
:::

**Output:** PR URL + security review report

::: tip Cuándo usar
Después de commits finales, listo para code review.
:::

**Next Steps:** Después de merge → `/ai-framework:git-github:cleanup`

---

### `/ai-framework:git-github:cleanup`

Limpia feature branch y sincroniza con base branch después de merge.

**Casos de Uso:**

```bash
# Auto-detect base branch
/ai-framework:git-github:cleanup

# Especificar base branch explícitamente
/ai-framework:git-github:cleanup main
/ai-framework:git-github:cleanup develop
```

**¿Qué hace?**

1. **Valida Estado Actual**
   - ❌ Si estás en main/master/develop: Error "Ya estás en rama base"
   - ✅ Si estás en feature branch: Continúa

2. **Detecta Base Branch**
   - Con argumento: usa el especificado
   - Sin argumento: auto-detecta (main → master → develop)

3. **Workflow de Limpieza**
   - `git checkout {base}` - Cambia a base branch
   - `git branch -D {feature}` - Elimina feature branch local
   - `git pull origin {base} --ff-only` - Sincroniza con remote

**Output:** Workspace limpio en base branch + summary de operaciones

::: info Branch Remota
GitHub elimina automáticamente la branch remota al mergear el PR. No necesitas limpiarla manualmente.
:::

::: tip Cuándo usar
Después de merge exitoso del PR.
:::

---

## Gestión de Worktrees

::: tip Worktree vs Branch: Entendiendo la Diferencia
Ver sección detallada en documentación original que explica cuándo usar cada uno.
:::

### Matriz de Decisión

| Necesidad                          | Usa Branch | Usa Worktree |
| ---------------------------------- | ---------- | ------------ |
| Desarrollo lineal (1 feature)      | ✅         | ❌           |
| Múltiples features en paralelo     | ❌         | ✅           |
| Bug fix urgente (no interrumpir)   | ❌         | ✅           |
| Experimentación/POC desechable     | ❌         | ✅           |
| Setup simple sin overhead          | ✅         | ❌           |
| Trabajo con main/develop inestable | ❌         | ✅           |

---

### `/ai-framework:git-github:worktree:create`

Crea worktree aislado en directorio sibling con rama nueva y upstream configurado.

**Usage:**

```bash
/ai-framework:git-github:worktree:create "{objetivo}" {parent-branch}

# Ejemplos
/ai-framework:git-github:worktree:create "implementar OAuth" main
/ai-framework:git-github:worktree:create "fix bug pagos" develop
```

**Execution Steps:**

1. **Argument validation**:
   - Count arguments (must be exactly 2)
   - Capture first argument como `objetivo_descripcion`
   - Capture second argument como `parent_branch`

2. **Working directory validation**:
   - Execute `git status --porcelain` para capture pending changes
   - If output exists (uncommitted changes): Error "Directorio no limpio" y TERMINATE
   - If no changes: Continue

3. **Parent branch validation**:
   - Execute `git show-ref --verify --quiet refs/heads/$parent_branch`
   - If fails: Error "Branch no existe" + show available branches y TERMINATE
   - If exists: Continue

4. **Generate consistent names**:
   - Convert `objetivo_descripcion` a valid slug: lowercase + replace non-alphanumeric con `-`
   - Build `worktree_name`: "worktree-$objetivo_slug"
   - Build `branch_name`: Identical a `worktree_name`
   - Build `worktree_path`: "../$worktree_name"

5. **Check for collisions**:
   - Directory collision check: `[ -d "$worktree_path" ]`
   - Branch collision check: `git show-ref --verify --quiet refs/heads/$branch_name`
   - If either exists: Error y TERMINATE

6. **Prepare parent branch**:
   - Execute `git checkout "$parent_branch"`
   - Execute `git pull origin "$parent_branch"` (update desde remote)
   - If pull fails: Warning pero continue

7. **Create worktree**:
   - Execute `git worktree add "$worktree_path" -b "$branch_name"`
   - If fails: Error y terminate

8. **Open IDE automatically**:
   - Detect available IDE: `which code` (VS Code) o `which cursor` (Cursor)
   - If found: Execute `(cd "$worktree_path" && [IDE] . --new-window)`
   - If not found: Warning "Abre manualmente"

9. **Logging and final result**:
   - Create logs directory: `.claude/logs/{date}/`
   - Add JSONL entry a `worktree_operations.jsonl`
   - Show critical instructions:

**Post-creación (importante):**

```
⚠️ IDE abierto automáticamente, pero debes:

PASO 1 - En la nueva ventana del IDE:
  Abrir Terminal integrado (Cmd+` o View → Terminal)

PASO 2 - Verificar directorio correcto:
  pwd  # Debe mostrar: ../worktree-XXX/

PASO 3 - Iniciar nueva sesión Claude Code:
  claude /workflow:session-start

❌ SI NO HACES ESTO: Claude seguirá trabajando en el directorio
   anterior y NO funcionará correctamente el worktree.

✅ SOLO así tendrás sesiones Claude Code paralelas funcionando.
```

**Output:**

- Crea worktree: `../worktree-{objetivo}/`
- Crea branch: `worktree-{objetivo}` (mismo nombre que directorio)
- Abre IDE automáticamente en nueva ventana (detecta code/cursor)
- Valida directorio limpio antes de crear

::: tip Cuándo usar

- Trabajo paralelo en múltiples features
- Bug fixes urgentes sin interrumpir trabajo actual
- Experimentación/POC sin afectar workspace principal
  :::

---

### `/ai-framework:git-github:worktree:cleanup`

Elimina worktrees con validación de ownership y cleanup triple (worktree/local/remote).

**Usage:**

```bash
/ai-framework:git-github:worktree:cleanup              # Discovery mode
/ai-framework:git-github:worktree:cleanup {worktree1}  # Cleanup específico
```

**Restrictions:**

- Only removes worktrees/branches created por you
- Never touches protected branches (main, develop, qa, staging, master)
- Requires clean state (no uncommitted changes)

**Discovery Mode (no arguments):**

Lists available worktrees con suggested commands.

**Phase 1: Discovery**

- Get current canonical path
- Process worktrees usando `git worktree list --porcelain`
- Filter by owner (only user's worktrees)
- Filter out current directory
- Build numbered list

**Phase 2: User Interaction**

- Show numbered list: "Tus worktrees disponibles para eliminar:"
- Ask: "Selecciona números separados por espacios (ej: 1 2) o 'todos':"
- WAIT para user response
- Parse input y convert a worktree names
- Continue con cleanup flow

**Cleanup Mode (with arguments):**

**Per-target validations:**

1. Format validation (alphanumeric + hyphens/underscores only)
2. Protected branch validation (skip protected branches)
3. Current directory validation (cannot delete where you are)
4. Existence validation (verify worktree exists)
5. Ownership validation (cross-platform compatible):
   - macOS: `stat -f %Su "$path"`
   - Linux: `stat -c %U "$path"`
   - Compare con `whoami`
6. Clean state validation (no uncommitted changes)

**User Confirmation:**

- Output summary de valid targets
- Ask: "¿Confirmas la eliminación? Responde 'ELIMINAR' para proceder:"
- WAIT para user response
- If response != "ELIMINAR": Cancel y terminate
- If response == "ELIMINAR": Proceed

**Dual Atomic Cleanup:**
Para cada confirmed target:

- Remove worktree: `git worktree remove "$target"`
- Remove local branch: `git branch -D "$branch_name"`

**Logging and Final Cleanup:**

- Log operation en JSONL format
- Execute `git remote prune origin`
- Show results report

**Update Current Branch:**

- Execute `git pull`
- If fails: Warning pero continue
- If success: "Updated from remote"

**Output:** Triple cleanup + regresa automáticamente a main

**Logging Format:** `.claude/logs/{date}/worktree_operations.jsonl`

::: tip Cuándo usar
Después de mergear PRs.
:::

---

## Utilidades

### `/ai-framework:utils:understand`

Análisis comprehensivo de arquitectura, patrones y dependencies.

**Usage:**

```bash
/ai-framework:utils:understand
/ai-framework:utils:understand "specific area"

# Ejemplos
/ai-framework:utils:understand
/ai-framework:utils:understand "authentication module"
```

**Phases:**

**Phase 1: Project Discovery**
Usando native tools:

- **Glob** para map entire project structure
- **Read** key files (README, docs, configs)
- **Grep** para identify technology patterns
- **Read** entry points y main files

Discover:

- Project type y main technologies
- Architecture patterns (MVC, microservices, etc.)
- Directory structure y organization
- Dependencies y external integrations
- Build y deployment setup

**Phase 2: Code Architecture Analysis**

- **Entry points**: Main files, index files, app initializers
- **Core modules**: Business logic organization
- **Data layer**: Database, models, repositories
- **API layer**: Routes, controllers, endpoints
- **Frontend**: Components, views, templates
- **Configuration**: Environment setup, constants
- **Testing**: Test structure y coverage

**Phase 3: Pattern Recognition**
Identify established patterns:

- Naming conventions para files y functions
- Code style y formatting rules
- Error handling approaches
- Authentication/authorization flow
- State management strategy
- Communication patterns between modules

**Phase 4: Dependency Mapping**

- Internal dependencies between modules
- External library usage patterns
- Service integrations
- API dependencies
- Database relationships
- Asset y resource management

**Phase 5: Integration Analysis**
Identify how components interact:

- API endpoints y their consumers
- Database queries y their callers
- Event systems y listeners
- Shared utilities y helpers
- Cross-cutting concerns (logging, auth)

**Output Format:**

```markdown
PROJECT OVERVIEW
├── Architecture: [Type]
├── Main Technologies: [List]
├── Key Patterns: [List]
└── Entry Point: [File]

COMPONENT MAP
├── Frontend
│ └── [Structure]
├── Backend
│ └── [Structure]
├── Database
│ └── [Schema approach]
└── Tests
└── [Test strategy]

INTEGRATION POINTS
├── API Endpoints: [List]
├── Data Flow: [Description]
├── Dependencies: [Internal/External]
└── Cross-cutting: [Logging, Auth, etc.]

KEY INSIGHTS

- [Important finding 1]
- [Important finding 2]
- [Unique patterns]
- [Potential issues]
```

**When to Use:**

- **MANDATORY**: New codebase, unknown architecture, major refactor (Size L)
- **RECOMMENDED**: Cambios en múltiples módulos (Size M), dependencias entre proyectos
- **OPTIONAL**: Single-file fixes (Size S), well-understood areas

**Success Criteria - Analysis complete cuando answerable:**

- [ ] What happens cuando [core user action]?
- [ ] Where would I add [typical feature]?
- [ ] What breaks si I change [critical module]?
- [ ] Can I draw data flow desde request a response?

::: tip Cuándo usar
SIEMPRE antes de implementar feature compleja.
:::

---

### `/ai-framework:utils:three-experts`

Panel de 3 expertos (backend/frontend/security) genera plan consensuado.

**Usage:**

```bash
/ai-framework:utils:three-experts {goal}

# Ejemplo
/ai-framework:utils:three-experts "Design scalable authentication system"
```

**Expert Panel (Fixed):**

Use these 3 native Claude Code agents:

1. **backend-architect** → API design, data modeling, services architecture
2. **frontend-developer** → UI components, user flows, client-side implementation
3. **security-reviewer** → Threat modeling, compliance, security validation

(_No agent discovery required - these are available en Claude Code memory_)

**Workflow: 2 Rounds**

**Round 1: Proposals (Independent)**

Cada expert provides their perspective:

**Backend Architect:**

- API endpoints y contracts
- Data model y schema
- Service architecture y dependencies
- Performance considerations

**Frontend Developer:**

- UI components y user flows
- State management approach
- Client-side integration patterns
- Accessibility y UX considerations

**Security Reviewer:**

- Threat model y attack vectors
- Authentication/authorization design
- Data protection y privacy
- Compliance requirements

**Round 2: Synthesis & Decision**

- Cross-review each proposal
- Identify integration points y conflicts
- Build consensus on unified approach
- Define implementation priorities
- Create final implementation plan

**Output: PLAN.md Generation**

Generate single artifact usando template con sections:

- OBJETIVO & SCOPE
- DECISIONES TÉCNICAS (Backend, Frontend, Seguridad)
- ✅ TAREAS CRÍTICAS
- CRITERIOS DE ÉXITO

**Constitutional Compliance:**

- **Value/Complexity**: ≥2x ratio (simple workflow, high value output)
- **AI-First**: Fully executable por AI agents via Task tool
- **Reuse First**: Uses existing Claude Code native agents
- **Simplicity**: No flags, minimal configuration, focused output
- **TDD-Ready**: Plan includes testing strategy y criteria

::: tip Cuándo usar
Features complejas que requieren múltiples perspectivas.
:::

---

### `/ai-framework:utils:docs`

Analiza y actualiza documentación usando specialist agents.

**Usage:**

```bash
/ai-framework:utils:docs                 # Analizar toda la docs
/ai-framework:utils:docs README API      # Focus específico

# Ejemplos
/ai-framework:utils:docs
/ai-framework:utils:docs README CHANGELOG
```

**Process:**

1. **Analyze** existing documentation (README, CHANGELOG, docs/\*)
2. **Identify** gaps y outdated content
3. **Delegate** a documentation specialist via Task tool
4. **Update** o create documentation as needed

**Capabilities:**

- Gap analysis y documentation planning
- Content creation con project templates
- Technical accuracy validation
- Integration con specialist agents para complex documentation tasks

**Output:** Documentación actualizada con análisis de calidad

::: tip Cuándo usar
Después de features o cambios importantes.
:::

---

### `/ai-framework:utils:polish`

Polishing meticuloso de archivos AI-generated. Preserva 100% funcionalidad mientras mejora calidad.

**Usage:**

```bash
/ai-framework:utils:polish {file_paths}

# Ejemplo
/ai-framework:utils:polish src/auth.ts src/components/Login.tsx
```

::: danger CRITICAL DISCLAIMER
**POLISHING ≠ SCOPE REDUCTION**

Este comando es para **REFINEMENT**, not **FUNCTIONAL REDUCTION**.
:::

**Mandate:** Si file serves critical user workflow (daily use, core functionality), prioritize COMPLETE PRESERVATION over optimization.

**Examples of CORRECT polishing:**

- Fix syntax errors, inconsistent formatting, broken links
- Eliminate promotional language, redundant explanations
- Standardize naming conventions, improve clarity
- Remove duplicate information, optimize structure

**Examples of INCORRECT reduction:**

- Removing methodology sections desde analysis commands
- Cutting algorithm logic para "brevity"
- Eliminating core features para "simplify"
- Reducing command capabilities para "efficiency"

**Universal Polishing Protocol (5 Phases):**

**Phase 1: Syntax & Structure Validation**

1. Documentation Files (.md, .rst, .txt)
2. Configuration Files (.json, .yaml, .env)
3. Data Files (.csv, .sql, .xml)
4. Code Files (any language)
5. Scripts & Templates (.sh, .html, .css)

**Phase 2: Logical Coherence Audit** 6. Information Flow 7. Configuration Logic 8. Data Integrity 9. Functional Logic 10. Template Logic

**Phase 3: Consistency & Standards Enforcement** 11. Naming Conventions 12. Format Standardization 13. Language Standards 14. Cross-file Consistency 15. Professional Standards

**Phase 4: Redundancy & Optimization Elimination** 16. Content Duplication 17. Unused Elements 18. Complexity Reduction 19. Performance Optimization 20. Resource Cleanup

**Phase 5: Communication & Content Quality** 21. Professional Language 22. Documentation Clarity 23. Content Accuracy

**Zero-Tolerance Polish Standards:**

**Critical Issues (Must Fix):**

1. Syntax Errors
2. Security Vulnerabilities
3. Broken References
4. Data Corruption
5. Functional Failures

**High Priority Issues:**

1. Inconsistent Formatting
2. Performance Problems
3. Clarity Issues
4. Standard Violations
5. Redundant Content

::: tip Importante
Preserva 100% funcionalidad mientras mejora calidad.
:::

::: tip Cuándo usar
Refinar contenido generado por AI.
:::

---

### `/ai-framework:utils:deep-research`

Professional audit con metodología sistemática y validación de múltiples fuentes.

**Usage:**

```bash
/ai-framework:utils:deep-research "{investigation topic}"

# Ejemplo
/ai-framework:utils:deep-research "OAuth 2.0 security best practices for microservices"
```

**Professional Audit Protocol:**

**Phase 1: Engagement Planning & Risk Assessment**

1. Scope Definition - Establish clear investigation boundaries
2. Risk Matrix Development - Identify key risk areas
3. Source Strategy - Plan systematic approach a primary/secondary/tertiary sources
4. Quality Gates - Define verification checkpoints

**Phase 2: Evidence Gathering & Documentation** 5. Multi-Source Validation - Minimum 3 independent sources para material claims 6. Primary Source Priority - Government, academic, regulatory data first 7. Industry Intelligence - Consulting reports, professional analysis 8. Real-time Verification - Current data validation

**Phase 3: Analytical Procedures & Verification** 9. Substantive Testing - Deep-dive analysis de core findings 10. Cross-validation Protocol - Verify claims across multiple reliable sources 11. Gap Analysis - Identify information limitations 12. Professional Judgment - Apply expert-level analytical reasoning

**Source Hierarchies:**

**Tier 1 (Primary - Highest Reliability):**

- Government/Regulatory: .gov sites, central banks, SEC filings
- Academic: Peer-reviewed journals, university research
- Official Data: World Bank, IMF, OECD, WHO
- Legal/Regulatory: Court decisions, regulatory guidance

**Tier 2 (Industry Authoritative - High Reliability):**

- Major Consulting: Deloitte, PwC, EY, KPMG research
- Strategy Consulting: McKinsey Global Institute, BCG, Bain
- Financial Intelligence: Bloomberg, Reuters, Financial Times
- Research Firms: Gartner, Forrester, IDC

**Tier 3 (Corroborative - Supporting Evidence):**

- Quality Journalism: WSJ, The Economist, HBR
- Industry Bodies: Professional associations
- Corporate Intelligence: Annual reports, 10-K filings
- Expert Analysis: Verified subject matter expert commentary

**Anti-Hallucination Rules:**

1. **Source Everything** - Every factual claim requires verifiable source con URL y date
2. **Multiple Sources** - Material findings require minimum 3 independent confirmations
3. **Document Conflicts** - All conflicting information must be documented
4. **State Uncertainty** - Explicitly declare cuando evidence insufficient
5. **Show Methods** - Document how each piece de evidence was obtained
6. **Attribute Sources** - Never present unattributed information as fact

**Deliverable Structure:**

1. **Executive Summary**: Key findings con confidence levels
2. **Methodology & Source Verification**: Complete source hierarchy used
3. **Detailed Findings & Evidence**: Each finding con full source documentation
4. **Risk Assessment & Recommendations**: Risk matrix con strategic recommendations

**Output:** Reporte de investigación con fuentes verificadas

::: tip Cuándo usar
Investigaciones complejas, due diligence, market research.
:::

---

### `/ai-framework:utils:changelog`

Actualiza CHANGELOG.md con PRs mergeados desde el último release (Keep a Changelog format).

**Usage:**

```bash
/ai-framework:utils:changelog    # Auto-detectar PRs pendientes

# Ejemplo
/ai-framework:utils:changelog
```

**Execution Steps:**

1. **Validación de herramientas y archivos**:
   - Validate `gh` (GitHub CLI) installed
   - Validate `jq` (JSON processor) installed
   - Validate `CHANGELOG.md` exists en raíz
   - Validate sección `[No Publicado]` exists

2. **Auto-detección de PRs pendientes**:
   - Get último PR documentado desde CHANGELOG (buscar `PR #número`)
   - Get PRs mergeados desde git log (commits con `#número` o `Merge pull request`)
   - Filter solo PRs posteriores al último documentado
   - Validate PRs en GitHub usando `gh pr view`
   - Verify estado MERGED
   - Detect duplicados (skip si PR ya existe en CHANGELOG)
   - If no new PRs: Show "CHANGELOG actualizado" y exit

3. **Actualización de CHANGELOG**:
   - Para cada PR nuevo:
     - Sanitizar título (prevenir injection)
     - Limpiar prefijo de tipo (`feat:`, `fix:`, etc.)
     - Insertar en sección `[No Publicado]` con formato: `- título (PR #número)`
   - Maintain Keep a Changelog format
   - Show count de PRs agregados

4. **Commit automático**:
   - Stage CHANGELOG.md
   - Create commit: `docs: update CHANGELOG with PRs {lista}`
   - Show success y suggest `/release` para publicar

**Output:** CHANGELOG.md actualizado + commit automático

::: tip Cuándo usar
Después de merges para mantener CHANGELOG actualizado. Luego usar `/release` para publicar versión.
:::

**Next Steps:** `➜ /ai-framework:utils:release` (para crear nueva versión)

---

### `/ai-framework:utils:release`

Ejecuta workflow completo de release: bump versión → actualizar CHANGELOG → sync → commit/tag → push.

**Usage:**

```bash
/ai-framework:utils:release    # Workflow interactivo

# Ejemplo
/ai-framework:utils:release
```

**Pre-requisitos:**

- CHANGELOG.md actualizado con `/changelog`
- Sección `[No Publicado]` con cambios documentados
- package.json con campo `version`

**Execution Steps:**

1. **Validar herramientas y archivos**:
   - Validate `npm`, `jq` installed
   - Validate `CHANGELOG.md` y `package.json` exist
   - Validate sección `[No Publicado]` exists
   - Verify `[No Publicado]` contiene cambios reales (no placeholder)

2. **Preguntar tipo de release**:
   - Show versión actual desde `package.json`
   - Opciones interactivas:
     - `[1] patch` - Bug fixes (X.X.X+1)
     - `[2] minor` - New features (X.Y+1.0)
     - `[3] major` - Breaking changes (X+1.0.0)
     - `[4] Cancelar`
   - Capturar elección

3. **Ejecutar npm version** (auto-dispara sync):
   - Execute `npm version [tipo]`
   - `npm version` automáticamente:
     - Bump version en package.json
     - Ejecuta `scripts/sync-versions.cjs` (hook)
     - Sincroniza: config.js, README.md, docs/changelog.md
     - Crea commit: `chore: release vX.X.X`
     - Crea tag: `vX.X.X`

4. **Actualizar CHANGELOG con versión**:
   - Reemplazar `[No Publicado]` con `[version] - YYYY-MM-DD`
   - Crear nueva sección `[No Publicado]` vacía
   - Update commit de release con CHANGELOG modificado (`git commit --amend`)

5. **Verificar commit y tag**:
   - Verify commit de release existe
   - Verify tag `vX.X.X` creado
   - Show detalles

6. **Preguntar si push**:
   - Show resumen: commit, tag, archivos sincronizados
   - Opciones: `[y/N]` para push a origin con `--follow-tags`
   - If yes: `git push origin {branch} --follow-tags`
   - If no: Show instrucciones para push manual

**Output:** Release completo (local o remoto según elección)

::: tip Cuándo usar
Después de `/changelog` cuando estés listo para publicar nueva versión.
:::

::: warning Auto-sync
`npm version` ejecuta automáticamente `scripts/sync-versions.cjs` que sincroniza versiones en:

- human-handbook/.vitepress/config.js
- README.md
- human-handbook/docs/changelog.md
  :::

**Next Steps:** Push con tags si no se hizo automáticamente

---

### `/ai-framework:utils:project-init`

Initialize o update project context con deep analysis y recomendaciones de agentes.

**Usage:**

```bash
/ai-framework:utils:project-init
/ai-framework:utils:project-init deep   # Force deep analysis
```

**Reuses:** `/ai-framework:utils:understand` phases 1-5 para systematic discovery

**Execution Flow:**

**Phase 1: Detect Existing Context**

- Check si `.specify/memory/project-context.md` exists
- If YES y no "deep" argument: Confirm overwrite
- If YES y "deep" argument: Skip confirmation, force overwrite
- If NO: Proceed directly

**Phase 2: Deep Discovery** (Reuse understand.md logic)

- Execute systematic analysis siguiendo `/utils:understand` methodology
- Project Discovery, Code Architecture Analysis, Pattern Recognition, Dependency Mapping, Integration Analysis

**Phase 3: Tech Stack Detection (Extended)**

- Parse exact versions y all dependencies desde package managers
- Node.js: Parse package.json para node_version + dependencies
- Python: Parse requirements.txt/pyproject.toml para python_version + frameworks
- Ruby: Parse Gemfile para ruby_version + Rails/RSpec
- PHP: Parse composer.json para php_version + Laravel/Symfony
- Go: Parse go.mod para go_version
- Infrastructure: Docker, Kubernetes, Terraform, CI/CD detection

**Phase 4: Agent Mapping + Gap Analysis**

**A. Load Agent Registry** desde `.claude-plugin/agents/**/*.md`

**B. Map Tech → Agents** (same registry como workspace-status.py):

```yaml
Core (Always):
  - code-quality-reviewer, systematic-debugger, test-automator

Languages:
  python: [python-pro]
  javascript: [javascript-pro]
  typescript: [typescript-pro, frontend-developer]
  ruby: [ruby-pro]
  php: [php-pro]

Frameworks:
  react|nextjs: [frontend-developer]
  fastapi|django|flask: [python-pro, backend-architect]
  express|fastify: [javascript-pro, backend-architect]

Databases:
  postgres|mysql|mongodb: [database-optimizer, database-admin]

Infrastructure:
  docker: [deployment-engineer, devops-troubleshooter]
  kubernetes: [kubernetes-architect, deployment-engineer]
  terraform: [terraform-specialist, cloud-architect]

APIs:
  graphql: [graphql-architect]
  rest|openapi: [backend-architect, api-documenter]
```

**C. Gap Detection:**

- Check dependencies para unmapped tech
- If gaps found: Display recommendation para create custom agent

**Phase 5: Generate Comprehensive project-context.md** con sections:

- Technology Stack (Core, Key Dependencies, Infrastructure)
- Architecture (Pattern, Entry Point, Directory tree)
- Code Patterns (Naming Conventions, Error Handling, Testing Strategy)
- Recommended Agents (Core, Project-Specific)
- Integration Points
- ⚠️ Potential Issues

**Phase 6: Update CLAUDE.md Reference**

- Check si `CLAUDE.md` already references `project-context.md`
- If not: Add reference after Constitution section

**Output:**

```
✅ Project context initialized (deep analysis)

Stack Detected:
   - [Language] [version]
   - [Framework] [version]
   - [Database]

Recommended Agents ([total]):
   Core: [list]
   Project-Specific: [list based on tech]

Generated:
   - .specify/memory/project-context.md
   - CLAUDE.md (reference added if missing)

⚠️ Potential Issues Flagged: [list]

Next: Claude ahora conoce tu proyecto en profundidad.
```

::: tip Cuándo usar
Setup inicial, cuando architecture evoluciona.
:::

---

### `/ai-framework:utils:setup-dependencies`

Instala dependencias esenciales faltantes con platform detection.

**Usage:**

```bash
/ai-framework:utils:setup-dependencies
```

**Execution Steps:**

1. **Detect Platform**:
   - Execute `uname -s`
   - Determine: darwin (macOS) / linux / unknown

2. **Dependency Registry** (single source of truth):

```bash
# Format: tool_name|installer|platforms|purpose
DEPS=(
    "terminal-notifier|brew|darwin|Notificaciones de tareas completadas"
    "black|pip|all|Auto-formateo de código Python"
    # Future additions here
)
```

3. **Discover Missing Dependencies**:
   - Process registry y detect faltantes
   - Check si tool installed con `command -v "$tool"`
   - Build list de missing tools

4. **Display Status**:
   - If all installed: "✅ Todas las dependencias ya instaladas" y exit
   - If missing: Show list + purposes + platform

5. **Confirm Installation**:
   - Ask: "¿Proceder con la instalación? (S/n):"
   - If NO: Show manual installation commands y exit
   - If YES: Continue

6. **Group by Installer**:
   - Group dependencies: brew_deps, pip_deps, npm_deps

7. **Install by Package Manager**:
   - **Homebrew (macOS)**: `brew install $brew_deps`
   - **pip (Python)**: `pip install $pip_deps` o `pip3 install $pip_deps`
   - **npm (Node)**: `npm install -g $npm_deps`

8. **Verify Installation**:
   - Para cada tool: Verify con `command -v`
   - Show "✅ $tool instalado" o "❌ $tool falló"

9. **Report Results**:
   - If all installed: "✅ Instalación completada"
   - If some failed: "⚠️ Algunas instalaciones fallaron" + manual instructions

**Extension Guide:**

Para agregar nuevas dependencias:

1. Add line al array DEPS: `"tool_name|installer|platforms|purpose"`
2. Supported: installers (brew, pip, npm, apt), platforms (darwin, linux, all)
3. Automáticamente detecta, agrupa, e instala

::: tip Cuándo usar
Setup inicial, cuando GitHub CLI o otras tools no están instaladas.
:::

---

## Workflows Completos

### Workflow Comparison Table

| Workflow          | Comandos Core (ORDEN CORRECTO)                                                                                                                     |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Feature nueva** | `specify` → `clarify` → `plan` → `tasks` → `[analyze]` → `[checklist]` → `implement` → `[sync]`                                                    |
| **Con PRP**       | `prp-new` → `prp-sync` → `specify --from-issue` → `clarify` → `plan` → `tasks` → `[analyze]` → `[checklist]` → `implement` → `[sync]`              |
| **Bug fix**       | `worktree:create` → `understand` → `specify` → `clarify` → `plan` → `tasks` → `[analyze]` → `[checklist]` → `implement` → `commit` → `pullrequest` |
| **Post-merge**    | `changelog` → `worktree:cleanup` → `docs` (o usar `/ai-framework:git-github:cleanup`)                                                              |

::: tip Comandos Opcionales
`[analyze]`, `[checklist]`, `[sync]` son opcionales. checklist es quality gate antes de implementar.
:::

---

## Tips de Uso

### Flujo Óptimo

::: tip Paso Valioso
`/ai-framework:SDD-cycle:speckit.clarify` - detecta problemas antes de implementar. ROI 100:1 (2 min save 4 hours)
:::

::: tip SIEMPRE

- Usar worktrees para trabajo paralelo - evita branch pollution
- Dejar `/ai-framework:git-github:pullrequest` ejecutar security review
  :::

::: info OPCIONAL

- `analyze` - Valida consistencia entre artefactos (después de tasks, antes de implement)
- `checklist` - Quality gate para requirements (antes de implement, genera "unit tests for requirements")
- `sync` - Documenta en GitHub lo que fue construido (después de implement)
  :::

### Comandos Pre-Production

1. `/ai-framework:SDD-cycle:speckit.implement` - TDD enforcement automático
2. `/ai-framework:git-github:pullrequest` - Security review blocking
3. `/ai-framework:utils:changelog` - Keep a Changelog compliance

### Parallel Execution

- `/ai-framework:SDD-cycle:speckit.implement` ejecuta agents en paralelo automáticamente
- Tasks marcadas `[P]` se ejecutan concurrentemente
- `/ai-framework:git-github:pullrequest` ejecuta security review en paralelo

---

## Estadísticas del Ecosistema

| Categoría      | Comandos | Notas                                |
| -------------- | -------- | ------------------------------------ |
| **PRP-cycle**  | 2        | Business layer                       |
| **SDD-cycle**  | 9        | Engineering layer (orden específico) |
| **git-github** | 5        | Delivery layer                       |
| **utils**      | 8        | Utilidades transversales             |
| **TOTAL**      | 24       | Comandos disponibles                 |

---

::: info Última Actualización
**Fecha**: 2025-10-16 | **Comandos Documentados**: 24 | **Categorías**: 4 | **Workflow**: 6 pasos core SDD
:::
