# AI Framework

**Transform any project into an AI-first development environment in 30 seconds.**

Constitutional SDD governance · Specialized agents · Intelligent hooks · Zero configuration

---

## Why This Exists

**Orchestration architecture for AI-first development with constitutional quality enforcement.**

Not a tool collection—a **system that creates systems** through specialized agents, phase-gated workflows, constitutional rules, and intelligent hooks.

**Foundation:**

- **Constitutional Governance** — Value/complexity ≥2x, TDD mandatory, complexity budgets enforced
- **Specification-Driven Development** — Spec → Plan → Tasks → Implementation with quality checkpoints
- **Orchestrated Execution** — Agents + skills + commands + hooks + MCP servers working in concert

ROI ≥ 2x · TDD mandatory · Complexity budgets—**enforced**, not suggested.

[Constitution →](https://github.com/Dario-Arcos/ai-framework/blob/main/template/.specify/memory/constitution.md)

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
├── .mcp.json              # MCP servers (gitignored by default)
├── .claude/
│   ├── settings.local.json  # Personal configuration (max priority)
│   └── rules/               # 5 governance files
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
- **MCP Servers** — Playwright (browser automation), Shadcn (UI components)

---

## Customization

**Framework provides defaults. You control overrides.**

Create these files for personal customizations (auto-gitignored, never overwritten):

- **`.claude/settings.local.json`** — Personal settings ([precedence](https://docs.claude.com/en/docs/claude-code/settings): local > shared)
- **`CLAUDE.local.md`** — Personal instructions ([pattern](https://www.anthropic.com/engineering/claude-code-best-practices))
- **`.claude/.mcp.json`** — Personal MCP servers ([precedence](https://docs.claude.com/en/docs/claude-code/mcp): local > plugin)

**Precedence:** local > shared > plugin. Personal configs override framework defaults without conflicts.

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

**Version:** 2.0.0 | **Changelog:** [CHANGELOG.md](CHANGELOG.md)

Contributions welcome via [GitHub Issues](https://github.com/Dario-Arcos/ai-framework/issues)

---

**Made by [Dario Arcos](https://github.com/Dario-Arcos)**
