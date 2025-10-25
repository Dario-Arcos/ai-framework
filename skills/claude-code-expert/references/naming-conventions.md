# Naming Conventions - Claude Code Components

**Apply consistently across all components.**

---

## Sub-Agents

**Format**: `snake-case` (lowercase, hyphens)

**Pattern**: `<domain>-<specialty>-<type>`

**Examples**:

- ✅ `code-quality-reviewer`
- ✅ `python-pro`
- ✅ `backend-architect`
- ❌ `CodeQualityReviewer` (CamelCase not allowed)
- ❌ `code_quality_reviewer` (underscores not allowed)

**Max length**: 64 characters

**File**: `agents/[Category]/[agent-name].md`

---

## Slash Commands

**Format**: `kebab-case` with category prefix

**Pattern**: `<category>.<command-name>` or `<command-name>`

**Examples**:

- ✅ `speckit.plan`
- ✅ `speckit.implement`
- ✅ `three-experts`
- ✅ `understand`
- ❌ `speckit_plan` (underscores not allowed)
- ❌ `SpecKit.Plan` (CamelCase not allowed)

**File**: `commands/[category]/[command-name].md`

**Categories**:

- `SDD-cycle/` → `speckit.*`
- `git-github/` → git operations
- `utils/` → general utilities
- `PRP-cycle/` → product requirements

---

## Hooks

**Format**: `snake_case` (lowercase, underscores) + `.py`

**Pattern**: `<event>_<purpose>.py`

**Examples**:

- ✅ `session_start.py`
- ✅ `security_guard.py`
- ✅ `minimal_thinking.py`
- ❌ `session-start.py` (hyphens not allowed)
- ❌ `sessionStart.py` (camelCase not allowed)

**File**: `hooks/[hook-name].py`

**Executable**: `chmod +x` required

---

## MCP Servers

**Format**: `kebab-case` (lowercase, hyphens)

**Pattern**: `<service-name>` or `<vendor-service>`

**Examples**:

- ✅ `playwright`
- ✅ `shadcn`
- ✅ `notion`
- ✅ `github-api`
- ❌ `Playwright` (uppercase not allowed)
- ❌ `notion_api` (underscores not allowed)

**Config**: `.claude/.mcp.json` → `mcpServers` object key

---

## Agent Skills

**Format**: `kebab-case` (lowercase, hyphens)

**Pattern**: `<domain>-<specialty>`

**Examples**:

- ✅ `claude-code-expert`
- ✅ `pdf-editor`
- ✅ `web-search-specialist`
- ❌ `ClaudeCodeExpert` (CamelCase not allowed)
- ❌ `claude_code_expert` (underscores not allowed)

**Max length**: 64 characters

**File**: `skills/[skill-name]/SKILL.md`

---

## Variables & Identifiers

### Bash (in Commands)

**Variables**: `snake_case`

**Examples**:

```bash
target_branch="main"
commit_count=$(git rev-list --count HEAD)
has_security_critical=false
```

### Python (in Hooks)

**Variables**: `snake_case`
**Functions**: `snake_case`
**Constants**: `UPPER_SNAKE_CASE`

**Examples**:

```python
hook_event_name = "PreToolUse"
def validate_input(data):
    pass
MAX_TIMEOUT = 60
```

### JSON/YAML (Config)

**Keys**: `camelCase` or `kebab-case` (depend on spec)

**MCP**: `camelCase` (official spec)

```json
{
  "mcpServers": {},
  "environmentVariables": {}
}
```

**Hooks**: `snake_case` (convention)

```json
{
  "hook_event_name": "SessionStart"
}
```

---

## Summary Table

| Component    | Convention      | Example                 | Max Length |
| ------------ | --------------- | ----------------------- | ---------- |
| Sub-agents   | `snake-case`    | `code-quality-reviewer` | 64 chars   |
| Commands     | `kebab-case`    | `speckit.plan`          | -          |
| Hooks        | `snake_case.py` | `session_start.py`      | -          |
| MCP servers  | `kebab-case`    | `playwright`            | -          |
| Skills       | `kebab-case`    | `claude-code-expert`    | 64 chars   |
| Bash vars    | `snake_case`    | `target_branch`         | -          |
| Python vars  | `snake_case`    | `hook_event`            | -          |
| Python const | `UPPER_SNAKE`   | `MAX_TIMEOUT`           | -          |

---

**Version**: 1.0.0
