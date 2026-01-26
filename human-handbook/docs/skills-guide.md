# Guía de Skills

::: tip ¿Qué son las Skills?
Capacidades especializadas que extienden Claude con conocimiento experto y workflows probados. Se activan automáticamente según el contexto o mediante invocación explícita.
:::

---

## Inicio Rápido

::: tip Encuentra tu Skill
Selecciona tu situación para ver las skills recomendadas
:::

| Situación | Skill Recomendada |
|-----------|-------------------|
| Idea nueva, necesito explorar | `brainstorming` |
| Testing E2E webapp | `webapp-testing` |
| Testing E2E mobile | `mobile-testing` |
| Crear PR con quality gate | `pr-workflow` |
| Crear componentes Claude Code | `claude-code-expert` |
| Diseño frontend distintivo | `frontend-design` |
| Humanizar texto AI-generated | `humanizer` |
| Desarrollo autónomo multi-iteración | `ralph-loop` |

---

## Skills por Categoría

| Categoría | Skills | Uso Recomendado |
|-----------|--------|-----------------|
| [Planning](#planning) | 1 | Explorar ideas antes de implementar |
| [Testing](#testing) | 2 | E2E testing para webapps y mobile |
| [Git](#git) | 1 | PR con quality gate integrado |
| [Development Tools](#development-tools) | 1 | Crear componentes Claude Code |
| [Design](#design) | 1 | Interfaces frontend distintivas |
| [Writing](#writing) | 1 | Humanización de texto |
| [Automation](#automation) | 1 | Desarrollo autónomo en loop |

---

## Planning

### brainstorming

::: tip Planning | Foundation
**Cuándo**: Antes de cualquier trabajo creativo - crear features, construir componentes, agregar funcionalidad o modificar comportamiento
**Qué hace**: Transforma ideas vagas en diseños completos mediante diálogo colaborativo. Preguntas una a la vez, exploración de alternativas, validación incremental.
:::

**Proceso**:

1. **Entender la idea**
   - Revisar estado actual del proyecto (archivos, docs, commits recientes)
   - Preguntas una a la vez (preferir multiple choice)
   - Foco: propósito, constraints, criterios de éxito

2. **Explorar alternativas**
   - Proponer 2-3 enfoques con trade-offs
   - Liderar con recomendación y razonamiento
   - Presentar opciones conversacionalmente

3. **Presentar diseño**
   - Secciones de 200-300 palabras
   - Validar después de cada sección
   - Cubrir: arquitectura, componentes, data flow, error handling, testing

**Después del diseño**:
- Documentar en `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Commit del documento
- Continuar con ralph-loop o Superpowers `writing-plans`

**Principios clave**:
- **Una pregunta a la vez** - No abrumar con múltiples
- **YAGNI ruthlessly** - Eliminar features innecesarios
- **Validación incremental** - Secciones pequeñas, validar cada una
- **Flexibilidad** - Volver atrás cuando algo no tiene sentido

**Ejemplo**:
```bash
"Necesito sistema de notificaciones push"
# → ¿Real-time o batch? (pregunta 1)
# → ¿Qué canales? Email, SMS, in-app? (pregunta 2)
# → Propone 3 enfoques con trade-offs
# → Diseño en secciones, valida cada una
# → docs/plans/2026-01-25-notifications-design.md
```

---

## Testing

### webapp-testing

::: tip Testing | E2E
**Cuándo**: Testear aplicaciones web locales, verificar funcionalidad frontend, debugging UI, o capturar screenshots del browser
**Qué hace**: Provee toolkit Playwright con server lifecycle management. Scripts helper para manejar servidores (start/stop automático)
:::

**Decision Tree**:
```
¿Es HTML estático?
├─ Sí → Lee HTML directo para identificar selectores → Playwright script
└─ No (webapp dinámica) → ¿Server ya corriendo?
    ├─ No → python scripts/with_server.py --help
    └─ Sí → Reconnaissance-then-action:
        1. Navigate + wait for networkidle
        2. Screenshot o inspect DOM
        3. Identify selectors
        4. Execute actions
```

**Helper Scripts**:
- `scripts/with_server.py` - Maneja lifecycle de servidores (soporta múltiples)

**Ejemplo**:
```bash
# Single server
python scripts/with_server.py --server "npm run dev" --port 5173 -- python test.py

# Multiple servers
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python test.py
```

**Best Practices**:
- Siempre `page.wait_for_load_state('networkidle')` antes de inspeccionar DOM
- Usar scripts como black boxes (--help primero)
- Cerrar browser al terminar

---

### mobile-testing

::: tip Testing | Mobile E2E
**Cuándo**: Testing de apps móviles (React Native, Expo, Flutter, native), debugging UI en simuladores/emuladores, o generación de test suites E2E mobile
**Qué hace**: Provee integración dual-stack con mobile-mcp (debugging interactivo) y Maestro (test suites E2E con YAML flows y AI assertions)
:::

**Dual-Stack Approach**:
- **mobile-mcp**: Screenshots, accessibility tree, interacción directa con simuladores/emuladores
- **Maestro**: YAML flows declarativos, auto-healing, assertions AI (`assertWithAI`, `assertNoDefectsWithAI`)

**Prerequisites**:
```bash
node --version    # v22+
java --version    # 17+
maestro --version # Latest
```

**Decision Tree**:
```
¿Tipo de testing?
├─ Debugging → mobile-mcp tools directamente
│   1. mobile_list_available_devices
│   2. mobile_launch_app(appId)
│   3. mobile_take_screenshot
│   4. mobile_list_elements_on_screen
│
├─ E2E Test Generation → Explorar con mobile-mcp, generar Maestro YAML
│   1. Explorar visualmente
│   2. Generar flows/[feature]/[scenario].yaml
│   3. Validar: maestro test flows/
│
└─ Expo/React Native → Ver references/expo-react-native.md
```

**Ejemplo Maestro Flow**:
```yaml
appId: com.myapp
---
- launchApp:
    clearState: true
- tapOn:
    id: "login-button"
- inputText: "user@example.com"
- extendedWaitUntil:
    visible:
      id: "home-screen"
    timeout: 10000
```

**Expo Critical**: Usar Development Builds, NO Expo Go. Usar `openLink` para deep links:
```yaml
- openLink: "exp+com.myapp://expo-development-client/?url=http://10.0.2.2:8081"
```

**References** (progressive disclosure):
- `references/maestro-patterns.md` - Sintaxis YAML completa
- `references/mobile-mcp-tools.md` - Tools de debugging
- `references/expo-react-native.md` - Guía específica Expo/RN

---

## Git

### pr-workflow

::: tip Git | Quality Gate
**Cuándo**: Al crear PR, necesitas quality gate con code + security review y observaciones contextualizadas
**Qué hace**: Valida cambios, dispara code-reviewer + security-reviewer en paralelo, genera observaciones (tests, API, complexity, breaking), presenta findings consolidados de 3 capas, ofrece auto fix loop, crea PR con documentación quality
:::

**Corporate Format Support:**
```
Pattern: type|TASK-ID|YYYYMMDD|description
Example: feat|TRV-350|20251023|add user authentication
```

**Workflow**:
1. **Validación**: Target branch existe, extrae commits, detecta formato
2. **Quality Gate (3 capas en paralelo)**:
   - Code review (lógica, arquitectura, bugs)
   - Security review (SQL injection, secrets, XSS)
   - Observations (tests, API, breaking, complexity)
3. **User Decision**: Create PR / Auto fix / Cancel
4. **Auto Fix Loop** (opcional): Subagent arregla issues → re-review (ambos) → usuario decide de nuevo
5. **Create PR**: Protected branch detection + temp branch si necesario, genera body con findings, crea PR

**User Decisions:**
- **Create PR**: Push y crear PR con findings de code + security reviews documentados
- **Auto fix**: Subagent arregla Critical+Important (code) + High+Medium (security) issues → re-review obligatorio de ambos
- **Cancel**: Salir con summary actionable de issues pendientes

**Ejemplo**:
```bash
"Crear PR a main con quality gate"
# → Analiza commits, detecta corporate format
# → Code review + observaciones
# → Usuario selecciona: Auto fix
# → Subagent arregla issues
# → Re-review (limpio)
# → Usuario selecciona: Create PR
# → PR creado con URL
```

---

## Development Tools

### claude-code-expert

::: tip Dev Tools | Production
**Cuándo**: Crear/modificar/update/fix agents, slash commands, hooks, o MCP integrations para Claude Code
**Qué hace**: Genera componentes Claude Code production-ready con 6 quality gates automáticos (syntax, security, logic, constitutional, integration, production). WebFetch docs oficiales para syntax actual
:::

**Workflow**:
1. **Identify Component**: Agent, slash command, hook, o MCP server
2. **WebFetch Docs**: Official Claude Code docs para EXACT current syntax (training stale)
3. **Analyze Patterns**: Lee project conventions
4. **Generate**: Component con validación
5. **6 Quality Gates**: Syntax, security, logic, constitutional, integration, production

**Ejemplo**:
```bash
"Crea agent para optimización PostgreSQL"
# → WebFetch Claude Code agent docs
# → Analiza agents/ patterns
# → Genera agent con tools, workflow, examples
# → 6 quality gates automáticos
```

**Output**: `.claude/agents/*.md`, `commands/*.md`, `hooks/*.py`, o `.claude/.mcp.json` update

**Critical**: Training data stale, SIEMPRE WebFetch docs oficiales primero

---

## Design

### frontend-design

::: tip Design | Production
**Cuándo**: Construir componentes web, páginas, o aplicaciones que requieren diseño distintivo y memorable
**Qué hace**: Crea interfaces frontend production-grade con dirección estética bold que evita la estética genérica "AI slop". Implementa código funcional con atención excepcional a detalles estéticos
:::

**Design Thinking** (antes de codear):
1. **Purpose**: ¿Qué problema resuelve? ¿Quién lo usa?
2. **Tone**: Elegir dirección extrema: brutalmente minimal, maximalist chaos, retro-futuristic, luxury/refined, editorial/magazine, brutalist/raw, art deco, etc.
3. **Constraints**: Framework, performance, accessibility
4. **Differentiation**: ¿Qué lo hace INOLVIDABLE?

**Focus Areas**:
- **Typography**: Fonts distintivas, NO genéricas (evitar Arial, Inter, Roboto). Pair display font + refined body font
- **Color & Theme**: Paleta cohesiva con CSS variables. Colores dominantes con acentos sharp > paletas tímidas
- **Motion**: CSS-only preferido. Staggered reveals con animation-delay > micro-interactions dispersas
- **Spatial Composition**: Layouts inesperados, asimetría, overlap, grid-breaking, negative space generoso
- **Backgrounds**: Gradient meshes, noise textures, geometric patterns, layered transparencies, grain overlays

**NEVER use**:
- Fonts genéricas: Inter, Roboto, Arial, system fonts
- Color schemes cliché: purple gradients on white
- Layouts predecibles y cookie-cutter
- Mismo estilo entre generaciones (variar light/dark, fonts, aesthetics)

**Ejemplo**:
```bash
"Crea landing page para startup fintech"
# → Design Thinking: luxury/refined tone, professional audience
# → Typography: distinctive serif headers + clean sans body
# → Color: deep navy + gold accents (not purple gradient)
# → Motion: staggered reveal on scroll, hover micro-interactions
# → Output: Production-ready React/HTML with memorable aesthetic
```

**Principio**: Match implementation complexity to aesthetic vision. Maximalist = elaborate code. Minimalist = restraint + precision + careful spacing.

---

## Writing

### humanizer

::: tip Writing | Text Humanization
**Cuándo**: Escribir o editar prosa para humanos: docs, READMEs, commits, PRs, error messages, UI text, reportes
**Qué hace**: Detecta y elimina 24 patrones de texto IA (Wikipedia's "Signs of AI writing") + añade personalidad y voz
:::

**Categorías de patrones detectados**:
- **Content**: Inflación de significancia, name-dropping, análisis superficiales con -ing, lenguaje promocional
- **Language**: Vocabulario IA ("Additionally", "delve", "landscape"), evitar "is/are", regla de tres
- **Style**: Abuso de em dash, negritas, emojis, Title Case en headings
- **Communication**: Artefactos de chatbot ("I hope this helps!"), tono sicofante
- **Filler**: Frases de relleno, hedging excesivo, conclusiones genéricas

**Personality and Soul** (no solo limpiar, añadir voz):
- Tener opiniones, no solo reportar neutro
- Variar ritmo: oraciones cortas. Luego largas que toman su tiempo.
- Reconocer complejidad ("impressive but also unsettling")
- Usar "I" cuando aplica
- Dejar algo de desorden (tangentes, pensamientos a medio formar)

**Ejemplo**:
```bash
# Antes (AI-sounding)
"The software update serves as a testament to the company's commitment
to innovation. Moreover, it provides a seamless, intuitive, and powerful
user experience—ensuring that users can accomplish their goals efficiently."

# Después (Humanized)
"The update adds batch processing, keyboard shortcuts, and offline mode.
Early feedback from beta testers has been positive."
```

**Principio**: Evitar patrones malos es solo la mitad. Texto estéril es tan obvio como slop.

---

## Automation

### ralph-loop

::: warning Automation | Advanced
**Cuándo**: Desarrollo autónomo multi-iteración con context rotation y state persistente
**Qué hace**: Loop infinito donde cada iteración opera con fresh context. Estado persiste en archivos y git, no en memoria LLM. Por defecto, corre hasta que objetivo esté 100% completo.
:::

**Prerequisites**:
- Git repository existente
- Proyecto con comandos de validación (tests, lint, build)

**Instalación**:
```bash
# Desde tu project root (debe tener .git/)
RALPH_SKILL="path/to/skills/ralph-loop"
cp "$RALPH_SKILL/scripts/loop.sh" .
cp "$RALPH_SKILL/scripts/PROMPT_build.md" .
cp "$RALPH_SKILL/scripts/PROMPT_plan.md" .
chmod +x loop.sh
```

**Uso**:
```bash
./loop.sh              # Build mode (unlimited, hasta complete)
./loop.sh 20           # Build mode, max 20 iteraciones
./loop.sh plan         # Plan mode (unlimited, hasta complete)
./loop.sh plan 5       # Plan mode, max 5 iteraciones
```

**Core Principles** (The Ralph Tenets):
1. **Fresh Context Is Reliability** - Cada iteración limpia contexto
2. **Backpressure Over Prescription** - Gates que rechazan mal trabajo
3. **The Plan Is Disposable** - Regeneración cuesta un loop
4. **Disk Is State, Git Is Memory** - Archivos son el mecanismo de handoff
5. **Steer With Signals, Not Scripts** - Cuando falla, agrega Sign para próxima vez
6. **Let Ralph Ralph** - Sit on the loop, not in it

**Safety Features**:
- Double completion verification (2 señales COMPLETE consecutivas)
- Runtime limit configurable
- Context health monitoring (exit >80%)
- Task abandonment detection (3+ intentos fallidos)
- Loop thrashing detection (patrones oscilantes)

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | SUCCESS - Objetivo completo |
| 1 | ERROR - Validación fallida |
| 2 | CIRCUIT_BREAKER - 3 fallos consecutivos |
| 3 | MAX_ITERATIONS - Límite alcanzado |
| 130 | INTERRUPTED - Ctrl+C |

---

## Cómo Usar Skills

**Activación automática**: Claude detecta contexto y carga skill apropiada sin invocación explícita.

```bash
# Solicitud natural
"Necesito crear un PR con review"
# → pr-workflow se activa automáticamente
```

**Invocación manual** (opcional):
```bash
"Usando frontend-design: crea landing page para mi startup"
```

::: tip Precedencia
**Skills > MCPs > Implementación directa**

Siempre verifica skills disponibles antes de implementar. Si skill existe para tu task, MUST use.
:::

---

## Skills Adicionales

Para workflows de desarrollo avanzados (TDD, debugging sistemático, brainstorming, plans), consulta el plugin **Superpowers**:

```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

Ver [Integrations](./integrations.md#superpowers-plugin) para más detalles.

---

## Solución de Problemas

::: details Skill no se activa automáticamente

**Causa común**: Solicitud demasiado genérica

```bash
❌ "Ayuda con código"
✅ "Crea PR con quality gate a main"
```

**Solución**: Menciona skill explícitamente:
```bash
"Usando pr-workflow: crea PR a develop"
```
:::

::: details Skill falta o versión antigua

**Update framework**:

```bash
# Si instalado vía marketplace
/plugin marketplace update ai-framework-marketplace
/plugin update ai-framework@ai-framework-marketplace
# Session restart
```

**Verificar versión**:
```bash
cat package.json | grep version
```
:::

---

::: info Metadata
**Última actualización**: 2026-01-25
**Skills disponibles**: 8 (Planning: 1, Testing: 2, Git: 1, Dev Tools: 1, Design: 1, Writing: 1, Automation: 1)
**Status**: Production-Ready
:::
