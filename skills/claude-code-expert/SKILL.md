---
name: claude-code-expert
description: Investigates Claude Code questions (skills, sub-agents, hooks, MCPs, SDK) in official documentation before implementation. Training data is stale - always verify current APIs. Use when user asks about Claude Code features or plugin development.
---

# Claude Code Expert

**Core Principle**: Official docs FIRST, implementation SECOND.

Your training data is 6+ months stale. Claude Code APIs change frequently. **Never assume syntax from memory.**

---

## When to Use

- Creating/modifying sub-agents, slash commands, hooks, or MCP integrations
- Questions about Claude Code features (skills, hooks, MCPs, SDK)
- Fixing bugs in Claude Code plugin components
- User mentions: "create agent", "add command", "new hook", "integrate MCP"

---

## Workflow

### Step 1: Investigate Official Documentation

**Use agent-browser to research the official docs:**

```bash
agent-browser open https://code.claude.com/docs/en/overview
agent-browser snapshot -i
```

Navigate to the relevant section based on the question:

| Topic | Navigate to |
|-------|-------------|
| Sub-agents | Agents & Agentic Coding |
| Slash commands | Commands |
| Hooks | Hooks |
| MCP servers | MCP Servers |
| Skills | Skills |
| SDK | Claude Code SDK |
| Settings | Settings & Configuration |

**Extract:**
- Current syntax and structure
- Required vs optional fields
- Official examples
- Breaking changes from previous versions

### Step 2: If Official Docs Insufficient

If official documentation doesn't resolve the question:

1. **Search GitHub issues/discussions**: `agent-browser open https://github.com/anthropics/claude-code`
2. **Search community resources**: Reliable forums, Stack Overflow
3. **Check Anthropic blog/changelog**: Recent announcements

**Priority order:**
1. Official docs (authoritative)
2. GitHub issues (current bugs/features)
3. Community (practical solutions)

### Step 3: Implement with Verification

After gathering current information:

1. **Match project patterns**: Read existing ai-framework examples
2. **Generate component**: Merge official syntax + project conventions
3. **Validate**: Ensure no deprecated APIs used

---

## Red Flags - STOP and Verify

If you think:
- "I remember the syntax"
- "It's probably the same as before"
- "Training data should be recent enough"

**STOP. Use agent-browser to verify.**

30 seconds of verification saves 30 minutes of debugging.

---

## Quick Reference

```bash
# Open official docs
agent-browser open https://code.claude.com/docs/en/overview

# Navigate and extract
agent-browser snapshot -i
agent-browser click @[element]

# Search for specific topic
agent-browser find text "hooks" click
```

---

*Training data is stale. Official docs are truth. Verify before implementing.*
