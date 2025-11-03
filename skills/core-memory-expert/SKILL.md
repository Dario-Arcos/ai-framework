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

## REST API (Advanced)

For programmatic access beyond MCP, Core provides a comprehensive REST API.

### When to Use REST API

**Use MCP (via setup_core_cloud.py) when:**
- Setting up for first time
- Using Claude Code, Cursor, VS Code
- Want automatic agents (memory-search, memory-ingest)
- Prefer zero-friction setup

**Use REST API when:**
- Building custom integrations
- Need granular control over memory operations
- Managing Spaces programmatically
- Implementing custom workflows
- Server-to-server communication

### Quick Start

**Get API Key:**
1. Visit https://core.heysol.ai → Settings → API Keys
2. Generate new key
3. Export: `export CORE_API_KEY='your-key-here'`

**Basic Search:**
```bash
curl -X POST https://core.heysol.ai/api/v1/search \
  -H "Authorization: Bearer $CORE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "TypeScript preferences"}'
```

**Ingest Data:**
```bash
curl -X POST https://core.heysol.ai/api/v1/add \
  -H "Authorization: Bearer $CORE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "Project uses PostgreSQL with JSONB for schemas",
    "metadata": {"project": "TaskMaster"}
  }'
```

### Spaces Management

**What are Spaces:**
- Organizational containers for memory
- Like folders for knowledge graph
- Filter searches to relevant context
- Manage privacy/sharing boundaries

**Manage via CLI:**
```bash
# List all spaces
python3 scripts/manage_spaces.py list

# Create new space
python3 scripts/manage_spaces.py create "Work Project" \
  --description "Professional context"

# View space details
python3 scripts/manage_spaces.py get space-work

# Assign statements to space
python3 scripts/manage_spaces.py assign space-work \
  --statements stmt_1,stmt_2,stmt_3

# Delete space
python3 scripts/manage_spaces.py delete space-old
```

**Example Workflow:**
```bash
# 1. Set API key
export CORE_API_KEY='rc_pat_xxx...'

# 2. Create project space
python3 scripts/manage_spaces.py create "Client Alpha" \
  --description "Alpha project memory"

# 3. Ingest data to space
curl -X POST https://core.heysol.ai/api/v1/add \
  -H "Authorization: Bearer $CORE_API_KEY" \
  -d '{
    "data": "Client prefers React over Vue",
    "metadata": {"spaceId": "space-alpha"}
  }'

# 4. Search within space
curl -X POST https://core.heysol.ai/api/v1/search \
  -H "Authorization: Bearer $CORE_API_KEY" \
  -d '{
    "query": "framework preferences",
    "spaceIds": ["space-alpha"]
  }'
```

### Privacy & Sharing

**What you can control:**
- Space organization (project, personal, work)
- Search filtering by space
- Statement assignment to spaces
- OAuth scopes (read, write, mcp, integration)

**What you CANNOT share natively:**
- Memory with other users (single-user per account)
- Public spaces (all data private by default)
- Cross-account search

**Workarounds for team collaboration:**
1. Export via API, share file
2. Build OAuth app that aggregates multiple users
3. Self-host with custom team features

See [references/spaces-and-privacy.md](references/spaces-and-privacy.md) for complete privacy model.

### Full API Reference

**Complete endpoint documentation:**
- Memory operations (add, search, retrieve facts)
- Spaces CRUD (create, read, update, delete, bulk assign)
- Monitoring (logs, queue status)
- Webhooks (real-time notifications)
- Integrations (connect external services)
- OAuth (scopes, authentication flows)

See [references/rest-api-reference.md](references/rest-api-reference.md) for comprehensive API docs.

### Python Integration Example

```python
import os
import requests

BASE_URL = "https://core.heysol.ai"
API_KEY = os.getenv("CORE_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def search_memory(query, space_ids=None):
    """Search Core memory"""
    payload = {"query": query}
    if space_ids:
        payload["spaceIds"] = space_ids

    response = requests.post(
        f"{BASE_URL}/api/v1/search",
        headers=HEADERS,
        json=payload
    )
    response.raise_for_status()
    return response.json()

# Usage
results = search_memory("authentication approach", ["space-work"])
for result in results.get("results", []):
    print(f"[{result['relevance']:.2f}] {result['content']}")
```

## Team Collaboration (Advanced)

**Problem:** Core Cloud doesn't support native team sharing.

**Solution:** MCP-to-REST proxy for read-only team access.

### Setup

**Repo:** https://github.com/Dario-Arcos/team-core-proxy

**Architecture:**
```
Team (Claude Code) → Proxy Railway → Core REST API
      MCP              MCP↔REST         Admin token
```

**Deploy:** 15 minutes to Railway (free tier)

**Result:**
- Team gets read-only memory access
- Admin controls what's in memory (deterministic)
- No team members need Core accounts
- Organize with Spaces (team sees all)

**Config team members:**
```json
{
  "mcpServers": {
    "team-memory": {
      "type": "http",
      "url": "https://your-proxy.railway.app/mcp",
      "headers": {
        "Authorization": "Bearer shared-team-token"
      }
    }
  }
}
```

See repo for complete setup instructions.

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
- `manage_spaces.py` - Spaces CRUD operations (REST API)

### References
- `core-concepts.md` - Architecture and data model
- `mcp-configuration.md` - Complete configuration reference
- `troubleshooting.md` - Common issues and solutions
- `rest-api-reference.md` - Complete REST API documentation
- `spaces-and-privacy.md` - Spaces management and privacy model

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
