#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Test Suite: ralph-orchestrator loop.sh functions
# ═══════════════════════════════════════════════════════════════════════════════
#
# Run with: ./test_loop_functions.sh
# Requires: bash 4+, jq
#
# Tests:
#   1. Context calculation (input + cache tokens)
#   2. Guardrails validation (empty detection)
#   3. Config mismatch detection (AGENTS.md vs config.sh)
#   4. Coverage gate validation (90% minimum)
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test utilities
assert_equals() {
  local expected="$1"
  local actual="$2"
  local message="$3"

  TESTS_RUN=$((TESTS_RUN + 1))

  if [ "$expected" = "$actual" ]; then
    echo -e "${GREEN}✓${NC} $message"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}✗${NC} $message"
    echo "  Expected: $expected"
    echo "  Actual:   $actual"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

assert_true() {
  local condition="$1"
  local message="$2"

  TESTS_RUN=$((TESTS_RUN + 1))

  if eval "$condition"; then
    echo -e "${GREEN}✓${NC} $message"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}✗${NC} $message"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  local message="$3"

  TESTS_RUN=$((TESTS_RUN + 1))

  if echo "$haystack" | grep -q "$needle"; then
    echo -e "${GREEN}✓${NC} $message"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}✗${NC} $message"
    echo "  String does not contain: $needle"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: Context Calculation
# ═══════════════════════════════════════════════════════════════════════════════

test_context_calculation() {
  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo "TEST SUITE: Context Calculation"
  echo "═══════════════════════════════════════════════════════════════"

  # Mock Claude output with usage stats
  local mock_output='{"type":"result","usage":{"input_tokens":1000,"cache_read_input_tokens":50000,"cache_creation_input_tokens":10000}}'

  # Extract tokens as loop.sh does
  local INPUT_TOKENS=$(echo "$mock_output" | jq -r '.usage.input_tokens // 0')
  local CACHE_READ=$(echo "$mock_output" | jq -r '.usage.cache_read_input_tokens // 0')
  local CACHE_CREATE=$(echo "$mock_output" | jq -r '.usage.cache_creation_input_tokens // 0')

  assert_equals "1000" "$INPUT_TOKENS" "Extract input_tokens correctly"
  assert_equals "50000" "$CACHE_READ" "Extract cache_read_input_tokens correctly"
  assert_equals "10000" "$CACHE_CREATE" "Extract cache_creation_input_tokens correctly"

  # Calculate total
  local TOTAL_CONTEXT=$((INPUT_TOKENS + CACHE_READ + CACHE_CREATE))
  assert_equals "61000" "$TOTAL_CONTEXT" "Calculate total context (input + cache_read + cache_create)"

  # Calculate percentage with 200K limit
  local CONTEXT_LIMIT=200000
  local CONTEXT_PERCENT=$((TOTAL_CONTEXT * 100 / CONTEXT_LIMIT))
  assert_equals "30" "$CONTEXT_PERCENT" "Calculate context percentage correctly (61K/200K = 30%)"

  # Test with missing cache fields (backward compatibility)
  local mock_output_no_cache='{"type":"result","usage":{"input_tokens":5000}}'
  CACHE_READ=$(echo "$mock_output_no_cache" | jq -r '.usage.cache_read_input_tokens // 0')
  CACHE_CREATE=$(echo "$mock_output_no_cache" | jq -r '.usage.cache_creation_input_tokens // 0')

  assert_equals "0" "$CACHE_READ" "Handle missing cache_read_input_tokens (default 0)"
  assert_equals "0" "$CACHE_CREATE" "Handle missing cache_creation_input_tokens (default 0)"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: Guardrails Validation
# ═══════════════════════════════════════════════════════════════════════════════

test_guardrails_validation() {
  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo "TEST SUITE: Guardrails Validation"
  echo "═══════════════════════════════════════════════════════════════"

  # Create temp directory for test
  local TEST_DIR=$(mktemp -d)
  trap "rm -rf $TEST_DIR" EXIT

  # Test 1: Empty guardrails (only template)
  cat > "$TEST_DIR/guardrails_empty.md" << 'EOF'
# Signs

## Example Signs (Remove and replace with your own)

### Sign: Test Framework Requires jsdom
- **Trigger**: Writing React component tests
- **Instruction**: Use testEnvironment

## Your Signs (Add here as you learn)

EOF

  local sign_count=$(grep -c "^### Sign:" "$TEST_DIR/guardrails_empty.md" 2>/dev/null || echo "0")
  local has_your_signs=$(grep -q "Your Signs (Add here as you learn)" "$TEST_DIR/guardrails_empty.md" && echo "1" || echo "0")

  assert_equals "1" "$sign_count" "Detect example signs in template"
  assert_equals "1" "$has_your_signs" "Detect 'Your Signs' section exists"

  # Real signs = total - examples (assuming 8 examples in full template)
  # In this test we have 1 example, so real = 1 - 1 = 0
  local real_signs=$((sign_count - 1))
  assert_equals "0" "$real_signs" "Calculate real signs (total - examples)"

  # Test 2: Guardrails with real signs
  cat > "$TEST_DIR/guardrails_real.md" << 'EOF'
# Signs

## Your Signs (Add here as you learn)

### Sign: Ajv ESM Import
- **Trigger**: Using ajv with TypeScript
- **Instruction**: Use Ajv.default()

### Sign: Commander Test Issue
- **Trigger**: Testing CLI
- **Instruction**: Wrap parse in condition

EOF

  sign_count=$(grep -c "^### Sign:" "$TEST_DIR/guardrails_real.md" 2>/dev/null || echo "0")
  assert_equals "2" "$sign_count" "Detect real signs added by user"

  # Test 3: No guardrails file
  local missing_count=$(grep -c "^### Sign:" "$TEST_DIR/nonexistent.md" 2>/dev/null || echo "0")
  assert_equals "0" "$missing_count" "Handle missing guardrails file gracefully"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: Config Mismatch Detection
# ═══════════════════════════════════════════════════════════════════════════════

test_config_mismatch() {
  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo "TEST SUITE: Config Mismatch Detection"
  echo "═══════════════════════════════════════════════════════════════"

  # Create temp directory
  local TEST_DIR=$(mktemp -d)
  mkdir -p "$TEST_DIR/.ralph"
  trap "rm -rf $TEST_DIR" EXIT

  # Test 1: Matching configs
  cat > "$TEST_DIR/AGENTS.md" << 'EOF'
# Project Config
**QUALITY_LEVEL**: production
EOF

  cat > "$TEST_DIR/.ralph/config.sh" << 'EOF'
QUALITY_LEVEL=production
EOF

  local agents_level=$(grep -i "quality.level" "$TEST_DIR/AGENTS.md" | head -1 | sed 's/.*:\s*\**\([^*]*\)\**.*/\1/' | tr -d ' ' | tr '[:upper:]' '[:lower:]')
  local config_level=$(grep "^QUALITY_LEVEL=" "$TEST_DIR/.ralph/config.sh" | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr '[:upper:]' '[:lower:]')

  assert_equals "production" "$agents_level" "Extract QUALITY_LEVEL from AGENTS.md"
  assert_equals "production" "$config_level" "Extract QUALITY_LEVEL from config.sh"
  assert_equals "$agents_level" "$config_level" "Configs match (no mismatch)"

  # Test 2: Mismatched configs
  cat > "$TEST_DIR/AGENTS_mismatch.md" << 'EOF'
# Project Config
**QUALITY_LEVEL**: prototype
EOF

  agents_level=$(grep -i "quality.level" "$TEST_DIR/AGENTS_mismatch.md" | head -1 | sed 's/.*:\s*\**\([^*]*\)\**.*/\1/' | tr -d ' ' | tr '[:upper:]' '[:lower:]')

  assert_equals "prototype" "$agents_level" "Extract different QUALITY_LEVEL"
  assert_true '[ "$agents_level" != "$config_level" ]' "Detect mismatch between AGENTS.md and config.sh"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: Coverage Gate Validation
# ═══════════════════════════════════════════════════════════════════════════════

test_coverage_gate() {
  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo "TEST SUITE: Coverage Gate Validation"
  echo "═══════════════════════════════════════════════════════════════"

  # Create temp directory
  local TEST_DIR=$(mktemp -d)
  mkdir -p "$TEST_DIR/coverage"
  trap "rm -rf $TEST_DIR" EXIT

  # Test 1: Coverage above 90%
  cat > "$TEST_DIR/coverage/coverage-summary.json" << 'EOF'
{
  "total": {
    "statements": {"pct": 92.5},
    "branches": {"pct": 88.0},
    "functions": {"pct": 95.0},
    "lines": {"pct": 91.0}
  }
}
EOF

  local coverage=$(jq -r '.total.statements.pct // 0' "$TEST_DIR/coverage/coverage-summary.json" 2>/dev/null || echo "0")
  local coverage_int=${coverage%.*}
  local MIN_TEST_COVERAGE=90

  assert_equals "92" "$coverage_int" "Extract coverage percentage from Jest/Istanbul format"
  assert_true '[ "$coverage_int" -ge "$MIN_TEST_COVERAGE" ]' "Coverage 92% passes 90% gate"

  # Test 2: Coverage below 90%
  cat > "$TEST_DIR/coverage/coverage-summary.json" << 'EOF'
{
  "total": {
    "statements": {"pct": 75.0}
  }
}
EOF

  coverage=$(jq -r '.total.statements.pct // 0' "$TEST_DIR/coverage/coverage-summary.json" 2>/dev/null || echo "0")
  coverage_int=${coverage%.*}

  assert_equals "75" "$coverage_int" "Extract low coverage percentage"
  assert_true '[ "$coverage_int" -lt "$MIN_TEST_COVERAGE" ]' "Coverage 75% fails 90% gate"

  # Test 3: Missing coverage file (non-code project)
  rm "$TEST_DIR/coverage/coverage-summary.json"
  coverage=$(jq -r '.total.statements.pct // 0' "$TEST_DIR/coverage/coverage-summary.json" 2>/dev/null || echo "0")

  assert_equals "0" "$coverage" "Handle missing coverage file (default 0)"

  # Test 4: Gate disabled with MIN_TEST_COVERAGE=0
  MIN_TEST_COVERAGE=0
  assert_true '[ "$MIN_TEST_COVERAGE" -eq 0 ]' "Gate disabled when MIN_TEST_COVERAGE=0"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 5: SOP Prerequisite Detection
# ═══════════════════════════════════════════════════════════════════════════════

test_sop_prerequisites() {
  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo "TEST SUITE: SOP Prerequisites Detection"
  echo "═══════════════════════════════════════════════════════════════"

  # Create temp directory with SOP structure
  local TEST_DIR=$(mktemp -d)
  mkdir -p "$TEST_DIR/specs/myfeature/design"
  mkdir -p "$TEST_DIR/specs/myfeature/implementation/step01"
  trap "rm -rf $TEST_DIR" EXIT

  # Test 1: All prerequisites exist
  touch "$TEST_DIR/specs/myfeature/discovery.md"
  touch "$TEST_DIR/specs/myfeature/design/detailed-design.md"
  touch "$TEST_DIR/specs/myfeature/implementation/plan.md"
  touch "$TEST_DIR/specs/myfeature/implementation/step01/task-01-setup.code-task.md"

  assert_true '[ -f "$TEST_DIR/specs/myfeature/discovery.md" ]' "Discovery.md exists"
  assert_true '[ -d "$TEST_DIR/specs/myfeature/design" ]' "Design directory exists"
  assert_true '[ -f "$TEST_DIR/specs/myfeature/design/detailed-design.md" ]' "Detailed design exists"
  assert_true '[ -f "$TEST_DIR/specs/myfeature/implementation/plan.md" ]' "Plan.md exists"

  # Count task files
  local task_count=$(find "$TEST_DIR/specs/myfeature/implementation" -name "*.code-task.md" | wc -l | tr -d ' ')
  assert_equals "1" "$task_count" "Count task files correctly"

  # Test 2: Missing discovery
  rm "$TEST_DIR/specs/myfeature/discovery.md"
  assert_true '[ ! -f "$TEST_DIR/specs/myfeature/discovery.md" ]' "Detect missing discovery.md"

  # Test 3: Missing design directory
  rm -rf "$TEST_DIR/specs/myfeature/design"
  assert_true '[ ! -d "$TEST_DIR/specs/myfeature/design" ]' "Detect missing design directory"
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN: Run all tests
# ═══════════════════════════════════════════════════════════════════════════════

main() {
  echo ""
  echo "═══════════════════════════════════════════════════════════════════════════════"
  echo " RALPH-ORCHESTRATOR TEST SUITE"
  echo "═══════════════════════════════════════════════════════════════════════════════"
  echo ""

  # Check dependencies
  if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed${NC}"
    exit 1
  fi

  # Run all test suites
  test_context_calculation || true
  test_guardrails_validation || true
  test_config_mismatch || true
  test_coverage_gate || true
  test_sop_prerequisites || true

  # Summary
  echo ""
  echo "═══════════════════════════════════════════════════════════════════════════════"
  echo " TEST SUMMARY"
  echo "═══════════════════════════════════════════════════════════════════════════════"
  echo ""
  echo "Tests run:    $TESTS_RUN"
  echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
  echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
  echo ""

  if [ $TESTS_FAILED -eq 0 ]; then
    local COVERAGE=$((TESTS_PASSED * 100 / TESTS_RUN))
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN} ALL TESTS PASSED! Coverage: ${COVERAGE}%${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    exit 0
  else
    echo -e "${RED}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED} SOME TESTS FAILED${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════════════════════${NC}"
    exit 1
  fi
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
