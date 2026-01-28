# Claude Code Documentation Map

## Overview

This reference provides a map to official Claude Code documentation. Use this to locate and verify current syntax for all component types.

**Source**: https://docs.claude.com/en/docs/claude-code/

---

## Core Documentation

**Constraints:**
- You MUST consult official documentation before implementing because stale training data causes errors
- You SHOULD use WebFetch to verify current syntax because documentation evolves

| Topic            | URL                                                          |
|------------------|--------------------------------------------------------------|
| Overview         | https://docs.claude.com/en/docs/claude-code/overview         |
| Quickstart       | https://docs.claude.com/en/docs/claude-code/quickstart       |
| Common Workflows | https://docs.claude.com/en/docs/claude-code/common-workflows |

---

## Components

### Sub-Agents

**Constraints:**
- You MUST verify current syntax before creating agents because YAML fields may change
- You MUST NOT assume training data is current because API evolves

- **Main Guide**: https://docs.claude.com/en/docs/claude-code/sub-agents
- **Use cases**: Specialized AI assistants with isolated context
- **Key fields**: `name`, `description`, `tools` (optional), `model` (optional)

### Slash Commands

**Constraints:**
- You MUST verify current syntax before creating commands because fields may change
- You SHOULD check allowed-tools patterns because syntax is specific

- **Main Guide**: https://docs.claude.com/en/docs/claude-code/slash-commands
- **Use cases**: User-invoked workflows with parameters
- **Key fields**: `description` (optional), `argument-hint` (optional), `allowed-tools` (optional)

### Agent Skills

**Constraints:**
- You MUST verify current syntax before creating skills because this is a newer feature
- You MUST include required fields because skills fail without them

- **Main Guide**: https://docs.claude.com/en/docs/claude-code/skills
- **Use cases**: Model-invoked capabilities that auto-activate
- **Key fields**: `name` (required), `description` (required), `allowed-tools` (optional)

### Hooks

**Constraints:**
- You MUST verify event types and JSON schema because hooks are sensitive to format
- You MUST use correct configuration file location because wrong path prevents loading

- **Main Guide**: https://docs.claude.com/en/docs/claude-code/hooks
- **Use cases**: Event handlers for lifecycle control
- **Configuration**: `~/.claude/settings.json` or `.claude/settings.json`
- **Events**: SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, Stop, Notification

### MCP (Model Context Protocol)

**Constraints:**
- You MUST verify transport types because SSE is deprecated
- You MUST use environment variables for secrets because hardcoded credentials are a security risk

- **Main Guide**: https://docs.claude.com/en/docs/claude-code/mcp
- **Use cases**: External tool integrations (databases, APIs, services)
- **Configuration**: `.mcp.json`
- **Transports**: http (recommended), stdio, sse (deprecated)

---

## Plugins

**Constraints:**
- You MUST verify plugin structure before creating because format may change
- You SHOULD follow plugin metadata requirements because incomplete plugins fail to load

| Topic            | URL                                                                  |
|------------------|----------------------------------------------------------------------|
| Plugin Structure | https://docs.claude.com/en/docs/claude-code/plugins                  |
| Creating Plugins | https://docs.claude.com/en/docs/claude-code/plugins#creating-plugins |
| Plugin Metadata  | https://docs.claude.com/en/docs/claude-code/plugins#plugin-metadata  |

---

## Reference

**Constraints:**
- You SHOULD consult CLI reference for command syntax because CLI flags change
- You SHOULD consult settings reference for configuration options because options evolve

| Topic            | URL                                                          |
|------------------|--------------------------------------------------------------|
| CLI Reference    | https://docs.claude.com/en/docs/claude-code/cli-reference    |
| Interactive Mode | https://docs.claude.com/en/docs/claude-code/interactive-mode |
| Settings         | https://docs.claude.com/en/docs/claude-code/settings         |

---

## How to Use This Map

**Constraints:**
- You MUST identify component type first because each type has different documentation
- You MUST use WebFetch to extract exact syntax because training data is stale
- You MUST apply ai-framework patterns after extracting syntax because project has additional conventions

**Workflow:**
1. Identify component type (agent, command, hook, MCP, skill)
2. WebFetch the corresponding URL from this map
3. Extract exact syntax (YAML frontmatter, configuration format)
4. Apply to implementation with ai-framework patterns

---

## Update Protocol

**Constraints:**
- You SHOULD verify URLs still resolve before using because docs may move
- You MUST update URLs if docs moved because broken links cause confusion
- You SHOULD add new component types if introduced because coverage should be complete

**When to update:**
- When Claude Code releases new documentation
- When syntax errors occur (indicates stale map)
- Quarterly maintenance check

**Maintenance frequency**: Check quarterly or when syntax errors occur.

---

## Troubleshooting

### URL Returns 404

If documentation URL is broken:
- You SHOULD search docs.claude.com for the topic
- You SHOULD update this map with new URL
- You MUST NOT use stale syntax from training data

### Syntax Doesn't Match

If implementation fails with syntax errors:
- You SHOULD re-fetch documentation to verify current syntax
- You SHOULD compare with working examples in project
- You MUST update this map if documentation changed

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
