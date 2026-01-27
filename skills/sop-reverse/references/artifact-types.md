# Artifact Types Reference

Detailed analysis and spec generation instructions per artifact type.

## Type Detection

When `target_type` is not provided, analyze the target:
- **Path exists?** Check if codebase, docs, or config
- **URL pattern?** Check if API docs, wiki, repository
- **Description only?** Likely process or concept

## Batch Analysis by Type

### Codebase

Analyze:
- Directory structure and file organization
- Entry points and main modules
- Dependencies (package.json, requirements.txt, etc.)
- Architecture patterns (MVC, microservices, etc.)
- Technology stack identification
- Test coverage and quality gates
- Build and deployment processes
- API surface (public interfaces)
- Data flow and state management

### API

Analyze:
- Authentication mechanisms (OAuth, API keys, JWT)
- Base URL and versioning scheme
- Endpoint inventory (method, path, purpose)
- Request/response schemas
- Rate limiting and quotas
- Error response formats
- Pagination patterns
- Webhook capabilities
- SDK availability

### Documentation

Analyze:
- Document hierarchy and organization
- Main topics and sections
- Cross-references and dependencies
- Missing or incomplete sections
- Audience and purpose
- Update frequency and recency
- Code examples and tutorials
- API reference completeness

### Process

Analyze:
- Process steps and sequence
- Actors/roles involved
- Inputs and outputs per step
- Decision points and branches
- Tools and systems used
- Success criteria
- Failure modes and exceptions
- Dependencies on other processes
- Metrics and KPIs

### Concept

Analyze:
- Core definition and scope
- Key components and relationships
- Common implementations
- Use cases and applications
- Advantages and limitations
- Related concepts and alternatives
- Industry standards and best practices
- Common misconceptions

## Spec Generation by Type

### Codebase -> Technical Specs

| File | Content |
|------|---------|
| `architecture.md` | System design, layers, boundaries |
| `components.md` | Major components, responsibilities |
| `data-model.md` | Entities, relationships, schemas |
| `api-surface.md` | Public interfaces, contracts |
| `patterns.md` | Design patterns, conventions |
| `dependencies.md` | External libs, services |
| `build-deployment.md` | Build process, deployment |
| `testing-strategy.md` | Test approach, coverage |

### API -> API Specs

| File | Content |
|------|---------|
| `overview.md` | Purpose, versioning, base URL |
| `authentication.md` | Auth methods, token management |
| `endpoints.md` | Complete endpoint catalog |
| `schemas.md` | Request/response models |
| `error-handling.md` | Error codes, formats |
| `rate-limits.md` | Quotas, throttling |
| `webhooks.md` | Webhook events, payloads |
| `sdk-integration.md` | Client libraries, examples |

### Documentation -> Documentation Map

| File | Content |
|------|---------|
| `summary.md` | Overview, purpose, audience |
| `structure.md` | Hierarchy, organization |
| `key-concepts.md` | Main topics, definitions |
| `coverage-gaps.md` | Missing or incomplete areas |
| `cross-references.md` | Dependencies, links |
| `examples-inventory.md` | Code samples, tutorials |

### Process -> Process Specs

| File | Content |
|------|---------|
| `workflow.md` | Steps, sequence, branches |
| `actors.md` | Roles, responsibilities |
| `artifacts.md` | Inputs, outputs, formats |
| `decision-points.md` | Criteria, alternatives |
| `tools-systems.md` | Technology, integrations |
| `metrics.md` | KPIs, success criteria |
| `exceptions.md` | Error handling, edge cases |

### Concept -> Concept Specs

| File | Content |
|------|---------|
| `definition.md` | Core meaning, scope |
| `components.md` | Key parts, structure |
| `relationships.md` | How parts connect |
| `implementations.md` | Common realizations |
| `use-cases.md` | Applications, examples |
| `trade-offs.md` | Pros, cons, limitations |
| `alternatives.md` | Related concepts, comparisons |
