---
description: Initialize or update project context with deep analysis and agent recommendations
argument-hint: "deep (optional: force deep analysis)"
allowed-tools: Read, Glob, Grep, LS, Write
---

# Project Initialization

Performs deep codebase analysis and generates project-aware configuration.

**Reuses**: `/utils:understand` phases 1-5 for systematic discovery

## Execution Flow

### Phase 1: Detect Existing Context

Check if `.specify/memory/project-context.md` exists:

- If YES and no "deep" argument: Confirm overwrite
- If YES and "deep" argument: Skip confirmation, force overwrite
- If NO: Proceed directly

### Phase 2: Deep Discovery (Reuse understand.md logic)

Execute systematic analysis following `/utils:understand` methodology:

**Phase 2.1: Project Discovery**

- **Glob** to map entire project structure
- **Read** key files: README.md, package.json, requirements.txt, Gemfile, composer.json, go.mod
- **Grep** to identify technology patterns
- **Read** entry points: main.js, server.js, app.py, main.py, index.php, main.go

Discover:

- Project type and main technologies
- Architecture patterns (MVC, microservices, monolith, etc.)
- Directory structure and organization
- Dependencies and external integrations
- Build and deployment setup

**Phase 2.2: Code Architecture Analysis**

- **Entry points**: Main files, index files, app initializers
- **Core modules**: Business logic organization
- **Data layer**: Database, models, repositories
- **API layer**: Routes, controllers, endpoints
- **Frontend**: Components, views, templates
- **Configuration**: Environment setup, constants
- **Testing**: Test structure and coverage

**Phase 2.3: Pattern Recognition**

Identify established patterns:

- Naming conventions for files and functions
- Code style and formatting rules
- Error handling approaches
- Authentication/authorization flow
- State management strategy
- Communication patterns between modules

**Phase 2.4: Dependency Mapping**

- Internal dependencies between modules
- External library usage patterns
- Service integrations
- API dependencies
- Database relationships

**Phase 2.5: Integration Analysis**

- API endpoints and their consumers
- Database queries and their callers
- Event systems and listeners
- Shared utilities and helpers
- Cross-cutting concerns (logging, auth)

### Phase 3: Tech Stack Detection (Extended)

Beyond quick detection, parse exact versions and all dependencies:

**Package Managers:**

```bash
# Node.js
if [ -f "package.json" ]; then
    node_version=`node --version 2>/dev/null || echo "unknown"`
    # Parse dependencies for frameworks, databases, tools
fi

# Python
if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    python_version=`python --version 2>/dev/null || python3 --version 2>/dev/null || echo "unknown"`
    # Parse for FastAPI, Django, Flask, SQLAlchemy, pytest, etc.
fi

# Ruby
if [ -f "Gemfile" ]; then
    ruby_version=`ruby --version 2>/dev/null || echo "unknown"`
    # Parse for Rails, ActiveRecord, RSpec
fi

# PHP
if [ -f "composer.json" ]; then
    php_version=`php --version 2>/dev/null || echo "unknown"`
    # Parse for Laravel, Symfony
fi

# Go
if [ -f "go.mod" ]; then
    go_version=`go version 2>/dev/null || echo "unknown"`
fi
```

**Infrastructure Detection:**

```bash
# Docker
docker_detected=false
if [ -f "Dockerfile" ] || [ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ]; then
    docker_detected=true
fi

# Kubernetes
k8s_detected=false
if [ -d "k8s" ] || [ -d ".kube" ] || [ -f "kubernetes.yml" ]; then
    k8s_detected=true
fi

# Terraform
terraform_detected=false
if [ -d "terraform" ] || [ -f "main.tf" ]; then
    terraform_detected=true
fi

# CI/CD
ci_cd=""
if [ -d ".github/workflows" ]; then
    ci_cd="GitHub Actions"
elif [ -f ".gitlab-ci.yml" ]; then
    ci_cd="GitLab CI"
elif [ -f "Jenkinsfile" ]; then
    ci_cd="Jenkins"
fi
```

### Phase 4: Agent Mapping + Gap Analysis

**A. Load Agent Registry**

Read all agents from `.claude/agents/**/*.md`:

```bash
# Extract agent metadata
agents=""

for category_dir in .claude/agents/*/; do
    category=`basename "$category_dir"`

    for agent_file in "$category_dir"*.md; do
        if [ -f "$agent_file" ]; then
            agent_name=`grep "^name:" "$agent_file" | head -1 | sed 's/name: *//'`
            agent_desc=`grep "^description:" "$agent_file" | head -1 | sed 's/description: *//'`

            agents="$agents\n$agent_name|$category|$agent_desc"
        fi
    done
done
```

**B. Map Tech → Agents (Same registry as workspace-status.py)**

```yaml
Core (Always):
  - code-quality-reviewer
  - systematic-debugger
  - test-automator

Languages:
  python: [python-pro]
  javascript: [javascript-pro]
  typescript: [typescript-pro, frontend-developer]
  ruby: [ruby-pro]
  php: [php-pro]

Frameworks:
  react|nextjs: [frontend-developer]
  fastapi|django|flask: [python-pro, backend-architect]
  express|fastify: [javascript-pro, backend-architect]
  rails: [ruby-pro, backend-architect]
  laravel: [php-pro, backend-architect]

Databases:
  postgres|pg: [database-optimizer, database-admin]
  mongodb|mongoose: [database-optimizer, database-admin]
  mysql: [database-optimizer, database-admin]

Infrastructure:
  docker: [deployment-engineer, devops-troubleshooter]
  kubernetes|k8s: [kubernetes-architect, deployment-engineer]
  terraform: [terraform-specialist, cloud-architect]

Testing:
  pytest: [test-automator, tdd-orchestrator]
  jest: [test-automator, tdd-orchestrator]
  playwright: [playwright-test-generator]

APIs:
  graphql: [graphql-architect]
  rest|openapi: [backend-architect, api-documenter]
```

**C. Gap Detection**

```bash
# Check dependencies for unmapped tech
unmapped=""

# Check Node.js dependencies
if [ -f "package.json" ]; then
    # Extract unique packages not in TECH_TO_AGENTS mapping
    # Example: stripe, aws-sdk, sendgrid, etc.
fi

# Check Python dependencies
if [ -f "requirements.txt" ]; then
    # Example: stripe, boto3, celery, redis, etc.
fi
```

If gaps found, display:

```markdown
## ⚠️ Missing Agents (Detected Gaps)

### stripe (detected in package.json)

❌ No specialized agent found for Stripe API integration

**Recommendation**: Create custom agent

- **Name**: `stripe-integration-expert`
- **Category**: Web & Application
- **Purpose**: Stripe API patterns, webhook handling, payment flows
- **Template**: Based on existing javascript-pro structure

💡 **¿Crear ahora?** (S/n):
```

### Phase 5: Generate Comprehensive project-context.md

```markdown
# Project Context

**Generated**: YYYY-MM-DD HH:MM | **Framework**: ai-framework v1.0
**Analysis**: Deep | **Update**: Re-run when architecture changes

## 📦 Technology Stack

### Core

- **Language**: [Detected language + version]
- **Framework**: [Detected framework + version]
- **Database**: [Detected database]

### Key Dependencies

[List from package manager with versions]

### Infrastructure

- Docker [if detected]
- Kubernetes [if detected]
- CI/CD: [GitHub Actions/GitLab CI/etc]

## 🏗️ Architecture

**Pattern**: [MVC/Microservices/Monolith/etc from Phase 2.2]
**Entry Point**: [File path from Phase 2.1]

[Directory tree structure from Glob]

## 🎨 Code Patterns

### Naming Conventions

- Files: [pattern from Phase 2.3]
- Functions: [pattern from Phase 2.3]
- Constants: [pattern from Phase 2.3]

### Error Handling

[Pattern from Phase 2.3]

### Testing Strategy

[Pattern from Phase 2.2]

## 🤖 Recommended Agents

### Core (Always)

[List from Phase 4.B core]

### Project-Specific

[List from Phase 4.B mapped to detected tech]

## 🔗 Integration Points

[Output from Phase 2.5]

## ⚠️ Potential Issues

[Flagged during analysis from Phase 2]

---

**Generated by**: /utils:project-init | **Framework**: ai-framework v1.0
```

### Phase 6: Update CLAUDE.md Reference

Check if `CLAUDE.md` already references `project-context.md`:

```bash
if ! grep -q "@.specify/memory/project-context.md" CLAUDE.md; then
    # Add reference after Constitution section
    # Insert:
    # **Project Context**: @.specify/memory/project-context.md
    # - Tech stack and architecture patterns
    # - Project-specific conventions and patterns
    # - Recommended agents for this codebase
fi
```

### Phase 7: Output

```
✅ Project context initialized (deep analysis)

📦 Stack Detected:
   - [Language] [version]
   - [Framework] [version]
   - [Database]
   - [Infrastructure tools]

🤖 Recommended Agents ([total]):
   Core:
   - code-quality-reviewer
   - systematic-debugger
   - test-automator

   Project-Specific:
   - [agent list based on tech]

📄 Generated:
   - .specify/memory/project-context.md (comprehensive)
   - CLAUDE.md (reference added if missing)

⚠️ Potential Issues Flagged:
   - [issue 1]
   - [issue 2]

Next: Claude ahora conoce tu proyecto en profundidad.
      Sugerirá agentes contextuales automáticamente.
```

## Extension Guide

To add new tech → agent mappings:

1. Edit Phase 4.B mapping registry
2. Add tech detection in Phase 3 if needed
3. Mapping is automatically applied

## Notes

- Reuses `/utils:understand` logic to avoid duplication
- Template-driven generation (no AI synthesis required)
- Registry-based agent mapping (extensible)
- Silent fail on analysis errors (non-blocking)
- User confirmation for overwrites
