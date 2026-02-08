---
name: project-init
description: Generate project memory rules in docs/claude-rules/ for native Claude Code integration
---

# Project Initialization

Analyzes the project and generates modular rule files that Claude Code loads automatically.

**Purpose**: High-signal project memory preventing context-related failures
**Output**: 4 rule files (~140 lines total)

## Architecture

```
docs/claude-rules/        ← TRACKED (source of truth, versioned)
├── stack.md
├── patterns.md
├── architecture.md
└── testing.md (if tests exist)

.claude/rules/            ← IGNORED (local working copy)
└── (auto-synced by session-start hook)
```

Pattern: Similar to `.env.example` → `.env`. Canonical rules in `docs/claude-rules/` (reviewable in PRs). Session-start hook syncs to `.claude/rules/`.

## Workflow

### Phase 1: Cleanup & Preparation

1. Detect existing: `docs/claude-rules/*.md`, `.claude/rules/*.md`, `.specify/memory/project-context.md`
2. Clean up old state if exists
3. Create directories: `mkdir -p docs/claude-rules/ .claude/rules/`

### Phase 2: Project Analysis

Execute all 5 layers. Read [references/analysis-layers.md](references/analysis-layers.md) for detailed grep patterns and extraction rules.

**Layer 1: Manifests** — Read package manager files, extract runtime, framework, top dependencies, scripts
**Layer 2: Configs** — Read compiler/formatter/test configs, extract settings
**Layer 3: Structure** — Analyze directories, entry points, file distribution
**Layer 4: Patterns** — Grep for naming conventions, error handling, imports, auth, tests
**Layer 5: Key File Sampling** — Read 5-8 representative files for style confirmation

### Phase 3: Synthesis → Rule Files

Generate rule files from analysis data. Write to `docs/claude-rules/`, then copy to `.claude/rules/`.

Read [references/rule-templates.md](references/rule-templates.md) for output format templates (stack.md, patterns.md, architecture.md, testing.md).

**Conditional**: testing.md only generated if tests detected (jest/pytest/vitest config, test directory, or >3 test files).

### Phase 4: Sync to Local & Report

```bash
cp docs/claude-rules/*.md .claude/rules/
```

Display summary: stack detected, patterns identified, architecture mapped, files generated with line counts.

## Notes

- **Dual-location pattern**: `docs/claude-rules/` (tracked) + `.claude/rules/` (ignored)
- **Auto-sync**: Session-start hook copies tracked rules to local on every session
- **Full rebuild**: Always regenerates all rules (no incremental)
- **Token budget**: ~1,800 tokens for analysis, ~140 lines output
