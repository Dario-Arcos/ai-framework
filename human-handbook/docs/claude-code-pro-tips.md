# Pro tips

Atajos, modos y patrones para trabajar con Claude Code de forma fluida en desarrollo real.

> **Antes de empezar**: lee [Workflow AI-first](./ai-first-workflow.md) para entender el pipeline de desarrollo.

---

## Referencia rápida

| Acción                    | Comando/Atajo              |
| ------------------------- | -------------------------- |
| Toggle razonamiento       | `Option+T` / `Alt+T`       |
| Configurar razonamiento   | `/config`                  |
| Referencia archivo/dir    | `@path`                    |
| Revertir cambios          | `ESC ESC` o `/rewind`      |
| Cambiar modo permisos     | `Shift+Tab` o `Alt+M`      |
| Cambiar modelo            | `/model`                   |
| Bash directo (sin tokens) | `! comando`                |
| Background (terminal)     | `Ctrl+B`                   |
| Background (web)          | `& mensaje`                |
| Ver procesos background   | `/tasks`                   |

---

## Control de razonamiento extendido

**Cómo activar:**
- **Toggle**: `Option+T` (macOS) / `Alt+T` (Windows/Linux)
- **Configuración persistente**: `/config`
- **Límite de tokens**: Variable de entorno `MAX_THINKING_TOKENS`

::: warning Importante
Frases como `thinking`, `think hard`, `ultrathink` **NO asignan tokens de razonamiento**. Son texto normal del prompt. Usa el toggle `Option+T`/`Alt+T` para activar extended thinking.
:::

**Cuándo usar extended thinking:**

| Escenario                        | Recomendación          |
| -------------------------------- | ---------------------- |
| Debugging simple, quick fixes    | Sin extended thinking  |
| Diseño arquitectónico            | Con extended thinking  |
| Refactoring complejo             | Con extended thinking  |
| Análisis de dependencias         | Con extended thinking  |

---

## Referencias rápidas con @

```bash
@src/utils/auth.js revisa esta implementación
@src/components analiza todos los componentes
compara @src/old-auth.js con @src/new-auth.js
```

**Ventajas:** Inmediato (no espera) · Preciso (archivo/dir exacto) · Eficiente con scope de git

---

## Ejecución eficiente

### Bash mode (`!` prefix)

Ejecuta comandos shell directamente **sin interpretación de Claude**, ahorrando tokens:

```bash
! npm test
! git status
! ls -la src/
```

- El comando se ejecuta inmediatamente en shell
- El output se añade al contexto de conversación
- No requiere aprobación de Claude
- Soporta `Ctrl+B` para background

**Cuándo usar:** Comandos rápidos donde no necesitas que Claude interprete o modifique el comando.

**Ahorro:** `! git status` usa ~0 tokens vs ~50+ tokens si Claude lo procesa conversacionalmente.

---

### Background commands (`Ctrl+B`)

Mueve comandos en ejecución al background mientras Claude sigue trabajando:

```bash
npm run dev        # Enter para ejecutar
Ctrl+B             # Push to background
```

- El proceso continúa ejecutándose independientemente
- Claude puede seguir respondiendo prompts
- Output buffereado, recuperable con `/tasks`
- Auto-cleanup al cerrar Claude Code

**Ideal para:** Dev servers, build processes, test suites, logs en tiempo real.

| Acción        | Atajo/Comando         |
| ------------- | --------------------- |
| Background    | `Ctrl+B` (2x en tmux) |
| Ver procesos  | `/tasks`              |
| Terminar      | `K`                   |

---

### Background web tasks (`&` prefix)

Envía tareas a **Claude Code en la web** prefijando con `&`:

```bash
& Refactoriza todos los tests de integración siguiendo el nuevo patrón
& Implementa feature X completa con tests y documentación
```

- La tarea se ejecuta en infraestructura cloud de Anthropic
- Tu terminal queda libre para otras tareas
- Monitoreable desde [claude.ai/code](https://claude.ai/code) o Claude iOS
- Notificación cuando termina

**Casos de uso:** Refactorings masivos, múltiples features en paralelo, iniciar tarea y monitorear desde el teléfono.

::: warning Requisito
Requiere cuenta Claude con acceso a Claude Code Web. La tarea se ejecuta en tu repositorio conectado.
:::

---

## Navegación temporal (/rewind)

Claude Code guarda checkpoints antes de cada edición.

**`ESC ESC`** (2 veces) o **`/rewind`** abre menú con 3 opciones:

- **Conversation only**: Retrocede mensaje, mantiene código
- **Code only**: Revierte archivos, mantiene conversación
- **Both**: Reset completo a checkpoint

```bash
# Explorar alternativa
[implementación A] → ESC ESC (Code only) → [implementación B]

# Recuperar de error
[cambios incorrectos] → ESC ESC (Both)

# Iterar features
[versión 1] → ESC ESC (Conversation only)
```

::: warning Limitaciones
No trackea bash commands · Solo sesión actual · No reemplaza git
:::

---

## Gestión de conversaciones

### La regla de las 3 correcciones

Corregir repetidamente al LLM crea un ciclo negativo. Cada corrección añade ruido al contexto.

```
Intento 1: Incorrecto → Corregir
Intento 2: Incorrecto → Corregir con más contexto
Intento 3: Incorrecto → STOP
```

**En intento 3:**

1. Usa `/rewind` si el error fue reciente
2. Inicia nueva conversación con contexto claro
3. Reformula el problema (la instrucción pudo ser ambigua)

Un fresh start elimina ruido acumulado. Claude procesa el request sin bias de intentos fallidos.

---

### Anti-pattern: expresar frustración

**No hagas:**

```
"No, eso está mal"
"Te dije que no hicieras eso"
"¿Por qué no entiendes?"
```

**Haz:**

```
ESC ESC → Both
[Nueva conversación]
"Necesito implementar X. Contexto: Y. Restricciones: Z."
```

La frustración en mensajes solo añade tokens que contaminan el contexto.

---

### Cuándo empezar de nuevo

**Indicadores:**

- 3+ correcciones sin progreso
- Claude repite el mismo error
- Respuestas confusas o inconsistentes
- Cambio significativo de dirección

**Template para nueva conversación:**

```
Contexto:
- [información relevante]
- [restricciones conocidas]

Intentos previos fallaron porque:
- [razón específica]

Enfoque esperado:
- [dirección clara]
```

---

## Control de permisos y plan mode

**4 modos disponibles:**

| Modo                | Indicador | Comportamiento                            |
| ------------------- | --------- | ----------------------------------------- |
| `default`           | (ninguno) | Pide confirmación para acciones sensibles |
| `acceptEdits`       | ⏵⏵        | Auto-acepta ediciones de archivos         |
| `plan`              | ⏸        | Solo planifica, no ejecuta                |
| `bypassPermissions` | ⏩        | Bypass total (para CI/CD)                 |

**Cambiar modo:** `Shift+Tab` cicla entre modos

**Plan mode workflow:**

1. **Activar**: `Shift+Tab` hasta ver `⏸ plan mode on`
2. **Planificar**: Claude presenta plan sin ejecutar
3. **Revisar**: Analizas el plan propuesto
4. **Aprobar**: Si apruebas, cambia a bypass permissions
5. **Ejecutar**: Cambios se aplican sin interrupciones

::: tip Plan mode para features complejas
Ideal para refactorings grandes, integraciones externas y cambios arquitectónicos. Plan mode + bypass permissions = review seguro antes, ejecución fluida después.
:::

**Configuración persistente en `.claude/settings.local.json`:**

```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": ["Bash(npm run lint)", "Bash(npm test)"],
    "deny": ["Read(.env)", "WebFetch"]
  }
}
```

**Modos recomendados por contexto:**

| Contexto          | Modo recomendado             |
| ----------------- | ---------------------------- |
| Desarrollo local  | `acceptEdits`                |
| Cambios complejos | `plan` → `bypassPermissions` |
| Exploración       | `plan`                       |
| CI/CD             | `bypassPermissions`          |
| Producción        | `default`                    |

::: warning Precaución
`bypassPermissions` elimina TODAS las confirmaciones. Solo usar con código trusted, en CI/CD, o después de revisar plan.
:::

---

## Personalización del framework

### Settings

| Archivo | Propósito | Precedencia |
|---------|-----------|-------------|
| `.claude/settings.json` | Framework defaults (auto-synced) | Base |
| `.claude/settings.local.json` | Overrides personales (nunca se sobrescriben) | **Máxima** |

**Ejemplo `.claude/settings.local.json`:**

```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": ["Bash(npm run lint)"],
    "deny": ["Read(.env)"]
  }
}
```

### Skills

El framework incluye 21+ skills especializados. Se cargan bajo demanda, sin consumir contexto permanente.

**Invocación explícita con `/`:**

El sistema automático de invocación detecta contexto e intenta invocar el skill adecuado, pero no siempre acierta. Para certeza absoluta, escribe `/nombre-del-skill` en cualquier parte de tu prompt:

```bash
# Invocación directa — siempre funciona
/commit
/brainstorming quiero explorar ideas para un sistema de cache
analiza este módulo y después /pull-request

# Combinable con texto natural
refactoriza el auth y cuando termines /commit
```

::: tip Recomendación
Si el skill que necesitas es claro, usa `/skill-name` directamente. La invocación automática es conveniente pero no infalible — el slash explícito elimina ambigüedad.
:::

[Ver guía completa de skills →](./skills-guide.md)

### MCP Servers

Los MCPs conectan Claude con servicios externos. Cada MCP activo consume parte del context window.

[Ver configuración de integraciones →](./integrations.md)

### Personal instructions

**`CLAUDE.local.md`** — Instrucciones personales (auto-gitignored, nunca se sincronizan).

[Best practices →](https://www.anthropic.com/engineering/claude-code-best-practices)

::: tip Personalización segura
El framework nunca sobrescribe `settings.local.json` ni `CLAUDE.local.md`. Personaliza sin riesgo de perder cambios.
:::

---

## Invocación explícita de agentes

Los agents se invocan automáticamente por contexto. Usa invocación explícita cuando necesites control directo.

**Sintaxis:**

```bash
# Natural language
"Use the {agent-name} agent to {task}"

# Paralelo con Task tool
"Use Task tool to launch code-reviewer and security-reviewer in parallel"
```

**Ejemplos:**

```bash
# Review en paralelo (PR workflow)
"Launch code-reviewer and security-reviewer in parallel
to review changes in current branch vs develop"

# Especialización forzada
"Use the performance-engineer agent to analyze
this database query optimization"
```

::: tip Cuándo usar invocación explícita
- Workflows establecidos (PR reviews, deployment checks)
- Paralelización (múltiples agents independientes)
- Control preciso (garantizar agent específico)
- Context overflow (task muy grande para un solo context)
:::

[Ver guía completa de agents →](./agents-guide.md)

---

## Análisis de pull requests

Claude Code integra con GitHub CLI:

```bash
"Analiza el PR #210 y evalúa los hallazgos objetivamente"
"Revisa los comentarios del PR actual y sugiere qué corregir"
```

**Workflow típico:**

```
1. "Analiza PR #210"     → Claude usa gh para obtener datos
2. Claude presenta evaluación
3. "Corrige X e Y"       → Aplica solo fixes confirmados
4. Claude commitea con /commit
```

---

## Optimización del workflow

**Validación de contexto** antes de comandos importantes:

```bash
git branch    # ¿Branch correcto?
pwd           # ¿Directorio correcto?
git status    # ¿Cambios pendientes?
```

**Checkpointing proactivo** antes de cambios grandes:

```bash
git add .
git commit -m "checkpoint: antes de refactor X"
[realizar cambios con Claude Code]
# Si falla: git reset --hard HEAD
```

Git checkpoint + Claude `/rewind` = doble red de seguridad.

---

## Selección de modelo

```bash
/model            # Ver modelos disponibles
/model haiku      # Testing, experimentos (bajo costo)
/model sonnet     # Producción, features reales (máxima calidad)
```

**Regla simple:** Haiku para probar, Sonnet para producción.

---

## Combinaciones efectivas

**@ referencias + extended thinking:**

```
@src/core/ Option+T "analiza la arquitectura de este módulo"
```

Contexto preciso desde el inicio + razonamiento profundo = análisis arquitectónico concreto.

**ESC ESC + nueva conversación:**

```
[resultado no deseado] → ESC ESC (Both) → [nueva conversación limpia]
```

Después de 3 intentos fallidos, un fresh start es mejor que insistir con contexto contaminado.

**Plan mode + extended thinking:**

```
Shift+Tab (plan mode) + Option+T → planificación profunda antes de ejecutar
```

Para tareas complejas: planifica con extended thinking, revisa, y luego ejecuta.

---

## Flujo recomendado

1. **Inicia con contexto** — Usa `@` para cargar archivos relevantes
2. **Ajusta razonamiento** — `Option+T`/`Alt+T` según complejidad de la tarea
3. **Checkpoint antes de cambios** — Protección contra errores
4. **3 intentos máximo** — Después, nueva conversación
5. **Revierte sin miedo** — `ESC ESC` está para eso

**Anti-pattern:** Corregir infinitamente sin fresh start. Si 3 intentos no funcionan, el enfoque necesita cambiar, no el número de intentos.

---

## Referencias

**Framework:**

- [AI-First Workflow](./ai-first-workflow.md) — Workflows completos
- [Skills](./skills-guide.md) — Skills especializados
- [Agents](./agents-guide.md) — Agentes especializados por dominio

**Docs oficiales:**

- [Claude Code](https://code.claude.com/docs/en/)
- [Extended Thinking](https://code.claude.com/docs/en/common-workflows#use-extended-thinking)
- [Interactive Mode](https://code.claude.com/docs/en/interactive-mode)

**Siguiente paso**: [Skills](./skills-guide.md)

---
::: info Última actualización
**Fecha**: 2026-02-08
:::
