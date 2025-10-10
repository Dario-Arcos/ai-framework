# Quick Start Guide

Get AI Framework running in 5 minutes.

---

## Prerequisites Check

```bash
# Verify you have the essentials
claude --version      # Claude Code CLI
git --version         # Git
python3 --version     # Python 3.8+
```

Missing something? See [Requirements](#requirements).

---

## Installation (2 minutes)

```bash
# 1. Clone framework
git clone https://github.com/Dario-Arcos/ai-framework.git

# 2. Navigate to YOUR project
cd /path/to/your/project

# 3. Run installer
~/ai-framework/install.sh
```

**What happens:**

- ✓ Copies configuration files
- ✓ Registers plugin marketplace
- ✓ Sets up `.claude/` and `.specify/` directories
- ✓ Validates installation

---

## Plugin Setup (1 minute)

```bash
# In your project directory
claude add plugin
```

**When prompted:**

1. Select marketplace: `ai-framework-local`
2. Select plugin: `ai-framework`
3. Confirm installation

---

## Verification (30 seconds)

```bash
# Start Claude Code
claude

# Check commands are available
/help

# You should see commands like:
# /SDD-cycle:specify
# /git-github:commit
# /utils:docs
# etc.
```

---

## Your First AI-First Workflow (2 minutes)

### Example: Create a New Feature

```bash
# 1. Start Claude Code in your project
cd /path/to/your/project
claude

# 2. Create feature specification
/SDD-cycle:specify

# Describe your feature in natural language
# Example: "Add user authentication with JWT tokens"

# 3. Generate implementation plan
/SDD-cycle:plan

# 4. Generate tasks
/SDD-cycle:tasks

# 5. Execute implementation
/SDD-cycle:implement
```

**Result:** Complete feature implementation following TDD, constitutional principles, and complexity budgets.

---

## Explore Agents

Agents are automatically suggested based on context, but you can invoke them explicitly:

```
"Use the security-reviewer agent to audit this code"
"Launch the performance-engineer agent to optimize this query"
"Run the tdd-orchestrator agent for this feature"
```

**Available categories:**

- Architecture & System Design
- Code Review & Security
- Testing & Debugging
- DevOps & Deployment
- Documentation & Technical Writing
- Performance & Observability
- Database Management
- Shadcn-UI Components
- User Experience & Design
- Web & Application Development
- Incident Response & Network

---

## Use Intelligent Hooks

Hooks run automatically. No configuration needed.

**Active hooks:**

| Hook                  | Trigger           | Action                       |
| --------------------- | ----------------- | ---------------------------- |
| `security_guard.py`   | Before Edit/Write | Prevents credential exposure |
| `pre-tool-use.py`     | Before Task       | Validates agent context      |
| `clean_code.py`       | After Edit/Write  | Auto-formats code            |
| `minimal_thinking.py` | User prompt       | Enforces thinking discipline |
| `ccnotify.py`         | Various events    | Desktop notifications        |

**Customize:** Edit `.claude/settings.json` hooks section.

---

## Validate Installation

```bash
cd /path/to/your/project
~/ai-framework/validate.sh
```

**Checks:**

- ✓ Configuration files present and valid
- ✓ Governance rules installed
- ✓ Plugin registered
- ✓ Scripts executable

---

## Common Tasks

### Make a Commit

```bash
# Intelligent commit with grouped changes
/git-github:commit all changes
```

### Create a Pull Request

```bash
# Auto-generates PR description from commit history
/git-github:pr
```

### Update Documentation

```bash
# Updates README, API docs, or CHANGELOG
/utils:docs README
```

### Research Complex Topic

```bash
# Professional investigation with systematic methodology
/utils:deep-research "competitor analysis for X"
```

---

## Requirements

### Essential

- **Claude Code:** [Install Guide](https://docs.anthropic.com/en/docs/claude-code/installation)
- **Git:** [Download](https://git-scm.com/downloads)
- **Python 3.8+:** [Download](https://www.python.org/downloads/)

### Recommended

- **GitHub CLI:** `brew install gh` (macOS) or see [gh CLI](https://cli.github.com/)
- **Node.js 18+:** For MCP servers and formatters
- **Python formatters:** `pip install black ruff` or `pip install autopep8`

### Optional

- **shfmt:** Bash formatter - `brew install shfmt`
- **jq:** JSON processor - `brew install jq`
- **Prettier:** Auto-installs via npx when needed

---

## Troubleshooting

### "Plugin not found"

```bash
# Verify marketplace is registered
cat ~/.config/claude-code/plugin-marketplaces.json

# Should contain path to: /path/to/ai-framework/plugin
```

**Fix:** Re-run `install.sh`

### "Commands not showing"

```bash
# Force refresh
claude --reset-config

# Restart Claude Code
```

### "Hooks not executing"

```bash
# Check Python 3
which python3

# Verify hooks are executable
ls -la .claude/hooks/*.py

# Should show: -rwxr-xr-x
```

### "Settings.json invalid"

```bash
# Validate JSON
python3 -c "import json; json.load(open('.claude/settings.json'))"

# If error, restore from template
cp ~/ai-framework/template/.claude/settings.json .claude/
```

---

## Next Steps

1. **Read the Constitution:** `.specify/memory/constitution.md`
   - Understand the 5 core principles
   - Learn complexity budgets
   - Review constitutional tests

2. **Explore Commands:** Type `/help` and try different workflows

3. **Customize Hooks:** Edit `.claude/settings.json` to add/remove hooks

4. **Review Agents:** See what specialized agents are available for your tech stack

5. **Join Community:** Share feedback and get support

---

## Learning Resources

- **Full README:** [README-FRAMEWORK.md](README-FRAMEWORK.md)
- **Constitution:** [.specify/memory/constitution.md](template/.specify/memory/constitution.md)
- **Always Works™ Methodology:** [.claude/rules/project-context.md](template/.claude/rules/project-context.md)
- **Effective Agents Guide:** [.claude/rules/effective-agents-guide.md](template/.claude/rules/effective-agents-guide.md)
- **Product Design Principles:** [.specify/memory/product-design-principles.md](template/.specify/memory/product-design-principles.md)

---

## Support

- **Issues:** [GitHub Issues](https://github.com/Dario-Arcos/ai-framework/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Dario-Arcos/ai-framework/discussions)
- **Contributions:** Pull requests welcome!

---

**Happy AI-First Development!** 🚀
