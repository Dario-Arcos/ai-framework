"""Central configuration for SDD hooks: TTLs, budgets, timeouts.

Single source of truth for time-based and numeric constants used across
hooks. Imported by consumers; function defaults reference these for
consistency.

Scope: Tier 1 constants only. Tier 2 (stack patterns) lives in
_sdd_coverage.py get_* functions (Phase 1, config-driven via
.claude/config.json).

Categories:
    - Gate budgets: total time allowed for gate pipeline
    - Subprocess timeouts: per-call upper bounds
    - State TTLs: age limits for cached state files
    - Lock retry: backoff + attempt bounds for flock contention
    - Circuit breakers: failure thresholds
    - Hook lifecycle timeouts: per-event upper bounds (hooks.json)
"""

# ─────────────────────────────────────────────────────────────────
# GATE BUDGETS — total time for gate pipeline execution
# ─────────────────────────────────────────────────────────────────
GATE_BUDGET_SECONDS = 270  # hooks.json TaskCompleted timeout=300 minus 30s margin

# ─────────────────────────────────────────────────────────────────
# SUBPROCESS TIMEOUTS — per-call upper bounds
# ─────────────────────────────────────────────────────────────────
COVERAGE_SUBPROCESS_TIMEOUT = 120  # coverage detection/runner spawn
DETECT_SUBPROCESS_TIMEOUT = 5      # framework detection (cat manifest, grep)
GIT_SUBPROCESS_TIMEOUT = 5         # git log/diff/show
AWAIT_TEST_COMPLETION_TIMEOUT = 60  # wait for sdd-auto-test subprocess
HOOK_INVOCATION_TIMEOUT = 10       # subprocess harness default

# ─────────────────────────────────────────────────────────────────
# STATE TTLs — cached state age limits
# ─────────────────────────────────────────────────────────────────
NEGATIVE_CACHE_TTL = 300       # 5 min — coverage-failure short-circuit
TEST_STATE_TTL = 600           # 10 min — test run result
COVERAGE_STATE_TTL = 14400     # 4h — coverage tracking state
FAILURE_STATE_TTL = 7200       # 2h — teammate-idle failure log
SKILL_INVOKED_TTL = 14400      # 4h — skill invocation signal
BASELINE_TTL = 14400           # 4h — SDD baseline commit
TEST_CMD_CACHE_TTL = 3600      # 1h — detected test command cache
RECENT_TEST_WINDOW = 60        # 1 min — "just finished" test proximity

# ─────────────────────────────────────────────────────────────────
# LOCK RETRY — transient contention absorption
# ─────────────────────────────────────────────────────────────────
ACQUIRE_LOCK_MAX_ATTEMPTS = 3
ACQUIRE_LOCK_BACKOFF_SECONDS = 0.1  # 100ms; total max wait ~200ms

# ─────────────────────────────────────────────────────────────────
# CIRCUIT BREAKERS — failure thresholds before giving up
# ─────────────────────────────────────────────────────────────────
MAX_RERUNS = 3                  # auto-test rerun safety valve
FAILURE_CIRCUIT_BREAKER = 3     # teammate-idle consecutive failures before halt

# ─────────────────────────────────────────────────────────────────
# ADAPTIVE GATE TIMEOUT — scales test gate by historical duration
# ─────────────────────────────────────────────────────────────────
ADAPTIVE_GATE_MULTIPLIER = 3
ADAPTIVE_GATE_MIN_TIMEOUT = 30
ADAPTIVE_GATE_MAX_TIMEOUT = 300

# ─────────────────────────────────────────────────────────────────
# HOOK LIFECYCLE TIMEOUTS — authoritative values in hooks.json
# Exposed here for hook-internal logic that needs to know the budget.
# ─────────────────────────────────────────────────────────────────
HOOK_TIMEOUT_PRE_TOOL_USE = 5
HOOK_TIMEOUT_POST_TOOL_USE = 10
HOOK_TIMEOUT_TASK_COMPLETED = 300

# ─────────────────────────────────────────────────────────────────
# PHASE 8 — PER-EDIT FAST-PATH (Factory.ai-aligned test impact)
#
# Rollout default (Phase 8.1): ON. Large projects need per-edit impact
# scoping out of the box — full-suite on every edit is unsustainable.
# Safety rests on the milestone gate (TaskCompleted) which always runs
# the full suite regardless of this flag. Users who want the old
# full-suite-per-edit behavior opt out via .claude/config.json:
#     {"FAST_PATH_ENABLED": false}
#
# Cascade — hooks/sdd-auto-test.py:
#   Rung 1a: edit IS a test file           → run that test file only
#   Rung 1b: edit IS source + session tests → run record_file_edit tests
#   Rung 2:  edit IS source + no session   → [SDD:ORDERING] warn + stack-native impacted
#   Rung 3:  no primitive / failure / fvf  → full suite (safety net)
#   Milestone (TaskCompleted): full suite + coverage + scenarios [unchanged]
#
# Telemetry (test_run_end): fast_path_rung, fast_path_duration_seconds,
# forced_full_reason, session_test_files_count — Meta PTS-style empirical
# observation for rung-distribution analysis post-deployment.
# ─────────────────────────────────────────────────────────────────
FAST_PATH_ENABLED = True            # Phase 8.1 default: cascade ON for per-edit efficiency
FAST_PATH_BUDGET_SECONDS = 30       # rungs 1-2 per-edit cap

# Files whose edit forces Rung 3 (Microsoft TIA fall-back-to-all pattern).
# Lockfiles can invalidate any test through dependency resolution; config
# files alter runtime assumptions test runners can't self-detect.
FAST_PATH_FORCE_FULL_FILES = frozenset({
    # Lockfiles — dependency resolution
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "poetry.lock", "uv.lock", "Cargo.lock", "requirements.txt",
    # Stack configs — runtime assumptions
    "pyproject.toml", "tsconfig.json", "nx.json", "turbo.json",
    "pytest.ini",
    "jest.config.js", "jest.config.ts", "jest.config.mjs", "jest.config.cjs",
    "vitest.config.js", "vitest.config.ts", "vitest.config.mjs",
    "vitest.config.cjs",
})


# ─────────────────────────────────────────────────────────────────
# TIER 2 — STACK PATTERNS (config-driven via .claude/config.json)
#
# Defaults match current hardcoded behavior (zero behavior change).
# Override per-project by writing .claude/config.json with any of:
#   {
#     "SOURCE_EXTENSIONS": [".py", ".jl", ".ex"],
#     "TEST_FILE_PATTERNS": ["(^|/)test_", "\\.spec\\.", "_test\\."],
#     "COVERAGE_REPORT_PATH": "custom/path/to/lcov.info"
#   }
#
# Stack-agnostic principle: the plugin knows about language families
# through detection (detect_test_command, detect_coverage_command) and
# classification (is_source_file, is_test_file). Users with uncommon
# stacks (Julia, Elixir, Ruby unusual layouts) can extend without
# modifying plugin code.
# ─────────────────────────────────────────────────────────────────
import json
from pathlib import Path

DEFAULT_SOURCE_EXTENSIONS = frozenset({
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs",
    ".java", ".kt", ".rb", ".swift", ".c", ".cpp", ".cs",
    ".vue", ".svelte",          # frontend frameworks
    ".mts", ".cts", ".mjs",     # ES module variants
    ".graphql", ".gql",         # schemas with logic
    ".prisma",                  # ORM schemas
    ".proto",                   # protobuf
    ".sql",                     # database
    ".sh", ".bash",             # shell scripts
})

DEFAULT_TEST_FILE_PATTERNS = (
    r"(?:test|spec|__tests__)[/\\]",
    r"\.(?:test|spec)\.",
    r"_tests?\.",
    r"test_",
)

# Per-cwd config cache (keyed by resolved absolute path).
# Invalidation: short process lifetime; edits to .claude/config.json after
# hook start are not picked up until next hook invocation. Acceptable.
_project_config_cache: dict[str, dict] = {}


def _load_project_config(cwd) -> dict:
    """Load .claude/config.json for tier 2 overrides. Cached per cwd.

    Silent on malformed JSON, missing file, permission errors, or invalid
    UTF-8. Returns empty dict in all error cases; callers should treat
    missing keys as "use default".
    """
    cwd_str = str(Path(cwd).resolve())
    if cwd_str in _project_config_cache:
        return _project_config_cache[cwd_str]
    config: dict = {}
    path = Path(cwd) / ".claude" / "config.json"
    if path.exists():
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(config, dict):
                config = {}
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            config = {}
    _project_config_cache[cwd_str] = config
    return config


def get_source_extensions(cwd=None) -> frozenset:
    """Project source file extensions.

    Override via `.claude/config.json`:
        {"SOURCE_EXTENSIONS": [".py", ".jl"]}

    Validation: must be list/tuple of strings starting with ".". A bare
    string or any other type falls back to defaults (not treated as char
    iterable — silent disable would be worse than ignoring the override).

    When cwd is None (back-compat for callers without project context),
    returns defaults.
    """
    if cwd is None:
        return DEFAULT_SOURCE_EXTENSIONS
    override = _load_project_config(cwd).get("SOURCE_EXTENSIONS")
    if override is None:
        return DEFAULT_SOURCE_EXTENSIONS
    # Require list/tuple to avoid accidental char-iteration from bare string
    if not isinstance(override, (list, tuple)):
        return DEFAULT_SOURCE_EXTENSIONS
    valid = frozenset(
        ext for ext in override
        if isinstance(ext, str) and ext.startswith(".") and len(ext) > 1
    )
    if not valid:
        return DEFAULT_SOURCE_EXTENSIONS
    return valid


def get_test_file_patterns(cwd=None) -> tuple:
    """Project test file regex patterns (joined with | in consumer).

    Override via `.claude/config.json`:
        {"TEST_FILE_PATTERNS": ["(^|/)test_", "\\.spec\\."]}

    Validation: must be list/tuple of non-empty strings AND each pattern
    must compile. A malformed entry (e.g., "[" or non-string) falls back
    to defaults. Prevents re.error / TypeError from crashing hooks.

    When cwd is None, returns defaults.
    """
    if cwd is None:
        return DEFAULT_TEST_FILE_PATTERNS
    override = _load_project_config(cwd).get("TEST_FILE_PATTERNS")
    if override is None:
        return DEFAULT_TEST_FILE_PATTERNS
    if not isinstance(override, (list, tuple)):
        return DEFAULT_TEST_FILE_PATTERNS
    import re as _re
    valid = []
    for p in override:
        if not isinstance(p, str) or not p:
            continue
        try:
            _re.compile(p)  # reject malformed regex
        except _re.error:
            continue
        valid.append(p)
    if not valid:
        return DEFAULT_TEST_FILE_PATTERNS
    return tuple(valid)


def get_coverage_report_path(cwd, default_path: str) -> str:
    """Coverage report path. Override via `.claude/config.json`:
        {"COVERAGE_REPORT_PATH": "custom/path/to/lcov.info"}

    When override absent or invalid, returns default_path (framework-derived).
    """
    if cwd is None:
        return default_path
    override = _load_project_config(cwd).get("COVERAGE_REPORT_PATH")
    if override is None or not isinstance(override, str) or not override.strip():
        return default_path
    return override


# ─────────────────────────────────────────────────────────────────
# PHASE 10 — SCENARIO DISCOVERY ROOTS
#
# Scenarios live alongside their spec folders, not in a flat
# `.claude/scenarios/` directory. Default discovery roots cover both
# the Ralph factory layout (`.ralph/specs/{goal}/scenarios/`) and the
# generic docs layout (`docs/specs/{name}/scenarios/`). Projects with
# non-standard spec locations override via `.claude/config.json`.
#
# Pattern matches files at `{root}/{spec}/scenarios/{name}.scenarios.md`
# at any depth — `**` handles nested spec hierarchies (e.g. monorepos
# with `docs/specs/auth/v2/scenarios/auth-v2.scenarios.md`).
# ─────────────────────────────────────────────────────────────────
DEFAULT_SCENARIO_DISCOVERY_ROOTS = (".ralph/specs", "docs/specs")
SCENARIO_FILE_PATTERN = "**/scenarios/*.scenarios.md"


def get_scenario_discovery_roots(cwd=None) -> tuple:
    """Discovery roots for scenario files. Override via `.claude/config.json`:
        {"SCENARIO_DISCOVERY_ROOTS": ["custom/specs"]}

    Validation: list/tuple of non-empty relative path strings. Absolute
    paths and `..` traversal entries fall back to defaults — discovery
    must never escape the project root.

    When cwd is None, returns defaults (called from contexts without
    project scope).
    """
    if cwd is None:
        return DEFAULT_SCENARIO_DISCOVERY_ROOTS
    override = _load_project_config(cwd).get("SCENARIO_DISCOVERY_ROOTS")
    if override is None:
        return DEFAULT_SCENARIO_DISCOVERY_ROOTS
    if not isinstance(override, (list, tuple)):
        return DEFAULT_SCENARIO_DISCOVERY_ROOTS
    valid = []
    for root in override:
        if not isinstance(root, str) or not root.strip():
            continue
        p = root.strip()
        if p.startswith("/") or ".." in Path(p).parts:
            continue
        valid.append(p)
    if not valid:
        return DEFAULT_SCENARIO_DISCOVERY_ROOTS
    return tuple(valid)


def _clear_project_config_cache() -> None:
    """Reset ALL per-cwd caches that depend on project config.

    Clears:
      1. Config dict cache (_project_config_cache)
      2. Compiled test regex cache (_sdd_coverage._compiled_test_pattern.cache_clear())
      3. Coverage command detection cache (_sdd_detect.detect_coverage_command.cache_clear())

    Without clearing #2 and #3, callers of is_test_file and
    detect_coverage_command would return stale values after config reload
    (Codex Phase 1 finding: downstream caches survived config invalidation).

    Lazy imports avoid circular dependencies at module load time.
    """
    _project_config_cache.clear()
    try:
        from _sdd_coverage import _compiled_test_pattern
        _compiled_test_pattern.cache_clear()
    except (ImportError, AttributeError):
        pass
    try:
        from _sdd_detect import detect_coverage_command
        detect_coverage_command.cache_clear()
    except (ImportError, AttributeError):
        pass
