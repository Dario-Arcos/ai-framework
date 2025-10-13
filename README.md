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

## Project Structure

This repository is a **monorepo** containing both the plugin and its documentation:

```
ai-framework/
├── .claude-plugin/          # Plugin source code
│   ├── hooks/               # 7 intelligent hooks (Python)
│   ├── commands/            # 24 slash commands (Markdown)
│   ├── agents/              # 45 specialized agents
│   └── template/            # Files installed in user projects
├── .github/workflows/       # CI/CD automation
│   ├── deploy.yml           # Auto-deploy docs to GitHub Pages
│   ├── claude-code-review.yml  # Security-first PR reviews
│   └── claude.yml           # Interactive Claude on @mentions
├── human-handbook/          # VitePress documentation site
│   ├── .vitepress/          # Build configuration
│   ├── docs/                # Markdown documentation
│   └── public/              # Static assets
├── docs/                    # Technical architecture docs
├── package.json             # VitePress dependency (docs only)
└── README.md                # You are here
```

**Why monorepo?**

- Plugin and docs share lifecycle (versioning, releases)
- Single source of truth for documentation
- Simplified CI/CD (one repo to maintain)

---

## Security Considerations

### npm Dependencies (Documentation)

The documentation uses VitePress 1.6.4, which currently shows 3 moderate severity vulnerabilities in its dev dependencies (esbuild).

**Conscious decision:** We've opted NOT to apply `npm audit fix` because:

1. **Risk is development-only:** Vulnerabilities affect the dev server (`npm run docs:dev`), not production builds
2. **Fix breaks the project:** The suggested fix downgrades VitePress from 1.6.4 to 0.1.1 (67 versions back), which would break all modern features
3. **Controlled environment:** The dev server is only used by maintainers in local environments
4. **GitHub Actions safety:** Our CI/CD only runs `npm run docs:build`, never the dev server

**Mitigation:**

- Production builds (`human-handbook/.vitepress/dist/`) are unaffected
- Dev server usage is restricted to maintainer's local machine
- Monitoring upstream (VitePress/esbuild) for proper fixes

This follows industry best practices (Next.js, Vite, Tailwind all accept similar dev-only risks rather than breaking their toolchains).

---

## License

MIT License — See [LICENSE](LICENSE)

**Version:** 1.0.0 (Unreleased) | **Changelog:** [CHANGELOG.md](CHANGELOG.md)

Contributions welcome via [GitHub Issues](https://github.com/Dario-Arcos/ai-framework/issues)

---

**Made by [Dario Arcos](https://github.com/Dario-Arcos)**
