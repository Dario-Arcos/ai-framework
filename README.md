# AI Framework

**Production-ready AI-first development ecosystem** for Claude Code.

Constitutional governance · 40+ specialized agents · Intelligent hooks · Workflow automation

---

## What Is This?

A complete, plug-and-play framework that transforms any project into an AI-first development environment. Install once, get:

- ✅ **Constitutional Governance** (Value/Complexity ratio, TDD enforcement, Complexity budgets)
- ✅ **40+ Specialized AI Agents** (Architecture, Testing, DevOps, Security, Documentation, UX)
- ✅ **22 Slash Commands** (Git/GitHub workflows, SDD cycle, Documentation automation)
- ✅ **Intelligent Hooks** (Security guards, Code formatters, TDD enforcement, Notifications)
- ✅ **MCP Servers** (Playwright for E2E testing, Shadcn/ui for components)

**Framework-agnostic** · Works with any tech stack · Zero vendor lock-in

---

## Quick Install

```bash
# 1. Clone this framework
git clone https://github.com/Dario-Arcos/ai-framework.git
cd ai-framework

# 2. Navigate to your project
cd /path/to/your/project

# 3. Install
~/ai-framework/install.sh

# 4. Complete plugin setup
claude add plugin
# Select: ai-framework

# 5. Start coding!
claude
```

**Installation time:** ~2 minutes

---

## What Gets Installed

### Configuration Files

```
your-project/
├── CLAUDE.md                    # Project-level configuration
├── .mcp.json                    # MCP servers (Playwright, Shadcn)
├── .claude/
│   ├── settings.json            # Hooks orchestrator
│   └── rules/                   # 5 governance files
│       ├── project-context.md           # Always Works™ methodology
│       ├── effective-agents-guide.md    # Context engineering
│       ├── datetime.md
│       ├── github-operations.md
│       └── worktree-operations.md
└── .specify/
    ├── memory/                  # Constitutional documents
    │   ├── constitution.md              # Core principles
    │   ├── product-design-principles.md # Steve Jobs philosophy
    │   └── uix-design-principles.md     # S-Tier SaaS checklist
    ├── scripts/bash/            # Utility scripts (5 files)
    └── templates/               # Templates (5 files)
```

### Plugin Components (via Claude Code)

- **44 Agents** organized in 13 categories
- **22 Commands** organized in 4 modules
- **5 Hooks** (Python scripts for enforcement)

---

## Core Principles

This framework enforces **5 non-negotiable principles**:

1. **AI-First**: Everything executable by AI with human oversight
2. **Value/Complexity**: ROI ≥ 2x implementation complexity
3. **Test-First Development**: TDD mandatory (Red-Green-Refactor)
4. **Complexity Budget**: S≤80LOC | M≤250LOC | L≤600LOC (net change)
5. **Reuse First**: Library-first, avoid abstractions <30% justification

Full governance: [`.specify/memory/constitution.md`](template/.specify/memory/constitution.md)

---

## Usage

### Available Commands

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

# Documentation
/utils:docs             # Update documentation
/utils:changelog        # Auto-generate changelog

# Research
/utils:deep-research    # Professional investigation
/utils:three-experts    # 3-expert panel workflow
```

See all: Type `/help` in Claude Code

### Agent Categories

- **Architecture & System Design** (8 agents)
- **Code Review & Security** (5 agents)
- **Testing & Debugging** (4 agents)
- **DevOps & Deployment** (4 agents)
- **Documentation** (5 agents)
- **Performance & Observability** (3 agents)
- **Database Management** (2 agents)
- **Shadcn-UI Components** (4 agents)
- **UX & Design** (3 agents)
- **Web & Application** (5 agents)
- **Incident Response** (2 agents)

---

## Validation

Verify installation integrity:

```bash
cd /path/to/your/project
~/ai-framework/validate.sh
```

Checks:

- ✓ All configuration files present
- ✓ JSON files valid
- ✓ All governance rules installed
- ✓ Plugin registered

---

## Architecture

### Hybrid Distribution Model

```
Framework Repository
├── plugin/                  # Official Plugin (commands/agents/hooks)
│   └── .claude-plugin/
│       ├── plugin.json
│       ├── agents/          (44 files)
│       ├── commands/        (22 files)
│       ├── hooks/           (5 scripts)
│       └── .mcp.json
│
└── template/                # Configuration Templates
    ├── CLAUDE.md
    ├── .claude/
    │   ├── settings.json
    │   └── rules/
    └── .specify/
```

**Why Hybrid?**

- Uses official plugin system where supported (agents, commands, hooks)
- Direct file distribution for unsupported items (settings, constitution)
- One-command installation for complete ecosystem

---

## Requirements

### Critical (Required)

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code/installation)
- [Git](https://git-scm.com/downloads)
- [Python 3.8+](https://www.python.org/downloads/)

### Essential (Full Functionality)

- [GitHub CLI](https://cli.github.com/) - for git/github commands
- [Node.js 18+](https://nodejs.org/) - for MCPs and formatters

### Optional

- Python formatters: Black, Ruff, or autopep8
- Prettier (auto-installed via npx)
- shfmt (Bash formatter)
- jq (JSON processor)

---

## Troubleshooting

| Issue                     | Solution                                     |
| ------------------------- | -------------------------------------------- |
| Plugin not appearing      | `claude add plugin`, select from marketplace |
| Settings.json not loading | Restart Claude Code                          |
| Hooks not executing       | Check Python 3 installation                  |
| Commands not visible      | Type `/help` to refresh command list         |

---

## Contributing

This framework is open for contributions:

1. Fork the repository
2. Create feature branch
3. Follow constitutional principles (see `.specify/memory/constitution.md`)
4. Submit PR with clear description

---

## License

MIT License - See [LICENSE](LICENSE)

Contributions and feedback welcome via [GitHub Issues](https://github.com/Dario-Arcos/ai-framework/issues).

---

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute getting started
- **[Constitution](template/.specify/memory/constitution.md)** - Core principles
- **[Always Works™](template/.claude/rules/project-context.md)** - Quality methodology
- **[Effective Agents](template/.claude/rules/effective-agents-guide.md)** - Context engineering

---

## Version

**Current:** 1.0.0

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**Made with ❤️ by [Dario Arcos](https://github.com/Dario-Arcos)**
