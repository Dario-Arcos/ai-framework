# Workflow AI-First

::: tip Un principo que lo rige todo
Cada iniciativa comienza como conversación sobre **porqué** y **qué** necesitan los usuarios. El framework guía esa conversación hasta código production-ready.
:::

---

## El Ecosistema en 3 Capas

```text
PRP (Business Layer)
   ↓ Define WHAT to build
SDD (Engineering Layer)
   ↓ Define HOW to build
GitHub (Delivery Layer)
   ↓ Track & deliver
```

**Por qué estas capas:**

- **PRP**: Stakeholders hablan business (no tech stack)
- **SDD**: Engineers convierten a implementation plan testeable
- **GitHub**: Team tracks progress, not just code

---

## Primera Decisión: ¿Branch o Worktree?

### Branch Simple

**Cuándo:** Una feature a la vez, desarrollo lineal.

```bash
/speckit.specify "feature"
# → Branch en mismo directorio
```

**Trade-off:** Cambiar de feature requiere commit/stash.

---

### Worktree Aislado

**Cuándo:** Múltiples features paralelas, bug fix urgente, experimentación.

```bash
/worktree-create "feature" main
# → Directorio separado, nueva ventana IDE
```

**Post-setup:** En nueva ventana: `Cmd+\``, verifica `pwd`, ejecuta `claude`

**Beneficio:** Workspace principal intacto.

---

## El Workflow SDD (6 Pasos Core + 2 Opcionales)

::: info Philosophy
Cada paso previene problema específico que cuesta horas. No es burocracia - es speedup.
:::

**Comandos Opcionales:**

| Comando     | Cuándo                    | Propósito                                                    | ROI                              |
| ----------- | ------------------------- | ------------------------------------------------------------ | -------------------------------- |
| `analyze`   | Entre tasks e implement   | Valida consistencia entre spec/plan/tasks                    | Alto para features complejas     |
| `checklist` | Entre analyze e implement | Quality gate para requirements (unit tests for requirements) | Alto para requirements complejos |

### 1. Specify → Spec Técnica

```bash
/speckit.specify "add OAuth auth"
```

Convierte descripción en spec estructurada. Output: `specs/001-feature/spec.md`

---

### 2. Clarify → Detectar Ambigüedades

```bash
/speckit.clarify
```

**Por qué importa - Ejemplo:**

```text
Spec: "Add user authentication"

Sin clarify:
- Dev 1: Email/password
- Dev 2: OAuth
- Dev 3: SSO
→ 3 implementations, hours de meetings, refactor

Con clarify:
Claude: "¿Qué auth methods?"
You: "OAuth"
→ 1 implementation correcta, zero refactor
```

**ROI:** 2 minutos save 4 horas. Nunca skip este paso.

---

### 3. Plan → Design Artifacts

```bash
/speckit.plan
```

Genera: `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Beneficio:** Todos trabajan con el mismo data model. No "oh, asumí que User tenía este field".

---

### 4. Tasks → Implementation Breakdown

```bash
/speckit.tasks
```

Genera `tasks.md` con dependency ordering, parallel markers `[P]`, file paths.

**Beneficio:** No más "¿qué hago ahora?" Cada task es self-contained.

---

### 5. Analyze → Consistency Check (Optional)

```bash
/speckit.analyze
```

Valida spec ↔ plan ↔ tasks consistency. Detecta gaps temprano.

**Skip si:** Feature simple (1-4 tasks).
**Use si:** Feature compleja (10+ tasks).

---

### 5.5. Checklist → Quality Gate (Optional)

```bash
/speckit.checklist "UX requirements quality"
```

Genera "unit tests for requirements". Valida que tus requirements estén bien escritos.

**¿Qué valida?**

- ✅ Requirements completos (no falta información)
- ✅ Requirements claros (no ambigüedades)
- ✅ Requirements consistentes (no contradicciones)
- ❌ NO valida que el código funcione

**Workflow:**

```text
analyze → checklist (genera preguntas) → TÚ marcas checkboxes → implement (bloquea si incomplete)
```

**Por qué ANTES de implement:**

Detectas requirements malos ANTES de codear. Corriges spec. Evitas re-work.

**Skip si:** Requirements ultra-claros, feature simple.
**Use si:** Requirements complejos, múltiples stakeholders, áreas de riesgo.

---

### 6. Implement → TDD + Execution

```bash
/speckit.implement
```

Ejecuta tasks con TDD enforcement, assigned agents, parallel execution.

**Por qué TDD es natural aquí:**

```
Sin framework: Write → Hope → Debug → Fix (unpredictable)
Con framework: Test → Fail → Code → Pass (predecible)
```

---

## Con PRP o Sin PRP?

### Con PRP (Business-Driven)

**Cuándo:** La feature necesita aprobación de stakeholders.

```bash
/prp-new "feature-name"
/speckit.specify --from-prp {feature-name}
# → Continuar pasos 2-6 normalmente
```

**Beneficio:** Business y Tech separados pero vinculados.

---

### Sin PRP (Tech-Driven)

**Cuándo:** Bug fixes, refactorings, internal tools.

```bash
/speckit.specify "fix race condition"
# → Continuar pasos 2-6 normalmente
# → Omitir sync (no PRP parent issue)
```

**Beneficio:** Inicio más rápido, sin overhead de negocio.

---

## Patterns Por Complexity

### Size S (≤80 LOC): Minimal Workflow

```bash
specify → clarify → plan → tasks → implement → commit → pr
```

**Skip:** analyze (overhead > benefit para size S)
**Time:** 5-10 min

---

### Size M (≤250 LOC): Full Workflow

```bash
specify → clarify → plan → tasks → [analyze] → [checklist] → implement → commit → pr
```

**Opcionales recomendados:** analyze (consistency), checklist (quality gate)
**Time:** 15-45 min

---

### Hotfix: Rapid + Isolated

```bash
worktree:create → understand → specify → clarify → plan → tasks → implement → commit → pr → cleanup
```

**Skip opcionales:** analyze, checklist, sync (prioridad = speed)
**Beneficio:** Trabajo principal intacto, fix rápido

---

## 🧭 Decision Trees

**¿PRP?**

```
¿Stakeholder approval needed? → YES: Use PRP | NO: Skip to SDD
```

**¿Worktree?**

```
¿Work in progress que no quieres interrumpir? → YES: worktree | NO: branch
```

---

## Post-Merge

```bash
/changelog      # Auto-detect merged PRs
/git-cleanup   # Delete branch, sync base
```

Si usaste worktree, cleanup regresa automáticamente a main.

---

## Mejores Prácticas

**Selección de Workflow:**
Comienza de forma simple (branch). Mejora a worktree cuando necesites aislamiento.

**Estrategia de Clarify:**
Responde preguntas incluso si parecen obvias. 2 min ahora > 2 horas después.

**Quality Gate:**
`/git-pullrequest` ejecuta pre-review con Observaciones Contextualizadas. Detecta issues y ofrece auto fix con re-validación.

**Estrategia de Commit:**
`commit "all changes"` auto-agrupa por categoría. Mejor que 1 commit gigante mezclado.

---

## Para Profundizar

- [Commands Guide](./commands-guide.md) — Completo conjunto de comandos, uso, opciones
- [Agents Guide](./agents-guide.md) — Extensa biblioteca de agentes, cuándo usar
- [MCP Servers](./mcp-servers.md) — Playwright, Shadcn
- [Pro Tips](./claude-code-pro-tips.md) — Patrones avanzados

---

::: info Última Actualización
**Fecha**: 2025-10-16 | **Ecosistema**: PRP-SDD-GitHub
:::
