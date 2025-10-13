# Guía de Agentes Especializados

_45 agentes organizados por dominio y frecuencia de uso_

---

## 🏗️ Architecture & System Design

### `backend-architect`

Design RESTful APIs, microservice boundaries, database schemas. Reviews architecture for scalability and performance bottlenecks.

**Cuándo**: New backend services or APIs.

### `frontend-developer`

Build React components, responsive layouts, client-side state management. React 19, Next.js 15, modern frontend architecture.

**Cuándo**: UI components or frontend fixes.

### `mobile-developer`

React Native, Flutter, native mobile apps. Cross-platform development, native integrations, offline sync.

**Cuándo**: Mobile features, cross-platform code, app optimization.

### `cloud-architect`

AWS/Azure/GCP multi-cloud infrastructure, IaC (Terraform/OpenTofu/CDK), FinOps cost optimization, serverless, microservices.

**Cuándo**: Cloud architecture, cost optimization, migrations.

### `hybrid-cloud-architect`

Multi-cloud solutions across AWS/Azure/GCP and private clouds (OpenStack/VMware). Hybrid connectivity, workload placement, edge computing.

**Cuándo**: Hybrid architecture, multi-cloud strategy.

### `kubernetes-architect`

Cloud-native infrastructure, GitOps workflows (ArgoCD/Flux), container orchestration. EKS/AKS/GKE, service mesh (Istio/Linkerd).

**Cuándo**: K8s architecture, GitOps implementation.

### `graphql-architect`

GraphQL federation, performance optimization, enterprise security. Scalable schemas, caching, real-time systems.

**Cuándo**: GraphQL architecture or performance.

### `agent-assignment-analyzer`

Intelligent task analysis and agent selection for parallel execution. Analyzes dependencies, generates optimal assignment strategies.

**Cuándo**: Multi-task workflows requiring optimal distribution.

---

## 🔍 Code Review & Security

### `code-quality-reviewer`

Universal code quality principles preventing technical debt. Reviews maintainability, reliability, architectural soundness.

**Cuándo**: Before PRs, code audits, architecture validation.

**Tools**: LS, Read, Grep, Glob, Bash

### `architect-reviewer`

Modern architecture patterns, clean architecture, microservices, event-driven systems, DDD. Reviews system designs for integrity.

**Cuándo**: Architectural decisions, system design reviews.

### `security-reviewer`

Security review of pending changes. Detects vulnerabilities, exposed credentials, authorization flaws, input validation issues.

**Cuándo**: Before merge, after critical changes, security audits.

### `config-security-expert`

Configuration security preventing production outages through vigilant config review.

**Cuándo**: Before production, audits, compliance.

**Tools**: LS, Read, Grep, Glob, Bash

### `edge-case-detector`

Production-critical edge cases causing silent failures and data corruption.

**Cuándo**: Critical testing, validation, failure scenarios.

**Tools**: LS, Read, Grep, Glob, Bash

---

## 🗄️ Database Management

### `database-optimizer`

Performance tuning, query optimization, scalable architectures. Indexing, N+1 resolution, multi-tier caching.

**Cuándo**: Database optimization, performance issues, scalability.

### `database-admin`

Cloud databases, automation, reliability engineering. AWS/Azure/GCP database services, IaC, high availability.

**Cuándo**: Database architecture, operations, reliability.

---

## 🚀 DevOps & Deployment

### `deployment-engineer`

CI/CD pipelines, GitOps workflows, deployment automation. GitHub Actions, ArgoCD/Flux, progressive delivery, container security.

**Cuándo**: CI/CD design, GitOps implementation.

### `devops-troubleshooter`

Rapid incident response, debugging, observability. Log analysis, distributed tracing, Kubernetes debugging.

**Cuándo**: Debugging, incident response, troubleshooting.

### `dx-optimizer`

Developer Experience. Improves tooling, setup, workflows.

**Cuándo**: Project setup, team feedback, development friction.

### `terraform-specialist`

Terraform/OpenTofu IaC automation, state management, infrastructure patterns. Module design, multi-cloud deployments.

**Cuándo**: IaC automation, state management.

---

## 📚 Documentation & Technical Writing

### `docs-architect`

Technical documentation from codebases. Analyzes architecture, design patterns, implementation for long-form technical manuals.

**Cuándo**: System documentation, architecture guides.

### `api-documenter`

API documentation with OpenAPI 3.1, AI-powered tools, developer experience. Interactive docs, SDK generation, developer portals.

**Cuándo**: API documentation, developer portals.

### `reference-builder`

Exhaustive technical references and API documentation. Parameter listings, configuration guides, searchable reference materials.

**Cuándo**: API docs, configuration references.

### `tutorial-engineer`

Step-by-step tutorials and educational content from code. Transforms complex concepts into progressive learning experiences.

**Cuándo**: Onboarding guides, feature tutorials.

### `mermaid-expert`

Mermaid diagrams for flowcharts, sequences, ERDs, architectures. All diagram types and styling.

**Cuándo**: Visual documentation, system diagrams.

---

## 🚨 Incident Response & Network

### `incident-responder`

SRE incident response. Rapid problem resolution, observability, incident management. Incident command, blameless post-mortems.

**Cuándo**: Production incidents, SRE practices.

### `network-engineer`

Cloud networking, security architectures, performance optimization. Multi-cloud connectivity, service mesh, zero-trust networking.

**Cuándo**: Network design, connectivity issues.

---

## ⚡ Performance & Observability

### `performance-engineer`

Observability, application optimization, scalable system performance. OpenTelemetry, distributed tracing, load testing.

**Cuándo**: Performance optimization, observability, scalability.

### `observability-engineer`

Production-ready monitoring, logging, tracing. Observability strategies, SLI/SLO management, incident response workflows.

**Cuándo**: Monitoring infrastructure, production reliability.

### `web-search-specialist`

Web research using search techniques and synthesis. Search operators, result filtering, multi-source verification.

**Cuándo**: Deep research, information gathering.

---

## 🎨 Shadcn-UI Components

### `shadcn-requirements-analyzer`

Analyze UI feature requests and break down into structured shadcn component requirements. Translates design concepts into component specifications.

**Cuándo**: Complex UI features requiring component analysis.

### `shadcn-component-researcher`

Research shadcn/ui components for implementation. Component details, examples, installation commands.

**Cuándo**: UI features requiring specific shadcn components.

### `shadcn-implementation-builder`

Production-ready UI components using shadcn/ui with TypeScript, state management, validation.

**Cuándo**: shadcn/ui implementation with TypeScript.

### `shadcn-quick-helper`

Rapid shadcn/ui component assistance. Installation commands and basic usage examples.

**Cuándo**: Quick shadcn/ui component help.

---

## 🧪 Testing & Debugging

### `test-automator`

AI-powered test automation with modern frameworks, self-healing tests, quality engineering. Scalable testing strategies with CI/CD.

**Cuándo**: Testing automation, quality assurance.

### `playwright-test-generator`

AI-driven test generation following Playwright Agent workflow. Atomic tests, code review, debugging, reporting.

**Cuándo**: Automated Playwright test generation.

### `tdd-orchestrator`

TDD orchestrator. Red-green-refactor discipline, multi-agent workflow coordination, test-driven development practices.

**Cuándo**: TDD implementation, governance.

### `systematic-debugger`

Systematic bug identification and root cause analysis using methodical debugging. Delegates implementation to sub-agents.

**Cuándo**: Complex debugging requiring systematic approach.

---

## 🎨 User Experience & Design

### `premium-ux-designer`

Premium, polished user interfaces or optimize complex user experiences. Sophisticated styling, animations, premium design elements.

**Cuándo**: Premium interfaces, UX optimization.

### `design-review`

Design review on front-end PRs or UI changes. Verifies visual consistency, accessibility compliance, user experience quality.

**Cuándo**: PRs modifying UI components, styles.

### `gsap-animation-architect`

Advanced GSAP v3 animation implementations. ScrollTrigger scroll-driven experiences, timeline orchestration, performance optimization, memory leak prevention.

**Cuándo**: Advanced scroll animations, complex timelines, GSAP optimization.

---

## 💻 Web & Application

### `typescript-pro`

TypeScript with types, generics, strict type safety. Complex type systems, decorators, enterprise patterns.

**Cuándo**: TypeScript architecture, type optimization.

### `python-pro`

Python 3.12+ with modern features, async programming, performance optimization. Production-ready practices. Tools: uv, ruff, pydantic, FastAPI.

**Cuándo**: Python development, optimization.

### `javascript-pro`

Modern JavaScript with ES6+, async patterns, Node.js APIs. Promises, event loops, browser/Node compatibility.

**Cuándo**: JavaScript optimization, async debugging.

### `php-pro`

Idiomatic PHP code with generators, iterators, SPL data structures, modern OOP features.

**Cuándo**: High-performance PHP applications.

### `ruby-pro`

Idiomatic Ruby code with metaprogramming, Rails patterns, performance optimization. Ruby on Rails, gem development, testing frameworks.

**Cuándo**: Ruby refactoring, optimization.

---

## 💡 Tips de Uso

### Selección de Agentes

- **Simple**: Agentes generales (backend-architect, frontend-developer)
- **Complex**: Múltiples especialistas + quality reviewers
- **Production-critical**: SIEMPRE incluir security, performance, observability

### Combinaciones Poderosas

- `backend-architect` + `database-optimizer` = Scalable architecture
- `code-quality-reviewer` + `security-reviewer` = Quality + Security gates
- `test-automator` + `playwright-test-generator` = Complete testing automation
- `shadcn-*` agents = Complete UI component implementation

### Flujo Óptimo

1. **Diseño**: Architecture/design agents
2. **Implementación**: Development agents
3. **Quality**: Review agents (quality, security, edge-case)
4. **Testing**: Test automation agents
5. **Deployment**: DevOps agents
6. **Observability**: Performance/observability agents

---

_Última actualización: 2025-10-06 | 45 agentes documentados_
