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

If you see "No such file or directory", you installed in the wrong location. Must be in `tools/` subdirectory, not in `skills/browser-automation/`.

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

**⚠️ CRITICAL WARNING:** Do NOT use `killall "Google Chrome"` - it will close ALL your Chrome windows (personal and debugging). Always use `./tools/stop.js` instead.
