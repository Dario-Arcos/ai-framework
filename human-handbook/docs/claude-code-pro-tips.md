# Claude Code Pro-Tips

::: tip ¿Para Qué Esta Guía?
Shortcuts, thinking modes, y patterns que funcionan para fluir naturalmente con Claude Code en desarrollo real.
:::

---

## Quick Reference

| Acción                    | Comando/Atajo         |
| ------------------------- | --------------------- |
| Razonamiento básico       | `thinking`            |
| Razonamiento profundo     | `think hard`          |
| Razonamiento más profundo | `think harder`        |
| Razonamiento máximo       | `ultrathink`          |
| Toggle razonamiento       | `Tab`                 |
| Referencia archivo/dir    | `@path`               |
| Revertir cambios          | `ESC ESC` o `/rewind` |
| Cambiar modo permisos     | `Shift+Tab`           |
| Cambiar modelo            | `/model`              |

---

## Control de Razonamiento Extendido

**Cuándo usar cada nivel:**

| Nivel          | Uso Recomendado                                            |
| -------------- | ---------------------------------------------------------- |
| `thinking`     | Debugging, refactoring simple, code review                 |
| `think hard`   | Diseño de features, optimización de queries                |
| `think harder` | Refactoring complejo, análisis de dependencias             |
| `ultrathink`   | Arquitectura de sistemas, análisis de codebase desconocida |

**Activación:** Incluye trigger en prompt o presiona `Tab` durante sesión.

```bash
ultrathink analiza esta optimización de performance
```

::: tip Pattern Efectivo
Comienza con nivel bajo, escala si el problema es más complejo. Claude se ajusta naturalmente.
:::

---

## Referencias Rápidas con @

```bash
@src/utils/auth.js revisa esta implementación
@src/components analiza todos los componentes
compara @src/old-auth.js con @src/new-auth.js
```

**Benefits:** Inmediato (no wait) · Preciso (exact file/dir) · Eficiente con scope de git

---

## Navegación Temporal (/rewind)

Claude Code guarda checkpoints antes de cada edición.

**`ESC ESC`** (2 veces) o **`/rewind`** abre menú con 3 opciones:

- **Conversation only**: Retrocede mensaje, mantiene código
- **Code only**: Revierte archivos, mantiene conversación
- **Both**: Reset completo a checkpoint

**Casos de uso:**

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

## Gestión de Conversaciones

### La Regla de las 3 Correcciones

**El problema:** Corregir repetidamente al LLM crea ciclo negativo. Cada corrección añade ruido al contexto.

**La regla:**

```
Intento 1: Incorrecto → Corregir
Intento 2: Incorrecto → Corregir con más contexto
Intento 3: Incorrecto → STOP
```

**En intento 3:**

1. Usa `/rewind` si error fue reciente
2. Inicia nueva conversación con contexto claro
3. Reformula el problema - instrucción pudo ser ambigua

**Por qué funciona:** Fresh start elimina ruido acumulado. Claude procesa request sin bias de intentos fallidos.

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

**Por qué:** Frustración en mensajes solo añade tokens que confunden el context.

---

### Cuándo Empezar de Nuevo

**Indicadores:**

- 3+ correcciones sin progreso
- LLM repite mismo error
- Respuestas confusas/inconsistentes
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

**4 modos disponibles:**

| Modo                | Indicador | Comportamiento                            |
| ------------------- | --------- | ----------------------------------------- |
| `default`           | (ninguno) | Pide confirmación para acciones sensibles |
| `acceptEdits`       | ⏵⏵        | Auto-acepta ediciones de archivos         |
| `plan`              | ⏸        | Solo planifica, no ejecuta                |
| `bypassPermissions` | ⏩        | Bypass total (para CI/CD)                 |

**Cambiar modo:** `Shift+Tab` cicla entre modos

**Plan Mode Workflow:**

1. **Activar**: `Shift+Tab` hasta ver `⏸ plan mode on`
2. **Planificar**: Claude presenta plan sin ejecutar
3. **Revisar**: Analizas plan propuesto
4. **Aprobar/Rechazar**: Si apruebas → cambio a bypass permissions
5. **Ejecutar**: Cambios se aplican sin interrupciones

::: tip Workflow Recomendado
Plan Mode + Bypass Permissions = Review seguro antes + ejecución fluida después
:::

::: tip Recomendación: Plan Mode para Features Complejas
Usa plan mode (`Shift+Tab` hasta ⏸) con `ultrathink` para features complejas. Combina análisis profundo + revisión antes de ejecutar. Pattern: **Think → Plan → Review → Execute**.

Ideal para: refactorings grandes, integraciones externas, cambios arquitectónicos.
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

**Casos de uso:**

| Contexto          | Modo Recomendado             |
| ----------------- | ---------------------------- |
| Desarrollo Local  | `acceptEdits`                |
| Cambios Complejos | `plan` → `bypassPermissions` |
| Exploración       | `plan`                       |
| CI/CD             | `bypassPermissions`          |
| Producción        | `default`                    |

::: warning Precaución
`bypassPermissions` elimina TODAS las confirmaciones. Solo usar con código trusted, en CI/CD, o después de revisar plan.
:::

---

## Framework Customization

**Framework provides defaults. You control overrides.**

### Settings (v2.0+)

| Archivo | Propósito | Precedencia |
|---------|-----------|-------------|
| `.claude/settings.json` | Framework defaults (auto-synced) | Base |
| `.claude/settings.local.json` | Personal overrides (never touched) | **Máxima** |

**Precedence:** `settings.local.json` > `settings.json`

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

### MCP Servers (v2.0+)

| Ubicación | Propósito | Precedencia |
|-----------|-----------|-------------|
| Plugin `.mcp.json` | Framework MCP (Playwright, Shadcn) | Base |
| Project `.mcp.json` | Custom MCP servers (optional) | **Máxima** |

**Precedence:** project > plugin

Agrega custom MCP servers en project root sin tocar framework defaults.

[MCP docs →](https://docs.claude.com/en/docs/claude-code/mcp)

### Personal Instructions

**`CLAUDE.local.md`** — Personal instructions (auto-gitignored, never synced)

[Best practices →](https://www.anthropic.com/engineering/claude-code-best-practices)

::: tip Arquitectura v2.0
Framework nunca sobrescribe `settings.local.json` o `CLAUDE.local.md`. Personaliza sin miedo a perder cambios.
:::

---

## Sub-Agents: Invocación Explícita

**Invocación Automática** (default):

```bash
"Revisa la seguridad de este código"
# Claude decide usar security-reviewer
```

**Invocación Explícita** (control manual):

```bash
"Use the security-reviewer agent to analyze this code"
# Fuerza uso de security-reviewer
```

**Sintaxis:**

```bash
# Natural language
"Use the {agent-name} agent to {task}"

# Task tool (paralelo)
"Use Task tool to launch code-quality-reviewer and security-reviewer in parallel"
```

**Best Practices:**

1. **Single Responsibility** - Cada agent un propósito claro
2. **Detailed Prompts** - Provee contexto específico
3. **Tool Access Control** - Solo herramientas necesarias
4. **Let Claude Orchestrate** - Solo invocación explícita cuando:
   - Necesitas garantizar agent específico
   - Quieres múltiples agents en paralelo
   - Task beneficia de context window separado

**Casos de uso común:**

```bash
# Review en paralelo (PR workflow)
"Launch code-quality-reviewer and security-reviewer in parallel
to review changes in current branch vs develop"

# Especialización forzada
"Use the performance-engineer agent specifically
to analyze this database query optimization"

# Research profundo
"Use the web-search-specialist agent to research
React Server Components best practices in 2025"
```

::: tip Cuándo Usar Invocación Explícita

- Workflows establecidos (PR reviews, deployment checks)
- Paralelización (múltiples agents independientes)
- Control preciso (garantizar agent específico)
- Context overflow (task muy grande para single context)
  :::

---

## Análisis de Pull Requests

Claude Code integra con GitHub CLI:

```bash
"Analiza el PR #210 y evalúa los hallazgos objetivamente"
"Revisa los comentarios del PR actual y sugiere qué corregir"
```

**Workflow típico:**

```
1. "Analiza PR #210"     → Claude usa gh para datos
2. Claude presenta evaluación crítica
3. "Corrige X e Y"       → Aplica solo fixes confirmados
4. Claude commitea con /ai-framework:git-github:commit
```

---

## Workflow Optimization

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

**Benefit:** Git checkpoint + Claude `/rewind` = doble red de seguridad

---

## Selección de Modelo

```bash
/model            # Ver modelos disponibles
/model haiku      # Testing, experimentos (bajo costo)
/model sonnet     # Producción, features reales (máxima calidad)
```

**Regla simple:** Haiku para probar, Sonnet para producción.

---

## Combinaciones Poderosas

**ultrathink + @directorio:**

```bash
ultrathink analiza la arquitectura de @src/core
```

Claude gets deep context upfront + razonamiento profundo = architectural insights precisos

**ESC ESC + nueva conversación:**

```
[resultado no deseado] → ESC ESC (Both) → [nueva conversación limpia]
```

Después de 3 intentos fallidos. Fresh start > insistir en contexto corrupto

**Tab + thinking explícito:**

```
Tab (activar razonamiento) + "ultrathink diseña este sistema"
```

Problems realmente complejos. Double thinking = Claude goes extra deep

---

## Flujo Natural Recomendado

**Secuencia que funciona:**

1. **Inicia con contexto** - Usa `@` para archivos relevantes
2. **Ajusta razonamiento** - `Tab` o triggers explícitos según complejidad
3. **Checkpoint antes de cambios** - Protección contra errores
4. **3 intentos máximo** - Después → nueva conversación
5. **Revierte sin miedo** - `ESC ESC` es tu amigo

**Anti-pattern:** Corregir infinitamente sin fresh start. Si 3 intentos no funcionan, el enfoque necesita cambiar.

---

## Referencias

**Framework:**

- [AI-First Workflow](./ai-first-workflow) — Workflows completos
- [Commands Guide](./commands-guide) — 25 comandos
- [Agents Guide](./agents-guide) — 45 specialized agents

**Docs oficiales:**

- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)
- [Extended Thinking](https://docs.claude.com/en/docs/build-with-claude/extended-thinking)

---

::: info Última Actualización
**Fecha**: 2025-10-29 | **Tips**: Claude Code Workflow Optimization
:::
