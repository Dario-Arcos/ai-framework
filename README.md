# AI Framework

**Transform any project into an AI-first development environment in 30 seconds.**

Constitutional SDD governance · Specialized agents · Intelligent hooks · Zero configuration

---

## Why This Framework Exists

**Claude Code is extraordinary. This framework makes it indispensable.**

### The Problem

**Claude Code vanilla** gives you access to world-class AI capable of writing code, analyzing systems, and executing commands. A universe of incredible possibilities.

**But there's a critical gap:** Without structure, without methodology, without "rails"—that power gets wasted.

**Symptoms:**
- Code that "works" but fails in production
- No tests, inconsistent architecture
- Brilliant ideas → fragile implementations
- AI as "advanced assistant" instead of "autonomous engineer"

### The Solution

**This framework transforms Claude Code from powerful tool into disciplined engineering system.**

**Not configuration—governance:**

- **Research-backed** — Integrates Anthropic context engineering, DeepMind LLM optimization, industry TDD practices
- **Constitutional enforcement** — Value/complexity ≥2x, TDD mandatory, complexity budgets (S≤80|M≤250|L≤600 Δ LOC)
- **Production-ready** — Not demos. Real software engineering guided by humans, executed by AI.
- **Orchestrated execution** — 45 agents + 26 commands + 5 hooks + 23 skills working in concert

**Result:** Claude Code stops being "assistant" and becomes **autonomous engineer** with scientific rigor.

### The Vision

> **Transform the complete lifecycle of digital products into an automated, high-quality process with compliance and versatility—freeing brilliant minds to make their ideas reality in record time without sacrificing quality, scalability, security, or potential.**

**Framework guarantees:**
- ✅ Production-ready quality (tests from day 1)
- ✅ Scalability by default (coherent architecture)
- ✅ Automatic security (vulnerability scanning)
- ✅ Constitutional compliance (enforced, not suggested)
- ✅ Velocity without friction (AI executes, framework validates)

**This framework isn't optional. It's indispensable.**

[Why AI Framework? →](https://dario-arcos.github.io/ai-framework/why-ai-framework) | [Constitution →](https://github.com/Dario-Arcos/ai-framework/blob/main/template/.specify/memory/constitution.md)

---

## Requirements

**Critical:**

- **Git** 2.0+ ([download](https://git-scm.com/downloads))
- **Claude Code CLI** 0.5.0+ ([installation](https://docs.claude.com/en/docs/claude-code/installation))
- **Python** 3.8+ (hooks and scripts)

**Essential:**

- **GitHub CLI (gh)** — Git/GitHub workflows
- **Node.js** 18+ — Documentation and MCP servers

**Optional:**

- **terminal-notifier** (macOS) — Desktop notifications
- Python formatters (black, ruff, autopep8)
- Prettier, shfmt, jq

---

## Quick Install

**Step 1: Install Claude Code CLI**

Follow the [official installation guide](https://docs.claude.com/en/docs/claude-code/installation) for your platform.

**Step 2: Add Marketplace**

```bash
/plugin marketplace add Dario-Arcos/ai-framework
```

**Step 3: Install Plugin**

```bash
/plugin install ai-framework@ai-framework
```

**Step 4: Start in Your Project**

```bash
cd /path/to/your/project
claude
# Framework auto-installs on first session
```

**Installation complete.** See Post-Installation for configuration steps.

[Official plugin documentation →](https://docs.claude.com/en/docs/claude-code/plugins)

---

## Post-Installation

**Step 1: Restart Claude Code** (Required)

Exit and reopen Claude Code to load the framework.

**Step 2: Initialize Project Context** (Critical)

```bash
/ai-framework:utils:project-init
```

Analyzes stack (languages, frameworks, databases), generates `project-context.md`, and configures specialized agent recommendations for your codebase.

**Step 3: Install Optional Dependencies**

```bash
/ai-framework:utils:setup-dependencies
```

Auto-detects and installs optional tools (terminal-notifier, formatters like black/ruff/prettier).

---

## What Gets Installed

### Framework Installation Structure

The framework adds these files/directories to your **existing project structure**:

```
your-project/              # Your existing project root
├── [your existing files]  # Your code, package.json, etc.
├── CLAUDE.md              # Project configuration (gitignored by default)
├── .claude/
│   ├── settings.json        # Framework defaults (synced from plugin)
│   ├── settings.local.json  # Personal overrides (optional, max priority)
│   └── rules/               # 3 governance files (datetime, agents-guide, operational-excellence)
└── .specify/
    ├── memory/              # Constitutional documents (constitution.md, project-context.md)
    ├── scripts/bash/        # Utility scripts
    └── templates/           # Workflow templates (spec, plan, tasks)
```

### Plugin Components (via Claude Code)

- **Agents** — Architecture, Security, Testing, DevOps, Database, Documentation, UX/Design, Performance
- **Skills** — Algorithmic art, Claude Code expert, Skill creator
- **Commands** — SDD cycle, Git/GitHub automation, Project utilities
- **Hooks** — SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, Stop
- **MCP Servers** — Playwright (browser automation), Shadcn (UI components) — Configured in plugin root, not project

---

## Customization

**Framework provides defaults. You control overrides.**

### Settings Architecture (v2.0+)

- **`.claude/settings.json`** — Framework defaults (synced from plugin, auto-updated)
- **`.claude/settings.local.json`** — Personal overrides (optional, **never touched by framework**)

**Precedence:** `settings.local.json` > `settings.json`. Personal settings always win.

### MCP Servers Architecture (v2.0+)

- **Plugin `.mcp.json`** — Framework MCP servers (Playwright, Shadcn)
- **Project `.mcp.json`** — Custom MCP servers (optional, user-defined)

**Precedence:** project > plugin. Add custom servers without touching framework defaults.

[MCP documentation →](https://docs.claude.com/en/docs/claude-code/mcp)

### Personal Instructions

- **`CLAUDE.local.md`** — Personal instructions (optional, auto-gitignored)

[Best practices →](https://www.anthropic.com/engineering/claude-code-best-practices)

---

## Core Principles

Framework enforces **5 non-negotiable principles**:

| Principle             | Enforcement                                          |
| --------------------- | ---------------------------------------------------- |
| **AI-First**          | Everything executable by AI with human oversight     |
| **Value/Complexity**  | ROI ≥ 2x implementation complexity                   |
| **Test-First**        | TDD mandatory (Red-Green-Refactor)                   |
| **Complexity Budget** | S≤80LOC \| M≤250LOC \| L≤600LOC (net change)         |
| **Reuse First**       | Library-first, avoid abstractions <30% justification |

Full governance: [constitution.md](https://github.com/Dario-Arcos/ai-framework/blob/main/template/.specify/memory/constitution.md)

---

## Documentation

**[Full Documentation →](https://dario-arcos.github.io/ai-framework/)**

**Key Guides:**

- [Quickstart](https://dario-arcos.github.io/ai-framework/quickstart) — 15 minutes to productive
- [MCP Servers](https://dario-arcos.github.io/ai-framework/mcp-servers) — Extend Claude Code capabilities
- [Commands Guide](https://dario-arcos.github.io/ai-framework/commands-guide) — Slash commands reference
- [Agents Guide](https://dario-arcos.github.io/ai-framework/agents-guide) — Specialized agents catalog

Constitution · Always Works™ methodology · Context engineering · Design principles

---

## Troubleshooting

| Issue                | Solution                                     |
| -------------------- | -------------------------------------------- |
| Plugin not appearing | `claude add plugin`, select from marketplace |
| Settings not loading | Restart Claude Code                          |
| Hooks not executing  | Check Python 3 installation                  |
| Commands not visible | Type `/help` to refresh                      |

---

## License

MIT License — See [LICENSE](LICENSE)

**Version:** 2.2.0 | **Changelog:** [CHANGELOG.md](CHANGELOG.md)

Contributions welcome via [GitHub Issues](https://github.com/Dario-Arcos/ai-framework/issues)

---

**Made by [Dario Arcos](https://github.com/Dario-Arcos)**
