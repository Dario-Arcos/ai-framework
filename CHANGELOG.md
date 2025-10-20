# Historial de Cambios

Todos los cambios importantes de AI Framework se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

---

## [No Publicado]

### Añadido

- Enable Spanish language for SDD documentation (PR #17)

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
