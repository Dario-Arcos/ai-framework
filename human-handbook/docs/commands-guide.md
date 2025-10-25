# Guía de Comandos Claude Code

::: tip ¿Qué son los Comandos?
Slash commands que ejecutan workflows completos del ciclo AI-first development. Diseñados para usarse en secuencia específica (ver workflows).
:::

---

| Categoría                                                     | Comandos | Flujo Típico                           |
| ------------------------------------------------------------- | -------- | -------------------------------------- |
| [Ciclo PRP (Business Layer)](#ciclo-prp-business-layer)       | 2        | Product Requirements → GitHub Tracking |
| [Ciclo SDD (Engineering Layer)](#ciclo-sdd-engineering-layer) | 9        | Spec → Plan → Tasks → Implement        |
| [Git & GitHub](#git-github)                                   | 5        | Commit → PR → Cleanup                  |
| [Utilidades](#utilidades)                                     | 9        | Understand → Research → Polish → Docs  |

::: tip Orden Recomendado
Los comandos del **Ciclo SDD** funcionan mejor en orden específico. Cada paso prepara el siguiente. Ver [Workflows Completos](#workflows-completos).
:::

---

## Ciclo PRP (Business Layer)

### `/ai-framework:PRP-cycle:prp-new`

::: tip Propósito
Brainstorming interactivo para crear Product Requirements Prompt (PRP) estructurado, minimalista (50-100 líneas), business-focused.
:::

**Usage:**

```bash
/ai-framework:PRP-cycle:prp-new {feature_name}
```

**Estructura PRP (Minimalista):**

1. **Problem Statement** (5-10 líneas) - Formato estructurado AI-parseable
2. **User Impact** (10-20 líneas) - Primary users, journey, pain points
3. **Success Criteria** (5-10 líneas) - Quantitative + Qualitative con checkboxes
4. **Constraints** (5-10 líneas) - Budget, timeline, team, compliance
5. **Out of Scope** (5-10 líneas) - Qué NO estamos building en V1

**Output:** `prps/{feature_name}/prp.md`

::: details Discovery Questions

- **Problem**: ¿Qué problema específico? ¿Por qué ahora?
- **Users**: ¿Quién experimenta este problema? ¿Personas primarias?
- **Impact**: ¿Qué pasa si NO resolvemos esto?
- **Success**: ¿Cómo medimos si esto funciona?
- **Constraints**: ¿Budget, timeline, compliance requirements?
- **Scope**: ¿Qué NO estamos building en V1?
  :::

**Next Steps:** `➜ /ai-framework:PRP-cycle:prp-sync {feature_name}`

---

### `/ai-framework:PRP-cycle:prp-sync`

::: tip Propósito
Sincroniza PRP a GitHub como Parent Issue con opción de milestone assignment.
:::

**Usage:**

```bash
/ai-framework:PRP-cycle:prp-sync {feature_name}
/ai-framework:PRP-cycle:prp-sync {feature_name} --milestone {number}
```

**Workflow:** Parse args → Validate PRP → Create GitHub issue (parent) → Update frontmatter con `github_synced`

**Output:** GitHub Issue (parent) + actualiza frontmatter + mapping file

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.specify --from-issue {issue_number}`

---

## Ciclo SDD (Engineering Layer)

::: tip Secuencia Recomendada
Comandos funcionan mejor en orden específico. Cada paso prepara el siguiente.
:::

### `/ai-framework:SDD-cycle:speckit.specify`

::: tip Propósito
Crea especificación técnica desde descripción natural, GitHub Issue, o PRP.
:::

**Casos de Uso:**

```bash
# Desde descripción natural
/ai-framework:SDD-cycle:speckit.specify "Implement OAuth 2.0 with Google and GitHub"

# Desde GitHub Issue
/ai-framework:SDD-cycle:speckit.specify --from-issue 247

# Desde PRP local
/ai-framework:SDD-cycle:speckit.specify --from-prp user-authentication
```

**Proceso:** Crea branch `001-feature-name` (número incremental) → Genera spec.md (WHAT/WHY, no HOW) → Validación automática

::: warning Importante
El comando hace checkout de la branch. Tu workspace cambia automáticamente.
:::

**Output:** Branch nueva + spec.md + checklist de validación

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.clarify` (recomendado)

---

### `/ai-framework:SDD-cycle:speckit.clarify`

::: tip Propósito
Detecta ambigüedades en spec y pregunta interactivamente hasta 5 clarificaciones prioritarias.
:::

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.clarify
```

**Proceso:** Escaneo ambigüedades → Preguntas interactivas (una a la vez, con recomendaciones) → Actualización incremental del spec

**Categorías que Detecta:**

- Scope & Behavior incompleto
- Data model indefinido
- UX flows ambiguos
- Edge cases sin definir
- Dependencias externas sin especificar

::: tip ROI 100:1
2 minutos de clarificaciones previenen 4 horas de refactor. SIEMPRE ejecutar antes de `/plan`.
:::

**Output:** spec.md actualizada + sección Clarifications

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.plan`

---

### `/ai-framework:SDD-cycle:speckit.plan`

::: tip Propósito
Genera artifacts de diseño técnico y decisiones de implementación.
:::

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.plan
```

**Genera:**

1. **research.md** - Stack seleccionado + rationale + alternativas
2. **data-model.md** - Entities + fields + validations + relationships
3. **contracts/** - API/GraphQL schemas (un endpoint por user action)
4. **quickstart.md** - Ejemplos de uso + flujos de integración
5. **Agent Context** - Actualiza `.claude/` con nuevas tecnologías

::: warning Prerequisito
Todas las clarificaciones resueltas. Falla si encuentra `[NEEDS CLARIFICATION]`.
:::

**Output:** 5 artifacts + agent context actualizado

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.tasks`

---

### `/ai-framework:SDD-cycle:speckit.tasks`

::: tip Propósito
Genera tasks.md ejecutable, organizado por user stories, con paralelización marcada [P].
:::

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.tasks
```

**Formato Obligatorio:**

```text
- [ ] T001 [P?] [US1?] Description con file path
      ↑    ↑    ↑      ↑
      │    │    │      └─ Descripción + ruta exacta
      │    │    └─ User Story label (solo en fases US)
      │    └─ [P] = Paralelizable (archivos diferentes)
      └─ Checkbox markdown
```

**Organización:** Setup → Foundational → User Stories (P1, P2, P3...) → Polish

::: tip Tests Opcionales
Solo se generan tasks de tests si están explícitamente solicitadas en spec o se pide enfoque TDD.
:::

**Output:** `tasks.md` + report con oportunidades de paralelización

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.analyze` (opcional)

---

### `/ai-framework:SDD-cycle:speckit.analyze`

::: tip Propósito
Análisis de consistencia entre artefactos. Valida spec.md + plan.md + tasks.md.
:::

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.analyze
```

::: warning STRICTLY READ-ONLY
Do NOT modify any files. Output structured analysis report.
:::

**Proceso:** Load artifacts → Build semantic models → 6 detection passes (duplication, ambiguity, underspecification, constitution alignment, coverage gaps, inconsistency)

**Severity Assignment:**

- **CRITICAL**: Violates constitution MUST, missing core spec, requirement con zero coverage
- **HIGH**: Duplicate/conflicting requirement, ambiguous security/performance
- **MEDIUM**: Terminology drift, missing non-functional task coverage
- **LOW**: Style/wording improvements, minor redundancy

**Output:** Markdown report con findings table + coverage summary + metrics

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.checklist` (opcional) o `➜ /ai-framework:SDD-cycle:speckit.implement`

---

### `/ai-framework:SDD-cycle:speckit.implement`

::: tip Propósito
Ejecuta tasks.md fase por fase con paralelización automática y TDD enforcement.
:::

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.implement
```

**Proceso:** Validación checklists → Carga contexto → Setup automático → Ejecución fase por fase (Setup → Foundational → User Stories → Polish) → Validación final

**Ejecución:**

- Tasks secuenciales: orden
- Tasks `[P]`: paralelo
- TDD: tests antes de implementación (si solicitado)
- Marca `[X]` al completar cada task

::: warning Prerequisito
Checklists incompletos bloquean ejecución (puedes override manualmente).
:::

**Output:** Implementación completa + tasks.md actualizada con `[X]`

**Next Steps:** `➜ /ai-framework:SDD-cycle:speckit.sync` (opcional)

---

### `/ai-framework:SDD-cycle:speckit.checklist`

::: tip Propósito
Genera checklist customizada para validar quality de requirements ("Unit Tests for Requirements").
:::

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.checklist "{domain} requirements quality"
```

::: danger CRITICAL CONCEPT
Checklists son **UNIT TESTS FOR REQUIREMENTS WRITING** - validan quality, clarity, y completeness de requirements en given domain.

**NO son verification tests** (esos son tests de código).
**SON quality gates** para tus especificaciones.
:::

**Propósito Real:**

Si tu spec.md es código escrito en inglés, el checklist es su unit test suite. Validando que tus REQUIREMENTS estén bien escritos, NO que tu implementación funcione.

::: details Workflow Integration

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

:::

**Category Structure:**

- Requirement Completeness
- Requirement Clarity
- Requirement Consistency
- Acceptance Criteria Quality
- Scenario Coverage
- Edge Case Coverage
- Non-Functional Requirements

**Output:** `checklists/{domain}.md` para validación manual antes de implementar

::: warning Importante
Después de generar checklist, DEBES marcar checkboxes manualmente revisando tu spec/plan. implement bloqueará si checklists están incomplete.
:::

**Next Steps:** Marcar checkboxes → `➜ /ai-framework:SDD-cycle:speckit.implement`

---

### `/ai-framework:SDD-cycle:speckit.sync`

::: tip Propósito
Sincroniza spec.md + plan.md + tasks.md a GitHub como child issue vinculado a parent PRP.
:::

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.sync {parent_issue_number}
```

::: warning IMPORTANT
Requiere parent PRP issue. Si no tienes PRP issue, ejecuta `/ai-framework:PRP-cycle:prp-sync` primero.
:::

**Proceso:** Parse parent issue → Validate spec → Prepare issue content → Create GitHub issue + link to parent → Update frontmatter

**Timing Recommendation:**

Ejecutar DESPUÉS de implementación completa y validada. Esto ensures:

- GitHub Issue documenta lo construido (no especulación)
- Spec + Plan + Tasks 100% accurate con final code
- Stakeholders ven resultados, no work-in-progress
- Zero need para re-sync

**Output:** GitHub Issue (child) + frontmatter updated + mapping file

**Next Steps:** `➜ /ai-framework:git-github:commit` → `/ai-framework:git-github:pullrequest`

---

### `/ai-framework:SDD-cycle:speckit.constitution`

::: tip Propósito
Crea o actualiza constitución del proyecto con principios fundamentales.
:::

**Usage:**

```bash
/ai-framework:SDD-cycle:speckit.constitution
```

::: danger RESTRICCIÓN
NO EJECUTAR sin autorización directa del usuario.
:::

**Proceso:** Load existing constitution → Identify placeholders → Collect/derive values → Draft updated content → Consistency propagation → Generate Sync Impact Report → Validation → Write back

**Output:** `.specify/memory/constitution.md` actualizada con sync impact report

---

## Git & GitHub

### `/ai-framework:git-github:commit`

::: tip Propósito
Commits semánticos con agrupación automática y soporte corporativo.
:::

**Casos de Uso:**

```bash
# 1. Formato Convencional (proyectos open source)
/ai-framework:git-github:commit "feat(auth): add OAuth2 support"

# 2. Task ID solo (tipo automático desde archivos modificados)
/ai-framework:git-github:commit "TRV-345 implementar autenticación"

# 3. Tipo + Task ID (RECOMENDADO - control total)
/ai-framework:git-github:commit "refactor: TRV-345 mejorar módulo auth"

# 4. Auto-commit (cuando no tienes Task ID)
/ai-framework:git-github:commit "all changes"
```

::: tip Mejor Práctica
**Usa siempre `tipo: TASK-ID descripción`** cuando tengas Task ID. Control total y evita sorpresas.
:::

**Formato Corporativo:**

```
Tipo|TaskID|YYYYMMDD|Descripción
```

**Agrupación Inteligente:** Multiple commits si modificas 2+ categorías (config + código, docs + tests)

**Output:** Commits agrupados por tipo con mensajes semánticos

**Next Steps:** `➜ /ai-framework:git-github:pullrequest`

---

### `/ai-framework:git-github:pullrequest`

::: tip Propósito
Crea PR con security review automático, detección de formato corporativo y título personalizable.
:::

**Usage:**

```bash
# Desde feature branch → PR a main
/ai-framework:git-github:pullrequest main

# Desde rama protegida → Crea temp branch automática
/ai-framework:git-github:pullrequest main
```

**Proceso:**

1. **Security Review Automático** (BLOCKING) - Analiza vulnerabilidades, bloquea si HIGH severity
2. **Título del PR** - Si detecta commits corporativos, pregunta: primer commit o custom
3. **Branch Protection** - Si estás en main/master/develop, crea temp branch
4. **PR Body Automático** - Summary + Changes + Files + Test Plan + Breaking Changes

::: warning Security Review es BLOCKING
Si encuentra vulnerabilidades HIGH, comando FALLA y NO crea PR. Debes corregir primero.
:::

**Output:** PR URL + security review report

**Next Steps:** Después de merge → `/ai-framework:git-github:cleanup`

---

### `/ai-framework:git-github:cleanup`

::: tip Propósito
Limpia feature branch y sincroniza con base branch después de merge.
:::

**Usage:**

```bash
/ai-framework:git-github:cleanup
/ai-framework:git-github:cleanup main
```

**Proceso:** Valida estado → Detecta base branch → Workflow de limpieza (checkout base → delete feature branch → pull origin)

::: info Branch Remota
GitHub elimina automáticamente branch remota al mergear PR.
:::

**Output:** Workspace limpio en base branch + summary de operaciones

---

## Gestión de Worktrees

::: tip Worktree vs Branch
**Usa Branch:** Desarrollo lineal (1 feature), setup simple
**Usa Worktree:** Múltiples features paralelo, bug fix urgente sin interrumpir, experimentación POC
:::

### `/ai-framework:git-github:worktree:create`

::: tip Propósito
Crea worktree aislado en directorio sibling con rama nueva y upstream configurado.
:::

**Usage:**

```bash
/ai-framework:git-github:worktree:create "{objetivo}" {parent-branch}
```

**Proceso:** Argument validation → Working directory validation → Parent branch validation → Generate consistent names → Check collisions → Prepare parent → Create worktree → Open IDE automatically → Logging

::: warning Post-creación (IMPORTANTE)

```
⚠️ IDE abierto automáticamente, pero debes:

PASO 1 - En nueva ventana IDE: Abrir Terminal integrado
PASO 2 - Verificar directorio: pwd (debe mostrar ../worktree-XXX/)
PASO 3 - Iniciar nueva sesión: claude /workflow:session-start

❌ SI NO HACES ESTO: Claude seguirá trabajando en directorio anterior
✅ SOLO así tendrás sesiones Claude Code paralelas funcionando
```

:::

**Output:** Worktree `../worktree-{objetivo}/` + branch + IDE abierto

---

### `/ai-framework:git-github:worktree:cleanup`

::: tip Propósito
Elimina worktrees con validación de ownership y cleanup triple (worktree/local/remote).
:::

**Usage:**

```bash
/ai-framework:git-github:worktree:cleanup              # Discovery mode
/ai-framework:git-github:worktree:cleanup {worktree1}  # Cleanup específico
```

**Restricciones:**

- Only removes worktrees/branches created por you
- Never touches protected branches (main, develop, qa, staging, master)
- Requires clean state (no uncommitted changes)

**Discovery Mode:** Lists available worktrees con suggested commands

**Cleanup Mode:** Per-target validations → User confirmation ("ELIMINAR") → Dual atomic cleanup → Logging → Update current branch

**Output:** Triple cleanup + regresa automáticamente a main

---

## Utilidades

### `/ai-framework:utils:understand`

::: tip Propósito
Análisis comprehensivo de arquitectura, patrones y dependencies.
:::

**Usage:**

```bash
/ai-framework:utils:understand
/ai-framework:utils:understand "specific area"
```

**Phases:**

1. **Project Discovery** - Glob structure → Read key files → Grep patterns → Read entry points
2. **Code Architecture Analysis** - Entry points → Core modules → Data layer → API layer → Frontend → Config → Testing
3. **Pattern Recognition** - Naming conventions → Code style → Error handling → Auth flow → State management
4. **Dependency Mapping** - Internal deps → External libs → Service integrations → API deps → DB relationships
5. **Integration Analysis** - API endpoints → DB queries → Event systems → Shared utilities → Cross-cutting concerns

::: details Output Format

```markdown
PROJECT OVERVIEW
├── Architecture: [Type]
├── Main Technologies: [List]
├── Key Patterns: [List]
└── Entry Point: [File]

COMPONENT MAP
├── Frontend → [Structure]
├── Backend → [Structure]
├── Database → [Schema approach]
└── Tests → [Test strategy]

INTEGRATION POINTS
├── API Endpoints: [List]
├── Data Flow: [Description]
├── Dependencies: [Internal/External]
└── Cross-cutting: [Logging, Auth, etc.]

KEY INSIGHTS

- [Important findings]
- [Unique patterns]
- [Potential issues]
```

:::

::: tip Cuándo usar
**MANDATORY:** New codebase, unknown architecture, major refactor (Size L)
**RECOMMENDED:** Cambios en múltiples módulos (Size M)
**OPTIONAL:** Single-file fixes (Size S)
:::

---

### `/ai-framework:utils:three-experts`

::: tip Propósito
Panel de 3 expertos (backend/frontend/security) genera plan consensuado.
:::

**Usage:**

```bash
/ai-framework:utils:three-experts {goal}
```

**Expert Panel (Fixed):**

1. **backend-architect** → API design, data modeling, services
2. **frontend-developer** → UI components, user flows, client-side
3. **security-reviewer** → Threat modeling, compliance, security validation

**Workflow:**

**Round 1: Proposals (Independent)** - Cada expert provides su perspectiva

**Round 2: Synthesis & Decision** - Cross-review → Identify integration points/conflicts → Build consensus → Define priorities → Create final plan

**Output:** PLAN.md con OBJETIVO & SCOPE + DECISIONES TÉCNICAS + ✅ TAREAS CRÍTICAS + CRITERIOS DE ÉXITO

---

### `/ai-framework:utils:docs`

::: tip Propósito
Analiza y actualiza documentación usando specialist agents.
:::

**Usage:**

```bash
/ai-framework:utils:docs                 # Analizar toda la docs
/ai-framework:utils:docs README API      # Focus específico
```

**Proceso:** Analyze docs → Identify gaps/outdated content → Delegate a documentation specialist → Update/create docs

**Output:** Documentación actualizada con análisis de calidad

---

### `/ai-framework:utils:polish`

::: tip Propósito
Polishing meticuloso de archivos AI-generated. Preserva 100% funcionalidad mientras mejora calidad.
:::

**Usage:**

```bash
/ai-framework:utils:polish {file_paths}
```

::: danger CRITICAL DISCLAIMER
**POLISHING ≠ SCOPE REDUCTION**

Este comando es para **REFINEMENT**, not **FUNCTIONAL REDUCTION**.
:::

**Mandate:** Si file serves critical user workflow, prioritize COMPLETE PRESERVATION over optimization.

::: details Universal Polishing Protocol (5 Phases)

**Phase 1:** Syntax & Structure Validation (docs, configs, data, code, scripts/templates)

**Phase 2:** Logical Coherence Audit (information flow, configuration logic, data integrity, functional logic, template logic)

**Phase 3:** Consistency & Standards Enforcement (naming, format, language, cross-file, professional standards)

**Phase 4:** Redundancy & Optimization Elimination (content duplication, unused elements, complexity reduction, performance, resource cleanup)

**Phase 5:** Communication & Content Quality (professional language, documentation clarity, content accuracy)

:::

**Zero-Tolerance Polish Standards:**

**Critical Issues (Must Fix):** Syntax Errors, Security Vulnerabilities, Broken References, Data Corruption, Functional Failures

**High Priority:** Inconsistent Formatting, Performance Problems, Clarity Issues, Standard Violations, Redundant Content

---

### `/ai-framework:utils:deep-research`

::: tip Propósito
Professional audit con metodología sistemática y validación de múltiples fuentes.
:::

**Usage:**

```bash
/ai-framework:utils:deep-research "{investigation topic}"
```

**Professional Audit Protocol:**

**Phase 1: Engagement Planning & Risk Assessment** - Scope definition → Risk matrix → Source strategy → Quality gates

**Phase 2: Evidence Gathering & Documentation** - Multi-source validation (minimum 3 independent sources) → Primary source priority → Industry intelligence → Real-time verification

**Phase 3: Analytical Procedures & Verification** - Substantive testing → Cross-validation → Gap analysis → Professional judgment

::: details Source Hierarchies

**Tier 1 (Primary):** Government/Regulatory (.gov, SEC), Academic (peer-reviewed), Official Data (World Bank, IMF), Legal/Regulatory

**Tier 2 (Industry):** Major Consulting (Deloitte, PwC, EY, KPMG), Strategy Consulting (McKinsey, BCG, Bain), Financial Intelligence (Bloomberg, Reuters), Research Firms (Gartner, Forrester)

**Tier 3 (Corroborative):** Quality Journalism (WSJ, The Economist), Industry Bodies, Corporate Intelligence, Expert Analysis

:::

**Anti-Hallucination Rules:**

1. Source Everything (every claim requires verifiable source con URL y date)
2. Multiple Sources (minimum 3 independent confirmations)
3. Document Conflicts
4. State Uncertainty (explicitly declare cuando evidence insufficient)
5. Show Methods
6. Attribute Sources

**Output:** Reporte de investigación con Executive Summary + Methodology + Detailed Findings + Risk Assessment

---

### `/ai-framework:utils:changelog`

::: tip Propósito
Actualiza CHANGELOG.md con PRs mergeados desde último release (Keep a Changelog format).
:::

**Usage:**

```bash
/ai-framework:utils:changelog
```

**Proceso:** Validación herramientas/archivos → Auto-detección PRs pendientes → Actualización CHANGELOG → Commit automático

**Output:** CHANGELOG.md actualizado + commit automático

**Next Steps:** `➜ /ai-framework:utils:release`

---

### `/ai-framework:utils:release`

::: tip Propósito
Workflow completo de release: bump versión → actualizar CHANGELOG → sync → commit/tag → push.
:::

**Usage:**

```bash
/ai-framework:utils:release
```

**Pre-requisitos:** CHANGELOG.md actualizado + sección `[No Publicado]` con cambios + package.json con `version`

**Proceso:** Validar herramientas/archivos → Preguntar tipo release (patch/minor/major) → Ejecutar `npm version` (auto-dispara sync) → Actualizar CHANGELOG con versión → Verificar commit/tag → Preguntar si push

::: warning Auto-sync
`npm version` ejecuta automáticamente `scripts/sync-versions.cjs` que sincroniza versiones en config.js, README.md, docs/changelog.md
:::

**Output:** Release completo (local o remoto según elección)

---

### `/ai-framework:utils:project-init`

::: tip Propósito
Initialize o update project context con deep analysis y recomendaciones de agentes.
:::

**Usage:**

```bash
/ai-framework:utils:project-init
/ai-framework:utils:project-init deep   # Force deep analysis
```

**Reuses:** `/ai-framework:utils:understand` phases 1-5 para systematic discovery

**Proceso:**

**Phase 1:** Detect Existing Context
**Phase 2:** Deep Discovery (reuse understand.md logic)
**Phase 3:** Tech Stack Detection (Extended) - Parse exact versions y all dependencies
**Phase 4:** Agent Mapping + Gap Analysis - Load agent registry → Map Tech → Agents → Gap detection
**Phase 5:** Generate project-context.md con Stack + Architecture + Patterns + Recommended Agents + Integration Points + ⚠️ Potential Issues
**Phase 6:** Update CLAUDE.md Reference (add si missing)

::: details Output

```
✅ Project context initialized (deep analysis)

Stack Detected:
   - [Language] [version]
   - [Framework] [version]

Recommended Agents ([total]):
   Core: [list]
   Project-Specific: [list based on tech]

Generated:
   - .specify/memory/project-context.md
   - CLAUDE.md (reference added if missing)

⚠️ Potential Issues Flagged: [list]

Next: Claude ahora conoce tu proyecto en profundidad.
```

:::

---

### `/ai-framework:utils:setup-dependencies`

::: tip Propósito
Instala dependencias esenciales faltantes con platform detection.
:::

**Usage:**

```bash
/ai-framework:utils:setup-dependencies
```

**Proceso:** Detect platform → Dependency registry → Discover missing deps → Display status → Confirm installation → Group by installer → Install by package manager → Verify installation → Report results

**Dependency Registry Format:**

```bash
"tool_name|installer|platforms|purpose"
```

**Supported:** installers (brew, pip, npm, apt), platforms (darwin, linux, all)

---

### `/ai-framework:utils:cleancode-format`

::: tip Propósito
Formateo on-demand de archivos usando formatters apropiados (prettier, black, shfmt).
:::

**Usage:**

```bash
/ai-framework:utils:cleancode-format                           # Git modified
/ai-framework:utils:cleancode-format src/auth.py src/utils.ts  # Específicos
/ai-framework:utils:cleancode-format src/                      # Directorio
```

**Formatters Soportados:**

| Extensión                    | Formatter | Comando                |
| ---------------------------- | --------- | ---------------------- |
| `.js`, `.jsx`, `.ts`, `.tsx` | prettier  | `npx prettier --write` |
| `.json`, `.md`, `.yml`       | prettier  | `npx prettier --write` |
| `.py`                        | black     | `black --quiet`        |
| `.sh`, `.bash`               | shfmt     | `shfmt -w`             |

**Comportamiento:**

- Sin argumentos: Detecta archivos modificados con `git diff --name-only`
- Con archivos: Formatea archivos específicos
- Con directorio: Escanea recursivamente archivos soportados
- Extensiones no soportadas: Ignoradas
- Formatters no instalados: Muestra instrucciones

::: tip Design Rationale
Control manual sobre cuándo formatear. Evita contaminar diffs en proyectos legacy con deuda técnica.
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

---

## Estadísticas del Ecosistema

| Categoría      | Comandos | Notas                                |
| -------------- | -------- | ------------------------------------ |
| **PRP-cycle**  | 2        | Business layer                       |
| **SDD-cycle**  | 9        | Engineering layer (orden específico) |
| **git-github** | 5        | Delivery layer                       |
| **utils**      | 9        | Utilidades transversales             |
| **TOTAL**      | 25       | Comandos disponibles                 |

---

::: info Última Actualización
**Fecha**: 2025-10-24 | **Comandos Documentados**: 25 | **Categorías**: 4 | **Workflow**: 6 pasos core SDD
:::
