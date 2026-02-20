# Evidence Documentation Standard

## Confidence Ratings

| Rating | Criteria |
|--------|----------|
| **High** | 3+ Tier 1/2 sources agree, recent data, no conflicts |
| **Medium** | 2+ sources agree, some Tier 3, minor conflicts resolved |
| **Low** | Limited sources, older data, or unresolved minor conflicts |
| **Uncertain** | Conflicting authoritative sources, insufficient data |
| **Insufficient** | Investigated but no confirming sources found. Search attempts documented |

## Per-Claim Format

```
[Statement] | Source: [URL] | Date: [YYYY-MM-DD] | Tier: [1/2/3] | Confidence: [H/M/L/U/I]
Perspective: [Who benefits from this claim? What viewpoint does the source represent?]
Cross-validation: [Confirming URLs] | Conflicts: [If any]
```

Example:
```
Global AI market size reached $196.6B in 2024
| Source: https://www.grandviewresearch.com/industry-analysis/artificial-intelligence-ai-market
| Date: 2025-01-15
| Tier: 2 (Industry Research)
| Confidence: High
| Perspective: Market research firm — incentivized to project growth; data methodology disclosed
| Cross-validation: Statista ($184B), IDC ($189B) - consistent range
| Conflicts: None
```

## Report Template

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

## Disputed/Uncertain Points

| Point | Source A Says | Source B Says | Assessment |
|-------|---------------|---------------|------------|

## Limitations & Gaps
- **Unanswered questions**: [Sub-questions that could not be resolved]
- **Source gaps**: [Topics where only Tier 3 sources were available]
- **Recency gaps**: [Areas where most recent data is older than 12 months]
- **Perspective gaps**: [Viewpoints not represented in available sources]
- **Scope exclusions**: [What was deliberately excluded and why]

## Risk Assessment & Recommendations

### Risks Identified
| Risk | Likelihood | Impact | Mitigation |

### Strategic Recommendations
1. [Recommendation] [Priority: High]

## Appendix: Complete Source Log
| # | URL | Accessed | Tier | Claims Extracted |
```

## Quality Gates

| Criterion | Requirement |
|-----------|-------------|
| **Factual grounding** | Every claim sourced |
| **Source diversity** | No over-reliance on single source |
| **Recency** | Prefer sources < 12 months old |
| **Uncertainty transparency** | Gaps explicitly declared |
| **Actionability** | Recommendations provided |
| **Insufficient documentation** | No INSUFFICIENT claim without documented search attempts |

Report NOT ready if: any material claim lacks citation, confidence ratings missing, known conflicts undocumented, no methodology section, no limitations stated, any INSUFFICIENT-rated claim lacks documented search attempts.

## Adaptive Output Templates

Select the output format based on research type. These supplement the full report template above for the Key Findings section.

### Direct Answer (API/Framework Research)

```markdown
### [Question]

**Answer**: [Concise direct answer]

**Code Example** (if applicable):
\`\`\`[language]
[Minimal working example from Tier 1 source]
\`\`\`

**Version Note**: Verified for [library] v[X.Y.Z] as of [date]
**Source**: [Tier 1 URL] | Confidence: [rating]
```

### Comparison Table (Technology Decision Research)

```markdown
### [Decision Question]

| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| [Criterion 1] | [value] | [value] | [value] |
| [Criterion 2] | [value] | [value] | [value] |

**Recommendation**: [Option] for [use case] because [evidence-backed reason]
**Caveat**: [Key trade-off or limitation]
**Sources**: [Tier 1-2 URLs for each cell value]
```

### Timeline (Current Events Research)

```markdown
### [Event/Topic]

| Date | Event | Source | Significance |
|------|-------|--------|--------------|
| [YYYY-MM-DD] | [What happened] | [URL] | [Why it matters] |
| [YYYY-MM-DD] | [What happened] | [URL] | [Why it matters] |

**Current Status**: [Latest known state as of research date]
**Projected Next**: [Expected developments, if supported by sources]
**Sources**: [Tier 1-2 URLs]
```

## Error Handling

| Condition | Action |
|-----------|--------|
| **Source unavailable** | Log, try archive.org, move to next source |
| **Paywall encountered** | Note limitation, seek alternative source |
| **Conflicting authoritative sources** | Document both, mark as Uncertain |
| **Insufficient sources found** | Expand to Tier 3, note coverage gap |
| **Browser navigation fails** | Use `--headed` to debug, retry |

---

*Version: 2.0.0 | Updated: 2026-02-20*
