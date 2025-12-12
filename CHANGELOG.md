# Historial de Cambios

::: tip Keep a Changelog
Todos los cambios importantes siguiendo [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y [Versionado Semántico](https://semver.org/lang/es/).
:::

---

## [No Publicado]

### Añadido

- **Skill dev-browser**: Reemplaza web-browser con arquitectura moderna TypeScript/Bun, servidor Express integrado para snapshots de accesibilidad y navegación persistente (PR #40)
- **Arquitectura team-shared rules**: Sistema dual `docs/claude-rules/` (tracked) + `.claude/rules/` (local), sincronización automática en session-start, reglas compartibles vía git (PR #41)

### Cambiado

- **Comando project-init**: Genera reglas en `docs/claude-rules/` como source of truth, patrón similar a `.env.example` → `.env` (PR #40, #41)
- **Guía AI-First Workflow**: Integración diagramas Mermaid con tema neutral dark/light mode (PR #39)

### Eliminado

- **Skill web-browser**: Reemplazado por dev-browser con arquitectura mejorada (PR #40)

---

## [4.2.0] - 2025-12-08

### Añadido

- **MCP Context7**: Integración de servidor MCP para documentación de APIs en tiempo real, mitiga stale training data al consultar docs oficiales antes de usar dependencias externas (commit 62943ad)
- **Hook SessionEnd**: Sincronización automática con episodic-memory al finalizar sesión (`hooks/episodic-memory-sync.py`), documentación Memory Systems actualizada (PR #36)
- **Infraestructura Mobile E2E Testing**: Agentes `mobile-developer` y `mobile-test-generator`, skill `mobile-testing` con dual-stack (mobile-mcp para debug interactivo + Maestro para E2E), referencias técnicas para Expo/React Native, ejemplos de flujos YAML (PR #38)

### Cambiado

- **CLAUDE.md v4.3.0**: Compliance Certification basada en 6 Killer Items (Objective, Verification, Calibration, Truth-Seeking, Skills-First, Transparency), anti_drift v4.0 alineado, code-reviewer sin model override hardcodeado (PR #34)
- **Discovery Engine (prp-new)**: Rediseño completo del comando con metodología científica Contexto→Problema→Impacto→Oportunidad, eliminados comandos obsoletos `prp-sync` y `speckit.sync` (PR #35)
- **Workflow git-pullrequest**: Auditoría y consolidación skill con 4 ejemplos de flujo completo (success-no-findings, success-with-findings, auto-fix-loop, manual-cancellation), integración receiving-code-review para verificación de fixes (PR #37)
- **Guía AI-First Workflow**: Reescritura completa con diagramas Mermaid, presentación dual-path Superpowers/SpecKit, tema neutral para compatibilidad dark/light mode, integración `vitepress-plugin-mermaid` (PR #39)

### Eliminado

- **Agente memory-search**: Removido en favor de integración directa con MCP episodic-memory (PR #36)
- **Hook core_session_search**: Eliminado, funcionalidad cubierta por MCP episodic-memory (PR #36)

---

## [4.1.0] - 2025-11-27

### Añadido

- **Skill git-pullrequest**: Arquitectura de 3 capas con revisiones paralelas (code-reviewer + security-reviewer + observaciones contextuales), soporte formato corporativo (`tipo|TASK-ID|YYYYMMDD|desc`), loop auto-fix con re-validación obligatoria, 4 ejemplos de flujo completo (PR #32)
- **Template settings**: Modo por defecto cambiado a `plan` (read-only para análisis y planificación) en lugar de `default` (PR #31)

### Cambiado

- ⚠️ **BREAKING**: **Workflow git-pullrequest v2.0** - Paradigma Observaciones Contextuales reemplaza security review con falsos positivos. Eliminado agent ci-cd-pre-reviewer (92 líneas), reducido de 550 a 336 líneas en skill, 3 fases en lugar de 7+ pasos, PR body format actualizado con observaciones. Migrado de comando monolítico a arquitectura skill + wrapper (6 líneas comando) (commits: 348ac12, 29e6006, 9ab0792, b7e3a03)
- **Skill git-pullrequest**: Integración de skills requesting-code-review y receiving-code-review para consistencia con framework, consolidación de findings de 3 fuentes (code + security + observations), detección de secrets movida de observations a security-reviewer para análisis con contexto de explotabilidad (commits: b7e3a03, bbac55a)
- **Handbook (idioma)**: Corrección masiva de inconsistencias idiomáticas español-inglés en 10 archivos (52 correcciones) preservando anglicismos técnicos apropiados - quickstart.md, ai-first-workflow.md, commands-guide.md, agents-guide.md, skills-guide.md, why-ai-framework.md, claude-code-pro-tips.md, mcp-servers.md, memory-systems.md (PR #32: commit f05b037)
- **Handbook (arquitectura)**: Actualización de commands-guide y skills-guide con detalles de arquitectura 3 capas - ejecución paralela de code + security reviews documentada, lista completa de 12 protected branches, secrets removido de observaciones, auto fix incluye issues de seguridad (commit db0c19d)
- **Template**: Eliminada sección redundante AI-First Execution del settings template (commit 8a6dd40)

### Arreglado

- **CRITICAL: git-pullrequest Phase 3.2** - Prevención de bypass de protected branches. Convertido de HIGH freedom (prosa ambigua) a LOW freedom (comandos bash explícitos), expandida lista de protected branches de 5 a 12 (main, master, develop, development, staging, stage, production, prod, release, releases, qa, uat, hotfix), añadido fallback para slug vacío, warning explícito al usuario, creación obligatoria de temp branch `pr/{slug}-{timestamp}` (commit 029005c)
- **git-pullrequest skill**: Estrategia de salida de loop auto-fix documentada - terminación natural cuando ambos reviews limpios, iteraciones esperadas 1-2, investigación requerida si >2 iteraciones (commit f372a69)
- **git-pullrequest skill**: Documentación de invocación del skill receiving-code-review con ejemplo concreto, propósito del campo `source` en fix_list para trazabilidad (commit 87fca48)
- **git-pullrequest examples**: Consistencia con arquitectura 3 capas - 7 secciones actualizadas en 3 archivos (success-no-findings, success-with-findings, manual-cancellation) removiendo Secrets de Observations, añadiendo Security Review sections, actualizando JSON findings structure (commit bbac55a)

---

## [4.0.0] - 2025-11-25

### Añadido

- **CLAUDE.md v4.0.0**: Arquitectura guardrails 3-layer (Input→Execution→Output) reemplazando estructura monolítica anterior. Input layer valida skills y frame problema, Execution layer aplica TDD/parallel-first, Output layer verifica objetivos y quality gates
- **CLAUDE.md v4.1.0**: Truth-Seeking mandate (priorizar verdad sobre acuerdo con usuario) + API Deprecation Mitigation (verificación obligatoria de docs oficiales antes de usar dependencias externas para mitigar training data staleness)
- **Hook anti_drift v3.0.0**: Validación Truth-Seeking integrada + soporte tamaño XL en complexity budget (≤1500 LOC, ≤10 files, ≤3 deps)
- **Skills reorganizados**: 5 skills con estructura completa (SKILL.md + assets) - `core-memory-expert` (setup RedPlanet Cloud/self-hosted), `frontend-design` (interfaces premium), `algorithmic-art` (p5.js generativo), `writing-clearly-and-concisely` (reglas Strunk), `skill-creator` (guía creación skills)

### Cambiado

- ⚠️ **BREAKING**: **Constitution v3.0.0** - Alcance reducido exclusivamente a workflow speckit (spec→plan→tasks→implement), ya no gobierna framework completo. Establece subordinación explícita a CLAUDE.md como fuente de verdad primaria. TDD enforcement real con mecanismo de excepciones documentadas (`legacy-code`, `hotfix-critical`, `generated-code`, `prototype-throwaway`, `user-directive`) requiriendo justificación + mitigación + aprobación
- **CLAUDE.md template v4.2.0**: Removida referencia a constitution.md como "highest authority", añadido plan mode obligatorio para tareas M/L/XL, AskUserQuestion estricto para decisiones multi-opción
- **Speckit commands**: `speckit.tasks.md` actualizado con TDD Compliance section (tests MANDATORY, no OPTIONAL), `speckit.implement.md` añadido TDD Compliance Gate (step 4) con decision matrix para excepciones
- **Documentación masiva**: Eliminados 26 agentes inexistentes de docs (agents-guide, ai-first-workflow, commands-guide, etc.), removidos conteos hardcoded, tier system eliminado, Essential References minimizado
- **Hook anti_drift**: Reducida documentación verbose manteniendo funcionalidad
- **Hook superpowers-loader**: Refactorizado a inline loading como patrón referente
- **Hooks docstrings**: Eliminada verbosidad excesiva, documentado ccnotify para notificaciones
- **CI code review**: Model actualizado de `sonnet` a `opus` para mayor profundidad de análisis
- **Agents references**: Actualizadas referencias en code-reviewer.md y systematic-debugger.md
- **Agent design-iterator**: Reemplaza premium-ux-designer con enfoque iterativo de refinamiento

### Arreglado

- **MCP config template**: Sintaxis args actualizada de array a string format, shebang portable `#!/usr/bin/env python3` en scripts
- **Skills descriptions**: Formato estandarizado a sintaxis "Use when..." para consistencia con Claude Code plugin spec
- **Hook Stop**: Removido prompt hook no funcional que causaba comportamiento errático
- **Docs references**: Corregidas referencias rotas a secciones CLAUDE.md (§3 → §Complexity Budget, etc.)
- **Scripts bash**: Aplicado fix CDPATH desde spec-kit v0.0.85 (check-prerequisites, create-new-feature, setup-plan, update-agent-context)
- **Skill web-browser**: Removido `killall` inseguro, migrado a puerto dedicado 9223 con comando stop explícito

### Eliminado

- **Carpeta `.claude/rules/`**: Eliminados `operational-excellence.md` y `effective-agents-guide.md` - archivos huérfanos que se sincronizaban pero nunca eran leídos por Claude (sin referencias `@`). Contenido ya cubierto por CLAUDE.md

---

::: details Versiones Anteriores

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

:::

---

::: info Última Actualización
**Fecha**: 2025-12-08 | **Versión**: 4.2.0 | **Formato**: Keep a Changelog
:::
