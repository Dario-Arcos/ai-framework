# MCP Server Validation Checklist

Use this checklist to validate MCP server integrations before delivery.

## Configuration File

- [ ] File location: `.claude/.mcp.json` (project) or `~/.claude/mcp.json` (user)
- [ ] File is valid JSON (no syntax errors)
- [ ] File encoding: UTF-8
- [ ] Proper structure with `mcpServers` root object

## MCP Server Entry

### Required Fields

- [ ] Server name (unique key in `mcpServers` object)
- [ ] Transport type determined (http, stdio, sse deprecated)

### HTTP Transport

```json
{
  "type": "http",
  "url": "https://api.example.com/mcp",
  "headers": {}
}
```

- [ ] `type:` set to `"http"`
- [ ] `url:` valid HTTPS URL
- [ ] `headers:` object for authentication (if needed)

### Stdio Transport

```json
{
  "command": "/path/to/server",
  "args": [],
  "env": {}
}
```

- [ ] `command:` absolute path or command in PATH
- [ ] `args:` array of string arguments
- [ ] `env:` object with environment variables (if needed)

### SSE Transport (Deprecated)

- [ ] **NOT USED** (sse transport is deprecated)
- [ ] If migrating from sse, use http instead

## Security

- [ ] No hardcoded credentials in configuration
- [ ] Secrets stored in environment variables
- [ ] Environment variable expansion used: `${VAR_NAME:-default}`
- [ ] Authorization headers use env vars (not plain text)
- [ ] API keys loaded from environment

### Example (Secure)

```json
{
  "mcpServers": {
    "secure-api": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_TOKEN}"
      }
    }
  }
}
```

## Scope

- [ ] Scope determined: `local`, `project`, or `user`
- [ ] `project` scope: Configuration in `.mcp.json` (version controlled)
- [ ] `local` scope: Not checked into git (personal config)
- [ ] `user` scope: User-wide (`~/.claude/mcp.json`)

## CLI Integration

### Adding Server via CLI

- [ ] Correct command used:
  - `claude mcp add --transport http <name> <url>` (HTTP)
  - `claude mcp add --transport stdio <name> -- <command>` (stdio)
- [ ] `--scope` flag used appropriately
- [ ] `--header` or `--env` flags for auth

### Validation Commands

- [ ] `claude mcp list` shows new server
- [ ] `claude mcp get <name>` displays correct config
- [ ] No errors in output

## Transport-Specific Validation

### HTTP Servers

- [ ] URL is publicly accessible (or within network)
- [ ] HTTPS preferred over HTTP
- [ ] Authentication headers correct format
- [ ] Endpoint responds to MCP protocol

### Stdio Servers

- [ ] Command is installed and in PATH
- [ ] `npx -y` used for npm packages (auto-install)
- [ ] Arguments array correctly formatted
- [ ] Environment variables set (if required by server)

## Environment Variables

- [ ] All referenced env vars documented
- [ ] Default values provided with `:-` syntax
- [ ] No circular dependencies in env var expansion
- [ ] Env vars exist in runtime environment

### Example Documentation

```bash
# Required environment variables:
export API_TOKEN="your-token-here"
export API_BASE_URL="https://api.example.com"  # optional, defaults shown
```

## Performance

- [ ] `MCP_TIMEOUT` environment variable set (if custom timeout needed)
- [ ] `MAX_MCP_OUTPUT_TOKENS` configured (for large datasets)
- [ ] Server startup time reasonable (< 10s)

## Integration

- [ ] No duplicate server names
- [ ] Server name descriptive (e.g., `playwright`, `shadcn`, `notion`)
- [ ] Server tools available in Claude Code
- [ ] Server tested with actual MCP calls

## Documentation

- [ ] Installation instructions included
- [ ] Authentication setup documented
- [ ] Required environment variables listed
- [ ] Example usage provided

## Common MCP Servers

### Official Servers (Reference)

- [ ] playwright: Browser automation
- [ ] shadcn: UI component discovery
- [ ] notion: Notion API integration
- [ ] airtable: Airtable database access

## Quality Gates

- [ ] JSON syntax validated (use `jq . .mcp.json`)
- [ ] Server responds to MCP protocol
- [ ] Authentication working (if required)
- [ ] All assumptions validated against official docs
- [ ] Ready for team use (if project scope)

## OAuth (if applicable)

- [ ] OAuth flow initiated via `/mcp` command
- [ ] OAuth credentials stored securely
- [ ] Token refresh mechanism working

## Constitutional Compliance

- [ ] Value/Complexity ≥ 2 (necessary integration)
- [ ] Reuses existing server config patterns
- [ ] Security validated (no credential exposure)
- [ ] Simplest configuration that works

## Final Verification

- [ ] WebFetch used to verify current official MCP docs
- [ ] Existing `.mcp.json` reviewed for patterns
- [ ] Server tested in actual Claude Code session
- [ ] Checklist items 100% confirmed
- [ ] Professional reputation staked on correctness

**Sign-off**: Only deliver when ALL items checked.
