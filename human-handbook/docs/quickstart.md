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
/ai-framework:utils:understand
```

**Purpose:** Claude analyzes your entire codebase architecture, preventing hours of refactoring later.

### Complete Feature Implementation

**Opción A: Branch simple** (desarrollo lineal)

```
/ai-framework:SDD-cycle:speckit.specify "add input validation to registration form"
# → Crea branch 001-add-input-validation en MISMO directorio
/ai-framework:SDD-cycle:speckit.clarify
/ai-framework:SDD-cycle:speckit.plan
/ai-framework:SDD-cycle:speckit.tasks
/ai-framework:Task agent-assignment-analyzer "Analyze tasks.md and assign specialized agents for parallel execution"
/ai-framework:SDD-cycle:speckit.analyze
/ai-framework:SDD-cycle:speckit.implement
```

**Opción B: Worktree aislado** (trabajo paralelo, RECOMENDADO)

```
/ai-framework:git-github:worktree:create "add input validation to registration form" main
# → Abre IDE en nueva ventana
# ⚠️ En nueva ventana: Cmd+` para abrir terminal, luego:
pwd  # Verificar: debe mostrar ../worktree-add-input-validation/
claude  # Iniciar nueva sesión Claude

# Continuar con SDD workflow (ORDEN CORRECTO):
/ai-framework:SDD-cycle:speckit.specify "add input validation to registration form"
/ai-framework:SDD-cycle:speckit.clarify
/ai-framework:SDD-cycle:speckit.plan
/ai-framework:SDD-cycle:speckit.tasks
/ai-framework:Task agent-assignment-analyzer "Analyze tasks.md and assign specialized agents for parallel execution"
/ai-framework:SDD-cycle:speckit.analyze
/ai-framework:SDD-cycle:speckit.implement
```

**Workflow (ORDEN CORRECTO):** Specification → Clarification → Planning → Task generation → **Agent Assignment (CRÍTICO)** → Cross-artifact analysis → TDD-enforced implementation with specialized agents.

### Create Production-Ready PR

```
/ai-framework:git-github:commit "feat: add registration validation"
/ai-framework:git-github:pr develop
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

1. **[ai-first-workflow.md](ai-first-workflow.md)** - Complete PRP → SDD → GitHub ecosystem
2. **[commands-guide.md](commands-guide.md)** - 24 documented commands
3. **[agents-guide.md](agents-guide.md)** - 45 specialized agents
4. **[claude-code-pro-tips.md](claude-code-pro-tips.md)** - Expert workflow patterns

---

## Learning Path

**Week 1: Foundation**

- Setup environment
- Master `/ai-framework:utils:session-start` and `/ai-framework:utils:understand`

**Week 2: Development Cycle**

- Complete SDD workflow (ORDEN CORRECTO: specify → clarify → plan → tasks → agent-assignment → analyze → implement)
- Practice `/ai-framework:SDD-cycle:speckit.specify`, `/ai-framework:SDD-cycle:speckit.clarify`, agent-assignment (via Task tool), `/ai-framework:SDD-cycle:speckit.implement`
- Master parallel execution with specialized agents

**Week 3: Version Control**

- GitHub operations
- Master `/ai-framework:git-github:commit`, `/ai-framework:git-github:pr`, `/ai-framework:git-github:worktree:*`

**Week 4+: Advanced**

- Specialized agents
- Multi-agent coordination

---

**Need assistance?** Run `claude "Help me with [issue]"` for setup, debugging, and workflow guidance.

---

_Última actualización: 2025-10-14_
