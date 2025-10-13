# Guía de Comandos Claude Code

**22 comandos disponibles** organizados por flujo de desarrollo

---

## 🚀 Inicio de Sesión

### `/utils:session-start`

Configura workspace, muestra issues activos, valida git y sincroniza con remoto. Primera acción en cada sesión.

```bash
/utils:session-start
```

---

## 📦 Gestión de Worktrees

### `/git-github:worktree:create`

Crea worktree aislado en directorio sibling con rama nueva y upstream configurado. SIEMPRE para desarrollo - mantiene workspace principal limpio.

```bash
/git-github:worktree:create "<objetivo>" <parent-branch>

# Ejemplos
/git-github:worktree:create "implementar OAuth" main
/git-github:worktree:create "fix bug pagos" develop
```

### `/git-github:worktree:cleanup`

Elimina worktrees con validación de ownership y cleanup triple (worktree/local/remote). Después de mergear PRs.

```bash
/git-github:worktree:cleanup              # Discovery mode
/git-github:worktree:cleanup <worktree1>  # Cleanup específico
```

---

## 🎯 Ciclo PRD

### `/PRD-cycle:prd-new`

Brainstorming para crear Product Requirements Document estructurado (minimalista, business-focused). Planificación de nueva feature desde cero.

```bash
/PRD-cycle:prd-new <feature_name>
```

### `/PRD-cycle:prd-sync`

Sincroniza PRD a GitHub como Parent Issue. Después de aprobar PRD, para tracking en GitHub.

```bash
/PRD-cycle:prd-sync <feature_name>
/PRD-cycle:prd-sync <feature_name> --milestone <number>
```

---

## 🏗️ Ciclo SDD

### `/SDD-cycle:specify`

Crea especificación técnica desde lenguaje natural o GitHub Issue. Primera fase SDD - convierte requisitos en spec técnica.

```bash
/SDD-cycle:specify "Create authentication system"
/SDD-cycle:specify --from-issue 456
/SDD-cycle:specify --from-prd <feature_name>
```

### `/SDD-cycle:clarify`

Detecta ambigüedades en spec, hace hasta 5 preguntas targeted. **ANTES** de `/SDD-cycle:plan`.

```bash
/SDD-cycle:clarify
```

### `/SDD-cycle:plan`

Genera artifacts de diseño (research.md, data-model.md, contracts/, quickstart.md). Describe estrategia para tasks pero NO los crea. Después de spec clarificada.

```bash
/SDD-cycle:plan
```

### `/SDD-cycle:tasks`

Genera tasks.md ejecutable con dependency ordering y GitHub sub-issues integration. Después de plan, antes de analyze.

```bash
/SDD-cycle:tasks
```

### `/SDD-cycle:analyze`

Análisis cross-artifact de consistency y quality, genera coordination plan. Validación pre-implementación.

```bash
/SDD-cycle:analyze
```

### `/SDD-cycle:implement`

Ejecuta tasks.md con parallelization, specialized agents y TDD enforcement. Motor central de implementación.

```bash
/SDD-cycle:implement
```

### `/SDD-cycle:constitution`

Crea/actualiza constitución del proyecto. Setup inicial o actualización de principios fundamentales.

**⚠️ RESTRICCIÓN**: NO EJECUTAR sin autorización directa del usuario.

```bash
/SDD-cycle:constitution
```

---

## 🔄 Git & GitHub

### `/git-github:commit`

Commits semánticos con grouping automático por categoría. Después de completar cambios.

```bash
/git-github:commit "descripción"
/git-github:commit "all changes"
```

### `/git-github:pr`

Crea PR con security review BLOCKING, push seguro y metadata completa. Para PRs con estándares de calidad.

```bash
/git-github:pr <target_branch>
```

### `/git-github:issue-manager`

Dashboard inteligente o análisis detallado con complejidad, prioridad y próximos pasos. Visión de workload o análisis pre-implementación.

```bash
/git-github:issue-manager              # Dashboard
/git-github:issue-manager <number>     # Análisis profundo
```

### `/git-github:issue-sync`

Push local updates como GitHub issue comments para audit trail.

```bash
/git-github:issue-sync <issue_number>
```

---

## 🛠️ Utilidades

### `/utils:understand`

Análisis comprehensivo de arquitectura, patrones y dependencies. SIEMPRE antes de implementar feature compleja.

```bash
/utils:understand
/utils:understand "specific area"
```

### `/utils:three-experts`

Panel de 3 expertos (backend/frontend/security) genera plan consensuado. Features complejas que requieren múltiples perspectivas.

```bash
/utils:three-experts <goal>
```

### `/utils:docs`

Analiza y actualiza documentación usando specialist agents. Después de features o cambios importantes.

```bash
/utils:docs                 # Analizar toda la docs
/utils:docs README API      # Focus específico
```

### `/utils:polish`

Polishing meticuloso de archivos AI-generated. Refinar contenido generado por AI.

**⚠️ CRÍTICO**: Preserva 100% funcionalidad mientras mejora calidad.

```bash
/utils:polish <file_paths>
```

### `/utils:deep-research`

Professional audit con metodología sistemática y multi-source validation. Investigaciones complejas, due diligence, market research.

```bash
/utils:deep-research "<investigation topic>"
```

### `/utils:changelog`

Actualiza CHANGELOG.md con PRs mergeados (Keep a Changelog format), detecta duplicados. Después de merge.

```bash
/utils:changelog                    # Auto-detectar PRs faltantes
/utils:changelog <pr_number>        # Single PR
/utils:changelog <pr1,pr2,pr3>     # Multiple PRs
```

---

## 🎯 Workflows

Ver workflows completos en @ai-first-workflow.md

| Workflow          | Comandos Core                                                                                            |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| **Feature nueva** | `specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement`                                       |
| **Con PRD**       | `prd-new` → `prd-sync` → `specify --from-issue` → `clarify` → `plan` → `tasks` → `analyze` → `implement` |
| **Bug fix**       | `worktree:create` → `understand` → fix → `commit` → `pr`                                                 |
| **Análisis**      | `issue-manager` → `understand` (si necesario)                                                            |

---

## 💡 Tips de Uso

### Flujo Óptimo

- **Siempre** iniciar con `/utils:session-start`
- **Siempre** usar worktrees (evita branch pollution)
- **Nunca** saltarse `/SDD-cycle:clarify`
- **Siempre** dejar `/git-github:pr` ejecutar security review

### Comandos Pre-Production

1. `/SDD-cycle:implement` - TDD enforcement automático
2. `/git-github:pr` - Security review blocking
3. `/utils:changelog` - Keep a Changelog compliance

### Parallel Execution

- `/SDD-cycle:implement` y `/git-github:pr` ejecutan agents en paralelo automáticamente
- Tasks marcadas `[P]` se ejecutan concurrentemente

---

## 🎓 Jerarquía por Frecuencia

**Uso Diario** (>5x/día):
`/utils:session-start` · `/git-github:commit` · `/SDD-cycle:implement`

**Uso Regular** (1-3x/día):
`/git-github:worktree:create` · `/SDD-cycle:specify` · `/git-github:pr` · `/utils:understand`

**Uso Semanal**:
`/SDD-cycle:clarify` · `/utils:changelog` · `/utils:docs` · `/git-github:issue-manager`

**Uso Mensual/Setup**:
`/PRD-cycle:prd-new` · `/utils:three-experts` · `/SDD-cycle:constitution` · `/utils:deep-research`

---

_Última actualización: 2025-10-07 | 22 comandos documentados_
