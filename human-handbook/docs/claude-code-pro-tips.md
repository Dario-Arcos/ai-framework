# Claude Code Pro-Tips

_Guía técnica para fluir naturalmente con Claude Code_

## ⚡ Quick Reference

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

## 🧠 Control de Razonamiento Extendido

Sistema de razonamiento con niveles progresivos de profundidad.

### Niveles

| Nivel          | Uso                                                        |
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

**Toggle** - Presiona `Tab` para activar/desactivar durante sesión

## 📁 Referencias Rápidas con @

Referencia archivos o directorios sin esperar a que Claude los lea.

**Sintaxis**:

```text
@src/utils/auth.js revisa esta implementación
@src/components analiza todos los componentes
compara @src/old-auth.js con @src/new-auth.js
```

**Ventajas**: Inmediato, preciso, eficiente con scope de git.

## ⏮️ Navegación Temporal

Claude Code guarda checkpoints antes de cada edición.

### Revertir

**`ESC ESC`** (2 veces) o **`/rewind`** abre menú con 3 opciones:

- **Conversation only**: Retrocede mensaje, mantiene código
- **Code only**: Revierte archivos, mantiene conversación
- **Both**: Reset completo a checkpoint

### Casos de Uso

```bash
# Explorar alternativa
[implementación A]
ESC ESC → Code only
[implementación B]

# Recuperar error
[cambios incorrectos]
ESC ESC → Both

# Iterar features
[versión 1]
ESC ESC → Conversation only
```

**Limitaciones**: No trackea bash commands, solo sesión actual, no reemplaza git.

---

## 🔄 Gestión de Conversaciones

### La Regla del Ciclo Negativo

**Problema**: Corregir repetidamente al LLM crea ciclo negativo de retroalimentación.

**Por qué**: Contexto completo (incluyendo errores) se usa como entrada. Cada corrección añade "ruido". LLM persevera en error al intentar "complacer" correcciones.

### Regla de las 3 Correcciones

```text
Intento 1: Resultado incorrecto → Corregir
Intento 2: Aún incorrecto → Corregir con más contexto
Intento 3: Sigue incorrecto → STOP
```

**En intento 3, no sigas corrigiendo:**

1. Usa `/rewind` si error fue reciente
2. Inicia nueva conversación con contexto claro
3. Reformula el problema - quizás instrucción fue ambigua

### Anti-Pattern: "Maldecir" al LLM

❌ **No hagas**:

```text
"No, eso está mal"
"Te dije que no hicieras eso"
"¿Por qué no entiendes?"
```

✅ **Haz**:

```text
ESC ESC → Both
[Nueva conversación]
"Necesito implementar X. Contexto: Y. Restricciones: Z."
```

### Cuándo Empezar de Nuevo

**Indicadores**:

- 3+ correcciones sin progreso
- LLM repite mismo error
- Respuestas confusas o inconsistentes
- Cambio significativo de dirección

**Template para nueva conversación**:

```text
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

## ⚙️ Control de Permisos

4 modos de permisos:

| Modo                | Comportamiento                            |
| ------------------- | ----------------------------------------- |
| `default`           | Pide confirmación para acciones sensibles |
| `acceptEdits`       | Auto-acepta ediciones de archivos         |
| `bypassPermissions` | Bypass total (CI/CD)                      |
| `plan`              | Solo planifica, no ejecuta                |

### Cambiar Modo

**`Shift+Tab`**: Cicla entre modos

**Configuración persistente** en `.claude/settings.json`:

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

| Contexto         | Modo                | Razón            |
| ---------------- | ------------------- | ---------------- |
| Desarrollo Local | `acceptEdits`       | Flujo rápido     |
| CI/CD            | `bypassPermissions` | Automatización   |
| Exploración      | `plan`              | Ver sin ejecutar |
| Producción       | `default`           | Control manual   |

⚠️ **Precaución**: `bypassPermissions` elimina TODAS las confirmaciones. Solo para automatización.

---

## 🔍 Análisis de Pull Requests

Claude Code integra con GitHub CLI:

```bash
# Análisis conversacional directo
"Analiza el PR #210 y evalúa los hallazgos objetivamente"
"Revisa los comentarios del PR actual y sugiere qué corregir"
```

**Capacidades**:

- Consulta estado, comentarios, checks via `gh pr view`
- Evalúa hallazgos críticamente (validez técnica, contexto, ROI)
- Aplica correcciones y commitea cambios

**Workflow**:

```text
1. "Analiza PR #210"     → Claude usa gh para datos
2. Claude presenta evaluación crítica
3. "Corrige X e Y"       → Aplica solo fixes confirmados
4. Claude commitea con /git-github:commit
```

---

## 🚀 Workflow Optimization

### Validación de Contexto

Antes de comandos críticos:

```bash
git branch    # ¿Branch correcto?
pwd           # ¿Directorio correcto?
git status    # ¿Cambios pendientes?
```

### Checkpointing Proactivo

Antes de cambios grandes:

```bash
git add .
git commit -m "checkpoint: antes de refactor X"
[realizar cambios con Claude Code]
# Si falla: git reset --hard HEAD
```

### Uso de Ecosistema

**Agentes especializados**: @agents-guide.md (45 agentes)
**Comandos disponibles**: @commands-guide.md (22 comandos)
**Workflows completos**: @ai-first-workflow.md

---

## 💡 Tips Finales

### Combinaciones Poderosas

**ultrathink + @directorio**

```text
ultrathink analiza la arquitectura de @src/core
```

**ESC ESC + nueva conversación**

```text
[resultado no deseado]
ESC ESC → Both
[nueva conversación con contexto limpio]
```

**Tab + thinking explícito**

```text
Tab (activar razonamiento)
"ultrathink diseña este sistema"
```

### Flujo Natural

1. **Inicia con contexto** - Usa `@` para archivos relevantes
2. **Ajusta razonamiento** - `Tab` o triggers explícitos según complejidad
3. **Checkpoint antes de cambios** - Protección contra errores
4. **3 intentos máximo** - Después → nueva conversación
5. **Revierte sin miedo** - `ESC ESC` es tu amigo

---

📚 **Más guías**: @ai-first-workflow.md · @commands-guide.md · @agents-guide.md
📖 **Docs oficiales**: [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) · [Extended Thinking](https://docs.claude.com/en/docs/build-with-claude/extended-thinking)

---

_Última actualización: 2025-10-06 | Claude Code Pro-Tips_
