# Historial de Cambios

::: tip Keep a Changelog
Todos los cambios importantes siguiendo [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y [Versionado Semántico](https://semver.org/lang/es/).
:::

---

## [No Publicado]

- [Cambios futuros se documentan aquí]

---

## [3.1.0] - 2025-11-12

> **⚠️ CRÍTICO - REINSTALACIÓN OBLIGATORIA**
>
> Esta versión requiere **BORRAR completamente el plugin** y reinstalarlo desde cero. **NO es suficiente actualizar**.
>
> **Proceso de migración:**
> ```bash
> # 1. Remover plugin actual
> /plugin marketplace remove ai-framework
> /plugin uninstall ai-framework@ai-framework
>
> # 2. Reinstalar desde marketplace
> /plugin marketplace add Dario-Arcos/ai-framework
> /plugin install ai-framework@ai-framework-marketplace
>
> # 3. Restart Claude Code
> ```
>
> **Razón**: La estructura flat de comandos/agents requiere reinstalación limpia para aplicar correctamente la nueva arquitectura de nombres.

### Añadido

- Documentación completa de Memory Systems con guías de setup para Team Memory y Episodic Memory, comparativa técnica detallada (knowledge graph vs vector search), guía de decisión problem-first, y troubleshooting para problemas comunes (PR #28, #29, #30)
- Comando `/setup-episodic-memory` para instalación y configuración automatizada de episodic-memory plugin con validación de dependencias y setup hooks (PR #29)
- Recomendación de procesamiento completo inicial en documentación de episodic-memory con comando `index-conversations --cleanup --concurrency 8` para indexar todas las conversaciones inmediatamente
- Estructura disciplinaria completa en 4 skills custom (browser-tools, claude-code-expert, skill-creator, algorithmic-art) con Core Principle, Iron Law, When to Use/NOT to Use, Red Flags, Common Rationalizations y Real-World Impact alineados al patrón superpowers
- Sección CRÍTICA en browser-tools skill explicando uso imperativo cuando WebFetch/WebSearch son insuficientes para research profundo multi-página

### Cambiado

- ⚠️ **BREAKING**: Estructura de plugin aplanada - commands y agents movidos de estructura jerárquica a flat (27 commands, 47 agents) con nombres explícitos en frontmatter para invocación simple sin namespace
  - Antes: `/ai-framework:utils:setup-dependencies`, `/ai-framework:systematic-debugger`
  - Ahora: `/setup-dependencies`, `/systematic-debugger`
  - Migración: Actualizar scripts/aliases que usen comandos antiguos
- Configuración MCP optimizada con modelo opt-in por defecto - solo Playwright habilitado inicialmente, shadcn/core-memory/team-memory requieren habilitación explícita vía `enabledMcpjsonServers` en settings
- Método de instalación de episodic-memory migrado de npm install a plugin marketplace para instalación zero-dependency
- Sidebar del handbook reorganizado con Memory Systems en Guides (conceptual) y MCP Servers en Tools (técnico) para mejor organización mental (PR #30)
- Template `.mcp.json` simplificado con documentación inline clara sobre configuración de servidores HTTP vs command-based
- Comando `/git-pullrequest` mejorado con workflow user-centric: reviews completos visibles antes de decisiones, fix automático guiado issue-by-issue vía AskUserQuestion, sin bloqueos automáticos (usuario controla todo), optimizado 590 → 507 líneas (-14%) (PR #28)
- Documentación actualizada globalmente (128+ cambios) para reflejar nueva estructura flat de comandos y agentes
- Skills guide rediseñado con UX premium usando componentes VitePress (tabs, cards, custom containers) para mejor navegabilidad

### Arreglado

- Hook session-start corregido para prevenir falsos positivos en detección de reglas gitignore con lógica mejorada de pattern matching
- Detección de episodic-memory en hooks con lógica denylist corregida para evitar errores de configuración
- Namespace de skills corregido de `superpowers:` a `ai-framework:` para consistencia con plugin name
- Consistencia de lenguaje en browser-tools skill (Español para secciones de usuario, English para código)
- Workflow develop-mirror corregido usando git reset en lugar de merge para mantener sincronización limpia con main

### Eliminado

- Hook Stop removido debido a comportamiento errático que causaba ejecuciones impredecibles
- Archivo `.mcp.json` del plugin eliminado en favor de template approach para evitar sobrescritura de configuración de usuario
- Directorio `docs/plans/` removido de tracking git (debe estar gitignored)

---

## [3.0.0] - 2025-11-09

### Añadido

- **Skill browser-automation**: Control Chrome/Chromium vía CDP con Puppeteer API completo para E2E testing, network interception, performance profiling, coverage analysis y scraping. Incluye tools (`start.js`, `nav.js`, `eval.js`, `screenshot.js`, `stop.js`) con setup npm install one-time. Soporte macOS only (paths específicos + rsync) (PR #26)
- **Hook anti_drift v2**: Sistema mejorado con precedencia CLAUDE.md, exception handling específico y validación de constitutional compliance. Reemplaza `minimal_thinking` con arquitectura robusta (PR #26)
- **Superpowers Skills (19 skills)**: Integración completa de skills de desarrollo profesional - **Testing**: test-driven-development, condition-based-waiting, testing-anti-patterns | **Debugging**: systematic-debugging, root-cause-tracing, verification-before-completion, defense-in-depth | **Collaboration**: brainstorming, writing-plans, executing-plans, dispatching-parallel-agents, requesting-code-review, receiving-code-review, using-git-worktrees, finishing-a-development-branch, subagent-driven-development | **Meta**: sharing-skills, testing-skills-with-subagents, using-superpowers. Proveen workflows estructurados para desarrollo AI-first (PR #27)
- **Comandos Superpowers**: Slash commands para workflows de planificación colaborativa - `/brainstorm` (refinamiento iterativo de ideas rough), `/write-plan` (creación de planes de implementación comprehensivos), `/execute-plan` (ejecución controlada de planes en batches). Integrados en `commands/superpowers/` para acceso directo desde CLI (PR #27)
- **Agente ci-cd-pre-reviewer**: Validación pre-deployment especializada en production readiness, CI/CD pipelines y release gates. Complementa code-reviewer para workflow dual-review (PR #27)
- **Agente code-reviewer**: Integrado desde superpowers, combina alineación con plan + quality review en un solo agente (92 líneas). Reemplaza code-quality-reviewer con funcionalidad extendida (PR #27)
- **Guía "Por Qué AI Framework"**: Documentación comprehensiva explicando value proposition, arquitectura constitucional, diferenciadores y casos de uso. Incluye comparativa con alternativas y filosofía de diseño (PR #27)
- **Paleta Slate Graphite**: Colores grises azulados fríos (Slate-900 a Slate-200) para diseño sobrio y profesional en docs. Reemplaza royal blue/purple con gradientes visibles y animados. Estilo Stripe/Tailwind/Vercel (PR #27)

### Cambiado

- ⚠️ **BREAKING**: MCP servers deshabilitados por defecto para optimización de contexto. Solo Playwright habilitado inicialmente, shadcn/core-memory/team-memory requieren opt-in explícito vía `enabledMcpjsonServers` en `settings.json.template`. Migración: usuarios existentes mantienen config (PR #26)
- **Workflow pullrequest**: Implementa dual-review paralelo (code-reviewer + security-reviewer) con blocking automático en vulnerabilidades HIGH confidence ≥0.8. Simplifica estructura workflow de 455 → 350 líneas (PR #27)
- **Skill renombrada browser-tools**: Anteriormente browser-automation, renombrada para reflejar naturaleza tooling. Archivos movidos `skills/browser-automation/` → `skills/browser-tools/` manteniendo funcionalidad completa. Actualizada documentación en skills-guide.md (PR #27)
- **README streamlined**: Reducido de ~400 → 276 líneas (-124 LOC), removida verbosidad innecesaria, agregada sección Why con enlace a guía comprehensiva. Estructura más directa: Features → Install → Quick Start → Why → License (PR #27)
- **Hook anti_drift v2.0.2**: Optimizado orden checklist para eficiencia (validación constitutional primero, luego operational), mejorada claridad mensajes de error (PR #27)
- **Separación docs Skills vs MCPs**: Secciones independientes en handbook con awareness de context budget. Skills en `skills-guide.md`, MCPs en `mcp-servers.md` con explicación diferencias y uso apropiado (PR #26)
- **Docs plugin management**: Mejora quickstart con instrucciones claras de instalación, configuración y troubleshooting. Incluye tips para context optimization (PR #26)

### Arreglado

- **Path hardcodeado usuario**: Removido path `/Users/dariarcos/` hardcoded en browser-automation skill, reemplazado con paths relativos y variables de entorno. Previene fallos en instalaciones multi-usuario (PR #26)
- **Exception handling anti_drift**: Reemplazados bare except clauses por tipos específicos (`FileNotFoundError`, `JSONDecodeError`) en hook anti_drift, mejora debugging y previene catch-all bugs (PR #26)

### Eliminado

- **Comando /ultrathink**: Removido `commands/utils/ultrathink.md`, funcionalidad migrada a slash command del framework base. Referencias eliminadas de handbook y guides (PR #27)
- **Agente code-quality-reviewer**: Reemplazado por code-reviewer (superpowers integration) que provee funcionalidad equivalente + plan alignment en un solo agente. Actualizado pullrequest.md y referencias (PR #27)

---

::: details Versiones Anteriores

## [2.2.0] - 2025-11-04

### Añadido

- **Skill core-memory-expert**: Setup automatizado para RedPlanet Core (Cloud <2min, self-hosted vía Docker), incluye REST API reference, Spaces CLI, agent templates y troubleshooting completo (PR #24)
- **Hooks Core Memory**: Búsquedas automáticas de contexto en SessionStart (3 queries optimizadas) y UserPromptSubmit (patrón oficial Core), con agente memory-search para retrieval de team memory (PR #25)
- **Protocolo de Verificación de Contexto**: Artículo VII §6 de la Constitución - mandato de búsqueda exhaustiva en Core Memory + docs locales antes de implementación (PR #25)
- **Tip Plan Mode avanzado**: Recomendación concisa en pro-tips para usar plan mode con `ultrathink` en features complejas, pattern Think→Plan→Review→Execute (PR #25)

### Cambiado

- ⚠️ **BREAKING**: `template/.claude.template/settings.json.template` - `defaultMode` cambió de `bypassPermissions` a `default` para mayor seguridad. Usuarios que requieran bypass: configurar en `.claude/settings.local.json` (PR #25)
- **MCP servers por defecto**: Solo Playwright habilitado inicialmente (minimal footprint), shadcn/core-memory/team-memory opt-in vía `enabledMcpjsonServers` (PR #24)
- **Team Memory como local config**: Movido de `.mcp.json` a `.claude/.mcp.json` (gitignored) para prevenir exposición de tokens, documentado setup en mcp-servers.md (PR #24)
- **Skill claude-code-expert optimizado**: Eliminada redundancia y verbosidad, condensado de 163 → 105 líneas (PR #24)

### Arreglado

- **Exposición de credenciales**: Removida flag `--openai-key` CLI en setup self-hosted (prevenía exposición en shell history), agregado `chmod 600` a `.env`, actualizada SKILL.md - severity HIGH, confidence 0.95 (PR #24)
- **Gaps Core Memory skill**: Token format corregido `sk-` → `rc_pat_`, documentado que `spaceIds` API no funciona (4 tests confirmaron), clarificado team sharing (Changelog vs Reality), agregado workaround team-core-proxy (PR #24)
- **Dead code hooks**: Removida función `find_project_root()` sin usar y imports innecesarios en `core_prompt_search.py` (-23 líneas) (PR #25)
- **Exception handling**: Bare except clauses reemplazadas por tipos específicos en `core_session_search.py` (líneas 41, 67) (PR #25)
- **.specify/ tracking**: Removido `constitution.md` del tracking git (debería estar solo en `template/.specify.template/`) (PR #25)

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

- `/cleancode-format`: Formatear código manualmente (prettier, black, shfmt)

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
  - **Cómo migrar**: Usar `/cleancode-format` cuando necesites formatear código
  - **Por qué**: El formateo automático generaba ruido en code reviews

---

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

---

:::

::: info Última Actualización
**Fecha**: 2025-11-09 | **Versión**: 3.0.0 | **Formato**: Keep a Changelog
:::
