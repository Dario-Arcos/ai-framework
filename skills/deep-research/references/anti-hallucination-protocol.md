# Anti-Hallucination Protocol

## Empirical Basis

| Finding | Source | Implication |
|---------|--------|-------------|
| 16.7% of ICLR 2026 papers had fabricated citations that expert reviewers did not detect | ICLR 2026 reproducibility audit | Citation fabrication is invisible without URL verification |
| Reasoning models hallucinate >10% on factual extraction tasks | Vectara Hallucination Leaderboard 2026 | Stronger reasoning ≠ more accurate facts |
| Retrieval augmentation improves accuracy 30-55pp over standalone on SimpleQA | SimpleQA benchmark | Tool-assisted retrieval is non-negotiable for factual claims |
| Claude achieves 93-94% citation accuracy but produces fewer citations than competitors | LLM citation accuracy studies | High accuracy per citation, but coverage gaps require explicit search effort |
| Multi-perspective research nearly doubles reference coverage (99.83 vs 39.56) | STORM methodology evaluation | Single-perspective research misses half the evidence |

## Hallucination Modes

### 1. Confabulation

**What it is**: Generating plausible-sounding facts from training patterns without any source.

**Detection signals**: Claims stated with high confidence but no URL. Smooth, detailed narratives without citations. Specific numbers or dates without attribution.

**Constraints:**
- You MUST NOT state facts without a navigated URL because confabulation is the dominant failure mode in AI research
- You MUST prefix unsourced knowledge with "Based on training knowledge (unverified):" when used for planning or hypothesis generation only
- You MUST NOT use training knowledge for factual claims in the final output

### 2. Citation Fabrication

**What it is**: Generating URLs, DOIs, or paper titles that do not exist or do not contain the claimed information.

**Detection signals**: URLs that return 404. Papers attributed to authors who did not write them. DOIs that do not resolve.

**Constraints:**
- You MUST verify that a URL loads successfully before citing it because 16.7% of AI citations are fabricated
- You MUST verify that the cited page actually contains the claimed information
- You MUST NOT cite a URL based on what you expect it to contain

### 3. Plausible Interpolation

**What it is**: Filling gaps between known facts with reasonable-sounding but unverified connections.

**Detection signals**: Words like "typically", "generally", "usually", "it is well-known that". Statements that bridge two sourced facts with unsourced connective logic.

**Constraints:**
- You MUST NOT use "typically", "generally", "usually", or "it is common" as evidence because these signal training-knowledge reasoning, not retrieval
- You MUST flag interpolated connections explicitly: "No source confirms the connection between A and B"
- You SHOULD search for the specific connection before assuming it exists

### 4. Temporal Confusion

**What it is**: Presenting outdated information as current, or mixing facts from different time periods.

**Detection signals**: Statistics without dates. Version-specific claims without version numbers. "Currently" or "recently" without timestamps.

**Constraints:**
- You MUST record the source date for every claim because recency determines reliability for time-sensitive topics
- You MUST flag claims from sources older than 12 months for time-sensitive research types
- You MUST NOT use "currently" or "recently" without a specific date or version

### 5. Authority Laundering

**What it is**: A secondary source cites a primary source; the AI cites the secondary as if it were the primary, inflating perceived authority.

**Detection signals**: Blog posts citing research papers. News articles citing government data. Aggregator sites citing original reports.

**Constraints:**
- You MUST navigate to the primary source when a secondary source cites it because authority laundering inflates weak evidence
- You MUST cite the primary source, not the secondary, when the primary is accessible
- You SHOULD note when the primary source is inaccessible and the secondary is the best available

## Pre-Synthesis Checklist

Run this checklist before entering Step 4 (Synthesis). Every item must pass.

- [ ] Every factual claim has a navigated URL (not training knowledge)
- [ ] Every cited URL was actually loaded and the content verified
- [ ] No claim uses "typically/generally/usually" as its sole evidence
- [ ] Every claim has a recorded source date
- [ ] Secondary sources have been traced to primaries where possible
- [ ] Claims with < 2 independent sources are marked Low or Insufficient
- [ ] Contradictions are documented with both positions, not silently resolved
- [ ] Interpolated connections are flagged explicitly

## When Evidence Feels Thin

Decision tree for insufficient evidence:

```
Evidence feels thin for a claim
├── Have you searched with 2+ different queries?
│   ├── No → Search again with alternative terms
│   └── Yes → Have you tried both Context7 and agent-browser?
│       ├── No → Try the other tool
│       └── Yes → Is this a time-sensitive topic?
│           ├── Yes → Mark INSUFFICIENT, document searches, note "may exist but not findable with current tools"
│           └── No → Is this a niche topic?
│               ├── Yes → Mark INSUFFICIENT, document searches, suggest primary research
│               └── No → Mark INSUFFICIENT, flag as potential gap in available sources
```

The abstention IS the finding. Documenting what you searched and did not find is more valuable than filling the gap with reasoning.

## Reasoning vs. Evidence Boundary

| Use Reasoning For | Use Evidence For |
|-------------------|------------------|
| Planning which sources to consult | Factual claims about the world |
| Synthesizing across multiple sources | Specific numbers, dates, statistics |
| Generating recommendations from evidence | Comparisons between technologies |
| Identifying logical connections to investigate | Current state of APIs, features, pricing |
| Structuring the output | Quotes, benchmarks, performance data |

**The rule**: Reasoning connects and synthesizes evidence. Reasoning never replaces evidence. If a claim could be wrong, it needs a source.

---

*Reference for: deep-research skill, Steps 2-4*
