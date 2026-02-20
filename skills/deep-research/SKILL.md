---
name: deep-research
description: Use when researching a topic in depth with verification — technology decisions, API comparisons, or architecture exploration.
---

# AI-Native Deep Research

Systematic research methodology optimized for AI agent execution.

Research topic: $ARGUMENTS

## Core Principles

| Principle | Implementation |
|-----------|----------------|
| **Attention Budget** | Treat context as finite resource with diminishing returns |
| **Multi-pass RAG** | 3-5 iterative search rounds, not single-pass |
| **Confidence Transparency** | Rate every claim (High/Medium/Low/Uncertain) |
| **Citation Granularity** | Source at sentence level, not paragraph |
| **Cross-validation** | Minimum 3 sources for material claims |

## Anti-Hallucination Protocol

AI researching has different failure modes than humans:

1. **Confabulation risk**: AI may generate plausible-sounding but fabricated details
2. **Citation fabrication**: Studies show 17-56% of AI citations contain errors
3. **Recency blindness**: Training data is stale — always verify current info
4. **Authority confusion**: AI may conflate rumor with fact

Countermeasures: real browser navigation, multi-source cross-validation, explicit uncertainty, source confidence ratings.

## Execution Flow

### Phase 0: Research Planning

- If `$ARGUMENTS` is empty or vague: Use AskUserQuestion to clarify scope
- Decompose into 3-7 sub-questions prioritized by information value
- Map sub-questions to source tiers (read [references/source-hierarchy.md](references/source-hierarchy.md))
- Display research plan with sub-questions, target sources, estimated passes

### Phase 1: Primary Research (Browser Navigation)

**CRITICAL**: Use `agent-browser` skill for ALL web navigation. Never WebFetch/WebSearch.

```bash
agent-browser open [URL]
agent-browser snapshot -i
agent-browser click @[relevant-section]
agent-browser screenshot evidence-[n].png
```

Navigate source hierarchy systematically: Tier 1 → Tier 2 → Tier 3.
Read [references/source-hierarchy.md](references/source-hierarchy.md) for tier definitions and navigation patterns.

Document immediately per source: URL, date accessed, tier, key claims, limitations.

### Phase 2: Iterative Refinement

Minimum 3 passes:

```
Pass 1: Primary sources → Core facts
Pass 2: Secondary sources → Confirmation + depth
Pass 3: Corroborative → Fill gaps + resolve conflicts
Pass 4+: Specialized sources for remaining gaps
```

Track coverage per sub-question: [N/3 sources] [Status: Confirmed/Needs more/Uncertain]

### Phase 3: Cross-Validation & Verification

For each material claim:
- Minimum 3 independent sources
- At least 1 Tier 1 source
- Check recency (prefer last 12 months)
- Identify potential biases

When sources disagree: document both positions, assess reliability hierarchy, note uncertainty explicitly, do NOT silently pick one version.

Read [references/evidence-standard.md](references/evidence-standard.md) for confidence ratings and report template.

### Phase 4: Synthesis & Report

Apply quality gates before delivering:
- Every factual claim has inline citation
- Confidence ratings assigned to all findings
- Conflicts documented, not hidden
- Limitations explicitly stated
- Actionable recommendations provided

After quality gates pass:
- Invoke humanizer on the synthesized report — research prose is especially vulnerable to inflated significance, vague attributions, filler phrases, and generic conclusions

## Context Management (Anti-Context-Rot)

1. Every 5 sources: summarize findings so far
2. Keep running list of confirmed facts vs. pending
3. Don't retain raw HTML — extract and discard
4. If approaching token limits: summarize, clear intermediates, keep only confirmed claims + URLs + pending questions
