# Anthropic Context Engineering Primer

> Distilled from [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Anthropic Applied AI team, Sep 2025)

Actionable primitives extracted from the source article. For the Three Laws and operational patterns, see the parent [SKILL.md](../SKILL.md).

## Context Engineering vs Prompt Engineering

Prompt engineering optimizes how to **write** instructions for one-shot tasks. Context engineering optimizes the **entire token state** across multi-turn agent sessions: system instructions, tools, MCP, external data, message history.

The shift: agents running in a loop generate data that *could* be relevant for the next turn. Context engineering is the iterative curation of what enters the limited window from that constantly evolving universe.

## Why Context Degrades: Architectural Constraints

**Context rot**: as token count increases, the model's ability to accurately recall information decreases. This emerges across all models, though degradation curves vary.

Root causes:
- **n² attention scaling**: Every token attends to every other token. For n tokens, the model must maintain n² pairwise relationships. This stretches thin at scale.
- **Training distribution bias**: Models see shorter sequences more often during training. Fewer specialized parameters exist for long-range context dependencies.
- **Position encoding interpolation**: Allows longer sequences but with reduced precision for token position understanding.

**Implication**: Context is a finite resource with diminishing marginal returns. Like human working memory — limited capacity, requires external systems (notes, indexes) for persistence.

## System Prompt Design

- Use simple, direct language at the right altitude (see SKILL.md §Right Altitude)
- Organize with distinct sections using XML tags or Markdown headers
- Strive for the **minimal set that fully outlines expected behavior**
- Start minimal with the best model → add instructions based on observed failure modes
- "Minimal" does not mean short — it means zero noise

## Tool Design Principles

- Tools define the contract between agents and their action space
- Must be self-contained, robust to error, extremely clear in intended use
- Input parameters: descriptive, unambiguous, play to model strengths
- **Most common failure**: bloated tool sets with overlapping functionality
- Test: if a human engineer can't definitively say which tool to use, the agent can't either

## Example Curation

- Few-shot prompting remains strongly advised
- **Anti-pattern**: stuffing laundry lists of edge cases into prompts
- **Better**: curate diverse, canonical examples that portray expected behavior
- For an LLM, examples are the "pictures" worth a thousand words

## Hybrid Retrieval Strategy

Most effective agents combine:

| Strategy | Mechanism | Trade-off |
|---|---|---|
| Pre-inference retrieval | Embed data up front (CLAUDE.md, AGENTS.md) | Fast but static |
| Just-in-time retrieval | Lightweight identifiers loaded at runtime via tools | Slower but current |

**Progressive disclosure**: agents incrementally discover context through exploration. Each interaction yields signals (file sizes suggest complexity, naming conventions hint at purpose, timestamps proxy relevance) that inform the next retrieval decision.

**Claude Code example**: CLAUDE.md loaded passively up front. Glob and grep navigate the environment just-in-time, bypassing stale indexing and complex syntax trees.

**Guidance**: "Do the simplest thing that works." As models improve, agentic design trends toward letting intelligent models act intelligently with progressively less curation.

## Key Principle

> Find the smallest set of high-signal tokens that maximize the likelihood of the desired outcome.

Every technique in this skill — passive context, indexes, compaction, sub-agents — serves this single objective.

---

*Version: 1.0.0 | Updated: 2026-02-11*
