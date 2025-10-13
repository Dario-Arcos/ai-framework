# Quickstart: 15 Minutes to Productive

## Step 1: Validate System (2 min)

```bash
git clone https://github.com/Dario-Arcos/ai-framework.git
cd ai-framework
./scripts/init.sh
```

**System checks:** Claude Code CLI, Git, Python, GitHub CLI, Node.js, formatters, notifications.

**Troubleshooting:** The script provides exact installation links for missing dependencies.

**Full dependency list:** Ver README.md del repositorio (sección Prerequisites)

---

## Step 2: Configure (5 min)

### GitHub CLI Authentication

```bash
gh auth login
```

### MCP Servers Setup

```bash
cp .mcp.json.example .mcp.json
```

Enables Playwright (browser testing) and Shadcn (UI components).

### Verification

```bash
./scripts/init.sh  # All checks should pass with ✓
```

---

## Step 3: Deploy (3 min)

### Single Project Deployment

```bash
cp -r .claude/ /path/to/your/project/
cd /path/to/your/project
claude
```

---

## Step 4: First Session (5 min)

### Map Codebase Context

```
/utils:understand
```

**Purpose:** Claude analyzes your entire codebase architecture, preventing hours of refactoring later.

### Complete Feature Implementation

```
/SDD-cycle:specify "add input validation to registration form"
/SDD-cycle:clarify
/SDD-cycle:plan
/SDD-cycle:tasks
/SDD-cycle:analyze
/SDD-cycle:implement
```

**Workflow:** Specification → Clarification → Planning → Task generation → Cross-artifact analysis → TDD-enforced implementation.

### Create Production-Ready PR

```
/git-github:commit "feat: add registration validation"
/git-github:pr develop
```

**Output:** Security-reviewed PR with comprehensive description, test plan, and CI/CD integration.

---

## Common Issues

| Problem                   | Solution                                           |
| ------------------------- | -------------------------------------------------- |
| Claude unresponsive       | `claude --reset-config`                            |
| GitHub CLI authentication | `gh auth logout && gh auth login`                  |
| MCP servers not working   | Verify `.mcp.json` exists, restart Claude CLI      |
| Init script fails         | `chmod +x scripts/init.sh && bash scripts/init.sh` |
| Missing notifications     | Check system notification permissions              |

---

## Next Steps

1. **[ai-first-workflow.md](ai-first-workflow.md)** - Complete PRD → SDD → GitHub ecosystem
2. **[commands-guide.md](commands-guide.md)** - 26 documented commands
3. **[agents-guide.md](agents-guide.md)** - 44 specialized agents
4. **[claude-code-pro-tips.md](claude-code-pro-tips.md)** - Expert workflow patterns

---

## Learning Path

**Week 1: Foundation**

- Setup environment
- Master `/utils:session-start` and `/utils:understand`

**Week 2: Development Cycle**

- Complete SDD workflow
- Practice `/SDD-cycle:specify`, `/SDD-cycle:clarify`, `/SDD-cycle:implement`

**Week 3: Version Control**

- GitHub operations
- Master `/git-github:commit`, `/git-github:pr`, `/git-github:worktree:*`

**Week 4+: Advanced**

- Specialized agents
- Multi-agent coordination

---

**Need assistance?** Run `claude "Help me with [issue]"` for setup, debugging, and workflow guidance.

---

_Última actualización: 2025-10-13_
