# Workflow AI-First

::: tip Un principo que lo rige todo
Cada iniciativa comienza como conversación sobre **porqué** y **qué** necesitan los usuarios. El framework guía esa conversación hasta código production-ready.
:::

---

## 🎯 El Ecosistema en 3 Capas

```
📋 PRP (Business Layer)
   ↓ Define WHAT to build
🏗️ SDD (Engineering Layer)
   ↓ Define HOW to build
🔄 GitHub (Delivery Layer)
   ↓ Track & deliver
```

**Por qué estas capas:**

- **PRP**: Stakeholders hablan business (no tech stack)
- **SDD**: Engineers convierten a implementation plan testeable
- **GitHub**: Team tracks progress, not just code

---

## 🎨 Primera Decisión: ¿Branch o Worktree?

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

## 🔄 El Workflow SDD (7 Pasos Core)

::: info Philosophy
Cada paso previene problema específico que cuesta horas. No es burocracia - es speedup.
:::

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

```
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

### 5. Agent Assignment → Parallel Optimization

```bash
/ai-framework:Task agent-assignment-analyzer "Analyze tasks"
```

**Cuándo vale la pena:**

```
Sin assignment:   210 min sequential
Con assignment:    75 min parallel (3 streams)
Speedup: 2.8x
```

**Rule of thumb:**

- 1-4 tasks: Skip (overhead > benefit)
- 5-10 tasks: Use (good ROI)
- 10+ tasks: Definitely (massive speedup)

---

### 6. Analyze → Consistency Check (Optional)

```bash
/ai-framework:SDD-cycle:speckit.analyze
```

Valida spec ↔ plan ↔ tasks consistency. Detecta gaps temprano.

**Skip si:** Feature simple (1-4 tasks).
**Use si:** Feature compleja (10+ tasks).

---

### 7. Implement → TDD + Execution

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

## 🎭 Con PRP o Sin PRP?

### Con PRP (Business-Driven)

**Cuándo:** Feature needs stakeholder buy-in.

```bash
/ai-framework:PRP-cycle:prp-new "feature-name"
/ai-framework:PRP-cycle:prp-sync "feature-name"
/ai-framework:SDD-cycle:speckit.specify --from-issue &lt;number&gt;
# → Continue steps 2-7 normalmente
```

**Benefit:** Business y Tech separated pero linked.

---

### Sin PRP (Tech-Driven)

**Cuándo:** Bug fixes, refactorings, internal tools.

```bash
/ai-framework:SDD-cycle:speckit.specify "fix race condition"
# → Continue steps 2-7 normalmente
```

**Benefit:** Faster start, no business overhead.

---

## 💡 Patterns Por Complexity

### Size S (≤80 LOC): Minimal Workflow

```bash
specify → clarify → plan → tasks → implement → commit → pr
```

**Skip:** agent-assignment, analyze (overhead > benefit)
**Time:** 5-10 min

---

### Size M (≤250 LOC): Full Workflow

```bash
specify → clarify → plan → tasks → agent-assignment → analyze → implement → commit → pr
```

**Include:** agent-assignment (5+ tasks), analyze (validation)
**Time:** 15-45 min (2-3x faster con agent-assignment)

---

### Hotfix: Rapid + Isolated

```bash
worktree:create → understand → specify → clarify → plan → tasks → implement → commit → pr → cleanup
```

**Skip:** agent-assignment (speed matters)
**Benefit:** Trabajo principal untouched

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

**¿Agent Assignment?**

```
Tasks count: 1-4 → Skip | 5-10 → Use | 10+ → Definitely
```

---

## 🎬 Post-Merge

```bash
/ai-framework:utils:changelog      # Auto-detect merged PRs
/ai-framework:git-github:cleanup   # Delete branch, sync base
```

Si usaste worktree, cleanup regresa automáticamente a main.

---

## 🎨 Best Practices

**Workflow Selection:**
Start simple (branch). Upgrade a worktree cuando needs isolation.

**Clarify Strategy:**
Answer questions even if obvious. 2 min ahora > 2 hours later.

**Agent Assignment:**
Exception - si todas tasks touch mismo file, assignment no ayuda (sequential anyway).

**Security Review:**
`/ai-framework:git-github:pr` auto-runs security review. Blocks PR si HIGH vulnerability found.

**Commit Strategy:**
`commit "all changes"` auto-groups por categoría. Better que 1 giant mixed commit.

---

## 📚 Para Profundizar

- [Commands Guide](./commands-guide.md) — 24 comandos, usage, options
- [Agents Guide](./agents-guide.md) — 45 agents, cuándo usar
- [MCP Servers](./mcp-servers.md) — Playwright, Shadcn
- [Pro Tips](./claude-code-pro-tips.md) — Advanced patterns

---

::: info Última Actualización
**Fecha**: 2025-10-15 | **Ecosistema**: PRP-SDD-GitHub
:::
