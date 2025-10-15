# Guía de Comandos Claude Code

**24 comandos disponibles** organizados por flujo de desarrollo

---

## 🎯 Ciclo PRP (Business Layer)

### `/ai-framework:PRP-cycle:prp-new`

Brainstorming interactivo para crear Product Requirements Prompt (PRP) estructurado, minimalista (50-100 líneas), business-focused.

```bash
/ai-framework:PRP-cycle:prp-new <feature_name>

# Ejemplo
/ai-framework:PRP-cycle:prp-new user-authentication
```

**Output**: `.claude/prps/<feature_name>/prp.md`

**Cuándo usar**: Planificación de nueva feature desde cero con stakeholders de negocio.

---

### `/ai-framework:PRP-cycle:prp-sync`

Sincroniza PRP a GitHub como Parent Issue con opción de milestone assignment.

```bash
/ai-framework:PRP-cycle:prp-sync <feature_name>
/ai-framework:PRP-cycle:prp-sync <feature_name> --milestone <number>

# Ejemplos
/ai-framework:PRP-cycle:prp-sync user-authentication
/ai-framework:PRP-cycle:prp-sync user-authentication --milestone 5
```

**Output**: GitHub Issue (parent) + actualiza frontmatter con `github_synced`

**Cuándo usar**: Después de aprobar PRP, para tracking en GitHub.

---

## 🏗️ Ciclo SDD (Engineering Layer - SECUENCIAL OBLIGATORIO)

### `/ai-framework:SDD-cycle:speckit.specify`

Crea especificación técnica desde lenguaje natural, GitHub Issue, o PRP local.

```bash
/ai-framework:SDD-cycle:speckit.specify "Create authentication system"
/ai-framework:SDD-cycle:speckit.specify --from-issue <issue_number>
/ai-framework:SDD-cycle:speckit.specify --from-prp <feature_name>

# Ejemplos
/ai-framework:SDD-cycle:speckit.specify "Implement OAuth 2.0 with Google and GitHub providers"
/ai-framework:SDD-cycle:speckit.specify --from-issue 247
/ai-framework:SDD-cycle:speckit.specify --from-prp user-authentication
```

**Output**:

- Crea branch: `001-feature-name` (incrementa número automáticamente)
- Crea spec: `specs/001-feature-name/spec.md`
- Hace checkout de la branch en MISMO directorio (NO crea worktree)
- Valida con checklist interno

**Comportamiento**:

- ⚠️ NO crea worktree (usa `worktree:create` si lo necesitas)
- ⚠️ NO abre IDE
- ✅ Cambia a nueva branch con `git checkout -b`
- ✅ Workspace actual cambia a la nueva branch

**Cuándo usar**: Primera fase SDD - convierte requisitos en spec técnica.

---

### `/ai-framework:SDD-cycle:speckit.clarify`

Detecta ambigüedades en spec, hace hasta 5 preguntas targeted, actualiza spec con clarifications.

```bash
/ai-framework:SDD-cycle:speckit.clarify
```

**Output**: spec.md actualizada con sección `## Clarifications`

**Cuándo usar**: OBLIGATORIO después de `/ai-framework:SDD-cycle:speckit.specify`, antes de `/ai-framework:SDD-cycle:speckit.plan`.

---

### `/ai-framework:SDD-cycle:speckit.plan`

Genera artifacts de diseño: research.md, data-model.md, contracts/, quickstart.md. Actualiza contexto del agente.

```bash
/ai-framework:SDD-cycle:speckit.plan
```

**Output**:

- `research.md` - Decisiones técnicas
- `data-model.md` - Entidades y relaciones
- `contracts/` - API/GraphQL schemas
- `quickstart.md` - Escenarios de integración
- Agent context actualizado

**Cuándo usar**: Después de spec clarificada, antes de generar tasks.

---

### `/ai-framework:SDD-cycle:speckit.tasks`

Genera tasks.md ejecutable con dependency ordering, organizado por user stories, marca tasks paralelizables [P].

```bash
/ai-framework:SDD-cycle:speckit.tasks
```

**Output**: `tasks.md` con:

- Setup phase
- Foundational tasks (blocking prerequisites)
- User story phases (P1, P2, P3...) con tasks independientes
- Polish & cross-cutting phase
- Parallel markers [P] donde aplique
- Tests solo si especificado en spec

**Cuándo usar**: Después de plan, antes de agent assignment.

---

### Agent Assignment (via Task tool - PASO 5 CRÍTICO)

Analiza tasks.md y asigna sub-agents especializados para ejecución paralela óptima.

```bash
# Después de /ai-framework:SDD-cycle:speckit.tasks
/ai-framework:Task agent-assignment-analyzer "Analyze tasks.md and assign specialized agents for parallel execution"
```

**Output**:

- Análisis de task types (API, frontend, DB, tests, infra)
- Asignación de agents especializados (backend-architect, frontend-developer, database-optimizer, etc.)
- Detección de file dependencies (tasks con mismo archivo = secuenciales)
- Tabla de parallel execution streams con agents asignados
- Speedup estimation (potencial 3-10x)

**Por qué es crítico**:

- Aprovecha contexto individual de cada sub-agent especializado
- Minimiza conflictos de archivos mediante detección de dependencies
- Ejecución en paralelo real (múltiples agents trabajando simultáneamente)
- Optimiza tiempo de implementación dramáticamente

**Cuándo usar**:

- **CASI MANDATORIO** para features con 5+ tasks
- Features que tocan múltiples dominios (backend + frontend + DB)
- Cuando se busca optimizar tiempo de implementación
- Tasks con independencia funcional clara

**Ejemplo de output**:

```
Stream 1 (backend-architect):
  - Task 2.1: API endpoints [estimated: 45min]
  - Task 2.3: Authentication middleware [estimated: 30min]

Stream 2 (frontend-developer):
  - Task 3.1: Login component [estimated: 60min]
  - Task 3.2: Protected routes [estimated: 40min]

Stream 3 (database-optimizer):
  - Task 1.1: User schema migration [estimated: 20min]
  - Task 1.2: Indexes and constraints [estimated: 15min]

Total sequential time: 210min
Parallel time (3 streams): 75min
Speedup: 2.8x
```

**Cuándo usar**: DESPUÉS de tasks, ANTES de analyze (paso 5 del flujo SDD-cycle).

---

### `/ai-framework:SDD-cycle:speckit.analyze`

Análisis cross-artifact de consistency y quality. Valida spec.md + plan.md + tasks.md.

```bash
/ai-framework:SDD-cycle:speckit.analyze
```

**Output**: Reporte con:

- Findings por severidad (CRITICAL/HIGH/MEDIUM/LOW)
- Coverage summary
- Constitution alignment issues
- Unmapped tasks
- Métricas de calidad

**Cuándo usar**: Validación pre-implementación, después de generar tasks.

---

### `/ai-framework:SDD-cycle:speckit.implement`

Ejecuta tasks.md con agents asignados, parallelization, specialized agents, TDD enforcement.

```bash
/ai-framework:SDD-cycle:speckit.implement
```

**Workflow**:

1. Carga contexto (tasks, plan, contracts, data-model, research, quickstart, agent assignments)
2. Valida/crea ignore files por tecnología
3. Ejecuta tasks por fases usando agents asignados:
   - Setup → Tests → Core → Integration → Polish
   - Tasks paralelas se ejecutan concurrentemente con agents especializados
4. Marca tasks completadas [X]
5. Reporta progreso y validación final

**Cuándo usar**: Motor central de implementación, después de agent assignment y analyze (paso 7 del flujo SDD-cycle).

---

### `/ai-framework:SDD-cycle:speckit.checklist`

Genera checklist customizada para validar calidad de implementación ("Unit tests for English").

```bash
# DESPUÉS de /ai-framework:SDD-cycle:speckit.implement
/ai-framework:SDD-cycle:speckit.checklist "<domain> implementation quality review"

# Ejemplos
/ai-framework:SDD-cycle:speckit.checklist "UX implementation quality review"
/ai-framework:SDD-cycle:speckit.checklist "API contract completeness"
/ai-framework:SDD-cycle:speckit.checklist "Security implementation coverage"
/ai-framework:SDD-cycle:speckit.checklist "Performance criteria compliance"
```

**Output**: `checklists/<domain>.md` con ítems de validación post-implementación

**Tipos comunes**:

- `ux.md` - UI/UX implementation quality
- `api.md` - API contracts completeness
- `security.md` - Security implementation coverage
- `performance.md` - Performance criteria compliance

**⚠️ CAMBIO IMPORTANTE**: `checklist` se ejecuta DESPUÉS de `implement` (paso 8) para validar calidad de la implementación completada, NO antes.

**Cuándo usar**: (Opcional) POST-implementación para validar calidad del código generado, DESPUÉS de implement (paso 8 del flujo SDD-cycle).

---

### `/ai-framework:SDD-cycle:speckit.sync`

Sincroniza spec.md + plan.md + tasks.md a GitHub como child issue vinculado a parent PRP.

```bash
/ai-framework:SDD-cycle:speckit.sync <parent_issue_number>

# Ejemplo
/ai-framework:SDD-cycle:speckit.sync 247
```

**Output**: GitHub Issue (child) + actualiza frontmatter con `github`, `github_synced`, `parent_prd`

**Cuándo usar**: (Opcional) DESPUÉS de implementación completa - documenta lo que fue construido.

---

### `/ai-framework:SDD-cycle:speckit.constitution`

Crea o actualiza constitución del proyecto con principios fundamentales.

```bash
/ai-framework:SDD-cycle:speckit.constitution
```

**Output**: `.specify/memory/constitution.md` actualizada con sync impact report

**⚠️ RESTRICCIÓN**: NO EJECUTAR sin autorización directa del usuario.

**Cuándo usar**: Setup inicial o actualización de principios fundamentales.

---

## 📦 Gestión de Worktrees

### Worktree vs Branch: Entendiendo la Diferencia

**Branch (MISMO directorio)** - Simple, desarrollo secuencial:

- Comando: `/ai-framework:SDD-cycle:speckit.specify`
- Comportamiento: `git checkout -b nueva-branch` en el directorio actual
- Workspace: El MISMO directorio cambia de rama
- Sesión Claude: La MISMA sesión continúa
- Casos de uso: Una feature a la vez, desarrollo lineal

**Worktree (directorio AISLADO)** - Seguro, trabajo paralelo:

- Comando: `/ai-framework:git-github:worktree:create`
- Comportamiento: `git worktree add ../worktree-XXX/` con rama nueva
- Workspace: Nuevo directorio INDEPENDIENTE del original
- Sesión Claude: Requiere NUEVA sesión en nueva ventana IDE
- Casos de uso: Múltiples features paralelas, bug fixes urgentes, experimentación

**Matriz de Decisión:**

| Necesidad                          | Usa Branch | Usa Worktree |
| ---------------------------------- | ---------- | ------------ |
| Desarrollo lineal (1 feature)      | ✅         | ❌           |
| Múltiples features en paralelo     | ❌         | ✅           |
| Bug fix urgente (no interrumpir)   | ❌         | ✅           |
| Experimentación/POC desechable     | ❌         | ✅           |
| Setup simple sin overhead          | ✅         | ❌           |
| Trabajo con main/develop inestable | ❌         | ✅           |

**Flujo Típico con Branches:**

```bash
# En main
/ai-framework:SDD-cycle:speckit.specify "feature A"
# → Ahora estás en branch 001-feature-a (MISMO directorio)
# → Trabajas en feature A
# → Commit + PR + Merge
# → Regresas a main: git checkout main
# → Repites para feature B
```

**Flujo Típico con Worktrees:**

```bash
# En main (workspace principal)
/ai-framework:git-github:worktree:create "feature A" main
# → IDE abre nueva ventana en ../worktree-feature-a/
# → En nueva ventana: inicias sesión Claude
# → Trabajas en feature A (workspace principal intacto)

# MIENTRAS feature A está en progreso:
# → En workspace principal (aún en main)
/ai-framework:git-github:worktree:create "feature B" main
# → IDE abre OTRA ventana en ../worktree-feature-b/
# → Ahora tienes 2 features en paralelo sin conflictos
```

---

### `/ai-framework:git-github:worktree:create`

Crea worktree aislado en directorio sibling con rama nueva y upstream configurado.

```bash
/ai-framework:git-github:worktree:create "<objetivo>" <parent-branch>

# Ejemplos
/ai-framework:git-github:worktree:create "implementar OAuth" main
/ai-framework:git-github:worktree:create "fix bug pagos" develop
```

**Output**:

- Crea worktree: `../worktree-<objetivo>/`
- Crea branch: `worktree-<objetivo>` (mismo nombre que directorio)
- Abre IDE automáticamente en nueva ventana (detecta code/cursor)
- Valida directorio limpio antes de crear

**Comportamiento**:

- ✅ Crea directorio AISLADO del workspace principal
- ✅ Abre IDE automáticamente (VS Code o Cursor)
- ✅ Actualiza rama padre desde remoto antes de crear
- ⚠️ Requiere iniciar nueva sesión Claude en la nueva ventana IDE

**Post-creación (CRÍTICO)**:

1. En la nueva ventana del IDE: Abrir terminal integrado (Cmd+\`)
2. Verificar: `pwd` → debe mostrar `../worktree-XXX/`
3. Iniciar nueva sesión: `claude`

**Cuándo usar**:

- Trabajo paralelo en múltiples features
- Bug fixes urgentes sin interrumpir trabajo actual
- Experimentación/POC sin afectar workspace principal

---

### `/ai-framework:git-github:worktree:cleanup`

Elimina worktrees con validación de ownership y cleanup triple (worktree/local/remote).

```bash
/ai-framework:git-github:worktree:cleanup              # Discovery mode
/ai-framework:git-github:worktree:cleanup <worktree1>  # Cleanup específico
```

**Output**: Triple cleanup + regresa automáticamente a main

**Cuándo usar**: Después de mergear PRs.

---

## 🔄 Git & GitHub

### `/ai-framework:git-github:commit`

Commits semánticos con grouping automático por categoría.

```bash
/ai-framework:git-github:commit "descripción"
/ai-framework:git-github:commit "all changes"

# Ejemplos
/ai-framework:git-github:commit "feat: add OAuth authentication"
/ai-framework:git-github:commit "all changes"
```

**Output**: Commits agrupados por tipo (feat, fix, docs, test, refactor, etc.)

**Cuándo usar**: Después de completar cambios.

---

### `/ai-framework:git-github:pr`

Crea PR con security review BLOCKING, push seguro y metadata completa.

```bash
/ai-framework:git-github:pr <target_branch>

# Ejemplos
/ai-framework:git-github:pr develop
/ai-framework:git-github:pr main
```

**Output**: PR en GitHub con:

- Summary completo
- Test plan
- Security review (BLOCKING)
- CI/CD integration

**Cuándo usar**: Para PRs con estándares de calidad.

---

### `/ai-framework:git-github:cleanup`

Post-merge cleanup workflow: actualiza CHANGELOG, limpia worktree, actualiza docs.

```bash
/ai-framework:git-github:cleanup

# Workflow incluye:
# 1. /ai-framework:utils:changelog (auto-detectar PRs mergeados)
# 2. /ai-framework:git-github:worktree:cleanup (si aplica)
# 3. /ai-framework:utils:docs (si necesario)
```

**Output**: Workspace limpio + documentación actualizada

**Cuándo usar**: Después de merge exitoso.

---

## 🛠️ Utilidades

### `/ai-framework:utils:understand`

Análisis comprehensivo de arquitectura, patrones y dependencies.

```bash
/ai-framework:utils:understand
/ai-framework:utils:understand "specific area"

# Ejemplos
/ai-framework:utils:understand
/ai-framework:utils:understand "authentication module"
```

**Output**: Mapeo completo de arquitectura existente

**Cuándo usar**: SIEMPRE antes de implementar feature compleja.

---

### `/ai-framework:utils:three-experts`

Panel de 3 expertos (backend/frontend/security) genera plan consensuado.

```bash
/ai-framework:utils:three-experts <goal>

# Ejemplo
/ai-framework:utils:three-experts "Design scalable authentication system"
```

**Output**: PLAN.md con propuestas → critique → decisión

**Cuándo usar**: Features complejas que requieren múltiples perspectivas.

---

### `/ai-framework:utils:docs`

Analiza y actualiza documentación usando specialist agents.

```bash
/ai-framework:utils:docs                 # Analizar toda la docs
/ai-framework:utils:docs README API      # Focus específico

# Ejemplos
/ai-framework:utils:docs
/ai-framework:utils:docs README CHANGELOG
```

**Output**: Documentación actualizada con análisis de calidad

**Cuándo usar**: Después de features o cambios importantes.

---

### `/ai-framework:utils:polish`

Polishing meticuloso de archivos AI-generated. Preserva 100% funcionalidad mientras mejora calidad.

```bash
/ai-framework:utils:polish <file_paths>

# Ejemplo
/ai-framework:utils:polish src/auth.ts src/components/Login.tsx
```

**⚠️ CRÍTICO**: Preserva 100% funcionalidad mientras mejora calidad.

**Cuándo usar**: Refinar contenido generado por AI.

---

### `/ai-framework:utils:deep-research`

Professional audit con metodología sistemática y multi-source validation.

```bash
/ai-framework:utils:deep-research "<investigation topic>"

# Ejemplo
/ai-framework:utils:deep-research "OAuth 2.0 security best practices for microservices"
```

**Output**: Reporte de investigación con fuentes verificadas

**Cuándo usar**: Investigaciones complejas, due diligence, market research.

---

### `/ai-framework:utils:changelog`

Actualiza CHANGELOG.md con PRs mergeados (Keep a Changelog format), detecta duplicados.

```bash
/ai-framework:utils:changelog                    # Auto-detectar PRs faltantes
/ai-framework:utils:changelog <pr_number>        # Single PR
/ai-framework:utils:changelog <pr1,pr2,pr3>     # Multiple PRs

# Ejemplos
/ai-framework:utils:changelog
/ai-framework:utils:changelog 247
/ai-framework:utils:changelog 245,246,247
```

**Output**: CHANGELOG.md actualizado siguiendo Keep a Changelog

**Cuándo usar**: Después de merge.

---

## 🎯 Workflows Completos

Ver workflows end-to-end en @ai-first-workflow.md

| Workflow          | Comandos Core (ORDEN CORRECTO)                                                                                                                                 |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Feature nueva** | `specify` → `clarify` → `plan` → `tasks` → **`agent-assignment`** → `[analyze]` → `implement` → `[checklist]` → `[sync]`                                       |
| **Con PRP**       | `prp-new` → `prp-sync` → `specify --from-issue` → `clarify` → `plan` → `tasks` → **`agent-assignment`** → `[analyze]` → `implement` → `[checklist]` → `[sync]` |
| **Bug fix**       | `worktree:create` → `understand` → `specify` → `clarify` → `plan` → `tasks` → **`agent-assignment`** → `[analyze]` → `implement` → `commit` → `pr`             |
| **Post-merge**    | `changelog` → `worktree:cleanup` → `docs` (o usar `/ai-framework:git-github:cleanup`)                                                                          |

**Comandos opcionales**: `[analyze]` `[checklist]` `[sync]`
**Comando crítico**: **`agent-assignment`** (casi mandatorio, paso 5)

---

## 💡 Tips de Uso

### Flujo Óptimo

- **NUNCA** saltarse `/ai-framework:SDD-cycle:speckit.clarify` - detecta problemas antes de implementar (paso 2 OBLIGATORIO)
- **CASI SIEMPRE** usar agent-assignment para features con 5+ tasks - speedup 3-10x (paso 5 CASI MANDATORIO)
- **SIEMPRE** usar worktrees para trabajo paralelo - evita branch pollution
- **SIEMPRE** dejar `/ai-framework:git-github:pr` ejecutar security review
- **OPCIONAL** generar checklists DESPUÉS de implementación para validar calidad (paso 8)
- **OPCIONAL** sync spec DESPUÉS de implementación completa (paso 9)

### Comandos Pre-Production

1. `/ai-framework:SDD-cycle:speckit.implement` - TDD enforcement automático
2. `/ai-framework:git-github:pr` - Security review blocking
3. `/ai-framework:utils:changelog` - Keep a Changelog compliance

### Parallel Execution

- `/ai-framework:SDD-cycle:speckit.implement` ejecuta agents en paralelo automáticamente
- Tasks marcadas `[P]` se ejecutan concurrentemente
- `/ai-framework:git-github:pr` ejecuta security review en paralelo

---

## 🎓 Jerarquía por Frecuencia

**Uso Diario** (>5x/día):
`/ai-framework:git-github:commit` · `/ai-framework:SDD-cycle:speckit.implement`

**Uso Regular** (1-3x/día):
`/ai-framework:git-github:worktree:create` · `/ai-framework:SDD-cycle:speckit.specify` · `/ai-framework:git-github:pr` · `/ai-framework:utils:understand`

**Uso Semanal**:
`/ai-framework:SDD-cycle:speckit.clarify` · `/ai-framework:utils:changelog` · `/ai-framework:utils:docs` · `/ai-framework:SDD-cycle:speckit.tasks`

**Uso Mensual/Setup**:
`/ai-framework:PRP-cycle:prp-new` · `/ai-framework:utils:three-experts` · `/ai-framework:SDD-cycle:speckit.constitution` · `/ai-framework:utils:deep-research`

---

## 📊 Estadísticas del Ecosistema

| Categoría      | Comandos | Notas                                |
| -------------- | -------: | ------------------------------------ |
| **PRP-cycle**  |        2 | Business layer                       |
| **SDD-cycle**  |        9 | Engineering layer (orden específico) |
| **git-github** |        5 | Delivery layer                       |
| **utils**      |        8 | Utilidades cross-cutting             |
| **TOTAL**      |       24 | Comandos disponibles                 |

---

_Última actualización: 2025-10-14 | 24 comandos documentados | PRP-SDD-GitHub ecosystem_
