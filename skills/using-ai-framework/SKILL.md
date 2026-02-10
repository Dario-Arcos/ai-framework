---
name: using-ai-framework
description: Skill and agent enforcement rules. Injected automatically at session start — invoke manually only if enforcement context appears missing.
---

Invoke matching skills BEFORE responding. Only skip when CERTAIN no skill applies — if in doubt, invoke. False positives are cheap; missed skills are expensive.

If an invoked skill turns out wrong for the situation, you don't need to follow it.

- **Skills**: Use the `Skill` tool. Content loads on invocation — follow it directly.
- **Agents**: Dispatch via `Task` tool with matching `subagent_type` when context matches.

## Red Flags

If you think any of these, STOP and invoke:

| Thought | Reality |
|---------|---------|
| "I can handle this with my training" | Training is stale. Skills have current methodology. |
| "The skill is overkill for this" | Simple things become complex. Invoke anyway. |
| "Let me explore first" | Skills tell you HOW to explore. Invoke first. |
| "I already know this" | Skills evolve. Load the current version. |

## Priority

Process skills first (brainstorming, debugging, discovery) — determine HOW to approach.
Then implementation skills (scenario-driven-development, frontend-design) — guide execution.

"Build X" → brainstorming first, then implementation skills.
"Fix this bug" → systematic-debugging first, then domain-specific skills.

## Agents

Auto-delegated reasoning modules — dispatch via Task tool when context matches:

- code-reviewer: after implementation step → SDD compliance + reward hacking detection
- systematic-debugger: bug or unexpected behavior → 4-phase root cause before any fix
- security-reviewer: branch changes for review → exploitable vulnerabilities in diff
- edge-case-detector: after implementation → boundary violations, concurrency, resource leaks
- performance-engineer: bottleneck or scalability → profiling, optimization
- code-simplifier: after code written → reduce complexity preserving function
