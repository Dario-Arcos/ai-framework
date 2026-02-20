# Source Routing

## Tool Routing Decision Tree

```
Research question received
├── Is this about a specific API, framework, or library?
│   ├── Yes → Is the library available in Context7?
│   │   ├── Yes → PRIMARY: Context7 (resolve-library-id → query-docs)
│   │   │         FALLBACK: agent-browser (official docs site)
│   │   └── No → PRIMARY: agent-browser (official docs site)
│   │             FALLBACK: agent-browser (GitHub repo)
│   └── No → Does answering require navigating complex web pages?
│       ├── Yes → PRIMARY: agent-browser
│       │         FALLBACK: None (browser is required)
│       └── No → Is this about current events, pricing, or real-time data?
│           ├── Yes → PRIMARY: agent-browser
│           │         FALLBACK: None (live data requires navigation)
│           └── No → PRIMARY: Context7 (if relevant library exists)
│                     FALLBACK: agent-browser
```

## Context7 Usage Patterns

**When to use**: API documentation, framework features, library comparisons, code examples, migration guides.

**Workflow**:
1. Call `resolve-library-id` with the library name and your specific question
2. Select the most relevant library from results (prioritize higher Code Snippet count and Benchmark Score)
3. Call `query-docs` with specific, detailed queries — not vague keywords

**Constraints:**
- You MUST NOT call Context7 tools more than 3 times per sub-question because excessive calls waste the tool budget
- You MUST use specific queries ("How to set up connection pooling in Prisma") not vague ones ("Prisma")
- You MUST extract claims from Context7 responses immediately and discard the raw response
- You SHOULD try Context7 before agent-browser for any API/framework question because it is faster and more focused

## agent-browser Usage Patterns

**When to use**: Complex page navigation, authenticated sources, visual content, real-time data, sources not in Context7.

**Navigation patterns**:

```bash
# Basic navigation
agent-browser open [URL]
agent-browser snapshot -i          # Get interactive snapshot with element labels

# Data extraction
agent-browser click @[element]     # Click labeled element
agent-browser fill @[input] "query" # Fill form field
agent-browser screenshot [name].png # Capture visual evidence

# Session management (for authenticated sources)
agent-browser state save session.json
agent-browser state load session.json
```

**Constraints:**
- You MUST use `snapshot -i` to understand page structure before clicking
- You MUST NOT navigate more than 5 pages per sub-question without extracting claims because excessive navigation wastes time
- You SHOULD capture screenshots for visual data (charts, tables) that cannot be represented as text

## Source Tiers by Research Type

### API/Framework Research

| Tier | Sources | Reliability |
|------|---------|-------------|
| **1 — Primary** | Official documentation (via Context7 or docs site), source code, changelogs | Highest — canonical truth |
| **2 — Authoritative** | GitHub issues/discussions, official blog posts, conference talks by maintainers | High — direct from creators |
| **3 — Community** | Stack Overflow (accepted answers), tutorial sites, community blog posts | Supporting — verify against Tier 1 |

### Technology Decision Research

| Tier | Sources | Reliability |
|------|---------|-------------|
| **1 — Primary** | Published benchmarks (reproducible), official documentation for each option | Highest — measurable claims |
| **2 — Authoritative** | Migration case studies, conference talks comparing options, maintainer statements | High — experienced practitioners |
| **3 — Community** | Blog comparisons, Reddit/HN discussions, developer surveys | Supporting — sentiment data |

### Market/Industry Research

| Tier | Sources | Reliability |
|------|---------|-------------|
| **1 — Primary** | Government/regulatory data (.gov, SEC, central banks), academic peer-reviewed research, official statistics (World Bank, IMF, OECD) | Highest — institutional authority |
| **2 — Authoritative** | Major consulting research (McKinsey, Deloitte, BCG), research firms (Gartner, Forrester, IDC), financial intelligence (Bloomberg, Reuters, FT) | High — professional analysis |
| **3 — Corroborative** | Quality journalism (WSJ, Economist, HBR), industry bodies, corporate reports (10-K, annual reports), expert commentary | Supporting — context and narrative |

### Architecture Research

| Tier | Sources | Reliability |
|------|---------|-------------|
| **1 — Primary** | Source code of reference implementations, architecture decision records (ADRs), technical RFCs | Highest — actual implementations |
| **2 — Authoritative** | Conference talks (StrangeLoop, QCon, GOTO), system design papers, post-mortems from scaled systems | High — battle-tested insights |
| **3 — Community** | Architecture blog posts, design pattern discussions, technology radar entries | Supporting — ideas to verify |

### Current Events Research

| Tier | Sources | Reliability |
|------|---------|-------------|
| **1 — Primary** | Official announcements, press releases, regulatory filings | Highest — direct from source |
| **2 — Authoritative** | Major news outlets (Reuters, AP, Bloomberg), official statements | High — professional journalism |
| **3 — Corroborative** | Analysis articles, expert commentary, social media from verified accounts | Supporting — interpretation |

---

*Reference for: deep-research skill, Steps 1-2*
