# MCP Server Validation Checklist

## Overview

This reference defines the validation checklist for MCP server integrations. Use this checklist to verify MCP configurations meet all requirements before delivery.

---

## Configuration File

**Constraints:**
- You MUST place configuration at `.claude/.mcp.json` (project) or `~/.claude/mcp.json` (user) because these are the official locations
- You MUST ensure file is valid JSON because syntax errors prevent loading
- You MUST use UTF-8 encoding because other encodings cause parsing errors
- You MUST use proper structure with `mcpServers` root object because this is the schema

---

## MCP Server Entry

### Required Fields

**Constraints:**
- You MUST provide unique server name (key in `mcpServers` object) because duplicates cause conflicts
- You MUST determine transport type (http, stdio; sse is deprecated) because this affects configuration

### HTTP Transport

```json
{
  "type": "http",
  "url": "https://api.example.com/mcp",
  "headers": {}
}
```

**Constraints:**
- You MUST set `type:` to `"http"` because this identifies the transport
- You MUST use valid HTTPS URL because HTTP is insecure
- You SHOULD include `headers:` object for authentication if needed because this enables auth

### Stdio Transport

```json
{
  "command": "/path/to/server",
  "args": [],
  "env": {}
}
```

**Constraints:**
- You MUST provide `command:` as absolute path or command in PATH because relative paths fail
- You MUST format `args:` as array of string arguments because this is the schema
- You SHOULD include `env:` object with environment variables if needed because servers may require configuration

### SSE Transport (Deprecated)

**Constraints:**
- You MUST NOT use SSE transport because it is deprecated
- You MUST migrate from SSE to HTTP if converting existing config because SSE will stop working

---

## Security

**Constraints:**
- You MUST NOT include hardcoded credentials in configuration because they get committed to version control
- You MUST store secrets in environment variables because this keeps them out of code
- You MUST use environment variable expansion syntax `${VAR_NAME:-default}` because this enables configuration
- You MUST NOT use plain text in Authorization headers because this exposes credentials
- You MUST load API keys from environment because hardcoded keys are a security risk

### Secure Example

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

---

## Scope

**Constraints:**
- You MUST determine scope (`local`, `project`, or `user`) before configuration because this affects location
- You MUST use `project` scope (`.mcp.json`) for version-controlled configuration because team needs access
- You SHOULD use `local` scope for personal config not checked into git because this keeps personal settings private
- You SHOULD use `user` scope (`~/.claude/mcp.json`) for user-wide configuration because this applies globally

---

## CLI Integration

### Adding Server via CLI

**Constraints:**
- You MUST use correct command format:
  - `claude mcp add --transport http <name> <url>` (HTTP)
  - `claude mcp add --transport stdio <name> -- <command>` (stdio)
- You SHOULD use `--scope` flag appropriately because this controls location
- You SHOULD use `--header` or `--env` flags for auth because this sets credentials

### Validation Commands

**Constraints:**
- You MUST verify `claude mcp list` shows new server because this confirms registration
- You SHOULD verify `claude mcp get <name>` displays correct config because this confirms settings
- You MUST NOT ignore errors in output because they indicate problems

---

## Transport-Specific Validation

### HTTP Servers

**Constraints:**
- You MUST verify URL is accessible (publicly or within network) because unreachable URLs fail
- You SHOULD prefer HTTPS over HTTP because HTTP is insecure
- You MUST format authentication headers correctly because incorrect format fails
- You MUST verify endpoint responds to MCP protocol because non-MCP endpoints fail

### Stdio Servers

**Constraints:**
- You MUST verify command is installed and in PATH because missing commands fail
- You SHOULD use `npx -y` for npm packages (auto-install) because this ensures availability
- You MUST format arguments array correctly because incorrect format fails
- You MUST set environment variables if required by server because missing vars cause failures

---

## Environment Variables

**Constraints:**
- You MUST document all referenced env vars because undocumented vars cause confusion
- You SHOULD provide default values with `:-` syntax because this handles missing vars
- You MUST NOT create circular dependencies in env var expansion because this causes infinite loops
- You MUST verify env vars exist in runtime environment because missing vars cause failures

### Example Documentation

```bash
# Required environment variables:
export API_TOKEN="your-token-here"
export API_BASE_URL="https://api.example.com"  # optional, defaults shown
```

---

## Performance

**Constraints:**
- You SHOULD set `MCP_TIMEOUT` environment variable if custom timeout needed because long operations may require more time
- You SHOULD configure `MAX_MCP_OUTPUT_TOKENS` for large datasets because default may be insufficient
- You MUST verify server startup time is reasonable (< 10s) because slow startup degrades experience

---

## Integration

**Constraints:**
- You MUST NOT use duplicate server names because name collisions cause conflicts
- You MUST use descriptive server name (e.g., `playwright`, `shadcn`, `notion`) because this aids discovery
- You MUST verify server tools are available in Claude Code because unavailable tools cannot be used
- You MUST test server with actual MCP calls because untested servers may fail

---

## Documentation

**Constraints:**
- You MUST include installation instructions because users need to set up
- You MUST document authentication setup because users need to configure auth
- You MUST list required environment variables because users need to set them
- You SHOULD provide example usage because this helps users get started

---

## Quality Gates

**Constraints:**
- You MUST validate JSON syntax (use `jq . .mcp.json`) because invalid JSON breaks loading
- You MUST verify server responds to MCP protocol because non-compliant servers fail
- You MUST verify authentication is working if required because failed auth blocks access
- You MUST validate all assumptions against official docs because stale training data causes errors
- You MUST be ready for team use if project scope because incomplete config blocks others

---

## OAuth (if applicable)

**Constraints:**
- You MUST initiate OAuth flow via `/mcp` command because this is the official method
- You MUST store OAuth credentials securely because exposed tokens are a security risk
- You MUST verify token refresh mechanism is working because expired tokens block access

---

## Constitutional Compliance

**Constraints:**
- You MUST achieve Value/Complexity ≥ 2 because lower ratios indicate over-engineering
- You MUST reuse existing server config patterns because duplication increases maintenance
- You MUST validate security (no credential exposure) because security is mandatory
- You MUST use simplest configuration that works because unnecessary complexity reduces maintainability

---

## Final Verification

**Constraints:**
- You SHOULD use WebFetch to verify current official MCP docs because documentation evolves
- You SHOULD review existing `.mcp.json` for patterns because consistency aids maintenance
- You MUST test server in actual Claude Code session because real testing catches issues
- You MUST confirm 100% of checklist items because partial compliance causes failures
- You MUST stake professional reputation on correctness because this is the standard

**Sign-off**: Only deliver when ALL constraints satisfied.

---

## Troubleshooting

### Server Not Loading

If server is not available in Claude Code:
- You SHOULD verify configuration file location is correct
- You SHOULD check JSON syntax is valid
- You MUST verify server name is unique

### Connection Issues

If server cannot connect:
- You SHOULD verify URL is accessible from your network
- You SHOULD check authentication headers are correct
- You MUST verify environment variables are set

### Authentication Failures

If authentication fails:
- You SHOULD verify API tokens are valid
- You SHOULD check token format in headers
- You MUST verify env var expansion is working

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
