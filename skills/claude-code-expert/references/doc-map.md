# Claude Code Documentation Map

**Last Updated**: 2025-10-24
**Source**: https://docs.claude.com/en/docs/claude-code/

## Core Documentation

| Topic            | URL                                                          |
| ---------------- | ------------------------------------------------------------ |
| Overview         | https://docs.claude.com/en/docs/claude-code/overview         |
| Quickstart       | https://docs.claude.com/en/docs/claude-code/quickstart       |
| Common Workflows | https://docs.claude.com/en/docs/claude-code/common-workflows |

## Components

### Sub-Agents

- **Main Guide**: https://docs.claude.com/en/docs/claude-code/sub-agents
- **Use cases**: Specialized AI assistants with isolated context
- **Key fields**: `name`, `description`, `tools` (optional), `model` (optional)

### Slash Commands

- **Main Guide**: https://docs.claude.com/en/docs/claude-code/slash-commands
- **Use cases**: User-invoked workflows with parameters
- **Key fields**: `description` (optional), `argument-hint` (optional), `allowed-tools` (optional)

### Agent Skills

- **Main Guide**: https://docs.claude.com/en/docs/claude-code/skills
- **Use cases**: Model-invoked capabilities that auto-activate
- **Key fields**: `name` (required), `description` (required), `allowed-tools` (optional)

### Hooks

- **Main Guide**: https://docs.claude.com/en/docs/claude-code/hooks
- **Use cases**: Event handlers for lifecycle control
- **Configuration**: `~/.claude/settings.json` or `.claude/settings.json`
- **Events**: SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, Stop, Notification

### MCP (Model Context Protocol)

- **Main Guide**: https://docs.claude.com/en/docs/claude-code/mcp
- **Use cases**: External tool integrations (databases, APIs, services)
- **Configuration**: `.mcp.json`
- **Transports**: http (recommended), stdio, sse (deprecated)

## Plugins

| Topic            | URL                                                                  |
| ---------------- | -------------------------------------------------------------------- |
| Plugin Structure | https://docs.claude.com/en/docs/claude-code/plugins                  |
| Creating Plugins | https://docs.claude.com/en/docs/claude-code/plugins#creating-plugins |
| Plugin Metadata  | https://docs.claude.com/en/docs/claude-code/plugins#plugin-metadata  |

## Reference

| Topic            | URL                                                          |
| ---------------- | ------------------------------------------------------------ |
| CLI Reference    | https://docs.claude.com/en/docs/claude-code/cli-reference    |
| Interactive Mode | https://docs.claude.com/en/docs/claude-code/interactive-mode |
| Settings         | https://docs.claude.com/en/docs/claude-code/settings         |

## How to Use This Map

1. **Identify component type** (agent, command, hook, MCP, skill)
2. **WebFetch the corresponding URL** from this map
3. **Extract exact syntax** (YAML frontmatter, configuration format)
4. **Apply to implementation** with ai-framework patterns

## Update Protocol

When Claude Code releases new documentation:

1. Verify URLs still resolve (test WebFetch)
2. Update URLs if docs moved
3. Add new component types if introduced
4. Update "Last Updated" date

**Maintenance frequency**: Check quarterly or when syntax errors occur.
