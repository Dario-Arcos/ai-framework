---
name: browser-automation
description: "Control Chrome/Chromium via CDP for automated testing, performance profiling, web scraping, and debugging. Full Puppeteer API access: E2E testing, network interception, coverage analysis, multi-tab orchestration. Zero context overhead - loads on-demand unlike persistent MCP servers."
---

# Browser Automation Skill

Full-featured browser automation via Chrome DevTools Protocol (CDP). Equivalent capabilities to Playwright MCP, zero context overhead.

**Platform Support:** macOS only. Uses macOS-specific Chrome paths and rsync. For Linux/Windows support, see repository issues.

## Initial Setup

**Run ONCE before first use:**

\`\`\`bash
cd skills/browser-automation/tools
npm install
\`\`\`

**Verify installation succeeded:**

\`\`\`bash
ls node_modules/puppeteer-core  # Should exist
\`\`\`

### ⚠️ CRITICAL INSTALLATION WARNING

**MUST install in `tools/` subdirectory, NOT in `browser-automation/`.**

```bash
# ❌ WRONG - Will fail at runtime
cd skills/browser-automation
npm install

# ✅ CORRECT - Works first time
cd skills/browser-automation/tools
npm install
```

**Why it matters:** Scripts expect relative path `./node_modules/puppeteer-core`. Wrong location = runtime failure requiring full restart.

### Why Setup Verification Matters (Real Timing)

| Approach | Initial Time | Failure Recovery | Total Time | Success Rate |
|----------|-------------|------------------|------------|--------------|
| Skip verification | 30 sec | 90 sec debug + restart | 2+ min | 40% |
| Verify setup (ls node_modules/) | 2 min | 0 sec (works first time) | 2 min | 100% |

**Under pressure, setup verification is faster than debugging failures.**

## Start Chrome

\`\`\`bash
./tools/start.js              # Fresh profile
./tools/start.js --profile    # Copy your profile (cookies, logins)
\`\`\`

Start Chrome on `:9223` with remote debugging (isolated from your main Chrome sessions).

## Navigate

\`\`\`bash
./tools/nav.js https://example.com
./tools/nav.js https://example.com --new
\`\`\`

Navigate current tab or open new tab.

## Evaluate JavaScript

\`\`\`bash
./tools/eval.js 'document.title'
./tools/eval.js 'document.querySelectorAll("a").length'
./tools/eval.js 'JSON.stringify(Array.from(document.querySelectorAll("a")).map(a => ({ text: a.textContent.trim(), href: a.href })).filter(link => !link.href.startsWith("https://")))'
\`\`\`

Execute JavaScript in active tab (async context).  Be careful with string escaping, best to use single quotes.

## Screenshot

\`\`\`bash
./tools/screenshot.js
\`\`\`

Screenshot current viewport, returns temp file path

## Pick Elements

\`\`\`bash
./tools/pick.js "Click the submit button"
\`\`\`

Interactive element picker. Click to select, Cmd/Ctrl+Click for multi-select, Enter to finish.

## Stop Chrome

\`\`\`bash
./tools/stop.js
\`\`\`

Safely stops the debugging Chrome instance on `:9223` without touching your main Chrome sessions.

### ⚠️ CRITICAL: NEVER Use killall

**NEVER use `killall "Google Chrome"`** - it closes ALL your Chrome sessions:
- ❌ Personal browsing tabs (work, email, social)
- ❌ Other development sessions
- ❌ Unsaved form data
- ❌ Active downloads
- ❌ **User trust when you destroy their work**

**ALWAYS use `./tools/stop.js`** - it ONLY closes the debugging instance on port `:9223`.

**Why this matters:** Running `killall` under pressure to "just get it working" destroys user sessions and breaks trust. The extra 2 seconds to use `stop.js` prevents catastrophic data loss.
