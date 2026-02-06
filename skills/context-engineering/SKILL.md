---
name: context-engineering
description: Use when designing system prompts, CLAUDE.md files, AGENTS.md, tool schemas, or agent architectures. Use when agents underperform despite correct instructions, fail to use available tools, lose coherence in long tasks, or when optimizing token efficiency for context windows.
---

# Context Engineering

## Overview

Find the smallest set of high-signal tokens that maximize desired agent behavior. Context is finite with diminishing returns -- past a threshold, more tokens degrade performance. The goal is precise curation: what to include, what to exclude, how to structure what remains.

## When to Use

- Designing or auditing system prompts, CLAUDE.md, AGENTS.md
- Agent underperforms despite correct instructions being present
- Agent ignores available tools (56% non-invocation rate in Vercel evals)
- Long-running tasks lose coherence or drift from original intent
- Optimizing token efficiency within context windows
- Choosing between passive context vs active retrieval strategies
- Building compressed indexes for documentation
- Diagnosing why wording changes produce wildly different agent behavior
- Architecting multi-agent systems with context isolation

## When NOT to Use

| Situation | Use Instead |
|-----------|-------------|
| Writing new skill documentation | writing-skills |
| Debugging specific code failures | systematic-debugging |
| One-shot prompt for simple task | Standard prompt engineering |
| API-specific documentation needs | Context7 MCP |
| Frontend component design | frontend-design |

## Three Laws of Context Delivery

Priority-ordered. When laws conflict, higher-numbered laws yield to lower.

### Law 1: Passive Over Active

Embed critical context directly in system prompt or AGENTS.md. Never require the agent to decide to retrieve it.

**The core problem with active retrieval**: agents must DECIDE to invoke a tool or read a file. That decision point is unreliable. The agent may not recognize it needs the information, may choose a different approach, or may simply skip the retrieval step.

Vercel eval data across four configurations:

| Configuration | Pass Rate | Delta |
|---------------|-----------|-------|
| Baseline (no docs) | 53% | -- |
| Skill (default) | 53% | +0pp |
| Skill + explicit instructions | 79% | +26pp |
| AGENTS.md docs index (passive) | 100% | +47pp |

**Rule**: If the agent needs it every session, embed it. If it needs it sometimes, provide a visible index entry that triggers retrieval without requiring a decision.

**Boundary**: Law 1 has diminishing returns when passive context exceeds ~8KB. Past that threshold, use Law 2 (index) instead of inlining more content.

### Law 2: Index Over Inline

A compressed index (~8KB) is as effective as full documentation (~40KB). Provide navigation maps, not full content. The agent reads specific files on demand.

```
[Docs Index]|root: ./.docs
|IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning
|routing:{defining-routes.mdx,dynamic-routes.mdx,middleware.mdx}
|caching:{use-cache.mdx,cache-life.mdx,revalidation.mdx}
|auth:{session-management.mdx,authorization.mdx}
```

| Metric | Full Docs | Compressed Index | Impact |
|--------|-----------|-----------------|--------|
| Size | ~40KB | ~8KB | 80% reduction |
| Pass Rate | -- | 100% | No measurable degradation in Vercel evals (2025) |
| Agent behavior | Attention diluted across content | Focused retrieval of specific files | More precise |

### Law 3: Retrieve Don't Remember

Use lightweight identifiers (file paths, search queries, URLs) loaded at runtime. Don't preload everything into context. Progressive disclosure beats exhaustive loading.

**Pattern**: Reference -> locate -> read on demand.

**Implementation**: Store file paths (not contents), search queries (not results), URLs (not page content). Let the agent read/fetch at the step that needs it.

## The Right Altitude

System prompts operate in a Goldilocks zone. Too specific and they break on edge cases. Too vague and agents lack actionable guidance. The right altitude provides heuristics -- rules of thumb that guide judgment without scripting every decision.

| Level | Characteristics | Failure Mode |
|-------|----------------|-------------|
| Too Low (hardcoded) | If-else logic, exact commands, specific filenames | Breaks on first edge case, high maintenance |
| Too High (vague) | Abstract goals, no concrete signals | Agent invents approach, often wrong |
| Right Altitude | Clear heuristics, concrete boundaries, flexible application | Rarely fails; degrades gracefully |

**Before/After**:

```
Too Low:  "If user says 'deploy', run `npm run build && npm run deploy`.
           If user says 'test', run `npm test`."

Too High: "Help the user with their project."

Right:    "Run the project's build pipeline before deployment.
           Verify tests pass before committing.
           When build fails, diagnose root cause before retrying."
```

**How to find the right altitude**: Write the instruction. Then ask: "Would this work if the project used a different build tool?" If the answer is no, you're too low. Ask: "Does this give the agent enough information to act without guessing?" If the answer is no, you're too high.

**Wording fragility**: Small phrasing changes produce large behavioral swings. The fix is structural (Law 1: make it passive) rather than linguistic (finding the perfect wording).

## Attention Budget Management

Every component in the context window competes for attention. The total budget is fixed. Adding tokens to one component steals attention from all others.

| Component | Optimize By |
|-----------|------------|
| System prompt | Minimal set that fully outlines behavior. Start minimal, add only based on observed failure modes |
| Tools | Self-contained descriptions, no overlap. If a human can't choose between two tools, neither can the agent |
| Examples | Curate diverse canonical set. One excellent example beats ten mediocre ones |
| Message history | Compaction when approaching limits. Clear old tool results that are no longer relevant |
| External data | Just-in-time loading via references (Law 3), not preloading |

**The subtraction test**: Remove a token from the prompt. Did behavior degrade? No? It was noise. Keep removing until every remaining token is load-bearing.

**Fixed vs variable costs**: System prompt and tool descriptions persist every turn (fixed). Message history and external data grow (variable). As variable costs grow, attention for fixed costs shrinks — this is why long conversations degrade.

## Retrieval-Led Reasoning

```
IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning.
```

Training data decays. For external APIs, frameworks, or version-specific knowledge, retrieve current documentation rather than relying on training knowledge. Without this instruction, agents generate code using deprecated APIs that passes syntax checks but fails at runtime.

**When to apply**: External dependencies with version-specific APIs, recently released features, frameworks with breaking changes between versions.

**Implementation**: Use Context7 MCP for library docs, read local project files via native tools, or search the web. Always verify the current year when searching documentation.

## Long-Horizon Strategies

When tasks exceed the context window or span many turns, use compaction, structured notes, or sub-agents. See [compaction-patterns.md](compaction-patterns.md) for implementation details, strategy selection, and prompt templates.

| Strategy | Use When | Core Mechanism |
|----------|----------|---------------|
| Compaction | Context approaching limit | Summarize → reinitiate (recall first, then precision) |
| Structured Notes | State must survive compaction | Write to disk → read back on demand |
| Sub-Agents | Task decomposes into independent parts | Clean context per agent → return 1-2K summary |

## Diagnostic: Why Is My Agent Failing?

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Ignores available tools | Active retrieval requiring decision | Law 1: Make context passive |
| Uses outdated APIs | Pre-training-led reasoning | Add retrieval-led reasoning instruction |
| Loses coherence after many turns | Context rot / attention dilution | Implement compaction (see [compaction-patterns.md](compaction-patterns.md)) |
| Inconsistent behavior across runs | Wording fragility in prompts | Stabilize with examples, not edge-case rules |
| Generates wrong code despite docs | Docs too large, diluting attention | Law 2: Compress to index |
| Skips important instructions | Instructions buried in noise | Apply subtraction test, reduce to high-signal tokens |
| Different wording produces different results | Right altitude miscalibration | Rewrite at correct altitude with heuristics |
| Tool chosen incorrectly between similar options | Overlapping tool descriptions | Make each tool self-contained with no overlap |
| Works on simple tasks, fails on complex ones | Context budget exhausted by task complexity | Decompose into sub-agents with isolated context |
| Agent hallucinates tool names | Tool not in context or name ambiguous | Verify tool is in active context; simplify tool naming |
| Agent calls tools in wrong order | Missing sequencing heuristics | Add explicit dependency guidance in tool descriptions |
| Agent loops retrying same failed action | No error-recovery heuristic | Add "on failure: diagnose root cause, then change approach" |
| Quality degrades mid-session (not just coherence) | Accumulated noise from tool results | Clear old tool results; compact before quality loss compounds |

## Validation

Measure context engineering changes with behavior-based evals, not subjective assessment:

- **Before/after pass rate**: Run the same task set before and after changes. Track % of correct completions.
- **Token tracking**: Measure total tokens consumed per task. Lower tokens with same pass rate = better signal density.
- **Coherence spot-check**: At turn N (e.g., turn 20, 40), verify the agent can recall key decisions from early turns.
- **Tool invocation rate**: Track % of available tools actually used. Low rate signals Law 1 violations.
- **Subtraction test**: Remove one section at a time. If pass rate holds, the section was noise.

## References

- [compaction-patterns.md](compaction-patterns.md) -- Long-horizon strategies: compaction, structured notes, sub-agent architectures
- [Anthropic: Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Vercel: AGENTS.md Outperforms Skills](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)
