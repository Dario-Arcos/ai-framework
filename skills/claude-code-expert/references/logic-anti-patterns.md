# Logic Consistency Anti-Patterns

**Purpose**: Knowledge base for AI self-review to detect logic errors in Claude Code components.

**Usage**: Claude reads this file before generating components to activate pattern detection.

---

## Commands: Bash Flow Issues

### ❌ AP-001: Variable Used Before Definition

**Pattern**: Variable referenced before it's assigned a value

**Bad**:

```bash
echo "Result: $result"
result=$(compute_something)
```

**Impact**: Empty output, silent failure, unpredictable behavior

**Fix**: Define before use

```bash
result=$(compute_something)
echo "Result: $result"
```

---

### ❌ AP-002: Missing Error Cleanup

**Pattern**: Error path exits without cleaning up temporary state

**Bad**:

```bash
git config --local temp.value "$data"
# ... some operation
if [ $? -ne 0 ]; then
  exit 1  # State leak!
fi
```

**Impact**: Polluted git config, temp files left behind

**Fix**: Always cleanup in error paths

```bash
git config --local temp.value "$data"
if [ $? -ne 0 ]; then
  git config --local --remove-section temp 2>/dev/null
  exit 1
fi
```

---

### ❌ AP-003: Unquoted Variable Expansion

**Pattern**: Variables used in commands without quotes

**Bad**:

```bash
branch=$user_input
git checkout $branch  # Command injection!
```

**Impact**: Command injection, word splitting, glob expansion

**Fix**: Quote all variables

```bash
branch=$user_input
git checkout "$branch"
```

---

### ❌ AP-004: Heredoc Without Quote Protection

**Pattern**: Heredoc without quotes when no variable expansion needed

**Bad**:

```bash
cat > file <<EOF
User data: $user_input  # Expands even if not intended!
EOF
```

**Impact**: Unintended variable expansion, security risk

**Fix**: Use quoted delimiter if no expansion needed

```bash
cat > file <<'EOF'
User data: $user_input  # Literal $user_input
EOF
```

---

### ❌ AP-005: Incomplete Conditional Blocks

**Pattern**: if/then without closing fi

**Bad**:

```bash
if [ "$condition" = "true" ]; then
  do_something
# Missing fi!
```

**Impact**: Syntax error, script fails

**Fix**: Close all blocks

```bash
if [ "$condition" = "true" ]; then
  do_something
fi
```

---

### ❌ AP-006: Inconsistent State Management

**Pattern**: Using git config for state but not cleaning up in ALL paths

**Bad**:

```bash
git config --local state.value "$data"
# Success path cleans up
git config --local --remove-section state
# Error path forgets cleanup!
```

**Impact**: State pollution across git operations

**Fix**: Cleanup in trap or all exit paths

```bash
cleanup() {
  git config --local --remove-section state 2>/dev/null || true
}
trap cleanup EXIT

git config --local state.value "$data"
```

---

## Commands: Tool Invocation Issues

### ❌ AP-007: Tool Invocation Before Context Load

**Pattern**: Invoking Task tool before loading necessary context

**Bad**:

```markdown
## Step 1

Task: backend-architect analyzing feature

## Step 2

Read specification.md
```

**Impact**: Agent lacks context, produces generic output

**Fix**: Load context first

```markdown
## Step 1

Read specification.md
Read @.specify/memory/constitution.md

## Step 2

Task: backend-architect analyzing feature with loaded context
```

---

### ❌ AP-008: Parallel Tasks with Sequential Dependencies

**Pattern**: Invoking tasks in parallel when they have dependencies

**Bad**:

```markdown
# In single message (parallel):

Task: generate-schema # Creates schema.json
Task: validate-schema # Reads schema.json - RACE CONDITION!
```

**Impact**: Second task may run before first completes

**Fix**: Sequential invocation or single task

```markdown
# Option A: Sequential messages

Task: generate-schema

# (wait for completion)

Task: validate-schema

# Option B: Single task

Task: generate and validate schema
```

---

### ❌ AP-009: Missing Tool in allowed-tools

**Pattern**: Command uses tool not listed in allowed-tools

**Bad**:

```yaml
---
allowed-tools: Read, Grep
---
# Later in command:
Task: security-reviewer # Task tool not in allowed-tools!
```

**Impact**: Tool invocation fails

**Fix**: Include all tools used

```yaml
---
allowed-tools: Read, Grep, Task
---
```

---

## Agents: Instruction Issues

### ❌ AP-010: Contradictory Tool Access

**Pattern**: Agent instructions require tools not granted

**Bad**:

```yaml
---
name: file-analyzer
tools: Read, Grep # Only read access
---
Analyze files and fix issues found. # Requires Edit!
```

**Impact**: Agent can detect but not fix

**Fix**: Grant necessary tools or adjust scope

```yaml
---
name: file-analyzer
tools: Read, Grep, Edit
---
Analyze files and fix issues found.
```

---

### ❌ AP-011: Circular Agent Invocation

**Pattern**: Agent A calls Agent B which calls Agent A

**Bad**:

```markdown
# Agent A

Use backend-architect for complex analysis

# Agent backend-architect

For detailed review, use code-reviewer

# Agent code-reviewer

For architecture issues, use backend-architect # LOOP!
```

**Impact**: Infinite recursion, timeout

**Fix**: Clear delegation hierarchy

```markdown
# Define clear levels:

# Level 1: code-reviewer (tactical)

# Level 2: backend-architect (strategic)

# No upward delegation
```

---

## Hooks: I/O Issues

### ❌ AP-012: Writing to stdout AND stderr for Normal Flow

**Pattern**: Hook writes normal output to both streams

**Bad**:

```python
sys.stdout.write("Processing...")
sys.stderr.write("Processing...")  # Redundant!
```

**Impact**: Duplicate messages, unclear semantics

**Fix**: stdout for data, stderr for errors only

```python
sys.stdout.write("Processing...")  # Normal output
# stderr only for actual errors
```

---

### ❌ AP-013: Exit Code Doesn't Match Behavior

**Pattern**: Hook succeeds but returns error code

**Bad**:

```python
# Everything OK
sys.stdout.write("Success")
sys.exit(1)  # But returns error!
```

**Impact**: Claude interprets as failure

**Fix**: Match exit code to outcome

```python
sys.stdout.write("Success")
sys.exit(0)  # Success code
```

---

## MCP: Configuration Issues

### ❌ AP-014: Hardcoded Secrets in Config

**Pattern**: API keys directly in mcp.json

**Bad**:

```json
{
  "mcpServers": {
    "api": {
      "type": "http",
      "url": "https://api.example.com",
      "headers": {
        "Authorization": "Bearer abc123def456..."  # Hardcoded!
      }
    }
  }
}
```

**Impact**: Secrets in version control, security risk

**Fix**: Use environment variables

```json
{
  "mcpServers": {
    "api": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}",
      "headers": {
        "Authorization": "Bearer ${API_TOKEN}"
      }
    }
  }
}
```

---

### ❌ AP-015: Missing Default Values in Env Var Expansion

**Pattern**: Required env var without fallback

**Bad**:

```json
{
  "url": "${API_URL}"  # Fails if not set!
}
```

**Impact**: Config breaks if env var missing

**Fix**: Provide defaults

```json
{
  "url": "${API_URL:-https://api.example.com}"
}
```

---

## Cross-Component Issues

### ❌ AP-016: Inconsistent Naming Across Components

**Pattern**: Same concept with different names

**Bad**:

```
Agent: user-authenticator
Command: auth-user
Hook: authenticate_users.py
```

**Impact**: Discovery confusion, maintenance overhead

**Fix**: Consistent naming

```
Agent: user-auth
Command: user-auth
Hook: user_auth.py
```

---

### ❌ AP-017: Duplicate Functionality Without Justification

**Pattern**: Creating new component that duplicates existing

**Bad**:

```markdown
# New agent: code-analyzer

# (But code-reviewer already exists and does the same!)
```

**Impact**: Violates "Reuse First" principle, maintenance burden

**Fix**: Reuse or justify ≥30% differentiation

```markdown
# Use existing code-reviewer

# OR

# Justify: code-analyzer focuses on performance (30% different scope)
```

---

## How to Use This Knowledge Base

**For Claude (AI Self-Review)**:

1. **Before generating component**: Read this file
2. **During generation**: Check patterns against anti-patterns
3. **After generation**: Re-read and validate no anti-patterns present
4. **Before delivery**: Confirm "zero anti-patterns detected"

**For Humans (Manual Review)**:

1. Use as checklist during code review
2. Reference anti-pattern number in feedback (e.g., "AP-003 detected")
3. Link to this doc in PR comments

---

## Anti-Pattern Detection Protocol

When reviewing a component, ask:

- [ ] **Bash flow**: Variables defined before use? (AP-001)
- [ ] **Error handling**: Cleanup in ALL paths? (AP-002, AP-006)
- [ ] **Security**: Variables quoted? No hardcoded secrets? (AP-003, AP-014)
- [ ] **Tools**: Context loaded before Task? No circular deps? (AP-007, AP-011)
- [ ] **I/O**: Correct streams used? Exit codes match? (AP-012, AP-013)
- [ ] **Integration**: Naming consistent? No duplication? (AP-016, AP-017)

**If ANY anti-pattern detected → FIX before delivery**

---

**Version**: 1.0.0 (17 anti-patterns documented)
**Last Updated**: 2025-10-24
