---
name: claude-code-expert
description: PROACTIVELY create, modify, update, improve, and fix Claude Code components (sub-agents, slash commands, hooks, MCP integrations). Use when working with Claude Code plugin development or when users mention creating, building, adding, implementing, modifying, updating, improving, fixing, or enhancing commands, agents, hooks, or MCP servers.
---

# Claude Code Expert

Production-ready Claude Code components with 100% consistency to official docs and ai-framework patterns.

## Purpose

Generate correct-on-first-attempt code for sub-agents, slash commands, hooks, and MCP integrations.

## Workflow

Before implementing ANY component, follow this protocol:

### Step 1: Identify Component Type

Determine which component user requests:

- **Sub-agent**: "Create agent for X" → specialized AI assistant
- **Slash command**: "Add command to X" → user-invoked workflow
- **Hook**: "Add hook to X" → event handler (SessionStart, PreToolUse, etc.)
- **MCP server**: "Integrate X server" → external tool integration

### Step 2: Official Documentation

**Training data is stale. APIs change every 3 months. Never assume syntax.**

Load [references/doc-map.md](references/doc-map.md) and WebFetch official docs for the component type:

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

Read existing ai-framework examples extracting patterns:

**Sub-agents**: Read agents/[relevant-category]/[similar-agent].md
- Extract: naming conventions, tool access patterns, constitutional constraints

**Commands**: Read commands/[relevant-category]/[similar-command].md
- Extract: argument-hint patterns, allowed-tools restrictions, workflow structure

**Hooks**: Read hooks/[similar-hook].py and hooks/hooks.json
- Extract: error handling patterns, JSON I/O format, exit code conventions

**MCP**: Read .claude/.mcp.json
- Extract: server configuration patterns, environment variable usage

See [references/naming-conventions.md](references/naming-conventions.md) and [references/language-conventions.md](references/language-conventions.md) for detailed standards.

### Step 4: Generate Component

Merge official syntax (Step 2) + project patterns (Step 3) + constitutional principles.

Load [references/constitutional-compliance.md](references/constitutional-compliance.md) for detailed requirements.

Core principles to apply:
- **Value/Complexity ≥ 2**: Simplest solution that works
- **Reuse First**: Use existing patterns before creating new
- **TDD**: Tests before implementation (if applicable)
- **AI-First**: Text/JSON interfaces for AI executability

### Step 5: Validate

Load appropriate checklist:

| Component     | Checklist                                                          |
| ------------- | ------------------------------------------------------------------ |
| Sub-agent     | [references/agent-checklist.md](references/agent-checklist.md)     |
| Slash command | [references/command-checklist.md](references/command-checklist.md) |
| Hook          | [references/hook-checklist.md](references/hook-checklist.md)       |
| MCP server    | [references/mcp-checklist.md](references/mcp-checklist.md)         |

Execute validation:

1. Run automated validators: `scripts/validate_[type].py`
2. Manual review against checklist
3. Execute Step 6 (Logic Review)
4. Confirm 100% correctness

**Only deliver when all gates passed.**

See [references/quality-gates.md](references/quality-gates.md) for gate details.

### Step 6: Logic Review

Load [references/logic-anti-patterns.md](references/logic-anti-patterns.md) verifying no anti-patterns present before delivery.

## Red Flags - STOP and Follow Workflow

If you catch yourself thinking:

- "I'm 90% confident from memory"
- "User is waiting / urgent deadline"
- "Just this once won't hurt"
- "Quick path is good enough"
- "I'll validate after delivery"
- "APIs probably haven't changed"
- "I saw similar syntax in training data"

**ALL of these mean: STOP. Follow Steps 1-6.**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "I remember the syntax" | Claude Code APIs change monthly. Your training data is 6+ months stale. |
| "It's urgent" | Broken code in production is 10x more urgent than current deadline. |
| "I'll validate later" | Later means never. Bugs compound with every use. |
| "Quality gates are overkill" | Gates exist because shortcuts created production incidents. |
| "WebFetch is slow" | 30 seconds of verification saves 30 minutes of debugging. |
| "Training data is recent enough" | **CRITICAL**: Assume all API syntax in your training is obsolete. |

## Deliverables

For each component, provide:
1. Component file(s) (agent.md, command.md, hook.py, .mcp.json entry)
2. Validation report confirming checklist passed
3. Integration instructions (file path, test commands)
