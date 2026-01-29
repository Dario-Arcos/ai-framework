# Ralph-Orchestrator: Flujo Paso a Paso

> Guía definitiva del proceso completo de orquestación

---

## Resumen

Ralph-orchestrator ejecuta proyectos complejos dividiendo el trabajo en fases SOP (Standard Operating Procedures) y delegando la implementación a un loop autónomo que mantiene contexto fresco.

```
┌─────────────────────────────────────────────────────────────────┐
│                    RALPH-ORCHESTRATOR                           │
├─────────────────────────────────────────────────────────────────┤
│  FASE HITL (Human-in-the-Loop)                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│  │Discovery│→│Planning │→│  Tasks  │→│ Config  │               │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘               │
├─────────────────────────────────────────────────────────────────┤
│  FASE AFK (Away-From-Keyboard)                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  LOOP.SH: Iteraciones con contexto fresco (~100K max)   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Fase 0: Verificación de Infraestructura

**Objetivo**: Asegurar que el proyecto tiene la infraestructura necesaria.

### Pasos:

1. **Verificar si existe `./loop.sh`** en la raíz del proyecto
2. **Si NO existe**, ejecutar instalación:
   ```bash
   ./skills/ralph-orchestrator/scripts/install.sh /path/to/project
   ```
3. **Verificar archivos creados**:
   - `./loop.sh` - Script de ejecución
   - `.ralph/config.sh` - Configuración
   - `guardrails.md` - Signs de sesión
   - `scratchpad.md` - Estado temporal

### Si falla:
- STOP inmediato
- Reportar qué falta
- NO improvisar

---

## Fase 1: Discovery (sop-discovery)

**Objetivo**: Documentar el problema antes de diseñar soluciones.

### Pasos:

1. **Ejecutar skill** `sop-discovery`
2. **Documentar en** `specs/{feature}/discovery.md`:
   - JTBD (Job To Be Done)
   - Constraints
   - Risks
   - Prior Art
   - Decision

### Modos:
- `--mode=interactive` - Con preguntas humanas (default)
- `--mode=autonomous` - Para ejecución AI (omite preguntas irrelevantes)

### Validación:
- ✓ `specs/{feature}/discovery.md` existe
- ✓ JTBD está documentado

---

## Fase 2: Planning (sop-planning)

**Objetivo**: Diseñar la arquitectura antes de implementar.

### Pasos:

1. **Ejecutar skill** `sop-planning`
2. **Crear en** `specs/{feature}/design/`:
   - `detailed-design.md` - Arquitectura
   - Decisiones técnicas
   - Trade-offs evaluados

### Validación:
- ✓ `specs/{feature}/design/` directorio existe
- ✓ `detailed-design.md` existe

---

## Fase 3: Task Generation (sop-task-generator)

**Objetivo**: Dividir el trabajo en tareas atómicas.

### Pasos:

1. **Ejecutar skill** `sop-task-generator`
2. **Crear** `specs/{feature}/implementation/plan.md` con steps
3. **Generar UN task file para CADA step**:
   ```
   specs/{feature}/implementation/
   ├── plan.md
   ├── step01/
   │   └── task-01-description.code-task.md
   ├── step02/
   │   └── task-01-description.code-task.md
   └── step03/
       └── task-01-description.code-task.md
   ```

### Validación:
- ✓ N task files = N steps en plan
- ✓ Cada task tiene acceptance criteria

---

## Fase 4: Configuración

**Objetivo**: Preparar el loop para ejecución.

### Archivo `.ralph/config.sh`:

```bash
# Modelo y contexto
MODEL=claude-sonnet-4-20250514
CONTEXT_LIMIT=200000      # 200K tokens
CONTEXT_WARNING=40        # Warning al 40%
CONTEXT_CRITICAL=60       # Iterar al 60%

# Quality gates
QUALITY_LEVEL=production  # prototype | production | world-class
MIN_TEST_COVERAGE=90      # 0-100, 0 deshabilita

# Iteraciones
MAX_ITERATIONS=10
```

---

## Fase 5: Ejecución del Loop

**Objetivo**: Implementar tareas de forma autónoma.

### Lanzamiento:

```bash
# SIEMPRE en background
Bash(command="./loop.sh", run_in_background=true)
```

### El loop hace por cada iteración:

1. **Lee** `scratchpad.md` para contexto
2. **Lee** `guardrails.md` para signs
3. **Ejecuta** la tarea actual
4. **Valida** gates (test, lint, typecheck, build)
5. **Actualiza** estado
6. **Captura** signs si encuentra gotchas
7. **Decide**: continuar o iterar (según contexto)

### Gestión de Contexto:

```
0-40%   → Zona verde, continuar
40-60%  → Zona amarilla, considerar iterar
60%+    → Zona roja, DEBE iterar
```

El cálculo incluye:
- `input_tokens`
- `cache_read_input_tokens`
- `cache_creation_input_tokens`

---

## Fase 6: Validaciones Pre-Complete

Antes de aceptar `<promise>COMPLETE</promise>`:

### 1. Test Coverage Gate
```bash
if coverage < MIN_TEST_COVERAGE (90%):
    REJECT → "Add more tests"
```

### 2. Guardrails Learning
```bash
if guardrails vacío after N iterations:
    WARNING → "Learning failure - no signs captured"
```

### 3. Config Consistency
```bash
if AGENTS.md.QUALITY_LEVEL != config.sh.QUALITY_LEVEL:
    WARNING → "Config mismatch detected"
```

---

## Fase 7: Monitoreo

### Cómo monitorear (no-bloqueante):

```bash
# Check estado
TaskOutput(task_id="{id}", block=false)

# Ver log completo
Read(file_path="logs/iteration-{N}.log")

# Ver último output
Read(file_path="logs/current.log")
```

### NO hacer:
- `tail -f` (bloquea)
- Timeout largo (puede matar proceso)

---

## Fase 8: Completitud

### Señal de completitud:

El loop emite `<promise>COMPLETE</promise>` cuando:
- Todos los tasks en plan.md están `[x]`
- Gates pasan (test, lint, build)
- Coverage >= 90%
- Doble verificación exitosa

### Artefactos finales:

```
proyecto/
├── src/                    # Código implementado
├── tests/                  # Tests (90%+ coverage)
├── specs/{feature}/
│   ├── discovery.md        # JTBD documentado
│   ├── design/
│   │   └── detailed-design.md
│   └── implementation/
│       ├── plan.md         # Todos [x]
│       └── step*/task*.md  # Status: COMPLETED
├── guardrails.md           # Signs capturados
├── scratchpad.md           # Estado final
└── logs/                   # Historia de iteraciones
```

---

## Diagrama de Flujo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                         INICIO                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE 0: ¿Existe ./loop.sh?                                     │
│  ├─ NO → Ejecutar install.sh                                    │
│  └─ SÍ → Continuar                                              │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE 1: DISCOVERY                                              │
│  └─ Crear specs/{feature}/discovery.md                          │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE 2: PLANNING                                               │
│  └─ Crear specs/{feature}/design/detailed-design.md             │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE 3: TASK GENERATION                                        │
│  └─ Crear plan.md + N task files                                │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE 4: CONFIGURACIÓN                                          │
│  └─ Verificar .ralph/config.sh                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE 5: LOOP AUTÓNOMO                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Para cada iteración:                                    │   │
│  │  1. Leer scratchpad + guardrails                         │   │
│  │  2. Ejecutar tarea                                       │   │
│  │  3. Validar gates                                        │   │
│  │  4. Actualizar estado                                    │   │
│  │  5. ¿Contexto > 60%? → Nueva iteración                   │   │
│  │  6. ¿Todo completo? → Salir                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE 6: VALIDACIONES                                           │
│  ├─ Coverage >= 90%?                                            │
│  ├─ Guardrails no vacío?                                        │
│  └─ Config consistente?                                         │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  <promise>COMPLETE</promise>                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| "loop.sh not found" | Infraestructura no instalada | Ejecutar install.sh |
| "Context: 0%" | Bug de cálculo (ya corregido) | Actualizar loop.sh |
| "discovery.md missing" | SOP saltado | Ejecutar sop-discovery primero |
| "design/ missing" | Planning saltado | Ejecutar sop-planning primero |
| "Coverage < 90%" | Tests insuficientes | Agregar más tests |
| "No signs captured" | Learning failure | Agregar signs manualmente |

---

## Principios Clave

1. **Contexto Fresco = Calidad**: El modelo es más efectivo en el primer 40-60% del contexto
2. **SOP No Negociable**: Discovery → Planning → Tasks → Execute
3. **Validación Continua**: Gates en cada iteración
4. **Aprendizaje Capturado**: Signs documentan gotchas para futuras iteraciones
5. **Autonomía Controlada**: El loop es autónomo pero validado

---

*Generado: 2026-01-28*
*Versión: Post-auditoría con 16 mejoras implementadas*
