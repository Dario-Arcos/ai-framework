# Ralph Orchestrator - Analisis Exhaustivo

> **Fecha**: 2026-01-25
> **Repositorio**: https://github.com/mikeyobrien/ralph-orchestrator
> **Version**: v2.2.4 (ultima release)

---

## 1. Arquitectura ralph-orchestrator

### 1.1 Vision General

Ralph Orchestrator es una implementacion en **Rust** de la tecnica "Ralph Wiggum" para orquestacion autonoma de agentes AI. Su filosofia central es:

> "El orquestador es una capa de coordinacion delgada, no una plataforma. Los agentes son inteligentes; dejalos hacer el trabajo."

### 1.2 Estructura de Crates (Rust Workspace)

```
crates/
├── ralph-core/         # Logica central del orchestrator
│   └── src/
│       ├── config.rs           # Configuracion YAML
│       ├── hat_registry.rs     # Registro de hats
│       ├── hatless_ralph.rs    # Modo sin hats
│       ├── memory.rs           # Sistema de memorias
│       ├── memory_store.rs     # Almacenamiento de memorias
│       ├── task.rs             # Sistema de tasks
│       ├── task_store.rs       # Almacenamiento de tasks
│       ├── event_parser.rs     # Parsing de eventos
│       ├── event_loop/         # Loop principal
│       ├── loop_registry.rs    # Registro de loops paralelos
│       ├── merge_queue.rs      # Cola de merges
│       └── worktree.rs         # Soporte git worktrees
├── ralph-adapters/     # Backends soportados
│   └── src/
│       ├── auto_detect.rs      # Deteccion automatica
│       ├── cli_backend.rs      # Backend CLI generico
│       ├── cli_executor.rs     # Ejecutor CLI
│       ├── pty_executor.rs     # Ejecutor PTY
│       └── claude_stream.rs    # Streaming Claude
├── ralph-cli/          # Interfaz de linea de comandos
├── ralph-tui/          # Terminal UI (ratatui)
├── ralph-e2e/          # Tests end-to-end
├── ralph-proto/        # Definiciones de protocolo
└── ralph-bench/        # Benchmarks
```

### 1.3 Backends Soportados

El orchestrator soporta **7+ backends** con un sistema de adaptadores pluggable:

| Backend | Descripcion |
|---------|-------------|
| **Claude Code** | Anthropic Claude CLI |
| **Kiro** | AWS Kiro CLI |
| **Gemini CLI** | Google Gemini |
| **Codex** | OpenAI Codex |
| **Amp** | Sourcegraph Amp |
| **Copilot CLI** | GitHub Copilot |
| **OpenCode** | OpenCode CLI |

### 1.4 Sistema de Hats (Sombreros)

Un **hat** es una persona especializada que Ralph puede "usar". Cada hat tiene:

```yaml
hats:
  planner:
    name: "📋 Planner"
    triggers: ["task.start"]          # Eventos que activan este hat
    publishes: ["plan.ready", "plan.blocked"]  # Eventos que puede emitir
    backend: "claude"                 # Override de backend (opcional)
    max_activations: 3               # Limite de activaciones (opcional)
    default_publishes: "plan.ready"  # Evento por defecto si no hay emit
    instructions: |
      Create an implementation plan for the task.
      When done, emit plan.ready with a summary.
```

### 1.5 Sistema de Eventos

Los eventos son mensajes tipados para coordinacion entre hats:

```yaml
event_loop:
  starting_event: "task.start"      # Primer evento
  completion_promise: "LOOP_COMPLETE"  # Senal de fin
  max_iterations: 50
  max_runtime_seconds: 7200
```

**Routing de eventos**:
- **Exact Match**: `triggers: ["task.start"]`
- **Glob Patterns**: `triggers: ["build.*"]`, `triggers: ["*.error"]`
- **Wildcard**: `triggers: ["*"]`

**Publicar eventos**:
```bash
ralph emit "build.done" "tests: pass, lint: pass"
ralph emit "review.done" --json '{"status": "approved", "issues": 0}'
```

### 1.6 Sistema de Memories + Tasks

**Archivos de estado**:

| Sistema | Archivo | Proposito |
|---------|---------|-----------|
| Memories | `.agent/memories.md` | Aprendizaje persistente cross-session |
| Tasks | `.agent/tasks.jsonl` | Tracking de trabajo runtime |

**Tipos de memorias**:
- `pattern`: Convenciones del codebase
- `decision`: Decisiones arquitecturales
- `fix`: Soluciones a problemas recurrentes
- `context`: Conocimiento especifico del proyecto

**CLI de memorias**:
```bash
ralph tools memory add "All API handlers return Result<Json<T>, AppError>" \
  -t pattern --tags api,error-handling

ralph tools memory search "api" -t fix --tags auth

ralph tools memory list -t fix --last 10
```

**CLI de tasks**:
```bash
ralph tools task add "Implement user authentication" -p 1
ralph tools task list
ralph tools task ready    # Solo tasks sin bloqueos
ralph tools task close task-123
```

**Formato de memories.md**:
```markdown
# Memories

## Patterns

### mem-1737372000-a1b2
> All API handlers return Result<Json<T>, AppError>
<!-- tags: api, error-handling | created: 2024-01-20 -->

## Decisions

### mem-1737372100-c3d4
> Chose JSONL over SQLite for simplicity
<!-- tags: storage | created: 2024-01-20 -->
```

**Formato de tasks.jsonl**:
```json
{"id":"task-001","title":"Implement auth","priority":2,"status":"open","created":"2024-01-20T10:00:00Z"}
{"id":"task-002","title":"Add tests","priority":3,"status":"open","blocked_by":["task-001"],"created":"2024-01-20T10:01:00Z"}
```

---

## 2. SOPs vs Skills

### 2.1 SOPs en ralph-orchestrator

El directorio `.sops/` contiene:
- `code-assist.sop.md`
- `code-task-generator.sop.md`
- `README.md`

**Diferencias clave**:

| Aspecto | SOPs (ralph-orchestrator) | Skills (ai-framework) |
|---------|---------------------------|----------------------|
| **Formato** | Markdown con instrucciones | SKILL.md + referencias |
| **Integracion** | Leidos por el orchestrator | Invocados via Skill tool |
| **Contexto** | Inyectados en prompts | Cargados dinamicamente |
| **Estado** | Persisten en memories | No persisten automaticamente |
| **Orquestacion** | Parte del event loop | Independientes |

### 2.2 Como se integran los SOPs

Los SOPs son instrucciones procedimentales que el orchestrator inyecta en el prompt segun el contexto:

1. **code-assist.sop.md**: Para tareas de asistencia de codigo
2. **code-task-generator.sop.md**: Para generacion de tareas desde specs

Los SOPs **no tienen** sistema de triggers/eventos - son documentos estaticos que el orchestrator usa segun el preset activo.

---

## 3. Presets Detallados

### 3.1 gap-analysis.yml

**Proposito**: Comparacion profunda entre specs e implementacion.

**Hats**:
1. **Analyzer**: Coordina el analisis, inventaria specs
2. **Verifier**: Deep-dive en codigo para verificar compliance
3. **Reporter**: Compila hallazgos en ISSUES.md estructurado

**Flujo**:
```
gap.start → Analyzer → analyze.spec → Verifier → verify.complete
                                              ↓
                     report.request → Reporter → GAP_ANALYSIS_COMPLETE
```

**Output**: `ISSUES.md` con categorias:
- Critical Gaps (Spec Violations)
- Missing Features (Spec Not Implemented)
- Undocumented Behavior (Implementation Without Spec)
- Spec Improvements Needed

### 3.2 research.yml

**Proposito**: Exploracion profunda sin cambios de codigo.

**Hats**:
1. **Researcher**: Busca informacion, analiza patrones
2. **Synthesizer**: Revisa hallazgos, crea resumen coherente

**Regla critica**: NO code changes, NO commits. Solo information gathering.

### 3.3 debug.yml

**Proposito**: Investigacion de bugs usando metodo cientifico.

**Hats**:
1. **Investigator**: Encuentra root cause sistematicamente
2. **Tester**: Disena y ejecuta experimentos para probar hipotesis
3. **Fixer**: Implementa fix con regression test
4. **Verifier**: Verifica que el fix resuelve el problema

**Flujo**:
```
debug.start → Investigator → hypothesis.test → Tester
                    ↓                              ↓
             fix.propose ← hypothesis.confirmed/rejected
                    ↓
               Fixer → fix.applied → Verifier → DEBUG_COMPLETE
```

### 3.4 spec-driven.yml

**Proposito**: Desarrollo specification-first.

**Hats**:
1. **Spec Writer**: Crea spec preciso e inequivoco
2. **Spec Critic**: Revisa completitud (puede rechazar 1 vez)
3. **Implementer**: Implementa EXACTAMENTE lo que dice el spec
4. **Verifier**: Verifica que implementacion coincide con spec

**Filosofia**: El spec es el contrato. La implementacion sigue.

### 3.5 confession-loop.yml

**Proposito**: Completion con auto-evaluacion estructurada.

**Hats**:
1. **Builder**: Implementa tarea, mantiene Internal Monologue
2. **Confessor**: Auditor interno que busca problemas (recompensado por honestidad)
3. **Handler**: Verifica claims y decide si continuar o finalizar

**ConfessionReport**:
```markdown
## Confession

### Objectives Assessment
- **Objective**: <one sentence>
  - **Met?**: Yes/No/Partial
  - **Evidence**: <file:line>

### Uncertainties & Conflicts
### Shortcuts Taken
### Single Easiest Issue to Verify
### Confidence (0-100): <integer>
```

**Umbral**: Confidence >= 80 para completar.

---

## 4. Diferencias Criticas vs skill ralph-loop

### 4.1 Features que orchestrator tiene y skill NO

| Feature | ralph-orchestrator | skill ralph-loop |
|---------|-------------------|------------------|
| **Arquitectura** | Binary Rust | Bash script |
| **Presets** | 27 presets configurables | Prompts hardcoded |
| **Multi-backend** | 7+ backends | Solo Claude Code |
| **Parallel loops** | Git worktrees | No soportado |
| **TUI** | Terminal UI con ratatui | Sin TUI |
| **Memories system** | Built-in con CLI tools | Sin persistencia |
| **Tasks tracking** | JSONL con dependencias | Sin tracking |
| **Event system** | Hats + events tipados | Fases simples |
| **Backpressure** | Configurable por hat | Basic checks |
| **E2E testing** | Framework completo | Sin testing |
| **Session recording** | JSONL replay | No soportado |
| **Diagnostics** | Sistema completo | Basico |

### 4.2 Por que Rust binary vs Bash script?

**Rust binary (ralph-orchestrator)**:
- Performance: ~10x mas rapido en parsing
- Type safety: Menos errores en runtime
- Concurrency: Async nativo para parallel loops
- TUI: ratatui para terminal interactiva
- Testing: Framework de tests robusto
- Distribución: Single binary portable

**Bash script (ralph-loop)**:
- Simplicidad: Facil de entender y modificar
- Zero dependencies: Solo Claude Code CLI
- Rapido de iterar: Cambios inmediatos
- Integración: Nativo en plugin system

### 4.3 Sistema de Presets vs PROMPTs hardcoded

**ralph-orchestrator (presets)**:
```yaml
# presets/feature.yml
event_loop:
  starting_event: "task.start"

hats:
  planner:
    triggers: ["task.start"]
    instructions: |
      Plan the implementation...

  builder:
    triggers: ["plan.ready"]
    instructions: |
      Implement the plan...
```

**skill ralph-loop (hardcoded)**:
```bash
PROMPT_START_FEATURE="Create detailed implementation plan..."
PROMPT_VALIDATE_FEATURE="Review task completion..."
```

---

## 5. Integracion con Brainstorming/Discovery

### 5.1 Como ralph-orchestrator hace discovery

El orchestrator **NO tiene** un sistema de discovery/brainstorming interactivo con el usuario.

El enfoque es:
1. **PROMPT.md**: El usuario escribe el prompt inicial
2. **Spec-first**: Se usa `spec-driven.yml` para definir requisitos
3. **Research preset**: Para exploracion antes de implementar

### 5.2 Presets relacionados con discovery

**research.yml**:
- Analisis de codebase
- Arquitectura review
- Evaluacion de tecnologias
- Analisis competitivo

**socratic-learning.yml**:
- Aprendizaje via preguntas
- Exploracion guiada
- Clarificacion de conceptos

**documentation-first.yml**:
- Documentar antes de implementar
- Clarificar requisitos via docs

### 5.3 NO tiene entrevistas al usuario

A diferencia del skill `brainstorming` en ai-framework, ralph-orchestrator **no** tiene:
- Entrevistas interactivas con el usuario
- Discovery de requirements via dialogo
- Clarification loops automaticos

El enfoque es: "El usuario ya sabe lo que quiere, escribelo en PROMPT.md".

---

## 6. Ralph Tenets (Principios Fundamentales)

### Los 6 Tenets

1. **Fresh Context Is Reliability**
   - Cada iteracion limpia contexto
   - Re-leer specs, plan, codigo cada ciclo
   - Optimizar para "smart zone" (40-60% de ~176K tokens)

2. **Backpressure Over Prescription**
   - No prescribir "como"; crear gates que rechacen mal trabajo
   - Tests, typechecks, builds, lints
   - Para criterios subjetivos: LLM-as-judge con pass/fail binario

3. **The Plan Is Disposable**
   - Regeneracion cuesta un planning loop. Barato.
   - Nunca pelear por salvar un plan

4. **Disk Is State, Git Is Memory**
   - Memories + Tasks son mecanismos de handoff
   - No se necesita coordinacion sofisticada

5. **Steer With Signals, Not Scripts**
   - El codebase es el manual de instrucciones
   - Cuando Ralph falla, agregar una senal para la proxima vez
   - Los prompts iniciales no seran los finales

6. **Let Ralph Ralph**
   - Sentarse en el loop, no en el
   - Afinar como guitarra, no dirigir como orquesta

### Anti-Patterns

- ❌ Construir features en el orchestrator que los agentes pueden manejar
- ❌ Logica de retry compleja (fresh context maneja recovery)
- ❌ Instrucciones paso-a-paso detalladas (usar backpressure)
- ❌ Scoping de trabajo en task selection (scope en plan creation)
- ❌ Asumir funcionalidad faltante sin verificar codigo

---

## 7. Conclusiones y Recomendaciones

### 7.1 Fortalezas de ralph-orchestrator

1. **Arquitectura robusta**: Rust + workspace modular
2. **Flexibilidad**: 27 presets para diferentes workflows
3. **Multi-backend**: No vendor lock-in
4. **Observabilidad**: Diagnostics, TUI, session recording
5. **Parallel execution**: Git worktrees para loops concurrentes

### 7.2 Gaps vs ai-framework skills

1. **Discovery/Brainstorming**: No tiene sistema interactivo
2. **Plugin integration**: No es un Claude Code plugin nativo
3. **Learning curve**: Requiere aprender sistema de hats/events
4. **Overhead**: Binary Rust vs script simple

### 7.3 Recomendaciones para ai-framework

**Adoptar**:
- Sistema de memories persistente
- Tasks con dependencias
- Presets configurables vs PROMPTs hardcoded
- Confession loop para accountability

**Mantener**:
- Brainstorming interactivo (gap de orchestrator)
- Integracion nativa con Claude Code plugin
- Simplicidad de bash para prototipado rapido

**Investigar**:
- Parallel loops via worktrees
- Backpressure configurable por skill
- Event system para coordinacion entre skills
