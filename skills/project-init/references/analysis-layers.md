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

## Layer 7: Factory-Readiness Audit (`.claude/rules/factory-readiness.md`)

Teach new users the mental model of the ai-framework factory contract
by showing them where they stand. Emit on every `/project-init`
invocation so the file tracks reality over time (as scenarios are
authored, Ralph configured, coverage added).

Observable checks, each emitted as a short bullet that cites a file
path the user can inspect:

### Scenario contract presence

- Count `.claude/scenarios/*.scenarios.md` files in git HEAD.
- Zero: `Scenarios: not yet defined — run /scenario-driven-development to author the first holdout contract.`
- N > 0: `Scenarios: {N} file(s) tracked in git.`

### Ralph orchestration readiness

- Check `.ralph/config.sh` presence and the GATE_* variables within.
- Missing: `Ralph mode: not configured — plugin operates in non-Ralph (interactive) mode.`
- Present + GATE_TEST set: `Ralph mode: ready. Configured gates: {list of GATE_* with non-empty values}.`
- Present + GATE_TEST empty: `Ralph mode: partial — .ralph/config.sh exists but GATE_TEST is empty. Configure gates before spawning teammates.`

### Per-edit cascade configuration

- Read `FAST_PATH_ENABLED` from plugin config (inspect
  `.claude/config.json` override; default True post-Phase-8.1).
- Emit: `Per-edit cascade: {on|off} (FAST_PATH_ENABLED={true|false}).`

### Coverage detection

- Probe `detect_coverage_command` for the project.
- Detected: `Coverage: {command} → {report path}.`
- None: `Coverage: no tool detected — add pytest-cov / c8 / cargo-llvm-cov to enable the coverage gate.`

### Web project signature

- If `package.json` declares a web-framework dep
  (react/vue/svelte/next/nuxt/astro/remix):
  `Web project detected: /dogfood will be signaled at milestone completion (set AUTO_DOGFOOD=false in .claude/config.json to opt out).`

### Mission observability

- Check `.claude/metrics.jsonl` existence + recent
  `mission_report_generated` events.
- No reports ever written: `Mission reports: none yet — invoke /ai-framework:mission-report any time to aggregate telemetry.`
- One or more: `Mission reports: last written {path} ({iso timestamp}).`

### Emission format

`.claude/rules/factory-readiness.md` receives the bullets under a
short preamble explaining the file's purpose (mirror, not gate). The
rule file is auto-regenerated on every `/project-init`.

Rationale: factory-readiness is not an enforcement gate, it's a
mirror. New users learn the contract by seeing their gaps; advanced
users see what's missing before shipping to teammates.

### Scope discipline

- Only OBSERVABLE checks (files on disk, git state, config values).
  Never "I think you should do X."
- Each bullet cites a file path the user can inspect.
- Do NOT duplicate content that lives in CLAUDE.md or other rule
  files — this layer teaches the contract, not constraints.

---

*Version: 1.3.0 | Updated: 2026-04-21*
