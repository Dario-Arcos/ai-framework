# Effective AI Agents: Context Engineering Guide

**Source**: [Effective Context Engineering for AI Agents](https://www.anthropic.com/research/effective-context-engineering) (Anthropic Research, Sept 2025)
**Scope**: Mandatory parameters for designing, creating, and operating AI agents

---

## Golden Rule

> **"Find the smallest possible set of high-signal tokens that maximize the likelihood of your desired outcome."**

Context is finite. Every token depletes attention budget. More context ≠ better performance.

---

## Core Truths

1. **Context Rot**: As token count increases, recall precision decreases
2. **Attention Budget**: Limited capacity that must be preserved
3. **Diminishing Returns**: There's an optimal context window; exceeding it degrades performance

---

## System Prompts

**Right Altitude Principle:**

- ❌ Too specific: Hardcoded logic, brittle if-else chains
- ❌ Too vague: "Be helpful", assumed shared context
- ✅ Optimal: Clear signals, flexible heuristics

**Rules:**

1. Use extremely clear, simple, direct language
2. Start minimal, add only based on observed failures
3. Continuously prune what doesn't change behavior
4. Organize with clear sections (background, instructions, examples, output format)

**Test:** Can I remove any instruction without degrading behavior?

---

## Tool Design

**Critical Rule:**
If a human engineer can't definitively say which tool to use in a situation, an AI agent can't either.

**Requirements:**

1. **Clarity**: Name, description, parameters unambiguous
2. **Single responsibility**: No functional overlap between tools
3. **Token efficiency**: Return concise, high-signal outputs
4. **Self-contained**: Handle own errors, no external dependencies

**Curation over accumulation**: Fewer well-designed tools > many overlapping ones

---

## Examples & Few-Shot

**Always use few-shot prompting.** For LLMs, examples are pictures worth a thousand words.

**Rules:**

1. Choose canonical, diverse examples (not edge case exhaustiveness)
2. Show patterns, let model generalize
3. Quality > quantity (3-5 good examples > 20 mediocre)
4. Use real-world scenarios

❌ "Here are 20 edge cases you must handle..."
✅ "Example 1: [core case]. Example 2: [key variant]. Example 3: [boundary]."

---

## Dynamic Context ("Just in Time")

**Strategy:**
Maintain lightweight identifiers (file paths, links), load data dynamically at runtime using tools.

**Rules:**

1. Keep references, not full content, in context
2. Load exactly what's needed, when needed
3. Leverage metadata (paths, names, timestamps) as refinement signals
4. Enable progressive disclosure (layer-by-layer assembly)

**Example:**

- Store: `src/components/auth.tsx` (23 bytes)
- NOT: Full file content (2000+ tokens)
- Load only when working on auth features

**Trade-off:**
Runtime exploration is slower but more context-efficient. Use hybrid: pre-load critical data, explore rest just-in-time.

---

## Long-Horizon Tasks

When token count exceeds context window or task spans extended time:

### 1. Compaction (simplest)

Summarize conversation, reinitiate with compressed version.

- **Preserve**: Decisions, bugs, implementation details, constraints
- **Discard**: Redundant tool outputs, verbose exchanges, superseded decisions

### 2. Structured Note-Taking

Persist memory outside context (to-do lists, NOTES.md, progress logs).

- **Use for**: Multi-session coherence, complex task tracking
- **Minimal overhead**: Simple formats, agent-driven structure

### 3. Sub-Agent Architectures

Specialized agents explore in parallel, return concise summaries.

- **Use for**: Complex research, parallel exploration
- **Contract**: Main agent coordinates, sub-agents explore deeply but return lightly

**Decision Matrix:**

| Technique   | Best For                                      |
| ----------- | --------------------------------------------- |
| Compaction  | Extensive back-and-forth conversation         |
| Note-Taking | Iterative development with clear milestones   |
| Sub-Agents  | Complex research, parallel exploration needed |

---

## Daily Practices

Before adding context:

- [ ] Does this increase likelihood of desired outcome?
- [ ] Is this the most concise way to provide this information?
- [ ] Can I justify the token cost?

Before finalizing:

- [ ] Can I remove anything without degrading behavior?
- [ ] Is signal-to-noise ratio high?
- [ ] Would a new contributor understand intent in one sitting?

During execution:

- [ ] Am I loading data just-in-time vs pre-loading?
- [ ] Are tool names/purposes unambiguous?
- [ ] Am I using examples instead of lengthy instructions?

For long tasks:

- [ ] Have I cleared redundant context?
- [ ] Am I maintaining working memory vs exhaustive history?
- [ ] Is appropriate strategy active (compaction/notes/sub-agents)?

---

## Integration with Trivance Constitution

Context engineering directly supports constitutional mandates:

- **Value/Complexity Ratio**: Efficient context = higher ROI
- **Simplicity**: Golden Rule enforces "simplest that works"
- **AI-First**: Optimized for LLM execution by design

---

## Quick Reference

**Three Actions to Take Now:**

1. Review system prompts: eliminate instructions that don't change behavior
2. Audit tool set: remove overlapping tools, clarify ambiguous ones
3. Add 3-5 canonical examples to critical workflows

**One Question to Ask Always:**
"What's the smallest context that achieves this outcome?"

---

**Version**: 1.0.0 (2025-10-01) | 145 lines | High-signal only
