---
name: project-init
description: Generate minimal project context memory to prevent implementation failures from missing context
allowed-tools: Read, Glob, Grep, LS, Write
---

# Project Initialization

Extracts critical project context (stack, patterns, constraints) to serve as persistent memory preventing context-related failures.

**Purpose**: High-signal memory for AI execution, NOT comprehensive analysis
**Output**: ~50 lines of critical context preventing 5 common failure modes

## Execution Flow

### Phase 1: Detect Existing Context

Check if `.specify/memory/project-context.md` exists:

- If **YES**: Confirm with user if they want to overwrite or keep existing
- If **NO**: Proceed directly to extraction

### Phase 2: Extract Critical Memory (Selective)

**2.1 Tech Stack Snapshot**

Extract ONLY versions that prevent compatibility failures:

- **Read** package manager files: `package.json`, `requirements.txt`, `Gemfile`, `composer.json`, `go.mod`
- **Extract**: Language version, framework version, database version
- **Identify**: Top 5 critical dependencies (most imported/used)

**Example output**:

```
Stack: Python 3.11.2, FastAPI 0.110.0, PostgreSQL 15
Critical deps: pydantic 2.5, sqlalchemy 2.0, redis 5.0
```

**2.2 Established Patterns**

Extract ONLY patterns that prevent style/convention violations:

- **Grep** for naming patterns: scan 5-10 files for convention (snake_case/camelCase/kebab-case)
- **Read** 2-3 error handling examples: identify throw/raise pattern
- **Grep** for auth implementation: find auth middleware/decorator location
- **Identify** state management: search for Redux/Zustand/Context usage

**Example output**:

```
Naming: snake_case (user_service.py)
Errors: raise HTTPException(status_code=...)
Auth: JWT in utils/auth.py (decorator @require_auth)
State: Redux Toolkit (store/ directory)
```

**2.3 Architecture Constraints**

Extract ONLY constraints that prevent wrong implementation choices:

- **Read** entry point: identify main file (server.js, main.py, index.php)
- **LS** top-level: list ONLY first-level directories (5-7 max)
- **Grep** for API type: search for "GraphQL" OR "REST" OR "gRPC" keywords

**Example output**:

```
Entry: src/main.py
Arch: REST API (no GraphQL)
Structure: api/, models/, services/, utils/, tests/
```

### Phase 3: Generate Minimal project-context.md

Create lightweight context document (~50 lines) using data from Phase 2:

**Template Structure:**

```markdown
# Project Context

**Stack**: [Language] [version] + [Framework] [version]
**DB**: [Database] [version]
**Arch**: [REST/GraphQL/Monolith/Microservices]

## Critical Dependencies

- [dep1] [version]
- [dep2] [version]
- [dep3] [version]
- [dep4] [version]
- [dep5] [version]

## Established Patterns

**Naming**: [example: snake_case / camelCase / kebab-case]
**Errors**: [example: raise HTTPException(...) / throw new Error(...)]
**Auth**: [example: JWT in utils/auth.py with @require_auth]
**State**: [example: Redux Toolkit / Context API / Zustand]

## Entry Point

`[file path: src/main.py / server.js / index.php]`

## Top-Level Structure
```

[dir1]/ # [purpose]
[dir2]/ # [purpose]
[dir3]/ # [purpose]
[dir4]/ # [purpose]
[dir5]/ # [purpose]

```

---
**Updated**: [YYYY-MM-DD] | Re-run when stack changes
```

### Phase 4: Update CLAUDE.md Reference

Check if `CLAUDE.md` already references `project-context.md`:

```bash
if ! grep -q "@.specify/memory/project-context.md" CLAUDE.md; then
    # Add reference in Documentation References section
    # Insert:
    # **Project Context**: @.specify/memory/project-context.md
fi
```

### Phase 5: Output

```
✅ Project context memory created (~50 lines)

📦 Stack:
   [Language] [version] + [Framework] [version]
   [Database] [version]

📐 Patterns Extracted:
   Naming: [convention]
   Errors: [pattern]
   Auth: [approach]

📄 Generated:
   .specify/memory/project-context.md (minimal, high-signal)
   CLAUDE.md (reference added if missing)

💡 Context prevents 5 common failure modes:
   1. Wrong library usage
   2. Naming convention violations
   3. Inconsistent error handling
   4. Version incompatibilities
   5. Architecture misalignment

Next: Claude tiene memoria persistente del proyecto.
```

## Notes

- **Purpose**: Persistent memory to prevent context-related failures
- **Not an audit**: Extracts ONLY critical context (stack, patterns, constraints)
- **Minimal output**: ~50 lines vs 400+ in comprehensive analysis
- **Signal-focused**: 90% high-signal content preventing real failures
- **Template-driven**: No AI synthesis, deterministic generation
- **Silent fail**: Non-blocking on analysis errors
- **User confirmation**: Always ask before overwriting existing context
