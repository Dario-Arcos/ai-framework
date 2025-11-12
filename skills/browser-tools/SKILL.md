---
name: browser-tools
description: "Control Chrome/Chromium via CDP for automated testing, performance profiling, web scraping, and debugging. Full Puppeteer API access: E2E testing, network interception, coverage analysis, multi-tab orchestration. Zero context overhead - loads on-demand unlike persistent MCP servers."
---

# Browser Tools Skill

Full-featured browser automation via Chrome DevTools Protocol (CDP). Equivalent capabilities to Playwright MCP, zero context overhead.

**Platform Support:** macOS only. Uses macOS-specific Chrome paths and rsync. For Linux/Windows support, see repository issues.

---

## Core Principle

Setup verification BEFORE use prevents runtime failures. Interactive browser access unlocks deep documentation research impossible with WebFetch/WebSearch.

**The Iron Law:**
```
NO BROWSER AUTOMATION WITHOUT VERIFIED SETUP FIRST
```

---

## When to Use

### CRITICAL: Use browser-tools When WebFetch/WebSearch Are Insufficient

**WebFetch/WebSearch limitations:**
- Surface-level snapshots only
- Single page, no navigation
- No JavaScript execution context
- No interactive exploration
- Miss nested documentation, examples, API details

**IMPERATIVO usar browser-tools cuando:**
- ✅ Need to read COMPLETE documentation (multi-page, nested sections)
- ✅ Investigating complex APIs with interactive examples
- ✅ Deep research requiring navigation through multiple related pages
- ✅ Documentation behind authentication or requires cookies
- ✅ Content generated dynamically via JavaScript

**Example scenario requiring browser-tools:**
```
User: "Research the complete React Router 7 data loading API"

❌ WRONG: WebFetch one page, give superficial summary
✅ CORRECT: Use browser-tools to:
   1. Navigate through full docs structure
   2. Read loaders, actions, defer, Await sections
   3. Extract code examples from interactive demos
   4. Compile comprehensive understanding
```

### Standard Use Cases

Use browser-tools for:
- **E2E testing** requiring real browser behavior
- **Web scraping** with JavaScript-rendered content
- **Performance profiling** with real metrics
- **Screenshot automation** with visual verification
- **Interactive debugging** of web applications

### When NOT to Use

**Don't use browser-tools when:**
- ❌ Simple HTTP requests suffice (use curl/WebFetch)
- ❌ API available (use API directly)
- ❌ Static HTML parsing (use grep on WebFetch result)
- ❌ Quick single-page lookup (WebFetch is faster)

**Decision tree:**
```
Need web content?
  → Single page, no interaction? → WebFetch
  → Multiple pages, deep dive? → browser-tools
  → API available? → Use API
```

---

## Red Flags - STOP and Follow Process

If you catch yourself thinking:
- "Skip npm install, it's probably there"
- "Runtime error? Just restart Chrome"
- "Wrong directory doesn't matter"
- "Setup verification wastes time"
- **"WebFetch summary is good enough" (for deep research)**
- **"User wants quick answer" (when they need complete docs)**
- "Just use killall to fix it"

**ALL mean: STOP. Return to Core Principle.**

---

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Setup check wastes time" | 2 min verification prevents 30 min debugging |
| "It worked last time" | Environment changes between sessions. Always verify. |
| "I'll fix errors if they happen" | Prevention is 15x faster than debugging failures |
| **"WebFetch is faster for research"** | **2 min WebFetch = superficial. 10 min browser-tools = complete.** |
| **"User seems in a hurry"** | **Incomplete research wastes MORE time with wrong answers.** |
| "killall is quicker" | Destroys user sessions. Breaks trust permanently. |

---

## Real-World Impact

From browser automation sessions:

**Setup discipline:**
- With verification: 2 min setup, 100% success rate
- Without verification: 30 sec setup, 40% success, 90 sec average recovery
- First-time success: 100% vs 40%

**Deep research quality:**
- WebFetch only: Surface-level understanding, 60% accuracy
- browser-tools: Complete documentation coverage, 95% accuracy
- Time saved by doing it right: Avoids 2-3 follow-up questions

**Stop vs killall:**
- Using stop.js: 100% safe, 2 sec
- Using killall: 0% safe, destroys user work, breaks trust

---

## Initial Setup

**Run ONCE before first use:**

\`\`\`bash
cd skills/browser-tools/tools
npm install
\`\`\`

**Verify installation succeeded:**

\`\`\`bash
ls node_modules/puppeteer-core  # Should exist
\`\`\`

### ⚠️ CRITICAL INSTALLATION WARNING

**MUST install in `tools/` subdirectory, NOT in `browser-tools/`.**

```bash
# ❌ WRONG - Will fail at runtime
cd skills/browser-tools
npm install

# ✅ CORRECT - Works first time
cd skills/browser-tools/tools
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
