---
outline: 2
---

# Changelog

Registro de cambios del framework, organizado por versión siguiendo [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y [CalVer](https://calver.org/) `YYYY.MINOR.MICRO`.

---

## [No Publicado]

### Añadido

- `HOOK_VERSION` ahora deriva de `package.json` (`_read_hook_version()` con `lru_cache`), alineando telemetría y manifiesto.
- `_SDD_DISABLE_SCENARIOS=1` como bypass real de los guards de escenarios (`sdd-test-guard.py` + `_enforce_scenario_gate` en `task-completed.py`), con evento `scenarios_bypassed` emitido en cada invocación.

### Cambiado

- `docs/migration-to-scenarios.md` y `skills/ralph-orchestrator/references/quality-gates.md`: se elimina el descargo "no cableado" y se documentan las tres superficies de configuración del bypass.
- `hooks/hooks.json` `PreToolUse.matcher`: removido `MultiEdit` (herramienta legacy ausente en la referencia oficial actual de Claude Code). Matcher final: `Edit|Write|NotebookEdit|TaskUpdate|Bash`.
- `skills/ralph-orchestrator/references/quality-gates.md`: añadida tabla de citas a la documentación oficial Claude Code (Phase 7 C7) — 16 claims verificadas vía `claude-code-guide` sub-agent.

## [2026.4.0] - 2026-04-16

### Añadido

- Scenario-driven development gate (Phase 3): `.claude/scenarios/` write-once artifacts enforced via PreToolUse guards + task-completed gate.
- Scenario parser/validator module (`hooks/_sdd_scenarios.py`) with amend marker protocol.
- Stack-agnostic Tier-2 config (`.claude/config.json`) for `SOURCE_EXTENSIONS`, `TEST_FILE_PATTERNS`, `COVERAGE_REPORT_PATH`.
- `project-init` Layer 6 auto-generates `.claude/config.json` from detected manifest.
- PASS_TO_PASS validation recording (Phase 4.1): every completion records the `SCEN` IDs validated this session.
- Scenario quality validator (Phase 4.2): soft warnings for single-anchor scenarios, identical When/Then, missing Evidence.
- Tautological test detection (Phase 4.3): blocks `assert True`, `expect(true).toBe(true)`, empty test bodies on Edit/Write.
- Critical-paths signaling (Phase 4.4): `.claude/critical-paths.md` triggers non-blocking warnings on sensitive file edits.
- Git-history recovery protection (Phase 4.5): baseline anchors on the file's first add commit, not `HEAD` — defeats `git checkout HEAD~N` attacks.
- Telemetry (Phase 5): `.claude/metrics.jsonl` with rotation, `[SDD:CATEGORY]` failure prefixes, structured logging helper.

### Cambiado

- `sdd-test-guard.py` PreToolUse matcher extended: `Edit|Write|MultiEdit|NotebookEdit|TaskUpdate|Bash`.
- `task-completed.py` scenarios-first gate runs BEFORE the existing gate loop. Coverage is demoted to an informational signal when scenarios pass.
- `_sdd_state.py` runner lock uses a stable lockfile separate from the PID file (closes the TOCTOU split-brain found in the Phase 2 Codex review).
- `_sdd_detect.py` reduced to facade (`1357 → 294 LOC`, `-79%`).

### Arreglado

- Phase 0 hardening: `record_file_edit` atomic via separate lockfile; narrow except tuples; `UnicodeDecodeError` handling across file readers.
- Phase 1 hardening: config validation against bare strings and malformed regex; cascade cache invalidation across `lru_cache`s.
- Phase 3 hardening: symlink/hardlink bypass of write-once guard closed; quoted filename bypass closed; `ln` added to Bash scenario write regex; `clear_coverage` called before `_fail_task` to avoid stale state.

### Security

- Pragmatic threat model documented (SPEC §3.5). Known out-of-scope bypasses (arbitrary Python scripts, direct skill-state writes) are now explicit in module docstrings.

### Cambiado

- **Hook coverage gate — diff-coverage del runner reemplaza basename pairing**: `compute_uncovered` ahora prefiere evidencia positiva de cobertura (líneas ejecutadas según el reporte del test runner) sobre ausencia de evidencia (heurística de archivos sibling). Detección runtime stack-agnóstica desde `package.json`/`pyproject.toml`/`go.mod`/`Cargo.toml` — vitest, jest, c8, pytest-cov, go-cover, cargo-llvm-cov soportados sin configuración por proyecto. Alineado con [diff-cover](https://github.com/Bachmann1234/diff_cover) y SWE-bench. Cierra el vector de reward hacking donde un test file vacío satisfacía el gate.
- **Hook subagent-start — skill index dinámico**: la lista de skills inyectada a sub-agentes se deriva del filesystem en cada invocación en lugar de estar hardcoded. Skills añadidas o removidas se reflejan inmediatamente. Skills con `SKILL.md` vacío se excluyen.

### Arreglado

- **Hook task-completed — false positives en proyectos sin basename pairing**: `compute_uncovered` consultaba solo los archivos editados en la sesión actual, ignorando tests que ya existían en disco. Proyectos con convenciones módulo-level (`apps/web/__tests__/modules/personas.test.ts` cubriendo `apps/web/app/personas/**/*`) recibían bloqueos espurios. Ahora `compute_uncovered` consulta `has_test_on_disk` como segundo paso, y prefiere el reporte de cobertura del runner cuando está disponible.
- **Hook subagent-start — drift de skills en sub-agentes**: sub-agentes general-purpose veían un catálogo de skills hardcoded de 14 entradas mientras el directorio `skills/` contenía 23, ocultando skills nuevas y listando algunas removidas.

### Añadido

- **`detect_coverage_command(cwd)`**: detección runtime del comando de cobertura del proyecto desde manifest. Returns `(cmd, format, path)` o `None`. Soporta lcov (universal) y go-cover (Go nativo).
- **`parse_lcov(path)` y `parse_go_cover(path)`**: parsers stdlib-only de los formatos de cobertura más universales. Tolerantes a registros malformados.
- **Mensajes diagnósticos en coverage gate**: cuando un archivo se reporta como no cubierto, el mensaje indica qué método de detección se usó (lcov report en `<path>` vs basename heurístico fallback) y sugiere resoluciones específicas. Trunca a 10 archivos con indicador "and N more".

---

## [2026.3.1] - 2026-03-16

### Cambiado

- **Hooks cross-platform Windows**: Reemplazar `_run.sh` (bash-only) con polyglot `_run.cmd` (CMD+bash) — hooks, statusline y notificaciones ahora funcionan en Windows sin requerir bash. Patrón superpowers: una ruta con comillas + nombre de script (commit `1271d13`)
- **Statusline standalone**: Extraer Python de heredoc en `statusline.sh` a `statusline.py` standalone + wrapper `statusline.cmd` — misma funcionalidad, cross-platform (commit `1271d13`)
- **SOP defaults desacoplados de `.ralph/`**: Rutas por defecto en 5 SOPs cambian `.ralph/specs/` → `docs/specs/`. Reglas gitignore user-decidable (`/.ralph/`, `/.research/`) ya no se re-inyectan en session-start — viven solo en gitignore.template (commit `eeb442e`)
- **Template gitignore**: Añadir `/.brainstorm/`, `/.visual-companion/`, y `/docs/specs/` a gitignore.template (commits `294dcc8`, `6e3a202`)

### Arreglado

- **Scripts ESM compat**: Renombrar `server.js` → `server.cjs` en brainstorming y frontend-design — `"type": "module"` en package.json causaba error al cargar scripts CommonJS (commits `45bad57`, `6e3a202`)

---

## [2026.3.0] - 2026-03-14

### Añadido

- **Visual Companion en brainstorming y frontend-design**: Servidor local con preview HTML, WebSocket live reload, y selección interactiva en browser — cada skill con scripts propios (aislamiento completo) (commit 80006db)
- **Spec Review Loop en brainstorming**: Subagente reviewer valida specs con prompt dedicado antes de user review gate, max 5 iteraciones (commit 80006db)
- **Plan Review Loop en sop-planning**: Subagente reviewer valida planes + sección File Structure antes de implementation plan (commit 80006db)
- **Testing anti-patterns en scenario-driven-development**: Referencia a patrones de testing problemáticos (mocks, test-only production methods, test doubles incompletos) (commit 80006db)
- **Condition-based waiting example en systematic-debugging**: Implementación TypeScript de `waitForEvent`, `waitForEventCount`, `waitForEventMatch` (commit 80006db)

### Cambiado

- **Reescribir brainstorming con Superpowers v5**: Observable Scenarios Bridge (brainstorming→SDD), hard gate pre-implementación, proceso con spec review loop y visual companion (commit 80006db)
- **Reescribir systematic-debugging con Superpowers v5**: Dot diagrams en referencias, Phase 1 expandida, referencias actualizadas (commit 80006db)
- **Estandarizar 15 descriptions de skills (CSO)**: Formato trigger + purpose, eliminar patterns Value/Skip risk de descriptions — info preservada en body (commit 80006db)
- **Refactorizar constraint-reinforcement hook**: Pointer-based activation (35 tokens) reemplaza verbose repetition (65 tokens) con wrapper `<EXTREMELY_IMPORTANT>` — activación sobre repetición (commit 0e1410c)
- **Actualizar identity en CLAUDE.md template**: "Combined rigor of a senior engineering team", resistencia a retracción por comfort (commit 0e1410c)
- **Serializar test gate en TaskCompleted con flock**: Prevenir pytest concurrente entre sdd-auto-test y TaskCompleted hook, `write_state` con `raw_output` (PR #53)

### Arreglado

- **Stale references en human-handbook**: Skill count 24→23, Superpowers v5 skill list, atribución correcta SDD/debugging como nativos, workflow con SDD + verification (commit 4486075)
- **Paths de visual-companion en skills**: Plugin-root paths (`skills/<name>/visual-companion.md`) consistentes con patrón upstream (commit 7e9631b)

---

## [2026.2.1] - 2026-03-14

### Añadido

- **Hook agent-browser skill sync**: Sincronizar 4 skills de agent-browser (agent-browser, dogfood, electron, vercel-sandbox) a `~/.claude/skills/` — antes solo copiaba agent-browser (PR #51)
- **Hook PGID-based orphan kill**: Registrar PGID de test subprocess en archivo para kill scoped del grupo huérfano exacto — reemplaza pkill indiscriminado que mataba procesos de sesiones paralelas (PR #51)
- **Hook SDD temp cleanup**: Purgar archivos `sdd-*` en tempdir mayores a 24h en SessionStart para prevenir acumulación de inodes (PR #51)
- **Context /dogfood gate**: Integrar /dogfood como QA exploratorio obligatorio en constraint 13 de CLAUDE.md ("claim web/mobile works") y en 5 skills (frontend-design, scenario-driven-development, verification-before-completion, sop-code-assist, sop-reviewer) (PR #51)
- **Docs agent-browser skills**: Documentar tabla de skills agent-browser (dogfood, electron, vercel-sandbox) en skills-guide, integrations, y ai-first-workflow (PR #51)

### Cambiado

- **Hook agent-browser update**: Reescribir mecanismo de actualización — `npm install -g agent-browser@latest` incondicional con dedup 5min reemplaza cooldown 24h que silenciaba fallos. Stderr capturado en log (`2>&1`) en vez de silenciado (`2>/dev/null`) (PR #51)
- **Hook constraint-reinforcement**: Reescribir texto de refuerzo — cubrir 7/11 constraints de CLAUDE.md (era 3/11), añadir formato literal `/skill-name`, añadir constraints de pre-training y scenarios+satisfaction (~65 tokens, bajo límite 400) (commit `93d1a7e`)
- **Template CLAUDE.md**: Comprimir constraints (~38 tokens menos), fusionar línea haiku/sonnet en "opus only", añadir prefijo `/` a todas las 10 referencias de skills, integrar /dogfood en constraint 13 y workflow (PR #51, commit `93d1a7e`)
- **Agents edge-case-detector y performance-engineer**: Eliminar restricción `tools: Read, Grep, Glob, Task` — permitir implementar fixes además de analizar (commit `c8d5d16`)

### Arreglado

- **Hook chrome-headless-shell orphans**: Añadir `pkill -P 1 -f chrome-headless-shell` en Phase 3 de cleanup — mata solo orphans reales (PPID=1), no chrome activo de sesiones paralelas (PR #51)
- **Hook PGID stale file**: Limpiar archivo PGID después de test exitoso — prevenir SIGKILL a proceso equivocado por reciclaje de PID del OS (PR #51)
- **Hook cross-platform process kill**: Reemplazar `os.killpg`/`SIGKILL` (POSIX-only) con `_kill_process_tree`/`_kill_pgid` — dispatch a `taskkill /T /F` en Windows, `killpg` en POSIX. Capturar `subprocess.TimeoutExpired` además de `OSError` (PR #51)
- **Hook Windows shell paths**: Usar `.as_posix()` para paths embebidos en comandos bash — prevenir backslashes interpretados como escapes en Git Bash (PR #51)
- **Docs README hooks table**: Corregir tabla — eliminar hook ghost (memory-check.py), añadir hooks faltantes (constraint-reinforcement, subagent-start), corregir descripción de MCP server (commit `c8d5d16`)

---

## [2026.2.0] - 2026-03-11

### Añadido

- **Hook constraint-reinforcement**: Añadir refuerzo constitucional en recency zone en cada prompt del usuario (UserPromptSubmit) — contrarresta dilución de atención en conversaciones largas (~55 tokens inyectados) (commit `c752197`)
- **Hook subagent-start**: Inyectar registro de skills en sub-agentes (SubagentStart) para que puedan invocar skills sin que el padre pase la lista manualmente (commit `3679a45`)
- **Hooks cross-platform Windows**: Añadir wrapper `_run.sh` con fallback python3→python y flag -B, condicionalizar `fcntl` con fallback no-op, usar `tempfile.gettempdir()` en lugar de `/tmp/` hardcoded. Todos los hooks ruteados via `bash _run.sh HOOK.py` (commit `3fd6204`)
- **Hook SDD session isolation**: Añadir estado session-scoped para teammates paralelos — coverage, baseline, skill tracking y trust validation aislados por sesión. Estado project-scoped (test results, PID, rerun marker) para coordinación entre teammates (commit `89a24c2`)
- **Hook SDD coalescing runner**: Añadir ejecución background con trailing-edge coalescing (1 runner máximo por proyecto), flock-based locking (TOCTOU-safe), rerun markers, y timeouts adaptativos basados en duración histórica de tests (commit `68ebeed`)
- **Hook SDD coverage enforcement**: Registrar ediciones source/test por sesión y detectar archivos sin tests en TaskCompleted — "reward hacking by omission" bloqueado (commit `a405c8a`)
- **Hook SDD precision detection**: Detectar downgrade de precisión de assertions (assertEqual→assertTrue) incluso cuando el conteo se mantiene — bloquear weakening semántico como reward hacking (commit `3d83606`)
- **Hook SDD baseline comparison**: Escribir baseline write-once al inicio de sesión para distinguir fallos preexistentes de regresiones nuevas — evitar deadlock por fallos heredados (commit `89a24c2`)
- **Hook SDD skill enforcement**: Requerir invocación de sop-code-assist (o sop-reviewer para rev-* teammates) antes de completar tarea. Gate de coverage valida que source files tengan tests correspondientes (commit `7c938a0`)
- **Hook SDD ordering guard**: Bloquear escritura a source files cuando no existe test file editado en la sesión y no hay test en disco para el archivo (commit `3d83606`)
- **Hooks subprocess validation**: Añadir 27 tests de validación real — contrato hooks.json (scripts existen, matchers compilan, timeouts coherentes), compliance gaps (assertion weakening, detección de archivos), 6 flujos E2E, y 4 thresholds de performance (commits `21fc0ff`, `1fd5fa7`)
- **Skill skill-creator**: Reescribir con sistema eval/benchmark — evals paralelos (con-skill vs baseline), grading cuantitativo, agregación de varianza, viewer HTML, y optimización de descriptions para triggering (commit `a3a5886`)
- **Skill deep-research**: Rediseñar como motor SOP con patrón STORM (investigación multi-perspectiva), protocolo anti-alucinación, routing Context7/agent-browser, y artefactos persistentes en `.research/` (commit `e6ac4ce`)
- **Template spinner tips**: Añadir 4 tips contextuales en español durante tiempos de espera del spinner (commit `a0193a4`)
- **Docs quickstart**: Añadir guía de auto-update para plugin marketplace con proceso step-by-step (commit `f9b0eb3`)

### Cambiado

- **Template CLAUDE.md**: Reescribir constraints con formato NEVER-first para máxima activación LLM, comprimir identidad, simplificar workflow a cadena única (brainstorming→plan mode→SDD→verification), eliminar tabla skill-routing (absorbida por constraints) (commit `344cb7c`)
- **Skill humanizer**: Añadir guía de voz en español con 6 directrices, 69 líneas de referencia con ejemplos before/after, y paso anti-AI audit explícito. Proceso expandido de 5 a 10 pasos con detección de idioma y ciclo draft/audit/rewrite (commit `a77cd61`)
- **Skill brainstorming**: Reemplazar escritura de design docs markdown + git commit con flujo EnterPlanMode/ExitPlanMode. Plan file ahora tiene secciones estructuradas (Context, Design, Observable Scenarios, Blast Radius, Verification) (commit `bc0ddce`)
- **Skill sop-code-assist**: Separar Step 4 en Implementation + Validate. Validación ahora incondicional con 4 agentes en paralelo (code-reviewer + code-simplifier + edge-case-detector + performance-engineer). Añadir Review Alignment Check y runtime validation via agent-browser (commits `4f81e49`, `d4b647a`)
- **Skill verification-before-completion**: Endurecer contra evasión — verificación de estabilidad (re-run obligatorio), ciclo red-green para regression tests, verificación independiente de claims de sub-agentes, scope expandido a paráfrasis e implicaciones de éxito (commit `8780fe5`)
- **Skill SDD**: Expandir Quality Integration de 2 a 4 agentes en paralelo (+ edge-case-detector + performance-engineer) (commit `8780fe5`)
- **Skill descriptions**: Reescribir descriptions de 20+ skills con formato "Value: [beneficio]. Skip risk: [consecuencia]" para mejorar precisión de triggering (commit `6efb409`)
- **Hook task-completed**: Eliminar validación scenario-strategy y tracking de métricas. Añadir gates de coverage, skill enforcement, y baseline comparison. Reusar estado de auto-test con trust validation (ahorro 30-120s). Eximir sub-agentes regulares del gate de completion (commit `e4ef515`)
- **Hooks context noise**: Silenciar session-start en éxito (era "AI Framework: checkmark"), agent-browser excepto en fallo de instalación, auto-test reporta solo fallos, eliminar nudge de coverage de PostToolUse (commits `485d7af`, `4a3af24`)
- **Hooks hooks.json**: Consolidar 3 entradas SessionStart en 1, expandir matcher PostToolUse a `Edit|Write|Skill`, rutear todos los hooks via _run.sh (commit `582d510`)
- **Hooks _sdd_detect performance**: Añadir lru_cache a project_hash, file-based cache con TTL+mtime para detect_test_command, deduplicar ~90 líneas con helpers genéricos de I/O JSON (commit `6600d62`)
- **Agents edge-case-detector y performance-engineer**: Añadir segundo ejemplo para mejorar triggering, clarificar scope boundaries entre correctness y performance, añadir commit log al contexto (commit `81e2bac`)

### Eliminado

- **Hook memory-check**: Eliminar detección automática de staleness de project rules en SessionStart — usar `/project-init` manualmente cuando la estructura del proyecto cambie (commit `1ecf83f`)
- **Skill using-ai-framework**: Eliminar skill de routing redundante — lógica absorbida por constraints de CLAUDE.md template ("Skills precede all work") (commit `7bc82de`)

### Arreglado

- **Hook adaptive_gate_timeout**: Corregir espiral de timeout en cold-start — default=60→120 alineado con worker background para prevenir que el gate mate la primera ejecución antes de escribir estado (commit `8f7c889`)
- **Hook rerun marker**: Corregir gap de coalescing — escribir marker antes del debounce check para que workers en ejecución detecten edits que llegan durante el test run (commit `8f7c889`)
- **Hook PID debounce**: Reemplazar check PID-only con flock de proyecto — eliminar race condition TOCTOU en concurrencia de teammates (commit `321bfc3`)
- **Hook orphan processes**: Añadir process group isolation via os.killpg para prevenir acumulación de procesos pytest/node huérfanos que consumen CPU (commit `82c2b9a`)
- **Hook stale failure counter**: Añadir TTL de 2h a failures.json en teammate-idle para prevenir triggers fantasma del circuit breaker por failures de ejecuciones anteriores (commit `89f0a70`)
- **Hook sub-agent deadlock**: Eximir sub-agentes regulares (non-ralph) del gate de completion en TaskCompleted — fix deadlock donde tareas interdependientes se bloquean mutuamente (commit `aab9509`)
- **Hook try/catch anti-pattern**: Añadir `try/catch` que traga excepciones como anti-patrón explícito en detección de precision de assertions (commit `b203bcd`)
- **Hook fork bomb prevention**: Añadir `_SDD_RECURSION_GUARD` para prevenir fork bomb cuando sdd-auto-test.py se re-invoca a sí mismo como subprocess (commit `79b1d94`)
- **Hook file-existence guard**: Añadir guard de existencia de archivo para prevenir ENOENT bloqueando todas las operaciones Edit/Write cuando CLAUDE_PLUGIN_ROOT apunta a path stale (commit `93c8eb1`)
- **Hook research task bypass**: Saltar enforcement SDD para tareas de research/planning sin ediciones de source files — prevenir bloqueos falsos en tareas de investigación (commit `3b373bf`)
- **Hook cwd resolution**: Usar CLAUDE_PROJECT_DIR como fuente primaria de cwd en todos los hooks — corregir resolución incorrecta en contexto de plugin (commit `f700e07`)
- **Skills ralph quality gates**: Corregir documentación incorrecta que implicaba que gates podían saltarse con scenario-strategy `not-applicable` — todos los gates corren incondicionalmente (commit `4f81e49`)
- **Skills YAML frontmatter**: Corregir parseo de descriptions con caracteres especiales — unificar quoting en frontmatter YAML de 20+ skills (commits `74701de`, `b903f92`)

---

## [2026.1.1] - 2026-02-19

### Añadido

- **Hook task-completed `validate_scenario_strategy()`**: Añadir safety net contra misclasificación de Scenario-Strategy — detectar archivos fuente en git diff cuando tarea marcada `not-applicable`, usando lógica invertida (allowlist de non-code). Incluye 19+ tests con mocks de ambos diffs (uncommitted + last commit) (commit `ae01a23`)
- **Skill project-init**: Añadir tabla Field Ownership que asigna hogar canónico a conceptos compartidos (test command → conventions, paradigms → project, boundaries → architecture) para eliminar redundancia cross-file. Añadir sección Versioning en conventions.md template (commit `e604132`)

### Cambiado

- **Skill pull-request**: Reescribir — eliminar dependencia de skill `receiving-code-review` (verificación ahora inline con protocolo READ→STUDY→VERIFY→EVALUATE→DECIDE→TEST), externalizar PR body template a `references/pr-body-template.md`, separar auto-fix en dos scopes (`all` y `blockers only`), forzar `git add <files>` explícito (commit `9d5dbe7`)
- **Skill commit**: Simplificar parseo a 3 componentes (type, task ID, description), forzar staging por path explícito excluyendo archivos sensibles — eliminar `git add -A` (commit `08cf8a5`)
- **Cadena de skills**: Integrar humanizer como quality gate de prosa obligatorio en brainstorming, deep-research y changelog. Añadir tablas Artifact Handoff en 4 skills (brainstorming → SDD → verification). Añadir sección `<skill-routing>` en CLAUDE.md template con tabla explícita de enrutamiento (commit `4282997`)
- **Agent code-simplifier**: Generalizar — reemplazar estándares hardcoded (ES modules, React Props, arrow functions) por referencia dinámica al CLAUDE.md y rules del proyecto (commit `4282997`)
- **README**: Reescribir para reflejar estado actual — eliminar lenguaje promocional, añadir tablas completas de skills (17), agents (6) y hooks (9), documentar metodología SDD (commit `3dbbc6f`)
- **Project rules (.claude/rules/)**: Actualizar versionado semver → CalVer, eliminar conteos hardcoded de agents/skills, documentar hooks PreToolUse/PostToolUse en data flow (commit `f786dec`)

### Arreglado

- **Hook task-completed**: Corregir parseo de Scenario-Strategy con HTML comments del template (`<!-- required | not-applicable -->`) — strip comment antes de evaluar (commit `ae01a23`)
- **Skill sop-code-assist**: Corregir escritura concurrente a `.ralph/guardrails.md` — Edit (append) en lugar de Write (overwrite) para teammates simultáneos (commit `4282997`)
- **Docs pro-tips**: Corregir defaults de effort level (medium → high), jerarquía de modelos (sonnet → opus), workflow de recuperación (auto-checkpoints reemplazan git checkpoint manual) (commit `4243aa2`)
- **Docs quickstart**: Corregir compatibilidad de plataformas — Linux marcado como full support, 4 SDD hooks documentados como POSIX-only con limitaciones Windows (`fcntl`, `/tmp/`) (commit `f47e278`)
- **Docs why-ai-framework**: Reemplazar diagrama Mermaid cortado por componente HTML stepper con CSS nativo VitePress (commit `a89e813`)

---

## [2026.1.0] - 2026-02-16

> **⚠️ MAJOR UPGRADE — Migración requerida desde v5.x**
>
> Esta versión reestructura la arquitectura completa del framework: metodología (TDD→SDD), invocación (commands→skills), orquestación (shell loop→Agent Teams), y enforcement (prescriptivo→empírico). 10 breaking changes documentados con guía de migración.

### Añadido

- **Skill scenario-driven-development**: Metodología SDD (Scenario→Satisfy→Refactor) con puertas de convergencia, principios anti-reward-hacking, y validación de comportamiento observable — reemplaza TDD como metodología core del framework (commit `d086eb8`)
- **Skill context-engineering**: Tres leyes de entrega de contexto (pasivo > activo, índice > inline, recuperar > recordar), gestión de attention budget, y estrategias long-horizon — gate obligatorio para modificar archivos de contexto (commit `45b731f`)
- **Skill verification-before-completion**: Gate de completitud evidence-based con 6 pasos y detección de reward hacking pre-completitud (commit `65c6693`)
- **Skill systematic-debugging**: 4 fases (Root Cause→Pattern Analysis→Hypothesis Testing→Implementation) con escape hatch arquitectural tras 3+ intentos fallidos, incluye sub-técnicas condition-based-waiting, defense-in-depth, root-cause-tracing y script find-polluter.sh (commit `65c6693`)
- **Skill sop-reviewer**: Validador SDD para tareas con 5 gates (compliance, acceptance criteria, behavioral satisfaction, reward hacking, structured output) — integrado con ralph-orchestrator para revisión autónoma (commit `ab39b2b`)
- **Skill skill-creator**: Meta-skill para creación de skills con anatomía, progressive disclosure, grados de libertad, y 3 scripts Python de scaffolding (commit `c35cab2`)
- **Skill using-ai-framework**: Primer de enrutamiento de skills con tabla de red flags y prioridades de invocación (commit `1797abe`)
- **Skill commit**: Migrar lógica de command a skill con soporte de formatos corporativos (task ID parsing) y estrategia multi-commit por categoría (commit `ea45eae`)
- **Skill changelog**: Migrar a skill con workflow de 9 fases, rúbrica de calidad, protocolo de breaking changes con severidad, y reglas de análisis de diff (commit `520d99d`)
- **Skill deep-research**: Migrar a skill con protocolo anti-alucinación, 4 fases de ejecución, investigación primaria vía agent-browser, y validación cruzada con 3+ iteraciones (commit `ea45eae`)
- **Skill project-init**: Migrar a skill con 5 capas de análisis, gate de context engineering (subtraction test, attention budget), detección de staleness, y diff reporting para actualizaciones (commit `55bc5b5`)
- **Skill branch-cleanup**: Migrar de command a skill con protección de branches vía regex, `--ff-only` safety, y auto-detección de branch base (commit `ea45eae`)
- **Skills worktree-create y worktree-cleanup**: Migrar de commands a skills auto-contenidos (commit `ea45eae`)
- **Sistema de project memory**: 4 archivos auto-generados en `.claude/rules/` (project.md, stack.md, architecture.md, conventions.md) — conocimiento estructurado que sobrevive context compaction (commit `3c0cc5a`)
- **Hook memory-check**: Detección de staleness de project memory en SessionStart con 4 niveles y hashing de contenido para eliminar falsos positivos (commit `4ac84f7`)
- **Hook sdd-auto-test**: Lanzar tests en background tras cada edición de código fuente (PostToolUse) con feedback continuo de resultados — implementa loop de retroalimentación SDD (commit `7a06618`)
- **Hook sdd-test-guard**: Bloquear ediciones que reducen assertions en test files cuando tests fallan — prevención de reward hacking (PreToolUse) (commit `7a06618`)
- **Hook task-completed**: Gate de calidad para Agent Teams con gates ordenados (test, typecheck, lint, build, integration, e2e, coverage) y tracking de failures por teammate (commit `d90fc12`)
- **Hook teammate-idle**: Safety net con detección de archivo ABORT y circuit breaker tras N failures consecutivos (commit `7a06618`)
- **Módulo _sdd_detect.py**: Biblioteca compartida SDD — detección de test commands (npm, pytest, go, cargo, make), parsing de output (TAP, Jest, Vitest, pytest, Go, cargo), e I/O atómico vía `/tmp/` (commit `4291a6b`)
- **Test suites para hooks**: 9 archivos, 230+ tests cubriendo todos los hooks — incluyendo 43 escenarios de integración SDD (commit `b5495d9`)
- **Ralph pipeline parallelism**: Ejecución paralela de tareas independientes con detección de overlap de archivos y regla de tarea lanzable (commit `f828cb2`)
- **Ralph GATE_INTEGRATION y GATE_E2E**: Gates de calidad de primera clase para integración y end-to-end (commit `73edd51`)
- **Memoria persistente en agentes**: Atributo `memory: user` en los 6 agentes core para acumulación de conocimiento cross-sesión (commit `393864d`)
- **Handbook página Ralph Orchestrator**: Documentación dedicada con arquitectura, prerequisites y guía de uso (commit `030e2a8`)
- **Hero animation**: Componente HeroDither.vue con animación cascade para landing page del handbook (commit `75862d3`)

### Cambiado

- ⚠️ **BREAKING**: **Metodología TDD → SDD** — Scenario-Driven Development reemplaza TDD como core del framework. Escenarios observables antes de código, tests como herramienta (no autoridad), prohibición explícita de reward hacking. Migración: definir escenarios de usuario antes de escribir tests, usar `/scenario-driven-development` (commit `d086eb8`)
- ⚠️ **BREAKING**: **Directorio `commands/` eliminado** — 15 commands migrados a skills o eliminados. Migración: invocar skills directamente (`/commit`, `/changelog`, `/pull-request`, `/deep-research`, etc.) (commit `ea45eae`)
- ⚠️ **BREAKING**: **Ralph orchestrator reescrito con Agent Teams** — `loop.sh` (789 líneas), `status.sh`, `tail-logs.sh`, `truncate-context.sh` eliminados. Ejecución ahora in-process con teammates efímeros (200K contexto fresco por tarea). Requiere `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Migración: eliminar `loop.sh` del proyecto, usar `/ralph-orchestrator` desde sesión activa (commits `8a8b97b`, `a23702a`)
- ⚠️ **BREAKING**: **CLAUDE.md template rediseñado** — de 301 líneas (manual prescriptivo con ROI scoring, graphviz, complexity budgets, compliance certification) a 37 líneas (constitución con `<constraints>`, `<identity>`, `<workflow>`, `<communication>`). Migración: regenerar con `/project-init` (commit `989dead`)
- ⚠️ **BREAKING**: **Template `.mcp.json` eliminado** — Context7 reubicado a plugin.json. Mobile-mcp y maestro eliminados. Migración: configurar MCP servers directamente en proyecto si se necesitan (commit `3a91ef0`)
- ⚠️ **BREAKING**: **Hooks lifecycle events reestructurados** — `UserPromptSubmit` y `SessionEnd` eliminados. `PreToolUse` cambiado de security scanning a SDD test guard. Nuevos eventos: `PostToolUse`, `TaskCompleted`, `TeammateIdle`. Migración: eliminar hooks personalizados que dependan de anti_drift o security_guard (commit `7a06618`)
- ⚠️ **BREAKING**: **Gitignore template reducido** — de 121 líneas (kitchen sink) a 12 líneas (solo framework-specific). `.claude/rules/` ahora versionable. Migración: mantener reglas genéricas en gitignore propio del proyecto (commit `3a91ef0`)
- ⚠️ **BREAKING**: **Skill pr-workflow → pull-request** — renombrado para consistencia. Migración: actualizar invocaciones de `/pr-workflow` a `/pull-request` (commits en rango)
- ⚠️ **BREAKING**: **Settings template: Tasks y Agent Teams habilitados** — `CLAUDE_CODE_ENABLE_TASKS`, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, `MAX_MCP_OUTPUT_TOKENS` añadidos. `MAX_THINKING_TOKENS` eliminado. Permisos `WebFetch` removidos (todo web vía agent-browser). `FILE_READ_MAX_OUTPUT_TOKENS` reducido de 200K a 100K (commit `c35cab2`)
- ⚠️ **BREAKING**: **Ralph config variables renombradas** — `QUALITY_LEVEL`, `CONFESSION_MIN_CONFIDENCE` → `GATE_TEST`, `GATE_TYPECHECK`, `GATE_LINT`, `GATE_BUILD`, `GATE_INTEGRATION`, `GATE_E2E`, `GATE_COVERAGE`, `MAX_TEAMMATES`, `MODEL`. `AGENTS.md` movido a `.ralph/agents.md` (commits `e193dd1`, `5455cff`)
- **Agentes consolidados de ~20 a 6**: edge-case-detector reescrito (+113% — 4 fases, 5 categorías, 20+ patrones, confidence scoring), performance-engineer reescrito (+446% — taxonomía 3-tier con 16 patrones), code-reviewer con SDD compliance gate y detección de reward hacking (commits `f1bce96`, `51c15d1`, `bc94991`)
- **Ralph simplificado de 3 capas a 2**: Lead (orquestador puro) + teammates efímeros (implementers y reviewers). Eliminada rotación de coordinadores. Un teammate = una tarea = contexto fresco (commit `a23702a`)
- **Ralph execution runbook**: Artefacto generado post-aprobación de plan que sobrevive context compression con registro de tareas, gates, y prompts inlined (commit `16f2c71`)
- **SOP skills alineados con SDD**: sop-code-assist, sop-discovery, sop-planning, sop-reverse, sop-task-generator actualizados con validación de escenarios, agent-browser para research, y containment de filesystem (commits `a9617b7`, `adb72ae`, `c47e7fc`)
- **Hook session-start simplificado**: Eliminada migración legacy de gitignore y lógica de scan compleja. Añadido patrón `/.claude/*` + `!/.claude/rules/`. Reducido ~320 a ~170 líneas (commit `2edad9e`)
- **Hook agent-browser-check reescrito**: Limpieza de daemons huérfanos, sync de skill a nivel usuario (`~/.claude/skills/`), cooldown anti-retry storms (commit `da354be`)
- **Hook notify.sh reescrito**: Parsing JSON, sonidos distintos por tipo (Funk/Purr/Pop/Tink), prevención de loop infinito, escaping AppleScript (commit `9c92fec`)
- **Statusline.sh optimizado**: De 6-9 invocaciones `jq` a single pass. Branch/worktree detection consolidado (commit `2edad9e`)
- **Plugin.json**: keyword `tdd` → `sdd`, Context7 MCP registrado en plugin manifest (commit `d086eb8`)
- **Handbook ai-first-workflow**: Reescrito con metodología SDD y estructura por fases (commit `0113e52`)
- **Handbook quickstart**: Expandido con prerequisites, post-install flow, y documentación de memory-check hook (commit `e3e6c6c`)
- **Handbook why-ai-framework**: Reescrito con sustancia técnica y componentes VitePress (commit `12998fc`)
- **Handbook pro-tips**: Reescrito como tips orientados a patrones (commit `f20626f`)
- **Handbook agents-guide**: Actualizado para roster de 6 agentes (commit `1627248`)
- **Skill humanizer**: Añadir patrones de escritura AI en español con `references/spanish-patterns.md` (commit `47437c2`)

### Eliminado

- **14 agentes**: architect-review, backend-architect, cloud-architect, config-security-expert, database-admin, design-iterator, mobile-test-generator, observability-engineer, playwright-test-generator, test-automator, frontend-developer, mobile-developer, docs-architect, design-review — consolidados en 6 agentes core o absorbidos por skills (commits `f1bce96`, `51c15d1`)
- **Skill mobile-testing**: Removido con ejemplos y referencias Maestro/Expo — demasiado especializado para framework general (commit `1b67340`)
- **Skill webapp-testing**: Removido con scripts Python — reemplazado por agent-browser (commit `1b67340`)
- **Skill writing-skills**: Removido — reemplazado por skill-creator con arquitectura mejorada (commit `45b731f`)
- **Skill claude-code-expert**: Deprecado en favor de claude-code-guide nativo de Claude Code (commit `7a093e2`)
- **Hook anti_drift**: Enforcement prescriptivo por prompt reemplazado por constraints constitucionales + SDD hooks empíricos (commit `3a91ef0`)
- **Hook superpowers-loader**: Carga forzada de skill redundante — Claude Code descubre skills nativamente (commit `3a91ef0`)
- **Hook security_guard**: Scanning regex en ediciones reemplazado por security-reviewer agent (commit `3a91ef0`)
- **Hook episodic-memory-sync**: Dependencia de plugin externo eliminada (commit `3a91ef0`)
- **Dashboard**: Removido completamente (server.js, readers.js, tests, package.json) — monitoreo de Ralph migrado a Agent Teams in-process (commit `1b67340`)
- **Specs**: Removido directorio specs/supervision-dashboard/ — artefactos muertos tras eliminación del dashboard (commit `1b67340`)
- **Ralph scripts legacy**: `loop.sh`, `status.sh`, `tail-logs.sh`, `truncate-context.sh`, `PROMPT_build.md`, `scratchpad.md.template`, examples/ (2,023 líneas) — reemplazados por Agent Teams in-process (commit `01e61e1`)
- **Handbook commands-guide**: Página eliminada — commands ya no existen como capa de invocación (commit `1627248`)
- **Template rules/browser-auth.md**: Guía de autenticación OAuth/SSO removida del template base (commit `3a91ef0`)
- **Comandos deprecados**: `/polish`, `/cleancode-format` — subsumidos por eliminación completa del directorio commands/ (commit `ea45eae`)

### Arreglado

- **SDD test guard**: Prevenir reward hacking bloqueando ediciones que reducen assertions cuando tests fallan (commit `7a06618`)
- **Containment SOP skills**: Restricciones de filesystem para prevenir leaks de archivos fuera del proyecto (commit `adb72ae`)
- **Agent-browser daemons**: Limpieza de procesos huérfanos en SessionStart (commit `84098bc`)
- **Gitignore concurrencia**: Prevenir entradas duplicadas por ejecución concurrente de hooks (commit `b8bff4e`)
- **Ralph exit code suppression**: Detección robusta de supresión de exit codes en gates de calidad (commit `16bb045`)
- **Ralph context compression**: Supervivencia vía execution-runbook artifact (commit `16f2c71`)
- **Ralph consistencia**: Resolución de 25+ findings en runtime files y 31 findings de auditoría (commits `5b77a11`, `fe50f43`)

---

::: details Versiones Anteriores

## [5.1.2] - 2026-01-07

### Cambiado

- **Skill git-pullrequest → pr-workflow**: Renombrado para resolver conflicto de nombres — el Skill tool devolvía contenido del comando en lugar del skill cuando ambos compartían nombre (PR #48, #49)
- **Comando git-pullrequest**: Actualizado para invocar `ai-framework:pr-workflow`, añadido campo `description` en frontmatter (PR #49)
- **Documentación skills/commands**: Referencias actualizadas al nuevo nombre `pr-workflow` en commands-guide.md y skills-guide.md (PR #48)

### Arreglado

- **Statusline context %**: Añadido prefijo `~` para indicar aproximación — `current_usage` no incluye MCP tools (~30-50k tokens), corregido cálculo removiendo `output_tokens`, añadido cap 100%, documentada limitación con referencia a issue #12510 (PR #49)

---

## [5.1.1] - 2026-01-07

### Añadido

- **CLAUDE.md template User Queries**: Nueva sección en Operational Standards que obliga uso de `AskUserQuestion` tool para input de usuario — evita preguntas en texto plano que requieren copy-paste (PR #47)

### Arreglado

- **Comando git-pullrequest**: Restaurado formato imperativo — Claude interpretaba formato documentación (## headers) como texto a mostrar en vez de comandos a ejecutar, causando que code review y AskUserQuestion no se ejecutaran (PR #47)

---

## [5.1.0] - 2025-12-28

### Añadido

- **CI marketplace sync**: Workflow GitHub Actions para sincronización automática de versiones con marketplace (commit 6e31082)

### Cambiado

- **CLAUDE.md v4.4.0**: Compliance Certification rediseñado con enfoque evidence-based — `✓ Certified` sin evidencia ahora INVÁLIDO, requiere bloque Evidence con 6 pruebas explícitas (Objective, Verification, Calibration, Truth-Seeking, Skills-First, Transparency), tabla "How to Prove" reemplaza "Prevents" para guía accionable (PR #46)
- **statusline.sh**: Consolidación de 5 operaciones shell en single jq expression para cálculo de tokens — mejora performance eliminando múltiples invocaciones jq (PR #46)
- **Commands synced v4.0.3**: `brainstorm`, `execute-plan`, `write-plan` actualizados con `disable-model-invocation: true` e invocación fully-qualified (`ai-framework:skillname`) (PR #46)
- **Skill using-superpowers**: Sincronizado con superpowers v4.0.3 — añadida sección "How to Access Skills", clarificado "invoke" vs "read", nueva red flag "I know what that means" (PR #46)
- **Documentación quickstart**: Proceso 2-step para actualización de plugins documentado (commit c5d8d54)
- **Documentación integrations**: Clarificado requisito instalación Maestro CLI (commit 5018840)

### Eliminado

- **Skill sharing-skills**: Removido (deprecated en superpowers v4.0.0), documentación sincronizada (PR #46)

---

## [5.0.0] - 2025-12-20

### Añadido

- **Native statusline**: Script bash reemplaza dependencia npm ccstatusline con cálculo preciso de contexto (incluye output_tokens), detección de worktree vía `git worktree list`, check de dependencia jq con fallback graceful (PR #45)
- **Skill linear-expert**: Skill completo para Linear MCP con 7 referencias técnicas (issues, projects, automation, integrations, AI/MCP, administration, views/navigation) (PR #44)
- **Skill writing-skills**: Arquitectura completa para creación de skills efectivos con graphviz conventions, Anthropic best practices, persuasion principles, TDD para documentación (PR #45)
- **Diagramas graphviz**: Visualizaciones DOT inline en CLAUDE.md template para flujos de decisión (PR #45)
- **Documentación integrations.md**: Nueva página unificada de integraciones MCP/plugins reemplazando mcp-servers.md (PR #45)

### Cambiado

- ⚠️ **BREAKING**: **Template MCP migrado a plugins oficiales Anthropic** — context7, playwright, episodic-memory removidos de `.mcp.json.template`, requieren instalación vía `/plugin install {name}@claude-plugin-directory`. Ver [integrations.md](human-handbook/docs/integrations.md) para comandos de migración (PR #45)
- **Hook anti_drift v6.0**: Upgrade a prescriptivo con restatement de 6 killer items (Objective, Verification, Calibration, Truth-Seeking, Skills-First, Transparency) en cada prompt submit (PR #45)
- **CLAUDE.md template v4.3.0**: Diagramas graphviz inline para problem framing, TDD loop, API verification y auto-continuation decision tree (PR #45)
- **Template settings.json**: Env vars optimizadas — `CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000`, `MAX_THINKING_TOKENS=31999`, `SLASH_COMMAND_TOOL_CHAR_BUDGET=30000`, statusline path actualizado a `.claude/statusline.sh` (PR #45)
- **Skills consolidados bajo systematic-debugging**: condition-based-waiting, defense-in-depth, root-cause-tracing movidos como sub-skills manteniendo funcionalidad (PR #45)
- **Skills consolidados bajo test-driven-development**: testing-anti-patterns movido como sub-skill (PR #45)
- **Skill frontend-design**: AI slop detection table, Design Research Protocol (5 áreas), Human Designer Test checklist (PR #45)
- **Skill subagent-driven-development**: Two-stage review (spec compliance → code quality) con prompts externalizados en 3 archivos (PR #45)
- **Skill using-superpowers**: Tabla de red flags y rationalizations, flujo imperativo (PR #45)

### Eliminado

- **marketplace.json**: Removido en favor de patrón Obra (plugin sin manifest marketplace) (PR #45)
- **skill-creator/**: Migrado completamente a writing-skills con arquitectura mejorada (PR #45)
- **mcp-servers.md**: Renombrado a integrations.md para reflejar scope expandido plugins+MCPs (PR #45)
- **Skills separados**: testing-skills-with-subagents movido a writing-skills, condition-based-waiting/defense-in-depth/root-cause-tracing/testing-anti-patterns consolidados (PR #45)

### Arreglado

- **dev-browser CSP**: Sincronizado con upstream, corregido Content Security Policy issue en páginas de GitHub (PR #44)

---

## [4.3.1] - 2025-12-12

### Cambiado

- **Comando /changelog**: Reescritura completa con enfoque Truth-Based — git diff como fuente de verdad en lugar de commits/PRs, elimina inconsistencias por reverts y overwrites (commit f6d079a)
- **Hook anti_drift**: Upgrade a v5.0 con scientific restatement para verificación de compliance (commit 89d4b88)
- **Guía AI-First Workflow**: Reemplazo de diagramas Mermaid redundantes por tablas y listas escaneables, nueva intro "Excelencia por diseño. Dos caminos." (commit f6d079a)
- **Guía commands**: Actualización con workflow Truth-Based del changelog (commit f6d079a)

---

## [4.3.0] - 2025-12-11

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
::: info Última actualización
**Versión**: 2026.3.0 | **Fecha**: 2026-03-14
:::
