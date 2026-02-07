# Commands

Slash commands para el ciclo de desarrollo. Cada uno resuelve un problema específico.

---

## Referencia rápida

| Command | Qué hace |
|---------|----------|
| `/git-commit` | Commits semánticos con agrupación |
| `/git-cleanup` | Limpieza post-merge |
| `/worktree-create` | Worktree aislado para trabajo paralelo |
| `/worktree-cleanup` | Eliminar worktrees |
| `/deep-research` | Investigación multi-fuente verificada |
| `/changelog` | Actualizar CHANGELOG desde diff real |
| `/release` | Bump versión + tag + GitHub release |
| `/project-init` | Generar reglas de proyecto |

---

## Git

### /git-commit

Commits semánticos con agrupación automática por tipo de archivo.

::: code-group
```bash [Convencional]
/git-commit "feat(auth): add OAuth2 support"
```

```bash [Corporativo]
/git-commit "TRV-345 implementar autenticación"
# Output: feat|TRV-345|20260131|implementar autenticación
```

```bash [Tipo explícito]
/git-commit "refactor: TRV-345 mejorar módulo auth"
```
:::

**Agrupación automática:** Si modificas archivos de 2+ categorías (config + código, docs + tests), crea commits separados por tipo.

---

---

### /git-cleanup

Limpieza después de merge: elimina feature branch, sincroniza con base.

```bash
/git-cleanup        # Auto-detecta base (main/master/develop)
/git-cleanup main   # Base explícita
```

GitHub elimina la branch remota al mergear. Este command limpia la local.

---

## Worktrees

::: tip Branch vs Worktree
**Branch:** Desarrollo lineal, una feature a la vez.
**Worktree:** Múltiples features en paralelo, cada una en directorio aislado.
:::

### /worktree-create

Crea worktree en directorio sibling con rama nueva.

```bash
/worktree-create "implementar autenticacion OAuth" main
# Crea: ../worktree-implementar-autenticacion-oauth
```

::: warning Después de crear
El IDE se abre automáticamente, pero debes iniciar nueva sesión Claude en esa ventana. Si no, Claude sigue trabajando en el directorio anterior.
:::

---

### /worktree-cleanup

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

## Release

### /changelog

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

### /release

Workflow completo: analiza CHANGELOG → propone versión → bump → tag → GitHub release.

```bash
/release
```

**Requisitos:**
- CHANGELOG.md con sección `[No Publicado]`
- package.json con `version`

Calcula versión según semver:
- Breaking changes → MAJOR
- Features nuevas → MINOR
- Solo fixes → PATCH

---

## Utilities

### /deep-research

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

### /project-init

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

## Plugins externos

::: warning Requiere instalación
Estos commands no están incluidos por defecto.
:::

### /episodic-memory:search-conversations

Busca en conversaciones pasadas de Claude Code.

```bash
/plugin install episodic-memory@superpowers-marketplace
```

Indexa automáticamente tus sesiones. Busca por conceptos (semántica) o texto exacto.

---

## Workflows típicos

| Escenario | Comandos |
|-----------|----------|
| **Feature nueva** | `/brainstorming` → implementar → `/git-commit` → `/pull-request` |
| **Bug fix urgente** | `/worktree-create` → fix → `/git-commit` → `/pull-request` |
| **Desarrollo autónomo** | `/ralph-orchestrator` (orquesta todo el pipeline) |
| **Post-merge** | `/git-cleanup` |
| **Release** | `/changelog` → `/release` |

---

::: info Última actualización
**Fecha**: 2026-01-31 | **Commands**: 11 total
:::
