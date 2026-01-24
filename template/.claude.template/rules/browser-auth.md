# Browser Authentication

## Critical Context

`agent-browser` uses isolated Chromium. No access to user's Chrome sessions or saved logins.

## OAuth/SSO Authentication Rule

**MANDATORY**: When authentication requires OAuth, SSO, Google login, or any third-party auth flow:

```bash
# 1. Clean previous sessions
agent-browser close 2>/dev/null

# 2. Open VISIBLE browser (--headed is REQUIRED)
agent-browser --headed open https://site.com/login

# 3. Inform user and WAIT for confirmation
# Say: "Browser abierto. Por favor haz login manualmente y confirma cuando estés listo."

# 4. Only after user confirms "listo" → continue automation
```

## Decision Flow

```
Is login required?
    ↓
Is it OAuth/SSO/Google/third-party?
    ├─ YES → Use --headed, ask user to login manually, wait for confirmation
    └─ NO (simple form) → Can automate with fill commands
```

## What NOT to Do

- ❌ Never attempt to automate OAuth flows (Google, GitHub, etc.)
- ❌ Never use headless mode for OAuth (will fail or get blocked)
- ❌ Never proceed without user confirmation after manual login
- ❌ Never assume session persists after `agent-browser close`

## Session Lifecycle

| Action | Result |
|--------|--------|
| `--headed open` | Session starts, browser visible |
| User logs in | Session authenticated |
| `state save file.json` | Session persisted to disk |
| `agent-browser close` | Session destroyed (unless saved) |
| `state load file.json` | Session restored |

## Persist Sessions (Optional)

After user completes manual login:

```bash
# Save for future use
agent-browser state save ./site-auth.json

# Later sessions - skip manual login
agent-browser state load ./site-auth.json
agent-browser open https://site.com/dashboard
```

**Security**: Never commit `*-auth.json` files. Add to `.gitignore`.

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `AGENT_BROWSER_SESSION` | Named session for parallel browsers |
| `AGENT_BROWSER_PROXY` | Proxy server URL |
