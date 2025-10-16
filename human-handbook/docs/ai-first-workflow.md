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
/ai-framework:SDD-cycle:speckit.specify "feature"
# → Branch en mismo directorio
```

**Trade-off:** Cambiar de feature requiere commit/stash.

---

### Worktree Aislado

**Cuándo:** Múltiples features paralelas, bug fix urgente, experimentación.

```bash
/ai-framework:git-github:worktree:create "feature" main
# → Directorio separado, nueva ventana IDE
```

**Post-setup:** En nueva ventana: `Cmd+\``, verify `pwd`, run `claude`

**Benefit:** Workspace principal intacto.

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
| `sync`      | Después de implement      | Documenta en GitHub lo construido                            | Solo si usas PRP workflow        |

### 1. Specify → Spec Técnica

```bash
/ai-framework:SDD-cycle:speckit.specify "add OAuth auth"
```

Convierte descripción en spec estructurada. Output: `specs/001-feature/spec.md`

---

### 2. Clarify → Detectar Ambigüedades

```bash
/ai-framework:SDD-cycle:speckit.clarify
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
/ai-framework:SDD-cycle:speckit.plan
```

Genera: `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Benefit:** Everyone trabaja con mismo data model. No "oh, asumí que User tenía este field".

---

### 4. Tasks → Implementation Breakdown

```bash
/ai-framework:SDD-cycle:speckit.tasks
```

Genera `tasks.md` con dependency ordering, parallel markers `[P]`, file paths.

**Benefit:** No más "¿qué hago ahora?" Cada task es self-contained.

---

### 5. Analyze → Consistency Check (Optional)

```bash
/ai-framework:SDD-cycle:speckit.analyze
```

Valida spec ↔ plan ↔ tasks consistency. Detecta gaps temprano.

**Skip si:** Feature simple (1-4 tasks).
**Use si:** Feature compleja (10+ tasks).

---

### 5.5. Checklist → Quality Gate (Optional)

```bash
/ai-framework:SDD-cycle:speckit.checklist "UX requirements quality"
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
/ai-framework:SDD-cycle:speckit.implement
```

Ejecuta tasks con TDD enforcement, assigned agents, parallel execution.

**Por qué TDD es natural aquí:**

```
Sin framework: Write → Hope → Debug → Fix (unpredictable)
Con framework: Test → Fail → Code → Pass (predecible)
```

---

### 7. Sync → GitHub Documentation (Optional)

```bash
/ai-framework:SDD-cycle:speckit.sync {parent_issue_number}
```

Documenta en GitHub lo que fue construido. Vincula spec técnica a PRP parent issue.

**Cuándo ejecutar:** DESPUÉS de implementación completa y validada.

**Por qué después de implementar:**

- GitHub issue documenta lo que SÍ construiste (no especulación)
- Spec + Plan + Tasks son 100% accurate con código final
- Stakeholders ven resultados, no work-in-progress
- Zero necesidad de re-sync

**Skip si:** No usas PRP workflow, feature interna sin stakeholders.
**Use si:** Feature con PRP parent issue, documentación para stakeholders.

---

## Con PRP o Sin PRP?

### Con PRP (Business-Driven)

**Cuándo:** La feature necesita aprobación de stakeholders.

```bash
/ai-framework:PRP-cycle:prp-new "feature-name"
/ai-framework:PRP-cycle:prp-sync "feature-name"
/ai-framework:SDD-cycle:speckit.specify --from-issue {number}
# → Continue steps 2-6 normalmente
# → Al final: speckit.sync (documenta en GitHub)
```

**Benefit:** Business y Tech separated pero linked.

---

### Sin PRP (Tech-Driven)

**Cuándo:** Bug fixes, refactorings, internal tools.

```bash
/ai-framework:SDD-cycle:speckit.specify "fix race condition"
# → Continue steps 2-6 normalmente
# → Skip sync (no PRP parent issue)
```

**Benefit:** Faster start, no business overhead.

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
**Benefit:** Trabajo principal untouched, fix rápido

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
/ai-framework:utils:changelog      # Auto-detect merged PRs
/ai-framework:git-github:cleanup   # Delete branch, sync base
```

Si usaste worktree, cleanup regresa automáticamente a main.

---

## Best Practices

**Workflow Selection:**
Comienza de forma simple (branch). Mejora a worktree cuando necesites aislamiento.

**Clarify Strategy:**
Answer questions even if obvious. 2 min ahora > 2 hours later.

**Security Review:**
`/ai-framework:git-github:pr` auto-runs security review. Blocks PR si HIGH vulnerability found.

**Commit Strategy:**
`commit "all changes"` auto-groups por categoría. Better que 1 giant mixed commit.

---

## Para Profundizar

- [Commands Guide](./commands-guide.md) — Completo conjunto de comandos, usage, options
- [Agents Guide](./agents-guide.md) — Extensa biblioteca de agentes, cuándo usar
- [MCP Servers](./mcp-servers.md) — Playwright, Shadcn
- [Pro Tips](./claude-code-pro-tips.md) — Advanced patterns

---

## Herramienta Opcional: Agent Strategy Advisor

::: tip Planificación Consultiva
Si no estás seguro qué agentes usar para una tarea compleja, puedes consultar al `agent-strategy-advisor`:

```bash
/ai-framework:Task agent-strategy-advisor "Analiza mi tasks.md y recomienda agentes"
```

**Este agente NO ejecuta tareas**, solo analiza y recomienda:

- Qué agentes usar para qué trabajo
- Cuándo usar agentes vs. main Claude
- ROI realista de paralelización
- Estrategia de ejecución con justificación

**Úsalo cuando**:

- Planeas trabajo complejo y no sabes qué agentes usar
- Quieres aprender el ecosistema de agentes
- Necesitas justificación de estrategia para tu equipo

**No lo uses cuando**:

- Ya sabes qué agentes necesitas
- Trabajo simple (<80 LOC)
- Necesitas ejecución inmediata (no planificación)
  :::

---

::: info Última Actualización
**Fecha**: 2025-10-16 | **Ecosistema**: PRP-SDD-GitHub
:::
