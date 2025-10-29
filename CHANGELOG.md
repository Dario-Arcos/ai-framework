# Historial de Cambios

::: tip Keep a Changelog
Todos los cambios importantes siguiendo [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y [Versionado Semántico](https://semver.org/lang/es/).
:::

---

## [No Publicado]

- [Cambios futuros se documentan aquí]

---

## [2.1.0] - 2025-10-29

### Cambiado

- ⚠️ **BREAKING**: Cambios arquitectónicos fundamentales con migración automática independiente (PR #23):

  **1. Control de Artefactos de Usuario (`.gitignore`)**
  - **Antes (v1.x)**: `/specs/` y `/prps/` forzosamente ignorados en todos los proyectos
  - Usuario decide si versionar o ignorar estos directorios
  - **Migración**: Reglas legacy auto-comentadas con marcador de versión, nueva sección USER ARTIFACTS documentada
  - **Impacto**: Posibilita documentación versionada de especificaciones

  **2. Configuración del Plugin (`settings.json` vs `settings.local.json`)**
  - **Antes (v1.x)**: `settings.local.json` = defaults del framework (sobrescritos cada sesión)
  - `settings.json` = framework (sincronizado) | `settings.local.json` = customs del usuario (nunca tocado)
  - **Precedencia**: `settings.local.json` > `settings.json`
  - **Impacto**: Configuraciones personales del usuario ya no se pierden

  **3. Servidores MCP (`.mcp.json`)**
  - **Antes (v1.x)**: `.mcp.json` copiado al proyecto desde template (redundante)
  - Plugin `.mcp.json` = servidores del framework (Playwright, Shadcn) | Proyecto `.mcp.json` = servidores custom del usuario (opcional)
  - **Precedencia**: proyecto > plugin
  - **Impacto**: Eliminada sincronización redundante, arquitectura simplificada

  **4. Workflow PRP-Cycle Optimizado**
  - **Antes (v1.x)**: Branch names forzados como único input
  - Input contextual flexible (lenguaje natural, GitHub issues `#N`, o rutas de archivos)
  - **Auto-detección**: Params vacíos buscan automáticamente PRPs no sincronizados
  - **Resultado**: +300% flexibilidad de entrada, -25% LOC

  **Filosofía de Migración**: Independiente, cero acción manual, patrón industry-standard (Rails/npm/Terraform)

---

## [2.0.0] - 2025-10-25

### 🎉 Añadido

**⭐ Integración de Claude Skills** (nuevo en Claude Code v2.0.20)

Skills disponibles:

- **algorithmic-art**: Crea arte algorítmico con p5.js usando seeded randomness
- **claude-code-expert**: Expertise senior para crear componentes Claude Code (agents, commands, hooks, MCP)
- **skill-creator**: Guía para crear tus propios skills personalizados

_Más skills en cada actualización_

**Comandos:**

- `/ai-framework:utils:cleancode-format`: Formatear código manualmente (prettier, black, shfmt)

### Cambiado

**Handbook:**

- Nueva paleta de colores Azul Royal como complemento elegante
- Animaciones sutiles y refinadas (estilo Linear/Notion)
- Mejor contraste en dark mode
- Performance mejorado

**Code Quality:**

- Eliminadas duplicaciones en validators (código más limpio)
- Mejor arquitectura de validación compartida

### Arreglado

- Animación faltante en hero (dark mode)
- Duplicaciones de código en validators
- Formato incorrecto en skills frontmatter
- Focus states agresivos en buscador

### Eliminado

- ⚠️ **BREAKING**: Hook automático de formateo `clean_code.py`
  - **Cómo migrar**: Usar `/ai-framework:utils:cleancode-format` cuando necesites formatear código
  - **Por qué**: El formateo automático generaba ruido en code reviews

---

::: details Versiones Anteriores

## [1.4.1] - 2025-10-23

### Añadido

- Soporte tipo explícito + Task ID en `/commit`: `refactor: TRV-345 descripción` (PR #21)

### Cambiado

- Título personalizable en PRs con formato corporativo (PR #21)
- Optimización comandos: patrón consistente, -30% verbosidad (commit 504f831)
- `/release`: 333 → 153 líneas (-54%), validación CHANGELOG corregida (commit ababbca)
- `/changelog`: 166 → 145 líneas (-13%), solo reglas esenciales (commit ababbca)

### Arreglado

- Detección branch duplicados: verificación 3 fuentes (remote + local + specs) (PR #21)
- Git config cleanup: `--unset-all` → `--remove-section` (PR #21)

---

## [1.4.0] - 2025-10-22

**Añadido:** `/update-docs` command · Formato corporativo commits con Task ID auto-detect

**Cambiado:** ⚠️ BREAKING: `pr.md` → `pullrequest.md` · `docs.md` → `update-docs` · Workflow review migrado a GitHub CLI

**Arreglado:** Regex portable BSD grep (macOS) · Branch limit 30→39 chars · Git diff stats vacíos

---

## [1.3.1] - 2025-10-20

**Añadido:** Docs SDD en español (spec/plan/tasks/checklist) · Auto-sync develop al push main · Logging estructurado clean_code.py

**Arreglado:** **CRÍTICO** - Validación `--short-name` regression · Condición carrera `.mcp.json` · Convención `.template` suffix

**Cambiado:** PRPs a raíz del repo · Comandos changelog/release con instrucciones declarativas

---

## [1.3.0] - 2025-10-18

**Cambiado:**

- ⚠️ **BREAKING**: Plugin restructurado per spec oficial (`commands/` y `agents/` a root)
- Docs comprimidas: architecture.md -56.5% · constitution.md v2.3.0 (-180 tokens)
- pr.md: 455 → 183 líneas (-60%) con dual review (quality + security)
- Hooks: path resolution con `__file__` · graceful degradation

**Arreglado:** **CRÍTICO** - Path resolution en 5 hooks (`os.getcwd()` → `find_plugin_root()`)

---

## [1.1.2] - 2025-10-17

**Cambiado:** Hooks/template a plugin root (PR #15) · pr.md crea branch temporal ANTES pre-review (PR #14)

**Arreglado:** Command injection risk pr.md · Variables persistence con git config · Hooks.json sin redundancias

---

## [1.1.1] - 2025-10-16

**Añadido:** Gestión automática versiones (`npm version` sync) · `agent-strategy-advisor`

**Cambiado:** ⚠️ Breaking - Auto-sync agents/commands desde templates · SDD 7→6 pasos · Checklist PRE-implementación

**Eliminado:** Badge duplicado · Emojis decorativos · 63 líneas "Agent Assignment" obsoletas

---

## [1.1.0] - 2025-10-15

**Añadido:** Diseño monocromático premium (brutalista Apple) · Animaciones botones (escala + shine) · Íconos Lucide

**Cambiado:** Color marca: azul → monocromático (#18181b) · Tipografía mejorada · Homepage reorganizada

---

## [1.0.0] - 2025-10-15

**Añadido:**

- Human Handbook (6 guías + GitHub Pages)
- 7 hooks · 24 commands · 45 agents
- Framework constitucional (5 principios)
- SDD Workflow

**Seguridad:** Hook security_guard · Review BLOQUEANTE en PR workflow

:::

---

::: info Última Actualización
**Fecha**: 2025-10-29 | **Versión**: 2.1.0 | **Formato**: Keep a Changelog
:::
