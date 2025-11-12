---
name: understand
description: Deep analysis of project architecture, patterns, and relationships for comprehensive understanding
argument-hint: "specific area to focus on (optional)"
allowed-tools: Read, Glob, Grep, LS, TodoWrite
---

# Project Understanding

**Comprehensive analysis for deep understanding:** $ARGUMENTS

## Phase 1: Project Discovery

Using native tools for comprehensive analysis:

- **Glob** to map entire project structure
- **Read** key files (README, docs, configs)
- **Grep** to identify technology patterns
- **Read** entry points and main files

Discover:

- Project type and main technologies
- Architecture patterns (MVC, microservices, etc.)
- Directory structure and organization
- Dependencies and external integrations
- Build and deployment setup

## Phase 2: Code Architecture Analysis

- **Entry points**: Main files, index files, app initializers
- **Core modules**: Business logic organization
- **Data layer**: Database, models, repositories
- **API layer**: Routes, controllers, endpoints
- **Frontend**: Components, views, templates
- **Configuration**: Environment setup, constants
- **Testing**: Test structure and coverage

## Phase 3: Pattern Recognition

Identify established patterns:

- Naming conventions for files and functions
- Code style and formatting rules
- Error handling approaches
- Authentication/authorization flow
- State management strategy
- Communication patterns between modules

## Phase 4: Dependency Mapping

- Internal dependencies between modules
- External library usage patterns
- Service integrations
- API dependencies
- Database relationships
- Asset and resource management

## Phase 5: Integration Analysis

Identify how components interact:

- API endpoints and their consumers
- Database queries and their callers
- Event systems and listeners
- Shared utilities and helpers
- Cross-cutting concerns (logging, auth)

## Output Format

```
PROJECT OVERVIEW
├── Architecture: [Type]
├── Main Technologies: [List]
├── Key Patterns: [List]
└── Entry Point: [File]

COMPONENT MAP
├── Frontend
│   └── [Structure]
├── Backend
│   └── [Structure]
├── Database
│   └── [Schema approach]
└── Tests
    └── [Test strategy]

INTEGRATION POINTS
├── API Endpoints: [List]
├── Data Flow: [Description]
├── Dependencies: [Internal/External]
└── Cross-cutting: [Logging, Auth, etc.]

KEY INSIGHTS
- [Important finding 1]
- [Important finding 2]
- [Unique patterns]
- [Potential issues]
```

## When to Use

- **MANDATORY**: New codebase, unknown architecture, major refactor (Size L)
- **RECOMMENDED**: Multi-module changes (Size M), cross-project dependencies
- **OPTIONAL**: Single-file fixes (Size S), well-understood areas

## Success Criteria

Analysis complete when answerable:

- [ ] What happens when [core user action]?
- [ ] Where would I add [typical feature]?
- [ ] What breaks if I change [critical module]?
- [ ] Can I draw data flow from request to response?

## Example Output

<details>
<summary>Sample: Express.js REST API</summary>

```
PROJECT OVERVIEW
├── Architecture: REST API (Express.js + MongoDB)
├── Main Technologies: Node.js 18, Express 4.18, Mongoose 7.x
├── Key Patterns: MVC-like (routes→controllers→services→models)
└── Entry Point: src/server.js

COMPONENT MAP
├── Backend
│   ├── Routes (src/routes/*.js) - Express routers
│   ├── Controllers (src/controllers/*.js) - Request handlers
│   ├── Services (src/services/*.js) - Business logic
│   └── Models (src/models/*.js) - Mongoose schemas
├── Database
│   └── MongoDB with Mongoose ODM
└── Tests
    └── Jest + Supertest (integration-first)

INTEGRATION POINTS
├── API Endpoints: /api/v1/* (RESTful)
├── Data Flow: Request → Route → Controller → Service → Model → MongoDB
├── Dependencies: express, mongoose, joi (validation), winston (logging)
└── Cross-cutting: JWT auth middleware, error handler middleware

KEY INSIGHTS
- Consistent error handling via custom AppError class
- Validation with Joi schemas before Mongoose
- No caching layer (potential performance issue for reads)
- Tests use real MongoDB (integration-first approach)
```

</details>

This provides complete understanding to prevent biased assumptions.
