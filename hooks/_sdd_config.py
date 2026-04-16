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
