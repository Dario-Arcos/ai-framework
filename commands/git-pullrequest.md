---
name: git-pullrequest
argument-hint: target-branch (e.g., "main")
---

## Pre-check

1. Verify git repository: `git rev-parse --git-dir`
2. Verify remote exists: `git remote get-url origin`

## Determine Target Branch

**If `$ARGUMENTS` provided:**
- Use `$ARGUMENTS` as target branch (e.g., `/git-pullrequest main`)

**If `$ARGUMENTS` empty:**
1. List available remote branches: `git branch -r | grep -v HEAD | sed 's/origin\///' | head -5`
2. Use AskUserQuestion:
   - Question: "¿A qué rama destino quieres dirigir el Pull Request?"
   - Header: "Target Branch"
   - Options: Include discovered branches (main, develop, etc.) from step 1

## Execute Skill

Invoke the Skill tool with:
- skill: `ai-framework:git-pullrequest`

The skill reads `$ARGUMENTS` (target branch) and executes the full PR workflow:
1. Phase 1: Validate & extract context
2. Phase 2: Quality gate (code review + security review + observations)
3. Phase 2b: Auto fix (if user chooses)
4. Phase 3: Create PR

See `skills/git-pullrequest/SKILL.md` for detailed workflow.
