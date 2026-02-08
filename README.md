# AI Framework

**Transform any project into an AI-first development environment in 30 seconds.**

Constitutional SDD governance · Specialized agents · Intelligent hooks · Zero configuration

---

## Why This Framework Exists

**Claude Code is extraordinary. This framework makes it indispensable.**

Without structure, Claude Code's power gets wasted: code that "works" but fails in production, no tests, inconsistent architecture. Brilliant ideas become fragile implementations.

**This framework transforms AI from assistant to autonomous engineer:**

- **Research-backed governance** — Anthropic context engineering, DeepMind LLM optimization, SDD enforcement
- **Constitutional compliance** — Value/complexity ≥2x, complexity budgets (S≤80|M≤250|L≤600 Δ LOC), enforced automatically
- **Production-ready output** — Tests from day 1, vulnerability scanning, coherent architecture
- **Orchestrated execution** — Specialized agents, workflow commands, lifecycle hooks, proven patterns working in concert

> Transform the complete lifecycle of digital products into an automated, high-quality process—freeing brilliant minds to make ideas reality in record time without sacrificing quality, scalability, security, or potential.

[Why AI Framework? →](https://dario-arcos.github.io/ai-framework/docs/why-ai-framework) | [Constitution →](https://github.com/Dario-Arcos/ai-framework/blob/main/template/.specify.template/memory/constitution.md)

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

**1. Install Claude Code CLI** — [Installation guide](https://docs.claude.com/en/docs/claude-code/installation)

**2. Add marketplace and install plugin:**

```bash
/plugin marketplace add Dario-Arcos/ai-framework-marketplace
/plugin install ai-framework@ai-framework-marketplace
```

**3. Start in your project:**

```bash
cd /path/to/your/project
claude  # Framework auto-installs on first session
```

**4. Post-install (required):**

Exit and reopen Claude Code, then initialize:

```bash
/ai-framework:utils:project-init        # Analyzes stack, generates team-shared rules
/ai-framework:utils:setup-dependencies   # Optional: installs formatters, notifier
```

---

## What Gets Installed

Framework adds to your existing project:

```
your-project/
├── CLAUDE.md              # Configuration (gitignored)
├── .claude/
│   ├── settings.json        # Framework defaults (synced)
│   ├── settings.local.json  # Personal overrides (optional)
│   └── rules/               # Governance files
└── .specify/
    ├── memory/              # Constitution, project-context
    ├── scripts/bash/        # Utilities
    └── templates/           # Spec, plan, tasks
```

**Plugin components** (via Claude Code):
- **Specialized agents** — Architecture, Security, Testing, DevOps, and more
- **Workflow skills** — Git/GitHub automation, project utilities, development workflows
- **Proven patterns** — On-demand context engineering patterns
- **Lifecycle hooks** — Session, tool, and prompt lifecycle automation
- **MCP servers** — Optional integrations (opt-in)

---

## Customization

**Framework provides defaults. You control overrides.**

**Settings:** `.claude/settings.local.json` > `settings.json` (personal always wins)

**Integrations:** Optional (zero by default). Use `/plugin install` for official plugins or copy `.mcp.json.template` for mobile MCPs — [Docs](https://dario-arcos.github.io/ai-framework/docs/integrations)

**Personal instructions:** `CLAUDE.local.md` (optional, auto-gitignored) — [Best practices](https://www.anthropic.com/engineering/claude-code-best-practices)

---

## Core Principles

Framework enforces **5 non-negotiable principles**:

| Principle             | Enforcement                                          |
| --------------------- | ---------------------------------------------------- |
| **AI-First**          | Everything executable by AI with human oversight     |
| **Value/Complexity**  | ROI ≥ 2x implementation complexity                   |
| **Scenario-First**    | SDD mandatory (Scenario-Satisfy-Refactor)            |
| **Complexity Budget** | S≤80LOC \| M≤250LOC \| L≤600LOC (net change)         |
| **Reuse First**       | Library-first, avoid abstractions <30% justification |

Full governance: [constitution.md](https://github.com/Dario-Arcos/ai-framework/blob/main/template/.specify.template/memory/constitution.md)

---

## Documentation

**[Full Documentation →](https://dario-arcos.github.io/ai-framework/)**

- [Quickstart](https://dario-arcos.github.io/ai-framework/docs/quickstart) — 15 minutes to productive
- [Skills Guide](https://dario-arcos.github.io/ai-framework/docs/skills-guide) — Skills and workflows reference
- [Agents Guide](https://dario-arcos.github.io/ai-framework/docs/agents-guide) — Specialized agents catalog
- [Integrations](https://dario-arcos.github.io/ai-framework/docs/integrations) — Plugins & MCPs to extend capabilities

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

**Version:** 5.1.2 | **Changelog:** [CHANGELOG.md](CHANGELOG.md)

Contributions welcome via [GitHub Issues](https://github.com/Dario-Arcos/ai-framework/issues)

---

**Made by [Dario Arcos](https://github.com/Dario-Arcos)**
