---
name: context-engineering
version: 1.0.0
description: >
  This skill should be used when the user asks to "design a system prompt",
  "audit CLAUDE.md", "create AGENTS.md", "optimize context window",
  "fix agent that ignores tools", "improve agent coherence", "build a docs index",
  or when diagnosing why agents underperform despite correct instructions.
  Provides the Three Laws of Context Delivery, attention budget management,
  and long-horizon strategies for building high-performance AI agents.
---

# Context Engineering

## Overview

Find the smallest set of high-signal tokens that maximize desired agent behavior. Context is finite with diminishing returns — past a threshold, more tokens degrade performance. The goal is precise curation: what to include, what to exclude, how to structure what remains.

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
|---|---|
| Writing new skill documentation | skill-creator |
| Debugging specific code failures | systematic-debugging |
| One-shot prompt for simple task | Standard prompt engineering |
| API-specific documentation needs | Context7 MCP |
| Frontend component design | frontend-design |

## Three Laws of Context Delivery

Priority-ordered. When laws conflict, higher-numbered laws yield to lower.

### Law 1: Passive Over Active

Embed critical context directly in system prompt or AGENTS.md. Never require the agent to decide to retrieve it.

The core problem: agents must DECIDE to invoke a tool or read a file. That decision point is unreliable — in Vercel evals, agents failed to invoke available skills in 56% of cases. See [references/passive-context-patterns.md](references/passive-context-patterns.md) for full empirical data.

| Configuration | Pass Rate | Delta |
|---|---|---|
| Baseline (no docs) | 53% | — |
| Skill (default) | 53% | +0pp |
| Skill + explicit instructions | 79% | +26pp |
| AGENTS.md docs index (passive) | 100% | +47pp |

**Rule**: If the agent needs it every session, embed it. If it needs it sometimes, provide a visible index entry that triggers retrieval without requiring a decision.

**Boundary**: Diminishing returns when passive context exceeds ~8KB. Past that threshold, use Law 2 instead.

### Law 2: Index Over Inline

A compressed index (~8KB) is as effective as full documentation (~40KB). Provide navigation maps, not full content. The agent reads specific files on demand.

```
[Docs Index]|root: ./.docs
|IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning
|routing:{defining-routes.mdx,dynamic-routes.mdx,middleware.mdx}
|caching:{use-cache.mdx,cache-life.mdx,revalidation.mdx}
|auth:{session-management.mdx,authorization.mdx}
```

80% token reduction, zero measurable pass rate degradation (Vercel evals, 2026).

### Law 3: Retrieve Don't Remember

Store lightweight identifiers (file paths, search queries, URLs) — not contents. Load at runtime. Progressive disclosure beats exhaustive loading.

**Pattern**: Reference → locate → read on demand.

## The Right Altitude

System prompts operate in a Goldilocks zone between two failure modes:

| Level | Characteristics | Failure Mode |
|---|---|---|
| Too Low (hardcoded) | If-else logic, exact commands | Breaks on first edge case |
| Too High (vague) | Abstract goals, no concrete signals | Agent invents approach, often wrong |
| Right Altitude | Clear heuristics, concrete boundaries | Degrades gracefully |

```
Too Low:  "If user says 'deploy', run `npm run build && npm run deploy`."
Too High: "Help the user with their project."
Right:    "Run the project's build pipeline before deployment.
           Verify tests pass before committing.
           When build fails, diagnose root cause before retrying."
```

### Altitude Test

1. Write the instruction.
2. "Would this work if the project used a different build tool?" → No = too low.
3. "Does this give the agent enough to act without guessing?" → No = too high.
4. Repeat until both answers are yes.

**Wording fragility**: Small phrasing changes produce large behavioral swings. The fix is structural (Law 1: make it passive) rather than linguistic (finding the perfect wording).

## Attention Budget Management

Every token competes for finite attention. Adding tokens to one component steals from all others.

| Component | Optimize By |
|---|---|
| System prompt | Minimal set that fully outlines behavior. Add only based on observed failure modes |
| Tools | Self-contained descriptions, no overlap. If a human can't choose between two tools, neither can the agent |
| Examples | One excellent example beats ten mediocre ones |
| Message history | Clear old tool results before full compaction |
| External data | Just-in-time loading via references (Law 3) |

**Subtraction test**: Remove a token. Did behavior degrade? No? It was noise. Keep removing until every remaining token is load-bearing.

**Fixed vs variable costs**: System prompt and tools persist every turn (fixed). History and external data grow (variable). As variable costs grow, attention for fixed costs shrinks — this is why long conversations degrade.

## Retrieval-Led Reasoning

```
IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning.
```

Training data decays. For external APIs, frameworks, or version-specific knowledge, retrieve current documentation rather than relying on training knowledge. Without this instruction, agents use deprecated APIs that pass syntax checks but fail at runtime.

**When to apply**: External dependencies with version-specific APIs, recently released features, frameworks with breaking changes between versions.

## Long-Horizon Strategies

When tasks exceed the context window, use compaction, structured notes, or sub-agents. See [references/long-horizon-patterns.md](references/long-horizon-patterns.md) for implementation details, strategy selection, and prompt templates.

| Strategy | Use When | Core Mechanism |
|---|---|---|
| Compaction | Context approaching limit | Summarize → reinitiate |
| Structured Notes | State must survive compaction | Write to disk → read back |
| Sub-Agents | Independent subtasks | Clean context per agent → 1-2K summary |
| Compressed Index | Large codebase navigation | Passive map eliminates search decisions |

## Diagnostic

| Symptom | Likely Cause | Fix |
|---|---|---|
| Ignores available tools | Active retrieval requiring decision | Law 1: Make context passive |
| Uses outdated APIs | Pre-training-led reasoning | Add retrieval-led reasoning instruction |
| Loses coherence after many turns | Context rot / attention dilution | Implement compaction ([long-horizon-patterns](references/long-horizon-patterns.md)) |
| Inconsistent behavior across runs | Wording fragility | Stabilize with examples, not edge-case rules |
| Generates wrong code despite docs | Docs too large, diluting attention | Law 2: Compress to index |
| Skips important instructions | Instructions buried in noise | Apply subtraction test |
| Works on simple, fails on complex | Context budget exhausted | Decompose into sub-agents |
| Agent loops retrying same action | No error-recovery heuristic | Add "on failure: diagnose, then change approach" |

## Validation

Measure with behavior-based evals, not subjective assessment:

- **Before/after pass rate**: Same task set, track % correct completions
- **Token tracking**: Lower tokens + same pass rate = better signal density
- **Coherence spot-check**: At turn N, verify recall of early decisions
- **Tool invocation rate**: Low rate signals Law 1 violations
- **Subtraction test**: Remove one section. Pass rate holds? It was noise

## Integration

- **skill-creator**: Apply Three Laws and Right Altitude when designing skill descriptions and content structure
- **systematic-debugging**: Use the Diagnostic table to identify context engineering root causes in agent failures
- **verification-before-completion**: Validation metrics above align with evidence-based completion gates

## References

- [references/long-horizon-patterns.md](references/long-horizon-patterns.md) — Compaction, structured notes, sub-agents, compressed indexes
- [references/anthropic-context-primer.md](references/anthropic-context-primer.md) — Theoretical foundations: context rot, attention architecture, hybrid retrieval
- [references/passive-context-patterns.md](references/passive-context-patterns.md) — Empirical evidence: Vercel evals, passive vs active, eval design
- [Anthropic: Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (source article)
- [Vercel: AGENTS.md Outperforms Skills](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) (source article)
