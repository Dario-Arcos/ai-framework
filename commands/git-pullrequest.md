---
name: git-pullrequest
argument-hint: target-branch (e.g., "main")
---

If $ARGUMENTS is empty, first use AskUserQuestion to ask "¿A qué rama destino quieres dirigir el Pull Request?" with options from `git branch -r | grep -v HEAD | sed 's/origin\///' | head -5`.

Then invoke the ai-framework:git-pullrequest skill and follow it exactly, using $ARGUMENTS as the target branch.
