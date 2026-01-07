---
argument-hint: target-branch (e.g., "main")
description: Create a PR with integrated quality gate (code review + security review)
---

If $ARGUMENTS is empty, first use AskUserQuestion to ask "¿A qué rama destino quieres dirigir el Pull Request?" with options from `git branch -r | grep -v HEAD | sed 's/origin\///' | head -5`.

Then invoke the ai-framework:pr-workflow skill and follow it exactly, using $ARGUMENTS as the target branch.
