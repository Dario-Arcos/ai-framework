# Historial de Cambios

Todos los cambios importantes de AI Framework se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

---

## [No Publicado]

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
