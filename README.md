# AI Framework

**Constitutional AI-first development framework for Claude Code.**

Scenario-Driven Development · Specialized agents · Lifecycle hooks · Agent Teams

---

## What It Does

Turns Claude Code into a governed engineering system. Without structure, AI-generated code drifts: no tests, inconsistent architecture, no quality gates. This framework enforces rigor automatically.

- **Scenario-Driven Development (SDD)** — Observable scenarios before code. Tests as validation tool, not authority. Anti-reward-hacking enforcement.
- **Constitutional governance** — Compact constitution installed per-project. Constraints, identity, workflow, and communication rules that survive context compaction.
- **Lifecycle automation** — Hooks across session, tool, notification, and team events: template sync, test guards, background test runners, desktop notifications, Agent Team safety nets.
- **Specialized agents** — Persistent cross-session memory for code review, security, performance, edge cases, debugging, and simplification.
- **Orchestrated execution** — Ralph Orchestrator launches parallel Agent Teams with ephemeral 200K-context teammates for multi-step implementations.

[Why AI Framework?](https://dario-arcos.github.io/ai-framework/docs/why-ai-framework) | [Full Documentation](https://dario-arcos.github.io/ai-framework/)

---

## Requirements

**Required:**

- **Git** 2.0+ ([download](https://git-scm.com/downloads))
- **Claude Code CLI** 0.5.0+ ([installation](https://docs.claude.com/en/docs/claude-code/installation))
- **Python** 3.8+ (hooks — stdlib only, no external dependencies)

**Recommended:**

- **GitHub CLI (gh)** — PR, issue, and release workflows
- **Node.js** 18+ — Documentation site (VitePress)

---

## Install

**1. Install Claude Code CLI** — [Guide](https://docs.claude.com/en/docs/claude-code/installation)

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

**4. Exit and reopen Claude Code, then initialize:**

```bash
/ai-framework:project-init   # Analyzes stack, generates .claude/rules/
```

---

## What Gets Installed

On first session, the `session-start` hook syncs files to your project:

```
your-project/
├── CLAUDE.md                  # Constitutional instructions (gitignored)
└── .claude/
    ├── settings.json          # Framework defaults (synced)
    └── statusline.sh          # Native statusline (model, context %, git, LOC)
```

After running `/project-init`, project-specific rules are generated:

```
.claude/rules/
├── project.md                 # Purpose, domain terms
├── stack.md                   # Runtime, dependencies, scripts
├── architecture.md            # Entry points, layers, data flow
└── conventions.md             # Naming, error handling, style
```

Rules are committed to the repo (shared with team). `CLAUDE.md` and `settings.json` are gitignored (personal).

**Plugin components** (loaded by Claude Code from the plugin):

- **Skills** — Workflow commands invoked by context or slash command
- **Agents** — Autonomous specialists with cross-session memory
- **Hooks** — Lifecycle automation (session, tool, notification, team events)
- **MCP server** — Context7 for up-to-date API documentation

---

## Skills

| Category | Skills |
|----------|--------|
| **Development** | `scenario-driven-development`, `brainstorming`, `frontend-design`, `systematic-debugging`, `verification-before-completion` |
| **SOP Pipeline** | `sop-discovery`, `sop-reverse`, `sop-planning`, `sop-task-generator`, `sop-code-assist`, `sop-reviewer` |
| **Orchestration** | `ralph-orchestrator` |
| **Git/GitHub** | `commit`, `pull-request`, `branch-cleanup`, `worktree-create`, `worktree-cleanup`, `changelog` |
| **Context** | `context-engineering`, `deep-research`, `project-init`, `using-ai-framework` |
| **Utilities** | `skill-creator`, `humanizer` |

Invoke with `/ai-framework:<skill-name>` or let Claude route automatically.

## Agents

| Agent | Purpose |
|-------|---------|
| **code-reviewer** | Validates completed steps against plans, SDD compliance gate, reward-hacking detection |
| **security-reviewer** | Focused security review of branch changes |
| **performance-engineer** | Query inefficiencies, algorithmic complexity, I/O bottlenecks, resource exhaustion |
| **edge-case-detector** | Boundary violations, concurrency bugs, resource leaks, silent failures |
| **systematic-debugger** | Four-phase root cause analysis — no fixes without investigation first |
| **code-simplifier** | Clarity and maintainability refactoring without changing behavior |

All agents use `memory: user` for cross-session knowledge accumulation.

## Hooks

| Event | Hook | Purpose |
|-------|------|---------|
| **SessionStart** | `session-start.py` | Sync templates to project |
| **SessionStart** | `agent-browser-check.py` | Browser daemon health + orphan cleanup |
| **SessionStart** | `memory-check.py` | Project rules staleness detection (4 levels, content hashing) |
| **Stop** | `notify.sh` | macOS desktop notification |
| **Notification** | `notify.sh` | Permission/idle/auth notifications with distinct sounds |
| **TeammateIdle** | `teammate-idle.py` | ABORT detection + circuit breaker for Agent Teams |
| **TaskCompleted** | `task-completed.py` | Quality gate: test, typecheck, lint, build, integration, e2e, coverage |
| **PreToolUse** | `sdd-test-guard.py` | Block edits that reduce assertions when tests fail |
| **PostToolUse** | `sdd-auto-test.py` | Run tests in background after every code edit |

Hooks are Python 3 (stdlib only) and Bash. Full test coverage.

---

## Customization

**Settings:** `.claude/settings.local.json` overrides `settings.json` (personal always wins)

**Integrations:** Zero MCP servers enabled by default (Context7 is plugin-level). Use `/plugin install` for additional plugins — [Docs](https://dario-arcos.github.io/ai-framework/docs/integrations)

**Personal instructions:** `CLAUDE.local.md` (optional, auto-gitignored) — [Best practices](https://www.anthropic.com/engineering/claude-code-best-practices)

---

## Core Methodology

The framework enforces **Scenario-Driven Development (SDD)**:

```
Scenario → Satisfy → Refactor
```

1. **Define observable scenarios** before writing any code
2. **Encode scenarios as failing tests**, then implement until they pass
3. **Refactor** only after all scenarios are satisfied
4. **Anti-reward-hacking**: modifying scenarios to pass or weakening tests to match bugs is explicitly prohibited and enforced by hooks

The `sdd-test-guard` hook blocks edits that reduce test assertions. The `sdd-auto-test` hook runs tests after every code edit and reports results continuously.

---

## Documentation

**[dario-arcos.github.io/ai-framework](https://dario-arcos.github.io/ai-framework/)**

- [Quickstart](https://dario-arcos.github.io/ai-framework/docs/quickstart) — Install to productive in 15 minutes
- [AI-First Workflow](https://dario-arcos.github.io/ai-framework/docs/ai-first-workflow) — 5-phase development lifecycle
- [Skills Guide](https://dario-arcos.github.io/ai-framework/docs/skills-guide) — Complete skills reference with usage triggers
- [Ralph Orchestrator](https://dario-arcos.github.io/ai-framework/docs/ralph-orchestrator) — Agent Teams for multi-step builds
- [Agents Guide](https://dario-arcos.github.io/ai-framework/docs/agents-guide) — Specialized agents catalog
- [Integrations](https://dario-arcos.github.io/ai-framework/docs/integrations) — Plugins and MCP extensions

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| Plugin not appearing | `/plugin marketplace add Dario-Arcos/ai-framework-marketplace`, then `/plugin install ai-framework@ai-framework-marketplace` |
| Settings not loading | Exit and reopen Claude Code |
| Hooks not executing | Verify `python3` is available in PATH |
| Rules not generating | Run `/ai-framework:project-init` |
| Stale rules warning | Run `/ai-framework:project-init` to regenerate |

---

## License

MIT License — See [LICENSE](LICENSE)

**Version:** 2026.1.1 | [CHANGELOG.md](CHANGELOG.md) | CalVer `YYYY.MINOR.MICRO`

Contributions welcome via [GitHub Issues](https://github.com/Dario-Arcos/ai-framework/issues)

---

**Made by [Dario Arcos](https://github.com/Dario-Arcos)**
