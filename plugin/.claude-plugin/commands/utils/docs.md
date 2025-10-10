---
description: Analyze and update project documentation using specialist agents
argument-hint: "README | API | CHANGELOG | specific docs to focus on"
allowed-tools: Read, Write, Edit, MultiEdit, Bash, Grep, LS, Glob, Task, TodoWrite
---

# Documentation Management

**Analyze and update project documentation:** $ARGUMENTS

## Process

1. **Analyze** existing documentation (README, CHANGELOG, docs/\*)
2. **Identify** gaps and outdated content
3. **Delegate** to documentation specialist via Task tool
4. **Update** or create documentation as needed

## Usage

```bash
/docs                    # Analyze all documentation
/docs README API         # Focus on specific docs
/docs CHANGELOG          # Update changelog only
```

## Capabilities

- Gap analysis and documentation planning
- Content creation with project templates
- Technical accuracy validation
- Integration with specialist agents for complex documentation tasks
