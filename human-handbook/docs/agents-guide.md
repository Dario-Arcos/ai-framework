# Guía de Agentes Especializados

::: tip ¿Qué son los Agentes?
Especialistas AI que ejecutan tareas complejas con expertise en dominios específicos. Usa Task tool para invocación explícita y ejecución paralela.
:::

---

| Categoría                                                             | Uso Recomendado                                 |
| --------------------------------------------------------------------- | ----------------------------------------------- |
| [Architecture & System Design](#architecture-system-design)           | Diseño de APIs, arquitectura de sistemas        |
| [Code Review & Security](#code-review-security)                       | Revisión de código, seguridad, edge cases       |
| [Database Management](#database-management)                           | Administración cloud databases                  |
| [Documentation & Technical Writing](#documentation-technical-writing) | Documentación técnica comprehensiva             |
| [Performance & Observability](#performance-observability)             | Optimización de rendimiento, observabilidad     |
| [Testing & Debugging](#testing-debugging)                             | TDD, testing automatizado, debugging sistemático |
| [User Experience & Design](#user-experience-design)                   | UX premium, design review                       |
| [Memory & Context](#memory-context)                                   | Búsqueda de contexto persistente                |

---

## Invocación de Agentes

### Métodos de Invocación

**Automática** (Claude decide):

```bash
"Analiza la arquitectura de este sistema backend"
```

**Explícita** (usuario especifica):

```bash
"Use the backend-architect agent to design this API"
```

**Task Tool** (ejecución paralela):

```bash
"Launch code-reviewer and security-reviewer agents in parallel"
```

### Ejecución en Paralelo

**Patrón recomendado:**

```bash
"Launch in parallel:
- code-reviewer for code standards
- security-reviewer for vulnerabilities
- performance-engineer for optimization

Combine findings in single report"
```

**Beneficios:** ⚡ Tiempo reducido · 🧠 Context windows independientes · 🎯 Análisis especializado

::: tip Cuándo Usar Cada Método
**Automática:** Task estándar, confianza en orquestación Claude
**Explícita:** Garantizar agent específico, paralelización
**Task Tool:** Context window separado, múltiples agents independientes
:::

---

## Architecture & System Design

### `backend-architect`

::: tip API Design & Scalability
Diseño RESTful, microservicios, esquemas BD, arquitectura escalable
:::

**Proceso:** Análisis → Definición endpoints → Esquema BD → Estrategia caché → Recomendaciones tech

**Salida:** API definitions, arquitectura (mermaid), esquema BD, tech stack, cuellos de botella

---

### `cloud-architect`

::: tip Multi-Cloud & IaC
AWS/Azure/GCP, Terraform/OpenTofu/CDK, optimización FinOps
:::

**Platforms:** AWS (Well-Architected) · Azure (ARM/Bicep) · GCP · Multi-cloud networking · Edge computing

**IaC:** Terraform/OpenTofu modules · CloudFormation · AWS/Azure CDK · Pulumi · GitOps (ArgoCD/Flux) · Policy as Code (OPA)

---

## Code Review & Security

### `code-reviewer`

::: tip Quality Gates Universales
Prevención de deuda técnica, principios universales de calidad
:::

**Dimensiones:** Code structure (<50 líneas/función, no duplicación) · Error handling (tipos específicos, cleanup) · Security (no secrets, SQL injection) · Testing (happy path + edge cases)

**Output:** CRITICAL (vulnerabilidades) · ⚠️ HIGH (deuda técnica) · SUGGESTIONS (optimizaciones)

---

### `architect-review`

::: tip Arquitectura Maestro
Clean Architecture, microservicios, event-driven, DDD
:::

**Patrones:** Clean/Hexagonal Architecture · Microservices · Event-driven (CQRS) · DDD (bounded contexts) · Serverless · API-first

**Sistemas distribuidos:** Service mesh (Istio/Linkerd) · Event streaming (Kafka/Pulsar) · Saga/Outbox patterns · Circuit breaker

**Principios:** SOLID · Repository/UnitOfWork · Factory/Strategy/Observer · Dependency Injection

---

### `security-reviewer`

::: danger Security Gates
Revisión completa de seguridad antes de merge
:::

**Vulnerabilities:** SQL/Command/XXE injection · Auth bypass · JWT vulnerabilities · Hardcoded secrets · RCE via deserialization · XSS · PII exposure

**Metodología:** Repository context → Comparative analysis → Vulnerability assessment

**Severity:** **HIGH** (RCE, data breach) · **MEDIUM** (condiciones específicas) · **LOW** (defense-in-depth)

---

### `config-security-expert`

::: danger Production Safety
Prevención de outages por configuración incorrecta
:::

**Archivos críticos:** docker-compose.yml, Dockerfile, .env, terraform, k8s manifests, database configs

**Detección magic numbers:** Value decreased? → Capacity reduction risk · Increased >50%? → Resource overload risk

**Preguntas obligatorias:** ¿Por qué este valor? · ¿Testeado bajo carga? · ¿Dentro de rangos recomendados? · ¿Plan de rollback?

---

### `edge-case-detector`

::: warning Edge Cases Production
Silent failures, data corruption, boundary conditions
:::

**Categorías:** Boundary (off-by-one, division by zero, null handling) · Concurrency (race conditions, deadlocks) · Integration (timeouts, API unavailability) · Failure recovery (state consistency)

**Framework de análisis:** ¿Valores mín/máx? · ¿Datos empty/null? · ¿Múltiples threads simultáneos? · ¿Servicios externos unavailable? · ¿Estado consistente después de failures?

---

## Database Management

### `database-admin`

::: tip Cloud DB Administration
AWS/Azure/GCP databases, automation, reliability engineering
:::

**Cloud:** AWS (RDS/Aurora/DynamoDB) · Azure (SQL DB/Cosmos DB) · GCP (Cloud SQL/Spanner) · Multi-cloud replication

**Technologies:** Relational (PostgreSQL/MySQL) · NoSQL (MongoDB/Cassandra/Redis) · NewSQL (CockroachDB/Spanner) · Time-series (InfluxDB/TimescaleDB) · Graph (Neo4j/Neptune)

**IaC:** Terraform/CloudFormation · Schema management (Flyway/Liquibase) · Backup automation · GitOps for databases

---

## Performance & Observability

### `performance-engineer`

::: tip Performance Optimization
Modern observability, application optimization, scalable systems
:::

**Observability:** OpenTelemetry · DataDog/New Relic/Dynatrace · Prometheus/Grafana · RUM (Core Web Vitals) · Synthetic monitoring

**Profiling:** CPU (flame graphs) · Memory (heap, GC) · I/O (disk, network, DB) · Language-specific (JVM/Python/Node/Go) · Container profiling

**Load Testing:** k6 · JMeter · Gatling · Locust · Stress testing · Performance regression testing · Chaos engineering

---

### `observability-engineer`

::: tip Production Monitoring
Production-ready monitoring, logging, tracing, SLI/SLO management
:::

**Metrics:** Prometheus/PromQL · Grafana dashboards · InfluxDB · DataDog · CloudWatch · High-cardinality metrics

**Tracing:** Jaeger · Zipkin · AWS X-Ray · OpenTelemetry · Service mesh observability · Performance bottlenecks

**Logging:** ELK Stack · Fluentd/Fluent Bit · Splunk · Loki/Grafana · Log parsing · Centralized logging

---

## Testing & Debugging

### `test-automator`

::: tip Test Automation Master
Modern frameworks, self-healing tests, quality engineering
:::

**Frameworks:** Jest/Vitest/Playwright/Cypress (JS/TS) · pytest/Robot (Python) · JUnit/TestNG (Java) · NUnit/xUnit (C#) · Appium (mobile)

**AI-Powered:** Applitools/Percy (visual) · Test case generation · Self-healing selectors · Risk-based prioritization · Synthetic data · Failure prediction

**Strategy:** Test pyramid (70% unit, 20% integration, 10% E2E) · Contract testing (Pact) · API testing (REST Assured) · Performance (k6/JMeter) · Security (OWASP ZAP)

**CI/CD:** Quality gates · Parallel execution · Test reporting (Allure/ReportPortal) · Deployment testing (canary/feature flags)

---

### `playwright-test-generator`

::: tip Autonomous E2E Tests
AI-powered Playwright test generation via visual exploration
:::

**Mission:** Generate production-ready E2E tests through autonomous visual exploration usando MCP tools

**Input:** TARGET (URL o file path)
**Output:** `tests/` + HTML report + `results.json`

**Phases:** Environment detection → Visual discovery (screenshots + accessibility) → Test generation (atomic files, modern patterns) → Reality-test validation (≥90% success, max 5 iterations) → Honest reporting

**Discovery:** Screenshot (visual prominence) + Snapshot (roles, labels) → Identify interactive elements → Discover flows (primary CTAs, forms, navigation, errors) → Progressive exploration

---

### `mobile-test-generator`

::: tip Autonomous Mobile E2E Tests
AI-powered mobile test generation via mobile-mcp visual exploration + Maestro YAML flows
:::

**Mission:** Generate production-ready mobile E2E tests through autonomous visual exploration of iOS/Android apps

**Stack:** React Native · Expo · Flutter · Native iOS/Android

**Input:** `APP_ID` (bundle identifier) o descripción de app
**Output:** `flows/` (Maestro YAML) + execution report

**Phases:**
1. **Environment Detection**: List devices, identify platform, detect app type
2. **Visual Discovery**: mobile_launch_app → mobile_take_screenshot → mobile_list_elements_on_screen → navigate → repeat
3. **Generate Maestro Flows**: YAML files estructurados en `flows/[feature]/[scenario].yaml`
4. **Validation Loop**: `maestro test flows/` hasta ≥90% pass rate (max 5 iterations)
5. **Reporting**: `.claude/reviews/mobile-test-report.md`

**First Step**: Load `mobile-testing` skill para referencias detalladas

**Expo Critical**: Usar Development Builds, NO Expo Go:
```yaml
- openLink: "exp+com.myapp://expo-development-client/?url=http://10.0.2.2:8081"
```

**Key References** (via skill):
- `references/maestro-patterns.md` - YAML syntax oficial
- `references/mobile-mcp-tools.md` - Tools de debugging
- `references/expo-react-native.md` - Guía específica Expo/RN

---

### `systematic-debugger`

::: tip Systematic Debugging
Methodical bug identification, root cause analysis, coordinated delegation
:::

**Workflow:** Problem analysis (clarification, codebase investigation, trace execution) → Root cause (15+ hypotheses, multiple angles) → Strategic planning (rank theories, identify sub-agents) → Coordinated delegation (brief agents, monitor, validate)

**Delegation Framework:**

| Bug Category    | Primary Sub-Agent     | Secondary Support         |
| --------------- | --------------------- | ------------------------- |
| Backend Logic   | backend-developer     | database-expert           |
| API Issues      | api-architect         | rails-api-developer       |
| Database Issues | database-expert       | rails-activerecord-expert |
| Performance     | performance-optimizer | code-reviewer             |
| Security        | security-reviewer     | config-security-expert    |

---

## User Experience & Design

### `design-iterator`

::: tip Iterative Design Refinement
Refinamiento sistemático y progresivo de componentes web mediante análisis visual e iteraciones
:::

**Metodología:** Para cada iteración: Screenshot (solo elemento target) → Análisis (3-5 mejoras) → Implementar → Documentar → Repetir

**Visual Hierarchy:** Headline sizing/weight · Color contrast · Whitespace · Section separation

**Modern Patterns:** Gradient backgrounds · Micro-interactions/hover states · Badge/tag styling · Icon treatments · Border radius consistency

**Typography:** Font pairing · Line height/letter spacing · Text color variations · Italic emphasis

**Layout:** Hero card patterns · Asymmetric grids · Alternating visual rhythm · Responsive breakpoints

**Polish:** Shadow depth/color · Animated elements · Social proof · Trust indicators

**Competitor Research:** Stripe (gradients, premium) · Linear (dark, minimal) · Vercel (typography-forward) · Notion (friendly, illustrations)

**Uso:** Invocar con número de iteraciones (default: 10). Ideal cuando 1-2 cambios simples no resuelven el problema de diseño

---

## Consejos de Uso

::: tip Selección Rápida
**Simple:** Agentes generales (backend-architect, cloud-architect)
**Complex:** Múltiples especialistas + quality reviewers
**Production-Critical:** SIEMPRE security + performance + observability
:::

### Combinaciones Poderosas

| Combinación                                    | Resultado                        |
| ---------------------------------------------- | -------------------------------- |
| `backend-architect` + `database-admin`         | Scalable architecture            |
| `code-reviewer` + `security-reviewer`          | Quality + Security gates         |
| `test-automator` + `playwright-test-generator` | Complete web testing automation  |

### Flujo Óptimo

**Diseño** → Architecture/design agents
**Implementación** → Development agents
**Quality** → Review agents (code, security, edge-case)
**Testing** → Test automation agents
**Observability** → Performance/observability agents

---

::: info Última Actualización
**Fecha**: 2026-01-11
:::
