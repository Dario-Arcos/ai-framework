---
name: deep-research
description: AI-native multi-pass research with verification pipeline and confidence-rated outputs
argument-hint: "complex investigations | due diligence | market research | regulatory analysis | strategic intelligence"
---

# AI-Native Deep Research

**Systematic research methodology optimized for AI agent execution.**

Research topic: $ARGUMENTS

---

## Core Principles

This command implements **context-aware research** following Anthropic's context engineering guidelines and state-of-the-art patterns from OpenAI Deep Research, Perplexity, and Gemini.

### AI-Native Methodology

| Principle | Implementation |
|-----------|----------------|
| **Attention Budget** | Treat context as finite resource with diminishing returns |
| **Multi-pass RAG** | 3-5 iterative search rounds, not single-pass |
| **Confidence Transparency** | Rate every claim (High/Medium/Low/Uncertain) |
| **Citation Granularity** | Source at sentence level, not paragraph |
| **Cross-validation** | Minimum 3 sources for material claims |

### Anti-Hallucination Protocol

An AI researching has **different failure modes** than humans:

1. **Confabulation risk**: AI may generate plausible-sounding but fabricated details
2. **Citation fabrication**: Studies show 17-56% of AI citations contain errors
3. **Recency blindness**: Training data is stale - always verify current info
4. **Authority confusion**: AI may conflate rumor with fact

**Countermeasures built into this protocol:**
- Real browser navigation (not cached/training data)
- Multi-source cross-validation mandatory
- Explicit uncertainty declaration
- Source confidence ratings required

---

## Execution Flow

### Phase 0: Research Planning

**Display**: "Planificando estrategia de investigacion..."

**0.1 Parse and validate arguments:**
- If `$ARGUMENTS` is empty or vague: Use AskUserQuestion to clarify scope
- Extract: topic, scope boundaries, depth level, deliverable format

**0.2 Decompose research question:**
- Break into 3-7 sub-questions that together answer the main query
- Identify: What facts needed? What analysis required? What comparisons?
- Prioritize by information value (high-impact questions first)

**0.3 Define source strategy:**
- Map sub-questions to source tiers (see Source Hierarchy below)
- Identify potential specialized sources for the domain
- Estimate search iterations needed (default: 3-5 passes)

**0.4 Display research plan:**

```
Research Plan for: [TOPIC]

Sub-questions:
1. [Question] → Target sources: [Tier 1/2/3]
2. [Question] → Target sources: [Tier 1/2/3]
...

Estimated passes: [N]
Depth level: [Executive summary | Detailed report | Comprehensive analysis]

Proceeding with research...
```

---

### Phase 1: Primary Research (Browser Navigation)

**CRITICAL**: Use `agent-browser` skill for ALL web navigation. Never WebFetch/WebSearch.

**1.1 Initialize browser session:**

```bash
agent-browser open [URL]
agent-browser snapshot -i  # Discover interactive elements
```

**1.2 Navigate source hierarchy systematically:**

#### Tier 1 Sources (Primary - Highest Reliability)

| Category | Examples | Navigation Pattern |
|----------|----------|-------------------|
| **Government/Regulatory** | .gov sites, SEC, central banks | Direct URL navigation |
| **Academic** | Peer-reviewed journals, ArXiv, PubMed | Search + filter by date |
| **Official Data** | World Bank, IMF, OECD, WHO | Data portals, reports |
| **Legal/Regulatory** | Court decisions, regulatory guidance | Legal databases |

```bash
# Example: SEC filings
agent-browser open https://www.sec.gov/cgi-bin/browse-edgar
agent-browser fill @companySearch "[company name]"
agent-browser click @searchBtn
agent-browser screenshot sec-results.png
```

#### Tier 2 Sources (Industry Authoritative - High Reliability)

| Category | Examples |
|----------|----------|
| **Major Consulting** | Deloitte, PwC, EY, KPMG research |
| **Strategy Consulting** | McKinsey Global Institute, BCG, Bain |
| **Financial Intelligence** | Bloomberg, Reuters, FT analysis |
| **Research Firms** | Gartner, Forrester, IDC |

#### Tier 3 Sources (Corroborative - Supporting Evidence)

| Category | Examples |
|----------|----------|
| **Quality Journalism** | WSJ, The Economist, HBR |
| **Industry Bodies** | Professional associations, trade orgs |
| **Corporate Intelligence** | Annual reports, 10-K filings |
| **Expert Analysis** | Verified SME commentary |

**1.3 For each source visited:**

```bash
agent-browser open [URL]
agent-browser snapshot -i
# Navigate to relevant section
agent-browser click @[relevant-section]
# Capture evidence
agent-browser screenshot evidence-[n].png
```

**Document immediately:**
```
Source: [URL]
Accessed: [YYYY-MM-DD HH:MM]
Tier: [1/2/3]
Key claims extracted:
- [Claim 1]
- [Claim 2]
Limitations noted: [any caveats]
```

---

### Phase 2: Iterative Refinement

**Display**: "Ejecutando pase [N] de investigacion..."

**2.1 After initial pass, identify gaps:**
- Which sub-questions remain unanswered?
- Which claims lack multi-source confirmation?
- What conflicting information requires resolution?

**2.2 Execute refinement passes (minimum 3):**

```
Pass 1: Primary sources → Core facts
Pass 2: Secondary sources → Confirmation + depth
Pass 3: Corroborative → Fill gaps + resolve conflicts
Pass 4+: (if needed) → Specialized sources for remaining gaps
```

**2.3 Track search coverage:**

```
Sub-question 1: [3/3 sources] [Status: Confirmed]
Sub-question 2: [2/3 sources] [Status: Needs more]
Sub-question 3: [1/3 sources] [Status: Uncertain - conflicting data]
```

---

### Phase 3: Cross-Validation & Verification

**Display**: "Verificando y validando fuentes..."

**3.1 Apply verification protocol:**

For each material claim:
- [ ] Minimum 3 independent sources
- [ ] At least 1 Tier 1 source
- [ ] Check for recency (prefer last 12 months)
- [ ] Identify potential biases in sources

**3.2 Resolve conflicts:**

When sources disagree:
1. Document both positions with sources
2. Assess source reliability hierarchy
3. Note uncertainty explicitly
4. Do NOT silently pick one version

**3.3 Assign confidence ratings:**

| Rating | Criteria |
|--------|----------|
| **High** | 3+ Tier 1/2 sources agree, recent data, no conflicts |
| **Medium** | 2+ sources agree, some Tier 3, minor conflicts resolved |
| **Low** | Limited sources, older data, or unresolved minor conflicts |
| **Uncertain** | Conflicting authoritative sources, insufficient data |

---

### Phase 4: Synthesis & Report Generation

**Display**: "Sintetizando hallazgos..."

**4.1 Structure report following this template:**

```markdown
# Research Report: [Topic]

## Executive Summary
[2-3 paragraphs: Key findings, confidence levels, actionable recommendations]

## Methodology & Source Verification
- **Sources consulted**: [N total, breakdown by tier]
- **Search iterations**: [N passes]
- **Coverage assessment**: [gaps identified]
- **Limitations**: [explicit constraints]

## Key Findings

### Finding 1: [Title] [Confidence: High/Medium/Low]
[Content with inline citations]

**Sources**:
- [Source 1] | [URL] | [Date] | Tier [N]
- [Source 2] | [URL] | [Date] | Tier [N]
- [Source 3] | [URL] | [Date] | Tier [N]

### Finding 2: [Title] [Confidence: X]
...

## Disputed/Uncertain Points

| Point | Source A Says | Source B Says | Assessment |
|-------|---------------|---------------|------------|
| [X] | [Position] | [Position] | [Analysis] |

## Risk Assessment & Recommendations

### Risks Identified
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [X] | High/Med/Low | High/Med/Low | [Action] |

### Strategic Recommendations
1. [Recommendation] [Priority: High]
2. [Recommendation] [Priority: Medium]
...

## Appendix: Complete Source Log

| # | URL | Accessed | Tier | Claims Extracted |
|---|-----|----------|------|------------------|
| 1 | ... | ... | ... | ... |
```

**4.2 Apply quality gates:**

Before delivering:
- [ ] Every factual claim has inline citation
- [ ] Confidence ratings assigned to all findings
- [ ] Conflicts documented, not hidden
- [ ] Limitations explicitly stated
- [ ] Actionable recommendations provided

---

## Evidence Documentation Standard

**Format for every claim:**

```
[Statement] | Source: [URL] | Date: [YYYY-MM-DD] | Tier: [1/2/3] | Confidence: [H/M/L/U]
Cross-validation: [Confirming URLs] | Conflicts: [If any]
```

**Example:**
```
Global AI market size reached $196.6B in 2024
| Source: https://www.grandviewresearch.com/industry-analysis/artificial-intelligence-ai-market
| Date: 2025-01-15
| Tier: 2 (Industry Research)
| Confidence: High
| Cross-validation: Statista ($184B), IDC ($189B) - consistent range
| Conflicts: None
```

---

## Browser Navigation

**The `agent-browser` skill is automatically loaded and provides complete command reference.**

### Essential Research Flow

```bash
agent-browser open [URL]          # Navigate
agent-browser snapshot -i         # Get element refs (@e1, @e2...)
agent-browser click @e1           # Interact using refs
agent-browser screenshot out.png  # Capture evidence
```

### For Authenticated Sources

```bash
agent-browser state save session.json   # After login
agent-browser state load session.json   # Resume later
```

**For full command reference**: See the loaded `agent-browser` skill documentation (snapshot options, wait commands, network mocking, etc.)

---

## Context Management (Anti-Context-Rot)

### During Long Research Sessions

1. **Compaction checkpoints**: Every 5 sources, summarize findings so far
2. **Working memory notes**: Keep running list of confirmed facts vs. pending
3. **Tool result clearing**: Don't retain raw HTML - extract and discard

### If Approaching Token Limits

1. Summarize current findings to condensed format
2. Clear intermediate search results
3. Keep only: confirmed claims + source URLs + pending questions
4. Resume with focused remaining queries

---

## Error Handling

| Condition | Action |
|-----------|--------|
| **Source unavailable** | Log, try archive.org, move to next source |
| **Paywall encountered** | Note limitation, seek alternative source |
| **Conflicting authoritative sources** | Document both, mark as Uncertain |
| **Insufficient sources found** | Expand to Tier 3, note coverage gap |
| **Browser navigation fails** | Use `--headed` to debug, retry |

---

## Quality Standards

**Every deliverable must pass:**

| Criterion | Requirement |
|-----------|-------------|
| **Factual grounding** | Every claim sourced |
| **Source diversity** | No over-reliance on single source |
| **Recency** | Prefer sources < 12 months old |
| **Uncertainty transparency** | Gaps explicitly declared |
| **Actionability** | Recommendations provided |

**Report NOT ready if:**
- Any material claim lacks citation
- Confidence ratings missing
- Known conflicts undocumented
- No methodology section
- No limitations stated

---

## Implementation Notes

- **Token budget**: ~3,000 for planning + navigation, ~2,000 for synthesis
- **Target output**: Comprehensive report (500-2000 words depending on scope)
- **Session persistence**: Use `agent-browser state save/load` for multi-session research
- **Screenshot evidence**: Store in `.claude/research/[topic-slug]/` for reference

**Goal**: Investigate with professional audit rigor, AI-native methodology, and complete source transparency.
