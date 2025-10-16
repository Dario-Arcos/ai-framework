# Guía de Agentes Especializados

::: tip Navegación Rápida
Usa esta guía para identificar el agente correcto para cada tarea. Todos los agentes están optimizados para ejecutarse de forma paralela cuando sea posible.
:::

_Extensa biblioteca de agentes especializados organizados por dominio y frecuencia de uso_

---

## Resumen Ejecutivo

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

## Architecture & System Design

### `backend-architect`

Diseño de APIs RESTful, límites de microservicios, esquemas de base de datos. Revisa arquitectura para escalabilidad y cuellos de botella de rendimiento.

::: tip Uso Proactivo
**Cuándo usar**: Al crear nuevos servicios backend o APIs.
:::

**Áreas de enfoque:**

- Diseño de API RESTful con versionado y manejo de errores adecuado
- Definición de límites de servicio y comunicación entre servicios
- Diseño de esquema de base de datos (normalización, índices, sharding)
- Estrategias de caché y optimización de rendimiento
- Patrones básicos de seguridad (autenticación, rate limiting)

**Salida:**

- Definiciones de endpoints API con ejemplos de request/response
- Diagrama de arquitectura de servicios (mermaid o ASCII)
- Esquema de base de datos con relaciones clave
- Recomendaciones de tecnología con justificación breve
- Cuellos de botella potenciales y consideraciones de escalamiento

---

### `frontend-developer`

Construye componentes React, layouts responsivos, gestión de estado client-side. Domina React 19, Next.js 15 y arquitectura frontend moderna.

::: tip Uso Proactivo
**Cuándo usar**: Al crear componentes UI o corregir issues frontend.
:::

**Capacidades principales:**

- React 19: Actions, Server Components, concurrent rendering
- Next.js 15: App Router, RSC, Server Actions, routing avanzado
- Arquitectura moderna: Atomic design, micro-frontends, design systems
- State management: Zustand, Jotai, React Query/TanStack Query
- Testing: React Testing Library, Playwright, Cypress
- Performance: Core Web Vitals, code splitting, image optimization

**Enfoque de desarrollo:**

1. Entender contexto y objetivos UX
2. Planear arquitectura de componentes antes de implementación
3. Usar patrones modernos de React/Next.js
4. Considerar rendimiento (bundle size, rendering optimization)
5. Incluir atributos ARIA y HTML semántico por defecto
6. Proporcionar estrategia de testing y casos clave

---

### `mobile-developer`

Desarrollo de apps móviles con React Native, Flutter o nativas. Domina desarrollo cross-platform, integraciones nativas, sincronización offline.

::: tip Uso Proactivo
**Cuándo usar**: Para features móviles, código cross-platform, o optimización de apps.
:::

**Expertise técnico:**

- **Cross-platform**: React Native (New Architecture), Flutter 3.x, Expo SDK 50+
- **Arquitectura**: Clean Architecture, MVVM/MVP/MVI, feature-based structure
- **Performance**: Memory management, battery optimization, launch time optimization
- **Device integration**: Camera, GPS, push notifications, biometric auth
- **Data management**: Offline-first, SQLite/Realm, background sync
- **App Store**: Submission processes, ASO, OTA updates

**Traits comportamentales:**

- Platform-agnostic pero respeta convenciones de plataforma
- Prioriza UX smooth y uso eficiente de recursos
- Implementa protección de datos y comunicación segura
- Construye apps que cumplen con guidelines de app stores

---

### `cloud-architect`

Experto en arquitectura cloud multi-cloud (AWS/Azure/GCP), IaC avanzado (Terraform/OpenTofu/CDK), optimización FinOps.

::: tip Uso Proactivo
**Cuándo usar**: Para arquitectura cloud, optimización de costos, planificación de migraciones, estrategias multi-cloud.
:::

**Expertise de plataforma:**

- **AWS**: EC2, Lambda, EKS, RDS, S3, VPC, Well-Architected Framework
- **Azure**: VMs, Functions, AKS, SQL Database, Virtual Network, ARM/Bicep
- **GCP**: Compute Engine, Cloud Functions, GKE, Cloud SQL, Cloud Storage
- **Multi-cloud**: Networking cross-cloud, replicación de datos, DR
- **Edge computing**: CloudFlare, CloudFront, Azure CDN, arquitecturas IoT

**Capacidades IaC:**

- Terraform/OpenTofu: Diseño avanzado de módulos, gestión de estado
- IaC nativo: CloudFormation, ARM/Bicep, Cloud Deployment Manager
- Modern IaC: AWS CDK, Azure CDK, Pulumi (TypeScript/Python/Go)
- GitOps: Automatización de infraestructura con ArgoCD, Flux
- Policy as Code: OPA, AWS Config, Azure Policy, GCP Organization Policy

---

### `graphql-architect`

Domina GraphQL moderno con federation, optimización de rendimiento y seguridad enterprise.

::: tip Uso Proactivo
**Cuándo usar**: Para arquitectura GraphQL o optimización de rendimiento.
:::

**Capacidades modernas:**

- **Federation**: Apollo Federation v2, GraphQL Fusion, composite schemas
- **Schema design**: Schema-first, interfaces, union types, Relay spec
- **Performance**: DataLoader (N+1 resolution), caching multi-tier, APQ
- **Security**: Field-level authorization, JWT, RBAC, rate limiting
- **Real-time**: GraphQL subscriptions con WebSocket/SSE, live queries

---

### `hybrid-cloud-architect`

Experto en soluciones híbridas complejas multi-cloud (AWS/Azure/GCP + clouds privadas como OpenStack/VMware).

::: tip Uso Proactivo
**Cuándo usar**: Para arquitectura híbrida, estrategia multi-cloud, o integración de infraestructura compleja.
:::

**Expertise multi-cloud:**

- **Public clouds**: AWS, Azure, GCP con integraciones cross-cloud avanzadas
- **Private clouds**: OpenStack (todos los servicios core), VMware vSphere/vCloud
- **Hybrid platforms**: Azure Arc, AWS Outposts, Google Anthos, VMware Cloud Foundation
- **Edge computing**: AWS Wavelength, Azure Edge Zones, Google Distributed Cloud Edge

**Expertise OpenStack profundo:**

- Core services: Nova, Neutron, Cinder, Swift
- Identity & management: Keystone, Horizon, Heat
- Advanced services: Octavia, Barbican, Magnum
- High availability: Multi-node deployments, clustering, DR
- Integration: APIs cross-cloud, hybrid identity management

---

### `kubernetes-architect`

Experto en infraestructura cloud-native, workflows GitOps avanzados (ArgoCD/Flux), orquestación enterprise de containers.

::: tip Uso Proactivo
**Cuándo usar**: Para arquitectura K8s, implementación GitOps, o diseño de plataformas cloud-native.
:::

**Expertise de plataforma:**

- **Managed K8s**: EKS (AWS), AKS (Azure), GKE (GCP) con configuración avanzada
- **Enterprise K8s**: Red Hat OpenShift, Rancher, VMware Tanzu
- **Self-managed**: kubeadm, kops, kubespray, bare-metal, air-gapped deployments
- **Multi-cluster**: Cluster API, fleet management, cross-cluster networking

**GitOps & Continuous Deployment:**

- **Tools**: ArgoCD, Flux v2, Jenkins X, Tekton
- **Principios OpenGitOps**: Declarativo, versionado, pull automático, reconciliación continua
- **Progressive delivery**: Argo Rollouts, Flagger, canary deployments, blue/green, A/B testing
- **Secret management**: External Secrets Operator, Sealed Secrets, Vault integration

---

### `agent-strategy-advisor`

Asesor estratégico para selección inteligente de agentes y planificación de trabajo. Analiza cualquier descripción de trabajo y recomienda agents óptimos con rationale detallado.

::: tip Herramienta Consultiva
**Cuándo usar**: Planificando trabajo complejo, aprendiendo ecosistema de agentes, o incierto qué agent usar.
:::

**Propósito:**

- NO ejecuta tareas (solo analiza y recomienda)
- SÍ genera planes estratégicos consultables
- SÍ educa sobre selección de agentes
- SÍ analiza ROI realista

**Input flexible:**

- tasks.md, free-form text, user stories, problem statements

**Output:**

Strategic plan con work analysis, recomendaciones de agentes, execution strategy, educational guide, honest assessment.

**Usage:**

```bash
/ai-framework:Task agent-strategy-advisor "Analiza mi tasks.md y recomienda agentes"
/ai-framework:Task agent-strategy-advisor "Build REST API with Python and PostgreSQL"
```

**Anti-Overengineering:**

- S ≤ 80 LOC: Main Claude suficiente
- Agent overhead = 5-10 min → Usar solo si ROI > 1.5x

---

## Code Review & Security

### `code-quality-reviewer`

Reviewer de calidad de código esencial enfocado en principios universales que previenen deuda técnica.

::: tip Uso Proactivo
**Cuándo usar**: Antes de PRs, auditorías de código, validación arquitectónica.
:::

**Dimensiones de calidad (todas igualmente críticas):**

**Code Structure & Architecture:**

- Código simple y legible con naming descriptivo
- Single responsibility por función/clase (<50 líneas)
- No código duplicado (principio DRY)
- Magic numbers reemplazados con constantes nombradas
- No god objects (<300 líneas) ni dependencias circulares

**Error Handling & Resilience:**

- Tipos de error específicos con mensajes significativos
- Cleanup adecuado de recursos (memoria, archivos, conexiones)
- Degradación elegante y retry logic para failures

**Security & Performance:**

- Sin secrets o credenciales expuestas
- Validación de input y prevención de SQL injection
- Sin anti-patrones de performance (N+1 queries, memory leaks)
- Async/await para operaciones I/O

**Testing & Documentation:**

- Cobertura de tests para happy path y edge cases
- Separación clara de concerns entre capas
- Documentación actualizada para cambios significativos

**Output format:**

- **CRITICAL**: Vulnerabilidades de seguridad, issues que causan inestabilidad del sistema
- ⚠️ **HIGH PRIORITY**: Deuda técnica que incrementa costo de mantenimiento
- **SUGGESTIONS**: Mejoras de legibilidad, oportunidades de optimización

---

### `architect-review`

Arquitecto de software maestro especializando en patrones de arquitectura modernos, clean architecture, microservicios, sistemas event-driven, y DDD.

::: tip Uso Proactivo
**Cuándo usar**: Para decisiones arquitectónicas y revisiones de diseño de sistema.
:::

**Patrones de arquitectura modernos:**

- Clean Architecture y Hexagonal Architecture
- Microservices con límites de servicio apropiados
- Event-driven architecture (EDA) con event sourcing y CQRS
- Domain-Driven Design (DDD) con bounded contexts
- Serverless architecture patterns y FaaS design
- API-first design con GraphQL, REST, gRPC
- Layered architecture con separación de concerns adecuada

**Diseño de sistemas distribuidos:**

- Service mesh con Istio, Linkerd, Consul Connect
- Event streaming con Kafka, Pulsar, NATS
- Patrones de datos distribuidos: Saga, Outbox, Event Sourcing
- Circuit breaker, bulkhead, timeout patterns para resiliencia
- Distributed caching con Redis Cluster, Hazelcast
- Load balancing y service discovery patterns

**Principios SOLID & Design Patterns:**

- Single Responsibility, Open/Closed, Liskov Substitution
- Interface Segregation, Dependency Inversion
- Repository, Unit of Work, Specification patterns
- Factory, Strategy, Observer, Command patterns
- Decorator, Adapter, Facade patterns
- Dependency Injection e Inversion of Control

---

### `security-reviewer`

Completa revisión de seguridad de los cambios pendientes en la rama actual.

::: tip Uso Proactivo
**Cuándo usar**: Antes de merge, después de cambios críticos, auditorías de seguridad.
:::

**Categorías de seguridad examinadas:**

**Input Validation Vulnerabilities:**

- SQL injection via unsanitized input
- Command injection en system calls o subprocesos
- XXE injection en XML parsing
- Template injection en templating engines
- NoSQL injection en database queries
- Path traversal en file operations

**Authentication & Authorization Issues:**

- Authentication bypass logic
- Privilege escalation paths
- Session management flaws
- JWT token vulnerabilities
- Authorization logic bypasses

**Crypto & Secrets Management:**

- Hardcoded API keys, passwords, tokens
- Weak cryptographic algorithms
- Improper key storage or management
- Cryptographic randomness issues
- Certificate validation bypasses

**Injection & Code Execution:**

- Remote code execution via deserialization
- Pickle injection en Python
- YAML deserialization vulnerabilities
- Eval injection en dynamic code execution
- XSS vulnerabilities (reflected, stored, DOM-based)

**Data Exposure:**

- Sensitive data logging o storage
- PII handling violations
- API endpoint data leakage
- Debug information exposure

**Methodology:**

1. **Repository Context Research**: Framework/libraries in use, patterns existentes
2. **Comparative Analysis**: Nuevos cambios vs patterns de seguridad establecidos
3. **Vulnerability Assessment**: Examinar cada archivo modificado para implicaciones de seguridad

**Output format:**

```markdown
# Vuln 1: XSS: `file.py:42`

- Severity: High
- Description: [detailed vulnerability description]
- Exploit Scenario: [concrete attack scenario]
- Recommendation: [specific fix recommendation]
```

**Severity Guidelines:**

- **HIGH**: Directly exploitable → RCE, data breach, authentication bypass
- **MEDIUM**: Require conditions específicas pero impact significativo
- **LOW**: Defense-in-depth issues o lower-impact vulnerabilities

---

### `config-security-expert`

Especialista en seguridad de configuración enfocado en prevenir outages de producción.

::: tip Uso Proactivo
**Cuándo usar**: Antes de producción, auditorías, compliance.
:::

**Detección de archivos de alto riesgo:**

```yaml
Configuration Security Domain:
  Container & Orchestration:
    - docker-compose*.yml
    - **/Dockerfile*
    - **/.env*
    - **/config/*.{yml,yaml}

  Infrastructure as Code:
    - terraform/**/*.tf
    - k8s/**/*.yaml
    - **/helm/**/*.yaml

  Database & Cache:
    - **/*database*.{yml,yaml}
    - **/*redis*.conf
    - **/application*.{yml,yaml,properties}
```

**Protocolo de detección de magic numbers:**
Para CUALQUIER cambio de valor numérico:

```
Numeric Change Detected:
├─ Value decreased? → HIGH RISK (capacity reduction)
├─ Value increased >50%? → HIGH RISK (resource overload)
├─ No evidence provided? → REQUIRE JUSTIFICATION
└─ Evidence present? → VALIDATE against production patterns
```

**Critical vulnerability patterns:**

- **Connection Pools**: Pool size reduced → connection starvation
- **Security Risks**: Debug mode in production, wildcard host allowlists
- **Resource Limits**: Memory limits sin load profiling
- **Cache TTLs**: Mismatched to usage patterns

**Framework de preguntas obligatorias:**

1. ¿Por qué este valor específico?
2. ¿Ha sido testeado bajo carga similar a producción?
3. ¿Está dentro de rangos recomendados?
4. ¿Qué pasa cuando se alcanza este límite?
5. ¿Cuál es el plan de rollback?

---

### `edge-case-detector`

Detector especializado de edge cases críticos de producción que causan silent failures y data corruption.

::: tip Uso Proactivo
**Cuándo usar**: Testing crítico, validación, escenarios de failure.
:::

**Categorías críticas de edge cases:**

**Boundary & Data Conditions:**

- Off-by-one errors en loops y array access
- Division by zero y integer overflow scenarios
- Null/empty collection handling en todo el data flow
- Array bounds violations y buffer overruns

**Concurrency & Threading:**

- Race conditions en shared state mutations
- Deadlock potential con múltiples resource locks
- Thread safety violations en singleton patterns
- Database transaction isolation failures

**Integration & External Dependencies:**

- Network timeouts sin proper retry logic
- External API unavailability causando cascading failures
- Partial response handling y data corruption scenarios
- Service degradation impact en dependent systems

**Structured analysis framework:**

**Boundary Conditions:**

- "¿Qué pasa con valores mínimo/máximo de input?"
- "¿Cómo se comporta el sistema con datos empty/null/undefined?"
- "¿Los bounds de array y colecciones están validados apropiadamente?"

**Concurrency Analysis:**

- "¿Pueden múltiples threads/procesos modificar estos datos simultáneamente?"
- "¿Qué pasa si dos operaciones intentan el mismo recurso?"
- "¿Las transacciones de database están aisladas apropiadamente?"

**Integration Resilience:**

- "¿Qué si los servicios externos están unavailable o slow?"
- "¿Cómo se manejan partial responses o corrupted data?"
- "¿Los retry attempts están bounded para prevenir infinite loops?"

**Failure Recovery:**

- "¿El sistema queda en estado consistente después de failures?"
- "¿Los recursos se cleanup apropiadamente en todos los error paths?"
- "¿Esto puede fail silently y corromper data downstream?"

---

## Database Management

### `database-optimizer`

Experto en optimización de bases de datos especializando en tuning moderno de rendimiento, optimización de queries, y arquitecturas escalables.

::: tip Uso Proactivo
**Cuándo usar**: Para optimización de BD, issues de performance, o desafíos de escalabilidad.
:::

**Advanced Query Optimization:**

- Análisis de execution plan: EXPLAIN ANALYZE, query planning, cost-based optimization
- Query rewriting: Subquery optimization, JOIN optimization, CTE performance
- Patrones complejos: Window functions, recursive queries, analytical functions
- Cross-database optimization: PostgreSQL, MySQL, SQL Server, Oracle-specific
- NoSQL query optimization: MongoDB aggregation pipelines, DynamoDB query patterns
- Cloud database optimization: RDS, Aurora, Azure SQL, Cloud SQL tuning específico

**Modern Indexing Strategies:**

- Advanced indexing: B-tree, Hash, GiST, GIN, BRIN indexes, covering indexes
- Composite indexes: Multi-column indexes, index column ordering, partial indexes
- Specialized indexes: Full-text search, JSON/JSONB indexes, spatial indexes
- Index maintenance: Index bloat management, rebuilding strategies, statistics updates
- Cloud-native indexing: Aurora indexing, Azure SQL intelligent indexing
- NoSQL indexing: MongoDB compound indexes, DynamoDB GSI/LSI optimization

**Performance Analysis & Monitoring:**

- Query performance: pg_stat_statements, MySQL Performance Schema, SQL Server DMVs
- Real-time monitoring: Active query analysis, blocking query detection
- Performance baselines: Historical performance tracking, regression detection
- APM integration: DataDog, New Relic database monitoring, custom metrics
- Cost analysis: Query cost analysis, resource utilization optimization
- Automated tuning: AWS Performance Insights, Azure SQL Database Advisor

---

### `database-admin`

Experto en administración de bases de datos especializando en databases cloud modernas, automatización, y reliability engineering.

::: tip Uso Proactivo
**Cuándo usar**: Para arquitectura de BD, operaciones, o reliability engineering.
:::

**Cloud Database Platforms:**

- **AWS**: RDS (PostgreSQL, MySQL, Oracle, SQL Server), Aurora, DynamoDB, DocumentDB, ElastiCache
- **Azure**: Azure SQL Database, PostgreSQL, MySQL, Cosmos DB, Redis Cache
- **GCP**: Cloud SQL, Cloud Spanner, Firestore, BigQuery, Cloud Memorystore
- **Multi-cloud**: Cross-cloud replication, disaster recovery, data synchronization
- **Database migration**: AWS DMS, Azure Database Migration, GCP Database Migration Service

**Modern Database Technologies:**

- **Relational**: PostgreSQL, MySQL, SQL Server, Oracle, MariaDB optimization
- **NoSQL**: MongoDB, Cassandra, DynamoDB, CosmosDB, Redis operations
- **NewSQL**: CockroachDB, TiDB, Google Spanner, distributed SQL systems
- **Time-series**: InfluxDB, TimescaleDB, Amazon Timestream operations
- **Graph**: Neo4j, Amazon Neptune, Azure Cosmos DB Gremlin API
- **Search**: Elasticsearch, OpenSearch, Amazon CloudSearch administration

**Infrastructure as Code for Databases:**

- **Database provisioning**: Terraform, CloudFormation, ARM templates
- **Schema management**: Flyway, Liquibase, automated migrations y versioning
- **Configuration management**: Ansible, Chef, Puppet para database config automation
- **GitOps for databases**: Database config y schema changes via Git workflows
- **Container databases**: Docker databases, Kubernetes operators, Helm charts
- **Backup automation**: Automated backup scheduling, cross-region replication, PITR

---

## DevOps & Deployment

### `deployment-engineer`

Experto en ingeniería de deployment especializando en CI/CD pipelines modernos, workflows GitOps, y automatización avanzada de deployment.

::: tip Uso Proactivo
**Cuándo usar**: Para diseño CI/CD, implementación GitOps, o automatización de deployment.
:::

**Modern CI/CD Platforms:**

- **GitHub Actions**: Advanced workflows, reusable actions, self-hosted runners, security scanning
- **GitLab CI/CD**: Pipeline optimization, DAG pipelines, multi-project pipelines
- **Azure DevOps**: YAML pipelines, template libraries, environment approvals
- **Jenkins**: Pipeline as Code, Blue Ocean, distributed builds
- **Platform-specific**: AWS CodePipeline, GCP Cloud Build, Tekton, Argo Workflows
- **Emerging**: Buildkite, CircleCI, Drone CI, Harness, Spinnaker

**GitOps & Continuous Deployment:**

- **Tools**: ArgoCD, Flux v2, Jenkins X con configuración avanzada
- **Repository patterns**: App-of-apps, mono-repo vs multi-repo, environment promotion
- **Automated deployment**: Progressive delivery, automated rollbacks, deployment policies
- **Configuration management**: Helm, Kustomize, Jsonnet para configs environment-specific
- **Secret management**: External Secrets Operator, Sealed Secrets, vault integration

**Container Technologies:**

- **Docker mastery**: Multi-stage builds, BuildKit, security best practices, image optimization
- **Alternative runtimes**: Podman, containerd, CRI-O, gVisor para enhanced security
- **Image management**: Registry security, vulnerability scanning, image signing con Cosign
- **Container orchestration**: Kubernetes deployment strategies, Helm charts, operators
- **Security scanning**: Trivy, Twistlock, Aqua Security, container compliance scanning

---

### `devops-troubleshooter`

Experto en troubleshooting DevOps especializando en respuesta rápida a incidentes, debugging avanzado, y observabilidad moderna.

::: tip Uso Proactivo
**Cuándo usar**: Para debugging, respuesta a incidentes, o troubleshooting de sistemas.
:::

**Modern Observability & Monitoring:**

- **Logging platforms**: ELK Stack, Loki/Grafana, Fluentd/Fluent Bit
- **APM solutions**: DataDog, New Relic, Dynatrace, AppDynamics, Instana, Honeycomb
- **Metrics & monitoring**: Prometheus, Grafana, InfluxDB, VictoriaMetrics, Thanos
- **Distributed tracing**: Jaeger, Zipkin, AWS X-Ray, OpenTelemetry, custom tracing
- **Cloud-native observability**: OpenTelemetry collector, service mesh observability
- **Synthetic monitoring**: Pingdom, Datadog Synthetics, custom health checks

**Container & Kubernetes Debugging:**

- **kubectl mastery**: Advanced debugging commands, resource inspection, troubleshooting workflows
- **Container runtime debugging**: Docker, containerd, CRI-O, runtime-specific issues
- **Pod troubleshooting**: Init containers, sidecar issues, resource constraints, networking
- **Service mesh debugging**: Istio, Linkerd, Consul Connect traffic y security issues
- **Kubernetes networking**: CNI troubleshooting, service discovery, ingress issues
- **Storage debugging**: Persistent volume issues, storage class problems, data corruption

**Network & DNS Troubleshooting:**

- **Network analysis**: tcpdump, Wireshark, nslookup, dig, traceroute, ping analysis
- **DNS resolution**: CoreDNS debugging, external DNS, service discovery issues
- **Load balancer debugging**: HAProxy, nginx, cloud load balancer configuration
- **SSL/TLS issues**: Certificate validation, cipher suite problems, handshake failures
- **Firewall y security groups**: iptables, cloud security group troubleshooting

---

### `dx-optimizer`

Especialista en Developer Experience. Mejora tooling, setup, y workflows.

::: tip Uso Proactivo
**Cuándo usar**: Al configurar nuevos proyectos, después de feedback del equipo, o cuando se nota friction en desarrollo.
:::

**Áreas de optimización:**

**Environment Setup:**

- Simplificar onboarding a < 5 minutos
- Crear defaults inteligentes
- Automatizar instalación de dependencias
- Agregar mensajes de error útiles

**Development Workflows:**

- Identificar tareas repetitivas para automatizar
- Crear aliases y shortcuts útiles
- Optimizar tiempos de build y test
- Mejorar hot reload y feedback loops

**Tooling Enhancement:**

- Configurar settings de IDE y extensions
- Setup de git hooks para checks comunes
- Crear comandos CLI específicos del proyecto
- Integrar herramientas de desarrollo útiles

**Documentation:**

- Generar guías de setup que realmente funcionen
- Crear ejemplos interactivos
- Agregar inline help a custom commands
- Mantener guías de troubleshooting actualizadas

**Success Metrics:**

- Time from clone to running app
- Número de pasos manuales eliminados
- Build/test execution time
- Developer satisfaction feedback

---

### `terraform-specialist`

Experto Terraform/OpenTofu especializando en automatización IaC avanzada, gestión de estado, y patrones de infraestructura enterprise.

::: tip Uso Proactivo
**Cuándo usar**: Para IaC avanzado, gestión de estado, o automatización de infraestructura.
:::

**Terraform/OpenTofu Expertise:**

- **Core concepts**: Resources, data sources, variables, outputs, locals, expressions
- **Advanced features**: Dynamic blocks, for_each loops, conditional expressions, complex type constraints
- **State management**: Remote backends, state locking, state encryption, workspace strategies
- **Module development**: Composition patterns, versioning strategies, testing frameworks
- **Provider ecosystem**: Official y community providers, custom provider development
- **OpenTofu migration**: Terraform a OpenTofu migration strategies, compatibility considerations

**Advanced Module Design:**

- **Module architecture**: Hierarchical module design, root modules, child modules
- **Composition patterns**: Module composition, dependency injection, interface segregation
- **Reusability**: Generic modules, environment-specific configurations, module registries
- **Testing**: Terratest, unit testing, integration testing, contract testing
- **Documentation**: Auto-generated documentation, examples, usage patterns
- **Versioning**: Semantic versioning, compatibility matrices, upgrade guides

**State Management & Security:**

- **Backend configuration**: S3, Azure Storage, GCS, Terraform Cloud, Consul, etcd
- **State encryption**: Encryption at rest, encryption in transit, key management
- **State locking**: DynamoDB, Azure Storage, GCS, Redis locking mechanisms
- **State operations**: Import, move, remove, refresh, advanced state manipulation
- **Backup strategies**: State backup, disaster recovery, state corruption prevention
- **Security scanning**: tfsec, Checkov, Terrascan, policy enforcement con Sentinel/OPA

---

## Documentation & Technical Writing

### `docs-architect`

Crea documentación técnica comprensiva desde codebases existentes. Analiza arquitectura, design patterns, e implementation details para producir manuales técnicos y ebooks long-form.

::: tip Uso Proactivo
**Cuándo usar**: Para documentación de sistema, architecture guides, o technical deep-dives.
:::

**Core Competencies:**

1. **Codebase Analysis**: Deep understanding de code structure, patterns, decisiones arquitectónicas
2. **Technical Writing**: Explicaciones claras y precisas para audiencias técnicas variadas
3. **System Thinking**: Capacidad de ver y documentar el big picture mientras explica detalles
4. **Documentation Architecture**: Organizar información compleja en estructuras navegables y digestibles
5. **Visual Communication**: Crear y describir architectural diagrams y flowcharts

**Documentation Process:**

1. **Discovery Phase**:
   - Analizar estructura del codebase y dependencias
   - Identificar componentes clave y sus relaciones
   - Extraer design patterns y decisiones arquitectónicas
   - Mapear data flows e integration points

2. **Structuring Phase**:
   - Crear jerarquía lógica de capítulos/secciones
   - Diseñar progressive disclosure de complejidad
   - Planear diagramas y ayudas visuales
   - Establecer terminología consistente

3. **Writing Phase**:
   - Comenzar con executive summary y overview
   - Progresar de high-level architecture a implementation details
   - Incluir rationale para design decisions
   - Agregar code examples con explicaciones exhaustivas

**Output Characteristics:**

- **Length**: Documentos comprehensivos (10-100+ páginas)
- **Depth**: Desde bird's-eye view a implementation specifics
- **Style**: Technical pero accesible, con complejidad progresiva
- **Format**: Estructurado con chapters, sections, y cross-references
- **Visuals**: Architectural diagrams, sequence diagrams, flowcharts (descritos en detalle)

**Key Sections to Include:**

1. Executive Summary: One-page overview para stakeholders
2. Architecture Overview: System boundaries, key components, interacciones
3. Design Decisions: Rationale detrás de elecciones arquitectónicas
4. Core Components: Deep dive en cada módulo/servicio principal
5. Data Models: Schema design y data flow documentation
6. Integration Points: APIs, external services, data pipelines
7. Security Architecture: Authentication, authorization, data protection
8. Deployment & Operations: Infrastructure, scaling, monitoring
9. Development Guide: Local setup, testing, contribution guidelines
10. Appendices: Glossary, references, configuraciones detalladas

---

### `api-documenter`

Domina documentación de API con OpenAPI 3.1, herramientas powered por AI, y prácticas modernas de developer experience.

::: tip Uso Proactivo
**Cuándo usar**: Para documentación de API o creación de developer portal.
:::

**Modern Documentation Standards:**

- OpenAPI 3.1+ specification authoring con features avanzadas
- API-first design documentation con contract-driven development
- AsyncAPI specifications para event-driven y real-time APIs
- GraphQL schema documentation y SDL best practices
- JSON Schema validation y documentation integration
- Webhook documentation con payload examples y security considerations
- API lifecycle documentation desde design a deprecation

**AI-Powered Documentation Tools:**

- AI-assisted content generation con tools como Mintlify y ReadMe AI
- Automated documentation updates desde code comments y annotations
- Natural language processing para developer-friendly explanations
- AI-powered code example generation across múltiples lenguajes
- Intelligent content suggestions y consistency checking
- Automated testing de documentation examples y code snippets
- Smart content translation y localization workflows

**Interactive Documentation Platforms:**

- Swagger UI y Redoc customization y optimization
- Stoplight Studio para collaborative API design y documentation
- Insomnia y Postman collection generation y maintenance
- Custom documentation portals con frameworks como Docusaurus
- API Explorer interfaces con live testing capabilities
- Try-it-now functionality con authentication handling
- Interactive tutorials y onboarding experiences

**Developer Portal Architecture:**

- Comprehensive developer portal design y information architecture
- Multi-API documentation organization y navigation
- User authentication y API key management integration
- Community features incluyendo forums, feedback, support
- Analytics y usage tracking para documentation effectiveness
- Search optimization y discoverability enhancements
- Mobile-responsive documentation design

---

### `mermaid-expert`

Crea diagramas Mermaid para flowcharts, sequences, ERDs, y architectures. Domina syntax para todos los diagram types y styling.

::: tip Uso Proactivo
**Cuándo usar**: Para documentación visual, system diagrams, o process flows.
:::

**Focus Areas:**

- Flowcharts y decision trees
- Sequence diagrams para APIs/interactions
- Entity Relationship Diagrams (ERD)
- State diagrams y user journeys
- Gantt charts para project timelines
- Architecture y network diagrams

**Diagram Types Expertise:**

```
graph (flowchart), sequenceDiagram, classDiagram,
stateDiagram-v2, erDiagram, gantt, pie,
gitGraph, journey, quadrantChart, timeline
```

**Approach:**

1. Elegir el diagram type correcto para los datos
2. Mantener diagramas legibles - evitar overcrowding
3. Usar styling y colores consistentes
4. Agregar labels y descriptions significativos
5. Testear rendering antes de delivery

**Output:**

- Complete Mermaid diagram code
- Rendering instructions/preview
- Alternative diagram options
- Styling customizations
- Accessibility considerations
- Export recommendations

---

### `reference-builder`

Crea referencias técnicas exhaustivas y documentación de API. Genera comprehensive parameter listings, configuration guides, y searchable reference materials.

::: tip Uso Proactivo
**Cuándo usar**: Para API docs, configuration references, o complete technical specifications.
:::

**Core Capabilities:**

1. **Exhaustive Coverage**: Documentar cada parameter, method, y configuration option
2. **Precise Categorization**: Organizar información para quick retrieval
3. **Cross-Referencing**: Linkear conceptos relacionados y dependencias
4. **Example Generation**: Proveer examples para cada feature documentada
5. **Edge Case Documentation**: Cubrir limits, constraints, y special cases

**Reference Documentation Types:**

**API References:**

- Complete method signatures con todos los parameters
- Return types y possible values
- Error codes y exception handling
- Rate limits y performance characteristics
- Authentication requirements

**Configuration Guides:**

- Every configurable parameter
- Default values y valid ranges
- Environment-specific settings
- Dependencies entre settings
- Migration paths para deprecated options

**Schema Documentation:**

- Field types y constraints
- Validation rules
- Relationships y foreign keys
- Indexes y performance implications
- Evolution y versioning

**Entry Format:**

```markdown
### [Feature/Method/Parameter Name]

**Type**: [Data type o signature]
**Default**: [Default value if applicable]
**Required**: [Yes/No]
**Since**: [Version introduced]
**Deprecated**: [Version if deprecated]

**Description**:
[Comprehensive description de purpose y behavior]

**Parameters**:

- `paramName` (type): Description [constraints]

**Returns**:
[Return type y description]

**Throws**:

- `ExceptionType`: When this occurs

**Examples**:
[Multiple examples showing different use cases]

**See Also**:

- [Related Feature 1]
- [Related Feature 2]
```

---

### `tutorial-engineer`

Crea step-by-step tutorials y educational content desde código. Transforma conceptos complejos en progressive learning experiences con hands-on examples.

::: tip Uso Proactivo
**Cuándo usar**: Para onboarding guides, feature tutorials, o concept explanations.
:::

**Core Expertise:**

1. **Pedagogical Design**: Understanding de cómo developers aprenden y retienen información
2. **Progressive Disclosure**: Breaking complex topics en digestible, sequential steps
3. **Hands-On Learning**: Crear practical exercises que refuerzan conceptos
4. **Error Anticipation**: Predecir y addressing common mistakes
5. **Multiple Learning Styles**: Soportar visual, textual, y kinesthetic learners

**Tutorial Development Process:**

1. **Learning Objective Definition**:
   - Identificar qué readers podrán hacer después del tutorial
   - Definir prerequisites y assumed knowledge
   - Crear measurable learning outcomes

2. **Concept Decomposition**:
   - Break complex topics en atomic concepts
   - Arrange en logical learning sequence
   - Identificar dependencies entre conceptos

3. **Exercise Design**:
   - Crear hands-on coding exercises
   - Build desde simple a complex
   - Incluir checkpoints para self-assessment

**Tutorial Structure:**

**Opening Section:**

- **What You'll Learn**: Clear learning objectives
- **Prerequisites**: Required knowledge y setup
- **Time Estimate**: Realistic completion time
- **Final Result**: Preview de lo que construirán

**Progressive Sections:**

1. **Concept Introduction**: Theory con real-world analogies
2. **Minimal Example**: Simplest working implementation
3. **Guided Practice**: Step-by-step walkthrough
4. **Variations**: Exploring different approaches
5. **Challenges**: Self-directed exercises
6. **Troubleshooting**: Common errors y solutions

**Closing Section:**

- **Summary**: Key concepts reinforced
- **Next Steps**: Where to go from here
- **Additional Resources**: Deeper learning paths

**Writing Principles:**

- **Show, Don't Tell**: Demonstrate con código, then explain
- **Fail Forward**: Include intentional errors para teach debugging
- **Incremental Complexity**: Each step builds en el previous
- **Context First**: Explain el "why" before el "how"
- **Multiple Paths**: Acknowledge different approaches y preferences

---

## Incident Response & Network

### `incident-responder`

Experto SRE incident responder especializando en rapid problem resolution, modern observability, y comprehensive incident management.

::: danger Uso Inmediato
**Cuándo usar**: INMEDIATAMENTE para production incidents o SRE practices.
:::

**Immediate Actions (First 5 minutes):**

**1. Assess Severity & Impact:**

- **User impact**: Affected user count, geographic distribution, user journey disruption
- **Business impact**: Revenue loss, SLA violations, customer experience degradation
- **System scope**: Services affected, dependencies, blast radius assessment
- **External factors**: Peak usage times, scheduled events, regulatory implications

**2. Establish Incident Command:**

- **Incident Commander**: Single decision-maker, coordina response
- **Communication Lead**: Maneja stakeholder updates y external communication
- **Technical Lead**: Coordina technical investigation y resolution
- **War room setup**: Communication channels, video calls, shared documents

**3. Immediate Stabilization:**

- **Quick wins**: Traffic throttling, feature flags, circuit breakers
- **Rollback assessment**: Recent deployments, configuration changes, infrastructure changes
- **Resource scaling**: Auto-scaling triggers, manual scaling, load redistribution
- **Communication**: Initial status page update, internal notifications

**Modern Investigation Protocol:**

**Observability-Driven Investigation:**

- **Distributed tracing**: OpenTelemetry, Jaeger, Zipkin para request flow analysis
- **Metrics correlation**: Prometheus, Grafana, DataDog para pattern identification
- **Log aggregation**: ELK, Splunk, Loki para error pattern analysis
- **APM analysis**: Application performance monitoring para bottleneck identification
- **Real User Monitoring**: User experience impact assessment y prioritization

---

### `network-engineer`

Experto network engineer especializando en modern cloud networking, security architectures, y performance optimization.

::: tip Uso Proactivo
**Cuándo usar**: Para network design, connectivity issues, o performance optimization.
:::

**Cloud Networking Expertise:**

- **AWS networking**: VPC, subnets, route tables, NAT gateways, Internet gateways, VPC peering, Transit Gateway
- **Azure networking**: Virtual networks, subnets, NSGs, Azure Load Balancer, Application Gateway, VPN Gateway
- **GCP networking**: VPC networks, Cloud Load Balancing, Cloud NAT, Cloud VPN, Cloud Interconnect
- **Multi-cloud networking**: Cross-cloud connectivity, hybrid architectures, network peering
- **Edge networking**: CDN integration, edge computing, 5G networking, IoT connectivity

**Modern Load Balancing:**

- **Cloud load balancers**: AWS ALB/NLB/CLB, Azure Load Balancer/Application Gateway, GCP Cloud Load Balancing
- **Software load balancers**: Nginx, HAProxy, Envoy Proxy, Traefik, Istio Gateway
- **Layer 4/7 load balancing**: TCP/UDP load balancing, HTTP/HTTPS application load balancing
- **Global load balancing**: Multi-region traffic distribution, geo-routing, failover strategies
- **API gateways**: Kong, Ambassador, AWS API Gateway, Azure API Management, Istio Gateway

**DNS & Service Discovery:**

- **DNS systems**: BIND, PowerDNS, cloud DNS services (Route 53, Azure DNS, Cloud DNS)
- **Service discovery**: Consul, etcd, Kubernetes DNS, service mesh service discovery
- **DNS security**: DNSSEC, DNS over HTTPS, DNS over TLS, DNS filtering y monitoring
- **Traffic routing**: Weighted routing, geolocation routing, health check-based routing
- **CDN integration**: CloudFlare, AWS CloudFront, Azure CDN, performance optimization

---

## Performance & Observability

### `performance-engineer`

Experto performance engineer especializando en modern observability, application optimization, y scalable system performance.

::: tip Uso Proactivo
**Cuándo usar**: Para performance optimization, observability, o scalability challenges.
:::

**Modern Observability & Monitoring:**

- **OpenTelemetry**: Distributed tracing, metrics collection, correlation across services
- **APM platforms**: DataDog APM, New Relic, Dynatrace, AppDynamics, Honeycomb, Jaeger
- **Metrics & monitoring**: Prometheus, Grafana, InfluxDB, custom metrics, SLI/SLO tracking
- **Real User Monitoring (RUM)**: User experience tracking, Core Web Vitals, page load analytics
- **Synthetic monitoring**: Uptime monitoring, API testing, user journey simulation
- **Log correlation**: Structured logging, distributed log tracing, error correlation

**Advanced Application Profiling:**

- **CPU profiling**: Flame graphs, call stack analysis, hotspot identification
- **Memory profiling**: Heap analysis, garbage collection tuning, memory leak detection
- **I/O profiling**: Disk I/O optimization, network latency analysis, database query profiling
- **Language-specific profiling**: JVM profiling, Python profiling, Node.js profiling, Go profiling
- **Container profiling**: Docker performance analysis, Kubernetes resource optimization
- **Cloud profiling**: AWS X-Ray, Azure Application Insights, GCP Cloud Profiler

**Modern Load Testing & Performance Validation:**

- **Load testing tools**: k6, JMeter, Gatling, Locust para comprehensive performance testing
- **Stress testing**: Breaking point analysis, capacity planning, resource saturation testing
- **Performance regression testing**: Automated performance validation en CI/CD pipelines
- **Chaos engineering**: Resilience testing, failure injection, system reliability validation

---

### `observability-engineer`

Construye production-ready monitoring, logging, y tracing systems. Implementa comprehensive observability strategies, SLI/SLO management, y incident response workflows.

::: tip Uso Proactivo
**Cuándo usar**: Para monitoring infrastructure, performance optimization, o production reliability.
:::

**Monitoring & Metrics Infrastructure:**

- Prometheus ecosystem con advanced PromQL queries y recording rules
- Grafana dashboard design con templating, alerting, y custom panels
- InfluxDB time-series data management y retention policies
- DataDog enterprise monitoring con custom metrics y synthetic monitoring
- New Relic APM integration y performance baseline establishment
- CloudWatch comprehensive AWS service monitoring y cost optimization
- Nagios y Zabbix para traditional infrastructure monitoring
- Custom metrics collection con StatsD, Telegraf, y Collectd
- High-cardinality metrics handling y storage optimization

**Distributed Tracing & APM:**

- Jaeger distributed tracing deployment y trace analysis
- Zipkin trace collection y service dependency mapping
- AWS X-Ray integration para serverless y microservice architectures
- OpenTracing y OpenTelemetry instrumentation standards
- Application Performance Monitoring con detailed transaction tracing
- Service mesh observability con Istio y Envoy telemetry
- Correlation entre traces, logs, y metrics para root cause analysis
- Performance bottleneck identification y optimization recommendations
- Distributed system debugging y latency analysis

**Log Management & Analysis:**

- ELK Stack (Elasticsearch, Logstash, Kibana) architecture y optimization
- Fluentd y Fluent Bit log forwarding y parsing configurations
- Splunk enterprise log management y search optimization
- Loki para cloud-native log aggregation con Grafana integration
- Log parsing, enrichment, y structured logging implementation
- Centralized logging para microservices y distributed systems

---

### `web-search-specialist`

Experto web researcher usando advanced search techniques y synthesis. Domina search operators, result filtering, y multi-source verification.

::: tip Uso Proactivo
**Cuándo usar**: Para deep research, information gathering, o trend analysis.
:::

**Focus Areas:**

- Advanced search query formulation
- Domain-specific searching y filtering
- Result quality evaluation y ranking
- Information synthesis across sources
- Fact verification y cross-referencing
- Historical y trend analysis

**Search Strategies:**

**Query Optimization:**

- Use specific phrases en quotes para exact matches
- Exclude irrelevant terms con negative keywords
- Target specific timeframes para recent/historical data
- Formulate multiple query variations

**Domain Filtering:**

- allowed_domains para trusted sources
- blocked_domains para exclude unreliable sites
- Target specific sites para authoritative content
- Academic sources para research topics

**WebFetch Deep Dive:**

- Extract full content desde promising results
- Parse structured data desde pages
- Follow citation trails y references
- Capture data before it changes

**Approach:**

1. Understand el research objective clearly
2. Create 3-5 query variations para coverage
3. Search broadly first, then refine
4. Verify key facts across multiple sources
5. Track contradictions y consensus

**Output:**

- Research methodology y queries used
- Curated findings con source URLs
- Credibility assessment de sources
- Synthesis highlighting key insights
- Contradictions o gaps identified
- Data tables o structured summaries
- Recommendations para further research

---

## Shadcn-UI Components

### `shadcn-requirements-analyzer`

Analiza complex UI feature requests y break down en structured shadcn component requirements. Traduce high-level design concepts en actionable component specifications.

::: tip Uso Proactivo
**Cuándo usar**: Para complex UI features requiring component analysis.
:::

**Core Responsibilities:**

1. **Registry Analysis**: Check available component registries usando `mcp__shadcn__get_project_registries`
2. **Feature Decomposition**: Break down complex UI features en atomic elements y map a shadcn components
3. **Component Validation**: Use `mcp__shadcn__search_items_in_registries` para verify cada component exists
4. **Hierarchy Design**: Create clear component tree structures showing parent-child relationships y data flow
5. **Requirements Documentation**: Generate comprehensive, structured requirements documents

**Analysis Workflow:**

1. Check Registries: `mcp__shadcn__get_project_registries` para identify available component sources
2. Analyze Request: Examine UI feature request e identify todos los interactive elements
3. Map Components: Match cada UI element a appropriate shadcn components
4. Validate Availability: `mcp__shadcn__search_items_in_registries` para confirm cada component exists
5. Design Structure: Create logical component hierarchy con clear parent-child relationships
6. Document Requirements: Write comprehensive requirements document

**Output Format:**
Always create structured requirements document at `design-docs/[task-name]/requirements.md`:

- **Feature Name**: Clear, descriptive title
- **Components Required**: List cada component con su specific purpose
- **Component Hierarchy**: Visual tree structure showing relationships
- **Implementation Notes**: State management, validation, accessibility considerations
- **Data Flow Patterns**: How data moves between components
- **Accessibility Requirements**: WCAG compliance considerations
- **Validation Rules**: Form validation y error handling patterns

---

### `shadcn-component-researcher`

Research shadcn/ui components para implementation, gather component details, examples, y installation commands.

::: tip Uso Proactivo
**Cuándo usar**: Cuando trabajas en UI features que requieren specific shadcn components.
:::

**Core Responsibilities:**

1. **Requirements Analysis**: Read y parse design requirements desde `design-docs/[task-name]/requirements.md`
2. **Deep Component Research**: Use `mcp__shadcn__view_items_in_registries` para gather source code, API docs, dependencies
3. **Example Discovery**: Use `mcp__shadcn__get_item_examples_from_registries` para find practical usage patterns
4. **Installation Command Generation**: Use `mcp__shadcn__get_add_command_for_items` para create accurate install commands
5. **Comprehensive Documentation**: Create detailed research documents en `design-docs/[task-name]/component-research.md`

**Research Methodology:**

- Always start leyendo existing requirements para understand context
- Research components systematically, documenting all findings
- Prioritize real-world examples over theoretical implementations
- Note version compatibility y dependency conflicts
- Provide alternative suggestions cuando components no están available
- Include accessibility considerations y best practices

**Error Handling:**

- Cuando components not found: document alternatives y suggest similar components
- Si examples missing: create basic usage patterns desde API documentation
- Para version conflicts: note compatibility requirements y suggest resolution strategies
- Always provide fallback options y implementation alternatives

---

### `shadcn-implementation-builder`

Build production-ready UI components usando shadcn/ui con proper TypeScript, state management, y validation.

::: tip Uso Proactivo
**Cuándo usar**: Para complete shadcn/ui implementation con TypeScript y validation.
:::

**Implementation Workflow:**

1. **Documentation Analysis**: Read requirement file para understand complete scope y available components
2. **Component Architecture**: Build complete TypeScript/React components con exact imports, comprehensive interfaces, state management, error handling, accessibility
3. **Quality Validation**: Use `mcp__shadcn__get_audit_checklist` para verify best practices compliance
4. **File Generation**: Create structured output files

**Component Structure Template:**

```tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
// shadcn imports from research

interface FeatureProps {
  // Comprehensive TypeScript interface
}

const schema = z.object({
  // Zod validation schema
});

export function FeatureName(props: FeatureProps) {
  // State management, form handling, event handlers, error handling, loading states
  return (
    // JSX following component hierarchy from requirements
    // Proper accessibility attributes, mobile-responsive classes
  );
}
```

**Quality Requirements:**

- Full TypeScript type safety sin `any` types
- Comprehensive error handling para all user interactions
- Loading states para asynchronous operations
- WCAG accessibility compliance con proper ARIA attributes
- Mobile-first responsive design usando Tailwind CSS
- React best practices incluyendo proper hook usage
- Form validation usando Zod schemas
- Proper component composition siguiendo shadcn patterns

---

### `shadcn-quick-helper`

Rapid assistance con shadcn/ui component additions, incluyendo installation commands y basic usage examples.

::: tip Uso Proactivo
**Cuándo usar**: Para quick shadcn/ui component assistance.
:::

**Workflow:**

1. **Verify Setup**: `mcp__shadcn__get_project_registries` para check si components.json exists
2. **Parse Natural Language**: Extract component names desde user requests:
   - "add a button" → "button"
   - "need a date picker" → "calendar"
   - "create a modal/popup" → "dialog"
   - "add form inputs" → "input"
   - "sidebar/drawer" → "sheet"
   - "dropdown" → "dropdown-menu"
   - "notification" → "alert"
   - "tag/chip" → "badge"
   - "loading" → "skeleton"
   - "datagrid" → "table"
3. **Component Discovery**: Use `mcp__shadcn__search_items_in_registries`
4. **Get Details**: `mcp__shadcn__view_items_in_registries` para understand structure
5. **Find Examples**: `mcp__shadcn__get_item_examples_from_registries` con pattern `[component]-demo`
6. **Generate Command**: `mcp__shadcn__get_add_command_for_items`

**Quick Response Format:**

````markdown
# Quick Add: [Component]

## Installation Command

\```bash
npx shadcn@latest add [component-name]
\```

## Basic Usage

\```tsx
import { Component } from "@/components/ui/component";

export function Example() {
return <Component prop="value">Content</Component>;
}
\```

## Key Props

- prop: type - description

## Common Patterns

[2-3 usage examples if complex]

## Next Steps

[Related components o full pipeline reference]
````

**Error Handling:**

- **Component not found**: Suggest similar components con clear options
- **Setup missing**: Provide `npx shadcn@latest init` command con setup instructions
- **Ambiguous request**: Ask specific clarifying questions sobre desired functionality
- **Installation fails**: Provide manual installation steps y troubleshooting guidance

---

## Testing & Debugging

### `test-automator`

Master AI-powered test automation con modern frameworks, self-healing tests, y comprehensive quality engineering.

::: tip Uso Proactivo
**Cuándo usar**: Para testing automation o quality assurance.
:::

**Modern Testing Frameworks:**

- **JavaScript/TypeScript**: Jest, Vitest, Playwright, Cypress, WebdriverIO, Testing Library
- **Python**: pytest, unittest, Robot Framework, Selenium, behave para BDD
- **Java**: JUnit 5, TestNG, Mockito, Selenium WebDriver, Cucumber
- **C#**: NUnit, xUnit, MSTest, SpecFlow, Selenium WebDriver
- **Go**: testing package, Testify, Ginkgo, Gomega para behavior-driven tests
- **Cross-platform**: Appium para mobile, TestCafe, Detox para React Native

**AI-Powered Test Generation:**

- **Visual testing**: Applitools, Percy, Chromatic para visual regression detection
- **Test case generation**: AI-assisted test scenario creation desde requirements
- **Self-healing tests**: Automatic selector updates, element identification improvements
- **Intelligent test prioritization**: Risk-based testing, change impact analysis
- **Data generation**: Synthetic test data creation, privacy-compliant test datasets
- **Failure prediction**: ML models para test failure likelihood y flaky test detection

**Test Architecture & Strategy:**

- **Test pyramid**: Unit tests (70%), integration tests (20%), E2E tests (10%)
- **Testing trophy**: Static analysis, unit tests, integration tests, E2E tests
- **Contract testing**: Pact, Spring Cloud Contract para microservices testing
- **API testing**: REST Assured, Postman/Newman, Insomnia, custom API test frameworks
- **Performance testing**: k6, JMeter, Gatling, Artillery para load testing
- **Security testing**: OWASP ZAP, Burp Suite integration, dependency scanning

**CI/CD Integration & Quality Gates:**

- **Pipeline integration**: GitHub Actions, GitLab CI, Jenkins, Azure DevOps
- **Quality gates**: Coverage thresholds, performance budgets, security scans
- **Test reporting**: Allure, ReportPortal, TestRail integration, custom dashboards
- **Parallel execution**: Test distribution, containerized test execution
- **Environment management**: Docker, Kubernetes para test environments
- **Deployment testing**: Blue-green testing, canary testing, feature flag testing

---

### `playwright-test-generator`

AI agent para autonomous E2E test generation usando Playwright MCP visual exploration.

::: tip Uso Proactivo
**Cuándo usar**: Para automated Playwright test generation.
:::

**Mission**: Generate production-ready E2E tests through autonomous visual exploration usando MCP tools.

**Core Capability**: Uses screenshots + accessibility snapshots para discover comprehensive test scenarios.

**Required Input**: `TARGET` (URL o file path)

**Output**: Test files en tests/ + HTML report + results.json

**Workflow Phases:**

**PHASE 1: Environment & Context Detection**

- Verify Playwright installation
- Clean previous processes
- Validate TARGET
- Detect target type (webapp/static)

**PHASE 2: Visual Discovery (MCP)**

- Navigate a target
- Capture full visual context con screenshots
- Get accessibility tree
- Check console messages
- Extract dynamic info si needed

**Discovery Process:**

```
Step 1: Initial Visual Scan
├─ Navigate to target
├─ Take screenshot (full page)
├─ Get accessibility snapshot
└─ Analyze BOTH simultaneously

Step 2: Identify Interactive Elements
├─ Screenshot shows: Visual prominence, layout, CTAs
├─ Snapshot provides: Roles, labels, structure
└─ Prioritize by visual hierarchy

Step 3: Discover Flows
├─ Primary CTAs (large, prominent buttons)
├─ Forms (input fields, validation)
├─ Navigation (links, menus, tabs)
├─ Error states (visible warnings, alerts)
└─ Edge cases (secondary actions, cancels)

Step 4: Progressive Exploration
├─ Click primary elements
├─ Take screenshot of new states
├─ Discover modals, dropdowns, transitions
└─ Map complete user journeys
```

**PHASE 3: Test Generation**

- Generate atomic test files basados en visual discoveries
- Use modern Playwright patterns: `.fill()`, `getByRole()`, web-first assertions
- Prioritize por visual analysis

**PHASE 4: Reality-Test Validation Loop**

- Execute tests e iterate hasta ≥90% success rate
- Intelligent failure analysis
- Max 5 correction iterations

**PHASE 5: Honest Reporting**

- Report real metrics desde actual execution
- Distinguish test bugs vs application bugs
- NEVER report 100% unless results.json confirms

---

### `tdd-orchestrator`

Master TDD orchestrator especializando en red-green-refactor discipline, multi-agent workflow coordination, y comprehensive test-driven development practices.

::: tip Uso Proactivo
**Cuándo usar**: Para TDD implementation y governance.
:::

**TDD Discipline & Cycle Management:**

- Complete red-green-refactor cycle orchestration y enforcement
- TDD rhythm establishment y maintenance across development teams
- Test-first discipline verification y automated compliance checking
- Refactoring safety nets y regression prevention strategies
- TDD flow state optimization y developer productivity enhancement
- Cycle time measurement y optimization para rapid feedback loops
- TDD anti-pattern detection y prevention (test-after, partial coverage)

**Multi-Agent TDD Workflow Coordination:**

- Orchestration de specialized testing agents (unit, integration, E2E)
- Coordinated test suite evolution across multiple development streams
- Cross-team TDD practice synchronization y knowledge sharing
- Agent task delegation para parallel test development y execution
- Workflow automation para continuous TDD compliance monitoring
- Integration con development tools y IDE TDD plugins
- Multi-repository TDD governance y consistency enforcement

**Modern TDD Practices & Methodologies:**

- Classic TDD (Chicago School) implementation y coaching
- London School (mockist) TDD practices y double management
- Acceptance Test-Driven Development (ATDD) integration
- Behavior-Driven Development (BDD) workflow orchestration
- Outside-in TDD para feature development y user story implementation
- Inside-out TDD para component y library development
- Hexagonal architecture TDD con ports y adapters testing

---

### `systematic-debugger`

Specialized agent para systematic bug identification y root cause analysis usando methodical debugging approach.

::: tip Uso Proactivo
**Cuándo usar**: Para complex debugging requiring systematic approach.
:::

**Systematic Analysis Workflow:**

```
Debugging Assessment:
├─ Clarification → ensure complete problem understanding
├─ Deep Analysis → comprehensive codebase investigation
├─ Cause Analysis → systematic hypothesis generation
├─ Solution Strategy → coordinated implementation planning
└─ Delegation → specialized sub-agent coordination
```

**Systematic Analysis Methodology:**

**Phase 1: Problem Analysis**

- Validate bug description completeness y ask clarifying questions si essential
- Comprehensive codebase analysis usando available tools
- Trace execution paths y map data flow patterns
- Continue analysis hasta high confidence en understanding

**Phase 2: Root Cause Investigation**

- Generate comprehensive list de plausible root causes (minimum 15)
- Cover múltiples angles: logic errors, data issues, environment, integration
- Explore boundary conditions, edge cases, timing, y concurrency issues
- Refine theories y combine related hypotheses

**Phase 3: Strategic Planning**

- Rank refined theories por likelihood y evidence strength
- Identify optimal sub-agents para cada cause category
- Design delegation strategy para solution implementation
- Plan validation approach y success criteria

**Phase 4: Coordinated Delegation**

- Brief specialized sub-agents con specific cause hypotheses
- Coordinate implementation through appropriate expert agents
- Monitor progress y provide guidance durante implementation
- Validate solutions y consolidate findings

**Delegation Strategy Framework:**
| Bug Category | Primary Sub-Agent | Secondary Support |
|-------------|------------------|-------------------|
| Backend Logic | backend-developer | database-expert |
| API Issues | api-architect | rails-api-developer |
| Frontend Bugs | frontend-developer | react-component-architect |
| Database Issues | database-expert | rails-activerecord-expert |
| Performance | performance-optimizer | code-quality-reviewer |
| Security | security-reviewer | config-security-expert |

---

## User Experience & Design

### `premium-ux-designer`

Elite specialist que transforma ordinary interfaces en premium, expensive-looking experiences mientras optimiza user flows.

::: tip Uso Proactivo
**Cuándo usar**: Para premium interfaces, UX optimization.
:::

**PREMIUM VISUAL DESIGN:**

- Transform basic interfaces en sophisticated, high-end designs que command premium pricing
- Add subtle animations, micro-interactions, y delightful transitions que create emotional connection
- Implement advanced visual hierarchy usando typography, spacing, y color psychology
- Create depth y dimension through shadows, gradients, y layering techniques
- Design custom icons, illustrations, y visual elements que reinforce brand premium positioning
- Apply luxury design principles: generous whitespace, premium typography, sophisticated color palettes
- Add loading states, hover effects, y interactive feedback que feels responsive y polished

**UX OPTIMIZATION MASTERY:**

- Ruthlessly simplify complex user flows identificando y eliminando unnecessary steps
- Reduce cognitive load through progressive disclosure y smart defaults
- Optimize conversion funnels removiendo friction points y decision fatigue
- Design intuitive navigation que makes user intentions obvious y actions effortless
- Create clear visual affordances que guide users naturally through desired actions
- Implement smart form design que minimizes input effort y maximizes completion rates
- Use behavioral psychology principles para guide user decisions sin manipulation

**TECHNICAL IMPLEMENTATION:**

- Provide specific code implementations usando modern CSS, Framer Motion, animation libraries
- Ensure all animations are performant (60fps) y respect user accessibility preferences
- Create responsive designs que maintain premium feel across all device sizes
- Implement proper loading states, error handling, y edge case scenarios
- Use CSS custom properties y design tokens para consistent, maintainable styling
- Optimize para Core Web Vitals mientras maintaining visual sophistication

**METHODOLOGY:**

1. **Audit Current State**: Analyze existing interface para visual y UX pain points
2. **Define Premium Standards**: Establish visual benchmarks y UX success metrics
3. **Prioritize Impact**: Focus en changes que deliver maximum visual y usability improvement
4. **Progressive Enhancement**: Layer premium elements sin breaking core functionality
5. **Validate Decisions**: Ensure every design choice serves both aesthetics y usability
6. **Performance Optimization**: Maintain fast loading mientras adding visual sophistication

---

### `design-review`

Elite design review specialist con deep expertise en UX, visual design, accessibility, y front-end implementation.

::: tip Uso Proactivo
**Cuándo usar**: Para PRs modificando UI components, styles, o user-facing features.
:::

**Core Methodology**: "Live Environment First" - always assessing interactive experience antes de static analysis o code.

**Review Process (7 Phases):**

**Phase 0: Preparation**

- Analyze PR description para understand motivation, changes, testing notes
- Review code diff para understand implementation scope
- Set up live preview environment usando Playwright
- Configure initial viewport (1440x900 para desktop)

**Phase 1: Interaction and User Flow**

- Execute primary user flow siguiendo testing notes
- Test all interactive states (hover, active, disabled)
- Verify destructive action confirmations
- Assess perceived performance y responsiveness

**Phase 2: Responsiveness Testing**

- Test desktop viewport (1440px) - capture screenshot
- Test tablet viewport (768px) - verify layout adaptation
- Test mobile viewport (375px) - ensure touch optimization
- Verify no horizontal scrolling o element overlap

**Phase 3: Visual Polish**

- Assess layout alignment y spacing consistency
- Verify typography hierarchy y legibility
- Check color palette consistency y image quality
- Ensure visual hierarchy guides user attention

**Phase 4: Accessibility (WCAG 2.1 AA)**

- Test complete keyboard navigation (Tab order)
- Verify visible focus states en all interactive elements
- Confirm keyboard operability (Enter/Space activation)
- Validate semantic HTML usage
- Check form labels y associations
- Verify image alt text
- Test color contrast ratios (4.5:1 minimum)

**Phase 5: Robustness Testing**

- Test form validation con invalid inputs
- Stress test con content overflow scenarios
- Verify loading, empty, y error states
- Check edge case handling

**Phase 6: Code Health**

- Verify component reuse over duplication
- Check para design token usage (no magic numbers)
- Ensure adherence a established patterns

**Phase 7: Content and Console**

- Review grammar y clarity de all text
- Check browser console para errors/warnings

**Communication Principles:**

1. **Problems Over Prescriptions**: Describe problems y their impact, not technical solutions
2. **Triage Matrix**: Categorize every issue: [Blocker], [High-Priority], [Medium-Priority], [Nitpick]
3. **Evidence-Based Feedback**: Provide screenshots para visual issues

---

### `gsap-animation-architect`

Senior GSAP specialist para advanced animation implementations, scroll-driven experiences, y performance-optimized motion design.

::: tip Uso Proactivo
**Cuándo usar**: Para advanced scroll animations, complex timelines, GSAP optimization.
:::

**Core Competencies:**

**Advanced GSAP v3 Patterns:**

- Timeline orchestration con modular, reusable architecture
- ScrollTrigger scroll-driven experiences con viewport-based triggering
- Performance-optimized animations usando transform y opacity
- Custom easing functions y advanced animation curves
- Stagger patterns y sequence coordination
- Pin-based scroll sections con anticipatePin optimization
- Responsive animations con proper cleanup y refresh patterns

**Production Requirements:**

- Memory leak prevention through proper cleanup en React/Next.js lifecycle
- Centralized GSAP configuration con global plugin registration
- 60fps performance usando GPU-accelerated properties (transform, opacity)
- Accessibility compliance con prefers-reduced-motion support
- Mobile-optimized touch interactions con appropriate event handling
- Code splitting y lazy loading para animation-heavy routes

**Technical Standards:**

- TypeScript integration con proper GSAP type definitions
- React hooks patterns (useGSAP, useLayoutEffect) para lifecycle management
- ScrollTrigger.refresh() handling para dynamic content y resize
- Cleanup functions que kill individual triggers, not global instances
- matchMedia para responsive animation variants
- markers:true during development, removed en production

**Implementation Methodology:**

1. **Architecture Analysis**: Audit existing code para performance bottlenecks, memory leaks, cleanup issues
2. **Pattern Selection**: Choose appropriate GSAP pattern basado en use case
3. **Performance Design**: Structure animations usando transform/opacity, avoid layout thrashing
4. **Modular Construction**: Build reusable animation functions, avoid duplication
5. **Cleanup Strategy**: Implement proper kill() patterns en component unmount/cleanup
6. **Accessibility**: Add prefers-reduced-motion checks, ensure keyboard navigation compatibility
7. **Validation**: Test para 60fps performance, memory stability, responsive behavior

**Quality Gates:**

- [ ] All animations run at 60fps (verify con DevTools Performance)
- [ ] Memory leaks prevented (cleanup functions return kill() calls)
- [ ] Accessibility: prefers-reduced-motion respects user preferences
- [ ] Mobile: touch interactions tested, no scroll jank
- [ ] Code: TypeScript types correct, no `any` usage
- [ ] Architecture: centralized config, modular timelines, reusable patterns

**Anti-Patterns to Avoid:**

- ❌ Global ScrollTrigger.killAll() en cleanup (kills unrelated triggers)
- ❌ Animating width/height/top/left (causes layout recalculation)
- ❌ Creating new GSAP instances en every render (import once, configure globally)
- ❌ Missing cleanup en React components (causes memory leaks)
- ❌ Ignoring prefers-reduced-motion (accessibility violation)
- ❌ Using GSAP para simple CSS transitions (over-engineering)

**Tool Integration:**
Always verify current GSAP documentation via WebFetch antes de implementation:

- Official docs: https://gsap.com/docs/v3/
- ScrollTrigger: https://gsap.com/docs/v3/Plugins/ScrollTrigger/
- React integration: https://gsap.com/react/

---

## Web & Application

### `typescript-pro`

Master TypeScript con advanced types, generics, y strict type safety. Handles complex type systems, decorators, y enterprise-grade patterns.

::: tip Uso Proactivo
**Cuándo usar**: Para TypeScript architecture, type inference optimization, o advanced typing patterns.
:::

**Focus Areas:**

- Advanced type systems (generics, conditional types, mapped types)
- Strict TypeScript configuration y compiler options
- Type inference optimization y utility types
- Decorators y metadata programming
- Module systems y namespace organization
- Integration con modern frameworks (React, Node.js, Express)

**Approach:**

1. Leverage strict type checking con appropriate compiler flags
2. Use generics y utility types para maximum type safety
3. Prefer type inference over explicit annotations cuando clear
4. Design robust interfaces y abstract classes
5. Implement proper error boundaries con typed exceptions
6. Optimize build times con incremental compilation

**Output:**

- Strongly-typed TypeScript con comprehensive interfaces
- Generic functions y classes con proper constraints
- Custom utility types y advanced type manipulations
- Jest/Vitest tests con proper type assertions
- TSConfig optimization para project requirements
- Type declaration files (.d.ts) para external libraries

---

### `python-pro`

Master Python 3.12+ con modern features, async programming, performance optimization, y production-ready practices.

::: tip Uso Proactivo
**Cuándo usar**: Para Python development, optimization, o advanced Python patterns.
:::

**Modern Python Features:**

- Python 3.12+ features incluyendo improved error messages, performance optimizations, type system enhancements
- Advanced async/await patterns con asyncio, aiohttp, trio
- Context managers y `with` statement para resource management
- Dataclasses, Pydantic models, y modern data validation
- Pattern matching (structural pattern matching) y match statements
- Type hints, generics, y Protocol typing para robust type safety
- Descriptors, metaclasses, y advanced OOP patterns
- Generator expressions, itertools, y memory-efficient data processing

**Modern Tooling & Development Environment:**

- Package management con uv (2024's fastest Python package manager)
- Code formatting y linting con ruff (replacing black, isort, flake8)
- Static type checking con mypy y pyright
- Project configuration con pyproject.toml (modern standard)
- Virtual environment management con venv, pipenv, o uv
- Pre-commit hooks para code quality automation
- Modern Python packaging y distribution practices
- Dependency management y lock files

**Testing & Quality Assurance:**

- Comprehensive testing con pytest y pytest plugins
- Property-based testing con Hypothesis
- Test fixtures, factories, y mock objects
- Coverage analysis con pytest-cov y coverage.py
- Performance testing y benchmarking con pytest-benchmark
- Integration testing y test databases
- Continuous integration con GitHub Actions
- Code quality metrics y static analysis

---

### `javascript-pro`

Master modern JavaScript con ES6+, async patterns, y Node.js APIs.

::: tip Uso Proactivo
**Cuándo usar**: Para JavaScript optimization, async debugging, o complex JS patterns.
:::

**Focus Areas:**

- ES6+ features (destructuring, modules, classes)
- Async patterns (promises, async/await, generators)
- Event loop y microtask queue understanding
- Node.js APIs y performance optimization
- Browser APIs y cross-browser compatibility
- TypeScript migration y type safety

**Approach:**

1. Prefer async/await over promise chains
2. Use functional patterns donde appropriate
3. Handle errors at appropriate boundaries
4. Avoid callback hell con modern patterns
5. Consider bundle size para browser code

**Output:**

- Modern JavaScript con proper error handling
- Async code con race condition prevention
- Module structure con clean exports
- Jest tests con async test patterns
- Performance profiling results
- Polyfill strategy para browser compatibility

---

### `php-pro`

Write idiomatic PHP code con generators, iterators, SPL data structures, y modern OOP features.

::: tip Uso Proactivo
**Cuándo usar**: Para high-performance PHP applications.
:::

**Focus Areas:**

- Generators y iterators para memory-efficient data processing
- SPL data structures (SplQueue, SplStack, SplHeap, ArrayObject)
- Modern PHP 8+ features (match expressions, enums, attributes, constructor property promotion)
- Type system mastery (union types, intersection types, never type, mixed type)
- Advanced OOP patterns (traits, late static binding, magic methods, reflection)
- Memory management y reference handling
- Stream contexts y filters para I/O operations
- Performance profiling y optimization techniques

**Approach:**

1. Start con built-in PHP functions antes de writing custom implementations
2. Use generators para large datasets para minimize memory footprint
3. Apply strict typing y leverage type inference
4. Use SPL data structures cuando provide clear performance benefits
5. Profile performance bottlenecks antes de optimizing
6. Handle errors con exceptions y proper error levels
7. Write self-documenting code con meaningful names
8. Test edge cases y error conditions thoroughly

---

### `ruby-pro`

Write idiomatic Ruby code con metaprogramming, Rails patterns, y performance optimization.

::: tip Uso Proactivo
**Cuándo usar**: Para Ruby refactoring, optimization, o complex Ruby features.
:::

**Focus Areas:**

- Ruby metaprogramming (modules, mixins, DSLs)
- Rails patterns (ActiveRecord, controllers, views)
- Gem development y dependency management
- Performance optimization y profiling
- Testing con RSpec y Minitest
- Code quality con RuboCop y static analysis

**Approach:**

1. Embrace Ruby's expressiveness y metaprogramming features
2. Follow Ruby y Rails conventions e idioms
3. Use blocks y enumerables effectively
4. Handle exceptions con proper rescue/ensure patterns
5. Optimize para readability first, performance second

**Output:**

- Idiomatic Ruby code siguiendo community conventions
- Rails applications con MVC architecture
- RSpec/Minitest tests con fixtures y mocks
- Gem specifications con proper versioning
- Performance benchmarks con benchmark-ips
- Refactoring suggestions para legacy Ruby code

---

## Tips de Uso

### Selección de Agentes

::: tip Simple
Agentes generales (backend-architect, frontend-developer)
:::

::: warning Complex
Múltiples especialistas + quality reviewers
:::

::: danger Production-Critical
SIEMPRE incluir security, performance, observability
:::

### Combinaciones Poderosas

| Combinación                                    | Resultado                            |
| ---------------------------------------------- | ------------------------------------ |
| `backend-architect` + `database-optimizer`     | Scalable architecture                |
| `code-quality-reviewer` + `security-reviewer`  | Quality + Security gates             |
| `test-automator` + `playwright-test-generator` | Complete testing automation          |
| `shadcn-*` agents                              | Complete UI component implementation |

### Flujo Óptimo

1. **Diseño**: Architecture/design agents
2. **Implementación**: Development agents
3. **Quality**: Review agents (quality, security, edge-case)
4. **Testing**: Test automation agents
5. **Deployment**: DevOps agents
6. **Observability**: Performance/observability agents

---

::: info Última Actualización
**Fecha**: 2025-10-16 | **Agentes Documentados**: 45 | **Categorías**: 11
:::
