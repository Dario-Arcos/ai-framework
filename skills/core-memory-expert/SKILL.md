---
name: core-memory-expert
description: Expert in implementing and using RedPlanet Core as memory layer for Claude Code projects. Use when user mentions Core, memory, RedPlanet, persistent context, knowledge graphs, or wants to setup/configure/troubleshoot memory systems. Handles both Cloud and self-hosted deployments with zero-friction setup automation.
---

# Core Memory Expert

World-class implementation and usage of RedPlanet Core memory layer for production projects.

## Overview

RedPlanet Core provides a portable memory layer based on temporal knowledge graphs, enabling persistent context across AI tools via Model Context Protocol (MCP).

**Key Capabilities:**
- **88.24% SOTA accuracy** on LoCoMo benchmark
- **Temporal knowledge graphs** tracking "who said what, when, why"
- **Cross-tool memory** (Claude, Cursor, VS Code, etc.)
- **Zero-friction setup** via automated scripts

## When to Use

Activate when user:
- Mentions "Core", "memory", "RedPlanet", "persistent context"
- Wants to setup memory system for project
- Needs troubleshooting for memory issues
- Asks about knowledge graphs or context persistence
- References "remember this" or "what did we discuss"

## Implementation Workflow

### Setup Core Cloud (Recommended)

**Quick Start:**
```bash
python3 scripts/setup_core_cloud.py
```

**What this does:**
1. Verifies Claude CLI installed
2. Registers Core MCP server
3. Provides authentication instructions
4. Verifies configuration

**With Integrations:**
```bash
# Specific integrations (GitHub + Linear)
python3 scripts/setup_core_cloud.py --integrations github,linear

# Core tools only (no external services)
python3 scripts/setup_core_cloud.py --no-integrations
```

**Manual Setup:**
```bash
claude mcp add --transport http core-memory \
  "https://core.heysol.ai/api/v1/mcp?source=Claude-Code"
```

Then authenticate:
1. Type `/mcp` in conversation
2. Select "core-memory"
3. Complete OAuth in browser

### Setup Self-Hosted

**Automated:**
```bash
bash scripts/setup_self_hosted.sh
```

**What this does:**
1. Checks Docker prerequisites
2. Clones Core repository
3. Configures environment (.env with OpenAI key)
4. Launches containers
5. Verifies services running

**With Options:**
```bash
# Custom directory
bash scripts/setup_self_hosted.sh --clone-dir ~/projects/core

# Provide OpenAI key upfront
bash scripts/setup_self_hosted.sh --openai-key sk-xxx...
```

### Create Automatic Memory Agents

**Generate Agents:**
```bash
python3 scripts/create_agents.py
```

**What this creates:**
- `.claude/agents/memory-search.md` - Auto-retrieves context at session start
- `.claude/agents/memory-ingest.md` - Auto-stores conversations after interactions

**Custom Location:**
```bash
python3 scripts/create_agents.py --output-dir custom/path
```

**Agent Behavior:**
- **memory-search**: Runs at SessionStart, searches for project context, user preferences, recent decisions
- **memory-ingest**: Runs after interactions, stores conceptual insights (excludes code blocks)

### Verify Connection

**Diagnostic Tool:**
```bash
python3 scripts/verify_connection.py
```

**What this checks:**
1. MCP registration in `.mcp.json`
2. Claude CLI availability
3. MCP server list status
4. Connection state

**Exit codes:**
- `0`: All checks passed, Core operational
- `1`: Issues detected, see output for remediation

## Using Core Memory

### Search Memory

**In conversation:**
```
What do you remember about TypeScript preferences?
```

Core automatically uses `mcp__core-memory__memory_search` tool.

**Best Practices:**
- Use specific queries: "authentication decisions" not "tell me everything"
- Include project context: "TaskMaster database schema"
- Use temporal filters when relevant: "decisions from last week"

### Store Information

**Explicit storage:**
```
Remember: This project uses PostgreSQL with JSONB for flexible schemas.
Rationale: Need schema flexibility for evolving product requirements.
```

**Automatic storage:**
If `memory-ingest` agent is configured, valuable insights are stored automatically after interactions.

### What Core Stores

**✅ Store:**
- Technical decisions and rationale
- User preferences and standards
- Architecture choices and trade-offs
- Project context and domain knowledge
- Conceptual explanations

**❌ Don't store:**
- Code blocks (use git)
- Logs/outputs (transient)
- Sensitive data (credentials, PII)
- File contents (use version control)

## Advanced Configuration

### MCP URL Parameters

**Base:** `https://core.heysol.ai/api/v1/mcp?source=Claude-Code`

**With integrations:**
```bash
# GitHub only
?source=Claude-Code&integrations=github

# Multiple
?source=Claude-Code&integrations=github,linear,slack

# Core tools only
?source=Claude-Code&no_integrations=true
```

See [references/mcp-configuration.md](references/mcp-configuration.md) for complete reference.

### Authentication Methods

**OAuth (Recommended):**
- Browser-based flow
- Automatic token refresh
- Easy revocation

**API Keys (Development):**
```json
{
  "mcpServers": {
    "core-memory": {
      "type": "http",
      "url": "...",
      "headers": {
        "Authorization": "Bearer ${CORE_API_KEY}"
      }
    }
  }
}
```

Set `CORE_API_KEY` environment variable.

## Troubleshooting

### Common Issues

**Core not in /mcp list:**
1. Check `.mcp.json` exists and valid
2. Verify "core-memory" entry present
3. Restart Claude Code

**Authentication fails:**
1. Type `/mcp` and select core-memory
2. Complete OAuth in browser
3. Verify at core.heysol.ai → Settings → MCP

**Tools not available:**
1. Verify authentication (green status in /mcp)
2. Check URL has `source` parameter
3. Restart Claude Code after config changes

**Memory not persisting:**
1. Verify memory_ingest executed (check core.heysol.ai)
2. Ensure storable content (not just code/logs)
3. Check agent configuration if using automatic storage

See [references/troubleshooting.md](references/troubleshooting.md) for comprehensive solutions.

## Architecture Deep Dive

### Memory Creation Pipeline

```
Input → Normalization → Extraction → Resolution → Graph Integration
```

1. **Normalization**: Contextualizes and standardizes input
2. **Extraction**: Identifies entities and relationships
3. **Resolution**: Handles contradictions, tracks evolution
4. **Graph Integration**: Connects temporal knowledge graph

### Memory Recall System

```
Query → Multi-Angle Search → Re-Ranking → Filtering → Results
```

**Search methods:**
- **Keyword**: Exact matching
- **Semantic**: Conceptual similarity
- **Graph traversal**: Relationship following

**Filtering:**
- Temporal (last week, month, all time)
- Reliability (confidence scoring)
- Relationship strength

See [references/core-concepts.md](references/core-concepts.md) for complete architecture.

## Integration Ecosystem

### External Services

When enabled, Core provides unified access to:
- **GitHub**: Issues, PRs, repositories
- **Linear**: Tasks, projects
- **Slack**: Messages, channels
- **Notion**: Pages, databases

**Enable via MCP URL:**
```
?source=Claude-Code&integrations=github,linear
```

### Browser Extension

Core captures content from:
- ChatGPT conversations
- Web pages (Chrome extension)
- YouTube transcripts
- Twitter threads

Configure at: core.heysol.ai → Integrations

## Resources

### Scripts
- `setup_core_cloud.py` - Automated Cloud setup
- `setup_self_hosted.sh` - Automated self-hosting
- `create_agents.py` - Generate automatic memory agents
- `verify_connection.py` - Connection diagnostic

### References
- `core-concepts.md` - Architecture and data model
- `mcp-configuration.md` - Complete configuration reference
- `troubleshooting.md` - Common issues and solutions

### Assets
- `memory-search-template.md` - Auto-search agent template
- `memory-ingest-template.md` - Auto-storage agent template

## Best Practices

**Setup:**
- Use Cloud deployment for simplicity
- Enable only needed integrations
- Verify connection before first use
- Create automatic agents for seamless experience

**Usage:**
- Store conceptual insights, not raw data
- Use specific queries for better recall
- Review memory monthly, prune obsolete data
- Never store sensitive information

**Security:**
- Prefer OAuth over API keys
- Use environment variables for credentials
- Review connected integrations quarterly
- Enable only required external services

**Performance:**
- Start with Core tools only, add integrations as needed
- Use keyword search when possible (faster)
- Prune knowledge graph periodically
- Monitor storage with Core web interface

## Performance Metrics

**LoCoMo Benchmark:**
- Average accuracy: 88.24%
- 300+ turn conversation support
- Sub-second search (after warm-up)
- Handles 1000s of stored facts

## Support

**Discord:** https://discord.gg/YGUZcvDjUa (#core-support)
**Email:** manik@poozle.dev
**GitHub:** https://github.com/RedPlanetHQ/core
**Docs:** https://docs.heysol.ai

---

**Implementation Checklist:**

1. [ ] Setup Core (Cloud or self-hosted)
2. [ ] Verify connection (`verify_connection.py`)
3. [ ] Create automatic agents (`create_agents.py`)
4. [ ] Test search with simple query
5. [ ] Store initial project context
6. [ ] Verify memory appears in core.heysol.ai
7. [ ] Configure integrations (if needed)
8. [ ] Review memory hygiene weekly
