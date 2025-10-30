# Claude Code Expert Skill

Production-ready Claude Code components with 100% consistency to official docs and ai-framework patterns.

## What This Does

Generates correct-on-first-attempt code for:
- **Sub-agents** (specialized AI assistants)
- **Slash commands** (user-invoked workflows)
- **Hooks** (event handlers for lifecycle control)
- **MCP integrations** (Model Context Protocol servers)

## Key Feature

**WebFetch Mandatory Protocol**: Always verifies current official syntax before implementation. Never assumes syntax from training data.

## Usage

Activates automatically when users request Claude Code components:

```
"Create a sub-agent for code review"
"Add a command to generate changelogs"
"Implement a hook for security validation"
"Integrate Playwright MCP server"
```

No explicit invocation needed.

## Validation

Test validators against real components:

```bash
# Validate specific component type
python3 scripts/validate_agent.py agents/category/agent.md
python3 scripts/validate_command.py commands/category/command.md
python3 scripts/validate_hook.py hooks/hook.py hooks/hooks.json
python3 scripts/validate_mcp.py .claude/.mcp.json
```

---

**Version**: 1.0.0 | Part of ai-framework Claude Code plugin
