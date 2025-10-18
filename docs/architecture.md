# AI Framework Architecture

**Internal architecture documentation for maintainers and AI.**

> This doc explains HOW the framework works internally. For user docs, see [README.md](../README.md).

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Core Components](#core-components)
4. [Session Lifecycle](#session-lifecycle)
5. [Integration Patterns](#integration-patterns)
6. [Extension Guide](#extension-guide)
7. [Troubleshooting](#troubleshooting)

---

## Overview

**AI Framework** = Claude Code Plugin + Constitutional Governance

Three pillars:

1. **Hooks** — Auto-execute on Claude events (SessionStart, PreToolUse, etc.)
2. **Commands** — Slash commands (`/utils:project-init`, `/commit`, etc.)
3. **Agents** — Specialized sub-agents for specific tasks (45 total)

**Key Insight**: Framework uses hooks to **enforce** governance, not just suggest.

---

## Directory Structure

**Plugin Source** (ai-framework/):

- `hooks/` — Auto-executing scripts (6 total: session-start, workspace-status, security_guard, clean_code, minimal_thinking, ccnotify)
- `commands/` — Slash commands (24 total in 4 categories: PRP-cycle, SDD-cycle, git-github, utils)
- `agents/` — Sub-agents (45 total in 11 categories)
- `template/` — Files copied to user projects on installation

**User Project** (after installation):

- `CLAUDE.md` — Project configuration
- `.claude/` — Settings + rules (operational-excellence.md, effective-agents-guide.md)
- `.specify/memory/` — constitution.md, project-context.md (generated)
- `.mcp.json` — MCP servers config

---

## Core Components

### 1. Hooks (Auto-Execution)

Python scripts registered in `hooks/hooks.json` that execute on Claude events:

| Hook                  | Trigger          | Purpose                                    | Critical? |
| --------------------- | ---------------- | ------------------------------------------ | --------- |
| `session-start.py`    | SessionStart     | Auto-installs framework files on first run | ✅ Yes    |
| `workspace-status.py` | SessionStart     | Shows session guidance                     | No        |
| `security_guard.py`   | PreToolUse(Edit) | Blocks security vulnerabilities            | ✅ Yes    |
| `clean_code.py`       | PostToolUse      | Auto-formats Python files                  | No        |
| `minimal_thinking.py` | UserPromptSubmit | Optimizes thought process budget           | No        |
| `ccnotify.py`         | Multiple events  | macOS desktop notifications                | No        |

### 2. Commands (Slash Commands)

Markdown files in `commands/` with frontmatter (description, allowed-tools). 24 total:

- **PRP-cycle** (2): `/prd-sync`, `/prd-new`
- **SDD-cycle** (7): `/specify`, `/plan`, `/tasks`, `/implement`, `/clarify`, `/analyze`, `/constitution`
- **git-github** (6): `/commit`, `/pr`, `/issue-manager`, `/issue-sync`, `/worktree:create`, `/worktree:cleanup`
- **utils** (9): `/project-init`, `/understand`, `/docs`, `/polish`, `/setup-dependencies`, `/changelog`, `/deep-research`, `/three-experts`, `/session-start`

### 3. Agents (Sub-Agents)

Markdown files in `agents/` with frontmatter (name, description, model). Invoked via Task tool. 45 total:

- Architecture & System Design (8)
- Code Review & Security (5)
- Database Management (2)
- DevOps & Deployment (4)
- Documentation & Technical Writing (5)
- Incident Response & Network (2)
- Performance & Observability (3)
- Shadcn-UI Components (4)
- Testing & Debugging (4)
- User Experience & Design (3)
- Web & Application (5)

### 4. Templates (Installation Files)

**Directory**: `.claude-plugin/template/`

Files copied to user project on first session:

- **CLAUDE.md**: Project configuration (references governance docs)
- **.mcp.json**: MCP servers configuration
- **.claude/settings.local.json**: User-specific settings
- **.claude/rules/**: Operational guidelines (operational-excellence.md, effective-agents-guide.md, etc.)
- **.specify/memory/**: Constitutional documents (constitution.md, design-principles.md, etc.)

---

## Session Lifecycle

**First Installation:**

1. `session-start.py` checks if framework installed (CLAUDE.md, constitution.md exist)
2. If NO → Copies template/ files (CLAUDE.md, .mcp.json, .claude/, .specify/)
3. Creates `.claude/.pending_restart` marker (signals workspace-status to skip)
4. Shows "✅ AI Framework instalado, 🔄 Reinicia Claude Code"
5. User restarts Claude

**Subsequent Sessions:**

1. `session-start.py` verifies .gitignore up to date, exits silently
2. `workspace-status.py` checks `.pending_restart` marker:
   - If exists → Delete marker, exit silently (avoid duplicate messages)
   - If not exists → Show session guidance (project-context status, worktree info, git sync reminders)

**Marker Coordination:** session-start creates `.claude/.pending_restart` after installation; workspace-status deletes it on next session to prevent showing both "Reinicia Claude" + "Project context no configurado" simultaneously.

---

## Integration Patterns

**Hook Coordination:** session-start creates `.pending_restart` marker → workspace-status checks marker → if exists, skip execution (prevents duplicate messages)

**Hook → Command:** workspace-status shows "Project context no configurado" → suggests `/utils:project-init` → user executes → generates project-context.md

**Command → Auto-Load:** `/utils:project-init` generates `.specify/memory/project-context.md` → CLAUDE.md references `@.specify/memory/project-context.md` → Claude auto-loads every session

**Sub-Agent Inheritance:** Task tool sub-agents inherit full system prompt including CLAUDE.md with all @ references (constitution.md, operational-excellence.md, project-context.md, etc.). No injection needed.

---

## Extension Guide

**New Hook:** Create Python script in `hooks/` → Register in `hooks.json` → Test with `python3 hooks/my-hook.py`. Must print JSON output, silent fail (sys.exit(0)), never block Claude.

**New Command:** Create `commands/category/my-command.md` with frontmatter (description, allowed-tools) → Test with `/my-command`.

**New Agent:** Create `agents/Category/my-agent.md` with frontmatter (name, description, model) → Invoke via Task tool.

**Template Files:** Add to `template/` → Reference in `template/CLAUDE.md` if needed → session-start.py auto-copies on next installation.

---

## Troubleshooting

### Common Issues

| Issue                         | Cause               | Solution                                   |
| ----------------------------- | ------------------- | ------------------------------------------ |
| **Hooks not executing**       | Python not in PATH  | Install Python 3.8+                        |
| **session-start loops**       | Marker not deleted  | Delete `.claude/.pending_restart` manually |
| **Commands not showing**      | Cache stale         | Restart Claude or `/help`                  |
| **Agent not in Task list**    | Invalid frontmatter | Check `name:` and `description:` fields    |
| **Template files not copied** | Already installed   | Delete CLAUDE.md and restart Claude        |
| **project-context stale**     | Project evolved     | Run `/utils:project-init` to regenerate    |

### Validation Checklist

Before committing changes:

- [ ] Python syntax valid: `python3 -m py_compile file.py`
- [ ] Hooks registered in `hooks.json`
- [ ] Commands have valid frontmatter
- [ ] Agents have `name` and `description`
- [ ] No hardcoded paths (use Path or env vars)
- [ ] Silent failures (hooks never block Claude startup)

---

## Architecture Decisions

**Python for Hooks:** Cross-platform, rich stdlib, Claude Code native support, easy text processing.

**Markdown for Commands/Agents:** Human-readable, Claude-native format, supports frontmatter, easy version control.

**Separate Hooks:** session-start (installer) + workspace-status (guide) = single responsibility, better performance (marker coordination), easier maintenance.

**No Auto-Generation:** AI-first principle—Claude AI generates better context than Python script; eliminates tech detection complexity.

---

## Version History

See [CHANGELOG.md](../CHANGELOG.md) for detailed version history.

---

## Maintenance Notes

**Template Updates:** Copied on first install only. To update: user manually updates OR deletes CLAUDE.md + restart. Make templates backward-compatible.

**New Hooks:** Only if prevents errors, saves manual work, or essential. Don't add for nice-to-haves, command-duplicates, or startup-slowing features.

**New Commands:** Cheap (markdown only). Add liberally for common workflows, reusable patterns, autonomous execution.

**New Agents:** Add only if solves specific domain problem, not covered by existing agents, and used frequently.

---

**Maintainer**: Dario Arcos
**License**: MIT
