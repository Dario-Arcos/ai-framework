# Setup Episodic Memory

Install and configure episodic-memory for semantic search of Claude Code conversations.

**What it does:**
- Installs episodic-memory npm package globally
- Creates session-end hook for automatic sync
- Configures retention policy (99999 days)
- Enables MCP server in project settings

**Compatible with team-memory** (different tool names: `search`/`read` vs `memory_search`/`memory_ingest`).

---

## Pre-Check

Before installation, check if already installed:

```bash
episodic-memory --version
```

If command exists:
- Skip installation
- Validate configuration
- Report current status

---

## Installation

### Step 1: Install npm package

```bash
npm install -g github:obra/episodic-memory
```

**On error:**
- Check Node.js ≥18: `node --version`
- Check npm ≥8: `npm --version`
- Verify network connectivity
- Check npm global prefix: `npm config get prefix`

### Step 2: Verify binary

```bash
episodic-memory --version
```

**Expected output:** `episodic-memory/1.x.x`

**If not found:**
- Restart shell: `exec $SHELL`
- Check PATH includes npm global bin: `npm bin -g`
- Verify installation: `npm list -g episodic-memory`

---

## Configuration

### Step 3: Create session-end hook

**File:** `~/.claude/hooks/session-end`

**Content:**
```bash
#!/bin/bash
episodic-memory sync
```

**Actions:**
- Create directory: `mkdir -p ~/.claude/hooks/`
- Write hook script
- Make executable: `chmod +x ~/.claude/hooks/session-end`

**Validate:** File exists and executable (`test -x`)

### Step 4: Configure retention policy

**File:** `.claude/settings.local.json`

**Update:**
```json
{
  "cleanupPeriodDays": 99999
}
```

**Merge strategy:**
- Read existing settings.local.json (if exists)
- Parse JSON (handle JSONDecodeError)
- Merge cleanupPeriodDays
- Preserve all other keys
- Write atomically (temp file + rename)

**Create if missing:** Initialize with empty object `{}`

### Step 5: Enable MCP server

**File:** `.claude/settings.local.json`

**Update:**
```json
{
  "enabledMcpjsonServers": ["episodic-memory"]
}
```

**Merge strategy:**
- Read current enabledMcpjsonServers array
- Add "episodic-memory" if not present
- Preserve other enabled servers
- Write atomically

### Step 6: Verify MCP template

**Check:** `.mcp.json` or `.claude/.mcp.json.template` has episodic-memory config

**Expected:**
```json
{
  "mcpServers": {
    "episodic-memory": {
      "command": "episodic-memory-mcp-server"
    }
  }
}
```

**If missing:**
```
⚠️ MCP configuration not found

Action required:
1. Copy template: cp .claude/.mcp.json.template .mcp.json
2. Or add to existing .mcp.json:
   "episodic-memory": {
     "command": "episodic-memory-mcp-server"
   }
```

---

## Validation

Run these checks before reporting success:

1. ✅ Binary exists: `which episodic-memory`
2. ✅ Hook exists: `test -f ~/.claude/hooks/session-end`
3. ✅ Hook executable: `test -x ~/.claude/hooks/session-end`
4. ✅ Retention configured: grep cleanupPeriodDays .claude/settings.local.json
5. ✅ MCP enabled: grep episodic-memory .claude/settings.local.json

**Do NOT run:** `episodic-memory sync` (can take minutes with large history)

---

## Final Report

```
✅ episodic-memory installed successfully

Configuration:
  • Binary: $(which episodic-memory)
  • Version: $(episodic-memory --version)
  • Hook: ~/.claude/hooks/session-end
  • Retention: 99999 days
  • MCP server: Enabled

⚠️ Restart Required:
  Press Ctrl+D, then run: claude

ℹ️ Compatibility:
  • Works with team-memory (different tools)
  • First sync runs on next session end
  • Use: "Busca en mis conversaciones: <query>"

📚 Documentation:
  • See: human-handbook/docs/memory-systems.md
  • CLI: episodic-memory search "query"
  • Stats: episodic-memory stats
```

---

## Error Diagnostics

### Installation fails

**Check:**
```bash
node --version  # Require ≥18
npm --version   # Require ≥8
npm config get prefix  # Global install location
```

**Common fixes:**
- Install Node.js from nodejs.org
- Use nvm for npm permission issues
- Check network/proxy settings

### Binary not in PATH

**Diagnostic:**
```bash
npm list -g episodic-memory  # Should show installed
npm bin -g  # Check global bin directory
echo $PATH | tr ':' '\n' | grep npm  # Verify in PATH
```

**Fix:** Restart shell or add npm bin to PATH

### Hook creation fails

**Causes:**
- Directory permissions
- Disk space
- ~/.claude/ doesn't exist (run project-init first)

**Action:** Create parent directories, check permissions

### Settings.json corruption

**Validation:**
- Parse JSON before write
- Backup original on error
- Use atomic write (temp file + rename)
- Report syntax errors clearly

---

## Idempotency

Safe to run multiple times:
- Skips if already installed
- Updates configuration if incomplete
- Reports current status
- Never overwrites user data
