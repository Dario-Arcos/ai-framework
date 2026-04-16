# Analysis Layers Reference

5 layers executed sequentially. Each layer feeds specific output files.

## Layer 1: Manifests → stack.md, project.md

Glob and read package manager files:
- `package.json`, `pyproject.toml`, `requirements.txt`, `setup.py`
- `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json`
- `pnpm-workspace.yaml`, `lerna.json`, `nx.json` (monorepo signals)

Extract:
- **Description**: `description` field from manifest, or first paragraph of README.md → project.md
- **Runtime**: version from engines, python_requires, go.mod
- **Framework**: main framework + version (largest dependency by import frequency)
- **Project type**: monorepo | library | CLI | API | SaaS | static-site (infer from structure + manifest)
- **Critical deps**: top 5-7 by import frequency, with one-word purpose
- **Scripts**: build, dev, lint, version (test commands route to conventions.md Testing)
- **Environment**: variables from `.env.example` (NEVER read `.env`)

## Layer 2: Configs → stack.md, conventions.md

Glob and read:
- `tsconfig.json`, `jsconfig.json` → strict mode, paths, target
- `.eslintrc*`, `.prettierrc*`, `biome.json` → formatting rules
- `.editorconfig` → tabs/spaces, line endings
- `jest.config.*`, `vitest.config.*`, `pytest.ini` → test framework
- `docker-compose.yml`, `Dockerfile` → containerization
- `.github/workflows/*.yml`, `.gitlab-ci.yml` → CI/CD pipeline

Extract:
- **Compiler settings**: strict mode, module system, target
- **Formatting**: tabs/spaces, quotes, semicolons (only if explicitly configured)
- **Test framework**: name, config location, coverage setup
- **CI/CD**: pipeline tool, key stages (build/test/deploy)
- **Containerization**: base image, exposed ports, services

## Layer 3: Structure → architecture.md, project.md

Analyze:
- Top-level directories (depth 1): `ls` and note purpose of each
- Entry points: glob `**/index.{ts,js,py}`, `**/main.{ts,js,py,go}`, `**/app.{ts,js,py}`
- File distribution: count files per major directory
- Boundary signals: separate `api/`, `domain/`, `infrastructure/` dirs suggest layered arch

Extract:
- **Entry point(s)**: path + what it bootstraps
- **Layer map**: each major directory → one-line purpose
- **Boundaries**: which directories are allowed to import from which (if detectable)
- **Data flow**: request path from entry to response (if API/web project)
- **Domain model hints**: directories named after business concepts (users/, orders/, payments/)

## Layer 4: Patterns → conventions.md, architecture.md, project.md

Sample 5-10 grep matches per pattern:

```
# Naming conventions → conventions.md
grep: "^(export )?(function|const|class|def|func) \w+"

# Error handling → conventions.md
grep: "(throw|raise|return err|new Error|\.catch|try\s*\{)"

# Import style → conventions.md
grep: "^(import|from|require)"

# Paradigm signals → project.md (boundaries → architecture.md)
grep: "(interface |abstract class|implements |extends )"     # OOP
grep: "(pipe|compose|curry|map\(|reduce\(|filter\()"         # Functional
grep: "(emit|on\(|subscribe|publish|EventEmitter)"           # Event-driven
grep: "(Repository|Service|Controller|UseCase|Handler)"      # DDD/Clean arch

# Test patterns → conventions.md
grep: "(describe|test|it|def test_|#\[test\])\("

# Logging/observability → conventions.md
grep: "(logger\.|console\.|log\.|winston|pino|slog)"
```

Extract:
- **Naming**: file convention (kebab/snake/camel), function convention, class convention
- **Error handling**: dominant pattern (try/catch, Result type, error returns)
- **Imports**: ESM/CJS/mixed, relative vs absolute paths
- **Paradigms detected**: OOP / functional / event-driven / procedural → project.md
- **Testing conventions**: describe/it style, file naming (*.test.* vs *.spec.*)
- **Logging**: framework used, pattern (structured/unstructured)

## Layer 5: Key File Sampling → all files

Read 5-8 representative files to confirm grep findings and extract signals that patterns miss:

1. **Entry point** (always): main/index/app file
2. **Largest file** in top 2-3 directories: reveals dominant coding style
3. **One test file** (if tests exist): confirms test conventions
4. **README.md** (if exists): first 50 lines — project description, setup instructions
5. **One config/setup file**: middleware chain, DI container, route registration

Extract:
- **Style confirmation**: validate Layer 4 findings against actual code
- **Framework idioms**: how the project uses its framework (conventional vs custom)
- **API type**: REST / GraphQL / gRPC / WebSocket / CLI (from routes, schemas, commands)
- **Domain concepts**: key business entities, terminology used in variable/type names → project.md

## Layer 6: Stack-Agnostic Hooks Config → `.claude/config.json`

**Purpose**: make the plugin's coverage gate, test detection, and file
classification aware of the project's actual stack without requiring the
user to read code. Invisible auto-detection = visible configuration.

Derive each key from Layer 1 + Layer 2 findings:

### `SOURCE_EXTENSIONS`

Emit only when NON-default extensions were detected. Defaults cover Python,
TypeScript, JavaScript, Go, Rust, Java, Kotlin, Ruby, Swift, C, C++, C#,
Vue, Svelte, GraphQL, SQL, shell. Extend with:

| Manifest / signal | Add extensions |
|---|---|
| `Project.toml` + Julia `.jl` files | `.jl` |
| `mix.exs` + Elixir `.ex`/`.exs` files | `.ex`, `.exs` |
| `pubspec.yaml` + Dart `.dart` files | `.dart` |
| `*.zig` files present | `.zig` |
| `*.nim` files + `.nimble` manifest | `.nim` |

Output format: full list (merge with defaults, don't replace).

### `TEST_FILE_PATTERNS`

Emit when the detected test framework uses a pattern NOT covered by the
default regex (`(?:test|spec|__tests__)[/\\]`, `\.(?:test|spec)\.`,
`_tests?\.`, `test_`). Heuristics:

| Framework signal | Additional pattern |
|---|---|
| Ruby `spec/` directory or `_spec.rb` files | `_spec\.rb$` |
| PHPUnit (`*Test.php` convention) | `Test\.php$` |
| Elixir ExUnit (`*_test.exs`) | `_test\.exs$` |
| Mix test (`test/` with `*_test.exs`) | (default covers `test/`) |
| Pytest with `tests_*` prefix (non-standard) | `tests_` |

### `COVERAGE_REPORT_PATH`

Emit only when the detected framework writes to a NON-default path. Check
for explicit configuration in pyproject.toml / vitest.config.ts / etc.
Examples:

- `pyproject.toml` with `[tool.pytest.ini_options] --cov-report=xml:build/coverage.xml` → `"build/coverage.xml"`
- `vitest.config.ts` with `coverage.outputDir = "reports/coverage"` → `"reports/coverage/lcov.info"`

### Visibility / output

After writing `.claude/config.json`, print to user:
```
📝 Stack-agnostic hooks config written: .claude/config.json
   Source extensions tracked: .py, .jl
   Test patterns: default + _spec.rb
   Coverage report: reports/coverage/lcov.info
```

Rationale: without this visibility, Tier 2 config is invisible. Users with
non-mainstream stacks (Julia, Elixir, Ruby unusual layouts) would see the
plugin silently ignore their files, undermining trust.

Do NOT write `.claude/config.json` when detection only produces defaults
(zero signal in the file). The presence of `.claude/config.json` implies
non-default overrides; redundant content is noise.

---

*Version: 1.2.0 | Updated: 2026-04-16*
