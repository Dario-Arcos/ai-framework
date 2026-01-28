# Naming Conventions Reference

## Overview

This reference defines naming conventions for Claude Code components. Apply these constraints consistently across all components to ensure discoverability and maintainability.

---

## Sub-Agents

**Format**: `kebab-case` (lowercase, hyphens)

**Pattern**: `<domain>-<specialty>` or `<domain>-<specialty>-<type>`

**Constraints:**
- You MUST use lowercase letters only because uppercase causes loading issues
- You MUST use hyphens as separators because underscores and camelCase are not allowed
- You MUST NOT exceed 64 characters because this is the max length
- You MUST place file at `agents/[Category]/[agent-name].md` because this enables discovery

**Examples:**
- `code-reviewer`
- `backend-architect`
- `security-reviewer`
- `CodeQualityReviewer` (PROHIBITED - CamelCase)
- `code_quality_reviewer` (PROHIBITED - underscores)

---

## Slash Commands

**Format**: `kebab-case` with category prefix

**Pattern**: `<category>-<command-name>` or `<command-name>`

**Constraints:**
- You MUST use lowercase letters only because uppercase causes loading issues
- You MUST use hyphens as separators because underscores and camelCase are not allowed
- You MUST place file at `commands/[category]/[command-name].md` because this enables discovery
- You MUST use established categories (git-github, utils, PRP-cycle) because this organizes commands

**Examples:**
- `git-commit`
- `git-pullrequest`
- `three-experts`
- `understand`
- `git_commit` (PROHIBITED - underscores)
- `GitCommit` (PROHIBITED - CamelCase)

---

## Hooks

**Format**: `snake_case` (lowercase, underscores) + `.py`

**Pattern**: `<event>_<purpose>.py`

**Constraints:**
- You MUST use lowercase letters only because uppercase causes loading issues
- You MUST use underscores as separators because this is Python convention
- You MUST NOT use hyphens because they are invalid in Python identifiers
- You MUST place file at `hooks/[hook-name].py` because this enables discovery
- You MUST make file executable (`chmod +x`) because non-executable hooks fail

**Examples:**
- `session_start.py`
- `security_guard.py`
- `minimal_thinking.py`
- `session-start.py` (PROHIBITED - hyphens)
- `sessionStart.py` (PROHIBITED - camelCase)

---

## MCP Servers

**Format**: `kebab-case` (lowercase, hyphens)

**Pattern**: `<service-name>` or `<vendor-service>`

**Constraints:**
- You MUST use lowercase letters only because uppercase causes loading issues
- You MUST use hyphens as separators because underscores are not allowed
- You MUST use unique server name in `mcpServers` object because duplicates cause conflicts

**Configuration**: `.claude/.mcp.json` → `mcpServers` object key

**Examples:**
- `playwright`
- `shadcn`
- `notion`
- `github-api`
- `Playwright` (PROHIBITED - uppercase)
- `notion_api` (PROHIBITED - underscores)

---

## Agent Skills

**Format**: `kebab-case` (lowercase, hyphens)

**Pattern**: `<domain>-<specialty>`

**Constraints:**
- You MUST use lowercase letters only because uppercase causes loading issues
- You MUST use hyphens as separators because underscores and camelCase are not allowed
- You MUST NOT exceed 64 characters because this is the max length
- You MUST place file at `skills/[skill-name]/SKILL.md` because this enables discovery

**Examples:**
- `claude-code-expert`
- `algorithmic-art`
- `skill-creator`
- `ClaudeCodeExpert` (PROHIBITED - CamelCase)
- `claude_code_expert` (PROHIBITED - underscores)

---

## Variables & Identifiers

### Bash (in Commands)

**Constraints:**
- You MUST use `snake_case` for variables because this is the Bash convention

**Examples:**
```bash
target_branch="main"
commit_count=$(git rev-list --count HEAD)
has_security_critical=false
```

### Python (in Hooks)

**Constraints:**
- You MUST use `snake_case` for variables because this is PEP 8
- You MUST use `snake_case` for functions because this is PEP 8
- You MUST use `UPPER_SNAKE_CASE` for constants because this is PEP 8

**Examples:**
```python
hook_event_name = "PreToolUse"
def validate_input(data):
    pass
MAX_TIMEOUT = 60
```

### JSON/YAML (Config)

**Constraints:**
- You MUST use `camelCase` for MCP configuration because this is the official spec
- You SHOULD use `snake_case` for hooks configuration because this is the convention

**Examples:**
```json
{
  "mcpServers": {},
  "environmentVariables": {}
}
```

---

## Summary Table

| Component    | Convention      | Example              | Max Length |
|--------------|-----------------|----------------------|------------|
| Sub-agents   | `kebab-case`    | `code-reviewer`      | 64 chars   |
| Commands     | `kebab-case`    | `git-commit`         | -          |
| Hooks        | `snake_case.py` | `session_start.py`   | -          |
| MCP servers  | `kebab-case`    | `playwright`         | -          |
| Skills       | `kebab-case`    | `claude-code-expert` | 64 chars   |
| Bash vars    | `snake_case`    | `target_branch`      | -          |
| Python vars  | `snake_case`    | `hook_event`         | -          |
| Python const | `UPPER_SNAKE`   | `MAX_TIMEOUT`        | -          |

---

## Troubleshooting

### Component Not Loading

If component is not discovered:
- You SHOULD verify naming convention matches component type
- You SHOULD check for uppercase letters (must be lowercase)
- You MUST verify file path matches expected location

### Name Too Long

If name exceeds max length:
- You SHOULD abbreviate domain or specialty
- You MUST NOT use full descriptive names if they exceed 64 characters

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
