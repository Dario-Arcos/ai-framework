# Guía de Comandos Claude Code

::: tip ¿Qué son los Comandos?
Slash commands que ejecutan workflows completos del ciclo AI-first development. Diseñados para usarse en secuencia específica (ver workflows).
:::

---

| Categoría                                                     | Flujo Típico                           |
| ------------------------------------------------------------- | -------------------------------------- |
| [Ciclo PRP (Business Layer)](#ciclo-prp-business-layer)       | Product Requirements → GitHub Tracking |
| [Git & GitHub](#git-github)                                   | Commit → PR → Cleanup                  |
| [Utilidades](#utilidades)                                     | Understand → Research                  |
| [Plugins Externos](#plugins-externos-opcional)                | Memory Search (requiere instalación)   |

---

## Ciclo PRP (Business Layer)

### `/prp-new`

::: tip Propósito
**Discovery Engine** - Proceso conversacional para definir QUÉ problema resolver y POR QUÉ importa, antes de cualquier consideración técnica.
:::

**Filosofía:**

```
"No documentamos requisitos - descubrimos oportunidades"
```

**Usage:**

```bash
/prp-new                           # Desde cero
/prp-new "contexto inicial"        # Con contexto previo
/prp-new docs/research.md          # Desde documento existente
```

**4 Fases de Discovery:**

| Fase | Objetivo | Técnica |
|------|----------|---------|
| 1. CONTEXTO | Entender situación actual | Preguntas abiertas |
| 2. PROBLEMA | Excavar hasta causa raíz | Five Whys adaptado |
| 3. IMPACTO | Cuantificar consecuencias | Métricas de negocio |
| 4. OPORTUNIDAD | Definir outcome deseado | Sin solución técnica |

**Validación Dual:**

- **Usuario valida**: "¿Entendiste MI problema correctamente?"
- **Claude valida**: "¿El output cumple estándares metodológicos world-class?"

**Output:** `prps/{project_name}/discovery.md`

::: details Estructura del Output

```markdown
## Opportunity Statement
"[Stakeholder] necesita [outcome deseado]
cuando [situación/contexto]
porque actualmente [fricción/dolor]
lo que causa [consecuencia de negocio]."

## Contexto
**Síntesis**: [Resumen]
**Evidencia**: > "Citas textuales del usuario"

## Problema Raíz
## Impacto
## Outcome Deseado
```

:::

::: tip Principios Clave
- **Una pregunta a la vez** - No abrumar
- **AskUserQuestion** para opciones múltiples
- **Síntesis + Evidencia** - Preserva palabras exactas del usuario
- **Cero soluciones técnicas** - Solo problema y oportunidad
:::

**Siguientes Pasos:** Continuar con planificacion tecnica sistematica.

---

## Git & GitHub

### `/git-commit`

::: tip Propósito
Commits semánticos con agrupación automática y soporte corporativo.
:::

**Casos de Uso:**

```bash
# 1. Formato Convencional (proyectos open source)
/git-commit "feat(auth): add OAuth2 support"

# 2. Task ID solo (tipo automático desde archivos modificados)
/git-commit "TRV-345 implementar autenticación"

# 3. Tipo + Task ID (RECOMENDADO - control total)
/git-commit "refactor: TRV-345 mejorar módulo auth"

# 4. Auto-commit (cuando no tienes Task ID)
/git-commit "all changes"
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

**Siguientes Pasos:** `➜ /git-pullrequest`

---

### `/git-pullrequest`

::: tip Propósito
Crea PR con quality gate basado en Observaciones Contextualizadas: pre-review inteligente sin falsos positivos.
:::

**Usage:**

```bash
# Desde feature branch → PR a main
/git-pullrequest main
```

**Proceso (3 fases):**

1. **Validación + Contexto**
   - Valida target branch existe
   - Extrae commits, stats, formato (conventional/corporate)
   - Auto-detecta tipo primario (feat/fix/refactor)
   - **Corporate format:** Detecta `type|TASK-ID|YYYYMMDD|desc` (e.g., `feat|TRV-350|20251023|add auth`)

2. **Review + Decisión** (ciclo con opción de fixes)
   - **Revisión en paralelo (3 capas)**:
     - **Code review**: Lógica, arquitectura, bugs, tests (via code-reviewer)
     - **Security review**: SQL injection, secrets, XSS, auth bypass (via security-reviewer)
     - **Observaciones**: Tests, complejidad, API, breaking changes (auto-detectadas)
   - **Decisión:** Create PR / Auto fix / Cancel
   - Si auto fix: subagent arregla Critical+Important+High+Medium issues → re-review (ambos) → usuario decide

3. **Crear PR**
   - **Protected branch detection**: Si estás en main, master, develop, development, staging, stage, production, prod, release, releases, qa, uat, o hotfix → crea temp branch `pr/{slug}-{timestamp}` automáticamente
   - Si corporate format: Pregunta título (usar primer commit o custom)
   - gh pr create con findings de ambas reviews en body
   - Output: PR URL

::: info Observaciones ≠ Bloqueantes
Las observaciones son **hechos con contexto**, no acusaciones. Tú decides si crear PR con issues documentados o arreglar primero.
:::

**Examples disponibles** (en `skills/pr-workflow/examples/`):
- `success-no-findings.md` - Review limpio, directo a PR
- `success-with-findings.md` - Issues encontrados, usuario procede
- `auto-fix-loop.md` - Loop de auto fix con re-review
- `manual-cancellation.md` - Usuario cancela para fix manual

**Output:** PR URL + resumen de observaciones

**Siguientes Pasos:** Después de merge → `/git-cleanup`

---

### `/git-cleanup`

::: tip Propósito
Limpia feature branch y sincroniza con base branch después de merge.
:::

**Usage:**

```bash
/git-cleanup
/git-cleanup main
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

### `/worktree-create`

::: tip Propósito
Crea worktree aislado en directorio sibling con rama nueva y upstream configurado.
:::

**Usage:**

```bash
/worktree-create "{objetivo}" {parent-branch}
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

### `/worktree-cleanup`

::: tip Propósito
Elimina worktrees con validación de ownership y cleanup triple (worktree/local/remote).
:::

**Usage:**

```bash
/worktree-cleanup              # Discovery mode
/worktree-cleanup {worktree1}  # Cleanup específico
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

### `/understand`

::: tip Propósito
Análisis comprehensivo de arquitectura, patrones y dependencies.
:::

**Usage:**

```bash
/understand
/understand "specific area"
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

### `/deep-research`

::: tip Propósito
Professional audit con metodología sistemática y validación de múltiples fuentes.
:::

**Usage:**

```bash
/deep-research "{investigation topic}"
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

### `/changelog`

::: tip Propósito
Actualiza CHANGELOG.md con análisis **Truth-Based** del diff real entre versiones.
:::

**Principio fundamental:** Los commits cuentan una historia. El diff cuenta la verdad.

**Usage:**

```bash
/changelog "desde última versión"
/changelog "desde v2.0.0"
/changelog "todos los cambios"
```

**Por qué Truth-Based:**

```
Commits:                          Realidad (diff):
─────────────────────────────     ─────────────────────────────
1. feat: add caching              Solo existe: logging.py
2. fix: caching bug
3. revert: remove caching         El caching NO EXISTE.
4. feat: add logging              Documentarlo sería MENTIR.
```

**Workflow (8 fases):**

1. **Determinar rango** - Parsear argumentos (`$last_tag..HEAD`)
2. **Extraer la verdad** - `git diff --name-status` (no commits)
3. **Análisis semántico** - Diff por archivo, categorizar cambios reales
4. **Contexto del "por qué"** - Commits/PRs como enriquecimiento
5. **Agrupación inteligente** - Una entrada por feature, no por archivo
6. **Síntesis y redacción** - Español, técnico, conciso
7. **Actualizar CHANGELOG** - Edit sección `[No Publicado]`
8. **Reporte final** - Estadísticas de confiabilidad

**Ventajas:**

| Aspecto | Commit-Based | Truth-Based |
|---------|--------------|-------------|
| Completitud | ~80% (solo PRs) | 100% (todo el diff) |
| Reverts | Contaminan | Auto-cancelados |
| Commits directos | Ignorados | Incluidos |
| Confiabilidad | Variable | Garantizada |

::: warning NO commitea automáticamente
El comando actualiza el archivo pero NO hace commit. Tú decides cuándo.
:::

**Output:** CHANGELOG.md actualizado + reporte de análisis

**Siguientes Pasos:** `➜ /release`

---

### `/release`

::: tip Propósito
Workflow completo de release: bump versión → actualizar CHANGELOG → sync → commit/tag → push.
:::

**Usage:**

```bash
/release
```

**Pre-requisitos:** CHANGELOG.md actualizado + sección `[No Publicado]` con cambios + package.json con `version`

**Proceso:** Validar herramientas/archivos → Preguntar tipo release (patch/minor/major) → Ejecutar `npm version` (auto-dispara sync) → Actualizar CHANGELOG con versión → Verificar commit/tag → Preguntar si push

::: warning Auto-sync
`npm version` ejecuta automáticamente `scripts/sync-versions.cjs` que sincroniza versiones en config.js, README.md, docs/changelog.md
:::

**Output:** Release completo (local o remoto según elección)

---

### `/project-init`

::: tip Propósito
Genera reglas modulares de proyecto que se comparten con el equipo y se cargan automáticamente en cada sesión.
:::

**Usage:**

```bash
/project-init
```

**Arquitectura Dual (Team-Shared Rules):**

```
docs/claude-rules/        ← TRACKED (source of truth)
├── stack.md              │  • Versionado en git
├── patterns.md           │  • Reviewable en PRs
├── architecture.md       │  • Compartido con equipo
└── testing.md            │
        ↓ session-start hook (auto-sync)
.claude/rules/            ← IGNORED (working copy)
└── (synced automatically)
```

::: info Patrón .env.example
Similar a `.env.example` → `.env`: las rules canónicas viven tracked, cada dev tiene copia local auto-synced.
:::

**Beneficios:**
- **Team-shared**: Rules versionadas, reviewables en PRs
- **Zero config**: Session-start sincroniza automáticamente
- **Carga nativa**: Auto-loaded con misma prioridad que CLAUDE.md
- **Modular**: Actualiza un aspecto sin tocar otros

**Proceso:**

**Phase 1:** Cleanup & Preparation - Detecta estado existente, limpia reglas anteriores
**Phase 2:** Project Analysis - 5 layers de extracción (Manifests → Configs → Structure → Patterns → Key Files)
**Phase 3:** Generate Rules - Escribe en `docs/claude-rules/` (tracked)
**Phase 4:** Sync to Local - Copia a `.claude/rules/` (ignored)

::: details Output

```
✅ Generated docs/claude-rules/ (tracked):
   • stack.md        (runtime, framework, dependencies)
   • patterns.md     (naming, imports, error handling)
   • architecture.md (structure, layers, entry points)
   • testing.md      (if tests detected)

📋 Synced to .claude/rules/ (local working copy)

💡 Rules flow:
   • docs/claude-rules/ → commit to git (team-shared)
   • .claude/rules/ → auto-synced on session start
```

:::

::: warning Para Nuevos Miembros del Equipo
Si el proyecto ya tiene `docs/claude-rules/`, **no necesitas ejecutar `/project-init`**. El hook de session-start sincroniza automáticamente las rules a tu `.claude/rules/` local.
:::

---

### `/setup-dependencies`

::: tip Propósito
Instala dependencias esenciales faltantes con platform detection.
:::

**Usage:**

```bash
/setup-dependencies
```

**Proceso:** Detect platform → Dependency registry → Discover missing deps → Display status → Confirm installation → Group by installer → Install by package manager → Verify installation → Report results

**Dependency Registry Format:**

```bash
"tool_name|installer|platforms|purpose"
```

**Supported:** installers (brew, pip, npm, apt), platforms (darwin, linux, all)

---

## Plugins Externos (Opcional)

::: warning Requisito de Instalación
Estos comandos requieren instalar plugins externos. **No están incluidos en ai-framework por defecto.**

Si no tienes el plugin instalado, el comando no existirá en tu sesión de Claude Code.
:::

### `/episodic-memory:search-conversations`

::: tip Propósito
Busca conversaciones pasadas de Claude Code usando búsqueda semántica o textual. Permite recuperar contexto de sesiones anteriores.
:::

**Plugin Requerido:** [episodic-memory](https://github.com/obra/episodic-memory)

**Instalación:**

```bash
/plugin install episodic-memory@superpowers-marketplace
```

**Usage:**

```bash
/episodic-memory:search-conversations
```

**Cómo Funciona:**

1. El plugin indexa automáticamente tus conversaciones al finalizar cada sesión
2. Puedes buscar en el histórico usando búsqueda semántica (por conceptos) o textual (exacta)
3. Claude también puede buscar automáticamente cuando referencias trabajo pasado en conversación

**Parámetros de Búsqueda (MCP Tool Subyacente):**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `query` | string \| array | Término(s) de búsqueda |
| `mode` | 'vector' \| 'text' \| 'both' | Tipo de búsqueda (default: 'both') |
| `limit` | 1-50 | Cantidad de resultados |
| `after` / `before` | YYYY-MM-DD | Filtros de fecha |
| `response_format` | 'markdown' \| 'json' | Formato de salida |

**Casos de Uso:**

```bash
# Buscar decisiones sobre autenticación
"¿Qué decidimos sobre el sistema de auth?"

# Buscar soluciones a errores similares
"¿Cómo resolvimos el error de conexión a DB?"

# Recuperar contexto de un proyecto específico
"¿Qué patrones establecimos para el API?"
```

::: tip Cuándo Usar
- **Al inicio de sesión**: Recuperar contexto de trabajo previo
- **Cuando estás atascado**: Buscar soluciones similares que ya resolviste
- **Para consistencia**: Verificar decisiones arquitectónicas anteriores
:::

::: danger Sin Plugin = Sin Comando
Si ejecutas `/episodic-memory:search-conversations` sin tener instalado el plugin, Claude Code no reconocerá el comando. Asegúrate de instalar primero:

```bash
/plugin install episodic-memory@superpowers-marketplace
```
:::

---

## Workflows Completos

### Tabla Comparativa de Workflows

| Workflow          | Comandos Core                                                                    |
| ----------------- | -------------------------------------------------------------------------------- |
| **Feature nueva** | `prp-new` → `understand` → implement → `commit` → `pullrequest`                  |
| **Bug fix**       | `worktree-create` → `understand` → fix → `commit` → `pullrequest`                |
| **Post-merge**    | `changelog` → `worktree-cleanup` → `docs` (o usar `/git-cleanup`)                |

---

## Consejos de Uso

::: tip SIEMPRE

- Usar worktrees para trabajo paralelo - evita branch pollution
- Dejar `/git-pullrequest` ejecutar security review
  :::

---

::: info Última Actualización
**Fecha**: 2026-01-11
:::
