---
name: git-pullrequest
argument-hint: target-branch (e.g., "main")
---

1. Use the Skill tool to load skill: `ai-framework:git-pullrequest`
2. If `$ARGUMENTS` is empty, use AskUserQuestion to ask: "¿A qué rama destino quieres dirigir el Pull Request?" with options for common branches (main, develop, staging)
3. Execute the skill with the target branch
