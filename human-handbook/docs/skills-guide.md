# Guía de Skills

::: tip ¿Qué son las Skills?
Capacidades especializadas que extienden Claude con conocimiento experto y workflows probados. Se activan automáticamente según el contexto o mediante invocación explícita.
:::

---

<style>
.skills-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin: 1.5rem 0;
}

@media (max-width: 768px) {
  .skills-grid {
    grid-template-columns: 1fr;
  }
}

.skills-grid > div {
  margin: 0;
}
</style>

## Inicio Rápido

::: tip Encuentra tu Skill
Selecciona tu situación para ver las skills recomendadas
:::

<div class="skills-grid">

<div>

### Implementación
::: details Voy a implementar una feature
- <Badge type="tip" text="Testing" /> `test-driven-development` - TDD obligatorio: test → fail → implement → pass
- <Badge type="info" text="Design" /> `brainstorming` - Refina idea antes de codear con preguntas iterativas
:::

</div>

<div>

### Debugging
::: details Tengo un bug o test fallando
- <Badge type="danger" text="Debug" /> `systematic-debugging` - Framework 4 fases: root cause primero, luego fix
- <Badge type="danger" text="Debug" /> `root-cause-tracing` - Trace backward por call stack al trigger original
- <Badge type="warning" text="Quality" /> `verification-before-completion` - Verifica con comando ANTES de declarar "fixed"
- <Badge type="warning" text="Security" /> `defense-in-depth` - Valida en cada layer para hacer bugs imposibles
:::

</div>

<div>

### Planificación
::: details Necesito planificar implementación compleja
- <Badge type="info" text="Design" /> `brainstorming` - Explora 2-3 alternativas con trade-offs
- <Badge type="info" text="Collab" /> `writing-plans` - Plan detallado ejecutable con rutas exactas
- <Badge type="info" text="Collab" /> `executing-plans` - Ejecuta plan existente en batches con reviews
:::

</div>

<div>

### Code Review
::: details Listo para review o recibí feedback
- <Badge type="tip" text="Quality" /> `requesting-code-review` - Dispara subagent code-reviewer
- <Badge type="tip" text="Quality" /> `receiving-code-review` - Procesa feedback con rigor técnico
:::

</div>

<div>

### Testing Avanzado
::: details Tests tienen timing issues, mocks incorrectos, o necesitas probar webapps/mobile
- <Badge type="tip" text="Testing" /> `condition-based-waiting` - Reemplaza timeouts con polling de condiciones
- <Badge type="warning" text="Testing" /> `testing-anti-patterns` - Evita testear mocks, test-only methods
- <Badge type="tip" text="Testing" /> `webapp-testing` - Playwright toolkit con server lifecycle management
- <Badge type="tip" text="Mobile" /> `mobile-testing` - Dual-stack mobile-mcp + Maestro para iOS/Android E2E testing
:::

</div>

<div>

### Workflow Git
::: details Necesito aislamiento, PR con quality gate, o branch management
- <Badge type="tip" text="Git" /> `git-pullrequest` - PR con quality gate: code review + observaciones + auto fix loop
- <Badge type="info" text="Git" /> `using-git-worktrees` - Workspace aislado sin switch de branch
- <Badge type="info" text="Git" /> `finishing-a-development-branch` - Integración limpia: merge/PR/cleanup
:::

</div>

<div>

### Herramientas
::: details Crear componentes o automatización
- <Badge type="tip" text="Dev Tools" /> `claude-code-expert` - Genera agents/commands/hooks production-ready
- <Badge type="info" text="Web" /> `web-browser` - Control Chrome/Chromium vía CDP para exploración web interactiva
- <Badge type="tip" text="Meta" /> `skill-creator` - Crea skill personalizada paso a paso
:::

</div>

<div>

### Design
::: details Interfaces frontend distintivas y de alta calidad
- <Badge type="tip" text="Design" /> `frontend-design` - Interfaces production-grade con dirección estética bold (anti-AI slop)
:::

</div>

<div>

### Parallelization
::: details Múltiples tareas independientes o failures no relacionadas
- <Badge type="info" text="Collab" /> `dispatching-parallel-agents` - Múltiples subagents concurrentes
- <Badge type="info" text="Collab" /> `subagent-driven-development` - Subagent por task + review entre tasks
:::

</div>

<div>

### Writing
::: details Documentación, commits, mensajes de error, o prosa técnica
- <Badge type="tip" text="Writing" /> `writing-clearly-and-concisely` - Reglas de Strunk para escritura clara y profesional
:::

</div>

</div>

---

## Skills por Categoría

| Categoría | Skills | Uso Recomendado |
|-----------|--------|-----------------|
| [Testing](#testing) | 5 | TDD, flaky tests, anti-patterns, webapp/mobile E2E |
| [Debugging](#debugging) | 4 | Debugging sistemático, root cause, verificación, defense-in-depth |
| [Collaboration](#collaboration) | 9 | Brainstorming, plans, reviews, git workflows, parallel agents |
| [Development Tools](#development-tools) | 3 | Claude Code components, browser automation, skill creation |
| [Design](#design) | 1 | Interfaces frontend distintivas (anti-AI slop) |
| [Writing](#writing) | 1 | Prosa clara y concisa (Strunk's Elements of Style) |
| [Meta](#meta) | 3 | Superpowers enforcement, skill contribution, testing skills |

---

### Testing

#### test-driven-development

::: tip Testing | Mandatory
**Cuándo**: Al implementar cualquier feature, bugfix o refactor
**Qué hace**: Garantiza que tests verifican comportamiento real escribiendo test primero, viéndolo fallar (RED), luego implementando código mínimo para pasar (GREEN), y refactorizando (REFACTOR)
:::

**Ejemplo**:
```bash
"Implementa validación de email en formulario"
# 1. Escribe test de validación
# 2. Ejecuta test (debe fallar = RED)
# 3. Implementa validación mínima
# 4. Test pasa (GREEN)
# 5. Refactoriza si necesario
```

**Principio**: Si no viste el test fallar, no sabes si testea lo correcto

**Workflow**: RED (test falla) → GREEN (test pasa) → REFACTOR (mejora código)

---

#### condition-based-waiting

::: tip Testing | Advanced
**Cuándo**: Tests tienen race conditions, timing dependencies o comportamiento flaky (pasan a veces, fallan bajo carga)
**Qué hace**: Reemplaza timeouts arbitrarios (`setTimeout`, `sleep`) con polling de condiciones reales, esperando cambios de estado específicos
:::

**Ejemplo**:
```typescript
// ❌ Antes: Guess timing
await new Promise(r => setTimeout(r, 2000));

// ✅ Después: Wait for condition
await waitFor(() => element.isVisible());
```

**Elimina**: Flaky tests causados por timing guessing
**Usa**: Polling de condición real que importa

---

#### testing-anti-patterns

::: warning Testing | Preventive
**Cuándo**: Antes de agregar mocks, crear métodos test-only en producción, o testear implementación vs comportamiento
**Qué hace**: Previene errores comunes: testear mocks en vez de comportamiento real, contaminar código producción con lógica test-only, mockear sin entender dependencias
:::

**Leyes de hierro**:
1. NUNCA testear comportamiento de mocks
2. NUNCA agregar métodos test-only a clases producción
3. NUNCA mockear sin entender dependencias

**Ejemplo**:
```typescript
// ❌ Testea que mock existe
expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();

// ✅ Testea comportamiento real o no mockees
expect(screen.getByRole('navigation')).toBeInTheDocument();
```

**Principio**: Si no puedes testear sin mock, el diseño está mal

---

#### webapp-testing

::: tip Testing | E2E
**Cuándo**: Testear aplicaciones web locales, verificar funcionalidad frontend, debugging UI, o capturar screenshots del browser
**Qué hace**: Provee toolkit Playwright con server lifecycle management. Scripts helper para manejar servidores (start/stop automático)
:::

**Decision Tree**:
```
¿Es HTML estático?
├─ Sí → Lee HTML directo para identificar selectores → Playwright script
└─ No (webapp dinámica) → ¿Server ya corriendo?
    ├─ No → python scripts/with_server.py --help
    └─ Sí → Reconnaissance-then-action:
        1. Navigate + wait for networkidle
        2. Screenshot o inspect DOM
        3. Identify selectors
        4. Execute actions
```

**Helper Scripts**:
- `scripts/with_server.py` - Maneja lifecycle de servidores (soporta múltiples)

**Ejemplo**:
```bash
# Single server
python scripts/with_server.py --server "npm run dev" --port 5173 -- python test.py

# Multiple servers
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python test.py
```

**Best Practices**:
- Siempre `page.wait_for_load_state('networkidle')` antes de inspeccionar DOM
- Usar scripts como black boxes (--help primero)
- Cerrar browser al terminar

---

#### mobile-testing

::: tip Testing | Mobile E2E
**Cuándo**: Testing de apps móviles (React Native, Expo, Flutter, native), debugging UI en simuladores/emuladores, o generación de test suites E2E mobile
**Qué hace**: Provee integración dual-stack con mobile-mcp (debugging interactivo) y Maestro (test suites E2E con YAML flows y AI assertions)
:::

**Dual-Stack Approach**:
- **mobile-mcp**: Screenshots, accessibility tree, interacción directa con simuladores/emuladores
- **Maestro**: YAML flows declarativos, auto-healing, assertions AI (`assertWithAI`, `assertNoDefectsWithAI`)

**Prerequisites**:
```bash
node --version    # v22+
java --version    # 17+
maestro --version # Latest
```

**Decision Tree**:
```
¿Tipo de testing?
├─ Debugging → mobile-mcp tools directamente
│   1. mobile_list_available_devices
│   2. mobile_launch_app(appId)
│   3. mobile_take_screenshot
│   4. mobile_list_elements_on_screen
│
├─ E2E Test Generation → Explorar con mobile-mcp, generar Maestro YAML
│   1. Explorar visualmente
│   2. Generar flows/[feature]/[scenario].yaml
│   3. Validar: maestro test flows/
│
└─ Expo/React Native → Ver references/expo-react-native.md
```

**Ejemplo Maestro Flow**:
```yaml
appId: com.myapp
---
- launchApp:
    clearState: true
- tapOn:
    id: "login-button"
- inputText: "user@example.com"
- extendedWaitUntil:
    visible:
      id: "home-screen"
    timeout: 10000
```

**Expo Critical**: Usar Development Builds, NO Expo Go. Usar `openLink` para deep links:
```yaml
- openLink: "exp+com.myapp://expo-development-client/?url=http://10.0.2.2:8081"
```

**References** (progressive disclosure):
- `references/maestro-patterns.md` - Sintaxis YAML completa
- `references/mobile-mcp-tools.md` - Tools de debugging
- `references/expo-react-native.md` - Guía específica Expo/RN

---

### Debugging

#### systematic-debugging

::: danger Debug | Mandatory
**Cuándo**: Ante cualquier bug, test fallando, comportamiento inesperado o problema de performance
**Qué hace**: Framework 4 fases (root cause investigation, pattern analysis, hypothesis testing, implementation) que garantiza entender problema antes de intentar fix
:::

**Ley de hierro**: NO FIXES SIN ROOT CAUSE INVESTIGATION PRIMERO

**Fases**:
1. **Root Cause**: Identifica causa inmediata con evidencia
2. **Pattern Analysis**: ¿Ocurre siempre? ¿Solo en CI? ¿Bajo qué condiciones?
3. **Hypothesis Testing**: Propón teorías, prueba sistemáticamente
4. **Implementation**: Fix verificado que elimina root cause

**Ejemplo**:
```bash
"Test falla con 'undefined property'"
# Fase 1: ¿Qué línea? ¿Qué objeto? ¿Cuándo se ejecuta?
# Fase 2: ¿Siempre falla? ¿Solo en paralelo?
# Fase 3: ¿Timing? ¿Estado compartido? ¿Init faltante?
# Fase 4: Fix en origen con test que previene regresión
```

---

#### root-cause-tracing

::: danger Debug | Investigation
**Cuándo**: Error ocurre profundo en ejecución y necesitas trace back al trigger original
**Qué hace**: Trace sistemático hacia atrás por call stack, agregando instrumentación cuando necesario, para identificar fuente de data inválida o comportamiento incorrecto
:::

**Workflow**: Error profundo → Instrumentar layers → Trace backward → Fix origen

**Ejemplo**:
```bash
"Error en DB layer: invalid UUID format"
# → Add logging: ¿de dónde viene UUID?
# → Trace back: controller → service → handler
# → Identifica: input no validado en controller
# → Fix en origen, no en DB layer (sintoma)
```

**Principio**: Fix síntoma = bug vuelve. Fix origen = bug imposible

**Combinar con**: `defense-in-depth` para validar en cada layer

---

#### verification-before-completion

::: warning Quality | Mandatory
**Cuándo**: Antes de declarar work complete, bug fixed, tests passing, o crear commit/PR
**Qué hace**: Requiere ejecutar comando de verificación y confirmar output ANTES de hacer cualquier claim de éxito. Evidencia antes de afirmaciones, siempre
:::

**Ley de hierro**: NO COMPLETION CLAIMS SIN FRESH VERIFICATION EVIDENCE

**Gate function**:
1. **IDENTIFY**: ¿Qué comando prueba este claim?
2. **RUN**: Ejecuta comando COMPLETO (fresh, not cached)
3. **READ**: Full output, exit code, count failures
4. **VERIFY**: ¿Output confirma el claim?
5. **ONLY THEN**: Haz el claim

**Ejemplo**:
```bash
# ❌ "Tests should pass now"
# ✅ "Tests pass (output: 24 passed, 0 failed)"

# ❌ "Bug is fixed" (code changed)
# ✅ "Bug fixed (test now passes: [show output])"
```

**Principio**: Claims sin evidencia = dishonesty, not efficiency

---

#### defense-in-depth

::: warning Security | Structural
**Cuándo**: Invalid data causa failures profundos, requiere validación en múltiples system layers
**Qué hace**: Valida en CADA layer por donde pasa data para hacer bugs estructuralmente imposibles (no solo "fixed")
:::

**4 Layers**:
1. **Entry Point**: Rechaza input obviamente inválido en API boundary
2. **Business Logic**: Data tiene sentido para esta operación
3. **Environment Guards**: Previene context-specific dangers
4. **Debug Logging**: Ayuda cuando otros layers fallan

**Ejemplo**:
```typescript
// Layer 1: Entry validation
if (!workingDirectory || workingDirectory.trim() === '') {
  throw new Error('workingDirectory cannot be empty');
}

// Layer 2: Business logic
if (!existsSync(workingDirectory)) {
  throw new Error(`workingDirectory does not exist`);
}

// Layer 3: Environment guard
if (process.env.CI && !isAbsolutePath(workingDirectory)) {
  throw new Error('CI requires absolute paths');
}
```

**Principio**: Single validation = "fixed bug". Multiple layers = "bug impossible"

---

### Collaboration

#### brainstorming

::: info Design | Foundation
**Cuándo**: Antes de implementar, cuando idea es rough o necesitas explorar alternativas antes de codear
**Qué hace**: Transforma ideas vagas en diseños completos mediante preguntas iterativas (una a la vez), exploración de 2-3 alternativas con trade-offs, validación incremental por secciones
:::

**Proceso**:
1. **Understand**: Preguntas one-at-a-time (prefer multiple choice)
2. **Explore**: 2-3 approaches con trade-offs + recomendación razonada
3. **Present**: Diseño en secciones 200-300 palabras, valida cada una
4. **Document**: Guarda en `docs/plans/YYYY-MM-DD-topic-design.md`

**Ejemplo**:
```bash
"Necesito sistema de notificaciones"
# → ¿Real-time vs batch? ¿Push vs pull?
# → Propone 3 enfoques con ROI
# → Presenta diseño incremental
# → Genera design doc
```

**Principios**: One question at a time, YAGNI ruthlessly, incremental validation

---

#### writing-plans

::: info Collab | Implementation
**Cuándo**: Diseño completo, necesitas plan detallado ejecutable por AI/engineer con cero contexto del codebase
**Qué hace**: Crea plan exhaustivo con rutas exactas de archivos, ejemplos completos de código, pasos de verificación, asumiendo ingeniero sin conocimiento del dominio
:::

**Granularidad**: Cada step = 1 acción (2-5 minutos)
- "Write failing test" = step
- "Run test to verify failure" = step
- "Implement minimal code" = step
- "Commit" = step

**Ejemplo**:
```markdown
### Task 1: Auth Middleware

1. Create `src/middleware/auth.ts`
2. Write test in `src/middleware/auth.test.ts`:
   [código completo, no pseudocódigo]
3. Run `npm test` (should fail)
4. Implement middleware: [código exacto]
5. Run `npm test` (should pass)
6. Commit: "Add auth middleware"
```

**Output**: `docs/plans/YYYY-MM-DD-feature.md` con header mandatorio + tasks bite-sized

**Principios**: DRY, YAGNI, TDD, frequent commits, assume zero context

---

#### executing-plans

::: info Collab | Execution
**Cuándo**: Tienes plan completo de implementación y necesitas ejecución controlada en batches con review checkpoints
**Qué hace**: Carga plan, revisa críticamente, ejecuta tareas en batches (default: 3), reporta para review entre batches, continua basado en feedback
:::

**Proceso**:
1. **Load & Review**: Lee plan, identifica concerns, crea TodoWrite
2. **Execute Batch**: Primeras 3 tasks (mark in_progress → implement → mark completed)
3. **Report**: Muestra implementación + verification output + "Ready for feedback"
4. **Continue**: Aplica changes si needed → next batch → repeat
5. **Complete**: Usa `finishing-a-development-branch` al final

**Ejemplo**:
```bash
"Ejecuta plan en docs/plans/2025-11-12-auth.md"
# → Load + review críticamente
# → Batch 1: Tasks 1-3
# → Report + checkpoint
# → Batch 2: Tasks 4-6
# → Pattern continues
```

**Principio**: Batch execution con checkpoints para architect review

---

#### requesting-code-review

::: tip Quality | Proactive
**Cuándo**: Al completar task (subagent-driven dev), implementar major feature, o antes de merge
**Qué hace**: Dispara subagent `code-reviewer` especializado que valida implementación contra plan/requirements antes de proceder
:::

**Workflow**:
1. Get git SHAs: `BASE_SHA=$(git rev-parse origin/main)`, `HEAD_SHA=$(git rev-parse HEAD)`
2. Dispatch `ai-framework/code-reviewer` subagent
3. Fill template: `{DESCRIPTION}`, `{PLAN_REFERENCE}`, `{BASE_SHA}`, `{HEAD_SHA}`
4. Act on feedback: Critical → immediate fix, Important → before proceeding, Minor → note for later

**Ejemplo**:
```bash
"Feature auth completa, revisar antes de merge"
# → code-reviewer analiza diff vs requirements
# → Reporta: security issues, performance, tests coverage
# → Aprueba o solicita changes con reasoning
```

**Mandatory**: After each task in subagent-driven dev, after major features, before merge

---

#### receiving-code-review

::: tip Quality | Response
**Cuándo**: Recibes feedback de code review, especialmente si parece unclear o técnicamente cuestionable
**Qué hace**: Requiere rigor técnico y verificación, NO acuerdo performativo ni implementación ciega. Valida feedback, cuestiona si necesario, implementa correctamente
:::

**Response pattern**:
1. **READ**: Complete feedback sin reaccionar
2. **UNDERSTAND**: Restate requirement in own words (or ask)
3. **VERIFY**: Check contra codebase reality
4. **EVALUATE**: ¿Técnicamente sound para ESTE codebase?
5. **RESPOND**: Technical acknowledgment o reasoned pushback
6. **IMPLEMENT**: One item at a time, test each

**Forbidden**: "You're absolutely right!", "Great point!", "Let me implement that now" (antes de verificar)

**Ejemplo**:
```bash
Reviewer: "Change singleton pattern"
# → ¿Por qué? ¿Evidencia de problema?
# → ¿Mejora real o preferencia personal?
# → Si válido: implement
# → Si cuestionable: discuss alternatives con reasoning
```

**Principio**: Technical correctness > social comfort

---

#### using-git-worktrees

::: info Git | Isolation
**Cuándo**: Feature necesita aislamiento de workspace actual o antes de ejecutar implementation plans
**Qué hace**: Crea worktrees aislados con smart directory selection (check existing, CLAUDE.md, o ask user) y safety verification
:::

**Directory priority**:
1. Check `.worktrees/` (preferred) o `worktrees/`
2. Check CLAUDE.md preference
3. Ask user: `.worktrees/` (local) vs `~/.config/superpowers/worktrees/<project>/` (global)

**Ejemplo**:
```bash
"Crear worktree para feature auth"
# → Crea ../ai-framework-auth/
# → Checkout branch feature/auth
# → Workspace aislado del main
# → Trabajo paralelo sin switch
```

**Uso típico**: Features grandes, múltiples branches simultáneos, executing-plans workflow

---

#### finishing-a-development-branch

::: info Git | Integration
**Cuándo**: Implementación completa, tests pasan, necesitas decidir cómo integrar el work
**Qué hace**: Guía completion verificando tests primero, luego presentando opciones estructuradas para merge, PR, o cleanup
:::

**Workflow**:
1. **Verify Tests**: Run test suite, STOP si fallan
2. **Determine Base**: Identifica base branch (main/master)
3. **Present Options**:
   - **A**: Direct merge (si trivial, solo tú trabajando)
   - **B**: Create PR (si requiere team review)
   - **C**: Cleanup branch (si trabajo descartado)
4. **Execute Choice**: Guía proceso seleccionado
5. **Clean Up**: Remove worktree, delete branch

**Ejemplo**:
```bash
"Feature completa, ¿qué sigue?"
# → Tests: 24 passed ✓
# → Options presented
# → User selects "Create PR"
# → Genera PR con summary + test plan
```

**Principio**: Verify tests → Present options → Execute choice → Clean up

---

#### git-pullrequest

::: tip Git | Quality Gate
**Cuándo**: Al crear PR, necesitas quality gate con code + security review y observaciones contextualizadas
**Qué hace**: Valida cambios, dispara code-reviewer + security-reviewer en paralelo, genera observaciones (tests, API, complexity, breaking), presenta findings consolidados de 3 capas, ofrece auto fix loop, crea PR con documentación quality
:::

**Corporate Format Support:**
```
Pattern: type|TASK-ID|YYYYMMDD|description
Example: feat|TRV-350|20251023|add user authentication
```

**Workflow**:
1. **Validación**: Target branch existe, extrae commits, detecta formato
2. **Quality Gate (3 capas en paralelo)**:
   - Code review (lógica, arquitectura, bugs)
   - Security review (SQL injection, secrets, XSS)
   - Observations (tests, API, breaking, complexity)
3. **User Decision**: Create PR / Auto fix / Cancel
4. **Auto Fix Loop** (opcional): Subagent arregla issues → re-review (ambos) → usuario decide de nuevo
5. **Create PR**: Protected branch detection + temp branch si necesario, genera body con findings, crea PR

**User Decisions:**
- **Create PR**: Push y crear PR con findings de code + security reviews documentados
- **Auto fix**: Subagent arregla Critical+Important (code) + High+Medium (security) issues → re-review obligatorio de ambos
- **Cancel**: Salir con summary actionable de issues pendientes

**Examples disponibles** (en `skills/git-pullrequest/examples/`):
- `success-no-findings.md` - Review limpio, directo a PR
- `success-with-findings.md` - Issues encontrados, usuario procede anyway
- `auto-fix-loop.md` - Loop de auto fix con re-review hasta éxito
- `manual-cancellation.md` - Usuario cancela para fix manual

**Ejemplo**:
```bash
"Crear PR a main con quality gate"
# → Analiza commits, detecta corporate format
# → Code review + observaciones
# → Usuario selecciona: Auto fix
# → Subagent arregla issues
# → Re-review (limpio)
# → Usuario selecciona: Create PR
# → PR creado con URL
```

**Principio**: Human always decides → Quality gate mandatory → Auto fix optional → Findings documented

---

#### dispatching-parallel-agents

::: info Collab | Concurrency
**Cuándo**: 3+ failures independientes sin shared state o dependencias que pueden investigarse sin contexto mutuo
**Qué hace**: Dispara múltiples subagents Claude concurrentemente para investigar y fixear problemas independientes en paralelo
:::

**Cuándo usar**:
- 3+ test files failing con diferentes root causes
- Múltiples subsystems broken independientemente
- Cada problema se entiende sin contexto de otros
- No shared state entre investigations

**Ejemplo**:
```bash
"3 tests fallan en módulos diferentes"
# → Agent 1: investiga + fix test auth
# → Agent 2: investiga + fix test payments
# → Agent 3: investiga + fix test notifications
# → Parallel execution, consolidated summary
```

**Don't use**: Si failures relacionados (fix uno → fix otros), need full system state, agents interferirían

---

#### subagent-driven-development

::: info Collab | Fast Iteration
**Cuándo**: Ejecutar implementation plan con tareas independientes en la sesión actual (no requiere parallel session como executing-plans)
**Qué hace**: Dispara subagent fresh por cada tarea con code review entre tasks, enabling fast iteration con quality gates en cada step
:::

**vs executing-plans**: Misma sesión (no context switch), fresh subagent per task (no context pollution), code review automático after each, faster iteration

**Proceso**:
1. **Load Plan**: Create TodoWrite con todas las tasks
2. **Execute Task**: Dispatch fresh general-purpose subagent
3. **Review**: Use `requesting-code-review` skill
4. **Next Task**: Repeat hasta completion

**Ejemplo**:
```bash
Plan con 5 tareas independientes:
# → Subagent Task 1 → Review → Merge
# → Subagent Task 2 → Review → Merge
# → Fresh context cada task
# → Quality gate en cada step
```

**Ventaja**: Fresh context per task (no context rot), continuous progress con quality gates

---

### Development Tools

#### claude-code-expert

::: tip Dev Tools | Production
**Cuándo**: Crear/modificar/update/fix agents, slash commands, hooks, o MCP integrations para Claude Code
**Qué hace**: Genera componentes Claude Code production-ready con 6 quality gates automáticos (syntax, security, logic, constitutional, integration, production). WebFetch docs oficiales para syntax actual
:::

**Workflow**:
1. **Identify Component**: Agent, slash command, hook, o MCP server
2. **WebFetch Docs**: Official Claude Code docs para EXACT current syntax (training stale)
3. **Analyze Patterns**: Lee project conventions
4. **Generate**: Component con validación
5. **6 Quality Gates**: Syntax, security, logic, constitutional, integration, production

**Ejemplo**:
```bash
"Crea agent para optimización PostgreSQL"
# → WebFetch Claude Code agent docs
# → Analiza agents/ patterns
# → Genera agent con tools, workflow, examples
# → 6 quality gates automáticos
```

**Output**: `.claude/agents/*.md`, `commands/*.md`, `hooks/*.py`, o `.claude/.mcp.json` update

**Critical**: Training data stale, SIEMPRE WebFetch docs oficiales primero

---

#### web-browser

::: info Web | Automation
**Cuándo**: Interacción colaborativa con sitios web (clicks, formularios, navegación)
**Qué hace**: Control minimalista Chrome/Chromium vía CDP (Chrome DevTools Protocol), herramientas para exploración web interactiva
:::

**Platform**: Multiplataforma (Chrome/Chromium)

**Setup** (una vez):
```bash
cd skills/web-browser/tools
npm install
ls node_modules/puppeteer-core  # Verify
```

**Tools**: `start.js`, `nav.js`, `eval.js`, `screenshot.js`, `pick.js`

**Ejemplo**:
```bash
"Explorar documentación de API"
# → Start Chrome debugging (port 9222)
# → Navigate → interact → screenshot
# → Extract information con eval.js
# → Cerrar Chrome manualmente cuando termines
```

**Critical Note**: Esta skill NO incluye `stop.js`. Cierra Chrome manualmente o usa `lsof -ti :9222 | xargs kill -9`

---

#### skill-creator

::: tip Meta | Creation
**Cuándo**: Necesitas skill personalizada para dominio/framework/workflow específico no cubierto por skills existentes
**Qué hace**: Proceso guiado 6 pasos (validación, recursos, estructura, edición, validación, empaquetado) para crear skills siguiendo best practices
:::

**6 Pasos**:
1. **Validación**: ¿Existe skill similar? ¿Problema claro? ¿Aplica broadly?
2. **Recursos**: Scripts, docs, referencias, assets necesarios
3. **Estructura**: `python scripts/init_skill.py skill-name`
4. **Edición**: SKILL.md (frontmatter + instructions) + bundled resources
5. **Validación**: `python scripts/validate_skill.py skill-name`
6. **Empaquetado**: `python scripts/package_skill.py skill-name`

**Ejemplo**:
```bash
"Crea skill para desarrollo Astro.js"
# → Valida: no existe Astro skill
# → Recursos: Astro docs, common patterns
# → Estructura: skills/astro-dev/SKILL.md
# → Edición: frontmatter + workflows + examples
# → Validación: structure OK
# → Package: ready for distribution
```

**Output**: `skills/skill-name/` con SKILL.md + scripts/ + references/ + assets/

---

### Design

#### frontend-design

::: tip Design | Production
**Cuándo**: Construir componentes web, páginas, o aplicaciones que requieren diseño distintivo y memorable
**Qué hace**: Crea interfaces frontend production-grade con dirección estética bold que evita la estética genérica "AI slop". Implementa código funcional con atención excepcional a detalles estéticos
:::

**Design Thinking** (antes de codear):
1. **Purpose**: ¿Qué problema resuelve? ¿Quién lo usa?
2. **Tone**: Elegir dirección extrema: brutalmente minimal, maximalist chaos, retro-futuristic, luxury/refined, editorial/magazine, brutalist/raw, art deco, etc.
3. **Constraints**: Framework, performance, accessibility
4. **Differentiation**: ¿Qué lo hace INOLVIDABLE?

**Focus Areas**:
- **Typography**: Fonts distintivas, NO genéricas (evitar Arial, Inter, Roboto). Pair display font + refined body font
- **Color & Theme**: Paleta cohesiva con CSS variables. Colores dominantes con acentos sharp > paletas tímidas
- **Motion**: CSS-only preferido. Staggered reveals con animation-delay > micro-interactions dispersas
- **Spatial Composition**: Layouts inesperados, asimetría, overlap, grid-breaking, negative space generoso
- **Backgrounds**: Gradient meshes, noise textures, geometric patterns, layered transparencies, grain overlays

**NEVER use**:
- Fonts genéricas: Inter, Roboto, Arial, system fonts
- Color schemes cliché: purple gradients on white
- Layouts predecibles y cookie-cutter
- Mismo estilo entre generaciones (variar light/dark, fonts, aesthetics)

**Ejemplo**:
```bash
"Crea landing page para startup fintech"
# → Design Thinking: luxury/refined tone, professional audience
# → Typography: distinctive serif headers + clean sans body
# → Color: deep navy + gold accents (not purple gradient)
# → Motion: staggered reveal on scroll, hover micro-interactions
# → Output: Production-ready React/HTML with memorable aesthetic
```

**Principio**: Match implementation complexity to aesthetic vision. Maximalist = elaborate code. Minimalist = restraint + precision + careful spacing.

---

### Writing

#### writing-clearly-and-concisely

::: tip Writing | Communication
**Cuándo**: Escribir prosa para humanos: documentación, commits, mensajes de error, explicaciones, reportes, UI text
**Qué hace**: Aplica las reglas atemporales de Strunk (*The Elements of Style*) para escritura más clara, fuerte y profesional
:::

**Cuándo usar**:
- Documentation, README, technical explanations
- Commit messages, PR descriptions
- Error messages, UI copy, help text
- Reports, summaries, cualquier explicación

**Reglas Core (Principles of Composition)**:
- **Use active voice** (Rule 10)
- **Put statements in positive form** (Rule 11)
- **Use definite, specific, concrete language** (Rule 12)
- **Omit needless words** (Rule 13)
- **Keep related words together** (Rule 16)
- **Place emphatic words at end of sentence** (Rule 18)

**Limited Context Strategy**:
1. Escribe tu draft usando judgment
2. Dispatch subagent con draft + `elements-of-style.md`
3. Subagent copyedita y retorna revisión

**Ejemplo**:
```bash
# Antes (pasivo, vago)
"The file was processed by the system"

# Después (activo, concreto)
"The parser extracted 42 records from config.yaml"
```

**Principio**: Si escribes oraciones para humanos, usa esta skill

---

### Meta

#### using-superpowers

::: danger Meta | Mandatory
**Cuándo**: Automáticamente al inicio de CADA conversación vía SessionStart hook (superpowers-loader.sh)
**Qué hace**: Establece workflows mandatorios: buscar/usar skills antes de ANY task, usar Skill tool antes de anunciar skill, brainstorming antes de coding, TodoWrite para checklists
:::

**Mandatory First Response Protocol**:
1. ☐ List available skills in mind
2. ☐ Ask: "Does ANY skill match this request?"
3. ☐ If yes → Use Skill tool to read skill file
4. ☐ Announce which skill using
5. ☐ Follow skill exactly

**Common Rationalizations = FAILURE**:
- "This is just a simple question" → WRONG
- "I can check files quickly" → WRONG
- "Let me gather info first" → WRONG
- "Skill is overkill" → WRONG
- "I remember this skill" → WRONG (skills evolve)

**Enforcement**: Skills > MCPs > Direct implementation. Si skill existe para task, MUST use or fail

**Cargado**: Automáticamente en SessionStart, no requiere invocación manual

---

#### sharing-skills

::: info Meta | Contribution
**Cuándo**: Desarrollaste skill broadly useful (no project-specific) y quieres contribuirla upstream vía pull request
**Qué hace**: Guía proceso completo: branching, edit/create skill, commit, push fork, create PR para contribuir al repositorio upstream
:::

**Prerequisite**: Skill debe estar tested usando `testing-skills-with-subagents` TDD process

**Workflow**:
1. **Sync**: `git checkout main && git pull upstream main`
2. **Branch**: `git checkout -b add-skillname-skill`
3. **Edit/Create**: Skill en `skills/skill-name/SKILL.md`
4. **Commit**: Mensaje descriptivo
5. **Push**: `git push origin add-skillname-skill`
6. **PR**: `gh pr create` con template

**Share when**: Broad applicability, well-tested, documented, follows guidelines

**Keep personal**: Project-specific, experimental, sensitive info, too niche

---

#### testing-skills-with-subagents

::: warning Meta | Quality
**Cuándo**: Crear/editar skill, antes de deployment, para verificar funciona bajo presión y resiste rationalization
**Qué hace**: Aplica RED-GREEN-REFACTOR cycle a process documentation. Baseline sin skill (watch fail), write skill addressing failures, iterate cerrando loopholes
:::

**TDD Mapping**:
- **RED**: Run scenario SIN skill → watch agent fail → capture exact failures
- **GREEN**: Write skill addressing baseline failures → verify compliance
- **REFACTOR**: Find new rationalizations → add counters → re-verify

**Ejemplo**:
```bash
"Validar skill TDD recién creada"
# RED: Subagent sin TDD skill → salta tests, va directo a implement
# GREEN: Con TDD skill → escribe test first, watch fail, implement
# REFACTOR: Encuentra loopholes ("just this once") → strengthen skill
```

**Test skills que**:
- Enforce discipline (TDD, testing requirements)
- Tienen compliance cost (time, effort, rework)
- Podrían ser racionalizadas ("skip just this once")
- Contradict immediate goals (speed over quality)

**Principio**: Si no viste agent fail sin skill, no sabes si skill previene right failures

---

## Cómo Usar Skills

**Activación automática**: Claude detecta contexto y carga skill apropiada sin invocación explícita.

```bash
# Solicitud natural
"Voy a implementar validación de formulario"
# → test-driven-development se activa automáticamente
```

**Invocación manual** (opcional):
```bash
"Usando systematic-debugging: investiga por qué el test falla aleatoriamente"
```

::: tip Precedencia
**Skills > MCPs > Implementación directa**

Siempre verifica skills disponibles antes de implementar. Si skill existe para tu task, MUST use.
:::

**Crear nueva skill**:
```bash
"Crea skill para [dominio específico]"
# → skill-creator guía el proceso interactivamente
```

---

## Solución de Problemas

::: details Skill no se activa automáticamente

**Causa común**: Solicitud demasiado genérica

```bash
❌ "Ayuda con código"
✅ "Implementa autenticación JWT siguiendo TDD"
```

**Solución**: Menciona skill explícitamente si sospechas de activación:
```bash
"Usando test-driven-development: implementa validación email"
```
:::

::: details Output no cumple expectativas

**Para claude-code-expert**: Docs oficiales pueden estar desactualizadas

```bash
"WebFetch latest Claude Code documentation antes de generar agent"
```

**Para cualquier skill**: Valida recursos existen

```bash
ls -la skills/skill-name/
# Verifica SKILL.md + scripts/ + references/ + assets/
```
:::

::: details Skill falta o versión antigua

**Update framework**:

```bash
# Si instalado vía marketplace
# Session restart carga nueva versión automáticamente

# Si clon local
cd /path/to/ai-framework
git pull origin main
# Session restart
```

**Verificar versión**:
```bash
cat package.json | grep version
```
:::

---

::: info Metadata
**Última actualización**: 2025-12-07
**Categorías**: Testing, Debugging, Collaboration, Development Tools, Design, Writing, Meta
**Status**: Production-Ready
:::
