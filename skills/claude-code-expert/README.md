# Claude Code Expert Skill

Expert-level skill for creating production-ready Claude Code components with 100% consistency to official documentation and ai-framework patterns.

## What This Skill Does

Generates correct-on-first-attempt code for:

- **Sub-agents** (specialized AI assistants invoked via Task tool)
- **Slash commands** (user-invoked workflows with parameters)
- **Hooks** (event handlers for lifecycle control)
- **MCP integrations** (Model Context Protocol servers)

## Key Features

### 1. WebFetch Mandatory Protocol

- **Always** verifies current official syntax before implementation
- Never assumes syntax from training data (prevents stale API usage)
- One WebFetch = avoid 10 correction iterations

### 2. Project Pattern Integration

- Analyzes existing ai-framework components
- Reuses established patterns (naming, error handling, tools)
- Enforces constitutional compliance (Value/Complexity ≥ 2)

### 3. Automated Validation

- Python validators for each component type
- Checks YAML/JSON syntax, required fields, security patterns
- Stdlib only (no external dependencies)

### 4. Comprehensive Checklists

- Component-specific validation criteria
- Security, performance, and constitutional compliance checks
- Production-ready quality gates

## Usage

The skill activates automatically when users request Claude Code components:

```
"Create a sub-agent for code review"
"Add a command to generate changelogs"
"Implement a hook for security validation"
"Integrate Playwright MCP server"
```

**No explicit invocation needed** - Claude detects component creation requests.

## Structure

```
claude-code-expert/
├── SKILL.md                    # Main skill instructions
├── README.md                   # This file
├── references/
│   ├── doc-map.md             # Official docs URLs
│   ├── agent-checklist.md     # Sub-agent validation
│   ├── command-checklist.md   # Command validation
│   ├── hook-checklist.md      # Hook validation
│   └── mcp-checklist.md       # MCP validation
├── scripts/
│   ├── validate_agent.py      # Agent validator
│   ├── validate_command.py    # Command validator
│   ├── validate_hook.py       # Hook validator
│   └── validate_mcp.py        # MCP validator
└── assets/                     # (Empty - templates optional)
```

## Validation

Test validators against real components:

```bash
# Validate agent
python3 scripts/validate_agent.py agents/[category]/[agent].md

# Validate command
python3 scripts/validate_command.py commands/[category]/[command].md

# Validate hook
python3 scripts/validate_hook.py hooks/[hook].py hooks/hooks.json

# Validate MCP config
python3 scripts/validate_mcp.py .claude/.mcp.json
```

## Workflow

1. **Detect** component type (agent, command, hook, MCP)
2. **WebFetch** official docs for current syntax
3. **Load** existing project patterns
4. **Generate** component merging official + project patterns
5. **Validate** against checklist + automated validator
6. **Deliver** production-ready component

## Quality Standards

- **100% correct on first attempt** (no iteration needed)
- **Constitutional compliance** (Value/Complexity ≥ 2, Reuse First)
- **Security validated** (no hardcoded credentials, proper error handling)
- **Production-ready** (ready for team use without modifications)

## Maintenance

Update `references/doc-map.md` when Claude Code docs change:

- Check quarterly or when syntax errors occur
- Verify URLs still resolve via WebFetch
- Add new component types if introduced
- Update "Last Updated" date

## License

Part of ai-framework Claude Code plugin.
