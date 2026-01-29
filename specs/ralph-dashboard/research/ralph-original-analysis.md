# Analysis: mikeyobrien/ralph-orchestrator

## Executive Summary

Ralph Orchestrator es una implementacion avanzada de la "Ralph Wiggum technique" para orquestacion autonoma de agentes AI. El repositorio muestra patrones maduros para ejecucion autonoma que resuelven directamente el problema de bloqueo por `AskUserQuestion`.

**Hallazgo Clave**: Ralph NO pregunta al usuario durante ejecucion autonoma. En su lugar usa:
1. **Eventos `build.blocked`** para dependencias faltantes
2. **Backpressure** en lugar de instrucciones paso a paso
3. **Auto-recuperacion** a traves de re-planificacion automatica

---

## 1. Estructura del Repositorio Original

```
mikeyobrien/ralph-orchestrator/
├── AGENTS.md              # (Legacy - ahora guia para agentes en docs/)
├── CLAUDE.md              # Instrucciones para Claude trabajando en el repo
├── PROMPT.md              # Prompt por defecto para tareas
├── ralph.yml              # Configuracion principal
├── presets/               # 31 presets predefinidos
│   ├── code-assist.yml    # Implementacion TDD adaptativa
│   ├── pdd-to-code-assist.yml  # Full PDD + implementacion
│   ├── tdd-red-green.yml  # TDD estricto
│   ├── spec-driven.yml    # Contract-first
│   ├── bugfix.yml         # Metodo cientifico para bugs
│   ├── debug.yml          # Investigacion sistematica
│   └── minimal/           # Configuraciones minimas por backend
├── prompts/               # Prompts especializados
├── docs/                  # Documentacion completa
│   ├── concepts/          # Tenets, backpressure, coordination
│   ├── guide/             # Agents, prompts, configuration
│   └── advanced/          # Production, parallel loops
├── crates/                # Codigo Rust
│   ├── ralph-core/        # Logica de orquestacion
│   ├── ralph-cli/         # Comandos CLI
│   └── ralph-adapters/    # Claude, Kiro, Gemini, etc.
├── backend/               # Web server (Fastify + tRPC)
└── frontend/              # Dashboard (React + Vite)
```

### Diferencias con Nuestra Implementacion

| Aspecto | Ralph Original | Nuestra Implementacion |
|---------|----------------|------------------------|
| **Prompts** | Un PROMPT.md + hat instructions | Skills separados (sop-*) |
| **Eventos** | JSONL pub/sub (build.blocked) | Archivos JSON directos |
| **Dependencias** | Re-planifica automaticamente | Pregunta al usuario |
| **Workers** | Hats internos del mismo proceso | Sub-agentes Task() |

---

## 2. Manejo de Dependencias Faltantes

### Patron Original: `build.blocked`

Cuando un builder encuentra una dependencia faltante, **NO pregunta**. En su lugar emite un evento que rutea de vuelta al planner:

```json
// Evento emitido por builder
{"topic": "build.blocked", "payload": {"reason": "Missing dependency", "task": "Implement feature X"}}

// Planner recibe y crea nueva tarea
{"topic": "build.task", "payload": "Add missing dependency to Cargo.toml"}
```

### Flujo de Recuperacion

```
Builder detecta: "Rust no esta instalado"
    │
    ▼
Emite: build.blocked
    │
    ▼
Planner recibe evento
    │
    ▼
Crea tarea: "Install Rust via rustup"
    │
    ▼
Builder ejecuta nueva tarea
    │
    ▼
Continua con tarea original
```

### Instrucciones en Presets (code-assist.yml)

```yaml
builder:
  instructions: |
    ## BUILDER MODE - TDD Implementation Cycle
    ...
    ### If Triggered by validation.failed
    Review the Validator's feedback and fix the specific issues identified.

    ### Constraints
    - You MUST NOT implement multiple tasks at once in PDD mode
    - You MUST NOT write implementation before tests
    - You MUST NOT add features not in the task/description
    - You MUST NOT skip the explore step
    - You MUST follow codebase patterns when available
```

**Nota**: NO hay instruccion de "preguntar al usuario". Las constraints son absolutas.

---

## 3. Modo Autonomo: Patrones Anti-Bloqueo

### Principio Fundamental: "Backpressure Over Prescription"

> "Don't prescribe how; create gates that reject bad work."

En lugar de:
```
1. Primero, verifica si Rust esta instalado
2. Si no, pregunta al usuario si quiere instalarlo
3. Si si, instala...
```

Ralph usa:
```
Implementa la feature.
Evidence required: tests: pass, lint: pass, build: pass
```

### Los 6 Tenets Relevantes

1. **Fresh Context Is Reliability** - Cada iteracion empieza limpia
2. **Backpressure Over Prescription** - Gates, no scripts
3. **The Plan Is Disposable** - Regenera libremente
4. **Disk Is State, Git Is Memory** - Archivos son la verdad
5. **Steer With Signals, Not Scripts** - Agrega senales, no pasos
6. **Let Ralph Ralph** - Manos fuera

### Instrucciones Explicitas de NO Preguntar

En los presets, encontramos secciones `### DON'T` que especifican comportamientos prohibidos:

```yaml
# De bugfix.yml - Reproducer hat
### DON'T
- Don't attempt to fix the bug - that's the Fixer's job
- Don't skip writing a failing test
- Don't write a test that passes

# De spec-driven.yml - Implementer hat
### DON'T
- Don't add features not in the spec
- Don't creative interpretation
```

**Observacion Critica**: Nunca se menciona "don't ask user" porque **la arquitectura hace imposible preguntar**. Los agentes no tienen acceso a input interactivo - solo pueden emitir eventos.

---

## 4. Sistema de Hats (Equivalente a Workers)

### Arquitectura Hat-Based

```yaml
hats:
  planner:
    triggers: ["task.start", "build.done", "build.blocked"]
    publishes: ["build.task"]

  builder:
    triggers: ["build.task"]
    publishes: ["build.done", "build.blocked"]
```

### Flujo de Eventos

```
task.start
    │
    ▼
[Planner] ──build.task──▶ [Builder]
    ▲                          │
    │                          ▼
    └───build.blocked─────────┘
    │
    └───build.done────▶ [Validator] ──▶ LOOP_COMPLETE
```

### Comparacion con Nuestra Implementacion

| Ralph Original | Nuestra Implementacion | Diferencia |
|----------------|------------------------|------------|
| `ralph emit "build.blocked"` | `AskUserQuestion()` | Evento vs Pregunta |
| Planner re-planifica | Usuario responde | Autonomo vs Interactivo |
| Worker continua | Worker se bloquea | Flujo vs Bloqueo |

---

## 5. Recomendaciones para Nuestra Implementacion

### Cambio 1: Eliminar AskUserQuestion del Worker

**Antes (Problematico):**
```javascript
// En sop-code-assist
if (!isRustInstalled()) {
  AskUserQuestion({
    question: "Rust no esta instalado. Quieres que lo instale?"
  });
}
```

**Despues (Patron Ralph):**
```javascript
// En sop-code-assist
if (!isRustInstalled()) {
  await emitEvent("build.blocked", {
    reason: "missing_dependency",
    dependency: "rust",
    suggested_action: "Install via: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
  });
  return; // Salir para que planner re-planifique
}
```

### Cambio 2: Agregar Backpressure a Skills

Crear seccion en cada skill SOP:

```markdown
## Constraints (MUST follow)
- NEVER ask user questions during autonomous execution
- NEVER block waiting for user input
- If blocked, emit event and exit
- Planner will re-route

## When Blocked
1. Document blocker in memories
2. Emit build.blocked event
3. Exit cleanly
4. Let next iteration handle it
```

### Cambio 3: Orquestador Maneja Blockers

```javascript
// En ralph-orchestrator skill
async function handleWorkerResult(result) {
  if (result.event === "build.blocked") {
    const newTask = createRecoveryTask(result.payload);
    await addTaskToQueue(newTask);
    // Continuar con siguiente iteracion
  }
}
```

### Cambio 4: Preset de Autonomia

Crear configuracion explicita para modo AFK:

```yaml
# presets/afk-mode.yml
autonomous:
  strict: true
  on_missing_dependency: "create_install_task"
  on_ambiguity: "use_best_guess_and_document"
  on_error: "retry_with_alternative"

constraints:
  - "NEVER use AskUserQuestion"
  - "NEVER block for user input"
  - "Document all decisions in memories"
```

---

## 6. Patrones de Codigo Relevantes

### Evento build.blocked (de cassettes)

```json
// Entrada: builder encuentra problema
{"ts": 3000, "event": "bus.publish", "data": {
  "topic": "build.blocked",
  "payload": {"reason": "Missing dependency", "task": "Implement feature X"}
}}

// Salida: planner crea tarea de recuperacion
{"ts": 4000, "event": "bus.publish", "data": {
  "topic": "build.task",
  "payload": "Add missing dependency to Cargo.toml"
}}
```

### Hat Instructions Pattern

```yaml
instructions: |
  ## [HAT_NAME] MODE

  [Descripcion del rol]

  ### Process
  1. [Paso 1]
  2. [Paso 2]

  ### DON'T
  - [Comportamiento prohibido 1]
  - [Comportamiento prohibido 2]

  ### Event Format
  ```
  ralph emit "[event.topic]" "[payload]"
  ```
```

---

## 7. Archivos Clave para Estudiar

1. **`presets/code-assist.yml`** - Patron completo de implementacion TDD
2. **`docs/concepts/backpressure.md`** - Filosofia anti-bloqueo
3. **`docs/concepts/tenets.md`** - Los 6 principios fundamentales
4. **`cassettes/event-routing/er-004-build-blocked-routes-to-planner.jsonl`** - Ejemplo de flujo blocker
5. **`docs/guide/agents.md`** - Como configurar agentes

---

## 8. Conclusion

El problema de `AskUserQuestion` en modo autonomo no es un bug - es un **anti-patron arquitectonico**. Ralph Orchestrator resuelve esto mediante:

1. **Arquitectura event-driven** que hace imposible bloquear en preguntas
2. **Backpressure** que define criterios de exito, no pasos
3. **Auto-recuperacion** donde blockers se convierten en nuevas tareas
4. **Constraints explicitos** en cada hat/worker

**Accion Inmediata**: Modificar `sop-code-assist` para emitir eventos en lugar de preguntar, y agregar manejo de `build.blocked` en `ralph-orchestrator`.

---

*Analisis generado: 2026-01-29*
*Fuente: https://github.com/mikeyobrien/ralph-orchestrator*
