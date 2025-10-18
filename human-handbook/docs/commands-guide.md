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

**Output:** `.specify/prps/{feature_name}/prp.md`

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
2. Validate required files exist (`.specify/prps/{feature_name}/prp.md`)
3. Milestone handling:
   - **If milestone number provided**: Use existing milestone
   - **If no milestone**: Continue sin milestone assignment
4. Create GitHub issue:
   - Title: Extract desde PRP frontmatter `name` field
   - Body: Clean PRP content sin frontmatter
   - Labels: `prp`, `parent-issue`, `sdd`
   - Assign to milestone si milestone number was provided
5. Update PRP file frontmatter con `github`, `github_synced`, `milestone` (si aplica)
6. Create GitHub mapping file (`.specify/prps/{feature_name}/github-mapping.md`)

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

Crea especificación técnica desde lenguaje natural, GitHub Issue, o PRP local.

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.specify "Create authentication system"
/ai-framework:SDD-cycle:speckit.specify --from-issue {issue_number}
/ai-framework:SDD-cycle:speckit.specify --from-prp {feature_name}

# Ejemplos
/ai-framework:SDD-cycle:speckit.specify "Implement OAuth 2.0 with Google and GitHub providers"
/ai-framework:SDD-cycle:speckit.specify --from-issue 247
/ai-framework:SDD-cycle:speckit.specify --from-prp user-authentication
```

**Output:**

- Crea branch: `001-feature-name` (incrementa número automáticamente)
- Crea spec: `specs/001-feature-name/spec.md`
- Hace checkout de la branch en MISMO directorio (NO crea worktree)
- Valida con checklist interno

**Comportamiento:**

- ⚠️ NO crea worktree (usa `/ai-framework:git-github:worktree:create` si lo necesitas)
- ⚠️ NO abre IDE
- ✅ Cambia a nueva branch con `git checkout -b`
- ✅ Workspace actual cambia a la nueva branch

**Quick Guidelines:**

- Focus en **WHAT** users need y **WHY**
- Avoid HOW to implement (no tech stack, APIs, code structure)
- Written para business stakeholders, not developers
- DO NOT create any checklists embedded en el spec (separate command)

**Success Criteria Guidelines (MUST be):**

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention de frameworks, languages, databases, tools
3. **User-focused**: Describe outcomes desde user/business perspective
4. **Verifiable**: Can be tested/validated sin knowing implementation details

**Clarification Handling:**

- **Make informed guesses**: Use context, industry standards, common patterns
- **Document assumptions**: Record reasonable defaults en Assumptions section
- **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers
- **Prioritize clarifications**: scope > security/privacy > user experience > technical details

::: tip Cuándo usar
Primera fase SDD - convierte requisitos en spec técnica.
:::

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.clarify` (recomendado - previene refactors)

---

### `/ai-framework:SDD-cycle:speckit.clarify`

Detecta ambigüedades en spec, hace hasta 5 preguntas targeted, actualiza spec con clarifications.

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.clarify
```

**Output:** spec.md actualizada con sección `## Clarifications`

**Execution Steps:**

1. Run prerequisite check script para get FEATURE_DIR y FEATURE_SPEC paths
2. Load current spec file y perform structured ambiguity & coverage scan
3. Generate prioritized queue de candidate clarification questions (maximum 5)
4. **Sequential questioning loop** (interactive):
   - Present EXACTLY ONE question at a time
   - For multiple-choice: Provide **recommended option** con reasoning + table con todas las options
   - For short-answer: Provide **suggested answer** basado en best practices
   - User can accept recommendation diciendo "yes" o "recommended"
   - Record answer y move to next question
   - Stop cuando: critical ambiguities resolved, user signals completion, o reach 5 questions
5. **Integration after EACH accepted answer** (incremental update):
   - Create `## Clarifications` section si no existe
   - Append bullet: `- Q: {question} → A: {final answer}`
   - Apply clarification a most appropriate section
   - Save spec file AFTER cada integration (atomic overwrite)
6. Validation after each write + final pass
7. Write updated spec back to FEATURE_SPEC

**Ambiguity Taxonomy Categories:**

- Functional Scope & Behavior
- Domain & Data Model
- Interaction & UX Flow
- Non-Functional Quality Attributes
- Integration & External Dependencies
- Edge Cases & Failure Handling
- Constraints & Tradeoffs
- Terminology & Consistency
- Completion Signals
- Misc / Placeholders

::: tip Paso Recomendado
Vale la pena los 2 minutos: `/ai-framework:SDD-cycle:speckit.clarify` detecta ambigüedades antes de implementar. ROI 100:1.
:::

::: tip Cuándo usar
Después de `/ai-framework:SDD-cycle:speckit.specify`, antes de `/ai-framework:SDD-cycle:speckit.plan`. Previene hours de refactor.
:::

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.plan`

---

### `/ai-framework:SDD-cycle:speckit.plan`

Genera artifacts de diseño: research.md, data-model.md, contracts/, quickstart.md. Actualiza contexto del agente.

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.plan
```

**Phases:**

**Phase 0: Outline & Research**

1. Extract unknowns desde Technical Context
2. Generate y dispatch research agents para cada unknown
3. Consolidate findings en `research.md`:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md con all NEEDS CLARIFICATION resolved

**Phase 1: Design & Contracts** (Prerequisites: research.md complete)

1. Extract entities desde feature spec → `data-model.md`
   - Entity name, fields, relationships
   - Validation rules desde requirements
   - State transitions si applicable
2. Generate API contracts desde functional requirements
   - Para cada user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema a `/contracts/`
3. Agent context update:
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
   - Detect which AI agent is in use
   - Update appropriate agent-specific context file
   - Add only new technology desde current plan
   - Preserve manual additions between markers

**Output:**

- `research.md` - Decisiones técnicas
- `data-model.md` - Entidades y relaciones
- `contracts/` - API/GraphQL schemas
- `quickstart.md` - Escenarios de integración
- Agent context actualizado

**Key Rules:**

- Use absolute paths
- ERROR on gate failures o unresolved clarifications

::: tip Cuándo usar
Después de spec clarificada, antes de generar tasks.
:::

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.tasks`

---

### `/ai-framework:SDD-cycle:speckit.tasks`

Genera tasks.md ejecutable con dependency ordering, organizado por user stories, marca tasks paralelizables [P].

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.tasks
```

**Task Generation Rules:**

::: tip Organización Recomendada
Tasks organized por user story permiten independent implementation y testing. Mejor separation of concerns.
:::

**Tests son OPTIONAL**: Solo generate test tasks si explicitly requested en feature specification o si user requests TDD approach.

**Checklist Format (REQUIRED):**

Cada task MUST strictly seguir este formato:

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**Format Components:**

1. **Checkbox**: ALWAYS start con `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential number (T001, T002, T003...) en execution order
3. **[P] marker**: Include ONLY si task es parallelizable (different files, no dependencies)
4. **[Story] label**: REQUIRED para user story phase tasks only
   - Format: [US1], [US2], [US3] (maps a user stories desde spec.md)
   - Setup phase: NO story label
   - Foundational phase: NO story label
   - User Story phases: MUST have story label
   - Polish phase: NO story label
5. **Description**: Clear action con exact file path

**Examples:**

- ✅ CORRECT: `- [ ] T001 Create project structure per implementation plan`
- ✅ CORRECT: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ CORRECT: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ CORRECT: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ WRONG: `- [ ] Create User model` (missing ID y Story label)
- ❌ WRONG: `T001 [US1] Create model` (missing checkbox)

**Task Organization:**

**From User Stories (spec.md)** - PRIMARY ORGANIZATION:

- Cada user story (P1, P2, P3...) gets its own phase
- Map all related components a their story:
  - Models needed para that story
  - Services needed para that story
  - Endpoints/UI needed para that story
  - Si tests requested: Tests specific a that story
- Mark story dependencies (most stories should be independent)

**Phase Structure:**

- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (blocking prerequisites - MUST complete before user stories)
- **Phase 3+**: User Stories en priority order (P1, P2, P3...)
  - Within each story: Tests (si requested) → Models → Services → Endpoints → Integration
  - Each phase should be complete, independently testable increment
- **Final Phase**: Polish & Cross-Cutting Concerns

**Output:** `tasks.md` con:

- Setup phase
- Foundational tasks (blocking prerequisites)
- User story phases (P1, P2, P3...) con tasks independientes
- Polish & cross-cutting concerns (concerns transversales)
- Parallel markers [P] donde aplique
- Tests solo si especificado en spec

**Report:**

- Total task count
- Task count per user story
- Parallel opportunities identified
- Independent test criteria para cada story
- Suggested MVP scope (typically just User Story 1)
- Format validation: ALL tasks follow checklist format

::: tip Cuándo usar
Después de plan, antes de analyze.
:::

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.analyze` (opcional, recomendado)

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

Ejecuta tasks.md con agents asignados, parallelization, specialized agents, TDD enforcement.

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.implement
```

**Workflow:**

1. **Check checklists status** (si `FEATURE_DIR/checklists/` exists):
   - Scan all checklist files
   - Count: Total items, Completed items, Incomplete items
   - Create status table
   - **If any checklist incomplete**: STOP y ask "Do you want to proceed anyway? (yes/no)"
   - **If all checklists complete**: Display table y proceed automáticamente

2. **Load and analyze implementation context:**
   - **REQUIRED**: Read tasks.md (complete task list + execution plan)
   - **REQUIRED**: Read plan.md (tech stack, architecture, file structure)
   - **IF EXISTS**: Read data-model.md (entities + relationships)
   - **IF EXISTS**: Read contracts/ (API specs + test requirements)
   - **IF EXISTS**: Read research.md (technical decisions + constraints)
   - **IF EXISTS**: Read quickstart.md (integration scenarios)

3. **Project Setup Verification**:
   - **REQUIRED**: Create/verify ignore files basado en actual project setup:
     - Git repository detected → create/verify `.gitignore`
     - Dockerfile\* exists → create/verify `.dockerignore`
     - ESLint config exists → create/verify `.eslintignore`
     - Prettier config exists → create/verify `.prettierignore`
     - package.json exists → create/verify `.npmignore` (if publishing)
     - Terraform files (\*.tf) exist → create/verify `.terraformignore`
     - Helm charts present → create/verify `.helmignore`
   - **If ignore file already exists**: Verify y append missing critical patterns only
   - **If ignore file missing**: Create con full pattern set para detected technology

4. **Parse tasks.md structure** y extract:
   - Task phases: Setup, Tests, Core, Integration, Polish
   - Task dependencies: Sequential vs parallel execution rules
   - Task details: ID, description, file paths, parallel markers [P]
   - Execution flow: Order y dependency requirements

5. **Execute implementation** following task plan:
   - **Phase-by-phase execution**: Complete each phase antes de moving to next
   - **Respect dependencies**: Run sequential tasks en order, parallel tasks [P] can run together
   - **Follow TDD approach**: Execute test tasks antes de their corresponding implementation tasks
   - **File-based coordination**: Tasks affecting same files must run sequentially
   - **Validation checkpoints**: Verify each phase completion antes de proceeding

6. **Implementation execution rules:**
   - **Setup first**: Initialize project structure, dependencies, configuration
   - **Tests before code**: Si need to write tests para contracts, entities, integration scenarios
   - **Core development**: Implement models, services, CLI commands, endpoints
   - **Integration work**: Database connections, middleware, logging, external services
   - **Polish and validation**: Unit tests, performance optimization, documentation

7. **Progress tracking** y error handling:
   - Report progress after each completed task
   - Halt execution si any non-parallel task fails
   - For parallel tasks [P], continue con successful tasks, report failed ones
   - Provide clear error messages con context para debugging
   - **IMPORTANT**: Para completed tasks, mark as [X] en tasks file

8. **Completion validation:**
   - Verify all required tasks completed
   - Check que implemented features match original specification
   - Validate que tests pass y coverage meets requirements
   - Confirm implementation follows technical plan
   - Report final status con summary de completed work

::: tip Cuándo usar
Motor central de implementación, después de analyze/checklist (paso 6 del flujo SDD-cycle).
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

**Next Steps:** `➜ /ai-framework:git-github:commit` → `/ai-framework:git-github:pr`

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

Commits semánticos con grouping automático por categoría.

**Usage:**

```bash
/ai-framework:git-github:commit "descripción"
/ai-framework:git-github:commit "all changes"

# Ejemplos
/ai-framework:git-github:commit "feat: add OAuth authentication"
/ai-framework:git-github:commit "all changes"
```

**Execution Steps:**

1. **Parse Arguments and Validate Repository**:
   - Parse commit message desde **$ARGUMENTS**
   - Execute `git rev-parse --git-dir` para verify git repository
   - If fails: Show error y stop

2. **Analyze Repository Status and Changes**:
   - Check repository status usando `git status --porcelain`
   - If no changes: Show "No changes to commit" y stop
   - Analyze change details:
     - `git diff --cached --name-only` (staged files)
     - `git diff --name-only` (unstaged modified files)
     - `git ls-files --others --exclude-standard` (untracked new files)
   - Display summary de files a be processed

3. **Handle Staging Strategy**:
   - Check si anything is staged con `git diff --cached --quiet`
   - If nothing staged y unstaged changes exist:
     - Stage all changes con `git add -A` (modified, new, deleted)
   - If files already staged: Use existing staged files
   - Display staging status

4. **Classify Changed Files by Category** usando natural language processing:
   - **config**: `.claude/*`, `*.md`, `CLAUDE.md`, configuration files
   - **docs**: `docs/*`, `README*`, `CHANGELOG*`, documentation
   - **security**: `scripts/*`, `*setup*`, `*security*`, security-related
   - **test**: `*test*`, `*spec*`, `*.test.*`, testing files
   - **main**: All other files (core functionality)

5. **Determine Commit Strategy** (Single vs Multiple):
   - Count files en cada category
   - **Multiple commits** if: 2+ categories con 2+ files each OR any security files exist
   - **Single commit** if: Only one significant category OR limited file changes

6. **Execute Smart Commit Strategy**:
   - **If multiple commits**: Para cada category (order: security, config, docs, test, main):
     - Reset y stage category files only
     - Generate appropriate commit message:
       - **config**: "feat(config): update configuration and commands"
       - **docs**: "docs: enhance documentation and setup guides"
       - **security**: "security: improve security measures and validation"
       - **test**: "test: update test suite and coverage"
       - **main**: "feat: implement core functionality changes"
     - Create commit
   - **If single commit**: Use custom message o generate conventional commit message

7. **Report Results**: Display recent commit history y summary

**Output:** Commits agrupados por tipo (feat, fix, docs, test, refactor, etc.)

::: tip Cuándo usar
Después de completar cambios.
:::

**Next Steps:** `➜ /ai-framework:git-github:pr`

---

### `/ai-framework:git-github:pr`

Crea PR con security review BLOCKING, push seguro y metadata completa.

**Usage:**

```bash
/ai-framework:git-github:pr {target_branch}

# Ejemplos
/ai-framework:git-github:pr develop
/ai-framework:git-github:pr main
```

**Execution Steps:**

1. **Validación del target branch**:
   - Validate argument format
   - Execute `git fetch origin`
   - Capture current branch
   - Verify target branch exists
   - Validate current ≠ target (exception: protected branches → auto-create feature branch)
   - Verify divergence con target

2. **Validación de sincronización de rama actual**:
   - Check si current branch has upstream
   - **If has upstream**: Verify not behind remote (blocks si behind)
   - **If NO upstream**: Continue silently (new branch)

3. **Operaciones en paralelo**:

   **Security Review (BLOCKING):**
   - Start `/agent:security-reviewer` para analyze changes
   - Timeout: 80 segundos máximo
   - **Blocking conditions**:
     - HIGH severity findings (confidence ≥ 8.0): ALWAYS block PR creation
     - MEDIUM severity findings (confidence ≥ 8.0): Block en production (configurable)
   - **Success**: Sin vulnerabilidades críticas → continue
   - **Failure**: Show findings + block PR creation + exit error
   - **Timeout**: Show warning + create PR con SECURITY_REVIEW_TIMEOUT flag
   - **System error**: Block PR creation + show retry instructions

   **Validar PR existente:**
   - Execute `gh pr view --json number,state,title,url`
   - Store result para next step

   **Análisis de commits:**
   - Git data combined (mode-aware):
     - If AUTO_CREATE_BRANCH mode: Analyze commits NOT en origin/target
     - If NORMAL mode: Diff against target
   - Variables preparadas: commit_count, git_data, files_data, files_changed

4. **Procesar PR existente**:
   - Si exists PR abierto: Ask "[1] Actualizar PR / [2] Crear nuevo PR"
   - Si no exists: Continue con creation

5. **Detectar tipo de rama y decidir acción**:

   **SI rama protegida** (main, master, develop, staging, production, etc.):
   - Create feature branch automática
   - Extract primary type desde conventional commits
   - Detect central theme desde commit scopes o frequent words
   - Generate timestamp UTC
   - Build branch name: `${tema_central}-${timestamp}` o `${primary_type}-improvements-${timestamp}`
   - Create nueva rama con validation y rollback on failure
   - Push to remote con `--set-upstream`

   **SI NO rama protegida** (feature branch):
   - Use current branch para PR
   - Push to remote (con `--set-upstream` si needed)

6. **Preparar contenido del PR**:
   - Generate título: `{type}({scope}): {description}` basado en commits
   - Count lines: additions + deletions
   - Identify affected areas (project directories)
   - Detect breaking changes (keywords: BREAKING/deprecated/removed)
   - **IMPORTANTE**: Al numerar items usa formato SIN símbolo hash: 'Bug 1:', 'Issue 1:', 'Task 1:' (NO 'Bug #1:') para evitar auto-linking no intencional de GitHub
   - Build PR body con sections: Summary, Changes Made, Files & Impact, Test Plan, Breaking Changes

7. **Crear PR**: Execute `gh pr create --title --body --base`

8. **Mostrar resultado**: PR URL + confirmation

**Logging:** JSONL format en `.claude/logs/{date}/`:

- Security review: `security.jsonl`
- PR operations: `pr_operations.jsonl`

::: tip Cuándo usar
Para PRs con estándares de calidad.
:::

**Next Steps:** Después de merge → `/ai-framework:git-github:cleanup`

---

### `/ai-framework:git-github:cleanup`

Post-merge cleanup workflow: delete feature branch y sync con base branch.

**Usage:**

```bash
/cleanup           # Auto-detect base branch (main/master/develop)
/cleanup main      # Specify base branch explicitly
/cleanup develop   # Cleanup and sync with develop
```

**Execution Steps:**

1. **Validate Current State**:
   - Get current branch name
   - Detect protected branches pattern
   - If current branch es protected: Error "Ya estás en rama base" y terminate
   - If not protected: Continue con cleanup

2. **Determine Target Base Branch**:
   - **If argument provided**: Use **$ARGUMENTS** as target base
   - **If no argument (auto-detect)**: Try detection en order (main → master → develop)
   - Validate target exists en origin

3. **Switch to Base Branch**:
   - Execute `git checkout $target_base`
   - Verify success
   - If fails: Show error y terminate

4. **Delete Feature Branch**:
   - Execute `git branch -D "$current_branch"` (force delete)
   - Use `-D` porque user explicitly requested cleanup
   - Show confirmation

5. **Sync with Remote**:
   - Execute `git pull origin $target_base --ff-only`
   - Use `--ff-only` para prevent accidental merges
   - If fails (diverged): Show rebase instructions y terminate
   - If success: Show commits pulled

6. **Cleanup Remote Branch (Optional)**:
   - Check si feature branch exists en remote
   - If exists: Ask "¿Eliminar rama remota? [y/N]"
   - If yes: Execute `git push origin --delete "$current_branch"`
   - If no: Skip

7. **Final Status**:
   - Show summary: operations, current branch, deleted branch, commits synced
   - Verify clean state con `git status --short`

**Output:** Workspace limpio + documentación actualizada

::: tip Cuándo usar
Después de merge exitoso.
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

| Workflow          | Comandos Core (ORDEN CORRECTO)                                                                                                            |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Feature nueva** | `specify` → `clarify` → `plan` → `tasks` → `[analyze]` → `[checklist]` → `implement` → `[sync]`                                           |
| **Con PRP**       | `prp-new` → `prp-sync` → `specify --from-issue` → `clarify` → `plan` → `tasks` → `[analyze]` → `[checklist]` → `implement` → `[sync]`     |
| **Bug fix**       | `worktree:create` → `understand` → `specify` → `clarify` → `plan` → `tasks` → `[analyze]` → `[checklist]` → `implement` → `commit` → `pr` |
| **Post-merge**    | `changelog` → `worktree:cleanup` → `docs` (o usar `/ai-framework:git-github:cleanup`)                                                     |

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
- Dejar `/ai-framework:git-github:pr` ejecutar security review
  :::

::: info OPCIONAL

- `analyze` - Valida consistencia entre artefactos (después de tasks, antes de implement)
- `checklist` - Quality gate para requirements (antes de implement, genera "unit tests for requirements")
- `sync` - Documenta en GitHub lo que fue construido (después de implement)
  :::

### Comandos Pre-Production

1. `/ai-framework:SDD-cycle:speckit.implement` - TDD enforcement automático
2. `/ai-framework:git-github:pr` - Security review blocking
3. `/ai-framework:utils:changelog` - Keep a Changelog compliance

### Parallel Execution

- `/ai-framework:SDD-cycle:speckit.implement` ejecuta agents en paralelo automáticamente
- Tasks marcadas `[P]` se ejecutan concurrentemente
- `/ai-framework:git-github:pr` ejecuta security review en paralelo

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
