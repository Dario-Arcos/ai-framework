---
name: linear-expert
description: |
  Provides expert guidance for Linear issue tracking and project management. Creates, edits, and manages issues, projects, initiatives, and cycles. Configures workflows, labels, priorities, SLAs, and team settings. Integrates Linear with GitHub, Slack, Figma, Jira, and other tools. Sets up and uses Linear MCP server for Claude automation. Triggers when user mentions Linear, issue tracker, project management, sprints, cycles, or asks about Linear features, best practices, workflows, or integrations.
---

# Linear Expert

Expert knowledge for Linear issue tracking and project management.

## Quick Reference

| Domain | Reference | Use When |
|--------|-----------|----------|
| Issues & Workflows | [issues-workflows.md](references/issues-workflows.md) | Creating/editing issues, workflows, triage |
| Projects & Initiatives | [projects-initiatives.md](references/projects-initiatives.md) | Project setup, milestones, cycles |
| AI & MCP | [ai-mcp.md](references/ai-mcp.md) | Claude integration, MCP server, AI agents |
| Integrations | [integrations.md](references/integrations.md) | GitHub, Slack, Figma, Jira, etc. |
| Administration | [administration.md](references/administration.md) | Teams, security, SAML, billing |
| Views & Navigation | [views-navigation.md](references/views-navigation.md) | Filters, views, dashboards |
| **Automation** | [automation-workflows.md](references/automation-workflows.md) | Linear↔GitHub↔Claude Code pipelines |

## Core Concepts

Linear organizes work hierarchically:

```
Workspace
├── Teams (engineering, design, product)
│   ├── Issues (atomic units of work)
│   │   ├── Sub-issues
│   │   └── Properties (status, priority, labels, estimates)
│   ├── Cycles (time-boxed iterations)
│   └── Triage (incoming issue inbox)
├── Projects (cross-team features with milestones)
└── Initiatives (strategic goals grouping projects)
```

## Workflow Patterns

### Issue Lifecycle

```
Triage → Backlog → Todo → In Progress → Done → Canceled/Archived
```

**Statuses are customizable per team.** Default statuses:
- Triage (incoming)
- Backlog (prioritized but not scheduled)
- Todo (ready to start)
- In Progress (active work)
- Done (completed)
- Canceled (won't do)

### Project-Driven Development

1. Create Initiative (strategic goal)
2. Create Project under Initiative
3. Add Milestones to Project
4. Create Issues under Project
5. Track progress via Project Graph
6. Post Project Updates

### Cycle-Based Sprints

1. Configure Cycle duration (team settings)
2. Add issues to current Cycle
3. Track burndown via Cycle Graph
4. Roll incomplete issues to next Cycle
5. Review Cycle completion rate

## MCP Integration

Linear provides an official MCP server for Claude integration.

### Setup (Claude Code)

```bash
claude mcp add --transport http linear-server https://mcp.linear.app/mcp
```

Then run `/mcp` to authenticate.

### Available MCP Tools

The Linear MCP server provides tools for:
- Finding issues, projects, and comments
- Creating new issues and projects
- Updating issue properties
- Adding comments

### Common MCP Patterns

**Create issue from conversation:**
```
Use Linear MCP to create an issue:
- Title: [extracted from context]
- Team: [infer from context or ask]
- Description: [summarize discussion]
- Priority: [infer urgency]
```

**Query issues:**
```
Use Linear MCP to find:
- My assigned issues
- Issues in [project/team]
- High-priority issues
- Issues updated this week
```

**Update issue status:**
```
Use Linear MCP to:
- Mark issue as Done
- Add comment with findings
- Update estimate
```

## Automation Workflows

### Claude Code-Centric Flow (Primary)

Claude Code is the command center. Everything originates here.

```
Claude Code (Centro)
    │
    ├─ MCP Linear: crear épica/stories
    ├─ Desarrollar código
    ├─ git commit "Fixes LIN-123"
    └─ git push
           │
           └─► GitHub ←sync nativo→ Linear (Done automático)
```

**No GitHub Actions needed. No webhooks to configure.**

### Git Integration

Use magic words in commits/PRs to link and auto-update Linear issues.

#### Magic Words

| Type | Words | Effect |
|------|-------|--------|
| **Closing** | fix, fixes, fixed, fixing, close, closes, closed, closing, resolve, resolves, resolved, resolving, complete, completes, completed, completing | Links + moves to Done on merge to default branch |
| **Non-closing** | ref, refs, references, part of, related to, contributes to, toward, towards | Links only (no auto-close) |
| **Unlinking** | skip, ignore | Prevents linking even if branch contains issue ID |

#### Where Magic Words Work

| Location | Example | Effect |
|----------|---------|--------|
| PR title | `Fixes LIN-123: Add login` | Links PR to issue |
| PR description | `Part of LIN-123` | Links PR to issue |
| Commit message | `Fixes LIN-123: implement auth` | Links commit to issue |
| Branch name | `feature/LIN-123-login` | Auto-links any PR from this branch |

#### Branch-Specific Rules (Critical)

**Branch rules only work with PRs, not direct pushes.**

> "Branch rules apply only to target branches—the branch a PR is being merged into."
> — Linear Official Documentation

Configure in: Settings → Team → Issue statuses & automations → Pull request and commit automation

| PR Event | Default Automation |
|----------|-------------------|
| PR opened/drafted | → In Progress |
| Review requested | → (configurable) |
| Ready for merge | → (configurable) |
| **PR merged to default branch** | → Done (with closing word) |
| **PR merged to custom branch** | → (branch-specific rule) |

Example branch-specific rules:
- PR merged to `staging` → In QA
- PR merged to `main` → Deployed

**For detailed patterns**: [automation-workflows.md](references/automation-workflows.md)

## Best Practices

### Issue Creation

- **Title**: Action-oriented, specific (`Implement OAuth login` not `Login`)
- **Description**: Context, acceptance criteria, links
- **Estimates**: Use team's scale (linear, fibonacci, t-shirt)
- **Labels**: Categorize (bug, feature, improvement, chore)
- **Priority**: Reserve Urgent for true emergencies

### Project Setup

- Assign a **Project Lead** (single owner)
- Set **Target Date** (can be quarter/month if uncertain)
- Add **Milestones** for phased delivery
- Enable **Project Notifications** for stakeholders

### Team Workflows

- Customize statuses to match your process
- Use **Triage** for incoming external issues
- Configure **SLAs** for support queues
- Set up **Automations** for repetitive actions

## Common Tasks

### "How do I..."

| Task | Solution |
|------|----------|
| Move issue to another team | `Shift T` or edit Team property |
| Link to GitHub PR | Mention issue ID in PR (`LIN-123`) |
| Create recurring issue | Use issue templates with automations |
| Bulk edit issues | Select multiple → right-click or `Cmd K` |
| Filter by label | Type `label:bug` in filter bar |
| Find my issues | Sidebar → My Issues or `G I` |

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Create issue | `C` |
| Open command palette | `Cmd/Ctrl K` |
| Go to My Issues | `G I` |
| Go to Inbox | `G N` |
| Set priority | `1-4` (with issue focused) |
| Set status | `S` |
| Add label | `L` |
| Assign | `A` |
| Add to project | `Shift P` |
| Add to cycle | `Shift C` |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| GitHub PR not linking | Check branch contains `LIN-123` or PR mentions it |
| Slack notifications missing | Verify Slack integration in team settings |
| Can't edit issue | Check team permissions and issue creator |
| MCP auth fails | Run `rm -rf ~/.mcp-auth` and re-authenticate |
| Import stuck | Large imports may take hours; check audit log |

## Domain References

For detailed information, read the appropriate reference file:

- **Issues**: Workflows, creation, editing, templates, relations → [issues-workflows.md](references/issues-workflows.md)
- **Projects**: Milestones, graphs, updates, dependencies → [projects-initiatives.md](references/projects-initiatives.md)
- **MCP/AI**: Setup, tools, triage intelligence → [ai-mcp.md](references/ai-mcp.md)
- **Integrations**: GitHub, Slack, Figma, Jira setup → [integrations.md](references/integrations.md)
- **Admin**: Teams, SAML, SCIM, security, billing → [administration.md](references/administration.md)
- **Views**: Filters, boards, timelines, dashboards → [views-navigation.md](references/views-navigation.md)
- **Automation**: Linear↔GitHub↔Claude Code pipelines → [automation-workflows.md](references/automation-workflows.md)
