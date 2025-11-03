# MCP Configuration Reference

Complete reference for configuring RedPlanet Core MCP server across different environments and use cases.

## Base Configuration

### Core Cloud (Recommended)

**Basic setup:**
```bash
claude mcp add --transport http core-memory \
  https://core.heysol.ai/api/v1/mcp?source=Claude-Code
```

**What this does:**
- Registers "core-memory" MCP server
- Uses HTTP transport
- Points to Core Cloud endpoint
- Identifies client as "Claude-Code"

### Self-Hosted

**Basic setup:**
```bash
claude mcp add --transport http core-memory \
  http://localhost:3000/api/v1/mcp?source=Claude-Code
```

**Custom domain:**
```bash
claude mcp add --transport http core-memory \
  https://your-core-instance.com/api/v1/mcp?source=Claude-Code
```

## URL Parameters

### Required: source

Identifies which tool is connecting.

**Valid values:**
- `Claude` - Claude AI (web/app)
- `Claude-Code` - Claude Code CLI
- `Cursor` - Cursor editor
- `VSCode` - VS Code
- `Windsurf` - Windsurf editor

**Example:**
```
?source=Claude-Code
```

### Optional: integrations

Enables specific external integrations while disabling others.

**Format:** Comma-separated list of integration names

**Available integrations:**
- `github` - GitHub repositories, issues, PRs
- `linear` - Linear tasks and projects
- `slack` - Slack messages and channels
- `notion` - Notion pages and databases

**Example:**
```
?source=Claude-Code&integrations=github,linear
```

**Use cases:**
- **Development focus:** `&integrations=github`
- **Project management:** `&integrations=linear,github`
- **Team communication:** `&integrations=slack,linear`

### Optional: no_integrations

Disables all external integrations, enabling only Core memory tools.

**Example:**
```
?source=Claude-Code&no_integrations=true
```

**Use case:**
- Pure memory functionality without external services
- Simplified setup for testing
- Privacy-focused configuration

**Note:** Mutually exclusive with `integrations` parameter.

## Configuration Examples

### Development Workflow

**Focused on code:**
```bash
claude mcp add --transport http core-memory \
  "https://core.heysol.ai/api/v1/mcp?source=Claude-Code&integrations=github"
```

### Project Management

**Tasks + code:**
```bash
claude mcp add --transport http core-memory \
  "https://core.heysol.ai/api/v1/mcp?source=Claude-Code&integrations=github,linear"
```

### Team Collaboration

**Full integration:**
```bash
claude mcp add --transport http core-memory \
  "https://core.heysol.ai/api/v1/mcp?source=Claude-Code&integrations=github,linear,slack"
```

### Memory Only

**No external services:**
```bash
claude mcp add --transport http core-memory \
  "https://core.heysol.ai/api/v1/mcp?source=Claude-Code&no_integrations=true"
```

### Maximum Access

**All integrations enabled:**
```bash
claude mcp add --transport http core-memory \
  "https://core.heysol.ai/api/v1/mcp?source=Claude-Code"
```

## .mcp.json Structure

After registration, Core appears in `.mcp.json`:

### HTTP Transport (Core Cloud)

```json
{
  "mcpServers": {
    "core-memory": {
      "type": "http",
      "url": "https://core.heysol.ai/api/v1/mcp?source=Claude-Code"
    }
  }
}
```

### HTTP with Integrations

```json
{
  "mcpServers": {
    "core-memory": {
      "type": "http",
      "url": "https://core.heysol.ai/api/v1/mcp?source=Claude-Code&integrations=github,linear"
    }
  }
}
```

### Self-Hosted

```json
{
  "mcpServers": {
    "core-memory": {
      "type": "http",
      "url": "http://localhost:3000/api/v1/mcp?source=Claude-Code"
    }
  }
}
```

### With Authentication Headers (Advanced)

```json
{
  "mcpServers": {
    "core-memory": {
      "type": "http",
      "url": "https://core.heysol.ai/api/v1/mcp?source=Claude-Code",
      "headers": {
        "Authorization": "Bearer ${CORE_API_KEY}"
      }
    }
  }
}
```

**Note:** OAuth is preferred over API keys for production.

## Available MCP Tools

Once configured, Core provides these tools:

### memory_search

**Purpose:** Retrieve context from memory

**Usage:**
```
Search memory for: "TypeScript preferences"
```

**Parameters:**
- `query` (required): Search query
- `temporal_filter` (optional): time range
- `reliability_filter` (optional): confidence threshold

### memory_ingest

**Purpose:** Store information in memory

**Usage:**
```
Store in memory: "Project uses TypeScript with strict mode enabled. Decided for better type safety."
```

**Parameters:**
- `content` (required): Information to store
- `metadata` (optional): Context tags

## Integration Tools (When Enabled)

### GitHub Integration

**Available when:** `&integrations=github` or default (all enabled)

**Tools:**
- `github_create_issue`
- `github_search_repos`
- `github_get_pr`
- `github_list_issues`

### Linear Integration

**Available when:** `&integrations=linear` or default

**Tools:**
- `linear_create_issue`
- `linear_search_issues`
- `linear_update_status`

### Slack Integration

**Available when:** `&integrations=slack` or default

**Tools:**
- `slack_send_message`
- `slack_search_messages`
- `slack_list_channels`

## Authentication

### OAuth Flow (Recommended)

**Trigger:** Type `/mcp` in Claude Code conversation

**Steps:**
1. Type `/mcp` in conversation
2. Select "core-memory" from list
3. Browser opens automatically
4. Sign in to core.heysol.ai
5. Grant permissions
6. Return to Claude Code

**Advantages:**
- Automatic token refresh
- Revocable access
- Best security
- User-friendly

### API Key (Development Only)

**Setup:**
1. Visit core.heysol.ai → Settings → API Keys
2. Generate new API key
3. Add to `.mcp.json` (see example above)
4. Set `CORE_API_KEY` environment variable

**Disadvantages:**
- Manual rotation required
- No automatic refresh
- Less secure
- Not recommended for production

## Verification

### Check Registration

```bash
# View .mcp.json content
cat .mcp.json

# Should contain core-memory entry
```

### Check MCP List

```bash
# If claude CLI supports mcp list
claude mcp list

# Look for core-memory in output
```

### Test Connection

```bash
# Run verification script
python3 scripts/verify_connection.py
```

### Test in Conversation

In Claude Code conversation:
```
/mcp
```

Look for "core-memory" with "Connected" status.

## Configuration Management

### Update URL

**Modify `.mcp.json` directly:**

```bash
# Edit file
nano .mcp.json

# Update URL value
# Save and restart Claude Code
```

**Or re-register:**

```bash
# Remove old registration
claude mcp remove core-memory

# Add new configuration
claude mcp add --transport http core-memory "NEW_URL"
```

### Change Integrations

**Update URL parameter:**

```json
{
  "mcpServers": {
    "core-memory": {
      "type": "http",
      "url": "https://core.heysol.ai/api/v1/mcp?source=Claude-Code&integrations=github"
    }
  }
}
```

Restart Claude Code for changes to take effect.

### Remove Core

```bash
# Remove MCP registration
claude mcp remove core-memory

# Verify removal
cat .mcp.json
```

## Environment-Specific Configurations

### Development Environment

**Minimal setup for testing:**
```
?source=Claude-Code&no_integrations=true
```

**Benefits:**
- Fast setup
- No external dependencies
- Focus on Core functionality

### Staging Environment

**Limited integrations:**
```
?source=Claude-Code&integrations=github
```

**Benefits:**
- Test integration workflows
- Controlled scope
- Faster troubleshooting

### Production Environment

**Full access:**
```
?source=Claude-Code
```

**Benefits:**
- All integrations available
- Maximum functionality
- Team collaboration enabled

## Troubleshooting Configuration

### Core not appearing in /mcp

**Check:**
1. `.mcp.json` exists and is valid JSON
2. `core-memory` entry present
3. URL format correct
4. Restart Claude Code

### OAuth not triggering

**Check:**
1. Browser allows popups from Claude Code
2. Already signed in to core.heysol.ai
3. Try manual navigation to core.heysol.ai

### Tools not available

**Check:**
1. Authentication completed (green status in /mcp)
2. URL includes correct `source` parameter
3. If missing integrations, verify URL has correct `integrations` parameter

## Best Practices

**URL construction:**
- Always include `source` parameter
- Quote URLs with special characters in shell
- Use `no_integrations` for testing

**Security:**
- Prefer OAuth over API keys
- Use HTTPS for Core Cloud
- Don't commit API keys to git
- Use environment variables for credentials

**Maintenance:**
- Review integration usage quarterly
- Update URLs when migrating instances
- Test configuration changes in development first
- Document custom configurations

## Further Reading

- Core Concepts: core-concepts.md
- Troubleshooting: troubleshooting.md
- Integration Details: integrations.md
- Official MCP docs: docs.heysol.ai/mcp
