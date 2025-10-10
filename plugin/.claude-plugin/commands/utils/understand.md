---
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

When analysis is large, create todo list to explore specific areas in detail.

This provides complete understanding to prevent biased assumptions.
