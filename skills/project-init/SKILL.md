---
name: project-init
description: Generates project memory (.claude/rules/) — project context, architecture, stack, and conventions that Claude loads every session
---

# Project Initialization

Builds the project's technical memory: rule files Claude loads automatically alongside CLAUDE.md.

**Purpose**: High-signal project context preventing wrong assumptions, wrong placement, wrong patterns
**Output**: 4 rule files in `.claude/rules/` (~130 lines, <2000 tokens total)

## Output Files

```
.claude/rules/              ← TRACKED (versioned, reviewable in PRs)
├── project.md              ← WHAT: purpose, paradigms, domain concepts
├── architecture.md         ← HOW: layers, boundaries, data flow
├── stack.md                ← WITH WHAT: runtime, deps, scripts
└── conventions.md          ← HOW TO WRITE: naming, errors, imports, testing
```

Each file answers ONE question. Zero overlap between files. Zero overlap with CLAUDE.md.

## Workflow

### Phase 1: Detect & Prepare

1. Check for existing `.claude/rules/*.md`
2. If rules exist → read them for diff reporting in Phase 4
3. `mkdir -p .claude/rules/`

### Phase 2: Auto-Analysis

Execute all 5 analysis layers. Read [references/analysis-layers.md](references/analysis-layers.md) for extraction patterns and heuristics.

**Layer 1: Manifests** → runtime, framework, dependencies, scripts, project type, description
**Layer 2: Configs** → compiler, formatter, test framework, CI/CD, Docker
**Layer 3: Structure** → layers, entry points, boundaries, file distribution
**Layer 4: Patterns** → naming, error handling, imports, paradigms, testing
**Layer 5: Sampling** → 5-8 key files for style confirmation and domain signals

Synthesize layer outputs into rule files. Read [references/rule-templates.md](references/rule-templates.md) for output templates and field guidance.

### Phase 3: Context Engineering Gate

Before writing, validate generated rules against context-engineering principles:

1. **Subtraction test**: Remove each line — does it prevent a wrong Claude decision? No → delete it
2. **Attention budget**: Total output must stay under ~2000 tokens. Compress if over
3. **Right altitude**: Each rule must work across project variations (not hardcoded) while giving enough to act (not vague)
4. **CLAUDE.md overlap**: If CLAUDE.md already says it, the rule is redundant noise. Remove
5. **Signal density**: Every line must pass: "Without this line, Claude would do X wrong"

### Phase 4: Present & Write

1. **Diff report** (if rules existed before):
   - Show what changed per file (added/removed/modified lines)
   - Highlight significant changes ("Added Redis as cache layer", "Testing framework changed to Vitest")
2. **User review**: Present generated rules for approval before writing
3. **Write** to `.claude/rules/`
4. **Summary**: Files generated, line counts, key findings

## Modes

### First Run (no existing rules)
Full flow: Analysis (2) → Gate (3) → Write (4)

### Update Run (rules exist)
Same flow, but Phase 4 shows diff vs previous rules.

## Notes

- **conventions.md absorbs testing**: Testing conventions (framework, commands, patterns) live as a section in conventions.md, not a separate file. Section omitted if no tests detected.
- **Staleness signal**: If rules were generated >90 days ago AND manifest files changed significantly, suggest re-running at session start.
- **Token discipline**: Rules are loaded EVERY session. Every excess token is a permanent tax on Claude's attention budget.
