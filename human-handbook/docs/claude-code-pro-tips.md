# Claude Code Pro-Tips

::: tip Objetivo
Fluir naturalmente con Claude Code usando shortcuts, thinking modes, y patterns que funcionan.
:::

---

## Quick Reference

| Acción                        | Comando/Atajo         |
| ----------------------------- | --------------------- |
| Razonamiento básico           | `thinking`            |
| Razonamiento profundo         | `think hard`          |
| Razonamiento más profundo     | `think harder`        |
| Razonamiento máximo           | `ultrathink`          |
| Toggle razonamiento           | `Tab`                 |
| Referencia archivo/directorio | `@path`               |
| Revertir cambios              | `ESC ESC` o `/rewind` |
| Cambiar modo permisos         | `Shift+Tab`           |

---

## 🧠 Control de Razonamiento Extendido

Sistema de razonamiento con niveles progresivos de profundidad.

### Cuándo Usar Cada Nivel

| Nivel          | Uso Recomendado                                            |
| -------------- | ---------------------------------------------------------- |
| `thinking`     | Debugging, refactoring simple, code review                 |
| `think hard`   | Diseño de features, optimización de queries                |
| `think harder` | Refactoring complejo, análisis de dependencias             |
| `ultrathink`   | Arquitectura de sistemas, análisis de codebase desconocida |

### Activación

**Explícita** - Incluye trigger en prompt:

```bash
ultrathink analiza esta optimización de performance
```

**Toggle** - Presiona `Tab` durante sesión para activar/desactivar

::: tip Pattern Efectivo
Comienza con nivel bajo, escala si el problema es más complejo de lo anticipado. Claude se ajusta naturalmente.
:::

---

## Referencias Rápidas con @

Referencia archivos o directorios sin esperar a que Claude los lea.

**Sintaxis:**

```text
@src/utils/auth.js revisa esta implementación
@src/components analiza todos los componentes
compara @src/old-auth.js con @src/new-auth.js
```

**Benefits:**

- Inmediato (no wait para tool calls)
- Preciso (exact file/directory)
- Eficiente con scope de git

**Pro tip:** Usa `@` para dar context upfront. Claude lee lo que necesita cuando lo necesita.

---

## ⏮️ Navegación Temporal

Claude Code guarda checkpoints antes de cada edición.

### Revertir Cambios

**`ESC ESC`** (2 veces) o **`/rewind`** abre menú con 3 opciones:

- **Conversation only**: Retrocede mensaje, mantiene código
- **Code only**: Revierte archivos, mantiene conversación
- **Both**: Reset completo a checkpoint

### Casos de Uso Comunes

```bash
# Explorar alternativa
[implementación A]
ESC ESC → Code only
[implementación B]

# Recuperar de error
[cambios incorrectos]
ESC ESC → Both

# Iterar features
[versión 1]
ESC ESC → Conversation only
```

**Limitaciones:** No trackea bash commands, solo sesión actual, no reemplaza git.

**Pro tip:** Piensa en `/rewind` como "undo experimental". Git es para undo production.

---

## Gestión de Conversaciones

### La Regla de las 3 Correcciones

**El problema:**
Corregir repetidamente al LLM crea ciclo negativo. Cada corrección añade "ruido" al contexto. LLM persevera en error al intentar "complacer" correcciones.

**La regla:**

```
Intento 1: Resultado incorrecto → Corregir
Intento 2: Aún incorrecto → Corregir con más contexto
Intento 3: Sigue incorrecto → STOP
```

**En intento 3, en lugar de seguir corrigiendo:**

1. Usa `/rewind` si error fue reciente
2. Inicia nueva conversación con contexto claro
3. Reformula el problema - quizás instrucción fue ambigua

**Por qué funciona:** Fresh start elimina el "ruido" acumulado. Claude procesa tu request sin bias de intentos fallidos previos.

---

### Anti-Pattern: "Maldecir" al LLM

❌ **No hagas:**

```
"No, eso está mal"
"Te dije que no hicieras eso"
"¿Por qué no entiendes?"
```

✅ **Haz:**

```
ESC ESC → Both
[Nueva conversación]
"Necesito implementar X. Contexto: Y. Restricciones: Z."
```

**Por qué:** LLM no tiene "memoria emocional". Frustración en tus mensajes solo añade tokens que confunden el context.

---

### Cuándo Empezar de Nuevo

**Indicadores claros:**

- 3+ correcciones sin progreso
- LLM repite mismo error
- Respuestas confusas o inconsistentes
- Cambio significativo de dirección

**Template para nueva conversación:**

```
ultrathink necesito [objetivo claro]

Contexto:
- [información relevante]
- [restricciones conocidas]

Intentos previos fallaron porque:
- [razón específica]

Enfoque esperado:
- [dirección clara]
```

---

## Control de Permisos & Plan Mode

4 modos de permisos disponibles:

| Modo                | Indicador | Comportamiento                            |
| ------------------- | --------- | ----------------------------------------- |
| `default`           | (ninguno) | Pide confirmación para acciones sensibles |
| `acceptEdits`       | ⏵⏵        | Auto-acepta ediciones de archivos         |
| `plan`              | ⏸        | Solo planifica, no ejecuta                |
| `bypassPermissions` | ⏩        | Bypass total (para CI/CD)                 |

### Cambiar Modo Durante Sesión

**`Shift+Tab`**: Cicla entre modos en orden

```
Normal (ninguno) → Auto-Accept (⏵⏵) → Plan Mode (⏸) → [repite ciclo]
```

**Indicadores visuales** en CLI:

- `⏸ plan mode on` → Plan Mode activo
- `⏵⏵ accept edits on` → Auto-Accept activo
- Sin indicador → Modo default

### Plan Mode Workflow

**Plan Mode** permite revisar cambios antes de ejecutar:

1. **Activar**: Presiona `Shift+Tab` hasta ver `⏸ plan mode on`
2. **Planificar**: Claude presenta plan completo sin ejecutar
3. **Revisar**: Analizas el plan propuesto
4. **Aprobar/Rechazar**:
   - Si apruebas → Claude Code UI facilita cambio a bypass permissions
   - Si rechazas → Modifica request y repite
5. **Ejecutar**: Con bypass permissions, cambios se aplican sin interrupciones

::: tip Workflow Recomendado
Plan Mode + Bypass Permissions = Mejor de ambos mundos:

- Review seguro antes de ejecutar (plan mode)
- Ejecución fluida después de aprobar (bypass)
  :::

### Configuración Persistente

En `.claude/settings.local.json`:

```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": ["Bash(npm run lint)", "Bash(npm test)"],
    "deny": ["Read(.env)", "WebFetch"]
  }
}
```

### Casos de Uso

| Contexto          | Modo Recomendado             | Razón                                  |
| ----------------- | ---------------------------- | -------------------------------------- |
| Desarrollo Local  | `acceptEdits`                | Flujo rápido sin confirmaciones        |
| Cambios Complejos | `plan` → `bypassPermissions` | Review antes, ejecución fluida después |
| Exploración       | `plan`                       | Ver sin ejecutar (dry-run)             |
| CI/CD             | `bypassPermissions`          | Automatización total                   |
| Producción        | `default`                    | Control manual estricto                |

::: warning Precaución de Seguridad
`bypassPermissions` elimina TODAS las confirmaciones. Solo usar:

- Con código trusted
- En automatización confiable (CI/CD)
- Después de revisar plan en plan mode
  :::

---

## Sub-Agents: Invocación Explícita

Claude Code puede usar sub-agents automáticamente o puedes invocarlos explícitamente cuando necesites control preciso.

### Invocación Automática vs Explícita

**Invocación Automática** (default):

```bash
"Revisa la seguridad de este código"
# Claude decide automáticamente usar security-reviewer
```

**Invocación Explícita** (control manual):

```bash
"Use the security-reviewer agent to analyze this code"
# Fuerza uso de security-reviewer específicamente
```

### Sintaxis de Invocación Explícita

**Opción 1: Natural language**

```bash
"Use the {agent-name} agent to {task}"
"Use the code-quality-reviewer agent to review changes in PR #123"
```

**Opción 2: Task tool (paralelo)**

```bash
# En tu prompt, describe que Claude debe usar Task tool:
"Use Task tool to launch code-quality-reviewer and security-reviewer in parallel"
```

### Best Practices (Claude Docs)

1. **Single Responsibility**
   - Cada sub-agent debe tener un propósito claro y único
   - Evita agents que hacen "todo"
   - Ejemplo: `security-reviewer` solo seguridad, no calidad de código

2. **Detailed Prompts**
   - Provee contexto específico al invocar
   - Incluye ejemplos y constraints
   - Más guía = mejor performance

3. **Tool Access Control**
   - Solo da herramientas necesarias
   - Mejora seguridad y foco
   - Ejemplo: `docs-writer` no necesita bash access

4. **Let Claude Orchestrate**
   - Claude delega apropiadamente sin instrucción explícita
   - Solo usa invocación explícita cuando:
     - Necesitas garantizar uso de agent específico
     - Quieres ejecutar múltiples agents en paralelo
     - El task claramente beneficia de context window separado

5. **Context Management**
   - Sub-agents mantienen context separado del main agent
   - Previene information overload
   - Útil para tasks complejos con mucho contexto

### Casos de Uso Común

**Review en Paralelo** (PR workflow):

```bash
"Launch code-quality-reviewer and security-reviewer in parallel
to review changes in current branch vs develop"
```

**Especialización Forzada**:

```bash
"Use the performance-engineer agent specifically
to analyze this database query optimization"
```

**Research Profundo**:

```bash
"Use the web-search-specialist agent to research
React Server Components best practices in 2025"
```

**Documentación Completa**:

```bash
"Use the api-documenter agent to generate
OpenAPI 3.1 spec for all endpoints in src/api/"
```

### Ejecución en Paralelo

Para máxima eficiencia, ejecuta agents independientes en paralelo:

```bash
# Ejemplo: PR review completo
"I need you to:
1. Use Task tool to launch code-quality-reviewer
2. Use Task tool to launch security-reviewer
Execute both in parallel, then report combined findings"
```

**Beneficios:**

- Tiempo de ejecución reducido
- Context windows independientes
- Análisis especializado sin interferencia

::: tip Cuándo Usar Invocación Explícita

- **Workflows establecidos**: PR reviews, deployment checks
- **Paralelización**: Múltiples agents independientes
- **Control preciso**: Garantizar agent específico
- **Context overflow**: Task muy grande para single context
  :::

---

## Análisis de Pull Requests

Claude Code integra con GitHub CLI para análisis conversacional:

```bash
# Natural language directo
"Analiza el PR #210 y evalúa los hallazgos objetivamente"
"Revisa los comentarios del PR actual y sugiere qué corregir"
```

**Qué hace Claude:**

- Consulta estado, comentarios, checks via `gh pr view`
- Evalúa hallazgos críticamente (validez técnica, contexto, ROI)
- Aplica correcciones y commitea cambios

**Workflow típico:**

```
1. "Analiza PR #210"     → Claude usa gh para datos
2. Claude presenta evaluación crítica
3. "Corrige X e Y"       → Aplica solo fixes confirmados
4. Claude commitea con /ai-framework:git-github:commit
```

---

## Workflow Optimization

### Validación de Contexto

Antes de comandos importantes, verifica:

```bash
git branch    # ¿Branch correcto?
pwd           # ¿Directorio correcto?
git status    # ¿Cambios pendientes?
```

**Por qué:** Previene "oh, estaba en la branch equivocada" después de 30 minutos de trabajo.

---

### Checkpointing Proactivo

Antes de cambios grandes:

```bash
git add .
git commit -m "checkpoint: antes de refactor X"
[realizar cambios con Claude Code]
# Si falla: git reset --hard HEAD
```

**Benefit:** Git checkpoint + Claude `/rewind` = doble red de seguridad.

---

## Selección de Modelo

Cambia modelo con `/model` para optimizar costos:

```bash
/model            # Ver modelos disponibles
/model haiku      # Testing, experimentos (bajo costo)
/model sonnet     # Producción, features reales (máxima calidad)
```

**Regla simple:** Haiku para probar, Sonnet para producción.

---

## Combinaciones Poderosas

### ultrathink + @directorio

```bash
ultrathink analiza la arquitectura de @src/core
```

**Por qué funciona:** Claude gets deep context upfront + razonamiento profundo = architectural insights precisos.

---

### ESC ESC + nueva conversación

```
[resultado no deseado]
ESC ESC → Both
[nueva conversación con contexto limpio]
```

**Cuándo:** Después de 3 intentos fallidos. Fresh start > insistir en contexto corrupto.

---

### Tab + thinking explícito

```
Tab (activar razonamiento)
"ultrathink diseña este sistema"
```

**Cuándo:** Problems realmente complejos. Double thinking = Claude goes extra deep.

---

## Flujo Natural Recomendado

**Secuencia que funciona:**

1. **Inicia con contexto** - Usa `@` para archivos relevantes
2. **Ajusta razonamiento** - `Tab` o triggers explícitos según complejidad
3. **Checkpoint antes de cambios** - Protección contra errores
4. **3 intentos máximo** - Después → nueva conversación
5. **Revierte sin miedo** - `ESC ESC` es tu amigo

**Anti-pattern:** Corregir infinitamente sin fresh start. Si 3 intentos no funcionan, el enfoque necesita cambiar, no más correcciones.

---

## Referencias

**Documentación del framework:**

- [AI-First Workflow](./ai-first-workflow.md) — Workflows completos
- [Commands Guide](./commands-guide.md) — 24 comandos
- [Agents Guide](./agents-guide.md) — 45 specialized agents

**Docs oficiales:**

- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)
- [Extended Thinking](https://docs.claude.com/en/docs/build-with-claude/extended-thinking)

---

::: info Última Actualización
**Fecha**: 2025-10-16 | **Tips**: Claude Code Workflow Optimization
:::
