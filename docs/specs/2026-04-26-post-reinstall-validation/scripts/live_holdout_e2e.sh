#!/usr/bin/env bash
# Live end-to-end test for Phase 2 (F1 holdout) and Phase 3 (F2/F3
# scenario hash binding) and Phase 4 (F4 TaskUpdate passthrough) and
# Phase 7 (--no-verify bypass). Invokes the installed plugin's
# sdd-test-guard.py via subprocess for both Ralph and non-Ralph modes.
#
# Usage:
#   MODE=nonralph ./live_holdout_e2e.sh   # default
#   MODE=ralph    ./live_holdout_e2e.sh
#
# Reports PASS/FAIL per phase. Final exit 0 if all GO.

set -uo pipefail
MODE="${MODE:-nonralph}"
INSTALLED="${CLAUDE_PLUGIN_ROOT:-/Users/dariarcos/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.5.0}"
GUARD="$INSTALLED/hooks/sdd-test-guard.py"
HOOKS="$INSTALLED/hooks"

if [[ ! -f "$GUARD" ]]; then
  echo "[FATAL] guard not found at $GUARD — reinstall first"
  exit 1
fi

work=$(mktemp -d -t "post-reinstall-${MODE}-XXX")
trap 'rm -rf "$work"' EXIT
cd "$work"

if [[ "$MODE" == "ralph" ]]; then
  MODE_DIR=".ralph/specs"
  mkdir -p .ralph
  echo 'GATE_TEST=""' > .ralph/config.sh
else
  MODE_DIR="docs/specs"
fi
SCEN_DIR="$MODE_DIR/x/scenarios"
mkdir -p "$SCEN_DIR"
cat > "$SCEN_DIR/x.scenarios.md" <<'SCEN_EOF'
---
name: x
---
## SCEN-001: probe
**Given**: x
**When**: x
**Then**: x
**Evidence**: x
SCEN_EOF

git init -q
git add -A
git -c "core.hooksPath=/dev/null" commit -q -m "init"

probe_guard() {
  local cmd="$1"
  python3 - "$GUARD" "$work" "$cmd" <<'PY'
import json, subprocess, sys
guard, cwd, cmd = sys.argv[1], sys.argv[2], sys.argv[3]
payload = {
    "session_id": "post-reinstall",
    "cwd": cwd,
    "tool_name": "Bash",
    "tool_input": {"command": cmd},
}
r = subprocess.run(
    ["python3", guard], input=json.dumps(payload),
    capture_output=True, text=True, timeout=10,
)
print(f"rc={r.returncode}")
print(f"stderr={r.stderr.strip()[:300]}")
PY
}

write_flag_with_hashes() {
  python3 - "$work" "$HOOKS" <<'PY'
import sys
sys.path.insert(0, sys.argv[2])
from _sdd_state import write_skill_invoked
from _sdd_scenarios import current_scenario_hashes
cwd = sys.argv[1]
h = current_scenario_hashes(cwd)
write_skill_invoked(cwd, "verification-before-completion", scenario_hashes=h)
print(f"flag written with {len(h)} scenario hash(es)")
PY
}

clear_flag() {
  python3 - "$work" "$HOOKS" <<'PY'
import sys, os
sys.path.insert(0, sys.argv[2])
from _sdd_state import skill_invoked_path
try:
    os.unlink(skill_invoked_path(sys.argv[1], "verification-before-completion"))
except FileNotFoundError:
    pass
PY
}

phase_pass=0
phase_fail=0
report() {
  local name="$1" expected="$2" got="$3"
  if [[ "$expected" == "$got" ]]; then
    echo "  [OK]   $name (rc=$got)"
    phase_pass=$((phase_pass+1))
  else
    echo "  [FAIL] $name: expected rc=$expected, got rc=$got"
    phase_fail=$((phase_fail+1))
  fi
}

extract_rc() { echo "$1" | grep -oE 'rc=-?[0-9]+' | head -1 | cut -d= -f2; }

echo "=== MODE: $MODE  WORK: $work ==="

echo
echo "Phase 2 — F1 holdout consume"
clear_flag
out=$(probe_guard "git commit -m 'p2-1'")
report "pre-skill commit BLOCKS" 2 "$(extract_rc "$out")"

write_flag_with_hashes
out=$(probe_guard "git commit -m 'p2-2'")
report "post-skill first commit PASSES (consumes flag)" 0 "$(extract_rc "$out")"

out=$(probe_guard "git commit -m 'p2-3'")
report "F1 second commit BLOCKS without re-invocation" 2 "$(extract_rc "$out")"

echo
echo "Phase 3 — F2/F3 hash binding"
clear_flag
write_flag_with_hashes
echo "## SCEN-002: tampered" >> "$SCEN_DIR/x.scenarios.md"
out=$(probe_guard "git commit -m 'p3-edit'")
report "F2/F3 edited scenario blocks commit" 2 "$(extract_rc "$out")"

echo
echo "Phase 7 — --no-verify bypass"
clear_flag
out=$(probe_guard "git commit --no-verify -m 'p7'")
report "--no-verify allows" 0 "$(extract_rc "$out")"
if echo "$out" | grep -q "no-verify bypass logged"; then
  echo "  [OK]   telemetry log present"
else
  echo "  [FAIL] telemetry log MISSING"
  phase_fail=$((phase_fail+1))
fi

echo
echo "Phase 4 — TaskUpdate passthrough"
clear_flag
out=$(python3 - "$GUARD" "$work" <<'PY'
import json, subprocess, sys
payload = {
    "session_id": "post-reinstall",
    "cwd": sys.argv[2],
    "tool_name": "TaskUpdate",
    "tool_input": {"status": "completed", "taskId": "T1"},
}
r = subprocess.run(["python3", sys.argv[1]], input=json.dumps(payload),
                   capture_output=True, text=True, timeout=10)
print(f"rc={r.returncode}")
print(f"stderr={r.stderr.strip()[:200]}")
PY
)
report "TaskUpdate(completed) passes (F4)" 0 "$(extract_rc "$out")"
if echo "$out" | grep -q "SDD:POLICY"; then
  echo "  [FAIL] [SDD:POLICY] still appears (F4 not closed)"
  phase_fail=$((phase_fail+1))
else
  echo "  [OK]   no [SDD:POLICY] in stderr"
fi

echo
echo "=== $MODE summary: $phase_pass passed, $phase_fail failed ==="
[[ $phase_fail -eq 0 ]] && exit 0 || exit 1
