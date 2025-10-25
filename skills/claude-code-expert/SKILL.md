---
name: claude-code-expert
description: PROACTIVELY create, modify, update, improve, and fix Claude Code components (sub-agents, slash commands, hooks, MCP integrations). Use when working with Claude Code plugin development or when users mention creating, building, adding, implementing, modifying, updating, improving, fixing, or enhancing commands, agents, hooks, or MCP servers.
---

# Claude Code Expert

Expert-level skill for creating production-ready Claude Code components with 100% consistency to official documentation and ai-framework project patterns.

## Purpose

Generate correct-on-first-attempt code for sub-agents, slash commands, hooks, and MCP integrations.

## Workflow

Before implementing ANY component, follow this protocol:

### Step 1: Identify Component Type

Determine which component the user is requesting:

- **Sub-agent**: "Create an agent for X" → Task tool invocation
- **Slash command**: "Add a command to X" → User-invoked workflow
- **Hook**: "Add a hook to X" → Event handler (SessionStart, PreToolUse, etc.)
- **MCP server**: "Integrate X server" → External tool integration

### Step 2: Official Documentation

**Your training data is stale. APIs change every 3 months. Never assume syntax.**

Load [references/doc-map.md](references/doc-map.md) and WebFetch the official docs for your component type:

```
1. Read references/doc-map.md
2. Get official URL for component type
3. WebFetch docs.claude.com/[component-url]
4. Extract:
   - Exact YAML frontmatter structure
   - Required vs optional fields
   - Field syntax and constraints
   - Official examples
```

### Step 3: Project Patterns

Read existing ai-framework examples to extract patterns:

**For Sub-agents**:
```bash
Read agents/[relevant-category]/[similar-agent].md
```
Extract: naming conventions, tool access patterns, constitutional constraints

**For Slash Commands**:
```bash
Read commands/[relevant-category]/[similar-command].md
```
Extract: argument-hint patterns, allowed-tools restrictions, workflow structure

**For Hooks**:
```bash
Read hooks/[similar-hook].py
Read hooks/hooks.json
```
Extract: error handling patterns, JSON I/O format, exit code conventions

**For MCP**:
```bash
Read .claude/.mcp.json
```
Extract: server configuration patterns, environment variable usage

### Step 4: Generate Component

Merge:

1. **Official syntax** (Step 2 - WebFetch)
2. **Project patterns** (Step 3 - existing code)
3. **Constitutional principles** (@.specify/memory/constitution.md)

Apply these principles:

- **Value/Complexity ≥ 2**: Simplest solution that works
- **Reuse First**: Use existing patterns before creating new ones
- **TDD**: Tests before implementation (if applicable)
- **AI-First**: Text/JSON interfaces for AI executability

### Step 5: Validate

Load the appropriate checklist:

| Component     | Checklist                                                          |
| ------------- | ------------------------------------------------------------------ |
| Sub-agent     | [references/agent-checklist.md](references/agent-checklist.md)     |
| Slash command | [references/command-checklist.md](references/command-checklist.md) |
| Hook          | [references/hook-checklist.md](references/hook-checklist.md)       |
| MCP server    | [references/mcp-checklist.md](references/mcp-checklist.md)         |

Execute validation:

1. **Run automated validators**: `scripts/validate_bash_blocks.py`, `scripts/validate_tool_invocations.py`, `scripts/validate_[type].py`
2. **Manual review against checklist** (semantic/logic)
3. **Execute Step 6** (Logic Review)
4. Confirm 100% correctness

**Only deliver when all gates passed.**

### Step 6: Logic Review

Load [references/logic-anti-patterns.md](references/logic-anti-patterns.md) and verify all applicable patterns before delivery.

## Component Reference

| Component | Key Patterns |
|-----------|--------------|
| **Sub-agent** | tools comma-separated (e.g., `Read, Grep, Glob, Bash`); model: `sonnet`, `opus`, `haiku`, `inherit`; include "PROACTIVELY" in description for auto-delegation; limit tools to necessary minimum (security) |
| **Command** | `allowed-tools:` restricts tool access (security); `argument-hint:` guides user input; bash execution: exclamation prefix before backticks; file references: at-sign prefix before paths |
| **Hook** | No external dependencies (stdlib only); Spanish error messages (user-facing); JSON stdin/stdout; exit codes: 0=success, 2=block, other=non-blocking error; absolute paths using `$CLAUDE_PROJECT_DIR` |
| **MCP** | Use `project` scope for team-shared tools; store secrets in env vars, not hardcoded; environment variable expansion: `${VAR_NAME:-default}`; HTTP servers for remote services; stdio servers for local processes |

See [references/doc-map.md](references/doc-map.md) for official documentation URLs.

## Standards

**Naming Conventions**:
- **Sub-agents**: `snake-case` (e.g., `code-quality-reviewer`)
- **Commands**: `kebab-case` with category prefix (e.g., `speckit.plan`)
- **Hooks**: `snake_case` with descriptive suffix (e.g., `session_start.py`)
- **MCP servers**: `kebab-case` (e.g., `playwright`, `shadcn`)

**Documentation Language**:
- **Code & AI instructions**: English
- **User-facing messages**: Spanish
- **Technical terms**: English (even in Spanish docs)

**Common Pitfalls**:
- ❌ Assuming syntax from training → Always WebFetch
- ❌ Creating new patterns → Reuse existing unless justified
- ❌ Over-engineering → Simplest solution wins
- ❌ Skipping validation → Checklist required
- ❌ Mixing languages → English for code, Spanish for users
- ❌ Hardcoding secrets → Use env vars
- ❌ Adding external deps → Stdlib only (hooks/scripts)

## Deliverables

For each component, provide:
1. Component file(s) (agent.md, command.md, hook.py, .mcp.json entry)
2. Validation report confirming checklist passed
3. Integration instructions (file path, test commands)
