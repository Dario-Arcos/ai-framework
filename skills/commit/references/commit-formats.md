# Commit Formats Reference

## Corporate Format

**Template**: `Tipo|IdTarea|YYYYMMDD|Descripción`

**When**: Task ID pattern detected in arguments (e.g., TRV-345, PROJ-123)

### Components

- **Tipo**: Commit type (priority order)
  1. **Explicit type** (highest): User provides `type: TASK-ID description`
     - Valid: feat, fix, refactor, chore, docs, test, security
  2. **Auto-mapped** (fallback): Based on file categories
     - config → chore
     - docs → docs
     - security → fix
     - test → test
     - main → feat
- **IdTarea**: Task ID from arguments
- **YYYYMMDD**: Current date (`date +%Y%m%d`)
- **Descripción**: Max 60 characters

### Examples

Auto-mapped:
- Input: `"TRV-345 implementación validación formulario"`
- Output: `feat|TRV-345|20251023|implementación validación formulario`

Explicit type:
- Input: `"refactor: TRV-345 mejora módulo autenticación"`
- Output: `refactor|TRV-345|20251023|mejora módulo autenticación`

## Conventional Format

**Template**: `type(scope): description`

**When**: No Task ID detected

### Multiple Commits (by category)

- config: `feat(config): update configuration and commands`
- docs: `docs: enhance documentation`
- security: `fix(security): update security configurations`
- test: `test: add/update tests`
- main: `feat: [description from arguments]`

## File Classification Rules

| Category | Matching Patterns |
|----------|-------------------|
| **config** | `.claude/*`, `*.md` (non-docs), `CLAUDE.md`, configuration files |
| **docs** | `docs/*`, `README*`, `CHANGELOG*`, documentation |
| **security** | `scripts/*`, `*setup*`, `*security*`, security-related |
| **test** | `*test*`, `*spec*`, `*.test.*`, testing files |
| **main** | All other files (core functionality) |

## Grouping Decision

- **Multiple commits**: 2+ categories with 2+ files each OR any security files
- **Single commit**: Only one significant category OR limited changes
- Processing order: security → config → docs → test → main

---

*Version: 1.0.0 | Updated: 2026-02-11*
