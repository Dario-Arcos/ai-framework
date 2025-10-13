# AI Framework

**Transform any project into an AI-first development environment in 30 seconds.**

Constitutional SDD governance · 40+ specialized agents · Intelligent hooks · Zero configuration

---

## Why This Exists

Most AI tools suggest. This framework **enforces**.

Not a collection of tools—a complete **development system** built on state-of-the-art AI engineering:

- **Specification-Driven Development (SDD)** — Constitutional enforcement at every gate: Spec → Plan → Tasks → Implementation
- **Context Engineering** — Anthropic's research on attention budgets, just-in-time loading, progressive disclosure
- **Persuasion Architecture** — Prompting strategies that maximize AI output quality
- **Graph-Based Workflows** — Dependencies mapped, parallel execution optimized

Implemented through 40+ specialized agents, 22 slash commands (SDD is core), 5 intelligent hooks, and MCP servers.

ROI ≥ 2x · TDD mandatory · Complexity budgets—**enforced**, not suggested.

[Read the constitution →](https://github.com/Dario-Arcos/ai-framework/blob/main/template/.specify/memory/constitution.md)

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
# Framework auto-installs on first session. Restart Claude Code to load configuration.
```

**Done.** 30 seconds, zero configuration.

[Official plugin documentation →](https://docs.claude.com/en/docs/claude-code/plugins)

---

## What Gets Installed

### Your Project Root

```
your-project/
├── CLAUDE.md                # Project configuration (ignored by default)
├── .mcp.json                # MCP servers (ignored by default)
├── .claude/
│   ├── settings.local.json  # Personal configuration (max priority)
│   └── rules/               # 5 governance files
└── .specify/
    ├── memory/              # Constitutional documents
    ├── scripts/bash/        # Utility scripts
    └── templates/           # Workflow templates
```

**Note:** `CLAUDE.md` and `.mcp.json` are ignored by default. To version control them, uncomment the respective lines in `.gitignore`.

### Plugin Components (via Claude Code)

- **44 Agents** — 13 categories (Architecture, Security, Testing, DevOps...)
- **22 Commands** — 4 modules (SDD cycle, Git/GitHub, Utils, Docs)
- **5 Hooks** — SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, Stop

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

## Requirements

**Critical** (Required)

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code/installation)
- [Git](https://git-scm.com/downloads)
- [Python 3.8+](https://www.python.org/downloads/)

**Essential** (Full Functionality)

- [GitHub CLI](https://cli.github.com/) — Git/GitHub commands
- [Node.js 18+](https://nodejs.org/) — MCPs and formatters

**Optional**

- Python formatters: Black, Ruff, autopep8
- Prettier (auto-installed via npx)
- shfmt, jq

---

## Documentation

**[Full Documentation →](https://dario-arcos.github.io/ai-framework/)**

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

**Version:** 1.0.0 (Unreleased) | **Changelog:** [CHANGELOG.md](CHANGELOG.md)

Contributions welcome via [GitHub Issues](https://github.com/Dario-Arcos/ai-framework/issues)

---

**Made by [Dario Arcos](https://github.com/Dario-Arcos)**
