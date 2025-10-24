---
name: claude-code-expert
description: Senior-level expert in creating Claude Code components (sub-agents, slash commands, hooks, MCP integrations) following official documentation and ai-framework patterns. Use when creating or modifying Claude Code plugin components.
---

# Claude Code Expert

Expert-level skill for creating production-ready Claude Code components with 100% consistency to official documentation and ai-framework project patterns.

## Purpose

Generate correct-on-first-attempt code for:

- **Sub-agents** (specialized AI assistants)
- **Slash commands** (user-invoked workflows)
- **Hooks** (event handlers for lifecycle control)
- **MCP integrations** (Model Context Protocol servers)

All outputs follow official Claude Code syntax and ai-framework constitutional principles.

## ⚠️ MANDATORY PRE-IMPLEMENTATION PROTOCOL

**CRITICAL**: Your training data is stale. APIs change every 3 months. Never assume syntax.

Before implementing ANY component, execute this protocol:

### Step 1: Identify Component Type

Determine which component the user is requesting:

- **Sub-agent**: "Create an agent for X" → Task tool invocation
- **Slash command**: "Add a command to X" → User-invoked workflow
- **Hook**: "Add a hook to X" → Event handler (SessionStart, PreToolUse, etc.)
- **MCP server**: "Integrate X server" → External tool integration

### Step 2: WebFetch Official Documentation (MANDATORY)

**DO NOT SKIP THIS STEP**

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

**Why this is mandatory**:

- Official docs = source of truth
- Training data = likely outdated
- One WebFetch = avoid 10 correction iterations

### Step 3: Load Project Patterns

Read existing ai-framework examples to extract:

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

1. **Run automated validators (MANDATORY)**:
   - Commands: `scripts/validate_bash_blocks.py` + `scripts/validate_tool_invocations.py`
   - All: `scripts/validate_[type].py`
2. **Manual review against checklist** (semantic/logic)
3. **Execute Step 6** (AI Logic Review - see below)
4. Confirm 100% correctness

**Only deliver when all gates passed.**

### Step 6: AI Logic Consistency Review (MANDATORY)

**Execute this self-review BEFORE delivery.**

#### 6.1 Load Anti-Patterns Knowledge

Read [references/logic-anti-patterns.md](references/logic-anti-patterns.md) to activate pattern detection.

#### 6.2 Analyze Generated Component

Review the component you just created:

**For Commands with Bash**:

- [ ] Variables defined before use? (no AP-001)
- [ ] Error paths include cleanup? (no AP-002, AP-006)
- [ ] Variables quoted in bash? (no AP-003)
- [ ] Heredocs properly scoped? (no AP-004)
- [ ] Conditionals closed? (no AP-005)

**For Commands with Tool Invocations**:

- [ ] Context loaded before Task calls? (no AP-007)
- [ ] Parallel tasks independent? (no AP-008)
- [ ] All tools in allowed-tools? (no AP-009)

**For Agents**:

- [ ] Tools sufficient for instructions? (no AP-010)
- [ ] No circular agent calls? (no AP-011)

**For Hooks**:

- [ ] I/O streams correct (stdout/stderr)? (no AP-012)
- [ ] Exit codes match behavior? (no AP-013)

**For MCP**:

- [ ] No hardcoded secrets? (no AP-014)
- [ ] Env vars have defaults? (no AP-015)

**Cross-Component**:

- [ ] Naming consistent with similar components? (no AP-016)
- [ ] Not duplicating existing functionality? (no AP-017)

#### 6.3 Self-Critique

Ask yourself:

> "If this fails in production, what would break?"
> "Did I check ALL anti-patterns?"
> "Would a senior engineer approve this without changes?"

#### 6.4 Fix or Report

**If ANY anti-pattern detected**:

- Fix immediately
- Re-run Step 5 validators
- Re-execute this step

**If zero anti-patterns**:

- Document that logic review passed
- Proceed to delivery

**Quality gate**: "Would you bet your professional reputation on this working correctly?"

## Component-Specific Workflows

### Creating Sub-Agents

**Triggers**: "Create agent for", "Add sub-agent that", "Build specialized agent"

**Workflow**:

1. WebFetch `https://docs.claude.com/en/docs/claude-code/sub-agents`
2. Read 2-3 similar agents from `agents/[category]/`
3. Generate agent.md with:
   - YAML frontmatter: `name`, `description`, `tools` (optional), `model` (optional)
   - Markdown body: clear instructions, examples, domain expertise
4. Validate with [references/agent-checklist.md](references/agent-checklist.md)
5. Save to `agents/[category]/[agent-name].md`

**Key patterns**:

- `tools:` field comma-separated (e.g., `Read, Grep, Glob, Bash`)
- `model:` values: `sonnet`, `opus`, `haiku`, `inherit`
- Include "PROACTIVELY" in description for auto-delegation
- Limit tools to necessary minimum (security)

### Creating Slash Commands

**Triggers**: "Create command for", "Add slash command", "Build workflow command"

**Workflow**:

1. WebFetch `https://docs.claude.com/en/docs/claude-code/slash-commands`
2. Read 2-3 similar commands from `commands/[category]/`
3. Generate command.md with:
   - YAML frontmatter: `description`, `argument-hint` (optional), `allowed-tools` (optional)
   - Markdown body: workflow steps, parameter usage ($1, $2, $ARGUMENTS)
4. Validate with [references/command-checklist.md](references/command-checklist.md)
5. Save to `commands/[category]/[command-name].md`

**Key patterns**:

- `allowed-tools:` restricts tool access (security)
- `argument-hint:` guides user input
- Use `!` prefix for bash execution in markdown
- Use `@` prefix for file references

### Creating Hooks

**Triggers**: "Create hook for", "Add event handler", "Implement lifecycle hook"

**Workflow**:

1. WebFetch `https://docs.claude.com/en/docs/claude-code/hooks`
2. Read similar hook from `hooks/[hook-name].py`
3. Read `hooks/hooks.json` for configuration patterns
4. Generate:
   - Python script with JSON stdin/stdout
   - Error handling (sys.stderr for errors)
   - Exit codes (0=success, 2=block, other=non-blocking error)
5. Update `hooks/hooks.json` with new hook registration
6. Validate with [references/hook-checklist.md](references/hook-checklist.md)
7. Save to `hooks/[hook-name].py`

**Key patterns**:

- **No external dependencies** (stdlib only)
- **Spanish error messages** (user-facing)
- **JSON output** for advanced control
- **Absolute paths** using `$CLAUDE_PROJECT_DIR`

### Creating MCP Integrations

**Triggers**: "Add MCP server", "Integrate [service] via MCP", "Configure MCP for"

**Workflow**:

1. WebFetch `https://docs.claude.com/en/docs/claude-code/mcp`
2. Read `.claude/.mcp.json` for existing patterns
3. Determine transport type: http, stdio (sse deprecated)
4. Generate configuration entry
5. Update `.claude/.mcp.json`
6. Validate with [references/mcp-checklist.md](references/mcp-checklist.md)

**Key patterns**:

- Use `project` scope for team-shared tools
- Store secrets in env vars, not hardcoded
- Environment variable expansion: `${VAR_NAME:-default}`
- HTTP servers preferred for remote services
- stdio servers for local processes

## Best Practices (Transversal)

### Naming Conventions

- **Sub-agents**: `snake-case` (e.g., `code-quality-reviewer`)
- **Commands**: `kebab-case` with category prefix (e.g., `speckit.plan`)
- **Hooks**: `snake_case` with descriptive suffix (e.g., `session_start.py`)
- **MCP servers**: `kebab-case` (e.g., `playwright`, `shadcn`)

### Documentation Language

- **Code & AI instructions**: English
- **User-facing messages**: Spanish
- **Technical terms**: English (even in Spanish docs)

### Constitutional Compliance

Always verify:

- [ ] Value/Complexity ratio ≥ 2
- [ ] Reused existing patterns where possible
- [ ] AI-First design (text/JSON interfaces)
- [ ] Security validated (no credential exposure)
- [ ] Simplest solution that meets requirements

### Common Pitfalls to Avoid

❌ **Assuming syntax from training** → Always WebFetch
❌ **Creating new patterns** → Reuse existing unless justified
❌ **Over-engineering** → Simplest solution wins
❌ **Skipping validation** → Checklist mandatory
❌ **Mixing languages** → English for code, Spanish for users
❌ **Hardcoding secrets** → Use env vars
❌ **Adding external deps** → Stdlib only (hooks/scripts)

## Output Format

Always deliver:

1. **Component file(s)** (agent.md, command.md, hook.py, .mcp.json entry)
2. **Validation report** (checklist confirmation)
3. **Integration instructions** (where to save, how to test)

**Quality standard**: Production-ready, no corrections needed.

## Examples

See existing components in ai-framework:

- **Sub-agents**: `agents/Code Review & Security/code-quality-reviewer.md`
- **Commands**: `commands/git-github/commit.md`, `commands/SDD-cycle/speckit.plan.md`
- **Hooks**: `hooks/session-start.py`, `hooks/security_guard.py`
- **MCP**: `.claude/.mcp.json` (playwright, shadcn servers)

## Supporting Files

- [references/doc-map.md](references/doc-map.md) - Official documentation URLs
- [references/agent-checklist.md](references/agent-checklist.md) - Sub-agent validation
- [references/command-checklist.md](references/command-checklist.md) - Command validation
- [references/hook-checklist.md](references/hook-checklist.md) - Hook validation
- [references/mcp-checklist.md](references/mcp-checklist.md) - MCP validation
- `scripts/validate_*.py` - Automated validators (optional)
- `assets/*.template.*` - Starting templates (optional)

## Skill Invocation

This skill activates when users request:

- "Create a sub-agent for X"
- "Add a command to X"
- "Implement a hook for X"
- "Integrate X via MCP"
- "Build a Claude Code component"

**Explicit invocation**: Not required, auto-activates based on description match.
