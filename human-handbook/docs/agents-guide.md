# Guía de Agentes Especializados

::: tip ¿Qué son los Agentes?
Especialistas AI que ejecutan tareas complejas con expertise en dominios específicos. Usa Task tool para invocación explícita y ejecución paralela.
:::

---

| Categoría                                                             | Agentes | Uso Recomendado                                       |
| --------------------------------------------------------------------- | ------- | ----------------------------------------------------- |
| [Architecture & System Design](#architecture-system-design)           | 8       | Diseño de APIs, arquitectura de sistemas, multi-cloud |
| [Code Review & Security](#code-review-security)                       | 5       | Revisión de código, seguridad, edge cases             |
| [Database Management](#database-management)                           | 2       | Optimización de BD, administración cloud              |
| [DevOps & Deployment](#devops-deployment)                             | 4       | CI/CD, GitOps, troubleshooting, DX                    |
| [Documentation & Technical Writing](#documentation-technical-writing) | 5       | Documentación técnica, APIs, tutoriales               |
| [Incident Response & Network](#incident-response-network)             | 2       | Respuesta a incidentes, ingeniería de redes           |
| [Performance & Observability](#performance-observability)             | 3       | Optimización de rendimiento, observabilidad           |
| [Shadcn-UI Components](#shadcn-ui-components)                         | 4       | Componentes UI con shadcn/ui                          |
| [Testing & Debugging](#testing-debugging)                             | 4       | TDD, testing automatizado, debugging sistemático      |
| [User Experience & Design](#user-experience-design)                   | 3       | UX premium, animaciones GSAP, design review           |
| [Web & Application](#web-application)                                 | 5       | TypeScript, Python, JavaScript, PHP, Ruby             |

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
"Launch code-quality-reviewer and security-reviewer agents in parallel"
```

### Ejecución en Paralelo

**Patrón recomendado:**

```bash
"Launch in parallel:
- code-quality-reviewer for code standards
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

### `frontend-developer`

::: tip React 19 & Next.js 15
Componentes React, layouts responsivos, state management client-side
:::

**Stack:** React 19 (Actions, RSC) · Next.js 15 (App Router) · Zustand/Jotai · React Query · Playwright

**Proceso:** Contexto UX → Arquitectura componentes → Patrones modernos → Performance → Accessibility → Testing

---

### `mobile-developer`

::: tip Cross-Platform Mobile
React Native, Flutter, desarrollo nativo, sincronización offline
:::

**Stack:** React Native (New Architecture) · Flutter 3.x · Expo SDK 50+ · SQLite/Realm

**Proceso:** Platform-agnostic → Performance (memory, battery) → Device integration → Offline-first → App Store compliance

---

### `cloud-architect`

::: tip Multi-Cloud & IaC
AWS/Azure/GCP, Terraform/OpenTofu/CDK, optimización FinOps
:::

**Platforms:** AWS (Well-Architected) · Azure (ARM/Bicep) · GCP · Multi-cloud networking · Edge computing

**IaC:** Terraform/OpenTofu modules · CloudFormation · AWS/Azure CDK · Pulumi · GitOps (ArgoCD/Flux) · Policy as Code (OPA)

---

### `graphql-architect`

::: tip GraphQL Moderno
Federation, optimización performance, seguridad enterprise
:::

**Stack:** Apollo Federation v2 · Schema-first design · DataLoader (N+1) · Field-level auth · Subscriptions (WebSocket/SSE)

---

### `hybrid-cloud-architect`

::: tip Soluciones Híbridas
Multi-cloud (AWS/Azure/GCP) + private clouds (OpenStack/VMware)
:::

**Public:** AWS/Azure/GCP cross-cloud · **Private:** OpenStack (Nova/Neutron/Cinder) · VMware vSphere
**Hybrid:** Azure Arc · AWS Outposts · Google Anthos · Edge computing

---

### `kubernetes-architect`

::: tip Cloud-Native Infrastructure
GitOps workflows (ArgoCD/Flux), orquestación enterprise containers
:::

**Platforms:** EKS/AKS/GKE · OpenShift/Rancher/Tanzu · Multi-cluster management
**GitOps:** ArgoCD · Flux v2 · Progressive delivery (canary/blue-green) · External Secrets Operator

---

### `agent-strategy-advisor`

::: tip Herramienta Consultiva
Analiza trabajo y recomienda agents óptimos con rationale detallado. NO ejecuta tareas.
:::

**Input:** tasks.md, free-form text, user stories
**Output:** Strategic plan con work analysis, agent recommendations, execution strategy, ROI assessment

**Usage:**

```bash
/ai-framework:Task agent-strategy-advisor "Analiza tasks.md"
```

**Anti-Overengineering:** S ≤ 80 LOC → Main Claude suficiente · Agent overhead = 5-10 min → ROI > 1.5x

---

## Code Review & Security

### `code-quality-reviewer`

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

### `database-optimizer`

::: tip Performance Tuning
Query optimization, indexing strategies, arquitecturas escalables
:::

**Query:** EXPLAIN ANALYZE · Subquery/JOIN optimization · Window functions · Cross-database (PostgreSQL/MySQL/SQL Server/Oracle) · NoSQL (MongoDB/DynamoDB)

**Indexing:** B-tree/Hash/GiST/GIN · Composite indexes · Full-text search · JSON indexes · Cloud-native indexing

**Monitoring:** pg_stat_statements · Performance Schema · APM integration · Query cost analysis · AWS Performance Insights

---

### `database-admin`

::: tip Cloud DB Administration
AWS/Azure/GCP databases, automation, reliability engineering
:::

**Cloud:** AWS (RDS/Aurora/DynamoDB) · Azure (SQL DB/Cosmos DB) · GCP (Cloud SQL/Spanner) · Multi-cloud replication

**Technologies:** Relational (PostgreSQL/MySQL) · NoSQL (MongoDB/Cassandra/Redis) · NewSQL (CockroachDB/Spanner) · Time-series (InfluxDB/TimescaleDB) · Graph (Neo4j/Neptune)

**IaC:** Terraform/CloudFormation · Schema management (Flyway/Liquibase) · Backup automation · GitOps for databases

---

## DevOps & Deployment

### `deployment-engineer`

::: tip CI/CD & GitOps
Pipelines modernos, workflows GitOps, automatización deployment
:::

**Platforms:** GitHub Actions · GitLab CI/CD · Azure DevOps · Jenkins · AWS CodePipeline · Tekton

**GitOps:** ArgoCD · Flux v2 · Progressive delivery · Helm/Kustomize · External Secrets Operator

**Containers:** Multi-stage builds · BuildKit · Podman/containerd · Image signing (Cosign) · Security scanning (Trivy)

---

### `devops-troubleshooter`

::: danger Incident Response
Respuesta rápida, debugging avanzado, observabilidad moderna
:::

**Observability:** ELK/Loki · DataDog/New Relic/Dynatrace · Prometheus/Grafana · Jaeger/Zipkin/X-Ray · OpenTelemetry

**Container/K8s:** kubectl mastery · Pod troubleshooting · Service mesh debugging (Istio/Linkerd) · CNI troubleshooting

**Network:** tcpdump/Wireshark · DNS resolution · Load balancer debugging · SSL/TLS issues · Firewall troubleshooting

---

### `dx-optimizer`

::: tip Developer Experience
Tooling, setup simplificado, workflows optimizados
:::

**Áreas:** Environment setup (<5 min onboarding) · Automation (tareas repetitivas) · Tooling (IDE config, git hooks, CLI) · Documentation (setup funcional, troubleshooting)

**Metrics:** Time from clone to running · Pasos manuales eliminados · Build/test execution time · Developer satisfaction

---

### `terraform-specialist`

::: tip IaC Avanzado
Terraform/OpenTofu automation, gestión de estado, patrones enterprise
:::

**Core:** Dynamic blocks · for_each loops · Complex type constraints · Remote backends · Workspace strategies

**Modules:** Hierarchical design · Composition patterns · Terratest testing · Semantic versioning

**State:** S3/Azure Storage/GCS backends · State encryption · DynamoDB locking · State operations (import/move/remove)

**Security:** tfsec · Checkov · Terrascan · Sentinel/OPA policy enforcement

---

## Documentation & Technical Writing

### `docs-architect`

::: tip Technical Deep-Dives
Manuales técnicos comprehensivos desde codebases existentes
:::

**Proceso:** Codebase analysis → Structure (chapters/sections) → Write (overview → details) → Diagrams (architecture/sequence/flow)

**Secciones:** Executive summary · Architecture overview · Design decisions · Core components · Data models · Integration points · Security · Deployment · Development guide

**Output:** 10-100+ páginas, bird's-eye → implementation specifics, diagrams exhaustivos

---

### `api-documenter`

::: tip API Documentation
OpenAPI 3.1, AI-powered tools, developer portals
:::

**Standards:** OpenAPI 3.1+ · AsyncAPI · GraphQL SDL · JSON Schema · Webhook docs · API lifecycle

**AI Tools:** Mintlify · ReadMe AI · Automated updates · Code example generation · Content translation

**Platforms:** Swagger UI/Redoc · Stoplight Studio · Postman collections · Docusaurus · API Explorer

**Developer Portal:** Multi-API organization · Auth/API key mgmt · Community features · Analytics · Search optimization

---

### `mermaid-expert`

::: tip Visual Diagrams
Flowcharts, sequences, ERDs, architecture diagrams
:::

**Types:** flowchart, sequenceDiagram, classDiagram, stateDiagram-v2, erDiagram, gantt, gitGraph, timeline

**Process:** Elegir diagram type → Mantener legibilidad → Styling consistente → Labels significativos → Testing rendering

---

### `reference-builder`

::: tip Referencias Exhaustivas
API docs, configuration guides, complete technical specs
:::

**Coverage:** Exhaustive parameters · Precise categorization · Cross-referencing · Examples · Edge cases

**Types:** API references (methods, returns, errors) · Config guides (parameters, defaults, dependencies) · Schema docs (fields, validation, relationships)

**Entry Format:** Type, Default, Required, Since, Description, Parameters, Returns, Throws, Examples, See Also

---

### `tutorial-engineer`

::: tip Learning Experiences
Step-by-step tutorials, educational content, hands-on examples
:::

**Process:** Learning objectives → Concept decomposition → Exercise design → Progressive sections

**Structure:** Opening (objectives, prerequisites, time, result) · Progressive (concept → minimal example → guided practice → variations → challenges → troubleshooting) · Closing (summary, next steps)

**Principles:** Show don't tell · Fail forward · Incremental complexity · Context first

---

## Incident Response & Network

### `incident-responder`

::: danger Incident Management
Rapid problem resolution, observability moderna, SRE practices
:::

**First 5 min:** Assess severity (user/business impact, scope) · Incident command (IC, Comms Lead, Tech Lead) · Stabilization (throttling, rollback, scaling)

**Investigation:** Distributed tracing (OpenTelemetry/Jaeger) · Metrics correlation (Prometheus/Grafana) · Log aggregation (ELK/Splunk) · APM analysis · RUM

---

### `network-engineer`

::: tip Cloud Networking
Modern cloud networking, security architectures, performance optimization
:::

**Cloud:** AWS (VPC, Transit Gateway) · Azure (Virtual networks, NSGs) · GCP (VPC networks, Cloud NAT) · Multi-cloud connectivity · Edge networking

**Load Balancing:** AWS ALB/NLB · Azure Load Balancer/Application Gateway · Nginx/HAProxy/Envoy/Traefik · Global LB · API gateways (Kong/Ambassador)

**DNS:** BIND/PowerDNS · Route 53/Azure DNS/Cloud DNS · Service discovery (Consul/etcd/K8s DNS) · DNSSEC · CDN integration

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

### `web-search-specialist`

::: tip Deep Research
Advanced search techniques, multi-source verification, trend analysis
:::

**Strategies:** Query optimization (exact matches, exclusions, timeframes) · Domain filtering (allowed/blocked) · WebFetch deep dive

**Process:** Understand objective → 3-5 query variations → Search broadly → Refine → Verify across sources → Track contradictions

**Output:** Research methodology · Curated findings con URLs · Credibility assessment · Synthesis · Contradictions/gaps · Structured summaries

---

## Shadcn-UI Components

### `shadcn-requirements-analyzer`

::: tip Component Analysis
Traduce UI features en structured shadcn component requirements
:::

**Workflow:** Check registries (`mcp__shadcn__get_project_registries`) → Analyze request → Map components → Validate (`mcp__shadcn__search_items_in_registries`) → Design hierarchy → Document requirements

**Output:** `design-docs/[task-name]/requirements.md` con Feature name, Components required, Hierarchy, Implementation notes, Data flow, Accessibility, Validation rules

---

### `shadcn-component-researcher`

::: tip Component Research
Gather component details, examples, installation commands
:::

**Workflow:** Read requirements → Deep research (`mcp__shadcn__view_items_in_registries`) → Examples (`mcp__shadcn__get_item_examples_from_registries`) → Install commands (`mcp__shadcn__get_add_command_for_items`) → Document

**Output:** `design-docs/[task-name]/component-research.md` con source code, API docs, dependencies, examples, installation, alternatives

---

### `shadcn-implementation-builder`

::: tip Production Components
TypeScript/React components con state management y validation
:::

**Workflow:** Read requirements → Build architecture (TypeScript, interfaces, state, error handling, accessibility) → Quality validation (`mcp__shadcn__get_audit_checklist`) → File generation

**Quality:** Full TypeScript (no `any`) · Error handling · Loading states · WCAG compliance · Mobile-first · React best practices · Zod validation

---

### `shadcn-quick-helper`

::: tip Quick Assistance
Rapid component additions, installation commands, basic usage
:::

**Workflow:** Verify setup → Parse natural language ("button" → "button", "modal" → "dialog") → Discover → Get details → Examples → Generate command

**Quick Response:** Installation command · Basic usage · Key props · Common patterns · Next steps

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

### `tdd-orchestrator`

::: tip TDD Master
Red-green-refactor discipline, multi-agent coordination
:::

**Discipline:** Red-green-refactor enforcement · TDD rhythm · Test-first verification · Refactoring safety nets · Cycle time optimization · Anti-pattern detection

**Coordination:** Specialized testing agents (unit/integration/E2E) · Cross-team TDD sync · Agent delegation · Multi-repository governance

**Practices:** Classic TDD (Chicago) · London School (mockist) · ATDD · BDD · Outside-in/Inside-out · Hexagonal architecture TDD

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
| Frontend Bugs   | frontend-developer    | react-component-architect |
| Database Issues | database-expert       | rails-activerecord-expert |
| Performance     | performance-optimizer | code-quality-reviewer     |
| Security        | security-reviewer     | config-security-expert    |

---

## User Experience & Design

### `premium-ux-designer`

::: tip Premium Interfaces
Transforma interfaces ordinary en expensive-looking experiences
:::

**Visual:** Sophisticated design · Subtle animations/micro-interactions · Typography/spacing/color psychology · Shadows/gradients/layering · Custom icons · Luxury principles (whitespace, premium typography)

**UX:** Simplify flows · Reduce cognitive load (progressive disclosure, smart defaults) · Optimize conversion · Intuitive navigation · Clear affordances · Smart forms · Behavioral psychology

**Technical:** Modern CSS/Framer Motion · 60fps animations · Responsive premium feel · Core Web Vitals optimization

**Methodology:** Audit → Define standards → Prioritize impact → Progressive enhancement → Validate → Performance optimization

---

### `design-review`

::: tip Elite Design Review
UX, visual design, accessibility, front-end implementation
:::

**Methodology:** "Live Environment First" - interactive experience antes de code analysis

**7 Phases:** Preparation (PR analysis, setup preview) → Interaction (user flow, states) → Responsiveness (1440px/768px/375px) → Visual polish (alignment, typography, hierarchy) → Accessibility (WCAG 2.1 AA, keyboard navigation, contrast) → Robustness (validation, overflow, edge cases) → Code health (reuse, design tokens) → Content/Console

**Communication:** Problems over prescriptions · Triage ([Blocker]/[High]/[Medium]/[Nitpick]) · Evidence-based (screenshots)

---

### `gsap-animation-architect`

::: tip GSAP Specialist
Advanced animations, scroll-driven experiences, performance optimization
:::

**Competencies:** Timeline orchestration · ScrollTrigger · Performance (transform/opacity) · Custom easing · Stagger patterns · Pin-based sections · Responsive animations

**Production:** Memory leak prevention (cleanup) · Centralized config · 60fps (GPU-accelerated) · Accessibility (prefers-reduced-motion) · Mobile optimization · Code splitting

**Standards:** TypeScript · React hooks (useGSAP) · ScrollTrigger.refresh() · Cleanup (kill individual triggers) · matchMedia · markers removed production

**Anti-Patterns:** ❌ Global ScrollTrigger.killAll() · ❌ Animate width/height · ❌ New instances every render · ❌ Missing cleanup · ❌ Ignore prefers-reduced-motion

**Verify docs:** https://gsap.com/docs/v3/ · https://gsap.com/react/

---

## Web & Application

### `typescript-pro`

::: tip TypeScript Master
Advanced types, generics, strict type safety, enterprise patterns
:::

**Focus:** Advanced types (generics, conditional, mapped) · Strict config · Type inference · Decorators · Module systems · Framework integration

**Output:** Strongly-typed code · Generic functions/classes · Custom utility types · Tests con type assertions · TSConfig optimization · Type declarations (.d.ts)

---

### `python-pro`

::: tip Python 3.12+ Expert
Modern features, async programming, performance optimization
:::

**Modern:** Python 3.12+ (improved errors, performance) · Async/await (asyncio/aiohttp/trio) · Dataclasses/Pydantic · Pattern matching · Type hints/generics · Descriptors/metaclasses · Generators/itertools

**Tooling:** uv (package manager) · ruff (formatting/linting) · mypy/pyright (type checking) · pyproject.toml · Pre-commit hooks

**Testing:** pytest + plugins · Hypothesis (property-based) · Fixtures/factories · Coverage (pytest-cov) · pytest-benchmark · CI (GitHub Actions)

---

### `javascript-pro`

::: tip Modern JavaScript
ES6+, async patterns, Node.js APIs
:::

**Focus:** ES6+ (destructuring, modules, classes) · Async (promises, async/await, generators) · Event loop · Node.js APIs · Browser APIs · TypeScript migration

**Output:** Modern JS con error handling · Async code sin race conditions · Module structure · Jest tests · Performance profiling · Polyfill strategy

---

### `php-pro`

::: tip PHP 8+ Master
Generators, iterators, SPL, modern OOP
:::

**Focus:** Generators/iterators (memory-efficient) · SPL data structures (SplQueue/SplStack/SplHeap) · PHP 8+ (match, enums, attributes) · Type system (union, intersection, never, mixed) · Advanced OOP (traits, late static binding) · Stream contexts · Performance profiling

**Approach:** Built-in functions first · Generators para large datasets · Strict typing · SPL cuando performance benefits · Profile antes optimizar

---

### `ruby-pro`

::: tip Ruby Master
Metaprogramming, Rails patterns, performance optimization
:::

**Focus:** Metaprogramming (modules, mixins, DSLs) · Rails patterns (ActiveRecord, controllers, views) · Gem development · Performance profiling · RSpec/Minitest · RuboCop

**Output:** Idiomatic Ruby · Rails MVC · RSpec/Minitest tests · Gem specs · Performance benchmarks (benchmark-ips) · Refactoring suggestions

---

## Tips de Uso

::: tip Selección Rápida
**Simple:** Agentes generales (backend-architect, frontend-developer)
**Complex:** Múltiples especialistas + quality reviewers
**Production-Critical:** SIEMPRE security + performance + observability
:::

### Combinaciones Poderosas

| Combinación                                    | Resultado                            |
| ---------------------------------------------- | ------------------------------------ |
| `backend-architect` + `database-optimizer`     | Scalable architecture                |
| `code-quality-reviewer` + `security-reviewer`  | Quality + Security gates             |
| `test-automator` + `playwright-test-generator` | Complete testing automation          |
| `shadcn-*` agents                              | Complete UI component implementation |

### Flujo Óptimo

**Diseño** → Architecture/design agents
**Implementación** → Development agents
**Quality** → Review agents (quality, security, edge-case)
**Testing** → Test automation agents
**Deployment** → DevOps agents
**Observability** → Performance/observability agents

---

::: info Última Actualización
**Fecha**: 2025-10-24 | **Agentes**: 45 | **Categorías**: 11
:::
