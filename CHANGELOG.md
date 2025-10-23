# Historial de Cambios

Todos los cambios importantes de AI Framework se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

---

## [No Publicado]

### Cambiado

- Comando `/release` optimizado y corregido (commit actual)
  - Reducción: 333 → 153 líneas (54% menos)
  - Eliminadas secciones meta innecesarias (Notas de Implementación, Seguridad, Rollback)
  - Validación corregida: permite CHANGELOG.md modificado (integración con /changelog)
  - Confirmación real con WAIT explícito
  - Orden corregido: CHANGELOG antes de npm version
- Comando `/changelog` optimizado (commit actual)
  - Reducción: 166 → 145 líneas (13% menos)
  - Eliminadas secciones "Principios de Diseño" y "Notas" verbosas
  - Solo 3 reglas esenciales

---

## [1.4.1] - 2025-10-23

### Añadido

- Soporte para tipo explícito con Task ID en comando `/commit` (PR #21)
  - Formato: `refactor: TRV-345 descripción` (tipo sobrescribe auto-mapping)
  - Prioridad: tipo explícito > auto-mapping desde archivos
  - Pattern detection automático: `type: TASK-ID description`

### Cambiado

- Título personalizable en PRs con formato corporativo (PR #21)
  - Pregunta interactiva cuando detecta commits corporativos
  - Opciones: usar primer commit o ingresar título custom
  - Validación de formato corporativo con fallback
- Documentación de comandos optimizada con formato consistente (commit 504f831)
  - Patrón "Casos de Uso" + "¿Qué hace?" aplicado
  - Reducción de verbosidad: 30% promedio
  - 8 comandos optimizados (commit, pullrequest, cleanup, specify, clarify, plan, tasks, implement)
- Comando `/release` optimizado y corregido (commit ababbca)
  - Reducción: 333 → 153 líneas (54% menos)
  - Eliminadas secciones meta innecesarias (Notas de Implementación, Seguridad, Rollback)
  - Validación corregida: permite CHANGELOG.md modificado (integración con /changelog)
  - Confirmación real con WAIT explícito
  - Orden corregido: CHANGELOG antes de npm version
- Comando `/changelog` optimizado (commit ababbca)
  - Reducción: 166 → 145 líneas (13% menos)
  - Eliminadas secciones "Principios de Diseño" y "Notas" verbosas
  - Solo 3 reglas esenciales

### Arreglado

- Detección de números de branch duplicados en entornos de equipo (PR #21)
  - Verificación de 3 fuentes: remote branches + local branches + specs directories
  - Previene conflictos cuando múltiples developers crean features simultáneamente
  - Pattern matching exacto para evitar falsos positivos
- Limpieza de git config estandarizada en `pullrequest.md` (PR #21)
  - Cambio de `--unset-all` a `--remove-section` (4 ubicaciones)
  - Fix consistente en todas las secciones de rollback

---

## [1.4.0] - 2025-10-22

### Añadido

- Comando `/update-docs` para actualización automatizada de documentación project-agnostic (PR #20)
- Formato corporativo de commits en comando `/commit` con detección automática de Task ID (PR #19)
  - Template: `Tipo|IdTarea|YYYYMMDD|Descripción`
  - Detección automática de patrones (TRV-345, PROJ-123, etc.)
  - Fallback a conventional commits si no hay Task ID

### Documentación

- Sincronización de referencias al comando `pullrequest` en handbook (PR #20)
- Guía de comandos actualizada con cambios recientes en workflow git (PR #20)
- Ejemplos de help con placeholders de fecha en lugar de valores hardcodeados (PR #20)
- Justificación de timeout documentada en commands-guide.md (PR #20)
- Refinamiento de mensajería arquitectónica y flujo de instalación en README (PR #19)

### Cambiado

- ⚠️ **BREAKING**: Comando `pr.md` renombrado a `pullrequest.md` (PR #20)
- ⚠️ **BREAKING**: Eliminado `docs.md`, reemplazado por `update-docs` portable (PR #20)
- Comando `changelog` optimizado con compatibilidad bash 3.2 (POSIX test, grep -E) (PR #20)
- Comando `update-docs` completamente project-agnostic (sin hardcoded paths) (PR #20)
- Workflow de review en CI migrado a GitHub CLI (PR #19)
- Interfaz de handbook simplificada removiendo efectos sobre-diseñados (PR #19)

### Arreglado

- Regex portable compatible con BSD grep en `pullrequest.md` (macOS) (PR #20)
- Límite de caracteres de branch corregido (30→39 chars) en `pullrequest.md` (PR #20)
- Validación de stats vacíos en git diff (PR #20)
- Extracción de body completo de PR en comando changelog (antes solo título) (PR #19)
- Sincronización de regla `/prps/` entre template y hook session-start (PR #19)
- Sincronización de `plugin.json` en proceso de versioning (PR #19)

---

## [1.3.1] - 2025-10-20

### Añadido

- Generación de documentación SDD en español (spec.md, plan.md, tasks.md, checklist.md) (PR #17, #18)
- Sincronización automática de develop al hacer push a main vía workflow CI (PR #18)
- Logging estructurado en hook clean_code.py (PR #18)

### Arreglado

- **CRÍTICO**: Regresión en validación de --short-name en create-new-feature.sh (permite valor faltante) (PR #18)
- Adopción de convención de sufijo .template en hook session-start (PR #18)
- Condición de carrera en .mcp.json en hook session-start (PR #18)

### Cambiado

- Directorio PRPs reubicado a raíz del repositorio (mejora organizacional) (PR #18)
- Comando changelog: eliminada lógica bash, usa instrucciones declarativas (PR #18)
- Comando release: eliminada lógica bash, usa instrucciones declarativas (PR #18)
- Comandos refactorizados siguiendo patrón de estructura de pr.md (PR #18)

---

## [1.3.0] - 2025-10-18

### Añadido

- Path resolution robusto en todos los hooks con múltiples estrategias de fallback
- Graceful degradation en hooks de logging (continúan funcionando sin project root)

### Cambiado

#### 🏗️ Arquitectura y Estructura (PR #16)

- **BREAKING**: Plugin restructurado según especificación oficial de Claude Code
  - `commands/` y `agents/` movidos a plugin root (69 archivos)
  - `.claude-plugin/` solo contiene metadata (plugin.json, marketplace.json)
  - Elimina jerarquía falsa, simplifica descubrimiento de comandos
- Hook architecture: todos los hooks usan path resolution confiable con `__file__` (no `os.getcwd()`)
- Hook fallbacks: logging a stderr cuando project root no disponible (graceful degradation)
- `.mcp.json` removido de gitignore de usuario (evita commits inadecuados de framework)
- Directorio `.claude.template` deprecado y removido

#### 📖 Documentación Comprimida (PR #16)

- **architecture.md**: 480 → 209 líneas (-56.5%)
  - Elimina redundancias con CLAUDE.md
  - Constitution retiene autoridad estratégica; CLAUDE.md retiene detalles tácticos
  - Sincronización de impacto documentada en header
- **constitution.md**: comprimido para eficiencia de tokens (v2.2.0 → v2.3.0)
  - Artículos fundamentales preservados
  - Detalles tácticos movidos a CLAUDE.md
  - Elimina ~180 tokens de redundancia
- **project-init**: optimizado para eficiencia de tokens sin perder contexto crítico
- **operational-excellence.md**: renamed from governance guide (mayor claridad)

#### 🎯 Comandos Optimizados (PR #16)

- **pr.md**: 455 → 183 líneas (-60%)
  - Dual review implementado (code quality + security review pre-launch)
  - Audit fixes y mejoras en validaciones
  - Separación clara de responsabilidades
  - `/changelog` y `/release` ahora son comandos separados (antes unificados)
- Guía de agentes efectivos (context engineering) integrada y referenciada
- Hojas de ruta documentadas para cada comando crítico

#### 🔐 Mejoras de Seguridad (PR #16)

- **security_guard hook**: feedback claro y accionable para violaciones
- **pre-tool-use hook**: rediseño para transparencia (eliminadas black boxes)
- **clean_code hook**: transformado de black box a formato transparente y auditable

#### 🚀 Características Nuevas (PR #16)

- **Execution Principles** añadidos a CLAUDE.md (objectivity, minimalism, communication, planning, implementation, validation)
- **security_guard improvements**: validaciones más granulares con mensajes de error específicos
- Separation de `/changelog` y `/release` como comandos independientes
  - `/changelog`: auto-detecta PRs, actualiza CHANGELOG, commitea
  - `/release`: bump versión, crea tag, crea release GitHub

### Arreglado

- **CRÍTICO**: Path resolution en 5 hooks (session-start, security_guard, ccnotify, minimal_thinking, pre-tool-use)
  - ❌ Bug: `os.getcwd()` no confiable cuando Claude Code ejecuta desde diferentes directorios
  - ❌ Bug: Logs/databases iban a ubicaciones incorrectas en proyectos anidados
  - ✅ Fix: `find_plugin_root()` usando `__file__` (100% confiable)
  - ✅ Fix: `find_project_root()` con búsqueda upward robusta + fallbacks
- Bug en loop de búsqueda upward en ccnotify.py y minimal_thinking.py
- session-start.py: fallback a `find_plugin_root()` si CLAUDE_PLUGIN_ROOT no existe
- security_guard.py: graceful degradation (no exceptions, logging a stderr)
- Pre-tool-use hook: arquitectura correcta (tool_input modification, no stdout context injection)

---

## [1.1.2] - 2025-10-17

### Añadido

- Workflow de GitHub Pages se dispara automáticamente con cambios en CHANGELOG.md

### Cambiado

- Plugin structure: hooks/ y template/ movidos a plugin root per especificación oficial (PR #15)
- Plugin configuration: eliminada redundancia en marketplace.json, versión sincronizada (PR #15)
- Command workflow: pr.md crea branch temporal ANTES de pre-review (permite correcciones) (PR #14, #15)
- Template naming: archivos framework usan sufijo .template para instalación (PR #14)

### Arreglado

- Security: command injection risk en pr.md (sanitización de pr_title, --body-file) (PR #15)
- Reliability: persistencia de variables en pr.md usando git config (PR #15)
- Configuration: hooks.json sin matchers innecesarios, sin timeouts redundantes (PR #15)
- Gitignore: rutas actualizadas /hooks/ (PR #15)
- Complexity: simplificación de commands pr.md, changelog.md, cleanup.md, commit.md (PR #14)
- Documentation: errors de parser Vue en VitePress (PR #13)
- Plugin: unificación agents/commands a patrón template-based (PR #12)
- Documentation: eliminación de agent-assignment obligatorio (PR #10, #11)
- Documentation: mejoras de calidad y gestión de versiones (PR #9)

---

## [1.1.1] - 2025-10-16

### Añadido

- Gestión automática de versiones con `npm version` (sincroniza package.json, docs, README)
- Componente de comparación de versiones en documentación
- Comandos opcionales: `/analyze`, `/checklist`, `/sync` con guía de uso
- `agent-strategy-advisor` para recomendaciones de agentes

### Cambiado

- ⚠️ Breaking: Sincronización automática de agents/commands desde templates (respaldar personalizaciones antes de actualizar)
- Workflow SDD simplificado: 7 → 6 pasos (eliminado agent-assignment obligatorio)
- Checklist reposicionado a PRE-implementación (valida specs, no código)

### Eliminado

- Badge de release duplicado en homepage
- Emojis decorativos en docs (conservados solo funcionales)
- 63 líneas de documentación obsoleta sobre "Agent Assignment"
- Referencias a `agent-assignment-analyzer` (ahora `agent-strategy-advisor`)

### Arreglado

- Errores de parsing Vue en VitePress (sintaxis de placeholders)
- Comportamiento documentado de `speckit.specify` (crea branch, no worktree)
- Precisión en documentación del workflow (numeración, conteos, terminología)
- Cálculo de complejidad constitucional (clasificación L-size correcta)

---

## [1.1.0] - 2025-10-15

### Añadido

- Sistema de diseño monocromático premium (estética brutalista inspirada en Apple)
- Animaciones premium en botones (escala + shine con easing Apple)
- Íconos Lucide: terminal.svg, zap.svg
- Grid de features balanceado (2x2, 4 tarjetas)

### Cambiado

- Color de marca: azul GitHub → monocromático (#18181b)
- Tipografía mejorada (font-weight 800, letter-spacing -0.5px)
- Homepage reorganizada (enfoque en propuesta de valor)

### Seguridad

- Revisión de seguridad aprobada (score 0.95)
- Activos SVG verificados como seguros

---

## [1.0.0] - 2025-10-15

### Añadido

- Documentación Human Handbook en GitHub Pages
- 6 guías completas: Quickstart, AI-First Workflow, Commands, Agents, Pro Tips, MCP
- Matriz de decisión Branch vs Worktree
- Diagramas de workflow (Mermaid)
- 7 lifecycle hooks (Python)
- 24 slash commands en 4 categorías
- 45 agentes especializados en 11 categorías
- Framework de gobernanza constitucional (5 principios no negociables)
- Workflow Specification-Driven Development (SDD)

### Cambiado

- Sintaxis de comandos usa namespace completo del plugin
- Terminología: PRD-cycle → PRP-cycle
- Workflow SDD-Cycle documentado (9 pasos completos)

### Arreglado

- Comportamiento de `speckit.specify` (crea branch, no worktree)
- Sintaxis de comandos (191 referencias corregidas)
- Conteo de agentes (45, no 44)

### Seguridad

- Hook `security_guard.py` bloquea 5 patrones críticos
- Revisión de seguridad BLOQUEANTE en workflow de PR
