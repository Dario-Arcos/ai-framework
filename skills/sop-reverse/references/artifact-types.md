# Artifact Types Reference

## Overview

This reference defines detailed analysis and spec generation instructions per artifact type. Understanding artifact types is essential for proper investigation and spec generation in sop-reverse.

---

## Type Detection

**Constraints:**
- You MUST detect artifact type when not provided because analysis approach varies by type
- You MUST check path existence first because this distinguishes file-based from concept-based artifacts
- You SHOULD identify specific artifact category because this guides analysis focus

When `target_type` is not provided, analyze the target:
- **Path exists?** Check if codebase, docs, or config
- **URL pattern?** Check if API docs, wiki, repository
- **Description only?** Likely process or concept

---

## Batch Analysis by Type

### Codebase

**Constraints:**
- You MUST analyze directory structure because organization reveals architecture
- You MUST identify entry points because these define system boundaries
- You SHOULD analyze dependencies because this reveals external coupling

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

**Constraints:**
- You MUST analyze authentication mechanisms because this affects integration approach
- You MUST document endpoint inventory because this defines API surface
- You SHOULD analyze rate limiting because this affects usage patterns

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

**Constraints:**
- You MUST analyze document hierarchy because organization affects navigation
- You MUST identify coverage gaps because missing areas need attention
- You SHOULD assess recency because outdated docs mislead

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

**Constraints:**
- You MUST identify process steps and sequence because this defines workflow
- You MUST document decision points because these are critical for implementation
- You SHOULD identify failure modes because error handling needs design

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

**Constraints:**
- You MUST define core meaning and scope because this establishes boundaries
- You MUST identify common implementations because this shows practical applications
- You SHOULD document trade-offs because this guides decision-making

Analyze:
- Core definition and scope
- Key components and relationships
- Common implementations
- Use cases and applications
- Advantages and limitations
- Related concepts and alternatives
- Industry standards and best practices
- Common misconceptions

---

## Spec Generation by Type

**Constraints:**
- You MUST generate appropriate spec files for artifact type because specs guide forward flow
- You MUST use consistent file naming because this enables automated processing
- You SHOULD cross-reference specs because this maintains coherence

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

---

## Troubleshooting

### Type Detection Fails

If artifact type cannot be determined:
- You SHOULD ask user for clarification because ambiguous targets need guidance
- You SHOULD default to concept analysis because this is most flexible
- You MUST NOT proceed with wrong type because analysis will be incomplete

### Spec Files Missing Expected Content

If generated specs lack detail:
- You SHOULD verify artifact was fully accessible because partial access limits analysis
- You SHOULD increase analysis depth because shallow passes miss important details
- You MUST re-run analysis if critical content is missing because incomplete specs cause planning failures

### Type-Specific Analysis Not Matching Artifact

If analysis approach doesn't fit artifact:
- You SHOULD reconsider type classification because initial detection may be wrong
- You SHOULD use hybrid approach if artifact spans types because real artifacts are complex
- You MUST document type ambiguity in specs because this informs forward planning

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
