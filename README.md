# AI Framework

**Transform any project into an AI-first development environment in 30 seconds.**

Constitutional governance · 40+ specialized agents · Intelligent hooks · Zero configuration

---

## Why This Exists

Most AI tools suggest. This framework **enforces**.

Install once, get a complete ecosystem that **mandates** quality:

- ⚖️ **Constitutional Governance** — Value/Complexity ratio ≥2x, TDD enforcement, Complexity budgets
- 🤖 **40+ Specialized Agents** — Architecture, Security, Testing, DevOps, Documentation, UX
- ⚡ **22 Slash Commands** — Git workflows, SDD cycle, Documentation automation
- 🛡️ **5 Intelligent Hooks** — Security guards, Code formatters, TDD enforcement
- 🎭 **MCP Servers** — Playwright (E2E), Shadcn/ui (Components)

Framework-agnostic · Production-ready · Zero vendor lock-in

---

## Quick Install

```bash
# Install plugin (auto-installs framework on first use)
claude add plugin
# → Select: ai-framework (GitHub marketplace)

# Start Claude Code in your project
cd /path/to/your/project
claude

# Done. Framework installs automatically.
```

**Installation time:** ~30 seconds
**What gets installed:** See [Architecture](#architecture)

---

## What Gets Installed

### Your Project Root

```
your-project/
├── CLAUDE.md                # Project configuration
├── .mcp.json                # MCP servers
├── .claude/
│   ├── settings.json        # Hooks orchestrator
│   └── rules/               # 5 governance files
└── .specify/
    ├── memory/              # Constitutional documents
    ├── scripts/bash/        # Utility scripts
    └── templates/           # Workflow templates
```

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

Full governance: [`.specify/memory/constitution.md`](template/.specify/memory/constitution.md)

---

## Commands

```bash
# Specification-Driven Development
/SDD-cycle:specify      # Create feature spec
/SDD-cycle:plan         # Generate implementation plan
/SDD-cycle:tasks        # Generate task breakdown
/SDD-cycle:implement    # Execute tasks

# Git/GitHub
/git-github:commit      # Intelligent commits
/git-github:pr          # Create pull request
/git-github:issue-manager  # Manage issues

# Documentation & Research
/utils:docs             # Update documentation
/utils:changelog        # Auto-generate changelog
/utils:deep-research    # Professional investigation
/utils:three-experts    # 3-expert panel workflow
```

**See all:** Type `/help` in Claude Code

---

## Agent Categories

**Architecture & System Design** (8)
Backend, Frontend, Cloud, Kubernetes, Mobile, GraphQL, Hybrid Cloud

**Code Review & Security** (5)
Architect Review, Quality Review, Security Review, Edge Case Detection, Config Security

**Testing & Debugging** (4)
TDD Orchestrator, Test Automator, Playwright Generator, Systematic Debugger

**DevOps & Deployment** (4)
Deployment Engineer, Terraform Specialist, DevOps Troubleshooter, DX Optimizer

**Documentation** (5)
API Documenter, Docs Architect, Tutorial Engineer, Reference Builder, Mermaid Expert

**Database** (2)
Database Admin, Database Optimizer

**UX & Design** (3)
Premium UX Designer, Design Review, GSAP Animation Architect

**Shadcn-UI** (4)
Requirements Analyzer, Component Researcher, Implementation Builder, Quick Helper

**Web & Application** (5)
TypeScript, JavaScript, Python, PHP, Ruby specialists

**Performance & Observability** (3)
Observability Engineer, Performance Engineer, Web Search Specialist

**Incident Response** (2)
Incident Responder, Network Engineer

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

- **[Constitution](template/.specify/memory/constitution.md)** — Core principles & governance
- **[Always Works™](template/.claude/rules/project-context.md)** — Quality methodology
- **[Effective Agents](template/.claude/rules/effective-agents-guide.md)** — Context engineering
- **[Product Design](template/.specify/memory/product-design-principles.md)** — Steve Jobs philosophy
- **[UX Design](template/.specify/memory/uix-design-principles.md)** — S-Tier SaaS checklist

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

**Version:** 1.0.0 | **Changelog:** [CHANGELOG.md](CHANGELOG.md)

Contributions welcome via [GitHub Issues](https://github.com/Dario-Arcos/ai-framework/issues)

---

**Made with ❤️ by [Dario Arcos](https://github.com/Dario-Arcos)**
