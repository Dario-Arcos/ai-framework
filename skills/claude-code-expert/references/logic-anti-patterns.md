# Logic Anti-Patterns Reference

## Overview

This reference defines logic anti-patterns for Claude Code components. Use this as a knowledge base for AI self-review to detect logic errors in commands, agents, hooks, and MCP integrations before delivery.

**Usage**: Read this file before generating components to activate pattern detection.

---

## Commands: Bash Flow Issues

### AP-001: Variable Used Before Definition

**Constraints:**
- You MUST define variables before use because undefined variables produce empty output
- You MUST NOT reference variables before assignment because this causes silent failures

**Bad:**
```bash
echo "Result: $result"
result=$(compute_something)
```

**Good:**
```bash
result=$(compute_something)
echo "Result: $result"
```

---

### AP-002: Missing Error Cleanup

**Constraints:**
- You MUST cleanup temporary state in ALL exit paths because error paths often forget cleanup
- You MUST NOT exit without cleaning up because state pollution affects subsequent operations

**Bad:**
```bash
git config --local temp.value "$data"
if [ $? -ne 0 ]; then
  exit 1  # State leak!
fi
```

**Good:**
```bash
git config --local temp.value "$data"
if [ $? -ne 0 ]; then
  git config --local --remove-section temp 2>/dev/null
  exit 1
fi
```

---

### AP-003: Unquoted Variable Expansion

**Constraints:**
- You MUST quote all variables in commands because unquoted variables enable injection attacks
- You MUST NOT use `$var` without quotes because word splitting and glob expansion occur

**Bad:**
```bash
branch=$user_input
git checkout $branch  # Command injection!
```

**Good:**
```bash
branch=$user_input
git checkout "$branch"
```

---

### AP-004: Heredoc Without Quote Protection

**Constraints:**
- You MUST use quoted heredoc delimiter when no expansion is needed because unquoted expands variables
- You MUST NOT use unquoted heredoc for literal content because this creates security risks

**Bad:**
```bash
cat > file <<EOF
User data: $user_input  # Expands even if not intended!
EOF
```

**Good:**
```bash
cat > file <<'EOF'
User data: $user_input  # Literal $user_input
EOF
```

---

### AP-005: Incomplete Conditional Blocks

**Constraints:**
- You MUST close all conditional blocks (if/fi, case/esac) because missing closures cause syntax errors
- You MUST NOT leave blocks unclosed because the script will fail to execute

**Bad:**
```bash
if [ "$condition" = "true" ]; then
  do_something
# Missing fi!
```

**Good:**
```bash
if [ "$condition" = "true" ]; then
  do_something
fi
```

---

### AP-006: Inconsistent State Management

**Constraints:**
- You MUST cleanup state in trap or ALL exit paths because partial cleanup causes pollution
- You SHOULD use trap for cleanup because it handles unexpected exits

**Bad:**
```bash
git config --local state.value "$data"
git config --local --remove-section state  # Success only!
# Error path forgets cleanup!
```

**Good:**
```bash
cleanup() {
  git config --local --remove-section state 2>/dev/null || true
}
trap cleanup EXIT

git config --local state.value "$data"
```

---

## Commands: Tool Invocation Issues

### AP-007: Tool Invocation Before Context Load

**Constraints:**
- You MUST load context before invoking Task tools because agents need context to produce quality output
- You MUST NOT invoke agents before reading specifications because output will be generic

**Bad:**
```markdown
## Step 1
Task: backend-architect analyzing feature

## Step 2
Read specification.md
```

**Good:**
```markdown
## Step 1
Read specification.md
Read @.specify/memory/constitution.md

## Step 2
Task: backend-architect analyzing feature with loaded context
```

---

### AP-008: Parallel Tasks with Sequential Dependencies

**Constraints:**
- You MUST NOT invoke dependent tasks in parallel because race conditions occur
- You MUST use sequential invocation when output of one task is input to another

**Bad:**
```markdown
# In single message (parallel):
Task: generate-schema # Creates schema.json
Task: validate-schema # Reads schema.json - RACE CONDITION!
```

**Good:**
```markdown
# Option A: Sequential messages
Task: generate-schema
# (wait for completion)
Task: validate-schema

# Option B: Single task
Task: generate and validate schema
```

---

### AP-009: Missing Tool in allowed-tools

**Constraints:**
- You MUST include all used tools in allowed-tools because missing tools cause invocation failures
- You MUST NOT use tools not listed in allowed-tools because access will be denied

**Bad:**
```yaml
---
allowed-tools: Read, Grep
---
# Later in command:
Task: security-reviewer # Task tool not in allowed-tools!
```

**Good:**
```yaml
---
allowed-tools: Read, Grep, Task
---
```

---

## Agents: Instruction Issues

### AP-010: Contradictory Tool Access

**Constraints:**
- You MUST grant tools required by instructions because mismatched access prevents execution
- You MUST NOT write instructions requiring tools not granted because agents cannot complete tasks

**Bad:**
```yaml
---
name: file-analyzer
tools: Read, Grep # Only read access
---
Analyze files and fix issues found. # Requires Edit!
```

**Good:**
```yaml
---
name: file-analyzer
tools: Read, Grep, Edit
---
Analyze files and fix issues found.
```

---

### AP-011: Circular Agent Invocation

**Constraints:**
- You MUST define clear delegation hierarchy because circular calls cause infinite recursion
- You MUST NOT allow upward delegation because loops cause timeouts

**Bad:**
```markdown
# Agent A
Use backend-architect for complex analysis

# Agent backend-architect
For detailed review, use code-reviewer

# Agent code-reviewer
For architecture issues, use backend-architect # LOOP!
```

**Good:**
```markdown
# Define clear levels:
# Level 1: code-reviewer (tactical)
# Level 2: backend-architect (strategic)
# No upward delegation
```

---

## Hooks: I/O Issues

### AP-012: Writing to stdout AND stderr for Normal Flow

**Constraints:**
- You MUST use stdout for data and stderr for errors only because mixing streams causes confusion
- You MUST NOT duplicate output to both streams because semantics become unclear

**Bad:**
```python
sys.stdout.write("Processing...")
sys.stderr.write("Processing...")  # Redundant!
```

**Good:**
```python
sys.stdout.write("Processing...")  # Normal output
# stderr only for actual errors
```

---

### AP-013: Exit Code Doesn't Match Behavior

**Constraints:**
- You MUST return exit code 0 for success because Claude interprets non-zero as failure
- You MUST NOT return error codes when operation succeeds because this triggers error handling

**Bad:**
```python
sys.stdout.write("Success")
sys.exit(1)  # But returns error!
```

**Good:**
```python
sys.stdout.write("Success")
sys.exit(0)  # Success code
```

---

## MCP: Configuration Issues

### AP-014: Hardcoded Secrets in Config

**Constraints:**
- You MUST NOT include hardcoded credentials in config files because they get committed to version control
- You MUST use environment variables for secrets because this keeps them out of code

**Bad:**
```json
{
  "headers": {
    "Authorization": "Bearer abc123def456..."
  }
}
```

**Good:**
```json
{
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

---

### AP-015: Missing Default Values in Env Var Expansion

**Constraints:**
- You SHOULD provide default values for environment variables because missing vars cause config failures
- You MAY omit defaults for truly required secrets because failures should be explicit

**Bad:**
```json
{
  "url": "${API_URL}"
}
```

**Good:**
```json
{
  "url": "${API_URL:-https://api.example.com}"
}
```

---

## Cross-Component Issues

### AP-016: Inconsistent Naming Across Components

**Constraints:**
- You MUST use consistent naming across related components because inconsistency causes confusion
- You SHOULD follow project naming conventions because this aids discovery

**Bad:**
```
Agent: user-authenticator
Command: auth-user
Hook: authenticate_users.py
```

**Good:**
```
Agent: user-auth
Command: user-auth
Hook: user_auth.py
```

---

### AP-017: Duplicate Functionality Without Justification

**Constraints:**
- You MUST reuse existing components when possible because duplication increases maintenance
- You MUST justify new components with ≥30% differentiation because this validates the addition

**Bad:**
```markdown
# New agent: code-analyzer
# (But code-reviewer already exists and does the same!)
```

**Good:**
```markdown
# Use existing code-reviewer
# OR
# Justify: code-analyzer focuses on performance (30% different scope)
```

---

## Anti-Pattern Detection Protocol

**Constraints:**
- You MUST check all applicable anti-patterns before delivery because undetected patterns cause failures
- You MUST NOT deliver components with detected anti-patterns because they will fail in production

**Checklist:**
- [ ] Bash flow: Variables defined before use? (AP-001)
- [ ] Error handling: Cleanup in ALL paths? (AP-002, AP-006)
- [ ] Security: Variables quoted? No hardcoded secrets? (AP-003, AP-014)
- [ ] Tools: Context loaded before Task? No circular deps? (AP-007, AP-011)
- [ ] I/O: Correct streams used? Exit codes match? (AP-012, AP-013)
- [ ] Integration: Naming consistent? No duplication? (AP-016, AP-017)

---

## Troubleshooting

### Pattern Detection Failures

If anti-patterns are missed during review:
- You SHOULD read this file before generating components to activate pattern detection
- You SHOULD re-read after generation to validate no anti-patterns present
- You MUST confirm "zero anti-patterns detected" before delivery

### False Positives

If a pattern is flagged but justified:
- You SHOULD document the justification in code comments
- You MUST get human review approval for exceptions
- You MUST NOT ignore patterns without explicit justification because this defeats the purpose

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
