# Automation Workflows

Reference for Claude Code-centric development with Linear and GitHub.

## Table of Contents

- [Claude Code-Centric Flow (Primary)](#claude-code-centric-flow-primary)
- [GitHub-Linear Native Sync](#github-linear-native-sync)
- [MCP Linear Operations](#mcp-linear-operations)
- [Git Workflow Patterns](#git-workflow-patterns)
- [Advanced: Headless Automation](#advanced-headless-automation)
- [Advanced: GitHub Actions](#advanced-github-actions)

---

## Claude Code-Centric Flow (Primary)

Claude Code acts as the command center for all development activities.

### The Flow

```
┌──────────────────────────────────────────────────────────────┐
│                     CLAUDE CODE (Centro)                      │
│                                                              │
│  1. Crear issue ───────────────────────────────► Linear      │
│     (MCP Linear)                                (Backlog)    │
│                                                              │
│  2. Planificar → mover a Todo ─────────────────► Linear      │
│     (MCP Linear)                                (Todo)       │
│                                                              │
│  3. Desarrollar en feature branch                            │
│     git checkout -b feature/LIN-123-login                    │
│                                                              │
│  4. Commits con magic word                                   │
│     git commit -m "Part of LIN-123: add form"                │
│                                                              │
│  5. Crear PR hacia branch target ──────────────► GitHub      │
│     gh pr create --base develop                    │         │
│                                                    ▼         │
│                                              Linear detecta  │
│                                              PR automático   │
│                                              (→ In Progress) │
│                                                              │
│  6. Merge PR ──────────────────────────────────► GitHub      │
│                                                    │         │
│                                                    ▼         │
│                                              Linear actualiza│
│                                              (→ estado según │
│                                               branch rules)  │
└──────────────────────────────────────────────────────────────┘
```

### Quick Reference: Recommended Workflow

| Step | Action | Tool | Linear Status |
|------|--------|------|---------------|
| 1 | Create issue | MCP Linear | Backlog |
| 2 | Plan & prioritize | MCP Linear | Todo |
| 3 | Start work | MCP Linear | In Progress |
| 4 | Create feature branch | Git | — |
| 5 | Develop with `Part of` commits | Git | — |
| 6 | Push & create PR to target branch | Git/GitHub | (auto) In Progress |
| 7 | Review & merge PR | GitHub | (auto) per branch rule |
| 8 | Certify completion | MCP Linear | Done |

**Key insight:** Use `Part of LIN-XXX` during development (non-closing), then let branch-specific rules handle status transitions on PR events.

### Step-by-Step Example

**1. Planning Phase (in Claude Code)**

```
Usuario: "Necesito implementar autenticación de usuarios"

Claude: Uso Linear MCP para crear la estructura:

Epic: "User Authentication System"
├── Story: "LIN-101 Implement login flow"
├── Story: "LIN-102 Implement registration"
├── Story: "LIN-103 Implement password recovery"
└── Story: "LIN-104 Add session management"
```

**2. Development Phase (in Claude Code)**

```
Usuario: "Implementa LIN-101"

Claude: [develops login code]
        [writes tests]
        [verifies functionality]
```

**3. Commit & Push (from Claude Code)**

```bash
# Claude prepares commit with magic word
git add .
git commit -m "Fixes LIN-101: implement login flow

- Add login form component
- Create auth API endpoint
- Add session token handling
- Include unit tests"

git push origin feature/LIN-101-login
```

**4. Automatic Sync (GitHub → Linear)**

- GitHub receives push
- Linear detects `LIN-101` in commit/branch
- Linear updates issue status:
  - Push to feature branch → In Progress
  - Merge to main → Done

**No GitHub Actions needed. No webhooks to configure. Native integration.**

---

## GitHub-Linear Native Sync

### Magic Words

Include these in commit messages, PR titles, or PR descriptions:

#### Closing Words (auto-close on merge to default branch)

| Word | Variants |
|------|----------|
| `fix` | fix, fixes, fixed, fixing |
| `close` | close, closes, closed, closing |
| `resolve` | resolve, resolves, resolved, resolving |
| `complete` | complete, completes, completed, completing |

#### Non-Closing Words (link only, no auto-close)

| Word | Variants |
|------|----------|
| `ref` | ref, refs, references |
| `part of` | part of |
| `related to` | related to |
| `contributes to` | contributes to |
| `toward` | toward, towards |

#### Unlinking Words (prevent auto-link)

| Word | Use Case |
|------|----------|
| `skip LIN-123` | Prevent linking when branch contains issue ID |
| `ignore LIN-123` | Same as skip |

### Branch Name Detection

Linear auto-detects issue IDs in branch names:

```bash
# All these formats work
feature/LIN-123-add-login
lin-123/authentication
123-new-feature  # if team prefix matches
```

### Automatic Status Updates

**CRITICAL: Branch-specific rules only work with PRs, not direct pushes.**

> "Branch rules apply only to target branches—the branch a PR is being merged into. Automations are not supported for source branches."
> — Linear Official Documentation

#### Default Automation (configurable per team)

| PR Event | Default Status Change |
|----------|----------------------|
| PR opened/drafted | → In Progress |
| Review requested | → (configurable) |
| Ready for merge | → (configurable) |
| PR merged (closing word) | → Done |

#### Branch-Specific Rules

Configure custom automations for different target branches:

| PR Merged To | Example Automation |
|--------------|-------------------|
| `staging` | → In QA |
| `develop` | → In Review |
| `main` | → Deployed |
| `^release/.*` | → Ready for Release (regex supported) |

**Configure in:** Settings → Team → Issue statuses & automations → Pull request and commit automation

### Enable Commit Linking (One-time Setup)

1. Linear: Settings → Integrations → GitHub
2. Enable "Link commits to issues with magic words"
3. Add webhook in GitHub repo settings
4. Paste Linear's webhook URL

---

## MCP Linear Operations

### Setup

```bash
claude mcp add --transport http linear-server https://mcp.linear.app/mcp
```

Run `/mcp` to authenticate.

### Creating Work Items

**Create Epic/Initiative:**
```
Create a Linear initiative called "Q1 Platform Improvements"
with description and target date
```

**Create Project:**
```
Create a Linear project "Authentication System"
under initiative "Q1 Platform Improvements"
with milestones: Design, Implementation, Testing
```

**Create Issues/Stories:**
```
Create these issues in project "Authentication System":
1. "Implement login flow" - priority high, estimate 3
2. "Implement registration" - priority high, estimate 5
3. "Password recovery" - priority medium, estimate 3
```

**Create Sub-issues:**
```
Add sub-issues to LIN-101:
- Create login form UI
- Implement auth API
- Add form validation
- Write tests
```

### Querying Work

```
Find all my open issues in "Authentication System" project
```

```
Show high-priority issues updated this week
```

```
What issues are blocking LIN-101?
```

### Updating Work

```
Mark LIN-101 as Done with comment "Implemented in PR #45"
```

```
Add LIN-101, LIN-102, LIN-103 to current cycle
```

```
Update LIN-101 estimate to 5 and add label "complex"
```

---

## Git Workflow Patterns

### Feature Branch Pattern

```bash
# Create branch with issue ID
git checkout -b feature/LIN-101-login-flow

# Develop...

# Commit with magic word
git commit -m "Fixes LIN-101: implement login flow"

# Push
git push -u origin feature/LIN-101-login-flow

# Create PR (title will include LIN-101)
gh pr create --title "Fixes LIN-101: Login flow implementation"
```

### Multiple Issues in One PR

```bash
git commit -m "Fixes LIN-101, LIN-102: implement auth flows

Implements both login and registration in a unified auth module.

Fixes LIN-101
Fixes LIN-102"
```

### Partial Progress (Link Without Closing)

```bash
git commit -m "Part of LIN-101: add login form UI

Form component complete, API integration pending."
```

### Commit Message Template

```
<magic-word> <issue-id>: <short description>

<detailed description>

<magic-word> <issue-id>
[repeat for additional issues]
```

---

## Advanced: Headless Automation

For CI/CD or batch processing scenarios where Claude Code runs without human interaction.

### Basic Headless Execution

```bash
# Execute single task
claude -p "Implement the feature described in LIN-123"

# With file context
claude -p "Review and fix issues in this file" --file src/auth.ts
```

### Session Resume for Multi-Step

```bash
# Start session
claude -p "Analyze LIN-123 and create implementation plan" --session task-123

# Continue later
claude --resume task-123 -p "Implement the plan"

# Final step
claude --resume task-123 -p "Generate tests and documentation"
```

### Environment Setup

```bash
export ANTHROPIC_API_KEY="sk-..."
export CLAUDE_CODE_MODEL="claude-sonnet-4-20250514"
```

---

## Advanced: GitHub Actions

For fully automated pipelines without human intervention.

### Auto-Implementation on Issue Creation

```yaml
name: Auto-Implement Linear Issues
on:
  repository_dispatch:
    types: [linear-issue-created]

jobs:
  implement:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Implement Feature
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          npm install -g @anthropic-ai/claude-code
          claude -p "Implement: ${{ github.event.client_payload.title }}"

      - name: Create PR
        run: |
          git checkout -b "feature/LIN-${{ github.event.client_payload.id }}"
          git add .
          git commit -m "Fixes LIN-${{ github.event.client_payload.id }}"
          gh pr create --title "Fixes LIN-${{ github.event.client_payload.id }}"
```

### Webhook Setup (Linear → GitHub)

1. Linear: Settings → API → Webhooks
2. URL: `https://api.github.com/repos/OWNER/REPO/dispatches`
3. Add GitHub token for auth
4. Select events: Issue created

**Note:** This advanced pattern is optional. The Claude Code-centric flow works without any GitHub Actions configuration.

---

## Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Push doesn't update Linear status | Branch rules only work with PRs | Create PR to target branch instead |
| PR not detected by Linear | Webhook not configured | Enable "Link commits to issues with magic words" + add webhook |
| Issue not auto-closing on merge | Missing closing magic word | Use `Fixes`, `Closes`, or `Resolves` in PR |
| Wrong status on PR merge | Branch rule misconfigured | Check Settings → Team → Issue statuses & automations |
| Can't unlink PR from issue | Branch name contains issue ID | Add `skip LIN-XXX` or `ignore LIN-XXX` to PR description |

### Debugging Checklist

1. **Webhook configured?** Linear Settings → Integrations → GitHub → Webhook URL copied to GitHub
2. **Branch rules set?** Settings → Team → Issue statuses & automations → Pull request automation
3. **Correct magic word?** `Part of` = link only, `Fixes` = close on merge
4. **PR to correct branch?** Branch rules apply to TARGET branch (e.g., `develop`, `main`)
5. **Issue ID format?** Must match team prefix (e.g., `LIN-123`, `ENG-456`)

## Best Practices

### For Claude Code-Centric Development

1. **Create issues before coding** - Establishes tracking from the start
2. **Use `Part of` during development** - Links without closing, allows multiple PRs
3. **Use `Fixes` in final PR** - Auto-closes when merged to default branch
4. **One issue per branch** - Cleaner history and automatic linking
5. **Configure branch-specific rules** - Automate status transitions per environment

### Security

- Never commit API keys
- Use environment variables or secrets
- Review generated code before merging

### Efficiency

- Batch related issues when planning
- Use sub-issues for complex work
- Keep commits atomic and focused

---

## Quick Reference

| Task | Command/Action |
|------|----------------|
| Create issue | MCP: "Create issue in team X..." |
| Link commit | `git commit -m "Fixes LIN-123: ..."` |
| Auto-status | Push → In Progress, Merge → Done |
| Query issues | MCP: "Find my open issues..." |
| Update status | MCP: "Mark LIN-123 as Done" |
