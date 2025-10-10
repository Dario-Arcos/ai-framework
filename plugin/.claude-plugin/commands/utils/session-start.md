---
allowed-tools: Read(*), Bash(git *), Bash(gh *), LS(*)
description: Configura workspace leyendo CLAUDE.md, verificando estado git y mostrando opciones de desarrollo
---

# Session Start

Configura workspace automáticamente según especificaciones del proyecto.

## Ejecución

Cuando ejecutes este comando, sigue estos pasos:

### 1. Bienvenida e inicialización

Mostrar exactamente este texto:

```
*Configurando workspace...*

```

### 2. Leer configuración del proyecto

- Ejecutar: `Read` en `/CLAUDE.md` para obtener configuraciones específicas
- Ejecutar: `Read` en `/.claude/settings.json` para verificar configuración de permisos (sin mostrar output)

### 3. Establecer contexto actual

- Ejecutar: `pwd` para detectar si estamos en worktree (contiene "worktree-")
- Ejecutar: `git status --porcelain` para ver cambios pendientes
- Ejecutar: `current_branch=\`git branch --show-current\`` para capturar rama actual
- Ejecutar: `git fetch --quiet 2>/dev/null` para actualizar referencias remotas (ignorar errores)

### 3.5. Sincronización proactiva con remoto

**Verificar upstream y sincronizar:**

- Ejecutar: `git config "branch.$current_branch.remote" > /dev/null 2>&1`
- Capturar exit code: `has_upstream=$?`

**Intentar sincronización (solo si rama tiene upstream y nombre válido):**

- Si `has_upstream = 0` Y `current_branch` no está vacío:
  - Ejecutar: `git pull --ff-only origin "$current_branch" 2>&1`
  - Capturar exit code: `sync_status=$?`
- Si `has_upstream != 0` O `current_branch` está vacío: asignar `sync_status=2` (rama sin upstream o detached HEAD)

**Mostrar resultado:**

- Si `sync_status = 0`: agregar a output del paso 4: "✅ Sincronizado con origin/$current_branch"
- Si `sync_status = 1`: agregar a output del paso 4: "⚠️ No se pudo sincronizar $current_branch - verificar: git status"
- Si `sync_status = 2`: agregar a output del paso 4: "ℹ️ Rama local sin upstream remoto"

**IMPORTANTE:**

- NO bloquear ejecución si sincronización falla
- Continuar con pasos 4-8 normalmente

### 4. Mostrar situación del trabajo actual

- Ejecutar: `gh issue list --assignee @me --state open --limit 6` si gh está disponible
- Si comando falla, mostrar: "ℹ️ GitHub CLI no disponible"
- Si exitoso y hay issues:
  - Mostrar header: "🎯 **Tu situación actual:**"
  - Agregar: "📍 Branch: [rama actual] | Estado: [limpio/[X] cambios pendientes]"
  - Agregar línea vacía
  - Agregar: "Tienes [número] Github issues activos:"
  - Para issues 1-5: mostrar cada uno como "• #[número] [título]"
  - Si hay 6 o más: agregar línea "• Ver todos en: github.com/[owner]/[repo]/issues/assigned"
  - Agregar línea vacía después
- Si exitoso y no hay issues:
  - Mostrar: "🎯 **Tu situación actual:**"
  - Agregar: "📍 Branch: [rama actual] | Estado: [limpio/[X] cambios pendientes]"
  - Agregar línea vacía
  - Agregar: "✓ No tienes issues asignados - workspace limpio para nuevas tareas"
  - Agregar línea vacía después

### 5. Protocolo de trabajo

**SI NO estamos en worktree (pwd no contiene "worktree-")**, mostrar:

```
⚙️ **Workflow:**
Para desarrollo, usamos worktrees para mantener branches limpias:

1. Crear worktree: /worktree:create <purpose> <parent-branch>
2. Cambiar directorio: cd ../worktree-<purpose>
3. Nueva sesión Claude: claude /utils:session-start

Comandos típicos:
/worktree:create feature-auth develop     # Feature desde develop
/worktree:create fix-payment-bug main     # Hotfix desde main
/worktree:cleanup worktree-feature-auth   # Limpiar al terminar
```

**SI YA estamos en worktree (pwd contiene "worktree-")**, mostrar:

```
✓ Ya estás en worktree - listo para desarrollo
```

### 6. Decisión asistida

**SI NO estamos en worktree**, mostrar:

```
🤔 **¿Cuál es tu objetivo para esta sesión?**

- **Desarrollo/bugs/refactor** → ¡Crea worktree primero! ⬆️
- **Solo Análisis/Docs** → Continúa aquí
```

**SI YA estamos en worktree**, mostrar:

```
🤔 **¿Cuál es tu objetivo para esta sesión?**

- **Desarrollo/bugs/refactor** → Continúa aquí ✓
- **Cambiar tarea** → Crea nuevo worktree
```

### 7. Recomendación crítica de sincronización

**Solo mostrar si `sync_status != 0` (sincronización falló o no aplicó):**

```
🚨 Si vas a hacer cambios, verifica estar sincronizado:
• git pull (si tu rama tiene upstream configurado)
• Resuelve cualquier conflicto antes de comenzar

Esto previene conflictos costosos y garantiza código actualizado.
```

### 8. Alerta de seguridad final

- Si el archivo settings.json leído en paso 2 contiene `"defaultMode": "bypassPermissions"`:
  - Mostrar: "⚠️ BYPASS PERMISSIONS ACTIVO - Claude tiene acceso completo al sistema sin restricciones. **Entorno seguro requerido.** Para restringir: defaultMode: 'default' o 'acceptEdits' en settings.local.json."
- Si el archivo no existe o falló lectura: no mostrar nada

**IMPORTANTE**:

- Ejecutar pasos 1-8 secuencialmente sin confirmación del usuario
- Si algún paso falla, continuar con warning pero no terminar
- Mantener output conciso y actionable
- Las restricciones del paso 5 NO se muestran al usuario, están solo como recordatorio interno
