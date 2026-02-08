# Analysis Layers Reference

## Layer 1: Manifests (Read 100%)

Glob and read package manager files:
- `package.json`, `package-lock.json` (deps section only)
- `pyproject.toml`, `requirements.txt`, `setup.py`
- `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json`

Extract:
- Runtime version (engines, python_requires)
- Framework + version (main dependency)
- Top 5-7 dependencies by import frequency
- Available scripts (build, test, dev)

## Layer 2: Configs (Read 100%)

Glob and read:
- `tsconfig.json`, `jsconfig.json`
- `.eslintrc*`, `.prettierrc*`, `biome.json`
- `.editorconfig`
- `pytest.ini`, `jest.config.*`, `vitest.config.*`
- `.env.example` (NOT `.env`)
- `docker-compose.yml`

Extract:
- Compiler/strict mode settings
- Formatting rules (tabs/spaces, quotes)
- Test framework configuration
- Expected environment variables

## Layer 3: Structure (LS + Glob)

Analyze:
- Top-level directories (depth 1)
- Entry points: `**/index.{ts,js,py}`, `**/main.{ts,js,py,go}`, `**/app.{ts,js,py}`
- File distribution per directory

Extract:
- Entry point file(s)
- Layer distribution (src/, lib/, api/)
- Major directories and their purpose

## Layer 4: Patterns (Grep targeted)

Sample 5-10 matches for each:

```
# Naming conventions
grep: "^(export )?(function|const|def|func) \w+"

# Error handling
grep: "(throw|raise|return err|new Error)"

# Import style
grep: "^(import|from|require)"

# Auth patterns
grep: "(@auth|@require|middleware.*auth|guard)"

# Test patterns
grep: "(describe|test|it|def test_)\("
```

Extract:
- Dominant naming convention (camelCase/snake_case/etc.)
- Error handling pattern
- Import style (ESM/CJS)
- Auth mechanism (if exists)

## Layer 5: Key File Sampling

Read 5-8 representative files:

1. **Entry point** (always): `main.*`, `index.*`, `app.*`
2. **One file per major directory**: Largest file in top 3-4 dirs
3. **One test file** (if tests exist): Any `*.test.*` or `*.spec.*`
4. **README.md** (if exists): First 50 lines only

Extract:
- Code style in practice (confirms grep findings)
- Framework idioms and patterns
- API type indicators (REST/GraphQL/gRPC)
