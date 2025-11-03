# Troubleshooting Guide

Comprehensive solutions for common Core MCP issues, organized by symptom.

## Quick Diagnostic Checklist

Run these checks first:

```bash
# 1. Verify claude CLI
which claude

# 2. Check .mcp.json exists
cat .mcp.json | grep core-memory

# 3. Run automated diagnostic
python3 scripts/verify_connection.py
```

---

## Setup Issues

### "claude: command not found"

**Symptom:** Cannot run `claude mcp add` command

**Cause:** Claude Code CLI not installed or not in PATH

**Solution:**
```bash
# Check if installed
which claude

# If not found, install Claude Code CLI
# Visit: https://docs.claude.com/
```

**Verify fix:**
```bash
claude --version
```

---

### "MCP server registration failed"

**Symptom:** `claude mcp add` returns error

**Possible causes:**

**1. Invalid URL format**

**Check:**
```bash
# URL must be properly quoted if contains special characters
# WRONG:
claude mcp add --transport http core-memory https://core.heysol.ai/api/v1/mcp?source=Claude-Code

# CORRECT:
claude mcp add --transport http core-memory "https://core.heysol.ai/api/v1/mcp?source=Claude-Code"
```

**2. Missing --transport flag**

**Check:**
```bash
# WRONG:
claude mcp add core-memory URL

# CORRECT:
claude mcp add --transport http core-memory URL
```

**3. Server name already exists**

**Solution:**
```bash
# Remove old registration
claude mcp remove core-memory

# Re-add with correct configuration
claude mcp add --transport http core-memory "URL"
```

---

### ".mcp.json not created"

**Symptom:** Registration succeeds but `.mcp.json` not in project

**Cause:** MCP server registered in global config instead

**Check:**
```bash
# Look for global config
ls ~/.claude/.mcp.json
# or
ls ~/Library/Application\ Support/Claude/.mcp.json
```

**Solution:**

**Option A:** Create project-level `.mcp.json`:
```bash
# In project root
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "core-memory": {
      "type": "http",
      "url": "https://core.heysol.ai/api/v1/mcp?source=Claude-Code"
    }
  }
}
EOF
```

**Option B:** Use global config (works but less portable)

---

## Authentication Issues

### "core-memory shows 'Not Connected' in /mcp"

**Symptom:** Server appears in `/mcp` but status is disconnected

**Cause:** OAuth not completed

**Solution:**
```
1. In Claude Code conversation, type: /mcp
2. Click on "core-memory" entry
3. Browser should open automatically
4. Sign in to core.heysol.ai
5. Grant permissions when prompted
6. Return to Claude Code
7. Type /mcp again to verify status
```

**If browser doesn't open:**
- Manually navigate to https://core.heysol.ai
- Sign in
- Return to Claude Code and retry /mcp

---

### "OAuth completes but still shows disconnected"

**Symptom:** Signed in to Core but MCP shows not connected

**Diagnostic steps:**

**1. Restart Claude Code:**
```bash
# Exit Claude Code completely
# Restart and check /mcp again
```

**2. Check URL matches:**
```bash
# Verify .mcp.json URL exactly matches Core instance
cat .mcp.json | grep core-memory
```

**3. Verify account access:**
- Visit https://core.heysol.ai
- Ensure you're signed in
- Check Settings → MCP Connections
- Verify Claude-Code appears as connected

**4. Re-authenticate:**
```
Type /mcp in conversation
Select core-memory
Complete OAuth flow again
```

---

### "API key authentication not working"

**Symptom:** Using API key but tools not available

**Solution:**

**1. Verify key format:**
```bash
# Check .mcp.json
cat .mcp.json
```

**Should look like:**
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

**2. Set environment variable:**
```bash
# Add to .env or shell profile
export CORE_API_KEY="rc_pat_xxx..."

# Verify it's set
echo $CORE_API_KEY
```

**3. Restart Claude Code** after setting environment variable

**Note:** OAuth is strongly preferred over API keys.

---

## Tool Availability Issues

### "memory_search tool not available"

**Symptom:** Tool doesn't appear in Claude Code

**Diagnostic:**

**1. Verify authentication:**
```
Type /mcp
Check core-memory shows "Connected"
```

**2. Check URL parameter:**
```bash
# Verify source parameter present
cat .mcp.json | grep source
# Should contain: ?source=Claude-Code
```

**3. Verify no typos in server name:**
```bash
# Check exact spelling
cat .mcp.json
# Must be exactly "core-memory"
```

**4. Restart Claude Code:**
```bash
# Tools loaded at startup
# Restart needed after config changes
```

---

### "Integration tools missing (github, linear, etc.)"

**Symptom:** Core memory tools work but integration tools don't appear

**Cause:** Integrations disabled or not connected

**Solution:**

**1. Check URL configuration:**
```bash
cat .mcp.json | grep url
```

**If contains `no_integrations=true`:**
```bash
# Remove that parameter
# Or change to specific integrations:
"url": "https://core.heysol.ai/api/v1/mcp?source=Claude-Code&integrations=github,linear"
```

**2. Connect integrations in Core:**
- Visit https://core.heysol.ai
- Go to Settings → Integrations
- Connect desired services (GitHub, Linear, Slack)
- Grant permissions

**3. Restart Claude Code** after URL or integration changes

---

## Memory/Search Issues

### "Search returns no results"

**Symptom:** `memory_search` tool runs but finds nothing

**Possible causes:**

**1. No data in memory yet**

**Verify:**
- Visit https://core.heysol.ai
- Check Memory section
- If empty, nothing stored yet

**Solution:**
```bash
# Store some information first
# In conversation: "Remember: I prefer TypeScript"
# Or run memory_ingest manually
```

**2. Query too specific**

**Solution:**
```
# Instead of: "exact phrase from three months ago"
# Try: "preferences about TypeScript"
```

**3. Temporal filter too restrictive**

**Solution:**
```
# Remove time constraints
# Search "all time" instead of "last week"
```

---

### "Memory not persisting across sessions"

**Symptom:** Stored information doesn't appear in later conversations

**Diagnostic:**

**1. Verify memory_ingest executed:**
```
# Check Core web interface
# Visit https://core.heysol.ai → Memory
# Verify entries appear
```

**2. Check agent configuration:**
```bash
# If using automatic agents
ls .claude/agents/memory-ingest.md

# Verify agent has memory_ingest tool
cat .claude/agents/memory-ingest.md | grep tools
```

**3. Verify same Core account:**
```
# Ensure not signed in to different account
# Check https://core.heysol.ai account email
```

---

### "Contradictory information in searches"

**Symptom:** Search returns conflicting results

**Explanation:** This is **expected behavior** - Core tracks evolution over time

**Example:**
```
2025-09-01: "Prefer Vue for frontend"
2025-10-31: "Prefer React for frontend"
```

**Both are stored with timestamps** showing preference changed.

**Solution:**
- Review timestamps to understand timeline
- Update outdated information explicitly if needed
- Use temporal filters to get recent preferences only

---

## Performance Issues

### "Searches are slow"

**Symptom:** memory_search takes >5 seconds

**Causes:**

**1. Large knowledge graph**
- Expected with 1000s of entries
- First search slower (cold start)
- Subsequent searches faster

**2. Complex queries**
- Graph traversal queries take longer
- Semantic search slower than keyword

**Solutions:**
- Use more specific queries
- Prefer keyword search when possible
- Consider pruning old/irrelevant data

---

### "Memory ingest timeouts"

**Symptom:** Storing large amounts fails or times out

**Cause:** Trying to ingest massive text blocks

**Solution:**
```
# Instead of: entire file contents
# Store: conceptual summary

# BAD:
Store 5000 lines of code

# GOOD:
Store: "Authentication module uses JWT with RS256 signing.
Refresh tokens in httpOnly cookies. Access tokens expire in 15min."
```

---

## Self-Hosted Issues

### "Docker containers won't start"

**Symptom:** `docker compose up -d` fails

**Diagnostic:**

**1. Check Docker running:**
```bash
docker ps
# Should not error
```

**2. Check ports available:**
```bash
# Verify port 3000 not in use
lsof -i :3000
```

**3. Check .env file:**
```bash
cat .env
# Must contain OPENAI_API_KEY
```

**4. Check Docker Compose version:**
```bash
docker compose version
# Must be 2.20.0+
```

**Solution:**
```bash
# View logs for specific error
docker compose logs

# Try rebuilding
docker compose down
docker compose up --build -d
```

---

### "Cannot connect to self-hosted instance"

**Symptom:** MCP configured but can't reach localhost

**Diagnostic:**

**1. Verify containers running:**
```bash
docker compose ps
# All should show "Up"
```

**2. Test endpoint directly:**
```bash
curl http://localhost:3000/api/v1/mcp
# Should return response (may be error about auth, but connection works)
```

**3. Check URL in .mcp.json:**
```bash
cat .mcp.json | grep url
# Should be: http://localhost:3000/api/v1/mcp?source=Claude-Code
```

**4. Firewall blocking:**
```bash
# On macOS
# System Settings → Network → Firewall
# Ensure Docker allowed
```

---

## Agent Issues (Automatic Memory)

### "memory-search agent not auto-running"

**Symptom:** Agent exists but doesn't trigger at session start

**Diagnostic:**

**1. Verify file location:**
```bash
ls .claude/agents/memory-search.md
# Must be exactly at this path
```

**2. Check YAML frontmatter:**
```bash
head -n 10 .claude/agents/memory-search.md
```

**Should contain:**
```yaml
---
name: Core Memory Search
description: Automatically retrieve...
tools: [mcp__core-memory__memory_search]
---
```

**3. Verify tool name exact:**
```
# Must be exactly: mcp__core-memory__memory_search
# With double underscores
```

**4. Restart Claude Code:**
```
# Agents loaded at startup
# Must restart after adding/modifying agents
```

---

### "memory-ingest agent stores too much"

**Symptom:** Agent storing code blocks, logs, unnecessary data

**Solution:**

**Edit `.claude/agents/memory-ingest.md`:**

Add stricter exclusion rules in agent instructions:

```markdown
## What NOT to Store

- Code blocks (use git instead)
- Command outputs
- File listings
- Logs
- Stack traces
- Test output
```

Or remove agent temporarily if causing issues:
```bash
mv .claude/agents/memory-ingest.md .claude/agents/memory-ingest.md.disabled
```

---

## Getting Help

### Support Channels

**Discord (Recommended):**
- Join: https://discord.gg/YGUZcvDjUa
- Channel: #core-support
- Response time: Usually within hours

**Email:**
- General: manik@poozle.dev
- Security: harshith@poozle.dev

**GitHub Issues:**
- Repository: https://github.com/RedPlanetHQ/core
- For bugs and feature requests

### Information to Provide

When asking for help, include:

```
1. Symptom description
2. What you were trying to do
3. Output from: python3 scripts/verify_connection.py
4. Relevant .mcp.json content (redact credentials)
5. Error messages (complete output)
6. Environment: OS, Claude Code version, Docker version (if self-hosted)
```

---

## Prevention Best Practices

**Setup:**
- Use automated scripts (setup_core_cloud.py)
- Verify with diagnostic tools
- Test with simple searches before complex usage

**Maintenance:**
- Review memory monthly
- Update outdated information
- Prune irrelevant data
- Keep Core updated (self-hosted)

**Security:**
- Use OAuth, not API keys
- Never commit credentials to git
- Use environment variables
- Review connected integrations quarterly

**Debugging:**
- Enable verbose logging
- Check official docs for updates
- Test in isolated environment first
- Document custom configurations

## Further Reading

- Configuration Reference: mcp-configuration.md
- Core Concepts: core-concepts.md
- Integration Setup: integrations.md
- Official troubleshooting: docs.heysol.ai/troubleshooting
